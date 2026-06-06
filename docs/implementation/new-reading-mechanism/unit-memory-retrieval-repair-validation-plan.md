# Unit Memory Retrieval Repair And Validation Plan

Purpose: define the repair and validation track for the current Unit Memory retrieval failure found in the five-window diagnostic run.
Use when: planning, implementing, or validating fixes for `Ingest recalls -> Unit Memory retrieval/selection -> Digest ReadingMemory`.
Not for: redesigning Unit Memory storage from first principles, evaluating subjective Digest quality, or promoting evidence-catalog claims.
Update when: a retrieval repair slice lands, a validation gate passes/fails, or a new retrieval failure category is discovered.

## Status

- Date: `2026-06-06`
- Status: repair-validation in progress.
- Source diagnostic run: `attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5`
- Source audit directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5/analysis/core_mechanism_behavior_audit/`
- Design baseline:
  - `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
  - `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
- Current boundary:
  - do not revive Detour, source-backread, source-skill, concept registry, or thread trace
  - do not inject raw prior source text into Digest as a retrieval workaround
  - do not update the evidence catalog from these repair checks

## Current Progress Snapshot

This track has started implementation, but the retrieval mechanism is not yet goal-complete.

Completed or partially landed repair evidence:

- Phase 0 health packet exists and reproduces the five-window diagnostic failure from artifacts.
- Trace/rendering repair has deterministic coverage: selected-but-not-rendered retrieved candidates are counted separately from hot memory, retrieval-layer suppressed candidates are counted by reason, and candidates without renderable Understanding are suppressed before entering `selected_units`.
- The sqlite-vec load path has been repaired locally: the adapter now enables SQLite extension loading before loading `sqlite_vec`, and a local `vec0` table with cosine distance can be created.
- Dense retrieval has deterministic code-path coverage with a fake embedder: `unit_understanding` vector rows are indexed, query embeddings are cached, sqlite-vec KNN returns dense candidates, distant dense candidates are filtered by `dense_max_distance`, and the selected result can come from the dense channel.
- The local live hybrid path is still blocked by environment because Ollama is not reachable on `127.0.0.1:11434`; therefore real Qwen embeddings, live dense candidates, and live RRF fusion have not been validated.
- `scripts/check_unit_memory_hybrid_readiness.py` now provides a repeatable operator-facing Phase 2 readiness probe. Current local output: sqlite-vec imports/loads and can create a `vec0` table, but Ollama is unreachable, so the configured `qwen3-embedding:0.6b` model and embedding dimension cannot be checked yet.
- Text-only retrieval has deterministic coverage for Chinese recall-meta wording, English concept recall, multi-recall aggregation, and empty-Understanding suppression.
- Runtime boundary / horizon governance has deterministic coverage: a tool-stage `boundary_unresolved` trace no longer prevents runtime retrieval after the source unit has been accepted, and horizon gates record counts rather than only labels.
- A first post-repair no-judge `text_only` smoke on `value_of_others_private_en__segment_1` completed the reading loop but failed the registered wrapper's strict LLM-health gate before summary generation. Its run-local retrieval health packet still showed no prompt-visible retrieved memory and exposed a new root cause: the Runner was passing the whole active Recent Reading Memory store as retrieval exclusions, which excluded all prior units by the end of the run. That exclusion bug was removed, and later post-R9/post-R11 smokes proved retrieved Understanding can become prompt-visible.
- A post-R9 `text_only` diagnostic smoke on `xidaduo_private_zh__segment_1` was intentionally stopped after collecting retrieval-success evidence. Its run-local health packet is `ok`: `57` Unit Memory entries, `353` retrieval docs, `67` retrieval rows, `57` selection rows, `selected_unit_count=71`, `renderable_selected_unit_count=29`, `retrieved_line_total=45`, and `non_renderable_selected_unit_count=0`. This proves the non-hybrid retrieval path can select prior Understanding and render long-distance retrieved lines into Digest `ReadingMemory`.
- The post-R9 retrieved-memory review found mixed relevance: broad Siddhartha / Govinda continuity recall works, but auxiliary surfaces can pull terminology / note-cluster units into prompt-visible `ReadingMemory`.
- Lexical surface weights now prioritize `unit_understanding` over `unit_source`, `unit_annotation`, and `unit_response`, preserving the auxiliary surfaces while restoring Understanding as the primary selection surface.
- `unit_memory_reading_memory_selection` trace now records `rendered_retrieved_units` and `rendered_retrieved_unit_ids`, so future health packets can identify which selected Unit Memory entries actually survived hot-memory dedupe and budget trimming into Digest.
- A post-R10/R11 `text_only` smoke on `xidaduo_private_zh__segment_1` was intentionally stopped after collecting rendered-id evidence. Its run-local health packet is `ok`: `47` Unit Memory entries, `293` retrieval docs, `54` retrieval rows, `47` selection rows, `selected_unit_count=18`, `renderable_selected_unit_count=11`, `retrieved_line_total=6`, and `rendered_retrieved_unique_unit_count=6`. This proves the Understanding-prioritized lexical path still renders prompt-visible retrieved memory and that the new trace fields work in live artifacts.
- Phase 6 prompt calibration is now implemented in Ingest prompt `attentional_v2.ingest.v5` / promptset `attentional_v2-phase6-v55`. The `RecallPriorReading` instruction now tells Ingest to start from the selected unit's primary semantic focus, avoid broad character/protagonist background unless the current unit hinges on it, prefer prior doctrinal/argument/concept content for doctrinal or argumentative units, and return no recall when only a generic recall would be possible.
- A post-Ingest-v5 `text_only` smoke on `xidaduo_private_zh__segment_1` was intentionally stopped after enough recall-specificity evidence was captured. Its run-local health packet is `ok`: `68` Unit Memory entries, `445` retrieval docs, `75` retrieval rows, `68` selection rows, `selected_unit_count=50`, `renderable_selected_unit_count=32`, `retrieved_line_total=27`, and `rendered_retrieved_unique_unit_count=19`. This proves v5 did not disable retrieval and reduced the post-R11 broad Buddha-sermon continuity injection, but it also exposed that later focused recalls can still render overly broad retrieved sets.
- A post-selection-cap `text_only` smoke on `xidaduo_private_zh__segment_1` was intentionally stopped after selection-cap evidence was captured. Its run-local health packet is `ok`: `46` Unit Memory entries, `287` retrieval docs, `49` retrieval rows, `46` selection rows, `selected_unit_count=8`, `renderable_selected_unit_count=7`, `retrieved_line_total=2`, and `rendered_retrieved_unique_unit_count=2`. One mature recall had `15` candidate units, selected `6`, and suppressed `8` with `per_recall_selection_limit_exceeded`; this validates the per-recall cap in `text_only` without clearing retrieved memory.
- Prompt-visible hot-memory exclusion now has deterministic and live `text_only` smoke coverage. Reading Runner computes only the hot current-chapter spans that would already render in Digest `ReadingMemory`, excludes those spans from long-distance Unit Memory retrieval, and records `excluded_source_unit_span_count` in retrieval trace rows. This is deliberately narrower than the old R9 bug: the full active Recent Reading Memory store is not excluded.
- A post-hot-exclusion `text_only` smoke on `xidaduo_private_zh__segment_1` was intentionally stopped after R12 evidence was captured. Its run-local health packet is `ok`: `52` Unit Memory entries, `306` retrieval docs, `57` retrieval rows, `52` selection rows, `selected_unit_count=23`, `retrieved_line_total=23`, `rendered_retrieved_unique_unit_count=11`, `selected_but_not_rendered_count=0`, `excluded_source_unit_span_total=250`, `max_excluded_source_unit_span_count=36`, and `dedupe_hot_memory=0`. This validates that hot-memory exclusion no longer clears retrieved memory and no longer spends selected long-distance slots on hot duplicates in the observed sample.
- Post-hot-exclusion relevance review then exposed the next repair target: once prompt-visible hot memories are correctly excluded, the selection layer can still fill the freed long-distance slots with low-score or broad weak matches. Examples include a water-walking / samana-magic unit receiving childhood or parental-background memories, and a Gotama-doctrine / Govinda-parting unit receiving father-vigil memories. This is now tracked as R13 / Phase 6E: a selection-quality gate is needed so runtime may choose fewer or no long-distance memories instead of filling the budget with weak candidates.
- R13 selection-quality gating is now validated in `text_only` diagnostics: after aggregation and renderability checks, candidates must show strong enough `unit_understanding` evidence or stricter auxiliary-surface evidence before final selection. Weak candidates are suppressed with `candidate_below_selection_quality_threshold`; tests cover both "strong candidate survives while weak filler is suppressed" and "all candidates weak means no long-distance selection"; the post-R13 smoke rendered retrieved Understanding while suppressing weak candidates.
- Ingest prompt `attentional_v2.ingest.v6` / promptset `attentional_v2-phase6-v56` tightened recall contract after that smoke exposed language/basis drift: model-side recall text should use the current source text's primary language, preserve source-form names/terms when available, and keep `basis` exactly `selected_source_unit`.
- A pre-contract Ingest-v6 `text_only` smoke on `xidaduo_private_zh__segment_1` confirmed that prompt wording alone was insufficient: a Chinese source unit produced an English recall with `basis = selected_source_unit`. The run was intentionally stopped and recorded as diagnostic-only.
- The Ingest structured-output contract now validates recall language against the current source text, and the `retrieve_unit_memory` action-tool preflight runs the same validator before retrieval execution. If the model emits a cross-language recall or other contract-violating recall payload, the tool returns `contract_violation` metadata so the forced final-output path can repair the result instead of silently retrieving on a bad recall.
- A post-contract Ingest-v6 `text_only` smoke on `xidaduo_private_zh__segment_1` was intentionally stopped after an early sample. The run-local recall-language review saw zero language violations in reviewed unique recalls and only `selected_source_unit` model-side basis values. Its retrieval health remained `needs_repair` because the run stopped before the long-distance retrieval horizon matured; it is not a replacement for the earlier prompt-visible retrieval smokes.

Current unresolved target:

- The `text_only` path has passed a live diagnostic proof for prompt-visible long-distance retrieved Understanding lines in Digest `ReadingMemory`.
- Understanding-prioritized lexical ranking still retrieves and renders prior Understanding in live artifacts; the remaining text-only issue is relevance calibration, not mechanical renderability.
- The first recall-specificity prompt calibration has been live-smoked in `text_only`: it is partially validated for avoiding the post-R11 sermon-area broad recall, but the remaining relevance problem has moved toward retrieval selection / budget discipline for focused recalls.
- The per-recall selection discipline slice is validated in `text_only` diagnostics: `max_units_per_recall_to_digest_context = 6` capped how many prior Unit Memory entries one recall could send toward Digest `ReadingMemory`, while preserving nonzero prompt-visible retrieved memory.
- The prompt-visible hot-memory exclusion slice is validated in a `text_only` diagnostic smoke: selected long-distance slots were no longer consumed by units that Digest would already receive as hot current-chapter memory, with `selected_but_not_rendered_count=0` and `dedupe_hot_memory=0` in the observed sample.
- The current non-hybrid selection-quality target is now validated in a no-judge `text_only` diagnostic: R13 suppressed weak broad candidates with explicit score/rank/surface-quality reasons while still rendering prompt-visible retrieved Understanding.
- The narrow Ingest v6 language/basis contract is validated by deterministic tests and an observed early live sample. The next non-hybrid target is relevance calibration only if reviewed recalls / rendered memories remain too broad; otherwise the main unresolved target is live hybrid dense validation.
- Hybrid dense retrieval remains environment-blocked because local Ollama / Qwen embedding service is unavailable; the goal should not claim live hybrid success until real Qwen embeddings, dense candidates, and RRF fusion are validated.
- The latest smoke was intentionally stopped before full summary generation, so it is diagnostic repair evidence, not formal evaluation evidence.

Current run-local health packet:

- JSON: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5/analysis/unit_memory_retrieval_health/summary.json`
- Markdown: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5/analysis/unit_memory_retrieval_health/README.md`

## Goal

The repair track is complete only when the current mechanism can demonstrate this live chain:

```text
Ingest memory_recalls[]
-> retrieve_unit_memory tool / runtime retrieval
-> lexical and/or dense candidates
-> selected prior Unit Memory entries with non-empty Understanding
-> top-level Digest ReadingMemory retrieved lines
-> Digest uses current source text plus ReadingMemory
-> settlement writes the new Unit Memory entry
```

The goal is not to guarantee that every unit retrieves memory. The goal is that when prior memory is relevant and available, the retrieval path can find it, select it, render it into Digest, and leave enough trace evidence to explain the outcome.

## Goal Execution Contract

This section is the executable contract for running this repair track in Codex Goal mode. Treat the design baseline documents as locked unless the user explicitly asks to redesign the mechanism. Goal-mode work should fix implementation, tests, prompts, traces, health reports, and stable fact docs so the current design actually works.

### Goal-Mode Objective

Use this objective if the work is launched through Codex Goal mode:

```text
Make the current attentional_v2 Unit Memory retrieval path conform to the locked design: Ingest expresses bounded prior-reading recalls, runtime retrieves/selects prior Unit Memory Understanding, Digest receives prompt-visible ReadingMemory, and settlement writes the new Unit Memory entry. Diagnose and repair implementation, prompt calibration, trace, health-report, and test gaps until the mechanism can demonstrate the path with deterministic fixtures plus a no-judge live smoke. Do not redesign the mechanism, do not update the evidence catalog, and do not revive retired Detour/backread or concept/thread stores.
```

### Goal-Mode Launch Packet

When launching this as a Codex Goal, use the objective above and attach this document as the execution contract. The agent should first read:

- `AGENTS.md`
- `reading-companion-backend/AGENTS.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- this repair plan
- `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
- `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`

The first goal turn should establish the current layer status, not launch a formal evaluation:

1. Check git status and active background jobs.
2. Read the current phase table and identify the smallest independently actionable phase.
3. Run or add deterministic tests before running any live smoke.
4. If a smoke is needed and may exceed `10-15` minutes, register it through the backend job registry and update the run ledger.
5. Treat no-judge smokes as diagnostic evidence only; do not update the evidence catalog.

The goal runner may use this phase order unless a newer phase status in this document makes a step unnecessary:

1. Verify deterministic fixture coverage for ledger, FTS retrieval, selection, renderability, and ReadingMemory injection.
2. Validate `text_only` retrieval mechanics and selection discipline with a no-judge smoke when deterministic coverage is not enough.
3. Validate Ingest recall calibration only after retrieval mechanics can render nonzero retrieved Understanding.
4. Validate hybrid dense retrieval only when sqlite-vec, Ollama reachability, the configured Qwen embedding model, vector rows, dense candidates, and RRF fusion are all observable.
5. Produce a short run-local review packet for every smoke that is used as validation evidence.

Do not let the goal runner convert this document into a moving target. If the implementation fails the locked design, repair the implementation. If a locked design point is genuinely impossible or inconsistent, record a `deferred_design` or `design_ambiguity_blocker`, continue the remaining independent checks, and ask the user before changing the design.

### Goal-Mode End-To-End Checklist

Goal mode should judge the mechanism by observable actions and artifacts, not by subjective reading quality. The executor should keep this checklist open while working and should not stop merely because one row has a finding if later rows can still be exercised.

| Layer | Required observable | Pass condition | If it fails |
| --- | --- | --- | --- |
| Ingest boundary | prompt manifest, Ingest trace, accepted source unit | Ingest selects a forward source boundary and runtime accepts a concrete source unit for Digest | repair boundary prompt/runtime governance, or record `design_ambiguity_blocker` only if the locked boundary contract is internally inconsistent |
| Ingest recalls | final-output tool args and `retrieve_unit_memory` tool traces | recalls are `0-3`, source-language aligned, `basis = selected_source_unit`, and empty recalls are allowed when no specific prior memory is needed | repair Ingest prompt, structured-output validation, or action-tool preflight; do not invent a separate query LLM |
| Retrieval execution | `unit_memory_retrieval_trace.jsonl` | every non-empty recall is either searched, gated with counts, or rejected with a contract reason | repair horizon gates, accepted-unit handoff, or trace completeness |
| Lexical retrieval | Unit Memory SQLite, FTS candidate trace | known-answer text-only recalls can retrieve expected prior units and trace candidate counts | repair FTS docs, tokenizer/query builder, ranking, or thresholds |
| Dense retrieval | sqlite-vec/vector rows/query embedding cache/dense candidate trace | hybrid produces real dense candidates when sqlite-vec, Ollama, and Qwen embeddings are available | repair code-owned adapter/index/cache problems; otherwise mark only the dense path `deferred_environment` and continue non-hybrid checks |
| Selection | selected/suppressed unit trace | selected units are deduped, renderable, Understanding-bearing, quality-gated, and suppressions have explicit reasons | repair aggregation, exclusion, per-recall cap, score/rank/surface-quality policy, or renderability filtering |
| Digest ReadingMemory | Digest prompt manifest and selection trace | prompt-visible memory contains hot Understanding plus any selected long-distance Understanding, and no raw prior source/Response/Annotation | repair ReadingMemory renderer, budget accounting, or hot/retrieved trace separation |
| Digest output | final-output tool args, read audit | Digest returns `understanding`, `response`, and `annotations`; runtime maps Understanding to recent memory | repair Digest prompt/schema/validator/runtime mapping; do not treat subjective phrasing quality as a retrieval blocker |
| Settlement/writeback | Recent Reading Memory, Unit Memory ledger/index rows | the newly digested unit is written back and retrieval docs are derived for later units | repair settlement/index writeback before claiming end-to-end success |
| Review packet | run-local report | selected retrieved Understanding lines, receiving source units, recall texts, and selection reasons are human-readable | add or repair the review packet before using the smoke as validation evidence |

### Goal-Mode Issue Handling

The executor should classify each issue as soon as it is understood, then continue every independent check that remains available.

- Fix immediately when the issue is a clear implementation, prompt-contract, trace, test, or stable-fact mismatch against the locked baseline.
- Record and continue when the issue is subjective quality, relevance nuance, or a design question that does not prevent the mechanism path from being exercised.
- Record and continue non-hybrid phases when hybrid dense validation is blocked only by local service/model availability.
- Do not edit the locked design docs to make a failure disappear. If the design itself seems wrong, write the blocker in this plan or the final report and ask the user before redesigning.
- Do not mark the goal complete from deterministic tests alone when the goal still requires a live no-judge smoke. Deterministic tests can prove code paths; the smoke must prove the live chain is observable.
- Do not mark the goal blocked while any non-blocked layer can still produce useful evidence or receive an allowed repair.

### Goal-Mode Progress Ledger

Every goal run should keep the phase table below current. Each phase update should include:

- status label from `Issue Disposition Labels`
- exact test command, smoke run id, or artifact path used as evidence
- whether the evidence is deterministic, no-judge live diagnostic, or environment check
- what remains unresolved
- whether the next action is implementation, prompt calibration, environment setup, or human review

If the goal reaches a blocker, the final report must distinguish:

- validated non-hybrid path
- unvalidated hybrid path
- environment blockers
- implementation blockers
- prompt/relevance calibration still worth doing
- subjective quality findings that should not block mechanism-conformance completion

### Design Baseline Lock

Goal mode must treat these documents as the test oracle, not as material to redesign during execution:

- `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
- `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`

