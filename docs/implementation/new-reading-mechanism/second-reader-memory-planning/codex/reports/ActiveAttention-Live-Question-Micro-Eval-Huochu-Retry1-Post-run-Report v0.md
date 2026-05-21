# Active Attention Live-Question Micro Eval Huochu Retry1 Post-run Report v0

Date: 2026-05-21

## Executive Summary

Retry1 completed successfully after the reader-native Active Attention prompt repair. The diagnostic result is positive for the targeted behavior: `attentional_v2` created live-question-native Active Attention items, updated their `working_answer`, resolved answered questions, and retained one defensible open question.

This is diagnostic micro-eval evidence only. It does not update the evidence catalog, does not promote Long Span vNext to formal benchmark authority, and does not prove product quality.

## What Changed Before The Run

- Updated Read prompt version to `attentional_v2.read.v18`.
- Reframed Active Attention creation as a reader-native carry-forward question check: after reading a unit, ask whether the passage leaves the reader wanting to understand something later.
- Preserved the existing structured JSON op contract: `memory_uptake_ops[]` still drives deterministic normalization, SourceRef resolution, admission, and state apply.
- Updated prompt contract tests and mechanism docs.
- No schema change, no new metric, no judge-prompt change, no evidence-catalog update.

## Commands Run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest \
  tests/test_attentional_v2_state_ops.py \
  tests/test_attentional_v2_nodes.py \
  tests/test_attentional_v2_state_projection.py \
  tests/test_attentional_v2_slow_cycle.py \
  tests/test_attentional_v2_scaffold.py \
  tests/test_long_span_vnext.py -q

git diff --check
git diff --name-only -- \
  reading-companion-frontend \
  reading-companion-backend/docs/evaluation/evidence_catalog.md \
  reading-companion-backend/docs/evaluation/evidence_catalog.json

cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
cd reading-companion-backend && .venv/bin/python scripts/check_llm_targets_live.py

cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_run_ledger.py upsert \
  --run-id attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1 \
  --date 2026-05-21 \
  --surface active_attention_live_question_micro \
  --lane mechanism_eval_diagnostic \
  --status planned \
  --mechanism attentional_v2 \
  --dataset-or-manifest state/eval_local_datasets/diagnostic_micro/active_attention_live_question_huochu_20260521/split_manifest.json \
  --dataset-or-manifest state/eval_local_datasets/diagnostic_micro/active_attention_live_question_huochu_20260521/probe_plan.json \
  --run-dir eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1 \
  --job-id bgjob_active_attention_live_question_micro_huochu_20260521_retry1 \
  --catalog-status not_cataloged \
  --notes "Planned retry1 diagnostic micro eval after reader-native Active Attention prompt repair; diagnostic only, no evidence catalog update or product-quality claim." \
  --local-missing-allowed reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1

cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- \
  --root . \
  --job-id bgjob_active_attention_live_question_micro_huochu_20260521_retry1 \
  --task-ref TASK-SECOND-READER-ACTIVE-ATTENTION-MICRO-EVAL-RETRY1-20260521 \
  --lane mechanism_eval \
  --purpose "Active Attention reader-native prompt repair retry1 micro eval: huochu p45-p61" \
  --cwd . \
  --run-dir eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1 \
  --expected-output eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/summary/aggregate.json \
  --expected-output eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/summary/report.md \
  --expected-output eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/summary/llm_usage.json \
  --shell-command ".venv/bin/python eval/attentional_v2/run_long_span_vnext.py --run-id attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1 --manifest-path state/eval_local_datasets/diagnostic_micro/active_attention_live_question_huochu_20260521/split_manifest.json --memory-quality-probe-plan state/eval_local_datasets/diagnostic_micro/active_attention_live_question_huochu_20260521/probe_plan.json --segment-id active_attention_live_question_huochu_p45_p61__segment_1 --v2-only --workers 1 --judge-mode llm --output-attempts 1 --output-retry-sleep-seconds 0 --reaction-reuse-run-root \"\""

cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py \
  --job-id bgjob_active_attention_live_question_micro_huochu_20260521_retry1

cd reading-companion-backend && .venv/bin/python scripts/check_eval_llm_health.py \
  eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1
```

## Job And Outputs

- Job id: `bgjob_active_attention_live_question_micro_huochu_20260521_retry1`
- Job status: `completed`
- Exit code: `0`
- Started at: `2026-05-21T12:18:19.888557Z`
- Ended at: `2026-05-21T12:31:17.686641Z`
- Run directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1`
- Run-local audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/analysis/active_attention_lifecycle_audit/README.md`
- Expected outputs present: `summary/aggregate.json`, `summary/report.md`, `summary/llm_usage.json`

## Aggregate Results

- Probe plan: `active_attention_live_question_micro_huochu_20260521`
- Probe selection method: `semantic_boundary_with_distance_reference`
- Mechanism keys: `["attentional_v2"]`
- Memory Quality probe count: `5`
- Memory Quality window count: `1`
- Memory snapshot basis: `full_probe_time_memory_state` for all `5` probes
- Average Memory Quality score: `3.85`
- Reaction audit source: `fresh_judge`
- Memory Quality source: `fresh_judge`
- Visible reactions: `16`
- Grounded callbacks: `0`
- Weak callbacks: `2`
- False visible integrations: `1`
- Local-only reactions: `13`

## Active Attention Lifecycle Verdict

The repair appears effective for this targeted micro window.

- The previous failed run had empty probe-time Active Attention and final legacy `statement`-only items.
- Retry1 produced `3` final Active Attention items, all with `question_from`, `driving_question`, `working_answer`, and no statement-only payload.
- Read audit observed `9` Active Attention ops: `3` creates, `4` updates, and `2` resolves.
- Final statuses:
  - `psychological_reaction_stages`: `answered`
  - `emotional_suppression_survival`: `answered`
  - `third_stage_uncertainty`: `open`
- Probe snapshots showed Active Attention present at all `5` probe points.
- `source_refs` grounded each question source; `answer_source_refs` appeared for updated / resolved answers.
- Durable state also captured related material: `concept_registry` has `4` entries and `thread_trace` has `1` entry.

The remaining open item is defensible: the excerpt raises the question of what comes after emotional death / protective numbness, but does not fully answer the later meaning-reconstruction arc inside the micro window.

## LLM Health And Usage

- Live target preflight: `2 / 2` MiniMax targets healthy.
- Eval health check: `ok`.
- Total LLM traces: `26`.
- Successes: `26`.
- Errors: `0`.
- Retries: `0`.
- Fallback traces: `0`.
- Targets used:
  - `MiniMax-M2.7-personal`: `3` requests.
  - `MiniMax-M2.7-personal-2`: `23` requests.

## Caveats

- This was one deliberately selected diagnostic micro excerpt, not broad product-quality proof.
- Some emitted source quotes required fallback unit-span resolution, so source-quote precision remains a useful follow-up area.
- Final active items did not link back through `linked_concept_keys` / `linked_thread_keys`, even though concept/thread durable stores captured related material.
- Callback/FVI still exposed reaction-layer issues: `0` grounded callbacks, `2` weak callbacks, and `1` false visible integration.
- No evidence catalog update was made.
- Long Span vNext remains diagnostic, not formal benchmark authority.
