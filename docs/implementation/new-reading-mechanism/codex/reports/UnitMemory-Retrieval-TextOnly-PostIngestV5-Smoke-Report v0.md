# Unit Memory Retrieval Text-Only Post-Ingest-v5 Smoke Report v0

Purpose: summarize the post-Ingest-v5 no-judge diagnostic smoke for Unit Memory recall specificity.
Use when: deciding the next repair slice after Ingest recall prompt calibration.
Not for: formal evaluation scoring, evidence-catalog promotion, or product-quality claims.

## Run Boundary

- run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606`
- job id: `bgjob_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606`
- segment: `xidaduo_private_zh__segment_1`
- mode: `text_only`
- prompt change under test: `attentional_v2.ingest.v5` / promptset `attentional_v2-phase6-v55`
- status: intentionally stopped after enough retrieval-specificity evidence was captured
- health packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606/analysis/unit_memory_retrieval_health/summary.json`
- review packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606/analysis/unit_memory_retrieval_review/README.md`

This run is diagnostic repair evidence only. It was stopped with SIGTERM after diagnostic evidence was collected, did not generate `summary/aggregate.json`, `summary/report.md`, or `summary/llm_usage.json`, and does not update the evidence catalog.

## Health Result

The health packet status is `ok`.

- Unit Memory entries: `68`
- retrieval docs: `445`
- retrieval rows: `75`
- ReadingMemory selection rows: `68`
- selected Unit Memory count: `50`
- renderable selected Unit Memory count: `32`
- retrieved lines rendered into Digest `ReadingMemory`: `27`
- rendered retrieved unique unit count: `19`
- dense vector rows: `0`, expected for `text_only`

## Recall-Specificity Finding

Ingest v5 did not shut retrieval off. It produced prompt-visible retrieved Understanding later in the run, so the repair did not break the text-only retrieval/rendering chain.

It did reduce the specific post-R11 over-broad event around Buddha's sermon. In the post-R11 smoke, the sermon / follower-acceptance area rendered broad Siddhartha / Govinda continuity memory. In the post-Ingest-v5 smoke, the comparable Buddha-sermon area produced no long-distance retrieved lines, which is consistent with the new instruction to avoid broad character-background recall when only generic continuity would be requested.

However, the later retrieved events still show a second problem:

- Some recalls are now more semantically focused, such as the `self / Atman / Maya` recall when Siddhartha turns toward knowing himself.
- The selected/rendered set can still become too large and include many broad early-life units, because lexical matching plus a large retrieved-memory budget can admit all units that partially support the recall.
- A later Kamala-introduction event still selected many early Siddhartha / ascetic-life memories even though the recall basis was narrower.

So Phase 6 is partially validated but not complete: recall prompting improved the worst broad-sermon pattern, but selection relevance still needs tightening so a focused recall does not expand into a broad life-history pack.

## Interpretation

Current text-only status:

- storage/indexing: working
- recall-to-retrieval execution: working
- selection/renderability: working
- Digest `ReadingMemory` rendering: working
- rendered unit trace ids: working
- recall specificity: improved for the post-R11 sermon baseline, still too broad in later events

Hybrid dense status remains unchanged:

- sqlite-vec local load path was repaired earlier
- dense retrieval still cannot be validated until local Ollama / Qwen embedding service is reachable

## Next Move

Do not revert the Ingest-v5 recall calibration. It improved a real failure mode without disabling retrieval.

The next repair should target retrieval selection / budget discipline for focused recalls:

- prefer fewer retrieved units per recall when the recall is already specific
- make the selected set favor the highest-scoring Understanding matches rather than filling the whole long-memory budget with broad partially related history
- review whether per-recall caps or a minimum score / rank gap should apply before rendering retrieved lines
- keep Digest `ReadingMemory` Understanding-only and do not revive raw source backread, Detour, or concept/thread memory

After a selection-tightening repair, rerun a small no-judge `text_only` smoke and compare:

- post-R11: `6` retrieved lines, broad sermon continuity
- post-Ingest-v5: `27` retrieved lines, no broad sermon injection, but later selected sets still broad
- next target: nonzero retrieved lines with smaller, more directly relevant rendered sets
