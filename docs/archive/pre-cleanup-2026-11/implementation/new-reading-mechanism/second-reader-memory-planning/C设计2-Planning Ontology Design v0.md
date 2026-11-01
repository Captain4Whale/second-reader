# Planning Ontology Design v0

## 1. Scope and Purpose

本页定义 Second Reader / Reading Companion 的 **Planning Ontology v0**。

它继承 P0 Shared Memory–Planning Mechanism Charter 的边界：Planning 不是通用任务规划，不是 AutoGPT-style task planning，而是 **source-grounded reading path planning / attention scheduling / navigation support**。它服务持续读书过程中的下一步路径控制：下一步读哪里、是否继续主线、是否需要 active recall、是否 look-back、是否 detour、哪些关注点 carry forward，以及是否把内部路线决定保留为 `reading_route_trace`，未来可能通过 `visible_route_disclosure` 展示。

本页也继承 Memory Ontology v0 的 memory 边界：Planning 只能通过 bounded、typed、source-ref-preserving memory projections 使用 memory；Planning 不拥有 durable memory，不直接写 memory，不把 visible reaction、audit trace、evaluation evidence 或 prompt packet 当成 memory 或 planning state。

本页只设计 Planning Ontology。它为后续 Navigation Policy、Detour / Look-back / Active Recall Policy、Visible Reading Route Surface Boundary、Slow-cycle / Macro-planning、Planning Audit、Planning Evaluation、Memory Retrieval / Utilization 提供基础。本页不是代码实现路线，不是外部文献综述，不是新 agent architecture proposal，也不替代当前 `attentional_v2`。

本设计的目标是收紧现有 Navigate / Read / Reading Runner / slow-cycle 结构，而不是新增大型 planner。

------

## 2. Current Implementation Understanding

当前项目的默认阅读机制是 `attentional_v2`；`iterator_v1` 保留为 explicit fallback / legacy-compatible path。`attentional_v2` 的核心不是 fixed section traversal，而是 paragraph-offset source cursor、`Navigate.choose_next_unit`、`Read`、Reading Runner deterministic settlement 与 chapter/session slow-cycle。

### 2.1 Source corpus / book document

共享 source truth 是 `public/book_document.json`。它包含 canonical chapter order、paragraph records、sentence records 和 locators。paragraph layer 是当前稳定 source substrate；sentence layer 仍可用于 legacy、eval、detour compatibility，但不再是当前 mainline reading lattice。

这意味着：source corpus 是被读对象，不是 plan，也不是 memory。Planning 可以引用 source substrate、preview、source refs 和 accepted spans，但不能把 “书本已经被 parse 出来” 当成系统已经规划或记住了它。

### 2.2 SourceCursor / SourceSpan / accepted unit

当前主线 cursor 使用 paragraph + char-offset：

```text
SourceCursor:
  chapter_id
  chapter_ref
  paragraph_index
  char_offset
```

`SourceSpan` 是 end-exclusive `[start_cursor, end_cursor)`。`Navigate.choose_next_unit` 接收从当前 cursor 开始的 adaptive paragraph-offset preview，返回 `end_anchor_text`。Reading Runner 解析 anchor，形成 accepted `SourceSpan`，调用 `Read`，settle 后推进 cursor，并写入 `unit_span_ledger.jsonl`。

Ontology 上，`SourceCursor / SourceSpan / accepted unit` 是 **reading locus** 与 **coverage fact**，不是 semantic memory，也不是 plan 本身。

### 2.3 Survey / reading_plan orientation

当前 `survey` 是 structural orientation。它会对 chapter 做 `chapter_zone` classification，并持久化 `reading_plan`，例如 `body_first`、`mainline_chapter_ids`、`deferred_chapter_ids`。它帮助 Reading Runner 先读 main body，再读 deferred support chapters。

它不做隐藏全文阅读，不产生 visible reactions，不写 durable reading memory，也不让 `Navigate` 拥有 book-level chapter ordering。

Ontology 上，`survey / reading_plan` 是 **macro orientation / scheduling prior**，不是 full book plan，不是 memory consolidation，也不是 visible route disclosure。

### 2.4 Navigate.choose_next_unit

`Navigate.choose_next_unit` 是当前唯一 live next-coverage-unit selector。主线 unit selection 与 active detour localization 都在同一个 entrypoint 下，只是 mode 不同。

在 mainline mode，它从 visible preview 中选择下一 readable unit，返回 exact `end_anchor_text`。在 detour mode，它可以选择 source-grounded already-read unit、请求 bounded source-evidence skill，或 honest defer。当前 legal first-phase skills 是 `source_map_overview`、`source_scope_drilldown`、`source_window_fetch`；它们只提供 source evidence，不做 semantic relevance judgment，不读未来文本，不访问外部网络。

Ontology 上，`Navigate.choose_next_unit` 是 **source-grounded next-unit selector / micro-planning navigator**；在 detour mode 中，它也是 **detour localizer**。它不是 global planner，不是 route-action layer，不是 visible route disclosure owner，不是 memory writer。

### 2.5 Read / detour_need

`Read` 是 current accepted source unit 的 reader-like interpretation call。当前输出：

```text
reading_impression
surfaced_reactions[]
memory_uptake_ops[]
detour_need?
```

`reading_impression` 是 temporary read-after impression，不是 durable memory。`surfaced_reactions` 是 visible reaction intent。`memory_uptake_ops` 是 bounded write intent，目标只允许 `active_attention / concept_registry / thread_trace`。`detour_need` 是 Planning intent：它表达当前阅读产生了离开主线的需要，但不定位 detour target，也不执行 detour。

Ontology 上，`Read` 提出 memory intent 与 planning intent；Reading Runner 才 settle。

### 2.6 Reading Runner settlement

Reading Runner 负责 deterministic settlement：

```text
resolve end_anchor_text
→ construct accepted SourceSpan
→ invoke Read
→ bind source refs / normalize operations
→ apply memory uptake through state_ops
→ persist surfaced reactions
→ write audit
→ append unit span ledger
→ update detour continuity
→ advance cursor
```

普通 forward progression 不再问 LLM。没有 replacement `forward` action；继续主线是 deterministic default。

Ontology 上，Runner 是 **executor / settlement authority**，不是 planner，也不是 memory semantic author。它把 LLM proposals 变成 accepted state、trace 与 cursor movement。

### 2.7 local_continuity / mainline_cursor / detour state

当前 `local_continuity` 已经持有 Planning v0 所需的最小 runtime continuity：

```text
mainline_cursor
reading_queue_stage
active_detour_id
active_detour_need
detour_trace
```

`mainline_cursor` 保留主线恢复点。`active_detour_need` 是当前 open detour obligation。`detour_trace` 记录 detour id、origin cursor、target hint、status。当前 status vocabulary 是 `open / resolved / abandoned`。

Ontology 上，`local_continuity` 是 Planning state 的 v0 起点，不是 memory store，也不是 audit dump。`local_continuity` is the v0 planning-state carrier, not a guarantee that future Planning state will never need additional bounded planning obligation records；但新增 store 必须由后续 Policy / Audit 的真实需求证明。

### 2.8 active_recall / look_back

当前 `read_context.py` 区分两类 supplemental context：

- `active_recall` 从 concept / thread / reaction records 中取回尚未 carry 的 reading state；
- `look_back` 根据 SourceRef / SourceSpan 回到 earlier source excerpts。

Ontology 上：

```text
active_recall = memory recovery
look_back = source calibration
detour = planning path deviation
```

三者不能互相替代。

### 2.9 state_projection / navigation context

`state_projection.py` 构造 bounded `state_packet.v1`、carry-forward context 与 navigation context。它包含 active attention digest、concept digest、thread digest、reflective digest、source_ref digest、recent reactions、continuation capsule 等。

Ontology 上，这些是 prompt-facing / navigation-facing projections，不是 authoritative state。Planning 可以消费它们，但不能把它们当完整 memory 或完整 planning state。

### 2.10 slow_cycle

当前 slow-cycle 处理 surfaced reaction persistence / compatibility projection / reflective promotion / reconsolidation / chapter consolidation / cooling / promotion candidates / knowledge activation updates / cross-chapter carry-forward。

Ontology 上，slow-cycle 同时涉及两类输出：

```text
Memory consolidation:
  reflective promotion
  reconsolidation
  knowledge activation status update
  memory cooling / resolve / supersede

Macro-planning / carry-forward:
  next chapter/session focus
  unresolved obligations
  carried active_attention
  resolved / abandoned detour continuity
```

Slow-cycle 不应成为 general planner、policy learner、prompt self-refiner 或 book-route optimizer。

### 2.11 read_audit / settlement_audit / navigation trace

当前 `read_audit.jsonl` 记录 unit source span、carry-forward refs、context request、supplemental refs、stop reason、budget exhaustion、reading impression、surfaced reactions、memory uptake ops、detour_need。`settlement_audit.jsonl` 记录 memory op counts、target-store distribution、active_attention / concept_registry / thread_trace / reaction_records compact deltas。`NavigateActTraceEntry` schema 已存在，可表达 decision、selection_mode、reason、skill request/result、budget state 等。

Ontology 上，这些是 diagnostic artifacts。它们服务 audit / evaluation，不默认进入 runtime planning context。

### 2.12 surfaced reactions / prior_link / outside_link / search_intent

当前 persisted visible reactions 来自 `Read.surfaced_reactions[]`，可带 `prior_link / outside_link / search_intent`。这些是 visible reading trace 的 surfaced semantics，不是成熟 visible route surface object。

