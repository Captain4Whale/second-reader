# Second Reader Annotation Pack v0

Status: reference implementation complete; contract version `0.1.0`.

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

## Detached package profile

The formal detached artifact uses media type `application/zip;profile="https://www.w3.org/TR/epub-anno-10/"` and contains exactly one root entry:

```text
/
└── annotations.json
```

`annotations.json` is the same complete canonical JSON-LD `AnnotationSet` that can be retained as a development artifact. The package must not contain the source EPUB, XHTML, cover, validation report, a `mimetype` entry, a custom manifest, optional assets, or private runtime data.

Second Reader v0 writes a deliberately narrow classic single-disk ZIP: root filename `annotations.json`, DEFLATED level 9, timestamp `1980-01-01T00:00:00`, Unix regular-file mode `0644`, flags zero, and no archive/entry comments or extra fields. The validator rejects ZIP64, multi-disk, prefixed/trailing data, extra entries, unsafe paths or modes, encryption/data descriptors, local/central-header disagreement, package bytes over 8 MiB, entry bytes over 16 MiB, compression ratios over 100, malformed DEFLATE/CRC, and noncanonical or semantically invalid JSON. It validates in memory and never extracts to disk.

These reproducibility and security restrictions are the Second Reader package profile, not general requirements asserted by the W3C drafts. Repeated generation is byte-stable within the supported compressor toolchain; independent validation does not require re-compressing with the local zlib version, because DEFLATE bitstreams are not guaranteed to remain identical across zlib versions.

## Version axes

- `sr:specVersion`: `0.1.0`
- `sr:schemaVersion`: `0.1.0`
- `sr:extensionVersion`: `0.1`
- canonical JSON: `sr-canonical-json-v1`
- detached package: canonical classic ZIP profile described above
- validation report JSON: `sr-annotation-validation-report-json-v1`

Any wire schema edit bumps `sr:schemaVersion`. A new required semantic, ID input change, target meaning change, or Highlight/Note body rule change requires a new major contract directory. Standards URLs never move to an undated or newer draft without an explicit conformance delta review.

## Local verification

After backend development dependencies are installed:

```bash
make annotation-pack-contract-check
```

The check is network-free: it validates the three schemas against Draft 2020-12, validates examples, verifies generated bindings and byte-identical runtime copies, rebuilds and byte-checks the tracked Tiny Reader real-EPUB golden, and stages the exact GitHub Pages projection without fetching remote contexts.

The examples are schema-valid protocol examples. Fixed identity, fingerprint, canonical-byte, package, and anchor vectors are implemented in backend tests; the end-to-end public-safe reference lives under `reading-companion-backend/tests/annotation_pack/fixtures/tiny-reader/`. These examples and goldens prove the Second Reader reference implementation offline, not external Reader interoperability.

`sr-canonical-json-v1` sorts object keys by Unicode code point, preserves array and string code-point order, emits UTF-8 without BOM or optional whitespace, uses lowercase JSON control escapes with `/` unescaped, and terminates with exactly one LF. Its numeric domain is limited to JSON integers in `[-(2^53-1), 2^53-1]`; floating-point values and lone Unicode surrogates are semantic errors. This restriction also applies to declared extension values before they can participate in a canonical Pack or semantic digest.
