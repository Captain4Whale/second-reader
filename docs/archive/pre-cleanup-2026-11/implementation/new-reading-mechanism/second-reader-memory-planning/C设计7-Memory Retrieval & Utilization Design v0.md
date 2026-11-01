# Memory Retrieval & Utilization Design v0

## 设计正文

### 1. Scope and Purpose

本设计定义 Second Reader / Reading Companion 的 **Memory Retrieval & Utilization v0**。

它继承 P0 Shared Charter 的边界：Memory 与 Planning 共同服务一个 source-grounded co-reading mind；运行原则是 `LLM proposes; deterministic runner settles`；source corpus、reading memory、planning state、audit trace、visible reaction、visible route disclosure、prior knowledge activation、evaluation evidence 必须分开；retrieval 必须 intent-aware and bounded；prompt-facing projection 不是 durable state；audit 是 diagnosis，不是 chain-of-thought exposure；active_recall 是 memory recovery；look_back 是 source calibration；detour 是 planning path deviation；默认不引入 vector DB、graph DB、Memory OS、hidden search 或 future text。

它继承 Memory Ontology：reading memory 是从 accepted source units 中形成的 source-grounded reading state；source corpus 不是 memory；visible reaction 不是 semantic memory；knowledge activation 是 warrant ledger；audit / evaluation artifacts 不是 runtime memory；Planning 只能通过 bounded typed source-ref-preserving projections 使用 memory。

它继承 Formation、Management、Navigation 与 Detour / Look-back / Active Recall Policy：retrieval 只能消费 settled, source-ref-preserving state；不能读取 raw `memory_uptake_ops`、failed ops、deferred candidates 作为 memory truth；superseded / invalidated / rejected items 不能普通进入 current truth；active_recall 不写 memory、不改变 cursor、不打开 detour；look_back 返回 source excerpt，不写 memory、不自动改变 path。

本页只设计：

- retrieval intent taxonomy；
- per-intent allowed source / filter / output / budget / stop condition；
- current truth、lineage、visible trace、warrant、source excerpt 的分层；
- prompt-facing context assembly；
- retrieval utilization trace；
- FVI / retrieval pollution guardrails；
- 与当前 `state_projection / read_context / source_ref / audit` 链路的收紧关系。

本页不是：

```text
Memory Ontology 重写
Memory Formation & Settlement 重写
Memory Management lifecycle 重写
Detour / Look-back / Active Recall trigger policy 重写
Navigation Policy 重写
Visible route surface object / UX 设计
full Evaluation rubric
Codex implementation roadmap
vector DB / graph DB / Memory OS 设计
new retriever agent
memory manager agent
broad RAG pipeline
```

本设计的目标是把现有 `attentional_v2` 的 fixed packet + supplemental context 链路，收紧成 **file-based、SourceRef-first、status-aware、intent-aware、bounded、可审计** 的 Memory Retrieval & Utilization contract。

------

### 2. Current Implementation Understanding

当前 GitHub repo 显示，Reading Companion 是 repo-first workspace；持久事实应沉淀在 canonical repo docs 或 state files，而不是 chat / scratch notes。 当前 default/live mechanism 是 `attentional_v2`，`iterator_v1` 是 explicit fallback / legacy-compatible path。

共享 source substrate 是 `public/book_document.json`，它是唯一 shared parsed-book truth；paragraph layer 是稳定 source substrate；当前 `attentional_v2` 使用 paragraph + char-offset cursor；source citations 使用 inline paragraph-offset `SourceRef`，没有 shared Anchor Bank 或 SourceRef registry。

当前 live loop 是：

```text
survey / reading_plan orientation
  → Navigate.choose_next_unit
  → Read
  → Reading Runner post-read settlement
  → cursor advance / unit span ledger / audit
  → chapter/session slow-cycle
```

`attentional_v2` 机制文档明确：Reading Runner 拥有 `Navigate.choose_next_unit`、Read、post-read settlement、cursor advancement、detour state handoff 与 mechanism-private runtime persistence；detour unit 一旦被选中，也走同一个 `Navigate.choose_next_unit → Read → settlement` loop。

#### 2.1 `state_projection.py`

`state_projection.py` 当前构造 `attentional_v2.state_packet.v1`。它从 authoritative stores 构造 bounded prompt-facing projection，而不是存储新 state。

它当前包括：

- `active_attention_digest`：来自 `active_attention.active_items`，最多 6 个 active items，hot view 最多 4 个；每项带 `item_id / attention_tags / statement / status / source_refs / linked_concept_keys / linked_thread_keys`。
- `concept_digest`：来自 `concept_registry.entries`，最多 3 个；排序偏向 source_refs 数量、status 与 key；每项带 `concept_key / concept_type / source_refs / sample_quotes / rationale`。
- `thread_digest`：来自 `thread_trace.entries`，最多 3 个；要求有 source_refs；保留 `thread_key / thread_type / source_refs / sample_quotes / rationale`。
- `reflective_digest` / `chapter_reflective_frame`：从 `reflective_frames` 中取 chapter frames、book frames、durable definitions 的小量 digest。
- `recent_reactions`：取最后 3 条 reaction records，带 primary_source_ref 与 source quote。
- `source_ref_digest`：从 carry refs 中取前 8 个 source_ref。
- `continuation_capsule`：包含 session continuity、active_attention、reflective frame、active focus、concept/thread digest、refs、rehydration entrypoints。
- `refs`：统一 carry-forward refs，用于后续 `context_ref_ids` 与 audit。

`build_navigation_context` 把上述 packet 投给 Navigate；`build_read_prompt_packet` 把 carry-forward context、supplemental context 与 detour context 投给 Read。Read prompt packet 只保留 narrow view：local continuity、active_attention、concept/thread digest、reflective digest，以及 selective carry 中的 earlier excerpts、source_ref_details、supporting_refs、active_detour_need 等。

当前 gap：projection 已 bounded，但还没有正式 intent label；status / validity / warrant / visible_trace markers 不够强；current truth 与 lineage 的分层还没有显式实现；reaction / knowledge 的 warning marker 需要收紧。

#### 2.2 `read_context.py`

`read_context.py` 当前已区分两个 supplemental-context helper：

```text
look_back:
  根据 SourceRef / SourceSpan 回到 earlier source excerpt。

active_recall:
  从 concept_registry / thread_trace / reaction_records 取回未 carry 的 reading state。
```

`look_back` 通过 carry-forward refs 或 explicit source_spans 解析 source_ref，返回 `source_refs / excerpts / refs`。`active_recall` 会避免重复返回已在 carry-forward digest 中的 concept/thread，最多返回 4 个 concepts、4 个 threads 与最近 4 条 reactions，并附带 refs。

当前 gap：active_recall 已有 duplicate suppression，但 filtering 还主要是“未 carry + store scan”，缺少 status-aware filtering；reaction records 返回时尚未强制标记 `visible_trace_support`；knowledge activations 没进入 active_recall contract；look_back failure / ambiguity / source calibration outcome 尚未成为统一 retrieval result。

#### 2.3 `source_spans.py`

`source_spans.py` 定义 paragraph-offset `SourceCursor / SourceSpan / SourceRef`。`SourceSpan` 是 end-exclusive range；`SourceRef` 是 inline source citation，不是 registry entry。

关键实现包括：

- `source_ref_from_unit()`：把 unit-local quote 解析为 paragraph-offset SourceRef。
- quote match 成功时产生 `matched` 或 `ambiguous_first_match`。
- quote 缺失或未找到时 fallback 到 unit span，并在 `resolution` 中标记 `missing_quote` 或 `quote_not_found`。
- `resolve_end_anchor_text()`：用 exact text 把 Navigate 返回的 `end_anchor_text` 解析为 `end_cursor`。
- `fallback_end_cursor_for_preview()`：anchor 失败时保守 fallback。
- `dedupe_source_refs()`：按 `source_span_id / role / quote` 去重。

这说明 retrieval / utilization 必须尊重 quote resolution marker。fallback source_ref 不是与 exact matched source_ref 等价的证据。

#### 2.4 Source skills

当前 repo 中 source skills 位于 `attentional_v2/skills/`。`runtime.py` 只允许：

```text
source_map_overview
source_scope_drilldown
source_window_fetch
```

并且 skill result provenance 标记为 `book_substrate` 与 `bounded_by_mainline_cursor = true`。

`source_skills.py` 将 visible source 限制在 mainline cursor 之前： earlier chapters 可见，future chapters 不可见，current chapter 只允许 mainline cursor 之前的 sentences；不可见范围返回 `range_outside_visible_scope`。

因此 source skills 是 detour localization 的 book-local evidence provider，不是 memory retrieval，不是 hidden search，不是 semantic relevance engine。

#### 2.5 `observability.py`

`record_read()` 当前写 `read_audit.jsonl`，记录：

```text
source_span / source_span_id
carry_forward_ref_ids
context_request
supplemental_ref_ids
supplemental_satisfied
supplemental_steps
stop_reason
budget_exhausted
reading_impression
surfaced_reactions
memory_uptake_ops
memory_uptake_ops_by_target_store
detour_need
```

`record_settlement()` 当前写 `settlement_audit.jsonl`，记录 source span、op counts、target-store distribution，以及 active_attention / concept_registry / thread_trace / reaction_records 的 compact ID deltas。

当前 gap：read_audit 记录了 supplemental refs / steps / stop reason，但还没有统一的 retrieval utilization trace，无法系统回答：

```text
取回了什么？
哪些被实际用了？
用于什么？
哪些没用？
为什么没用？
是否造成 FVI 风险？
```

#### 2.6 `storage.py`

`storage.py` 证明当前机制仍是 file-based JSON / JSONL first。机制私有 artifacts 包括：

```text
active_attention.json
concept_registry.json
thread_trace.json
reflective_frames.json
knowledge_activations.json
reaction_records.json
reconsolidation_records.json
unit_span_ledger.jsonl
read_audit.jsonl
settlement_audit.jsonl
local_continuity.json
continuation_capsule.json
reader_policy.json
memory_quality_probe_snapshots.json
```

这些 runtime files 都在 `_mechanisms/attentional_v2/` 下，不需要为了 v0 retrieval 引入新数据库。

#### 2.7 `schemas.py`

`schemas.py` 已定义 retrieval 相关边界：

- `ContextRequestKind = active_recall / look_back`；
- `DetourStatus = open / resolved / abandoned`；
- `NavigateActDecision = choose_unit / request_skill / defer_detour`；
- `StateOperationType` 包含 append/update/close/link/create/cool/drop/promote/supersede/reactivate/resolve；
- `SourceRef` 是 inline paragraph-offset citation；
- `LocalContinuityState` 持有 `mainline_cursor / active_detour_id / active_detour_need / detour_trace`；
- `ReadUnitResult` 持有 `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`；
- `NavigateActTraceEntry` 已能记录 decision、selection mode、reason、skill request/result、resolution、budget state。

当前 gap：schema 已有许多 status 与 trace 字段，但 retrieval intent / retrieval result / utilization trace 还不是 first-class schema；`KnowledgeActivation` 有 warrant fields，但尚未进入 retrieval output markers。

#### 2.8 `runner.py`

`runner.py` 是 Reading Runner integration。它加载 runtime bundle、构造 navigation context、调用 Navigate / Read、执行 source skills、记录 read / settlement audit、应用 memory ops、持久化 surfaced reactions、推进 cursor，并通过 `_apply_detour_need` 维护 local continuity。

`_apply_detour_need` 证明当前 detour 是 planning continuity state，不是 retrieval result：open detour 会写入 `active_detour_id / active_detour_need / detour_trace`；resolved / abandoned 更新 active detour pointer。

#### 2.9 `nodes.py` and `prompts.py`

