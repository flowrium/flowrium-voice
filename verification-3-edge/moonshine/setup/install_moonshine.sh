#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Installing Moonshine ==="

python3 -m pip install --upgrade moonshine-voice soundfile
mkdir -p "$ENGINE_DIR/cache"
echo "OK: installed moonshine-voice and prepared cache dir $ENGINE_DIR/cache"
