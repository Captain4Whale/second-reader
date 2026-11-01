# Detour / Look-back / Active Recall Policy Design v0

## 1. Scope and Purpose

本设计定义 Reading Companion / Second Reader 的 **Detour / Look-back / Active Recall Policy v0**。

它继承 P0 Shared Charter 的核心边界：Memory 与 Planning 共同服务一个 source-grounded co-reading mind；运行原则是 **LLM proposes; deterministic runner settles**；source corpus、reading memory、planning state、audit trace、visible reaction、visible route disclosure、evaluation evidence 必须分开。

它继承 Planning Ontology：Planning 是 source-grounded reading path planning / attention scheduling / navigation support；`local_continuity` 是 Planning state v0；`mainline_cursor` 是 source-order mainline restore point；`active_detour_need` 是 open planning obligation；`detour_trace` 是 lightweight path-deviation continuity record。

它继承 Navigation Policy：`Navigate.choose_next_unit` 是 source-grounded next-unit selector / active-detour localizer；默认 source-order mainline；detour 是 bounded exception；Navigate 的 live act space 仍只有：

```text
choose_unit
request_skill
defer_detour
```

本页补 Navigation Policy 故意延后的问题：什么时候 active recall，什么时候 look-back，什么时候 open / continue / defer / abandon / resolve detour，如何预算，如何退出，如何恢复主线，如何审计。

它兼容 Memory Ontology、Formation & Settlement、Management & Evolution：active recall 只能恢复 memory state；look-back 只能校准 source evidence；detour 只能控制 reading path；三者都不能改变 memory formation contract。

本页不是完整 Memory Retrieval / Utilization 设计，不定义 vector / graph retrieval，不定义 visible route surface object，不写 Planning Audit full schema，不写 Evaluation rubric，不写 Codex implementation roadmap，不新增 planner node，不新增 memory manager agent。

------

## 2. Current Implementation Understanding

当前 repo 的默认 live mechanism 是 `attentional_v2`；`iterator_v1` 保留为 explicit fallback / legacy-compatible path。机制目录将 `attentional_v2` 标为 current default/live mechanism，artifact root 是 `_mechanisms/attentional_v2/`。

共享 source substrate 是 `public/book_document.json`，它是唯一 shared parsed-book truth；当前 `attentional_v2` mainline 使用 paragraph + char-offset cursor，source citations 使用 inline paragraph-offset `SourceRef`，没有 shared Anchor Bank 或 SourceRef registry。

当前 live loop 是：

```text
survey / reading_plan orientation
  → Navigate.choose_next_unit
  → Read
  → Reading Runner post-read settlement
  → cursor advance / unit span ledger / audit
  → chapter/session slow-cycle
```

`Reading Runner` 是机制内部 read-progress executor，负责 `Navigate.choose_next_unit`、`Read`、post-read settlement、cursor advancement、detour state handoff 与 mechanism-private runtime persistence。

### 2.1 `Read.detour_need`

当前 `ReadUnitResult` 包含：

```text
reading_impression
surfaced_reactions[]
memory_uptake_ops[]
detour_need?
```

`DetourNeed` schema 只有：

```text
reason
target_hint
status
```

其中 `status` 当前 vocabulary 是：

```text
open
resolved
abandoned
```

这些字段已经足够表达一个最小 planning intent，但不足以表达本页需要的完整 detour audit，例如 source_scent、detour_value、continuity_cost、budget、restore_reason。后者应先作为 policy / audit fields，而不是立即要求 schema 扩张。

Read prompt 也已经明确：Read 可以 emit `detour_need`，但不能 secretly route or resolve it；如果正在 active detour 中，Read 可以将 `detour_need.status` 设为 `resolved` 或 `abandoned`，但最终 state effect 仍由 Runner settle。

### 2.2 `LocalContinuityState`

当前 `LocalContinuityState` 已包含：

```text
mainline_cursor
reading_queue_stage
active_detour_id
active_detour_need
detour_trace
```

`DetourTraceEntry` 当前包含：

```text
detour_id
origin_cursor
origin_target_hint
status
```

Runner 的 `_apply_detour_need` 在 `open` 时从 `mainline_cursor` 记录 origin cursor，生成 detour id，append `detour_trace`，并设置 `active_detour_id / active_detour_need`；在 `resolved / abandoned` 时更新当前 active detour trace，并同步 active detour pointer。

当前 gap 是：trace 记录了 open / resolved / abandoned，但缺少 structured `opened_by`、origin source span、defer reason、abandon reason、resolve reason、restore-mainline reason、budget state 与 source evidence used。

### 2.3 `NavigateActResult` and `NavigateActTraceEntry`

当前 `NavigateActDecision` 只有：

```text
choose_unit
request_skill
defer_detour
```

`NavigateActTraceEntry` 已经能记录：

```text
decision
selection_mode
reason
end_anchor_text
source_span_id
resolution
skill_request
skill_result
error
budget_state
```

这说明 trace surface 已经存在，但 policy reason、support flags、restore-mainline reason、retrieval utilization trace 仍需要收紧。

Navigation prompt 当前要求：mainline mode 必须从 provided mainline preview 直接 choose；不能 request skills，不能 defer。Detour mode 可以 choose source-grounded already-read unit、request one source skill if evidence insufficient、或 honest defer。Skill results are evidence, not answers；不允许 external web search，不允许选择 beyond `mainline_cursor` 的 future text。

### 2.4 `read_context.py`: active recall and look-back

`read_context.py` 已有两个 supplemental-context helper：

```text
look_back:
  根据 SourceRef / SourceSpan 回到 earlier source excerpt。

active_recall:
  从 concept_registry / thread_trace / reaction_records 中取回尚未 carry 的 reading state。
```

`look_back` 返回 source refs、earlier excerpts 与 supporting refs；`active_recall` 返回 concepts、threads、recent reactions 与 refs，并且会避免重复返回已在 carry-forward digest 中的 concept/thread。

当前实现正确地区分了两个方向，但 policy 仍不够明确：什么时候触发、什么时候停止、什么时候失败后恢复主线、什么时候升级为 detour、以及取回内容到底用于什么。

### 2.5 Source skills

当前 book-local source skills 是：

```text
source_map_overview
source_scope_drilldown
source_window_fetch
```

Skill runtime 只接受这些 known skills，并在 result provenance 中标记 source = `book_substrate`、bounded_by_mainline_cursor = true。

`source_skills.py` 的 visibility rule 很重要：earlier chapters 可见，future chapters 不可见，current chapter 只允许 mainline cursor 之前的 sentences。range 不在 visible scope 内会返回 `range_outside_visible_scope`。

这支持本页的 detour policy：source skill 是 book-local evidence provider，不是 hidden search engine，不做 semantic relevance judgment，不写 memory，不生成 route-disclosure output。

### 2.6 Source spans and SourceRefs

`source_spans.py` 定义：

```text
SourceCursor:
  chapter_id
  chapter_ref
  paragraph_index
  char_offset

SourceSpan:
  end-exclusive [start_cursor, end_cursor)

SourceRef:
  inline paragraph-offset source citation
```

`resolve_end_anchor_text` 以 exact-text 解析 `Navigate` 返回的 `end_anchor_text`；`source_ref_from_unit` 将 unit-local quote 解析成 inline paragraph-offset SourceRef，并在失败时记录 `fallback_unit_span / quote_not_found` 等 resolution marker。

这意味着 look-back 与 memory recall 都必须保留 source_ref boundary：memory projection 不能替代 source evidence；source evidence 不能被当作 hidden reading unit，除非 detour policy 正式升级为 detour unit。

### 2.7 State projection

`state_projection.py` 构造 bounded prompt-facing packet，包括：

```text
active_attention_digest
concept_digest
thread_digest
reflective_digest
recent_reactions
source_ref_digest
continuation_capsule
refs
```

