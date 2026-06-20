# Digest Marginalia Prompt Revision Design

Purpose: provide a review workspace for revising the Digest prompt, especially the Marginalia selection and output contract.
Use when: discussing or drafting changes to live Digest prompt structure, Marginalia quality policy, highlight/note behavior, or Marginalia output fields.
Not for: current live runtime authority, historical eval artifacts, or formal evidence promotion.
Update when: a reviewed Marginalia prompt draft changes, the candidate output contract changes, or a Digest prompt section is accepted for implementation.

Created: `2026-06-20`

## Status

- Status: candidate design / review draft.
- Live prompt unchanged by this document.
- Current live Digest baseline:
  - prompt version: `attentional_v2.digest.v10`
  - XML spec: `attentional_v2.digest.xml.v10`
  - promptset: `attentional_v2-phase6-v68`
  - output contract: `digest_understanding_response_marginalia_json_v4`
- Current live model-facing outputs:
  - `understanding`
  - `response`
  - `marginalia[]`
- Current implementation caveat:
  - The live schema exposes `marginalia[].source_quote` and `marginalia[].content`.
  - The current runtime normalizer requires both `source_quote` and `content` to be non-empty.
  - A pure highlight-only Marginalia item therefore needs an output-contract/runtime revision before it can be represented cleanly as `source_quote` without note content.
- Working output-contract direction:
  - The next model-facing Marginalia item should contain only `source_quote` and `content`.
  - `source_quote` is required.
  - `content` may be omitted or empty; omitted / empty `content` means highlight-only.
  - Non-empty `content` means note-bearing Marginalia.
  - Do not add `mode`, `kind`, `decision`, or inherited optional metadata to the normal model-facing Marginalia item unless a later product/runtime design explicitly reintroduces it.

## Design Goal

Revise the Digest prompt so Marginalia becomes a stronger user-visible reading surface:

- Marginalia should cover both highlight-only marks and note-bearing marks.
- Highlight-only means the source quote itself is worth preserving, and no added note is necessary.
- Note-bearing Marginalia means the quote needs a reader-visible thought, explanation, question, connection, or judgment to preserve its value.
- The prompt should help the model avoid generic annotation, forced commentary, unsupported external knowledge, and note inflation.
- Any final output-contract change must stay compatible with source anchoring and frontend highlight behavior.

## Digest Prompt Structures To Review

This revision may touch more than the Marginalia block. The review surface is organized around the current live Digest prompt structure.

### 1. Transport / System Prompt

Current role:

- Instruct the model to follow the structured Digest prompt.
- Tell it to use `submit_digest_result` as the final output channel.

Potential review questions:

- Does the final-output channel need wording that distinguishes highlight-only Marginalia from note-bearing Marginalia?
- Does the transport wording need to mention compatibility with JSON-object structured output, or should that stay gateway/runtime-only?

### 2. ReaderRole

Current role:

- Establish the model as the current reader moving through the book.
- Shared across prompt families through the common reader role fragment.

Potential review questions:

- Should the reader role explicitly say that visible Marginalia are written for the user in the margin?
- Or should that remain entirely inside the Marginalia block?

### 3. Instruction / CurrentStep

Current role:

- Tell Digest it is reading the next source unit in sequence.
- Frame the current source unit as the present moment of reading.
- State that output has three connected parts: `understanding`, `response`, and `marginalia`.

Potential review questions:

- Should CurrentStep name highlight-only and note-bearing Marginalia at the top level?
- Should CurrentStep stay compact and leave Marginalia detail to the dedicated block?

### 4. Instruction / ContextUseGuide

Current role:

- Distinguish BookInfo, ReadingMemory, CurrentFocus, and OutputContract.
- Tell the model how prior ReadingMemory may support continuity without becoming current source text.

Current working answer:

- Note-bearing Marginalia may naturally callback to ReadingMemory when that genuinely helps the reader understand why the quoted span matters.
- Any callback should appear in visible `content`, written as normal reader-facing prose.
- Do not expose hidden internal ids, source span ids, memory ids, reaction ids, or coordinate-like tokens.
- Highlight-only items should not carry hidden prior-memory metadata; if a prior connection needs to be visible, the item should become note-bearing Marginalia with non-empty `content`.

### 5. Instruction / Understanding

Current role:

- Produce one compact source-established understanding of the current source unit.
- Store the content needed for continued reading.
- Keep it distinct from reader response and Marginalia.

