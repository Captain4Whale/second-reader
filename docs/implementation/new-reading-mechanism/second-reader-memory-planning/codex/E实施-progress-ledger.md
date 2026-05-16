# E实施 Progress Ledger

## Purpose

This is the progress ledger for the Second Reader Memory / Planning optimization implementation track.

Use it to record `E实施1`, each implementation PR, each pre-implementation brief, each post-implementation report, contract gates, test results, review decisions, and next steps.

This ledger is not stable product behavior authority. It does not replace `docs/current-state.md`, `docs/tasks/registry.md`, `docs/tasks/registry.json`, or `docs/history/decision-log.md`.

Stable mechanism behavior changes still need to be promoted to the relevant stable docs when implementation lands and is accepted.

## Current Status

```text
Current phase: Slice 3B Pre-implementation Brief waiting for human review
Implementation status: Slice 1 accepted; Slice 2A accepted; Slice 2B accepted; Slice 3A accepted; no Slice 3B implementation started
Next action: human reviewer accepts the Slice 3B Pre-implementation Brief or requests a patch
Full AI Evaluation: not yet; deferred until core instrumentation is ready
```

## Entry 2026-05-16 — E实施1 feasibility audit created

Type:
- E实施 audit

Slice:
- Slice 0

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md` through `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link:
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- none for implementation code; docs only for E实施1 audit landing

Design contracts addressed:
- accepted Memory / Planning / Evaluation design chain readiness for implementation audit
- SourceRef-first behavior
- deterministic settlement before behavior expansion
- audit-before-behavior implementation posture
- no full AI Evaluation before core instrumentation

Engineering tests:
- Commands run: none
- Result: not run
- Not run / reason: E实施1 is a documentation audit; no implementation code changed

Contract / audit checks:
- SourceRef preserved: audit confirms SourceRef-first contract needs implementation gates
- per-op outcome: missing; proposed for Slice 1
- candidate vs settled separated: partially present; slow-cycle audit gap identified
- audit not routed into prompt: preserved as rule; no code changed
- reaction_records not semantic memory: preserved as rule; projection marker gap identified
- knowledge_activations not source truth: preserved as rule; warrant marker gap identified
- other: retrieval utilization trace and planning restore trace gaps identified

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation deferred until core instrumentation is ready

Post-implementation Report:
- Link:
- Summary:
- Deviations from accepted brief:
- Known gaps:

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up:

Next recommended step:
- Human reviewer accepts E实施1 or requests a patch. If accepted, create a Pre-implementation Brief for Slice 1 / Contract and Audit Foundations.

## Entry 2026-05-16 — E实施1 accepted and Slice 1 brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 1

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Brief: `briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- none for implementation code; docs only for Slice 1 brief landing

Design contracts addressed:
- E实施1 accepted with reviewer constraints
- Slice 1 limited to additive contract / audit scaffolding
- missing `target_store` tolerated with explicit audit / compatibility warning in the first pass
- `resolve` allowlist alignment deferred to Slice 2 or a separate brief after audit visibility exists
- projection markers deferred to Slice 3
- slow-cycle candidate / settlement envelopes deferred to Slice 6
- no full AI Evaluation
- first PR must stay small and reversible

Engineering tests:
- Commands run: none
- Result: not run
- Not run / reason: this entry records a doc-only pre-implementation brief landing; no implementation code changed

Contract / audit checks:
- SourceRef preserved: planned for additive audit visibility only
- per-op outcome: planned for Slice 1 implementation after brief acceptance
- candidate vs settled separated: deferred to Slice 6
- audit not routed into prompt: no prompt changes in the brief
- reaction_records not semantic memory: unchanged and out of Slice 1
- knowledge_activations not source truth: unchanged and out of Slice 1
- other: missing `target_store` remains tolerated in Slice 1 with compatibility warning

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link:
- Summary:
- Deviations from accepted brief:
- Known gaps:

Reviewer decision:
- E实施1 accepted with reviewer constraints; Slice 1 brief waiting for human acceptance
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: accept or patch the Slice 1 Pre-implementation Brief before any implementation PR

Next recommended step:
- Human reviewer accepts `briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md` or requests a patch. Do not implement code yet.

## Entry 2026-05-16 — Slice 1 contract and audit foundations implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 1

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
- Brief: `briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: none; implementation stayed within accepted brief and additional reviewer constraints

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
- additive audit-only scaffolding for normalized `memory_uptake_ops`
- missing `target_store` preserved as tolerated behavior with `missing_target_store_defaulted`
- `read_audit.jsonl` now has `memory_uptake_op_contracts`
- `settlement_audit.jsonl` now has `memory_uptake_op_outcomes`
- per-op outcomes are audit-observed / inferred, not authoritative settlement truth

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py -q`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py -q`
- Result:
  - direct `pytest` command unavailable on PATH
  - `.venv/bin/python -m pytest ...` passed: `15 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; source refs stay inline and resolution statuses are summarized in audit rows
- per-op outcome: yes; added as audit-observed inference from compact state deltas
- candidate vs settled separated: not part of Slice 1; deferred to Slice 6
- audit not routed into prompt: yes; no prompt files changed
- reaction_records not semantic memory: yes; no reaction memory behavior changed
- knowledge_activations not source truth: yes; no knowledge activation behavior changed
- other: `resolve` allowlist alignment deferred to Slice 2 or separate brief

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
- Summary: Slice 1 additive audit scaffolding implemented and targeted tests passed through backend venv.
- Deviations from accepted brief: none
- Known gaps: `resolve` allowlist alignment, projection markers, retrieval utilization, planning traces, and slow-cycle envelopes remain deferred

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: create and accept the Slice 2A Pre-implementation Brief before any Slice 2A implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`. Do not start Slice 2A implementation yet.

