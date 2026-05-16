# Second Reader Shared Memory–Planning Mechanism Charter v0

## 0. Charter Status

本文档是 Phase 0 的 shared mechanism charter。它只定义 Memory 与 Planning 后续具体设计必须共同遵守的机制边界、接口原则、状态分区、settlement 规则和复杂度守门线。

本文档不重新定义 Second Reader / Reading Companion 的产品北极星，不替代 Memory Ontology、Planning Ontology、Navigation Policy、Visible Reading Route Surface Boundary、Slow-cycle、Audit / Evaluation 等后续设计页，也不规划后续设计顺序。

本次对 runtime artifacts 没有逐行打开真实运行目录中的 `read_audit.jsonl / settlement_audit.jsonl / unit_span_ledger.jsonl / active_attention.json / concept_registry.json / thread_trace.json / reaction_records.json` 等文件。因此本文的运行质量判断只限于 repo 文档记录的诊断摘要；正文规则主要是 architecture-level 与 contract-level charter，不声称已完成独立 runtime-quality audit。

------

## 1. Charter Purpose

Memory 与 Planning 在 Second Reader 中不是两个独立平台能力。它们共同服务一个更窄的对象：一个 text-grounded、legible、self-propelled 的共读心智如何持续读一本书。

Second Reader is an independent reader. Users do not decide its reading route. Future user-visible route surfaces may disclose or explain the reader's path, but must not become route steering.

Canonical terms for later pages:

```text
internal_navigation = actual reading path control
reading_route_trace = internal route / audit trace for mainline, detour, look-back, restore, defer, and resolve
visible_reading_route_surface / visible_route_disclosure = future optional display of route trace
visible_reading_note = low-interruption explanation of reader behavior
no_user_surface_needed = no visible route display needed
```

因此，本 Charter 要固定三条边界：

第一，Memory 不是“把更多东西记住”。Memory 是从 accepted source units 中形成的 source-grounded reading state，用来支撑后续阅读、回看、连接、再进入和 faithful continuity。

第二，Planning 不是 AutoGPT-style task planning。Planning 是 source-grounded reading path planning / attention scheduling / navigation support，用来决定下一步读哪里、是否继续主线、是否回看、是否 active recall、是否 detour、哪些关注点 carry forward，以及是否将内部路径决策保留为 `reading_route_trace`，未来可能通过 `visible_route_disclosure` 展示。

第三，Memory 与 Planning 都必须服从同一条运行原则：

> LLM proposes; deterministic runner settles.

LLM 可以提出阅读判断、记忆写入意图、detour need、下一 unit 边界、slow-cycle promotion 候选和 future visible reading note rationale。确定性 runner / state_ops / settlement 负责 SourceRef 绑定、schema normalization、ID 与 metadata、allowed operation 应用、cursor 推进、audit outcome 与 durable persistence。

------

## 2. Current Mechanism Understanding

当前默认机制是 `attentional_v2`。本 Charter 保留它的主骨架，并对其边界做收紧。

当前主循环应理解为：

```
survey / reading_plan orientation → Navigate.choose_next_unit → Read → Reading Runner post-read settlement → cursor advance / audit / ledger → slow-cycle at chapter/session boundary
```

其中：

- `survey` 是结构性 orientation，不是隐藏全文阅读，不产生 visible reactions，也不写 durable reading memory。
- `Navigate.choose_next_unit` 是当前唯一 next coverage unit selector。主线 unit selection 与 active detour localization 都是该入口下的模式，而不是并行的 planner family。
- `Read` 是当前 accepted source unit 的 reader-like interpretation call。它产生 `reading_impression`、`surfaced_reactions`、`memory_uptake_ops` 和可选 `detour_need`。
- `Reading Runner` 不询问 LLM 是否继续普通前进；普通 forward progression 是 deterministic settlement 后的默认行为。
- `detour` 是 normal reading redirection，不是隐藏 supplemental fetch。detour unit 一旦被选中，也通过同一个 `Navigate.choose_next_unit → Read → settlement` 路径读取。
- `slow-cycle` 同时涉及 memory consolidation 与 macro carry-forward，但不得成为大 planner、memory manager agent 或 self-modifying policy agent。

本 Charter 对当前实现的态度是：

- **保留**：paragraph-offset `SourceCursor / SourceSpan`、inline `SourceRef`、`Navigate → Read → settlement`、file-based JSON / JSONL、existing primary state stores、bounded prompt-facing projection、read / settlement audit。
- **收紧**：source corpus / reading memory / planning state / visible reaction / audit / visible route disclosure / evaluation evidence 的边界；`memory_uptake_ops` 作为 write intent；detour / look-back / active_recall 的归属；audit 不自动进 prompt。
- **调整**：把 Planning 正式定义为 reading-path planning / attention scheduling，而不是 task planning；把 slow-cycle 拆成 memory consolidation 与 macro carry-forward planning 两个可审计输出面。

------

## 3. Shared Territory Map

Memory 与 Planning 后续设计必须共用同一张状态边界图。

| Territory                             | Definition                                                   | Durable?                          | Prompt-facing by default?          | Owner                  |
| ------------------------------------- | ------------------------------------------------------------ | --------------------------------- | ---------------------------------- | ---------------------- |
| Source corpus                         | `book_document.json` 中的 parsed book substrate，包括 chapter / paragraph / sentence / locator truth | Yes, as source                    | No, only selected preview/excerpt  | Shared substrate       |
| Reading locus / source cursor         | 当前阅读位置、paragraph-offset cursor、accepted `SourceSpan`、unit boundary resolution | Yes, as runtime position / ledger | Only current preview / locus       | Runner                 |
| Accepted unit                         | 已由 Navigate 选中并由 runner 解析成功、交给 Read 的 source span | Ledger yes                        | Current unit yes                   | Runner                 |
| Reading memory                        | 从 accepted source units 中形成的 source-grounded reading state，如 `active_attention / concept_registry / thread_trace / reflective_frames` | Yes                               | Only via bounded projection        | Memory mechanism       |
| Planning state                        | 当前阅读路径控制状态，如 `mainline_cursor / active_detour_need / detour_trace / reading_queue_stage / pending navigation obligation` | Yes, lightweight                  | Only via navigation context        | Planning / Runner      |
| Audit trace                           | `unitization_audit / read_audit / settlement_audit / navigate_trace / debug events` | Yes, diagnostic                   | No                                 | Observability          |
| Visible reaction                      | 面向用户的 reading-time thought / mark / margin note         | Yes, as visible trace             | No, except recent bounded digest   | Reaction persistence   |
| Future visible reading route surface | 未来可能显示或解释 Second Reader 自己的 mainline、detour、look-back、restore 等 reading route trace 的产品 surface | Optional display trace             | Visible to user only; not internal plan | UX / route disclosure surface |
| External / prior knowledge activation | 先验知识被触发、允许参与阅读的 warrant ledger                | Yes, as warrant                   | No, unless explicitly projected    | Knowledge activation   |
| Evaluation evidence                   | probe snapshots、judge reports、benchmark outputs、quality audit summaries | Yes, eval artifact                | No                                 | Evaluation             |

