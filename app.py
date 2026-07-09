import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
HF_CACHE_DIR = os.path.join(BASE_DIR, "hf_cache")

os.environ["OMP_NUM_THREADS"] = "12"
os.environ["MKL_NUM_THREADS"] = "12"
os.environ["HF_HOME"] = HF_CACHE_DIR

import re
import json
import io
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

app = Flask(__name__)

# ── Pfade zu lokalen Modellen ────────────────────────────────────────────────
TTS_MODEL_PATH = os.path.join(MODELS_DIR, "de_DE-thorsten-high.onnx")
LLM_MODEL_PATH = os.path.join(MODELS_DIR, "Qwen2.5-7B-Instruct-Q4_K_M.gguf")

# ── Global State ────────────────────────────────────────────────────────────
_tool_registry: dict = {}
_tool_results: dict = {}

# Speichert den Kontext eines laufenden Gesprächs, das auf Tool-Ergebnisse wartet
# Key: session_id (z.B. SteamID des Spielers), Value: dict mit original_text
_pending_sessions: dict = {}

# ── STT ───────────────────────────────────────────────────────────────────────
print("[STT] Lade Whisper...")
start_time = time.time()
stt_model = WhisperModel(
    "small",
    device="cuda",
    compute_type="float16",
    download_root=HF_CACHE_DIR,
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
print("[AI] Lade LLM...")
start_time = time.time()
try:
    llm = Llama(
        model_path=LLM_MODEL_PATH,
        n_ctx=4096,
        n_gpu_layers=-1,
        n_batch=512,
        flash_attn=True,
        n_threads=12,
        verbose=False,
    )
    print(f"[AI] LLM bereit in {time.time() - start_time:.2f}s")
except Exception as e:
    import traceback
    traceback.print_exc()
    llm = None

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
    print(f"[PROMPT] Erstelle System-Prompt mit {len(_tool_registry)} Tools")

    if not _tool_registry:
        print("[PROMPT] Keine Tools registriert")
        return SYSTEM_PROMPT_BASE

    tool_lines = ["Verfügbare Tools:"]
    for name, info in _tool_registry.items():
        params = ", ".join(
            f"{p['name']}: {p['type']}" for p in info.get("params", [])
        )
        tool_lines.append(f"- {name}({params}): {info.get('description', '')}")
        print(f"[PROMPT] Tool: {name} mit Parametern: {params}")

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
    """Erster LLM-Aufruf oder zweiter mit Tool-Ergebnissen."""
    print(f"[AI] Starte Anfrage: {player_text!r}")
    print(f"[AI] Tool-Ergebnisse vorhanden: {tool_results is not None and len(tool_results) > 0}")

    if llm is None:
        print("[AI] LLM nicht verfügbar")
        return {"speech": "Entschuldigung, aber meine Gedanken sind gerade... woanders.", "actions": []}

    system = build_system_prompt()

    if tool_results:
        # Zweiter Schritt: Mit Tool-Ergebnissen
        # Wir instruieren das Modell explizit, KEINE weiteren Tools aufzurufen
        tool_section = "\n\nDu hast folgende Informationen erhalten:\n"
        for tool_name, result in tool_results.items():
            tool_section += f"\n[{tool_name}]:\n{result}\n"
        tool_section += (
            "\nBeantworte nun die Frage des Spielers mit diesen Informationen. "
            "Rufe KEINE weiteren Tools auf. Setze 'actions' auf []."
        )

        # Simuliere einen Gesprächsverlauf: user → assistant (tool call) → tool results → final answer
        prompt = (
            f"<|system|>\n{system}<|end|>\n"
            f"<|user|>\n{player_text}<|end|>\n"
            f"<|assistant|>\n{tool_section}\n"
            f"<|assistant|>\n"
        )
        print(f"[AI] Prompt-Länge (2. Schritt): {len(prompt)} Zeichen")
    else:
        # Erster Schritt: Normale Anfrage
        prompt = f"<|system|>\n{system}<|end|>\n<|user|>\n{player_text}<|end|>\n<|assistant|>\n"
        print(f"[AI] Prompt-Länge (1. Schritt): {len(prompt)} Zeichen")

    start_time = time.time()
    try:
        result = llm(
            prompt,
            max_tokens=40,
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
    print(f"[AI] Raw output: {raw!r}")

    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        print(f"[AI] KEIN JSON gefunden — nutze raw als speech")
        speech_text = raw[:120] if raw else "Ich... ich kann nicht sprechen."
        return {"speech": speech_text, "actions": []}

    json_str = match.group(0)

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[AI] JSON-Fehler: {e}, versuche zu reparieren...")
        try:
            repaired = repair_json(json_str)
            print(f"[AI] Repariertes JSON: {repaired!r}")
            parsed = json.loads(repaired)
        except json.JSONDecodeError as e2:
            print(f"[AI] Reparatur fehlgeschlagen: {e2}")
            speech_match = re.search(r'"speech"\s*:\s*"([^"]*)"', json_str)
            if speech_match:
                return {"speech": speech_match.group(1), "actions": []}
            return {"speech": raw[:120] if raw else "Meine Worte... sie zerfallen.", "actions": []}

    speech = parsed.get('speech', '')
    actions = parsed.get('actions', [])

    if not isinstance(actions, list):
        print(f"[AI] actions ist kein Array: {actions}")
        actions = []

    print(f"[AI] speech: {speech!r}, actions: {actions}")

    if not speech:
        parsed['speech'] = "Ich... ich kann nicht sprechen."

    return parsed

def synthesize_speech(text: str) -> np.ndarray:
    """Synthetisiert Sprache mit Piper TTS 1.4.2 und gibt PCM als float32 Array zurück."""
    print(f"[TTS] Synthetisiere: {text!r}")

    if tts_voice is None:
        print(f"[TTS] TTS nicht verfügbar!")
        return np.array([], dtype=np.float32)

    if not text or text.strip() == "":
        print(f"[TTS] Text ist leer")
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

            print(f"[TTS] WAV: {n_frames} frames, {sample_rate}Hz, {n_channels} Kanäle, {samp_width} bytes/Sample")

            if n_frames == 0:
                print("[TTS] WARNING: Keine Audio-Daten erzeugt!")
                return np.array([], dtype=np.float32)

        if samp_width == 2:
            pcm = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        elif samp_width == 1:
            pcm = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
        else:
            print(f"[TTS] Nicht unterstützte Sample-Breite: {samp_width}")
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
            print(f"[TTS] Resample von {sample_rate}Hz auf 48000Hz")
            pcm = resample_poly(pcm, up=up, down=down).astype(np.float32)

        max_val = np.max(np.abs(pcm))
        if max_val > 0:
            pcm = pcm / max_val * 0.90

        print(f"[TTS] Final: {len(pcm)} samples @48kHz")
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
            except:
                pass

def synthesize_speech_fallback(text: str) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name

    try:
        subprocess.run(
            [
                "piper",
                "--model", TTS_MODEL_PATH,
                "--output_file", output_path,
            ],
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
    """Hilfsfunktion: TTS generieren und fertiges Response-Dict bauen."""
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

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/transcribe", methods=["POST"])
def transcribe():
    print(f"[REQUEST] Transcribe-Anfrage erhalten")
    start_time_total = time.time()

    raw = request.data
    print(f"[REQUEST] Daten-Länge: {len(raw)} Bytes")

    if not raw:
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    # ── Audio-Konvertierung ───────────────────────────────────────────────────
    try:
        pcm_48k = np.frombuffer(raw, dtype=np.float32).copy()
        pcm_16k = resample_poly(pcm_48k, up=1, down=3).astype(np.float32)
        print(f"[AUDIO] {len(pcm_16k)/16000:.2f}s Audio empfangen")
    except Exception as e:
        print(f"[AUDIO] FEHLER: {e}")
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    if len(pcm_16k) < 16000 * 0.3:
        print(f"[AUDIO] Zu kurz")
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    # ── STT ──────────────────────────────────────────────────────────────────
    try:
        segments, info = stt_model.transcribe(
            pcm_16k,
            language="de",
            beam_size=1,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=180, speech_pad_ms=80),
        )
    except Exception as e:
        print(f"[STT] FEHLER: {e}")
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    text = " ".join(s.text for s in segments).strip()
    print(f"[STT] Erkannt: {text!r}")

    if not text:
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    # ── Erster AI-Schritt ─────────────────────────────────────────────────────
    try:
        ai_result = ask_ai(text)
        speech_text = ai_result.get("speech", "")
        actions = ai_result.get("actions", [])
        print(f"[AI] Erster Schritt: speech={speech_text!r}, actions={actions}")
    except Exception as e:
        print(f"[AI] FEHLER: {e}")
        print(traceback.format_exc())
        speech_text = "Meine Gedanken sind... zersplittert."
        actions = []

    # ── Prüfe ob Info-Tools dabei sind ───────────────────────────────────────
    info_tool_names = [a.get("tool") for a in actions if a.get("tool") in INFO_TOOLS]

    if info_tool_names:
        # Speichere Kontext für den Follow-up
        # Wir verwenden den Text als Key (simpel; bei Mehrspieler: SteamID nutzen)
        session_id = str(hash(text + str(time.time())))
        _pending_sessions[session_id] = {
            "original_text": text,
            "expected_tools": set(info_tool_names),
            "received_tools": set(),
            "tool_results": {},
        }
        print(f"[SESSION] Neue Session {session_id} wartet auf: {info_tool_names}")

        # Zwischen-Antwort als Audio synthetisieren (z.B. "Ich durchsuche meine Gedanken...")
        # C# spielt das direkt ab; die finale Antwort kommt später via /followup
        between_audio = []
        if speech_text:
            try:
                pcm = synthesize_speech(speech_text)
                if len(pcm) > 0:
                    between_audio = pcm.tolist()
            except Exception as e:
                print(f"[TTS] FEHLER bei Zwischen-Antwort: {e}")

        print(f"[REQUEST] Fertig in {time.time() - start_time_total:.2f}s (wartet auf Tool-Ergebnisse)")
        return jsonify({
            "text": text,
            "response": speech_text,       # C# kann das optional anzeigen
            "actions": actions,
            "audio": between_audio,        # Zwischen-Antwort — finales Audio kommt via /followup
            "session_id": session_id,      # C# muss das mitspeichern und bei /followup mitschicken
            "awaiting_tools": True,        # Hinweis für C#: bitte /followup aufrufen
        })
    else:
        # Keine Info-Tools → direkt antworten
        response = build_tts_response(speech_text, actions)
        response["text"] = text
        response["awaiting_tools"] = False
        print(f"[REQUEST] Fertig in {time.time() - start_time_total:.2f}s")
        return jsonify(response)


@app.route("/tts", methods=["POST"])
def tts_only():
    """
    Reine TTS-Route ohne LLM — synthetisiert den gegebenen Text direkt.
    Body (JSON): { "text": "..." }
    Genutzt z.B. von C# Speak()/scp1356 speak <text>.
    """
    print("[REQUEST] TTS-only Anfrage erhalten")
    start_time = time.time()

    try:
        data = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Ungültiger JSON-Body: {e}"}), 400

    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"text": "", "audio": []})

    print(f"[TTS-ONLY] Text: {text!r}")

    audio_samples = []
    try:
        pcm = synthesize_speech(text)
        if len(pcm) > 0:
            audio_samples = pcm.tolist()
    except Exception as e:
        print(f"[TTS-ONLY] FEHLER: {e}")
        print(traceback.format_exc())

    print(f"[TTS-ONLY] Fertig in {time.time() - start_time:.2f}s")
    return jsonify({"text": text, "audio": audio_samples})


