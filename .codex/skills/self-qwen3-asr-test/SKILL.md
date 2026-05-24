---
name: self-qwen3-asr-test
description: Run Qwen3-ASR batch ASR tests via an OpenAI-compatible HTTP transcription API against audio manifests. Outputs CER metrics, latency, and grouped summaries. Accepts args like "10" (limit), "--role principal", "--model Qwen/Qwen3-ASR-1.7B", etc.
metadata:
  author: flowrium
  version: "1.0"
---

Run Qwen3-ASR batch ASR tests against the project's audio manifests via the Qwen3-ASR OpenAI-compatible transcription API. This skill wraps `verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py` and provides structured result formatting.

## Arguments

The skill accepts arguments passed after `/self-qwen3-asr-test`. Parse them as follows:

- **A bare number** → treated as `--limit` (test only the first N rows **across all roles**). Example: `/self-qwen3-asr-test 10`
- **Any other text** → passed through as-is to the script. Example: `/self-qwen3-asr-test --role principal --model Qwen/Qwen3-ASR-1.7B`
- **No arguments** → run with defaults (all rows, default API URL, default model)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/self-qwen3-asr-test` | `--api-url http://127.0.0.1:8001/v1/audio/transcriptions --model Qwen/Qwen3-ASR-1.7B` | All rows |
| `/self-qwen3-asr-test 5` | `--api-url http://127.0.0.1:8001/v1/audio/transcriptions --model Qwen/Qwen3-ASR-1.7B --limit 5` | First 5 rows total |
| `/self-qwen3-asr-test --role principal` | `--api-url http://127.0.0.1:8001/v1/audio/transcriptions --model Qwen/Qwen3-ASR-1.7B --role principal` | All principal rows |
| `/self-qwen3-asr-test 10 --language zh` | `--api-url http://127.0.0.1:8001/v1/audio/transcriptions --model Qwen/Qwen3-ASR-1.7B --limit 10 --language zh` | First 10 rows with a language hint |
| `/self-qwen3-asr-test --api-url http://host:8001/v1/audio/transcriptions` | `--api-url http://host:8001/v1/audio/transcriptions --model Qwen/Qwen3-ASR-1.7B` | Custom endpoint |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. All other arguments pass through unchanged.

## Prerequisites

- Qwen3-ASR service must be running and expose an OpenAI-compatible endpoint (default: `http://127.0.0.1:8001/v1/audio/transcriptions`)
- Python dependencies installed: `requests`
- Audio manifests exist under `audio/` directories
- If using the official `qwenllm/qwen3-asr` image, a Linux host with NVIDIA GPU support is typically required

## Commands

### Quick test

```bash
python verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py --api-url http://127.0.0.1:8001/v1/audio/transcriptions --model Qwen/Qwen3-ASR-1.7B [--limit N] [--version V] [--role R] [--language zh]
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--api-url` | Qwen3-ASR transcription endpoint | `http://127.0.0.1:8001/v1/audio/transcriptions` |
| `--model` | Model name sent to API | `Qwen/Qwen3-ASR-1.7B` |
| `--api-key` | Optional bearer token | empty |
| `--language` | Optional language hint | empty |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--limit` | Only test first N rows | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |
| `--output-json` | Write JSON report to file | `verification-2-self/qwen3-asr/results/qwen3-asr-results.json` |
| `--output-csv` | Write CSV results to file | `verification-2-self/qwen3-asr/results/qwen3-asr-results.csv` |
| `--output-md` | Write Markdown summary report to file | `verification-2-self/qwen3-asr/results/qwen3-asr-report.md` |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** — apply the rules from the Arguments section above (bare number → `--limit`)
2. **Check the Qwen3-ASR service** — verify the HTTP endpoint is reachable before starting tests
3. **Run the test command** with parsed args
4. **Format and present results** using the structure below

## Metrics & Report Format

指标说明和报告格式见公共文件：[_shared/asr-report-format.md](../_shared/asr-report-format.md)

### Qwen3-ASR 特有说明

- Qwen3-ASR 当前接入走 OpenAI-compatible `audio/transcriptions`
- 无热词参数，也不依赖流式 WebSocket 协议
- 报告中 `language_detected` 来自 API 返回的 `language` 字段

## Common Workflows

### "Run a quick smoke test"
```bash
python verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py --api-url http://127.0.0.1:8001/v1/audio/transcriptions --limit 5
```

### "Test only principal role"
```bash
python verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py --api-url http://127.0.0.1:8001/v1/audio/transcriptions --role principal
```

### "Test with explicit model name"
```bash
python verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py --api-url http://127.0.0.1:8001/v1/audio/transcriptions --model Qwen/Qwen3-ASR-1.7B
```

### "Test with language hint"
```bash
python verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py --api-url http://127.0.0.1:8001/v1/audio/transcriptions --language zh --limit 10
```

### "Run and save detailed results"
```bash
python verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py --api-url http://127.0.0.1:8001/v1/audio/transcriptions --output-json verification-2-self/qwen3-asr/results/qwen3-asr-results.json --output-csv verification-2-self/qwen3-asr/results/qwen3-asr-results.csv --output-md verification-2-self/qwen3-asr/results/qwen3-asr-report.md
```

## Notes

- This integration assumes an OpenAI-compatible transcription response containing at least `text`
- No hotword support is currently wired into this route
- Results are saved to `verification-2-self/qwen3-asr/results/`
- After each run, the script refreshes `verification-2-self/results/multi-engine-comparison.md`
