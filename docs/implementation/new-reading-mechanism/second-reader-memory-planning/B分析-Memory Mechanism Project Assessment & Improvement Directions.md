# Memory Mechanism Project Assessment & Improvement Directions

## 1. Executive Assessment

Reading Companion 当前的 `attentional_v2` Memory 机制，已经不是“前文摘要 + prompt 拼接”的早期方案。它在架构层已经进入了一个较成熟的、面向阅读任务的 application memory 阶段：项目明确不是摘要器，也不是通用服务型聊天助手，而是一个 text-grounded、legible、具有自驱好奇心的共读心智；产品价值来自“AI thinking while reading”的可见阅读过程，而不是读后报告。

当前机制相对主流 Agent Memory 工作，最做对的是三件事。第一，它没有把 source corpus 当作 memory：共享 parsed-book truth 是 `public/book_document.json`，而 `attentional_v2` 自己使用 paragraph-offset cursor 和 inline `SourceRef`；平台层没有共享 Anchor Bank 或 SourceRef registry。 第二，它把 `Read` 与 deterministic settlement 分开：`Read` 产生 `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`，Reading Runner 再应用 memory uptake、持久化 reactions、写 audit、关闭 unit、推进 cursor。 第三，它优先使用 file-based JSON / JSONL runtime artifacts，而不是过早引入 vector DB 或 graph DB；`storage.py` 明确列出 `active_attention.json`、`concept_registry.json`、`thread_trace.json`、`reflective_frames.json`、`knowledge_activations.json`、`reaction_records.json`、`unit_span_ledger.jsonl`、`read_audit.jsonl`、`settlement_audit.jsonl` 等机制私有文件。

最大的短板不是缺少复杂基础设施，而是 **contract-level semantics 还不够稳定**。当前已经有 `active_attention / concept_registry / thread_trace / reflective_frames / knowledge_activations / reaction_records` 等 store，也有 `append / update / close / link / create / cool / drop / promote / supersede / reactivate / resolve` 等 operation vocabulary。 但这些 store 的身份、允许写入内容、生命周期语义、prompt 可见性、audit outcome、以及 retrieval intent 还需要进一步收紧。否则后续 Memory Ontology、Formation、Management、Retrieval、Evaluation、Audit、Storage 设计都会不断互相拉扯。

必须分三层判断当前成熟度：

**Architecture-level maturity：中高。** 当前架构已经在主流 Agent Memory 工作中处在合理位置：它选择 source-grounded textual memory、operation intent、deterministic settlement、slow-cycle consolidation、compact audit，而不是模型参数记忆、用户画像 memory、Memory OS、或 graph/vector infra-first。

**Contract-level maturity：中等。** `ReadResult` 的最小契约已经很清楚；SourceRef、runtime stores、state packet、audit streams 也已经落地。但 `memory_uptake_ops` 仍需要被正式定义为 bounded write intent，而不是 final persisted object；lifecycle operations 也需要按 store 明确语义。

**Runtime-quality maturity：低到中。** 仓库当前状态记录了一个 no-judge settlement-audit diagnostic：`59` 条 read-audit、`59` 条 settlement-audit、`29 / 59` 个 read units 产生 memory ops、总计 `31` 个 ops，分布到 `active_attention = 12`、`concept_registry = 18`、`thread_trace = 1`；并且诊断发现并修复了 Read output 与 durable store field-shape 不对齐、SourceRef 在 carry-forward 中可能丢失的问题。 但本轮没有直接逐条读取 runtime artifacts，如 `read_audit.jsonl`、`settlement_audit.jsonl`、`active_attention.json`、`concept_registry.json`、`thread_trace.json` 等。因此当前评价主要是架构与契约层评价，加上 repo 文档中的诊断摘要；不是充分独立的 runtime-quality validation。

当前最不应该继续复杂化的是：立即引入 vector DB、graph DB、Memory OS、RL-based Memory-as-Action、复杂 memory manager agent、per-unit reflection、full snapshot per unit audit、或新增一个笼统的 `structure_memory` store。当前最应该做的是把已经存在的好骨架收紧：明确 ontology、稳定 write contract、定义 lifecycle、设计 intent-aware retrieval、建立 operation-level audit 与 stage-aware evaluation。

后续设计工作应围绕以下模块展开：Memory Ontology、Memory Formation、Memory Management / Evolution、Memory Retrieval / Utilization、Memory Evaluation、Audit / Observability、Storage / Infrastructure。核心不是“做更大”，而是“让现有 reading memory 变得可解释、可更新、可检索、可评估、可审计”。

------

## 2. Current Project Level Assessment

### 2.1 What is already strong

当前最强的一点是 **source-grounded memory 边界已经被放在正确位置**。项目的共享机制文档明确说，`public/book_document.json` 是唯一共享 parsed-book truth，paragraph layer 是稳定 source substrate，`attentional_v2` 当前主线阅读使用 paragraph + char offset source cursor，而当前 source citations 使用 inline paragraph-offset `SourceRef`，没有平台级共享 Anchor Bank 或 SourceRef registry。 这恰好避免了 Agent Memory 中常见的混淆：把 source corpus、retrieval corpus、reading observations、durable memory、audit trace 全部叫作 memory。
外部工作中，Zep 的 graph / facts / observations docs 对这个方向支持很强：它把 episodes、entities、facts、observations 分层，避免把原始交互、事实、摘要、高层模式混在一起。Reading Companion 的相似点在于也需要区分 source substrate、reading observation、durable state、audit；差异在于 Zep 是 temporal knowledge graph for agent memory，而 Reading Companion 是 source-grounded reading state，不应照搬 graph DB，只应借它的分层与时态效力思想。

第二，**SourceRef / evidence spine 是当前机制最重要的质量资产**。代码中 `SourceRef` 被定义为 inline paragraph-offset source citation，包含 `source_span_id`、`source_span`、`quote`、`role`、`resolution`，并明确不是 registry entry。 `SourceRef` 不是一个装饰字段，而是 Memory Formation、Retrieval、Evaluation、Audit 的共同骨架。
这与 Mem0 的 metadata / timestamps / memory item framing，以及 Zep 的 evidence-backed facts / observations 接近。不同点是：Mem0/Zep 多面向 conversation/user facts，而 Reading Companion 的证据必须来自 accepted source units。因此本地化借鉴应是 source-ref-preserving update、source-ref-preserving supersede、source-ref-grounded recall，而不是通用 user memory item。

第三，**`Read -> settlement` 的分工是当前架构里的高价值设计**。`attentional_v2` 文档明确：`Read` 是 reader-first 的正式 unit read call，直接产生 `reading_impression`、`surfaced_reactions`、`memory_uptake_ops` 和可选 `detour_need`；Reading Runner post-read settlement 则确定性应用 memory uptake、持久化 reactions、写 audit、记录 unit span、推进 cursor。 这使 LLM 不直接重写完整 state，而是提出 bounded memory intent。
Mem0 的 add / update / delete operation docs 支持这个方向：成熟 memory write path 不是“LLM 生成一个最终对象”，而是 extraction、conflict handling、storage、update/delete 的可控 pipeline。LangGraph Memory Concepts 也把 hot-path write 与 background write 作为一等设计维度。Reading Companion 的本地化更保守：`Read` 表达“什么自然需要留存”，settlement 负责规范化、合并、落库与审计。

