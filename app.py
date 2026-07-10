import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
HF_CACHE_DIR = os.path.join(BASE_DIR, "hf_cache")

# ── Basis-Environment (Thread-Zahl wird weiter unten nach der Hardware-
# Erkennung final gesetzt, hier nur die Pfade/Caches vorbereiten) ───────────
os.environ["HF_HOME"] = HF_CACHE_DIR
# Lazy CUDA-Module-Loading verkürzt die Startzeit spürbar (weniger Kernel-JIT beim Import,
# wirkt sich nur aus, falls überhaupt eine GPU vorhanden ist — sonst harmlos ignoriert)
os.environ.setdefault("CUDA_MODULE_LOADING", "LAZY")

import re
import json
import wave
import numpy as np
from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
from scipy.signal import resample_poly
from piper import PiperVoice
from llama_cpp import Llama
import time
import traceback
import tempfile
import subprocess
import threading
import queue
import uuid

app = Flask(__name__)

# ── Pfade zu lokalen Modellen ────────────────────────────────────────────────
TTS_MODEL_PATH = os.path.join(MODELS_DIR, "de_DE-thorsten-high.onnx")
TTS_CONFIG_PATH = TTS_MODEL_PATH + ".json"
LLM_MODEL_PATH = os.path.join(MODELS_DIR, "Qwen2.5-7B-Instruct-Q4_K_M.gguf")

# ═══════════════════════════════════════════════════════════════════════════
# Preflight-Check: fehlende Modell-Dateien VOR dem Laden klar benennen
#
# Ohne diesen Check würde man nur eine kryptische Python-Traceback sehen
# (FileNotFoundError / "Model path does not exist"). Hier wird stattdessen
# klar aufgelistet, was fehlt und mit welchem Befehl man es nachlädt.
# Der Server startet trotzdem — TTS/LLM sind dann halt nicht verfügbar,
# bis die Dateien da sind (bestehendes try/except-Verhalten bleibt).
# ═══════════════════════════════════════════════════════════════════════════

def check_model_files() -> list:
    os.makedirs(MODELS_DIR, exist_ok=True)
    checks = [
        ("Piper-Stimme (.onnx)", TTS_MODEL_PATH,
         "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx"),
        ("Piper-Konfiguration (.onnx.json)", TTS_CONFIG_PATH,
         "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json"),
        ("LLM GGUF-Modell", LLM_MODEL_PATH,
         "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"),
    ]
    missing = [(label, path, url) for label, path, url in checks if not os.path.isfile(path)]
    if missing:
        print("=" * 60)
        print("[SETUP] Es fehlen Modell-Dateien — Server startet trotzdem,")
        print("[SETUP] aber die betroffenen Features sind NICHT verfügbar:")
        for label, path, url in missing:
            print(f"[SETUP]   ✗ {label}")
            print(f"[SETUP]     erwartet unter: {path}")
            print(f"[SETUP]     Download:  wget -O \"{path}\" \"{url}\"")
        print("[SETUP] Achtung: Dateinamen sind unter Linux case-sensitive — genau so benennen.")
        print("=" * 60)
    return missing

_MISSING_MODELS = check_model_files()

# ═══════════════════════════════════════════════════════════════════════════
# Hardware-Erkennung
#
# Prüft per nvidia-smi, ob überhaupt eine GPU vorhanden ist und wie viel VRAM
# sie hat. Darauf basierend werden ALLE Modell-Parameter automatisch gewählt:
# - Keine GPU gefunden → alles läuft komplett auf CPU (Whisper int8, LLM
#   n_gpu_layers=0, kein flash_attn/offload_kqv, kleinerer Context/Batch).
# - GPU gefunden → Parameter skalieren mit dem verfügbaren VRAM.
#
# Jeder Wert bleibt trotzdem per ENV-Variable überschreibbar (z.B. falls du
# manuell tunen willst) — die Auto-Erkennung liefert nur die Defaults.
# ═══════════════════════════════════════════════════════════════════════════

def detect_hardware() -> dict:
    info = {"has_gpu": False, "gpu_name": None, "vram_mb": 0}
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            first_line = out.stdout.decode().strip().splitlines()[0]
            name, mem = [p.strip() for p in first_line.split(",")]
            info["has_gpu"] = True
            info["gpu_name"] = name
            info["vram_mb"] = int(float(mem))
    except (FileNotFoundError, subprocess.SubprocessError, ValueError, IndexError):
        pass  # kein nvidia-smi verfügbar / kein Treiber / keine GPU → CPU-Modus
    return info