## Entry 2026-05-16 — Slice 1 report accepted and Slice 2A brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 2

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
- Brief: `briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: accepted with additional reviewer constraints; implementation stayed within accepted brief

Files changed:
- none for implementation code; docs only for Slice 2A brief landing

Design contracts addressed:
- Slice 1 Post-implementation Report accepted by human reviewer / user
- Slice 2A brief created for operation vocabulary and admission visibility hardening
- `resolve` allowlist alignment scoped for future Slice 2A implementation
- raw unknown / malformed `memory_uptake_ops` admission visibility scoped as audit-only evidence
- missing `target_store` remains tolerated with `missing_target_store_defaulted`
- prompt changes and `state_ops.py` behavior changes explicitly excluded from Slice 2A

Engineering tests:
- Commands run: none
- Result: not run
- Not run / reason: this entry records a doc-only pre-implementation brief landing; no implementation code changed

Contract / audit checks:
- SourceRef preserved: planned; no implementation code changed in this brief landing
- per-op outcome: preserved from Slice 1; no implementation code changed
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: no prompt changes in the brief
- reaction_records not semantic memory: unchanged and out of Slice 2A
- knowledge_activations not source truth: unchanged and out of Slice 2A
- other: Slice 2A implementation remains blocked until this brief is accepted

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link:
- Summary:
- Deviations from accepted brief:
- Known gaps:

Reviewer decision:
- Slice 1 Post-implementation Report accepted; Slice 2A brief accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: implement Slice 2A exactly within the accepted brief and produce a Post-implementation Report

Next recommended step:
- Human reviewer reviews `reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-16 — Slice 2A operation vocabulary and admission visibility implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 2

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 2A implementation instruction

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
- `resolve` is admitted at the `nodes.py` normalization boundary
- `state_ops.py` behavior is unchanged
- raw unknown / malformed `memory_uptake_ops` remain dropped but now emit audit-only admission metadata
- `memory_uptake_admission_events` is additive metadata on `ReadUnitResult`
- `read_audit.jsonl` now writes `memory_uptake_admission_events`
- missing `target_store` still defaults to `active_attention` and records `missing_target_store_defaulted`
- existing Slice 1 audit fields remain present

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py tests/test_attentional_v2_state_ops.py -q`
- Result:
  - first run failed while the `state_ops.py` regression assertion overclaimed concept/thread `resolve` behavior without explicit payload status
  - final run passed: `22 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; source-ref resolution and inline SourceRef semantics unchanged
