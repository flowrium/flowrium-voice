#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-mobvoiwenet/wenet:latest}"
CONTAINER_NAME="wenet"
PORT=10097
STARTUP_TIMEOUT="${STARTUP_TIMEOUT:-120}"
MODEL_DIR="${MODEL_DIR:-/home/20210618_u2pp_conformer_libtorch}"
CHUNK_SIZE="${CHUNK_SIZE:-16}"

if lsof -iTCP:"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Port $PORT is already in use."
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "WeNet container is already running."
    echo "WebSocket: ws://localhost:$PORT"
  else
    echo "Another process is using port $PORT. Stop it first or change the port."
    exit 1
  fi
  exit 0
fi

echo "Starting WeNet container..."
echo "  Image: $IMAGE"
echo "  Port: $PORT"
echo "  Model dir: $MODEL_DIR"
echo "  Chunk size: $CHUNK_SIZE"
echo "  Startup timeout: ${STARTUP_TIMEOUT}s"

docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT:$PORT" \
  "$IMAGE" \
  bash -lc "export GLOG_logtostderr=1; /home/wenet/runtime/server/x86/build/websocket_server_main --port $PORT --chunk_size $CHUNK_SIZE --model_path $MODEL_DIR/final.zip --dict_path $MODEL_DIR/words.txt"

echo "Waiting for WeNet WebSocket to become ready..."
for i in $(seq 1 "$STARTUP_TIMEOUT"); do
  if python3 -c "import socket; s=socket.create_connection(('127.0.0.1', $PORT), timeout=1); s.close()" >/dev/null 2>&1; then
    echo "WeNet is ready!"
    echo "  WebSocket: ws://localhost:$PORT"
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for WeNet to start. Check logs:"
echo "  docker logs $CONTAINER_NAME"
exit 1