Allowed document updates inside the goal:

- update this repair plan's phase statuses, blocker notes, and validation evidence
- update stable facts when implementation behavior or operator expectations actually change
- update task registry/current-state references so another agent can resume from the same facts

Disallowed document updates inside the goal:

- change the retrieval architecture, Digest memory packaging, or Ingest/Digest responsibility split to make a failing implementation appear compliant
- relax success criteria after a failed smoke unless the user explicitly changes the goal
- move unresolved implementation problems into design docs as if they were intended behavior

### Completion Definition

The goal is complete only when all of these are true:

1. A no-judge live smoke proves that at least one Digest prompt receives prompt-visible long-distance retrieved Understanding memory.
2. The smoke artifact health report shows:
   - `retrieved_line_total > 0` or an equivalent reviewed retrieved-line metric
   - `renderable_selected_unit_count > 0`
   - every selected-but-not-rendered case has a specific suppression / dedupe / budget reason
   - at least one selected retrieved Unit Memory entry has non-empty Understanding
   - rendered retrieved unit ids are machine-readable in the selection trace or health packet
3. The retrieval trace can explain the path for each recall:
   - skipped intentionally
   - gated by horizon
   - searched with lexical / dense / hybrid channels
   - produced candidates
   - selected or suppressed with reason
   - rendered or not rendered with reason
