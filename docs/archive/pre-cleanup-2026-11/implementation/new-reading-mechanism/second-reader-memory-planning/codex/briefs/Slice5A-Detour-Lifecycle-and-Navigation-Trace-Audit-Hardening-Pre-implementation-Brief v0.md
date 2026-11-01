# Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0

## PR title

Slice 5A: Detour Lifecycle and Navigation Trace Audit Hardening

## Implementation slice

Slice 5A is the first small reversible sub-slice of Slice 5 / Planning Trace, Detour, Recall, and Look-back Hardening.

The focus is trace and audit clarity for the existing detour lifecycle and navigation act loop, not new planning behavior.

## Design sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计2-Planning Ontology Design v0.md`
- `C设计4-Navigation Policy Design v0.md`
- `C设计6-Detour : Look-back : Active Recall Policy Design v0.md`
- `C设计7-Memory Retrieval & Utilization Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `codex/briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
- `codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
- `codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- `codex/briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
- `codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
- `codex/E实施-progress-ledger.md`

## Current code facts

- `schemas.py` defines `DetourNeed`, `DetourTraceEntry`, `NavigateActResult`, `NavigateActTraceEntry`, and the current Navigate decisions `choose_unit`, `request_skill`, and `defer_detour`.
- `runner.py` owns `_apply_detour_need(...)`, `_active_detour_need(...)`, `_build_detour_navigation_packet(...)`, `_build_detour_read_context(...)`, `_navigate_trace_entry(...)`, and `navigate_choose_next_unit(...)`.
- `detour_trace` currently records `detour_id`, `origin_cursor`, `origin_target_hint`, and `status`, but not open, defer, resolve, abandon, or restore-mainline reasons.
- `_apply_detour_need(...)` supports durable statuses `open`, `resolved`, and `abandoned`, not durable `deferred`.
- `navigate_trace` already captures act decision, reason, budget state, and compact skill request/result evidence, but it is returned in selection results and is not clearly persisted as read-audit evidence.
- Current source skills live at `reading-companion-backend/src/attentional_v2/skills/source_skills.py`, not a top-level `source_skills.py`.
- Slice 4B confirmed that the current runner main read path still passes `supplemental_context=None`; Slice 5A must not create active-recall, look-back, or supplemental retrieval loops.

## Files to change

Future implementation PR may change:

- `reading-companion-backend/src/attentional_v2/schemas.py`, for optional trace/audit `TypedDict` fields only.
- `reading-companion-backend/src/attentional_v2/runner.py`, for helper-level detour trace enrichment and passing compact navigation trace evidence only.
- `reading-companion-backend/src/attentional_v2/observability.py`, for compact `read_audit` navigation/detour trace fields only.
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`
- Optionally `reading-companion-backend/tests/test_attentional_v2_nodes.py`, only to lock the unchanged Navigate act space.

## Files explicitly not changing

- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/skills/source_skills.py`
- durable memory stores
- public API
- frontend
- eval runners

No prompt text or prompt version change is in scope unless a later brief patch proves it is necessary.

## Planned deltas

- Add compact optional detour trace metadata only where current lifecycle facts are otherwise ambiguous:
  - `open_reason`
  - `defer_reason`
  - `resolve_reason`
  - `abandon_reason`
  - `restore_mainline_reason`
  - `last_navigation_decision`
  - `last_navigation_reason`
- Preserve current durable detour statuses: `open`, `resolved`, and `abandoned`.
- Keep `deferred` as a navigation outcome or audit reason, not a new durable detour status.
- Add compact `read_audit` navigation evidence when available, reusing the existing `NavigateActTraceEntry` shape and skill result summary.
- Do not write full prompt packets, source-skill payloads, or audit dumps into prompts.
- Keep `active_detour_id`, origin cursor, target hint, source-skill evidence, and budget state visible enough to reconstruct detour open, continue, defer, resolve, abandon, and mainline restore.
- Preserve the existing Navigate act space: `choose_unit`, `request_skill`, and `defer_detour`.
- Do not implement an `active_recall` / `look_back` retrieval loop in Slice 5A.

## Engineering tests

Future implementation PR should run:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_scaffold.py tests/test_attentional_v2_resume.py tests/test_attentional_v2_nodes.py -q
```

Tests should verify:

- detour open records origin cursor, target hint, and open reason;
- detour deferral records defer reason without adding a new Navigate decision;
- detour abandon records abandon reason without adding a durable `deferred` status;
- detour resolution records resolve and restore-mainline reasons without deleting lineage;
- skill request/result evidence remains compact;
- `read_audit` preserves old fields and adds navigation/detour evidence only when available;
- `choose_unit`, `request_skill`, and `defer_detour` remain the only Navigate act decisions.

## Contract / audit checks

- Preserve source-grounded mainline continuity.
- Preserve `active_recall = memory_recovery`.
- Preserve `look_back = source_calibration`.
- Preserve `detour = planning path deviation`.
- Do not treat memory projection as source truth.
- Do not route audit dumps into prompts.
- Do not introduce route steering, user route choice, visible route UX, recommender behavior, new planner behavior, planner agent, memory manager, retriever agent, vector DB, graph DB, or Memory OS.

## Behavior smoke, if any

- None for the brief-landing task.
- Future Slice 5A implementation should use targeted tests only.
- No full AI Evaluation.

## Non-goals

- No new planner.
- No new Navigate decisions.
- No retrieval behavior change.
- No active-recall or look-back retrieval loop.
- No prompt text change.
- No `state_ops.py` behavior change.
- No slow-cycle work.
- No public API, frontend, or eval runner change.
- No full utilization trace.
- No full AI Evaluation.

## Risks

- Adding trace fields to `local_continuity.detour_trace` could be mistaken for a new detour state machine; the future implementation must keep them audit metadata only.
- Persisting navigation trace could bloat `read_audit` if full payloads are copied; the future implementation must keep entries compact and reuse existing summaries.
- Recording restore-mainline reason could be overread as user-visible route disclosure; it must remain mechanism-private.

## Rollback plan

Revert the future Slice 5A PR.

Optional `TypedDict`, `read_audit`, and `local_continuity` trace metadata is additive and mechanism-private, with no migration requirement. Existing detour behavior returns to the Slice 4B state.

## Open questions

None blocking.

Default decisions:

- no prompt change;
- no durable `deferred` status;
- no new Navigate act;
- no retrieval loop;
- no source-skill behavior change;
- no visible route surface.

## Go / no-go recommendation

Go for human review of the Slice 5A brief.

No-go for implementation until the Slice 5A Pre-implementation Brief is accepted.
