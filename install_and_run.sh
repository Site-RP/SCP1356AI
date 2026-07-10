#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# SCP1356AI – Installer für frische Ubuntu 22.04 VMs
#
# - Erkennt automatisch, ob eine NVIDIA-GPU vorhanden ist
# - Installiert System-Pakete, Python-venv, Requirements von GitHub
# - Lädt app.py vom Repo
# - Baut llama-cpp-python passend (CUDA oder CPU)
# - Lädt die Modelle (LLM + Piper-Stimme) in models/
#
# Nutzung:
#   chmod +x install_scp1356ai.sh
#   ./install_scp1356ai.sh
#
# Optional per ENV-Variable überschreibbar:
#   INSTALL_DIR=/opt/SCP1356AI ./install_scp1356ai.sh
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Konfiguration ────────────────────────────────────────────────────────────
REPO_RAW_BASE="https://raw.githubusercontent.com/Site-RP/SCP1356AI/main"
INSTALL_DIR="${INSTALL_DIR:-$HOME/SCP1356AI}"
VENV_DIR="$INSTALL_DIR/venv"
MODELS_DIR="$INSTALL_DIR/models"
PYTHON_BIN="python3"

LLM_MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
LLM_MODEL_FILE="$MODELS_DIR/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

TTS_MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx"
TTS_MODEL_FILE="$MODELS_DIR/de_DE-thorsten-high.onnx"

TTS_CONFIG_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json"
TTS_CONFIG_FILE="$MODELS_DIR/de_DE-thorsten-high.onnx.json"

# ── Farb-Helfer ───────────────────────────────────────────────────────────────
c_info()  { echo -e "\e[1;34m[INFO]\e[0m  $*"; }
c_ok()    { echo -e "\e[1;32m[OK]\e[0m    $*"; }
c_warn()  { echo -e "\e[1;33m[WARN]\e[0m  $*"; }
c_err()   { echo -e "\e[1;31m[FEHLER]\e[0m $*" >&2; }

trap 'c_err "Installation abgebrochen (Zeile $LINENO). Siehe Ausgabe oben."' ERR

