#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENDOR_DIR="$ENGINE_DIR/vendor/whisper.cpp"

echo "=== Installing whisper.cpp ==="

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but not found." >&2
  exit 1
fi

mkdir -p "$ENGINE_DIR/vendor"

if [ ! -d "$VENDOR_DIR/.git" ]; then
  echo "Cloning whisper.cpp into $VENDOR_DIR ..."
  git clone https://github.com/ggml-org/whisper.cpp "$VENDOR_DIR"
else
  echo "whisper.cpp repo already present: $VENDOR_DIR"
fi

echo "Building whisper.cpp ..."
SDK_PATH="$(xcrun --show-sdk-path)"
export SDKROOT="$SDK_PATH"
export CXXFLAGS="${CXXFLAGS:-} -I$SDK_PATH/usr/include/c++/v1"
export CPPFLAGS="${CPPFLAGS:-} -I$SDK_PATH/usr/include/c++/v1"
if command -v cmake >/dev/null 2>&1; then
  cmake -S "$VENDOR_DIR" -B "$VENDOR_DIR/build" -DWHISPER_BUILD_TESTS=OFF -DCMAKE_CXX_FLAGS="-I$SDK_PATH/usr/include/c++/v1" -DCMAKE_C_FLAGS="-isysroot $SDK_PATH"
  cmake --build "$VENDOR_DIR/build" --config Release -j
  CLI_PATH="$VENDOR_DIR/build/bin/whisper-cli"
elif command -v make >/dev/null 2>&1; then
  make -C "$VENDOR_DIR" -j
  CLI_PATH="$VENDOR_DIR/build/bin/whisper-cli"
  if [ ! -x "$CLI_PATH" ] && [ -x "$VENDOR_DIR/main" ]; then
    CLI_PATH="$VENDOR_DIR/main"
  fi
else
  echo "Neither cmake nor make is available." >&2
  exit 1
fi

if [ ! -x "$CLI_PATH" ]; then
  echo "whisper-cli not found after build: $CLI_PATH" >&2
  exit 1
fi

echo "OK: built $CLI_PATH"
