#!/usr/bin/env bash
# ==============================================================================
# SCP-1356 AI - Universal Ubuntu Installer + Starter
#
# Ziel:
#   - Frisches Ubuntu 22.04 / 24.04
#   - CPU-only ODER NVIDIA/CUDA
#   - GitHub-Repo klonen/aktualisieren
#   - Python venv + passende Dependencies installieren
#   - Whisper/faster-whisper, Piper, llama.cpp installieren
#   - Qwen2.5-7B GGUF + Piper Thorsten herunterladen
#   - Transport-Key erzeugen, falls keiner existiert
#   - SCP-1356 AI auf Port 5000 starten
#   - Cloudflare Quick Tunnel OHNE Login starten
#   - Öffentliche URL als LETZTE Ausgabe ausgeben
#
# Nutzung:
#   chmod +x start.sh
#   ./start.sh
#
# Optional:
#   REPO_URL=https://github.com/Site-RP/SCP1356AI.git ./start.sh
#   INSTALL_DIR=/opt/SCP1356AI ./start.sh
#   FORCE_CPU=1 ./start.sh
#   FORCE_REINSTALL=1 ./start.sh
# ==============================================================================

set -Eeuo pipefail
IFS=$'\n\t'

# ------------------------------------------------------------------------------
# Konfiguration
# ------------------------------------------------------------------------------

REPO_URL="${REPO_URL:-https://github.com/Site-RP/SCP1356AI.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

INSTALL_DIR="${INSTALL_DIR:-$HOME/SCP1356AI}"
VENV_DIR="${VENV_DIR:-$INSTALL_DIR/.venv}"
MODELS_DIR="$INSTALL_DIR/models"
LOG_DIR="$INSTALL_DIR/logs"
RUN_DIR="$INSTALL_DIR/run"

APP_PORT="${APP_PORT:-5000}"
APP_HOST="${APP_HOST:-127.0.0.1}"

FORCE_CPU="${FORCE_CPU:-0}"
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"

LLAMA_CPP_VERSION="${LLAMA_CPP_VERSION:-0.3.9}"

LLM_MODEL_NAME="Qwen2.5-7B-Instruct-Q4_K_M.gguf"
LLM_MODEL_URL="${LLM_MODEL_URL:-https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf}"

PIPER_MODEL_NAME="de_DE-thorsten-high.onnx"
PIPER_MODEL_URL="${PIPER_MODEL_URL:-https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx}"
PIPER_CONFIG_URL="${PIPER_CONFIG_URL:-https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json}"

# Richtiger Fallback, falls die obige URL-Struktur von HF abweicht.
PIPER_CONFIG_URL_FALLBACK="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json"

APP_LOG="$LOG_DIR/app.log"
CF_LOG="$LOG_DIR/cloudflared.log"
INSTALL_LOG="$LOG_DIR/install.log"

APP_PID_FILE="$RUN_DIR/app.pid"
CF_PID_FILE="$RUN_DIR/cloudflared.pid"

# ------------------------------------------------------------------------------
# Ausgabe
# ------------------------------------------------------------------------------

NO_COLOR="${NO_COLOR:-0}"
if [[ -t 1 && "$NO_COLOR" != "1" ]]; then
    C_BLUE=$'\033[1;34m'
    C_GREEN=$'\033[1;32m'
    C_YELLOW=$'\033[1;33m'
    C_RED=$'\033[1;31m'
    C_RESET=$'\033[0m'
else
    C_BLUE=""
    C_GREEN=""
    C_YELLOW=""
    C_RED=""
    C_RESET=""
fi

