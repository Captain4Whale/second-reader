# Digest Understanding / Response / Annotation Design

Purpose: define the implemented Digest action semantics and prompt/output contract shift from memory-shaped output to reading-action-shaped output.
Use when: reviewing the Digest `Understanding / Response / Annotation` prompt contract after `DEC-108` and `DEC-109`.
Not for: stable runtime authority, evaluation claims, or evidence-catalog updates.
Update when: Digest action names, output fields, XML prompt structure, or runtime mapping from Digest output to stored memory changes.

## Status

- Date: `2026-06-01`
- Status: implemented in live Digest prompt / LLM output normalization.
- Evaluation status: no eval run, no evidence-catalog update.
- Supersession note:
  - This document remains the authority for Digest's three peer model-facing outputs: `understanding`, `response`, and `annotations`.
  - Its early `ReadingState` context examples were superseded by `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`.
  - The current live Digest prompt uses top-level `ReadingMemory`, not `ReadingState`, `RecentMemory`, or `RetrievedUnitMemory`.
- Current basis:
  - `DEC-108` makes `Digest` the concrete per-unit interpretation LLM call.
  - `DEC-109` removes content-typed structured long-memory stores from the current live surface.
  - Current Digest stores one model-produced `understanding` object through runtime `recent_reading_memory`, but the model-facing task no longer phrases this as "maintain memory."

## Implementation Status

- Implemented prompt version: `attentional_v2.digest.v3`
- Implemented XML assembly spec: `attentional_v2.digest.xml.v3`
- Implemented promptset: `attentional_v2-phase6-v47`
- Implemented output contract: `digest_understanding_response_annotation_json_v2`
- Runtime mapping:
  - `understanding.content` -> zero or one internal `memory_uptake_ops[].payload.memory_text` targeting `recent_reading_memory`
  - `response` -> internal `DigestResult.reading_impression`
  - `annotations[]` -> internal `DigestResult.surfaced_reactions`
- Old model-facing fields `reading_impression`, `surfaced_reactions`, and `recent_reading_memory` are not accepted as current Digest LLM contract fields; internal runtime/audit names remain stable in this slice.

## Design Claim

Digest should be described as one coherent reading action with three peer outputs:

- `Understanding`: read the source unit in; capture what the original text says, establishes, changes, or makes available for continued reading.
- `Response`: read the source unit out; express the reader's integrated feeling, thought, pressure, question, or aftertaste after understanding it.
- `Annotation`: produce visible margin-note-style output anchored to exact source text.

This replaces the current uneven semantic split:

- `reading_impression` and `surfaced_reactions` are described as reading behavior.
- `recent_reading_memory` is described under memory maintenance.

The new model-facing semantics should not ask Digest to remember for memory's sake. Digest should understand the present unit. The runtime may store that understanding as recent reading memory afterward, but storage is a post-processing consequence rather than the LLM's primary self-description.

## Is Instruction-Only Enough?

No. The main semantic work belongs in `Instruction`, but the refactor should also update the LLM-facing output contract and runtime normalization.

Minimum implementation scope:

- `Instruction`
  - Make `Understanding`, `Response`, and `Annotation` direct child blocks under top-level `Instruction`.
  - Remove `MemoryInstruction` as a top-level action category.
  - Keep non-action support blocks such as `CurrentStep` / `TaskOverview`, `ContextUseGuide`, `SourceGrounding`, and `ResponseDiscipline`.
- `OutputContract`
  - Rename LLM-facing output fields from `recent_reading_memory`, `reading_impression`, and `surfaced_reactions` to `understanding`, `response`, and `annotations`.
  - Update field contracts so the three outputs are peers.
- Runtime adapter
  - Convert the single `understanding` object into zero or one internal `memory_uptake_ops[]` with `target_store="recent_reading_memory"`.
  - Normalize `annotations[]` using the existing surfaced-reaction grounding rules.
  - Map `response` into the current internal `reading_impression` field unless a later cleanup renames audit/runtime artifacts too.
