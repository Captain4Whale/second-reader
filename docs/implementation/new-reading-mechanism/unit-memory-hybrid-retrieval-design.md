# Unit Memory Hybrid Retrieval Design

Purpose: define the first design frame for content-neutral long-distance memory retrieval in the new `Ingest -> Digest` mechanism.
Use when: designing the Unit Memory ledger, hybrid retrieval index, Ingest retrieval requests, or Digest retrieval context packaging.
Not for: Digest retrieved-memory context authority, evaluation claims, or evidence-catalog updates.
Update when: Unit Memory entry shape, indexed fields, retrieval ranking, query generation, or Digest retrieval-context packaging changes.

## Status

- Date: `2026-06-02`
- Status: bottom retrieval framework implemented; bounded recall/tool loop and Digest `ReadingMemory` packaging implemented in the follow-through slice.
- Evaluation status: no eval run, no evidence-catalog update.
- Current basis:
  - `DEC-103` pauses the old Second Reader Memory / Planning track as the default implementation authority.
  - `DEC-107` makes `Ingest` the forward boundary LLM call and reserves memory-support retrieval for later design.
  - `DEC-108` makes `Digest` the concrete per-unit interpretation LLM call.
  - `DEC-109` removes content-typed concept/thread long-memory stores from the current live surface.
  - `DEC-110` makes Unit Memory ledger + hybrid retrieval the current long-distance memory substrate for `attentional_v2`.
  - Digest now emits model-facing `understanding`, `response`, and `annotations`, with the single `understanding` object stored internally through the existing `recent_reading_memory` path.
- Follow-up implementation reference:
  - `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md` records the implemented slice that replaces the single model-facing `memory_query` with bounded `memory_recalls[]`, adds the Anthropic-style `retrieve_unit_memory` tool loop, aggregates multi-recall retrieval, and renders Digest `ReadingMemory`.

## Design Claim

Long-distance memory should be content-neutral and unit-centered.

The basic retrievable object is not a concept, thread, theme, progression, or pre-labeled content type. It is one completed reading unit: the accepted source unit selected by `Ingest`, plus what `Digest` produced after reading that unit.

This follows the retrieval purpose:

- near-neighbor continuity is handled by carrying recent memory directly
- farther memory is recalled only when the next selected unit makes earlier reading relevant again
- the retrieval system should preserve source-grounded reading process, not collapse the book into a full summary

## Current Design Scope

This document anchors the implemented bottom retrieval framework:

- Unit Memory storage
- field-specific retrieval documents
- FTS5 lexical index
- sqlite-vec dense index
- embedding policy
- hybrid retrieval, fusion, aggregation, and rebuild boundaries
- Ingest bounded recall output and runtime fallback query behavior
- retrieval-mode configuration and trace ownership

The original bottom-framework slice deferred prompt packaging, but the follow-through slice now implements:

- bounded `memory_recalls[]` in the same Ingest call that chooses the forward unit boundary
- a mechanism-private `retrieve_unit_memory` tool loop
- runtime-owned multi-recall retrieval aggregation, selected-Understanding rendering, and Digest `ReadingMemory` context

One boundary remains: query/recall generation should not require a separate LLM call. `Ingest` expresses prior-reading recalls inside the same LLM call that chooses the forward unit boundary. If recall data is malformed or boundary fallback changes the accepted source unit, runtime may derive a fallback query from the accepted source unit text, but an intentional `memory_recalls: []` skips long-distance retrieval for that cycle.

Another boundary remains: reading must be able to choose its memory retrieval mode before starting a book / read session. The user or operator should be able to run long-distance memory as text-only lexical retrieval, or as hybrid lexical + vector retrieval. This mode controls read-time retrieval behavior, not the Unit Memory ledger shape. The V1 default is `hybrid`.

## Implemented Slice

The first implementation landed the storage, indexing, read-time retrieval, and trace layer. The follow-through slice now connects that layer to Ingest recalls and Digest `ReadingMemory`.

Implemented now:

- `unit_memory.sqlite` under `_mechanisms/attentional_v2/runtime/`
  - durable `unit_memory_entries`
  - derived `retrieval_docs`
  - FTS5 trigram index
  - optional sqlite-vec vector table
  - query embedding cache
- `memory_retrieval_config.json`
  - persisted read-time retrieval mode and backend defaults
  - default mode is `hybrid`
  - supported explicit modes are `hybrid` and `text_only`
- `unit_memory_retrieval_trace.jsonl`
  - records Ingest recalls or fallback query source, per-recall candidate counts, channel availability, degradation, selected/suppressed units, latency, and ReadingMemory token accounting