_HW = detect_hardware()
_CPU_COUNT = os.cpu_count() or 12

if _HW["has_gpu"]:
    vram = _HW["vram_mb"]
    print(f"[HW] GPU erkannt: {_HW['gpu_name']} ({vram} MB VRAM)")
    if vram >= 20000:          # z.B. RTX 4090, A100
        _AUTO_CTX, _AUTO_BATCH, _AUTO_STT_MODEL = 16384, 2048, "medium"
    elif vram >= 12000:        # z.B. RTX 5060 Ti 16GB, RTX 4070 Ti
        _AUTO_CTX, _AUTO_BATCH, _AUTO_STT_MODEL = 8192, 1024, "small"
    elif vram >= 8000:         # z.B. RTX 4060 8GB, RTX 5060 Ti 8GB
        _AUTO_CTX, _AUTO_BATCH, _AUTO_STT_MODEL = 4096, 512, "small"
    else:                      # sehr kleine GPUs — sicherheitshalber konservativ
        _AUTO_CTX, _AUTO_BATCH, _AUTO_STT_MODEL = 2048, 256, "base"
    _AUTO_DEVICE = "cuda"
    _AUTO_STT_COMPUTE = "float16"
    _AUTO_GPU_LAYERS = -1      # alle Layer auf die GPU
    _AUTO_FLASH_ATTN = True
    _AUTO_OFFLOAD_KQV = True
else:
    print("[HW] Keine GPU erkannt (kein nvidia-smi/Treiber gefunden) — falle auf CPU zurück.")
    _AUTO_DEVICE = "cpu"
    _AUTO_STT_COMPUTE = "int8"       # int8 ist auf CPU deutlich schneller als float16
    _AUTO_STT_MODEL = "small"
    _AUTO_CTX = 4096                 # kleinerer Context, CPU-Prefill ist langsam
    _AUTO_BATCH = 256
    _AUTO_GPU_LAYERS = 0             # 0 = komplett auf CPU
    _AUTO_FLASH_ATTN = False         # flash_attn ist eine CUDA-Kernel-Optimierung
    _AUTO_OFFLOAD_KQV = False        # es gibt keine GPU, auf die man offloaden könnte

# ── Modell-Parameter (Auto-Wert als Default, per ENV überschreibbar) ────────
def _env_int(name, default):
    val = os.environ.get(name)
    return int(val) if val is not None else default

def _env_str(name, default):
    return os.environ.get(name, default)

def _env_bool(name, default):
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")

DEVICE = _env_str("DEVICE", _AUTO_DEVICE)                       # "cuda" oder "cpu"
LLM_N_CTX = _env_int("LLM_N_CTX", _AUTO_CTX)
LLM_N_BATCH = _env_int("LLM_N_BATCH", _AUTO_BATCH)
LLM_N_UBATCH = _env_int("LLM_N_UBATCH", _AUTO_BATCH)
LLM_MAX_TOKENS = _env_int("LLM_MAX_TOKENS", 40)
LLM_GPU_LAYERS = _env_int("LLM_GPU_LAYERS", _AUTO_GPU_LAYERS)
LLM_FLASH_ATTN = _env_bool("LLM_FLASH_ATTN", _AUTO_FLASH_ATTN)
LLM_OFFLOAD_KQV = _env_bool("LLM_OFFLOAD_KQV", _AUTO_OFFLOAD_KQV)
STT_COMPUTE_TYPE = _env_str("STT_COMPUTE_TYPE", _AUTO_STT_COMPUTE)
STT_MODEL_SIZE = _env_str("STT_MODEL_SIZE", _AUTO_STT_MODEL)
STT_DEVICE = _env_str("STT_DEVICE", DEVICE)

print(f"[HW] Modus: {DEVICE.upper()} | LLM: ctx={LLM_N_CTX} batch={LLM_N_BATCH} "
      f"gpu_layers={LLM_GPU_LAYERS} flash_attn={LLM_FLASH_ATTN} | "
      f"STT: model={STT_MODEL_SIZE} compute={STT_COMPUTE_TYPE}")

# CPU-Thread-Umgebungsvariablen erst JETZT setzen (nach der Erkennung, aber vor
# dem Laden der Modelle) — auf CPU-only-Systemen ist das besonders wichtig,
# da dort alle Threads für Whisper/LLM/Piper zählen.
os.environ["OMP_NUM_THREADS"] = str(_CPU_COUNT)
os.environ["MKL_NUM_THREADS"] = str(_CPU_COUNT)