`build_navigation_context` 把这些投影给 Navigate；`build_read_prompt_packet` 把 carry-forward 和 supplemental context 变成 Read prompt 的 narrow view。Projection 是 prompt-facing view，不是 authoritative durable state。

### 2.8 Observability

当前 observability 已有：

```text
unitization_audit.jsonl
read_audit.jsonl
settlement_audit.jsonl
```

`record_read` 记录 source span、carry_forward_ref_ids、context_request、supplemental_ref_ids、supplemental_steps、stop_reason、budget_exhausted、reading_impression、surfaced_reactions、memory_uptake_ops、detour_need。`record_settlement` 记录 memory op counts、target-store distribution、active_attention / concept_registry / thread_trace / reaction_records 的 compact deltas。

当前 gap 是：active recall / look-back / detour 的 policy-level utilization trace 还不足；例如取回了什么、用了什么、为什么没用、budget 为什么停止、restore-mainline 为什么发生，还没有形成最小统一 contract。

### 2.9 Runtime artifact boundary

`storage.py` 定义了机制私有 runtime artifacts：`local_continuity.json`、`active_attention.json`、`concept_registry.json`、`thread_trace.json`、`reflective_frames.json`、`knowledge_activations.json`、`reaction_records.json`、`unit_span_ledger.jsonl`、`read_audit.jsonl`、`settlement_audit.jsonl` 等。

本设计读取了 GitHub 文档与核心代码，也读取了 `current-state.md` 中记录的诊断摘要；但本轮没有逐行打开真实运行目录中的 runtime JSON / JSONL rows。因此本文不声称已经独立验证 runtime quality，只做 architecture-level、contract-level 与 assessment-level policy design。`current-state.md` 记录过 settlement-audit diagnostic：59 条 read-audit / settlement-audit、31 个 memory ops、SourceRef carry-forward repair等，这些是 repo-recorded diagnostic evidence，不等同于本轮独立 runtime artifact audit。

------

## 3. Core Definitions

```text
active_recall = memory recovery
look_back = source calibration
detour = planning path deviation
```

### Active recall

**Active recall** 是 memory recovery move。它从已经形成并 settle 的 reading memory 中，取回当前 reading / navigation 需要但未被 carry-forward packet 带入的 bounded memory state。

它回答：

```text
之前我们怎么理解它？
这条 thread / concept / reaction 之前在 reading memory 中是什么状态？
```

它不是 source verification，不是 source reread，不是 detour，不写 memory，不改变 cursor，不生成 route-disclosure output。

### Look-back

**Look-back** 是 source calibration move。它根据 SourceRef / SourceSpan 回到 earlier source excerpt，校准原文到底怎么说。

它回答：

```text
原文到底怎么说？
这个 earlier definition / distinction / callback 的 source evidence 是什么？
```

它不是 semantic memory recall，不自动改变 reading path，不自动写 memory，不自动生成 route-disclosure output。

### Detour

**Detour** 是 planning path deviation。它表示当前下一步阅读路径应暂时离开 source-order mainline，去读一个 source-grounded、bounded、allowed 的非主线 source unit。

它回答：

```text
下一步应该临时离开主线读哪里？
```

Detour 不是 hidden supplemental fetch。一旦 detour unit 被选中，必须走同一个：

```text
Navigate.choose_next_unit
  → Read
  → Runner settlement
```

loop。

### Source calibration

**Source calibration** 是把当前理解、memory projection、callback 或 claim 与 source text 重新对齐。其核心输出是 source excerpt / SourceRef / calibration result。

### Memory recovery

**Memory recovery** 是把已经 settle 的 reading memory 重新带回当前上下文，帮助继续理解或保持 continuity。其核心输出是 memory refs、compact summaries、source_refs、status markers。

### Path deviation

**Path deviation** 是从 source-order mainline 临时偏离。它必须有 origin、reason、target hint、budget、exit condition 与 restore plan。

### Detour need

**Detour need** 是 Read 或后续 policy-authorized surface 提出的 planning intent。它说明“当前阅读可能需要离开主线”，但不是 detour target，不是 source evidence，不是 route-disclosure output。

### Detour candidate

**Detour candidate / `detour_candidate`** 是 source-grounded path-deviation possibility。它不是 `active_detour_need`，也不是 durable detour state。它可以由 active recall、look-back、source skill result 或 Read 暴露，但不改变 cursor 或 `local_continuity`；必须经过 policy / Runner settlement admission 后，才可能打开 active detour。

### Detour localization

**Detour localization** 是 active detour mode 下，Navigate 使用 `target_hint` 与 book-local source evidence 定位一个 allowed detour unit 的过程。

`target_hint` 是 hint，不是 target。

### Detour resolution

**Detour resolution** 是 detour obligation 已经完成其功能：澄清、回答、拒绝、或使原问题不再需要路径偏离。

### Detour abandonment

**Detour abandonment** 是 detour 被判断不再值得追：没有 valid target、source scent repeatedly weak、预算耗尽且无恢复价值、或继续会损害 mainline continuity。

### Detour defer

**Detour defer** 是一次 Navigate act decision，表示“当前不继续这个 detour localization attempt”。它不是 durable status，不等于 abandon。

### Mainline restoration

**Mainline restoration** 是 Runner / local_continuity settlement effect：在 detour resolve / abandon / defer 后，把 path-control state 恢复到 `mainline_cursor` 或当前 mainline restore point。

它不是 Navigate output。

### Recovery budget

**Recovery budget** 是 active recall、look-back、detour、source skill 在一次 reading decision window 中可使用的 bounded effort。它包括 act count、source window count、retrieved item count、detour unit count、连续尝试次数与 chapter/session boundary。

### Source scent

**Source scent** 是 detour / look-back 可定位 source evidence 的强度。它不是“主题相关性”，而是：

```text
有 SourceRef / SourceSpan / already-read source card / visible source window
能支持一个明确 source-locus question
```

### Continuity cost

**Continuity cost** 是偏离主线造成的阅读连续性代价，包括打断当前 source move、增加恢复负担、造成 detour lingering、或降低用户可见阅读节奏。

Qualitative markers for policy/audit:

```text
source_scent: none / weak / plausible / strong
detour_value: low / medium / high
continuity_cost: low / medium / high
```

These are audit-facing qualitative markers, not numerical scores or a ranking model.

### Retrieval / use trace

**Retrieval / use trace** 是记录取回了什么、哪些被实际使用、用于什么、哪些未使用以及为什么未使用的 diagnostic trace。它不是 chain-of-thought，不进入 prompt。

### Support flag

**Support flag** 是 Navigate / Read / policy surface 标记“可能需要 active recall / look-back / detour support”的信号。它不是 operational trigger。

### Operational trigger

**Operational trigger** 是经过本页 policy 判定后，允许实际执行 active recall、look-back 或 open / continue detour 的条件集合。

### Audit-only signal

**Audit-only signal** 是记录给 observability / evaluation 的迹象；它不改变路径，不触发 retrieval，不写 memory。

------

## 4. Relationship Between the Three Mechanisms

三者协作的最小判断语言是：

| 问题                             | 机制          |
| -------------------------------- | ------------- |
| “之前我们怎么理解它？”           | active recall |
| “原文到底怎么说？”               | look-back     |
| “下一步应该临时离开主线读哪里？” | detour        |

当当前理解缺的是 **memory state**，使用 active recall。比如当前 unit 重新激活了早先的 concept/thread，但 carry-forward packet 没带足；或者当前 visible callback 需要知道之前的 reading state。

当当前理解缺的是 **source evidence**，使用 look-back。比如 current source 与 memory summary 冲突；概念定义需要早先原文校准；FVI 风险出现；memory projection 可能 stale。