- `Ingest` output now includes bounded `memory_recalls[]`
  - zero to three recalls
  - generated in the same LLM call as boundary selection
  - no separate query-generation LLM call
  - when recalls are non-empty, the Ingest call must use the `retrieve_unit_memory` tool loop
- Reading Runner now executes retrieval after accepting the source unit and before `Digest`
  - runtime selects Understanding memory, dedupes against hot current-chapter memory, and renders top-level Digest `ReadingMemory`
  - tool results exposed back to Ingest are status/count summaries only, never retrieved Understanding text or selected memory ids
- settlement writes one Unit Memory Entry per accepted source unit after `Digest` output has been accepted
  - source, understanding, response, and annotation retrieval documents are derived from the entry
  - valid documents are always FTS-indexed
  - vector indexing is attempted only for `unit_understanding` documents in `hybrid` mode and may remain pending when sqlite-vec or Ollama is unavailable

The backend entry points accept `memory_retrieval_mode`, but the frontend does not expose a new UI control in this slice.

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

V1 supports two read-time memory retrieval modes:

- `text_only`
  - use Unit Memory retrieval documents and FTS5 BM25 only
  - do not generate query embeddings during the read loop
  - do not require sqlite-vec to be present or up to date
  - useful for low-latency reading, local debugging, and machines without reliable embedding service availability
- `hybrid`
  - use FTS5 BM25 plus query embedding and sqlite-vec KNN
  - fuse lexical and dense candidate lists with RRF
  - degrade to text-only behavior if vector retrieval is unavailable, times out, or has no usable indexed vectors

The mode should be selected before reading a book / starting a read session and persisted with run configuration, checkpoint metadata, and retrieval trace records. The same Unit Memory ledger supports both modes. Switching a book from `text_only` to `hybrid` later should not require rewriting ledger entries; it may require building or catching up the vector index.

Default and resume semantics:

- default mode: `hybrid`
- first implementation source: mechanism-private read/run configuration, falling back to the default when no user-facing option is provided
- checkpoint / resume: restore the mode from the checkpoint or live run config; do not silently change retrieval mode during resume
- if a resume request explicitly asks for a different mode, treat it as a new operator decision that must be recorded in resume metadata and retrieval trace

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
- `sqlite-vec` `vec0` supports cosine distance through `distance_metric=cosine`; V1 should use that when available and fall back explicitly when the installed binding cannot.
- Qwen3-Embedding supports query-side instructions; retrieval-query embedding should therefore use a stable instruction template while indexed documents should use the document text without a query instruction unless a later test proves otherwise.

External implementation references:

- SQLite FTS5 documentation: <https://www.sqlite.org/fts5.html>
- sqlite-vec project: <https://github.com/asg017/sqlite-vec>
- sqlite-vec KNN queries: <https://alexgarcia.xyz/sqlite-vec/features/knn.html>
- sqlite-vec vec0 table design: <https://alexgarcia.xyz/sqlite-vec/features/vec0.html>
- Ollama embeddings API: <https://docs.ollama.com/capabilities/embeddings>
- Ollama Qwen3 embedding model tags: <https://ollama.com/library/qwen3-embedding>
- Qwen3-Embedding-0.6B model reference: <https://huggingface.co/Qwen/Qwen3-Embedding-0.6B>

### Initial SQLite Shape

The first schema should separate durable unit records from retrieval documents and retrieval indexes:

```sql
CREATE TABLE unit_memory_entries (
  unit_id TEXT PRIMARY KEY,
  book_id TEXT NOT NULL,
  schema_version TEXT NOT NULL,
  mechanism_version TEXT NOT NULL,
  chapter_id INTEGER,
  chapter_ref TEXT,
  unit_index INTEGER NOT NULL,
  source_span_id TEXT NOT NULL,
  source_text TEXT NOT NULL,
  entry_json TEXT NOT NULL,
  index_status_json TEXT NOT NULL,
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
  vector_index_status TEXT NOT NULL DEFAULT 'pending',
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
- `query_embedding_cache`
  - cache read-time query embeddings by query hash, embedding model, dimension, and query instruction version
  - lives in the same SQLite file because it is retrieval-runtime cache state, not Unit Memory truth
  - use SHA-256 over normalized query text for `query_hash`

In v1, index participation is intentionally asymmetric: every valid retrieval document is FTS-indexed, while only `unit_understanding` is vector-index eligible. In `hybrid` mode, Understanding vector rows should be present or pending; in `text_only` mode, vector rows may be absent until catch-up is requested. Surface semantics should be expressed through channel weights and unit aggregation, with Understanding carrying dense semantic recall.

The exact SQL may change during implementation, but the ownership boundary should not: `unit_memory_entries` is the source of truth, while FTS and vector tables are rebuildable indexes.

Recommended first vector schema:

```sql
CREATE VIRTUAL TABLE retrieval_doc_vectors USING vec0(
  embedding float[1024] distance_metric=cosine
);
```

Insert each vector row with `rowid = retrieval_docs.retrieval_doc_pk`. V1 should prefer cosine distance because retrieval embeddings are used for semantic similarity and Ollama returns normalized vectors. If the installed sqlite-vec binding does not support `distance_metric=cosine`, fall back to L2 distance and record `vector_metric="l2_on_normalized_vectors"` in index metadata and retrieval trace.

Recommended first query cache schema:

```sql
CREATE TABLE query_embedding_cache (
  query_hash TEXT NOT NULL,
  embedding_model TEXT NOT NULL,
  embedding_dimension INTEGER NOT NULL,
  query_instruction_version TEXT NOT NULL,
  embedding_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (
    query_hash,
    embedding_model,
    embedding_dimension,
    query_instruction_version
  )
);
```

Store cached embeddings as JSON in v1 for simplicity and inspectability. A later optimization may switch to compact float32 BLOB storage.

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
  "distance_metric": "cosine",
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

Use RRF as the default fusion algorithm when the read-time retrieval mode is `hybrid`.

Process:

1. Run FTS5 BM25 and keep top lexical candidates.
2. In `hybrid` mode, run sqlite-vec KNN and keep top dense candidates.
3. Convert each candidate list to ranks.
4. Apply RRF per retrieval document:

```text
doc_rrf_score =
  sum(
    base_channel_weight
    * surface_channel_weight
    / (rrf_k + rank_in_channel)
  )
```

Initial defaults:

- `lexical_top_k = 80`
- `dense_top_k = 80`
- `rrf_k = 60`
- base lexical channel weight = `1.0`
- base dense channel weight = `1.0`
- apply each retrieval document's `weight_profile` after rank conversion or during unit aggregation, not by mutating raw BM25/vector scores

In `text_only` mode, skip query embedding, sqlite-vec KNN, dense channel weighting, and RRF cross-channel fusion. Rank the FTS5 candidate list, apply lexical surface weights, then aggregate by unit using the same unit aggregation path.

Initial surface / channel weights:

| surface | lexical weight | dense weight | purpose |
| --- | ---: | ---: | --- |
| `unit_source` | `1.25` | none | emphasize exact wording, names, quote callbacks, and source recurrence |
| `unit_understanding` | `0.85` | `1.35` | emphasize semantic continuity and what the unit established |
| `unit_annotation` | `1.10` | none | let exact quote and note wording act as an auxiliary lexical signal |
| `unit_response` | `0.45` | none | keep readerly aftertaste as a weak lexical support signal |

These weights are deliberately modest. They should express surface posture without overpowering rank evidence. Dense weights apply only to vector-eligible `unit_understanding` documents.

Why not weighted sum first:

- FTS5 BM25 is a lower-is-better score.
- sqlite-vec commonly returns a distance-like lower-is-better value.
- semantic similarity and lexical match strength have different distributions.
- rank fusion is more stable before we have project-specific calibration data.

Weighted sum may be revisited after retrieval review produces calibration examples.

### Unit Aggregation And MMR

After RRF in `hybrid` mode, or after lexical ranking in `text_only` mode, aggregate retrieval documents by `unit_id`.

V1 unit score:

```text
unit_score =
  best_doc_score
  + 0.35 * second_best_doc_score
  + 0.15 * sum(next_doc_scores, capped_to_3_docs)
  + surface_coverage_bonus
  + channel_coverage_bonus
