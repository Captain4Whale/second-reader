# Memory Formation & Settlement Design v0

## 1. Scope and Purpose

本设计定义 Reading Companion / Second Reader 在 Phase 2.1 的 **Memory Formation & Settlement** 机制。

它继承 P0 Charter 的最高边界：**LLM proposes; deterministic runner settles**。`Read` 可以提出阅读印象、可见反应、有限 memory write intent 与 detour need；最终 SourceRef 绑定、schema normalization、store admission、ID、merge、state mutation、audit outcome 与 durable persistence 由 Runner / settlement / state_ops 确定性完成。

它继承 Memory Ontology v0：reading memory 是从 accepted source units 中形成的 source-grounded reading state；source corpus 不是 memory；visible reaction 不是 semantic memory；prompt-facing projection 不是 authoritative state；Read-path 只能提出 `memory_uptake_ops`，且 target stores 只能是 `active_attention / concept_registry / thread_trace`。

它兼容 Planning Ontology v0：Planning 使用 Memory，但不拥有 Memory；`detour_need` 是 planning intent，不是 memory op；`active_recall` 是 memory recovery，`look_back` 是 source calibration，`detour` 是 planning path deviation。

本页只设计 **read-path memory formation 与 deterministic settlement**。它为后续 Memory Management / Evolution、Retrieval / Utilization、Audit / Evaluation、Planning Policy、Implementation Handoff 提供 contract，但不替这些页面展开设计。

本页不是：

- Memory Ontology 重写；
- Planning Ontology 重写；
- Agent Memory 外部综述；
- `attentional_v2` greenfield redesign；
- Codex task list 或实现路线图；
- full lifecycle / retrieval / evaluation 设计。

本设计的核心目标是让现有链路：

```text
Read.memory_uptake_ops
  → settlement
  → state_ops
  → audit
```

变得更清晰、更可靠、更可诊断。

------

## 2. Current Implementation Understanding

当前默认机制是 `attentional_v2`，`iterator_v1` 是 explicit fallback / legacy-compatible path。机制目录把 `attentional_v2` 标为 current default/live mechanism，`iterator_v1` 标为 fallback。

当前 `attentional_v2` 主循环是：

```text
survey orientation
  → Navigate.choose_next_unit
  → Read
  → Reading Runner post-read settlement
  → cursor advance / ledger / audit
  → chapter-end slow-cycle
```

`Navigate.choose_next_unit` 从 paragraph-offset preview 中选择下一 readable unit，返回 exact `end_anchor_text`；Runner 把它解析成 end-exclusive `SourceSpan`，构造 accepted unit 后交给 `Read`；`Read` 输出 `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`；Runner 再应用 memory uptake、持久化 reactions、写 audit、记录 accepted unit span，并推进 cursor。机制文档明确：ordinary forward progression 是 deterministic settlement 后的默认行为，不再由 LLM route action 决定。

### 2.1 `ReadUnitResult`

代码 schema 中 `ReadUnitResult` 当前包含：

```text
reading_impression
surfaced_reactions[]
memory_uptake_ops[]
detour_need?
```

同一 schema 也定义了 `SourceRef`、`StateOperation`、`StateOperationType`、`SurfacedReaction`、`DetourNeed`、active/concept/thread/reflective/reaction/knowledge/reconsolidation stores。

### 2.2 `reading_impression`

`reading_impression` 是读完当前 accepted unit 后留下的自然印象。当前机制文档和 prompts 都把它定位为 temporary read-after impression，不是 durable memory。

### 2.3 `surfaced_reactions`

`surfaced_reactions[]` 是 visible reaction intent。Prompt 要求每条 surfaced reaction 的 `source_quote` 必须是 current unit 中的 exact quote，且 visible `content` 不能泄漏 internal handles。

`nodes.py` 会过滤 source_quote 不在当前 unit 的 reaction，也会过滤 visible content 中类似 `c1-s1135`、`source:...`、`thread:...` 之类 internal reference markup。

持久化时，`slow_cycle.py` 的 reaction builder 会把 surfaced reaction 转成 `reaction_records`，保留 `primary_source_ref`、`prior_link`、`outside_link`、`search_intent` 等 visible trace fields。

### 2.4 `memory_uptake_ops`

Prompt 已经把 `memory_uptake_ops` 收紧为 bounded memory ops：只记录读完当前 unit 后“应该继续可用”的内容；只允许 target：

```text
active_attention
concept_registry
thread_trace
```

并明确禁止写 `reflective_frames`、`reaction_records`、history/audit layers，也禁止 whole-object rewrite。Prompt 还要求当 operation 需要 source evidence 时，在 payload 中加入 `source_quote` 和可选 `source_role`，由 Runner 解析成 paragraph + char-offset `source_refs`。

### 2.5 `detour_need`

`detour_need` 是 `Read` 提出的 planning intent。当前实现中 Runner 把它写入 `local_continuity`，并由后续 `Navigate.choose_next_unit` 在 active-detour mode 下定位、请求 source evidence 或 defer。Runner 中 `_apply_detour_need` 会把 open detour 写成 `detour_trace`，resolved/abandoned 会更新 active detour 状态。

### 2.6 SourceRef / SourceSpan / SourceCursor

当前 source substrate 是 paragraph layer。`SourceCursor` 包含 `chapter_id / chapter_ref / paragraph_index / char_offset`；`SourceSpan` 是 end-exclusive `[start_cursor, end_cursor)`；`SourceRef` 是 inline paragraph-offset citation，不是 registry entry。`source_ref_from_unit()` 会把 unit-local quote 解析成 paragraph-offset SourceRef，并记录 resolution status，例如 `matched`、`ambiguous_first_match`、`quote_not_found`、`fallback_unit_span`。

### 2.7 state_ops apply and merge

`state_ops.py` 当前是 deterministic state mutation layer：

- active_attention 支持 create / update / reactivate / cool / resolve / close / link / drop；
- concept/thread 中 append / create / link 归一化为 update；
- close 归一化为 resolve；
- source refs 通过 `dedupe_source_refs` merge / dedupe；
- reflective item supersede 会标记旧 item 为 `superseded`，不 silent overwrite statement。

### 2.8 observability

`record_read()` 当前写 `read_audit.jsonl`，包含 source span、carry-forward refs、context request、supplemental refs、stop reason、reading impression、surfaced reactions、memory_uptake_ops、detour_need 等。`record_settlement()` 当前写 `settlement_audit.jsonl`，包含 op count、target-store distribution，以及 active_attention / concept_registry / thread_trace / reaction_records 的 compact ID deltas。

### 2.9 current known gaps

当前实现的方向正确，但 contract 仍需收紧：

1. `memory_uptake_ops` 已存在，但仍需要正式定义为 **bounded write intent**，不是 final persisted object。
2. `nodes.py` 的 operation normalization 仍偏宽：它会过滤 unknown operation type，但 target_store 没有在该处完整 admission；且 `target_store` 缺失时当前会默认到 `active_attention`，本设计将把这种行为降级为 legacy tolerant parse，并要求 audit marker。
3. Schema 中 `StateOperationType` 包含 `resolve`，但 nodes 的 `_STATE_OPERATION_TYPES` 集合未列出 `resolve`；这是 contract alignment gap 的一个例子。
4. 当前 state_ops 是 apply layer，不应承担 semantic admission；settlement 需要在 state_ops 之前完成 source binding、payload validation 与 outcome attribution。
5. 当前 `settlement_audit` 有 compact transaction summary，但缺少 per-op outcome、source-binding result 与 failure/defer reason。
6. 项目 current-state 记录过真实诊断：fresh Read output 确实 emitted memory ops，但 durable-store field-shape alignment 需要修复；SourceRef smoke 又暴露 active_attention carry-forward source-ref erasure 风险，后来通过 deterministic merge 修复。

本轮没有逐行打开真实 runtime 目录中的 `read_audit.jsonl / settlement_audit.jsonl / active_attention.json / concept_registry.json / thread_trace.json / reaction_records.json` 等 artifacts。因此，本页只做 architecture-level、contract-level 与 assessment-level 设计判断，不声称已经独立验证真实运行质量。

------

## 3. Core Definitions

### 3.1 Memory Formation

**Memory Formation** 是 accepted source unit 被正式读取后，把当前阅读经验中值得继续可用的 source-grounded state 表达为 bounded write intent 的过程。

它包括：

```text
current accepted SourceSpan
  → Read interpretation
  → candidate memory intent
  → source evidence binding
  → target-store admission
  → payload normalization
  → settlement outcome
```

Memory Formation 不是“把当前段落总结存起来”，也不是“让 LLM 写最终 state object”。

### 3.2 Memory Write Intent

**Memory Write Intent** 是 `Read.memory_uptake_ops[]` 中的一条 bounded proposal。它表达：

> “基于当前 accepted unit 的 source evidence，我建议对某个允许的 memory store 做一个有限操作。”

它不是：

- final persisted memory object；
- whole-store rewrite；
- reflection；
- visible reaction；
- planning state；
- audit artifact；
- prompt packet。

### 3.3 Memory Settlement

**Memory Settlement** 是 deterministic authority。它把 memory write intent 转成 state 或 audit outcome。

Settlement 可以 normalize、validate、bind SourceRef、merge、upsert、link、resolve、reactivate、cool、skip、reject、defer，并记录 outcome。Settlement 不是另一个 LLM judgment layer。

### 3.4 Source Binding

**Source Binding** 是把 unit-local `source_quote / source_role / source_ref_hint` 转成 inline paragraph-offset `SourceRef` 的过程。

Source Binding 是 formation contract 的核心，不是装饰字段。一个普通 read-path semantic memory op 如果不能绑定到 accepted source unit，就不能作为 source-grounded memory 写入。

### 3.5 Operation Normalization

**Operation Normalization** 是把 Read output 中的 tolerated aliases 或 legacy fields 规范化为 canonical operation：

```text
op / operation_type
target_store
target_key / item_id / concept_key / thread_key
payload
reason
source_evidence
```

Normalization 只处理形状与命名，不做语义幻想。

### 3.6 Payload Validation

