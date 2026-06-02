# Ingest Recall And Digest Memory Context Design

Purpose: design the next Unit Memory slice after the bottom hybrid retrieval framework: how Ingest expresses prior-reading recalls, how the Ingest LLM call invokes retrieval through tools, and how retrieved Unit Memory should later enter Digest context.
Use when: designing or implementing bounded multi-recall Ingest output, the `retrieve_unit_memory` tool loop, retrieval aggregation across recalls, or Digest retrieved-memory XML context.
Not for: the already-landed Unit Memory ledger / FTS5 / sqlite-vec bottom framework, evaluation claims, or evidence-catalog updates.
Update when: Ingest recall wording, tool schema, recall output schema, retrieval aggregation, retrieved-memory card shape, or Digest context rules change.

## Status

- Date: `2026-06-02`
- Status: design draft for the next implementation slice.
- Current live baseline:
  - `DEC-110` implemented the Unit Memory ledger, FTS5 text retrieval, optional sqlite-vec vector retrieval, retrieval mode config, and trace.
  - Current live Ingest still emits at most one `memory_query`.
  - Current retrieval result is trace-only and is not injected into Digest XML.
- Proposed next change:
  - Replace model-facing `memory_query` with bounded `memory_recalls[]`.
  - Let the Ingest LLM call invoke Unit Memory retrieval through an Anthropic-style tool loop.
  - Keep actual retrieval execution, score fusion, source-unit resolution, and artifact writing in Reading Runner/runtime code.
  - Let Ingest see compact retrieval results and select/confirm memory support for Digest without copying retrieved card content into final JSON.
  - Add Digest retrieved-memory context only after recall, tool result packaging, and card selection are implemented deliberately.
- Tool capability note:
  - On `2026-06-02`, a minimal live probe against the configured `MiniMax-M2.7` Anthropic-compatible endpoint succeeded with `tool_use -> tool_result -> final answer`.
  - The probe verifies basic provider support for Anthropic-style tools, not the Reading Companion retrieval tool implementation.
- Evaluation status: no eval run, no evidence-catalog update.

## Design Claim

Ingest should not be prompted as a query generator.

Ingest is the same Reader, at the moment just before careful reading. After choosing the next source unit, it should notice what the selected unit naturally asks the reader to remember from earlier reading.

Runtime can use those recalls as retrieval inputs, but the model-facing act should be reader-shaped:

- not "generate search queries"
- not "summarize prior context"
- but "what should I remember before I read this unit carefully?"

The tool call is an implementation channel, not the product-facing act. Ingest may call `retrieve_unit_memory`, but the prompt should still frame the activity as prior-reading recall in service of continuous reading, not as operating a search interface.

## Scope

This design covers:

- Ingest prompt wording for prior-reading recall
- the Ingest tool loop contract
- multi-recall output shape
- how recalls map to tool inputs and retrieval execution
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

It also keeps the retrieval result outside the Ingest LLM call. That was useful for the bottom-framework slice, but the next slice should let Ingest see the retrieved prior-reading support before the final Ingest result is accepted.

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

A recall is not a search string and not a summary task. It is a concise description of something from earlier reading that would help you read the selected unit continuously now.

Write recalls only when the selected unit gives you a real reason to remember earlier reading: a returning person, place, object, concept, question, image, scene, argument, contrast, relationship, or unresolved pressure.

Each recall should name the concrete source footing in the selected unit and the kind of earlier reading it asks to remember.

Do not list every name or noun. Do not split mechanically by entity. Create separate recalls only when the selected unit contains distinct recall needs.

Return zero to three recalls. If nothing in the selected unit asks for earlier memory, return an empty list.

If you write one or more recalls, call the Unit Memory retrieval tool with those recalls. Use the tool result only to decide which retrieved prior-unit cards should support Digest.
```

### Current Step Adjustment

The `CurrentStep` wording should also avoid "query" language.

Target direction:

```text
Your work in this call is to select the next forward source unit that you should read carefully in the Digest step.

