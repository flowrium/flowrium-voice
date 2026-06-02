## whisper.cpp base Test Results

**Config**: model=base, language=zh, threads=4, manifests=/Users/lixiaofeng/Code/github/flowrium-voice/audio/standard/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/humanized/manifest.csv, /Users/lixiaofeng/Code/github/flowrium-voice/audio/myvoice/manifest.csv

### Overall
| Metric | Value | Note |
| --- | --- | --- |
| 测试总数 | 10 | |
| 成功条数 | 1 | 归一化后完全匹配 |
| **成功率** | **10.00%** | 成功条数/总条数 |
| CER | 33.05% | 字符错误率 |
| 平均 RTF | 0.7339 | <1.0 表示快于实时 |
| P95 RTF | 0.9205 | |

### By Role
| Role | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| principal | 10 | 1 | **10.00%** | 33.05% | 0.7339 |

### By Version
| Version | Count | 成功数 | **成功率** | CER | Avg RTF |
| --- | --- | --- | --- | --- | --- |
| standard | 10 | 1 | **10.00%** | 33.05% | 0.7339 |

### Failed Cases (top 8)
| ID | Expected | Actual | CER |
| --- | --- | --- | --- |
| principal_005 | 打开校长驾驶舱里的学校运行总览页。 | 打開校長駕駛倉裡的學校運行總來業 | 68.75% |
| principal_002 | 切换到校长驾驶舱首页。 | 切換到校長駕石艙首頁。 | 60.00% |
| principal_003 | 帮我打开学校运行总览。 | 幫我打開學校運行總覽 | 60.00% |
| principal_006 | 看学校总览。 | 看學校中藍 | 60.00% |
| principal_008 | 查询本周各年级学生出勤率。 | 查詢本週各年級學生出情率 | 41.67% |
| principal_009 | 帮我看一下今天全校到校情况。 | 幫我看一下今天全笑到笑情況。 | 30.77% |
| principal_007 | 查看今天全校学生到校情况。 | 查看今天全校學生到校情況 | 16.67% |
| principal_001 | 打开学校今日运行数据大屏。 | 打开学校今日运行数据大评。 | 8.33% |
