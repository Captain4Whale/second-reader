# Slice 8F: Lane B Bounded Diagnostic Smoke Post-run Report

## Summary

Slice 8F ran the bounded Lane B diagnostic smoke from the accepted Slice 8C plan after the Slice 8E Lane A `_retry1` report was accepted.

The run completed successfully as a registered background job. It remained `attentional_v2` only, used one selected `huochu` Memory Quality window, reused semantic-probe source outputs, performed a fresh Memory Quality rejudge, copied the reaction audit from the source run, and did not launch reading jobs.

This report is diagnostic execution evidence only. It is not product-quality proof, does not promote Long Span vNext to formal benchmark authority, and does not update the evidence catalog.

## Scope

- Lane: Lane B / Long Span MQ / Callback / FVI diagnostic phase 1.
- Mechanism: `attentional_v2` only.
- Run id: `attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`.
- Background job id: `bgjob_minimal_eval_suite_lane_b_smoke_20260517`.
- Segment/window selection: `huochu_shengming_de_yiyi_private_zh__segment_1`, `--window-limit 1`.
- Memory Quality source policy: reused semantic-probe source outputs from `attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504`, then fresh-rejudged Memory Quality.
- Reaction audit policy: copied from the Memory Quality source run; `--rerun-reaction-audit` was omitted.
- Judge mode: `llm`.

## Commands Run

Preflight:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py tests/test_run_user_level_selective_comparison.py -q
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json
test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517
```

Source-run metadata check:

```bash
node - <<'NODE'
const fs = require('fs');
const p = 'reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504/summary/aggregate.json';
const a = JSON.parse(fs.readFileSync(p, 'utf8'));
if (a.probe_plan_id !== 'memory_quality_semantic_probe_plan_20260504') throw new Error(a.probe_plan_id);
if (a.probe_selection_method !== 'semantic_boundary_with_distance_reference') throw new Error(a.probe_selection_method);
console.log(JSON.stringify({probe_plan_id:a.probe_plan_id, probe_selection_method:a.probe_selection_method}));
NODE
```

Launch:

```bash
cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- \
  --root . \
  --job-id bgjob_minimal_eval_suite_lane_b_smoke_20260517 \
  --task-ref TASK-SECOND-READER-MEMORY-PLANNING-SLICE8F-EXECUTION \
  --lane mechanism_eval \
  --purpose "Slice 8F Lane B bounded diagnostic smoke: V2-only Long Span MQ Callback FVI" \
  --cwd . \
  --run-dir eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517 \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/aggregate.json \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/report.md \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/llm_usage.json \
  --shell-command ".venv/bin/python eval/attentional_v2/run_long_span_vnext.py --run-id attentional_v2_minimal_eval_suite_lane_b_smoke_20260517 --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json --memory-quality-probe-plan eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json --memory-quality-source-run-root eval/runs/attentional_v2/attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504 --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 --window-limit 1 --v2-only --workers 1 --judge-mode llm"
