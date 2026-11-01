# Slow-cycle / Macro-planning Design v0

## 设计正文

### 1. Scope and Purpose

本设计定义 Second Reader / Reading Companion 在 `chapter / session / boundary` 时的 **Slow-cycle / Macro-planning v0** 机制。

它继承 P0 Shared Charter 的共同边界：Memory 与 Planning 服务同一个 source-grounded co-reading mind；运行原则是 **LLM proposes; deterministic runner settles**；source corpus、reading memory、planning state、audit trace、visible reaction、future visible route disclosure、knowledge activation、evaluation evidence 必须分开。

它继承 Memory Ontology、Formation、Management、Retrieval 的边界：slow-cycle 只能读取 settled memory 与授权 retrieval packet；不得把 raw `Read.memory_uptake_ops`、failed / skipped settlement ops、deferred candidate、prompt projection、audit dump、evaluation report 当作 authoritative memory；所有持久状态变化仍必须经过 deterministic state_ops / settlement-style application。

它继承 Planning Ontology、Navigation Policy、Detour / Look-back / Active Recall Policy 的边界：slow-cycle 可以在 chapter/session 边界整理 macro carry-forward、open obligations、detour continuity 与 mainline restoration rationale；但它不选择下一 unit，不重排整本书，不替代 `Navigate.choose_next_unit`，不打开未经 policy 授权的新 detour，不生成 visible route surface。

本页只设计：

```text
chapter/session boundary slow-cycle contract
memory consolidation
macro carry-forward
continuation capsule / re-entry packet
slow-cycle audit minimum
failure guardrails
与当前 attentional_v2 的职责收紧
```

本页不是：

```text
Memory Ontology 重写
Memory Formation / Management / Retrieval 重写
Planning / Navigation / Detour Policy 重写
Visible Reading Route Surface UX
Codex implementation roadmap
full Audit / Evaluation schema
new planner agent
new memory manager agent
vector DB / graph DB / Memory OS
prompt self-refinement / procedural memory
full book route optimizer
```

本设计的目标是让现有 `slow_cycle / chapter consolidation / reflective promotion / reconsolidation / carry-forward / knowledge activation update` 链路更清晰、更可靠、更可审计，同时保持 Simplicity and Universality。

------

### 2. Current Implementation Understanding

当前 repo 的默认机制是 `attentional_v2`，`iterator_v1` 是 fallback / legacy-compatible path。项目文档把 `attentional_v2` 明确列为 default/live mechanism，并且当前 shared source substrate 是 `public/book_document.json`；`attentional_v2` 使用 paragraph + char-offset cursor 与 inline paragraph-offset `SourceRef`，没有共享 Anchor Bank 或 SourceRef registry。

当前 live loop 是：

```text
survey / reading_plan orientation
  → Navigate.choose_next_unit
  → Read
  → Reading Runner post-read settlement
  → cursor advance / audit / unit_span_ledger
  → chapter/session slow-cycle
```

`Read` 的当前 contract 是 `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`；`Read.memory_uptake_ops` 只允许 target `active_attention / concept_registry / thread_trace`，不得写 `reflective_frames / reaction_records / audit`；`Read.detour_need` 只是 planning intent，不定位下一步路线。

`slow_cycle.py` 当前承担 Phase 6 slow-cycle reasoning、durable reaction truth 与 compatibility projection。它包含 surfaced reaction persistence、compatibility projection、reflective promotion、reconsolidation、chapter consolidation、active_attention cooling / carry-forward、promotion candidates、knowledge activation updates 与 cross-chapter carry-forward。

当前 surfaced reaction persistence 已经是 surfaced-native builder：`build_reaction_record_from_surfaced_reaction` 会把 `thought / source_quote / primary_source_ref / related_source_refs / prior_link / outside_link / search_intent / supersedes_reaction_id` 等字段持久化为 durable reaction history。 这支持本设计继续把 `reaction_records` 视为 visible trace，而不是 semantic memory。

当前 reflective promotion 是二段式：`chapter_consolidation` 只返回 `promotion_candidates`；随后 `reflective_promotion` 决定 `promote / withhold`，并通过 `apply_reflective_promotion` 写入 reflective frame。若需要替代旧 frame，代码调用 `supersede_reflective_item`，旧 statement 被标记为 `superseded` 并保留，不做 destructive overwrite。

当前 reconsolidation 也是 append-only：若 later reading materially changes earlier persisted reaction，`reconsolidation` 会创建 later reaction，并 append `reconsolidation_record`；旧 reaction 不被改写。

当前 chapter consolidation prompt 明确：chapter end 是 cool / sweep / prepare promotion 的机会，不是 false closure；不得直接 promote reflective summaries；carry-forward active item 必须复用 existing `item_id` 并保留 `source_refs`。 代码中的 `apply_cross_chapter_carry_forward` 已经按 `item_id` merge existing source refs 与 LLM 返回 source refs，防止 omitted source_refs 擦除证据。 相关测试也验证了 preserve、merge/dedupe、以及不为新 item invent refs。

当前 `state_ops.py` 是 deterministic apply layer。它对 `active_attention` 支持 create / update / reactivate / cool / close / resolve / link / drop，并 merge source refs；对 concept/thread，把 append/create/link 归一化为 update，把 close 归一化为 resolve；对 reflective frame，supersede 保留旧 statement。

当前 `state_projection.py` 构造 bounded `state_packet.v1`、`carry_forward_context`、`navigation_context` 与 `continuation_capsule`。它最多投影少量 active items、concept digest、thread digest、reflective digest、recent reactions、source_ref digest 与 rehydration entrypoints；这些是 prompt-facing projection，不是 authoritative state。

当前 `knowledge.py` 管理 knowledge activation lifecycle：只有 live 且带 warrant 的 `plausible / strong` activation 才会让 `knowledge_use_mode` 进入 `book_grounded_plus_prior_knowledge`；`cool / drop / supersede` 分别转为 `weak / dropped / rejected`。 这支持本设计继续把 `knowledge_activations` 定义为 warrant ledger，而不是 book-grounded concept truth。

当前 `runner.py` 在 chapter 完成后构造 chapter-end SourceRef，并调用 `run_phase6_chapter_cycle`，然后保存 active_attention、concept_registry、thread_trace、reflective_frames、knowledge_activations、reaction_records 与 continuation_capsule，并写 chapter checkpoint。 当前 session resume / checkpoint 体系存在，但 repo 中可确认的 slow-cycle 触发主要是 chapter boundary；session boundary slow-cycle 尚未作为同等显式 contract 定义。

当前 observability 有 `unitization_audit / read_audit / settlement_audit`。`read_audit` 记录 source span、carry-forward refs、supplemental context、reading impression、surfaced reactions、memory_uptake_ops、detour_need；`settlement_audit` 记录 compact transaction summary 与 active/concept/thread/reaction 的 ID deltas。 但 slow-cycle 自身还没有同等清晰的 event-level audit；per-candidate outcome、withheld_promotion reason、not_carried reason、projection impact、continuation_capsule_delta 仍需要收紧。

当前 runtime artifact evidence boundary：本设计读取了 GitHub docs、核心代码、测试和项目文档记录的诊断摘要；没有逐行审计真实运行目录中的 `read_audit.jsonl / settlement_audit.jsonl / active_attention.json / concept_registry.json / thread_trace.json / reflective_frames.json / reaction_records.json / knowledge_activations.json / reconsolidation_records.json / local_continuity.json / continuation_capsule.json`。因此本文只做 architecture-level、contract-level 与 assessment-level 设计判断，不声称已独立验证 runtime quality。

当前 gaps：

```text
memory consolidation vs macro carry-forward 边界不够显式；
candidate vs settled state 边界不够硬；
slow-cycle audit 不够阶段化；
not_carried / withhold / insufficient evidence 等 outcome 不够显式；
session boundary / re-entry slow-cycle 没有正式 contract；
detour continuity 在 chapter/session 边界的 cleanup / carry-forward 还不够显式；
runtime quality 仍需后续 Audit / Evaluation 验证。
```

------

### 3. Core Definitions

**Slow-cycle**
Slow-cycle 是在 chapter / session / boundary 发生的慢周期处理。它对已经 settled 的 reading memory 与 planning continuity 做 bounded review，提出 memory consolidation candidates 与 macro carry-forward candidates。它不是 per-unit reflection，不是 general planner，不是 memory manager agent，不是 prompt self-refinement，不是 full book route optimizer。

**Boundary event**
Boundary event 是阅读过程中的阶段边界，例如 chapter completed、session ended、run resume / re-entry、long detour completion、support/deferred chapter transition、active_attention overflow、promotion/reconsolidation threshold、knowledge activation status review。Boundary event 只提供触发条件，不自动授权写入。

