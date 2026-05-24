#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODELS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/models"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "=== Verifying Sherpa-ONNX setup ==="

# Check pip package
echo ""
echo "1. Checking sherpa-onnx pip package..."
python3 -c "import sherpa_onnx; print(f'   OK: sherpa-onnx {sherpa_onnx.__version__}')"

# Check model files
echo ""
echo "2. Checking model files..."
check_model_files() {
    local model_dir="$1"
    shift
    local files=("$@")
    local file
    for file in "${files[@]}"; do
        if [ ! -f "$MODELS_DIR/$model_dir/$file" ]; then
            echo "   MISSING: $model_dir/$file — run download_models.sh first"
            exit 1
        fi
    done
    echo "   OK: $model_dir"
}

check_model_files "paraformer-zh-int8" "model.int8.onnx" "tokens.txt"
check_model_files "sense-voice-zh-int8" "model.int8.onnx" "tokens.txt"
check_model_files "zipformer-transducer-zh-int8" "encoder.int8.onnx" "decoder.onnx" "joiner.int8.onnx" "tokens.txt"

# Check test audio
echo ""
echo "3. Checking test audio..."
TEST_AUDIO=$(find "$ROOT_DIR/audio/standard" -name "*.wav" -type f | head -1)
if [ -n "$TEST_AUDIO" ]; then
    echo "   OK: $TEST_AUDIO"
else
    echo "   MISSING: no test audio found in audio/standard/"
    exit 1
fi

# Run inference
echo ""
echo "4. Running inference with Paraformer Int8..."
python3 -c "
import sherpa_onnx
import wave
import numpy as np

model_dir = '$MODELS_DIR/paraformer-zh-int8'
test_wav = '$TEST_AUDIO'

recognizer = sherpa_onnx.OfflineRecognizer.from_paraformer(
    paraformer=f'{model_dir}/model.int8.onnx',
    tokens=f'{model_dir}/tokens.txt',
)

stream = recognizer.create_stream()
with wave.open(test_wav, 'rb') as f:
    sample_rate = f.getframerate()
    frames = f.readframes(f.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

stream.accept_waveform(sample_rate, samples.tolist())
recognizer.decode_stream(stream)
result = stream.result.text

print(f'   Input: $TEST_AUDIO')
print(f'   Output: {result}')
print(f'   OK: Paraformer Int8 inference works!')
"

echo ""
echo "5. Running inference with Transducer Int8..."
python3 -c "
import sherpa_onnx
import wave
import numpy as np

model_dir = '$MODELS_DIR/zipformer-transducer-zh-int8'
test_wav = '$TEST_AUDIO'

recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
    tokens=f'{model_dir}/tokens.txt',
    encoder=f'{model_dir}/encoder.int8.onnx',
    decoder=f'{model_dir}/decoder.onnx',
    joiner=f'{model_dir}/joiner.int8.onnx',
)

stream = recognizer.create_stream()
with wave.open(test_wav, 'rb') as f:
    sample_rate = f.getframerate()
    frames = f.readframes(f.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

stream.accept_waveform(sample_rate, samples.tolist())
stream.input_finished()
while recognizer.is_ready(stream):
    recognizer.decode_stream(stream)
result = recognizer.get_result(stream)

print(f'   Input: $TEST_AUDIO')
print(f'   Output: {result}')
print(f'   OK: Transducer Int8 inference works!')
"

echo ""
echo "=== Setup verification passed! ==="
