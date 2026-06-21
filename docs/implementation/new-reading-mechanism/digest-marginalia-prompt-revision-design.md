# Digest Marginalia Prompt Revision Design

Purpose: provide a review workspace for revising the Digest prompt, especially the Marginalia selection and output contract.
Use when: discussing or drafting changes to live Digest prompt structure, Marginalia quality policy, highlight/note behavior, or Marginalia output fields.
Not for: current live runtime authority, historical eval artifacts, or formal evidence promotion.
Update when: a reviewed Marginalia prompt draft changes, the candidate output contract changes, or a Digest prompt section is accepted for implementation.

Created: `2026-06-20`

## Status

- Status: implemented-live in Digest v17.
- Live prompt now implements the reviewed candidate in `reading-companion-backend/src/attentional_v2/prompts/digest.py`.
- Current live Digest baseline:
  - prompt version: `attentional_v2.digest.v17`
  - XML spec: `attentional_v2.digest.xml.v17`
  - promptset: `attentional_v2-phase6-v77`
  - output contract: `digest_understanding_response_marginalia_json_v7`
- Current live model-facing outputs:
  - `understanding`
  - `response`
  - `marginalia[]`
- Implemented output-contract direction:
  - The model-facing Marginalia item contains `source_quote`, optional `content`, and optional private `selection_reason`.
  - `source_quote` is required.
  - `content` may be omitted or empty; omitted / empty `content` means highlight-only.
  - Non-empty `content` means note-bearing Marginalia.
  - Highlight-only Marginalia must carry a short private `selection_reason` inline on the same item.
  - Note-bearing Marginalia may omit `selection_reason` because visible `content` carries the reason.
  - Do not add `mode`, `kind`, `decision`, or inherited optional metadata to the normal model-facing Marginalia item unless a later product/runtime design explicitly reintroduces it.
- Implemented v12 quality-policy follow-up:
  - Highlight-only now means an exact quote can stand alone as an excerpt worth preserving; another reader should be able to see the reason for marking from the quoted words themselves.
  - Structurally important but context-dependent spans, such as topic sentences, transitions, setup questions, recaps, or argument signposts, should usually stay in Understanding or become note-bearing Marginalia rather than quote-only highlights.
  - The output contract is unchanged from v11 / v5; this is a prompt-selection discipline change, not a schema change.
- Implemented v13 quality-policy follow-up:
  - Highlight-only now has two gates: the quote must stand alone, and it must have intrinsic excerpt value.
  - Self-contained is necessary but not sufficient; a merely complete, informative, or easy-to-locate sentence is not automatically worth highlighting.
  - The intended target is the kind of source text that carries its own value through wording, image, insight, emotional force, conceptual compression, or compact principle.
  - The output contract remains unchanged from v11 / v5.
- Implemented v14 audit follow-up:
  - Highlight-only Marginalia now requires a short private `selection_reason` in `marginalia_audit[]`.
  - Note-bearing Marginalia does not get a private selection reason because the visible `content` is already the reader-facing reason.
  - Product-visible Marginalia remains only `source_quote` plus optional `content`; `marginalia_audit[]` is mechanism-private audit metadata.
- Implemented v15 inline audit follow-up:
  - The private highlight-selection reason moved from top-level `marginalia_audit[]` into `marginalia[].selection_reason`.
  - Highlight-only Marginalia requires inline `selection_reason`; note-bearing Marginalia may omit it.
  - New runtime/audit/Unit Memory artifacts do not emit a fresh top-level `marginalia_audit[]`; legacy artifacts may still be read as a compatibility fallback.
  - Product-visible Marginalia remains only `source_quote` plus optional `content`; `selection_reason` is mechanism-private audit metadata and is not public API / frontend content.
- Implemented v16 quote-span follow-up:
  - `source_quote` selection now prefers the smallest complete contiguous local meaning span, not the shortest exact phrase.
  - Highlight-only Marginalia has three gates: complete local meaning, standalone readability, and intrinsic excerpt value.
  - Famous tail clauses, clipped predicates, and adjacent sentences / clauses that jointly form one coherent image, thought, contrast, or emotional movement should be expanded into one complete Marginalia item instead of split into fragments.
