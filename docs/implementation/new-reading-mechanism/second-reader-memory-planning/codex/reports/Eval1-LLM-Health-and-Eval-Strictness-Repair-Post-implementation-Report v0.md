# Eval1 LLM Health and Eval Strictness Repair Post-implementation Report v0

## Executive Summary

This patch repairs the immediate Eval-1 safety gap exposed by the aborted post-Slice8H full active evaluation attempt.

The core change is policy separation:

- Evaluation runners now treat degraded LLM-backed reading outputs as invalid evidence and fail fast before judging or reuse.
- Product/runtime reading behavior remains graceful by default: `llm_fallback` can still preserve a user-facing run from hard failure, but those fallbacks are now easier to diagnose and are not acceptable as eval evidence.
- The shared LLM gateway can now fail over within the same configured target tier after `network_blocked` / `llm_timeout` style provider failures instead of staying stuck on one selected target.

No full eval was run in this patch. No Eval-1 retry was launched. No evidence catalog update was made.

## Failure Context

The stopped optimized Eval-1 Long Span producer (`attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5`) produced partial local artifacts but no valid summary outputs.

The preserved traces showed:

- `919` local LLM trace rows.
- `465` successful rows.
- `454` error rows.
- Error breakdown: `network_blocked=334`, `llm_timeout=120`.
- Recent trace tail: `90 / 90` rows in the final window were `llm_timeout`.
- Runtime activity included `llm_fallback` events, so paragraph-position progress was not reliable model-backed evaluation progress.

This means the aborted run is operational failure evidence only. It must not be reused as Long Span evidence or as Lane A source-output evidence.

## Changes Implemented

### Eval Strict Mode

Added `eval/attentional_v2/llm_health.py`.

The helper scans reading output traces and activity logs for:

- `llm_fallback` activity events.
- trace files with no successful LLM calls.
- recent consecutive `network_blocked` / `llm_timeout` streaks.

The active eval runners now call this strict health gate when producing or reusing `attentional_v2` reading outputs:

- `eval/attentional_v2/run_user_level_selective_comparison.py`
- `eval/attentional_v2/run_long_span_vnext.py`

If an output is unhealthy, the runner raises before downstream judge or reuse can turn it into eval evidence.

### Gateway Same-tier Failover

Updated `src/reading_runtime/llm_gateway.py`.

When a profile is selected from a multi-target tier and the selection was not a manual override, a non-quota provider failure can now try the next reachable target in the same tier. The actual target and model used are recorded in LLM traces.

Manual/env overrides remain pinned.

### Preflight and Operator Diagnostics

Added:

- `scripts/check_llm_targets_live.py`
- `scripts/check_eval_llm_health.py`

`check_llm_targets_live.py` performs a short live request against configured Anthropic-compatible targets and reports target-level health without printing credentials or response text.

`check_eval_llm_health.py` summarizes strict-eval LLM health for run roots or output dirs so operators do not have to infer health from PID liveness alone.

## Product Runtime Posture

Product runtime was not changed to fail fast on every fallback.

That is intentional: ordinary reading runs may still degrade rather than crash immediately. The key repaired boundary is that fallback-backed product outputs are visible diagnostics and are not acceptable as valid eval reading outputs.

## Tests and Validation

Targeted tests added or updated:

- gateway same-tier timeout failover
- strict eval health pass/fail cases
- existing active user-level selective runner tests
- existing Long Span vNext runner tests

Commands run:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_llm_health.py tests/test_llm_gateway.py::test_same_tier_failover_tries_second_target_after_timeout tests/test_run_user_level_selective_comparison.py tests/test_long_span_vnext.py -q
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_llm_health.py tests/test_llm_gateway.py tests/test_run_user_level_selective_comparison.py tests/test_long_span_vnext.py -q
cd reading-companion-backend && .venv/bin/python scripts/check_llm_targets_live.py
cd reading-companion-backend && .venv/bin/python scripts/check_eval_llm_health.py eval/runs/attentional_v2/attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5 | python3 -m json.tool | sed -n '1,160p'
cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_catalog.py --check
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-frontend reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json reading-companion-backend/src/attentional_v2
```

Result:

- `39 passed`
- `99 passed`
- live target preflight returned `status=ok` for both configured targets without printing credentials
- eval health checker correctly classified the aborted optimized producer as `failed` with fallback events and a retryable error streak
- catalog check passed
- registry JSON parse passed
- `git diff --check` passed
- forbidden frontend / evidence-catalog / runtime mechanism diff check returned empty

Final validation commands are recorded in the task closeout.

## Explicit Non-actions

- No full eval was run.
- No Eval-1 retry was launched.
- No eval run directories were created by this patch.
- No evidence catalog update was made.
- No new metrics or scoring were added.
- No Long Span vNext formal-authority promotion was made.
- No judge prompts were changed.
- No frontend, public API, or durable mechanism state was changed.
- No product-quality claim is made from this repair.

## Impact and Scope

This patch affects both evaluation and shared LLM invocation:

- Evaluation impact: active eval runners fail fast instead of judging or reusing fallback-backed `attentional_v2` outputs.
- Shared gateway impact: non-manual multi-target profiles can use same-tier failover during one invocation.
- Product runtime impact: product reads may still fallback, but these fallback events are now easier to detect through output health tooling.

The original Eval-1 failure was therefore not limited to the eval harness. It exposed a shared gateway failover weakness plus an eval-specific evidence-validity gap. Product runtime was less directly affected because graceful fallback was intentional, but the fallback needed clearer operator visibility.

## Retry Policy

The aborted Eval-1 producer remains invalid and must not be reused.

Any future Eval-1 retry must:

- use fresh run ids;
- run `scripts/check_llm_targets_live.py` before launch;
- run the strict eval health checker on produced/reused outputs;
- avoid evidence-catalog updates until post-run human review;
- preserve the no-product-quality-claim and no-formal-authority guardrails.

## Recommendation

Do not immediately relaunch Eval-1 from this patch report alone.

Recommended next step is human review of this repair, then a fresh Eval-1 retry brief or explicit launch approval using new run ids and the new LLM health gates.
