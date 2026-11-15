# Rubric-driven Q1 rejudgment protocol

This workflow rejudges existing anonymous mixed annotations without changing source
outputs, prompts, the reader mechanism or historical judgments. It does not run models.
The owner-approved first form is `rubric/q1-v0.form.json`, registered separately in
`rubric/form-releases.json` and frozen by `experiments/frozen.json`. Existing rubric
publication entries and q1-v0 Markdown remain immutable. Add a new form version for
later changes; criterion/tag IDs, labels, help and supported policies are configuration,
not annotator code. Form text contains rules only, never identifiable rubric examples.

## Published v3.4 Note review (2026-11-15)

The owner-approved `q1-v3.4.form.v1` is a separate Note-only protocol and entrypoint.
The published rubric owns options/thresholds; `q1-annotation-guide.md` owns sequence.
The v0/v1 forms, browser entrypoint, caches and old journal readers are unchanged.
Form schema is `q1-note-rubric-form/1`; journal schema is `q1-note-judgment/1`.
`form-releases.json` and `frozen.json` append the new identity, including the rubric
and annotation-guide hashes. The existing form loader dispatches by schema.

### Start and storage

From the backend, launch an existing prepared session:

```sh
.venv/bin/python scripts/q1_note_review.py serve state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v3.4
```

This binds only `127.0.0.1:8767` and opens the browser; `--no-open` and `--port` are
available. Stop with Ctrl-C; restart preserves all locks and judgments. No API server,
model, frontend build, cloud call or npm install is needed. This is a Chinese internal
annotation tool, not a change to the product application's locale or public API.

To prepare another isolated session from an **existing** comparison bundle:

```sh
.venv/bin/python scripts/q1_note_review.py prepare --source state/PATH_TO_EXISTING_BLIND_BATCH --session state/q1_rubric_reviews/NEW_SESSION --book-root state/PATH_TO_FIRST_ORIGINAL --book-root state/PATH_TO_SECOND_ORIGINAL --seed 20261115
```

Each book root must contain `public/book_document.json` and `_assets/source.epub`.
Both EPUB and substrate identity must match the original batch. `launch` accepts the
same arguments and prepares only if the session does not exist, then serves it.
Existing directories are never overwritten. `--purpose test --test-mark ANONYMOUS_ID`
(repeat the latter) restricts an isolated test session; formal preparation does not
sample or regenerate a batch. It selects all existing Notes, leaving Highlights intact.
All Notes across books share deterministic `sha256-sort-v1` order, bound with its seed,
ordered ID list and fingerprint. This is display randomization, not sampling.

Everything containing source text stays under ignored `state/`: `context.json`,
`judgments.jsonl`, `progress.jsonl`, screenshots and test evidence. `manifest.json`
binds input/context/form identity and session purpose. Formal and test directories
must differ; the page labels their purpose. Only explicit upstream unit notes are
carried forward; no historical annotation outcomes or blind group mappings reach UI.
Anonymous IDs permit later operator-side attribution through the original blind key.
Existing exposure to DIAG-001 is not undone by hiding groups in this new interface.

### Interaction contract

- One Note at a time, original source through the **end of its complete anchor**.
  Exact Unicode code-point coordinates also split a paragraph at the anchor end.
  Earlier context initially offers four preceding pieces and can expand through earlier
  chapters. No other annotations are shown.
- Within-unit and outside-unit following text remain absent from the initial response.
  Only N1 and spoiler steps may request it; each request is persisted before delivery.
  Each step has independent `viewed_following_text`, timestamp/range events. Switching
  steps collapses the text; exposures never reset. Following text stops at chapter end:
  “更远的后文靠你对这本书的了解”.
- Original notes use exact source HTML blocks, numeric note links and reciprocal
  backlinks. Independently deduplicated BookDocument link arrays are not zipped.
  Missing/unresolved links display “未解析” and do not block; conflicting resource/ID
  resolutions raise `UnreliableNotesError` and require owner review, never guessing.
- First impression explicitly locks before difficulty; difficulty completes before any
  later options appear. Unfinished drafts are durable in `progress.jsonl`. Both return
  and reload preserve locks. The first impression is immutable for the session.
- Difficulty is three-way: 一遍能复述 / 能改写得更直白 / 改写不出. The third automatically
  marks uncertainty; only the second is a veto. Explicit later correction preserves
  `original_choice`, ordered `amendments` (from/to/time/reason), and final `choice`.
  Outcome and future statistics always use the final choice. Count changed items by
  nonempty amendments, transitions by each event, and original-to-final separately.
