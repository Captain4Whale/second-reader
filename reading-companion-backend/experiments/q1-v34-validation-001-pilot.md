# Q1 rubric v3.4 Terra medium 试跑记录

记录ID：`Q1-RUBRIC-V34-VALIDATION-001-PILOT-001`；运行完成，等待用户确认，正式批次未启动。
协议补充：`Q1-RUBRIC-V34-VALIDATION-001-PROTOCOL-001`，在首次模型调用前追加；原预登记保持原样。

## 抽样与原文检查
- 种子20261116；候选先按原书坐标排序，一个random.Random实例依包法利、人类简史顺序shuffle，取1／2个。
- 包法利排除第一批、DIAG、第2批全部36个、第3批、全部已知上游单元；人类简史排除第一批、DIAG、检验集、验收集、u000037。
- 疑似原书注释按固定队列顺延至同层下一个未占用候选，逐次留痕；本次3个单元全文检查均通过，无替换。
- 候选队列、来源哈希和各项空交集见[试跑清单](unit-sets/q1-v34-pilot-001.json)。
- 包法利u000138：原书序位139/352，第二部第8章；人类简史u000019：23/245，第二章；u000139：143/245，第十三章。

## 每单元数量与历史均值
所有值依次为Note／Highlight；历史每书每组8个单元，试跑单元与DIAG不同。

| 试跑单元 | 本次N/H | DIAG A1 Luna medium均值 | DIAG A2 Luna medium均值 | DIAG B Sol high均值 |
|---|---:|---:|---:|---:|
| bovary/u000138 | 0/0 | 1.250/0.500 | 1.125/0.500 | 2.000/0.750 |
| sapiens/u000019 | 2/2 | 1.375/0.750 | 1.375/0.875 | 1.750/1.750 |
| sapiens/u000139 | 2/0 | 1.375/0.750 | 1.375/0.875 | 1.750/1.750 |

合计4条Note、2条Highlight，全部来自人类简史。整体每单元1.333 N／0.667 H；DIAG A1为1.3125／0.625，A2为1.25／0.6875，B为1.875／1.25。整体数量与Luna相近、低于Sol；这不是质量或模型能力结论。包法利0批注是正常解析的空marginalia，不是失败吞空，未重跑。

## 每次调用
配置均为digest.v24、gpt-6.1-terra、reasoning_effort=medium、temperature=0.2、max_output_tokens=4096；完整历史记忆不更新。

| 单元 | 实际返回模型标识 | finish_reason | 输入token | 输出token | reasoning token | 重试/修复 |
|---|---|---|---:|---:|---:|---|
| bovary/u000138 | gpt-6.1-terra | tool_calls | 10078 | 158 | 0 | 无 |
| sapiens/u000019 | gpt-6.1-terra | tool_calls | 10141 | 652 | 0 | 无 |
| sapiens/u000139 | gpt-6.1-terra | tool_calls | 8851 | 375 | 0 | 无 |

总输入29,070、输出1,185（报告reasoning为0），总token30,255。按输入$1／输出$5每百万计参考费用 **$0.034995**，实际扣费未知。
三次输出分别只占4096上限的3.86%、15.92%、9.16%；未见reasoning占据大部分上限，未截断。reasoning=0是上游返回字段，并非独立验证内部推理为零。实际模型标识也只代表响应元数据。

## 解析与证据
- 三个原始工具payload均由现有validate_digest_result验证通过；理解和回应字段有效。6条批注的原文锚点均精确匹配。
- 所有逻辑请求哈希与实际捕获一致，完整system/user与预冻结输入一致，记忆ID、顺序、正文核对通过。
- 3次逻辑／物理请求；没有重试、配额重试、修复、failover或模型调用错误；473个原历史文件前后哈希不变。
- 一条Note尾部空白被现有解析器trim（97→96字符），正文内容未改；Highlight的null内容按既有规则归一化为空串。原始响应完整保留。
- 独立审查最初按原始Note逐字节相等断言过严，在确认仅末尾空白归一化后按既有解析规则复核通过；没有为此修改解析器或重新调用模型。
- 全部试跑批注正文：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/pilot/annotations.md`。
- 逐调用request/response和result：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/pilot/outputs`。
- 汇总与独立验证：`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/pilot/summary.json`、`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion/reading-companion-backend/state/experiments/Q1-RUBRIC-V34-VALIDATION-001/pilot/validation.json`。

## 已固定的稳定性复判抽法
- 种子20261122；正式26单元所有Note生成成功后、人工标注前立即抽15条，试跑不进入总体。
- 唯一身份为book、unit_id、marginalia_id。后者沿用export_fixed_history_digest.py的unit_id-replay-mNNN，NNN是完整marginalia数组的1起算序号，含Highlight占位。
- 初始化random.Random(20261122)，先choice([bovary,sapiens])决定哪本取8条、另一本7条；各书Note按上述身份字典序排序，依书序各shuffle一次。
- 每书先取min(数量,配额)；不足15时按固定书序从剩余容量补足；总量不足15则报错停下。按书序连接入选身份，最后用同一随机实例shuffle呈现顺序。
- 固定完整输入身份清单、各正式result哈希及最终名单。不得利用人工判定或标签筛选、排序。抽样后保持隐藏旧判定，首次整批标注完成至少7天后盲重判。
- 翻转率＝同一Note首次完成的总体通过/不通过与盲重判结果不同的条数／15；阈值≤15%，即15条中至多2条翻转。
- 实现为scripts/run_q1_v34_pilot.py的stability_sample；7种平衡/缺量情形、输入乱序一致性、重复与不足15条拒绝检查通过。

## 和指令／初始方案的出入
- 经用户确认，分层依据由最初方案的ID区间改为原书坐标顺序。
- 经用户指定，分支名由codex/task3-new-batch改为codex/261115-new-batch。
- 未变更模型、prompt、medium、4096上限，也未扩大试跑数量；没有正式生成、质量标注或rubric冻结结论。

## 验证、环境与提交边界
- 45项既有Digest重建、调用与A1工具测试通过；试跑队列独立复算、全部排除交集、解析、请求与源文证据验证通过。
- 独立工作树补齐1个经内容哈希验证的私有prompt资产；为完整台账核验建立116个现有历史产物的只读用途链接，均位于忽略目录。不复制凭据，不改历史产物，当前试跑输出和job记录独立本地保存。
- 任务注册器已登记并结束bgjob_q1_v34_validation_001_pilot；run_ledger登记为review_pending，仍未晋升为正式质量证据。
- 提交仅为试跑/协议记录、试跑清单、必要运行和稳定性抽样脚本、试跑台账。既有预登记、检验/验收清单、rubric、表单、scorings.jsonl、INDEX及任务二文件均不改。
