# Ingest Next-Unit Optimization Design

Purpose: collect concrete optimization points discovered while reviewing
`attentional_v2` Ingest next-unit selection reports.
Use when: turning a reviewed report insight into a candidate prompt/schema/runtime
change for Ingest.
Not for: the live prompt source of truth, formal evaluation scoring, or Unit
Memory retrieval policy.
Update when: a new Ingest next-unit optimization point is accepted for design,
implemented, rejected, or superseded.

Status: living design note. This document is organized by optimization point so
one accepted point can be reviewed or extended without reopening every later
idea. Individual points below may be candidate, implemented, rejected, or
superseded.

Current live baseline:
- Ingest prompt: `attentional_v2.ingest.v17`
- Promptset: `attentional_v2-phase6-v67`
- Live boundary contract: `unit.end_paragraph_n` + `unit.end_at`
- Live audit contract: `preview_partition[]`, with `preview_partition[0]`
  matching `unit`
- Live recall contract: prior-reading recall intent is expressed only through
  `retrieve_unit_memory` action-tool args; final Ingest output does not carry
  `memory_recalls[]`
- Authoritative runtime coordinate: paragraph-char `SourceSpan` /
  `source_span_id`, derived by runtime after resolving the model boundary
- Related decisions: `DEC-116`, `DEC-117`, `DEC-118`, `DEC-120`, `DEC-121`,
  `DEC-127`
- Related living pattern: `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md` entry 19
- Related upstream source-substrate design: `docs/implementation/new-reading-mechanism/source-normalization-design.md`

## Upstream Source Normalization Boundary

Some next-unit failures are caused by source-stream hygiene rather than by
Ingest boundary selection. Footnote/endnote clusters, layout noise, and repeated
source artifacts should be handled by import-time Source Normalization before
Ingest runs. The accepted design keeps raw paragraph coordinates canonical,
attaches richer normalization metadata to existing paragraph records, and lets
Ingest read only the normalized mainline stream. This is not an Ingest prompt
change and is not implemented in the live parser/runtime yet.

## Optimization Point 1: Preview Partition Audit Map

### Status

Implemented as the live Ingest v15 prompt/schema/runtime audit contract on
`2026-06-13`. Historical A/B report packages were not regenerated in this
slice.

### Source Insight

The June 2026 rolling A/B review found that the window-partition Ingest prompt
often selected a better first unit because it did not stop at the first locally
plausible paragraph boundary. It looked across the visible preview, inferred
where later text continued the same semantic move or began a new move, and then
committed only the first unit.

The prior v14 live prompt already asked for this whole-window conceptual
partition:

- consider the whole visible window first
- conceptually divide the window into consecutive reading units
- commit only the first unit
- treat the rest of the window as lookahead context only

The v15 live output now exposes that provisional map through
`preview_partition[]`, while keeping only the first committed boundary
authoritative for runtime cursor movement and Digest.

### Design Goal

Make the model's whole-preview semantic map visible for audit while preserving
the current runtime control shape.

This serves two purposes:

1. Improve first-unit selection by making the model explicitly form the
   whole-window partition it is already asked to use.
2. Improve reviewability by showing how Ingest understood every visible part of
   the preview at the moment it chose the first unit.

### Non-Goals

- Do not make Ingest digest future text.
- Do not let later preview partitions become runtime input for Digest.
- Do not expose `preview_partition[]` as a frontend/public API contract in this
  slice.
- Do not change Unit Memory recall semantics or `retrieve_unit_memory` behavior.
- Do not ask the model to output raw `char_offset` values.
- Do not create one partition per paragraph unless the paragraphs truly are
  separate semantic units.
- Do not add per-partition long rationales that turn Ingest into a second
  Digest call over future units.

### Conceptual Contract

`unit` remains the runtime contract.

`preview_partition[]` is an audit/planning contract:

- It is the model's provisional map of the visible preview.
- It must cover the visible preview from the current cursor through the preview
  tail in order, with no intentional gaps or overlaps.
