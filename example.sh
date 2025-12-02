#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  ZipAndHash - Example Runner (Unix/Linux/macOS)"
echo "============================================================"

# Activate venv
if [ -f "venv/bin/activate" ]; then
    . venv/bin/activate
else
    echo "[ERROR] Virtual environment not found: ./venv/"
    exit 1
fi

# --------------------------------------------------------------
# Modify parameters below as needed
# --------------------------------------------------------------

SRC="/path/to/source"
DST="/path/to/destination"
CPY="/path/to/copy"

# Optional flags (modify or remove as you prefer)
OPTIONS="--debug --fzip --fcpy --fmv --cpy \"$CPY\" --unsafe"

echo "Running:"
echo "    zah \"$SRC\" \"$DST\" $OPTIONS"
echo "--------------------------------------------------------------"

eval zah "$SRC" "$DST" "$OPTIONS"

echo "--------------------------------------------------------------"
echo "Execution completed."
