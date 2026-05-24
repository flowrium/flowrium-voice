---
name: self-wenet-test
description: Run WeNet batch ASR tests via WebSocket against audio manifests. Outputs CER metrics, latency, and grouped summaries. Accepts args like "10" (limit), "--role principal", "--hotword 出勤率", etc.
metadata:
  author: flowrium
  version: "1.0"
---

Run WeNet batch ASR tests against the project's audio manifests via the WeNet WebSocket service. This skill wraps `verification-2-self/wenet/scripts/test_wenet_batch.py` and provides structured result formatting.

## Arguments

The skill accepts arguments passed after `/self-wenet-test`. Parse them as follows:

- **A bare number** → treated as `--limit` (test only the first N rows **across all roles**). Example: `/self-wenet-test 10`
- **Any other text** → passed through as-is to the script. Example: `/self-wenet-test --role principal --hotword 出勤率`
- **No arguments** → run with defaults (all rows, default WebSocket URL)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/self-wenet-test` | `--ws-url ws://127.0.0.1:10097` | All rows |
| `/self-wenet-test 5` | `--ws-url ws://127.0.0.1:10097 --limit 5` | First 5 rows total |
| `/self-wenet-test --role principal` | `--ws-url ws://127.0.0.1:10097 --role principal` | All principal rows |
| `/self-wenet-test 10 --hotword 出勤率` | `--ws-url ws://127.0.0.1:10097 --limit 10 --hotword 出勤率` | First 10 rows with one hotword |
| `/self-wenet-test --hotwords-file config/hotwords.txt` | `--ws-url ws://127.0.0.1:10097 --hotwords-file config/hotwords.txt` | Use hotwords from file |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. All other arguments pass through unchanged.

## Prerequisites

- WeNet WebSocket service must be running (default: `ws://127.0.0.1:10097`)
- Python dependencies installed: `websockets`
- Audio manifests exist under `audio/` directories

## Commands

### Quick test

```bash
python verification-2-self/wenet/scripts/test_wenet_batch.py --ws-url ws://127.0.0.1:10097 [--limit N] [--version V] [--role R] [--hotword WORD]
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--ws-url` | WeNet WebSocket endpoint | `ws://127.0.0.1:10097` |
| `--hotword` | Hotword to send (repeatable) | none |
| `--hotwords-file` | Hotwords file path | none |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--limit` | Only test first N rows | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |
| `--output-json` | Write JSON report to file | `verification-2-self/wenet/results/wenet-results.json` |
| `--output-csv` | Write CSV results to file | `verification-2-self/wenet/results/wenet-results.csv` |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** — apply the rules from the Arguments section above (bare number → `--limit`)
2. **Check the WeNet service** — verify the WebSocket endpoint is reachable before starting tests
3. **Run the test command** with parsed args
4. **Format and present results** using the structure below

## Metrics & Report Format

指标说明和报告格式见公共文件：[_shared/asr-report-format.md](../_shared/asr-report-format.md)

### WeNet 特有说明

无特殊附加指标，直接按公共格式展示结果。

## Common Workflows

### "Run a quick smoke test"
```bash
python verification-2-self/wenet/scripts/test_wenet_batch.py --ws-url ws://127.0.0.1:10097 --limit 5
```

### "Test only principal role"
```bash
python verification-2-self/wenet/scripts/test_wenet_batch.py --ws-url ws://127.0.0.1:10097 --role principal
```

### "Test with inline hotwords"
```bash
python verification-2-self/wenet/scripts/test_wenet_batch.py --ws-url ws://127.0.0.1:10097 --hotword 出勤率 --hotword 合格率
```

### "Test with hotwords file"
```bash
python verification-2-self/wenet/scripts/test_wenet_batch.py --ws-url ws://127.0.0.1:10097 --hotwords-file config/hotwords.txt
```

### "Run and save detailed results"
```bash
python verification-2-self/wenet/scripts/test_wenet_batch.py --ws-url ws://127.0.0.1:10097 --output-json verification-2-self/wenet/results/wenet-results.json --output-csv verification-2-self/wenet/results/wenet-results.csv
```

## Notes

- WeNet uses WebSocket, not HTTP
- The service expects `start -> binary audio frames -> end`
- Audio is sent in 960-sample frames at 16kHz
- Current runtime returns `nbest` as a JSON string; the wrapped script already handles this
- Results are saved to `verification-2-self/wenet/results/`
