# Unit Memory Retrieval Repair And Validation Plan

Purpose: define the repair and validation track for the current Unit Memory retrieval failure found in the five-window diagnostic run.
Use when: planning, implementing, or validating fixes for `Ingest recalls -> Unit Memory retrieval/selection -> Digest ReadingMemory`.
Not for: redesigning Unit Memory storage from first principles, evaluating subjective Digest quality, or promoting evidence-catalog claims.
Update when: a retrieval repair slice lands, a validation gate passes/fails, or a new retrieval failure category is discovered.

## Status

- Date: `2026-06-06`
- Status: repair-validation plan, not yet implemented.
- Source diagnostic run: `attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5`
- Source audit directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5/analysis/core_mechanism_behavior_audit/`
- Design baseline:
  - `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
  - `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
- Current boundary:
  - do not revive Detour, source-backread, source-skill, concept registry, or thread trace
  - do not inject raw prior source text into Digest as a retrieval workaround
  - do not update the evidence catalog from these repair checks

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

Status: `not_started`

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

Status: `not_started`

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

Status: `not_started`

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

Status: `not_started`

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

Status: `not_started`

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

Status: `not_started`

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

Status: `not_started`

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