Potential review questions:

- Should the Understanding block mention that quote-level close reading belongs in Marginalia, not Understanding?
- Should it warn against turning Understanding into a list of potential Marginalia?
- Should it stay unchanged while Marginalia is revised?

### 6. Instruction / Response

Current role:

- Produce a brief natural reader response after understanding the unit.
- Keep it distinct from source-faithful Understanding and span-anchored Marginalia.

Potential review questions:

- Should Response be allowed to mention the same local trigger as Marginalia?
- Should Response be shortened if Marginalia is rich?
- Should Response stay as whole-unit aftertaste, while Marginalia stays local and source-anchored?

### 7. Instruction / Marginalia

Current role:

- Select exact source spans worth visible page-margin notes.
- Avoid forced notes.
- Keep source quotes exact and local.
- Allow zero or multiple Marginalia items.

Current working answer:

- Distinguish highlight-only from note-bearing Marginalia by `content`: empty / omitted `content` is highlight-only; non-empty `content` is note-bearing.
- Do not output an explicit `kind` / `mode` field in this slice.
- Use a soft density guide rather than a hard cap: emit zero items when nothing is worth marking, and avoid manufacturing notes to fill space.
- Research-needed material should become visible note content only when the uncertainty itself is valuable to preserve for the reader. Do not use `search_intent` in the normal live output contract.
- Keep most theory in this design/sourcebook layer. The live prompt should carry only the compact decision rules that help the model choose and write better Marginalia.

The current user-provided Marginalia draft is preserved verbatim below for review.

#### User Draft: Marginalia Prompt Source Text

