# Second Reader Reading Product Output v1

Status: canonical v1 contract implemented and accepted; public schema hosting is deferred.

Reading Product Output is the mechanism-neutral product fact produced while Second Reader reads one exact EPUB. It records the source Units that were actually accepted and, for each Unit, the resulting `understanding`, `response`, and source-grounded `marginalia`. It is the stable boundary from which product projections and Annotation Packs may be derived even when the private reading mechanism changes.

## Authorities

- wire authority: [`schema/reading-product-output.schema.json`](schema/reading-product-output.schema.json)
- local complete-revision pointer schema: [`schema/publication-pointer.schema.json`](schema/publication-pointer.schema.json)
- local sanitized validation-report schema: [`schema/validation-report.schema.json`](schema/validation-report.schema.json)
- positive examples: [`examples/partial-reading-product.json`](examples/partial-reading-product.json) and [`examples/complete-reading-product.json`](examples/complete-reading-product.json)
- implementation sequence and Definition of Done: [`../../../docs/implementation/reading-product/reading-product-output-v1-detailed-design-and-implementation-handoff.md`](../../../docs/implementation/reading-product/reading-product-output-v1-detailed-design-and-implementation-handoff.md)

The pointer and report are local publication companions. They do not embed or redefine the Reading Product wire. Runtime bindings and schema copies are generated or byte-checked derivatives, not additional authorities.

## Stable schema IRI

`https://captain4whale.github.io/second-reader/schema/reading-product/v1/reading-product-output.schema.json`

This remains the reserved future public location, but `DEC-159` defers GitHub Pages hosting because the current producer/consumer lifecycle does not require a remotely served schema. The checked projection remains a deterministic derivative only. The current workflow does not upload or deploy it, and the IRI must not be described as live. Any future public hosting requires an explicit follow-up decision plus served-byte verification against the canonical schema.

## Product boundary

Reading Product contains the durable result of reading:

- the exact EPUB and canonical BookDocument substrate against which the reading occurred;
- the accepted Unit's start/end source range;
- the Unit-level `understanding` and `response`;
- zero or more Highlights or Notes, each bound to one exact source range and quote.

It deliberately excludes the mechanism and its evidence trail. Selection reasons, alternative candidates, source-window previews, prompts, model/provider data, token usage, memories, retrieval traces, checkpoints, job IDs, private Agent IDs, compatibility taxonomies, retries, and provenance remain runtime or audit facts. A finalizer may validate and aggregate accepted product records; it must never infer product meaning from those private artifacts.

The contract is not an Agent prompt schema. A model may return a mechanism-private shape. The mechanism adapter and settlement runtime are responsible for producing a valid product record without copying private fields into this wire.

## Canonical wire

Every document contains only:

- `schema_version`: `reading-product-output/1.0`
- `reading_id`: a fresh lowercase RFC 4122 UUIDv4 URN for one reading revision
- `status`: `partial` or `complete`
- `source`: exact `epub_sha256` plus `book_document_substrate_sha256`
- `started_at`, and `completed_at` only when complete
- ordered `units[]`

Every Unit contains only:

- `unit_id`: the one-based six-digit identifier derived from `sequence_index`, for example `u000001`
- `sequence_index`: contiguous and one-based within the reading revision
- `source_range`: the accepted Unit range
- `settled_at`: the UTC time at which the Unit product transaction committed
- non-empty `understanding` and `response`
- ordered `marginalia[]`

Every Marginalia contains only:

- `marginalia_id`: the Unit ID plus a one-based, three-digit item index, for example `u000001-m001`
- `kind`: `highlight` or `note`
- `source_range` and exact `source_quote`
- `body_text` only for a Note

A Highlight forbids `body_text`. A Note requires non-empty `body_text`. The wire has strict property whitelists at every level. Runtime validation additionally enforces ID/index coherence, deterministic order, non-overlapping ordered Units, source containment, quote round-trip, and semantic duplicate rejection.

`source_quote` is limited to 1024 Unicode code points, matching Annotation Pack v0's `TextQuoteSelector.exact` ceiling. This profile constraint makes every accepted Reading Product Marginalia structurally eligible for Pack export instead of allowing a complete Product to contain an inherently unexportable mark.

## Source identity and coordinates

`epub_sha256` is the lowercase SHA-256 of the exact EPUB bytes. `book_document_substrate_sha256` is the lowercase SHA-256 produced by the shared `sr-book-document-substrate-v1` canonical projection/stream. This binds product ranges to the exact parsed source meaning while excluding local paths and output-language/runtime metadata. Annotation Pack may retain compatibility re-exports of the same implementation, but must not own a second algorithm.

