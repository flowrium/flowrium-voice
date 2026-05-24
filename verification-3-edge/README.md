# 验证三：端侧部署

## 目标

评估各端本地运行 ASR 的可行性，实现离线语音识别，无需联网。

## 候选技术

| 技术 | 说明 | 覆盖平台 |
|------|------|---------|
| Sherpa-ONNX | C++ ONNX 推理引擎，跨平台 | Android, Apple, C#, HarmonyOS |
| whisper.cpp | GGML/GGUF 本地推理，跨平台 | Apple, Android, Linux, Windows |
| Moonshine | 轻量端侧 ASR，偏实时交互 | Apple, Android, Linux |
| WeNet Runtime | Runtime / WebSocket 服务，适合作为原生集成前的参考链路 | Apple, Android, Linux |
| MindSpore Lite | 华为端侧推理框架，.ms 模型格式 | HarmonyOS |

## 目录结构

```
verification-3-edge/
├── sherpa-onnx/                    # 技术：Sherpa-ONNX
│   ├── models/                     # 量化模型（跨平台共用）
│   ├── results/                    # 准确率结果（跨平台通用，CER 是模型属性非平台属性）
│   ├── scripts/                    # 批量测试脚本（跨平台通用）
│   ├── setup/                      # macOS 开发环境搭建
│   ├── benchmarks/                 # 性能基准（按平台分：RTF / 内存 / 延迟）
│   │   ├── android/
│   │   ├── apple/
│   │   ├── csharp/
│   │   └── harmonyos/
│   └── integrations/               # 平台集成（Demo / 构建配置）
│       ├── android/                #   JNI / AAR
│       ├── apple/                  #   Swift / Core ML
│       ├── csharp/                 #   NuGet
│       └── harmonyos/              #   NAPI / ArkTS
├── whisper.cpp/                    # 技术：whisper.cpp
│   ├── models/
│   ├── results/
│   ├── scripts/
│   ├── setup/
│   ├── benchmarks/
│   │   └── apple/
│   └── integrations/
│       └── apple/
├── moonshine/                      # 技术：Moonshine
│   ├── models/
│   ├── results/
│   ├── scripts/
│   ├── setup/
│   ├── benchmarks/
│   │   └── apple/
│   └── integrations/
│       └── apple/
├── wenet-runtime/                  # 技术：WeNet Runtime
│   ├── models/
│   ├── results/
│   ├── scripts/
│   ├── setup/
│   ├── benchmarks/
│   │   └── apple/
│   └── integrations/
│       └── apple/
├── mindspore-lite/                 # 技术：MindSpore Lite (华为备选)
│   └── harmonyos/
│       └── ...
├── results/                        # 跨平台对比结果
├── scripts/                        # 跨平台对比脚本
└── common/                         # 批测共享工具
```

## 验证阶段

```
Phase 0: 模型选型 (开发机)
│  macOS 上用 Sherpa-ONNX 测试 Paraformer Int8 vs SenseVoice Int8
│  复用验证二测试音频，对比 CER
│  确定端侧主力模型
│
Phase 1: Android (含大屏)
│  模拟器验证集成流程与准确率
│  真机验证 RTF / 内存 / CER
│
Phase 2: Apple
│  模拟器验证流程
│  后续可考虑 Core ML 加速
│
Phase 3: C# 桌面端
│  NuGet 包集成验证
│
Phase 4: 华为纯血鸿蒙
│  方案一：Sherpa-ONNX 编译到鸿蒙 (高风险)
│  方案二：MindSpore Lite 模型转换 (备选)
│  可能结论：某阶段前华为只能联网
│
Web 离线：暂不验证
```

## 通过/失败判定

| 指标 | 通过标准 |
|------|---------|
| 推理实时率 (RTF) | < 1.0 (快于实时) |
| 准确率 | 安静环境 CER < 15% |
| 内存占用 | < 1.5GB |
| 华为可行性 | 能跑或明确给出替代方案 |

## 详细计划

见 [docs/verification-plan.md](../docs/verification-plan.md)
