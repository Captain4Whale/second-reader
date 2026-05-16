# Navigation Policy Design v0

## 1. Scope and Purpose

本设计定义 Reading Companion / Second Reader 的 **Navigation Policy v0**。

它继承 P0 Shared Charter：Planning 在本项目中是 source-grounded reading path planning / attention scheduling / navigation support，不是 AutoGPT-style task planning；运行原则是 **LLM proposes; deterministic runner settles**。它继承 Planning Ontology v0：`Navigate.choose_next_unit` 是当前 micro-planning 层的 source-grounded next-unit selector，在 active detour mode 中也是 detour localizer，不是 global planner、visible route disclosure owner 或 memory writer。它兼容 Memory Ontology v0：Navigation 只能消费 bounded typed source-ref-preserving memory projections，不能直接读取完整 durable stores，也不能把 memory projection 当作 source truth。它也兼容 Memory Formation & Settlement v0：`Read.detour_need` 是 planning intent，`Read.memory_uptake_ops` 是 bounded write intent，最终 state mutation 由 Runner / settlement / state_ops 完成。

本页只设计 **Navigation Policy**。它为后续 Detour / Look-back / Active Recall Policy、Visible Reading Route Surface Boundary、Planning Audit / Observability、Planning Evaluation、Memory Retrieval / Utilization、Slow-cycle / Macro-planning、Implementation Handoff 提供边界与接口。本页不是 Planning Ontology 重写，不是 Memory Ontology 重写，不是 Memory Formation 重写，不是外部文献综述，也不是 Codex implementation roadmap。

本设计的目标是让现有 `attentional_v2` 中的 `Navigate.choose_next_unit` 更清晰、更可靠、更可审计：默认保持 source-order mainline continuity；在 active detour 中只做 bounded source-grounded localization；必要时请求 book-local source evidence；证据不足时 honest defer；detour 结束后恢复 mainline；需要 memory recovery 或 source calibration 时只标记支持需求，不把 Navigation 本身扩张成 Retrieval Policy。

------

## 2. Current Implementation Understanding

当前项目是 Reading Companion workspace，默认机制是 `attentional_v2`，`iterator_v1` 是 explicit fallback / legacy-compatible path。工作区由 backend 与 frontend 两个子应用构成，`BACKEND_READING_MECHANISM` unset 或 `attentional_v2` 时使用默认 deep-reading path，`iterator_v1` 可被显式选择为 fallback。 机制目录也明确把 `attentional_v2` 标为 current default/live mechanism，把 `iterator_v1` 标为 fallback。

共享 source truth 是 `public/book_document.json`。共享机制文档说明它是唯一 shared parsed-book truth，包含 canonical chapter order、paragraph records、sentence records、locators；paragraph layer 是稳定 shared source substrate；当前 `attentional_v2` 使用 paragraph + char-offset cursor，source citations 使用 inline paragraph-offset `SourceRef`，没有 shared Anchor Bank 或 SourceRef registry。

当前 `attentional_v2` 的 live loop 是：

```text
survey / reading_plan orientation
  → Navigate.choose_next_unit
  → Read
  → Reading Runner post-read settlement
  → cursor advance / audit / unit span ledger
  → chapter/session slow-cycle
```

`survey` 是 structural orientation。它产生 `chapter_zone` 与 `reading_plan`，当前支持 body-first scheduling：main body first，front/back support chapters deferred；它不做隐藏全文阅读，不产生 visible reactions，不写 durable reading memory，`Navigate` 也不拥有 book-level chapter ordering。`attentional_v2` 机制文档明确，Reading Runner 维护 paragraph-offset source cursor，`Navigate.choose_next_unit` 接收 adaptive preview 并返回 exact `end_anchor_text`；Runner 解析为 accepted `SourceSpan` 后调用 `Read`，再进行 settlement、audit、ledger、cursor advancement。

当前 source locus 由 `SourceCursor / SourceSpan / SourceRef` 承载。`source_spans.py` 定义 `SourceCursor` 为 `chapter_id / chapter_ref / paragraph_index / char_offset`，`SourceSpan` 为 end-exclusive range；`build_paragraph_offset_preview` 从当前 cursor 构造 adaptive preview；`resolve_end_anchor_text` 用 exact text match 把 `end_anchor_text` 解析成 `end_cursor`；`source_unit_from_span` 生成 accepted unit text 与 paragraph slices。 当前 `current-state.md` 也记录了这个切换：`Navigate.choose_next_unit` 看到 paragraph-offset preview，返回 `end_anchor_text`，Runner 解析 accepted span、推进 cursor、写入 `unit_span_ledger.jsonl`，且 SourceRef cutover 已落地。

`Navigate.choose_next_unit` 当前是唯一 live next-coverage-unit selector。它在 mainline mode 中从 visible preview 选择下一 readable unit；在 active detour mode 中可以选择 source-grounded already-read unit、请求 source skill，或 defer detour。Prompt 明确要求 mainline mode 不 request skills、不 defer；detour mode 只能选择 source-grounded already-read unit，或在证据不足时请求一个 source skill，或 honest defer。它不能请求 external web search，不能越过 `mainline_cursor` 读 future text。

当前 source skills 是 book-local source evidence layer。`source_map_overview` 返回 already-read book/chapter cards；`source_scope_drilldown` 把 scope 展开为更细 source cards；`source_window_fetch` 抓取 bounded visible sentence window。`source_skills.py` 中 `sentences_visible_to_mainline` 将可见范围限制在 mainline cursor 之前；range 不在 visible scope 中会返回错误。

`Read` 当前输出 `reading_impression / surfaced_reactions[] / memory_uptake_ops[] / detour_need?`。Read prompt 明确：`memory_uptake_ops` 只允许 target `active_attention / concept_registry / thread_trace`；surfaced reaction 已作为 reaction record 持久化，不能因为强烈就自动复制进 concept/thread；如果当前理解需要 detour，Read 只 emit `detour_need`，不能自己 route 或 resolve。

当前 `local_continuity` 已经是 Navigation / Planning state v0 的核心 carrier。`schemas.py` 中 `LocalContinuityState` 包含 `mainline_cursor / reading_queue_stage / active_detour_id / active_detour_need / detour_trace`；`DetourNeed` 有 `reason / target_hint / status`；`NavigateActResult` 支持 `choose_unit / request_skill / defer_detour`；`NavigateActTraceEntry` 支持 decision、selection mode、reason、skill request/result、resolution、budget state。 Runner 中 `_apply_detour_need` 会把 open detour 写入 `detour_trace` 并设置 `active_detour_id / active_detour_need`，resolved / abandoned 会更新 active pointer。

`state_projection.py` 构造 bounded prompt-facing packets：active attention digest、concept digest、thread digest、reflective frame digest、source_ref digest、recent reactions、continuation capsule、refs。它也提供 `build_navigation_context`，把这些压缩投影给 Navigate。 `read_context.py` 区分 `active_recall` 与 `look_back`：active recall 从 concept/thread/reaction records 取回未 carry 的 memory state；look_back 根据 SourceRef / SourceSpan 回到 earlier source excerpts。

当前 observability 已有 `unitization_audit / read_audit / settlement_audit`。`record_read` 记录 unit source span、carry_forward_ref_ids、context request、supplemental refs/steps、stop reason、budget exhaustion、reading impression、surfaced reactions、memory uptake ops、detour need；`record_settlement` 记录 op counts、target-store distribution 与 active_attention / concept_registry / thread_trace / reaction_records 的 compact ID deltas。 `storage.py` 定义了 mechanism-private artifacts，包括 `active_attention.json`、`concept_registry.json`、`thread_trace.json`、`reflective_frames.json`、`knowledge_activations.json`、`reaction_records.json`、`unit_span_ledger.jsonl`、`read_audit.jsonl`、`settlement_audit.jsonl`。

当前 visible reaction 可带 `prior_link / outside_link / search_intent`。`slow_cycle.py` 的 surfaced-native reaction record builder 会把这些字段保存在 durable reaction history，并通过 compatibility helper 派生旧 family labels。 它们是 visible trace semantics，不是成熟 visible route surface object，也不自动改变 navigation state。

Runtime artifacts boundary：本页读取了 GitHub 文档与核心代码，并使用 repo `current-state.md` 中记录的运行诊断摘要；本轮没有逐行打开真实运行目录中的 `read_audit.jsonl / settlement_audit.jsonl / unit_span_ledger.jsonl / detour_trace / active_attention.json / concept_registry.json / thread_trace.json / reaction_records.json`。因此，本文不声称已经独立验证 runtime quality；它只做 architecture-level、contract-level 与 assessment-level 设计判断。

------

## 3. Navigation Policy Core Definition

Reading Companion 中的 **Navigation Policy** 是：

> 对 `Navigate.choose_next_unit` 这一次 next-reading-unit decision 的 source-grounded、bounded、auditable policy contract。它规定在 current source cursor、visible preview、reading_plan orientation、mainline continuity、active detour state、source evidence、bounded memory projections 与 budget constraints 下，下一步应该继续主线、选择 detour unit、请求 source evidence skill、defer detour、restore mainline，或标记需要 active recall / look-back support。

它和 Planning Ontology 的关系是：Planning 是 reading path / attention / navigation support 的 territory；Navigation Policy 是 micro/meso 层当前最核心的 runtime policy。它不重新定义 Planning，只把已定义的 Planning 对象落到 `Navigate.choose_next_unit` 的决策纪律中。

它和 `Navigate.choose_next_unit` 的关系是：`Navigate.choose_next_unit` 是执行表面；Navigation Policy 是该表面必须遵守的选择规则、证据边界、reason vocabulary、state/trace边界与复杂度守门线。

Navigation Policy 不是 global planner。它不生成整本书路线，不重排 book order，不拥有 durable planning store，不做 planner-executor architecture，不做 tree search。它只为当前下一步 reading path 做 local decision。

Navigation Policy 不是 Visible Reading Route Surface Boundary。Internal navigation 是系统下一步实际读哪里；visible route disclosure 是未来可能展示或解释 Second Reader 自己路线的产品 surface。`Navigate` 不拥有 visible route surface object，不把 internal detour decision 自动变成用户可选择路线，也不把 visible reaction 当作 route control。

