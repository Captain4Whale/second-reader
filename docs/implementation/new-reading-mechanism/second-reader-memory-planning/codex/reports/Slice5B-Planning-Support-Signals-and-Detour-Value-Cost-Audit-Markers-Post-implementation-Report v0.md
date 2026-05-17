# Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0

## PR title / branch

Slice 5B: Planning Support Signals and Detour Value-Cost Audit Markers

Branch: `main`

## Slice

Slice 5B, a small reversible sub-slice of Slice 5 / Planning Trace, Detour, Recall, and Look-back Hardening.

## Summary of actual changes

Slice 5B adds compact mechanism-private planning support-signal and value-cost audit markers to existing detour / navigation audit evidence.

Implemented changes:

- Added optional `NavigateActTraceEntry` marker fields: `source_scent`, `detour_value`, `continuity_cost`, `active_recall_needed`, `look_back_needed`, `support_signal_reason`, and `budget_stop_reason`.
- Added helper-level marker derivation in `runner.py` using only deterministic existing navigation trace fields: decision, selection mode, source ids, source skill request/result summaries, budget state, explicit error, and explicit defer reason.
- Added markers to compact `navigation_trace` entries only after trace compaction.
- Added top-level marker fields to `detour_trace_evidence` when detour evidence exists.
- Preserved `local_continuity.detour_trace` as lifecycle trace state, not a planning score store.
- Preserved existing Slice 5A `navigation_trace` and `detour_trace_evidence` fields.

Markers are audit / explanation metadata only. They are not product scores, planning-quality proof, state-machine authority, route recommendations, route steering, or user-facing route UX.

## Files changed

- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design contracts addressed

- Planning support markers are compact, symbolic, and mechanism-private.
- No numeric scoring was introduced.
- `active_recall_needed` and `look_back_needed` remain audit markers only.
- No active-recall, look-back, supplemental-context, runner retry, or retrieval loop was introduced.
- `budget_stop_reason` is derived only from explicit deterministic budget / defer evidence.
- Navigate act space remains `choose_unit`, `request_skill`, and `defer_detour`.
- Durable detour statuses remain `open`, `resolved`, and `abandoned`.
- No durable `status="deferred"` was introduced.
- Audit evidence is not routed into prompts.
- No planner agent, memory manager agent, retriever agent, vector DB, graph DB, Memory OS, route steering UI, user route choice, visible route UX, or recommender behavior was introduced.

## Deviations from accepted brief

None.

## Tests added or updated

- `test_attentional_v2_observability.py`
  - verifies marker-bearing `navigation_trace` and `detour_trace_evidence` are persisted without losing old Slice 5A fields.
- `test_attentional_v2_scaffold.py`
  - verifies source-skill request and landed detour entries receive compact symbolic markers;
  - verifies budget exhaustion records `budget_stop_reason` from deterministic evidence;
  - verifies deferred detours use `not_assessed` / `false` rather than over-inference;
  - verifies `local_continuity.detour_trace` does not become a planning score store.
- Existing `test_attentional_v2_nodes.py` coverage continues to verify Navigate act space remains bounded.

## Commands run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_scaffold.py tests/test_attentional_v2_nodes.py -q
```

Result:

```text
42 passed, 6 warnings
```

## Contract / audit evidence produced

- `read_audit.jsonl` `navigation_trace` entries may now include compact marker fields when the entry has detour / support evidence.
- `read_audit.jsonl` `detour_trace_evidence` may now include compact marker fields when detour evidence exists.
- Marker values are symbolic / boolean only.
- Ambiguous evidence falls back to `not_assessed`, `false`, or omission.
- `observability.py` does not infer planning quality; it persists compact dictionaries it receives.

## Backward compatibility notes

- No public API fields changed.
- No prompt text or prompt version changed.
- No schema version changed.
- No durable memory state changed.
- No `prompts.py`, `state_ops.py`, `slow_cycle.py`, `state_projection.py`, `read_context.py`, source skill behavior, frontend, public API, or eval runner changed.
- Additive mechanism-private audit fields require no migration.

## Risk / rollback notes

The main risk is that fields named `detour_value` or `continuity_cost` could be misread as product scores. This report records that they are symbolic audit markers only and must not be treated as proof of planning quality.

Rollback is a normal revert of the Slice 5B PR. Additive typing and read-audit metadata require no migration.

## Known gaps

- No full retrieval utilization trace was added.
- No active-recall / look-back loop was added.
- No planner behavior was added.
- No full AI Evaluation was run.
- Markers do not claim actual model utilization, planning quality, product correctness, or route recommendation quality.

## Next recommended step

Human reviewer should review and accept or patch this Slice 5B Post-implementation Report before any next implementation slice begins.

## Required checks

- Did this PR change behavior, schema, prompt, audit, evaluation, or tests? It changed mechanism-private audit metadata typing / generation and targeted tests only.
- Did this PR introduce new infrastructure? No.
- Did this PR preserve SourceRef-first behavior? Yes; unchanged.
- Did this PR avoid audit dump into runtime prompt? Yes.
- Did this PR avoid reaction_records as semantic memory? Yes; unchanged.
- Did this PR avoid knowledge_activations as source truth? Yes; unchanged.
- Is this PR safe to review as a small slice? Yes.
