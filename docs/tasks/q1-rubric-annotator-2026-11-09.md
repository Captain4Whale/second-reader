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

## 2026-11-10 keyboard interaction (2.5)

Owner-approved keyboard flow is implemented in the existing standalone annotator:
1–4 criteria (1–3 for Highlights), 5/6/7 Note labels, 0 uncovered, Shift+digits criterion
help, B prior judgment, Enter completion/stay and Shift+Enter completion/next within
the current window. Last items stay; existing arrows, J/K, R/M/U, S/V and legacy
Open Coding controls keep their meanings. Keys are shown inline and in a compact,
mode/type-aware help dialog that opens at its heading. Configured controls and existing
mouse handlers remain the source of action semantics; published rubric/form bytes,
journal schemas and cache identities are unchanged.

Completion is shared by button and keyboard. It checks both save receipts (storage
queues report failures without rejecting), suppresses concurrent completion and does
not duplicate unchanged revisions. Pending work cannot navigate or steal focus after
leaving and returning, editing, switching focus or opening help. Errors keep the item
visible with a save-state explanation. V now respects held-key suppression; scrolling
still repeats. Native button/summary Enter, checkbox Space, Tab, text input/newlines,
IME guards and modifier combinations remain supported. Prior reveal also checks the
navigation epoch before rendering an asynchronous result.

Version 2.5 is accepted by browser import and Python statistics alongside 2.3/2.4;
Open Coding version acceptance remains backward compatible. Refresh existing HTML
pages to load the new code. No model calls, original journal edits or push.

Validation:

- 37 Node storage/form/keyboard tests; 50 focused Python rubric/review/statistics/
  provenance tests; affected Python Ruff and frozen prompt/provenance checks pass.
- `make agent-check` passes contract/OpenAPI/frontend checks, including 55 Annotation
  Pack tests; it retains the same 17 historical traceability warnings.
- Isolated headed Chromium, synthetic OPFS files: all N/H toggles and reversals,
  pass/fail and star rules, input/newlines, completion, exposure reveal/collapse,
  Shift+Enter boundaries, restored unconfirmed amendments, slow disk, duplicate
  completion, navigation away/back during save, disk/browser failures and retry.
  Tab/Space/native Enter, held V, mode-specific help and Open Coding P/F/S/V/O
  were exercised with browser input. Composition/229 guards use simulated events
  and unit tests; the OS-native IME candidate UI and file picker were not automated.
- UI-written 2.5 journal successfully produces an offline comparison report: five
  items, three completed, two incomplete, one old-pass/new-fail difference.
- Screenshots at 1600×900 and 960×800 cover criteria/labels, expanded explanations,
  completion/prior judgment, save failure and N/H help. No horizontal overflow,
  overlapping controls or clipped help; long annotation panels retain page scrolling.
  Exploratory checks covered focus on completion controls, amendments/reload and
  late save receipts after navigation.
- Real DIAG-001 was opened only in an isolated copied browser filesystem for display;
  five original input-file hashes remained unchanged and no judgments were entered.
  It still showed 0/81 at verification. Original Edge was not reloaded or operated.
- Private QA inventory, screenshots, synthetic journal/report and source-hash receipt:
  `reading-companion-backend/state/q1_rubric_reviews/qa/keyboard-2.5/` (ignored).

This is an interaction change, not a mechanism/product-direction decision; this
record and the rejudgment protocol capture the behavior, so no decision-log entry
is needed.

## 2026-11-10 stepwise interaction (3.0)

The owner replaced the checkbox review flow with explicit per-criterion decisions.
Each case now has a second row of rubric squares (unjudged / pass / fail, current
outline) and a summary step. Only one criterion is displayed. P/F judges and stays;
R enters its independent optional reason; Enter requires a judgment before advancing.
The last criterion leads to summary. All criteria must be judged even after an early
failure. Clear restores unjudged and preserves that criterion's reason. Step/draft
state survives case/window navigation and reload.

