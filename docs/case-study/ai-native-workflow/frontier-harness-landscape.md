# Frontier Harness Landscape

Purpose: 调研当前 AI agent / AI harness / AI coding workflow 的外部方法论，并说明它们如何支撑 operator-side AI Harness。
Use when: 需要理解外部方法论如何帮助一个 operator 更好地驾驭现有 AI agent、coding agent 和多工具 AI workflow。
Not for: Reading Companion 产品机制权威、运行时规范、某个外部工具的完整教程，或对单一社区观点的背书。

Source check date: 2026-04-23.

Boundary statement: 本文借用 agent engineering、MCP、eval、observability 和 orchestration 等领域的概念，但目标不是说明如何从零开发 agent runtime、agent framework 或通用 agent 平台。这里的视角是 operator-side AI Harness。

## Source Tiers

| Tier | How it is used |
| --- | --- |
| `official/frontier docs` | 官方文档、标准规格、平台工程博客。用作结构锚点。 |
| `practitioner systems` | 高质量实践者框架和工作流文章。用作方法补充。 |
| `fast-moving signals` | Reddit / X / HN-style 讨论和工具信号。只作为趋势雷达，不作为权威结论。 |

Every external source is classified in [Evidence Index](evidence-index.md). The core distinction is:

- `durable principle`: 工具换代后仍大概率有效。
- `current tactical`: 当前工具阶段很有用，但可能随平台变化。
- `speculative signal`: 值得观察，但不能单独作为方法论基础。

## What The Field Is Really Converging On

外部方法论虽然使用不同语言，但正在收敛到同一个方向：复杂 AI 协作的质量不是只由模型决定，而是由模型周围的目标、上下文、工具、执行、评测、观测、治理和学习结构共同决定。

不同来源的关注点并不相同：

- Agent workflow / orchestration 关注如何把不确定任务拆成可组合流程。
- Context engineering 关注如何管理模型注意力和长期记忆。
- Tool / environment 方法论关注工具边界、sandbox、权限和运行环境。
- Eval / error analysis 关注如何证明系统真的变好。
- Observability 关注如何看见 run、trace、artifact 和反馈。
- Governance 关注不可逆动作、prompt injection、凭证、模型/provider 变化。
- Learning loop 关注如何把失败变成下一轮更好的规则、数据和流程。

这些外部方法论不是要被硬套成一个 agent platform。对本 case study 来说，它们的价值在于帮助 operator 设计更可靠的 AI 协作方式。

## 1. Agent Workflow / Orchestration

### 它解决的 operator-side 问题

当任务变复杂时，直接让 AI “继续做”会把目标澄清、方案判断、代码实现、验证和交接混在一起。Agent workflow / orchestration 的价值，是提醒 operator 把工作拆成可控阶段，并决定哪些阶段由模型判断，哪些阶段由确定性流程控制。

### 外部方法论提供了什么

- Anthropic 的 agent 指南强调优先使用简单、可组合的 workflow，并区分 workflow 与更自主的 agent。
- OpenAI agent guide 将 run loop、exit condition、handoff 和 structured output 放在编排核心。
- Microsoft orchestration patterns 将 sequential、concurrent、group chat、handoff、magentic 等模式视为可按阶段组合的策略。
- HumanLayer 的 12-factor agents 更强调普通程序控制流：让 LLM 输出下一步或结构化判断，再由代码负责 reducer / switch / state transition。

### 对驾驭 AI 的启发

operator 不需要先造一个复杂 agent system。更重要的是在每个任务前判断：这里需要 sequential workflow、并行探索、handoff、evaluator loop，还是只需要一个普通 coding agent 加清晰检查命令。

## 2. Context Engineering

### 它解决的 operator-side 问题

AI 工具失败往往不是因为上下文太少，而是上下文没有路由。信息可能过期、重复、层级混乱，或者把真正稀缺的 attention budget 消耗在可从代码或索引恢复的细节上。

### 外部方法论提供了什么

- Claude Code memory docs 将 memory、rules、imports、path-scoped rules、skills 做分层。
- Claude Code subagents docs 和 Anthropic subagents blog 强调独立 context window 可以隔离高噪声探索。
- Augment Code 的 context commentary 提醒：context file 应该少而 failure-backed，不应重复代码本身可见的信息。
- 社区信号显示，context management 正在从个人纪律转向 hooks、routing、subagent isolation 和 shared AGENTS-style files。

### 对驾驭 AI 的启发

operator-side context governance 的重点是先设计信息生命周期：哪些信息是长期规则，哪些是当前状态，哪些是历史决策，哪些只是临时 scratch。具体文档只是这套治理框架的载体。

## 3. Tool / Environment Boundary

### 它解决的 operator-side 问题

coding agent 的能力来自模型加工具。工具 schema、sandbox、权限、工作目录、依赖、凭证和失败模式都会改变 agent 行为。如果这些边界不清楚，AI 可能把工具错误当事实，或在错误权限下执行高风险操作。

### 外部方法论提供了什么

- MCP specification 将 resources、prompts、tools、lifecycle、authorization 分离，为 tool/context boundary 提供标准语言。
- OpenAI Agents SDK 的 sandbox / workspace manifest / snapshot / rehydration 方向说明，受控环境和可恢复状态正在成为 agent 平台的核心能力。
- Anthropic agent guidance 明确提醒：很多 agent 失败来自 tool design，而不是 prompt 本身。

### 对驾驭 AI 的启发

operator 不必开发工具协议，但需要用协议化思维管理工具：哪些工具只读，哪些能写，哪些需要审批，哪些环境可恢复，哪些凭证不该进入模型上下文。