`prior_link` 可支持 callback / continuity evidence；`outside_link` 可记录外部联想；`search_intent` 可表达用户可见的 follow-up curiosity。但它们不自动改变 navigation state，不自动改变 memory state，也不等于 visible route disclosure。

### 2.13 Runtime-artifact evidence boundary

本轮可读取 GitHub 文档与代码，且可读取 repo 文档中记录的运行诊断摘要。但没有逐行打开真实运行目录中的 `read_audit.jsonl / settlement_audit.jsonl / unit_span_ledger.jsonl / detour_trace / active_attention.json / concept_registry.json / thread_trace.json / reaction_records.json` 作为 runtime-row audit。

因此本文区分：

```text
architecture-level evidence:
  docs and code architecture

contract-level evidence:
  schema, prompt, state_ops, projection, observability contracts

assessment-level inference:
  P0 / Planning Assessment / Memory Ontology / Memory Assessment conclusions

runtime-artifact evidence:
  本轮未直接逐行验证，不做真实运行质量断言
```

------

## 3. Planning Ontology Core Definition

Reading Companion 中的 **Planning** 是：

> 一套 source-grounded、bounded、lightweight 的阅读路径控制与注意力调度机制。它基于当前 reading locus、visible source preview、mainline continuity、active detour state，以及来自 Memory Ontology 授权的 bounded typed memory projections，决定下一步系统应该读哪里、是否继续主线、是否需要 memory recovery、是否需要 source calibration、是否进入或退出 detour、哪些关注点应 carry forward，以及是否把内部路线决定保留为结构化 `reading_route_trace`，供未来可能的 `visible_route_disclosure` 使用。

这个定义有几个关键含义。

第一，Planning 不是 AutoGPT-style task planning。它不把读书建模成外部任务拆解，不生成完整执行计划，不调用任意工具完成外部目标，不建立 full planner-executor architecture。

第二，Planning 更准确地说是：

```text
source-grounded reading path planning
+ attention scheduling
+ navigation support
```

它的对象是 source path、attention、continuity、detour、recall、look-back、macro carry-forward 与 route trace preservation，而不是 “完成任务”。

第三，Planning 与 Navigation 的关系是：Planning 是 ontology territory；Navigation 是当前主要执行表面。`Navigate.choose_next_unit` 是 Planning 在 micro layer 的具体 selector。

第四，Planning 与 Memory 的关系是：Planning 使用 Memory，但不拥有 Memory。Planning 只消费 bounded typed source-ref-preserving memory projections，不能直接读取完整 durable stores，不能写 memory，不能把 prompt packet、visible reaction、audit 或 evaluation result 变成 memory。

第五，Planning 与 visible route disclosure 的关系是：internal navigation 是系统下一步实际读哪里；visible route disclosure 未来只解释 Second Reader 已经做了什么或正在做什么。它不是 route-choice system，也不是 user control surface。

第六，Planning 与 Audit / Evaluation 的关系是：audit 记录 planning behavior；evaluation 判断 planning quality。两者都不是 runtime planning state。

明确排除：

```text
source corpus ≠ plan
reading memory ≠ plan
prompt packet ≠ planning state
visible reaction ≠ visible route disclosure
visible route disclosure ≠ internal navigation decision
audit trace ≠ runtime planning context
evaluation evidence ≠ planning state
planning state ≠ memory state
```

------

## 4. Planning Territory Map

| Territory                                     | Ontology definition                                          | Boundary rule                                                |
| --------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Source corpus                                 | `book_document.json` 中的 book substrate：chapters、paragraphs、sentences、locators | 可被读、预览、引用、look-back；不是 plan，不是 memory        |
| Reading locus / source cursor / accepted unit | 当前 reading position、`SourceCursor`、accepted `SourceSpan`、unit ledger | Runner-owned coverage/resume fact；不是 semantic memory，也不是 visible route disclosure |
| Reading memory projection                     | active_attention / concept / thread / reflective / reaction / knowledge activation 的 bounded projection | Planning 可消费；projection 不是 authoritative memory        |
| Planning state                                | 当前 path-control obligations，例如 `mainline_cursor / reading_queue_stage / active_detour_need / detour_trace` | Lightweight runtime state；不与 memory state 合并            |
| Navigation decision                           | 一次 next-unit 选择、skill request 或 detour defer           | LLM proposes；Runner resolves / settles                      |
| Detour state                                  | 暂时离开 mainline 的 open path deviation obligation          | 一旦选中 detour unit，也走同一 read loop；不是 hidden supplemental fetch |
| Look-back / source calibration move           | 回到 earlier source excerpt 以校准证据                       | 不等于 memory recall；不自动改变 reading path                |
| Active recall / memory recovery move          | 从 stored reading state 取回未 carry 的 concept/thread/reaction | 不等于 source verification；不自动写 memory                  |
| Slow-cycle macro carry-forward                | chapter/session boundary 选择下一阶段 focus / obligations    | 与 memory consolidation 相交，但不等于 memory consolidation  |
| Future visible reading route surface          | 未来可能展示 Second Reader 自己的 route trace、detour、look-back、restore 的产品 surface | 可引用 source/memory/planning rationale；不创建 choices、accept/reject states 或 navigation transitions |
| Visible reaction                              | 用户可见的 reading-time thought / mark                       | 可作为 trace/evidence；不是 visible route disclosure，不自动成为 memory |
| Audit trace                                   | read / settlement / unitization / navigation diagnostic rows | 供 diagnosis/eval；默认不进入 prompt                         |
| Evaluation evidence                           | probe snapshots、judge reports、benchmark summaries          | 判断机制质量；不是 runtime state                             |

------

## 5. Planning Object Ontology

本页中关于 `status / lifecycle` 的描述只定义 ontology-level semantic boundary：它们说明 Planning 对象状态在语义上大致意味着什么；具体状态机、字段名、合法转移与 audit schema 留给后续 Detour / Look-back / Active Recall Policy 和 Planning Audit / Observability Design。

### 5.1 `survey / reading_plan orientation`

`survey / reading_plan` 的 role 是 structural orientation。它根据 chapter order、headings、openings、closings 和 chapter sample 对章节做 narrow structural classification，并形成 reading queue orientation，例如 main body first、support material deferred。

它不是隐藏阅读，不是 full book route optimizer，不是 durable memory，也不是 visible route disclosure。

Admission rule：当一个 book / run 开始，或当 source corpus 的 chapter-level structure 需要形成默认 reading order 时产生。State owner 是 survey + Reading Runner；Runner 消费 plan，`Navigate` 不拥有 book-level chapter ordering。

Source-grounding requirement：只能使用 source corpus 的 structural sample 与 chapter metadata，不从未来正文形成 interpretive conclusions。Memory dependency：原则上不依赖 reading memory；它可以作为 macro orientation，但不能基于未读 memory 作推断。

Prompt / context visibility：可作为 runner scheduling context 或 navigation background，但不应作为 hidden source reading。User visibility：v0 默认不作为 visible route disclosure 展示；若未来展示，应归 Visible Reading Route Surface Boundary。

Lifecycle：`ready / active / deferred / drained` 等状态表示 scheduling status，不表示 source truth 或 memory truth。

Audit / evaluation use：可用于检查 support chapters 是否被合理 deferred、main body continuity 是否被维护。Complexity caution：最容易被误用成 “系统已经粗读全书并知道该怎么读”。v0 明确：它只是 orientation。

### 5.2 `Navigate.choose_next_unit`

Object role：当前唯一 source-grounded next-unit selector。它在 mainline mode 中选择下一 readable unit；在 active detour mode 中定位 detour unit、请求 bounded source-evidence skill，或 defer detour。

Not this：不是 global planner，不是 full router，不是 `Navigate.route` 的继任者，不是 visible route disclosure generator，不是 memory mutator，不是外部工具 agent。

Admission / creation rule：每次 Reading Runner 需要下一个 accepted unit 时调用。State owner：LLM 提出 act；Runner 负责 skill dispatch、anchor resolution、fallback、accepted span construction、audit 与 cursor advancement。

Source-grounding requirement：mainline 只从 visible preview 选择，返回 exact `end_anchor_text`；detour 只能使用 already-read evidence 或 allowed source skills，不读未来 text，不用 external web search。

Memory dependency：只能使用 bounded navigation context，包括 active_attention digest、concept/thread digest、reflective digest、recent reactions、source_ref digest、continuation capsule。它不能直接读完整 memory stores。

Prompt visibility：显式进入 Navigator prompt。User visibility：默认不可见；若 decision 被解释给用户，必须经 Visible Reading Route Surface Boundary 重新表达为 display-only route disclosure，而不是暴露 internal trace 或创建 user approval state。

Lifecycle：一次 call 产生一个 `choose_unit / request_skill / defer_detour` act。act 不是 durable plan；其 settlement 结果才改变 cursor 或 detour continuity。

Audit / evaluation use：核心用于 Navigation Groundedness、Reading Path Quality、Mainline Continuity、Detour Precision、Overplanning / Thrashing。Complexity caution：最容易被误用成万能 planner。v0 结论是：保持它为 next-unit selector + detour localizer。

### 5.3 `NavigateActResult / NavigateActTraceEntry`

Object role：`NavigateActResult` 是一次 bounded navigation act 的 normalized result；`NavigateActTraceEntry` 是 compact diagnostic trace。它们记录 decision、selection_mode、reason、end_anchor_text、source_span_id、skill_request/result、resolution、budget_state、error 等。

