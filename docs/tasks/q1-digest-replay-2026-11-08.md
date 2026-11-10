# Fixed-history Digest rerun diagnostic

Status: A1/B blind annotation revealed; waiting for owner review of the report and next experiment decision, 2026-11-08. Earlier sections below are chronological checkpoints.
Branch: `codex/q1-digest-replay`, base `b5fa38c` (comparison import contract present).

## Authorized scope

Build an isolated run-id/unit-id Digest rerunner, freeze original source and selected
historical Understanding lines, then run A1/A2 (`gpt-6-luna`, medium) and B
(`gpt-6-sol`, high) over the owner's 16 selected dev units. Use original Digest v24.
Do not modify the annotator or comparison implementation. Package A1/B through the
existing importer, with A2 reserved for repeatability reporting. No push.

The registered hypothesis is "Note 质量差主要来自 prompt 而非模型能力". The baseline
is `Q1-BASELINE-001`, original full-book runs plus first-batch open-coding journals.
This design holds the prompt fixed and changes model plus reasoning effort as a
configuration bundle. It does not alone isolate a prompt effect or model-only effect.

## Implemented first slice

- `eval/attentional_v2/fixed_history_digest.py`: read-only SQLite/artifact reader,
  accepted-attempt selection, ordered historical memory reconstruction, exact last
  manifest check, isolated Digest helper with raw request/response capture and usage.
  No Ingest, retrieval, Runner or settlement entrypoint. Results are reconstructed.
- `scripts/rerun_fixed_history_digest.py`: single-unit CLI; `--prepare-only` avoids
  model calls. Source inputs are external read-only paths; outputs are restricted to
  ignored local backend `state/`.
- `llm_calls.py`: only optional Digest prompt selection; default behavior retained.
  Published text/dependencies are verified by the separate prompt selection helper.
- Tests: accepted-attempt/time ordering, historical memory conflict/future rejection,
  source drift rejection, default selected prompt byte equivalence and unknown version.

The invocation helper completed the A1 pilot and the subsequent authorized 16-unit
A1 continuation below. A1's comparison report is complete. A2, B and the mixed blind
batch have not been run/created; A2/B require another owner confirmation.

## Fail-stop evidence

Both final-unit checks pass against the historical manifests: Bovary `u000352` and
Sapiens `u000245`, full system/user strings equal. First selected-unit reconstruction
(`q1_full_bovary_d414030_20261103 / u000006`) then fails `Unit source mismatch`.
Per the owner's explicit "任何单元重建失败就停下来告诉我，不要跳过", no target was
skipped and no LLM call was launched. No source Product, cursor, memory or annotations
were changed. Tokens consumed: 0; diagnostic generation cost: 0.

Read-only diagnosis found identical source span ID `src:c7:p38@0-p42@97` and identical
canonical chapter/paragraph/offset coordinates. The rejected difference is the
decorative `chapter_ref`: Unit Memory says `Chapter 1`, unit span ledger says `第1章`.
The first implementation compared the entire cursor dictionaries, so it also rejected
this display-label difference. This is an overly strict tool check, not established
source-coordinate corruption or evidence that the historical text is missing.

The owner subsequently authorized this exact canonical-coordinate repair, historical
artifact linking and only the `u000006` A1 pilot. The original stop artifacts remain
unchanged. No other generation was authorized in that follow-up.

