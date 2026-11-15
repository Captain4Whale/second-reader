# Q1 rubric v3.4 正式生成记录（盲标前）

记录：`Q1-RUBRIC-V34-VALIDATION-001-RESULT-001`；补充诊断：`Q1-RUBRIC-V34-VALIDATION-001-REASONING-DIAG-001`。

26单元串行生成完成，等待人工盲标。本文没有批注正文、引用原文、质量评价或稳定性复判名单。

## 范围与配置

- [已确认检验集26单元](unit-sets/q1-v34-validation-001.json)；[人类简史验收集13单元](unit-sets/q1-v34-acceptance-sapiens-001.json)未运行。包法利第3批不整理、不运行。
- 固定原历史上下文，只重跑Digest；gpt-6.1-terra、medium、digest.v24、temperature=0.2、max_output_tokens=4096。相对原运行changed_variables为model。
- 试跑和high诊断均排除正式统计；未补单元、未为凑数重跑。原清单、rubric、表单、scorings、INDEX不改。

## 数量与调用

| 书 | 单元数 | Note | Highlight |
|---|---:|---:|---:|
| bovary | 13 | 18 | 3 |
| sapiens | 13 | 28 | 7 |
| 合计 | 26 | 46 | 10 |

Note门槛30–80已通过。输入253,511、输出11,496（其中上游报告reasoning 0），总token 265,007；参考费用 **$0.310991**，实际扣费未知。

| 书/单元 | Note | Highlight | 返回模型 | finish_reason | 输入token | 输出token | reasoning | 重试 |
|---|---:|---:|---|---|---:|---:|---:|---:|
| bovary/u000032 | 3 | 0 | gpt-6.1-terra | tool_calls | 10421 | 620 | 0 | 0 |
| bovary/u000043 | 1 | 0 | gpt-6.1-terra | tool_calls | 8849 | 319 | 0 | 0 |
| bovary/u000089 | 1 | 0 | gpt-6.1-terra | tool_calls | 9625 | 294 | 0 | 0 |
| bovary/u000109 | 1 | 0 | gpt-6.1-terra | tool_calls | 9996 | 306 | 0 | 0 |
| bovary/u000145 | 0 | 0 | gpt-6.1-terra | tool_calls | 10017 | 160 | 0 | 0 |
| bovary/u000161 | 3 | 0 | gpt-6.1-terra | tool_calls | 10453 | 688 | 0 | 0 |
| bovary/u000175 | 3 | 2 | gpt-6.1-terra | tool_calls | 10400 | 720 | 0 | 0 |
| bovary/u000177 | 1 | 0 | gpt-6.1-terra | tool_calls | 9461 | 276 | 0 | 0 |
| bovary/u000195 | 1 | 0 | gpt-6.1-terra | tool_calls | 9657 | 369 | 0 | 0 |
| bovary/u000239 | 0 | 1 | gpt-6.1-terra | tool_calls | 10145 | 316 | 0 | 0 |
| bovary/u000262 | 1 | 0 | gpt-6.1-terra | tool_calls | 8418 | 262 | 0 | 0 |
| bovary/u000281 | 1 | 0 | gpt-6.1-terra | tool_calls | 8989 | 268 | 0 | 0 |
| bovary/u000329 | 2 | 0 | gpt-6.1-terra | tool_calls | 9626 | 368 | 0 | 0 |
| sapiens/u000027 | 1 | 0 | gpt-6.1-terra | tool_calls | 8742 | 323 | 0 | 0 |
| sapiens/u000033 | 2 | 0 | gpt-6.1-terra | tool_calls | 10783 | 497 | 0 | 0 |
| sapiens/u000048 | 2 | 0 | gpt-6.1-terra | tool_calls | 9035 | 475 | 0 | 0 |
| sapiens/u000061 | 2 | 1 | gpt-6.1-terra | tool_calls | 9858 | 557 | 0 | 0 |
| sapiens/u000094 | 1 | 1 | gpt-6.1-terra | tool_calls | 9064 | 405 | 0 | 0 |
| sapiens/u000125 | 3 | 0 | gpt-6.1-terra | tool_calls | 10062 | 547 | 0 | 0 |
| sapiens/u000128 | 3 | 1 | gpt-6.1-terra | tool_calls | 10478 | 687 | 0 | 0 |
| sapiens/u000148 | 2 | 0 | gpt-6.1-terra | tool_calls | 9299 | 381 | 0 | 0 |
| sapiens/u000152 | 2 | 0 | gpt-6.1-terra | tool_calls | 10237 | 387 | 0 | 0 |
| sapiens/u000165 | 2 | 1 | gpt-6.1-terra | tool_calls | 10356 | 517 | 0 | 0 |
| sapiens/u000176 | 2 | 0 | gpt-6.1-terra | tool_calls | 8380 | 393 | 0 | 0 |
| sapiens/u000183 | 3 | 1 | gpt-6.1-terra | tool_calls | 10132 | 623 | 0 | 0 |
| sapiens/u000189 | 3 | 2 | gpt-6.1-terra | tool_calls | 11028 | 738 | 0 | 0 |

