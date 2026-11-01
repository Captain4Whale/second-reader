# Memory Ontology Design v0

## 1. Scope and Purpose

本页定义 Reading Companion / Second Reader 的 **Memory Ontology v0**。

它继承 Phase 0 的 Shared Memory–Planning Mechanism Charter：Memory 与 Planning 共用同一张 territory map，Memory 不是“把更多东西记住”，而是从 accepted source units 中形成的 source-grounded reading state；Planning 只能通过 bounded、typed、source-ref-preserving projections 使用 memory；运行原则是 **LLM proposes; deterministic runner settles**。

本页只回答 ontology 问题：什么是 memory，什么不是 memory；现有 memory-related stores 的身份、边界、可写入内容、source-grounding、visibility、lifecycle、Planning 使用方式与 audit/evaluation 角色。它为后续 Memory Formation、Management / Evolution、Retrieval / Utilization、Evaluation、Planning Ontology 提供基础，但不替代那些页面。

本页不是代码实现路线，不是 Codex task，不是新的 agent architecture proposal，也不是 Agent Memory 外部综述。当前目标是让现有 `attentional_v2` 更清晰、更可靠、更可审计，而不是引入更复杂的系统。

------

## 2. Current Implementation Understanding

当前项目是 Reading Companion workspace，默认机制是 `attentional_v2`，`iterator_v1` 保留为 fallback / legacy-compatible path。机制目录也明确把 `attentional_v2` 标为 current default / live mechanism。

产品定位不是摘要器，也不是服务式助手，而是一个 text-grounded、legible、self-propelled 的共读心智；产品价值来自 witnessing a living reading mind think while reading，而 prior knowledge 的使用不能变成 text-detached certainty。 这决定了 Memory Ontology 不能迁移成普通聊天助手的 user profile memory，也不能迁移成通用 Memory OS。

### 2.1 Source corpus and reading locus

共享 source truth 是 `public/book_document.json`。它包含 canonical chapter order、paragraph records、sentence records、locators；paragraph layer 是稳定 source substrate；sentence layer 是 parse-time helper，而不是当前主线阅读 lattice。当前 `attentional_v2` 使用 paragraph + char-offset `SourceCursor`，当前 citations 使用 inline paragraph-offset `SourceRef`，没有共享 Anchor Bank 或 SourceRef registry。

在当前机制中：

- `SourceCursor` 是当前阅读位置，包含 `chapter_id / chapter_ref / paragraph_index / char_offset`；
- `SourceSpan` 是 accepted unit 的 end-exclusive `[start_cursor, end_cursor)`；
- `SourceRef` 是 inline paragraph-offset source citation，不是 registry entry；
- `Unit Span Ledger` 记录已接受并读取的 source spans，是 coverage / resume fact，不是 semantic memory。

这些事实已经在 `current-state.md` 中作为当前主线状态记录：`Navigate.choose_next_unit` 看到 adaptive paragraph-offset preview，返回 `end_anchor_text`，Reading Runner 解析为 accepted `SourceSpan`，推进 cursor，并写入 `unit_span_ledger.jsonl`；SourceRef cutover 已落地，new runtime/checkpoint truth 不再依赖 `anchor_bank`。

### 2.2 Current live loop

当前 live loop 应理解为：

```text
survey orientation
  → Navigate.choose_next_unit
  → Read
  → Reading Runner post-read settlement
  → cursor advance / unit ledger / audit
  → chapter-end slow-cycle
```

`survey` 只是 structural orientation，不做隐藏全文阅读，不产生 visible reactions，不写 durable reading memory。`Navigate.choose_next_unit` 是唯一 current selector；mainline unitization 与 detour localization 都在同一入口内。`Read` 的 current contract 是 `reading_impression / surfaced_reactions / memory_uptake_ops / optional detour_need`。Reading Runner settlement 确定性应用 memory uptake，持久化 surfaced reactions，写 audit，记录 accepted unit span，并推进 cursor。

这意味着：`Read` 不是最终 state writer。它提出 bounded write intent；settlement / state_ops 才是 authoritative state mutation layer。

### 2.3 Current memory-related stores

当前 runtime artifact map 中已经有以下机制私有文件：`active_attention.json`、`concept_registry.json`、`thread_trace.json`、`reflective_frames.json`、`knowledge_activations.json`、`reaction_records.json`、`reconsolidation_records.json`、`unit_span_ledger.jsonl`、`read_audit.jsonl`、`settlement_audit.jsonl` 等。

代码 schema 已经定义：

- `ActiveAttention`：primary hot attention state；
- `ConceptRegistryState`：primary durable object-memory layer；
- `ThreadTraceState`：primary durable trace / line layer；
- `ReflectiveFramesState`：slower reflective layer；
- `KnowledgeActivationsState`：prior knowledge activation ledger plus current use-policy mode；
- `ReactionRecordsState`：append-only mechanism-owned durable reaction history；
- `ReconsolidationRecordsState`：append-only ledger of reconsolidation events；
- `ReadUnitResult`：`reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`；
- `StateOperationType`：`append / update / close / link / create / cool / drop / promote / supersede / reactivate / resolve` 等。

### 2.4 Current settlement and projection behavior

`state_ops.py` 当前对 operations 做确定性应用：`active_attention` 支持 create / update / reactivate / cool / resolve / close / link / drop；concept / thread 中 append / create / link 会归一化为 update，close 会归一化为 resolve，drop 会移除；source refs 会 merge / dedupe；reflective item 可以被 superseded 而不改写原 statement。

`state_projection.py` 当前构造 bounded `state_packet.v1`：active attention digest、concept digest、thread digest、reflective digest、source_ref digest、recent reactions、refs、continuation capsule。它是 prompt-facing projection，不是 authoritative state。

`read_context.py` 区分了两种 supplemental context：

- `active_recall`：从 concept / thread / reaction records 中取回尚未 carry 的 memory state；
- `look_back`：根据 SourceRef / SourceSpan 回到 earlier source excerpts。

### 2.5 Current slow-cycle and audit behavior

`slow_cycle.py` 负责 surfaced reaction persistence / compatibility projection / reflective promotion / reconsolidation / chapter consolidation。它可以产生 cooling operations、promotion candidates、knowledge activation updates、cross-chapter carry-forward，也可以处理 reflective promotion 与 reconsolidation。

`observability.py` 记录：

- `read_audit.jsonl`：unit source span、carry-forward refs、context request、supplemental refs、stop reason、budget exhaustion、reading impression、surfaced reactions、memory uptake ops、detour need；
- `settlement_audit.jsonl`：memory op counts、target-store distribution、active_attention / concept_registry / thread_trace / reaction_records 的 compact ID deltas；
- Memory Quality probe snapshots 经 observability boundary 产生。

### 2.6 Runtime-artifact evidence boundary

本页没有直接逐行打开真实运行目录中的 `read_audit.jsonl / settlement_audit.jsonl / unit_span_ledger.jsonl / active_attention.json / concept_registry.json / thread_trace.json / reaction_records.json / reconsolidation_records.json`。GitHub search 只返回了 docs / code references，没有给出可直接审计的 runtime JSONL rows。因此本文对 runtime quality 不做独立验证结论。

本文区分：

- **architecture-level evidence**：当前 repo docs 与代码结构显示的机制边界；
- **contract-level evidence**：schema、prompt、state_ops、projection、audit 的契约；
- **runtime-artifact evidence**：本轮不可直接审计；
- **assessment-level inference**：P0 Charter、Memory Assessment、Planning Assessment 的总结判断。

------

## 3. Memory Ontology Core Definition

Reading Companion 中的 **reading memory** 是：

> 从已被 Reading Runner 接受并读取的 source units 中形成的、带有 SourceRef 或明确 warrant 的 reading state。它能在后续阅读中支撑 continuity、active recall、look-back decision、detour need、concept/thread carry-forward、slow-cycle consolidation、faithful callback 与 re-entry。它不是 source text 本身，不是 prompt packet，不是 visible reaction 本身，不是 audit trace，也不是 prior knowledge 的自由发挥。