当当前下一步阅读路径需要 **离开 mainline**，使用 detour。比如当前 unit 打开一个 unresolved source dependency，继续主线会显著削弱理解，而已有 target_hint 和 source_scent 支持一个 bounded non-mainline unit。

Look-back 通常只是 source excerpt support，不改变 path。当它返回的 excerpt 足以校准当前理解时，mainline 继续。只有当 source excerpt 不足以解决问题，且需要正式读取一个 bounded source unit 时，才可能升级为 detour。

Active recall 通常只是 Read support，不改变 path。当它恢复足够 memory state 后，mainline 继续。只有当 active recall 暴露出“这个 memory item 的 source evidence 必须重新校准”时，才转向 look-back；只有当它暴露出“下一步必须读某个 source locus”时，才可能 open detour。

Detour 有时需要先 active recall 或 look-back。若 target_hint 来自 memory projection，需要 active recall 确认 memory state；若 target_hint 需要 source locus，需要 source skill / look-back 校准。但 detour target 不能只由 memory projection 选中。

三者避免互相吞并职责的规则是：

```text
active recall restores memory state;
look-back calibrates source evidence;
detour controls reading path.

memory summary cannot become source truth;
source excerpt cannot become semantic memory automatically;
path deviation cannot become hidden retrieval.
```

------

## 5. Active Recall Policy

### 5.1 Trigger conditions

Active recall 应触发，当当前 reading / navigation 出现以下情况之一：

1. 当前 unit 或 preview 依赖 earlier concept / thread / reaction，但该信息未在 carry-forward packet 中。
2. 当前 `reading_impression` 风险是丢失一个已知 thread，而不是只缺当前 source wording。
3. visible callback 需要 earlier memory state 才能保持 faithful continuity。
4. `active_attention` references unresolved prior focus，而当前 packet 无法解释它。
5. current source reactivates cooled / dormant thread，需要恢复其 prior state。
6. current source 需要 prior conceptual distinction 才能理解。
7. 当前 state packet 明显不足，例如 concept/thread digest 没带相关条目，但 SourceRef digest 或 current source 提示该条目仍重要。
8. Detour localization 前需要确认 target_hint 是否来自真实 prior memory，而不是 theme-only association。

### 5.2 Non-trigger conditions

Active recall 不应触发，当：

1. 需要的是 source evidence，而不是 memory state；此时应 look-back。
2. 相关 memory item 是 `superseded / invalidated / rejected`，且没有 explicit lineage intent。
3. 当前 source 可以安全理解，recall 只会满足 curiosity。
4. reaction digest 是唯一依据；reaction_records 是 visible trace，不是 semantic basis。
5. knowledge activation 是唯一依据；knowledge_activations 是 warrant ledger，不是 book truth。
6. memory projection 与 current source 冲突；此时先 look-back 校准。
7. recall 会超过 budget，且 mainline 可以安全继续。
8. recall 只是为了“更完整”，没有当前 reading need。

### 5.3 Allowed sources

Active recall 允许读取：

```text
active_attention digest / authorized store projection
concept_registry
thread_trace
bounded reflective_frames
reaction_records, only as visible trace / callback context
knowledge_activations, only as warrant-bearing projection with warning
current_truth_projection
lineage_projection, only with explicit lineage intent
```

Active recall 不允许读取：

```text
full durable store prompt dump
audit dump
evaluation reports
raw debug trace
source corpus as memory
future text
external web
```

Lifecycle-aware rules：

```text
current_truth_projection:
  normal active recall should use current, source-supported, non-rejected items.

lineage_projection:
  can include superseded / invalidated / retired items only when the intent is historical lineage, correction, reconsolidation, or FVI diagnosis.
  Must carry warning markers.
```

### 5.4 Output and use

Active recall 返回：

```text
memory_refs
compact summaries
source_refs available
store scope
status / validity markers
why recalled
used_for
warning markers if stale / lineage-only
```

Active recall output should also classify use channel:

```text
current_memory_support
lineage_support
visible_trace_support
warrant_support
not_used
```

Active recall 不能：

```text
write memory
change cursor
open detour by itself
select detour target
generate route-disclosure output
replace source verification
treat reaction_records as semantic truth
treat knowledge_activations as source truth
```

### 5.5 Exit / stop condition

Active recall 停止，当：

```text
relevant current memory found
no relevant memory found
only stale / superseded memory found
budget exhausted
source verification required
returned memory not useful
conflicting memory requires look-back
memory item status requires lineage warning
```

Fallback：

- 若 found current relevant memory：用作 Read / Navigate support，继续当前 loop。
- 若 no relevant memory：继续 mainline，记录 failure_reason。
- 若 stale only：不作为 current truth；可触发 look-back 或 lineage-only note。
- 若 conflict：look-back 校准 source。
- 若 budget exhausted：不继续扩检索，不开 hidden search。

### 5.6 Active recall audit

最小 fields：

```text
active_recall_requested
trigger_reason
query_basis
memory_store_scopes
memory_refs_returned
status_markers
source_refs_available
used_for
no_use_reason
budget_state
stop_reason
failure_reason
lineage_intent
warning_markers
```

------

## 6. Look-back Policy

### 6.1 Trigger conditions

Look-back 应触发，当当前 reading / navigation 需要 earlier source evidence：

1. 当前理解依赖 earlier definition / distinction / claim。
2. concept digest 或 memory summary 与 current source 出现冲突。
3. visible callback 需要 source grounding，避免凭记忆联想硬连。
4. FVI risk detected：overclaim、hard-linking、theme-only similarity、memory drift。
5. SourceRef chain 需要验证。
6. active recall 返回 stale / uncertain / conflicting memory。
7. 当前 reading 若继续会 overclaim。
8. current source contains explicit backward cue，例如“前文”“earlier”“as said above”，且 SourceRef 可定位。

### 6.2 Non-trigger conditions

Look-back 不应触发，当：

1. active recall 已足够，缺的是 memory state 而非 source evidence。
2. current source 已提供足够 evidence。
3. look-back 只是为了 comfort reread。
4. source_ref unavailable 或太弱，无法提出 source-grounded question。
5. curiosity / theme association only。
6. budget exhausted。
7. look-back 会打断主线且无明确 calibration value。
8. 用户可见 reaction 只是情绪/共鸣，不需要原文校准。

### 6.3 Allowed source locus

Look-back 只能使用：

```text
SourceRef
SourceSpan
unit_span_ledger / accepted-read coverage facts
already-read source
bounded excerpt
```

Look-back 不允许：

```text
future text
external web
hidden search
whole chapter reread by default
unbounded source dump
source excerpt without SourceRef / SourceSpan basis
```

### 6.4 Output and use

Look-back 返回：

```text
earlier source excerpt
source span / SourceRef
reason for calibration
source_evidence_used
relation to current source
quote boundaries
calibration_result
```

Look-back 不能：

```text
write memory
automatically write excerpt into memory
change path by itself
generate route-disclosure output
automatically become detour
treat excerpt as hidden reading unit
```

若 excerpt 需要被正式“读”而不是作为 calibration support 使用，必须由 detour policy 升级为 detour unit，走同一个 Navigate → Read → settlement loop。

### 6.5 Exit / stop condition

Look-back 停止，当：

```text
source excerpt returned and sufficient
source unavailable
SourceRef ambiguous
look-back failed
current source still uncertain
should escalate to detour candidate
budget exhausted
```

Fallback：

- sufficient：校准当前理解，继续 mainline。
- ambiguous/unavailable：记录 failure；必要时 active recall 或继续 mainline with uncertainty。
- still uncertain and path-relevant：可成为 detour candidate。
- budget exhausted：不扩大为 hidden search。

A failed look-back / failed source calibration must not be silently replaced by memory confidence. If source calibration fails, the system may record uncertainty, use an allowed fallback, form a detour_candidate, or continue mainline with uncertainty, but it cannot simply trust memory as source truth.

### 6.6 Look-back audit

