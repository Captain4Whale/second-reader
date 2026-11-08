# Fixed-history Digest rerun diagnostic

Status: waiting for owner review of the completed single A1 pilot, 2026-11-08.
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

The invocation helper completed one live A1 pilot after the follow-up authorization
below. The full diagnostic, comparative report and blind batch have not been created.

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

**Next gate: wait for owner confirmation before any other unit, A2 or B.** The pilot
should be reused as this unit's A1 sample, not regenerated to seek a different output.
