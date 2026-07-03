# Digest Marginalia Prompt Revision Design

Purpose: provide a review workspace for revising the Digest prompt, especially the Marginalia selection and output contract.
Use when: discussing or drafting changes to live Digest prompt structure, Marginalia quality policy, highlight/note behavior, or Marginalia output fields.
Not for: current live runtime authority, historical eval artifacts, or formal evidence promotion.
Update when: a reviewed Marginalia prompt draft changes, the candidate output contract changes, or a Digest prompt section is accepted for implementation.

Created: `2026-06-20`

## Status

- Status: implemented-live in Digest v24.
- Live prompt now implements the reviewed candidate in `reading-companion-backend/src/attentional_v2/prompts/digest.py`.
- Current live Digest baseline:
  - prompt version: `attentional_v2.digest.v24`
  - XML spec: `attentional_v2.digest.xml.v24`
  - promptset: `attentional_v2-phase6-v84`
  - output contract: `digest_understanding_response_marginalia_json_v8`
- Current live model-facing outputs:
  - `understanding`
  - `response`
  - `marginalia[]`
- Implemented output-contract direction:
  - The model-facing Marginalia item contains required `kind`, required `source_quote`, optional `content`, and optional private `selection_reason`.
  - `kind` is required and must be `"highlight"` or `"note"` for new live output.
  - `source_quote` is required.
  - `kind: "highlight"` preserves exact source text worth carrying forward by itself; it requires non-empty private `selection_reason` and keeps `content` empty or omitted.
  - `kind: "note"` attaches reader-facing cognitive surplus to a precise source anchor; it requires non-empty visible `content` and may omit `selection_reason`.
  - Highlights and Notes are independent reader actions; their source quotes may overlap and are not deduped by quote.
  - Do not add `mode`, `decision`, `prior_link`, `outside_link`, `search_intent`, or other inherited optional metadata to the normal model-facing Marginalia item unless a later product/runtime design explicitly reintroduces it.
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
  - `selection_reason` must name both why the quote remains understandable out of context and what intrinsic excerpt value it carries.
  - Locally important but context-dependent character judgments, relationship turns, plot hinges, or referential lines should become note-bearing Marginalia or stay in Understanding rather than quote-only highlights.
- Implemented v18 note-bearing cognitive-increment follow-up:
  - Note-bearing Marginalia now asks directly what a thoughtful ordinary reader may not notice, know, or infer on their own.
  - Note content must add cognitive value beyond paraphrase, such as hidden structure, literary technique, motif, cultural/historical context, translation nuance, philosophical tension, precise inference, or a question that changes how the quote is read.
  - The prior `verb + object` intention method is removed from the live prompt; the prompt now forbids classroom paraphrase and shallow restatement of visible actions or obvious emotions.
  - Future-spoiler and evidence boundaries remain: use the current unit, ReadingMemory, and high-confidence common literary/cultural knowledge; uncertain future connections should stay questions or be skipped.
- Implemented v19 Marginalia value-calibration follow-up:
  - Highlight-only now emphasizes durable long-term reader value, not only local importance inside the current book. Local facts, plot evidence, scene details, shocking narrative evidence, topic sentences, and ordinary informative sentences should usually be skipped unless their exact wording becomes a durable excerpt outside the current context.
  - Note-bearing now prioritizes useful knowledge, context, or non-obvious connections that a thoughtful ordinary reader may not know, notice, or infer on their own.
  - Ordinary close-reading / technique commentary is explicitly demoted: technique notes are allowed only when they reveal something non-obvious and materially change the quote's value.
  - The Resistance / Leverage / Growth ideas remain as silent checks, not as a generation menu.
- Implemented v20 density-aware follow-up:
  - Dense units should preserve all genuinely durable thought nodes rather than treating Marginalia as a top-1 or top-2 selection task.
  - Adjacent valuable spans should be emitted separately only when they are distinct portable ideas; neighboring sentences that jointly form one definition, argument step, contrast, analogy, or mini-theory should be quoted together as one Marginalia item.
  - `source_quote` selection now clarifies that "smallest complete" means the shortest contiguous span that preserves the full reusable idea, not the shortest possible sentence.
  - Output contract remains `digest_understanding_response_marginalia_json_v7`; this is a prompt-selection discipline change, not a schema or runtime contract change.
