# Excerpt Surface V1.1 Draft

Purpose: capture the incremental retune of the excerpt surface without mutating the currently running judged rerun inputs.
Use when: deciding the next chapter-scoped excerpt eval surface, understanding what was already reused versus newly needed, or resuming the v1.1 retune lane after the live rerun merges.
Not for: long-span accumulation design, active live-run control, or stable evaluation constitution.
Update when: the fixed roster changes, the reuse/fill policy changes, the shortfall is resolved, or the draft is promoted into the next judged excerpt surface.

## Safety Rule
- Do not mutate the currently running notes-guided judged rerun inputs in place until the active retry3 shards finish and the explicit merge completes:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_human_notes_guided_excerpt_eval_v1_draft.json`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_human_notes_guided_dataset_v1_excerpt_en_reviewed_cluster_freeze_20260404`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_human_notes_guided_dataset_v1_excerpt_zh_reviewed_cluster_freeze_complete_20260404`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_human_notes_guided_excerpt_eval_v1_judged_parallel_retry1_20260405`
- V1.1 therefore writes only new draft outputs:
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

## Current Draft Result
- Fresh draft manifest:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_excerpt_surface_v1_1_draft.json`
- Fresh draft summary:
  - `reading-companion-backend/state/dataset_build/build_runs/excerpt_surface_v1_1_20260405/excerpt_surface_v1_1_summary.json`
  - `reading-companion-backend/state/dataset_build/build_runs/excerpt_surface_v1_1_20260405/excerpt_surface_v1_1_summary.md`
- Current reuse-only draft counts:
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

## Known Shortfall
- `nawaer_baodian_private_zh__22` is still below the v1.1 honest-short floor:
  - current reused count: `5`
  - floor: `6`
- This means the draft is already good enough to quantify the next excerpt surface and its ROI, but it should not become the next judged default excerpt surface until one targeted fill repair/review finishes or an explicit defer decision records why the chapter remains short.

## Next Move
- Let the active notes-guided judged rerun finish and merge.
- Archive that run as evidence only.
- Then decide one narrow v1.1 follow-up for `nawaer_baodian_private_zh__22`:
  - targeted fill repair/review inside the same chapter
  - or explicit defer with the shortfall kept honest in the draft
- After that, run the new-surface smoke and then the next judged local excerpt comparison on the v1.1 manifest rather than on the old 8-unit notes-guided surface.
