## Sherpa-ONNX transducer Test Results

**Config**: model=transducer, recognizer=online, decoding=greedy_search, hotwords=无热词, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 1 | |
| 成功条数 | 0 | 归一化后完全匹配 |
| **成功率** | **0.00%** | 成功条数/总条数 |
| CER | 16.67% | 字符错误率 |
| 平均 RTF | 0.1094 | <1.0 表示快于实时 |
| P95 RTF | 0.1094 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| principal | 1 | 0 | **0.00%** | 16.67% | 0.1094 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| standard | 1 | 0 | **0.00%** | 16.67% | 0.1094 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| principal_001 | 打开学校今日运行数据大屏。 | 打开学校今日运行数据 | 16.67% |
