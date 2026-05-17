#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT_DIR/venv/bin/activate"

PORT=8000
if command -v lsof >/dev/null 2>&1; then
  if lsof -iTCP:"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Porta $PORT já está em uso. Pare o servidor que está rodando ou escolha outra porta."
    exit 1
  fi
fi

uvicorn app.app:app --host 0.0.0.0 --port "$PORT"
