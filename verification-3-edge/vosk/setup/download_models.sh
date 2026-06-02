#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MODELS_DIR="$ENGINE_DIR/models"

BASE_URL="https://alphacephei.com/vosk/models"

echo "=== Downloading Vosk models ==="
mkdir -p "$MODELS_DIR"

download_and_extract() {
    local zip_name="$1"
    local label="$2"
    local target_dir="$MODELS_DIR/$zip_name"

    if [ -d "$target_dir" ] && [ -f "$target_dir/am/final.mdl" ]; then
        echo "[$label] already exists, skipping."
        return 0
    fi

    echo "[$label] downloading $zip_name ..."
    curl -L --fail --progress-bar -o "$MODELS_DIR/$zip_name.zip" "$BASE_URL/$zip_name.zip"
    echo "[$label] extracting ..."
    unzip -q -o "$MODELS_DIR/$zip_name.zip" -d "$MODELS_DIR"
    rm -f "$MODELS_DIR/$zip_name.zip"
    echo "[$label] ready: $target_dir"
}

download_and_extract "vosk-model-small-cn-0.22" "small"
download_and_extract "vosk-model-cn-0.22" "big"

echo ""
echo "=== Models downloaded ==="
ls -d "$MODELS_DIR"/*/
