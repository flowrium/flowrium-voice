## SenseVoice Test Results

**Config**: mode=offline, hotwords=no, manifests=audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | 240 | 共测试了多少条语音 |
| 成功条数 (Passed) | 173 | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **72.08%** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | 3.71% | 按字统计，辅助参考 |
| 平均最终延迟 | 247.4ms | — |
| P95 最终延迟 | 424.8ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| director | 60 | 39 | **65.00%** | 4.73% |
| principal | 60 | 39 | **65.00%** | 5.09% |
| staff | 60 | 52 | **86.67%** | 1.45% |
| teacher | 60 | 43 | **71.67%** | 3.19% |

### Language Detection
| Language | Count |
| --- | --- |
| ko | 1 |
| yue | 3 |
| zh | 236 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| director_030 | 看违纪记录。 | 의지지로 | 100.00% |
| principal_048 | 看招生分析。 | 探州商分市 | 80.00% |
| principal_042 | 看德育统计。 | 判得预统计 | 60.00% |
| staff_036 | 订会议室。 | 定会议识 | 50.00% |
| director_048 | 看备课检查。 | 看贝克检查 | 40.00% |
| teacher_018 | 看班级名单。 | 判班及名单 | 40.00% |
| teacher_042 | 看课堂表现。 | 课糖表现 | 40.00% |
| teacher_054 | 看家校沟通。 | 参加校沟通 | 40.00% |