- Implemented v17 highlight-only context-loss follow-up:
  - Highlight-only Marginalia now has two hard gates: completeness and value.
  - Completeness means the quote remains understandable and its main meaning does not collapse when lifted out of the book without surrounding scene, speaker, character relation, plot function, or prior setup.
  - Value means the quote itself gives the reader a real cognitive, knowledge, aesthetic, emotional, ethical, or expressive gain.
  - `selection_reason` must name both why the quote remains understandable out of context and what value it carries.
  - Locally important but context-dependent character judgments, relationship turns, plot hinges, or referential lines should become note-bearing Marginalia or stay in Understanding rather than quote-only highlights.

## Design Goal

Revise the Digest prompt so Marginalia becomes a stronger user-visible reading surface:

- Marginalia should cover both highlight-only marks and note-bearing marks.
- Highlight-only means the source quote itself is excerpt-worthy, preserves a complete local meaning span, can stand alone without surrounding context or an added note, and has intrinsic value as an excerpt.
- Highlight-only selection should leave a short private reason for audit, so later review can tell why the quote was selected without exposing that reason to the reader.
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

The current Marginalia prompt candidate is preserved below for review.

#### Current Candidate: Marginalia Prompt Source Text

```markdown
# Marginalia

After reading and understanding the current source unit, decide whether any exact quote from this unit should be preserved in the margin.

Marginalia are source-anchored reading marks. They are not passage summaries, generic annotations, metadata labels, or a place to prove cleverness. A good Marginalia item helps the reader notice, remember, question, or return to something specific at the exact quoted words.

## Two Forms

Marginalia can be either highlight-only or note-bearing.

- Highlight-only: use this only when the exact quote passes both gates. First, the completeness gate: if lifted out of the book, the quote can still be understood and its main meaning does not collapse without the surrounding scene, speaker, character relation, plot function, or prior setup. Second, the intrinsic excerpt value gate: the quote itself gives the reader a real gain through insight, knowledge, conceptual compression, aesthetic force, emotional condensation, ethical pressure, memorable language, or a transferable way of seeing. Output an exact `source_quote`; leave `content` empty or omit it according to the output contract.
- Note-bearing: use this when the quote is valuable but its value would not be clear enough from the quote alone. A relationship, explanation, question, connection, contrast, structural role, or judgment must be written down for the value to survive. Output an exact `source_quote` plus concise reader-visible `content`.

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

Highlight-only has two hard gates: completeness and value. The quote must be a complete local meaning span whose main meaning survives outside the book, and it must give the reader a real cognitive, knowledge, aesthetic, emotional, ethical, or expressive gain. Self-contained is necessary but not sufficient. Do not mark a merely ordinary sentence just because it is complete, informative, or easy to locate.

A quote is not complete just because it is exact or famous. Avoid clipped clauses, isolated predicates, local terms, half-images, famous closing clauses, or explanation targets whose meaning depends on nearby words. If the candidate quote depends on an earlier subject, setup, contrast, image, or emotional build-up, expand it to include the smallest preceding span needed for the quote to stand as a complete local meaning. If two adjacent sentences jointly form one coherent image, thought, contrast, or emotional movement, quote them together as one contiguous Marginalia item instead of splitting them into separate fragments.

Structural importance is not the same as excerpt-worthiness. Topic sentences, transitions, setup questions, recaps, and argument signposts may be important for Understanding, but they should not become highlight-only Marginalia unless their exact wording is itself valuable outside the current context.

Context-loss test: if the quote matters mainly because of who says it, who is being described, where it appears in the plot, what relation it changes, or why it matters in this book's local situation, then it is context-dependent. Do not make it highlight-only unless the quoted words themselves still carry clear value without that context. Character judgments, relationship turns, plot hinges, and lines such as "this person...", "he...", or "she..." often belong in Understanding or note-bearing Marginalia rather than quote-only highlights.

## Minimal Intervention

Before producing each candidate Marginalia item, ask:

1. Should this source span be marked at all?
   If it is only a transition, filler, repeated information, or a detail with no return value, skip it.

2. Can this quote stand alone as an intrinsically valuable excerpt?
   If another reader saw only this complete quote, without the surrounding unit or an added note, would they still understand the main meaning? Would they naturally see the value in the original wording, image, insight, emotional force, conceptual compression, or transferable way of seeing? If both completeness and value are present, and a note would only repeat or dilute the quote, use highlight-only.

3. Is the quote valuable only after explanation?
   If the quote matters because of its role in the argument, scene, contrast, turn, hidden relation, or local mechanism, use note-bearing Marginalia. Do not hide context-dependent value inside a quote-only highlight.

4. Is it only structurally useful?
   If the span is mainly a topic sentence, transition, setup question, recap, or roadmap, put that function in Understanding or Response if needed; usually do not create Marginalia.

5. If writing a note, what would the reader miss without it?
   The answer must be specific: a mechanism, relation, tension, inference, uncertainty, callback, or question.

6. Can the note send the reader back to exact words in the quote?
   If the note cannot return to a word, syntax, image, structure, claim, or fact in the source quote, delete it or choose a better quote.

Choose the smallest complete contiguous `source_quote` that can honestly preserve the item's local meaning. "Smallest" means no unnecessary surrounding prose, not a fragmentary phrase. Prefer a complete sentence or a tightly connected pair of sentences when that is the minimal complete unit. Do not isolate a famous tail clause when its subject, setup, contrast, image, or emotional build-up is outside the quote. Do not use ellipses, stitched fragments, paraphrases, translations, source coordinates, or paragraph numbers as the quote.

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

Avoid empty praise. A note like "this passage is tense," "this sentence is beautiful," or "this character is vivid" is not enough. Explain what in the quote creates the effect. Use highlight-only only when the exact quote itself already carries the value.

## Output Discipline

This section explains only the `marginalia` field. The final Digest output must still follow the full OutputContract for `understanding`, `response`, and `marginalia`.

For each Marginalia item:

- `source_quote` must be an exact contiguous quote from the current source unit, and it should be the smallest complete span that preserves the item.
- Empty or omitted `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- For each highlight-only Marginalia item, include a short private `selection_reason` inside the same item. The reason must name both why the quote remains understandable out of context and what intrinsic excerpt value it carries.
- For note-bearing Marginalia, write the explanation in visible `content`; `selection_reason` may be omitted or empty.
- Do not output `mode`, `kind`, `decision`, `hook`, `intent`, `evidence_status`, `calibration`, `rejected_output`, `source`, `prior_link`, `outside_link`, or `search_intent` unless a later output contract explicitly asks for them.

