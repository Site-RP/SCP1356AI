#!/usr/bin/env bash

set -e

REPO_URL="https://github.com/Site-RP/SCP1356AI.git"
REPO_NAME="SCP1356AI"

echo "Lade Repository herunter..."
git clone "$REPO_URL"

cd "$REPO_NAME"

echo "Erstelle models-Ordner..."
mkdir -p models

echo "Lade Sprachmodell herunter..."
wget -O models/de_DE-thorsten-high.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx"

echo "Lade LLM herunter..."
wget -O models/Qwen2.5-7B-Instruct-Q4_K_M.gguf \
    "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

cd .

echo "Erstelle Python Virtual Environment..."
python3 -m venv venv

echo "Aktiviere Virtual Environment..."
source venv/bin/activate

echo "Installiere Requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "fertig"