这个定义有几个必要排除项。

**Source corpus is not memory.**
`book_document.json` 是被读对象与 locator truth。它提供 source substrate，但不代表系统已经“记住”了它。Memory 必须来自 accepted source units 之后形成的 reading state。

**Visible reaction is not semantic memory.**
`surfaced_reactions` / `reaction_records` 是面向用户的 reading-time trace。它可以被保存、回看、用于 callback / FVI audit，也可以在 bounded projection 中作为 recent continuity，但它不自动变成 concept / thread / reflective memory。

**Audit trace is not runtime memory.**
`read_audit`、`settlement_audit`、`unitization_audit`、debug events 是诊断层。它们可以解释一次状态变化如何发生，但不应默认进入 prompt，也不应成为后续阅读的 semantic context。

**Prior knowledge activation is not source-given truth.**
`knowledge_activations` 记录“某个 prior / external knowledge 为什么被允许参与阅读”的 warrant。它不是书中事实，不能自动合并进 book-grounded concept memory。

**Evaluation evidence is not memory.**
Memory Quality probes、Callback / FVI judge reports、benchmark outputs、eval summaries 是评估证据，不是下一次 reading run 的 runtime state。

**Prompt-facing projection is not authoritative state.**
`state_packet.v1`、source_ref digest、navigation context、read prompt packet 都是 bounded projections。它们可以被 Planning / Read 使用，但不能反向当成完整真实 memory store。

------

## 4. Territory Map

| Territory                                     | Definition                                                   | Memory status                      | Boundary rule                                                |
| --------------------------------------------- | ------------------------------------------------------------ | ---------------------------------- | ------------------------------------------------------------ |
| Source corpus                                 | `book_document.json` 中的 parsed source truth，包括 chapters / paragraphs / sentences / locators | Not memory                         | 可被引用、回看、读取；不能因为存在于 source corpus 就算已形成 memory |
| Reading locus / source cursor / accepted unit | 当前 cursor、preview、accepted `SourceSpan`、unit ledger     | Not semantic memory                | 记录阅读位置与覆盖事实；不是概念或理解                       |
| Reading memory                                | 从 accepted units 中形成的 source-grounded reading state     | Memory                             | 包括 active_attention、concept_registry、thread_trace、reflective_frames；必须有 SourceRef 或明确 warrant |
| Prompt-facing projection                      | `state_packet.v1`、carry-forward context、source_ref digest  | Projection, not state              | bounded、typed、临时；不能作为 authoritative memory          |
| Visible reaction                              | `surfaced_reactions` 与 persisted `reaction_records`         | Visible trace, not semantic memory | 可做 callback/FVI evidence；不自动进入 concept/thread        |
| Visible reading route surface / route disclosure | 未来可能展示 Second Reader 自己的 `reading_route_trace`、detour、look-back、restore 的产品 surface | Visible product surface, not memory | Derived from route trace / audit；does not write memory；does not change navigation |
| Prior / external knowledge activation         | 被 source trigger 激活的先验知识 warrant                     | Warrant ledger, not source truth   | 必须标注 trigger、confidence、warrant、conflict；不能冒充书中事实 |
| Audit trace                                   | `read_audit`、`settlement_audit`、`unitization_audit`、debug events | Diagnostic, not runtime memory     | 可供 evaluation / debugging；默认不进 prompt                 |
| Evaluation evidence                           | probes、judge reports、benchmark summaries                   | Eval artifact, not memory          | 不自动回写 runtime memory                                    |
| Planning-facing memory projection             | 给 Planning 的 bounded typed memory digest                   | Interface projection               | Planning 只能消费 projection；不能直接读完整 durable store   |

------

## 5. Store Ontology

本节各 store 的 **Lifecycle meaning** 只定义 ontology-level semantic boundary：这些词说明状态变化在语义上大致意味着什么；最终 operation matrix 与合法转移以后续 Memory Management / Evolution Design 为准。

### 5.1 `active_attention`

`active_attention` 是当前最热的 near-term reading state。它保存仍在拉动接下来几步阅读的 question、tension、interpretation、motif、focus 或 working distinction。它可以包含 hypothesis-like material，但它不是 stable semantic truth。

**Admission rule.**
只有当一个 unit 产生的关注点会继续影响近端阅读时才进入。例如：当前未解决的问题、需要下一段验证的 tension、刚被作者引入但还没有稳定归档的定义、需要跨接下来几段 carry 的 focal contrast。

**Rejection rule.**
普通 passing understanding、漂亮但只适合 visible trace 的 margin note、已稳定定义的概念条目、跨章 thread、章末高层 frame、prior knowledge activation、audit/debug reason 都不应塞入 active_attention。

**Source-grounding.**
每个 active item 应保留 `source_refs[]`。若由 Read 提出，payload 可带 unit-local `source_quote / source_role`，由 runner 解析成 inline SourceRef。若 slow-cycle carry-forward，一个 item 的 `source_refs` 不得因 omitted field 被擦除；当前项目已把 active_attention carry-forward source-ref erasure 作为真实风险修复过。

**Allowed writers.**

- `Read`：只能提出 `memory_uptake_ops`；
- settlement / state_ops：应用 create / update / reactivate / cool / resolve / close / link / drop；
- slow-cycle：可以 cool、resolve、carry forward、reactivate；
- evaluation：不得写；
- manual correction：只允许 source-ref-preserving、audited correction。

**Prompt visibility.**
默认通过 bounded active_attention digest 进入 prompt，不以完整 store 进入。当前 projection 最多输出 bounded active items / hot items。

**Planning visibility.**
Planning 可以使用 active_attention digest 判断当前 reading pressure、detour value、是否继续主线、是否需要 recall / look-back。Planning 不得把 active_attention 中的 hypothesis 当成 settled truth。

**Lifecycle meaning.**

- `create / append / update`：近端关注点被引入或刷新；
- `reactivate`：此前 cooled / resolved 但又被当前 source 重新激活；
- `cool`：从 hot view 降温，不代表语义失效；
- `resolve / close`：当前问题或 tension 已被 source 暂时解决；
- `drop`：从 hot store 移除，主要是 visibility lifecycle，不应当作 semantic deletion；
- `supersede`：当前不是 active_attention 的主语义；如果涉及版本效力，应交给 concept/thread/reflective 或后续 Management 页。

**Audit / evaluation use.**
Memory Quality probe snapshots 应检查 active_attention 是否保留当前最重要、最主线、最忠实的 near-term state。Callback 可通过 active_attention ref 成为 prior_link support。FVI 风险是把 active hypothesis 过早当成 source-established truth。

**Complexity caution.**
最容易被误用成“所有有趣想法的桶”。v0 规则是：active_attention 只承载仍会拉动近端阅读的热状态。

------

### 5.2 `concept_registry`

`concept_registry` 是 source-grounded concept / object / definition / model / classification / named distinction registry。它承载书中已经被 accepted units 明确给出、命名、定义、区分或稳定复用的对象层记忆。

**Admission rule.**
可以进入的内容包括：作者给出的核心定义、阶段模型、分类、命名区分、关键对象、可复用概念框架，以及后续阅读反复需要引用的 source-grounded term。

**Rejection rule.**
不要把 chapter summary、thread development、visible reaction、prior knowledge guess、theme-only association、reading strategy、audit explanation 塞进 concept_registry。概念条目不是“摘要句子库”。

**Source-grounding.**
每个 concept entry 必须有 `source_refs[]`，至少能回到首次定义或关键 evidence span。若概念来自多个 source units，source_refs 应 merge / dedupe，而不是覆盖旧 evidence。

**Allowed writers.**

- `Read`：通过 `memory_uptake_ops` 提出 create / update / link / resolve；
- settlement / state_ops：规范化与 upsert；
- slow-cycle：可在后续设计中提出 consolidation / supersede / merge candidate，但不应绕过 settlement；
- evaluation：不得写；
- manual correction：只允许 audited、source-ref-preserving correction。

