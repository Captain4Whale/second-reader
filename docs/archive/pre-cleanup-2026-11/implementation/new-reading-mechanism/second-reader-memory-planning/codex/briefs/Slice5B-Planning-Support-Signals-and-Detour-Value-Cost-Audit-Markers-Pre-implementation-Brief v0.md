# Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0

## PR title

Slice 5B: Planning Support Signals and Detour Value-Cost Audit Markers

## Implementation slice

Slice 5B is a small reversible sub-slice of Slice 5 / Planning Trace, Detour, Recall, and Look-back Hardening.

The focus is compact planning support-signal and value-cost audit markers for the existing detour and navigation trace surfaces, not new planning behavior.

## Design sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计2-Planning Ontology Design v0.md`
- `C设计4-Navigation Policy Design v0.md`
- `C设计6-Detour : Look-back : Active Recall Policy Design v0.md`
- `C设计7-Memory Retrieval & Utilization Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `codex/briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
- `codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
- `codex/E实施-progress-ledger.md`

## Current code facts

- `Read` can emit optional `detour_need`.
- `schemas.py` defines `DetourNeed`, `DetourTraceEntry`, `NavigateActResult`, and `NavigateActTraceEntry`.
- Slice 5A added optional detour lifecycle reason fields to `DetourTraceEntry` and compact `navigation_trace` / `detour_trace_evidence` blocks to `read_audit.jsonl`.
- `runner.py` owns detour application, active-detour lookup, the Navigate act loop, compact navigation trace packaging, compact detour trace evidence, and source skill request/result summaries.
- `_apply_detour_need(...)` still supports durable detour statuses only as `open`, `resolved`, and `abandoned`.
- `nodes.py` bounds Navigate decisions to `choose_unit`, `request_skill`, and `defer_detour`.
- `read_context.py` already preserves `look_back = source_calibration` and `active_recall = memory_recovery` metadata from Slice 4A.
- Slice 5B must not create active-recall, look-back, supplemental retrieval, planner, or route-steering loops.

## Files to change

Future implementation PR may change:

- `reading-companion-backend/src/attentional_v2/schemas.py`, for optional trace/audit `TypedDict` fields only.
- `reading-companion-backend/src/attentional_v2/runner.py`, for helper-level marker derivation and compact trace packaging only.
- `reading-companion-backend/src/attentional_v2/observability.py`, for compact `read_audit` persistence only.
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- Optionally `reading-companion-backend/tests/test_attentional_v2_nodes.py`, only to lock unchanged Navigate act space.

## Files explicitly not changing

- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/skills/source_skills.py`
- durable memory stores
- public API
- frontend
- eval runners

No prompt text or prompt version change is in scope.

## Planned deltas

- Add compact optional audit markers where existing planning evidence is otherwise hard to inspect:
  - `source_scent`
  - `detour_value`
  - `continuity_cost`
  - `active_recall_needed`
  - `look_back_needed`
  - `support_signal_reason`
  - `budget_stop_reason`
- Derive markers only from already-available evidence:
  - `Read.detour_need` reason and target hint
  - Navigate act reason
  - source skill request/result summaries
  - budget state
  - defer reason
  - existing navigation trace and detour trace evidence
- Add marker fields to compact trace/audit evidence only when relevant.
- Preserve existing `DetourTraceEntry`, `NavigateActTraceEntry`, `navigation_trace`, and `detour_trace_evidence` fields.
- Do not use markers to choose units, alter detour lifecycle, alter source-skill behavior, or change prompt content.
- Do not write full prompt packets, source-skill payload dumps, route traces, or audit dumps into prompts.

## Marker policy

These markers are mechanism-private audit and explanation metadata only.

They are not:

- product scores;
- planning-quality proof;
- state-machine authority;
- route recommendations;
- route steering;
- user-facing route UX.

Use symbolic / compact values only. If evidence is insufficient, prefer `not_assessed`, `false`, or omission over pretending precision.

## Behavior boundaries

- Preserve existing Navigate act space: `choose_unit`, `request_skill`, and `defer_detour`.
- Preserve durable detour statuses: `open`, `resolved`, and `abandoned`.
- Do not add durable `status="deferred"`.
- Preserve `detour = planning path deviation`.
- Preserve `active_recall = memory recovery`.
- Preserve `look_back = source calibration`.
- Do not add retrieval loops, planner behavior, prompt text changes, route steering, user route choice, visible route UX, or recommender behavior.

## Engineering tests

Future implementation PR should run:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_scaffold.py tests/test_attentional_v2_nodes.py -q
```

Tests should verify:

- compact support markers appear on detour / navigation evidence only when relevant;
- `budget_stop_reason` is recorded for budget exhaustion or deferred paths when available;
- marker fields preserve old Slice 5A lifecycle and audit fields;
- Navigate act space remains only `choose_unit`, `request_skill`, and `defer_detour`;
- no durable `deferred` detour status is introduced;
- no active-recall or look-back retrieval loop is introduced;
- markers are not treated as utilization proof, planning-quality proof, product scores, or settlement truth;
- read-audit rows do not receive full prompt packets, full skill payloads, or route UX payloads.

## Contract / audit checks

- Do not route audit dumps into prompts.
- Do not treat memory projection as source truth.
- Do not expose route trace as user-facing route UX.
- Do not claim planning quality from audit markers.
- Preserve source-grounded mainline continuity.
- Preserve active-recall / look-back / detour distinctions.
- Do not introduce planner agent, memory manager agent, retriever agent, vector DB, graph DB, or Memory OS.

## Behavior smoke, if any

- None for the brief-landing task.
- Future Slice 5B implementation should use targeted tests only.
- No full AI Evaluation.

## Non-goals

- No new planner behavior.
- No new Navigate decisions.
- No active-recall loop.
- No look-back loop.
- No prompt text or prompt version change.
- No `state_ops.py` change.
- No `read_context.py` change.
- No source-skill behavior change.
- No slow-cycle work.
- No public API, frontend, or eval runner change.
- No route steering UI.
- No user route choice.
- No visible route UX.
- No full AI Evaluation.

## Risks

- Field names such as `detour_value` and `continuity_cost` may be misread as product scoring. The implementation must define them as symbolic audit markers only.
- Over-inference from reason strings, budget state, or skill summaries could create false precision. Default to `not_assessed`, `false`, or omission.
- Persisting too much trace evidence could bloat `read_audit.jsonl`. Keep markers compact and avoid full payload dumps.
- Route trace metadata could be mistaken for user-facing route disclosure. Keep all additions mechanism-private.

## Rollback plan

Revert the future Slice 5B PR.

Additive optional `TypedDict`, read-audit, and local-continuity trace metadata requires no migration. Existing detour and navigation behavior returns to the Slice 5A state.

## Open questions

None blocking.

Default decisions:

- no prompt change;
- no `read_context.py` change;
- no source-skill behavior change;
- no retrieval loop;
- no new Navigate act;
- no durable `deferred`;
- no route UX;
- use `not_assessed`, `false`, or omission when support/value/cost evidence is ambiguous.

## Go / no-go recommendation

Go for human review of this Slice 5B Pre-implementation Brief.

No-go for implementation until this brief is accepted.