4. Settlement still writes the newly digested unit into Recent Reading Memory and Unit Memory.
5. Digest `ReadingMemory` remains Understanding-only:
   - no raw prior source text
   - no prior Response
   - no prior Annotation
6. A small human-readable review packet lists the retrieved Understanding lines, the current source units that received them, and the reason those memories were selected.
7. No formal judged eval, evidence-catalog update, Detour/backread revival, or concept/thread memory revival is used to satisfy the goal.

If the mechanism can retrieve and render relevant prior Understanding in `text_only` mode but the local environment cannot support sqlite-vec / Ollama after reasonable repair attempts, the goal may not be marked fully complete. It should instead be reported as:

```text
text_only retrieval path passed; hybrid vector path blocked by environment.
```

Goal mode should then continue through all non-hybrid phases before stopping, and the final report must include the exact hybrid blocker.

### Continue / Pause / Complete Semantics

Goal mode should continue working while any independent repair path remains actionable. A blocker in one layer is not a reason to abandon other layers.

Continue when:

- hybrid dense retrieval is blocked by Ollama / model availability, but text-only retrieval, selection, rendering, trace, or recall prompt calibration can still be tested
- a smoke fails in the registered wrapper because of strict LLM-health or summary-generation problems, but run-local retrieval artifacts are complete enough to diagnose a lower layer
- a prompt calibration issue is found after mechanics are proven, and it can be repaired without changing the locked design
- a retrieved memory line is broad or weakly relevant, but the trace is sufficient to identify whether the cause is recall wording, retrieval weighting, selection, dedupe, or budget rendering

Pause and ask the user only when:

- the next repair would require changing the locked design baseline
- the next repair would require installing or starting external services that the current environment cannot provide automatically
- all remaining failures are subjective quality judgments rather than mechanism conformance gaps
- the repo has unrelated user changes that directly conflict with the needed edit

Mark the goal complete only when the completion definition is satisfied and no required work remains.

Mark the goal blocked only when every remaining actionable path is blocked by the same external condition or design-level decision for at least three consecutive goal turns. Before marking blocked, the final status must state which non-blocked layers were already validated.

### Issue Disposition Labels

Use these labels in phase notes, review packets, and final reports:

- `fixed`: implementation or prompt changed, targeted checks passed, and docs were updated if needed
- `validated`: no change was needed; artifact or test evidence proves the layer already conforms
- `pending_validation`: a fix landed but has not yet been proven in a live smoke or known-answer fixture
- `deferred_environment`: blocked by local dependency such as Ollama / embedding model availability
- `deferred_design`: would require changing the locked mechanism design; ask the user before proceeding
- `deferred_quality`: subjective quality concern outside mechanism-conformance scope
- `not_applicable`: old mechanism surface or non-goal

Do not use `deferred_*` labels to hide a fixable implementation problem. Every deferred issue should include the next evidence that would reopen it.

### Goal-Mode Repair Matrix

Use this matrix to keep automatic repair work on the intended path. The design baseline is the oracle; implementation is repaired to meet it.

| Problem observed | Primary repair layer | Allowed actions | Required evidence | Stop / continue rule |
| --- | --- | --- | --- | --- |
| No Unit Memory entries or retrieval docs are written after Digest settlement | ledger / settlement | fix writeback, entry derivation, artifact paths, trace creation | deterministic writeback test plus run-local sqlite row counts | continue until settlement writes new entry or a repo/runtime blocker prevents writing |
| Retrieval trace exists but candidate counts are zero for obvious known-answer recall | FTS query / lexical index / vector adapter | fix tokenizer/query builder, FTS table wiring, vector degradation handling | known-answer fixture retrieves expected unit id; trace shows channel counts | continue through text-only even if hybrid is environment-blocked |
| Selected units exist but Digest receives no retrieved lines | renderability / ReadingMemory packaging | fix empty-Understanding suppression, hot-memory dedupe reason, token-budget rendering, trace fields | selection trace has render/suppress reasons and Digest prompt manifest contains retrieved Understanding lines | continue until every selected-but-not-rendered case has a machine-readable reason |
| One recall renders a large broad pack of loosely related prior memories | selection / budget discipline | add per-recall cap, score threshold, rank-gap threshold, or selected-set policy; preserve Understanding-only memory | deterministic cap/threshold fixture plus no-judge smoke review of rendered unit ids | continue; this is implementation calibration, not design failure |
| Hot-memory exclusion removes the strongest nearby matches and selection fills long-distance slots with weak broad candidates | selection quality gate | add minimum score/rank/surface-evidence gates, auxiliary-only thresholds, or explicit no-fill behavior; preserve runtime-owned selection | deterministic weak-filler fixture plus post-smoke review showing weak candidates suppressed with reasons | continue; do not rewrite Ingest recall prompt until selection can decline low-quality candidates |
| Ingest emits broad generic recalls where no specific memory is needed | Ingest recall prompt | tune `RecallPriorReading` wording after retrieval mechanics are proven | no-judge smoke review showing fewer generic recalls without disabling useful recalls | continue after selection/rendering mechanics are already validated |
| Hybrid mode degrades to text-only because Ollama or Qwen embedding is unavailable | environment / vector adapter | repair adapter if code-owned; otherwise record service/model blocker and keep text-only validation moving | sqlite-vec import/load check, deterministic fake-embedder dense-path test, Ollama reachability/model check, trace degradation reason | do not stop other phases; report `deferred_environment` for live hybrid only |
| Retrieved memory is visible but subjectively weak or not very helpful | review / prompt calibration | create review packet; tune only if pattern is mechanical or prompt-contract related | examples with source unit, recall, rendered memory, and suspected layer | do not mark goal complete on subjective quality alone, but do not block mechanical validation if chain works |

### Current Selection-Discipline Slice

Status: `validated_text_only_diagnostic`

Repair rule:

- `max_units_per_recall_to_digest_context = 6`
- The total long-distance selection ceiling remains `max_units_to_digest_context = 40`.
- The fixed Digest `ReadingMemory` budgets remain `5K` hot, `10K` retrieved, and `15K` total estimated tokens.
- The per-recall cap applies after unit aggregation and renderability checks, before Digest `ReadingMemory` rendering.
- Suppressed candidates must record `per_recall_selection_limit_exceeded`.

Rationale:

- Post-Ingest-v5 smoke showed that retrieval is no longer mechanically absent, but a single focused recall can still render a large broad memory pack.
- The product goal is not to shrink long-distance memory to a few entries globally. The goal is to prevent one recall from monopolizing prompt-visible memory while allowing multiple specific recalls to cover more of the already-read book.
- This repair does not change Ingest's responsibility, does not expose retrieved content back to Ingest, and does not put prior source / Response / Annotation into Digest.

Acceptance:

- `validated`: deterministic fixture proves one recall that matches many renderable prior units selects no more than the cap and suppresses the rest with `per_recall_selection_limit_exceeded`
- `validated`: trace records `selection_config.max_units_per_recall_to_digest_context`
- `validated`: post-selection-cap no-judge `text_only` smoke showed prompt-visible retrieved Understanding remained nonzero with `retrieved_line_total = 2`
- `partially_validated`: review packet confirms rendered retrieved sets became smaller; relevance is improved by volume control, but recall-language drift and broad recall wording remain follow-up calibration targets

### Allowed Changes

Goal-mode repair may change:

- Unit Memory index and retrieval implementation
- sqlite-vec adapter, vector-table creation, vector catch-up, and embedding-cache code
- Ollama embedding adapter health checks and timeout/degradation handling
- FTS5 query builder, lexical query normalization, and lexical candidate thresholds
- RRF / aggregation / scoring / selection / dedupe logic
- retrieval horizon gates and recent-neighbor exclusion policy
- boundary-governance integration when retrieval should run from the runtime-accepted source unit
- Digest `ReadingMemory` renderer and budget/suppression trace
- retrieval trace shape and health-report scripts
- deterministic tests and no-judge smoke harnesses
- Ingest recall prompt wording, but only after retrieval/search/rendering is proven mechanically functional
- stable facts docs required by the changed behavior

### Disallowed Changes

Goal-mode repair must not:

- restore Detour, source-backread, source-skill, `look_back`, or old source-skill loops
- restore concept registry, thread trace, or content-typed long-memory stores
- inject raw prior source text into Digest as a workaround
- place prior Response or prior Annotation into Digest `ReadingMemory`
- expose retrieved memory content or selected memory ids back to Ingest through tool results
- make Ingest choose final memory entries
- count hot recent memory as long-distance retrieval success
- update the evidence catalog
- run a formal judged evaluation unless the user explicitly asks for it after no-judge retrieval smoke passes

### Known-Answer Fixtures

Before relying on live reading behavior, Goal mode should create or reuse deterministic known-answer fixtures. These fixtures should be tiny and local to tests or scratch health checks; they are not product data.

Minimum fixture set:

1. Chinese lexical exact / near-exact recall
   - prior Unit Memory Understanding contains a distinctive Chinese phrase or named concept
   - recall text should retrieve that prior unit through FTS
2. Chinese paraphrase recall
   - recall text does not share exact wording with the prior Understanding
   - dense retrieval should retrieve the prior unit in hybrid mode
3. English concept recall
   - prior Understanding contains an English claim or definition
   - text-only and hybrid channels should both produce candidates when appropriate
4. Multi-recall aggregation
   - two recalls retrieve overlapping candidate units
   - aggregation dedupes by unit and preserves recall-match metadata
5. Non-renderable candidate defense
   - a retrieval doc matches a unit with empty Understanding
   - final selection suppresses it with `candidate_not_renderable_empty_understanding`
6. Hot-neighbor exclusion
   - a recent unit matches strongly
   - it is excluded or deduped from long-distance retrieved lines because it already belongs to hot memory
7. Boundary fallback
   - the raw boundary attempt is unresolved but runtime accepts a source unit
   - retrieval still runs from the accepted source unit / accepted recalls instead of stopping at `boundary_unresolved`
8. Per-recall selection discipline
   - one recall matches many renderable prior units
   - selection caps prompt-visible candidates for that recall and records `per_recall_selection_limit_exceeded` for the rest
9. Prompt-visible hot-memory exclusion
   - one prior unit is active Recent Reading Memory and would already render as hot Digest `ReadingMemory`
   - another older prior unit matches the same recall
   - long-distance retrieval excludes only the prompt-visible hot span, still selects the older matching unit, and records `excluded_source_unit_span_count`

The fixture pass should verify known expected unit ids, not only nonzero candidate counts.

### Phase Exit Gates

Each phase must leave behind a concrete pass/fail result.

- Phase 0 exits only when the health packet reproduces the five-window diagnostic facts from artifacts.
- Phase 1 exits only when every selected-but-not-rendered candidate has a machine-readable reason.
- Phase 2 exits only when hybrid can show indexed vectors, query embeddings, dense candidates, and RRF fusion on a known-answer case, or the environment blocker is explicitly recorded.
- Phase 3 exits only when text-only known-answer probes retrieve expected prior units.
- Phase 4 exits only when horizon and boundary gates are counted and explainable, and boundary fallback can still run retrieval when an accepted source unit exists.
- Phase 5 exits only when a selected non-empty Understanding can be rendered into Digest `ReadingMemory`.
- Phase 6 exits only when recall prompt calibration is tested after the retrieval path is already mechanically functional.
- Phase 6B exits only when retrieval selection discipline has deterministic coverage and a no-judge smoke proves it does not remove prompt-visible retrieved memory.
- Phase 6C exits only when recall language/basis contract has deterministic coverage and live artifacts no longer show model-side basis drift or same-source-language drift in reviewed recalls.
- Phase 6D has exited for `text_only`: prompt-visible hot-memory exclusion has deterministic coverage and a no-judge smoke proves selected long-distance slots are no longer being spent on hot-memory duplicates in the observed sample.
- Phase 6E exits only when selection quality gating has deterministic coverage and a no-judge smoke or run-local replay proves weak broad candidates can be suppressed without clearing all useful retrieved Understanding.
- Phase 7 exits only when a no-judge smoke shows prompt-visible retrieved Understanding lines and a review packet confirms they are relevant enough for continued reading.

### Phase Status Summary

| Phase | Current status | What is proven | What remains |
| --- | --- | --- | --- |
| Phase 0 | `passed_initial` | The health packet reproduces the five-window failure and separates hot memory, retrieved memory, selected candidates, renderability, vector availability, and degradation facts. | Keep the packet updated as later trace fields change. |
| Phase 1 | `passed_deterministic` | Selected-but-not-rendered candidates are no longer invisible; retrieval-layer suppressed candidates are counted by reason; empty/missing Understanding is suppressed before selection. | Run a fresh post-repair smoke to prove the trace behavior in real artifacts. |
| Phase 2 | `partially_validated_fake_embedder_deferred_environment` | sqlite-vec can be imported and loaded locally after the adapter fix; deterministic fake-embedder coverage proves vector rows, query embedding cache, dense candidates, dense distance filtering, and dense-channel selection work in code. `scripts/check_unit_memory_hybrid_readiness.py` now verifies readiness repeatably; latest local probe shows sqlite-vec `ok` and `ollama_unreachable`. | Ollama/Qwen embedding service must be reachable before real Qwen query embeddings, live dense candidates, and live RRF fusion can be validated. |
| Phase 3 | `passed_deterministic_text_only` | Text-only FTS retrieves known Chinese and English prior Understanding; multi-recall aggregation preserves recall-match metadata; empty-Understanding candidates are suppressed. | Validate with a post-repair no-judge smoke; dense paraphrase remains Phase 2-dependent. |
| Phase 4 | `passed_deterministic` | Runtime retrieval can continue after boundary acceptance even if the earlier tool-stage trace was `boundary_unresolved`; horizon gates now record current unit, recent exclusion, max retrievable unit, prior count, and minimum prior count. | Validate the gate counts in fresh smoke artifacts. |
| Phase 5 | `passed_deterministic` | A selected non-empty Understanding from the real Unit Memory index renders into Digest `ReadingMemory`, and prior Response / Annotation / raw source stay out of prompt-facing memory. | Validate prompt-visible retrieved lines in a no-judge smoke. |
| Phase 6 | `partially_validated_post_ingest_v5_text_only` | Ingest prompt `attentional_v2.ingest.v5` now asks recalls to follow the selected unit's primary semantic focus, avoid broad background recall unless needed, prefer prior doctrinal / argument / concept content for such units, and return empty when only generic recall is possible. A post-v5 text-only smoke rendered retrieved memory later in the run and avoided the post-R11 broad sermon-area recall. | Tighten selection / budget discipline so focused recalls do not expand into large broad life-history retrieved packs; then rerun a small no-judge text-only smoke. |
| Phase 6B | `validated_text_only_diagnostic` | Per-recall selection discipline caps prompt-visible selected units per recall while preserving nonzero retrieved memory; post-selection-cap smoke selected `6` out of `15` candidate units for one recall, suppressed `8` with `per_recall_selection_limit_exceeded`, and rendered `2` retrieved Understanding lines. | Relevance calibration remains possible if reviewed recalls / rendered memories stay too broad; hybrid dense validation remains environment-blocked. |
| Phase 6C | `validated_observed_live_contract_sample` | Ingest prompt `attentional_v2.ingest.v6`, structured-output validation, and action-tool preflight require model-side recalls to use the current source text's primary language and `basis = selected_source_unit`; runtime fallback recalls may still use `runtime_source_text_fallback`. A pre-contract smoke exposed English recall text for a Chinese source unit; a post-contract early stopped smoke observed zero language violations and only `selected_source_unit` basis values in reviewed unique recalls. | Do not treat the early stopped post-contract run as mature retrieval validation; rerun only if later artifacts show language/basis drift again or if a combined contract-plus-mature-retrieval sample is needed. |
| Phase 6D | `validated_text_only_diagnostic` | Reading Runner excludes only prompt-visible hot current-chapter spans from long-distance Unit Memory retrieval and records the exclusion count; a deterministic runner fixture proves a non-hot matching prior unit can still be selected. The post-hot-exclusion smoke rendered `23` retrieved lines from `11` unique units with `selected_but_not_rendered_count=0`, `dedupe_hot_memory=0`, and `max_excluded_source_unit_span_count=36`. | Relevance review/calibration remains possible; live hybrid dense validation remains environment-blocked. |
| Phase 6E | `validated_text_only_diagnostic` | Post-hot-exclusion review proved R12 mechanics but found low-score / weak broad long-distance fills after hot candidates were excluded. R13 adds a content-neutral quality gate: strong `unit_understanding` evidence can pass, auxiliary-only evidence must be stronger, and weak candidates are suppressed with `candidate_below_selection_quality_threshold`. The post-R13 text-only smoke rendered retrieved Understanding while suppressing weak candidates. | Continue relevance review/calibration only if later rendered memories remain broad; live hybrid dense validation remains environment-blocked. |
| Phase 7 | `passed_post_r11_text_only_diagnostic` | Post-R9 and post-R10/R11 `text_only` smokes proved prompt-visible retrieved Understanding lines; rendered retrieved unit ids now appear in live traces; auxiliary-surface-only rendered pollution was reduced in the observed event. | Calibrate recall specificity / relevance; hybrid dense validation remains environment-blocked. |

### External Environment Handling

Hybrid depends on local sqlite-vec and Ollama. Goal mode should handle those as repairable environment dependencies, not as silent degradations.

Required behavior:

- Use `cd reading-companion-backend && .venv/bin/python scripts/check_unit_memory_hybrid_readiness.py` as the first repeatable check for sqlite-vec / Ollama / model / embedding-dimension readiness.
- If sqlite-vec is missing, attempt to install/load it through the backend environment or document the exact unsupported state.
- If Ollama is unavailable, check whether the service is reachable and whether the configured Qwen embedding model is installed.
- If embedding fails, record model name, endpoint, timeout, and error category without printing secrets.
- If hybrid is blocked, continue repairing and validating text-only, selection, rendering, and trace behavior.
- Do not report hybrid success unless dense candidates actually contribute to at least one known-answer retrieval or smoke retrieval.