```

Initial aggregation defaults:

- `max_docs_per_unit_for_scoring = 5`
- `surface_coverage_bonus = 0.03 * min(distinct_surface_count - 1, 3)`
- `channel_coverage_bonus = 0.03` when both lexical and dense channels matched
- `exact_phrase_bonus = 0.0` by default; record exact phrase / quote matches for audit and later calibration, but do not add another boost until query fields are designed
- distance penalty = none by default beyond recent-neighbor exclusion
- `recent_neighbor_exclusion_unit_count = 20`
- also exclude any source unit ids already carried directly in the Digest recent-memory context
- `max_units_after_aggregation = 20`
- `max_units_to_digest_context` should be recalibrated by the later Digest memory-budget slice
  - do not inherit the old `4` to `6` detailed-memory cap now that Digest context is Understanding-only
  - Understanding-only briefs should optimize for broader relevant Entry coverage under the final budget

Unit-level score should consider:

- best retrieval-doc RRF score
- number of distinct matching surfaces and matched channels
- retrieval document weight profiles
- exact phrase/source quote match
- distance from current unit
- duplicate suppression against recent memory

After unit aggregation, an optional MMR rerank can improve diversity:

```text
mmr_score = lambda * relevance - (1 - lambda) * max_similarity_to_selected
```

Initial default:

- `mmr_enabled = false`
- `lambda = 0.75` if enabled
- `mmr_candidate_units = 20`
- `mmr_output_units = 6`
- apply only after selecting a larger candidate pool, not as a replacement for RRF
- compare units by dense embedding of their Understanding document or by a compact Understanding-brief embedding

MMR should prevent redundant retrieval briefs, not force diversity when the top results are genuinely connected.

### Adapter Boundary

All direct technology calls should live behind a mechanism-local adapter, for example `UnitMemoryIndex`.

The rest of the reader should ask for semantic operations:

- write one Unit Memory Entry
- index retrieval documents for that entry
- embed vector-eligible Understanding documents
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
  - answers what completed units can later be recalled by text-only or hybrid retrieval

The retrieval system should index `UnitMemoryLedger`, not reconstruct long-distance memory by stitching together `read_audit`, UI records, and recent-memory artifacts.

FTS5 and sqlite-vec indexes are derived from `UnitMemoryLedger`. They are rebuildable indexes, not independent sources of truth.

### Unit Memory Entry

One `UnitMemoryEntry` corresponds to one completed `Ingest -> Digest -> Reading Runner settlement` transaction.

It should store the accepted unit and the Digest outputs as one logical record:

```json
{
  "unit_id": "unit:c1:u0007",
  "book_id": "book:...",
  "schema_version": "unit_memory_entry.v1",
  "mechanism_version": "attentional_v2",
  "created_at": "2026-06-01T00:00:00Z",
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
  },
  "index_status": {
    "fts": "indexed",
    "vector": "pending",
    "last_error": null
  }
}
```

The entry should be append-only for v1. If later reading changes how an earlier unit is understood, that later change should become a new linked record or reconsolidation layer, not a silent overwrite of the original read.

### Stored Fields

The stored unit should preserve enough information to support retrieval and later Digest context rendering:

- stable identity:
  - `unit_id`
  - `book_id`
  - `schema_version`
  - `mechanism_version`
  - `chapter_id`
  - `chapter_ref`
  - `unit_index`
  - `created_at`
- source coordinates:
  - `source_span_id`
  - `source_span`
  - paragraph-offset cursor data
- source content:
  - accepted source text
  - paragraph slices with paragraph index, role, and local char offsets when available
- Digest outputs:
  - `understanding`
  - `understanding_token_estimate`
    - first estimator: `tiktoken_o200k_base_v1`
    - store both raw `tiktoken` count and safety-multiplied budget count when available
    - used for fast `ReadingMemory` budget assembly without re-counting every retrieved entry
  - `response`
  - `annotations[]`
- audit / lifecycle metadata:
  - prompt versions and model trace ids may be linked by reference, but should not be part of the retrieval text by default
  - index status for FTS and vector rows
  - `memory_retrieval_mode` from the read/run configuration

### Boundary

Do not reintroduce content-typed long-memory stores here.

The unit entry may contain `understanding.kind` because Digest already emits that lightweight kind for local readability, but retrieval should not depend on a fixed concept/thread/progression ontology. The primary retrieval object is still the unit and its reading outputs.

## Index Surfaces

Storage is unit-centered, but retrieval should index multiple field-specific surfaces.

This avoids flattening source, understanding, response, and annotations into one undifferentiated blob while keeping `understanding` as the primary long-distance memory surface. In V1, all valid retrieval documents participate in lexical recall, but only `unit_understanding` participates in dense vector recall.

### Source Surface

Index:

- accepted source text
- text from `accepted_source_unit.paragraph_slices`
- annotation `source_quote` may also be included as exact source evidence

Use:

- BM25 / full-text matching for names, terms, repeated phrases, images, quotes, and exact wording

Default channel posture:

- high lexical weight
- no dense vector weight in V1

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

- medium-low to medium lexical weight
- no dense vector weight in V1

Each annotation should produce one retrieval document. Its retrieval text should combine the exact source quote and the annotation content, for example `source_quote + "\n" + content`, because the quote gives source footing while the note content gives readerly meaning. Do not split quote and note into separate v1 documents.

### Response Surface

Index:

- `response`

Use:

- recall readerly aftertaste, questions, felt pressure, and companion-like continuity

Default channel posture:

- low lexical weight
- no dense vector weight in V1

Response is useful as a lexical support signal, but it should not dominate source-grounded retrieval or later Digest context. It is a support signal, not the primary memory truth.

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

Every valid retrieval document is eligible for lexical retrieval. Dense retrieval is Understanding-only in V1:

- FTS5 indexes `retrieval_docs.text` for lexical / BM25 candidate ranks.
- sqlite-vec embeds only `unit_understanding` documents for dense candidate ranks.

This is an intentional performance and context-discipline choice. Source, response, and annotation text can still help recall through FTS5, but they are not treated as dense semantic memory. Understanding is the only surface expected to carry the durable semantic memory that future reading should recall.

Surface differences should instead be expressed through channel weights and later unit aggregation:

| surface | lexical channel | dense channel | role |
| --- | --- | --- | --- |
| `unit_source` | high | none | exact wording, names, quotes, source-near lexical recall |
| `unit_understanding` | medium | high | primary semantic memory of what the unit established |
| `unit_annotation` | medium-low to medium | none | auxiliary recall through marked quote / note wording |
| `unit_response` | low | none | auxiliary recall through readerly aftertaste / pressure wording |

The implementation may store these as a `weight_profile` value on `retrieval_docs` and resolve concrete numeric weights in retrieval config. Empty or invalid material should not create a retrieval document at all. Once a retrieval document exists, it should always be FTS-indexed. Vector indexing is expected only for `unit_understanding` in `hybrid` mode and may be pending / absent while a book is being read in `text_only` mode.

### V1 Document Granularity

Use surface-specific document granularity:

- `unit_source`
  - one retrieval document per `accepted_source_unit.paragraph_slices[]` item
  - retrieval doc id pattern: `unit:{id}#source:slice:{index}`
  - text: the recorded slice text
  - metadata: `paragraph_index`, `start_char`, `end_char`, `text_role`, `source_span_id`
  - purpose: exact phrase, name, quote-like callback, and repeated wording recall
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
  - purpose: auxiliary lexical recall of visible notes and exact lines that were previously marked