After selecting it, briefly name any earlier reading that this unit makes you want to remember before Digest reads it closely.

When those recalls exist, use the available Unit Memory retrieval tool to bring back compact prior-reading cards before you return the final Ingest JSON.
```

### Context Use Guide Adjustment

The `RetrievalSurface` remains empty in the initial Ingest XML. Retrieved Unit Memory enters the Ingest call through the tool result, not through the initial prompt context.

Target direction:

```text
- the visible source preview is primary
- book identity is orientation, not source text
- `RetrievalSurface` is intentionally empty here
- prior-reading recall here means describing what should be remembered; runtime performs retrieval only through the provided tool
```

## Ingest Tool Loop

### Principle

The retrieval layer should be exposed to Ingest as a typed tool, not as prompt text and not as direct store access.

The LLM decides whether the selected unit calls for prior-reading recall. Runtime remains responsible for:

- resolving the selected source boundary against the visible preview
- executing FTS5 / sqlite-vec retrieval
- applying retrieval mode fallback and degradation handling
- fusing and aggregating results
- writing retrieval traces
- packaging compact prior-unit cards

The model sees the compact tool result and chooses which cards are useful enough to carry toward Digest. It must not receive raw retrieval internals or mutate stored memory.

### Call Sequence

Recommended first implementation:

```text
Initial Ingest XML prompt
  -> model selects a provisional forward boundary and writes 0-3 recalls
  -> if recalls are empty, model returns final JSON without tool use
  -> if recalls are non-empty, model calls retrieve_unit_memory
  -> runtime resolves the boundary, executes Unit Memory retrieval, and returns compact cards
  -> model returns final Ingest JSON with boundary fields, recalls, and selected card ids
  -> Reading Runner accepts/governs the boundary and assembles Digest context from runtime-owned cards
```

This keeps one Ingest LLM call conceptually, even if the transport contains multiple Anthropic Messages turns.

### Tool Name

Use a mechanism-private tool:

```text
retrieve_unit_memory
```

Tool description:

```text
Retrieve compact prior Unit Memory cards that may help the Reader read the selected source unit continuously.
```

### Tool Input

The tool input should include the provisional boundary and the recalls. This lets runtime resolve the selected unit before retrieval, rather than trusting invented source text from the model.

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

The model should not pass selected source text, previous memory ids, SQL, scores, or store names.

### Tool Result

The tool result should be compact and Digest-oriented:

```json
{
  "status": "ok",
  "effective_mode": "hybrid",
  "boundary_resolution": {
    "status": "matched",
    "source_span_id": "..."
  },
  "cards": [
    {
      "card_id": "umc_...",
      "unit_id": "...",
      "unit_index": 12,
      "chapter_ref": "chapter-1",
      "matched_recalls": ["r1"],
      "prior_source_excerpt": "...",
      "prior_understanding": "...",
      "prior_response": "...",
      "prior_annotations": [
        {
          "quote": "...",
          "note": "..."
        }
      ]
    }
  ],
  "degradation_reason": ""
}
```

Allowed statuses:

- `ok`: retrieval ran and returned one or more cards
- `no_recall`: no recalls were supplied
- `no_match`: retrieval ran but no usable prior-unit card remained after filters
- `boundary_unresolved`: runtime could not resolve `end_anchor_text` against the current preview
- `degraded`: retrieval ran with fallback or partial capability, such as lexical-only under `hybrid`
- `error`: runtime tool execution failed in a recoverable way

The tool result should not expose raw scores, RRF internals, embedding distances, SQL, FTS snippets with markup, or full previous unit text.

### Tool Choice And Limits

First implementation defaults:

- allow at most one `retrieve_unit_memory` call per Ingest attempt
- do not allow arbitrary tool names
- if `memory_recalls` is empty, do not call the tool
- if `memory_recalls` is non-empty and the model finalizes without a tool call, runtime should record `tool_not_called` and either retry once or proceed without retrieved cards, depending on implementation risk
- if the tool returns `boundary_unresolved`, runtime should use the existing boundary retry path rather than letting the model perform unbounded repair inside the tool loop
- if the tool returns `degraded` or `error`, Ingest may still return a final boundary result with `memory_support.status` reflecting the degraded state

## Ingest Output Contract

### Final JSON Shape

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
  ],
  "memory_support": {
    "status": "used",
    "selected_card_ids": ["umc_..."],
    "note": "..."
  }
}
```

