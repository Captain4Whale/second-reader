# Q1 rubric v3.4 Note form

Status: done. Scope: implement the owner-approved Note form and isolated session protocol.
No sampling, generation, old-type conversion, Highlight form, statistical adapter or scoring snapshot.

## Implementation

- Immutable `q1-v3.4.form.v1` publication and protocol validation: `b870d6e`.
- Dedicated local entrypoint: `reading-companion-backend/scripts/q1_note_review.py`.
- Source packaging: `scripts/q1_note_context.py`; durable state/reader: `scripts/q1_note_session.py`.
- UI: `tools/q1-note-annotator.{html,css,js}`. Old v0/v1 entrypoint and forms are unchanged.
- Canonical operator/schema documentation: [rubric review](../../reading-companion-backend/experiments/rubric-review.md#published-v34-note-review-2026-11-15).

The prepared formal session is
`reading-companion-backend/state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v3.4`.
It contains all 51 Notes from the existing 16-window, two-book DIAG-001 bundle,
with an empty formal judgment journal. Preparing a display session did not resample
or change the original 81-annotation bundle or its Highlights.

UI fixtures and browser evidence are isolated at
`reading-companion-backend/state/q1_rubric_reviews/qa/v3.4-20261115/`.
Three existing Notes were exercised: civil/church marriage (pass), insurance adverse
selection (N1 pass, difficulty veto), and the wedding-ring interpretation (N1 fail).
These agent-operated test judgments are not human gold or evaluation results.
The first case also has a later test revision for validation/flag-clearing checks;
unit-note exclusion was toggled on then off without rewriting annotation rows.
`example-record.json` contains a complete test record with difficulty amendment history.

## Validation

- 128 Python tests pass across new form/session, old form/review, comparison/scoring
  and iteration-provenance tests.
- 48 existing Node storage/keyboard/form tests pass; the old HTML/JS are untouched.
- Ruff check and JavaScript syntax checks pass.
- Workspace traceability check exits successfully with 18 existing warnings about
  historical evidence paths and duplicate decision IDs; none concern this new task.
- History check gives its warning-only reminder for the runtime-document update;
  the concrete reason for leaving the decision log unchanged is recorded below.
- Published-form/rubric hashes and old frozen registrations verified against the
  pre-task Git base. `experiments/scorings.jsonl` and `q1_scoring.py` remain unchanged.
- Read-only context verification covers all 51 DIAG Notes: exact anchor matches,
  chapter-bounded following text, and 16 resolved note-link occurrences in the relevant
  prefixes. No ambiguous/conflicting note resolutions were encountered. Absence of a
  resolved link is reported as unresolved, not proof that the book has no notes.
- Browser checks: first-choice mandatory, first-impression lock across reload, stage
  gating, three-way difficulty and correction, auto/manual uncertainty, N1 conditional
  required fields, independent spoiler step after N1 failure, following expand/collapse,
  uncovered reason and tag/star clearing, original-note unresolved display, unit-note
  exclusion and reversal, append-only submission, reload restore and navigation.
- Layout inspected at 1440×1000 and 390×844 and a native browser context. Natural page
  scrolling preserves long content; no horizontal overflow or clipped decision controls
  found in inspected states. Screenshots remain in the private QA directory.

## Decisions and limitations

The rubric owns options/thresholds and the annotation guide owns sequence. “其他”
failure is already in rubric 2.2. The fourth following-use branch is owner-approved
and does not replace the independent spoiler judgment. The anchor endpoint means the
end of the complete selected source range, including same-paragraph clipping.

Difficulty final choice controls veto/statistics; original choice and every from/to
transition remain available. Uncertainty sources are distinct, and automatic difficulty
uncertainty is removed when its triggering choice changes while manual uncertainty
stays. Following text cannot go beyond the chapter. Unresolved original notes do not
block; ambiguous source/target resolution stops for owner review.

Long original passages make source/decision navigation slower; added “定位锚点” and
“返回判定”. N1 help is long and defaults collapsed. The form cannot verify whether a
human really read once or knows later chapters. Timing records visible-page interaction,
not cognitive reading time. DIAG material has prior exposure; this UI cannot restore
an unseen blind experiment. Future freeze thresholds are not invented here.

The task uses two commits as requested. Generated material already lies under the
existing ignored backend `state/` boundary, so no additional ignore rule is needed.
No decision-log update: this implements the already-published rubric and approved
annotation protocol, without changing product direction or the reading mechanism;
its decisions are recoverable from the frozen form, operator contract and this record.