**Memory consolidation**
Memory consolidation 是对 settled memory 的慢周期整理：cool、refresh、carry-forward、not_carried、promotion candidate、reflective promotion、reconsolidation、supersede candidate、knowledge activation update、source-ref-preserving support set update。它不重新定义 store identity，不直接消费 raw Read intent。

**Macro carry-forward**
Macro carry-forward 是 chapter/session 边界对下一阶段内部 focus 的选择：哪些 active_attention、concept、thread、reflective frame、reaction trace、knowledge activation、detour obligation、open question 应被带入下一阶段；哪些应 cool、resolve、not_carried、defer 或只保留 lineage。

**Macro-planning**
Macro-planning 是 reading boundary 层面的 attention scheduling 与 continuity preparation。它只回答“下一阶段阅读应保留哪些内部 focus / obligations / continuity notes”，不回答“下一 unit 读哪里”，不生成全书路线。

**Carry-forward focus**
Carry-forward focus 是进入下一 chapter/session 的 bounded internal focus packet。它可以来自 active_attention、重要 concept/thread、reflective digest、open detour obligation、knowledge activation warning 或 source_ref digest。它是 projection / planning support，不是新的 source truth。

**Open obligation**
Open obligation 是仍需下一阶段关注的 unresolved reading need，例如 active_attention 中未解决的问题、open detour、unresolved concept ambiguity、live thread development、source-ref recalibration need、knowledge activation warrant conflict。Open obligation 必须有 status、source_refs 或 warrant markers。

**Closed / resolved obligation**
Closed / resolved obligation 是当前 source-so-far 已足以暂时关闭的 obligation。Resolved 不等于 permanently complete；未来 source 可 reactivated。

**Promotion candidate**
Promotion candidate 是 slow-cycle 认为可能值得提升到 reflective_frames 的 candidate。它必须带 supporting_source_refs / promoted_from / rationale。它不是 settled memory。

**Reflective promotion**
Reflective promotion 是把 source-supported、durable enough、超出 local moment 的 understanding 写入 `reflective_frames` 的 boundary operation。它只能由 slow-cycle / boundary 正常写入。

**Reconsolidation**
Reconsolidation 是 later reading materially changes earlier visible reaction / thought 的 reinterpretation ledger。它写 `reconsolidation_records`，通常同时 append later reaction；它不是 reflective frame，不替代 semantic supersede。

**Chapter/session consolidation**
Chapter/session consolidation 是在 chapter/session boundary 上执行的 slow-cycle event。Chapter consolidation 主要基于当前 chapter source refs、meaning units、reaction records 与 memory snapshots；session consolidation 更偏 re-entry safety、stale focus control 与 continuation capsule refresh。

**Slow-cycle candidate**
Slow-cycle candidate 是 LLM 或 deterministic prefilter 提出的 boundary operation proposal。它不是 durable memory、不是 final state mutation、不是 evaluation score、不是 user-facing text。

**SlowCycleCandidateSet**
`SlowCycleCandidateSet` 是 LLM / deterministic prefilter 在 boundary event 上提出的候选集合。它只表达 proposed candidates，不产生 durable state mutation，不等于 settled memory，不是 prompt-facing projection。

**Slow-cycle settlement**
Slow-cycle settlement 是 deterministic runner / state_ops / settlement-style application 对 candidates 的 final application。它负责 legality、source_ref preservation、ID、status transition、failure outcome、audit delta 与 persistence。

**SlowCycleSettlementEvent**
`SlowCycleSettlementEvent` 是 deterministic application result envelope。它记录 accepted / rejected / withheld / failed / no_change outcomes，以及 source_ref preservation、state delta、failure reason 与 audit delta；它才是 durable mutation 的 settlement-facing事实。

**Continuation capsule**
Continuation capsule 是 resume / re-entry seed projection。它可包含 active_attention digest、concept/thread digest、reflective digest、source_ref digest、route trace summary、open obligations 与 warning markers。它不是 authoritative memory，原则上应可从 durable stores 重建。

**Slow-cycle audit**
Slow-cycle audit 是 diagnostic artifact。它记录 trigger、input packet、candidates、selected/rejected items、state deltas、source_refs used、failure reasons、projection impact、continuation capsule delta。它不进入 runtime prompt，不暴露 chain-of-thought，不等于 evaluation score。

**Route trace summary**
Route trace summary 是对 mainline / detour / defer / resolve / restore-mainline 等 planning continuity 的 compact audit/display-readiness summary。它不是 Visible Route Surface UX，也不创建 user route controls。

Route trace summary is produced for audit and future disclosure readiness only. It is not product copy and not visible route surface text.

**Not-carried decision**
Not-carried decision 是 slow-cycle 判定某 item 不进入下一阶段 carry-forward focus。它不等于 drop，不等于 semantic invalidation，不等于从 lineage 删除。它必须有 reason。

必须固定的排除项：

```text
slow-cycle is not per-unit reflection
slow-cycle is not general planner
slow-cycle is not memory manager agent
slow-cycle is not prompt self-refinement
slow-cycle is not full book route optimizer
slow-cycle candidate is not settled memory
slow-cycle summary is not source truth
```

------

### 4. Trigger and Timing Policy

Slow-cycle 有四类触发。

v0 先区分 MVP 与 extended trigger，防止 slow-cycle 被实现成频繁运行的 mini-manager。

```text
MVP slow-cycle triggers:
- chapter boundary
- lightweight session boundary / resume capsule refresh
- long detour completion
- support/deferred chapter transition

Extended / later triggers:
- high-density active_attention overflow
- reflective promotion threshold
- reconsolidation opportunity
- knowledge activation status review
```

Extended triggers must not run full chapter-like consolidation unless explicitly authorized. They may produce diagnostic/candidate review or bounded cleanup, but cannot inherit chapter-boundary authority by default.

#### 4.1 Normal scheduled slow-cycle

**chapter boundary**
当一个 chapter mainline 读完并完成 chapter-tail detour drain 后触发。这是当前实现最明确的 slow-cycle 触发点。它执行 chapter consolidation、active_attention cooling/carry-forward、knowledge activation review、promotion candidate review、reflective promotion、continuation capsule update。

**session boundary**
当用户/系统暂停、run ends mid-chapter、显式保存 session、或需要跨进程/跨天 resume 时触发 lightweight session consolidation。v0 session boundary 不应强行做 chapter-level reflective promotion；它主要做 continuation capsule refresh、active_attention stale marker、open obligations snapshot、detour continuity summary、warning markers。

Session boundary v0 should not promote reflective frames, supersede concepts/threads, or run broad consolidation by default. It may only refresh continuation capsule, snapshot open obligations, mark stale focus, preserve detour continuity summary, add warning markers, and write session-boundary audit.

**support / deferred chapter transition**
当 reading_queue_stage 从 mainline 转入 deferred_support，或 support chapter 读完回到 mainline queue 时触发 macro carry-forward review。它不重排 book route，只确认哪些 mainline focus 仍需保留，以及 support chapter 是否改变了 active/reflective/knowledge warrant status。

#### 4.2 Event-triggered slow-cycle

**long detour completion**
当一个 detour 经过多个 units 或 chapter-tail drain 后 resolved / abandoned / repeatedly deferred 时触发 bounded detour consolidation：resolve linked active item、记录 restore-mainline rationale、carry unresolved obligation 或 mark not_carried。

**high-density active_attention overflow**
当 active_attention 超过 projection/carry budget，触发 cooling/carry-forward selection。该触发不授权 reflective promotion，除非同时满足 promotion evidence threshold。

**reflective promotion threshold**
当多条 settled active/concept/thread/reaction evidence 支持同一 higher-order understanding，触发 promotion candidate review。Threshold 是 boundary-only，不在每个 unit 后做 reflection。

**reconsolidation opportunity**
当 later source / reaction materially changes earlier reaction interpretation，触发 reconsolidation review。它应保留 prior/new reaction linkage。

**knowledge activation status review**
当 source evidence strengthens / weakens / conflicts with prior activation，或 session/chapter boundary 需要刷新 use-policy mode，触发 knowledge activation review。

#### 4.3 Diagnostic-only slow-cycle

**evaluation / probe boundary**
Memory Quality / Callback / FVI / Planning-Memory Alignment probe 可读取 slow-cycle audit 或 snapshot，但不触发 runtime mutation。Evaluation probe boundary 只产生 diagnostic packets。

**audit failure boundary**
Audit failure 本身不应自动触发 state mutation。若出现 malformed output、missing SourceRef、state_ops failure、projection mismatch，可生成 diagnostic-only slow-cycle 或 manual repair candidate。

#### 4.4 Manual/admin repair review

