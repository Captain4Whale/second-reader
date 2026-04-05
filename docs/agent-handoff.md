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

Last updated: `2026-04-05T01:48:52Z`

## Session Scratchpad
- This file is only a fast handoff index. Durable truth has already been synced into:
  - `docs/current-state.md`
  - `docs/tasks/registry.md`
  - `docs/tasks/registry.json`
  - `reading-companion-backend/state/job_registry/jobs/<job_id>.json`

### Must-Read For A New Codex Thread
- `AGENTS.md`
- `README.md`
- `docs/current-state.md`
- `reading-companion-backend/AGENTS.md`
- `docs/tasks/registry.md`

### What The Project Is Doing Right Now
- Mainline work is in `Phase 9` under the split-surface evaluation strategy.
- The three kept eval targets are:
  - `reader_character.selective_legibility`
  - `reader_character.coherent_accumulation`
  - `reader_value.insight_and_clarification`
- Evaluation is intentionally split into two surfaces:
  - `local / excerpt`
    - uses the completed human-notes-guided excerpt reviewed freeze
    - currently the decisive active lane
  - `long-span / window`
    - uses the bounded accumulation benchmark v1
    - first-review repair just completed and now needs a freeze decision

### Current Live Background Job
- Active job id:
  - `bgjob_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405`
- Purpose:
  - rerun the full judged local excerpt comparison on the human-notes-guided manifest under `MiniMax-M2.7-personal`
- Status at handoff:
  - still `running`
  - no `summary/aggregate.json` yet
- Key files:
  - job record:
    - `reading-companion-backend/state/job_registry/jobs/bgjob_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405.json`
  - log:
    - `reading-companion-backend/state/job_registry/logs/bgjob_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405.log`
  - run dir:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405`

### Completed Just Before Handoff
- Long-span repaired first review completed:
  - `bgjob_accumulation_benchmark_v1_repair_first_review_20260405`
- Result:
  - `keep = 7`
  - `revise = 2`
  - `drop = 0`
  - post-import:
    - `reviewed_active = 7`
    - `needs_revision = 2`
- The two revise probes are:
  - `huochu_shengming_de_yiyi_private_zh__8__probe_1`
  - `huochu_shengming_de_yiyi_private_zh__8__probe_2`
- Meaning:
  - the long-span repair succeeded enough to produce benchmark-ready keeps
  - next long-span move is narrow:
    - either repair those two chapter-8 probes
    - or freeze honestly short
  - do not launch judged accumulation comparison until that choice is made

### Background Job Survival
- The active eval job was launched through the detached wrapper:
  - `reading-companion-backend/scripts/launch_registered_job_detached.py`
- Because the launcher uses a detached process/session, switching Codex thread or Codex key should not stop the job by itself.
- Another thread can re-check with:
  - `cd /Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py --job-id bgjob_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405 --job-id bgjob_accumulation_benchmark_v1_repair_first_review_20260405`
- Quick active-view file:
  - `reading-companion-backend/state/job_registry/active_jobs.md`

### Immediate Next Move For The New Thread
- First, re-check the active excerpt rerun job.
- If `summary/aggregate.json` and `summary/report.md` exist, interpret:
  - `selective_legibility` first
  - `insight_and_clarification` second
- If those files are still missing, keep monitoring; if the run exits without them, treat it as harness failure rather than mechanism evidence.
- Separately, keep the long-span next decision narrow:
  - do not reopen a broad builder wave
  - decide repair-vs-freeze on the two revise probes only
