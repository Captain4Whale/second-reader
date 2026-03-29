# Current State

Purpose: capture the canonical repo-local view of current project status for agent switching and human recovery.
Use when: onboarding a new coding agent, resuming work without chat history, or checking which initiative is current now.
Not for: long-form rationale, full historical detail, or session-only scratch notes.
Update when: the current objective, active tasks, blockers, active jobs, open decisions, risks, or recommended reading path change.

This file is authoritative for durable current status. Do not keep unique active-state information only in `docs/agent-handoff.md`.

Last verified: `2026-03-29T09:12:56Z`

## Current Objective
- Keep Phase 9 of the new reading mechanism project recoverable and decision-ready:
  - inspect the completed English two-case evidence rerun without converting it into an automatic mechanism or promotion decision
  - work from the recovered private-library local-only datasets rather than the stale seed-reset narrative
  - preserve the remaining benchmark-hardening backlog and human-owned gate decisions in repo-local state

## Now
- Treat `attentional_v2` as experimental and `iterator_v1` as the current default mechanism.
- The English chapter-core retry-2 closeout is still the last completed comparison baseline:
  - run:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round2_microselectivity_retry2_20260328/`
  - round-1 vs retry-2 shift:
    - English `local_impact` improved from `0/4` win-or-tie to `2/4` win-or-tie
    - English `system_regression` improved from `2/4` wins to `3/4` wins
  - verified interpretation:
    - the landed micro-selectivity repair helped most on argumentative / expository English chapters
    - the remaining local gap is now concentrated on narrative / reference-heavy English cases rather than on the whole pack
  - live queue record:
    - `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md`
    - `docs/implementation/new-reading-mechanism/execution-tracker.md`
- The bounded narrative/reference-heavy Phase 4 repair is landed in code for:
  - `up_from_slavery_public_en__10`
  - `walden_205_en__10`
  - landed mechanism change:
    - deterministic local cue packets now include `actor_intention`, `social_pressure`, and `causal_stakes`
    - short spans may synthesize one bounded local candidate from those cues when the local gate is genuinely open
    - zoom/closure/emission prompts now prefer one grounded why-now observation or question over retrospective summary in those moments
  - local verification:
    - `reading-companion-backend/tests/test_attentional_v2_nodes.py`
    - `13` node tests passed on `2026-03-28`
- The temporary seed-reset / missing-review-state problem is no longer current:
  - English cleanup recovery completed successfully:
    - archive:
      - `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_recovery_20260329/`
    - summary:
      - `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_recovery_20260329/dataset_review_pipeline_summary.json`
    - live English local-only dataset counts:
      - `7` `reviewed_active`
      - `3` `needs_revision`
      - `6` `needs_replacement`
      - `154` `unset`
    - live open English cases:
      - `fooled_by_randomness_private_en__14__seed_2`
      - `evicted_private_en__10__seed_1`
      - `evicted_private_en__17__seed_2`
      - `poor_charlies_almanack_private_en__10__seed_1`
      - `poor_charlies_almanack_private_en__10__seed_2`
      - `steve_jobs_private_en__24__seed_1`
      - `steve_jobs_private_en__24__seed_2`
      - `steve_jobs_private_en__17__seed_1`
      - `supremacy_private_en__13__seed_1`
  - Chinese cleanup recovery completed successfully:
    - archive:
      - `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_recovery_20260329/`
    - summary:
      - `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_recovery_20260329/dataset_review_pipeline_summary.json`
    - live Chinese local-only dataset counts:
      - `13` `reviewed_active`
      - `1` `needs_revision`
      - `2` `needs_replacement`
      - `40` `unset`
    - live open Chinese cases:
      - `kangxi_hongpiao_private_zh__12__seed_2`
      - `kangxi_hongpiao_private_zh__27__seed_1`
      - `zouchu_weiyi_zhenliguan_private_zh__8__seed_1`
  - both recovery summaries explicitly recorded `decision_bearing_followup_launched: false`
- The review queue is empty again:
  - `reading-companion-backend/eval/review_packets/review_queue_summary.json`
  - `active_packet_count = 0`
- The focused English round-3 narrative/reference rerun is no longer running:
  - job id:
    - `bgjob_en_chapter_core_rerun_round3_parallel_20260329`
  - run dir:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_20260329/`
  - log:
    - `reading-companion-backend/state/job_registry/logs/bgjob_en_chapter_core_rerun_round3_parallel_20260329.log`
  - terminal status:
    - registry now reports `status = failed`, `exit_code = 1`, and `ended_at = 2026-03-29T03:22:18.900454Z`
    - the log ends with `ReaderLLMError: malformed json payload`
  - recovered partial outputs:
    - `up_from_slavery_public_en__10` has a case artifact, but its `attentional_v2` entry incorrectly points at the `walden_205_en__10` output directory, so the packaged comparison is not trustworthy as-is
    - `walden_205_en__10` never received a case artifact or final summary artifacts
    - `walden_205_en__10` `iterator_v1` activity shows repeated `network_blocked` stalls before the terminal malformed-JSON failure on `Visitors.13`
