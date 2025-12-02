#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  ZipAndHash Installation Script  (Unix/Linux/macOS)"
echo "============================================================"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python3 is not installed or not in PATH."
    exit 1
fi

# Create venv if missing
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
. venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing project..."
pip install .

echo "------------------------------------------------------------"
echo "Installation completed successfully."
echo "------------------------------------------------------------"
zah -h

read -r -p "Press ENTER to continue..."