@app.route("/prompt", methods=["POST"])
def prompt():
    """
    Nimmt direkten Text entgegen (kein Audio/STT), z.B. von C# SendPrompt().
    Body (JSON): { "text": "..." }
    Verhält sich identisch zu /transcribe ab dem AI-Schritt.
    """
    print("[REQUEST] Prompt-Anfrage erhalten")
    start_time_total = time.time()

    try:
        data = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Ungültiger JSON-Body: {e}"}), 400

    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"text": "", "response": "", "actions": [], "audio": []})

    print(f"[PROMPT] Text: {text!r}")

    # ── Erster AI-Schritt ─────────────────────────────────────────────────────
    try:
        ai_result = ask_ai(text)
        speech_text = ai_result.get("speech", "")
        actions = ai_result.get("actions", [])
        print(f"[AI] Erster Schritt: speech={speech_text!r}, actions={actions}")
    except Exception as e:
        print(f"[AI] FEHLER: {e}")
        print(traceback.format_exc())
        speech_text = "Meine Gedanken sind... zersplittert."
        actions = []

    info_tool_names = [a.get("tool") for a in actions if a.get("tool") in INFO_TOOLS]

    if info_tool_names:
        session_id = str(hash(text + str(time.time())))
        _pending_sessions[session_id] = {
            "original_text": text,
            "expected_tools": set(info_tool_names),
            "received_tools": set(),
            "tool_results": {},
        }
        print(f"[SESSION] Neue Session {session_id} wartet auf: {info_tool_names}")

        between_audio = []
        if speech_text:
            try:
                pcm = synthesize_speech(speech_text)
                if len(pcm) > 0:
                    between_audio = pcm.tolist()
            except Exception:
                pass

        print(f"[REQUEST] Fertig in {time.time() - start_time_total:.2f}s (awaiting_tools)")
        return jsonify({
            "text": text,
            "response": speech_text,
            "actions": actions,
            "audio": between_audio,
            "session_id": session_id,
            "awaiting_tools": True,
        })
    else:
        response = build_tts_response(speech_text, actions)
        response["text"] = text
        response["awaiting_tools"] = False
        print(f"[REQUEST] Fertig in {time.time() - start_time_total:.2f}s")
        return jsonify(response)


