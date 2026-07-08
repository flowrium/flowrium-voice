## Vosk small Test Results

**Config**: model=small, model_path=/Users/lixiaofeng/Workspace/personal/flowrium-voice/verification-3-edge/vosk/models/vosk-model-small-cn-0.22, manifests=/Users/lixiaofeng/Workspace/personal/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Workspace/personal/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Workspace/personal/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 720 | |
| 成功条数 | 418 | 归一化后完全匹配 |
| **成功率** | **58.06%** | 成功条数/总条数 |
| CER | 6.29% | 字符错误率 |
| 平均 RTF | 0.3255 | <1.0 表示快于实时 |
| P95 RTF | 0.4990 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| director | 180 | 100 | **55.56%** | 7.16% | 0.3176 |
| principal | 180 | 83 | **46.11%** | 7.32% | 0.3042 |
| staff | 180 | 133 | **73.89%** | 3.55% | 0.3479 |
| teacher | 180 | 102 | **56.67%** | 6.78% | 0.3322 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| humanized | 240 | 159 | **66.25%** | 4.15% | 0.3269 |
| myvoice | 240 | 104 | **43.33%** | 10.43% | 0.3039 |
| standard | 240 | 155 | **64.58%** | 4.30% | 0.3457 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| director_042 | 看调课审批。 | 砍掉 雕刻 审批 | 80.00% |
| staff_006 | 打开办公台。 | 那 派 半公开 | 80.00% |
| staff_042 | 提报修。 | 题 保修 | 66.67% |
| staff_042 | 提报修。 | 题 保修 | 66.67% |
| teacher_054 | 看家校沟通。 | 参加 小 沟通 | 60.00% |
| teacher_054 | 看家校沟通。 | 参加 小 沟通 | 60.00% |
| principal_048 | 看招生分析。 | 按照 上 分析 | 60.00% |
| director_036 | 看值班安排。 | 但 纸板 安排 | 60.00% |
