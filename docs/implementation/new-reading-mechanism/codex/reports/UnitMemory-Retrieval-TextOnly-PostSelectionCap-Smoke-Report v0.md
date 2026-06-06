# UnitMemory Retrieval TextOnly PostSelectionCap Smoke Report v0

Date: `2026-06-06`

## Scope

- run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606`
- job id: `bgjob_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606`
- segment: `xidaduo_private_zh__segment_1`
- mode: `text_only`
- status: diagnostic only; intentionally stopped after enough selection-cap evidence was collected
- catalog status: not cataloged; no evidence-catalog update

## Artifact Pointers

- health packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606/analysis/unit_memory_retrieval_health/summary.json`
- health report: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606/analysis/unit_memory_retrieval_health/README.md`
- review packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606/analysis/unit_memory_retrieval_review/README.md`

## Health Snapshot

- health status: `ok`
- Unit Memory entries: `46`
- retrieval docs: `287`
- retrieval rows: `49`
- ReadingMemory selection rows: `46`
- selected unit count: `8`
- renderable selected unit count: `7`
- non-renderable selected unit count: `0`
- selected-but-not-rendered count: `6`
- retrieval-layer suppressed unit count: `9`
- retrieved line total: `2`
- rendered retrieved unique unit count: `2`
- rendered retrieved unit ids: `u000002`, `u000004`
- vector rows: `0`, expected for `text_only`

## What Passed

- The per-recall selection cap is live in runtime traces.
- The key selected retrieval event recorded:
  - `selection_config.max_units_per_recall_to_digest_context = 6`
  - `candidate_units = 15`
  - `selected_units = 6`
  - `per_recall_selection_limit_exceeded = 8`
- Digest `ReadingMemory` did not lose retrieved memory entirely:
  - `retrieved_line_total = 2`
  - rendered retrieved ids were machine-readable.
- Retrieved prompt-facing memory remained Understanding-only.

## What The Review Shows

The rendered event was `src:c1:p128@0-p130@64`, where Siddhartha and Govinda recognize the Buddha and follow him.

The selected recall was broad but relevant to the immediate continuity:

```text
悉达多和乔文达作为沙门修行后，决定离开沙门去朝圣，他们此行的目的正是寻找并见到佛陀世尊。这段叙事承接了他们的朝圣之旅，遇到了佛陀。
```

After selection cap and hot-memory dedupe, only two long-distance retrieved Understanding lines reached Digest:

- `u000004`: Siddhartha and Govinda meditate under the banyan tree and recite the `Om` / bow-arrow-Brahman formula.
- `u000002`: Govinda's early devotion to Siddhartha and desire to follow him.

The cap therefore reduced a broad candidate set without making retrieval disappear. However, the run also exposed two contract issues:

- Some later Chinese-source recalls were written in English, which weakens `text_only` FTS retrieval.
- Some model-emitted recall `basis` values drifted away from the intended `selected_source_unit`.

These are Ingest recall-contract issues, not a reason to change the Unit Memory architecture.

## Follow-Up

- Implement Ingest v6 recall contract tightening:
  - write `recall_text` in the same primary language as the current source text
  - preserve source-form names, titles, and technical terms
  - require model-side recall `basis = selected_source_unit`
- Keep runtime fallback basis `runtime_source_text_fallback` for malformed or boundary-fallback cases.
- Rerun a small no-judge `text_only` smoke after Ingest v6 if recall-language drift continues to affect retrieval.
- Hybrid dense retrieval remains environment-blocked by missing/unreachable local Ollama / Qwen embedding service.