Manual/admin repair 只用于 corrupted state、source_ref repair、schema migration、policy/compliance-required correction。它可以读取更宽 audit context，但不属于 normal slow-cycle，也不应进入 runtime prompt。

#### 4.5 Explicit non-triggers

以下不是 normal slow-cycle trigger：

```text
every unit
every surfaced reaction
every active recall
every look-back
every detour signal
ordinary curiosity
theme-only association
audit failure alone, unless routed to diagnostic/manual repair
```

------

### 5. Slow-cycle Input Contract

#### 5.1 Allowed inputs

Slow-cycle 可以读取：

```text
settled active_attention
settled concept_registry
settled thread_trace
reflective_frames
reaction_records
reconsolidation_records
knowledge_activations
current chapter/session source_refs
unit_span_ledger coverage facts
local_continuity / detour_trace summary
slow_cycle_consolidation retrieval results
deferred candidates as candidate evidence only
compact audit summaries, only if explicitly needed
continuation capsule
reading_queue_stage / chapter_ref / session_id
```

#### 5.2 Not allowed as authoritative memory

Slow-cycle 不得把以下内容当作 authoritative memory：

```text
raw Read.memory_uptake_ops
failed / skipped settlement ops
deferred candidates without re-admission
full audit dump
evaluation reports / judge prose
visible route surface text
raw hidden reasoning
future text
source corpus merely because it exists
```

#### 5.3 Input packet discipline

Slow-cycle input 必须遵守 packet discipline：

```text
1. candidate index packet first
   先给候选索引：item ids、statuses、source_ref counts、recentness、reason markers、store type。

2. expanded evidence packet only for selected candidates
   只对进入 review 的候选展开 source_refs、reaction snippets、thread/concept details。

3. no full-store prompt dump
   active/concept/thread/reaction/knowledge stores 不全量进入 prompt。

4. no full audit dump
   audit 只能作为 compact summary 或 failure marker 进入 diagnostic-only path。

5. SourceRef / status / warning markers must be preserved
   source_refs、resolution status、visibility/validity/warrant markers 不能在 prompt projection 中被剥离。

6. future text disallowed
   slow-cycle 只能使用 source-so-far 与 already-read / boundary-authorized source facts。
```

------

### 6. Slow-cycle Output Contract

Slow-cycle 输出分三层。

#### 6.1 Memory consolidation outputs

Slow-cycle 可以提出：

```text
active_attention:
  cooling candidate
  carry_forward candidate
  not_carried candidate
  resolved candidate
  reactivate candidate

concept_registry:
  refresh candidate
  source_ref merge candidate
  definition refinement candidate
  local ambiguity resolution candidate
  merge / supersede / retire / invalidate candidate

thread_trace:
  continuation candidate
  dormant / reactivate candidate
  merge / split candidate
  resolved_local_development candidate
  retire candidate
  cross-chapter carry-forward candidate

reflective_frames:
  promotion candidate
  withhold promotion
  update existing frame
  supersede old frame
  retire / invalidate candidate

reaction_records / reconsolidation_records:
  reconsolidation candidate
  later reaction candidate
  supersedes_reaction_id link
  change_kind classification

knowledge_activations:
  strengthen / weaken / reject / drop / reactivate candidate
  conflict_source_ref update
  use-policy mode review

support sets:
  source-ref-preserving support set update
  source_ref_recalibration candidate
```

#### 6.2 Macro carry-forward outputs

Slow-cycle 可以提出：

```text
next chapter/session focus
active_attention to carry
unresolved obligations
resolved obligations
abandoned / deferred detour cleanup
mainline restoration rationale
focus budget / continuity note
continuation capsule update
route trace summary for audit/display-readiness
```

这些 outputs 不等于 `Navigate.choose_next_unit`。Slow-cycle 不选择下一 source unit，不生成 route options，不重排全书。

#### 6.3 Audit-only outputs

Slow-cycle 可以输出 audit-only outcome：

```text
no_change
withheld_promotion
candidate_rejected
insufficient_source_evidence
overbroad_summary_rejected
reaction_only_evidence
knowledge_only_evidence
deferred_candidate_only
source_ref_missing
state_ops_application_failed
projection_impact summary
warning markers
```

#### 6.4 Authority rule

```text
LLM may propose candidates.
Deterministic runner / state_ops / settlement applies final state changes.
Slow-cycle output is not automatically durable memory.
Slow-cycle output is not user-facing product text.
Slow-cycle output is not evaluation score.
```

If current `slow_cycle.py` directly mutates any durable store, that behavior should be treated as current implementation fact, not final design authority. Implementation Handoff should route durable mutations through canonical `state_ops` / settlement-style wrappers where feasible.

------

### 7. Active Attention Carry-forward and Cooling

`active_attention` 是 near-term hot reading state，不承载 stable semantic truth。Slow-cycle 对它的主要职责是 visibility lifecycle 与 macro carry-forward，而不是 semantic validation。

#### 7.1 Legal slow-cycle statuses / markers

```text
hot
active
cooling
cooled
resolved
dormant
carried_forward
not_carried
reactivated
```

这些是 visibility / continuity markers，不是事实真伪判断。

#### 7.2 Carry-forward

当 active item 仍会拉动下一章/下一 session 阅读时，slow-cycle 应提出 `carry_forward`：

```text
复用 existing item_id；
保留 / merge / dedupe source_refs；
source_refs 不得因 LLM omitted field 被擦除；
保留 linked_concept_keys / linked_thread_keys when valid；
标记 carry_forward_reason；
进入 continuation capsule 的 active focus digest；
记录 carried_source_refs_used。
```

当前实现已经用 `item_id` merge existing source refs，这是应保留并收紧为 contract 的行为。

#### 7.3 Cooling

当 active item 不再是 near-term focus，但仍有历史/lineage 价值时，slow-cycle 可提出 `cool / cooling / cooled`：

```text
cool = visibility lifecycle
cool ≠ semantic invalidation
cool ≠ deletion
cool 不擦除 source_refs
cool 不关闭 concept/thread truth
```

Cooling 的典型 reason：

```text
resolved_by_current_source
no_longer_near_term
absorbed_by_reflective_frame
support_chapter_context_complete
lower_priority_due_to_focus_budget
```

#### 7.4 Resolved

`resolved` 表示当前 source-so-far 暂时关闭该 question / tension / focus。Resolved 不等于 permanently complete；后文可以 `reactivate`。

#### 7.5 Dormant / reactivated

当 item 不适合进入当前 prompt，但仍可能被 later source reactivated，可标记 dormant。后续 source 再次触发该 focus 时，slow-cycle 或 read-path settlement 可 reactivate。

#### 7.6 Not-carried

`not_carried` 表示 item 不进入下一阶段 internal focus。它不等于 drop，不等于 semantic invalidation，不等于 lineage 删除。必须记录：

```text
item_id
previous_status
not_carried_reason
source_refs retained
projection_impact
whether still recallable
```

当前实现用 `apply_cross_chapter_carry_forward` 替换 active_items；本设计要求在替换前形成 not_carried audit，避免 silent disappearance。

In v0, not_carried is audit / continuation-capsule marker by default, not a durable `active_attention` status, unless Implementation Handoff explicitly introduces it as a store marker.

#### 7.7 When to promote from active_attention

只有当 active_attention item 超出 near-term focus，且有 supporting source set / concept-thread support / repeated source pressure / reaction lineage 时，才可成为 reflective promotion candidate。单条 active item 不能直接变成 reflective truth。

#### 7.8 When to leave active only

当 issue 仍未解决、source pressure still current、且下一章/session 可能继续处理时，应 carry active，而不是过早 promote 或 cool。

#### 7.9 When not to cool

不得把 current-source unresolved issue 过早冷却。若 active item 明确 linked to current source dependency、open detour、unresolved concept ambiguity 或 next-session obligation，应 carry_forward 或 mark open obligation。

------

### 8. Concept / Thread Consolidation

#### 8.1 Concept registry

`concept_registry` 是 source-grounded concept / object / definition / model / classification / named distinction registry。Slow-cycle 可以提出：

```text
refresh
source_ref merge
definition refinement
local ambiguity resolution
concept-thread link
merge candidate
supersede candidate
retire candidate
invalidation candidate
```

Rules：

```text
concept 不变成 chapter summary bucket；
prior knowledge 不能写成 source truth；
definition refinement 必须保留旧 source_refs；
source_ref merge 只能 add/dedupe，不擦除；
supersede 不 destructive overwrite；
merge 必须基于 same source-grounded object，而不是主题相似；
invalidation 必须有 later source evidence 或 manual repair reason；
final mutation 仍走 deterministic state_ops / settlement-style application。
```

