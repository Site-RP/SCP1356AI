#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# SCP1356AI – Schnellinstaller für Vast.ai / Ubuntu 22.04 + RTX 3090
#
# Empfohlenes Vast.ai-Image:
#   nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
#
# Nutzung:
#   chmod +x install_scp1356ai.sh
#   ./install_scp1356ai.sh
#
# Optional:
#   INSTALL_DIR=/workspace/SCP1356AI ./install_scp1356ai.sh
# ═══════════════════════════════════════════════════════════════════════════

set -Eeuo pipefail

# ── Konfiguration ────────────────────────────────────────────────────────────

REPO_RAW_BASE="https://raw.githubusercontent.com/Site-RP/SCP1356AI/main"

INSTALL_DIR="${INSTALL_DIR:-$HOME/SCP1356AI}"
VENV_DIR="$INSTALL_DIR/venv"
MODELS_DIR="$INSTALL_DIR/models"
PYTHON_BIN="${PYTHON_BIN:-python3}"

LLM_MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
LLM_MODEL_FILE="$MODELS_DIR/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

TTS_MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx"
TTS_MODEL_FILE="$MODELS_DIR/de_DE-thorsten-high.onnx"

TTS_CONFIG_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json"
TTS_CONFIG_FILE="$MODELS_DIR/de_DE-thorsten-high.onnx.json"

# Vorgefertigtes CUDA-12.4-Wheel.
LLAMA_CUDA_WHEEL_INDEX="https://abetlen.github.io/llama-cpp-python/whl/cu124"

# ── Ausgabe ──────────────────────────────────────────────────────────────────

c_info() {
    echo -e "\e[1;34m[INFO]\e[0m  $*"
}

c_ok() {
    echo -e "\e[1;32m[OK]\e[0m    $*"
}

c_warn() {
    echo -e "\e[1;33m[WARN]\e[0m  $*"
}

c_err() {
    echo -e "\e[1;31m[FEHLER]\e[0m $*" >&2
}

trap 'c_err "Installation abgebrochen – Zeile $LINENO."' ERR

if [[ "$(id -u)" -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 1. Betriebssystem prüfen
# ═══════════════════════════════════════════════════════════════════════════

if [[ ! -f /etc/os-release ]]; then
    c_err "/etc/os-release wurde nicht gefunden."
    exit 1
fi

# shellcheck disable=SC1091
source /etc/os-release

c_info "Betriebssystem: ${PRETTY_NAME:-unbekannt}"

if [[ "${ID:-}" != "ubuntu" ]]; then
    c_warn "Dieser Installer wurde für Ubuntu geschrieben."
fi

# ═══════════════════════════════════════════════════════════════════════════
# 2. Systempakete
# ═══════════════════════════════════════════════════════════════════════════

c_info "Installiere System-Abhängigkeiten ..."

$SUDO apt-get update

$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    wget \
    curl \
    ca-certificates \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    pkg-config \
    pciutils

c_ok "System-Abhängigkeiten installiert."

# ═══════════════════════════════════════════════════════════════════════════
# 3. NVIDIA-GPU prüfen
# ═══════════════════════════════════════════════════════════════════════════

if ! command -v nvidia-smi &>/dev/null; then
    c_err "nvidia-smi wurde nicht gefunden."
    c_err "Starte auf Vast.ai eine NVIDIA-/CUDA-Instanz."
    exit 1
fi

if ! nvidia-smi &>/dev/null; then
    c_err "Die NVIDIA-GPU ist nicht erreichbar."
    c_err "Prüfe den Vast.ai-Container beziehungsweise die GPU-Zuweisung."
    exit 1
fi

GPU_NAME="$(
    nvidia-smi \
        --query-gpu=name \
        --format=csv,noheader \
        | head -n1 \
        | xargs
)"

GPU_VRAM="$(
    nvidia-smi \
        --query-gpu=memory.total \
        --format=csv,noheader \
        | head -n1 \
        | xargs
)"

DRIVER_VERSION="$(
    nvidia-smi \
        --query-gpu=driver_version \
        --format=csv,noheader \
        | head -n1 \
        | xargs
)"

c_ok "NVIDIA-GPU erkannt:"
echo "  GPU:     $GPU_NAME"
echo "  VRAM:    $GPU_VRAM"
echo "  Treiber: $DRIVER_VERSION"

