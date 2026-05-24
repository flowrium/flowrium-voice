## Sherpa-ONNX sensevoice Test Results

**Config**: model=sensevoice, hotwords=无热词, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 3 | |
| 成功条数 | 3 | 归一化后完全匹配 |
| **成功率** | **100.00%** | 成功条数/总条数 |
| CER | 0.00% | 字符错误率 |
| 平均 RTF | 0.0625 | <1.0 表示快于实时 |
| P95 RTF | 0.0605 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| principal | 3 | 3 | **100.00%** | 0.00% | 0.0625 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| standard | 3 | 3 | **100.00%** | 0.00% | 0.0625 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| — | — | — | — |
