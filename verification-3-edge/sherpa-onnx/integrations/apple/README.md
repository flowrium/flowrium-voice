# Apple Integration

This directory is for Apple-platform Sherpa-ONNX integration work.

## Current Scope

Current repo status:

- Model-level accuracy validation is done in the shared top-level scripts/results
- Apple-specific integration code is not implemented yet
- Apple-specific performance measurement now lives in `../../benchmarks/apple/`

## Recommended Integration Order

### 1. macOS validation

Use the existing Python-based local inference path and benchmark it on the current Mac:

```bash
bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh
```

This answers:

- Can the chosen model run reliably on Apple hardware?
- What are the reference `RTF` and memory numbers on the current Mac?

### 2. Native Apple demo

After benchmark numbers are acceptable, build a minimal native Apple demo under `demo/`:

- load `model.int8.onnx`
- load `tokens.txt`
- feed one local WAV
- print transcription

The first demo should stay offline and file-based.
Do not start from microphone streaming first.

### 3. Real-time Apple app path

After file-based inference works:

- connect microphone input
- measure first-token / final latency
- record memory growth during continuous usage

## Platform Goals

For Apple-side verification, collect:

- model load time
- single-utterance inference time
- Avg/P95 RTF
- peak memory
- streaming latency (later)

## Directory Intent

- `setup/` - Apple dependency/bootstrap notes or scripts
- `demo/` - minimal native Apple demo app or CLI
