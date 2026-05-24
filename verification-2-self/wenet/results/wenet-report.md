## WeNet Test Results

**Config**: mode=single, hotwords=no, manifests=audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | 240 | 共测试了多少条语音 |
| 成功条数 (Passed) | 71 | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **29.58%** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | 14.80% | 按字统计，辅助参考 |
| 平均最终延迟 | 217.8ms | — |
| P95 最终延迟 | 342.3ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| director | 60 | 16 | **26.67%** | 13.75% |
| principal | 60 | 9 | **15.00%** | 18.61% |
| staff | 60 | 28 | **46.67%** | 10.18% |
| teacher | 60 | 18 | **30.00%** | 15.93% |

### Failed Cases (top 8)
| ID | 标记 | Expected | Actual | CER |
| --- | --- | --- | --- | --- |
| principal_012 | NORM_MISMATCH | 看今天到校。 | 很仅仅到笑 | 80.00% |
| principal_042 | NORM_MISMATCH | 看德育统计。 | 判得一同计 | 80.00% |
| director_030 | NORM_MISMATCH | 看违纪记录。 | 潘玮琪纪录 | 80.00% |
| staff_036 | NORM_MISMATCH | 订会议室。 | 定会一线 | 75.00% |
| principal_054 | NORM_MISMATCH | 看家校沟通统计。 | 你点小国同统计 | 71.43% |
| director_057 | NORM_MISMATCH | 帮我生成本年级周简报。 | 王某申成本年期交警报告 | 70.00% |
| principal_044 | NORM_MISMATCH | 查询本学期学生流失预警名单。 | 他行等贤妻学生刘诗玉警名单 | 61.54% |
| principal_030 | NORM_MISMATCH | 看安全巡检。 | 安全行件 | 60.00% |
