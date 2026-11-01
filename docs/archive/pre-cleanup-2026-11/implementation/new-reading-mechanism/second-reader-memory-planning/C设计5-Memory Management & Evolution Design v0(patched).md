# Memory Management & Evolution Design v0

## 1. Scope and Purpose

本设计定义 Second Reader / Reading Companion 中 **已经形成并 settle 的 reading memory** 后续如何被管理与演化。

它继承 P0 Shared Charter 的最高运行边界：**LLM proposes; deterministic runner settles**。LLM 可以提出 lifecycle intent、promotion candidate、cooling candidate、supersede candidate 或 reconsolidation candidate；但最终的状态转移、SourceRef 合并、ID 链接、合法性判断、audit outcome 与 durable persistence 必须由 deterministic runner / settlement / state_ops 完成。

它继承 Memory Ontology v0：reading memory 是从 accepted source units 中形成的 source-grounded reading state；source corpus 不是 memory；prompt-facing projection 不是 authoritative state；visible reaction 不是 semantic memory；knowledge activation 是 warrant ledger；audit / evaluation artifacts 不是 runtime memory。

它继承 Memory Formation & Settlement v0：`Read.memory_uptake_ops` 是 bounded write intent，不是最终持久对象；read-path target stores 仍只有 `active_attention / concept_registry / thread_trace`；SourceRef binding 是 formation contract 核心；full lifecycle matrix、supersede / invalidate、destructive overwrite、multi-source conflict 等由本页定义。

它兼容 Planning Ontology 与 Navigation Policy：Planning 使用 memory projection 但不拥有 memory；Navigation 不写 memory；active_recall 是 memory recovery，look_back 是 source calibration，detour 是 planning path deviation。

本页只设计 **settled memory 的 lifecycle 与 evolution contract**。它不是 Memory Ontology 重写，不是 Formation 重写，不是 Retrieval 设计，不是 Evaluation rubric，不是 Codex implementation roadmap，也不是外部文献综述。它的目标是让现有 `attentional_v2` memory lifecycle 更清晰、更可靠、更可审计，而不是引入 memory manager agent、vector DB、graph DB 或 Memory OS。

------

## 2. Current Implementation Understanding

当前 repo 显示，Reading Companion 是一个 workspace，后端与前端分别位于 `reading-companion-backend` 与 `reading-companion-frontend`；默认机制为 `attentional_v2`，`iterator_v1` 是显式 fallback / legacy-compatible path。

产品定位不是摘要器或服务型助手，而是一个 text-grounded、legible、self-propelled 的共读心智；broad prior knowledge 有价值，但不能制造 text-detached certainty。 共享机制文档也明确：`public/book_document.json` 是唯一 shared parsed-book truth；当前 `attentional_v2` 使用 paragraph + char-offset cursor 与 inline paragraph-offset `SourceRef`，没有共享 Anchor Bank 或 SourceRef registry。

当前 live loop 是：

```text
survey / reading_plan orientation
  → Navigate.choose_next_unit
  → Read
  → Reading Runner post-read settlement
  → cursor advance / unit ledger / audit
  → chapter/session slow-cycle
```

`attentional_v2` 机制文档明确：`Navigate.choose_next_unit` 选择下一 coverage unit，`Read` 输出 `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`，Reading Runner 确定性应用 memory uptake、持久化 reactions、写 audit、记录 accepted unit span，并推进 cursor。

### 2.1 Current operation vocabulary

`schemas.py` 中 `StateOperationType` 当前包含：

```text
append
update
close
link
create
cool
drop
retain_anchor
link_anchors
promote
supersede
reactivate
resolve
```

同一 schema 还定义了 `active_attention / concept_registry / thread_trace / reflective_frames / knowledge_activations / reaction_records / reconsolidation_records` 等 primary stores，以及 `DetourNeed`、`NavigateActResult`、`ReadUnitResult`、`SourceRef` 等核心对象。

需要注意一个 contract gap：`schemas.py` 已包含 `resolve`，但 `nodes.py` 的 `_STATE_OPERATION_TYPES` 当前没有列出 `resolve`，这会使 read-path normalization 与 schema vocabulary 不完全一致。 本设计不把这个现状当作设计真理，而把它视为后续 implementation alignment 的收紧点。

### 2.2 Current `state_ops.py` behavior

`state_ops.py` 是当前 deterministic apply layer。它对 `active_attention` 支持 create / append / update / reactivate / cool / close / resolve / link / drop。`cool` 在没有 payload status 时设为 `cooling`；`resolve` 设为 `resolved`；`drop` 从 active items 中移除。Source refs 会通过 `_merge_source_refs` 和 `dedupe_source_refs` 合并去重。

对 `concept_registry` 与 `thread_trace`，当前实现会把 `append / create / link` 归一化为 `update`，把 `close` 归一化为 `resolve`，并允许 `drop` 直接移除 entry。entry 更新时会 merge source_refs 与 linked ids，而不是简单覆盖。

对 `reflective_frames`，当前实现已有 `supersede_reflective_item`：它把旧 item 标记为 `status = superseded` 并写入 `superseded_by_item_id`，但不修改旧 statement。这是本设计扩展为全局原则的重要实现依据。

`reaction_records` 当前通过 `append_reaction_record` append-only 写入；`reconsolidation_records` 当前通过 `append_reconsolidation_record` append-only 写入。

### 2.3 SourceRef merge / dedupe

`source_spans.py` 定义 `SourceCursor / SourceSpan / SourceRef`。`SourceRef` 是 inline paragraph-offset source citation；`source_ref_from_unit()` 能把 unit-local quote 解析成 paragraph-offset span，失败时会 fallback 到 unit span 并在 `resolution` 中标记 `missing_quote` 或 `quote_not_found`；`dedupe_source_refs()` 按 `source_span_id / role / quote` 去重。

本设计继承 SourceRef-first，但会进一步收紧：semantic validity update 不得只靠 fallback source binding；promotion / supersede / invalidate 必须保留可解释的 source evidence lineage。

### 2.4 Reaction records and visible trace

`slow_cycle.py` 的 surfaced-native reaction builder 会把 `Read.surfaced_reactions[]` 持久化为 `reaction_records`，保留 `primary_source_ref`、`prior_link`、`outside_link`、`search_intent`、`supersedes_reaction_id` 等字段，并通过 compatibility helper 派生旧 family labels。

`prompts.py` 明确要求：surfaced reaction 是 visible trace；强 reaction 不应自动复制进 `concept_registry` 或 `thread_trace`。

### 2.5 Knowledge activations

`knowledge.py` 管理 `knowledge_activations` lifecycle。当前 operations 支持 create / update / reactivate；`cool` 会把 status 设为 `weak`，`drop` 设为 `dropped`，`supersede` 设为 `rejected`。`refresh_knowledge_modes()` 只有在存在带 warrant 的 `plausible / strong` live activation 时，才切换到 `book_grounded_plus_prior_knowledge`。

这支持本设计的边界：knowledge activation 是 warrant ledger，不是 book-grounded concept truth。

### 2.6 Slow-cycle

当前 slow-cycle 已拥有 surfaced reaction persistence、reflective promotion、reconsolidation、chapter consolidation、cooling operations、promotion candidates、knowledge activation updates 与 cross-chapter carry-forward。`prompts.py` 的 chapter consolidation prompt 明确要求 chapter end 是 cool / sweep / prepare promotion 的机会，不直接 promote reflective summaries；carry-forward active item 必须复用 existing `item_id` 并尽量 preserve `source_refs`。

当前 `slow_cycle.py` 可 apply reflective promotion，调用 `supersede_reflective_item`，并 append reconsolidation records。

### 2.7 Projection and audit

`state_projection.py` 构造 bounded prompt-facing packets：active attention digest、concept digest、thread digest、reflective digest、source_ref digest、recent reactions、continuation capsule 与 refs。它是 projection，不是 authoritative state。

`read_context.py` 区分 `look_back` 与 `active_recall`：look_back 根据 SourceRef / SourceSpan 返回 earlier source excerpts；active_recall 从 concept/thread/reaction records 中取回未 carry 的 state。

`observability.py` 当前写入 `read_audit.jsonl` 与 `settlement_audit.jsonl`。`read_audit` 记录 source span、context request、supplemental steps、reading impression、surfaced reactions、memory uptake ops、detour need；`settlement_audit` 记录 memory op count、target-store distribution 与 active_attention / concept_registry / thread_trace / reaction_records 的 compact ID deltas。

当前缺口是：已有 compact transaction summary，但还没有完整 per-op management outcome、failure reason、supersede chain、projection impact。