**Prompt visibility.**
通过 bounded concept digest 进入 prompt；当前 digest limit 是小量条目，按 source_refs 数量、状态、key 排序。

**Planning visibility.**
Planning 可以使用 concept digest 判断当前 unit 是否依赖 earlier definition、是否应 active recall、是否需要 look-back source calibration。Planning 不得直接读取完整 registry。

**Lifecycle meaning.**

- `create / update`：概念首次进入或定义被丰富；
- `link`：与 thread 或其他 concept 建立轻量关联；
- `resolve`：概念相关 unresolved question 被 source 暂时关闭；
- `reactivate`：后文重新让该概念 become active；
- `drop`：极少使用，通常应改为 status / supersede；
- `supersede`：v0 接受为后续 Management 页需要正式化的 semantic validity operation；当前不要求 concept store 直接实现完整 supersede chain。

**Audit / evaluation use.**
Memory Quality 中的 structural-signal supplement 应重点检查 concept_registry 是否保留 source-given definitions、classifications、stage models、named distinctions。Callback / FVI audit 应检查 visible reaction 对 concept 的引用是否有 source_ref 支撑，而不是仅凭名称相似。

**Complexity caution.**
最容易被误用成 generic summary bucket。v0 明确：concept_registry 是 object / definition / distinction layer，不是 reading impression store。

------

### 5.3 `thread_trace`

`thread_trace` 是跨 passage / 跨章节延续的 line、motif、argument、contrast、question、development trace。它保存“某条线如何持续展开”，不是保存“某个词是什么意思”。

**Admission rule.**
可以进入：反复出现并发生变化的 motif、argument line、人物/思想/结构关系、持续 unresolved question、跨 source span 的对照或推进。一个 thread 至少应有两个潜在或实际 source footholds，或者明确预计会继续拉动后文。

**Rejection rule.**
单个定义、孤立概念、纯 visible reaction、一次性 local highlight、prior knowledge link、chapter summary 不应进入 thread_trace。

**Source-grounding.**
每个 thread entry 应保留 source_refs set；新增 source evidence 应 merge 而不是替代。Thread 的 value 来自 source sequence，因此 source_refs 的顺序和阶段性很重要。

**Allowed writers.**

- `Read`：通过 memory_uptake_ops 提出 create / update / link / resolve；
- settlement / state_ops：确定性 upsert / merge；
- slow-cycle：可 cool / resolve / promote thread summary candidate；
- evaluation：不得写；
- manual correction：需 audited。

**Prompt visibility.**
通过 bounded thread digest 进入 prompt，当前 digest limit 小，优先带 source_refs 的 entries。

**Planning visibility.**
Planning 可使用 thread digest 判断主线 continuity、detour 是否有价值、look-back 是否必要、是否需要 active recall。Planning 不得把 thread digest 当成完整 route plan。

**Lifecycle meaning.**

- `create`：一条跨 passage line 开始；
- `update / link`：新 source span 加入该 line；
- `resolve`：该 thread 的当前问题被 source 关闭；
- `reactivate`：后文再次激活；
- `cool`：v0 建议通过 active_attention cooling 处理，不直接把 thread 降温；
- `supersede`：应作为 semantic validity lifecycle 后续设计；
- `drop`：谨慎，通常仅用于误写或 corrupted entry。

**Audit / evaluation use.**
Memory Quality 检查 thread_trace 是否保留 mainline lines；Spontaneous Callback 看 visible reactions 是否自然回到 earlier thread；FVI 检查 thread linkage 是否只是 theme-only similarity 或 hard-linking。

**Complexity caution.**
最容易被误用成 concept_registry 的重复副本。v0 规则：concept 是 object，thread 是 development。

------

### 5.4 `reflective_frames`

`reflective_frames` 是 slow-cycle promoted higher-order memory。它承载 chapter_understandings、book_level_frames、durable_definitions、stabilized_motifs、resolved_questions_of_record、chapter_end_notes 等。

它不是每个 read unit 的 reflection，也不是随手总结。它必须来自多个 source-grounded lower-level signals，或者来自章末/会话末明确 consolidation。

**Admission rule.**
只有当一个 understanding 已经 durable enough beyond immediate local moment，且有 supporting source set，才可进入。包括：章级理解、跨章 frame、被 source 稳定的 durable definition、稳定 motif、被明确解决的问题记录。

**Rejection rule.**
单段感想、漂亮反应、单个未验证 hypothesis、prior knowledge flourish、reader strategy note、audit summary、visible route disclosure 不应进入 reflective_frames。

**Source-grounding.**
每个 ReflectiveItem 应有 source_refs，并保留 confidence_band、promoted_from、status、chapter_ref。若新 frame 替代旧 frame，应显式 supersede，而不是 silent overwrite。

**Allowed writers.**

- Read-path：不得写；
- settlement：不得直接从 Read ops 写；
- slow-cycle：唯一正常 writer，通过 reflective_promotion / chapter_consolidation / reconsolidation；
- manual correction：仅 audited correction；
- evaluation：不得写。

**Prompt visibility.**
只通过 bounded reflective digest / chapter reflective frame 进入 prompt。完整 reflective store 不应进 prompt。

**Planning visibility.**
Planning 可以使用 reflective digest 做 macro carry-forward：下一章保留哪些高层 frame、哪些 thread 已 resolved、哪些 open obligations 仍需关注。但 Planning 不得把 reflective_frames 改写成 plan store。

**Lifecycle meaning.**

- `promote`：从 active / concept / thread / reaction / chapter sweep 中提升；
- `withhold`：候选不足，不进入；
- `supersede`：新 frame 替代旧 frame，旧 statement 保留但标记 superseded；
- `resolve`：frame 代表的问题已被 source 关闭；
- `cool`：通常不是 reflective_frames 的主操作，visibility 可由 projection 控制；
- `drop`：仅用于 corruption / manual repair，不用于正常演化。

**Audit / evaluation use.**
Memory Quality 可检查 reflective frames 的 salience、mainline fidelity、organization、fidelity。FVI 风险是 reflective frame 过早概括、脱离 source、或把 prior knowledge 当成书中结构。

**Complexity caution.**
最容易被误用成 per-unit reflection 或 chapter summary dump。v0 明确：reflective_frames 是 slow-cycle promoted higher-order memory。

------

### 5.5 `reaction_records`

`reaction_records` 是 append-only visible reaction history。它保存用户可见的 reading-time thoughts / margin notes / marks，来源是 `Read.surfaced_reactions[]` 经 settlement / reaction builder 持久化。

它不是 semantic memory，但它是产品体验和 long-span evaluation 的重要 evidence layer。

**Admission rule.**
只有 anchored surfaced reaction 可以进入。每条 reaction 必须有 current unit 的 exact `source_quote`，并形成 `primary_source_ref`。它可以带 `prior_link`、`outside_link`、`search_intent`，但 visible wording 不得泄漏 internal handles。

**Rejection rule.**
raw LLM reasoning、unanchored commentary、audit note、concept summary、thread summary、route-surface rationale、external search result 不应写入 reaction_records。强 reaction 不自动生成 concept/thread memory。

**Source-grounding.**
source_quote 必须来自 current unit；nodes normalization 会过滤不在 current unit 中的 source_quote，并过滤 visible internal reference handles。

**Allowed writers.**

- `Read`：提出 surfaced reactions；
- settlement / reaction builder：唯一正常 durable writer；
- slow-cycle：可产生 anchored optional chapter reaction only under later strict rules，但不能把它当 semantic memory；
- evaluation：不得写；
- manual correction：只用于 visible trace repair，需保留 audit reason。

**Prompt visibility.**
默认不进入 prompt。可以通过 recent reaction digest 或 active_recall bounded retrieval 进入，但只能作为 continuity / visible trace，不作为 source-given semantic truth。

**Planning visibility.**
Planning 可以看到 recent reaction digest，用来保持 visible continuity 或判断用户可见 trace 的节奏。Planning 不得把 reaction_records 当作 concept registry。Recent reaction digest may support visible continuity / callback awareness, but not semantic navigation justification by itself. `prior_link / outside_link / search_intent` may later be displayed as part of the reader's visible route or curiosity trace, but they are not route guidance and cannot steer navigation.

