# Second Reader Annotation Pack v0

Status: canonical minimal v0 contract; not yet published at its GitHub Pages IRI.

This directory is the protocol authority for Second Reader Annotation Pack v0. A Pack is a detached JSON-LD `AnnotationSet` for one exact EPUB file and the Highlight/Note annotations exported by Second Reader. It uses only terms from the pinned W3C EPUB Annotations context, including Web Annotation and Dublin Core terms. The contract is W3C-aligned; it is not a W3C schema and does not claim conformance to the EPUB Annotations Working Draft.

## Authorities

- Pack wire authority: [`schema/annotation-pack.schema.json`](schema/annotation-pack.schema.json)
- local publication-pointer auxiliary schema: [`schema/publication-pointer.schema.json`](schema/publication-pointer.schema.json)
- local validation-report auxiliary schema: [`schema/validation-report.schema.json`](schema/validation-report.schema.json)
- pinned standards and status wording: [`standards.md`](standards.md)
- unpublished contract history: [`CHANGELOG.md`](CHANGELOG.md)

The pointer and report schemas describe local publication companions. They neither embed nor redefine `annotations.json`. Generated Pydantic bindings and backend runtime schema copies are checked derivatives, not additional authorities.

## Stable schema IRI

`https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/annotation-pack.schema.json`

GitHub Pages is the approved publication mechanism. The site contains a strict allowlist of the Annotation Pack and Reading Product contract artifacts; Annotation Pack lives under `/schema/annotation-pack/v0/`. Minimal v0 has no Second Reader JSON-LD vocabulary, custom context, or namespace landing page. A feature-branch build proves only the projection; the schema IRI is not live until the workflow reaches the default branch, Pages deploys successfully, and served bytes are compared with this authority.

## Canonical wire

Every Pack is a strict `AnnotationSet` with exactly these root properties:

- `@context`: the string `https://www.w3.org/ns/epub-anno.jsonld`
- `id`: a lowercase RFC 4122 UUIDv5 URN
- `type`: `AnnotationSet`
- `generator`: the fixed software identity `https://github.com/Captain4Whale/second-reader`, `Software`, `Second Reader Annotation Pack Exporter`
- `generated`: a UTC timestamp with second precision
- `about`: exact EPUB identity and display metadata
- `items`: Highlight and Note annotations, sorted by `id` by the reference builder

`about` requires:

- `dc:identifier`: exactly one `nih:sha-256;<digest>` value, where `<digest>` is the 64-character lowercase hexadecimal SHA-256 of the exact EPUB bytes
- `dc:format`: `application/epub+zip`
- `dc:title`: a non-empty source-book title
- optional `dc:creator`: a non-empty, duplicate-free list emitted when the source EPUB has usable authors

Each Annotation requires `id`, `type=Annotation`, `created`, `motivation`, and `target`. A Highlight has `motivation=highlighting` and no `body`. A Note has `motivation=commenting` and one `TextualBody` containing only `type` and a non-empty `value`. Per-annotation creator, private kind, track, provenance, public digest, chapter context, anchor id, CFI, and body format/language fields are not part of minimal v0.

Each target contains only:

- `source`: the canonical relative XHTML/HTML href from the exact EPUB manifest
- `selector`: exactly two selectors in fixed order
  1. `TextQuoteSelector`, with required `exact` and optional non-empty `prefix`/`suffix` (omit either when no adjacent context exists)
  2. `TextPositionSelector`, with integer `start` and `end`

The schema owns object whitelists, required fields, enums, scalar formats, limits, selector order, and Highlight/Note body conditionals. The offline semantic validator owns `start < end`, quote-length/position coherence, deterministic ID recomputation, item ordering, and semantic duplicate rejection. Manifest membership and actual quote/prefix/suffix round-trip require the exact EPUB, so the EPUB-backed anchor/export acceptance path owns those checks; standalone validation never claims to have performed them.

## Producer-neutral information responsibility

This section is the canonical responsibility contract between a reading mechanism and Annotation Pack export. The JSON Schema remains the sole authority for the public wire. This section answers which facts must exist before that wire can be built and who is allowed to supply them.

| Responsibility | Required facts | Owner | Public result |
| --- | --- | --- | --- |
| Source publication facts | exact EPUB bytes; EPUB SHA-256; media type; title; usable authors when present; manifest XHTML/HTML hrefs; deterministic resource text; coherent mapping from the shared `BookDocument` to those resources | verified EPUB/parser substrate, never the LLM or reading mechanism | `about`, target `source`, and the text stream against which selectors are checked |
| Annotation intent | `highlight` or `note`; one exact contiguous selected source span; the exact source text for that span; non-empty note text only for a Note | the reading mechanism as a whole; the model may choose the span/content, while runtime may resolve or copy exact source text | `motivation`, optional `body`, and the semantic choice of target passage |
| Settlement event | one valid UTC creation time for the accepted annotation | reading runtime/settlement, not necessarily model-authored | Annotation `created` |
| Pack derivation | fixed generator identity; Pack generation time; exact href and TextQuote/TextPosition projection; motivations and body wrapper; deterministic IDs, ordering, validation, serialization, packaging, pointer/report metadata | producer adapter plus generic Annotation Pack resolver/builder/exporter | every remaining public field and all local publication companions |

The minimum normalized handoff from any mechanism adapter to the generic Pack pipeline is one `AnnotationDraft` per candidate:

| Neutral value | Requirement |
| --- | --- |
| `kind` | exactly `highlight` or `note` |
| `source_range` | one start-inclusive/end-exclusive range in the canonical shared `BookDocument` coordinate system; the current representation is same-chapter paragraph/character coordinates |
| `source_quote` | non-empty exact source text for that range; it must round-trip against the verified source and is not free-form commentary |
| `body_text` | absent for Highlight; non-empty for Note |
| `created_at` | the runtime settlement timestamp carried into public `created` |

Adapter bookkeeping such as source-record index/digest, producer-snapshot digest, findings, and adapter version may accompany this handoff for safe export and reporting, but it is neither Agent semantic output nor public Pack data.

The default adapter consumes only a complete [Reading Product Output v1](../../reading-product/v1/README.md) publication selected by `public/reading-products/current.json`. It does not read Agent run state, reaction records, audit, prompts, or memory. `attentional_v2-phase9` remains an explicitly selected legacy input only; there is no automatic fallback, and phase8 remains rejected. A future mechanism may use a different prompt, ontology, ledger, version, or source-citation representation, but it must settle the same mechanism-neutral Reading Product facts rather than pretending to be phase9. The generic exporter must not infer annotation kind, source selection, or Note content from compatibility taxonomies.

Consequently, a reading mechanism does **not** need to generate EPUB hashes, book metadata, manifest hrefs, resource-wide TextPosition offsets, W3C JSON-LD, UUIDs, motivations, generator metadata, package files, or public digests. Those are verified or derived outside the mechanism. What the mechanism must preserve is the user-visible annotation decision: which exact source span is marked, whether it is a Highlight or Note, and the Note text when present.

## Resource text and TextPosition

`TextPositionSelector` offsets are zero-based Unicode code-point indexes into one deterministic logical text stream for `target.source`. `start` is inclusive and `end` is exclusive. The v0 stream is built as follows:

1. Read the exact verified UTF-8 XHTML/HTML manifest resource as XML; do not fall back to regex or plaintext recovery after a parse/coherence failure. A resource may contain exactly one simple HTML5 `<!DOCTYPE html>` immediately after optional BOM/whitespace and an optional XML declaration. Any other `DOCTYPE` or `ENTITY` token—including `SYSTEM`, `PUBLIC`, an internal subset, or duplicate/misplaced declarations—makes that resource unverifiable. Container and OPF XML remain DTD-free.
2. Visit `p`, `li`, `blockquote`, `caption`, `div`, `figcaption`, and `h1` through `h6` elements in document order.
3. Skip a non-heading container when emitting it would duplicate text already represented by a nested textual block and the container has no direct non-whitespace text.
4. For each included block, concatenate descendant text, replace every Python Unicode `\s+` run with one ASCII space, trim leading/trailing whitespace, and omit an empty result. Do not apply NFC or any other Unicode normalization to source text.
5. Join included blocks with exactly two LF characters (`\n\n`).

A valid target satisfies `0 <= start < end <= len(resource_text)` and `resource_text[start:end] == exact`. The reference producer emits up to 64 immediately adjacent code points before and after that range as `prefix` and `suffix`, omitting either property when its slice is empty. These requirements bind the selectors to the EPUB hash in `about`; they do not claim cross-edition anchoring.

## Deterministic identity

The reference implementation derives Pack and Annotation UUIDv5 values from NUL-framed canonical inputs under audited v0 namespaces:

- Pack: exact EPUB SHA-256 plus the fixed generator IRI
- Annotation: exact EPUB SHA-256, NFC canonical href, `start`, `end`, motivation, and the NFC Note body or an empty Highlight body field

Timestamps, quote context, producer records, and local publication paths do not participate. Changing any byte of the EPUB changes the `nih` identifier and the Pack/Annotation identity inputs. JSON Schema checks only the UUIDv5 URN shape; the semantic validator recomputes the values.

## Detached package and local companions

The formal detached artifact uses media type `application/zip;profile="https://www.w3.org/TR/epub-anno-10/"` and contains exactly one root `annotations.json`. It never contains the EPUB, XHTML, cover, validation report, manifest, optional assets, or private runtime data.

Second Reader retains its bounded deterministic classic-ZIP profile: one DEFLATED root file, fixed timestamp/mode/flags, no comments or extra fields, no ZIP64/multi-disk/encryption/data descriptors, hard byte/ratio limits, strict local/central-header agreement, and in-memory validation without extraction. Those restrictions are project rules, not W3C requirements.

Input snapshot/content digests, adapter details, findings, immutable revision paths, and recovery metadata may exist only in sanitized local pointer/report companions. The report always carries nullable `producer` and `adapter_version` fields; a publishable `valid` or `degraded` report requires an absolute producer IRI and a semantic-version adapter value, while a pre-Pack `failed` report may use null. These fields are forbidden from `annotations.json` and therefore from the `.annotations` entry.

## Compatibility and versioning

This path directly replaces an unpublished heavier v0 under `DEC-156`; there is no old-wire migration or compatibility mode. Phase 8 producer ledgers are rejected rather than upgraded. The contract path remains `v0` and the runtime constants remain `0.1.0` for local companion compatibility, but no version field is emitted in the public Pack.

After public deployment, a change to required wire semantics, deterministic identity inputs, target meaning, or Highlight/Note body rules requires a new contract path. Standards URLs never move to a newer draft without an explicit conformance-delta review.

## Local verification

After backend development dependencies are installed:

```bash
make annotation-pack-contract-check
```

The check is network-free. It validates all three schemas, validates the three examples, verifies generated bindings and byte-identical runtime schema copies, rebuilds the tracked Tiny Reader fixture, runs focused contract tests, and stages the strict Pages projection without dereferencing the W3C context.