### 2.8 Runtime artifact boundary

`storage.py` 定义机制私有 artifacts，包括 `active_attention.json`、`concept_registry.json`、`thread_trace.json`、`reflective_frames.json`、`knowledge_activations.json`、`reaction_records.json`、`reconsolidation_records.json`、`unit_span_ledger.jsonl`、`read_audit.jsonl`、`settlement_audit.jsonl` 等。

本轮读取了 GitHub repo 文档与核心代码，也读取了 `current-state.md` 中记录的诊断摘要：例如 59 条 read-audit 与 settlement-audit、31 个 memory ops、SourceRef carry-forward repair等。 但本轮没有直接访问真实运行目录中的 runtime JSON / JSONL rows。因此本文不声称已经独立验证 runtime quality；下面区分 architecture-level evidence、contract-level evidence、runtime-artifact evidence gap 与 assessment-level inference。

------

## 3. Core Definitions

### 3.1 Memory Management

**Memory Management** 是对已经 settle 的 memory item 执行合法 lifecycle operation 的机制。它回答：

```text
这个 item 是否仍应可见？
它是否仍被 source-so-far 支持？
它是否需要新 source evidence 刷新？
它是否被后文修正、替代、否定、合并、链接、降温、恢复或退休？
这些变化如何审计？
```

Management 不是新 agent，不是 store-wide rewrite，不是 retrieval，不是 evaluation，不是 prompt self-refinement。

Memory Management is a lifecycle contract, not a new runtime actor. In v0, management actions are executed through existing surfaces: settlement / state_ops for deterministic local lifecycle actions; slow-cycle for promotion, reconsolidation, carry-forward, and supersede candidate review; manual/admin repair for exceptional audited correction; evaluation only reports failures and never mutates runtime memory. `deferred_to_management` means "requires a later lifecycle decision surface", not "send to a new manager agent".

### 3.2 Memory Evolution

**Memory Evolution** 是 reading memory 随 source-so-far 增加而改变其解释、证据、状态、可见性、链接和层级的过程。

Evolution 的核心场景是：后文修正前文。Reading Companion 必须保留旧理解为何出现、后来为何被修正、当前 projection 为什么不应再把旧理解当作 current truth。

### 3.3 Visibility lifecycle

**Visibility lifecycle** 表达某个 memory item 是否应该出现在 prompt-facing / planning-facing projection 中，以及以多高优先级出现。

它不回答这个 statement 是否为真。Cooling 不等于失效；drop from hot view 不等于 semantic deletion。

### 3.4 Semantic validity lifecycle

**Semantic validity lifecycle** 表达一个 memory statement 是否仍被当前 source-so-far 支持。

它回答：source 支持、修正、替代、否定、拒绝或仍不确定。Supersede / invalidate / reject 属于 semantic validity lifecycle，不是 visibility lifecycle。

### 3.5 Evidence lineage

**Evidence lineage** 是 memory item 与其 supporting source_refs、later correction source_refs、supersede chain、reconsolidation event、deferred candidate source 的关系记录。

SourceRef 是 memory evolution 的证据脊柱。没有 source evidence 的 semantic validity update 不能被写成 source-grounded memory。

### 3.6 SourceRef-preserving update

**SourceRef-preserving update** 是在更新 statement、summary、status、links 时保留旧 source_refs，并 merge / dedupe 新 source_refs。Update 不得擦除旧 evidence。

### 3.7 Refresh

**Refresh** 是当前 source 再次支持或扩展某个 item，使其 evidence、recency 或 projection priority 被刷新。Refresh 可以增加 source_ref、更新 statement 精度或恢复 visibility priority，但不自动改变 semantic validity。

### 3.8 Reactivate

**Reactivate** 是 cooled / dormant / resolved item 被新 source pressure 重新拉回 active or prompt-facing use。Reactivate 不等于“旧理解重新变真”；它只是当前阅读又需要它。

### 3.9 Resolve

**Resolve** 是某个 local question、tension、ambiguity、thread development 或 frame question 被 current source 暂时关闭。Resolve 不等于永久完成，也不等于删除；resolved item 未来可被 reactivated 或 superseded。

### 3.10 Cool

**Cool** 是 visibility 降温。它通常意味着 item 不再是 near-term hot focus，但仍可作为 durable state、source evidence 或 recall candidate 存在。Cool 不等于 semantic invalidation。

### 3.11 Drop

**Drop** 是从某个 store 中移除或从 projection 中完全隐藏。Drop 默认不是正常语义删除。对 semantic stores，drop 只应用于 corrupted / mistaken entry / manual repair / policy reason。多数正常演化应使用 cool、retire、supersede、invalidate，而不是 drop。

In v0, `drop` must be typed by effect:

```text
projection_drop:
  remove from hot/prompt-facing view, not from durable store

repair_drop:
  remove or tombstone corrupted/mistaken entry, always audited

policy_hide:
  hide a visible reaction from user-facing surface, preserving internal lineage unless compliance requires deletion

hard_delete:
  not a normal lifecycle operation; allowed only under explicit compliance/admin policy
```

For semantic stores, prefer retire / supersede / invalidate over drop. For `reaction_records`, prefer hide / reconsolidate over delete. For audit artifacts, never drop as lifecycle management.

### 3.12 Retire

**Retire** 是 item 不再适合 active use 或 routine projection，但没有被证明为 false。Retire 适用于过时、局部性耗尽、低价值、已被更高层 frame 吸收的 memory。Retired item 仍保留 lineage，可被 audit 或 explicit recall 访问。

retire means:

```text
no longer used in normal current projection
still source-supported or historically valid
still accessible for explicit lineage / audit / historical recall
does not imply falsehood
does not erase source_refs
```

Allowed normal writers are slow-cycle, management repair / admin, and settlement only when applying a pre-authorized lifecycle operation. Ordinary Read-path, Navigation, and Evaluation direct write are not allowed to retire memory.

### 3.13 Supersede

**Supersede** 是新 item 或新 statement 替代旧 item 的 current semantic role。旧 item 保留，标记 `superseded`，并链接 `superseded_by_id`；新 item 标记 `supersedes_id`。Supersede 不等于 destructive overwrite。

Same-store supersede is normal: concept -> concept, thread -> thread, and reflective_frame -> reflective_frame. Cross-store supersede is exceptional: `active_attention` should normally cool/resolve rather than supersede a concept; reaction reconsolidation does not supersede concept/thread memory; knowledge activation rejection does not supersede `concept_registry` unless a separate source-grounded concept update exists.

### 3.14 Invalidate / Reject

**Invalidate** 表示一个 source-grounded memory statement 被后文 source evidence 证明不再成立或不应继续作为当前理解使用。

**Reject** 更常用于 warrant ledger 或 candidate：例如 knowledge activation 的 warrant 失败，或 deferred candidate 经审查不成立。

Invalidate / reject 必须保留来源和理由。不能无证据 silent invalidate。

### 3.15 Promote

**Promote** 是 lower-level settled memory、source_refs、reaction evidence 或 chapter sweep candidate 被提升为 `reflective_frames` 等高层 memory。Promote 正常只属于 slow-cycle / chapter/session boundary，不属于 read-path。

### 3.16 Reconsolidate

**Reconsolidate** 是 later reading moment materially changes the meaning of an earlier visible reaction or prior thought。它写入 `reconsolidation_records`，解释 visible trace 的 reinterpretation。它不是 semantic memory store，也不能替代 supersede。

### 3.17 Deferred candidate

**Deferred candidate** 是 formation / settlement 发现“可能有价值但不应立即写为 settled memory”的 candidate。它不是 memory truth，不进入 prompt-facing projection，不被 Retrieval 当 memory item。Management / slow-cycle 使用它时必须重新 admission / validation / settlement。

### 3.18 Lifecycle event audit

**Lifecycle event audit** 是一次 management action 的 compact diagnostic record。它不是 runtime memory，不进入 prompt，不暴露 chain-of-thought。它记录 actor、target、operation、previous/new status、source_refs、reason_code、outcome、failure_reason 与 projection impact。

------

## 4. Lifecycle Taxonomy

Reading Companion 的 lifecycle 必须分四类，不能混用。

本节的 lifecycle vocabulary 是 conceptual taxonomy，不等于第一轮实现必须全部落成 enum。Implementation Handoff 应先采用 MVP implementation subset，并把较细的状态词保留为 reason / audit marker，直到真实 runtime 需求证明它们需要进入正式 status vocabulary。

MVP visibility markers:

```text
active
cooling
cooled
dormant
carried_forward
not_carried
```

MVP semantic validity markers:

```text
provisional
source_supported
refined
resolved
superseded
invalidated
rejected
retired
```

MVP lineage markers:

```text
source_ref_added
supersedes_id
superseded_by_id
invalidating_source_refs
conflict_source_refs
promoted_from
deferred_candidate_used
```

Other markers such as `hot / hidden_from_projection / contradicted / uncertain / support_expanded / fallback_source_ref_rebound` can remain reason / audit markers at v0 implementation time instead of becoming first-round enums.

### 4.1 Visibility lifecycle

用于表达某个 item 是否仍应在 prompt-facing / planning-facing projection 中可见或优先。

Canonical visibility states / markers：

```text
active
hot
cooling
cooled
dormant
reactivated
hidden_from_projection
carried_forward
not_carried
```

适用 store：

- `active_attention`：主 lifecycle。active / hot / cooling / cooled / reactivated / carried_forward / not_carried 是核心状态。
- `thread_trace`：可有 dormant / reactivated，但 thread 的语义存在不因 dormant 消失。
- `reflective_frames`：可有 projection-level carried_forward / not_carried / hidden_from_projection，但 frame 的 semantic status 另行表达。
- `reaction_records`：通常不以 visibility lifecycle 改写本体；可有 hide / suppressed_from_projection 的 visible-surface marker。
- `knowledge_activations`：可有 weak / live / hidden_from_projection，但其 core status 属于 warrant validity。

规则：

```text
cooling ≠ invalidation
not_carried ≠ deleted
hidden_from_projection ≠ false
reactivated ≠ proven true
```

### 4.2 Semantic validity lifecycle

用于表达一个 memory statement 是否仍被当前 source-so-far 支持。

Canonical validity states / markers：

```text
provisional
source_supported
refined
resolved
superseded
invalidated
rejected
contradicted
uncertain
retired
```

适用 store：

- `concept_registry`：source_supported / refined / superseded / invalidated / retired；resolve 只关闭 attached ambiguity，不关闭 concept 本体。
- `thread_trace`：source_supported / provisional / resolved local development / dormant / reactivated / superseded / split / merge / retired。
- `reflective_frames`：working / source_supported / superseded / invalidated / retired。
- `knowledge_activations`：weak / plausible / strong / rejected / dropped；不能变成 source truth。
- `active_attention`：通常只带 provisional / resolved 等轻量 marker，不承载 stable semantic truth。
- `reaction_records`：visible trace 不以 semantic validity 标记为 book truth；可通过 reconsolidation 解释 later reinterpretation。

### 4.3 Evidence lineage lifecycle

用于表达 source_refs、supporting evidence、later correction 与 reinterpretation 的关系。

Canonical evidence events：

```text
source_ref_added
source_ref_merged
support_expanded
conflict_source_ref_added
invalidated_by_source_ref
superseded_by_item_id
supersedes_item_id
reconsolidated_by_record_id
reconsolidated_by_reaction_id
promoted_from_item_id
promoted_from_reaction_id
deferred_candidate_used
fallback_source_ref_rebound
```

规则：

- update 不覆盖旧 source_refs。
- merge 必须 dedupe。
- supersede 必须双向链接。
- invalidate 必须保留 invalidating_source_ref。
- knowledge activation reject 必须保留 conflict_source_ref。
- reaction reconsolidation 必须链接 prior_reaction_id / new_reaction_id。
- reflective promotion 必须保留 supporting_source_refs 与 promoted_from。

### 4.4 Audit / evaluation lifecycle

用于表达一次 management action 如何被记录和评估，但不进入 runtime memory。

Canonical audit / eval markers：

```text
management_event_recorded
audit_only
evaluation_only
probe_snapshot_only
no_runtime_write
manual_repair_recorded
failure_recorded
```

适用对象：

- `unit_span_ledger`
- `read_audit`
- `settlement_audit`
- `management_audit`
- evaluation artifacts
- probe snapshots
- judge reports

这些 lifecycle 不能混为一谈。Audit 可以说明某次状态变化为何发生，但不能反向成为 memory truth。Evaluation 可以发现 stale memory 或 pollution，但不能直接写 runtime memory。

------

## 5. Store-specific Operation Matrix

本节是本设计的核心 contract。它不重定义 store identity，只定义每个 store 的合法 management / evolution operations。

### 5.1 Summary matrix

| Store                     | Primary lifecycle                 | Legal operations                                             | Restricted / exceptional operations                 | Default prohibited                                  |
| ------------------------- | --------------------------------- | ------------------------------------------------------------ | --------------------------------------------------- | --------------------------------------------------- |
| `active_attention`        | visibility                        | create, update, refresh, reactivate, resolve, cool, drop hot-view, link, carry_forward, not_carried | drop as destructive removal only for mistaken item  | stable semantic truth, semantic invalidate          |
| `concept_registry`        | semantic validity + evidence      | create, update, refresh, merge, link, resolve_local_ambiguity, supersede, invalidate/reject, retire | drop only corrupted/mistaken                        | destructive overwrite, prior knowledge as truth     |
| `thread_trace`            | development validity + visibility | create, update, refresh, link, resolve_local_development, reactivate, cool/dormant, supersede, split, merge, retire | drop only mistaken thread                           | theme-only link, overwrite                          |
| `reflective_frames`       | slow-cycle semantic validity      | promote, withhold, update, supersede, invalidate, retire, link_to_supporting_items, chapter_carry_forward, resolve_frame_question | manual repair audited                               | read-path write, per-unit reflection                |
| `reaction_records`        | visible trace lineage             | append, annotate/link, supersede_visible_reaction, reconsolidate, hide/remove with explicit reason | semantic promotion only by explicit op / slow-cycle | automatic concept/thread promotion, silent deletion |
| `knowledge_activations`   | warrant validity                  | create_activation, update_warrant, strengthen, weaken, reject, drop, reactivate, add_conflict_source_ref, change_use_policy_mode | source-grounded concept write must be separate      | treating prior as source truth                      |
| `reconsolidation_records` | reinterpretation ledger           | append_reinterpretation_event, link_prior_reaction, link_new_reaction, classify_change_kind | correction only manual audited                      | overwrite, independent semantic claim               |
| Audit / ledger artifacts  | diagnostic                        | append audit, compact deltas, management_event_recorded, evaluation_only | explicit projection gate later                      | runtime prompt memory                               |

### 5.2 `active_attention`

`active_attention` 是当前最热的 near-term reading state。它主要承载 visibility lifecycle，不承载 stable semantic truth。

Legal operations：

```text
create
update
refresh
reactivate
resolve
cool
drop
link
carry_forward
not_carried
```

Rules：

- `create/update`：当前 source 引入仍会拉动后续阅读的 question、tension、focus、motif、working distinction。
- `refresh`：当前 source 再次支持该 active item，merge source_refs，可能保持 hot。
- `reactivate`：cooled/resolved item 被当前 source 重新激活。
- `resolve`：local focus / question / tension 被 current source 暂时关闭。
- `cool`：从 hot view 降温，不是 semantic invalidation。
- `drop`：主要是 hot-view removal。除 corrupted / mistaken item，不应作为事实删除。
- `carry_forward / not_carried`：由 slow-cycle / chapter boundary 决定该 item 是否跨章保留。

Read-path 权限：

- 可以 create/update/reactivate/resolve。
- 可以提出 narrow `cool`，但仅当 current source directly discharges hot focus。
- 不得用 `drop` 表达 semantic invalidation。
- 不得写 supersede / invalidate。

Slow-cycle 权限：

- general cooling、carry-forward、chapter boundary not_carried。
- 可把稳定内容作为 promotion candidate，但不能把 active item silent overwrite 成 reflective truth。

### 5.3 `concept_registry`

`concept_registry` 是 source-grounded concept / object / definition / model / classification / named distinction registry。Concept 本体通常不被 resolve 成“完成”；resolve 只关闭 attached ambiguity / pending question。

Legal operations：

```text
create
update
refresh
merge
link
resolve_local_ambiguity
supersede
invalidate / reject
retire
drop only for corrupted or mistaken entry
```

Rules：

- 后文补充定义时使用 `refresh / refine / update`，保留旧 source_refs。
- 后文修正定义时使用 `supersede`，旧 item 保留，不能 silent overwrite。
- source 证明旧概念理解错误时使用 `invalidate`，保留 invalidating_source_ref。
- prior knowledge 不能直接写成 concept truth。只有 source text itself establishes the concept，才可通过 separate source-grounded concept op 写入。
- `merge` 需要同一 source-grounded object 的 evidence，不是 theme similarity。
- `drop` 只用于 mistaken key、corrupted payload、manual repair，不是正常 lifecycle。