## Calibration Examples

These examples show only the `marginalia` field shape.

Case 1: skip a structural transition
Text: "下面分别讨论这三个方面。"
Output:
{"marginalia": []}

Case 2: skip a structural signpost
Text: "这一章将从三个方面说明问题的来龙去脉。"
Why: this sentence may organize the reading, but it is not a standalone excerpt worth preserving.
Output:
{"marginalia": []}

Case 3: highlight-only standalone excerpt
Text: "旧钥匙打不开新门。"
Why: the quoted sentence is compact and self-contained; the reason for preserving it is visible in the sentence itself.
Output:
{"marginalia": [{"source_quote": "旧钥匙打不开新门。", "content": "", "selection_reason": "Understandable out of context as a complete metaphor; valuable through principle-like compression."}]}

Case 3B: reject locally important but context-dependent highlight-only
Text: "这个人是神圣的。悉达多从未如此敬重过一个人，从未如此爱慕过一个人。"
Why: this may be important inside the novel, but the value depends on knowing who "this person" is and what this relationship means. Do not use highlight-only.
Output:
{"marginalia": []}

Case 3C: reject clipped or under-complete highlight-only
Text: "在水面行走并不是我的追求。"
Why: the sentence may matter in context, but by itself it does not preserve enough of the thought or its value. Use note-bearing Marginalia only if the local contrast is worth explaining.
Output:
{"marginalia": []}

Case 4: note-bearing when the value depends on explanation
Text: "所有人都被叫成编号。"
Why: the quoted words are important, but the cognitive value comes from naming what the replacement of names with numbers does.
Output:
{"marginalia": [{"source_quote": "被叫成编号", "content": "Turning names into numbers changes people into administratively handled units; the violence here is in the replacement of personal identity by a sortable label."}]}

Case 5: note-bearing close reading
Text: "门开着，屋里却没有人敢进去。"
Why: the note explains how the sentence produces its local tension.
Output:
{"marginalia": [{"source_quote": "门开着，屋里却没有人敢进去", "content": "The open door suggests access, but the shared refusal to enter turns openness into prohibition; the tension comes from the gap between physical possibility and social fear."}]}

Case 6: note a reasoning hinge
Text: "由此可见，问题不在资源太少，而在资源被错误地锁住。"
Why: the quote marks the bridge from preceding evidence to a claim about where the real constraint lies.
Output:
{"marginalia": [{"source_quote": "问题不在资源太少，而在资源被错误地锁住", "content": "The sentence shifts the diagnosis from scarcity to blocked access; the important move is not that resources are limited, but that the system prevents available resources from circulating."}]}

