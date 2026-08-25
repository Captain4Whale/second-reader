# Recent Real Agent Artifact vs Annotation Pack Responsibility Contract

Status: completed artifact-specific audit; input rejected before export.

Date: `2026-08-25`

Authority: [`contract/annotation-pack/v0/README.md#producer-neutral-information-responsibility`](../../../contract/annotation-pack/v0/README.md#producer-neutral-information-responsibility)

## Outcome

The most recent completed real product Agent artifact does **not** satisfy the producer-neutral Annotation Pack handoff and cannot be safely exported as minimal v0.

This is a completed negative validation result, not an implementation blocker and not evidence that the responsibility contract is too strict. The artifact predates the current native handoff: its ledger is `attentional_v2-phase8`, its annotation intent is expressed through compatibility categories, and its persisted `BookDocument` no longer passes exact-EPUB coherence against the current deterministic parser/indexer.

No Agent was rerun. No Tiny Reader data was substituted. The exporter was not invoked after the input gates failed, and no Annotation Pack revision or package was created.

## Artifact selection

The selection rule was: inspect product `reaction_records.json` ledgers under `reading-companion-backend/output/`, exclude non-completed runs, and choose the completed run with the newest runtime settlement timestamp.

| Candidate | Run state | Runtime updated | Ledger updated | Records | Selection |
| --- | --- | --- | --- | ---: | --- |
| `output/悉达多` | `completed` | `2026-04-08T23:37:12.620303Z` | `2026-04-08T23:37:12.584087Z` | 63 | selected |
| `output/纳瓦尔宝典硅谷投资人纳瓦尔十年人生智慧教你如何获得财富与幸福新时代创业者的穷查理宝典` | `completed` | `2026-04-08T20:20:45.468075Z` | `2026-04-08T20:20:09.430204Z` | 54 | older completed run |
| `output/women-and-economics` | `paused` | `2026-04-09T15:58:22.330162Z` | `2026-03-24T14:09:38.045501Z` | 0 | excluded: not completed |

Selected evidence:

- exact source: `reading-companion-backend/output/悉达多/_assets/source.epub`
- shared parsed substrate: `reading-companion-backend/output/悉达多/public/book_document.json`
- settled producer ledger: `reading-companion-backend/output/悉达多/_mechanisms/attentional_v2/runtime/reaction_records.json`
- run state: `reading-companion-backend/output/悉达多/_runtime/run_state.json`

Annotation text and Note bodies were not copied into this report. Only structural counts, safe error codes, coordinates, timestamps, and publication hashes were inspected or retained.

## Responsibility-by-responsibility result

| Required responsibility | Result | Evidence |
| --- | --- | --- |
| Exact EPUB bytes and file identity | **pass** | The source is a strictly readable EPUB of `190814` bytes. SHA-256 is `f239921773ac5abc86527fb78379cbd68cdf2cb901d253e085b2883180984a4f`, yielding the correctly shaped exact-file identity `nih:sha-256;f239921773ac5abc86527fb78379cbd68cdf2cb901d253e085b2883180984a4f`. |
| Source metadata and manifest | **pass** | OPF verification resolved usable publication metadata, `31` manifest items, and `22` spine items without asking the Agent to supply these facts. |
| Coherent `BookDocument` to exact EPUB resource text | **fail** | `PublicationIdentityBuilder` fails closed with `publication_substrate_mismatch` at `/chapters/2/paragraphs`. All `16` chapter identities align, but current reparse paragraph projections differ in seven chapters; three have paragraph-count differences. The exact-resource index marks all `22` text-resource hrefs unverifiable, so no current resource-wide TextPosition stream is available for these anchors. |
| Neutral `kind` | **fail** | None of the `63` records has `marginalia_kind`. The legacy `type` distribution is `discern=36`, `highlight=15`, `retrospect=12`; the generic exporter is forbidden to infer current Highlight/Note intent from that compatibility taxonomy. |
| Exact neutral `source_range` | **fail** | None of the records has `primary_source_ref`, `source_span`, or unique exact-resolution evidence. All `63` historical locators point to existing paragraphs and valid ranges in the persisted `BookDocument`, but that old substrate is not coherent with the exact EPUB under the current verifier and therefore cannot be promoted to a Pack range. |
| Exact neutral `source_quote` | **fail** | All `63` historical anchors have non-empty quotes. Against the old persisted paragraph ranges, `42` equal the locator slice and `21` are contained within a broader locator slice. None has the current top-level exact quote/SourceRef contract, and zero can complete current exact EPUB resource-text round-trip because all target resources are unverifiable. |
| Conditional Note body / bodyless Highlight | **fail** | All `63` legacy records carry non-empty `thought`. The `48` non-highlight rows have no authoritative mapping to Note, while all `15` rows named `highlight` also carry a thought; the adapter may neither silently discard those thoughts nor publish them as Highlight bodies. |
| Settlement `created_at` | **pass** | All `63` values parse as valid UTC timestamps. |
| Semantic duplicate rejection input | **pass on historical keys only** | No duplicate group was found using the historical type, href, paragraph range, and thought tuple. This does not cure the missing neutral intent or failed source coherence. |
| Current producer adapter | **fail as designed** | Read-only adapter loading rejects the envelope with `reaction_ledger_schema_unsupported` because it is `schema_version=1`, `attentional_v2-phase8`, not the supported current native `attentional_v2-phase9` shape. |
| Pack derivation and detached packaging | **not run** | Source coherence and neutral annotation intent are prerequisite gates. Running the exporter after those failures would not be valid acceptance evidence. |

## Historical-anchor detail

The old output is not empty or ungrounded. Every record has a non-empty historical quote, a locator object, matching persisted paragraph href, valid paragraph-local range, and existing start/end sentence IDs. That makes it useful migration evidence.

It still is not the responsibility contract:

1. a historical locator may identify a sentence or a broader paragraph slice without stating the exact selected annotation range;
2. compatibility `type` plus `thought` does not state the current Highlight/Note and body decision;
3. coordinates relative to a non-coherent `BookDocument` cannot be asserted against the hashed EPUB;
4. phase8 contains no unique exact-match resolution record that the current adapter can verify instead of guessing.

This distinction is why the contract keeps Agent intent small but explicit: `kind`, exact span, exact quote, conditional Note text, and settlement time.

## Disposition and next proof

- Keep the strict current adapter unchanged. Do not add phase8 inference or compatibility behavior to minimal v0.
- Keep the Annotation Pack completion claim unchanged: Tiny Reader proves the current-format producer pipeline, not prior whole-book conversion.
- The next positive real-book proof should use a completed current-native Agent artifact whose `BookDocument` is rebuilt from and coherent with its retained exact EPUB, then run the real exporter and independent validate/inspect path.
- If this specific historical book must be preserved without rerunning the Agent, authorize a separate bounded migration task. It must explicitly decide legacy kind/body semantics and re-resolve every quote against the exact EPUB; it must not weaken `SecondReaderProducerAdapter` or silently classify ambiguous rows.

No decision-log entry is added: this audit applies `DEC-157` and confirms the already-approved phase8 rejection boundary; it does not change product direction, protocol semantics, mechanism behavior, or public integration.

## Verification

- Read-only exact EPUB, substrate, ledger, timestamp, legacy-anchor, and adapter probes completed against the selected output. They emitted aggregate counts and safe codes only.
- `make annotation-pack-contract-check`: exit `0`; generated artifacts and Pages projection current; `55 passed`.
- `make agent-check`: exit `0`; Annotation Pack, API/frontend contract, mechanism appendix, OpenAPI, and frontend checks pass. Existing warning-only task-traceability and duplicate-decision observations remain unrelated baseline items.
- `git diff --check`: pass.
