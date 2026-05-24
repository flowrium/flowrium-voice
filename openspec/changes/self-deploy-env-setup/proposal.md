## Why

自部署 ASR 引擎验证需要可交互的实时转写环境。当前没有任何本地部署的语音识别服务或测试工具，无法实际体验 Paraformer/SenseVoice 的转写效果和热词能力。Phase 1 搭建完整验证环境，让后续模型对比测试（Phase 2-4）可以直接"说话看结果"。

## What Changes

- 启动 FunASR Docker 容器，提供实时流式（:10095）和离线（:10096）转写 WebSocket 服务
- 开发纯前端转写验证 Demo 页面，支持实时录音和音频文件上传两种输入方式
- Demo 支持 2pass/online/offline 模式切换、热词管理（增删、预设学校场景热词）、结果导出
- 区分显示 partial（实时）和 final（修正后）转写结果

## Capabilities

### New Capabilities

- `funasr-docker-service`: FunASR Docker 容器部署与运行，提供 WebSocket 转写服务（流式 :10095 + 离线 :10096）
- `transcription-demo`: 纯前端转写验证 Demo，支持实时录音、文件上传、模式切换、热词管理、结果导出

### Modified Capabilities

## Impact

- 依赖 Docker Desktop（Mac/Linux）运行 FunASR 容器
- 新增前端静态页面（index.html + JS），无后端依赖
- WebSocket 连接本地 FunASR 服务（localhost:10095/10096）
- 后续 Phase 2-4 测试依赖此环境