Case 7: preserve uncertainty without inventing context
Text: "他又引用那句古话，说真正的路总要绕远。"
Why: the phrase appears to invoke classical language, but if verified context is not present in CurrentFocus or ReadingMemory, do not invent the allusion's source or function.
Output:
{"marginalia": [{"source_quote": "真正的路总要绕远", "content": "This is framed as an inherited saying, but the current material is not enough to verify its source or original context; keep the uncertainty visible rather than inventing a background."}]}
```

### 8. Instruction / SourceGrounding

Current role:

- Require exact contiguous `marginalia[].source_quote` from the current unit.
- Prohibit model-authored coordinates.
- Let runtime resolve source quotes to `SourceRef`.

Current working answer:

- Highlight-only and note-bearing Marginalia follow the same exact-quote rule.
- `source_quote` must be an exact contiguous span copied from the current source unit, with no ellipses, stitched fragments, paraphrase, translation, paragraph number, or coordinate-like token.
- Source quote length guidance should remain primarily in the Marginalia instruction block: choose the smallest complete contiguous quote that preserves the item's local meaning.
- Note-bearing `content` should be able to return the reader to a specific word, syntax, image, structure, claim, or fact in `source_quote`.
- Runtime remains responsible for resolving the quote into `SourceRef`; the model must not output source coordinates.

### 9. Instruction / ResponseDiscipline

Current role:

- Avoid broad chapter summaries.
- Avoid explaining whether prior material was used.
- Avoid route decisions.
- Submit final output through the required final-output channel.

Current working answer:

- ResponseDiscipline should forbid hidden calibration fields such as `decision`, `hook`, `intent`, `evidence_status`, `calibration`, `rejected_output`, and `source` in final output.
- The live output should distinguish user-visible text from implementation metadata by excluding implementation metadata from the model-facing Marginalia item.
- It should also forbid inherited optional metadata fields from the normal model-facing Marginalia item: `prior_link`, `outside_link`, and `search_intent`.
- It should remind the model that final Digest output still goes through the full `understanding` / `response` / `marginalia` contract; Marginalia examples are field-shape calibration only.

### 10. BookInfo

Current role:

- Stable book identity: title and author.
- Not source text.

Current working answer:

- BookInfo should remain orientation only.
- Do not infer author biography, historical intention, edition facts, or allusion sources from BookInfo alone.
- No large Marginalia-specific BookInfo prompt change is needed in this slice.

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

Current working answer:

- Marginalia prompt text should not mention paragraph boundaries or source coordinates.
- `source_quote` is unit-local from the model's point of view; current runtime resolves it inside the current source unit.
- CurrentFocus should remain the current source substrate and reading-position carrier, not a Marginalia-specific instruction surface.

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

Current working answer:

- No large Understanding rewrite is needed in this slice.
- Keep Understanding focused on compact source-established content for continued reading.
- Add at most one narrow boundary sentence if needed: quote-level close reading, margin questions, and local source-anchored reader notes belong in `marginalia`, not in `understanding`.
- Do not turn Understanding into a list of possible Marginalia.

### 15. OutputContract / ResponseField

Current role:

- Define `response` as immediate reader expression after the unit.
- Keep it distinct from Understanding and Marginalia.

Current working answer:

- No large Response rewrite is needed in this slice.
- Keep Response as whole-unit reader aftertaste, pressure, feeling, or question.
- Response may naturally resonate with a local trigger, but source-anchored local thoughts should be expressed in `marginalia`.
- Do not require Response to shrink mechanically when Marginalia is rich; rely on the existing distinctness rule.

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
- Allows each Marginalia item to include `source_quote`, optional `content`, and optional private `selection_reason`.

Current working answer:

- The live final-output tool schema should expose `source_quote`, optional `content`, and optional private `selection_reason` for each Marginalia item.
- `source_quote` should be required.
- `content` should be optional and nullable / empty-string tolerant.
- Highlight-only Marginalia should include non-empty inline `selection_reason`.
- `selection_reason` should be short, private, and specific to the quote's intrinsic excerpt value.
- Note-bearing Marginalia does not require inline `selection_reason`; its visible `content` is the selection reason.
- The schema should not expose `prior_link`, `outside_link`, or `search_intent` as normal live output fields.
- Backward-compatible normalizers may continue to read legacy metadata from older artifacts or malformed outputs, but those fields are not a current model-facing contract.
- Do not add `mode` / `kind` in this slice; highlight-only remains runtime-derived from empty, null, or omitted `content`.

### 18. Runtime Normalization And Settlement

Current role:

- Normalize `marginalia[]` into canonical Digest Marginalia.
- Verify `source_quote` appears in current unit text.
- Drop items with missing quote or missing content under the current implementation.
- Store Marginalia in runtime/audit and Unit Memory surfaces.
- Preserve legacy annotation/reaction aliases for compatibility.

Current working answer:

- Runtime normalization should accept Marginalia items with exact `source_quote` and empty, null, or omitted `content`.
- Missing or unresolved `source_quote` remains invalid / dropped according to existing source-grounding rules.
- Highlight-only items should be stored as canonical Marginalia records with empty note content, so they can travel through the same mark / Marginalia surface as note-bearing items.
- Highlight-only private audit reasons should be stored in mechanism-private runtime / audit / Unit Memory metadata, but they should not become public Marginalia content or retrieval text.
- Runtime/frontend can derive highlight-only vs note-bearing from normalized `content`.
- Legacy annotation/reaction aliases should preserve highlight-only semantics where compatibility surfaces need them, but new runtime/audit rows should use canonical Marginalia vocabulary.
- Legacy `prior_link`, `outside_link`, and `search_intent` may remain compatibility-read fields; they should not be required or emitted for new live Marginalia.

## Open Output-Contract Direction

Current working decision for the next reviewed Digest Marginalia contract:

```json
{
  "source_quote": "...",
  "content": "",
  "selection_reason": "..."
}
```

Interpretation:

- `source_quote` is required.
- Empty, `null`, or omitted `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- Highlight-only requires inline `selection_reason` naming both out-of-context completeness and excerpt value; note-bearing may omit it.
- No explicit `mode` / `kind` / `decision` field is needed in this slice.
- `prior_link`, `outside_link`, and `search_intent` should not be part of the normal model-facing Marginalia item. They may remain backward-compatible backend fields for older reaction / annotation / Marginalia artifacts, but should not appear in the live prompt ReturnFormat, final-output tool schema, or few-shot examples.
- Future source-backlink, external-reference, or research-intent behavior should be redesigned as an explicit product/runtime feature rather than hidden inside ordinary Marginalia item metadata.