The help text opens by default, scrolls inside a maximum 240px/20vh region, and reasons
start at two lines. Pass/fail buttons precede the potentially long explanation so they
remain reachable in the initial small-window view. N2 verification stays in N2;
labels, star, uncovered/reason, overall memo and historical judgment live in summary.
Digits select criteria; brackets browse; Shift+digit opens/toggles help. Summary
Enter confirms/stays; Shift+Enter confirms and advances only after both save receipts.
Existing case/window navigation, source/page scrolling, native controls, composition
protection and Open Coding shortcuts remain available. Save failures and navigation
races retain the 2.5 completion/exposure protections.

New formal records use `q1-mixed-judgment/3`, with exact configured
`criterion_assessments` keys containing pass/fail plus reason, and `uncovered_reason`.
`failed_criteria` and overall outcome are derived and validated in JS/Python. Drafts
may be unjudged; formal rows may not. Historical overall `reason` is separate and
never split or synthesized from per-criterion reasons. Reports include all completed
cases' criterion assessments/reasons, including unchanged outcomes, and identify
legacy whole-case confirmations explicitly.

Existing `/2` completed records still count as complete and are read-only until
“重新逐项判断”; restart sets every criterion unjudged. Old unfinished drafts retain
only checked failures as explicit fail, preserving overall reason, notes and flags.
An incomplete draft cannot retain an enabled star. New completions append `/3` in the
same session without rewriting the old prefix or snapshot. Old exposure-only
revisions retain `/2`. Tool versions 2.3–2.6 remain accepted; `/3` requires 3.0.
Published rubric/form, cache identity and public APIs are unchanged.

Isolation and environment:

- Implementation branch: `codex/q1-rubric-stepwise`, based on `73f4d38`, worktree
  `/Users/baiweijiang/.codex/worktrees/q1-rubric-stepwise/reading-companion`.
- At start, the original workspace had uncommitted 2.6 compatibility changes in
  `q1_comparison_stats.py`, its test, `test_q1_rubric_form.py` and the storage test.
  These were preserved; the 3.0 implementation is committed separately, not pushed.
  Open the HTML from the new worktree; refreshing the original HTML still loads 2.x.
- The independent worktree reuses existing ignored `.venv`, `node_modules`, private
  prompt assets, job registry and historical evidence through local symlinks for
  read-only checks. No private evidence was migrated or committed. QA writes stayed
  in this worktree's ignored `state/q1_rubric_reviews/qa/stepwise-3.0/`.

Validation:

- 42 Node storage/form/keyboard tests; 72 Python rubric/review/statistics/provenance/
  scoring tests pass, plus affected Python Ruff and `git diff --check`.
- Prompt releases and frozen iteration checks pass against trusted base `73f4d38`;
  registered rubric/form bytes are unchanged. `make agent-check` passes Reading
  Product/Annotation Pack checks (55 tests), OpenAPI and frontend contract checks,
  scoring/index checks. The initial fresh worktree lacked ignored local evidence;
  after linking existing evidence for read-only checks, traceability retains the
  same 17 historical warnings (missing old acceptance refs/paths, duplicate decisions).
- Isolated headed Chromium with synthetic OPFS: N/H P/F, unjudged gate, clear/reason
  retention, independent multiline reasons, tags/verification, all-pass star and
  uncovered clearing star, summary completion, last-case boundary, prior exposure,
  amendments, case/window/step switching, reload restoration, native Enter/Tab/Space,
  held-event/modifier/composition-229 guards, slow save + duplicate completion +
  navigation away/back, file and browser write failure/retry, Open Coding regression.
  IME guards were exercised by simulated composition/229 events, not an OS-native
  candidate-window test; the native folder picker was replaced with isolated OPFS.
- Legacy complete/restart and unfinished-draft migration were exercised in separate
  synthetic contexts. New `/3` appends preserved the exact `/2` byte prefix.