第四，**store 分层已经有雏形，而不是单一 summary store**。当前 schema 已经区分 `ActiveAttention`、`ConceptRegistryState`、`ThreadTraceState`、`ReflectiveFramesState`、`KnowledgeActivationsState`、`ReactionRecordsState`、`ReconsolidationRecordsState`。 这与 LangGraph 的 semantic / episodic / procedural taxonomy、Zep 的 facts / summaries / observations 分层、Letta 的 core / archival memory 边界都相近。
差异在于，Reading Companion 的 store 不应围绕用户 persona，也不应围绕通用 assistant memory，而应围绕阅读任务：hot attention、source-grounded concepts、thread continuity、slow-cycle reflective frames、visible reaction trace、prior knowledge warrant ledger。

第五，**file-based JSON / JSONL runtime 当前仍是正确选择**。`storage.py` 的 artifact map 说明当前 runtime artifacts 完全可以承载机制私有 state、audit、checkpoint、probe export。 这与项目 repo-first 事实治理一致：Source of Truth Map 明确说 workspace 是 repo-first，Chat、Notion 等可以孵化，但不是 authoritative current project state。
外部应用层证据中，Claude Code 的 `CLAUDE.md`、Gemini CLI 的 `GEMINI.md`、OpenClaw / Clawdbot 的 `MEMORY.md` 与 daily logs、Hermes 的 hot memory file + cold archive 都说明：应用层 memory 不一定要从数据库开始；可见、可编辑、可导出、可审计的文件状态在早期反而更可靠。Reading Companion 的 JSON/JSONL 比 Markdown 更适合结构化 SourceRef 和 audit。

第六，**audit / evaluation 已经抓住了正确问题**。`observability.py` 的 `record_read` 记录 carry-forward refs、context request、supplemental refs、stop reason、budget exhaustion、reading impression、surfaced reactions、memory uptake ops 与 target-store distribution；`record_settlement` 记录 memory op count、target-store distribution、active_attention / concept_registry / thread_trace / reaction_records 的 compact ID deltas。 `backend-reader-evaluation.md` 已经把当前长跨度方向定义为 `Memory Quality / Spontaneous Callback / False Visible Integration`，并要求 Memory Quality 判断 retained state 的重要性、主线性、组织性与 fidelity；FVI 则审计 overclaim、hard-linking、theme-only similarity、memory drift。
这与 LongMemEval 的 stage decomposition、HaluMem 的 operation-level hallucination、LoCoMo 的 temporal continuity 风险相近。Reading Companion 的本地化更贴近阅读：它不是只问“用户信息是否被记住”，而是问“阅读中形成的状态是否 faithful、可继续使用、不会污染后续理解”。

### 2.2 What is weak, underspecified, or risky

第一，**store ontology 边界仍不够清楚**。`active_attention`、`concept_registry`、`thread_trace`、`reflective_frames`、`reaction_records`、`knowledge_activations` 都存在，但它们的身份 contract 需要更硬。比如：`reaction_records` 是 visible trace，还是可自动进入 semantic memory？`knowledge_activations` 是 prior knowledge warrant ledger，还是可自动合并到 concept registry？`reflective_frames` 与 `thread_trace` 的边界是什么？这不是实现 bug，而是 ontology 缺口。
Zep 的 facts / observations / episodes 分层提醒我们：事实、观察、高层 pattern 与证据来源必须分开。LangGraph 的 semantic / episodic / procedural split 也提醒我们：事实性状态、经验轨迹、策略性知识不能混写。Reading Companion 应本地化成自己的 store contract，而不是照搬这些名字。

第二，**`memory_uptake_ops` 的 contract 还不够稳定**。当前 `StateOperationType` 已经覆盖 `append / update / close / link / create / cool / drop / promote / supersede / reactivate / resolve`。 `state_ops.py` 中 active_attention 的 `cool` 会设置 cooling，concept/thread 的 `append/create/link` 会归一化为 update，`close` 会归一化为 resolve，`drop` 会移除条目。 这些实现很实用，但还不是完整设计 contract。
Mem0 的 update/delete docs 支持把 update/delete 作为一等操作；HaluMem 提醒 hallucination 可以发生在 extraction、updating、QA 任一阶段。Reading Companion 如果不定义每个 op 在每个 store 中的语义，就无法判断一次失败是 Read 抽取错、payload shape 错、settlement 归一化错、source_ref 绑定错，还是 retrieval/utilization 错。

第三，**memory lifecycle 仍像词汇表，而不是成熟演化机制**。阅读中常见情况是“后文修正前文”：早先的 hypothesis 后来被确认为 definition，某个 thread 后来被解释为 contrast，某个 prior knowledge activation 后来被 source 否定，某个 reflective frame 需要被替换。当前 reflective item 已有 `superseded_by_item_id`，`supersede_reflective_item` 会把旧 item 标记为 superseded 而不是直接改写 statement。 这是正确方向，但应扩展为整体 lifecycle contract。
Zep 的 `valid_at / invalid_at` 提醒我们：旧理解很多时候不是“应该删除”，而是“在早先 source-so-far 下有效，后来失效或被修正”。MemoryBank 的 forgetting / reinforcement 也更适合本地化为 visibility decay / reactivation，而不是事实抹除。

第四，**retrieval 仍偏 fixed packet，而不是 intent-aware retrieval**。`state_projection.py` 当前会生成 bounded `state_packet.v1`，包括 active_attention digest、concept digest、thread digest、reflective digest、source_ref digest、recent reactions 等。 `read_context.py` 的 `active_recall` 可以从 concept/thread/reactions 中补充未 carry 的内容，`look_back` 可以返回 bounded earlier source excerpts。 这是好雏形，但还不是成熟 retrieval policy。
Generative Agents 的 recency / relevance / importance retrieval、MemGuide 的 intent-driven memory selection、GraphRAG 的 local/global/DRIFT distinction、ComoRAG 的 impasse-triggered probing 都说明：retrieval 需要知道“为什么此刻取回”。Reading Companion 当前已经有 active_recall / look_back / detour 的雏形，下一步不是上 vector DB，而是明确 retrieval intent taxonomy 与 utilization trace。

第五，**Memory Quality 方向正确，但仍需拆成可诊断维度**。当前 MQ 已经关注 salience、mainline fidelity、organization、fidelity，并加入 structural-signal supplement：当 source-so-far 引入 stage model、classification、core definition、roadmap、named distinction 时，judge 要检查 snapshot 是否保留这些结构。 这对阅读非常关键。
但 holistic MQ 分数还不能定位失败层。LongMemEval 把长期记忆评估拆成 indexing / retrieval / reading，HaluMem 拆 extraction / updating / QA，StructMemEval 关注 memory structure itself。Reading Companion 未来应保留 holistic MQ，但同时拆出 formation、settlement、retrieval、utilization、drift/pollution、structural retention 等维度。

第六，**audit 缺少 per-op outcome / failure reason**。当前 `settlement_audit` 有 compact ID delta，这比 full snapshot 好。 但它还没有充分表达每个 `memory_uptake_op` 的 outcome：accepted、normalized、merged、skipped、failed、deferred、superseded？为什么失败？当前诊断已经出现过 Read output payload shape 与 state_ops persisted field shape 不对齐。 这说明 per-op outcome 是设计缺口，不只是调试细节。

