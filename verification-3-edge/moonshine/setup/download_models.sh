#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MODELS_DIR="$ENGINE_DIR/models"
CACHE_DIR="$ENGINE_DIR/cache"
METADATA_DIR="$MODELS_DIR/metadata"

echo "=== Downloading Moonshine models ==="
mkdir -p "$MODELS_DIR" "$METADATA_DIR"

download_model() {
  local model_name="$1"
  local language="$2"
  local output_dir="$MODELS_DIR/$model_name"

  if find "$output_dir" \( -name "*.onnx" -o -name "*.bin" \) -print -quit >/dev/null 2>&1; then
    echo "[$model_name] already exists, skipping."
    return 0
  fi

  mkdir -p "$output_dir"
  echo "[$model_name] downloading ..."
  XDG_CACHE_HOME="$CACHE_DIR" python3 - "$language" "$output_dir" "$METADATA_DIR/$model_name.json" <<'PY'
import json
import shutil
import sys
from pathlib import Path

from moonshine_voice import get_model_for_language

language = sys.argv[1]
output_dir = Path(sys.argv[2])
metadata_path = Path(sys.argv[3])
model_path, model_arch = get_model_for_language(language, None)
model_path = Path(model_path)
target_path = output_dir / model_path.name
if not target_path.exists():
    shutil.copy2(model_path, target_path)
metadata_path.write_text(
    json.dumps(
        {
            "language": language,
            "source_model_path": str(model_path),
            "copied_model_path": str(target_path),
            "model_arch": model_arch,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print(target_path)
PY
}

download_model "zh" "zh"
download_model "en" "en"

echo ""
echo "=== Models ready ==="
find "$MODELS_DIR" -maxdepth 2 \( -name "*.onnx" -o -name "*.bin" -o -name "*.json" \) | sort
