## whisper.cpp base Test Results

**Config**: model=base, language=zh, threads=4, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 5 | |
| 成功条数 | 0 | 归一化后完全匹配 |
| **成功率** | **0.00%** | 成功条数/总条数 |
| CER | 100.00% | 字符错误率 |
| 平均 RTF | 0.5083 | <1.0 表示快于实时 |
| P95 RTF | 0.5584 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| principal | 5 | 0 | **0.00%** | 100.00% | 0.5083 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| standard | 5 | 0 | **0.00%** | 100.00% | 0.5083 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| principal_005 | 打开校长驾驶舱里的学校运行总览页。 |  | 100.00% |
| principal_004 | 我想看一下今天的学校整体情况。 |  | 100.00% |
| principal_001 | 打开学校今日运行数据大屏。 |  | 100.00% |
| principal_002 | 切换到校长驾驶舱首页。 |  | 100.00% |
| principal_003 | 帮我打开学校运行总览。 |  | 100.00% |
