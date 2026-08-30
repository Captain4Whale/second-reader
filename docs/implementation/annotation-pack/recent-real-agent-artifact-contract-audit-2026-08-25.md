# Recent Real Agent Artifact vs Annotation Pack Responsibility Contract

Status: corrected completed audit; current Agent semantics substantially pass, but the eval artifact is not directly exportable.

Date: `2026-08-25`

Authority: [`contract/annotation-pack/v0/README.md#producer-neutral-information-responsibility`](../../../contract/annotation-pack/v0/README.md#producer-neutral-information-responsibility)

## Correction

The first version of this audit selected `reading-companion-backend/output/悉达多`, an April `attentional_v2-phase8` product output, because its search was incorrectly limited to top-level `output/` ledgers. That was not the most recent real Agent artifact and made the resulting mechanism-level conclusion wrong.

The current mechanism and the most recent completed current-native run **do explicitly distinguish Highlight from Note**. The latest usable evidence is the July 5 `attentional_v2-phase9` Xidaduo full-window continuation under `eval/runs/`. It contains `112` settled records: `83` bodyless Highlights and `29` Notes with non-empty bodies.

This corrected audit supersedes the earlier negative conclusion. The April phase8 output remains relevant only as historical migration evidence.

## Correct artifact selection

The corrected selection enumerated `reaction_records.json` across the backend, including ignored evaluation/runtime artifacts rather than only tracked product outputs. It found `383` parseable ledgers, `289` non-empty ledgers, and `23` non-empty current-explicit-kind ledgers. Apart from the Tiny Reader fixture, the current-explicit-kind artifacts are July evaluation runtimes; there is no current-native, exact-EPUB-co-located, terminal whole-book product output.

The best recent real current-native candidate is:

- run: `digest_marginalia_v24_xidaduo_fullwindow_continue2_20260705`
- segment: `xidaduo_private_zh__segment_1`
- evidence status: evaluation `completed/pass`, real provider trace present, `chapter_end` reached
- coverage: original parsed chapters `3` through `14`, from `婆罗门之子` through `唵`
- limitation: this is one completed evaluation segment, not all chapters of the original EPUB and not a terminal product output

The run ledger records `19` newly accepted units and `34` new Marginalia; its cumulative runtime carries `64` units and `112` settled records after the parent and two continuations. The evaluation status is complete, but the copied runtime shell/run-state remains stale as `running/deep_reading`. The production exporter therefore rejects this directory with `run_state_not_exportable` before attempting publication identity.

Primary evidence:

- evaluation record: `reading-companion-backend/docs/evaluation/run_ledger.md`
- phase9 ledger: `reading-companion-backend/eval/runs/attentional_v2/digest_marginalia_v24_xidaduo_fullwindow_continue2_20260705/analysis/digest_marginalia_v24_xidaduo_fullwindow_continue2/runtime/xidaduo_private_zh__segment_1/_mechanisms/attentional_v2/runtime/reaction_records.json`
- segment BookDocument: the sibling `public/book_document.json`
- exact source EPUB: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260629_source_norm_v1_2_unique_notes/fresh_parse_outputs/xidaduo_private_zh/_assets/source.epub`
- exact-source BookDocument: the sibling `public/book_document.json`

Annotation text and Note bodies were not copied into this report. Only structural counts, safe error codes, coordinates, timestamps, hashes, and aggregate round-trip results were retained.

## Responsibility-by-responsibility result

| Required responsibility | Corrected result | Evidence |
| --- | --- | --- |
| Neutral Highlight/Note intent | **pass: 112/112** | `83` records carry `marginalia_kind=highlight`; all `83` have empty `thought`. `29` carry `marginalia_kind=note`; all `29` have non-empty `thought`. |
| Conditional body shape | **pass: 112/112** | Current tool schema, validator, settlement, and adapter all preserve the same rule: Highlight has no public body; Note has one non-empty body. |
| Exact quote and selected range on the read surface | **pass: 112/112** | Every stored range is in bounds and its segment `BookDocument` slice equals both `source_quote` and `primary_source_ref.quote`. All ranges are same-paragraph ranges. |
| Unique semantic source selection | **pass: 111/112; one unresolved** | `111` refs are `matched/exact_text/match_count=1`. Record index `44` has a five-code-point quote occurring twice in its source unit; runtime selected the first occurrence and honestly stored `ambiguous_first_match/match_count=2`. Its coordinate slice is exact, but the intended occurrence is not independently proven. |
| Settlement timestamp | **pass: 112/112** | Every `created_at` parses as UTC. |
| Semantic duplicate input | **pass** | No duplicate group exists under kind, mapped source range, and Note-body semantics. |
| Current producer adapter | **pass: 111 drafts; one row finding** | The real adapter accepts `83` Highlights and `28` Notes. Its sole finding is `ambiguous_source_quote` at `/records/44`; this is a row-level source-intent issue, not a kind/body failure. |
| Exact EPUB bytes and identity | **pass through dataset provenance; not co-located** | The retained EPUB is `190814` bytes with SHA-256 `f239921773ac5abc86527fb78379cbd68cdf2cb901d253e085b2883180984a4f`. The same bytes are in the source library and older product output. The July eval runtime itself does not contain `_assets/source.epub`. |
| Exact-source metadata and `BookDocument` coherence | **pass for the source artifact** | The fresh-parse full `BookDocument` has `16` chapters and `590` paragraphs and passes current strict `PublicationIdentityBuilder` substrate comparison against the exact EPUB. The one-chapter/`511`-paragraph eval `BookDocument` is a TXT segment projection and must not be supplied directly as that EPUB's substrate. |
| Segment range to exact EPUB range | **reconstructible, but not persisted as an export input** | Replaying the versioned dataset renderer reproduces the segment bytes exactly. `499` source-derived segment paragraphs map to the full `BookDocument`; `12` are inserted chapter-title rows. All `112` annotation ranges deterministically map to one original chapter/paragraph/href and round-trip to the exact EPUB text in the safe parser trial. The eval artifact did not persist this map, so the generic adapter/exporter must not guess it. |
| Exact EPUB resource-text index | **pass after committed safe-DOCTYPE repair** | The resource parser now accepts exactly one simple HTML5 `<!DOCTYPE html>` in the resource prolog and continues to reject `ENTITY`, internal subsets, `SYSTEM`, `PUBLIC`, duplicate/misplaced declarations, malformed XML, and hostile resources. The retained exact EPUB produces `22` resource streams, all `590` paragraph ranges, and zero unverifiable hrefs. |
| EPUB-backed anchor resolution | **positive dry-run for the 111 accepted drafts** | After deterministic coordinate remap, the real `AnchorBuilder` resolves all `111` adapter-accepted drafts with exact quote/position round-trip and no findings. The parser portion now uses committed production code; coordinate remap remains diagnostic evidence rather than a committed historical migration or published Pack. |
| Pack derivation and detached packaging | **not run for this historical segment** | The real exporter first fails the stale run-state gate. A historical migration would still need a persisted/audited coordinate bridge, co-located EPUB, honest terminal state, and an explicit skip or resolution policy for record `44`. Current/new Reading Product output does not need this migration. |

## Why the first point now passes

The distinction is explicit at every current phase9 layer:

1. `src/attentional_v2/llm_output_tools.py` requires `kind` to be `highlight` or `note` in the Digest result tool.
2. `validate_digest_result` requires Highlight content to be empty and Note content to be non-empty.
3. `src/attentional_v2/slow_cycle.py` persists `kind` as authoritative `marginalia_kind`, content as `thought`, and the settlement timestamp as `created_at`.
4. `src/annotation_pack/producers/second_reader.py` uses `marginalia_kind`, not compatibility `type`, and maps bodyless Highlight versus body-bearing Note into neutral drafts.

The compatibility `type` field is not authoritative: a current Note may retain `type=association` for older consumers while still carrying `marginalia_kind=note`. Reading `type` as the Pack kind was one cause of the earlier mistaken interpretation.

## Implemented follow-through

### 1. Repair the safe EPUB resource parser — completed

The blanket content-resource doctype rejection in `src/annotation_pack/epub_resources.py` is replaced by a narrow rule that accepts only one simple HTML5 `<!DOCTYPE html>` declaration in the initial resource prolog. `ENTITY`, internal subsets, `SYSTEM`, `PUBLIC`, wrong names, duplicates/misplacement, malformed XML, oversized trees, and hostile ZIP cases remain fail-closed. Container and OPF XML retain their original blanket DTD prohibition.

Committed positive/negative coverage passes, and the retained Xidaduo EPUB yields `22` resource texts, `590` paragraph ranges, zero unverifiable hrefs, with exact SHA-256 `f239921773ac5abc86527fb78379cbd68cdf2cb901d253e085b2883180984a4f`.

## Historical migration work intentionally not taken

### 2. Make evaluation source provenance exportable

Persist a versioned `segment -> canonical BookDocument` coordinate map when the dataset is rendered. Bind it to the source EPUB SHA-256, full `BookDocument` digest, segment-text hash, renderer version, and source chapter/sentence bounds. The eval runner should retain that reference and the exact EPUB rather than emitting an EPUB-shaped manifest for a TXT-only runtime.

For this historical artifact, perform the same remap only in an isolated staging copy, verify all hashes and monotonic paragraph mappings, and write a remapped phase9 ledger against the full `BookDocument`. Do not add segment inference to the generic adapter.

### 3. Resolve record `44` without pretending first-match is unique

Preferred: rerun or re-settle only its source unit and require a longer unique quote. Acceptable for a one-off proof: inspect the two contexts and explicitly choose the intended occurrence, then update the coordinate and resolution evidence in the staging copy. If completeness is not required, use the existing explicit skip policy and export the other `111` records while reporting one skipped error.

Do not merely change `ambiguous_first_match` to `matched`: the stored first occurrence is technically valid, but the run contains no independent evidence that it is the model's intended occurrence.

### 4. Finalize evaluation runtime state

When an eval segment reaches `chapter_end`, finalize its export-facing `run_state` instead of leaving copied state as `deep_reading` and runtime shell as `running`. Also stop unconditionally advertising `_assets/source.epub` for TXT-backed eval artifacts.

### 5. Run the actual Pack proof at the right scope

After steps 1–4, run adapter -> remap -> publication identity -> anchor -> builder -> validate -> detached package -> independent inspect. There are two honest acceptance targets:

- `111`-item proof with record `44` explicitly skipped and reported;
- `112`-item proof after record `44` is explicitly resolved.

Neither target proves a current whole-book Agent-to-Pack route because this run covers source chapters `3–14`, not the entire EPUB. A whole-book claim still requires a current-native product run over the exact EPUB with canonical coordinates retained from the start.

## Historical phase8 appendix

The April `output/悉达多` artifact is genuinely phase8 and is correctly rejected by the strict current adapter. It predates the explicit parallel Highlight/Note contract introduced in July, so its compatibility categories and non-empty thoughts cannot be treated as current kinds without an explicit migration policy.

Its source EPUB is not corrupt. It has the same exact SHA-256 as the fresh-parse source. Its old persisted `BookDocument` differs because parser/source-normalization behavior changed. The former `22` resource failures were caused only by the now-fixed blanket-doctype gate; that parser defect no longer applies. The remaining substrate difference still makes this historical migration material, not evidence that the current Agent lacks required output.

## Verification

- Current producer-adapter and source-span focused tests: `83 passed`.
- Read-only current adapter invocation: `112` input, `111` accepted, one `ambiguous_source_quote` finding.
- Read-only segment quote/range audit: `112/112` exact round-trip, `112/112` valid UTC, zero semantic duplicates.
- Read-only dataset renderer replay: byte-identical segment source and deterministic original-source mapping for all `112` annotation ranges.
- Current strict source identity and committed resource parser: exact EPUB/full `BookDocument` coherence passes with `22` resource texts, `590` paragraph ranges, and zero unverifiable hrefs.
- Safe-DOCTYPE focused source/resource tests: `246 passed`; complete Annotation Pack suite: `804 passed`.
- Remapped real AnchorBuilder trial: `111/111` accepted drafts resolve exactly with no findings.
- `make annotation-pack-contract-check`: exit `0`; `55` contract tests pass and generated/Page-projection bytes are current.
- `make agent-check`: exit `0`; only the separately recorded historical task-traceability and duplicate-decision warnings remain.

The follow-through changes only the production XHTML resource declaration gate and its tests/docs. No Agent was rerun, no historical product was migrated, and no Annotation Pack revision or package was published from this eval artifact.

No decision-log entry is added: this correction fixes artifact selection and factual classification. It does not change the producer-neutral contract, public wire, default mechanism, or approved compatibility boundary.