- Tests / docs
  - Update prompt manifest tests, Digest output-normalizer tests, read-audit tests, and stable docs that describe the current Digest output contract.

Storage can remain unchanged in the first implementation slice:

- `recent_reading_memory` remains the runtime store.
- `read_audit.jsonl` may continue to record internal `reading_impression`, `surfaced_reactions`, and normalized memory ops.
- A later cleanup can decide whether audit keys should become `digest_understanding`, `digest_response`, and `digest_annotations`.

## Pre-Implementation Prompt Structure

Before this implementation, the top-level user prompt shape was:

```xml
<ReaderRole>...</ReaderRole>
<Instruction>...</Instruction>
<BookInfo>...</BookInfo>
<ReadingState>...</ReadingState>
<CurrentFocus>...</CurrentFocus>
<OutputContract>...</OutputContract>
```

Pre-implementation `Instruction` shape:

```xml
<Instruction>
  <TaskOverview>...</TaskOverview>
  <ContextUseGuide>...</ContextUseGuide>
  <ReadingBehavior>
    <ReadingImpression>...</ReadingImpression>
    <SurfacedReaction>
      <ReactionSelection>...</ReactionSelection>
      <ReactionGroundingAndCallback>...</ReactionGroundingAndCallback>
    </SurfacedReaction>
  </ReadingBehavior>
  <MemoryInstruction>
    <MemoryBoundary>...</MemoryBoundary>
    <RecentReadingMemory>...</RecentReadingMemory>
  </MemoryInstruction>
  <SourceGrounding>...</SourceGrounding>
  <ResponseDiscipline>...</ResponseDiscipline>
</Instruction>
```

Pre-implementation LLM-facing output contract:

```json
{
  "reading_impression": "...",
  "surfaced_reactions": [],
  "recent_reading_memory": []
}
```

Before this implementation, runtime converted:

- `recent_reading_memory[]` -> `memory_uptake_ops[]` targeting `recent_reading_memory`
- `reading_impression` -> internal `DigestResult.reading_impression`
- `surfaced_reactions[]` -> internal `DigestResult.surfaced_reactions`

## Current Live Prompt Structure

The current live Digest prompt shape is:

```xml
<ReaderRole>...</ReaderRole>
<Instruction>...</Instruction>
<BookInfo>...</BookInfo>
<ReadingMemory>...</ReadingMemory>
<CurrentFocus>...</CurrentFocus>
<OutputContract>...</OutputContract>
```

Current prompt-facing memory is one `ReadingMemory` text block. Runtime merges hot current-chapter Understanding from `recent_reading_memory` with selected long-distance Unit Memory Understanding lines before rendering it. Digest does not receive separate `ReadingState`, `RecentMemory`, `RetrievedUnitMemory`, raw prior source text, prior Response, or prior Annotation blocks.

## Old Prompt Text Moved Or Rewritten

### Old Task Overview

Old fragment:

```text
Your job is to read the exact current unit with a small carried-forward memory packet, then return a structured record of the reading experience.

Rules:
- First read the provided unit as the current reading present, not as a field-filling task.
```

Assessment:

- Keep the "current reading present" idea.
- Replace "structured record of the reading experience" with the three peer outputs.

### Old Reading Impression Policy

Old fragment:

```text
- Let `reading_impression` be the brief natural impression that remains after reading: what you now understand, notice, or feel from this passage.
- Use the carried-forward memory naturally when it genuinely matters, but do not collapse the unit into a chapter summary or evaluator voice.
- Do not invent earlier text that is not present in the carried memory or selective carry.
```

Assessment:

- Keep most of this, but rename and narrow it to `Response`.
- Remove "what you now understand" from this field because `Understanding` will own source-faithful content.
- Keep "notice or feel" only if it is framed as a reader response after understanding.

### Old Surfaced Reaction Policy

Old fragment is already mostly aligned with `Annotation`. It says surfaced reactions should:

- stay proportionate around thin structural units
- only surface naturally worth-marking material
- stay anchored to the current unit
- use exact `source_quote`
- default to `0-2`
- avoid swallowing earlier independently meaningful lines
- use a wide-entry, narrow-expression stance

Assessment:

- Keep the policy substance.
- Rename `surfaced_reactions` to `annotations` in prompt-facing text.
- Rename `SurfacedReaction` instruction block to `Annotation`.
- Keep callback/link hygiene under `AnnotationGroundingAndCallback`.

### Old Recent Reading Memory Policy

Old fragment begins:

```text
- First maintain Recent Reading Memory: after reading this unit, write one Recent Reading Memory entry for your future self unless the unit is empty or purely structural.
- Assume the exact source text of this unit may not be shown again in the next Digest step. Record what you now understand from this unit that should remain available for coherent continued reading.
- Write Recent Reading Memory as source-established content first, not essay-like analysis.
- First record what the source directly establishes for future reading: who or what appears, what happened, what the author claims, what distinction / stage / example is introduced, what condition or consequence is stated, or what writing position / evidence boundary / reader-orientation is declared.
```

Assessment:

- This is the largest semantic rewrite.
- The core content rules are useful, but the "maintain memory" framing should be removed.
- The output should be `Understanding`: what the current unit itself establishes, not "what should be remembered."
- Future-use language can remain lightly as "for continued reading," but should not dominate the task.
- References to stable concept/thread context should be removed because `DEC-109` retired those model-facing stores.

## Target Instruction Shape

`Understanding`, `Response`, and `Annotation` should be direct child tags under `Instruction`.

Target shape:

```xml
<Instruction>
  <CurrentStep>...</CurrentStep>
  <ContextUseGuide>...</ContextUseGuide>
  <Understanding>...</Understanding>
  <Response>...</Response>
  <Annotation>...</Annotation>
  <SourceGrounding>...</SourceGrounding>
  <ResponseDiscipline>...</ResponseDiscipline>
</Instruction>
```

Why direct children:

- They are the three main work products of Digest.
- Keeping them direct makes the prompt easy to inspect and avoids hiding one output under "memory."
- `CurrentStep`, `ContextUseGuide`, `SourceGrounding`, and `ResponseDiscipline` remain support blocks rather than peer outputs.

## Target Prompt Text

Tone rule:

- The beginning of `Instruction` should invite a readerly stance before it introduces output governance.
- Mechanical language is acceptable in `OutputContract`, but `CurrentStep`, `Understanding`, and `Response` should not sound like schema-filling instructions.
- Boundary rules should appear after the positive reading posture is established.

### CurrentStep

```text
You are now reading the next source unit in an ongoing deep reading of this book.

Stay with this unit as the present moment of reading. Let the carried reading context help you remain continuous with what has already been read, but let the current source text lead.

After reading, express what this unit gives you in three connected ways: what you understand from the text, how you respond to it as a reader, and which exact lines, if any, are worth annotating.
```

### ContextUseGuide

```text
- Let BookInfo orient you to the stable identity of the book; it is not source text.
- Let ReadingMemory hold prior understanding that the reading has already carried forward. Use it for continuity, contrast, callback, and unresolved pressure when it genuinely clarifies the current source unit.
- Do not treat ReadingMemory as current source text, prior reader response to imitate, or a reason to force a connection.
- Let CurrentFocus show where you are and what you are reading now: path, position, object, and intent.
- Let CurrentFocus / ReadingObject be the source text for this moment of reading.
- Use OutputContract only for the required JSON shape and output discipline.
```

This is the current `digest.context_use_guide` posture after the `ReadingMemory` follow-through slice.

### Understanding

