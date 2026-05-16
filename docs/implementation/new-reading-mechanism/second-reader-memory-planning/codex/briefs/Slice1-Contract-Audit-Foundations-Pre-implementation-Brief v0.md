# Slice 1-Contract-Audit-Foundations-Pre-implementation-Brief v0

PR title:
Slice 1: Add Contract and Audit Foundations for Memory Uptake Settlement

Slice:
Slice 1 / Contract and Audit Foundations

Design sources:
- `../E实施1-Implementation Feasibility & Delta Audit v0.md`
- `../../E实施0-Implementation Roadmap & Handoff v0.md`
- `../../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `../../C设计3-Memory Formation & Settlement Design v0.md`
- `../../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`

Reviewer constraints accepted for this brief:
- E实施1 is accepted.
- Do not implement code until this Pre-implementation Brief is accepted.
- Slice 1 focuses on additive contract / audit scaffolding, not behavior rejection.
- Missing `target_store` is tolerated in the first pass with explicit audit / compatibility warning, not rejected immediately.
- `resolve` allowlist alignment is accepted in principle but deferred to Slice 2 or a separate brief after audit visibility exists.
- Current-support / lineage / visible-trace / warrant projection markers are deferred to Slice 3.
- Slow-cycle candidate / settlement envelopes are deferred to Slice 6.
- Do not run full AI Evaluation.
- Keep the first PR small and reversible.

Current code facts:
- `ReadUnitResult` already carries `memory_uptake_ops`, and the prompt limits write targets to `active_attention`, `concept_registry`, and `thread_trace`.
- `runner.py` already normalizes `payload.source_quote` into inline `payload.source_refs` before settlement.
- `source_ref_from_unit(...)` already records resolution states such as `matched`, `ambiguous_first_match`, and `fallback_unit_span`.
- `nodes.py` currently defaults missing `target_store` to `active_attention`.
- `nodes.py` currently omits `resolve` from `_STATE_OPERATION_TYPES`, while `schemas.py` and `state_ops.py` recognize `resolve`; this is explicitly out of Slice 1.
- `observability.record_read(...)` persists raw normalized `memory_uptake_ops` and target-store counts.
- `observability.record_settlement(...)` persists compact store deltas but not per-op validation, source binding, compatibility warning, or settlement outcome rows.

Files to change:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`

Files explicitly not changing:
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- public API files
- frontend files
- evaluation runners
- prompt text / prompt versions

Planned deltas:
- Add a small internal audit contract shape for memory uptake operations, using additive fields only.
- Add `memory_uptake_op_contracts` to `read_audit.jsonl` rows, derived from normalized `memory_uptake_ops`.
- Add `memory_uptake_op_outcomes` to `settlement_audit.jsonl` rows, derived from the same operations plus before/after store deltas.
- Include per-op fields sufficient for audit visibility:
  - operation index;
  - operation type;
  - target store as emitted;
  - effective target store after compatibility default;
  - target key / item id;
  - source-ref count;
  - source-ref resolution statuses;
  - compatibility warnings, including `missing_target_store_defaulted`;
  - outcome classification such as `accepted_observed`, `accepted_no_visible_delta`, `skipped_out_of_scope`, or `unclassified`.
- Preserve the current missing-`target_store` runtime behavior in Slice 1 by defaulting to `active_attention` while recording the compatibility warning.
- Do not introduce strict validation, rejection, or behavior changes in this slice.
- Do not align the `resolve` allowlist in this slice.
- Do not introduce projection markers, retrieval utilization traces, planning traces, or slow-cycle envelopes in this slice.

Engineering tests to add/update:
- Add or update `test_attentional_v2_nodes.py` coverage showing a missing `target_store` memory op still normalizes to `active_attention` and carries an auditable compatibility warning or marker.
- Add or update `test_attentional_v2_observability.py` coverage showing `record_settlement(...)` writes `memory_uptake_op_outcomes` without removing existing compact `state_deltas`.
- Add or update `test_attentional_v2_observability.py` coverage showing source-ref resolution statuses are summarized per op when `payload.source_refs` exists.
- Preserve existing assertions for `memory_uptake_ops_by_target_store` and `state_deltas`.

Contract / audit checks:
- SourceRef preserved: source refs stay inline on operation payloads; Slice 1 only summarizes their resolution status in audit rows.
- per-op outcome: added as additive audit metadata; no runtime rejection.
- candidate vs settled separated: not implemented in Slice 1; slow-cycle candidate/settlement envelopes remain deferred to Slice 6.
- audit not routed into prompt: no prompt inputs, prompt text, or prompt versions change.
- reaction_records not semantic memory: unchanged and out of Slice 1.
- knowledge_activations not source truth: unchanged and out of Slice 1.
- other: missing `target_store` is tolerated with explicit compatibility warning in audit.

Behavior smoke, if any:
- No full AI Evaluation.
- No benchmark jobs.
- No long-running runs.
- If implementation needs a runtime smoke, keep it optional and local-only after targeted unit tests pass; do not require it for the first PR unless tests expose uncertainty.

Non-goals:
- No behavior rejection.
- No strict schema validation.
- No `resolve` allowlist alignment.
- No changes to `state_ops.py` settlement behavior.
- No changes to prompt wording or prompt versions.
- No changes to projection, retrieval, planning trace, slow-cycle, public API, frontend, or evaluation runners.
- No vector DB, graph DB, Memory OS, planner agent, memory manager agent, retriever agent, route steering UI, or user route choice.

Risks:
- Audit fields may accidentally imply behavior guarantees that settlement does not yet provide.
- Missing-target-store compatibility handling could be mistaken for an approved long-term policy.
- Per-op outcomes can be approximate when compact before/after deltas do not prove causality for multiple ops touching one item.

Risk controls:
- Name compatibility warnings explicitly and keep them separate from final validation decisions.
- Mark outcomes as audit observations, not formal semantic truth.
- Keep fields additive and readers tolerant.
- Keep the PR small enough to roll back by removing only audit scaffolding.

Rollback plan:
- Revert the Slice 1 PR.
- Because planned fields are additive audit metadata only, rollback should not require data migration.
- Existing `read_audit.jsonl`, `settlement_audit.jsonl`, state stores, prompts, and public API behavior should remain readable after rollback.

Open questions:
- Exact field names may be adjusted during implementation if existing code style strongly favors shorter names, but the semantics above must remain intact.
- If per-op outcome cannot be inferred safely from compact deltas for a case, prefer `unclassified` or `accepted_no_visible_delta` over pretending precision.

Go / no-go recommendation:
- Go for human review of this brief.
- No-go for implementation until this Pre-implementation Brief is accepted.