最小 fields：

```text
look_back_requested
trigger_reason
source_ref_or_span_used
excerpt_returned
quote_boundaries
calibration_result
used_for
source_evidence_used
budget_state
stop_reason
failure_reason
escalated_to_detour_candidate
```

------

## 7. Detour Policy

### 7.1 What can open a detour

Detour 可以由以下来源打开：

1. `Read.detour_need` from current accepted unit。
2. 后续 policy-authorized、source-grounded path need。
3. unresolved source dependency blocks or seriously weakens current reading。
4. high-value earlier source target can clarify current unit。
5. active recall / look-back reveals a source-grounded path need。
6. current thread requires bounded path deviation to preserve mainline understanding。

Active recall or look-back may surface a detour_candidate, but only Runner / policy-authorized settlement can open active_detour_need. read_context never mutates local_continuity.

Detour 不应由以下内容单独打开：

```text
ordinary curiosity
visible reaction
outside_link
search_intent
knowledge activation
theme-only association
visible route disclosure
prior knowledge without source trigger
reaction digest without source evidence
```

### 7.2 Required detour opening fields

当前 schema 已有：

```text
DetourNeed:
  reason
  target_hint
  status

LocalContinuityState:
  mainline_cursor
  active_detour_id
  active_detour_need
  detour_trace

DetourTraceEntry:
  detour_id
  origin_cursor
  origin_target_hint
  status
```

本 policy 要求 opening decision 至少概念上具备：

```text
detour_id
origin_cursor
origin_source_span_id
opened_by
reason
target_hint
source_scent
detour_value
continuity_cost
budget
status = open
restore_mainline_cursor
```

其中：

- `detour_id / origin_cursor / target_hint / status` 已有 runtime continuity support。
- `origin_source_span_id / opened_by / source_scent / detour_value / continuity_cost / budget / restore_mainline_cursor` 可先作为 audit fields。
- 不要求本页立即新增 durable planning store。
- 不要求 `DetourNeed` schema 一次性承载所有 fields。

### 7.3 Detour localization

Active detour mode 的 localization 规则：

```text
Navigate uses target_hint as localization hint, not target.
Source skills provide evidence, not semantic judgment.
Target must be already-read or visible-to-mainline boundary allowed by current system.
No future text.
No external web.
Candidate unit must have source evidence.
Detour target cannot be selected by memory projection alone.
Reaction digest / knowledge activation cannot be sole target basis.
```

If target_hint only forms a theme association, defer.

### 7.4 Detour continue / choose unit

Navigate chooses a detour unit only when：

```text
source_evidence_sufficient
source_scent strong enough
detour_value high enough
continuity_cost acceptable
target unit bounded
budget available
candidate likely to clarify / resolve / reject active detour need
```

Once chosen, detour unit enters:

```text
Navigate.choose_next_unit
  → Runner resolves source span
  → Read
  → settlement
  → detour state update
  → restore or continue
```

No hidden supplemental fetch.

### 7.5 Request source evidence skill

Navigate requests a source skill when：

```text
mode = active_detour
source_scent plausible
evidence missing
allowed skill can answer a source-locus question
budget available
missing evidence reason is structured
```

Allowed skills：

```text
source_map_overview
  already-read chapter/source cards

source_scope_drilldown
  finer cards from a selected scope

source_window_fetch
  bounded source text from a visible sentence range
```

Skill is not：

```text
hidden search
answer generator
route-disclosure generator
memory writer
semantic relevance judge
future-text reader
```

### 7.6 Defer detour

`defer_detour` 继承 Navigation Policy：

```text
defer_detour is a Navigate act decision.
It is not durable detour status.
It must not silently become abandoned.
It should record defer_reason.
```

Policy conditions for defer：

```text
source_scent weak
target_hint only thematic
detour_value too low
continuity_cost high
budget exhausted
source evidence unavailable
current source likely to explain itself soon
detour would cause thrashing
better preserved as audit-only curiosity, visible reading note candidate, outside_link, or search_intent without affecting route
```

Behavior:

- If implementation can safely do it, restore mainline for at least the next mainline unit.
- Prevent immediate reattempt only if implementation or later policy supports cooldown.
- Durable `deferred` status is not required in v0.
- If current runner cannot safely support cooldown, implement audit/logging first.
- Even if behavior-level cooldown is not implemented, audit must record `same_detour_reattempt_risk` when the same `target_hint` is deferred repeatedly.

### 7.7 Abandon detour

Abandon means the detour is no longer worth pursuing or no longer valid.

Abandon conditions：

```text
evidence proves target not relevant
driving uncertainty naturally resolved
repeated weak scent
budget exhausted with no recovery value
detour would harm mainline continuity
current source moved on and no longer requires it
```

Distinction：

```text
defer:
  not now / insufficient evidence / continue mainline

abandon:
  no longer worth pursuing / no valid target / invalidated

resolve:
  detour fulfilled its function
```

Visible route disclosure has no detour lifecycle authority: it cannot open, defer, abandon, resolve, restore, or steer a detour, and it creates no user accept/reject state.

Read may propose resolved / abandoned status inside active detour. Navigate may provide evidence for defer or a bounded reason that the target is weak, but Navigate does not directly abandon durable detour state. Runner / local_continuity settlement records final status transition.

### 7.8 Resolve detour

Resolve conditions：

```text
detour unit read and clarified original uncertainty
look-back/source evidence answered the question
current source made detour unnecessary
active recall recovered sufficient memory state and no path deviation needed
source evidence rejects target_hint
Read returns detour_need.status = resolved, and Runner settles state effect
```

Resolve does not mean source truth was rewritten. It closes a path obligation.

### 7.9 Restore mainline

`restore_mainline` is not a Navigate output. It is a Runner / local_continuity settlement effect.

Restore should record：

```text
restored_cursor = mainline_cursor
restore_mainline = true
restore_reason
status_before
status_after
detour_trace updated
```

Recommended restore reason vocabulary：

```text
resolved_current_uncertainty
detour_value_satisfied
detour_scent_weak
source_evidence_missing
budget_exhausted
avoid_detour_lingering
mainline_continuity_restored
abandoned_no_valid_target
deferred_low_value
```

### 7.10 Budget and stop condition

Detour budget contract includes：

```text
act budget
skill budget
source window budget
max detour units
max consecutive detour attempts
chapter/session boundary guard
stop reason
```

No numeric constants are set here. Implementation Handoff may assign values later.

Stop reasons：

```text
resolved
abandoned_no_valid_target
deferred_low_value
source_scent_weak
source_evidence_missing
budget_exhausted
mainline_continuity_at_risk
chapter_boundary
runner_resolution_failed
```

### 7.11 Detour audit

Minimum detour audit fields：

```text
detour_id
origin_cursor
origin_source_span_id
opened_by
reason
target_hint
source_scent
detour_value
continuity_cost
budget_state
decision
source_evidence_used
memory_refs_used
skill_requests
chosen_source_span
defer_reason
abandon_reason
resolve_reason
restore_mainline
restore_reason
status_before
status_after
failure_reason
```

------

## 8. Interaction with Read / Navigate / Runner / Settlement

### Read

Read may：

```text
emit detour_need
create surfaced reactions
propose memory_uptake_ops
set detour_need.status to resolved / abandoned when reading inside active detour
```

Read does not：

```text
localize detour target
execute look-back
decide next route
write final memory state
write planning state directly
generate visible route surface object
```

### Navigate

Navigate may：

```text
choose mainline unit
choose detour unit
request source skill
defer detour
mark support flags / audit signals
```

Navigate does not：

```text
execute full active recall
execute full look-back policy
write memory
write reaction_records
generate visible route surface object
restore mainline as output
read future text
perform external search
```

### Runner

Runner：

```text
applies local_continuity
dispatches source skills
resolves end_anchor_text / source spans
invokes Read
settles state effects
restores mainline
records audit
advances cursor
persists runtime artifacts
```