**Payload Validation** 是按 target store 检查 payload 是否满足最低字段、source_refs、status、links、field shape 与 illegal-promotion rules。

Validation 失败时，settlement 应产生 explicit outcome，而不是让 state_ops 静默跳过后只留下不可解释的 delta 缺失。

### 3.7 Store Admission

**Store Admission** 是判断某个 op 是否允许在 read-path 写入目标 store。

Read-path allowed stores 只有：

```text
active_attention
concept_registry
thread_trace
```

`StateOperationType` 是跨机制/跨慢周期的广义 vocabulary；read-path admission 是更窄的 store-specific contract。

### 3.8 Settlement Outcome

**Settlement Outcome** 是每个 memory op 在 settlement 后的诊断结果，例如 accepted、merged_existing、failed_source_binding、deferred_to_slow_cycle。

Outcome 是后续 Memory Evaluation 与 runtime diagnosis 的最小证据单位。

### 3.9 Settlement Audit

**Settlement Audit** 是针对 settlement transaction 的 structured diagnostic record。它不是 chain-of-thought，不是 prompt context，不是 memory store。

它应回答：每个 op 被如何处理、为什么、绑定了哪些 source refs、改动了哪些 state IDs、失败或延后在哪里。

------

## 4. Formation Pipeline

Read-path formation pipeline 固定为：

```text
Accepted SourceSpan
  → Read call
  → Read output normalization
  → memory_uptake_ops parsing
  → source evidence binding
  → target store / operation validation
  → payload normalization
  → relation / conflict pre-check
  → state_ops application
  → per-op settlement outcome
  → read_audit / settlement_audit
```

### 4.1 Accepted SourceSpan

Input：Runner 已经解析成功的 accepted `SourceSpan`、source text、source_span_id、paragraph slices。

Owner：Runner。

Failure：`end_anchor_text` 无法解析、ambiguous、preview mismatch。

Handling：Runner 已有 fallback / retry / conservative boundary 逻辑；formation 只在 accepted unit 确认后开始。

Audit：unitization / read_audit / settlement_audit 均应保留 source_span_id。

### 4.2 Read call

Input：current unit、carry-forward context、selective carry、policy snapshot。

Output：`ReadUnitResult`。

Owner：LLM Read node proposes。

Failure：invalid JSON、missing fields、overbroad output、illegal target store、source_quote 不在 current unit、visible content leaks internal handles。

Handling：nodes normalization 过滤或归一化；不能被安全解释的部分进入 skipped/rejected outcome。

Audit：read_audit 保存 raw or normalized Read result summary。

### 4.3 Read output normalization

Input：LLM JSON。

Output：normalized `reading_impression`、`surfaced_reactions`、`memory_uptake_ops`、`detour_need`。

Owner：nodes / settlement preprocessor。

Failure：unknown op、unknown target, malformed payload, missing target key, illegal surfaced reaction.

Handling：shape-level normalization；unsafe fields dropped with tolerant marker；semantic admission deferred to settlement。

Audit：read_audit 记录 normalized read payload；settlement_audit 记录 op-level normalization result。

### 4.4 memory_uptake_ops parsing

Input：normalized list.

Output：candidate `MemoryUptakeIntent[]` with op_index.

Owner：settlement.

Failure：non-list、non-dict、missing operation_type、missing target_store、missing target key。

Handling：produce per-op skipped outcome; do not call state_ops for that op.

Audit：settlement_audit per-op outcome.

### 4.5 source evidence binding

Input：candidate intent, current source_unit.

Output：payload with canonical `source_refs[]` and binding metadata.

Owner：settlement, using deterministic source-span helpers.

Failure：source_quote missing, quote not found, ambiguous quote, role illegal, ref points outside accepted unit.

Handling：

- concept/thread semantic writes: reject or defer if primary source binding fails;
- active_attention: may partial_accept only when bound to accepted unit span and audit marks fallback;
- never write unbound semantic memory.

Audit：source_binding_result required.

### 4.6 target store / operation validation

Input：bound intent.

Output：admitted or rejected op.

Owner：settlement.

Failure：illegal target store, illegal op for store, destructive overwrite, Read trying to write slow-cycle store.

Handling：reject / defer_to_slow_cycle / defer_to_management.

Audit：per-op outcome and reason.

### 4.7 payload normalization

Input：admitted intent.

Output：canonical state_ops payload.

Owner：settlement.

Failure：payload shape mismatch, missing required fields, unknown fields, legacy shape not safely interpretable.

Handling：accepted_normalized if safe; failed_payload_validation if unsafe; fallback_tolerant_parse marker when legacy repair is applied.

Audit：normalized_payload_summary and tolerant_parse marker.

### 4.8 relation / conflict pre-check

Input：canonical op and current store snapshot.

Output：merge/upsert/link/resolve decision or defer.

Owner：settlement.

Failure：duplicate ambiguous target, conflict with existing item, suspected supersede, relation link invalid.

Handling：

- simple same-key merge: proceed;
- current-source resolve: proceed if local and low-risk;
- semantic supersede or multi-source conflict: defer_to_slow_cycle / defer_to_management;
- destructive overwrite prohibited.

Audit：relation_merge_result.

### 4.9 state_ops application

Input：canonical operations only.

Output：new state snapshots.

Owner：state_ops.

Failure：unexpected state shape, persistence failure, corrupted store.

Handling：infrastructure failure can block transaction; op-level validation failures should already have been handled before state_ops.

Audit：state deltas and op outcomes.

### 4.10 per-op settlement outcome

Input：before/after state, op metadata.

Output：operation outcome record.

Owner：settlement / observability.

Failure：missing delta attribution.

Handling：if accepted op produces no state delta due to duplicate, outcome should be `no_op_duplicate` or `merged_existing`, not silent.

Audit：settlement_audit.

### 4.11 read_audit / settlement_audit

`read_audit` records what Read proposed and the source/carry context around it.

`settlement_audit` records what the deterministic system did with each op.

Neither audit stream is runtime memory or prompt context.

------

## 5. `memory_uptake_ops` Contract

### 5.1 Conceptual contract

A `MemoryUptakeIntent` should conceptually contain:

```text
MemoryUptakeIntent:
  intent_id_or_op_index
  target_store
  operation_type
  proposed_key_or_id
  source_evidence
  payload
  reason
  relation_hints
  status_hint
  confidence_or_uncertainty
```

This is a conceptual contract. It does not require final code field names to match exactly.

Likely schema fields:

```text
op / operation_type
target_store
target_key / item_id
reason
payload:
  statement / summary
  concept_key / thread_key
  concept_type / thread_type
  attention_tags
  status
  source_quote
  source_role
  linked_concept_keys
  linked_thread_keys
```

### 5.2 What it is

`memory_uptake_ops` is:

- bounded write intent;
- source-grounded;
- read-path-local;
- target-store typed;
- operation-level auditable;
- accepted-unit anchored.

### 5.3 What it is not

It is not:

- final persisted object;
- reflection;
- visible reaction;
- visible route surface object;
- detour target;
- route decision;
- state snapshot;
- prompt packet;
- audit artifact;
- evaluation artifact;
- prior knowledge truth.

### 5.4 Allowed target stores

Read-path target stores are only:

```text
active_attention
concept_registry
thread_trace
```

Any other target store must produce `skipped_illegal_target_store` or `deferred_to_slow_cycle / deferred_to_management`.

### 5.5 Allowed operation types

Allowed operation types are store-specific.

For read-path v0:

```text
create / update / link / reactivate / resolve
```

are generally legal when the store admits them.

`cool` is legal only as active_attention visibility intent and must not mean semantic invalidation.

`append` may be tolerated as legacy alias for create/update, but should normalize with audit marker.

`close` may normalize to resolve with audit marker.

`drop`, `promote`, `supersede` are not ordinary read-path memory formation operations. If present from Read, settlement should reject or defer unless a later Management design explicitly permits a narrow case.

### 5.6 Minimum required fields

Every op requires:

```text
target_store
operation_type
proposed_key_or_id
payload
reason
source_evidence
```

`source_evidence` normally means `source_quote` from current accepted unit, plus optional `source_role`.

Store-specific required fields:

```text
active_attention:
  item_id / target_key
  statement
  attention_tags
  source_refs after binding

concept_registry:
  concept_key / target_key
  concept_type
  summary or definition-like payload
  source_refs after binding

thread_trace:
  thread_key / target_key
  thread_type
  summary
  source_refs after binding
```

### 5.7 Optional fields

Optional but useful:

```text
status_hint
linked_concept_keys
linked_thread_keys
relation_hints
uncertainty_note
confidence_band
source_role
```

Confidence should not become a fake numeric authority. If used, prefer coarse markers such as `low / medium / high` or a short uncertainty note. Settlement outcome is determined by deterministic validation, not by LLM confidence.

### 5.8 Stable key / target item id

Read may propose a stable key, but settlement normalizes it.

Rules:

- active_attention uses `item_id`;
- concept_registry uses `concept_key`;
- thread_trace uses `thread_key`;
- `target_key` can be accepted as conceptual alias;
- item IDs must be stable enough for merge/upsert within a run;
- generated IDs are allowed only when settlement can derive a deterministic key from source_span_id + normalized label + store;
- vague keys such as `important_point` should be rejected or normalized only with tolerant parse marker.

### 5.9 Relation / link rules

Links are lightweight hints, not graph DB commitments.

Allowed:

```text
active_attention.linked_concept_keys
active_attention.linked_thread_keys
concept_registry.linked_thread_ids
thread_trace.linked_concept_keys
```

A relation hint must not replace source evidence. If relation target does not exist, settlement may:

- keep the link as unresolved hint only if store contract allows it;
- or skip the link while accepting the main op;
- or defer relation to Management.

### 5.10 Illegal cases

Illegal read-path cases include:

- target_store = `reflective_frames`;
- target_store = `reaction_records`;
- target_store = `knowledge_activations` under ordinary memory_uptake_ops;
- target_store = audit / eval / planning / prompt / visible route surface object;
- no source evidence;
- source_quote not found in current accepted unit;
- source evidence from future text;
- prior knowledge presented as source truth;
- visible reaction copied into concept/thread merely because it is strong;
- detour_need written as active_attention without separate source-grounded memory intent;
- whole-store rewrite;
- destructive overwrite;
- semantic supersede from a single Read op.