**Lifecycle meaning.**

- `append`：一次 visible thought 被记录；
- `supersedes_reaction_id`：后续 visible thought 可表示覆盖/修正旧 visible reaction；
- `reconsolidation_record`：解释 later reinterpretation；
- `drop`：默认不使用，除非合规、corruption、manual repair；
- reaction 本体通常 immutable。

**Audit / evaluation use.**
Spontaneous Callback 与 False Visible Integration 的主要 evidence layer。Callback 成功不是“有反应”，而是 reaction 自然、source-grounded 地使用 earlier material。FVI 检查 weak grounding、overclaim、hard-linking、theme-only similarity、memory drift。

**Complexity caution.**
最容易被误用成 semantic memory。v0 规则：reaction_records 是 visible trace；promotion 必须显式，并进入 concept/thread/reflective 的相应 contract。

------

### 5.6 `knowledge_activations`

`knowledge_activations` 是 prior / external knowledge warrant ledger。它记录某个先验知识被 source trigger 激活、为什么允许参与当前阅读、置信度、reading warrant、evidence hints、conflict source refs 与 status。

它不是 source-given truth，不是 book concept registry，也不是 external fact database。

**Admission rule.**
只有当 current source 触发了明确 prior / external reference，且该 reference 对理解当前 text 有潜在帮助时才进入。必须说明 trigger_source_ref、source_candidate、recognition_confidence、reading_warrant、role_assessment、status。

**Rejection rule.**
泛泛常识、模型自由联想、为了显得聪明的 outside link、无 source trigger 的百科知识、用户画像、搜索结果摘要，不应进入 knowledge_activations。

**Source-grounding / warrant.**
它的 grounding 不是“书中事实”，而是 “source trigger + reading warrant”。若 source 后续否定或弱化该 prior，应记录 conflict_source_refs，并进入 rejected / dropped 状态。`knowledge.py` 当前也将 active with warrant 的 activation 才转入 `book_grounded_plus_prior_knowledge` 模式。

**Allowed writers.**

- Bridge / knowledge activation path：可以 create / update / reactivate / cool / drop / supersede；
- slow-cycle：可以更新 activation status；
- Read-path：当前不应直接写 ordinary knowledge activation；
- evaluation：不得写；
- manual correction：只允许修正 warrant / status，并保留 source evidence。

**Prompt visibility.**
默认不进入 prompt。只有在 explicit projection gate 下，以 warrant-bearing form 进入：必须标注这是 prior activation，而不是 book truth。

**Planning visibility.**
Planning 可以在 rationale 中使用 knowledge activation，但必须带 trigger SourceRef、status、warrant、conflict markers。无 warrant 的 activation 不得成为 detour or visible route disclosure 理由。Knowledge activation cannot be the sole reason for detour or visible route disclosure unless paired with current source evidence and clearly marked as warrant, not source truth.

**Lifecycle meaning.**

- `weak`：触发很弱，只能提醒；
- `plausible`：有可用 warrant，但还需 source 校准；
- `strong`：source trigger 与 reading warrant 都较强；
- `rejected`：后续 source 或 audit 否定；
- `dropped`：不再可用或价值不足；
- `reactivate`：后文重新提供 warrant。

**Audit / evaluation use.**
FVI 的高风险区域。Memory Quality 不应把 prior activation 当作 source-retained memory；Callback 若使用 prior knowledge，需要区分 prior_link / outside_link / source-grounded callback。

**Complexity caution.**
最容易被误用成“书里已经说了”。v0 规则：knowledge_activations 是 warrant ledger，不是 concept truth。

------

### 5.7 `reconsolidation_records`

`reconsolidation_records` 是 append-only ledger，记录 later reading moment 如何 materially changes the meaning of an earlier persisted reaction or understanding。它是 reinterpretation ledger，不是新的 semantic memory store。

**Admission rule.**
只有当 later source materially reframes earlier reaction / thought 时进入。必须记录 prior_reaction_id、new_reaction_id、change_kind、what_changed、rationale。

**Rejection rule.**
普通补充、同义改写、单纯更漂亮的表达、无 source anchor 的 hindsight summary 不应进入。

**Source-grounding.**
reconsolidation 必须通过 prior reaction 与 later reaction 的 source refs 间接 grounded；later thought 应独立 anchored。

**Allowed writers.**

- reconsolidation slow-cycle：唯一正常 writer；
- Read-path：不得直接写；
- settlement：只负责持久化 normalized record；
- evaluation：不得写；
- manual correction：仅用于 corruption repair。

**Prompt visibility.**
默认不进入 prompt。若后续需要，可以通过 reflective/supersede digest 的结果体现，而不是把完整 reconsolidation ledger 放进 prompt。

**Planning visibility.**
Planning 通常不直接使用 reconsolidation_records。它可以看到由 reconsolidation 造成的 supersede / reflective update 结果。

**Lifecycle meaning.**

- append-only；
- 不用于删除 earlier reaction；
- 不替代 reflective supersede；
- 主要服务 audit lineage 和 FVI diagnosis。

**Audit / evaluation use.**
帮助解释 visible trace 的演化，特别是后文修正前文时，为什么某个 earlier reaction 不应再被当作 current understanding。FVI audit 可用它判断系统是否保留了 reinterpretation boundary。

**Complexity caution.**
最容易被误用成“第二套 reflective memory”。v0 规则：它只记录 reinterpretation event，不承载独立 frame。

------

### 5.8 `unit_span_ledger / read_audit / settlement_audit`

这三者是 non-memory diagnostic artifacts。

`unit_span_ledger` 记录 accepted source units，是 coverage / resume / source-locus fact。它不是 semantic memory。

`read_audit` 记录 Read intent、carry-forward refs、supplemental context、reading impression、surfaced reactions、memory_uptake_ops、detour_need 等。它不是 prompt context。

`settlement_audit` 记录 settlement transaction summary、memory op count、target-store distribution、state deltas。它不是 runtime memory。

**Allowed writers.**

- runner / observability：唯一正常 writers；
- evaluation 可读取；
- manual correction 默认不写，除非 audit repair policy 明确授权。

**Prompt / Planning visibility.**
默认不可见。Planning 不得用 audit dump 作为 reasoning context。Evaluation / debugging 可读取 audit，但结果不自动回写 memory。

**Audit / evaluation use.**
它们是 Memory Quality / Callback / FVI / runtime diagnosis 的 evidence spine。当前缺口不是 full snapshot，而是 per-op outcome / failure reason 的进一步结构化；这属于后续 Audit / Observability 页面。

**Complexity caution.**
最容易被误用成“既然完整就拿来当上下文”。v0 明确：diagnostic completeness 不等于 runtime usefulness。

------

## 6. Store Relationship and Layering

### 6.1 Layering diagram

```text
Source corpus
  public/book_document.json
  chapters / paragraphs / sentences / locators
        │
        ▼
Reading locus
  SourceCursor → Navigate.choose_next_unit → accepted SourceSpan
        │
        ▼
Read result
  reading_impression        = temporary impression, not durable memory
  surfaced_reactions        = visible trace intent
  memory_uptake_ops         = bounded write intent
  detour_need               = planning intent
        │
        ▼
Deterministic settlement / state_ops
  ├─ active_attention        hot near-term reading state
  ├─ concept_registry        source-grounded concept/object/definition layer
  ├─ thread_trace            cross-passage development line layer
  ├─ reaction_records        visible trace ledger
  ├─ unit_span_ledger        accepted-unit coverage ledger
  └─ read/settlement audit   diagnostic trace
        │
        ▼
Slow-cycle
  ├─ reflective_frames       promoted high-level frames
  ├─ knowledge_activations   prior/external warrant ledger
  ├─ reconsolidation_records later reinterpretation ledger
  └─ active_attention carry/cool/resolve
        │
        ▼
Bounded projections
  state_packet.v1 / source_ref_digest / planning-facing memory projection
        │
        ▼
Planning / Navigate / Read-context
  uses typed projections only; does not own durable memory
```