第七，**runtime quality 仍不能过度声称成熟**。当前状态记录显示 Phase-1 diagnostic、SourceRef smoke、F4A quality audit 等已经完成或进行中，但本轮没有逐条读取实际 runtime artifacts。尤其当前文档也记录了 F4A 中 detour / prior_link / outside_link / search_intent 等部分能力尚未充分出现或验证。 因此不能把 architecture-level readiness 等同于 runtime-quality maturity。

### 2.3 What is currently over-risky or not worth doing

立即引入 **vector DB** 很诱人，因为它看起来能解决 recall。但当前问题不是“没有相似度检索”，而是 store ontology、operation semantics、source_ref binding、retrieval intent、per-op audit 尚未稳定。Mem0 的 search filters / reranking 可以支持未来检索，但本地化优先级应是 metadata filters、source refs、status、chapter scope、lightweight links，而不是向量基础设施。

立即引入 **graph DB** 也很诱人，因为 Zep、GraphRAG、HippoRAG 都证明图结构对关系和全局 sensemaking 有价值。但它们的原场景分别是 temporal KG、corpus-level QFS、多跳 QA；Reading Companion 当前是 inside-run source-grounded reading state。应先在 JSON store 中做 `linked_concept_keys`、`linked_thread_keys`、source_refs、supersede chains，再用小窗口验证图关系是否真成瓶颈。

新增 **`structure_memory`** 现在不值得。结构保留确实重要，但当前已有 `concept_registry / thread_trace / reflective_frames`。问题不是缺一个叫 structure 的 store，而是这些 store 如何承载 stage model、classification、definition、roadmap、named distinction。CAM 支持 reading-specific structured memory，但本地化应是增强现有 store contract，而不是新增模糊层。

引入 **Memory OS / MemOS / MemGPT-style OS paging** 当前过重。MemGPT 和 MemOS 的价值主要是边界参照：它们说明 memory 可以被做成系统资源调度问题。但 Reading Companion 不是 memory OS，也不是通用 agent platform。当前应拒绝 OS 化。

引入 **RL-based Memory-as-Action** 当前也不适合。Memory-as-Action 把 working memory editing 作为 policy action，在长周期 agent 任务中有研究价值，但 Reading Companion 当前缺少稳定 reward、足够重复环境和 operation-level evaluation，会损害可解释性和审计性。

让 **Read 直接写 final persisted object** 不应做。当前 `Read -> memory_uptake_ops -> deterministic settlement` 是正确边界。Mem0 与 HaluMem 都支持保留 operation pipeline，而不是让 LLM 直接改写最终 state。

**每个 unit 都做 reflection** 不应做。Generative Agents 的 reflection 是累积 observation 后的 second-order operation，不是每步都做。Reading Companion 当前已有 slow-cycle consolidation，应继续节流。

**full snapshot per unit audit** 不应做。当前 compact audit + ID deltas 是更好方向。应增加 per-op outcome，而不是每步保存全量 state。

**procedural memory / prompt refinement** 当前不应作为主机制。LangGraph / LangMem 把 prompt refinement 视作 procedural memory，但 Reading Companion 当前优先对象是 source-grounded reading memory。自改 prompt 容易污染内容层，且缺少评估闭环。

**complex memory manager agent** 应延后。当前 deterministic settlement + chapter slow-cycle 已足以承载受控 memory management。复杂 manager agent 会把 contract-driven 机制变成 behavior-driven 机制，增加不可诊断性。

------

## 3. Layered Improvement Analysis

## 3.1 Memory Ontology and Boundaries

### Current state and gap

当前项目已经具备多层 memory territory：`active_attention` 是热状态，`concept_registry` 是 durable concept/object layer，`thread_trace` 是 line/thread layer，`reflective_frames` 是慢周期高层 frame，`reaction_records` 是 visible reaction history，`knowledge_activations` 是 prior knowledge activation ledger，`reconsolidation_records` 是后续 reinterpretation ledger。代码中这些 schema 都已存在，并且多数具备 `source_refs` 或可追溯字段。

主要 gap 是：这些 store 已经实现，但还没有被充分定义为 ontology contract。尤其容易混淆的是：source corpus、reading memory、visible trace、prior knowledge warrant、audit ledger。若不先明确这些边界，后续 formation 会不知道写哪里，retrieval 会不知道取什么，evaluation 会不知道评估哪一层。

### Improvement directions

第一，后续 Memory Ontology 必须把 **source corpus / reading memory / audit** 明确分开。当前共享机制文档已经给了正确起点：`book_document.json` 是 source truth，机制可以选择自己的 cursor semantics，`attentional_v2` 的 source citations 是 inline paragraph-offset SourceRef。 因此，source corpus 不是 memory；unit_span_ledger 是 coverage/audit ledger，不是 semantic memory；reaction_records 是 visible trace，不自动等于 durable semantic memory；reading memory 是从 accepted source units 中形成、未来阅读可能会用到的 source-grounded state。

Zep 的 episodes / entities / facts / observations 是直接支持：它的价值不在于 graph DB，而在于把原始 episode、事实、实体、高层 observation 分开。CAM 的 constructivist reading memory 也支持 Reading Companion 不应复制 chatbot memory，而应围绕阅读理解逐步形成 schemata。但 CAM 是 frontier prototype，本地化时只能借 reading-specific organization 原则，不能直接搬 incremental clustering。

第二，当前 store 应保留，但必须明确身份：

`active_attention` 应定义为 hot, prompt-facing, near-term reading state。它可以包含 hypothesis-like material，但不是 durable semantic truth。它应有 cooling / resolve / reactivate / drop-like visibility lifecycle。

`concept_registry` 应定义为 source-grounded concept/object/definition registry，适合承载 stage model、classification、definition、named distinction、关键对象。它不应变成 generic summary bucket。

`thread_trace` 应定义为跨 unit / 跨章节延续的 line、motif、argument、contrast、question trace。它不是 concept dictionary，而是 continuity-bearing relation/thread store。

`reflective_frames` 应定义为 slow-cycle promoted higher-order memory，包括 chapter_understandings、book_level_frames、durable_definitions、stabilized_motifs、resolved_questions_of_record。它应保留 supporting source set，并支持 supersede。

`reaction_records` 应定义为 visible trace / reading process history。它可以被 recall，用作 callback audit evidence，但不自动提升为 semantic memory。

`knowledge_activations` 应定义为 prior/external knowledge warrant ledger。代码中它包含 `trigger_source_ref`、`source_candidate`、`recognition_confidence`、`reading_warrant`、`evidence_hints`、`conflict_source_refs`、`status` 等字段。 这更像“我为什么暂时允许某个先验知识参与阅读”的 ledger，而不是 book-grounded semantic truth。

Letta Memory Blocks 的 `label / description / value / limit` contract 很适合本地化到这里：Reading Companion 不需要 Letta 的 persona/human memory blocks，但需要每个 store 都有 label、description、allowed writes、visibility、limit、audit role。LangGraph 的 semantic / episodic / procedural split 也能作为抽象卫生：concept/thread/reflective 偏 semantic，reaction_records / unit_span_ledger 偏 episodic/audit，reader_policy / prompt refinement 才是 procedural，而且 procedural 当前应延后。