- per-op outcome: preserved from Slice 1; no new authoritative settlement truth introduced
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes; no prompt files changed
- reaction_records not semantic memory: unchanged
- knowledge_activations not source truth: unchanged
- other: admission events are compact metadata-only and do not persist full raw payload dumps

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
- Summary: Slice 2A operation vocabulary alignment and admission visibility implemented; targeted tests passed through backend venv.
- Deviations from accepted brief: none
- Known gaps: strict missing-target-store validation, broader store-specific admission hardening, projection markers, retrieval utilization, planning trace, and slow-cycle envelopes remain deferred

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: create and accept the Slice 2B Pre-implementation Brief before any Slice 2B implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`. Do not start Slice 2B implementation yet.

## Entry 2026-05-16 — Slice 2A report accepted and Slice 2B brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 2

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 2B implementation instruction

Files changed:
- docs only for Slice 2B brief landing

Design contracts addressed:
- Slice 2A Post-implementation Report accepted by human reviewer / user
- Slice 2B brief created for store-specific admission and target-store policy hardening
- future Slice 2B implementation scoped to audit-only visibility for unsupported `target_store` and operation-store pairing issues
- future Slice 2B implementation remains blocked until this brief is accepted

Engineering tests:
- Commands run:
  - none
- Result:
  - not run; this is a doc-only brief landing task
- Not run / reason:
  - backend tests not run by doc-only task constraint

Contract / audit checks:
- SourceRef preserved: unchanged and out of this doc-only task
- per-op outcome: unchanged and out of this doc-only task
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: unchanged; no prompt files changed
- reaction_records not semantic memory: unchanged and out of Slice 2B
- knowledge_activations not source truth: unchanged and out of Slice 2B
- other: Slice 2B implementation remains blocked until this brief is accepted

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link:
- Summary:
- Deviations from accepted brief:
- Known gaps:

Reviewer decision:
- Slice 2A Post-implementation Report accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: implement Slice 2B exactly within the accepted brief and produce a Post-implementation Report

Next recommended step:
- Human reviewer reviews `reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-16 — Slice 2B store-specific admission and target-store policy hardening implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 2

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 2B implementation instruction

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
- target-store support metadata added to read-output admission events
- operation-store admission policy metadata added to read-output admission events
- unsupported target stores remain normalized and non-rejected
- unsupported operation-store pairings remain normalized and non-rejected
- missing `target_store` still defaults to `active_attention` and records `missing_target_store_defaulted`
- policy warnings are compact and audit-only
- normalized op `compatibility_warnings` surface the same policy risks for existing contract rows
- existing Slice 1 and Slice 2A fields remain present

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_nodes.py -q`
- Result:
  - `20 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; source-ref resolution and inline SourceRef semantics unchanged
- per-op outcome: preserved from Slice 1; no new authoritative settlement truth introduced
- admission vs settlement separated: yes; `admission_status="accepted"` remains normalization admission only
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes; no prompt files changed
- reaction_records not semantic memory: unchanged
- knowledge_activations not source truth: unchanged
- other: `operation_store_policy` is conservative read-path admission-policy visibility, not exact `state_ops.py` behavior

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
- Summary: Slice 2B store-specific admission and target-store policy audit metadata implemented; targeted tests passed through backend venv.
- Deviations from accepted brief: none
- Known gaps: strict target-store validation, strict operation-store pairing validation, projection markers, retrieval utilization, planning trace, and slow-cycle envelopes remain deferred

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: create and accept the Slice 3A Pre-implementation Brief before any Slice 3A implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`. Do not start Slice 3A implementation yet.

## Entry 2026-05-16 — Slice 2B report accepted and Slice 3A brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 3

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 3A implementation instruction

Files changed:
- docs only for Slice 3A brief landing

Design contracts addressed:
- Slice 2B Post-implementation Report accepted by human reviewer / user
- Slice 3A brief created for status-aware projection and boundary marker hardening
- future Slice 3A implementation scoped to prompt-facing projection markers in `state_projection.py`
- future Slice 3A implementation explicitly excludes durable lifecycle mutation, `state_ops.py`, prompt changes, `read_context.py`, retrieval utilization, planning trace, slow-cycle, public API, frontend, and eval runners
- reaction records remain visible trace, not semantic memory
- future knowledge projection remains deferred and must be warrant / context only, not source truth

Engineering tests:
- Commands run:
  - none
- Result:
  - not run; this is a doc-only brief landing task
- Not run / reason:
  - backend tests not run by doc-only task constraint

Contract / audit checks:
- SourceRef preserved: unchanged and planned for future Slice 3A projection markers
- per-op outcome: unchanged and out of Slice 3A
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: no audit dumps are routed into prompts
- reaction_records not semantic memory: preserved as an explicit Slice 3A boundary
- knowledge_activations not source truth: preserved as an explicit Slice 3A boundary
- other: Slice 3A implementation remains blocked until this brief is accepted

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link:
- Summary:
- Deviations from accepted brief:
- Known gaps:

Reviewer decision:
- Slice 2B Post-implementation Report accepted; Slice 3A brief accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: implement Slice 3A exactly within the accepted brief and produce a Post-implementation Report

Next recommended step:
- Human reviewer reviews `reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-16 — Slice 3A status-aware projection and boundary markers implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 3

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 3A implementation instruction

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
- prompt-facing projection markers added for active attention, concept digest, thread digest, reflective frame digest, and recent reaction projections
- prompt-facing packet metadata changed additively while prompt text and prompt version remained unchanged
- `lineage_only` means not current support, not deletion or invalidation
- `source_ref_missing` is a projection warning, not invalidation
- reaction records remain visible trace, not semantic memory
- `knowledge_activations` are not projected in Slice 3A
- persisted `continuation_capsule` remains on the existing unmarked shape

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_state_projection.py -q`
- Result:
  - `4 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; SourceRef selection and inline citation semantics unchanged