```text
Begin by staying with what this unit is saying. Let it settle before turning it into reaction, summary, or commentary.

Understanding is the source-faithful grasp of what this unit gives to the ongoing reading: what it establishes, changes, clarifies, contrasts, withholds, frames, or makes newly available.

Write it as the understanding you would carry forward from having read this unit, not as a memory-maintenance task and not as a visible margin note.

Let the source lead. Notice who or what appears, what happened, what the author claims, what distinction, stage, example, condition, consequence, method, evidence boundary, reader-orientation, image, scene, or tonal shift is introduced.

Add interpretation only when it is needed to preserve source-established meaning. Do not start from your theory of the passage.

Compress meaning, not wording. Do not copy the whole passage. Do not predict whether something will matter later. Do not import outside knowledge.

Use the carried reading context to understand this unit as part of the unfolding book, but keep Understanding centered on what this unit itself brings. Do not turn it into a recap of prior context.

Write Understanding so the reading can continue coherently even if the exact source text of this unit is not shown again soon.

Be context-resolvable, not standalone exhaustive. Avoid bare pronouns or vague references unless the referent is explicit in the same Understanding.

Write one holistic Understanding for this unit. The unit may contain several source-established meanings, but integrate them into one coherent Understanding instead of splitting them into multiple entries.

Do not split Understanding by sentence, paragraph, theme, future use, or separate memory point. Digest may produce multiple Annotations, but it produces only one Understanding for the unit.

If the unit is empty or purely structural, Understanding may be empty. If the unit is author-facing or method-facing, treat it as meaningful when it declares witness position, evidence boundary, writing method, intended reader, or what the book will / will not explain.
```

Mapping from old prompt:

- Reuses the source-established-content rules from `digest.recent_reading_memory_policy`.
- Removes "First maintain Recent Reading Memory."
- Replaces "write one Recent Reading Memory entry for your future self" with "write Understanding for the current unit itself."
- Removes concept/thread context language.

### Response

```text
After understanding the unit, let yourself respond as a reader.

Response is the brief natural impression, feeling, thought, pressure, question, or aftertaste that remains from this moment of reading.

Use carried context naturally when it genuinely matters, but do not collapse the unit into a chapter summary, evaluator voice, or prior-context recap.

Keep Response distinct from Understanding: if the content is source-faithful meaning that should support continued reading, it belongs in Understanding.

Keep Response distinct from Annotation: if the expression is tied to a specific source span and worth showing as a visible margin-note-style output, it belongs in Annotation.
```

Mapping from old prompt:

- Reuses `reading_impression` policy.
- Removes "what you now understand" from the definition.
- Keeps the anti-summary and anti-invention rules.

### Annotation

```text
When a line or small span genuinely asks to be marked, annotate it.

An Annotation is a visible margin-note-style response anchored to exact source text from the current unit.

It may be a line that lands with force, a margin-note thought or question, a natural connection, a distinction or turn that suddenly clarifies something, or a local trigger that feels worth marking.

Do not create an Annotation just to fill the field. It is acceptable to emit zero annotations. Default to 0-2.

Each Annotation must stay anchored to the current unit. Each `source_quote` must be an exact quote from this unit.

Choose each `source_quote` as the smallest self-sufficient span that can honestly stand as the annotation's footing.

If the unit contains multiple independently valuable local triggers, you may annotate them separately. Do not let one sharper later sentence erase an earlier framing line, premise line, or hinge line that also stands on its own.

Keep V1's wide-entry, narrow-expression stance: be willing to notice and surface a real local trigger, but do not manufacture commentary just to fill space.

If you callback to earlier material in visible content, speak naturally to the reader. Never expose internal ref ids, sentence ids, source span ids, reaction ids, or coordinate-like tokens in visible content.
```

Mapping from old prompt:

- Reuses `digest.surfaced_reaction_policy`.
- Reuses `digest.reaction_anchor_and_callback_policy`.
- Renames the output and instruction from reaction to annotation.
- Keeps exact-quote grounding.

### SourceGrounding

```text
- `annotations[].source_quote` must be a short exact contiguous span copied from the current unit: no ellipses, no stitched fragments, no paraphrase, no translation.
- Never invent source coordinates. The runner resolves source quotes to paragraph + char-offset `SourceRef` objects after Digest returns.
- Understanding is grounded in the current source unit as a whole; it does not need exact source quotes.
```

