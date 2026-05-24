## Context

端侧验证 Phase 0，目标是在 macOS 开发机上验证 Sherpa-ONNX + 量化模型的可行性。

当前状态：
- 验证二已完成 FunASR/SenseVoice/WeNet/Qwen3-ASR 的自部署验证，有完整的测试音频（3 个 manifest：standard/humanized/myvoice）和 CER 计算体系
- 开发机为 macOS x86_64 (Intel i7)，Sherpa-ONNX 未安装
- `verification-3-edge/sherpa-onnx/` 目录结构已建好，按端分类（android/apple/csharp/harmonyos），但无内容
- Phase 0 在开发机上跑，不涉及任何端设备

约束：
- Sherpa-ONNX 的 Python API 是最快的验证路径，无需编译 C++ 库
- 量化模型从 HuggingFace sherpa-onnx 组织下载
- 测试音频复用 `audio/standard/manifest.csv`、`audio/humanized/manifest.csv`、`audio/myvoice/manifest.csv`
- CER 计算逻辑复用验证二已有的模式（去除标点后对比）

## Goals / Non-Goals

**Goals:**
- 搭建 Sherpa-ONNX Python 环境，确认在 macOS 上可正常推理
- 跑通 Paraformer Int8 和 SenseVoice Int8 两个量化模型的批量测试
- 得到 CER、RTF、内存占用的量化数据
- 与验证二的完整模型 CER 对比，评估量化损失
- 给出端侧主力模型推荐

**Non-Goals:**
- 不做各端（Android/Apple/C#/鸿蒙）的集成
- 不做流式推理验证（Phase 0 只测离线批量）
- 不做真机性能测试（RTF/内存数据仅作参考）
- 不做 Web 离线验证

## Decisions

### 1. 用 Sherpa-ONNX Python API 而非 C++ API

Sherpa-ONNX 提供 `sherpa-onnx` pip 包，封装了 C++ 核心，Python 调用即可完成离线推理。Phase 0 只需要验证模型能不能跑、CER 如何，Python 足够。

**备选**：直接编译 C++ 库 → 更接近各端最终集成方式，但 Phase 0 阶段增加复杂度，收益不大。

### 2. 测试脚本结构与验证二保持一致

复用 manifest CSV 格式、CER 计算逻辑、结果输出格式（JSON + CSV + report.md），方便直接对比。

### 3. 量化模型选择

| 模型 | 模型 ID (HuggingFace) | 量化 | 大小 |
|------|----------------------|------|------|
| Paraformer | sherpa-onnx/paraformer-zh-quantized | Int8 | ~200MB |
| SenseVoice | sherpa-onnx/sensevoice-zh-quantized | Int8 | ~230MB |

Int8 是 Sherpa-ONNX 官方提供的量化版本，Int4 需自行量化或社区提供，Phase 0 先用官方 Int8。

### 4. 热词验证

Sherpa-ONNX 的 Paraformer 模型支持热词（通过 `HotwordsFile` 参数），SenseVoice 不支持。测试时对 Paraformer 加热词测试，与无热词对比。

## Risks / Trade-offs

- [Sherpa-ONNX Python 包在 macOS x86_64 上可能没有预编译 wheel] → 用 `pip install sherpa-onnx` 测试，如果失败则考虑从源码编译或用 Docker
- [量化模型 CER 可能显著高于完整模型] → 如果 CER > 15%，记录差距并评估是否可接受
- [开发机 RTF 数据不能代表 ARM 端侧] → 在报告中明确标注"仅 macOS 参考，真机数据需后续验证"
- [SenseVoice 量化模型可能不可用或效果差] → 记录实际情况，可能排除
