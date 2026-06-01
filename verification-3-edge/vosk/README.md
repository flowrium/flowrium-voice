# Vosk 端侧 ASR

Vosk is an offline speech recognition toolkit based on Kaldi. Unlike whisper.cpp, Vosk models are self-contained and auto-downloaded via the Python API — no separate vendor repo or build step needed.

## 目录

```
vosk/
├── models/                # model metadata
├── results/               # CER / RTF results
├── scripts/               # batch test script
├── setup/                 # install / download / verify
├── benchmarks/
│   └── apple/             # macOS benchmarks
└── integrations/
    └── apple/             # Apple integration placeholder
```

## Quick Start

```bash
bash verification-3-edge/vosk/setup/install_vosk.sh
bash verification-3-edge/vosk/setup/download_models.sh
bash verification-3-edge/vosk/setup/verify_setup.sh
python3 verification-3-edge/vosk/scripts/test_vosk_batch.py --model small
```

## 当前模型

- `small` (vosk-model-small-cn-0.22, ~42MB)
- `big` (vosk-model-cn-0.22, ~1.3GB)

默认输出文件：

- `results/vosk-<model>-no-hotword-results.json`
- `results/vosk-<model>-no-hotword-results.csv`
- `results/vosk-<model>-no-hotword-report.md`

## Notes

- 不支持热词：Vosk 的 SetGrammar 是词汇表约束，不是热词偏置加分
- 纯 Python API，无需 CLI 二进制、无需 vendor 仓库、无需 cmake/make 编译
- 模型通过 `download_models.sh`（curl 下载 zip 解压）安装到 `models/` 目录，测试脚本通过 `vosk.Model(model_path=...)` 本地加载