#### 8.2 Thread trace

`thread_trace` 是 cross-passage development line，不是 concept dictionary。Slow-cycle 可以提出：

```text
thread continuation
thread dormant
thread reactivate
thread merge
thread split
thread source sequence update
resolved_local_development
cross-chapter thread carry-forward
thread promotion candidate
retire candidate
```

Rules：

```text
thread 必须有 source sequence 或 future-pulling continuity；
theme-only association rejected；
merge/split 必须有 source evidence；
resolved_local_development 不等于整条 thread 永久完成；
thread dormant 不等于 false；
thread promotion 只能成为 reflective promotion candidate，不能直接写 frame；
all changes preserve SourceRef lineage。
```

------

### 9. Reflective Frames and Promotion

`reflective_frames` 是 slow-cycle promoted higher-order memory。它只能由 slow-cycle / boundary 正常写入。

#### 9.1 Promotion candidate sources

Promotion candidates 可以来自：

```text
settled active_attention items
concept_registry entries
thread_trace entries
persisted reaction_records
chapter source_refs
existing reflective_frames
reconsolidation_records
knowledge activation warrant as warning/support, not source truth
slow_cycle_consolidation retrieval results
```

#### 9.2 Minimum supporting evidence

Reflective promotion 至少需要：

```text
supporting_source_refs；
promoted_from；
chapter_ref / scope；
frame type / target_bucket；
confidence_band or status；
rationale；
projection impact estimate；
```

普通情况下，应有多条 source-backed lower-level signals。单条 source 可以支持 promotion 只在作者明确给出 stage model、core definition、chapter conclusion、named distinction、resolved question of record 等强 source structure 时成立。

#### 9.3 Frame types

合法 frame bucket 继承当前 implementation：

```text
chapter_understandings
book_level_frames
durable_definitions
stabilized_motifs
resolved_questions_of_record
chapter_end_notes
```

chapter_end_notes should be treated as audit/support/continuation note, not reflective truth by default. If stored in `reflective_frames` for compatibility, it must carry `note_only`, `supporting_source_refs`, and `not_current_truth` markers unless separately promoted by reflective promotion rules.

#### 9.4 Withhold conditions

必须 withhold promotion，当：

```text
source_refs missing
candidate overbroad
candidate is chapter summary dump
candidate depends only on reaction
candidate depends only on knowledge activation
candidate repeats prior frame without new evidence
candidate overrides current source evidence
candidate lacks stable scope
candidate belongs in concept/thread, not reflective frame
```

#### 9.5 Supersede / update

若新 frame 替代旧 frame：

```text
old frame remains immutable in statement；
old status = superseded；
old superseded_by_item_id set；
new frame carries supersedes relation or promotion rationale；
source_refs from old/new support sets preserved；
audit records why supersede happened。
```

#### 9.6 Relationship with stores

Reflective frame can summarize or stabilize concept/thread development, but it cannot override current source evidence. Reaction_records can provide evidence of reading trajectory, but not semantic truth by itself. Route trace summary can contextualize why a focus mattered, but not become frame evidence unless tied to source_refs.

------

### 10. Reaction Records and Reconsolidation

#### 10.1 Reaction records

`reaction_records` 是 append-only visible trace。Slow-cycle 可以读取它们作为 visible continuity / callback / promotion evidence candidate，但不能把 strong reaction 自动写入 concept/thread/reflective.

A reaction can become promotion evidence only when：

```text
it has primary_source_ref；
its source_quote is attributable；
it is supported by concept/thread/source evidence beyond mere feeling；
promotion candidate explicitly marks reaction as promoted_from evidence；
deterministic settlement applies final promotion。
```

#### 10.2 Surfaced reaction persistence

Current surfaced reaction persistence should remain:

```text
source_quote / primary_source_ref required
prior_link / outside_link / search_intent preserved as visible trace semantics
visible content must not leak internal handles
compatibility projection is not authoritative state
```

#### 10.3 Prior link / outside link / search intent

```text
prior_link:
  visible trace of callback relation; not semantic proof.

outside_link:
  visible trace of association; not source truth.

search_intent:
  visible follow-up curiosity; not actual search result, not navigation target.
```

#### 10.4 Reconsolidation event

Reconsolidation writes a reinterpretation ledger when later reading materially changes an earlier reaction. It should include:

```text
prior_reaction_id
new_reaction_id
supersedes_reaction_id on later reaction
change_kind
what_changed
rationale
later_source_ref
created_at
```

Reconsolidation does not equal reflective frame. If semantic memory changes, separate concept/thread/reflective supersede operation is required.

#### 10.5 Deletion / hiding

Reaction deletion or hiding should not automatically delete linked semantic memory. Visible trace policy is out of scope here and belongs to future visible surface / policy design.

------

### 11. Knowledge Activation Review

`knowledge_activations` 是 prior / external knowledge warrant ledger，不是 source truth。

#### 11.1 Status review

Slow-cycle 可以 review：

```text
weak
plausible
strong
rejected
dropped
```

Possible candidates：

```text
strengthen
weaken
reject
drop
reactivate
add_conflict_source_ref
update reading_warrant
update use-policy mode
```

#### 11.2 Evidence requirements

Knowledge activation change requires：

```text
source trigger；
current source evidence or conflict source ref；
reading warrant；
status marker；
warrant / conflict explanation。
```

Prior knowledge cannot become book-grounded concept truth without separate source-grounded concept op.

#### 11.3 Relation to concept/thread

A knowledge activation may inform interpretation only with warrant marker. If source text itself establishes a concept, write or update `concept_registry` via concept op; do not treat knowledge activation as concept_registry.

#### 11.4 Relation to detour / route trace

Knowledge activation cannot alone drive detour, macro carry-forward, or route trace. It may be a warning/support marker only when paired with current source trigger and source_scent.

#### 11.5 Use-policy mode

`change_use_policy_mode` / `refresh_knowledge_modes` is a gating result derived from activation statuses and warrants. It is not procedural memory, not prompt self-modification, and not a strategy update.

------

### 12. Detour Continuity and Macro Carry-forward

Slow-cycle may review detour continuity and propose cleanup / carry-forward. It must not choose next unit, replan the book, or override Navigation Policy.

#### 12.1 Open detour

For open detour, slow-cycle reviews:

```text
origin_cursor
origin_source_span_id if available
target_hint
reason
source_scent
detour_value
continuity_cost
budget / repeated defer risk
current status
linked active_attention item
```

Outcomes：

```text
carry as open obligation
defer with cooldown/audit marker
abandon with reason
resolve if later source made it unnecessary
convert to source_ref_recalibration candidate
```

New detour cannot be opened by slow-cycle unless policy-authorized source-grounded reason exists. Slow-cycle normally carries or cleans existing detour obligations.

#### 12.2 Resolved detour

Resolved detour should produce:

```text
resolved_obligation record
restore-mainline reason
linked active item resolve/cool candidate
source_refs used
detour_outcome summary
```

#### 12.3 Abandoned detour

Abandoned detour should preserve:

```text
abandon_reason
source_scent weak / budget exhausted / theme-only / continuity_cost high
not_carried marker if not entering next focus
repeated_defer_risk marker if relevant
```

Abandon does not delete route trace.

#### 12.4 Deferred detour

`defer_detour` is an act decision, not necessarily durable status. At slow-cycle boundary, repeated defer should be reviewed:

```text
if source_scent weak → abandon or not_carried;
if source_scent plausible but budget/session ended → carry as open obligation with warning;
if target_hint theme-only → reject as detour, preserve as visible curiosity only if later surface supports it.
```

#### 12.5 Mainline restoration rationale

Every detour boundary should have restore-mainline reason:

```text
resolved_current_uncertainty
detour_value_satisfied
detour_scent_weak
budget_exhausted
avoid_detour_lingering
mainline_continuity_restored
support_chapter_complete
```

#### 12.6 Macro carry-forward focus

Macro carry-forward focus contains:

```text
carried active_attention
unresolved concept/thread obligations
selected reflective digest
open detour obligations
knowledge activation warnings
source_ref digest
continuity note
focus budget
```

It does not contain next unit choice.

#### 12.7 local_continuity and continuation capsule

Final local_continuity mutation must be deterministic / settlement-style. Slow-cycle may propose `detour_continuity_changes`, but Runner settles them. Continuation capsule carries compact detour/open-obligation summary, not full detour audit.

------

### 13. Continuation Capsule and Re-entry

Continuation capsule is projection / resume seed, not authoritative memory.

#### 13.1 What goes in

```text
chapter_ref / session_id
active_attention carry-forward digest
concept digest
thread digest
reflective frame digest
source_ref digest
open obligation summary
detour / route trace summary
knowledge activation warning markers
recent visible reaction digest, clearly marked visible_trace
rehydration entrypoints
status markers
warning markers
```