关键规则：

- Source corpus is not memory.
- Unit span ledger is not semantic memory.
- Audit trace is not prompt-facing context.
- Visible reaction is not automatically semantic memory.
- Future visible route disclosure is derived from internal route trace and cannot create route controls, accept/reject states, or navigation transitions.
- Prior knowledge activation is not book-grounded memory unless explicitly grounded and settled.
- Evaluation evidence is not runtime memory.

------

## 4. Memory–Planning Interface Contract

### 4.1 Planning 如何使用 Memory

Planning 只能通过 bounded, typed, source-ref-preserving projections 使用 memory。

允许的 memory-to-planning 输入包括：

- active attention digest：当前仍影响近端阅读的 hot items；
- concept digest：少量当前最相关的概念、定义、模型、分类、命名区别；
- thread digest：少量跨 passage / 跨 chapter 的延续线索；
- reflective digest：已被 slow-cycle promoted 的高层 frame；
- source_ref digest：可回到 source 的 evidence spine；
- recent reaction digest：少量最近 visible trace，用于 continuity，不等于 durable semantic truth；
- active_recall result：当当前 reading need 指向未 carry 的 concept/thread/reaction 时补充；
- look_back excerpt：当需要重新校准 source evidence 时回到 earlier source text。

Planning 不得直接读取整个 durable memory store 作为大 prompt，也不得把 audit dump 当作 reasoning context。

### 4.2 Memory 如何被 Planning 触发或影响

Planning 可以触发 memory retrieval，但不能直接写 memory。

具体规则：

- `Navigate.choose_next_unit` 可以使用 memory projection 来判断下一步 source unit、detour 是否值得继续、是否 defer。
- `Read` 可以基于当前 unit 与 carry-forward context 提出 `memory_uptake_ops`。
- `Read` 可以提出 `detour_need`，但不定位 detour target，也不读取 detour source。
- `active_recall` 是 memory retrieval move；它取回 stored reading state。
- `look_back` 是 source calibration move；它取回 earlier source excerpts。
- Slow-cycle 可以使用 settled memory、visible reactions、chapter source refs 与 audit summaries，提出 promotion / cooling / supersede / carry-forward 候选。
- Durable memory 的最终变化必须由 runner / state_ops / settlement 应用。

### 4.3 Read 节点的双重 intent

`Read` 在 Memory 与 Planning 中都提出 intent，但不能越界。

Memory intent：

- 形成 `reading_impression`，但它不是 durable memory；
- 产生 `memory_uptake_ops`，但它们是 bounded write intents，不是 final persisted objects；
- 只针对允许的 primary state stores 提出低风险局部更新；
- 不写 `reflective_frames`、`reaction_records`、audit layer、policy layer 或完整 state object。

Planning intent：

- 可以发出 `detour_need`；
- 可以说明 detour 的 reason、target_hint、status；
- 不能决定下一步实际路线；
- 不能定位 detour unit；
- 不能自行执行 look-back / detour / route transition。

### 4.4 Runner / state_ops / settlement 的确定性职责

Runner / state_ops / settlement 必须负责：

- 将 `end_anchor_text` 解析为 exact paragraph-offset `SourceSpan`；
- 生成或校验 `source_span_id`；
- 将 unit-local `source_quote` / source hints 解析为 inline `SourceRef`；
- 规范化 `memory_uptake_ops`；
- 校验 target store、allowed operation、payload shape；
- 合并 / upsert / resolve / cool / supersede；
- 生成 IDs、timestamps、metadata；
- 持久化 JSON / JSONL artifacts；
- 写入 `read_audit`、`settlement_audit`、unit span ledger；
- 推进 cursor；
- 对失败、fallback、skipped op、source binding failure、budget exhaustion 形成可诊断 outcome。

### 4.5 Detour / Look-back / Active Recall 的归属

这三者都横跨 Memory 与 Planning，但归属不同：

- **Active recall**：memory recovery。用于“之前形成的 reading state 现在可能需要回来”。它从 concept/thread/reaction 等 stores 取回 bounded state，不等于 source verification。
- **Look-back**：source calibration。用于“原文到底怎么说、当前理解是否需要证据校准”。它回到 earlier source span，不等于 semantic memory recall。
- **Detour**：planning path deviation。用于“下一步阅读路径应暂时离开 mainline”。它由 `Read` 提出 need，由 `Navigate` 选择或 defer source-grounded target，由 runner 持久化 trace，并通过同一 read loop 读取。

Detour 必须有：

- origin cursor；
- target hint；
- reason；
- budget / stop reason；
- status：open / resolved / abandoned；
- restore-mainline reason 或 defer reason；
- outcome trace。

### 4.6 Slow-cycle 的边界

Slow-cycle 同时涉及 Memory 与 Planning，但输出必须分层：

Memory consolidation outputs：

- cooling operations；
- promotion candidates；
- reflective frames；
- supersede / reconsolidation；
- knowledge activation updates；
- source-ref-preserving carry-forward decisions。

Macro-planning outputs：

- next chapter/session carry-forward focus；
- open obligations；
- resolved / abandoned detour status；
- mainline restoration rationale；
- optional next-focus suggestion。

Slow-cycle 不得：

- 改写产品目标；
- 自行修改 prompts / reader policy；
- 生成完整 book-level planner；
- 重排全书阅读路线，除非后续机制设计明确授权；
- 把 strategy reflection 混入 book-grounded content memory。

------

## 5. Durable State / Trace / Output / Evaluation Boundary

### 5.1 可以进入 durable state 的内容

可以 durable 的内容必须满足至少一个条件：

