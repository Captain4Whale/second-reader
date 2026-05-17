# Slice 8C: Minimal Eval Suite Execution Preflight and Bounded Run - Post-implementation Report v0

## PR Title / Branch

`Slice 8C: Minimal Eval Suite Execution Preflight and Bounded Run`

Branch: `main`

## Slice

Slice 8C / Post-implementation Review & Eval Readiness

## Summary Of Actual Execution

Slice 8C executed the accepted static preflight and then launched the bounded Lane A smoke as a registered background job.

Lane A failed after the fresh `attentional_v2` read completed, before eval summaries were written. The failure occurred in the user-level selective matching path because a visible reaction emitted by the fresh run did not expose a usable source-span locator for the runner's matching contract:

```text
ValueError: Visible reaction rx:Full_Content:src:c1:p1@0-p3@146:highlight:1 in segment huochu_shengming_de_yiyi_private_zh__segment_1 has no usable source locator; user-level selective matching requires source-span locators.
```

Per the accepted failure policy, Lane B was not launched, the failed Lane A run directory and job logs were preserved, no retry was attempted, and the evidence catalog was not updated.

This report records a failed bounded execution attempt. It does not claim eval success, product quality, planning quality, callback correctness, retrieval utilization, source fidelity, or Long Span formal-authority promotion.

## Files Changed

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Commands Actually Run

Preflight:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517
test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517
```

Lane B source metadata was checked from:

```text
reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504/summary/aggregate.json
```

Lane A launch:

```bash
cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- \
  --root . \
  --job-id bgjob_minimal_eval_suite_lane_a_smoke_20260517 \
  --task-ref TASK-SECOND-READER-MEMORY-PLANNING-SLICE8C-EXECUTION \
  --lane mechanism_eval \
  --purpose "Slice 8C Lane A minimal eval smoke: V2-only user-level selective legibility" \
  --cwd . \
  --run-dir eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517 \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517/summary/aggregate.json \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517/summary/report.md \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517/summary/llm_usage.json \
  --shell-command ".venv/bin/python eval/attentional_v2/run_user_level_selective_comparison.py --run-id attentional_v2_minimal_eval_suite_lane_a_smoke_20260517 --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json --mechanism-filter attentional_v2 --judge-mode llm --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004"
```

Read-only follow-up inspection commands included `scripts/check_background_jobs.py`, registry JSON inspection, Lane A run-state inspection, Lane A output existence checks, job log inspection, and forbidden-diff/evidence-catalog-diff checks.

Lane B launch command was not run.

## Background Job Statuses

| Job id | Lane | Registry status | Exit code | Notes |
| --- | --- | --- | --- | --- |
| `bgjob_minimal_eval_suite_lane_a_smoke_20260517` | Lane A / Local User-level Selective Legibility | `failed` | `1` | Fresh V2 read completed, then user-level selective matching failed before summary files were emitted. |
| `bgjob_minimal_eval_suite_lane_b_smoke_20260517` | Lane B / Long Span MQ Callback FVI | not launched | n/a | Blocked by Lane A failure per accepted execution policy. |

The active job registry view was empty after the failed Lane A job reached terminal status.

## Run Directories

| Run id | Path | Status |
| --- | --- | --- |
| `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517` | created; preserved for debugging |
| `attentional_v2_minimal_eval_suite_lane_b_smoke_20260517` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517` | not created |

Generated run and job-registry files remain local ignored artifacts and are not committed.

## Preflight Results

| Check | Result |
| --- | --- |
| Slice 7B manifest smoke | passed; `status=ok`, `tracked_path_count=13`, `local_only_present_count=6`, `local_only_missing_count=0` |
| Static inventory pytest | passed; `8 passed in 0.07s` |
| Background job registry check before launch | passed; no active jobs |
| `docs/tasks/registry.json` parse | passed |
| `git diff --check` | passed |
| Forbidden runtime/frontend/eval-runner diff check | empty output |
| Target Lane A run directory absence | passed before launch |
| Target Lane B run directory absence | passed and remained absent |
| Lane B source run metadata | passed; `probe_plan_id=memory_quality_semantic_probe_plan_20260504`, `probe_selection_method=semantic_boundary_with_distance_reference` |

## Lane A Output Validation

Required output files:

| File | Present? |
| --- | --- |
| `summary/aggregate.json` | no |
| `summary/report.md` | no |
| `summary/llm_usage.json` | no |

Partial files present:

| File | Present? |
| --- | --- |
| `meta/selection.json` | yes |
| `segments/huochu_shengming_de_yiyi_private_zh__segment_1.json` | yes |
| `outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_runtime/run_state.json` | yes |
| `outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_runtime/activity.jsonl` | yes |
| `outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_runtime/llm_standard.jsonl` | yes |
| `outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/public/book_document.json` | yes |
| `outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/public/book_manifest.json` | yes |

