#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

has_tkinter() {
  "$1" - <<'PY' >/dev/null 2>&1
import tkinter
PY
}

PYTHON_BIN="${PYTHON:-}"

if [ -n "$PYTHON_BIN" ]; then
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Requested PYTHON=$PYTHON_BIN was not found."
    exit 1
  fi
elif command -v python3 >/dev/null 2>&1 && has_tkinter "$(command -v python3)"; then
  PYTHON_BIN="$(command -v python3)"
elif [ -x /usr/local/bin/python3 ] && has_tkinter /usr/local/bin/python3; then
  PYTHON_BIN=/usr/local/bin/python3
elif [ -x /opt/homebrew/bin/python3 ] && has_tkinter /opt/homebrew/bin/python3; then
  PYTHON_BIN=/opt/homebrew/bin/python3
else
  echo "Could not find a Python 3 interpreter with tkinter support."
  echo "Install the python.org macOS installer, or use a Homebrew Python with Tk support."
  echo "You can also run: PYTHON=/path/to/python3 ./setup_macos.sh"
  exit 1
fi

if ! has_tkinter "$PYTHON_BIN"; then
  echo "$PYTHON_BIN does not have tkinter support."
  echo "Try PYTHON=/path/to/python3 ./setup_macos.sh with a Tk-enabled Python."
  exit 1
fi

if [ -x .venv/bin/python ] && ! has_tkinter .venv/bin/python; then
  echo "Existing .venv was created with a Python build without tkinter; recreating it."
  rm -rf .venv
fi

echo "Using Python: $PYTHON_BIN"
"$PYTHON_BIN" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo
echo "Setup complete."
echo "Run the GUI with:"
echo "  .venv/bin/python main.py"
