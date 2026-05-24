# WAV 生成规划

## 1. 目标

为 `docs/wav-test.md` 中的测试语料生成可重复、可对比、可扩展的 WAV 文件，用于：

- ASR 准确率测试
- 不同声线版本对比
- 后续方言版本扩展
- 不同模型或引擎的批量回归测试

本文档只定义音频生成规范，不维护测试句子本身。

## 2. 基本原则

### 2.1 语料与音频分离

- `docs/wav-test.md` 负责维护测试语料。
- 本文档负责维护音频版本、目录、命名、验收标准。
- 脚本负责批量生成，不在脚本里长期硬编码全部测试文本。

### 2.2 版本先行

音频文件按“版本”管理，而不是只按“角色”管理。这样后续新增方言、情绪、录制方式时，不需要重构目录。

### 2.3 结果可追溯

每个音频文件都应能追溯到：

- 原始文本
- 角色
- 版本
- 使用声线
- 生成方式

## 3. 输出格式

统一输出：

- 格式：`wav`
- 编码：`PCM 16-bit`
- 采样率：`16kHz`
- 声道：`mono`

这样可以直接用于现有验证文档和 Demo 中的上传/转写测试。

## 4. 版本体系

第一阶段先定义两类版本。

### 4.1 `standard`

标准版，目标是稳定、清晰、无明显个性化修饰，适合做基础识别率测试。

建议特征：

- 正常语速
- 发音清晰
- 断句直接
- 情绪中性

### 4.2 `humanized`

拟人化版，目标是更接近日常办公口播，但仍然服务于识别测试，不追求表演感。

建议特征：

- 语速略慢于标准版
- 句间停顿更自然
- 断句更接近日常说话
- 语气自然，但不夸张
- 保持指令清晰，不牺牲可识别性

说明：

- “拟人化”不是简单更换一个发音人，而是一套可复用的生成标准。
- 后续不论接本地 TTS、云端 TTS，还是人工录音，都应尽量满足这组特征。

## 5. 方言扩展方式

后续新增方言版本时，不改现有结构，只新增版本名。

示例：

- `dialect-cantonese`
- `dialect-sichuan`
- `dialect-minnan`

扩展约束：

- 方言版仍保持统一输出格式。
- 每个方言版本都要保留同一批测试文本，便于横向对比。
- 若同一句在方言中需要更自然的说法，应在 manifest 中记录“原文”和“方言口语化文本”。

## 6. 目录结构

建议采用“版本 + 角色”双层目录：

```text
audio/
  standard/
    principal/
    director/
    teacher/
    staff/
  humanized/
    principal/
    director/
    teacher/
    staff/
```

后续扩展：

```text
audio/
  dialect-cantonese/
    principal/
    director/
    teacher/
    staff/
```

这样可以直接按版本做批量对比，也方便按角色抽样测试。

## 7. 命名规则

建议文件名包含角色和顺序号，版本放在目录层级，不重复写入文件名：

```text
audio/humanized/principal/principal_001.wav
audio/humanized/principal/principal_002.wav
audio/standard/teacher/teacher_001.wav
```

命名要求：

- 顺序号统一 3 位：`001`
- 同一角色下编号稳定，不因版本变化而改变
- 同一条文本在不同版本中保持相同编号，便于对比

## 8. Manifest 设计

每次批量生成都建议产出一份清单文件，例如：

- `audio/manifest.json`
- 或 `audio/manifest.csv`

建议字段：

- `id`
- `role`
- `index`
- `text`
- `version`
- `voice`
- `source`
- `file_path`
- `notes`

示例：

```json
{
  "id": "principal_001",
  "role": "principal",
  "index": 1,
  "text": "打开学校今日运行数据大屏。",
  "version": "humanized",
  "voice": "Tingting",
  "source": "macos-say",
  "file_path": "audio/humanized/principal/principal_001.wav",
  "notes": "slower pace, natural pause"
}
```

## 9. 生成方式规划

### 9.1 当前可用方式

仓库里已有 [scripts/generate_school_audio.sh](/Users/lixiaofeng/Code/github/flowrium-voice/scripts/generate_school_audio.sh)，当前能力是：

- 使用 macOS `say`
- 生成单一声线
- 转成 16kHz 单声道 WAV

### 9.2 下一步脚本改造方向

建议后续把脚本改成以下结构：

- 支持 `VERSION=standard|humanized`
- 支持按角色输出到 `audio/<version>/<role>/`
- 支持从语料清单读取内容，而不是在脚本中硬编码
- 支持生成 manifest
- 支持后续增加更多版本配置

### 9.3 版本配置建议

后续可以单独维护一份版本配置，例如：

- `config/audio-versions.json`
- 或 `docs/audio-versions.md`

配置内容可以包括：

- 版本名
- 使用声线
- 语速
- 停顿策略
- 备注

## 10. 验收标准

无论哪种版本，都建议满足以下最低要求：

- 无明显爆音、截断、杂音
- 音量基本一致
- 句首句尾完整
- 指令内容清楚可辨
- 同批次文件格式一致

拟人化版额外关注：

- 不要出现机械逐字朗读感
- 不要加入夸张情绪
- 不要因为停顿过长影响识别

## 11. 推荐实施顺序

第一步：

- 固化 `docs/wav-test.md` 作为测试语料库
- 固化本文档作为生成规范

第二步：

- 改造生成脚本，先产出 `standard` 和 `humanized` 两套版本

第三步：

- 为生成结果补 manifest
- 用现有 Demo 或测试流程做首轮对比

第四步：

- 再增加方言版本或其他特殊版本

## 12. 当前结论

当前阶段先把“拟人化”定义成一个独立版本 `humanized` 是合理的。这样后续新增方言版本时，体系仍然稳定，只是在版本层增加新分支，不需要重写语料、目录结构或测试方法。