全部26个输出由现有代码正常解析；56条批注精确锚点通过；逐请求哈希、完整system/user及历史记忆一致。无模型报错、重试、修复、failover或截断。473个历史文件未变。

## 试跑断言说明与正式归一化记录

- 试跑sapiens/u000139第1条Note：原始tool_calls[-1].args.marginalia[0].content与result.marginalia[0].content的独立全等断言失败。原始末尾恰多一个U+0020；97→96字符，289→288 UTF-8字节；其余字符逐字相同，source_quote不变。
- 这不是生产解析错误。已有llm_calls._clean_text在空白折叠后strip；原始值去掉该末尾空格即精确等于结果。接受的是既有行为，没有改解析器或重跑。此前最终汇报漏提此差异，本次补记。
- 正式每处归一化均留逐条回执；原始/结果全文仅在state，下面仅列字段与非正文差异。非空白变更拒绝。

| 书/单元 | 字段（0起算） | 规则 | 字符数 | 差异代码点 |
|---|---|---|---|---|
| bovary/u000089 | marginalia[0].content | existing_clean_text_whitespace | 71→70 | delete U+0020→∅ |
| bovary/u000175 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| bovary/u000175 | marginalia[1].content | highlight_null_to_empty | null→0 | null→空串 |
| bovary/u000239 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| bovary/u000262 | marginalia[0].content | existing_clean_text_whitespace | 62→61 | delete U+0020→∅ |
| bovary/u000329 | marginalia[0].content | existing_clean_text_whitespace | 80→79 | delete U+0020→∅ |
| sapiens/u000061 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| sapiens/u000094 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| sapiens/u000128 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| sapiens/u000165 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| sapiens/u000183 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| sapiens/u000189 | marginalia[0].content | highlight_null_to_empty | null→0 | null→空串 |
| sapiens/u000189 | marginalia[1].content | highlight_null_to_empty | null→0 | null→空串 |

## high补充诊断与已知局限

仅sapiens/u000019追加一次high调用，其他配置和逻辑请求内容与试跑一致。实际模型gpt-6.1-terra，finish_reason=tool_calls，输入10141、输出660、reasoning 0；无重试、截断或解析错误。参考费用$0.013441，单列且排除所有统计。

- **medium下上游报告的reasoning为0**；本次high诊断也报告0。不能据此确认内部推理量、effort实际执行或上游计数实现。实际模型标识仅代表响应元数据。正式仍用medium。
- 预登记的14%／73%来自v1＋人工裁决换算到v2，Terra居中只是预期。预计联想／其他写法很少的局限保留；未查看正式质量，未对此进行实测分类。

## 稳定性抽样及冻结条件

- 按PROTOCOL-001、种子20261122，在全部正式Note生成后、人工标注前抽15条；尽量两书各半，随机分配8／7，缺量按协议补足。名单和原总体/各结果哈希已固定，独立复算通过；不在报告或实验日志中暴露入选身份。
- 名单固定时间：2026-11-15T12:52:23.316340+00:00。公开元数据回执：`state/experiments/Q1-RUBRIC-V34-VALIDATION-001/formal/stability-receipt.json`。
- 初次整批标注完成至少7天后，盲重判；翻转率≤15%（15条至多2条）。本任务未创建标注会话或读取任何新判定。
- 原冻结条件不变：第一印象不一致率≤15%；rubric未覆盖≤2条；拿不准≤15%；其他写法仅报数且逐条回看。

## 私有输出与验证

- 全部正式Note与Highlight正文：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/formal/annotations.md`。
- 逐调用原始请求/响应/解析结果：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/formal/outputs`。
- 归一化原值与逐条编辑记录：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/formal/normalizations.json`。
- 数量/调用/用量：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/formal/summary.json`；独立核验：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/formal/verification.json`。
- 45项既有测试通过，归一化接受/拒绝检查通过；协议清单哈希、逐调用用量交叉核对、串行时序、源文件不变、稳定性随机复算均通过。

## 与初始方案的出入及判断

- 经确认，分层由ID区间改为原书坐标顺序；分支由codex/task3-new-batch改为codex/261115-new-batch。
- 按本次授权新增一次high诊断，不改变正式medium，也不将诊断混入统计。原始输出保留；只接受现有解析器的空白及Highlight null归一化并逐条登记。
- 价格按输入$1、输出$5每百万token估算，reasoning已经包含在输出，不重复计费；没有实际账单证据。
- 未修改模型客户端、prompt、rubric、表单、scorings、INDEX生成器或冻结清单；未进行标注、质量评价、冻结判断、推送或合并。
- 本批只承接源文无关实验说明及运行台账；共享current-state/任务注册表沿用先前隔离约定，不改并行任务文件。没有产品/机制方向变更，不新增decision-log。
