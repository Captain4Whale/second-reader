# Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0

PR title / branch:
- PR title: Slice 2B: Store-specific Admission and Target-store Policy Hardening
- Branch: `main`

Slice:
- Slice 2B / Store-specific Admission and Target-store Policy Hardening

Summary of actual changes:
- Added compact audit-only target-store and operation-store policy metadata to `memory_uptake_admission_events`.
- Preserved normalization behavior for known operations:
  - missing `target_store` still defaults to `active_attention`;
  - unsupported `target_store` remains normalized;
  - unsupported operation-store pairings remain normalized;
  - no strict rejection was introduced.
- Added policy warnings to normalized op `compatibility_warnings` so existing `memory_uptake_op_contracts` also expose compatibility risk.
- Kept `admission_status="accepted"` as normalization admission only, not downstream settlement success.
- Did not change prompt text, `state_ops.py`, runner, projection, retrieval, planning trace, slow-cycle, public API, frontend, or eval runners.

Files changed:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Store-specific admission policy visibility added at the `nodes.py` normalization boundary.
- `active_attention`, `concept_registry`, and `thread_trace` remain the bounded read-path stores for admission policy visibility.
- Missing `target_store` remains tolerated with `missing_target_store_defaulted`.
- Unsupported `target_store` emits `unsupported_target_store` as audit / compatibility metadata only.
- Unsupported operation-store pairing emits `unsupported_operation_for_target_store` as audit / compatibility metadata only.
- Admission events remain compact and do not persist full raw payload dumps.
- Admission events are not authoritative settlement truth.
- Slice 1 and Slice 2A fields remain present:
  - `memory_uptake_ops`
  - `memory_uptake_op_count`
  - `memory_uptake_ops_by_target_store`
  - `memory_uptake_op_contracts`
  - `memory_uptake_op_outcomes`
  - `memory_uptake_admission_events`

Deviations from accepted brief:
- None.

Tests added or updated:
- Added node coverage for unsupported target-store policy metadata.
- Added node coverage for unsupported operation-store pairing policy metadata.
- Added node coverage showing supported operation-store pairs receive policy metadata without warnings.
- Updated missing-target-store and resolve-admission expectations for additive policy metadata.
- Updated read-audit coverage to assert the additive policy fields pass through while old audit fields remain present.

Commands run:
- `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py -q`

Test results:
- `20 passed, 6 warnings`

Contract / audit evidence produced:
- Accepted known operations now include:
  - `target_store_supported`
  - `operation_store_policy`
  - `policy_warnings`
- Unsupported target-store example:
  - `target_store_supported=false`
  - `operation_store_policy=unsupported_target_store`
  - `policy_warnings=["unsupported_target_store"]`
- Unsupported operation-store pairing example:
  - `target_store_supported=true`
  - `operation_store_policy=unsupported_operation_for_target_store`
  - `policy_warnings=["unsupported_operation_for_target_store"]`

Sample audit rows or sample output, if applicable:
- `read_audit.jsonl` rows continue to include `memory_uptake_admission_events`.
- Each accepted admission event can now carry compact policy metadata while dropped unknown or malformed entries remain metadata-only and payload-free.

Backward compatibility notes:
- Additive mechanism-private audit fields only.
- No public API migration required.
- Existing missing-`target_store` behavior is preserved.
- Existing settlement behavior is preserved.

Risk / rollback notes:
- Risk: `admission_status="accepted"` could be misread as settlement success.
- Mitigation: report and tests keep the distinction explicit; `operation_store_policy` is admission-policy visibility only.
- Rollback: revert this Slice 2B PR. Additive audit fields require no migration.

Known gaps:
- No strict target-store rejection yet.
- No strict operation-store pairing rejection yet.
- No `state_ops.py` semantics change.
- No projection markers, retrieval utilization trace, planning trace hardening, or slow-cycle candidate / settlement envelope work.

Next recommended step:
- Human reviewer reviews and accepts this Slice 2B Post-implementation Report or requests a patch before any next-slice brief or implementation PR.

Required checks:
- Did this PR change behavior, schema, prompt, audit, evaluation, or tests?
  - It changed internal TypedDict shape, mechanism-private audit metadata, and targeted tests only.
- Did this PR introduce new infrastructure?
  - No.
- Did this PR preserve SourceRef-first behavior?
  - Yes; SourceRef handling was unchanged.
- Did this PR avoid audit dump into runtime prompt?
  - Yes; prompt inputs and prompt text were unchanged.
- Did this PR avoid reaction_records as semantic memory?
  - Yes; unchanged.
- Did this PR avoid knowledge_activations as source truth?
  - Yes; unchanged.
- Is this PR safe to review as a small slice?
  - Yes.