- `preview_partition[0]` must exactly match `unit`.
- Later partitions are future source text, not already-read text.
- Later partition titles are lightweight understanding evidence for reviewers,
  not memory, reactions, summaries, or Digest results.

### Prompt Posture

The `Instruction` wording should stay reader-shaped. It should not open with a
mechanical schema instruction such as "output a partition array." The point is
to preserve Ingest as a reader-like planning step:

```text
Before committing the next unit, browse the whole visible preview as a reader.
Notice where one local reading movement gives way to the next.

Form a provisional map of the visible preview as consecutive semantic units.
Give each provisional unit a short title that names what that unit is doing in
the reading.

Use that whole-preview map to choose the first unit well. Only the first unit is
committed for Digest; later units are lookahead context and have not been read
closely yet.
```

The `OutputContract` should then be strict and mechanical:

- required fields
- boundary syntax
- first-partition equality
- title requirements
- runtime/audit authority

This split keeps the model in a reader/planner posture while keeping the output
validatable.

### Candidate Output Shape

Recommended minimal candidate:

```json
{
  "unit": {
    "end_paragraph_n": "8",
    "end_at": "paragraph_end"
  },
  "preview_partition": [
    {
      "title": "悉达多被众人爱戴的外部完美形象",
      "end_paragraph_n": "8",
      "end_at": "paragraph_end",
      "status": "complete"
    },
    {
      "title": "悉达多内心不满的转折开始",
      "end_paragraph_n": "12",
      "end_at": "paragraph_end",
      "status": "complete"
    },
    {
      "title": "沙门出现并触发离家决定",
      "end_paragraph_n": "22",
      "end_at": "paragraph_end",
      "status": "open_tail"
    }
  ],
  "reason": "The first unit ends at paragraph 8 because paragraph 1-8 completes the external portrait of Siddhartha as beloved and apparently perfect; paragraph 9 begins a new inward turn with '可是'.",
  "memory_recalls": []
}
```

Field rules:

- `unit`
  - unchanged live boundary object
  - remains the only authoritative committed next unit
- `preview_partition`
  - non-empty array
  - first item must match `unit.end_paragraph_n` and `unit.end_at`
  - ordered by source position
  - covers the visible preview from the current cursor through the visible tail
- `title`
  - short local-function title, not a summary
  - normally uses the primary language of the source text
  - names what the unit is doing in the reading
  - good: `外部完美形象的建立`
  - bad: `这一段讲了悉达多、父亲、母亲和朋友都喜欢他`
- `end_paragraph_n`
  - same meaning as live `unit.end_paragraph_n`
  - must copy a visible `Paragraph n` from `CurrentView / Content`
- `end_at`
  - same meaning as live `unit.end_at`
  - either `paragraph_end` for the end of the visible paragraph slice or an
    exact paragraph-local tail quote
- `status`
  - `complete`: this provisional unit is locally complete inside the visible
    preview
  - `open_tail`: only allowed for the final partition when the visible preview
    ends in the middle of a larger semantic move

### Coordinate Discipline

The model-facing output should continue to use `end_paragraph_n` + `end_at`,
not raw paragraph-char offsets.

Reason:

- semantic boundary choice is the model's job
- coordinate precision is runtime's job
- model-emitted `char_offset` values are fragile around Chinese text, quotation
  marks, whitespace, trailing closers, and preview slices

Runtime should resolve every partition boundary into the project-standard
paragraph-char coordinate shape for audit:

```json
{
  "index": 0,
  "title": "悉达多被众人爱戴的外部完美形象",
  "boundary": {
    "end_paragraph_n": "8",
    "end_at": "paragraph_end"
  },
  "status": "complete",
  "source_span_id": "src:c1:p1@0-p8@31",
  "source_span": {
    "start_cursor": {
      "chapter_id": "chapter_1",
      "chapter_ref": "1",
      "paragraph_index": 1,
      "char_offset": 0
    },
    "end_cursor": {
      "chapter_id": "chapter_1",
      "chapter_ref": "1",
      "paragraph_index": 8,
      "char_offset": 31
    }
  },
  "resolution_status": "resolved"
}
```