- The UI-written 5-revision journal generates a valid private comparison report:
  5 cases, 4 completed, 1 incomplete, 2 unchanged, 1 old-pass/new-fail,
  1 old-fail/new-pass and 1 uncovered; per-criterion reasons are displayed.
- Screenshots inspected at 1600×900 and 960×800: grid status/current outline, N/H,
  summary and legacy presentation, bounded scrolling explanations, two-line reasons,
  no horizontal overflow. Long original text/case bodies retain page scrolling;
  P/F stays visible initially on the checked real small-window case, R brings its
  reason into view. Rule and source scrolling were exercised independently.
- Real DIAG-001 display only through copied browser files: still 0/81, five original
  hashes unchanged. No real decisions, model calls or original browser actions.
- Evidence: QA inventory, screenshots, `synthetic-session/`, `synthetic-report-final/`,
  `real-source-hashes.json`, `agent-check-final.log` and `traceability-final.log` in the ignored
  QA directory above. Synthetic fixture input was read from the prior QA folder.

This is a scoped annotation interaction/protocol extension, fully recorded here and
in the rejudgment protocol. It does not change mechanism/product direction and needs
no new mechanism decision-log entry.

## 2026-11-10 main integration

The owner explicitly authorized merging and pushing. After fetching, `main` and
`origin/main` were both `73f4d38`. The original four uncommitted 2.6 compatibility
edits were preserved intact in local stash `fd6de499ea9d01f716aa5924068e6dc1b21aea9b`
(`preserve pre-3.0 main 2.6 compatibility edits before stepwise merge`); the stash
was not dropped. Main fast-forwarded to implementation commit `acd1503`.

3.0 already includes the 2.6 parser/form acceptance. The remaining mixed-statistics
version test now covers both 2.6 and 3.0; the storage output-version assertion stays
at 3.0 rather than restoring the obsolete 2.6 expectation. The README, current state
and task router now direct the owner to the main workspace HTML. The separate
implementation worktree remains available; no real journal or snapshot was changed.

Main verification: 42 Node tests, 74 focused Python tests, affected Ruff,
`git diff --check`, frozen prompt/iteration checks against `73f4d38`, and
`make agent-check` pass. The same 17 historical traceability warnings remain.

## 2026-11-10 layout 3.1

Implemented the approved layout directly in default workspace `main`, from `65d0992`.
One independent local commit; no push. The 3.0 rubric, form/hash, `/3` schema, cache
identity, all-criteria completion and prior-view/save gates remain unchanged.

- ≥1440px: source / current annotation / decision at 44% / 26% / 30%, using the
  viewport below the measured toolbar. Each content area scrolls locally; actions
  remain at the decision panel's bottom. Source/body typography is unchanged.
- 960–1439px: source left, annotation over decision right; short viewports reserve
  usable decision height. <960px: natural source → annotation → decision page flow.
- Window progress moved below the annotation; window remarks are collapsed by default,
  show “已填写” when present, and U opens/focuses the existing field. R/M reveal their
  own scrollers. Desktop Shift+J/K scrolls decisions, or the explanation when the form
  already fits. J/K continues to scroll source. Narrow/Open Coding page keys stay intact.
- One DOM control per field; reparent only on review/Open Coding mode transitions.
  No cloned fields or extra event registrations. Browser and Python accept 3.1 plus
  previous versions; a regression verifies appending 3.1 after an unchanged 3.0 prefix.

Validation:

- 45 Node storage/form/keyboard tests and 78 focused Python tests passed; affected Ruff
  checks passed. Frozen prompt/rubric/form checks and `make agent-check` passed; the
  latter retains the same 17 historical traceability warnings, with no new issues.
- `playwright-interactive`, isolated Chromium/OPFS synthetic batches: 1920×1080,
  1600×900, 1440×900, 1280×800 and 390×844. Wide normal cases show current annotation,
  criterion, P/F, reason and actions without page scrolling; long text uses local scroll.