### 5.11 Backward compatibility / tolerant parsing

Current and legacy shapes may be tolerated when unambiguous:

```text
op → operation_type
target_key → item_id / concept_key / thread_key
append/create/link → update for concept/thread when safe
close → resolve when safe
payload.source_quote → source_refs after binding
```

But tolerant parsing must be marked in audit.

Settlement should reject rather than guess when:

- target store is illegal;
- target key is missing;
- source quote cannot bind;
- payload is too vague to map to store schema;
- operation type implies lifecycle semantics not authorized by read-path.

------

## 6. Allowed Read-path Target Stores and Operations

## 6.1 `active_attention`

`active_attention` is hot near-term reading state. Read may propose active_attention ops when the current unit creates or changes a focus that will pull on the next reads.

Allowed read-path intents:

```text
create
update
reactivate
resolve
link
cool-like visibility update
```

Use cases:

- an unresolved question from current unit;
- a live tension;
- a provisional interpretation that the next passages must test;
- a motif/focus that remains hot;
- a current-source resolution of a previously hot question.

Minimum payload:

```text
item_id / target_key
statement
attention_tags[]
source_quote or source_refs
status_hint
optional linked_concept_keys
optional linked_thread_keys
```

Admission rules:

- must be anchored in current accepted unit;
- must plausibly affect near-term reading;
- must not be a generic summary;
- must not be a visible reaction copy;
- must not be a durable concept definition unless concept_registry also receives a separate concept op.

Not allowed from Read:

- destructive drop as normal lifecycle;
- semantic invalidation;
- reflective promotion;
- store-wide cooling;
- chapter-level carry-forward decisions.

`cool` in read-path means local visibility cooling only. It must not be interpreted as semantic invalidation.

## 6.2 `concept_registry`

`concept_registry` is source-grounded concept / object / definition / model / classification / named distinction memory.

Allowed read-path intents:

```text
create
update
link
reactivate
resolve
```

Use cases:

- source-given definition;
- named distinction;
- classification;
- stage model;
- roadmap term;
- reusable object or conceptual frame explicitly introduced by the author.

Minimum payload:

```text
concept_key / target_key
concept_type
summary or definition
source_quote or source_refs
status_hint
optional linked_thread_ids
```

Admission rules:

- must be source-given or source-grounded;
- must not be prior knowledge masquerading as source truth;
- must not be a chapter summary bucket;
- must not be a mere reaction;
- must preserve source_refs across updates.

Not allowed from Read:

- broad reflective frame;
- unsourced model inference;
- concept supersede requiring multiple source spans;
- delete/drop as ordinary lifecycle.

## 6.3 `thread_trace`

`thread_trace` is cross-passage line / motif / argument / question / development memory.

Allowed read-path intents:

```text
create
update
link
reactivate
resolve
```

Use cases:

- a line that is recurring or likely to recur;
- a motif whose meaning is unfolding;
- an argument thread;
- a cross-passage contrast;
- a source-grounded unresolved question expected to pull future reading.

Minimum payload:

```text
thread_key / target_key
thread_type
summary
source_quote or source_refs
status_hint
optional linked_concept_keys
```

Admission rules:

- must have source foothold in current accepted unit;
- must be more than a single isolated concept;
- must express development over time or future-pulling continuity;
- new source evidence should merge into existing source_refs, not overwrite.

Not allowed from Read:

- single definition better suited for concept_registry;
- visible reaction ledger entry;
- chapter summary;
- purely thematic association;
- semantic supersede requiring multi-source review.

## 6.4 Explicitly not writable by ordinary read-path `memory_uptake_ops`

Read-path must not write:

```text
reflective_frames
reaction_records directly
knowledge_activations directly
reconsolidation_records
unit_span_ledger
read_audit
settlement_audit
evaluation evidence
planning state
visible route surface object
prompt packet
reader policy / procedural memory
```

`knowledge_activations` may have a separate warrant-bearing bridge path in current code, but that path is not ordinary `memory_uptake_ops`. `knowledge.py` separately manages knowledge activation lifecycle and only enables prior knowledge mode when an activation has warrant and live status.

------

## 7. Source Binding Design

### 7.1 What Read should provide

Read should provide source evidence as:

```text
payload.source_quote
payload.source_role?
```

`source_quote` should be the smallest current-unit quote that supports the op. It must come from the current accepted unit.

`source_role` may be:

```text
definition
evidence
trigger
contrast
callback
resolution
support
```

The role describes how the quote supports the op. It is not a free-form claim of truth.

### 7.2 Who binds SourceRef

Read does not generate authoritative SourceRef. Read gives source evidence.

Settlement binds SourceRef deterministically using current source_unit and paragraph-offset helpers.

Current helper behavior already supports exact quote matching, ambiguity reporting, and fallback resolution. This design tightens admission around those resolution statuses.

### 7.3 Binding outcome categories

Source binding should produce:

```text
matched
ambiguous_first_match
fallback_unit_span_missing_quote
fallback_unit_span_quote_not_found
failed_quote_not_found
failed_outside_current_unit
failed_missing_source_evidence
```

Design rule:

- `matched` is normal accept condition.
- `ambiguous_first_match` may be accepted with audit marker if the exact quote is still in current unit and ambiguity is low-risk.
- `fallback_unit_span_missing_quote` may support active_attention partial_accept only when the accepted unit itself is sufficiently narrow.
- concept_registry and thread_trace should not accept `quote_not_found` as source-grounded semantic memory.
- `failed_*` outcomes do not write semantic memory.

### 7.4 Multiple source refs

An op may bind multiple source refs when the payload contains multiple source quotes. Settlement must dedupe by source_span_id + role + quote, preserving stable order.

This follows the current source_ref dedupe posture in source helpers and state_ops merge logic.

### 7.5 Source binding failure

Source binding failure should not be silent.

If binding fails:

```text
concept_registry op → failed_source_binding or deferred_to_management
thread_trace op → failed_source_binding or deferred_to_management
active_attention op → failed_source_binding, or partial_accept only with accepted-unit span fallback and explicit audit marker
```

No ordinary unbound memory op may be written as source-grounded memory.

### 7.6 Relation to surfaced reaction source binding

Surfaced reactions and memory ops both require current-unit source footing, but they settle separately.

For surfaced reactions:

- `source_quote` anchors visible trace;
- builder persists `reaction_records`;
- source binding creates `primary_source_ref`;
- reaction does not become semantic memory.

For memory ops:

- `source_quote` supports durable reading state;
- settlement writes active/concept/thread;
- audit records per-op outcome.

The same quote may support both a reaction and a memory op, but those are two different settlement surfaces.

------

## 8. Settlement Authority and Outcome Design

Settlement is the authoritative boundary. LLM does not decide final outcome.

Settlement may produce these outcomes.

### 8.1 Accepting outcomes

```
accepted
```

- Op is valid, source-bound, canonical, and writes state.
- Writes state: yes.
- Cursor advancement: unaffected.
- Audit: read_audit + settlement_audit.
- Evaluation use: positive formation/settlement evidence.

```
accepted_normalized
```

- Op was valid after safe normalization, such as `append → update`.
- Writes state: yes.
- Audit must record normalization reason.
- Evaluation use: useful for legacy/shape drift diagnosis.

```
merged_existing
```

- Same target key exists; new source_refs / fields merge.
- Writes state: yes, update existing ID.
- Audit records target ID and merged source refs.

```
linked_existing
```

- Main effect is relation/link update.
- Writes state: yes if link admitted.
- Audit records link target and relation hint.

```
reactivated_existing
```

- Existing cooled/resolved item becomes active again due to current source.
- Writes state: yes.
- Audit records prior status and new status.

```
resolved_existing
```

- Existing active question/thread/focus is locally resolved by current source.
- Writes state: yes.
- Audit records resolution source_ref.
- Full semantic validity changes remain Management territory.

```
cooled_existing
```

- Active_attention item loses near-term heat.
- Writes state: yes.
- Audit marks visibility lifecycle, not semantic invalidation.

```
partial_accept
```

- A safe part writes, unsafe part is skipped.
- Example: active_attention statement accepted but relation link skipped.
- Audit must record accepted and skipped subparts.

```
no_op_duplicate
```

- Intent duplicates existing state and no new evidence is added.
- Writes state: no.
- Audit records duplicate target/source.

### 8.2 Skipping / rejecting outcomes

```
skipped_missing_required_field
```

- Missing key, statement/summary, source evidence, or payload.
- Writes state: no.

```
skipped_illegal_target_store
```

- Target is not active_attention / concept_registry / thread_trace.
- Writes state: no.
- Settlement must not silently remap illegal store to a legal one.

```
skipped_illegal_operation
```

- Operation not allowed for store/read-path.
- Writes state: no.

```
failed_source_binding
```

- Source evidence cannot bind to current accepted unit.
- Writes state: no, except explicitly marked active_attention partial_accept case.

```
failed_payload_validation
```

- Payload shape cannot be safely normalized.
- Writes state: no.

```
rejected_ungrounded
```

- Claim is not grounded in current source or explicit warrant.
- Writes state: no.

```
fail
```

- Infrastructure-level failure, such as corrupted state or persistence failure.
- May block transaction or run depending on severity.
- Audit/debug event required.

### 8.3 Deferral outcomes

```
deferred_to_slow_cycle
```

Use when op asks for:

- reflective frame;
- chapter/book synthesis;
- reconsolidation;
- knowledge activation status update;
- multi-source supersede;
- cross-chapter carry-forward.

Writes state: no immediate memory write.

```
deferred_to_management
```

Use when op needs lifecycle semantics not defined here:

- merge conflict;
- semantic invalidation;
- destructive deletion question;
- concept/thread supersede chain.

Writes state: no immediate write.

```
request_manual_review
```

Rare debug/admin outcome for suspicious legacy shape or source-binding ambiguity.

