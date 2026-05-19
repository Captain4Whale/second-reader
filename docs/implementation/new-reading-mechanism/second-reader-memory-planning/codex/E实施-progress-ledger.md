# E实施 Progress Ledger

## Purpose

This is the progress ledger for the Second Reader Memory / Planning optimization implementation track.

Use it to record `E实施1`, each implementation PR, each pre-implementation brief, each post-implementation report, contract gates, test results, review decisions, and next steps.

This ledger is not stable product behavior authority. It does not replace `docs/current-state.md`, `docs/tasks/registry.md`, `docs/tasks/registry.json`, or `docs/history/decision-log.md`.

Stable mechanism behavior changes still need to be promoted to the relevant stable docs when implementation lands and is accepted.

## Current Status

```text
Current phase: Memory / Planning / Minimal Eval implementation track closed after Slice 8H
Implementation status: Slice 1 accepted; Slice 2A accepted; Slice 2B accepted; Slice 3A accepted; Slice 3B accepted; Slice 4A accepted including precision patch; Slice 4B accepted; Slice 5A accepted; Slice 5B accepted; Slice 6A accepted including carried SourceRef audit precision patch; Slice 6B no-code closure brief accepted; Slice 6 closed; Slice 7A accepted; Slice 7B accepted; Slice 8A accepted; Slice 8B accepted; Slice 8C execution brief accepted; Slice 8C bounded Lane A execution attempted and failed before summary generation; Slice 8C report accepted as failed execution evidence; Slice 8D Lane A source-locator compatibility patch accepted; Slice 8E Lane A `_retry1` accepted; Slice 8F Lane B bounded diagnostic smoke accepted; Slice 8G closure report accepted; Slice 8H diagnostic evidence catalog entry brief accepted; Slice 8H diagnostic catalog entry report accepted; implementation track closed; post-Slice8H Eval-1 broader active evaluation attempt stopped and recorded as aborted operational evidence
Next action: no active implementation or eval job remains in this track; do not retry Eval-1 or reuse partial producer outputs until a separate accepted brief or patch plan addresses LLM-health / fallback guardrails and assigns fresh run ids
Full AI Evaluation: post-Slice8H broader active evaluation was attempted but stopped before valid summaries; no valid full-evaluation evidence is accepted from that attempt
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
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 3B implementation instruction

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
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: implement Slice 3B exactly within the accepted brief and produce a Post-implementation Report

Next recommended step:
- Human reviewer reviews `reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-16 — Slice 3B lifecycle semantics and state-op boundaries implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 3

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 3B implementation instruction

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
- cooling is not invalidation or deletion
- resolve / close preserve active-attention items and source refs
- active-attention `drop` remains the explicit deletion path
- concept and thread lifecycle behavior remains deterministic and store-specific
- reaction records remain append-only visible trace
- reflective supersession does not destructively overwrite the superseded statement
- Slice 3A projection markers remain stable for cooling and superseded entries
- `knowledge_activations` are not projected in Slice 3B

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_state_ops.py tests/test_attentional_v2_state_projection.py -q`
- Result:
  - `12 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; tests assert lifecycle operations preserve source refs where applicable
- per-op outcome: unchanged and out of Slice 3B
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: unchanged
- reaction_records not semantic memory: yes; reaction helper remains append-only visible trace
- knowledge_activations not source truth: yes; `knowledge_activations` are not projected
- other: no `state_ops.py` runtime behavior changed

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
- Summary: Slice 3B lifecycle semantics and state-op boundary hardening implemented as targeted tests and implementation-track documentation.
- Deviations from accepted brief: none
- Known gaps: no behavior-level lifecycle hardening beyond tests; retrieval utilization, planning trace, and slow-cycle candidate / settlement envelopes remain deferred

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or patch the Slice 3B Post-implementation Report before any next-slice brief or implementation PR

Next recommended step:
- Human reviewer accepts `reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md` or requests a patch. Do not start the next implementation slice yet.

## Entry 2026-05-16 — Slice 3B report accepted and Slice 4A brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 4

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- docs only for Slice 4A brief landing

Design contracts addressed:
- Slice 3B Post-implementation Report accepted by human reviewer / user
- Slice 4A brief created for supplemental retrieval intent and context assembly contract visibility
- future Slice 4A implementation must clarify `look_back` as source calibration and `active_recall` as memory recovery
- future Slice 4A implementation must preserve the distinction between source excerpts / source refs and settled memory / visible trace refs
- future Slice 4A implementation must not build a new retriever, broad RAG pipeline, full utilization trace, or full active-recall object projection into the Read prompt packet
- future Slice 4A implementation explicitly excludes prompt text changes, runner changes, `state_ops.py`, durable memory state, navigation / detour policy, slow-cycle, public API, frontend, eval runners, and full AI Evaluation

Engineering tests:
- Commands run:
  - not run for this doc-only brief landing
- Result:
  - not run
- Not run / reason:
  - this task only creates the Slice 4A Pre-implementation Brief and status updates

Contract / audit checks:
- SourceRef preserved: unchanged and planned for future Slice 4A retrieval-boundary tests
- per-op outcome: unchanged and out of Slice 4A
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: unchanged; Slice 4A brief excludes audit dumps and prompt text changes
- reaction_records not semantic memory: preserved as an explicit Slice 4A boundary
- knowledge_activations not source truth: preserved; Slice 4A does not project `knowledge_activations`
- other: Slice 4A implementation remains blocked until this brief is accepted

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
- Slice 3B report accepted; Slice 4A brief waiting for human acceptance
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: accept or patch the Slice 4A Pre-implementation Brief before any Slice 4A implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`. Do not start Slice 4A implementation yet.

## Entry 2026-05-16 — Slice 4A supplemental retrieval intent and context assembly contract implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 4

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
- Brief: `briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: additional reviewer constraints from the Slice 4A implementation instruction

Files changed:
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_read_context.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- `look_back` is explicitly marked as source calibration
- `active_recall` is explicitly marked as memory recovery
- supplemental retrieval result boundaries are visible through compact metadata
- merged supplemental bundles preserve compact `retrieval_events`
- prompt-facing `selective_carry.retrieval_context` exposes result groups and full-object forwarding policy
- active-recall concepts, threads, and reactions are not forwarded as full objects into the Read prompt packet in Slice 4A
- reaction records remain visible trace, not semantic memory
- `knowledge_activations` are not projected or treated as source truth
- full retrieval utilization trace remains deferred

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_read_context.py tests/test_attentional_v2_state_projection.py -q`
- Result:
  - `8 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; look_back remains source-ref / excerpt oriented and active_recall refs remain source-ref-backed where available
- per-op outcome: unchanged and out of Slice 4A
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes; no audit dumps are routed into prompts
- reaction_records not semantic memory: yes; reaction refs are marked visible trace with `semantic_memory=false`
- knowledge_activations not source truth: yes; `knowledge_activations` are not projected
- other: `observability.py` was not changed; `read_audit` retrieval utilization trace remains deferred

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
- Summary: Slice 4A supplemental retrieval intent and prompt-facing context assembly contract metadata implemented with focused tests.
- Deviations from accepted brief: none
- Known gaps: full retrieval utilization trace, read-audit retrieval-intent evidence, and full active-recall object projection remain deferred

Reviewer decision:
- accepted with patch
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: complete the precise `result_groups` / forwarding metadata patch before any Slice 4B brief or implementation PR

Next recommended step:
- Complete and review `reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`. Do not start Slice 4B yet.

## Entry 2026-05-16 — Slice 4A precise result groups patch implemented

Type:
- implementation PR
- patch report

Slice:
- Slice 4

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- Prior report: `reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: Slice 4A report direction accepted with required precision patch before Slice 4B

Files changed:
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/tests/test_attentional_v2_read_context.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- `result_groups` now represents actual non-empty result groups after resolution
- `look_back` result groups are derived from actual `source_refs`, `excerpts`, and `refs`
- `active_recall` result groups are derived from actual `concepts`, `threads`, `reactions`, and `refs`
- `not_forwarded_result_groups` now excludes absent groups because it is derived from precise result groups
- active-recall full concepts, threads, and reactions remain not forwarded as full objects
- reaction records remain visible trace, not semantic memory
- `knowledge_activations` remain excluded

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_read_context.py tests/test_attentional_v2_state_projection.py -q`
- Result:
  - `10 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; retrieval refs remain compact and source-ref-oriented where available
- per-op outcome: unchanged and out of Slice 4A
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes; no audit dumps are routed into prompts
- reaction_records not semantic memory: yes; reaction refs remain visible trace with `semantic_memory=false`
- knowledge_activations not source truth: yes; `knowledge_activations` are not projected
- other: `observability.py` was not changed; `read_audit` retrieval utilization trace remains deferred

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- Summary: Slice 4A metadata now reports actual non-empty retrieval groups and precise non-forwarded groups.
- Deviations from accepted patch scope: none
- Known gaps: full retrieval utilization trace, read-audit retrieval-intent evidence, and full active-recall object projection remain deferred

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: create Slice 4B Pre-implementation Brief before any Slice 4B implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`. Do not start Slice 4B implementation yet.