Navigation Policy 不是 Memory Retrieval Policy。它可以标记 `active_recall_needed` 或 `look_back_needed`，也可以消费 Memory Ontology 授权的 projections；但它不定义完整 retrieval taxonomy，不直接读取 durable stores，不执行 full recall / look-back policy，不写 memory。

Navigation Policy 通过四个约束保持 source-grounded、bounded、auditable：

```text
source-grounded:
  mainline selection 只能来自 visible source preview；
  detour selection 必须来自 already-read source evidence 或 source skill result；
  memory projection 不能替代 source evidence。

bounded:
  单次 Navigate 只选择下一 readable unit 或一个 source skill request / defer act；
  source skills 有 scope 与 budget；
  detour 有 origin、target_hint、status、stop reason。

auditable:
  decision、mode、reason、source evidence、memory refs、skill request/result、budget state、defer/restore reason 应形成 structured summary；
  不暴露 chain-of-thought。

settled:
  Navigate act 是 proposal；
  Runner / settlement 才解析 anchor、构造 SourceSpan、推进 cursor、写 state 与 audit。
```

明确排除：

```text
source corpus 不是 navigation state；
memory projection 不是 navigation decision；
visible reaction 不是 visible route disclosure；
visible route disclosure 不是 internal navigation；
audit trace 不是 runtime navigation context；
Navigate 不写 memory；
Navigate 不写 reaction_records；
Navigate 不拥有 durable planning store；
Navigate 不生成完整 book route；
Navigate 不调用 external search；
source skills 不成为 hidden search engine。
```

------

## 4. Navigation Policy Inputs and Outputs

### 4.1 Inputs

Navigation Policy v0 允许 `Navigate.choose_next_unit` 使用以下输入：

```text
current SourceCursor
  当前 paragraph-offset reading locus。

visible source preview
  从 current cursor 开始的 bounded preview；
  mainline mode 的 unit boundary 必须从这里选择。

reading_plan / survey orientation
  当前 chapter scheduling orientation，如 body_first、mainline_chapter_ids、deferred_chapter_ids；
  它是 structural prior，不是 hidden reading result。

mainline_cursor
  source-order mainline restore point；
  active detour mode 下尤其重要。

active detour state
  active_detour_id、active_detour_need、target_hint、origin cursor、detour_trace summary。

navigation context
  bounded packet，包括 active attention、concept/thread/reflective digest、source refs、continuation capsule 等。

bounded memory projections
  active_attention digest、concept digest、thread digest、reflective digest、recent reaction digest、knowledge activation projection、source_ref digest、continuation capsule。

source skill results
  source_map_overview / source_scope_drilldown / source_window_fetch 的 bounded source evidence。

constraints / budget
  act-loop budget、skill budget、preview boundary、no future text、no external search、chapter/session context。

current chapter/session context
  chapter_ref、reading_queue_stage、support/deferred status、recent unit continuity。
```

### 4.2 Outputs

Navigation Policy v0 的 legal outputs 是：

```text
choose next mainline unit
  以 end_anchor_text 指定当前 preview 中的下一 readable unit boundary。

choose detour unit
  在 active detour mode 中选择 source-grounded detour unit。

request source evidence skill
  请求一个 book-local source evidence skill，并说明 missing evidence reason。

defer detour
  诚实停止当前 detour localization attempt，记录 defer reason。

restore mainline
  标记 detour 已 resolved / abandoned / deferred 后恢复 mainline cursor；
  这可以作为 decision summary / settlement audit reason 表达，不必是新 node。

continue current mode
  mainline mode 下继续 source-order reading；
  detour mode 下继续 bounded detour localization loop，前提是 budget 与 evidence 支持。

active_recall_needed
  标记需要 memory recovery support；
  不直接执行完整 retrieval policy。

look_back_needed
  标记需要 source calibration support；
  不直接执行完整 look-back policy。

no-op / wait
  仅在 runner 当前没有 valid preview、source resolution pending、或 skill result pending 时可用；
  v0 默认不作为常规 Navigate act。

no_user_surface_needed
  当前 internal navigation 不需要生成用户可见建议。
```

每个 output 应携带：

```text
reason_summary
source_evidence_used
memory_refs_used
mode
uncertainty / evidence_need / budget_state, when relevant
audit_summary
```

这些是 structured decision summary，不是 hidden chain-of-thought。

------

## 5. Source-order Mainline Default

### 5.1 Core rule

Navigation Policy v0 的默认规则是：

> 没有明确 source-grounded exception 时，继续 source-order mainline。

这不是“保守不动”，而是把书的 authorial order 作为默认路径。书本主线通常承载定义、论证、叙事、铺垫与节奏；`Navigate` 的首要任务是把系统持续带过这个 source order，而不是把阅读改造成相关片段推荐流。

### 5.2 默认继续主线的条件

在 mainline mode 下，默认继续主线需要满足：

```text
current cursor valid；
visible preview sufficient；
没有 open detour 正在被 runner 激活；
当前 source move 可以形成一个 bounded readable unit；
没有必须先校准的 source uncertainty；
没有必须先恢复的 missing memory dependency；
没有 high-value, source-grounded, budget-appropriate detour exception。
```

其中 “没有 detour exception” 不等于没有好奇心。好奇、联想、outside_link、search_intent 可以成为 visible reading trace 或 future visible route disclosure candidate，但不能自动替代 source-order reading。

### 5.3 可以偏离主线的条件

偏离主线必须是 bounded exception。允许偏离的场景包括：

```text
active detour:
  已由 Read.detour_need 或后续 policy 授权；
  有 current source origin、reason、target_hint、budget、status。

look-back support:
  当前理解需要 source calibration；
  earlier SourceRef / SourceSpan 可定位；
  不改变 mainline path，除非后续 policy 将它升级为 detour。

active recall support:
  当前 unit 依赖 earlier reading state；
  所需 state 不在 carry-forward packet 中；
  它是 memory recovery，不是 source verification。

deep-dive:
  仅作为未来 Detour / Visible Reading Route Surface Boundary 的 bounded exception；
  v0 不设计完整 deep-dive policy。
```

### 5.4 偏离主线所需证据

偏离主线不能只靠“相关”或“有趣”。至少需要：

```text
current source trigger
  当前 accepted unit 或 visible preview 中有明确 pressure、reference、unresolved dependency、definition gap、thread callback。

source_scent
  有可定位 source evidence，或 source skill 能在 already-read boundary 内给出 evidence。

detour_value
  detour 可能修复当前理解缺口、澄清当前 source、恢复重要 thread、避免 FVI、或支持主线理解。

continuity_cost
  离开主线的成本可接受，且有 restore-mainline plan/reason。

budget
  act/skill budget 允许，并有 stop condition。

uncertainty
  不确定性足够影响当前阅读，而不是普通 curiosity。
```

### 5.5 Lightweight judgment language

v0 使用轻量判断语言，不做复杂评分模型：

```text
mainline_value
continuity_cost
detour_value
source_scent
uncertainty
evidence_need
budget
recovery_risk
```

这些 terms 用于 reason summary 与 audit / evaluation，不要求数字化。例子：

```text
reason_codes:
  mainline_continuity
  natural_boundary
  detour_scent_weak
  source_evidence_missing
  budget_exhausted
  restore_mainline
```

### 5.6 防止 novelty chasing

Navigation Policy v0 通过以下规则防止 novelty chasing：

```text
reaction digest 不能单独打开 detour；
knowledge activation 不能单独打开 detour；
outside_link / search_intent 不是 navigation target；
theme-only association 不能成为 detour source-grounding；
detour 必须有 target_hint、source_scent、budget、exit reason；
skill result 是 evidence，不是 route-disclosure output；
defer_detour 是合法且常常正确的结果；
restore_mainline reason 必须记录。
```

### 5.7 Support chapters / deferred chapters

Support chapters、preface、appendix、afterword 等不是“不可读”，也不是 unconditional mainline。Survey / reading_plan 已经提供 structural scheduling prior。Navigation Policy 只在 Runner 当前 scheduled chapter / source locus 内选择 unit；它不重排 book-level chapter order，也不把 deferred support chapter 当作 free detour target。若未来 Visible Reading Route Surface Boundary 想向用户展示“稍后读 support chapter”的建议，必须另行转译为 scaffold。

------

## 6. Decision Options

### 6.1 `continue_mainline`

应该继续主线，当：

```text
mode = mainline；
preview 可见且 cursor 有效；
当前 text 有自然 readable boundary；
没有 active detour；
当前 uncertainty 不阻塞继续阅读；
memory projection 只提示 continuity，不要求 recall/look-back；
detour_value 不足以克服 continuity_cost。
```

需要输入：current SourceCursor、visible preview、reading_plan orientation、navigation context、budget、chapter/session context。

不应继续主线，当：

```text
active_detour_need 已 open 且 runner 进入 active detour mode；
current preview source resolution 不可用；
当前 unit 依赖 missing definition/thread，且 active_recall/look_back 被后续 policy 判定为 blocking；
source evidence uncertainty 高到继续会放大 FVI；
source boundary 只能形成过长/过短且不可修复的 unit。
```

### 6.2 `choose_detour_unit`

应该选择 detour unit，当：

```text
mode = active detour；
active_detour_need 有 origin、reason、target_hint；
source evidence 已足够定位 already-read unit；
target unit 在 allowed source boundary 内，不越过 mainline_cursor；
detour_value 明确，source_scent strong enough；
unit 可通过 same Navigate → Read → settlement loop 正式读取。
```

Detour unit 必须满足：

```text
source-grounded；
bounded；
not future text；
not external web；
not hidden supplemental fetch；
not theme-only association；
可记录 source evidence used。
```

### 6.3 `request_source_evidence_skill`

应该请求 source skill，当：

```text
mode = active detour；
target_hint 有一定 source_scent，但 current evidence 不足以 choose unit；
缺的是 book-local source evidence，不是 LLM semantic judgment；
skill budget 允许；
request reason 能说明 missing evidence。
```

当前 skill policy：

