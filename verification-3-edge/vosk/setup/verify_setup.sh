#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "=== Verifying Vosk setup ==="

echo ""
echo "1. Checking vosk pip package..."
python3 -c "import vosk; print('   OK: vosk is importable')"

echo ""
echo "2. Checking model availability..."
MODEL_PATH="$ENGINE_DIR/models/vosk-model-small-cn-0.22"
if [ -d "$MODEL_PATH" ] && [ -f "$MODEL_PATH/am/final.mdl" ]; then
    echo "   OK: model at $MODEL_PATH"
else
    echo "   MISSING: model not found at $MODEL_PATH"
    echo "   Run download_models.sh first."
    exit 1
fi

echo ""
echo "3. Checking test audio..."
TEST_AUDIO=$(find "$ROOT_DIR/audio/standard" -name "*.wav" -type f | head -1)
if [ -n "$TEST_AUDIO" ]; then
    echo "   OK: $TEST_AUDIO"
else
    echo "   MISSING: no test audio found in audio/standard/"
    exit 1
fi

echo ""
echo "4. Running inference with small model..."
python3 -c "
import json
import wave
import vosk

vosk.SetLogLevel(-1)
model = vosk.Model(model_path='$MODEL_PATH')

with wave.open('$TEST_AUDIO', 'rb') as wf:
    sample_rate = wf.getframerate()
    pcm_data = wf.readframes(wf.getnframes())

rec = vosk.KaldiRecognizer(model, sample_rate)
rec.SetWords(True)
rec.AcceptWaveform(pcm_data)
result = json.loads(rec.FinalResult())

print(f'   Input: $TEST_AUDIO')
print(f'   Output: {result.get(\"text\", \"\")}')
print(f'   OK: Vosk inference works!')
"

echo ""
echo "=== Setup verification passed! ==="
