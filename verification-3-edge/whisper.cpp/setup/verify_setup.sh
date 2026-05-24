#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CLI_PATH="$ENGINE_DIR/vendor/whisper.cpp/build/bin/whisper-cli"
MODEL_PATH="$ENGINE_DIR/models/ggml-base.bin"

echo "=== Verifying whisper.cpp setup ==="

if [ ! -x "$CLI_PATH" ]; then
  echo "Missing whisper-cli: $CLI_PATH" >&2
  echo "Run install_whisper_cpp.sh first." >&2
  exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
  echo "Missing model: $MODEL_PATH" >&2
  echo "Run download_models.sh first." >&2
  exit 1
fi

TEST_AUDIO="$(find "$ROOT_DIR/audio/standard" -name "*.wav" -type f | head -1)"
if [ -z "$TEST_AUDIO" ]; then
  echo "No test wav found under audio/standard" >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
OUT_PREFIX="$TMP_DIR/verify"

"$CLI_PATH" -m "$MODEL_PATH" -f "$TEST_AUDIO" -l zh -nt -otxt -of "$OUT_PREFIX" >/dev/null

if [ ! -f "$OUT_PREFIX.txt" ]; then
  echo "Expected transcript not produced: $OUT_PREFIX.txt" >&2
  exit 1
fi

echo "Input: $TEST_AUDIO"
echo "Output: $(tr '\n' ' ' < "$OUT_PREFIX.txt" | sed 's/[[:space:]]\+/ /g')"
echo "OK: whisper.cpp inference works"
