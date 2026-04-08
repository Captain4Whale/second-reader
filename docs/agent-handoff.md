# Agent Handoff

Purpose: provide a session-only scratchpad for in-flight work that has not yet been canonicalized.
Use when: a current task needs temporary notes during one active session.
Not for: durable project status, task routing, active job truth, or any fact that should survive the session by itself.
Update when: temporary session notes appear or are cleared.

This file is not authoritative. Durable current state must live in:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/state/job_registry/jobs/<job_id>.json`

Derived active-job views may also help during a session:
- `reading-companion-backend/state/job_registry/active_jobs.json`
- `reading-companion-backend/state/job_registry/active_jobs.md`

Before ending a task, move any durable information into those canonical files and clear this scratchpad.

Last updated: `2026-04-08T13:50:14Z`

## Session Scratchpad