- N1 following use has four choices: 没用到 / 紧接着几段 / 挂早了 /
  更远后文，转第四步判剧透. The fourth is the owner-approved form branch; the first
  three alone cannot encode distant spoilers. Immediate repetition forces N1 fail
  plus 下文马上讲了. Early anchor is judged at the hypothetical correct location,
  and adds an anchor tag only if the final result passes. Distant following use
  does not replace the independent spoiler decision.
- N1 passing style is single-select; failing types are multi-select. They cannot coexist.
  Other style, other failure, and uncovered require explanations. **Other failure is
  already in rubric 2.2**, not an extra form criterion. It categorizes an N1 failure;
  uncovered says the rubric's criteria cannot express the reason for failure.
- Even N1 failure must complete spoiler and incorrect-information steps. Default unchecked
  vetoes become judgments only on explicit step completion. Verification is separate.
- Outcome is derived from N1 and all three vetoes plus uncovered. Uncovered immediately
  clears tags/star. Failing journal rows omit `tags` entirely. Stars require pass.
- Uncertainty is per item (`unsure`); `unsure_sources` distinguishes `automatic`,
  `manual`, or both. Automatic difficulty uncertainty disappears if its triggering
  choice changes; manual uncertainty is preserved. Original choice and amendments
  retain evidence of prior automatic uncertainty. Reasons, paraphrase and rewrite
  text are optional except the three required explanations above.
- Explicit completion appends a complete judgment; corrections append revisions with
  `supersedes_revision`. `progress.jsonl` is a separate append-only transition journal,
  not a statistics input. The server rejects stale page versions and incomplete JSONL
  tails, fsyncs saves, and recovers a completed record if interrupted between the two
  journal writes. Source/form/context identities are checked on open. The server
  restricts paths and rejects cross-origin writes.

### Future scoring boundary

`read_note_review()` in `scripts/q1_note_session.py` validates and reads v3.4 records;
`q1_scoring.py` is unchanged and does not yet accept this protocol. A future adapter
must bind frozen journal bytes/hashes and select latest complete revisions within one
session/annotator/rubric/form scope. **No scoring snapshot is created by this task.**
Future `experiments/scorings.jsonl` rows carry hashes/identifiers/aggregate results,
never book text, quotes, Note bodies or free-text reasons; private evidence stays in state.

All Appendix A measures are recoverable: pass rate; pass without 有空话/冗余 over all;
that same clean numerator over passes; independent N1 and veto rates; other-style count
and pass rates with/without those items; uncertainty, verification and uncovered counts;
N1 pass failing only on difficulty. Per-item uncertainty counts once even with several
uncertain criteria; automatic/manual/both remain separable. The frozen-threshold inputs
are locked-first-impression disagreement / eligible completed Notes, uncovered count,
and uncertain-item proportion. No numeric threshold is invented by the form.

`unit_note` revisions carry `unit_key`, `remarks` and `upstream_excluded`; “上游：”
activates exclusion of the entire unit. Apply latest unit-note state before denominators,
not a stale per-mark copy. Unit notes do not enter annotation counts. No omission or
within-unit redundancy form is added. The frozen manifest detects incomplete coverage;
a finished-batch rate must not disguise missing judgments. Zero denominators are null.

Each applicable step stores `started_at`, `completed_at`, `active_ms`; fail-only label
skips are explicit. First reading occurs during step one, so difficulty-duration work
must include both steps one and two. Correction timestamps do not replace initial
completion times. `active_ms` measures visible-page interaction time, not pure reading
or attention, and background-tab time is excluded.

### v3.4 verification

```sh
.venv/bin/python -m pytest -q tests/test_q1_note_form.py tests/test_q1_note_session.py tests/test_q1_rubric_form.py tests/test_q1_rubric_review.py tests/test_q1_comparison_stats.py tests/test_q1_scoring.py tests/test_iteration_provenance.py
node --test tools/q1-annotator-storage.test.cjs tools/q1-annotator-keyboard.test.cjs tools/q1-rubric-form.test.cjs
.venv/bin/python scripts/check_iteration_provenance.py --base-ref b870d6e^
```

## Published v1 and separate sessions (2026-11-11)

