# Ingest Recall And Digest Memory Context Design

Purpose: design the next Unit Memory slice after the bottom hybrid retrieval framework: how Ingest expresses prior-reading recalls, how those recalls drive retrieval, and how retrieved Unit Memory should later enter Digest context.
Use when: designing or implementing bounded multi-recall Ingest output, retrieval aggregation across recalls, or Digest retrieved-memory XML context.
Not for: the already-landed Unit Memory ledger / FTS5 / sqlite-vec bottom framework, evaluation claims, or evidence-catalog updates.
Update when: Ingest recall wording, recall output schema, retrieval aggregation, retrieved-memory card shape, or Digest context rules change.

## Status

- Date: `2026-06-02`
- Status: design draft for the next implementation slice.
- Current live baseline:
  - `DEC-110` implemented the Unit Memory ledger, FTS5 text retrieval, optional sqlite-vec vector retrieval, retrieval mode config, and trace.
  - Current live Ingest still emits at most one `memory_query`.
  - Current retrieval result is trace-only and is not injected into Digest XML.
- Proposed next change:
  - Replace model-facing `memory_query` with bounded `memory_recalls[]`.
  - Keep retrieval execution in Reading Runner.
  - Add Digest retrieved-memory context only after recall and retrieval packaging are implemented deliberately.
- Evaluation status: no eval run, no evidence-catalog update.

## Design Claim

Ingest should not be prompted as a query generator.

Ingest is the same Reader, at the moment just before careful reading. After choosing the next source unit, it should notice what the selected unit naturally asks the reader to remember from earlier reading.

Runtime can use those recalls as retrieval queries, but the model-facing act should be reader-shaped:

- not "generate search queries"
- not "request a tool"
- not "summarize prior context"
- but "what should I remember before I read this unit carefully?"

This preserves the product posture: retrieval serves continuous reading rather than turning Ingest into a search operator.

## Scope

This design covers:

- Ingest prompt wording for prior-reading recall
- multi-recall output shape
- how recalls map to retrieval inputs
- how multiple recall result lists should be merged
- how retrieved Unit Memory should be represented to Digest
- prompt/context guardrails for Digest once retrieved memory is injected

This design does not cover:

- changing the Unit Memory ledger entry shape
- changing the FTS5/sqlite-vec storage stack
- adding frontend controls
- running eval
- evidence catalog updates

## Ingest Prompt Design

### Current Problem

The current live prompt says Ingest should write one memory retrieval query.

That is operationally clear, but it creates two problems:

- It frames Ingest as a retrieval/query generator rather than as the Reader preparing to continue reading.
- One query can collapse multiple distinct recall needs into a single muddy text string.

For example, one selected unit may contain:

- a returning person
- a renewed relationship pressure
- a repeated image
- a concept or claim that earlier units established

Packing all of those into one query weakens both lexical and dense retrieval. It can also cause the model to enumerate nouns instead of expressing actual recall needs.

### Target Instruction Block

Replace the current `RequestMemorySupport` instruction with a reader-facing recall block.

Recommended XML child under `Instruction`:

```xml
<RecallPriorReading>
...
</RecallPriorReading>
```

Target text:

```text
After choosing the next source unit, notice whether this unit naturally calls back to anything already read.

A recall is not a tool request and not a summary task. It is a concise description of something from earlier reading that would help you read the selected unit continuously now.

Write recalls only when the selected unit gives you a real reason to remember earlier reading: a returning person, place, object, concept, question, image, scene, argument, contrast, relationship, or unresolved pressure.

Each recall should name the concrete source footing in the selected unit and the kind of earlier reading it asks to remember.

Do not list every name or noun. Do not split mechanically by entity. Create separate recalls only when the selected unit contains distinct recall needs.

Return zero to three recalls. If nothing in the selected unit asks for earlier memory, return an empty list.
```

### Current Step Adjustment

The `CurrentStep` wording should also avoid "query" language.

Target direction:

```text
Your work in this call is to select the next forward source unit that you should read carefully in the Digest step.

After selecting it, briefly name any earlier reading that this unit makes you want to remember before Digest reads it closely.
```

### Context Use Guide Adjustment

The `RetrievalSurface` remains empty until runtime injects available retrieved memory into Digest, not Ingest.

Target direction:

```text
- the visible source preview is primary
- book identity is orientation, not source text
- `RetrievalSurface` is intentionally empty here
- prior-reading recall here means describing what should be remembered; runtime performs retrieval after the boundary is accepted
```

## Ingest Output Contract

### Proposed Shape

Replace:

```json
{
  "memory_query": {
    "query_version": "unit_memory_query.v1",
    "query_text": "...",
    "basis": "selected_source_unit"
  }
}
```

With:

```json
{
  "memory_recalls": [
    {
      "recall_id": "r1",
      "recall_text": "...",
      "basis": "selected_source_unit"
    }
  ]
}
```

Full output:

```json
{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "...",
  "memory_recalls": [
    {
      "recall_id": "r1",
      "recall_text": "...",
      "basis": "selected_source_unit"
    }
  ]
}
```

### Field Semantics

- `memory_recalls`
  - zero to three recall descriptions
  - empty list means Ingest intentionally found no prior-reading recall need
- `recall_id`
  - stable local id within this Ingest result
  - recommended values: `r1`, `r2`, `r3`
- `recall_text`
  - reader-facing recall description that runtime can use as retrieval text
  - should combine concrete selected-unit cues with the kind of earlier reading needed
  - should not be a question for Digest to answer
- `basis`
  - `selected_source_unit` for the first version

### Good Recall Examples

```text
the earlier relationship between A and B before this renewed confrontation
```

```text
the previous seaside silence scene that gives this quiet exchange emotional continuity
```

```text
the earlier definition of value judgment that this paragraph now applies to a concrete case
```

### Poor Recall Examples

Too broad:

```text
everything about loneliness and growth in this chapter
```

Too entity-list-like:

```text
A B sea station mother promise
```

Too tool-shaped:

```text
search memory for all references to A
```

Too Digest-shaped:

```text
explain what this paragraph means
```

## Runtime Mapping

### Recall To Retrieval Query

The model-facing shape is `memory_recalls[]`.

Runtime may map each recall to an internal retrieval query:

```json
{
  "query_version": "unit_memory_recall_query.v1",
  "query_text": "<recall_text>",
  "basis": "selected_source_unit",
  "recall_id": "r1"
}
```

The term `query` should remain runtime/internal. Prompt wording should stay with "recall".

### Empty Recall Semantics

An empty `memory_recalls` list is meaningful.

If boundary acceptance succeeds and Ingest returns `memory_recalls: []`, runtime should skip long-distance Unit Memory retrieval for that cycle rather than manufacturing a fallback query.

Fallback should be used only when:

- the recall field is missing or malformed
- a retry/fallback changes the accepted source unit enough that the original recalls no longer apply
- runtime needs diagnostic continuity for a degraded Ingest response

When fallback is used, it should be recorded as runtime fallback, not as model-authored recall.

### Boundary Retry / Fallback

If the boundary returned by Ingest cannot be resolved and runtime retries Ingest, use recalls from the accepted retry result.

If runtime deterministic fallback changes the accepted source unit after Ingest, discard model recalls and either:

- derive one fallback retrieval query from the accepted source unit excerpt, or
- skip retrieval if the fallback source unit is too short or structurally uninformative

Trace should distinguish:

- `ingest_recall`
- `retry_ingest_recall`
- `runtime_source_text_fallback`
- `skip_empty_recalls`
- `skip_unusable_fallback`

## Multi-Recall Retrieval Architecture

### Retrieval Execution

For each recall:

1. Build one internal retrieval query from `recall_text`.
2. Run FTS5 lexical retrieval.
3. If mode is `hybrid`, run query embedding + sqlite-vec KNN when available.
4. Keep per-recall candidate lists.
5. Fuse and aggregate across recall ids.

### Aggregation

The current Unit Memory retriever already aggregates document candidates by unit. Multi-recall retrieval should extend that path.

Recommended flow:

```text
memory_recalls[]
  -> per recall lexical candidates
  -> per recall dense candidates
  -> per recall/channel ranked lists
  -> RRF over (recall_id, channel) lists
  -> unit-level aggregation
  -> recent-neighbor exclusion and dedupe
  -> compact retrieved-memory cards for Digest
```

### Why Multi-Recall Instead Of One Query

Multiple recalls are useful when the selected unit has distinct recall needs.

They are not useful when they merely enumerate entities. The model should not create one recall per noun, name, or object unless each one asks for a different kind of earlier reading.

### First Budgets

Initial recommendation:

- `max_recalls_per_ingest = 3`
- per recall lexical top-k: lower than current single-query top-k, for example `40`
- per recall dense top-k: lower than current single-query top-k, for example `40`
- aggregate final retrieved units: keep current small context cap, for example `max 6` cards for Digest
- skip vector work entirely in `text_only` mode
- cache query embeddings per recall text

These numbers should be treated as calibration defaults, not product-quality claims.

### Trace Additions

`unit_memory_retrieval_trace.jsonl` should record:

- accepted source unit id / span id
- recall count
- per recall:
  - `recall_id`
  - `recall_text`
  - query source
  - lexical candidate count
  - dense candidate count
  - degradation reason
- aggregated selected units
- which recalls matched each selected unit
- final retrieval mode / effective mode
- latency breakdown

## Digest Retrieved-Memory Context