## Entry 2026-05-16 — Slice 4A patch accepted and Slice 4B brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 4

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- Brief: `briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- docs only for Slice 4B brief landing

Design contracts addressed:
- Slice 4A precision patch accepted
- Slice 4B brief created for compact `read_audit.jsonl` retrieval evidence
- future Slice 4B implementation must not change retrieval behavior
- future Slice 4B implementation must not claim actual model utilization unless Read output explicitly supports it
- future Slice 4B implementation keeps full utilization trace deferred
- future Slice 4B implementation excludes prompt text changes, `runner.py` changes, `state_ops.py`, slow-cycle, durable memory state, public API, frontend, eval runners, and full AI Evaluation

Engineering tests:
- Commands run:
  - none
- Result:
  - not run; doc-only brief landing
- Not run / reason:
  - backend tests not run by scope; full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: unchanged; future Slice 4B tests should cover compact supplemental retrieval audit evidence
- per-op outcome: unchanged and out of Slice 4B
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: unchanged; Slice 4B brief excludes audit dumps routed into prompts
- reaction_records not semantic memory: preserved as an explicit Slice 4B boundary
- knowledge_activations not source truth: preserved; Slice 4B does not project `knowledge_activations`
- other: Slice 4B implementation remains blocked until this brief is accepted

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
- Required follow-up: accept or patch the Slice 4B Pre-implementation Brief before any Slice 4B implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`. Do not start Slice 4B implementation yet.

## Entry 2026-05-16 — Slice 4B implemented and post-report created

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 4

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Brief: `briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
- Report: `reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: compact `read_audit` retrieval evidence only; no retrieval behavior change, no `runner.py` change, no prompt text/version change, no full utilization trace, no full AI Evaluation

Files changed:
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- `read_audit.jsonl` records compact `supplemental_retrieval` only when supplemental retrieval metadata exists
- no empty `supplemental_retrieval` block is written when no retrieval metadata exists
- prompt-facing forwarding logic is shared through `build_supplemental_selective_carry(...)`
- `look_back` remains source calibration
- `active_recall` remains memory recovery
- reaction refs remain visible trace, not semantic memory
- `knowledge_activations` remain excluded
- retrieval availability is not claimed as actual model utilization
- current runner main read path still passes `supplemental_context=None`; this PR does not create a supplemental retrieval loop

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_state_projection.py -q`
- Result:
  - `12 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; returned and forwarded supplemental refs are compact id summaries
- per-op outcome: unchanged and out of Slice 4B
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes; read-audit evidence is not routed into prompts
- reaction_records not semantic memory: yes; visible-trace refs are counted separately from semantic memory refs
- knowledge_activations not source truth: yes; `knowledge_activations` are not projected or counted as source truth
- other: `utilization_observed=false` and `utilization_basis="not_claimed_by_read_output"` are fixed in Slice 4B

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
- Summary: Slice 4B adds compact read-audit retrieval evidence for supplemental contexts with retrieval metadata, while leaving retrieval behavior, runner flow, prompt text/version, and full utilization trace unchanged.
- Deviations from accepted brief: none
- Known gaps: main runner path still passes `supplemental_context=None`; no supplemental retrieval loop; actual model utilization not observed or claimed; full retrieval utilization trace deferred

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or patch the Slice 4B Post-implementation Report before any next implementation slice

Next recommended step:
- Human reviewer reviews `reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-16 — Slice 4B report accepted and Slice 5A brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 5

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计2-Planning Ontology Design v0.md`, `../C设计4-Navigation Policy Design v0.md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Accepted report: `reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
- Brief: `briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- docs only for Slice 5A brief landing

Design contracts addressed:
- Slice 4B Post-implementation Report accepted by human reviewer / user
- Slice 5A brief created for detour lifecycle and navigation trace audit hardening
- future Slice 5A must preserve the current Navigate act space: `choose_unit`, `request_skill`, `defer_detour`
- future Slice 5A must keep `deferred` as a navigation outcome or audit reason, not a new durable detour status
- future Slice 5A must not introduce new planner behavior, route steering, user route choice, visible route UX, retrieval behavior changes, prompt text changes, public API/frontend/eval runner changes, or full AI Evaluation

Engineering tests:
- Commands run: none
- Result: not run; doc-only brief landing
- Not run / reason: backend tests not run by scope; full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: unchanged; future Slice 5A must preserve source-grounded mainline continuity
- per-op outcome: unchanged and out of Slice 5A
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: unchanged; Slice 5A brief excludes audit dumps routed into prompts
- reaction_records not semantic memory: unchanged and out of Slice 5A
- knowledge_activations not source truth: unchanged and out of Slice 5A
- other: detour must remain planning path deviation; `active_recall` remains memory recovery; `look_back` remains source calibration

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
- Required follow-up: accept or patch the Slice 5A Pre-implementation Brief before any Slice 5A implementation PR

Next recommended step:
- Human reviewer reviews `briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`. Do not start Slice 5A implementation yet.

## Entry 2026-05-16 — Slice 5A implemented and post-report created

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 5

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计2-Planning Ontology Design v0.md`, `../C设计4-Navigation Policy Design v0.md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Brief: `briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
- Report: `reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-16
- Scope changes approved: compact optional trace metadata and compact `read_audit` navigation/detour evidence only; no new planner behavior, no new Navigate decisions, no durable `deferred` status, no retrieval loop, no prompt text/version change, no full AI Evaluation

Files changed:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- detour lifecycle trace records open, defer/abandon, resolve, and restore-mainline reasons as compact audit metadata
- durable detour statuses remain `open`, `resolved`, and `abandoned`
- no durable `deferred` status introduced
- Navigate act space remains `choose_unit`, `request_skill`, and `defer_detour`
- read-audit navigation/detour evidence is written only when available
- no new planner behavior, route steering, user route choice, visible route UX, retrieval loop, prompt text/version change, public API/frontend/eval runner change, or full AI Evaluation

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_scaffold.py tests/test_attentional_v2_resume.py tests/test_attentional_v2_nodes.py -q`
- Result:
  - `51 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; source-grounded mainline continuity unchanged
- per-op outcome: unchanged and out of Slice 5A
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes; read-audit evidence is not routed into prompts
- reaction_records not semantic memory: unchanged and preserved
- knowledge_activations not source truth: unchanged and preserved
- other: `deferred` remains navigation outcome / audit reason only

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
- Summary: Slice 5A adds compact detour lifecycle and navigation trace audit evidence while preserving existing planning behavior, Navigate act space, durable statuses, prompt text/version, and retrieval behavior.
- Deviations from accepted brief: none
- Known gaps: no retrieval loop, full utilization trace, or full AI Evaluation; detour trace evidence is compact audit metadata and does not claim planning quality

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-16
- Required follow-up: prepare and review Slice 5B Pre-implementation Brief before any Slice 5B implementation

Next recommended step:
- Human reviewer reviews `briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`. Do not start Slice 5B implementation yet.

## Entry 2026-05-16 — Slice 5A report accepted and Slice 5B brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 5

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计2-Planning Ontology Design v0.md`, `../C设计4-Navigation Policy Design v0.md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Prior report: `reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
- Brief: `briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: compact planning support-signal / value-cost markers only; markers are mechanism-private audit / explanation metadata only; no numeric scoring, new planner behavior, new Navigate decisions, durable `deferred`, retrieval loops, prompt text/version changes, route steering, user route choice, visible route UX, public API/frontend/eval runner changes, or full AI Evaluation

Files changed:
- docs only for Slice 5B brief landing

Design contracts addressed:
- Slice 5A Post-implementation Report accepted by human reviewer / user
- Slice 5B brief created for compact planning support-signal and detour value-cost audit markers
- future Slice 5B must keep markers as mechanism-private audit / explanation metadata only
- future Slice 5B must not treat `source_scent`, `detour_value`, or `continuity_cost` as product scores, planning-quality proof, route recommendations, or state-machine authority
- future Slice 5B must preserve Navigate act space: `choose_unit`, `request_skill`, `defer_detour`
- future Slice 5B must preserve durable detour statuses: `open`, `resolved`, `abandoned`
- future Slice 5B must not introduce durable `deferred`, retrieval loops, new planner behavior, prompt text/version changes, route steering, user route choice, visible route UX, public API/frontend/eval runner changes, or full AI Evaluation

Engineering tests:
- Commands run:
  - not run for this doc-only brief landing
- Result:
  - not applicable
- Not run / reason:
  - backend tests not run because no implementation code changed
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: unchanged
- per-op outcome: unchanged and out of Slice 5B brief landing
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: unchanged; Slice 5B brief excludes audit dumps routed into prompts
- reaction_records not semantic memory: unchanged and out of Slice 5B
- knowledge_activations not source truth: unchanged and out of Slice 5B
- other: future Slice 5B must use `not_assessed`, `false`, or omission when support/value/cost evidence is ambiguous

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
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-17
- Required follow-up: implement Slice 5B exactly within the accepted brief, then produce a Post-implementation Report

Next recommended step:
- Human reviewer reviews `reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-17 — Slice 5B implemented and post-report created

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 5

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计2-Planning Ontology Design v0.md`, `../C设计4-Navigation Policy Design v0.md`, `../C设计6-Detour : Look-back : Active Recall Policy Design v0.md`, `../C设计7-Memory Retrieval & Utilization Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Brief: `briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
- Report: `reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: compact planning support-signal / value-cost markers only; markers are mechanism-private audit / explanation metadata only; no numeric scoring, new planner behavior, new Navigate decisions, durable `deferred`, retrieval loops, prompt text/version changes, route steering, user route choice, visible route UX, public API/frontend/eval runner changes, or full AI Evaluation