The new published rubric is `q1-v1`, with `rubric/q1-v1.form.json` registered as
`q1-v1.form.v1`. N2 now means accuracy only; substantiated disagreement belongs to
N1, and relevance to the anchor belongs to N4. IDs N1–N4 / H1–H3, tag IDs/labels,
N2's verification flag and policy are retained. Help is derived from the corresponding
v1 sections without identifiable examples. The annotator and record schema are unchanged.

The owner stopped the q1-v0 review after a few judgments because N2 combined different
questions. At preparation time its on-disk journal was empty; browser-only judgments
or drafts were not inspected. Preserve the complete old session and any drafts as-is.
Do not migrate, delete or merge judgments. **N2 and N4 changed meaning: per-criterion
judgments from the v0 and v1 sessions must never be pooled or treated as the same measure.**
Rubric/form hashes and a fresh session ID keep storage and future scoring separate.

The prepared v1 directory is:
`/Users/baiweijiang/.codex/worktrees/q1-rubric-v1/reading-companion/reading-companion-backend/state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v1`.
Session ID: `a46a04d3-6e04-430d-bd60-0f744f910a33`. It contains 81 annotations,
zero completed judgments and an empty new journal; its baseline is the original
313-revision open_coding journal, not the stopped v0 review. The old session remains at
`/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v0`.
Open the new directory with the existing main-workspace annotator 3.2.

v1 explicitly supports optional criterion reasons, so the v0 reason-policy difference
below no longer applies. The unchanged form policy also permits an empty uncovered
reason; v1 Markdown asks for a sentence there. The form deliberately retains the
owner-requested policy, rather than silently adding validation. This pass still does
not record omissions, even though the rubric describes unit-level omissions.

## Historical v0 operational differences (retained for v0)

- A failure reason is optional for this rejudgment; q1-v0 Markdown says to write one.
  `policy.reason_required_on_fail=false` records this operational difference.
- This pass does not record omissions. Reuse historical open_coding omissions outside
  this workflow. Hide omission controls, selection actions and shortcuts; reject new
  omission records. The comparison report is annotation-only.
- Deferred: mixed mode currently permits unlimited omissions while q1-v0 says at most
  two per unit. Do not change either existing behavior or published rubric in this task.

## Completed records

`q1-mixed-judgment/3` retains anonymous batch/window/mark identity, exact content/range,
human/rubric identity, timestamp and append-only per-journal revision. It adds:

| Field | Contract |
|---|---|
| rubric_form_version / rubric_form_sha256 | Registered immutable form identity |
| review_session_id | Isolated rejudgment session; never a group or run identity |
| criterion_assessments | Every configured criterion ID → `{judgment: "pass" / "fail", reason: string}` |
| failed_criteria | Derived unique IDs whose criterion assessment is fail |
| uncovered_reason | Optional explanation for rubric_uncovered; independent of historical overall reason |
| tags | Unique configured tag IDs; do not cause failure |
| criterion_flags | Configured criterion → flag → boolean; N2 has needs_verification |
| rubric_uncovered | Owner considers this a failure not covered by criteria |
| review_completed | true for persisted annotation assessments; drafts stay in browser |
| prior_judgment_seen | Whether historical judgment has been revealed; cannot revert |

Every criterion must be explicitly pass/fail before a new completed record can be
written. Browser drafts may contain null judgments. Any failed criterion or uncovered
flag yields fail; otherwise pass. `judgment` and `failed_criteria` are checked derived
fields. Tags and `needs_verification` (a mirror of criterion flags) do not cause failure.
Stars require all criteria judged and overall pass. Per-criterion and uncovered reasons
are optional under the published form policy. Historical overall `reason` keeps its
original meaning; do not split it into criterion reasons or concatenate new reasons there.
`unit_note` remains supported with null assessment fields; omissions are not supported.

New confirmations append revisions; editing a completed case makes an unconfirmed browser
draft until all criteria are judged and the summary is confirmed again. Navigation,
checkboxes, P/F and typing never append a completed judgment by themselves.

Legacy `/2` completed rows remain complete and show “旧版整条确认”, without fabricated
per-criterion pass results. “重新逐项判断” starts a new draft with every criterion
unjudged, retaining historical reason/remarks and flags. Only a completed new review
appends `/3`. Legacy unfinished drafts retain checked failures as fail; unchecked
criteria stay unjudged, and the old overall reason stays separate. Clearing a new
criterion restores unjudged while retaining its reason.