Not this：不是 planning state，不是 user-facing rationale，不是 chain-of-thought，不是 memory。

Admission rule：每次 Navigate act 或 detour skill loop step 产生。State owner：Navigate output 被 nodes normalization 处理，Runner/observability 写入 trace/audit。

Source-grounding requirement：`choose_unit` 必须能回到 preview / source evidence；`request_skill` 必须说明具体 missing evidence；`defer_detour` 必须有 bounded reason。

Memory dependency：可记录使用了哪些 refs，但不能把 trace 当 memory。

Prompt visibility：同一 Navigate act loop 内的 skill results 可作为 evidence 回传；历史 trace默认不进入后续 prompt。User visibility：不可见，除非后续 Visible Reading Route Surface Boundary 提供 concise rationale。

Lifecycle：per decision append / compact；无 open/closed semantic。Audit / evaluation use：用于区分 navigation error、source resolution error、skill budget failure、detour defer failure。Complexity caution：不要把 trace 做成 hidden long planner context。

### 5.4 `SourceCursor / SourceSpan / accepted unit`

Object role：Reading locus。`SourceCursor` 表示当前 source position；`SourceSpan` 表示被 Runner 接受并交给 `Read` 的 exact unit；accepted unit 是一次正式阅读的 source evidence boundary。

Not this：不是 memory，不是 plan，不是 visible route disclosure，不是 audit explanation。

Admission rule：cursor 初始化于 chapter / source start；`Navigate` 返回 `end_anchor_text` 后，Runner 解析成 accepted `SourceSpan`。State owner：Runner。

Source-grounding requirement：必须绑定到 paragraph-offset source coordinates；accepted unit 必须可回到 source text。

Memory dependency：无。Prompt visibility：current unit 进入 `Read` prompt；cursor/preview进入 Navigate prompt。User visibility：可作为 reading locus / highlight / source anchor 展示，但不是 visible route disclosure。

Lifecycle：`candidate preview → accepted unit → read → settled → ledgered → cursor advanced`。Audit / evaluation use：Reading Path Quality、coverage、resume、source resolution、note/reaction source matching。Complexity caution：不要把 source coverage fact误当成 semantic understanding。

### 5.5 `local_continuity`

Object role：Planning state v0 的主承载。它表达当前 path-control continuity，包括 mainline recovery、queue stage、active detour pointer、detour trace。

Not this：不是 durable semantic memory，不是 full planning store，不是 audit log，不是 user profile。

Admission rule：runtime bootstrap 初始化；Runner 在 cursor movement、chapter scheduling、detour open/resolve/abandon 时更新。State owner：Reading Runner。

Source-grounding requirement：其 cursor、detour origin 与 target hints 应可回到 source locus。Memory dependency：可以引用 memory-derived focus，但不储存 semantic memory payload。

Prompt visibility：通过 navigation context 或 detour_context bounded projection 进入 prompt。User visibility：默认不可见；可间接影响 visible progress/status。

Lifecycle：`mainline / deferred_support / active_detour / restored / reconstructed` 等表示 runtime continuity，不表示理解状态。Audit / evaluation use：Mainline Continuity、Detour Recovery、resume quality。Complexity caution：不要把它扩展成大型 planning manager store。v0 暂不新增 planning store。

### 5.6 `mainline_cursor`

Object role：source-order mainline 的恢复点与默认 forward baseline。

Not this：不是用户目标，不是 visible route disclosure，不是阅读理解 state。

Admission rule：Runner 初始化并在每个 settled accepted unit 后推进；detour 打开时保留为 restore point。State owner：Runner。

Source-grounding requirement：必须是 source cursor / shared cursor projection。Memory dependency：无。

Prompt visibility：active detour mode 下可进入 context，帮助恢复主线。User visibility：可作为 reading locus 显示。

Lifecycle：`current / advanced / restored`。Audit / evaluation use：mainline jump detection、detour recovery、coverage continuity。Complexity caution：不要让 visible route disclosure 或 detour 静默改写 mainline_cursor。

### 5.7 `active_detour_need`

Object role：一个 open planning obligation，表示当前阅读产生了暂时离开 mainline 的需要。

Not this：不是 detour target，不是 source excerpt，不是 memory retrieval request，不是 visible route disclosure。

Admission rule：由 `Read.detour_need` 提出；Runner 写入 `local_continuity`。State owner：Read proposes；Runner settles；Navigate consumes。

Source-grounding requirement：必须来自当前 accepted unit 的 reading need，包含 reason 与 target_hint。Memory dependency：可以由 memory projection参与判断，但不能仅凭 theme association 打开。

Prompt visibility：active detour mode 中进入 Navigate prompt。User visibility：默认不可见；未来可能被保留为 visible route disclosure candidate，但不创建 route choice。

Lifecycle：`open → resolved / abandoned / deferred / restored`。当前 schema 支持 open/resolved/abandoned；`deferred` 主要是 Navigate act decision，不一定是 state status。Audit / evaluation use：Detour Precision、Recovery Quality、Over-search / Thrashing。Complexity caution：最容易被误用成“有趣关联就跳转”。

### 5.8 `detour_trace`

Object role：lightweight path-deviation continuity record。记录 detour id、origin cursor、origin target hint、status。

Not this：不是 full audit log，不是 chain-of-thought，不是 source evidence bundle。

Admission rule：Runner 在 open detour_need settle 时 append；在 resolved / abandoned 时更新。State owner：Runner / local_continuity。

Source-grounding requirement：origin cursor 与 target hint 应 source-grounded。Memory dependency：可引用 memory ref 作为 reason，但不储存 memory payload。

Prompt visibility：active detour context 可以传入 compact trace summary。User visibility：默认不可见。

Lifecycle：`open / resolved / abandoned`；未来可在 audit 中记录 restore-mainline reason 与 budget reason。Audit / evaluation use：Detour Precision、Recovery Quality、Mainline Restoration。Complexity caution：不要让 detour_trace 变成第二套 audit 或 hidden planner history。

### 5.9 `active_recall`

Object role：memory recovery move。它从 stored reading state 中取回未 carry 的 concept、thread、reaction 等 bounded memory material。

Not this：不是 source verification，不是 detour，不是 visible route disclosure，不是 memory write。

Admission rule：当当前 read / navigation context 需要 earlier reading state，而该 state 不在 carry-forward packet 中时触发。State owner：retrieval/read-context layer；Memory owns durable stores。

Source-grounding requirement：返回的 memory item 应保留 source_refs 或 reaction anchors。Memory dependency：直接依赖 Memory Ontology 授权的 projection / retrieval path。

Prompt visibility：作为 selective carry 进入 Read prompt。User visibility：默认不可见；若产生 visible callback，必须自然、source-grounded。

Lifecycle：ephemeral request/result；不是 persistent Planning state，除非后续 policy 定义 unresolved recall obligation。Audit / evaluation use：Planning-Memory Alignment、Callback Utilization、FVI diagnosis。Complexity caution：不要用 active_recall 替代 look-back。

### 5.10 `look_back`

Object role：source calibration move。它返回 earlier source excerpts，帮助确认原文到底怎么说。

Not this：不是 semantic memory recall，不是 detour unit selection，不是 visible route disclosure。

Admission rule：当当前理解、callback、concept dependency 或 conflict 需要 source evidence 校准时触发。State owner：read_context/source helper；Runner/audit记录。

Source-grounding requirement：必须根据 SourceRef / SourceSpan 定位 earlier source excerpt。Memory dependency：可以由 memory ref 指向 source ref，但返回的是 source text。

Prompt visibility：作为 earlier_excerpts / source_ref_details 进入 selective carry。User visibility：默认不可见；未来可被 Visible Reading Route Surface Boundary 转成“建议回看这里”。

Lifecycle：ephemeral request/result。Audit / evaluation use：source calibration quality、FVI prevention、recovery from uncertainty。Complexity caution：不要因为“相关”就回看；look-back 是校准，不是自由重读。

### 5.11 `state_packet / navigation context`

Object role：prompt-facing / navigation-facing projection。它把 durable memory state、local continuity 与 recent reaction 等压缩成 bounded packet。

Not this：不是 authoritative memory，不是 planning store，不是 audit trace。

Admission rule：每次 Navigate / Read call 前由 `state_projection.py` 构造。State owner：projection layer。

Source-grounding requirement：projection 中的 refs 必须 source-ref-preserving；缺 source refs 的条目不能被 Planning 当作 source truth。

Memory dependency：来自 Memory stores 的 bounded digest。Prompt visibility：是。User visibility：否。

Lifecycle：per-call ephemeral；可被 continuation capsule持久化为 resume seed，但仍是 projection。Audit / evaluation use：Memory Quality probe snapshots、Planning-Memory Alignment。Complexity caution：不要把 prompt packet 反向当成 state truth。

### 5.12 `slow_cycle carry-forward`

Object role：chapter/session boundary 的 macro focus selection 与 carry-forward obligation formation。

Not this：不是 general planner，不是 memory-only cleanup，不是 policy learner，不是 prompt self-refiner。

Admission rule：chapter/session boundary、chapter tail、run boundary 或 slow-cycle trigger。State owner：slow-cycle proposes；Runner/state_ops settle where applicable。

Source-grounding requirement：carry-forward focus 必须基于 settled reading state、source refs、reaction records 或 chapter source refs。Memory dependency：高度依赖 settled memory，但不能直接改写未授权 stores。

