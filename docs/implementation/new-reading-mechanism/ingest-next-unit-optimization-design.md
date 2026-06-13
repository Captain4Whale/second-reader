# Ingest Next-Unit Optimization Design

Purpose: collect concrete optimization points discovered while reviewing
`attentional_v2` Ingest next-unit selection reports.
Use when: turning a reviewed report insight into a candidate prompt/schema/runtime
change for Ingest.
Not for: the live prompt source of truth, formal evaluation scoring, or Unit
Memory retrieval policy.
Update when: a new Ingest next-unit optimization point is accepted for design,
implemented, rejected, or superseded.

Status: active design note. This document is organized by optimization point so
one accepted point can be implemented without reopening every later idea.

Current live baseline:
- Ingest prompt: `attentional_v2.ingest.v14`
- Promptset: `attentional_v2-phase6-v64`
- Live boundary contract: `unit.end_paragraph_n` + `unit.end_at`
- Authoritative runtime coordinate: paragraph-char `SourceSpan` /
  `source_span_id`, derived by runtime after resolving the model boundary
- Related decision: `DEC-116`
- Related living pattern: `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md` entry 19

## Optimization Point 1: Preview Partition Audit Map

### Status

Candidate for the next Ingest prompt/schema experiment. Not implemented in the
live prompt, schemas, runner, or reports yet.

### Source Insight

The June 2026 rolling A/B review found that the window-partition Ingest prompt
often selected a better first unit because it did not stop at the first locally
plausible paragraph boundary. It looked across the visible preview, inferred
where later text continued the same semantic move or began a new move, and then
committed only the first unit.

The current live prompt already asks for this whole-window conceptual partition:

- consider the whole visible window first
- conceptually divide the window into consecutive reading units
- commit only the first unit
- treat the rest of the window as lookahead context only

But the live output exposes only the first committed boundary. Reviewers cannot
see how the model provisionally divided the rest of the preview or what titles /
local functions it assigned to later units.

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
- If the model omits `preview_partition[]` entirely, treat that as a candidate
  prompt/schema failure during v15 experiments; do not silently pretend the
  audit map exists.

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
- `memory_recalls[]` matching rule with `retrieve_unit_memory` remains unchanged

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

### Suggested Implementation Sequence

1. Add a candidate prompt/schema behind a probe-only branch or prompt version.
2. Update Ingest final-output schema and validator for `preview_partition[]`.
3. Add resolver support that derives `preview_partition_audit[]` without making
   later partitions runtime-authoritative.
4. Update unitization/read audit artifacts and report rendering.
5. Run targeted tests for prompt rendering, schema validation, resolver, runner,
   and report rendering.
6. Run a rolling A/B probe against live v14 before promoting the candidate.

### Promotion Gate

Promote only if the candidate shows at least one of:

- first-unit boundaries improve or stay at least as good as v14
- audit reports become materially easier to review
- the additional partition titles reveal useful failure modes without increasing
  runtime fallback / contract failure rate

Do not promote if:

- the model starts over-digesting future preview text
- later partition output causes frequent contract failures
- titles become verbose summaries
- the first unit gets worse because the model tries to make the whole preview
  partition look balanced
- Unit Memory retrieval or Digest context behavior changes accidentally
