## Context

验证二（verification-2-self）目前验证了 FunASR (Paraformer) 和 SenseVoice 两个 ASR 引擎。两者均为阿里系模型，技术路线差异有限（Paraformer 非自回归 vs SenseVoice 自回归+多任务）。WeNet 是出门问问/西湖大学出品的开源 ASR 引擎，基于 U2 统一架构，原生支持流式/非流式一体化推理和热词（LM rescoring），且专为中文优化，是与 FunASR 直接竞争的独立技术路线。

现有目录结构约定：每个引擎有独立的 `demo/`、`docker/`、`results/`、`scripts/` 子目录。批量测试脚本读取相同的 manifest CSV，输出 CER 指标，支持 `--compare` 模式。

## Goals / Non-Goals

**Goals:**
- 新增 WeNet 引擎的完整验证环境（Docker 部署、批量测试脚本、浏览器 Demo）
- 批量测试脚本输出格式与 FunASR/SenseVoice 对齐，支持三方 CER 对比
- 更新验证文档，将双引擎对比扩展为三引擎对比

**Non-Goals:**
- 不实现 WeNet 与 FunASR 的实时流式结果交叉对比（仅离线批量对比）
- 不修改 FunASR 或 SenseVoice 的现有代码
- 不实现端侧部署（属于验证三的范畴）

## Decisions

### D1: WeNet Docker 镜像选用 wenet-e2e/wenet:latest 官方镜像

WeNet 官方提供 `wenet-e2e/wenet:latest` Docker 镜像，内置 Python 推理服务和 WebSocket 端点。

**备选方案**：
- 用 sherpa-onnx 加载 WeNet 模型 → 属于端侧方案，留给验证三
- 手动搭建推理服务 → 部署复杂度高，不符合验证二的快速验证目标

### D2: 批量测试脚本基于 WebSocket 协议

WeNet runtime 的 WebSocket 接口与 FunASR 类似但消息格式不同：
- 连接时发送 `{"signal": "start", "nbest": 1}` 起始信号
- 音频以二进制帧分片发送（每帧 960 samples / 16kHz = 60ms）
- 结束时发送 `{"signal": "end"}` 结束信号
- 返回 `{"status": "ok", "nbest": [{"sentence": "..."}]}` 格式

脚本复用 FunASR 脚本的 CER 计算、manifest 加载、结果汇总逻辑，仅替换 WebSocket 通信协议部分。

### D3: WeNet 默认使用 10097 端口

避免与 FunASR (10095/10096) 和 SenseVoice (8000) 冲突。

### D4: WeNet Demo 支持实时录音和文件上传

与 FunASR Demo 功能对齐，因为 WeNet 原生支持流式，Demo 应展示实时转写能力。

### D5: 三引擎对比报告采用独立的 Markdown 文件

在 `verification-2-self/results/` 下生成 `three-engine-comparison.md`，不修改 FunASR 或 SenseVoice 各自的报告。

## Risks / Trade-offs

- [WeNet Docker 镜像可能更新不及时] → 可降级为从源码构建，但增加部署步骤
- [WeNet 热词为 LM rescoring 方式，效果可能与 FunASR 的热词注入机制差异较大] → 测试时需明确区分热词实现方式，对比报告中注明
- [三引擎同时运行占用内存可能超过 8GB] → 验证时不需要同时运行，逐个启动测试即可
