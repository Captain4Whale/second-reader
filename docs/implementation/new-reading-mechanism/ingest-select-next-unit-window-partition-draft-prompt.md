# Ingest SelectNextUnit Window Partition Draft Prompt

Purpose: hold the reviewed draft prompt used by the `window_partition_draft`
Ingest A/B probes.

Use when: reviewing, editing, or preparing a possible replacement for the
current live `Ingest / SelectNextUnit` prompt.

Not for: live runtime behavior, evaluation scoring, or Unit Memory retrieval
policy.

Status: draft for review. It is not the live prompt.

Last synchronized: `2026-06-11`

## Source

This file records the draft prompt used by the debug-only A/B probes:

- fixed-cursor probe:
  `reading-companion-backend/eval/runs/attentional_v2/ingest_select_next_unit_ab_probe_20260610/analysis/select_next_unit_prompt_ab/run_probe.py`
- rolling probe:
  `reading-companion-backend/eval/runs/attentional_v2/ingest_select_next_unit_rolling_ab_probe_20260610/analysis/rolling_select_next_unit_ab/run_probe.py`

The rolling probe reused the fixed-cursor probe's `DRAFT_CURRENT_STEP`,
`DRAFT_SELECT_NEXT_UNIT`, `DRAFT_OUTPUT_CONTRACT`, and draft final-output tool
schema.

## Integration Shape

The draft only changes these prompt sections:

- `Instruction / CurrentStep`
- `Instruction / SelectNextUnit`
- `OutputContract`

These sections intentionally remain the same as the current live Ingest prompt
unless a later edit says otherwise:

- `ReaderRole`
- `Instruction / ContextUseGuide`
- `Instruction / RecallPriorReading`
- `Instruction / ExecutionLimits`
- `BookInfo`
- `CurrentView`
- `RetrievalSurface`

The intended top-level XML shape remains:

```xml
<ReaderRole>...</ReaderRole>
<Instruction>
  <CurrentStep>...</CurrentStep>
  <ContextUseGuide>...</ContextUseGuide>
  <SelectNextUnit>...</SelectNextUnit>
  <RecallPriorReading>...</RecallPriorReading>
  <ExecutionLimits>...</ExecutionLimits>
</Instruction>
<BookInfo>...</BookInfo>
<CurrentView>...</CurrentView>
<RetrievalSurface />
<OutputContract>...</OutputContract>
```

## Draft CurrentStep

```text
You are in the Ingest step of a sequential deep-reading loop.

This step happens before Digest. You are not yet reading the selected unit for interpretation or reader-facing output.

You are shown a bounded forward reading lookahead window from the current reading cursor. In this call you do two things:

1. Consider the window as a sequence of coherent reading units, then commit only the FIRST unit as the next source unit Digest should read closely.
2. After committing that first unit, briefly name any earlier reading that this unit makes you want to remember before Digest reads it closely.

The rest of the window is lookahead context only. It helps you place the first boundary; it is not itself being read by Digest yet.
```

## Draft SelectNextUnit

```text
Partition the forward window into coherent reading units, then commit the first one. The first unit starts at the current reading cursor.

What a semantic unit is — a continuous span of source text that satisfies all of:

- Internally coherent: its sentences hang together on one topic, argument, scene, exchange, image, concept, or logical move.
- Locally complete: it closes one forward move enough for Digest to read it as the present object of attention. For example: a claim and its immediate support, an example and its point, a scene or beat that lands, a concept introduced and initially unpacked, a turn in dialogue, or a local summary.
- Minimal: it is the smallest span that is still locally complete. Do not greedily merge several complete moves into one large unit just because they are related.
- Naturally bounded: it ends at a real transition, such as topic shift, argument closing, scene change, change in speaker, change in rhetorical function, or the start of a new move.

How to choose the boundary:

- Consider the whole visible window first. Do not commit a boundary the moment you reach the first plausible stopping point.
- Conceptually divide the window into consecutive reading units in order, with no gaps. Use that whole-window view only to place the first boundary well.
- Commit only the FIRST unit. Anything after it is provisional lookahead context.
- The first unit always starts at the current source cursor in `CurrentView / Position`. Do not invent or output a start position.
- A boundary falls on a sentence edge and never inside a sentence.
- A boundary may fall inside a paragraph when one long paragraph contains more than one complete move.
- A unit may also span several paragraphs when the same local move clearly continues across them.
- The window is assembled from paragraph slices, but the unit is not required to align to paragraph edges.

Window tail:

- The window end is controlled by runtime budget and may fall in the middle of a move.
- Do not over-merge the first unit just to make the later window tail look balanced or complete.
- Only the first boundary is authoritative.

Signals you may use:

- Discourse markers such as 因此 / 然而 / 另一方面 / 总之 / 例如 often close a unit or open a new one.
- Lexical cohesion and topic continuity suggest the same unit is continuing.
- A clear shift in topic, speaker, time, place, goal, cause-effect, or rhetorical function suggests a boundary.
- In argument, claim → evidence → qualification may form one unit; a new claim opens a new unit.
- In narrative, a scene/beat may end when an action, recognition, exchange, or emotional turn lands.
- A unit should usually compress into one main idea. If it sprawls into several main ideas, it is probably too long.

Size and length:

- A unit is a small, digestible reading move: about the amount Digest can turn into one coherent Understanding.
- It may be part of a long paragraph, one paragraph, or a few paragraphs.
- It must never cross a chapter boundary.
- The lookahead window is deliberately longer than one unit. The first unit should usually end well within it.
- If the first unit approaches the length of the whole window, you have almost certainly merged too much. Back off to the nearest earlier locally complete move.

Structural cues:

- Treat `chapter_heading` and `section_heading` as weak structure cues, not automatic standalone units.
- Merge a label-like heading with the body it introduces.
- Let a heading stand alone only if its wording itself forms a complete, meaningful move.
- Ignore pure ornament / divider / separator lines at the boundary.
- `text_role` may help orient you, but it must not decide the boundary by itself.
```

