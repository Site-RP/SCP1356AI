#!/bin/bash

set -e

REPO_URL="https://github.com/Site-RP/SCP1356AI.git"
PROJECT_DIR="SCP1356AI"

echo "[1/5] System prüfen..."

if ! command -v python3 >/dev/null 2>&1; then
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git
fi

if ! command -v git >/dev/null 2>&1; then
    apt-get update
    apt-get install -y git
fi

echo "[2/5] Repository vorbereiten..."

if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Repository existiert bereits."
    cd "$PROJECT_DIR"
    git pull
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo "Aktuelles Verzeichnis:"
pwd

echo "Dateien:"
ls -la

echo "[3/5] Virtual Environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "[4/5] Abhängigkeiten installieren..."

python -m pip install --upgrade pip

if [ -f requirements.txt ]; then
    python -m pip install -r requirements.txt
elif [ -f Requirements.txt ]; then
    python -m pip install -r Requirements.txt
else
    echo "FEHLER: Keine requirements.txt oder Requirements.txt gefunden!"
    exit 1
fi

echo "[5/5] SCP1356AI starten..."

python app.py
