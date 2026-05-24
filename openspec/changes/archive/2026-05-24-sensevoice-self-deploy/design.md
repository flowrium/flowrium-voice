## Context

验证二（自部署开源模型）已通过 Phase 1 完成了 FunASR+Paraformer 的环境搭建和初步测试。当前 verification-2-self/ 目录结构是扁平的（demo/、docker/、results/ 平铺），不支持多引擎并行管理。Phase 3 需要部署 SenseVoice 并测试，而 SenseVoice 的部署方式（HTTP REST API）与 Paraformer（WebSocket 流式）完全不同，需要独立的 Demo 和测试脚本。

当前状态：
- FunASR Docker 运行在 ws://localhost:10095（2pass 流式）和 ws://localhost:10096（离线）
- yiminger/sensevoice 镜像已拉取，提供 HTTP POST /extract_text，端口 8000
- SenseVoice 是纯离线模型：不支持流式、不支持热词，但支持多语言和情感/事件检测
- 现有批量测试脚本 test_funasr_batch.py 使用 WebSocket 协议，无法直接用于 SenseVoice

## Goals / Non-Goals

**Goals:**
- 将 verification-2-self/ 重组为 funasr/ 和 sensevoice/ 两个引擎子目录
- 部署 SenseVoice Docker 服务（yiminger/sensevoice 镜像）
- 新建 SenseVoice 转写验证 Demo（文件上传 + HTTP API）
- 新建 SenseVoice 批量测试脚本，输出格式与 FunASR 对齐
- 重命名 funasr-test skill 为 self-funasr-test，新建 self-sensevoice-test
- 产出两引擎对比结论

**Non-Goals:**
- 不尝试将 SenseVoice 集成到 FunASR 2pass 框架中（留作后续探索）
- 不为 SenseVoice 添加流式或热词支持（模型本身不支持）
- 不修改现有 FunASR Demo 的功能
- 不涉及验证三（云API方向）的内容

## Decisions

### D1: 使用 yiminger/sensevoice 镜像而非自行构建

**选择**: 直接使用 yiminger/sensevoice:latest Docker 镜像

**理由**: 该镜像封装了 funasr_onnx + FastAPI + ONNX 量化版 SenseVoiceSmall，开箱即用（docker run 即可），省去自行安装依赖和编写 API 层的工作。社区维护，3 stars，功能稳定。

**备选**:
- 自行构建 Python 推理服务：灵活但开发量大
- FunASR Docker 内加载 SenseVoice 模型：不确定兼容性，风险高

### D2: Demo 采用文件上传模式而非实时录音

**选择**: SenseVoice Demo 只支持文件上传（wav/mp3/m4a），不支持实时录音

**理由**: SenseVoice 是纯离线模型，无流式推理能力。文件上传是最自然的交互方式，也便于用同一批音频文件做 Paraformer vs SenseVoice 的精确对比。

### D3: SenseVoice Demo 与 FunASR Demo 风格统一但功能独立

**选择**: 两个 Demo 各自独立（不同 HTML 文件），共享视觉风格但不共享代码

**理由**: 两个引擎的协议（WebSocket vs HTTP）、交互模式（实时 vs 离线）、功能（热词 vs 语言选择）差异太大，强行合并到一个 Demo 会增加复杂度。独立维护更清晰。

### D4: 批量测试输出格式对齐

**选择**: SenseVoice 批量测试脚本输出与 FunASR 相同的 JSON/CSV 格式（包含 id, expected, actual, cer, category 等字段）

**理由**: 便于最终 Phase 4 做自动化对比分析，不需要手动对齐两套不同格式的结果。

### D5: Skill 命名加 self- 前缀

**选择**: funasr-test → self-funasr-test，新建 self-sensevoice-test

**理由**: 区分自部署验证（self-）和云API验证（cloud-）方向，未来云API验证会有 cloud-aliyun-test、cloud-volcengine-test 等。

### D6: 测试脚本随引擎目录存放

**选择**: 每个引擎目录下带自己的 scripts/ 子目录

**理由**: 两个引擎的协议和依赖完全不同，放在一起会造成混乱。各自独立更便于维护和复用。

## Risks / Trade-offs

- **[SenseVoice 无热词]** → 测试对比时热词维度 SenseVoice 为空，只能比离线准确率 → 在报告中明确标注此维度不适用
- **[yiminger/sensevoice 镜像维护风险]** → 社区镜像可能停止更新 → 记录镜像 SHA，必要时可自行构建
- **[目录搬迁可能破坏现有工作流]** → 已有的 FunASR Docker 容器和测试脚本路径会变 → 搬迁后立即验证所有路径引用
- **[SenseVoice ONNX 量化版精度]** → 量化可能影响转写准确率 → 测试时记录此变量，如需要可测试非量化版