```text
source_map_overview:
  当需要已读范围内的 coarse source map。

source_scope_drilldown:
  当已有 scope/card，但需要更细 source cards。

source_window_fetch:
  当已有 sentence range 或 card，需要 bounded source text。
```

Skill result 只能成为 evidence input。它不决定 target，不生成 route-disclosure output，不写 memory，不读 future text，不访问 external web。

### 6.4 `defer_detour`

应该 defer detour，当：

```text
source_scent weak；
target hint 只能形成 theme association；
detour_value 不足以抵消 continuity_cost；
skill budget exhausted；
source evidence missing 或 unavailable；
detour 会造成 recovery_risk；
当前更适合继续 mainline 等待 source 自己展开；
当前 detour 已不适合由 Navigation 解决，需后续 Visible Route Disclosure / Slow-cycle 判断是否保留为 display-only route trace candidate。
```

Defer 不是 abandon。`defer_detour` 是一次 navigation act：当前不继续定位或读取 detour。`abandoned` 是 detour state lifecycle：当前 detour need 被判断不再值得追。当前 schema 已有 `open / resolved / abandoned`，但没有 `deferred` state；v0 建议继续把 defer 作为 act decision 与 audit reason，是否新增 durable `deferred` status 留给 Detour Policy。

### 6.5 `restore_mainline`

应该恢复主线，当：

```text
detour unit 已被读取并解决 driving uncertainty；
Read 在 detour 中将 detour_need.status 置为 resolved；
detour 被 abandoned；
detour 被 deferred；
skill budget exhausted 且继续 detour 会损害 mainline continuity；
source_scent 不足；
active detour 读完一个 bounded unit 后没有新的 source-grounded detour need。
```

Restore-mainline reason 应表达：

```text
resolved_current_uncertainty
detour_value_satisfied
detour_scent_weak
budget_exhausted
avoid_detour_lingering
mainline_continuity_restored
```

Restore 不是“忘掉 detour”。它是把 path-control state 从 active detour 回到 `mainline_cursor`，同时把 outcome 留给 audit / detour_trace / settlement。

### 6.6 `active_recall_needed`

Navigation 可以标记需要 active recall，当：

```text
current preview / unit boundary depends on an earlier concept/thread/reaction；
bounded navigation context 没带足够 memory；
memory dependency 影响下一步 unit choice 或当前理解；
source evidence不足以说明“之前怎么理解过”。
```

但 Navigation 不执行完整 retrieval taxonomy。它只输出 structured support signal，后续由 Detour / Look-back / Active Recall Policy 或 read_context interface 处理。

### 6.7 `look_back_needed`

Navigation 可以标记需要 look-back，当：

```text
当前理解需要校准 earlier source；
memory projection 与 current source 可能冲突；
callback / definition / thread dependency 需要原文证据；
当前继续读会放大 source-grounding uncertainty。
```

Look-back 是 source calibration，不是 memory recovery，也不是 detour unit selection。Navigation v0 只标记需要，不设计完整 look-back trigger/exit policy。

### 6.8 `no_user_surface_needed`

Internal navigation 默认不需要 visible route disclosure。以下场景应显式允许 `no_user_surface_needed`：

```text
ordinary continue_mainline；
technical source skill loop；
low-value detour defer；
restore_mainline internal recovery；
active_recall/look_back internal support；
audit-only reason summary。
```

未来若要展示路线，只能由 Visible Reading Route Surface Boundary 把 settled route trace 转译为 source-grounded、低打扰的 route disclosure；它不能要求用户 approve、reject 或选择下一步路线。

------

## 7. Mainline Mode Policy

### 7.1 Mainline mode 的职责

Mainline mode 下，`Navigate.choose_next_unit` 的职责是：

> 从 current SourceCursor 开始的 visible preview 中，选择下一段最小但完整的 readable source unit，并返回 exact `end_anchor_text`。

它不决定是否普通 forward progression；普通 forward progression 是 Runner settlement 后的 deterministic default。它也不请求 source skills，不生成 route-disclosure output，不写 memory。

### 7.2 Unit boundary 合理性

合理 unit boundary 满足：

```text
starts at current cursor；
ends at a natural source boundary；
is large enough to carry one local reading move；
is small enough not to swallow multiple unrelated moves；
does not cross preview boundary；
does not cross chapter boundary；
preserves author structure；
does not cut off an unfolding definition / argument / scene / dialogue turn；
does not isolate a heading that is merely a label unless the heading itself is meaningful as a complete move。
```

Boundary examples：

```text
paragraph_end:
  ordinary default when one paragraph completes a local move。

intra_paragraph_semantic_close:
  paragraph unusually dense，句内/段内已经完成一个 definition、claim、contrast、turn。

cross_paragraph_continuation:
  heading + body, premise + immediate explanation, dialogue turn continuation, argument step continued across short paragraphs。

section_end:
  source section reaches a natural stop inside preview。

budget_cap:
  source move still unfolding but preview/guardrail requires bounded unit；must mark continuation_pressure。
```

### 7.3 为什么 `end_anchor_text` 必须来自 visible preview

`end_anchor_text` 是 LLM proposal 与 deterministic runner settlement 的桥。它必须来自 visible preview，因为：

```text
LLM 不应直接输出 raw offsets；
Runner 需要 deterministic exact-text resolution；
visible preview 是 mainline mode 唯一 source evidence；
如果 anchor 不在 preview 中，source boundary 无法审计；
如果 anchor paraphrase，Runner 无法可靠构造 accepted SourceSpan。
```

因此 v0 强化现有 prompt rule：`end_anchor_text` 必须逐字复制 preview 中的 tail quote，不得 paraphrase、补标点、加省略号。

### 7.4 避免过长 / 过短 unit

过短风险：

```text
heading-only label；
ornament/divider；
未完成的 definition；
单句 premise 被从 immediate elaboration 中切开；
dialogue/argument turn 被过早截断。
```

过长风险：

```text
多个 independent local moves 被吞成一段；
跨越 scene shift / section break；
把 current unit 变成 mini-summary target；
超出 Read 可产生清晰 impression / reaction / memory ops 的长度。
```

Policy：默认 paragraph-end；只有当 same local move clearly continues 时跨段；当 paragraph 内已经完成 strong move 时可 intra-paragraph close；当文字薄弱时不制造“深度”。

### 7.5 常见 source boundary cues

`Navigate` 可使用以下 visible source cues：

```text
section break / heading:
  weak structure cue；
  如果是 label，与下一 body paragraph 合并；
  如果 wording 本身完整，可 standalone。

dialogue break:
  角色/视角/turn change 可能形成 boundary；
  不切断 question-answer pair 或 reply chain。

argument step:
  一个 claim + support 完成时 boundary；
  若下一句仍在同一 premise 的 cash-out，应继续。

scene shift:
  时间/地点/视角明显转移可 boundary；
  但短 transition 可和后文合并。

definition boundary:
  term introduced + definition complete 可 boundary；
  definition 未完成时不得切开。
```

### 7.6 Memory projection 在 mainline mode 中的角色

Memory projection 可以：

```text
提醒当前 active_attention pressure；
提示某个 concept definition 可能需要 carry；
提示某个 thread continuity 正在延续；
提示 reflective frame 的 macro continuity；
提示 recent reaction 的 visible continuity；
提供 source_ref evidence spine。
```

Memory projection 不可以：

```text
override visible source boundary；
把 reaction digest 当 semantic truth；
把 knowledge activation 当 source truth；
打开 detour 的唯一理由；
替代 current source evidence；
让 Navigate 读取完整 durable memory store。
```

### 7.7 Mainline mode 可以提出的 support signals

Mainline mode 可以在 reason summary 中标记：

```text
active_recall_needed
  current preview depends on prior concept/thread not present in packet。

look_back_needed
  current preview requires source calibration。

possible_detour_signal
  current source introduces target_hint，但不在本次 mainline act 中直接跳转；
  是否 open detour 由 Read.detour_need 或后续 Detour Policy 管理。
```

Mainline mode 不应该：

```text
request source skills；
read future text；
run external search；
generate route-disclosure output；
write memory；
choose detour unit；
rewrite reading_plan；
dump audit trace into prompt。
```

------

## 8. Active Detour Mode Policy

### 8.1 Active detour 输入

Active detour mode 的最低输入：

```text
active_detour_need:
  reason
  target_hint
  status = open

origin / mainline cursor:
  detour 打开时的 mainline restore point

detour_trace summary:
  detour_id
  origin_cursor
  origin_target_hint
  status

navigation context:
  bounded memory projections and source refs

source evidence:
  already-read evidence
  skill results so far

budget:
  act count / skill count / stop reason
```

### 8.2 `target_hint` 如何使用

`target_hint` 是 localization hint，不是 target。Navigation 必须把它当作“需要找什么”的描述，而不是“已经知道读哪里”。

Allowed use：

```text
用 target_hint 指导 source_map_overview；
用 target_hint 判断哪个 source scope 需要 drilldown；
用 target_hint 检查 candidate source window 是否足够相关；
在 reason summary 中说明 detour_value。
```

Not allowed：

```text
把 target_hint 直接当 source evidence；
根据 target_hint 自由联想到未读文本；
根据 target_hint 打开 external search；
根据 target_hint 生成 route-disclosure output。
```

### 8.3 Detour localization 如何 source-grounded

Detour localization 必须满足：

```text
candidate unit 在 already-read / visible-to-mainline boundary 内；
candidate unit 来自 source skill result 或 existing source refs；
candidate unit 有 source id / sentence range / source span evidence；
candidate unit 与 active_detour_need 的 relation 可简要说明；
candidate unit 不只是 theme similarity。
```

### 8.4 什么时候 choose detour unit

Choose detour unit，当：

```text
source_evidence_sufficient；
detour_value_high；
continuity_cost acceptable；
unit boundary natural；
budget available；
choosing this unit likely resolves / clarifies / rejects current detour need。
```

Chosen detour unit 一旦确定，必须走同一 loop：

```text
Navigate.choose_next_unit
  → Runner resolves / constructs accepted SourceSpan
  → Read
  → settlement
  → detour state update
  → restore or continue according to settled state
```

不能把 detour 当作 hidden supplemental fetch 直接塞进 Read prompt。

### 8.5 什么时候 request skill

Request skill，当：

