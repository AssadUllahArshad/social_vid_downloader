#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export STATE_BACKEND=sqlite
cd "$ROOT_DIR/apps/api"
if [ ! -x .venv/bin/python ]; then
  echo "Set up the API virtualenv first; see README.md."
  exit 1
fi
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
API_PID=$!
trap 'kill "$API_PID" 2>/dev/null || true' EXIT INT TERM
cd "$ROOT_DIR"
npm run dev
