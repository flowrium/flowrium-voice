## Context

验证二（自部署开源模型）需要先搭建可交互的验证环境。当前项目无本地 ASR 服务和测试工具。目标是在 Mac 上通过 Docker 跑 FunASR，并用纯前端页面实时验证转写效果。

约束：Mac 环境（Apple Silicon / Intel 均需支持）、CPU-only（无 GPU）、纯前端 Demo（无需后端服务器）。

## Goals / Non-Goals

**Goals:**

- FunASR Docker 容器一键启动，提供 WebSocket 流式和离线转写服务
- 纯前端 Demo 页面，对着麦克风说话即可实时看到转写结果
- 支持音频文件上传做可重复对比测试
- 支持热词管理和 2pass/online/offline 模式切换
- 结果可导出，为 Phase 2-4 测试提供记录基础

**Non-Goals:**

- 不做生产级部署优化（这是验证环境）
- 不做 SenseVoice 部署（Phase 3 内容）
- 不做后端服务（Demo 是纯前端静态文件）
- 不做自动化测试脚本（人工说话验证）
- 不做模型训练或微调

## Decisions

### 1. FunASR Docker CPU 镜像

**选择**: `funasr-runtime-sdk-online-cpu-0.1.12`

**理由**: 官方维护的 CPU-only 镜像，开箱即用，内含 Paraformer 模型 + 2pass 机制。Mac Docker 无 GPU，必须用 CPU 版本。

**替代方案**:
- GPU 镜像：Mac 不支持 NVIDIA Docker runtime
- 从源码构建：耗时且无额外收益，验证阶段无需自定义

### 2. 纯前端 Demo（无后端）

**选择**: 单个 HTML 文件 + 原生 JavaScript，浏览器直接通过 WebSocket 连 FunASR

**理由**: 验证阶段最小化开发量。FunASR WebSocket 协议可直接被浏览器使用，无需中间层。部署即打开文件。

**替代方案**:
- React/Vue SPA：引入构建工具链，对验证 Demo 过度
- Node.js 后端代理：增加一层无必要的复杂性

### 3. 音频输入双模式：实时录音 + 文件上传

**选择**: 同时支持 MediaRecorder API 实时采集和 `<input type="file">` 上传

**理由**: 实时录音用于主观体验验证，文件上传用于可重复对比测试（Phase 2-4 用同一段音频测不同模型/热词配置）。

### 4. 热词通过 WebSocket 消息传递

**选择**: 在建立 WebSocket 连接后，通过 FunASR 协议的 `hotwords` 字段发送热词

**理由**: FunASR 原生支持运行时热词，无需重启服务。Demo 层只需在发送音频前先发热词配置消息。

## Risks / Trade-offs

- [Mac Docker 性能] → CPU-only 镜像在 Mac 上延迟可能偏高（尤其 Apple Silicon 通过 Rosetta 模拟 x86）。缓解：记录延迟体感，若不可接受则改用 Linux 服务器。
- [FunASR 镜像版本锁定] → 0.1.12 可能不是最新。缓解：先用此版本验证，若遇问题再升级。
- [WebSocket 跨域] → 本地文件打开 HTML 可能遇 CORS 问题。缓解：用 `python -m http.server` 或直接在浏览器中允许。
- [音频格式兼容] → 浏览器 MediaRecorder 输出格式因浏览器而异（Chrome WebM, Safari MP4）。缓解：在 JS 中做 PCM 转换后再发送。
