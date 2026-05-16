# Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0

## PR title / branch

Slice 5A: Detour Lifecycle and Navigation Trace Audit Hardening

Branch: `main`

## Slice

Slice 5A, first small reversible sub-slice of Slice 5 / Planning Trace, Detour, Recall, and Look-back Hardening.

## Summary of actual changes

Slice 5A adds compact mechanism-private detour lifecycle and navigation trace audit metadata without changing planner behavior, Navigate act space, prompt text/version, retrieval behavior, or durable detour status semantics.

Implemented changes:

- Added optional `DetourTraceEntry` fields for lifecycle reason and last-navigation metadata.
- Enriched `_apply_detour_need(...)` so `open`, `resolved`, and `abandoned` detours record compact audit reasons while preserving the existing durable statuses.
- Kept `deferred` as a navigation outcome / audit reason only; no durable `deferred` status was introduced.
- Added compact detour trace and navigation trace helpers in `runner.py`.
- Passed compact navigation and detour evidence into `record_read(...)` for read steps where evidence is available.
- Added optional `navigation_trace` and `detour_trace_evidence` blocks to `read_audit.jsonl`, written only when non-empty.
- Preserved existing read-audit memory uptake and supplemental retrieval fields.

## Files changed

- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design contracts addressed

- Detour remains a bounded planning path deviation.
- Navigate act space remains `choose_unit`, `request_skill`, and `defer_detour`.
- Durable detour statuses remain `open`, `resolved`, and `abandoned`.
- Deferred detours are represented as navigation outcomes / audit reasons, not durable lifecycle states.
- Source-grounded mainline continuity is preserved.
- Source-skill evidence remains compact; no full skill payload dump is persisted.
- Audit evidence is not routed into prompts.
- No planner agent, memory manager, retriever agent, vector DB, graph DB, Memory OS, route steering UI, or user route choice was introduced.

## Deviations from accepted brief

None.

## Tests added or updated

- `test_attentional_v2_observability.py`
  - verifies `record_read(...)` omits navigation/detour audit blocks when absent;
  - verifies compact `navigation_trace` and `detour_trace_evidence` are written only when supplied;
  - verifies old memory uptake read-audit fields remain present.
- `test_attentional_v2_scaffold.py`
  - verifies detour open records `open_reason`;
  - verifies deferred/unlanded detour abandon records defer/abandon and last-navigation evidence without durable `deferred`;
  - verifies resolved detours record resolve and restore-mainline reasons.
- `test_attentional_v2_resume.py`
  - verifies additive detour trace metadata survives persisted reading-position snapshots.
- `test_attentional_v2_nodes.py`
  - verifies Navigate act space remains bounded to `choose_unit`, `request_skill`, and `defer_detour`.

## Commands run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_scaffold.py tests/test_attentional_v2_resume.py tests/test_attentional_v2_nodes.py -q
```

Result:

```text
51 passed, 6 warnings
```

## Contract / audit evidence produced

- `read_audit.jsonl` now supports compact optional `navigation_trace` when a read step has navigation evidence.
- `read_audit.jsonl` now supports compact optional `detour_trace_evidence` when a read step has detour evidence.
- No empty navigation/detour audit blocks are written.
- Deferred selections that do not run Read are represented in `local_continuity.detour_trace`, not by invented read-audit rows.

## Backward compatibility notes

- No public API fields changed.
- No prompt text or prompt version changed.
- No schema version changed.
- No `state_ops.py`, `slow_cycle.py`, `read_context.py`, `state_projection.py`, source skill behavior, frontend, public API, or eval runner changed.
- Existing detour behavior remains intact; the change is additive trace/audit metadata.

## Risk / rollback notes

Risk remains that mechanism-private trace metadata could be misread as a new user-visible route or state machine. This report records that the fields are audit metadata only.

Rollback is a normal revert of the Slice 5A PR. Additive trace/read-audit fields require no migration.

## Known gaps

- No active-recall / look-back retrieval loop was added.
- No full retrieval utilization trace was added.
- No full AI Evaluation was run.
- Detour trace evidence is compact and does not claim planning quality or product correctness.

## Next recommended step

Human reviewer should review and accept or patch this Slice 5A Post-implementation Report before any Slice 5B or next implementation slice begins.

## Required checks

- Did this PR change behavior, schema, prompt, audit, evaluation, or tests? It changed mechanism-private trace/read-audit metadata and targeted tests only.
- Did this PR introduce new infrastructure? No.
- Did this PR preserve SourceRef-first behavior? Yes.
- Did this PR avoid audit dump into runtime prompt? Yes.
- Did this PR avoid reaction_records as semantic memory? Yes; unchanged.
- Did this PR avoid knowledge_activations as source truth? Yes; unchanged.
- Is this PR safe to review as a small slice? Yes.
