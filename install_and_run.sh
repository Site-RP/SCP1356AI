#!/bin/bash

set -e

REPO_URL="https://github.com/Site-RP/SCP1356AI.git"
PROJECT_DIR="SCP1356AI"

echo "[1/7] System prüfen..."

apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    ffmpeg

echo "[2/7] Repository vorbereiten..."

if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Repository existiert bereits."
    cd "$PROJECT_DIR"
    git pull
else
    git clone "$REPO_URL"
    cd "$PROJECT_DIR"
fi

echo "[3/7] Virtual Environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "[4/7] Python-Abhängigkeiten..."

python -m pip install --upgrade pip

export CMAKE_ARGS="-DGGML_CUDA=ON"
export FORCE_CMAKE=1

pip install -r requirements.txt
pip install huggingface_hub

mkdir -p models

echo "[5/7] Piper herunterladen..."

if [ ! -f models/de_DE-thorsten-high.onnx ]; then
    wget -O models/de_DE-thorsten-high.onnx \
        https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
fi

if [ ! -f models/de_DE-thorsten-high.onnx.json ]; then
    wget -O models/de_DE-thorsten-high.onnx.json \
        https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
fi

echo "[6/7] Qwen herunterladen..."

if [ ! -f models/Qwen2.5-7B-Instruct-Q4_K_M.gguf ]; then
    python -m huggingface_hub download \
        Qwen/Qwen2.5-7B-Instruct-GGUF \
        Qwen2.5-7B-Instruct-Q4_K_M.gguf \
        --local-dir models
fi

echo "[7/7] SCP1356AI starten..."

python app.py