- 是 source-grounded reading state，且有 accepted source unit 的 SourceRef；
- 是 current reading locus / cursor / accepted span / resume continuity 所需；
- 是 planning continuity 所需的 lightweight obligation，如 active detour；
- 是 visible reaction history，但仅作为 visible trace；
- 是 audit / evaluation artifact，但仅作为 diagnostic / benchmark evidence；
- 是 prior knowledge activation warrant，但不冒充 source-given truth。

### 5.2 只能作为 trace / audit 的内容

以下内容默认只能作为 trace / audit，不能自动进入 prompt-facing context 或 semantic memory：

- LLM raw reasoning；
- rejected navigation alternatives；
- skill request history；
- budget exhaustion details；
- failed source resolution；
- skipped memory ops；
- judge comments；
- evaluation report prose；
- debug events；
- full settlement deltas。

这些信息对诊断重要，但不能成为 runtime memory，除非后续设计定义了明确的 projection gate。

### 5.3 只能作为 visible output 的内容

Visible reaction 与 visible route disclosure 是用户可见产物。它们可以被持久化为 trace / display marker，但不能自动成为 concept/thread/reflective memory。

尤其是：

- 一条漂亮的 surfaced reaction 不自动进入 `concept_registry`。
- 一个 callback-like visible thought 不自动证明 memory utilization 成功。
- 一个 visible route disclosure 不自动改变 internal navigation state，也不让用户选择系统怎么读。
- 一个 outside_link / search_intent 不自动变成 external knowledge memory。

### 5.4 Evaluation evidence 的隔离

Evaluation evidence 是机制判断材料，不是 runtime state。

Memory Quality probe snapshot、Spontaneous Callback audit、False Visible Integration audit、planning audit report、judge score、benchmark summary，都不能自动成为下一次 reading run 的 prompt context 或 durable memory。

------

## 6. LLM / Runner / Settlement Division of Responsibility

### 6.1 LLM 可以提出

LLM 可以提出：

- 下一 readable unit 的 semantic boundary；
- `end_anchor_text`；
- `reading_impression`；
- bounded `surfaced_reactions`；
- bounded `memory_uptake_ops`；
- `detour_need`；
- active-detour skill request；
- detour defer reason；
- slow-cycle promotion / cooling / carry-forward candidates；
- reflective promotion candidate；
- reconsolidation candidate；
- future visible reading note rationale, if a route surface is designed。

### 6.2 LLM 不应该直接决定

LLM 不应该直接决定：

- final persisted memory object；
- raw cursor offsets；
- SourceRef binding validity；
- source span closure；
- unit ledger writes；
- durable deletion；
- destructive overwrite；
- store-wide rewrite；
- memory lifecycle final outcome；
- audit outcome；
- evaluation score;
- ordinary forward progression；
- future text usage；
- external search as default;
- visible route disclosure replacing source-order reading。

### 6.3 Runner / state_ops 必须决定

Runner / state_ops 必须决定：

- anchor resolution；
- SourceSpan construction；
- SourceRef normalization；
- operation normalization；
- allowed operation application；
- payload shape acceptance / rejection；
- ID and metadata；
- source-ref-preserving merge；
- status transition；
- persistence；
- audit row content；
- cursor advancement；
- resume and checkpoint consistency。

### 6.4 Settlement 的最低要求

每个 settlement transaction 应能回答：

- 这个 unit 的 source span 是什么；
- Read 提出了哪些 memory ops；
- 每个 op 的 target store 是什么；
- 每个 op 是否 accepted / normalized / merged / skipped / failed / deferred；
- source evidence 是否绑定成功；
- 哪些 state IDs added / updated / removed；
- 哪些 visible reactions emitted；
- detour state 是否打开 / 关闭 / 维持；
- cursor 是否推进；
- fallback 是否发生，为什么发生。

当前 audit 已经有 compact transaction summary；后续需要补的是 per-op outcome 与 failure reason，而不是 full snapshot per unit。

------

## 7. Shared Principles for Future Memory / Planning Design Pages

后续所有 Memory 与 Planning 详细设计页应继承以下原则。

### 7.1 Source-grounded before clever

任何 memory、plan、visible route disclosure、detour、callback 都必须能回到 source locus 或明确标记为 prior knowledge warrant。Broad prior knowledge 可以参与阅读，但不能制造 text-detached certainty。

### 7.2 Source corpus is not memory

书的原文是阅读对象，不是 agent memory。Memory 是阅读过程中从 accepted source units 形成的 state。

### 7.3 Reading memory is not visible trace

Visible reaction 是用户体验的一部分，也是 reaction history，但它不自动成为 semantic memory。需要进入 concept/thread/reflective state 时，必须经过 explicit memory operation 或 slow-cycle promotion。

### 7.4 Planning is reading-path control, not task decomposition

Planning 的对象是 reading path、attention、continuity、detour、look-back、recall、visible route disclosure boundary，不是通用外部任务执行。

### 7.5 Mainline continuity is the default

普通阅读默认继续 source-order mainline。Detour、look-back、deep-dive 都是有理由的例外，需要 value / evidence / uncertainty / continuity-cost 判断。

### 7.6 Detour is a first-class reading path, not a side channel

Detour 不应成为隐藏检索器。它必须有 origin、target hint、budget、status、exit reason，并通过同一 read loop 读取。

### 7.7 Retrieval must be intent-aware and bounded

默认不是全局 semantic search。先定义 retrieval intent：continuity carry、active recall、look-back、detour localization、slow-cycle consolidation、probe retrieval。每种 retrieval 都应有 budget、reason、stop condition 和 utilization trace。

### 7.8 Prompt-facing projection is not durable state

`state_packet.v1`、navigation context、read prompt packet 是 bounded projection，不是 authoritative store。后续设计不得把 prompt packet 反向当作 state truth。

### 7.9 Lifecycle must separate visibility and validity

Cooling / dropping from active view 是 visibility lifecycle；supersede / invalidate / rejected / resolved 是 semantic validity lifecycle。后文修正前文时，优先 soft invalidation / supersede，而不是 destructive overwrite。

### 7.10 Visible route disclosure is optional product surface

Visible route disclosure 是可解释、低打扰的产品展示面。它 derived from `reading_route_trace`，不等于 internal navigation decision，不能替代 source-order reading，也不能控制 internal navigation。

### 7.11 Audit is for diagnosis, not chain-of-thought exposure

Audit 需要 structured decision summary、source evidence、op outcome、failure reason、budget reason、restore-mainline reason。它不需要也不应该暴露完整 hidden reasoning。

### 7.12 Evaluation must separate quality, utilization, and pollution

