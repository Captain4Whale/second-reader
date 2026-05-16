# C设计9-Evaluation Calibration & Minimal Eval Suite v0

## 0. Evaluation Calibration 结论

Second Reader 当前不需要重做一套大型 AI Evaluation 体系。已有 repo 资产至少形成了两条核心 evaluation lane：**Local/User-level Selective Legibility** 与 **Long Span MQ / Callback / FVI**。本设计的结论是：

1. **保留 Local/User-level Selective Legibility 作为当前核心 local/user-level eval family。**
   `user-level selective v1` 是 active local/user-level benchmark，评估 Second Reader 是否在 high-value、human-note-aligned source spans 上产生 visible reactions。旧 `excerpt surface v1.1` 只是 historical / superseded surface name；“高价值文本是否触发可见反应”这个 evaluation goal 必须继续保留。
2. **保留 MQ / Callback / FVI 作为当前核心 Long Span evaluation 三件套。**
   它们已经是 active long-span direction，并且 Phase-1 runner 已落地；但当前 evidence status 仍是 `quality_audit`，尚未提升为 formal long-span benchmark authority。
3. **Memory Quality 保持主指标，但需要从“状态是否好”校准为“retained reading state 是否 faithful / useful / organized / source-grounded / continuity-useful”。**
   当前四维 `salience / mainline_fidelity / organization / fidelity` 可以继续保留；新增内容应尽量作为 rubric 强化与 diagnostic tags，而不是拆成一堆新分数。
4. **Spontaneous Callback 必须从“有没有回调”升级为“回调是否正确利用 memory/source”。**
   当前 reaction audit 已能区分 `grounded_callback / weak_callback / false_visible_integration`；下一步应把 callback 与 `memory_refs_used / source_refs_used / retrieval utilization trace` 关联，而不是只看 visible reaction 文本。
5. **False Visible Integration 继续作为核心 pollution / safety 指标。**
   它需要显式覆盖 stale memory current-use、reaction semanticization、knowledge activation source-truth 化、theme-only hard-linking、source-free callback、audit/projection leakage、memory-source conflict 未解决即输出。
6. **Planning 侧只做轻量 trace-quality eval。**
   不做 big planner benchmark，不做 route-disclosure UX eval，不做 ToT/MCTS 式 planning score。最小覆盖是：Navigation Groundedness、Mainline Continuity、Detour Precision / Recovery、Look-back / Active Recall Appropriateness、Planning-Memory Alignment。
7. **Slow-cycle 侧只做 safety / carry-forward eval。**
   不做大型 reflection quality benchmark。最小覆盖是：Promotion Safety、Carry-forward Quality、Not-carried / Cooling Appropriateness、Reaction Boundary Safety、Continuation Capsule Usefulness。
8. **Contract / Audit Checks 是 eval instrumentation，不是产品质量分数。**
   SourceRef binding、settlement outcome、retrieval utilization trace、detour restore reason、slow-cycle promotion evidence 都是 evaluation evidence substrate；它们不能被当作 MQ / Callback / FVI 的替代分数。
9. **当前不需要立即写两个庞大的 C设计10 / C设计11 evaluation pages。**
   C设计9 足够进入 Implementation Handoff。后续若 MVP eval 运行后暴露 rubric 或 trace ambiguity，再补短而聚焦的 Memory 或 Planning eval addendum。

------

## 1. Scope and Purpose

本页是 **AI Evaluation / Product Evaluation calibration**。它回答的是：Second Reader 的阅读行为是否达到产品目标，尤其是 memory 是否 faithful/useful，callback 是否自然且 grounded，FVI 是否受控，detour 是否 bounded，slow-cycle promotion 是否可靠。

本页不是 Engineering Test Plan。pytest、unit tests、schema tests、CI regression、文件写入、函数返回值、runner retry correctness 等属于 Codex implementation / Implementation Handoff，不是本页核心。

本页也不是新 benchmark proposal。它优先复用当前 repo 已有 evaluation docs、datasets、evidence catalog、probe snapshots、judge prompts、eval runner、audit/probe/export code，并校准现有 Local/User-level Selective Legibility、MQ / Callback / FVI 与 C设计0–8 的机制 contract。

------

## 2. Existing Evaluation Asset Inventory

下表先盘点现有资产，再决定是否补新 eval。结论是：Second Reader 已经有一条 active local/user-level selective lane，也有一条可执行的 Long Span vNext evaluation lane；Planning / Slow-cycle coverage 仍主要停留在 audit / trace evidence 层，还没有足够产品质量 judge 覆盖。

