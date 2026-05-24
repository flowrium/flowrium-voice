## ADDED Requirements

### Requirement: Sherpa-ONNX Python 环境安装
系统 SHALL 提供 `setup/install_sherpa_onnx.sh` 脚本，在 macOS 上安装 `sherpa-onnx` pip 包并验证安装成功。

#### Scenario: 全新安装成功
- **WHEN** 在未安装 sherpa-onnx 的 macOS 环境下执行 `setup/install_sherpa_onnx.sh`
- **THEN** 脚本成功安装 `sherpa-onnx` pip 包，且 `python -c "import sherpa_onnx"` 无报错

#### Scenario: 已安装时跳过
- **WHEN** sherpa-onnx 已安装时执行脚本
- **THEN** 脚本检测到已安装并提示，不重复安装

### Requirement: 量化模型下载
系统 SHALL 提供 `setup/download_models.sh` 脚本，从 HuggingFace 下载 Paraformer Int8 和 SenseVoice Int8 量化模型到本地目录。

#### Scenario: 下载两个量化模型
- **WHEN** 执行 `setup/download_models.sh`
- **THEN** 脚本下载 sherpa-onnx/paraformer-zh-quantized 和 sherpa-onnx/sensevoice-zh-quantized 到 `verification-3-edge/sherpa-onnx/models/` 目录

#### Scenario: 模型已存在时跳过
- **WHEN** 模型文件已存在时执行脚本
- **THEN** 脚本检测到已有文件并跳过下载

### Requirement: 环境验证
系统 SHALL 提供 `setup/verify_setup.sh` 脚本，加载模型并运行一次短音频推理，验证整个链路可用。

#### Scenario: 环境验证通过
- **WHEN** 执行 `setup/verify_setup.sh`
- **THEN** 脚本加载 Paraformer Int8 模型，对 `audio/standard/` 下任意一条音频进行推理，输出转写结果
