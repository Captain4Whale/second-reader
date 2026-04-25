# Frontier Harness Landscape

Purpose: 综合当前 AI agent / AI harness / AI coding workflow 的前沿方法论，定义可复用的 AI Harness Stack。
Use when: 需要判断“先进 AI 协同系统应该包含哪些层”，或需要把 Reading Companion 的经验放进更大的方法论参照系。
Not for: Reading Companion 产品机制权威、运行时规范、某个外部工具的完整教程，或对单一社区观点的背书。

Source check date: 2026-04-23.

This document uses three evidence tiers:

- `official/frontier docs`: 官方文档、标准规格、平台工程博客。用作结构锚点。
- `practitioner systems`: 高质量实践者框架和工作流文章。用作方法补充。
- `fast-moving signals`: Reddit / X / HN-style 讨论和工具信号。只作为趋势雷达，不作为权威结论。

Every external source is classified in [Evidence Index](evidence-index.md). The core distinction is:

- `durable principle`: 工具换代后仍大概率有效。
- `current tactical`: 当前工具阶段很有用，但可能随平台变化。
- `speculative signal`: 值得观察，但不能单独作为方法论基础。

## Why Harness, Not Just Prompting

前沿 agent 实践的共同趋势是：真正提升复杂 AI 工作质量的，不是再写一个更长的 prompt，而是把模型放进一个可控的系统。

这个系统通常包含：

- 清晰的目标和退出条件。
- 可被模型安全使用的工具和上下文。
- 独立上下文或 subagent，用来隔离高噪声探索。
- 可恢复的执行环境、run state、checkpoint 或 snapshot。
- trace、eval、feedback、human approval 的闭环。
- prompt injection、权限、凭证隔离、不可逆操作保护。
- 把每轮失败转成下一轮的规则、测试、dataset 或 harness 改进。

这也是为什么这里使用 `AI Harness Stack`，而不是只说 prompt engineering、agent framework 或 coding assistant workflow。

## How To Read The Stack

`AI Harness Stack` 不是业界已经统一命名的标准分层，而是对当前官方文档、实践者系统和社区信号的综合抽象。不同外部框架通常只覆盖其中几层：agent design patterns 多关注 Execution，MCP 多关注 Tool / Environment，Claude Code 多关注 Context / Execution / Governance，LangSmith 和 Hamel-style eval practice 多关注 Evaluation / Observability / Learning。

这个 stack 试图回答的是另一个问题：一个人或一个团队要稳定驾驭 AI、coding agents 和多工具 workflow，需要控制哪些面。

每一层都可以用四类控制动作理解：

- 定义对象：这层到底管理什么，例如 task、context、tool、run、trace、eval、rule。
- 划定边界：什么可以进入，什么必须排除，谁拥有权限，什么不是这轮任务。
- 组织流程：如何执行、暂停、恢复、分阶段推进、交接给另一个 agent。
- 形成反馈：如何判断做得好不好，以及如何把经验转成下一轮的结构。

八层之间也不是平行 checklist。Intent 是上游，Context 和 Tool / Environment 是基础设施，Execution 是工作流，Evaluation 和 Observability 是反馈系统，Governance 是风险边界，Learning 是复利层。

## AI Harness Stack

### 1. Intent Harness

Intent Harness 负责把人的模糊意图变成 AI 可执行、可评测、可拒绝的任务边界。

Substructure:

**任务定义**

- `problem framing`: 把“我想改善一点东西”转成“这轮到底要回答哪个问题”，避免 AI 直接跳进方案生成。
- `success criteria`: 预先说明什么证据代表完成，防止 agent 把工作无限延伸成开放探索。

**边界控制**

- `scope and non-goals`: 写清本轮做什么、不做什么，让 AI 知道哪些热心扩展其实是越界。
- `tradeoffs`: 明确可以牺牲什么、不能牺牲什么，例如速度、覆盖面、稳定性、source grounding、用户体验。