第三，必须防止 chatbot/user-profile memory 迁移进 Reading Companion。MemoryBank 的 personality synthesis 对 companion chat 有价值，但对 Reading Companion 是负迁移。项目产品文档明确说 broad prior knowledge 是价值来源，但不能 justify text-detached certainty or generic cleverness。 因此，用户画像、偏好、人格、聊天 history reference 不应成为当前主机制。这个判断主要是 project-specific judgment，外部工作只提供 boundary / negative support。

第四，`reaction_records` 和 `knowledge_activations` 不应自动合并进 semantic stores。Zep 的 observations 是 evidence-backed durable pattern，会随新证据 merge/supersede；Reading Companion 若要把 reaction 或 prior activation 提升为 durable memory，也必须通过 explicit memory operation 或 slow-cycle promotion，并保留 supporting source refs。否则很容易把“我想到过”误当“书里建立了”。

### Design implications

- Memory Ontology 页面应先定义 source corpus、reading memory、visible trace、audit ledger、prior knowledge warrant ledger。
- 当前不应新增 store；应先给现有 stores 写 role、allowed writers、allowed operations、visibility、evaluation use。
- `reaction_records` 默认是 visible trace，不是 semantic memory。
- `knowledge_activations` 默认是 warrant ledger，不是 concept registry。
- Store contract 可借 Letta block contract，但必须 source-ref-first。
- 用户画像 / persona memory / account-wide personalization 当前应明确排除。

------

## 3.2 Memory Formation and Write Contract

### Current state and gap

当前 `Read` 的 naturalized contract 是强项：`reading_impression` 是当下读完一个 unit 的自然印象，不是 durable memory；`surfaced_reactions` 是 visible reaction；durable memory 只通过 `memory_uptake_ops` 进入既有 primary state layers；visible reaction 不会自动复制进 concept 或 thread memory。

gap 在于：`memory_uptake_ops` 虽然已经存在，但需要被正式定义为 **bounded memory write intent**。它不应是 final persisted object，也不应是 LLM 自由重写 state 的入口。当前诊断已经证明字段 shape alignment 是真实风险：fresh Read output 提出 concept/thread payloads，但 shape 与 `state_ops` persistence 不对齐。 这说明需要 formation contract，而不是只修一次 bug。

### Improvement directions

第一，`memory_uptake_ops` 应正式定义为 write intent。Mem0 的 add operation docs 是最直接依据：add 不是黑盒写入，而是 information extraction、conflict resolution、storage；update/delete/search 也是一等操作。Reading Companion 应本地化为：`Read` 只提出“这个 unit 之后什么需要留存、目标 store 是什么、operation 是什么、source evidence 是什么、reason 是什么、payload 是什么”；settlement 才决定 accepted、merged、normalized、skipped、failed、deferred。

第二，formation 应拆成 extraction、evidence binding、relation/conflict handling、settlement。SourceRef 不能在最后才补；如果 `Read` 只输出抽象 summary，settlement 很难可靠绑定 source。当前 Read contract 已经要求 surfaced reaction 的 `source_quote` 是最小 self-sufficient span；同样原则应扩展到 memory uptake。 未来每个 op 应至少包含 target_store、operation_type、target key/item id、source quote or source_ref hint、payload、reason。Settlement 负责把 unit-local quote 解析成 inline SourceRef；无法解析时应记录 `failed_source_binding` 或 `skipped_unbound_evidence`。

第三，Read-path 不应形成高层 reflective memory。Generative Agents 的 observation -> reflection 支持“低层 observation 先进入 stream，高层 reflection 由阈值触发”，不是每个 observation 都立刻升格。Reading Companion 的本地化：Read-path 可以写 active_attention、concept_registry、thread_trace 的低风险局部更新；reflective_frames、chapter-level synthesis、book-level motifs、reconsolidation、supersede 更适合 slow-cycle。

第四，Read 不应形成三类东西：不应自动把 `reaction_records` 提升成 semantic memory；不应自动把 `knowledge_activations` 合并进 concept_registry；不应自改 procedural prompt / reader policy。LangGraph / LangMem 的 hot-path / background memory writes 支持这种分工：即时写入与后台 consolidation 是不同设计点。HaluMem 的 operation-level hallucination 也说明，越让 LLM 在 hot path 做最终状态改写，污染越难定位。

### Design implications

- `memory_uptake_ops` 是 bounded write intent，不是 final persisted object。
- 每个 op 应带 target_store、operation_type、stable key、payload、reason、source evidence。
- Settlement 应记录 per-op outcome。
- SourceRef binding 是 formation contract 的核心。
- Read-path 只做局部、低风险、source-grounded 写入。
- 高层 reflection、supersede、reconsolidation 交给 slow-cycle。

------

## 3.3 Memory Management and Evolution

### Current state and gap

当前项目已经有 lifecycle vocabulary，并且 state_ops 中已经实现了部分语义：active_attention 支持 create/update/reactivate/cool/resolve/drop，concept/thread 支持 update/resolve/drop，reflective item 支持 supersede。 这说明项目没有停留在 append-only memory。

gap 是 lifecycle 还没有被设计成跨 store 的稳定机制。尤其是阅读中最常见的“后文修正前文”，不能只靠 update 或 append。否则旧理解、新理解、visible reaction、prior activation 会并存，retrieval 时很容易引发 FVI。

### Improvement directions

第一，应把 lifecycle 分成 **visibility lifecycle** 与 **semantic validity lifecycle**。MemoryBank 的 forgetting curve 可以类比支持 refresh / reinforcement / decay，但 Reading Companion 不应把 forgetting 直接理解为删除事实。对 reading state 来说，很多变化只是可见性变化：active_attention item cooling、resolved、dropped from hot view。另一些是语义效力变化：旧解释被 supersede，某个 prior activation 被 rejected，某个 thread 被 resolved。
Zep 的 valid_at / invalid_at 更适合后者。Reading Companion 不需要 wall-clock temporal KG，但可以用 source-span 或 chapter-scope validity：例如 “valid until later source ref X superseded it” 或 “invalidated_by_source_ref”。这能保留解释演化轨迹。

第二，应定义哪些 op 属于 read-path，哪些属于 slow-cycle。Read-path 适合 create/update/reactivate/resolve/cool 这类局部状态操作；slow-cycle 适合 promote、supersede、chapter_consolidation、reflective_promotion、reconsolidation、cross-chapter carry-forward。当前机制已经有 slow-cycle node bundle：`reflective_promotion / reconsolidation / chapter_consolidation` 与 steady-state `read_unit` 分开。 LangMem 的 background memory manager 支持“consolidation/update 应与即时理解分离”，但 Reading Companion 不需要引入独立 manager agent；chapter-end / run-end slow-cycle 就是本地化的 background consolidation。

第三，后文修正前文时应优先使用 supersede / invalidate，而不是 destructive overwrite。当前 `supersede_reflective_item` 已经保留旧 statement，只标记 `status = superseded` 与 `superseded_by_item_id`。 这应成为全局设计原则。Mem0 的 update/delete docs 支持 update/delete 是一等 lifecycle operation，但 Reading Companion 应本地化为 source-ref-preserving update 和 soft invalidation，而不是简单硬删除。

第四，复杂 memory manager agent 应延后。当前 deterministic state_ops + slow-cycle LLM nodes + audit 组合更符合项目约束。复杂 manager agent 会让每次 management decision 变成另一个不可解释的 LLM 行为，反而削弱 audit。

### Design implications

