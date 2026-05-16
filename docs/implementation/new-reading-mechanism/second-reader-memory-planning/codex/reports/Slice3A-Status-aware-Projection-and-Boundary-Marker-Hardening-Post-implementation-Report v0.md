# Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0

PR title / branch:
- Slice 3A: Status-aware Projection and Boundary Marker Hardening
- Branch: `main`

Slice:
- Slice 3A / Memory Lifecycle and Projection Hardening

Summary of actual changes:
- Added compact prompt-facing projection markers for active attention, concept digest, thread digest, reflective frame digest, and recent reaction projections.
- Added marker calculation helpers in `state_projection.py` and applied markers only to projection copies returned through carry-forward, navigation, and read prompt packets.
- Kept the persisted `continuation_capsule` on the existing unmarked digest shape.
- Prompt-facing packet metadata changed additively; prompt text and prompt version did not change.

Files changed:
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- `projection_role`, `support_status`, `current_support`, `lineage_only`, and `projection_warning` are present on prompt-facing memory projection copies.
- `visible_trace_support` is present only on reaction-derived projection entries.
- `lineage_only` means not current support; it does not delete, invalidate, or treat an item as useless.
- `source_ref_missing` is a projection warning; it is not invalidation.
- Reaction records remain visible trace and are not semantic memory.
- `knowledge_activations` are not projected in Slice 3A.
- SourceRef-first behavior is preserved.

Deviations from accepted brief:
- None.

Tests added or updated:
- Updated `test_attentional_v2_state_projection.py` to verify current-support markers, lineage-only markers, `source_ref_missing` warnings, reaction visible-trace markers, prompt-packet marker preservation, no `knowledge_activations` projection, and no marker fields in persisted `continuation_capsule`.

Commands run:
- `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_state_projection.py -q`

Test results:
- Passed: `4 passed, 6 warnings`

Contract / audit evidence produced:
- Active attention, concept, thread, and reflective prompt-facing projections now carry compact support markers.
- Recent reaction prompt-facing projections now carry visible-trace markers and `current_support=false`.
- Persisted continuation capsule entries remain unmarked, preserving the previous durable continuity shape.

Sample audit rows or sample output, if applicable:
- Not applicable; Slice 3A changes prompt-facing projection metadata and does not add audit JSONL output.

Backward compatibility notes:
- Additive prompt-facing packet metadata only.
- No prompt text changes.
- No prompt version changes.
- No schema version changes.
- No public API changes.
- No persistence migration required.

Risk / rollback notes:
- Risk: downstream prompt consumers may start relying on additive metadata before the contract is promoted to stable mechanism docs.
- Rollback: revert this Slice 3A PR. Additive projection metadata requires no migration.

Known gaps:
- No lifecycle mutation hardening in `state_ops.py`.
- No retrieval utilization trace hardening.
- No planning trace hardening.
- No slow-cycle candidate / settlement envelope work.
- No `knowledge_activations` projection; future projection must use warrant / context markers and must not become source truth.

Next recommended step:
- Human reviewer reviews and accepts this Slice 3A Post-implementation Report or requests a patch before any next-slice brief or implementation PR.

Required checks:
- Did this PR change behavior, schema, prompt, audit, evaluation, or tests?
  - It changed internal prompt-facing projection packet metadata additively and updated tests. It did not change prompt text, prompt version, schema version, audit JSONL, evaluation outputs, or public API behavior.
- Did this PR introduce new infrastructure?
  - No.
- Did this PR preserve SourceRef-first behavior?
  - Yes.
- Did this PR avoid audit dump into runtime prompt?
  - Yes.
- Did this PR avoid reaction_records as semantic memory?
  - Yes.
- Did this PR avoid knowledge_activations as source truth?
  - Yes; `knowledge_activations` are not projected in Slice 3A.
- Is this PR safe to review as a small slice?
  - Yes. Runtime code changes are limited to `state_projection.py`, and tests are limited to `test_attentional_v2_state_projection.py`.
