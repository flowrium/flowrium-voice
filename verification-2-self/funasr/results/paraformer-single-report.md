## FunASR Test Results

**Config**: mode=2pass, hotwords=no, manifests=C:/Users/lixiaofeng/Repos/flowrium-voice/audio/standard/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/humanized/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | 720 | 共测试了多少条语音 |
| 成功条数 (Passed) | 574 | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **79.72%** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | 2.34% | 按字统计，辅助参考 |
| 平均最终延迟 | 552.2ms | — |
| P95 最终延迟 | 853.5ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| director | 180 | 134 | **74.44%** | 2.77% |
| principal | 180 | 144 | **80.00%** | 2.54% |
| staff | 180 | 162 | **90.00%** | 1.02% |
| teacher | 180 | 134 | **74.44%** | 2.88% |

### Failed Cases (top 8)
| ID | 标记 | Expected | Actual | CER |
| --- | --- | --- | --- | --- |
| principal_054 | NORM_MISMATCH | 看家校沟通统计。 | 参加校高通统计。 | 42.86% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 参加校沟通。 | 40.00% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 参加校沟通。 | 40.00% |
| principal_042 | NORM_MISMATCH | 看德育统计。 | 潘德预统计。 | 40.00% |
| director_042 | NORM_MISMATCH | 看调课审批。 | 看雕刻审批。 | 40.00% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 参加校沟通。 | 40.00% |
| staff_042 | NORM_MISMATCH | 提报修。 | t报修。 | 33.33% |
| staff_042 | NORM_MISMATCH | 提报修。 | t报修。 | 33.33% |