A journal may contain `/2` and `/3` revisions from the same person, rubric, form and
review session. Existing raw prefixes, snapshots, cache keys and session identities are
unchanged. JS/Python accept `/2` rows from annotators 2.3–2.6, 3.0, 3.1 and 3.2 (for a legacy
exposure-only revision); `/3` accepts 3.0, 3.1 and 3.2. `/1` and single-group Open Coding retain
their previous validation, including nonempty failure reasons, and remain separate.
First completion must precede prior-judgment exposure; exposure cannot revert. Both
first completion and later amendments remain inspectable.

## Prepare, annotate and compare

Run from `reading-companion-backend/`:

```sh
.venv/bin/python scripts/q1_rubric_review.py prepare "$ORIGINAL_BLIND_BATCH" --form q1-v1.form.v1 --output state/q1_rubric_reviews/NEW_SESSION
.venv/bin/python scripts/q1_rubric_review.py report state/q1_rubric_reviews/NEW_SESSION --output state/q1_rubric_reviews/NEW_REPORT
```

For v0, explicitly select `--form q1-v0.form.v1`; omitting `--form` still defaults
to v0 for compatibility. Never reuse a prepared directory to switch rubric versions.

Output paths must be new directories under ignored backend `state/`; neither command
overwrites an existing destination. Preparation checks the original bundle and baseline,
then copies exact `mixed.json`, exact registered `rubric-form.json`, and an exact
`open_coding.snapshot.jsonl`. It creates a fresh empty `judgments.jsonl`, a hash-bound
`annotation-context.json` and an operator-only `preparation.json`. Private group keys and
canonical batch provenance are not copied. A prepared baseline stays fixed even if the
original journal later gains revisions; prepare another session to choose a newer baseline.

Open the prepared directory using annotator 3.2's “打开批次文件夹”. The HTML requires
the adjacent `q1-rubric-form.js`; keep both files together. The UI reads only the mixed
projection, context, form, baseline and new result journal. Browser drafts and remembered
handles are keyed by batch, annotator, rubric, form and review session. Old cache keys
remain intact. Restoring or navigating preserves unfinished drafts without confirming them.
If the HTML was already open before an update, refresh it first. The header displays
the loaded annotator version and current rubric/mode. Opening a folder does not load new
HTML code. Failed folder loads keep the prior batch visible and name the selected folder
and missing required file; they do not silently create missing review resources or import
old labels. Selecting only the JSON file does not load the companion review context/form.
The case's rubric squares show unjudged (·), pass (✓) or fail (×), with an outline
for the current step. One criterion is visible at a time. Help opens by default and
expands to its full content height. Reasons and remarks grow with their text; they do
not use capped internal reading areas. N2 verification is inside N2. The summary contains tags, star, uncovered
and its optional reason, case remarks and historical judgment. Even after one failure,
judge every remaining criterion before confirmation. Window notes remain separate.

## Layout (annotator 3.2)

Readability takes priority over fitting one viewport. Long content extends the page;
source/body font sizes and all judgment semantics stay unchanged.

- ≥1440 CSS pixels: source / annotation / decision retain 44% / 26% / 30% widths.
  Desktop source stays sticky with independent scrolling. A wide-screen annotation
  panel sticks only when its complete height fits below the toolbar; long annotations
  scroll naturally with the page.
- 960–1439px: source left; annotation followed by decision on the right, with natural
  heights. No 42%/58% row split or nested reading scrollers. <960px uses single-column
  source → annotation → decision page flow.
- Complete quotes, Notes, explanations, expanded prior judgments and window remarks
  are never height-capped. Textareas grow. Help remains initially open and collapsible.
- P/F follows the current criterion heading. Desktop previous/next/completion lives in
  a sticky bottom action bar with trailing flow space; focused fields clear both the
  toolbar and actions. On narrow screens actions remain in ordinary flow.
- Window remarks start collapsed and show “已填写” when present; U expands/focuses them.
  R/M reveal their fields in the page. Switching cases reveals annotation navigation;
  switching criteria scrolls only when the target heading is outside the usable view.
- Every field has one DOM control. Reflow does not duplicate handlers or discard drafts.
  Open Coding keeps its previous layout and density/omission behavior.

`q1-mixed-judgment/3`, form/hash, caches, explicit outcomes, completion and prior-view
save gates are unchanged. Existing 3.0/3.1 journal prefixes remain intact when appending 3.2.

## Keyboard interaction (annotator 3.2)

