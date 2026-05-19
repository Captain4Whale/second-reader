# Eval-1: Full Active Evaluation Post-Slice8H Retry1 High-parallel - Post-run Report v0

## Executive Summary

Eval-1 Retry1 completed the current active evaluation lanes for `attentional_v2` with high-parallel registered jobs and output reuse.

What ran:

- Lane B / Long Span vNext: 5 independent `attentional_v2` producer jobs, one per active semantic-probe window, each with fresh reading output, fresh Memory Quality judging, and fresh reaction-audit judging.
- Lane A / Local User-level Selective Legibility: 5 segment-level reuse shards, each launched only after the matching Lane B producer reached terminal success and passed strict LLM health validation.

What did not run:

- No `iterator_v1`.
- No cross-mechanism comparison.
- No old `excerpt_surface_v1_1`, target-centered accumulation, or historical benchmark surfaces.
- No Reader Reaction Value / Insight and Clarification addendum.
- No evidence catalog update.
- No runtime mechanism, eval-runner, judge-prompt, frontend, public API, or durable-state change.

Job outcome:

- Lane B: completed successfully for all 5 windows.
- Lane A: completed successfully for all 5 reuse shards.
- Failed jobs: none in this Retry1 run.

Interpretation boundary: this is full active evaluation output for human review, not an automatic product-quality proof, not an automatic evidence-catalog update, and not a Long Span vNext formal-authority promotion.

## Preflight

Commands run before launch:

```bash
git status --short
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
cd reading-companion-backend && .venv/bin/python scripts/check_llm_targets_live.py
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_llm_health.py tests/test_llm_gateway.py tests/test_run_user_level_selective_comparison.py tests/test_long_span_vnext.py -q
cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_catalog.py --check
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

Preflight result:

- Repo started clean.
- No active background jobs were present before launch.
- Both configured MiniMax targets passed live health preflight.
- Minimal eval inventory smoke passed.
- Targeted tests passed: `99 passed, 6 warnings`.
- Catalog check passed before execution.
- Registry JSON parsed.
- `git diff --check` passed.
- Forbidden code/catalog diff check returned empty output.
- Fresh `20260519` target run directories were absent before launch.

## Execution Plan Used

Old aborted outputs were preserved and not reused, especially:

- `attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5`

Prior stopped jobs remain preserved as operational failure evidence only:

- `bgjob_full_user_level_selective_post_slice8h_20260518` (`abandoned`)
- `bgjob_full_long_span_vnext_post_slice8h_20260518` (`abandoned`)
- `bgjob_full_long_span_vnext_post_slice8h_20260518_parallel5` (`abandoned`)

No output from those stopped jobs was reused in Retry1.

Lane B producer command shape:

```bash
cd reading-companion-backend && .venv/bin/python eval/attentional_v2/run_long_span_vnext.py \
  --run-id attentional_v2_eval1_long_span_post_slice8h_20260519_<slug> \
  --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json \
  --memory-quality-probe-plan eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json \
  --v2-only \
  --segment-id <segment_id> \
  --workers 1 \
  --output-attempts 1 \
  --output-retry-sleep-seconds 0 \
  --judge-mode llm
```

Lane A reuse shard command shape:

```bash
cd reading-companion-backend && .venv/bin/python eval/attentional_v2/run_user_level_selective_comparison.py \
  --run-id attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_<slug> \
  --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json \
  --mechanism-filter attentional_v2 \
  --judge-mode llm \
  --segment-id <segment_id> \
  --reuse-output-dir eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_<slug>/outputs/<segment_id>/attentional_v2
```

Health gate command run for all producer outputs:

```bash
cd reading-companion-backend && .venv/bin/python scripts/check_eval_llm_health.py \
  eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu \
  eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge \
  eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer \
  eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others \
  eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo
