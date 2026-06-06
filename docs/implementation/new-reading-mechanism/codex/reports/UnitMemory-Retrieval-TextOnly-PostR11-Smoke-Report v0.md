# Unit Memory Retrieval Text-Only Post-R11 Smoke Report v0

Purpose: summarize the post-R10/R11 no-judge diagnostic smoke for Unit Memory retrieval mechanics and trace observability.
Use when: deciding whether the next repair should target retrieval mechanics or recall relevance.
Not for: formal evaluation scoring, evidence-catalog promotion, or product-quality claims.

## Run Boundary

- run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606`
- job id: `bgjob_unit_memory_text_only_smoke_xidaduo_post_r11_20260606`
- segment: `xidaduo_private_zh__segment_1`
- mode: `text_only`
- status: intentionally stopped after rendered retrieved unit ids were captured
- health packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606/analysis/unit_memory_retrieval_health/summary.json`
- review packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606/analysis/unit_memory_retrieval_review/README.md`

This run is diagnostic repair evidence only. It did not generate `summary/aggregate.json`, `summary/report.md`, or `summary/llm_usage.json`, and it does not update the evidence catalog.

## Health Result

The health packet status is `ok`.

- Unit Memory entries: `47`
- retrieval docs: `293`
- retrieval rows: `54`
- ReadingMemory selection rows: `47`
- selected Unit Memory count: `18`
- renderable selected Unit Memory count: `11`
- retrieved lines rendered into Digest `ReadingMemory`: `6`
- rendered retrieved unique unit count: `6`
- dense vector rows: `0`, expected for `text_only`

The rendered retrieved ids are now directly visible in trace:

```text
u000010
u000009
u000007
u000006
u000003
u000002
```

This proves R11's trace-observability repair in live artifacts.

## Relevance Finding

R10 did not break text-only retrieval. The observed prompt-visible retrieved units all had `unit_understanding` among their matched surfaces, so the specific post-R9 failure mode of auxiliary-surface-only rendered pollution was reduced in this observed event.

However, the retrieved memory is still broad. The current unit is Buddha's sermon in Jetavana and the acceptance of new followers. The rendered prior memory mostly recalls Siddhartha and Govinda's earlier relationship, Siddhartha's spiritual thirst, and the decision to leave home for the Samanas. These memories are relevant to continuity, but they are not the most precise doctrinal recall for the sermon itself.

This moves the next repair layer from mechanical retrieval / rendering to recall specificity and selection relevance.

## Interpretation

Current text-only status:

- storage/indexing: working
- recall-to-retrieval execution: working
- selection/renderability: working
- Digest `ReadingMemory` rendering: working
- rendered unit trace ids: working
- precise relevance: still needs calibration

Hybrid dense status remains unchanged:

- sqlite-vec local load path was repaired earlier
- dense retrieval still cannot be validated until local Ollama / Qwen embedding service is reachable

## Next Move

Do not tune general retrieval mechanics again before reviewing recall specificity. The next likely repair should inspect Ingest's recall text for this event and ask:

- Did Ingest ask for the right prior-reading memory?
- Did broad protagonist recall crowd out the more precise Buddhist-doctrine / teaching-content recall?
- Should recall wording encourage fewer broad character-background recalls when the current unit's primary content is doctrinal or argumentative?

After any recall-specificity calibration, rerun a small no-judge `text_only` smoke and compare rendered retrieved unit ids against this post-R11 baseline.