For later partitions, runtime can derive each start cursor from the previous
resolved partition end. If a later audit partition cannot be resolved, that
should be recorded as audit metadata and should not by itself invalidate the
already accepted first unit.

### Validation Posture

Because this optimization has both runtime and audit parts, validation should
separate first-unit correctness from later-partition audit quality.

Contract-critical:

- `unit` exists and passes the existing live boundary validation
- `preview_partition[]` exists and is non-empty
- `preview_partition[0]` exactly matches `unit`
- `preview_partition[0]` resolves to the same accepted first-unit boundary

Audit-critical but not runtime-blocking:

- later partition boundaries resolve successfully
- later partition boundaries advance monotonically
- final partition covers the visible tail
- `open_tail` appears only on the final partition
- titles are non-empty and look like unit titles rather than summaries

Recommended retry/fallback behavior:

- If `unit` or `preview_partition[0]` is missing, mismatched, or unresolved,
  follow the existing Ingest retry/fallback path.
- If only later audit partitions are malformed or unresolved, accept the first
  unit and record `preview_partition_audit_status = "partial"`.
- If the model omits `preview_partition[]` entirely, treat that as a live v15
  prompt/schema contract failure; do not silently pretend the audit map exists.

### Runtime Artifact Plan

The first implementation should keep this audit map mechanism-private:

- `unitization_audit.jsonl`
  - raw model `preview_partition[]`
  - normalized `preview_partition_audit[]`
  - per-partition source span ids when resolved
  - per-partition resolution status / failure reason
- `read_audit.jsonl`
  - compact copy or reference to the accepted `preview_partition_audit[]` for
    the read cycle
- `UnitizeDecision`
  - may carry raw `preview_partition[]` and derived audit fields for reports
- report renderer
  - show each preview partition title, boundary, and resolved span
  - visually distinguish `preview_partition[0]` as committed and later entries
    as lookahead audit metadata

Do not write later preview partitions into Unit Memory, Recent Reading Memory,
Digest `ReadingMemory`, surfaced reactions, or public chapter results.

### Report / Review Expectations

The report should let reviewers answer:

- Did Ingest really use the whole preview before choosing the first boundary?
- Did it over-split by paragraph?
- Did it over-merge several complete moves?
- Does `preview_partition[1]` make the first boundary more convincing?
- Is the final visible tail marked as incomplete when appropriate?
- Are titles short local-function names rather than summaries?

Useful report display shape:

```text
Committed unit:
  [0] 外部完美形象的建立
      P1@0 -> P8@31

Lookahead audit map:
  [1] 内心不满的转折开始
      P9@0 -> P12@...
  [2] 沙门出现并触发离家决定
      P13@0 -> P22@...  (open tail)
```

### Test Plan

Prompt rendering tests:

- assert reader-shaped instruction language for the preview audit map
- assert output contract includes `preview_partition[]`
- assert recall/retrieval instructions remain unchanged

Schema / validator tests:

- valid multi-partition output with `preview_partition[0] == unit`
- missing `preview_partition`
- empty `preview_partition`
- first partition mismatch with `unit`
- title missing / blank
- invalid visible paragraph n
- `open_tail` on non-final partition
- optional `reason` remains accepted
- `retrieve_unit_memory` action-tool preflight remains unchanged for recall language / basis validation; final output no longer carries a matching `memory_recalls[]` echo

Resolver / audit tests:

- paragraph-end partition boundary
- paragraph-local exact tail quote
- quote-normalized tail quote
- trailing closer extension
- unresolved later audit partition does not block accepted first unit
- unresolved first partition follows existing retry/fallback path
- non-advancing later partition marks audit partial

Runner / artifact tests:

- first-call success records raw and resolved preview partition audit
- retry after unresolved committed boundary still works
- Unit Memory tool preflight ignores later preview partitions
- `UnitizeDecision` / ledger keep authoritative `source_span` for the accepted
  first unit