| Key | Action outside text inputs |
|---|---|
| P / F | Current criterion pass / fail; stay, without focusing reason |
| R | Current criterion reason; in summary, uncovered reason when enabled |
| Enter | Judged criterion → next step; last criterion → summary; summary → complete/stay |
| Shift+Enter | Summary only: complete/save, then next case within this window |
| [ / ] | Browse previous / next step without changing judgment |
| 1–4 | Select Note criterion; Highlights use 1–3 |
| Shift+number | Toggle current explanation; select and open another criterion's explanation |
| V | Current criterion's first configured verification flag, if present |
| 5/6/7 | Summary: Note tags (teacher tone, redundancy, too terse) |
| 0 / S / B | Summary: uncovered / permitted star / saved prior judgment |
| M / U | Summary case remarks / expand and focus window remarks |
| ↑ / ↓, ← / → | Previous/next case, previous/next window; existing boundaries |
| J / K | Source scrolling; narrow screens scroll the page |
| Shift+J / K | Page scrolling in all modes; no nested review scrolling |
| ? / Esc | Shortcut help / exit input or help, keeping the current step |

Enter on an unjudged criterion prompts P/F and does not assume pass. New cases start
at the first criterion; revisiting and reloading restore each case's step and draft.
Single actions ignore held repeats; J/K scrolling still repeats. Text-field Enter
inserts a newline, Esc keeps the unconfirmed draft, and IME/229 or Cmd/Ctrl/Option
input is not intercepted. Native button/link/disclosure Enter, Tab and checkbox Space
remain available. Open Coding retains P/F, density 1/2/3, omission O and existing keys;
rubric mode still disables omission O.

Summary completion is shared by button and keyboard. Both browser and disk must
acknowledge before advancing. It stays at the last case; use → to change windows.
Missing connections, failed writes or pending amendments prevent advancement.
Concurrent completion and unchanged revisions do not duplicate submissions. Pending
work cannot advance or steal focus after changing case/window/step (including away
and back), input, focus or opening help. Save failures remain visible with retry controls.

Bindings use configured order (first four criteria 1–4, first five tags 5–9, first
criterion verification flag V). Other configured controls remain reachable by keyboard.
Published rubric and frozen form bytes are unchanged; keys live only in the UI.

The old-judgment toggle unlocks only when the current completed assessment is saved in
both browser and file. Failed/slow writes or a pending amendment keep it locked. Opening
it first appends a monotonic exposure revision, waits for both save receipts, then displays
only the same anonymous mark's latest baseline judgment/reason/remarks. Navigating hides
the panel again. Group identity is never revealed. This is interaction-level protection
from accidental priming, not encryption of the local baseline file.

Reports pair each anonymous marginalia ID with the latest completed revision in each
journal. JSON and Markdown contain the note body or Highlight quote, exact anchor,
old/new outcomes, old reason, failed criteria, tags/flags, historical overall new reason,
criterion assessments and independent reasons, uncovered reason, remarks, and
exposure/first-completion revision metadata. `assessment_mode` distinguishes `stepwise`
from `legacy_whole_case`; legacy `criterion_assessments` is null. The `assessments` list
and Markdown detail section cover every completed case, including unchanged outcomes.
They group old-pass/new-fail, old-fail/new-pass,
and rubric-uncovered (which may overlap a disagreement group). Missing new assessments
remain incomplete, not passes; unmatched baseline labels are counted separately. Reports
do not read blind keys or group maps and do not analyze omissions or window notes.
Rubric examples **are included** in this human rejudgment report. The example exclusion
list still applies to future LLM-judge agreement evaluation.

## Frozen form evolution and checks

Do not edit q1-v0 Markdown, its registry or the released form in place. A later rubric/form
gets a new file and identity in `form-releases.json`, plus an added frozen lock. Criterion
and tag IDs/labels/help, flags and supported policies are data-driven; registering a v1
form within this protocol needs no UI-code change. A protocol expansion (for example a new
annotation type or omission review) requires a separate implementation decision.

```sh
node --test tools/q1-annotator-storage.test.cjs tools/q1-annotator-keyboard.test.cjs tools/q1-rubric-form.test.cjs
.venv/bin/python -m pytest tests/test_q1_rubric_form.py tests/test_q1_rubric_review.py tests/test_q1_comparison_stats.py tests/test_iteration_provenance.py -q
.venv/bin/python scripts/check_iteration_provenance.py
```

Deferred, by owner instruction: reconcile mixed-mode unlimited omissions with rubric
maximum two. This pass neither changes the original omission logic nor re-labels omissions.
