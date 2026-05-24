# Sherpa-ONNX 端侧 ASR

## 为什么准确率不按平台分？

ONNX Runtime 是确定性推理引擎——同一个 `.onnx` 模型文件喂同样的音频数据，无论跑在 x86 还是 ARM、macOS 还是 Android，输出文本完全一致。因此 **CER（字符错误率）是模型属性，不是平台属性**。

在 macOS 开发机上用批量脚本跑出的 CER，就是所有平台的 CER，无需在每个端上重复测试准确率。

真正因平台而变的是性能指标：RTF（推理实时率）、内存占用、首字延迟。这些取决于 CPU 算力、内存大小、运行时实现，必须分平台实测。

## 目录结构

```
sherpa-onnx/
├── models/                # 量化模型（跨平台共用）
│   ├── paraformer-zh-int8/
│   ├── sense-voice-zh-int8/
│   └── zipformer-transducer-zh-int8/
│
├── results/               # 准确率结果（跨平台通用）
├── scripts/               # 批量测试脚本（跨平台通用）
├── setup/                 # macOS 开发环境搭建
│
├── benchmarks/            # 性能基准（按平台分）
│   ├── android/           #   RTF / 内存 / 首字延迟
│   ├── apple/
│   ├── csharp/
│   └── harmonyos/
│
└── integrations/          # 平台集成（Demo / 构建）
    ├── android/
    │   ├── demo/
    │   └── setup/
    ├── apple/
    │   ├── demo/
    │   └── setup/
    ├── csharp/
    │   ├── demo/
    │   └── setup/
    └── harmonyos/
        ├── demo/
        └── setup/
```

### 三个区域的划分理由

| 区域 | 内容 | 理由 |
|------|------|------|
| `models/` `results/` `scripts/` `setup/` | 模型、CER 结果、测试脚本、开发环境 | 准确率由模型决定，跨平台通用，放在顶层 |
| `benchmarks/` | RTF、内存、延迟等性能数据 | 性能因平台硬件不同而异，必须按平台实测和记录 |
| `integrations/` | 平台集成 Demo、构建配置 | 每个平台的集成方式完全不同（JNI/Swift/NuGet/NAPI），独立维护 |

## 已完成

- [x] Phase 0: 模型选型（macOS）— 见 [results/model-selection-report.md](results/model-selection-report.md)

## 待验证

- [ ] 流式推理：当前只测了离线批量，端侧实际需要边说边出字
- [ ] 热词支持：Paraformer/SenseVoice Int8 不支持；已补充 transducer 模型接入，待批量验证热词效果
- [ ] 各平台性能基准（benchmarks/）
- [ ] 各平台集成验证（integrations/）