`nodes.py` 当前会 normalize LLM output。重要 contract gap 是：`schemas.py` 已包含 `resolve`，但 `_STATE_OPERATION_TYPES` 当前没有列出 `resolve`；同时 `_normalize_state_operations` 在缺失 `target_store` 时会默认到 `active_attention`。 这对 retrieval 的启示是：retrieval 不能把 raw Read output 或 normalized raw ops 当 memory truth；只能读取 settled stores。

`prompts.py` 已把 Navigate 与 Read 边界写得很清楚：Navigate mainline mode 不能 request skills / defer；detour mode 可 choose source-grounded already-read unit、request one source skill 或 defer；不得 external web search；不得 future text；skill results are evidence, not answers。Read prompt 明确：`memory_uptake_ops` 只 target `active_attention / concept_registry / thread_trace`；surfaced reaction 已持久化为 reaction record，不能因为强烈就复制到 concept/thread；Read 可 emit detour_need，但不能 route / resolve it secretly。

#### 2.10 `state_ops.py`, `slow_cycle.py`, `knowledge.py`

`state_ops.py` 是 deterministic apply layer。它合并 source_refs，active_attention 支持 create/update/reactivate/cool/resolve/drop；concept/thread 把 append/create/link 归一化为 update，close 归一化为 resolve；reflective item supersede 会保留旧 statement 并标记 `superseded_by_item_id`。

`slow_cycle.py` 负责 durable reaction truth、reflective promotion、reconsolidation、chapter consolidation。Reaction builder 保留 `prior_link / outside_link / search_intent`，但这些是 visible reaction semantics，不是 semantic memory。

`knowledge.py` 管理 knowledge activation lifecycle：只有带 warrant 的 `plausible / strong` live activation 会把 mode 变为 `book_grounded_plus_prior_knowledge`；cool/drop/supersede 分别映射到 weak/dropped/rejected。

#### 2.11 Runtime-artifact evidence boundary

本设计读取了 GitHub repo 文档与核心代码，也读取了当前项目文档中记录的运行诊断摘要。但本轮没有逐行打开真实输出目录中的 runtime JSON / JSONL rows，例如：

```text
active_attention.json
concept_registry.json
thread_trace.json
reflective_frames.json
reaction_records.json
knowledge_activations.json
reconsolidation_records.json
unit_span_ledger.jsonl
read_audit.jsonl
settlement_audit.jsonl
local_continuity.json
```

因此本文只做 architecture-level、contract-level 与 assessment-level 设计判断，不声称已经独立验证真实 runtime quality。

------

### 3. Core Definitions

#### 3.1 Memory Retrieval

**Memory Retrieval** 是在明确 retrieval intent、bounded budget 与 SourceRef-first constraints 下，从 settled reading memory stores 或授权 source evidence 中取回 typed, status-aware, source-ref-preserving material 的机制。

它回答：

```text
当前 reading / navigation / slow-cycle / evaluation 需要什么既有 state 或 source evidence？
从哪些允许来源取？
哪些 status 可以作为 current truth？
哪些只能作为 lineage / visible trace / warrant / audit-only？
取回后是否真正被使用？
```

#### 3.2 Memory Utilization

**Memory Utilization** 是 retrieval result 被某个 consumer 实际用于某个声明用途的过程，例如 read continuity、definition support、thread continuity、source calibration、detour localization、slow-cycle candidate、evaluation probe。

Retrieval hit 不等于 utilization success。一个 item 被取回后可以：

```text
used
not_used
used_only_as_warning
used_only_as_lineage
used_only_as_visible_trace
used_only_as_warrant
```

#### 3.3 Retrieval intent

**Retrieval intent** 是一次 retrieval request 的目的类型。它决定 allowed stores、filtering rules、output shape、budget、stop condition 与 audit fields。

#### 3.4 Projection

**Projection** 是从 authoritative store 派生出的 bounded prompt-facing 或 consumer-facing view。Projection 不是 authoritative durable state。

#### 3.5 Prompt-facing packet

**Prompt-facing packet** 是实际进入 Navigate / Read / slow-cycle prompt 的 narrow context。它可以包含 projection、retrieval result 或 source excerpt，但不包含 full store dump、audit dump、raw Read intents 或 evaluation reports。

#### 3.6 Authoritative store

**Authoritative store** 是持久 state 文件，例如 `active_attention.json / concept_registry.json / thread_trace.json / reflective_frames.json / knowledge_activations.json / reaction_records.json / reconsolidation_records.json`。它们是 retrieval 的可读取状态来源，但读取方式必须受 intent / status / budget 限制。

#### 3.7 Current truth retrieval

**Current truth retrieval** 是取回当前 source-so-far 下仍可作为普通 reading memory support 的 item。它只允许 source-supported / refined / active / resolved-as-relevant / provisional-with-marker 的 items，不允许把 superseded / invalidated / rejected 当普通 truth。

In this design, `current_truth` means "currently usable as source-so-far reading support", not absolute truth. If this wording causes implementation confusion, Implementation Handoff may rename it to `current_support_projection` while preserving the same semantics.

#### 3.8 Lineage retrieval

**Lineage retrieval** 是取回 superseded、invalidated、rejected、retired、reconsolidated 或 historical items，用于解释演化、FVI diagnosis、supersede chain、manual repair 或 slow-cycle review。Lineage retrieval 必须带 warning markers。

#### 3.9 Visible trace retrieval

**Visible trace retrieval** 是取回 `reaction_records` 或 visible-reaction lineage，用于 callback context、reader-facing continuity 或 FVI diagnosis。它不产生 semantic truth。

#### 3.10 Warrant retrieval

**Warrant retrieval** 是取回 `knowledge_activations` 中的 source trigger、reading warrant、status、conflict_source_refs。它说明 prior / external knowledge 为什么被允许参与 reading，不说明书中事实为真。

#### 3.11 Source calibration support

**Source calibration support** 是使用 SourceRef / SourceSpan / unit_span_ledger / already-read source 取回 source excerpt，以校准“原文到底怎么说”。它属于 look_back_support，不属于 semantic memory recall。

#### 3.12 Retrieval candidate

**Retrieval candidate** 是经过 source/store scope 与 initial filters 后可考虑返回的 item。Candidate 不是 result，也不是 used item。

#### 3.13 Retrieval result

**Retrieval result** 是经过 status-aware filtering、dedupe、budget trimming 与 output classification 后返回给 consumer 的 typed packet。它必须保留 source_refs、status markers、warning markers 与 intended support channel。

#### 3.14 Context assembly

**Context assembly** 是把 continuity packet、retrieval results、source excerpts、detour context、warnings 组装成 consumer-specific prompt-facing packet 的步骤。Assembly 不是 retrieval 本身，也不是 utilization success。

#### 3.15 Utilization trace

**Utilization trace** 是记录 retrieval event 与 use event 的 diagnostic artifact。它回答：

```text
取回了什么？
用了什么？
用于什么？
没用什么？
为什么没用？
是否造成 projection / visible output / memory write / detour impact？
是否有 FVI risk？
```

它不进入 runtime prompt，不暴露 chain-of-thought，不等于 evaluation score。

#### 3.16 Not-used result

**Not-used result** 是 retrieval result 中明确被 consumer 或 assembly 拒绝使用的 item。必须记录 `no_use_reason`，例如 stale_only、lineage_only、reaction_only、knowledge_only、duplicate_already_carried、source_ref_missing、budget_trimmed、overbroad、conflict_with_current_source。

#### 3.17 Retrieval budget

**Retrieval budget** 是每次 retrieval 的 hard / soft bounds，包括 store scope、item count、source excerpt count、source window size、lineage depth、duplicate budget、act count、stop reason。

#### 3.18 Stop reason

**Stop reason** 是 retrieval 正常停止的原因，例如:

```text
sufficient_current_support
sufficient_source_excerpt
no_relevant_memory
only_lineage_available
duplicate_already_carried
budget_exhausted
source_ref_unavailable
source_calibration_required
detour_candidate_only
```

#### 3.19 Failure reason

**Failure reason** 是 retrieval 无法产生有效 support 的原因，例如:

```text
missing_source_refs
ambiguous_source_ref
look_back_source_unavailable
store_unavailable
status_blocked
audit_only_evidence
deferred_candidate_only
reaction_only_hit
knowledge_only_hit
overbroad_result
conflict_unresolved
```

#### 3.20 Retrieval pollution

**Retrieval pollution** 是取回或组装阶段把不该作为当前语义依据的材料污染 runtime prompt 或 visible output，例如 audit dump、raw failed ops、stale lineage、reaction-only trace、knowledge-only warrant、theme-only association。

#### 3.21 False Visible Integration risk

**False Visible Integration risk / FVI risk** 是 retrieval material 被过度整合成用户可见 callback、semantic claim 或 detour justification，导致 overclaim、hard-linking、theme-only similarity、memory drift 或 source-misaligned confidence。

#### 3.22 Non-goals as definitions

```text
retrieval is not memory formation
retrieval is not memory management
retrieval is not source corpus search by default
retrieval is not audit replay
retrieval is not visible route disclosure policy
retrieval is not evaluation
retrieval result is not automatically used
retrieval hit is not utilization success
```

------

### 4. Retrieval Intent Taxonomy

v0 taxonomy 保持少量、可审计、可实现。

Retrieval intents are divided into three bands:

```text
A. Runtime prompt-facing intents:
  continuity_carry
  active_recall
  look_back_support
  detour_support

B. Boundary / background intents:
  source_ref_recalibration
  lineage_recall
  slow_cycle_consolidation
  visible_route_surface_support

C. Diagnostic / repair intents:
  evaluation_probe
  manual_repair_support
```

Only Band A may normally enter Read / Navigate prompt. Band B requires explicit policy or boundary trigger. Band C never enters runtime prompt.

#### 4.1 MVP subset

MVP 必须支持：

1. **continuity_carry**
   默认 carry-forward / projection，用于正常持续阅读。
2. **active_recall**
   memory recovery，用于取回未 carry 的 earlier reading state。
3. **look_back_support**
   source calibration support，用于取回 earlier source excerpt / SourceRef evidence。它返回 source text，不返回 semantic memory truth。
4. **detour_support**
   为 active detour localization 或 detour candidate admission 提供 memory/source support。Detour target 不能仅由 memory projection 选择。
5. **source_ref_recalibration**
   当 memory item 的 source_refs、quote resolution、fallback status 需要校准时使用。
6. **lineage_recall**
   为 supersede / invalidate / reconsolidation / FVI diagnosis 取回 historical lineage。
7. **slow_cycle_consolidation**
   为 chapter/session slow-cycle 的 cooling / carry-forward / promotion / reconsolidation 提供候选材料。
8. **evaluation_probe**
   为 Memory Quality / Callback / FVI / Planning-Memory Alignment probe 提供诊断取样。它不进入 runtime prompt。

#### 4.2 Extended subset

Extended 允许作为接口保留，但不在本页展开完整对象：

1. **visible_route_surface_support**
   为未来 Visible Reading Route Surface Boundary 提供 source-grounded、status-aware evidence scaffold。本页不生成 route-disclosure text、route options、accept/skip state、navigation transition 或 persistence。
2. **manual_repair_support**
   为人工或 admin repair 提供 source-ref-preserving review context。它不是正常 runtime retrieval。

#### 4.3 不单独列为 top-level intent 的内容

以下作为 sub-intent 或 `used_for`，不扩张 taxonomy：

```text
definition_recall       → active_recall / used_for = definition_support
thread_recall           → active_recall / used_for = thread_continuity
visible_callback_recall → active_recall / visible_trace_support
warrant_check           → active_recall or visible_route_surface_support / warrant_support
```

------