**决策与退出**

- `decision owner`: 说明最终由用户、稳定文档、评测结果、工程约束还是外部标准来拍板。
- `stop / retry / abandon condition`: 规定什么时候停止、重跑、缩小范围或承认路线不成立。

External echoes:

- Anthropic 的 agent 指南强调先选择最简单可行方案，并区分 workflow 与 agent。
- OpenAI 的 agent guide 把 run loop、exit condition、handoff 和 structured output 放在 agent 编排的核心位置。
- Microsoft orchestration patterns 强调不同阶段可以混用 sequential、concurrent、handoff、group chat 等模式，而不是强行套一个统一形态。

Durable principle:

- AI 不能替代意图界定。
- 复杂任务必须先定义“什么算完成”和“什么证据会改变决策”。
- 多 agent 或复杂 harness 只有在任务不确定性、并行度或工具边界需要时才值得引入。

### 2. Context Harness

Context Harness 负责决定哪些信息进入模型、何时进入、以什么粒度进入，以及哪些内容必须留在 repo / memory / index 中。

Substructure:

**权威来源**

- `source-of-truth docs`: 指定哪些文档或代码位置是事实来源，避免 AI 从聊天残影或过期总结里拼接事实。
- `path-scoped rules`: 让不同目录、模块、语言或任务类型拥有各自规则，避免一套泛化规则覆盖所有上下文。

**上下文选择**

- `index-first retrieval`: 先通过目录、registry、source-of-truth map 或搜索定位入口，再按需读取细节。
- `context budgets`: 把上下文窗口当作稀缺预算，决定哪些信息值得占用 attention，哪些应留在文件或工具里。

**记忆生命周期**

- `memory routing`: 决定某条信息应该进入 `AGENTS.md`、current-state、task registry、decision log、机制文档、评测文档，还是只留在临时 scratch。
- `compaction and re-injection`: 长线程压缩后，重新注入关键事实、决策和约束，而不是假设压缩摘要已经保留全部语义。

**隔离与降噪**

- `subagent isolation`: 把高体积探索、并行调查或噪声较高的试探放进隔离上下文，只把结论、证据和风险回传主线。

External echoes:

- Claude Code memory docs 将项目记忆、规则、imports、path-scoped rules、skills 做分层。
- Claude Code subagents docs 和 Anthropic blog 都强调 subagent 的独立 context window 和主会话降噪价值。
- 实践者和社区讨论反复提醒：上下文越多不一定越好，过多通用规则会挤占真正稀缺的 attention budget。

Durable principle:

- 不要把所有记忆变成一个越来越大的 blob。
- Context file 应该像 routing table，而不是百科全书。
- 可从代码或工具直接恢复的信息，不必重复写进 agent memory。
- 高体积探索适合放进隔离上下文，只把结论回传主线。

### 3. Tool / Environment Harness

Tool / Environment Harness 负责让 AI 使用稳定、明确、可审计的工具和运行环境。

Substructure:

**工具接口**

- `stable tool schema`: 工具的输入、输出、错误形态和边界要稳定，因为 tool schema 本身会塑造模型行为。
- `MCP-style resources / prompts / tools boundary`: 把可读资源、可复用提示、可执行工具分开，降低“一个接口什么都做”的混乱度。

**运行环境**

- `sandbox`: 限制 AI 在什么文件系统、网络、权限和计算环境中执行，尤其保护高风险操作。
- `environment manifests`: 记录运行环境、依赖、工作区状态或 snapshot，让一次 agent run 可以被恢复或复现。
- `dependency availability`: 确认可用命令、库、模型和服务真实存在，避免 AI 按想象中的环境执行。

**权限与安全**

- `permission model`: 区分自动允许、需要审批、禁止执行的操作，并让不同工具或 subagent 只能使用必要权限。
- `credential separation`: 把凭证、密钥、用户数据和模型可见上下文分离，避免工具调用扩大泄漏面。
- `tool reliability`: 让工具失败、超时、空输出或部分成功能被识别和处理，而不是被模型误读成事实。

