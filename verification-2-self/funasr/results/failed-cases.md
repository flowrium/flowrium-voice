# 未匹配用例详情 (2pass / 无热词)

总计: 240 条, 未匹配: 32 条

| # | ID | 分类 | CER | 期望 | 实际 |
|---|---|---|---|---|---|
| 1 | director_019 | myvoice/director | 100.00% | 生成本年级周工作简报。 |  |
| 2 | teacher_006 | myvoice/teacher | 100.00% | 为今天第一节课发起点名。 |  |
| 3 | teacher_010 | myvoice/teacher | 100.00% | 查询本次作业完成率。 |  |
| 4 | staff_004 | myvoice/staff | 100.00% | 打开请假申请页面。 |  |
| 5 | staff_012 | myvoice/staff | 100.00% | 打开设备报修页面。 |  |
| 6 | staff_019 | myvoice/staff | 100.00% | 打开教职工通讯录。 |  |
| 7 | director_019 | standard/director | 20.00% | 生成本年级周工作简报。 | 生成本年吉州工作简报。 |
| 8 | teacher_007 | standard/teacher | 20.00% | 查询本周我的调课记录。 | 查询本周我的雕刻记录。 |
| 9 | director_019 | humanized/director | 20.00% | 生成本年级周工作简报。 | 生成本年吉州工作简报。 |
| 10 | teacher_007 | humanized/teacher | 20.00% | 查询本周我的调课记录。 | 查询本周我的雕刻记录。 |
| 11 | teacher_007 | myvoice/teacher | 20.00% | 查询本周我的调课记录。 | 查询本周我的雕刻记录。 |
| 12 | principal_007 | myvoice/principal | 14.29% | 对比本学期各年级成绩变化趋势。 | 对比本学7个年级成绩变化趋势。 |
| 13 | director_020 | myvoice/director | 11.11% | 返回主任工作台首页。 | 返回主任工作排首页。 |
| 14 | staff_020 | myvoice/staff | 11.11% | 返回教职工服务首页。 | 返回教职工服首页。 |
| 15 | teacher_016 | standard/teacher | 10.00% | 查看本周家校沟通记录。 | 查看本周驾校沟通记录。 |
| 16 | teacher_016 | humanized/teacher | 10.00% | 查看本周家校沟通记录。 | 查看本周驾校沟通记录。 |
| 17 | teacher_016 | myvoice/teacher | 10.00% | 查看本周家校沟通记录。 | 查看本周驾校沟通记录。 |
| 18 | director_007 | standard/director | 9.09% | 查看本年级数学成绩排名。 | 查看本年及数学成绩排名。 |
| 19 | teacher_004 | standard/teacher | 9.09% | 打开七年级一班学生名单。 | 打开7年级一班学生名单。 |
| 20 | director_007 | humanized/director | 9.09% | 查看本年级数学成绩排名。 | 查看本年及数学成绩排名。 |
| 21 | teacher_004 | humanized/teacher | 9.09% | 打开七年级一班学生名单。 | 打开7年级一班学生名单。 |
| 22 | principal_012 | myvoice/principal | 9.09% | 查看各班级综合评价排名。 | 查看的班级综合评价排名。 |
| 23 | director_003 | myvoice/director | 9.09% | 查询本周各班级迟到人数。 | 查询本周各班及迟到人数。 |
| 24 | director_009 | myvoice/director | 9.09% | 查看各班级纪律扣分统计。 | 查看的班级纪律扣分统计。 |
| 25 | teacher_004 | myvoice/teacher | 9.09% | 打开七年级一班学生名单。 | 打开7年级一班学生名单。 |
| 26 | principal_016 | myvoice/principal | 8.33% | 查看本月家校沟通情况统计。 | 查看本月驾校沟通情况统计。 |
| 27 | teacher_009 | myvoice/teacher | 8.33% | 查看未提交作业的学生名单。 | 查看为提交作业的学生名单。 |
| 28 | director_002 | standard/director | 7.69% | 查看今天本年级学生出勤情况。 | 查看今天本年及学生出勤情况。 |
| 29 | director_002 | humanized/director | 7.69% | 查看今天本年级学生出勤情况。 | 查看今天本年及学生出勤情况。 |
| 30 | principal_014 | myvoice/principal | 7.69% | 查看各学科教学任务完成情况。 | 查看个学科教学任务完成情况。 |
| 31 | principal_006 | myvoice/principal | 7.14% | 查看各年级最近一次考试平均分。 | 查看个年级，最近一次考试平均分。 |
| 32 | director_015 | myvoice/director | 7.14% | 查看未完成备课检查的教师名单。 | 查看为完成备课检查的教师名单。 |