### `read_context`

`read_context` executes bounded active_recall / look_back support when authorized.

It returns supplemental context and does not mutate memory.

### settlement / state_ops

Settlement / state_ops：

```text
bind SourceRefs
normalize operations
apply memory ops
persist visible reactions
update detour state where authorized
record audit
```

------

## 9. Policy Decision Table

| Situation                                        | Active recall?                          | Look-back?                                  | Open / continue detour?                       | Default action                                               | Reason / audit consequence                              |
| ------------------------------------------------ | --------------------------------------- | ------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------- |
| 当前 source 引用前文定义                         | Yes, if definition memory not carried   | Yes, if exact wording matters               | No by default                                 | Recall concept; look-back only if source calibration needed  | audit `definition_dependency`, memory refs / SourceRefs |
| 当前 source 与 memory summary 冲突               | No as final answer                      | Yes                                         | No initially                                  | Look-back source evidence before using memory                | audit `memory_source_conflict`, calibration_result      |
| current unit opens unresolved target_hint        | Maybe, if target_hint depends on memory | Maybe, if source locus exists               | Yes, if source_scent/value/cost pass          | Open detour_need through Runner                              | audit opened_by=Read, target_hint, source_scent         |
| reaction wants callback earlier moment           | Yes, for visible continuity             | Yes, if callback risks FVI                  | No by default                                 | Recall visible trace; calibrate source if overclaim risk     | reaction_records are trace, not semantic basis          |
| prior knowledge activation triggered             | No, unless current memory also needed   | Maybe, if source trigger needs calibration  | No by itself                                  | Treat as warrant; continue mainline unless blocking source cue | audit knowledge_activation_warning                      |
| thread digest indicates continuity               | Yes, if thread state not carried        | Maybe, if source evidence needed            | No by default                                 | Recall thread or continue with digest                        | audit thread_continuity, used_for                       |
| detour source scent weak                         | No                                      | Maybe one bounded source skill if plausible | Defer                                         | Restore/continue mainline                                    | audit defer_reason=`detour_scent_weak`                  |
| detour budget exhausted                          | No more                                 | No more                                     | Stop                                          | Defer or abandon; restore mainline                           | audit budget_state, stop_reason                         |
| active recall returns superseded memory          | Only lineage use                        | Yes if current truth needed                 | No by default                                 | Mark stale warning; look-back if needed                      | audit lineage_intent, warning_markers                   |
| look-back source unavailable                     | Maybe, for memory continuity            | Failed                                      | No unless path need remains                   | Continue mainline with uncertainty or defer                  | audit failure_reason=`source_unavailable`               |
| current source likely explains itself next       | No unless blocking                      | No unless FVI risk                          | Defer                                         | Continue mainline                                            | audit `current_source_likely_self_explains`             |
| support chapter appears relevant but is deferred | No by default                           | No by default                               | No internal detour by default                 | Keep survey reading_plan and route trace only; future visible surface may disclose the deferral but not create a user choice | avoid support-chapter novelty chasing                   |
| theme-only association appears interesting       | No                                      | No                                          | No                                            | Visible reaction or audit-only curiosity                     | audit-only `theme_only_association`; no detour          |
| FVI risk detected                                | Maybe, to inspect memory state          | Yes                                         | Only if calibration requires formal unit read | Look-back first                                              | audit FVI risk, source evidence used                    |
| current mainline can continue safely             | No                                      | No                                          | No                                            | Continue source-order mainline                               | audit mainline_continuity; no support action            |

------

## 10. Stale Memory / FVI / Source-grounding Guardrails

1. `superseded / invalidated / rejected` memory must not be returned as current truth under ordinary active recall.
2. Stale item may be returned only with explicit lineage intent and warning marker.
3. Look-back is preferred when source calibration is needed.
4. `reaction_records` are visible trace. They cannot serve as semantic recall basis by themselves.
5. Recent reaction digest may support visible continuity, but not semantic navigation justification.
6. `knowledge_activations` are warrant ledger, not book truth.
7. Prior knowledge cannot open detour alone.
8. Theme-only association cannot open detour.
9. Source skill result does not become memory automatically.
10. Audit trace must not enter runtime prompt.
11. No hidden search.
12. No future text.
13. No detour lingering: every detour attempt needs stop reason.
14. No over-search: weak scent + low value + high continuity cost must defer.
15. No route-disclosure leakage: internal defer or detour candidate is only internal route trace / audit until a future Visible Reading Route Surface Boundary authorizes display-only disclosure.

------

## 11. Budget, Failure, and Recovery

### Active recall budget

Budget dimensions：

```text
store scopes
item count
lineage item count
source_ref count
attempt count
prompt token budget
```

Stop reasons：

```text
found_relevant_memory
no_relevant_memory
stale_only
conflict_requires_look_back
budget_exhausted
not_useful
source_verification_required
```

Recovery：

- If successful: use returned memory with refs and status markers.
- If no memory: continue mainline if safe.
- If stale only: do not use as truth; look-back if source evidence needed.
- If conflict: look-back.
- If budget exhausted: audit-only; no expansion.

### Look-back budget

Budget dimensions：

```text
SourceRef count
SourceSpan count
excerpt count
source window size
attempt count
```

Stop reasons：

```text
excerpt_sufficient
source_unavailable
source_ref_ambiguous
look_back_failed
still_uncertain
escalate_to_detour_candidate
budget_exhausted
```

Recovery：

- If sufficient: continue current reading.
- If unavailable: record uncertainty, continue mainline if safe.
- If still uncertain and path-relevant: detour candidate.
- If budget exhausted: no broader search.

### Detour budget

Budget dimensions：

```text
Navigate act budget
source skill budget
source window budget
max detour units
max consecutive detour attempts
chapter/session boundary allowance
```

Stop reasons：

```text
resolved
deferred
abandoned
budget_exhausted
source_evidence_missing
source_scent_weak
continuity_cost_high
mainline_restored
```

Recovery：

- After failed detour: restore mainline and record failure.
- After weak scent: defer, optionally cooldown future reattempt if later implementation supports it.
- After no valid target: abandon.
- After budget exhaustion: stop; do not run hidden search.
- If still valuable but not internal-path-worthy: preserve as audit-only curiosity, visible reading note candidate, outside_link, or search_intent, without affecting route.
- If repeated unresolved obligation persists across chapter/session: Slow-cycle / Macro-planning may carry an obligation, but must not become detour manager.

------

## 12. Audit / Observability Minimal Contract

Audit is diagnostic artifact. It must not expose chain-of-thought and must not enter prompt by default.

### Active recall audit

```text
mechanism = active_recall
active_recall_requested
trigger_reason
query_basis
memory_store_scopes
memory_refs_returned
status_markers
source_refs_available
used_for
no_use_reason
budget_state
stop_reason
failure_reason
lineage_intent
warning_markers
```

### Look-back audit

```text
mechanism = look_back
look_back_requested
trigger_reason
source_ref_or_span_used
excerpt_returned
quote_boundaries
calibration_result
used_for
source_evidence_used
budget_state
stop_reason
failure_reason
escalated_to_detour_candidate
```

### Detour audit

```text
mechanism = detour
detour_id
origin_cursor
origin_source_span_id
opened_by
reason
target_hint
source_scent
detour_value
continuity_cost
budget_state
decision
source_evidence_used
memory_refs_used
skill_requests
chosen_source_span
defer_reason
abandon_reason
resolve_reason
restore_mainline
restore_reason
status_before
status_after
failure_reason
```

### Cross-mechanism fields

```text
current_source_span_id
current_cursor
mode
support_flags
operational_trigger
audit_only_signal
source_evidence_used
memory_refs_used
used_for
not_used_reason
budget_state
stop_reason
failure_reason
outcome
visible_user_surface = false by default
chain_of_thought_exposed = false
```

