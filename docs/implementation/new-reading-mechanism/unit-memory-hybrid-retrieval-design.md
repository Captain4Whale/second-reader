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
  - Digest now emits model-facing `understanding`, `response`, and `annotations`, with the single `understanding` object stored internally through the existing `recent_reading_memory` path.

## Design Claim

Long-distance memory should be content-neutral and unit-centered.

The basic retrievable object is not a concept, thread, theme, progression, or pre-labeled content type. It is one completed reading unit: the accepted source unit selected by `Ingest`, plus what `Digest` produced after reading that unit.

This follows the retrieval purpose:

- near-neighbor continuity is handled by carrying recent memory directly
- farther memory is recalled only when the next selected unit makes earlier reading relevant again
- the retrieval system should preserve source-grounded reading process, not collapse the book into a full summary

## Current Design Scope

This document currently anchors the bottom retrieval framework:

- Unit Memory storage
- field-specific retrieval documents
- FTS5 lexical index
- sqlite-vec dense index
- embedding policy
- hybrid retrieval, fusion, aggregation, and rebuild boundaries

The following concerns are intentionally deferred from this implementation slice:

- how `Ingest` writes retrieval queries from the selected unit
- how many retrieval queries one unit may produce
- how retrieved memory cards are rendered into `Digest` XML context
- how `Digest` should use retrieved memory alongside recent-neighbor memory

One boundary is decided now: query generation should not require a separate LLM call. When query generation is designed, it should remain inside the `Ingest` step, after or alongside its source-unit boundary selection. The exact query contract is deferred and should not block the bottom retrieval index implementation.

## V1 Technical Stack

Use one local SQLite-backed retrieval store for the first implementation.

Default components:

- storage database: SQLite
- lexical / sparse retrieval: SQLite FTS5 with BM25
- dense vector retrieval: `sqlite-vec`
- embedding provider: local Ollama
- embedding model: `Qwen3-Embedding-0.6B`
- embedding type: dense vectors only
- first fusion strategy: Reciprocal Rank Fusion / RRF
- optional second-stage diversity pass: MMR rerank after unit-level aggregation

Rationale:

- SQLite keeps the Unit Memory ledger and both indexes local, inspectable, easy to back up, and easy to rebuild.
- FTS5 is the right first lexical layer because it is already in SQLite, has built-in BM25 ranking, supports auxiliary snippets/highlights, and can be tuned with tokenizer/index choices.
- `sqlite-vec` keeps vector search inside the same database boundary, avoiding a separate vector service before the retrieval behavior is proven.
- Qwen3-Embedding-0.6B is small enough for local use and suitable for the mixed Chinese/English reading corpus; it supports dense text embeddings with up to 1024 dimensions.
- RRF avoids raw-score calibration problems between FTS5 BM25 and vector distance scores. Weighted score fusion can be revisited after retrieval-review data exists.

Reference facts that matter for implementation:

- FTS5 `bm25()` returns better matches as numerically smaller values, so raw BM25 scores should not be directly added to similarity scores.
- Ollama `/api/embed` returns L2-normalized vectors; still record the metric and provider metadata because future providers may differ.
- `sqlite-vec` is pre-v1, so all direct extension calls should be wrapped by a small adapter and all indexes should be rebuildable from `unit_memory_entries`.
- Qwen3-Embedding supports query-side instructions; retrieval-query embedding should therefore use a stable instruction template while indexed documents should use the document text without a query instruction unless a later test proves otherwise.

External implementation references:

- SQLite FTS5 documentation: <https://www.sqlite.org/fts5.html>
- sqlite-vec project: <https://github.com/asg017/sqlite-vec>
- Ollama embeddings API: <https://docs.ollama.com/capabilities/embeddings>
- Ollama Qwen3 embedding model tags: <https://ollama.com/library/qwen3-embedding>
- Qwen3-Embedding-0.6B model reference: <https://huggingface.co/Qwen/Qwen3-Embedding-0.6B>

### Initial SQLite Shape

The first schema should separate durable unit records from retrieval documents and retrieval indexes:

