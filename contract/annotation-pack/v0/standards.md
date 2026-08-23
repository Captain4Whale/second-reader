# Standards baseline

Annotation Pack v0 pins dated standards so an upstream draft cannot silently change the implemented contract.

- W3C Web Annotation Data Model, Recommendation, 23 February 2017: <https://www.w3.org/TR/2017/REC-annotation-model-20170223/>
- EPUB Annotations 1.0, Working Draft, 21 May 2026: <https://www.w3.org/TR/2026/WD-epub-anno-10-20260521/>
- EPUB Annotations publication history, review entrypoint only: <https://www.w3.org/standards/history/epub-anno-10/>

The EPUB document is a Working Draft, not a Recommendation. Its JSON Schema and privacy/security sections are incomplete, so `annotation-pack.schema.json` is explicitly a Second Reader profile schema. Pack metadata says `sr:conformance = "aligned"`, never `conformant`.

The project profile intentionally narrows two draft-era localization shapes: publication title/creator and annotation creator names are simple strings, and Note bodies use the stable Web Annotation sibling `language` field rather than the EPUB draft's localizable `value` object example.

The detached artifact planned for the completed v0 follows the pinned draft's ZIP shape: media type `application/zip;profile="https://www.w3.org/TR/epub-anno-10/"` and one root `annotations.json`. Reproducible ZIP bytes are a Second Reader project rule, not a W3C requirement.

The stable Web Annotation context IRI accepted in Pack documents is `https://www.w3.org/ns/epub-anno.jsonld`. Validators use a committed allowlist and do not dereference it while validating.
