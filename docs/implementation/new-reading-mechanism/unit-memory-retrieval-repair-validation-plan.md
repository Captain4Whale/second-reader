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
- The local hybrid path is still blocked by environment because Ollama is not installed or reachable on `127.0.0.1:11434`; therefore dense retrieval has not been validated.
- Text-only retrieval has deterministic coverage for Chinese recall-meta wording, English concept recall, multi-recall aggregation, and empty-Understanding suppression.
- Runtime boundary / horizon governance has deterministic coverage: a tool-stage `boundary_unresolved` trace no longer prevents runtime retrieval after the source unit has been accepted, and horizon gates record counts rather than only labels.
- A first post-repair no-judge `text_only` smoke on `value_of_others_private_en__segment_1` completed the reading loop but failed the registered wrapper's strict LLM-health gate before summary generation. Its run-local retrieval health packet still showed no prompt-visible retrieved memory and exposed a new root cause: the Runner was passing the whole active Recent Reading Memory store as retrieval exclusions, which excluded all prior units by the end of the run. That exclusion bug has been removed in code and still needs a fresh smoke.

Current unresolved target:

- No no-judge live smoke after the whole-Recent-Memory exclusion fix has yet proven prompt-visible long-distance retrieved Understanding lines in Digest `ReadingMemory`.
- The goal remains active until at least one repair smoke demonstrates `retrieved_line_count > 0` with renderable selected Unit Memory Understanding.

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

### Completion Definition

The goal is complete only when all of these are true:

1. A no-judge live smoke proves that at least one Digest prompt receives prompt-visible long-distance retrieved Understanding memory.
2. The smoke artifact health report shows:
   - `retrieved_line_count > 0`
   - `renderable_selected_unit_count > 0`
   - `selected_but_not_rendered_count = 0`, or every nonzero case has a specific suppression reason
   - at least one selected retrieved Unit Memory entry has non-empty Understanding
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
- Phase 7 exits only when a no-judge smoke shows prompt-visible retrieved Understanding lines and a review packet confirms they are relevant enough for continued reading.

### Phase Status Summary

| Phase | Current status | What is proven | What remains |
| --- | --- | --- | --- |
| Phase 0 | `passed_initial` | The health packet reproduces the five-window failure and separates hot memory, retrieved memory, selected candidates, renderability, vector availability, and degradation facts. | Keep the packet updated as later trace fields change. |
| Phase 1 | `passed_deterministic` | Selected-but-not-rendered candidates are no longer invisible; retrieval-layer suppressed candidates are counted by reason; empty/missing Understanding is suppressed before selection. | Run a fresh post-repair smoke to prove the trace behavior in real artifacts. |
| Phase 2 | `blocked_by_ollama_environment_after_sqlite_vec_fix` | sqlite-vec can be imported and loaded locally after the adapter fix. | Ollama/Qwen embedding service must be available before query embeddings, vector rows, dense candidates, and RRF fusion can be validated. |
| Phase 3 | `passed_deterministic_text_only` | Text-only FTS retrieves known Chinese and English prior Understanding; multi-recall aggregation preserves recall-match metadata; empty-Understanding candidates are suppressed. | Validate with a post-repair no-judge smoke; dense paraphrase remains Phase 2-dependent. |
| Phase 4 | `passed_deterministic` | Runtime retrieval can continue after boundary acceptance even if the earlier tool-stage trace was `boundary_unresolved`; horizon gates now record current unit, recent exclusion, max retrievable unit, prior count, and minimum prior count. | Validate the gate counts in fresh smoke artifacts. |
| Phase 5 | `passed_deterministic` | A selected non-empty Understanding from the real Unit Memory index renders into Digest `ReadingMemory`, and prior Response / Annotation / raw source stay out of prompt-facing memory. | Validate prompt-visible retrieved lines in a no-judge smoke. |
| Phase 6 | `not_started` | None. | Calibrate Ingest recall prompt only after retrieval/search/rendering is mechanically functional. |
| Phase 7 | `attempted_failed_pre_r9_fix` | A `text_only` smoke can complete the read loop, and the health packet can explain no-retrieval artifacts. | Re-run after the whole-Recent-Memory exclusion fix and produce a human-readable review packet with selected retrieved Understanding examples. |

### External Environment Handling

Hybrid depends on local sqlite-vec and Ollama. Goal mode should handle those as repairable environment dependencies, not as silent degradations.

Required behavior:

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

1. Re-run a small no-judge post-repair smoke in `text_only` mode after the whole-Recent-Memory exclusion fix.
2. Inspect the post-repair health packet for:
   - prompt-visible `retrieved_line_count > 0`
   - `renderable_selected_unit_count > 0`
   - retrieval-layer suppression reasons when candidates are not renderable
   - horizon counts for skipped retrieval rows
3. Produce a small human-readable review packet with current source unit, recalls, selected Understanding lines, and Digest `ReadingMemory` snippets.
4. Attempt Phase 2 only when environment can support it:
   - sqlite-vec load works
   - Ollama is reachable
   - configured Qwen embedding model is available
   - query embedding cache and vector rows become nonzero