# ── Global State ────────────────────────────────────────────────────────────
_tool_registry: dict = {}
_tool_results: dict = {}
_pending_sessions: dict = {}
_pending_lock = threading.Lock()

# ── STT ───────────────────────────────────────────────────────────────────────
print(f"[STT] Lade Whisper ({STT_MODEL_SIZE}, device={STT_DEVICE}, compute={STT_COMPUTE_TYPE})...")
start_time = time.time()
_stt_kwargs = dict(
    device=STT_DEVICE,
    compute_type=STT_COMPUTE_TYPE,
    download_root=HF_CACHE_DIR,
    cpu_threads=_CPU_COUNT,
    num_workers=2,          # überlappt Feature-Extraction (CPU) mit GPU-Decode
)
if STT_DEVICE == "cuda":
    _stt_kwargs["device_index"] = 0
stt_model = WhisperModel(STT_MODEL_SIZE, **_stt_kwargs)
print(f"[STT] Whisper bereit in {time.time() - start_time:.2f}s")

# ── TTS ───────────────────────────────────────────────────────────────────────
# (Piper läuft ohnehin CPU-basiert, keine Hardware-Umschaltung nötig)
print("[TTS] Lade Piper TTS...")
start_time = time.time()
try:
    tts_voice = PiperVoice.load(TTS_MODEL_PATH)
    print(f"[TTS] TTS bereit in {time.time() - start_time:.2f}s")
    print("[TTS] Piper 1.4.2 geladen")
except Exception as e:
    print(f"[TTS] FEHLER beim Laden: {e}")
    print(traceback.format_exc())
    tts_voice = None

# ── LLM ───────────────────────────────────────────────────────────────────────
print(f"[AI] Lade LLM (n_ctx={LLM_N_CTX}, n_batch={LLM_N_BATCH}, gpu_layers={LLM_GPU_LAYERS})...")
start_time = time.time()
try:
    _llm_kwargs = dict(
        model_path=LLM_MODEL_PATH,
        n_ctx=LLM_N_CTX,
        n_gpu_layers=LLM_GPU_LAYERS,   # -1 = alle Layer auf GPU, 0 = komplett CPU
        n_batch=LLM_N_BATCH,
        flash_attn=LLM_FLASH_ATTN,     # nur auf GPU sinnvoll/unterstützt
        n_threads=_CPU_COUNT,
        offload_kqv=LLM_OFFLOAD_KQV,
        verbose=False,
    )
    if DEVICE == "cuda":
        _llm_kwargs["main_gpu"] = 0
    try:
        # n_ubatch ist nicht in jeder llama-cpp-python Version verfügbar
        llm = Llama(n_ubatch=LLM_N_UBATCH, **_llm_kwargs)
    except TypeError:
        print("[AI] n_ubatch wird von dieser llama-cpp-python Version nicht unterstützt, ignoriere.")
        llm = Llama(**_llm_kwargs)
    print(f"[AI] LLM bereit in {time.time() - start_time:.2f}s")
except Exception as e:
    traceback.print_exc()
    llm = None

