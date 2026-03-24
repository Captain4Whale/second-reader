# Evaluation Datasets

Purpose: define how tracked benchmark datasets are organized on disk.

This directory is family-first, not mechanism-first.

Conceptual rule:
- benchmark families are defined by evaluation role, not by storage location
- a package under `eval/datasets/` and a package under `state/eval_local_datasets/` may belong to the same benchmark family if they differ only by `storage_mode`

## Family Roots
- `excerpt_cases/`
  - local passage or short-span benchmark inputs
- `chapter_corpora/`
  - chapter-scale comparison inputs
- `runtime_fixtures/`
  - resume, runtime, and operational-gate fixtures
- `compatibility_fixtures/`
  - persisted public-surface and migration-audit fixtures
- `templates/`
  - optional package templates or reference examples

## Legacy Note
- Older benchmark packages such as `subsegment_benchmark_v1/` may still exist at the top level.
- Treat those as legacy layouts.
- New dataset packages should follow the family-first structure documented here.

## Package Rule
Each concrete dataset package lives under exactly one family root:

- `eval/datasets/<family>/<dataset_id>/`

Examples:
- `eval/datasets/excerpt_cases/attentional_v2_excerpt_en_v1/`
- `eval/datasets/chapter_corpora/cross_mechanism_chapters_zh_v1/`
- `eval/datasets/runtime_fixtures/attentional_v2_runtime_en_v1/`
- `eval/datasets/compatibility_fixtures/attentional_v2_shared_v1/`

## Required Files Per Dataset Package
Every concrete dataset package must include:
- `manifest.json`
- one primary payload file:
  - `cases.jsonl` for excerpt datasets
  - `chapters.jsonl` for chapter corpora
  - `fixtures.jsonl` for runtime or compatibility fixtures

Optional files:
- `README.md`
- `judge_notes.md`
- small checked-in helper assets that are part of the dataset itself

Do not put machine-generated benchmark results in a tracked dataset package.

## Manifest Minimum
Each `manifest.json` should record at least:
- `dataset_id`
- `family`
- `language_track`
- `version`
- `description`
- `primary_file`
- `question_ids`
- `source_manifest_refs`
- `split_refs`

Recommended additional field:
- `storage_mode`
  - `tracked`
  - `local-only`

## Language Tracks
Use:
- `en`
- `zh`
- `shared`

Rule:
- Keep English and Chinese as separate dataset tracks.
- Use `shared` only for language-agnostic fixture packages.

## Relationship To `eval/manifests/`
Datasets and manifests are different:

- `eval/datasets/`
  - tracked benchmark inputs actually consumed by benchmark code
- `eval/manifests/`
  - source-book inventories
  - corpus selection manifests
  - split definitions
  - local-path reference files for private/local corpora and local-only dataset packages

## Private-Local Mirror
- When a package contains copyrighted or otherwise private source text, keep it out of this tracked tree.
- Put the package instead under:
  - `state/eval_local_datasets/<family>/<dataset_id>/`
- Keep the same family roots and package contract there so tracked and local packages stay structurally comparable as one benchmark family across two storage modes.

Do not duplicate source-book inventory metadata into every dataset package.