## 错误类型分析

### 完全识别为空 (6 条)

- director_019 (myvoice/director): 期望 "生成本年级周工作简报。"
- teacher_006 (myvoice/teacher): 期望 "为今天第一节课发起点名。"
- teacher_010 (myvoice/teacher): 期望 "查询本次作业完成率。"
- staff_004 (myvoice/staff): 期望 "打开请假申请页面。"
- staff_012 (myvoice/staff): 期望 "打开设备报修页面。"
- staff_019 (myvoice/staff): 期望 "打开教职工通讯录。"

### 替换/插入/删除错误 (26 条)

- director_019 (standard/director):
  - 期望: 生成本年级周工作简报。
  - 实际: 生成本年吉州工作简报。
- teacher_007 (standard/teacher):
  - 期望: 查询本周我的调课记录。
  - 实际: 查询本周我的雕刻记录。
- director_019 (humanized/director):
  - 期望: 生成本年级周工作简报。
  - 实际: 生成本年吉州工作简报。
- teacher_007 (humanized/teacher):
  - 期望: 查询本周我的调课记录。
  - 实际: 查询本周我的雕刻记录。
- teacher_007 (myvoice/teacher):
  - 期望: 查询本周我的调课记录。
  - 实际: 查询本周我的雕刻记录。
- principal_007 (myvoice/principal):
  - 期望: 对比本学期各年级成绩变化趋势。
  - 实际: 对比本学7个年级成绩变化趋势。
- director_020 (myvoice/director):
  - 期望: 返回主任工作台首页。
  - 实际: 返回主任工作排首页。
- staff_020 (myvoice/staff):
  - 期望: 返回教职工服务首页。
  - 实际: 返回教职工服首页。
- teacher_016 (standard/teacher):
  - 期望: 查看本周家校沟通记录。
  - 实际: 查看本周驾校沟通记录。
- teacher_016 (humanized/teacher):
  - 期望: 查看本周家校沟通记录。
  - 实际: 查看本周驾校沟通记录。
- teacher_016 (myvoice/teacher):
  - 期望: 查看本周家校沟通记录。
  - 实际: 查看本周驾校沟通记录。
- director_007 (standard/director):
  - 期望: 查看本年级数学成绩排名。
  - 实际: 查看本年及数学成绩排名。
- teacher_004 (standard/teacher):
  - 期望: 打开七年级一班学生名单。
  - 实际: 打开7年级一班学生名单。
- director_007 (humanized/director):
  - 期望: 查看本年级数学成绩排名。
  - 实际: 查看本年及数学成绩排名。
- teacher_004 (humanized/teacher):
  - 期望: 打开七年级一班学生名单。
  - 实际: 打开7年级一班学生名单。
- principal_012 (myvoice/principal):
  - 期望: 查看各班级综合评价排名。
  - 实际: 查看的班级综合评价排名。
- director_003 (myvoice/director):
  - 期望: 查询本周各班级迟到人数。
  - 实际: 查询本周各班及迟到人数。
- director_009 (myvoice/director):
  - 期望: 查看各班级纪律扣分统计。
  - 实际: 查看的班级纪律扣分统计。
- teacher_004 (myvoice/teacher):
  - 期望: 打开七年级一班学生名单。
  - 实际: 打开7年级一班学生名单。
- principal_016 (myvoice/principal):
  - 期望: 查看本月家校沟通情况统计。
  - 实际: 查看本月驾校沟通情况统计。
- teacher_009 (myvoice/teacher):
  - 期望: 查看未提交作业的学生名单。
  - 实际: 查看为提交作业的学生名单。
- director_002 (standard/director):
  - 期望: 查看今天本年级学生出勤情况。
  - 实际: 查看今天本年及学生出勤情况。
- director_002 (humanized/director):
  - 期望: 查看今天本年级学生出勤情况。
  - 实际: 查看今天本年及学生出勤情况。
- principal_014 (myvoice/principal):
  - 期望: 查看各学科教学任务完成情况。
  - 实际: 查看个学科教学任务完成情况。
- principal_006 (myvoice/principal):
  - 期望: 查看各年级最近一次考试平均分。
  - 实际: 查看个年级，最近一次考试平均分。
- director_015 (myvoice/director):
  - 期望: 查看未完成备课检查的教师名单。
  - 实际: 查看为完成备课检查的教师名单。
