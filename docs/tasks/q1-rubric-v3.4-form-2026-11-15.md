# Q1 rubric v3.4 Note form

Status: done; initial service-based UI superseded by the offline follow-up below. Scope: implement the owner-approved Note form and isolated session protocol.
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


## Offline integration follow-up (annotator 3.3)

The owner required continuity with the original offline tool after using the separate UI.
The current entrypoint is `tools/q1-annotator.html`: same directory picker, IndexedDB
store and tab lock. Existing 3.2 stylesheet/layout is reused at runtime for v3.4;
legacy controls remain isolated from v3.4 controls. Both modes share prefix-preserving
journal append I/O. Tool version advances to 3.3; published forms and their hashes,
rubric versions and existing records are not changed. Legacy version readers accept
3.3 while the Note journal keeps `q1-note-judgment/1`.

Browser drafts replace ongoing service progress writes; existing progress is read-only
input. Locks, amendments, timing, uncertainty sources, chapter cutoff and statistics
fields retain the approved semantics. `serve`/`launch` now open the offline entrypoint;
the old standalone Note HTML provides an explicit link to it. No migration of formal
journals or cache entries is performed. No sampling, conversion or scoring work.

QA inventory/evidence is private under `state/q1_rubric_reviews/qa/offline-3.3/`.
Node protocol/storage tests run the new implementation, in addition to legacy tests.
Browser cases use isolated directory handles and copied Notes; no formal record writes.
This change restores the existing tool architecture; it does not change rubric rules
or the reading mechanism, so no new mechanism decision-log entry is needed.

Offline follow-up validation:

- 67 Node tests cover the new browser protocol and storage plus legacy keyboard/form/
  storage regressions; 128 focused Python tests pass. Browser-written test judgments
  are accepted by the existing Python Note reader, without schema conversion.
- Three existing Notes exercised with real UI input: pass, difficulty correction veto,
  and N1 failure with subsequent veto steps. P/F, Enter, focused-button Shift+Enter,
  read-only step browsing, help, source reveal/collapse, R input, multiline text,
  simulated Chinese composition, reload/close-and-reopen recovery, injected disk
  failure/retry, and switching back to the original Open Coding mode were checked.
- Browser fixtures use real isolated OPFS directory handles through the folder button;
  the macOS native directory chooser itself was not automated. The actual file:// HTML
  entry was separately opened and its folder control verified enabled. A temporary
  static test server supplies only assets for OPFS automation; no backend endpoints
  are used by the new UI. IME composition is simulated, not an OS candidate-menu test.
- Visual checks at 1600×1000, 1100×800, 390×844 and a native window. Corrected medium/
  narrow sticky-panel overlap and heading navigation under the toolbar. Long help and
  reasons flow naturally, no horizontal overflow in the inspected narrow state.
- Formal judgments remain empty. Existing formal `progress.jsonl` is 109880 bytes,
  SHA-256 `d7123d1a7c24a7c04392c6b57fe23bff236e04f22b8201c58c3d1db1264498ec`;
  these existing user drafts were not rewritten or removed.
- Workspace traceability retains its existing warnings. Runtime-doc history reminder
  is addressed by the concrete no-new-mechanism-decision rationale above.

## Desktop usability follow-up (annotator 3.4, 2026-11-17)

Tool 3.4 retains the frozen form and record schema. Decision fields and uncertainty
flags now precede collapsible full guidance; per-step expansion preferences stay in
local browser UI storage, outside judgments. The decision area can reveal the full
current Note, the header/session controls are compact, and cases open at their anchor
without revealing following text. Read-only outcomes use Chinese and return controls
name the destination. Pending steps remain disabled after a save. Old journal versions,
including 3.3, remain readable; the comparison reader only expands its tool-version
allowlist, with no new statistics or snapshot logic.

Acceptance targets PC at normal usage sizes (100% and the owner's 125% zoom), not
mobile annotation. Native Edge Computer Use verified three/two-column layouts,
full-Note disclosure, read-only first impression, explicit return target, anchor
positioning, help preference across refresh, M/Esc/Enter and step-5 restoration with
synced status. Test interaction used only the existing isolated `qa/offline-3.3/session`;
no formal judgment was entered or submitted. Screenshots are in private
`state/q1_rubric_reviews/qa/offline-3.4/` (before, medium, wide, supplementary zoom).
This was a focused usability check, not a full accessibility certification.

Validation: 73 Node tests and 111 focused Python tests pass; immutable prompt releases
and iteration provenance checks pass. Workspace agent checks pass with existing
historical traceability warnings and the existing scoring evidence-not-verified notice.
No new architecture decision is introduced: this is a usability correction within the
already-approved offline approach, so the decision log is unchanged.


## New validation batch connected (2026-11-17)

The owner requested the completed new batch, not DIAG-001 reannotation. Source is
`Q1-RUBRIC-V34-VALIDATION-001-RESULT-001` in the separate worktree
`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion`, commit
`fcad1a346893`. Its branch has not been merged as part of this handoff.

The existing fixed-history exporter verifies the registered unit-set hash, each of
26 result hashes, packet hashes and exact source anchors. Window metadata comes from
the accepted packets; the existing comparison builder assigns opaque identities and
retains all 46 Notes and 10 Highlights. The existing Note session preparer creates
chapter-bounded contexts and a seeded mixed-book order (20261115). Counts verified:
18 Bovary Notes and 28 Sapiens Notes. Original-note resolution: 10 cases resolved,
36 unresolved; no ambiguity raised. No model calls or original-result edits.

Private paths relative to backend:
- Active formal session: `state/q1_rubric_reviews/Q1-RUBRIC-V34-VALIDATION-001-q1-v3.4/`.
- Source export, canonical bundle, blind identity map and receipt:
  `state/experiments/Q1-RUBRIC-V34-VALIDATION-001/annotation-handoff/`.
- `receipt.json` binds the source/result registration, unit set, session manifest,
  randomization and frozen stability receipt without disclosing selection identities.
  The blind key preserves source/unit/original marginalia IDs for later stability use.

Native Edge opened this session and displayed `1 / 46`, `0 / 46`, synchronized,
first impression unselected. No judgment was entered by the agent. DIAG-001 and QA
sessions remain separate. This is an artifact handoff using existing validated code;
no form/schema change, score snapshot, quality assessment or architecture decision.
