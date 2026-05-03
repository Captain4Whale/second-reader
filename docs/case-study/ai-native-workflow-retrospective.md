# AI-Native Workflow Retrospective

Purpose: 作为 Reading Companion case study 的入口，概括 operator-side AI Harness 方法论，并指向更细的项目总结、外部调研、操作手册和改进路线。
Use when: 复盘个人 AI 协同能力、准备方法论材料、规划下一阶段复杂 AI 产品项目的工作方式。
Not for: 产品运行时权威说明、机制规格、评测契约、简历 bullet 或面试话术成稿。

This document is a case-study gateway. It deliberately does not update product behavior, runtime behavior, task status, mechanism authority, or benchmark authority.

Boundary statement: 本包讨论的不是如何从零开发 agent runtime、agent framework 或通用 agent 平台，而是一个 operator 如何驾驭现有 AI agent、coding agent 和多工具 AI workflow。

## Core Thesis

Reading Companion 最值得沉淀的 AI-native workflow，不是“用 AI 更快写代码”，而是逐步形成了一套 operator-side AI Harness：在复杂项目里，人如何定义目标、治理上下文、组织执行、校验证据、控制工具风险，并把每轮经验转成下一轮 AI 更容易接住的结构。

这个 Harness 的核心不是一组工具技巧，而是一种工作方式：

- 先治理目标：让 AI 明确这轮到底要解决什么、什么算完成、什么不该做。
- 再治理上下文：让重要信息有生命周期、权威来源、检索入口和更新规则。
- 然后治理执行：让 coding agent 的工作可分阶段推进、可恢复、可交接、可追溯。
- 同时治理证据：让结果不只是“看起来不错”，而是能被 eval、artifact、run id 和人工判断复查。
- 最后治理学习：把失败和洞察转成规则、模板、评测样本、脚本、文档路由或明确的 defer reason。

## Document Map

| Document | Job |
| --- | --- |
| [Reading Companion Methodology Summary](ai-native-workflow/reading-companion-gap-map.md) | 总结本项目中已经形成的 AI 协同方法、强项、缺口和改进方向。 |
| [Frontier Harness Landscape](ai-native-workflow/frontier-harness-landscape.md) | 调研外部 agent / eval / context / observability / governance 方法论，并说明它们如何支撑 operator-side AI Harness。 |
| [Playbook](ai-native-workflow/playbook.md) | 把方法论转成下一次复杂 AI 协作可直接使用的操作流程。 |
| [Improvement Roadmap](ai-native-workflow/improvement-roadmap.md) | 按能力环节规划下一阶段最值得补强的 AI 协同能力。 |
| [Evidence Index](ai-native-workflow/evidence-index.md) | 汇总项目证据、外部来源、来源类型、耐久性和纳入原因。 |

建议阅读顺序：

1. 先读 [Reading Companion Methodology Summary](ai-native-workflow/reading-companion-gap-map.md)，看自己的项目实践已经形成了什么。
2. 再读 [Frontier Harness Landscape](ai-native-workflow/frontier-harness-landscape.md)，看外部方法论如何呼应这些经验。
3. 然后读 [Playbook](ai-native-workflow/playbook.md)，把经验转成下一次可执行的流程。
4. 最后读 [Improvement Roadmap](ai-native-workflow/improvement-roadmap.md)，决定下一阶段训练什么能力。

## One-Page Answer

### 截止目前已经形成的有效方法

第一，你已经形成了目标优先的 AI 协作方式。AI 不再只是被要求“继续做”，而是被放进更明确的产品目的、机制边界、评测目标和停止条件中。证据包括 [Product Overview](../product-overview.md)、[Backend Reader Evaluation](../backend-reader-evaluation.md) 和 [Decision Log](../history/decision-log.md) 中关于 product-first evaluation 与机制方向的决策。

第二，你已经形成了 repo-first context governance。项目的工作规则、当前状态、任务注册、决策历史、评测证据和机制说明都有稳定位置，AI 通过文档路由进入项目，而不是依赖聊天记忆。证据包括 [AGENTS.md](../../AGENTS.md)、[Source Of Truth Map](../source-of-truth-map.md)、[Current State](../current-state.md) 和 [Task Registry](../tasks/registry.md)。

第三，你已经把复杂实现从“一次性让 AI 写完”变成了 staged execution。source mirror、requirement ledger、execution tracker、validation matrix、job registry、watchdog 和 `bundle -> judge -> merge` 这类设计，让任务可以分阶段推进、失败后恢复、跨线程交接。

第四，你已经把评测从 scoreboard 变成 evidence system。项目会区分机制弱、数据弱、harness 弱；会保留 invalidated / diagnostic / formal evidence 的边界；也会要求 meaningful eval result 进入 selective implementation 或 explicit deferment。证据包括 [Evaluation Evidence Catalog](../../reading-companion-backend/docs/evaluation/evidence_catalog.md)、[Mechanism Pattern Ledger](../implementation/new-reading-mechanism/mechanism-pattern-ledger.md) 和 [Backend Reader Evaluation](../backend-reader-evaluation.md)。

第五，你已经开始区分长期原则和阶段性工具技巧。比如某个模型、某个 watchdog interval、某个 context window 限制都是阶段性策略；但目标契约、上下文路由、source-grounded eval、run provenance、decision-bearing docs 是更长期有效的 operator-side 方法。

### 最值得继续补强的能力

最值得补强的是“预先设计 AI 协作结构”的能力。

项目已经很强地把结果沉淀成证据，但很多高成本问题仍然来自开工前的 harness 不够显式：这轮到底回答什么、什么证据足以改变决策、哪些上下文必须进入、哪些工具权限可以开放、哪些 artifact 只是 diagnostic、什么时候应停止或重跑。

下一阶段应把复杂 AI 协作任务都包进一层轻量 operator harness：

- 开始前定义目标、scope、non-goal、decision owner、stop condition。
- 装载上下文前先确认信息路由、权威来源、检索入口和上下文预算。
- 执行中保留 run id、命令、artifact path、工具边界、恢复姿态。
- 评测后写 post-run interpretation，区分 result、validity、cause、decision、follow-up。
- 定期把外部 AI workflow 前沿材料纳入 source monitoring，但只把被验证的做法转成稳定规则。

## Evidence Links

更完整证据见 [Evidence Index](ai-native-workflow/evidence-index.md)。核心项目证据入口包括：

- [AGENTS.md](../../AGENTS.md)
- [Source Of Truth Map](../source-of-truth-map.md)
- [Task Registry](../tasks/registry.md)
- [Current State](../current-state.md)
- [Decision Log](../history/decision-log.md)
- [Backend Reader Evaluation](../backend-reader-evaluation.md)
- [Mechanism Pattern Ledger](../implementation/new-reading-mechanism/mechanism-pattern-ledger.md)
- [Claude Code context-management research](../../reading-companion-backend/docs/research/claude_code_context_management_research_20260412.md)