#### 13.2 What must not go in

```text
full active_attention store
full concept/thread/reflective store
full reaction history
full audit dump
evaluation reports
raw memory_uptake_ops
failed settlement ops as memory
hidden reasoning
future text
prompt self-refinement / reader policy changes
visible route surface text
```

#### 13.3 Prompt bloat control

Continuation capsule should use fixed caps and entrypoints:

```text
active items: focus budget
concept/thread: digest only
source refs: small evidence spine
detour: summary only
warnings: compact markers
rehydration: entrypoints for retrieval, not full payload
```

#### 13.4 Resume handling

On session resume:

```text
rebuild capsule from durable stores where possible；
compare persisted capsule updated_at / chapter_ref / current cursor；
mark stale items；
do not mutate memory just because capsule is stale；
run diagnostic-only review if mismatch is severe；
allow active_recall / look_back to rehydrate when needed。
```

#### 13.5 Chapter transition

At chapter transition, capsule should reflect chapter-end slow-cycle settlement: carried items, not-carried markers, reflective digest, open obligations, restored mainline.

------

### 14. Slow-cycle Audit / Observability

This is not a full audit schema. v0 first uses an MVP subset before broader audit enrichment.

MVP SlowCycleAudit fields are:

```text
slow_cycle_event_id
trigger_type
chapter_ref / session_id
input_packet_summary
candidate_counts
items_selected
items_rejected
active_attention_changes
reflective_promotions
withheld_promotions
reconsolidation_events
knowledge_activation_changes
detour_continuity_changes
not_carried_items
source_refs_used
memory_refs_used
outcomes
failure_reasons
projection_impact
continuation_capsule_delta
```

Later / optional audit enrichment:

```text
full candidate counts by store
full items_considered list
unstable full thread/concept changes
full state_ops_application_summary
```

Broader minimum slow-cycle audit fields:

```text
slow_cycle_event_id
trigger_type
chapter_ref / session_id
reading_queue_stage
input_packet_summary
retrieval_intents_used
candidate_counts
items_considered
items_selected
items_rejected
active_attention_changes
concept_changes
thread_changes
reflective_candidates
reflective_promotions
withheld_promotions
reconsolidation_events
knowledge_activation_changes
detour_continuity_changes
carry_forward_focus
not_carried_items
source_refs_used
memory_refs_used
status_markers
warning_markers
outcomes
failure_reasons
projection_impact
continuation_capsule_delta
state_ops_application_summary
```

Rules：

```text
slow-cycle audit is diagnostic artifact；
does not enter runtime prompt；
does not expose chain-of-thought；
does not require full snapshot；
compact deltas preferred；
supports Memory Quality / Callback / FVI / Planning-Memory Alignment / Mainline Continuity / Detour Recovery；
is not evaluation score。
```

------

### 15. Slow-cycle Failure and Guardrails

| Failure / risk                         | Required handling                                            |
| -------------------------------------- | ------------------------------------------------------------ |
| insufficient source evidence           | withhold promotion; audit `insufficient_source_evidence`; keep candidate only if useful |
| overbroad promotion                    | reject / withhold; audit `overbroad_summary_rejected`        |
| source_refs missing                    | source_ref_recalibration candidate or withhold; no source-free reflection |
| stale memory only                      | lineage-only warning; not current truth; optionally look-back candidate |
| reaction-only evidence                 | audit-only or promotion candidate with warning; no automatic semantic write |
| knowledge-only evidence                | warrant marker only; no concept truth; no detour/carry-forward by itself |
| deferred candidate only                | candidate evidence only; must re-admit before write          |
| conflicting concept/thread             | defer to management review; no destructive overwrite         |
| detour unresolved but low source scent | abandon/defer/not_carried with reason; continue mainline     |
| too many active_attention items        | preserve current-source unresolved first; cool / not_carried lower-priority items with reason |
| prompt budget exceeded                 | use candidate index packet; expand only selected candidates; no full-store dump |
| slow-cycle LLM output malformed        | no_change; audit malformed; no silent mutation               |
| state_ops application failure          | no silent mutation; rollback/partial outcome only if deterministic; audit failure |
| runtime artifact unavailable           | diagnostic marker; no quality claim; preserve current state  |
| audit failure alone                    | diagnostic-only / manual repair; no automatic runtime mutation |

Global guardrails：

```text
when in doubt, withhold promotion
no source-free reflection
no destructive overwrite
no silent mutation
no prompt self-modification
no full book route replan
no raw audit dump in prompt
no automatic reaction-to-semantic promotion
no knowledge-only reflective truth
```

------

### 16. Interaction with Current Functions

**`slow_cycle.py`**
Boundary candidate orchestrator. It may run chapter/session consolidation, reflective promotion, reconsolidation, carry-forward review, knowledge activation review, and call settlement-style apply surfaces. It should not become a manager agent.

**`prompts.py`**
Constrains chapter/session consolidation prompts. The prompt should explicitly separate memory consolidation outputs from macro carry-forward outputs and require candidate/outcome markers.

**`state_ops.py`**
Applies canonical state operations and source-ref-preserving mutations. It should not receive raw ambiguous candidates; settlement pre-validation should make operation legality explicit.

**`state_projection.py`**
Provides bounded projections and continuation capsule. It should add status/warning markers where needed, but remain projection-only.

**`read_context.py`**
May supply `slow_cycle_consolidation` retrieval results under Retrieval design. It should not feed raw stores or audit dumps into slow-cycle.

**`knowledge.py`**
Manages knowledge activation lifecycle and use-policy mode. Slow-cycle may propose knowledge activation status changes; `knowledge.py` settles lifecycle within warrant rules.

**`runner.py`**
Triggers slow-cycle at chapter boundary and coordinates persistence. It should also be the natural home for future session-boundary trigger orchestration and continuation capsule refresh.

**`observability.py`**
Records slow-cycle audit and compact deltas. It should not turn audit into prompt context.

**`storage.py`**
Persists runtime artifacts in existing file-based JSON / JSONL territory. No new database is required.

**Evaluation**
Reads slow-cycle artifacts and snapshots; never mutates runtime state.

------

### 17. Compatibility with Prior Designs

This design remains compatible because it:

```text
does not redefine Memory Ontology；
does not redefine store identity；
does not let slow-cycle read raw Read intents as memory truth；
does not let deferred candidates directly become memory；
does not let reaction_records automatically become semantic memory；
does not let knowledge_activations become source truth；
does not let slow-cycle directly write final state without deterministic settlement；
does not create a memory manager agent；
does not create a general planner；
does not rewrite Navigation Policy；
does not rewrite Detour Policy；
does not design Visible Route Surface UX；
does not treat audit / evaluation artifacts as runtime context；
does not introduce vector DB / graph DB / Memory OS；
keeps SourceRef-first；
keeps candidate vs settled state separation；
keeps memory consolidation vs macro carry-forward separation；
keeps Simplicity and Universality。
```

------

### 18. Accepted Constraints and Deferred Directions

Accepted constraints:

```text
no per-unit reflection
  Reflection belongs to boundary slow-cycle.

no memory manager agent
  Lifecycle is a contract; settlement/state_ops apply.

no general planner
  Macro carry-forward is not next-unit selection or book route planning.

no full book route optimizer
  Survey/read plan remains structural orientation; Navigation owns local choice.

no prompt self-refinement
  Knowledge use-policy mode is gating, not procedural memory.

no procedural memory update
  Reader policy changes are out of scope.

no vector DB / graph DB
  Existing JSON/JSONL + SourceRef + metadata first.

no full audit dump
  Compact audit summaries only.

no source-free reflection
  Reflective frames require supporting source refs.

no destructive overwrite
  Supersede preserves old statements and lineage.

no automatic reaction-to-semantic promotion
  Reaction is visible trace.

no knowledge-only reflective truth
  Knowledge activation is warrant ledger.

no Visible Route Surface UX
  Only route trace summary for audit/display-readiness.

no Codex implementation roadmap
  This page defines contract, not tasks.
```

Deferred directions:

```text
full Memory Audit / Evaluation schema
full Planning Audit / Evaluation schema
Integrated Mechanism Design
Implementation Handoff
future Visible Reading Route Surface Boundary
optional deeper source_ref_recalibration flow
possible durable deferred-detour status, if Detour Policy later requires it
```

------

### 19. What This Design Changes or Tightens

#### 19.1 Preserved

```text
slow_cycle.py boundary role
file-based JSON / JSONL runtime artifacts
chapter_consolidation
reflective promotion
reconsolidation
knowledge activation updates
cross-chapter active_attention carry-forward
compatibility projection
continuation capsule
Runner-triggered chapter boundary cycle
```

