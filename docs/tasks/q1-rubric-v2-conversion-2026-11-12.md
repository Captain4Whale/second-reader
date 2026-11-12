# Q1 rubric v2 publication and DIAG-001 conversion

Status: done, 2026-11-12. Based on `3018d23`; isolated branch `codex/q1-rubric-v2`; no push.

## Scope and provenance

Published the owner's exact rubric bytes as q1-v2, with 22 examples (A1 7 / B 15 / R 0), release and frozen registrations. No v2 form. All 15 adjudication IDs uniquely match the evidence bodies. Examples match the converted final judgments; edited example reasons are not required to match historical reason strings.

N1/H1 uses q1-v1 wording and the owner's adjudications, then deterministic conversion into v2 structure. This is not per-item annotation under q1-v2. N2/N3 failures become vetoes, N4 failure becomes an anchor tag, the exact uncovered reason 尾巴：阅读理解 becomes an empty-talk tag, and existing tags/verification flags are copied. H2/H3 failures become vetoes. Note passes iff N1 passes with no veto; Highlight passes iff H1 passes with no veto. Clean Note passes also exclude empty-talk and redundancy. The new uncertainty field remains null because it was not collected.

The 81-row source snapshot is `259a4c704174478003457a46b4ceb27d7ecb8c726e1ae3d842ebbcfb2fe5c1db`. Raw owner evidence is preserved at SHA-256 `2fdca04d07470fe91abf024b9cf591ead669038e80735c5fb2202dc120914aaa`. Derived records bind source revision/session, field rules, evidence item and final adjudication text without creating new annotation revisions.

Two append-only scores: `Q1-SCORE-DIAG-Q1V1-S001` (previously unregistered original completed v1) and `Q1-SCORE-DIAG-Q1V2-CONVERTED-S001` (converted). Both record comparison limits: same 81 products, repeated owner exposure and prior group reveal. The source journal remains the real v1 snapshot. Two append-only experiment rows register publication and conversion facts/numbers; no conclusions. INDEX displays the conversion basis, no-form identity, clean rate and veto/tag counts.

## Results and pending owner input

All requested checks match: Note 25/51, N1 fail 25, spoiler 1, empty-talk 2, anchor issues 2, Highlight 28/30. Clean Note pass is 21/51. A1 Note 3/21, clean 2/21, H 10/10; B Note 22/30, clean 19/30, H 18/20. Sapiens Note 10/25, clean 10/25, H 18/20; Bovary Note 15/26, clean 11/26, H 10/10.

Private evidence is in the main workspace's ignored `reading-companion-backend/state/scorings/q1-v2-final-20261112/`, exposed in this worktree through an ignored state link. `summary.md` and `v2-scoring-report.json` contain full group/book tables; `conversion.json` contains the 81 derived records. `adjudication.md` retains raw evidence. `failure-types-to-fill.md` and `.json` contain 25 anonymous N1 failures: 10 prefilled from explicit rubric examples / exact v1 reasons, 15 blank. The owner fills the worksheet and requests import in a separate task; pending values are not imported or inferred here.

## Validation

38 targeted Python tests passed for conversion, scoring, review and INDEX. Scoring evidence mode revalidated all five receipts and reproduced the converted records against the frozen v1 snapshot and raw adjudication. Experiment provenance validates 12 records against trusted base `3018d23`. Immutable-source hashes and both old JSONL prefixes are checked separately. `make agent-check` passed, including 55 Annotation Pack tests and frontend/OpenAPI contracts, with 369 traceability warnings for historical missing evidence paths / duplicate decision identifiers. See private `validation.json` and `agent-check.log` for final results.

No existing annotation or published v0/v1 file was changed; the main workspace's pre-existing q1-v0 edit remains untouched. No prompt, mechanism, annotator or model changes. Raw text stays under the already ignored scoring territory, so no new ignore rule is needed. No new decision-log entry: this implements the owner's supplied publication and conversion rules without changing mechanism/product direction; DEC-162 and historical scoring records remain byte-identical. No new model/eval job or run-ledger entry was created. README commands and public API/runtime contracts remain unchanged.