Files changed:
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

Design contracts addressed:
- compact planning support-signal / value-cost markers added to existing navigation/detour audit evidence only
- markers are symbolic / boolean mechanism-private audit metadata, not product scores or planning-quality proof
- no numeric scoring introduced
- `active_recall_needed` and `look_back_needed` remain audit markers only and do not trigger retrieval
- `budget_stop_reason` is derived only from explicit deterministic budget / defer evidence
- durable detour statuses remain `open`, `resolved`, and `abandoned`
- Navigate act space remains `choose_unit`, `request_skill`, and `defer_detour`
- no new planner behavior, route steering, user route choice, visible route UX, retrieval loop, prompt text/version change, public API/frontend/eval runner change, or full AI Evaluation

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_scaffold.py tests/test_attentional_v2_nodes.py -q`
- Result:
  - `42 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; unchanged
- per-op outcome: unchanged and out of Slice 5B
- candidate vs settled separated: unchanged and deferred to Slice 6
- audit not routed into prompt: yes
- reaction_records not semantic memory: unchanged and preserved
- knowledge_activations not source truth: unchanged and preserved
- other: `local_continuity.detour_trace` remains lifecycle trace state, not a planning score store

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`
- Summary: Slice 5B adds compact mechanism-private planning support markers to existing navigation/detour audit evidence while preserving planner behavior, Navigate act space, durable statuses, prompt text/version, retrieval behavior, source skills, public API/frontend/eval runners, and full AI Evaluation boundaries.
- Deviations from accepted brief: none
- Known gaps: no full retrieval utilization trace, active-recall/look-back loop, planner behavior, or full AI Evaluation

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or patch the Slice 5B Post-implementation Report before any next implementation slice

Next recommended step:
- Human reviewer reviews `reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-17 — Slice 5B report accepted and Slice 6A brief created

Type:
- review decision
- pre-implementation brief

Slice:
- Slice 6

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计8-Slow-cycle : Macro-planning Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Prior report: `reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`
- Brief: `briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
- Accepted by:
- Acceptance date:
- Scope changes approved:

Files changed:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- docs only for Slice 6A brief landing
- Slice 5B Post-implementation Report accepted by human reviewer / user
- future Slice 6A focuses on slow-cycle candidate-vs-settled audit envelope foundations
- future Slice 6A must keep candidates separate from durable truth
- future Slice 6A must treat `withhold` and `not_carried` as valid auditable outcomes, not failures
- future Slice 6A must preserve `reaction_records` as visible trace and `knowledge_activations` as warrant/context, not source truth
- future Slice 6A must not add per-unit reflection, broad slow-cycle behavior expansion, prompt changes by default, public API/frontend/eval runner changes, or full AI Evaluation

Engineering tests:
- Commands run:
  - not run; doc-only brief landing
- Result:
  - not applicable
- Not run / reason:
  - backend tests, benchmark jobs, implementation code, and full AI Evaluation intentionally not run by scope

Contract / audit checks:
- SourceRef preserved: unchanged; future Slice 6A must preserve SourceRef-first behavior and promotion evidence boundaries
- per-op outcome: unchanged and out of Slice 6A brief landing
- candidate vs settled separated: brief created to scope this future audit boundary
- audit not routed into prompt: unchanged; Slice 6A brief excludes audit dumps routed into prompts
- reaction_records not semantic memory: unchanged and explicitly preserved
- knowledge_activations not source truth: unchanged and explicitly preserved
- other: future Slice 6A should use `not_assessed`, omission, or count-only metadata when evidence cannot be derived safely

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
- Slice 5B Post-implementation Report accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-17
- Required follow-up: accept or patch the Slice 6A Pre-implementation Brief before any Slice 6A implementation

Next recommended step:
- Human reviewer reviews `briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`. Do not start Slice 6A implementation yet.

## Entry 2026-05-17 — Slice 6A implemented and post-report created

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 6

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计8-Slow-cycle : Macro-planning Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Brief: `briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
- Report: `reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: compact mechanism-private slow-cycle candidate-vs-settled audit envelope foundations only; no slow-cycle behavior change, prompt text/version change, `runner.py` change, public API/frontend/eval runner change, or full AI Evaluation

Files changed:
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/tests/test_attentional_v2_slow_cycle.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- compact `slow_cycle_audit.jsonl` mechanism-private audit stream added
- slow-cycle candidates and outcomes are visible without treating candidate existence as durable truth
- promotion candidate existence is separated from promotion success
- `withheld` and `not_carried` are valid auditable outcomes, not failures
- optional chapter reactions are marked visible trace, not semantic memory
- knowledge activation operations are marked warrant/context, not source truth
- no full prompt packets, chapter-consolidation payloads, durable stores, source windows, or audit dumps copied into audit rows
- no slow-cycle behavior change, prompt text/version change, `runner.py` change, public API/frontend/eval runner change, or full AI Evaluation

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_slow_cycle.py tests/test_attentional_v2_scaffold.py -q`
- Result:
  - `26 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; carry-forward SourceRef merge/dedupe behavior preserved
- per-op outcome: unchanged and out of Slice 6A
- candidate vs settled separated: yes; slow-cycle audit envelopes distinguish candidate evidence from settled outcome labels
- audit not routed into prompt: yes
- reaction_records not semantic memory: yes; optional chapter reaction audit uses visible-trace boundary
- knowledge_activations not source truth: yes; knowledge operation audit uses warrant/context boundary
- other: `continuation_capsule_delta` omitted to avoid touching `state_projection.py` or copying larger payloads

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: full AI Evaluation remains deferred until core instrumentation is ready

Post-implementation Report:
- Link: `reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
- Summary: Slice 6A adds compact mechanism-private `slow_cycle_audit.jsonl` evidence for existing slow-cycle candidate-vs-settled boundaries while preserving slow-cycle behavior and prompt/runtime/public/eval boundaries.
- Deviations from accepted brief: none
- Known gaps: no full continuation-capsule delta; no full AI Evaluation

Reviewer decision:
- reviewed; implementation direction accepted with required carried SourceRef audit precision patch
- Reviewer: human reviewer / user
- Decision date: 2026-05-17
- Required follow-up: produce and review the Slice 6A carried SourceRef audit precision patch report before any next implementation slice

Next recommended step:
- Human reviewer reviews `reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`. Do not start the next implementation slice yet.

## Entry 2026-05-17 — Slice 6A carried SourceRef audit precision patch

Type:
- implementation patch
- patch report

Slice:
- Slice 6A patch

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计8-Slow-cycle : Macro-planning Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 6A report: `reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
- Patch report: `reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Reviewer decision:
- Slice 6A Post-implementation Report reviewed; implementation direction accepted with a requested carried SourceRef audit precision patch
- Reviewer: human reviewer / user
- Decision date: 2026-05-17

Files changed:
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/tests/test_attentional_v2_slow_cycle.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- carried `cross_chapter_carry_forward` audit envelopes now derive SourceRef evidence from the settled carried item evidence shape
- existing post-cooling active item SourceRefs and carry-forward candidate SourceRefs are combined using `dedupe_source_refs(...)`
- durable carry-forward behavior is unchanged
- audit rows remain compact and do not copy merged refs, full durable stores, source windows, prompt packets, or audit dumps
- ambiguous SourceRef resolution remains `not_assessed`

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_slow_cycle.py tests/test_attentional_v2_scaffold.py -q`
- Result:
  - `26 passed, 6 warnings`
- Not run / reason:
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: yes; `apply_cross_chapter_carry_forward(...)` still preserves existing refs for reused `item_id`
- audit evidence precision: yes; carried audit envelope reports nonzero SourceRef evidence when refs are supplied by the existing settled item shape
- behavior change: none; slow-cycle behavior, prompt text/version, `runner.py`, public API/frontend/eval runner behavior unchanged
- audit not routed into prompt: yes
- next slice: not started

Post-patch Report:
- Link: `reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
- Summary: Slice 6A patch tightens carried SourceRef audit evidence precision for reused active-attention items without changing durable carry-forward behavior.
- Deviations from accepted patch scope: none

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-17
- Required follow-up: prepare Slice 6B closure brief before Slice 7 / Minimal Eval Implementation