```markdown
**A highlight marks attention; a note records thought. If the quote itself preserves the value, produce highlight-only. If the value requires explanation, question, connection, or judgment, add note content.**
You may also write your own marginalia.These marginalia helps others borrowing your cognitive resources to extend the boundaries of their own understanding.

# II. Conditions for Marginalia
**Within the flow of reading, attention is snagged somewhere by the text, producing a "cognitive change" worth preserving or expressing.**
## 1. Resistance: this passage cannot be smoothly absorbed — what cannot be stably understood right now?
Have you found some obstacle to understanding or some instability:
- Compressed concepts, leaps in argument;
- Ambiguity, contradiction, or vagueness;
- Unfamiliar allusions, historical background, technical terms;
- The narrator's and characters' stances are hard to distinguish;
- A fact, causal relation, or authorial intent needs verification;
- The translation may obscure features of the original.
...
The marginalia intentions it may trigger:
> Clarify a concept, unpack an argument, reconstruct context, verify facts, compare translations, raise a question...
>
## 2. Leverage: this local part significantly alters understanding of the whole — what is rewriting the understanding already formed?
Some text carries disproportionate explanatory power:
- A key definition;
- A turning point in the argument or narrative;
- A recurring image that changes at this moment;
- A foreshadowing, echo, irony, or shift in perspective;
- A seemingly minor action that nonetheless reveals character relationships;
- A sentence that redefines what was read earlier.
...
The marginalia intentions it may trigger:
> Reveal structure, explain technique, point out a turn, connect what comes before and after, expose implicit premises, reread earlier content...
>
### 3. Growth: this passage opens a direction worth continuing to track — where does this passage lead me?
This is not necessarily an obstacle to understanding, nor necessarily a pivot of the whole book, but it generates new possibilities:
- Forms connections with other works, theories, or events;
- Leads to a valuable question or counterexample;
- Can be transferred to real-world problems or personal experience;
- Produces strong emotional, aesthetic, or ethical tension;
- Provides a research lead worth developing later;
- Makes the reader aware of their own presuppositions or limitations.
...
The marginalia intentions it may trigger:
> Connect, compare, rebut, apply, probe further, record feelings, generate hypotheses...
>
# III. How to Write Marginalia
## Mode of Intervention: Highlight or Note?
Attention being snagged does not mean you must write a full note. **Do not write marginalia for the sake of marginalia** — it depends on whether the passage has produced a "cognitive change" worth externalizing and preserving.
The principle of **minimal necessary intervention**:
1. Highlight: worth finding later, but the meaning is already self-evident, so highlighting is enough.
For example, a sentence is beautiful and well-suited for rereading later, but for now there is nothing that needs explaining; the model should only suggest a highlight, rather than forcing out a note like "this sentence expresses profound emotion through beautiful language."
1. Note: a relationship, explanation, question, or judgment must be written out for the value to be preserved; or the value may be high but depends on verifying editions, historical facts, allusions, or external sources...
## What to Write in a Note
If viewed in terms of **"the direction of attention radiating out from the current reading point,"** it may be:
Inward (the text's own mechanisms) → formal close reading
Backward / surrounding (the scene of production) → contextual reconstruction
Outward (the larger network of knowledge) → knowledge supplementation
Counter-directional (resistance, questioning) → critique
Toward the reader themselves (resonance, memory, being moved) → personal response
Forward (anticipation, suspense, questioning) → questioning
...
(Of course there is no need to scan item by item, nor any requirement to cover any of these directions.)
For example, you may:
- **Knowledge supplementation**: any text is a node in a larger network of knowledge; look for the theoretical frameworks, historical dialogues, and echoes of other texts it may participate in. Eliot appended extensive notes on allusions to *The Waste Land*, helping readers identify mythological, religious, and literary sources. *Buque* (filling gaps): adding material omitted from the main text. *Beiyi* (preserving variants): preserving different accounts of the same event;
- **Content decomposition**
Like Nabokov's close reading, **perform a structured, layered decomposition of the text, searching for its internal correspondences, echoes, ironies, and formal design.** An ordinary reader might only say: "this passage is very tense," "this character is very vivid." Jin Shengtan, by contrast, **tries to explain how such effects are produced: how a character makes their entrance, how the narrative is delayed, how scenes mirror one another, how information is hidden and released,** touching on multiple levels — story and discourse, time and space, narrative grammar, and narrative rhetoric.
- **Contextual reconstruction**
Like the **classical Chinese commentary (*pingdian*) tradition,** marginalia can preserve the scene of a work's production. Often, the true meaning of a passage lies not in what it says but in what "could not be said" or "could only be said this way" within its cultural context at the time. Marginalia in Zhiyanzhai often does not explain "what was written" but rather restores "why it had to be written this way." For instance, Zhiyanzhai's commentary on *The Story of the Stone*: the most typical is the commentary on the death of Qin Keqing. The Zhi commentary left traces of the revision of the "Tianxiang Pavilion" plot, and, using phrases like "writing by not writing" and "deleted, yet an undeleted stroke," prompts readers to reconstruct the deleted narrative from the gaps, anomalies, and remnants of the surviving text.
- Questioning the argument;
- Emotional response;
- Prediction and hypothesis;
- Meta-reading reflection;
- Other moves...
## Producing a Note — Thinking and Recording
Around the text where attention rests, you may think from more than one direction; within each direction:
1. First generate an open-ended "verb + object" intention, for example:
"Unpack how this passage delays key information"
"Verify the historical time implied here"
"Connect this image with its first appearance in Chapter 3"
"Question the leap from an individual case to a universal conclusion"
"Record the ethical discomfort triggered here and its causes"
1. With that intention as the goal, think, and record your thoughts.
## Principles to Follow
**Add evidence, not just attitude. Show reasoning, not just announce conclusions. Distinguish fact, conjecture, and free association.**
...
### **The Cognitive Honesty Contract**
[In-text inference] — holds based on the given passage alone (most credible)
[Common knowledge] — general literary/narrative knowledge, low risk
[Requires verification] — assertions involving real historical facts / editions / the author's biography must provide checkable evidence (edition name, commentary, historical sources);
if none can be given → downgrade to "association" and explicitly state the evidence gap
[Don't know] — **better to leave it blank; fabricating the "real story" (*benshi*) is forbidden**
### Valuable
- Explicitly forbid clichés: "Uninformative evaluations such as 'this passage is tense' or 'this character is vivid' are forbidden; you must explain how the effect is produced."
## Checking the Marginalia
Every candidate note must first pass three tests.
### 1. The Omission Test
> Without this note, what specifically would the reader miss, and what might they later forget?
>
The answer must be specific, for example:
> They would treat this sentence as ordinary scene description and miss its hint about the power relations between characters.
>
> This is a very beautiful / very important sentence; without highlighting it, it may be hard to find later.
>
> They would fail to see the background information behind this passage.
>
...
If you can only answer in generalities, you have not yet found a genuine cognitive increment.
### 2. The Minimal Intervention Test
> Would a plain highlight already suffice?
>
If the note merely repeats "this is important" or "this is well written," you should fall back to a highlight, or even skip it.
### 3. The Return-to-Text Test
> Can this note send the reader back to a specific word, syntax, structure, or fact?
>
Associations that cannot be precisely anchored to the original text should usually be deleted.
The final threshold can be written as a conceptual formula:
> **Only add marginalia when the expected cognitive increment exceeds the cost of interrupting reading.**
>
# Few-shot Calibration Examples
These examples are for learning the boundary between skip, highlight-only, and note-bearing Marginalia. In formal output, use only the fields allowed by the output contract.

- Case 1: structural transition
Text: "下面分别讨论这三个方面。"
Why: This is only a transition. It does not need to be found later, and there is no local cognitive increment worth preserving.
Output: {"marginalia": []}

- Case 2A: same text, highlight-only
Text: "庭下如积水空明，水中藻荇交横，盖竹柏影也。"
Why: If the reading purpose is simply to preserve beautiful imagery for later return, the quote itself carries the value.
Output: {"marginalia": [{"source_quote": "庭下如积水空明，水中藻荇交横，盖竹柏影也。", "content": ""}]}

- Case 2B: same text, note-bearing
Text: "庭下如积水空明，水中藻荇交横，盖竹柏影也。"
Why: If the reading purpose is to study how the visual effect is produced, the note should explain the local mechanism.
Output: {"marginalia": [{"source_quote": "盖竹柏影也", "content": "The first two clauses make moonlight and tree shadows look like water and waterweeds; only the final clause, with \"盖\", reveals the misrecognition. The sentence works as a small process of perception and correction."}]}

- Case 3: close reading without generic praise
Text: "孔乙己是站着喝酒而穿长衫的唯一的人。"
Why: The useful note is not "this vividly portrays Kong Yiji," but the specific contradiction between two social markers.
Output: {"marginalia": [{"source_quote": "站着喝酒而穿长衫", "content": "\"Standing\" and the long gown normally belong to different kinds of customers; putting them together compresses Kong Yiji's suspended class position into one bodily posture."}]}

- Case 4: quote selection that corrects a common misreading
Text: "吾生也有涯，而知也无涯。以有涯随无涯，殆已。"
Why: The note should anchor on the latter clause, because it changes the first clause from an exhortation to study into a warning about finite life chasing infinite knowledge.
Output: {"marginalia": [{"source_quote": "以有涯随无涯，殆已", "content": "The latter clause restrains an isolated reading of the first: this is not simply praising endless learning, but warning that finite life can be endangered by pursuing the infinite without limit."}]}

- Case 5: argumentative structure
Text: "今人乍见孺子将入于井，皆有怵惕恻隐之心……由是观之，无恻隐之心，非人也。"
Why: The useful note preserves the reasoning bridge from a concrete sudden reaction to a universal claim about human nature.
Output: {"marginalia": [{"source_quote": "由是观之", "content": "The argument moves from a spontaneous reaction in one extreme scene to a universal claim about human nature. The hinge worth testing is whether that one reaction can support the conclusion about everyone."}]}

- Case 6A: research-needed note without verified context
Text: "什么'君子固穷'，什么'者乎'之类……"
Why: The phrase clearly invokes established classical language, but without verified source context the note should preserve the uncertainty rather than inventing the allusion's function.
Output: {"marginalia": [{"source_quote": "君子固穷", "content": "This appears to invoke classical language, but the current text is not enough to confirm the source, original context, or how Kong Yiji may be altering it."}]}

- Case 6B: research context available
Text: "什么'君子固穷'，什么'者乎'之类……"
Why: If the source context is verified as 《论语·卫灵公》, the note can explain how the allusion is being ironized in the new scene.
Output: {"marginalia": [{"source_quote": "君子固穷", "content": "In the original saying, being \"qiong\" means holding to one's principles in hardship. Kong Yiji invokes it while excusing himself, turning moral self-restraint into self-exoneration and deepening the irony."}]}
```

