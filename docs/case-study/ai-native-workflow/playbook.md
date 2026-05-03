# AI-Native Workflow Playbook

Purpose: 将 Reading Companion 中可复用的 operator-side AI Harness 方法整理成操作手册。
Use when: 启动复杂 AI 产品任务、组织多轮 AI 协作、设计评测闭环、准备交接或复盘。
Not for: 产品运行时权威、机制规格、任务状态更新、简历 bullet 或对任何单一工具的固定教程。

This playbook is methodology guidance. It should be adapted to task risk: small changes should stay light; high-cost, high-risk, ambiguous work should use more of the checklist.

Boundary statement: 这份手册面向“如何驾驭现有 AI / coding agent 工具”，不是“如何开发一个 agent framework”。

## How To Use This Playbook

每个复杂 AI 协作任务都先问两个问题：

- 这个环节本质上要治理什么？
- 为了让 AI 不漂移、不失忆、不误判、不难以交接，我需要先设计什么机制？

小任务可以使用文末的 Lightweight Mode。高风险、高成本、高不确定性的任务应使用 Full Harness Mode。

## 1. 目标与意图控制

### 目的

把模糊需求变成 AI 可以执行、判断和停止的任务契约。不要让 AI 在目标还没定清楚时直接进入执行。

### 启动前问题

- 这轮到底要回答什么问题？
- 这是澄清、比较、实现、评测、修复、文档、交接，还是复盘？
- 什么算完成？
- 什么明确不做？
- 谁拥有最终判断权？
- 什么情况应该停止、重跑、缩小范围或放弃路线？

### 执行中检查

- AI 是否开始解决一个没有被明确授权的问题？
- 是否出现“看似相关但其实偏离本轮目标”的扩展？
- 是否需要把目标写进稳定文档或 decision log，而不是只留在 chat？

### 完成证据

- 一句话目标。
- Success criteria。
- Scope / non-goals。
- Decision owner。
- Stop / retry / abandon condition。

Reading Companion pattern: product purpose was stabilized through [Product Overview](../../product-overview.md) and [Backend Reader Evaluation](../../backend-reader-evaluation.md), then later mechanism work had to align to that purpose.

## 2. 上下文治理

### 目的

设计信息的维护和输入方式，让 AI 在正确时间拿到正确信息，而不是靠聊天记忆或一次性全文灌入。

### 启动前问题

- 哪些信息是长期规则、当前状态、历史决策、评测证据、临时探索？
- 这轮 AI 应该先看哪个索引或路由入口？
- 哪些信息必须进入主上下文？
- 哪些信息应该按需检索？
- 哪些探索适合放进隔离上下文或 subagent？

### 执行中检查

- 是否把代码可检索的信息重复写进上下文？
- 是否让过期文档或聊天记忆压过 source of truth？
- 是否在 compaction / handoff 后重新注入了关键事实和约束？
- 是否把 durable facts 写回正确文档，而不是留在 chat？

### 完成证据

- 已确认的 source-of-truth entry points。
- 本轮使用的上下文清单。
- 新增或更新的 durable information 位置。
- 未进入主上下文但可按需检索的材料。

Reading Companion pattern: [AGENTS.md](../../../AGENTS.md) defines load matrix and routing; [Source Of Truth Map](../../source-of-truth-map.md) defines durable information locations; [Claude Code context-management research](../../../reading-companion-backend/docs/research/claude_code_context_management_research_20260412.md) imports index-first memory, compaction plus re-injection, and side-context isolation.

## 3. 执行可靠性

### 目的

把 AI 的执行从一次性对话变成可分阶段、可恢复、可交接的工程流程。

### 启动前问题

- 这项任务能不能拆成阶段产物？
- 哪些步骤应由确定性脚本或测试控制，哪些步骤适合 AI 判断？
- 哪些文件、模块或 artifact 由本轮任务负责？
- 失败后能否从中间阶段恢复？
- 长任务是否需要 job record、run id、watchdog 或 registry entry？

### 执行中检查

- 是否按计划分阶段推进，而不是让 AI 一次性改到底？
- 是否记录了命令、输入、输出路径和恢复方式？
- 是否出现可复用 artifact，应避免无意义重跑？
- 是否需要把当前进展写入 current-state / registry / handoff？

### 完成证据

- 执行计划和 landed stages。
- Run id / job id / command / output path。
- Validation command。
- Recovery posture。
- Generated artifacts 的保留或忽略策略。

Reading Companion pattern: `bundle -> judge -> merge` made evaluation restarts evidence-based; job registry and watchdogs made long-running work recoverable across agent handoffs.

## 4. 证据与评测

### 目的

把“结果看起来怎么样”转成可复查、可校准、可改进的 evidence system。

### Evidence Contract Template

```markdown
## Evidence Contract

Question:
- What exact decision or uncertainty should this task resolve?

Expected artifacts:
- Code paths:
- Docs:
- Eval outputs:
- Logs / traces:
- Screenshots / reports:

Validity criteria:
- What must be true for the evidence to count?
- What would invalidate the run?
- What must be source-grounded or reproducible?

Decision rule:
- If evidence shows X, we will do Y.
- If evidence shows Z, we will defer / rerun / redesign.

Stop condition:
- When do we stop expanding scope?
- When do we abandon this route?
```

