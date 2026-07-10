#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# SCP-1356 AI Server – Full Installer
# Klont https://github.com/Site-RP/SCP1356AI, installiert CUDA, alle Python-
# Abhängigkeiten in einem venv, installiert (aber startet NICHT) cloudflared,
# und startet den Server am Ende per nohup.
#
# One-Liner, um NUR dieses Skript zu holen und direkt auszuführen:
#   curl -fsSL https://raw.githubusercontent.com/Site-RP/SCP1356AI/main/install.sh -o install.sh && chmod +x install.sh && ./install.sh
#
# (Passe den Branch-Namen "main" an, falls dein Repo z.B. "master" nutzt.)
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

# ── Konfiguration ────────────────────────────────────────────────────────
REPO_URL="https://github.com/Site-RP/SCP1356AI.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/SCP1356AI}"
VENV_DIR="${INSTALL_DIR}/venv"
CUDA_VERSION="12-8"                 # apt-Paketsuffix, z.B. cuda-toolkit-12-8 (Blackwell/sm_120 braucht >=12.8)
CUDNN_PACKAGE="cudnn9-cuda-12"       # cuDNN 9 wird für CUDA 12.8 benötigt
SERVER_ENTRY="${SERVER_ENTRY:-server.py}"   # Passe an, falls die Startdatei anders heißt
LOG_FILE="${INSTALL_DIR}/server.log"

log()  { echo -e "\n\033[1;32m[INSTALL]\033[0m $*"; }
warn() { echo -e "\n\033[1;33m[WARN]\033[0m $*"; }
err()  { echo -e "\n\033[1;31m[ERROR]\033[0m $*" >&2; }

if [[ $EUID -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

# ── 1. System-Pakete ─────────────────────────────────────────────────────
log "Aktualisiere Paketlisten und installiere Basis-Pakete..."
$SUDO apt-get update -y
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential cmake ninja-build pkg-config \
    git wget curl unzip ca-certificates gnupg lsb-release \
    python3 python3-venv python3-dev python3-pip \
    ffmpeg libsndfile1 libssl-dev \
    software-properties-common apt-transport-https

# ── 2. NVIDIA Treiber-Check + CUDA Toolkit ───────────────────────────────
log "Prüfe NVIDIA-Treiber..."
if ! command -v nvidia-smi &>/dev/null; then
    warn "nvidia-smi nicht gefunden. Stelle sicher, dass der NVIDIA-Treiber"
    warn "auf dem HOST installiert ist bzw. --gpus all beim Docker-Run gesetzt ist."
else
    nvidia-smi || true
fi

# Automatische Erkennung der GPU-Architektur (Compute Capability) statt fest
# codierter Werte — funktioniert für V100 (70), Ampere (80/86), Ada/RTX 4090 (89),
# Blackwell/RTX 50-Serie (120) etc. Override per: GPU_ARCH=89 ./install.sh
GPU_ARCH="${GPU_ARCH:-auto}"
if [[ "$GPU_ARCH" == "auto" ]] && command -v nvidia-smi &>/dev/null; then
    RAW_CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader -i 0 2>/dev/null | head -1)
    if [[ -n "$RAW_CC" ]]; then
        GPU_ARCH=$(echo "$RAW_CC" | tr -d '.' | tr -d ' ')
        log "GPU Compute Capability erkannt: ${RAW_CC} → sm_${GPU_ARCH}"
    else
        GPU_ARCH="89"
        warn "Konnte Compute Capability nicht auslesen, nutze Ada-Default sm_89 (RTX 4090)."
    fi
elif [[ "$GPU_ARCH" == "auto" ]]; then
    GPU_ARCH="89"
    warn "nvidia-smi nicht gefunden, nutze Ada-Default sm_89 (RTX 4090)."
fi

# Blackwell (RTX 50-Serie) braucht CUDA >= 12.8. Ada/RTX 4090 läuft ab CUDA 12.0
# problemlos — CUDA 12.8 funktioniert dank Abwärtskompatibilität aber genauso gut,
# daher lassen wir den Toolkit-Wert oben unverändert bei 12-8, das ist die sichere
# Wahl für beide Kartengenerationen.
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader -i 0 2>/dev/null || echo "unbekannt")
    log "Erkannte GPU: ${GPU_NAME}"
    if echo "$GPU_NAME" | grep -qiE "RTX 50|B100|B200|GB2"; then
        log "Blackwell-GPU erkannt — CUDA ${CUDA_VERSION}+ und aktueller Treiber sind Pflicht."
    fi