Memory Quality、Spontaneous Callback、False Visible Integration 不应合并成一个模糊分数。Planning evaluation 也应区分 path quality、navigation groundedness、mainline continuity、detour precision、recovery quality、route trace legibility、visible route disclosure readiness、overplanning / thrashing、planning-memory alignment。

------

## 8. Complexity Guardrails

### 8.1 不默认引入 vector DB

当前主要风险不是“没有相似度检索”，而是 store ontology、operation semantics、SourceRef binding、retrieval intent 和 per-op audit 尚未稳定。先用 SourceRef、metadata、chapter scope、status、lightweight links、bounded digests。只有当评估证明 metadata/source-ref/link-based retrieval 已成为瓶颈，且 vector retrieval 不显著增加 False Visible Integration，才考虑引入。

### 8.2 不默认引入 graph DB

Concept/thread links、supersede chain、source_refs 可以先在 JSON state 中表达。Graph DB 只有在多跳 concept/thread 查询被证明是核心瓶颈，且 lightweight links 无法解决时才进入讨论。

### 8.3 不做 Memory OS

Second Reader 不是通用 memory runtime、context OS 或 memory platform。OS-style paging、agent-wide memory scheduling、account-wide personalization 会把产品推离 source-grounded co-reader。

### 8.4 不新增 large planner node

当前缺口不是“没有大 planner”，而是 planning ontology、navigation policy、detour policy、visible route disclosure boundary、audit fields 未收紧。新增大 planner 会把不清楚的职责包装成更难诊断的行为。

### 8.5 不做 multi-agent reading team

产品需要一个连贯的 co-reading mind。拆成 navigator agent、memory agent、critic agent、route-disclosure agent 会破坏 legibility，并显著增加 audit 与 user experience complexity。

### 8.6 不做 graph workflow rewrite

可以借鉴 durable execution、checkpoint、interrupt、trace 等思想，但当前 Reading Runner 已经承担 deterministic orchestration。工作流框架迁移不能替代 reading judgment 与 state contract。

### 8.7 不把 ToT / LATS / MCTS 作为默认阅读 loop

Search-based deliberation 适合 hard passage、争议解释、多路径 deep-dive；不适合作为每个 next-unit decision 的默认 loop。普通阅读缺少稳定 reward function，对延迟敏感，也需要维护 source-order continuity。

### 8.8 Visible route disclosure 不替代 source-order reading

书本的 source order 通常承载作者结构。Visible route disclosure 只能展示或解释 Second Reader 的 `reading_route_trace`；它不能把 reading path 改造成推荐流、learning path engine、或用户路线选择界面。

### 8.9 不合并 planning state 与 memory state

Planning state 是路径控制、pending obligations、detour status、restore-mainline logic。Memory state 是 source-grounded reading understanding。两者可以互相引用，但不能合并成一个大 store。

### 8.10 不让 Read 直接写 final persisted object

`Read` 应提出 bounded intent。Final persistence 必须经过 deterministic settlement，否则 source grounding、schema normalization、audit outcome 和 failure localization 都会失效。

### 8.11 不做 complex memory manager / planning manager agent

当前需要 contract-driven settlement、slow-cycle consolidation、structured audit，而不是另一个自治 manager agent。复杂 manager 会把可验证契约变成不可预测 behavior。

------

## 9. Accepted Shared Constraints

后续具体设计默认继承：

- file-based JSON / JSONL first；
- textual structured state first；
- inline paragraph-offset SourceRef first；
- stable IDs、metadata、status、links、source_refs before backend migration；
- bounded prompt projection；
- no future text beyond allowed reading frontier；
- no hidden search / hidden detour；
- no automatic promotion from visible trace to semantic memory；
- no automatic promotion from prior knowledge activation to book-grounded memory；
- no full snapshot per unit audit by default；
- compact audit + targeted per-op outcome；
- shared runtime shell boundary remains separate from mechanism-private ontology；
- `attentional_v2` evolves in place unless project leadership explicitly changes default mechanism.

------

## 10. Tentative / Open Boundaries

Two boundaries remain intentionally tentative for downstream design, not for this Charter to close.

First, visible route disclosure is currently emerging territory. This Charter allows future display of the reader's own route trace, but does not authorize a route-choice system, learning path platform, user steering surface, or user route control.

Second, planning audit should gain structured decision fields, but exact field names and storage shape belong to the Planning Audit / Observability design page. This Charter only requires that audit distinguish navigator error, memory retrieval error, source resolution error, settlement error, detour recovery failure, and route-disclosure display-boundary failure.

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

### A.1 Product positioning

`docs/product-overview.md` defines the product as a genuinely curious, self-propelled co-reading mind, not a summary engine or service-style assistant, and requires the co-reader to remain text-grounded and legible. This directly supports the Charter’s refusal to turn Memory into user-profile memory, Planning into AutoGPT-style task planning, or visible route disclosure into a control layer over the reader.

### A.2 Shared substrate and mechanism-private territory

`docs/backend-reading-mechanism.md` states that `public/book_document.json` is the only shared parsed-book truth; the paragraph layer is the stable source substrate; mechanisms may choose their own cursor semantics; current `attentional_v2` uses paragraph + char-offset cursors and inline `SourceRef`; there is no shared Anchor Bank or SourceRef registry. This supports the Charter’s `source corpus != memory` rule and the decision to keep SourceRef as inline evidence spine rather than a universal platform registry.

`docs/source-of-truth-map.md` says the workspace is repo-first and durable facts belong in canonical repo docs or state files, not chat or ad hoc tools. This supports the file-based JSON / JSONL, auditable artifact, and canonical-boundary posture.

### A.3 Current default mechanism

`docs/backend-reading-mechanisms/README.md` identifies `attentional_v2` as the current default/live mechanism and `iterator_v1` as fallback. This supports the Charter’s decision to optimize within `attentional_v2`, not to design a greenfield agent.

`docs/backend-reading-mechanisms/attentional_v2.md` defines the live mechanism as paragraph-offset cursor reading with `Navigate.choose_next_unit`, `Read`, and deterministic post-read settlement. It also defines `ReadResult` as `reading_impression`, `surfaced_reactions`, `memory_uptake_ops`, and optional `detour_need`; it states that visible reactions are persisted separately and not automatically copied into concept/thread memory. This directly supports the Charter’s Read/Planning/Memory interface contract.

### A.4 SourceCursor / SourceSpan / SourceRef

