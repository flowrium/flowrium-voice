# Moonshine 端侧 ASR

Moonshine 在这里按 `sherpa-onnx` 的 Phase 0 规格接入：先统一开发机安装、模型下载、单条验证、批量 CER/RTF，再记录 Apple 侧参考基准。

## Quick Start

```bash
bash verification-3-edge/moonshine/setup/install_moonshine.sh
bash verification-3-edge/moonshine/setup/download_models.sh
bash verification-3-edge/moonshine/setup/verify_setup.sh
python3 verification-3-edge/moonshine/scripts/test_moonshine_batch.py --model mandarin
```

## 当前模型

- `mandarin`
- `english`

默认输出文件：

- `results/moonshine-<model>-no-hotword-results.json`
- `results/moonshine-<model>-no-hotword-results.csv`
- `results/moonshine-<model>-no-hotword-report.md`
