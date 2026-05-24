## Why

验证二当前已经覆盖 FunASR、SenseVoice 和 WeNet，但还缺少 `qwenllm/qwen3-asr` 这条新路线的验证。为了让自部署 ASR 选型结论更完整，并且保持 `verification-2-self` 下各引擎验证方式一致，现在需要把 Qwen3-ASR 纳入同样的 Docker、Demo、批测和结果对比体系。

## What Changes

- 新增 `verification-2-self/qwen3-asr/` 目录结构，包含 `docker/`、`demo/`、`scripts/`、`results/`
- 新增 Qwen3-ASR Docker 启停脚本，使用 `qwenllm/qwen3-asr` 镜像并提供本地可验证的服务入口
- 新增 Qwen3-ASR 批量测试脚本，复用现有 manifest、CER 计算、过滤参数和输出结构
- 新增 Qwen3-ASR 浏览器验证 Demo，交互形态与现有自部署引擎保持一致
- 更新 `verification-2-self/README.md`，将引擎表和运行说明扩展为四引擎
- 更新 `docs/verification-2-self-deploy.md`，加入 Qwen3-ASR 的验证阶段、对比维度和结论表

## Capabilities

### New Capabilities
- `qwen3-asr-deploy`: Qwen3-ASR Docker 部署与本地启动脚本，基于 `qwenllm/qwen3-asr` 镜像提供可验证服务
- `qwen3-asr-demo`: Qwen3-ASR 浏览器验证 Demo，用于手工上传音频或交互式验证转写效果
- `qwen3-asr-batch-test`: Qwen3-ASR 批量测试脚本，复用 audio manifests 并输出与现有引擎可直接对比的结果

### Modified Capabilities
- `batch-test-comparison`: 将现有三引擎对比扩展为包含 Qwen3-ASR 的四引擎对比，并补充 README / 执行文档中的对比说明

## Impact

- 新增 `verification-2-self/qwen3-asr/` 目录及其脚本、Demo、结果文件
- 修改 `verification-2-self/README.md` 和 `docs/verification-2-self-deploy.md`
- 新增对 `qwenllm/qwen3-asr` Docker 镜像的依赖，以及与其实际暴露协议匹配的本地验证适配逻辑
- 无线上 API 变更，无破坏性改动
