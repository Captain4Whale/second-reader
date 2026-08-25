# Standards baseline

Annotation Pack v0 pins dated standards so an upstream draft cannot silently change the implemented profile.

- W3C Web Annotation Data Model, Recommendation, 23 February 2017: <https://www.w3.org/TR/2017/REC-annotation-model-20170223/>
- EPUB Annotations 1.0, Working Draft, 21 May 2026: <https://www.w3.org/TR/2026/WD-epub-anno-10-20260521/>
- EPUB Annotations publication history, review entrypoint only: <https://www.w3.org/standards/history/epub-anno-10/>
- RFC 6920, Naming Things with Hashes: <https://www.rfc-editor.org/rfc/rfc6920>

The EPUB document is a Working Draft, not a Recommendation. Its JSON Schema and privacy/security sections are incomplete, so `annotation-pack.schema.json` is explicitly a Second Reader profile schema. Minimal v0 is described as aligned with the Web Annotation Recommendation and the dated EPUB Working Draft; it is never described as EPUB-WD conformant.

## Vocabulary and project requirements

The public wire uses the pinned EPUB context string `https://www.w3.org/ns/epub-anno.jsonld`. Validators recognize that exact IRI from an offline allowlist and do not dereference it. The profile does not publish or load a Second Reader context or namespace.

The following wire terms come from Web Annotation, the EPUB draft profile, or Dublin Core: `AnnotationSet`, `Annotation`, `id`, `type`, `generator`, `generated`, `created`, `motivation`, `body`, `target`, `source`, `selector`, `TextualBody`, `TextQuoteSelector`, `TextPositionSelector`, `exact`, `prefix`, `suffix`, `start`, `end`, `value`, `Software`, `name`, `dc:identifier`, `dc:format`, `dc:title`, and `dc:creator`.

Second Reader v0 deliberately makes some of those standard terms stricter than the upstream models: fixed generator identity, required generated/created timestamps, exact-file metadata, one RFC 6920 SHA-256 name in `dc:identifier`, Highlight/Note-only motivations, fixed body rules, exactly two ordered selectors, deterministic UUIDv5 identities and item order, strict object whitelists, and source-dependent quote/position validation. These are project profile requirements, not claims that W3C requires the same restrictions.

Text positions count Unicode code points in the deterministic resource stream defined once in [`README.md`](README.md). The stream and its exact-EPUB coherence rule are project choices made to remove ambiguity; they are not presented as a general W3C counting mandate.

## Detached package status

The detached artifact follows the pinned draft's ZIP shape: media type `application/zip;profile="https://www.w3.org/TR/epub-anno-10/"` and one root `annotations.json`. Second Reader further narrows it to a bounded deterministic classic-ZIP envelope with fixed writer metadata and no optional assets. Those reproducibility and security restrictions are project profile rules; cross-zlib DEFLATE bitstream identity is not claimed.
