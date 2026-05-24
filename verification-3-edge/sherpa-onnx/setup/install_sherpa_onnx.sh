#!/usr/bin/env bash
set -euo pipefail

echo "=== Installing sherpa-onnx ==="

if python3 -c "import sherpa_onnx" 2>/dev/null; then
    echo "sherpa-onnx already installed, skipping."
    python3 -c "import sherpa_onnx; print(f'  version: {sherpa_onnx.__version__}')"
    exit 0
fi

python3 -m pip install sherpa-onnx

echo ""
echo "=== Verifying installation ==="
python3 -c "import sherpa_onnx; print(f'sherpa-onnx installed: version {sherpa_onnx.__version__}')"

echo "Done."