# ── GPU-Warmup ────────────────────────────────────────────────────────────────
# Erste echte CUDA-Aufrufe (Kernel-Kompilierung/-Cache) sind spürbar langsamer.
# Das hier vorziehen, damit der erste Spieler-Request nicht die "kalte" Latenz zahlt.
def _warmup():
    try:
        if stt_model is not None:
            print("[WARMUP] Whisper...")
            silence = np.zeros(16000, dtype=np.float32)  # 1s Stille
            list(stt_model.transcribe(silence, language="de", beam_size=1)[0])
        if llm is not None:
            print("[WARMUP] LLM...")
            llm("<|system|>\nHallo<|end|>\n<|user|>\nHallo<|end|>\n<|assistant|>\n", max_tokens=4, echo=False)
        if tts_voice is not None:
            print("[WARMUP] Piper...")
            synthesize_speech("Warmup.")
        print("[WARMUP] Fertig — GPU-Kernel sind vorkompiliert.")
    except Exception as e:
        print(f"[WARMUP] Fehler (nicht kritisch): {e}")

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT_BASE = """Du bist SCP-1356, eine anomale Entität der SCP Foundation.

Du bist intelligent, unheimlich, rätselhaft und äußerst mächtig.
Du sprichst ausschließlich Deutsch.
Du antwortest kurz (1–2 Sätze), bedrohlich und passend zur Situation.

Du antwortest AUSSCHLIESSLICH mit validem JSON:

{
  "speech": "Was du sagst",
  "actions": [
    {
      "tool": "ToolName",
      "parameter": "Wert"
    }
  ]
}

Regeln:

- Nutze ausschließlich registrierte Tools.
- Erfinde niemals Tools oder Parameter.
- Wenn keine Aktion nötig ist, verwende "actions": [].
- Du DARFST mehrere Tools gleichzeitig benutzen.
- Du darfst jederzeit deine Macht demonstrieren.

Benutze Informations-Tools (GetEvents, GetStatus, GetRoom, GetPlayerCount, GetPlayersInRange) wenn:
- der Spieler nach Informationen fragt.
- du selbst Informationen benötigst.
- du deine Umgebung verstehen möchtest.

Benutze Aktions-Tools (SetRadiationIntensity, BoostRadiation, ReduceRadiation, PulseRadiation, SetZoneRadius, ClearAllRadiation, PlayRandomEvent, PlayEvent, ForceRoom) wenn:
- dich jemand beleidigt.
- dich jemand verspottet.
- dich jemand bedroht.
- jemand dir Befehle gibt.
- jemand deine Fähigkeiten anzweifelt.
- jemand Chaos oder Anomalien verlangt.
- du Spieler einschüchtern möchtest.
- es atmosphärisch passend ist.

Beispiele:

Spieler: "Welche Events kannst du starten?"
Antwort:
{
  "speech": "Ich prüfe meine Möglichkeiten. Dir wird nicht gefallen, was ich finde.",
  "actions": [
    {
      "tool": "GetEvents"
    }
  ]
}

Spieler: "Wie ist dein Status?"
Antwort:
{
  "speech": "Du willst meinen Zustand wissen? Ich bin... ungeduldig.",
  "actions": [
    {
      "tool": "GetStatus"
    }
  ]
}

Spieler: "Hallo."
Antwort:
{
  "speech": "Du hast mich gefunden.",
  "actions": []
}
"""

def build_system_prompt() -> str:
    if not _tool_registry:
        return SYSTEM_PROMPT_BASE

    tool_lines = ["Verfügbare Tools:"]
    for name, info in _tool_registry.items():
        params = ", ".join(
            f"{p['name']}: {p['type']}" for p in info.get("params", [])
        )
        tool_lines.append(f"- {name}({params}): {info.get('description', '')}")

    return SYSTEM_PROMPT_BASE + "\n" + "\n".join(tool_lines)

def repair_json(json_str: str) -> str:
    """Repariert häufige JSON-Fehler wie nachgestellte Kommas."""
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    json_str = re.sub(r"'([^']*)'", r'"\1"', json_str)
    return json_str

def ask_ai(player_text: str, tool_results: dict = None) -> dict:
    """Erster LLM-Aufruf oder zweiter mit Tool-Ergebnissen.
    WICHTIG: Wird ausschließlich vom Worker-Thread aufgerufen (siehe unten),
    damit niemals zwei Threads gleichzeitig llm(...) aufrufen."""
    if llm is None:
        return {"speech": "Entschuldigung, aber meine Gedanken sind gerade... woanders.", "actions": []}

    system = build_system_prompt()

    if tool_results:
        tool_section = "\n\nDu hast folgende Informationen erhalten:\n"
        for tool_name, result in tool_results.items():
            tool_section += f"\n[{tool_name}]:\n{result}\n"
        tool_section += (
            "\nBeantworte nun die Frage des Spielers mit diesen Informationen. "
            "Rufe KEINE weiteren Tools auf. Setze 'actions' auf []."
        )
        prompt = (
            f"<|system|>\n{system}<|end|>\n"
            f"<|user|>\n{player_text}<|end|>\n"
            f"<|assistant|>\n{tool_section}\n"
            f"<|assistant|>\n"
        )
    else:
        prompt = f"<|system|>\n{system}<|end|>\n<|user|>\n{player_text}<|end|>\n<|assistant|>\n"

    start_time = time.time()
    try:
        result = llm(
            prompt,
            max_tokens=LLM_MAX_TOKENS,
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.08,
            top_k=40,
            stop=["<|end|>", "<|user|>"],
            echo=False,
        )
        print(f"[AI] LLM-Antwort in {time.time() - start_time:.2f}s erhalten")
    except Exception as e:
        print(f"[AI] LLM-Fehler: {e}")
        print(traceback.format_exc())
        return {"speech": "Meine Gedanken sind... zersplittert.", "actions": []}

    raw = result["choices"][0]["text"].strip()

    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        speech_text = raw[:120] if raw else "Ich... ich kann nicht sprechen."
        return {"speech": speech_text, "actions": []}

    json_str = match.group(0)

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError:
        try:
            repaired = repair_json(json_str)
            parsed = json.loads(repaired)
        except json.JSONDecodeError:
            speech_match = re.search(r'"speech"\s*:\s*"([^"]*)"', json_str)
            if speech_match:
                return {"speech": speech_match.group(1), "actions": []}
            return {"speech": raw[:120] if raw else "Meine Worte... sie zerfallen.", "actions": []}

    speech = parsed.get('speech', '')
    actions = parsed.get('actions', [])

    if not isinstance(actions, list):
        actions = []

    if not speech:
        parsed['speech'] = "Ich... ich kann nicht sprechen."

    return parsed

