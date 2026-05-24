## Context

验证二 Phase 2 需要系统化测试 Paraformer 转写效果。当前 `scripts/test_funasr_batch.py` 支持单次运行（一个模式、一组热词配置），输出 JSON/CSV 和终端摘要。Phase 2 需要 6 轮对比（3 模式 × 2 热词配置），并产出对齐验证计划的 Markdown 报告。

音频目录约定：`audio/A-daily/` ~ `audio/F-far/`（用户自录），已有 `audio/standard/` 和 `audio/humanized/`（TTS 基线）。所有目录下的 manifest.csv 格式一致。

约束：FunASR Docker 服务在本地运行（ws://127.0.0.1:10095），CPU-only。

## Goals / Non-Goals

**Goals:**

- 一键全跑 6 轮对比（3 模式 × 有/无热词），自动产出 Markdown 报告
- 从音频目录名推断 category，支持 by_category 分组统计
- 报告对齐验证计划结构：模式对比表、热词效果表、场景分组表、最差案例
- 保留原有单次运行能力（向后兼容）

**Non-Goals:**

- 不改 FunASR Docker 配置或 Demo 页面
- 不做自动化噪音/远距离音频生成
- 不做 CER 的人工校对流程
- 不做资源占用监控（docker stats），那是手动观察的

## Decisions

### 1. category 从目录名推断

**选择**: 脚本从 `file_path` 的父目录名提取 category。匹配 `^[A-F]-` 前缀的归入对应分类，其余归入 `tts-baseline`。

**理由**: 用户用目录分类就是因为简单直观，不应要求多维护一列。目录命名已有约定（A-daily, B-metrics 等），直接用。

**替代方案**:
- manifest.csv 加 category 列：多维护一列，目录已经编码了这个信息
- 硬编码目录→category 映射：不如正则灵活

### 2. 一键全跑通过 `--compare` flag 触发

**选择**: 新增 `--compare` flag，跑全量对比。不加 flag 时行为不变。

**理由**: 向后兼容。`python test_funasr_batch.py` 仍然单次运行，`--compare` 才触发多轮。

**替代方案**:
- `--mode 2pass,online,offline` 逗号分隔：改变了 `--mode` 的语义，且无法表达热词对比
- 独立脚本 `run_comparison.py`：重复代码多，不如在原脚本里加 flag

### 3. 热词列表从预设文件读取

**选择**: `--compare` 模式下，热词列表从 `config/hotwords.txt`（每行一个词）读取。也可通过 `--hotword` 覆盖。

**理由**: 验证计划里的热词列表是固定的（出勤率、合格率等），文件比命令行传 16 个 `--hotword` 方便。

### 4. 报告直接写入 results 目录

**选择**: `--compare` 输出 `verification-2-self/results/paraformer-report.md`，每轮 JSON 也保留在同目录。

**理由**: 和已有目录结构一致，结果和代码分离。

## Risks / Trade-offs

- [6 轮耗时] → 80 条 × 6 = 480 次 WebSocket 调用，约 15-25 分钟。缓解：终端实时打印进度，支持 Ctrl+C 中断。
- [目录名约定耦合] → 如果用户录的音频目录名不以 A-F 开头，会被归入 `tts-baseline`。缓解：终端打印 category 推断结果，用户可及时发现。
- [FunASR 容器中途断连] → 单轮失败不中断整体，标记 error 继续。缓解：报告里标注失败条目。