Mapping from old prompt:

- Rename `surfaced_reactions[].source_quote` to `annotations[].source_quote`.
- Rename Recent Reading Memory grounding to Understanding grounding.

### ResponseDiscipline

```text
- Do not output broad chapter summary.
- Do not explain whether you "used prior material".
- Do not decide or name the next route. After this read, the runner will settle the unit and advance normally.
- Return JSON only.
```

This can reuse the current response-discipline text.

## Target Output Contract

Recommended LLM-facing contract:

```json
{
  "understanding": {
    "kind": "event_or_situation|claim_or_argument|definition_or_distinction|causal_or_structural_link|character_or_relationship|emotional_or_tonal_shift|image_or_scene|local_pattern_or_thread|fact|author_or_method_frame|other",
    "content": "..."
  },
  "response": "...",
  "annotations": [
    {
      "source_quote": "...",
      "content": "...",
      "prior_link": null,
      "outside_link": null,
      "search_intent": null
    }
  ]
}
```

Notes:

- `understanding.content` replaces `recent_reading_memory[].memory_text` at the model-facing level.
- `response` replaces `reading_impression`.
- `annotations` replaces `surfaced_reactions`.
- `author_or_method_frame` is proposed as an optional `kind` because current prompt rules explicitly treat author stance, evidence boundary, writing method, and intended reader as meaningful content. If the team wants fewer kinds, this can remain `other` instead.
- `understanding.content` may be empty only for empty or purely structural units; runtime does not append an empty recent-memory entry.

Runtime mapping:

```text
understanding -> zero or one memory_uptake_ops[] entry -> recent_reading_memory store
response -> DigestResult.reading_impression
annotations[] -> DigestResult.surfaced_reactions
```

This keeps runtime state stable while making the LLM call semantically cleaner.

## Implementation Checklist

- Rename or add prompt fragments:
  - `digest.current_step`
  - `digest.understanding_policy`
  - `digest.response_policy`
  - `digest.annotation_policy`
  - `digest.annotation_grounding_and_callback_policy`
- Reshape `DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE`:
  - remove `ReadingBehavior`
  - remove `MemoryInstruction`
  - add direct children `Understanding`, `Response`, and `Annotation`
- Update source-grounding text:
  - `surfaced_reactions[].source_quote` -> `annotations[].source_quote`
  - `Recent Reading Memory entries` -> one holistic `Understanding`
- Update `OutputContract`:
  - `ReturnFormat`
  - field contracts
  - output contract name: `digest_understanding_response_annotation_json_v2`
- Update `llm_calls.digest(...)` normalizer:
  - parse `payload["understanding"]`
  - parse `payload["response"]`
  - parse `payload["annotations"]`
  - optionally ignore legacy fields rather than supporting them, depending on whether this is a hard cutover
- Update tests:
  - prompt XML structure contains direct `Understanding`, `Response`, `Annotation`
  - prompt XML no longer has `MemoryInstruction` or model-facing `RecentReadingMemory`
  - output contract no longer asks for `reading_impression`, `surfaced_reactions`, or `recent_reading_memory`
  - runtime still stores Understanding through `recent_reading_memory` append ops
- Update stable docs after implementation:
  - `docs/backend-reading-mechanisms/attentional_v2.md`
  - `docs/current-state.md`
  - `docs/tasks/registry.md`
  - `docs/tasks/registry.json`

## Open Questions

- Should the implementation be a hard LLM-facing field rename, or should it temporarily accept both old and new fields?
  - Default recommendation: hard rename for prompt/LLM-facing fields; keep only internal runtime mapping stable.
- Should `response` remain a single string?
  - Default recommendation: yes. It should stay compact and not compete with Understanding.
- Should `annotations` remain 0-2 by default?
  - Default recommendation: yes. The current density rule is working conceptually and should not be loosened in this semantic refactor.
- Should `understanding` be a list or one object/string?
  - Default recommendation: list, because some units establish two naturally separable meanings; keep prompt pressure toward one entry in most cases.