5. Calibrate Ingest recall wording only after the post-repair smoke proves search / selection / rendering mechanics.

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

- add an invariant that separates `selected_unit_count`, `renderable_selected_unit_count`, and `retrieved_line_count`
- record why each selected candidate is rendered or suppressed
- treat `selected_unit_count > 0` with `retrieved_line_count = 0` as a diagnostic failure unless every selected unit has an explicit suppression reason

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
  - `retrieved_line_count`
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

Repair direction:

- Do not pass the whole active Recent Reading Memory store as `excluded_source_unit_span_ids` to Unit Memory retrieval.
- Let UnitMemoryIndex horizon gates exclude only direct recent neighbors for long-distance retrieval.
- Let Digest `ReadingMemory` rendering dedupe retrieved lines against hot memory, rather than preventing retrieval from seeing the whole prior ledger.
- Re-run a no-judge smoke after the fix; this R9 repair is not validated until fresh artifacts show whether candidates can now be selected and rendered.

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
10. If selected retrieved memory does not enter Digest, the trace must say why.

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
- add smoke assertions for `selected_unit_count > 0` and `retrieved_line_count = 0`
- make `ReadingMemory` prompt-manifest inspection report hot vs retrieved separately

Acceptance:

- no run can pass retrieval smoke merely because `ReadingMemory` exists
- every unrendered selected candidate has a machine-readable reason

### Phase 2. Hybrid Vector Path Repair

Status: `blocked_by_ollama_environment_after_sqlite_vec_fix`

Current evidence:

- `sqlite-vec` is declared in `pyproject.toml`.
- Current venv initially lacked `sqlite_vec`; installing `sqlite-vec>=0.1.6` fixed the import.
- The sqlite-vec adapter now enables SQLite extension loading before calling `sqlite_vec.load(...)`; vec0 table creation with `distance_metric=cosine` is locally verified.
- Current machine does not have the `ollama` command and `127.0.0.1:11434` is not serving embeddings, so full hybrid query embedding / dense retrieval remains environment-blocked.

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

Status: `not_started`

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

### Phase 7. End-To-End Diagnostic Validation

Status: `attempted_failed_pre_r9_fix`

Current evidence:

- Run id: `attentional_v2_unit_memory_text_only_smoke_value_20260606`
- Job id: `bgjob_unit_memory_text_only_smoke_value_20260606`
- Segment: `value_of_others_private_en__segment_1`
- Mode: `text_only`
- The underlying read loop completed and wrote runtime artifacts, including `run_state.json` with `stage=completed`.
- The registered wrapper exited `1` because strict LLM-health validation reported `llm_fallback_events_present`, so summary files were not generated.
- The run-local retrieval health packet remained `needs_repair`: `50` Unit Memory entries, `228` retrieval docs, `63` retrieval rows, `50` selection rows, but `selected_unit_count=0`, `renderable_selected_unit_count=0`, and `retrieved_line_total=0`.
- The smoke exposed R9: all active Recent Reading Memory source spans were passed into retrieval exclusions, preventing otherwise matching prior units from becoming candidates.
- The R9 code repair has landed, but no post-R9 smoke has run yet.

Goal:

- verify that long-distance Unit Memory becomes prompt-visible and useful before any formal evaluation promotion

Work:

- run a no-judge smoke first
- then run a small diagnostic with artifacts sufficient for human review
- inspect selected retrieved Understanding lines and the Digest outputs that received them
- do not update the evidence catalog

Acceptance:

- `retrieved_line_count > 0` in a meaningful subset of mature units where prior memory exists
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
- hot ReadingMemory line count
- retrieved ReadingMemory line count
- budget suppressions
- latency by retrieval stage

## Stop Conditions

Stop and reassess rather than continuing blindly if any of these remain true after the relevant phase:

- `hybrid` still records zero vector rows and zero query embeddings after Phase 2
- `text_only` still cannot retrieve known-answer lexical probes after Phase 3
- boundary-unresolved rows still block all retrieval after Phase 4
- selected non-empty Understanding entries still fail to render into Digest after Phase 5
- retrieved lines enter Digest but are mostly irrelevant or polluting after Phase 7

These stop conditions should lead to a focused diagnosis, not to reviving retired Detour/backread or content-typed concept/thread memory.

## Implementation Notes

- Do not run full judged eval until at least one no-judge smoke proves prompt-visible retrieved memory.
- Do not treat `ReadingMemory` presence as proof of retrieval; hot memory and retrieved memory must be reported separately.
- Do not make Ingest choose final memory entries. Ingest only expresses recalls and may call the retrieval tool.
- Do not expose retrieved memory content back to Ingest through tool results.
- Do not place prior Response, Annotation, or raw prior source into Digest `ReadingMemory` in this repair track.
- If a repair changes the stable mechanism contract, promote the fact into `docs/backend-reading-mechanisms/attentional_v2.md`, `docs/current-state.md`, and `docs/tasks/registry.*` in the same slice.