Full final output:

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
  ],
  "memory_support": {
    "status": "used",
    "selected_card_ids": ["umc_..."],
    "note": "retrieved prior relationship context is relevant"
  }
}
```

The final Ingest JSON should not copy full retrieved card content. Runtime owns the cards and passes them to Digest context after boundary governance.

### Empty Recall Output

When nothing in the selected unit calls for earlier reading:

```json
{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "...",
  "memory_recalls": [],
  "memory_support": {
    "status": "no_recall",
    "selected_card_ids": [],
    "note": ""
  }
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
- `memory_support.status`
  - `used`: tool returned cards and Ingest selected at least one
  - `no_recall`: Ingest found no recall need and did not call the tool
  - `no_match`: tool ran but no useful cards remained
  - `degraded`: tool ran with degraded retrieval capability
  - `tool_not_called`: recalls existed but no tool call completed
  - `error`: retrieval tool failed in a recoverable way
- `memory_support.selected_card_ids`
  - card ids from the tool result that runtime may package into Digest context
  - empty when no retrieved support should be carried
- `memory_support.note`
  - short internal reason for selected cards or degraded/no-match status
  - must not include full card text

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

## Runtime Interaction

### Recalls As Tool Retrieval Inputs

The model-facing shape is `memory_recalls[]`.

During `retrieve_unit_memory` execution, runtime maps each recall to an internal retrieval query:

```json
{
  "query_version": "unit_memory_recall_query.v1",
  "query_text": "<recall_text>",
  "basis": "selected_source_unit",
  "recall_id": "r1"
}
```

The term `query` remains runtime/internal. Prompt wording stays with "recall".

### Empty Recall Semantics

An empty `memory_recalls` list is meaningful.

If Ingest returns `memory_recalls: []`, it should not call `retrieve_unit_memory`. Runtime should skip long-distance Unit Memory retrieval for that cycle rather than manufacturing a fallback query.

Fallback should be used only when:

- the recall field is missing or malformed
- a boundary retry/fallback changes the accepted source unit enough that the original recalls/tool result no longer apply
- runtime needs diagnostic continuity for a degraded Ingest response

When fallback is used, it should be recorded as runtime fallback, not as model-authored recall.

### Boundary Retry / Fallback With Tool Loop

The tool input includes `end_anchor_text`, so runtime can resolve the provisional boundary before retrieval.

If the tool receives an unresolvable boundary:

- do not execute memory retrieval for that tool call
- return `boundary_unresolved` with compact resolution evidence
- let Reading Runner use the existing retry path rather than letting the model perform an unbounded repair loop inside tools

If the boundary returned by the final Ingest result cannot be resolved and runtime retries Ingest, use recalls and tool cards from the accepted retry result only.

If runtime deterministic fallback changes the accepted source unit after Ingest, discard model recalls and either:

- skip retrieved Unit Memory for that cycle, or
- derive one runtime-only fallback retrieval query from the accepted source unit excerpt for diagnostics
- skip retrieval if the fallback source unit is too short or structurally uninformative

Runtime-only fallback retrieval should not be presented as model-selected memory support unless a later explicit design chooses that behavior.

Trace should distinguish:

- `ingest_recall`
- `retry_ingest_recall`
- `tool_retrieve_unit_memory`
- `tool_boundary_unresolved`
- `tool_not_called`
- `runtime_source_text_fallback`
- `skip_empty_recalls`
- `skip_unusable_fallback`

## Multi-Recall Retrieval Architecture

### Retrieval Execution

Retrieval execution happens inside the `retrieve_unit_memory` tool handler.

For each recall supplied to the tool:

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
  -> compact retrieved-memory cards for the tool result
  -> Ingest-selected card ids
  -> runtime-packaged Digest context
```

### Why Multi-Recall Instead Of One Query

Multiple recalls are useful when the selected unit has distinct recall needs.

They are not useful when they merely enumerate entities. The model should not create one recall per noun, name, or object unless each one asks for a different kind of earlier reading.

### First Budgets

Initial recommendation:

- `max_recalls_per_ingest = 3`
- per recall lexical top-k: lower than current single-query top-k, for example `40`
- per recall dense top-k: lower than current single-query top-k, for example `40`
- aggregate final retrieved units: keep current small tool-result cap, for example `max 6` cards
- allow Ingest to select fewer than the tool cap, including none
- skip vector work entirely in `text_only` mode
- cache query embeddings per recall text

These numbers should be treated as calibration defaults, not product-quality claims.

### Trace Additions

`unit_memory_retrieval_trace.jsonl` should record:

- tool call id
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
- cards returned to Ingest
- card ids selected by Ingest for Digest
- final retrieval mode / effective mode
- latency breakdown
- tool-loop status such as `ok`, `no_recall`, `no_match`, `boundary_unresolved`, `degraded`, `tool_not_called`, or `error`

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
- Runtime assembles this context from cards returned by `retrieve_unit_memory` and selected/confirmed by Ingest, not from free-form text in the final Ingest JSON.

### Candidate Card Shape

Each retrieved prior unit should become one compact card.

Candidate XML shape:

```xml
<MemoryCard unit_id="..." unit_index="..." chapter_ref="..." matched_recalls="r1 r2">
  <WhyRemembered>...</WhyRemembered>
  <PriorUnderstanding>...</PriorUnderstanding>
  <PriorResponse>...</PriorResponse>
  <PriorAnnotations>
    <Annotation>
      <Excerpt>...</Excerpt>
      <Note>...</Note>
    </Annotation>
  </PriorAnnotations>
</MemoryCard>
```

Field guidance:

- `WhyRemembered`
  - concise reason derived from the matched Ingest recalls
  - tells Digest why this prior unit was brought back without exposing retrieval scores
- `PriorUnderstanding`
  - the main compact memory from that earlier unit
  - usually the highest-value field for Digest continuity
  - include by default when non-empty
- `PriorResponse`
  - include when non-empty, but keep compact and omit/trim if it repeats `PriorUnderstanding`
- `PriorAnnotations`
  - include only annotations whose own retrieval document contributed to this selected Entry
  - each included annotation carries its bound `Excerpt` plus `Note`
  - default cap: 0-2 annotations per card
- `matched_recalls`
  - shows why the card was retrieved without exposing scores
  - can be included if we want Digest to see the recall reason; otherwise it can remain audit-only while still being stored in trace

### Document-To-Card Policy

All retrieval documents may participate in recall, ranking, fusion, and Entry selection, but they do not all become Digest context.

- `unit_source`
  - participates in lexical and vector retrieval
  - helps the system find relevant Entries
  - does not enter Digest memory cards as prior source text
- `unit_understanding`
  - participates in retrieval
  - enters Digest by default for selected Entries when non-empty
- `unit_response`
  - participates in retrieval
  - enters Digest for selected Entries when non-empty, with compact clipping and duplication control
- `unit_annotation`
  - participates in retrieval
  - enters Digest only when that specific annotation document contributed to the selected Entry
  - carries its bound excerpt and note together

Do not add a separate annotation-specific threshold. Annotation inclusion follows the same retrieval/fusion/Entry-selection process as every other retrieval document; the special rule is only that an annotation is shown if its own document contributed to the selected Entry.

### What Not To Include

Do not expose raw retrieval scores, RRF internals, embedding distances, FTS snippets with markup, or full previous unit text by default.

Do not dump every matched document. Digest should receive compact prior-reading support, not a retrieval audit.

Do not include the raw source text of the previous Unit as a card field. Source text is useful for finding memories, but Digest continuity should be carried by the remembered understanding, response, and selected prior annotations rather than by replaying old source units.

Do not let Ingest rewrite card content into Digest context. Ingest may select card ids; runtime supplies the canonical card text.

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
If Ingest selects a card whose unit is later suppressed by dedupe, runtime should record the suppression in trace and omit the card from Digest.

Recommended ordering inside Digest context:

1. Recent Reading Memory
2. Retrieved Unit Memory
3. Current Focus / Current Unit

The current unit remains the object of reading regardless of context ordering.

## Retrieval Result Packaging

### Unit-Level Cards, Not Doc-Level Cards

The tool result and Digest should use unit-level memory cards.

Retrieval docs are internal matching surfaces. If source, understanding, response, and annotation documents from the same prior unit all match, Digest should see one prior unit card with selected fields, not four separate cards.

The selection goal is to maximize useful continuity under a small context budget:

- cover as much relevant reading span as possible
- include more distinct Entries rather than replaying long source excerpts
- avoid repeating the same remembered content across cards
- prefer compact memory products over raw source text

### Selection Within A Unit

For each selected unit:

- always include `PriorUnderstanding` when non-empty
- include `PriorResponse` when non-empty, unless it duplicates the understanding too closely or must be clipped out for budget
- include annotations only when their own annotation documents contributed to the selected Entry
- do not include raw prior unit source text, even when `unit_source` helped retrieve the Entry

### Dedupe And Suppression

Suppress:

- current unit
- recent-neighbor units already carried by Recent Reading Memory
- duplicate units across recalls
- cards with only weak response matches and no source/understanding support
- cards not selected by Ingest unless runtime is in an explicit diagnostic override mode
- repeated card content that says the same thing as another selected card with weaker coverage value

## Open Questions

- Should `memory_recalls[]` include a separate `source_cues[]` field, or is `recall_text` enough?
- Should runtime retry once when recalls exist but the model returns final JSON without calling `retrieve_unit_memory`, or should it proceed degraded?
- Should Digest see `matched_recalls`, or should that remain audit-only while Ingest alone sees them?
- How should card budget change for fiction vs argument-heavy nonfiction?
- Should Ingest select card ids, or should runtime treat the highest-ranked tool cards as selected unless Ingest rejects them?
- Should `retrieve_unit_memory` be forced with `tool_choice` when recalls are present, or should the model be allowed to decide under `auto`?
- What is the review rubric for a good recall: coverage of relevant prior units, absence of noisy recall, or downstream Digest usefulness?

## Current Recommendation

Move the next implementation from single model-facing `memory_query` to bounded model-facing `memory_recalls[]` plus a mechanism-private `retrieve_unit_memory` tool loop.

Prompt Ingest as a reader noticing what the selected unit asks it to remember, not as a query generator. Allow zero to three recalls. When recalls exist, Ingest calls `retrieve_unit_memory`; runtime resolves the selected boundary, maps each recall to internal retrieval queries, retrieves per recall, fuses across recall/channel lists, aggregates by Unit Memory Entry, dedupes against recent memory, and returns compact unit-level cards.

Ingest should see the compact cards and return selected card ids in `memory_support`, not copy retrieved text into final JSON. For Digest, introduce `RetrievedUnitMemory` under `ReadingState`, not under `Instruction`. Runtime should package selected canonical prior-unit cards from `Understanding`, compact `Response`, and contributing `Annotations`; raw prior Unit source text remains an internal retrieval surface and should not be replayed into Digest context.