### Placement

Retrieved Unit Memory should enter Digest as context, not as instruction.

Recommended placement:

```xml
<ReadingState>
  ...
  <RecentReadingMemory>...</RecentReadingMemory>
  <RetrievedUnitMemory>...</RetrievedUnitMemory>
</ReadingState>
```

Rationale:

- It is prior reading state, not a new task.
- Digest's task remains Understanding / Response / Annotation.
- Retrieved memory should help continuity without becoming the object of reading.

### Candidate Card Shape

Each retrieved prior unit should become one compact card.

Candidate XML shape:

```xml
<MemoryCard unit_id="..." unit_index="..." chapter_ref="..." matched_recalls="r1 r2">
  <PriorSourceExcerpt>...</PriorSourceExcerpt>
  <PriorUnderstanding>...</PriorUnderstanding>
  <PriorResponse>...</PriorResponse>
  <PriorAnnotations>
    <Annotation>
      <Quote>...</Quote>
      <Note>...</Note>
    </Annotation>
  </PriorAnnotations>
</MemoryCard>
```

Field guidance:

- `PriorSourceExcerpt`
  - short source excerpt from the earlier accepted unit
  - included only when it helps source grounding
- `PriorUnderstanding`
  - the main compact memory from that earlier unit
  - usually the highest-value field for Digest continuity
- `PriorResponse`
  - optional; include when it carries a useful reader impression or unresolved pressure
- `PriorAnnotations`
  - optional; include only the most relevant 0-2 annotations from that prior unit
- `matched_recalls`
  - shows why the card was retrieved without exposing scores

### What Not To Include

Do not expose raw retrieval scores, RRF internals, embedding distances, FTS snippets with markup, or full previous unit text by default.

Do not dump every matched document. Digest should receive compact prior-reading support, not a retrieval audit.

### Digest Instruction Adjustment

Digest's `ContextUseGuide` should explain retrieved memory softly but clearly:

```text
Let RetrievedUnitMemory help you remember earlier reading when it genuinely clarifies the current source unit.

Do not treat retrieved memory as the current source text. The current unit remains primary.

Use retrieved memory for continuity, contrast, callback, and unresolved pressure, but do not force a connection when the current unit does not support it.
```

### Relationship To Recent Reading Memory

Recent Reading Memory remains the near-neighbor continuity layer.

Retrieved Unit Memory is for farther or non-neighbor recall. Runtime should dedupe against directly carried Recent Reading Memory so Digest does not receive the same prior unit twice.

Recommended ordering inside Digest context:

1. Recent Reading Memory
2. Retrieved Unit Memory
3. Current Focus / Current Unit

The current unit remains the object of reading regardless of context ordering.

## Retrieval Result Packaging

### Unit-Level Cards, Not Doc-Level Cards

Digest should receive unit-level memory cards.

Retrieval docs are internal matching surfaces. If source, understanding, response, and annotation documents from the same prior unit all match, Digest should see one prior unit card with selected fields, not four separate cards.

### Selection Within A Unit

For each selected unit:

- always include `PriorUnderstanding` when non-empty
- include a clipped prior source excerpt when the source document was one of the best matches
- include `PriorResponse` only if it was matched or compact enough
- include annotations only if annotation docs matched or if the annotation quote is strongly tied to the recall

### Dedupe And Suppression

Suppress:

- current unit
- recent-neighbor units already carried by Recent Reading Memory
- duplicate units across recalls
- cards with only weak response matches and no source/understanding support

## Open Questions

- Should `memory_recalls[]` include a separate `source_cues[]` field, or is `recall_text` enough?
- Should runtime skip retrieval when `memory_recalls` is empty, or should there be an operator option to always run source-text fallback?
- Should Digest see `matched_recalls`, or should that remain audit-only?
- How should card budget change for fiction vs argument-heavy nonfiction?
- Should `PriorSourceExcerpt` be generated from matched docs or from the whole accepted source unit clipped around matching text?
- Should annotations be included by default, or only when the annotation surface contributed to retrieval?
- What is the review rubric for a good recall: coverage of relevant prior units, absence of noisy recall, or downstream Digest usefulness?

## Current Recommendation

Move the next implementation from single model-facing `memory_query` to bounded model-facing `memory_recalls[]`.

Prompt Ingest as a reader noticing what the selected unit asks it to remember, not as a query generator. Allow zero to three recalls. Runtime maps each recall to an internal retrieval query, retrieves per recall, fuses across recall/channel lists, aggregates by Unit Memory Entry, dedupes against recent memory, and eventually packages compact unit-level cards for Digest.

For Digest, introduce `RetrievedUnitMemory` under `ReadingState`, not under `Instruction`. Give Digest compact prior-unit cards and tell it to use them only for continuity where the current source unit supports the connection.
