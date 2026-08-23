# Tiny Reader Annotation Pack fixture

`source.epub` is a deliberately small, valid EPUB 3 publication used for the
Annotation Pack v0 end-to-end golden. It contains an EPUB navigation document,
two spine XHTML resources, six original body paragraphs, and fixed OPF
metadata. The exact tracked source is `3158` bytes with SHA-256:

```text
1325ba2f76406fb22a1bb0f02edd735983cc150f64cc4af5bb00fbf6d873f7a7
```

## Provenance and license

The title, headings, prose, Note body, metadata, and EPUB assembly code were
written specifically for the Second Reader test suite; they do not come from a
private evaluation book or a third-party publication. The fixture credits the
collective name `Second Reader Fixture Authors`. To remove redistribution
ambiguity, those original fixture contents are dedicated to the public domain
under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

The surrounding Second Reader source code remains under the repository's own
license. The W3C and EPUB names referenced by the generated protocol artifact
are standards identifiers, not source-text provenance.

## Rebuild and verification

From `reading-companion-backend/`, with the checked-in Python environment
installed, rebuild or byte-check every generated fixture file offline:

```bash
.venv/bin/python tests/annotation_pack/fixtures/tiny-reader/build_fixture.py --write
.venv/bin/python tests/annotation_pack/fixtures/tiny-reader/build_fixture.py --check
```

The builder fixes the EPUB ZIP member order, timestamp, Unix mode, storage
method, OPF identifier, metadata, and XHTML bytes. It then uses the production
`parse_epub_stream` -> neutral `build_book_document_from_chapters` -> source
normalization path to generate `producer/public/book_document.json`. It writes
one current-shaped settled Highlight and one current-shaped settled Note to the
native `reaction_records.json` envelope, runs the real explicit exporter with a
fixed UTC generation time, and records the resulting canonical JSON, detached
package, validation report, publication pointer, and digests.

The source EPUB uses only stored ZIP entries, so its fixture hash does not
depend on a DEFLATE implementation. The detached `.annotations` golden uses
the reference packager's pinned DEFLATE level and is byte-exact only for the
repository's currently supported Python/zlib toolchain. `--check` intentionally
detects a compressor-byte change; the project does not promise identical
DEFLATE bytes across zlib versions. Independent package validity depends on the
decompressed canonical `annotations.json`, CRC, and narrow ZIP profile, not on
recompressing it to match this golden.

The committed golden was generated and accepted with CPython `3.11.15`, zlib
`1.2.12`, and ebooklib `0.20`. A supported parser or compressor toolchain change
must explain any resulting byte/substrate drift and regenerate the golden
intentionally; changing an expected digest alone is not acceptance.

The generated layout is:

```text
source.epub
producer/
  public/book_document.json
  _runtime/run_state.json
  _mechanisms/attentional_v2/runtime/reaction_records.json
golden/
  annotations.json
  tiny-reader.annotations
  validation-report.json
  current.json
  digests.json
```

`golden/tiny-reader.annotations` is byte-identical to the formal package that
the exporter names `second-reader-agent-04f55dd82c11.annotations`; the generic
fixture filename keeps the committed golden easy to address. Both forms contain
exactly root `annotations.json`.

The golden deliberately succeeds without an EPUB CFI selector. The first spine
item observes the parser's existing spine-zero CFI-null behavior, and the
second item has only parser-produced lightweight CFIs; neither is published
without an exact CFI resolver and quote round-trip. Both annotations instead
prove exact XHTML href, `TextQuoteSelector`, and paragraph-character selector
round trips. This is an offline reference-implementation fixture, not evidence
of external Reader interoperability.

Validate and safely inspect the committed standalone artifacts without the
producer directory:

```bash
.venv/bin/python scripts/validate_annotation_pack.py \
  tests/annotation_pack/fixtures/tiny-reader/golden/annotations.json
.venv/bin/python scripts/validate_annotation_pack.py \
  tests/annotation_pack/fixtures/tiny-reader/golden/tiny-reader.annotations
.venv/bin/python scripts/inspect_annotation_pack.py \
  tests/annotation_pack/fixtures/tiny-reader/golden/tiny-reader.annotations
```
