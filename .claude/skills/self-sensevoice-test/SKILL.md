---
name: self-sensevoice-test
description: Run SenseVoice batch ASR tests via HTTP API against audio manifests. Outputs CER metrics, latency, language detection, and grouped summaries. Accepts args like "10" (limit), "--role principal", "--language zh", etc.
metadata:
  author: flowrium
  version: "1.0"
---

Run SenseVoice batch ASR tests against the project's audio manifests via the SenseVoice HTTP API service. This skill wraps `verification-2-self/sensevoice/scripts/test_sensevoice_batch.py` and provides structured result formatting.

## Arguments

The skill accepts arguments passed after `/self-sensevoice-test`. Parse them as follows:

- **A bare number** -> treated as `--limit` (test only the first N rows **across all roles**). Example: `/self-sensevoice-test 10`
- **Any other text** -> passed through as-is to the script. Example: `/self-sensevoice-test --role principal --language zh`
- **No arguments** -> run with defaults (all rows, language auto)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/self-sensevoice-test` | `--api-url http://localhost:8000 --language auto` | All rows, auto language |
| `/self-sensevoice-test 5` | `--api-url http://localhost:8000 --language auto --limit 5` | First 5 rows total |
| `/self-sensevoice-test --role principal` | `--api-url http://localhost:8000 --language auto --role principal` | All principal rows only |
| `/self-sensevoice-test 10 --language zh` | `--api-url http://localhost:8000 --language zh --limit 10` | First 10 rows, Chinese forced |
| `/self-sensevoice-test --language en --limit 20` | `--api-url http://localhost:8000 --language en --limit 20` | 20 rows, English forced |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. All other arguments pass through unchanged.

## Prerequisites

- SenseVoice HTTP API service must be running (default: `http://localhost:8000`, endpoint `/extract_text`)
- Python dependencies installed: `requests`
- Audio manifests exist under `audio/` directories

## Commands

### Quick test

```bash
python verification-2-self/sensevoice/scripts/test_sensevoice_batch.py --api-url http://localhost:8000 --language auto [--limit N] [--version V] [--role R]
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--api-url` | SenseVoice HTTP API endpoint | `http://localhost:8000` |
| `--language` | Language hint: `auto`, `zh`, `en`, `ja`, `ko`, `yue` | `auto` |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--limit` | Only test first N rows | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |
| `--output-json` | Write JSON report to file | `verification-2-self/sensevoice/results/sensevoice-results.json` |
| `--output-csv` | Write CSV results to file | `verification-2-self/sensevoice/results/sensevoice-results.csv` |
| `--output-md` | Write Markdown summary report to file | `verification-2-self/sensevoice/results/sensevoice-report.md` |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** -- apply the rules from the Arguments section above (bare number -> `--limit`)
2. **Check the SenseVoice service** -- verify the HTTP endpoint is reachable before starting tests
3. **Run the test command** with parsed args
4. **Format and present results** using the structure below

## Metrics & Report Format

指标说明和报告格式见公共文件：[_shared/asr-report-format.md](../_shared/asr-report-format.md)

### SenseVoice 特有说明

- SenseVoice 走 HTTP API，非 WebSocket，无流式处理
- 支持语言检测（label 中的 `<|lang|>` 标签）和情绪识别（`<|emotion|>` 标签）
- `language` 参数可选 `auto/zh/en/ja/ko/yue`
- 无热词参数
- 默认 API endpoint 是 `http://localhost:8000`，POST `/extract_text`

## Common Workflows

### "Run a quick smoke test"
```bash
python verification-2-self/sensevoice/scripts/test_sensevoice_batch.py --api-url http://localhost:8000 --language auto --limit 5
```

### "Test only principal role"
```bash
python verification-2-self/sensevoice/scripts/test_sensevoice_batch.py --api-url http://localhost:8000 --language auto --role principal
```

### "Force Chinese recognition"
```bash
python verification-2-self/sensevoice/scripts/test_sensevoice_batch.py --api-url http://localhost:8000 --language zh
```

### "Test English audio"
```bash
python verification-2-self/sensevoice/scripts/test_sensevoice_batch.py --api-url http://localhost:8000 --language en
```

### "Run and save detailed results"
```bash
python verification-2-self/sensevoice/scripts/test_sensevoice_batch.py --api-url http://localhost:8000 --language auto --output-json verification-2-self/sensevoice/results/sensevoice-results.json --output-csv verification-2-self/sensevoice/results/sensevoice-results.csv --output-md verification-2-self/sensevoice/results/sensevoice-report.md
```

## Notes

- SenseVoice uses HTTP REST API (POST `{api_url}/extract_text` with multipart form data), not WebSocket
- Audio file is sent as `file` field, `language` as form data
- The response contains `results` (transcribed text) and `label_result` (tags like `<|zh|><|NEUTRAL|>`)
- Label result parsing extracts language and emotion tags; the clean text is used for CER comparison
- Text normalization strips all CJK/Latin punctuation before comparison
- Results are saved to `verification-2-self/sensevoice/results/`
- After each run, the script refreshes `verification-2-self/_cross-engine/results/multi-engine-comparison.md`