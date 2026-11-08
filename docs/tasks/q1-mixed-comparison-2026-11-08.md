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
- Mixed UI 2.0 implemented; 14 storage/projection tests passed. Synthetic browser flow
  completed all 5 marks, exported JSONL and restored all decisions on reload. Crossing
  marks show full quotes with clipped highlights. Omission edit/remove, reason drafts,
  flags, keyboard navigation and density suppression verified. Desktop 1600x1000 and
  narrow 390x844 inspected; no horizontal overflow or clipped primary controls.
- Real converted dev (67/110) and original Bovary batch (36/40) both load in the browser.
  Actual historical journals validate with 303 + 302 rows. Highlight null bodies are
  normalized to empty strings only in the new projection; original data stays unchanged.
- Statistics are in progress. No real A/B generation artifacts existed at audit time;
  synthetic fixtures are explicitly labelled.
- Browser verification used local persistent Node/Playwright with cached headless Chromium;
  the skill's provided JS tool denied local connections, and headed screenshots timed out.
  No packages or global settings changed. Screenshots remain in ignored comparison state.

## Validation boundary

Browser QA inventory: import synthetic mixed and legacy dev; verify no provenance or
density controls, one current anchor only, complete crossing quote + clipped highlight,
pass/fail/reason draft, star/verification toggle, notes, omission save/edit/remove,
window/mark navigation, completion without density, export and reload recovery. Inspect
desktop and narrow layouts. Off-path checks: invalid blind fields and a corrupt/forked
journal must reject without changing the active batch; a fail without a reason remains
a draft across navigation/reload. Storage tests cover permission loss and write races.

Only dev source/judgment files are inspected. Holdout is not opened. Pre-existing local
run-ledger changes are left untouched. Generated text, comparisons and mappings live in
ignored backend state. Public tests use authored synthetic text only.

This is an offline workflow extension under existing Q1 provenance authority, not a
mechanism or product-direction decision; no new decision-log entry is needed.
