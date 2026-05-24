#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CACHE_DIR="$ENGINE_DIR/cache"

echo "=== Verifying Moonshine setup ==="

MODEL_PATH="$(find "$ENGINE_DIR/models/zh" \( -name "*.onnx" -o -name "*.bin" \) | head -1)"
if [ -z "$MODEL_PATH" ]; then
  echo "No Chinese model found under $ENGINE_DIR/models/zh" >&2
  echo "Run download_models.sh first." >&2
  exit 1
fi

TEST_AUDIO="$(find "$ROOT_DIR/audio/standard" -name "*.wav" -type f | head -1)"
if [ -z "$TEST_AUDIO" ]; then
  echo "No test wav found under audio/standard" >&2
  exit 1
fi

XDG_CACHE_HOME="$CACHE_DIR" python3 - "$MODEL_PATH" "$TEST_AUDIO" <<'PY'
import sys
from moonshine_voice import Transcriber, load_wav_file

model_path = sys.argv[1]
test_audio = sys.argv[2]
transcriber = Transcriber(model_path=model_path)
audio_data, sample_rate = load_wav_file(test_audio)
transcript = transcriber.transcribe_without_streaming(audio_data, sample_rate=sample_rate, flags=0)
text = " ".join(line.text for line in transcript.lines).strip()
print(f"Input: {test_audio}")
print(f"Output: {text}")
PY
echo "OK: Moonshine inference works"