```text
source_evidence_missing 但 source_scent plausible；
需要从 chapter cards 到 section/window cards；
需要 bounded source text 才能判断；
skill budget 尚未耗尽。
```

Skill request 必须记录：

```text
skill_name
missing_evidence_reason
arguments
budget_state
source boundary
```

### 8.6 什么时候 defer

Defer，当：

```text
source_scent_weak；
skill_result 不足；
budget_exhausted；
candidate 只是 theme-only association；
detour_value_low；
continuity_cost_high；
继续 detour 可能导致 detour_lingering。
```

Defer reason 应短、结构化、可审计。

### 8.7 什么时候 abandon

Abandon 是 detour lifecycle decision，不是单次 Navigate act 的默认输出。应在以下情况下由 Read / Runner / Detour Policy 处理：

```text
detour target 被 source evidence 证明不相关；
driving uncertainty 已自然消失；
active detour 读后反而证明不值得继续；
detour 多次 weak scent / budget exhausted 且没有可恢复价值。
```

v0 不完整设计 abandon trigger，但要求 Navigation 不把 `defer_detour` 偷偷写成 abandon state。

### 8.8 什么时候 restore mainline

Restore mainline，当：

```text
detour resolved；
detour abandoned；
detour deferred；
detour read one bounded unit 后没有新 active need；
skill budget exhausted；
source_scent_weak；
continuity_cost 开始超过 detour_value。
```

Restore-mainline reason 必须可审计，避免 detour lingering。

### 8.9 Active detour mode 不做什么

Active detour mode 不得：

```text
自由搜索；
读 future text；
调用 external web search；
根据 prior knowledge 单独选 target；
根据 reaction digest 单独选 target；
把 source skills 当 semantic relevance engine；
把 detour target 直接表述成 user route guidance；
绕过 Read / settlement；
形成 long detour route plan。
```

------

## 9. Source Evidence Skill Policy

Source skills 是 **book-local source evidence providers**。它们的职责是给 Navigate 提供可定位的 source evidence，不是替 Navigate 做判断。

v0 规定：

```text
source skills 只读 book substrate 与 allowed runtime state；
source skills 不做 semantic relevance judgment；
source skills 不读 future text；
source skills 不访问 external web；
source skills 不生成 memory；
source skills 不生成 route-disclosure output；
source skills 不改变 navigation state；
source skills 不选择 detour target。
```

Skill request 必须有 missing evidence reason：

```text
source_evidence_missing:
  当前 evidence 不足以定位 target。

source_scope_too_coarse:
  需要从 chapter-level card drilldown。

source_text_needed:
  需要 bounded source window 才能判断 unit boundary。
```

Skill result 的使用规则：

```text
结果只能作为 Navigate 的 evidence input；
结果必须受 budget 限制；
结果不足时可 defer；
结果强时可 choose detour unit；
skill history 不自动成为 runtime navigation context；
skill budget 与 stop reason 需要 audit。
```

当前已有或允许的 skills：

```text
source_map_overview
  返回已读范围内 chapter/source cards。

source_scope_drilldown
  从 current scope card/range 展开到更细 source cards。

source_window_fetch
  抓取 bounded already-read sentence/source window。
```

------

## 10. Memory Projection Use in Navigation

Navigation 只能使用 Memory Ontology 授权的 bounded typed source-ref-preserving projections。它不能直接读取完整 durable memory stores，不能读取 audit dump，不能把 projection 当 authoritative state。

### 10.1 `active_attention digest`

Use for：

```text
当前 hot reading pressure；
near-term question / tension / focus；
是否存在 active_attention_pressure；
是否可能需要 recall / look-back / detour defer。
```

Do not use for：

```text
把 hypothesis 当 settled truth；
单独打开 detour；
覆盖 visible source boundary。
```

### 10.2 `concept digest`

Use for：

```text
definition_dependency；
current preview 是否依赖 earlier definition/model/classification；
是否需要 active_recall_needed 或 look_back_needed。
```

Do not use for：

```text
替代 source text；
把 concept summary 当 exhaustive source truth。
```

### 10.3 `thread digest`

Use for：

```text
thread_continuity；
判断当前 mainline move 是否延续 earlier line；
判断 detour_value 是否真实服务主线 thread。
```

Do not use for：

```text
theme-only association；
把 thread 名称当 detour evidence。
```

### 10.4 `reflective digest`

Use for：

```text
chapter/session macro continuity；
current support chapter / main body orientation；
判断某些 high-level frame 是否应保持在 background。
```

Do not use for：

```text
生成 global route；
替代 slow-cycle；
替代 source evidence。
```

### 10.5 `recent reaction digest`

Use for：

```text
visible continuity；
callback awareness；
避免重复 visible surface；
理解用户可见 trace 的节奏。
```

Do not use for：

```text
semantic navigation justification；
detour target selection 的唯一理由；
visible route disclosure justification 的唯一理由。
```

### 10.6 `knowledge activation projection`

Use for：

```text
标记 prior/external knowledge warrant；
提醒 source trigger 可能涉及外部 reference；
在 reason 中作为 secondary support。
```

Do not use for：

```text
把 prior knowledge 当 book truth；
单独打开 detour；
单独生成 visible route disclosure；
绕过 current source evidence。
```

### 10.7 `source_ref digest`

Use for：

```text
evidence spine；
定位 look-back source；
支撑 source-grounded reason summary。
```

Do not use for：

```text
当作完整 source corpus；
当作 full memory store。
```

### 10.8 `continuation capsule`

Use for：

```text
resume / re-entry continuity；
recent local context；
bounded carry-forward of active focus。
```

Do not use for：

```text
完整 plan；
完整 memory；
audit trace replay。
```

### 10.9 `active_recall_needed` vs `look_back_needed`

```text
active_recall_needed:
  需要恢复之前形成的 reading memory state。
  问题是“之前我们怎样理解 / 追踪过它？”

look_back_needed:
  需要回到 earlier source text 校准。
  问题是“原文到底怎么说？”
```

Retrieved memory / projection 若进入 navigation reason，应记录 `memory_refs_used`。Look-back source 若进入 reason，应记录 `source_evidence_used`。二者不得混用。

------

## 11. Interaction with Read / Runner / Settlement

Navigation / Read / Runner / Settlement 的职责分工固定如下：

```text
Navigate:
  决定下一步读哪里；
  在 mainline mode 选择 next unit；
  在 active detour mode 定位 detour unit、request skill、或 defer；
  可以标记 recall/look-back support need；
  不写 memory；
  不写 reactions；
  不直接写 route-disclosure output；
  不推进 cursor。

Read:
  决定 accepted unit 读出了什么；
  输出 reading_impression；
  输出 surfaced_reactions；
  输出 memory_uptake_ops；
  可输出 detour_need；
  不定位 detour target；
  不决定下一 route；
  不写 final persisted object。

Runner:
  构造 visible preview；
  调用 Navigate；
  dispatch source skills；
  解析 end_anchor_text；
  构造 accepted SourceSpan；
  调用 Read；
  调用 settlement/state_ops；
  推进 cursor；
  更新 local_continuity；
  写 ledger / audit / checkpoint。

Settlement / state_ops:
  绑定 SourceRef；
  normalize operations；
  apply memory_uptake_ops；
  persist surfaced reactions；
  update detour state；
  record audit outcome。
```

普通 forward progression 是 deterministic default。`Navigate` 不需要也不应该生成 `forward` action。它提出的 `choose_unit / request_skill / defer_detour` 是 proposal；Runner / settlement 才改变 source cursor、local continuity、durable state 与 audit artifacts。

------

## 12. Navigation Reason Vocabulary

Navigation Policy v0 使用轻量 structured reason vocabulary。它服务 audit / evaluation，不是 chain-of-thought，也不是复杂 numerical scoring model。

Core reason codes：

```text
mainline_continuity
natural_boundary
author_structure_preserved
heading_merged_with_body
definition_dependency
thread_continuity
active_attention_pressure
source_calibration_needed
memory_recovery_needed
possible_detour_signal
detour_value_high
detour_scent_weak
detour_deferred_low_value
detour_deferred_high_continuity_cost
budget_exhausted
restore_mainline
source_evidence_missing
source_evidence_sufficient
skill_result_insufficient
avoid_novelty_chasing
theme_only_association_rejected
knowledge_activation_secondary_only
recent_reaction_continuity_only
support_chapter_deferred
no_user_surface_needed
```

Structured summary shape can be:

```text
decision
selection_mode
reason_codes[]
reason_summary
source_evidence_used[]
memory_refs_used[]
uncertainty
evidence_need
budget_state
restore_or_defer_reason
```

No hidden reasoning text is required. The reason vocabulary should support later Planning Audit / Evaluation dimensions such as Mainline Continuity、Navigation Groundedness、Detour Precision、Recovery Quality、Overplanning / Thrashing。

------

## 13. Navigation State and Trace Boundary

### 13.1 State

Navigation state v0 is primarily carried by `local_continuity`:

```text
mainline_cursor
reading_queue_stage
active_detour_id
active_detour_need
detour_trace
```

v0 不新增 durable planning store。Current `local_continuity` 已足够表达 mainline restore point、active detour pointer、detour trace 与 queue stage。新增 store 必须由后续 Visible Route Disclosure / Slow-cycle / Audit 的真实需求证明。

### 13.2 Trace

Navigation trace 是 diagnostic artifact：

```text
NavigateActTraceEntry
unitization_audit
read_audit
settlement_audit
debug events
skill request/result trace
```

Trace 不等于 state，不等于 memory，不等于 user-facing rationale。Rejected alternatives、failed resolution、budget exhaustion details、skill history、debug events 默认不进入 prompt。

### 13.3 Trace 不自动回流 prompt 的原因

```text
contamination:
  把诊断噪声变成阅读理由。

self-reinforcement:
  让系统追随上一轮失败 rationale。

legibility leak:
  把 internal trace 误当成 user-facing explanation。

novelty drift:
  让 rejected detours 反复诱发新 detours。
```

因此 v0 只允许当前 act loop 内的 skill results 作为 evidence 回传；历史 trace 不自动进入后续 Navigate prompt。

### 13.4 未来 planning obligations store

