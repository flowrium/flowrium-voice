# ASR Test Report — Shared Format & Metrics

所有 ASR 测试 skill（funasr、sensevoice、wenet）共用此报告格式和指标说明。各 skill 的 SKILL.md 直接引用此文件，不再重复撰写。

## Metrics Explained

报告中包含两个核心指标，容易混淆，这里明确区分：

### 总体成功率 (Success Rate) — 主指标
- **统计粒度**：按**句**计算（utterance-level）
- **计算方式**：每条语音是一个样本，ASR 识别结果与期望文本完全一致（标点符号归一化后）即算"成功"
  ```
  总体成功率 = 成功条数 / 总条数 × 100%
  ```
- **含义**：10 条语音中只有 1 条完全识别正确，成功率为 **10%**
- **报告中对应字段**：`总体成功率` / `Norm Exact Match Rate`
- **意义**：反映最终用户体验——用户说了一句话，系统能否一字不差地听懂

### CER (Character Error Rate) — 辅助指标
- **统计粒度**：按**字**计算（character-level）
- **计算方式**：对所有语音累加编辑距离后，除以总字符数
  ```
  CER = Σ编辑距离(期望, 实际) / Σ期望字符数
  ```
- **含义**：100 个字里错了 3 个字，CER 为 **3%**
- **意义**：反映整体识别质量，适合跨版本对比

### 为什么短文本 CER 看起来特别高
短文本对 CER 更敏感——同样错 1 个字：
| 文本长度 | CER |
| --- | --- |
| "订会议室"（4字） | 25% |
| "查看本月教师考勤异常统计"（13字） | 7.7% |

所以单个案例 CER 高达 40%，并不意味着"一半的字都错了"，而可能是 7 个字的短句错了 3 个字。

**判断整体质量应优先看总体成功率，CER 辅助参考。**

## Report Format — Single Mode Run

```
## <Engine> Test Results

**Config**: mode=<mode>, hotwords=<yes/no>, manifests=<list>

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | <count> | 共测试了多少条语音 |
| 成功条数 (Passed) | <n> | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **<rate>** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | <cer> | 按字统计，辅助参考 |
| 平均最终延迟 | <latency>ms | — |
| P95 最终延迟 | <latency>ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| <role> | <n> | <n> | <rate> | <cer> |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| <id> | <text> | <text> | <cer> |
```

每个 engine 可以根据自身特性在 Overall 表格中追加额外指标行（如语言检测、首次部分延迟等），但上述列为必含项。

## Report Format — Comparison Run

For comparison runs across multiple modes/hotword combinations:

1. **Overall summary table** — mode x hotword matrix with pass rate + CER
2. **Category pass rates** — per round breakdown
3. **Version x Role cross table** — for best mode+hotword combination
4. **Mode comparison** — CER, pass rate, latency across modes
5. **Hotword effect** — before/after comparison for each mode
6. **Failed cases** — all non-matching results

## Key Metrics to Highlight

- **总体成功率 (Success Rate)**: 主指标，按句统计。每条语音完全正确才算成功。
- **CER (字符错误率)**: 辅助指标，按字统计。< 5% 为优秀。
- **Latency**: first-partial and final; watch for P95 spikes
- **Hotword lift**: compare with vs without hotwords