## Draft OutputContract

```text
`OutputFields` and `ReturnFormat` define the concrete structured result.

Submit this shape through the required final output tool:

{
  "unit": {
    "end_paragraph_n": "<the n attribute of the Paragraph where the first unit ends>",
    "end_at": "paragraph_end | <exact tail quote located inside end_paragraph_n>"
  },
  "reason": "<boundary rationale>",
  "memory_recalls": [
    {
      "recall_id": "r1",
      "recall_text": "<concise prior-reading memory target>",
      "basis": "selected_source_unit"
    }
  ]
}

Rules:

- The committed unit starts at the current cursor in `CurrentView / Position`; do not emit a start position.
- `end_paragraph_n` must copy the `n` attribute from one visible `Paragraph` in `CurrentView / Content`.
- Use `"paragraph_end"` when the unit ends at the end of that visible paragraph slice.
- Use an exact tail quote only when the unit must end inside a long paragraph at a sentence boundary.
- The exact tail quote must be copied character-for-character from `end_paragraph_n` and must uniquely identify the unit end within that paragraph.
- `reason` explains why the unit starting at the current cursor should end at this boundary. It is a boundary rationale, not a summary and not a second source span.
- `memory_recalls` contains zero to three entries. Use an empty list if the selected unit does not call for prior memory.
- Every recall `basis` must be exactly `"selected_source_unit"`.
- Do not output markdown, commentary, or extra fields.
```

## Draft Final Output Tool Schema

This is the tool schema used by the A/B probe harness for the draft variant.
If this draft becomes live, the production schema should be reviewed rather
than copied mechanically.

```json
{
  "name": "submit_ingest_result",
  "description": "Submit the final Ingest unit boundary and prior-reading recall result. Use this tool exactly once as the final answer.",
  "input_schema": {
    "type": "object",
    "properties": {
      "unit": {
        "type": "object",
        "properties": {
          "end_paragraph_n": {
            "type": [
              "string",
              "number"
            ]
          },
          "end_at": {
            "type": "string"
          }
        },
        "required": [
          "end_paragraph_n",
          "end_at"
        ]
      },
      "reason": {
        "type": "string"
      },
      "memory_recalls": {
        "type": "array",
        "maxItems": 3,
        "items": {
          "type": "object",
          "properties": {
            "recall_id": {
              "type": "string"
            },
            "recall_text": {
              "type": "string"
            },
            "basis": {
              "type": "string",
              "enum": [
                "selected_source_unit"
              ]
            }
          },
          "required": [
            "recall_id",
            "recall_text"
          ]
        }
      }
    },
    "required": [
      "unit",
      "memory_recalls"
    ]
  }
}
```

## Review Notes

- The draft changes boundary expression from live `end_anchor_text` to
  `unit.end_paragraph_n + unit.end_at`.
- `paragraph_end` means the selected unit ends at the end of the visible
  paragraph slice with that `n`.
- An exact tail quote means the selected unit ends inside that paragraph at a
  sentence boundary.
- The draft asks the model to view the whole lookahead window as consecutive
  reading units, but only commit the first unit.
- The A/B probe intentionally isolated retrieval: `memory_recalls` was recorded
  for observation, but retrieval was not executed.
- The A/B probe schema did not require `reason`, although the prompt did ask for
  it. If promoted to live, this should be resolved deliberately.
