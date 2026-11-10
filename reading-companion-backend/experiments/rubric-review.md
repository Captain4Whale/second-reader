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

`q1-mixed-judgment/2` retains anonymous batch/window/mark identity, exact content/range,
human/rubric identity, timestamp and append-only per-journal revision. It adds:

| Field | Contract |
|---|---|
| rubric_form_version / rubric_form_sha256 | Registered immutable form identity |
| review_session_id | Isolated rejudgment session; never a group or run identity |
| failed_criteria | Unique configured criterion IDs for this annotation type |
| tags | Unique configured tag IDs; do not cause failure |
| criterion_flags | Configured criterion → flag → boolean; N2 has needs_verification |
| rubric_uncovered | Owner considers this a failure not covered by criteria |
| review_completed | true for persisted annotation assessments; drafts stay in browser |
| prior_judgment_seen | Whether historical judgment has been revealed; cannot revert |

No failed criterion and no uncovered flag means pass; otherwise fail. `judgment` is a
checked derived field. `needs_verification` mirrors configured criterion flags without
causing failure. Stars require pass. Merely opening a mark, toggling a control or moving
away never confirms it. Explicit completion distinguishes an unchecked valid pass from
an untouched form. Subsequent assessments append revisions. `unit_note` remains supported
with null assessment fields; omission records are not supported in this mode.

New journals cannot mix legacy records, people, rubrics, forms or review-session IDs.
Old q1-mixed-judgment/1 and legacy single-group journals keep their previous validation
rules, including nonempty failure reasons. New parsing does not rewrite old rows.
The browser and Python validators both check choices, mirrors, identities and exposure
ordering. First completion must precede viewing the old judgment; exposure stays true
in later revisions. Both first completion and later amendments remain inspectable.

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

Open the prepared directory using annotator 2.4's “打开批次文件夹”. The HTML requires
the adjacent `q1-rubric-form.js`; keep both files together. The UI reads only the mixed
projection, context, form, baseline and new result journal. Browser drafts and remembered
handles are keyed by batch, annotator, rubric, form and review session. Old cache keys
remain intact. Restoring or navigating preserves unfinished drafts without confirming them.
If the HTML was already open before an update, refresh it first. The header displays
the loaded annotator version and current rubric/mode. Opening a folder does not load new
HTML code. Failed folder loads keep the prior batch visible and name the selected folder
and missing required file; they do not silently create missing review resources or import
old labels. Selecting only the JSON file does not load the companion review context/form.
Checkboxes preview pass/fail; “完成本条” confirms it. Reasons and remarks are optional.
Stars require pass. N2 “待核实” and tags do not fail a mark by themselves. P/F/O and
source-selection omission actions are disabled in review; S and configured verification
V remain available. Window notes remain separate optional records.

The old-judgment toggle unlocks only when the current completed assessment is saved in
both browser and file. Failed/slow writes or a pending amendment keep it locked. Opening
it first appends a monotonic exposure revision, waits for both save receipts, then displays
only the same anonymous mark's latest baseline judgment/reason/remarks. Navigating hides
the panel again. Group identity is never revealed. This is interaction-level protection
from accidental priming, not encryption of the local baseline file.

Reports pair each anonymous marginalia ID with the latest completed revision in each
journal. JSON and Markdown contain the note body or Highlight quote, exact anchor,
old/new outcomes, old reason, failed criteria, tags/flags, new reason and remarks, and
exposure/first-completion revision metadata. They group old-pass/new-fail, old-fail/new-pass,
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
node --test tools/q1-annotator-storage.test.cjs tools/q1-rubric-form.test.cjs
.venv/bin/python -m pytest tests/test_q1_rubric_form.py tests/test_q1_rubric_review.py tests/test_q1_comparison_stats.py tests/test_iteration_provenance.py -q
.venv/bin/python scripts/check_iteration_provenance.py
```

Deferred, by owner instruction: reconcile mixed-mode unlimited omissions with rubric
maximum two. This pass neither changes the original omission logic nor re-labels omissions.
