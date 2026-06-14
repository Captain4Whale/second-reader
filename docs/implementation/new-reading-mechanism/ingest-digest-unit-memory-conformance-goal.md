# Ingest / Digest / Unit Memory Conformance Goal

Purpose: define the executable goal contract for end-to-end structural conformance testing of the current `attentional_v2` Ingest, Unit Memory, Digest, and settlement path.
Use when: creating or running a Codex Goal that should verify the current mechanism against the locked design baseline, repair implementation or test mismatches, and produce a conformance report.
Not for: changing mechanism design, judging subjective reading quality, promoting eval evidence, or replacing stable mechanism docs.
Update when: the conformance execution policy changes, the locked design baseline changes by explicit user-approved design work, or a new required observable is added to the current live mechanism.

## Status

- Date: `2026-06-02`
- Status: ready goal contract.
- Evaluation status: no formal eval run, no judge run, no evidence-catalog update.
- Scope status: this document is an execution contract, not a new mechanism design document.

## Goal Objective

Use this objective when starting the Codex Goal:

```text
Verify that the current attentional_v2 Ingest / Unit Memory / Digest mechanism conforms end to end to the locked design documents. The test must check that the Second Reader can select a forward source unit, express bounded prior-reading recalls, trigger runtime-owned Unit Memory retrieval, carry selected Understanding memory into Digest ReadingMemory, digest the selected source unit into understanding / response / annotations, settle the result, and write back memory artifacts. Fix implementation, prompt-rendering, runtime, test, or stable-doc mismatches found during this conformance pass. Do not modify locked mechanism design documents, do not judge subjective reading quality, do not run formal eval, do not update the evidence catalog, and do not change mechanism direction.
```

## Locked Baseline

The following documents are normative for this conformance pass:

- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/implementation/new-reading-mechanism/ingest-context-and-navigate-mapping.md`
- `docs/implementation/new-reading-mechanism/digest-understanding-response-annotation-design.md`
- `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
- `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
- `docs/history/decision-log.md` entries `DEC-103` through `DEC-110`

During this conformance goal, these mechanism design documents must be treated as the standard, not as files to edit into agreement with the implementation.

## Baseline Protection Rules

- Do not modify locked mechanism design documents unless the user explicitly approves a design-doc correction.
- If code, prompt renderers, runtime artifacts, tests, or stable docs conflict with the locked baseline, fix the conflicting surface.
- If a locked design document appears ambiguous, incomplete, or internally inconsistent, record a `design_ambiguity_blocker` in the final report, skip only the affected judgment, and continue all other conformance checks that remain independently testable.
- Do not introduce a new mechanism direction, memory ontology, retrieval policy, prompt field, or compatibility layer to make tests pass.
- Do not revive retired Detour / source-backread / source-skill, `memory_query`, concept/thread structured memory, or old `read_unit` surfaces.

## Non-Goals

This goal does not evaluate:

- whether an `understanding` is deep, elegant, or product-quality
- whether a `response` is emotionally satisfying
- whether an `annotation` is insightful or beautifully phrased
- whether retrieved memory improves final reading quality
- whether the current product is ready for evidence-catalog promotion

This goal only evaluates structural and artifact-level conformance:

- required fields exist
- prohibited fields are absent or ignored
- required tools and runtime calls happen in the intended ownership boundary
- required runtime artifacts are written
- prompt-facing context has the intended shape
- settlement writes the intended internal memory and note artifacts

## Execution Order

Run the goal in this order. If one layer cannot be fully judged, record the issue and continue every later layer that can still be tested without changing the locked design baseline:

1. Static contract sweep.
2. Prompt and LLM-call unit tests.
3. Unit Memory ledger / index / retrieval tests.
4. Runner, settlement, observability, and resume tests.
5. Minimal no-judge end-to-end smoke with a real active segment.
6. Artifact inspection for the smoke run.
7. Repair only implementation, prompt, runtime, test, or stable-doc mismatches.
8. Final conformance report and commit.

If a real smoke is expected to run longer than roughly `10-15` minutes, register it through the backend background-job registry. A no-judge smoke is diagnostic only and must not update the evidence catalog.

## Continuation And Stop Semantics

The goal should stop because the conformance pass has reached its completion criteria, not because the first unresolved issue appears.

Default behavior:

- Keep testing independently testable layers even when one requirement has a recorded issue.
- Fix issues that are within the allowed repair surface.
- Record issues that are outside the allowed repair surface, then continue other checks.
- Treat external degradation as testable behavior when the design expects graceful degradation.
- Produce the final report only after static checks, targeted tests, any approved smoke, artifact inspection, and allowed repairs have all been attempted.

The goal should not stop early merely because:

- one test is outdated but can be updated
- one optional dependency is missing but degradation behavior can be inspected
- one design point is ambiguous while other requirements remain independently testable
- one artifact is missing and the writer can be fixed
- a formal subjective quality question remains unanswered

The goal should stop as complete when:

- the Second Reader has been structurally verified to perform the designed end-to-end loop, or every missing part has been classified and reported
- all allowed repairs discovered during the pass have been applied and rechecked
- all non-repaired issues are listed as follow-up findings with categories and affected requirements
- no remaining planned conformance check can add new structural evidence without changing the locked baseline or running out-of-scope work

In short: continue through findings; stop after the target has been fully exercised and reported.

## Failure Categories

Classify each discovered issue with exactly one primary category:

- `implementation_bug`: live code does not implement the locked baseline.
- `prompt_contract_mismatch`: live prompt text, XML shape, or prompt manifest does not match the locked baseline.
- `runtime_artifact_missing`: required trace, ledger, manifest, audit, or runtime file is absent or malformed.
- `test_outdated`: a test still expects a retired or superseded surface.
- `stable_doc_inconsistent`: stable docs describe a non-current mechanism fact.
- `design_ambiguity_blocker`: the locked baseline is ambiguous or conflicting enough that implementation cannot be judged safely.
- `external_dependency_degraded`: sqlite-vec, Ollama, provider tools, or another external dependency degrades, while the mechanism handles degradation as designed.

## Repair Rules

Allowed fixes:

- implementation code
- live prompt renderers and prompt manifest generation
- normalizers and schema adapters
- runtime artifact writers
- backend test expectations and new conformance tests
- stable current-fact docs such as `docs/current-state.md`, `docs/tasks/registry.*`, and `docs/backend-reading-mechanisms/attentional_v2.md`
- eval harness structure only when needed to inspect current artifacts without judging subjective quality

Disallowed fixes without explicit user approval:

- locked mechanism design documents
- subjective prompt optimization for better prose or deeper insight
- formal evaluation, judge prompts, evidence-catalog updates, or product-quality claims
- frontend UI changes
- new memory surfaces, new retrieval stores, new LLM calls, or new public API surfaces
- old-run compatibility for retired Detour, concept/thread, `read_unit`, or `memory_query` artifacts

## End-To-End Requirements

### REQ-GOV-001 Locked Baseline

Requirement:
The conformance goal must use the locked baseline documents as the source of truth and must not edit them during execution.

Observable evidence:
- git diff
- final conformance report

Pass condition:
- no locked mechanism design document is modified
- any suspected design problem is recorded as a blocker or question

Allowed fix:
- none for locked design docs
- stable docs may be updated only when they conflict with the locked baseline

Must not:
- change the design baseline to match observed implementation behavior

### REQ-INGEST-001 Prompt Context

Requirement:
The live Ingest LLM call must use the current XML context shape for boundary selection and prior-reading recall.

Observable evidence:
- `prompt_manifests/ingest.json`
- Ingest prompt renderer tests
- LLM trace prompt packet when available

Pass condition:
- prompt contains `ReaderRole`, `Instruction`, `BookInfo`, `CurrentView`, `RetrievalSurface`, and `OutputContract`
- `CurrentView` contains `Position` and `Content`
- `RetrievalSurface` is empty at the prompt level
- prompt uses reader-facing prior-reading recall language rather than query-generator language

Allowed fix:
- Ingest prompt renderer
- prompt manifest tests

Must not:
- inject retrieved memory text into Ingest context
- restore old navigation context, source-skill, backread, or Detour prompt language

### REQ-INGEST-002 Output Contract

Requirement:
The final Ingest JSON must contain boundary fields, while bounded Unit Memory recall intent must be carried only by `retrieve_unit_memory` action-tool args.

Observable evidence:
- Ingest output normalizer tests
- LLM trace parsed output
- read audit `ingest_trace`

Pass condition:
- final output includes the live unit-boundary fields, `preview_partition[]`, and optional `reason`
- final output does not require or author `memory_recalls[]`
- when the action tool is called, its `memory_recalls[]` array has one to three items
- each tool recall has `recall_id`, `recall_text`, and `basis="selected_source_unit"`
- old `memory_query` output is absent or ignored

Allowed fix:
- Ingest normalizer
- prompt output contract
- tests

Must not:
- add a separate query-generation LLM call
- let Ingest decide selected memory ids or Digest context contents

### REQ-INGEST-003 Tool Loop

Requirement:
If Ingest needs non-empty recalls, it must submit them through the `retrieve_unit_memory` tool loop or trigger a traceable contract-violation repair path.

Observable evidence:
- LLM gateway tool-loop tests
- Ingest LLM call tests
- retrieval trace
- read audit compact trace

Pass condition:
- empty recalls can finalize without tool use
- non-empty recalls call `retrieve_unit_memory`
- non-empty recalls without tool use are treated as `tool_call_contract_violation` and retried or failed traceably
- tool result exposes only status and counts, not retrieved memory content or selected ids

Allowed fix:
- tool-loop helper
- Ingest call path
- tests and trace shaping

Must not:
- expose Unit Memory entries, retrieved Understanding text, SQL, scores, or selected memory ids to Ingest

### REQ-BOUNDARY-001 Runtime Boundary Governance

Requirement:
Reading Runner, not Ingest, owns boundary preparation, anchor resolution, retry, fallback, source unit acceptance, and cursor advancement.

Observable evidence:
- runner tests
- unit span ledger
- read audit
- source cursor runtime state

Pass condition:
- runner prepares the source preview and calls Ingest
- runner resolves `end_anchor_text` into an accepted source unit
- retry and fallback paths still produce a forward-only accepted source unit
- no Detour, source-backread, or path-redirection behavior is created

Allowed fix:
- runner boundary governance
- tests

Must not:
- let Ingest return routing decisions beyond the accepted boundary contract

### REQ-UNITMEM-001 Ledger Writeback

Requirement:
After each settled source unit, runtime must write one Unit Memory entry for the accepted unit and Digest result.

Observable evidence:
- `_mechanisms/attentional_v2/runtime/unit_memory.sqlite`
- Unit Memory tests
- settlement audit

Pass condition:
- `unit_memory_entries` has one entry per settled accepted source unit
- entry includes accepted source unit data, one holistic Digest `understanding`, `response`, `annotations`, mode, and index status
- empty understanding content does not create an empty recent-memory append

Allowed fix:
- Unit Memory ledger writer
- settlement mapping
- tests

Must not:
- recreate concept/thread structured long-memory stores

### REQ-UNITMEM-002 Retrieval Documents And Index Surfaces

Requirement:
Unit Memory entries must derive retrieval documents with the designed lexical and dense-vector surfaces.

Observable evidence:
- `retrieval_docs` table
- FTS5 tables
- vector status rows
- Unit Memory index tests

Pass condition:
- retrieval docs are derived for `unit_source`, `unit_understanding`, `unit_response`, and `unit_annotation` when content exists
- all valid retrieval docs participate in SQLite FTS5 text retrieval
- only `unit_understanding` participates in dense-vector indexing
- source, response, and annotation docs are not dense-vector surfaces

Allowed fix:
- retrieval document derivation
- FTS/vector adapter code
- tests

Must not:
- embed raw source, response, or annotation docs unless the locked design changes

### REQ-UNITMEM-003 Retrieval Mode And Degradation

Requirement:
Unit Memory retrieval must support `text_only` and default `hybrid` mode, with clean degradation when vector dependencies are unavailable.

Observable evidence:
- `memory_retrieval_config.json`
- retrieval trace
- Unit Memory index tests

Pass condition:
- default mode is `hybrid`
- `text_only` skips vector work
- missing sqlite-vec, Ollama, embedding timeout, or vector absence degrades to lexical retrieval without breaking the read loop
- degradation reason is recorded

Allowed fix:
- config normalizer
- vector adapter
- retrieval trace
- tests

Must not:
- fail the read cycle solely because the optional vector path is unavailable

### REQ-UNITMEM-004 Runtime Retrieval Selection

Requirement:
Runtime must own multi-recall retrieval, candidate aggregation, dedupe, recent-neighbor exclusion, and Digest memory selection.

Observable evidence:
- `unit_memory_retrieval_trace.jsonl`
- Unit Memory retrieval tests
- Digest prompt manifest

Pass condition:
- each recall can produce its own retrieval run
- results are fused/aggregated at runtime
- repeated units are deduped
- current unit and direct recent-neighbor units are excluded from long-distance selection
- selected memory lines are Understanding-only
- selected and suppressed units are traceable

Allowed fix:
- retrieval orchestrator
- selection and dedupe logic
- trace writer
- tests

Must not:
- let Ingest choose final memory entries for Digest
- pass raw prior source, prior response, or prior annotation into Digest `ReadingMemory`

### REQ-DIGEST-001 Prompt Context

Requirement:
The live Digest prompt must use top-level `ReadingMemory` and the implemented XML prompt shape.

Observable evidence:
- `prompt_manifests/digest.json`
- Digest prompt renderer tests
- LLM trace prompt packet when available

Pass condition:
- prompt contains `ReaderRole`, `Instruction`, `BookInfo`, `ReadingMemory`, `CurrentFocus`, and `OutputContract`
- prompt does not contain prompt-facing `ReadingState`, `RecentMemory`, `RetrievedUnitMemory`, raw prior source text, prior Response, or prior Annotation blocks
- `ReadingMemory` appears before `CurrentFocus`

Allowed fix:
- Digest prompt renderer
- tests

Must not:
- restore old `read_unit` prompt naming or legacy prompt assembly toggles

### REQ-DIGEST-002 ReadingMemory Content And Budget

Requirement:
Runtime must render one merged prompt-facing `ReadingMemory` text block from hot current-chapter Understanding and selected long-distance Unit Memory Understanding.

Observable evidence:
- Digest prompt manifest
- retrieval trace token accounting
- ReadingMemory builder tests

Pass condition:
- hot memory uses current-chapter prior Understanding
- long-distance memory uses runtime-selected Unit Memory Understanding
- both are merged into one text block
- lines use compact location labels such as `P42 U18: ...`
- lines are sorted nearest-prior first unless the locked design changes
- budgets are enforced without splitting Understanding text:
  - hot memory up to `5,000` estimated tokens
  - selected long-distance memory up to `10,000` estimated tokens
  - total prompt-facing `ReadingMemory` up to `15,000` estimated tokens
- token estimates use `tiktoken_o200k_base_v1` with the configured safety multiplier

Allowed fix:
- ReadingMemory builder
- token estimator
- tests and trace token accounting

Must not:
- insert raw prior source excerpts as memory context
- expose scores, internal ids, SQL, or retrieval mechanics to Digest

### REQ-DIGEST-003 Output Contract

Requirement:
Digest must output three peer reading products: one holistic `understanding` object, `response`, and `annotations[]`.

Observable evidence:
- Digest prompt manifest
- Digest output-normalizer tests
- read audit `digest_result`

Pass condition:
- output contract uses `understanding`, `response`, and `annotations`
- `understanding` is a single object, not an array
- `understanding.content` can contain multiple meanings but must be one coherent whole
- `annotations` are anchored to current source text when present
- old model-facing fields `reading_impression`, `surfaced_reactions`, and `recent_reading_memory` are absent or ignored at the LLM contract boundary

Allowed fix:
- Digest prompt renderer
- Digest normalizer
- tests

Must not:
- judge the literary or interpretive quality of these fields in this conformance pass

### REQ-SETTLE-001 Post-Digest Settlement

Requirement:
After Digest, runtime must settle the read cycle by writing notes, recent memory, Unit Memory, audit rows, and cursor progress.

Observable evidence:
- `read_audit.jsonl`
- `unit_span_ledger.jsonl`
- `recent_reading_memory` runtime state
- `unit_memory.sqlite`
- reaction records
- settlement tests

Pass condition:
- Digest `understanding.content` maps to zero or one internal append op targeting `recent_reading_memory`
- Digest `response` maps to internal `reading_impression`
- Digest `annotations[]` map to internal surfaced reactions
- Unit Memory writeback happens after settlement
- cursor advances to the accepted source unit end
- read audit records `ingest_trace`, `digest_result`, memory ops, and settlement inputs

Allowed fix:
- settlement mapping
- audit writer
- runtime state ops
- tests

Must not:
- create retired Detour traces, concept/thread stores, or old source-backread artifacts for new runs

### REQ-OBS-001 Artifact Completeness

Requirement:
A successful end-to-end smoke must leave enough artifacts to inspect every major mechanism step.

Observable evidence:
- runtime directory
- prompt manifests
- LLM traces
- `read_audit.jsonl`
- `unit_memory_retrieval_trace.jsonl`
- `unit_memory.sqlite`
- summary files for no-judge smoke, if run

Pass condition:
- Ingest prompt manifest exists
- Digest prompt manifest exists
- retrieval config exists
- retrieval trace has rows for recall, skip-empty, fallback, or degradation cases
- Unit Memory DB has entries and retrieval docs after at least one settled unit
- read audit includes both `ingest_trace` and `digest_result`

Allowed fix:
- artifact writers
- test harness checks
- trace schemas

Must not:
- use missing artifacts as evidence of success

### REQ-DOC-001 Stable Fact Consistency

Requirement:
Stable current-fact docs must describe the current live mechanism consistently.

Observable evidence:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `docs/backend-state-aggregation.md`

Pass condition:
- stable docs say current live loop is `Ingest -> Unit Memory retrieval/selection -> Digest -> settlement`
- stable docs do not describe Detour, source-backread, source-skill, concept/thread structured memory, `memory_query`, `read_unit`, `ReadingState`, or trace-only retrieved memory as current live surfaces
- stable docs distinguish structural conformance testing from subjective reader-quality evaluation

Allowed fix:
- stable docs listed above

Must not:
- edit locked design docs without user approval

## Static Sweep Targets

The conformance pass should include targeted sweeps for stale current-surface language. Hits are not automatically failures if they are clearly historical, archived, or explicitly retired, but active code/prompts/tests/stable docs should not expose them as live interfaces.

Suggested terms:

```text
memory_query
read_unit
ReadingState
RecentMemory
RetrievedUnitMemory
detour
backread
request_skill
source-skill
look_back
active_recall
concept_registry
thread_trace
concept_digest
thread_digest
```

## Minimal End-To-End Smoke Standard

A real smoke is allowed only as a structural diagnostic, not as formal evaluation.

Minimum pass conditions:

- job exits `0`
- strict LLM health is `ok`
- `memory_retrieval_config.mode` is present and defaults to `hybrid` unless explicitly overridden
- Unit Memory DB contains entries and retrieval docs
- only `unit_understanding` has dense-vector pending/indexed status
- retrieval trace exists and records recalls, skip-empty recalls, fallback query source, or degradation reasons
- Digest prompt manifest contains top-level `ReadingMemory`
- read audit contains `ingest_trace` and `digest_result`
- settlement writes recent memory and Unit Memory after Digest

Do not interpret the smoke as evidence that reading quality is good.

## Final Report Template

The Goal executor must finish with a concise report:

```text
Conformance Goal Result

Status:
- passed | completed_with_findings | blocked_by_unexecutable_goal

Checked:
- static sweeps
- prompt contracts
- tool loop
- Unit Memory ledger/index/retrieval
- Digest ReadingMemory
- settlement/writeback
- end-to-end smoke, if run

Fixed:
- [category] file/path: short description

Blocked:
- [only if the whole goal cannot be exercised] reason and exact evidence

Not Run:
- subjective quality evaluation
- formal eval
- evidence catalog update

Findings Carried Forward:
- [category] affected requirement and recommended next owner

Residual Risk:
- short note
```

## Completion Criteria

The goal is complete only when all applicable requirements above are either:

- passed,
- fixed and then passed,
- intentionally not applicable with a documented reason, or
- carried forward as a categorized finding after all independently testable checks have continued.

The goal is not complete merely because a smoke run exits `0`. The artifacts must show the intended end-to-end mechanism actions.

The goal is also not incomplete merely because a non-critical finding remains. If the mechanism has been exercised end to end, allowed repairs are complete, and remaining findings are outside the allowed repair surface or require later design/product decisions, the correct status is `completed_with_findings`.