- Lifecycle 应区分 visibility change 与 semantic validity change。
- Read-path 负责局部低风险 op；slow-cycle 负责 promotion、supersede、reconsolidation、chapter consolidation。
- `supersede / invalidate / retire` 优先于 destructive overwrite。
- 每个 store 应定义 allowed operation set。
- `drop` 应谨慎，尤其不用于 reaction_records 和 audit ledger。
- 当前不引入复杂 memory manager agent。

------

## 3.4 Memory Retrieval and Utilization

### Current state and gap

当前 retrieval 已有好雏形，但还不成熟。`state_projection.py` 生成 bounded prompt-facing packet：active_attention 最多若干条、concept digest、thread digest、reflective frame、recent reactions、source_ref digest。 `read_context.py` 的 `active_recall` 会补充未 carry 的 concept/thread/reaction，`look_back` 会基于 source refs 返回 earlier excerpts。

gap 是：当前 retrieval 更像 fixed packet + supplemental context，而不是按 intent 选择 memory。它还缺少“取回后如何被使用”的最小 trace。取回 memory 并塞进 prompt，不等于 memory 被正确利用；它可能被忽略、误用、过度整合，或造成 FVI。

### Improvement directions

第一，应先定义 retrieval intent taxonomy。当前机制天然已有几种 retrieval intent：continuity carry、active recall、look-back、detour localization、slow-cycle consolidation、probe retrieval。
Generative Agents 的 recency / relevance / importance retrieval 说明 retrieval 不应只看语义相似；MemGuide 的 intent-driven memory selection 说明应按当前 goal / missing slot 选 memory；GraphRAG 的 local/global/DRIFT 说明局部证据问题与全局 sensemaking 问题需要不同 mode；ComoRAG 的 impasse-triggered probing 说明 retrieval 可以在理解卡住时触发，而不是每步固定执行。

Reading Companion 可本地化为：

- **continuity retrieval**：默认 carry-forward，支撑局部阅读连续性；
- **active recall**：当当前 unit 需要旧 concept/thread/reaction 但未 carry 时补充；
- **look-back retrieval**：回到 earlier source span，用于校准、补证、避免 FVI；
- **detour retrieval**：由 Navigate 在 active detour 中定位可读 source unit；
- **slow-cycle retrieval**：章末或窗口末 consolidating；
- **probe retrieval**：benchmark snapshot / diagnostic 使用。

第二，metadata、source refs、lightweight links 应优先于 vector DB / graph DB。Mem0 的 search filters / reranking 支持 filters-first 的思路。Reading Companion 先需要 store type、status、chapter scope、source_ref、concept/thread link、supersede chain、attention tags。这些字段即使在 file-based JSON 中也能发挥作用。GraphRAG 和 RAPTOR 支持 multi-granularity retrieval 的思想，但它们主要是 corpus index / RAG pipeline，不是 inside-run reading memory。

第三，retrieval 后要有 utilization trace。当前 `record_read` 已经记录 `carry_forward_ref_ids`、`context_request`、`supplemental_ref_ids`、stop_reason、budget_exhausted。 下一步可以增加最小 signal：哪些 refs 被 used，used_for 什么，哪些 ignored，是否生成 prior_link / memory_uptake / detour_need。LongMemEval 的 retrieval vs reading stage decomposition 支持这个拆分：retrieval 命中不等于 utilization 正确。

第四，active_recall / look_back 应继续 bounded，不应变成自由 RAG loop。ComoRAG 的 iterative retrieval-consolidation 对 narrative reasoning 有启发，但照搬会使 Reading Companion runtime 过重。当前 read audit 已记录 supplemental steps 与 budget exhaustion，应该继续保留预算边界。

### Design implications

- Retrieval 设计页应先定义 retrieval intent taxonomy。
- 默认路径是 bounded carry-forward + selective recall，不是全局 semantic search。
- SourceRef、metadata、status、links、chapter scope 优先于 vector DB / graph DB。
- 需要最小 utilization trace：取回了什么、用了什么、为什么没用。
- active_recall / look_back / detour retrieval 必须有预算、stop reason、failure reason。
- 高层 frame 可以作为 retrieval entry，但必须保留 lower-level source evidence。

------

## 3.5 Memory Evaluation and Audit

### Current state and gap

当前评估方向非常好。`Memory Quality / Spontaneous Callback / False Visible Integration` 三者分别覆盖：state snapshot quality、自然回忆/连接、错误整合/污染。`backend-reader-evaluation.md` 明确说这三个目标互补但 contract-level distinct，不能过早合成一个总分。

gap 是：当前 evaluation 需要从 holistic quality 进入 stage-aware diagnosis。现在可以评估“当前 memory state 好不好”“visible reaction 是否 callback”“是否 FVI”，但还不一定能定位失败来自 formation、settlement、retrieval、utilization、还是 visible integration。

### Improvement directions

第一，Memory Quality 应拆成可诊断维度。LongMemEval 把 long-term memory ability 拆成 indexing / retrieval / reading，并包含 knowledge update、temporal reasoning、abstention。Reading Companion 应本地化为：formation correctness、source evidence binding、settlement success、retrieval availability、utilization correctness、structural retention、drift/pollution、abstention/uncertainty。
当前 holistic MQ 的 salience、mainline fidelity、organization、fidelity 应保留，但要能回溯到这些阶段。比如一个 source-given definition 没被保留，可能是 Read 没写 op，可能是 settlement skipped，可能是 concept digest 没 carry，也可能是 judge snapshot 未暴露到该 store。

第二，Spontaneous Callback 与 FVI 应分别接入 utilization evaluation 与 pollution evaluation。Callback 成功不是“提到了旧东西”，而是自然、source-grounded、恰当地使用了 earlier material。FVI 则是 weak grounding、theme-only similarity、overclaim、hard-linking、drift。LoCoMo 的 temporal/causal continuity 与 LoCoMo-Plus 的 latent constraint evaluation 都提醒我们：长期记忆不能只看 explicit factual recall，必须看跨时序约束是否持续正确。

第三，audit 应增加 per-op outcome，而不是 full snapshot。`settlement_audit` 的 compact delta 已经很好。 但应补充 op-level outcome：accepted、merged、normalized、skipped_bad_payload_shape、failed_source_binding、deferred_to_slow_cycle、superseded_existing、resolved_existing。HaluMem 的 operation-level hallucination 直接支持这一点：如果 formation / update 阶段污染，等最终输出才发现已经太晚。

第四，runtime-quality 报告要诚实标注 artifact-read status。本轮没有直接逐条打开 runtime artifacts；后续正式 runtime-quality assessment 应基于 actual `read_audit.jsonl / settlement_audit.jsonl / active_attention.json / concept_registry.json / thread_trace.json / reaction_records.json`，并区分 code-contract evidence、runtime-row evidence、judge-eval evidence、diagnostic-only evidence。

### Design implications

- Evaluation 页面应保留 holistic MQ，但增加 stage-aware diagnostic axes。
- Callback 是 utilization 成功信号；FVI 是 pollution / over-integration 风险信号。
- Audit 页面应定义 per-op outcome 和 failure reason。
- 不做 full snapshot per unit；保留 compact deltas + targeted probe snapshots。
- Structural retention 应继续作为 MQ 重点。
- Runtime-quality 报告必须标注是否直接读取 artifacts。

------

## 3.6 Storage and Infrastructure Restraint

### Current state and gap