Next recommended step:
- Human reviewer reviews `briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`. Do not start Slice 7 yet.

## Entry 2026-05-17 — Slice 6A patch accepted and Slice 6B no-code closure brief created

Type:
- review decision
- pre-implementation brief
- no-code closure recommendation

Slice:
- Slice 6B

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`, `../C设计1-Memory Ontology Design v0.md`, `../C设计3-Memory Formation & Settlement Design v0.md`, `../C设计5-Memory Management & Evolution Design v0(patched).md`, `../C设计8-Slow-cycle : Macro-planning Design v0.md`, `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 6A report: `reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
- Slice 6A patch report: `reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
- Brief: `briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Reviewer decision:
- Slice 6A patch report accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-17

Pre-implementation Brief:
- Link: `briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
- Status: waiting for human review
- Recommendation: no additional Slice 6 runtime implementation; close Slice 6 if accepted and proceed to Slice 7 / Minimal Eval Implementation

Files changed:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Slice 6A plus patch provides enough slow-cycle candidate-vs-settled evidence for minimal eval-readiness
- reconsolidation append-only records and tests are sufficient for now
- continuation / re-entry evidence should be evaluated in Slice 7 from existing artifacts rather than pre-emptively instrumented in Slice 6
- detour continuity remains owned by Slice 5 navigation/detour trace
- no slow-cycle behavior change, prompt text/version change, `runner.py` change, public API/frontend/eval runner change, or full AI Evaluation

Engineering tests:
- Commands run:
  - none; doc-only brief landing
- Not run / reason:
  - backend tests not run because no runtime implementation changed
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: unchanged; Slice 6A patch accepted
- candidate vs settled separated: unchanged and sufficient for minimal eval smoke
- reconsolidation append-only boundary: unchanged and covered by existing tests
- audit not routed into prompt: unchanged
- next slice: not started

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: Slice 7 / Minimal Eval Implementation remains the next planned eval step if this closure brief is accepted

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or revise the Slice 6B no-code closure brief before Slice 7 / Minimal Eval Implementation

Next recommended step:
- Human reviewer reviews `briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`. Do not start Slice 7 yet.

## Entry 2026-05-17 — Slice 6B accepted, Slice 6 closed, and Slice 7A brief created

Type:
- review decision
- pre-implementation brief
- slice closure

Slice:
- Slice 7A

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- Stable eval docs: `docs/backend-reader-evaluation.md`, `reading-companion-backend/docs/evaluation/README.md`, `reading-companion-backend/docs/evaluation/user_level/README.md`, `reading-companion-backend/docs/evaluation/long_span/README.md`
- Slice 6B brief: `briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
- Brief: `briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Reviewer decision:
- Slice 6B no-code closure brief accepted
- Slice 6 closed with no additional runtime implementation
- Reviewer: human reviewer / user
- Decision date: 2026-05-17

Pre-implementation Brief:
- Link: `briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
- Status: waiting for human review
- Recommendation: proceed only after human acceptance with static eval asset inventory and evidence wiring; do not run eval in Slice 7A

Files changed:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Slice 6 is closed after accepted Slice 6B no-code closure brief
- Slice 7 starts with minimal eval asset inventory and evidence wiring, not evaluation redesign
- existing eval lanes are preserved:
  - Lane A: Local / User-level Selective Legibility
  - Lane B: Long Span MQ / Callback / FVI
- planning trace and slow-cycle safety remain lightweight diagnostics only
- contract / audit checks are not product quality scores
- no runtime mechanism behavior, prompt text/version, public API, frontend, eval runner, or mechanism state change
- no full AI Evaluation

Engineering tests:
- Commands run:
  - none; doc-only brief landing
- Not run / reason:
  - backend tests not run because no runtime implementation changed
  - eval runners not run by constraint
  - full AI Evaluation not run by constraint

Contract / audit checks:
- SourceRef preserved: unchanged
- per-op outcome: unchanged; available as Slice 1 / Slice 2 evidence substrate
- candidate vs settled separated: unchanged; Slice 6 closed with existing slow-cycle audit substrate
- audit not routed into prompt: unchanged
- reaction_records not semantic memory: unchanged
- knowledge_activations not source truth: unchanged
- other: retrieval availability, trace existence, audit existence, visible reaction presence, and SourceRef counts are not treated as quality scores

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: none
- Notes: Slice 7A brief defines future static inventory / evidence-wiring implementation only; actual eval smoke remains deferred until a later accepted slice

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or revise the Slice 7A Pre-implementation Brief before any Slice 7A implementation or eval run

Next recommended step:
- Human reviewer reviews `briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`. Do not start eval implementation or run evaluation yet.

## Entry 2026-05-17 — Slice 7A minimal eval asset inventory implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 7A

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- Stable eval docs: `docs/backend-reader-evaluation.md`, `reading-companion-backend/docs/evaluation/README.md`, `reading-companion-backend/docs/evaluation/user_level/README.md`, `reading-companion-backend/docs/evaluation/long_span/README.md`
- Brief: `briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
- Report: `reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: none; implementation stayed static inventory / evidence wiring only

Files changed:
- `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- `reading-companion-backend/docs/evaluation/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Lane A / Local User-level Selective Legibility preserved as active benchmark lane
- Lane B / Long Span MQ / Callback / FVI preserved as diagnostic Phase-1 lane
- Lane A active dataset pointer distinguished from the current formal evidence bundle dataset
- Long Span vNext diagnostic evidence distinguished from formal benchmark authority
- historical / superseded / discontinued assets marked without reactivation
- Slice 1-6 evidence surfaces mapped to eval lanes and diagnostic additions
- Planning Trace Quality and Slow-cycle Safety kept as evidence-availability diagnostics only
- retrieval availability, visible reaction presence, SourceRef counts, trace existence, and `slow_cycle_audit` existence explicitly guarded from quality-score interpretation

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- Result:
  - `6 passed in 0.01s`
  - `docs/tasks/registry.json` parsed successfully
  - `git diff --check` returned no whitespace errors
  - forbidden runtime/frontend/eval-runner diff check returned empty output
- Not run / reason:
  - full AI Evaluation not run by constraint
  - benchmark jobs, judge calls, reading jobs, long-running eval jobs, and broad stale suites not run by constraint

Contract / audit checks:
- SourceRef preserved: unchanged; manifest states SourceRef count is not fidelity score
- per-op outcome: unchanged; manifest maps memory uptake admission / outcome fields as evidence substrate only
- candidate vs settled separated: unchanged; manifest maps `slow_cycle_audit` without treating existence as quality
- audit not routed into prompt: unchanged; no runtime prompt code changed
- reaction_records not semantic memory: unchanged; visible reaction presence is not callback correctness
- knowledge_activations not source truth: unchanged
- other: no runtime mechanism code, eval runner, judge prompt, public API, frontend, durable state, prompt text, or prompt version changed

AI Evaluation:
- Full eval run? no
- Smoke only? no
- Eval lane affected: Lane A and Lane B are inventoried only
- Notes: actual eval smoke remains deferred to a later accepted slice

Post-implementation Report:
- Link: `reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
- Summary: Slice 7A landed a static minimal eval inventory and evidence-wiring manifest plus pure static validation tests.
- Deviations from accepted brief: none
- Known gaps: no eval execution; no eval runner consumption; no Long Span formal-authority promotion

Reviewer decision:
- accepted
- Reviewer: human reviewer / user
- Decision date: 2026-05-17
- Required follow-up: create and review the Slice 7B Pre-implementation Brief before Slice 7B implementation or any eval run

Next recommended step:
- Human reviewer reviews `briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`. Do not start Slice 7B implementation or run eval yet.

## Entry 2026-05-17 — Slice 7B Pre-implementation Brief created

Type:
- review decision / pre-implementation brief

Slice:
- Slice 7B

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 7A report: `reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
- Slice 7B brief: `briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Decision:
- Slice 7A Post-implementation Report accepted by human reviewer / user.
- Slice 7B Pre-implementation Brief created and accepted by human reviewer / user.
- Slice 7B implementation landed as a tiny static smoke harness.

Scope:
- Defines a tiny non-LLM minimal eval smoke harness / validator for the Slice 7A inventory manifest.
- Keeps Slice 7B implementation limited to a read-only smoke script, tests, and optional eval README pointer.
- Does not run full AI Evaluation, benchmark jobs, judge calls, reading jobs, or long-running eval jobs.
- Does not modify runtime mechanism code, eval runners, judge prompts, public API, frontend, or durable mechanism state.

Validation for brief landing:
- planned:
  - parse `docs/tasks/registry.json`
  - `git diff --check`
  - confirm diff is docs-only

Next recommended step:
- Human reviewer reviews `reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`.
- Do not start the next eval slice or run eval until the report is accepted.

## Entry 2026-05-17 — Slice 7B implementation and post-report

Type:
- implementation PR / post-implementation report

Slice:
- Slice 7B

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Brief: `briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
- Report: `reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: none