```sql
CREATE TABLE unit_memory_entries (
  unit_id TEXT PRIMARY KEY,
  book_id TEXT NOT NULL,
  chapter_id INTEGER,
  chapter_ref TEXT,
  unit_index INTEGER NOT NULL,
  source_span_id TEXT NOT NULL,
  source_text TEXT NOT NULL,
  entry_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE retrieval_docs (
  retrieval_doc_pk INTEGER PRIMARY KEY,
  retrieval_doc_id TEXT NOT NULL UNIQUE,
  unit_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  surface TEXT NOT NULL,
  weight_profile TEXT NOT NULL,
  text TEXT NOT NULL,
  source_span_id TEXT,
  text_hash TEXT NOT NULL,
  embedding_model TEXT,
  embedding_provider TEXT,
  embedding_dimension INTEGER,
  doc_instruction_version TEXT,
  created_at TEXT NOT NULL
);
```

Then maintain:

- `retrieval_docs_fts`
  - FTS5 index over every valid `retrieval_docs.text`
  - metadata stays in `retrieval_docs`, joined by rowid / primary key
- `retrieval_doc_vectors`
  - `sqlite-vec` `vec0` table
  - rowid should match `retrieval_docs.retrieval_doc_pk`
  - vector dimension should default to 1024 for Qwen3-Embedding-0.6B unless a later Matryoshka dimension decision changes it

In v1, index participation is simple: every valid retrieval document is indexed in both FTS5 and sqlite-vec. Surface semantics should be expressed through channel weights and unit aggregation, not by excluding a surface from one index.

The exact SQL may change during implementation, but the ownership boundary should not: `unit_memory_entries` is the source of truth, while FTS and vector tables are rebuildable indexes.

### FTS5 Tokenizer Policy

The corpus includes Chinese and English. Plain word-token behavior is insufficient for Chinese source text because Chinese source spans often have no whitespace word boundary. A pure word tokenizer can keep a long Chinese phrase as one token, making shorter phrase recall brittle.

V1 default:

- use FTS5 for all lexical retrieval
- use a single `trigram` tokenizer FTS5 table as the first lexical index
- keep `detail=full` and `columnsize=1` in the first implementation
- keep tokenizer choice as an index-versioned setting so the lexical index can be rebuilt without changing Unit Memory storage

Recommended first schema:

```sql
CREATE VIRTUAL TABLE retrieval_docs_fts USING fts5(
  text,
  content='retrieval_docs',
  content_rowid='retrieval_doc_pk',
  tokenize='trigram',
  detail=full,
  columnsize=1
);
```

Why this default:

- SQLite's built-in `trigram` tokenizer treats each contiguous sequence of three Unicode characters as a token, which gives useful substring-style recall for Chinese phrases, source fragments, names, images, and exact quote callbacks.
- It keeps V1 inside standard SQLite FTS5, without adding jieba, ICU, or a custom compiled tokenizer dependency before retrieval behavior is proven.
- Dense retrieval, RRF, weight profiles, and unit-level aggregation should absorb some of the noise that trigram lexical matching can introduce.
- `detail=full` preserves phrase/snippet/debug evidence; `columnsize=1` preserves token length information used by built-in BM25. Local book-scale indexes are expected to be small enough that this is the safer first tradeoff.

Known limits:

- FTS5 `trigram` does not help MATCH queries shorter than three Unicode characters.
- `trigram` is substring matching, not true Chinese word segmentation.
- English lexical matching may be noisier than `unicode61` / `porter unicode61`, so review should inspect English-heavy books before treating this as final.

Do not introduce a custom Chinese tokenizer in V1. Custom tokenizers are a valid later path, but they add deployment and rebuild complexity that is not needed for the first Unit Memory retrieval framework.

V2 escalation path:

- if retrieval review shows too many false positives or poor English lexical ranking, add a second FTS5 lexical channel instead of replacing the V1 trigram channel:
  - `trigram` for Chinese, exact fragments, and quote-like substring recall
  - `unicode61` or `porter unicode61` for English word-level recall
- fuse both lexical channels with dense retrieval using RRF, then aggregate by unit
- keep both lexical indexes rebuildable from `retrieval_docs`

### Embedding Policy

Use local Ollama for embedding generation.

Default embedding config:

```json
{
  "provider": "ollama",
  "model": "Qwen3-Embedding-0.6B",
  "ollama_model_id": "qwen3-embedding:0.6b",
  "dimension": 1024,
  "vector_type": "dense",
  "normalization": "l2_normalized_by_provider"
}
```

Implementation should keep the exact Ollama model id configurable because local model tags may differ.

Query embeddings should use a stable instruction, for example:

```text
Instruct: Given the next source unit in an ongoing deep reading of a book, retrieve prior read units that help understand this unit continuously without summarizing the whole book.
Query: {query_text}
```