`docs/current-state.md` records the cutover from sentence traversal to paragraph-offset `SourceCursor` and `SourceSpan`, with SourceRef cutover to inline paragraph-offset `source_refs[]`. It also records settlement diagnostics and SourceRef carry-forward repair. This supports the Charter’s SourceRef-first evidence spine and the warning that runtime quality should not be overclaimed without artifact audit.

`schemas.py` defines `SourceRef` as an inline paragraph-offset source citation, not a registry entry, and defines `SourceCursor`-related continuity, `ReadUnitResult`, `StateOperation`, `DetourNeed`, `NavigateActResult`, `ConceptRegistryEntry`, `ThreadTraceEntry`, `ReflectiveItem`, `KnowledgeActivation`, and `ReactionRecordsState`. This supports the Charter’s state territory map.

### A.5 Read / Navigate / Runner / settlement

`prompts.py` makes `Navigate.choose_next_unit` choose the next readable unit, with detour mode allowed to request bounded source evidence but no external search and no future text. It also makes `Read` a reader-like call that proposes bounded `memory_uptake_ops`, only targets `active_attention / concept_registry / thread_trace`, and does not write `reflective_frames`, `reaction_records`, history, audit, or whole-object rewrites. This is the strongest project evidence for “LLM proposes; deterministic runner settles.”

`nodes.py` normalizes LLM outputs for state operations, surfaced reactions, detour needs, and navigate acts. It filters invalid operation types, requires surfaced reaction source quotes to come from the current unit, and prevents visible content from leaking internal handles. This supports the Charter’s claim that LLM output already passes through contract normalization and should remain bounded.

`state_ops.py` applies operations deterministically, merges source refs, upserts concept/thread entries, handles active_attention cooling/resolution/drop, appends reaction records, and marks reflective items superseded without mutating their statements. This supports lifecycle separation and source-ref-preserving settlement.

`runner.py` owns the live Reading Runner integration, local continuity, detour application, runtime bundle loading/saving, mechanism-private artifact persistence, and rejection of unsupported legacy state shapes. This supports the Charter’s runner ownership boundary.

### A.6 Memory stores and prompt-facing projection

`storage.py` defines mechanism-private JSON / JSONL artifacts including `active_attention.json`, `concept_registry.json`, `thread_trace.json`, `reflective_frames.json`, `knowledge_activations.json`, `reaction_records.json`, `unit_span_ledger.jsonl`, `read_audit.jsonl`, and `settlement_audit.jsonl`. This supports the Charter’s file-first infrastructure restraint.

`state_projection.py` builds bounded prompt-facing packets with active attention, concept digest, thread digest, reflective digest, source_ref digest, recent reactions, refs, and continuation capsule. This supports the Charter’s distinction between durable state and prompt-facing projection.

### A.7 Active recall / look-back / detour

`read_context.py` distinguishes `look_back`, which resolves source refs into earlier source excerpts, from `active_recall`, which retrieves concepts, threads, and reactions not already carried. This supports the Charter’s rule that active recall is memory recovery while look-back is source calibration.

`slow_cycle.py` handles surfaced reaction persistence, compatibility projection, reflective promotion, reconsolidation, and chapter consolidation, including cooling operations, promotion candidates, knowledge activation updates, and cross-chapter carry-forward. This supports the Charter’s slow-cycle dual boundary: memory consolidation plus macro carry-forward, not large planner.

### A.8 Observability / audit / evaluation

`observability.py` records read audit fields, memory uptake counts by target store, surfaced reactions, detour need, context requests, supplemental steps, and compact settlement deltas for active_attention, concept_registry, thread_trace, and reaction_records. It supports the Charter’s audit-first stance while also revealing the next gap: per-op outcome and failure reason are not yet first-class.

`docs/backend-reader-evaluation.md` defines evaluation as product-first and mechanism-agnostic, and establishes the active long-span direction as Memory Quality, Spontaneous Callback, and False Visible Integration. This supports the Charter’s separation between memory quality, callback utilization, and pollution/FVI.

------

## B. External Evidence Basis

The external sources below were used as mechanism evidence, not as systems to copy wholesale. For post-2025 sources, the stable URLs and metadata come from the provided evidence packs; live web verification was not performed in this environment.

### B.1 Generative Agents

**Source**: Joon Sung Park et al., “Generative Agents: Interactive Simulacra of Human Behavior,” 2023. Stable URL: https://arxiv.org/abs/2304.03442

Original problem: make LLM agents behave continuously in a simulated social world through memory stream, reflection, and planning.

Useful mechanism: low-level observations enter a memory stream; higher-level reflections are generated only after accumulated evidence and importance thresholds.

Supports this Charter: not every read unit should become durable reflective memory. `Read` should propose local memory intents; slow-cycle should handle second-order promotion.

Similarity: both systems need continuity across many local observations.

Difference: Generative Agents does not treat source-grounded textual evidence as a first-class requirement.

Localized borrowing: use reflection-trigger logic as slow-cycle justification, but require SourceRef-preserving promotion.

Cannot copy: social simulation reflection memory should not be copied into book-grounded content memory without source evidence.

### B.2 Mem0

**Source**: Prateek Chhikara et al., “Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory,” 2025. Stable URL: https://arxiv.org/abs/2504.19413
Docs: https://docs.mem0.ai/core-concepts/memory-operations/add

Original problem: make long-term agent memory production-ready through add/search/update/delete operations and metadata.

Useful mechanism: memory write is a pipeline involving extraction, conflict handling, storage, update, and delete.

Supports this Charter: `memory_uptake_ops` should be write intent, not final persisted object; settlement must normalize, merge, accept, reject, or defer.

Similarity: both need item identity, metadata, lifecycle operations, and auditability.

Difference: Mem0 is mainly general agent / user memory; Second Reader memory is book-source-grounded reading state.

Localized borrowing: adopt operation-centric pipeline; do not adopt vector/graph infrastructure as default.

Cannot copy: user-profile memory and vector-first retrieval do not define Second Reader’s memory ontology.

### B.3 Zep

**Source**: Preston Rasmussen et al., “Zep: A Temporal Knowledge Graph Architecture for Agent Memory,” 2025. Stable URL: https://arxiv.org/abs/2501.13956
Docs: https://help.getzep.com/graph-overview

Original problem: manage dynamic, temporally changing facts across agent sessions.

Useful mechanism: episodes, entities, facts, observations, summaries, and validity / invalidity are separated.

