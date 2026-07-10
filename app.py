import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
HF_CACHE_DIR = os.path.join(BASE_DIR, "hf_cache")

# ── CPU-Threads: auf tatsächliche Kernzahl ausrichten statt hart 12 ─────────
_CPU_COUNT = os.cpu_count() or 12
os.environ["OMP_NUM_THREADS"] = str(_CPU_COUNT)
os.environ["MKL_NUM_THREADS"] = str(_CPU_COUNT)
os.environ["HF_HOME"] = HF_CACHE_DIR
# Lazy CUDA-Module-Loading verkürzt die Startzeit spürbar (weniger Kernel-JIT beim Import)
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
LLM_MODEL_PATH = os.path.join(MODELS_DIR, "Qwen2.5-7B-Instruct-Q4_K_M.gguf")

# ── GPU-Tuning-Parameter (per ENV überschreibbar) ────────────────────────────
# Defaults sind für 24GB-Karten (z.B. RTX 4090) ausgelegt: Qwen2.5-7B-Q4 (~4.7GB)
# + Whisper-small (~1.5GB) lassen selbst bei n_ctx=16384 noch ~15GB VRAM frei.
# Für 16GB-Karten (z.B. RTX 5060 Ti) setze LLM_N_CTX=8192 LLM_N_BATCH=1024 als ENV.
LLM_N_CTX = int(os.environ.get("LLM_N_CTX", 16384))
LLM_N_BATCH = int(os.environ.get("LLM_N_BATCH", 2048))
LLM_N_UBATCH = int(os.environ.get("LLM_N_UBATCH", 2048))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", 40))
STT_COMPUTE_TYPE = os.environ.get("STT_COMPUTE_TYPE", "float16")
STT_MODEL_SIZE = os.environ.get("STT_MODEL_SIZE", "small")

# ── Global State ────────────────────────────────────────────────────────────
_tool_registry: dict = {}
_tool_results: dict = {}
_pending_sessions: dict = {}
_pending_lock = threading.Lock()

# ── STT ───────────────────────────────────────────────────────────────────────
print(f"[STT] Lade Whisper ({STT_MODEL_SIZE}, {STT_COMPUTE_TYPE})...")
start_time = time.time()
stt_model = WhisperModel(
    STT_MODEL_SIZE,
    device="cuda",
    device_index=0,
    compute_type=STT_COMPUTE_TYPE,
    download_root=HF_CACHE_DIR,
    cpu_threads=_CPU_COUNT,
    num_workers=2,          # überlappt Feature-Extraction (CPU) mit GPU-Decode
)
print(f"[STT] Whisper bereit in {time.time() - start_time:.2f}s")

# ── TTS ───────────────────────────────────────────────────────────────────────
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
print(f"[AI] Lade LLM (n_ctx={LLM_N_CTX}, n_batch={LLM_N_BATCH})...")
start_time = time.time()
try:
    _llm_kwargs = dict(
        model_path=LLM_MODEL_PATH,
        n_ctx=LLM_N_CTX,
        n_gpu_layers=-1,        # alle Layer auf die GPU
        n_batch=LLM_N_BATCH,
        flash_attn=True,        # nutzt Tensor Cores, Blackwell profitiert stark davon
        n_threads=_CPU_COUNT,
        main_gpu=0,
        offload_kqv=True,       # KV-Cache ebenfalls auf GPU statt RAM
        verbose=False,
    )
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

        with open(temp_path, 'wb') as f:
            tts_voice.synthesize(text, f)

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
        "tts_available": tts_voice is not None,
        "llm_available": llm is not None,
        "tools_count": len(_tool_registry),
        "registered_tools": list(_tool_registry.keys()),
        "pending_sessions": len(_pending_sessions),
        "gpu_queue_depth": _gpu_queue.qsize(),
    })


@app.route("/gpu_status", methods=["GET"])
def gpu_status():
    """Roher nvidia-smi Output zur schnellen Sichtprüfung der GPU-Auslastung/VRAM."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True,
        )
        return jsonify({"gpu": out.stdout.decode().strip()})
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
        "llm_n_ctx": LLM_N_CTX,
        "llm_n_batch": LLM_N_BATCH,
        "stt_compute_type": STT_COMPUTE_TYPE,
        "cpu_threads": _CPU_COUNT,
    })


if __name__ == "__main__":
    print("=" * 60)
    print("SCP-1356 Server startet...")
    print("=" * 60)
    print(f"[START] TTS Voice: {'Verfügbar' if tts_voice is not None else 'NICHT VERFÜGBAR'}")
    print(f"[START] LLM: {'Verfügbar' if llm is not None else 'NICHT VERFÜGBAR'}")
    print(f"[START] LLM n_ctx={LLM_N_CTX} n_batch={LLM_N_BATCH} n_ubatch={LLM_N_UBATCH}")
    print(f"[START] STT compute_type={STT_COMPUTE_TYPE}")

    _warmup()

    print("[START] Server läuft auf 0.0.0.0:5000 (threaded=True)")
    print("=" * 60)
    # threaded=True: Flask nimmt mehrere Requests gleichzeitig an (I/O-parallel),
    # die eigentliche GPU-Arbeit läuft trotzdem sicher seriell über den Worker.
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)