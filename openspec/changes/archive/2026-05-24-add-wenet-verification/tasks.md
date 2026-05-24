## 1. WeNet 部署

- [x] 1.1 创建 `verification-2-self/wenet/` 目录结构（demo/, docker/, results/, scripts/）
- [x] 1.2 编写 `wenet/docker/start.sh` — 拉取 wenet-e2e/wenet:latest 镜像并启动容器，映射端口 10097
- [x] 1.3 编写 `wenet/docker/stop.sh` — 停止并移除 WeNet 容器
- [x] 1.4 验证 Docker 容器启动后 WebSocket 端点 ws://localhost:10097 可用

## 2. WeNet 批量测试脚本

- [x] 2.1 编写 `wenet/scripts/test_wenet_batch.py` 基础框架 — argparse、manifest 加载、CER 计算（复用 FunASR 脚本逻辑）
- [x] 2.2 实现 WeNet WebSocket 协议通信 — start signal、音频帧分片发送（960 samples/frame）、end signal、响应解析
- [x] 2.3 实现 --hotword 和 --hotwords-file 参数支持
- [x] 2.4 实现 --limit、--version、--role 过滤选项
- [x] 2.5 实现 JSON 和 CSV 输出，字段结构与 FunASR 对齐
- [x] 2.6 实现汇总统计（overall/by_version/by_role/by_category/worst_cases）
- [x] 2.7 验证脚本对 Wenet 服务执行批量测试并生成结果文件

## 3. WeNet 浏览器 Demo

- [x] 3.1 编写 `wenet/demo/index.html` — 实时录音界面（开始/停止、WebSocket 连接配置、热词管理、结果展示）
- [x] 3.2 编写 `wenet/demo/serve.py` — 本地代理服务，处理浏览器同源访问
- [x] 3.3 编写 `wenet/demo/start.sh` — 启动本地代理
- [x] 3.4 验证 Demo 可连接 WeNet 服务，实时录音能出字，文件上传能出结果

## 4. 文档更新

- [x] 4.1 更新 `verification-2-self/README.md` — 引擎表新增 WeNet 行（协议: WebSocket，说明: WeNet 流式/离线转写，支持热词）
- [x] 4.2 更新 `docs/verification-2-self-deploy.md` — Phase 3 后插入 WeNet Phase，Phase 4 对比表扩展为三引擎
