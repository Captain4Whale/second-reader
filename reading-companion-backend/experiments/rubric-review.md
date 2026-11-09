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