Writes state: no by default. It should not block ordinary cursor advancement unless operator policy says otherwise.

### 8.4 Cursor and run effects

Per-op skip/reject/defer normally does not block cursor advancement. The accepted source unit has been read; memory failure should be diagnosable, not silently converted into reading-loop failure.

Only infrastructure failure that threatens persistence integrity should block or require resume recovery.

------

## 9. Payload Normalization and Validation

The core principle is:

> `state_ops` should apply canonical operations; settlement should validate and normalize before state_ops.

This avoids repeating the current class of bug where Read output payload shape and persisted field shape diverge.

### 9.1 active_attention canonical payload

```text
item_id
statement
attention_tags[]
status
source_refs[]
linked_concept_keys[]
linked_thread_keys[]
```

Validation:

- `item_id` required;
- `statement` required for create/update/reactivate;
- `source_refs` required after binding;
- `attention_tags` optional but recommended;
- status must be allowed active/cooling/resolved/closed-like vocabulary;
- unknown legacy bucket/list fields should not be persisted.

### 9.2 concept_registry canonical payload

```text
concept_key
concept_type
summary
status
source_refs[]
linked_thread_ids[]
```

Validation:

- `concept_key` required;
- `summary` or definition-like content required;
- `source_refs` required after binding;
- `concept_type` defaults only if semantically safe, otherwise `concept`;
- not a generic summary bucket.

### 9.3 thread_trace canonical payload

```text
thread_key
thread_type
summary
status
source_refs[]
linked_concept_keys[]
```

Validation:

- `thread_key` required;
- `summary` required;
- `source_refs` required after binding;
- thread_type defaults only if safe;
- must express development/line/argument/motif/question, not isolated concept.

### 9.4 Target key normalization

Settlement maps:

```text
target_key → item_id       for active_attention
target_key → concept_key   for concept_registry
target_key → thread_key    for thread_trace
```

`item_id` may be accepted as alias for all stores at intent layer, but canonical store payload must use the store’s own key.

### 9.5 Status normalization

Read may provide status hints. Settlement owns final status.

Examples:

```text
create/update active_attention without status → active
reactivate without status → active
cool without status → cooling
resolve without status → resolved
```

Status normalization must be recorded when it changes the op.

### 9.6 Source refs

Any `source_quote` / `source_role` must be transformed into `source_refs[]` before state_ops.

State_ops should not receive a payload that only contains `source_quote` for concept/thread/active memory writes.

### 9.7 Duplicate detection

Duplicate detection uses:

```text
same store
same stable key
source_ref overlap
payload semantic shape
```

v0 does not require embedding similarity or graph lookup. Same-key merge is enough for read-path settlement.

### 9.8 Unknown operation / target

Unknown operation type or target store should not be guessed.

Current code’s defaulting to `active_attention` can be tolerated only as legacy parsing when there is strong evidence the op was meant for active_attention. New contract should require explicit target_store.

### 9.9 Illegal payload promotion

Settlement must not promote:

- reaction payload into concept/thread because it is eloquent;
- active_attention hypothesis into concept truth without source-given stability;
- prior knowledge into concept_registry without source-given grounding;
- Read op into reflective frame.

### 9.10 Legacy payload shape

Legacy payloads may be normalized if the mapping is deterministic and source-bound.

Otherwise they should be skipped with:

```text
failed_payload_validation
fallback_tolerant_parse = false
```

or accepted with:

```text
accepted_normalized
fallback_tolerant_parse = true
legacy_shape_reason = ...
```

------

## 10. Relation / Conflict / Merge Handling

This page only defines lightweight relation/conflict behavior for formation. Full lifecycle matrix belongs to Memory Management / Evolution.

### 10.1 Duplicate concept / thread

Settlement may merge when:

- same `concept_key` or `thread_key`;
- source_refs add evidence to existing item;
- payload is compatible with existing summary/status.

It should merge source_refs and links rather than overwrite.

### 10.2 Same source evidence supports concept and thread

The same source quote may support both:

- a concept entry: “what is this distinction/model?”
- a thread entry: “how is this line unfolding?”

This is allowed only when the two payloads have distinct store semantics. Settlement should express the relationship via lightweight links or shared source_refs, not by duplicating identical summaries.

### 10.3 New evidence merge

When new source evidence supports an existing item:

```text
merge source_refs
merge lightweight links
update summary only when payload is compatible
preserve older source_refs
```

Destructive overwrite is forbidden.

### 10.4 Conflict / correction

Settlement can handle only local, low-risk correction:

- current source resolves an active question;
- current source reactivates a cooled item;
- current source adds new evidence to an existing concept/thread.

Settlement should defer when:

- existing item must be semantically superseded;
- two source spans conflict;
- old understanding becomes invalid;
- change affects reflective frame or cross-chapter memory;
- prior knowledge warrant is weakened or rejected.

### 10.5 Can Read propose supersede?

For v0 read-path: no ordinary Read op should finalize `supersede`.

Read may express a `reason` such as “this seems to correct an earlier understanding,” but settlement should convert that to:

```text
deferred_to_slow_cycle
or
deferred_to_management
```

unless a later Management design authorizes a narrow read-path supersede.

### 10.6 Can Read close / resolve?

Read may propose `resolve` for local active_attention or thread questions when the current unit directly resolves the issue.

Settlement must distinguish:

```text
resolve = local obligation closure
supersede / invalidate = semantic validity lifecycle
```

The latter is deferred.

------

## 11. Surfaced Reactions vs Memory Formation

### 11.1 Distinction

`surfaced_reactions` are visible trace intent. They answer:

> “What would this co-reader naturally mark, underline, wonder, or say visibly at this moment?”

`memory_uptake_ops` are memory write intent. They answer:

> “What should remain available to shape later reading?”

A strong reaction is still a reaction until a separate explicit memory op or slow-cycle promotion creates semantic memory.

### 11.2 Reaction persistence

`reaction_records` are durable visible trace ledger, not semantic memory store.

The current builder persists surfaced reaction with:

```text
reaction_id
thought
source_quote
primary_source_ref
prior_link
outside_link
search_intent
record_source = read_surface
```

This is separate from active_attention/concept/thread state.

### 11.3 `prior_link / outside_link / search_intent`

These are visible support semantics.

They do not automatically become:

- concept memory;
- thread memory;
- knowledge activation;
- route guidance;
- user-facing route guidance;
- navigation decision.

They may support later audit, callback diagnosis, or slow-cycle promotion.

### 11.4 Audit relationship

Reaction persistence and memory op settlement should be separately audited but cross-referenceable through:

```text
source_span_id
source_refs
reaction_id
op_index
```

A single source quote can produce both a reaction and a memory op, but the outcome of one does not imply acceptance of the other.

------

## 12. `detour_need` Boundary

`detour_need` is planning intent, not memory formation.

Read may propose:

```text
reason
target_hint
status
```

Read may not:

- locate detour target;
- decide next source unit;
- execute look-back;
- convert detour into memory state;
- write `local_continuity` directly.

Runner / Planning settlement may update `local_continuity` under Planning Ontology rules. In current code, `local_continuity` persists `mainline_cursor / active_detour_id / active_detour_need / detour_trace`.

`detour_need` must not be written into `active_attention` unless there is a separate, source-grounded memory intent. The distinction is:

```text
detour_need:
  a path obligation — “the reading path may need to leave mainline”

active_attention:
  a reading focus — “this question/tension/focus should remain hot”
```

A detour audit may record source evidence and reason, but that audit does not automatically become memory.

------

## 13. Read-path vs Slow-cycle Settlement Boundary

### 13.1 Read-path settlement may handle

```text
local active_attention create/update/reactivate/resolve/cool
concept definition/distinction/classification update
thread create/update/link/resolve
source-ref-preserving merge
visible reaction persistence
compact audit
```

These are low-risk, local, source-grounded, accepted-unit anchored operations.

### 13.2 Must defer to slow-cycle

```text
reflective frame promotion
chapter-level synthesis
book-level frame
reconsolidation
knowledge activation status update, unless handled by separate warrant path
cross-chapter carry-forward
semantic supersede requiring multiple source spans
procedural prompt / policy refinement
visible route surface output / macro-planning display output
```

Current slow-cycle already owns reflective promotion, reconsolidation, chapter consolidation, cooling/promotion candidates, knowledge activation updates, and carry-forward style outputs.

------

## 14. Audit Design for Formation & Settlement

### 14.1 `read_audit` should record

`read_audit` should remain the record of what was read and what Read proposed:

```text
accepted source_span / source_span_id
unit text size summary
carry_forward_ref_ids
context_request
supplemental_ref_ids
supplemental steps / stop reason / budget
reading_impression
surfaced_reactions
raw or normalized memory_uptake_ops
detour_need
llm fallback markers
```

Current `record_read()` already records most of these fields.

### 14.2 `settlement_audit` should record

`settlement_audit` should remain compact transaction audit, but gain per-op outcomes.

Transaction-level fields:

```text
recorded_at
chapter_id / chapter_ref
source_span_id
source_span
memory_uptake_op_count
target-store distribution
state_deltas
emitted_reaction_ids
```

Current `record_settlement()` already records compact deltas for active_attention, concept_registry, thread_trace, and reaction_records.

Add per-op outcome fields:

```text
op_index
raw_op_summary
normalized_op_summary
target_store
operation_type
proposed_key_or_id
source_binding_result
payload_validation_result
relation_merge_result
outcome
state_ids_added
state_ids_updated
state_ids_linked
state_ids_resolved
failure_reason
defer_reason
tolerant_parse_marker
normalization_reason
projection_impact
```

`projection_impact` should be conservative:

```text
none
may_affect_active_attention_digest
may_affect_concept_digest
may_affect_thread_digest
may_affect_recent_reaction_digest
unknown_due_to_projection_budget
```

It should not claim the item definitely appeared in the next prompt, because projection is bounded.

### 14.3 Outcome taxonomy v0

