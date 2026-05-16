# Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0

PR title:
Slice 2B: Store-specific Admission and Target-store Policy Hardening

Implementation slice:
Slice 2B / Store-specific Admission and Target-store Policy Hardening.

This is a small, reversible Slice 2 sub-slice focused on audit-only visibility for unsupported `target_store` values and unsupported operation-store pairings at the read-output normalization boundary. It builds on Slice 1 contract/audit foundations and Slice 2A admission events. It does not start implementation until this brief is accepted.

Design sources:
- `../E实施1-Implementation Feasibility & Delta Audit v0.md`
- `../../E实施0-Implementation Roadmap & Handoff v0.md`
- `../../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `../../C设计3-Memory Formation & Settlement Design v0.md`
- `../../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
- `../reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
- `Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
- `../reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
- `../E实施-progress-ledger.md`

Reviewer constraints accepted for this brief:
- Slice 2A Post-implementation Report is accepted.
- Do not implement code until this Pre-implementation Brief is accepted.
- Continue the audit-first implementation strategy.
- Build on Slice 1 and Slice 2A.
- Keep read-path `memory_uptake_ops` bounded to `active_attention`, `concept_registry`, and `thread_trace`.
- Add audit-only visibility for unsupported `target_store` and operation-store pairing issues, if feasible.
- Keep missing `target_store` tolerated with `missing_target_store_defaulted`.
- Do not introduce strict rejection unless a later accepted brief proves a safe migration path.
- Do not change prompts unless clearly justified.
- Do not change `state_ops.py` behavior unless explicitly scoped and justified.
- Do not touch projection, retrieval, planning trace, slow-cycle, public API, frontend, or eval runners.
- Do not run full AI Evaluation.
- Keep the future PR small and reversible.
- Keep admission events compact and audit-only.
- Do not persist full raw payload dumps.
- Do not treat admission events as authoritative settlement truth.
- Preserve Slice 1 and Slice 2A fields:
  - `memory_uptake_ops`
  - `memory_uptake_op_count`
  - `memory_uptake_ops_by_target_store`
  - `memory_uptake_op_contracts`
  - `memory_uptake_op_outcomes`
  - `memory_uptake_admission_events`

Current code facts:
- `prompts.py` already constrains read-path `memory_uptake_ops` to the bounded target stores `active_attention`, `concept_registry`, and `thread_trace`.
- `nodes.py` now admits `resolve` after Slice 2A and emits `memory_uptake_admission_events` at the raw-op normalization boundary.
- `nodes.py` currently admits known operation types even when the emitted or effective `target_store` is outside the bounded read-path stores.
- `nodes.py` still defaults missing `target_store` to `active_attention` and records `missing_target_store_defaulted` in `compatibility_warnings`.
- `memory_uptake_admission_events` currently distinguish accepted, unknown-operation drops, and malformed-operation drops, but do not yet expose target-store support or operation-store pairing policy.
- `observability.record_read(...)` writes `memory_uptake_admission_events` from `ReadUnitResult`; compact additive fields on those events can flow into `read_audit.jsonl` without prompt or runtime behavior changes.
- `state_ops.py` applies store-specific settlement behavior and silently ignores or no-ops some out-of-scope inputs, but this brief does not change `state_ops.py`.
- `prompts.py` does not need to change in Slice 2B because it already states the bounded target-store contract.

Files to change:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`

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
- Add compact audit-only policy fields to `MemoryUptakeAdmissionEvent`:
  - `target_store_supported`
  - `operation_store_policy`
  - `policy_warnings`
- Keep `admission_status="accepted"` for known operations that remain normalized. Admission status must continue to mean normalization admission only, not settlement success.
- Add a bounded read-path target-store policy in `nodes.py`:
  - supported stores: `active_attention`, `concept_registry`, `thread_trace`
  - unsupported stores: record `unsupported_target_store` in audit metadata and compatibility warnings, but do not reject the op in Slice 2B
- Evaluate operation-store policy after missing-`target_store` defaulting:
  - if `target_store` is missing, effective store remains `active_attention`
  - `missing_target_store_defaulted` remains in `compatibility_warnings`
  - target-store support and operation-store policy are evaluated against the effective store
- Add conservative operation-store pairing visibility:
  - `active_attention`: `append`, `create`, `update`, `reactivate`, `cool`, `close`, `resolve`, `link`, `link_anchors`, `drop`
  - `concept_registry`: `append`, `create`, `update`, `link`, `close`, `resolve`, `drop`, `reactivate`
  - `thread_trace`: `append`, `create`, `update`, `link`, `close`, `resolve`, `drop`, `reactivate`
