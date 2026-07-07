---
name: edge-whisper-cpp-test
description: Run whisper.cpp batch ASR tests locally (no external service needed) against audio manifests. Supports base, small, and large-v3-turbo models with CER metrics and RTF. Accepts args like "10" (limit), "--model large-v3-turbo --limit 5", "--role principal", etc.
metadata:
  author: flowrium
  version: "1.0"
---

Run whisper.cpp batch ASR tests against the project's audio manifests using the local `whisper-cli` binary. This skill wraps `verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py` and provides structured result formatting. **No external service is needed** -- inference runs locally via subprocess invocation of `whisper-cli`.

## Arguments

The skill accepts arguments passed after `/edge-whisper-cpp-test`. Parse them as follows:

- **A bare number** → treated as `--limit` (test only the first N rows). Example: `/edge-whisper-cpp-test 10`
- **Any other text** → passed through as-is to the script. Example: `/edge-whisper-cpp-test --model large-v3-turbo --role principal`
- **No arguments** → run with defaults (all rows, base model)

| User Input | Parsed Command | Meaning |
| --- | --- | --- |
| `/edge-whisper-cpp-test` | (no args) | All rows, base model |
| `/edge-whisper-cpp-test 5` | `--limit 5` | First 5 rows, base model |
| `/edge-whisper-cpp-test --model large-v3-turbo` | `--model large-v3-turbo` | All rows, large-v3-turbo |
| `/edge-whisper-cpp-test 10 --model small` | `--model small --limit 10` | First 10 rows, small model |
| `/edge-whisper-cpp-test --role principal` | `--role principal` | All principal rows, base model |

**Parsing rule**: If the first argument is a plain integer, prepend `--limit` before it. All other arguments pass through unchanged.

## Prerequisites

- `whisper-cli` binary built at `verification-3-edge/whisper.cpp/vendor/whisper.cpp/build/bin/whisper-cli`
- Model files downloaded to `verification-3-edge/whisper.cpp/models/`:
  - `ggml-base.bin` (~141MB)
  - `ggml-small.bin` (~465MB)
  - `ggml-large-v3-turbo-q5_0.bin` (~547MB)
- Audio manifests exist under `audio/` directories
- **No external service required** -- runs fully offline

## Commands

### Quick test

```bash
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py [--model base|small|large-v3-turbo] [--limit N] [--version V] [--role R] [--language zh] [--threads 4]
```

## Key CLI Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--model` | Model to use: `base`, `small`, `large-v3-turbo` | `base` |
| `--manifest` | Manifest CSV path (repeatable) | all 3 manifests |
| `--limit` | Only test first N rows | 0 (all) |
| `--version` | Filter by version (repeatable) | all |
| `--role` | Filter by role (repeatable) | all |
| `--language` | Language code for ASR | `zh` |
| `--threads` | Number of CPU threads | `4` |

## What This Skill Does

When the user invokes this skill, follow these steps:

1. **Parse arguments** -- apply the rules from the Arguments section above (bare number → `--limit`)
2. **Check prerequisites** -- verify `whisper-cli` binary exists and model file is present
3. **Run the test command** with parsed args
4. **Format and present results** using the structure below

## Metrics & Report Format

指标说明和报告格式见公共文件：[_shared/asr-report-format.md](../_shared/asr-report-format.md)

### whisper.cpp 特有说明

- **无需外部服务**：本地 `whisper-cli` 二进制，通过 subprocess 调用
- 支持 3 种模型：
  - **base** (默认)：ggml-base.bin，约 141MB，RTF 通常 < 1
  - **small**：ggml-small.bin，约 465MB，RTF 约 2
  - **large-v3-turbo**：ggml-large-v3-turbo-q5_0.bin，约 547MB（q5_0 量化），精度最高但 RTF 约 7
- **不支持热词**：whisper.cpp 没有热词偏置机制
- **默认语言 zh**：通过 `-l zh` 指定中文识别
- base 和 small 模型可能输出繁体中文，注意繁简差异对 CER 的影响
- 结果自动保存到 `verification-3-edge/whisper.cpp/results/`
- 文件名格式：`whisper-cpp-{model}-no-hotword-results.{json|csv}` 及 `-report.md`

## Common Workflows

### "Run a quick smoke test"
```bash
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --limit 5
```

### "Test with large-v3-turbo model"
```bash
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --model large-v3-turbo --limit 10
```

### "Test all models (full run)"
```bash
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --model base
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --model small
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --model large-v3-turbo
```

### "Test only principal role"
```bash
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --role principal
```

### "Filter by specific version"
```bash
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --version standard
```

## Notes

- whisper.cpp 运行纯本地推理，不需要任何外部服务
- 推理通过 subprocess 调用 `whisper-cli` 二进制，非 Python 绑定
- 模型从 HuggingFace 或 hf-mirror.com 下载，通过 `download_models.sh` 管理
- 使用 Levenshtein 距离计算 CER
- 文本归一化去除所有中英文标点和空格后再比较（注意：不包含繁→简转换）
- 当前机器（Intel Mac + AMD GPU）不支持 Metal GPU 加速，使用 BLAS CPU 后端
- `-ng`（no-gpu）和 `-nfa`（no-flash-attn）为默认启用的兼容性标志
- Results are saved to `verification-3-edge/whisper.cpp/results/`
