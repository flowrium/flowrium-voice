## SenseVoice Test Results

**Config**: mode=offline, hotwords=no, manifests=C:/Users/lixiaofeng/Repos/flowrium-voice/audio/standard/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/humanized/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | 720 | 共测试了多少条语音 |
| 成功条数 (Passed) | 617 | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **85.69%** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | 1.89% | 按字统计，辅助参考 |
| 平均最终延迟 | 753.6ms | — |
| P95 最终延迟 | 1013.9ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| director | 180 | 151 | **83.89%** | 2.15% |
| principal | 180 | 149 | **82.78%** | 2.41% |
| staff | 180 | 159 | **88.33%** | 1.35% |
| teacher | 180 | 158 | **87.78%** | 1.52% |

### Language Detection
| Language | Count |
| --- | --- |
| ko | 1 |
| yue | 3 |
| zh | 716 |

### Failed Cases (top 8)
| ID | 标记 | Expected | Actual | CER |
| --- | --- | --- | --- | --- |
| director_030 | NORM_MISMATCH | 看违纪记录。 | 의지지로 | 100.00% |
| principal_048 | NORM_MISMATCH | 看招生分析。 | 探州商分市 | 80.00% |
| staff_042 | NORM_MISMATCH | 提报修。 | 起报销 | 66.67% |
| principal_042 | NORM_MISMATCH | 看德育统计。 | 判得预统计 | 60.00% |
| staff_036 | NORM_MISMATCH | 订会议室。 | 定会议识 | 50.00% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 参加校沟通 | 40.00% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 参加校沟通 | 40.00% |
| director_048 | NORM_MISMATCH | 看备课检查。 | 看贝克检查 | 40.00% |
