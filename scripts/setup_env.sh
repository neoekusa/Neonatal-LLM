#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python_bin="${PYTHON:-}"
if [[ -z "$python_bin" ]]; then
    for candidate in python3.12 python3.13 python3.11 python3; do
        if command -v "$candidate" >/dev/null && "$candidate" -c 'import sys; sys.exit(not ((3, 11) <= sys.version_info[:2] <= (3, 13)))'; then
            python_bin="$candidate"
            break
        fi
    done
fi
if [[ -z "$python_bin" ]]; then
    echo "Install Python 3.12, or set PYTHON to a Python 3.11–3.13 interpreter." >&2
    exit 1
fi
if [[ ! -x .venv/bin/python ]]; then
    "$python_bin" -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
echo "Python setup complete. The full analysis also uses R and the lme4 package."
echo "Run .venv/bin/python scripts/run_core_pipeline.py --with-figures"
if .venv/bin/python -c 'import tkinter' >/dev/null 2>&1; then
    echo "Launch the graphical runner with .venv/bin/python main.py"
fi
