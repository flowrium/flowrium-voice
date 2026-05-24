## Why

验证二（自部署开源模型）已完成 Phase 1 环境搭建和 Phase 2 Paraformer 测试，现在需要推进 Phase 3：SenseVoice 部署与测试。当前 verification-2-self/ 目录结构未按引擎分组，且只支持 FunASR（WebSocket 协议），需要为 SenseVoice 建立独立的验证环境（HTTP API 协议），最终产出两引擎的对比结论。

## What Changes

- **目录重组**：将 verification-2-self/ 下的 demo/、docker/、results/ 按 funasr/ 和 sensevoice/ 引擎分组，各引擎独立管理自己的 Demo、Docker 配置、测试脚本和结果
- **SenseVoice Docker 部署**：使用 yiminger/sensevoice 镜像（基于 funasr_onnx + FastAPI，ONNX 量化版 SenseVoiceSmall），提供 HTTP API（POST /extract_text，端口 8000）
- **SenseVoice 转写 Demo**：新建纯前端页面，支持文件上传、语言选择（auto/zh/en/ja/ko/yue）、label_result 展示（语言标识+情感标签）、批量上传、结果导出
- **SenseVoice 批量测试脚本**：新建 HTTP POST 协议的批量测试脚本，复用现有 audio/ 目录的 manifest，输出格式与 FunASR 测试对齐
- **Skill 重命名+新建**：funasr-test → self-funasr-test（加 self- 前缀），新建 self-sensevoice-test
- **根 README 更新**：改为整体概览 + 两引擎链接，各引擎细节下沉到各自目录

## Capabilities

### New Capabilities
- `sensevoice-deploy`: SenseVoice Docker 部署（yiminger/sensevoice 镜像），提供离线转写 HTTP API 服务
- `sensevoice-demo`: 纯前端 SenseVoice 转写验证 Demo，支持文件上传、语言选择、情感标签展示、批量上传、结果导出
- `sensevoice-batch-test`: SenseVoice HTTP 批量测试脚本，复用 audio manifest，输出对齐 FunASR 格式便于对比

### Modified Capabilities
- `batch-test-comparison`: Skill 重命名为 self-funasr-test，路径从 verification-2-self/results/ 调整为 verification-2-self/funasr/results/；manifest 路径和输出路径随目录重组更新

## Impact

- verification-2-self/ 目录结构变更，现有文件需要搬迁（demo/ → funasr/demo/，results/ → funasr/results/）
- 新增 yiminger/sensevoice Docker 镜像（约 1-2GB），端口 8000
- 新增 self-sensevoice-test skill（.claude/skills/self-sensevoice-test/）
- self-funasr-test skill 内路径引用需更新（结果目录、脚本位置）
- 根 scripts/test_funasr_batch.py 迁移到 verification-2-self/funasr/scripts/
- SenseVoice 为纯离线模型，不支持流式、热词，测试方式与 Paraformer 有本质区别
