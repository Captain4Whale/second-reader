# Slice 7A: Minimal Eval Asset Inventory and Evidence Wiring - Post-implementation Report v0

## PR Title / Branch

`Slice 7A: Minimal Eval Asset Inventory and Evidence Wiring`

Branch: `main`

## Slice

Slice 7A / Minimal Eval Implementation

## Summary Of Actual Changes

Slice 7A landed a static, mechanism-private minimal eval inventory and evidence-wiring manifest. The manifest preserves the two required eval lanes, records historical / superseded / discontinued assets, and maps Slice 1-6 evidence surfaces to the existing minimal eval lanes and lightweight diagnostic additions.

No eval was run. No runtime mechanism behavior changed.

## Files Changed

- `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- `reading-companion-backend/docs/evaluation/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design Contracts Addressed

- Preserved Lane A: Local / User-level Selective Legibility.
- Preserved Lane B: Long Span MQ / Callback / FVI.
- Distinguished Lane A active dataset pointer `attentional_v2_user_level_selective_v1_repaired_20260422` from the current formal evidence bundle using `attentional_v2_user_level_selective_v1_repaired_20260416`.
- Distinguished Long Span vNext diagnostic evidence from formal benchmark authority.
- Marked historical / superseded / discontinued assets without promoting them to active lanes.
- Mapped Slice 1-6 evidence surfaces:
  - `read_audit`
  - `settlement_audit`
  - `supplemental_retrieval`
  - `navigation_trace`
  - `detour_trace_evidence`
  - `slow_cycle_audit`
  - `source_ref_binding_resolution_markers`
  - `projection_markers`
  - `memory_uptake_admission_outcome_fields`
- Kept Planning Trace Quality and Slow-cycle Safety as diagnostic evidence-availability additions only, not product-quality scores.
- Explicitly preserved interpretation guards:
  - retrieval availability is not utilization success
  - visible reaction presence is not callback correctness
  - SourceRef count is not fidelity score
  - trace existence is not planning quality
  - `slow_cycle_audit` existence is not slow-cycle quality

## Deviations From Accepted Brief

None.

## Tests Added Or Updated

- Added `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`.
- The test is pure JSON/path validation and does not import or execute eval runners.

## Commands Run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

## Test Results

```text
6 passed in 0.01s
docs/tasks/registry.json parsed successfully.
git diff --check returned no whitespace errors.
Forbidden runtime/frontend/eval-runner diff check returned empty output.
```

## Contract / Audit Evidence Produced

- New manifest:
  - `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- It is static inventory / evidence wiring only.
- It is not eval result evidence.
- It does not run judges, start reading jobs, or score product quality.

## Backward Compatibility Notes

- No runtime mechanism code changed.
- No prompt text or prompt version changed.
- No public API or frontend contract changed.
- No eval runner or judge prompt changed.
- The manifest uses `path_status="tracked"` for required tracked assets and `path_status="local_only"` for local dataset / run-output pointers that may not exist in every clone.

## Risk / Rollback Notes

Rollback is a simple revert of this static inventory / docs / test slice.

No migration is required.

## Known Gaps

- Slice 7A does not execute the future minimal eval smoke.
- Slice 7A does not modify eval runners to consume the manifest.
- Slice 7A does not promote Long Span vNext to formal benchmark authority.
- Slice 7A does not create new metrics or quality scores for planning trace or slow-cycle safety.

## Next Recommended Step

Human reviewer reviews this Slice 7A Post-implementation Report.

Do not start Slice 7B or run eval until this report is accepted and a next-slice brief is created and accepted.

## Required Checks

- Did this PR change behavior, schema, prompt, audit, evaluation, or tests?
  - It changed tests and added a static eval inventory manifest. It did not change runtime behavior, prompt text/version, audit writers, eval runners, or evaluation outputs.
- Did this PR introduce new infrastructure?
  - No.
- Did this PR preserve SourceRef-first behavior?
  - Yes. Runtime behavior is unchanged, and the manifest explicitly treats SourceRef evidence as substrate rather than fidelity score.
- Did this PR avoid audit dump into runtime prompt?
  - Yes. No prompt path changed.
- Did this PR avoid reaction_records as semantic memory?
  - Yes. Runtime behavior is unchanged.
- Did this PR avoid knowledge_activations as source truth?
  - Yes. Runtime behavior is unchanged.
- Is this PR safe to review as a small slice?
  - Yes. It is static manifest / docs / targeted test only.