### 6.2 Required relationship clarifications

**active_attention vs concept_registry.**
`active_attention` is hot; `concept_registry` is stabilized object memory. A fresh definition may first appear in active_attention if it pulls on next reads, but once reusable and stable, it should be represented in concept_registry. If a concept remains locally urgent, both can exist with links, but their meanings differ.

**active_attention vs thread_trace.**
active_attention tracks what is currently pulling; thread_trace tracks a line of development across source spans. A thread may be dormant but still durable; an active item may be hot but not yet a thread.

**concept_registry vs thread_trace.**
Concepts answer “what is this object / distinction / model?” Threads answer “how is this line unfolding?” A named distinction belongs in concept_registry; its repeated use to structure the chapter may also generate thread_trace. The same source evidence may support both a concept entry and a thread entry, but the relationship should be expressed through lightweight links / shared `source_refs`, not by duplicating the same payload into both stores.

**thread_trace vs reflective_frames.**
Thread trace is ongoing and often unresolved. Reflective frames are slow-cycle promoted and should carry stronger source support and stability.

**reflective_frames vs slow-cycle.**
Reflective frames should normally be written only by slow-cycle. Read-path can generate lower-level evidence and candidates but not direct high-level frames.

**reaction_records vs semantic memory.**
Reaction_records preserve the visible reading process. They can provide evidence for later promotion, but they are not semantic memory until an explicit op or slow-cycle promotion creates concept/thread/reflective state.

**knowledge_activations vs concept_registry.**
Knowledge activation records a prior/external warrant. Concept registry records source-grounded book concepts. If source text itself introduces an external concept, it may enter concept_registry as source-given; the prior activation remains separate as warrant / recognition context.

**reconsolidation_records vs supersede / reflective_frames.**
Reconsolidation records a later reinterpretation event. Supersede changes validity / status of an earlier frame. Reflective_frames hold the resulting high-level memory; reconsolidation_records explain how a visible trace or prior thought evolved.

**source_ref_digest / state_packet vs durable stores.**
`source_ref_digest` and `state_packet.v1` are projections produced from durable stores. They are not storage truth and should not be used as reverse-authoritative state.

------

## 7. Read-path vs Slow-cycle Ontology Boundary

### 7.1 Read-path

Read-path may propose:

- `reading_impression`：temporary immediate reading impression；
- `surfaced_reactions`：visible reaction candidates anchored in current unit；
- `memory_uptake_ops`：bounded write intent targeting only `active_attention / concept_registry / thread_trace`；
- `detour_need`：planning intent, not navigation execution.

Read-path must not:

- write final persisted objects；
- rewrite whole stores；
- write `reflective_frames`；
- write `reaction_records` directly；
- write audit or evaluation artifacts；
- auto-promote reaction_records into semantic memory；
- auto-merge knowledge_activations into concept_registry；
- perform per-unit reflection；
- decide actual detour route；
- decide ordinary forward progression.

### 7.2 Settlement

Settlement is the authoritative boundary that turns intent into state. It must:

- resolve `end_anchor_text` to accepted `SourceSpan`；
- bind source quotes / source hints to inline `SourceRef`；
- normalize operations；
- check target store and payload shape；
- apply allowed state_ops；
- persist visible reactions through reaction builder；
- write unit ledger and audit；
- advance cursor；
- preserve failure / fallback / skipped-op diagnosis.

### 7.3 Slow-cycle

Slow-cycle may:

- cool or carry forward active_attention；
- generate promotion candidates；
- promote reflective frames；
- supersede old reflective items；
- reconsolidate later reinterpretations；
- update knowledge activation status；
- prepare cross-chapter carry-forward focus.

Slow-cycle must not:

- become a general memory manager agent；
- rewrite product goals or prompts；
- read future text；
- silently overwrite source-grounded memory；
- merge prior knowledge into book truth without source warrant；
- turn chapter summary into ungrounded high-level truth；
- own visible route disclosure policy.

### 7.4 Reaction / reflective / knowledge promotion boundary

A strong reaction is still a reaction until explicit memory operation or slow-cycle promotion creates a semantic item.

A reflective frame is valid only after slow-cycle promotion with supporting source set.

A knowledge activation can affect reading only as warrant-bearing prior context; it becomes source-grounded concept memory only if source text itself establishes it and settlement writes it as source-grounded concept state.

------

## 8. Memory–Planning Interface

Planning can use Memory only through **bounded, typed, source-ref-preserving projections**. Planning must not directly read full durable stores, audit dumps, or evaluation reports. This follows the P0 Charter and Planning Assessment boundary: Planning is reading-path planning / attention scheduling / navigation support, not a task-planning agent or memory owner.

### 8.1 Allowed Planning-facing memory projections

**active_attention digest.**
Used for hot reading pressure: current tensions, questions, active foci. Planning may use it to decide whether to continue mainline, defer detour, request look-back, or carry a concern forward. It must treat hypothesis-like content as provisional.

**concept digest.**
Used for compact access to relevant definitions, models, classifications, named distinctions. Planning may use it to decide whether current source depends on earlier concepts and whether active_recall is needed.

**thread digest.**
Used for continuity-bearing lines. Planning may use it to judge detour value, mainline continuity, whether a thread is resolved, and whether an earlier line should be recalled.

**reflective digest.**
Used for chapter/session carry-forward. Planning may use it to maintain macro continuity, not to generate a new global book plan.

**recent reaction digest.**
Can be used for visible continuity and callback awareness. It is not semantic truth. Planning may not treat “the reader once reacted this way” as “the book established this.”

**knowledge activation projection.**
May enter Planning rationale only with trigger SourceRef, warrant, status, and conflict information. It must remain labeled as prior/external activation, not source truth.

**source_ref digest.**
Used as evidence spine. Planning can cite refs to justify recall/look-back/detour decisions, but must not treat digest as exhaustive source truth.

### 8.2 Active recall / look-back / detour

- **active_recall is memory recovery.** It retrieves stored reading state that is not currently carried.
- **look_back is source calibration.** It returns earlier source excerpts to check what the source actually said.
- **detour is planning path deviation.** It changes the next source unit to be read, through the same Navigate → Read → settlement loop.

Planning must preserve this distinction. Active recall cannot replace source verification. Look-back cannot become semantic memory recall. Detour cannot become hidden supplemental fetch.

### 8.3 Visible route disclosure and audit boundaries

Visible route disclosure cannot automatically change memory state. It may point to memory or source evidence, but it does not create user route controls and cannot update semantic memory by itself.

Planning audit cannot automatically enter memory. A good or bad planning decision may become evaluation evidence or strategy discussion later, but not runtime reading memory unless a future procedural memory page explicitly authorizes it.

### Planning-facing summary for the next design page

Planning should see Memory as a set of bounded typed projections: hot active_attention, compact concepts, compact threads, promoted reflective frames, recent visible reactions, warranted knowledge activations, and source_ref evidence. Planning may retain route trace fields for future route disclosure, but route disclosure is not a memory store and not a planning control input. Planning must use memory projections only for reading path moves—continue, active recall, look-back, detour, defer—without owning durable memory, reading full stores, or converting visible/audit/evaluation artifacts into semantic state.

------

## 9. Accepted Constraints and Deferred Directions

This ontology accepts the following constraints.

**No new `structure_memory`.**
Structural retention is important, but existing `concept_registry / thread_trace / reflective_frames` already have places for definitions, classifications, stage models, roadmaps, and higher-order frames. Adding a vague structure store would blur boundaries instead of clarifying them.

**No vector DB as ontology premise.**
The current blocker is not lack of embedding recall; it is store identity, SourceRef binding, lifecycle, retrieval intent, and audit outcome. Vector search can be considered only after metadata/source_ref/link-based retrieval is proven insufficient and FVI does not increase.

**No graph DB as ontology premise.**
Concept/thread links, source_refs, and supersede chains can first be represented in JSON. Graph DB is infrastructure, not ontology.