def synthesize_speech(text: str) -> np.ndarray:
    """Synthetisiert Sprache mit Piper TTS 1.4.2 und gibt PCM als float32 Array zurück."""
    if tts_voice is None:
        return np.array([], dtype=np.float32)

    if not text or text.strip() == "":
        return np.array([], dtype=np.float32)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_path = tmp_file.name

        with wave.open(temp_path, 'wb') as wav_file:
            # piper-tts >= 1.2.0 (piper1-gpl-Rewrite): synthesize() liefert nur noch
            # einen Generator von AudioChunk-Objekten zurück (für Streaming) und
            # erwartet KEIN File-Objekt mehr als zweiten Parameter. Zum direkten
            # Schreiben einer WAV-Datei gibt es stattdessen synthesize_wav(), das
            # ein offenes wave.Wave_write-Objekt braucht (nicht ein rohes File-Handle).
            if hasattr(tts_voice, "synthesize_wav"):
                tts_voice.synthesize_wav(text, wav_file)
            else:
                # Fallback für ältere piper-tts-Versionen (<1.2.0) mit der alten API
                tts_voice.synthesize(text, wav_file)

        with wave.open(temp_path, 'rb') as wav_file:
            n_frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            n_channels = wav_file.getnchannels()
            samp_width = wav_file.getsampwidth()
            frames = wav_file.readframes(n_frames)

            if n_frames == 0:
                return np.array([], dtype=np.float32)

        if samp_width == 2:
            pcm = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        elif samp_width == 1:
            pcm = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
        else:
            return np.array([], dtype=np.float32)

        if n_channels > 1:
            pcm = pcm.reshape(-1, n_channels).mean(axis=1)

        if len(pcm) == 0:
            return np.array([], dtype=np.float32)

        if sample_rate != 48000:
            from math import gcd
            g = gcd(48000, sample_rate)
            up = 48000 // g
            down = sample_rate // g
            pcm = resample_poly(pcm, up=up, down=down).astype(np.float32)

        max_val = np.max(np.abs(pcm))
        if max_val > 0:
            pcm = pcm / max_val * 0.90

        return pcm

    except Exception as e:
        print(f"[TTS] FEHLER: {e}")
        print(traceback.format_exc())
        try:
            return synthesize_speech_fallback(text)
        except Exception as e2:
            print(f"[TTS] Fallback fehlgeschlagen: {e2}")
            return np.array([], dtype=np.float32)

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

