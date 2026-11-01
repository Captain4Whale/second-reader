# Memory External Evidence Pack v1

## 研究范围与文献质量

### Research Scope & Source Quality

本轮研究严格限定在“Agent Memory 外部证据调研”，没有进入项目内部机制设计，也没有输出 Candidate Decision Ledger、Memory Ontology 正文、Formation/Management/Retrieval/Evaluation 设计文档，更没有做 GitHub 代码级诊断。对用户指定仓库 `Captain4Whale/second-reader` 的使用，只限于确认项目边界、产品定位与当前评估词汇表，用作筛选约束，而不是做实现审计。仓库 README 显示该项目是一个 Reading Companion / Reading Companion Workspace；`docs/current-state.md` 则明确了当前项目内部关心的 Memory Quality、Spontaneous Callback、False Visible Integration、inline SourceRef、以及 `active_attention / concept_registry / thread_trace` 等概念，但本报告在这些点上止步于“选择外部证据时的约束”，不做内部映射。

**Usage Note for route disclosure.** Evidence about user-visible memory management or source disclosure may inform future route-disclosure UX, but it does not justify user route choice, route preference memory, or recommendation-driven navigation in Second Reader.

本轮实际阅读结构分四档。第一档是**深读官方文档/官方页面**：[Letta Docs](https://docs.letta.com) 的 core memory / memory blocks / archival memory，[Mem0 Docs](https://docs.mem0.ai) 的 add/search/update/delete，[Zep Docs](https://help.getzep.com) 的 graph/facts/entities/observations/context block，[LangChain Docs on LangGraph memory](https://docs.langchain.com/oss/python/concepts/memory)，[LangMem README](https://github.com/langchain-ai/langmem)，以及 [Microsoft GraphRAG Docs](https://microsoft.github.io/graphrag/)。这些来源直接给出了 memory representation、operation、context assembly、retrieval、hot-path/background 写入等机制细节，因此是本轮最可靠的“实现面”证据。

第二档是**部分深读一手论文官方条目/会议页面/官方摘要页**：Generative Agents 的 Google Research 页面与 UIST 录用条目，MemoryBank 的 AAAI 页面，LoCoMo 的 ACL Anthology 页面，以及 LongMemEval、Mem0、Zep、A-MEM、CAM、ComoRAG、HippoRAG、LoCoMo-Plus、StructMemEval、HaluMem、MemoryBench、Memory-as-Action、Semantic Anchoring 等论文的 arXiv/官方摘要页。对这些来源，本轮大多做到“问题设定—机制摘要—边界判断—与 Reading Companion 的 reasoning bridge”，但并未对所有论文全文逐节精读，因此 read status 会诚实标为 partial-read 或 skimmed。

第三档是**综述/二手入口**。用户给出的知乎综述与附件 PDF 在本轮中扮演的是**入口、框架、文献线索**，不是主证据。它帮助本轮将研究面向拆成 Memory Sources / Representation / Formation / Management / Retrieval / Evaluation / Systems & Frameworks 七个区块，并暴露出若干必须回到一手来源补强的问题：比如 update/merge/consolidation/forgetting/invalidation 的操作定义到底是什么、semantic/episodic/procedural 在 agent memory 中如何分工、以及 evaluation 如何从“答对了”走向“记得对、用得好、不污染、不漂移”。这些问题最终都回到一手论文与官方文档来回答。

第四档是**没有来得及深入的 frontier 信号**。例如 MemOS、ReasoningBank、Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions、StoryBench，以及部分 reading-memory frontier（如 SGMem、Pre-Storage Reasoning for Episodic Memory、WebWeaver 等）本轮只做定位，没有把它们升格成高置信主证据。原因不是它们不重要，而是本轮目标是建立可长期沉淀的外部证据包，宁可保守标注“frontier / unvalidated”与“not read, listed for future”，也不拿未核实前沿工作做设计背书。

本轮来源置信等级可粗分为三层。**高置信**：会议/期刊正式页面、ACL Anthology、AAAI、Google Research、官方文档；**中置信**：arXiv 官方摘要页、OpenReview ARR 页面、官方 GitHub README；**低置信**：论文聚合站点的摘要镜像、研究博客、第三方解读。本报告正文里的判断尽量以前两层为依据；第三层只用于发现线索，不作为高强度论证支柱。

下一轮才应该做 Evidence-to-Project Mapping：也就是把这里得出的“哪些机制值得 adopt/adapt/reject”映射到 Reading Companion 现有 store、审计、runner settlement、source grounding、JSON/JSONL 约束与评估体系。本轮故意停在外部证据层。

### Canonical Bibliography

以下表格优先列入一手论文、正式会议页面和官方产品/框架文档。除特别标为 `secondary only` 或 `not read, listed for future` 的条目外，均有稳定链接；无法确认者标注 `Unresolved`。表中元数据优先根据官方页面、会议页面、官方 docs 或 arXiv ID 编制。代表性的元数据核验来源包括 Google Research / UIST / AAAI / ACL Anthology / Letta Docs / Mem0 Docs / Zep Docs / LangChain Docs / GraphRAG 官方站点。

| Work ID | Tier | Canonical Title | Authors / Organization | Year / First Posted | Venue / Source | Source Type | Stable URL | DOI / arXiv ID / Official Doc URL | Read Status | Maturity | Why included | Relevance to Reading Companion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M-WORK-001 | Tier 1 | Generative Agents: Interactive Simulacra of Human Behavior | Joon Sung Park et al. | 2023 | UIST 2023 / Google Research | Paper | <https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/> | DOI 10.1145/3586183.3606763 | partial-read | Established paper | reflection / memory stream / retrieval triad 的经典起点 | 对 observation→reflection 提升链路极相关 |
| M-WORK-002 | Tier 1 | MemGPT: Towards LLMs as Operating Systems | Charles Packer et al. | 2023 | arXiv | Paper | <https://arxiv.org/abs/2310.08560> | arXiv:2310.08560 | partial-read | Established paper | memory hierarchy / virtual context 的代表作 | 适合拿来划清 hot/context vs archival 的边界 |
| M-WORK-003 | Tier 1 | Letta Memory Blocks Docs | Letta | 2025–2026 docs | Letta Docs | Official framework docs | <https://docs.letta.com/guides/core-concepts/memory/memory-blocks> | Official docs | deep-read | Official framework docs | memory block contract 最具体 | 可借鉴轻量 block contract，不宜照搬 persona memory |
| M-WORK-004 | Tier 1 | Letta Archival Memory Docs | Letta | 2025–2026 docs | Letta Docs | Official framework docs | <https://docs.letta.com/guides/ade/archival-memory/> | Official docs | deep-read | Official framework docs | core vs archival 的官方分层说明 | 有助于界定 prompt-facing memory 与外部存储边界 |
| M-WORK-005 | Tier 1 | MemoryBank: Enhancing Large Language Models with Long-Term Memory | Wanjun Zhong et al. | 2023 / 2024 | AAAI 2024 | Paper | <https://ojs.aaai.org/index.php/AAAI/article/view/29946> | DOI 10.1609/aaai.v38i17.29946 | partial-read | Established paper | forgetting / reinforcement / personality memory 的早期代表 | lifecycle 概念可借鉴，user persona 部分不宜照搬 |
| M-WORK-006 | Tier 1 | Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | Prateek Chhikara et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2504.19413> | arXiv:2504.19413 | partial-read | Recent arXiv | production-ready memory operation 代表作 | 对 operation 拆分最有启发 |
| M-WORK-007 | Tier 1 | Mem0 Core Concepts Docs | Mem0 | 2025–2026 docs | Mem0 Docs | Official product docs | <https://docs.mem0.ai/core-concepts/memory-operations/add> | Official docs | deep-read | Official product docs | add/search/update/delete 细粒度操作清晰 | 可直接支持 memory_uptake_ops 的 operation 分解 |
| M-WORK-008 | Tier 1 | Zep: A Temporal Knowledge Graph Architecture for Agent Memory | Preston Rasmussen et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2501.13956> | arXiv:2501.13956 | partial-read | Recent arXiv | temporal fact invalidation / enterprise memory | 对 supersede / invalidate 思路有价值 |
| M-WORK-009 | Tier 1 | Zep Graph / Facts / Entities / Observations Docs | Zep | 2025–2026 docs | Zep Docs | Official product docs | <https://help.getzep.com/graph-overview> | Official docs | deep-read | Official product docs | facts / entities / episodes / observations 分层最清楚 | 可借鉴时态语义与 evidence-backed pattern，不必上 graph DB |
| M-WORK-010 | Tier 1 | A-MEM: Agentic Memory for LLM Agents | Wujiang Xu et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2502.12110> | arXiv:2502.12110 | partial-read | Recent arXiv | structured note / links / evolution | 对 structured note 比纯字符串更相关 |
| M-WORK-011 | Tier 1 | LangGraph Memory Overview | LangChain | 2025–2026 docs | LangChain Docs | Official framework docs | <https://docs.langchain.com/oss/python/concepts/memory> | Official docs | deep-read | Official framework docs | semantic/episodic/procedural + hot/background | 对 memory type split 与写入时机极有参考值 |
| M-WORK-012 | Tier 1 | LangMem | LangChain | 2025–2026 | GitHub README / docs | Official framework docs | <https://github.com/langchain-ai/langmem> | Official repo/docs | deep-read | Official framework docs | background memory manager / prompt refinement | 对 background consolidation 与 procedural memory 有代表性 |
| M-WORK-013 | Tier 1 | RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval | Parth Sarthi et al. | 2024 | arXiv | Paper | <https://arxiv.org/abs/2401.18059> | arXiv:2401.18059 | skimmed | Established paper | hierarchical summarization tree 的代表 | 对多粒度 frame 有启发，但更像 corpus index |
| M-WORK-014 | Tier 1 | From Local to Global: A Graph RAG Approach to Query-Focused Summarization | Darren Edge et al. | 2024 | arXiv / GraphRAG site | Paper | <https://arxiv.org/abs/2404.16130> | arXiv:2404.16130 | partial-read | Established paper | global sensemaking 与 community summaries | 对全局聚合启发强，对基础设施启发需谨慎 |
| M-WORK-015 | Tier 1 | GraphRAG Docs | Microsoft Research | 2024–2026 docs | GraphRAG Docs | Official framework docs | <https://microsoft.github.io/graphrag/index/overview/> | Official docs | deep-read | Official framework docs | local/global/DRIFT query modes | 可帮助界定 “聚合检索” 与 “memory” 的边界 |
| M-WORK-016 | Tier 1 | LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory | Di Wu et al. | 2024 | arXiv | Paper | <https://arxiv.org/abs/2410.10813> | arXiv:2410.10813 | partial-read | Established paper | 形成—检索—阅读三阶段评估拆解 | 对 Reading Companion 的 evaluation decomposition 很关键 |
| M-WORK-017 | Tier 1 | Evaluating Very Long-Term Conversational Memory of LLM Agents | Adyasha Maharana et al. | 2024 | ACL 2024 | Paper | <https://aclanthology.org/2024.acl-long.747/> | DOI 10.18653/v1/2024.acl-long.747 | partial-read | Established paper | very-long dialogue / temporal-causal continuity | 对跨 session / temporal continuity 的 benchmark 很重要 |
| M-WORK-018 | Tier 1 | LoCoMo-Plus: Beyond-Factual Cognitive Memory Evaluation Framework for LLM Agents | Yifei Li et al. | 2026 | OpenReview / arXiv | Paper | <https://openreview.net/forum?id=QWVKrMGdah> | arXiv:2602.10715 | skimmed | Frontier / unvalidated | latent constraints / cue-trigger disconnect | 对“最终答对但记忆隐约错位”的风险非常相关 |
| M-WORK-019 | Tier 1 | Evaluating Memory Structure in LLM Agents | Alina Shutova et al. | 2026 | arXiv | Paper | <https://arxiv.org/abs/2602.11243> | arXiv:2602.11243 | skimmed | Frontier / unvalidated | memory structure benchmark | 对 structure-aware evaluation 很有价值 |
| M-WORK-020 | Tier 1 | MemoryBench: A Benchmark for Memory and Continual Learning in LLM Systems | Qingyao Ai et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2510.17281> | arXiv:2510.17281 | skimmed | Frontier / unvalidated | continual update / memory learning | 对 update / forgetting / continuality 是补充信号 |
| M-WORK-021 | Tier 1 | HaluMem: Evaluating Hallucinations in Memory Systems of Agents | Ding Chen et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2511.03506> | arXiv:2511.03506 | skimmed | Frontier / unvalidated | operation-level hallucination benchmark | 对形成/更新阶段污染诊断极关键 |
| M-WORK-022 | Tier 1 | CAM: A Constructivist View of Agentic Memory for LLM-Based Reading Comprehension | Rui Li et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2510.05520> | arXiv:2510.05520 | partial-read | Frontier / unvalidated | reading-specific memory design | 与 Reading Companion 的任务形态最接近之一 |
| M-WORK-023 | Tier 1 | ComoRAG: A Cognitive-Inspired Memory-Organized RAG for Stateful Long Narrative Reasoning | Juyuan Wang et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2508.10419> | arXiv:2508.10419 | partial-read | Frontier / unvalidated | long narrative reasoning / dynamic memory workspace | 对 narrative continuity 与 probing retrieval 很相关 |
| M-WORK-024 | Tier 1 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models | Bernal Jiménez Gutiérrez et al. | 2024 | arXiv | Paper | <https://arxiv.org/abs/2405.14831> | arXiv:2405.14831 | partial-read | Recent arXiv | graph-indexed multi-hop retrieval | 对 concept/thread 链接结构有启发 |
| M-WORK-025 | Tier 1 | Semantic Anchoring in Agentic Memory: Leveraging Linguistic Structures for Persistent Conversational Context | Maitreyi Chatterjee, Devansh Agarwal | 2025 | arXiv | Paper | <https://arxiv.org/abs/2508.12630> | arXiv:2508.12630 | skimmed | Frontier / unvalidated | linguistic anchors / discourse / coreference | 对 source-grounded textual memory 很贴近 |
| M-WORK-026 | Tier 1 | MemGuide: Intent-Driven Memory Selection for Goal-Oriented Multi-Session LLM Agents | Yiming Du et al. | 2025 / 2026 | AAAI 2026 | Paper | <https://ojs.aaai.org/index.php/AAAI/article/view/40313> | DOI 10.1609/aaai.v40i36.40313 | partial-read | Established paper | intent-aligned retrieval | 对“按当前阅读意图选记忆”很有启发 |
| M-WORK-027 | Tier 1 | Memory as Action: Autonomous Context Curation for Long-Horizon Agentic Tasks | Yuxiang Zhang et al. | 2025 | arXiv | Paper | <https://arxiv.org/abs/2510.12635> | arXiv:2510.12635 | partial-read | Frontier / unvalidated | working memory editing as policy | 主要用于划边界：当前 RC 不应走 RL 记忆编辑 |
| M-WORK-028 | Tier 2 | A Survey on the Memory Mechanism of Large Language Model based Agents | — | 2024 | arXiv | Survey | <https://arxiv.org/abs/2404.13501> | arXiv:2404.13501 | secondary only | Secondary / background only | 作为术语与脉络背景 | 不是高置信设计依据 |
| M-WORK-029 | Tier 2 | MemOS: A Memory OS for AI System | — | 2025 | arXiv | Paper | <https://arxiv.org/abs/2507.03724> | arXiv:2507.03724 | not read, listed for future | Frontier / unvalidated | memory OS 趋势代表 | 当前 RC 过重，主要用于 boundary 判断 |
| M-WORK-030 | Tier 2 | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions | — | 2025 | arXiv | Paper | <https://arxiv.org/abs/2507.05257> | arXiv:2507.05257 | not read, listed for future | Frontier / unvalidated | 增量多轮评估可能补足现有 benchmark 缺口 | 值得下一轮 deep-read |
| M-WORK-031 | Tier 2 | StoryBench: A Dynamic Benchmark for Evaluating Long-Term Memory with Multi Turns | — | 2025 | arXiv | Paper | <https://arxiv.org/abs/2506.13356> | arXiv:2506.13356 | not read, listed for future | Frontier / unvalidated | narrative / multi-turn benchmark 线索 | 可作为 reading-specific evaluation 候选 |
| M-WORK-032 | Tier 3 | Beyond Goldfish Memory: Long-Term Open-Domain Conversation | — | 2021 | arXiv | Paper | <https://arxiv.org/abs/2107.07567> | arXiv:2107.07567 | not read, listed for future | Classic theory | 早期 long-term conversation 背景 | 主要是历史背景，不是当前主证据 |

## 外部领域地图

### External Memory Field Map

| Area | Core question | Representative works | Why it matters | Risk if copied blindly |
| --- | --- | --- | --- | --- |
| Memory Sources | memory 来自哪里：对话、事件、工具结果、文档、运行轨迹，还是 source-grounded observations？ | Generative Agents, Mem0, Zep, LangGraph | 决定“什么有资格进 memory” | 把 source corpus 本身误当 memory |
| Memory Representations | memory 是纯字符串、结构化 note、profile、collection、fact graph，还是 summary？ | Letta, A-MEM, Zep, LangGraph | 决定可解释性、可审计性与更新难度 | 过早引入 graph/vector infra |
| Working / Episodic / Semantic / Procedural | 不同记忆类型如何分工？ | LangGraph, LangMem, Zep, MemGPT | 有助于避免把所有状态都塞进一个桶 | 类型过多导致抽象先行、实现过重 |
| Memory Formation | 何时从 observation 变成 durable memory？ | Generative Agents, Mem0, CAM, A-MEM | 直接影响污染率与 recall 质量 | “逢读必记”“逢句必记” |
| Semantic Summarization | 什么该被压缩为 summary / frame？ | RAPTOR, GraphRAG, Zep entity summary | 有助于建立多粒度入口 | 把 summary 当事实真值 |
| Knowledge Distillation / Extraction | 如何从 原始交互/文本 中抽取可复用知识？ | Mem0, Zep, CAM, Semantic Anchoring | 支撑 source-grounded 提炼 | 抽取器先天高幻觉、无审计 |
| Structured Construction | memory item 是否该有 schema、标签、链接、ID？ | Letta blocks, A-MEM, Mem0, LangGraph profile/collection | 决定更新、审计、merge 的可操作性 | schema 过重拖累通用性 |
| Reflection / Consolidation | 哪些低层 observation 应当上升为高层 memory？ | Generative Agents, LangMem, Zep observations | 对 slow-cycle / chapter-level consolidation 很关键 | 反思过频、反思无证据、反思漂移 |
| Memory Management / Evolution | memory 生命周期如何演进？ | MemoryBank, Mem0, Zep, A-MEM, LangMem | 决定 update / supersede / forgetting | 只有 add 没有 revise/delete |
| Update / Refresh / Merge / Forgetting / Invalidation | 当后文修正前文时怎么办？ | MemoryBank, Mem0, Zep facts/observations | 是 reading continuity 的核心难题 | 旧记忆与新记忆并存导致 visible integration 错误 |
| Memory Retrieval | 何时、按何种线索找回 memory？ | Generative Agents, Mem0, Zep, MemGuide | 直接影响 recall precision | 单一 semantic top-k 无法覆盖时序/意图 |
| Context Engineering | 检索到的 memory 怎么装进上下文？ | MemGPT, Letta, Zep context block, GraphRAG | retrieval ≠ assembly，组装本身是设计问题 | 把“检索”与“提示拼接”混为一谈 |
| Storage / Indexing | file/json、vector、graph、hybrid 哪个必要？ | Mem0, Zep, GraphRAG, RAPTOR | 影响复杂度与演进路径 | 基础设施先行，超出产品必要性 |
| Audit / Observability | 如何知道 memory 是怎么进来的、怎么被更新的？ | Mem0 ops, Zep facts/episodes, HaluMem | 对 source-grounded / traceability 至关重要 | 没有 operation trace，评估无法定位失败层 |
| Memory Evaluation | 如何证明记得对、用得好、不污染、不漂移？ | LongMemEval, LoCoMo, LoCoMo-Plus, StructMemEval, MemoryBench, HaluMem | 防止只看最终 QA 对错 | 用单一 correctness 掩盖上游错误 |
| Production Memory Systems | 真实系统怎么把 memory API 产品化？ | Letta, Mem0, Zep, LangGraph/LangMem | 给出 operation contract 与实现边界 | 产品 docs 可能偏聊天/用户画像，不可直接平移 |
| Reading / Narrative Memory | 长文本、叙事、角色关系、主题线索如何保持？ | CAM, ComoRAG, HippoRAG, Semantic Anchoring | 和 Reading Companion 任务最接近 | 把 narrative RAG 直接当 agent memory |
| Agent Framework Memory Patterns | 框架层怎样教开发者分 memory？ | LangGraph, LangMem, Letta | 有助于抽象出低复杂度模式 | 框架语义未必适合以 source 为中心的阅读任务 |
| Frontier Memory OS / Self-evolving Memory | memory 是否应成为 OS / policy learner？ | MemGPT, MemOS, Memory-as-Action | 有助于划边界，防止过度乐观 | 容易把系统做成过重、不可审计、难落地 |

## Tier 1 Work Cards

### Work Card: Generative Agents

- Work ID: M-WORK-001
- Source link: <https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/>
- Authors / Organization: Joon Sung Park et al.
- Year / First Posted: 2023
- Venue / Source: UIST 2023 / Google Research
- Source Type: Paper
- Read status: partial-read
- Maturity: Established paper
- Original problem: 让 LLM 代理在开放世界模拟中维持可信、连续、可规划的行为
- Target agent / system setting: 社会模拟 agent；以 observation-driven 行为生成与计划为核心
- Memory ontology: memory stream + 反思层 + 计划层
- Memory representation: 以自然语言 observation / reflection / plan 为主
- Memory formation: 新 observation 持续写入；超过阈值时触发 reflection，把多条 observation 提升为高层判断
- Memory management / evolution: 通过 recency / relevance / importance 选择检索；high-level reflections 会影响后续 planning
- Memory retrieval: recency + relevance + importance 的组合检索
- Context engineering: 把检索到的 memories 注入规划与下一步行为生成
- Memory evaluation: 重点看行为连续性、社会互动与 emergent coordination
- Key mechanisms: memory stream；importance scoring；reflection trigger；observation→reflection→planning 循环
- What it directly supports: “并非每个单位都应变成 durable memory”；高层 frame 应从多个低层 observation 中提炼
- What it only analogically supports: 阅读中的 chapter/frame consolidation
- What it argues against: 把每个 read unit 都等价写入高层 memory
- Fit to Reading Companion: 很适合支撑“低层 reading observation → 慢周期 reflective memory”的设计方向，尤其是说明为什么 reflection 应该是节流后的 second-order operation
- Misfit / limitation: 原场景是社会行为规划，不是 source-grounded reading；其 high-level reflection 并不天然绑定可审计 source evidence
- Complexity implication: 引入 reflection 后，必须同时设计触发条件、证据保留、反思去重
- Candidate project-relevant implications: 适合作为“为什么需要 slow-cycle consolidation”的外部证据，不适合作为最终 storage schema
- Evidence strength: 中高；概念经典，但对 source-grounding 的回答不够直接

### Work Card: MemGPT / Letta

- Work ID: M-WORK-002 / M-WORK-003 / M-WORK-004
- Source link: <https://arxiv.org/abs/2310.08560>；<https://docs.letta.com/guides/core-concepts/memory/memory-blocks>；<https://docs.letta.com/guides/ade/archival-memory/>
- Authors / Organization: Charles Packer et al.; Letta
- Year / First Posted: 2023; docs 2025–2026
- Venue / Source: arXiv; Letta Docs
- Source Type: Paper + Official framework docs
- Read status: MemGPT partial-read；Letta docs deep-read
- Maturity: MemGPT Established paper；Letta Official framework docs
- Original problem: 在有限 context 窗口下维持看似“无限”的可用上下文
- Target agent / system setting: 长对话与文档分析 agent；stateful agent platform
- Memory ontology: in-context/core memory vs out-of-context/archival memory
- Memory representation: memory blocks（label/description/value/limit）；archival memory fragments
- Memory formation: core block 可被 agent 编辑；archival memory 可 insert/search
- Memory management / evolution: 以层级与 paging/view 管理 context scarcity
- Memory retrieval: archival memory 通过 semantic search；core memory 无需检索、总可见
- Context engineering: 很强调 always-visible block 与 out-of-context retrieval 的边界
- Memory evaluation: 更偏系统行为而非严格 memory benchmark
- Key mechanisms: virtual context；memory hierarchy；memory blocks；always-visible memory；archival search
- What it directly supports: 区分 prompt-facing hot memory 与 authoritative durable memory；使用 block contract 明确用途和上限
- What it only analogically supports: reading memory 的 hot/durable 层次区分
- What it argues against: 把全部 memory 都塞进 prompt；也反对没有 contract 的自由拼接
- Fit to Reading Companion: 很适合支撑“轻量 contract”“有限 always-visible slots”“authoritative store 与 prompt projection 区分”
- Misfit / limitation: MemGPT/Letta 默认重心是聊天助手、persona/user memory、多 agent 协调；这与 source-grounded reading memory 并不等价
- Complexity implication: 如果照搬 OS-style paging，会迅速把 RC 推向 context OS，而非 reading memory
- Candidate project-relevant implications: 可借鉴 block 的 label/description/value/limit 约束；不宜照搬 human/persona 双块与多 agent shared memory
- Evidence strength: 高于一般论文方向，因为 docs 给出了实际 contract

### Work Card: MemoryBank

- Work ID: M-WORK-005
- Source link: <https://ojs.aaai.org/index.php/AAAI/article/view/29946>
- Authors / Organization: Wanjun Zhong et al.
- Year / First Posted: 2023 / AAAI 2024
- Venue / Source: AAAI 2024
- Source Type: Paper
- Read status: partial-read
- Maturity: Established paper
- Original problem: companion / counseling / assistant 长期对话中的长期记忆与人格理解
- Target agent / system setting: user-centric companion/chat setting
- Memory ontology: long-term memory with user personality synthesis
- Memory representation: memories extracted from long dialogs
- Memory formation: 从对话中抽取并存储长期相关内容
- Memory management / evolution: 借鉴遗忘曲线按时间与重要性进行强化或遗忘
- Memory retrieval: 按相关记忆召回服务对话
- Context engineering: 为当前多轮对话提供长期 user context
- Memory evaluation: 以长期陪伴、共情、人格理解为主
- Key mechanisms: forgetting curve；importance/time-aware retention；personality synthesis
- What it directly supports: 记忆可有生命周期，而不是只增不减
- What it only analogically supports: reading state 中“衰减/刷新/再激活”的逻辑
- What it argues against: 静态、永不淘汰的 memory store
- Fit to Reading Companion: 支持“不是所有 durable memory 都应永久等权保留”
- Misfit / limitation: 其核心对象是 user profile / companion continuity，不是 text-grounded reading state；人格画像那一部分对 RC 基本是负迁移
- Complexity implication: 一旦引入 forgetting，必须说明丢失的是热度、可见性还是事实有效性
- Candidate project-relevant implications: 可借鉴 refresh / reinforcement / decay 概念；但不能把 “读者画像” 当主记忆对象
- Evidence strength: 中等；方向有价值，但场景错位明显

### Work Card: Mem0

- Work ID: M-WORK-006 / M-WORK-007
- Source link: <https://arxiv.org/abs/2504.19413>；<https://docs.mem0.ai/core-concepts/memory-operations/add>
- Authors / Organization: Prateek Chhikara et al.; Mem0
- Year / First Posted: 2025
- Venue / Source: arXiv; Mem0 Docs
- Source Type: Paper + Official product docs
- Read status: paper partial-read；docs deep-read
- Maturity: Recent arXiv + Official product docs
- Original problem: 把长期 memory 从实验性组件变成 production-ready capability
- Target agent / system setting: production AI agents / multi-session memory
- Memory ontology: memory items with IDs, metadata, optional graph layer
- Memory representation: extracted memories + metadata + timestamps；可选 graph memory
- Memory formation: 明确拆成 information extraction → conflict resolution → storage
- Memory management / evolution: add / search / update / delete 是一等操作
- Memory retrieval: vector search + filters + rerank + thresholds
- Context engineering: 搜索结果回传给 agent / service，再由上层做 prompt assembly
- Memory evaluation: 论文中强调长期一致性与效率；docs 中强调操作可控性
- Key mechanisms: operation-centric memory API；metadata scoping；explicit update/delete；optional graph memory
- What it directly supports: `memory_uptake_ops` 不应只是一坨“写入”，而应拆成抽取、冲突解析、落库、更新、删除
- What it only analogically supports: 面向 reading run 的 store pipeline
- What it argues against: 只有 append、没有 revision 的 memory
- Fit to Reading Companion: 是最适合作为“操作分解与 item lifecycle”外部证据的一组来源
- Misfit / limitation: 默认语境仍偏聊天/用户偏好；graph memory 不是必需前提
- Complexity implication: 借鉴 Mem0 时，真正该先引入的是 ID、metadata、update/delete，而不是 vector/graph infra
- Candidate project-relevant implications: 对 JSON/JSONL 时代的轻量 operation contract 特别有借鉴价值
- Evidence strength: 高

### Work Card: Zep

- Work ID: M-WORK-008 / M-WORK-009
- Source link: <https://arxiv.org/abs/2501.13956>；<https://help.getzep.com/graph-overview>
- Authors / Organization: Preston Rasmussen et al.; Zep
- Year / First Posted: 2025
- Venue / Source: arXiv; Zep Docs
- Source Type: Paper + Official product docs
- Read status: paper partial-read；docs deep-read
- Maturity: Recent arXiv + Official product docs
- Original problem: 企业/多轮 agent 需要处理动态事实、跨 session 关系和时序更新
- Target agent / system setting: enterprise agent memory / graph-backed memory layer
- Memory ontology: episodes / entities / facts / observations / user summary
- Memory representation: temporal knowledge graph；fact 的 valid/invalid timestamps；entity summaries；observations
- Memory formation: 从 episodes 中抽 entity/fact，再进一步衍生 summaries/observations
- Memory management / evolution: dedup、merge、invalidate、retire older observations
- Memory retrieval: context block 自动装配 facts/entities/episodes；observations 默认不自动进 block
- Context engineering: default context block、templates、advanced construction 三层控制
- Memory evaluation: 论文以 DMR 与 LongMemEval 为代表；docs 更强调 temporal accuracy
- Key mechanisms: precise facts vs summaries；valid_at / invalid_at；episodes as evidence；observation as durable pattern
- What it directly supports: 当新理解推翻旧理解时，需要 explicit supersede / invalidate 语义
- What it only analogically supports: concept/thread/frame 的多层组织
- What it argues against: 只用 summary、不保留 granularity 与时间效力
- Fit to Reading Companion: 非常适合支撑“原始 observation—概念/实体—关系/线程—高层 pattern”分层思路
- Misfit / limitation: graph DB 与自动实体图谱不是 RC 当前优先级；其默认 user-summary / enterprise context block 也不适合直接照搬
- Complexity implication: 适合借 concept，而不适合直接引入整套 graph stack
- Candidate project-relevant implications: 可借鉴 temporal validity、事实与摘要分离、observation 不默认 always-visible
- Evidence strength: 高

### Work Card: A-MEM / LangGraph / LangMem Memory Patterns

- Work ID: M-WORK-010 / M-WORK-011 / M-WORK-012
- Source link: <https://arxiv.org/abs/2502.12110>；<https://docs.langchain.com/oss/python/concepts/memory>；<https://github.com/langchain-ai/langmem>
- Authors / Organization: Wujiang Xu et al.; LangChain
- Year / First Posted: 2025
- Venue / Source: arXiv + framework docs
- Source Type: Paper + Official framework docs
- Read status: A-MEM partial-read；LangGraph/LangMem deep-read
- Maturity: Recent arXiv + Official framework docs
- Original problem: memory 不应只是“存了能搜”，还要能组织、分类、演化，并在热路径与后台路径中分工
- Target agent / system setting: general agents / framework patterns
- Memory ontology: semantic / episodic / procedural；profile vs collection；structured notes with tags/keywords/links
- Memory representation: JSON profile、document collection、few-shot episodes、refined instructions、structured note
- Memory formation: hot-path write 与 background extraction/consolidation 双路径
- Memory management / evolution: consolidate、update knowledge、prompt refinement、memory consistency
- Memory retrieval: search memory tools；few-shot episodic selection；collection/profile retrieval
- Context engineering: profile 或 selected items 进入 prompt；procedural memory 可回写 instruction
- Memory evaluation: 更多是开发模式与实践指导，而非标准 benchmark
- Key mechanisms: profile vs collection；semantic/episodic/procedural split；background manager；prompt refinement；structured note/linking
- What it directly supports: RC memory item 不必是纯字符串；links/tags/source_refs 可以成为轻量组织骨架
- What it only analogically supports: procedural memory 映射到 reading policy / prompt refinement
- What it argues against: 把所有 information 一律写入同一列表
- Fit to Reading Companion: 对 item schema、write timing、memory type split 最有实际开发参考价值
- Misfit / limitation: 框架文档以 user/application memory 为主，profile 模式对 RC 可能不如 collection/note 模式合适；A-MEM 的自由动态网络也可能过重
- Complexity implication: 最好借用其“分类与写入时机”的思想，而不是连带引入 framework-shaped storage
- Candidate project-relevant implications: structured note、profile/collection 二选一、hot/background 分工、prompt refinement 作为 procedural memory 候选
- Evidence strength: 高于纯论文方向

### Work Card: RAPTOR

- Work ID: M-WORK-013
- Source link: <https://arxiv.org/abs/2401.18059>
- Authors / Organization: Parth Sarthi et al.
- Year / First Posted: 2024
- Venue / Source: arXiv
- Source Type: Paper
- Read status: skimmed
- Maturity: Established paper
- Original problem: 长文问答中，单层 chunk retrieval 缺乏全局视角
- Target agent / system setting: retrieval-augmented QA over long documents
- Memory ontology: 不是 agent memory ontology，而是 corpus summarization tree
- Memory representation: chunk → cluster → summary → tree
- Memory formation: recursive embedding / clustering / summarization
- Memory management / evolution: 主要是索引构建，不是会话内 memory lifecycle
- Memory retrieval: multi-granularity tree retrieval
- Context engineering: 用不同层级 summary 提供不同抽象度上下文
- Memory evaluation: long-document QA
- Key mechanisms: recursive abstraction；hierarchical retrieval；multi-granularity summaries
- What it directly supports: 高层 reflective frame 作为 retrieval entry 的想法
- What it only analogically supports: chapter-level 或 book-level frame 的构建
- What it argues against: 只检索局部 chunk 就能解决长文全局理解
- Fit to Reading Companion: 适合作为“高层 frame 可能有独立检索价值”的证据
- Misfit / limitation: 它本质是 corpus index，不是阅读中逐步形成的 agent memory
- Complexity implication: 如果直接照搬 tree index，会把 RC 引到重型 precomputed hierarchy
- Candidate project-relevant implications: 可吸收“多粒度入口”，不宜直接上树索引
- Evidence strength: 中等

### Work Card: GraphRAG

- Work ID: M-WORK-014 / M-WORK-015
- Source link: <https://arxiv.org/abs/2404.16130>；<https://microsoft.github.io/graphrag/index/overview/>
- Authors / Organization: Darren Edge et al.; Microsoft Research
- Year / First Posted: 2024
- Venue / Source: arXiv; official docs
- Source Type: Paper + Official framework docs
- Read status: paper partial-read；docs deep-read
- Maturity: Established paper + Official framework docs
- Original problem: 回答“全局 sensemaking”问题时，向量 RAG 无法从单个 chunk 得到整体答案
- Target agent / system setting: corpora-level QFS / GraphRAG
- Memory ontology: entity graph + community summaries
- Memory representation: extracted entities/relations/claims + hierarchical community reports
- Memory formation: graph extraction + community detection + summary generation
- Memory management / evolution: 主要是 indexing pipeline 的再生成，不是细粒度 memory lifecycle
- Memory retrieval: local search / global search / DRIFT search
- Context engineering: map-reduce over community summaries
- Memory evaluation: global question answering / comprehensiveness / diversity
- Key mechanisms: local-to-global retrieval；community summaries；local/global mode split
- What it directly supports: global sensemaking 需要更高层聚合结构，而不是只搜原子片段
- What it only analogically supports: book-level concept/thread/frame 的轻量链接
- What it argues against: 在全局问题上只做 top-k chunk retrieval
- Fit to Reading Companion: 适合作为“为什么需要轻量结构化聚合”的外部依据
- Misfit / limitation: 它更像 corpus analytics stack，不是 run-internal reading memory；图抽取和社区摘要成本高
- Complexity implication: 如果没有强烈全局问答需求，不应直接引入 GraphRAG 基建
- Candidate project-relevant implications: 吸收 local/global distinction 与高层聚合思想；拒绝直接上 graph stack
- Evidence strength: 高

### Work Card: LongMemEval

- Work ID: M-WORK-016
- Source link: <https://arxiv.org/abs/2410.10813>
- Authors / Organization: Di Wu et al.
- Year / First Posted: 2024
- Venue / Source: arXiv
- Source Type: Paper
- Read status: partial-read
- Maturity: Established paper
- Original problem: 聊天助手的长期记忆能力缺乏系统 benchmark
- Target agent / system setting: multi-session chat assistants
- Memory ontology: 不直接规定 ontology，而是拆成 indexing / retrieval / reading 三阶段
- Memory representation: benchmark-specific histories + questions
- Memory formation: 评估信息抽取能力
- Memory management / evolution: 评估 knowledge updates / temporal reasoning / abstention
- Memory retrieval: 强调 retrieval stage 的独立作用
- Context engineering: reading stage 单列出来，避免把检索命中率等同于最终可用性
- Memory evaluation: information extraction、multi-session reasoning、temporal reasoning、knowledge updates、abstention 五项核心能力
- Key mechanisms: stage decomposition；session decomposition；fact-augmented key expansion；time-aware query expansion
- What it directly supports: RC 评估不应只看最终回答；formation / retrieval / utilization 应分层诊断
- What it only analogically supports: reading run / chapter span 上的多阶段 memory evaluation
- What it argues against: 把 QA correctness 当 memory 唯一指标
- Fit to Reading Companion: 是建立“阶段化评估面板”最强的外部证据之一
- Misfit / limitation: benchmark 场景主要还是 chat history，不是 source-grounded reading observations
- Complexity implication: 若采用其思路，RC 必须保有足够 trace 才能分层定位
- Candidate project-relevant implications: future evaluation 应至少区分 formation、retrieval、usefulness、abstention
- Evidence strength: 高

### Work Card: LoCoMo / LoCoMo-Plus

- Work ID: M-WORK-017 / M-WORK-018
- Source link: <https://aclanthology.org/2024.acl-long.747/>；<https://openreview.net/forum?id=QWVKrMGdah>
- Authors / Organization: Adyasha Maharana et al.; Yifei Li et al.
- Year / First Posted: 2024; 2026
- Venue / Source: ACL 2024; OpenReview/ARR 2026
- Source Type: Paper
- Read status: LoCoMo partial-read；LoCoMo-Plus skimmed
- Maturity: Established paper + Frontier / unvalidated
- Original problem: 评估 very long-term conversation 中的 temporal/causal continuity，与 beyond-factual cognitive memory
- Target agent / system setting: very long conversational memory
- Memory ontology: benchmark-driven；包含 persona、事件图、latent constraints
- Memory representation: long multi-session dialogues + event graphs / cognitive constraints
- Memory formation: 更强调“系统是否把长期上下文组织起来”，不是某个固定 formation 机制
- Memory management / evolution: 测 temporal causality、event continuity、latent constraints 持续生效
- Memory retrieval: 对 long-context、RAG、memory systems 做困难对抗
- Context engineering: 暴露出“表面事实对了，但隐性约束没被维持”的失败模式
- Memory evaluation: QA、event summarization、multimodal dialogue generation；LoCoMo-Plus 进一步测 cue-trigger semantic disconnect 下的 constraint consistency
- Key mechanisms: temporal event graph benchmark；latent constraint evaluation；constraint consistency
- What it directly supports: 评估中必须把“隐含约束持续有效”独立出来
- What it only analogically supports: chapter order、叙事连续性、隐式阅读约束
- What it argues against: 只考 explicit factual recall 就等于 memory 很好
- Fit to Reading Companion: 非常适合启发 temporal / chapter-order / latent-constraint 风险面
- Misfit / limitation: 仍是对话 benchmark；LoCoMo-Plus 仍属于前沿，成熟度不足
- Complexity implication: 若直接迁入 RC，需先明确“阅读中的 latent constraints”到底指什么
- Candidate project-relevant implications: 未来 RC 评估不能只看明面 recall，还要看隐式 continuity
- Evidence strength: 中高；LoCoMo 高于 LoCoMo-Plus

### Work Card: StructMemEval / MemoryBench / HaluMem

- Work ID: M-WORK-019 / M-WORK-020 / M-WORK-021
- Source link: <https://arxiv.org/abs/2602.11243>；<https://arxiv.org/abs/2510.17281>；<https://arxiv.org/abs/2511.03506>
- Authors / Organization: Alina Shutova et al.; Qingyao Ai et al.; Ding Chen et al.
- Year / First Posted: 2025–2026
- Venue / Source: arXiv
- Source Type: Papers
- Read status: skimmed
- Maturity: Frontier / unvalidated
- Original problem: 现有 benchmark 太偏 factual recall，无法测结构组织、持续学习、operation-level hallucination
- Target agent / system setting: long-term memory systems / continual memory / memory operations
- Memory ontology: 更关注“memory system 的能力面”而非某种单一 ontology
- Memory representation: structure tasks / continual update tasks / extraction-update-QA tasks
- Memory formation: HaluMem 显式拆 extraction；MemoryBench 关心 sim user feedback 下的持续学习
- Memory management / evolution: update / forgetting / continual adaptation / conflict/omission
- Memory retrieval: 不是核心唯一对象，而是系统整体的一环
- Context engineering: 主要是用 benchmark 暴露 failure localization
- Memory evaluation: Structure-aware；continual learning aware；operation-level hallucination
- Key mechanisms: structure benchmark；continual update benchmark；operation-level hallucination benchmark
- What it directly supports: RC 需要 structure-aware + operation-aware evaluation，而不是只看终端答案
- What it only analogically supports: 将 RC 的 read audit / settlement audit 升级为 memory operation audit
- What it argues against: 只用一个 aggregate correctness score 做 memory 评估
- Fit to Reading Companion: 对“污染可能发生在 formation/update，不只在最终输出”的判断极有帮助
- Misfit / limitation: 都较新，尚未形成成熟共识；且场景并不专门针对阅读 agents
- Complexity implication: 评估想做细，必须先有 trace
- Candidate project-relevant implications: operation-level audit 优先级很高，但应先确保 traceability 再立 rubric
- Evidence strength: 中等

### Work Card: CAM

- Work ID: M-WORK-022
- Source link: <https://arxiv.org/abs/2510.05520>
- Authors / Organization: Rui Li et al.
- Year / First Posted: 2025
- Venue / Source: arXiv
- Source Type: Paper
- Read status: partial-read
- Maturity: Frontier / unvalidated
- Original problem: 长文阅读理解中的 agentic memory 缺乏系统设计原则
- Target agent / system setting: LLM-based reading comprehension
- Memory ontology: constructivist memory / schemata
- Memory representation: structured memory with incremental overlapping clustering + hierarchical summaries
- Memory formation: assimilation / accommodation 风格的在线整合
- Memory management / evolution: online batch integration into growing structure
- Memory retrieval: 沿 memory structure 自适应激活 query-relevant information
- Context engineering: 用 memory structure 辅助后续阅读与作答
- Memory evaluation: 多类长文本理解任务
- Key mechanisms: constructivist schemata；incremental overlapping clustering；adaptive activation
- What it directly supports: reading-specific memory 不必复制 chatbot memory；它可以围绕文本理解而组织
- What it only analogically supports: reflective frames / concept aggregation
- What it argues against: 纯 heuristic chunk cache 足以支撑复杂长文理解
- Fit to Reading Companion: 是最贴近 RC 任务面的 frontier 之一
- Misfit / limitation: 仍是研究型原型；其 clustering 复杂度与结构构建成本需谨慎
- Complexity implication: 若采纳，只能吸收“reading-specific organization”原则，不能直接搬结构算法
- Candidate project-relevant implications: RC 的 memory ontology 应针对阅读而非聊天设计
- Evidence strength: 中等

### Work Card: ComoRAG

- Work ID: M-WORK-023
- Source link: <https://arxiv.org/abs/2508.10419>
- Authors / Organization: Juyuan Wang et al.
- Year / First Posted: 2025
- Venue / Source: arXiv
- Source Type: Paper
- Read status: partial-read
- Maturity: Frontier / unvalidated
- Original problem: 长叙事推理中，stateless single-step RAG 容易“丢剧情”
- Target agent / system setting: long narrative reasoning
- Memory ontology: dynamic memory workspace + global memory pool
- Memory representation: iterative retrieved evidence + consolidated workspace
- Memory formation: reasoning impasse 时生成 probing queries，吸收新证据进入 memory pool
- Memory management / evolution: memory workspace 在多轮迭代中扩展与整合
- Memory retrieval: iterative retrieval，不是一次 top-k
- Context engineering: 每个循环都让过去知识与新证据交互
- Memory evaluation: long-context narrative benchmarks
- Key mechanisms: probing queries；dynamic workspace；iterative retrieval-consolidation cycles
- What it directly supports: 阅读 agent 在“理解卡住”时可触发针对性 recall / retrieval，而非无差别检索
- What it only analogically supports: 阅读中的 detour / look-back / targeted recall
- What it argues against: narrative reasoning 可由一次检索完成
- Fit to Reading Companion: 很贴近 stateful long-form reasoning；尤其适合证明为什么 memory retrieval 应当与 ongoing reasoning 互动
- Misfit / limitation: 属于 narrative RAG，不是 source-grounded memory ontology 本身
- Complexity implication: 若照搬 iterative loop，会让 runtime 显著复杂化
- Candidate project-relevant implications: 可借“impasse-triggered targeted recall”，不宜照搬整套 iterative RAG
- Evidence strength: 中等

### Work Card: HippoRAG

- Work ID: M-WORK-024
- Source link: <https://arxiv.org/abs/2405.14831>
- Authors / Organization: Bernal Jiménez Gutiérrez et al.
- Year / First Posted: 2024
- Venue / Source: arXiv
- Source Type: Paper
- Read status: partial-read
- Maturity: Recent arXiv
- Original problem: 多跳知识整合检索效率与质量不足
- Target agent / system setting: long-term retrieval / multi-hop QA
- Memory ontology: hippocampal indexing inspired retrieval layer
- Memory representation: knowledge graph + Personalized PageRank
- Memory formation: offline OpenIE-style KG construction
- Memory management / evolution: 更偏知识整合与索引，而不偏 lifecycle
- Memory retrieval: graph traversal / PPR
- Context engineering: 用图索引替代多轮昂贵检索
- Memory evaluation: multi-hop QA
- Key mechanisms: graph indexing；single-step multi-hop retrieval；knowledge integration
- What it directly supports: concept/thread links 可能比纯向量更有助于跨远距离关联
- What it only analogically supports: reading memory 中的 lightweight link graph
- What it argues against: 多跳关联只能靠 repeated top-k
- Fit to Reading Companion: 可作为“链接结构有价值”的证据
- Misfit / limitation: 它依赖 graphized corpus；RC 当前不应直接重投 KG infra
- Complexity implication: 最多借链接思想，不借底层图系统
- Candidate project-relevant implications: 若将来需要 thread-level associations，可先做 JSON links 再谈图
- Evidence strength: 中等

### Work Card: Reading/Narrative Frontier Cluster

- Work ID: M-WORK-025 / M-WORK-026 / M-WORK-027
- Source link: <https://arxiv.org/abs/2508.12630>；<https://ojs.aaai.org/index.php/AAAI/article/view/40313>；<https://arxiv.org/abs/2510.12635>
- Authors / Organization: Maitreyi Chatterjee & Devansh Agarwal; Yiming Du et al.; Yuxiang Zhang et al.
- Year / First Posted: 2025–2026
- Venue / Source: arXiv / AAAI
- Source Type: Papers
- Read status: Semantic Anchoring skimmed；MemGuide partial-read；Memory-as-Action partial-read
- Maturity: Frontier / unvalidated
- Original problem: 分别处理 persistent conversational context 中的 linguistic structure、goal-oriented memory selection、以及 long-horizon tasks 中的 autonomous context curation
- Target agent / system setting: conversational memory / multi-session goal tasks / long-horizon agents
- Memory ontology: anchors / intent-aligned memories / editable working memory
- Memory representation: linguistic structures；QA-formatted memory units；editable context state
- Memory formation: 通过 linguistic parsing、intent selection、policy-driven edit actions
- Memory management / evolution: 对 working memory 主动改写，或按 intent 筛选可用 memories
- Memory retrieval: intent-driven retrieval、slot-guided filtering、anchor-based recall
- Context engineering: 强调“不是所有相似记忆都该拿出来”；也强调“working memory 本身可以被编辑”
- Memory evaluation: 任务成功率、对话长度、长期任务性能
- Key mechanisms: semantic anchoring；intent-guided selection；memory-as-action
- What it directly supports: retrieval 需要超越 semantic similarity，引入意图、缺口、语言结构线索
- What it only analogically supports: 阅读中的“当前问题/阅读意图”驱动的 selective recall
- What it argues against: 纯语义 top-k 足以服务复杂长期任务
- Fit to Reading Companion: MemGuide 类机制对“按当前阅读意图检索”最相关；Semantic Anchoring 对 source-linked textual memory 的线索最贴近
- Misfit / limitation: Memory-as-Action 走向 RL/context editing OS，不符合 RC 的可审计、轻量、file-based 优先级
- Complexity implication: 可借 retrieval cue，不应借 RL memory editing
- Candidate project-relevant implications: 未来 recall policy 可能需要 intent / missing-slot / discourse anchor，而不是只看 embedding 相似度
- Evidence strength: 中等偏低，宜作为 frontier signal

## 机制证据卡

### Evidence Card: M-EXT-001

- External work: Generative Agents
- Work ID: M-WORK-001
- Year: 2023
- Mechanism name: memory stream
- Original context: 社会模拟 agent 连续观察环境与行为
- Mechanism summary: 所有 observation 先进入低层 memory stream，再由后续机制决定哪些上升为高层反思
- Supports which possible design area: Memory Formation / Audit
- Support type: Direct
- Reasoning bridge: Reading Companion 同样面对大量 unit-level observation。如果一开始就把每个 read unit 都写成 durable memory，会迅速稀释真正重要的 reading state。memory stream 提供了一个关键分层：先保留低层观察，再由后续规则决定是否提升。
- Why not direct copy: 原论文没有把 source-grounded evidence 保留当成一等要求
- Complexity implication: 需要在低层 observation 与 durable memory 之间设计过渡层
- What project evidence would still be needed: 当前 RC 的 read_audit 是否已足够承载低层 observation
- Confidence: High
- Stable citation: <https://arxiv.org/abs/2304.03442>

### Evidence Card: M-EXT-002

- External work: Generative Agents
- Work ID: M-WORK-001
- Year: 2023
- Mechanism name: recency / relevance / importance tri-score retrieval
- Original context: 行为规划前的 memory reactivation
- Mechanism summary: 检索不只看语义相关，还看最近性与重要性
- Supports which possible design area: Memory Retrieval / Context Engineering
- Support type: Direct
- Reasoning bridge: 在阅读中，某个 earlier observation 可能语义相关但并不当前重要；反过来，某个 chapter roadmap 虽不最相似却更关键。三因子思路说明：检索应当是多准则，而不是单纯 semantic top-k。
- Why not direct copy: importance scoring 在阅读场景如何定义，需要 source-structure 约束
- Complexity implication: 需要 metadata 或 scoring signal
- What project evidence would still be needed: 当前 RC 中哪些字段能代表 importance / freshness
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2304.03442>

### Evidence Card: M-EXT-003

- External work: Generative Agents
- Work ID: M-WORK-001
- Year: 2023
- Mechanism name: reflection trigger
- Original context: 累积足够 observation 后，系统生成高层 reflection
- Mechanism summary: reflection 是慢周期 operation，不是每步都做
- Supports which possible design area: Memory Formation / Planning Interface
- Support type: Direct
- Reasoning bridge: 这直接支撑 RC 中“为什么不应每个 read unit 都反思”。阅读中的 reflective memory 应当是阶段性地从多条 observation 汇总出来，而不是单位级噪声放大器。
- Why not direct copy: reflection 的阈值与触发条件在阅读中要绑定章、段、结构断点
- Complexity implication: 需要 slow-cycle 触发策略
- What project evidence would still be needed: 哪些断点最适合作为 reflection 边界
- Confidence: High
- Stable citation: <https://arxiv.org/abs/2304.03442>

### Evidence Card: M-EXT-004

- External work: MemGPT / Letta
- Work ID: M-WORK-002/003/004
- Year: 2023–2026
- Mechanism name: core vs archival memory hierarchy
- Original context: context-window scarcity 下的 stateful agents
- Mechanism summary: 把 always-visible core memory 与 searchable archival memory 分层
- Supports which possible design area: Memory Representation / Context Engineering / Storage
- Support type: Direct
- Reasoning bridge: RC 也需要区分“当前回合一定要看见的 hot memory”与“需要时可找回的 durable memory”。这不是为了做 OS，而是为了阻止 authoritative store 与 prompt projection 混成一层。
- Why not direct copy: Letta 默认人设/用户画像块不适合 RC
- Complexity implication: 需要明确 authoritative store 与 prompt-facing projection 的边界
- What project evidence would still be needed: 当前 RC 是否真的需要 always-visible block，而非简单 carry-forward digest
- Confidence: High
- Stable citation: <https://docs.letta.com/guides/ade/archival-memory/>

### Evidence Card: M-EXT-005

- External work: Letta
- Work ID: M-WORK-003
- Year: 2025–2026
- Mechanism name: memory block contract
- Original context: self-editing core memory blocks
- Mechanism summary: 每个 block 至少有 label / description / value / limit
- Supports which possible design area: Memory Representation / Audit
- Support type: Direct
- Reasoning bridge: 这为 RC 的轻量 textual memory contract 提供了一个极其实用的最小模板。尤其是 description 字段，实际上把“这个记忆块该怎么被读写”以文本方式显式化，这比纯表名更强。
- Why not direct copy: Letta 的 block 是 prompt-first abstraction；RC 需要 authoritative source-linked item contract
- Complexity implication: 低；非常适合 JSON/JSONL
- What project evidence would still be needed: 当前 RC item-level 而非 block-level 是否更合适
- Confidence: High
- Stable citation: <https://docs.letta.com/guides/core-concepts/memory/memory-blocks>

### Evidence Card: M-EXT-006

- External work: Letta
- Work ID: M-WORK-003
- Year: 2025–2026
- Mechanism name: description-guided block semantics
- Original context: agent 通过 block description 学会如何使用 block
- Mechanism summary: 好的 description 是 agent 判断如何读写 block 的主要线索
- Supports which possible design area: Context Engineering / Audit
- Support type: Direct
- Reasoning bridge: 这对 RC 尤其重要，因为许多 memory buckets 容易语义漂移。若 block/item 的用途不被说明，系统与人都会逐渐混淆 “记录 source-grounded state” 与 “自由总结” 的边界。
- Why not direct copy: RC 更可能是 item contract + store contract 的组合，而不是纯 block
- Complexity implication: 低
- What project evidence would still be needed: 哪些 store / item 需要显式 description
- Confidence: High
- Stable citation: <https://docs.letta.com/guides/core-concepts/memory/memory-blocks>

### Evidence Card: M-EXT-007

- External work: Letta
- Work ID: M-WORK-003/004
- Year: 2025–2026
- Mechanism name: always-visible core memory
- Original context: persona/human/planning blocks 固定 pinned 到 prompt
- Mechanism summary: 某些 memory 无需检索，始终在上下文中
- Supports which possible design area: Context Engineering
- Support type: Boundary
- Reasoning bridge: 这帮助 RC 划清一个重要边界：不是所有 durable memory 都该 always-visible。只有极少数“当前 reading continuity 的基线状态”可能值得常驻，否则 prompt 会被常驻块污染。
- Why not direct copy: RC 不是 user-persona assistant
- Complexity implication: 常驻块越多，prompt 越脆弱
- What project evidence would still be needed: 哪些 state 真正值得 always carry
- Confidence: High
- Stable citation: <https://docs.letta.com/guides/ade/core-memory/>

### Evidence Card: M-EXT-008

- External work: MemoryBank
- Work ID: M-WORK-005
- Year: 2024
- Mechanism name: forgetting curve-inspired retention
- Original context: long-term companion memory
- Mechanism summary: 随时间和重要性动态强化或遗忘 memory
- Supports which possible design area: Memory Management
- Support type: Analogical
- Reasoning bridge: 阅读 memory 也可能需要“冷却”与“再激活”，尤其是只在某章节局部有效的 reading state。MemoryBank 提醒我们：生命周期不是可选附属，而是 memory design 的内核之一。
- Why not direct copy: 忘记在阅读中更像“可见性衰减”而不是“事实抹除”
- Complexity implication: 需要区分失效、降权、归档
- What project evidence would still be needed: RC 是否真的存在应被衰减的 state 类别
- Confidence: Medium
- Stable citation: <https://ojs.aaai.org/index.php/AAAI/article/view/29946>

### Evidence Card: M-EXT-009

- External work: MemoryBank
- Work ID: M-WORK-005
- Year: 2024
- Mechanism name: user personality synthesis
- Original context: AI companion 的长期 user understanding
- Mechanism summary: 从历史对话综合用户画像
- Supports which possible design area: Memory Ontology
- Support type: Negative
- Reasoning bridge: 这恰好说明 RC 当前不应把“读者偏好/人格画像”当核心 memory 目标。项目当前更强调 inside-trial reading observations 与 source-grounded state，而不是 companion persona memory。
- Why not direct copy: 场景错位
- Complexity implication: 会诱导项目向 personalized assistant 演化
- What project evidence would still be needed: 除非产品目标显著变更，否则不需要
- Confidence: High
- Stable citation: <https://ojs.aaai.org/index.php/AAAI/article/view/29946>

### Evidence Card: M-EXT-010

- External work: Mem0
- Work ID: M-WORK-006/007
- Year: 2025
- Mechanism name: extraction → conflict resolution → storage pipeline
- Original context: production-ready memory write path
- Mechanism summary: add 不是一个黑盒写入，而是显式三阶段
- Supports which possible design area: Memory Formation / Memory Management / Audit
- Support type: Direct
- Reasoning bridge: 这是 RC 最重要的外部机制之一。它说明 `memory_uptake_ops` 如果只表达“产生了记忆”，就太粗了；应该至少能区分抽取了什么、与已有 state 如何冲突、最终如何落库。
- Why not direct copy: Mem0 默认面向对话事实/偏好，不是 source-grounded reading units
- Complexity implication: 中低；适合先在 JSONL 审计层引入
- What project evidence would still be needed: 当前 state_ops 是否已经隐式包含这些阶段
- Confidence: High
- Stable citation: <https://docs.mem0.ai/core-concepts/memory-operations/add>

### Evidence Card: M-EXT-011

- External work: Mem0
- Work ID: M-WORK-007
- Year: 2025–2026
- Mechanism name: explicit update operation
- Original context: 修正已存在 memory
- Mechanism summary: update 是一等 API，不必 delete-readd
- Supports which possible design area: Memory Management / Audit
- Support type: Direct
- Reasoning bridge: 阅读中后文纠正前文理解是常态。如果没有 update/supersede 语义，系统只会不断 append，最后在 retrieval 和 visible integration 阶段爆炸。
- Why not direct copy: RC 可能需要 source-ref preserving update，而不是简单 overwrite
- Complexity implication: 需要 memory_id 与 revision semantics
- What project evidence would still be needed: item identity 如何定义
- Confidence: High
- Stable citation: <https://docs.mem0.ai/core-concepts/memory-operations/update>

### Evidence Card: M-EXT-012

- External work: Mem0
- Work ID: M-WORK-007
- Year: 2025–2026
- Mechanism name: explicit delete operation
- Original context: compliance / cleanup / expired data
- Mechanism summary: delete 是 memory lifecycle 的一等操作
- Supports which possible design area: Memory Management
- Support type: Direct
- Reasoning bridge: RC 未必频繁 delete，但至少需要“这条旧理解不该再作为可见候选”的明确动作。哪怕最终实现是 soft-delete / invalidation，设计上也不该只有 add/update。
- Why not direct copy: RC 更可能采用 invalidate/retire 而不是硬删除
- Complexity implication: 低到中
- What project evidence would still be needed: 哪些场景该 retire 而非 delete
- Confidence: High
- Stable citation: <https://docs.mem0.ai/core-concepts/memory-operations/delete>

### Evidence Card: M-EXT-013

- External work: Mem0
- Work ID: M-WORK-007
- Year: 2025–2026
- Mechanism name: metadata filters and reranking
- Original context: production search
- Mechanism summary: search 不只是 embedding 相似，还可用 filters/rerank/threshold
- Supports which possible design area: Memory Retrieval / Context Engineering
- Support type: Direct
- Reasoning bridge: 对 RC 而言，先有 scope/filter 再有 fancy storage 更重要。比如章节、时间、store 类型、来源 run、结构类目，这些 metadata 往往比“是否接了 vector DB”更先影响 retrieval precision。
- Why not direct copy: RC 未必要默认走向向量检索
- Complexity implication: 低；文件型存储同样可做 filters
- What project evidence would still be needed: 需要哪些最小 metadata 字段
- Confidence: High
- Stable citation: <https://docs.mem0.ai/core-concepts/memory-operations/search>

### Evidence Card: M-EXT-014

- External work: Mem0
- Work ID: M-WORK-006/007
- Year: 2025
- Mechanism name: optional graph memory
- Original context: relational memory enhancement
- Mechanism summary: graph memory 被设计为 optional extension，而不是 prerequisite
- Supports which possible design area: Storage
- Support type: Boundary
- Reasoning bridge: 这恰好支持 RC 的一个保守方向：即便将来需要 links / relations，也不等于现在就该上 graph DB。先把 item、ID、metadata、links 设计清楚，再看 infra。
- Why not direct copy: Mem0 graph memory 服务的是生产会话关系网络
- Complexity implication: 图层代价高，且可能过早
- What project evidence would still be needed: RC 是否真的出现向量难以解决的关系型 recall
- Confidence: High
- Stable citation: <https://docs.mem0.ai/platform/features/graph-memory>

### Evidence Card: M-EXT-015

- External work: Zep
- Work ID: M-WORK-009
- Year: 2025–2026
- Mechanism name: episodes / entities / facts layering
- Original context: temporal knowledge graph for agent memory
- Mechanism summary: 原始 episode、实体节点、事实边分层保存
- Supports which possible design area: Memory Ontology / Audit
- Support type: Direct
- Reasoning bridge: 这为 RC 提供了很强的 ontology 线索：原始 reading observation、抽象出的 concept/entity、以及它们之间的 relation/thread，最好不要混在一层。
- Why not direct copy: 不需要真的采用图数据库
- Complexity implication: 中；但可以先做逻辑分层
- What project evidence would still be needed: RC 当前 stores 是否足以承载这三层
- Confidence: High
- Stable citation: <https://help.getzep.com/graph-overview>

### Evidence Card: M-EXT-016

- External work: Zep
- Work ID: M-WORK-009
- Year: 2025–2026
- Mechanism name: valid_at / invalid_at timestamps
- Original context: changing facts over time
- Mechanism summary: fact 有时间有效区间，而不是静态真值
- Supports which possible design area: Memory Management / Evaluation
- Support type: Direct
- Reasoning bridge: 阅读里的许多理解并非“彻底错”，而是“早先版本有效、后文被修订”。valid/invalid 语义比简单 overwrite 更适合表达解释演化。
- Why not direct copy: RC 可能需要 section/chapter-based validity，而非 wall-clock timestamps
- Complexity implication: 需要时态字段或 supersede chain
- What project evidence would still be needed: 哪些 memory 类型需要 temporal validity
- Confidence: High
- Stable citation: <https://help.getzep.com/facts>

### Evidence Card: M-EXT-017

- External work: Zep
- Work ID: M-WORK-009
- Year: 2025–2026
- Mechanism name: facts vs entity summaries
- Original context: context block assembly
- Mechanism summary: 精确事实与聚合摘要同时保留，但角色不同
- Supports which possible design area: Memory Representation / Context Engineering
- Support type: Direct
- Reasoning bridge: RC 中高层 frame 很可能也应与 source-grounded fine-grain memory 并存。否则要么只有碎片、难以整体理解；要么只有 summary、难以纠错和追溯。
- Why not direct copy: Zep summary 以 entity 为中心，RC 未必
- Complexity implication: 中
- What project evidence would still be needed: 哪类高层 frame 最值得和细粒度事实并存
- Confidence: High
- Stable citation: <https://help.getzep.com/entities>

### Evidence Card: M-EXT-018

- External work: Zep
- Work ID: M-WORK-009
- Year: 2025–2026
- Mechanism name: observations as durable, evidence-backed patterns
- Original context: cross-entity stable patterns
- Mechanism summary: observation 捕捉 decision/commitment/constraint/pattern，并会随着新证据 merge / supersede
- Supports which possible design area: Memory Formation / Memory Management
- Support type: Analogical
- Reasoning bridge: 这和 RC 中“reflective frame / stable thread-level judgment”非常接近：它们不应直接等于单条 source，而应是基于多条 evidence 的 durable pattern。
- Why not direct copy: Zep 的 observation 建立在图结构分析上
- Complexity implication: 高层 pattern 需要明确 evidence backing
- What project evidence would still be needed: RC 高层 frame 是否也应保存 supporting source set
- Confidence: High
- Stable citation: <https://help.getzep.com/observations>

### Evidence Card: M-EXT-019

- External work: Zep
- Work ID: M-WORK-009
- Year: 2025–2026
- Mechanism name: default context block with configurable assembly
- Original context: query-time context assembly
- Mechanism summary: 默认 context block + templates + advanced construction 三层模式
- Supports which possible design area: Context Engineering
- Support type: Direct
- Reasoning bridge: 这直接说明 retrieval 与 context assembly 应分开建模。RC 将来即使有 recall，也最好区分“默认常态拼装”“模板式拼装”“高级控制拼装”三档成熟度。
- Why not direct copy: Zep 面向 user graph，RC 是 source-grounded reading state
- Complexity implication: 中
- What project evidence would still be needed: RC 当前是否已有足够清晰的 context packet layer
- Confidence: High
- Stable citation: <https://help.getzep.com/assembling-context>

### Evidence Card: M-EXT-020

- External work: A-MEM
- Work ID: M-WORK-010
- Year: 2025
- Mechanism name: structured note with tags / keywords / links
- Original context: Zettelkasten-inspired agentic memory
- Mechanism summary: 每条记忆以结构化 note 存储，并建立动态连接
- Supports which possible design area: Memory Representation / Storage
- Support type: Direct
- Reasoning bridge: 对 RC 来说，这提供了比“纯字符串 memory item”更合理的中间形态。它不一定需要图数据库，但至少说明 note 内部可以包含关键词、标签、上下文描述、链接与来源。
- Why not direct copy: A-MEM 的网络自由度很高，容易失控
- Complexity implication: 中
- What project evidence would still be needed: RC item schema 的最小字段集
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2502.12110>

### Evidence Card: M-EXT-021

- External work: A-MEM
- Work ID: M-WORK-010
- Year: 2025
- Mechanism name: memory evolution of existing notes
- Original context: 新 note 到来后触发旧 note 上下文更新
- Mechanism summary: 新记忆会改变旧记忆的表示与连接
- Supports which possible design area: Memory Management
- Support type: Analogical
- Reasoning bridge: 这说明“后文修正前文”不一定只能表现为新建 item；也可能表现为旧 item 被 enriched / reframed。对于 RC，这有助于思考 refresh/merge/supersede 的层级关系。
- Why not direct copy: 自由演化容易破坏审计性
- Complexity implication: 高；需要 revision trace
- What project evidence would still be needed: RC 更适合 update 还是 append+supersede
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2502.12110>

### Evidence Card: M-EXT-022

- External work: LangGraph
- Work ID: M-WORK-011
- Year: 2025–2026
- Mechanism name: semantic / episodic / procedural split
- Original context: framework-level memory taxonomy
- Mechanism summary: facts、experiences、instructions 分开对待
- Supports which possible design area: Memory Ontology
- Support type: Direct
- Reasoning bridge: RC 如果以后继续扩展，很可能也会遇到“事实状态”“阅读经历”“阅读策略指令”混淆问题。这个分法不是终局 ontology，但非常适合作为第一层抽象卫生。
- Why not direct copy: RC 的核心不在用户事实，而在 reading state
- Complexity implication: 低到中
- What project evidence would still be needed: 现有概念谁属于 semantic / episodic / procedural
- Confidence: High
- Stable citation: <https://docs.langchain.com/oss/python/concepts/memory>

### Evidence Card: M-EXT-023

- External work: LangGraph
- Work ID: M-WORK-011
- Year: 2025–2026
- Mechanism name: profile vs collection
- Original context: semantic memory management patterns
- Mechanism summary: 单一 profile 文档 vs 多个文档集合
- Supports which possible design area: Memory Representation
- Support type: Direct
- Reasoning bridge: 这给 RC 一个非常具体的问题框架：阅读 memory 更像不断修订的 profile，还是不断积累的 collection？从 source-grounded、可审计、低风险角度看，collection 往往更稳。
- Why not direct copy: RC 可能需要 hybrid：小型 carry-forward profile + durable collection
- Complexity implication: 中
- What project evidence would still be needed: 当前 stores 更像哪种模式
- Confidence: High
- Stable citation: <https://docs.langchain.com/oss/python/concepts/memory>

### Evidence Card: M-EXT-024

- External work: LangGraph
- Work ID: M-WORK-011
- Year: 2025–2026
- Mechanism name: hot path vs background writes
- Original context: 运行时即写 vs 后台 memory manager
- Mechanism summary: 记忆写入时机是设计维度，不只是实现细节
- Supports which possible design area: Memory Formation / Memory Management
- Support type: Direct
- Reasoning bridge: 这极适合 RC。某些低风险事实可以 hot-path 写入；高层总结、整合、清理则更适合 slow-cycle/background。这比“一个 read step 输出所有东西”更稳健。
- Why not direct copy: RC 的“后台”可能不是异步线程，而是 chapter/book 结算周期
- Complexity implication: 中
- What project evidence would still be needed: 当前 runner settlement 是否可承载 slow-cycle 写入
- Confidence: High
- Stable citation: <https://docs.langchain.com/oss/python/concepts/memory>

### Evidence Card: M-EXT-025

- External work: LangMem
- Work ID: M-WORK-012
- Year: 2025–2026
- Mechanism name: background memory manager
- Original context: 自动 extract / consolidate / update knowledge
- Mechanism summary: memory manager 在后台完成 consolidation/update
- Supports which possible design area: Memory Management / Audit
- Support type: Direct
- Reasoning bridge: RC 的 chapter settlement / book settlement 很像一种受控的 background memory manager。它启发的不是“后台线程”，而是“将 consolidation 从即时理解中剥离出来”。
- Why not direct copy: LangMem 默认依赖 LangGraph store 与 agent tools
- Complexity implication: 中
- What project evidence would still be needed: 当前 settlement 是否已经在做隐式 consolidation
- Confidence: High
- Stable citation: <https://github.com/langchain-ai/langmem>

### Evidence Card: M-EXT-026

- External work: LangGraph / LangMem
- Work ID: M-WORK-011/012
- Year: 2025–2026
- Mechanism name: prompt refinement as procedural memory
- Original context: agent 通过 reflection 更新 instructions
- Mechanism summary: instruction 自身也可被视作可演化的 procedural memory
- Supports which possible design area: Procedural Memory / Context Engineering
- Support type: Analogical
- Reasoning bridge: RC 不一定需要“自改 prompt”，但这至少提醒我们：并非所有 memory 都是事实对象；有些 memory 是“以后怎么读/怎么判断”的程序性经验。
- Why not direct copy: 项目当前优先 textual source-grounded memory，不优先自演化策略层
- Complexity implication: 高；容易失控
- What project evidence would still be needed: 项目是否真的需要 procedural memory 层
- Confidence: Medium
- Stable citation: <https://docs.langchain.com/oss/python/concepts/memory>

### Evidence Card: M-EXT-027

- External work: RAPTOR
- Work ID: M-WORK-013
- Year: 2024
- Mechanism name: hierarchical summarization tree
- Original context: long-document QA
- Mechanism summary: 多层摘要树提供不同粒度的检索入口
- Supports which possible design area: Retrieval / Context Engineering
- Support type: Analogical
- Reasoning bridge: RC 的高层 reflective frame 也可能作为 retrieval entry 工作。RAPTOR 证明“抽象层入口”本身可以提升长文理解，即使它不是 agent memory。
- Why not direct copy: 树索引是 corpus-side，不是 run-side memory
- Complexity implication: 中到高
- What project evidence would still be needed: 高层 frame 是否真的比原子条目更常被召回
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2401.18059>

### Evidence Card: M-EXT-028

- External work: GraphRAG
- Work ID: M-WORK-014/015
- Year: 2024–2026
- Mechanism name: local vs global retrieval modes
- Original context: corpus question answering
- Mechanism summary: specific questions 用 local，global sensemaking 用 global map-reduce over community reports
- Supports which possible design area: Retrieval / Context Engineering
- Support type: Direct
- Reasoning bridge: 阅读场景也存在“局部证据问题”和“全局意义问题”。这支持 RC 在 retrieval policy 层面对 query type 做区分，而不是单一路径召回。
- Why not direct copy: RC 当前 query 类型可能还没系统化
- Complexity implication: 中
- What project evidence would still be needed: 哪些 RC task 是 local，哪些是 global
- Confidence: High
- Stable citation: <https://microsoft.github.io/graphrag/query/overview/>

### Evidence Card: M-EXT-029

- External work: GraphRAG
- Work ID: M-WORK-014/015
- Year: 2024–2026
- Mechanism name: community summaries for global sensemaking
- Original context: dataset-level summarization
- Mechanism summary: 将实体社区预先汇总为多层 summaries
- Supports which possible design area: Memory Representation / Retrieval
- Support type: Analogical
- Reasoning bridge: 对 RC 来说，它支持“高层聚合物有独立价值”，例如 book-level themes、chapter-level frames、thread-level summaries。但这些应当被视为聚合物，不应替代 source-grounded lower layers。
- Why not direct copy: 预建社区摘要成本高，且面向 corpus
- Complexity implication: 高
- What project evidence would still be needed: RC 是否真的需要预生成全局 summaries
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2404.16130>

### Evidence Card: M-EXT-030

- External work: LongMemEval
- Work ID: M-WORK-016
- Year: 2024
- Mechanism name: indexing / retrieval / reading stage decomposition
- Original context: benchmarking chat assistants
- Mechanism summary: memory design 被拆为阶段，而不是黑箱
- Supports which possible design area: Evaluation / Audit
- Support type: Direct
- Reasoning bridge: RC 也需要把失败定位到 formation、retrieval、use 之中至少某一层。否则“答错了”并不能告诉我们 memory 是没形成、没找到，还是找到了但没被正确利用。
- Why not direct copy: RC 的阶段名可能不同
- Complexity implication: 低到中；前提是 trace 在
- What project evidence would still be needed: read audit / settlement audit 能否映射阶段
- Confidence: High
- Stable citation: <https://arxiv.org/abs/2410.10813>

### Evidence Card: M-EXT-031

- External work: LongMemEval
- Work ID: M-WORK-016
- Year: 2024
- Mechanism name: knowledge update and abstention as core memory abilities
- Original context: long-term memory benchmark
- Mechanism summary: 记忆能力不只包含 recall，也包括更新与“知道自己不知道”
- Supports which possible design area: Evaluation
- Support type: Direct
- Reasoning bridge: RC 一旦进入长期使用，知识更新与 abstention 会非常关键。否则系统会把陈旧理解当成稳定真理，或在没有足够支持时硬性整合。
- Why not direct copy: RC 还需把 abstention 绑定到 source evidence 缺失
- Complexity implication: 低
- What project evidence would still be needed: 当前评估是否已有 abstention 位点
- Confidence: High
- Stable citation: <https://arxiv.org/abs/2410.10813>

### Evidence Card: M-EXT-032

- External work: LoCoMo
- Work ID: M-WORK-017
- Year: 2024
- Mechanism name: temporal event graph grounded long conversations
- Original context: very long conversational memory benchmark
- Mechanism summary: benchmark 用 event graph 与多 session continuity 检验 temporal/causal memory
- Supports which possible design area: Evaluation
- Support type: Analogical
- Reasoning bridge: 阅读长书时，章序、因果演进、人物状态变化与跨段 continuity 是类似问题。LoCoMo 证明：如果 benchmark 不显式考 temporal/casual continuity，这类错误会被掩盖。
- Why not direct copy: 对话 benchmark ≠ 阅读 benchmark
- Complexity implication: 低到中
- What project evidence would still be needed: RC 的 chapter-order / state change probe 怎样定义
- Confidence: High
- Stable citation: <https://aclanthology.org/2024.acl-long.747/>

### Evidence Card: M-EXT-033

- External work: LoCoMo-Plus
- Work ID: M-WORK-018
- Year: 2026
- Mechanism name: latent constraint / cue-trigger disconnect evaluation
- Original context: beyond-factual conversational memory
- Mechanism summary: 测试系统是否能在语义线索不直接重合时仍保持隐性约束
- Supports which possible design area: Evaluation
- Support type: Direct
- Reasoning bridge: 对 RC 而言，这尤其贴近“读得对、用得好”的高阶要求。系统可能能复述事实，却在后续综合中违背先前隐含约束、定义边界或结构前提；LoCoMo-Plus 专门暴露这种失败。
- Why not direct copy: benchmark 尚新，且评价框架仍在形成共识
- Complexity implication: 中
- What project evidence would still be needed: RC 的 latent constraints 来自何处——定义、分类、范围、章节路线图？
- Confidence: Medium
- Stable citation: <https://openreview.net/forum?id=QWVKrMGdah>

### Evidence Card: M-EXT-034

- External work: StructMemEval
- Work ID: M-WORK-019
- Year: 2026
- Mechanism name: memory organization benchmark
- Original context: 测 agent 能否把记忆组织成树、账本、状态追踪等结构
- Mechanism summary: 结构能力本身被 benchmark 化，而不是只测事实 recall
- Supports which possible design area: Evaluation / Memory Structure
- Support type: Direct
- Reasoning bridge: 这直接支撑一个关键判断：memory 结构本身应该被评估，不然系统可能“记住了很多条”，却无法维持 thread、ledger、state tracker 这类人类实际使用的组织形态。
- Why not direct copy: benchmark 新且规模有限
- Complexity implication: 低；至少先引入结构成功/失败维度
- What project evidence would still be needed: RC 哪些结构最关键——concept tree、thread trace、stage ledger？
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2602.11243>

### Evidence Card: M-EXT-035

- External work: MemoryBench
- Work ID: M-WORK-020
- Year: 2025
- Mechanism name: continual memory / learning benchmark
- Original context: simulated user feedback and continual learning
- Mechanism summary: 评估系统在持续反馈下构建/更新记忆的能力
- Supports which possible design area: Evaluation / Memory Management
- Support type: Background
- Reasoning bridge: RC 当前不是 continual learning 平台，但它迟早会遇到修正、补充、再阅读带来的连续演化问题。MemoryBench 是提醒，而不是当前设计依据。
- Why not direct copy: 场景并非阅读 agent
- Complexity implication: 暂不值得直接引入
- What project evidence would still be needed: 是否真的要支持跨 run continual adaptation
- Confidence: Low to Medium
- Stable citation: <https://arxiv.org/abs/2510.17281>

### Evidence Card: M-EXT-036

- External work: HaluMem
- Work ID: M-WORK-021
- Year: 2025
- Mechanism name: operation-level hallucination benchmark
- Original context: extraction / updating / QA 三阶段幻觉定位
- Mechanism summary: 幻觉可在 memory extraction、memory updating、memory QA 中分别发生并累积
- Supports which possible design area: Evaluation / Audit
- Support type: Direct
- Reasoning bridge: 这和 RC 当前最关心的“污染”问题高度同构。若只看最终 answer hallucination，就看不到污染是 formation 阶段注入，还是 update 阶段扩散。
- Why not direct copy: benchmark 较新，且基于对话 memory 系统
- Complexity implication: 低到中；关键在 trace
- What project evidence would still be needed: 当前 audit 能否定位 formation/update/retrieval 的错误传播
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2511.03506>

### Evidence Card: M-EXT-037

- External work: CAM
- Work ID: M-WORK-022
- Year: 2025
- Mechanism name: constructivist schemata for reading memory
- Original context: LLM-based reading comprehension
- Mechanism summary: 把 memory 视为逐步形成与重构的 schemata
- Supports which possible design area: Memory Ontology / Formation
- Support type: Direct
- Reasoning bridge: 这比 chatbot memory 更贴近 RC，因为它关注的是“阅读中结构如何逐渐形成”，而不是“用户告诉了我什么事实”。
- Why not direct copy: 论文仍是 frontier prototype
- Complexity implication: 中到高
- What project evidence would still be needed: RC 现有概念能否承载 schemata 视角
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2510.05520>

### Evidence Card: M-EXT-038

- External work: CAM
- Work ID: M-WORK-022
- Year: 2025
- Mechanism name: incremental overlapping clustering
- Original context: structured memory development for reading
- Mechanism summary: 通过在线重叠聚类将新理解整合进现有结构
- Supports which possible design area: Memory Formation / Structured Construction
- Support type: Analogical
- Reasoning bridge: 它说明阅读 memory 的形成可能不是单条独立写入，而是“新 observation 进入已有结构”的过程。对 RC 来说，这支持 concept/thread aggregation 的必要性。
- Why not direct copy: 算法复杂，且需要稳定结构构建基础
- Complexity implication: 高
- What project evidence would still be needed: RC 是否真的需要 algorithmic clustering，而非规则化聚合
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2510.05520>

### Evidence Card: M-EXT-039

- External work: ComoRAG
- Work ID: M-WORK-023
- Year: 2025
- Mechanism name: dynamic memory workspace
- Original context: narrative reasoning
- Mechanism summary: reasoning 过程中维护一个动态可扩展 workspace
- Supports which possible design area: Memory Retrieval / Context Engineering
- Support type: Direct
- Reasoning bridge: RC 在长文本中也可能需要一个“当前工作空间”，它不同于 durable memory：更短期、更任务驱动、更强选择性。ComoRAG 提供了这一层的存在理由。
- Why not direct copy: 其 workspace 与 iterative RAG 强绑定
- Complexity implication: 中
- What project evidence would still be needed: RC 是否已有 equivalent packet/context workspace
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2508.10419>

### Evidence Card: M-EXT-040

- External work: ComoRAG
- Work ID: M-WORK-023
- Year: 2025
- Mechanism name: probing queries on reasoning impasse
- Original context: 当 narrative reasoning 卡住时生成 exploratory queries
- Mechanism summary: 检索由 impasse 触发，而非固定频率执行
- Supports which possible design area: Memory Retrieval
- Support type: Direct
- Reasoning bridge: 这与 RC 中的 detour / active recall 非常同构。它提示一种更强的 retrieval boundary：只有在理解真的出现缺口时才触发 targeted recall。
- Why not direct copy: RC 不一定要引入完整 iterative loop
- Complexity implication: 中
- What project evidence would still be needed: 当前系统如何识别真正的 reasoning impasse
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2508.10419>

### Evidence Card: M-EXT-041

- External work: HippoRAG
- Work ID: M-WORK-024
- Year: 2024
- Mechanism name: graph-based associative retrieval
- Original context: multi-hop question answering
- Mechanism summary: 通过 KG + PPR 做关联性更强的 recall
- Supports which possible design area: Retrieval / Storage
- Support type: Analogical
- Reasoning bridge: 阅读中 concept/thread 之间的“联想式召回”可能不适合只靠向量相似度。HippoRAG 给出一个证据：结构化关联能提升远距离多跳召回。
- Why not direct copy: RC 当前不应引入 KG infra
- Complexity implication: 高
- What project evidence would still be needed: simpler lightweight links 是否已足够
- Confidence: Medium
- Stable citation: <https://arxiv.org/abs/2405.14831>

### Evidence Card: M-EXT-042

- External work: Semantic Anchoring
- Work ID: M-WORK-025
- Year: 2025
- Mechanism name: linguistic anchors beyond embeddings
- Original context: persistent conversational context
- Mechanism summary: 用 dependency / discourse / coreference 增强 memory entry
- Supports which possible design area: Memory Formation / Retrieval
- Support type: Analogical
- Reasoning bridge: 对 RC 而言，这比一般 chat memory 更接近文本理解，因为阅读状态高度依赖定义、指代、话语关系与结构信号。它支持“语义相似度之外的 textual anchors”。
- Why not direct copy: 论文仍前沿，且 conversational 取向明显
- Complexity implication: 中
- What project evidence would still be needed: RC 最有价值的 linguistic anchors 是哪些
- Confidence: Low to Medium
- Stable citation: <https://arxiv.org/abs/2508.12630>

### Evidence Card: M-EXT-043

- External work: MemGuide
- Work ID: M-WORK-026
- Year: 2026
- Mechanism name: intent-aligned retrieval + missing-slot filtering
- Original context: goal-oriented multi-session TOD
- Mechanism summary: 先按意图检索，再按当前信息缺口过滤
- Supports which possible design area: Retrieval / Context Engineering
- Support type: Direct
- Reasoning bridge: 这对 RC 很重要，因为阅读 recall 也不该只按“语义相似”返回，而应问：当前阅读意图是什么？当前理解缺了什么？这比笼统 top-k 更贴近辅助阅读。
- Why not direct copy: TOD 的 slot 逻辑不能直接平移到阅读
- Complexity implication: 中
- What project evidence would still be needed: RC 中“缺口”如何被表示
- Confidence: Medium
- Stable citation: <https://ojs.aaai.org/index.php/AAAI/article/view/40313>

### Evidence Card: M-EXT-044

- External work: Memory as Action
- Work ID: M-WORK-027
- Year: 2025
- Mechanism name: memory editing as policy action
- Original context: long-horizon agentic tasks with RL
- Mechanism summary: working memory 的 curating/editing 被建模为 agent 行动
- Supports which possible design area: Working Memory / Planning Interface
- Support type: Boundary
- Reasoning bridge: 它帮助 RC 明确边界：主动编辑 working context 是有吸引力的，但一旦走向 RL/policy learning，系统就会远离当前强调的 source-grounded、可解释、可审计、file-based simplicity。
- Why not direct copy: 场景和技术路线都不匹配
- Complexity implication: 极高
- What project evidence would still be needed: 若未来真要引入 learnable context curation，需重新立项
- Confidence: High
- Stable citation: <https://arxiv.org/abs/2510.12635>

### Evidence Card: M-EXT-045

- External work: MemGPT / MemOS-style memory OS line
- Work ID: M-WORK-002 / M-WORK-029
- Year: 2023–2025
- Mechanism name: memory OS framing
- Original context: treating LLM + memory as OS-like virtualized runtime
- Mechanism summary: memory 作为系统资源统一调度
- Supports which possible design area: Storage / Context Engineering
- Support type: Negative
- Reasoning bridge: 这条线对 RC 的价值主要在于提醒复杂度上限。它很容易把“阅读状态管理”升级成“通用 memory OS”，从而偏离产品原则中的 Simplicity and Universality。
- Why not direct copy: 当前目标太窄，不需要 OS
- Complexity implication: 极高
- What project evidence would still be needed: 除非项目目标扩展成通用 agent runtime
- Confidence: High
- Stable citation: <https://arxiv.org/abs/2310.08560>；<https://arxiv.org/abs/2507.03724>

## 证据账本与按工作处置

### External Evidence Ledger

| Evidence ID | Work ID | Work | Year | Mechanism | Topic | Support Type | Reasoning Bridge Summary | Possible RC Design Area | Why Not Direct Copy | Complexity Cost | Confidence | Stable Citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M-EXT-001 | M-WORK-001 | Generative Agents | 2023 | memory stream | Formation | Direct | 低层观察先存，再决定是否上升 | Formation / Audit | 无 source-grounding 约束 | 中 | High | [arXiv 2304.03442](https://arxiv.org/abs/2304.03442) |
| M-EXT-002 | M-WORK-001 | Generative Agents | 2023 | tri-score retrieval | Retrieval | Direct | 检索需兼看相关性/近期性/重要性 | Retrieval | importance 定义需重做 | 中 | Medium | [arXiv 2304.03442](https://arxiv.org/abs/2304.03442) |
| M-EXT-003 | M-WORK-001 | Generative Agents | 2023 | reflection trigger | Formation | Direct | 反思应为慢周期而非步步触发 | Formation | 阅读边界不同 | 中 | High | [arXiv 2304.03442](https://arxiv.org/abs/2304.03442) |
| M-EXT-004 | M-WORK-002/003/004 | MemGPT/Letta | 2023–2026 | core vs archival | Representation | Direct | 区分 always-visible hot state 与 durable store | Representation / Context | persona/chat bias 强 | 中 | High | [Letta archival docs](https://docs.letta.com/guides/ade/archival-memory/) |
| M-EXT-005 | M-WORK-003 | Letta | 2025–2026 | block contract | Representation | Direct | label/description/value/limit 适合轻量 contract | Representation / Audit | block 是 prompt-first | 低 | High | [Letta memory blocks docs](https://docs.letta.com/guides/core-concepts/memory/memory-blocks) |
| M-EXT-006 | M-WORK-003 | Letta | 2025–2026 | description semantics | Audit | Direct | 用 description 显式声明 block 用途 | Audit / Context | item-level 可能更合适 | 低 | High | [Letta memory blocks docs](https://docs.letta.com/guides/core-concepts/memory/memory-blocks) |
| M-EXT-007 | M-WORK-003/004 | Letta | 2025–2026 | always-visible blocks | Context | Boundary | 只有极少数 state 值得常驻 prompt | Context Engineering | user/persona 模型错位 | 中 | High | [Letta core memory docs](https://docs.letta.com/guides/ade/core-memory/) |
| M-EXT-008 | M-WORK-005 | MemoryBank | 2024 | forgetting curve | Management | Analogical | memory 可能需要冷却/再激活 | Management | 用户画像场景偏差 | 中 | Medium | [AAAI MemoryBank](https://ojs.aaai.org/index.php/AAAI/article/view/29946) |
| M-EXT-009 | M-WORK-005 | MemoryBank | 2024 | personality synthesis | Ontology | Negative | 提醒 RC 不应转向 companion persona | Ontology boundary | 场景错位 | 中 | High | [AAAI MemoryBank](https://ojs.aaai.org/index.php/AAAI/article/view/29946) |
| M-EXT-010 | M-WORK-006/007 | Mem0 | 2025 | extract-resolve-store | Formation | Direct | 形成阶段应拆解为多个可审计 operation | Formation / Audit | 默认对话场景 | 中 | High | [Mem0 add docs](https://docs.mem0.ai/core-concepts/memory-operations/add) |
| M-EXT-011 | M-WORK-007 | Mem0 | 2025–2026 | explicit update | Management | Direct | 后文修正前文需要 update 语义 | Management | 需 source-ref preserving update | 中 | High | [Mem0 update docs](https://docs.mem0.ai/core-concepts/memory-operations/update) |
| M-EXT-012 | M-WORK-007 | Mem0 | 2025–2026 | explicit delete | Management | Direct | lifecycle 不应只有 add | Management | RC 更可能 retire/invalidate | 低 | High | [Mem0 delete docs](https://docs.mem0.ai/core-concepts/memory-operations/delete) |
| M-EXT-013 | M-WORK-007 | Mem0 | 2025–2026 | filters + rerank | Retrieval | Direct | metadata scope 往往先于 infra | Retrieval | 未必需向量检索 | 低 | High | [Mem0 search docs](https://docs.mem0.ai/core-concepts/memory-operations/search) |
| M-EXT-014 | M-WORK-006/007 | Mem0 | 2025 | optional graph memory | Storage | Boundary | links 有价值≠现在就上 graph DB | Storage | infra 过早 | 高 | High | [Mem0 graph memory docs](https://docs.mem0.ai/platform/features/graph-memory) |
| M-EXT-015 | M-WORK-009 | Zep | 2025–2026 | episodes/entities/facts | Ontology | Direct | 原始观察、实体概念、关系事实分层 | Ontology / Audit | 不需图 DB | 中 | High | [Zep graph overview](https://help.getzep.com/graph-overview) |
| M-EXT-016 | M-WORK-009 | Zep | 2025–2026 | valid_at/invalid_at | Management | Direct | 早先理解可能有效但后被修订 | Management / Eval | 时间语义需本地化 | 中 | High | [Zep facts docs](https://help.getzep.com/facts) |
| M-EXT-017 | M-WORK-009 | Zep | 2025–2026 | facts vs summaries | Representation | Direct | 高层 frame 与细粒度事实应并存 | Representation | summary 以 entity 为中心 | 中 | High | [Zep entities docs](https://help.getzep.com/entities) |
| M-EXT-018 | M-WORK-009 | Zep | 2025–2026 | observations | Formation | Analogical | durable pattern 应有 evidence backing | Formation / Management | 建立在 graph analysis 上 | 中高 | High | [Zep observations docs](https://help.getzep.com/observations) |
| M-EXT-019 | M-WORK-009 | Zep | 2025–2026 | context block modes | Context | Direct | 检索与装配应分层 | Context Engineering | user-graph 偏向 | 中 | High | [Zep assembling context docs](https://help.getzep.com/assembling-context) |
| M-EXT-020 | M-WORK-010 | A-MEM | 2025 | structured note | Representation | Direct | item 不必是纯字符串 | Representation / Storage | 网络过自由 | 中 | Medium | [arXiv 2502.12110](https://arxiv.org/abs/2502.12110) |
| M-EXT-021 | M-WORK-010 | A-MEM | 2025 | memory evolution | Management | Analogical | 新理解可更新旧 note 的语境 | Management | 审计难度高 | 高 | Medium | [arXiv 2502.12110](https://arxiv.org/abs/2502.12110) |
| M-EXT-022 | M-WORK-011 | LangGraph | 2025–2026 | semantic/episodic/procedural | Ontology | Direct | 先把 memory 类型卫生做好 | Ontology | RC 语义需重命名 | 低 | High | [LangGraph memory docs](https://docs.langchain.com/oss/python/concepts/memory) |
| M-EXT-023 | M-WORK-011 | LangGraph | 2025–2026 | profile vs collection | Representation | Direct | 阅读 memory 更可能偏 collection | Representation | 可能仍需 hybrid | 中 | High | [LangGraph memory docs](https://docs.langchain.com/oss/python/concepts/memory) |
| M-EXT-024 | M-WORK-011 | LangGraph | 2025–2026 | hot vs background | Formation | Direct | 即时写入与慢周期整合应分工 | Formation / Management | background 不一定是异步线程 | 中 | High | [LangGraph memory docs](https://docs.langchain.com/oss/python/concepts/memory) |
| M-EXT-025 | M-WORK-012 | LangMem | 2025–2026 | background manager | Management | Direct | settlement/consolidation 可被视作 memory manager | Management / Audit | 绑定 LangGraph store | 中 | High | [LangMem README](https://github.com/langchain-ai/langmem) |
| M-EXT-026 | M-WORK-011/012 | LangGraph/LangMem | 2025–2026 | prompt refinement | Procedural | Analogical | 策略性 memory 与事实性 memory 应分开 | Procedural / Context | 当前优先级偏低 | 高 | Medium | [LangGraph memory docs](https://docs.langchain.com/oss/python/concepts/memory) |
| M-EXT-027 | M-WORK-013 | RAPTOR | 2024 | hierarchical tree | Retrieval | Analogical | 高层 frame 可作为检索入口 | Retrieval | 它是 corpus index | 中高 | Medium | [arXiv 2401.18059](https://arxiv.org/abs/2401.18059) |
| M-EXT-028 | M-WORK-014/015 | GraphRAG | 2024–2026 | local vs global modes | Retrieval | Direct | local/global 问题需要不同路线 | Retrieval / Context | query taxonomy 需本地化 | 中 | High | [GraphRAG query docs](https://microsoft.github.io/graphrag/query/overview/) |
| M-EXT-029 | M-WORK-014/015 | GraphRAG | 2024–2026 | community summaries | Representation | Analogical | 高层聚合物有独立价值 | Representation / Retrieval | 成本高、过重 | 高 | Medium | [arXiv 2404.16130](https://arxiv.org/abs/2404.16130) |
| M-EXT-030 | M-WORK-016 | LongMemEval | 2024 | stage decomposition | Evaluation | Direct | 失败定位必须分 formation/retrieval/use | Evaluation / Audit | 阶段名需本地化 | 低中 | High | [arXiv 2410.10813](https://arxiv.org/abs/2410.10813) |
| M-EXT-031 | M-WORK-016 | LongMemEval | 2024 | updates + abstention | Evaluation | Direct | memory 评估也应测更新与克制 | Evaluation | 需 source-grounded abstention | 低 | High | [arXiv 2410.10813](https://arxiv.org/abs/2410.10813) |
| M-EXT-032 | M-WORK-017 | LoCoMo | 2024 | temporal event continuity | Evaluation | Analogical | 章序/因果/状态演进需单列评价 | Evaluation | 对话 benchmark | 中 | High | [ACL LoCoMo](https://aclanthology.org/2024.acl-long.747/) |
| M-EXT-033 | M-WORK-018 | LoCoMo-Plus | 2026 | latent constraint consistency | Evaluation | Direct | 表面 recall 对了也可能隐式约束错 | Evaluation | frontier，成熟度不足 | 中 | Medium | [OpenReview LoCoMo-Plus](https://openreview.net/forum?id=QWVKrMGdah) |
| M-EXT-034 | M-WORK-019 | StructMemEval | 2026 | structure benchmark | Evaluation | Direct | memory 结构本身应被评估 | Evaluation / Structure | 新 benchmark | 低 | Medium | [arXiv 2602.11243](https://arxiv.org/abs/2602.11243) |
| M-EXT-035 | M-WORK-020 | MemoryBench | 2025 | continual memory benchmark | Evaluation | Background | 提醒持续更新问题，但非当前核心 | Evaluation | 场景不够贴近 | 中 | Low-Med | [arXiv 2510.17281](https://arxiv.org/abs/2510.17281) |
| M-EXT-036 | M-WORK-021 | HaluMem | 2025 | operation-level hallucination | Evaluation | Direct | 污染可能在 extraction/update，而非最后 QA | Evaluation / Audit | benchmark 尚新 | 中 | Medium | [arXiv 2511.03506](https://arxiv.org/abs/2511.03506) |
| M-EXT-037 | M-WORK-022 | CAM | 2025 | constructivist schemata | Ontology | Direct | reading-specific memory 应围绕文本理解组织 | Ontology / Formation | frontier | 中高 | Medium | [arXiv 2510.05520](https://arxiv.org/abs/2510.05520) |
| M-EXT-038 | M-WORK-022 | CAM | 2025 | overlapping clustering | Formation | Analogical | 新观察进入已有结构，而非孤立写入 | Formation | 算法重 | 高 | Medium | [arXiv 2510.05520](https://arxiv.org/abs/2510.05520) |
| M-EXT-039 | M-WORK-023 | ComoRAG | 2025 | dynamic workspace | Retrieval | Direct | 当前工作空间应区别于 durable memory | Retrieval / Context | 绑定 iterative RAG | 中 | Medium | [arXiv 2508.10419](https://arxiv.org/abs/2508.10419) |
| M-EXT-040 | M-WORK-023 | ComoRAG | 2025 | probing queries | Retrieval | Direct | 理解卡住时再 targeted recall | Retrieval | loop 过重 | 中 | Medium | [arXiv 2508.10419](https://arxiv.org/abs/2508.10419) |
| M-EXT-041 | M-WORK-024 | HippoRAG | 2024 | associative graph retrieval | Retrieval | Analogical | concept/thread links 可帮助远距多跳关联 | Retrieval / Storage | 需图 infra | 高 | Medium | [arXiv 2405.14831](https://arxiv.org/abs/2405.14831) |
| M-EXT-042 | M-WORK-025 | Semantic Anchoring | 2025 | linguistic anchors | Formation | Analogical | 阅读依赖 discourse/coreference 这类 textual anchors | Formation / Retrieval | frontier | 中 | Low-Med | [arXiv 2508.12630](https://arxiv.org/abs/2508.12630) |
| M-EXT-043 | M-WORK-026 | MemGuide | 2026 | intent + missing-slot retrieval | Retrieval | Direct | recall 应看当前意图与缺口，不止相似度 | Retrieval / Context | TOD slot 不能直搬 | 中 | Medium | [AAAI MemGuide](https://ojs.aaai.org/index.php/AAAI/article/view/40313) |
| M-EXT-044 | M-WORK-027 | Memory-as-Action | 2025 | memory editing as action | Working memory | Boundary | 划清 RL memory editing 不适合当前 RC | Boundary | 复杂度极高 | 极高 | High | [arXiv 2510.12635](https://arxiv.org/abs/2510.12635) |
| M-EXT-045 | M-WORK-002/029 | MemGPT/MemOS line | 2023–2025 | memory OS framing | Boundary | Negative | 防止项目被诱导成通用 memory OS | Boundary | 目标膨胀 | 极高 | High | [arXiv 2310.08560](https://arxiv.org/abs/2310.08560) |

### Adopt / Adapt / Reject by Work

| Work ID | Work | Adopt | Adapt | Reject | Why |
| --- | --- | --- | --- | --- | --- |
| M-WORK-001 | Generative Agents | slow-cycle reflection principle | tri-score retrieval; evidence-backed reflection | step-level pervasive reflection | M-EXT-001/002/003 |
| M-WORK-002 | MemGPT | hot vs archival boundary | virtual context only as light mental model | OS-style paging as design center | M-EXT-004/045 |
| M-WORK-003 | Letta memory blocks | label/description/value/limit contract | minimal always-visible slots | persona/human block defaults | M-EXT-005/006/007 |
| M-WORK-004 | Letta archival docs | out-of-context searchable store concept | archival semantics as durable memory tier | generic conversational archival as-is | M-EXT-004/007 |
| M-WORK-005 | MemoryBank | lifecycle awareness | decay/refresh as visibility logic | user personality synthesis | M-EXT-008/009 |
| M-WORK-006 | Mem0 paper | operation-centric framing | graph option only as future extension | graph-first interpretation | M-EXT-010/014 |
| M-WORK-007 | Mem0 docs | add/search/update/delete; metadata filters | conflict resolution tuned for source-grounded memory | raw transcript storage as default | M-EXT-010/011/012/013 |
| M-WORK-008 | Zep paper | temporal validity intuition | enterprise findings only as analogical support | benchmark claims as sole basis | M-EXT-016/018 |
| M-WORK-009 | Zep docs | facts vs summaries; episode evidence; observation layering | context assembly modes | full graph DB stack | M-EXT-015/016/017/018/019 |
| M-WORK-010 | A-MEM | structured note idea | links/tags with lightweight schema | unconstrained evolving memory network | M-EXT-020/021 |
| M-WORK-011 | LangGraph memory | semantic/episodic/procedural split; profile vs collection; hot/background | rename categories to fit reading | user-profile-centric examples | M-EXT-022/023/024 |
| M-WORK-012 | LangMem | background consolidation manager | procedural memory only if later needed | store/framework coupling | M-EXT-025/026 |
| M-WORK-013 | RAPTOR | multi-granularity abstraction insight | high-level reflective entry points | tree index as default memory backend | M-EXT-027 |
| M-WORK-014 | GraphRAG paper | local/global question distinction | lightweight structural aggregation | graph extraction pipeline | M-EXT-028/029 |
| M-WORK-015 | GraphRAG docs | retrieval-mode taxonomy | query-type aware policy | full GraphRAG infra | M-EXT-028/029 |
| M-WORK-016 | LongMemEval | stage-decomposed evaluation | ability taxonomy localized to reading | chat benchmark as sufficient final rubric | M-EXT-030/031 |
| M-WORK-017 | LoCoMo | temporal continuity requirement | chapter-order / state-change probes | dialogue-specific tasks | M-EXT-032 |
| M-WORK-018 | LoCoMo-Plus | latent-constraint risk lens | constraint consistency probe for reading | frontier benchmark as definitive | M-EXT-033 |
| M-WORK-019 | StructMemEval | structure-aware evaluation | RC-specific structural tasks | direct leaderboard chasing | M-EXT-034 |
| M-WORK-020 | MemoryBench | continuality as future concern | later multi-run evaluation | immediate benchmark adoption | M-EXT-035 |
| M-WORK-021 | HaluMem | operation-level hallucination framing | read/update/retrieval diagnostics | direct benchmark adoption before trace exists | M-EXT-036 |
| M-WORK-022 | CAM | reading-specific memory framing | selected constructivist ideas | full clustering stack | M-EXT-037/038 |
| M-WORK-023 | ComoRAG | impasse-triggered targeted recall | dynamic workspace as bounded carry-forward context | iterative RAG loop as default | M-EXT-039/040 |
| M-WORK-024 | HippoRAG | association/link intuition | lightweight JSON links | knowledge graph backend now | M-EXT-041 |
| M-WORK-025 | Semantic Anchoring | discourse/coreference anchor intuition | selective linguistic metadata | full NLP anchoring stack now | M-EXT-042 |
| M-WORK-026 | MemGuide | intent-driven retrieval | gap-aware filtering localized to reading | TOD slot machinery | M-EXT-043 |
| M-WORK-027 | Memory-as-Action | boundary insight only | none for near-term | RL memory editing route | M-EXT-044 |
| M-WORK-028 | Memory mechanism survey | terminology map only | bibliography seeding | survey as final evidence | Background only |
| M-WORK-029 | MemOS | boundary signal | future strategic scan only | current-scope adoption | M-EXT-045 |
| M-WORK-030 | Incremental multi-turn memory eval | future follow-up candidate | possible next-round benchmark scan | current-cycle dependence | frontier, unread |
| M-WORK-031 | StoryBench | future reading benchmark lead | later narrative eval mapping | immediate inclusion as core evidence | frontier, unread |
| M-WORK-032 | Beyond Goldfish Memory | historical background | none | direct design borrowing | background only |

## 跨工作综合与 Reading Companion 相关性预览

### Cross-work Synthesis

Agent Memory 的主流范式大致可分成五类。第一类是**transcript / history memory**：把对话或 observation 留在可检索存储中，需要时召回。第二类是**structured item memory**：memory 被显式建模成带 ID、metadata、schema 的条目，典型代表是 Mem0、A-MEM、部分 Letta block 使用方式。第三类是**hierarchical / summary memory**：通过反思、总结、聚合构建更高层入口，典型代表是 Generative Agents、RAPTOR、GraphRAG、Zep summaries/observations。第四类是**typed memory**：把 semantic / episodic / procedural 分离，典型代表是 LangGraph/LangMem 与部分 cognitive-inspired 工作。第五类是**memory OS / intrinsic policy**：把记忆管理提升为系统级资源调度或可学习策略，典型有 MemGPT 的 OS 比喻、Memory-as-Action、MemOS 方向。对 Reading Companion 最相关的是第二、第三、第四类；最容易诱导过度复杂化的是第五类。

“从 transcript / summary memory 到 structured / lifecycle-managed memory 的演进”总体上是成立的，但需要两点修正。第一，这不是线性进步史；很多 production 系统仍然主要靠 history + retrieval。第二，真正成熟的演进不是“上图数据库”，而是“把写入、更新、失效、检索、组装显式化”。Mem0、Zep、LangGraph docs 都在说明这一点：memory 的先进性往往体现在 contract 与 lifecycle，而不是存储引擎名称。

formation 的演进很清楚：早期更像 summarization / logging；随后变成 extraction；再往后是 structured construction；再进一步是 reflection / consolidation；前沿则开始讨论 pre-storage reasoning、impasse-triggered recall、以及对 existing memory 的 update 而非 append。对 RC 而言，最重要的不是追最前沿，而是先承认 formation 不是一个单点动作：它至少包括“是否值得记”“记成什么粒度”“与已有 memory 什么关系”“是否保留 evidence pointers”。

management 方面，主流做法已经明显从 add-only 走向 add / update / refresh / merge / consolidation / forgetting / invalidation / supersede。MemoryBank 给了 decay/refresh 直觉；Mem0 给了 explicit update/delete 操作；Zep 给了 temporal validity 与 retire older observations 的表达。一个重要结论是：**forgetting** 不应被简单理解为“删除事实”，更多时候它代表的是可见性下降、热度下降、或旧版本被 supersede。对于强调 source-grounded 和审计的 RC，这一点尤其关键。

retrieval 的演进也很明确：从 simple top-k，逐渐变成多因子、多阶段、多粒度、多模式。Generative Agents 把 retrievability 做成 recency/relevance/importance 的联合；Mem0 把 filters / rerank / thresholds 做成产品级显式机制；MemGuide 把当前任务意图与缺口带进 retrieval；GraphRAG 把问题类型切成 local/global；ComoRAG 把 retrieval 变成 reasoning impasse 的响应动作。这说明 retrieval policy 的核心不再只是“相似”，而是“当前为什么要找、找哪一类、找多少、装到哪里”。

context engineering 与 memory retrieval 的边界可以这样划：retrieval 解决“从总体存储里找什么”，context engineering 解决“找出来以后怎么编进当前上下文”。Zep 把这两个面区分得很清楚：有 context block、template、advanced construction 三层装配；Letta 则强调某些 block 永远在 prompt 中而 archival memory 需按需搜索。对 RC 而言，这是一个重要边界：不能把“回忆了什么”与“当前 packet 怎么拼”混成一个黑箱。

evaluation 方面，领域明显正在从 result correctness 走向 groundedness / usefulness / non-drift / operation-level failure。LongMemEval 把 indexing / retrieval / reading 分层，并把 updates / abstention 列为能力；LoCoMo 把 temporal/causal continuity 拉进来；LoCoMo-Plus 把 latent constraints 拉进来；StructMemEval 检查 memory structure 本身；HaluMem 则把 extraction/update/QA 三阶段的 hallucination 拆开。对 RC 最关键的启示是：如果没有 formation/update/audit trace，评估就只能停留在终端表象。

reading / narrative / long-form memory 的特别启发主要有四个。第一，阅读 memory 与聊天 memory 的源头不同，更应该围绕 source-grounded observations 组织，而不是围绕 user facts 组织。第二，长叙事推理比普通 recall 更依赖 continuity、entity drift 控制与高层框架的渐进形成。第三，阅读中 retrieval 往往是 impasse-driven、question-driven、gap-driven，而不是每步固定执行。第四，文本理解高度依赖 discourse / reference / structure 等 textual anchors，因此 Memory 不能只剩 embedding 相似度。CAM、ComoRAG、HippoRAG、Semantic Anchoring 都在不同侧面指向这四点。

对 Reading Companion 最相关的趋势，不是 graph DB、vector DB、memory OS、multi-agent shared memory、RL-based context editing，而是以下四种“较轻而强”的方向：**source-grounded itemization**、**lifecycle-managed updates**、**slow-cycle consolidation**、**stage-aware evaluation**。最容易诱导项目过度复杂化的趋势，则是 Memory OS 化、graph-first 基建、自由演化网络、以及没有 trace 支撑的复杂 benchmark 套件。

### Reading Companion Relevance Preview

| External pattern | Possible RC relevance | Needed project-side validation | Risk |
| --- | --- | --- | --- |
| Memory hierarchy | 可能支持 hot / durable / reflective 分层 | 检查当前 stores 与 carry-forward packet 是否已有边界 | 照搬 OS-style paging |
| Block contract | 可能支持 lightweight item/store contract | 检查当前 item schema 是否缺 description/limit 类字段 | 过早抽象出过多块类型 |
| Explicit update operation | 可能支持 memory item lifecycle | 检查 `state_ops` 是否已隐含 update/refresh/supersede | 过早引入 revision system |
| Explicit delete / retire / invalidate | 可能支持旧理解退役 | 检查哪些错误应 invalidate，哪些应仅降权 | 删除过度造成证据丢失 |
| Facts vs summaries coexist | 可能支持细粒度 state 与高层 frame 共存 | 检查当前 frame 是否能保留 supporting source refs | summary 漂移成为伪真值 |
| Observations / durable patterns | 可能支持 reflective frame / stable thread judgment | 检查是否真有多证据支撑的 pattern 类 memory | 高层 pattern 脱离 source |
| Hot-path vs slow-cycle writes | 可能支持 unit write 与 chapter/book consolidation 分工 | 检查 runner settlement 是否适合 slow-cycle | 两条路径语义重叠 |
| Metadata filters before fancy infra | 可能先提升 retrieval precision | 检查最小 metadata 集：chapter/store/type/run/source | 空谈 vector/graph，忽略 metadata |
| Intent- / gap-aware retrieval | 可能改善“当前为什么要回忆” | 检查现有阅读问题/意图表示是否足够清晰 | 用复杂策略掩盖上游 formation 问题 |
| Impasse-triggered recall | 可能支持 targeted look-back / detour recall | 检查系统如何识别真正理解缺口 | 召回过频，打断主线阅读 |
| Multi-granularity retrieval | 可能支持 frame 级与 item 级双入口 | 检查高层 frame 质量是否足以做入口 | 高层入口不可靠，反而误导 |
| Stage-aware evaluation | 可能支持 formation / retrieval / use / abstention 诊断 | 检查 audit trace 是否足够定位失败层 | 没有 trace 时只剩空框架 |
| Operation-level hallucination eval | 可能支持 formation/update 污染诊断 | 检查 read_audit / settlement_audit 粒度是否够细 | 诊断目标过多、执行不了 |
| Temporal validity | 可能支持后文修正前文理解时的 supersede 语义 | 检查当前数据模型是否能表达 validity / superseded_by | 简单 overwrite 丢失历史 |
| Lightweight links | 可能支持 concept / thread / frame 的结构 retention | 检查 JSON links 是否就足够 | 误以为必须上 graph DB |
| Procedural memory | 可能支持未来的阅读策略学习 | 先确认项目是否真的需要策略记忆层 | 自改提示词失控 |
| Narrative continuity benchmarks | 可能支持 chapter order / latent constraints probes | 需要定义阅读场景的连续性检测点 | 直接拿对话 benchmark 套用 |
| Memory OS / RL memory editing | 现在主要用于划边界 | 除非产品目标大幅扩张，否则不建议验证 | 复杂度与不透明度急剧上升 |

## 研究缺口与引用审计

### Research Gaps

| Gap | Why it matters | Suggested next action |
| --- | --- | --- |
| 多数论文未全文逐节精读 | 会限制对细节机制与消融设计的把握 | 下一轮优先精读 Generative Agents、Mem0、Zep、LongMemEval、CAM、ComoRAG |
| reading-specific memory 一手工作仍偏少且较新 | 直接贴近 Reading Companion 的证据仍不足 | 把 CAM、ComoRAG、HippoRAG、Semantic Anchoring 列为下一轮重点 |
| frontier benchmarks 成熟度不足 | 容易把实验性 benchmark 当标准 | 对 LoCoMo-Plus、StructMemEval、HaluMem 做单独 maturity review |
| operation-level memory evaluation 尚未直接适配阅读 agent | RC 很需要这类评估，但现成 benchmark 场景不完全匹配 | 下一轮做“外部 benchmark 元件 → RC 评估维度”映射 |
| graph-style memory 与 lightweight JSON links 的边界仍未证实 | 直接影响是否过早上复杂基础设施 | 下一轮先做项目侧需求诊断，再判断是否只需 links |
| procedural memory 对 RC 是否必要仍不清楚 | 关系到是否引入 prompt refinement 或策略层 | 暂缓；先把 source-grounded state memory 做扎实 |
| 2025/2026 frontier work 变化快 | 可能很快出现新版本、新评估或撤稿/改稿 | 下一轮开始前再做一次 targeted freshness check |
| 某些 Tier 2/Tier 3 工作只做了定位 | 无法作为高置信论据 | 若进入下一轮范围，再逐项补一手页面 |
| 用户提供综述 PDF 的参考文献未全部追完 | 可能遗漏 reading-specific 文献线索 | 下一轮从综述参考文献中挑 5–8 篇最贴题的一手来源继续追 |

### Citation Quality Audit

| Check | Result | Notes |
| --- | --- | --- |
| 是否没有输出 `turn...` 作为最终 citation？ | Pass | 正文使用了可渲染引用与稳定链接；未把 `turn...` 当人类可读最终 citation 文本 |
| 是否为所有 Work Cards 添加年份？ | Pass | 已覆盖 |
| 是否为所有 Work Cards 添加 stable URL？ | Pass | 已用稳定链接或官方 docs 链接 |
| Tier 1 工作是否至少覆盖 14 个？ | Pass | Bibliography 中 Tier 1 超过 14 个 |
| Reading / Narrative / Long-form direction 是否至少覆盖 5 个？ | Pass | CAM、ComoRAG、HippoRAG、Semantic Anchoring、MemGuide、Memory-as-Action、LoCoMo family |
| Evaluation 方向是否至少覆盖 5 个？ | Pass | LongMemEval、LoCoMo、LoCoMo-Plus、StructMemEval、MemoryBench、HaluMem |
| Production / official docs 方向是否至少覆盖 4 个？ | Pass | Letta、Mem0、Zep、LangGraph、LangMem、GraphRAG docs |
| 每个 Work Card 是否有一手来源或明确标注二手？ | Pass | 已标 read status 与 maturity |
| 每个 Evidence Card 是否有 reasoning bridge？ | Pass | 全部卡片都写了场景相似点、差异点与支撑理由 |
| 是否区分 Direct / Analogical / Negative / Boundary / Background support？ | Pass | 已显式区分 |
| 是否避免把项目内部假设写成外部事实？ | Pass | 只把 repo 信息当约束，不当外部结论 |
| 是否过度依赖综述而非一手来源？ | Pass | 综述只当入口；主证据来自论文官方页面与官方 docs |
| 是否明确标注未深读来源？ | Pass | bibliography 中已区分 deep-read / partial-read / skimmed / future |
| 是否没有输出项目设计决策 / Candidate Decision Ledger？ | Pass | 本报告止步于外部证据与 adopt/adapt/reject 级别，不进入项目设计决策 |