| Asset                                        | Path                                                         | Type                                 | Current purpose                                              | What it evaluates                                   | What evidence it consumes                                    | What it does not evaluate                            | Decision                                                     |
| -------------------------------------------- | ------------------------------------------------------------ | ------------------------------------ | ------------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------ |
| Evaluation constitution                      | `docs/backend-reader-evaluation.md`                          | doc / stable methodology             | 定义 product-first、mechanism-agnostic eval constitution；区分 active / historical / discontinued surfaces | 评估体系的北极星与 surface 边界                     | benchmark reports、dataset truth、run evidence               | 不直接评分，不验证 runtime rows                      | **Keep**；作为本页最高 eval 方法论依据                       |
| Evaluation docs index                        | `reading-companion-backend/docs/evaluation/README.md`        | doc / eval index                     | 组织 reviewed evaluation reports、evidence catalog、surface entry points | 哪些 run / report 是当前、历史、superseded          | `eval/runs` summaries、report docs、catalog                  | 不替代具体 runner / judge                            | **Keep**；作为 asset inventory 入口                          |
| Evidence catalog                             | `reading-companion-backend/docs/evaluation/evidence_catalog.md` | evidence catalog / doc               | 记录 current formal evidence、quality audits、historical/superseded/invalidated diagnostics | 运行证据的 authority status                         | aggregate/report/llm usage/run IDs                           | 不直接跑 eval，不读 runtime rows                     | **Keep**；继续作为 durable evidence index                    |
| Evidence catalog JSON                        | `reading-companion-backend/docs/evaluation/evidence_catalog.json` | evidence catalog / machine-readable  | 机器可读 catalog；记录 run_id、surface、goal、status、metric_summary、paths | Run evidence status 与 metric summary               | run summaries、reports、catalog updates                      | 不代表原始 evidence 完整审计                         | **Keep**；Implementation Handoff 应继续更新                  |
| Long Span docs                               | `reading-companion-backend/docs/evaluation/long_span/README.md` | doc / long-span index                | 定义 active Long Span direction 与 historical/discontinued layers | MQ / Callback / FVI 方法方向                        | phase-1 run、semantic probe manifest、reaction audit         | 不提供 planning / slow-cycle rubric                  | **Keep**；当前 Long Span authority at methodology layer      |
| Memory Quality report contract               | `reading-companion-backend/docs/evaluation/long_span/memory_quality_report_contract.md` | report contract / audit doc          | 固定 MQ evidence report shape：probe snapshot、source marker、runtime appendix | MQ evidence 是否可被人类 reviewer 一次读懂          | probe snapshots、source docs、runtime appendices             | 不改变 score / prompt / runtime state                | **Keep**；用于 MQ report reproducibility                     |
| Target-centered accumulation v2 design       | `reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md` | archived eval design                 | 保存 discontinued target-centered long-span route            | 历史上“target 点是否重建 upstream thread”           | target cases、target-local reactions、callback actions       | 不再代表 active Long Span methodology                | **Deprecate as active / keep historical**                    |
| Long Span vNext runner                       | `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py` | runner + embedded judge prompts      | 执行 Phase-1 MQ / reaction audit；读窗口、复用 outputs、调 judge、聚合 report | MQ、Spontaneous Callback、FVI                       | user-level windows、probe manifest、probe snapshots、reaction records、normalized bundles | 不评估 planning trace / slow-cycle safety            | **Keep + adjust**；补 utilization / planning / slow-cycle evidence hooks |
| MQ judge prompt                              | embedded in `run_long_span_vnext.py`                         | judge prompt                         | 1–5 分判断 probe-time memory snapshot                        | salience、mainline fidelity、organization、fidelity | source-so-far context、probe payload、snapshot、probe_review_focus | 不定位 formation / settlement / retrieval stage      | **Keep + rubric tighten**；加 source-grounding / store-appropriateness diagnostics |
| Reaction audit judge prompt                  | embedded in `run_long_span_vnext.py`                         | judge prompt                         | 将 visible reactions 分类为 local / grounded / weak / FVI    | callback quality 与 false integration               | ordered visible reactions、prior_link、outside_link、search_intent | 不知道实际 memory retrieval/utilization 是否发生     | **Keep + adjust**；与 utilization trace 关联                 |
| Semantic probe manifest                      | `reading-companion-backend/eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json` | probe manifest / dataset contract    | 5 个 active windows × 5 semantic probe targets               | MQ probe placement 与 structural signals            | source sentence ids、semantic boundary rationale、structural signals | 不提供 gold answer；不评估 callback / planning       | **Keep**；当前 MQ probe plan authority                       |
| Probe manifest README                        | `reading-companion-backend/eval/manifests/probes/README.md`  | doc / probe contract                 | 说明 ratio probes retired，semantic targets required         | MQ probe construction discipline                    | active manifest                                              | 不评估结果质量                                       | **Keep**                                                     |
| Probe snapshot exporter                      | `reading-companion-backend/src/attentional_v2/benchmark_probes.py` | probe snapshot / export code         | benchmark-only MQ snapshot export                            | probe-time prompt-facing state                      | active_attention、concept/thread/reflective digest、source_ref_digest、recent orientation | 不是 runtime memory；不评分                          | **Keep**；属于 eval instrumentation                          |
| Runtime artifact map                         | `reading-companion-backend/src/attentional_v2/storage.py`    | audit artifact map / instrumentation | 定义 runtime/eval artifact paths                             | 可观测性覆盖                                        | active_attention、concept_registry、thread_trace、reaction_records、read/settlement audit、probe export | 不评价产品质量                                       | **Keep**；用于 audit evidence coverage                       |
| Read / settlement audit                      | `observability.py` + runtime `read_audit.jsonl / settlement_audit.jsonl` | audit artifact / instrumentation     | 记录 read result、memory uptake、source span、state deltas   | formation / settlement observability                | source span、memory ops、surfaced reactions、state deltas    | 当前缺 per-op outcome / utilization trace            | **Keep + extend**                                            |
| Unit span ledger                             | runtime `unit_span_ledger.jsonl`                             | audit artifact                       | accepted source unit coverage / resume fact                  | reading coverage, probe crossing, cursor continuity | accepted SourceSpan                                          | 不代表 semantic memory quality                       | **Keep**；coverage evidence only                             |
| User-level evaluation index                  | `reading-companion-backend/docs/evaluation/user_level/README.md` | doc / active local benchmark index   | 定义 active `user-level selective v1`、formal evidence bundle、active metric 与 matching contract | Local/User-level Selective Legibility               | active split manifest、dataset package、formal rerun evidence、runner links | 不评估 long-span memory quality、distant callback、detour、slow-cycle | **Keep**；作为 Family A 的 primary project evidence          |
| User-level selective split manifest          | `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json` | split manifest                       | 固定 active local/user-level benchmark 的 eligible source split | note-aligned local/user-level coverage              | selected reading segments                                    | 不代表 judge result 或 long-span probe plan          | **Keep**；Family A split authority                           |
| User-level selective active dataset package  | `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/manifest.json` | dataset package                      | active repaired package；包含 `segments.jsonl`、`note_cases.jsonl`、`segment_sources/*.txt` | note recall over aligned human notes                | rendered source segments、aligned human notes、source span slices | 不测 MQ / distant callback / detour / slow-cycle      | **Keep**；core Family A dataset                              |
| User-level selective comparison runner       | `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py` | runner                               | 对 `attentional_v2` 与 `iterator_v1` 执行 active local/user-level comparison | selective legibility / note recall                  | dataset package、visible reactions、source locators、judge decisions | 不生成 Long Span MQ / Callback / FVI score            | **Keep**；Implementation Handoff 不得只保留 Long Span runner |
| User-level selective audit renderer          | `reading-companion-backend/eval/attentional_v2/render_user_level_selective_audit.py` | local audit renderer                 | 渲染 human-readable local audit docs                         | audit readability for Family A                      | `segments.jsonl`、`note_cases.jsonl`、segment source text     | local-only；不是 checked-in formal evidence           | **Keep as audit support**                                    |
| Historical excerpt surface index             | `reading-companion-backend/docs/evaluation/excerpt/README.md` | historical / superseded eval index   | 保存被 `user-level selective v1` 替代的 chapter-scoped `excerpt surface v1.1` reports | historical local/user-level predecessor             | historical aggregate/report/interpretation links             | 不是当前 active eval surface                         | **Keep historical only**；不要恢复为 active benchmark        |
| Runtime run artifacts                        | `eval/runs/attentional_v2/...`                               | run output / raw evidence            | 保存 aggregate、report、case rows、llm usage、raw outputs    | 已完成 run 的 evidence                              | normalized bundles、snapshots、reaction labels               | 本轮未逐行审计真实 runtime JSONL                     | **Keep / inspect when promoting**                            |
| `tests/test_long_span_vnext.py`              | `reading-companion-backend/tests/test_long_span_vnext.py`    | engineering test / contract test     | 测 runner/probe export/reuse/prompt scale behavior           | 代码是否按契约运行                                  | fixtures、mocked runner/judge payloads                       | 不评价真实阅读产品质量                               | **Keep outside eval suite**；属于 Codex/CI                   |
| Current-state / task registry / decision log | `docs/current-state.md`, `docs/tasks/registry.md/json`, `docs/history/decision-log.md` | project docs / traceability          | 当前状态、任务、历史决策                                     | 评估资产状态与 historical context                   | run ids、evidence refs、jobs、decisions                      | 不直接作为 score evidence                            | **Use as context**；not eval metric                          |
| Standalone judge prompt files                | not found in inspected repo search                           | unknown                              | 未发现独立 judge prompt file；当前 prompt 嵌在 runner        | N/A                                                 | N/A                                                          | N/A                                                  | **Inspect further if repo adds prompt files**                |
| Planning-specific eval dataset               | not found as active dedicated asset                          | dataset gap                          | 未发现 dedicated planning eval dataset                       | N/A                                                 | N/A                                                          | Detour / navigation trace quality coverage weak      | **Add minimal cases only**                                   |
| Slow-cycle-specific eval dataset             | not found as active dedicated asset                          | dataset gap                          | 未发现 dedicated slow-cycle safety dataset                   | N/A                                                 | N/A                                                          | Promotion / carry-forward safety coverage weak       | **Add minimal cases only**                                   |