This minimal contract should support later Planning Evaluation:

```text
Detour Precision
Recovery Quality
Over-search Rate
Planning-Memory Alignment
```

and later Memory Evaluation:

```text
False Visible Integration
Spontaneous Callback
Memory utilization diagnosis
stale-memory diagnosis
```

------

## 13. Compatibility with Prior Designs

Compatibility check:

| Constraint                                                   | Status    |
| ------------------------------------------------------------ | --------- |
| No redefinition of Memory Ontology                           | Satisfied |
| No redefinition of Planning Ontology                         | Satisfied |
| No expansion of Navigate act space                           | Satisfied |
| `active_recall_needed / look_back_needed` not operational triggers | Satisfied |
| `restore_mainline` not Navigate output                       | Satisfied |
| Read does not localize detour target                         | Satisfied |
| Look-back does not automatically write memory                | Satisfied |
| Active recall does not replace source verification           | Satisfied |
| Detour does not become hidden supplemental fetch             | Satisfied |
| reaction_records not semantic memory                         | Satisfied |
| knowledge_activations not source truth                       | Satisfied |
| audit trace not runtime context                              | Satisfied |
| No full Retrieval / Visible Route Disclosure / Evaluation design | Satisfied |
| Simplicity and Universality preserved                        | Satisfied |

------

## 14. Accepted Constraints and Deferred Directions

Accepted constraints:

```text
No large planner node.
  The current problem is policy clarity, not missing planner.

No new planning store.
  local_continuity is enough for v0; richer fields can begin as audit.

No expansion of NavigateActResult decisions.
  choose_unit / request_skill / defer_detour remain sufficient.

No full retrieval taxonomy.
  This page defines interface constraints only.

No vector DB / graph DB.
  SourceRef, metadata, status, links, scope, and bounded projections come first.

No hidden search.
  Source skills are book-local evidence only.

No future text.
  Detour and look-back stay inside allowed source boundary.

No visible route disclosure design.
  Route disclosure is later optional product surface, not route control.

No default ToT / LATS / MCTS.
  Search-based deliberation is over-complex for ordinary reading.

No full learner model.
  Reading Companion is not a tutoring platform.

No Codex roadmap.
  This page is policy design.

No full audit schema.
  Only minimal contract.

No slow-cycle takeover.
  Slow-cycle may carry macro obligations but is not detour manager.
```

------

## 15. What This Design Changes or Tightens

### Preserved

```text
active_recall and look_back helpers
detour same-loop reading
source skills
local_continuity
mainline default
Read.detour_need
Runner settlement authority
file-based JSON / JSONL artifacts
```

### Tightened

```text
active recall trigger / non-trigger
look-back trigger / non-trigger
detour open / continue / defer / abandon / resolve
restore-mainline reason vocabulary
source_scent / detour_value / continuity_cost language
budget / stop reason
stale memory warning markers
source_evidence_used / memory_refs_used audit fields
support flags as audit/support, not triggers
```

### Reinterpreted

```text
defer_detour:
  Navigate act decision, not durable status.

detour_need:
  planning intent, not target and not memory op.

reaction_records:
  visible trace only.

knowledge_activations:
  warrant ledger only.

source skills:
  source evidence providers, not hidden search.
```

### Deferred

```text
full Retrieval / Utilization
visible route surface / UX
Planning Audit full schema
Planning Evaluation rubric
durable deferred detour state machine
multi-detour queue
implementation roadmap
```

------

## 16. Design Implications for Later Pages

### Memory Retrieval / Utilization

This page provides retrieval intents and utilization trace requirements:

```text
active_recall: memory recovery
look_back: source calibration
detour support: source-grounded path need
```

Later Retrieval design must define ranking, filtering, lifecycle-aware current truth vs lineage projection, and retrieval algorithms.

### Visible Reading Route Surface Boundary

Deferred detour or low-value detour may become display candidate input, but internal detour state does not automatically become visible route disclosure. Visible Reading Route Surface Boundary must preserve legibility and no_user_surface_needed, and it must not create route controls, route options, or route-steering output.

### Planning Audit / Observability

This page supplies minimal fields for detour / recall / look-back trace. Later Audit design may normalize them into schema.

### Planning Evaluation

This page supplies behavior categories for Detour Precision, Recovery Quality, Over-search Rate, Mainline Restoration, and Planning-Memory Alignment.

### Memory Audit / Evaluation

This page supplies utilization trace boundaries for Callback / FVI diagnosis and stale-memory use.

### Slow-cycle / Macro-planning

Slow-cycle may carry unresolved high-value obligations across chapter/session boundary, but must not become a big planner or detour manager.

### Implementation Handoff

Implementation Handoff should translate reason vocabulary and audit fields into small safe patches, not redesign the mechanism.

------

## 17. Implementation Readiness Notes

### MVP ready

```text
reason logging for active_recall / look_back / detour
source_evidence_used / memory_refs_used
support flags as audit-only
detour defer / resolve / abandon / restore reason logging
budget_state / stop_reason
stale memory warning marker
no future text guardrail
```

Later / not MVP:

```text
full active recall execution changes
full look-back execution changes
detour candidate admission engine
defer cooldown behavior
durable deferred status
multi-detour queue
```

### Ready for narrow implementation

```text
active_recall / look_back / detour reason logging
support flag audit fields
detour open / defer / abandon / resolve reason vocabulary
restore-mainline reason logging
source_evidence_used / memory_refs_used
skill budget / stop reason logging
stale memory warning markers
no future text guardrails
audit-only support flags
defer_reason logging
no-op prevention for ordinary Navigate acts
```

### Needs Retrieval design first

```text
full retrieval intent taxonomy
memory ranking
lifecycle-aware current_truth_projection vs lineage_projection
retrieval failure semantics
retrieval utilization schema beyond minimal trace
```

### Needs Visible Reading Route Surface Boundary first

```text
visible route surface display shape
visible reading note wording
display preference / suppression, if needed
route trace disclosure rules
optional support chapter deferral note
```

### Needs Planning Audit / Evaluation first

```text
full planning audit schema
Detour Precision rubric
Recovery Quality rubric
Over-search Rate computation
Planning-Memory Alignment scoring
```

### Needs Slow-cycle / Macro-planning first

```text
chapter/session carry-forward of unresolved detour obligations
macro focus selection
cross-chapter detour cooling / retirement
```

### Needs Implementation Handoff

```text
schema field placement
backward-compatible migration
runtime artifact update
test contract
prompt wording changes
```

### Explicitly not now

```text
full retrieval taxonomy
retrieval ranking infrastructure
vector retrieval
graph retrieval
visible route surface object
user interaction surface
full durable detour state machine if current runner cannot safely support it
multi-detour queue
full evaluation rubric
Codex implementation roadmap
```

------

## 18. Optional Open Questions

1. **Should `deferred` become durable detour status?**
   Not critical at this phase. Current schema supports open / resolved / abandoned; Navigation Policy treats defer as act decision. Durable deferred status depends on Implementation Handoff and possibly Visible Reading Route Surface Boundary.
2. **How should lifecycle-aware active recall expose superseded / invalidated items?**
   Not blocking. This depends on Memory Retrieval / Utilization design for current_truth_projection vs lineage_projection. v0 only requires warning markers and explicit lineage intent.
3. **Should detour skills migrate fully from legacy sentence handles to paragraph-offset SourceSpan handles?**
   Not blocking policy. Current implementation uses sentence handles for source skills while mainline cursor is paragraph-offset. Implementation Handoff may decide whether to bridge or migrate.

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

