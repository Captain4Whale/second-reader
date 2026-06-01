# Unit Memory Hybrid Retrieval Design

Purpose: define the first design frame for content-neutral long-distance memory retrieval in the new `Ingest -> Digest` mechanism.
Use when: designing the Unit Memory ledger, hybrid retrieval index, Ingest retrieval requests, or Digest retrieval context packaging.
Not for: current live runtime authority, implemented schema guarantees, evaluation claims, or evidence-catalog updates.
Update when: Unit Memory entry shape, indexed fields, retrieval ranking, query generation, or Digest retrieval-context packaging changes.

## Status

- Date: `2026-06-01`
- Status: design draft; not implemented.
- Evaluation status: no eval run, no evidence-catalog update.
- Current basis:
  - `DEC-103` pauses the old Second Reader Memory / Planning track as the default implementation authority.
  - `DEC-107` makes `Ingest` the forward boundary LLM call and reserves memory-support retrieval for later design.
  - `DEC-108` makes `Digest` the concrete per-unit interpretation LLM call.
  - `DEC-109` removes content-typed concept/thread long-memory stores from the current live surface.
  - Digest now emits model-facing `understanding`, `response`, and `annotations`, with `understanding[]` stored internally through the existing `recent_reading_memory` path.

## Design Claim

Long-distance memory should be content-neutral and unit-centered.

The basic retrievable object is not a concept, thread, theme, progression, or pre-labeled content type. It is one completed reading unit: the accepted source unit selected by `Ingest`, plus what `Digest` produced after reading that unit.

This follows the retrieval purpose:

- near-neighbor continuity is handled by carrying recent memory directly
- farther memory is recalled only when the next selected unit makes earlier reading relevant again
- the retrieval system should preserve source-grounded reading process, not collapse the book into a full summary

## Storage Entry

### Unit Memory Entry

One `UnitMemoryEntry` corresponds to one completed `Ingest -> Digest -> Reading Runner settlement` transaction.

It should store the accepted unit and the Digest outputs as one logical record:

```json
{
  "unit_id": "unit:c1:u0007",
  "book_id": "book:...",
  "chapter_id": 1,
  "chapter_ref": "Chapter 1",
  "unit_index": 7,
  "accepted_source_unit": {
    "source_span_id": "src:c1:p45@0-p46@24",
    "source_span": {},
    "source_text": "...",
    "paragraph_slices": []
  },
  "digest": {
    "understanding": [
      {
        "kind": "claim_or_argument",
        "content": "..."
      }
    ],
    "response": "...",
    "annotations": [
      {
        "source_quote": "...",
        "content": "...",
        "prior_link": null,
        "outside_link": null,
        "search_intent": null
      }
    ]
  }
}
```

The entry should be append-only for v1. If later reading changes how an earlier unit is understood, that later change should become a new linked record or reconsolidation layer, not a silent overwrite of the original read.

### Stored Fields

The stored unit should preserve enough information to support retrieval and later Digest context rendering:

- stable identity:
  - `unit_id`
  - `book_id`
  - `chapter_id`
  - `chapter_ref`
  - `unit_index`
- source coordinates:
  - `source_span_id`
  - `source_span`
  - paragraph-offset cursor data
- source content:
  - accepted source text
  - paragraph slices with paragraph index, role, and local char offsets when available
- Digest outputs:
  - `understanding[]`
  - `response`
  - `annotations[]`
- audit / lifecycle metadata:
  - prompt versions and model trace ids may be linked by reference, but should not be part of the retrieval text by default

### Boundary

Do not reintroduce content-typed long-memory stores here.

The unit entry may contain `understanding.kind` because Digest already emits that lightweight kind for local readability, but retrieval should not depend on a fixed concept/thread/progression ontology. The primary retrieval object is still the unit and its reading outputs.

## Index Surfaces

Storage is unit-centered, but retrieval should index multiple field-specific surfaces.

This avoids flattening source, understanding, response, and annotations into one undifferentiated blob while still allowing all of them to participate in both lexical and semantic recall.

### Source Surface

Index:

- accepted source text
- paragraph slice text
- annotation `source_quote` may also be included as exact source evidence

Use:

- BM25 / full-text matching for names, terms, repeated phrases, images, quotes, and exact wording
- semantic embedding for source-near paraphrase recall

Default weight:

- high lexical weight
- medium semantic weight

### Understanding Surface

Index:

- each `understanding[].content`
- optionally include `understanding.kind` as a low-weight facet, not a hard filter

Use:

- semantic retrieval for earlier claims, situations, definitions, evidence boundaries, stages, contrasts, and local developments
- BM25 retrieval for named structures or repeated wording inside understanding text

Default weight:

- high semantic weight
- medium lexical weight

### Annotation Surface

Index:

- `annotations[].source_quote`
- `annotations[].content`

Use:

- recall visible notes and exact lines that the reader previously marked
- connect current text to earlier margin-note-like reactions without exposing internal ids

