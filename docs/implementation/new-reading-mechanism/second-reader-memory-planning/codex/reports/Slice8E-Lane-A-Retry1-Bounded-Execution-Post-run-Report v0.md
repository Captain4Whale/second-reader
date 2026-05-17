# Slice 8E: Lane A Retry1 Bounded Execution Post-run Report

## Summary

Slice 8E executed the accepted Lane A `_retry1` bounded smoke after the Slice 8D source-locator compatibility patch. The run stayed within scope: `attentional_v2` only, one `huochu` segment, three note cases, and `--judge-mode llm`.

Result: completed. The retry run produced the expected summary files and validated the Slice 8D locator patch enough to unblock human review of whether Lane B can be launched next.

No Lane B run was launched. No evidence catalog update was made. No runtime mechanism code, eval runner, judge prompt, frontend, public API, durable mechanism state, new scoring, cross-mechanism comparison, or full AI Evaluation was introduced in this slice.

## Run Identity

| Field | Value |
| --- | --- |
| Run id | `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1` |
| Background job id | `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1` |
| Job status | `completed` |
| Exit code | `0` |
| Started at | `2026-05-17T09:22:31.719758Z` |
| Ended at | `2026-05-17T11:07:31.654879Z` |
| Run directory | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1` |
| Job log | `reading-companion-backend/state/job_registry/logs/bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1.log` |

## Commands Run

Preflight:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py tests/test_run_user_level_selective_comparison.py -q
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json
test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1
```

Execution:

```bash
cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- \
  --root . \
  --job-id bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1 \
  --task-ref TASK-SECOND-READER-MEMORY-PLANNING-SLICE8E-EXECUTION \
  --lane mechanism_eval \
  --purpose "Slice 8E Lane A retry1 bounded eval smoke: V2-only user-level selective legibility" \
  --cwd . \
  --run-dir eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1 \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/aggregate.json \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/report.md \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/llm_usage.json \
  --shell-command ".venv/bin/python eval/attentional_v2/run_user_level_selective_comparison.py --run-id attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1 --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json --mechanism-filter attentional_v2 --judge-mode llm --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004"
```

Polling and validation:

```bash
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py --job-id bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/aggregate.json
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/report.md
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/llm_usage.json
```

## Preflight Results

- Manifest smoke validator: passed.
- Focused tests: `22 passed, 6 warnings in 0.38s`.
- Background job registry preflight: no active jobs before launch.
- Registry JSON parse: passed.
- `git diff --check`: passed.
- Forbidden runtime/frontend/Long Span/evidence-catalog diff check: empty.
- Retry run directory absence check: passed.

## Expected Outputs

| Output | Status |
| --- | --- |
| `summary/aggregate.json` | present |
| `summary/report.md` | present |
| `summary/llm_usage.json` | present |
| `meta/selection.json` | present |
| `segments/huochu_shengming_de_yiyi_private_zh__segment_1.json` | present |
| Three note-case JSON files | present |

## Aggregate Checks

| Check | Result |
| --- | --- |
| `run_id` | `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1` |
| `segment_count` | `1` |
| `note_case_count` | `3` |
| Mechanisms | `["attentional_v2"]` |
| `exact_match_count` | `2` |
| `miss_count` | `1` |
| `note_recall` | `0.6667` |
| `span_candidate_count` | `2` |
| `duplicate_reaction_count` | `2` |
| `unlocatable_reaction_count` | `1` |
| `unlocatable_reaction_observation_count` | `3` |

Unlocatable diagnostic id:

```text
rx:Chapter_1:src:c1:p239@287-p239@287:retrospect:1
```

The unlocatable reaction id did not appear as a `best_reaction` or candidate match in any note-case result.

## Note-case Results

| Note case | Label | Counts for recall | Best reaction | Candidate count | Unlocatable diagnostics |
| --- | --- | --- | --- | --- | --- |
| `...e0002` | `exact_match` | `true` | `rx:Full_Content:src:c1:p13@0-p14@155:discern:9` | `1` | `1` unlocatable retrospect id |
| `...e0003` | `miss` | `false` | none | `0` | `1` unlocatable retrospect id |
| `...e0004` | `exact_match` | `true` | `rx:Full_Content:src:c1:p58@0-p62@195:highlight:38` | `1` | `1` unlocatable retrospect id |

## LLM Usage And Job Behavior

`summary/llm_usage.json` recorded:

- `request_count=213`
- `success_count=213`
- `error_count=0`
- `retry_count=12`
- `average_rpm=2.029`
- `peak_1m_rpm=5`
- `max_inflight=1`
- `provider_gate_wait_ms=0`
- `profile_gate_wait_ms=0`
- `quota_wait_ms=0`
- target: `MiniMax-M2.7-personal`

A fresh reading job occurred because the command did not use `--reuse-output-dir`.

The runner was launched with `--judge-mode llm`. In this bounded output, the three note cases resolved through deterministic exact-span or no-overlap paths, so no shortlisted non-exact candidate required the LLM judge path. The recorded LLM usage above is the fresh `attentional_v2` reader runtime usage.

## Guardrail Confirmation

- Lane B was not launched.
- The old failed Slice 8C run id was not reused.
- The failed Slice 8C run directory and logs were preserved.
- `reading-companion-backend/docs/evaluation/evidence_catalog.md` was not updated.
- `reading-companion-backend/docs/evaluation/evidence_catalog.json` was not updated.
- No runtime mechanism code was modified.
- No eval runners were modified further.
- No judge prompts were modified.
- No frontend, public API, or durable mechanism state was modified.
- No cross-mechanism comparison was run.
- No full AI Evaluation was run.
- No new metrics or scoring were added.
- Long Span vNext was not promoted to formal benchmark authority.

## Known Limitations

- This is a three-note-case Lane A smoke, not a full Lane A benchmark and not product-quality evidence.
- `note_recall=0.6667` belongs only to this bounded smoke scope.
- The single unlocatable retrospect diagnostic remains diagnostic evidence only; it was skipped, not matched.
- Lane B remains unrun after Slice 8C/8E.
- The run does not update the evidence catalog.

## Interpretation Guards

- Audit existence is not product quality.
- Retrieval availability is not utilization success.
- Visible reaction presence is not callback correctness.
- SourceRef count is not fidelity score.
- Trace existence is not planning quality.
- `slow_cycle_audit` existence is not slow-cycle quality.
- This report makes no product-quality claim.

## Recommendation

Lane A `_retry1` completed successfully after the Slice 8D compatibility patch. It is reasonable for a human reviewer to authorize a separately scoped Lane B bounded diagnostic launch next, using the previously accepted Slice 8C Lane B guardrails, if they agree that the Lane A prerequisite is satisfied.

Do not launch Lane B automatically from this report. Lane B should remain blocked until this Slice 8E post-run report is accepted and the next action is explicitly approved.