------

## 3. Evaluation vs Engineering Tests vs Contract / Audit Checks

### Evaluation / AI Evals

Evaluation 评估 Second Reader 的阅读行为是否达到产品目标。它回答：

- 读到当前点时，memory 是否保存了重要、主线、组织清楚、忠实的 reading state；
- callback 是否自然、正确、source-grounded；
- visible integration 是否存在 overclaim、hard-linking、memory drift；
- navigation 是否 grounded；
- detour 是否有价值、有边界、能恢复主线；
- slow-cycle promotion 是否安全、carry-forward 是否有用。

当前属于 evaluation 的核心资产是：`user-level selective v1` local/user-level lane、Long Span vNext MQ / Callback / FVI lane、semantic probe manifest、probe snapshots、reaction audit、reviewed evidence reports、evidence catalog。

### Engineering Tests

Engineering Tests 检查代码是否正确运行。它们回答：

- 函数是否返回正确 shape；
- probe export 是否只 emit 一次；
- explicit probe targets 缺失是否 fail fast；
- runner 是否复用 completed output；
- judge prompt 是否包含评分 scale；
- retry 是否按预期发生。

`tests/test_long_span_vnext.py` 属于这一类。它保护 eval runner 和 probe contract，不应被解释成产品质量评估。

### Contract / Audit Checks

Contract / Audit Checks 介于二者之间。它们为 Evaluation 提供 evidence substrate，但不是产品质量分数本身。

例子：

- SourceRef binding result；
- settlement per-op outcome；
- state IDs added / updated / skipped / failed；
- retrieval utilization trace；
- detour open / defer / abandon / resolve / restore reason；
- slow-cycle promotion outcome；
- continuation capsule delta；
- warning markers / status markers。

当前 `read_audit` 与 `settlement_audit` 已记录 source span、memory ops、surfaced reactions、detour_need、state deltas等，但仍缺 per-op outcome 与 retrieval utilization trace。

------

## 4. Existing Evaluation Goals Calibration

### 4.0 Local/User-level Selective Legibility：保留为核心 local/user-level family

`user-level selective v1` 不是 Long Span Memory eval 的附属数据源。它评估的是另一个产品目标：

```text
Second Reader 是否会在 high-value、human-note-aligned source spans 上产生 visible reactions。
```

Active metric：

```text
note recall over aligned human notes
```

Matching contract：

- candidate retrieval 先看 strict source-span overlap；
- text similarity / semantic similarity 不能 admit candidates；
- canonical char spans 完全相同时才算 `exact_match`；
- non-exact source-overlap candidates 进入 judge；
- `focused_hit` counts toward recall；
- `incidental_cover` 只是 supporting-only；
- visible reactions 如果没有 usable source locator，应 fail the surface，而不是 fallback 到 string matching。

它评估：

- `reader_character.selective_legibility`；
- Second Reader 是否对人类 note-aligned 的高价值文本做出可见反应；
- visible reaction 是否能被稳定定位回 source span。

它不评估：

- long-span memory quality；
- distant callback；
- detour policy；
- slow-cycle promotion；
- general insight quality。

旧 `excerpt surface v1.1` 是 historical / superseded surface name。它不应恢复为 active benchmark；但它留下的“高价值文本是否触发可见反应”问题，应由 `user-level selective v1` 继续承担。

### 4.1 Memory Quality：保留为主指标

当前 MQ 应继续作为 Second Reader memory eval 的主指标。它不只是“summary 是否好”，而是：

- 是否保留了 source-so-far 中重要、主线、后续会用到的 reading state；
- 是否保留 author-given structures，例如 stage model、classification、core definition、roadmap、named distinction；
- 是否组织成 usable concepts / threads / active attention，而不是散碎 highlights；
- 是否 source-grounded；
- 是否忠实，不 drift，不 over-abstract；
- 是否存到了合适的 store，而不是把 reaction、hypothesis、concept、thread 混在一起；
- 是否能支持后续 continuation、callback、look-back、detour。

当前四个分数维度保留：

```text
salience_score
mainline_fidelity_score
organization_score
fidelity_score
```

调整方式：不新增复杂分数；新增少量 diagnostic tags，例如 `source_grounding_issue / store_appropriateness_issue / stale_memory_issue / audit_missing_issue`。MQ 总分仍由四维派生。

### 4.2 Spontaneous Callback / Callback Quality：保留并拔高

当前 reaction audit 已能区分 grounded callback、weak callback、FVI。下一步应把 callback 评估从“看起来像 recall”升级为：

```text
callback quality = naturalness
                 + source-grounding
                 + correct memory utilization
                 + no overclaim
                 + correct boundary between visible reaction and semantic memory
                 + no FVI
```

必须新增或强化的 evidence：

- callback 是否引用了实际 prior memory / source，而不是只靠主题相似；
- `prior_link` 是否有 ref_ids，是否能回到 memory/source；
- callback 是否使用 stale / superseded / invalidated memory；
- callback visible wording 是否把 reaction-only trace 写成 source truth；
- callback 是否在 memory-source conflict 未解决时 visible hard-link。

当前 reaction audit prompt 可保留，但应加入 utilization evidence 输入；否则只能评估 visible output quality，无法判断 retrieval/utilization stage 是否健康。

### 4.3 False Visible Integration：保留为核心 pollution 指标

FVI 是当前最重要的 safety / pollution eval 之一。它应覆盖：

- **reaction semanticization**：visible reaction 被当作 semantic memory；
- **stale memory current-use**：旧 memory 被当作当前 source-so-far truth；
- **knowledge activation source-truth 化**：prior knowledge warrant 被说成书中事实；
- **theme-only hard-linking**：仅凭主题相似硬连前文；
- **source-free callback**：无 source / memory support 的回调；
- **audit/projection leakage**：audit 或 prompt projection 进入 visible output；
- **memory-source conflict unresolved**：memory 与 current source 冲突但未 look-back 校准即输出；
- **memory drift**：callback 逐渐离开原 source meaning。

现有 FVI label 保留，不拆成很多新指标；上述失败模式进入 diagnostic tags。

------

## 5. Minimal Planning-side Evaluation

Planning eval 应主要是 **trace-quality / behavior-quality eval**，不是 big planner benchmark。

