# Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0

PR title / branch:
- Slice 3B: Lifecycle Semantics and State-op Boundary Hardening
- Branch: `main`

Slice:
- Slice 3B / Memory Lifecycle and Projection Hardening

Summary of actual changes:
- Added targeted lifecycle-boundary tests for active attention, concept registry, thread trace, reaction records, and reflective supersession.
- Added projection compatibility assertions that keep Slice 3A marker semantics stable for cooling and superseded entries.
- Kept Slice 3B test-first and contract-focused.
- No `state_ops.py` runtime behavior changed.
- No schema, prompt, public API, frontend, eval runner, retrieval, planning trace, or slow-cycle code changed.

Files changed:
- `reading-companion-backend/tests/test_attentional_v2_state_ops.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Cooling is a lifecycle status, not invalidation or deletion.
- Resolve / close preserve active-attention items and source refs; `drop` remains the explicit deletion path.
- Concept and thread lifecycle behavior remains deterministic and store-specific.
- Concept and thread operations ignore mismatched target stores.
- Concept and thread `close` can route through the resolve path without forcing active-attention semantics.
- Reaction records remain append-only visible trace.
- Reflective supersession marks lineage state without mutating the superseded statement.
- Slice 3A projection markers are preserved: cooling remains current support; superseded reflective entries project as lineage-only.
- `source_ref_missing` remains a projection warning, not invalidation.
- `knowledge_activations` remain unprojected.

Deviations from accepted brief:
- None.

Tests added or updated:
- Updated `test_attentional_v2_state_ops.py` with lifecycle-boundary coverage for active attention, concept registry, thread trace, reaction append-only behavior, and reflective supersession.
- Updated `test_attentional_v2_state_projection.py` with Slice 3A marker compatibility coverage for cooling and superseded entries.

Commands run:
- `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_state_ops.py tests/test_attentional_v2_state_projection.py -q`

Test results:
- Passed: `12 passed, 6 warnings`

Contract / audit evidence produced:
- Test assertions now lock that lifecycle state changes do not imply deletion or invalidation.
- Test assertions now lock that concept and thread stores remain store-specific instead of being forced to match active-attention semantics.
- Test assertions now lock that reaction records are append-only visible trace and that supersede does not destructively overwrite reflective statements.
- Test assertions now lock that Slice 3A projection markers remain stable for cooling and superseded entries.

Sample audit rows or sample output, if applicable:
- Not applicable; Slice 3B adds tests and does not add audit JSONL output.

Backward compatibility notes:
- No runtime behavior changes.
- No `state_ops.py` behavior changes.
- No prompt text changes.
- No prompt version changes.
- No schema version changes.
- No public API changes.
- No persistence migration required.

Risk / rollback notes:
- Risk: the tests document current store-specific lifecycle semantics, including concept/thread preservation of existing status unless the payload explicitly changes it. This is intentional and should not be read as a broad lifecycle redesign.
- Rollback: revert this Slice 3B PR. Test-only and documentation changes require no migration.

Known gaps:
- No behavior-level lifecycle hardening beyond tests.
- No retrieval utilization trace hardening.
- No planning trace hardening.
- No slow-cycle candidate / settlement envelope work.
- No `knowledge_activations` projection.

Next recommended step:
- Human reviewer reviews and accepts this Slice 3B Post-implementation Report or requests a patch before any next-slice brief or implementation PR.

Required checks:
- Did this PR change behavior, schema, prompt, audit, evaluation, or tests?
  - It changed tests and implementation-track docs only. It did not change runtime behavior, schema, prompt text, audit output, evaluation output, public API, frontend, or eval runners.
- Did this PR introduce new infrastructure?
  - No.
- Did this PR preserve SourceRef-first behavior?
  - Yes.
- Did this PR avoid audit dump into runtime prompt?
  - Yes.
- Did this PR avoid reaction_records as semantic memory?
  - Yes.
- Did this PR avoid knowledge_activations as source truth?
  - Yes; `knowledge_activations` are not projected.
- Is this PR safe to review as a small slice?
  - Yes. Runtime implementation code is unchanged; code-facing changes are limited to targeted tests.