Default weight:

- medium-high lexical weight
- medium-high semantic weight

### Response Surface

Index:

- `response`

Use:

- recall readerly aftertaste, questions, felt pressure, and companion-like continuity

Default weight:

- low-to-medium semantic weight
- low lexical weight

Response is useful, but it should not dominate source-grounded retrieval. It is a support signal, not the primary memory truth.

## Retrieval Documents

A single Unit Memory Entry can produce multiple retrieval documents:

```json
{
  "retrieval_doc_id": "unit:c1:u0007#understanding:0",
  "unit_id": "unit:c1:u0007",
  "surface": "understanding",
  "text": "...",
  "weight_profile": "understanding_default",
  "source_span_id": "src:c1:p45@0-p46@24"
}
```

Recommended v1 surfaces:

- `unit_source`
- `unit_understanding`
- `unit_annotation`
- `unit_response`

Retrieval should score sub-documents first, then aggregate by `unit_id`. Digest should receive retrieved units or compact unit memory cards, not a loose pile of disconnected snippets.

## Hybrid Retrieval Outline

### Query Generation

`Ingest` selects the next forward source unit first.

After the selected unit is accepted or at least sufficiently resolved for retrieval, the runtime should ask `Ingest` for memory-support query material, or derive it from the selected unit plus Ingest's boundary reason.

The query should be about the selected unit, not about a broad chapter topic.

Open design work:

- whether Ingest emits one query string or structured query facets
- whether query generation happens inside the same Ingest call or as a second Ingest-adjacent call after anchor resolution
- whether annotation-like local triggers should produce separate retrieval queries

### Candidate Retrieval

Use hybrid retrieval:

- lexical candidate set from BM25 / full-text search
- semantic candidate set from embeddings
- optional metadata filters:
  - same book
  - only prior units
  - exclude current unit
  - exclude recent-neighbor units already carried directly

The recent-neighbor exclusion is important: recent memory will be passed directly to Digest, so long-distance retrieval should avoid returning the same nearby units again unless explicitly requested.

### Ranking And Aggregation

Rank sub-document hits first, then aggregate to unit-level memory cards.

Ranking should consider:

- retrieval score from lexical search
- retrieval score from vector search
- surface weight
- distance from current unit
- exact source phrase match bonus
- diversity across units and surfaces
- duplicate suppression against recent memory

The final output should explain why a unit was retrieved in machine-readable terms for audit, but Digest should see only reader-usable context.

### Digest Context Packaging

Digest should not receive raw index rows.

It should receive compact retrieved memory cards, likely grouped by prior unit:

- source locator
- short source excerpt or exact matching quote when useful
- relevant understanding
- relevant annotation content when applicable
- optional response only when it materially helps continuity
- retrieval reason / matched surface for audit, not necessarily visible in prompt text

Open design work:

- XML shape for `RetrievedMemory`
- maximum card count and token budget
- how to mark near-neighbor direct memory versus long-distance retrieved memory
- how much exact source text can be shown without turning retrieval into hidden backread

### Persistence And Refresh

The first implementation can rebuild the retrieval index from the Unit Memory ledger when needed.

Later implementation can add incremental index updates after each settlement:

- write Unit Memory Entry
- create/update retrieval documents
- update lexical index
- update vector index

Open design work:

- artifact paths under `_mechanisms/attentional_v2/runtime/`
- whether vector index lives as local files, SQLite, or an external vector store
- embedding model / dimensionality / migration strategy
- index rebuild checksums and prompt-version compatibility

## What We Still Need To Design

- Unit Memory ledger schema:
  - exact persisted JSON shape
  - relationship to `unit_span_ledger`, `read_audit`, `reaction_records`, and `recent_reading_memory`
- Query contract:
  - what Ingest emits
  - whether query emission is same-call or second-call
  - how many queries are allowed
- Retrieval algorithm:
  - lexical engine
  - embedding model
  - score normalization
  - surface weights
  - dedupe and diversity policy
- Context packaging:
  - XML block shape for Digest
  - retrieved-card budget
  - source quote / understanding / response / annotation rendering rules
- Runtime ownership:
  - which step executes retrieval
  - how retrieval traces are audited
  - how failures degrade gracefully
- Recent-neighbor policy:
  - how many recent units are always carried
  - which units are excluded from long-distance retrieval
  - how to avoid duplicate context
- Evaluation / review criteria:
  - whether retrieved memory is relevant
  - whether it improves continuity without forcing callbacks
  - whether it avoids summary-like overreach

## Current Recommendation

Use one append-only Unit Memory Entry per completed read unit.

Index all four memory surfaces:

- accepted source unit
- `understanding[]`
- `response`
- `annotations[]`

But do not index them as equal signals. Use field-specific surfaces, weights, and unit-level aggregation.

The retrieval result should be source-grounded and unit-centered, then rendered to Digest as compact prior-reading support rather than as a hidden backread path.