| Project evidence                                    | Current fact shown                                           | Supports design judgment                                     | Status                                            |
| --------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------- |
| `docs/product-overview.md`                          | Product is a text-grounded, legible, self-propelled co-reading mind; not summary engine or service assistant; prior knowledge cannot justify text-detached certainty. | No hidden search, no novelty chasing, knowledge activation not source truth. | Stable product constraint                         |
| `docs/current-state.md`                             | Current source cursor / SourceRef cutover, settlement audit diagnostic, source-skill posture, active long-span direction. | Use current implementation facts but avoid overclaiming runtime quality. | Current fact plus runtime-artifact validation gap |
| `docs/source-of-truth-map.md`                       | Workspace is repo-first; durable project truth belongs in canonical repo docs. | This design should be a stable mechanism design doc, not chat-only guidance. | Stable governance constraint                      |
| `docs/backend-reading-mechanism.md`                 | `book_document.json` is shared source truth; paragraph substrate; inline SourceRef; no shared Anchor Bank. | Source corpus is not memory; source evidence must use source locus. | Stable shared mechanism constraint                |
| `docs/backend-reading-mechanisms/attentional_v2.md` | Current loop is `Navigate.choose_next_unit → Read → settlement`; detour uses same loop; source skills are bounded book-local evidence; Read emits detour_need. | Preserve attentional_v2, same-loop detour, source skill boundaries. | Live mechanism fact                               |
| `schemas.py`                                        | Defines `DetourNeed`, `LocalContinuityState`, `NavigateActResult`, `NavigateActTraceEntry`, store schemas, operation vocabulary. | Policy must not expand act space; detour fields beyond schema begin as audit. | Contract-level evidence                           |
| `prompts.py`                                        | Navigate prompt restricts act space and source skills; Read prompt limits memory targets and detour role. | Read cannot localize target; Navigate cannot search web; memory ops bounded. | Contract-level evidence                           |
| `nodes.py`                                          | Normalizes detour statuses, surfaced reactions, state ops; filters internal handles; current `_STATE_OPERATION_TYPES` misses `resolve` despite schema. | Shows normalization surface and contract alignment gap; supports tightening. | Current implementation fact                       |
| `runner.py`                                         | Applies detour_need into local_continuity; opens trace, sets active_detour pointer, resolves/abandons by status. | Runner settles detour state effects; restore-mainline belongs to Runner/local_continuity. | Contract-level evidence                           |
| `read_context.py`                                   | Implements bounded `active_recall` and `look_back` helpers.  | active_recall = memory recovery; look_back = source calibration. | Current implementation fact                       |
| `skills/runtime.py` and `skills/source_skills.py`   | Skills are `source_map_overview / source_scope_drilldown / source_window_fetch`, bounded by mainline cursor and visible scope. | Source skills are evidence providers, not hidden search or memory writers. | Contract-level evidence                           |
| `source_spans.py`                                   | Defines paragraph-offset SourceCursor / SourceSpan / SourceRef, preview, exact anchor resolution, source-ref quote resolution. | Look-back and detour must be source-locus grounded.          | Stable mechanism fact                             |
| `state_projection.py`                               | Builds bounded read/navigation prompt packets, concept/thread/source_ref/reaction digests. | Planning consumes projections only; projection is not authoritative state. | Contract-level evidence                           |
| `state_ops.py`                                      | Deterministic apply layer; merges source refs; concept/thread updates; reflective supersede preserves old statement. | Lifecycle-aware recall; stale/superseded guardrails.         | Contract-level evidence                           |
| `observability.py`                                  | Current read/settlement audit fields.                        | Minimal audit can extend existing streams rather than full snapshot. | Current implementation fact                       |
| `storage.py`                                        | Lists mechanism-private runtime artifacts.                   | State / audit / memory / reaction separation.                | Current implementation fact                       |
| `slow_cycle.py`                                     | Persists surfaced reactions with `prior_link / outside_link / search_intent`; compatibility family derived. | reaction_records are visible trace, not semantic memory or route disclosure. | Contract-level evidence                           |
| `knowledge.py`                                      | Knowledge activations require warrant; rejected/dropped statuses; search remains conservative. | knowledge activation is warrant ledger, not source truth or detour trigger. | Contract-level evidence                           |
| `backend-reader-evaluation.md`                      | Long-span direction: Memory Quality, Spontaneous Callback, False Visible Integration. | Audit fields should support FVI / callback / memory utilization diagnosis. | Stable evaluation constitution                    |

Runtime-artifact validation gap: this design did not independently inspect real `read_audit.jsonl / settlement_audit.jsonl / unit_span_ledger.jsonl / local_continuity.json` rows. It uses repo code, mechanism docs, and `current-state.md` diagnostic summaries.

------

## B. Upstream Design Basis

P0 Shared Charter supplies the fixed boundaries: `LLM proposes; deterministic runner settles`; source corpus / memory / planning state / audit / visible reaction / visible route disclosure separation; active recall as memory recovery; look-back as source calibration; detour as planning path deviation; mainline continuity default; detour same-loop; audit as diagnosis, not chain-of-thought.

Planning Ontology supplies object identity: Planning is reading path control and attention scheduling, not AutoGPT-style task planning. `local_continuity`, `mainline_cursor`, `active_detour_need`, and `detour_trace` are the v0 planning-state surfaces. This design turns those objects into policy rules without redefining them.

Navigation Policy supplies act-space constraints: `Navigate.choose_next_unit` remains source-grounded next-unit selector / detour localizer; `choose_unit / request_skill / defer_detour` remain the only live decisions; support flags are not operational triggers; `restore_mainline` is Runner effect, not Navigate output. This design fills trigger / exit / budget / recovery.

Memory Ontology supplies memory-store boundaries: active_attention, concept_registry, thread_trace, reflective_frames, reaction_records, knowledge_activations, reconsolidation_records have distinct identities. This design prevents active recall from treating reaction_records or knowledge_activations as semantic truth.

Memory Formation & Settlement supplies Read boundaries: `memory_uptake_ops` are bounded write intent; `detour_need` is planning intent; Read cannot locate detour targets, execute look-back, or write final state. This design preserves those boundaries.

Memory Management & Evolution supplies lifecycle constraints: visibility lifecycle differs from semantic validity lifecycle; superseded / invalidated / rejected memory must not be returned as current truth; cooled / dormant items are low-priority, not false; lineage projection requires warning. This design makes active recall lifecycle-aware.

Planning Assessment supplies the core problem diagnosis: detour / look-back / active recall exist but lack trigger, budget, exit, recovery, and audit policy; avoid novelty chasing and over-search; do not introduce large planners, multi-agent teams, graph rewrites, or default tree search.

Memory Assessment supplies retrieval-interface constraints: retrieval must be intent-aware and bounded; active recall / look-back / detour retrieval needs budget, stop reason, failure reason, and utilization trace; SourceRef, metadata, status, links, chapter scope come before vector / graph retrieval.

No upstream conflict requires reopening ontology. The main conflict is implementation incompleteness: current schemas and audits do not yet carry all policy fields. This design resolves that by classifying new fields first as policy/audit fields, not by demanding immediate durable state expansion.

------

## C. External Rationale, as Filtered Through the Assessments

