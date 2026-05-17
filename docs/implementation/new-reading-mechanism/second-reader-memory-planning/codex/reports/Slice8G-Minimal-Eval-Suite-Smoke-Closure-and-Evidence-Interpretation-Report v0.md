# Slice 8G: Minimal Eval Suite Smoke Closure and Evidence Interpretation Report

## Executive Verdict

The bounded Minimal Eval Suite smoke sequence completed successfully after the Lane A retry.

Covered sequence:

- Slice 8C: Lane A bounded run attempted and failed because one visible reaction had no usable source-span locator for user-level selective matching.
- Slice 8D: Lane A source-locator compatibility patch landed.
- Slice 8E: Lane A `_retry1` completed successfully.
- Slice 8F: Lane B bounded diagnostic smoke completed successfully.

This evidence is diagnostic smoke evidence only. It is not formal benchmark authority, not product-quality proof, not a new metric taxonomy, and not a Long Span vNext promotion.

## Lane A Summary

Original Slice 8C failure:

- Run id: `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517`.
- Job id: `bgjob_minimal_eval_suite_lane_a_smoke_20260517`.
- Failure cause: visible reaction `rx:Full_Content:src:c1:p1@0-p3@146:highlight:1` had no usable source-span locator for user-level selective matching.
- Lane B was not launched after the failure.

Slice 8D compatibility patch:

- The Lane A user-level selective runner now derives `segment_source_v1` slices from structured same-paragraph `primary_source_ref.source_span` when `target_locator` is absent.
- Truly unlocatable reactions are recorded as compact diagnostics and skipped from matching.
- The patch does not turn unlocatable reactions into matches and does not weaken strict source-span overlap matching for valid candidates.

Slice 8E retry:

| Field | Value |
| --- | --- |
| Run id | `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1` |
| Job id | `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1` |
| Job status | `completed` |
| Mechanism | `attentional_v2` only |
| Segment count | `1` |
| Note-case count | `3` |
| Exact matches | `2` |
| Misses | `1` |
| Note recall | `0.6667` |

Unlocatable diagnostic:

- `rx:Chapter_1:src:c1:p239@287-p239@287:retrospect:1`
- This diagnostic was not counted as a best reaction, candidate match, or successful note match.

## Lane B Summary

Slice 8F bounded diagnostic smoke:

| Field | Value |
| --- | --- |
| Run id | `attentional_v2_minimal_eval_suite_lane_b_smoke_20260517` |
| Job id | `bgjob_minimal_eval_suite_lane_b_smoke_20260517` |
| Job status | `completed` |
| Mechanism keys | `["attentional_v2"]` |
| Memory Quality window count | `1` |
| Memory Quality probe count | `5` |
| Average Memory Quality score | `3.700` |
| Memory Quality source | `fresh_judge` |
| Reaction audit source | `copied_from_memory_quality_source_run` |
| Reading jobs | `0` |
| Fresh Memory Quality judge calls | `5` |
| Fresh reaction-audit judge calls | `0` |

Selected-window copied reaction audit for `huochu_shengming_de_yiyi_private_zh__segment_1`:

| Field | Value |
| --- | --- |
| Grounded callbacks | `29` |
| Weak callbacks | `9` |
| False visible integrations | `0` |
| Total visible reactions | `267` |

Copied-audit caveat:

- Lane B fresh Memory Quality rejudge covered one selected window.
- The copied reaction audit artifacts contain the full source run's five reaction windows.
- This broader copied reaction audit is useful diagnostic context but is not fresh Callback / FVI judging and should not be interpreted as a newly filtered one-window reaction-audit run.

## Interpretation

What this smoke supports:

- The accepted minimal eval wiring can execute both required lanes under bounded scope.
- Lane A source-locator compatibility is sufficient for the accepted three-note-case retry.
- Lane B can reuse semantic-probe source outputs and fresh-rejudge Memory Quality without launching reading jobs.
- The job registry, expected outputs, aggregate summaries, and LLM usage summaries are sufficient for human review of bounded smoke execution.

What this smoke does not support:

- It does not prove product quality.
- It does not establish full benchmark authority.
- It does not support cross-mechanism comparison.
- It does not prove broad Lane A performance beyond the three note cases.
- It does not provide fresh Callback / FVI judging for Lane B.
- It does not promote Long Span vNext from diagnostic phase 1 to formal authority.

Why this is not product-quality proof:

- Lane A used one segment and three note cases.
- Lane B used one Memory Quality window and copied reaction audit from a broader source run.
- The run sequence was designed to validate bounded execution, evidence availability, and interpretation guardrails, not to produce a stable product score.

## Known Limitations

- Lane A sample is intentionally tiny.
- Lane B Memory Quality covers one window only.
- Lane B reaction audit was copied, not freshly judged.
- Copied reaction audit is broader than the selected Memory Quality window.
- No cross-mechanism comparison was run.
- No full AI Evaluation was run.
- No evidence catalog entry was created.
- No public product-quality claim is supported by these smoke outputs.

## Recommended Follow-ups

- No immediate runtime patch is indicated.
- No immediate eval-runner patch is required.
- Optional: create a narrow follow-up brief for Lane B copied reaction-audit filtering or reporting semantics if reviewers want one-window reaction-audit artifacts in future smoke reports.
- Optional: create a diagnostic evidence-catalog entry brief after human review if the team wants to catalog the smoke as diagnostic evidence.
- Possible broader eval remains blocked until explicitly scoped and approved.

## Guardrails Preserved

- No eval was run in Slice 8G.
- No eval run directories were created in Slice 8G.
- No evidence catalog update was made.
- No runtime mechanism code was changed.
- No eval runner was changed.
- No judge prompt was changed.
- No frontend, public API, or durable mechanism state was changed.
- No new metrics or scoring were added.
- Long Span vNext was not promoted to formal benchmark authority.
- No product-quality claim is made.

## Validation For Slice 8G Landing

Required validation:

```bash
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json
```

The forbidden diff check must return empty output.