- reports render committed unit separately from lookahead audit partitions

### Implementation Result

Implemented directly as the live v15 Ingest contract after the v14
window-partition prompt had already been reviewed and promoted.

Landed behavior:

1. Ingest final output now requires `preview_partition[]`.
2. `preview_partition[0]` must match the authoritative `unit`.
3. Runtime derives `preview_partition_audit[]` with paragraph-char
   `source_span` / `source_span_id` where boundaries resolve.
4. Later partition resolution failures mark
   `preview_partition_audit_status = "partial"` and do not block the accepted
   first unit.
5. `retrieve_unit_memory` action-tool input and recall matching semantics remain
   unchanged; tool preflight does not require `preview_partition[]`.
6. Historical A/B run packages are left untouched. Maintained future report
   renderers should consume `UnitizeDecision.preview_partition_audit[]` when
   they want to display this map.

Deferred checks:

- Formal A/B rerun of v15 against v14.
- Any frontend/public API presentation of `preview_partition[]`.
- Dedicated historical-report regeneration for the June 2026 rolling A/B runs.

## Optimization Point 2: Character-Bounded Preview Construction

### Status

Implemented as live runtime preview construction on `2026-06-13`.

No Ingest prompt change, formal A/B rerun, or historical report-package
regeneration was included in this slice.

### Source Insight

While reviewing
`reading-companion-backend/eval/runs/attentional_v2/ingest_select_next_unit_rolling_ab_probe_20260610/analysis/rolling_select_next_unit_ab/preview_window_review/segments/xidaduo_private_zh__segment_1/window_partition_draft_preview_units.md`,
the `window_partition_draft` output over-split the father-son confrontation in
`Unit 008` through `Unit 011`.

The likely complete reading movement is one scene arc:

- Siddhartha asks his father to leave with the Samanas.
- The father refuses and leaves in anger.
- Siddhartha remains standing through the night.
- The father repeatedly observes him and tests his resolve.
- The father finally recognizes the decision and lets him go.

The model instead cut local beats such as "one hour later", "the last hour
before dawn", and separate dialogue rounds as separate units. The strongest
runtime cause was that the preview horizon was too short for dialogue-shaped
paragraphs:

- current default preview values are `preview_soft_min_chars=3000`,
  `preview_hard_max_chars=7000`, and `max_lookahead_paragraphs=12`
- in dialogue-heavy text, thirteen paragraphs can be only a few hundred source
  characters
- one reviewed preview stopped around `P36-P48` at roughly 186 characters,
  before the decisive concession around `P49-P53`
- `truncated=false` was therefore not enough evidence that the semantic horizon
  was adequate; it only meant the hard character cap had not been reached

The paragraph-count cap made the preview look structurally full while leaving
the scene semantically incomplete.

### Design Goal

Make source-character budget the primary preview capacity rule while keeping
paragraphs as the alignment and coordinate unit.

Principle:

```text
Paragraphs are preview assembly boundaries, not the main preview budget.
The preview should stop because the source-character budget is full, not
because a dialogue or poetry passage used many short paragraphs.
```

### Proposed Runtime Policy

Build the Ingest preview by adding visible paragraph slices in source order from
the current cursor.

Stop when one of these conditions is true:

1. Adding the next complete paragraph slice would exceed
   `preview_hard_max_chars`.
2. The source reaches the chapter or visible corpus tail.
3. An emergency paragraph guard is reached in pathological short-line material.

Recommended first live values:

```text
preview_hard_max_chars = 7000
max_lookahead_paragraphs = disabled as a normal stopping rule
emergency_max_preview_paragraphs = 200
```

The first implementation should keep the current `preview_hard_max_chars=7000`
unless a focused probe proves it is too small. The reviewed failure did not come
from a 7000-character ceiling; it came from stopping after a small number of
short paragraphs long before the character ceiling mattered.

`preview_soft_min_chars` may remain as a diagnostic or target value, but it
should not be paired with a low paragraph cap that can stop the preview below
the soft minimum. If the implementation still keeps a soft minimum, the preview
should normally continue until at least that many source characters are visible
or the source tail is reached.