fi

if ! command -v nvcc &>/dev/null || ! nvcc --version | grep -q "release 12\.\(8\|9\)\|release 1[3-9]\."; then
    log "Installiere/aktualisiere CUDA Toolkit ${CUDA_VERSION}..."
    UBUNTU_CODENAME=$(lsb_release -cs 2>/dev/null || echo "jammy")
    UBUNTU_VER=$(lsb_release -rs 2>/dev/null | tr -d '.')
    CUDA_KEYRING_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${UBUNTU_VER}/x86_64/cuda-keyring_1.1-1_all.deb"
    TMP_DEB="/tmp/cuda-keyring.deb"

    if wget -q "$CUDA_KEYRING_URL" -O "$TMP_DEB"; then
        $SUDO dpkg -i "$TMP_DEB"
        $SUDO apt-get update -y
        if ! $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y "cuda-toolkit-${CUDA_VERSION}"; then
            warn "cuda-toolkit-${CUDA_VERSION} nicht verfügbar, versuche generisches 'cuda-toolkit' (neueste Version)..."
            $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y cuda-toolkit || \
                warn "CUDA Toolkit Installation fehlgeschlagen — bitte manuell prüfen: https://developer.nvidia.com/cuda-downloads"
        fi

        # cuDNN 9 (Pflicht für CUDA 12.8 + Blackwell, u.a. für onnxruntime-gpu/ctranslate2)
        log "Installiere cuDNN 9 (${CUDNN_PACKAGE})..."
        $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y "${CUDNN_PACKAGE}" || \
            warn "${CUDNN_PACKAGE} nicht per apt verfügbar — Fallback: pip-Paket nvidia-cudnn-cu12 wird später mitinstalliert."
    else
        warn "Konnte CUDA-Keyring nicht laden (Ubuntu ${UBUNTU_VER} evtl. nicht unterstützt)."
        warn "Bitte CUDA >= 12.8 ggf. manuell installieren: https://developer.nvidia.com/cuda-downloads"
    fi

    # CUDA PATH persistieren
    CUDA_HOME_GUESS="/usr/local/cuda"
    if [[ -d "$CUDA_HOME_GUESS" ]]; then
        {
            echo "export PATH=${CUDA_HOME_GUESS}/bin\${PATH:+:\${PATH}}"
            echo "export LD_LIBRARY_PATH=${CUDA_HOME_GUESS}/lib64\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}"
        } >> "$HOME/.bashrc"
        export PATH="${CUDA_HOME_GUESS}/bin${PATH:+:${PATH}}"
        export LD_LIBRARY_PATH="${CUDA_HOME_GUESS}/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    fi
else
    log "CUDA Toolkit bereits vorhanden und kompatibel: $(nvcc --version | tail -1)"
fi

# Treiber-Version grob prüfen — Mindestanforderung hängt von der Architektur ab:
# Blackwell (sm_120) >= 570.x, Ada/RTX 4090 (sm_89) reicht ab >= 525.x
if command -v nvidia-smi &>/dev/null; then
    DRIVER_VER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader -i 0 2>/dev/null | cut -d. -f1)
    MIN_DRIVER=525
    [[ "$GPU_ARCH" == "120" ]] && MIN_DRIVER=570
    if [[ -n "${DRIVER_VER:-}" ]] && [[ "$DRIVER_VER" -lt "$MIN_DRIVER" ]]; then
        warn "NVIDIA-Treiber ${DRIVER_VER}.x erkannt — für sm_${GPU_ARCH} wird Treiber >= ${MIN_DRIVER}.x empfohlen."
        warn "Bitte Host-Treiber aktualisieren: https://www.nvidia.com/Download/index.aspx"
    fi
fi

# ── 3. Repository klonen ─────────────────────────────────────────────────
log "Klone Repository ${REPO_URL} nach ${INSTALL_DIR}..."
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Repo existiert bereits — führe git pull aus..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# ── 4. Virtuelle Umgebung erstellen + aktivieren ─────────────────────────
log "Erstelle Python venv unter ${VENV_DIR}..."
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

log "Aktualisiere pip/setuptools/wheel..."
pip install --upgrade pip setuptools wheel

# ── 5. requirements.txt installieren (ALLES) ─────────────────────────────
if [[ -f "${INSTALL_DIR}/requirements.txt" ]]; then
    REQ_FILE="${INSTALL_DIR}/requirements.txt"
    log "Nutze requirements.txt aus dem Repository."