## 4. Evaluation And Error Analysis

### 它解决的 operator-side 问题

AI 输出开放、不确定、易受上下文影响。没有 eval 和 error analysis，operator 很容易用“感觉更好”替代证据，或者把数据、judge、retrieval、prompt、机制问题混成一个“模型不行”。

### 外部方法论提供了什么

- OpenAI evaluation best practices 强调 objective、dataset、metrics、run / compare、continuous evaluation，并反对 vibe-based evals。
- OpenAI agent evals 将 trajectory、tool calls 和最终结果都纳入 agent workflow 评测。
- Hamel Husain 的 eval 方法论强调 domain-specific evals、trace review、error analysis，且不把 model switching 当成第一反应。

### 对驾驭 AI 的启发

operator 应该先定义 evidence contract，再运行高成本评测。评测后要解释结果是否有效、错因属于哪里、是否足以改变决策，而不是只记录一个分数。

## 5. Observability

### 它解决的 operator-side 问题

最终输出不是唯一证据。复杂 AI 协作需要回答：这次 run 用了什么输入、走了什么路径、调用了什么工具、生成了什么 artifact、哪些判断被人工接受或拒绝。

### 外部方法论提供了什么

- LangSmith 将 trace 定义为一次操作下多个 run / span 的集合，并支持 metadata、tags、feedback。
- Microsoft Foundry / Agent Framework 方向强调 multi-agent observability、OpenTelemetry 和 tool invocation visibility。
- 社区讨论反复出现同一痛点：很多团队有 trace、eval、artifact 和 approval，但很难把它们连成从 run id 到 reviewer decision 的干净链路。此类讨论在这里只作为 `fast-moving signals`。

### 对驾驭 AI 的启发

operator 不一定需要大型 dashboard，但需要 run dossier 思维：每个关键 run 都应能连接命令、输入、输出、artifact、eval、解释和决策。

## 6. Governance And Safety

### 它解决的 operator-side 问题

当 AI 能读写文件、运行命令、调用浏览器、接触凭证或影响生产环境时，不能只靠“模型会小心”。权限、审批、prompt injection、exfiltration、model/provider upgrade 都需要规则。

### 外部方法论提供了什么

- OpenAI Agents SDK sandbox announcement 强调 prompt injection / exfiltration assumptions，以及 harness 与 compute 分离以保护凭证。
- Claude Code docs 暴露了 permission modes、tool restrictions、subagent capabilities 等治理面。
- Microsoft enterprise agent material 将 observability、durability、compliance、governance 视为 multi-agent production 的核心问题。

### 对驾驭 AI 的启发

operator-side governance 的重点不是让模型“更谨慎”，而是按任务风险分配权限：读、写、执行、联网、访问凭证、不可逆操作、模型升级都应该有边界和审计。

## 7. Learning Loop

### 它解决的 operator-side 问题

没有学习回路，AI 协作的经验会反复留在聊天里；过度学习又会把所有经验塞进 context file，制造噪声。关键是判断一条经验应该进入规则、checklist、eval case、script、decision log、roadmap，还是只作为观察信号。

### 外部方法论提供了什么

- Hamel-style eval practice 将 traces 和 error analysis 转成 dataset 与改进循环。
- Augment Code 的 context essay 强调规则要 failure-backed，而不是 aspirational。
- 社区信号显示，先进个人 workflow 正在从“每次手动提醒 AI”转向 hooks、skills、slash commands、memory files、source monitoring 和 run-history diffing。

### 对驾驭 AI 的启发

operator 应该维护一个 source-monitoring habit，但不能把每条外部技巧都写进稳定方法论。只有被官方文档、开源工具、多方实践或自己的项目经验重复印证后，才值得升级为强规则。

## Auxiliary Stack Map

原先的八层 `AI Harness Stack` 仍然有用，但它更适合作为地图，而不是本文主叙事：

| Stack layer | Operator-side reading |
| --- | --- |
| Intent Harness | 目标与意图控制 |
| Context Harness | 上下文治理 |
| Tool / Environment Harness | 工具、环境与权限控制 |
| Execution Harness | 执行可靠性 |
| Evaluation Harness | 证据与评测 |
| Observability Harness | 可观测与交接 |
| Governance Harness | 风险、安全与供应商治理 |
| Learning Harness | 复盘、学习与外部来源监控 |

## What Is Tactical vs Durable

| Category | Examples | How to use |
| --- | --- | --- |
| Current tactical | Claude Code subagent behavior, OpenAI Agents SDK sandbox providers, current MCP revision, current context-window limits, current permission modes | 适合短中期采用，但要预期工具会变化；采用时要记录版本、适用条件和迁移风险。 |
| Durable principle | simple composable workflows, context budgets, typed tools, staged artifacts, eval/error-analysis flywheel, trace provenance, approval gates | 可以沉淀成个人方法论、项目规则、checklist、eval case 或自动化检查。 |
| Speculative signal | X threads about auto-memory, Reddit discussions about AGENTS.md stubs, new process-mining tools, emerging memory-first harness claims | 作为观察雷达；只有被官方文档、开源工具或多方实践重复印证后再写入强规则。 |

## Reading Companion Implication

Reading Companion 的经验与外部方法论是互相印证的：项目已经强在目标、上下文、执行、评测和学习，下一阶段更需要补齐 general-purpose tool governance、visual / queryable observability、prompt-injection / provider-upgrade governance 和 systematic source monitoring。

Use this document as the external landscape, then read [Reading Companion Methodology Summary](reading-companion-gap-map.md) for project evidence, [Playbook](playbook.md) for operating rules, and [Improvement Roadmap](improvement-roadmap.md) for next upgrades.
