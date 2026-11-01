# Eval1 Full Active Evaluation Post-Slice8H Aborted Run Report v0

## Summary

Eval-1 was stopped before completion. The current active background job `bgjob_full_long_span_vnext_post_slice8h_20260518_parallel5` was terminated with `SIGTERM` and is now recorded as `abandoned`. No Lane A reuse shards were launched from this producer output.

The stopped run is not valid full-evaluation evidence. Its partial Long Span output advanced through runtime fallback during LLM call failures, produced no summary outputs, and must not be reused as the source for Lane A user-level shard evaluation.

## Jobs

| Job id | Run id | Intended scope | Final status | Notes |
| --- | --- | --- | --- | --- |
| `bgjob_full_user_level_selective_post_slice8h_20260518` | `attentional_v2_full_user_level_selective_post_slice8h_20260518` | conservative Lane A full active user-level run | `abandoned`, exit `-15` | stopped during the later reuse/parallelism correction; partial output preserved |
| `bgjob_full_long_span_vnext_post_slice8h_20260518` | `attentional_v2_full_long_span_vnext_post_slice8h_20260518` | conservative Lane B full active Long Span run | `abandoned`, exit `-15` | stopped during the later reuse/parallelism correction; partial output preserved |
| `bgjob_full_long_span_vnext_post_slice8h_20260518_parallel5` | `attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5` | optimized Lane B producer, `attentional_v2` only, `--workers 5` | `abandoned`, exit `-15` | stopped after LLM-health investigation showed timeout/fallback progress and no usable summaries |

Latest confirmed background-job registry state after stopping: no active jobs.

## Output State

The optimized Long Span producer run directory exists at:

`reading-companion-backend/eval/runs/attentional_v2/attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5`

Observed outputs:

- `meta/selected_windows.json`: present.
- `summary/aggregate.json`: missing.
- `summary/report.md`: missing.
- `summary/llm_usage.json`: missing.

Because the expected summary outputs are missing, the run is incomplete and invalid for evaluation interpretation or Lane A output reuse.

## LLM Health Findings

Static inspection of the optimized producer's local `_runtime/llm_standard.jsonl` traces found:

- total LLM trace rows: `919`
- successful rows: `465`
- error rows: `454`
- error breakdown: `network_blocked=334`, `llm_timeout=120`
- provider distribution: `MiniMax-M2.7-personal-2=696`, `MiniMax-M2.7-personal=223`
- recent five-hour window from the final completed trace: `90 / 90` rows were `llm_timeout`
- error failover pattern: repeated attempts stayed on the same selected provider for many failures instead of producing a healthy cross-target recovery

Runtime activity also recorded LLM fallback events:

- `huochu_shengming_de_yiyi_private_zh__segment_1`: `32` `network_blocked` fallbacks and `14` `llm_timeout` fallbacks.
- `mangge_zhi_dao_private_zh__segment_1`: `32` `network_blocked` fallbacks and `14` `llm_timeout` fallbacks.
- `nawaer_baodian_private_zh__segment_1`: completed without observed fallback in this partial run.
- `value_of_others_private_en__segment_1`: `15` `network_blocked` fallbacks.
- `xidaduo_private_zh__segment_1`: `32` `network_blocked` fallbacks and `13` `llm_timeout` fallbacks.

These facts explain why paragraph-position progress estimates were misleading: several windows continued moving through deterministic fallback after LLM failures rather than producing normal model-backed reading evidence.

## Interpretation

This aborted Eval-1 attempt supports only an operational finding:

- current full-eval execution needs an LLM-health / fallback guard before another broad run;
- partial producer outputs from `attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5` must not be used as valid Long Span evidence or as the Lane A reuse source;
- no product-quality conclusion can be drawn from this aborted attempt.

This report does not promote Long Span vNext to formal benchmark authority and does not update the evidence catalog.

## Recommended Follow-up

Before retrying Eval-1, prepare a separate brief or patch plan for one or more small guardrails:

- a live LLM preflight that verifies both configured MiniMax targets can complete real text-generation calls before launch;
- eval-time fail-fast behavior when LLM fallbacks exceed a small threshold or when no successful LLM calls occur for a bounded interval;
- clearer provider failover or abort behavior for repeated `network_blocked` / `llm_timeout` errors;
- a runner or registry health check that distinguishes model-backed progress from deterministic fallback progress.

Any retry should use fresh run ids and should not reuse the aborted producer directory as valid evidence.

## Guardrails Preserved

- No new eval was launched after stopping the job.
- No Lane A reuse shards were launched.
- No evidence catalog update was made.
- No runtime mechanism code was changed.
- No eval runners were modified.
- No judge prompts were modified.
- No frontend, public API, or durable mechanism state was changed.
- No new metrics or scoring were added.
- No Long Span vNext formal-authority promotion was made.
- No product-quality proof is claimed.
