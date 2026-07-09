# SCP-1356 Server

Flask-basierter Voice-AI-Server für SCP-1356: nimmt Sprachaudio oder Text entgegen,
transkribiert es (Whisper), lässt ein lokales LLM (Qwen2.5-7B-Instruct, GGUF) antworten
und synthetisiert die Antwort per Piper TTS. Unterstützt zusätzlich ein Tool-Call-Protokoll
für einen externen (z.B. C#/Unity/SCP:SL) Server, der Informations- und Aktions-Tools bereitstellt.

## Projektstruktur

```
scp1356-server/
├── app.py                  # Flask-Server (STT → LLM → TTS, Tool-Calling)
├── requirements.txt         # Python-Abhängigkeiten
├── .gitignore
├── README.md
├── models/
│   ├── de_DE-thorsten-high.onnx        # Piper TTS Stimme
│   └── Qwen2.5-7B-Instruct-Q4_K_M.gguf # LLM-Gewichte (llama.cpp GGUF)
└── hf_cache/                # HF_HOME Cache (für faster-whisper Modell-Downloads)
```

> **Hinweis:** Die Dateien unter `models/` sind nicht im Repository enthalten (siehe `.gitignore`).
> Lade sie manuell herunter und lege sie unter den oben genannten Namen im `models/`-Ordner ab:
> - Piper-Stimme `de_DE-thorsten-high.onnx` (+ zugehörige `.onnx.json`)
> - Qwen2.5-7B-Instruct GGUF-Quantisierung `Qwen2.5-7B-Instruct-Q4_K_M.gguf`
>   (z.B. von `bartowski/Qwen2.5-7B-Instruct-GGUF`)

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`llama-cpp-python` benötigt für GPU-Beschleunigung ggf. einen speziellen Build
(CUDA/cuBLAS). Siehe die offizielle Dokumentation des Pakets für Installationsoptionen
mit GPU-Support.

Lege die Modelldateien wie oben beschrieben in `models/` ab.

## Start

```bash
python app.py
```

Der Server läuft danach auf `0.0.0.0:5000`.

## Endpoints

| Route             | Methode | Beschreibung                                              |
|-------------------|---------|-------------------------------------------------------------|
| `/transcribe`      | POST    | Rohes PCM-Float32-Audio (48kHz) → STT → LLM → TTS           |
| `/tts`             | POST    | `{ "text": "..." }` → reine TTS-Synthese ohne LLM            |
| `/prompt`          | POST    | `{ "text": "..." }` → direkte LLM-Anfrage (ohne STT)          |
| `/followup`        | POST    | Zweiter LLM-Schritt mit Tool-Ergebnissen                     |
| `/tool_result`     | POST    | Externer Server liefert Tool-Ergebnis ein                    |
| `/register_tools`  | POST    | Registriert verfügbare Tools inkl. Parametern                |
| `/health`          | GET     | Statusübersicht (Modelle geladen, Tools, offene Sessions)     |
| `/debug_info`      | GET     | Detaillierte Debug-Informationen                             |

## Umgebungsvariablen

`app.py` setzt beim Start automatisch:
- `OMP_NUM_THREADS`, `MKL_NUM_THREADS` → Thread-Limits für CPU-Bibliotheken
- `HF_HOME` → zeigt auf `./hf_cache`, damit Whisper-Modell-Downloads lokal im Projekt landen