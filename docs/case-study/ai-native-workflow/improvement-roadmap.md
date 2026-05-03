# Improvement Roadmap

Purpose: 按 operator-side AI Harness 能力环节规划未来最值得补强的 AI 协同能力。
Use when: 制定个人 AI-native workflow 学习计划、决定下一阶段方法论升级、把 Reading Companion 经验转成可复用系统。
Not for: Reading Companion 当前任务状态、产品机制权威、运行时计划、评测结果权威或简历 bullet。

Boundary statement: 本路线图关注如何更好地驾驭现有 AI / coding agent 工具，不是如何开发 agent framework。

## North Star

下一阶段目标不是让每个任务更重，而是让高不确定、高成本、高风险的 AI 协作任务在开始前就拥有清晰 harness：

- 目标有契约。
- 上下文有路由。
- 执行有阶段。
- 证据有有效性边界。
- 工具有权限治理。
- 过程有可观测链路。
- 经验能进入下一轮结构。

## 1. 目标与意图控制

### Current state

Reading Companion 已经能把产品目的、机制边界和评测目标写进稳定文档，避免 AI 协作漂回 summary engine 或局部机制迷恋。

### Upgrade

建立 pre-task intent contract：每个复杂任务启动前写清 question、done criteria、non-goals、decision owner、stop / retry / abandon condition。

### Success signal

高成本任务不再以“继续优化”开头，而是以可判断、可停止、可复查的任务契约开头。

## 2. 上下文治理

### Current state

项目内 repo-first memory 很强：load matrix、source-of-truth map、current-state、registry、decision log 都已经形成。

### Upgrade

把项目内上下文治理升级为个人级 context governance：

- 区分 project-specific rules 和 personal AI workflow rules。
- 为跨 repo / 跨工具任务设计 shared entry point。
- 建立 context budget habit：先索引和检索，再加载全文。

### Success signal

换项目或换 AI 工具时，方法论不从零开始；只需要替换项目特定上下文。

## 3. 执行可靠性

### Current state

Reading Companion 已经有 phased implementation、job registry、watchdogs、staged artifacts 和 long-running eval recovery。

### Upgrade

沉淀 reusable multi-agent planning / execution pattern：

- 主线程负责目标、决策和整合。
- Side context / subagent 负责高体积探索。
- Deterministic scripts 负责可重复流程。
- Run dossier 负责状态和证据。

### Success signal

复杂任务可以在 agent 中断、上下文压缩或跨线程交接后继续推进，而不是重新考古。

## 4. 证据与评测

### Current state

项目已经擅长事后解释 eval：dual diagnosis、invalidated evidence、diagnostic evidence、formal evidence 都有明确概念。

### Upgrade

把 evidence contract 前置化，并增强人类校准：

- 评测前定义 objective、dataset、validity criteria、decision rule。
- LLM-as-judge 必须说明可判断范围和人工校准点。
- 高影响结果必须写 post-run interpretation。

### Success signal

每个高成本 eval 都能回答：它测了什么、证据是否有效、结果由什么导致、下一步采用/推迟/否决/重跑的理由是什么。

## 5. 工具、环境与权限控制

### Current state

项目内有较强的 backend runtime、validation scripts、job registry 和 artifact hygiene，但个人级 AI tool governance 还不够显式。

### Upgrade

建立 lightweight tool governance：

- 工具分类：read、write、execute、browse、judge、deploy、delete。
- 权限分类：auto-allowed、ask-first、forbidden。
- 风险规则：credentials、destructive commands、external systems、model/provider upgrades。
- 环境记录：cwd、dependencies、outputs、sandbox assumptions。

### Success signal

AI 工具使用不再靠临场判断；高风险操作有稳定审批规则，模型/provider 变化有证据和回退。

## 6. 可观测与交接

### Current state

Reading Companion 的 artifact provenance 很强，但 visual / queryable observability 还弱。

### Upgrade

建立轻量 run dossier 和 execution-path inspection：

- 每个关键 run 有 command、input、model/provider、output、artifact、eval、interpretation、decision。
- Long-running jobs 有 active view、check command、recovery posture。
- 重要评审可以从 final result 回溯到 run path。

### Success signal

未来自己或另一个 agent 可以从 run dossier 恢复任务，而不是从聊天记录里找线索。

## 7. 复盘与学习

### Current state

项目已经通过 mechanism pattern ledger、decision log、case-study docs 将经验从 chat 迁移到 repo。

### Upgrade

建立 source-monitoring habit 和 learning disposition：

- 每月或每个项目阶段检查官方 docs、实践者框架和高信号社区讨论。
- 每条新做法标记为 durable principle、current tactical 或 speculative signal。
- 每条项目内经验标记为 adopt、test、defer、reject、monitor。

### Success signal

AI 协作方法持续进化，但不会被新工具信号带偏；只有经验证的做法进入稳定规则。

## Highest-Leverage Focus

下一阶段最高杠杆不是新增更多文档，而是把三个动作前置化：

1. Pre-task intent contract。
2. Pre-run evidence contract。
3. Post-run interpretation。

这三个动作能同时改善目标清晰度、上下文选择、执行恢复、评测解释和下一轮学习，是从“项目内证据系统”升级到“个人 AI Harness”的最小可行路径。
