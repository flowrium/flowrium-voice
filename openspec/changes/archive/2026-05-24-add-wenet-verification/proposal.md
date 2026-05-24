## Why

当前验证二只覆盖了 FunASR (Paraformer) 和 SenseVoice 两个引擎。WeNet 是另一个专门为中文优化的开源 ASR 引擎，原生支持流式识别和热词，技术路线（U2 统一架构）与 Paraformer（非自回归）不同，性能特征可能有差异。缺少 WeNet 会导致选型结论缺少一个关键竞争方案的对比数据。

## What Changes

- 新增 `verification-2-self/wenet/` 目录结构（demo/docker/results/scripts），与现有 funasr/sensevoice 保持一致
- 新增 WeNet 批量测试脚本（WebSocket 协议），复用现有 manifest 和 CER 计算逻辑
- 新增 WeNet Docker 部署脚本
- 新增 WeNet 浏览器验证 Demo
- 更新 `verification-2-self/README.md` 引擎表，加入 WeNet
- 更新 `docs/verification-2-self-deploy.md`，在 SenseVoice 之后插入 WeNet Phase，更新对比表从双引擎扩展为三引擎

## Capabilities

### New Capabilities
- `wenet-batch-test`: WeNet 批量测试脚本，基于 WebSocket 协议对音频 manifest 执行转写，输出 CER 指标和对比报告
- `wenet-deploy`: WeNet Docker 部署脚本和配置
- `wenet-demo`: WeNet 浏览器验证 Demo

### Modified Capabilities
- `batch-test-comparison`: 三引擎对比报告，扩展为 FunASR / SenseVoice / WeNet 三方对比

## Impact

- 新增 `verification-2-self/wenet/` 目录及全部内容
- 修改 `verification-2-self/README.md`
- 修改 `docs/verification-2-self-deploy.md`（Phase 结构扩展、对比表增加列）
- 无 API 变更，无破坏性改动
