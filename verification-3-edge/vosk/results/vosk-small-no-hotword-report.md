## Vosk small Test Results

**Config**: model=small, model_path=/Users/lixiaofeng/Code/github/flowrium-voice/verification-3-edge/vosk/models/vosk-model-small-cn-0.22, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 5 | |
| 成功条数 | 3 | 归一化后完全匹配 |
| **成功率** | **60.00%** | 成功条数/总条数 |
| CER | 4.84% | 字符错误率 |
| 平均 RTF | 0.5674 | <1.0 表示快于实时 |
| P95 RTF | 0.6102 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| principal | 5 | 3 | **60.00%** | 4.84% | 0.5674 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| standard | 5 | 3 | **60.00%** | 4.84% | 0.5674 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| principal_005 | 打开校长驾驶舱里的学校运行总览页。 | 打开 校长 驾驶舱 里 的 学校 运行 总揽 夜 | 12.50% |
| principal_003 | 帮我打开学校运行总览。 | 帮 我 打开 学校 运行 总揽 | 10.00% |
