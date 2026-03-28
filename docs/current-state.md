# Current State

Purpose: capture the canonical repo-local view of current project status for agent switching and human recovery.
Use when: onboarding a new coding agent, resuming work without chat history, or checking which initiative is current now.
Not for: long-form rationale, full historical detail, or session-only scratch notes.
Update when: the current objective, active tasks, blockers, active jobs, open decisions, risks, or recommended reading path change.

This file is authoritative for durable current status. Do not keep unique active-state information only in `docs/agent-handoff.md`.

Last verified: `2026-03-28T07:33:36Z`

## Current Objective
- Keep Phase 9 of the new reading mechanism project recoverable and decision-ready:
  - review the landed English chapter-core retry-2 evidence and turn it into a bounded repair queue
  - apply the round-2 private-library benchmark-growth decision now that cleanup and draft generation are finished
  - preserve later migration and doc-promotion work without letting it disappear into chat memory

## Now
- Treat `attentional_v2` as experimental and `iterator_v1` as the current default mechanism.
- The English chapter-core retry-2 run is fully landed and archived:
  - run:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round2_microselectivity_retry2_20260328/`
  - retry-2 vs round-1 shift:
    - English `local_impact` improved from `0/4` win-or-tie to `2/4` win-or-tie
    - English `system_regression` improved from `2/4` wins to `3/4` wins
- The private-library cleanup orchestrator is also fully landed and archived:
  - decision artifact:
    - `docs/implementation/new-reading-mechanism/private-library-promotion-round2.md`
    - `docs/implementation/new-reading-mechanism/private-library-promotion-round2.json`
  - current dataset-growth result:
    - decision `hold_for_backlog_rescue`
    - English private-library excerpt lane remains thin at `6` `reviewed_active` against threshold `7`
    - Chinese private-library excerpt lane now passes the gate at `11` `reviewed_active` against threshold `9`
- There are no active long-running background jobs in the registry right now.
- Use the task registry plus the execution tracker as the route back into detailed mechanism work.

## Next
- Compare retry-2 English chapter-core results against round 1 and turn the split result into a bounded implementation queue.
- Apply the round-2 `hold_for_backlog_rescue` decision:
  - rescue the English private-library excerpt backlog before formal curated promotion
  - preserve the Chinese gains without expanding the chapter lane beyond the current `2` eligible chapter candidates
- After the current chapter-core follow-up is dispositioned, run durable-trace, re-entry, and runtime-viability evaluation.

## Blocked
- Formal curated promotion from the modern private-library supplement remains withheld by the round-2 `hold_for_backlog_rescue` decision while the English excerpt lane stays below threshold.
- The later frontend/API retirement of section-first chapter/detail and marks surfaces remains blocked on benchmark stabilization plus stable doc promotion timing.
- `Q10` remains open: when the detailed `attentional_v2` working design should be promoted from temp docs into stable mechanism docs.

## Open Decisions
- `OD-CHAPTER-CORE-SPLIT-RESPONSE`
  - How much additional English-side local-reading repair should land before the broader comparison ladder continues unchanged?
- `OD-BENCHMARK-SIZE`
  - Is the current benchmark family already large enough for high-confidence cross-mechanism judgment, or should the benchmark expand before any default-cutover decision?
- `Q10`
  - When should the detailed `attentional_v2` working design be promoted from temporary implementation docs into stable mechanism docs?

## Active Risks
- Current public chapter/detail surfaces still carry section-shaped compatibility assumptions that may not fit the new mechanism directly.
- Route mismatches between frontend routes and backend-returned targets can still regress the canonical product path.
- Reaction taxonomy drift can reappear between runtime artifacts, API normalization, and frontend filters.
- Resume behavior remains sensitive to artifact placement under `reading-companion-backend/output/` and `reading-companion-backend/state/`.
- Benchmark confidence can look stronger than it really is if corpus growth, promotion, and reviewed-slice confidence gates drift apart.

## Active Task IDs
- `TASK-MECH-EN-RERUN`
- `TASK-BENCH-BACKLOG-RESCUE`

## Active Job IDs
- none

## Recommended Reading Path
1. `AGENTS.md`
2. `README.md`
3. `docs/current-state.md`
4. relevant child `AGENTS.md`
5. `docs/tasks/registry.md`
6. `docs/implementation/new-reading-mechanism/execution-tracker.md`
7. `reading-companion-backend/state/job_registry/active_jobs.md`
8. `docs/source-of-truth-map.md` when you need to decide where durable information belongs

## Machine-Readable Appendix
```json
{
  "updated_at": "2026-03-28T07:33:36Z",
  "last_updated_by": "codex",
  "active_task_ids": [
    "TASK-MECH-EN-RERUN",
    "TASK-BENCH-BACKLOG-RESCUE"
  ],
  "blocked_task_ids": [],
  "active_job_ids": [],
  "open_decision_ids": [
    "OD-CHAPTER-CORE-SPLIT-RESPONSE",
    "OD-BENCHMARK-SIZE",
    "Q10"
  ],
  "detail_refs": [
    "docs/implementation/new-reading-mechanism/execution-tracker.md",
    "docs/implementation/new-reading-mechanism/open-questions.md",
    "docs/implementation/new-reading-mechanism/private-library-promotion-round1-execution.md",
    "docs/implementation/new-reading-mechanism/private-library-promotion-round2.md"
  ],
  "truth_refs": [
    "docs/source-of-truth-map.md",
    "docs/product-overview.md",
    "docs/backend-reading-mechanism.md",
    "docs/backend-reader-evaluation.md",
    "docs/runtime-modes.md",
    "docs/tasks/registry.json"
  ]
}
```