| Planning eval item                        | Purpose                                                      | Current data support                                         | Required audit evidence                                      | Judge needed?                                                | Existing coverage | Minimal rubric                                               |
| ----------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| Navigation Groundedness                   | 判断下一 unit / source move 是否来自 visible source preview 或 allowed source evidence | partial：unit span ledger、source spans、Navigate trace schema、read_audit | navigation decision reason、source_evidence_used、end_anchor_text resolution、budget_state | small judge for sampled moves; audit-only for field coverage | partial           | 选择是否 source-grounded、bounded、非 future text、reason 是否足够 |
| Mainline Continuity                       | 判断是否默认保持 source-order continuity，避免 novelty chasing | partial：cursor, unit_span_ledger, local_continuity          | mainline_cursor, reading_queue_stage, detour state, restore reason | mostly audit-only                                            | partial           | 不无故跳跃；detour 后能恢复；coverage 无异常缺口             |
| Detour Precision / Recovery               | 判断 detour 是否有明确 need、target hint、source scent、退出与恢复 | weak：F4A 曾显示 detour 未被验证；当前 active assets detour coverage 不足 | detour_id, open/defer/resolve/abandon/restore reason, source skill result, budget_state | yes for minimal cases                                        | weak              | detour 有价值、目标 grounded、预算受控、恢复主线明确         |
| Look-back / Active Recall Appropriateness | 判断 recall/look-back 是否在正确缺口触发                     | partial：context_request, supplemental_steps, supplemental_ref_ids | retrieval_intent, items_returned, items_used, source_refs_used, no_use_reason | audit-only plus sampled judge                                | partial           | 缺 memory 用 active_recall；缺 source 用 look_back；不以 recall 替 source truth |
| Planning-Memory Alignment                 | 判断 planning 是否正确使用 memory projection，而不是把 memory 当 source truth | weak / partial                                               | memory_refs_used, source_refs_used, current truth vs lineage marker, warning markers | yes for sampled cases                                        | weak              | memory 只作为 continuity support；detour/callback 需 source grounding |

Minimal addition：只补一小组 detour / look-back / active recall cases，不新建大 benchmark。每类 3–5 个高信号窗口足够第一轮诊断。

------

## 6. Minimal Slow-cycle Evaluation

Slow-cycle eval 只评估 safety、carry-forward 与 boundary，不评估“大反思质量”。

| Slow-cycle eval item                       | Purpose                                                      | Required evidence                                            | Existing data support                                        | Judge or audit?                            | Failure tags                                                 |
| ------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------ | ------------------------------------------------------------ |
| Slow-cycle Promotion Safety                | 判断 reflective promotion 是否基于足够 settled memory / source_refs，而不是单段过早概括 | promotion candidate, supporting_source_refs, outcome, withhold reason | partial：slow_cycle code handles reflective promotion / reaction persistence / reconsolidation, but no active dedicated eval dataset inspected | small safety judge + audit                 | `slow_cycle_issue`, `source_grounding_issue`, `reaction_semanticization_issue` |
| Carry-forward Quality                      | 判断跨章/session carry-forward 是否保留重要 active focus 与 source_refs | carried IDs, not_carried reason, active_attention source_refs before/after | partial：current-state records active_attention SourceRef carry-forward repair | judge on small sample + audit              | `management_issue`, `stale_memory_issue`, `audit_missing_issue` |
| Not-carried / Cooling Appropriateness      | 判断 cooling / not carried 是否合理，不丢主线 memory         | cooling ops, not_carried reason, status markers              | weak / partial                                               | mostly audit-only; judge if loss suspected | `management_issue`, `slow_cycle_issue`                       |
| Reconsolidation / Reaction Boundary Safety | 判断 later reading 是否正确 reinterpret visible reactions，而不把 reaction 自动变 semantic memory | reaction_records, reconsolidation_records, prior_link, supersedes_reaction_id | partial：reaction builder persists source refs and prior/outside/search fields | FVI-style judge                            | `reaction_semanticization_issue`, `fvi_issue`                |
| Continuation Capsule Usefulness            | 判断 continuation capsule 是否帮助恢复 reading focus，而不是污染 prompt | continuation_capsule_delta, refs, status markers             | partial：artifact exists in storage map                      | audit + small judge on resumed runs        | `retrieval_issue`, `utilization_issue`, `slow_cycle_issue`   |

Minimal addition：只需要 2–3 个 chapter-boundary / resume / promotion-focused cases，不做 reflection benchmark。

------

## 7. Stage-aware Failure Attribution

Diagnostic tags 不是独立指标。它们用于定位失败发生在哪一层，并帮助决定修机制、修 audit，还是修 dataset。

| Tag                                       | Meaning                                                      | Evidence source                                     |
| ----------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------- |
| `formation_issue`                         | Read 提出的 memory intent 不重要、不忠实、错 store           | read_audit, memory_uptake_ops, MQ judge observation |
| `settlement_issue`                        | SourceRef binding / schema / state mutation 失败             | settlement_audit, per-op outcome                    |
| `management_issue`                        | lifecycle / cooling / resolve / supersede / carry-forward 不当 | state diffs, slow-cycle audit                       |
| `retrieval_issue`                         | 该取回的 memory/source 未取回，或取错                        | retrieval trace, context_request                    |
| `utilization_issue`                       | 取回了但没用、误用、claim 与 evidence 不一致                 | items_returned vs items_used                        |
| `slow_cycle_issue`                        | promotion / cooling / continuation capsule 出错              | slow-cycle event evidence                           |
| `navigation_issue`                        | 下一 unit 选择不 grounded 或不 bounded                       | Navigate trace, unit_span_ledger                    |
| `detour_recovery_issue`                   | detour 无退出、无恢复、过度 linger                           | detour_trace, restore reason                        |
| `source_grounding_issue`                  | visible / memory claim 缺 SourceRef 或 source excerpt        | source_refs_used, SourceRef resolution              |
| `stale_memory_issue`                      | superseded / invalidated / old state 被当 current truth      | status markers, lineage                             |
| `reaction_semanticization_issue`          | visible reaction 被当 concept/thread/source truth            | reaction_records, FVI judge                         |
| `knowledge_activation_source_truth_issue` | prior knowledge warrant 被说成书中事实                       | knowledge_activations, visible output               |
| `audit_missing_issue`                     | 无法判断，因为 evidence 缺失                                 | audit coverage check                                |
| `dataset_gap`                             | 现有 cases 没覆盖行为                                        | dataset map                                         |
| `judge_uncertainty`                       | judge 无法可靠判定，需要 human / repeated review             | judge output, disagreement                          |

------

## 8. Minimal Eval Suite Proposal

### MVP Families

Current MVP family order:

- Family A: Local/User-level Selective Legibility
- Family B: Memory Quality
- Family C: Callback Quality
- Family D: FVI / Pollution
- Family E: Planning Trace Quality
- Family F: Slow-cycle Safety
- Family G: Instrumentation Coverage Audit