- For known operations with unsupported operation-store pairings, keep the op normalized but record `unsupported_operation_for_target_store` in admission metadata and compatibility warnings.
- Keep admission events compact and metadata-only. Do not persist full raw payload dumps.
- Preserve existing Slice 1 and Slice 2A fields in `read_audit.jsonl` and settlement audit outputs.
- Do not add strict validation or rejection in this slice.
- Do not change settlement semantics in this slice.

Engineering tests:
- Add or update `test_attentional_v2_nodes.py` coverage showing an unsupported target store, such as a known operation targeting `reflective_frames`, remains normalized but emits:
  - `target_store_supported=false`
  - `operation_store_policy=unsupported_target_store`
  - `unsupported_target_store` in `policy_warnings`
  - `unsupported_target_store` in normalized op `compatibility_warnings`
- Add or update `test_attentional_v2_nodes.py` coverage showing an unsupported operation-store pairing, such as `cool` targeting `concept_registry`, remains normalized but emits:
  - `target_store_supported=true`
  - `operation_store_policy=unsupported_operation_for_target_store`
  - `unsupported_operation_for_target_store` in `policy_warnings`
  - `unsupported_operation_for_target_store` in normalized op `compatibility_warnings`
- Preserve missing-`target_store` coverage showing the op still normalizes to `active_attention` and records `missing_target_store_defaulted`.
- Add or update supported-pair coverage showing a valid pairing has no new policy warning.
- Add or update `test_attentional_v2_observability.py` coverage showing `read_audit.jsonl` preserves Slice 1 and Slice 2A fields and includes the new compact policy fields inside `memory_uptake_admission_events`.

Targeted implementation PR test command:
```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py -q
```

Contract / audit checks:
- SourceRef preserved: yes; this slice must not change source-ref resolution or inline SourceRef semantics.
- per-op outcome: preserved from Slice 1; no new authoritative settlement truth is introduced.
- admission vs settlement separated: yes; admission policy fields describe normalization and compatibility evidence only.
- candidate vs settled separated: unchanged and deferred to Slice 6.
- audit not routed into prompt: yes; no prompt inputs, prompt text, or prompt versions change.
- reaction_records not semantic memory: unchanged and out of Slice 2B.
- knowledge_activations not source truth: unchanged and out of Slice 2B.
- missing target store: still tolerated with `missing_target_store_defaulted`; no rejection yet.
- unsupported target store: visible as audit-only compatibility evidence; no rejection yet.
- unsupported operation-store pairing: visible as audit-only compatibility evidence; no settlement behavior change.

Behavior smoke, if any:
- No full AI Evaluation.
- No benchmark jobs.
- No long-running reads.
- No runtime smoke required for this small slice unless targeted tests expose uncertainty.

Non-goals:
- No strict rejection of unsupported target stores.
- No strict rejection of unsupported operation-store pairings.
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
- `admission_status="accepted"` could be misread as downstream settlement success.
- Operation-store policy could be mistaken for an exact description of all current `state_ops.py` behavior.
- Unsupported target stores may still normalize and later no-op or be ignored by settlement.
- Audit rows could become noisy if policy evidence is too verbose.

Risk controls:
- State explicitly that admission events are not authoritative settlement truth.
- Treat operation-store policy as conservative admission-policy visibility, not a rewrite of `state_ops.py`.
- Keep fields compact and metadata-only.
- Prefer warnings over rejection in Slice 2B.
- Keep prompt and settlement files unchanged.

Rollback plan:
- Revert the Slice 2B implementation PR.
- Additive audit fields require no data migration.
- Reverting the PR restores Slice 2A admission visibility without target-store or operation-store policy metadata.
- Existing state stores, public API payloads, prompt files, and eval runners should remain unaffected.

Open questions:
- None blocking.
- This brief explicitly chooses no prompt change for Slice 2B.
- This brief explicitly chooses no `state_ops.py` behavior change for Slice 2B.
- This brief explicitly chooses no strict rejection for Slice 2B.
- A later accepted brief may decide whether unsupported target stores or unsupported operation-store pairings should become strict validation failures after enough audit evidence exists.

Go / no-go recommendation:
- Go for human review of this brief.
- No-go for implementation until this Pre-implementation Brief is accepted.
