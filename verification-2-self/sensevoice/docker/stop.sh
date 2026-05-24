#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="sensevoice"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Stopping SenseVoice container..."
  docker stop "$CONTAINER_NAME" >/dev/null
  docker rm "$CONTAINER_NAME" >/dev/null
  echo "SenseVoice container stopped and removed."
else
  echo "No running SenseVoice container found."
fi