- per-op outcome: unchanged and out of Slice 3A
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes; no audit dumps routed into prompts
- reaction_records not semantic memory: yes; reaction projections are marked `visible_trace`
- knowledge_activations not source truth: yes; `knowledge_activations` are not projected
- other: durable lifecycle mutation, settlement behavior, prompt text, prompt version, and schema version unchanged

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
- Summary: Slice 3A status-aware projection and boundary marker metadata implemented; targeted projection tests passed.
- Deviations from accepted brief: none
- Known gaps: lifecycle mutation hardening, retrieval utilization, planning trace, and slow-cycle candidate / settlement envelopes remain deferred

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: create and accept the Slice 3B Pre-implementation Brief before any Slice 3B implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`. Do not start Slice 3B implementation yet.

## Entry 2026-05-16 — Slice 3A report accepted and Slice 3B brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 3

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- docs only for Slice 3B brief landing

Design contracts addressed:
- Slice 3A Post-implementation Report accepted by human reviewer / user
- Slice 3B brief created for lifecycle semantics and state-op boundary hardening
- future Slice 3B implementation must prefer tests and narrow helper-level clarification over broad lifecycle behavior changes
- future Slice 3B implementation explicitly excludes prompt changes, schema migration, retrieval utilization, planning trace, slow-cycle, public API, frontend, eval runners, and full AI Evaluation

Engineering tests:
- Commands run:
  - not run for this doc-only brief landing
- Result:
  - not run
- Not run / reason:
  - this task only creates the Slice 3B Pre-implementation Brief and status updates

Contract / audit checks:
- SourceRef preserved: unchanged and planned for future Slice 3B lifecycle boundary tests
- per-op outcome: unchanged and out of Slice 3B
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: unchanged
- reaction_records not semantic memory: preserved as an explicit Slice 3B boundary
- knowledge_activations not source truth: preserved; Slice 3B does not project `knowledge_activations`
- other: Slice 3B implementation remains blocked until this brief is accepted

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link:
- Summary:
- Deviations from accepted brief:
- Known gaps:

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or patch the Slice 3B Pre-implementation Brief before any Slice 3B implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`. Do not start Slice 3B implementation yet.

## Entry Template

```text
## Entry YYYY-MM-DD — <short title>

Type:
- E实施 audit / pre-implementation brief / implementation PR / post-implementation report / review decision / eval smoke / other

Slice:
- Slice 0 / Slice 1 / Slice 2 / Slice 3 / Slice 4 / Slice 5 / Slice 6 / Slice 7 / Slice 8

Related docs:
- E实施0:
- C设计 source:
- E实施1 / PR / report:

Branch / PR:
- Branch:
- PR:
- Commit:

Pre-implementation Brief:
- Link:
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- none / list files

Design contracts addressed:
- list accepted contracts

Engineering tests:
- Commands run:
- Result:
- Not run / reason:

Contract / audit checks:
- SourceRef preserved:
- per-op outcome:
- candidate vs settled separated:
- audit not routed into prompt:
- reaction_records not semantic memory:
- knowledge_activations not source truth:
- other:

AI Evaluation:
- Full eval run? no / yes
- Smoke only? no / yes
- Eval lane affected:
- Notes:

Post-implementation Report:
- Link:
- Summary:
- Deviations from accepted brief:
- Known gaps:

Reviewer decision:
- accepted / accepted with patch / needs revision / blocked
- Reviewer:
- Decision date:
- Required follow-up:

Next recommended step:
-
```

## Current Planned Sequence

```text
E实施1: Implementation Feasibility & Delta Audit
Slice 1: Contract / Audit Foundations
Slice 2: Memory Formation & Settlement Hardening
Slice 3: Memory Lifecycle / Projection Hardening
Slice 4: Retrieval / Utilization Instrumentation
Slice 5: Planning Trace / Detour / Recall / Look-back Hardening
Slice 6: Slow-cycle Safety
Slice 7: Minimal Eval Implementation Slice
Slice 8: Post-implementation Review & Eval Readiness
```

## Rules

- Do not mark a slice complete without a Post-implementation Report.
- Do not mark implementation accepted without engineering tests or an explicit no-test rationale.
- Do not run full AI Evaluation unless explicitly requested.
- Do not advance to the next slice if the contract / audit gate failed.
- Human reviewer owns go/no-go.
- Codex may recommend the next step but must not self-approve phase transition.