```text
accepted
accepted_normalized
merged_existing
linked_existing
reactivated_existing
resolved_existing
cooled_existing
partial_accept
no_op_duplicate

skipped_missing_required_field
skipped_illegal_target_store
skipped_illegal_operation
failed_source_binding
failed_payload_validation
rejected_ungrounded

deferred_to_slow_cycle
deferred_to_management
request_manual_review
fail
```

### 14.4 No full snapshot per unit

This design does not require full state snapshots for every unit.

The correct pattern is:

```text
compact transaction summary
+ per-op outcome
+ targeted probe snapshots only when evaluation explicitly asks for them
```

This aligns with current evaluation guidance that `unit_span_ledger.jsonl`, `read_audit.jsonl`, and `settlement_audit.jsonl` are runtime diagnosis evidence, not benchmark targets by themselves.

------

## 15. Runtime Artifact and Backward Compatibility Considerations

### 15.1 Existing JSON / JSONL runtime remains

No new infrastructure is required.

Current runtime artifacts already include:

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
```

These are defined under `_mechanisms/attentional_v2/runtime/`.

### 15.2 Schema version

Design-level recommendation:

```text
memory_uptake_intent_schema_version
settlement_audit_schema_version
source_binding_schema_version
```

These can be added without changing existing store state.

### 15.3 Old audit compatibility

Old `read_audit` / `settlement_audit` rows may lack per-op outcomes. Interpret missing outcome as:

```text
outcome = not_recorded_legacy
```

No migration is required for current design acceptance.

### 15.4 Old `memory_uptake_ops` compatibility

Tolerate old fields when safe:

```text
op / operation_type
target_key / item_id
payload.source_quote
append/create/link aliases
```

Reject rather than guess when target store, source evidence, or key is ambiguous.

### 15.5 State migration

This design does not require state migration for existing `active_attention / concept_registry / thread_trace` files.

Potential changes are mostly:

```text
prompt contract tightening
schema / type normalization
settlement validation
audit outcome enrichment
```

Implementation handoff may later decide whether to add migration for audit-only shape, but this design does not require it.

------

## 16. What This Design Changes or Tightens

### 16.1 Preserved

This design preserves:

```text
attentional_v2 as current default
Navigate.choose_next_unit → Read → Runner settlement
paragraph-offset SourceCursor / SourceSpan
inline SourceRef evidence spine
file-based JSON / JSONL runtime
active_attention / concept_registry / thread_trace as read-path target stores
reaction_records as visible trace ledger
chapter-end slow-cycle
read_audit / settlement_audit
bounded prompt-facing state_packet
```

### 16.2 Tightened

This design tightens:

```text
memory_uptake_ops = bounded write intent
Read never writes final persisted objects
SourceRef binding is mandatory formation contract
settlement owns final outcome
state_ops receives canonical payload only
illegal target stores are rejected/deferred, not remapped
per-op settlement outcome becomes minimum audit unit
reaction_records do not automatically become semantic memory
detour_need does not enter memory_uptake_ops
prior knowledge does not become source truth
```

### 16.3 Reinterpreted

- `reading_impression`: immediate read-after impression, not memory.
- `memory_uptake_ops`: write intent, not memory object.
- `surfaced_reactions`: visible trace intent, not semantic memory op.
- `detour_need`: planning intent, not memory op.
- `settlement`: deterministic authority, not LLM adjudicator.

### 16.4 Deferred

Deferred to later pages:

```text
full lifecycle operation matrix
supersede / invalidate semantics
Memory Management / Evolution
retrieval intent taxonomy
Memory Retrieval / Utilization
Navigation / Detour / Look-back / Active Recall policy
Visible Reading Route Surface Boundary
full Audit / Evaluation schema
Implementation Handoff
```

Any future route display must be derived from settled route trace, source refs, and audit summaries; it must not be produced as a `memory_uptake_op`. Read-path never creates user route controls.

------

## 17. Design Implications for Later Pages

### 17.1 Memory Management / Evolution

This page supplies the admission boundary. Management must later define full lifecycle semantics:

```text
cool vs resolve
drop vs retire
supersede vs invalidate
merge vs link
visibility lifecycle vs semantic validity lifecycle
```

### 17.2 Memory Retrieval / Utilization

Retrieval must consume only settled, source-ref-preserving state. It should not retrieve raw Read intents as memory truth.

Retrieval design should use settlement outcomes to distinguish unavailable memory, skipped memory, and failed memory formation.

### 17.3 Memory Audit / Evaluation

Audit/Evaluation should treat formation quality as stage-aware:

```text
Read proposed?
Source bound?
Payload validated?
Settlement accepted?
State updated?
Projection used?
Visible output integrated correctly?
```

Memory Quality, Spontaneous Callback, and FVI can use per-op outcomes to localize failure.

### 17.4 Detour / Look-back / Active Recall Policy

This page preserves the boundary:

```text
active_recall = memory recovery
look_back = source calibration
detour = planning path deviation
```

Formation settlement should not absorb those policy decisions.

### 17.5 Slow-cycle / Macro-planning

Slow-cycle receives deferred candidates and settled state. It should not rely on raw read intents as authoritative memory.

### 17.6 Implementation Handoff

Handoff can later translate this into concrete schema/prompt/state_ops/audit changes. This page only defines the contract and readiness boundary.

------

## 18. Implementation Readiness Notes

### 18.1 Ready for narrow implementation validation

The following are ready for small-window implementation validation:

```text
memory_uptake_ops contract tightening
explicit target-store / operation validation
source_quote → SourceRef binding validation
payload normalization before state_ops
per-op settlement outcome audit
legacy tolerant parse markers
unknown target/op rejection
```

These are narrow because they strengthen the existing Read → settlement → state_ops → audit chain without adding stores or agents.

### 18.2 Needs Management design first

```text
full lifecycle operation matrix
supersede / invalidate / retire semantics
destructive drop policy
multi-source conflict handling
concept/thread merge semantics beyond same-key merge
```

### 18.3 Needs Retrieval design first

```text
retrieval intent taxonomy
utilization trace
projection ranking beyond current bounded digest
active_recall / look_back trigger policy
```

### 18.4 Needs Audit / Evaluation design first

```text
full audit schema versioning
Memory Quality stage-aware rubric
formation-quality metrics
pollution / drift attribution rubric
```

### 18.5 Needs Planning / Navigation policy first

```text
detour trigger / exit policy
look-back policy
active recall policy
Visible Reading Route Surface Boundary
planning audit fields
```

### 18.6 Explicitly not now

```text
vector DB
graph DB
Memory OS
RL Memory-as-Action
complex memory manager agent
per-unit reflection
large planner rewrite
full implementation roadmap
```

------

## 19. Optional Open Questions

None critical at this phase.

Two non-blocking questions remain:

1. **How strict should settlement be with `fallback_unit_span` SourceRef?**
   Current source helper can fall back to the whole unit when quote is missing or not found. For v0, concept/thread should reject failed quote binding; active_attention may partial_accept only under explicit audit marker. A final strictness matrix belongs to Audit / Evaluation and Management.
2. **Should `resolve` be accepted as a first-class Read op immediately?**
   Conceptually yes, because schema includes it and state_ops can handle resolve-like semantics. Current normalization appears not fully aligned with schema. This is an implementation alignment issue, not a design blocker.

# Memory Formation & Settlement Design v0 — Revision Patch

## Patch 1：明确 `deferred_to_slow_cycle / deferred_to_management` 的载体

建议并入正文第 8 节 **Settlement Authority and Outcome Design**，并在第 13 节 **Read-path vs Slow-cycle Settlement Boundary** 中交叉引用。

### Deferred Candidate Carrier

`deferred_to_slow_cycle` 与 `deferred_to_management` 的含义不是“把 op 丢掉”，也不是“把 op 写入 durable memory”。它们表示：

> settlement 判断该 op 不适合 read-path 立即落入 memory state，但它包含的 source-grounded candidate evidence 可能对后续 slow-cycle 或 Management 有价值。

因此，deferred op 不写入 `active_attention / concept_registry / thread_trace`，也不生成 settled memory item；但 `settlement_audit` 必须保留一个 compact deferred candidate record。

最小字段：

```
DeferredCandidateRecord:
  op_index
  requested_target_store
  requested_operation_type
  normalized_payload_summary
  bound_source_refs
  defer_reason
  recommended_downstream_owner
    - slow_cycle
    - management
  not_authoritative_memory = true
```

规则：

- deferred candidate 是 **candidate evidence**，不是 settled memory truth；
- slow-cycle / Management 可以读取 deferred candidates，但只能把它们当作候选材料；
- slow-cycle / Management 若决定写入 durable memory，仍必须重新经过其自身的 admission / validation / settlement；
- deferred candidate 不应进入 prompt-facing memory projection；
- deferred candidate 不应被 Retrieval 当作 memory item；
- deferred candidate 不应被 Evaluation 计为 successful memory formation，只能计为 “formation deferred with evidence preserved”。

适用例子：

```
Read proposes:
  target_store = reflective_frames
  operation_type = promote
  payload = chapter-level synthesis

Settlement:
  outcome = deferred_to_slow_cycle
  writes memory state = no
  writes settlement_audit.deferred_candidate = yes
