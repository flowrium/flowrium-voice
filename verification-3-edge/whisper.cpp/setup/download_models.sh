#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENDOR_DIR="$ENGINE_DIR/vendor/whisper.cpp"
MODELS_DIR="$ENGINE_DIR/models"

echo "=== Downloading whisper.cpp models ==="
mkdir -p "$MODELS_DIR"

if [ ! -x "$VENDOR_DIR/models/download-ggml-model.sh" ]; then
  echo "Missing downloader: $VENDOR_DIR/models/download-ggml-model.sh" >&2
  echo "Run install_whisper_cpp.sh first." >&2
  exit 1
fi

download_model() {
  local source_name="$1"
  local target_file="$2"
  if [ -f "$MODELS_DIR/$target_file" ]; then
    echo "[$source_name] already exists, skipping."
    return 0
  fi

  echo "[$source_name] downloading ..."
  (
    cd "$VENDOR_DIR/models"
    bash ./download-ggml-model.sh "$source_name"
  )
  cp "$VENDOR_DIR/models/ggml-$source_name.bin" "$MODELS_DIR/$target_file"
}

download_model "base" "ggml-base.bin"
download_model "small" "ggml-small.bin"
download_model "large-v3-turbo-q5_0" "ggml-large-v3-turbo-q5_0.bin"

echo ""
echo "=== Models ready ==="
find "$MODELS_DIR" -maxdepth 1 -name "*.bin" | sort