info() { printf '%s[INFO]%s %s\n' "$C_BLUE" "$C_RESET" "$*"; }
ok()   { printf '%s[ OK ]%s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
warn() { printf '%s[WARN]%s %s\n' "$C_YELLOW" "$C_RESET" "$*"; }
die()  { printf '%s[FAIL]%s %s\n' "$C_RED" "$C_RESET" "$*" >&2; exit 1; }

trap 'printf "\n[FAIL] Fehler in Zeile %s. Siehe: %s\n" "$LINENO" "$INSTALL_LOG" >&2' ERR

# ------------------------------------------------------------------------------
# Helfer
# ------------------------------------------------------------------------------

if [[ "$(id -u)" -eq 0 ]]; then
    SUDO=()
else
    command -v sudo >/dev/null 2>&1 || die "sudo fehlt. Installiere sudo oder führe das Skript als root aus."
    SUDO=(sudo)
fi

mkdir -p "$INSTALL_DIR" "$LOG_DIR" "$RUN_DIR"
touch "$INSTALL_LOG"

# Alles außer der finalen URL zusätzlich loggen.
exec > >(tee -a "$INSTALL_LOG") 2>&1

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

is_pid_alive() {
    local pid_file="$1"
    [[ -f "$pid_file" ]] || return 1

    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    [[ "$pid" =~ ^[0-9]+$ ]] || return 1

    kill -0 "$pid" 2>/dev/null
}

stop_pid_file() {
    local pid_file="$1"

    if ! is_pid_alive "$pid_file"; then
        rm -f "$pid_file"
        return 0
    fi

    local pid
    pid="$(cat "$pid_file")"

    kill "$pid" 2>/dev/null || true

    for _ in {1..20}; do
        if ! kill -0 "$pid" 2>/dev/null; then
            break
        fi
        sleep 0.25
    done

    if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
    fi

    rm -f "$pid_file"
}

download_file() {
    local label="$1"
    local url="$2"
    local dest="$3"

    if [[ -s "$dest" ]]; then
        ok "$label bereits vorhanden: $dest"
        return 0
    fi

    info "Lade $label ..."

    local tmp="${dest}.part"
    rm -f "$tmp"

    if command_exists curl; then
        curl \
            --fail \
            --location \
            --retry 5 \
            --retry-delay 2 \
            --connect-timeout 20 \
            --continue-at - \
            --output "$tmp" \
            "$url"
    else
        wget \
            --tries=5 \
            --timeout=30 \
            --continue \
            --output-document="$tmp" \
            "$url"
    fi

    [[ -s "$tmp" ]] || die "Download von $label ist leer."

    mv -f "$tmp" "$dest"
    ok "$label heruntergeladen."
}

wait_for_http() {
    local url="$1"
    local timeout="${2:-180}"
    local start
    start="$(date +%s)"

    while true; do
        if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
            return 0
        fi

        if (( $(date +%s) - start >= timeout )); then
            return 1
        fi

        if ! is_pid_alive "$APP_PID_FILE"; then
            return 1
        fi

        sleep 1
    done
}

wait_for_port() {
    local host="$1"
    local port="$2"
    local timeout="${3:-180}"
    local start
    start="$(date +%s)"

    while true; do
        if python3 - "$host" "$port" <<'PY' >/dev/null 2>&1
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

with socket.create_connection((host, port), timeout=1.5):
    pass
PY
        then
            return 0
        fi

        if (( $(date +%s) - start >= timeout )); then
            return 1
        fi

        if ! is_pid_alive "$APP_PID_FILE"; then
            return 1
        fi

        sleep 1
    done
}

# ------------------------------------------------------------------------------
# 1. Betriebssystem prüfen + Pakete
# ------------------------------------------------------------------------------

if [[ ! -r /etc/os-release ]]; then
    die "Dieses Skript erwartet Ubuntu/Debian mit /etc/os-release."
fi

# shellcheck disable=SC1091
source /etc/os-release

if [[ "${ID:-}" != "ubuntu" && "${ID_LIKE:-}" != *"debian"* ]]; then
    warn "System ist '${PRETTY_NAME:-unbekannt}'. Getestet/gedacht für Ubuntu/Debian."
fi

info "Installiere System-Abhängigkeiten ..."

"${SUDO[@]}" apt-get update -y

"${SUDO[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates \
    curl \
    wget \
    git \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    pciutils \
    jq

ok "System-Abhängigkeiten installiert."

# ------------------------------------------------------------------------------
# 2. Hardware erkennen
# ------------------------------------------------------------------------------

HAS_NVIDIA=0
HAS_WORKING_NVIDIA=0
HAS_NVCC=0

if [[ "$FORCE_CPU" != "1" ]]; then
    if lspci 2>/dev/null | grep -qiE 'NVIDIA.*(VGA|3D|Display)|VGA.*NVIDIA|3D.*NVIDIA'; then
        HAS_NVIDIA=1
    fi

    if command_exists nvidia-smi && nvidia-smi >/dev/null 2>&1; then
        HAS_WORKING_NVIDIA=1
    fi

    if command_exists nvcc; then
        HAS_NVCC=1
    fi
fi

if [[ "$FORCE_CPU" == "1" ]]; then
    warn "FORCE_CPU=1 -> CPU-Modus erzwungen."
elif [[ "$HAS_WORKING_NVIDIA" == "1" ]]; then
    ok "NVIDIA/CUDA-fähige GPU erkannt:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true
else
    if [[ "$HAS_NVIDIA" == "1" ]]; then
        warn "NVIDIA-Hardware erkannt, aber nvidia-smi funktioniert nicht."
        warn "Installer verwendet vorerst CPU. Installiere/aktiviere den NVIDIA-Treiber und starte dieses Skript danach erneut."
    else
        info "Keine nutzbare NVIDIA-GPU erkannt -> CPU-Modus."
    fi
fi

# ------------------------------------------------------------------------------
# 3. GitHub Repository
# ------------------------------------------------------------------------------

info "Synchronisiere SCP-1356AI von GitHub ..."

if [[ -d "$INSTALL_DIR/.git" ]]; then
    git -C "$INSTALL_DIR" remote set-url origin "$REPO_URL"
    git -C "$INSTALL_DIR" fetch --depth=1 origin "$REPO_BRANCH"

    # Lokale Konfig/Modelle bleiben erhalten; tracked Repo-Code wird aktualisiert.
    git -C "$INSTALL_DIR" reset --hard "origin/$REPO_BRANCH"
    ok "Repository aktualisiert."
else
    # INSTALL_DIR kann bereits durch logs/run angelegt worden sein.
    tmp_clone="${INSTALL_DIR}.clone.$$"
    rm -rf "$tmp_clone"

    git clone \
        --depth 1 \
        --branch "$REPO_BRANCH" \
        "$REPO_URL" \
        "$tmp_clone"

    # Repo-Inhalt in bestehendes Installationsverzeichnis übernehmen.
    cp -a "$tmp_clone"/. "$INSTALL_DIR"/
    rm -rf "$tmp_clone"

    ok "Repository geklont."
fi

mkdir -p "$MODELS_DIR" "$LOG_DIR" "$RUN_DIR"

[[ -f "$INSTALL_DIR/app.py" ]] || die "app.py wurde im Repository nicht gefunden: $INSTALL_DIR/app.py"

# ------------------------------------------------------------------------------
# 4. Python Virtual Environment
# ------------------------------------------------------------------------------

if [[ "$FORCE_REINSTALL" == "1" && -d "$VENV_DIR" ]]; then
    info "FORCE_REINSTALL=1 -> entferne bestehende venv."
    rm -rf "$VENV_DIR"
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    info "Erstelle Python venv: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel packaging

PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
info "Python: $PYTHON_VERSION"

# ------------------------------------------------------------------------------
# 5. Requirements hardwaregerecht installieren
# ------------------------------------------------------------------------------

REQ_SOURCE="$INSTALL_DIR/requirements.txt"
REQ_FILTERED="$RUN_DIR/requirements.filtered.txt"

if [[ -f "$REQ_SOURCE" ]]; then
    info "Bereite hardwaregerechte requirements.txt vor ..."

    python - "$REQ_SOURCE" "$REQ_FILTERED" "$HAS_WORKING_NVIDIA" <<'PY'
from pathlib import Path
import sys
import re

source = Path(sys.argv[1])
dest = Path(sys.argv[2])
gpu = sys.argv[3] == "1"

skip_prefixes = {
    "llama-cpp-python",
}

# GPU-only Pakete auf CPU-Systemen nicht erzwingen.
if not gpu:
    skip_prefixes.update({
        "onnxruntime-gpu",
        "nvidia-cudnn-cu12",
        "nvidia-cublas-cu12",
        "nvidia-cuda-runtime-cu12",
    })

lines = []
for raw in source.read_text(encoding="utf-8").splitlines():
    stripped = raw.strip()

    if not stripped or stripped.startswith("#"):
        lines.append(raw)
        continue

    name = re.split(r"[<>=!~;\[\s]", stripped, maxsplit=1)[0].lower()
    if name in skip_prefixes:
        lines.append(f"# [installer-managed] {raw}")
        continue

    lines.append(raw)

dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

    python -m pip install --prefer-binary -r "$REQ_FILTERED"
else
    warn "requirements.txt fehlt. Installiere Mindest-Abhängigkeiten direkt."

    python -m pip install --prefer-binary \
        "Flask>=3,<4" \
        "Werkzeug>=3,<4" \
        "gunicorn>=22" \
        "numpy>=1.26,<3" \
        "scipy>=1.13,<2" \
        "faster-whisper>=1.0" \
        "ctranslate2>=4.6" \
        "av>=12" \
        "huggingface_hub>=0.24" \
        "tokenizers>=0.19" \
        "cryptography>=42" \
        "piper-tts>=1.2" \
        "onnx>=1.16" \
        "requests>=2.32" \
        "soundfile>=0.12" \
        "pydub>=0.25" \
        "python-dotenv>=1" \
        "psutil>=6"
fi

# CPU braucht onnxruntime, falls das Projekt ONNX direkt nutzt.
if [[ "$HAS_WORKING_NVIDIA" != "1" ]]; then
    python -m pip install --prefer-binary "onnxruntime>=1.18"
fi

# NVIDIA CUDA Runtime Libraries für faster-whisper / CTranslate2.
if [[ "$HAS_WORKING_NVIDIA" == "1" ]]; then
    info "Installiere CUDA-Laufzeitbibliotheken für Python/Whisper ..."
    python -m pip install --prefer-binary \
        "nvidia-cublas-cu12>=12" \
        "nvidia-cudnn-cu12>=9"

    # onnxruntime-gpu ist optional für Teile des Projekts.
    python -m pip install --prefer-binary "onnxruntime-gpu>=1.18" || \
        warn "onnxruntime-gpu konnte nicht installiert werden; Kern-AI kann trotzdem weiter funktionieren."
fi

# ------------------------------------------------------------------------------
# 6. llama-cpp-python: CUDA schnell versuchen, sonst CPU fallback
# ------------------------------------------------------------------------------

install_llama_cpu() {
    info "Installiere llama-cpp-python $LLAMA_CPP_VERSION im CPU-Modus ..."
    CMAKE_ARGS="-DGGML_CUDA=off" \
    FORCE_CMAKE=1 \
        python -m pip install \
            --upgrade \
            --force-reinstall \
            --no-cache-dir \
            "llama-cpp-python==$LLAMA_CPP_VERSION"
}

install_llama_cuda() {
    local installed=0

    # Schneller Weg: CUDA-Wheels probieren. cu124 ist mit aktuellen NVIDIA-
    # Treibern meist der kompatibelste veröffentlichte Wheel-Kanal.
    if [[ "$PYTHON_VERSION" =~ ^3\.(10|11|12)$ ]]; then
        info "Versuche vorkompiliertes CUDA-Wheel für llama-cpp-python ..."

        if python -m pip install \
            --upgrade \
            --force-reinstall \
            --no-cache-dir \
            "llama-cpp-python==$LLAMA_CPP_VERSION" \
            --extra-index-url "https://abetlen.github.io/llama-cpp-python/whl/cu124"
        then
            installed=1
        fi
    fi

    if [[ "$installed" == "1" ]]; then
        ok "llama-cpp-python CUDA-Wheel installiert."
        return 0
    fi

    if [[ "$HAS_NVCC" == "1" ]]; then
        info "CUDA-Wheel nicht verfügbar -> baue llama-cpp-python mit nvcc ..."

        if CMAKE_ARGS="-DGGML_CUDA=on" \
           FORCE_CMAKE=1 \
           CMAKE_BUILD_PARALLEL_LEVEL="$(nproc)" \
           python -m pip install \
               --upgrade \
               --force-reinstall \
               --no-cache-dir \
               "llama-cpp-python==$LLAMA_CPP_VERSION"
        then
            ok "llama-cpp-python mit CUDA gebaut."
            return 0
        fi
    else
        warn "nvcc nicht vorhanden; CUDA-Source-Build wird übersprungen."
    fi

    warn "CUDA-Installation von llama-cpp-python fehlgeschlagen -> sicherer CPU-Fallback."
    install_llama_cpu
}

if [[ "$HAS_WORKING_NVIDIA" == "1" ]]; then
    install_llama_cuda
else
    install_llama_cpu
fi

# ------------------------------------------------------------------------------
# 7. Modelle
# ------------------------------------------------------------------------------

mkdir -p "$MODELS_DIR"

download_file \
    "Qwen2.5-7B-Instruct Q4_K_M (~4-5 GB)" \
    "$LLM_MODEL_URL" \
    "$MODELS_DIR/$LLM_MODEL_NAME"

download_file \
    "Piper de_DE Thorsten High" \
    "$PIPER_MODEL_URL" \
    "$MODELS_DIR/$PIPER_MODEL_NAME"

# Piper config: erst primäre, dann bekannte offizielle URL.
if [[ ! -s "$MODELS_DIR/$PIPER_MODEL_NAME.json" ]]; then
    info "Lade Piper-Konfiguration ..."

    if ! curl \
        --fail \
        --location \
        --retry 3 \
        --connect-timeout 20 \
        --output "$MODELS_DIR/$PIPER_MODEL_NAME.json.part" \
        "$PIPER_CONFIG_URL"
    then
        rm -f "$MODELS_DIR/$PIPER_MODEL_NAME.json.part"

        curl \
            --fail \
            --location \
            --retry 5 \
            --retry-delay 2 \
            --connect-timeout 20 \
            --output "$MODELS_DIR/$PIPER_MODEL_NAME.json.part" \
            "$PIPER_CONFIG_URL_FALLBACK"
    fi

    mv -f \
        "$MODELS_DIR/$PIPER_MODEL_NAME.json.part" \
        "$MODELS_DIR/$PIPER_MODEL_NAME.json"

    ok "Piper-Konfiguration heruntergeladen."
fi

# ------------------------------------------------------------------------------
# 8. Transport-Key
# ------------------------------------------------------------------------------

TRANSPORT_KEY_FILE="${SCP1356_TRANSPORT_KEY_FILE:-$INSTALL_DIR/transport.key}"

if [[ ! -s "$TRANSPORT_KEY_FILE" ]]; then
    info "Erzeuge sicheren 32-Byte Transport-Key ..."

    umask 077
    python - "$TRANSPORT_KEY_FILE" <<'PY'
from pathlib import Path
import base64
import os

path = Path(os.sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(base64.b64encode(os.urandom(32)).decode("ascii") + "\n", encoding="utf-8")
try:
    path.chmod(0o600)
except OSError:
    pass
PY

    ok "Transport-Key erzeugt: $TRANSPORT_KEY_FILE"
else
    ok "Transport-Key vorhanden: $TRANSPORT_KEY_FILE"
fi

# ------------------------------------------------------------------------------
# 9. Runtime Environment
# ------------------------------------------------------------------------------

RUNTIME_ENV="$INSTALL_DIR/.runtime.env"

cat > "$RUNTIME_ENV" <<EOF
# Automatisch von start.sh erzeugt.
SCP1356_TRANSPORT_KEY_FILE=$TRANSPORT_KEY_FILE
DEVICE=$([[ "$HAS_WORKING_NVIDIA" == "1" ]] && echo "cuda" || echo "cpu")
STT_DEVICE=$([[ "$HAS_WORKING_NVIDIA" == "1" ]] && echo "cuda" || echo "cpu")
EOF

chmod 600 "$RUNTIME_ENV"

export SCP1356_TRANSPORT_KEY_FILE="$TRANSPORT_KEY_FILE"

if [[ "$HAS_WORKING_NVIDIA" == "1" ]]; then
    export DEVICE="cuda"
    export STT_DEVICE="cuda"

    # NVIDIA pip wheels legen native Libraries in site-packages/nvidia/*/lib ab.
    NVIDIA_LIBRARY_PATHS="$(
        python - <<'PY'
from pathlib import Path
import site

paths = []
for root in site.getsitepackages():
    nvidia = Path(root) / "nvidia"
    if not nvidia.is_dir():
        continue
    for lib in nvidia.glob("*/lib"):
        if lib.is_dir():
            paths.append(str(lib))

print(":".join(paths))
PY
    )"

    if [[ -n "$NVIDIA_LIBRARY_PATHS" ]]; then
        export LD_LIBRARY_PATH="$NVIDIA_LIBRARY_PATHS:${LD_LIBRARY_PATH:-}"
    fi
else
    export DEVICE="cpu"
    export STT_DEVICE="cpu"
    export STT_COMPUTE_TYPE="${STT_COMPUTE_TYPE:-int8}"
    export LLM_GPU_LAYERS="0"
    export LLM_FLASH_ATTN="0"
    export LLM_OFFLOAD_KQV="0"
fi

# ------------------------------------------------------------------------------
# 10. cloudflared installieren
# ------------------------------------------------------------------------------

install_cloudflared() {
    if command_exists cloudflared; then
        ok "cloudflared bereits installiert."
        return 0
    fi

    info "Installiere cloudflared ..."

    local arch
    case "$(uname -m)" in
        x86_64|amd64)
            arch="amd64"
            ;;
        aarch64|arm64)
            arch="arm64"
            ;;
        *)
            die "Nicht unterstützte Architektur für cloudflared: $(uname -m)"
            ;;
    esac

    local tmp="/tmp/cloudflared-${arch}.deb"

    curl \
        --fail \
        --location \
        --retry 5 \
        --retry-delay 2 \
        --output "$tmp" \
        "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${arch}.deb"

    "${SUDO[@]}" dpkg -i "$tmp" || "${SUDO[@]}" apt-get -f install -y
    rm -f "$tmp"

    command_exists cloudflared || die "cloudflared wurde nicht korrekt installiert."
    ok "cloudflared installiert."
}

