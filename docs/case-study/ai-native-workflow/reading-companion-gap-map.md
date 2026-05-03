# Reading Companion Methodology Summary

Purpose: 总结 Reading Companion 项目中已经形成的 operator-side AI Harness 方法论，并标出仍需补强的能力。
Use when: 需要回答“我在这个项目中如何驾驭 AI / coding agent 工具”以及“下一步最值得提升什么”。
Not for: 产品运行时权威、机制规格、任务状态更新、评测结论权威或简历 bullet。

Boundary statement: 本文不是讲如何开发 agent，而是总结一个 operator 如何用现有 AI agent、coding agent 和多工具 workflow 推进复杂 AI 产品项目。

## Summary

Reading Companion 中形成的方法论可以概括为七个环节：

| 环节 | 本质 | 当前状态 |
| --- | --- | --- |
| 目标与意图控制 | 把模糊愿望变成 AI 可执行、可评测、可停止的任务契约 | strong |
| 上下文治理 | 让重要信息有权威来源、生命周期、路由和输入策略 | strong |
| 执行可靠性 | 把 AI 对话变成分阶段、可恢复、可交接的工程流程 | strong |
| 证据与评测 | 把“感觉好坏”转成可复查、可校准、可改进的证据系统 | strong |
| 工具、环境与权限控制 | 管理 AI 能调用什么、在哪里调用、风险如何隔离 | partial |
| 可观测与交接 | 让 agent 的过程、产物、判断和恢复姿态可追踪 | partial |
| 复盘与学习 | 把一次协作经验转成下一轮结构性能力 | strong |

## 1. 目标与意图控制

### 这一层在治理什么

这一层治理的是“AI 到底应该服务哪个人的目标”。复杂项目里，最危险的不是 AI 不够聪明，而是目标没有被人先界定清楚，AI 就沿着看似合理的方向继续产出。

目标与意图控制不是把 prompt 写得更长，而是把任务变成一个小契约：当前问题是什么、什么算完成、什么不做、谁有最终判断权、什么证据会改变方向。

### 需要设计的机制

- 任务开始前要先区分任务类型：澄清产品方向、比较技术方案、实现代码、解释评测、修复回归、整理交接，不能混成一句“继续优化”。
- 目标表达要包含 success criteria 和 non-goals，让 AI 的注意力集中在本轮真正要解决的问题上。
- 对复杂或高成本任务，要定义 stop / retry / abandon condition，避免 AI 把不确定性自动转成更长的执行。

### Reading Companion 中的体现

- [Product Overview](../../product-overview.md) 将项目从 summary engine 稳定为 living co-reader mind，给后续机制和评测提供上游目的。
- [Backend Reader Evaluation](../../backend-reader-evaluation.md) 把产品目的转成 mechanism-agnostic evaluation constitution。
- [Decision Log](../../history/decision-log.md) 保存 `DEC-011`、`DEC-012`、`DEC-013` 等关键意图决策，避免后续 AI 协作漂回旧目标。
- [Requirement Ledger](../../implementation/new-reading-mechanism/requirement-ledger.md) 用 atomic requirements 和 disposition 管理大设计里的目标遗漏。

### 仍需补强

最值得补强的是“每轮任务开工前的轻量 task contract”。项目已经有很多事后证据，但未来更应该在任务启动时就写清：本轮要回答的问题、完成标准、无效条件和停止条件。

## 2. 上下文治理

### 这一层在治理什么

这一层治理的是“AI 该知道什么，以及它应该从哪里知道”。上下文治理的核心不是多写文档，也不是把所有信息塞进 context window，而是设计一套信息维护框架：哪些信息是长期规则，哪些是当前状态，哪些是历史决策，哪些只是临时探索。

如果没有上下文治理，AI 会在聊天记忆、过期总结、局部代码和个人偏好之间拼接事实，最后看似懂很多，实际失去判断依据。

### 需要设计的机制

- 先设计信息分层，再写具体文档：规则、当前状态、任务索引、稳定事实、决策历史、临时 handoff、评测证据应该有不同生命周期。
- 先检索索引和路由，再加载全文：AI 应该通过 source-of-truth map、registry、load matrix 或搜索进入事实，而不是靠操作者每次手动复制背景。
- 对高噪声探索使用隔离上下文或 subagent，只把结论、证据、风险和下一步回传主线。
- 每次自动维护文档时，都要判断这条信息是 durable fact、current state、decision、diagnostic evidence，还是只该留在 scratch。

### Reading Companion 中的体现

- [AGENTS.md](../../../AGENTS.md) 定义 load matrix、doc routing、trigger matrix 和长任务协作规则。
- [Source Of Truth Map](../../source-of-truth-map.md) 说明 durable information 应该进入哪里，以及如何验证 switching system。
- [Current State](../../current-state.md) 和 [Task Registry](../../tasks/registry.md) 让 AI 能找到当前目标、active jobs、task status、decision refs 和 evidence refs。
- [Claude Code context-management research](../../../reading-companion-backend/docs/research/claude_code_context_management_research_20260412.md) 将 coding-agent context management 的经验转成 index-first memory、side context、compaction plus re-injection 等实践。

