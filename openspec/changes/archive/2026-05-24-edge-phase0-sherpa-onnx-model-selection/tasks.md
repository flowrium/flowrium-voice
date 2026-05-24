## 1. 环境搭建

- [x] 1.1 编写 `verification-3-edge/sherpa-onnx/setup/install_sherpa_onnx.sh`，安装 sherpa-onnx pip 包并验证
- [x] 1.2 编写 `verification-3-edge/sherpa-onnx/setup/download_models.sh`，从 HuggingFace 下载 Paraformer Int8 和 SenseVoice Int8 量化模型
- [x] 1.3 编写 `verification-3-edge/sherpa-onnx/setup/verify_setup.sh`，加载模型并对一条测试音频推理，验证链路可用
- [x] 1.4 执行安装脚本，确认 macOS 环境下 Sherpa-ONNX 可正常工作

## 2. 批量测试脚本

- [x] 2.1 编写 `verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py`，支持 `--model`（paraformer/sensevoice）和 `--manifest` 参数
- [x] 2.2 实现 CER 计算逻辑（去除标点、编辑距离），与验证二保持一致
- [x] 2.3 实现 RTF 测量（推理耗时/音频时长）
- [x] 2.4 实现 `--hotword` 参数支持，Paraformer 加热词测试，SenseVoice 忽略并提示
- [x] 2.5 实现按 role 分组统计
- [x] 2.6 实现结果输出：JSON + CSV + report.md 三种格式

## 3. 运行测试

- [x] 3.1 运行 Paraformer Int8 批量测试（standard + humanized + myvoice manifest）
- [x] 3.2 运行 Paraformer Int8 加热词批量测试 — 发现 Sherpa-ONNX Paraformer 量化模型不支持热词（仅 transducer 模型支持），记录此限制
- [x] 3.3 运行 SenseVoice Int8 批量测试
- [x] 3.4 检查结果文件完整性（JSON/CSV/report.md）

## 4. 模型选型报告

- [x] 4.1 编写 `verification-3-edge/sherpa-onnx/results/model-selection-report.md`，对比两个模型的 CER、RTF、内存、热词效果
- [x] 4.2 对比量化模型与验证二完整模型的 CER 差距，量化精度损失
- [x] 4.3 根据通过标准（RTF < 1.0、CER < 15%、内存 < 1.5GB）给出各模型判定
- [x] 4.4 给出端侧主力模型推荐及理由