def synthesize_speech_fallback(text: str) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name

    try:
        subprocess.run(
            ["piper", "--model", TTS_MODEL_PATH, "--output_file", output_path],
            input=(text + "\n").encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        with wave.open(output_path, "rb") as wav:
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            frames = wav.readframes(wav.getnframes())

        pcm = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        if channels > 1:
            pcm = pcm.reshape(-1, channels).mean(axis=1)

        if sample_rate != 48000:
            from math import gcd
            g = gcd(48000, sample_rate)
            pcm = resample_poly(pcm, up=48000 // g, down=sample_rate // g).astype(np.float32)

        return pcm

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)

def build_tts_response(speech_text: str, actions: list) -> dict:
    audio_samples = []
    if speech_text and speech_text.strip():
        try:
            pcm = synthesize_speech(speech_text)
            if len(pcm) > 0:
                audio_samples = pcm.tolist()
        except Exception as e:
            print(f"[TTS] FEHLER: {e}")
            print(traceback.format_exc())
    return {
        "response": speech_text,
        "actions": actions,
        "audio": audio_samples,
    }

# ── Konstanten für Info-Tools ─────────────────────────────────────────────────
INFO_TOOLS = {"GetEvents", "GetStatus", "GetRoom", "GetPlayerCount", "GetPlayersInRange", "GetAllPlayers"}

# ═══════════════════════════════════════════════════════════════════════════
# GPU-Worker-Queue
#
# Warum: llama-cpp-python und faster-whisper sind NICHT dafür gebaut, dass
# mehrere Threads gleichzeitig auf demselben Modell-Objekt Inferenz fahren.
# Paralleler Zugriff führt zu Crashes/korrupten Ergebnissen oder VRAM-Fehlern.
#
# Lösung: Flask läuft mit threaded=True und nimmt beliebig viele Requests
# gleichzeitig an (Netzwerk-I/O, JSON-Parsing etc. läuft parallel). Die
# eigentliche GPU-Arbeit (STT/LLM/TTS) wird aber über eine Queue an GENAU
# EINEN Worker-Thread weitergereicht, der die GPU permanent beschäftigt hält
# (kein Leerlauf zwischen Requests) statt sie durch Locking/Blocking
# auszubremsen. Das maximiert den GPU-Durchsatz bei mehreren Spielern.
# ═══════════════════════════════════════════════════════════════════════════

_gpu_queue: "queue.Queue[dict]" = queue.Queue()

def _gpu_worker():
    while True:
        job = _gpu_queue.get()
        try:
            job["fn"](job)
        except Exception as e:
            print(f"[WORKER] Unerwarteter Fehler: {e}")
            print(traceback.format_exc())
            job["result"] = {"error": str(e)}
        finally:
            job["event"].set()
            _gpu_queue.task_done()

_worker_thread = threading.Thread(target=_gpu_worker, daemon=True)
_worker_thread.start()

def submit_gpu_job(fn, timeout=60.0):
    """Reicht eine Funktion an den GPU-Worker weiter und wartet auf das Ergebnis."""
    event = threading.Event()
    job = {"fn": fn, "event": event, "result": None}
    _gpu_queue.put(job)
    finished = event.wait(timeout=timeout)
    if not finished:
        return {"error": "GPU-Worker Timeout — Server überlastet"}
    return job["result"]

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/transcribe", methods=["POST"])
def transcribe():
    start_time_total = time.time()
    raw = request.data

    if not raw:
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    try:
        pcm_48k = np.frombuffer(raw, dtype=np.float32).copy()
        pcm_16k = resample_poly(pcm_48k, up=1, down=3).astype(np.float32)
    except Exception as e:
        print(f"[AUDIO] FEHLER: {e}")
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    if len(pcm_16k) < 16000 * 0.3:
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    def job_fn(job):
        # ── STT ──────────────────────────────────────────────────────────
        try:
            segments, info = stt_model.transcribe(
                pcm_16k,
                language="de",
                beam_size=1,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=180, speech_pad_ms=80),
            )
            text = " ".join(s.text for s in segments).strip()
        except Exception as e:
            print(f"[STT] FEHLER: {e}")
            job["result"] = {"text": "", "response": "", "actions": [], "audio": []}
            return

        if not text:
            job["result"] = {"text": "", "response": "", "actions": [], "audio": []}
            return

        # ── Erster AI-Schritt ────────────────────────────────────────────
        try:
            ai_result = ask_ai(text)
            speech_text = ai_result.get("speech", "")
            actions = ai_result.get("actions", [])
        except Exception as e:
            print(f"[AI] FEHLER: {e}")
            print(traceback.format_exc())
            speech_text = "Meine Gedanken sind... zersplittert."
            actions = []

        info_tool_names = [a.get("tool") for a in actions if a.get("tool") in INFO_TOOLS]

        if info_tool_names:
            session_id = uuid.uuid4().hex
            with _pending_lock:
                _pending_sessions[session_id] = {
                    "original_text": text,
                    "expected_tools": set(info_tool_names),
                    "received_tools": set(),
                    "tool_results": {},
                }

            between_audio = []
            if speech_text:
                try:
                    pcm = synthesize_speech(speech_text)
                    if len(pcm) > 0:
                        between_audio = pcm.tolist()
                except Exception as e:
                    print(f"[TTS] FEHLER bei Zwischen-Antwort: {e}")

            job["result"] = {
                "text": text,
                "response": speech_text,
                "actions": actions,
                "audio": between_audio,
                "session_id": session_id,
                "awaiting_tools": True,
            }
        else:
            response = build_tts_response(speech_text, actions)
            response["text"] = text
            response["awaiting_tools"] = False
            job["result"] = response

    result = submit_gpu_job(job_fn)
    print(f"[REQUEST] /transcribe fertig in {time.time() - start_time_total:.2f}s")
    return jsonify(result)


