# Q1 rubric-driven annotator 2.3

- Task: `TASK-Q1-RUBRIC-ANNOTATOR`, done (tooling; human rejudgment pending).
- Scope: offline form/UI/report workflow, three commits, no push. No model calls,
  prompt/mechanism changes, rubric Markdown edits or historical annotation edits.
- Authority: [review protocol](../../reading-companion-backend/experiments/rubric-review.md).
- Owner adjustments: failure reasons optional and recorded as a form-protocol difference;
  hide/disable all omission entry points, retain historical omissions, exclude them from reports.
- Deferred: unlimited mixed omissions vs q1-v0 max two. Published-draft freeze strictness
  from the preceding publication task remains unchanged too.

## Implementation

1. Frozen `rubric/q1-v0.form.json`, separate `form-releases.json`, hash-bound form checks,
   and `q1-mixed-judgment/2` validation. Existing publication entries stay immutable.
2. Annotator 2.3 renders N/H criteria and tags from configuration, derives outcomes, keeps
   unchecked unconfirmed marks unjudged, and isolates caches/handles by review identity.
   Completion writes only new revisions; old judgment display requires saved completion.
   Exposure is monotonic and first pre-exposure completion remains in the journal.
3. `scripts/q1_rubric_review.py` prepares a fresh private folder and creates JSON/Markdown
   comparison reports with both disagreement directions and an overlapping uncovered list.
   Reports pair latest completed revisions, preserve exact mark/anchor text, and omit
   omissions. They include rubric examples because this is human rejudgment, not unseen
   LLM-judge agreement measurement.

## Prepared real session

- Open `reading-companion-backend/state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v0`
  using annotator “打开批次文件夹”. It contains no blind key/group map.
- 16 windows / 81 items (51 Notes, 30 Highlights), zero new judgments.
- Baseline: latest 313-revision DIAG-001 open_coding journal, SHA-256
  `28fff5eb3b0269d69c46d46b66f67f654dcc1ac6703e07edd4cbec4f627235b5`.
- Exact baseline/mixed copies, form identity and source location are recorded in the
  private `annotation-context.json` and `preparation.json`; originals remain untouched.
- Source journal lives in the q1-digest-replay worktree. The prepared snapshot is fixed;
  later original revisions require another explicitly prepared session.

## Validation

- 50 focused Python tests and 22 Node storage/form tests pass. Ruff passes for the new
  form/review code and affected statistics/tests. Immutable rubric/form/prompt checks pass.
- `make agent-check` passes contracts (including 55 Annotation Pack tests, OpenAPI and
  frontend contract checks); it reports 17 existing historical traceability warnings,
  unrelated to this task. The pre-existing E731 lambda in `check_iteration_provenance.py`
  was observed in the broader lint command and left unchanged.
- Synthetic browser flow: multi-criterion fail with empty reason, tags/verification-only
  pass, star restriction, uncovered fail, explicit completion, old-judgment reveal/collapse,
  amendment after reveal, navigation, draft reload and scope-labelled export.
- Synthetic report from actual UI-written rows: 5 items, 4 completed, 1 incomplete;
  2 old-pass/new-fail, 2 old-fail/new-pass, 1 uncovered (overlaps differences).
  Python fixtures additionally test unchanged/latest revisions and omitted baseline omissions.
- Storage tests cover delayed/failed writes, snapshot corruption, wrong scope, exposure
  ordering and no writes to the original journal. Form tests cover type/choice rejection,
  derived fields and future configured IDs; frozen checks reject refreshed-hash rewrites.
- Real DIAG-001 opened in isolated Chromium using exact prepared files and genuine OPFS
  filesystem handles. Browser read only `mixed.json`, context, form, old snapshot and new
  journal; N/H controls matched, prior panel stayed empty, P/F/O and omission selection
  did not create rows. No group keys were copied/read; no source group identity rendered.
- Visual checks at 1600×900 and 960×800 covered initial/expanded/confirmed/revealed forms.
  No horizontal overflow, overlapping controls or clipped form content; long sidebars use
  the existing page scroll. Exploration covered type/window switching, backtracking and
  restoring unfinished drafts. The OS-native directory permission dialog was not automated;
  the fixture picker returned actual isolated browser filesystem handles.
- Private evidence: `reading-companion-backend/state/q1_rubric_reviews/qa/inventory.md`,
  screenshots and `synthetic-report-final/report.{json,md}`. No source text or reports added to Git.

This is a bounded tool extension, not a mechanism or product-direction decision. The
protocol and this task record preserve its choices; no decision-log entry is needed.

## 2026-11-10 folder-open diagnosis and recovery

Owner reported a generic browser NotFoundError and the completed old 81-item view staying
visible. Both the supplied file URL and review-folder path were correct; all six files
were present. The original error lacked file/stage details, so its precise failing handle
cannot be reconstructed. Refreshing the owner's actual Edge tab and selecting the same
directory through the native macOS dialog succeeded: q1-v0 review, 0/81, N1–N4 and tags,
no omission controls, old-judgment toggle locked. No judgments were entered.

Annotator 2.4 now displays version and rubric mode and names missing batch/form/snapshot/
journal files instead of forwarding only the generic English exception. Failed loads
retain the current batch. Both 2.3 and 2.4 review records remain readable with no schema
change or record rewrite. Regression coverage includes missing files, failed-load session
preservation and switching from the same batch's completed open_coding cache to blank review.
Isolated Chromium screenshots cover 1600×900 and 960×800; the real Edge/native picker flow
now supplements the earlier OPFS-only acceptance. No form, rubric or historical data edits.
Validation: 51 focused Python tests, 24 Node tests, affected Python lint and frozen-provenance
checks pass. The 17 historical traceability warnings remain unchanged. The original
313-row journal still has the same `28fff5eb…` hash after native-folder recovery.