### 5. Intent-specific Retrieval Contract

#### 5.1 Contract summary

| Intent                     | Primary purpose               | Allowed source                                 | Output channel                  | Runtime prompt?                 |
| -------------------------- | ----------------------------- | ---------------------------------------------- | ------------------------------- | ------------------------------- |
| `continuity_carry`         | normal carry-forward          | state_projection over settled stores           | bounded projection              | yes                             |
| `active_recall`            | memory recovery               | settled memory stores                          | retrieval result packet         | yes, if authorized              |
| `look_back_support`        | source calibration            | SourceRef / SourceSpan / already-read source   | source excerpt packet           | yes, if authorized              |
| `detour_support`           | detour localization support   | memory projection + source evidence            | support packet / candidate refs | yes, bounded                    |
| `source_ref_recalibration` | repair / verify source refs   | SourceRef + source text + source_spans         | calibration result              | usually no, except warning      |
| `lineage_recall`           | historical lineage            | lifecycle / supersede / reconsolidation stores | lineage packet                  | only with warning               |
| `slow_cycle_consolidation` | consolidation candidates      | broader settled memory                         | candidate set                   | slow-cycle only                 |
| `visible_route_surface_support`   | future route disclosure evidence | source-grounded eligible memory/source         | evidence scaffold               | future-only; not current runtime prompt |
| `evaluation_probe`         | diagnosis                     | broader state/audit/snapshots                  | diagnostic packet               | no                              |
| `manual_repair_support`    | admin repair                  | broader state/audit/source                     | review packet                   | no normal runtime               |

#### 5.2 `continuity_carry`

Purpose：让正常 Read / Navigate 保持连续阅读，不靠每次 broad retrieval。

Requester：

```text
state_projection
runner before Navigate / Read
resume / continuation capsule
```

Allowed sources：

```text
active_attention
concept_registry
thread_trace
reflective_frames
recent reaction digest
source_ref digest
continuation capsule
```

Filtering rules：

- 只构造 bounded digest，不读 full store prompt dump。
- 默认 current truth only。
- `cooled / dormant` 低优先级，但不视为 false。
- `provisional` 必须带 marker。
- `superseded / invalidated / rejected` 不进入普通 current packet。
- reaction records 只能作为 recent visible trace digest。
- knowledge activations 默认不进入，除非后续 projection gate 明确以 warrant marker 投入。
- 不包含 audit dump、failed ops、deferred candidates、raw memory_uptake_ops。

Output shape：

```text
state_packet.v1
active_attention_digest
concept_digest
thread_digest
reflective_digest
recent_reactions
source_ref_digest
continuation_capsule
refs
status_markers
warning_markers, when needed
```

Budget / stop condition：

- 每 store 小量 fixed caps；
- 不追求 exhaustive recall；
- stop_reason = `bounded_projection_complete`。

Utilization expectation：

- 默认进入 Read / Navigate。
- 但 item 在 packet 中仍不等于被 Read / Navigate 实际使用。
- 可记录 carry refs 与 later used refs 的差异。

Audit fields：

```text
retrieval_intent = continuity_carry
items_returned
source_refs_returned
projection_scope
filters_applied
duplicate_suppression
status_markers
```

Must not：

- 不把 projection 当 authoritative store；
- 不塞 full store；
- 不塞 audit；
- 不塞 deferred candidate；
- 不把 reaction 当 semantic support；
- 不把 knowledge activation 当 source truth。

Design change：当前 fixed packet 保留，但重新解释为 `continuity_carry` baseline，而不是唯一 retrieval policy。

#### 5.3 `active_recall`

Purpose：恢复未被 carry-forward packet 带入、但当前 reading / navigation 需要的 settled reading memory。

Requester：

```text
Read / runner after Design6 authorization
Navigate support signal after policy authorization
Detour support pre-check
Slow-cycle review, if using active recall channel narrowly
```

Allowed stores：

```text
active_attention
concept_registry
thread_trace
bounded reflective_frames
reaction_records as visible trace
knowledge_activations as warrant support
current_truth_projection
lineage_projection only with explicit lineage intent
```

Filtering rules：

- 普通 active_recall 只返回 current truth candidates。
- `superseded / invalidated / rejected` 只能在 lineage intent 下返回。
- `retired` 只能 historical recall / lineage / audit。
- `cooled / dormant` 可低优先级返回，但必须标记。
- `provisional` 可返回，但带 marker。
- fallback_source_ref / missing source_refs 降权并触发 warning。
- reaction_records 必须标记 `visible_trace_support`。
- knowledge_activations 必须标记 `warrant_support`，带 trigger / warrant / status。
- already carried concepts/threads 默认 suppress，并记录 duplicate.

Output shape：

```text
retrieval_result:
  intent: active_recall
  current_memory_support[]
  lineage_support[]
  visible_trace_support[]
  warrant_support[]
  not_used[]
  memory_refs[]
  source_refs[]
  status_markers[]
  warning_markers[]
  used_for_hint
```

Budget / stop condition：

- store-limited；
- item-limited；
- duplicate suppression；
- stop when sufficient relevant current memory found, only stale/lineage found, no relevant memory, budget exhausted, or source calibration required.

Utilization expectation：

- 可用于 read_continuity、definition_support、thread_continuity、visible_callback_support、detour_localization pre-check。
- 不能替代 look-back source calibration。
- 不改变 cursor，不写 memory，不打开 detour。

Audit fields：

```text
retrieval_event_id
retrieval_intent = active_recall
query_basis
store_scopes
filters_applied
items_returned
items_used
used_for
not_used_items
no_use_reason
status_markers
warning_markers
stop_reason
failure_reason
```

Must not：

- 不读 raw Read intents；
- 不读 audit dump；
- 不把 stale lineage 当 current truth；
- 不把 reaction_records 当 semantic truth；
- 不把 knowledge_activations 当 book truth；
- 不自动生成 detour target。

#### 5.4 `look_back_support`

Purpose：校准 earlier source evidence。它回答“原文到底怎么说”。

Requester：

```text
Read / runner after Design6 authorization
Navigate support signal after policy authorization
active_recall fallback when source verification required
FVI-sensitive visible callback guard
```

Allowed source locus：

```text
SourceRef
SourceSpan
unit_span_ledger coverage facts
already-read source
source_spans helpers
```

Filtering rules：

- 只在 already-read / visible-to-mainline boundary 内。
- 不读 future text。
- SourceRef fallback / ambiguous marker 必须暴露。
- failed look-back 不得被 memory confidence 静默替代。
- source excerpt 与 memory summary 分开组装。

Output shape：

```text
source_excerpt_packet:
  intent: look_back_support
  source_refs[]
  excerpts[]
  quote_boundaries
  source_span_ids
  calibration_result
  warning_markers
```

Budget / stop condition：

- 最多少量 source_refs；
- excerpt bounded；
- stop when sufficient excerpt found, SourceRef ambiguous, source unavailable, budget exhausted, or detour_candidate needed.

Utilization expectation：

- 用于 source_calibration。
- 如果 excerpt 足以校准，mainline 继续。
- 如果需要正式“读”一个 source unit，必须升级为 detour candidate，经 Detour Policy / Navigate / Runner 进入同一 read loop。

Audit fields：

```text
retrieval_intent = look_back_support
source_ref_or_span_used
excerpt_returned
quote_boundaries
calibration_result
source_refs_used
used_for = source_calibration
stop_reason
failure_reason
escalated_to_detour_candidate
```

Must not：

- 不写 memory；
- 不自动改变 cursor；
- 不自动打开 detour；
- 不作为 hidden reading unit；
- 不被 memory summary 替代。

#### 5.5 `detour_support`

Purpose：为 active detour localization 或 detour candidate admission 提供 memory/source support。

Requester：

```text
Navigate active detour mode
Runner after active_detour_need exists
Detour Policy when active recall / look-back reveals source-grounded path need
```

Allowed sources：

```text
active_attention digest / selected entries
concept_registry / thread_trace selected entries
source_ref_digest
look_back source excerpts
source skills results
bounded reflective frames as macro context
reaction_records only as visible trace warning/support
knowledge_activations only as warrant warning/support
```

Filtering rules：

- memory projection 不能单独选择 detour target。
- target_hint 来自 memory 时，必须再通过 source evidence 校准。
- reaction digest / knowledge activation 不能单独作为 detour target basis。
- theme-only association blocked。
- stale / lineage-only memory 只能说明“可能需要校准”，不能直接定位 target。
- source_scent / detour_value / continuity_cost 是 policy/audit markers，不是 ranking model。

Output shape：

```text
detour_support_packet:
  memory_refs_used[]
  source_evidence_needed[]
  candidate_source_refs[]
  source_scent_marker
  detour_value_marker
  continuity_cost_marker
  warning_markers[]
  not_used[]
```

Budget / stop condition：

- source skill act budget；
- memory item budget；
- source window budget；
- stop when source evidence sufficient, scent weak, target theme-only, budget exhausted, or defer recommended.

Utilization expectation：

- 用于 detour_localization；
- 可帮助 Navigate choose unit / request skill / defer；
- 不直接写 `active_detour_need`；
- 不直接 choose detour target without source evidence。

Audit fields：

```text
retrieval_intent = detour_support
target_hint
memory_refs_returned
memory_refs_used
source_evidence_needed
candidate_source_refs
used_for = detour_localization
not_used_items
no_use_reason
budget_state
stop_reason
failure_reason
detour_impact
```

Must not：

- 不变成 hidden search；
- 不读 future text；
- 不绕过 Navigate；
- 不绕过 Read / settlement；
- 不把 detour support 变成 route guidance。

#### 5.6 `source_ref_recalibration`

Purpose：校准 memory item 的 source_refs、quote resolution 或 fallback status。

source_ref_recalibration is a validation / warning subroutine. It may be invoked inside active_recall, look_back_support, lineage_recall, slow_cycle_consolidation, or manual_repair_support. It should not become a general prompt-facing retrieval mode or an independent repair workflow.

Requester：

```text
retrieval assembly when fallback_source_ref detected
look_back_support when source_ref ambiguous
slow_cycle when candidate source evidence weak
manual repair
evaluation probe
```

Allowed sources：

```text
memory item source_refs
source_spans.py quote resolution
accepted source unit
unit_span_ledger
already-read source text
```

Filtering rules：

- exact `matched` 优先；
- `ambiguous_first_match` 可保留但带 marker；
- `fallback_unit_span / missing_quote / quote_not_found` 降权；
- missing source_refs 不能作为 current semantic support；
- recalibration 不自动更新 memory，除非进入 Management / repair settlement。

Output shape：

```text
source_ref_calibration_result:
  memory_ref
  original_source_refs
  recalibrated_source_refs
  resolution_status
  confidence_marker
  warning_markers
  proposed_next_action
```

Budget / stop condition：

- bounded quote attempts；
- bounded source window；
- stop when exact match found, ambiguity remains, missing source unavailable, or repair requires manual/management.

Utilization expectation：

- 用于 warning、downgrade、look_back, or manual repair candidate。
- 不自行改写 durable memory。

Must not：

- 不把 fallback source_ref 升格成 exact evidence；
- 不因为 missing source_ref 就删除 memory；
- 不在 runtime prompt 中暴露 repair audit dump。

#### 5.7 `lineage_recall`

Purpose：取回历史 lineage，用于后文修正前文、supersede chain、invalidate explanation、reconsolidation、FVI diagnosis。

Requester：

```text
Management / slow-cycle
FVI diagnosis
evaluation_probe
manual_repair_support
active_recall only with explicit lineage intent
```

Allowed sources：

```text
concept_registry / thread_trace / reflective_frames with supersede or status history
knowledge_activations rejected / dropped
reaction_records with supersedes_reaction_id
reconsolidation_records
management / settlement audit only in diagnostic contexts
```