```

这样可以同时满足两点：

1. read-path 不越权写 high-level memory；
2. slow-cycle 不会因为只有 audit outcome 而丢失候选材料。

------

## Patch 2：收紧 SourceRef fallback 的 v0 硬门槛

建议并入正文第 7 节 **Source Binding Design**。

### SourceRef Binding Admission v0

v0 对 source binding 的 admission 采用硬规则，不把 fallback 当作普通成功绑定。

#### `concept_registry`

`concept_registry` 只接受：

```
matched
low-risk ambiguous_first_match
```

不接受：

```
fallback_unit_span_missing_quote
fallback_unit_span_quote_not_found
failed_quote_not_found
failed_missing_source_evidence
failed_outside_current_unit
```

原因：concept_registry 保存 source-grounded concept / definition / model / classification。如果 quote 找不到，settlement 不能把它写成稳定 semantic memory。

#### `thread_trace`

`thread_trace` 只接受：

```
matched
low-risk ambiguous_first_match
```

不接受 fallback unit span 作为普通绑定。

原因：thread_trace 保存跨 passage / cross-unit development line。如果当前 source evidence 都无法精确绑定，后续 callback / FVI 风险会显著升高。

#### `active_attention`

`active_attention` 可以在非常窄的情况下 `partial_accept` fallback unit span，但必须同时满足：

```
1. accepted unit length below configured threshold
2. op is hot focus / question / tension, not stable semantic claim
3. source_binding_result explicitly marked fallback_unit_span
4. projection treats the item as provisional
```

建议 conceptual threshold：

```
unit_char_count <= active_attention_fallback_max_chars
or
paragraph_count == 1 and char_count within configured small-unit limit
```

该 threshold 的具体数值属于 implementation handoff，但设计要求是：fallback 只能用于短 unit 中的近端 hot focus，不得用于稳定概念或 thread。

### Projection consequence

如果 active_attention 使用 fallback partial accept，则 prompt-facing projection 必须标记：

```
source_binding = fallback_unit_span
memory_status = provisional
```

该 item 可以帮助下一步阅读保持注意力，但不能被 Planning 或 Read 当作 stable source-established fact。

### Audit consequence

`settlement_audit.per_op_outcome` 必须记录：

```
outcome = partial_accept
source_binding_result = fallback_unit_span
fallback_reason = missing_or_unmatched_source_quote
projection_impact = provisional_active_attention_only
```

------

## Patch 3：进一步收紧 read-path `resolve` 与 `cool`

建议并入正文第 6 节 **Allowed Read-path Target Stores and Operations** 与第 10 节 **Relation / Conflict / Merge Handling**。

### `resolve` in read-path

Read-path 可以提出 `resolve`，但 v0 必须区分 “local obligation closure” 与 “semantic finalization”。

#### active_attention

`active_attention.resolve` 允许用于：

```
当前 source 直接回答了某个 hot question
当前 source 直接消解了某个 tension
当前 source 让一个 near-term focus 不再需要继续拉动下一步阅读
```

这表示 hot focus 被局部关闭，不表示相关概念或 thread 被永久完成。

#### concept_registry

`concept_registry.resolve` 只允许表示：

> attached local ambiguity / pending question around a concept is closed.

它不表示：

```
the concept itself is completed
the concept is semantically finalized
the concept is invalidated
the concept no longer needs future evidence
```

推荐 audit reason：

```
resolve_scope = local_ambiguity
not_semantic_finalization = true
```

如果 Read 试图用 `resolve` 表达 “这个概念已经最终解释完了”，settlement 应改为：

```
deferred_to_management
```

或在无充分 source support 时 reject。

#### thread_trace

`thread_trace.resolve` 只允许用于当前 source 直接关闭某条 thread 的 local question 或 immediate development obligation。

它不表示整条 thread 永久终止。跨章节 thread 结束、语义收束、旧 thread 被新 thread 替代，都属于 Management / slow-cycle territory。

### `cool` in read-path

Read-path `cool` 只允许用于 `active_attention`。

更严格规则：

```
Read-path cool is allowed only when the current source directly resolves or discharges the hot focus.
General cooling remains slow-cycle territory.
```

不允许 Read 因为 “这一点看起来暂时不重要” 就单步降温。普通 cooling、chapter-end cooling、cross-chapter carry-forward selection 应由 slow-cycle 处理。

Read-path `cool` 的最小条件：

```
target_store = active_attention
operation_type = cool
existing item_id exists
current source directly discharges the hot focus
source_ref binding succeeds
audit records cooling_basis = current_source_discharge
```

若缺少 existing item 或 source basis：

```
outcome = skipped_illegal_operation
or
outcome = failed_source_binding
```

------

## Patch 4：定义同一 ReadUnitResult 内多 op 的事务顺序

建议并入正文第 4 节 **Formation Pipeline** 与第 8 节 **Settlement Authority and Outcome Design**。

### Intra-unit Operation Ordering

同一个 `ReadUnitResult.memory_uptake_ops[]` 可能包含多条相互关联的 ops。Settlement v0 必须采用稳定事务规则。

处理顺序：

```
1. assign stable op_index
2. parse all ops
3. validate and source-bind each op independently
4. normalize admitted payloads
5. precompute dependency graph only for explicit links
6. apply canonical writes in stable op_index order
7. resolve links to earlier accepted ops in the same transaction
8. skip or mark unresolved links to failed/skipped/deferred ops
9. emit per-op outcome and dependency outcome
```

核心规则：

- 每条 op 的 source binding 独立完成；
- op2 不能因为 op1 成功而免除 source evidence；
- links to items created earlier in the same transaction may resolve；
- links to failed/skipped/deferred ops must not hallucinate target；
- link failure 不应自动导致 main op failure，除非该 op 是 pure link-only op；
- audit 必须记录 `dependency_skipped` 或 `link_unresolved`。

### Example

```
op1:
  create concept_registry concept_x

op2:
  create thread_trace thread_y
  linked_concept_keys = [concept_x]

op3:
  update active_attention focus_z
  linked_concept_keys = [concept_x]
```

如果 op1 accepted：

```
op2.linked_concept_keys resolves to concept_x
op3.linked_concept_keys resolves to concept_x
```

如果 op1 failed_source_binding：

```
op2 main thread may still be accepted if independently valid
op2 link to concept_x = link_unresolved or dependency_skipped
op3 main active_attention update may still be accepted if independently valid
op3 link to concept_x = link_unresolved or dependency_skipped
```

Audit fields:

```
dependency_result:
  depends_on_op_indexes
  resolved_dependencies
  skipped_dependencies
  unresolved_links
  dependency_reason
```

------

## Patch 5：给 outcome taxonomy 标出 MVP subset

建议并入正文第 14 节 **Audit Design for Formation & Settlement** 与第 18 节 **Implementation Readiness Notes**。

### MVP Settlement Outcomes

v0 narrow implementation 不需要一次性实现完整 outcome taxonomy。MVP 应先覆盖诊断闭环所必需的 outcomes：

```
accepted
accepted_normalized
merged_existing
no_op_duplicate

skipped_missing_required_field
skipped_illegal_target_store
skipped_illegal_operation
failed_source_binding
failed_payload_validation
rejected_ungrounded

deferred_to_slow_cycle
deferred_to_management
fail
```

### v0.2 / alias outcomes

以下 outcomes 可以作为 v0.2 或 MVP aliases：

```
linked_existing
reactivated_existing
resolved_existing
cooled_existing
partial_accept
request_manual_review
```

MVP 中可映射为：

```
linked_existing       → accepted or accepted_normalized with effect_type = link
reactivated_existing  → accepted_normalized with status_change = reactivated
resolved_existing     → accepted_normalized with status_change = resolved
cooled_existing       → accepted_normalized with status_change = cooling
partial_accept        → accepted_normalized with partial = true
request_manual_review → fail or deferred_to_management with review_requested = true
```

### Design rule

完整 taxonomy 可保留在设计文档中，但 Implementation Handoff 应优先使用 MVP subset，避免 Codex 在第一轮实现中过度铺开状态空间。

------

## Patch 6：明确 pure link-only op 的权限

建议并入正文第 5 节 **`memory_uptake_ops` Contract** 与第 10 节 **Relation / Conflict / Merge Handling**。

### Pure Link-only Ops v0

Pure link-only op 指 payload 不新增 statement / summary / definition / thread evidence，只试图建立两个已有 memory items 之间的关系。

v0 允许 pure link-only op 的条件非常窄：

```
1. both endpoints already exist
   or are accepted earlier in the same settlement transaction

2. the link is source-supported by the current accepted unit

3. the link does not create a new semantic claim by itself

4. source binding succeeds

5. audit records both endpoint ids and source_ref
```

如果 endpoint 不存在：

```
outcome = skipped_missing_required_field
or
outcome = deferred_to_management
```

如果 endpoint 来自同一 transaction 但前序 op failed：

```
outcome = no_op_duplicate? no
outcome = skipped_illegal_operation or dependency_skipped
```

如果 link itself 需要解释一个新的 semantic relation，而不是简单关联：

```
deferred_to_management
```

### Link as subpart of main op

如果一个 main op 附带 links，而 links 不满足条件：

```
accept main op if independently valid
skip/defer invalid link subpart
audit partial link outcome
```

例子：

```
create thread_trace thread_y
  summary = ...
  linked_concept_keys = [concept_x]
