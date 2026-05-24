## ADDED Requirements

### Requirement: 批量测试脚本支持双模型
系统 SHALL 提供 `scripts/test_sherpa_onnx_batch.py` 脚本，支持通过 `--model` 参数选择 Paraformer Int8 或 SenseVoice Int8 模型。

#### Scenario: 使用 Paraformer 模型测试
- **WHEN** 执行 `python test_sherpa_onnx_batch.py --model paraformer`
- **THEN** 脚本加载 Paraformer Int8 模型，对 manifest 中所有音频进行推理，输出 CER 和 RTF 指标

#### Scenario: 使用 SenseVoice 模型测试
- **WHEN** 执行 `python test_sherpa_onnx_batch.py --model sensevoice`
- **THEN** 脚本加载 SenseVoice Int8 模型，对 manifest 中所有音频进行推理，输出 CER 和 RTF 指标

### Requirement: 复用音频 Manifest
脚本 SHALL 接受 `--manifest` 参数，复用 `audio/standard/manifest.csv`、`audio/humanized/manifest.csv`、`audio/myvoice/manifest.csv`，默认加载全部三个 manifest。

#### Scenario: 默认加载全部 manifest
- **WHEN** 执行脚本不指定 `--manifest`
- **THEN** 脚本加载 standard、humanized、myvoice 三个 manifest

#### Scenario: 指定单个 manifest
- **WHEN** 执行 `python test_sherpa_onnx_batch.py --model paraformer --manifest audio/standard/manifest.csv`
- **THEN** 脚本只加载指定的 manifest

### Requirement: CER 计算
脚本 SHALL 计算每条音频的 CER（字错率）和整体 CER，计算方式为：去除标点后，对比参考文本与转写文本的编辑距离除以参考文本长度。

#### Scenario: CER 计算正确
- **WHEN** 转写结果为"打开学校运行数据"而参考文本为"打开学校今日运行数据大屏"
- **THEN** CER = 缺失字数 / 参考文本字数（去除标点后计算）

### Requirement: RTF 测量
脚本 SHALL 测量每条音频的 RTF（实时率），计算方式为：推理耗时 / 音频时长。RTF < 1.0 表示快于实时。

#### Scenario: RTF 计算正确
- **WHEN** 音频时长 3 秒，推理耗时 0.5 秒
- **THEN** RTF = 0.5 / 3 = 0.167

### Requirement: 热词测试
脚本 SHALL 支持 `--hotword` 参数，对 Paraformer 模型加热词进行测试。SenseVoice 模型忽略热词参数并给出提示。

#### Scenario: Paraformer 加热词测试
- **WHEN** 执行 `python test_sherpa_onnx_batch.py --model paraformer --hotword "出勤率,合格率,教务处"`
- **THEN** 脚本将热词传入模型，输出加热词后的 CER 结果

#### Scenario: SenseVoice 忽略热词
- **WHEN** 执行 `python test_sherpa_onnx_batch.py --model sensevoice --hotword "出勤率"`
- **THEN** 脚本提示 SenseVoice 不支持热词，忽略该参数继续测试

### Requirement: 结果输出格式
脚本 SHALL 输出三种格式的结果文件到 `results/` 目录：JSON（完整数据）、CSV（汇总表）、report.md（可读报告）。

#### Scenario: 输出三种格式
- **WHEN** 脚本完成批量测试
- **THEN** 在 `results/` 目录下生成 `sherpa-onnx-{model}-results.json`、`sherpa-onnx-{model}-results.csv`、`sherpa-onnx-{model}-report.md`

### Requirement: 按 role 分组统计
脚本 SHALL 按 manifest 中的 role 字段（如 principal）分组统计 CER 和 RTF，并在报告中展示分组结果。

#### Scenario: 分组统计输出
- **WHEN** manifest 包含 principal 和 teacher 两种 role
- **THEN** 报告中分别展示各 role 的 CER 和 RTF 均值