### Automatic Repair Loop

Use this loop for each phase:

1. Add or identify the smallest test / health check that exposes the current failure.
2. Run it and record the failure layer:
   - ledger/index
   - lexical query
   - vector/embedding
   - fusion/aggregation
   - horizon gate
   - boundary gate
   - selection/renderability
   - budget/rendering
   - Ingest recall prompt
3. Implement the smallest fitting fix.
4. Re-run the targeted checks.
5. Update this document's phase status if the phase passes or a new blocker is discovered.
6. Update stable docs only when behavior or operator expectations changed.
7. Commit the completed slice after checks, following workspace rules.

Goal mode should not stop merely because one layer is blocked if later independent layers can still be validated. For example, a hybrid vector blocker should not prevent text-only fixture tests, selection/rendering fixes, trace improvements, or no-judge text-only smoke from being completed.

### Required Final Deliverables

When Goal mode finishes or reaches a real blocker, it must produce:

- changed-code summary
- changed-doc summary
- tests and checks run
- retrieval health report path
- known-answer fixture result summary
- no-judge smoke run id / path, if run
- hot vs retrieved ReadingMemory summary
- selected retrieved Understanding examples
- unresolved blockers, grouped by:
  - environment
  - implementation
  - prompt
  - evaluation/review

## Next Repair Queue

Continue from the smallest independent checks rather than jumping directly to a formal evaluation:

1. Review R13 post-smoke evidence and continue only targeted relevance calibration if needed:
   - R12 mechanics are validated in `text_only`
   - post-hot-exclusion review found that the selection layer can backfill freed long-distance slots with low-score or broad weak candidates after prompt-visible hot memories are correctly excluded
   - R13 deterministic tests now cover strong Understanding evidence, weak filler suppression, and no-fill behavior when all candidates are weak
   - post-R13 text-only diagnostic evidence shows weak candidates suppressed with machine-readable reasons while useful retrieved Understanding still renders
   - next action is review/calibration only if the selected rendered memories remain too broad in the R13 review packet
2. Validate Ingest v6 recall language/basis tightening only if needed:
   - post-selection-cap smoke proved volume control works and retrieved memory remains prompt-visible
   - the same smoke exposed Chinese-source recalls written in English and model-side `basis` drift
   - Ingest v6 plus structured-output validation and action-tool preflight now require recall text in the current source text's primary language and model-side `basis = selected_source_unit`
   - a post-contract early stopped smoke observed zero reviewed language violations and no basis drift; rerun only if later artifacts show drift again or if a combined contract-plus-mature-retrieval sample is needed
   - preserve the policy that Digest `ReadingMemory` contains Understanding only
3. Attempt Phase 2 only when environment can support it:
   - sqlite-vec load works
   - Ollama is reachable
   - configured Qwen embedding model is available
   - query embedding cache and vector rows become nonzero
4. If recall-specificity tuning lands, rerun a small no-judge `text_only` smoke and compare rendered retrieved unit ids against the post-hot-exclusion review packet.

Do not tune Ingest recall wording until search, selection, renderability, and trace mechanics have been proven with deterministic cases. Otherwise prompt changes may hide mechanical retrieval failures.

## Current Failure Summary

The five-window diagnostic proved that the retrieval surface is structurally present but not mechanism-effective.

Observed facts from the audit:

- `ReadingMemory` was rendered for Digest, but it contained hot recent memory only.
- Across `531` Digest calls, `retrieved_line_count` was always `0`.
- Across `576` retrieval trace rows, only `1` retrieved unit was selected.
- The only selected retrieved unit was not renderable because its stored Understanding was empty.
- Configured mode was `hybrid`, but actual search attempts degraded to `text_only` because `sqlite_vec` was unavailable.
- `244` actual search rows produced only `1` lexical candidate unit and `0` dense candidates.

Therefore the current failure is not "no trace files" or "no Unit Memory ledger". The failure is that the path from recall to prompt-visible retrieved Understanding does not form a working loop.

## Failure Taxonomy

### R1. Prompt-visible retrieved memory is zero

Symptom:

- `unit_memory_reading_memory_selection` rows exist, but every row has `retrieved_line_count = 0`.
- Digest receives only hot current-chapter memory.

Likely causes:

- no candidates
- no selected units
- selected units are not renderable
- selection-to-rendering reasons are not explicit enough

Repair direction:

- add an invariant that separates `selected_unit_count`, `renderable_selected_unit_count`, and the retrieved-line metric such as `retrieved_line_total`
- record why each selected candidate is rendered or suppressed
- treat `selected_unit_count > 0` with zero retrieved lines as a diagnostic failure unless every selected unit has an explicit suppression / dedupe / budget reason

### R2. Hybrid mode degrades before dense retrieval is tested

Symptom:

- `memory_retrieval_config.mode = hybrid`
- no sqlite-vec vector table is present
- `query_embedding_cache` is empty
- all actual search rows that reach vector search degrade with `sqlite_vec_unavailable`

Repair direction:

- make sqlite-vec availability a first-class health check
- make Ollama embedding availability and model dimension a first-class health check
- require at least one controlled hybrid smoke where:
  - `unit_understanding` vector rows are indexed
  - query embeddings are cached
  - dense candidates are nonzero for a known query
  - RRF sees both lexical and dense channels

### R3. Text-only fallback is too weak

Symptom:

- after vector degradation, FTS5 fallback technically runs but barely returns candidates
- `244` actual text-only search rows yielded only `1` candidate unit

Likely causes to inspect:

- recall text is too paraphrastic for lexical matching
- query builder may be too strict
- Chinese trigram matching may be underused or filtered away
- FTS candidate thresholds may be too high
- retrieval documents may be present but not queryable in the intended way

Repair direction:

- build deterministic text-only probes against known prior Understanding/source terms
- inspect the generated FTS SQL and query text
- tune FTS query construction before changing the Unit Memory entry shape
- keep all retrieval docs in FTS, but preserve the current policy that only Understanding enters Digest

### R4. Retrieval horizon gates suppress too much

Symptom:

- `recent_neighbor_exclusion_unit_count = 20`
- `min_retrievable_prior_units = 20`
- early and short windows produce many `not_enough_prior_units_after_recent_exclusion` and `below_min_retrievable_prior_units` rows

Repair direction:

- replace fixed `20 + 20` assumptions with a window-aware policy
- make the gate explainable in trace:
  - current unit index
  - prior unit count
  - excluded hot-neighbor count
  - remaining retrievable count
  - exact reason no retrieval was attempted
- allow a shorter exclusion horizon in short windows or early chapters while still avoiding duplicate hot memory

### R5. Boundary unresolved blocks retrieval before search

Symptom:

- `boundary_unresolved` rows stop before candidate search
- recall retrieval is made dependent on exact boundary resolution that is already handled later by runtime boundary governance

Repair direction:

- run retrieval from the runtime-accepted source unit after boundary resolution/retry/fallback
- decouple recall search from the raw tool boundary anchor when runtime has a usable accepted source unit
- keep `boundary_unresolved` as a trace reason for the boundary attempt, not as a reason to skip all retrieval when accepted source text exists

### R6. Recall trigger and recall wording need calibration

Symptom:

- some substantive units have no recall
- some recalls may be too abstract, future-facing, or temporally confused
- no-recall rows should not all count as failures, but recall absence must be reviewable

Repair direction:

- keep `memory_recalls[]` optional
- calibrate Ingest to recall when the selected unit naturally returns to:
  - a person
  - relationship
  - concept
  - question
  - object
  - image
  - argument
  - unresolved pressure
- do not ask Ingest to list every noun
- reject or repair recalls that refer to future material not yet in the accepted Unit Memory ledger

### R7. Selected entries must be renderable Understanding

Symptom:

- the single selected retrieved unit matched `unit_source`, but its Digest Understanding was empty
- Digest `ReadingMemory` only renders Understanding, so the selected entry produced no prompt-visible memory

Repair direction:

- selection may use all retrieval docs, but selected units must have non-empty Understanding to enter Digest
- filter empty-Understanding entries before final selection
- if a source/response/annotation doc matches a unit with empty Understanding, record `candidate_not_renderable_empty_understanding`
- rely on the structured-output repair to reduce new empty Understanding, but keep this retrieval-side guard anyway

### R8. Observability currently lets hot memory hide retrieval failure

Symptom:

- Digest prompt has a `ReadingMemory` block, so a casual check can conclude memory injection worked
- in reality, retrieved long-distance memory was zero and hot memory supplied all lines

Repair direction:

- always report hot and retrieved memory separately
- do not treat `ReadingMemory` presence as retrieval success
- add hard counters to smoke reports:
  - `hot_line_count`
  - retrieved-line total / per-row retrieved-line counts
  - `selected_unit_count`
  - `renderable_selected_unit_count`
  - `selected_but_not_rendered_count`

### R9. Whole active Recent Memory was used as a retrieval exclusion set

Symptom:

- A first post-repair `text_only` smoke on `value_of_others_private_en__segment_1` completed the read loop, but the retrieval health packet still showed:
  - `selected_unit_count = 0`
  - `renderable_selected_unit_count = 0`
  - `retrieved_line_total = 0`
- Manual FTS checks against the same `unit_memory.sqlite` could match prior units for the recall text.
- The runtime `recent_reading_memory.json` contained active entries for almost every prior unit, so passing all active recent-memory source spans into retrieval exclusions removed the entire retrievable prior-unit set.

Root cause:

- The Runner conflated "hot memory should not be duplicated in the Digest prompt" with "all active Recent Reading Memory source spans should be excluded from Unit Memory retrieval".
- Because active Recent Reading Memory accumulates through the chapter, the exclusion set grew until it covered nearly all prior units.

Repair:

- Do not pass the whole active Recent Reading Memory store as `excluded_source_unit_span_ids` to Unit Memory retrieval.
- Let UnitMemoryIndex horizon gates exclude only direct recent neighbors for long-distance retrieval.
- Let Digest `ReadingMemory` rendering dedupe retrieved lines against hot memory, rather than preventing retrieval from seeing the whole prior ledger.
- Post-R9 and post-R11 no-judge `text_only` smokes validated that prior Understanding candidates can now be selected and rendered.

### R10. Auxiliary retrieval surfaces outweighed Understanding in lexical ranking

Symptom:

- Post-R9 `text_only` review showed prompt-visible retrieved memory, but some retrieved units were terminology / note-cluster units selected through auxiliary surfaces such as `unit_response`.
- Examples included current doctrinal or selfhood passages receiving earlier Upanishad / term-note units as retrieved `ReadingMemory`.
- The code gave `unit_source` and `unit_annotation` higher lexical weights than `unit_understanding`, which contradicted the current design that Understanding is the primary retrieval and prompt-facing memory surface.

Repair:

- Lexical weights now prioritize `unit_understanding`.
- `unit_source`, `unit_annotation`, and `unit_response` still participate in FTS retrieval, but as auxiliary cue surfaces.
- A deterministic test now verifies that when the same recall phrase matches one unit's source text and another unit's Understanding, the Understanding match ranks first.

Validation:

- A post-R10/R11 no-judge `text_only` smoke showed prompt-visible retrieved memory still worked and rendered retrieved unit ids were traceable. Relevance improved by restoring Understanding as the primary surface, but further recall/selection calibration remains separate follow-up work.

### R11. Selection trace did not identify rendered retrieved unit ids

Symptom:

- Retrieval trace rows listed `selected_units`, and ReadingMemory selection rows listed `retrieved_line_count`, but the trace did not identify which selected Unit Memory ids survived hot-memory dedupe and budget trimming into prompt-visible Digest `ReadingMemory`.
- This made relevance review depend on inference from adjacent rows rather than direct trace evidence.

Repair:

- `unit_memory_reading_memory_selection` rows now record `rendered_retrieved_units`, `rendered_retrieved_unit_ids`, and `rendered_hot_units`.
- The health script reports `rendered_retrieved_unique_unit_count` and rendered retrieved ids when available.

Validation:

- Post-R11 and post-selection-cap smoke artifacts confirmed the new fields appear in fresh runtime traces and health packets.

### R12. Prompt-visible hot memory consumed long-distance selection slots

Symptom:

- A post-selection-cap review showed a mature recall selecting several prior units, but only two retrieved lines reached Digest `ReadingMemory`.
- Many selected units were later suppressed as `dedupe_hot_memory`, because they were already present in the hot current-chapter memory block.
- This wasted long-distance selection capacity on information Digest would already see.

Root cause:

- After R9, retrieval correctly stopped excluding the whole active Recent Reading Memory store.
- However, the retrieval layer also stopped excluding the narrower set of hot current-chapter spans that were already prompt-visible for Digest.
- The renderer could dedupe them after selection, but that happened too late to free the selection slots for older long-distance memories.

Repair:

- Before Unit Memory retrieval, Reading Runner computes only the hot current-chapter memory lines that would already render in Digest `ReadingMemory`.
- It passes those source span ids as `excluded_source_unit_span_ids` to retrieval.
- It does not pass the whole active Recent Reading Memory store.
- Retrieval traces record `excluded_source_unit_span_count`.

Validation:

- `validated`: deterministic runner fixture proves that a prompt-visible hot matching span is excluded while a non-hot matching prior unit remains retrievable and selected.
- `validated_text_only_diagnostic`: post-hot-exclusion smoke health packet is `ok`, with `retrieved_line_total=23`, `rendered_retrieved_unique_unit_count=11`, `selected_but_not_rendered_count=0`, `excluded_source_unit_span_total=250`, and `dedupe_hot_memory=0`.

### R13. Selection fills freed slots with weak broad candidates

Symptom:

- After R12, selected long-distance slots are no longer wasted on memories that Digest already receives as hot current-chapter `ReadingMemory`.
- The post-hot-exclusion review found a new failure mode: when the most direct recent matches are correctly excluded, selection can still backfill the available long-distance slots with weak broad candidates.
- Example pattern:
  - a current unit about Siddhartha rejecting water-walking and samana magic selected broad childhood / parental / general quest memories
  - a current unit about Gotama doctrine, Govinda joining the Buddha, or Siddhartha parting from Govinda selected weak father-vigil or general early-life memories

Root cause hypothesis:

- Selection currently treats a renderable non-hot candidate as eligible even when its fused score, matched surface, or per-recall evidence is too weak.
- The per-recall cap controls volume, but it does not decide whether the tail candidates are good enough to include at all.
- Auxiliary FTS surfaces are useful cues, but they can still promote a unit whose prompt-facing Understanding is only broadly related.

Repair direction:

- Add an explicit selection-quality gate after aggregation and renderability checks, before final prompt-facing selection.
- Allow runtime to select fewer than the cap when candidates are weak; an empty retrieved-memory result is better than filling Digest with broad low-value continuity.
- Candidate gate policies may include:
  - minimum selected-unit fused score
  - maximum acceptable rank or minimum score on `unit_understanding`
  - stricter threshold for auxiliary-only matches
  - suppression when a candidate has only broad protagonist / background overlap and no strong Understanding evidence
- Every suppressed candidate must record a machine-readable reason such as `candidate_below_selection_quality_threshold`.

Validation:

- deterministic fixture: a recall returns one strong Understanding-bearing candidate and several weak auxiliary / broad candidates; selection keeps the strong candidate and suppresses weak fillers with reasons
- deterministic fixture: when all candidates are weak, selection may return no long-distance retrieved units while the trace explains why
- no-judge smoke or run-local replay: post-hot-exclusion style events show fewer weak broad retrieved lines without clearing useful prompt-visible retrieved Understanding

## Golden Path Invariants

Every repair slice should preserve these invariants:

1. Settlement writes one Unit Memory entry per accepted source unit.
2. Retrieval documents are derived from the Unit Memory entry and are rebuildable.
3. All valid retrieval docs participate in FTS.
4. Only `unit_understanding` participates in dense vector retrieval.
5. Ingest can express zero to three recalls, but does not see retrieved memory content.
6. Runtime owns retrieval, selection, dedupe, budget trimming, and rendering.
7. Digest receives prior memory only through top-level `ReadingMemory`.
8. Digest `ReadingMemory` contains Understanding memory only, not raw prior source, prior Response, or prior Annotation.
9. Hot current-chapter memory and selected long-distance memory are distinguishable in trace and validation.
10. Long-distance retrieval excludes prompt-visible hot current-chapter spans, but must not exclude the whole active Recent Reading Memory store.
11. If selected retrieved memory does not enter Digest, the trace must say why.
12. Selection should not fill long-distance memory slots with weak candidates merely because budget remains; low-quality suppression is acceptable and should be traceable.

## Repair Phases

### Phase 0. Baseline Reproduction And Health Packet

Status: `passed_initial`

Current evidence:

- added `reading-companion-backend/scripts/diagnose_unit_memory_retrieval_health.py`
- generated run-local health artifacts for `attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5`
- reproduced the diagnostic failure:
  - `531` Unit Memory entries
  - `576` retrieval rows
  - `retrieved_line_total = 0`
  - `selected_unit_count = 1`
  - `renderable_selected_unit_count = 0`
  - `query_embedding_cache_rows = 0`
  - `vector_rows = 0`

Goal:

- create a small deterministic health packet that can reproduce the current retrieval failure categories without running a full judged eval

Work:

- add or reuse scripts that read `unit_memory.sqlite`, `unit_memory_retrieval_trace.jsonl`, Digest prompt manifests, and `read_audit.jsonl`
- produce one compact retrieval health report per run
- verify that the five-window diagnostic facts above are reproducible from artifacts

Acceptance:

- the report can distinguish:
  - hot memory lines
  - retrieved memory lines
  - selected units
  - renderable selected units
  - vector availability
  - lexical candidate counts
  - gate/degradation reasons

### Phase 1. Trace And Invariant Repair

Status: `passed_deterministic`

Current evidence:

- Digest `ReadingMemory` rendering records suppression reasons when selected units are missing an entry, missing Understanding, or have empty Understanding.
- Unit Memory retrieval now suppresses candidates without renderable Understanding before final selection and records them in `suppressed_units`.
- The health packet reports selected-but-not-rendered counts separately from hot/retrieved line totals and reports retrieval-layer suppression reason counts.

Goal:

- make retrieval failures visible at the exact boundary where they happen

Work:

- enrich retrieval trace with renderability reasons
- record selected-but-not-rendered suppressions
- add smoke assertions for `selected_unit_count > 0` and zero retrieved lines
- make `ReadingMemory` prompt-manifest inspection report hot vs retrieved separately

Acceptance:

- no run can pass retrieval smoke merely because `ReadingMemory` exists
- every unrendered selected candidate has a machine-readable reason

### Phase 2. Hybrid Vector Path Repair

Status: `partially_validated_fake_embedder_deferred_environment`

Current evidence:

- `sqlite-vec` is declared in `pyproject.toml`.
- Current venv initially lacked `sqlite_vec`; installing `sqlite-vec>=0.1.6` fixed the import.
- The sqlite-vec adapter now enables SQLite extension loading before calling `sqlite_vec.load(...)`; vec0 table creation with `distance_metric=cosine` is locally verified.
- Deterministic fake-embedder coverage verifies the code path that writes `unit_understanding` vector rows, caches query embeddings, runs sqlite-vec KNN, filters distant dense candidates with `dense_max_distance`, and selects a dense-channel result.
- Current machine does not have the `ollama` command and `127.0.0.1:11434` is not serving embeddings, so real Qwen query embedding / live dense retrieval remains environment-blocked.

Goal:

- make `hybrid` mean actual lexical + dense retrieval when the environment supports it

Work:

- fix or document sqlite-vec installation/loading for the backend venv
- validate vector table creation in `unit_memory.sqlite`
- validate Ollama embedding availability and Qwen3 embedding dimension
- build/catch up vectors for `unit_understanding`
- cache query embeddings
- record dense candidate counts in trace

Acceptance:

- a controlled hybrid smoke shows:
  - sqlite-vec table present
  - `unit_understanding` vector rows indexed
  - query embedding cache nonzero after retrieval
  - at least one dense candidate returned for a known prior-memory query
  - effective search channel is not only text-only
- deterministic fake-embedder coverage can prove the adapter and sqlite-vec code path, but it does not satisfy live hybrid acceptance until the local Ollama/Qwen service is available

### Phase 3. Text-Only Retrieval Repair

Status: `passed_deterministic_text_only`

Current evidence:

- FTS query builder now removes recall-meta wording such as `先前阅读中`, `Earlier reading`, `Paragraph N`, and `recall`.
- FTS query builder now adds English keyword phrases and Chinese three/four-character chunks so text-only retrieval can match paraphrastic recall wording more often.
- A known-answer text-only test now verifies that a recall like `先前阅读中悉达多对佛陀法义的态度和评价` retrieves the prior unit whose Understanding discusses `悉达多` and `佛陀法义`.
- A known-answer English concept test verifies that a recall like `Earlier reading about perceived attractiveness and valuation` retrieves the expected prior Understanding.
- Multi-recall aggregation continues to select expected units and preserve `matched_recalls`.
- Empty-Understanding candidates are suppressed instead of being selected.

Goal:

- make `text_only` a useful fallback rather than a mostly empty path

Work:

- inspect FTS tokenizer and query builder behavior for Chinese and English
- create known-answer lexical probes from stored Unit Memory entries
- tune query normalization, phrase splitting, OR/AND strategy, and candidate thresholds
- keep FTS retrieval docs broad, while final Digest context remains Understanding-only

Acceptance:

- text-only probes can retrieve known prior units by:
  - exact or near-exact terms
  - short Chinese phrases
  - English definitions or claims
  - names / repeated concepts
- fallback mode reports useful lexical candidates before dense retrieval is considered

### Phase 4. Horizon And Boundary Governance Repair

Status: `passed_deterministic`

Current evidence:

- Runtime retrieval no longer returns the stale tool result when the only existing tool trace is `boundary_unresolved`.
- After runtime accepts a source unit, the same `memory_recalls[]` can run through normal retrieval even if the tool-stage boundary anchor was unresolved.
- Horizon gate traces now include `current_unit_index`, `recent_neighbor_exclusion_unit_count`, `max_retrievable_unit_index`, `prior_units_after_recent_exclusion`, and `min_retrievable_prior_units` where applicable.

Goal:

- stop suppressing valid recall searches due to overly rigid early gates or boundary-resolution coupling

Work:

- make recent-neighbor exclusion and minimum prior count adaptive
- separate hot-memory duplication avoidance from long-distance retrievability
- execute retrieval against the accepted runtime source unit after boundary governance
- prevent `boundary_unresolved` from blocking retrieval when accepted source text exists

Acceptance:

- short windows can produce long-distance retrieval once enough non-hot prior units exist
- boundary fallback units can still trigger retrieval using accepted source text or accepted recalls
- trace explains each gate decision with counts, not just labels

### Phase 5. Selection And Digest Rendering Repair

Status: `passed_deterministic`

Current evidence:

- Unit Memory retrieval suppresses empty/missing Understanding before final selection.
- Digest `ReadingMemory` rendering still records defensive suppression reasons for malformed selected-unit payloads.
- A runner-level deterministic test writes a Unit Memory entry, retrieves it through the real index, and verifies that the selected non-empty Understanding renders as a retrieved `ReadingMemory` line while prior Response and Annotation remain excluded.

Goal:

- ensure selected retrieved memories are actually usable by Digest

Work:

- require selected long-distance memory entries to have non-empty Understanding
- dedupe selected retrieved entries against hot memory entries
- keep whole Understanding lines under the long-distance memory budget
- record budget suppressions separately from score suppressions

Acceptance:

- when a selected retrieved entry is non-empty and within budget, it appears as a retrieved line in Digest `ReadingMemory`
- selected-but-not-rendered count is zero except for explicitly justified budget or renderability reasons
- Digest prompt manifests show both hot and retrieved line counts when both exist

### Phase 6. Ingest Recall Calibration

Status: `partially_validated_post_ingest_v5_text_only`

Current evidence:

- Prompt calibration landed in `attentional_v2.ingest.v5` / promptset `attentional_v2-phase6-v55`.
- The updated `RecallPriorReading` prompt keeps the reader-shaped recall framing but adds specificity guidance:
  - start from the selected unit's primary semantic focus
  - avoid broad character background / protagonist history unless the current unit hinges on it
  - prefer prior doctrinal, argumentative, conceptual, or methodological content for units whose main focus is teaching / claim / concept / method
  - return no recall when only a generic recall would be possible
- Post-Ingest-v5 text-only smoke:
  - run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606`
  - job id: `bgjob_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606`
  - intentionally stopped after diagnostic evidence; no summary aggregate/report/usage files are present
  - health packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606/analysis/unit_memory_retrieval_health/summary.json`
  - review packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606/analysis/unit_memory_retrieval_review/README.md`
  - health status `ok`: `68` Unit Memory entries, `445` retrieval docs, `75` retrieval rows, `68` selection rows, `selected_unit_count=50`, `renderable_selected_unit_count=32`, `retrieved_line_total=27`, and `rendered_retrieved_unique_unit_count=19`
  - interpretation: v5 reduced the post-R11 broad Buddha-sermon continuity injection and still allowed later retrieval, but some later focused recalls still rendered large broad retrieved sets

Goal:

- improve recall intent frequency and wording only after retrieval can actually search and render

Work:

- review recall examples after Phases 1-5
- tune `RecallPriorReading` prompt if recalls are too sparse, too abstract, noun-list-like, or future-facing
- preserve the zero-recall option for genuinely local new information

Acceptance:

- recalls are produced for obvious returns to prior persons, concepts, images, claims, and unresolved pressures
- no-recall units are reviewable and generally defensible
- recall wording is standalone enough for retrieval without becoming a mechanical keyword list
- rendered retrieved Unit Memory after the next smoke is not dominated by broad protagonist / character-background continuity when the current source unit's primary focus is doctrinal, argumentative, conceptual, or methodological

Current disposition:

- `validated`: v5 did not shut retrieval off; prompt-visible retrieved lines still appear.
- `validated`: the post-R11 sermon-area broad Siddhartha / Govinda continuity injection was reduced in the reviewed event.
- `pending_validation`: whether v5 recall wording is robust across books and languages.
- `fixed_pending_validation`: retrieval selection / budget discipline now has a deterministic R13 quality gate, but focused-recall live artifacts still need smoke/replay validation.

Post-v6 follow-up:

- Ingest prompt `attentional_v2.ingest.v6` / promptset `attentional_v2-phase6-v56` was added after post-selection-cap smoke exposed recall-language and basis drift.
- `fixed`: structured-output validation now checks recall language against the current source text and rejects model-side basis values other than `selected_source_unit`.
- `fixed`: `retrieve_unit_memory` action-tool preflight applies the same validator before retrieval execution and returns `contract_violation` metadata for repair when the action payload violates the contract.
- `validated_observed_live_contract_sample`: pre-contract smoke `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_20260606` exposed one English recall for a Chinese source; post-contract smoke `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606` observed zero language violations in reviewed unique recalls and only `selected_source_unit` basis values.
- `pending_validation`: the post-contract smoke stopped early, so it does not prove prompt-visible retrieved memory in the same run; use the earlier post-R9/R11/post-selection-cap smokes for text-only renderability proof.

### Phase 6E. Selection Quality Gate

Status: `validated_text_only_diagnostic`

Current evidence:

- The post-hot-exclusion `text_only` smoke validated R12 mechanics: hot prompt-visible current-chapter spans were excluded before long-distance selection, retrieved lines remained prompt-visible, and `dedupe_hot_memory=0`.
- Manual review of the four selected/rendered retrieval events in that smoke found that some rendered long-distance memories were only broad continuity:
  - water-walking / samana-magic rejection received childhood, parental, or general quest memories
  - Gotama doctrine / Govinda parting received father-vigil or general early-life memories
- These examples are not a reason to restore broad hot exclusions. They show that the selection layer needs a quality gate that can decline weak long-distance candidates after hot candidates are correctly removed.
- Deterministic tests now cover the quality gate:
  - a weak broad candidate with low Understanding evidence is suppressed even when it has a higher aggregate score than a strong Understanding-bearing candidate
  - when all candidates are weak, runtime can select no long-distance Unit Memory entries
- Current default gate settings:
  - `min_understanding_doc_score_to_digest_context = 0.019`
  - `max_understanding_doc_rank_to_digest_context = 12`
  - `min_auxiliary_unit_score_to_digest_context = 0.08`
  - `max_auxiliary_doc_rank_to_digest_context = 6`
- Current live validation attempt:
  - run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r13_20260606`
  - job id: `bgjob_unit_memory_text_only_smoke_xidaduo_post_r13_20260606`
  - segment: `xidaduo_private_zh__segment_1`
  - mode: `text_only`
  - status: `diagnostic_intentionally_stopped_after_r13_evidence`
  - health packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r13_20260606/analysis/unit_memory_retrieval_health/README.md`
  - review packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r13_20260606/analysis/unit_memory_r13_selection_quality_review/README.md`
  - observed result: health status `ok`; `48` Unit Memory entries, `273` retrieval docs, `54` retrieval rows, `48` selection rows, `selected_unit_count=6`, `renderable_selected_unit_count=6`, `retrieved_line_total=6`, `rendered_retrieved_unique_unit_count=6`, `selected_but_not_rendered_count=0`, and `candidate_below_selection_quality_threshold=11`
  - interpretation: R13 suppressed weak candidates with explicit quality-gate reasons while preserving prompt-visible retrieved Understanding in the observed text-only sample; the run was intentionally stopped after diagnostic evidence and has no summary aggregate/report/usage files