Files changed:
- `reading-companion-backend/scripts/validate_minimal_eval_inventory_smoke.py`
- `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- `reading-companion-backend/docs/evaluation/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- added stdlib-only smoke validator for the Slice 7A manifest
- validator emits compact JSON summary with lane IDs, evidence surface IDs, tracked path count, local-only counts, and diagnostics
- missing local-only paths are reported, not failed
- required evidence surfaces, interpretation guards, and non-scoring diagnostics are validated
- no eval runner is imported, invoked, or modified
- smoke summary is evidence-availability validation only, not eval result evidence or product-quality score

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q`
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- Result:
  - `8 passed in 0.07s`
  - smoke summary returned `status=ok`, `tracked_path_count=13`, `local_only_present_count=6`, `local_only_missing_count=0`
  - `docs/tasks/registry.json` parsed successfully
  - `git diff --check` returned no whitespace errors
  - forbidden runtime/frontend/eval-runner diff check returned empty output
- Not run / reason:
  - full AI Evaluation not run by constraint
  - benchmark jobs, judge calls, reading jobs, long-running eval jobs, broad stale suites, and eval runners not run by constraint

Contract / audit checks:
- runtime mechanism code unchanged
- eval runners and judge prompts unchanged
- public API/frontend/durable mechanism state unchanged
- no scoring introduced
- Long Span vNext remains diagnostic Phase-1, not formal benchmark authority

Post-implementation Report:
- Link: `reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
- Summary: Slice 7B landed a tiny non-LLM smoke validator plus subprocess tests and status docs.
- Deviations from accepted brief: none
- Known gaps: no actual eval execution; no eval runner consumption of the manifest

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or revise the Slice 7B Post-implementation Report before the next eval slice or any eval run

Next recommended step:
- Human reviewer reviews `reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`.
- Do not start the next eval slice or run eval until this report is accepted.

## Entry 2026-05-17 — Slice 7B report accepted and Slice 8A readiness brief created

Type:
- review decision / pre-implementation brief

Slice:
- Slice 8A

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 7A manifest: `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- Slice 7B report: `reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
- Slice 8A brief: `briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Decision:
- Slice 7B Post-implementation Report accepted by human reviewer / user.
- Slice 8A Pre-implementation Brief created as a readiness-gate brief.

Scope:
- Reviews accepted Slice 1 through Slice 7B evidence.
- Checks readiness of `read_audit`, `settlement_audit`, `supplemental_retrieval`, `navigation_trace`, `detour_trace_evidence`, `slow_cycle_audit`, SourceRef binding/resolution markers, projection markers, and memory uptake admission/outcome fields.
- Preserves Lane A / Local User-level Selective Legibility and Lane B / Long Span MQ Callback FVI.
- Recommends no runtime patch and no eval-runner patch before a later Minimal Eval Suite run brief.
- Does not run full AI Evaluation, benchmark jobs, judge calls, reading jobs, or create eval run directories.

Validation for brief landing:
- planned:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q`
  - parse `docs/tasks/registry.json`
  - `git diff --check`
  - confirm forbidden runtime/frontend/eval-runner diff is empty

Next recommended step:
- Human reviewer reviews `briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`.
- Do not run eval or create a Minimal Eval Suite run until the Slice 8A brief is accepted and a later eval-run brief is created and accepted.

## Entry 2026-05-17 — Slice 8A doc-only readiness gate landed

Type:
- doc-only readiness gate / post-implementation report

Slice:
- Slice 8A

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Brief: `briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
- Report: `reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: none

Files changed:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Slice 1 through Slice 7B accepted evidence inventoried for readiness
- evidence-surface readiness matrix recorded
- Lane A / Local User-level Selective Legibility preserved as active benchmark lane
- Lane B / Long Span MQ Callback FVI preserved as diagnostic phase 1, not formal authority
- no prerequisite runtime patch or eval-runner patch currently indicated
- actual Minimal Eval Suite execution remains blocked until a later eval-run brief is created and accepted

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- Result:
  - smoke summary returned `status=ok`, `tracked_path_count=13`, `local_only_present_count=6`, `local_only_missing_count=0`
  - `8 passed in 0.07s`
  - `docs/tasks/registry.json` parsed successfully
  - `git diff --check` returned no whitespace errors
  - forbidden runtime/frontend/eval-runner diff check returned empty output
- Not run / reason:
  - full AI Evaluation, benchmark jobs, judge calls, reading jobs, eval run directories, broad suites, and eval runners not run by constraint

Contract / audit checks:
- SourceRef preserved: no runtime changes
- per-op outcome: no runtime changes
- candidate vs settled separated: no runtime changes
- audit not routed into prompt: no prompt changes
- reaction_records not semantic memory: no runtime changes
- knowledge_activations not source truth: no runtime changes
- other: instrumentation availability is not product quality; retrieval availability is not utilization success; visible reaction presence is not callback correctness; SourceRef count is not fidelity score; trace existence is not planning quality; `slow_cycle_audit` existence is not slow-cycle quality

AI Evaluation:
- Full eval run? no
- Smoke only? static manifest smoke only; no eval execution
- Eval lane affected: Lane A and Lane B readiness documentation only
- Notes: no benchmark jobs, judge calls, reading jobs, eval run directories, scoring, or formal-authority promotion

Post-implementation Report:
- Link: `reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
- Summary: Slice 8A readiness gate landed as doc-only status/report update.
- Deviations from accepted brief: none
- Known gaps: no actual Minimal Eval Suite run; later eval-run brief still required before execution

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or revise the Slice 8A Post-implementation Report before any Minimal Eval Suite run brief or eval execution

Next recommended step:
- Human reviewer reviews `reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`.
- Do not start the Minimal Eval Suite, create eval run directories, run benchmark jobs, call judges, launch reading jobs, or create the next eval-run brief until this report is accepted and the user explicitly requests the later run brief.

## Entry 2026-05-17 — Slice 8A report accepted and Slice 8B run brief created

Type:
- review decision / pre-implementation brief

Slice:
- Slice 8B

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 8A report: `reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
- Slice 8B brief: `briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Decision:
- Slice 8A Post-implementation Report accepted by human reviewer / user.
- Slice 8B Pre-implementation Brief created as a doc-only run brief and execution guardrail package.

Scope:
- Defines a future bounded Minimal Eval Suite run profile without executing it.
- Preserves Lane A / Local User-level Selective Legibility and Lane B / Long Span MQ Callback FVI.
- Keeps Planning Trace Quality and Slow-cycle Safety as diagnostic evidence-availability checks only.
- Keeps actual eval execution blocked until a later separately accepted execution slice.
- Does not change runtime mechanism code, prompts, eval runners, judge prompts, public API, frontend, durable mechanism state, schemas, or metric taxonomy.
- Does not run full AI Evaluation, benchmark jobs, judge calls, reading jobs, or create eval run directories.

Validation for brief landing:
- planned:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q`
  - parse `docs/tasks/registry.json`
  - `git diff --check`
  - confirm forbidden runtime/frontend/eval-runner diff is empty

Next recommended step:
- Human reviewer reviews `briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`.
- Do not start the Minimal Eval Suite, create eval run directories, run benchmark jobs, call judges, launch reading jobs, or start a later execution slice until this brief is accepted and that later execution slice is explicitly requested and accepted.

## Entry 2026-05-17 — Slice 8B brief accepted and Slice 8C execution brief created

Type:
- review decision / pre-implementation brief

Slice:
- Slice 8C

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 8A report: `reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
- Slice 8B brief: `briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
- Slice 8C brief: `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Decision:
- Slice 8B Pre-implementation Brief accepted by human reviewer / user.
- Slice 8C Pre-implementation Brief created as a doc-only execution-slice brief.

Scope:
- Defines exact future preflight checks, run ids, commands, background-job policy, expected outputs, cost posture, evidence-catalog policy, acceptance checks, and rollback rules.
- Future bounded execution includes both lanes:
  - Lane A: fresh `attentional_v2`-only Local / User-level Selective Legibility smoke on one segment and three note cases.
  - Lane B: `attentional_v2`-only Long Span MQ / Callback / FVI smoke using existing semantic-probe source outputs, fresh Memory Quality rejudge, copied reaction audit, and no reading jobs.
- Keeps actual eval execution blocked until Slice 8C is accepted and execution is explicitly requested.
- Does not change runtime mechanism code, prompts, eval runners, judge prompts, public API, frontend, durable mechanism state, schemas, evidence catalog, or metric taxonomy.
- Does not run full AI Evaluation, benchmark jobs, judge calls, reading jobs, or create eval run directories.

Validation for brief landing:
- planned:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q`
  - parse `docs/tasks/registry.json`
  - `git diff --check`
  - confirm forbidden runtime/frontend/eval-runner diff is empty

Next recommended step:
- Human reviewer reviews `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`.
- Do not start the Minimal Eval Suite, create eval run directories, run benchmark jobs, call judges, launch reading jobs, modify eval runners, or update the evidence catalog until this brief is accepted and execution is explicitly requested.

## Entry 2026-05-17 — Slice 8C bounded eval execution attempted and report created

