# Digest Marginalia Live Prompt Candidate v1

Purpose: provide a candidate live-prompt rewrite for Digest Marginalia selection, writing, and output-contract wording.
Use when: comparing candidate Marginalia prompt wording against the current review draft before implementing Digest prompt/schema/runtime changes.
Not for: current live runtime authority, historical eval artifacts, or formal evidence promotion.
Update when: the candidate prompt text changes after review, or when a later implementation slice promotes part of it into live Digest.

Created: `2026-06-20`

## Status

- Status: candidate prompt text for human review.
- Live prompt unchanged by this document.
- Companion design doc: `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
- Current live baseline:
  - Digest prompt: `attentional_v2.digest.v10`
  - promptset: `attentional_v2-phase6-v68`
  - current model-facing fields: `understanding`, `response`, `marginalia[]`
- Candidate output direction:
  - `marginalia[].source_quote` is required.
  - `marginalia[].content` is optional / empty-string tolerant.
  - Empty or omitted `content` means highlight-only.
  - Non-empty `content` means note-bearing Marginalia.
  - No `mode`, `kind`, `decision`, `prior_link`, `outside_link`, or `search_intent` in the normal model-facing Marginalia item.

## Design Intent

This candidate keeps the strongest ideas from the source draft:

- highlight marks attention, note records thought
- Marginalia begins when attention is caught by a local source span
- the useful triggers are Resistance, Leverage, and Growth
- write notes only when a plain highlight is not enough
- add evidence and reasoning, not attitude
- preserve uncertainty honestly
- every note must return the reader to the source text

It removes or compresses material that should stay in the design/sourcebook layer rather than the live prompt:

- long theory about why Marginalia matters
- named literary-critical traditions as long examples
- broad checklists that encourage scanning item by item
- hidden planning fields such as `hook`, `intent`, `decision`, or `evidence_status`
- inherited visible-reaction metadata as normal model output

## Candidate Instruction Text

The following text is written as a candidate replacement for the live `<Marginalia>` instruction block, with adjacent contract wording where useful.

### Marginalia

Marginalia are exact-source marks in the page margin for the current source unit. They may be highlight-only or note-bearing.

A highlight marks attention. A note records thought. If the quote itself preserves the value, produce highlight-only Marginalia by returning the exact `source_quote` with empty or omitted `content`. If the value would be lost without an explanation, question, connection, or judgment, add note content.

Do not create Marginalia just to fill the field. It is acceptable to emit zero Marginalia items.

Look for local places where the text catches attention in a way worth preserving:

- Resistance: the quote makes understanding unstable. It may contain a compressed idea, ambiguity, contradiction, unfamiliar allusion, technical term, uncertain fact, translation pressure, or a hard-to-separate speaker / narrator / character stance.
- Leverage: the quote changes how the unit, scene, argument, character, concept, or earlier material should be understood. It may be a definition, hinge sentence, turn, echo, irony, recurring image, shift in perspective, or small action that reveals a larger relation.
- Growth: the quote opens a useful direction to keep tracking. It may raise a question, suggest a comparison, create ethical or emotional tension, point toward a research lead, or make a reader's own assumption visible.

These are decision aids, not output labels. Do not output `Resistance`, `Leverage`, `Growth`, `hook`, `intent`, `decision`, or other calibration fields.

### Choosing Highlight Or Note

Use the minimal necessary intervention.

- Choose highlight-only when the quote is worth finding again and already carries its value without explanation. This includes striking wording, concentrated imagery, a compact claim, a memorable formulation, or a line whose importance is self-evident in context.
- Choose note-bearing Marginalia when a plain highlight would not preserve the value. The note should add a specific relation, explanation, question, distinction, or judgment that helps the reader see why the quote matters.
- Skip the quote when the only possible note would say a generic thing such as "this is important", "this is well written", "this character is vivid", or "this passage is tense".

### Selecting The Source Quote

Each `source_quote` must be an exact contiguous span copied from the current source unit.

Choose the smallest self-sufficient span that can honestly support the highlight or note. Do not use ellipses, stitched fragments, paraphrase, translation, source coordinates, sentence ids, paragraph ids, memory ids, or internal ref ids.

If multiple local triggers are independently worth preserving, emit separate Marginalia items. Do not let one sharp later sentence erase an earlier framing line, premise line, hinge line, or image that also stands on its own.

### Writing Note Content

Before writing note content, silently form a simple purpose such as:

- unpack how this wording creates an effect
- explain why this sentence changes the unit
- connect this image with a prior established pattern
- question an inference or assumption
- preserve an uncertainty that should not be flattened
- record a grounded reader response

Do not output this purpose. Output only `source_quote` and, when needed, `content`.

Good note content should:

- add evidence, not just attitude
- show reasoning, not just announce a conclusion
- stay anchored to the chosen quote's wording, syntax, structure, fact, or local relation
- be compact enough to sit beside the source text
- distinguish in-text inference, low-risk common knowledge, uncertainty, and free association

You may use ReadingMemory for a callback only when it genuinely clarifies the chosen quote. Write the callback naturally in visible prose. Never expose internal ids or coordinates. If prior context is not needed, do not force a connection.

For real historical facts, editions, biography, allusions, or external sources, state them as facts only when the current source unit or ReadingMemory already provides enough support. If verification is needed but unavailable, preserve the uncertainty instead of inventing the answer. If the uncertainty itself is not useful to the reader, skip it.

### Final Quality Checks

Before emitting each Marginalia item, apply three checks:

- Omission test: without this mark, what specific thing would the reader miss or later fail to find?
- Minimal intervention test: would the quote alone be enough? If yes, use highlight-only instead of writing content.
- Return-to-text test: does the note send the reader back to a specific word, phrase, syntax, structure, fact, or local relation in the quote?

Only emit Marginalia when the expected value exceeds the cost of interrupting the reading flow. For highlight-only, the cost is low but the quote still needs real rereading value. For note-bearing Marginalia, the content must provide a concrete cognitive increment.

## Candidate Output Contract Text

The following text is written as a candidate replacement for the Marginalia-related parts of `<ReturnFormat>` and `<MarginaliaField>`.

### ReturnFormat Excerpt

```json
{
  "understanding": "...",
  "response": "...",
  "marginalia": [
    {
      "source_quote": "...",
      "content": ""
    }
  ]
}
```

### MarginaliaField

`marginalia` contains source-anchored visible margin marks for the current source unit.

Each item has:

- `source_quote`: required exact contiguous quote from the current source unit.
- `content`: optional note content. Empty, `null`, or omitted `content` means highlight-only. Non-empty `content` means note-bearing Marginalia.

Do not output `mode`, `kind`, `decision`, `hook`, `intent`, `evidence_status`, `calibration`, `prior_link`, `outside_link`, `search_intent`, source coordinates, or internal ids.

## Candidate Adjacent Prompt Edits

These are small companion edits to keep the Marginalia prompt coherent with the rest of Digest.

### CurrentStep Addendum

Candidate addition:

```text
Marginalia may be highlight-only or note-bearing; decide this through the Marginalia rules and output contract rather than by adding extra labels.
```

Reason:

- Makes highlight-only part of the top-level Digest action without overloading CurrentStep.

### UnderstandingField Addendum

Candidate addition:

```text
Do not turn Understanding into a list of possible Marginalia. Local quote-level close reading belongs in Marginalia when it is worth showing beside the source text.
```

Reason:

- Prevents rich Marginalia thinking from bloating the memory-facing Understanding field.

### ResponseField Addendum

Candidate addition:

```text
Keep Response as whole-unit aftertaste. If a thought belongs to one exact quote and should be visible in the margin, put it in Marginalia instead.
```

Reason:

- Maintains the boundary between whole-unit response and source-span Marginalia.

### SourceGrounding Addendum

Candidate addition:

```text
Highlight-only and note-bearing Marginalia follow the same grounding rule: every `source_quote` must be an exact contiguous span from the current unit.
```

Reason:

- Keeps highlight-only marks under the same source-coordinate discipline as notes.

### ResponseDiscipline Addendum

Candidate addition:

```text
Do not output calibration fields, hidden planning labels, source coordinates, or implementation metadata. The final Marginalia item contains only `source_quote` and optional `content`.
```

Reason:

- Prevents few-shot explanation fields from leaking into final output.

## Few-Shot Calibration Examples

These examples illustrate only the `marginalia` field. In the full Digest result, the model must still also return top-level `understanding` and `response` according to the OutputContract.

### Case 1: Skip A Structural Transition

Text:

```text
下面分别讨论这三个方面。
```

Why:

This is only a transition. It does not need to be found later, and there is no local cognitive increment worth preserving.

Output:

```json
{
  "marginalia": []
}
```

### Case 2A: Highlight-Only

Text:

```text
庭下如积水空明，水中藻荇交横，盖竹柏影也。
```

Why:

If the purpose is simply to preserve the image for later return, the quote itself carries the value.

Output:

```json
{
  "marginalia": [
    {
      "source_quote": "庭下如积水空明，水中藻荇交横，盖竹柏影也。",
      "content": ""
    }
  ]
}
```

### Case 2B: Note-Bearing Close Reading

Text:

```text
庭下如积水空明，水中藻荇交横，盖竹柏影也。
```

Why:

If the purpose is to notice how the visual effect is produced, the note should explain the local mechanism.

Output:

```json
{
  "marginalia": [
    {
      "source_quote": "盖竹柏影也",
      "content": "The first two clauses make moonlight and tree shadows look like water and waterweeds; only the final clause, with \"盖\", reveals the misrecognition. The sentence works as a small process of perception and correction."
    }
  ]
}
```

### Case 3: Avoid Generic Praise

Text:

```text
孔乙己是站着喝酒而穿长衫的唯一的人。
```

Why:

The useful note is not "this vividly portrays Kong Yiji", but the specific contradiction between two social markers.

Output:

```json
{
  "marginalia": [
    {
      "source_quote": "站着喝酒而穿长衫",
      "content": "\"Standing\" and the long gown normally belong to different kinds of customers; putting them together compresses Kong Yiji's suspended class position into one bodily posture."
    }
  ]
}
```

### Case 4: Correct A Common Misreading

Text:

```text
吾生也有涯，而知也无涯。以有涯随无涯，殆已。
```

Why:

The note should anchor on the latter clause because it changes the first clause from an exhortation to study into a warning about finite life chasing infinite knowledge.

Output:

```json
{
  "marginalia": [
    {
      "source_quote": "以有涯随无涯，殆已",
      "content": "The latter clause restrains an isolated reading of the first: this is not simply praising endless learning, but warning that finite life can be endangered by pursuing the infinite without limit."
    }
  ]
}
```

### Case 5: Preserve An Argument Hinge

Text:

```text
今人乍见孺子将入于井，皆有怵惕恻隐之心……由是观之，无恻隐之心，非人也。
```

Why:

The useful note preserves the reasoning bridge from a concrete sudden reaction to a universal claim about human nature.

Output:

```json
{
  "marginalia": [
    {
      "source_quote": "由是观之",
      "content": "The argument moves from a spontaneous reaction in one extreme scene to a universal claim about human nature. The hinge worth testing is whether that one reaction can support the conclusion about everyone."
    }
  ]
}
```

### Case 6A: Preserve Uncertainty Without Inventing Context

Text:

```text
什么'君子固穷'，什么'者乎'之类……
```

Why:

The phrase appears to invoke established classical language, but if the current source unit and ReadingMemory do not verify the source context, the note should preserve uncertainty rather than invent the allusion's function.

Output:

```json
{
  "marginalia": [
    {
      "source_quote": "君子固穷",
      "content": "This appears to invoke classical language, but the current reading context is not enough to confirm the source, original setting, or how Kong Yiji may be altering it."
    }
  ]
}
```

### Case 6B: Use Verified Context Only When Provided

Text:

```text
什么'君子固穷'，什么'者乎'之类……
```

Available ReadingMemory:

```text
The phrase "君子固穷" comes from 《论语·卫灵公》: "君子固穷，小人穷斯滥矣。"
```

Why:

Because the verified source context is present in the provided reading context, the note can explain the local irony.

Output:

```json
{
  "marginalia": [
    {
      "source_quote": "君子固穷",
      "content": "In the original saying, being \"qiong\" means holding to one's principles in hardship. Kong Yiji invokes it while excusing himself, turning moral self-restraint into self-exoneration and deepening the irony."
    }
  ]
}
```

## Implementation Implications If Promoted

If this candidate is accepted later, implementation should include:

- bump Digest prompt / XML / promptset / output-contract ids
- update the live `<Marginalia>` instruction text
- update `<ReturnFormat>` and `<MarginaliaField>` to remove inherited metadata fields
- update final-output tool schema so `content` is optional / nullable or empty-string tolerant
- update runtime normalization so highlight-only items with exact `source_quote` are kept instead of dropped
- keep backward-compatible reading of legacy `annotations[]` and legacy metadata fields from old artifacts
- update tests for highlight-only, note-bearing, omitted content, exact quote validation, no extra calibration fields, and legacy compatibility