| Family                                      | Goal                                                         | Existing data source                                         | Input artifacts                                              | Judge needed?               | Audit evidence needed                                        | Output                                         | Diagnostic tags                                              | Action                              | Blocking gaps                               |
| ------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------------- | ------------------------------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------ | ----------------------------------- | ------------------------------------------- |
| A. Local/User-level Selective Legibility    | 判断 high-value、human-note-aligned source spans 是否触发 visible reactions | `user-level selective v1` active dataset, user-level README, active split manifest | `segments.jsonl`, `note_cases.jsonl`, segment source text, visible reactions | yes for non-exact overlap   | usable source locator, strict source-span overlap, judge decision | note recall over aligned human notes + focused/incidental labels | source_grounding / audit_missing / dataset_gap               | **Keep as core local family**       | active run may need rerun after package repair |
| B. Memory Quality eval                      | 判断 probe-time memory/state snapshot 是否 faithful/useful/organized | semantic probe manifest, MQ probe snapshots, Long Span vNext run | `memory_quality_probe_snapshots.json`, source marker, source refs, state digests | yes                         | SourceRef digest, read/settlement audit, probe target rationale | MQ 4-dim scores + overall + tags               | formation / settlement / management / source_grounding / audit_missing | **Keep + adjust rubric**            | per-op outcome missing for attribution      |
| C. Callback Quality eval                    | 判断 visible callbacks 是否自然且 grounded                   | reaction audit, reaction_records, normalized bundles         | ordered reactions, prior/outside/search fields, prior context | yes                         | memory_refs_used, source_refs_used, prior_link support       | grounded / weak / local labels + quality notes | retrieval / utilization / source_grounding / stale_memory    | **Keep + add utilization evidence** | utilization trace missing                   |
| D. FVI / Pollution eval                     | 识别 false visible integration 与 memory pollution           | reaction audit, FVI labels                                   | callback-like reactions, memory/source context, lineage warnings | yes                         | stale/lineage markers, knowledge warrant markers, source conflict evidence | FVI count/rate + examples + tags               | stale_memory / reaction_semanticization / knowledge_activation_source_truth | **Keep + tighten failure modes**    | stale/reaction/knowledge markers missing    |
| E. Planning Trace Quality eval              | 轻量评估 navigation / recall / detour 行为                   | read_audit, unit_span_ledger, local_continuity, Navigate trace if present | source moves, context requests, detour trace, source skill results | small sampled judge + audit | navigation reason, source evidence, restore reason, budget   | trace-quality labels, not product score        | navigation / detour_recovery / retrieval / utilization       | **Add minimal cases**               | detour coverage weak                        |
| F. Slow-cycle Safety eval                   | 轻量评估 promotion / carry-forward / continuation safety     | slow-cycle artifacts, state diffs, reaction/reconsolidation records | reflective frames, carry-forward deltas, continuation capsule | small judge + audit         | promotion outcome, withhold/not_carried reasons, source refs | safety pass/fail + tags                        | slow_cycle / management / source_grounding                   | **Add minimal cases**               | promotion/carry-forward evidence incomplete |
| G. Instrumentation coverage audit           | 确保 eval 有证据可查                                         | storage map, observability, runtime audits                   | artifact map, read/settlement/ledger rows                    | no                          | required evidence field coverage                             | coverage checklist                             | audit_missing / dataset_gap                                  | **MVP audit-only**                  | per-op and utilization fields missing       |

### Optional Families

不进入 MVP：

- full route disclosure UX eval；
- user-controlled route recommendation eval；
- vector DB / graph DB retrieval eval；
- full Memory Evaluation encyclopedia；
- full Planning Evaluation encyclopedia；
- human user study；
- all-store lifecycle benchmark。

------

## 9. Existing Dataset Coverage Map

| Existing asset / dataset                           | Covers which family                 | Coverage strength              | Missing behavior                                             | Action                                    |
| -------------------------------------------------- | ----------------------------------- | ------------------------------ | ------------------------------------------------------------ | ----------------------------------------- |
| `user-level selective v1` dataset                  | A                                   | strong for local selective legibility | not designed for long-span memory, distant callback, detour, slow-cycle | keep as core local eval family; do not replace with MQ/FVI |
| `memory_quality_semantic_probe_plan_20260504.json` | B                                   | strong for MQ placement        | no callback / planning / slow-cycle behavior                 | keep                                      |
| Long Span vNext Phase-1 run                        | B/C/D                               | partial-to-strong diagnostic   | not formal authority; MQ older score partly from hard-ratio era; no planning/slow-cycle score | keep, rerun under semantic probe manifest |
| Reaction audit rows from April 25 rejudge          | C/D                                 | strong visible-output evidence | no retrieval utilization proof                               | keep + add utilization trace              |
| `memory_quality_probe_snapshots.json`              | B                                   | strong for probe-time state    | final runtime state cannot replace probe state               | keep                                      |
| `read_audit / settlement_audit / unit_span_ledger` | B/G, partial E/F                    | partial                        | per-op outcome and utilization missing                       | add audit evidence                        |
| `target-centered accumulation v2` frozen set       | historical C/D-like long-span       | weak for current method        | discontinued product question                                | keep historical; mine only if needed      |
| F4A quality audit                                  | visible reaction density / wording  | partial                        | detour not exercised; prior/outside/search absent            | keep diagnostic only                      |
| `tests/test_long_span_vnext.py`                    | G / contract behavior               | strong engineering coverage    | not product eval                                             | keep outside eval suite                   |
| Dedicated Planning dataset                         | E                                   | unknown / not found            | detour, recovery, grounded navigation                        | add small cases                           |
| Dedicated Slow-cycle dataset                       | F                                   | unknown / not found            | promotion/carry-forward/reconsolidation safety               | add small cases                           |

Minimal补 case 策略：不要扩成大数据集。先在现有 5 个 active windows 里挑选少量高信号 windows，补：

- 3–5 个 detour / look-back / active recall cases；
- 2–3 个 slow-cycle / chapter-boundary / carry-forward cases；
- 3–5 个 FVI high-risk stale / reaction / knowledge activation cases。

------

## 10. Rubric Calibration

### MQ rubric

保留当前 MQ 四维与 overall。调整为：

- 不奖励 source text 本身，必须看 snapshot retained state；
- 加强 source-grounding、store appropriateness、structural signal retention；
- judge reason 必须指出 concrete retained items 与 omissions/drift；
- source-given stage model / classification / definition / roadmap / named distinction 缺失时影响 salience / organization / mainline fidelity；
- 输出 `judge_uncertainty` 与 diagnostic tags。

不新增独立 `source_grounding_score`，避免指标泛滥。

### Callback rubric

当前 labels 保留：

```text
local_only
grounded_callback
weak_callback
false_visible_integration
```

调整：

- `grounded_callback` 必须有 visible naturalness + prior material correctness；
- 若有 utilization evidence，应要求 callback 的 `memory_refs_used / source_refs_used` 与 visible wording一致；
- `weak_callback` 用于 vague / under-supported / partial；
- `false_visible_integration` 用于 overclaim / hard-link / stale / source-free / drift；
- `prior_link / outside_link / search_intent` 只能作为 support，不是 proof。

### FVI rubric

在现有 FVI label 下增加失败检查：

```text
reaction_semanticization
stale_memory_current_use
knowledge_activation_as_source_truth
theme_only_hard_linking
source_free_callback
audit_projection_leakage
unresolved_memory_source_conflict
```

这些是 tags，不是新分数。

### Planning Trace Quality rubric

只用小 rubric：

- source-grounded？
- bounded？
- mainline continuity preserved？
- detour has source scent / value / budget / restore？
- active recall vs look-back 用对了吗？
- memory projection 有没有被误作 source truth？