Filtering rules：

- 可返回 superseded / invalidated / rejected / retired。
- 必须带 warning markers。
- 必须带 replacement IDs、superseded_by_id、invalidating_source_refs、conflict_source_refs 或 reconsolidation ids when available。
- 不进入 normal current_truth_projection。

Output shape：

```text
lineage_packet:
  lineage_items[]
  current_replacement_refs[]
  invalidating_source_refs[]
  reconsolidation_records[]
  warning_markers[]
  not_current_truth = true
```

Budget / stop condition：

- bounded lineage depth；
- stop at current replacement, invalidating source, or budget.

Utilization expectation：

- 用于 lineage_explanation、FVI diagnosis、slow-cycle review。
- Read 不应把它当 current source truth。

Must not：

- 不进入 ordinary Read prompt without explicit warning；
- 不让 superseded content reappear as current truth；
- 不替代 source calibration。

#### 5.8 `slow_cycle_consolidation`

Purpose：为 chapter/session boundary 的 cooling、carry-forward、promotion、reconsolidation 提供 candidate materials。

Requester：

```text
slow_cycle
chapter_consolidation
reflective_promotion
reconsolidation
```

Allowed sources：

```text
active_attention
concept_registry
thread_trace
reflective_frames
reaction_records
knowledge_activations
reconsolidation_records
chapter source refs
deferred candidates as candidate evidence only
selected audit summaries only if explicitly needed for diagnosis
```

Filtering rules：

- broader than Read / Navigate but still bounded。
- deferred candidates 仍不是 memory truth，必须重新 admission。
- reaction_records 可用于 visible trace / reconsolidation，不自动 semantic promotion。
- knowledge_activations 可用于 warrant review，不自动 concept truth。
- raw audit dump 默认不进入 slow-cycle prompt；仅 selected diagnostic summary 可进入。
- Slow-cycle consolidation retrieval should use a two-stage packet: first a candidate index packet with IDs, store, status, source_refs, short reason, and warning markers; then an expanded evidence packet only for selected candidates that pass budget and source-ref gate. Do not send full broad memory plus audit summaries in one prompt.

Output shape：

```text
slow_cycle_candidate_set:
  candidate_items[]
  source_refs[]
  lifecycle_status[]
  support_summary
  warning_markers[]
  deferred_candidate_markers[]
```

Budget / stop condition：

- per chapter/session；
- capped per store；
- stop when candidate set sufficient or budget exhausted。

Utilization expectation：

- 生成 candidate set，不生成 final reflective truth。
- Final promotion / cooling / supersede 仍由 slow-cycle result + settlement/state_ops 决定。

Must not：

- 不变成 general planner；
- 不把 deferred candidate 当 memory；
- 不把 reaction/knowledge 自动 semanticize；
- 不写 route-disclosure output。

#### 5.9 `visible_route_surface_support`

Purpose：Provide source-grounded, status-aware evidence that could later help explain Second Reader's own `reading_route_trace` to the user through a visible route disclosure surface.

Requester：

```text
Visible Reading Route Surface Boundary, once designed
```

Allowed sources：

```text
current truth memory
source excerpts
visible trace with marker
warrant with marker
lineage only with explicit warning
```

Filtering rules：

- stale / rejected / knowledge-only material 不能作为 current source truth。
- reaction-only 可以提示“visible interest”，不能独立支撑 route disclosure。
- source-groundedness 必须标记。
- user-facing risk 必须标记。

Output shape：

```text
route_surface_evidence_support:
  candidate_source_refs[]
  candidate_memory_refs[]
  support_type
  source_groundedness_marker
  user_facing_risk_marker
  status_markers[]
```

Utilization expectation：

- 本页不生成 visible route surface object。
- 本页不决定 UX。
- 本页只提供 evidence scaffold。
- visible_route_surface_support returns evidence scaffolds only. It must not produce route-disclosure text, route options, user-facing rationale, display preference / suppression state, reading path change, navigation transition, or route-surface persistence.

#### 5.10 `evaluation_probe`

Purpose：为 Memory Quality / Callback / FVI / Planning-Memory Alignment 等 probe 提供诊断取样。

Requester：

```text
evaluation runner
benchmark probe
audit tooling
```

Allowed sources：

```text
broader snapshots
settled stores
lineage
read_audit
settlement_audit
unit_span_ledger
evaluation snapshots
failed ops, if diagnostic
```

Filtering rules：

- diagnostic only。
- 不进入 runtime prompt。
- 可访问 audit rows，但 audit rows 不是 memory。
- 可读取 failed ops / deferred candidates 用于 failure attribution，但不能把它们当 truth。

Output shape：

```text
evaluation_probe_packet:
  state_snapshot
  retrieval_trace
  utilization_trace
  audit_refs
  failure_attribution_fields
```

Utilization expectation：

- 区分 formation failure、settlement failure、retrieval failure、utilization failure、pollution。
- 不写 runtime memory。
- 不改变 projection。

#### 5.11 `manual_repair_support`

Purpose：为人工或 admin repair 提供 source-ref-preserving review context。

Requester：

```text
operator
admin repair tool
manual audit process
```

Allowed sources：

```text
settled stores
lineage
source excerpts
audit rows
evaluation reports
```

Filtering rules：

- review only；
- repair must later go through explicit source-ref-preserving settlement / management process；
- not normal runtime retrieval。

Output shape：

```text
manual_repair_review_packet:
  suspect_items
  source_refs
  source_excerpts
  lineage
  audit_refs
  recommended_review_questions
```

------

### 6. Store-specific Retrieval Rules

#### 6.1 `active_attention`

Role：hot near-term reading state。它是当前仍拉动后续阅读的 question、tension、interpretation、motif、focus 或 working distinction。它不是 stable semantic truth。

Use for：

```text
continuity_carry
active_recall
detour_support
slow_cycle_consolidation
```

Rules：

- `active / hot / carried_forward` 高优先级。
- `cooling / cooled` 低优先级，但不是 false。
- `resolved` 只在当前 source 需要解释 resolution 或 lineage 时取回。
- `dormant` 只在 explicit recall / slow-cycle 时考虑。
- `provisional` 必须带 marker。
- fallback source_ref 降权。
- missing source_refs 不作为 stable semantic support。
- 不用于替代 concept truth 或 source text。

#### 6.2 `concept_registry`

Role：definition / object / distinction / model / classification / named source-given structure。

Use for：

```text
continuity_carry
definition_support
active_recall
look_back_support via source_refs
detour_support
visible_route_surface_support
slow_cycle_consolidation
```

Rules：

- `source_supported / refined / active` 可 current truth。
- `provisional` 可返回但带 marker。
- `superseded / invalidated / rejected` lineage_only。
- `retired` historical recall only。
- concept digest 是 summary，不是 source text。
- 当需要原文定义时，必须 look_back_support。
- concept links 不能因主题相似自动扩张。

#### 6.3 `thread_trace`

Role：development-line continuity。它记录 argument、motif、contrast、question、relationship 如何跨 source spans 展开。

Use for：

```text
thread_continuity
continuity_carry
active_recall
detour_support
slow_cycle_consolidation
FVI diagnosis
```

Rules：

- 保留 source sequence when possible。
- `dormant` 表示低可见性，不表示 stale。
- `resolved_local_development` 可在 current reading 需要时取回。
- `superseded / invalidated / rejected` lineage_only。
- thread links 不能因为 theme similarity 扩张。
- theme-only association blocked。

#### 6.4 `reflective_frames`

Role：slow-cycle promoted higher-order frame。

Use for：

```text
macro continuity
slow_cycle_consolidation
visible_route_surface_support evidence
lineage_recall
```

Rules：

- 不用于 local source verification。
- reflective frame 不能覆盖 current source evidence。
- `superseded / retired` 只用于 lineage。
- `working / provisional` 必须 marker。
- `durable_definitions` 可作为 concept-like macro support，但若需原文仍 look_back。

#### 6.5 `reaction_records`

Role：visible trace / callback context / FVI diagnosis。

Use for：

```text
recent visible continuity
visible_callback_support
spontaneous callback audit
FVI diagnosis
reconsolidation
```

Rules：

- 不作为 semantic memory truth。
- retrieval result 必须标记 `visible_trace_support`。
- strong reaction 不自动变 concept/thread。
- recent reaction digest 与 full reaction lineage 分开。
- `prior_link` 可说明 visible callback relation，但不能证明 semantic truth。
- `outside_link / search_intent` 不等于 external knowledge truth 或 route guidance。

#### 6.6 `knowledge_activations`

Role：prior / external warrant ledger。

Use for：

```text
warrant_support
prior knowledge warning
visible_route_surface_support with caution
FVI diagnosis
slow_cycle_consolidation
```

Rules：

- `weak`：low priority / warning only。
- `plausible`：eligible warrant support if source trigger exists。
- `strong`：high-priority warrant support, still not source truth。
- `rejected / dropped`：lineage / audit only。
- 必须带 trigger_source_ref、reading_warrant、status、conflict_source_refs when available。
- 不能单独驱动 detour or visible route disclosure。
- 不能写入 concept truth without separate source-grounded concept op。

#### 6.7 `reconsolidation_records`

Role：reinterpretation lineage。

Use for：

```text
lineage_recall
FVI diagnosis
visible trace evolution
manual repair
```

Rules：

- 不是 semantic memory。
- 不替代 supersede chain。
- 默认不进 prompt。
- 只在 explicit lineage / diagnostic intent 下返回。

#### 6.8 Audit / ledger artifacts

Artifacts：

```text
unit_span_ledger
read_audit
settlement_audit
management_audit, if later added
evaluation artifacts
probe snapshots
```

Role：diagnostic only。

Rules：

- 不进入 runtime prompt。
- `unit_span_ledger` 可支持 source coverage / source locus，但不是 semantic memory。
- `read_audit` 可说明 Read proposed what，但 raw Read intent 不是 memory truth。
- `settlement_audit` 可说明 deterministic system did what，但不是 runtime memory。
- evaluation artifacts 不写 runtime memory。
- 只有 `evaluation_probe / manual_repair_support` 可读取 broader audit rows。

------

### 7. Status-aware Filtering and Ranking

v0 不引入 numerical ranking model。使用轻量优先级语言：

```text
must_include
high_priority
eligible
low_priority
lineage_only
audit_only
blocked
```

这些是 deterministic / policy markers，不是复杂 score。

#### 7.1 Priority classes

**must_include**

- current accepted source excerpt needed for source calibration；
- active detour required source evidence；
- explicitly requested memory_ref with current valid status；
- active_attention item that directly explains current continuation.

**high_priority**

- source_supported / refined current truth；
- active concept/thread with source_refs；
- current active_attention hot item；
- strong knowledge activation with current source trigger, only as warrant；
- source_ref exact matched.

**eligible**

- provisional with marker；
- resolved item relevant to current source；
- cooled item with current source reactivation；
- reflective frame relevant to macro continuity；
- visible reaction for visible continuity.

**low_priority**

- cooled / dormant item；
- weak knowledge activation；
- fallback_source_ref item；
- old but still source-supported item without current source pressure；
- broad reflective frame for local read.

**lineage_only**

- superseded；
- invalidated；
- rejected；
- retired；
- reconsolidated prior reaction；
- dropped knowledge activation with conflict markers.

**audit_only**

- failed ops；
- skipped ops；
- deferred candidates；
- raw audit rows；
- evaluation judge prose；
- debug events。

**blocked**

- future text；
- external web result not explicitly authorized；
- raw memory_uptake_ops as memory truth；
- unbound semantic memory；
- reaction-only semantic claim；
- knowledge-only source claim；
- theme-only thread association；
- audit dump prompt context。