Aggregate checks could not be completed because `summary/aggregate.json` was not emitted.

Selection facts from `meta/selection.json`:

```json
{
  "mechanism_keys": ["attentional_v2"],
  "judge_mode": "llm",
  "segment_ids": ["huochu_shengming_de_yiyi_private_zh__segment_1"],
  "note_case_ids": [
    "huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002",
    "huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003",
    "huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004"
  ]
}
```

Runtime read completion facts from `_runtime/run_state.json`:

```json
{
  "stage": "completed",
  "completed_chapters": 1,
  "total_chapters": 1,
  "error": null
}
```

Activity facts from `_runtime/activity.jsonl`:

```json
{
  "row_count": 156,
  "chapter_started": 1,
  "reaction_emitted": 152,
  "checkpoint.saved": 1,
  "chapter_completed": 1,
  "run_completed": 1
}
```

## Lane B Output Validation

Lane B was not launched because Lane A failed. No Lane B output files were expected or created.

Required Lane B aggregate checks were not applicable.

## LLM Usage Summaries

Lane A did not emit `summary/llm_usage.json` because the eval runner failed before summary generation.

The partial Lane A runtime read did emit `_runtime/llm_standard.jsonl`:

```json
{
  "row_count": 221,
  "model": ["MiniMax-M2.7"],
  "nodes": [
    "chapter_consolidation",
    "chapter_zone_classifier",
    "navigate_choose_next_unit",
    "read_unit",
    "reflective_promotion"
  ]
}
```

Token totals were not available from the recorded `llm_standard.jsonl` rows. No Lane B LLM usage exists because Lane B was not launched.

## Reading Jobs And Judge Calls

- Lane A reading jobs: one fresh `attentional_v2` read was launched and completed for `huochu_shengming_de_yiyi_private_zh__segment_1`.
- Lane A eval judge calls: no note-case output files or `summary/llm_usage.json` were emitted; the failure occurred while building reaction candidates for matching, before a complete eval summary.
- Lane B reading jobs: none; Lane B was not launched.
- Lane B judge calls: none; Lane B was not launched.
- Full AI Evaluation: not run.
- Broad benchmark jobs: not run.
- Cross-mechanism comparison: not run.

## Evidence Catalog And Diff Checks

- `reading-companion-backend/docs/evaluation/evidence_catalog.md` unchanged.
- `reading-companion-backend/docs/evaluation/evidence_catalog.json` unchanged.
- Forbidden runtime/frontend/eval-runner diff check returned empty output.
- Runtime mechanism code was not modified.
- Eval runners were not modified.
- Judge prompts were not modified.
- Frontend, public API, and durable mechanism state were not modified.

## Known Limitations / Follow-up Questions

- The bounded Lane A run exposed a source-locator compatibility failure between fresh `attentional_v2` visible reactions and the user-level selective runner's source-span locator requirement.
- The exact repair path is not chosen in this report. Potential future options may include a small source-locator compatibility patch, a narrower run-profile adjustment, or an explicit dataset/runner contract decision.
- Any retry must use a new `_retry1` run id after human approval. The failed run directory should remain preserved for debugging.
- Lane B was not exercised, so Slice 8C did not produce Long Span MQ / Callback / FVI smoke evidence.
- This partial run is not a product-quality result.

## Interpretation Guards

- Audit existence is not product quality.
- Retrieval availability is not utilization success.
- Visible reaction presence is not callback correctness.
- SourceRef count is not fidelity score.
- Trace existence is not planning quality.
- `slow_cycle_audit` existence is not slow-cycle quality.
- A failed smoke run is diagnostic execution evidence, not a benchmark score or formal product claim.

## Explicit Boundary Statement

- No runtime mechanism behavior was changed.
- No prompt text or prompt version was changed.
- No eval runner was imported for modification or changed.
- No judge prompt was changed.
- No public API or frontend code was changed.
- No durable mechanism state was changed.
- No evidence catalog update was made.
- No new metrics or scoring taxonomy were introduced.
- Long Span vNext was not promoted to formal benchmark authority.
- Lane A and Lane B were not broadened.
- No cross-mechanism comparison was run.
- No silent fallback to `--judge-mode none` occurred.

## Rollback / Cleanup Notes

No cleanup was performed. Per the accepted failure policy, partial Lane A run artifacts and job logs were preserved for debugging.

Do not delete or catalog the failed output by default. Do not retry with the same run id. Any retry requires human approval and a new `_retry1` run id.

Tracked repo rollback is a simple revert of this report and status-doc updates.

## Next Recommended Step

Human reviewer reviews this Slice 8C Post-implementation Report.

Recommended decision gate: decide whether to patch the Lane A source-locator compatibility seam, revise the bounded run profile, or authorize a `_retry1` run with a specific change. Do not launch Lane B, retry Lane A, update the evidence catalog, or start another eval slice until this report is reviewed and the next action is explicitly accepted.