Prompt visibility：结果通过 active_attention carry-forward、reflective digest、continuation capsule 等 bounded projection 进入后续 prompt。User visibility：默认不可见；未来可被 route disclosure surface 转成 visible reading note。

Lifecycle：`carry_forward / cool / resolve / promote_candidate / supersede / abandoned` 等。Audit / evaluation use：Macro Continuity、chapter transition quality、open obligation preservation。Complexity caution：不要让 slow-cycle 承担全书路线规划。

### 5.13 `surfaced_reaction / prior_link / outside_link / search_intent`

Object role：visible reading trace 的 surfaced payload。它表达读书时浮现的 margin-note-like thought，可带 prior link、outside link 或 search intent。

Not this：不是 visible route disclosure，不是 semantic memory，不是 internal navigation decision。

Admission rule：由 `Read.surfaced_reactions[]` 提出，经 reaction builder 持久化。State owner：Read proposes；settlement/reaction builder writes.

Source-grounding requirement：source_quote 必须来自 current unit；prior_link 必须引用 allowed refs；visible wording不得泄漏 internal handles。

Memory dependency：prior_link 可引用 bounded memory refs，但 reaction 本身不成为 memory。Prompt visibility：recent reaction digest 可 bounded projection。User visibility：是。Recent reaction digest may support visible continuity and callback awareness, but it cannot be the sole semantic justification for navigation, detour, or visible route disclosure.

Lifecycle：append-only；可通过 reconsolidation 解释 later reinterpretation。Audit / evaluation use：Spontaneous Callback、False Visible Integration、visible route disclosure support evidence。Complexity caution：不要把 `search_intent` 当成实际搜索，也不要把 `outside_link` 当成 source truth。

### 5.14 `read_audit / settlement_audit / navigation trace`

Object role：non-planning-state diagnostic artifacts。它们记录决策、settlement、context、ops、deltas、budget 与 failure evidence。

Not this：不是 runtime planning context，不是 memory，不是 user-facing rationale。

Admission rule：Runner / observability 写入。State owner：observability。

Source-grounding requirement：audit 应记录 source span / source refs / resolution where relevant。Memory dependency：可记录 memory refs used，但不成为 memory。

Prompt visibility：默认不进入 prompt。User visibility：默认不展示；可在 admin/eval/report 中使用。

Lifecycle：append-only diagnostic stream。Audit / evaluation use：Planning Audit、Reading Path Quality、Detour Precision、Planning-Memory Alignment、failure localization。Complexity caution：不要把 rejected alternatives 或 raw traces 注入下一步 reading loop。

------

## 6. Micro / Meso / Macro Planning Layers

Planning v0 使用轻量三层，不引入 formal HTN、RL、global planner 或 MCTS loop。

### 6.1 Micro planning

Micro planning 是 immediate next-step control：

```text
next unit selection
continue mainline default
whether Read needs active_recall / look_back support
whether current unit creates detour_need
whether active detour is resolved / abandoned
```

主要对象：`Navigate.choose_next_unit`、`Read`、Reading Runner settlement、read_context。

Micro layer 的核心原则：source-order mainline 是默认；exceptions 必须有 source-grounded reason。

### 6.2 Meso planning

Meso planning 是 local route deviation and recovery：

```text
open detour
localize detour target
read detour through same loop
resolve / abandon detour
restore mainline
handle bounded deep-dive
```

主要对象：`active_detour_need`、`detour_trace`、`Navigate` detour mode、source skills、Runner restoration.

Meso layer 的核心原则：detour 是 first-class path deviation，不是 hidden supplemental fetch。

### 6.3 Macro planning

Macro planning 是 chapter/session boundary 的 carry-forward planning：

```text
which focus carries into next chapter/session
which unresolved questions remain active
which detours were resolved / abandoned
which reflective frames are now stable
which obligations should be deferred
```

主要对象：survey orientation、reading_plan、slow_cycle carry-forward、local_continuity、continuation capsule、reflective digest。

Macro layer 的核心原则：slow-cycle 可以选择 next focus，但不生成完整 book-level route optimizer。

### 6.4 Survey / reading_plan and macro planning

`survey / reading_plan` 是 macro orientation，不是 macro planner 的全部。它提供 book-level structural queue；slow-cycle 提供 chapter/session carry-forward focus。二者共同支撑 macro planning，但都不应变成 full planner。

------

## 7. Navigate.choose_next_unit Ontology

本设计对 `Navigate.choose_next_unit` 的结论是明确的：

> `Navigate.choose_next_unit` 在 ontology 上是 source-grounded next-unit selector；它是 micro-planning navigator；在 active detour mode 中也是 detour localizer。它不是 large planner node，不是 general router，不是 visible route disclosure owner，不是 memory mutation layer。

这里的 micro-planning 只是命名局部路径选择层，不授予 `Navigate` 全局路线规划、visible route disclosure ownership、memory mutation 或 evaluation 权限。

### 7.1 它是什么

它选择下一段真正要读的 source unit。它的 selection 必须来自 current preview、allowed source evidence、active detour need 与 bounded navigation context。

在 mainline mode：

```text
input:
  current cursor
  adaptive source preview
  navigation context

output:
  end_anchor_text
  boundary_type
  reason
  continuation_pressure
```

在 detour mode：

```text
input:
  active_detour_need
  mainline_cursor
  already-read evidence
  optional skill results
  navigation context

output:
  choose_unit / request_skill / defer_detour
```

### 7.2 它不是什么

它不拥有：

```text
memory mutation
visible route disclosure
book-level chapter ordering
full route history
ordinary forward settlement
external search
full planning audit schema
```

它也不应被替换成大型 planner node。当前 blocker 是 ontology、policy、audit 字段与 evaluation，不是缺一个更大的 planner。

### 7.3 与 Read 的分工

`Navigate` 决定 **读哪里**。`Read` 决定 **这个 accepted unit 读出了什么**。

`Read` 可以提出 `detour_need`，但不能定位 detour target。`Navigate` 可以定位 detour unit，但不能写 memory，也不能把 detour 的解释变成 visible route disclosure output。

### 7.4 与 Runner settlement 的分工

`Navigate` 返回 proposal。Runner 才负责：

```text
anchor resolution
SourceSpan construction
fallback handling
unit ledger
Read invocation
memory/reaction settlement
cursor advancement
audit
```

这是 `LLM proposes; deterministic runner settles` 在 Planning 中的核心形式。

### 7.5 与 survey / reading_plan 的关系

`survey / reading_plan` 给 Runner 提供 chapter-level schedule。`Navigate` 不拥有 book-level chapter ordering；它只在当前 scheduled chapter / current source locus 内选择 next unit，或在 active detour mode 中定位 allowed detour unit。

### 7.6 如何使用 memory projection

`Navigate` 只使用 navigation context 中的 bounded projections：

```text
active_attention digest
concept digest
thread digest
reflective digest
recent reaction digest
source_ref digest
continuation capsule
```

它不得读取完整 durable stores，不得读取 audit dump，不得使用 evaluation report。

Knowledge activation projection can strengthen or warn a planning rationale, but it cannot by itself open a detour or visible route disclosure without current source evidence.

### 7.7 mainline 与 active detour

`mainline` 是默认。`active_detour` 是 mode，不是另一套 planner family。两者都走同一个 `Navigate.choose_next_unit → Read → Runner settlement` loop。

------

## 8. Planning State and Trace Boundary

### 8.1 Planning state 应表达什么

Planning state 只表达 runtime path-control obligations：

```text
mainline cursor / restore point
reading queue stage
active detour id
active detour need
detour trace status
bounded macro carry-forward focus
unresolved path obligations, if later authorized
```

这些状态回答的是：“下一步路径控制还欠什么？”

它不回答：“这本书现在被理解成什么？”后者属于 Memory。

Planning obligation 必须与路径控制有关。它至少应有 origin/source locus、reason class、status、owner、bounded lifetime 或 exit condition，以及可选 source/memory refs。一个概念“仍然重要”本身不构成 planning obligation；它应先留在 memory projection，除非它要求下一步路径动作。

### 8.2 Planning trace / audit 应记录什么

Planning trace 应记录 diagnostic facts：

```text
decision type
selection mode
selected source evidence
skill request/result
budget state
resolution status
defer reason
restore-mainline reason
memory refs used
uncertainty / reason class, if later authorized
candidate/rejected alternatives summary, if later authorized
```

它不需要暴露 hidden chain-of-thought。它需要 structured decision summary。

### 8.3 Trace 为什么不自动成为 runtime context

Trace 包含 rejected alternatives、failed resolution、budget details、debug events、operator/eval artifacts。把 trace 自动放回 prompt 会造成三类风险：

```text
contamination:
  把诊断噪声变成阅读理由

self-reinforcement:
  让系统追随自己上一轮的失败 rationale

legibility leak:
  把 hidden planning trace 误当 user-facing explanation
```

因此 audit trace 默认不进入 runtime planning context。

### 8.4 Planning state 与 Memory state 为什么不能合并

Memory state 是 source-grounded understanding。Planning state 是 path-control obligation。两者可以互相引用，但不能合并。

如果合并，会发生三种混淆：

```text
source understanding 被 path convenience 污染
path obligation 被 semantic memory 长期化
evaluation/audit artifact 被误当 runtime truth
```

### 8.5 local_continuity 是否足够作为 v0 起点

是。v0 不新增 planning store。`local_continuity` 已经表达：

```text
mainline_cursor
reading_queue_stage
active_detour_id
active_detour_need
detour_trace
```

