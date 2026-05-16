# Slice1-Contract-Audit-Foundations-Post-implementation-Report v0

PR title / branch:
- PR title: Slice 1: Add Contract and Audit Foundations for Memory Uptake Settlement
- Branch: `main`

Slice:
- Slice 1 / Contract and Audit Foundations

Summary of actual changes:
- Added audit-only memory uptake operation metadata to normalized `StateOperation` records.
- Preserved current missing `target_store` behavior by continuing to default it to `active_attention`.
- Added explicit compatibility visibility through `target_store_emitted`, `effective_target_store`, and `compatibility_warnings`.
- Added `memory_uptake_op_contracts` to `read_audit.jsonl` rows.
- Added `memory_uptake_op_outcomes` to `settlement_audit.jsonl` rows.
- Marked per-op settlement outcomes as audit-observed inference from compact state deltas, not authoritative settlement truth.

Files changed:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Additive contract / audit scaffolding only.
- Missing `target_store` remains tolerated and defaults to `active_attention`.
- Missing `target_store` now emits `missing_target_store_defaulted`.
- SourceRef-first behavior is preserved; source-ref resolution statuses are summarized from existing inline `source_refs`.
- Per-op outcomes are audit-observed / inferred only.

Deviations from accepted brief:
- None.
- The direct `pytest` command was unavailable from the backend shell PATH, so the same targeted tests were run through `.venv/bin/python -m pytest`.

Tests added or updated:
- Added `test_read_unit_marks_missing_target_store_as_compatibility_default`.
- Added read-audit assertions for `memory_uptake_op_contracts`.
- Added settlement-audit assertions for `memory_uptake_op_outcomes`.
- Added source-ref resolution status summary assertions.
- Added duplicate-target causality coverage so compact-delta ambiguity remains `unclassified`.
- Preserved existing assertions for `memory_uptake_op_count`, `memory_uptake_ops_by_target_store`, and `state_deltas`.

Commands run:
- `cd reading-companion-backend && pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py -q`
- `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py -q`

Test results:
- `pytest ...`: not run; shell returned `command not found` because `pytest` was not on PATH.
- `.venv/bin/python -m pytest ...`: passed, `15 passed, 6 warnings`.

Contract / audit evidence produced:
- `read_audit.jsonl` rows now include additive `memory_uptake_op_contracts`.
- `settlement_audit.jsonl` rows now include additive `memory_uptake_op_outcomes`.
- Existing audit fields remain present.

Sample audit rows or sample output, if applicable:
- Read contract sample fields: `operation_index`, `operation_type`, `target_store_emitted`, `effective_target_store`, `target_key`, `item_id`, `source_ref_count`, `source_ref_resolution_statuses`, `compatibility_warnings`.
- Settlement outcome sample fields: all read contract fields plus `target_id`, `outcome`, and `outcome_basis`.
- Missing target store sample warning: `missing_target_store_defaulted`.
- Outcome basis: `audit_observed_inferred_from_compact_state_delta`.

Backward compatibility notes:
- Runtime behavior is preserved for missing `target_store`.
- Existing audit fields are preserved.
- New fields are additive and mechanism-private.
- No public API, prompt, frontend, evaluation runner, or stable behavior doc changes were made.

Risk / rollback notes:
- Per-op outcomes are intentionally limited to compact-delta inference and may be `unclassified` when causality is unclear.
- Rollback is a normal revert of this slice; no data migration is required because all fields are additive audit metadata.

Known gaps:
- `resolve` allowlist alignment remains deferred to Slice 2 or a separate accepted brief.
- Projection markers remain deferred to Slice 3.
- Retrieval utilization, planning trace, and slow-cycle audit envelopes remain deferred.
- Full AI Evaluation remains deferred.

Next recommended step:
- Human reviewer should review and accept this post-implementation report or request a patch.
- Do not start Slice 2 or any new implementation PR until this report is accepted and the next Pre-implementation Brief is created and accepted.

Required checks:
- Did this PR change behavior, schema, prompt, audit, evaluation, or tests? Yes: internal schema metadata, mechanism-private audit rows, and targeted tests only.
- Did this PR introduce new infrastructure? No.
- Did this PR preserve SourceRef-first behavior? Yes.
- Did this PR avoid audit dump into runtime prompt? Yes.
- Did this PR avoid reaction_records as semantic memory? Yes.
- Did this PR avoid knowledge_activations as source truth? Yes.
- Is this PR safe to review as a small slice? Yes.