- Implemented v21-v22 Highlight gate follow-up:
  - Highlights must pass durable-value, out-of-context-completeness, and excerpt-necessity gates.
  - Strong facts, suffering, historical importance, emotional force, and moral shock are not enough by themselves unless the quote itself crystallizes a reusable insight, distinction, mechanism, warning, model, or self-correction.
  - Private `selection_reason` must name the specific portable gain and fail if it could fit many similar passages by merely swapping names or situations.
- Implemented v23 parallel-actions follow-up:
  - Marginalia now include explicit parallel `Highlights` and `Notes` rather than a single content-empty/content-bearing choice.
  - New live output requires `marginalia[].kind`.
  - Highlights and Notes are judged in separate passes; overlapping anchors are allowed.
  - Output contract is now `digest_understanding_response_marginalia_json_v8`.
- Implemented v24 intrinsic quote-value follow-up:
  - Highlights now use an intrinsic quote-value gate: the quoted words themselves must already carry the portable cognitive gain.
  - Private `selection_reason` may identify value already visible in the quote, but must not supply missing value by translating a local fact, scene, example, testimony, emotional shock, or book-specific event into a general lesson after the fact.
  - The quote-itself test asks whether a thoughtful reader would still see why the quote is worth preserving without `selection_reason`, `content`, surrounding context, or an explanation from the model.
  - Notes remain an independent pass; failing the Highlight gate does not automatically make a passage a Note candidate.

## Design Goal

Revise the Digest prompt so Marginalia becomes a stronger user-visible reading surface:

- Marginalia should cover both Highlights and Notes as independent reader actions.
- Highlights mean the source quote itself is excerpt-worthy, preserves a complete local meaning span, can stand alone without surrounding context or an added note, and already carries durable portable cognitive value in the quoted words.
- Highlight selection should leave a short private reason for audit, so later review can tell why the quote was selected without exposing that reason to the reader.
- Notes mean the quote is a precise anchor for a reader-visible thought, explanation, question, connection, or judgment that adds cognitive surplus.
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

After reading and understanding the current source unit, decide whether any exact quote from this unit deserves to become a page-margin reader mark.

Marginalia are not summaries, reading-comprehension explanations, or marks for everything important in the book. A good Marginalia item preserves something the reader may want to carry forward beyond this moment of reading.

Do not create Marginalia just to fill the field. It is normal to emit zero items.

## Two Forms

Marginalia can be highlight-only or note-bearing.

### Highlight-only

Use highlight-only only when the quote itself is worth preserving without added explanation.

A highlight-only quote must pass both gates:

1. Out-of-context completeness:
   If lifted out of the book, the quote can still be understood. Its main meaning must not collapse without knowing the plot situation, speaker identity, character relation, prior setup, local argument, or why this moment matters in this book.

2. Durable excerpt value:
   The quote gives the reader a lasting gain by itself: insight, conceptual compression, practical wisdom, aesthetic force, emotional condensation, ethical pressure, memorable language, or a transferable way of seeing.

Do not use highlight-only merely because a sentence is important for understanding this book. A sentence may be crucial as evidence, plot movement, or local explanation while still having little long-term value as a standalone excerpt.

Avoid highlight-only for:
- local facts, plot evidence, scene details, or examples whose value depends on the current narrative;
- topic sentences, transitions, setup questions, recaps, and argument roadmaps;
- shocking or emotional details that matter mainly as evidence inside this book;
- sentences whose value depends mainly on who says them, who is being described, or what happens nearby;
- ordinary informative sentences, even when they are clear and complete.

If two adjacent sentences jointly form one complete thought, image, contrast, or emotional movement, quote them together as one contiguous Marginalia item. Do not split a complete excerpt into clipped fragments.

For highlight-only, output `source_quote`, leave `content` empty or omit it, and include a short private `selection_reason` naming both why the quote remains understandable out of context and what durable excerpt value it carries.

### Note-bearing