这足以支撑当前 micro / meso planning ontology。

### 8.6 何时未来可能需要新 store

未来如果出现以下情况，才考虑新增 lightweight planning obligations store：

```text
visible route disclosure display preference/suppression 需要跨会话追踪
slow-cycle macro obligations 超出 active_attention carry-forward 能表达的范围
multiple concurrent detours 成为真实需求
navigation audit 需要 replayable path state，而非 diagnostic trace
```

这些都标为 later，不进入 v0。

------

## 9. Detour / Look-back / Active Recall Ontology Boundary

### 9.1 Active recall

`active_recall` 是 memory recovery。

Trigger：当当前 unit 需要 earlier reading state，而该 state 不在 carry-forward packet 中。

Executor：read_context / memory retrieval interface。

Writer：不写 durable memory；只返回 bounded supplemental context。Audit 由 read_audit 记录 supplemental activity。

Planning state：通常不进入 durable planning state；它是 per-read recovery move。若 recovery 失败且造成 unresolved obligation，后续 Detour / Recall Policy 可定义 pending obligation。

Exit：retrieval satisfied、no relevant memory、budget exhausted、or no-use.

User visibility：默认不可见；若形成 visible callback，必须由 Read 以 natural surfaced reaction 表达。

Visible route disclosure relation：This internal recovery event may later be disclosed as part of a visible reading route surface, but it does not create route choices, approval states, or navigation transitions.

Common confusion：把 memory recall 当成 source verification。

### 9.2 Look-back

`look_back` 是 source calibration。

Trigger：当前理解需要确认 earlier source text；memory 与 source 可能冲突；callback 需要证据；概念/定义依赖 earlier source。

Executor：read_context / source excerpt resolver。

Writer：不写 memory；不改变 path；audit 记录 supplemental source refs/excerpts。

Planning state：通常不持久化。若 look-back 暴露需要离开主线读取一段 source，才可能打开 detour。

Exit：source excerpt returned、source unavailable、budget exhausted、or calibration complete.

User visibility：默认不可见；未来可被 Visible Reading Route Surface Boundary 表达为 “这里可以回看”。

Visible route disclosure relation：A look-back event may later be disclosed as part of the reader's route trace, but the look_back operation itself is internal source calibration and creates no user route choice.

Common confusion：把 look_back 当成 active_recall。

### 9.3 Detour

`detour` 是 planning path deviation。

Trigger：`Read.detour_need`，或后续 policy 明确授权的 navigation-level path need。v0 不展开触发条件。

Executor：`Navigate.choose_next_unit` detour mode + Runner settlement。detour unit 一旦被 chosen，也通过同一 read loop 读取。

Writer：Runner 写 `local_continuity.active_detour_id / active_detour_need / detour_trace`。Audit 写 read / navigation / settlement trace。

Planning state：open detour 是 planning state；resolved / abandoned detour status 是 planning continuity。

Exit：resolved、abandoned、deferred、budget exhausted、restore mainline。当前 state status 支持 open/resolved/abandoned；defer 是 act decision，后续 policy可细化。

User visibility：默认不直接可见；未来可被 route disclosure surface 表达为 “Second Reader 在这里短暂离开 / 恢复了主线”。

Visible route disclosure relation：A detour event may later be disclosed as part of the reader's route trace, but the internal detour decision is not route guidance and creates no user approval state.

Common confusion：把 detour 当成 hidden supplemental fetch 或 free association search。

------

## 10. Internal Navigation vs Visible Route Disclosure

### 10.1 Internal navigation

Internal navigation 是系统下一步实际读哪里。它发生在 Runner / Navigate / Read loop 内。它决定 accepted source unit、detour defer、skill request、mainline restoration。

Internal navigation 不需要每次都告诉用户，也不应把所有 rationale 展示给用户。

### 10.2 Visible route disclosure

Visible route disclosure 是未来可能展示 Second Reader 自己路线的低打扰说明。它可以解释：

```text
Second Reader 继续了主线；
Second Reader 回看了某处；
Second Reader 暂缓了 detour；
Second Reader 恢复了主线；
Second Reader 带着某个 focus 继续读。
```

Visible route disclosure 可以引用 source evidence、memory projection 或 planning rationale，但只披露路线，不让用户选择路线。

### 10.3 Visible reaction 不是 visible route disclosure

Visible reaction 是 “这个读书时刻浮现了什么”。它可以包含 prior_link / outside_link / search_intent，但这只是 surfaced semantics，不是 visible route surface object。

### 10.4 Visible disclosure 不改变 state

Visible route disclosure never changes navigation state in v0. Any future user feedback on the display is a UX preference or suppression signal, not route control.

### 10.5 当前成熟度判断

当前项目已有 surfaced reactions 与 optional semantics，但没有成熟 visible route surface。因此 v0 只定义 route disclosure boundary，不设计完整 Visible Reading Route Surface Boundary，也不创建 route control state。

------

## 11. Slow-cycle / Macro-planning Ontology Boundary

Slow-cycle 中必须分开两类工作。

### 11.1 Memory consolidation

属于 Memory consolidation 的是：

```text
reflective promotion
reconsolidation
knowledge activation status update
source-ref-preserving cooling / resolve / supersede
reaction compatibility projection
```

这些输出改变的是 reading memory 或 visible trace lineage。

### 11.2 Macro-planning / carry-forward planning

属于 macro-planning 的是：

```text
next chapter/session carry-forward focus
unresolved questions that should remain active
detour status after chapter boundary
mainline restoration rationale
optional next-focus suggestion
```

这些输出改变的是下一阶段读书应该带着什么注意力继续。

### 11.3 active_attention cooling / carry-forward 的交叉性

`active_attention` cooling 是 memory-management visibility operation；`cross_chapter_carry_forward` 同时也是 macro focus selection。它是 Memory 与 Planning 的交叉点，但不能因此把 Memory 和 Planning 合并。

### 11.4 Open obligations

Open obligations 可以属于 Planning state，前提是它们是 path-control obligations，例如 “这个 detour 仍 open” 或 “这个 unresolved focus 应 carry into next chapter”。如果只是 “某个概念仍重要”，应留在 memory projection，而不是 planning state。

### 11.5 Slow-cycle 不应做什么

Slow-cycle 不应成为：

```text
general planner
policy learner
prompt self-refiner
book-route optimizer
learning path engine
all-purpose macro-planning manager
```

------

## 12. Planning–Memory Compatibility Check

1. **没有重新定义 reading memory。**
   本页继承 Memory Ontology：reading memory 是从 accepted source units 中形成的 source-grounded reading state。
2. **没有把 source corpus 当成 memory 或 plan。**
   `book_document.json` 是 source substrate；不是 plan，不是 memory。
3. **没有把 planning state 合并进 memory state。**
   Planning state 表达 runtime path obligations；Memory state 表达 source-grounded understanding。
4. **没有把 reaction_records 当作 semantic memory。**
   reaction_records 是 visible trace；可作为 evidence，但不自动进入 concept/thread/reflective memory。
5. **没有把 knowledge_activations 当作 source-given truth。**
   它是 prior/external knowledge warrant ledger；只能以 warrant-bearing projection 使用。
6. **没有把 audit trace 当作 prompt-facing context。**
   read/settlement/navigation traces 是 diagnostic artifacts；默认不进 prompt。
7. **没有把 visible route disclosure 当作 internal navigation decision。**
   Visible route disclosure 是 optional display-only route legibility surface；navigation 是 internal path decision。
8. **正确区分 active_recall、look_back、detour。**
   active_recall = memory recovery；look_back = source calibration；detour = planning path deviation。
9. **只通过 bounded memory projection 使用 memory。**
   Planning 使用 active_attention / concept / thread / reflective / reaction / knowledge activation / source_ref digest，不直接读完整 stores。
10. **没有新增未经 Memory Ontology 授权的 memory store。**
    v0 不新增 memory store，也不新增 large planning store。
11. **Memory-facing requirements。**
    Planning v0 只提出两个接口要求，不改写 Memory Ontology：

- memory projections 应保留 `status / source_refs / supersede or validity markers`，以免 Planning 使用 stale memory；
- Memory Retrieval / Utilization 页面应定义 retrieval intent taxonomy，使 active_recall 与 look_back 的接口更稳定。

------

## 13. Accepted Constraints and Deferred Directions

本页接受以下约束。

**不新增 large planner node。**
当前缺口是 ontology、policy、audit、evaluation，不是缺一个更大的 planner。新增大 planner 会把不清楚的职责包进更难诊断的节点。

**不做 multi-agent reading team。**
产品需要一个连贯的 co-reading mind。Navigator agent、Memory agent、Critic agent、route-disclosure agent 的拆分会损害 voice coherence 与 audit simplicity。

**不做 graph workflow rewrite。**
可借鉴 durable execution、checkpoint、interrupt、trace，但当前 Reading Runner 已经是 deterministic orchestrator。基础设施迁移不能替代 reading judgment。

**不把 ToT / LATS / MCTS 作为默认 reading loop。**
Search-based deliberation 适合 hard passage / optional deep-dive，不适合每个 next-unit decision。

**不做 full planner-executor architecture。**
当前已有 Navigate / Read / Runner / slow-cycle 的轻量分工。Formal planner-executor 会过度任务化阅读。

**不让 visible route disclosure 替代 source-order reading。**
Source order 通常承载作者结构。Visible route disclosure 只能展示或解释 `reading_route_trace`，不能把阅读改成推荐流、route choice UI 或 route steering。

