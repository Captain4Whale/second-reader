# Post-Recovery Gate Review Checklist

Purpose: turn the current post-recovery benchmark gate discussion into one explicit review procedure with concrete evidence inputs, decision questions, and allowed next moves.
Use when: resolving the current human-owned gate after cleanup recovery, deciding whether the callback slice is good enough to freeze for comparison cadence, or choosing whether the project returns to decisive mechanism-eval lanes now.
Not for: stable evaluation constitution, final default-cutover judgment, or open-ended dataset-builder brainstorming.
Update when: the evidence pack, decision order, acceptance framing, or allowed next-move matrix for this gate materially changes.

## Scope
- This checklist is for one narrow review only.
- It is meant to resolve the currently open near-term decisions:
  - `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE`
  - `OD-CALLBACKSLICE-BOUNDED-VARIANCE`
  - the near-term part of `OD-BENCHMARK-SIZE`
- It is not meant to decide:
  - final benchmark adequacy for default-cutover
  - whether `attentional_v2` should become the default mechanism
  - whether the dataset builder should expand again in general
  - whether stable-doc promotion under `Q10` should happen now

## Review Outcome Contract
- The review must end with explicit recorded answers, not only discussion.
- The required outputs are:
  - one decision for the private-library promotion gate
  - one decision for callbackslice bounded variance
  - one benchmark-size statement for the next lane
  - one concrete next move with an owner
- Allowed next moves are intentionally narrow:
  - keep promotion on `hold` and return the main cadence to decisive mechanism-eval work
  - keep promotion on `hold` and run one later audit-stage-only reproducibility pass before decisive mechanism-eval work
  - reopen promotion review only if the evidence genuinely changed beyond mechanical cleanup hardening
- Not allowed from this review:
  - opening a new general builder repair wave
  - widening unattended automation
  - treating current benchmark size as sufficient for default-cutover confidence

## Evidence Pack To Freeze Before Discussion
- Review this exact evidence set before any decision is recorded.
- Benchmark gate evidence:
  - [private-library-promotion-round2.md](/Users/baiweijiang/Documents/Projects/reading-companion/docs/implementation/new-reading-mechanism/private-library-promotion-round2.md)
  - [review_queue_summary.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/review_packets/review_queue_summary.json)
  - English recovery follow-up summary:
    - [dataset_review_pipeline_summary.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_en_followup_after_recovery_20260329/dataset_review_pipeline_summary.json)
  - Chinese recovery follow-up summary:
    - [dataset_review_pipeline_summary.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_cleanup_zh_followup_after_recovery_20260329/dataset_review_pipeline_summary.json)
- Callbackslice bounded-variance evidence:
  - adjudication probe job:
    - [bgjob_callbackslice_probeonly_20260331.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/job_registry/jobs/bgjob_callbackslice_probeonly_20260331.json)
  - adjudication probe summary:
    - [summary.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/review_packets/archive/attentional_v2_private_library_excerpt_en_question_aligned_v1__scratch__callbackslice_auditv4_20260331/llm_review_runs/llm_review__20260331-020939__1e09365bb0cb/summary.json)
  - same-input audit rerun job:
    - [bgjob_callbackslice_auditrerun_20260331.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/job_registry/jobs/bgjob_callbackslice_auditrerun_20260331.json)
  - same-input audit rerun state:
    - [run_state.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/runs/attentional_v2/case_audits/attentional_v2_private_library_excerpt_en_question_aligned_v1__scratch__callbackslice_auditv4_20260331__20260331-122848/run_state.json)
- Mechanism-mainline evidence that justifies returning to decisive eval:
  - broader English retry-2 aggregate:
    - [aggregate.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round2_microselectivity_retry2_20260328/summary/aggregate.json)
  - focused two-case substantive rerun aggregate:
    - [aggregate.json](/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round3_caseiso_judged_substantive_backup_20260331/summary/aggregate.json)
- Current routing and methodology:
  - [current-state.md](/Users/baiweijiang/Documents/Projects/reading-companion/docs/current-state.md)
  - [backend-reader-evaluation.md](/Users/baiweijiang/Documents/Projects/reading-companion/docs/backend-reader-evaluation.md)
  - [evaluation-question-map.md](/Users/baiweijiang/Documents/Projects/reading-companion/docs/implementation/new-reading-mechanism/evaluation-question-map.md)

## Review Order
1. Freeze the evidence pack named above. Do not mix in newer ad hoc artifacts halfway through the review.
2. Resolve `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE`.
3. Resolve `OD-CALLBACKSLICE-BOUNDED-VARIANCE`.
4. Record the near-term answer to `OD-BENCHMARK-SIZE`.
5. Choose exactly one next move from the allowed-outcome matrix below.
6. Update `docs/current-state.md` and `docs/tasks/registry.*` in the same task that records the outcome.

## Decision 1: `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE`

### Question
- Did the post-recovery cleanup work materially improve benchmark promotion readiness, or did it only harden the backlog mechanically?

### Facts To Keep Visible
- Queue state is clean:
  - `active_packet_count = 0`
- English remains the constraining lane:
  - `reviewed_active = 7`
  - `needs_revision = 3`
  - `needs_replacement = 6`
  - open backlog `= 9`
- Chinese is healthier:
  - `reviewed_active = 13`
  - `needs_revision = 1`
  - `needs_replacement = 2`
  - open backlog `= 3`
- The follow-up cleanup pass added `0` new `keep` decisions in both languages.
- The current recovery evidence explicitly says `decision_bearing_followup_launched: false`.

