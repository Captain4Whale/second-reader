# Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0

PR title:
Slice 2A: Operation Vocabulary and Admission Visibility Hardening

Implementation slice:
Slice 2A / Operation Vocabulary and Admission Visibility Hardening.

This is a small Slice 2 sub-slice focused on aligning `StateOperation` vocabulary at the read-output normalization boundary and making pre-normalization admission outcomes visible in audit artifacts. It preserves the Slice 1 audit-first posture and does not start implementation until this brief is accepted.

Design sources:
- `../E实施1-Implementation Feasibility & Delta Audit v0.md`
- `../../E实施0-Implementation Roadmap & Handoff v0.md`
- `../../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `../../C设计3-Memory Formation & Settlement Design v0.md`
- `../../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
- `../reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
- `../E实施-progress-ledger.md`

Reviewer constraints accepted for this brief:
- Slice 1 Post-implementation Report is accepted.
- Do not implement code until this Pre-implementation Brief is accepted.
- Preserve the Slice 1 additive and audit-first posture.
- Do not reject missing `target_store` yet.
- Keep `missing_target_store_defaulted` as a compatibility warning unless a later accepted brief proves a safe migration path.
- Add visibility for raw unknown or malformed `memory_uptake_ops` that are dropped before normalization, if feasible, as audit-only admission evidence.
- Keep the future PR small and reversible.
- Do not change prompts unless the brief clearly justifies it.
- Do not change `state_ops.py` behavior unless explicitly scoped.
- Do not touch projection, retrieval, planning trace, slow-cycle, public API, frontend, or eval runners.
- Do not run full AI Evaluation.

Current code facts:
- `schemas.py` includes `resolve` in `StateOperationType`.
- `state_ops.py` already handles `resolve` for current store settlement behavior:
  - `active_attention` treats `close` and `resolve` as close-like item status mutations.
  - `concept_registry` and `thread_trace` normalize `close` to `resolve` and already apply `resolve`.
- `nodes.py` `_STATE_OPERATION_TYPES` currently omits `resolve`, so a schema-valid `resolve` operation can be dropped before settlement.
- `nodes.py` currently drops non-object, unknown-operation, and other malformed `memory_uptake_ops` before durable read-audit admission evidence exists.
- `nodes.py` still defaults missing `target_store` to `active_attention`, now with Slice 1 metadata: `target_store_emitted`, `effective_target_store`, and `compatibility_warnings`.
- `observability.record_read(...)` now writes Slice 1 `memory_uptake_op_contracts` for normalized ops only.
- `observability.record_settlement(...)` now writes Slice 1 `memory_uptake_op_outcomes` for normalized ops only.
- `prompts.py` constrains `memory_uptake_ops` target stores but does not list the full operation vocabulary in a way that justifies prompt changes in this small slice.

Files to change:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_state_ops.py`

Files explicitly not changing:
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- public API files
- frontend files
- evaluation runners
- prompt text / prompt versions

Planned deltas:
- Add `resolve` to the `nodes.py` read-output normalization allowlist so node normalization matches `schemas.py` and existing `state_ops.py` behavior.
- Add a small internal `memory_uptake_admission_events` shape to capture admission evidence for raw `memory_uptake_ops`.
- Preserve missing `target_store` behavior:
  - continue defaulting to `active_attention`;
  - keep `target_store_emitted`;
  - keep `effective_target_store`;
  - keep `missing_target_store_defaulted` in `compatibility_warnings`.
- Record compact admission events for:
  - accepted normalized operations;
  - unknown operation types dropped before normalization;
  - malformed or non-object raw operation entries dropped before normalization.
- Keep admission events audit-only and compact:
  - include operation index, emitted operation type, normalized operation type when available, target-store metadata when available, admission status, drop reason, and compatibility warnings;
  - do not persist full raw payload dumps into audit artifacts.