#### 7.2 Status rules

- `source_supported / refined` 优先进入 current truth。
- `provisional` 可进 current packet，但必须 marker，不得用 confident wording。
- `cooled / dormant` 是低优先级，不是假。
- `resolved` 在解释当前理解、mainline restoration、lineage 或 thread closure 时可取回。
- `superseded` 普通 current truth blocked；只 lineage。
- `invalidated / rejected` 普通 current truth blocked；只 lineage / audit。
- `retired` historical recall only。
- fallback_source_ref 或 missing source_refs 降权；可触发 source_ref_recalibration。
- reaction_records 必须 visible_trace marker。
- knowledge_activations 必须 warrant marker。
- deferred candidates 默认 exclusion；slow_cycle 可作为 candidate evidence 重新 admission。
- retrieval 不应只按 recency。
- retrieval 不应只按 semantic similarity。
- v0 不引入 numerical score、embedding ranker、graph ranker。

------

### 8. Retrieval Sources and Context Assembly

#### 8.1 Six context classes

必须区分：

1. **authoritative durable store**
   JSON state files；retrieval reads them under intent/filter rules。
2. **prompt-facing projection**
   `state_packet.v1 / navigation_context / read_prompt_packet`；bounded, ephemeral, not authoritative。
3. **retrieval result packet**
   typed output from active_recall / lineage / warrant / detour_support 等；不自动进入 prompt。
4. **source excerpt**
   look_back/source calibration output；source text, not memory summary。
5. **audit trace**
   read_audit / settlement_audit / debug rows；diagnostic, not runtime context。
6. **evaluation snapshot**
   probe exports / judge packets；evaluation-only, not memory.

#### 8.2 Read prompt packet

Read sees:

```text
continuity_carry baseline
authorized active_recall result
authorized look_back excerpt
active_detour_need if in detour context
status / source_ref / warning markers
```

Read must not see:

```text
full store dump
audit dump
raw Read intents
failed ops
deferred candidates as truth
evaluation reports
future text
```

Assembly rules：

- suppress duplicate already-carried items；
- include source_refs for every semantic support item；
- include warning markers for provisional / fallback / lineage / visible_trace / warrant；
- keep source excerpts separate from memory summaries；
- cap items by intent budget；
- record assembled vs retrieved vs used.

#### 8.3 Navigate context

Navigate sees:

```text
active_attention digest
concept digest
thread digest
reflective digest
source_ref digest
continuation capsule
support flags from Navigation / Detour Policy
bounded detour source evidence
```

Navigate must not see:

```text
full recall unless authorized
stale current truth
reaction semanticization
knowledge activation as source truth
audit dump
evaluation report
```

Navigation can mark `active_recall_needed / look_back_needed` as support signals, but it does not execute full retrieval policy by itself. This inherits Navigation Policy.

#### 8.4 Slow-cycle input

Slow-cycle may see broader but bounded settled memory:

```text
active_attention
concepts
threads
reflective frames
reaction records
knowledge activations
reconsolidation records
chapter source refs
deferred candidates as candidate evidence
selected audit summaries if explicitly diagnostic
```

It must still not see raw audit dump by default. Its output is candidate / lifecycle intent, not final truth until settlement.

#### 8.5 Evaluation / probe context

Evaluation may access:

```text
broader state snapshots
audit rows
lineage
failed / skipped / deferred ops
utilization trace
runtime coverage ledger
```

Evaluation context does not enter runtime prompt and does not write runtime memory.

#### 8.6 Prompt bloat control

Rules：

- continuity baseline remains small；
- active_recall returns only missing items, not full store；
- look_back excerpt bounded by source span/window；
- lineage recall excluded unless explicit；
- already-carried duplicate suppressed；
- reaction / knowledge are marker-bearing and short；
- audit-only material not assembled；
- overbroad result trimmed or marked not_used.

------

### 9. Utilization Trace Design

Retrieval hit 不等于 successful utilization。v0 requires a compact diagnostic trace per retrieval event or per assembled supplemental bundle.

#### 9.1 Minimal fields

```text
retrieval_event_id
timestamp
requester
retrieval_intent
query_basis
source_context
store_scopes
filters_applied
budget_state
candidates_considered_count
items_returned
source_refs_returned
items_used
source_refs_used
used_for
not_used_items
no_use_reason
status_markers
warning_markers
stop_reason
failure_reason
projection_impact
visible_output_impact
memory_write_impact
detour_impact
```

MVP RetrievalUtilizationTrace:

```text
retrieval_event_id
timestamp
requester
retrieval_intent
query_basis
store_scopes
filters_applied
budget_state
items_returned
source_refs_returned
items_used
source_refs_used
used_for
not_used_items
no_use_reason
status_markers
warning_markers
stop_reason
failure_reason
projection_impact
```

Fields such as `candidates_considered_count / visible_output_impact / memory_write_impact / detour_impact` can remain v0.2 or evaluation-enriched trace fields. They are useful, but should not force the first implementation pass into a full trace schema migration.

#### 9.2 `used_for` vocabulary

```text
read_continuity
definition_support
thread_continuity
visible_callback_support
source_calibration
detour_localization
slow_cycle_candidate
visible_route_surface_support
evaluation_probe
manual_repair
not_used
```

#### 9.3 Impact fields

**projection_impact**

```text
entered_read_prompt
entered_navigation_context
entered_slow_cycle_context
suppressed_duplicate
warning_only
not_projected
```

**visible_output_impact**

```text
none
visible_callback_supported
visible_callback_blocked
visible_warning_needed
fvi_risk_detected
```

**memory_write_impact**

```text
none
informed_memory_uptake
blocked_memory_write
deferred_to_slow_cycle
deferred_to_management
```

**detour_impact**

```text
none
supported_detour_localization
requested_source_evidence
formed_detour_candidate
blocked_theme_only_detour
defer_detour
```

#### 9.4 No-use reasons

Recommended vocabulary：

```text
duplicate_already_carried
stale_only
lineage_only
invalidated_or_rejected
reaction_only
knowledge_only
source_ref_missing
source_ref_ambiguous
fallback_source_ref_only
conflicts_with_current_source
overbroad_result
budget_trimmed
deferred_candidate_only
audit_only
not_relevant_after_read
not_needed_after_source_excerpt
fvi_risk
```

#### 9.5 Trace boundary

Utilization trace is:

```text
diagnostic artifact
not prompt context
not chain-of-thought
not evaluation score
not durable reading memory
```

Utilization should distinguish declared use from observable use:

```text
items_claimed_used:
  LLM / node reports that it used these items.

items_evidenced_used:
  observable evidence shows use, such as source_refs cited in surfaced reaction, memory_refs referenced in reason summary, source_refs used in memory_uptake_ops, detour target selected from source evidence, or visible output callback explicitly grounded in retrieved item.
```

Utilization trace records observable / declared use, not hidden mental use.

It supports later Memory Quality / Callback / FVI / Planning-Memory Alignment analysis, but it does not replace those evaluation designs.

------

### 10. Retrieval Failure and Fallback

#### 10.1 Failure matrix

| Case                                      | Runtime behavior                                             | Trace result                    |
| ----------------------------------------- | ------------------------------------------------------------ | ------------------------------- |
| no relevant memory                        | continue mainline if safe                                    | `not_used / no_relevant_memory` |
| only stale memory                         | do not use as current truth; maybe look_back / lineage       | `lineage_only / stale_only`     |
| source_refs missing                       | downgrade; trigger source_ref_recalibration if useful        | `source_ref_missing`            |
| source_ref ambiguous                      | warning; bounded recalibration / look_back                   | `source_ref_ambiguous`          |
| look-back source unavailable              | record failure; do not replace with memory certainty         | `look_back_source_unavailable`  |
| budget exhausted                          | stop; no hidden search                                       | `budget_exhausted`              |
| retrieved memory conflicts current source | prefer current source; look_back; mark memory not_used/lineage | `conflicts_with_current_source` |
| reaction-only hit                         | visible trace only; no semantic claim                        | `reaction_only`                 |
| knowledge-only hit                        | warrant only; no source truth                                | `knowledge_only`                |
| deferred candidate only                   | slow-cycle candidate only; not memory truth                  | `deferred_candidate_only`       |
| audit-only evidence                       | evaluation/manual only                                       | `audit_only`                    |
| duplicate already-carried                 | suppress; log duplicate                                      | `duplicate_already_carried`     |
| overbroad result                          | trim or not_used                                             | `overbroad_result`              |
| hallucinated relation risk                | not_used or look_back                                        | `fvi_risk`                      |

#### 10.2 Fallback rules

- Failed look-back must not be silently replaced by memory confidence.
- Failed active recall must not become source truth.
- Only stale memory must not be used as current truth.
- Reaction-only / knowledge-only hit cannot justify semantic claim.
- Retrieval failure should be visible in audit / utilization trace, not silently hidden.
- Mainline should continue when comprehension is not blocked and no source-grounded exception is justified.
- If failure indicates source calibration need, trigger look_back only when policy authorizes and SourceRef locus exists.
- If failure indicates broader lifecycle issue, defer to slow-cycle / management, not runtime prompt inflation.

------

### 11. FVI and Retrieval Pollution Guardrails

#### 11.1 Guarded risks

FVI-sensitive retrieval must guard against:

```text
stale memory leakage
superseded / invalidated / rejected current use
reaction semanticization
knowledge activation source-truth化
source excerpt becoming hidden reading unit
audit dump becoming prompt context
deferred candidate becoming memory item
theme-only thread association
vector-like semantic drift even without vector DB
over-retrieval causing prompt bloat
retrieval result over-integrated into visible reaction
memory-source conflict unresolved before visible callback
```

#### 11.2 Guardrail rules

1. **Prefer source calibration over confident integration**
   If current source and memory disagree, use look_back / warning / not_used. Do not integrate confidently.
2. **Visible trace marker is mandatory**
   Reaction records may support visible callback continuity, but cannot carry semantic truth.
3. **Warrant marker is mandatory**
   Knowledge activations can support prior knowledge awareness, but cannot become book truth.
4. **Lineage marker is mandatory**
   Superseded / invalidated / rejected / retired items can appear only with lineage intent and warnings.
5. **No hidden reading through excerpts**
   Source excerpt can calibrate; if the system must actually read a source unit, detour must use Navigate → Read → settlement.
6. **No audit replay**
   Audit rows can diagnose; they cannot become runtime context unless a later explicit projection gate is designed.
7. **No theme-only thread links**
   Thread continuity requires source sequence or explicit relation, not semantic vibes.
8. **Over-retrieval is a pollution risk**
   More recalled material can increase FVI. Bounded retrieval is a quality requirement, not just efficiency.
9. **Not-used is a valid success**
   In FVI-sensitive contexts, correctly retrieving and then not using stale / weak / warning-only material is a good outcome.

------

### 12. Interaction with Current Functions

#### 12.1 `state_projection`

Responsibility：

```text
build bounded default projections
implement continuity_carry baseline
preserve source_refs and status/warning markers
support duplicate suppression via refs
```

Not responsibility：

```text
full retrieval policy
lineage expansion
audit replay
semantic ranking
```

#### 12.2 `read_context`

Responsibility：

```text
execute authorized active_recall
execute authorized look_back_support
merge supplemental contexts
return typed result packets
avoid already-carried duplicates
```

Tightening needed：

```text
add retrieval_intent labels
add status-aware filtering
classify result into current_memory_support / lineage_support / visible_trace_support / warrant_support / not_used
add stop_reason / failure_reason
```

#### 12.3 `source_spans`

Responsibility：