Document embeddings should embed the retrieval document text itself. Do not prepend query-style instructions to stored documents in v1.

The query instruction version belongs in retrieval config / retrieval trace metadata, not in each stored retrieval document.

### Fusion Policy

Use RRF as the default fusion algorithm.

Process:

1. Run FTS5 BM25 and keep top lexical candidates.
2. Run sqlite-vec KNN and keep top dense candidates.
3. Convert each candidate list to ranks.
4. Apply RRF per retrieval document:

```text
rrf_score(doc) = sum(channel_weight_for_doc / (rrf_k + rank_in_channel))
```

Initial defaults:

- `rrf_k = 60`
- base lexical channel weight = `1.0`
- base dense channel weight = `1.0`
- apply each retrieval document's `weight_profile` after rank conversion or during unit aggregation, not by mutating raw BM25/vector scores

Why not weighted sum first:

- FTS5 BM25 is a lower-is-better score.
- sqlite-vec commonly returns a distance-like lower-is-better value.
- semantic similarity and lexical match strength have different distributions.
- rank fusion is more stable before we have project-specific calibration data.

Weighted sum may be revisited after retrieval review produces calibration examples.

### Unit Aggregation And MMR

After RRF, aggregate retrieval documents by `unit_id`.

Unit-level score should consider:

- best retrieval-doc RRF score
- number of distinct matching surfaces and matched channels
- retrieval document weight profiles
- exact phrase/source quote match
- distance from current unit
- duplicate suppression against recent memory

Recommended first-pass weight profiles:

- `unit_understanding`: dense high, lexical medium; best for conceptual continuity.
- `unit_source`: lexical high, dense medium; best for exact phrasing, named entities, and source recurrence.
- `unit_annotation`: lexical medium-high, dense medium-high; best for visible note continuity around a marked line.
- `unit_response`: lexical low, dense low-to-medium; support signal only, useful when a prior reader response strongly echoes the current unit.

After unit aggregation, an optional MMR rerank can improve diversity:

```text
mmr_score = lambda * relevance - (1 - lambda) * max_similarity_to_selected
```

Initial default:

- `lambda = 0.7`
- apply only after selecting a larger candidate pool, not as a replacement for RRF
- compare units by dense embedding of their best matching retrieval doc or by a compact unit-card embedding

MMR should prevent redundant retrieval cards, not force diversity when the top results are genuinely connected.

### Adapter Boundary

All direct technology calls should live behind a mechanism-local adapter, for example `UnitMemoryIndex`.

The rest of the reader should ask for semantic operations:

- write one Unit Memory Entry
- index retrieval documents for that entry
- embed retrieval documents
- retrieve prior unit candidates for a query
- rebuild all indexes from the ledger

Do not scatter sqlite-vec SQL, FTS5 SQL, Ollama request shapes, or fusion constants through runner or prompt code.

## Storage Entry

### Source Of Truth Boundary

`UnitMemoryLedger` is the source of truth for long-distance retrievable reading memory.

It does not replace the existing runtime artifacts. These artifacts own different layers of fact:

- `unit_span_ledger`
  - reading-position and source-span facts
  - answers what source range has been accepted and read
- `read_audit`
  - runtime trace and debugging facts
  - answers how an `Ingest -> Digest -> settlement` cycle ran
- `reaction_records`
  - UI-visible annotation / reaction facts
  - answers what reader-facing notes should be shown or linked back to source text
- `recent_reading_memory`
  - near-neighbor continuity facts
  - answers what recent understanding should be carried directly into the next Digest context
- `UnitMemoryLedger`
  - long-distance retrievable reading-memory facts
  - answers what completed units can later be recalled by hybrid retrieval

The retrieval system should index `UnitMemoryLedger`, not reconstruct long-distance memory by stitching together `read_audit`, UI records, and recent-memory artifacts.

FTS5 and sqlite-vec indexes are derived from `UnitMemoryLedger`. They are rebuildable indexes, not independent sources of truth.

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
    "understanding": {
      "kind": "claim_or_argument",
      "content": "..."
    },
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
  - `understanding`
  - `response`
  - `annotations[]`
- audit / lifecycle metadata:
  - prompt versions and model trace ids may be linked by reference, but should not be part of the retrieval text by default

### Boundary

Do not reintroduce content-typed long-memory stores here.

The unit entry may contain `understanding.kind` because Digest already emits that lightweight kind for local readability, but retrieval should not depend on a fixed concept/thread/progression ontology. The primary retrieval object is still the unit and its reading outputs.