if [[ "$GPU_NAME" != *"3090"* ]]; then
    c_warn "Erwartet wurde eine RTX 3090, erkannt wurde: $GPU_NAME"
    c_warn "Der Installer versucht trotzdem fortzufahren."
fi

# ═══════════════════════════════════════════════════════════════════════════
# 4. Projektdateien
# ═══════════════════════════════════════════════════════════════════════════

c_info "Erstelle Projektverzeichnis: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR"
mkdir -p "$MODELS_DIR"

c_info "Lade app.py und requirements.txt aus dem Repository ..."

curl \
    --fail \
    --location \
    --retry 3 \
    --output "$INSTALL_DIR/app.py" \
    "$REPO_RAW_BASE/app.py"

curl \
    --fail \
    --location \
    --retry 3 \
    --output "$INSTALL_DIR/requirements.txt" \
    "$REPO_RAW_BASE/requirements.txt"

if [[ ! -s "$INSTALL_DIR/app.py" ]]; then
    c_err "app.py ist leer oder wurde nicht richtig heruntergeladen."
    exit 1
fi

if [[ ! -s "$INSTALL_DIR/requirements.txt" ]]; then
    c_err "requirements.txt ist leer oder wurde nicht richtig heruntergeladen."
    exit 1
fi

c_ok "Projektdateien heruntergeladen."

# ═══════════════════════════════════════════════════════════════════════════
# 5. Python-Virtualenv
# ═══════════════════════════════════════════════════════════════════════════

if [[ -d "$VENV_DIR" ]]; then
    c_warn "Bestehende Python-Umgebung wird entfernt."
    rm -rf "$VENV_DIR"
fi

c_info "Erstelle Python-Virtualenv ..."

"$PYTHON_BIN" -m venv "$VENV_DIR"

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install \
    --upgrade \
    pip \
    setuptools \
    wheel

c_ok "Python-Virtualenv erstellt."

# ═══════════════════════════════════════════════════════════════════════════
# 6. Requirements installieren
# ═══════════════════════════════════════════════════════════════════════════

c_info "Installiere Projekt-Requirements ..."

# llama-cpp-python wird separat mit CUDA installiert.
# Deshalb wird es beim ersten Requirements-Durchlauf ausgelassen.
grep -viE '^[[:space:]]*llama[-_]cpp[-_]python([<>=!~].*)?[[:space:]]*$' \
    "$INSTALL_DIR/requirements.txt" \
    > "$INSTALL_DIR/requirements.without-llama.txt" || true

if [[ -s "$INSTALL_DIR/requirements.without-llama.txt" ]]; then
    python -m pip install \
        --no-cache-dir \
        -r "$INSTALL_DIR/requirements.without-llama.txt"
fi

c_ok "Allgemeine Requirements installiert."

# ═══════════════════════════════════════════════════════════════════════════
# 7. llama-cpp-python mit CUDA
# ═══════════════════════════════════════════════════════════════════════════

c_info "Installiere llama-cpp-python mit CUDA-12.4-Unterstützung ..."

python -m pip uninstall -y llama-cpp-python 2>/dev/null || true

if python -m pip install \
    --upgrade \
    --force-reinstall \
    --no-cache-dir \
    llama-cpp-python \
    --extra-index-url "$LLAMA_CUDA_WHEEL_INDEX"
then
    c_ok "CUDA-Wheel für llama-cpp-python installiert."
else
    c_warn "CUDA-Wheel konnte nicht installiert werden."

    if command -v nvcc &>/dev/null; then
        c_info "Versuche lokalen CUDA-Build mit nvcc ..."

        CMAKE_ARGS="-DGGML_CUDA=on" \
        FORCE_CMAKE=1 \
        CMAKE_BUILD_PARALLEL_LEVEL="$(nproc)" \
        python -m pip install \
            --upgrade \
            --force-reinstall \
            --no-cache-dir \
            llama-cpp-python

        c_ok "llama-cpp-python lokal mit CUDA gebaut."
    else
        c_err "Kein CUDA-Wheel verfügbar und nvcc wurde nicht gefunden."
        c_err "Nutze auf Vast.ai ein CUDA-12.4-Image."
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# 8. llama-cpp-python testen
# ═══════════════════════════════════════════════════════════════════════════

c_info "Teste llama-cpp-python ..."

python - <<'PY'
import llama_cpp

print("llama-cpp-python Version:", llama_cpp.__version__)
print("Bibliothek erfolgreich importiert.")
PY

c_ok "llama-cpp-python funktioniert."