install_cloudflared

# ------------------------------------------------------------------------------
# 11. Alte Prozesse sauber stoppen
# ------------------------------------------------------------------------------

info "Stoppe alte SCP-1356-AI/Quick-Tunnel Prozesse dieses Installers ..."

stop_pid_file "$CF_PID_FILE"
stop_pid_file "$APP_PID_FILE"

# ------------------------------------------------------------------------------
# 12. AI starten
# ------------------------------------------------------------------------------

cd "$INSTALL_DIR"

: > "$APP_LOG"

info "Starte SCP-1356 AI ..."

APP_ENV=(
    "SCP1356_TRANSPORT_KEY_FILE=$SCP1356_TRANSPORT_KEY_FILE"
    "DEVICE=$DEVICE"
    "STT_DEVICE=$STT_DEVICE"
    "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}"
)

if [[ "$DEVICE" == "cpu" ]]; then
    APP_ENV+=(
        "STT_COMPUTE_TYPE=${STT_COMPUTE_TYPE:-int8}"
        "LLM_GPU_LAYERS=0"
        "LLM_FLASH_ATTN=0"
        "LLM_OFFLOAD_KQV=0"
    )
fi

nohup env "${APP_ENV[@]}" \
    "$VENV_DIR/bin/python" "$INSTALL_DIR/app.py" \
    >>"$APP_LOG" 2>&1 &