当前 file-based JSON / JSONL storage 仍然适合。`storage.py` 已经完整定义机制私有 runtime artifacts、audit streams、probe exports、checkpoint files。 Source-of-truth map 也明确 repo-first：持久事实应在 canonical repo docs 或 runtime files 中，而不是 chat 或 Notion。

gap 不在存储引擎，而在 IDs、metadata、links、source_refs、status、lifecycle contract。没有这些，迁移到 vector DB / graph DB 只会把模糊语义搬进更难审计的基础设施。

### Improvement directions

第一，继续以 JSON / JSONL 为默认。当前 memory volume、inside-trial reading scope、source-grounded evidence spine 都适合 file-based state。外部应用工作如 Claude Code、Gemini CLI、OpenClaw、Hermes 也显示 file memory / workspace memory / daily logs 可以成为真实产品中的高可审计实践。Reading Companion 需要结构化 JSON 而不是 Markdown，是因为 SourceRef 和 audit 需要 typed fields。

第二，何时才需要 vector DB？只有当 memory item 数量和跨章节 recall 复杂度超过 metadata/source_ref/link-based retrieval 能力，并且 eval case 明确证明 vector retrieval 提升 recall、没有显著增加 FVI，才值得考虑。Mem0 的 vector search 仍要配 filters、rerank、threshold；这说明即便未来用 vector，也不能绕过 metadata contract。

第三，何时才需要 graph DB？只有当 JSON links 无法处理多跳 concept/thread 查询，且这种多跳 retrieval 已被小窗口验证为核心痛点时，才值得考虑。Zep temporal KG、GraphRAG、HippoRAG 都是 boundary case，而不是当前路径。Reading Companion 应先做 lightweight links。

第四，避免把项目做成 memory platform。MemGPT / MemOS / Memory-as-Action 都提供 complexity boundary：它们有研究价值，但会把 Reading Companion 从“第二读者”推向“通用 memory runtime”。这与项目 Simplicity and Universality 不匹配。

### Design implications

- Storage 页面默认坚持 JSON / JSONL。
- 先定义 stable IDs、metadata、source_refs、links、status、supersede chain。
- Vector DB 只能由 retrieval failure + eval evidence 触发。
- Graph DB 只能由 JSON links 无法解决的多跳关系任务触发。
- GraphRAG / RAPTOR 是 corpus-index 边界参照，不是 run-internal memory backend。
- Storage 设计应体现 Simplicity and Universality，不做 memory platform。

------

## 4. Cross-Module Priority Summary

### Blocking priorities

**明确 store ontology 与边界。**
归属模块：Memory Ontology。优先原因：如果 `active_attention / concept_registry / thread_trace / reflective_frames / reaction_records / knowledge_activations` 的身份不清，后续 Formation、Retrieval、Evaluation 都会不稳定。主要外部依据：Zep facts/entities/observations、LangGraph Memory Concepts、Letta Memory Blocks、CAM。复杂度：Medium。需要小窗口验证：是，验证同一批 source units 在不同 store 的写入边界是否稳定。

**固定 `memory_uptake_ops` 作为 bounded write intent。**
归属模块：Memory Formation / Audit。优先原因：当前诊断已经暴露 Read payload shape 与 state_ops field shape 不对齐；如果 contract 不收紧，op quality 无法评估。主要外部依据：Mem0 add/update/delete docs、HaluMem、LangGraph hot-path/background memory。复杂度：Medium。需要小窗口验证：是，逐条审计 op outcome。

**定义 lifecycle semantics 与 read-path / slow-cycle 分工。**
归属模块：Memory Management / Evolution。优先原因：后文修正前文是 reading memory 核心场景；没有 supersede / invalidate / visibility decay，会诱发冲突状态和 FVI。主要外部依据：Mem0 update/delete、Zep valid_at/invalid_at、MemoryBank forgetting、Generative Agents reflection trigger。复杂度：Medium。需要小窗口验证：是，选择概念被后文修正的窗口。

**建立 per-op outcome audit。**
归属模块：Audit / Observability、Memory Evaluation。优先原因：当前 compact audit 已有，但缺少 failure localization。主要外部依据：LongMemEval、HaluMem。复杂度：Low-to-Medium。需要小窗口验证：是。

### High-value next priorities

**定义 retrieval intent taxonomy。**
归属模块：Retrieval / Utilization。优先原因：当前 retrieval 已有 fixed packet 与 active_recall/look_back 雏形，但缺 intent-aware selection。主要外部依据：Generative Agents、MemGuide、GraphRAG、ComoRAG。复杂度：Medium。需要小窗口验证：是。

**把 `reaction_records` 与 semantic memory 的边界写硬。**
归属模块：Ontology / Formation / Evaluation。优先原因：callback 需要 reaction history，但 FVI 也常来自把 visible trace 当 semantic truth。主要外部依据：Zep observations、LongMemEval utilization separation、HaluMem pollution framing。复杂度：Low。需要小窗口验证：是。

**把 `knowledge_activations` 固定为 warrant ledger。**
归属模块：Ontology / Formation。优先原因：prior knowledge 是产品价值，但也最容易造成 text-detached certainty。主要外部依据：Zep evidence-backed observations、CAM、Semantic Anchoring。复杂度：Low-to-Medium。需要小窗口验证：是。

**把 structural retention 纳入 Memory Quality 诊断链。**
归属模块：Evaluation。优先原因：阅读理解高度依赖 stage model、classification、definition、roadmap。主要外部依据：StructMemEval、CAM、GraphRAG、RAPTOR。复杂度：Medium。需要小窗口验证：是。

### Later / optional priorities

**轻量 linguistic anchors。**
归属模块：Formation / Retrieval。价值：文本阅读依赖指代、定义、discourse hinge；当前可先用 source refs 与 tags。主要外部依据：Semantic Anchoring。复杂度：Medium。需要小窗口验证：是。

**跨 run / cross-session memory。**
归属模块：Management / Storage。价值：未来再阅读和长期 reading companion 可能需要；当前 source 主要是 inside-trial reading observations。主要外部依据：LongMemEval、LoCoMo、MemoryBench。复杂度：High。需要小窗口验证：是，但应后置。

**procedural reading memory。**
归属模块：Ontology / Management。价值：可能记录“以后如何读这种段落/这种书”；但当前不应进入主机制。主要外部依据：LangGraph / LangMem prompt refinement。复杂度：High。需要小窗口验证：必须先有评估闭环。

### Reject / defer priorities

**vector DB now、graph DB now、Memory OS now、RL Memory-as-Action now、complex memory manager agent now。**
归属模块：Storage / Infrastructure、Management。优先原因：它们会放大复杂度，但不解决当前 blocking gap。主要外部依据：Mem0 optional graph memory、Zep as graph boundary case、GraphRAG/RAPTOR as corpus-index boundary cases、MemGPT/MemOS/Memory-as-Action as complexity boundary。复杂度：High。需要小窗口验证：只有轻量方案被证明不足后才需要。

------

## 5. What to Reject or Defer Now

**vector DB now。**
诱惑是用 semantic similarity 解决 recall。但现在真正缺的是 metadata、source refs、store identity、lifecycle、retrieval intent 和 utilization trace。Mem0 的 search filters / reranking 支持“先有 filters 与 thresholds”，不是“先接向量库”。重新考虑条件：JSON/source_ref/link-based recall 在明确 eval cases 上反复失败，且 vector recall 不显著增加 FVI。

