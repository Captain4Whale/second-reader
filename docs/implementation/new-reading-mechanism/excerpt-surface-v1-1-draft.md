# Excerpt Surface V1.1 Draft

Purpose: capture the incremental retune of the excerpt surface without mutating the older notes-guided evidence line in place.
Use when: deciding the next chapter-scoped excerpt eval surface, understanding what was already reused versus newly needed, or resuming the v1.1 retune lane after the live rerun merges.
Not for: long-span accumulation design, active live-run control, or stable evaluation constitution.
Update when: the fixed roster changes, the reuse/fill policy changes, the shortfall is resolved, or the draft is promoted into the next judged excerpt surface.

## Isolation Rule
- V1.1 remains isolated from the older notes-guided excerpt evidence line:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_human_notes_guided_excerpt_eval_v1_draft.json`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_human_notes_guided_dataset_v1_excerpt_en_reviewed_cluster_freeze_20260404`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_human_notes_guided_dataset_v1_excerpt_zh_reviewed_cluster_freeze_complete_20260404`
- V1.1 therefore keeps its own manifest and local dataset outputs:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_excerpt_surface_v1_1_draft.json`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_excerpt_surface_v1_1_excerpt_en`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_excerpt_surface_v1_1_excerpt_zh`

## Fixed Roster
- Keep from the notes-guided freeze:
  - `value_of_others_private_en__8`
  - `huochu_shengming_de_yiyi_private_zh__8`
  - `xidaduo_private_zh__15`
  - `nawaer_baodian_private_zh__13`
  - `nawaer_baodian_private_zh__22`
- Import from the clustered benchmark:
  - `supremacy_private_en__13`
  - `meiguoren_de_xingge_private_zh__19`
- Drop from v1.1:
  - `mangge_zhi_dao_private_zh__18`
  - `mangge_zhi_dao_private_zh__26`
  - `nawaer_baodian_private_zh__23`
- Keep as fallback donors only:
  - `steve_jobs_private_en__17`
  - `zouchu_weiyi_zhenliguan_private_zh__14`

## Composition Rule
- V1.1 is incremental, not a rebuild:
  - reuse reviewed frozen rows first
  - then apply the current grouped duplicate controls chapter-by-chapter
  - only after reuse is exhausted should targeted chapter-wide fill be reviewed
- The retune builder mode is now `excerpt_surface_retune`:
  - `note_preserve` first
  - `chapter_wide_fill` second
  - same-span, same-anchor, same-profile overlap, and same-profile anchor-distance guards stay in force
- `excerpt surface` is the semantic term.
  - `state/eval_local_datasets/` remains a storage term only
  - `public/private` remains explicitly non-semantic for benchmark meaning

## Finalized V1.1 Result
- Fresh draft manifest:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_excerpt_surface_v1_1_draft.json`
- Fresh draft summary:
  - `reading-companion-backend/state/dataset_build/build_runs/excerpt_surface_v1_1_20260406/excerpt_surface_v1_1_summary.json`
  - `reading-companion-backend/state/dataset_build/build_runs/excerpt_surface_v1_1_20260406/excerpt_surface_v1_1_summary.md`
- Finalized counts:
  - total primary excerpt cases: `59`
  - `insight_and_clarification` derived subset: `43`
- Per-chapter reused counts after duplicate-control pruning:
  - `value_of_others_private_en__8`: `8`
  - `huochu_shengming_de_yiyi_private_zh__8`: `8`
  - `xidaduo_private_zh__15`: `8`
  - `nawaer_baodian_private_zh__13`: `6`
  - `nawaer_baodian_private_zh__22`: `5`
  - `supremacy_private_en__13`: `12`
  - `meiguoren_de_xingge_private_zh__19`: `12`
- Important reuse finding:
  - `value_of_others_private_en__8` looked like `14` reviewed rows on the old notes-guided surface, but V1.1 dedupes it back down to `8` real unique-span cases because both dense-note bands had produced repeated same-span cases after resolving to the same chapter

## Narrow Fill Attempt
- Prepared one explicit chapter-22 fill dataset:
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_excerpt_surface_v1_1_fill_zh_chapter22_20260406`
- Fill prep summary:
  - `reading-companion-backend/state/dataset_build/build_runs/excerpt_surface_v1_1_fill_chapter22_20260406/excerpt_surface_v1_1_fill_chapter22_summary.md`
- Reviewed packet:
  - `reading-companion-backend/eval/review_packets/archive/excerpt_surface_v1_1_fill_chapter22_first_review_20260406/dataset_review_pipeline_summary.json`
- Candidate reviewed:
  - `nawaer_baodian_private_zh__22__anchored_reaction_selectivity__fill_1`
- Result:
  - stayed `revise`
  - problem type remained `ambiguous_focus`
  - the adjudicator sharpened the focus again, but it still did not clear into `reviewed_active`

## Explicit Exception
- `nawaer_baodian_private_zh__22` remains below the v1.1 honest-short floor:
  - current selected count: `5`
  - floor: `6`
- The approved fallback is now in force:
  - keep the fixed 7-chapter roster unchanged
  - keep `nawaer_baodian_private_zh__22` as the single explicit `5`-case exception
  - do not reopen a broader fill wave or replace the chapter

## Active Eval Order
- Active smoke run id:
  - `attentional_v2_excerpt_surface_v1_1_smoke_20260406`
- Active smoke shard jobs:
  - `bgjob_excerpt_surface_v1_1_smoke_shard_a_20260406`
  - `bgjob_excerpt_surface_v1_1_smoke_shard_b_20260406`
- Active follow-on orchestrator:
  - `bgjob_excerpt_surface_v1_1_eval_orchestrator_20260406`
  - role:
    - wait for both smoke shards
    - run the explicit smoke merge
    - launch both judged shards with `--skip-existing`
    - run the explicit judged merge
- Fixed chapter order:
  - shard A:
    - `supremacy_private_en__13`
    - `meiguoren_de_xingge_private_zh__19`
    - `nawaer_baodian_private_zh__13`
    - `nawaer_baodian_private_zh__22`
  - shard B:
    - `xidaduo_private_zh__15`
    - `value_of_others_private_en__8`
    - `huochu_shengming_de_yiyi_private_zh__8`

## Next Move
- Let both smoke shards finish and run the explicit merge on the shared smoke run root.
- If smoke stays clean:
  - launch the judged shards in the same order
  - use `--skip-existing` so judged reuses the smoke bundles
- Keep long-span out of the execution path until excerpt v1.1 smoke and judged work are both fully settled.
