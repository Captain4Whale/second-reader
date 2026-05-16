# Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0

PR title / branch:
- PR title: Slice 2A: Operation Vocabulary and Admission Visibility Hardening
- Branch: `main`

Slice:
- Slice 2A / Operation Vocabulary and Admission Visibility Hardening

Summary of actual changes:
- Added `resolve` to the `nodes.py` memory operation admission allowlist.
- Added additive `memory_uptake_admission_events` metadata to `ReadUnitResult`.
- Captured admission events at the `nodes.py` normalization boundary, before unknown or malformed raw operations are dropped.
- Added `memory_uptake_admission_events` to `read_audit.jsonl` rows.
- Preserved missing `target_store` compatibility behavior: missing target store still defaults to `active_attention` and still records `missing_target_store_defaulted`.
- Preserved unknown / malformed operation behavior: those raw ops remain dropped before settlement, but the drop is now visible in audit metadata.
- Preserved all Slice 1 audit fields.

Files changed:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_state_ops.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- `resolve` operation vocabulary is now aligned between schema and node normalization.
- Admission visibility is captured where raw dropped operations are still available.
- Admission events are audit-only and compact.
- Full raw payload dumps are not persisted in admission events.
- Missing `target_store` remains tolerated with compatibility warning.
- `state_ops.py` behavior is unchanged.

Deviations from accepted brief:
- None.
- During targeted test development, a regression assertion initially overclaimed concept/thread `resolve` behavior without explicit payload status. The test was corrected to reflect current `state_ops.py` behavior instead of changing settlement semantics.

Tests added or updated:
- Added `read_unit(...)` coverage showing `resolve` memory ops are admitted by node normalization.
- Added `read_unit(...)` coverage showing unknown and malformed raw ops stay dropped but emit admission events.
- Extended missing-`target_store` node coverage to assert admission metadata.
- Extended read-audit coverage to assert `memory_uptake_admission_events` and old Slice 1 read-audit fields.
- Added `state_ops.py` regression coverage showing existing `resolve` behavior without modifying `state_ops.py`.

Commands run:
- `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py tests/test_attentional_v2_state_ops.py -q`

Test results:
- First targeted run: failed while developing the `state_ops.py` regression assertion because the test expected concept/thread `resolve` to override existing active status without explicit payload status.
- Final targeted run: passed, `22 passed, 6 warnings`.

Contract / audit evidence produced:
- `ReadUnitResult` now has additive `memory_uptake_admission_events`.
- `read_audit.jsonl` rows now include `memory_uptake_admission_events`.
- Admission statuses are:
  - `accepted`
  - `dropped_unknown_operation`
  - `dropped_malformed_operation`
- Admission events contain compact metadata such as operation index, operation type, target-store metadata, compatibility warnings, and drop reason.
- Admission events do not include full raw payload dumps.
- Existing `memory_uptake_ops`, `memory_uptake_op_count`, `memory_uptake_ops_by_target_store`, `memory_uptake_op_contracts`, and `memory_uptake_op_outcomes` are preserved.

Sample audit rows or sample output, if applicable:
- Accepted op sample fields: `operation_index`, `admission_status`, `operation_type_emitted`, `operation_type_normalized`, `target_store_emitted`, `effective_target_store`, `target_key`, `item_id`, `compatibility_warnings`, `drop_reason`.
- Unknown op sample status: `dropped_unknown_operation`.
- Malformed op sample status: `dropped_malformed_operation`.
- Missing target store sample warning: `missing_target_store_defaulted`.

Backward compatibility notes:
- Public API is unchanged.
- Prompt text and prompt versions are unchanged.
- `state_ops.py` behavior is unchanged.
- Unknown / malformed raw operations are still dropped before settlement.
- Missing `target_store` remains tolerated and defaults to `active_attention`.
- New audit fields are additive and mechanism-private.

Risk / rollback notes:
- Admitting `resolve` is a narrow behavior fix: schema-valid `resolve` ops can now reach existing settlement instead of being dropped at node normalization.
- Admission events should not be treated as strict validation authority; they are audit visibility.
- Rollback is a normal revert of this slice. No data migration is required because the new fields are additive audit metadata.

Known gaps:
- Missing `target_store` strict validation remains deferred.
- Store-specific admission hardening beyond operation vocabulary remains deferred.
- Projection markers remain deferred to Slice 3.
- Retrieval utilization, planning trace, and slow-cycle audit envelopes remain deferred.
- Full AI Evaluation remains deferred.

Next recommended step:
- Human reviewer should review and accept this post-implementation report or request a patch.
- Do not start the next implementation slice until this report is accepted and the next Pre-implementation Brief is created and accepted.

Required checks:
- Did this PR change behavior, schema, prompt, audit, evaluation, or tests? Yes: internal schema metadata, node admission allowlist, mechanism-private read audit rows, and targeted tests only.
- Did this PR introduce new infrastructure? No.
- Did this PR preserve SourceRef-first behavior? Yes.
- Did this PR avoid audit dump into runtime prompt? Yes.
- Did this PR avoid reaction_records as semantic memory? Yes.
- Did this PR avoid knowledge_activations as source truth? Yes.
- Is this PR safe to review as a small slice? Yes.