**graph DB now。**
诱惑是把 concept/thread 直接图谱化。Zep、GraphRAG、HippoRAG 都是强参照，但它们的原场景比当前 Reading Companion 重得多。现在应先做 JSON lightweight links。重新考虑条件：多跳 relation recall 成为核心失败模式，且 JSON links 无法支撑。

**structure_memory now。**
诱惑是为 stage model、classification、definition、roadmap 开一个新 store。但当前已有 concept_registry、thread_trace、reflective_frames。新增 `structure_memory` 会制造边界混乱。重新考虑条件：现有 store contract 被写清后仍无法表达某类 source-given structure。

**Memory OS now。**
诱惑是把 memory 做成完整 OS 或 virtual context system。MemGPT / MemOS 说明这条路线存在，但 Reading Companion 当前不是通用 agent memory platform。重新考虑条件：产品目标明确转向长期、多任务、跨书、跨 agent 的 memory runtime。

**RL-based Memory-as-Action now。**
诱惑是让系统自动学习 memory editing policy。但当前没有稳定 reward、重复环境和 operation-level eval。重新考虑条件：已有稳定 op audit、大量可重复运行数据、明确 reward，并且可解释性不被牺牲。

**procedural memory / prompt refinement as main mechanism now。**
诱惑是让系统自我改进阅读策略。LangGraph / LangMem 支持 procedural memory 作为一种类型，但 Reading Companion 当前主机制应是 source-grounded reading memory。重新考虑条件：内容 memory 已稳定，且有独立 evaluation 能判断 prompt refinement 是否提升阅读而非污染。

**Read writes final persisted object。**
诱惑是减少 settlement complexity。但这会让 LLM 直接改写 state，难以审计。Mem0 和 HaluMem 都支持 operation-level pipeline。重新考虑条件：无；当前应保持 Read intent + deterministic settlement。

**per-unit reflection。**
诱惑是每段都总结高层意义。但 Generative Agents 的 reflection 是阈值触发，不是每步触发。Reading Companion 应用 slow-cycle consolidation。重新考虑条件：只有特定 hard passage / chapter boundary 需要。

**reaction_records auto-promoted to semantic memory。**
诱惑是让自然反应成为 richer memory。但 visible reaction 是阅读过程 trace，不等于 book-grounded semantic truth。重新考虑条件：必须经过 explicit op 或 slow-cycle promotion，并带 source refs。

**knowledge_activations auto-merged into semantic stores。**
诱惑是 broad prior knowledge 能增强理解。但 product guardrail 已明确 prior knowledge 不能 justify text-detached certainty。重新考虑条件：只有 source text 给出 warrant，并通过 explicit operation 绑定 evidence。

**full snapshot per unit audit。**
诱惑是“全都存下来就可审计”。但它会产生巨大噪声。当前 compact delta + per-op outcome 更好。重新考虑条件：只有在少量 debug session 中临时使用，不作为标准 audit。

**complex memory manager agent。**
诱惑是把 lifecycle 全交给一个智能 manager。但当前 deterministic settlement + slow-cycle 足够，且更可审计。重新考虑条件：当 rule-based settlement 无法覆盖复杂跨章节演化，且已有 per-op audit 能监督 manager。

------

## 6. Design Takeaways for Future Work

### Memory Ontology

- 要解决 source corpus、reading memory、visible trace、audit ledger、prior knowledge warrant ledger 的边界；这是后续所有页面的前提。主要参考 Zep、LangGraph、Letta、CAM。避免把 chatbot/user-profile memory 迁移进 Reading Companion。
- 现有 stores 应先写清身份，不新增 `structure_memory`。`concept_registry` 承载 concept/definition/classification，`thread_trace` 承载 line/thread，`reflective_frames` 承载 promoted higher-order frame。
- `reaction_records` 默认是 visible trace；`knowledge_activations` 默认是 warrant ledger。避免自动语义化。

### Memory Formation

- `memory_uptake_ops` 必须是 bounded write intent，不是最终持久对象。主要参考 Mem0 operation docs、HaluMem。
- Formation 应包含 extraction、evidence binding、relation/conflict handling、settlement。SourceRef 是必需字段，不是附属字段。
- Read-path 不应做 high-level reflection、reaction auto-promotion、prior knowledge merge、prompt refinement。避免 LLM 直接重写完整 state。

### Memory Management / Evolution

- lifecycle 要区分 visibility change 与 semantic validity change。主要参考 Zep valid/invalid、Mem0 update/delete、MemoryBank forgetting。
- 后文修正前文应优先 supersede / invalidate / retire，而不是 destructive overwrite。
- read-path 与 slow-cycle 要分工：局部更新在 read-path，高层 promotion / reconsolidation 在 slow-cycle。避免 complex memory manager agent。

### Memory Retrieval / Utilization

- 先定义 retrieval intent taxonomy：continuity、active_recall、look_back、detour、slow-cycle、probe。
- SourceRef、metadata、links、status、chapter scope 优先于 vector DB / graph DB。主要参考 Generative Agents、MemGuide、GraphRAG、ComoRAG。
- 取回后需要 utilization trace：用了什么、没用什么、用于什么。避免把“塞进 prompt”当成“利用”。

### Memory Evaluation

- Memory Quality 保留 holistic score，但增加 formation / retrieval / utilization / drift / structural retention 诊断维度。
- Spontaneous Callback 是 utilization 成功信号，FVI 是 pollution 风险信号。主要参考 LongMemEval、LoCoMo、HaluMem、StructMemEval。
- Structural retention 必须继续关注 stage model、classification、definition、roadmap、named distinction。避免只看 final QA correctness。

### Audit / Observability

- 增加 per-op outcome 与 failure reason，而不是 full snapshot per unit。主要参考 HaluMem、LongMemEval。
- `read_audit` 与 `settlement_audit` 应能串起 Read intent、source binding、settlement result、store delta。
- Runtime-quality assessment 必须基于实际 artifacts；不能只凭 architecture 与 docs 判断。

### Storage / Infrastructure

- JSON / JSONL 仍是默认。主要参考 file-based application memory practices、Mem0 metadata-first、Zep as boundary case。
- 先做 stable IDs、metadata、source_refs、links、status、supersede chains。
- vector DB / graph DB 只能由 eval-proven bottleneck 触发。避免把项目做成 memory platform。

------

## 7. Source Usage Appendix

说明：以下列出本报告实际依赖的外部 paper / official docs / project pages。未把 `Memory External Evidence Pack v1.md` 或 `Application Memory External Evidence Patch v1.md` 当作外部来源列入。由于当前环境无法进行实时网页检索，2025/2026 官方文档的年份与机制描述按用户提供的外部证据索引与稳定 URL 使用；本报告没有声称这些产品页面的实时 UI 状态已被重新在线验证。

