# Memory Quality Evidence Report Contract

Purpose: define the durable writing contract for Memory Quality evidence reports.
Use when: generating or regenerating Long Span vNext Memory Quality audit docs.
Not for: changing scores, changing judge prompts, or changing runtime state.
Update when: the Memory Quality evidence surface or required audit layout changes.

## Why This Contract Exists

Memory Quality reports are meant to let a human reviewer answer two questions in one pass:

- What did the reader have in memory at this probe?
- Was that memory good evidence of continuous reading quality?

The report should not make each run invent its own audit shape. Future renderers should follow this contract unless the evaluation method itself changes.

## Required Report Shape

Each Memory Quality evidence audit should include:

- `README.md`
  - run ids and source runs
  - score scale
  - state-map summary
  - window links
  - post-eval action ledger link when the audit belongs to a diagnostic run
- one window report per reading window
  - full runtime state map
  - how to read probe snapshots
  - source evidence model
  - probe source map
  - one section per probe
- one full source document per window
  - 5 inline probe markers
  - no repeated full source-so-far copies inside probe sections
- runtime appendix per window
  - links to raw runtime artifacts
  - file purpose and top-level structure
  - do not duplicate raw JSON wholesale unless a specific audit requires it

## Probe Placement Explanation

Probe positions are fixed progress checkpoints, not semantic target selections.

Each report must explain:

- schedule: `20% / 40% / 60% / 80% / window end`
- `target_sentence`: the mathematical target by sentence count
- `actual_captured_sentence`: the end of the first completed read unit that crossed the threshold
- no probe-only read step is inserted
- the probe may be slightly later than the mathematical target because reading units are indivisible for capture

## Source Evidence Rules

- Put the complete window source in exactly one `source_texts/<segment_id>.md`.
- Insert 5 probe markers into that source document.
- In each probe section, show only a short deterministic orientation excerpt plus a link to the source marker.
- Do not repeat the full source-so-far slice in every probe section.
- If a structural signal is known to be high risk for review, show it under `Structural Signals To Check`; make clear it is an audit focus, not a hard gold answer.

## State Evidence Rules

The scoring evidence remains the probe-time snapshot, not the final runtime dump.

Each window report must explain the difference:

- `probe snapshot`: the state evidence captured at that checkpoint and used for scoring
- `full runtime dump`: the final complete runtime state for learning, debugging, and mechanism inspection
- final runtime dump cannot replace probe-time state evidence because it is captured after later reading has changed state

Each probe should show:

- score dimensions and judge reason
- raw snapshot link
- state layer counts
- readable state digests
- recent orientation context

## Recent Moves Naming Rule

`Recent Moves` is a compact projection from runtime `move_history`, not the raw full move history.

Current renderer behavior:

- source: `move_history.moves[-3:]` at the probe snapshot time
- kept fields include move id, move type, route reason, source sentence, target anchor, and target sentence
- dropped fields include full file-level metadata and older moves outside the recent window
- the text should be labeled `move reason`, not `statement`
- `Recent Moves` is local continuity / audit evidence, not long-term memory

Do not label a move reason as `statement` in generated Memory Quality reports. `statement` is reserved for memory-like items such as active-attention items, concepts, threads, anchors, or reactions.

## Current-State Naming Rules

New reports should use current mechanism vocabulary:

- `active_attention`, not `working_state`
- `active_items[]` with `attention_tags[]`, not fixed `open_questions / live_tensions / live_hypotheses / live_motifs`
- `reading_impression`, not `unit_delta`
- `memory_uptake_ops`, not `implicit_uptake_ops`

Historical reports may retain older field names because they reflect the code that produced them. New report generators should not reintroduce those names as current truth.

## Minimum Checks

Before closing a generated Memory Quality evidence report, check:

- 5 window reports exist.
- 25 probe sections exist.
- 5 full source documents exist.
- Each full source document has 5 probe markers.
- Probe sections do not repeat full source-so-far blocks.
- Every probe links to raw snapshot JSON, source marker, source landmark, and runtime appendix.
- `Recent Moves` blocks say `move reason`, not `statement`.
- The report states that probe placement is progress-based, not semantic.
- The report states that final runtime dump cannot replace probe-time snapshot evidence.