## Accepted Implementation Slice

This design is implemented by the Digest v11-v17 slices. The implementation updated these surfaces together:

- Digest prompt version / XML spec / promptset / output-contract id.
- `Instruction / Marginalia` with the current candidate prompt text.
- v16 quote-span guidance so Marginalia uses the smallest complete local meaning span rather than clipped phrases, isolated terms, or partial images.
- v17 highlight-only context-loss guidance so quote-only highlights must remain understandable out of context and carry visible excerpt value.
- `Instruction / SourceGrounding` to align exact-quote wording with highlight-only and note-bearing Marginalia.
- `Instruction / ResponseDiscipline` to forbid calibration fields and inherited metadata fields in final output.
- `OutputContract / ReturnFormat` and `OutputFields / MarginaliaField` to show visible `source_quote` plus optional `content`, plus inline private highlight-only `selection_reason` audit metadata.
- Final-output tool schema so `marginalia[].content` is not required.
- Digest output validator and normalizer so highlight-only items are accepted when `source_quote` resolves and `content` is empty / null / omitted, and so each highlight-only item carries one private inline audit reason.
- Runtime/audit/unit-memory persistence so new records use canonical `marginalia` vocabulary, preserve highlight-only vs note-bearing semantics, and keep private audit reasons out of reader-visible Marginalia content.

Non-goals for this slice:

- Do not redesign `ReadingMemory`, Unit Memory retrieval, Ingest, or Digest `understanding` semantics.
- Do not reintroduce `prior_link`, `outside_link`, or `search_intent` into the live Marginalia output contract.
- Do not add explicit `mode`, `kind`, or `decision` fields.
- Do not expose `selection_reason` as a frontend/public API field in this slice.
- Do not modify frontend presentation beyond whatever minimal compatibility is required to carry highlight-only Marginalia through existing mark surfaces.

## Review Order

Suggested review sequence:

1. Decide the Marginalia concept: highlight-only plus note-bearing marks.
2. Decide the minimal output contract for one Marginalia item.
3. Rewrite the Marginalia instruction block around that contract.
4. Convert few-shot examples so they output only fields allowed by the contract.
5. Adjust SourceGrounding and ResponseDiscipline to enforce exact quote and no extra calibration fields.
6. Decide whether Understanding and Response need narrow edits or should stay unchanged.
7. Implement prompt/schema/runtime changes in a later code slice after this design is reviewed.
