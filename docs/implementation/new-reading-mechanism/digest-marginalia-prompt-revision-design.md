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

Potential review questions:

- Should Marginalia be allowed to callback to ReadingMemory?
- If callbacks are allowed, should they appear only in `content` / `prior_link`, never as hidden internal ids?
- Should prior-memory use be forbidden for highlight-only items?

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

Potential review questions:

- How should the prompt distinguish highlight-only from note-bearing Marginalia?
- Should the model output an explicit `kind` / `mode`, or should runtime derive highlight vs note from whether `content` is present?
- Should Marginalia have a quantity cap, a soft density guide, or no cap?
- Should research-needed items use `search_intent`, or should they become note content with an uncertainty phrase?
- How much theory belongs in live prompt versus design/sourcebook reference?

The current user-provided Marginalia draft is preserved verbatim below for review.

#### User Draft: Marginalia Prompt Source Text

```markdown
After reading and understanding this section, you may mark the high-quality content within it, and you may also write your own marginalia.
# I. The Value and Significance of Marginalia
## Characteristics of Reading
1. For the book being read:
1) No book is entirely self-sufficient. Classic works especially tend to bury the author's hidden intentions, the subtext of their era, and meanings that can be reactivated by different eras.
2) No book is entirely independent. A work may, together with other works and information, form a theoretical framework, a body of knowledge, or a thread of inquiry.
1. For the reader, **purely individual reading is severely limited when facing complex texts**.
We do not live in a vacuum. We are bounded by our era, our cultural background, and our personal experience. Zhiyanzhai could perceive much of Cao Xueqin's "real story" (*benshi*) because he lived in the same cultural context as the author; Nabokov could analyze structure so precisely because he was himself a top-tier literary craftsman; and other readers on WeChat Read may, drawing on contemporary life experience similar to ours, offer interpretations that resonate strongly with you or spark insight.
## The Significance of Marginalia
1. For the marginalia writer
Writing marginalia forces (or guides) us into "active, structured thinking."
1. For other readers
When others read your marginalia, they are essentially **borrowing your cognitive resources to extend the boundaries of their own understanding**.
## The Essence of Marginalia
**Underlining and highlighting are markers of attention, whereas marginalia are the traces of thought.**
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
These examples are for learning the decision boundary; you are not required to imitate their subject matter, wording, or structure.
In formal output, produce the specified content according to the output contract.
- case: 1
purpose: "Sparse marginalia; grasping the main thread of the text"
text: "下面分别讨论这三个方面。"
output:
decision: SKIP
calibration:
reason: "Merely a structural transition; no independent recall value, and no cognitive increment that needs to be externalized and preserved."
- case: 2A
purpose: "Collecting text and imagery worth rereading"
density: "sparse"
text: "庭下如积水空明，水中藻荇交横，盖竹柏影也。"
output:
decision: HIGHLIGHT
anchor: "庭下如积水空明，水中藻荇交横，盖竹柏影也。"
calibration:
reason: "The text itself already completes its expression; the current purpose only requires being able to find it again later."
- case: 2B
purpose: "Studying how prose creates visual effects"
density: "balanced"
text: "庭下如积水空明，水中藻荇交横，盖竹柏影也。"
output:
decision: NOTE
hook: "Leverage"
intent: "Unpack how the illusion of the water scene is formed"
anchor: "盖竹柏影也"
note: >
The first two clauses render the moonlight and tree shadows as "still water" and "waterweeds";
only the final clause, with "盖" (it turns out), reveals the truth. The scene is not a static display
but a perceptual process of "misrecognition—correction."
evidence_status: "textual interpretation"
calibration:
reason: "The same original text shifts from an object of recall to an object of analysis as the reading purpose changes."
- case: 3
purpose: "Close reading of a fictional character and narrative technique"
context: "Earlier text explains that the short-coated crowd drink standing up, while customers in long gowns go inside to sit and drink."
text: "孔乙己是站着喝酒而穿长衫的唯一的人。"
output:
decision: NOTE
hook: "Leverage"
intent: "Reveal how two identity markers jointly shape the character"
anchor: "站着喝酒而穿长衫"
note: >
"Standing" and "the long gown" originally belong to two different classes of customer;
two mutually conflicting identity markers fall on Kong Yiji at once,
compressing his suspended class status into a single bodily posture.
evidence_status: "textual interpretation"
rejected_output:
note: "This sentence vividly portrays Kong Yiji's tragic fate."
reason: "Only evaluation, with no account of which textual mechanism produces the effect."
- case: 4
purpose: "Understanding a philosophical text and preventing quotation out of context"
text: "吾生也有涯，而知也无涯。以有涯随无涯，殆已。"
output:
decision: NOTE
hook: "Resistance"
intent: "Use the latter clause to correct an isolated reading of the former"
anchor: "以有涯随无涯，殆已"
note: >
Quoting only the first clause makes it easy to read as a simple exhortation to study;
the latter clause, however, turns the momentum toward a warning: if a finite life endlessly
pursues infinite knowledge, it instead falls into danger. The leverage of understanding lies in
the latter clause's constraint on the former.
evidence_status: "textual observation + textual interpretation"
- case: 5
purpose: "Analyzing argumentative structure rather than simply agreeing or disagreeing"
text: >
今人乍见孺子将入于井，皆有怵惕恻隐之心……
由是观之，无恻隐之心，非人也。
output:
decision: NOTE
hook: "Leverage"
intent: "Reconstruct the inference from a concrete reaction to universal human nature"
anchor: "由是观之"
note: >
The argument first excludes interested motives such as social ties and reputation,
then interprets the compassionate reaction in a sudden situation as the beginning of a universal moral capacity.
The reasoning bridge worth testing is:
can a reaction in one extreme moment sufficiently support a conclusion about "everyone"?
evidence_status: "textual interpretation"
- case: 6A
purpose: "Identifying an allusion and its function in the novel"
retrieval_available: false
text: "什么'君子固穷'，什么'者乎'之类……"
output:
decision: RESEARCH
hook: "Resistance"
intent: "Verify the allusion's source and judge whether the character has altered its original meaning"
anchor: "君子固穷"
note: >
This is clearly invoking established classical language, but the current material is insufficient to confirm the source,
the original context, and its contrast with Kong Yiji's situation.
evidence_status: "to be verified"
- case: 6B
purpose: "Identifying an allusion and its function in the novel"
retrieval_available: true
text: "什么'君子固穷'，什么'者乎'之类……"
verified_source: "《论语·卫灵公》：君子固穷，小人穷斯滥矣。"
output:
decision: NOTE
hook: "Growth"
intent: "Explain the ironic appropriation of the allusion in the new context"
anchor: "君子固穷"
note: >
In the original classic, "qiong" (being in dire straits) means holding to one's principles even in hardship.
Kong Yiji, however, invokes this line while justifying his own behavior,
turning moral self-restraint into self-exoneration; the gap between the allusion's original meaning and the character's use of it
deepens the irony.
evidence_status: "external fact + textual interpretation"
source: "《论语·卫灵公》"
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

Potential review questions:

- Should this block forbid hidden calibration fields such as `decision`, `hook`, `intent`, `evidence_status`, and `calibration` unless the output contract explicitly asks for them?
- Should it distinguish visible user text from metadata fields?

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

Potential review questions:

- Should Marginalia content be allowed to reference prior Understanding?
- Should `prior_link` point to prior memory ids or be derived by runtime?
- Should highlight-only items avoid prior links?

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
      "content": "...",
      "prior_link": null,
      "outside_link": null,
      "search_intent": null
    }
  ]
}
```

