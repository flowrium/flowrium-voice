# 验证二：自部署开源模型

## 目标

自部署 ASR 引擎，通过离线/实时语音交互验证在学校管理场景下的转写效果，对比 Paraformer、SenseVoice、WeNet 和 Qwen3-ASR。

## 详细计划

见 [docs/verification-2-self-deploy.md](../docs/verification-2-self-deploy.md)

## 引擎目录

| 引擎 | 协议 | 说明 |
| --- | --- | --- |
| [funasr/](funasr/) | WebSocket | Paraformer 实时/离线转写，支持流式和热词 |
| [sensevoice/](sensevoice/) | HTTP REST | SenseVoice 离线转写，支持多语言和情感/事件检测 |
| [wenet/](wenet/) | WebSocket | WeNet 流式/离线转写，支持热词 |
| [qwen3-asr/](qwen3-asr/) | OpenAI-compatible HTTP | Qwen3-ASR 离线转写，基于 `vllm serve` 暴露 `/v1/audio/transcriptions` |

各引擎目录下包含：
- `demo/` — 浏览器验证 Demo
- `docker/` — Docker 部署脚本（start.sh / stop.sh）
- `results/` — 测试结果（JSON/CSV/报告）
- `scripts/` — 批量测试脚本

## 运行 SenseVoice Demo

1. 启动 Docker 服务：`bash verification-2-self/sensevoice/docker/start.sh`
2. 启动本地 Demo 代理：`bash verification-2-self/sensevoice/demo/start.sh`
3. 浏览器打开 `http://127.0.0.1:18080`

说明：
- Demo 代理会把 `/extract_text` 和 `/docs` 转发到 `http://127.0.0.1:8000`
- 这样浏览器和 Demo 同源，避免直接访问 Docker API 时的跨域问题

## 运行 WeNet Demo

1. 启动 Docker 服务：`bash verification-2-self/wenet/docker/start.sh`
2. 启动本地 Demo 代理：`bash verification-2-self/wenet/demo/start.sh`
3. 浏览器打开 `http://127.0.0.1:18081`

说明：
- Demo 页面默认连接本地代理 `ws://127.0.0.1:18082`
- 代理会把 WebSocket 转发到 `ws://127.0.0.1:10097`

## 运行 Qwen3-ASR Demo

1. 启动 Docker 服务：`bash verification-2-self/qwen3-asr/docker/start.sh`
2. 启动本地 Demo 代理：`bash verification-2-self/qwen3-asr/demo/start.sh`
3. 浏览器打开 `http://127.0.0.1:18083`

说明：
- Qwen3-ASR 使用 `qwenllm/qwen3-asr` 运行环境镜像，在容器内通过 `vllm serve` 暴露 OpenAI 兼容接口
- Demo 默认代理到 `http://127.0.0.1:8001/v1`
- 官方镜像是 CUDA 环境，通常需要 Linux + NVIDIA GPU；macOS 上大概率只能完成脚本和目录接入，不能直接跑通模型服务
