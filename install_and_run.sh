#!/bin/bash
set -euo pipefail

REPO_URL="https://github.com/Site-RP/SCP1356AI.git"
PROJECT_DIR="SCP1356AI"

# Cloudflare Tunnel Konfiguration
CF_HOSTNAME="app.ducktales.online"
CF_LOCAL_PORT=5000
# Tunnel-Token aus dem Cloudflare Zero Trust Dashboard (Networks -> Tunnels ->
# dein Tunnel -> "Install and run a connector" -> Token). Am besten als
# Umgebungsvariable setzen statt hart im Skript, z.B.:
#   export CF_TUNNEL_TOKEN="eyJ..."
#   ./install.sh
CF_TUNNEL_TOKEN="${CF_TUNNEL_TOKEN:-}"

# ── Helper ───────────────────────────────────────────────────────────────────

log()  { echo -e "\n\033[1;32m$1\033[0m"; }
warn() { echo -e "\033[1;33m$1\033[0m" >&2; }
err()  { echo -e "\033[1;31m$1\033[0m" >&2; }

trap 'err "Fehler in Zeile $LINENO. Abbruch."' ERR

# ── [0/8] Root-Check ─────────────────────────────────────────────────────────

if [ "$EUID" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
        warn "Skript läuft nicht als root — verwende sudo für apt-Befehle."
    else
        err "Bitte als root ausführen oder sudo installieren (für apt-get benötigt)."
        exit 1
    fi
else
    SUDO=""
fi

# ── [1/9] System-Pakete ──────────────────────────────────────────────────────

log "[1/9] System prüfen und Pakete installieren..."
$SUDO apt-get update
$SUDO apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1

# ── [2/9] GPU / CUDA Erkennung ───────────────────────────────────────────────

log "[2/9] GPU-Erkennung..."
USE_CUDA=0
if command -v nvidia-smi >/dev/null 2>&1; then
    if nvidia-smi >/dev/null 2>&1; then
        log "NVIDIA-GPU gefunden:"
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
        if command -v nvcc >/dev/null 2>&1; then
            log "CUDA-Toolkit (nvcc) gefunden — Build mit CUDA-Unterstützung."
            USE_CUDA=1
        else
            warn "nvidia-smi vorhanden, aber 'nvcc' (CUDA-Toolkit) fehlt."
            warn "llama-cpp-python würde ohne nvcc NICHT mit CUDA kompilieren können."
            warn "Installiere ggf. das CUDA-Toolkit (z.B. via 'apt-get install nvidia-cuda-toolkit')"
            warn "oder fahre ohne GPU-Beschleunigung fort (CPU-Fallback)."
        fi
    else
        warn "nvidia-smi vorhanden, aber Zugriff fehlgeschlagen — fahre mit CPU fort."
    fi
else
    warn "Keine NVIDIA-GPU gefunden — Build läuft im CPU-Modus (langsamer)."
fi

# ── [3/9] Repository ─────────────────────────────────────────────────────────

log "[3/9] Repository vorbereiten..."
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Repository existiert bereits, aktualisiere..."
    cd "$PROJECT_DIR"
    git pull --ff-only || warn "git pull fehlgeschlagen (lokale Änderungen?) — fahre mit vorhandenem Stand fort."
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

if [ ! -f "requirements.txt" ]; then
    err "requirements.txt nicht gefunden — falsches Repo oder Clone fehlgeschlagen."
    exit 1
fi

# ── [4/9] Virtual Environment ────────────────────────────────────────────────

log "[4/9] Virtual Environment einrichten..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# ── [5/9] Python-Abhängigkeiten ──────────────────────────────────────────────

log "[5/9] Python-Abhängigkeiten installieren..."
python -m pip install --upgrade pip wheel setuptools

if [ "$USE_CUDA" -eq 1 ]; then
    export CMAKE_ARGS="-DGGML_CUDA=ON"
    export FORCE_CMAKE=1
else
    # Explizit CPU-only bauen, damit kein halbfertiger CUDA-Build versucht wird
    export CMAKE_ARGS="-DGGML_CUDA=OFF"
    unset FORCE_CMAKE || true
fi

pip install -r requirements.txt
pip install -U "huggingface_hub[cli]"

mkdir -p models

# ── [6/9] Piper (TTS) herunterladen ──────────────────────────────────────────

log "[6/9] Piper TTS-Modell herunterladen..."
if [ ! -f models/de_DE-thorsten-high.onnx ]; then
    wget --tries=3 -O models/de_DE-thorsten-high.onnx \
        https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
fi
if [ ! -f models/de_DE-thorsten-high.onnx.json ]; then
    wget --tries=3 -O models/de_DE-thorsten-high.onnx.json \
        https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
fi

# ── [7/9] Qwen LLM herunterladen ─────────────────────────────────────────────

log "[7/9] Qwen2.5-7B-Instruct (GGUF) herunterladen..."
if [ ! -f models/Qwen2.5-7B-Instruct-Q4_K_M.gguf ]; then
    huggingface-cli download \
        Qwen/Qwen2.5-7B-Instruct-GGUF \
        Qwen2.5-7B-Instruct-Q4_K_M.gguf \
        --local-dir models

    # Manche huggingface_hub-Versionen legen die Datei in einem Unterordner ab
    # statt flach im Zielverzeichnis — hier absichern und ggf. verschieben.
    if [ ! -f models/Qwen2.5-7B-Instruct-Q4_K_M.gguf ]; then
        FOUND_FILE=$(find models -name "Qwen2.5-7B-Instruct-Q4_K_M.gguf" -print -quit)
        if [ -n "$FOUND_FILE" ]; then
            mv "$FOUND_FILE" models/Qwen2.5-7B-Instruct-Q4_K_M.gguf
        else
            err "Qwen-Modell konnte nicht gefunden werden nach dem Download."
            exit 1
        fi
    fi
fi

# ── [8/9] Cloudflare Tunnel ───────────────────────────────────────────────────

log "[8/9] Cloudflare Tunnel einrichten (Port ${CF_LOCAL_PORT} -> ${CF_HOSTNAME})..."

if ! command -v cloudflared >/dev/null 2>&1; then
    log "Installiere cloudflared..."
    ARCH="$(dpkg --print-architecture)"
    CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb"
    TMP_DEB="$(mktemp --suffix=.deb)"
    wget --tries=3 -O "$TMP_DEB" "$CLOUDFLARED_URL"
    $SUDO dpkg -i "$TMP_DEB" || $SUDO apt-get install -f -y
    rm -f "$TMP_DEB"
else
    log "cloudflared ist bereits installiert ($(cloudflared --version 2>&1 | head -n1))."
fi

# Kein systemd verfügbar (z.B. Jupyter/Container-Umgebung) -> Tunnel als
# einfacher Hintergrundprozess mit nohup, gesteuert über eine PID-Datei.
CF_PID_FILE="$(pwd)/cloudflared.pid"
CF_LOG_FILE="$(pwd)/cloudflared.log"

stop_existing_tunnel() {
    if [ -f "$CF_PID_FILE" ]; then
        OLD_PID="$(cat "$CF_PID_FILE" 2>/dev/null || true)"
        if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
            log "Beende laufenden cloudflared-Prozess (PID $OLD_PID)..."
            kill "$OLD_PID" 2>/dev/null || true
            sleep 1
        fi
        rm -f "$CF_PID_FILE"
    fi
}

if [ -n "$CF_TUNNEL_TOKEN" ]; then
    # ── Non-interaktiver Weg: Named Tunnel per Token ────────────────────────
    # Voraussetzung: Der Tunnel wurde bereits im Cloudflare Zero Trust
    # Dashboard angelegt UND die Public Hostname-Route dort auf
    # "http://localhost:5000" für app.ducktales.online gesetzt.
    stop_existing_tunnel

    log "Starte cloudflared im Hintergrund (nohup, kein systemd)..."
    nohup cloudflared tunnel run --token "$CF_TUNNEL_TOKEN" \
        > "$CF_LOG_FILE" 2>&1 &
    NEW_PID=$!
    disown "$NEW_PID" 2>/dev/null || true
    echo "$NEW_PID" > "$CF_PID_FILE"

    sleep 2
    if kill -0 "$NEW_PID" 2>/dev/null; then
        log "cloudflared läuft im Hintergrund (PID $NEW_PID). Log: $CF_LOG_FILE"
    else
        err "cloudflared ist sofort abgestürzt. Prüfe das Log:"
        tail -n 30 "$CF_LOG_FILE" || true
        exit 1
    fi

    log "Stelle sicher, dass im Cloudflare Dashboard unter deinem Tunnel eine"
    log "Public Hostname-Route existiert: ${CF_HOSTNAME} -> http://localhost:${CF_LOCAL_PORT}"
    log ""
    log "Zum späteren Stoppen: kill \$(cat \"$CF_PID_FILE\")"
else
    warn "Keine CF_TUNNEL_TOKEN gesetzt — es kann kein Named Tunnel für"
    warn "${CF_HOSTNAME} automatisch/nicht-interaktiv eingerichtet werden."
    warn ""
    warn "So richtest du es einmalig ein:"
    warn "  1. https://one.dash.cloudflare.com -> Networks -> Tunnels -> Create a tunnel"
    warn "  2. Connector-Typ 'cloudflared' wählen, Token kopieren"
    warn "  3. Public Hostname hinzufügen: ${CF_HOSTNAME} -> http://localhost:${CF_LOCAL_PORT}"
    warn "  4. Skript erneut ausführen mit:"
    warn "       export CF_TUNNEL_TOKEN=\"<dein-token>\""
    warn "       ./install.sh"
    warn ""
    warn "Alternativ als schneller Test OHNE eigene Domain (temporäre trycloudflare.com-URL):"
    warn "  nohup cloudflared tunnel --url http://localhost:${CF_LOCAL_PORT} > cloudflared.log 2>&1 &"
    warn "  disown"
    warn ""
    warn "Fahre trotzdem mit dem lokalen Start von app.py fort (nur über localhost:${CF_LOCAL_PORT} erreichbar)."
fi

# ── [9/9] Start ───────────────────────────────────────────────────────────────

log "[9/9] SCP1356AI wird gestartet..."
exec python app.py