If the current visible paragraph slice alone is longer than the hard character
budget, keep the existing oversized-paragraph fallback behavior rather than
inventing a new model-facing coordinate contract in this slice. Any truncation
inside a paragraph must remain explicit in preview metadata.

### Implementation Result

Landed behavior:

1. `build_paragraph_offset_preview(...)` now assembles the visible preview by
   adding paragraph slices until source tail, hard character budget, or the
   emergency paragraph guard.
2. `preview_hard_max_chars` remains `7000`.
3. `emergency_max_preview_paragraphs` defaults to `200`.
4. Existing `max_lookahead_paragraphs` values in old policy snapshots are
   ignored as normal stopping rules.
5. Preview metadata now includes `preview_end_reason` for `source_tail`,
   `hard_max`, `emergency_paragraph_guard`, or `empty`.
6. Oversized current paragraphs still truncate inside the current paragraph at
   the hard character budget.

### Non-Goals

- Do not change the Ingest prompt in the same slice unless the targeted probe
  shows over-splitting persists after the preview horizon is repaired.
- Do not make Ingest digest future text; the preview remains lookahead for
  selecting the next unit only.
- Do not change `unit.end_paragraph_n` / `unit.end_at` or
  `preview_partition[]` output semantics.
- Do not change Unit Memory retrieval semantics, recall validation, or
  `retrieve_unit_memory` behavior.
- Do not expose any preview-window policy as a frontend/public API contract.

### Prompt Interaction

The first follow-up should change only preview construction and run a targeted
probe around the Siddhartha father-son scene.

Expected diagnostic:

- If the longer character-bounded preview causes Ingest to group the scene arc
  naturally, the primary defect was preview horizon.
- If Ingest still cuts each dialogue round after seeing the full concession, add
  a separate prompt optimization for dialogue and scene-arc boundaries.

The likely later prompt rule, if needed, is:

```text
In dialogue-heavy passages, do not treat every reply, pause, or small time
advance as a complete reading unit. Repeated challenge-answer turns, silent
tests, and delayed concessions may belong to one scene arc. Prefer a boundary
after the decision, concession, action transfer, or thematic turn has landed.
```

That prompt change should remain separate so its effect can be measured against
the preview-only repair.

### Test / Probe Plan

Runtime tests:

- many short dialogue paragraphs continue beyond the old 12-paragraph lookahead
  when still below `preview_hard_max_chars`
- poetry or short-line text can include many short paragraphs without early
  semantic under-windowing
- ordinary prose still stops before adding a paragraph that would exceed
  `preview_hard_max_chars`
- preview metadata clearly reports whether the preview ended at source tail,
  character budget, or emergency paragraph guard
- existing paragraph-number and paragraph-local boundary resolution tests remain
  valid

Targeted probe:

- rerun a small Ingest-only probe for `xidaduo_private_zh__segment_1` around the
  original `Unit 008` cursor
- verify the preview covers the father-son concession area before asking the
  model to select the next unit
- compare whether the accepted unit shifts from local dialogue beats toward the
  full father-son confrontation / resolution arc
- inspect `preview_partition[]` titles to confirm whether the model saw the
  scene as one arc or still split it by local turns

Implementation should not regenerate or edit historical A/B report packages;
new probe artifacts should be written as a new run or scratch analysis package.

## Optimization Point 3: Token-Bounded Preview Capacity

### Status

Implemented as live runtime preview construction and Ingest v16 output-discipline
wording on `2026-06-13`. Historical A/B report packages were not regenerated in
this slice.

This point supersedes the prior live `7000` source-character hard budget as the
current preview-capacity policy, but it does not change the authoritative
runtime coordinate system. Ingest still exposes paragraph-local coordinates and
runtime still accepts boundaries as paragraph-char `SourceSpan` /
`source_span_id`.

### Source Insight

The focused Siddhartha probe after Optimization Point 2 showed that the old
`12`-paragraph cap had been overcorrected in the opposite direction.

