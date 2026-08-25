# Changelog

## Producer responsibility clarification - 2026-08-25

- recorded the mechanism-neutral `AnnotationDraft` handoff and separated source-publication facts, annotation intent, runtime settlement facts, and exporter-derived wire data under `DEC-157`
- clarified that `attentional_v2-phase9` is one current private adapter binding, not a Pack version or a requirement that future mechanisms must imitate
- made no public wire, schema, deterministic identity, package, or compatibility change

## 0.1.0 minimal reset - 2026-08-25

- directly replaced the unpublished heavy v0 wire under `DEC-156`; no old-wire compatibility or migration surface was retained
- reduced the public Pack to strict Web Annotation and Dublin Core terms with a single W3C EPUB context string and zero custom Second Reader fields
- replaced Work/Edition/File identity with one RFC 6920 `nih:sha-256;<hex>` exact-EPUB identifier
- replaced paragraph-local and chapter/fingerprint anchor objects with ordered `TextQuoteSelector` plus resource-wide `TextPositionSelector`
- removed per-item creator, private kind, target type, CFI, track, provenance, semantic digest, profile/version objects, and body format/language
- removed the custom JSON-LD context and namespace publication surface while retaining the approved schema IRI
- retained non-wire pointer/report schemas, detached single-root packaging, canonical JSON, immutable publication, recovery, and security boundaries

## Superseded unpublished implementation - 2026-08-23

The first local `0.1.0` implementation established the canonical schema/tooling, generated bindings, pointer/report companions, Pages projection, examples, and detached package profile. It also exposed a heavier custom Work/Edition/File/Track/anchor/provenance model. That wire was never published and is historical only; the minimal reset above is the sole v0 authority.