#### Assistant Draft: Marginalia Prompt Candidate

```markdown
# Marginalia

After reading and understanding the current source unit, decide whether any exact quote from this unit should be preserved in the margin.

Marginalia are source-anchored reading marks. They are not passage summaries, generic annotations, metadata labels, or a place to prove cleverness. A good Marginalia item helps the reader notice, remember, question, or return to something specific at the exact quoted words.

## Two Forms

Marginalia can be either highlight-only or note-bearing.

- Highlight-only: use this when the quote itself is worth finding again, and adding a note would only repeat or dilute its value. Output an exact `source_quote`; leave `content` empty or omit it according to the output contract.
- Note-bearing: use this when a relationship, explanation, question, connection, or judgment must be written down for the value to survive. Output an exact `source_quote` plus concise reader-visible `content`.

Do not create Marginalia just to fill the field. It is normal to emit zero items when nothing in the current unit is worth marking.

## What Makes A Quote Worth Marking

Use the following lenses silently. Do not output these labels.

1. Resistance: the quote creates friction in understanding.
   It may contain ambiguity, a compressed concept, an argumentative leap, a hard-to-place stance, an allusion, a translation issue, or a factual claim that needs verification.

2. Leverage: the quote changes the meaning of the current unit or the larger reading.
   It may be a key definition, a hinge in the argument or scene, a turn in character relation, a repeated image, a foreshadowing, an irony, a shift of perspective, or a sentence that rereads earlier material.

3. Growth: the quote opens something worth carrying forward.
   It may lead to a useful question, a comparison with another work or idea, a research lead, an ethical or emotional pressure, a transferable insight, a hypothesis, or a recognition of the reader's own assumption.

A quote does not need to satisfy all three lenses. One real trigger is enough; a vague sense that the passage is "important" is not enough.

## Minimal Intervention

Before producing each candidate Marginalia item, ask:

1. Should this source span be marked at all?
   If it is only a transition, filler, repeated information, or a detail with no return value, skip it.

2. Would a highlight already be enough?
   If the quote is beautiful, forceful, memorable, or worth finding later, but its meaning is already self-evident, use highlight-only.

3. If writing a note, what would the reader miss without it?
   The answer must be specific: a mechanism, relation, tension, inference, uncertainty, callback, or question.

4. Can the note send the reader back to exact words in the quote?
   If the note cannot return to a word, syntax, image, structure, claim, or fact in the source quote, delete it or choose a better quote.

Choose the smallest exact contiguous `source_quote` that can honestly support the item. Do not use ellipses, stitched fragments, paraphrases, translations, source coordinates, or paragraph numbers as the quote.

## Writing Note Content

For note-bearing Marginalia, write the content as a compact margin note for the reader. The note may:

- unpack how a local effect is produced;
- name a distinction, tension, turn, or inference;
- connect this quote to prior ReadingMemory when the connection is genuinely useful and source-supported;
- raise a precise question or uncertainty;
- mark a research lead without pretending it has been verified;
- record an emotional, aesthetic, or ethical response when the response is anchored in the quote itself.

Use a silent "verb + object" intention if it helps you think, such as "unpack how this sentence delays the reveal" or "question the inference from one case to everyone." Do not output that intention unless the output contract explicitly asks for it.

## Evidence And Honesty

Add evidence, not just attitude. Show the reason for the note, not just the conclusion.

- In-text interpretation is the safest: base the note on the current source quote and current unit.
- ReadingMemory may be used for continuity or callback, but only when it directly clarifies why this quote matters. Do not expose internal ids or coordinate-like tokens.
- Common literary or narrative knowledge may be used cautiously, but do not turn it into unsupported certainty.
- If a historical fact, edition issue, biography claim, allusion source, or translation claim needs verification and the verified context is not present in CurrentFocus or ReadingMemory, do not state it as fact. Mark the uncertainty as uncertainty, or skip the note.
- It is better to leave a note unwritten than to fabricate hidden background, authorial intent, or a "real story" behind the text.

Avoid empty praise. A note like "this passage is tense," "this sentence is beautiful," or "this character is vivid" is not enough. Explain what in the quote creates the effect, or use highlight-only.

## Output Discipline

This section explains only the `marginalia` field. The final Digest output must still follow the full OutputContract for `understanding`, `response`, and `marginalia`.

For each Marginalia item:

- `source_quote` must be an exact contiguous quote from the current source unit.
- Empty or omitted `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- Do not output `mode`, `kind`, `decision`, `hook`, `intent`, `evidence_status`, `calibration`, `rejected_output`, `source`, `prior_link`, `outside_link`, or `search_intent` unless a later output contract explicitly asks for them.