### 5.4 `thread_trace`

`thread_trace` 是 development line，不是 concept dictionary。它记录 argument、motif、contrast、question、relationship 如何跨 source spans 展开。

Legal operations：

```text
create
update
refresh
link
resolve_local_development
reactivate
cool / dormant
supersede
split
merge
retire
drop only for mistaken thread
```

Rules：

- `resolve_local_development` 关闭当前 thread 的某个 development question，不代表整条 thread 永久终止。
- Thread 可 dormant 后 reactivated。
- Thread merge/split 必须有 source evidence，不能只凭主题相似。
- theme-only association 不能成为 thread link。
- 后文揭示“这条线其实是另一条线的一部分”时，优先 split / merge / supersede，并保留 source_refs。

### 5.5 `reflective_frames`

`reflective_frames` 是 slow-cycle promoted higher-order memory。它只能由 slow-cycle / chapter/session boundary 正常写入；Read-path 不写。

Legal operations：

```text
promote
withhold
update
supersede
invalidate
retire
link_to_supporting_items
chapter_carry_forward
resolve_frame_question
```

Rules：

- `promote` 必须有 supporting source set 或 promoted_from item/reaction/source_refs。
- `withhold` 是合法结果：candidate 不足，不写 memory。
- `update` 必须 source-ref-preserving。
- `supersede` 保留旧 statement，并写 superseded_by / supersedes。
- `invalidate` 需要 later source evidence 或 manual repair reason。
- 不做 per-unit reflection。
- 不把 chapter summary dump 写成 reflective truth。

### 5.6 `reaction_records`

`reaction_records` 是 visible trace ledger，不是 semantic memory。默认 append-only。

Legal operations：

```text
append
annotate / link if safe
supersede_visible_reaction
reconsolidate
hide / remove only under explicit manual or policy reason
no semantic promotion unless explicit op or slow-cycle
```

Rules：

- Strong reaction 不自动进入 semantic memory。
- Reaction deletion / hiding 不应自动删除 linked semantic memory。
- `supersede_visible_reaction` 用于 visible wording / visible interpretation 的 later correction，不等同于 concept supersede。
- `reconsolidate` 解释 visible meaning changes，但不在 reaction store 中写 book truth。
- Reaction records 可进入 recent reaction digest，但必须带 warning：visible trace, not semantic truth。

### 5.7 `knowledge_activations`

`knowledge_activations` 是 prior / external knowledge warrant ledger，不是 source truth。

Legal operations：

```text
create_activation
update_warrant
strengthen
weaken
reject
drop
reactivate
add_conflict_source_ref
change_use_policy_mode
```

Rules：

- status 变化必须由 source trigger、reading warrant 或 conflict source refs 支撑。
- 它不能单独驱动 detour or visible route disclosure。
- `reject` 不是删除；它保留 conflict_source_ref 与 warrant failure reason。
- `drop` 表示不再可用或无价值，但应保留 reason。
- change_use_policy_mode is a local knowledge-use gating result, not procedural memory and not prompt/policy self-modification. It must be derived from current activation statuses and warrants, not from free-form reflection.
- 如果 source text itself establishes the concept，应通过 separate concept op 写入 `concept_registry`；knowledge activation 仍只保留 recognition / warrant context。

### 5.8 `reconsolidation_records`

`reconsolidation_records` 是 reinterpretation ledger，不是 reflective frame，不替代 supersede。

Legal operations：

```text
append_reinterpretation_event
link_prior_reaction
link_new_reaction
classify_change_kind
no overwrite
no independent semantic memory claim
```

Rules：

- 只记录 later reading materially changes earlier visible thought 的事件。
- 它服务 visible trace lineage 与 FVI diagnosis。
- 若 later correction 改变 semantic memory，则另行对 concept/thread/reflective item 执行 supersede / invalidate。

### 5.9 Audit / ledger artifacts

Artifacts：

```text
unit_span_ledger
read_audit
settlement_audit
management_audit
evaluation artifacts
probe snapshots
```

Rules：

- 它们不是 memory。
- 默认不进入 runtime prompt。
- 不能作为 lifecycle truth，除非后续 explicit projection gate 授权。
- `unit_span_ledger` 是 coverage / resume fact，不是 semantic memory。
- `read_audit` 记录 Read proposed what。
- `settlement_audit` 记录 deterministic system did what。
- `management_audit` 记录 lifecycle changed what。
- Evaluation artifacts 读 state、打分、诊断，不写 runtime memory。

------

## 6. Read-path vs Settlement vs Slow-cycle vs Manual Correction

### 6.1 Read-path permissions

Read-path 可以提出 lifecycle intent，但权限必须继承 Formation 边界。

Allowed from read-path：

```text
active_attention:
  create / update / refresh / reactivate / resolve
  narrow cool only when current source directly discharges hot focus

concept_registry:
  create / update / refresh / link
  resolve_local_ambiguity

thread_trace:
  create / update / refresh / link / reactivate
  resolve_local_development
```

Read-path 不允许：

```text
write reflective_frames
write reaction_records directly
write knowledge_activations through ordinary memory_uptake_ops
write reconsolidation_records
finalize supersede
finalize invalidate / reject
drop semantic memory as normal lifecycle
promote reflective memory
rewrite whole object or whole store
modify audit / evaluation artifacts
modify planning state except detour_need intent
```

Read-path 可以表达 “this seems to correct earlier understanding”，但 settlement 应转成 `deferred_to_management` 或 `deferred_to_slow_cycle`，除非后续设计明确授权极窄 read-path supersede。

### 6.2 Settlement / state_ops permissions

Settlement 是 deterministic authority。它可以：

```text
normalize operation names and aliases
bind SourceRef from current source unit
merge / dedupe source_refs
upsert same-key items
apply canonical operation
reject illegal target store
reject illegal operation
skip malformed payload
defer conflict or supersede to Management / slow-cycle
record compact op outcome
```

Settlement 不应：

```text
invent semantic support
decide high-level reflective truth
silently overwrite old memory
silently delete semantic memory
turn reaction into concept
turn prior knowledge into source truth
collapse visibility and validity
```

`state_ops` 应保持 apply canonical ops 的 deterministic role；semantic admission 与 lifecycle legality 应尽量由 settlement pre-check 与 Management contract 明确，而不是让 state_ops 暗中承载所有语义判断。

### 6.3 Slow-cycle permissions

Slow-cycle 可以做：

```text
general active_attention cooling
carry_forward / not_carried
reflective promotion / withhold
chapter consolidation
reconsolidation
knowledge activation updates
supersede candidate review
cross-chapter evidence merge
macro carry-forward focus, separated from memory consolidation
```

Slow-cycle 不能做：

```text
general planner
prompt self-refiner
book-route optimizer
silent overwrite
future-text reading
unbounded memory manager agent
automatic reaction-to-semantic promotion without explicit op
prior-knowledge-to-book-truth merge
```

Slow-cycle may propose or select supersede / invalidate / retire candidates. Final state mutation still goes through deterministic state_ops / settlement-style application. Slow-cycle is not allowed to silently rewrite stores as free-form JSON.

### 6.4 Manual correction / admin repair

Manual repair is allowed, but only under strict rules：

```text
source-ref-preserving
audited
explicit reason_code
operator / admin actor recorded
no silent rewrite
no deletion without tombstone or repair event
before/after compact status and ID deltas recorded
```

Manual repair can fix:

- corrupted entry；
- mistaken key；
- impossible source_ref；
- obvious field-shape mismatch；
- policy-required reaction hiding；
- explicit human correction of invalid memory.

Manual repair should not become normal lifecycle. It is exceptional repair.

### 6.5 Evaluation permissions

Evaluation 可以：

```text
read stores
read audit
judge quality
score snapshots
report stale / polluted / unsupported memory
recommend design or repair action
```

Evaluation 不应：

```text
directly write runtime memory
change statuses
delete items
modify projection
inject judge comments into prompt
```

If evaluation finds failure, it should enter audit / design feedback / manual repair queue, not directly mutate memory.

------

## 7. 后文修正前文：Correction / Supersede / Invalidation Design

后文修正前文是 Reading Companion memory evolution 的核心场景。

### 7.1 When it is update / refine

Use `update / refine / refresh` when：

```text
the old item remains source-supported
new source adds precision, example, scope, definition, or relation
no contradiction with old statement
same item identity remains valid
```

Action：

```text
merge source_refs
preserve old source_refs
update summary only if compatible
mark status = refined or source_supported
record source_ref_added / support_expanded
```

