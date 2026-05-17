# Slice 8H: Diagnostic Evidence Catalog Entry for Minimal Eval Suite Smoke - Pre-implementation Brief v0

## PR Title

`Slice 8H: Diagnostic Evidence Catalog Entry for Minimal Eval Suite Smoke`

## Implementation Slice

Slice 8H is a doc-only cataloging brief. It decides whether and how the completed Slice 8C through Slice 8G Minimal Eval Suite smoke sequence should be added to the evaluation evidence catalog in a later accepted implementation slice.

This brief does not update `evidence_catalog.md` or `evidence_catalog.json`, run eval, create eval run directories, change runtime mechanism behavior, modify eval runners, modify judge prompts, add metrics, claim product quality, or promote Long Span vNext to formal benchmark authority.

## Design Sources

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.json`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- `docs/backend-reader-evaluation.md`
- `docs/tasks/registry.json`

## Current Evidence Facts

- Slice 8G Minimal Eval Suite smoke closure and evidence interpretation is accepted by reviewer instruction.
- Slice 8C Lane A failed before summary generation because visible reaction `rx:Full_Content:src:c1:p1@0-p3@146:highlight:1` had no usable source-span locator for user-level selective matching.
- Slice 8D patched Lane A source-locator compatibility by deriving `segment_source_v1` slices from structured same-paragraph `primary_source_ref.source_span` when `target_locator` is absent.
- Slice 8D also records truly unlocatable reactions as diagnostics and skips them from matching; it does not turn unlocatable reactions into matches.
- Slice 8E Lane A `_retry1` succeeded with run id `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1` and job id `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1`.
- Slice 8E covered one segment and three note cases: `exact_match_count=2`, `miss_count=1`, and `note_recall=0.6667`.
- Slice 8E recorded one unlocatable retrospect diagnostic, and that diagnostic was not counted as a best reaction, candidate match, or successful note match.
- Slice 8F Lane B bounded diagnostic smoke succeeded with run id `attentional_v2_minimal_eval_suite_lane_b_smoke_20260517` and job id `bgjob_minimal_eval_suite_lane_b_smoke_20260517`.
- Slice 8F used `mechanism_keys=["attentional_v2"]`, one Memory Quality window, five probes, average MQ score `3.700`, `memory_quality_source=fresh_judge`, and `reaction_audit_source=copied_from_memory_quality_source_run`.
- Slice 8F selected-window copied reaction audit recorded `grounded=29`, `weak=9`, and `FVI=0`.
- The copied reaction audit is broader than the single selected Memory Quality window and is not fresh Callback / FVI judging.
- Existing evidence catalog status labels do not yet include `diagnostic_smoke`; existing entries distinguish current formal evidence, quality audits, historical evidence, superseded evidence, failed diagnostics, and invalidated diagnostics.
- `evidence_catalog.json` schema version `1` already supports nested `metric_summary`, `run_paths`, `job_ids`, and `one_line_conclusion` fields, so a future diagnostic smoke entry should not require a schema migration.

## Proposed Catalog Status

A diagnostic evidence catalog entry is warranted after Slice 8G acceptance.

Recommended status:

- `diagnostic_smoke`

Rationale:

- The Slice 8C through Slice 8G sequence is reviewed, bounded, and meaningful diagnostic evidence across both required minimal eval lanes.
- `diagnostic_smoke` is more precise than `quality_audit` because the smoke validates bounded wiring, execution, and interpretation guardrails rather than claiming mechanism quality.
- `not_formal_authority` and `not_product_quality_proof` should be explicit caveats or metadata fields, not the primary status label.
- Waiting for a broader eval is not necessary before cataloging this diagnostic smoke; a broader eval can receive a separate catalog entry later if explicitly approved.

## Proposed Catalog Fields

Future implementation should add one synthetic catalog entry. It must reference existing run outputs and reports without creating a new run directory.

Recommended entry shape:

- `run_id`: `attentional_v2_minimal_eval_suite_smoke_20260517`
- `surface`: `minimal_eval_suite_smoke`
- `evaluation_goal`: `Minimal Eval Suite bounded diagnostic smoke`
- `status`: `diagnostic_smoke`
- `mechanisms`: `["attentional_v2"]`
- `dataset_path`: `state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422`
- `manifest_path`: `eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- `job_ids`:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517`
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1`
  - `bgjob_minimal_eval_suite_lane_b_smoke_20260517`
