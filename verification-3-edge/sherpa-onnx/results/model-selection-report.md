# Sherpa-ONNX 端侧模型选型报告

## 测试环境

- **平台**: macOS x86_64 (Intel i7-9750H)
- **注意**: RTF 和内存数据仅为 macOS 参考，ARM 端侧实际数据需真机验证
- **测试数据**: 720 条音频 (standard 240 + humanized 240 + myvoice 240)

## 量化模型对比

| 指标 | Paraformer Int8 | SenseVoice Int8 |
| --- | --- | --- |
| 模型大小 | 227MB | 226MB |
| **CER (总体)** | **2.24%** | **1.97%** |
| 成功率 | 83.61% | 83.75% |
| 平均 RTF | 0.0557 | 0.0701 |
| P95 RTF | 0.0710 | 0.0986 |
| 热词支持 | 不支持 | 不支持 |

## 分版本 CER

| Version | Paraformer Int8 | SenseVoice Int8 |
| --- | --- | --- |
| standard | 1.18% | 1.10% |
| humanized | 1.14% | 1.10% |
| myvoice | 4.41% | 3.71% |

## 分角色 CER

| Role | Paraformer Int8 | SenseVoice Int8 |
| --- | --- | --- |
| principal | 1.92% | 2.50% |
| director | 2.67% | 2.15% |
| teacher | 2.23% | 1.62% |
| staff | 2.15% | 1.51% |

## 与验证二完整模型对比

| 模型 | CER | 量化损失 | 备注 |
| --- | --- | --- | --- |
| 验证二 SenseVoice (完整) | 3.71% | — | 基线 (仅 standard/humanized 对比) |
| 端侧 SenseVoice Int8 | 1.10% | -2.61% | 量化后反而更好（模型版本差异） |
| 验证二 WeNet (完整) | 14.80% | — | 基线 |
| 端侧 Paraformer Int8 | 1.18% | — | 与验证二 FunASR Paraformer 不同模型版本 |

> 注：端侧量化模型与验证二完整模型来自不同版本（Sherpa-ONNX 用的是 2025-10-07 版 Paraformer 和 2025-09-09 版 SenseVoice），CER 差异主要来自模型版本而非量化损失。量化损失需同版本对比才能准确量化。

## 热词能力

| 模型 | 热词支持 | 说明 |
| --- | --- | --- |
| Paraformer Int8 | 不支持 | Sherpa-ONNX 仅 transducer 模型支持热词，Paraformer 不支持 |
| SenseVoice Int8 | 不支持 | SenseVoice 架构本身不支持热词 |

这是端侧方案的重大限制。验证二中 FunASR Paraformer 通过 WebSocket 支持热词，效果提升明显。端侧 Sherpa-ONNX 目前无法复现此能力。

## 通过/失败判定

| 指标 | 通过标准 | Paraformer Int8 | SenseVoice Int8 |
| --- | --- | --- | --- |
| RTF | < 1.0 | 0.0557 ✅ | 0.0701 ✅ |
| CER | < 15% | 2.24% ✅ | 1.97% ✅ |
| 内存 | < 1.5GB | ~500MB ✅ | ~500MB ✅ |
| 热词 | 期望可用 | 不支持 ⚠️ | 不支持 ⚠️ |

两个模型均通过基本性能和准确率标准，但热词缺失是重要短板。

## 推荐

**端侧主力模型：Paraformer Int8**

理由：
1. **RTF 更低** (0.0557 vs 0.0710)，推理更快，在 ARM 端侧性能余量更大
2. **CER 差距极小** (2.24% vs 1.97%)，在实际使用中差异可忽略
3. **模型生态更成熟**：Sherpa-ONNX 的 Paraformer 支持更完善，流式版本也存在（后续可探索）
4. **未来热词可能性**：虽然当前 Int8 量化版不支持热词，但 Sherpa-ONNX 的 transducer 架构模型支持热词，后续可评估切换

**备选：SenseVoice Int8**
- 如果后续需要多语言（中英日韩粤）支持，SenseVoice 是更好选择
- myvoice 数据集上 CER 更低 (3.71% vs 4.41%)，对真实语音更鲁棒

## 遗留问题

1. **热词缺失如何弥补？** 端侧无热词，学校专有名词（出勤率、教务处等）的识别准确率可能受影响，需要在后续端集成中探索后处理纠错或 FST 热词方案
2. **ARM 真机性能未验证**：RTF 数据仅 macOS 参考，ARM 大屏上 RTF 可能增大 3-5 倍
3. **流式推理未验证**：Phase 0 只测了离线批量，端侧实际需要流式实时转写
4. **Int4 量化未探索**：如果 ARM 端侧内存更紧张，可进一步量化到 Int4
