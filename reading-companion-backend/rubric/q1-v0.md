# Q1 rubric q1-v0

| 版本 | 日期 | 改了什么 | 为什么 |
|---|---|---|---|
| q1-v0 | 2026-11-08 | 建立规则、判定口径与例子引用的版本骨架 | 为 open coding 之后的人工评测提供可冻结的 rubric 身份 |

状态：**draft，不可用于正式判断或实验评分**。该文件已登记，后续规则改动另建版本。

## 适用范围

Q1 已生成 Highlight / Note 的质量判断、单元密度、漏标及单元备注。
具体判定规则、通过率分母、待核验项处理、多次判断的汇总口径均待人工确认。
本骨架不从旧标注自动推导规则，不改变现有 prompt 或阅读机制。

## 判定规则

待确认。正式版本需明确 pass / fail 的标准，及 Highlight 与 Note 的适用差异。
`star`、`needs_verification`、密度和漏标是否进入指标，也须明确后再发布。

## 正反例引用

暂空。仅登记批注引用：`batch_id / unit_id / marginalia_id`；人工漏标使用
`batch_id / unit_id / record_id`。不得粘贴书籍原文、批注正文或含原文的说明。
需要正文的私有例子放 `state/rubric_examples/<rubric_version>/`，不进 Git。

## 历史标注

首批标注使用 `open_coding`，表示没有 rubric，不能追认为 q1-v0。