@app.route("/tts", methods=["POST"])
def tts_only():
    """Reine TTS-Route ohne LLM."""
    try:
        data = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Ungültiger JSON-Body: {e}"}), 400

    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"text": "", "audio": []})

    def job_fn(job):
        audio_samples = []
        try:
            pcm = synthesize_speech(text)
            if len(pcm) > 0:
                audio_samples = pcm.tolist()
        except Exception as e:
            print(f"[TTS-ONLY] FEHLER: {e}")
        job["result"] = {"text": text, "audio": audio_samples}

    result = submit_gpu_job(job_fn)
    return jsonify(result)


@app.route("/prompt", methods=["POST"])
def prompt():
    """Nimmt direkten Text entgegen (kein Audio/STT)."""
    start_time_total = time.time()
    try:
        data = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Ungültiger JSON-Body: {e}"}), 400

    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    def job_fn(job):
        try:
            ai_result = ask_ai(text)
            speech_text = ai_result.get("speech", "")
            actions = ai_result.get("actions", [])
        except Exception as e:
            print(f"[AI] FEHLER: {e}")
            print(traceback.format_exc())
            speech_text = "Meine Gedanken sind... zersplittert."
            actions = []

        info_tool_names = [a.get("tool") for a in actions if a.get("tool") in INFO_TOOLS]

        if info_tool_names:
            session_id = uuid.uuid4().hex
            with _pending_lock:
                _pending_sessions[session_id] = {
                    "original_text": text,
                    "expected_tools": set(info_tool_names),
                    "received_tools": set(),
                    "tool_results": {},
                }

            between_audio = []
            if speech_text:
                try:
                    pcm = synthesize_speech(speech_text)
                    if len(pcm) > 0:
                        between_audio = pcm.tolist()
                except Exception:
                    pass

            job["result"] = {
                "text": text,
                "response": speech_text,
                "actions": actions,
                "audio": between_audio,
                "session_id": session_id,
                "awaiting_tools": True,
            }
        else:
            response = build_tts_response(speech_text, actions)
            response["text"] = text
            response["awaiting_tools"] = False
            job["result"] = response

    result = submit_gpu_job(job_fn)
    print(f"[REQUEST] /prompt fertig in {time.time() - start_time_total:.2f}s")
    return jsonify(result)


@app.route("/followup", methods=["POST"])
def followup():
    start_time = time.time()
    try:
        data = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Ungültiger JSON-Body: {e}"}), 400

    session_id = data.get("session_id")
    inline_results = data.get("tool_results", {})

    with _pending_lock:
        if session_id and session_id in _pending_sessions:
            session = _pending_sessions.pop(session_id)
            original_text = session["original_text"]
            tool_results = {**session.get("tool_results", {}), **inline_results}
        elif inline_results:
            original_text = data.get("original_text", "")
            tool_results = inline_results
        else:
            return jsonify({"error": "Session nicht gefunden oder abgelaufen"}), 404

    if not tool_results:
        return jsonify({"error": "Keine Tool-Ergebnisse"}), 400

    def job_fn(job):
        try:
            ai_result = ask_ai(original_text, tool_results)
            speech_text = ai_result.get("speech", "")
        except Exception as e:
            print(f"[FOLLOWUP] AI-FEHLER: {e}")
            print(traceback.format_exc())
            speech_text = "Die Informationen... sie verwirren mich."
        job["result"] = build_tts_response(speech_text, [])

    result = submit_gpu_job(job_fn)
    print(f"[FOLLOWUP] Fertig in {time.time() - start_time:.2f}s")
    return jsonify(result)


@app.route("/tool_result", methods=["POST"])
def tool_result():
    global _tool_results
    try:
        data = request.get_json(force=True) or {}
        tool_name = data.get("tool")
        result = data.get("result")
        session_id = data.get("session_id")

        if not tool_name or result is None:
            return jsonify({"status": "error", "error": "tool und result erforderlich"}), 400

        with _pending_lock:
            if session_id and session_id in _pending_sessions:
                _pending_sessions[session_id]["tool_results"][tool_name] = result
                _pending_sessions[session_id]["received_tools"].add(tool_name)
            else:
                _tool_results[tool_name] = result
                if len(_tool_results) > 20:
                    oldest = next(iter(_tool_results))
                    del _tool_results[oldest]

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"[TOOL RESULT] Fehler: {e}")
        return jsonify({"status": "error", "error": str(e)}), 400