### Slow-cycle Safety rubric

只用 safety rubric：

- promotion 是否有 sufficient source support；
- carry-forward 是否保留 important / live / source-ref-bearing state；
- not_carried 是否有理由；
- reaction / knowledge boundary 是否安全；
- continuation capsule 是否帮助恢复而不污染。

不做：

- general reflection eloquence score；
- planner intelligence score；
- route disclosure usefulness score；
- all-store lifecycle score。

------

## 11. Audit Evidence Requirements

| Evidence                                                 | Current status                                | Needed for MVP? | Notes                                                        |
| -------------------------------------------------------- | --------------------------------------------- | --------------- | ------------------------------------------------------------ |
| SourceRef binding result                                 | partial                                       | yes             | SourceRef exists; per-op binding result still需显式化        |
| settlement per-op outcome                                | missing / partial                             | yes             | 当前是 compact state delta；需要 accepted / merged / skipped / failed / deferred |
| state IDs added / updated / skipped / failed             | added/updated partial; skipped/failed missing | yes             | state_deltas 已有 added/updated/removed，缺 skipped/failed   |
| memory_refs_used                                         | missing / partial                             | yes             | carry_forward_ref_ids 有，但不等于 used                      |
| source_refs_used                                         | partial                                       | yes             | source_ref_digest 有；visible/judge use trace不足            |
| retrieval_intent                                         | partial                                       | yes             | context_request 有 active_recall/look_back 雏形；需统一      |
| items_returned                                           | missing / partial                             | yes             | supplemental refs 可近似，但需 explicit                      |
| items_used / items_claimed_used / items_evidenced_used   | missing                                       | yes             | Callback / FVI calibration 的 blocking gap                   |
| no_use_reason                                            | missing                                       | yes             | retrieval hit ≠ utilization success                          |
| detour_id                                                | partial                                       | yes for D       | local_continuity / detour_trace 有雏形                       |
| detour open / defer / abandon / resolve / restore reason | partial                                       | yes for D       | restore reason 尤其缺                                        |
| budget_state / stop_reason                               | partial                                       | yes             | read_audit 有 stop_reason / budget_exhausted；Navigate trace需统一 |
| navigation decision reason                               | partial                                       | yes for D       | NavigateActTrace schema supports reason；coverage需验证      |
| slow_cycle_event_id                                      | missing / unknown                             | yes for E       | minimal slow-cycle eval 需要                                 |
| promotion candidate outcome                              | partial / unknown                             | yes for E       | promote / withhold / rejected                                |
| withhold_promotion reason                                | missing / unknown                             | yes for E       | 防止过度 promotion                                           |
| not_carried reason                                       | missing / unknown                             | yes for E       | carry-forward safety                                         |
| continuation_capsule_delta                               | partial                                       | important       | artifact exists，delta trace需补                             |
| warning markers                                          | partial / missing                             | yes             | stale / lineage / reaction / knowledge warnings              |
| status markers                                           | partial                                       | yes             | lifecycle/status-aware retrieval                             |

这些 evidence 不能当 score。它们只让 MQ / Callback / FVI / Planning / Slow-cycle 的失败可归因。

------

## 12. Coverage Gaps and Minimal Additions

### Blocking

1. **Utilization trace 缺口**
   没有 `items_returned / items_used / no_use_reason / memory_refs_used / source_refs_used`，就无法把 Callback 与真实 memory/source utilization 关联，也难以诊断 FVI 是 retrieval 污染还是 visible wording 问题。
2. **Per-op settlement outcome 缺口**
   当前 settlement audit 有 compact state deltas，但缺每条 memory op 的 source binding、normalization、accept/skip/fail/defer reason。没有它，MQ 失败无法归因到 formation vs settlement。
3. **Detour / slow-cycle minimal behavior coverage 缺口**
   现有核心 assets 对 detour precision/recovery 与 slow-cycle promotion/carry-forward safety 覆盖弱。只需补少量 cases，不需要大 benchmark。

### Important

- stale / lineage / reaction / knowledge activation warning markers；
- judge uncertainty field；
- human review fallback for high-impact ambiguous cases；
- Planning trace report shape；
- slow-cycle event audit surface。

### Deferred

- full Memory Audit & Evaluation encyclopedia；
- full Planning Audit & Evaluation page；
- route disclosure UX eval；
- recommendation / learning path eval；
- vector DB / graph DB eval；
- user study；
- full formal promotion threshold design。

------

## 13. What This Design Changes or Tightens

### 保留

- MQ / Spontaneous Callback / FVI；
- semantic probe manifest；
- Phase-1 Long Span vNext runner；
- reaction audit labels；
- evidence catalog；
- user-level selective v1 as core Local/User-level Selective Legibility family；
- read/settlement audit as instrumentation。

### 调整

- MQ rubric 加强 source grounding、store appropriateness、structural signal retention；
- Callback 与 utilization trace 关联；
- FVI 扩展到 stale memory、reaction semanticization、knowledge activation source-truth；
- Planning 只加 trace-quality eval；
- Slow-cycle 只加 safety eval；
- audit evidence 不再被误当产品 score。

### 新增

- Minimal Planning Trace Quality family；
- Minimal Slow-cycle Safety family；
- audit-only instrumentation coverage family；
- stage-aware diagnostic tags；
- very small detour / slow-cycle / FVI high-risk cases。

### 不做

- Engineering Test Plan；
- full benchmark platform；
- new giant dataset；
- full Memory Evaluation encyclopedia；
- full Planning Evaluation encyclopedia；
- Codex task list；
- all diagnostic tags as separate metrics。

------

## 14. Decision on C设计10 / C设计11

**建议：暂时不需要立即写 C设计10-Memory Audit & Evaluation Design v0 或 C设计11-Planning Audit & Evaluation Design v0 两个大页。**

理由：

1. 当前 repo 已经有 stable evaluation constitution、active `user-level selective v1` benchmark、long-span active direction、runner、semantic probe manifest、reaction audit、evidence catalog。
2. 当前最大缺口不是“再设计一套 eval 理论”，而是少量 audit evidence 与 utilization trace 缺失。
3. Planning / Slow-cycle 只需要轻量 trace-quality / safety eval；写大页容易把本轮变成新 benchmark 平台设计。
4. 补回 Local/User-level Selective Legibility 不要求新增一篇大评测页；它应作为 C设计9 的核心 Family A 进入同一个 Minimal Eval Suite。
5. C设计9 已足够交给 Implementation Handoff 做最小 instrumentation + runner/rubric adjustment。
6. 若 MVP 运行后发现 Memory rubric 或 Planning trace ambiguity 仍然大，再补短 addendum，而不是预先写百科式 C10/C11。

推荐路径：

```text
C设计9 accepted
→ Implementation Handoff for minimal eval instrumentation and small cases
→ rerun / inspect MVP eval
→ only if needed, write short Memory or Planning eval addendum
```

------

## 15. Implementation Handoff Implications

后续 Implementation Handoff 需要拿走：

