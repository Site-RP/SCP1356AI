#!/bin/bash

set -e

REPO_URL="https://github.com/Site-RP/SCP1356AI.git"
PROJECT_DIR="SCP1356AI"

echo "[1/5] System prüfen..."

# Python prüfen
if ! command -v python3 &> /dev/null; then
    echo "Python3 nicht gefunden. Installiere..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip git
fi

# Git prüfen
if ! command -v git &> /dev/null; then
    echo "Git nicht gefunden. Installiere..."
    sudo apt update
    sudo apt install -y git
fi


echo "[2/5] Repository klonen..."

if [ -d "$PROJECT_DIR" ]; then
    echo "Projekt existiert bereits, überspringe Clone."
else
    git clone "$REPO_URL"
fi

cd "$PROJECT_DIR"


echo "[3/5] Virtual Environment erstellen..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate


echo "[4/5] Requirements installieren..."

python -m pip install --upgrade pip
python -m pip install -r requirements.txt


echo "[5/5] SCP1356AI starten..."

python app.py