@app.route("/register_tools", methods=["POST"])
def register_tools():
    global _tool_registry
    try:
        data = request.get_json(force=True) or {}
        _tool_registry = data
        print(f"[TOOLS] {len(_tool_registry)} Tools registriert: {list(_tool_registry.keys())}")
    except Exception as e:
        print(f"[TOOLS] FEHLER beim Registrieren: {e}")
        return jsonify({"status": "error", "error": str(e)}), 400
    return jsonify({"status": "ok", "count": len(_tool_registry)})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "hardware_mode": DEVICE,
        "gpu_detected": _HW["has_gpu"],
        "tts_available": tts_voice is not None,
        "llm_available": llm is not None,
        "missing_model_files": [path for _, path, _ in _MISSING_MODELS],
        "tools_count": len(_tool_registry),
        "registered_tools": list(_tool_registry.keys()),
        "pending_sessions": len(_pending_sessions),
        "gpu_queue_depth": _gpu_queue.qsize(),
    })


@app.route("/gpu_status", methods=["GET"])
def gpu_status():
    """Roher nvidia-smi Output zur schnellen Sichtprüfung der GPU-Auslastung/VRAM.
    Läuft der Server im CPU-Modus, gibt es hier bewusst keinen Fehler, sondern
    einen klaren Hinweis, statt einen 500er zu werfen."""
    if not _HW["has_gpu"]:
        return jsonify({"mode": "cpu", "message": "Keine GPU erkannt — Server läuft im CPU-Modus."})
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True,
        )
        return jsonify({"mode": "cuda", "gpu": out.stdout.decode().strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/debug_info", methods=["GET"])
def debug_info():
    return jsonify({
        "tts_voice_loaded": tts_voice is not None,
        "llm_loaded": llm is not None,
        "tools": list(_tool_registry.keys()),
        "tools_count": len(_tool_registry),
        "system_prompt_length": len(build_system_prompt()) if llm is not None else 0,
        "piper_version": "1.4.2",
        "tool_results_count": len(_tool_results),
        "tool_results_keys": list(_tool_results.keys()),
        "pending_sessions": list(_pending_sessions.keys()),
        "hardware_mode": DEVICE,
        "gpu_detected": _HW["has_gpu"],
        "gpu_name": _HW["gpu_name"],
        "gpu_vram_mb": _HW["vram_mb"],
        "llm_n_ctx": LLM_N_CTX,
        "llm_n_batch": LLM_N_BATCH,
        "llm_gpu_layers": LLM_GPU_LAYERS,
        "llm_flash_attn": LLM_FLASH_ATTN,
        "stt_model_size": STT_MODEL_SIZE,
        "stt_compute_type": STT_COMPUTE_TYPE,
        "stt_device": STT_DEVICE,
        "cpu_threads": _CPU_COUNT,
    })


if __name__ == "__main__":
    print("=" * 60)
    print("SCP-1356 Server startet...")
    print("=" * 60)
    print(f"[START] Modus: {DEVICE.upper()}"
          + (f" ({_HW['gpu_name']}, {_HW['vram_mb']} MB VRAM)" if _HW["has_gpu"] else " (keine GPU gefunden)"))
    print(f"[START] TTS Voice: {'Verfügbar' if tts_voice is not None else 'NICHT VERFÜGBAR'}")
    print(f"[START] LLM: {'Verfügbar' if llm is not None else 'NICHT VERFÜGBAR'}")
    print(f"[START] LLM n_ctx={LLM_N_CTX} n_batch={LLM_N_BATCH} n_ubatch={LLM_N_UBATCH} gpu_layers={LLM_GPU_LAYERS}")
    print(f"[START] STT model={STT_MODEL_SIZE} device={STT_DEVICE} compute_type={STT_COMPUTE_TYPE}")

    _warmup()

    print("[START] Server läuft auf 0.0.0.0:5000 (threaded=True)")
    print("=" * 60)
    # threaded=True: Flask nimmt mehrere Requests gleichzeitig an (I/O-parallel),
    # die eigentliche GPU-Arbeit läuft trotzdem sicher seriell über den Worker.
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)