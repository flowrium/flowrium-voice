---
name: edge-sherpa-onnx-test
description: Run Sherpa-ONNX edge batch ASR tests against the project's audio manifests using local quantized models. Outputs CER, RTF, and grouped summaries. Accepts args like "10" (limit), "--model sensevoice", "--role principal", etc.
metadata:
  author: flowrium
  version: "1.0"
---

Run Sherpa-ONNX edge batch ASR tests against the project's audio manifests with local quantized models. This skill wraps `verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py` and provides structured result formatting.

## Arguments

The skill accepts arguments passed after `/edge-sherpa-onnx-test`. Parse them as follows:

- **A bare number** -> treated as `--limit` (test only the first N rows across all roles). Example: `/edge-sherpa-onnx-test 10`
- **Any other text** -> passed through as-is to the script. Example: `/edge-sherpa-onnx-test --model sensevoice --role principal`
- **No arguments** -> run with defaults (`--model paraformer`, all rows, all manifests)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/edge-sherpa-onnx-test` | `--model paraformer` | All rows with Paraformer Int8 |
| `/edge-sherpa-onnx-test 5` | `--model paraformer --limit 5` | First 5 rows total |
| `/edge-sherpa-onnx-test --model sensevoice` | `--model sensevoice` | All rows with SenseVoice Int8 |
| `/edge-sherpa-onnx-test --role principal` | `--model paraformer --role principal` | All principal rows only |
| `/edge-sherpa-onnx-test 10 --version myvoice` | `--model paraformer --limit 10 --version myvoice` | First 10 myvoice rows |
| `/edge-sherpa-onnx-test --manifest audio/standard/manifest.csv` | `--model paraformer --manifest audio/standard/manifest.csv` | Only one manifest |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. Unless `--model` is explicitly provided, default to `--model paraformer`.

## Prerequisites

- `sherpa-onnx` Python package installed and importable
- Model files present under `verification-3-edge/sherpa-onnx/models/`
- Audio manifests exist under `audio/`
- Recommended precheck:

```bash
bash verification-3-edge/sherpa-onnx/setup/verify_setup.sh
```

## Commands

### Quick test

```bash
python3 verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model paraformer [--limit N] [--version V] [--role R]
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--model` | Model to test: `paraformer` or `sensevoice` | `paraformer` |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--limit` | Only test first N rows | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |
| `--hotword` | Hotword to pass through | none |
| `--hotwords-file` | Hotwords file path | `config/hotwords.txt` |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** - apply the rules from the Arguments section above (bare number -> `--limit`)
2. **Check local setup** - confirm `sherpa_onnx` imports and model files exist before starting tests
3. **Run the test command** with parsed args
4. **Format and present results** by following the shared ASR report format file, with Sherpa-ONNX-specific metric substitutions noted below

## Metrics & Report Format

指标说明和默认输出格式必须遵循公共文件：[asr-report-format.md](../../../.claude/skills/_shared/asr-report-format.md)

### Sherpa-ONNX 特有说明

- 这是本地离线推理，不依赖 WebSocket 或 HTTP 服务
- 主要指标是 `总体成功率`、`CER` 和 `RTF`
- 当前仓库里的 Paraformer Int8 和 SenseVoice Int8 都不支持热词；传入 `--hotword` 时脚本会忽略并提示
- 结果默认写到 `verification-3-edge/sherpa-onnx/results/`
- 单次运行的用户汇报结构默认沿用 shared format 的 `Single Mode Run`
- shared format 里的 `平均最终延迟` / `P95 最终延迟` 在本 skill 中替换为 `平均 RTF` / `P95 RTF`
- 如果脚本打印大量逐条日志或重采样日志，只用于内部观察；面向用户的最终汇报仍按 shared format 收口，不直接粘贴原始长日志

## Common Workflows

### "Run a quick smoke test"

```bash
python3 verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model paraformer --limit 5
```

### "Compare the two models on the same slice"

```bash
python3 verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model paraformer --role principal --limit 20
python3 verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model sensevoice --role principal --limit 20
```

### "Test only myvoice"

```bash
python3 verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model paraformer --version myvoice
```

### "Run full batch with SenseVoice"

```bash
python3 verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model sensevoice
```

## Notes

- This skill is for edge accuracy validation, not platform integration testing
- Accuracy results are model-level and do not need to be split by Android vs Apple when the same ONNX model and preprocessing path are used
- Platform-specific work such as streaming latency, memory, and integration belongs in later edge benchmark or integration tasks