### 执行中检查

- 这个 run 是否真的测试了想测试的问题？
- LLM-as-judge 可以判断什么，不能判断什么？
- 是否需要 human calibration？
- 结果属于 formal evidence、diagnostic evidence、historical evidence，还是 invalidated evidence？

### Post-Run Interpretation Template

```markdown
## Post-Run Interpretation

Run:
- run id:
- command:
- input dataset / split:
- model / provider:

Top-line result:
- What happened?

Validity:
- Did the run test the intended question?
- Any invalidation risks?
- Any missing artifacts?

Causal read:
- What likely caused the result?
- Is it mechanism, dataset, harness, provider, or operator issue?

Decision:
- adopt now:
- defer:
- reject / invalidate:
- rerun condition:

Follow-up:
- code:
- docs:
- eval:
- task registry / current-state if applicable:
```

### 完成证据

- Evidence contract。
- Eval outputs / reports。
- Post-run interpretation。
- Formal / diagnostic / invalidated status。
- Follow-up action or defer reason。

Reading Companion pattern: [Backend Reader Evaluation](../../backend-reader-evaluation.md) defines dual diagnosis and source-span rules; [Evidence Catalog](../../../reading-companion-backend/docs/evaluation/evidence_catalog.md) separates current, historical, superseded, failed, and invalidated evidence.

## 5. 工具、环境与权限控制

### 目的

控制 AI 能调用什么、在哪里调用、出错或越权时怎么办。

### 启动前问题

- 这轮需要哪些工具：read、edit、shell、browser、MCP、eval runner、LLM judge？
- 哪些操作可以自动执行，哪些需要人工审批？
- 是否涉及凭证、生产环境、不可逆动作或外部系统？
- 依赖、工作目录、输出目录和环境假设是否明确？

### 执行中检查

- 工具失败、超时、空输出是否被正确识别？
- AI 是否在错误目录或错误权限下执行？
- 是否把高风险操作交给模型自律，而不是规则或审批？
- 模型/provider 切换是否记录原因和回退方式？

### 完成证据

- Tool / permission boundary。
- Command and environment notes。
- Credential and sandbox assumptions。
- Model/provider config when relevant。
- Any approval or escalation decision。

## 6. 可观测与交接

### 目的

让 AI 协作过程本身可看见、可解释、可交接。

### 启动前问题

- 这项任务需要哪些 run ids、artifact ids、trace links 或 log paths？
- 下一个 agent 接手时最需要知道什么？
- 哪些证据是可信的，哪些只是 diagnostic？
- 失败后从哪里恢复？

### 执行中检查

- 是否能把 final result 追溯到 run、input、command、artifact、review decision？
- 是否记录了 blocked items 和 next action？
- 是否把 active state 写进 current-state / registry，而不是只写在聊天里？
- 是否需要 run dossier？

### 完成证据

- Run dossier or equivalent index。
- Current state / task registry update when applicable。
- Artifact provenance。
- Recovery command。
- Clear next action。

Reading Companion pattern: [Current State](../../current-state.md) records active jobs, commands, expected outputs, and recovery posture; [Task Registry](../../tasks/registry.md) links active tasks to decisions, jobs, and evidence; [Decision Log](../../history/decision-log.md) preserves hard-to-reconstruct inflections.

## 7. 复盘与学习

### 目的

把一次 AI 协作的经验变成下一次 AI 协作的结构。

### 启动前问题

- 这次暴露了什么真实失败或反复成本？
- 什么机制能更早发现它？
- 这是 durable principle、current tactical，还是 speculative signal？
- 它应该成为规则、checklist、test、eval case、script、decision log、roadmap，还是被丢弃？

### 执行中检查

- 是否在写 vague lesson，例如“以后小心”？
- 是否把可自动化的规则长期塞进上下文？
- 是否给每个 high-value insight 一个 disposition？
- 是否需要进入 source monitoring，而不是稳定规则？

### 完成证据

- Failure-backed rule, checklist item, test, script, eval case, decision log entry, roadmap item, or explicit defer reason。
- Removed or avoided aspirational context rule。
- Clear link back to the failure or opportunity that justified the lesson。

Reading Companion pattern: [Mechanism Pattern Ledger](../../implementation/new-reading-mechanism/mechanism-pattern-ledger.md) stores strengths, failure modes, dispositions, and next actions; `DEC-035` and `DEC-036` require evaluation to preserve portable patterns and close the loop to implementation or deferment.

## Lightweight Mode

Not every task needs the full harness. For small tasks, use this compressed version:

- Intent: one-sentence question, done criteria, and non-goal。
- Context: required docs or search entry points only。
- Execution: scoped edit and validation command。
- Evidence: final diff plus test result。
- Learning: only write a new rule if a real failure surfaced。

## Full Harness Mode

Use the full playbook when the task has any of these signs:

- ambiguous product direction
- new architecture or mechanism boundary
- long-running eval or dataset job
- LLM-as-judge or benchmark promotion
- model/provider changes
- cross-agent handoff
- irreversible operation
- broad generated artifacts
- high risk of confusing diagnostic evidence with formal evidence

The principle is simple: make the harness proportional to uncertainty and blast radius.