- eval family list：A–G；
- two eval lanes：Local/User-level Selective Legibility 与 Long Span Evaluation；
- dataset mapping：现有 active / historical / partial / gap；
- rubric adjustments：MQ / Callback / FVI / Planning / Slow-cycle；
- audit evidence requirements：per-op outcome、utilization trace、detour restore、slow-cycle outcome；
- minimal new cases：detour、look-back/active recall、slow-cycle、FVI high-risk；
- judge uncertainty handling；
- clear separation：engineering tests 留给 Codex / CI，不写进 product eval score。

Implementation Handoff 不得只实现 Long Span MQ / Callback / FVI adjustments。它必须保留 active `user-level selective v1` runner 与 dataset lane，并把 local/user-level note recall 与 long-span MQ / Callback / FVI 作为并行 evaluation tracks 处理。

------

## 16. Optional Open Questions

1. **C设计8 原始文档未在本轮可访问输入中出现。**
   不阻塞 MVP，因为 slow-cycle eval 可基于用户给出的 C设计8 requirements、当前 repo slow-cycle code、C设计0–7 边界先做 safety coverage。若要写 detailed slow-cycle eval addendum，需要读取 C设计8 正文。
2. **本轮没有逐行审计真实 runtime JSONL rows。**
   不阻塞 eval design，但阻塞“当前 runtime quality 已经稳定”的断言。正式 benchmark promotion 前需要抽样检查 run artifacts。
3. **Formal long-span authority promotion threshold 尚未决定。**
   不阻塞 MVP eval suite；阻塞的是将 Phase-1 diagnostic 升级为 formal benchmark authority。

------

# Appendix: Design Rationale and Evidence Basis

## A. Project Evidence Basis

| Repo file                                                    | What it is                               | Current use                                             | Supports this design judgment                                | Asset type             | Runtime-artifact validation gap      |
| ------------------------------------------------------------ | ---------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------ | ---------------------- | ------------------------------------ |
| `reading-companion-backend/docs/evaluation/README.md`        | evaluation docs index                    | 跨 surface 入口与 report/catalog 路由                   | 现有 eval 资产应优先复用，不重建平台                         | eval doc               | 不验证 runtime rows                  |
| `reading-companion-backend/docs/evaluation/user_level/README.md` | active user-level eval index             | 定义 `user-level selective v1` active benchmark、metric、matching contract、formal evidence | Local/User-level Selective Legibility 是核心 eval family，不是 Long Span 附属 substrate | eval doc               | 不直接评分；链接 dataset/runner/evidence |
| `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json` | active split manifest                    | 固定 active local/user-level benchmark split             | Family A 应复用现有 active split，不新建 benchmark           | split manifest         | 需由 runner/evidence 验证实际 run    |
| `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/manifest.json` | active user-level dataset package        | 入口到 `segments.jsonl`、`note_cases.jsonl`、segment sources | note recall over aligned human notes 是 active local/user-level metric | dataset package        | formal rerun may lag current package |
| `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py` | active local/user-level comparison runner | 跑 `attentional_v2` vs `iterator_v1` note recall comparison | Implementation Handoff 必须保留 local lane，不得只做 Long Span | runner                 | runner behavior 仍需工程测试保护     |
| `reading-companion-backend/eval/attentional_v2/render_user_level_selective_audit.py` | local audit renderer                     | 渲染 human-readable audit docs                           | Family A 需要 audit readability，但 audit export 本身不是 formal score | audit renderer         | local-only output                    |
| `reading-companion-backend/docs/evaluation/excerpt/README.md` | historical excerpt surface index         | 保存 `excerpt surface v1.1` reports                      | 旧 surface name 是 historical / superseded；underlying high-value visible-reaction goal 由 `user-level selective v1` 继承 | historical eval doc    | 不能当 current active surface        |
| `reading-companion-backend/docs/evaluation/evidence_catalog.md/json` | durable evidence catalog                 | 标记 current / quality_audit / historical / invalidated | Phase-1 evidence 是 quality audit，不是 formal authority     | evidence catalog       | catalog summary 不是原始 row audit   |
| `docs/backend-reader-evaluation.md`                          | stable eval constitution                 | product-first、mechanism-agnostic、split-surface rules  | Evaluation 不应防守当前机制，也不应混成单分数                | eval methodology doc   | 不直接评分                           |
| `reading-companion-backend/docs/evaluation/long_span/README.md` | long-span surface authority              | 定义 active MQ / Callback / FVI direction               | MQ / Callback / FVI 应保留为核心                             | eval doc               | Phase-1 未 formal promoted           |
| `target_centered_accumulation_v2_design.md`                  | archived design                          | 保存 discontinued target-centered route                 | 不应回到 target-centered visible integration as current method | historical eval design | 可用于历史诊断，不做 active score    |
| `run_long_span_vnext.py`                                     | runner + embedded judge prompts          | 执行 Phase-1 MQ / reaction audit                        | 现有 runner 可复用，只需 calibration                         | runner / judge         | 不覆盖 planning/slow-cycle           |
| `tests/test_long_span_vnext.py`                              | engineering/contract tests               | 测 probe export、prompt scale、reuse/retry              | tests 不等于 product-quality eval                            | engineering test       | 无真实 reading quality judgement     |
| `docs/current-state.md`                                      | current project status                   | 当前 objective、diagnostic result、next target          | runtime quality 不可过度声称；已有 diagnostics 可作为 evidence | project doc            | 记录诊断摘要，但非独立 runtime audit |
| `docs/history/decision-log.md`                               | historical decision log                  | 保留设计演化与 rejected alternatives                    | Evaluation frame product-first / mechanism-agnostic 是已冻结方向 | historical doc         | 不做 current score                   |
| `docs/tasks/registry.md/json`                                | task traceability                        | 记录 active eval tasks、evidence refs、job refs         | Long Span memory direction 已是 active task；next phase 是 review/implementation not redesign | project registry       | machine refs 需人工/runner核验       |
| `storage.py` / `observability.py`                            | runtime artifact + audit instrumentation | 定义 files，记录 read/settlement audit                  | audit evidence 是 eval substrate，不是 score                 | audit instrumentation  | 缺 per-op outcome/utilization trace  |
| `benchmark_probes.py`                                        | benchmark-only probe exporter            | 生成 MQ snapshots                                       | probe snapshot 是 evaluation artifact，不是 runtime memory   | probe snapshot/export  | 只在 explicit config 下启用          |

------

## B. Upstream Design Basis