#### 19.2 Tightened

```text
candidate vs settled state
memory consolidation vs macro carry-forward
active_attention carry_forward / cooling / not_carried semantics
SourceRef preservation as boundary contract
reflective promotion evidence threshold
reaction_records visible-trace boundary
knowledge activation warrant boundary
detour continuity cleanup at boundary
slow-cycle audit minimum
failure / withhold / reject outcomes
```

#### 19.3 Renamed or reinterpreted

```text
chapter_consolidation = boundary candidate generator, not final truth writer
cross_chapter_carry_forward = macro carry-forward candidate, settled by deterministic apply
chapter_summary_note = audit/support note, not source truth
optional_chapter_reaction = visible trace candidate, not reflective frame
promotion_candidates = candidates, not durable reflective memory
```

#### 19.4 Deferred

```text
Visible Route Surface UX
full evaluation rubric
full implementation handoff
new storage backend
planner agent
memory manager agent
prompt self-refinement
procedural strategy memory
```

------

### 20. Design Implications for Later Pages

**Memory Audit / Evaluation**
Must evaluate slow-cycle at operation/outcome level: withhold, promotion, source-ref preservation, not_carried, reconsolidation, knowledge warrant change, projection impact.

**Planning Audit / Evaluation**
Must evaluate macro continuity: open obligations preserved, detours resolved/abandoned honestly, mainline restoration rationale, repeated defer risk, planning-memory alignment.

**Integrated Mechanism Design**
Must specify exact orchestration sequence among Runner, slow_cycle, state_ops, state_projection, read_context, knowledge, observability.

**Implementation Handoff**
Should translate candidate/settled markers, audit fields, and source-ref preservation rules into schema/code changes only after Audit / Integrated design accepts field names.

**Future Visible Reading Route Surface Boundary**
May consume route trace summary, but cannot create route steering, accept/reject route controls, or navigation state transitions.

------

### 21. Implementation Readiness Notes

This is not a Codex task list.

#### 21.1 Ready for narrow implementation validation

```text
slow_cycle trigger_type logging
candidate vs settled markers
slow-cycle compact audit event
active_attention carry_forward reason
active_attention not_carried reason
withhold_promotion reason
reflective promotion evidence markers
supporting_source_refs / promoted_from markers
reconsolidation event reason markers
knowledge activation status review markers
detour continuity summary fields
restore-mainline reason marker
continuation_capsule_delta logging
source_refs_used / memory_refs_used
projection_impact summary
warning_markers
```

#### 21.2 Needs Audit / Evaluation design first

```text
full slow-cycle audit schema
Memory Quality scoring of slow-cycle outcomes
Planning-Memory Alignment metrics
Detour Recovery metrics
FVI diagnosis using reconsolidation / reaction lineage
```

#### 21.3 Needs Integrated Mechanism design first

```text
exact session-boundary orchestration
how slow_cycle_consolidation retrieval is invoked
how local_continuity mutation is settled at session boundary
how not_carried is retained when active_items are replaced
```

#### 21.4 Needs Implementation Handoff

```text
exact field names
schema migrations
backward compatibility behavior
test fixture plan
runtime artifact write locations
prompt updates
```

#### 21.5 Explicitly not now

```text
new planner agent
new memory manager agent
vector DB
graph DB
full book route optimizer
prompt self-refinement
procedural memory update
Visible Route Surface UX
full evaluation rubric
full implementation roadmap
```

------

### 22. Optional Open Questions

**Q1. Session boundary 是否应运行完整 chapter-like consolidation？**
现在不能完全解决，因为 current repo 显式 slow-cycle 主要是 chapter boundary；session boundary 需要 Integrated Mechanism 决定触发条件与最小 persistence shape。它不阻塞 chapter slow-cycle audit 收紧。

**Q2. `not_carried` 应存在于 active_attention store 还是只在 slow-cycle audit 中？**
v0 默认已经锁定为 audit / continuation-capsule marker，以避免 silent disappearance，同时不扩大 `active_attention` store status。后续仍可由 Audit / Implementation Handoff 决定是否新增 durable store marker；这是 durable-store placement question，不阻塞 v0 not_carried 可审计性。

**Q3. `deferred` detour 是否需要 durable status？**
Detour Policy 当前把 defer 作为 Navigate act decision，不一定作为 durable state。Slow-cycle 可先记录 repeated defer risk 与 abandon/defer reason；是否扩展 enum 依赖 Planning Audit / Detour Policy 后续收紧。

None of these are critical blockers for accepting this design phase.

------

## Appendix: Design Rationale and Evidence Basis

### A. Project Evidence Basis

本节说明项目事实如何支持正文设计。这里区分 current fact、stable constraint、runtime validation gap。

**Product overview / current-state / source-of-truth-map**
Product overview 把项目定义为 text-grounded、legible、self-propelled co-reading mind，而不是摘要器或服务式助手；这支持 slow-cycle 不做 generic planner、prompt self-refiner 或 user-profile memory。 Source-of-truth map 明确 repo-first authority，这支持继续使用 file-based JSON/JSONL 与 canonical docs / state files，而不是引入数据库优先。 Current-state 记录了 paragraph-offset cursor、SourceRef cutover、settlement diagnostic、source-ref carry-forward repair等当前事实；它支持正文把 SourceRef preservation 作为 slow-cycle contract，但该诊断摘要不是本轮逐行 runtime artifact audit。

**Shared source substrate and mechanism docs**
`backend-reading-mechanism.md` 明确 `book_document.json` 是唯一 shared parsed-book truth，paragraph layer 是稳定 source substrate，`attentional_v2` 使用 inline paragraph-offset SourceRef；这支持 `source corpus != memory` 与 `slow-cycle summary != source truth`。 `attentional_v2.md` 明确 current loop、Runner ownership、Read output、slow-cycle ownership与 current artifact territories；这支持本页不 greenfield、继续沿用 Navigate→Read→settlement→slow-cycle。

**`schemas.py`**
Schema 已定义 `StateOperationType`、`SourceRef`、`ActiveAttentionItem`、`LocalContinuityState`、`ContinuationCapsule`、`ReadUnitResult`、`DetourNeed`、`NavigateActTraceEntry`、`ReflectivePromotionCandidate/Result`、`ChapterConsolidationResult`、`KnowledgeActivation`、`ReactionRecordsState`、`ReconsolidationRecord` 等；这说明正文设计没有新建 store，而是收紧现有类型与输出 contract。

**`slow_cycle.py`**
Current slow-cycle 已有 durable reaction truth、compatibility projection、reflective promotion、reconsolidation、chapter consolidation、carry-forward、knowledge activation updates。`apply_cross_chapter_carry_forward` 保留 existing source_refs，是本设计 SourceRef preservation 规则的直接实现依据。

**`prompts.py`**
Read prompt 已经约束 `memory_uptake_ops` 只写 active/concept/thread，并禁止写 reflective/reaction/audit；chapter consolidation prompt 已经要求 chapter end cool/sweep/prepare promotion、promotion candidates、reuse `item_id`、preserve `source_refs`。本设计把这些 prompt-level rules 提升为 slow-cycle contract。

**`runner.py`**
Runner 已经是 deterministic orchestration owner：它处理 detour trace、mainline cursor、Navigate act loop、read settlement、memory op apply、reaction persistence、unit_span ledger、chapter-end `run_phase6_chapter_cycle`、checkpoint。正文把 slow-cycle settlement 归给 Runner/state_ops，是对当前实现的收紧而非替换。

**`state_ops.py`**
State ops 已经执行 source-ref-preserving merge、active_attention cooling/resolution、concept/thread update/resolve/drop、reaction/reconsolidation append-only、reflective supersede non-destructive。正文的 lifecycle guardrails 与 no destructive overwrite 来自这些 current facts 与上游 Management contract。

**`state_projection.py`**
Projection 已经 bounded，并提供 continuation capsule、active/concept/thread/reflective/reaction/source_ref digest、rehydration entrypoints。正文把 continuation capsule 定义为 projection / resume seed，来自该实现事实。

**`read_context.py`**
Current read_context 已区分 `look_back` 与 `active_recall`，并返回 source excerpts 或 settled memory refs。正文没有重写 Retrieval，而是继承其 slow-cycle-facing discipline。

**`source_spans.py`**
Source span helpers 定义 paragraph-offset `SourceCursor / SourceSpan / SourceRef`、source_ref quote resolution、fallback_unit_span、ambiguous_first_match、dedupe_source_refs。正文要求 SourceRef-first、resolution marker preservation、fallback not equal exact evidence，来自此实现。

