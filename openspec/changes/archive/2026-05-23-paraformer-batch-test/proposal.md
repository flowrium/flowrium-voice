## Why

Phase 2 需要系统化测试 Paraformer 的转写效果，产出可量化的对比报告（模式对比、热词效果、场景分组）。当前批量测试脚本只支持单次运行，无法自动产出 Phase 2 验证计划要求的对比维度。

## What Changes

- 增强 `test_funasr_batch.py`，支持一键全跑（3 模式 × 2 热词配置 = 6 轮）
- 从音频目录名推断 category（A-daily ~ F-far），新增 by_category 分组统计
- 新增 Markdown 报告生成，对齐验证计划的表格结构：模式对比、热词效果、场景分组、最差案例
- 已有 TTS 音频（standard/humanized）归为 `tts-baseline` category

## Capabilities

### New Capabilities

- `batch-test-comparison`: 批量测试脚本的多轮对比运行与报告生成能力，包括模式对比、热词前后对比、场景分组统计、Markdown 报告输出

### Modified Capabilities

## Impact

- 修改 `scripts/test_funasr_batch.py`
- 新增 `config/hotwords.txt`
- 新增报告输出到 `verification-2-self/results/`
- 音频目录结构约定：`audio/A-daily/` ~ `audio/F-far/`，manifest.csv 沿用现有格式