Type:
- eval smoke / post-implementation report

Slice:
- Slice 8C

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 8B brief: `briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
- Slice 8C brief: `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
- Slice 8C report: `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: execute bounded two-lane plan sequentially, with Lane B blocked unless Lane A reaches terminal success

Files changed:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- Static preflight checks ran before execution.
- Lane A used `attentional_v2` only, one `huochu` segment, and three note cases.
- Lane B was not launched because Lane A failed.
- Evidence catalog was not updated.
- Runtime mechanism code, eval runners, judge prompts, frontend, public API, and durable mechanism state were not modified.

Engineering tests / checks:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q`
  - `cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - forbidden runtime/frontend/eval-runner diff check
  - target run-directory absence checks
  - Lane B source-run metadata check
- Result:
  - manifest smoke returned `status=ok`
  - static inventory pytest returned `8 passed in 0.07s`
  - registry had no active jobs before launch
  - `docs/tasks/registry.json` parsed successfully
  - `git diff --check` passed before execution
  - forbidden runtime/frontend/eval-runner diff check returned empty output
  - Lane B source metadata matched `probe_plan_id=memory_quality_semantic_probe_plan_20260504` and `probe_selection_method=semantic_boundary_with_distance_reference`
- Not run / reason:
  - Lane B not run because Lane A failed
  - full AI Evaluation, broad benchmark jobs, cross-mechanism comparison, evidence-catalog updates, eval-runner changes, and retries not run by constraint

Execution result:
- Lane A job id: `bgjob_minimal_eval_suite_lane_a_smoke_20260517`
- Lane A run id: `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517`
- Lane A registry status: `failed`
- Lane A exit code: `1`
- Lane A failure: user-level selective matching raised `ValueError` because visible reaction `rx:Full_Content:src:c1:p1@0-p3@146:highlight:1` had no usable source locator.
- Lane A partial evidence: fresh V2 read completed one chapter, emitted `152` visible reactions, and wrote runtime `activity.jsonl` plus `llm_standard.jsonl`.
- Lane A missing expected outputs: `summary/aggregate.json`, `summary/report.md`, and `summary/llm_usage.json`.
- Lane B job id: `bgjob_minimal_eval_suite_lane_b_smoke_20260517`
- Lane B status: not launched; run directory not created.

Contract / audit checks:
- SourceRef preserved: no runtime changes
- per-op outcome: no runtime changes
- candidate vs settled separated: no runtime changes
- audit not routed into prompt: no prompt changes
- reaction_records not semantic memory: no runtime changes
- knowledge_activations not source truth: no runtime changes
- other: audit existence is not product quality; retrieval availability is not utilization success; visible reaction presence is not callback correctness; SourceRef count is not fidelity score; trace existence is not planning quality; `slow_cycle_audit` existence is not slow-cycle quality

AI Evaluation:
- Full eval run? no
- Smoke only? attempted bounded Lane A smoke; failed before eval summary generation
- Eval lane affected: Lane A attempted; Lane B not launched
- Notes: this is diagnostic execution evidence only, not product-quality proof

Post-implementation Report:
- Link: `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
- Summary: Slice 8C preflight passed, Lane A launched and failed after fresh V2 read completion due source-locator compatibility in user-level selective matching, Lane B was not launched, and partial outputs/logs were preserved.
- Deviations from accepted brief: none; failure policy followed
- Known gaps: no Lane A aggregate summary, no Lane B smoke evidence, no product-quality claim

Reviewer decision:
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: decide whether to patch the source-locator compatibility seam, adjust the run profile, or authorize a `_retry1` run

Next recommended step:
- Human reviewer reviews `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`.
- Do not retry Lane A, launch Lane B, start another eval slice, modify eval runners, or update the evidence catalog until the report is reviewed and a next action is explicitly accepted.

## Entry 2026-05-17 — Slice 8D Lane A source-locator compatibility patch implemented

Type:
- implementation PR
- post-implementation report

Slice:
- Slice 8D

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1: `E实施1-Implementation Feasibility & Delta Audit v0.md`
- Slice 8C report: `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
- Slice 8D report: `reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: user-accepted Slice 8D triage / patch plan in chat
- Accepted by: human reviewer / user
- Acceptance date: 2026-05-17
- Scope changes approved: patch Lane A source-locator compatibility only; no eval retry, no Lane B launch, no evidence-catalog update, no runtime mechanism change

Files changed:
- `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- `reading-companion-backend/tests/test_run_user_level_selective_comparison.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Design contracts addressed:
- uses structured `primary_source_ref.source_span` as Lane A source-locator compatibility fallback when `target_locator` is absent
- preserves locator precedence and strict source-span overlap matching
- skips truly unlocatable reactions as compact diagnostics rather than converting them into matches
- does not parse `reaction_id` as the primary locator solution
- does not change normalized export, runtime mechanism code, prompts, judge prompts, evidence catalog, Long Span runner, frontend, public API, or durable mechanism state

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_run_user_level_selective_comparison.py -q`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - forbidden runtime/frontend/Long Span/evidence-catalog diff check
- Result:
  - targeted pytest passed: `14 passed, 6 warnings`
  - `docs/tasks/registry.json` parsed successfully
  - `git diff --check` passed
  - forbidden runtime/frontend/Long Span/evidence-catalog diff check returned empty output
- Not run / reason:
  - no Lane A retry, no Lane B launch, no judges, no reading jobs, no full AI Evaluation, no benchmark jobs, and no new eval run directories by constraint

Contract / audit checks:
- SourceRef preserved: yes; patch uses existing structured SourceRef evidence
- per-op outcome: no runtime changes
- candidate vs settled separated: no runtime changes
- audit not routed into prompt: no prompt changes
- reaction_records not semantic memory: no runtime memory behavior changed
- knowledge_activations not source truth: no knowledge activation behavior changed
- other: unlocatable locator diagnostics are not product scores or matches

AI Evaluation:
- Full eval run? no
- Smoke only? no new smoke run; this patch only repairs the Lane A source-locator compatibility seam exposed by Slice 8C
- Eval lane affected: Lane A runner compatibility only
- Notes: Slice 8C remains failed execution evidence; any retry requires a later accepted execution slice with a new `_retry1` run id

Post-implementation Report:
- Link: `reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
- Summary: Lane A user-level selective runner now falls back to `primary_source_ref.source_span` when `target_locator` is absent and reports truly unlocatable reactions as diagnostics.
- Deviations from accepted brief: none
- Known gaps: no Lane A retry, no Lane B smoke evidence, no product-quality claim

Reviewer decision:
- accepted
- Reviewer: user
- Decision date: 2026-05-17
- Required follow-up: Lane A `_retry1` and Lane B bounded diagnostic smoke are accepted; Slice 8G closure report is pending review

Next recommended step:
- Continue with `reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md` review.
- Do not update the evidence catalog, promote Long Span vNext to formal benchmark authority, run broader eval, or start another eval slice until the Slice 8G report is accepted and a next action is explicitly approved.

## Entry 2026-05-17 — Slice 8E Lane A `_retry1` bounded execution

Type:
- eval smoke / post-run report

Slice:
- Slice 8

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report:
  - `E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
  - `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
  - `reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
  - `reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
- Accepted by: user
- Acceptance date: 2026-05-17
- Scope changes approved:
  - Slice 8D report accepted
  - run Lane A only as `_retry1`
  - do not launch Lane B
  - do not update evidence catalog
  - do not modify runtime code, eval runners, judge prompts, frontend, public API, or durable state

Files changed:
- `reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
- `../README.md`
- `E实施-progress-ledger.md`
- `../../../../current-state.md`
- `../../../../tasks/registry.md`
- `../../../../tasks/registry.json`

Execution:
- Job id: `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1`
- Run id: `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1`
- Run directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1`
- Job status: `completed`
- Exit code: `0`
- Started: `2026-05-17T09:22:31.719758Z`
- Ended: `2026-05-17T11:07:31.654879Z`

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py tests/test_run_user_level_selective_comparison.py -q`
  - `cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json`
- Result:
  - manifest smoke passed
  - focused tests passed: `22 passed, 6 warnings in 0.38s`
  - pre-launch background-job registry showed no active jobs
  - registry JSON parse passed
  - diff check passed
  - forbidden diff check was empty

Contract / audit checks:
- SourceRef preserved: no runtime SourceRef behavior changed
- per-op outcome: no runtime op behavior changed
- candidate vs settled separated: no runtime behavior changed
- audit not routed into prompt: no prompt changes
- reaction_records not semantic memory: no runtime memory behavior changed
- knowledge_activations not source truth: no slow-cycle behavior changed
- other:
  - Lane A `_retry1` used only `attentional_v2`, one segment, and three note cases
  - aggregate checks passed: `segment_count=1`, `note_case_count=3`, mechanisms `["attentional_v2"]`
  - unlocatable diagnostic remained diagnostic-only and was not counted as a match

AI Evaluation:
- Full eval run? no
- Smoke only? yes, Lane A bounded `_retry1` only
- Eval lane affected: Lane A / Local User-level Selective Legibility
- Notes:
  - no Lane B launch
  - no cross-mechanism comparison
  - no evidence catalog update
  - fresh reading job occurred
  - runner launched with `--judge-mode llm`, but the three produced note-case results resolved through deterministic exact-span or no-overlap paths; no shortlisted non-exact candidate required the LLM judge path
  - runtime LLM usage: `213` requests, `213` successes, `0` errors, `12` retries

Post-implementation Report:
- Link: `reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
- Summary: Lane A `_retry1` completed successfully after Slice 8D source-locator compatibility patch; outputs and aggregate checks are present.
- Deviations from accepted brief: none
- Known gaps:
  - no Lane B smoke run yet
  - no product-quality claim
  - no evidence catalog entry

