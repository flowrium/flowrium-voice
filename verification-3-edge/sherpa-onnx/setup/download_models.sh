#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODELS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/models"

PARAFORMER_REPO="csukuangfj/sherpa-onnx-paraformer-zh-int8-2025-10-07"
SENSEVOICE_REPO="csukuangfj/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09"
TRANSDUCER_REPO="csukuangfj/sherpa-onnx-streaming-zipformer-zh-int8-2025-06-30"

echo "=== Downloading Sherpa-ONNX quantized models ==="
echo "Models directory: $MODELS_DIR"
mkdir -p "$MODELS_DIR"

download_model() {
    local repo="$1"
    local dest="$2"
    shift 2
    local required_files=("$@")
    local name
    name=$(basename "$dest")

    local all_present=1
    local file
    for file in "${required_files[@]}"; do
        if [ ! -f "$dest/$file" ]; then
            all_present=0
            break
        fi
    done

    if [ "$all_present" -eq 1 ]; then
        echo "  [$name] Already exists, skipping."
        return 0
    fi

    echo "  [$name] Downloading from $repo ..."
    python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('$repo', local_dir='$dest', ignore_patterns=['test_wavs/*'])
"
    echo "  [$name] Done."
}

echo ""
download_model "$PARAFORMER_REPO" "$MODELS_DIR/paraformer-zh-int8" "model.int8.onnx" "tokens.txt"
download_model "$SENSEVOICE_REPO" "$MODELS_DIR/sense-voice-zh-int8" "model.int8.onnx" "tokens.txt"
download_model "$TRANSDUCER_REPO" "$MODELS_DIR/zipformer-transducer-zh-int8" \
  "encoder.int8.onnx" "decoder.onnx" "joiner.int8.onnx" "tokens.txt"

echo ""
echo "=== Models downloaded ==="
find "$MODELS_DIR" -maxdepth 2 \( -name "*.onnx" -o -name "tokens.txt" \) | sort
