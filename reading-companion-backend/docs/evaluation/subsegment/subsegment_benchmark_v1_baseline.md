# Subsegment Benchmark Baseline: v1

## Summary

This report promotes two runtime-first benchmark runs into one reviewed baseline for `target = subsegment_segmentation`.

It records the first standard benchmark executed after the subsegment eval taxonomy was stabilized around:

- `target`
- `scope`
- `method`

This report is evidence-bearing, not methodology-bearing. Use [`../../../../docs/backend-reader-evaluation.md`](../../../../docs/backend-reader-evaluation.md) for the stable evaluation framework.

## Comparison Target

- `heuristic_only` vs `llm_primary` on curated subsegment benchmark cases

## Dataset

- Dataset ID: `subsegment_benchmark_v1`
- Dataset version: `1`
- Tracked dataset size: `24` cases
- Core development pool: `18` cases
- Audit pool: `6` cases

## Run Set

### Run A

- Run ID: `subsegment_benchmark_v1_direct_core18`
- Scope: `direct_quality`
- Method: `deterministic_metrics`, `pairwise_judge`
- Case set: all `18` core cases
- Segment timeout: `45s`
- Operator setting: `LLM_RETRY_ATTEMPTS=1`
- Runtime report:
  - [`../../../eval/runs/subsegment/subsegment_benchmark_v1_direct_core18/summary/report.md`](../../../eval/runs/subsegment/subsegment_benchmark_v1_direct_core18/summary/report.md)

### Run B

- Run ID: `subsegment_benchmark_v1_local_impact_audit6`
- Scope: `local_impact`
- Method: `deterministic_metrics`, `pairwise_judge`
- Case set: `core_c1_01`, `core_c1_02`, `core_c3_02`, `core_c8_01`, `core_c9_02`, `audit_c4_02`
- Segment timeout: `120s`
- Operator setting: `LLM_RETRY_ATTEMPTS=1`
- Runtime report:
  - [`../../../eval/runs/subsegment/subsegment_benchmark_v1_local_impact_audit6/summary/report.md`](../../../eval/runs/subsegment/subsegment_benchmark_v1_local_impact_audit6/summary/report.md)

## Rubric

### Direct Quality

- self-containedness
- minimal sufficiency
- one primary reading move

### Local Impact

- reaction focus
- source-anchor quality
- coverage of meaningful turns, definitions, and callbacks
- coherence after merge

## Aggregate Findings

### Direct Quality

- Cases evaluated: `18`
- `llm_primary` fallback rate: `38.89%`
- `llm_primary` invalid-plan rate: `38.89%`
- `llm_primary` failure rate: `0.00%`
- `heuristic_only` failure rate: `0.00%`
- Average unit count (`heuristic_only`): `2.78`
- Average unit count (`llm_primary`): `4.94`

#### Pairwise Winners

- `llm_primary`: `6`
- `heuristic_only`: `4`
- `tie`: `8`

### Local Impact

- Cases evaluated: `6`
- `llm_primary` fallback rate: `33.33%`
- `llm_primary` invalid-plan rate: `33.33%`
- `llm_primary` failure rate: `83.33%`
- `heuristic_only` failure rate: `83.33%`
- Average unit count (`heuristic_only`): `3.67`
- Average unit count (`llm_primary`): `5.83`

#### Pairwise Winners

- `heuristic_only`: `4`
- `llm_primary`: `2`

## Representative Evidence

### Direct-Quality Wins For `llm_primary`

- `core_c1_02`
  - The planner won by separating distinct reading moves at natural argumentative turns instead of keeping rule-definition material fused into a longer mixed unit.
- `core_c2_02`
  - The planner won by separating framework introduction from the later causal explanation, producing cleaner move boundaries.
- `core_c3_01`
  - The planner won by treating the aerodynamic analogy and the later conceptual shift as separate local reading objects instead of mixing analogy, definition, and turn in one larger block.

### Direct-Quality Wins For `heuristic_only`

- `core_c9_01`
  - The heuristic baseline won because the planner over-segmented a definition-plus-theory passage into several micro-units that no longer felt "fewest but self-contained."
- `core_c10_01`
  - The heuristic baseline won because the planner cut one argumentative flow into `8` units, including overly fine example and turn fragments.
- `core_c11_01`
  - The heuristic baseline won because the planner split a causal chain and closing move more finely than the rubric considered necessary.

## Failure Analysis

### Direct Quality Planner Failure Reasons

The `llm_primary` path fell back or produced an invalid plan in `7 / 18` direct-quality cases:

- `too_many_units`: `5`
- `missing_units`: `1`
- `incomplete_sentence_coverage`: `1`

Affected cases:

- `core_c1_01`: `missing_units`
- `core_c2_01`: `incomplete_sentence_coverage`
- `core_c3_02`: `too_many_units`
- `core_c6_01`: `too_many_units`
- `core_c7_01`: `too_many_units`
- `core_c8_01`: `too_many_units`
- `core_c9_02`: `too_many_units`

Important pattern:

- All `7` invalid-plan cases still ended as `tie` in the direct-quality judgment.
- The most common structural miss is over-segmentation, not planner crash or section-level failure.

### Local-Impact Noise

The local-impact run is currently dominated by runtime noise:

- `5 / 6` cases had `timed_out = True` for both strategies
- only `audit_c4_02` completed without a timeout on either side

Per-case timeout status:

- `core_c1_01`: both timed out
- `core_c1_02`: both timed out
- `core_c3_02`: both timed out
- `core_c8_01`: both timed out
- `core_c9_02`: both timed out
- `audit_c4_02`: neither timed out

Interpretation:

- The local-impact run is still useful as audit evidence.
- It is not yet clean enough to act as the primary decision surface for this mechanism change.

## Conclusions

- The new `llm_primary` planner has a positive direct-quality signal:
  - it wins more direct-quality comparisons than `heuristic_only`
  - it does so without introducing direct planner execution failures
- The planner is not yet stable enough:
  - invalid/fallback behavior remains high at `38.89%`
  - the dominant miss is `too_many_units`, which matches the observed qualitative complaints about over-segmentation
- The current local-impact audit is too noisy to overturn the direct-quality result:
  - the section-level comparison remains heavily confounded by timeouts even with a `120s` section budget

## Recommended Next Steps

1. Treat this report as the checked-in baseline for future subsegment reruns.
2. Improve planner and validator behavior before changing the judge rubric.
3. Prioritize planner fixes around:
   - `too_many_units`
   - `missing_units`
   - `incomplete_sentence_coverage`
4. Re-run the `direct_quality` core-18 benchmark after those fixes.
5. Revisit `local_impact` only after the direct-quality invalid-plan rate drops and section-level timeout noise is lower.

## Known Caveats

- This benchmark is intentionally curated for attribution, not broad corpus coverage.
- The v1 dataset is still dominated by repo-tracked nonfiction sections from one primary source book plus one fixture sanity case.
- `LLM_RETRY_ATTEMPTS=1` was used operationally to keep provider retry stalls from dominating wall-clock time.
- This report promotes runtime-first benchmark artifacts into a checked-in baseline; it should not be read as a stable methodology document.
