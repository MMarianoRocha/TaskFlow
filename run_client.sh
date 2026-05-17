#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT_DIR/venv/bin/activate"
cd "$ROOT_DIR"

API_URL="${1:-${POMODORO_HUB_API_URL:-http://127.0.0.1:8000}}"

export POMODORO_HUB_API_URL="$API_URL"
python -m desktop --api-url "$API_URL"
