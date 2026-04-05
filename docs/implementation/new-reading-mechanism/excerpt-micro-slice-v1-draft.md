# Excerpt Micro-Slice V1 Draft

Purpose: define the first ROI-first judged excerpt micro-slice used for fast iteration while `attentional_v2` throughput repair is underway.
Use when: deciding the next excerpt-scale judged harness, resuming the bounded throughput-repair lane, or checking how this micro-slice fits into the broader excerpt roadmap.
Not for: replacing the broader excerpt surface, changing the stable evaluation constitution, or deciding the long-span benchmark.
Update when: the fixed chapter roster changes, the slice is expanded, or it is retired in favor of a later micro-harness.

## Role In The Roadmap
- The next excerpt work is intentionally ordered:
  1. freeze and use this micro-slice as the default judged fast-iteration harness
  2. make bounded `attentional_v2` throughput repairs against this slice
  3. return to the broader excerpt-surface adjustment lane:
     - `excerpt surface v1.1` promotion or honest-short defer
     - then the later larger excerpt-surface / dataset retune
- This draft is therefore a repair harness, not the final excerpt benchmark pointer.

## Safety Rule
- Reuse already reviewed rows only.
- Do not mutate:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_human_notes_guided_excerpt_eval_v1_draft.json`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_human_notes_guided_dataset_v1_excerpt_en_reviewed_cluster_freeze_20260404`
  - `reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_human_notes_guided_dataset_v1_excerpt_zh_reviewed_cluster_freeze_complete_20260404`
- The micro-slice writes only a new manifest:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_excerpt_micro_slice_v1_draft.json`

## Fixed V1 Roster
- `nawaer_baodian_private_zh__22`
  - `5` primary excerpt cases
  - `5` derived `insight_and_clarification` cases
  - chosen because it already yielded the clearest non-placeholder judged evidence in the partial retry3 run and gives mixed pressure in a bounded read
- `xidaduo_private_zh__15`
  - `8` primary excerpt cases
  - `3` derived `insight_and_clarification` cases
  - chosen because it is dense, non-duplicative, and materially cheaper than the heaviest long chapters
- Total:
  - `13` primary excerpt cases
  - `8` derived `insight_and_clarification` cases
- Optional later expansion candidate:
  - `supremacy_private_en__13`

## Why This Slice
- The failed broad reruns taught two different lessons:
  - `attentional_v2` currently has real call-count amplification on excerpt-scale chapter reads
  - low-ROI heavy chapters can occupy the first worker slots long enough to starve higher-value later units
- This slice answers both problems at once:
  - it keeps only chapters that already look worth judging
  - it gives one mixed-pressure chapter and one denser local-text chapter
  - it avoids front-loading the worst long heavy reads while we are still repairing throughput

## Use Rule
- Default next excerpt smoke and judged repair runs should use:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_excerpt_micro_slice_v1_draft.json`
- Do not interpret micro-slice wins or losses as sufficient to settle the full excerpt surface.
- After the bounded throughput-repair loop stabilizes, return to:
  - `docs/implementation/new-reading-mechanism/excerpt-surface-v1-1-draft.md`
  - and then the broader excerpt-surface / dataset adjustment lane already recorded in living docs
