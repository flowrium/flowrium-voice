## FunASR Test Results

**Config**: mode=2pass, hotwords=no, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | 240 | 共测试了多少条语音 |
| 成功条数 (Passed) | 179 | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **74.58%** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | 3.05% | 按字统计，辅助参考 |
| 平均最终延迟 | 1246.3ms | — |
| P95 最终延迟 | 2330.5ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| director | 60 | 42 | **70.00%** | 3.44% |
| principal | 60 | 40 | **66.67%** | 4.15% |
| staff | 60 | 53 | **88.33%** | 1.13% |
| teacher | 60 | 44 | **73.33%** | 3.19% |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| principal_054 | 看家校沟通统计。 | 参加校高通统计。 | 42.86% |
| principal_042 | 看德育统计。 | 潘德预统计。 | 40.00% |
| director_042 | 看调课审批。 | 看雕刻审批。 | 40.00% |
| teacher_054 | 看家校沟通。 | 参加校沟通。 | 40.00% |
| director_020 | 对比各班级语文平均分。 | 对比各班及与文凭均分。 | 30.00% |
| staff_036 | 订会议室。 | 进会议室。 | 25.00% |
| principal_052 | 我想查查各学科教学任务完成情况。 | 我想扎扎个学科教学任务完成情况。 | 20.00% |
| director_039 | 帮我打开调课审批列表。 | 帮我打开雕刻审批列表。 | 20.00% |