- `unit_response`
  - zero or one retrieval document per Unit Memory Entry
  - retrieval doc id pattern: `unit:{id}#response`
  - text: `digest.response`
  - omit this document when response is empty
  - purpose: low-weight lexical support for readerly aftertaste, question, pressure, and companion-like continuity

Do not create these documents in v1:

- no sentence-level source documents
- no whole-paragraph documents unless the accepted paragraph slice is itself whole
- no multiple understanding documents for one unit
- no separate source-quote-only and annotation-note-only documents
- no default `unit_all_text` blob that flattens source, understanding, response, and annotations together

If later retrieval review shows that an additional whole-unit semantic surface is needed, add it as a low-weight `unit_brief` surface. Do not add it as a default v1 document, because `unit_understanding` already carries the primary whole-unit semantic memory.

Retrieval should score sub-documents first, then aggregate by `unit_id`. Digest should receive compact Understanding briefs, not a loose pile of disconnected snippets or rich multi-field bundles.

## Retrieval Outline

### Recall Generation And Runtime Queries

`Ingest` selects the next forward source unit first.

Prior-reading recall generation remains part of the `Ingest` step. Do not introduce a separate query-generation LLM call by default.

The recall should be about the selected unit, not about a broad chapter topic.

Current Ingest recall contract:

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

Rules:

- Ingest emits zero to three recalls.
- `recall_text` should be a concise reader-facing description of earlier reading that the selected unit naturally asks the Reader to remember.
- `recall_text` is not a question-answer prompt for Digest and should not ask for a full summary.
- `basis` is `selected_source_unit` in v1.
- If recalls are empty intentionally, runtime skips long-distance Unit Memory retrieval for that cycle.
- If recall data is missing/malformed or boundary fallback changes the accepted unit, runtime may derive a fallback query from the accepted source unit text.
- Fallback query text should be a clipped, whitespace-normalized source-unit excerpt, capped at roughly `1200` characters.
- Retrieval trace should record whether retrieval came from `tool_retrieve_unit_memory`, `ingest_recall`, `retry_ingest_recall`, or `runtime_source_text_fallback`.

Do not add unbounded query planning objects in V1. Multiple recalls are allowed, but they are capped and reader-shaped rather than a general search-plan interface.

### FTS5 Query Builder