## Calibration Examples

These examples show only the `marginalia` field shape.

Case 1: skip a structural transition
Text: "下面分别讨论这三个方面。"
Output:
{"marginalia": []}

Case 2: highlight-only
Text: "庭下如积水空明，水中藻荇交横，盖竹柏影也。"
Why: the image itself is worth finding again, and no note is needed for the current purpose.
Output:
{"marginalia": [{"source_quote": "庭下如积水空明，水中藻荇交横，盖竹柏影也。", "content": ""}]}

Case 3: note-bearing close reading
Text: "庭下如积水空明，水中藻荇交横，盖竹柏影也。"
Why: the note explains how the sentence produces its visual effect.
Output:
{"marginalia": [{"source_quote": "盖竹柏影也", "content": "The first two clauses let moonlight and tree shadows appear as water and waterweeds; only this final phrase reveals the misrecognition. The sentence works as a small movement from perception to correction."}]}

Case 4: avoid generic praise
Text: "孔乙己是站着喝酒而穿长衫的唯一的人。"
Why: the valuable note is not that the sentence is vivid, but how two social markers collide.
Output:
{"marginalia": [{"source_quote": "站着喝酒而穿长衫", "content": "\"Standing\" and the long gown usually belong to different social positions; placing both on Kong Yiji compresses his suspended class status into one bodily posture."}]}