else
    REQ_FILE="${INSTALL_DIR}/requirements.txt"
    warn "Keine requirements.txt im Repo gefunden — kopiere mitgelieferte Vollversion."
    cat > "$REQ_FILE" <<'REQEOF'
Flask==3.0.3
Werkzeug==3.0.3
gunicorn==22.0.0
numpy==1.26.4
scipy==1.13.1
faster-whisper==1.0.3
ctranslate2==4.5.0
av==12.3.0
huggingface_hub==0.24.6
tokenizers==0.19.1
onnxruntime-gpu==1.20.1
piper-tts==1.2.0
piper-phonemize==1.1.0
onnx==1.16.2
llama-cpp-python==0.3.9
nvidia-cudnn-cu12==9.3.0.75
requests==2.32.3
tqdm==4.66.5
soundfile==0.12.1
pydub==0.25.1
python-dotenv==1.0.1
psutil==6.0.0
jupyterlab==4.2.5
notebook==7.2.2
ipykernel==6.29.5
ipywidgets==8.1.5
REQEOF
fi

log "Installiere alle Python-Pakete aus requirements.txt..."
pip install -r "$REQ_FILE"

# ── 6. llama-cpp-python explizit MIT CUDA-Support für erkannte Architektur neu bauen ─
# (Das reine pip-Wheel oben ist meist CPU-only – wir erzwingen hier GPU-Build.
#  CMAKE_CUDA_ARCHITECTURES=${GPU_ARCH} zielt auf die oben automatisch erkannte
#  Architektur, z.B. 89 für RTX 4090, 120 für RTX 5060 Ti. Für gemischte Hardware
#  kann GPU_ARCH auch eine Semikolon-Liste sein, z.B. GPU_ARCH="89;120" ./install.sh)
log "Baue llama-cpp-python mit CUDA (GGML_CUDA, sm_${GPU_ARCH}) neu..."
CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=${GPU_ARCH}" FORCE_CMAKE=1 \
    pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python==0.3.9 \
    || warn "CUDA-Build von llama-cpp-python fehlgeschlagen — Fallback auf CPU-Version aus requirements.txt."

# ── 7. Cloudflare Tunnel installieren (NICHT starten) ────────────────────
log "Installiere cloudflared (wird NICHT gestartet)..."
if ! command -v cloudflared &>/dev/null; then
    CLOUDFLARED_DEB="/tmp/cloudflared-linux-amd64.deb"
    ARCH=$(dpkg --print-architecture)
    wget -q "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb" -O "$CLOUDFLARED_DEB"
    $SUDO dpkg -i "$CLOUDFLARED_DEB" || $SUDO apt-get install -f -y
    log "cloudflared installiert: $(cloudflared --version || true)"
else
    log "cloudflared ist bereits installiert."
fi
log "Hinweis: Tunnel wurde NICHT gestartet. Starte ihn manuell z.B. mit:"
log "         cloudflared tunnel --url http://localhost:5000"

# ── 8. Modelle prüfen ─────────────────────────────────────────────────────
MODELS_DIR="${INSTALL_DIR}/models"
mkdir -p "$MODELS_DIR"
if [[ ! -f "${MODELS_DIR}/de_DE-thorsten-high.onnx" ]] || [[ ! -f "${MODELS_DIR}/Qwen2.5-7B-Instruct-Q4_K_M.gguf" ]]; then
    warn "Modelle (Piper .onnx / Qwen .gguf) nicht in ${MODELS_DIR} gefunden."
    warn "Bitte lege 'de_DE-thorsten-high.onnx' (+ .onnx.json) und"
    warn "'Qwen2.5-7B-Instruct-Q4_K_M.gguf' manuell dort ab, bevor der Server startet."
fi

# ── 9. Server per nohup starten ──────────────────────────────────────────
log "Starte Server (${SERVER_ENTRY}) im Hintergrund via nohup..."
cd "$INSTALL_DIR"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
nohup python3 "${SERVER_ENTRY}" > "$LOG_FILE" 2>&1 < /dev/null &
disown
SERVER_PID=$!

sleep 2
if kill -0 "$SERVER_PID" 2>/dev/null; then
    log "Server läuft mit PID ${SERVER_PID}. Logs: tail -f ${LOG_FILE}"
else
    err "Server scheint nicht gestartet zu sein — prüfe ${LOG_FILE}"
fi

log "Fertig! Aktiviere das venv künftig manuell mit:"
log "  source ${VENV_DIR}/bin/activate"