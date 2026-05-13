#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT_DIR/venv/bin/activate"

API_URL="${1:-${POMODORO_HUB_API_URL:-}}"
if [[ -z "$API_URL" ]]; then
  echo "Uso: $0 http://<server_ip>:8000"
  echo "Ou defina POMODORO_HUB_API_URL no ambiente."
  exit 1
fi

export POMODORO_HUB_API_URL="$API_URL"
python "$ROOT_DIR/desktop_app.py" --api-url "$API_URL"
