#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-qwenllm/qwen3-asr:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-qwen3-asr}"
HOST_PORT="${HOST_PORT:-8001}"
CONTAINER_PORT="${CONTAINER_PORT:-80}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3-ASR-1.7B}"
HF_HOME_HOST="${HF_HOME_HOST:-${HOME}/.cache/huggingface}"
STARTUP_TIMEOUT="${STARTUP_TIMEOUT:-600}"
VLLM_EXTRA_ARGS="${VLLM_EXTRA_ARGS:---enforce-eager}"
START_COMMAND="${START_COMMAND:-vllm serve \"$MODEL_NAME\" --host 0.0.0.0 --port ${CONTAINER_PORT} ${VLLM_EXTRA_ARGS}}"

if [[ "$(uname -s)" == "Darwin" ]]; then
  echo "Warning: qwenllm/qwen3-asr is a CUDA-based image."
  echo "It typically requires a Linux host with NVIDIA GPU support; Docker Desktop on macOS may not run it successfully."
fi

if lsof -iTCP:"$HOST_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Port $HOST_PORT is already in use."
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Qwen3-ASR container is already running."
    echo "API base: http://127.0.0.1:${HOST_PORT}/v1"
  else
    echo "Another process is using port $HOST_PORT. Stop it first or change HOST_PORT."
    exit 1
  fi
  exit 0
fi

mkdir -p "$HF_HOME_HOST"

echo "Starting Qwen3-ASR container..."
echo "  Image: $IMAGE"
echo "  Model: $MODEL_NAME"
echo "  API base: http://127.0.0.1:${HOST_PORT}/v1"
echo "  HuggingFace cache: $HF_HOME_HOST"
echo "  Startup timeout: ${STARTUP_TIMEOUT}s"
echo "  Start command: $START_COMMAND"

docker run -d \
  --name "$CONTAINER_NAME" \
  --shm-size 16g \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  -v "${HF_HOME_HOST}:/root/.cache/huggingface" \
  "$IMAGE" \
  bash -lc "$START_COMMAND" >/dev/null

echo "Waiting for Qwen3-ASR service to become ready..."
for i in $(seq 1 "$STARTUP_TIMEOUT"); do
  if curl -sf "http://127.0.0.1:${HOST_PORT}/v1/models" >/dev/null 2>&1; then
    echo "Qwen3-ASR is ready!"
    echo "  API base: http://127.0.0.1:${HOST_PORT}/v1"
    echo "  Transcriptions: http://127.0.0.1:${HOST_PORT}/v1/audio/transcriptions"
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for Qwen3-ASR to start. Check logs:"
echo "  docker logs ${CONTAINER_NAME}"
exit 1
