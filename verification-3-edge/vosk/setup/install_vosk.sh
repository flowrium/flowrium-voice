#!/usr/bin/env bash
set -euo pipefail

echo "=== Installing Vosk ==="

if python3 -c "import vosk" 2>/dev/null; then
    echo "vosk already installed, skipping."
    python3 -c "import vosk; print('  OK: vosk is importable')"
    exit 0
fi

python3 -m pip install vosk

echo ""
echo "=== Verifying installation ==="
python3 -c "import vosk; print('vosk installed successfully')"

echo "Done."