APP_PID=$!
echo "$APP_PID" > "$APP_PID_FILE"

ok "AI-Prozess gestartet (PID $APP_PID)."

# Flask kann je nach Modellgröße lange zum Laden brauchen.
info "Warte, bis Port $APP_PORT erreichbar ist ..."

if ! wait_for_port "$APP_HOST" "$APP_PORT" 900; then
    warn "AI-Port wurde nicht rechtzeitig erreichbar."
    warn "Letzte 80 Zeilen aus $APP_LOG:"
    tail -n 80 "$APP_LOG" || true
    die "SCP-1356 AI konnte nicht gestartet werden."
fi

ok "SCP-1356 AI ist lokal erreichbar: http://$APP_HOST:$APP_PORT"

# ------------------------------------------------------------------------------
# 13. Cloudflare Quick Tunnel ohne Login
# ------------------------------------------------------------------------------

: > "$CF_LOG"

info "Starte Cloudflare Quick Tunnel (kein Login erforderlich) ..."

nohup cloudflared tunnel \
    --no-autoupdate \
    --url "http://$APP_HOST:$APP_PORT" \
    >"$CF_LOG" 2>&1 &

CF_PID=$!
echo "$CF_PID" > "$CF_PID_FILE"

PUBLIC_URL=""

for _ in {1..120}; do
    if ! kill -0 "$CF_PID" 2>/dev/null; then
        warn "cloudflared wurde unerwartet beendet."
        tail -n 80 "$CF_LOG" || true
        die "Cloudflare Quick Tunnel konnte nicht gestartet werden."
    fi

    PUBLIC_URL="$(
        grep -Eo 'https://[A-Za-z0-9-]+\.trycloudflare\.com' "$CF_LOG" \
            | tail -n 1 \
            || true
    )"

    if [[ -n "$PUBLIC_URL" ]]; then
        break
    fi

    sleep 0.5
