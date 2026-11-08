# Fixed-history Digest rerun diagnostic

Status: waiting for owner review of the completed 16-unit A1 diagnostic, 2026-11-08.
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