External echoes:

- MCP specification 把 resources、prompts、tools、lifecycle、authorization 等边界拆开，并建立 JSON-RPC 消息形态。
- OpenAI Agents SDK 的最新 harness / sandbox 方向强调 controlled workspace、portable environment manifest、snapshot / rehydration、harness 与 compute 分离。
- Anthropic 的 agent 指南提醒，很多 agent 成败来自 tool design，而不是 prompt 本身。

Durable principle:

- Tool shape 是 prompt 的一部分。
- AI 使用工具时，路径、权限、凭证、输出目录和失败模式都应该明确。
- 对高风险操作，sandbox、审批和不可逆动作保护比“让模型更小心”可靠。

### 4. Execution Harness

Execution Harness 负责把 AI 协作从一次对话变成可恢复、可重放、可并行、可交接的执行系统。

Substructure:

**流程控制**

- `deterministic workflow where possible`: 能由脚本、状态机、CI 或普通程序确定执行的流程，不交给模型即兴发挥。
- `staged artifacts`: 把大任务拆成可检查的中间产物，让失败后可以 reuse、resume、rejudge 或 restart。

**Agent 组织**

- `scoped agents`: 为每个 agent 或 subagent 指定窄职责、输入、输出和工具范围，避免多个 agent 在同一问题上无序重叠。
- `ownership boundaries`: 明确文件、模块、阶段或判断面的归属，降低并行协作时的覆盖和冲突。

**持久执行**

- `durable execution`: 长任务的状态、命令、产物和下一步要能跨线程、跨会话、跨 agent 恢复。
- `run ids`: 给每次执行可引用身份，把日志、artifact、eval、review 和决策绑定到同一次 run。

**恢复机制**

- `retry / resume / watchdog`: 为失败、卡住、超时或部分完成的任务定义检查、重试、恢复和告警方式。
- `pause and recovery`: 让任务可以安全暂停，并让下一位 agent 知道从哪里继续、哪些产物可信。

External echoes:

- OpenAI agent guide 把 agent run 描述成循环，直到 final output、tool call、error 或 max turns 等退出条件出现。
- Microsoft Agent Framework 和 orchestration docs 强调持久状态、错误处理、retries、recovery、multi-agent coordination。
- HumanLayer 的 12-factor agents 更偏实践派：让 LLM 输出下一步 JSON / tool call，再由普通程序 switch / reducer 控制流程。

Durable principle:

- 能确定的流程交给代码，不要交给模型即兴发挥。
- Agent 的价值在处理不确定判断和语言/工具选择，而不是替代所有控制流。
- 大任务要拆成 artifact stages，这样失败后可以决定 reuse、resume、rejudge 或 restart。

### 5. Evaluation Harness

Evaluation Harness 负责让 AI 系统在不确定输出下仍然可以被改进。

Substructure:

**样本与任务**

- `datasets`: 用代表性样本定义要测的问题，避免凭少数印象样例判断系统质量。
- `offline and online evals`: 用离线评测支持机制比较和回归，用在线反馈观察真实使用中的质量与风险。

**判断机制**

- `LLM-as-judge`: 用模型辅助评审开放式输出，但明确 judge 可以判断什么、不能替代什么。
- `human calibration`: 用人工抽检、标注或仲裁校准 judge、metric 和任务定义，防止自动评测漂移。

**过程评测**

- `trace grading`: 评估 agent 的中间路径、tool call、证据使用和执行轨迹，而不只看最终答案。
- `error analysis`: 先分析错因属于机制、数据、prompt、工具、模型还是 operator，再决定改哪里。

**回归控制**

- `regression gates`: 在默认机制、模型/provider、prompt 或工具升级前设置最低质量门槛。
- `continuous evaluation`: 把评测变成持续比较、追踪和改进的流程，而不是一次性报告。

