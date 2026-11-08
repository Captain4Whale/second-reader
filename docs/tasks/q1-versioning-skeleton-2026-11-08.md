# Q1 iteration versioning skeleton

Scope: immutable runtime-loaded prompt text, rubric identity, frozen unit sets, trial
records, human attribution, private request samples and dirty-workspace evidence.
No model was run, no prompt words or mechanism decisions were changed, no push.
Branch: `codex/q1-versioning-skeleton`, based on the latest Q1 annotator branch.

## Delivered

- `5153a57`: sole-source version files, private SHA-256 few-shot assets, fail-closed loader,
  explicit offline recovery, immutable publication checks and nine complete prompt-pair
  comparisons. All nine pairs matched byte for byte; existing prompt tests also passed.
- `70d47e3`: standard-mode complete logical request hashes (including tool history and
  repairs), per-invocation samples, immutable invocation receipts and tracked diff patches.
- `5d2d8ce`: rubric draft and version registry, annotator 1.9 identity fields and preserved
  legacy contexts. Ten actual annotator storage tests passed; original 605 rows untouched.
- `376f9b3`: frozen unit manifests, one baseline trial, historical workspace evidence,
  checked experiment appends and annotation-context generation.
- Frozen dev 67 units / 110 marks; holdout 75 units / 80 marks; no unit-ID overlap.
  No holdout source or judgments were reviewed. Metadata-only extraction preserves
  source coordinates, product/source hashes, run/reading/batch/unit/mark IDs.
- `Q1-BASELINE-001`: both original full-book runs, initial first-batch labels,
  `open_coding`, `weijiang`, reconstructed release hashes, pass rate null. No new
  subjective quality claim or score. `q1-v0` remains draft; rules need owner definition
  in a later version before rubric-based scoring can begin.

## Historical dirty-state evidence

The actual original session's completed status commands at 2026-11-03 12:28:33Z,
12:29:03Z, 22:38:55Z and 22:58:36Z name only the two run-ledger files as modified.
Both run metadata and standard traces name commit d414030 and dirty=true. Exact
historical patches and changes between snapshots cannot be recovered. The sanitized
evidence is frozen at `reading-companion-backend/experiments/baselines/q1-workspace-evidence.json`.
Current working-tree diffs are not substituted for old ones.

## Boundaries and verification

Raw few-shot bodies, samples, patches and migration captures are ignored. Missing
private assets stop prompt loading with a recovery pointer; no shortened fallback.
The local d414030 Git object can recover the initial exact few-shot, with hash
verification and no network. A clone without that object needs the private backup.

The original pre-task `run_ledger.json` / `.md` modifications are deliberately left
unstaged and unchanged. No run status is changed by registering a baseline. No API,
Reading Product, Annotation Pack or consumer wire changes were needed: provenance
remains private runtime/evaluation data. DEC-161 records the new storage authority;
product purpose, journey, model selection and reading control shape remain as before.

Operator commands and current artifact identities: `reading-companion-backend/experiments/README.md`.

Validation: all 1,779 backend tests passed with socket connections blocked. Subsequent
active-release/Gitless-install hardening passed 16 focused tests. Ten annotator storage
tests and `make contract-check` passed; immutable prompt/unit/rubric and real legacy
journal-prefix checks passed. The switching checker reports the same 17 historical
warnings (old task acceptance paths and duplicate DEC-066/DEC-079), with no new issue.
No new frontend application UI/route or public wire changed; this task adds metadata
to the existing standalone annotation tool rather than changing its visible layout.
