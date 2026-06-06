# Unit Memory Retrieval Text-Only Post-R9 Relevance Review v0

Purpose: review whether the first prompt-visible retrieved Unit Memory examples from the post-R9 `text_only` diagnostic are useful enough to continue calibration.
Use when: deciding the next repair slice for `Ingest recalls -> Unit Memory retrieval/selection -> Digest ReadingMemory`.
Not for: formal evaluation scoring, evidence-catalog promotion, or judging Digest prose quality.

## Run Boundary

- run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606`
- segment: `xidaduo_private_zh__segment_1`
- mode: `text_only`
- source packet: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606/analysis/unit_memory_retrieval_review/README.md`
- status: diagnostic only. The registered smoke was intentionally stopped after retrieval-success evidence was collected, so this is not formal eval evidence.

## Mechanical Finding

The non-hybrid retrieval path is no longer broken at the mechanical level.

- Unit Memory entries were written.
- Retrieval docs were indexed.
- Ingest recall traces produced lexical candidates.
- Runtime selected renderable prior Unit Memory entries.
- Digest `ReadingMemory` received retrieved Understanding lines.

The health packet reports:

- `selected_unit_count = 71`
- `renderable_selected_unit_count = 29`
- `retrieved_line_total = 45`
- `non_renderable_selected_unit_count = 0`

## Relevance Review

### Strong Continuity Cases

Several examples are genuinely useful continuity memory:

- `src:c1:p122@0-p125@63` recalls Siddhartha and Govinda's shared journey to find the Buddha. Selected prior units include:
  - `u000012`: Siddhartha decides to join the Samanas, and Govinda recognizes that this is both Siddhartha's path and his own.
  - `u000003`: Govinda's loyalty to Siddhartha is established.
  - `u000021` / `u000022`: Govinda follows Siddhartha into the ascetic journey.
- `src:c1:p172@0-p172@2` recalls the teacher-seeking arc as Siddhartha turns toward self-awakening. Selected prior units include:
  - `u000030`: Siddhartha questions whether Samana training truly brings progress.
  - `u000006`: Siddhartha's desire to find the inner source of the self is established.

These are the kind of prior Understanding lines the mechanism is supposed to recover: earlier established relationships, quests, and unresolved seeking that help the current unit remain continuous.

### Over-Broad Entity Recall

Some results are plausible but repetitive. Recalls mentioning `乔文达`, `佛陀`, or `沙门` repeatedly select the same early relationship/path units.

This is not yet a correctness failure because those units are often relevant, but it can waste the retrieved-memory budget. Future tuning should watch whether the same broad protagonist memories crowd out more specific prior claims.

### Auxiliary-Surface Pollution

The review packet shows a more actionable problem: retrieval can select a unit because auxiliary surfaces match, then render that unit's Understanding into Digest.

Examples:

- `src:c1:p151@0-p155@409`
  - the current unit concerns Siddhartha's objection to the Buddha's doctrine.
  - selected units include `u000023` and `u000029`, whose matched surfaces were `unit_response`.
  - their rendered Understanding content is mostly terminology / practice background, not the strongest continuity memory for this doctrinal objection.
- `src:c1:p157@378-p161@42`
  - the current unit concerns Siddhartha's worry that doctrine, love for the Buddha, and Sangha could become a new false self.
  - selected prior unit `u000025` is an Upanishad / Brahman terminology note; it is related at the level of Indian philosophy terms, but weak as direct continuity support.
- `src:c1:p167@0-p171@29`
  - the current unit is a note cluster about Jetavana, Anathapindika, the Four Noble Truths, and the Eightfold Path.
  - selected prior unit `u000025` is another terminology note. This is understandable lexical matching, but it risks making `ReadingMemory` into a term-note chain rather than reading continuity.

This is not caused by raw prior source text entering Digest. Digest still receives Understanding-only memory. The problem is selection: source / response / annotation surfaces can help select an Entry, but their weights should not dominate `unit_understanding` when deciding which Entry's Understanding enters `ReadingMemory`.

## Repair Landed From This Review

Two small repairs were made after this review:

1. Lexical surface weights now prioritize `unit_understanding`.
   - `unit_understanding.lexical` is higher than `unit_source`, `unit_annotation`, and `unit_response`.
   - This restores the design intent that Understanding is the primary retrieval and prompt-facing memory surface, while source / response / annotation remain auxiliary match surfaces.
2. `unit_memory_reading_memory_selection` trace now records the exact `rendered_retrieved_units` and `rendered_retrieved_unit_ids`.
   - Future health reports can identify which selected Unit Memory ids actually survived hot-memory dedupe and budget trimming into prompt-visible Digest `ReadingMemory`.
   - This removes a blind spot in the post-R9 review packet.

## Remaining Questions

- Does the new Understanding-prioritized lexical weighting still retrieve enough relevant memories in a live smoke?
- Does it reduce terminology / note-cluster pollution without losing useful source-cue recall?
- Are broad protagonist recalls crowding out more specific continuity memories?
- Should Ingest recall wording be calibrated after the next smoke, or is the selection/ranking layer enough for the current failure?

## Next Move

Run a small no-judge `text_only` smoke after the surface-weight and trace-observability repair. The acceptance question should be narrower than formal evaluation:

```text
Do retrieved Understanding lines still appear in Digest ReadingMemory, and are the rendered retrieved unit ids mostly relevant continuity memories rather than auxiliary-surface artifacts?
```

Hybrid dense retrieval remains separately blocked by the local Ollama / Qwen embedding environment.