- **C设计0 Shared Charter** 转化为本页的三分法：Evaluation / Contract-Audit / Engineering Tests。它要求 source corpus、reading memory、planning state、audit trace、visible reaction、evaluation evidence 分开；也要求 MQ / Callback / FVI 与 Planning eval 不混成一个模糊分数。
- **C设计1 Memory Ontology** 转化为 MQ / FVI 的 store-boundary checks：reaction_records 不是 semantic memory，knowledge_activations 是 warrant ledger，prompt projection 不是 authoritative state。
- **C设计2 Planning Ontology** 转化为 Planning Trace Quality 的边界：Planning 是 reading path / attention scheduling，不是 AutoGPT-style task planning。
- **C设计3 Memory Formation & Settlement** 转化为 per-op settlement outcome 与 SourceRef binding evidence requirement。
- **C设计4 Navigation Policy** 转化为 Navigation Groundedness、Mainline Continuity、detour boundedness。
- **C设计5 Memory Management & Evolution** 转化为 stale memory、supersede / invalidate / cooling / carry-forward diagnostic tags。
- **C设计6 Detour / Look-back / Active Recall** 转化为 active_recall = memory recovery、look_back = source calibration、detour = path deviation 的 eval distinction。
- **C设计7 Retrieval & Utilization** 转化为 utilization trace：retrieval hit ≠ successful utilization；必须记录 items_returned、items_used、no_use_reason、source_refs_used、memory_refs_used。
- **C设计8 Slow-cycle / Macro-planning** 的原始文件本轮未可访问；本页依据用户提供的 C设计8 requirements 与 repo slow-cycle code，仅做最小 safety eval，不展开大型 reflection benchmark。
- **B分析-Memory Assessment** 支持保留 MQ / Callback / FVI，要求 stage-aware attribution，不做过大指标体系。
- **B分析-Planning Assessment** 支持 Planning 侧只做 trace-quality / behavior-quality eval，避免 big planner / multi-agent / ToT/MCTS 默认化。

------

## C. External Rationale, as Filtered Through Assessments

本阶段不重新综述外部研究，只用外部依据支撑本页少数设计判断。

- **LongMemEval** 支持 stage-aware memory evaluation：它把长期记忆问题放在 extraction / indexing / retrieval / reading 等设计选择中考察，因此本页把 MQ 失败归因到 formation / settlement / retrieval / utilization，而不是只看最终分数。([arXiv](https://arxiv.org/abs/2410.10813?utm_source=chatgpt.com))
- **HaluMem** 支持 memory hallucination / pollution 的 operation-level 诊断：其摘要明确指出 hallucination 会在 extraction、updating、QA 阶段发生并传播，因此本页把 FVI 与 stale memory、reaction semanticization、knowledge activation misuse 关联。([arXiv](https://arxiv.org/abs/2511.03506?utm_source=chatgpt.com))
- **LoCoMo / Very Long-Term Conversational Memory** 支持 long-range temporal/causal continuity 评估，但本页不照搬对话 benchmark，而把它过滤成 Second Reader 的 continuity / callback / source-grounding coverage。([arXiv](https://arxiv.org/abs/2402.17753?utm_source=chatgpt.com))
- **AgentBench / WebArena / τ-bench** 支持 agent evaluation 需要看 interactive behavior、trace reliability、multi-turn consistency，而不是只看最终输出；本页只借它们的 trace-quality analogy，不引入 agent task benchmark。([arXiv](https://arxiv.org/abs/2308.03688?utm_source=chatgpt.com))
- **OpenAI Agents SDK tracing** 支持 trace/span 作为调试、可视化、监控的 instrumentation analogy；本页同样把 audit trace 作为 diagnosis，不把它当产品分数或 prompt context。([OpenAI](https://openai.github.io/openai-agents-python/tracing/))
- **Generative Agents / Reflexion** 支持 reflection / slow-cycle 应该位于 observation 之后、episode/chapter boundary 处，而不是每个 unit 都做高层反思；本页因此只做 Slow-cycle Safety eval，不做大型 reflection quality benchmark。([arXiv](https://arxiv.org/abs/2304.03442?utm_source=chatgpt.com))

------

## D. Simplicity and Universality Check

| Check                                     | Result                                                       |
| ----------------------------------------- | ------------------------------------------------------------ |
| 复用现有 eval assets                      | yes：保留 MQ / Callback / FVI、semantic probe manifest、runner、reaction audit、evidence catalog |
| 避免指标泛滥                              | yes：核心仍是 1 个 local/user-level family + 3 个 long-span goals + 2 个轻量 trace/safety families + audit-only coverage |
| 区分 Evaluation / Tests / Contract checks | yes：tests 不进入 product score，audit evidence 不当 score   |
| 避免 full benchmark platform              | yes：只补最小 cases，不重建数据平台                          |
| 避免把 diagnostic tags 变成独立分数       | yes：tags 仅归因                                             |
| 支持 Implementation Handoff               | yes：明确 family、dataset map、rubric adjustments、audit evidence |
| 仍有复杂化风险                            | medium：Planning / Slow-cycle 容易膨胀；必须坚持 small rubric + audit-first |

------

## E. Source Usage List

| External source                                              | Authors / Organization  | Year           | Stable URL                                               | Used for                                          | Support type                                                 |
| ------------------------------------------------------------ | ----------------------- | -------------- | -------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------ |
| LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory | Di Wu et al.            | 2024           | `https://arxiv.org/abs/2410.10813`                       | stage-aware memory evaluation                     | direct analogy ([arXiv](https://arxiv.org/abs/2410.10813?utm_source=chatgpt.com)) |
| HaluMem: Evaluating Hallucinations in Memory Systems of Agents | Ding Chen et al.        | 2025           | `https://arxiv.org/abs/2511.03506`                       | memory-induced hallucination / pollution          | direct analogy ([arXiv](https://arxiv.org/abs/2511.03506?utm_source=chatgpt.com)) |
| Evaluating Very Long-Term Conversational Memory of LLM Agents / LoCoMo | Adyasha Maharana et al. | 2024           | `https://arxiv.org/abs/2402.17753`                       | long-range continuity reference                   | filtered analogy ([arXiv](https://arxiv.org/abs/2402.17753?utm_source=chatgpt.com)) |
| AgentBench                                                   | Xiao Liu et al.         | 2023           | `https://arxiv.org/abs/2308.03688`                       | agent behavior evaluation analogy                 | trace/behavior analogy ([arXiv](https://arxiv.org/abs/2308.03688?utm_source=chatgpt.com)) |
| WebArena                                                     | Shuyan Zhou et al.      | 2023           | `https://arxiv.org/abs/2307.13854`                       | grounded long-horizon agent eval analogy          | trace/behavior analogy ([arXiv](https://arxiv.org/abs/2307.13854?utm_source=chatgpt.com)) |
| τ-bench                                                      | Shunyu Yao et al.       | 2024           | `https://arxiv.org/abs/2406.12045`                       | reliability over repeated interactions            | reliability analogy ([arXiv](https://arxiv.org/abs/2406.12045?utm_source=chatgpt.com)) |
| OpenAI Agents SDK Tracing                                    | OpenAI                  | 2025–2026 docs | `https://openai.github.io/openai-agents-python/tracing/` | trace-based evaluation/instrumentation analogy    | official trace docs ([OpenAI](https://openai.github.io/openai-agents-python/tracing/)) |
| Generative Agents                                            | Joon Sung Park et al.   | 2023           | `https://arxiv.org/abs/2304.03442`                       | reflection / slow-cycle boundary                  | reflection analogy ([arXiv](https://arxiv.org/abs/2304.03442?utm_source=chatgpt.com)) |
| Reflexion                                                    | Noah Shinn et al.       | 2023           | `https://arxiv.org/abs/2303.11366`                       | episode-level reflection, not per-unit reflection | reflection analogy ([arXiv](https://arxiv.org/abs/2303.11366?utm_source=chatgpt.com)) |