```

若 `thread_y` 本身有效但 `concept_x` 不存在：

```
main op outcome = accepted
link outcome = link_unresolved / dependency_skipped
```

### What link cannot do

Pure link op 不得：

```
create hidden graph node
create new concept/thread implicitly
assert source-unsupported semantic relation
turn theme similarity into durable memory relation
repair missing source evidence
```

这能防止 `link` 变成隐形 graph-building 或 bypass source binding。

------

## Patch 7：给 Implementation Readiness 加一个 Handoff Gate

建议并入正文第 18 节 **Implementation Readiness Notes** 末尾。

### Pre-Codex Handoff Gate

在进入 Codex implementation 之前，本设计不应直接作为全文交给 Codex 拆任务。应先转换成一个窄 implementation handoff packet，至少包含：

```
1. minimal schema delta
2. prompt delta
3. settlement validation rules
4. per-op audit fields
5. backward compatibility behavior
6. explicit non-goals
```

#### 1. Minimal schema delta

只定义必须新增或收紧的字段，例如：

```
memory_uptake_intent_schema_version
settlement_outcome
source_binding_result
deferred_candidate
tolerant_parse_marker
dependency_result
```

不在此阶段扩展 full lifecycle matrix。

#### 2. Prompt delta

只收紧 Read prompt 中的 `memory_uptake_ops` 输出要求：

```
target_store explicit
operation_type explicit
source_quote required when source evidence is needed
source_role optional
no illegal stores
no final state objects
no reaction auto-promotion
```

不重写 Read persona。

#### 3. Settlement validation rules

把设计中的 admission rules 转为 deterministic validators：

```
allowed target stores
allowed op per store
required payload fields
SourceRef binding gate
fallback rules
pure link-only rules
intra-transaction dependency handling
```

#### 4. Per-op audit fields

实现 MVP per-op outcome，而不是 full audit schema：

```
op_index
target_store
operation_type
proposed_key_or_id
source_binding_result
outcome
failure_reason
defer_reason
state_delta_summary
tolerant_parse_marker
```

#### 5. Backward compatibility behavior

明确 legacy parsing：

```
op → operation_type
target_key → store-specific key
append/create/link aliases
close → resolve
missing target_store no longer silently defaults except legacy marker
```

以及 reject conditions。

#### 6. Explicit non-goals

第一轮不做：

```
lifecycle operation matrix
retrieval taxonomy
navigation/detour policy
recommendation
vector DB
graph DB
manager agent
full evaluation rubric
full implementation roadmap
```

### Gate rule

只有当 handoff packet 明确回答以上 6 项后，才进入窄实现验证。这样 Codex 拿到的是 implementation entrypoint，而不是整篇设计文档。

------

## Patch 8：建议插入的简短总述

可以把下面这段加到正文第 16 节 **What This Design Changes or Tightens** 之后，作为 v0 修订总结。

### v0 Tightening Summary

本修订进一步收紧 v0 的实施边界：

- deferred op 不写 memory，但通过 `settlement_audit.deferred_candidate` 保留候选证据；
- SourceRef fallback 不等于成功绑定，concept/thread 必须 matched 或 low-risk ambiguous；
- active_attention fallback 只允许短 unit、hot focus、provisional projection；
- concept_registry 的 resolve 只关闭 attached ambiguity，不完成或终结概念；
- read-path cool 只允许 current source directly discharges hot focus；
- 同一 ReadUnitResult 内多 op 按 `op_index` 稳定应用，links 可以依赖 earlier accepted ops，但不能依赖 failed/skipped ops；
- MVP outcome subset 优先于完整 taxonomy；
- pure link-only op 只在 endpoints 存在或本 transaction earlier accepted 时允许；
- implementation 前必须先生成 minimal handoff packet。

这些收紧不会改变原设计的主方向：Read 仍只提出 bounded intent，settlement 仍是 deterministic authority，SourceRef 仍是 formation contract 的核心，slow-cycle / Management 仍处理高层演化与冲突。

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

### A.1 Product and source-of-truth boundary

`docs/product-overview.md` defines the product as a living, curious, text-grounded co-reading mind rather than a summary engine or service assistant. This supports the design choice that memory formation must preserve source-grounded reading state, not user-profile memory or generic cleverness.

`docs/source-of-truth-map.md` says the workspace is repo-first and that durable facts belong in canonical repo docs or state files. This supports JSON/JSONL audit/state continuity and a contract-first design posture.

`docs/current-state.md` records the paragraph-offset SourceCursor/SourceSpan cutover, inline SourceRef truth, Read naturalization, settlement diagnostics, field-shape alignment repair, and SourceRef carry-forward repair. It supports the design’s focus on SourceRef binding, payload normalization, and per-op audit. It also records diagnostic run facts but does not replace independent runtime-row audit.

### A.2 Mechanism platform and current default

`docs/backend-reading-mechanism.md` defines `public/book_document.json` as shared parsed-book truth, paragraph layer as stable source substrate, and `attentional_v2` SourceRef as inline paragraph-offset citation with no shared registry. This supports the design choice that SourceRef is bound inline at settlement rather than through a new Anchor Bank.

`docs/backend-reading-mechanisms/README.md` identifies `attentional_v2` as current default/live mechanism and `iterator_v1` as fallback. This supports evolving current Read → settlement chain in place rather than designing greenfield.

`docs/backend-reading-mechanisms/iterator_v1.md` provides legacy contrast: section-first, subsegment runtime, read/think/express/search/fuse/reflect loop, and memory packet assembly. This supports the decision not to reintroduce old express/reaction-family or section-first assumptions into current formation design.

### A.3 `attentional_v2` mechanism doc

`docs/backend-reading-mechanisms/attentional_v2.md` is the strongest current mechanism authority. It states that current live loop is `Navigate.choose_next_unit → read → Reading Runner settlement`, that `Read` outputs `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`, that `reading_impression` is temporary, that durable memory changes only through `memory_uptake_ops`, and that surfaced reactions are not automatically copied into concept/thread memory.

This is stable current implementation evidence, not merely assessment inference.

### A.4 Schemas

`schemas.py` defines `ReadUnitResult`, `StateOperation`, `StateOperationType`, `SourceRef`, `SurfacedReaction`, `DetourNeed`, and all primary stores. It shows the current contract surface and the broad operation vocabulary.

This supports the design’s distinction between broad `StateOperationType` vocabulary and narrower read-path store admission.

### A.5 Prompts

`prompts.py` already instructs Read to target only `active_attention / concept_registry / thread_trace`, to avoid writing `reflective_frames / reaction_records / audit`, to propose operations rather than whole-object rewrites, and to supply `source_quote / source_role` so Runner can resolve source_refs.

This supports treating the design as a tightening of current contract rather than a new architecture.

### A.6 Nodes normalization

`nodes.py` normalizes state operations, surfaced reactions, detour_need, and navigation acts. It filters invalid operation types, requires surfaced reaction source_quote to appear in current unit, and rejects visible internal handle leakage.

It also reveals contract gaps: op-type set alignment and target-store admission are not yet sufficient for per-op outcome audit.

### A.7 Runner

`runner.py` owns Reading Runner integration, runtime bundle loading/saving, local continuity, detour application, state artifact persistence, and rejection of unsupported legacy runtime shapes. It applies the current post-read settlement path and persists mechanism-private artifacts.

This supports the design’s assignment of settlement authority to Runner / settlement layer, not Read.

### A.8 State operations

`state_ops.py` deterministically applies operations to active_attention, concept_registry, thread_trace, reaction_records, reconsolidation, and reflective supersede; it merges source_refs and linked IDs.

This supports preserving state_ops as apply layer while adding explicit settlement validation before state_ops.

### A.9 Observability

`observability.py` writes read_audit and settlement_audit. The current `record_settlement()` records compact ID deltas but not per-op outcomes.

This directly supports the design’s per-op outcome audit requirement and its rejection of full snapshot per unit.

### A.10 Storage

`storage.py` defines mechanism-private JSON/JSONL artifacts, including active_attention, concept_registry, thread_trace, reflective_frames, knowledge_activations, reaction_records, reconsolidation_records, unit_span_ledger, read_audit, and settlement_audit.

This supports file-based runtime continuity and no new database requirement.

### A.11 Source spans

`source_spans.py` defines paragraph-offset source cursors/spans, deterministic source_span_id, inline SourceRef construction, quote-to-SourceRef binding, fallback resolution statuses, and source ref dedupe.

This is the direct code basis for Source Binding Design.

### A.12 State projection

`state_projection.py` builds bounded prompt-facing `state_packet.v1`, active_attention digest, concept digest, thread digest, reflective digest, source_ref digest, recent reactions, and refs.

This supports the design distinction between authoritative stores and prompt-facing projection.

### A.13 Read context

`read_context.py` distinguishes `look_back` source excerpt resolution from `active_recall` over concepts/threads/reactions.

This supports keeping formation separate from retrieval/calibration policy.

### A.14 Slow-cycle

`slow_cycle.py` owns reaction record building, compatibility projection, reflective promotion, reconsolidation, chapter consolidation, cooling operations, promotion candidates, and knowledge activation updates.

This supports deferring high-level reflection, reconsolidation, knowledge updates, and cross-chapter carry-forward out of read-path formation.

### A.15 Knowledge path

`knowledge.py` defines knowledge activation lifecycle and conservative knowledge/search modes. It keeps prior/external knowledge as warrant-bearing activation rather than source truth.

This supports excluding ordinary knowledge activation writes from `memory_uptake_ops`.

### A.16 Evaluation

`docs/backend-reader-evaluation.md` defines product-first, mechanism-agnostic evaluation and the current long-span direction: Memory Quality, Spontaneous Callback, and False Visible Integration. It also states that runtime ledgers/audits are diagnosis evidence, not benchmark targets by themselves.

This supports compact audit plus per-op outcomes as diagnosis infrastructure.

### A.17 Decision log and task registry

`docs/history/decision-log.md` preserves major decisions and rejected alternatives; it records the project’s repeated pattern of choosing focus, shared substrate boundaries, and mechanism-private artifact separation.

`docs/tasks/registry.md` records current active structural rework, SourceRef cutover, Read naturalization, settlement-audit diagnostic, and long-span Memory Quality direction. It supports the design’s focus on current `attentional_v2` rather than greenfield replacement.

### A.18 Runtime-artifact validation gap

This design uses repo docs, code contracts, and recorded diagnostic summaries. It does **not** claim independent row-level validation of actual runtime artifacts. The runtime-artifact validation gap remains open for later audit/evaluation work.

------

## B. Upstream Design Basis

### B.1 Design Route

The design route places this page in Phase 2: core running contract layer, after Memory Ontology and Planning Ontology. It specifically names this page as the place to define `Read.memory_uptake_ops`, Read’s proposal authority, settlement authority, SourceRef binding, formation decomposition, and read-path vs slow-cycle boundary.

This page follows that scope exactly and does not design retrieval, management, evaluation, or implementation roadmap.

### B.2 P0 Shared Charter

P0 supplies the governing boundary:

```text
LLM proposes; deterministic runner settles
```

It also requires separation of durable state, trace, visible output, evaluation evidence, and prompt-facing projection; makes SourceRef / SourceSpan / accepted unit the evidence spine; and defines settlement transaction’s minimum diagnostic questions.

This page turns those shared rules into a concrete read-path memory formation contract.

### B.3 Memory Ontology

Memory Ontology supplies the store identities and hard boundaries:

```text
active_attention
concept_registry
thread_trace
reflective_frames
reaction_records
knowledge_activations
reconsolidation_records
audit artifacts
```

It also states that Read-path only proposes `memory_uptake_ops`, and those ops may target only `active_attention / concept_registry / thread_trace`.

This page does not redefine stores; it defines how writes enter the allowed stores.

### B.4 Planning Ontology

Planning Ontology supplies interface guardrails: Planning uses Memory but does not own it; `detour_need` is planning intent; `local_continuity` is planning state; active_recall/look_back/detour are distinct.

This page prevents memory formation from absorbing detour/navigation/visible route disclosure responsibilities.

### B.5 Memory Assessment

Memory Assessment identifies the central gap: `memory_uptake_ops` contract is not stable enough, SourceRef binding must become formation core, payload shape alignment has already failed once, and per-op outcome is needed.

This page directly converts that assessment into design.

### B.6 Planning Assessment

Planning Assessment warns not to let memory formation swallow planning / navigation / visible route disclosure. It also frames detour/look-back/active_recall as related but distinct mechanisms.

This page follows that boundary by keeping `detour_need` out of `memory_uptake_ops`.

------

## C. External Rationale, as Filtered Through the Assessments

This section uses only external works already filtered through the upstream assessments and ontology documents. It does not cite Evidence Pack files as evidence.

### C.1 Mem0

Mem0 frames memory as operation-centric add/search/update/delete with extraction, conflict handling, storage, metadata, and update/delete as first-class operations.

Supported design judgment: `memory_uptake_ops` should be write intent, not final object; settlement must accept/normalize/merge/reject/defer.

Similarity: both need item identity, metadata, update semantics, and auditable operation pipeline.

Difference: Mem0 is general agent/user memory; Reading Companion memory is accepted-source-unit-grounded reading state.

Localized borrowing: operation-centric pipeline and metadata discipline.

Not copied: vector/graph infrastructure and user-profile memory.

Support type: Direct.

### C.2 Zep

Zep separates episodes, entities, facts, observations, summaries, and temporal validity / invalidity.

Supported design judgment: source evidence, memory item, visible trace, prior knowledge warrant, and audit must stay separate; later correction should use supersede/invalidate rather than destructive overwrite.

Similarity: both need evidence-backed memory and temporal change.

Difference: Zep is graph-backed temporal agent memory; Reading Companion stays file-first and source-span-first.

Localized borrowing: evidence layering, validity/supersede principles.

Not copied: graph DB and enterprise entity graph.

Support type: Direct / Analogical.

### C.3 LangGraph Memory / LangMem

LangGraph / LangMem distinguish memory types and hot-path vs background writes.

Supported design judgment: Read-path formation should only do local low-risk writes; slow-cycle handles reflection, consolidation, knowledge activation updates, and higher-order promotion.

Similarity: both need write-timing separation.

Difference: framework memory is general; Reading Companion has stricter source and reading-path boundaries.

Localized borrowing: hot/background write separation and type hygiene.

Not copied: autonomous memory manager agent or procedural prompt refinement as current mechanism.

Support type: Direct / Boundary.

### C.4 Letta / MemGPT

Letta / MemGPT distinguish prompt-facing memory blocks from archival/durable memory and emphasize bounded context.

Supported design judgment: `state_packet.v1` and prompt-facing digests are projections, not authoritative state; memory stores need role and visibility contracts.

Similarity: both face context-window pressure and need bounded projections.

Difference: Letta/MemGPT are general stateful agents and often persona/user-memory oriented.

Localized borrowing: projection discipline and lightweight store contract.

Not copied: OS-style paging or persona/human memory blocks.

Support type: Boundary.

### C.5 Generative Agents

Generative Agents use low-level observations and delayed reflection; reflection is triggered after accumulated evidence rather than every local observation.

Supported design judgment: Read-path should not write `reflective_frames`; reflection belongs to slow-cycle.

Similarity: both need continuity from many local observations.

Difference: Generative Agents are social simulation agents, not source-grounded readers.

Localized borrowing: observation → reflection timing.

Not copied: ungrounded social reflection memory.

Support type: Direct / Boundary.

### C.6 LongMemEval

LongMemEval separates long-term memory evaluation into stages such as indexing / retrieval / reading and includes update/temporal/abstention dimensions.

Supported design judgment: audit must support stage-aware diagnosis; per-op outcome helps distinguish formation, settlement, retrieval, and utilization failures.

Similarity: both need failure localization.

Difference: benchmark is chat assistant memory, not source-span reading.

Localized borrowing: stage-aware evaluation decomposition.

Not copied: final QA as primary product metric.

Support type: Direct.

### C.7 HaluMem

HaluMem focuses on hallucination/pollution in memory systems at operation level.

Supported design judgment: failed source binding, bad payload, illegal update, and ungrounded writes must be visible at settlement time, not discovered only in final output.

Similarity: both face memory pollution risks.

Difference: HaluMem is general memory benchmark, not Reading Companion-specific.

Localized borrowing: operation-level audit and pollution diagnosis.

Not copied: benchmark tasks wholesale.

Support type: Direct.

### C.8 ReAct / ReWOO

ReAct and ReWOO support bounded observation-grounded loops and decoupled evidence gathering.

Supported design judgment: detour/source-evidence loops belong to Planning / Navigation boundary, not ordinary memory formation; source evidence is used to correct or localize, not to become automatic memory.

Similarity: both use evidence to constrain next moves.

Difference: Reading Companion’s environment is source text and reading path, not a tool sandbox.

Localized borrowing: bounded evidence-loop analogy.

Not copied: every read unit as tool-use action loop.

Support type: Analogical / Boundary.

### C.9 Reflexion

Reflexion places verbal reflection between episodes and separates feedback-derived strategy from immediate action.

Supported design judgment: slow-cycle may use audit/failure signals, but procedural strategy reflection must not pollute source-grounded content memory.

Similarity: both need between-episode reflection.

Difference: Reading Companion’s primary memory is book-grounded understanding, not task policy memory.

Localized borrowing: episode-boundary reflection.

Not copied: self-modifying prompt/policy memory.

Support type: Boundary.

------

## D. Simplicity and Universality Check

This design satisfies Simplicity and Universality in these ways:

1. It tightens the existing Read / Runner / state_ops / audit chain instead of adding a manager agent.
2. It adds no new memory store.
3. It keeps Read as proposer, not final state writer.
4. It keeps settlement deterministic, not another LLM layer.
5. It keeps SourceRef binding as the evidence spine.
6. It does not automatically semanticize `reaction_records`.
7. It does not write `detour_need` into memory.
8. It does not turn prior knowledge into source truth.
9. It does not introduce vector DB, graph DB, Memory OS, or RL memory editing.
10. It supports later Management / Retrieval / Audit / Planning pages without pre-binding full implementation.

Remaining complexity risks:

- Tolerant legacy parsing could become silent guessing unless audit markers are mandatory.
- Source binding fallback could over-accept weakly grounded ops unless concept/thread rejection remains strict.
- Relation hints could drift toward graph semantics unless kept lightweight.
- Per-op audit could become too verbose unless it remains compact and avoids full snapshots.
- Slow-cycle deferral could become a dumping ground unless later Management defines lifecycle semantics.

------

## E. Source Usage List

| External source                                              | Authors / Organization         | Year        | Stable URL                                                   | Used for                                           | Support type          |
| ------------------------------------------------------------ | ------------------------------ | ----------- | ------------------------------------------------------------ | -------------------------------------------------- | --------------------- |
| Generative Agents: Interactive Simulacra of Human Behavior   | Joon Sung Park et al.          | 2023        | https://arxiv.org/abs/2304.03442                             | Observation vs reflection; slow-cycle boundary     | Direct / Boundary     |
| Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | Prateek Chhikara et al. / Mem0 | 2025        | https://arxiv.org/abs/2504.19413                             | Operation-centric memory write pipeline            | Direct                |
| Mem0 Memory Operations docs                                  | Mem0                           | 2025–2026   | https://docs.mem0.ai/core-concepts/memory-operations/add     | Add/update/delete/search as explicit operations    | Direct                |
| Zep: A Temporal Knowledge Graph Architecture for Agent Memory | Preston Rasmussen et al. / Zep | 2025        | https://arxiv.org/abs/2501.13956                             | Evidence-backed facts and temporal validity        | Direct / Analogical   |
| Zep Graph Overview docs                                      | Zep                            | 2025–2026   | https://help.getzep.com/graph-overview                       | Episodes/entities/facts/observations separation    | Direct                |
| LangGraph Memory Concepts                                    | LangChain                      | 2025–2026   | https://docs.langchain.com/oss/python/concepts/memory        | Memory type hygiene; hot-path vs background writes | Direct / Boundary     |
| LangMem                                                      | LangChain                      | 2025–2026   | https://github.com/langchain-ai/langmem                      | Background memory consolidation patterns           | Boundary              |
| MemGPT: Towards LLMs as Operating Systems                    | Charles Packer et al.          | 2023        | https://arxiv.org/abs/2310.08560                             | Durable state vs context projection boundary       | Boundary              |
| Letta Memory Blocks docs                                     | Letta                          | 2025–2026   | https://docs.letta.com/guides/core-concepts/memory/memory-blocks | Lightweight memory block contract                  | Boundary              |
| Letta Archival Memory docs                                   | Letta                          | 2025–2026   | https://docs.letta.com/guides/ade/archival-memory/           | Core vs archival distinction                       | Boundary              |
| LongMemEval                                                  | Di Wu et al.                   | 2024        | https://arxiv.org/abs/2410.10813                             | Stage-aware memory diagnosis                       | Direct                |
| HaluMem                                                      | Ding Chen et al.               | 2025        | https://arxiv.org/abs/2511.03506                             | Operation-level hallucination / pollution          | Direct                |
| ReAct                                                        | Shunyu Yao et al.              | 2022 / 2023 | https://arxiv.org/abs/2210.03629                             | Bounded observation-grounded loop analogy          | Analogical / Boundary |
| ReWOO                                                        | Binfeng Xu et al.              | 2023        | https://arxiv.org/abs/2305.18323                             | Decoupled evidence-gathering analogy               | Analogical            |
| Reflexion                                                    | Noah Shinn et al.              | 2023        | https://arxiv.org/abs/2303.11366                             | Episode-boundary reflection boundary               | Boundary              |
