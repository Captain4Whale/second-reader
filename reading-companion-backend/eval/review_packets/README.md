# Review Packets

Purpose: make dataset review executable without a frontend UI.

This directory contains human-review packets for benchmark datasets.

## Lifecycle
- `pending/`
  - packets exported by Codex and waiting for human review
- `archive/`
  - packets already imported back into the dataset with their review CSV preserved

## Packet Contents
Each packet folder should contain:
- `packet_manifest.json`
- `cases.review.csv`
- `cases.preview.md`
- `cases.source.jsonl`
- `README.md`

## Human Workflow
1. Open `cases.preview.md` for the readable view.
2. Edit only the `review__...` columns in `cases.review.csv`.
3. Save the file in place.
4. Tell Codex the packet is ready.

Codex then runs:
- `eval/attentional_v2/import_dataset_review_packet.py --packet-id <packet_id> --archive`

## Why This Exists
- The current benchmark family still contains builder-curated cases.
- Some benchmark problems are dataset problems rather than mechanism problems.
- A fast packet workflow makes it practical to improve dataset quality before we trust broader evaluations too much.