Private evidence (this worktree's backend):
`state/experiments/q1_digest_fixed_history_20261108/reconstruction-failed.json` and
`state/experiments/q1_digest_fixed_history_20261108/manifest-checks.json`.

Verification before commit: reconstruction/prompt and existing Digest call tests
(42 passed), immutable prompt release check (3 releases), iteration provenance check
(2 experiments). The mandatory whole run-ledger check was run but fails because the
new worktree does not contain the historical ignored evaluation artifacts referenced
by old entries. No historical entries or allow-missing lists were changed to hide
that limitation; the new ledger entry independently validates with zero errors.
Backend/frontend contracts and OpenAPI checks passed. Full agent traceability still
fails on historical ignored-artifact references absent from this worktree. Local
Python/frontend dependency links and an empty local job-registry summary were
provisioned to resolve new-worktree setup blockers; no background job was launched.
No live model, blind-batch, or semantic-quality
verification claimed. No history decision update: this is a bounded offline tool
prototype, not a mechanism or product direction change.

## Follow-up: label lineage and prompt fidelity

Historical authority is commit `d414030c149bc56590bed890421eb59aad22aa05`:

- `source_spans._chapter_ref` uses chapter `reference`, then `title`; the parsed
  BookDocument chapter ID 7 has title `第1章`, chapter number 1, no `reference`.
  Thus the originally selected source cursors retain `第1章`.
- `runner._chapter_ref` delegates to `reading_runtime.sequential_state.chapter_reference`,
  which uses chapter number 1 to produce `Chapter 1`. This labels the audit and
  span ledger's top-level `chapter_ref` even in the original transaction.
- Resume's `_reconcile_unit_memory_from_reading_product` calls
  `_source_unit_for_product_unit`, re-creating cursors with the runtime reference
  `Chapter 1` and rewriting the derived Unit Memory row. For this unit the row's
  timestamp is `2026-11-03T22:50:29.503790Z`, versus original span-ledger settlement
  `2026-11-03T12:34:28.105122Z`. This explains the later cursor-label difference.
- `_run_digest_for_source_unit` passes `chapter_title=chapter["title"]` to Digest.
  `render_digest_prompt_xml` uses it for `ReadingPosition.chapter_title` and
  `human_position`; its SourceUnit renderer reads paragraph text/indices, not cursor
  `chapter_ref`. The system prompt has no chapter-label slot. The correct dynamic
  title is therefore **`第1章`**, with human position **`第1章, p38-p42`**.

Full last-unit system/user checks still pass for both books. A test mutates both
cursor labels while keeping coordinates/title fixed and verifies identical system
and user text; changing `chapter_title` does change the user text. Historical raw
source files used for this diagnosis are preserved privately beside preflight
evidence. The target historical request itself was not recorded, so this remains
reconstructed input, not a newly invented original request receipt.

## Read-only historical evidence and full checks

Mounted the original ignored artifact paths using symlinks without shadowing tracked
files or adding missing-evidence waivers. Added 244 initial artifact links and 279
job-record links; the connection manifest is private. New outputs, provider
quota/dispatch state and job records are local. The default job wrapper briefly
created this task's new log through a historical log-directory link; that new log
was moved back into a local writable `logs/` directory, and the old link was renamed
`historical-logs/`. No pre-existing historical log was changed or moved.

The ledger Markdown renderer now preserves checkout-local symlink aliases, while
artifact validation still follows the links and checks their existence. This avoids
unrelated rewrites of 99 historical ledger links; a regression test covers it.

Full `update_evaluation_run_ledger.py --check` passes. Full `make agent-check` passes,
including actual backend/frontend contract, OpenAPI and traceability execution.
Traceability reports the exact same 17 warnings as the original workspace (old
acceptance references, old missing source files/job references and duplicate decision
IDs); no new warnings were introduced and none were suppressed. Final checks: 50 focused reconstruction/prompt/Digest/ledger tests, two gateway
observation/usage tests, three immutable prompt releases and iteration provenance
validation pass. The contract phase also passes its 55 tests.

## Single authorized A1 pilot

- Run: `q1_digest_fixed_history_20261108_A1`, status `review_pending`.
- Registered job: `bgjob_q1_digest_fixed_history_20261108_A1_pilot`, completed.
- Original unit: `q1_full_bovary_d414030_20261103 / u000006`.
- Original accepted call: `067505ae2b2b427ebfda65f562658437`.
- Source: `src:c7:p38@0-p42@97`, canonical chapter ID 7, paragraph 38 offset 0
  through paragraph 42 offset 97 (half-open), 677 characters / 5 paragraph slices.
- Frozen memory order (all hot; no retrieved entries): `recent:c7:u0005:m1`,
  `recent:c7:u0004:m1`, `recent:c7:u0003:m1`, `recent:c7:u0002:m1`.
- Prompt: original `attentional_v2.digest.v24`, release SHA-256
  `b20654a196efd6d83e6e8411f580c9bb119054878e6de74b8575ccfc3a33571e`.
- Effective model/config: `gpt-6-luna`, medium reasoning, temperature 0.2, output
  limit 4096, matching the original unit's sampling receipt.
- One logical/physical request, about 10.708 seconds. Result: **0 Highlights /
  1 Note**, H:N **0:1** (0% / 100%). Its exact quote resolves at chapter ID 7,
  paragraph 42 offsets 56–97. No semantic-quality conclusion is made.
- Provider-reported usage: **9,224 input + 324 output = 9,548 total tokens**;
  zero reported cache-read/reasoning tokens. Actual billed cost is unknown.
- Actual request SHA-256:
  `d1c11d43dbe43e3112a6e761cfe81570ed7be503a6cb37e08b1deeb22712ca13`.
- Actual initial system/user exactly match the frozen preflight text. Before/after
  SHA-256 inventories confirm all **279 original output files** are byte-identical.
- Pilot code identity is `3e0fcb9` plus the invocation-captured dirty-workspace patch.
  The initial helper omitted an observation scope, so its standard trace lacks usage;
  the complete provider response retained the usage above. The immutable pilot
  result remains untouched; `pilot-summary.json` records normalized response usage
  and its source. The helper now saves response usage directly and adds the standard
  observation scope. No additional model call was used for that logging repair.

Private outputs: `state/experiments/q1_digest_fixed_history_20261108/pilot-summary.json`,
`pilot-preflight/`, and `A1/bovary/u000006/` (input, rendered prompt, actual request,
response, result and invocation provenance). The experiment log retains the requested
hypothesis and baseline linkage, with status `pilot_review_pending` and no pass rate.

The owner accepted the pilot and subsequently authorized **A1 only** over the full
registered 16-unit selection. The pilot is reused as this unit's A1 sample, never
regenerated to seek a different output. A2 and B remain confirmation-gated.

## A1-only continuation

State: all 16 A1 units completed; owner review pending. One approved pilot was
reused and 15 new requests were made. No A2/B calls were made.

`HistoricalRun.verify_memory_selection` now independently checks serialized input
against the chosen original trace's hot and retrieved IDs/order, the historical
stable descending `unit_index` merge, and each complete memory line derived from
the original audit Understanding. The per-unit check is saved with the result's
verification receipt. A mismatch stops before the affected call. The approved
pilot's original input and rendered prompt are checked under the same rule.

All 16 units passed preflight. No memory body matched the explicit chapter-label
scan (`Chapter N`/Roman numeral or `第…章/节/卷/部/篇`); regardless of scan results,
the full bodies are compared verbatim, including every possible label. Both books'
last-unit manifest checks pass. All 16 baseline audit mark lists and Unit source
ranges also match the hash-verified immutable Reading Products exactly.

The A1-only runner is `scripts/run_fixed_history_a1.py`; it freezes all inputs
before generation, runs serially, reuses existing matching outputs, validates exact
anchors and writes reports under ignored `state/experiments/q1_digest_fixed_history_20261108/A1-full/`.
Job `bgjob_q1_digest_fixed_history_20261108_A1_full` owns this continuation. The
pre-generation example selection is Bovary `u000006` and Sapiens `u000015`, the first
specified unit from each book. Side-by-side ordering does not assert semantic pairs.
No annotator/comparison implementation or original annotation journal is modified.

Per-unit comparisons use all Product-accepted historical marks and all generated
A1 marks, not just the first batch's sampled annotated marks. Note average length
uses stripped visible-body Unicode code points, including punctuation, excluding
quotes/private selection reasons. No Notes => null / `—`. Aggregate averages use
total body length divided by total Note count. Sentence-end and question-mark counts
are descriptive surface features, not a quality judgment or causal explanation.

### Completed A1 evidence

- Every unit's serialized input passes the original trace ID/order check before its
  model call, including the reused pilot. **105 memory-line occurrences** across
  the 16 inputs pass the complete-text audit check. No explicit chapter labels were
  detected by the documented scan; no text or label was rewritten.
- Both final-unit system/user manifest checks still pass. Every generated source
  quote has a unique exact anchor. All source output files retain their before-run
  SHA-256 values: **Bovary 279 + Sapiens 194 = 473 files**.
- Actual serialized system/user prompts, request hashes, effective sampling and
  provider-reported model are independently verified for all 16 A1 requests against
  the frozen preflight/original sampling receipts.
- Original: **34 marks, 9 H / 25 N**, total Note body length 2,323 characters,
  average **92.92**. A1: **31 marks, 10 H / 21 N**, total Note body length 1,868,
  average **88.95238095**. Counts and lengths were independently recomputed from
  immutable Product (original) and the actual provider tool-call payloads (A1).
- A1 total usage, including pilot: **156,855 input + 7,647 output = 164,502 tokens**.
  Continuation alone: **147,631 input + 7,323 output = 154,954 tokens**. There are
  16 logical/physical requests in total, one per unit, with no structural repair or
  failed attempt. Cache-read and reasoning-token usage were both reported as zero.
  Actual billed cost is unknown; no zero-cost or API-price estimate is asserted.
- Fixed side-by-side examples: Bovary `u000006`, Sapiens `u000015`, complete quote
  and Note body from both versions. The per-unit 16-row table also includes H/N
  and Note average length; the appendix counts sentence-end punctuation/questions.
  No human quality score, causal conclusion or hypothesis verdict is produced.
- Job `bgjob_q1_digest_fixed_history_20261108_A1_full` completed; run
  `q1_digest_fixed_history_20261108_A1` is `review_pending`. The experiment keeps
  the requested hypothesis and original-run/first-batch baseline, with A2/B
  explicitly `not_started`.

Private evidence under `state/experiments/q1_digest_fixed_history_20261108/A1-full/`:
`report.md`, `summary.json`, `validation-summary.json`, `baseline-product-checks.json`,
`request-fidelity-checks.json`, `preflight.json`, per-unit `preflight/` and `verification/`, and the before/after source
fingerprint inventories. Per-unit actual requests/responses remain under `../A1/`.
The generation ran at code `88bd98a` plus fully captured staged/unstaged invocation
patches. The report renderer was subsequently formatted without further model calls.

Final verification: 55 focused tests passed, three immutable prompt releases and
iteration provenance validated, full run-ledger check passed, and full agent-check
(including 55 contract tests and frontend/OpenAPI checks) passed. Its 17 traceability
warnings match the original workspace exactly; none were suppressed.

Next action: owner reviews A1. **Do not run A2 or B without confirmation.** No
annotator/comparison implementation changes or push. No decision-log update is
needed for a bounded mechanical check and descriptive comparison with no mechanism
or product direction change.

## Authorized A2/B continuation (2026-11-08)

This section supersedes the earlier confirmation gate: the owner authorized A2 and B,
then SHA-preserving integration and mixed A1/B packaging. Both groups completed all
16 units at clean `ca4e28c7964d3e28eaa77408fb0850d31a8ec867`, before any merge or tracked
edit. A2 uses gpt-6-luna/medium; B uses gpt-6-sol/high. Both retain v24, temperature
0.2 and max output 4096. The ignored `continuation/run_groups.py` orchestrated the
existing Digest entrypoint serially with fail-stop, without changing generation code;
its SHA-256 is recorded in `continuation/driver-receipt.json`. Job:
`bgjob_q1_digest_fixed_history_20261108_A2_B` (completed).

Each unit rechecked original trace memory IDs, each selection order, complete memory
body/labels, canonical source range and exact A1 system/user prompt. Both original
final-unit manifests still match. Actual requests, effective sampling, provider model
and clean code receipts were checked. All 473 original output files retain their
hashes. No Ingest, retrieval, settlement, memory application or Product write occurred.
Per-unit physical request counts and gateway `quota_retry_attempt_count` are retained
in each group's `*-full/summary.json` and detailed request traces; no outer retry hides
failed generations. Shared log/ledger writes happened only after both groups completed.

A2 versus A1 per-unit counts, H:N, Note mean lengths and anchor overlap are in
`reading-companion-backend/state/experiments/q1_digest_fixed_history_20261108/continuation/report.md`.
Anchor overlap is the intersection/union of unique canonical character positions
covered by either group's H/N anchors, without paragraph separators or type/body
comparison; both empty gives null. Synthetic checks cover duplicate anchors, partial
overlap, cross-paragraph ranges and empty input. No Note gives a null mean length.
B completed successfully: input 156,855, output 26,589, total 183,444 tokens (reasoning
usage is included in output, not added again). Its contents and mark statistics are
withheld. Actual billed cost remains unknown; no quality/causal conclusion is drawn.

`Q1-DIGEST-DIAG-001-CONTINUATION` is an append-only completion record linked to the
original diagnostic, not a rewritten A1 checkpoint. It supersedes that checkpoint's
pending A2/B statuses. Existing baseline and A1 lines retain every byte. The provenance
tests' obsolete single-JSON assumption was corrected to select the baseline by ID;
a regression check verifies append operations preserve the complete prior log prefix.
This is an evaluation workflow continuation, not a mechanism/product direction change;
no decision-log update is needed.

## SHA-preserving integration

A2/B completion was committed as `28069a9`. Main's three previously uncommitted
original pilot/full-book ledger rows were separately preserved as `9dbe361`.
The replay branch merges main without rewriting any historical SHA. Conflict
resolution keeps main's completed mixed-comparison status/annotator 2.0 and the
replay continuation. Ledgers are unioned by `run_id`; Markdown is regenerated.
The experiment log retains both main's and pre-continuation replay's exact byte
prefixes. Comparison/annotator implementation files are byte-identical to main.

Full verification: 1,811 backend tests passed, 14 annotator-storage tests passed,
three published prompt releases and the full iteration/journal provenance checks
passed, full ledger check passed, and `make agent-check` passed (55 contract tests).
Its 17 traceability warnings exactly match main. Initial backend failures exposed
missing local-only config and historical test inputs; read-only-use links were
added for the two Q1 run directories, chapter corpora, missing excerpt input files,
and local target/profile configuration. Test-only credential placeholders stayed
in process environment; no actual credentials were written. All failures passed
on recheck and on the subsequent full suite. Test generation left tracked fixtures
unchanged. Main receives read-only-use links to replay artifacts and its three
job records so post-fast-forward traceability can inspect actual evidence.
No annotation-hub work, rebase, deletion or push is part of integration.

Post-fast-forward check exposed checkout-dependent relative links for the four
replay ledger rows, whose index paths were absolute. Those ledger index paths now
use the same workspace-relative artifact alias available in both worktrees;
immutable generation receipts and existing experiment log bytes stay unchanged.
This keeps Markdown regeneration byte-stable in both checkouts.

## Frozen diagnostic subset and blind batch

`experiments/unit-sets/diag-001.json` is `fixed-unit-set/1`, purpose `dev`, containing
16 original JSON object text slices copied verbatim from `dev-v1`, in original
manifest order. Only the manifest header differs; existing dev/holdout rows and
frozen entries are untouched. `experiments/frozen.json` adds its file SHA-256.
The original experiment rows still name the parent dev set with their explicit
16-unit selection; the bundle records the exact diagnostic subset hash.

The offline producer `scripts/export_fixed_history_digest.py` converts existing
Digest results to `q1-digest-comparison-output/1`, verifies input/accepted request
identity, original coverage, canonical substrate and exact anchors, and preserves
complete group coverage including units with zero marks. It does not call a model
or import Ingest/retrieval/settlement. Group exports and exact source-document copies
are retained under `state/experiments/q1_digest_fixed_history_20261108/imports/`.
A1 links to the original diagnostic row; B links to its append-only continuation.

The existing importer was invoked with `--unit-set experiments/unit-sets/diag-001.json`,
the existing first-batch annotation root, both group exports, and output root
`state/experiments/q1_digest_fixed_history_20261108/blind-batch/`.
Bundle ID: `e03310c157a7b5df0561eb90bf1d579393b59f10cbc1d883636ef5c8327d5246`.
The bundle has **16 windows / 2 opaque groups / 81 mixed items / 0 unassigned**,
`synthetic=false`. A2 is excluded. Only `mixed.json` is intended for annotation;
`blind-key.json` and the separate `group-map.json` retain private mappings. A new
empty `judgments.jsonl` and `weijiang / open_coding` annotation context are present.
No historical judgment journal was edited.

Import validation checks both complete source documents, every exact anchor and
coverage range. Independent `load_bundle` checks manifest/projection/key hashes,
unique mixed ownership and exact projection fidelity. Explicit field allowlists
and a scan against private mappings confirm that mixed.json has no group/model,
experiment/run/unit/original mark/source IDs, request hashes or prompt version.
Do not run group-quality statistics or reveal before the owner completes blind review.
This task did not modify annotator, comparison importer, statistics or contract files.

Private packaging receipt: `reading-companion-backend/state/experiments/q1_digest_fixed_history_20261108/continuation/blind-batch-validation.json`.
Per-unit noise report: `reading-companion-backend/state/experiments/q1_digest_fixed_history_20261108/continuation/report.md`.
The hypothesis remains unadjudicated; descriptive counts/lengths/overlaps are not
quality or causal evidence. No further generation or push is authorized by packaging.

Packaging checks: 43 focused replay/provenance/comparison tests passed; complete
real A1/B exports passed the existing importer and independent bundle validator;
full `make agent-check`, immutable release/manifest/journal checks and ledger check
passed. The 16 raw JSON object slices were independently rechecked against dev-v1;
all prior frozen entries and experiment-log bytes remain unchanged. The historical
annotation-hub branch still points to `e323902`.

## Blind-review limitation: prior exposure

这 16 个单元的原运行输出已在第一批标注中看过，A1 与之相似，盲标可能被
“见过”感削弱。混合批次隐藏组别和来源元数据，但不能消除既有阅读记忆；
因此不能将本轮标注称为未接触过材料的完全盲评。此局限已同时记入追加的
`Q1-DIGEST-DIAG-001-CONTINUATION` 实验行，既有实验行和历史标注不改写。
这仅限定后续盲标的解释范围，不评价模型或 Note 好坏，不给假设下结论。

## Pre-annotation protocol and actual request-hash audit

At **2026-11-08 14:55:18 +08:00**, appended
`Q1-DIGEST-DIAG-001-PREREG-001` to `experiments/log.jsonl`, explicitly amending
`Q1-DIGEST-DIAG-001`. Existing bytes remain unchanged. The row preserves the owner's
Note/Highlight pass criteria and B-versus-A1 Note pass-rate thresholds verbatim,
uses `open_coding` with the first-batch criteria, and does not publish a rubric or
launch further generation/A2 annotation. Criteria authority is the appended log row.
The mixed batch's canonical `judgments.jsonl` was empty immediately before and after
append. The actual timestamp is retained without backdating; browser-local unsaved
work was not inspected, and no annotation-start timestamp is fabricated.

All **48 unit outputs (A1/A2/B: 16 each)** contain non-null `request_sha256` values.
Each was recomputed from the retained adapter request capture and matched against
gateway calls, provenance request indexes and the invocation sample; the accepted
provider response's Marginalia also match the saved result. These are actual new
provider-neutral logical request hashes over messages/tools/tool choice/expect_json,
not reconstructed historical input hashes, prompt release hashes or HTTP transport
byte hashes. Model and sampling remain separate recorded metadata.

All A1/B per-mark comparison export hashes and the private blind-key references
match their producing unit's request. Raw nested Marginalia inherit the parent
`result.json` request hash; A2 has no comparison export, so it has no separate per-mark
export field to inspect. No actual unit request hash is missing or synthesized.
All generation artifacts remain byte-identical. `mixed.json` intentionally omits
request hashes as part of its anonymous projection and is not a provenance receipt.

Private checks: `state/experiments/q1_digest_fixed_history_20261108/continuation/preregistration-001/`
contains `request-hash-audit.json` and `registration-receipt.json`. No quality judgment
or threshold decision was computed; the prior-exposure limitation remains in effect.


## Completed blind annotation and authorized reveal

At 2026-11-08T09:39:02.151226+00:00, appended the unique linked row
`Q1-DIGEST-DIAG-001-REVEAL-001`; the prior 13,118 log bytes remain identical.
The frozen 313-row / revision-313 journal (81/81 marks judged) has SHA-256
`28fff5eb3b0269d69c46d46b66f67f654dcc1ac6703e07edd4cbec4f627235b5`.
Statistics use `weijiang / open_coding`, latest revision per record, with an
independent recomputation. Annotation starts after the preregistration timestamp.

Read-only version audit: `81a0a5d` (2.1) restores explicit Highlight/Note labels in
mixed navigation; `96c5a15` (2.2) avoids redundant DOM updates and stabilizes the
save-status width to fix typing-related flicker. Both accept old journals; neither
changes judgment fields nor adds group/model/original identifiers. Mixed projection
field/value scans and storage tests find no explicit group leak. UI cues were not
constant throughout annotation: final marks retain 3 records from 2.0, 57 from 2.1,
and 21 from 2.2. Familiarity/style cues remain outside that metadata guarantee.
The replay checkout fast-forwarded to main's existing `96c5a15` to use its
cross-version statistics parser; no annotator/comparison implementation was edited.

A1 (`gpt-6-luna`, medium): Note 4/21 (19.05%), Highlight 9/10 (90%), no stars.
B (`gpt-6-sol`, high): Note 21/30 (70%), Highlight 15/20 (75%), four Note stars.
B−A1 Note rate is +50.95 percentage points: the preregistered ≥25-point threshold
is met within this sample. The same 16 units' original first annotations were
Note 3/25 (12%), Highlight 3/9 (33.33%). Different generated output populations
prevent attributing these rate changes entirely to judgment-standard drift.
Six exactly identical Highlight quotes/anchors permit a narrower check: three
change fail→pass, three remain unchanged. No identical Note body+anchor pair exists.
This establishes some rejudgment inconsistency, not its cause.

Private evidence: `reading-companion-backend/state/experiments/q1_digest_fixed_history_20261108/reveal-001/`
contains `report.md`, the grouped 51-Note `notes.md` (no source excerpts), raw statistics,
independent analysis, version diffs, frozen current/baseline journals, scripts and
append receipt. Baseline attribution uses the immutable legacy-context journal-prefix
hashes; all 16 units/mark IDs/source identities/coordinates were verified.

The result does not establish that prompt is the dominant cause: there is no prompt
arm, and B changes model plus reasoning effort together. Prior exposure and UI changes
also limit interpretation. Mechanism/default changes are deferred until the owner
reviews individual reasons and chooses the next controlled experiment. No new model
calls, A2 blind annotation, evidence-catalog promotion or push. This is a bounded
sample-level diagnostic, not a new stable mechanism requirement or direction decision;
no stable mechanism or decision-log change is warranted.

Reveal validation: 18 comparison/provenance tests and 15 annotator-storage tests
passed; full ledger/provenance and `make agent-check` passed (55 contract tests,
17 pre-existing traceability warnings). Final source journal still matches the frozen
snapshot. The report hash and unchanged prior experiment-log prefix were rechecked;
private `validation.json` binds report/scripts/input fingerprints. No tool code changed.