未来若出现以下真实需求，才考虑新增 lightweight planning obligations store：

```text
multiple concurrent detours 成为常态；
future visible route surface display preference / suppression state 需要跨会话追踪；
slow-cycle macro obligations 超出 active_attention carry-forward 能表达的范围；
planning audit 需要 replayable path state，而非 diagnostic trace。
```

这不进入 v0。

------

## 14. Internal Navigation vs Visible Route Disclosure

Internal navigation 是系统下一步实际读哪里。它发生在 `Navigate.choose_next_unit → Read → settlement` 内部 loop 中。它不需要每次展示给用户。

Visible route disclosure 是可见、低打扰的产品展示面。它可以展示 Second Reader 继续主线、回看、暂缓 detour、恢复主线或带着某个 focus 继续读的路线痕迹。但它必须由 Visible Reading Route Surface Boundary 设计，不由 `Navigate` 直接生成，也不让用户选择下一步路线。

明确边界：

```text
Navigate 不拥有 visible route surface object；
visible reaction 不是 route control；
prior_link 不是 route control；
outside_link 不是 route control；
search_intent 不是 route control；
internal detour decision 不等于 visible route disclosure；
no_user_surface_needed 是合法输出。
```

如果未来要展示 route disclosure note，必须经过 Visible Reading Route Surface Boundary 转译为：

```text
source-grounded；
低打扰；
不替代 source-order reading；
不暴露 hidden navigation trace；
不创建 accept/reject/skip route state；
不把 visible surface 变成 route steering。
```

------

## 15. Complexity Guardrails

Navigation Policy v0 明确不进入以下方向。

不新增 large planner node。当前短板是 policy、reason、audit、detour boundary，而不是缺一个更大的 planner。大 planner 会把边界不清的问题包进更难诊断的黑箱。

不做 multi-agent reading team。Reading Companion 的产品需要一个连贯的 co-reading mind，而不是 navigator agent、memory agent、critic agent、route-disclosure agent 的角色拼盘。

不做 graph workflow rewrite。可借 checkpoint、interrupt、trace 等思想；但当前 Reading Runner 已是 deterministic orchestration authority。工作流迁移不能替代 reading judgment。

不把 ToT / LATS / MCTS 作为默认 next-unit decision。Search-based deliberation 适合 hard passage / optional deep-dive，不适合普通 source-order reading loop；它成本高、reward function 不稳定、会破坏 mainline continuity。

不做 full planner-executor architecture。当前只有局部 selector + deterministic runner，不需要把每步阅读变成 plan decomposition。

不让 visible route disclosure 替代 source-order reading。Visible route disclosure 是 optional display-only route legibility surface，不是 reading path owner。

不暴露全部 navigation reasoning 给用户。Audit 需要 structured summary，不需要 chain-of-thought；用户 surface 需要 concise rationale，不需要 internal trace dump。

不合并 planning state 与 memory state。Planning state 是 path-control obligations；Memory state 是 source-grounded understanding。

不让 Navigate 写 memory。Memory formation 与 settlement 已经有独立 contract。

不让 Navigate 执行 external search。Broad prior knowledge 可参与阅读，但不能成为 hidden search-driven navigation。

不让 source skills 成为 hidden search engine。它们是 book-local source evidence providers，不是 relevance agents。

不做 complex learning path engine / full learner model。Reading Companion 当前不是 tutoring system，也没有 mastery/prerequisite graph。

不让 slow-cycle 接管 Navigation Policy。Slow-cycle 可 carry-forward / consolidate，但不拥有 immediate next-unit selection。

不写 Codex implementation roadmap。本页只给 policy 与 readiness notes。

------

## 16. What This Design Changes or Tightens

### 16.1 Preserved

本设计保留：

```text
attentional_v2 as current default；
Navigate.choose_next_unit；
mainline / active detour 同一入口；
paragraph-offset SourceCursor / SourceSpan；
end_anchor_text → deterministic resolution；
Read → Runner settlement；
local_continuity as v0 planning-state carrier；
book-local source skills；
state_packet / navigation context projections；
read_audit / settlement_audit / unitization audit；
chapter-end slow-cycle。
```

### 16.2 Tightened

本设计收紧：

```text
source-order mainline default；
detour 必须是 bounded exception；
source skill request 必须有 missing evidence reason；
defer_detour 是合法且可审计结果；
restore-mainline reason 必须记录；
memory projection 只能 secondary support；
reaction digest 不能单独 justify navigation；
knowledge activation 不能单独 open detour 或 visible route disclosure；
navigation trace 不自动进入 runtime prompt；
visible route disclosure 不混入 Navigate；
Navigate 不写 memory。
```

### 16.3 Reinterpreted / renamed

```text
Navigate.choose_next_unit:
  policy-governed source-grounded next-unit selector / detour localizer。

source skills:
  source evidence providers, not search tools。

defer_detour:
  navigation act decision, not necessarily durable detour status。

restore_mainline:
  required detour-exit reason, not a separate planner node。

reason:
  structured audit summary, not chain-of-thought。
```

### 16.4 Deferred

以下内容延后：

```text
full Detour / Look-back / Active Recall trigger/exit policy；
Visible route surface object and UX policy；
Memory Retrieval / Utilization taxonomy；
Planning Audit full schema；
Planning Evaluation rubric；
Slow-cycle / Macro-planning matrix；
Implementation Handoff；
Codex task list。
```

------

## 17. Downstream Interface Summary

### Detour / Look-back / Active Recall Policy

本页提供三分法边界：detour 是 path deviation，look-back 是 source calibration，active recall 是 memory recovery。后续页面需要定义 trigger、exit、budget、restore-mainline、failure reason，但必须保持 detour 走同一 read loop。

### Visible Reading Route Surface Boundary

本页只规定：internal navigation 不等于 visible route disclosure；`Navigate` 不拥有 visible route surface object；visible reaction / prior_link / outside_link / search_intent 不是 route control。未来 route disclosure 必须 derived from settled route trace、source-grounded、低打扰，并且不能改变 navigation state。

### Planning Audit / Observability

本页提供 decision options、reason vocabulary、source evidence used、memory refs used、budget/defer/restore reason。后续 Audit 页面可据此定义 schema，但不能要求 chain-of-thought。

### Planning Evaluation

本页提供后续 metrics 的 policy basis：mainline continuity、navigation groundedness、detour precision、recovery quality、overplanning / thrashing、planning-memory alignment。具体 rubric 延后。

### Memory Retrieval / Utilization

本页只允许 Navigation 标记 `active_recall_needed / look_back_needed`，不设计完整 retrieval taxonomy。后续 Retrieval 页面必须保持 source_ref-preserving、bounded、intent-aware。

### Slow-cycle / Macro-planning

本页规定 slow-cycle 不接管 `Navigate.choose_next_unit`。它可以 carry-forward focus、cool/resolve active items、prepare macro obligations，但不能生成 full book route 或替代 source-order mainline。

### Implementation Handoff

本页不是 handoff。它只说明哪些 policy pieces 已足够窄，可进入小窗口验证；完整 implementation plan 留给后续 Handoff。

------

## 18. Implementation Readiness Notes

### Ready for narrow implementation

以下内容可以作为小窗口实现验证候选：

```text
structured navigation reason vocabulary；
explicit mainline vs detour mode logging；
skill request reason tightening；
defer_detour reason tightening；
restore-mainline reason logging；
navigation audit summary enrichment；
source_evidence_used / memory_refs_used compact fields；
budget / stop reason enrichment for Navigate act loop。
```

这些都是 logging / prompt / trace contract 级别收紧，不引入新 planner。

### Needs Detour / Look-back / Active Recall Policy first

```text
full detour trigger / exit state machine；
defer vs abandon durable status；
active_recall_needed operational trigger；
look_back_needed operational trigger；
multi-step recovery after failed detour。
```

### Needs Visible Reading Route Surface Boundary first

```text
visible route surface display shape；
visible reading note wording；
display preference / suppression, if needed；
route trace disclosure rules；
route-disclosure persistence, if needed。
```

### Needs Planning Audit first

```text
final navigation audit schema；
candidate/rejected alternative summary policy；
per-decision replay format；
trace retention and projection gates。
```

### Needs Planning Evaluation first

```text
Reading Path Quality rubric；
Mainline Continuity metric；
Detour Precision / Recovery Quality metric；
Overplanning / Thrashing metric；
Visible Route Disclosure Readiness metric。
```

### Needs Memory Retrieval / Utilization first

```text
retrieval intent taxonomy；
active recall query construction；
look-back source calibration budget；
memory utilization trace。
```

### Explicitly not now

```text
large planner node；
multi-agent reading team；
graph workflow rewrite；
ToT / LATS / MCTS default loop；
full learner model；
complex learning path engine；
external search navigation；
vector/graph retrieval migration as Navigation work；
Codex implementation roadmap。
```

------

## 19. Optional Open Questions

1. **`defer_detour` 是否应成为 durable detour status？**
   现在不能在 Navigation Policy 中关闭，因为当前 schema 支持 `open / resolved / abandoned`，而 defer 更像 act decision。它依赖 Detour Policy 与 Planning Audit。它不阻塞本页设计。
2. **Navigation audit 是否应记录 rejected alternatives？**
   本页只要求 structured reason summary。是否记录低成本 rejected alternative classes，依赖 Planning Audit / Evaluation。它不阻塞小窗口 logging 收紧。
3. **`active_recall_needed / look_back_needed` 应从 Navigate 还是 Read-context 发起？**
   当前实现中 `read_context.py` 已有 active_recall / look_back helper；Navigation v0 只允许标记 support need。完整 trigger/placement 依赖 Detour / Look-back / Active Recall Policy 与 Memory Retrieval / Utilization，不阻塞本页。

# Navigation Policy Design v0 — Tightening Patch

## Patch 1: Navigation outputs 分层

替换原第 4 节中 “Navigation Policy outputs / legal outputs” 的写法。

### Revised rule

Navigation Policy v0 的 **actual Navigate act outputs** 只有三种：

```
NavigateActResult.decision:
  choose_unit
  request_skill
  defer_detour
```

其他内容不是新的 Navigate act type。它们必须分层处理：