FTS5 query construction should be centralized in `UnitMemoryIndex`, not spread through runner code.

V1 lexical query builder:

- normalize whitespace and strip control characters
- discard lexical search when the normalized query has fewer than `3` Unicode codepoints, because the trigram tokenizer cannot produce useful matches
- split the query into phrase candidates on sentence punctuation, line breaks, and semicolon-like separators
- keep up to `8` phrase candidates
- cap each phrase candidate at roughly `80` characters
- discard phrase candidates shorter than `3` Unicode codepoints
- escape double quotes by doubling them
- render each phrase as a quoted FTS5 phrase
- join phrases with `OR`

If no safe phrase candidate remains, skip the FTS5 channel for that cycle and record `fts_skipped_reason = "empty_or_too_short_query"` in the retrieval trace.

This builder is intentionally conservative. It avoids exposing raw model text directly as FTS5 query syntax while still supporting Chinese phrase and exact-fragment recall through the trigram tokenizer.

### Candidate Retrieval

Use retrieval according to the selected `memory_retrieval_mode`:

- all modes use a lexical candidate set from SQLite FTS5 BM25 over all valid retrieval documents
- `hybrid` mode also uses a semantic candidate set from sqlite-vec dense vector KNN over `unit_understanding` documents only
- optional metadata filters:
  - same book
  - only prior units
  - exclude current unit
  - exclude recent-neighbor units already carried directly

The recent-neighbor exclusion is important: recent memory will be passed directly to Digest, so long-distance retrieval should avoid returning the same nearby units again unless explicitly requested.

V1 recent-neighbor exclusion:

- exclude units with `unit_index > current_unit_index - recent_neighbor_exclusion_unit_count`
- default `recent_neighbor_exclusion_unit_count = 20`
- also exclude units whose ids appear in the prompt-facing `recent_reading_memory.active_entries[].source_unit_span_id`
- if all candidates are excluded, return empty long-distance retrieval and rely on direct recent memory

### Ranking And Aggregation

Rank sub-document hits first, then aggregate to unit-level memory briefs.

Ranking should consider:

- retrieval rank from FTS5 BM25
- retrieval rank from sqlite-vec vector search
- surface / channel weights from the retrieval document's weight profile, with dense channel available only for `unit_understanding`
- distance from current unit
- exact source phrase match bonus
- diversity across units and surfaces
- duplicate suppression against recent memory

Do not fuse raw scores in v1. Use RRF first, then aggregate by unit.

The final output should explain why a unit was retrieved in machine-readable terms for audit, but Digest should see only reader-usable context.

### Runtime Ownership And Degradation

Retrieval belongs between `Ingest` and `Digest` in runtime orchestration:

```text
Ingest LLM
  -> selected source unit
  -> optional bounded prior-reading recalls
  -> retrieve_unit_memory tool call when recalls are non-empty

Runtime
  -> UnitMemoryIndex.retrieve_for_recalls(...)
  -> mode-aware retrieval, optional RRF, unit aggregation
  -> merged ReadingMemory text rendering

Digest LLM
  -> current source unit
  -> top-level ReadingMemory with direct recent and selected retrieved Understanding lines
```

`Digest` should not know about SQLite, FTS5, sqlite-vec, embedding providers, RRF, raw scores, or retrieval rows. It should only see reader-usable prior-reading support.

### Retrieval Performance Envelope

High-frequency retrieval is acceptable only if it is bounded. Retrieval is an enhancement to the read cycle, not a synchronous critical dependency that may stall `Digest`.

V1 read-time defaults:

- `memory_retrieval_mode = hybrid`
- `max_recalls_per_ingest = 3`
- `min_retrievable_prior_units = 20`
- `recent_neighbor_exclusion_unit_count = 20`
- `retrieval_total_timeout_ms = 800`
- `query_embedding_timeout_ms = 500`
- `fts_timeout_ms = 100`
- `vector_timeout_ms = 250`
- `aggregation_timeout_ms = 50`

Execution rules:

- If fewer than `min_retrievable_prior_units` have been completed, skip long-distance retrieval and rely on recent-neighbor memory.
- In `text_only` mode, the retrieval budget is spent only on FTS5, unit aggregation, and packaging. No query embedding should be requested.
- In `hybrid` mode, start FTS5 retrieval without waiting for query embedding; run vector retrieval only after the query embedding is available.
- Cache query embeddings by `(query_text_hash, embedding_model, query_instruction_version)`.
- Keep candidate fanout bounded by the documented `lexical_top_k` and `dense_top_k`.
- Keep prompt context bounded by `max_units_to_digest_context`.
- Record latency breakdown for query generation, query embedding, FTS5, vector KNN, RRF, unit aggregation, and prompt packaging.

