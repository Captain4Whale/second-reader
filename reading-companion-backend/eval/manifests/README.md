# Evaluation Manifests

Purpose: store tracked corpus manifests and local-source reference files for benchmark and evaluation work.

Use this directory for:
- corpus manifests
- source-book inventory files
- local-path reference files that point to private/local full-book corpora
- bilingual corpus split definitions

Recommended subdirectories:
- `source_books/`
- `corpora/`
- `splits/`
- `local_refs/`

Do not use this directory for:
- transient user uploads
- machine-generated run outputs
- runtime book copies
- checked-in full commercial book files

Related territories:
- transient uploads: `reading-companion-backend/state/uploads/`
- durable local source library: `reading-companion-backend/state/library_sources/`
- tracked excerpt datasets: `reading-companion-backend/eval/datasets/`
- machine-generated benchmark runs: `reading-companion-backend/eval/runs/`