Potential review questions:

- Should `content` become optional or nullable to represent highlight-only Marginalia?
- Should the model output an explicit `mode` such as `highlight` / `note`, or should runtime derive mode from `content`?
- Are `prior_link`, `outside_link`, and `search_intent` still model-authored fields, runtime-derived fields, or future-only metadata?
- Should `marginalia[]` item validation require exact quote presence but allow empty content?

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

Potential review questions:

- Should this field become the canonical place for highlight-only vs note-bearing output rules?
- Should metadata fields be described as rare and optional?
- Should the contract say "do not output calibration fields"?

### 17. Final-Output Tool Schema

Current role:

- Requires top-level `understanding`, `response`, and `marginalia`.
- Allows each Marginalia item to include `source_quote`, `content`, `prior_link`, `outside_link`, and `search_intent`.

Potential review questions:

- Does the schema need `content` to be optional for highlight-only?
- Should `prior_link`, `outside_link`, and `search_intent` stay as object/null fields or move into a more compact metadata object?
- Should a future schema add `mode`, or should that remain runtime-derived?

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

This document does not settle the output contract yet. The current working direction to review is:

```json
{
  "source_quote": "...",
  "content": ""
}
```

Interpretation:

- `source_quote` is required.
- Empty or omitted `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- `prior_link`, `outside_link`, and `search_intent` remain candidate optional metadata, but should not burden normal Marginalia output.
- A separate `mode` field is optional and should be added only if runtime/frontend ambiguity requires it.

## Review Order

Suggested review sequence:

1. Decide the Marginalia concept: highlight-only plus note-bearing marks.
2. Decide the minimal output contract for one Marginalia item.
3. Rewrite the Marginalia instruction block around that contract.
4. Convert few-shot examples so they output only fields allowed by the contract.
5. Adjust SourceGrounding and ResponseDiscipline to enforce exact quote and no extra calibration fields.
6. Decide whether Understanding and Response need narrow edits or should stay unchanged.
7. Implement prompt/schema/runtime changes in a later code slice after this design is reviewed.
