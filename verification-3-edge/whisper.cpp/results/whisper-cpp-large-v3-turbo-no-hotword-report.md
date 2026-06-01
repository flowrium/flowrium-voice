## whisper.cpp large-v3-turbo Test Results

**Config**: model=large-v3-turbo, language=zh, threads=4, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 10 | |
| 成功条数 | 9 | 归一化后完全匹配 |
| **成功率** | **90.00%** | 成功条数/总条数 |
| CER | 0.85% | 字符错误率 |
| 平均 RTF | 7.0880 | <1.0 表示快于实时 |
| P95 RTF | 6.9259 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| principal | 10 | 9 | **90.00%** | 0.85% | 7.0880 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| standard | 10 | 9 | **90.00%** | 0.85% | 7.0880 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| principal_001 | 打开学校今日运行数据大屏。 | 大开学校今日运行数据大屏。 | 8.33% |
