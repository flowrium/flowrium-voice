## Context

`verification-2-self` 目前已经为 FunASR、SenseVoice 和 WeNet 建立了统一的引擎目录约定：每个引擎都有独立的 `docker/`、`demo/`、`scripts/`、`results/` 子目录，并共享同一套 `audio/*/manifest.csv` 数据源、CER 统计口径和结果沉淀方式。用户希望把 `qwenllm/qwen3-asr` 也纳入同一体系，以便在相同场景下做横向验证。

与前三个引擎不同，当前唯一未确认的是 `qwenllm/qwen3-asr` 镜像实际暴露的服务协议、默认端口和请求格式。提案阶段不应假设其一定是 HTTP 或 WebSocket，但需要先把目录结构、适配层位置和文档更新方式定下来，保证后续实现可以在最小范围内落地。

## Goals / Non-Goals

**Goals:**
- 为 Qwen3-ASR 增加与现有引擎一致的验证目录结构和文档入口
- 保持批量测试的数据源、过滤参数、CER 统计和结果格式与现有引擎一致
- 将 `qwenllm/qwen3-asr` 的协议适配限制在单独的部署脚本、Demo 和批测脚本中，不影响现有三套实现
- 扩展 README 与验证文档，使四引擎的运行方式和对比结论有统一入口

**Non-Goals:**
- 不在本次提案中预先承诺 Qwen3-ASR 支持流式、热词或多语言等尚未验证的能力
- 不重构 FunASR、SenseVoice、WeNet 现有脚本为统一公共库
- 不在本次变更中引入新的评估指标体系，仍以现有 manifest + CER + 延迟口径为主
- 不处理端侧部署或云 API 方向的验证

## Decisions

### D1: 继续采用“每引擎一套适配器”的目录模式

Qwen3-ASR 将新增 `verification-2-self/qwen3-asr/`，内部仍按 `docker/`、`demo/`、`scripts/`、`results/` 划分。

**理由**：现有项目已经证明这种方式适合协议差异较大的引擎。Qwen3-ASR 是否为 HTTP、WebSocket 或兼容接口尚未确认，单独隔离最稳妥，不会把不确定性扩散到其他引擎目录。

**备选方案**：
- 复用现有某个引擎目录并做少量改造：会让协议适配逻辑混杂，后续维护不清晰
- 抽公共框架后让各引擎插件化：方向上可行，但超出本次“快速补齐第四套验证”的目标

### D2: 先做协议探测，再决定 Demo 和批测的传输层实现

实现阶段的第一步应是启动 `qwenllm/qwen3-asr` 容器，确认默认端口、健康检查方式、请求协议和返回格式；随后再选择 HTTP 适配路线、WebSocket 适配路线，或兼容 OpenAI 风格音频接口的路线。

**理由**：当前最主要的不确定性不是功能需求，而是容器接口。如果在设计阶段硬编码成某一种协议，后面很容易推翻规范或返工。

**备选方案**：
- 默认按 SenseVoice 的 HTTP 方案写死：若镜像实际是 WebSocket，会造成设计失真
- 默认按 FunASR/WeNet 的 WebSocket 方案写死：同样风险过高

### D3: 无论底层协议如何，批测脚本对外接口保持现有风格

Qwen3-ASR 的批量测试脚本应继续支持：
- 默认读取 `audio/standard`、`audio/humanized`、`audio/myvoice` manifests
- `--manifest`、`--limit`、`--version`、`--role`
- JSON / CSV / Markdown 结果输出到 `verification-2-self/qwen3-asr/results/`

协议相关参数只在必要时暴露，例如 `--api-url` 或 `--ws-url`，由实现阶段根据实际容器接口确定。

**理由**：用户要的是同一验证体系，而不是四套互不兼容的使用方式。对外 CLI 约定保持一致，最终比对和自动化运行才容易。

### D4: Demo 功能以“可手工验证转写”为最低保底，不预先承诺流式能力

Qwen3-ASR Demo 至少应支持用户手工提交音频并查看转写结果；若镜像支持流式协议，再追加实时录音和 partial/final 展示。

**理由**：用户明确要求体系与现有引擎一致，但“体系一致”不等于“能力完全一致”。像 SenseVoice 也没有流式输入，因此对 Qwen3-ASR 的最低契约应是“可验证”，扩展能力取决于容器本身。

### D5: 对比报告从“三引擎命名”泛化为“多引擎命名”

随着引擎数量继续增长，比较结果的输出和文档表述不应继续绑定“三引擎”字样。实现阶段应把总对比结果收敛到更通用的命名和文档章节，纳入 FunASR、SenseVoice、WeNet、Qwen3-ASR 四方对比。

**理由**：当前项目已经从两引擎演进到三引擎，再到四引擎，命名泛化可以避免每次新增引擎都重命名一轮概念。

## Risks / Trade-offs

- [Qwen3-ASR 镜像实际接口与预期差异较大] → 先做最小协议探测，再落具体适配；必要时在实现前补充设计结论
- [镜像只支持离线转写，不支持流式或热词] → Demo 和文档按“能力探测结果”降级，保持功能说明准确
- [四引擎结果字段不完全一致] → 维持核心对比字段一致，附加字段保留在各自结果中，不强行抹平
- [对比报告继续绑定某一引擎脚本生成] → 在实现时将总对比逻辑抽成更通用入口或独立报告生成步骤

## Migration Plan

1. 拉起 `qwenllm/qwen3-asr` 容器并确认协议、端口、探活方式
2. 按确认后的接口补齐 `qwen3-asr/docker`、`qwen3-asr/scripts`、`qwen3-asr/demo`
3. 更新 `verification-2-self/README.md` 和 `docs/verification-2-self-deploy.md`
4. 运行最小批测，生成结果并纳入总对比报告

本变更为增量扩展，无需回滚现有三引擎代码；若 Qwen3-ASR 集成受阻，可单独移除 `verification-2-self/qwen3-asr/` 和对应文档入口，不影响其他验证链路。

## Open Questions

- `qwenllm/qwen3-asr` 默认暴露的具体接口是什么：HTTP、WebSocket，还是兼容 OpenAI 的音频接口？
- 默认端口、健康检查路径、返回 JSON 结构分别是什么？
- 是否支持流式结果、热词、语言配置等高级能力，还是仅支持离线文件转写？
- 总对比报告最终继续由某个现有脚本生成，还是应该顺势抽出一个独立的多引擎汇总步骤？
