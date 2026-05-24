## 1. Protocol Discovery And Structure

- [ ] 1.1 启动 `qwenllm/qwen3-asr` 容器并确认默认端口、协议类型、探活方式和返回格式
- [x] 1.2 创建 `verification-2-self/qwen3-asr/` 目录结构（`docker/`、`demo/`、`scripts/`、`results/`）
- [x] 1.3 基于探测结果确定 Qwen3-ASR 采用 HTTP、WebSocket 或兼容接口的适配路线，并记录到实现说明中

## 2. Docker Deployment

- [x] 2.1 编写 `verification-2-self/qwen3-asr/docker/start.sh`，启动 `qwenllm/qwen3-asr` 容器并等待服务就绪
- [x] 2.2 编写 `verification-2-self/qwen3-asr/docker/stop.sh`，停止并移除 Qwen3-ASR 容器
- [ ] 2.3 验证启动脚本在“首次启动”和“服务已运行”两种情况下都能给出正确输出

## 3. Batch Test Script

- [x] 3.1 编写 `verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py` 基础框架，复用 manifest 加载、文本归一化、CER 计算和汇总逻辑
- [x] 3.2 实现面向 Qwen3-ASR 实际协议的请求适配层，并完成单文件转写流程
- [x] 3.3 实现 `--manifest`、`--limit`、`--version`、`--role` 等过滤参数
- [x] 3.4 实现 JSON、CSV、Markdown 输出，写入 `verification-2-self/qwen3-asr/results/`
- [x] 3.5 运行最小批测并确认输出字段与现有自部署引擎结果可直接对比

## 4. Browser Demo

- [x] 4.1 编写 `verification-2-self/qwen3-asr/demo/index.html`，支持文件上传转写和结果展示
- [x] 4.2 如 Qwen3-ASR 支持流式接口，则补充实时录音、增量结果和最终结果展示
- [x] 4.3 如浏览器不能直接访问容器接口，则补充本地代理或 Demo 启动脚本
- [x] 4.4 验证 Demo 能连接本地 Qwen3-ASR 服务并完成至少一次成功转写

## 5. Docs And Comparison

- [x] 5.1 更新 `verification-2-self/README.md`，加入 Qwen3-ASR 引擎表项和运行说明
- [x] 5.2 更新 `docs/verification-2-self-deploy.md`，加入 Qwen3-ASR 验证阶段、能力说明和四引擎对比表
- [x] 5.3 更新多引擎对比逻辑或报告产物，使其纳入 FunASR、SenseVoice、WeNet、Qwen3-ASR 四方结果
- [x] 5.4 运行一次端到端验证，确认 Qwen3-ASR 能进入现有验证二体系
