#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="wenet"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Stopping WeNet container..."
  docker stop "$CONTAINER_NAME" >/dev/null
  docker rm "$CONTAINER_NAME" >/dev/null
  echo "WeNet container stopped and removed."
else
  echo "No running WeNet container found."
fi
