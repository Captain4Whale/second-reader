# Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0

## Patch title / branch

Slice 4A Patch: Precise result_groups and forwarding metadata

Branch: `main`

## Slice

Slice 4A patch / Retrieval & Utilization Instrumentation.

This patch refines the accepted Slice 4A metadata contract. It is not Slice 4B and does not start the next implementation slice.

## Summary of actual changes

- Tightened supplemental retrieval metadata so `result_groups` now represents actual non-empty result groups after resolution, not all possible groups.
- For `look_back`, `result_groups` is derived from actual non-empty `source_refs`, `excerpts`, and `refs`.
- For `active_recall`, `result_groups` is derived from actual non-empty `concepts`, `threads`, `reactions`, and `refs`.
- Kept prompt-facing forwarding metadata additive and mechanism-private. `not_forwarded_result_groups` now naturally excludes absent groups because it is calculated from precise `result_groups`.
- Preserved reaction boundary markers:
  - `result_role="visible_trace"`
  - `semantic_memory=false`
- Preserved `knowledge_activations` exclusion.

## Files changed

- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/tests/test_attentional_v2_read_context.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design contracts addressed

- Retrieval metadata is contract visibility only, not proof of retrieval quality, successful utilization, or product correctness.
- `result_groups` means actual non-empty output groups after resolution.
- `not_forwarded_result_groups` means actual result groups that existed but were not forwarded into the Read prompt packet.
- Full active-recall concepts, threads, and reactions are still not forwarded into the Read prompt packet.
- `reaction_records` remain visible trace, not semantic memory.
- `knowledge_activations` remain excluded and are not treated as source truth.

## Deviations from accepted patch scope

None.

## Tests added or updated

- Updated `reading-companion-backend/tests/test_attentional_v2_read_context.py`.
- Updated `reading-companion-backend/tests/test_attentional_v2_state_projection.py`.

## Commands run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_read_context.py tests/test_attentional_v2_state_projection.py -q
```

## Test results

```text
10 passed, 6 warnings
```

Warnings were dependency deprecation warnings from import-time packages.

## Boundary checks

- No prompt text or prompt version changed.
- `runner.py` was not changed.
- `state_ops.py` was not changed.
- `slow_cycle.py` was not changed.
- `observability.py` was not changed.
- durable memory state was not changed.
- public API, frontend, and eval runners were not changed.
- full retrieval utilization trace remains deferred.
- full AI Evaluation was not run.

## Known gaps

- `read_audit` retrieval utilization trace remains deferred.
- active-recall full object projection remains deferred.
- Slice 4B has not started.

## Next recommended step

Human reviewer should review and accept this Slice 4A patch report before any Slice 4B brief or implementation work begins.
