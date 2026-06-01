## whisper.cpp small Test Results

**Config**: model=small, language=zh, threads=4, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 10 | |
| 成功条数 | 2 | 归一化后完全匹配 |
| **成功率** | **20.00%** | 成功条数/总条数 |
| CER | 31.36% | 字符错误率 |
| 平均 RTF | 1.9261 | <1.0 表示快于实时 |
| P95 RTF | 2.0761 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| principal | 10 | 2 | **20.00%** | 31.36% | 1.9261 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| standard | 10 | 2 | **20.00%** | 31.36% | 1.9261 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| principal_002 | 切换到校长驾驶舱首页。 | 切換到校長駕駛艙手藝 | 70.00% |
| principal_005 | 打开校长驾驶舱里的学校运行总览页。 | 打開校長駕駛艙裡的學校運行總產業 | 68.75% |
| principal_006 | 看学校总览。 | 看學校總蘭 | 60.00% |
| principal_008 | 查询本周各年级学生出勤率。 | 查詢本周各年級學生出情侶 | 41.67% |
| principal_009 | 帮我看一下今天全校到校情况。 | 幫我看一下今天全笑到笑情況。 | 30.77% |
| principal_004 | 我想看一下今天的学校整体情况。 | 我想看一下今天的學校整體情況。 | 21.43% |
| principal_003 | 帮我打开学校运行总览。 | 帮我打开学校运行踪篮 | 20.00% |
| principal_010 | 我想查一下这周各年级的出勤率。 | 我想查一下这周各年级的初情率 | 14.29% |