### 仍需补强

项目内上下文治理已经很强，但跨工具、跨 repo、跨模型的个人上下文治理仍不够显式。未来需要更清楚地定义哪些规则属于个人级 AI Harness，哪些只属于 Reading Companion 这个项目。

## 3. 执行可靠性

### 这一层在治理什么

这一层治理的是“AI 如何把事情做完，而不是只在聊天里推进”。复杂任务不能依赖一次对话、一段超长 prompt 或一个 agent 的短期记忆，而要被拆成可检查、可恢复、可交接的执行流程。

执行可靠性不是让 AI 先写一份计划这么简单。计划只是入口，真正重要的是阶段产物、状态记录、失败恢复、边界控制和下一位 agent 能否接手。

### 需要设计的机制

- 高不确定任务先设计 execution plan，再让 AI 按阶段实现，不让它边猜目标边改代码。
- 每个阶段要有 artifact、检查命令、完成条件和下一步，而不是只留下聊天摘要。
- 长任务要登记 run id、命令、输入、输出路径、watchdog、当前阶段和恢复方式。
- 失败后要能判断继续、retry、resume、restart、废弃，或者把结果降级为 diagnostic evidence。

### Reading Companion 中的体现

- [Backend Sequential Lifecycle](../../backend-sequential-lifecycle.md) 定义 upload/start/resume、job records、checkpoint 和 recovery semantics。
- [Execution Tracker](../../implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md) 记录 phased implementation、landed behavior、validation posture 和 next moves。
- [Dataset Platform Closed Loop](../../implementation/new-reading-mechanism/dataset-platform-closed-loop.md) 展示 source intake、case generation、packet review、repair loop、stop condition 的闭环。
- `bundle -> judge -> merge`、job registry、watchdogs 和 expected outputs 让 long-running eval 可以跨线程恢复，而不是靠聊天窗口记住。

### 仍需补强

执行流程强，但个人级 reusable multi-agent planning / execution pattern 还不够抽象。未来可以把“什么时候主线程做、什么时候 subagent 探索、什么时候脚本控制流程”沉淀成稳定模板。

## 4. 证据与评测

### 这一层在治理什么

这一层治理的是“AI 结果为什么可信，以及它到底说明了什么”。复杂 AI 项目里，结果看起来好不等于方向正确，分数提高也不一定代表机制更好；有时只是 dataset、judge、source retrieval 或 harness 本身出了问题。

证据与评测的核心是把主观感觉转成可复查的 evidence contract：评测回答什么问题、什么证据有效、什么会使 run invalid、LLM judge 可以判断什么、人类校准在哪里介入。

### 需要设计的机制

- 评测前定义 objective、dataset、validity criteria、artifact path、decision rule 和 stop condition。
- 评测后写 post-run interpretation，区分 top-line result、validity、causal read、decision 和 follow-up。
- 区分 formal evidence、diagnostic evidence、invalidated run 和 historical evidence，避免把错误证据继续用于决策。
- 先做 error analysis，再决定改 prompt、换模型、修工具、改数据还是调整产品目标。

### Reading Companion 中的体现

- [Backend Reader Evaluation](../../backend-reader-evaluation.md) 定义 product-first evaluation、dual diagnosis、source-span rules 和 benchmark-size adequacy。
- [Evaluation Evidence Catalog](../../../reading-companion-backend/docs/evaluation/evidence_catalog.md) 将 current formal evidence、quality audits、historical evidence、superseded evidence、failed diagnostics、invalidated diagnostics 分层。
- [Long-Span Evaluation README](../../../reading-companion-backend/docs/evaluation/long_span/README.md) 记录从 discontinued target-centered route 转向 Memory Quality、Spontaneous Callback、False Visible Integration 的方法路线调整。
- [Decision Log](../../history/decision-log.md) 的 `DEC-064` 将错误 candidate retrieval gate 视为 benchmark-contract failure，而不是弱模型结果。

### 仍需补强

下一步最值得补强的是预任务 evidence contract 和更强的人类校准。项目已经擅长事后解释证据，但高成本 eval 应该在运行前就更明确地定义“什么样的结果有资格改变决策”。

## 5. 工具、环境与权限控制

### 这一层在治理什么

这一层治理的是“AI 可以调用什么，以及调用时风险如何被限制”。对 coding agent 来说，模型能力只是其中一部分；工具接口、工作目录、sandbox、依赖、凭证、审批和失败模式共同决定了它能做什么、会误伤什么。

这不是开发一个工具平台，而是 operator 为现有 AI 工具设计使用边界。

### 需要设计的机制

- 明确哪些工具适合读取、哪些适合修改、哪些适合验证、哪些需要人工审批。
- 对高风险操作设置 sandbox、permission、credential isolation 和 irreversible-action guard。
- 记录模型/provider、依赖、环境、命令入口和输出位置，避免 agent 依赖想象中的环境。
- 将工具失败视为可观察事件，而不是让模型把空输出、超时或局部成功误读成事实。