```text
resolve SourceRefs / SourceSpans / quote boundaries
expose fallback / ambiguity / quote_not_found markers
support source_ref_recalibration
```

Not responsibility：

```text
semantic truth judgment
memory lifecycle decision
```

#### 12.4 `source_skills`

Responsibility：

```text
provide book-local source evidence for detour localization
respect mainline_cursor visibility
return bounded source cards/windows
```

Not responsibility：

```text
memory retrieval
semantic relevance ranking
external web search
detour target ownership
```

#### 12.5 `runner`

Responsibility：

```text
orchestrate context assembly
call Navigate / Read
execute source skills
pass supplemental context
record retrieval / utilization trace through observability
settle cursor / detour continuity
```

Not responsibility：

```text
invent memory truth
hide retrieval failure
read future text
```

#### 12.6 `settlement / state_ops`

Responsibility：

```text
write memory
normalize operations
merge source_refs
apply lifecycle operations
persist state
```

Not responsibility：

```text
retrieval
prompt assembly
route-disclosure output generation
evaluation scoring
```

#### 12.7 `observability`

Responsibility：

```text
record retrieval and utilization trace
extend read_audit / settlement_audit with compact retrieval-use fields
preserve diagnosis without CoT
```

#### 12.8 `slow_cycle`

Responsibility：

```text
request broader but bounded consolidation retrieval
use candidate sets
propose lifecycle / promotion / reconsolidation candidates
```

Not responsibility：

```text
general planner
unbounded retrieval
reaction semanticization
```

#### 12.9 `evaluation`

Responsibility：

```text
read broader snapshots and audit
diagnose formation / retrieval / utilization / pollution
```

Not responsibility：

```text
write runtime memory
alter projection
feed judge reports into prompt
```

------

### 13. Compatibility with Prior Designs

This design passes the required compatibility checks:

- 不重新定义 Memory Ontology。
- 不读取 raw `memory_uptake_ops` 当 memory truth。
- 不把 deferred candidates 当 memory item。
- 不把 `reaction_records` 当 semantic memory。
- 不把 `knowledge_activations` 当 source truth。
- 不把 audit / evaluation artifacts 当 runtime prompt。
- 不让 Retrieval 写 memory。
- 不让 Retrieval 打开 detour。
- 不让 active recall 替代 look-back。
- 不让 look-back 替代 memory recall。
- 不让 memory projection 替代 source evidence。
- 不扩展 Navigate act space。
- 不设计 Visible route surface object。
- 不引入 vector DB / graph DB / Memory OS。
- 保持 `LLM proposes; deterministic runner settles`。
- 保持 SourceRef-first。
- 遵守 Simplicity and Universality。

存在的 current implementation / contract tension：

1. `nodes.py` normalization 仍会在缺失 target_store 时默认到 `active_attention`；Formation 已要求把这视为 legacy tolerant parse，而不是新 contract。Retrieval 本页因此明确只消费 settled stores，不消费 raw ops。
2. `schemas.py` 有 `resolve`，但 `nodes.py` `_STATE_OPERATION_TYPES` 未列出 `resolve`；这是 implementation alignment gap，不影响 retrieval design，但说明 status-aware retrieval 必须依赖 settled store status，而不是 raw op vocabulary。
3. `read_context.py` 当前 active_recall 返回 concepts / threads / reactions，但 status filtering 与 visible_trace markers 还不充分。本页将其作为收紧点。
4. 当前 `state_projection.py` 有 status 字段，但尚未显式区分 current truth / lineage / visible trace / warrant。本页将该区分作为 projection assembly contract。

------

### 14. Accepted Constraints and Deferred Directions

- **No vector DB by default**
  当前瓶颈是 intent、status、SourceRef、utilization trace，不是相似度基础设施。
- **No graph DB by default**
  Concept/thread links、source_refs、supersede chains 可先在 JSON state 表达。
- **No Memory OS**
  Reading Companion 不是通用 memory runtime。
- **No retriever agent**
  Retrieval v0 是 deterministic / policy-guided helper contract，不是自治 agent。
- **No memory manager agent**
  Management 是 lifecycle contract，已有 slow-cycle / settlement surfaces。
- **No full-store prompt dump**
  Projection must remain bounded。
- **No audit dump prompt**
  Audit is diagnosis, not runtime context。
- **No hidden search**
  source skills are book-local and bounded；external search 不在 v0 retrieval scope。
- **No future text**
  Source calibration / detour support 只能在 allowed reading frontier 内。
- **No visible route surface object**
  `visible_route_surface_support` 只提供 future evidence scaffold。
- **No evaluation rubric**
  `evaluation_probe` 是接口，不是 rubric。
- **No full implementation roadmap**
  本页只给 readiness notes，不拆 Codex tasks。
- **No numerical ranking model in v0**
  使用 priority classes，不使用 score model。
- **No broad RAG loop**
  Retrieval is intent-aware memory/source support, not general RAG.
- **No raw Read intent retrieval**
  Read proposals 必须经过 settlement 才可作为 memory truth。

------

### 15. What This Design Changes or Tightens

#### 15.1 保留

- 保留 `state_projection` fixed packet as continuity baseline。
- 保留 `read_context` active_recall / look_back helper。
- 保留 paragraph-offset SourceRef / SourceSpan / SourceCursor。
- 保留 file-based JSON / JSONL runtime artifacts。
- 保留 `Navigate.choose_next_unit → Read → Runner settlement`。
- 保留 source skills as book-local detour evidence layer。

#### 15.2 收紧

- 把 fixed packet 正式命名为 `continuity_carry`。
- 增加 retrieval intent taxonomy。
- 把 status-aware filtering 写成 contract。
- 区分 current_truth / lineage / visible_trace / warrant / source_excerpt。
- 强化 reaction_records 的 visible_trace marker。
- 强化 knowledge_activations 的 warrant marker。
- 明确 fallback_source_ref / ambiguous_source_ref 降权。
- 明确 retrieval hit 不等于 utilization success。
- 新增 utilization trace contract。
- 明确 active_recall 不替代 look-back。
- 明确 failed look-back 不可被 memory certainty 替代。
- 明确 detour_support 不能仅用 memory projection 选 target。

#### 15.3 重新解释

- `source_ref_digest` 是 evidence spine digest，不是 source corpus search。
- `recent_reactions` 是 visible trace digest，不是 semantic support。
- `knowledge_use_mode` 是 warrant mode，不是 source truth mode。
- `supplemental_context` 是 retrieval result assembly，不是 arbitrary prompt extension。

#### 15.4 延后

- vector / graph / ranking；
- full Visible Reading Route Surface Boundary；
- full Audit / Evaluation design；
- Implementation Handoff；
- full schema migration；
- multi-hop graph retrieval；
- broad RAG pipeline；
- retriever agent / memory manager agent。

------

### 16. Design Implications for Later Pages

#### 16.1 Visible Reading Route Surface Boundary

Visible Reading Route Surface Boundary must consume `visible_route_surface_support` evidence scaffold rather than direct memory stores. It must preserve source-groundedness, status markers, visible_trace / warrant warnings, and it must not create route controls or navigation transitions.

#### 16.2 Slow-cycle / Macro-planning

Slow-cycle 可使用 `slow_cycle_consolidation` candidate set，但 deferred candidates 仍需重新 admission。Reaction records 用于 visible lineage / reconsolidation，knowledge activations 用于 warrant review。

#### 16.3 Memory Audit / Evaluation

Audit / Evaluation 应使用 utilization trace 区分：

```text
retrieval failure
utilization failure
formation failure
settlement failure
FVI pollution
```

但本页不定义评分 rubric。

#### 16.4 Planning Audit / Evaluation

Planning audit 可使用 `memory_refs_used / source_refs_used / used_for / no_use_reason / budget_state / stop_reason` 来诊断 active_recall、look_back、detour_support 的使用质量。

#### 16.5 Integrated Mechanism Design

Integrated design 应把 `state_projection → read_context → source_spans → runner → observability` 连接成统一 context assembly / utilization trace loop。

#### 16.6 Implementation Handoff

Implementation Handoff 可把本页的 intent labels、markers、trace fields 转成 schema/prompt/audit changes；本页不拆 task list。

------

### 17. Implementation Readiness Notes

#### Pre-Handoff Gate

Before Codex implementation, convert this design into a Memory Retrieval & Utilization Handoff Packet containing:

```text
MVP retrieval intent labels
marker vocabulary
current_support / lineage filtering rules
compact utilization trace fields
read_context changes
state_projection changes
observability changes
explicit non-goals
```

#### 17.1 Ready for narrow implementation

可以进入小窗口验证：

```text
retrieval_intent labels in read_context / observability
status markers in projection packets
current_truth vs lineage warning markers
items_returned / items_used / no_use_reason compact trace
source_refs_used / memory_refs_used
already-carried duplicate suppression logging
stale memory warning markers
reaction_records visible_trace marker
knowledge_activations warrant marker
budget / stop reason enrichment
fallback_source_ref warning
source_ref_ambiguous warning
```

#### 17.2 Needs Audit / Evaluation design first

```text
full utilization trace schema migration
Memory Quality / Callback / FVI diagnostic aggregation
formal retrieval quality metrics
full audit report shape
failed-op / deferred-candidate diagnostic rules
```

#### 17.3 Needs Visible Reading Route Surface Boundary first

```text
visible_route_surface_support evidence-to-display-boundary mapping
user-facing risk vocabulary
visible reading note wording
no_user_surface_needed handling
```

#### 17.4 Needs Slow-cycle / Macro-planning first

```text
slow_cycle_consolidation broad candidate budget
promotion candidate source weighting
cross-chapter carry-forward retrieval priority
macro-planning obligations
```

#### 17.5 Needs Implementation Handoff

```text
exact field names
backward compatibility plan
storage location for retrieval_utilization_audit
prompt wording changes
budget constants
test fixtures
```

#### 17.6 Explicitly not now

```text
vector DB
graph DB
retrieval ranking model
full RAG pipeline
retriever agent
memory manager agent
visible route surface object
full evaluation rubric
full audit schema migration
multi-hop graph retrieval
full implementation roadmap
```

------

### 18. Optional Open Questions

None critical at this phase.

Non-blocking questions:

1. **Status vocabulary alignment**
   Current stores use heterogeneous status strings. Exact enum harmonization should wait for Audit / Implementation Handoff. It does not block intent labels and warning markers.
2. **SourceRef recalibration write path**
   v0 says recalibration produces a result / warning / repair candidate. Whether it can directly write repaired source_refs should depend on Management / Implementation Handoff.
3. **Lineage visibility in user-facing callbacks**
   Whether a user-visible callback may mention superseded lineage belongs to Visible Reading Route Surface Boundary / UX policy, not this page.

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

This section states what project evidence supports the design, what it shows, how it supports the design, and whether runtime-artifact validation is missing.

### A.1 Product and source-of-truth docs

`docs/product-overview.md` defines the product as a text-grounded, legible, self-propelled co-reading mind rather than a summary engine or service assistant. This supports the decision that retrieval should preserve source-grounded reading continuity, not become user-profile memory or generic assistant recall. Runtime-artifact validation gap: none needed for product boundary.

`docs/current-state.md` records the paragraph-offset `SourceCursor / SourceSpan` cutover, SourceRef cutover, settlement diagnostic, and current long-span direction around Memory Quality / Spontaneous Callback / FVI. This supports SourceRef-first retrieval, current fixed packet tightening, and the need to separate retrieval / utilization / FVI diagnosis. It is repo-recorded diagnostic evidence, not this round’s independent runtime-row audit.

`docs/source-of-truth-map.md` says the workspace is repo-first and durable information belongs in canonical repo docs / state files. This supports file-based JSON / JSONL retrieval and diagnostic trace rather than database-first migration.