**`source_skills.py`**
Book-local source skills 只提供 visible-to-mainline source evidence，并禁止 future scope by visibility rules。正文把 detour continuity review 保持为 source-grounded、no hidden search，来自该事实。

**`nodes.py`**
Nodes normalization 过滤 visible internal reference leak、normalize surfaced reactions、normalize state operations、normalize detour need；但 `_STATE_OPERATION_TYPES` 当前未列入 `resolve`，且 missing target_store 会默认 `active_attention`。正文把 candidate vs settled 与 audit marker 收紧，正是对这类 contract gap 的回应。

**`knowledge.py`**
Knowledge lifecycle 与 `knowledge_use_mode` gating 已存在；正文将 knowledge activation限定为 warrant ledger，不是 source truth。

**`observability.py` / `storage.py`**
Audit 与 runtime artifacts 已有 read/settlement/unitization streams、probe export、state JSON files。正文要求新增/收紧 slow-cycle audit compact event，不要求 full snapshot 或新数据库。

**`backend-reader-evaluation.md`**
Evaluation constitution 区分 runtime behavior、benchmark evidence、Memory Quality / Spontaneous Callback / False Visible Integration；这支持正文把 slow-cycle audit 作为 diagnostic artifact，不把 evaluation evidence 回流 runtime prompt。

**`test_attentional_v2_slow_cycle.py`**
Tests 覆盖 source_refs preservation、reaction native fields、reconsolidation append-only、reflective provenance 等；这些是 contract-level evidence，不是 full runtime-quality validation。

**`docs/history/decision-log.md` / `docs/tasks/registry.md`**
Decision log 记录项目长期选择 focus over maximal flexibility、runtime recovery 与 docs 分层；tasks registry 记录 `attentional_v2` structural rework 选择继续在现有 mechanism key 下演进、paragraph-offset SourceRef cutover、carry-forward source-ref repair、F4A 运行中 detour/optional surfaced semantics 尚未充分验证。这支持本设计“保留 attentional_v2、收紧 contract、不引入新 agent/DB、承认 runtime validation gap”。

------

### B. Upstream Design Basis

**C设计-设计路线**
本页是设计8，位于 Memory Management、Memory Retrieval、Detour / Look-back / Active Recall Policy 之后。设计路线把本页限定在 chapter/session boundary 的 consolidation、carry-forward、open obligations、detour cleanup、reflective promotion、reconsolidation、knowledge activation update，并把 Visible Route Surface、full Audit/Evaluation、Implementation Handoff 延后。

**C设计0 Shared Charter**
P0 提供本页最高约束：`LLM proposes; deterministic runner settles`；slow-cycle 同时涉及 memory consolidation 与 macro carry-forward；不得成为大 planner、memory manager agent、prompt self-refiner、full book route optimizer；source corpus / memory / planning state / audit / visible reaction / route disclosure / evaluation evidence 必须分开。正文几乎所有边界均由 P0 直接转化而来。

**C设计1 Memory Ontology**
Memory Ontology 定义 reading memory、source corpus、visible reaction、knowledge activation、audit/evaluation、prompt projection 的身份边界；也定义 active_attention、concept_registry、thread_trace、reflective_frames、reaction_records、knowledge_activations、reconsolidation_records 的 store identity。正文不重新定义 store identity，只设计 slow-cycle 如何读取、冷却、刷新、提升、carry forward 或审计这些 stores。

**C设计3 Memory Formation & Settlement**
Formation 定义 `Read.memory_uptake_ops` 是 bounded write intent，不是 final persisted object；read-path 只写 active/concept/thread；failed/skipped/deferred ops 不能成为 memory truth。正文的 input contract 明确禁止 slow-cycle 直接消费 raw Read intent 或 failed settlement op。

**C设计5 Memory Management & Evolution**
Management 是本页最重要上游：它区分 visibility lifecycle 与 semantic validity lifecycle；`cool ≠ invalidate`，`resolve ≠ permanently complete`，`supersede ≠ destructive overwrite`，`deferred candidate ≠ memory truth`；slow-cycle 可做 promotion/reconsolidation/carry-forward/supersede review，但 final mutation 必须经 deterministic state_ops/settlement。正文把这些 lifecycle contract 落到 boundary operations。

**C设计7 Memory Retrieval & Utilization**
Retrieval 定义 `slow_cycle_consolidation` intent、current_truth / lineage / visible trace / warrant retrieval、SourceRef-first、status-aware、bounded packet、不做 full store dump、不把 retrieval hit 当 utilization success。正文的 input packet discipline 与 failure rules 直接继承该约束。

**C设计2 Planning Ontology**
Planning Ontology 定义 Planning 是 source-grounded reading path planning / attention scheduling / navigation support；local_continuity 是 planning state v0；slow-cycle 同时涉及 memory consolidation 与 macro carry-forward；不得成为 general planner。正文据此把 macro-planning 定义为 boundary focus / obligation selection，而不是 next-unit planner。

**C设计4 Navigation Policy**
Navigation Policy 固定 `Navigate.choose_next_unit` 是 source-grounded next-unit selector / detour localizer；source-order mainline default；Navigation 不写 memory，不执行 full retrieval，不拥有 visible route surface；detour 结束需 restore-mainline reason。正文只让 slow-cycle review detour continuity与 restore rationale，不让它选择下一 unit。

**C设计6 Detour / Look-back / Active Recall Policy**
该设计区分 active_recall = memory recovery、look_back = source calibration、detour = planning path deviation；detour open/continue/defer/abandon/resolve/restore-mainline 有 policy constraints；Runner/local_continuity 才 settle final detour state effects。正文只定义 slow-cycle 如何在边界处理这些状态，不重写 detour policy。

**Memory Assessment**
Memory Assessment 诊断当前最大问题不是缺复杂基础设施，而是 contract-level semantics 不稳定；slow-cycle consolidation 必要但不能 per-unit reflection；不要引入 vector DB、graph DB、Memory OS、complex manager agent、full snapshot audit；audit 需要 per-op outcome / failure reason。正文的简化策略和 audit tightening 来自该评估。

**Planning Assessment**
Planning Assessment 认为当前 Planning/Navigation skeleton 合理，但 macro-planning 尚未正式定义；slow-cycle 既像 memory consolidation 又像 macro carry-forward，需要边界；不要引入 large planner、multi-agent team、ToT/LATS/MCTS default loop。正文将 Slow-cycle 分成两个 output planes，避免它滑向 general planner。

------

### C. External Rationale, as Filtered Through the Assessments

本阶段没有重新读取完整 External Evidence Pack；以下仅使用上游设计与评估已筛选过的外部来源。Evidence Pack 本身不作为外部依据引用。

**Generative Agents — observation → reflection boundary**
Generative Agents 使用 memory stream，并在累积 observations 达到 reflection trigger 后生成 higher-level reflections。它支持本设计“reflective_frames 只在 slow-cycle / boundary 正常写入，不做 per-unit reflection”。相似点是低层 observation 到高层 reflection 的提升；差异是 Generative Agents 面向社会模拟行为，不天然 source-ref-first。Reading Companion 只借 boundary-triggered reflection，不借其无 SourceRef 的自由反思。Support type: Analogical / Boundary.

**Reflexion — episode-boundary reflection**
Reflexion 把 verbal reflection 放在 episode 之间，用于失败后改进后续 trial。它支持本设计“失败/恢复/策略性诊断应在边界 audit 中处理，不进入内容 memory，也不做 prompt self-refinement”。差异是 Reflexion 目标是 agent trial learning，Reading Companion 目标是 source-grounded reading continuity。Support type: Analogical / Negative.

**LangGraph / LangMem — hot-path vs background memory**
LangGraph / LangMem 把 hot-path write、background consolidation、semantic/episodic/procedural memory 分开。它支持本设计将 Read-path formation 与 slow-cycle boundary consolidation 分离，并拒绝把 prompt refinement/procedural memory混入本页。差异是框架通用 agent memory，Reading Companion 是书本 source-grounded memory。Support type: Direct for timing pattern; Boundary for procedural memory.

**Mem0 — operation-centric update/delete**
Mem0 的 add/search/update/delete operation framing 支持本设计把 slow-cycle outputs 作为 candidates and canonical ops，而不是 LLM final state objects。相似点是 memory update需要 ID、metadata、operation outcome；差异是 Mem0 偏 production chat agent memory，Reading Companion 当前不需要 vector/graph infra。Support type: Direct for operation contract; Negative for infra-first adoption.

**Zep — temporal validity / invalidation**
Zep 的 temporal facts、invalidated facts、episodes/observations分层支持本设计的 supersede / invalidation / warrant lineage：旧理解保留 lineage，不 silent overwrite。差异是 Zep 是 temporal knowledge graph；Reading Companion 用 JSON stores + SourceRefs 表达 lineage。Support type: Direct / Analogical.

