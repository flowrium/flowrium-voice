---
name: edge-vosk-test
description: Run Vosk batch ASR tests locally (no external service needed) against audio manifests. Supports small and big Chinese models with CER metrics and RTF. Accepts args like "10" (limit), "--model big --limit 5", "--role principal", etc.
metadata:
  author: flowrium
  version: "1.0"
---

Run Vosk batch ASR tests against the project's audio manifests using local Vosk Kaldi models. This skill wraps `verification-3-edge/vosk/scripts/test_vosk_batch.py` and provides structured result formatting. **No external service is needed** -- inference runs locally via the Vosk Python API.

## Arguments

The skill accepts arguments passed after `/edge-vosk-test`. Parse them as follows:

- **A bare number** → treated as `--limit` (test only the first N rows). Example: `/edge-vosk-test 10`
- **Any other text** → passed through as-is to the script. Example: `/edge-vosk-test --model big --role principal`
- **No arguments** → run with defaults (all rows, small model)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/edge-vosk-test` | (no args) | All rows, small model |
| `/edge-vosk-test 5` | `--limit 5` | First 5 rows, small model |
| `/edge-vosk-test --model big` | `--model big` | All rows, big model |
| `/edge-vosk-test 10 --model big` | `--model big --limit 10` | First 10 rows, big model |
| `/edge-vosk-test --role principal` | `--role principal` | All principal rows, small model |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. All other arguments pass through unchanged.

## Prerequisites

- Vosk Python package installed (`pip install vosk`)
- Vosk models auto-downloaded (run `download_models.sh` first, or let the Python API auto-download on first use)
- Audio manifests exist under `audio/` directories
- **No external service required** -- runs fully offline

## Commands

### Quick test

```bash
python verification-3-edge/vosk/scripts/test_vosk_batch.py [--model small|big] [--limit N] [--version V] [--role R]
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--model` | Model to use: `small`, `big` | `small` |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--limit` | Only test first N rows | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** -- apply the rules from the Arguments section above (bare number → `--limit`)
2. **Check prerequisites** -- verify vosk is importable and model is cached
3. **Run the test command** with parsed args
4. **Format and present results** using the structure below

## Metrics & Report Format

指标说明和报告格式见公共文件：[_shared/asr-report-format.md](../_shared/asr-report-format.md)

### Vosk 特有说明

- **无需外部服务**：本地 Kaldi 推理，纯 Python API
- 支持 2 种中文模型：
  - **small** (默认)：vosk-model-small-cn-0.22，约 42MB
  - **big**：vosk-model-cn-0.22，约 1.3GB
- **不支持热词**：Vosk 的 SetGrammar 是词汇表约束，不是热词偏置
- 结果自动保存到 `verification-3-edge/vosk/results/`
- 文件名格式：`vosk-{model}-no-hotword-results.{json|csv}` 及 `-report.md`

## Common Workflows

### "Run a quick smoke test"
```bash
python verification-3-edge/vosk/scripts/test_vosk_batch.py --limit 5
```

### "Test with big model"
```bash
python verification-3-edge/vosk/scripts/test_vosk_batch.py --model big --limit 10
```

### "Test only principal role"
```bash
python verification-3-edge/vosk/scripts/test_vosk_batch.py --role principal
```

### "Filter by specific version"
```bash
python verification-3-edge/vosk/scripts/test_vosk_batch.py --version standard
```

## Notes

- Vosk 运行纯本地推理，不需要任何外部服务
- 模型通过 `download_models.sh` 下载到 `verification-3-edge/vosk/models/`，测试脚本通过本地路径加载
- 使用 Levenshtein 距离计算 CER
- 文本归一化去除所有中英文标点和空格后再比较
- `vosk.SetLogLevel(-1)` 抑制 Kaldi 的 INFO/WARNING 日志
- `rec.SetWords(True)` 启用词级时间戳（保留以备将来使用）
- Results are saved to `verification-3-edge/vosk/results/`