**No Memory OS.**
Reading Companion is not a universal memory runtime. OS-style paging, account-wide personalization, agent-wide memory scheduler, or cross-agent memory platform would move the product away from source-grounded co-reading.

**No RL Memory-as-Action.**
The project lacks stable reward, repeated environment, and operation-level evaluation needed for policy-learned memory editing. It would reduce auditability.

**Read does not write final persisted object.**
Read proposes; deterministic settlement settles. This is a hard contract.

**No per-unit reflection.**
Reflection is slow-cycle promotion, not default read-path behavior.

**No automatic reaction promotion.**
Reaction_records are visible trace. Promotion requires explicit semantic operation or slow-cycle.

**No automatic knowledge activation merge.**
Prior knowledge activation remains warrant ledger unless source text establishes it and settlement writes source-grounded memory.

**Audit / evaluation evidence is not runtime memory.**
Diagnostic and benchmark artifacts can explain quality but cannot become prompt context by default.

**No complex memory manager agent.**
Current needs are contract-driven settlement, slow-cycle consolidation, and audit—not another autonomous manager.

------

## 10. What This Design Changes or Tightens

### 10.1 Preserved

This design preserves:

- `attentional_v2` as the current mechanism；
- paragraph-offset `SourceCursor / SourceSpan`；
- inline `SourceRef` evidence spine；
- `Navigate.choose_next_unit → Read → Reading Runner settlement`；
- `ReadResult` contract；
- existing primary stores；
- file-based JSON / JSONL runtime；
- bounded prompt-facing projection；
- chapter/session slow-cycle；
- Memory Quality / Spontaneous Callback / False Visible Integration as distinct evaluation surfaces.

### 10.2 Tightened

This design tightens:

- `memory_uptake_ops` are write intents, not final memory objects；
- prompt packet is projection, not state；
- visible reaction is visible trace, not semantic memory；
- prior knowledge activation is warrant, not source truth；
- audit/evaluation artifacts are diagnostic/eval evidence, not runtime memory；
- Planning can only consume bounded projections；
- lifecycle separates visibility from semantic validity；
- reflective memory is slow-cycle promoted, not per-unit.

### 10.3 Reinterpreted names

- `active_attention` is hot near-term reading state, not a general memory bucket.
- `concept_registry` is source-grounded concept/object/definition registry, not summary store.
- `thread_trace` is development-line memory, not concept list.
- `reflective_frames` is promoted higher-order memory, not every-unit reflection.
- `reaction_records` is visible trace ledger.
- `knowledge_activations` is prior/external knowledge warrant ledger.
- `reconsolidation_records` is reinterpretation event ledger.
- `state_packet.v1 / source_ref_digest` are bounded projections.

### 10.4 Deferred

Deferred to later pages:

- exact Formation pipeline and op schema details；
- store-specific lifecycle operation matrix；
- retrieval intent taxonomy and policy；
- per-op audit outcome schema；
- Memory Evaluation rubric；
- Planning Ontology；
- Navigation / Detour / Look-back / Visible Route Disclosure policy；
- Storage / infrastructure migration thresholds.

------

## 11. Optional Open Questions

None critical at this phase. Three non-blocking questions remain.

**Should concept_registry and thread_trace get explicit supersede chains?**
Current code supports statuses and reflective supersede, but concept/thread validity semantics need a Management / Evolution page. This does not block Planning Ontology because Planning can treat current status + SourceRef as sufficient for v0 projections.

**Should knowledge activations ever appear in default Planning projection?**
v0 says no by default; they require explicit warrant projection. The exact gate belongs to Planning Ontology / Visible Reading Route Surface Boundary. This does not block Planning because default exclusion is safe.

**How should manual correction be represented?**
Manual correction is allowed only as audited, source-ref-preserving exceptional repair. Exact fields belong to Audit / Storage design. It does not block ontology.

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

| Project evidence                                    | What it shows                                                | Design judgment supported                                    | Constraint status                       | Runtime-artifact validation gap                        |
| --------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------------------------- | ------------------------------------------------------ |
| `docs/product-overview.md`                          | Product is a curious, self-propelled co-reading mind; not summary engine; must remain text-grounded; prior knowledge cannot justify text-detached certainty. | Memory must be reading-state, not user profile / generic assistant memory; knowledge activation must be warrant-bound. | Stable product constraint.              | No runtime validation needed for product boundary.     |
| `docs/current-state.md`                             | Current direction is Memory Quality / Callback / FVI; paragraph-offset cursor and inline SourceRef cutover landed; diagnostic summary shows 59 read/settlement rows, 31 ops, SourceRef repair issues. | Ontology must preserve SourceRef-first evidence, distinguish architecture readiness from runtime quality, and avoid overclaiming. | Current status + documented diagnostic. | Actual JSONL rows not directly audited in this task.   |
| `docs/source-of-truth-map.md`                       | Repo-first source-of-truth discipline; mechanism internals belong in mechanism docs/state files. | JSON/JSONL runtime and docs-first boundaries are appropriate; artifacts must not be treated as chat memory. | Stable workspace governance.            | No row-level runtime validation.                       |
| `docs/backend-reading-mechanism.md`                 | `book_document.json` is shared parsed-book truth; paragraph layer stable substrate; current `attentional_v2` citations are inline SourceRef; no shared SourceRef registry. | Source corpus is not memory; SourceRef is evidence spine; mechanism-private ontology remains inside `attentional_v2`. | Stable shared boundary.                 | N/A.                                                   |
| `docs/backend-reading-mechanisms/README.md`         | `attentional_v2` is current default; `iterator_v1` fallback. | Ontology should evolve current mechanism, not greenfield.    | Stable catalog fact.                    | N/A.                                                   |
| `docs/backend-reading-mechanisms/attentional_v2.md` | Current loop, core primitives, Read contract, settlement boundary, survey boundary, detour same-loop rule, memory target stores. | Read proposes; settlement settles; Read only targets active_attention / concept_registry / thread_trace; visible reaction not semantic memory. | Strong contract-level evidence.         | Runtime behavior still requires artifact audit.        |
| `schemas.py`                                        | Defines SourceRef, stores, StateOperation, ReadUnitResult, knowledge activations, reaction/reconsolidation ledgers. | Existing store ontology should be tightened, not replaced.   | Code-level current fact.                | Schema existence does not prove runtime quality.       |
| `prompts.py`                                        | Read prompt forbids whole-object rewrites, limits memory ops to active_attention / concept_registry / thread_trace, states surfaced reaction not copied to semantic memory; Navigate / slow-cycle prompts set boundaries. | Store admission/rejection and read-path vs slow-cycle boundary. | Strong contract evidence.               | Prompt compliance requires audit rows.                 |
| `state_ops.py`                                      | Deterministic operation application, source_ref merging, active cooling/resolution, concept/thread upsert, reaction append, reflective supersede. | Lifecycle must separate visibility and validity; settlement is deterministic state mutator. | Code-level current behavior.            | Per-op outcome not yet fully surfaced in audit.        |
| `runner.py`                                         | Reading Runner loads/saves runtime bundle, owns continuity/detour integration, rejects legacy route state, imports settlement/projection/audit/storage seams. | Runner is orchestration / settlement owner, not LLM.         | Architecture-level evidence.            | Full settlement loop not independently traced here.    |
| `storage.py`                                        | Lists current JSON/JSONL artifacts and initializes runtime state. | File-based store ontology is current substrate; audit/ledger artifacts are non-memory diagnostics. | Current implementation fact.            | Actual artifact contents not audited.                  |
| `state_projection.py`                               | Builds bounded prompt packets from durable stores; active/concept/thread/reflective/source_ref/reaction digests. | Prompt-facing projection is not authoritative state; Planning should receive bounded projection. | Strong contract evidence.               | Does not prove projection is always optimal.           |
| `read_context.py`                                   | Distinguishes `active_recall` from `look_back`; active_recall retrieves memory state, look_back resolves source excerpts. | active_recall = memory recovery; look_back = source calibration. | Strong contract evidence.               | Trigger quality not validated here.                    |
| `slow_cycle.py`                                     | Handles reaction records, reflective promotion, reconsolidation, chapter consolidation, knowledge activation updates, carry-forward. | Slow-cycle owns high-level promotion / reconsolidation, not Read-path. | Strong implementation evidence.         | Runtime output quality not audited.                    |
| `observability.py`                                  | `record_read` and `record_settlement` write compact read/settlement audit with ops, deltas, source span, context, reactions. | Audit is diagnostic, not memory; per-op outcome is natural next tightening. | Current audit contract evidence.        | Actual JSONL rows inaccessible.                        |
| `backend-reader-evaluation.md`                      | Product-first evaluation; active long-span direction is Memory Quality / Spontaneous Callback / False Visible Integration; probe snapshots expose prompt-facing state only. | MQ / Callback / FVI must stay distinct and not become runtime memory. | Stable evaluation constitution.         | Benchmark authority still Phase-1, not fully promoted. |

