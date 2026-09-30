#!/bin/bash
# Champignon Editor launcher script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Launching Champignon Editor..."
python3 champignon_editor.py "$@"
