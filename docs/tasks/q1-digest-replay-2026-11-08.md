# Fixed-history Digest rerun diagnostic

Status: waiting after fail-stop preflight, 2026-11-08.
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

The invocation helper has not been live-tested. This slice is not a completed or
accepted experiment tool. The 48-call orchestration, comparative report and blind
batch have not been created.

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

Proposed next step: compare canonical chapter/paragraph/offset identity, retain both
display labels as provenance, and keep the BookDocument exact-text round-trip check.
Do not resume generation until the owner responds to the required stop report.

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
