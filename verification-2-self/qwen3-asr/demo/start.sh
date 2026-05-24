#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-18083}"
API_URL="${QWEN3_ASR_API_URL:-http://127.0.0.1:8001/v1}"

echo "Starting Qwen3-ASR demo server..."
echo "  Demo: http://${HOST}:${PORT}"
echo "  Proxy target: ${API_URL}"

python3 "$(dirname "$0")/serve.py" --host "$HOST" --port "$PORT" --api-url "$API_URL"
