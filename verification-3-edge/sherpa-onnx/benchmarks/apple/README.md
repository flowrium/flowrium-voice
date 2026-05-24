# Apple Benchmarks

This directory stores macOS / Apple-side performance measurements for Sherpa-ONNX edge inference.

## Purpose

`results/` under `verification-3-edge/sherpa-onnx/` records model-level accuracy.

This directory records Apple-platform performance metrics that are expected to vary by device:

- RTF
- wall-clock run time
- peak memory (`Max RSS`)

## Quick Start

Run the default macOS benchmark with Paraformer Int8:

```bash
bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh
```

Run SenseVoice:

```bash
bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh --model sensevoice
```

Run a smaller slice:

```bash
bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh --model paraformer -- --version myvoice --limit 60
```

## Output Files

Each run writes files under `benchmarks/apple/results/`:

- `<label>.log` - raw batch test stdout
- `<label>.time.txt` - `/usr/bin/time -l` output
- `<label>-benchmark.json` - structured benchmark summary
- `<label>-benchmark.md` - readable benchmark report

## Notes

- `Max RSS` is collected from `/usr/bin/time -l`
- These numbers are valid as **macOS reference values**, not iPhone/iPad final values
- For Apple edge go/no-go, prioritize:
  1. `Avg RTF`
  2. `P95 RTF`
  3. `Max RSS`
  4. `myvoice` accuracy slice