**不暴露全部 planning reasoning 给用户。**
用户需要 concise rationale、source grounding 和性，不需要 internal trace 或 rejected alternatives。

**不合并 planning state 与 memory state。**
路径控制与理解状态必须分开。

**不做 complex learning path engine / full learner model。**
Reading Companion 当前不是 tutoring system，没有 mastery model、prerequisite graph 或课程目标。

**不让 slow-cycle 负责所有 macro-planning。**
Survey、Navigate、Read、Runner、slow-cycle 分担不同时间尺度；slow-cycle 只做 chapter/session carry-forward 与 consolidation。

**不做 complex planning manager agent。**
Planning v0 使用 local_continuity、bounded trace、policy pages，而不是自治 manager。

------

## 14. What This Design Changes or Tightens

### 14.1 Preserved

本设计保留：

```text
attentional_v2 current default
paragraph-offset SourceCursor / SourceSpan
inline SourceRef evidence spine
survey / reading_plan orientation
Navigate.choose_next_unit → Read → Runner settlement
local_continuity
active_detour_need / detour_trace
active_recall / look_back
bounded state_packet / navigation context
chapter-end slow-cycle
read_audit / settlement_audit / unit_span_ledger
```

### 14.2 Tightened

本设计收紧：

```text
Planning = reading path control, not task planning
Navigate = next-unit selector / detour localizer, not large planner
local_continuity = v0 planning state, not memory
detour = path deviation, not hidden supplemental fetch
active_recall = memory recovery
look_back = source calibration
visible reaction ≠ visible route disclosure
visible route disclosure ≠ internal navigation
audit trace ≠ runtime context
state_packet ≠ planning state
slow-cycle output must split memory consolidation vs macro carry-forward
```

### 14.3 Reinterpreted names

- `reading_plan`：structural orientation / scheduling prior。
- `Navigate.choose_next_unit`：source-grounded next-unit selector。
- `active_detour_need`：open planning obligation。
- `detour_trace`：lightweight path-deviation continuity record。
- `navigation context`：bounded projection, not state。
- `surfaced_reaction`：visible trace, not visible route disclosure。
- `prior_link / outside_link / search_intent`：visible support semantics, not route disclosure policy or route control。

### 14.4 Deferred

Deferred to later pages：

```text
Navigation Policy triggers
Detour / Look-back / Active Recall Policy
Visible route surface object and UX
Planning Audit schema
Planning Evaluation rubric
Memory Retrieval / Utilization details
Slow-cycle macro carry-forward operation matrix
Codex implementation roadmap
```

------

## 15. Design Implications for Later Pages

**Navigation Policy**
Must define source-order default, bounded exceptions, mainline continuity, value/cost/scent language, and how `Navigate.choose_next_unit` decides among continue, defer, detour localization, and source-evidence request.

**Detour / Look-back / Active Recall Policy**
Must formalize triggers, budgets, exit conditions, recovery and utilization trace while preserving ontology distinctions.

**Visible Reading Route Surface Boundary**
Must define display boundary, `no_user_surface_needed`, concise rationale, and display preference / suppression semantics if needed. It must not create route controls, accept/reject navigation states, or reuse visible reaction as route control.

**Slow-cycle / Macro-planning**
Must separate reflective promotion from macro carry-forward; define open obligations and chapter/session focus without making slow-cycle a planner.

**Planning Audit / Observability**
Must add structured decision summaries, not hidden reasoning. It should record selected option, source evidence, memory refs, budget reason, defer/restore reason, and failure class.

**Planning Evaluation**
Should define Reading Path Quality, Navigation Groundedness, Mainline Continuity, Detour Precision, Recovery Quality, Visible Route Disclosure Readiness, Overplanning / Thrashing, and Planning-Memory Alignment.

**Memory Retrieval / Utilization**
Must define retrieval intents and utilization trace so Planning can request memory recovery without owning Memory.

------

## 16. Optional Open Questions

### 16.1 是否需要 `planning_obligations.json`？

现在不能解决，因为 current `local_continuity` 足够表达 v0 path obligations。是否新增 store 取决于 Visible Reading Route Surface Boundary、Slow-cycle / Macro-planning 与 Planning Audit 是否证明 local_continuity 不足。它不阻塞下一步 Navigation Policy。

### 16.2 Visible route surface display 是否需要持久化？

现在不能解决，因为当前项目还没有成熟 visible route surface。它依赖 Visible Reading Route Surface Boundary。即使未来持久化，也只能是 display trace / display preference，不是 route control state；它不阻塞 Navigation Policy，因为 internal navigation 可先独立收紧。

### 16.3 Navigation trace 是否需要 replayable decision graph？

现在不能解决，因为 Planning Audit schema 尚未设计。v0 只要求 compact diagnostic trace，不要求 replayable graph。它不阻塞 Navigation Policy。

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

| Project evidence                                    | What it shows                                                | Supports which design judgment                               | Constraint status               | Runtime-artifact validation gap                              |
| --------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------- | ------------------------------------------------------------ |
| `docs/product-overview.md`                          | Product is a living, curious, self-propelled co-reading mind; not a summary engine or service-style assistant; must remain text-grounded and legible. | Planning must stay reading-specific and source-grounded; visible route disclosure cannot replace reading. | Stable product constraint.      | No runtime row needed.                                       |
| `README.md`                                         | Workspace has backend/frontend, `attentional_v2` default override and `iterator_v1` fallback mechanism path. | Design should evolve current mechanism, not invent greenfield architecture. | Workspace fact.                 | N/A.                                                         |
| `docs/current-state.md`                             | Current paragraph-offset cursor, SourceSpan, SourceRef cutover, `Navigate.choose_next_unit`, unit ledger, settlement diagnostics, source-skill posture, F4A gaps. | Planning ontology must distinguish architecture readiness from runtime quality; detour and visible route disclosure still need policy. | Current canonical status.       | Actual JSONL rows not directly audited here.                 |
| `docs/source-of-truth-map.md`                       | Repo-first authority and canonical locations for product, mechanism, evaluation, current state, tasks. | Planning state/trace must be placed in mechanism-private or canonical docs, not chat memory. | Stable governance constraint.   | N/A.                                                         |
| `docs/backend-reading-mechanism.md`                 | `book_document.json` is shared parsed-book truth; paragraph substrate stable; `attentional_v2` uses paragraph/char cursor and inline SourceRef; no shared Anchor Bank registry. | Source corpus is not plan or memory; SourceRef is evidence spine. | Shared platform constraint.     | N/A.                                                         |
| `docs/backend-reading-mechanisms/README.md`         | `attentional_v2` is current default/live mechanism; `iterator_v1` fallback. | Planning Ontology should be compatible with current live mechanism. | Catalog fact.                   | N/A.                                                         |
| `docs/backend-reading-mechanisms/attentional_v2.md` | Reading Runner owns loop; survey orientation; `Navigate.choose_next_unit`; Read contract; detour same-loop; settlement and slow-cycle roles. | Core Planning objects and layer boundaries.                  | Strong mechanism contract.      | Runtime quality still requires artifact audit.               |
| `schemas.py`                                        | Defines `SourceRef`, `LocalContinuityState`, `DetourNeed`, `DetourTraceEntry`, `NavigateActResult`, `NavigateActTraceEntry`, `ReadUnitResult`, store schemas. | Existing object ontology should be tightened, not replaced.  | Code-level contract.            | Schema does not prove behavior quality.                      |
| `prompts.py`                                        | Navigate prompt constrains source-grounded unit selection; Read prompt limits memory ops, surfaced reactions, detour_need; chapter consolidation prompt preserves carry-forward. | LLM proposal boundaries; Navigate not visible route disclosure/memory owner; Read not route owner. | Prompt contract.                | Prompt compliance requires runtime audit.                    |
| `nodes.py`                                          | Normalizes state ops, surfaced reactions, detour_need and Navigate acts; filters ungrounded source_quote and internal handles. | LLM output is bounded proposal, not final state.             | Code-level current behavior.    | Normalization quality needs row audit.                       |
| `runner.py`                                         | Runner loads/saves runtime bundle, manages local continuity/detour, applies reading plan, skill dispatch, settlement seams. | Runner is deterministic executor and planning-state owner.   | Architecture evidence.          | Tool response truncated; enough for boundary, not full loop audit. |
| `state_ops.py`                                      | Deterministic application of active_attention, concept, thread, reaction and reflective supersede operations; source_ref merging. | Settlement, not LLM, owns state mutation; lifecycle must separate visibility and validity. | Code-level behavior.            | Per-op outcome not fully first-class.                        |
| `storage.py`                                        | Mechanism-private artifacts include local_continuity, unit_span_ledger, active_attention, concept/thread/reflective, reaction records, read/settlement audit. | JSON/JSONL first; audit artifacts not runtime planning context. | Current storage fact.           | Actual contents not audited.                                 |
| `state_projection.py`                               | Builds bounded `state_packet.v1`, carry-forward context, navigation context from durable stores. | Projection is not authoritative state; Planning uses bounded memory projections. | Strong contract evidence.       | Does not prove projection optimality.                        |
| `read_context.py`                                   | `look_back` resolves source excerpts; `active_recall` retrieves concept/thread/reaction state. | active_recall / look_back ontology boundary.                 | Strong contract evidence.       | Trigger policy not validated.                                |
| `slow_cycle.py`                                     | Reaction persistence, reflective promotion, reconsolidation, chapter consolidation and carry-forward. | Slow-cycle must split memory consolidation and macro carry-forward planning. | Strong implementation evidence. | Output quality not audited.                                  |
| `knowledge.py`                                      | Conservative knowledge activation lifecycle and search policy; prior knowledge only changes use mode when warrant exists. | Prior/external knowledge must stay warrant-bound, not source truth. | Code-level boundary.            | No runtime activation audit here.                            |
| `observability.py`                                  | Records read audit, settlement audit, unitization audit, compact deltas, supplemental context, detour_need. | Audit is diagnostic and should support Planning Audit without becoming prompt context. | Strong audit contract.          | Actual JSONL rows not opened.                                |
| `docs/backend-reader-evaluation.md`                 | Product-first, mechanism-agnostic evaluation; active long-span line: Memory Quality, Spontaneous Callback, False Visible Integration. | Planning Evaluation should be separate but compatible with memory/reaction evaluation. | Stable evaluation constitution. | Planning-specific metrics not yet formalized.                |
| `docs/tasks/registry.md`                            | Active structural rework summary; detour and optional surfaced semantics not yet runtime-validated in F4A. | Detour and visible route disclosure policy should not overclaim maturity. | Current task evidence.          | Runtime rows not directly inspected.                         |
| `docs/history/decision-log.md`                      | Records focus over flexibility, canonical substrate, mechanism-private artifact boundary, product-first evaluation. | Supports conservative, non-greenfield Planning Ontology.     | Historical design evidence.     | N/A.                                                         |