Case 5: note a reasoning hinge
Text: "今人乍见孺子将入于井，皆有怵惕恻隐之心……由是观之，无恻隐之心，非人也。"
Why: the quote marks the bridge from one sudden reaction to a universal claim.
Output:
{"marginalia": [{"source_quote": "由是观之", "content": "This is the argument's hinge: it moves from a concrete spontaneous reaction to a general claim about human nature. The point worth testing is whether that one reaction can support the conclusion about everyone."}]}

Case 6: preserve uncertainty without inventing context
Text: "什么'君子固穷'，什么'者乎'之类……"
Why: the phrase appears to invoke classical language, but if verified context is not present in CurrentFocus or ReadingMemory, do not invent the allusion's source or function.
Output:
{"marginalia": [{"source_quote": "君子固穷", "content": "This appears to invoke established classical language, but the current material is not enough to confirm the source, original context, or how Kong Yiji may be altering it."}]}
```

### 8. Instruction / SourceGrounding

Current role:

- Require exact contiguous `marginalia[].source_quote` from the current unit.
- Prohibit model-authored coordinates.
- Let runtime resolve source quotes to `SourceRef`.

Potential review questions:

- Should highlight-only items follow the same exact-quote rule? Expected answer: yes.
- Should note-bearing items require the note to return to the quote's wording, syntax, structure, or fact?
- Should source quote length guidance move here or remain in Marginalia?

### 9. Instruction / ResponseDiscipline

Current role:

- Avoid broad chapter summaries.
- Avoid explaining whether prior material was used.
- Avoid route decisions.
- Submit final output through the required final-output channel.

Current working answer:

- ResponseDiscipline should forbid hidden calibration fields such as `decision`, `hook`, `intent`, `evidence_status`, `calibration`, `rejected_output`, and `source` in final output.
- The live output should distinguish user-visible text from implementation metadata by excluding implementation metadata from the model-facing Marginalia item.

### 10. BookInfo

Current role:

- Stable book identity: title and author.
- Not source text.

Potential review questions:

- Should author/title influence Marginalia style or only factual orientation?
- Should the prompt warn not to infer author biography from BookInfo alone?

### 11. ReadingMemory

Current role:

- Prompt-facing prior Understanding only.
- Used for continuity, callback, contrast, and unresolved pressure.
- Does not include raw prior source, prior Response, or prior Marginalia in the live prompt.

Current working answer:

- Marginalia `content` may reference prior Understanding in reader-facing prose when the connection is useful and source-supported.
- Do not ask the model to output `prior_link` in the normal Marginalia contract.
- Highlight-only items should avoid hidden prior-link semantics; if a prior callback matters, write a note.

### 12. CurrentFocus

Current role:

- Provides the current mainline reading path.
- Provides current chapter/position.
- Provides the source unit as paragraph text.
- Provides reading intent: `read_current_source_unit_in_sequence`.

Potential review questions:

- Should Marginalia prompt text mention paragraph boundaries? Expected answer: probably no; source quote exactness is enough.
- Should quote anchors be paragraph-local or unit-local? Current runtime accepts exact quote from the current unit.

### 13. OutputContract / ReturnFormat

Current role:

```json
{
  "understanding": "...",
  "response": "...",
  "marginalia": [
    {
      "source_quote": "...",
      "content": "..."
    }
  ]
}
```

Current working answer:

- `source_quote` should be the only required Marginalia item field.
- `content` should be optional or nullable / empty-string tolerant.
- Omitted, `null`, or empty `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- Do not add an explicit `mode` / `kind` field in this slice. Runtime and frontend can derive highlight-only vs note-bearing from `content`.
- Do not include `prior_link`, `outside_link`, or `search_intent` in the normal model-facing Marginalia output contract. These fields entered as inherited visible-reaction metadata during the older Phase E / Express path; keep backward-compatible normalization/persistence if needed, but do not teach the live Marginalia prompt to emit them as ordinary output.
- `marginalia[]` validation should require exact quote presence and tolerate empty content.