Performance implications:

- FTS5 and unit aggregation are expected to be cheap at single-book scale.
- Query embedding is the main per-unit online cost in `hybrid` mode.
- Vector indexing after `Digest` is write-side maintenance and should not block the next read cycle.
- `text_only` mode should remain a first-class mode, not just an error fallback, so users can choose lower latency and simpler local dependencies.

V1 degradation policy:

- If retrieval fails after `Ingest` succeeds, continue to `Digest` without long-distance retrieved memory.
- If FTS5 succeeds and vector retrieval fails, continue with FTS-only candidates.
- If vector retrieval succeeds and FTS5 fails, continue with vector-only candidates.
- If the Unit Memory index does not exist yet, treat retrieval as empty.
- If retrieval exceeds its time budget, return empty retrieval and record a timeout.
- If `hybrid` mode is selected but query embedding times out, continue with text-only retrieval for that cycle.
- Retrieval failure should not fail the read cycle unless the failure corrupts the Unit Memory ledger itself.

Audit should keep the engineering trace separate from prompt context. A retrieval trace should record:

- recalls and per-recall internal query metadata
- query source: `tool_retrieve_unit_memory`, `ingest_recall`, `retry_ingest_recall`, or `runtime_source_text_fallback`
- selected memory retrieval mode
- retrieval config version
- latency breakdown
- channel candidate counts
- top retrieval document ids
- RRF and aggregation scores
- selected unit ids
- degradation reason, when present

The prompt-facing `ReadingMemory` block should omit raw scores and internal ids unless a later prompt design explicitly needs a reader-safe locator.

### Digest Context Packaging

Digest should not receive raw index rows.

It should receive one top-level `ReadingMemory` block containing compact prior Understanding lines. Direct recent memory and selected retrieved long-distance memory should be merged before rendering because both are the same prompt-facing substance: prior Understanding.

Prompt-facing shape:

```xml
<ReadingMemory>
P42 U18: ...
P41 U17: ...
P12 U04: ...
</ReadingMemory>
```

Rendering rules:

- one line per selected prior unit
- simple position prefix, such as `P42 U18`, with a compact chapter prefix only when needed for disambiguation
- one relevant Understanding per selected prior unit
- line budget uses stored Understanding token estimates plus the estimated token cost of the position prefix
- first estimator is `tiktoken_o200k_base_v1` with `o200k_base`, `cl100k_base` fallback, and an initial `1.10` safety multiplier because the target MiniMax tokenizer differs from `tiktoken`
- hot current-chapter memory has an internal `5,000` estimated-token pool; selected long-distance retrieved memory has an internal `10,000` estimated-token pool; the merged prompt-facing `ReadingMemory` block has an effective `15,000` estimated-token ceiling
- no per-entry XML tags such as `MemoryBrief` or `Understanding`
- no recent-vs-retrieved labels in the prompt
- no prior source excerpt
- no prior Response text
- no prior Annotation text
- retrieval reason, matched recall id, matched surface, source, score, and suppression reason stay in audit / trace

Digest context packaging is now implemented as the live Digest prompt path. Remaining work is calibration, not initial packaging:

- maximum ReadingMemory line count and token budget calibration after the initial `5K hot / 10K retrieved / 15K total` estimate
- whether MiniMax's official tokenizer should replace `tiktoken` after latency and calibration review
- how broad selected retrieved memory should be before it starts to distract from the current source unit

### Retrieval Review Criteria

V1 should use a human-reviewable retrieval trace before broad automated scoring. Each review record should show:

- current source unit
- Ingest retrieval query or runtime fallback query
- top retrieved unit briefs
- matched surfaces and retrieval reasons
- whether the selected Understandings were rendered into `ReadingMemory`

Review dimensions:

- relevance: the retrieved unit is genuinely related to the current unit
- continuity helpfulness: the memory helps the current reading remain continuous without forcing a callback
- source grounding: the match can point back to source, Understanding, Annotation, or Response evidence in trace, while Digest receives Understanding only
- non-redundancy: the result is not merely repeating recent-neighbor memory already carried directly
- non-dominance: the retrieved memory supports the current source unit without becoming the main object of reading
- coverage: important prior dependencies are not missing from the top briefs
- noise: unrelated top briefs are rare enough not to pollute `ReadingMemory`

Use review findings to calibrate fanout, surface / channel weights, recent-neighbor exclusion, `ReadingMemory` budget, MMR, and whether V2 needs a second lexical channel.