Supports this Charter: source corpus, reading observation, durable memory, visible trace, prior knowledge, and audit must be separate. Later correction should use supersede / invalidate rather than destructive overwrite.

Similarity: both systems need evidence-backed memory and temporal change.

Difference: Zep is graph-backed enterprise / conversation memory; Second Reader is file-based reading state.

Localized borrowing: borrow validity and evidence layering; keep JSON links and SourceRefs first.

Cannot copy: graph DB, entity graph extraction, and user summary are not current defaults.

### B.4 Letta / MemGPT

**Sources**: Charles Packer et al., “MemGPT: Towards LLMs as Operating Systems,” 2023. Stable URL: https://arxiv.org/abs/2310.08560
Letta Memory Blocks: https://docs.letta.com/guides/core-concepts/memory/memory-blocks
Letta Archival Memory: https://docs.letta.com/guides/ade/archival-memory/

Original problem: manage context-window scarcity through core vs archival memory.

Useful mechanism: always-visible memory blocks have label, description, value, and limit; archival memory is retrieved separately.

Supports this Charter: durable state, prompt-facing projection, and cold/audit artifacts must be separate. Each store should have explicit role, allowed writes, visibility, and limit.

Similarity: both need bounded context assembly.

Difference: Letta/MemGPT focus on general stateful agents and persona/user memory.

Localized borrowing: adopt lightweight store contract and prompt projection discipline.

Cannot copy: OS-style paging or persona/human blocks would overfit the wrong product.

### B.5 LangGraph Memory / LangMem

**Sources**: LangGraph Memory Concepts, https://docs.langchain.com/oss/python/concepts/memory
LangMem, https://github.com/langchain-ai/langmem

Original problem: provide framework patterns for semantic, episodic, and procedural memory, plus hot-path and background writes.

Useful mechanism: type hygiene and write-timing separation.

Supports this Charter: reaction_records / audit traces should not be mixed with semantic memory; slow-cycle consolidation is distinct from hot-path Read writing.

Similarity: both need hot-path vs slow/background memory operations.

Difference: LangGraph/LangMem are general frameworks; Second Reader has source corpus and reading path constraints.

Localized borrowing: adopt type hygiene and background consolidation; keep current runner/state_ops rather than adding manager agents.

Cannot copy: procedural prompt refinement as a live self-modifying mechanism is too risky now.

### B.6 LongMemEval and HaluMem

**Sources**: Di Wu et al., “LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory,” 2024. Stable URL: https://arxiv.org/abs/2410.10813
Ding Chen et al., “HaluMem: Evaluating Hallucinations in Memory Systems of Agents,” 2025. Stable URL: https://arxiv.org/abs/2511.03506

Original problem: evaluate long-term memory beyond final answer correctness and localize hallucinations across memory operations.

Useful mechanism: split evaluation into formation / indexing / retrieval / reading / update / QA stages.

Supports this Charter: audit should record per-op outcome and failure reason; Memory Quality should remain holistic but add stage-aware diagnosis.

Similarity: both need to know whether failure came from formation, retrieval, utilization, or output integration.

Difference: these benchmarks focus mostly on chat/agent memory, not source-span reading.

Localized borrowing: use stage-aware diagnosis, not benchmark tasks wholesale.

Cannot copy: final QA correctness is not Second Reader’s primary memory target.

### B.7 ReAct

**Source**: Shunyu Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models,” 2022 / ICLR 2023. Stable URL: https://arxiv.org/abs/2210.03629

Original problem: interleave reasoning, action, and observation so agents can correct themselves with environment feedback.

Useful mechanism: observation-grounded correction.

Supports this Charter: detour and source-skill loops should be local, bounded, and grounded in new source evidence.

Similarity: both benefit from letting observation revise the next step.

Difference: Reading Companion’s environment is source text, not a tool sandbox.

Localized borrowing: use ReAct only for bounded detour/source-evidence loops.

Cannot copy: making every read unit a ReAct action loop would overcomplicate ordinary reading.

### B.8 Plan-and-Solve and ReWOO

**Sources**: Lei Wang et al., “Plan-and-Solve Prompting,” ACL 2023. Stable URL: https://aclanthology.org/2023.acl-long.147/
Binfeng Xu et al., “ReWOO,” 2023. Stable URL: https://arxiv.org/abs/2305.18323

Original problem: reduce missing-step errors and costly observation interleaving in multi-step reasoning.

Useful mechanism: explicit plan sketches and decoupled evidence gathering.

Supports this Charter: explicit planning can be useful at chapter boundaries, hard passages, or bounded detour bundles.

Similarity: Second Reader sometimes needs boundary-level planning.

Difference: normal reading is source-order and responsive; over-planning every unit harms continuity.

Localized borrowing: allow plan sketches only at boundary / hard cases.

Cannot copy: no large planner node in the steady-state loop.

### B.9 Reflexion

**Source**: Noah Shinn et al., “Reflexion: Language Agents with Verbal Reinforcement Learning,” 2023. Stable URL: https://arxiv.org/abs/2303.11366

Original problem: help agents learn from trial feedback through verbal reflection stored between episodes.

Useful mechanism: reflection belongs between episodes, not every step.

Supports this Charter: slow-cycle may summarize failure/recovery patterns, but strategy reflection must not pollute source-grounded content memory.

Similarity: both need learning from accumulated behavior.

Difference: Second Reader’s primary memory is book-grounded, not task-strategy memory.

Localized borrowing: use reflection as slow-cycle audit / carry-forward signal.

Cannot copy: self-learning policy memory or prompt refinement should remain deferred.

### B.10 HTN / Options / MAXQ

**Sources**: Kutluhan Erol, “Hierarchical Task Network Planning,” 1996. Stable URL: http://hdl.handle.net/1903/5810
Richard Sutton, Doina Precup, Satinder Singh, “Between MDPs and semi-MDPs,” 1999. Stable DOI: https://doi.org/10.1016/S0004-3702(99)00052-1
Thomas Dietterich, “Hierarchical Reinforcement Learning with the MAXQ Value Function Decomposition,” 2000. Stable DOI: https://doi.org/10.1613/jair.639

Original problem: handle long-horizon control through hierarchy, temporal abstraction, and controller/worker separation.

Useful mechanism: micro / meso / macro planning layers and temporally extended options.

Supports this Charter: Navigate is micro navigation; detour is meso path deviation; slow-cycle is macro carry-forward; runner is deterministic executor.

Similarity: both need layered decisions.