- Add `memory_uptake_admission_events` to `read_audit.jsonl` rows while preserving existing Slice 1 fields including `memory_uptake_ops`, `memory_uptake_op_count`, `memory_uptake_ops_by_target_store`, and `memory_uptake_op_contracts`.
- Do not add strict validation or rejection in this slice.
- Do not change settlement semantics in this slice.

Engineering tests:
- Add or update `test_attentional_v2_nodes.py` coverage showing `read_unit(...)` admits a `resolve` memory operation instead of dropping it.
- Add or update `test_attentional_v2_nodes.py` coverage showing unknown-operation and malformed/non-object raw operations are dropped but produce `memory_uptake_admission_events`.
- Preserve existing missing-`target_store` coverage showing the op still normalizes to `active_attention` and records `missing_target_store_defaulted`.
- Add or update `test_attentional_v2_observability.py` coverage showing `record_read(...)` writes `memory_uptake_admission_events`.
- Add or update `test_attentional_v2_observability.py` coverage showing old read-audit fields remain present.
- Add or update `test_attentional_v2_state_ops.py` regression coverage showing current `state_ops.py` already applies `resolve` without changing `state_ops.py` behavior.

Targeted implementation PR test command:
```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py tests/test_attentional_v2_state_ops.py -q
```

Contract / audit checks:
- SourceRef preserved: yes; this slice must not change source-ref resolution or inline SourceRef semantics.
- per-op outcome: preserved from Slice 1; no new authoritative settlement truth is introduced.
- candidate vs settled separated: unchanged and deferred to Slice 6.
- audit not routed into prompt: yes; no prompt inputs, prompt text, or prompt versions change.
- reaction_records not semantic memory: unchanged and out of Slice 2A.
- knowledge_activations not source truth: unchanged and out of Slice 2A.
- operation vocabulary alignment: `resolve` becomes admitted by node normalization to match schema and existing settlement behavior.
- admission visibility: raw unknown or malformed memory uptake entries become visible as compact audit-only admission events.
- missing target store: still tolerated with compatibility warning; no rejection yet.

Behavior smoke, if any:
- No full AI Evaluation.
- No benchmark jobs.
- No long-running reads.
- No runtime smoke required for this small slice unless targeted tests expose uncertainty.

Non-goals:
- No strict rejection of unknown, malformed, or missing-target-store operations.
- No target-store migration.
- No prompt change.
- No `state_ops.py` behavior change.
- No projection markers.
- No retrieval utilization traces.
- No planning trace hardening.
- No slow-cycle candidate or settlement envelopes.
- No public API changes.
- No frontend changes.
- No evaluation runner changes.
- No vector DB, graph DB, Memory OS, planner agent, memory manager agent, retriever agent, route steering UI, or user route choice.

Risks:
- Admitting `resolve` is a narrow behavior fix because a previously dropped schema-valid operation may now reach existing settlement.
- Admission audit fields could be mistaken for strict validation authority if not clearly labeled as audit-only.
- Unknown-op visibility could bloat audit rows if full raw payloads are copied.
- Causality can remain unclear for dropped or malformed entries; admission events should report admission status, not pretend to know downstream settlement effects.

Risk controls:
- Keep the PR small and reversible.
- Keep admission events compact and metadata-only.
- Label unknown and malformed entries as dropped before normalization.
- Keep missing `target_store` as tolerated compatibility behavior.
- Do not change prompts or settlement behavior.

Rollback plan:
- Revert the Slice 2A implementation PR.
- Additive audit fields require no data migration.
- Reverting the PR restores prior node-normalization behavior where `resolve` is not admitted by `_STATE_OPERATION_TYPES`.
- Existing state stores, public API payloads, prompt files, and eval runners should remain unaffected.

Open questions:
- None blocking.
- This brief explicitly chooses no prompt change and no `state_ops.py` behavior change for Slice 2A.
- A later accepted brief may decide whether missing `target_store` should remain tolerated or become strict rejection after enough audit evidence exists.

Go / no-go recommendation:
- Go for human review of this brief.
- No-go for implementation until this Pre-implementation Brief is accepted.