### Checklist
- [ ] Confirm the review is using the recovered live local-only datasets, not older seed-reset narratives.
- [ ] Confirm the queue is empty and there is no hidden active packet that would change the gate.
- [ ] Confirm the latest follow-up cleanup produced backlog hardening only, not new promotion-strengthening evidence.
- [ ] Confirm whether any substantive backlog-clearing move has landed after the cleanup summaries.

### Allowed Outcomes
- `keep_hold_for_backlog_rescue`
  - choose this when the evidence is still only mechanical hardening plus unchanged or still-thin English benchmark strength
- `reopen_promotion_review`
  - choose this only if there is genuinely new benchmark-strengthening evidence beyond the cleanup hardening itself

### Default Recommendation From Current Evidence
- `keep_hold_for_backlog_rescue`

## Decision 2: `OD-CALLBACKSLICE-BOUNDED-VARIANCE`

### Question
- Is the current callback slice already good enough to freeze for comparison cadence, or is one more audit-stage-only reproducibility pass still required first?

### Facts To Keep Visible
- The probe/rerun evidence now separates builder/input drift from audit/adjudication variance.
- Same-input adjudication probe:
  - `same_packet_input_fingerprint = true`
  - `audit_input_drift = 0`
  - `action_drift = 1`
- Same-input audit rerun:
  - `audit_input_drift = 0`
  - `primary_decision_drift = 1`
  - `primary_score_drift = 2`
- Current interpretation already recorded elsewhere:
  - this is bounded same-input variance
  - this is not evidence for another general builder repair wave

### Checklist
- [ ] Confirm the observed remaining drift is audit/adjudication-stage variance, not builder/input drift.
- [ ] Confirm no one is using this review to smuggle in a new builder redesign request.
- [ ] Decide whether `action_drift = 1` plus `primary_decision_drift = 1` is acceptable for frozen-slice comparison cadence.
- [ ] If not acceptable, confirm the repair is exactly one later audit-stage-only reproducibility pass on frozen inputs.

### Allowed Outcomes
- `accept_bounded_variance_for_frozen_slice`
  - use this when the team judges the remaining variance small enough to stop blocking comparison cadence
- `run_one_more_audit_stage_repro_pass`
  - use this when the team still wants tighter same-input stability before freezing the slice

### Explicit Guardrail
- Even if the decision is `run_one_more_audit_stage_repro_pass`, the next move is still not:
  - a new general builder wave
  - wider unattended automation

## Decision 3: Near-Term `OD-BENCHMARK-SIZE`

### Question
- Is the current benchmark family large enough for the next decisive mechanism-eval lane, even if it is not yet large enough for final default-cutover confidence?

### Checklist
- [ ] Separate "enough for the next decisive lane" from "enough for final promotion/default-cutover confidence".
- [ ] Confirm whether the current benchmark is already adequate to support durable-trace / re-entry / runtime-viability work.
- [ ] Confirm whether any benchmark expansion is being proposed for final confidence only, not as a reason to block the next lane automatically.

### Allowed Outcomes
- `adequate_for_next_decisive_lane_only`
  - the likely current answer if the team agrees that decisive mechanism-eval should resume now
- `expand_before_default_cutover_only`
  - use this together with the outcome above when the family is still too small for final product-confidence
- `not_enough_even_for_next_lane`
  - choose this only if there is a specific reason the current benchmark cannot support durable-trace / re-entry / runtime-viability work yet

### Default Recommendation From Current Methodology
- `adequate_for_next_decisive_lane_only`
- `expand_before_default_cutover_only`

## Allowed Outcome Matrix

### Path A
- `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE = keep_hold_for_backlog_rescue`
- `OD-CALLBACKSLICE-BOUNDED-VARIANCE = accept_bounded_variance_for_frozen_slice`
- `OD-BENCHMARK-SIZE = adequate_for_next_decisive_lane_only`
- Next move:
  - keep promotion closed
  - freeze the callback slice for comparison cadence
  - launch durable-trace / re-entry / runtime-viability
  - do not open new general builder or automation work first

### Path B
- `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE = keep_hold_for_backlog_rescue`
- `OD-CALLBACKSLICE-BOUNDED-VARIANCE = run_one_more_audit_stage_repro_pass`
- `OD-BENCHMARK-SIZE = adequate_for_next_decisive_lane_only`
- Next move:
  - keep promotion closed
  - register one later audit-stage-only reproducibility job on frozen inputs
  - return to the same decisive mechanism-eval lanes immediately after that pass
  - do not open new general builder or automation work first

### Path C
- `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE = reopen_promotion_review`
- Additional rule:
  - this path requires explicit new benchmark-strengthening evidence, not just the already-known cleanup state
- Next move:
  - record exactly what changed
  - update the promotion doc and task routing in the same task
  - still keep decisive mechanism-eval timing explicit instead of letting promotion work swallow the whole cadence again

## Review Closeout Template
- `reviewed_at`:
- `reviewers`:
- `evidence_pack_frozen_at`:
- `OD-PRIVATE-LIBRARY-POST-RESCUE-GATE`:
- `OD-CALLBACKSLICE-BOUNDED-VARIANCE`:
- `OD-BENCHMARK-SIZE`:
- `chosen_path`:
- `next_job_or_task`:
- `owner`:
- `docs_to_update_now`:

## Recording Rule
- The review is not complete until the chosen outcomes are written back into:
  - `docs/current-state.md`
  - `docs/tasks/registry.md`
  - `docs/tasks/registry.json`
- If the outcome changes project direction materially, also update:
  - `docs/history/decision-log.md`