| External source                                              | Authors / Organization               | Year           | Stable URL                                                   | Used in sections           | Role                                  |
| ------------------------------------------------------------ | ------------------------------------ | -------------- | ------------------------------------------------------------ | -------------------------- | ------------------------------------- |
| Generative Agents: Interactive Simulacra of Human Behavior   | Joon Sung Park et al.                | 2023           | https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/ | 2.3, 3.2, 3.3, 3.4, 5      | Direct support                        |
| Mem0 Core Concepts: Memory Operations — Add / Update / Delete / Search | Mem0                                 | 2025–2026 docs | https://docs.mem0.ai/core-concepts/memory-operations/add     | 2.1, 2.2, 3.2, 3.3, 3.4, 5 | Direct support                        |
| Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | Prateek Chhikara et al.              | 2025           | https://arxiv.org/abs/2504.19413                             | 3.2, 3.6, 5                | Direct support                        |
| Zep: A Temporal Knowledge Graph Architecture for Agent Memory | Preston Rasmussen et al.             | 2025           | https://arxiv.org/abs/2501.13956                             | 2.1, 3.1, 3.3, 3.6         | Direct support                        |
| Zep Graph / Facts / Entities / Observations Docs             | Zep                                  | 2025–2026 docs | https://help.getzep.com/graph-overview                       | 2.1, 2.2, 3.1, 3.3, 3.6    | Direct support                        |
| LangGraph Memory Concepts                                    | LangChain                            | 2025–2026 docs | https://docs.langchain.com/oss/python/concepts/memory        | 2.1, 3.1, 3.2, 3.3, 5      | Direct support                        |
| LangMem                                                      | LangChain                            | 2025–2026 docs | https://github.com/langchain-ai/langmem                      | 3.2, 3.3, 5                | Direct support                        |
| Letta Memory Blocks Docs                                     | Letta                                | 2025–2026 docs | https://docs.letta.com/guides/core-concepts/memory/memory-blocks | 2.2, 3.1                   | Direct support                        |
| Letta Archival Memory Docs                                   | Letta                                | 2025–2026 docs | https://docs.letta.com/guides/ade/archival-memory/           | 2.3, 3.4, 3.6              | Boundary / negative support           |
| MemoryBank: Enhancing Large Language Models with Long-Term Memory | Wanjun Zhong et al.                  | 2024           | https://ojs.aaai.org/index.php/AAAI/article/view/29946       | 3.1, 3.3, 5                | Analogical support / boundary         |
| LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory | Di Wu et al.                         | 2024           | https://arxiv.org/abs/2410.10813                             | 2.2, 3.4, 3.5, 4           | Direct support                        |
| Evaluating Very Long-Term Conversational Memory of LLM Agents / LoCoMo | Adyasha Maharana et al.              | 2024           | https://aclanthology.org/2024.acl-long.747/                  | 3.5, 4                     | Analogical support                    |
| LoCoMo-Plus: Beyond-Factual Cognitive Memory Evaluation Framework for LLM Agents | Yifei Li et al.                      | 2026           | https://openreview.net/forum?id=QWVKrMGdah                   | 3.5                        | Analogical support                    |
| HaluMem: Evaluating Hallucinations in Memory Systems of Agents | Ding Chen et al.                     | 2025           | https://arxiv.org/abs/2511.03506                             | 2.2, 3.2, 3.5, 4           | Direct support                        |
| Evaluating Memory Structure in LLM Agents / StructMemEval    | Alina Shutova et al.                 | 2026           | https://arxiv.org/abs/2602.11243                             | 3.5, 4                     | Direct support                        |
| MemoryBench: A Benchmark for Memory and Continual Learning in LLM Systems | Qingyao Ai et al.                    | 2025           | https://arxiv.org/abs/2510.17281                             | 4                          | Background only                       |
| CAM: A Constructivist View of Agentic Memory for LLM-Based Reading Comprehension | Rui Li et al.                        | 2025           | https://arxiv.org/abs/2510.05520                             | 3.1, 3.6, 4, 5             | Direct / analogical support           |
| ComoRAG: A Cognitive-Inspired Memory-Organized RAG for Stateful Long Narrative Reasoning | Juyuan Wang et al.                   | 2025           | https://arxiv.org/abs/2508.10419                             | 3.4, 5                     | Analogical support                    |
| RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval | Parth Sarthi et al.                  | 2024           | https://arxiv.org/abs/2401.18059                             | 3.4, 3.6, 5                | Analogical support / boundary         |
| From Local to Global: A Graph RAG Approach to Query-Focused Summarization | Darren Edge et al.                   | 2024           | https://arxiv.org/abs/2404.16130                             | 3.4, 3.6, 5                | Analogical support / boundary         |
| GraphRAG Docs                                                | Microsoft Research                   | 2024–2026 docs | https://microsoft.github.io/graphrag/index/overview/         | 3.4, 3.6, 5                | Boundary / negative support           |
| HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models | Bernal Jiménez Gutiérrez et al.      | 2024           | https://arxiv.org/abs/2405.14831                             | 3.6, 5                     | Analogical support / boundary         |
| MemGuide: Intent-Driven Memory Selection for Goal-Oriented Multi-Session LLM Agents | Yiming Du et al.                     | 2026           | https://ojs.aaai.org/index.php/AAAI/article/view/40313       | 3.4, 4                     | Direct support                        |
| Semantic Anchoring in Agentic Memory                         | Maitreyi Chatterjee, Devansh Agarwal | 2025           | https://arxiv.org/abs/2508.12630                             | 4, 6                       | Analogical support                    |
| Memory as Action: Autonomous Context Curation for Long-Horizon Agentic Tasks | Yuxiang Zhang et al.                 | 2025           | https://arxiv.org/abs/2510.12635                             | 2.3, 5                     | Boundary / negative support           |
| MemGPT: Towards LLMs as Operating Systems                    | Charles Packer et al.                | 2023           | https://arxiv.org/abs/2310.08560                             | 2.3, 3.6, 5                | Boundary / negative support           |
| MemOS: A Memory OS for AI System                             | MemOS authors                        | 2025           | https://arxiv.org/abs/2507.03724                             | 2.3, 5                     | Boundary / negative support           |
| Claude Code: How Claude remembers your project               | Anthropic                            | 2026 docs      | https://docs.anthropic.com/en/docs/claude-code/memory        | 2.1, 3.6                   | Analogical support                    |
| Gemini CLI: Memory Tool / GEMINI.md                          | Google Gemini CLI                    | 2026 docs      | https://google-gemini.github.io/gemini-cli/docs/tools/memory.html | 2.1, 3.6                   | Analogical support                    |
| OpenClaw / Clawdbot Memory Docs                              | OpenClaw / Clawd.bot                 | 2026 docs      | https://docs.openclaw.ai/concepts/memory                     | 2.1, 3.6                   | Analogical support                    |
| Hermes Agent Memory System                                   | Hermes Agent / Nous Research         | 2026           | https://hermes-agent.ai/blog/hermes-agent-memory-system      | 2.1, 3.6                   | Analogical support                    |
| ChatGPT Memory / Temporary Chat / Memory Sources docs        | OpenAI                               | 2024–2026 docs | https://help.openai.com/en/articles/8983136-what-is-memory   | 3.1, 5                     | Boundary / product governance support |
| Claude chat search and memory / project memory docs          | Anthropic                            | 2026 docs      | https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context | 3.4, 5                     | Analogical support                    |
| Gemini Apps Saved Info / Previous Chats docs                 | Google                               | 2026 docs      | https://support.google.com/gemini/answer/15637730            | 3.1, 5                     | Boundary / source disclosure support  |
| Perplexity Memory docs                                       | Perplexity                           | 2026 docs      | https://www.perplexity.ai/help-center/en/articles/10968016-memory | 3.4, 5                     | Boundary / source disclosure support  |