Example：作者先提出一个 named distinction，后文补充其第二个维度。旧 distinction 没错，只是更完整。

### 7.2 When it is resolve

Use `resolve` when：

```text
a local question / ambiguity / tension is answered by current source
the underlying concept/thread may still exist
no old statement is replaced
```

Action：

```text
status = resolved
resolution_source_ref added
visibility may cool
future source may reactivate
```

Resolve 不等于永久完成。

### 7.3 When it is supersede

Use `supersede` when：

```text
later source establishes a new interpretation that replaces an earlier current understanding
old item was reasonable under source-so-far
new item is incompatible enough that both cannot be current truth
```

Action：

```text
old.status = superseded
old.superseded_by_id = new_id
new.supersedes_id = old_id
new.source_refs include new supporting refs
old source_refs retained
management_event recorded
projection excludes old as current truth
```

Supersede 不等于 destructive overwrite。旧 item 保留 because it explains the reading path.

### 7.4 When it is invalidate / reject

Use `invalidate` when：

```text
later source directly contradicts or disproves old memory
old claim should not be treated as source-supported
there may or may not be a replacement item
```

Use `reject` when：

```text
candidate or warrant fails
knowledge activation no longer has valid warrant
deferred candidate is reviewed and not admitted
```

Action：

```text
old.status = invalidated or rejected
invalidating_source_refs / conflict_source_refs retained
reason_code recorded
projection blocks current use
active_recall may retrieve only with warning / audit purpose
```

Invalidation / rejection requires later source evidence or explicit warrant failure. Do not invalidate because the item is merely not currently useful.

### 7.5 When it is reconsolidation

Use `reconsolidation` when：

```text
later reading materially changes the meaning of an earlier visible reaction
the earlier reaction remains a visible historical trace
the semantic store may or may not need separate supersede
```

Action：

```text
append reconsolidation_record
link prior_reaction_id
link new_reaction_id
classify change_kind
do not overwrite prior reaction
if semantic memory changed, separately supersede / invalidate semantic item
```

### 7.6 When it is only active_attention cooling

Use cooling when：

```text
the item no longer pulls near-term reading
the question was answered enough for now
the chapter moved on
there is no semantic contradiction
```

Action：

```text
visibility status = cooling / cooled
semantic validity unchanged
item may become dormant or not_carried
```

### 7.7 When to defer

Defer to Management when：

```text
multi-source conflict
uncertain identity / same-key ambiguity
possible supersede of concept/thread/reflective item
source evidence missing or weak
drop / delete requested
manual repair needed
```

Defer to Slow-cycle when：

```text
chapter-level synthesis
reflective promotion
visible reaction reinterpretation
knowledge activation status review
cross-chapter carry-forward
```

### 7.8 Projection / Retrieval stale prevention

Planning / Retrieval must not use stale item as current truth:

```text
superseded: exclude from normal current projection; may show only as lineage
invalidated / rejected: exclude from normal projection
retired: exclude unless explicit historical recall
cooled / dormant: low priority, not false
provisional: include only with status marker
```

Active recall may retrieve superseded / invalidated items only when the intent is correction lineage, audit, or explaining a later reinterpretation; it must carry warning markers.

Look-back should use SourceRefs to recalibrate against source text.

Audit records old/new IDs, source_refs, operation, actor, outcome, failure reason, projection impact.

------

## 8. Deferred Candidates from Formation

Formation already defines deferred outcomes such as `deferred_to_slow_cycle` and `deferred_to_management` for ops that need lifecycle semantics beyond read-path. This page formalizes their later use.

Rules：

```text
deferred candidate is not settled memory
deferred candidate cannot enter prompt-facing projection
deferred candidate cannot be returned by Retrieval as memory item
deferred candidate can be read by Management / slow-cycle as candidate evidence
using a deferred candidate requires re-admission, validation, SourceRef check, and settlement
```

Minimum deferred candidate fields：

```text
deferred_candidate_id
created_at
source_span_id
candidate_target_store
candidate_operation
candidate_payload_summary
source_refs
reason_for_deferral
required_review_surface
expires_after_scope
```

Consumption：

```text
slow-cycle / management reads candidate
checks source_refs and current state
chooses accept / normalize / reject / expire / remain audit-only
records deferred_candidate_used when accepted or used in reasoning
```

Preventing garbage bucket behavior：

- Candidates expire at chapter/session boundary unless explicitly retained.
- Candidate list should be bounded.
- A candidate that cannot bind SourceRef remains audit-only.
- Repeated unresolved candidates should be summarized and retired, not carried forever.
- Deferred candidates do not count as memory quality positives.

Recommended v0 storage posture：do not introduce a new memory store. Deferred candidates can live inside settlement / management audit as compact candidate records. If implementation later needs a file, it should be `deferred_candidates.jsonl` under audit territory, not a runtime memory store.

------

## 9. SourceRef and Evidence Lineage

SourceRef is the evidence spine of memory evolution.

### 9.1 SourceRef-preserving lifecycle rules

```text
update:
  preserve old source_refs
  add new source_refs
  dedupe by source_span_id / role / quote

merge:
  merge source_refs from both items
  preserve source roles when possible

supersede:
  old item keeps old source_refs
  new item carries new supporting source_refs
  old.superseded_by_id and new.supersedes_id both recorded

invalidate:
  old item keeps original support
  invalidating_source_refs added
  reason_code recorded

knowledge reject:
  conflict_source_refs retained

reaction reconsolidation:
  prior_reaction_id and new_reaction_id linked
  source_refs remain on reactions

reflective promotion:
  supporting_source_refs and promoted_from retained

deferred candidate:
  deferred_candidate_used recorded when consumed
```

### 9.2 SourceRef digest and stale evidence

`source_ref_digest` should not imply that all referenced items are current truth. Projection should carry status / validity markers with refs where possible. A source_ref attached to a superseded item remains evidence for history, not current support.

### 9.3 Missing source_refs

Items missing source_refs should be treated as degraded:

```text
active_attention:
  may remain hot only if accepted-unit fallback exists and audit marks fallback

concept_registry / thread_trace:
  should not be promoted, superseded, or used as source-grounded truth until rebound

reflective_frames:
  cannot be newly promoted without supporting source set

knowledge_activations:
  must at least have trigger_source_ref or explicit warrant source

reaction_records:
  visible record without anchor is a persistence defect
```

Fallback source binding items may be retained as provisional / needs_rebind, but Management cannot promote them or use them to invalidate other items until source evidence is precise enough.

------

## 10. Management Audit Design

This design proposes a minimal `management_audit` diagnostic artifact. It can be a new JSONL stream or an enriched settlement/slow-cycle audit section; exact implementation shape belongs to Audit / Implementation Handoff.

Minimum fields：

```text
management_event_id
timestamp
source_event_type
actor
target_store
target_id
operation
previous_status
new_status
source_refs_added
source_refs_used
invalidating_source_refs
supersedes_id
superseded_by_id
deferred_candidate_ids
reason_code
outcome
failure_reason
projection_impact
```

MVP ManagementEvent for first implementation readiness:

```text
management_event_id
timestamp
actor
target_store
target_id
operation
previous_visibility
new_visibility
previous_validity
new_validity
source_refs_used
source_refs_added
supersedes_id
superseded_by_id
invalidating_source_refs
reason_code
outcome
projection_impact
```

Fields such as `manual_repair_reason / policy_version / slow_cycle_run_id / linked_item_ids / deferred_candidate_ids` can remain later / optional for the first implementation pass. They are useful, but should not force the v0 patch into a full audit schema migration.

Optional fields：

```text
previous_visibility
new_visibility
previous_validity
new_validity
linked_item_ids
manual_repair_reason
policy_version
settlement_transaction_id
read_audit_ref
slow_cycle_run_id
```

Rules：

- management audit is diagnostic artifact, not runtime memory.
- no full snapshot per management event by default.
- compact before/after status and ID delta are enough.
- management audit can be consumed by Memory Evaluation.
- management audit should not enter prompt by default.
- failure reason is required when operation is rejected / skipped / deferred.

`projection_impact` should be conservative：

```text
none
may_affect_active_attention_digest
may_affect_concept_digest
may_affect_thread_digest
may_affect_reflective_digest
may_affect_recent_reaction_digest
blocked_from_projection
unknown_due_to_projection_budget
```

It should not claim the item definitely appeared in prompt because projection is bounded.

------

## 11. Projection and Retrieval Implications

This page does not design Retrieval, but it sets lifecycle-facing constraints.

### 11.1 Projection constraints

Projection should split current use from lineage use:

```text
current_truth_projection:
  excludes superseded / invalidated / rejected items
  includes provisional only with marker
  includes cooled/dormant only at low priority

lineage_projection:
  may include superseded / invalidated / rejected items
  only for correction_lineage, audit_explanation, FVI diagnosis, reconsolidation review
  must carry warning markers and current replacement IDs
```

Prompt-facing and planning-facing projections should:

```text
include active/hot items normally
include provisional items only with marker
de-prioritize cooling/cooled/dormant items
exclude invalidated/rejected items from normal current truth
exclude superseded items from current truth, unless lineage is explicitly needed
exclude deferred candidates
include knowledge_activations only with warrant/status marker
include reaction_records only as visible trace, not semantic truth
```

### 11.2 Planning stale-memory prevention

Planning memory projection must preserve:

```text
status
source_refs
supersede / validity markers
visibility markers
warrant markers for knowledge activation
reaction trace marker for reaction_records
```

Planning must not use a stale memory item as detour / visible route disclosure reason. Navigation already forbids reaction digest and knowledge activation as sole detour drivers; this Management design adds the lifecycle markers needed to enforce that boundary.

### 11.3 Retrieval implications

Retrieval should use:

```text
status
source_refs
supersede chain
validity markers
visibility markers
store type
chapter / source scope
links
```

Active recall may retrieve superseded / invalidated item only with explicit intent:

```text
correction_lineage
audit_explanation
why_current_projection_changed
source_conflict_review
```

Look-back remains source calibration: it goes to source text, not memory truth.

------

## 12. Compatibility with Prior Designs

Compatibility check:

```text
Does not redefine Memory Ontology:
  yes. Store identities are inherited.

Does not extend read-path target stores:
  yes. Read-path remains active_attention / concept_registry / thread_trace only.

Does not let Read write final state:
  yes. Read proposes; settlement / Management settles.

Does not make Management Retrieval:
  yes. Only lifecycle-facing retrieval constraints are defined.

Does not make Management Evaluation:
  yes. Evaluation remains read / judge / report only.

Does not swallow Planning / Navigation:
  yes. Detour, look-back, active_recall policy remains separate.

Does not treat reaction_records as semantic memory:
  yes. Reaction records are visible trace.

Does not treat knowledge_activations as source truth:
  yes. They remain warrant ledger.

Does not treat audit / eval artifact as runtime memory:
  yes.

Respects Navigation boundary:
  yes. Navigation does not write memory; active_recall/look_back/detour remain support/path mechanisms.

Respects P0 Simplicity and Universality:
  yes. It tightens existing stores and ops; no new manager agent, vector DB, graph DB, Memory OS.
```

------

## 13. Accepted Constraints and Deferred Directions

Accepted constraints:

- **No memory manager agent.** Current need is lifecycle contract + deterministic settlement + slow-cycle review, not another autonomous actor.
- **No vector DB / graph DB.** Current risk is semantic instability and auditability, not missing infrastructure.
- **No Memory OS.** Reading Companion is a source-grounded co-reader, not a general memory runtime.
- **No `structure_memory`.** Structural memory should be expressed through concept/thread/reflective stores.
- **No RL Memory-as-Action.** Current project lacks reward and operation-level eval maturity for RL editing.
- **No per-unit reflection.** Reflective frames belong to slow-cycle / chapter/session boundary.
- **No destructive overwrite.** Supersede / invalidate / retire preserve lineage.
- **No full snapshot per lifecycle event.** Compact event audit + ID/status/source delta is preferred.
- **No retrieval implementation.** This page only sets lifecycle constraints.
- **No evaluation rubric.** This page only defines audit hooks and evaluability.
- **No Codex roadmap.** Implementation notes remain readiness classification, not task list.
- **No prompt / policy rewriting by Management.** Procedural memory remains out of scope.
- **No slow-cycle as general planner.** Slow-cycle may consolidate and carry forward; it does not optimize the book route.

Deferred directions:

- exact management audit schema；
- retrieval taxonomy and stale-memory filtering implementation；
- active_recall / look_back / detour policy；
- slow-cycle / macro-planning full strategy；
- evaluation rubric；
- implementation handoff.

------

## 14. What This Design Changes or Tightens

### Retained

- current stores: `active_attention / concept_registry / thread_trace / reflective_frames / reaction_records / knowledge_activations / reconsolidation_records`;
- file-based JSON / JSONL;
- deterministic `state_ops`;
- SourceRef-first evidence spine;
- read-path target stores;
- slow-cycle as consolidation boundary;
- compact audit posture.

### Tightened

- lifecycle split into visibility vs semantic validity;
- store-specific legal operations;
- `cool / resolve / drop / retire / supersede / invalidate` semantics;
- destructive overwrite prohibition;
- SourceRef-preserving update and supersede;
- deferred candidates are not memory;
- reaction_records and knowledge_activations cannot masquerade as semantic truth;
- evaluation cannot directly mutate runtime memory;
- audit requires management event minimum.

### Reinterpreted

- `drop` becomes exceptional repair / hot-view removal, not normal semantic deletion.
- `cool` becomes visibility-only.
- `resolve` becomes local closure, not permanent truth finalization.
- `supersede` becomes first-class semantic validity change.
- `knowledge_activations.supersede → rejected` is better named as reject / warrant failure in design language.
- `reaction_records.supersedes_reaction_id` is visible-trace supersede, not semantic supersede.

### Deferred

- exact field names for all lifecycle statuses;
- projection filtering implementation;
- retrieval intent taxonomy;
- memory evaluation rubric;
- Codex task planning.

------

## 15. Design Implications for Later Pages

### Memory Retrieval / Utilization

Retrieval must become status-aware. It should not return superseded / invalidated / rejected items as current truth. It must distinguish active recall, correction lineage recall, look-back source calibration, and slow-cycle consolidation support.

### Memory Audit / Evaluation

Audit / Evaluation should use per-op and per-management-event outcomes. Memory Quality can inspect whether important items are retained and whether stale items are blocked. FVI can inspect whether superseded / rejected material leaks into visible reactions.

### Detour / Look-back / Active Recall Policy

Detour and active_recall should consume lifecycle markers. Look-back should calibrate against source when memory status is uncertain, contradicted, or superseded.

### Slow-cycle / Macro-planning

Slow-cycle receives legal authority for cooling, carry-forward, reflective promotion, reconsolidation, knowledge activation updates, and supersede candidate review. It must keep memory consolidation separate from macro carry-forward. Slow-cycle may prepare route-trace summaries for future display only if explicitly designed, but it must not create user route controls or route-control output.

### Visible Reading Route Surface Boundary

Future route disclosure must not cite stale, rejected, invalidated, or knowledge-only material as current source truth. If it uses memory, it must respect status and source_refs. `route_trace_display_candidate` can only be an audit/display marker, not a lifecycle state. Slow-cycle cannot create user-facing route steering, display-driven navigation, or accept/reject route state.

### Implementation Handoff

Implementation should align vocabularies, harden source-ref-preserving merge, enrich audit, and filter projections, without adding new infrastructure.

------

## 16. Implementation Readiness Notes

### Ready for narrow implementation

These can enter small-window validation if this design is accepted:

```text
lifecycle status vocabulary alignment
StateOperationType / nodes normalization alignment, especially resolve
source_ref-preserving merge hardening
concept/thread drop restriction or audit marker
reflective supersede audit enrichment
knowledge activation reject / drop audit
management_event compact audit
projection filtering for superseded / invalidated / rejected items
fallback SourceRef status marker for non-promotable items
```

### Needs Retrieval design first

```text
full retrieval taxonomy
active_recall behavior for superseded / invalidated lineage
status-aware retrieval ranking
correction-lineage recall
```

### Needs Audit / Evaluation design first

```text
full management_audit schema
Memory Quality lifecycle dimensions
FVI stale-memory leakage checks
manual repair queue semantics
```

### Needs Slow-cycle / Macro-planning design first

```text
chapter-level supersede candidate review
carry-forward obligation policy
promotion thresholds
cross-chapter retirement policy
```

### Needs Implementation Handoff

```text
schema field migration
backward compatibility details
test plan
artifact file additions, if any
runtime validation windows
```

### Explicitly not now

```text
vector / graph retrieval
manager agent
Memory OS
Visible Reading Route Surface Boundary
full Memory Evaluation rubric
full implementation roadmap
per-unit reflection
```

------

## 17. Optional Open Questions