------

## B. Assessment Basis

**From P0 Shared Charter.**
This design inherits the shared territory map, the boundary that source corpus / reading memory / planning state / audit trace / visible reaction / visible route disclosure / prior knowledge / evaluation evidence are distinct, the interface rule that Planning uses only bounded typed source-ref-preserving projections, and the principle **LLM proposes; deterministic runner settles**. It also inherits the active_recall / look-back / detour split and the rule that slow-cycle outputs must be separated into memory consolidation and macro carry-forward.

**From Memory Assessment.**
The main ontology judgments come from the Memory Assessment: current architecture is reasonably mature, but store ontology, `memory_uptake_ops` contract, lifecycle semantics, retrieval intent, and operation-level audit need tightening. It also identifies `reaction_records` as visible trace, `knowledge_activations` as warrant ledger, and warns against vector DB, graph DB, Memory OS, RL memory-as-action, per-unit reflection, `structure_memory`, and complex memory manager agent.

**From Planning Assessment.**
Planning Assessment informs only the Memory–Planning interface: Planning is source-grounded reading path planning / attention scheduling, not AutoGPT-style task planning; it should not directly read memory stores; active_recall, look-back, and detour have distinct roles; internal navigation and visible route disclosure must remain separate; planning state must not merge with memory state.

**Where this design makes project-specific judgments.**
The refusal to add `structure_memory`, to make vector/graph DB an ontology premise, and to keep JSON/JSONL first are project-specific judgments supported by current implementation and Simplicity and Universality. External work provides analogies and boundary warnings, not a direct mandate.

------

## C. External Rationale, as Filtered Through the Assessments

This phase did not redo broad external research. The sources below are those already filtered through the P0 / Memory / Planning assessments.

### Generative Agents

Original problem: sustain believable agents through memory stream, reflection, and planning.
Support: reflection should be second-order and thresholded, not per-unit.
Similarity: Reading Companion accumulates many local observations.
Difference: Generative Agents does not make source-grounded textual evidence first-class.
Localized borrowing: low-level reading state can accumulate first; reflective_frames belong to slow-cycle with SourceRefs.
Do not copy: social simulation reflection memory as book-grounded truth.
Support type: Direct / Analogical.
Stable URL: https://arxiv.org/abs/2304.03442

### Mem0

Original problem: production-ready long-term memory with add/search/update/delete operations.
Support: memory write should be operation-centric; `memory_uptake_ops` are bounded write intent, not final objects.
Similarity: both need IDs, metadata, update/delete, lifecycle.
Difference: Mem0 is general agent/user memory, not source-grounded reading.
Localized borrowing: extraction → conflict / merge → storage thinking; per-op audit.
Do not copy: vector-first user memory infrastructure as ontology.
Support type: Direct.
Stable URL: https://arxiv.org/abs/2504.19413 and https://docs.mem0.ai/core-concepts/memory-operations/add

### Zep

Original problem: temporal knowledge graph memory for changing facts.
Support: evidence layering, validity / invalidity, facts vs summaries vs observations.
Similarity: both need source-backed state and later correction.
Difference: Zep is graph-backed enterprise / conversation memory.
Localized borrowing: supersede / invalidate / warrant separation.
Do not copy: graph DB or user-summary context block as default.
Support type: Direct / Boundary.
Stable URL: https://arxiv.org/abs/2501.13956 and https://help.getzep.com/graph-overview

### MemGPT / Letta

Original problem: context-window scarcity through core / archival memory and memory blocks.
Support: authoritative state and prompt-facing projection must be separated; each store needs a role/limit contract.
Similarity: both need bounded context assembly.
Difference: Letta focuses on general stateful agents, persona/user memory.
Localized borrowing: lightweight block contract discipline.
Do not copy: OS-style paging or persona/human blocks.
Support type: Boundary / Direct.
Stable URL: https://arxiv.org/abs/2310.08560, https://docs.letta.com/guides/core-concepts/memory/memory-blocks

### LangGraph Memory / LangMem

Original problem: framework-level semantic / episodic / procedural memory, hot-path vs background writes.
Support: type hygiene and write-timing separation.
Similarity: Read-path vs slow-cycle split.
Difference: general framework, not source-book reading.
Localized borrowing: semantic vs episodic/trace distinction; background consolidation idea.
Do not copy: procedural prompt refinement as current main mechanism.
Support type: Direct / Boundary.
Stable URL: https://docs.langchain.com/oss/python/concepts/memory, https://github.com/langchain-ai/langmem

### LongMemEval / HaluMem

Original problem: evaluate long-term memory and memory-induced hallucinations with stage-level diagnosis.
Support: Memory Quality must eventually be stage-aware; audit needs per-op outcome.
Similarity: both need to locate failures across formation, retrieval, utilization, update.
Difference: benchmarks are chat/agent memory oriented, not source-span reading.
Localized borrowing: stage-aware diagnosis, not tasks wholesale.
Do not copy: final QA correctness as primary product metric.
Support type: Direct.
Stable URL: https://arxiv.org/abs/2410.10813, https://arxiv.org/abs/2511.03506

### CAM / ComoRAG

Original problem: reading-specific constructivist memory and long narrative reasoning.
Support: Reading Companion memory should be reading-specific and can support impasse-triggered recall.
Similarity: long text understanding and narrative continuity.
Difference: research prototypes / RAG systems, not current product runtime.
Localized borrowing: reading-specific organization and targeted recall idea.
Do not copy: incremental clustering or iterative RAG loop as default.
Support type: Analogical / Direct.
Stable URL: https://arxiv.org/abs/2510.05520, https://arxiv.org/abs/2508.10419

### GraphRAG / RAPTOR / HippoRAG

Original problem: global sensemaking and multi-hop retrieval over corpora.
Support: high-level frames and links can be useful; local/global retrieval differs.
Similarity: reading may require concept/thread aggregation.
Difference: corpus indexing, not run-internal reading memory.
Localized borrowing: lightweight links, source-ref-preserving high-level frames.
Do not copy: graph/tree infrastructure as ontology premise.
Support type: Boundary / Analogical.
Stable URL: https://arxiv.org/abs/2404.16130, https://arxiv.org/abs/2401.18059, https://arxiv.org/abs/2405.14831

### ReAct / Plan-and-Solve / ReWOO / Reflexion

Original problem: agent planning, observation correction, planner-executor separation, episode reflection.
Support: detour/source loops should be bounded; explicit planning only at boundaries; reflection belongs between episodes, not every step.
Similarity: Reading Companion has local uncertainty and slow-cycle boundaries.
Difference: reading is source-order, not external task execution.
Localized borrowing: local observation correction, boundary planning, slow-cycle reflection separation.
Do not copy: every read unit as ReAct loop or global planner-executor architecture.
Support type: Direct / Boundary / Analogical.
Stable URLs: https://arxiv.org/abs/2210.03629, https://aclanthology.org/2023.acl-long.147/, https://arxiv.org/abs/2305.18323, https://arxiv.org/abs/2303.11366

