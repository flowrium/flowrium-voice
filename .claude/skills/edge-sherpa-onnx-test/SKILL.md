---
name: edge-sherpa-onnx-test
description: Run Sherpa-ONNX batch ASR tests locally (no external service needed) against audio manifests. Supports paraformer, sensevoice, and transducer models with CER metrics, RTF, and hotword analysis (transducer only). Accepts args like "10" (limit), "--model transducer --limit 5", "--role principal", etc.
metadata:
  author: flowrium
  version: "1.0"
---

Run Sherpa-ONNX batch ASR tests against the project's audio manifests using local ONNX quantized models. This skill wraps `verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py` and provides structured result formatting. Unlike SenseVoice/WeNet skills, **no external service is needed** — inference runs locally.

## Arguments

The skill accepts arguments passed after `/edge-sherpa-onnx-test`. Parse them as follows:

- **A bare number** → treated as `--limit` (test only the first N rows). Example: `/edge-sherpa-onnx-test 10`
- **Any other text** → passed through as-is to the script. Example: `/edge-sherpa-onnx-test --model transducer --role principal --limit 5`
- **No arguments** → run with defaults (all rows, paraformer model)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/edge-sherpa-onnx-test` | (no args) | All rows, paraformer |
| `/edge-sherpa-onnx-test 5` | `--limit 5` | First 5 rows, paraformer |
| `/edge-sherpa-onnx-test --model transducer` | `--model transducer` | All rows, transducer |
| `/edge-sherpa-onnx-test 10 --model sensevoice` | `--model sensevoice --limit 10` | First 10 rows, sensevoice |
| `/edge-sherpa-onnx-test --role principal` | `--role principal` | All principal rows, paraformer |
| `/edge-sherpa-onnx-test --model transducer --hotword 出勤率` | `--model transducer --hotword 出勤率` | Transducer with hotword |
| `/edge-sherpa-onnx-test --use-hotwords-file` | `--use-hotwords-file` | Load hotwords from configured file |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. All other arguments pass through unchanged.

## Prerequisites

- ONNX model files downloaded under `verification-3-edge/sherpa-onnx/models/` (run `download_models.sh` first)
- Python dependencies: `sherpa-onnx`, `numpy`
- Audio manifests exist under `audio/` directories
- **No external service required** — runs fully offline

## Commands

### Quick test

```bash
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py [--model paraformer|sensevoice|transducer] [--limit N] [--version V] [--role R] [--hotword WORD]
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--model` | Model to use: `paraformer`, `sensevoice`, `transducer` | `paraformer` |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--hotword` | Hotword (repeatable, transducer only) | none |
| `--use-hotwords-file` | Load hotwords from `config/hotwords.txt` | off |
| `--decoding-method` | Transducer decoding: `greedy_search` or `modified_beam_search` | auto |
| `--max-active-paths` | Transducer max active paths | 4 |
| `--hotwords-score` | Transducer hotword bias score | 1.5 |
| `--limit` | Only test first N rows | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** — apply the rules from the Arguments section above (bare number → `--limit`)
2. **Check prerequisites** — verify model files exist (listed in `MODEL_CONFIGS`), and sherpa-onnx is importable
3. **Run the test command** with parsed args
4. **Format and present results** using the structure below

## Metrics & Report Format

指标说明和报告格式见公共文件：[_shared/asr-report-format.md](../_shared/asr-report-format.md)

### Sherpa-ONNX 特有说明

- **无需外部服务**：本地 ONNX 推理，不依赖 HTTP/WebSocket 服务
- 支持 3 种模型：
  - **paraformer** (默认)：离线识别，不支持热词
  - **sensevoice**：离线识别，支持语言检测和 ITN，不支持热词
  - **transducer**：流式识别，支持热词(`modified_beam_search`)
- 热词仅 transducer + `modified_beam_search` 组合支持
- 结果自动保存到 `verification-3-edge/sherpa-onnx/results/`
- 文件名格式：`sherpa-onnx-{model}-{hotword|no-hotword}-results.{json|csv}` 及 `-report.md`

## Common Workflows

### "Run a quick smoke test with paraformer"
```bash
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --limit 5
```

### "Test all models sequentially"
```bash
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model paraformer --limit 10
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model sensevoice --limit 10
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model transducer --limit 10
```

### "Test transducer with hotwords"
```bash
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model transducer --hotword 出勤率 --hotword 合格率
```

### "Test transducer with hotwords file"
```bash
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model transducer --use-hotwords-file
```

### "Test only principal role with sensevoice"
```bash
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --model sensevoice --role principal
```

### "Filter by specific version"
```bash
python verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py --version v1.0 --version v2.0
```

## Notes

- Sherpa-ONNX 运行纯本地推理，不需要任何外部服务，开箱即用（只要模型文件已下载）
- 三种模型的 recognizer 类型不同：paraformer 和 sensevoice 为 `OfflineRecognizer`，transducer 为 `OnlineRecognizer`
- 使用 Levenshtein 距离计算 CER
- 文本归一化去除所有中英文标点和空格后再比较
- 热词自动去重；非 transducer 模型使用热词会被忽略并给出警告
- Results are saved to `verification-3-edge/sherpa-onnx/results/`