@app.route("/followup", methods=["POST"])
def followup():
    """
    C# ruft diesen Endpoint auf, nachdem alle Tool-Ergebnisse per /tool_result
    eingetragen wurden.

    Body (JSON):
    {
        "session_id": "...",
        "tool_results": {          // Optional: C# kann Ergebnisse direkt mitschicken
            "GetStatus": "...",    // statt vorher /tool_result aufzurufen
            "GetEvents": "..."
        }
    }
    """
    print("[FOLLOWUP] Follow-up Anfrage erhalten")
    start_time = time.time()

    try:
        data = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Ungültiger JSON-Body: {e}"}), 400

    session_id = data.get("session_id")
    inline_results = data.get("tool_results", {})  # Optional: direkt mitgeschickte Ergebnisse

    # ── Session laden ─────────────────────────────────────────────────────────
    if session_id and session_id in _pending_sessions:
        session = _pending_sessions.pop(session_id)
        original_text = session["original_text"]
        # Merge: erst gespeicherte Ergebnisse, dann inline überschreiben
        tool_results = {**session.get("tool_results", {}), **inline_results}
        print(f"[FOLLOWUP] Session {session_id} geladen: original_text={original_text!r}")
    elif inline_results:
        # Kein session_id, aber direkte Ergebnisse + original_text im Body
        original_text = data.get("original_text", "")
        tool_results = inline_results
        print(f"[FOLLOWUP] Kein Session-ID, nutze inline Daten: {original_text!r}")
    else:
        print(f"[FOLLOWUP] Session {session_id!r} nicht gefunden")
        return jsonify({"error": "Session nicht gefunden oder abgelaufen"}), 404

    if not tool_results:
        print("[FOLLOWUP] Keine Tool-Ergebnisse vorhanden")
        return jsonify({"error": "Keine Tool-Ergebnisse"}), 400

    print(f"[FOLLOWUP] Tool-Ergebnisse: {list(tool_results.keys())}")

    # ── Zweiter AI-Schritt ────────────────────────────────────────────────────
    try:
        ai_result = ask_ai(original_text, tool_results)
        speech_text = ai_result.get("speech", "")
        # Im zweiten Schritt keine weiteren Actions erlaubt
        print(f"[FOLLOWUP] Finale Antwort: {speech_text!r}")
    except Exception as e:
        print(f"[FOLLOWUP] AI-FEHLER: {e}")
        print(traceback.format_exc())
        speech_text = "Die Informationen... sie verwirren mich."

    # ── TTS ───────────────────────────────────────────────────────────────────
    response = build_tts_response(speech_text, [])
    print(f"[FOLLOWUP] Fertig in {time.time() - start_time:.2f}s")
    return jsonify(response)


