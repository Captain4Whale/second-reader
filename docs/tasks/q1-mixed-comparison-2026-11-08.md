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
- Independent statistics implemented. 20 focused Python tests passed (data/contract,
  statistics and existing provenance); actual browser export validates at 16 revisions.
  Per-rubric/person latest revisions, null denominators, exact prefix snapshots, flag-only
  judgments, omission deletion and cross-window full-anchor hits are covered. No real A/B
  generation artifacts existed at audit time; synthetic fixtures are explicitly labelled.
- Browser verification used local persistent Node/Playwright with cached headless Chromium;
  the skill's provided JS tool denied local connections, and headed screenshots timed out.
  No packages or global settings changed. Screenshots remain in ignored comparison state.
- `make agent-check` passed, including 55 Annotation Pack tests and product/API/frontend
  contract checks. Its 17 historical traceability warnings remain; the additional history
  reminder is due to the new AGENTS doc-routing pointer (reason below). Provenance checker
  validates both original dev journal prefixes. The two pre-existing run-ledger file
  hashes still match the pre-task state and are excluded from commits.

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

## Next

Follow-up: annotator 2.1 restores H/N type labels in mixed navigation. Blinding applies
to group/model/prompt provenance, not to Highlight/Note type. Existing 2.0 journals are
accepted unchanged by the UI and statistics; only new appends carry version 2.1.
Validated with 14 annotator storage tests and 12 statistics tests, including old 2.0
records followed by 2.1 revisions. No diagnostic content or group mappings were opened.

The separately assigned Digest rerun tool should implement the documented output contract.
Finish real A/B mixed annotation before resuming side-by-side, preferences and reveal.
No real quality scores were computed and no baseline pass-rate field was filled.
Private acceptance index: `reading-companion-backend/state/q1_comparison/acceptance.json`.
It identifies the synthetic and converted-dev bundles, browser screenshots and synthetic
statistics snapshot without putting copyrighted source or annotation content in Git.


Follow-up: annotator 2.2 fixes toolbar flicker during text entry. Save-status strings
changed the flex layout on each save receipt, moving buttons by approximately 76 px
at a 1280 px viewport; progress rendering also rewrote unchanged navigation nodes.
The save-feedback area now has a stable width, and unchanged text/attributes are
left intact. Autosave timing, IME composition handling and journal semantics are unchanged.
The UI and statistics accept 2.0/2.1/2.2 mixed records.

Validation: 15 annotator storage tests and 13 statistics tests passed, including a
regression for unchanged progress during typing and revisions across all three versions.
An isolated browser with synthetic data and an OPFS test journal verified English typing,
Chinese IME composition/commit, retained focus, and successful file persistence. Across
English and IME checks at 1280 px and a narrow 390 px layout, toolbar button geometry
remained constant and navigation nodes were not rewritten. Screenshots are private under
`reading-companion-backend/state/q1_comparison/typing-fixed-{desktop,mobile}.png`.
No real judgments, diagnostic content or group mappings were opened or modified.