A source coordinate has exactly `chapter_id`, `paragraph_index`, and `char_offset`:

- `chapter_id` and `paragraph_index` are one-based values from canonical `public/book_document.json`;
- `char_offset` is a zero-based Unicode code-point offset in the paragraph's stored `text`;
- every range is start-inclusive and end-exclusive;
- start and end must belong to the same chapter and satisfy `start < end`;
- a Unit spans only readable, non-auxiliary BookDocument text;
- a Marginalia range must be non-empty, be contained by its Unit range, and map wholly into one EPUB XHTML/HTML resource.

To reconstruct a range, slice the first and last paragraph at their coordinate offsets, include complete intervening readable paragraphs, and join paragraph slices with exactly two LF characters (`\n\n`). A valid Marginalia satisfies `reconstructed_text == source_quote` byte-for-byte as a Python Unicode string. No NFC or quote normalization may turn an inexact candidate into an exact product mark.

An ambiguous quote is not resolved by first match. The runtime may accept it only when the mechanism already supplied a unique exact range. Otherwise that Marginalia item is rejected into private audit findings while the valid Unit-level `understanding`, `response`, and other valid Marginalia may still settle.

## Settlement, partial projection, and finalization

One successful Unit is committed atomically before the accepted reading cursor advances. The Product Store is the commit truth; Unit Memory, reaction records, compatibility chapter views, and audit rows are rebuildable consequences. Identical replay is unchanged. A repeated ID with different canonical bytes, a sequence gap, overlapping Unit, source mutation, or invalid non-empty U/R fails closed.

The running projection has `status=partial` and no `completed_at`. It may contain no Units before the first settlement. It is useful for inspection and recovery but is never selected by the public `current.json` pointer and cannot be exported as an Annotation Pack.

The whole-book finalizer may seal `status=complete` only when every scheduled `mainline` and `deferred` reading-plan chapter is complete. `auxiliary` plan items are outside this condition. Chapter-only runs, audit-window caps, partial stops, source mutation, missing Units, range/order failure, or an unfinished scheduled chapter must not seal. The finalizer aggregates already committed Units; it never calls the model and never repairs or invents semantics.

Complete products are immutable revisions under:

```text
public/reading-products/
├── current.json
└── revisions/<reading-product-sha256>/
    ├── reading-product.json
    └── validation-report.json
```

The revision ID is the SHA-256 of canonical `reading-product.json` bytes. The pointer switches atomically only after the product and sanitized report validate. Repeated finalization returns the existing byte-identical revision without changing timestamps or digests. Failed reports may be retained outside immutable revisions but may never be selected as current.

## Annotation Pack relationship

Reading Product is not W3C Annotation JSON-LD. Annotation Pack consumes only complete-product Marginalia:

| Reading Product fact | Annotation Pack handoff/result |
| --- | --- |
| `kind` | Highlight/Note motivation |
| `source_range` | producer-neutral SourceRange, then EPUB href and TextPosition |
| `source_quote` | TextQuote `exact` and source round-trip |
| Note `body_text` | `TextualBody.value` |
| Unit `settled_at` | Annotation `created` |

`understanding` and `response` remain core product outputs but are not Annotation Pack fields. EPUB title/authors/manifest resources, W3C wrappers, deterministic Pack IDs, generation time, packaging, and Pack publication companions remain source/exporter responsibilities. The Reading Product contract does not alter Annotation Pack v0 wire semantics.

## Compatibility and versioning

New normal `attentional_v2` runs write Reading Product directly. Existing historical outputs remain readable through explicit legacy compatibility paths; they are not silently promoted into complete Reading Product revisions. The old `attentional_v2-phase9` Annotation Pack adapter may remain as an explicitly selected legacy adapter, never as an automatic fallback or a requirement on this contract. Phase 8 remains unsupported.

Fresh reruns create a new `reading_id`; v1 Marginalia are immutable within that reading revision. Replacement/supersession semantics are intentionally absent. A change to coordinate meaning, required fields, finalization meaning, ID semantics, or source identity requires a new contract version.

## Local verification

The contract check is network-free and does not call any model provider:

```bash
make reading-product-contract-check
```

It validates all schemas and examples, exercises strict negative cases and semantic invariants, verifies runtime schema copies when present, and stages the unified allowlisted GitHub Pages projection.
