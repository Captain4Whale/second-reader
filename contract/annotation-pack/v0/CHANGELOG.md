# Changelog

## 0.1.0 - 2026-08-23

- established the canonical Draft 2020-12 Pack wire schema
- froze `sr-canonical-json-v1` to interoperable safe integers and explicit UTF-8 string escaping; floating-point values are rejected
- established non-wire publication pointer and validation report schemas
- required every non-null detached-package digest in a validation report to be paired with the exact annotations JSON digest
- fixed the project-controlled GitHub Pages namespace and schema IRIs
- pinned the 2017 Web Annotation Recommendation and 2026-05-21 EPUB Annotations Working Draft
- added schema-valid Highlight, Note, and minimal Pack examples
- added generated Pydantic bindings and offline drift checks
