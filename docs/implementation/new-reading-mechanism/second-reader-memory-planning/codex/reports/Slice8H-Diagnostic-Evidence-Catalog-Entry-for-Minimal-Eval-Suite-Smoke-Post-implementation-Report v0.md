# Slice 8H: Diagnostic Evidence Catalog Entry for Minimal Eval Suite Smoke - Post-implementation Report v0

## Summary

Slice 8H added one diagnostic smoke evidence catalog entry for the completed Slice 8C through Slice 8G Minimal Eval Suite smoke sequence.

The catalog entry is diagnostic only. It is not formal benchmark authority, not product-quality proof, not a new metric taxonomy, and not a Long Span vNext promotion.

## Implementation

Catalog entry added:

- `run_id`: `attentional_v2_minimal_eval_suite_smoke_20260517`
- `surface`: `minimal_eval_suite_smoke`
- `evaluation_goal`: `Minimal Eval Suite bounded diagnostic smoke`
- `status`: `diagnostic_smoke`
- `mechanisms`: `["attentional_v2"]`

Tooling update:

- `diagnostic_smoke` was added to `ALLOWED_STATUSES`.
- `diagnostic_smoke` was added to markdown status ordering as `Diagnostic Smoke Evidence`.
- `diagnostic_smoke` was added to Status Meanings as reviewed bounded smoke evidence that is diagnostic only, not formal benchmark authority or product-quality proof.
- `FORMAL_STATUSES` remains unchanged, so `diagnostic_smoke` is not treated as formal evidence.

Catalog evidence references:

- Lane A failed run id: `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517`
- Lane A retry run id: `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1`
- Lane B run id: `attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`
- Slice 8C through Slice 8G reports
- Existing Lane A and Lane B aggregate, report, LLM usage, and output-sourcing artifacts

No matching synthetic run directory was created for `attentional_v2_minimal_eval_suite_smoke_20260517`.

## Recorded Evidence Facts

Lane A:

- `segment_count=1`
- `note_case_count=3`
- `exact_match_count=2`
- `miss_count=1`
- `note_recall=0.6667`
- `source_locator_compatibility_patch_required=true`
- `unlocatable_reactions_not_counted_as_matches=true`

Lane B:

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

Required caveats:

- `not_product_quality_proof=true`
- `not_formal_benchmark_authority=true`
- `not_long_span_vnext_promotion=true`
- `no_cross_mechanism_comparison=true`
- `no_full_ai_evaluation=true`
- `callback_fvi_not_fresh_judged_in_slice8f=true`

## Files Changed

- `reading-companion-backend/scripts/update_evaluation_catalog.py`
- `reading-companion-backend/docs/evaluation/evidence_catalog.json`
- `reading-companion-backend/docs/evaluation/evidence_catalog.md`
- `reading-companion-backend/docs/evaluation/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Validation

Commands run:

```bash
cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_catalog.py --check
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

Result:

- Catalog validation passed.
- Registry JSON parsed successfully.
- `git diff --check` passed.
- Forbidden runtime/frontend/eval-runner diff check returned empty output.
- `test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_smoke_20260517` passed.

## Explicit Non-actions

- No eval was run.
- No eval directories were created.
- No runtime mechanism code was changed.
- No eval runner was changed.
- No judge prompt was changed.
- No frontend, public API, or durable mechanism state was changed.
- No new metrics or scoring were added.
- Long Span vNext remains diagnostic phase 1.
- No product-quality claim is made.
- `diagnostic_smoke` is not formal authority.

## Deviations From Accepted Brief

None.

## Known Limitations

- This entry catalogs diagnostic smoke evidence only.
- Lane A remains a three-note-case smoke.
- Lane B remains a one-window Memory Quality smoke with copied reaction audit, not fresh Callback / FVI judging.
- The evidence catalog now records the smoke sequence, but it does not promote it to formal benchmark authority.

## Next Recommended Step

Human review of this Slice 8H Post-implementation Report.

Do not run broader eval, promote Long Span vNext, claim product quality, or add further catalog entries until a later human-approved slice explicitly scopes that work.
