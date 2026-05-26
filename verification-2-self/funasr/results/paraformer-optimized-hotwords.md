## FunASR Test Results

**Config**: mode=2pass, hotwords=yes, manifests=C:/Users/lixiaofeng/Repos/flowrium-voice/audio/standard/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/humanized/manifest.csv, C:/Users/lixiaofeng/Repos/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 (Count) | 720 | 共测试了多少条语音 |
| 成功条数 (Passed) | 576 | 归一化后完全匹配的条数 |
| **总体成功率 (Success Rate)** | **80.00%** | 按句统计：成功条数/总条数 |
| CER (字符错误率) | 2.78% | 按字统计，辅助参考 |
| 平均最终延迟 | 476.3ms | — |
| P95 最终延迟 | 712.8ms | — |

### By Role (按角色分组的总体成功率)
| Role | Count | 成功数 | **成功率** | CER |
| --- | --- | --- | --- | --- |
| director | 180 | 132 | **73.33%** | 3.96% |
| principal | 180 | 139 | **77.22%** | 3.21% |
| staff | 180 | 163 | **90.56%** | 0.97% |
| teacher | 180 | 142 | **78.89%** | 2.73% |

### Failed Cases (top 8)
| ID | 标记 | Expected | Actual | CER |
| --- | --- | --- | --- | --- |
| principal_054 | NORM_MISMATCH | 看家校沟通统计。 | 参加校高通统计。 | 42.86% |
| principal_042 | NORM_MISMATCH | 看德育统计。 | 潘德预统计。 | 40.00% |
| teacher_054 | NORM_MISMATCH | 看家校沟通。 | 参加校沟通。 | 40.00% |
| director_005 | NORM_MISMATCH | 切到七年级管理工作台首页。 | 切到7年级一班工作台首页。 | 25.00% |
| director_005 | NORM_MISMATCH | 切到七年级管理工作台首页。 | 切到7年级一班工作台首页。 | 25.00% |
| director_005 | NORM_MISMATCH | 切到七年级管理工作台首页。 | 切到7年级一班工作台首页。 | 25.00% |
| staff_036 | NORM_MISMATCH | 订会议室。 | 进会议室。 | 25.00% |
| staff_036 | NORM_MISMATCH | 订会议室。 | 进会议室。 | 25.00% |