1. **Exact status field vocabulary.** Current code uses free-form `status`. This design defines canonical meanings, but exact enum field names should wait for Implementation Handoff to avoid premature migration churn. It does not block Retrieval design, but it affects implementation.
2. **Whether to introduce `management_audit.jsonl` or enrich `settlement_audit.jsonl`.** The design needs management audit events; storage shape can wait for Audit / Implementation Handoff. It does not block conceptual adoption.
3. **How long deferred candidates persist.** The design says bounded and expiring, but exact TTL may depend on slow-cycle design. It does not block narrow lifecycle implementation.
4. **How much supersede lineage appears in user-visible UI.** Runtime prompt should not see stale truth, but UX display of reading evolution belongs to later product / visible route disclosure / audit surface design.

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

| Evidence                                            | Current fact shown                                           | Supports design judgment                                     | Stability                      | Runtime validation gap                                      |
| --------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------ | ----------------------------------------------------------- |
| `docs/product-overview.md`                          | Product is a living, text-grounded co-reader, not summary engine or service assistant. | Management must preserve source-grounded reading evolution, not user-profile memory. | Stable product constraint      | None for product; runtime behavior separate                 |
| `docs/current-state.md`                             | Current direction uses Memory Quality / Spontaneous Callback / FVI; diagnostic run shows memory ops emitted and SourceRef carry-forward repair. | Lifecycle audit and source-ref-preserving carry-forward are real needs. | Current status evidence        | Runtime rows not independently opened here                  |
| `docs/source-of-truth-map.md`                       | Repo-first durable truth; canonical docs and artifacts own durable project state. | File-based JSON / JSONL and auditable artifact design remain appropriate. | Stable governance              | N/A                                                         |
| `docs/backend-reading-mechanism.md`                 | Shared `book_document.json` is source truth; `attentional_v2` uses inline paragraph-offset SourceRef; no shared Anchor Bank. | Source corpus is not memory; SourceRef is evidence spine.    | Stable shared boundary         | Runtime source-ref quality still needs row audit            |
| `docs/backend-reading-mechanisms/attentional_v2.md` | Current loop is Navigate → Read → Runner settlement → slow-cycle; Read is bounded. | Management cannot authorize Read to write high-level memory. | Stable current mechanism       | Runtime quality not guaranteed                              |
| `schemas.py`                                        | Defines StateOperationType, store schemas, SourceRef, detour, reflective, knowledge, reaction, reconsolidation objects. | Current stores are sufficient; lifecycle vocabulary exists but needs semantics. | Contract-level evidence        | Some enum / normalization drift exists                      |
| `state_ops.py`                                      | Deterministic apply supports active cooling/resolution/drop, concept/thread merge/drop, source_ref merge, reflective supersede. | Preserve deterministic apply; tighten legal operation semantics and destructive overwrite ban. | Implementation fact            | Does not itself provide per-op outcome                      |
| `slow_cycle.py`                                     | Builds reaction records, reflective promotion, reconsolidation, compatibility projection. | Slow-cycle is correct locus for promotion / reconsolidation. | Implementation fact            | Full chapter consolidation details truncated in tool output |
| `storage.py`                                        | Lists memory stores and audit ledgers as file artifacts.     | No need for new DB; artifact boundaries are already present. | Stable implementation          | Actual runtime artifact rows not opened                     |
| `observability.py`                                  | Records read_audit and settlement_audit with compact deltas. | Add management audit minimum rather than full snapshots.     | Implementation fact            | Per-op outcome missing                                      |
| `state_projection.py`                               | Builds bounded prompt-facing digests for active/concept/thread/reflective/source refs/reactions. | Projection must become lifecycle-status aware; projection is not authoritative state. | Implementation fact            | Filtering for superseded/invalidated not fully specified    |
| `read_context.py`                                   | Distinguishes active_recall from look_back.                  | Retrieval implications must preserve memory recovery vs source calibration boundary. | Implementation fact            | Full Retrieval policy deferred                              |
| `knowledge.py`                                      | Knowledge activations have weak/plausible/strong/rejected/dropped status and warrant-based mode switching. | Knowledge activation is warrant ledger, not source truth.    | Implementation fact            | Need audit enrichment for reject/conflict refs              |
| `nodes.py`                                          | Normalizes state ops and surfaced reactions; filters visible internal handle leaks. | Need operation vocabulary alignment; visible trace must not leak handles. | Implementation fact            | `resolve` normalization gap                                 |
| `prompts.py`                                        | Read prompt limits memory_uptake_ops to active_attention/concept_registry/thread_trace and forbids writing reflective/reaction/audit layers. | Read-path permissions remain narrow.                         | Contract-level evidence        | Prompt alone not enough; settlement must enforce            |
| `source_spans.py`                                   | Defines SourceCursor/SourceSpan/SourceRef, quote binding, fallback, dedupe. | SourceRef-preserving update and fallback limitations are necessary. | Implementation fact            | Fallback-bound semantic memory must be audited              |
| `runner.py`                                         | Runner owns live loop, detour state, runtime load/save, and deterministic execution. | Management authority should stay runner/settlement-based.    | Implementation fact            | Tool output truncated before full settlement body           |
| `docs/backend-reader-evaluation.md`                 | Active long-span direction separates Memory Quality, Spontaneous Callback, FVI; audit artifacts are runtime evidence, not score inputs by themselves. | Management audit should support evaluation without becoming runtime memory. | Stable evaluation constitution | Evaluation rubric deferred                                  |

## B. Upstream Design Basis

The design route positions this as design 5, after Formation & Settlement, and explicitly assigns lifecycle, supersede, cool, resolve, legal operation matrix, destructive overwrite / soft invalidate / supersede / cooling, and slow-cycle promotion authority to this page.

P0 supplies the non-negotiable boundaries: `LLM proposes; deterministic runner settles`; source corpus / reading memory / planning state / audit trace / visible reaction / prior knowledge / evaluation evidence are separate; lifecycle must distinguish visibility and validity; slow-cycle cannot become a general planner or memory manager agent; file-based JSON / JSONL first; SourceRef-first auditability.

Memory Ontology supplies store identities and non-memory boundaries. This design intentionally does not redefine stores; it only defines legal lifecycle operations over them.

Memory Formation & Settlement supplies admission boundaries: read-path writes only active_attention / concept_registry / thread_trace; memory_uptake_ops are bounded write intents; SourceRef binding is core; supersede / invalidate / drop are deferred here.

Planning Ontology and Navigation Policy supply guardrails: Planning uses memory but does not own memory; Navigation does not write memory; active_recall / look_back / detour are related but distinct mechanisms.

Memory Assessment identifies the main weakness as contract-level semantic instability, especially lifecycle being a vocabulary rather than an evolution mechanism, the need to separate visibility lifecycle and semantic validity lifecycle, and the priority of supersede / invalidate / retire over destructive overwrite.

Planning Assessment is used only as boundary input: do not let Memory Management swallow Planning / Navigation / Visible Route Disclosure; detour, look-back, and active_recall are different mechanisms; slow-cycle cannot become a general planner.

## C. External Rationale, as Filtered Through the Assessments

This appendix uses external sources already surfaced in the upstream assessment/evidence materials, not new broad research.

### Zep

Original problem：temporal, dynamic agent memory with facts, entities, episodes, observations, validity and invalidity.

Supports：supersede / invalidate should preserve temporal/evidence lineage rather than overwriting.

Similarity：both need memory that can become stale or invalid under later evidence.

Difference：Zep is graph-backed enterprise/conversation memory; Reading Companion is file-based source-grounded reading memory.

Localized borrowing：borrow validity / invalidity / retired observation concepts; do not adopt graph DB.

Support type：Direct / Boundary.

### Mem0

Original problem：production long-term agent memory with add/search/update/delete operations and metadata.

Supports：operation-centric memory update/delete; write intent should pass through controlled pipeline.

Similarity：both need item identity, metadata, update/delete, conflict handling.

Difference：Mem0 is general agent/user memory; Reading Companion is book-source-grounded.

Localized borrowing：operation contract, update/delete semantics, metadata; not vector/graph-first infra.

Support type：Direct.

### LangGraph / LangMem

Original problem：framework-level memory concepts, hot-path vs background writes, semantic/episodic/procedural distinctions.

Supports：read-path vs slow-cycle split; background consolidation without putting all writes in hot path.

Similarity：both need different write timing and memory types.

Difference：framework docs are generic; Reading Companion stores are reading-specific.

Localized borrowing：hot/background write timing and type hygiene; do not adopt procedural prompt refinement now.

Support type：Analogical / Boundary.

### Letta / MemGPT

Original problem：context-window scarcity and memory hierarchy.

Supports：prompt-facing memory projection is not authoritative state; core/hot vs archival/durable separation.