The character-bounded preview solved the original `Unit 008` through `Unit 013`
over-splitting problem: the father-son confrontation was visible as one larger
scene arc instead of many short dialogue beats. However, every reviewed preview
then ran close to the `7000` character hard cap:

- preview source characters: `6884` to `6984`
- preview paragraphs: `81` to `100`
- preview end reason: `hard_max` for every sampled unit
- `o200k_base` estimate for raw preview text: roughly `6300` tokens
- `o200k_base` estimate with Paragraph XML wrappers: roughly `8200-8600`
  tokens
- `cl100k_base` estimate for raw preview text: roughly `9100-9300` tokens
- `cl100k_base` estimate with Paragraph XML wrappers: roughly `10900-11400`
  tokens

That is much larger than the intended Ingest task. The model is not merely
checking whether the next paragraph continues the current unit; with v15 it also
has to form and output a whole-preview `preview_partition[]` audit map. A
`7000`-character Chinese preview therefore becomes a heavy multi-page planning
task rather than a bounded lookahead.

The lesson is:

```text
Model context capacity is not the right default preview capacity.
Ingest needs enough lookahead to see the first unit and the next-unit turn,
not a maximal scan of many future pages.
```

### Design Goal

Use token budget as the primary preview capacity rule while preserving
paragraph-char coordinates as the precise source boundary contract.

Principle:

```text
Tokens decide how far Ingest may look.
Paragraph-char coordinates decide where the accepted unit ends.
```

This keeps the preview budget closer to the model's actual workload across
Chinese, English, and mixed-language sources, while avoiding a migration away
from stable source coordinates.

### Implemented Runtime Policy

Build the Ingest preview by adding visible paragraph slices in source order from
the current cursor, as today. Before adding the next complete paragraph slice,
estimate the token count of the candidate preview.

Current live calibrated values:

```text
preview_soft_min_tokens = 1600
preview_target_max_tokens = 3000
preview_hard_max_tokens = 4200
emergency_max_preview_paragraphs = 200
```

The three token values have distinct roles:

- `preview_soft_min_tokens`: minimum useful lookahead. Before this floor is
  reached, runtime should keep adding paragraphs when doing so stays within the
  hard max.
- `preview_target_max_tokens`: normal stopping line. After the soft minimum is
  satisfied, runtime should stop before adding a paragraph that would exceed the
  target.
- `preview_hard_max_tokens`: absolute safety line. Runtime should not include a
  candidate preview beyond this value. If the current paragraph remainder alone
  exceeds this value, include only a prefix and mark the preview truncated.

Stopping order:

1. If the source reaches the chapter or visible corpus tail, stop with
   `preview_end_reason = "source_tail"`.
2. If `emergency_max_preview_paragraphs` would be exceeded, stop with
   `preview_end_reason = "emergency_paragraph_guard"`.
3. If adding the next complete paragraph would exceed
   `preview_hard_max_tokens`, stop with
   `preview_end_reason = "hard_max"`.
4. If the current preview is still below `preview_soft_min_tokens`, keep adding
   paragraphs as long as the hard max is respected, even if the candidate would
   exceed `preview_target_max_tokens`.
5. If the current preview has reached `preview_soft_min_tokens`, stop before
   adding a paragraph that would exceed `preview_target_max_tokens`; use
   `preview_end_reason = "target_max"`.
6. Otherwise, add the paragraph and continue.

Examples with `1600 / 3000 / 4200`:

```text
current=1200, candidate=1900 -> add; soft min takes priority over target
current=1500, candidate=3200 -> add if it stays below hard max
current=2200, candidate=2900 -> add; candidate stays below target
current=2600, candidate=3300 -> stop at target_max
current=1500, candidate=4400 -> stop at hard_max
```

This should make normal previews land around `1600-3000` estimated tokens, with
occasional larger previews only when needed to satisfy the soft minimum, to
handle coarse paragraph granularity, or to preserve enough planning context in
dialogue / scene-transition material.