### Reading Companion 中的体现

- [Backend Reading Mechanism](../../backend-reading-mechanism.md) 定义 shared runtime shell、shared substrate、mechanism-private artifacts 和 shared evaluation boundary。
- [Backend AGENTS.md](../../../reading-companion-backend/AGENTS.md) 定义 backend-local 的 LLM gateway、artifact routing、job registry usage 和 generated artifact hygiene。
- [Source Of Truth Map](../../source-of-truth-map.md) 记录 `make agent-check`、contract checks、background-job checks 等 validation commands。

### 仍需补强

Reading Companion 内部工具治理较强，但还没有 generalized personal AI tool governance layer。未来需要一个轻量规则：哪些 AI 工具、MCP server、browser source、local script、permission mode 适用于哪类个人 workflow task。

## 6. 可观测与交接

### 这一层在治理什么

这一层治理的是“AI 做过什么，以及下一轮如何接上”。复杂 AI 协作如果只保存最终输出，下一个 agent 或未来的自己就必须重新考古；真正可恢复的协作需要 run、artifact、metadata、decision 和 recovery posture 的链路。

可观测不是为了做漂亮 dashboard，而是为了在失败、回归、交接、评审时能回答：这次 run 发生了什么、用了什么输入、产出了什么证据、哪些结论可信、下一步从哪里继续。

### 需要设计的机制

- 每个关键 run 都应该能连到命令、输入、输出、模型/provider、artifact、评测、人工判断和后续动作。
- 长任务和复杂评测需要 run dossier 或等价索引，避免证据散落在日志、聊天和目录里。
- 交接文档应记录当前状态、blocked items、expected outputs、recovery command 和失效证据。
- 评审不仅看最终输出，还要检查 execution path 是否合理。

### Reading Companion 中的体现

- [Current State](../../current-state.md) 记录 active jobs、run ids、watchdog ids、expected outputs 和 recovery posture。
- [Task Registry](../../tasks/registry.md) 将 task status 连接到 decision refs、job refs、evidence refs 和 next actions。
- [Attentional V2 mechanism doc](../../backend-reading-mechanisms/attentional_v2.md) 记录 read audits、context use、continuation capsules、probe snapshots 和 mechanism-private runtime artifacts。
- [Evaluation Evidence Catalog](../../../reading-companion-backend/docs/evaluation/evidence_catalog.md) 将 runs 连接到 aggregates、reports、analyses 和 status classes。

### 仍需补强

项目有很强的 artifact provenance，但缺少更 visual / queryable 的 trace or dashboard layer。未来应重点补 run dossier、execution-path inspection 和 trace-to-eval-to-review linkage。

## 7. 复盘与学习

### 这一层在治理什么

这一层治理的是“这次协作如何改变下一次协作”。复盘不是写感想，而是判断一条经验应该进入规则、checklist、test、eval case、script、decision log、roadmap，还是应该被丢弃。

如果没有学习治理，AI 协作会反复依赖同样的手动提醒；如果学习治理过度，又会把所有经验塞进上下文，制造新的噪声。

### 需要设计的机制

- 只保留 failure-backed rules：每条稳定规则都应该能解释它预防了什么真实失败或反复成本。
- 区分 durable principle、current tactical 和 speculative signal，避免把工具阶段性技巧写成长期方法论。
- 对高价值 insight 设置 disposition：adopt、test、defer、reject、monitor，而不是只存进 ledger。
- 建立 source monitoring，让外部 AI workflow 方法论进入观察雷达，但只有被项目经验或多方实践印证后才升级为规则。

### Reading Companion 中的体现

- [Mechanism Pattern Ledger](../../implementation/new-reading-mechanism/mechanism-pattern-ledger.md) 保存 strengths、adoption candidates、failure modes、anti-patterns、status 和 next action。
- [Decision Log](../../history/decision-log.md) 保存后续难以从代码恢复的设计 inflections 和 rejected alternatives。
- [Claude Code context-management research](../../../reading-companion-backend/docs/research/claude_code_context_management_research_20260412.md) 展示如何把 coding-agent context management 迁移到 Reading Companion 机制设计。
- 本 case-study 包本身就是一次将项目经验从 chat 迁移成方法论结构的学习产物。

### 仍需补强

未来最值得做的是 systematic source monitoring：定期观察官方 docs、实践者框架和社区信号，但用 evidence index 和 project fit 过滤噪声，而不是追逐每个新工具技巧。

## The Two Direct Answers

### 当前做得好的地方

你已经形成了目标优先、repo-first context governance、staged execution、evidence-driven evaluation、recoverable handoff 和 learning loop。最核心的进步是：你不是只让 AI 产出答案，而是在逐步设计 AI 协作的外部控制系统。

### 最值得继续补强的能力

最值得补强的是前置化：在任务开始前更明确地设计目标契约、上下文入口、工具权限、证据契约和可观测路径。也就是说，把现在很多强大的事后整理能力，提前放到 AI 协作开始之前。
