---
name: self-funasr-test
description: Run FunASR batch ASR tests against audio manifests with comparison reports, CER metrics, and hotword analysis. Accepts args like "10" (limit), "10 --compare", "--role principal --limit 5", etc.
metadata:
  author: flowrium
  version: "1.2"
---

Run FunASR batch ASR tests against the project's audio manifests. This skill wraps `verification-2-self/funasr/scripts/test_funasr_batch.py` and provides structured result formatting.

## Arguments

The skill accepts arguments passed after `/self-funasr-test`. Parse them as follows:

- **A bare number** → treated as `--limit` (test only the first N rows **across all roles**). Example: `/self-funasr-test 10`
- **Any other text** → passed through as-is to the script. Example: `/self-funasr-test --compare --limit 5`
- **No arguments** → run with defaults (all rows, 2pass mode, hotwords from config)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/self-funasr-test` | `--mode 2pass` | All rows, all roles |
| `/self-funasr-test 5` | `--mode 2pass --limit 5` | First 5 rows total (across all roles) |
| `/self-funasr-test 20 --compare` | `--compare --limit 20` | First 20 rows total in comparison |
| `/self-funasr-test --role principal` | `--mode 2pass --role principal` | All principal rows only |
| `/self-funasr-test 10 --role teacher` | `--mode 2pass --limit 10 --role teacher` | First 10 teacher rows only |
| `/self-funasr-test --compare` | `--compare` | Full comparison, all roles |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. All other arguments pass through unchanged. `--limit` always counts total rows across all roles; only when `--role` is explicitly specified does it filter to that role first.

## Prerequisites

- FunASR WebSocket service must be running (default: `ws://127.0.0.1:10095`)
- Python dependencies installed: `websockets`
- Audio manifests exist under `audio/` directories

## Commands

### Quick test (single mode)

```bash
python verification-2-self/funasr/scripts/test_funasr_batch.py --mode 2pass [--hotword WORD] [--limit N] [--version V] [--role R]
```

### Full comparison (all modes x hotword combinations)

```bash
python verification-2-self/funasr/scripts/test_funasr_batch.py --compare
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--ws-url` | FunASR WebSocket endpoint | `ws://127.0.0.1:10095` |
| `--mode` | ASR mode: `2pass`, `online`, `offline` | `2pass` |
| `--hotword` | Hotword to send (repeatable) | from `config/hotwords.txt` |
| `--hotwords-file` | Hotwords file path | `config/hotwords.txt` |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--limit` | Only test first N rows (total across all roles, unless `--role` is specified) | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |
| `--compare` | Run all mode x hotword combos | off |
| `--output-json` | Write JSON report to file | `verification-2-self/funasr/results/paraformer-results.json` |
| `--output-csv` | Write CSV results to file | `verification-2-self/funasr/results/paraformer-results.csv` |
| `--output-md` | Write Markdown summary report to file | `verification-2-self/funasr/results/paraformer-single-report.md` |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** — apply the rules from the Arguments section above (bare number → `--limit`)
2. **Check the FunASR service** — verify the WebSocket endpoint is reachable before starting tests
3. **Run the appropriate command** based on parsed args:
   - If `--compare` present → full comparison run
   - Otherwise → single mode test with `--mode 2pass` (unless `--mode` specified)
4. **Format and present results** using the structure below

## Metrics & Report Format

指标说明和报告格式见公共文件：[_shared/asr-report-format.md](../_shared/asr-report-format.md)

### FunASR 特有说明

报告中的 `总体成功率` 对应脚本输出的 `norm_exact_match_rate`（归一化后完全匹配的比例）。

### Comparison 运行

配合 `--compare` 参数，读取 `verification-2-self/funasr/results/paraformer-report.md` 并按公共格式展示。

## Common Workflows

### "Run a quick smoke test"
```bash
python verification-2-self/funasr/scripts/test_funasr_batch.py --mode 2pass --limit 5
```

### "Test only principal role"
```bash
python verification-2-self/funasr/scripts/test_funasr_batch.py --mode 2pass --role principal
```

### "Full comparison with custom hotwords"
```bash
python verification-2-self/funasr/scripts/test_funasr_batch.py --compare --hotword 出勤率 --hotword 合格率
```

### "Test specific version across all modes"
```bash
python verification-2-self/funasr/scripts/test_funasr_batch.py --compare --version standard
```

### "Run and save detailed results"
```bash
python verification-2-self/funasr/scripts/test_funasr_batch.py --mode 2pass --output-json verification-2-self/funasr/results/paraformer-results.json --output-csv verification-2-self/funasr/results/paraformer-results.csv --output-md verification-2-self/funasr/results/paraformer-single-report.md
```

## Notes

- The script sends audio in 15360-byte chunks over WebSocket
- Audio is automatically resampled to 16kHz if needed (only 16-bit mono WAV supported)
- Hotword weights are auto-calculated: `min(20 + len(word) * 25, 300)`
- Text normalization strips all CJK/Latin punctuation before comparison
- Comparison results are saved to `verification-2-self/funasr/results/`