| External work                                | Original problem                                             | Supports this design                                         | Similarity                                               | Difference                                              | Localized use                                | Do not copy                          | Support type          |
| -------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------------------------- | ------------------------------------------------------- | -------------------------------------------- | ------------------------------------ | --------------------- |
| ReAct                                        | Interleave reasoning, action, and observation for correction. | Detour source-skill loop should be observation-grounded.     | Source skill result is observation-like evidence.        | Reading is not open tool task.                          | Bounded detour correction loop.              | Full ReAct every read step.          | Analogical            |
| ReWOO                                        | Decouple reasoning from observation gathering to reduce cost. | Source evidence gathering can be bounded and budgeted.       | Skill requests can gather evidence before decision.      | Reading path changes with ongoing source understanding. | Local evidence bundle only.                  | Frozen multi-hop planner.            | Analogical            |
| Options Framework                            | Temporally extended actions need initiation and termination. | Detour needs open, budget, stop, restore.                    | Detour is a temporally extended path option.             | No RL policy learning here.                             | Termination / restore contract.              | Formal RL option machinery.          | Direct / Analogical   |
| Information Foraging                         | Navigation balances value, cost, and scent.                  | detour_value / continuity_cost / source_scent.               | Reading path is information navigation.                  | Book reading has stronger author-order mainline.        | Lightweight reason vocabulary.               | Free web-style patch switching.      | Direct                |
| Exploratory Search                           | Open-ended exploration supports understanding but can sprawl. | Avoid novelty chasing and over-search.                       | Detour resembles exploratory move.                       | RC must preserve source-order reading.                  | Defer low-scent exploration.                 | Unbounded search loop.               | Boundary              |
| Rereading Effect                             | Rereading can improve metacomprehension accuracy.            | Look-back as calibration move.                               | Earlier source revisit can calibrate understanding.      | Human study, not agent implementation.                  | Triggered bounded look-back.                 | Default reread for comfort.          | Direct / Background   |
| Metacomprehension                            | Surface confidence can be unreliable.                        | FVI guardrails and look-back on conflict.                    | Need calibration beyond “seems understood”.              | Does not define LLM triggers.                           | Conflict / FVI triggers.                     | Blind trust in generated memory.     | Background            |
| Reflexion                                    | Agents learn between episodes through verbal reflection.     | Slow-cycle caution; audit should capture failures.           | Recovery and failure diagnosis matter.                   | RC must not mix strategy reflection into source memory. | Boundary for slow-cycle.                     | Per-step reflection memory.          | Boundary              |
| LongMemEval                                  | Long-term memory evaluation separates stages.                | Retrieval vs use trace.                                      | Memory retrieved must be distinguished from memory used. | Chat benchmark, not reading memory.                     | Audit retrieval/use fields.                  | QA-only benchmark schema.            | Analogical            |
| HaluMem                                      | Memory systems can hallucinate at operation stages.          | Guard stale memory / FVI / operation trace.                  | Pollution can happen before final output.                | Frontier benchmark, not RC-specific.                    | Need status markers and no hidden promotion. | Heavy benchmark machinery.           | Boundary              |
| MemGuide / ComoRAG                           | Intent-driven or impasse-triggered recall.                   | Active recall should be triggered by reading need, not fixed packet alone. | Recall responds to missing slot / impasse.               | Narrative RAG differs from RC memory.                   | Intent-aware recall interface.               | Full iterative RAG loop.             | Analogical            |
| Zep / Mem0                                   | Production memory requires operations, metadata, validity, lifecycle. | Stale / superseded / rejected handling; operation trace.     | Memory items need status and update semantics.           | Chat / enterprise memory, often graph/vector based.     | Lifecycle and operation language.            | Graph DB / user facts stack.         | Boundary / Analogical |
| Adaptive Navigation Support / Learner Agency | Guidance should not take over user path.           | Route disclosure boundary and no_user_surface_needed leakage.       | User-facing navigation support is display-only route disclosure.     | RC is co-reader, not tutoring platform.                 | Defer route disclosure UX to later boundary.     | Full learner model / mastery engine. | Boundary              |

------

## D. Simplicity and Universality Check

This design stays simple by tightening existing surfaces:

```text
existing active_recall / look_back helpers
existing detour_need
existing local_continuity
existing source skills
existing Navigate act space
existing read / settlement audit streams
```

It does not add:

```text
large planner
memory manager
planning manager
vector DB
graph DB
Memory OS
multi-agent team
default ToT / LATS / MCTS
full learner model
route-steering engine
```

It preserves:

```text
source-order mainline default
detour same-loop reading
no hidden search
no future text
reaction_records as visible trace
knowledge_activations as warrant ledger
audit trace not prompt context
bounded prompt-facing projections
```

It supports later design pages by providing clear interface constraints without prematurely implementing Retrieval, Visible Route Disclosure, Audit, Evaluation, or Slow-cycle policy.

Remaining complexity risks:

1. Audit field creep: minimal contract should not become full trace dump.
2. Durable detour state creep: `deferred` should remain act/audit unless implementation proves durable status necessary.
3. Source skill creep: skills must remain evidence providers, not relevance engines.
4. Route-disclosure leakage: deferred detours must not appear as visible route disclosures without Visible Reading Route Surface Boundary, and disclosure must not steer the route.
5. Lifecycle leakage: stale lineage recall must not become current truth.

------

## E. Source Usage List

| External source                                            | Authors / Organization   | Year        | Stable URL                                               | Used for                                      | Support type        |
| ---------------------------------------------------------- | ------------------------ | ----------- | -------------------------------------------------------- | --------------------------------------------- | ------------------- |
| ReAct: Synergizing Reasoning and Acting in Language Models | Shunyu Yao et al.        | 2022        | https://arxiv.org/abs/2210.03629                         | Observation-grounded local correction analogy | Analogical          |
| ReWOO: Decoupling Reasoning from Observations              | Binfeng Xu et al.        | 2023        | https://arxiv.org/abs/2305.18323                         | Bounded evidence gathering analogy            | Analogical          |
| Between MDPs and semi-MDPs: Options Framework              | Sutton, Precup, Singh    | 1999        | https://doi.org/10.1016/S0004-3702(99)00052-1            | Detour initiation / termination               | Direct / Analogical |
| Information Foraging                                       | Pirolli & Card           | 1999        | https://doi.org/10.1037/0033-295X.106.4.643              | source_scent / value / cost                   | Direct              |
| Exploratory Search: From Finding to Understanding          | Gary Marchionini         | 2006        | https://cacm.acm.org/research/exploratory-search/        | Boundary against uncontrolled exploration     | Boundary            |
| The rereading effect                                       | Rawson, Dunlosky, Thiede | 2000        | https://doi.org/10.3758/BF03209348                       | Look-back as calibration                      | Direct              |
| Metacomprehension                                          | Dunlosky & Lipko         | 2007        | https://doi.org/10.1111/j.1467-8721.2007.00509.x         | Calibration / confidence caution              | Background          |
| Reflexion                                                  | Noah Shinn et al.        | 2023        | https://arxiv.org/abs/2303.11366                         | Slow-cycle and recovery boundary              | Boundary            |
| LongMemEval                                                | Di Wu et al.             | 2024        | https://arxiv.org/abs/2410.10813                         | Retrieval vs use separation                   | Analogical          |
| HaluMem                                                    | Ding Chen et al.         | 2025        | https://arxiv.org/abs/2511.03506                         | Memory pollution / hallucination risk         | Boundary            |
| MemGuide                                                   | Yiming Du et al.         | 2025 / 2026 | https://ojs.aaai.org/index.php/AAAI/article/view/40313   | Intent-driven recall                          | Analogical          |
| ComoRAG                                                    | Juyuan Wang et al.       | 2025        | https://arxiv.org/abs/2508.10419                         | Impasse-triggered targeted recall             | Analogical          |
| Mem0 Memory Operations                                     | Mem0                     | 2025        | https://docs.mem0.ai/core-concepts/memory-operations/add | Operation/lifecycle boundary                  | Boundary            |
| Zep Temporal Knowledge Graph Architecture                  | Preston Rasmussen et al. | 2025        | https://arxiv.org/abs/2501.13956                         | Validity / invalidation / warrant boundary    | Boundary            |
| Adaptive Navigation Support in Educational Hypermedia      | Peter Brusilovsky        | 2003        | https://doi.org/10.1111/1467-8535.00345                  | Route disclosure boundary                    | Boundary            |
| Learner Agency systematic review                           | Michelle Deschênes       | 2020        | https://doi.org/10.1186/s41239-020-00219-w               | User-facing scaffold boundary                 | Boundary            |