Difference: these are formal planning/RL theories, not source-grounded reading systems.

Localized borrowing: adopt hierarchy language, not formal planner machinery.

Cannot copy: no formal HTN planner or RL policy in current reading loop.

### B.11 Information Foraging and Exploratory Search

**Sources**: Peter Pirolli and Stuart Card, “Information Foraging,” 1999. Stable DOI: https://doi.org/10.1037/0033-295X.106.4.643
Gary Marchionini, “Exploratory Search: From Finding to Understanding,” 2006. Stable URL: https://cacm.acm.org/research/exploratory-search/
Ryen White and Resa Roth, “Exploratory Search: Beyond the Query-Response Paradigm,” 2009. Stable DOI: https://doi.org/10.2200/S00174ED1V01Y200901ICR003

Original problem: explain how people navigate information spaces through value, cost, scent, and exploratory understanding.

Useful mechanism: stay / leave decisions depend on information scent and expected gain.

Supports this Charter: mainline continuity and detour value should be evaluated together; detour should not be novelty chasing.

Similarity: choosing next source unit is closer to information navigation than task decomposition.

Difference: book reading has stronger author-order discipline than open web search.

Localized borrowing: use value / cost / scent language but keep source-order as default.

Cannot copy: free exploratory search should not replace mainline reading.

### B.12 Rereading and Metacomprehension

**Sources**: Katherine Rawson, John Dunlosky, Keith Thiede, “The rereading effect,” 2000. Stable DOI: https://doi.org/10.3758/BF03209348
John Dunlosky and Amanda Lipko, “Metacomprehension,” 2007. Stable DOI: https://doi.org/10.1111/j.1467-8721.2007.00509.x

Original problem: understand when rereading improves comprehension monitoring and why readers misjudge understanding.

Useful mechanism: rereading is valuable as calibration, not as automatic repetition.

Supports this Charter: look-back should be triggered by source-evidence need, conflict, unresolved reference, or calibration gap.

Similarity: both involve deciding when to revisit earlier text.

Difference: human metacomprehension studies do not directly define LLM trigger rules.

Localized borrowing: define look-back as calibration move.

Cannot copy: no blanket “if uncertain, reread” rule.

### B.13 Adaptive Navigation Support, Learner Agency, and Route Disclosure Evaluation

**Sources**: Peter Brusilovsky, “Adaptive Hypermedia,” 2001. Stable DOI: https://doi.org/10.1023/A:1011143116306
Peter Brusilovsky, “Adaptive Navigation Support in Educational Hypermedia,” 2003. Stable DOI: https://doi.org/10.1111/1467-8535.00345
Michelle Deschênes, “Recommender systems to support learners’ Agency,” 2020. Stable DOI: https://doi.org/10.1186/s41239-020-00219-w
Yanjin Long and Vincent Aleven, “Open Learner Model,” 2017. Stable DOI: https://doi.org/10.1007/s11257-016-9186-6
Chun-Hua Tsai and Peter Brusilovsky, “Controllability and Explainability in a Social Recommender System,” 2021. Stable DOI: https://doi.org/10.1007/s11257-020-09281-5
Sean McNee, John Riedl, Joseph Konstan, “Being Accurate Is Not Enough,” 2006. Stable DOI: https://doi.org/10.1145/1125451.1125659
Pearl Pu and Li Chen, “A user-centric evaluation framework for recommender systems,” 2011. Stable DOI: https://doi.org/10.1145/2043932.2043962

Original problem: support navigation, explanation, usefulness, trust, and agency.

Useful mechanism: adaptive navigation literature can inform how a future route-disclosure surface stays low-interruption and source-grounded; evaluation should go beyond accuracy.

Supports this Charter: internal navigation and visible route disclosure must be separated; route disclosure is legibility surface, not route steering.

Similarity: both involve guiding a reader/learner through information.

Difference: Second Reader is not a full tutoring system and does not have mastery model or prerequisite graph.

Localized borrowing: use only route-disclosure boundary lessons; do not create user route control.

Cannot copy: no full learner model, course sequencing engine, or learning path recommender by default.

### B.14 ToT / LATS and search-based deliberation

**Sources**: Shunyu Yao et al., “Tree of Thoughts,” 2023. Stable URL: https://arxiv.org/abs/2305.10601
Andy Zhou et al., “Language Agent Tree Search,” 2023. Stable URL: https://arxiv.org/abs/2310.04406

Original problem: improve hard reasoning through branching, evaluation, backtracking, or MCTS-like search.

Useful mechanism: deliberate search can help hard passages or multiple interpretation comparisons.

Supports this Charter as boundary evidence: these methods are too costly and value-function-dependent to be the default reading loop.

Similarity: difficult interpretive moments may benefit from structured alternatives.

Difference: ordinary book reading prioritizes continuity, source order, latency, and legibility.

Localized borrowing: reserve for optional deep-dive / hard-passage cases later.

Cannot copy: no default ToT / LATS / MCTS over every next-unit choice.

------

## C. Simplicity and Universality Check

This Charter satisfies Simplicity and Universality in the following ways.

It prioritizes understanding and tightening the existing `attentional_v2` structure rather than inventing a new agent architecture.

It avoids unnecessary new stores. The first move is to define roles, allowed writes, visibility, lifecycle, and audit use for existing stores.

It avoids unnecessary planner nodes. Planning is defined as reading-path control distributed across Navigate, Read intent, runner settlement, detour policy, and slow-cycle carry-forward.

It does not treat storage backend as mechanism essence. JSON / JSONL remains the default because current problems are semantic contract problems, not backend capacity problems.

It preserves source-grounded auditability by making SourceRef, accepted source spans, unit ledger, read audit, and settlement audit shared constraints.

It supports later detailed designs without binding them to one implementation shape. It defines boundaries and principles, not full page designs.

Remaining complexity risks:

- planning audit could expand into over-recording if candidate / rejected alternatives are not kept compact;
- visible route disclosure could quietly replace internal navigation if not kept as display-only route disclosure;
- slow-cycle could become an implicit macro-planner if outputs are not split into consolidation and carry-forward;
- prior knowledge activation could pollute source-grounded memory if warrant and source truth are not separated;
- vector/graph infrastructure could be introduced before metadata, SourceRef, and lifecycle contracts are stable.

------

## D. Source Usage List