Reviewer decision:
- accepted
- Reviewer: user
- Decision date: 2026-05-17
- Required follow-up: Lane B bounded diagnostic smoke is accepted; Slice 8G closure report is pending review before any evidence-catalog update, formal-authority promotion, broader eval, or next eval slice

Next recommended step:
- Continue with `reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md` review.
- Do not update the evidence catalog, promote Long Span vNext to formal benchmark authority, run broader eval, or start another eval slice until the Slice 8G report is accepted and a next action is explicitly approved.

## Entry 2026-05-17 — Slice 8F Lane B bounded diagnostic smoke

Type:
- eval smoke / post-run report

Slice:
- Slice 8

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report:
  - `E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
  - `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
  - `reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
  - `reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
- Accepted by: user
- Acceptance date: 2026-05-17
- Scope changes approved:
  - Slice 8E report accepted
  - run Lane B only as a bounded diagnostic smoke
  - do not launch another Lane A run
  - do not update evidence catalog
  - do not modify runtime code, eval runners, judge prompts, frontend, public API, or durable state
  - do not promote Long Span vNext to formal benchmark authority

Files changed:
- `reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
- `../README.md`
- `E实施-progress-ledger.md`
- `../../../../current-state.md`
- `../../../../tasks/registry.md`
- `../../../../tasks/registry.json`

Execution:
- Job id: `bgjob_minimal_eval_suite_lane_b_smoke_20260517`
- Run id: `attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`
- Run directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`
- Job status: `completed`
- Exit code: `0`
- Started: `2026-05-17T11:39:24.773270Z`
- Ended: `2026-05-17T11:40:54.920938Z`

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py tests/test_run_user_level_selective_comparison.py -q`
  - `cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json`
- Result:
  - manifest smoke passed
  - focused tests passed: `22 passed, 6 warnings in 0.31s`
  - pre-launch background-job registry showed no active jobs
  - registry JSON parse passed
  - diff check passed
  - forbidden diff check was empty

Contract / audit checks:
- SourceRef preserved: no runtime SourceRef behavior changed
- per-op outcome: no runtime op behavior changed
- candidate vs settled separated: no runtime behavior changed
- audit not routed into prompt: no prompt changes
- reaction_records not semantic memory: no runtime memory behavior changed
- knowledge_activations not source truth: no slow-cycle behavior changed
- other:
  - Lane B used only `attentional_v2`, one selected Memory Quality window, reused source outputs, and `--judge-mode llm`
  - aggregate checks passed: `mechanism_keys=["attentional_v2"]`, `probe_plan_id=memory_quality_semantic_probe_plan_20260504`, `probe_selection_method=semantic_boundary_with_distance_reference`, `memory_quality.window_count=1`, `memory_quality.probe_count=5`, `memory_quality_source=fresh_judge`, `reaction_audit_source=copied_from_memory_quality_source_run`
  - `meta/output_sourcing.json.fresh_task_count=0`, so no reading jobs were launched
  - copied reaction audit contains the full source run's five reaction windows, while fresh Memory Quality rejudge covers one selected window; this is recorded as a diagnostic observation, not a product-quality claim

AI Evaluation:
- Full eval run? no
- Smoke only? yes, Lane B bounded diagnostic smoke only
- Eval lane affected: Lane B / Long Span MQ / Callback / FVI diagnostic phase 1
- Notes:
  - no Lane A launch
  - no cross-mechanism comparison
  - no evidence catalog update
  - no reading jobs
  - `5` fresh Memory Quality judge calls
  - no fresh reaction-audit judge calls
  - LLM usage: `5` requests, `5` successes, `0` errors, `0` retries

Post-implementation Report:
- Link: `reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
- Summary: Lane B bounded diagnostic smoke completed successfully; outputs and aggregate checks are present.
- Deviations from accepted brief:
  - `reaction_window_summaries.jsonl` contains `5` copied source-run rows rather than only one target-window row because reaction audit was copied unchanged from the source run.
- Known gaps:
  - no product-quality claim
  - no evidence catalog entry
  - Long Span vNext remains diagnostic phase 1, not formal authority

Reviewer decision:
- accepted
- Reviewer: user
- Decision date: 2026-05-17
- Required follow-up: Slice 8G closure and evidence interpretation report landed; review the Slice 8G report before any evidence-catalog update, formal-authority promotion, broader eval, or next eval slice

Next recommended step:
- Continue with `reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md` review.
- Do not update the evidence catalog, promote Long Span vNext to formal benchmark authority, run broader eval, or start another eval slice until the Slice 8G report is accepted and a next action is explicitly approved.

## Entry 2026-05-17 — Slice 8G Minimal Eval Suite smoke closure and evidence interpretation

Type:
- doc-only closure report
- evidence interpretation report

Slice:
- Slice 8

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report:
  - `E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
  - `reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
  - `reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
  - `reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
  - `reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
- Accepted by: user
- Acceptance date: 2026-05-17
- Scope changes approved:
  - Slice 8F report accepted
  - land doc-only closure and evidence interpretation
  - do not run more eval
  - do not update evidence catalog
  - do not modify runtime code, eval runners, judge prompts, frontend, public API, or durable state
  - do not promote Long Span vNext to formal benchmark authority
  - do not claim product-quality proof

Files changed:
- `reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`
- `../README.md`
- `E实施-progress-ledger.md`
- `../../../../current-state.md`
- `../../../../tasks/registry.md`
- `../../../../tasks/registry.json`

Design contracts addressed:
- closes Slice 8C through Slice 8F as bounded diagnostic smoke evidence
- preserves Lane A / Lane B interpretation boundaries
- keeps Long Span vNext diagnostic-only
- records that Lane B copied reaction audit is broader than the selected Memory Quality window
- does not claim product-quality proof from smoke outputs

Engineering tests:
- Commands run:
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json`
- Result:
  - passed; forbidden diff check returned empty output
- Not run / reason:
  - no eval, no benchmark jobs, no judge calls, no reading jobs, and no eval run directories by constraint

Contract / audit checks:
- SourceRef preserved: no runtime SourceRef behavior changed
- per-op outcome: no runtime op behavior changed
- candidate vs settled separated: no runtime behavior changed
- audit not routed into prompt: no prompt changes
- reaction_records not semantic memory: no runtime memory behavior changed
- knowledge_activations not source truth: no slow-cycle behavior changed
- other:
  - no evidence catalog update
  - no formal benchmark authority promotion
  - no new metric taxonomy

AI Evaluation:
- Full eval run? no
- Smoke only? no new smoke run in Slice 8G; this is interpretation of already completed Slice 8C through Slice 8F evidence
- Eval lane affected: Lane A and Lane B interpretation only
- Notes:
  - Minimal Eval Suite smoke is recorded as completed after Lane A retry
  - evidence remains diagnostic and not product-quality proof

Post-implementation Report:
- Link: `reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`
- Summary: Closure report interprets Slice 8C failed Lane A attempt, Slice 8D source-locator patch, Slice 8E Lane A retry success, and Slice 8F Lane B diagnostic smoke success.
- Deviations from accepted brief: none
- Known gaps:
  - no evidence catalog entry
  - no formal benchmark promotion
  - no broader eval
  - optional future brief may clarify Lane B copied reaction-audit filtering/reporting semantics

Reviewer decision:
- accepted
- Reviewer: user
- Decision date: 2026-05-17
- Required follow-up: Slice 8H diagnostic evidence catalog entry brief created; do not update the evidence catalog until the Slice 8H brief is accepted

Next recommended step:
- Human reviewer reviews `briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`.
- If accepted, add one diagnostic smoke entry to the evidence catalog with strong caveats; do not run eval or promote Long Span vNext.

## Entry 2026-05-17 — Slice 8H diagnostic evidence catalog entry brief

Type:
- pre-implementation brief
- cataloging brief
- catalog-only implementation
- post-implementation report

