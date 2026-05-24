## Why

端侧验证 Phase 0：在开发机上搭建 Sherpa-ONNX 环境，对比 Paraformer Int8 与 SenseVoice Int8 量化模型的转写准确率，复用验证二已有测试音频，确定端侧主力模型。只有先选定模型，后续各平台（Android/Apple/C#/鸿蒙）的集成验证才有意义。

## What Changes

- 新增 Sherpa-ONNX macOS 安装与环境搭建脚本（`verification-3-edge/sherpa-onnx/*/setup/`）
- 新增量化模型下载与管理脚本，支持 Paraformer Int8 和 SenseVoice Int8
- 新增 Sherpa-ONNX 批量测试脚本，复用 `audio/` 目录下的 manifest 和参考文本，输出 CER、RTF 等指标
- 新增测试结果报告，包含与验证二完整模型的 CER 对比
- 新增模型选型结论文档

## Capabilities

### New Capabilities
- `sherpa-onnx-setup`: Sherpa-ONNX 安装与量化模型下载管理，覆盖 macOS 开发环境
- `sherpa-onnx-batch-test`: Sherpa-ONNX 批量测试脚本，复用音频 manifest 输出 CER/RTF，支持 Paraformer Int8 和 SenseVoice Int8 两个模型
- `sherpa-onnx-model-selection`: 量化模型选型结论，对比两个模型的准确率、RTF、内存占用，给出端侧主力模型推荐

### Modified Capabilities

（无）

## Impact

- 新增 `verification-3-edge/sherpa-onnx/` 下的 setup、scripts、results 文件
- 依赖验证二已有的音频数据集和参考文本
- 依赖 Sherpa-ONNX pip 包和 HuggingFace 上的量化模型文件
- 无线上 API 变更，无破坏性改动
