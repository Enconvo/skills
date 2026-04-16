#!/usr/bin/env bash
# BotFather CLI wrapper — ensures Telethon is available and delegates to Python script.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/botfather.py"
VENV_DIR="$HOME/.botfather/venv"

# Ensure venv with telethon exists
if [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo "First run: setting up Python venv with Telethon..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet telethon
    echo "Done."
fi

exec "$VENV_DIR/bin/python3" "$PYTHON_SCRIPT" "$@"