Similarity：both need bounded prompt-facing memory.

Difference：Letta/MemGPT often center persona/user memory and OS-style paging.

Localized borrowing：block contract / bounded visibility; reject Memory OS migration.

Support type：Boundary / Analogical.

### Generative Agents

Original problem：LLM agents in social simulation with memory stream, reflection, planning.

Supports：not every observation becomes high-level memory; reflection is slow-cycle, evidence-accumulated operation.

Similarity：both need local observations to consolidate into higher-order memory.

Difference：Generative Agents does not make source-grounded book evidence first-class.

Localized borrowing：observation → reflection pacing; require SourceRef support in Reading Companion.

Support type：Analogical / Direct for slow-cycle.

### MemoryBank

Original problem：long-term companion memory with forgetting/reinforcement.

Supports：cooling / refresh / reactivation as visibility decay analog.

Similarity：both need lifecycle, not append-only.

Difference：MemoryBank is user/persona-centered; Reading Companion is source-centered.

Localized borrowing：forgetting curve as visibility lifecycle only, not semantic deletion.

Support type：Analogical / Negative.

### LongMemEval

Original problem：benchmarking long-term memory via stages such as extraction/indexing, retrieval, reading/use.

Supports：audit should let evaluation localize failures by stage.

Similarity：both need to distinguish memory quality from retrieval/utilization.

Difference：benchmark is conversation-memory oriented.

Localized borrowing：stage-aware diagnosis; not benchmark schema.

Support type：Background / Direct for evaluation decomposition.

### HaluMem

Original problem：hallucinations in memory systems can occur during extraction, updating, or QA.

Supports：management audit needs operation-level outcome and failure reason.

Similarity：Reading Companion memory pollution can occur in formation, update, projection, visible integration.

Difference：frontier benchmark, not reading-specific.

Localized borrowing：operation-level pollution diagnosis.

Support type：Background / Direct.

### CAM / ComoRAG

Original problem：reading / narrative memory organization and long narrative reasoning.

Supports：reading memory should be task-specific and support ongoing narrative/source understanding.

Similarity：closest external task shape.

Difference：frontier prototypes; may use more complex clustering/RAG loops.

Localized borrowing：reading-specific organization; not complex structure algorithms.

Support type：Analogical / Boundary.

### GraphRAG / RAPTOR / HippoRAG

Original problem：multi-granularity corpus retrieval and graph/hierarchical sensemaking.

Supports：links and higher-order frames may be useful.

Similarity：both handle long text and multi-hop/global sensemaking.

Difference：they are corpus indexing / RAG systems, not settled reading memory management.

Localized borrowing：local/global and multi-granularity thinking; reject graph/vector infra now.

Support type：Boundary / Negative.

### Reflexion

Original problem：episode-level verbal reflection for agents.

Supports：slow-cycle at chapter/session boundary, not per-unit reflection.

Similarity：both benefit from between-episode consolidation.

Difference：Reflexion often learns strategy; Reading Companion must not mix procedural strategy with book memory.

Localized borrowing：boundary reflection; no self-modifying prompt policy.

Support type：Analogical / Boundary.

### Information Foraging / rereading / metacomprehension

Original problem：when to seek information, when rereading helps calibration, how readers monitor comprehension.

Supports：look-back / detour / active_recall should remain separate from memory management; stale memory should trigger source calibration rather than silent overwrite.

Similarity：reading is local evidence-seeking, not task-planning.

Difference：human cognition studies do not define agent storage schemas.

Localized borrowing：source calibration vs memory recovery distinction.

Support type：Analogical / Background.

## D. Simplicity and Universality Check

- Existing stores are retained; no new semantic store is introduced.
- No memory manager agent is introduced.
- No vector DB / graph DB / Memory OS is introduced.
- Destructive overwrite is prohibited by default.
- SourceRef-first evidence lineage is central.
- Visibility lifecycle and semantic validity lifecycle are separated.
- Reaction records remain visible trace, not semantic memory.
- Knowledge activations remain warrant ledger, not source truth.
- Audit / evaluation artifacts remain diagnostic, not runtime memory.
- Management does not swallow Retrieval, Evaluation, Planning, Navigation, or Visible Route Disclosure.
- The design supports later Retrieval / Audit / Implementation without binding a full implementation now.

Remaining complexity risks：

```text
status vocabulary may proliferate if not normalized in Implementation Handoff
deferred candidates can become a garbage bucket without expiry
projection filtering may silently hide useful lineage unless Retrieval design handles correction recall
manual repair can become a shadow management process unless audited strictly
```

## E. Source Usage List

| External source           | Authors / Organization                        | Year      | Stable URL                                                   | Used for                                                     | Support type          |
| ------------------------- | --------------------------------------------- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------- |
| Generative Agents         | Joon Sung Park et al.                         | 2023      | https://arxiv.org/abs/2304.03442                             | slow-cycle promotion; not every observation becomes reflection | Direct / Analogical   |
| Mem0 paper                | Prateek Chhikara et al.                       | 2025      | https://arxiv.org/abs/2504.19413                             | operation-centric add/update/delete                          | Direct                |
| Mem0 docs                 | Mem0                                          | 2025–2026 | https://docs.mem0.ai/core-concepts/memory-operations/add     | memory operation pipeline                                    | Direct                |
| Zep paper                 | Preston Rasmussen et al.                      | 2025      | https://arxiv.org/abs/2501.13956                             | temporal validity, invalidation, evidence-backed facts       | Direct                |
| Zep docs                  | Zep                                           | 2025–2026 | https://help.getzep.com/graph-overview                       | facts/entities/episodes/observations boundary                | Direct / Boundary     |
| LangGraph Memory Concepts | LangChain                                     | 2025–2026 | https://docs.langchain.com/oss/python/concepts/memory        | semantic/episodic/procedural and hot/background writes       | Analogical            |
| LangMem                   | LangChain                                     | 2025–2026 | https://github.com/langchain-ai/langmem                      | background memory consolidation                              | Analogical / Boundary |
| MemGPT                    | Charles Packer et al.                         | 2023      | https://arxiv.org/abs/2310.08560                             | memory hierarchy / virtual context boundary                  | Boundary              |
| Letta memory blocks       | Letta                                         | 2025–2026 | https://docs.letta.com/guides/core-concepts/memory/memory-blocks | bounded memory block contract                                | Analogical            |
| MemoryBank                | Wanjun Zhong et al.                           | 2024      | https://ojs.aaai.org/index.php/AAAI/article/view/29946       | forgetting / reinforcement as visibility decay analogy       | Analogical / Negative |
| LongMemEval               | Di Wu et al.                                  | 2024      | https://arxiv.org/abs/2410.10813                             | stage-aware memory evaluation                                | Background / Direct   |
| HaluMem                   | Ding Chen et al.                              | 2025      | https://arxiv.org/abs/2511.03506                             | operation-level memory pollution                             | Background / Direct   |
| CAM                       | Rui Li et al.                                 | 2025      | https://arxiv.org/abs/2510.05520                             | reading-specific memory organization                         | Analogical            |
| ComoRAG                   | Juyuan Wang et al.                            | 2025      | https://arxiv.org/abs/2508.10419                             | narrative reasoning and targeted recall boundary             | Analogical            |
| GraphRAG                  | Microsoft Research / Darren Edge et al.       | 2024      | https://arxiv.org/abs/2404.16130                             | boundary for graph/global sensemaking                        | Boundary / Negative   |
| RAPTOR                    | Parth Sarthi et al.                           | 2024      | https://arxiv.org/abs/2401.18059                             | multi-granularity frame analogy                              | Boundary              |
| HippoRAG                  | Bernal Jiménez Gutiérrez et al.               | 2024      | https://arxiv.org/abs/2405.14831                             | link structure analogy, not graph DB adoption                | Boundary              |
| Reflexion                 | Noah Shinn et al.                             | 2023      | https://arxiv.org/abs/2303.11366                             | episode-boundary reflection boundary                         | Analogical            |
| Information Foraging      | Peter Pirolli, Stuart Card                    | 1999      | https://doi.org/10.1037/0033-295X.106.4.643                  | detour/look-back/retrieval boundary analogy                  | Background            |
| The rereading effect      | Katherine Rawson, John Dunlosky, Keith Thiede | 2000      | https://doi.org/10.3758/BF03209348                           | look-back as calibration, not management                     | Background            |
| Metacomprehension         | John Dunlosky, Amanda Lipko                   | 2007      | https://doi.org/10.1111/j.1467-8721.2007.00509.x             | source calibration boundary                                  | Background            |
