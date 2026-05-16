# Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0

## PR title / branch

Slice 4A: Supplemental Retrieval Intent and Context Assembly Contract

Branch: `main`

## Slice

Slice 4A / Retrieval & Utilization Instrumentation.

This PR is a small additive metadata slice for supplemental retrieval intent and prompt-facing context assembly contract visibility.

## Summary of actual changes

- Added compact retrieval metadata to `look_back` and `active_recall` supplemental contexts:
  - `retrieval_intent`
  - `result_boundary`
  - `result_groups`
  - `retrieval_events`
- Preserved current retrieval content bounds:
  - `look_back` remains bounded to source excerpts, source refs, and flattened refs.
  - `active_recall` still resolves concepts, threads, reactions, and flattened refs internally.
  - full active-recall concepts, threads, and reactions are not forwarded into the Read prompt packet in Slice 4A.
- Added compact prompt-facing `selective_carry.retrieval_context` metadata in `build_read_prompt_packet(...)`.
- Added compact visible-trace markers to active-recall reaction items and reaction refs:
  - `result_role="visible_trace"`
  - `semantic_memory=false`
- Added focused tests for retrieval intent, merge preservation, prompt-packet contract metadata, and no full-object forwarding.

## Files changed

- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_read_context.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design contracts addressed

- `look_back` is explicitly marked as `source_calibration`.
- `active_recall` is explicitly marked as `memory_recovery`.
- `look_back` remains source excerpt / source ref oriented.
- `active_recall` remains bounded to settled memory refs and visible trace refs.
- `reaction_records` remain visible trace, not semantic memory.
- `knowledge_activations` are not projected or treated as source truth.
- retrieval metadata is contract visibility only; it is not proof of retrieval quality, successful utilization, or product correctness.
- full retrieval utilization trace remains deferred.

## Deviations from accepted brief

None.

## Tests added or updated

- Added `reading-companion-backend/tests/test_attentional_v2_read_context.py`.
- Updated `reading-companion-backend/tests/test_attentional_v2_state_projection.py`.

## Commands run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_read_context.py tests/test_attentional_v2_state_projection.py -q
```

## Test results

```text
8 passed, 6 warnings
```

Warnings were existing dependency deprecation warnings from import-time packages.

## Contract / audit evidence produced

- `look_back` resolved contexts now emit:
  - `retrieval_intent="source_calibration"`
  - `result_boundary="source_refs_and_excerpts"`
  - `result_groups=["source_refs", "excerpts", "refs"]`
- `active_recall` resolved contexts now emit:
  - `retrieval_intent="memory_recovery"`
  - `result_boundary="settled_memory_refs_and_visible_trace_refs"`
  - `result_groups=["concepts", "threads", "reactions", "refs"]`
- merged supplemental contexts now preserve compact per-request `retrieval_events`.
- `build_read_prompt_packet(...)` now adds `selective_carry.retrieval_context` while preserving existing `earlier_excerpts`, `source_ref_details`, and `supporting_refs`.
- `selective_carry.retrieval_context.active_recall_full_objects_forwarded` is explicitly `false`.

## Prompt / observability notes

- Prompt-facing packet metadata changed additively.
- Prompt text did not change.
- Prompt version did not change.
- `observability.py` was not changed.
- `read_audit` retrieval utilization trace remains deferred.

## Backward compatibility notes

- Existing supplemental context fields remain present.
- The new metadata is mechanism-private and additive.
- No public API, frontend contract, durable memory state, prompt text, prompt version, runner behavior, `state_ops.py`, navigation / detour policy, slow-cycle, eval runner, vector DB, graph DB, Memory OS, or retriever-agent behavior changed.

## Risk / rollback notes

Risk:
- Retrieval metadata could be misread as retrieval quality proof if taken out of context.
- Since full active-recall objects are still not forwarded, this slice clarifies the contract before increasing prompt payload.

Rollback:
- Revert this PR. Additive supplemental-context and prompt-packet metadata require no migration.

## Known gaps

- Full retrieval utilization trace is still deferred.
- `read_audit` does not yet capture retrieval-intent or utilization evidence.
- active-recall full object projection remains deferred.
- stale `test_attentional_v2_phase_b.py` remains outside this Slice 4A contract and was not run.

## Next recommended step

Human reviewer should review and accept this Slice 4A Post-implementation Report or request a patch.

Do not start the next implementation slice until this report is accepted and the next Pre-implementation Brief is created and accepted.

## Required checks

- Did this PR change behavior, schema, prompt, audit, evaluation, or tests?
  - It changed mechanism-private supplemental-context metadata, prompt-facing packet metadata, and tests. It did not change prompt text/version, public API, eval runners, or durable memory schema.
- Did this PR introduce new infrastructure?
  - No.
- Did this PR preserve SourceRef-first behavior?
  - Yes.
- Did this PR avoid audit dump into runtime prompt?
  - Yes.
- Did this PR avoid `reaction_records` as semantic memory?
  - Yes.
- Did this PR avoid `knowledge_activations` as source truth?
  - Yes.
- Is this PR safe to review as a small slice?
  - Yes.
