# E实施 Progress Ledger

## Purpose

This is the progress ledger for the Second Reader Memory / Planning optimization implementation track.

Use it to record `E实施1`, each implementation PR, each pre-implementation brief, each post-implementation report, contract gates, test results, review decisions, and next steps.

This ledger is not stable product behavior authority. It does not replace `docs/current-state.md`, `docs/tasks/registry.md`, `docs/tasks/registry.json`, or `docs/history/decision-log.md`.

Stable mechanism behavior changes still need to be promoted to the relevant stable docs when implementation lands and is accepted.

## Current Status

```text
Current phase: Slice 1 implementation complete; Post-implementation Report waiting for human review
Implementation status: Slice 1 additive contract / audit scaffolding implemented
Next action: human reviewer accepts the Slice 1 Post-implementation Report or requests a patch before any Slice 2 brief / implementation PR
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
- waiting for human review
- Reviewer:
- Decision date:
- Required follow-up: accept or patch the Slice 1 Post-implementation Report before any Slice 2 brief or implementation PR

Next recommended step:
- Human reviewer accepts `reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md` or requests a patch. Do not start Slice 2 yet.

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