### Persistence And Refresh

`UnitMemoryLedger` is the durable source of truth. Retrieval documents, FTS5 rows, and sqlite-vec rows are derived indexes and must be rebuildable.

V1 write lifecycle:

- write the Unit Memory Entry during settlement after a `Digest` result has been accepted
- derive retrieval documents from that entry
- update the FTS5 index for those retrieval documents
- in `hybrid` mode, request embeddings for `unit_understanding` documents and update the sqlite-vec index within the write-side budget
- in `text_only` mode, vector embeddings may remain absent / pending unless a background rebuild is explicitly requested
- if embedding or vector insertion fails, keep the Unit Memory Entry and lexical index usable, and mark vector indexing pending / failed for retry

The read cycle should not be blocked by rebuildable index maintenance. Ledger write failure is serious; index update failure should degrade retrieval and be recoverable.

Write-side vector maintenance defaults:

- `vector_index_write_budget_ms = 1000`
- if the budget is exceeded, leave remaining Understanding vector rows as `pending`
- pending vector rows should not prevent FTS retrieval, text-only mode, or resume
- hybrid retrieval should use available vector rows only and record vector coverage in the retrieval trace

Implementation should record enough index metadata to make rebuilds safe:

- tokenizer config / lexical index version
- embedding provider, model id, dimension, and vector metric
- retrieval document build version
- weight profile version
- promptset / Digest output contract version that produced the source entry

The first implementation should include a rebuild path that can recreate retrieval documents, FTS5, and Understanding-only vector rows from the ledger.

Remaining implementation hardening:

- explicit rebuild / catch-up command for derived retrieval documents, FTS5 rows, and Understanding vector rows
- tokenizer review results and whether V2 needs a dual lexical channel
- embedding model version pinning and local Ollama health checks beyond graceful degradation
- index rebuild checksums and prompt-version compatibility

## What We Still Need To Design

- Context calibration:
  - maximum useful `ReadingMemory` line count under the fixed token budgets
  - whether the first `5K / 10K / 15K` budget split should be adjusted after real read traces
  - whether Digest needs any reader-safe locator beyond `P{paragraph} U{unit}`
- Retrieval calibration:
  - whether retrieval review requires a second `unicode61` / `porter unicode61` lexical channel
  - calibration of the initial V1 fanout, RRF, surface / channel weight, aggregation, and MMR defaults
  - dedupe and diversity policy after real trace review
- Vector maintenance:
  - whether switching from `text_only` to `hybrid` should trigger vector-index catch-up immediately or leave it pending
  - explicit operator command for vector catch-up / rebuild
- Recent-neighbor policy:
  - whether the current current-chapter hot-memory policy should be tightened by unit count as well as token budget
  - whether the default long-distance neighbor exclusion window should stay at `20` units after real trace review
  - how often retrieved Understandings duplicate hot memory despite source-span dedupe
- Evaluation / review criteria:
  - concrete review examples
  - labeling rubric and pass / fail thresholds
  - calibration protocol for weights, topK, MMR, and context budget

## Current Recommendation

Use one append-only Unit Memory Entry per completed read unit.

Create retrieval documents from all four memory surfaces. Every valid retrieval document should be FTS-indexed, but only Understanding should be vector-index eligible in V1:

- accepted source unit
- `understanding`
- `response`
- `annotations[]`

This keeps retrieval broad while making the semantic memory spine explicit. Source, response, and annotation documents may recall Entries through lexical evidence, but `understanding` has the highest authority and is the only dense-vector surface.

Use the initial conservative retrieval parameters in this document: per-recall top `40` lexical docs across all FTS surfaces, per-recall top `40` dense docs from `unit_understanding`, `rrf_k = 60`, modest surface / channel weights, unit aggregation led by the best matching retrieval document, and MMR disabled unless review shows repeated near-duplicate briefs.

Before reading a book / starting a read session, choose `memory_retrieval_mode`: default `hybrid` for FTS5 plus query embedding and sqlite-vec, or `text_only` for FTS5-only low-latency memory retrieval. Treat `UnitMemoryLedger` as the only durable fact source for long-distance memory. Keep FTS5 and sqlite-vec as rebuildable indexes. Execute retrieval in runtime after `Ingest` and before `Digest`, enforce the performance budget, degrade gracefully when retrieval/index channels fail, and use retrieval review records to calibrate parameters before broad evaluation.

The retrieval result should be source-grounded and unit-centered, then rendered to Digest as compact prior-reading support rather than as a hidden backread path.