@app.route("/tool_result", methods=["POST"])
def tool_result():
    """
    Erhält Tool-Ergebnisse vom C#-Server.

    Body (JSON):
    {
        "tool": "GetStatus",
        "result": "...",
        "session_id": "..."   // Optional: weist Ergebnis einer Session zu
    }
    """
    global _tool_results
    try:
        data = request.get_json(force=True) or {}
        tool_name = data.get("tool")
        result = data.get("result")
        session_id = data.get("session_id")

        if not tool_name or result is None:
            return jsonify({"status": "error", "error": "tool und result erforderlich"}), 400

        # In Session speichern (falls vorhanden)
        if session_id and session_id in _pending_sessions:
            _pending_sessions[session_id]["tool_results"][tool_name] = result
            _pending_sessions[session_id]["received_tools"].add(tool_name)
            print(f"[TOOL RESULT] {tool_name} → Session {session_id}")
        else:
            # Globaler Fallback (für alte C#-Integration ohne Session-ID)
            _tool_results[tool_name] = result
            if len(_tool_results) > 20:
                oldest = next(iter(_tool_results))
                del _tool_results[oldest]
            print(f"[TOOL RESULT] {tool_name} (global, kein Session-Match)")

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"[TOOL RESULT] Fehler: {e}")
        return jsonify({"status": "error", "error": str(e)}), 400


@app.route("/register_tools", methods=["POST"])
def register_tools():
    global _tool_registry
    print("[TOOLS] Registriere Tools...")
    try:
        data = request.get_json(force=True) or {}
        _tool_registry = data
        print(f"[TOOLS] {len(_tool_registry)} Tools registriert: {list(_tool_registry.keys())}")
        for name, info in _tool_registry.items():
            print(f"[TOOLS]   - {name}: {info.get('description', 'keine Beschreibung')}")
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
    })


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
    })


if __name__ == "__main__":
    print("=" * 60)
    print("SCP-1356 Server startet...")
    print("=" * 60)
    print(f"[START] TTS Voice: {'Verfügbar' if tts_voice is not None else 'NICHT VERFÜGBAR'}")
    print(f"[START] LLM: {'Verfügbar' if llm is not None else 'NICHT VERFÜGBAR'}")
    print("[START] Server läuft auf 0.0.0.0:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, threaded=False, debug=False)