```

Polling and validation:

```bash
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py --job-id bgjob_minimal_eval_suite_lane_b_smoke_20260517
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/aggregate.json
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/report.md
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/llm_usage.json
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/memory_quality_results.jsonl
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/reaction_audit_results.jsonl
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/reaction_window_summaries.jsonl
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/meta/selected_windows.json
test -f reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/meta/output_sourcing.json
```

## Job Status

- Job id: `bgjob_minimal_eval_suite_lane_b_smoke_20260517`.
- Job status: `completed`.
- Exit code: `0`.
- Started: `2026-05-17T11:39:24.773270Z`.
- Ended: `2026-05-17T11:40:54.920938Z`.
- Launcher log: `reading-companion-backend/state/job_registry/logs/bgjob_minimal_eval_suite_lane_b_smoke_20260517.launcher.log`.
- Job log: `reading-companion-backend/state/job_registry/logs/bgjob_minimal_eval_suite_lane_b_smoke_20260517.log`.

## Run Directory And Outputs

Run directory:

```text
reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517
```

Required outputs present:

- `meta/selected_windows.json`
- `meta/output_sourcing.json`
- `summary/aggregate.json`
- `summary/report.md`
- `summary/llm_usage.json`
- `summary/memory_quality_results.jsonl`
- `summary/reaction_audit_results.jsonl`
- `summary/reaction_window_summaries.jsonl`

Missing required outputs:

- None.

Generated run outputs are local ignored eval artifacts and were not force-added to git.

## Aggregate Checks

From `summary/aggregate.json` and `meta/output_sourcing.json`:

| Check | Result |
| --- | --- |
| `mechanism_keys` | `["attentional_v2"]` |
| `probe_plan_id` | `memory_quality_semantic_probe_plan_20260504` |
| `probe_selection_method` | `semantic_boundary_with_distance_reference` |
| `memory_quality.window_count` | `1` |
| `memory_quality.probe_count` | `5` |
| `memory_quality_source` | `fresh_judge` |
| `reaction_audit_source` | `copied_from_memory_quality_source_run` |
| `meta/output_sourcing.json.fresh_task_count` | `0` |
| selected window count | `1` |
| selected segment | `huochu_shengming_de_yiyi_private_zh__segment_1` |
| Memory Quality result rows | `5`, all for `huochu_shengming_de_yiyi_private_zh__segment_1` |

## Memory Quality Summary

- Judge contract: `scale_v3_structural_signal_aware`.
- Probe count: `5`.
- Window count: `1`.
- Average overall Memory Quality score: `3.700`.
- Window: `huochu_shengming_de_yiyi_private_zh__segment_1`.
- Per-probe overall scores:
  - Probe 1 near 20%: `3.250`.
  - Probe 2 near 40%: `3.750`.
  - Probe 3 near 60%: `4.000`.
  - Probe 4 near 80%: `3.750`.
  - Probe 5 window end: `3.750`.

These values are diagnostic smoke outputs, not product-quality claims.

## Callback / FVI Diagnostic Summary

Reaction audit was copied unchanged from the Memory Quality source run. The copied aggregate contains:

- Total visible reactions: `1170`.
- Callback attempts: `131`.
- Grounded callbacks: `99`.
- Weak callbacks: `31`.
- False visible integrations: `1`.
- Judge-unavailable labels: `0`.
- Native surfaced evidence counts: prior_link `68`, outside_link `0`, search_intent `1`.

For the selected `huochu` window inside the copied reaction audit:

- Total visible reactions: `267`.
- Grounded callbacks: `29`.
- Weak callbacks: `9`.
- False visible integrations: `0`.
- Judge-unavailable labels: `0`.
- Native surfaced evidence counts: prior_link `12`, outside_link `0`, search_intent `1`.

Validation observation:

- `summary/reaction_window_summaries.jsonl` contains `5` rows and `summary/reaction_audit_results.jsonl` contains `1170` rows because the runner copied the full source-run reaction audit unchanged.
- This means the copied reaction audit evidence is broader than the one selected Memory Quality window, even though `memory_quality.window_count=1` and `fresh_task_count=0`.
- This was recorded as a diagnostic observation, not fixed in Slice 8F, because the accepted execution plan required no eval-runner changes and explicitly used copied reaction audit.

## Reading Jobs And Judge Calls

- Reading jobs occurred: no.
- Evidence: `meta/output_sourcing.json.fresh_task_count=0`; output mode for the selected window was `memory_quality_rejudge_source_output`.
- Memory Quality judge calls occurred: yes, `5` fresh LLM judge requests.
- Fresh reaction-audit judge calls occurred: no; reaction audit was copied from the source run.
- Cross-mechanism comparison occurred: no.
- Full AI Evaluation occurred: no.

## LLM Usage

From `summary/llm_usage.json`:

- Requests: `5`.
- Successes: `5`.
- Errors: `0`.
- Retries: `0`.
- Average RPM: `3.356`.
- Peak 1m RPM: `4`.
- Peak 5m RPM: `1`.
- Average inflight: `1`.
- Max inflight: `1`.
- Provider/profile/quota wait: `0 ms`.
- Profile: `eval_judge_high_trust`, `5` requests.
- Targets: `MiniMax-M2.7-personal` with `3` requests and `MiniMax-M2.7-personal-2` with `2` requests.

## Evidence Catalog And Diff Guardrails

- `reading-companion-backend/docs/evaluation/evidence_catalog.md` was not updated.
- `reading-companion-backend/docs/evaluation/evidence_catalog.json` was not updated.
- Runtime mechanism code under `reading-companion-backend/src/attentional_v2/` was not modified.
- Frontend code was not modified.
- Eval runners were not modified.
- Judge prompts were not modified.
- Long Span vNext remains diagnostic phase 1, not formal benchmark authority.

The forbidden diff check was run during preflight and returned empty output:

```bash
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json
```

## Known Limitations

- This was a bounded diagnostic smoke, not a full evaluation.
- Lane B reused source outputs and copied reaction audit artifacts; it did not produce a fresh full reaction-audit pass.
- Copied reaction audit rows cover the full source run's five windows, while fresh Memory Quality rejudge covers one selected window. Consumers should not interpret the reaction audit files as newly filtered one-window artifacts.
- Memory Quality scores, callback counts, FVI counts, and native surfaced evidence counts are diagnostic smoke outputs only.
- No evidence catalog entry was created; any catalog update requires separate human review.

## Interpretation Guards

- Audit existence is not product quality.
- Retrieval availability is not utilization success.
- Visible reaction presence is not callback correctness.
- SourceRef count is not fidelity score.
- Trace existence is not planning quality.
- `slow_cycle_audit` existence is not slow-cycle quality.
- Memory Quality smoke scores are not a formal benchmark promotion.
- Copied reaction audit presence is not evidence of fresh Callback / FVI judging.

## Recommendation

The bounded Lane B diagnostic smoke can be considered executed for Slice 8F after human review of this report. The Minimal Eval Suite smoke now has:

- Lane A `_retry1` successful execution evidence from Slice 8E.
- Lane B bounded diagnostic execution evidence from Slice 8F.

Recommended next gate:

- Human review of this Slice 8F report.
- Do not update the evidence catalog, promote Long Span vNext to formal authority, or start another eval slice until this report is accepted.
- If the reviewer wants stricter Lane B reaction-audit one-window artifacts, create a separate small follow-up brief to clarify copied reaction-audit filtering or reporting semantics before any catalog entry.