### 14. OutputContract / UnderstandingField

Current role:

- Define `understanding` as one self-contained string for ReadingMemory / Unit Memory.

Potential review questions:

- Should it explicitly say that Marginalia-worthy local close reading should not be duplicated into Understanding?
- Should it remain unchanged until Marginalia output format is settled?

### 15. OutputContract / ResponseField

Current role:

- Define `response` as immediate reader expression after the unit.
- Keep it distinct from Understanding and Marginalia.

Potential review questions:

- Should it instruct the model to keep Response shorter when Marginalia already captures local thoughts?
- Should it remain unchanged in the first Marginalia revision slice?

### 16. OutputContract / MarginaliaField

Current role:

- Define item shape.
- Point detailed selection and source-quote behavior back to Instruction.

Current working answer:

- This field should define the minimal item shape and the highlight-only / note-bearing interpretation of `content`.
- Do not describe inherited metadata fields as normal optional fields in the live contract.
- The contract should explicitly say not to output calibration or decision-boundary fields.

### 17. Final-Output Tool Schema

Current role:

- Requires top-level `understanding`, `response`, and `marginalia`.
- Allows each Marginalia item to include `source_quote` and `content`.

Potential review questions:

- Does the schema need `content` to be optional for highlight-only?
- Should legacy `prior_link`, `outside_link`, and `search_intent` continue to be accepted by the normalizer for old artifacts or malformed model outputs without appearing in the live tool schema?
- Should a future schema add `mode`, or should highlight-only remain runtime-derived from empty `content`?

### 18. Runtime Normalization And Settlement

Current role:

- Normalize `marginalia[]` into canonical Digest Marginalia.
- Verify `source_quote` appears in current unit text.
- Drop items with missing quote or missing content under the current implementation.
- Store Marginalia in runtime/audit and Unit Memory surfaces.
- Preserve legacy annotation/reaction aliases for compatibility.

Potential review questions:

- Should highlight-only items be stored as Marginalia with empty content?
- Should the frontend display highlight-only items through the same marks/marginalia surface?
- Should legacy aliases preserve highlight-only semantics after the contract changes?

## Open Output-Contract Direction

Current working decision for the next reviewed Digest Marginalia contract:

```json
{
  "source_quote": "...",
  "content": ""
}
```

Interpretation:

- `source_quote` is required.
- Empty, `null`, or omitted `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- No explicit `mode` / `kind` / `decision` field is needed in this slice.
- `prior_link`, `outside_link`, and `search_intent` should not be part of the normal model-facing Marginalia item. They may remain backward-compatible backend fields for older reaction / annotation / Marginalia artifacts, but should not appear in the live prompt ReturnFormat, final-output tool schema, or few-shot examples.
- Future source-backlink, external-reference, or research-intent behavior should be redesigned as an explicit product/runtime feature rather than hidden inside ordinary Marginalia item metadata.

## Review Order

Suggested review sequence:

1. Decide the Marginalia concept: highlight-only plus note-bearing marks.
2. Decide the minimal output contract for one Marginalia item.
3. Rewrite the Marginalia instruction block around that contract.
4. Convert few-shot examples so they output only fields allowed by the contract.
5. Adjust SourceGrounding and ResponseDiscipline to enforce exact quote and no extra calibration fields.
6. Decide whether Understanding and Response need narrow edits or should stay unchanged.
7. Implement prompt/schema/runtime changes in a later code slice after this design is reviewed.
