#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-18081}"
WS_URL="${WENET_WS_URL:-ws://127.0.0.1:10097}"

echo "Starting WeNet demo server..."
echo "  Demo: http://${HOST}:${PORT}"
echo "  Proxy WebSocket: ws://${HOST}:$((PORT + 1))"
echo "  Upstream WeNet: ${WS_URL}"

python3 "$(dirname "$0")/serve.py" --host "$HOST" --port "$PORT" --ws-url "$WS_URL"
