# Ingest / Digest / Unit Memory Conformance Smoke Post-run Report v0

Date: 2026-06-03

## Scope

This pass executed the Goal-mode conformance contract in `docs/implementation/new-reading-mechanism/ingest-digest-unit-memory-conformance-goal.md`.

The pass checked structural behavior only:

- `Ingest` produces a forward boundary and bounded prior-reading recall surface.
- runtime owns Unit Memory retrieval/selection and does not expose retrieved content back to `Ingest`.
- `Digest` receives top-level `ReadingMemory`.
- `Digest` emits model-facing `understanding / response / annotations`, which runtime maps into settlement fields.
- settlement writes Recent Reading Memory, reaction records, Unit Memory entries/docs, and audit traces.

This pass did not judge subjective quality, did not run a formal eval, and did not update the evidence catalog.

## Code Fixes Made

- `read_audit.jsonl` now includes a compact nested `digest_result` object while preserving existing flattened fields.
- no-judge Long Span summary/report output now labels judge-disabled sources as `judge_disabled` instead of `fresh_judge`.
- the reused attentional_v2 output label in the Long Span harness now says `Attentional V2 Ingest/Digest` instead of the old scaffold label.

## Real Smoke Evidence

### Full active diagnostic smoke

Run root:

`reading-companion-backend/eval/runs/attentional_v2/attentional_v2_conformance_smoke_nawaer_20260602`

Segment:

`nawaer_baodian_private_zh__segment_1`

Result:

- process exit: `0`
- strict LLM health: `ok`
- LLM trace rows: `119`
- fallback rows: `0`
- read audit rows: `39`
- Unit Memory entries: `39`
- retrieval docs by surface:
  - `unit_source`: `101`
  - `unit_understanding`: `39`
  - `unit_response`: `39`
  - `unit_annotation`: `46`
- vector policy:
  - `unit_understanding`: `pending`
  - source / response / annotation docs: `not_requested`
- retrieval trace rows: `78`
- query sources included `tool_retrieve_unit_memory`, `skip_empty_recalls`, and `runtime_source_text_fallback`.

Finding from this run:

- The live mechanism completed structurally, but the read audit did not yet include the nested `digest_result` key required by the conformance contract. This was fixed in this pass.

### Post-fix direct capped smoke

Run root:

`reading-companion-backend/eval/runs/attentional_v2/attentional_v2_conformance_direct_nawaer_cap4_20260602/direct_read/attentional_v2`

Source:

`state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/segment_sources/nawaer_baodian_private_zh__segment_1.txt`

Mechanism config:

- `audit_window_max_units = 4`
- `memory_retrieval_mode = hybrid`
- `persist_normalized_eval_bundle = true`

Result:

- process exit: `0`
- strict LLM health: `ok`
- LLM trace rows: `17`
- fallback rows: `0`
- read audit rows: `4`
- every read audit row has `ingest_trace`
- every read audit row has the new compact `digest_result`
- Unit Memory entries: `4`
- Recent Reading Memory entries: `4`
- reaction records: `6`
- retrieval trace rows: `8`
- query sources included `tool_retrieve_unit_memory`, `skip_empty_recalls`, and `tool_boundary_unresolved`
- Digest prompt manifest includes top-level `ReadingMemory`
- Digest prompt manifest does not include `ReadingState`
- Ingest prompt manifest includes `memory_recalls`
- Ingest prompt manifest does not include model-facing `memory_query`
- vector policy:
  - `unit_understanding`: `pending`
  - source / response / annotation docs: `not_requested`

### No-judge harness label smoke

Run root:

`reading-companion-backend/eval/runs/attentional_v2/attentional_v2_conformance_smoke_huochu_micro_20260602`

Result:

- no mechanism output was produced because the diagnostic manifest did not resolve to a selected Long Span window under the current harness path rules.
- summary/report artifacts were still useful for validating the no-judge label fix:
  - `memory_quality_source = judge_disabled`
  - `reaction_audit_source = judge_disabled`
  - report includes judge-disabled explanatory notes.

This run is not counted as mechanism conformance evidence.

## Automated Checks

- targeted backend tests:
  - `225 passed`
- compile:
  - `python -m compileall src/attentional_v2 src/reading_runtime`
- registry JSON parse:
  - `python -m json.tool docs/tasks/registry.json`
- diff whitespace:
  - `git diff --check`
- terminology sweep:
  - remaining current-surface matches are negative assertions, historical stable-doc references, or the internal retrieval-layer `unit_memory_query.v1` identifier.
  - `unit_memory_query.v1` is not the model-facing old `memory_query`; it is the lower-level retrieval query version used under multi-recall orchestration.

## Conclusion

The current implementation now structurally conforms to the intended live path:

`Ingest recalls -> runtime Unit Memory retrieval/selection -> Digest ReadingMemory -> Digest output mapping -> settlement -> Unit Memory writeback`.

This pass confirms the project can perform the required actions and produce the required structural outputs. It does not claim that recall quality, ReadingMemory usefulness, Understanding quality, Response quality, or Annotation quality are product-ready.

## Remaining Non-blocking Work

- review 5-10 real `memory_recalls` and selected ReadingMemory lines for usefulness and pollution risk.
- add a proper `text_only` vs `hybrid` comparison path in the eval harness before using mode comparison as evidence.
- decide whether the internal retrieval-layer `unit_memory_query.v1` name should be renamed for clarity, even though it is not a model-facing compatibility leak.
- run a small judged diagnostic only after the structural smoke findings above are accepted.