done

if [[ -z "$PUBLIC_URL" ]]; then
    warn "Keine Quick-Tunnel-URL im Log gefunden."
    tail -n 80 "$CF_LOG" || true
    die "Cloudflare Quick Tunnel hat keine URL geliefert."
fi

# ------------------------------------------------------------------------------
# 14. Persistentes lokales Startskript für spätere Starts erzeugen
# ------------------------------------------------------------------------------

cat > "$INSTALL_DIR/run_local.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
cd "$INSTALL_DIR"
source "$VENV_DIR/bin/activate"
export SCP1356_TRANSPORT_KEY_FILE="$TRANSPORT_KEY_FILE"
export DEVICE="$DEVICE"
export STT_DEVICE="$STT_DEVICE"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}"
exec python app.py
EOF

chmod +x "$INSTALL_DIR/run_local.sh"

# ------------------------------------------------------------------------------
# 15. Zusammenfassung
# ------------------------------------------------------------------------------

echo
echo "============================================================================="
ok "SCP-1356 AI INSTALLATION + START ABGESCHLOSSEN"
echo "============================================================================="
echo "Installationsordner : $INSTALL_DIR"
echo "Python venv          : $VENV_DIR"
echo "Modelle              : $MODELS_DIR"
echo "AI Log               : $APP_LOG"
echo "Cloudflare Log       : $CF_LOG"
echo "Transport-Key        : $TRANSPORT_KEY_FILE"
echo "Hardware-Modus       : $([[ "$HAS_WORKING_NVIDIA" == "1" ]] && echo "NVIDIA/CUDA" || echo "CPU")"
echo "Lokale URL           : http://$APP_HOST:$APP_PORT"
echo
echo "Stoppen:"
echo "  kill \$(cat '$APP_PID_FILE')"
echo "  kill \$(cat '$CF_PID_FILE')"
echo
echo "HINWEIS: Der trycloudflare.com Quick Tunnel ist eine Demo-/Test-URL und"
echo "ändert sich beim nächsten Tunnel-Start."
echo "============================================================================="

# WICHTIG: Diese URL ist absichtlich die LETZTE Ausgabe des Installers.
printf '%s\n' "$PUBLIC_URL"