- Note/Highlight, cross-window full quote, all four Note conditions, longest help,
  long reason/Note, summary, long expanded prior judgment, empty window and single-group
  density/mixed Open Coding were exercised. Mode switches and resizing preserve drafts
  and unique field IDs. R/M/U, J/K and Shift+J/K were checked in their relevant layouts.
- English typing and CDP-simulated Chinese composition persist through refresh without
  moving the toolbar button. This checks browser composition, not the OS IME candidate
  chooser. Directory selection uses genuine isolated OPFS handles; native picker
  permission UI was not automated.
- Injected disk and browser failures retain data and expose retry feedback; retry saves
  successfully and prior viewing unlocks only after receipts. Test judgments exist only
  in isolated synthetic storage and ignored QA evidence.
- A native-window pass and 125% / 150% effective desktop viewport checks (1280×720 /
  1067×600 for a 1600×900 viewport) covered display enlargement and short-height focus.
  Zoom was simulated with viewport/DPI settings, not the browser's native zoom menu.
- Real DIAG-001 was opened only from an exact isolated copy; zero completed rows remain.
  All five original UI input/journal files retained their SHA-256 values. No original
  annotation, rubric, form, prompt or experiment/scoring row was modified.
- Screenshots, measurements, synthetic journal and integrity receipts remain ignored in
  `reading-companion-backend/state/q1_rubric_reviews/qa/layout-3.1/`.

Operator behavior is documented in the root README and `experiments/rubric-review.md`.
No API/frontend integration, mechanism or evaluation policy changed; their stable docs
and decision log need no update for this bounded annotator presentation change.

## 2026-11-11 natural layout 3.2

Owner feedback showed that 3.1's viewport-height constraint left the actual Note and
rules squeezed beneath navigation, particularly at medium widths/display enlargement.
3.2 prioritizes readable content and permits page scrolling. Implemented directly on
main from `adebf77`; one local commit, no push.

- Wide 44/26/30 columns remain. Medium layout uses source left, annotation then decision
  right with natural row heights. Mobile stays single-column. Source remains sticky and
  independently scrollable; the wide annotation sticks only when its full height fits.
- Removed nested reading scrollers and height caps for quotes, Notes, explanations,
  expanded prior text and remarks. Textareas grow. Desktop actions stick at the viewport
  bottom within the editor; flow space and focus offsets keep final content reachable.
- R/M/U reveal page fields; condition/case navigation reveals the appropriate heading.
  J/K still scrolls desktop source, Shift+J/K scrolls the page. No cloned controls.
- Version 3.2 accepts 3.0/3.1 and earlier records. Schema `/3`, form/hash, cache identities,
  assessment rules, completion/save gates and Open Coding remain unchanged.

Validation: 47 Node tests, 82 focused Python tests and affected Ruff checks passed.
Browser acceptance used playwright-interactive with isolated synthetic OPFS batches at
1920×1080, 1600×900, 1440×900, 1280×800, 390×844, and effective 125%/150% desktop
viewports (1280×720 / 1067×600). Checked full quote/Note/help, long reason/prior, fit-only
sticky behavior, Note/Highlight summary and prior gate, empty/cross-boundary windows,
Open Coding switching, unique controls, toolbar stability, IME composition, refresh
recovery and injected browser/disk failures with retry. Chinese composition was CDP
simulated, not OS candidate-menu automation; native folder picker was substituted with
isolated real filesystem handles. No model calls.

Real DIAG-001 was displayed from an exact isolated copy without test judgments; all five
original input/journal hashes remain unchanged and the journal still has zero completed
rows. Private screenshots, measurements, synthetic revisions and hash receipts live in
`reading-companion-backend/state/q1_rubric_reviews/qa/layout-3.2/` (ignored).

This is an annotator presentation correction, with no API, rubric, mechanism or evaluation
policy change. README/protocol/current task records are updated; no decision-log change
is needed. Frozen-asset checks and `make agent-check` passed; the latter retains the
same 17 historical traceability warnings, with no new issues.