Slice:
- Slice 8

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- C设计 source: `../C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- E实施1 / PR / report:
  - `E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
  - `reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
  - `reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
  - `reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
  - `reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`
  - `briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`

Branch / PR:
- Branch: `main`
- PR:
- Commit:

Pre-implementation Brief:
- Link: `briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`
- Accepted by: user
- Acceptance date: 2026-05-17
- Scope changes approved:
  - Slice 8G closure report accepted
  - prepare a doc-only cataloging brief
  - do not update the evidence catalog yet
  - do not run eval, create eval run directories, modify runtime code, modify eval runners, modify judge prompts, or promote Long Span vNext

Files changed:
- `briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`
- `reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.json`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/scripts/update_evaluation_catalog.py`
- `../README.md`
- `E实施-progress-ledger.md`
- `../../../../current-state.md`
- `../../../../tasks/registry.md`
- `../../../../tasks/registry.json`

Design contracts addressed:
- adds one diagnostic smoke evidence catalog entry for the Slice 8C through Slice 8G sequence
- adds `diagnostic_smoke` as a catalog status label, with `not_formal_authority` and `not_product_quality_proof` preserved as caveats
- keeps `FORMAL_STATUSES` unchanged, so `diagnostic_smoke` is not formal authority
- keeps Long Span vNext diagnostic-only, not formal benchmark authority

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_catalog.py --check`
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- Result:
  - passed; forbidden runtime/frontend/eval-runner diff check returned empty output
- Not run / reason:
  - no eval, benchmark jobs, judge calls, reading jobs, or eval run directories by constraint

Contract / audit checks:
- SourceRef preserved: no runtime SourceRef behavior changed
- per-op outcome: no runtime op behavior changed
- candidate vs settled separated: no runtime behavior changed
- audit not routed into prompt: no prompt changes
- reaction_records not semantic memory: no runtime memory behavior changed
- knowledge_activations not source truth: no slow-cycle behavior changed
- other:
  - evidence catalog updated with one diagnostic smoke entry only
  - no formal benchmark authority promotion
  - no new metric taxonomy

AI Evaluation:
- Full eval run? no
- Smoke only? no new smoke run in Slice 8H; existing Slice 8C through Slice 8G smoke sequence was cataloged
- Eval lane affected: Lane A and Lane B cataloging recommendation only
- Notes:
  - Slice 8H catalogs completed smoke evidence as diagnostic only
  - the catalog entry must not be read as product-quality proof

Post-implementation Report:
- Link: `reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`
- Summary: Adds one `diagnostic_smoke` evidence catalog entry for the completed Slice 8C through Slice 8G Minimal Eval Suite smoke sequence and updates catalog tooling so validation accepts the non-formal status.
- Deviations from accepted brief: none
- Known gaps:
  - diagnostic catalog entry does not prove product quality
  - broader eval and Long Span formal-authority promotion remain blocked pending later human approval

Reviewer decision:
- accepted
- Reviewer: user
- Decision date: 2026-05-18
- Required follow-up: none for this implementation track; future broader eval, formal-authority promotion, runtime patches, further catalog entries, or product-quality claims require a separate future brief

Next recommended step:
- Memory / Planning / Minimal Eval implementation track is closed after Slice 8H.
- Do not run eval, broaden benchmark authority, add more catalog entries, patch runtime, or claim product quality without a later accepted brief.

## Entry 2026-05-18 — Final status-only closure after Slice 8H

Type:
- status-only closure update

Slice:
- Slice 8H final closure

Related docs:
- E实施0: `../E实施0-Implementation Roadmap & Handoff v0.md`
- E实施1 / reports:
  - `E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`

Decision:
- Slice 8H diagnostic catalog entry is accepted.
- `attentional_v2_minimal_eval_suite_smoke_20260517` remains cataloged as `diagnostic_smoke` only.
- The completed Slice 8C through Slice 8G Minimal Eval Suite smoke is diagnostic evidence only, not formal benchmark authority, not Long Span vNext promotion, and not product-quality proof.
- The Memory / Planning / Minimal Eval implementation track is closed after Slice 8H.

Files changed:
- `../README.md`
- `E实施-progress-ledger.md`
- `../../../../current-state.md`
- `../../../../tasks/registry.md`
- `../../../../tasks/registry.json`

Validation:
- Commands to run:
  - `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"`
  - `git diff --check`
  - `git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json`

Explicit non-actions:
- no eval run
- no eval run directories created
- no evidence catalog files changed
- no runtime mechanism code changed
- no eval runners, judge prompts, frontend, public API, or durable mechanism state changed
- no Long Span vNext formal-authority promotion
- no product-quality claim

Required follow-up:
- none for this implementation track
- any broader eval, formal-authority promotion, runtime patch, further catalog entry, or product-quality claim requires a separate future brief

## Entry 2026-05-19 — Post-Slice8H Eval-1 broader evaluation attempt stopped

Type:
- aborted broader-eval operation record

Slice:
- post-Slice8H Eval-1

Related docs:
- Report: `reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Aborted-Run-Report v0.md`
- Current state: `../../../../current-state.md`
- Task registry: `../../../../tasks/registry.md`, `../../../../tasks/registry.json`

Decision:
- Stop the current Eval-1 background work before launching any additional shards.
- Preserve existing logs and partial run directories.
- Treat all partial Eval-1 outputs from this attempt as invalid for evaluation interpretation and invalid as Lane A reuse sources.

Jobs:
- `bgjob_full_user_level_selective_post_slice8h_20260518`: `abandoned`, exit `-15`.
- `bgjob_full_long_span_vnext_post_slice8h_20260518`: `abandoned`, exit `-15`.
- `bgjob_full_long_span_vnext_post_slice8h_20260518_parallel5`: `abandoned`, exit `-15`.
- latest registry refresh after stop: no active jobs.

Key evidence:
- Optimized Long Span producer run dir:
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5`
- The optimized producer created `meta/selected_windows.json` but did not create:
  - `summary/aggregate.json`
  - `summary/report.md`
  - `summary/llm_usage.json`
- Local LLM trace inspection for the optimized producer found `919` rows: `465` successful and `454` error rows.
- Error breakdown: `network_blocked=334`, `llm_timeout=120`.
- In the recent five-hour window from the final completed trace, `90 / 90` rows were `llm_timeout`.
- Runtime activity contained LLM fallback events, so paragraph-position progress was not reliable model-backed evaluation progress.

Explicit non-actions:
- no new eval run launched after stop
- no Lane A reuse shard launched
- no evidence catalog update
- no runtime mechanism code change
- no eval runner change
- no judge-prompt change
- no frontend, public API, or durable mechanism state change
- no new metrics or scoring
- no Long Span vNext formal-authority promotion
- no product-quality claim

Required follow-up:
- before retrying Eval-1, prepare a separate accepted brief or patch plan for LLM-health / fallback guardrails and fresh run ids
- do not reuse `attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5` as the Lane A source-output producer
- do not treat any partial output from the stopped jobs as product-quality proof or formal benchmark authority

## Entry 2026-05-19 — Eval-1 LLM health / eval strictness repair landed

Type:
- implementation PR / post-implementation report

Slice:
- Post-Slice8H Eval-1 repair

Related docs:
- abort evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Aborted-Run-Report v0.md`
- repair report:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-LLM-Health-and-Eval-Strictness-Repair-Post-implementation-Report v0.md`

Files changed:
- `reading-companion-backend/src/reading_runtime/llm_gateway.py`
- `reading-companion-backend/eval/attentional_v2/llm_health.py`
- `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- `reading-companion-backend/scripts/check_llm_targets_live.py`
- `reading-companion-backend/scripts/check_eval_llm_health.py`
- `reading-companion-backend/tests/test_llm_health.py`
- `reading-companion-backend/tests/test_llm_gateway.py`
- status / evaluation docs

Implementation summary:
- Added strict eval LLM-health validation for active `attentional_v2` eval reading outputs.
- Active user-level and Long Span eval runners now reject fallback-backed or all-failed LLM output before judge/reuse.
- Shared gateway now supports same-tier failover for non-manual `network_blocked` / `llm_timeout` provider failures.
- Added a live target preflight script and an output/run health checker.
- Product runtime fallback remains allowed, but fallback-backed outputs are explicit diagnostics and not eval evidence.

Engineering tests:
- Commands run:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_llm_health.py tests/test_llm_gateway.py::test_same_tier_failover_tries_second_target_after_timeout tests/test_run_user_level_selective_comparison.py tests/test_long_span_vnext.py -q`
- Result:
  - `39 passed`

AI Evaluation:
- Full eval run? no
- Eval retry launched? no
- Eval lane affected:
  - Lane A / active user-level selective runner health gate
  - Lane B / active Long Span vNext runner health gate
- Notes:
  - no evidence catalog update
  - no product-quality claim
  - no Long Span formal-authority promotion

Post-implementation Report:
- Link:
  - `codex/reports/Eval1-LLM-Health-and-Eval-Strictness-Repair-Post-implementation-Report v0.md`
- Summary:
  - repaired the Eval-1 LLM health guardrail gap and shared target-failover weakness exposed by the aborted optimized producer
- Known gaps:
  - no Eval-1 retry has been launched
  - future retry must use fresh run ids and explicit human approval

Reviewer decision:
- pending human review

Next recommended step:
- human review of the repair report before any broader Eval-1 retry

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