## Index Surfaces

Storage is unit-centered, but retrieval should index multiple field-specific surfaces.

This avoids flattening source, understanding, response, and annotations into one undifferentiated blob while still allowing all valid retrieval documents to participate in both lexical and semantic recall. The surface sections below describe weighting posture, not exclusive index membership.

### Source Surface

Index:

- accepted source text
- text from `accepted_source_unit.paragraph_slices`
- annotation `source_quote` may also be included as exact source evidence

Use:

- BM25 / full-text matching for names, terms, repeated phrases, images, quotes, and exact wording
- semantic embedding for source-near paraphrase recall

Default channel posture:

- high lexical weight
- medium semantic weight

Do not assume an accepted source unit is larger than a paragraph or aligned to paragraph boundaries. Current reading units are paragraph-offset source spans and may start or end inside a paragraph, so the source retrieval docs should follow the accepted unit's recorded paragraph slices.

### Understanding Surface

Index:

- `understanding.content`
- optionally include `understanding.kind` as a low-weight facet, not a hard filter

Use:

- semantic retrieval for earlier claims, situations, definitions, evidence boundaries, stages, contrasts, and local developments
- BM25 retrieval for named structures or repeated wording inside understanding text

Default channel posture:

- high semantic weight
- medium lexical weight

Digest produces one holistic Understanding per accepted source unit. The `unit_understanding` retrieval document should therefore be one document per Unit Memory Entry, not one document per sentence, paragraph, topic, or future-use split.

### Annotation Surface

Index:

- `annotations[].source_quote`
- `annotations[].content`

Use:

- recall visible notes and exact lines that the reader previously marked
- connect current text to earlier margin-note-like reactions without exposing internal ids

Default channel posture:

- medium-high lexical weight
- medium-high semantic weight

Each annotation should produce one retrieval document. Its retrieval text should combine the exact source quote and the annotation content, for example `source_quote + "\n" + content`, because the quote gives source footing while the note content gives readerly meaning. Do not split quote and note into separate v1 documents.

### Response Surface

Index:

- `response`

Use:

- recall readerly aftertaste, questions, felt pressure, and companion-like continuity

Default channel posture:

- low-to-medium semantic weight
- low lexical weight

Response is useful, but it should not dominate source-grounded retrieval. It is a support signal, not the primary memory truth.

## Retrieval Documents

A single Unit Memory Entry can produce multiple retrieval documents:

```json
{
  "retrieval_doc_id": "unit:c1:u0007#understanding",
  "unit_id": "unit:c1:u0007",
  "surface": "unit_understanding",
  "text": "...",
  "weight_profile": "understanding_default",
  "source_span_id": "src:c1:p45@0-p46@24"
}
```

### V1 Index Participation

Every valid retrieval document should participate in both retrieval indexes:

- FTS5 indexes `retrieval_docs.text` for lexical / BM25 candidate ranks.
- sqlite-vec embeds the same `retrieval_docs.text` for dense candidate ranks.

Do not decide index membership by surface in v1. A source slice can still benefit from dense semantic recall; an Understanding can still benefit from lexical names or terms; an Annotation naturally combines exact quote and reader meaning; a Response may occasionally help semantic continuity.

Surface differences should instead be expressed through channel weights and later unit aggregation:

| surface | lexical channel | dense channel | role |
| --- | --- | --- | --- |
| `unit_source` | high | medium | exact wording, names, quotes, source-near semantic recall |
| `unit_understanding` | medium | high | primary semantic memory of what the unit established |
| `unit_annotation` | medium-high | medium-high | visible-note continuity with both quote and note meaning |
| `unit_response` | low | low-to-medium | support signal for readerly aftertaste / pressure |

The implementation may store these as a `weight_profile` value on `retrieval_docs` and resolve concrete numeric weights in retrieval config. Empty or invalid material should not create a retrieval document at all; once a retrieval document exists, it is dual-indexed.

### V1 Document Granularity

Use surface-specific document granularity:

- `unit_source`
  - one retrieval document per `accepted_source_unit.paragraph_slices[]` item
  - retrieval doc id pattern: `unit:{id}#source:slice:{index}`
  - text: the recorded slice text
  - metadata: `paragraph_index`, `start_char`, `end_char`, `text_role`, `source_span_id`
  - purpose: exact phrase, name, quote-like callback, repeated wording, and source-near semantic recall