if [[ "$(id -u)" -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 1) System-Pakete
# ═══════════════════════════════════════════════════════════════════════════
c_info "Aktualisiere Paketlisten und installiere System-Abhängigkeiten..."
$SUDO apt-get update -y
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential cmake git wget curl ca-certificates \
    python3 python3-venv python3-pip python3-dev \
    ffmpeg libsndfile1 pkg-config \
    software-properties-common

c_ok "System-Pakete installiert."

# ═══════════════════════════════════════════════════════════════════════════
# 2) GPU-Erkennung
# ═══════════════════════════════════════════════════════════════════════════
HAS_GPU=false
if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
    HAS_GPU=true
    c_ok "NVIDIA-GPU erkannt:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
    c_warn "nvidia-smi nicht gefunden oder keine GPU aktiv."
    # Prüfen, ob überhaupt NVIDIA-Hardware im PCI-Bus steckt, aber der Treiber fehlt
    if command -v lspci &>/dev/null && lspci | grep -qi nvidia; then
        c_warn "NVIDIA-Hardware im System erkannt, aber kein funktionierender Treiber."
        read -rp "Soll der NVIDIA-Treiber jetzt automatisch installiert werden? [y/N] " ANSWER
        if [[ "${ANSWER,,}" == "y" ]]; then
            c_info "Installiere NVIDIA-Treiber via ubuntu-drivers..."
            $SUDO apt-get install -y ubuntu-drivers-common
            $SUDO ubuntu-drivers autoinstall
            c_warn "Treiber installiert. Ein REBOOT ist erforderlich, bevor die GPU nutzbar ist."
            c_warn "Bitte nach dem Neustart dieses Skript erneut ausführen."
            exit 0
        else
            c_warn "Fahre ohne GPU-Treiber fort -> Installation läuft im CPU-Modus."
        fi
    else
        c_info "Keine NVIDIA-Hardware gefunden -> Installation läuft im CPU-Modus."
    fi
fi

# Falls GPU vorhanden: CUDA-Toolkit (nvcc) sicherstellen, wird für den
# GPU-Build von llama-cpp-python benötigt.
if [[ "$HAS_GPU" == true ]]; then
    if ! command -v nvcc &>/dev/null; then
        c_info "nvcc nicht gefunden, installiere nvidia-cuda-toolkit..."
        $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y nvidia-cuda-toolkit
    else
        c_ok "CUDA-Toolkit (nvcc) bereits vorhanden."
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# 3) Projektverzeichnis + Repo-Dateien holen
# ═══════════════════════════════════════════════════════════════════════════
c_info "Erstelle Projektverzeichnis: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$MODELS_DIR"

c_info "Lade app.py und requirements.txt von GitHub..."
wget -q -O "$INSTALL_DIR/app.py" "$REPO_RAW_BASE/app.py" \
    || { c_err "Konnte app.py nicht laden (Pfad im Repo geändert?)"; exit 1; }
wget -q -O "$INSTALL_DIR/requirements.txt" "$REPO_RAW_BASE/requirements.txt" \
    || { c_err "Konnte requirements.txt nicht laden (Pfad im Repo geändert?)"; exit 1; }

c_ok "app.py und requirements.txt heruntergeladen."

# ═══════════════════════════════════════════════════════════════════════════
# 4) Python venv + Requirements
# ═══════════════════════════════════════════════════════════════════════════
c_info "Erstelle Python virtualenv..."
$PYTHON_BIN -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

pip install --upgrade pip wheel setuptools

c_info "Installiere Requirements aus requirements.txt..."
pip install -r "$INSTALL_DIR/requirements.txt"

# ── llama-cpp-python passend zur Hardware (neu) bauen ───────────────────────
# requirements.txt installiert i.d.R. eine generische CPU-Version. Hier wird
# sie – falls eine GPU vorhanden ist – mit CUDA-Unterstützung neu gebaut.
if [[ "$HAS_GPU" == true ]]; then
    c_info "Baue llama-cpp-python MIT CUDA-Unterstützung (kann einige Minuten dauern)..."
    CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 \
        pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
else
    c_info "Baue llama-cpp-python im CPU-Modus..."
    CMAKE_ARGS="-DGGML_CUDA=off" FORCE_CMAKE=1 \
        pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
fi

c_ok "Python-Umgebung fertig eingerichtet."

# ═══════════════════════════════════════════════════════════════════════════
# 5) Modelle herunterladen
# ═══════════════════════════════════════════════════════════════════════════
download_if_missing() {
    local label="$1" url="$2" dest="$3"
    if [[ -f "$dest" ]]; then
        c_ok "$label bereits vorhanden, überspringe: $dest"
    else
        c_info "Lade $label..."
        wget -c -O "$dest" "$url"
        c_ok "$label heruntergeladen."
    fi
}

download_if_missing "LLM GGUF-Modell (Qwen2.5-7B-Instruct-Q4_K_M)" "$LLM_MODEL_URL" "$LLM_MODEL_FILE"
download_if_missing "Piper-Stimme (de_DE-thorsten-high.onnx)" "$TTS_MODEL_URL" "$TTS_MODEL_FILE"
download_if_missing "Piper-Konfiguration (de_DE-thorsten-high.onnx.json)" "$TTS_CONFIG_URL" "$TTS_CONFIG_FILE"

# ═══════════════════════════════════════════════════════════════════════════
# 6) Start-Skript ablegen
# ═══════════════════════════════════════════════════════════════════════════
cat > "$INSTALL_DIR/start.sh" <<EOF
#!/usr/bin/env bash
cd "$INSTALL_DIR"
source "$VENV_DIR/bin/activate"
python app.py
EOF
chmod +x "$INSTALL_DIR/start.sh"

deactivate

# ═══════════════════════════════════════════════════════════════════════════
# Zusammenfassung
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "════════════════════════════════════════════════════════════════"
c_ok "Installation abgeschlossen!"
echo "  Verzeichnis:   $INSTALL_DIR"
echo "  Modelle:       $MODELS_DIR"
echo "  Hardware-Modus: $( [[ "$HAS_GPU" == true ]] && echo 'GPU (CUDA)' || echo 'CPU' )"
echo
echo "  Server starten mit:"
echo "    $INSTALL_DIR/start.sh"
echo "════════════════════════════════════════════════════════════════"
