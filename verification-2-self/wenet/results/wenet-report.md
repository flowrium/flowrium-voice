## WeNet Test Results

**Config**: mode=single, hotwords=no, manifests=C:/Users/lixiaofeng/Repos/flowrium-voice/audio/standard/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/humanized/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | 720 | 共测试了多少条语音 |
| 成功条数 (Passed) | 155 | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **21.53%** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | 13.83% | 按字统计，辅助参考 |
| 平均最终延迟 | 188.5ms | — |
| P95 最终延迟 | 240.5ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| director | 180 | 28 | **15.56%** | 13.28% |
| principal | 180 | 29 | **16.11%** | 14.37% |
| staff | 180 | 67 | **37.22%** | 10.02% |
| teacher | 180 | 31 | **17.22%** | 17.40% |

### Failed Cases (top 8)
| ID | 标记 | Expected | Actual | CER |
| --- | --- | --- | --- | --- |
| teacher_030 | NORM_MISMATCH | 看未交作业。 | 捍卫焦 | 100.00% |
| teacher_030 | NORM_MISMATCH | 看未交作业。 | 捍卫焦 | 100.00% |
| staff_042 | NORM_MISMATCH | 提报修。 | 踢豹 | 100.00% |
| director_030 | NORM_MISMATCH | 看违纪记录。 | 看维际 | 80.00% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 康佳小沟 | 80.00% |
| director_030 | NORM_MISMATCH | 看违纪记录。 | 看维季 | 80.00% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 康佳小沟 | 80.00% |
| principal_012 | NORM_MISMATCH | 看今天到校。 | 很仅仅到笑 | 80.00% |