The initial live v16 values were `1000 / 1800 / 2600`. After the first focused
Siddhartha v16 probe, those values looked stable but slightly too narrow for
Ingest's planning role: the model avoided the original under-preview defect, yet
sometimes lacked enough "peripheral vision" to judge whether nearby dialogue
moves belonged to a larger scene. The current values deliberately expand the
window by about `1.6x-1.7x` rather than a full hard doubling, keeping the prompt
well below the interim 7000-character-preview workload while giving Ingest more
global context for first-unit boundary choice.

### Token Estimation

The implementation should use a deterministic local estimator rather than
provider-side billing data, because preview construction happens before an LLM
request is sent.

Preferred order:

1. Use a known local tokenizer for the selected model family if one is already
   available and stable in the backend runtime.
2. Otherwise use a conservative local approximation, such as a bundled
   `tiktoken` encoding, and record the estimator name in private preview
   metadata.
3. Keep `char_count`, `paragraph_count`, and `preview_end_reason`; add
   `estimated_token_count` and `preview_token_estimator`.

The estimator should count the model-facing preview shape, not only the raw
paragraph text, because `CurrentView / Content` includes Paragraph wrappers and
attributes. If implementation cost makes exact prompt-fragment counting awkward,
the first version may count raw preview text plus a conservative per-paragraph
overhead, but the metadata must name that approximation.

### Prompt / Contract Interaction

No output schema change is required for this capacity adjustment. The live v16
prompt now tightens output discipline so the shorter preview does not regrow
through verbose planning output.

The model-facing contract remains:

- `unit.end_paragraph_n`
- `unit.end_at`
- `preview_partition[]`
- `retrieve_unit_memory.memory_recalls[]` when prior-reading recall is needed
- optional normalized `reason`

Unit Memory retrieval remains based on the selected first unit and required
recalls, not later preview partitions.

Output burden should stay proportional to Ingest's job:

- `reason` should explain only the committed first unit boundary.
- Later `preview_partition[]` entries should remain short audit/planning
  records: title, boundary, and status only.
- Do not ask for rationale, summary, or interpretive commentary for
  non-first partitions.
- Do not let later partition titles become miniature Digest outputs. They
  should name the visible semantic move, not explain or evaluate it.

This is not a schema change. It is a prompt/output-discipline constraint to
prevent token-bounded previews from regrowing through verbose reasoning. If the
model still produces oversized output after this change, prefer inspecting the
live output shape before increasing runtime `max_output_tokens`.

### Non-Goals

- Do not change `unit` or `preview_partition[]` schema in this slice.
- Do not change Digest unit boundaries directly.
- Do not create memory entries, Digest units, or cursor movement from later
  preview partitions.
- Do not expose preview-token policy through a frontend/public API.
- Do not rerun or edit historical A/B report packages as part of the runtime
  change.

### Test / Probe Plan

Runtime tests:

- short dialogue paragraphs continue past a small paragraph count when still
  below `preview_soft_min_tokens`
- normal prose stops around `preview_target_max_tokens` after the soft minimum
  has been satisfied
- adding a next paragraph that would exceed `preview_hard_max_tokens` stops with
  `preview_end_reason = "hard_max"`
- a current paragraph remainder longer than `preview_hard_max_tokens` truncates
  inside the current paragraph and preserves paragraph-char coordinates
- old `max_lookahead_paragraphs` snapshots still do not reintroduce the old
  short-dialogue bug
- preview metadata includes `estimated_token_count` and
  `preview_token_estimator`

Targeted probes:

- rerun the Siddhartha `Unit 008` region to confirm the father-son scene still
  stays visible enough to avoid the old over-splitting
- compare opening-window behavior against the current `7000`-character preview,
  because the latest focused report suggested that the very long preview may
  encourage overly global first-unit partitioning near the chapter opening
- inspect prompt token usage and `preview_partition[]` length to confirm the
  model's planning burden shrinks materially
- inspect final output size to confirm later partitions stay as short titles and
  boundaries rather than growing into rationales for non-first units
