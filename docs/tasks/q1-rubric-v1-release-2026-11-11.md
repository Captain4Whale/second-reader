# Q1 rubric v1 publication and new review

Status: done, 2026-11-11. Base: `20f9270`; branch: `codex/q1-rubric-v1`.
Local independent commits only; no push. No model calls, prompt/mechanism changes,
annotator code changes, record schema changes or existing annotation writes.

## Publication

- Exact owner attachment published as `reading-companion-backend/rubric/q1-v1.md`;
  SHA-256 `adabae9d16162163ffe25dfe81cd60515788d899aa436da25476095d614de2e3`.
- `q1-v1.form.v1` registered and frozen; form SHA-256
  `0b7d3d49bc33affe65f2adf8ee6934adae3ae1957a42789a0fb655e355a14126`.
- [Example verification](../../reading-companion-backend/rubric/q1-v1.verification.md):
  38 unique identities equal v0; B u000237-replay-m005 and B u000017-replay-m002 move
  N2 → N1. Body checks: 11 exact, 8 quotation-only, 2 excerpts, 17 ID-only.
- IDs/tags/flags/policy retained; N2 label is 准确; help derives from v1 sections
  with identifiable examples removed. CLI default stays v0; v1 is explicit.
- The main workspace already had an uncommitted q1-v0.md change. It was neither
  overwritten nor committed; all publication/identity checks use the clean base in
  this isolated worktree. This release does not repair or endorse that dirty copy.

## New session

`/Users/baiweijiang/.codex/worktrees/q1-rubric-v1/reading-companion/reading-companion-backend/state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v1`

Session ID: `a46a04d3-6e04-430d-bd60-0f744f910a33`. Empty new `judgments.jsonl`, 81 annotations,
0 completed / 81 incomplete; no v0 judgments imported. Exact mixed and 313-revision
open_coding snapshots match the original DIAG-001 source; no private group keys copied.
Open this folder with the unchanged main-workspace annotator 3.2.

The old session remains at
`/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v0`.
The owner reports stopping after a few judgments due to N2's definition defect.
The on-disk journal was empty when inspected; browser drafts were not inspected or
changed. All old session bytes are preserved. N2/N4 meanings changed, so criterion
judgments must not be pooled across v0/v1, migrated or retroactively reinterpreted.

## Append-only registration

Exactly two rows appended to `experiments/log.jsonl`, each binding its previous raw
prefix's length and SHA-256:

- `Q1-RUBRIC-V1-RELEASE-001`: change summary, rubric/form/examples hashes, new session,
  v0 stop reason and the distinction between owner report and disk observation.
- `Q1-DIGEST-DIAG-001-HIGHLIGHT-RECONCILIATION-001`: owner verification of 3 Highlights
  with identical A1/original selection and opposite judgments. Bovary u000031's original
  reason evaluated the attached Note; Sapiens u000237 failed for missing a neighboring
  sentence and should pass from v0 onward with a separate omission; Sapiens u000144's
  original failure was a mistaken action. Conclusion: unwritten rules plus one mistaken
  action, not standards drift. This records the owner's finding, not new assistant scoring.

DEC-162 and CLOSE-001 remain byte-identical. No new decision-log entry: this is a bounded
publication and an explicit append-only correction requested by the owner, not new
mechanism/product direction. The addendum and stable evaluation doc carry the clarification.
Old scores/thresholds and exclusion of H rates from the existing decision remain intact.
The generated INDEX is refreshed from the logs; no new scoring receipt is fabricated.
Its existing generator hardcodes the earlier Highlight drift sentence and displays
experiment_closure conclusions only, so it lists the new addendum ID but does not
render its correction text. The current clarification lives in log.jsonl and the
stable evaluation/current-state docs. Generator changes are deferred as outside this
configuration/publication task; the v0 pending scoring receipt remains historical.

## Validation

- 82 Python tests: forms, both-version preparation/reporting, statistics and immutable provenance.
- 48 Node tests: storage, keyboard and form rules, including v1 engine/cache compatibility.
- Trusted-base immutable release check against `20f9270`, including both legacy journal prefixes.
- `make agent-check` contract phase passed (including 55 Annotation Pack tests,
  OpenAPI and frontend checks). It initially stopped at the isolated worktree’s
  missing job-registry metadata; after provisioning an ignored copy, the remaining
  traceability, scoring and INDEX checks completed. Traceability reports 391 warnings
  about historical/missing private evidence and existing duplicate decision IDs;
  none requires changing this release. No unrelated evidence was fabricated.
- Source hashes, raw log prefix, all existing v0 files and old session bytes checked.
- Exact attachment copy and new session/form/baseline identities verified offline.

Private audit scripts and evidence are in ignored
`reading-companion-backend/state/rubric_examples/q1-v1-publication-20261111/` in this
worktree. The complete review-session territory is explicitly ignored. No long-running
model/eval job was launched, so no new job or run-ledger entry is needed.

Local check setup reuses the main-workspace Python environment and frontend dependencies
through ignored links, and copies private prompt assets plus job-registry metadata into
ignored state. No service, system setting or source workspace dependency was changed.