### A.2 Mechanism platform and catalog docs

`docs/backend-reading-mechanism.md` states that `public/book_document.json` is the only shared parsed-book truth; paragraph layer is stable substrate; `attentional_v2` uses paragraph + char-offset cursor and inline SourceRef; no shared SourceRef registry exists. This supports the design’s distinction between source corpus, source excerpt, SourceRef digest, and reading memory.

`docs/backend-reading-mechanisms/README.md` identifies `attentional_v2` as current default/live mechanism and `iterator_v1` as fallback. This supports designing in place rather than greenfield.

`docs/backend-reading-mechanisms/attentional_v2.md` documents the live Reading Runner loop, Navigate.choose_next_unit, Read, post-read settlement, detour through the same loop, state_packet.v1, active_recall/look_back supplementation, and file artifacts. This directly supports the decision to tighten `state_projection / read_context / source_ref / audit` rather than replacing them.

### A.3 `schemas.py`

`schemas.py` shows current contracts: `ContextRequestKind = active_recall / look_back`, `SourceRef` as inline citation, state stores for active_attention / concept_registry / thread_trace / reflective_frames / knowledge_activations / reaction_records / reconsolidation_records, `ReadUnitResult`, `StateOperation`, `LocalContinuityState`, and `NavigateActTraceEntry`. It supports the design’s store-specific retrieval rules and function boundary mapping. It is stable contract-level evidence, though exact status vocabulary remains implementation-alignment work.

### A.4 `state_projection.py`

`state_projection.py` builds `state_packet.v1`, active_attention digest, concept digest, thread digest, reflective frame digest, recent reactions, source_ref digest, refs, continuation capsule, navigation context, and read prompt packet. This supports `continuity_carry` as the MVP baseline. It also reveals the gap: projection is bounded but not yet fully status-aware / current-vs-lineage aware.

### A.5 `read_context.py`

`read_context.py` already distinguishes look_back from active_recall. Look_back returns source excerpts; active_recall returns concepts, threads, reactions not already carried. This supports the design’s separation of memory recovery and source calibration. It also supports the tightening need: add status filtering, support-channel classification, and utilization trace.

### A.6 `source_spans.py`

`source_spans.py` defines SourceCursor, SourceSpan, SourceRef, quote resolution, fallback markers, exact anchor resolution, source_unit_from_span, and dedupe. This supports source_ref_recalibration, look_back_support, and warning markers for fallback / ambiguous / quote_not_found cases.

### A.7 Source skills

`skills/runtime.py` allows only book-local `source_map_overview / source_scope_drilldown / source_window_fetch`, with provenance bounded by mainline cursor. `skills/source_skills.py` enforces visible-to-mainline source ranges and blocks future text. These support detour_support as source evidence, not hidden search or memory retrieval.

### A.8 `runner.py`

`runner.py` shows Reading Runner as the orchestrator: runtime bundle, navigation, skill execution, read, settlement, detour continuity, audit, persistence. `_apply_detour_need` demonstrates detour state belongs to local_continuity, not retrieval. This supports the interaction boundary: retrieval may support detour localization but cannot open detour.

### A.9 `nodes.py`

`nodes.py` normalizes LLM outputs, filters surfaced reactions, normalizes detour need, and normalizes state ops. It shows a contract gap: `_STATE_OPERATION_TYPES` lacks `resolve` while schema includes it, and missing target_store can default to active_attention. This supports the design rule that retrieval must consume settled stores, not raw Read intent or normalized raw ops.

### A.10 `prompts.py`

`prompts.py` enforces Navigate as next-unit selector / detour localizer; no mainline skills; detour source skills only; no external web; no future text; Read only targets active_attention / concept_registry / thread_trace; surfaced reaction is separate; detour_need is planning intent. This supports current function boundaries and guardrails against retrieval pollution.

### A.11 `state_ops.py`

`state_ops.py` applies operations deterministically, merges source_refs, handles active_attention cooling/resolution/drop, concept/thread update/resolve/drop, append-only reaction/reconsolidation records, and reflective supersede without overwriting statements. This supports status-aware filtering and current truth vs lineage distinction.

### A.12 `storage.py`

`storage.py` defines file-based mechanism-private artifacts, including memory stores, continuity, unit_span_ledger, read_audit, settlement_audit, and memory_quality probe export. This supports no-vector/no-graph v0 and file-first retrieval.

### A.13 `observability.py`

`observability.py` records read_audit and settlement_audit with carry-forward refs, context_request, supplemental refs, supplemental_steps, stop_reason, budget_exhausted, memory op counts, and compact deltas. This supports extending existing audit with utilization trace rather than creating a separate opaque layer.

### A.14 `slow_cycle.py`

`slow_cycle.py` handles durable reaction truth, reflective promotion, reconsolidation, chapter consolidation, and compatibility projection. It preserves surfaced fields like prior_link / outside_link / search_intent as reaction semantics. This supports reaction_records as visible trace and slow_cycle_consolidation as candidate-oriented retrieval.

### A.15 `knowledge.py`

`knowledge.py` makes knowledge activation a warrant-ledger mechanism: live statuses are weak/plausible/strong; only warranted plausible/strong activations change knowledge_use_mode; cool/drop/supersede become weak/dropped/rejected. This supports warrant retrieval and the rule that knowledge activations are not book truth.

### A.16 `backend-reader-evaluation.md`

The evaluation constitution defines the current long-span direction as Memory Quality, Spontaneous Callback, and False Visible Integration; it treats read_audit / settlement_audit / unit_span_ledger as runtime evidence, not benchmark targets by themselves. This supports utilization trace as diagnostic input, not evaluation score.

### A.17 Decision log and task registry

`docs/history/decision-log.md` preserves major decisions and rejected alternatives; it documents why the project converged on source substrate, mechanism-private artifacts, product-first evaluation, and attentional_v2 evolution. This supports using current accepted architecture as design basis rather than reopening greenfield choices.

`docs/tasks/registry.md` shows the active structural rework history: state_packet.v1, bounded active_recall/look_back, primary stores, SourceRef cutover, source skills, unified Navigate.choose_next_unit, and current long-span Memory Quality direction. This supports the implementation-readiness distinction: narrow trace/marker additions are ready; broader audit/eval/visible route disclosure remain separate tasks.

------

## B. Upstream Design Basis

### B.1 From C设计-设计路线

Design route places this page after Memory Ontology, Formation, Management, and Detour / Look-back / Active Recall. It says Design7 must solve retrieval intent taxonomy, context assembly, status-aware filtering, and utilization trace, and must not become Visible Reading Route Surface Boundary, Audit / Evaluation rubric, or Implementation Handoff. This directly defines the scope of this page.

### B.2 From C设计0 Shared Charter

P0 provides the hard boundaries: source corpus / reading memory / planning state / audit / visible reaction / visible route disclosure / prior knowledge / evaluation must stay separate; retrieval must be intent-aware and bounded; prompt-facing projection is not durable state; audit is diagnosis; no vector/graph/Memory OS by default. This page turns those into retrieval filtering and assembly rules.

### B.3 From C设计1 Memory Ontology

Memory Ontology defines store identity. This page does not redefine stores; it defines how each store may be retrieved and used:

- active_attention as hot state；
- concept_registry as concept/object/definition layer；
- thread_trace as development line；
- reflective_frames as slow-cycle promoted frame；
- reaction_records as visible trace；
- knowledge_activations as warrant ledger；
- reconsolidation_records as reinterpretation ledger；
- audit/evaluation as non-runtime memory.

### B.4 From C设计3 Formation & Settlement

Formation defines `memory_uptake_ops` as bounded write intent and settlement as deterministic authority. This page uses that to block retrieval from raw Read intents, failed ops, skipped ops, and deferred candidates as memory truth.

### B.5 From C设计5 Management & Evolution

Management defines visibility lifecycle vs semantic validity lifecycle, current_truth_projection vs lineage_projection, superseded / invalidated / rejected filtering, provisional markers, cooled/dormant low priority, reaction visible trace, knowledge warrant ledger, deferred candidates exclusion, and warning markers. This page turns those lifecycle constraints into retrieval priority classes and prompt assembly rules.

### B.6 From C设计6 Detour / Look-back / Active Recall Policy

Design6 defines:

```text
active_recall = memory recovery
look_back = source calibration
detour = planning path deviation
```

It also defines active recall not writing memory / cursor / detour, look-back returning source excerpt, detour using the same Navigate → Read → settlement loop, and audit fields like `memory_refs_used / source_evidence_used / used_for / no_use_reason`. This page does not rewrite triggers; it designs retrieval execution and utilization trace after those policies authorize the move.

### B.7 From Planning Ontology and Navigation Policy

Planning Ontology says Planning uses Memory but does not own Memory; Navigation consumes bounded memory projections and remains source-grounded next-unit selector / detour localizer. Navigation Policy says Navigate can mark active_recall_needed / look_back_needed, but must not become full retrieval executor. This page preserves that interface.

### B.8 From Memory Assessment

Memory Assessment identifies that current retrieval is biased toward fixed packet; the next step is intent-aware retrieval, metadata / source_refs / status / links / chapter scope before vector DB / graph DB, and utilization trace recording what was retrieved, used, used_for, and not_used. This page directly implements that diagnosis.

### B.9 From Planning Assessment

Planning Assessment distinguishes active_recall, look_back, detour; says look-back is calibration, detour value depends on information scent + reading value, and audit needs source evidence / memory used / uncertainty / budget reason / restore-mainline reason. This page uses those as planning-facing guardrails, not as a full planning redesign.

------

## C. External Rationale, as Filtered Through the Assessments

This section uses external work only as rationale after project-specific constraints. It does not override accepted project designs.

### C.1 Mem0

Original problem：production-ready long-term memory operations for agents.

Supports：operation-centric memory design, metadata, explicit add/search/update/delete, and item-level trace.

Similarity：Reading Companion also needs memory item identity, source_refs, operation trace, update/delete/supersede discipline.

Difference：Mem0 is general agent/user memory; Reading Companion is source-grounded book-reading state.

Local adaptation：borrow operation and metadata discipline; do not import vector/graph infra by default.

Do not copy：default vector search / graph memory as first move.

Support type：Direct for operation contract; Boundary for infra.

### C.2 Zep

Original problem：temporal knowledge graph for dynamic agent memory.

Supports：facts vs episodes vs observations, temporal validity, invalidation, evidence-backed memory.

Similarity：Reading Companion also needs old understanding vs current truth vs lineage.

Difference：Reading Companion does not need enterprise temporal KG / graph DB in v0.

Local adaptation：borrow validity / invalidation / observation separation; keep JSON SourceRef chains.

Do not copy：graph DB, enterprise context block.

Support type：Direct for validity concepts; Boundary for graph infra.

### C.3 LangGraph Memory Concepts / LangMem

Original problem：framework-level semantic / episodic / procedural memory and hot-path vs background memory updates.

Supports：separating semantic memory, episodic trace, procedural memory, and background consolidation.

Similarity：Reading Companion needs concept/thread/reflective vs reaction/audit vs policy separation.

Difference：Reading Companion’s content memory is source-grounded reading state, not generic app memory.

Local adaptation：use hot-path vs slow-cycle distinction; avoid prompt self-refinement in content retrieval v0.

Do not copy：general memory manager agent / procedural prompt rewriting.

Support type：Direct for memory type hygiene; Boundary for manager agent.

### C.4 Letta / MemGPT

Original problem：manage finite context via core vs archival memory / memory blocks.

Supports：prompt-facing memory vs durable external state separation.

Similarity：`state_packet.v1` is prompt-facing projection; durable stores are authoritative.

Difference：Letta/MemGPT are more OS-like / chat-agent oriented.

