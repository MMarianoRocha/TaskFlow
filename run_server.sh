#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT_DIR/venv/bin/activate"

uvicorn app.app:app --host 0.0.0.0 --port 8000