- The first malformed-JSON recovery rerun is no longer active:
  - job id:
    - `bgjob_20260329_035257_e6069f7e`
  - run dir:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_jsonfix_20260329/`
  - log:
    - `reading-companion-backend/state/job_registry/logs/bgjob_20260329_035257_e6069f7e.log`
  - terminal status:
    - registry now reports `status = abandoned` and `ended_at = 2026-03-29T04:18:48.646303Z`
    - the rerun was stopped intentionally after confirming the same parallel case path could still cross-wire isolated output directories
- The first case-isolation rerun did not finish cleanly:
  - job id:
    - `bgjob_20260329_041914_5de2c4c4`
  - run dir:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_caseiso_20260329/`
  - log:
    - `reading-companion-backend/state/job_registry/logs/bgjob_20260329_041914_5de2c4c4.log`
  - terminal status:
    - registry now reports `status = abandoned` and `ended_at = 2026-03-29T04:24:43.447157Z`
    - the log stops after initial submit/skip lines, with no traceback and no summary outputs
  - launcher diagnosis:
    - the wrapper was launched from the Codex shell session and appears to have been terminated externally before it could record an exit code or traceback
    - the missing wrapper launch banner in the earlier failed log was consistent with the wrapper being killed before its buffered write flushed
- A detached-launch follow-up rerun completed successfully after the malformed-JSON recovery patch, the packaging isolation repair, and the launcher hardening:
  - job id:
    - `bgjob_en_chapter_core_rerun_round3_parallel_caseiso_detached_20260329_125043`
  - run dir:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_caseiso_detached_20260329_125043/`
  - log:
    - `reading-companion-backend/state/job_registry/logs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_detached_20260329_125043.log`
  - current state:
    - the wrapper was launched via `scripts/launch_registered_job_detached.py`
    - registry now reports `status = completed`, `exit_code = 0`, and `ended_at = 2026-03-29T06:30:08.986637Z`
    - both case artifacts now point at their own output directories instead of cross-wiring `up_from_slavery` into `walden`
    - `summary/report.md`, `summary/aggregate.json`, and `summary/case_results.jsonl` were written successfully
    - the run used `--judge-mode none`, so the reported `tie: 2` outcome is placeholder evidence with `judge_unavailable`, not real judged comparison evidence
    - the rerun remains evidence-only and does not change promotion or default-cutover policy automatically
  - diagnosis/fix summary:
    - the prior `up_from_slavery` -> `walden` mispackaging is consistent with process-wide `resolve_output_dir` patching during parallel case execution
    - `run_chapter_comparison.py` now uses context-local output-dir overrides plus per-case subprocess isolation when parallel case workers are used
    - `run_registered_job.py` now flushes its launch banner, isolates the wrapped command into a new session, and records signal-based abandonment explicitly
    - `scripts/launch_registered_job_detached.py` is now the reliable path for launching long-running registered jobs from agent/non-interactive shells
- No benchmark promotion reopening, reviewed-slice freezing, durable-trace, re-entry, runtime-viability, or default-cutover work has been launched automatically after recovery.
- The new cleanup follow-up packet pair is now completed and archived:
  - English follow-up:
    - job id: `bgjob_private_library_cleanup_en_followup_after_recovery_20260329_launch`
    - packet id: `attentional_v2_private_library_cleanup_en_followup_after_recovery_20260329`
    - archived summary: `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_followup_after_recovery_20260329/dataset_review_pipeline_summary.json`
    - import result:
      - `drop = 6`
      - `revise = 3`
      - `keep = 0`
    - post-import counts remain:
      - `7` `reviewed_active`
      - `3` `needs_revision`
      - `6` `needs_replacement`
      - `154` `unset`
  - Chinese follow-up:
    - job id: `bgjob_private_library_cleanup_zh_followup_after_recovery_20260329_launch`
    - packet id: `attentional_v2_private_library_cleanup_zh_followup_after_recovery_20260329`
    - archived summary: `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_followup_after_recovery_20260329/dataset_review_pipeline_summary.json`
    - import result:
      - `drop = 2`
      - `revise = 1`
      - `keep = 0`
    - post-import counts remain:
      - `13` `reviewed_active`
      - `1` `needs_revision`
      - `2` `needs_replacement`
      - `40` `unset`
- The coordination lane closeout is complete:
  - `eval/review_packets/review_queue_summary.json` was refreshed once after both imports
  - both archived follow-up packets now have `dataset_review_pipeline_summary.json`
- The judged mechanism-evidence lane remains active:
  - job id: `bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329`
  - run id: `attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_caseiso_judged_20260329`
  - this rerun uses `--judge-mode llm` and is intended to produce real comparison evidence rather than placeholder `judge_unavailable` ties
  - latest diagnosis:
    - the job is not currently showing the same early silent-exit pattern as the earlier abandoned launcher run
    - both case-worker subprocesses remain alive and are still writing fresh `attentional_v2` runtime state under:
      - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_caseiso_judged_20260329/outputs/up_from_slavery_public_en__10/attentional_v2/_runtime/run_state.json`
      - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_caseiso_judged_20260329/outputs/walden_205_en__10/attentional_v2/_runtime/run_state.json`
    - both case workers are still emitting successful LLM trace rows into their local `llm_standard.jsonl` files with `MiniMax-M2.7-highspeed` and `quota_wait_ms_total = 0`
    - the wrapper log still looks almost frozen because `eval/attentional_v2/run_chapter_comparison.py` prints only submit and whole-case completion lines at the parent level; it does not surface per-case worker progress while a case is still inside mechanism execution
    - operational conclusion: do not relaunch this judged rerun unless the per-case runtime files stop advancing or the worker processes exit without writing case summaries
- The earlier "10 more books" note now appears to have been a misunderstanding rather than a separate visible intake wave:
  - the repo-visible private-library source pool still matches the tracked `29`-book supplement
  - that supplement already includes the known `16`-book `/Users/baiweijiang/Documents/BOOK/` batch plus the earlier `13` private Downloads books
  - `state/library_sources/` has no extra private EPUBs beyond that tracked manifest
  - no separate new 10-book wave is currently visible to the private-library builder
- The next queued dataset-platform roadmap is now explicit:
  - make the dataset build method smarter, more effective, and more efficient
  - make dataset building fully automated end to end, with LLM replacing remaining non-decision curation where policy allows
  - make source-book intake and intermediate-artifact management clear and durable, with canonical managed copies and one documented drop-folder workflow for future additions
- Use the task registry plus the execution tracker as the route back into detailed mechanism work.

## Next
- Monitor the remaining active judged rerun:
  - `bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329`
- Treat the current sparse wrapper log as a visibility limitation rather than as proof of another early failure.
  - confirm health from the live case runtime files and per-case `llm_standard.jsonl` traces until `summary/report.md` lands
- Inspect the judged rerun as real mechanism evidence once its `summary/report.md` and `summary/aggregate.json` land.
- Use the cleanup follow-up summaries as the new benchmark-hardening truth:
  - the extra cleanup pass did not produce any `keep` decisions
  - the English `9` and Chinese `3` open cases were reaffirmed as `revise` / `drop` rather than promoted into `reviewed_active`
- Prepare the next dataset-platform design while the judged rerun is still in flight, but implement it in phases:
  - source-book intake and intermediate-artifact governance first
  - smarter question-first case mining second
  - end-to-end dataset automation/orchestration third
- Keep the prior failed `bgjob_en_chapter_core_rerun_round3_parallel_20260329` artifacts as debugging evidence:
  - treat `up_from_slavery_public_en__10` as packaging-corrupted because the `attentional_v2` case entry points at `walden` outputs
  - treat `walden_205_en__10` as incomplete because no case artifact or summary artifacts were written
- Work from the recovered live local-only excerpt datasets:
  - the current follow-up cleanup pass has now dispositioned those cases mechanically, but it did not clear the open benchmark-status backlog
  - keep the review queue empty unless a deliberate new packet is created
- Prepare a human-owned post-cleanup gate review from the recovered counts, the two new follow-up packet summaries, and the still-open benchmark statuses.
- Keep benchmark promotion, reviewed-slice freezing, durable-trace, re-entry, runtime-viability, and any default-cutover decision paused until a human explicitly asks for them.

## Blocked
- Formal curated promotion from the modern private-library supplement remains paused until the remaining open cases are dispositioned and a human explicitly reopens the post-recovery gate discussion.
- Reviewed-slice freezing remains paused until a human explicitly chooses to freeze a slice.
- Durable-trace, re-entry, and runtime-viability remain intentionally queued until the failed rerun is dispositioned and the post-recovery benchmark gate becomes an explicit human-owned decision.
- The later frontend/API retirement of section-first chapter/detail and marks surfaces remains blocked on benchmark stabilization plus stable doc promotion timing.
- `Q10` remains open: when the detailed `attentional_v2` working design should be promoted from temp docs into stable mechanism docs.

## Open Decisions
- `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE`
  - The live reviewed state has been restored, and the extra cleanup/review pass is now complete. The new follow-up packet summaries did not add any `keep` decisions, so the remaining human-owned question is whether promotion should stay closed until a more substantive backlog-clearing move is chosen.
- `OD-BENCHMARK-SIZE`
  - Is the current benchmark family already large enough for high-confidence cross-mechanism judgment, or should the benchmark expand before any default-cutover decision?
- `Q10`
  - When should the detailed `attentional_v2` working design be promoted from temporary implementation docs into stable mechanism docs?

## Active Risks
- Re-running `build_private_library_supplement.py` without explicit intent to rebuild seed datasets can wipe live private-library review status again.
- Pre-fix parallel comparison artifacts can misassign case-to-output mappings, so partial outputs from the earlier round-3 reruns must be sanity-checked before they are treated as evidence.
- Malformed-JSON handling in the reading path can still terminate a bounded rerun after substantial partial output has already been written.
- Launching `run_registered_job.py` from a transient agent shell without the detached launcher can leave long-running jobs looking `abandoned` even when the wrapped command itself never raised a Python traceback.
- The current judged rerun's parent log is sparse enough to resemble a stall even while child workers continue making progress, so health checks should look at per-case runtime files and local LLM traces rather than only the top-level job log.
- The completed detached two-case rerun used `--judge-mode none`, so its `tie: 2` aggregate can be mistaken for a real comparison result unless we keep the placeholder nature explicit.
- Private-library source intake still depends on hard-coded builder specs and indirect external roots, which makes future book addition, provenance control, and zero-touch automation harder than it should be.
- Current public chapter/detail surfaces still carry section-shaped compatibility assumptions that may not fit the new mechanism directly.
- Route mismatches between frontend routes and backend-returned targets can still regress the canonical product path.
- Resume behavior remains sensitive to artifact placement under `reading-companion-backend/output/` and `reading-companion-backend/state/`.
- Benchmark confidence can look stronger than it really is if corpus growth, promotion, and reviewed-slice confidence gates drift apart.

## Active Task IDs
- `TASK-BENCH-BACKLOG-RESCUE`
- `TASK-MECH-EN-RERUN`

## Active Job IDs
- `bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329`

## Recommended Reading Path
1. `AGENTS.md`
2. `README.md`
3. `docs/current-state.md`
4. relevant child `AGENTS.md`
5. `docs/tasks/registry.md`
6. `reading-companion-backend/state/job_registry/jobs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329.json`
7. `reading-companion-backend/state/job_registry/logs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329.log`
8. `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_followup_after_recovery_20260329/dataset_review_pipeline_summary.json`
9. `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_followup_after_recovery_20260329/dataset_review_pipeline_summary.json`
10. `reading-companion-backend/state/job_registry/jobs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_detached_20260329_125043.json`
11. `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_recovery_20260329/dataset_review_pipeline_summary.json`
12. `reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_recovery_20260329/dataset_review_pipeline_summary.json`
13. `docs/implementation/new-reading-mechanism/private-library-promotion-round2.md`
14. `docs/implementation/new-reading-mechanism/evaluation-question-map.md`
15. `docs/implementation/new-reading-mechanism/evaluation-corpus-requirements.md`
16. `docs/source-of-truth-map.md` when you need to decide where durable information belongs

## Machine-Readable Appendix
```json
{
  "updated_at": "2026-03-29T09:12:56Z",
  "last_updated_by": "codex",
  "active_task_ids": [
    "TASK-BENCH-BACKLOG-RESCUE",
    "TASK-MECH-EN-RERUN"
  ],
  "blocked_task_ids": [],
  "active_job_ids": [
    "bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329"
  ],
  "open_decision_ids": [
    "OD-PRIVATE-LIBRARY-POST-RESCUE-GATE",
    "OD-BENCHMARK-SIZE",
    "Q10"
  ],
  "detail_refs": [
    "docs/implementation/new-reading-mechanism/execution-tracker.md",
    "docs/implementation/new-reading-mechanism/private-library-promotion-round2.md",
    "docs/implementation/new-reading-mechanism/evaluation-question-map.md",
    "docs/implementation/new-reading-mechanism/evaluation-corpus-requirements.md",
    "reading-companion-backend/state/job_registry/jobs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329.json",
    "reading-companion-backend/state/job_registry/logs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_judged_20260329.log",
    "reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_followup_after_recovery_20260329/dataset_review_pipeline_summary.json",
    "reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_followup_after_recovery_20260329/dataset_review_pipeline_summary.json",
    "reading-companion-backend/state/job_registry/jobs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_detached_20260329_125043.json",
    "reading-companion-backend/state/job_registry/logs/bgjob_en_chapter_core_rerun_round3_parallel_caseiso_detached_20260329_125043.log",
    "reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_caseiso_detached_20260329_125043/summary/report.md",
    "reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_narrative_reference_repair_parallel_caseiso_detached_20260329_125043/summary/aggregate.json",
    "reading-companion-backend/state/job_registry/jobs/bgjob_en_chapter_core_rerun_round3_parallel_20260329.json",
    "reading-companion-backend/state/job_registry/logs/bgjob_en_chapter_core_rerun_round3_parallel_20260329.log",
    "reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_recovery_20260329/dataset_review_pipeline_summary.json",
    "reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_recovery_20260329/dataset_review_pipeline_summary.json"
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
