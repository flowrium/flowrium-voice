## ADDED Requirements

### Requirement: 模型选型结论报告
系统 SHALL 生成 `results/model-selection-report.md`，对比 Paraformer Int8 和 SenseVoice Int8 的 CER、RTF、内存占用、热词支持，给出端侧主力模型推荐。

#### Scenario: 包含完整对比维度
- **WHEN** 两个模型的批量测试均已完成
- **THEN** 报告包含以下对比维度：整体 CER、分组 CER、RTF、内存占用、热词效果（仅 Paraformer）、与验证二完整模型的 CER 差距

#### Scenario: 给出明确推荐
- **WHEN** 报告完成
- **THEN** 报告给出明确的端侧主力模型推荐及理由

### Requirement: 与验证二完整模型对比
报告 SHALL 包含量化模型与验证二完整模型（FunASR Paraformer、SenseVoice）的 CER 对比，量化精度损失。

#### Scenario: 量化损失量化
- **WHEN** Paraformer Int8 CER 为 8%，验证二 FunASR Paraformer CER 为 5%
- **THEN** 报告记录量化损失为 +3% CER

### Requirement: 端侧可行性判定
报告 SHALL 根据验证计划中的通过标准（RTF < 1.0、CER < 15%、内存 < 1.5GB）给出各模型的通过/失败判定。

#### Scenario: 模型通过
- **WHEN** Paraformer Int8 的 CER < 15%、RTF < 1.0
- **THEN** 报告判定 Paraformer Int8 端侧可行

#### Scenario: 模型未通过
- **WHEN** SenseVoice Int8 的 CER > 15%
- **THEN** 报告判定 SenseVoice Int8 端侧不可行，记录原因
