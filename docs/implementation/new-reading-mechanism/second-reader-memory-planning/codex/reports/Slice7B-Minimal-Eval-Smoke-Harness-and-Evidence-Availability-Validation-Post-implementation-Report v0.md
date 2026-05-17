# Slice 7B: Minimal Eval Smoke Harness and Evidence Availability Validation - Post-implementation Report v0

## PR Title / Branch

`Slice 7B: Minimal Eval Smoke Harness and Evidence Availability Validation`

Branch: `main`

## Slice

Slice 7B / Minimal Eval Implementation

## Summary Of Actual Changes

Slice 7B added a tiny stdlib-only smoke validator for the accepted Slice 7A minimal eval inventory manifest. The validator checks manifest identity, lane separation, tracked/local-only path handling, evidence-surface wiring, non-scoring diagnostics, and interpretation guards, then prints a compact JSON availability summary.

This is evidence-availability validation only. It is not eval result evidence and not a product-quality score.

## Files Changed

- `reading-companion-backend/scripts/validate_minimal_eval_inventory_smoke.py`
- `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- `reading-companion-backend/docs/evaluation/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design Contracts Addressed

- Preserved Lane A: Local / User-level Selective Legibility.
- Preserved Lane B: Long Span MQ / Callback / FVI.
- Preserved Long Span vNext as diagnostic Phase-1, not formal benchmark authority.
- Added a reusable non-LLM smoke command without importing, invoking, or modifying eval runners.
- Kept missing `local_only` paths reportable rather than failing.
- Preserved interpretation guards:
  - retrieval availability is not utilization success
  - visible reaction presence is not callback correctness
  - SourceRef count is not fidelity score
  - trace existence is not planning quality
  - `slow_cycle_audit` existence is not slow-cycle quality

## Deviations From Accepted Brief

None.

## Tests Added Or Updated

- Extended `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`.
- Added subprocess coverage for the committed manifest smoke command.
- Added a negative temp-manifest case that rejects a false interpretation guard without modifying the committed manifest.

## Commands Run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

## Test Results

```text
8 passed in 0.07s
docs/tasks/registry.json parsed successfully.
git diff --check returned no whitespace errors.
Forbidden runtime/frontend/eval-runner diff check returned empty output.
```

Smoke summary:

```json
{"diagnostic_ids": ["planning_trace_quality", "slow_cycle_safety"], "evidence_surface_ids": ["detour_trace_evidence", "memory_uptake_admission_outcome_fields", "navigation_trace", "projection_markers", "read_audit", "settlement_audit", "slow_cycle_audit", "source_ref_binding_resolution_markers", "supplemental_retrieval"], "lane_ids": ["lane_a_local_user_level_selective_legibility", "lane_b_long_span_mq_callback_fvi"], "local_only_missing_count": 0, "local_only_present_count": 6, "manifest_id": "attentional_v2_minimal_eval_inventory_v1", "status": "ok", "tracked_path_count": 13}
```

## Contract / Audit Evidence Produced

- New smoke command:
  - `cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- It validates manifest/evidence availability only.
- It does not create run directories or write output files by default.

## Explicit Non-execution Statement

- Full AI Evaluation was not run.
- Benchmark jobs were not run.
- Judge calls were not made.
- Reading jobs were not launched.
- Eval runners were not imported, invoked, or modified.
- Runtime mechanism behavior was not changed.
- No scoring was introduced.

## Backward Compatibility Notes

- No runtime mechanism code changed.
- No prompt text or prompt version changed.
- No public API or frontend contract changed.
- No eval runner or judge prompt changed.
- The smoke script uses only Python stdlib.

## Risk / Rollback Notes

Rollback is a simple revert of this static smoke script / docs / test slice.

No migration is required.

## Known Gaps

- Slice 7B does not execute an actual eval run.
- Slice 7B does not check whether available evidence is good, sufficient, or used by a model.
- Slice 7B does not modify eval runners to consume the manifest.

## Next Recommended Step

Human reviewer reviews this Slice 7B Post-implementation Report.

Do not start the next eval slice or run eval until this report is accepted and a next-slice brief is created and accepted.
