# Q1 mixed comparison

Scope approved: data layer, mixed blind annotation and independent statistics (steps
1, 2, 4). Side-by-side, preferences and reveal are deferred until A/B annotation.
No prompt/mechanism edits, model calls or push. Branch `codex/q1-mixed-comparison`.

## Progress

- Data layer implemented; 5 focused offline tests passed. Synthetic two-group bundle:
  2 windows / 5 marks, including one boundary-crossing mark assigned only once.
- Real dev baseline converted without copying judgments: 67 windows / 110 marks,
  1 group, no unassigned marks. Original 605 journal rows remain unchanged.
- Fixed-history rerun output contract is in
  `reading-companion-backend/experiments/comparison.md`; the producer is a separate task.
- Mixed UI and statistics are in progress. No real A/B generation artifacts existed
  at audit time; synthetic fixtures are explicitly labelled.

## Validation boundary

Only dev source/judgment files are inspected. Holdout is not opened. Pre-existing local
run-ledger changes are left untouched. Generated text, comparisons and mappings live in
ignored backend state. Public tests use authored synthetic text only.

This is an offline workflow extension under existing Q1 provenance authority, not a
mechanism or product-direction decision; no new decision-log entry is needed.