- `metric_summary.lane_a`:
  - `failed_run_id=attentional_v2_minimal_eval_suite_lane_a_smoke_20260517`
  - `retry_run_id=attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1`
  - `segment_count=1`
  - `note_case_count=3`
  - `exact_match_count=2`
  - `miss_count=1`
  - `note_recall=0.6667`
  - `source_locator_compatibility_patch_required=true`
  - `unlocatable_reactions_not_counted_as_matches=true`
- `metric_summary.lane_b`:
  - `run_id=attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`
  - `window_count=1`
  - `probe_count=5`
  - `average_memory_quality_score=3.700`
  - `memory_quality_source=fresh_judge`
  - `reaction_audit_source=copied_from_memory_quality_source_run`
  - `selected_window_grounded_callbacks=29`
  - `selected_window_weak_callbacks=9`
  - `selected_window_false_visible_integrations=0`
  - `copied_reaction_audit_scope=broader_than_selected_mq_window`
  - `fresh_callback_fvi_judging=false`
- `metric_summary.caveats`:
  - `not_product_quality_proof=true`
  - `not_formal_benchmark_authority=true`
  - `not_long_span_vnext_promotion=true`
  - `no_cross_mechanism_comparison=true`
  - `no_full_ai_evaluation=true`
  - `callback_fvi_not_fresh_judged_in_slice8f=true`
- `run_paths` should reference the Lane A retry aggregate/report/LLM usage, Lane B aggregate/report/LLM usage/output sourcing, and Slice 8C through Slice 8G interpretation reports.

The Markdown catalog row should summarize the same facts compactly and add `diagnostic_smoke` to the catalog's status meanings.

## Files To Change If Accepted

- `reading-companion-backend/docs/evaluation/evidence_catalog.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.json`
- `reading-companion-backend/docs/evaluation/README.md`, only if a small pointer is useful after the catalog entry exists
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Files Explicitly Not Changing

- Runtime mechanism code under `reading-companion-backend/src/attentional_v2/`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- source skills
- eval runners
- judge prompts
- frontend
- public API
- durable mechanism state
- eval run directories

## Validation Commands

Brief landing validation:

```bash
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json
```

The forbidden diff check must return empty output during this brief landing because the evidence catalog is not edited yet.

Future catalog implementation validation, if this brief is accepted:

```bash
cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_catalog.py --check
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

## Non-goals

- No eval run.
- No new eval run directory.
- No evidence catalog update during this brief landing.
- No runtime mechanism change.
- No eval-runner or judge-prompt change.
- No frontend, public API, or durable-state change.
- No new metrics or scoring.
- No cross-mechanism comparison.
- No product-quality claim.
- No Long Span vNext formal-authority promotion.

## Risks

- A catalog entry could be mistaken for product-quality proof. Mitigation: use `diagnostic_smoke`, explicit caveats, and a conclusion that states the smoke validates bounded execution and wiring only.
- Lane B copied reaction audit could be mistaken for fresh Callback / FVI judging. Mitigation: record `reaction_audit_source=copied_from_memory_quality_source_run`, `fresh_callback_fvi_judging=false`, and the broader-than-selected-window caveat.
- Adding a new status label could create catalog taxonomy drift. Mitigation: define `diagnostic_smoke` narrowly as reviewed bounded smoke evidence, not a new scoring category.
- The synthetic catalog id could be mistaken for a real run directory. Mitigation: record it as a catalog entry id that references Lane A and Lane B run outputs, and do not create a matching run directory.

## Rollback Plan

- Revert the future catalog-entry PR.
- No runtime rollback, data migration, eval artifact cleanup, or run-directory deletion is required.
- If reviewers reject `diagnostic_smoke`, a follow-up can use the existing `quality_audit` status with stronger caveats, but that is not the recommended default.

## Go / No-go Recommendation

Go for human review of this Slice 8H brief.

Recommended future action after acceptance: add one diagnostic smoke evidence catalog entry with strong caveats in `evidence_catalog.md` and `evidence_catalog.json`.

No-go for eval execution, evidence catalog edits during brief landing, runtime changes, eval-runner changes, judge-prompt changes, new metrics, product-quality claims, or Long Span vNext formal-authority promotion.
