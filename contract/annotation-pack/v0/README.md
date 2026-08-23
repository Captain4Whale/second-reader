# Second Reader Annotation Pack v0

Status: implementation active; contract version `0.1.0`.

This directory is the protocol authority for Second Reader Annotation Pack v0. The Pack is a compact JSON-LD `AnnotationSet` aligned with the W3C Web Annotation Data Model and the pinned EPUB Annotations Working Draft. The word **aligned** is deliberate: this project schema is not a W3C schema and does not claim full EPUB Annotations conformance.

## Authorities

- Pack wire authority: [`schema/annotation-pack.schema.json`](schema/annotation-pack.schema.json)
- local publication-pointer auxiliary schema: [`schema/publication-pointer.schema.json`](schema/publication-pointer.schema.json)
- local validation-report auxiliary schema: [`schema/validation-report.schema.json`](schema/validation-report.schema.json)
- Second Reader vocabulary context: [`context/second-reader-annotation-context.jsonld`](context/second-reader-annotation-context.jsonld)
- pinned standards and status wording: [`standards.md`](standards.md)
- compatible-change history: [`CHANGELOG.md`](CHANGELOG.md)

The pointer and report schemas describe local publication companions. They neither embed nor redefine the Pack wire document. Backend Pydantic bindings and runtime schema copies are generated artifacts; they are not additional authorities.

## Stable IRIs

- namespace: `https://captain4whale.github.io/second-reader/ns/annotation-pack#`
- Pack schema: `https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/annotation-pack.schema.json`

GitHub Pages is the approved publication mechanism. The repository workflow publishes an allowlisted projection of this contract after it lands on the default branch. A feature-branch push proves the mapping and build, but the IRIs must not be described as live until the Pages deployment and HTTP byte comparison succeed.

## Invariants beyond JSON Schema

The canonical schema owns wire shape, required fields, enums, basic formats, limits, and Highlight/Note body conditionals. Cross-object and source-dependent invariants remain semantic-validator responsibilities, including deterministic ID recomputation, creator equality, item ordering and uniqueness, publication/source coherence, digest recomputation, declared-prefix governance, privacy scanning, and anchor round trips against the exact EPUB.

Unknown unprefixed fields are rejected. The second `@context` object requires `"@protected": true` and the fixed `sr` binding. A compatible document may declare additional safe prefixes in that object and preserve optional prefixed fields; a semantic validator must reject undeclared prefixes, reserved-prefix redefinition, unsafe depth/size, or extensions that change core interpretation.

Source-derived quote strings are not normalized during serialization because their Unicode code-point coordinates must continue to match the source substrate. Metadata, creator names, and Note bodies are normalized by their builders before schema validation.

## Version axes

- `sr:specVersion`: `0.1.0`
- `sr:schemaVersion`: `0.1.0`
- `sr:extensionVersion`: `0.1`
- canonical JSON: `sr-canonical-json-v1`
- validation report JSON: `sr-annotation-validation-report-json-v1`

Any wire schema edit bumps `sr:schemaVersion`. A new required semantic, ID input change, target meaning change, or Highlight/Note body rule change requires a new major contract directory. Standards URLs never move to an undated or newer draft without an explicit conformance delta review.

## Local verification

After backend development dependencies are installed:

```bash
make annotation-pack-contract-check
```

The check is network-free: it validates the three schemas against Draft 2020-12, validates examples, verifies generated bindings and byte-identical runtime copies, and stages the exact GitHub Pages projection without fetching remote contexts.

The examples are schema-valid protocol examples. Fixed identity, fingerprint, canonical-byte, package, and anchor golden vectors are added by the later implementation slices using the tracked tiny EPUB fixture; these examples must not be treated as external-reader interoperability proof.
