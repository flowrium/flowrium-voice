# whisper.cpp 端侧 ASR

`whisper.cpp` 在这一轮里按 `sherpa-onnx` 的目录规格接入，目标是先在 macOS 开发机上统一跑出模型级 CER/RTF，再补 Apple 侧基准记录。

## 目录

```text
whisper.cpp/
├── models/                # ggml / gguf 模型
├── results/               # CER / RTF 结果
├── scripts/               # 批量测试脚本
├── setup/                 # 安装 / 下载 / 验证
├── benchmarks/
│   └── apple/             # macOS 基准
└── integrations/
    └── apple/             # Apple 集成说明占位
```

## Quick Start

```bash
bash verification-3-edge/whisper.cpp/setup/install_whisper_cpp.sh
bash verification-3-edge/whisper.cpp/setup/download_models.sh
bash verification-3-edge/whisper.cpp/setup/verify_setup.sh
python3 verification-3-edge/whisper.cpp/scripts/test_whisper_cpp_batch.py --model base
```

## 当前模型

- `base`
- `small`
- `large-v3-turbo`

默认输出文件：

- `results/whisper-cpp-<model>-no-hotword-results.json`
- `results/whisper-cpp-<model>-no-hotword-results.csv`
- `results/whisper-cpp-<model>-no-hotword-report.md`