Local adaptation：borrow label/description/limit style discipline; reject Memory OS migration.

Support type：Direct for projection boundary; Negative for OS-style adoption.

### C.5 LongMemEval

Original problem：benchmark long-term memory by separating stages such as retrieval and reading/use.

Supports：retrieval vs utilization distinction.

Similarity：Reading Companion must know whether failure is formation, retrieval, utilization, or visible integration.

Difference：LongMemEval is chat benchmark, not reading mechanism.

Local adaptation：use stage decomposition; keep evaluation rubric separate.

Support type：Direct for stage separation.

### C.6 HaluMem

Original problem：memory system hallucination can occur at extraction, update, retrieval, and QA/use stages.

Supports：retrieval pollution and operation-level diagnosis.

Similarity：Reading Companion FVI risk can come from stale retrieval, reaction semanticization, knowledge source-truthing.

Difference：Reading Companion’s visible output is reading reaction, not generic QA answer.

Local adaptation：record utilization trace; prefer not_used / warning over confident integration.

Support type：Direct for pollution risk.

### C.7 MemGuide

Original problem：intent-driven memory selection for goal-oriented multi-session agents.

Supports：retrieval should know why it is retrieving.

Similarity：Reading Companion needs continuity_carry, active_recall, look_back_support, detour_support, slow_cycle_consolidation, evaluation_probe.

Difference：Reading Companion’s intents are reading-specific and SourceRef-first.

Local adaptation：intent taxonomy without adding retriever agent.

Support type：Direct.

### C.8 ComoRAG

Original problem：long narrative reasoning needs dynamic workspace and impasse-triggered retrieval.

Supports：retrieval as response to comprehension impasse / narrative continuity.

Similarity：Reading Companion active_recall / look_back should trigger when current reading needs it.

Difference：ComoRAG is RAG over narrative tasks, not source-order co-reading loop.

Local adaptation：borrow impasse-trigger logic; reject broad RAG loop.

Support type：Analogical / Boundary.

### C.9 GraphRAG / RAPTOR / HippoRAG

Original problem：multi-granularity / graph / hierarchical retrieval for corpus QA and multi-hop reasoning.

Supports：sometimes local/global or multi-level retrieval matters.

Similarity：Reading Companion has concept/thread/reflective layers.

Difference：Reading Companion already has file-based source-grounded memory stores; current bottleneck is contract, not index infra.

Local adaptation：borrow multi-granularity idea; keep lightweight links and reflective frames.

Do not copy：graph DB, community summaries, tree index as v0 infrastructure.

Support type：Boundary / Negative.

### C.10 Generative Agents

Original problem：agents need memory stream, recency/relevance/importance retrieval, and reflection.

Supports：not every observation becomes high-level memory; reflection is second-order; retrieval involves more than recency.

Similarity：Reading Companion also separates Read-path memory from slow-cycle reflective frames.

Difference：Generative Agents is social simulation, not SourceRef-first reading.

Local adaptation：use recency/relevance/importance only as analogy; actual v0 uses status/source_refs/intent priority.

Support type：Analogical.

### C.11 MemoryBank

Original problem：long-term companion memory with forgetting / reinforcement.

Supports：visibility decay and refresh as lifecycle analogy.

Similarity：cooled/dormant items can be low-priority without being false.

Difference：MemoryBank focuses user/personality memory; Reading Companion does not.

Local adaptation：borrow visibility decay, not user-profile memory.

Support type：Analogical / Negative.

### C.12 Information Foraging

Original problem：humans navigate information spaces by scent, value, and cost.

Supports：detour_support should consider source_scent, detour_value, continuity_cost.

Similarity：Reading Companion decides whether to stay mainline, look back, or detour.

Difference：book reading has stronger source-order discipline than web foraging.

Local adaptation：use qualitative markers, not ranking model.

Support type：Analogical / Direct for detour boundary.

### C.13 Rereading effect / Metacomprehension

Original problem：rereading can improve comprehension calibration; readers’ self-monitoring can be inaccurate.

Supports：look-back as source calibration, not comfort rereading.

Similarity：Reading Companion must verify source when memory and current source conflict or when FVI risk is high.

Difference：human cognition evidence does not prescribe code triggers.

Local adaptation：look_back_support is bounded and SourceRef-based.

Support type：Direct for look-back rationale.

### C.14 ReAct / ReWOO

Original problem：reasoning-action loops and decoupled observation planning in tool-using LLM agents.

Supports：bounded source-evidence loops for detour, and separating evidence gathering from final decision.

Similarity：Navigate detour mode uses source skills and then chooses/defer.

Difference：Reading Companion is not a general tool agent; source skills are book-local.

Local adaptation：use in detour_support only; not main reading loop.

Support type：Analogical / Boundary.

### C.15 Adaptive Navigation Support

Original problem：educational hypermedia can guide navigation through annotation/direct guidance while preserving learner context.

Supports：visible_route_surface_support should remain evidence-only support for future route disclosure, not internal navigation.

Similarity：future Reading Companion route disclosure must be source-grounded and low-interruption.

Difference：this page does not design route disclosure UX or user route control.

Local adaptation：only define evidence scaffold boundary.

Support type：Boundary.

------

## D. Simplicity and Universality Check

| Check                                                        | Result |
| ------------------------------------------------------------ | ------ |
| 优先收紧 `state_projection / read_context` 而非新增基础设施  | Pass   |
| 避免 vector DB / graph DB / Memory OS                        | Pass   |
| 避免 retriever agent / memory manager agent                  | Pass   |
| 保持 SourceRef-first                                         | Pass   |
| 保持 status-aware filtering                                  | Pass   |
| 区分 current truth / lineage / visible trace / warrant / source excerpt | Pass   |
| 避免 reaction_records 语义化                                 | Pass   |
| 避免 knowledge_activations source-truth 化                   | Pass   |
| 避免 audit trace 回流 prompt                                 | Pass   |
| 支持后续 Visible Route Disclosure / Audit / Evaluation / Implementation，但不过早实现 | Pass   |

Remaining complexity risks：

1. `utilization_trace` 字段过多可能在 implementation 中膨胀。v0 应先做 compact trace。
2. status vocabulary 可能跨 store 不一致。先用 markers / reason codes，后续再 enum。
3. active_recall 与 look_back 可能被 prompt 混淆。必须在 prompt / trace 中保留 intent labels。
4. source_ref_recalibration 可能滑向 repair workflow。本页只允许 result / warning，实际 write path 等 Implementation Handoff。
5. visible_route_surface_support 可能被误用成 route disclosure policy。必须保持 evidence-only，且不能进入 current runtime prompt。

------

## E. Source Usage List

| External source                                              | Authors / Organization                              | Year      | Stable URL                                                   | Used for                                                   | Support type          |
| ------------------------------------------------------------ | --------------------------------------------------- | --------- | ------------------------------------------------------------ | ---------------------------------------------------------- | --------------------- |
| Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | Prateek Chhikara et al.                             | 2025      | https://arxiv.org/abs/2504.19413                             | operation-centric memory and metadata boundary             | Direct / Boundary     |
| Mem0 Memory Operations Docs                                  | Mem0                                                | 2025–2026 | https://docs.mem0.ai/core-concepts/memory-operations/add     | add/search/update/delete as operation contract             | Direct                |
| Zep: A Temporal Knowledge Graph Architecture for Agent Memory | Preston Rasmussen et al.                            | 2025      | https://arxiv.org/abs/2501.13956                             | temporal validity and invalidation                         | Direct / Boundary     |
| Zep Graph / Facts / Observations Docs                        | Zep                                                 | 2025–2026 | https://help.getzep.com/graph-overview                       | facts / entities / episodes / observations separation      | Direct                |
| LangGraph Memory Concepts                                    | LangChain                                           | 2025–2026 | https://docs.langchain.com/oss/python/concepts/memory        | semantic / episodic / procedural and hot/background memory | Direct                |
| LangMem                                                      | LangChain                                           | 2025–2026 | https://github.com/langchain-ai/langmem                      | background memory pattern and procedural boundary          | Boundary              |
| MemGPT                                                       | Charles Packer et al.                               | 2023      | https://arxiv.org/abs/2310.08560                             | virtual context / memory hierarchy as boundary             | Boundary              |
| Letta Memory Blocks Docs                                     | Letta                                               | 2025–2026 | https://docs.letta.com/guides/core-concepts/memory/memory-blocks | prompt-facing memory block contract                        | Direct                |
| Letta Archival Memory Docs                                   | Letta                                               | 2025–2026 | https://docs.letta.com/guides/ade/archival-memory/           | core vs archival memory distinction                        | Direct                |
| LongMemEval                                                  | Di Wu et al.                                        | 2024      | https://arxiv.org/abs/2410.10813                             | retrieval vs reading/use stage separation                  | Direct                |
| HaluMem                                                      | Ding Chen et al.                                    | 2025      | https://arxiv.org/abs/2511.03506                             | memory-induced hallucination / operation-level pollution   | Direct                |
| MemGuide                                                     | Yiming Du et al.                                    | 2026      | https://ojs.aaai.org/index.php/AAAI/article/view/40313       | intent-driven memory selection                             | Direct                |
| ComoRAG                                                      | Juyuan Wang et al.                                  | 2025      | https://arxiv.org/abs/2508.10419                             | impasse-triggered narrative recall                         | Analogical / Boundary |
| GraphRAG                                                     | Darren Edge et al. / Microsoft Research             | 2024      | https://arxiv.org/abs/2404.16130                             | local/global retrieval as boundary                         | Boundary              |
| GraphRAG Docs                                                | Microsoft Research                                  | 2024–2026 | https://microsoft.github.io/graphrag/index/overview/         | multi-granularity retrieval boundary                       | Boundary              |
| RAPTOR                                                       | Parth Sarthi et al.                                 | 2024      | https://arxiv.org/abs/2401.18059                             | hierarchical retrieval as analogy                          | Boundary              |
| HippoRAG                                                     | Bernal Jiménez Gutiérrez et al.                     | 2024      | https://arxiv.org/abs/2405.14831                             | graph-indexed multi-hop retrieval boundary                 | Boundary              |
| Generative Agents                                            | Joon Sung Park et al.                               | 2023      | https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/ | recency / relevance / importance and reflection analogy    | Analogical            |
| MemoryBank                                                   | Wanjun Zhong et al.                                 | 2024      | https://ojs.aaai.org/index.php/AAAI/article/view/29946       | visibility decay / refresh analogy                         | Analogical            |
| Information Foraging                                         | Peter Pirolli, Stuart K. Card                       | 1999      | https://doi.org/10.1037/0033-295X.106.4.643                  | source scent / value / cost for detour support             | Analogical / Direct   |
| The Rereading Effect                                         | Katherine A. Rawson, John Dunlosky, Keith W. Thiede | 2000      | https://doi.org/10.3758/BF03209348                           | look-back as calibration                                   | Direct                |
| Metacomprehension                                            | John Dunlosky, Amanda R. Lipko                      | 2007      | https://doi.org/10.1111/j.1467-8721.2007.00509.x             | source calibration and self-monitoring caution             | Direct                |
| ReAct                                                        | Shunyu Yao et al.                                   | 2022      | https://arxiv.org/abs/2210.03629                             | bounded evidence/action loop analogy                       | Analogical            |
| ReWOO                                                        | Binfeng Xu et al.                                   | 2023      | https://arxiv.org/abs/2305.18323                             | decoupled evidence gathering boundary                      | Analogical            |
| Adaptive Navigation Support in Educational Hypermedia        | Peter Brusilovsky                                   | 2003      | https://doi.org/10.1111/1467-8535.00345                      | route-disclosure boundary only                            | Boundary              |