```
A. Canonical NavigateActResult
  choose_unit
  request_skill
  defer_detour

B. Support / audit flags
  active_recall_needed
  look_back_needed
  possible_detour_signal
  no_user_surface_needed

C. Runner / settlement effects
  restore_mainline
  cursor advancement
  detour_trace update
  active_detour pointer update

D. Audit-only structured fields
  reason_summary
  reason_codes[]
  source_evidence_used[]
  memory_refs_used[]
  budget_state
  uncertainty
```

### Design consequence

`active_recall_needed / look_back_needed / possible_detour_signal / no_user_surface_needed` 可以出现在 reason codes、audit summary、read_context hint 或 future policy input 中，但它们 **不是** `NavigateActResult.decision`。

`restore_mainline` 不是 Navigate output。它是 Runner / local_continuity settlement effect。

`no-op / wait` 不是常规 Navigate act。它是 runner/system condition，只能由 system fallback 或 runner pending state 处理。

### Implementation caution

不要为了容纳 support flags 而扩展：

```
NavigateActDecision
NavigateActResult.decision
NavigateActTraceEntry.decision
```

v0 应继续保持 canonical act set：

```
choose_unit | request_skill | defer_detour
```

这与当前 Planning Ontology 中 `Navigate.choose_next_unit` 是 next-unit selector / detour localizer，而不是 global planner 或 visible route disclosure owner 的结论一致。

------

## Patch 2: `defer_detour` 的状态后果收紧

替换原 `defer_detour` 小节中较宽的表述。

### Revised rule

`defer_detour` 是一个 **Navigate act decision**，不是 durable detour lifecycle status。

它不应 silent become `abandoned`。当前 durable detour status 仍以既有 schema 为准：

```
open
resolved
abandoned
```

但 `defer_detour` 不能只是 free-text reason，否则 active detour 下一轮会再次被激活并循环 defer。因此 v0 对它给出两层规则。

### Policy-level effect

当 Navigate 返回 `defer_detour` 时，Runner / local_continuity 层至少应形成 bounded effect：

```
write defer_reason to navigation / detour trace;
restore mainline for at least the next mainline unit;
prevent immediate reattempt of the same detour in the next Navigate call without a new source trigger;
leave durable deferred status unresolved until Detour Policy.
```

### Implementation readiness

v0 只将以下部分标为 ready for narrow implementation：

```
defer_detour reason logging
budget_state logging
source_evidence_missing / detour_scent_weak reason logging
```

以下行为不应在 Navigation Policy 页面内直接实现为完整状态机：

```
deferred durable status;
same-detour cooldown rules;
reattempt gating;
defer → abandon transition;
multi-detour queue.
```

这些必须等待 Detour / Look-back / Active Recall Policy。

### Practical v0 fallback

如果当前 Runner 尚不能安全支持 “restore mainline for at least one unit / prevent immediate reattempt”，则 `defer_detour` 的 behavior-level implementation 应暂缓，只实现 audit/logging，不把它当作完整可运行状态机。

------

## Patch 3: `restore_mainline` 降级为 Runner / settlement effect

替换原文中把 `restore_mainline` 放进 Navigation output 的所有表述。

### Revised rule

`restore_mainline` is not a `NavigateActResult`.

它是 Runner / local_continuity settlement effect，基于：

```
defer_detour
detour_need.status = resolved
detour_need.status = abandoned
budget_exhausted
source_evidence_missing
detour_value_satisfied
detour_scent_weak
```

由 Runner 记录并应用。

### Navigate may provide

Navigate 可以提供：

```
defer_detour reason;
source_evidence_missing reason;
detour_scent_weak reason;
detour_value_satisfied reason;
budget_exhausted reason;
```

### Runner records

Runner / settlement 决定并记录：

```
restore_mainline: true / false
restore_reason
restored_cursor = mainline_cursor
detour_id
defer_reason or close_reason
```

### Design consequence

Navigation Policy 不新增 `restore_mainline` act。它只要求 detour exit / defer / close 后必须有 restore reason，以避免 detour lingering。

------

## Patch 4: `active_recall_needed / look_back_needed` 降级为 support flags

替换原文中 “legal outputs: active_recall_needed / look_back_needed” 的写法。

### Revised rule

`active_recall_needed` 和 `look_back_needed` 在 v0 中是 **support flags / audit flags**，不是 operational triggers。

它们可以出现于：

```
reason_codes[]
reason_summary
audit summary
read_context request hint
future Detour / Look-back / Active Recall Policy input
```

它们不能单独触发：

```
execute retrieval;
execute look_back;
alter navigation state;
open detour;
create visible route disclosure;
request source skill;
change cursor.
```

### Meaning boundary

```
active_recall_needed:
  “当前选择/理解可能需要恢复 earlier reading state。”
  It is memory recovery support.

look_back_needed:
  “当前选择/理解可能需要回到 earlier source text 校准。”
  It is source calibration support.
```

这继承 Memory Ontology 中 active_recall 是 memory recovery、look_back 是 source calibration、detour 是 planning path deviation 的区分。

### Implementation consequence

Navigation v0 可以记录这些 flags，但不实现完整 recall / look-back trigger policy。完整触发、预算、source selection、retrieval result utilization 与 exit condition 均延后。

------

## Patch 5: Reason vocabulary 拆成 MVP 与 extended

替换原第 12 节 reason vocabulary。

### MVP reason codes

Implementation handoff 只应优先使用 MVP subset：

```
mainline_continuity
natural_boundary
author_structure_preserved
definition_dependency
thread_continuity
source_calibration_needed
memory_recovery_needed
active_detour_open
source_evidence_missing
source_evidence_sufficient
detour_value_high
detour_scent_weak
detour_deferred_low_value
budget_exhausted
restore_mainline
avoid_novelty_chasing
theme_only_association_rejected
no_user_surface_needed
```

### Extended / v0.2 reason codes

以下可以保留在设计文档中，但不应进入第一轮 implementation handoff：

```
heading_merged_with_body
possible_detour_signal
detour_deferred_high_continuity_cost
skill_result_insufficient
knowledge_activation_secondary_only
recent_reaction_continuity_only
support_chapter_deferred
recovery_risk
```

### Rule

Reason vocabulary 是 structured audit summary，不是 scoring model，也不是 chain-of-thought。第一轮实现不应引入复杂 enum explosion。

------

## Patch 6: Mainline `choose_unit` 最小字段化

在 Mainline Mode Policy 后增加 “minimal structured fields”。

### Mainline choose_unit minimal fields

Mainline mode 下，`Navigate.choose_next_unit` 的最小 structured output 应是：

```
decision = choose_unit
selection_mode = mainline
end_anchor_text
boundary_type
reason_codes[]
reason_summary
continuation_pressure
source_evidence_used[]
memory_refs_used[]
uncertainty
```

其中：

```
decision:
  must be choose_unit in mainline mode.

selection_mode:
  must be mainline.

end_anchor_text:
  exact quote from visible preview.

boundary_type:
  controlled vocabulary, not free text.

reason_codes:
  MVP subset preferred.

source_evidence_used:
  current preview / paragraph slice / source quote references.

memory_refs_used:
  bounded projection refs only, if any.

uncertainty:
  short structured marker, not hidden reasoning.
```

### Mainline boundary_type v0

第一轮只使用当前可控边界类型：

```
paragraph_end
intra_paragraph_semantic_close
cross_paragraph_continuation
section_end
budget_cap
```

这些与当前 `UnitizeBoundaryType` contract 保持一致，不新增复杂 boundary taxonomy。

### Design consequence

Codex 不应只实现 free-text `reason`。即使当前 schema 只支持 `reason: str`，audit enrichment 也应朝 structured summary 靠拢，而不是扩 act type。

------

## Patch 7: `no-op / wait` 移出常规 policy

删除原文中将 `no-op / wait` 列为 legal Navigation output 的表述。

### Revised rule

`no-op / wait` is not a normal Navigate act.

它只属于 runner/system condition，例如：

```
preview unavailable;
source resolution pending;
skill result pending;
runtime pause;
checkpoint/resume boundary;
system fallback after invalid LLM output.
```

LLM Navigate 不应在正常 reading loop 中输出 `wait`。否则模型可能在不确定时停住 loop，而不是选择 source-grounded unit、请求 skill 或 defer detour。

### Implementation consequence

不要把 `wait` 加入：

```
NavigateActDecision
NavigateActResult.decision
Navigate prompt legal act list
```

如果系统级 fallback 需要 wait，应由 Runner 自己处理，而不是交给 LLM 决定。

------

## Patch 8: Implementation readiness notes 同步收紧

替换原 Implementation Readiness Notes 中与行为相关的部分。

### Ready for narrow implementation

仍然 ready：

```
structured navigation reason vocabulary MVP subset
explicit mainline vs detour mode logging
skill request reason tightening
defer_detour reason logging
restore-mainline reason logging
navigation audit summary enrichment
source_evidence_used / memory_refs_used compact fields
budget / stop reason enrichment
mainline choose_unit minimal fields
```

### Not ready as behavior-level implementation

暂不 ready：

```
defer_detour durable state machine
defer_detour cooldown / reattempt gating
defer → abandon transition
active_recall_needed operational trigger
look_back_needed operational trigger
restore_mainline as Navigate output
no-op / wait as LLM act
full detour lifecycle policy
visible route surface object
retrieval taxonomy
planning evaluation rubric
```

### Implementation boundary

第一轮实现应是：

```
log clearer;
summarize clearer;
audit clearer;
do not expand planner;
do not expand NavigateActDecision;
do not implement full recall/look-back/detour state machine prematurely.
```

------

## Patch 9: Revised canonical output section summary

可以把第 4 节最后压成以下结论：

```
Navigation Policy v0 does not expand the Navigate act space.

The only canonical NavigateActResult decisions are:

  choose_unit
  request_skill
  defer_detour

All other labels are either support flags, runner/settlement effects, or audit-only fields.

Support flags:
  active_recall_needed
  look_back_needed
  possible_detour_signal
  no_user_surface_needed

Runner / settlement effects:
  restore_mainline
  cursor advancement
  detour_trace update
  active_detour pointer update

Audit-only fields:
  reason_codes
  reason_summary
  source_evidence_used
  memory_refs_used
  budget_state
  uncertainty

This keeps Navigate as a bounded next-unit selector / detour localizer, not a global planner, retrieval executor, visible route disclosure owner, or memory mutator.
```

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