## B. Assessment Basis

**From P0 Shared Charter.**
This design inherits the shared territory map and hard boundaries: source corpus, reading locus, reading memory, planning state, audit trace, visible reaction, visible route disclosure, prior knowledge activation and evaluation evidence are distinct. It also inherits `LLM proposes; deterministic runner settles`, Planning as source-grounded reading path planning, the active_recall / look_back / detour split, slow-cycle memory vs macro carry-forward boundary, and complexity guardrails.

**From Planning Assessment.**
The assessment identifies the current system as a reasonable mid-stage reading-specific planning architecture, with the main blocker being Planning Ontology and policy vocabulary, not lack of a stronger planner. It also identifies `Navigate.choose_next_unit` as simultaneously next-unit selector, source-grounded navigator, micro-planner and detour localizer, and warns against large planner nodes, multi-agent teams, graph workflow rewrite and default search-based deliberation.

**From Memory Ontology.**
This page takes Memory Ontology’s “Planning-facing summary” as binding: Planning sees bounded typed projections of active_attention, concepts, threads, reflective frames, recent reactions, warranted knowledge activations and source_ref evidence; it must not own durable memory or convert visible/audit/eval artifacts into semantic state.

**From Memory Assessment.**
Memory Assessment is used only as a compatibility guard: `memory_uptake_ops` are bounded write intent, retrieval intent is not yet formalized, active_recall / look_back are retrieval-related but distinct, reaction_records and knowledge_activations have hard boundaries, and Callback / FVI risks constrain Planning’s use of memory.

Where this page makes project-specific judgments, the most important one is: `local_continuity` is sufficient as Planning state v0; no new planning store is added now.

## C. External Rationale, as Filtered Through the Assessments

| External work                                                | Original problem                                             | Supports this design judgment                                | Similarity to Reading Companion                          | Difference / do not copy                                     | Localized borrowing                                      | Support type      |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------- | ----------------- |
| ReAct — https://arxiv.org/abs/2210.03629                     | Interleave reasoning, acting and observation.                | Detour and source-skill loops should be bounded and observation-grounded. | Both use evidence to correct next step.                  | Reading source text is not generic tool sandbox.             | Use only for local detour/source evidence loop.          | Direct / Boundary |
| Plan-and-Solve — https://aclanthology.org/2023.acl-long.147/ | Reduce missing-step errors with explicit plans.              | Explicit planning may help at chapter/hard-passage boundaries, not every unit. | Some reading boundaries need lightweight planning.       | Reading should not become per-unit task decomposition.       | Boundary-level plan sketch only.                         | Boundary          |
| ReWOO — https://arxiv.org/abs/2305.18323                     | Decouple reasoning from observations for efficient tool use. | Detour evidence gathering may be bundled, but not frozen globally. | Local evidence slots resemble detour subneeds.           | Reading is responsive and source-order constrained.          | Possible later detour bundle, not v0 loop.               | Analogical        |
| Reflexion — https://arxiv.org/abs/2303.11366                 | Use verbal reflection between episodes.                      | Slow-cycle may learn/carry forward only at boundaries; strategy reflection must not pollute memory. | Both use between-episode reflection.                     | Reading memory is source-grounded content, not task strategy memory. | Keep slow-cycle boundary and audit separation.           | Boundary          |
| HTN — http://hdl.handle.net/1903/5810                        | Hierarchical task planning.                                  | Micro / meso / macro layer language is useful.               | Reading has unit / detour / chapter levels.              | No formal task network.                                      | Lightweight hierarchy only.                              | Analogical        |
| Options — https://doi.org/10.1016/S0004-3702(99)00052-1      | Temporal abstraction in RL.                                  | Detour and chapter carry-forward behave like temporally extended moves. | Both need start/termination conditions.                  | No RL value function.                                        | Use open/resolve/abandon lifecycle.                      | Analogical        |
| MAXQ — https://doi.org/10.1613/jair.639                      | Controller-worker decomposition.                             | Runner and Navigate should remain separated.                 | High-level choice vs deterministic execution.            | No value decomposition.                                      | Keep LLM proposal / Runner settlement.                   | Analogical        |
| Information Foraging — https://doi.org/10.1037/0033-295X.106.4.643 | Navigate information spaces by value/cost/scent.             | Next-unit and detour decisions are closer to information navigation than task planning. | Stay/leave decisions map to mainline/detour.             | Book reading has stronger source-order discipline.           | Later policy vocabulary: value, cost, scent, continuity. | Direct            |
| Exploratory Search — https://cacm.acm.org/research/exploratory-search/ | Search as open-ended understanding.                          | Visible route disclosure / deep-dive framing should support exploration without replacing mainline. | Reading can be exploratory.                              | Not open web search.                                         | Optional route-disclosure surface, not route takeover.                   | Background        |
| Rereading effect — https://doi.org/10.3758/BF03209348        | Rereading can improve metacomprehension.                     | Look-back is calibration, not automatic repetition.          | Earlier text can improve understanding.                  | Human study does not define LLM trigger policy.              | Define look-back as source calibration.                  | Direct            |
| Metacomprehension — https://doi.org/10.1111/j.1467-8721.2007.00509.x | Readers misjudge understanding.                              | Planning needs calibration moves; “seems understood” is insufficient. | Reading companion monitors understanding.                | No direct agent implementation.                              | Calibration category for look-back.                      | Background        |
| Adaptive Hypermedia — https://doi.org/10.1023/A:1011143116306 | User-model-based adaptation.                                 | Boundary evidence for separating display support from internal plan. | Both guide readers/learners.                             | RC lacks full learner model and does not ask users to choose the route. | Display-only route disclosure boundary.                 | Analogical        |
| Adaptive Navigation Support — https://doi.org/10.1111/1467-8535.00345 | Direct guidance / annotation / adaptive links.               | Route disclosure can be weak, optional and explanatory without granting route control. | Source-span route notes resemble navigation support. | Link adaptation is not source-span reading.                  | Define display boundary before policy.                   | Direct            |
| Learner Agency review — https://doi.org/10.1186/s41239-020-00219-w | Recommenders supporting learner agency.                      | Visible route disclosure must be optional and non-steering. | Both support human reader/learner.                       | RC is not tutoring platform.                                 | Agency-preserving route disclosure.                      | Direct            |
| Open Learner Model — https://doi.org/10.1007/s11257-016-9186-6 | Make learner state visible for self-regulation.              | Explainability helps but should not expose full trace.       | Both benefit from understandable rationale.              | No full mastery model.                                       | Concise source-grounded rationale only.                  | Analogical        |
| Controllability / Explainability recommenders — https://doi.org/10.1007/s11257-020-09281-5 | Recommender control and explanation effects.                 | Future route disclosure should be explainable without implying route control. | Both involve user-visible guidance.                      | Not all internal planning should be exposed, and RC does not ask users to choose the route. | User-facing rationale separate from audit trace.         | Boundary          |
| Being Accurate Is Not Enough — https://doi.org/10.1145/1125451.1125659 | Accuracy-only recommender evaluation is insufficient.        | Visible Route Disclosure Readiness should include trust, agency, interruption, source-grounding. | Both evaluate user-visible guidance.                     | Reading path ≠ item ranking.                                  | Later route disclosure evaluation dimensions.            | Direct            |
| ResQue — https://doi.org/10.1145/2043932.2043962             | User-centric recommender evaluation.                         | Evaluate route-disclosure usefulness, not just hit-rate.     | Optional reading notes need UX quality.                  | No direct rubric copy.                                       | Usefulness/trust/agency dimensions.                      | Direct            |
| WebArena — https://arxiv.org/abs/2307.13854                  | Long-horizon agent evaluation in realistic environments.     | Planning Evaluation should localize planner/executor/retrieval errors. | Both need trace-aware diagnosis.                         | Reading is source-span environment, not web task.            | Failure localization, not benchmark tasks.               | Analogical        |
| τ-bench — https://arxiv.org/abs/2406.12045                   | Tool-agent-user interaction reliability.                     | Repeated reliability and recovery matter.                    | Both involve long chains and user-facing effects.        | Reading has no fixed transactional goal.                     | Recovery and consistency metrics.                        | Analogical        |
| Tree of Thoughts — https://arxiv.org/abs/2305.10601          | Branch/backtrack deliberate reasoning.                       | Default reading loop should not be search-based.             | Hard passages may need small comparison.                 | Ordinary reading lacks stable reward and is latency-sensitive. | Later optional hard-mode only.                           | Negative          |
| LATS — https://arxiv.org/abs/2310.04406                      | MCTS-like agent planning.                                    | MCTS is too heavy for default next-unit decisions.           | Deep-dive may need lookahead.                            | Reading lacks clear terminal reward.                         | Boundary evidence.                                       | Negative          |
| Mem0 — https://arxiv.org/abs/2504.19413                      | Production-ready long-term memory with operations.           | Planning should consume operation-settled projections, not write memory. | Both require metadata/lifecycle.                         | Mem0 is general agent memory.                                | Operation boundary analogy.                              | Background        |
| Zep — https://arxiv.org/abs/2501.13956                       | Temporal knowledge graph for agent memory.                   | Source, memory, observations, validity and summaries should be separated. | Both need evidence and validity.                         | RC does not need graph DB.                                   | Validity/status in projections.                          | Background        |
| Letta / MemGPT — https://arxiv.org/abs/2310.08560            | Context scarcity and memory hierarchy.                       | Prompt-facing projection is not durable state.               | Both manage context windows.                             | RC is not Memory OS/persona assistant.                       | Projection discipline only.                              | Boundary          |
| LangGraph Memory Concepts — https://docs.langchain.com/oss/python/concepts/memory | Semantic/episodic/procedural split and hot/background writes. | Type hygiene and write timing support Planning-Memory separation. | Both need state/context separation.                      | Framework taxonomy not RC ontology.                          | Hot-path vs slow-cycle boundary.                         | Background        |
| LongMemEval — https://arxiv.org/abs/2410.10813               | Stage-aware long-term memory evaluation.                     | Planning-Memory failures need formation/retrieval/utilization localization. | Both need long-span diagnosis.                           | Chat benchmark, not source reading.                          | Stage-aware audit idea.                                  | Analogical        |
| HaluMem — https://arxiv.org/abs/2511.03506                   | Hallucination in memory systems.                             | Planning must not over-integrate retrieved memory into visible output. | Both face memory pollution.                              | Frontier benchmark.                                          | FVI-aware boundary.                                      | Background        |