```

Health result:

- `status=ok`
- `checked_count=5`
- `failed_count=0`
- total producer traces checked by shard: `huochu=225`, `mangge=488`, `nawaer=88`, `value_of_others=123`, `xidaduo=347`
- all producer traces had `error_count=0`
- all producer outputs had `fallback_count=0`

## Job Registry

| Lane | Slug | Job id | Status | Start UTC | End UTC |
| --- | --- | --- | --- | --- | --- |
| Lane B | `huochu` | `bgjob_eval1_long_span_post_slice8h_20260519_huochu` | `completed` / `0` | `2026-05-19T00:33:24.477206Z` | `2026-05-19T02:26:52.956191Z` |
| Lane B | `mangge` | `bgjob_eval1_long_span_post_slice8h_20260519_mangge` | `completed` / `0` | `2026-05-19T00:33:24.511628Z` | `2026-05-19T04:25:11.734790Z` |
| Lane B | `nawaer` | `bgjob_eval1_long_span_post_slice8h_20260519_nawaer` | `completed` / `0` | `2026-05-19T00:33:24.560916Z` | `2026-05-19T01:02:23.510385Z` |
| Lane B | `value_of_others` | `bgjob_eval1_long_span_post_slice8h_20260519_value_of_others` | `completed` / `0` | `2026-05-19T00:33:24.600470Z` | `2026-05-19T01:18:20.686480Z` |
| Lane B | `xidaduo` | `bgjob_eval1_long_span_post_slice8h_20260519_xidaduo` | `completed` / `0` | `2026-05-19T00:33:24.635891Z` | `2026-05-19T03:52:27.470095Z` |
| Lane A | `huochu` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_huochu` | `completed` / `0` | `2026-05-19T02:30:26.885721Z` | `2026-05-19T02:35:55.776022Z` |
| Lane A | `mangge` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_mangge` | `completed` / `0` | `2026-05-19T04:25:12.132014Z` | `2026-05-19T04:27:14.527855Z` |
| Lane A | `nawaer` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_nawaer` | `completed` / `0` | `2026-05-19T01:03:44.622442Z` | `2026-05-19T01:05:58.188836Z` |
| Lane A | `value_of_others` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_value_of_others` | `completed` / `0` | `2026-05-19T01:20:00.136476Z` | `2026-05-19T01:27:13.950215Z` |
| Lane A | `xidaduo` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_xidaduo` | `completed` / `0` | `2026-05-19T03:53:09.265858Z` | `2026-05-19T03:56:12.741268Z` |

After completion, `scripts/check_background_jobs.py` reported no active background jobs.

Run directories created by Retry1:

- Lane B: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_{huochu,mangge,nawaer,value_of_others,xidaduo}`
- Lane A: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_{huochu,mangge,nawaer,value_of_others,xidaduo}`

## Lane A Results

Dataset and manifest:

- Dataset path: `state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422`
- Active dataset boundary: `20260422`
- Manifest path: `eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- Mechanism scope: `attentional_v2` only
- Output source: reused matching Lane B producer `outputs/<segment_id>/attentional_v2`
- Fresh reading jobs in Lane A reuse shards: no
- Judge calls in Lane A: yes, `61` LLM judge requests

| Slug | Note cases | Exact | Focused hit | Incidental cover | Miss | Note recall | Unlocatable reactions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `huochu` | 40 | 7 | 8 | 2 | 23 | 0.3750 | 1 |
| `mangge` | 25 | 2 | 7 | 0 | 16 | 0.3600 | 0 |
| `nawaer` | 23 | 8 | 2 | 2 | 11 | 0.4348 | 1 |
| `value_of_others` | 94 | 10 | 18 | 4 | 62 | 0.2979 | 1 |
| `xidaduo` | 20 | 1 | 7 | 0 | 12 | 0.4000 | 0 |
| **Total** | **202** | **28** | **42** | **8** | **124** | **0.3465** | **3** |

Lane A aggregate checks:

- Shard count: `5`
- Total `segment_count`: `5` at report-level aggregation
- Total `note_case_count`: `202`
- Mechanisms: only `attentional_v2`
- No `iterator_v1` output was produced.
- Strict source-span matching semantics remained runner-owned:
  - no text-similarity candidate admission
  - no semantic-similarity candidate admission
  - exact match remains identical canonical char span
  - focused hit counts toward recall
  - incidental cover remains supporting-only
- Unlocatable reactions remained diagnostics only and were not counted as matches.

Unlocatable diagnostic ids:

- `rx:Chapter_1:src:c1:p239@287-p239@287:retrospect:1`
- `rx:Chapter_1:src:c1:p99@193-p99@193:retrospect:1`
- `rx:Chapter_1:src:c1:p78@176-p78@176:retrospect:1`

## Lane B Results

Dataset and probe plan:

- Dataset path: `state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422`
- Manifest path: `eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- Probe plan: `eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json`
- Probe plan id: `memory_quality_semantic_probe_plan_20260504`
- Probe selection method: `semantic_boundary_with_distance_reference`
- Mechanism scope: `attentional_v2` only
- Memory Quality source: `fresh_judge`
- Reaction audit source: `fresh_judge`
- Fresh reading jobs: yes, `5` producer tasks
- Fresh reaction-audit judging: yes

| Slug | MQ windows | Probes | Avg MQ | Visible reactions | Grounded callbacks | Weak callbacks | FVI | Local only |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `huochu` | 1 | 5 | 3.70 | 150 | 19 | 9 | 0 | 122 |
| `mangge` | 1 | 5 | 3.10 | 270 | 43 | 13 | 0 | 214 |
| `nawaer` | 1 | 5 | 3.65 | 40 | 6 | 4 | 1 | 29 |
| `value_of_others` | 1 | 5 | 3.65 | 58 | 11 | 9 | 1 | 37 |
| `xidaduo` | 1 | 5 | 3.00 | 211 | 47 | 25 | 0 | 139 |
| **Total** | **5** | **25** | **3.42** | **729** | **126** | **60** | **2** | **541** |

Lane B aggregate checks:

- `mechanism_keys == ["attentional_v2"]` for every shard.
- `memory_quality.window_count == 1` per shard, `5` report-level total.
- `memory_quality.probe_count == 5` per shard, `25` report-level total.
- `memory_quality_source == "fresh_judge"` for every shard.
- `reaction_audit_source == "fresh_judge"` for every shard.
- `judge_unavailable_count == 0` across all shards.
- `meta/output_sourcing.json` was present for every shard and reported fresh sourcing.
- Required output files were present for every shard:
  - `summary/aggregate.json`
  - `summary/report.md`
  - `summary/llm_usage.json`
  - `summary/memory_quality_results.jsonl`
  - `summary/reaction_audit_results.jsonl`
  - `summary/reaction_window_summaries.jsonl`
  - `meta/selected_windows.json`
  - `meta/output_sourcing.json`

## Parallelization

Parallelization used:

- Registered job parallelism: launched 5 independent Lane B producer jobs together.
- Per-producer internal workers: `--workers 1`, because each producer was already sharded to one semantic-probe window.
- Dependent Lane A shards: launched per segment only after the matching producer completed and passed strict LLM health validation.
- Maximum active registered jobs: `5`.

Why Lane A was not launched before its producer:

- Lane A reuse must point at the matching producer's completed `outputs/<segment_id>/attentional_v2` directory.
- Fallback-backed or incomplete producer outputs are invalid as eval evidence.
- The user-level runner has segment filters but no authoritative full-run merge/report path, so Lane A aggregation is report-level across 5 shard summaries.

Both configured MiniMax targets were used through the existing pooled target configuration. This report records target ids and counts only; no secrets are included.

## LLM Usage

Total LLM usage across Lane A and Lane B:

- Requests: `1332`
- Successes: `1332`
- Errors: `0`
- Retries: `47`
- Quota wait: `0 ms`
- Provider gate wait: `0 ms`
- Profile gate wait: `0 ms`

By lane:

| Lane | Requests | Successes | Errors | Retries |
| --- | ---: | ---: | ---: | ---: |
| Lane A user-level judge | 61 | 61 | 0 | 2 |
| Lane B Long Span producer + judges | 1271 | 1271 | 0 | 45 |
| **Total** | **1332** | **1332** | **0** | **47** |

By profile:

| Profile | Requests | Successes | Errors | Retries |
| --- | ---: | ---: | ---: | ---: |
| `runtime_reader_default` | 1200 | 1200 | 0 | 38 |
| `eval_judge_high_trust` | 132 | 132 | 0 | 9 |

By target:

| Target | Requests | Successes | Errors | Retries |
| --- | ---: | ---: | ---: | ---: |
| `MiniMax-M2.7-personal` | 1066 | 1066 | 0 | 17 |
| `MiniMax-M2.7-personal-2` | 266 | 266 | 0 | 30 |

Some successful calls used same-tier failover after retryable provider failures. This is gateway-level target failover and not runtime `llm_fallback`. Strict eval health reported `fallback_count=0` for all producer outputs.

## Guardrails

Confirmed:

- `attentional_v2` only.
- No `iterator_v1`.
- No historical or discontinued benchmark surfaces.
- No cross-mechanism comparison.
- No Reader Reaction Value / Insight and Clarification judge.
- No runtime mechanism code change.
- No eval-runner change.
- No judge-prompt change.
- No frontend, public API, or durable-state change.
- No evidence catalog update.
- No Long Span vNext formal-authority promotion.
- No product-quality claim before human review.

Interpretation guards preserved:

- Audit existence is not product quality.
- Retrieval availability is not utilization success.
- Visible reaction presence is not callback correctness.
- SourceRef count is not fidelity score.
- Trace existence is not planning quality.
- `slow_cycle_audit` existence is not slow-cycle quality.

## Known Limitations

- Lane A and Lane B are report-level aggregations across independently launched shard summaries, not runner-emitted merged root summaries.
- Lane B is still Long Span vNext diagnostic / phase-1 evaluation. It is not automatically formal benchmark authority.
- This run does not include Reader Reaction Value / Insight and Clarification; that remains a possible future addendum only.
- This report does not update `evidence_catalog.md` or `evidence_catalog.json`.
- Human review is still required before cataloging results, promoting authority, or making product-quality claims.

## Post-run Validation

Commands run after execution:

```bash
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
cd reading-companion-backend && .venv/bin/python scripts/check_eval_llm_health.py eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json
```

Validation result:

- Background job checker reported no active jobs.
- Strict LLM health check passed for all 5 Long Span producer run dirs.
- Registry JSON parsed.
- `git diff --check` passed.
- Forbidden runtime/frontend/eval-runner/evidence-catalog diff check returned empty output.

## Recommended Next Step

Human review of this Eval-1 Retry1 post-run report.

Potential follow-ups after review:

- Decide whether this full active Eval-1 run should receive an evidence catalog entry.
- Decide whether Long Span vNext remains diagnostic-only or needs a separate promotion brief.
- Decide whether to scope a future Reader Reaction Value / Insight and Clarification addendum.
- Do not automatically launch broader eval, update the catalog, or promote formal authority without separate approval.