### A.1 Product and project boundary

`docs/product-overview.md` 定义 Reading Companion 是一个 genuinely curious, self-propelled co-reading mind；它不是 summary engine，也不是 service-style assistant；它必须 text-grounded、legible、valuable to another person。 这支持正文把 Navigation 限定为 source-grounded reading path control，而不是 route-disclosure flow、generic assistant steering 或 task planner。它是稳定产品约束，不只是当前实现事实。

`docs/source-of-truth-map.md` 说明 workspace 是 repo-first，durable current state 应进入 canonical repo docs / state files，而不是 chat scratch。 这支持本页把 Navigation Policy 写成可沉淀机制设计，而不是临时 prompt patch。

### A.2 Shared source substrate and mechanism status

`docs/backend-reading-mechanism.md` 说明 `public/book_document.json` 是唯一 shared parsed-book truth；paragraph layer 是稳定 source substrate；`attentional_v2` 使用 paragraph + char-offset cursor；source citations 使用 inline paragraph-offset SourceRef；没有 shared Anchor Bank 或 SourceRef registry。 这支持正文中的 “source corpus is not navigation state / memory / plan” 与 “mainline mode 只能从 visible preview 选 boundary”。

`docs/backend-reading-mechanisms/README.md` 把 `attentional_v2` 标为 current default/live mechanism，`iterator_v1` 标为 fallback。 这支持本页不做 greenfield redesign，而是在 `attentional_v2` 上收紧 `Navigate.choose_next_unit`。

### A.3 `attentional_v2` mechanism facts

`docs/backend-reading-mechanisms/attentional_v2.md` 说明 `Reading Runner` owns the live loop around `Navigate.choose_next_unit`、`Read`、post-read settlement、cursor advancement、detour state handoff 与 mechanism-private persistence；也说明 `Navigate.choose_next_unit` 是 sole current selector，mainline unitization 与 detour localization 是同一 entrypoint 中的 modes。 这直接支持正文保留同一入口而不新增 planner。

同一机制文档还说明 survey 是 orientation layer，产生 body-first reading_plan，Reading Runner 消费它，`Navigate` 不拥有 book-level chapter ordering；source skills 是 active-detour 下的 controlled source-evidence layer，不读 future text、不做 semantic relevance judgment、不访问 external network；skill result 是 evidence，不是 answer。 这支持正文中的 Source Evidence Skill Policy 与 support/deferred chapter 边界。

### A.4 Code-level contract evidence

`schemas.py` 定义了核心对象：`SourceRef` 是 inline paragraph-offset citation；`LocalContinuityState` 包含 `mainline_cursor / reading_queue_stage / active_detour_id / active_detour_need / detour_trace`；`NavigateActResult` 支持 `choose_unit / request_skill / defer_detour`；`NavigateActTraceEntry` 可记录 decision、selection mode、reason、skill request/result、resolution、budget state。 这支持正文的 inputs / outputs、state / trace boundary 与 decision options。

`prompts.py` 中 Navigate prompt 已经明确：mainline mode 直接从 preview 选，不能 request skills 或 defer；detour mode 可 choose source-grounded already-read unit、request one source skill、或 honest defer；`end_anchor_text` 必须来自 visible preview；不能 external web search；skill results 是 evidence。 这支持正文把现有 prompt contract 提升为正式 policy。

`nodes.py` 对 LLM outputs 做 normalization：会过滤 visible reaction 中的 internal handles，过滤 source_quote 不在 current unit 的 reaction，normalize detour statuses 与 skill request。它也显示当前 contract 仍有 gap：schema 中 `resolve` 是 StateOperationType，但 `_STATE_OPERATION_TYPES` 未列入 `resolve`；missing `target_store` 会 default to `active_attention`。 这支持正文 “当前实现可保留但需收紧 reason / target / audit”的判断。

`runner.py` 显示 Runner 负责加载/保存 runtime bundle、source skill dispatch、state_ops、observability、source span helpers；它的 detour helper 会把 Read 产出的 detour_need 写入 local continuity，并以 trace 维护 open/resolved/abandoned。 这支持正文中 Runner / Settlement 是 mutation authority 的分工。

`source_spans.py` 以代码形式定义了 paragraph-offset `SourceCursor / SourceSpan`、adaptive preview、exact anchor resolution、fallback cursor、source_ref_from_unit。 这支持正文对 mainline unit boundary、`end_anchor_text` 与 deterministic settlement 的要求。

`source_skills.py` 证明当前 skills 是 book-local source providers，并通过 `sentences_visible_to_mainline` 限制可见范围在 mainline cursor 之前；`source_map_overview / drilldown / fetch_source_window` 都围绕已读 source scope 工作。 这支持正文“不读 future / 不做 external search / evidence not answer”。

`state_projection.py` 构造 bounded navigation/read packets，包含 active_attention、concept、thread、reflective、source_ref digest、recent reactions、continuation capsule。 这支持正文中 “Navigation 只能消费 bounded projections，不读完整 durable stores”。

`read_context.py` 区分 `look_back` 与 `active_recall`，前者返回 earlier source excerpts，后者从 concept/thread/reaction records 补充未 carry state。 这支持正文中 active_recall = memory recovery、look_back = source calibration 的接口边界。

`state_ops.py` 证明 final state mutation 是 deterministic apply layer：active_attention merge/source_ref preserve，concept/thread append/create/link normalize to update，close normalize to resolve，reflective supersede 不 silent overwrite statement。 这支持正文中 Navigate 不写 memory、Read proposes、settlement applies 的边界。

`observability.py` 证明当前已有 read_audit / settlement_audit / unitization_audit；但 read/settlement audit 更偏 Read 与 memory settlement，Navigation-specific reason summary 仍可增强。 这支持正文中的 implementation-ready “navigation audit summary enrichment”。

`storage.py` 证明当前已有 file-based mechanism-private artifacts，不需要新增 planning store 才能执行 v0 policy。

### A.5 Runtime-artifact validation gap

`docs/current-state.md` 记录了已完成或进行中的 diagnostics，例如 paragraph-offset cursor cutover、SourceRef cutover、source skill posture、settlement-audit diagnostic、SourceRef smoke repair，以及 F4A 仍有 detour / prior_link / outside_link / search_intent 未充分验证的能力记录。 本页只把这些作为 repo-documented runtime summary，不声称独立读取了真实 JSONL rows。因此，正文关于 runtime quality 的判断是 cautious：当前 skeleton 合理，但 policy 与 audit 需要收紧。

------

## B. Upstream Design Basis

本页对上游设计的使用方式如下。

`设计-设计路线.md` 定位本页是设计 4：Navigation Policy；它位于 Planning Ontology 之后，解决 `Navigate.choose_next_unit` 职责与主线纪律；它不替代 Detour / Look-back / Active Recall Policy、Visible Reading Route Surface Boundary、Planning Audit / Evaluation 或 Codex Handoff。 本页因此只设计 Navigation Policy，不展开后续子政策。

P0 Shared Charter 给出最高边界：Planning 是 source-grounded reading path planning / attention scheduling / navigation support；`LLM proposes; deterministic runner settles`；`Navigate.choose_next_unit → Read → settlement` 是主循环；mainline continuity 是默认；detour 是 first-class reading path；active_recall 是 memory recovery；look_back 是 source calibration；visible route disclosure 是 optional product surface；audit 是 diagnosis，不是 chain-of-thought exposure；不新增 large planner、multi-agent team、graph workflow rewrite、ToT/LATS/MCTS default loop。 正文中的 core definition、mainline default、state/trace boundary 与 complexity guardrails 都直接继承这些约束。

Planning Ontology v0 已经定义 Planning territory、Planning Object Ontology、`Navigate.choose_next_unit` ontology、micro/meso/macro planning、internal navigation vs visible route disclosure、active_recall / look_back / detour 的区别。 本页没有重新定义 Planning，而是把这些 ontology 结论转成 runtime policy：decision options、mode policy、reason vocabulary、state/trace边界。

Memory Ontology v0 规定 Planning 只能使用 bounded typed source-ref-preserving memory projections，并定义 active_attention digest、concept digest、thread digest、reflective digest、recent reaction digest、knowledge activation projection、source_ref digest、continuation capsule 的边界；recent reaction digest 只能支持 visible continuity，knowledge activation 不能单独成为 detour or visible route disclosure reason。 正文第 10 节完全继承这些 Memory–Navigation interface guardrails。

Memory Formation & Settlement v0 规定 `Read.memory_uptake_ops` 是 bounded write intent，`detour_need` 是 planning intent，Read 可以提出 detour need 但不能定位 target；Runner / settlement 才是 deterministic authority。 正文第 11 节据此明确 Navigate / Read / Runner / Settlement 分工。

Planning Assessment 的主要判断是：当前系统已经是合理的 source-grounded reading navigator skeleton；最大短板不是缺大 planner，而是 Navigation Policy、Detour Policy、Visible Route Surface Boundary、Planning Audit 未收紧；source-order discipline 应作为 default hard preference；value/cost/information scent 可作为轻量判断语言；应拒绝 large planner、multi-agent、graph rewrite、ToT/LATS/MCTS default loop、user-facing surface replacing source-order reading。 正文第 5、12、15、16 节直接吸收这些判断。

Memory Assessment 的接口性判断是：active_recall / look_back / retrieval intent 尚未正式化；Retrieval / Utilization 后续会单独设计；reaction_records 与 knowledge_activations 有 Callback / FVI 风险；Navigation Policy 不应过早定义完整 retrieval 或 evaluation。 正文只允许 Navigation 标记 `active_recall_needed / look_back_needed`，不设计完整 retrieval taxonomy。

本页与上游没有实质冲突。唯一收紧是把 “source-order continuity default” 明确写成 Navigation Policy 的 default hard preference，并把 `defer_detour` 定义为 act-level 合法输出，而不是 durable status；这是对 current implementation 与 Planning Assessment 的 project-specific tightening。

