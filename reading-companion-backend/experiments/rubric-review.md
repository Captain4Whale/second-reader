# Rubric-driven Q1 rejudgment protocol

This workflow rejudges existing anonymous mixed annotations without changing source
outputs, prompts, the reader mechanism or historical judgments. It does not run models.
The owner-approved first form is `rubric/q1-v0.form.json`, registered separately in
`rubric/form-releases.json` and frozen by `experiments/frozen.json`. Existing rubric
publication entries and q1-v0 Markdown remain immutable. Add a new form version for
later changes; criterion/tag IDs, labels, help and supported policies are configuration,
not annotator code. Form text contains rules only, never identifiable rubric examples.

## Owner-authorized differences from q1-v0 Markdown

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
unchanged. JS/Python accept `/2` rows from annotators 2.3–2.6, 3.0 and 3.1 (for a legacy
exposure-only revision); `/3` accepts 3.0 and 3.1. `/1` and single-group Open Coding retain
their previous validation, including nonempty failure reasons, and remain separate.
First completion must precede prior-judgment exposure; exposure cannot revert. Both
first completion and later amendments remain inspectable.

## Prepare, annotate and compare

Run from `reading-companion-backend/`:

```sh
.venv/bin/python scripts/q1_rubric_review.py prepare "$ORIGINAL_BLIND_BATCH" --output state/q1_rubric_reviews/NEW_SESSION
.venv/bin/python scripts/q1_rubric_review.py report state/q1_rubric_reviews/NEW_SESSION --output state/q1_rubric_reviews/NEW_REPORT
```

Output paths must be new directories under ignored backend `state/`; neither command
overwrites an existing destination. Preparation checks the original bundle and baseline,
then copies exact `mixed.json`, exact registered `rubric-form.json`, and an exact
`open_coding.snapshot.jsonl`. It creates a fresh empty `judgments.jsonl`, a hash-bound
`annotation-context.json` and an operator-only `preparation.json`. Private group keys and
canonical batch provenance are not copied. A prepared baseline stays fixed even if the
original journal later gains revisions; prepare another session to choose a newer baseline.

Open the prepared directory using annotator 3.1's “打开批次文件夹”. The HTML requires
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
for the current step. One criterion is visible at a time. Help opens by default and uses the remaining desktop decision space with its own
scrollbar; narrow screens retain the 240px / 20vh limit. Optional reasons start at
two lines and long reasons scroll inside the field. N2 verification is inside N2. The summary contains tags, star, uncovered
and its optional reason, case remarks and historical judgment. Even after one failure,
judge every remaining criterion before confirmation. Window notes remain separate.

## Layout (annotator 3.1)

- At ≥1440 CSS pixels, source / current annotation / decision use 44% / 26% / 30%
  of the available width (excluding gaps). Each panel uses the actual viewport space
  below the measured toolbar. Source text, complete quotes/Notes and long explanations
  remain available through local scrolling. Source typography is unchanged.
- At 960–1439px, source stays left; annotation and decision stack on the right with
  local scrolling. Previous/next criterion and completion remain in the decision's
  fixed bottom action area. Short desktop viewports omit the duplicate decision heading.
- Below 960px, source → annotation → decision use natural page scrolling.
- Window progress is at the annotation panel's bottom; window remarks start collapsed.
  “已填写” identifies an existing note. **U** opens and focuses the same note field.
  **R/M** reveal the appropriate decision field in its own scroller. Each field has one
  DOM control; changing mode/size retains drafts and does not bind another handler.
- Summary-only tags, star, remarks and gated prior viewing retain the 3.0 workflow.
  Expanded prior text scrolls locally; the completion action stays visible on desktop.
  Open Coding retains its previous layout, density/omission behavior and page scrolling.

This is a presentation/version change only: `q1-mixed-judgment/3`, registered form/hash,
cache identities, explicit criterion outcomes and completion/save gates are unchanged.
Existing 3.0 journals can be read and receive new 3.1 revisions without prefix edits.

## Keyboard interaction (annotator 3.1)

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
| Shift+J / K | Desktop review: decision scrolling (explanation when the whole form already fits); narrow screens and Open Coding: page scrolling |
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
