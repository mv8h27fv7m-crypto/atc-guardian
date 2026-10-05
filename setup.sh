#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
(cd frontend && npm ci --no-fund && npm run build)
.venv/bin/python -m pytest
printf '\nReady. Run: .venv/bin/python run.py\n'