Use note-bearing Marginalia when the quote becomes more valuable because there is something useful to tell the reader around it.

A good note should answer this question:

"What is something valuable here that a thoughtful ordinary reader may not know, may not notice, or may not be able to infer on their own?"

Prefer notes that add real cognitive value, such as:
- cultural, historical, religious, philosophical, economic, or institutional background;
- the source, function, or implication of an allusion, term, concept, example, or comparison;
- a high-confidence connection to another work, idea, tradition, or real-world mechanism;
- a non-obvious inference that changes how the quote should be read;
- a precise tension, ambiguity, or question that prevents a too-simple reading;
- a prior ReadingMemory callback when it genuinely changes the current quote's meaning.

Use literary technique, close reading, or formal analysis only when it reveals something a reader probably would not notice and materially changes the value of the quote. Do not write a note merely to say that the passage "forms a contrast", "creates tension", "emphasizes", "shows emotion", "foreshadows", or "reveals character" unless the note gives a non-obvious gain.

Do not write a note if it only:
- paraphrases the quote;
- explains a plainly visible action;
- repeats what Understanding already says;
- names an obvious emotion, theme, contrast, or technique;
- gives a generic classroom-style interpretation;
- praises the passage without adding evidence.

For note-bearing Marginalia, output an exact `source_quote` plus visible `content`. The note should be compact but substantial. It should give the reader something they did not already get just by rereading the quote.

## Silent Lenses

Use these only as private checks, not as output labels or a generation menu.

- Resistance: Is there a term, allusion, ambiguity, compressed idea, factual uncertainty, or translation issue that blocks easy understanding?
- Leverage: Does the quote change how the reader should understand the local argument, scene, relationship, or earlier material?
- Growth: Does the quote open a valuable connection to background knowledge, another text, a broader concept, a real-world mechanism, or a useful question?

One real trigger may justify Marginalia, but a vague sense that something is "important" is not enough.

## Source Quote Span

Choose the smallest complete contiguous `source_quote` that can honestly carry the Marginalia item.

"Smallest" means no unnecessary surrounding prose, but it must not be fragmentary. Prefer a complete sentence, or a tightly connected pair of sentences, when that is the minimal complete unit.

Do not use ellipses, stitched fragments, paraphrases, translations, paragraph numbers, or source coordinates.

## Evidence And Honesty

Use the current unit, ReadingMemory, and high-confidence common knowledge.

You may use well-known cultural, historical, philosophical, literary, or practical background when it is reliable and useful. If a fact, source, edition issue, biography claim, or allusion is uncertain, mark the uncertainty or skip the note.

Do not spoil future unread content. If a future connection is only a hunch, keep it as a question or leave it unwritten.

Do not fabricate hidden background, authorial intent, future plot, or a "real story" behind the text.

It is better to output no Marginalia than to produce a weak highlight or an obvious note.

## Output Discipline

This section explains only the `marginalia` field. The final Digest output must still follow the full OutputContract for `understanding`, `response`, and `marginalia`.

For each Marginalia item:

- `source_quote` must be an exact contiguous quote from the current source unit, and it should be the smallest complete span that preserves the item.
- Empty or omitted `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- For each highlight-only Marginalia item, include a short private `selection_reason` inside the same item. The reason must name both why the quote remains understandable out of context and what durable excerpt value it carries.
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
Why: the quoted sentence is compact, self-contained, and has durable excerpt value as a transferable metaphor.
Output:
{"marginalia": [{"source_quote": "旧钥匙打不开新门。", "content": "", "selection_reason": "Understandable out of context as a complete metaphor; durable value through principle-like compression."}]}

Case 3B: reject locally important but context-dependent highlight-only
Text: "这个人是神圣的。她从未如此敬重过一个人。"
Why: this may be important inside the story, but the value depends on knowing who "this person" is and what the relationship means. Do not use highlight-only.
Output:
{"marginalia": []}

Case 3C: reject local evidence without durable excerpt value
Text: "那天晚上，城门口多了七具尸体。"
Why: the detail may be shocking and important evidence inside the narrative, but by itself it does not offer durable reader value outside that narrative context.
Output:
{"marginalia": []}

Case 4: note-bearing with useful external background
Text: "就像那个买下梵高画作的日本人一样。"
Why: the quote's value depends on background many readers may not know.
Output:
{"marginalia": [{"source_quote": "就像那个买下梵高画作的日本人一样。", "content": "This points to the late-1980s Japanese asset bubble, when Japanese buyers paid startling prices for Western trophy art, including Yasuda Fire and Marine's roughly US$40 million purchase of Van Gogh's Sunflowers. The comparison sharpens the criticism: the bidder is spending other people's money with bubble-era abandon."}]}

Case 5: reject shallow note-bearing close reading
Text: "门开着，屋里却没有人敢进去。"
Bad note: "The open door and nobody entering form a contrast that creates tension."
Why bad: it only names an obvious contrast and offers a classroom-style technique comment. If there is no non-obvious gain, skip it.
Output:
{"marginalia": []}

Case 6: note a reasoning hinge only when it changes the reader's model
Text: "由此可见，问题不在资源太少，而在资源被错误地锁住。"
Why: the note gives a reusable conceptual distinction rather than merely saying the sentence is important.
Output:
{"marginalia": [{"source_quote": "由此可见，问题不在资源太少，而在资源被错误地锁住。", "content": "The sentence changes the diagnosis from scarcity to access. That distinction matters beyond this passage: a system can have enough resources in total and still fail because rules, ownership, or bottlenecks prevent those resources from circulating."}]}

Case 7: preserve uncertainty without inventing context
Text: "他又引用那句古话，说真正的路总要绕远。"
Why: the phrase appears to invoke inherited language, but if verified context is not present in CurrentFocus or ReadingMemory, do not invent the allusion's source or function.
Output:
{"marginalia": [{"source_quote": "真正的路总要绕远", "content": "This is framed as an inherited saying, but the current material is not enough to verify its source or original context; keep the uncertainty visible rather than inventing a background."}]}

Case 8: reject shallow note-bearing paraphrase
Text: "愿你将这条路走到底，愿你寻得解脱！"
Bad note: "The repeated blessing shows that Siddhartha recognizes Govinda's independent choice and hints that he will not go with him."
Why bad: it mostly restates the visible scene and gives little beyond what a reader can infer by rereading the sentence.
Better output:
{"marginalia": []}
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
- Allows each Marginalia item to include required `kind`, required `source_quote`, optional `content`, and optional private `selection_reason`.

Current working answer:

- The live final-output tool schema should expose `kind`, `source_quote`, optional `content`, and optional private `selection_reason` for each Marginalia item.
- `kind` should be required and must be `"highlight"` or `"note"` for new live output.
- `source_quote` should be required.
- `kind: "highlight"` should include non-empty inline `selection_reason`; `content` should be empty or omitted.
- `selection_reason` should be short, private, and specific to durable value already visible in the quote itself.
- `kind: "note"` should require non-empty visible `content` and does not require inline `selection_reason`; its visible `content` is the reader-facing note.
- The schema should not expose `prior_link`, `outside_link`, or `search_intent` as normal live output fields.
- Backward-compatible normalizers may continue to read legacy metadata from older artifacts or malformed outputs, but those fields are not a current model-facing contract.
- Do not add `mode` / `decision` in this slice.

### 18. Runtime Normalization And Settlement

Current role:

- Normalize `marginalia[]` into canonical Digest Marginalia.
- Verify `source_quote` appears in current unit text.
- Drop items with missing quote or missing content under the current implementation.
- Store Marginalia in runtime/audit and Unit Memory surfaces.
- Preserve legacy annotation/reaction aliases for compatibility.

Current working answer:

- Runtime normalization should accept new live Marginalia items with required `kind`, exact `source_quote`, and kind-appropriate `content` / `selection_reason`.
- Missing or unresolved `source_quote` remains invalid / dropped according to existing source-grounding rules.
- Highlight items should be stored as canonical Marginalia records with empty note content, so they can travel through the same mark / Marginalia surface as Notes.
- Highlight private audit reasons should be stored in mechanism-private runtime / audit / Unit Memory metadata, but they should not become public Marginalia content or retrieval text.
- Runtime/frontend should use canonical normalized `kind` for new artifacts while preserving legacy content-derived inference for old artifacts.
- Legacy annotation/reaction aliases should preserve highlight-only semantics where compatibility surfaces need them, but new runtime/audit rows should use canonical Marginalia vocabulary.
- Legacy `prior_link`, `outside_link`, and `search_intent` may remain compatibility-read fields; they should not be required or emitted for new live Marginalia.

## Current Live Output-Contract Direction

Current live Digest Marginalia contract:

```json
{
  "kind": "highlight",
  "source_quote": "...",
  "content": "",
  "selection_reason": "..."
}
```

Interpretation:

- `kind` is required and must be `"highlight"` or `"note"` for new live outputs.
- `source_quote` is required.
- For `kind: "highlight"`, `selection_reason` is required, `content` is empty or omitted, and the quote must pass intrinsic quote-value, quote-itself, out-of-context-completeness, excerpt-necessity, and selection-reason-audit gates.
- For `kind: "note"`, `content` is required and visible, while `selection_reason` may be omitted or empty.
- No explicit `mode` / `decision` field is needed in this slice.
- `prior_link`, `outside_link`, and `search_intent` should not be part of the normal model-facing Marginalia item. They may remain backward-compatible backend fields for older reaction / annotation / Marginalia artifacts, but should not appear in the live prompt ReturnFormat, final-output tool schema, or few-shot examples.
- Future source-backlink, external-reference, or research-intent behavior should be redesigned as an explicit product/runtime feature rather than hidden inside ordinary Marginalia item metadata.

## Accepted Implementation Slice

This design is implemented by the Digest v11-v24 slices. The implementation updated these surfaces together:

- Digest prompt version / XML spec / promptset / output-contract id.
- `Instruction / Marginalia` with the current candidate prompt text.
- v16 quote-span guidance so Marginalia uses the smallest complete local meaning span rather than clipped phrases, isolated terms, or partial images.
- v17 highlight-only context-loss guidance so quote-only highlights must remain understandable out of context and carry visible excerpt value.
- v18 note-bearing guidance so note content asks directly for what a thoughtful ordinary reader may not notice, know, or infer on their own.
- v19 quality calibration so highlight-only targets durable long-term reader value and note-bearing demotes ordinary close-reading / technique commentary unless it produces non-obvious gain.
- v20 density guidance so high-value units can produce multiple Highlights / Notes and adjacent sentences are quoted together when they form one complete reusable idea.
- v21-v22 Highlight gates so strong facts, moral shock, and local evidence are not enough unless the quote itself crystallizes reusable cognitive value.
- v23 explicit `kind` so Highlights and Notes are parallel reader actions rather than a content-derived choice.
- v24 intrinsic quote-value guidance so private `selection_reason` identifies value already present in the quote rather than rescuing weak local evidence through post-hoc abstraction.
- `Instruction / SourceGrounding` to align exact-quote wording with highlight-only and note-bearing Marginalia.
- `Instruction / ResponseDiscipline` to forbid calibration fields and inherited metadata fields in final output.
- `OutputContract / ReturnFormat` and `OutputFields / MarginaliaField` to show visible `kind`, `source_quote`, optional `content`, plus inline private Highlight `selection_reason` audit metadata.
- Final-output tool schema so `marginalia[].kind` is required for new live output, Highlight items require `selection_reason`, and Note items require visible `content`.
- Digest output validator and normalizer so new items are validated by `kind`, legacy items without `kind` remain accepted through compatibility inference, and old top-level `marginalia_audit[]` can still provide fallback reasons for historical payloads.
- Runtime/audit/unit-memory persistence so new records use canonical `marginalia` vocabulary, preserve explicit Highlight vs Note semantics, and keep private audit reasons out of reader-visible Marginalia content.

Non-goals for this slice:

- Do not redesign `ReadingMemory`, Unit Memory retrieval, Ingest, or Digest `understanding` semantics.
- Do not reintroduce `prior_link`, `outside_link`, or `search_intent` into the live Marginalia output contract.
- Do not add explicit `mode` or `decision` fields.
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