## D. Simplicity and Universality Check

**是否优先收紧现有结构？**
是。本设计保留 Navigate / Read / Runner / slow-cycle，只收紧 object roles、state boundaries、projection rules 和 trace separation。

**是否避免把 source corpus 变成 plan？**
是。Source corpus 是 substrate；planning decision 只发生在 current preview、accepted unit、detour localization 或 carry-forward obligation 上。

**是否避免把 memory state 变成 planning state？**
是。Memory stores 只通过 projection 被 Planning 使用；Planning state v0 是 local_continuity。

**是否避免把 visible reaction 变成 visible route disclosure？**
是。Visible reaction 是 reading trace；visible route disclosure 是 optional display-only route legibility surface，当前只定义 territory。

**是否避免把 visible route disclosure 变成 internal navigation？**
是。Internal navigation 可以发生无 visible route disclosure；visible route disclosure 不能改 path。

**是否避免把 audit trace 变成 runtime context？**
是。Audit 只服务 diagnosis/evaluation，默认不进 prompt。

**是否避免 large planner / multi-agent / graph workflow / ToT / LATS / MCTS 默认 loop？**
是。它们被明确列为 deferred / negative boundary。

**是否保留 source-order mainline continuity？**
是。Mainline continuity 是 default；detour、look-back、active recall 都是 bounded exceptions or support moves。

**是否给 Memory 足够接口但不接管 Memory？**
是。Planning 需要 bounded projections、status/source refs、retrieval intents；不新增 memory store，不改 Memory Ontology。

**仍有哪些复杂化风险？**
三个风险仍需后续页面控制：

1. `Navigate.choose_next_unit` 被 policy 继续膨胀成万能 planner；
2. Visible route surface object 未定义前，visible reaction / search_intent 被误用为 route disclosure 或 route control；
3. slow-cycle 同时处理 memory consolidation 与 macro carry-forward，后续如果不分输出面，会滑向 general planner。

## E. Source Usage List

| External source                  | Authors / Organization   | Year        | Stable URL                                            | Used for                                                 | Support type      |
| -------------------------------- | ------------------------ | ----------- | ----------------------------------------------------- | -------------------------------------------------------- | ----------------- |
| ReAct                            | Shunyu Yao et al.        | 2022 / 2023 | https://arxiv.org/abs/2210.03629                      | Local source-grounded detour/action-observation boundary | Direct / Boundary |
| Plan-and-Solve                   | Lei Wang et al.          | 2023        | https://aclanthology.org/2023.acl-long.147/           | Boundary-level planning, not per-unit planner            | Boundary          |
| ReWOO                            | Binfeng Xu et al.        | 2023        | https://arxiv.org/abs/2305.18323                      | Bounded evidence slots for detour                        | Analogical        |
| Reflexion                        | Noah Shinn et al.        | 2023        | https://arxiv.org/abs/2303.11366                      | Slow-cycle reflection boundary                           | Boundary          |
| HTN Planning                     | Kutluhan Erol            | 1996        | http://hdl.handle.net/1903/5810                       | Lightweight micro / meso / macro language                | Analogical        |
| Options Framework                | Sutton, Precup, Singh    | 1999        | https://doi.org/10.1016/S0004-3702(99)00052-1         | Temporally extended detour / carry-forward moves         | Analogical        |
| MAXQ                             | Thomas Dietterich        | 2000        | https://doi.org/10.1613/jair.639                      | Controller / worker separation analogy                   | Analogical        |
| Information Foraging             | Pirolli & Card           | 1999        | https://doi.org/10.1037/0033-295X.106.4.643           | Mainline vs detour value/cost/scent framing              | Direct            |
| Exploratory Search               | Marchionini              | 2006        | https://cacm.acm.org/research/exploratory-search/     | Deep-dive / exploration boundary                         | Background        |
| The rereading effect             | Rawson, Dunlosky, Thiede | 2000        | https://doi.org/10.3758/BF03209348                    | Look-back as calibration                                 | Direct            |
| Metacomprehension                | Dunlosky & Lipko         | 2007        | https://doi.org/10.1111/j.1467-8721.2007.00509.x      | Calibration and uncertainty                              | Background        |
| Adaptive Hypermedia              | Brusilovsky              | 2001        | https://doi.org/10.1023/A:1011143116306               | Route disclosure / navigation support separation         | Analogical        |
| Adaptive Navigation Support      | Brusilovsky              | 2003        | https://doi.org/10.1111/1467-8535.00345               | Optional user-facing navigation support                  | Direct            |
| Learner Agency review            | Deschênes                | 2020        | https://doi.org/10.1186/s41239-020-00219-w            | User agency in route disclosure                          | Direct            |
| Open Learner Model               | Long & Aleven            | 2017        | https://doi.org/10.1007/s11257-016-9186-6             | Explainable but not fully exposed rationale              | Analogical        |
| Controllability / Explainability | Tsai & Brusilovsky       | 2021        | https://doi.org/10.1007/s11257-020-09281-5            | User control and route-disclosure rationale              | Direct            |
| Being Accurate Is Not Enough     | McNee, Riedl, Konstan    | 2006        | https://doi.org/10.1145/1125451.1125659               | Beyond-accuracy route-disclosure evaluation              | Direct            |
| ResQue                           | Pu & Chen                | 2011        | https://doi.org/10.1145/2043932.2043962               | Route-disclosure usefulness / trust                      | Direct            |
| WebArena                         | Shuyan Zhou et al.       | 2023 / 2024 | https://arxiv.org/abs/2307.13854                      | Trace-aware failure localization                         | Analogical        |
| τ-bench                          | Shunyu Yao et al.        | 2024 / 2025 | https://arxiv.org/abs/2406.12045                      | Reliability and recovery framing                         | Analogical        |
| Tree of Thoughts                 | Shunyu Yao et al.        | 2023        | https://arxiv.org/abs/2305.10601                      | Boundary against default search loop                     | Negative          |
| LATS                             | Andy Zhou et al.         | 2023        | https://arxiv.org/abs/2310.04406                      | Boundary against MCTS default loop                       | Negative          |
| Mem0                             | Chhikara et al. / Mem0   | 2025        | https://arxiv.org/abs/2504.19413                      | Operation-centric memory boundary                        | Background        |
| Zep                              | Rasmussen et al. / Zep   | 2025        | https://arxiv.org/abs/2501.13956                      | Evidence-backed state / validity analogy                 | Background        |
| MemGPT / Letta                   | Packer et al. / Letta    | 2023        | https://arxiv.org/abs/2310.08560                      | Prompt-facing vs durable memory boundary                 | Boundary          |
| LangGraph Memory Concepts        | LangChain                | 2025–2026   | https://docs.langchain.com/oss/python/concepts/memory | Type hygiene and hot/background timing                   | Background        |
| LongMemEval                      | Di Wu et al.             | 2024        | https://arxiv.org/abs/2410.10813                      | Stage-aware evaluation / failure localization            | Analogical        |
| HaluMem                          | Ding Chen et al.         | 2025        | https://arxiv.org/abs/2511.03506                      | Memory pollution / hallucination boundary                | Background        |