- `unit_understanding`
  - one retrieval document per Unit Memory Entry
  - retrieval doc id pattern: `unit:{id}#understanding`
  - text: `digest.understanding.content`
  - metadata: `understanding.kind`, `source_span_id`
  - purpose: primary semantic recall of what the unit established for continued reading
- `unit_annotation`
  - one retrieval document per annotation
  - retrieval doc id pattern: `unit:{id}#annotation:{index}`
  - text: `source_quote + "\n" + content`
  - metadata: annotation index, `source_quote`, resolved source ref if available
  - purpose: recall visible notes and exact lines that were previously marked
- `unit_response`
  - zero or one retrieval document per Unit Memory Entry
  - retrieval doc id pattern: `unit:{id}#response`
  - text: `digest.response`
  - omit this document when response is empty
  - purpose: low-weight support for readerly aftertaste, question, pressure, and companion-like continuity

Do not create these documents in v1:

- no sentence-level source documents
- no whole-paragraph documents unless the accepted paragraph slice is itself whole
- no multiple understanding documents for one unit
- no separate source-quote-only and annotation-note-only documents
- no default `unit_all_text` blob that flattens source, understanding, response, and annotations together

If later retrieval review shows that an additional whole-unit semantic surface is needed, add it as a low-weight `unit_card` surface. Do not add it as a default v1 document, because `unit_understanding` already carries the primary whole-unit semantic memory.

Retrieval should score sub-documents first, then aggregate by `unit_id`. Digest should receive retrieved units or compact unit memory cards, not a loose pile of disconnected snippets.

## Hybrid Retrieval Outline

### Query Generation

`Ingest` selects the next forward source unit first.

When retrieval-query generation is implemented, it should remain part of the `Ingest` step. Do not introduce a separate query-generation LLM call by default.

The query should be about the selected unit, not about a broad chapter topic.

Deferred design work:

- what exact query fields `Ingest` emits
- whether one unit can emit multiple retrieval queries, and what the cap should be
- how much of the selected unit should be available to query generation after boundary resolution
- whether annotation-like local triggers should produce separate retrieval queries
- how query-generation traces should be audited

### Candidate Retrieval

Use hybrid retrieval:

- lexical candidate set from SQLite FTS5 BM25 over all valid retrieval documents
- semantic candidate set from sqlite-vec dense vector KNN over the same valid retrieval documents
- optional metadata filters:
  - same book
  - only prior units
  - exclude current unit
  - exclude recent-neighbor units already carried directly

The recent-neighbor exclusion is important: recent memory will be passed directly to Digest, so long-distance retrieval should avoid returning the same nearby units again unless explicitly requested.

### Ranking And Aggregation

Rank sub-document hits first, then aggregate to unit-level memory cards.

Ranking should consider:

- retrieval rank from FTS5 BM25
- retrieval rank from sqlite-vec vector search
- surface / channel weights from the retrieval document's weight profile
- distance from current unit
- exact source phrase match bonus
- diversity across units and surfaces
- duplicate suppression against recent memory

Do not fuse raw scores in v1. Use RRF first, then aggregate by unit.

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

Digest context packaging is not part of the current bottom-framework slice.

Deferred design work:

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
- exact SQLite schema and migration / rebuild commands
- tokenizer review results and whether V2 needs a dual lexical channel
- embedding model version pinning and local Ollama health checks
- index rebuild checksums and prompt-version compatibility

## What We Still Need To Design

- Unit Memory ledger schema:
  - exact persisted JSON shape
  - write timing and failure behavior inside settlement
  - migration / rebuild behavior for existing runtime artifacts
- Query contract:
  - deferred from the bottom-framework implementation slice
  - what Ingest emits
  - no separate query-generation LLM call by default
  - how many queries are allowed
- Retrieval algorithm:
  - whether retrieval review requires a second `unicode61` / `porter unicode61` lexical channel
  - exact sqlite-vec distance / metric behavior to standardize behind the adapter
  - score normalization
  - concrete numeric weight profiles for each surface / channel posture
  - dedupe and diversity policy
- Context packaging:
  - deferred from the bottom-framework implementation slice
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

Create retrieval documents from all four memory surfaces and index every valid retrieval document in both FTS5 and sqlite-vec:

- accepted source unit
- `understanding`
- `response`
- `annotations[]`

But do not score them as equal signals. Use field-specific retrieval documents, weight profiles, and unit-level aggregation.

The retrieval result should be source-grounded and unit-centered, then rendered to Digest as compact prior-reading support rather than as a hidden backread path.
