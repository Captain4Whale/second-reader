# Q1 rubric v0 publication

Status: done, 2026-11-09. Scope: exact rubric publication, reference verification,
example exclusions, immutable-release tests and append-only registration. No prompt,
mechanism, model, annotator, existing judgments or batch-context changes; no push.

## Publication

- `reading-companion-backend/rubric/q1-v0.md`: exact owner attachment bytes,
  SHA-256 `3ed0c44ab82b1a95802eb669717570a282169200b45faec1a090706ab1bd12fa`.
- `rubric/q1-v0.examples.json`: 38 unique exclusions, 20 positive / 18 negative;
  A1 4/8, B 16/8, R 0/2. Four upstream unit exclusions are listed separately.
- `rubric/q1-v0.verification.md`: full mappings, latest revisions and discrepancies.
  All 38 resolve uniquely and agree on pass/fail. Of 21 quoted bodies, 11 match exactly,
  8 differ only in quotation marks, and 2 are excerpts with changed quotation marks.
  Reasons are edited summaries, not verbatim journal text; the B u000006-replay-m003
  reason differs in its rationale. Supplied rubric bytes were not corrected.
- `experiments/log.jsonl`: one `Q1-RUBRIC-V0-RELEASE-001` row, existing bytes preserved.
  Source labels remain `open_coding`; this is publication, not retrospective scoring.

## Authorized frozen-draft migration

The old q1-v0 draft was already frozen. The owner explicitly authorized moving its
identity to q1-v0-draft only if no log, judgment or run metadata referenced it.
Searches of four existing worktrees found only frozen registry references. Old bytes
remain in `rubric/q1-v0-draft.md`; original registration and frozen entry remain in
the release registry and its hash-bound `rubric/q1-v0.migration.json` receipt. Both
registries bind old/new file hashes, migration timestamp and reason.

The overly strict frozen-draft rule is recorded, not changed. Existing trusted-base
checks intentionally reject this explicit one-time migration from its earlier base.
Current identities and source bytes are validated before the migration commit; normal
trusted-base checks use that commit thereafter. No general migration bypass was added.

The DIAG reveal is in another local worktree at b431889. Its live private files were
read directly; that commit and unrelated task/ledger updates were not merged here.

## Validation

- Nine focused provenance tests pass, including four trusted-Git-base tamper cases
  covering rubric body, example list, status downgrade and registration removal.
- Existing comparison bundle and journal validators pass on the 313-row DIAG journal.
- Current identity checks and both real legacy journal-prefix checks pass; source
  snapshots, exact attachment copy, old draft bytes and experiment-log prefix verified.
- `make agent-check` passed all contract checks (including 55 Annotation Pack tests)
  and completed traceability checks with the same 17 historical warnings.

No new decision-log entry: this implements the already requested version-management
workflow and the owner's bounded draft migration; it does not change product/runtime
direction. The source-of-truth map and AGENTS load order remain valid. Evaluation
methodology and operational exclusion policy are updated in the evaluation and
comparison authorities.