# ═══════════════════════════════════════════════════════════════════════════
# 9. Modelle herunterladen
# ═══════════════════════════════════════════════════════════════════════════

download_if_missing() {
    local label="$1"
    local url="$2"
    local destination="$3"

    if [[ -s "$destination" ]]; then
        c_ok "$label bereits vorhanden:"
        echo "  $destination"
        return
    fi

    c_info "Lade $label ..."

    wget \
        --continue \
        --tries=5 \
        --timeout=30 \
        --output-document="$destination" \
        "$url"

    if [[ ! -s "$destination" ]]; then
        c_err "$label wurde nicht richtig heruntergeladen."
        rm -f "$destination"
        exit 1
    fi

    c_ok "$label heruntergeladen."
}

download_if_missing \
    "Qwen2.5-7B-Instruct Q4_K_M" \
    "$LLM_MODEL_URL" \
    "$LLM_MODEL_FILE"

download_if_missing \
    "Piper Thorsten High" \
    "$TTS_MODEL_URL" \
    "$TTS_MODEL_FILE"

download_if_missing \
    "Piper-Konfiguration" \
    "$TTS_CONFIG_URL" \
    "$TTS_CONFIG_FILE"

# ═══════════════════════════════════════════════════════════════════════════
# 10. Transport-Schlüssel
# ═══════════════════════════════════════════════════════════════════════════

KEY_FILE="$INSTALL_DIR/transport.key"

if [[ -s "$KEY_FILE" ]]; then
    c_ok "Transport-Schlüssel bereits vorhanden."
else
    c_info "Erzeuge neuen 256-Bit-Transport-Schlüssel ..."

    python - <<PY
import base64
import os
from pathlib import Path

path = Path("$KEY_FILE")
path.write_text(base64.b64encode(os.urandom(32)).decode("ascii") + "\n")
path.chmod(0o600)

print(f"Transport-Schlüssel erstellt: {path}")
PY
fi

# ═══════════════════════════════════════════════════════════════════════════
# 11. Startskript
# ═══════════════════════════════════════════════════════════════════════════

cat > "$INSTALL_DIR/start.sh" <<EOF
#!/usr/bin/env bash

set -Eeuo pipefail

cd "$INSTALL_DIR"

source "$VENV_DIR/bin/activate"

export SCP1356_TRANSPORT_KEY_FILE="$KEY_FILE"
export CUDA_VISIBLE_DEVICES="\${CUDA_VISIBLE_DEVICES:-0}"
export PYTHONUNBUFFERED=1

exec python app.py
EOF

chmod +x "$INSTALL_DIR/start.sh"

# ═══════════════════════════════════════════════════════════════════════════
# 12. GPU-Funktionstest mit Modell
# ═══════════════════════════════════════════════════════════════════════════

c_info "Teste das GGUF-Modell mit GPU-Offloading ..."

python - <<PY
from llama_cpp import Llama

model_path = r"$LLM_MODEL_FILE"

llm = Llama(
    model_path=model_path,
    n_ctx=512,
    n_batch=128,
    n_gpu_layers=-1,
    verbose=True,
)

result = llm(
    "Antworte nur mit dem Wort: bereit",
    max_tokens=8,
    temperature=0.0,
)

print()
print("Modellantwort:", result["choices"][0]["text"].strip())
print("GPU-Modelltest abgeschlossen.")
PY

c_ok "Modell konnte geladen werden."

# ═══════════════════════════════════════════════════════════════════════════
# 13. Abschluss
# ═══════════════════════════════════════════════════════════════════════════

deactivate

echo
echo "════════════════════════════════════════════════════════════════"
c_ok "SCP1356AI wurde installiert."
echo
echo "  GPU:          $GPU_NAME"
echo "  Installation: $INSTALL_DIR"
echo "  Virtualenv:   $VENV_DIR"
echo "  Modelle:      $MODELS_DIR"
echo "  Schlüssel:    $KEY_FILE"
echo
echo "  Starten:"
echo "    $INSTALL_DIR/start.sh"
echo
echo "  Schlüssel anzeigen:"
echo "    cat $KEY_FILE"
echo
echo "  Diesen Schlüssel auch auf dem SCP:SL-Server speichern unter:"
echo "    ~/.config/EXILED/Configs/SCP1356/key.txt"
echo
echo "  beziehungsweise dem Pfad aus Paths.Exiled/SCP1356/key.txt."
echo "════════════════════════════════════════════════════════════════"