**MemoryBank — forgetting / reinforcement analogy**
MemoryBank 的 forgetting/reinforcement 支持 visibility decay、refresh、reactivation 的类比；本设计明确 `cool ≠ invalidate`。差异是 MemoryBank 面向 user-centric companion/personality memory，这部分对 Reading Companion 是负迁移。Support type: Analogical / Negative.

**LongMemEval — stage-aware diagnosis**
LongMemEval 拆分长期 memory 的阶段能力，支持本设计将 slow-cycle audit 与 evaluation分开，并要求 candidate outcome / utilization / failure reason，而不是只看最终表现。差异是 LongMemEval 面向 chat memory benchmark，Reading Companion 需要 source-grounded reading-specific metrics。Support type: Background / Direct for stage separation.

**HaluMem — memory pollution / operation hallucination**
HaluMem 强调 memory systems 在 extraction/update/QA 中都可能 hallucinate，支持本设计对 reaction-only、knowledge-only、source-free promotion、malformed output 的 guardrails。差异是 benchmark 新且场景更泛；本设计只借 pollution diagnosis principle。Support type: Negative / Boundary.

**GraphRAG / RAPTOR — multi-granularity summary**
GraphRAG / RAPTOR 支持“高层 frame 有价值”的背景，但它们是 corpus indexing / summarization stack。Reading Companion 只借 multi-granularity idea，不引入 graph/tree infra，也不把 chapter summary dump 当 reflective truth。Support type: Background / Negative.

**HTN / Options / MAXQ — temporal abstraction**
HTN、Options、MAXQ 支持 micro / meso / macro 分层与 temporally extended option 的类比。本设计把 chapter/session boundary 视为 macro abstraction，把 detour视为 bounded temporally extended deviation。差异是这些理论不是 LLM reading mechanism，不直接提供 source-grounding rules。Support type: Analogical.

**Information Foraging — value / cost / scent**
Information Foraging 支持 detour boundary 的 source_scent / detour_value / continuity_cost vocabulary。本设计在 slow-cycle 只用这些作为 qualitative audit markers，不做 ranking model。Support type: Direct analogy for navigation/carry-forward.

**ReAct / ReWOO — bounded evidence loop**
ReAct / ReWOO 支持局部 evidence loop 与 tool observation separation，但也提醒不要把每个 reading step 变成 agentic tool loop。本设计把 source skills / detour evidence 保持为 bounded support，不让 slow-cycle成为 tool/planner loop。Support type: Analogical / Negative.

**OpenAI Agents SDK / LangGraph trace docs — trace / guardrail / audit analogy**
官方 agent trace/guardrail docs 支持 structured trace、handoff、guardrail、diagnostic separation。本设计借审计/trace思想，不迁移为多-agent runtime。Support type: Background / Boundary.

------

### D. Simplicity and Universality Check

本设计符合 Simplicity and Universality：

```text
优先收紧现有 slow_cycle / state_ops / projection / audit；
不新增 planner agent；
不新增 memory manager agent；
不引入 vector DB / graph DB / Memory OS；
不做 per-unit reflection；
不做 prompt self-refinement；
保持 SourceRef-first；
区分 candidate / settled state；
区分 memory consolidation / macro carry-forward；
避免 reaction_records 语义化；
避免 knowledge_activations source-truth 化；
避免 audit trace 回流 prompt；
支持后续 Audit / Evaluation / Implementation，但不过早替它们设计；
保持 file-based JSON / JSONL first；
保留现有 attentional_v2 mechanism identity。
```

仍存在的复杂化风险：

```text
session boundary 若设计过宽，可能变成 per-pause manager；
promotion threshold 若不硬，可能变成 chapter summary dump；
route trace summary 若被提前产品化，可能滑向 Visible Route Surface UX；
knowledge activation review 若不带 warrant marker，可能污染 concept truth；
not_carried 若不审计，可能变成 silent memory loss；
audit fields 若过多，可能退化为 full snapshot dump。
```

本设计通过 withhold、candidate index packet、compact audit、SourceRef preservation、no full prompt dump 等规则控制这些风险。

------

### E. Source Usage List

| External source                                              | Authors / Organization                          | Year      | Stable URL                                                   | Used for                                                     | Support type          |
| ------------------------------------------------------------ | ----------------------------------------------- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------- |
| Generative Agents: Interactive Simulacra of Human Behavior   | Joon Sung Park et al.                           | 2023      | https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/ | observation → reflection；boundary promotion analogy         | Analogical / Boundary |
| Reflexion: Language Agents with Verbal Reinforcement Learning | Noah Shinn et al.                               | 2023      | https://arxiv.org/abs/2303.11366                             | episode-boundary reflection；failure learning as boundary evidence | Analogical / Negative |
| LangGraph Memory Concepts                                    | LangChain                                       | 2024–2026 | https://docs.langchain.com/oss/python/concepts/memory        | hot-path vs background memory；semantic/episodic/procedural separation | Direct / Boundary     |
| LangMem                                                      | LangChain                                       | 2025–2026 | https://github.com/langchain-ai/langmem                      | background consolidation and prompt refinement boundary      | Boundary / Negative   |
| Mem0 Docs / Memory Operations                                | Mem0                                            | 2025–2026 | https://docs.mem0.ai/core-concepts/memory-operations/add     | operation-centric add/update/delete; candidate vs applied op | Direct                |
| Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | Prateek Chhikara et al.                         | 2025      | https://arxiv.org/abs/2504.19413                             | production memory operation framing; metadata/update/delete  | Background / Direct   |
| Zep: A Temporal Knowledge Graph Architecture for Agent Memory | Preston Rasmussen et al.                        | 2025      | https://arxiv.org/abs/2501.13956                             | temporal validity; invalidation; evidence-backed facts       | Direct / Analogical   |
| Zep Graph / Facts / Observations Docs                        | Zep                                             | 2025–2026 | https://help.getzep.com/graph-overview                       | episodes/facts/entities/observations separation              | Direct / Boundary     |
| MemoryBank                                                   | Wanjun Zhong et al.                             | 2024      | https://ojs.aaai.org/index.php/AAAI/article/view/29946       | forgetting/reinforcement as visibility decay analogy         | Analogical / Negative |
| LongMemEval                                                  | Di Wu et al.                                    | 2024      | https://arxiv.org/abs/2410.10813                             | stage-aware memory diagnosis                                 | Direct / Background   |
| HaluMem                                                      | Ding Chen et al.                                | 2025      | https://arxiv.org/abs/2511.03506                             | memory pollution and operation hallucination risks           | Negative / Boundary   |
| RAPTOR                                                       | Parth Sarthi et al.                             | 2024      | https://arxiv.org/abs/2401.18059                             | multi-granularity summary as boundary-only inspiration       | Background / Negative |
| GraphRAG                                                     | Darren Edge et al. / Microsoft Research         | 2024      | https://arxiv.org/abs/2404.16130                             | global summary / multi-granularity caution                   | Background / Negative |
| HTN Planning                                                 | Kutluhan Erol                                   | 1996      | http://hdl.handle.net/1903/5810                              | macro/micro abstraction analogy                              | Analogical            |
| Options Framework                                            | Richard S. Sutton, Doina Precup, Satinder Singh | 1999      | https://doi.org/10.1016/S0004-3702(99)00052-1                | temporally extended option / detour analogy                  | Analogical            |
| MAXQ                                                         | Thomas G. Dietterich                            | 2000      | https://doi.org/10.1613/jair.639                             | controller-worker separation analogy                         | Analogical            |
| Information Foraging                                         | Peter Pirolli, Stuart K. Card                   | 1999      | https://doi.org/10.1037/0033-295X.106.4.643                  | source_scent / value / continuity cost vocabulary            | Analogical / Direct   |
| ReAct                                                        | Shunyu Yao et al.                               | 2022      | https://arxiv.org/abs/2210.03629                             | bounded evidence/action loop analogy                         | Analogical            |
| ReWOO                                                        | Binfeng Xu et al.                               | 2023      | https://arxiv.org/abs/2305.18323                             | decoupled reasoning/evidence loop; detour boundary caution   | Analogical / Negative |
| OpenAI Agents SDK docs                                       | OpenAI                                          | 2025–2026 | https://developers.openai.com/api/docs/guides/agents         | trace / guardrail / handoff analogy                          | Background / Boundary |
| LangGraph overview / durable execution                       | LangChain                                       | 2024–2026 | https://docs.langchain.com/oss/javascript/langgraph/overview | checkpoint / trace / durable execution analogy               | Background / Boundary |
