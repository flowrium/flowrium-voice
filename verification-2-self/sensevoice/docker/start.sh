#!/usr/bin/env bash
set -euo pipefail

IMAGE="yiminger/sensevoice:latest"
CONTAINER_NAME="sensevoice"
PORT=8000
LANGUAGE="${LANGUAGE:-auto}"
STARTUP_TIMEOUT="${STARTUP_TIMEOUT:-120}"

# Check if port is already in use
if lsof -iTCP:"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Port $PORT is already in use."
  # Check if it's our container
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "SenseVoice container is already running."
    echo "API: http://localhost:$PORT"
    echo "Docs: http://localhost:$PORT/docs"
  else
    echo "Another process is using port $PORT. Stop it first or change the port."
    exit 1
  fi
  exit 0
fi

echo "Starting SenseVoice container..."
echo "  Image: $IMAGE"
echo "  Port: $PORT"
echo "  Language: $LANGUAGE"
echo "  Startup timeout: ${STARTUP_TIMEOUT}s"

docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT:8000" \
  -e LANGUAGE="$LANGUAGE" \
  "$IMAGE"

echo "Waiting for service to become ready..."
for i in $(seq 1 "$STARTUP_TIMEOUT"); do
  if curl -sf "http://127.0.0.1:$PORT/docs" >/dev/null 2>&1; then
    echo "SenseVoice is ready!"
    echo "  API: http://localhost:$PORT"
    echo "  Docs: http://localhost:$PORT/docs"
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for SenseVoice to start. Check logs:"
echo "  docker logs $CONTAINER_NAME"
exit 1
