# 验证一：三方云 API

## 目标

确认校长语音指令场景下转写是否可行，建立准确率基准线。

## 厂商总览

第一批：

- [阿里云](./aliyun/README.md)
- [讯飞开放平台](./iflytek/README.md)

第二批：

- [火山引擎](./volcengine/README.md)
- [腾讯云](./tencent-cloud/README.md)
- [百度智能云](./baidu-cloud/README.md)

## 横向对比

- [厂商对比表](./comparison.md)

## 关注维度

- ASR 实时转写与录音文件转写能力
- 热词、自定义词表、领域适配能力
- 中英混合、数字、专有名词识别效果
- API 易用性、鉴权方式、SDK 质量
- 并发、限流、稳定性和错误码设计
- 价格模型、免费额度和测试门槛
- 音频格式、采样率、时长限制

## 目录结构

- `comparison.md`：横向对比与评估建议
- `aliyun/`：阿里云产品介绍
- `iflytek/`：讯飞开放平台产品介绍
- `volcengine/`：火山引擎产品介绍
- `tencent-cloud/`：腾讯云产品介绍
- `baidu-cloud/`：百度智能云产品介绍

## 详细计划

见 [docs/verification-plan.md](../docs/verification-plan.md)