### HTN / Options / MAXQ

Original problem: hierarchical control and temporal abstraction.
Support: micro read navigation, meso detour, macro slow-cycle can be separated without complex planner.
Similarity: multi-timescale decisions.
Difference: formal planning/RL, not reading memory.
Localized borrowing: hierarchy language only.
Do not copy: formal HTN/RL machinery.
Support type: Analogical.
Stable URLs: http://hdl.handle.net/1903/5810, https://doi.org/10.1016/S0004-3702(99)00052-1, https://doi.org/10.1613/jair.639

### Information Foraging / Rereading / Metacomprehension / Adaptive Navigation

Original problem: when to move through information, reread, calibrate understanding, and support user navigation.
Support: look-back is calibration; detour value must weigh value/cost/scent; route disclosure is an optional display surface, not route control.
Similarity: deciding next reading move and when to revisit source.
Difference: human reading / HCI evidence, not LLM memory ontology.
Localized borrowing: value-cost-scent and calibration distinctions.
Do not copy: free exploratory search or strong learner model.
Support type: Direct / Analogical / Boundary.
Stable URLs: https://doi.org/10.1037/0033-295X.106.4.643, https://doi.org/10.3758/BF03209348, https://doi.org/10.1111/j.1467-8721.2007.00509.x, https://doi.org/10.1111/1467-8535.00345

------

## D. Simplicity and Universality Check

This design prioritizes tightening existing stores rather than adding stores. It keeps `active_attention / concept_registry / thread_trace / reflective_frames / reaction_records / knowledge_activations / reconsolidation_records`, but assigns sharper roles.

It avoids turning source corpus into memory. `book_document.json` remains substrate.

It avoids turning visible trace into semantic memory. `reaction_records` remains visible trace unless explicitly promoted.

It avoids turning prior knowledge into source truth. `knowledge_activations` remains warrant ledger.

It avoids treating prompt packet as authoritative memory. `state_packet.v1` remains projection.

It avoids vector DB, graph DB, Memory OS, RL memory editing, and complex memory manager agent as ontology premises.

It preserves SourceRef-first auditability. Every semantic memory store needs source_refs or explicit warrant.

It gives Planning enough interface—active, concept, thread, reflective, reaction, knowledge, source_ref digests—without letting Planning own memory.

Remaining complexity risks:

- `active_attention` can still become a junk drawer if admission rules are loose;
- `reaction_records` can still tempt automatic semantic promotion;
- `knowledge_activations` can still pollute book-grounded memory if warrant is not visible;
- slow-cycle can drift into hidden macro-planner if outputs are not separated;
- evaluation artifacts can accidentally leak into prompt if report/probe boundaries are not enforced.

------

## E. Source Usage List

| External source             | Authors / Organization                  | Year        | Stable URL                                                   | Used for                                                     | Support type          |
| --------------------------- | --------------------------------------- | ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------- |
| Generative Agents           | Joon Sung Park et al.                   | 2023        | https://arxiv.org/abs/2304.03442                             | Observation → reflection, slow-cycle boundary                | Direct / Analogical   |
| Mem0 paper                  | Prateek Chhikara et al.                 | 2025        | https://arxiv.org/abs/2504.19413                             | Operation-centric memory pipeline                            | Direct                |
| Mem0 memory operations docs | Mem0                                    | 2025–2026   | https://docs.mem0.ai/core-concepts/memory-operations/add     | Add / update / delete contract                               | Direct                |
| Zep temporal memory paper   | Preston Rasmussen et al.                | 2025        | https://arxiv.org/abs/2501.13956                             | Temporal validity, evidence-backed memory                    | Direct / Boundary     |
| Zep graph docs              | Zep                                     | 2025–2026   | https://help.getzep.com/graph-overview                       | Episodes / facts / observations layering                     | Direct                |
| MemGPT                      | Charles Packer et al.                   | 2023        | https://arxiv.org/abs/2310.08560                             | Core vs archival boundary                                    | Boundary              |
| Letta Memory Blocks         | Letta                                   | 2025–2026   | https://docs.letta.com/guides/core-concepts/memory/memory-blocks | Store/block contract discipline                              | Direct                |
| LangGraph Memory Concepts   | LangChain                               | 2025–2026   | https://docs.langchain.com/oss/python/concepts/memory        | Semantic / episodic / procedural split; hot/background writes | Direct / Boundary     |
| LangMem                     | LangChain                               | 2025–2026   | https://github.com/langchain-ai/langmem                      | Background consolidation pattern                             | Direct / Boundary     |
| LongMemEval                 | Di Wu et al.                            | 2024        | https://arxiv.org/abs/2410.10813                             | Stage-aware memory evaluation                                | Direct                |
| HaluMem                     | Ding Chen et al.                        | 2025        | https://arxiv.org/abs/2511.03506                             | Operation-level memory hallucination                         | Direct                |
| CAM                         | Rui Li et al.                           | 2025        | https://arxiv.org/abs/2510.05520                             | Reading-specific memory organization                         | Direct / Analogical   |
| ComoRAG                     | Juyuan Wang et al.                      | 2025        | https://arxiv.org/abs/2508.10419                             | Impasse-triggered narrative memory retrieval                 | Analogical            |
| GraphRAG                    | Darren Edge et al. / Microsoft Research | 2024        | https://arxiv.org/abs/2404.16130                             | Local/global retrieval and global sensemaking boundary       | Boundary / Analogical |
| RAPTOR                      | Parth Sarthi et al.                     | 2024        | https://arxiv.org/abs/2401.18059                             | Multi-granularity frame as retrieval entry                   | Analogical            |
| HippoRAG                    | Bernal Jiménez Gutiérrez et al.         | 2024        | https://arxiv.org/abs/2405.14831                             | Lightweight links as future relation retrieval analogy       | Boundary / Analogical |
| ReAct                       | Shunyu Yao et al.                       | 2022 / 2023 | https://arxiv.org/abs/2210.03629                             | Bounded observation-grounded detour loops                    | Direct / Boundary     |
| Plan-and-Solve              | Lei Wang et al.                         | 2023        | https://aclanthology.org/2023.acl-long.147/                  | Boundary-level planning only                                 | Boundary              |
| ReWOO                       | Binfeng Xu et al.                       | 2023        | https://arxiv.org/abs/2305.18323                             | Local evidence-gathering sketch; not full planner            | Analogical            |
| Reflexion                   | Noah Shinn et al.                       | 2023        | https://arxiv.org/abs/2303.11366                             | Episode-boundary reflection and strategy/content separation  | Boundary              |
| HTN Planning                | Kutluhan Erol                           | 1996        | http://hdl.handle.net/1903/5810                              | Micro / meso / macro layering analogy                        | Analogical            |
| Options Framework           | Sutton, Precup, Singh                   | 1999        | https://doi.org/10.1016/S0004-3702(99)00052-1                | Detour as temporally extended option analogy                 | Analogical            |
| MAXQ                        | Thomas Dietterich                       | 2000        | https://doi.org/10.1613/jair.639                             | Controller / executor separation analogy                     | Analogical            |
| Information Foraging        | Peter Pirolli, Stuart Card              | 1999        | https://doi.org/10.1037/0033-295X.106.4.643                  | Mainline vs detour value/cost/scent                          | Direct / Analogical   |
| The rereading effect        | Rawson, Dunlosky, Thiede                | 2000        | https://doi.org/10.3758/BF03209348                           | Look-back as calibration                                     | Direct                |
| Metacomprehension           | Dunlosky, Lipko                         | 2007        | https://doi.org/10.1111/j.1467-8721.2007.00509.x             | Calibration need and uncertainty                             | Direct                |
| Adaptive Navigation Support | Peter Brusilovsky                       | 2003        | https://doi.org/10.1111/1467-8535.00345                      | Route disclosure as optional navigation scaffold             | Direct / Boundary     |
| Learner Agency review       | Michelle Deschênes                      | 2020        | https://doi.org/10.1186/s41239-020-00219-w                   | Route disclosure should preserve agency                      | Boundary              |