External echoes:

- OpenAI evaluation best practices 强调 objective、dataset、metric、run / compare、continuous evaluation，以及不要依赖 vibe-based evals。
- OpenAI agent evals 将 agent workflow 的 trajectory、tool call 和最终结果都纳入评测视野。
- Hamel Husain 的 eval 方法论强调 domain-specific evals、trace review、error analysis，且不把 model switching 当成第一反应。

Durable principle:

- 先做 error analysis，再决定换模型、改 prompt、改工具还是改数据。
- LLM-as-judge 需要人类校准和不可能组合校验。
- 输出分数不够，必须检查 harness 是否测试了正确问题。

### 6. Observability Harness

Observability Harness 负责回答“这次 agent 到底做了什么，以及为什么结果可信或不可信”。

Substructure:

**运行记录**

- `traces`: 保存一次 agent 工作的整体路径，包括输入、步骤、工具调用、模型响应和结果。
- `spans / runs`: 把一次复杂执行拆成可定位的小单元，方便定位慢、错、空转或风险步骤。
- `run ids`: 用稳定标识串起日志、产物、评测、人工审批和后续决策。

**证据链**

- `metadata`: 记录模型、provider、prompt版本、数据集、命令、环境、参数和时间等解释结果所需的上下文。
- `artifacts`: 保存中间产物和最终产物，让评审者能看见 agent 实际生成和消费了什么。
- `provenance`: 标明某个结论、分数或文档更新来自哪次 run、哪个输入、哪个 artifact。

**审查界面**

- `dashboards`: 让人能快速查看趋势、失败模式、成本、队列、质量变化和异常 run。
- `execution-path inspection`: 检查 agent 是否通过合理路径得到结果，识别“答案看似正确但过程不可接受”的情况。
- `trace-to-eval-to-review linkage`: 把 trace、eval、artifact、human review 和最终决策连成可追溯链条。

External echoes:

- LangSmith 把 trace 定义为一次操作下多个 run / span 的集合，并支持 metadata、tags、feedback。
- Microsoft Foundry / Agent Framework 方向强调 multi-agent observability、OpenTelemetry、tool invocation visibility。
- 社区讨论的高频痛点是：很多团队有 trace、eval 和 approval，但很难把“输入 -> 工具 -> artifact -> 人工审批 -> 可复现 rerun”连成一条干净链；此类讨论在这里只作为 `fast-moving signals`。

Durable principle:

- 最终输出不是唯一证据。
- 复杂 agent 需要 execution path eval，而不只是 output eval。
- 评审决策应绑定 run id、trace snapshot、artifact version 和 reviewer decision。

### 7. Governance Harness

Governance Harness 负责管理 AI 的权限、安全、不可逆行为和供应商/模型变化。

Substructure:

**行为约束**

- `guardrails`: 对不允许的输出、动作、数据访问或工作流路径设置明确限制。
- `approval gates`: 对不可逆、高成本、外部影响、凭证相关或生产环境操作设置人工审批点。

**安全假设**

- `prompt injection and exfiltration assumptions`: 默认外部内容可能诱导 agent 忽略规则、泄露信息或误用工具。
- `tool safety`: 按工具风险设计限制、确认、日志和回滚策略，而不是只让模型“谨慎一点”。

**权限与凭证**

- `credential isolation`: 将凭证和敏感资源从模型上下文、低信任工具和不必要的执行环境中隔离。
- `audit policy`: 规定哪些操作必须记录、由谁审查、保留多久，以及发生事故后如何追溯。

**供应商治理**

- `model/provider pinning`: 记录模型、provider、版本、参数和切换理由，避免隐性升级改变行为却无法复盘。
- `escalation rules`: 规定什么时候升级到更强模型、交给人工、缩小任务或停止自动化。

External echoes:

- OpenAI Agents SDK sandbox announcement 明确强调 prompt injection / exfiltration assumptions，以及 harness 与 compute 分离以保护凭证。
- Claude Code docs 暴露了 permission modes、tool restrictions、subagent capabilities 等治理面。
- Microsoft enterprise agent material 把 observability、durability、compliance、governance 作为 multi-agent production 的核心问题。

Durable principle:

- 不能只靠模型自律。
- 工具权限应按任务、子代理、环境和风险分级。
- 模型和 provider 升级要有 protocol，而不是感觉“新模型更强”就切。

### 8. Learning Harness

Learning Harness 负责把每次 AI 协作的经验变成下一轮更好的结构。

Substructure:

**经验记录**

- `pattern ledger`: 记录可复用模式、失败模式、适用条件、证据和下一步处置。
- `decision log`: 保存重大方向、拒绝路线和难以从代码恢复的判断背景。
- `retrospectives`: 把一段工作复盘成方法论、流程或能力缺口，而不是只留下流水账。

**规则形成**

- `failure-backed rules`: 只保留能对应真实失败、真实风险或真实反复成本的规则。
- `model / prompt / tool upgrade lessons`: 记录模型、prompt、工具或 harness 变化带来的收益、失败和迁移条件。

**外部吸收**

- `source monitoring`: 持续观察官方文档、实践者系统和社区信号，把工具前沿转成可评估的候选做法。
- `improvement roadmap`: 将复盘和外部观察转成近中长期升级项，而不是收藏链接后遗忘。

**沉淀转化**

- `rules / checklists / tests / scripts / eval cases`: 判断一条经验应该成为上下文规则、操作清单、自动检查、评测样本，还是脚本化流程。

External echoes:

- Hamel-style eval practice 把 traces 和 error analysis 变成 dataset 与改进循环。
- 社区信号显示，很多先进个人工作流都在从“每次手动提醒 AI”转向 hooks、skills、slash commands、memory files、source monitoring、run-history diffing；此类信号需要被官方文档、开源工具或多方实践重复印证后再升级为强规则。
- Augment Code 的 context essay 提醒：不是每条规则都值得写入 agent memory，规则应当能解释它预防了哪个真实失败。

Durable principle:

- 能被测试、lint、hook、script 执行的规则，不应长期占据模型上下文。
- 保留 failure-backed rules，删除 aspirational rules。
- 学习不是多写总结，而是把总结转成下一轮 harness 的入口。

## What Is Tactical vs Durable

| Category | Examples | How to use |
| --- | --- | --- |
| Current tactical | Claude Code subagent behavior, OpenAI Agents SDK sandbox providers, current MCP revision, current context-window limits, current permission modes | 适合短中期采用，但要预期工具会变化；采用时要记录版本、适用条件和迁移风险。 |
| Durable principle | simple composable workflows, context budgets, typed tools, staged artifacts, eval/error-analysis flywheel, trace provenance, approval gates | 可以沉淀成个人方法论、项目规则、checklist、eval case 或自动化检查。 |
| Speculative signal | X threads about auto-memory, Reddit discussions about AGENTS.md stubs, new process-mining tools, emerging memory-first harness claims | 作为观察雷达；只有被官方文档、开源工具或多方实践重复印证后再写入强规则。 |

## Reading Companion Implication

Reading Companion 已经在 Intent、Context、Execution、Evaluation、Learning 这几层做得很强。更明显的缺口在：

- general-purpose Tool / Environment governance
- visual / queryable Observability
- prompt-injection / permission / provider-upgrade Governance
- systematic source monitoring for frontier AI workflow ideas

这些缺口不是项目失败，而是下一阶段从“项目内 AI 协同”升级到“个人 AI Harness”的自然方向。

Use this document as the landscape map, then read [Reading Companion Gap Map](reading-companion-gap-map.md) for project evidence, [Playbook](playbook.md) for operating rules, and [Improvement Roadmap](improvement-roadmap.md) for next upgrades.