------

## C. External Rationale, as Filtered Through the Assessments

本阶段没有重新读取完整 Evidence Pack，也没有做 broad external research。以下外部依据均是 P0 / Ontology / Assessments 中已筛选过的来源。本页只把它们作为机制判断的 rationale，不把外部系统直接照搬进 Reading Companion。

### C.1 Information Foraging

Information Foraging 原本解释人在信息空间中如何根据 value、cost、information scent 决定 stay / leave。Reading Companion 的相似点是：下一步读哪里也需要判断当前 patch（mainline）是否继续、是否暂时 detour、是否获取更多 source evidence。差异是：书本阅读有更强 source-order / author-structure 纪律，不能像 web browsing 一样自由跳转。

本地化借鉴：正文采用 `mainline_value / continuity_cost / detour_value / source_scent / uncertainty / budget` 作为轻量 reason language。支持类型：Direct / Analogical。不可照搬：不能把 reading path 变成自由信息觅食或 novelty chasing。

### C.2 ReAct

ReAct 原本解决 reasoning 与 acting 交错、通过 observation 修正 hallucinated reasoning 的问题。相似点是 active detour / source skill loop 也需要 source evidence 纠正 navigation uncertainty。差异是 Reading Companion 的 environment 主要是 source text，不是外部工具任务环境。

本地化借鉴：source skill result 是 observation-like evidence，帮助 Navigate 在 active detour 中 choose / request more / defer。支持类型：Direct for bounded evidence correction。不可照搬：不能把每个 mainline unit 都变成 ReAct tool loop。

### C.3 ReWOO

ReWOO 原本解决 tool-augmented LLM 中 reasoning 与 observation 交替成本高的问题，通过计划/变量绑定降低成本。相似点是 detour localization 有时需要先收集 bounded source evidence。差异是阅读中很多判断必须随 source observation 更新，不能冻结成多步计划。

本地化借鉴：source skills 是 bounded evidence gathering，而不是 generic tool planning。支持类型：Analogical。不可照搬：不引入 variable-bound multi-hop planner。

### C.4 Plan-and-Solve

Plan-and-Solve 原本用于复杂 reasoning task 前先形成 plan，减少 missing-step errors。相似点是章初/难段/深钻可能需要 boundary-level planning。差异是普通 reading loop 是 source-order process，不是每步都需要 task decomposition。

本地化借鉴：Navigation 只做 next-unit local policy；显式大 plan 留给 boundary / slow-cycle / future policy。支持类型：Boundary。不可照搬：不新增每步大 planner。

### C.5 HTN / Options / MAXQ

这些 work 原本解决 long-horizon control 的 hierarchy、temporally extended actions 与 controller-worker separation。相似点是 Reading Companion 也有 micro next-unit、meso detour、macro chapter/session carry-forward。差异是 RC 不是 formal planner / RL environment。

本地化借鉴：detour 像 temporally bounded option，必须有 origin、budget、termination/restore reason；Navigate 是 local selector，Runner 是 deterministic executor。支持类型：Analogical / Background。不可照搬：不实现 formal HTN/RL。

### C.6 Rereading / Metacomprehension

Rereading 与 metacomprehension work 原本研究人何时需要回读、理解自我判断如何校准。相似点是 look-back 应服务 source calibration，而不是“相关就回看”。差异是这些研究不直接给 LLM trigger schema。

本地化借鉴：正文把 look_back_needed 限定为 source calibration signal，不让 active_recall 替代 source verification。支持类型：Direct / Analogical。不可照搬：不把 rereading 变成默认动作。

### C.7 Adaptive Navigation Support / Learner Agency / Open Learner Model

这些 work 原本研究教育超媒体和学习系统中如何提供导航支持、保持用户 agency、让建议可解释可控。相似点是 Reading Companion 未来也可能给用户 reading scaffold。差异是 RC 当前不是 tutoring/mastery system，也没有 full learner model。

本地化借鉴：visible route disclosure 是 optional product surface；internal navigation 不等于 visible route disclosure；no_user_surface_needed 是合法输出。支持类型：Boundary for route disclosure / Analogical for agency。不可照搬：不做 full learning path engine，也不做 route steering UI。

### C.8 ToT / LATS / MCTS-style search loops

这些 work 原本用于 hard reasoning、branching deliberation、search/backtracking。相似点是 hard passage / deep-dive 可能有 optional use。差异是普通阅读没有稳定 reward function，且需要低延迟与 mainline continuity。

本地化借鉴：作为 negative / boundary support，拒绝把 ToT / LATS / MCTS 作为 default next-unit decision。支持类型：Negative。不可照搬：不把每步阅读变成 search tree。

### C.9 LangGraph / OpenAI-style trace ideas

Framework trace / durable execution / guardrail 思想可启发 audit、checkpoint、failure attribution。相似点是 Reading Companion 也需要 trace-aware diagnosis。差异是当前 Reading Runner 已是 deterministic orchestrator，迁移 runtime framework 不会自动解决 reading judgment。

本地化借鉴：structured decision summary、budget reason、restore-mainline reason；不迁移为 graph workflow。支持类型：Analogical / Boundary。

------

## D. Simplicity and Universality Check

本设计优先收紧现有 `Navigate / Runner / local_continuity`，没有新增 planner node。

它保留 source-order mainline default，把 detour、look-back、active recall、deep-dive 都定义为 bounded exceptions。

它避免让 Navigate 写 memory。Memory write 仍由 Read 提出 intent，Runner / settlement / state_ops 决定 final mutation。

它避免让 Navigation 变成 route steering surface。Internal navigation 与 visible route disclosure 被明确分层，visible reaction / prior_link / outside_link / search_intent 均不等于 route control。

它避免让 Navigation 变成 Retrieval。Navigation 只消费 bounded projections，并可标记 `active_recall_needed / look_back_needed`；完整 Retrieval / Utilization taxonomy 延后。

它避免把 audit trace 变成 runtime context。Trace 是 diagnostic artifact，不自动进入 prompt；skill history 与 rejected alternatives 不成为 hidden planning memory。

它避免引入 large planner、multi-agent team、graph workflow rewrite、ToT / LATS / MCTS default loop、complex learning path engine、full learner model。

它保留 bounded source skills，并将其定义为 book-local evidence providers，而不是 search engine 或 semantic relevance owner。

它给后续 Detour / Visible Route Disclosure / Audit / Evaluation 留出接口，但没有替它们提前设计完整 schema、rubric、UX 或 implementation plan。

仍存在的复杂化风险：

```text
reason vocabulary 可能被误用成复杂 scoring model；
source skills 可能逐步滑向 hidden semantic search；
defer_detour 若没有后续 Detour Policy，可能在 trace 与 state 中含义漂移；
navigation audit summary 若设计过宽，可能变成 prompt contamination；
future route disclosure surface 若过强，可能重新替代 source-order reading。
```

------

## E. Source Usage List

| External source              | Authors / Organization                              | Year      | Stable URL                                                   | Used for                                                     | Support type            |
| ---------------------------- | --------------------------------------------------- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------------- |
| Information Foraging         | Peter Pirolli, Stuart K. Card                       | 1999      | https://doi.org/10.1037/0033-295X.106.4.643                  | value / cost / information scent for mainline vs detour      | Direct / Analogical     |
| ReAct                        | Shunyu Yao et al.                                   | 2022      | https://arxiv.org/abs/2210.03629                             | bounded observation-grounded correction for detour/source skills | Direct                  |
| Plan-and-Solve Prompting     | Lei Wang et al.                                     | 2023      | https://aclanthology.org/2023.acl-long.147/                  | boundary-level planning, not every-step large planner        | Boundary                |
| ReWOO                        | Binfeng Xu et al.                                   | 2023      | https://arxiv.org/abs/2305.18323                             | bounded evidence gathering analogy for detour support        | Analogical              |
| Options Framework            | Richard S. Sutton, Doina Precup, Satinder Singh     | 1999      | https://doi.org/10.1016/S0004-3702(99)00052-1                | detour as bounded temporally extended path with exit         | Analogical              |
| MAXQ                         | Thomas G. Dietterich                                | 2000      | https://doi.org/10.1613/jair.639                             | controller / executor separation analogy                     | Background / Analogical |
| HTN Planning                 | Kutluhan Erol                                       | 1996      | http://hdl.handle.net/1903/5810                              | micro / meso / macro planning background                     | Background              |
| The rereading effect         | Katherine A. Rawson, John Dunlosky, Keith W. Thiede | 2000      | https://doi.org/10.3758/BF03209348                           | look-back as calibration rather than default reread          | Direct / Analogical     |
| Metacomprehension            | John Dunlosky, Amanda R. Lipko                      | 2007      | https://doi.org/10.1111/j.1467-8721.2007.00509.x             | source calibration and uncertainty discipline                | Analogical              |
| Adaptive Navigation Support  | Peter Brusilovsky                                   | 2003      | https://doi.org/10.1111/1467-8535.00345                      | route disclosure as optional navigation support, not internal control | Direct / Analogical     |
| Learner Agency review        | Michelle Deschênes                                  | 2020      | https://doi.org/10.1186/s41239-020-00219-w                   | visible route disclosure should preserve agency            | Direct                  |
| Open Learner Model           | Yanjin Long, Vincent Aleven                         | 2017      | https://doi.org/10.1007/s11257-016-9186-6                    | explainable scaffold vs internal trace                       | Analogical              |
| Tree of Thoughts             | Shunyu Yao et al.                                   | 2023      | https://arxiv.org/abs/2305.10601                             | negative boundary against default search loop                | Negative                |
| Language Agent Tree Search   | Andy Zhou et al.                                    | 2023      | https://arxiv.org/abs/2310.04406                             | negative boundary against MCTS default reading               | Negative                |
| LangGraph docs               | LangChain                                           | 2024–2026 | https://docs.langchain.com/oss/javascript/langgraph/overview | trace/checkpoint inspiration only                            | Analogical / Boundary   |
| OpenAI Agents / tracing docs | OpenAI                                              | 2025–2026 | https://developers.openai.com/api/docs/guides/agents         | trace-aware audit inspiration only                           | Analogical / Boundary   |
