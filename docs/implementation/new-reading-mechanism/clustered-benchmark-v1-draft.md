# Clustered Benchmark V1 Draft

Purpose: define the active chapter-clustered benchmark shape that replaces the older broad `40 / 40` formal benchmark as the mainline Phase 9 evaluation surface.
Use when: building the new benchmark, checking which four chapters define the clustered surface, or deciding what counts as the active benchmark pointer versus historical evidence.
Not for: stable evaluation constitution, final frozen excerpt membership, or historical comparison details that belong to the archived formal-benchmark draft.
Update when: the selected chapter clusters change, the excerpt freeze advances, or the active benchmark pointer changes again.

## Status
- Active benchmark pointer:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_clustered_benchmark_v1_draft.json`
- Historical benchmark evidence:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_formal_benchmark_v1_draft.json`
  - `docs/implementation/new-reading-mechanism/formal-benchmark-v1-freeze-draft.md`
- Current freeze state:
  - `chapter_core = 4 / 4`
  - `excerpt_primary = 40 / 40`
  - `reserve = 7 / 8`
- Freeze closeout evidence:
  - summary:
    - `reading-companion-backend/state/dataset_build/build_runs/clustered_benchmark_v1_freeze_20260404/clustered_benchmark_v1_freeze_summary.json`
  - machine-readable manifest:
    - `reading-companion-backend/eval/manifests/splits/attentional_v2_clustered_benchmark_v1_draft.json`
  - final local benchmark packages:
    - `reading-companion-backend/state/eval_local_datasets/chapter_corpora/attentional_v2_clustered_benchmark_v1_chapters_en`
    - `reading-companion-backend/state/eval_local_datasets/chapter_corpora/attentional_v2_clustered_benchmark_v1_chapters_zh`
    - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_clustered_benchmark_v1_excerpt_en`
    - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_clustered_benchmark_v1_excerpt_zh`
    - `reading-companion-backend/state/eval_local_datasets/runtime_fixtures/attentional_v2_clustered_benchmark_v1_runtime_en`
    - `reading-companion-backend/state/eval_local_datasets/runtime_fixtures/attentional_v2_clustered_benchmark_v1_runtime_zh`
    - `reading-companion-backend/state/eval_local_datasets/compatibility_fixtures/attentional_v2_clustered_benchmark_v1_compat_shared`
- Completed review waves:
  - primary review:
    - `bgjob_clustered_benchmark_v1_first_review_en_20260403`
    - `bgjob_clustered_benchmark_v1_first_review_zh_20260403`
  - reserve review:
    - `bgjob_clustered_benchmark_v1_reserve_review_en_20260404`
    - `bgjob_clustered_benchmark_v1_reserve_review_zh_20260404`
  - reserve review packet outcomes:
    - EN:
      - `7 keep`, `1 revise`
    - ZH:
      - `7 keep`, `1 unclear`

## Benchmark Shape
- `chapter_core`
  - exactly `4` chapters, one per cluster
- `excerpt_core`
  - target freeze `40` primary excerpt cases
  - target allocation `10` per selected chapter
- `reserve`
  - target freeze `8` reserve cases
  - target allocation `2` per selected chapter

## Active Chapter Clusters
- `supremacy_private_en__13`
  - book: `Supremacy`
  - chapter: `Chapter 7. Playing Games`
- `steve_jobs_private_en__17`
  - book: `Steve Jobs`
  - chapter: `Chapter Eight: Xerox and Lisa: Graphical User Interfaces`
- `zouchu_weiyi_zhenliguan_private_zh__14`
  - book: `走出唯一真理观`
  - chapter: `说理与对话`
- `meiguoren_de_xingge_private_zh__19`
  - book: `美国人的性格`
  - chapter: `5 幸福单车的脱节`

## Eval Mapping
- `reader_character.coherent_accumulation`
  - use the `4` clustered `chapter_core` chapters
- `reader_character.selective_legibility`
  - use all frozen primary excerpt cases
- `reader_value.insight_and_clarification`
  - derive a subset from frozen primary excerpt cases whose `target_profile_id` is:
    - `distinction_definition`
    - `tension_reversal`
    - `callback_bridge`
- `anchored_reaction_selectivity`
  - stays in the benchmark, but only serves `selective_legibility`

## Builder Rules
- Reuse the existing builder/review/import stack.
- Switch construction to clustered mode for this benchmark.
- Allow multiple same-profile cases in one chapter.
- Use stronger duplicate control instead of one-profile-per-chapter caps:
  - reject same normalized excerpt span across profiles
  - reject same anchor sentence reuse
  - reject same-profile overlapping excerpt windows
  - require same-profile anchor distance of at least `3` sentences
- Active clustered profiles are:
  - `distinction_definition`
  - `tension_reversal`
  - `callback_bridge`
  - `anchored_reaction_selectivity`
- Do not include `reconsolidation_later_reinterpretation` in this benchmark build.

## Construction Flow
- Phase A:
  - clustered scratch build on the `4` selected chapters only
  - emit `12` candidate cases plus `4` reserve rows per chapter
- Phase B:
  - first review wave on primary candidates only
  - current live wave is the bilingual smoke2 primary review
- Phase C:
  - reserve top-up only for chapters that still fall short of `10` accepted primaries
- Phase D:
  - freeze the benchmark honestly, even if a chapter saturates short of `10`
- Phase E:
  - derive `insight_and_clarification` mechanically by profile membership rather than a new construction-time taxonomy

## Freeze Closeout
- The clustered benchmark is now truly frozen for mainline use.
- Chapter-level outcome:
  - `supremacy_private_en__13`:
    - `10` primaries
    - `2` reserves
  - `steve_jobs_private_en__17`:
    - `10` primaries
    - `1` reserve
    - needed reserve promotion to reach `10` primaries:
      - `steve_jobs_private_en__17__tension_reversal__reserve_1`
      - `steve_jobs_private_en__17__tension_reversal__reserve_2`
    - honest shortfall:
      - the chapter kept only one additional reserve after those promotions, so clustered benchmark v1 freezes at `7 / 8` reserves overall rather than widening to a fifth chapter
  - `zouchu_weiyi_zhenliguan_private_zh__14`:
    - `10` primaries
    - `2` reserves
  - `meiguoren_de_xingge_private_zh__19`:
    - `10` primaries
    - `2` reserves

## Frozen Composition
- `excerpt_core_primary` composition:
  - `distinction_definition = 1`
  - `tension_reversal = 28`
  - `callback_bridge = 6`
  - `anchored_reaction_selectivity = 5`
- `reader_value.insight_and_clarification` subset:
  - derived mechanically from frozen primary cases whose `target_profile_id` is `distinction_definition`, `tension_reversal`, or `callback_bridge`
  - current frozen subset size: `35`
- Important interpretation:
  - clustered benchmark v1 is now quota-complete on primary cases, but it is not pressure-balanced
  - the current frozen surface leans heavily toward `tension_reversal` and `callback_bridge`
  - treat this as a known limitation of the fast-iteration clustered benchmark, not as a reason to reopen builder widening before the next decisive eval

## Membership Source Of Truth
- Full explicit primary and reserve case membership now lives in:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_clustered_benchmark_v1_draft.json`
  - `reading-companion-backend/state/dataset_build/build_runs/clustered_benchmark_v1_freeze_20260404/clustered_benchmark_v1_freeze_summary.json`

## Working Rule
- This clustered benchmark is intentionally optimized for fast iteration and interview-legible evidence.
- The old broad formal benchmark remains valid historical evidence, but it is no longer the active benchmark pointer.