| External source                       | Authors / Organization                        | Year      | Stable URL                                                   | Used for                                          | Support type            |
| ------------------------------------- | --------------------------------------------- | --------- | ------------------------------------------------------------ | ------------------------------------------------- | ----------------------- |
| Generative Agents                     | Joon Sung Park et al.                         | 2023      | https://arxiv.org/abs/2304.03442                             | Observation → reflection, slow-cycle boundary     | Direct / Analogical     |
| Mem0 paper                            | Prateek Chhikara et al.                       | 2025      | https://arxiv.org/abs/2504.19413                             | Operation-centric memory pipeline                 | Direct                  |
| Mem0 memory operations docs           | Mem0                                          | 2025–2026 | https://docs.mem0.ai/core-concepts/memory-operations/add     | Add / search / update / delete contract           | Direct                  |
| Zep temporal memory paper             | Preston Rasmussen et al.                      | 2025      | https://arxiv.org/abs/2501.13956                             | Temporal validity, evidence-backed memory         | Direct / Boundary       |
| Zep graph / facts / observations docs | Zep                                           | 2025–2026 | https://help.getzep.com/graph-overview                       | Episodes / facts / observations split             | Direct                  |
| MemGPT                                | Charles Packer et al.                         | 2023      | https://arxiv.org/abs/2310.08560                             | Core vs archival memory boundary                  | Boundary                |
| Letta Memory Blocks                   | Letta                                         | 2025–2026 | https://docs.letta.com/guides/core-concepts/memory/memory-blocks | Lightweight memory block contract                 | Direct                  |
| Letta Archival Memory                 | Letta                                         | 2025–2026 | https://docs.letta.com/guides/ade/archival-memory/           | Prompt-facing vs archival state                   | Direct / Boundary       |
| LangGraph Memory Concepts             | LangChain                                     | 2025–2026 | https://docs.langchain.com/oss/python/concepts/memory        | Semantic / episodic / procedural split            | Direct / Analogical     |
| LangMem                               | LangChain                                     | 2025–2026 | https://github.com/langchain-ai/langmem                      | Hot-path vs background memory writes              | Analogical              |
| LongMemEval                           | Di Wu et al.                                  | 2024      | https://arxiv.org/abs/2410.10813                             | Stage-aware memory evaluation                     | Direct                  |
| HaluMem                               | Ding Chen et al.                              | 2025      | https://arxiv.org/abs/2511.03506                             | Operation-level memory hallucination              | Analogical / Frontier   |
| ReAct                                 | Shunyu Yao et al.                             | 2022      | https://arxiv.org/abs/2210.03629                             | Local detour / observation-grounded correction    | Direct / Analogical     |
| Plan-and-Solve                        | Lei Wang et al.                               | 2023      | https://aclanthology.org/2023.acl-long.147/                  | Boundary-level planning                           | Direct / Boundary       |
| ReWOO                                 | Binfeng Xu et al.                             | 2023      | https://arxiv.org/abs/2305.18323                             | Bounded detour bundle / placeholder planning      | Analogical              |
| Reflexion                             | Noah Shinn et al.                             | 2023      | https://arxiv.org/abs/2303.11366                             | Episode-boundary reflection                       | Direct / Boundary       |
| HTN Planning                          | Kutluhan Erol                                 | 1996      | http://hdl.handle.net/1903/5810                              | Micro / meso / macro decomposition                | Analogical              |
| Options Framework                     | Richard Sutton, Doina Precup, Satinder Singh  | 1999      | https://doi.org/10.1016/S0004-3702(99)00052-1                | Detour as temporally bounded option               | Analogical              |
| MAXQ                                  | Thomas Dietterich                             | 2000      | https://doi.org/10.1613/jair.639                             | Controller / worker separation                    | Analogical              |
| Information Foraging                  | Peter Pirolli, Stuart Card                    | 1999      | https://doi.org/10.1037/0033-295X.106.4.643                  | Value / cost / scent for navigation               | Direct / Analogical     |
| Exploratory Search                    | Gary Marchionini                              | 2006      | https://cacm.acm.org/research/exploratory-search/            | Open-ended understanding and detour boundary      | Background / Analogical |
| Exploratory Search book               | Ryen White, Resa Roth                         | 2009      | https://doi.org/10.2200/S00174ED1V01Y200901ICR003            | Exploration vs lookup distinction                 | Background              |
| The rereading effect                  | Katherine Rawson, John Dunlosky, Keith Thiede | 2000      | https://doi.org/10.3758/BF03209348                           | Look-back as calibration                          | Direct / Analogical     |
| Metacomprehension                     | John Dunlosky, Amanda Lipko                   | 2007      | https://doi.org/10.1111/j.1467-8721.2007.00509.x             | Comprehension monitoring limits                   | Direct / Analogical     |
| Adaptive Hypermedia                   | Peter Brusilovsky                             | 2001      | https://doi.org/10.1023/A:1011143116306                      | Adaptive navigation boundary                      | Analogical              |
| Adaptive Navigation Support           | Peter Brusilovsky                             | 2003      | https://doi.org/10.1111/1467-8535.00345                      | Route disclosure as navigation scaffold           | Direct / Analogical     |
| Learner Agency review                 | Michelle Deschênes                            | 2020      | https://doi.org/10.1186/s41239-020-00219-w                   | Agency-preserving route disclosure                | Direct / Analogical     |
| Open Learner Model                    | Yanjin Long, Vincent Aleven                   | 2017      | https://doi.org/10.1007/s11257-016-9186-6                    | Explainable support without full control transfer | Analogical              |
| Controllability and Explainability    | Chun-Hua Tsai, Peter Brusilovsky              | 2021      | https://doi.org/10.1007/s11257-020-09281-5                   | Route-disclosure controllability                  | Direct / Analogical     |
| Being Accurate Is Not Enough          | Sean McNee, John Riedl, Joseph Konstan        | 2006      | https://doi.org/10.1145/1125451.1125659                      | Route-disclosure evaluation beyond accuracy       | Direct                  |
| ResQue                                | Pearl Pu, Li Chen                             | 2011      | https://doi.org/10.1145/2043932.2043962                      | Usefulness / trust / user-centric evaluation      | Direct                  |
| Tree of Thoughts                      | Shunyu Yao et al.                             | 2023      | https://arxiv.org/abs/2305.10601                             | Search-based deliberation guardrail               | Boundary / Negative     |
| Language Agent Tree Search            | Andy Zhou et al.                              | 2023      | https://arxiv.org/abs/2310.04406                             | MCTS-style planning boundary                      | Boundary / Negative     |