Goal:

- prevent Unit Memory selection from filling Digest `ReadingMemory` with low-value long-distance memories merely because candidates are renderable, non-hot, and within budget

Work:

- inspect current aggregation scores, per-surface matches, per-recall ranks, and selected/suppressed trace shape
- add the smallest deterministic gate that separates strong continuity from weak filler
- prefer content-neutral gating signals such as score, rank, surface evidence, and matched Understanding strength; do not introduce a new content taxonomy
- record suppression reasons for every candidate removed by the quality gate
- keep Digest `ReadingMemory` Understanding-only and keep Ingest outside final memory selection

Acceptance:

- `validated`: deterministic fixture proves a strong Understanding-bearing candidate survives while weak broad candidates are suppressed
- `validated`: deterministic fixture proves runtime can select no long-distance memories when all candidates are weak
- `validated`: trace includes a specific quality-gate suppression reason and enough score/surface metadata to review the decision
- `validated_text_only_diagnostic`: the post-R13 smoke showed R13 does not regress the already validated text-only ability to render useful retrieved Understanding lines

Goal-mode R13 validation checklist:

1. Generate or inspect a run-local health packet for the R13 smoke / replay.
2. Confirm `selection_config` in retrieval traces records the quality-gate thresholds above.
3. Confirm weak suppressed candidates include `candidate_below_selection_quality_threshold`.
4. Confirm selected/rendered retrieved lines, if any, are backed by strong enough `unit_understanding` evidence or stricter auxiliary evidence.
5. Confirm the gate may select fewer than the cap, including zero long-distance memories for a unit, without treating that as failure.
6. Confirm no raw prior source, prior Response, or prior Annotation enters Digest `ReadingMemory`.
7. If the smoke has no prompt-visible retrieved lines, distinguish:
   - legitimate no-fill because all candidates were weak
   - no mature long-distance retrieval horizon
   - retrieval/search failure
   - renderability/budget failure
8. Do not change Ingest recall wording until this selection-quality layer is either validated or its remaining failure is clearly not selection-owned.

### Phase 7. End-To-End Diagnostic Validation

Status: `passed_post_r11_text_only_diagnostic`

Current evidence:

- Pre-R9 failed smoke:
  - run id: `attentional_v2_unit_memory_text_only_smoke_value_20260606`
  - job id: `bgjob_unit_memory_text_only_smoke_value_20260606`
  - segment: `value_of_others_private_en__segment_1`
  - mode: `text_only`
  - underlying read loop completed, but wrapper exited `1` because strict LLM-health validation reported `llm_fallback_events_present`
  - health packet remained `needs_repair`: `50` Unit Memory entries, `228` retrieval docs, `63` retrieval rows, `50` selection rows, `selected_unit_count=0`, `renderable_selected_unit_count=0`, `retrieved_line_total=0`
  - exposed R9: all active Recent Reading Memory source spans were passed into retrieval exclusions
- Post-R9 passing diagnostic:
  - run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606`
  - job id: `bgjob_unit_memory_text_only_smoke_xidaduo_post_r9_20260606`
  - segment: `xidaduo_private_zh__segment_1`
  - mode: `text_only`
  - intentionally stopped after retrieval-success evidence was collected; summary aggregate/report/usage files are absent
  - health packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606/analysis/unit_memory_retrieval_health/summary.json`
  - review packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606/analysis/unit_memory_retrieval_review/README.md`
  - health status `ok`: `57` Unit Memory entries, `353` retrieval docs, `67` retrieval rows, `57` selection rows, `selected_unit_count=71`, `renderable_selected_unit_count=29`, `retrieved_line_total=45`, `non_renderable_selected_unit_count=0`
  - `selected_but_not_rendered_count=26` is explained by `dedupe_hot_memory`
- Post-R9 relevance review:
  - report: `docs/implementation/new-reading-mechanism/codex/reports/UnitMemory-Retrieval-TextOnly-PostR9-Relevance-Review v0.md`
  - strong continuity examples exist, especially Siddhartha / Govinda path and self-seeking recall
  - auxiliary-surface pollution exists: source / response / annotation matches can select terminology or note-cluster units whose Understanding is weak continuity support
- Post-review repair:
  - R10 lexical weights now prioritize `unit_understanding`
  - R11 selection traces now record actual rendered retrieved unit ids
- Post-R10/R11 passing diagnostic:
  - run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606`
  - job id: `bgjob_unit_memory_text_only_smoke_xidaduo_post_r11_20260606`
  - segment: `xidaduo_private_zh__segment_1`
  - mode: `text_only`
  - intentionally stopped after rendered-id evidence was collected; summary aggregate/report/usage files are absent
  - health packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606/analysis/unit_memory_retrieval_health/summary.json`
  - review packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606/analysis/unit_memory_retrieval_review/README.md`
  - health status `ok`: `47` Unit Memory entries, `293` retrieval docs, `54` retrieval rows, `47` selection rows, `selected_unit_count=18`, `renderable_selected_unit_count=11`, `retrieved_line_total=6`, `rendered_retrieved_unique_unit_count=6`
  - observed rendered retrieved ids: `u000010`, `u000009`, `u000007`, `u000006`, `u000003`, `u000002`
  - interpretation: all rendered units had `unit_understanding` among matched surfaces, so the observed prompt-visible retrieved memory no longer comes from auxiliary-surface-only hits; relevance remains broad and should be calibrated at the recall specificity layer

Goal:

- verify that long-distance Unit Memory becomes prompt-visible and useful before any formal evaluation promotion

Work:

- run a no-judge smoke first
- then run a small diagnostic with artifacts sufficient for human review
- inspect selected retrieved Understanding lines and the Digest outputs that received them
- do not update the evidence catalog

Acceptance:

- `retrieved_line_total > 0` or an equivalent reviewed retrieved-line metric in a meaningful subset of mature units where prior memory exists
- selected retrieved Understanding lines are relevant to the current source unit
- Digest prompt manifests include top-level `ReadingMemory` with hot and retrieved portions distinguishable by trace
- no prior-memory overclaim or obvious memory pollution is introduced by the repair

## Validation Ladder

Use this ladder after each repair slice:

1. Static checks
   - schema/config defaults
   - prompt/context naming
   - JSON registry parse
   - `git diff --check`
2. Deterministic unit tests
   - FTS query builder
   - vector adapter degradation
   - RRF / aggregation
   - selection / renderability
   - ReadingMemory budget rendering
3. Artifact health packet
   - run-local trace/database inspection, no LLM judge
4. Minimal live smoke
   - one short segment, no judge, no evidence catalog update
5. Small diagnostic review
   - inspect Ingest recalls, retrieval candidates, selected Understanding, Digest ReadingMemory, and Digest outputs
6. Formal evaluation consideration
   - only after the mechanism path is visible and stable

## Required Health Metrics

Each post-repair retrieval health report should include:

- total units
- Unit Memory entries
- retrieval docs by surface
- vector rows by surface
- vector pending / indexed / failed counts
- query embedding cache count
- retrieval rows by query source
- degradation reasons
- gate reasons
- actual search rows
- lexical candidate count
- dense candidate count
- fused candidate count
- selected unit count
- renderable selected unit count
- selected-but-not-rendered count
- excluded prompt-visible hot source-span count
- hot ReadingMemory line count
- retrieved ReadingMemory line count
- budget suppressions
- latency by retrieval stage

## Reassessment Triggers

Reassess rather than continuing blindly if any of these remain true after the relevant phase:

- `hybrid` still records zero vector rows and zero query embeddings after Phase 2
- `text_only` still cannot retrieve known-answer lexical probes after Phase 3
- boundary-unresolved rows still block all retrieval after Phase 4
- selected non-empty Understanding entries still fail to render into Digest after Phase 5
- retrieved lines enter Digest but are mostly irrelevant or polluting after Phase 7

These triggers are not terminal stop conditions by themselves. They should lead to a focused diagnosis, a smaller test, or a defer label while other independent phases continue. They must not lead to reviving retired Detour/backread or content-typed concept/thread memory.

## Implementation Notes

- Do not run full judged eval until at least one no-judge smoke proves prompt-visible retrieved memory.
- Do not treat `ReadingMemory` presence as proof of retrieval; hot memory and retrieved memory must be reported separately.
- Do not make Ingest choose final memory entries. Ingest only expresses recalls and may call the retrieval tool.
- Do not expose retrieved memory content back to Ingest through tool results.
- Do not place prior Response, Annotation, or raw prior source into Digest `ReadingMemory` in this repair track.
- If a repair changes the stable mechanism contract, promote the fact into `docs/backend-reading-mechanisms/attentional_v2.md`, `docs/current-state.md`, and `docs/tasks/registry.*` in the same slice.
