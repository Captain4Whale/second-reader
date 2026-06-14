# Ingest Context And Navigate Mapping

Purpose: capture the first design mapping from the old forward-only `Navigate` prompt to the first implemented `Ingest` LLM call.
Use when: checking the landed first-slice Ingest XML context or understanding how the old boundary-selection prompt was mapped into `Ingest`.
Not for: stable mechanism authority, broad runtime behavior, or evidence-catalog claims.
Update when: the Ingest role, XML context shape, retrieval-request contract, or mapping from old Navigate fields changes.

## Status

- Date: `2026-05-31`
- Status: implemented first-slice reference.
- Code status: implemented after `DEC-107`.
- Evaluation status: no eval run, no evidence-catalog update.
- Supersession note:
  - This document is the first-slice boundary-selection mapping.
  - Its memory-retrieval placeholders and "deferred until the memory design lands" language are historical for that slice.
  - The current retrieval/context authority is `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`, where `Ingest` expresses bounded recall intent through `retrieve_unit_memory` action-tool args and Reading Runner renders Digest `ReadingMemory`.
- Current basis:
  - `DEC-103` pauses the old Second Reader Memory / Planning implementation track as the default direction.
  - `DEC-104` retires live Detour / source-backread.
  - `DEC-105` hard-purges retired Detour / backread / source-skill interfaces.
  - `DEC-106` separates the LLM call from runtime preparation / boundary governance.
  - `DEC-107` lands `llm_calls.ingest(...)` as the current LLM call, using this XML context shape.
  - `DEC-108` renames the concrete per-unit interpretation call to `llm_calls.digest(...)`, so this document's `Ingest -> Digest` vocabulary is current.

## Design Claim

The current `Navigate` prompt already performs the useful first half of `Ingest`: selecting the next forward semantic reading unit from the current source frontier. That boundary-selection policy should be reused rather than redesigned.

The main change is not the boundary-selection content. The change is the node identity and context structure:

- old name: `Navigate`
- new name: `Ingest`
- old role: choose the next readable unit
- new role: choose the next readable unit; in the current follow-through slice, also express bounded prior-reading recall intentions through `retrieve_unit_memory.memory_recalls[]`
- old structure: flat prompt sections with JSON blocks
- new structure: XML prompt assembly aligned with the current Digest prompt framework
- old context block: `navigation_context`
- new split:
  - no direct carried reading-state block in the first Ingest slice
  - `RetrievalSurface` retained as an intentionally empty placeholder until the new memory design lands

## Target Ingest Definition

`Ingest` is the reading-before-reading LLM call.

It receives the current reading frontier and a bounded forward source preview. Eventually it will also use a retrieval surface to request memory support for `Digest`, but the first context-shape slice leaves that surface empty until the new memory design lands.

`Ingest` does not:

- interpret the selected unit for the reader
- produce reader-facing notes, highlights, or surfaced reactions
- update memory
- choose a backward path or source detour
- run external web search
- own runtime anchor resolution, retry, fallback, retrieval execution, settlement, or cursor advancement

## Target XML Context Shape

The target Ingest prompt should follow the XML assembly discipline used by the current Digest prompt, but its top-level blocks should be semantically direct. `ReaderRole` and `Instruction` are both top-level prompt blocks; do not wrap them in a `RoleAndInstruction` container.

Top-level rule:

- `ReaderRole` owns the stable reader identity.
- `Instruction` owns all fixed non-role directions for this LLM call.
- Runtime context/data blocks stay outside `Instruction`: `BookInfo`, `CurrentView`, `RetrievalSurface`, and `OutputContract`.

```xml
<ReaderRole>...</ReaderRole>

<Instruction>
	  <CurrentStep>...</CurrentStep>
	  <ContextUseGuide>...</ContextUseGuide>
	  <SelectNextUnit>...</SelectNextUnit>
	  <RecallPriorReading>...</RecallPriorReading>
	  <ExecutionLimits>...</ExecutionLimits>
</Instruction>

<BookInfo>
  <BookIdentity>{...}</BookIdentity>
</BookInfo>

<CurrentView>
  <Position>{...}</Position>
  <Content>
    <Paragraph n="..." role="..." start_char="..." end_char="...">...</Paragraph>
  </Content>
</CurrentView>

<RetrievalSurface />

<OutputContract>
  <OutputFields>...</OutputFields>
  <ReturnFormat>...</ReturnFormat>
</OutputContract>
```

### ReaderRole

`ReaderRole` should contain the fixed product-level reader identity, not runtime state.

Rules:

- must reference the same prompt fragment used by the current Digest XML prompt: `reader.role`
- owned by `reading-companion-backend/src/attentional_v2/prompts/reader_role.py`
- implementation should import `READER_ROLE_FRAGMENT` or include `READER_ROLE_FRAGMENT_REGISTRY` when building the Ingest prompt fragment registry
- the Ingest prompt must not duplicate or locally redefine the role text
- current reader role text is: `你是一个知识渊博、有深刻洞见的阅读爱好者。当前你正在深入阅读一本书，在理解这本书内容的同时，积极对其进行思考，沉淀有价值的理解，并产生有价值的输出，从而获得最大的求知乐趣与自我提升。你的阅读可能分为多个步骤，具体每一步的活动请参考具体指令。`

### Instruction

`Instruction` is a top-level prompt block. It may be internally nested, but it should not sit under a `RoleAndInstruction` wrapper.

Recommended child blocks:

- `CurrentStep`
- `ContextUseGuide`
- `SelectNextUnit`
- `RecallPriorReading`
- `ExecutionLimits`

The child blocks should correspond to distinct model responsibilities, not to every policy paragraph. This keeps `Instruction` readable while avoiding duplicated task/policy pairs.

Merge rule:

- `CurrentStep` absorbs the old `StepPosition` and `TaskOverview`.
- `SelectNextUnit` absorbs the old `NextUnitSelection` and `BoundarySelection`.
- `RecallPriorReading` is the current follow-through memory-support task: it asks what prior reading the selected unit naturally calls back to, without showing retrieved memory to Ingest.
- `ExecutionLimits` absorbs the old `ResponsibilityBoundary` and `ResponseDiscipline`.

Target assembly shape:

```xml
<ReaderRole prompt_fragment_ref="reader.role" />

<Instruction>
	  <CurrentStep prompt_fragment_ref="ingest.current_step" />
	  <ContextUseGuide prompt_fragment_ref="ingest.context_use_guide" />
	  <SelectNextUnit prompt_fragment_ref="ingest.select_next_unit" />
	  <RecallPriorReading prompt_fragment_ref="ingest.recall_prior_reading" />
	  <ExecutionLimits prompt_fragment_ref="ingest.execution_limits" />
</Instruction>
```

The `prompt_fragment_ref` attributes above are implementation-facing references in the assembly spec. The rendered model-facing XML should contain only resolved text, following the current Digest XML assembly convention.

Recommended `Instruction` child meanings:

#### CurrentStep

`CurrentStep` says the model is in the `Ingest` step of a sequential deep-reading loop. This step happens before `Digest`: the model is previewing the next forward source area, not yet producing the final reading of that unit.

First-slice target output:

- selected next source unit boundary

Current follow-through output, specified in `ingest-recall-and-digest-memory-context-design.md`:

- zero to three prior-reading `retrieve_unit_memory.memory_recalls[]` for that selected unit
- a required `retrieve_unit_memory` tool call when non-empty recalls are needed

Proposed `ingest.current_step` fragment:

```text
You are in the Ingest step of a sequential deep-reading loop.

This step happens before Digest. You are not yet reading the selected unit for interpretation or reader-facing output. You are previewing the bounded forward source area from the current reading cursor in order to prepare Digest.

Your work in this call is to select the next forward source unit that you should read carefully in the Digest step.

First-slice note: memory-retrieval support was deferred in this mapping document. The current live prompt adds a `RecallPriorReading` instruction and uses `retrieve_unit_memory` action-tool args for bounded recall intent.
```

#### ContextUseGuide

`ContextUseGuide` tells the model how to use `BookInfo`, `CurrentView`, `RetrievalSurface`, and `OutputContract`.

It should emphasize:

- the visible source preview is primary
- book identity is orientation, not source text
- `RetrievalSurface` is intentionally empty in the current design slice

#### SelectNextUnit

`SelectNextUnit` says Ingest must select one forward source unit from the current frontier. The unit starts at the current source cursor and ends at an exact visible anchor.

This is where the already-approved "determine next unit" task and prompt rules are placed together. It contains the mature next-unit boundary policy reused from current Navigate.

Proposed `ingest.select_next_unit` fragment:

```text
Select one forward source unit from the current reading cursor.

Priority order:
- Judge from the visible source text first.
- Respect author structure before local convenience.

Source range:
- Choose directly from `CurrentView / Content`.
- Do not cross the provided `CurrentView / Content` boundary.
- The unit always starts at the current source cursor in `CurrentView / Position`. Do not invent a start id.

Unit size:
- Choose the smallest complete local move that can honestly be read as one unit.
- Prefer ending within the current paragraph.
- Continue into the next paragraph only when the same local move is clearly continuing.
- Do not pretend a move is finished when it is still unfolding; choose the best honest boundary available.

Structural cues:
- Treat `chapter_heading` and `section_heading` as weak structure cues, not automatic standalone units.
- A heading may stand alone only when its visible wording already forms a complete, meaningful local move.
- If a heading reads more like a label, lead-in, or structural setup, merge it with the immediately following body paragraph when `CurrentView / Content` allows.
- Stay proportionate around thin structural text. Do not carve out a very short unit just because the text is marked as a heading.
- Before finalizing the unit boundary, trim only boundary sentences that are purely non-lexical residue, such as ornament/divider/separator lines.
- `text_role` may help orient you, but it must not decide the boundary by itself.

End anchor and continuation:
- Set `end_anchor_text` to an exact quote from the visible preview at the end of the unit you choose.
- Copy `end_anchor_text` character-for-character from the preview source text. Do not paraphrase, omit punctuation, or add ellipses.
- Choose a sufficiently unique tail anchor, usually 20-80 Chinese characters or 8-25 English words. If the unit is very short, the full unit tail is acceptable.
- If the move is still unfinished at the available boundary, choose the best honest end point you have. Do not pretend the local move is complete.

Boundary closure check:
- After choosing the semantic end of the unit, check whether `end_anchor_text` accidentally leaves behind punctuation that belongs to the same sentence, quotation, parenthetical, bracketed span, or footnote marker.
- Include terminal punctuation and attached closing marks that complete the chosen unit, such as `。`, `.`, `！`, `？`, `”`, `’`, `）`, `]`, and `】`.
- Do not stop immediately before punctuation or a closing mark that closes the sentence, quote, parenthesis, bracket, or note span you are choosing.
- Do not absorb opening punctuation, bullets, separators, or markers that begin the next unit.
```

#### RecallPriorReading

`RecallPriorReading` tells Ingest how to notice the prior reading that the selected source unit naturally asks to remember before Digest reads it carefully.

Current status: implemented in the follow-through recall/context slice.

The detailed recall/tool policy lives in `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`: Ingest may call `retrieve_unit_memory` with zero to three `memory_recalls[]` args when prior memory is needed, and receives only status/count tool results while runtime owns retrieval selection and Digest `ReadingMemory` rendering.

#### ExecutionLimits

`ExecutionLimits` says what Ingest must not do.

It should state:

- do not interpret the selected unit for the reader
- do not write notes, highlights, surfaced reactions, or memory updates
- do not execute retrieval, resolve anchors, retry/fallback, settle runtime state, or advance the cursor
- do not request external search
- return JSON only and follow `OutputContract`

Proposed `ingest.execution_limits` fragment:

```text
Stay inside the Ingest boundary.

Do not read or interpret the selected unit as the final reading. Do not write reading impressions, notes, highlights, surfaced reactions, summaries, or memory updates.

Do not perform runtime work. Do not resolve anchors, retry or choose fallback boundaries, advance the cursor, settle state, or execute memory retrieval.

Do not use external web search or request tools. Memory retrieval request behavior is deferred until the memory design lands.

Return only the JSON described by OutputContract. Do not include markdown, commentary, hidden reasoning, or fields that are not requested.
```

### BookInfo

Maps from the old `structural_frame`.

#### BookIdentity

Target fields:

```json
{
  "book_title": "...",
  "author": "..."
}
```

`BookInfo` should match the Digest XML pattern: it identifies the stable book, not the current reading location.

`chapter_title` belongs in `CurrentView / Position`, because it describes the current location in the reading flow. `output_language` is not part of the first-slice Ingest context.

### CurrentView

Maps from the old `reading_position` and `mainline_preview`.

`CurrentView` is the source text currently visible to Ingest for next-unit selection. It is not the already accepted reading object. The accepted object is produced by Ingest and later becomes Digest's `CurrentFocus / ReadingObject / SourceUnit`.

#### Position

`Position` contains the current chapter reference, current source cursor, and retry evidence when the runtime is asking for a second anchor attempt.

Target fields:

```json
{
  "current_chapter_id": 1,
  "current_chapter_ref": "chapter_1",
  "chapter_title": "...",
  "current_cursor": {},
  "retry": false
}
```

On retry, runtime may also include `previous_end_anchor_text`, `previous_resolution`, and `retry_instruction`.

#### Content

`Content` contains the paragraph-offset source preview rendered as XML paragraphs where practical.

Paragraph indexes and text roles may be attributes. The source text itself remains visible and primary.

### RetrievalSurface

This was an intentionally empty placeholder in the first design slice.

The current live Ingest XML still keeps `<RetrievalSurface />` empty because retrieved memory is not shown to Ingest. Concrete recall behavior now lives in the follow-through design: Ingest calls `retrieve_unit_memory` with `memory_recalls[]` args, and runtime renders selected Understanding lines into Digest `ReadingMemory`.

### OutputContract

Maps from the old Navigate return JSON. This section records the first-slice boundary-only output; the current follow-through behavior carries bounded `memory_recalls[]` only in the `retrieve_unit_memory` action-tool args.

#### OutputFields

`OutputFields` names the information Ingest must output.

Fields:

- `end_anchor_text`: exact visible source quote at the end of the chosen unit
- `boundary_type`: boundary classification for why the unit ends there
- `reason`: brief internal reason for the boundary choice

#### ReturnFormat

`ReturnFormat` defines the concrete JSON shape.

Return JSON only:

```json
{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "...",
  "memory_recalls": []
}
```

#### BoundaryOutput

The selected unit is represented by the flat boundary output above. Runtime owns the start cursor, anchor resolution, source span, source id, retry/fallback handling, and final accepted source unit.

The output preserves the current Navigate boundary semantics for:

- `end_anchor_text`
- `boundary_type`
- `reason`

## Old-To-New Mapping

| Current Navigate prompt surface | Target Ingest XML surface | Notes |
| --- | --- | --- |
| `You are Navigate...` | `ReaderRole` plus `Instruction / CurrentStep` | Replace the old node-specific role with the reader role fragment `reader.role`; put the Ingest step position in `CurrentStep`. |
| `Your single job is to choose...` | `Instruction / CurrentStep` | Replace with the current Ingest step framing: select the next source unit; memory support is now handled by `RecallPriorReading` / `retrieve_unit_memory` args in the follow-through design. |
| Next-unit task framing | `Instruction / SelectNextUnit` | Name the task and keep the detailed boundary policy together here. |
| Boundary-selection rules | `Instruction / SelectNextUnit` | Reuse almost directly. This is where the already-approved next-unit selection prompt content belongs. |
| no old equivalent | `Instruction / RecallPriorReading` | Follow-through design: ask what prior reading should be remembered for the selected unit; runtime maps recalls to retrieval. |
| `Structural frame` | `BookInfo / BookIdentity` and `CurrentView / Position` | Keep stable book identity in `BookInfo`; move `chapter_title` to `CurrentView / Position`; do not carry an output-language block in first-slice Ingest. |
| `Reading position` | `CurrentView / Position` | Keep current cursor and retry feedback here. |
| `Mainline preview` | `CurrentView / Content` | Prefer paragraph XML nodes over one JSON blob. |
| `Mainline cursor` | `CurrentView / Position` | Keep only cursor facts needed to understand where the preview starts; do not revive mode/decision fields. |
| `Navigation context` | not carried as a first-slice state block | Do not inject recent-memory or continuity summaries into Ingest by default. |
| `Policy snapshot` | `Instruction / SelectNextUnit` policy | Unit-selection policy stays here; retrieval behavior lives in `RecallPriorReading` and runtime Unit Memory selection. |
| `Output language contract` | omitted | Ingest has no reader-facing natural-language output in this slice; `end_anchor_text` is copied source text and `reason` is internal. |
| `end_anchor_text` | `end_anchor_text` | Same semantics: exact quote from preview tail. |
| `boundary_type` | `boundary_type` | Same boundary vocabulary unless later simplified. |
| `reason` | `reason` | Keep short explanation; useful for trace/audit. |
| no old equivalent | `retrieve_unit_memory.memory_recalls[]` | New Ingest responsibility specified in the follow-through design. |

## Boundary-Selection Content To Reuse

The current Navigate policy should carry forward into `Instruction / SelectNextUnit`.

Reuse rule:

- Keep the mature unit-boundary policy inside the `SelectNextUnit` fixed fragment, proposed id: `ingest.select_next_unit`.
- Start from the current `attentional_v2.navigate` boundary rules.
- Preserve the operational behavior unless the Ingest design explicitly changes it later.
- Adjust only names and routing boundaries required by the new XML structure.

The following current Navigate rules should carry forward almost directly:

- choose directly from the provided forward preview
- respect author structure first
- choose the smallest complete local move that can honestly be read as one unit
- prefer ending within the current paragraph
- cross into the next paragraph only when the same local move clearly continues
- treat headings as weak structure cues, not automatic standalone units
- merge label-like headings with following body text when the preview allows
- trim only purely non-lexical boundary residue
- judge from visible source text first
- never cross the provided preview boundary
- the unit always starts at the current source cursor
- return an exact `end_anchor_text` copied character-for-character from the preview
- preserve an honest boundary when the move is still unfolding; do not overstate closure

The following current Navigate prompt material should move or be adjusted:

- `You are Navigate...` should not carry forward as text. The product-level identity comes from top-level `<ReaderRole>` / `reader.role`; the step framing comes from `Instruction / CurrentStep`.
- `Your single job is to choose...` should be replaced by the Ingest instruction charter; current retrieval support is expressed through `RecallPriorReading` rather than the boundary-selection rules.
- `Use navigation context only as secondary support...` should not carry forward in the first Ingest slice, because the current target context has no carried reading-state block.
- `Do not request tools or external web search` should not be copied unchanged. Current live behavior allows only the mechanism-private Unit Memory retrieval tool, never external web search:

```text
Do not request external web search. If you write one or more prior-reading recalls, use the available Unit Memory retrieval tool so runtime can prepare support for Digest.
```

- `Return JSON only` belongs in `Instruction / ExecutionLimits` and the concrete `OutputContract`.
- The old flat return JSON example belongs in `OutputContract` as the first-slice Ingest return shape. The current follow-through path keeps final output boundary-focused and sends recalls through `retrieve_unit_memory`.

## Runtime Boundary

The LLM-call/runtime split from `DEC-106` should remain.

In the target shape:

1. Reading Runner builds the Ingest prompt packet.
2. Ingest LLM returns the boundary JSON and may call the mechanism-private `retrieve_unit_memory` tool with bounded `memory_recalls[]`.
3. If recalls are non-empty, the tool result returns status/count metadata only.
4. Reading Runner resolves `end_anchor_text`, retries/falls back if needed, accepts the source unit, executes/records runtime Unit Memory retrieval, and selects prompt-facing Understanding memory.
5. Reading Runner assembles the Digest packet with:
   - accepted source unit
   - retrieved supporting memory later, once retrieval is designed
   - compact carried state still needed by Digest
6. Digest reads the unit and produces reader-facing/current-reading outputs.
7. Reading Runner settles output, memory updates, audit, unit ledger, and cursor advance.

This means the first Ingest LLM call should not directly contain retrieved memory bodies produced after its own selection, unless the implementation later adopts an explicit multi-step Ingest tool loop.

## Digest Packet Implication

The Ingest output is not the final Digest context. The Digest context should be assembled after runtime boundary acceptance. Retrieval execution will be added later once the memory design defines it.

Digest should receive:

- the accepted source unit, not just the preview
- retrieved supporting memory later, once retrieval is designed
- compact local continuity that remains useful for reading
- output contract for reader-facing note/highlight/reaction work

Digest should not receive the entire Ingest preview, all candidate memory indexes, or runtime retry/audit machinery unless a later design gives a specific reason.

## Open Design Questions

- Should `memory_retrieval_requests` be emitted in the same Ingest call, or should Ingest become an explicit tool loop after boundary acceptance?
- Should `reason` remain in the long-term contract, or become audit-only once confidence is high?
- Should `boundary_type` keep the current unitization vocabulary, or become a smaller Digest-facing boundary classification?
- Which memory indexes are allowed once the new memory design lands?
- What should `RetrievalSurface` contain after the new memory design defines the available retrieval surface?
- How much retrieved support should Digest receive before it starts overweighting prior memory against the current source unit?

## Non-Goals For The First Mapping

- no Detour / source-backread restoration
- no old source-skill loop restoration
- no ActiveRecall / look_back revival
- no eval run
- no evidence catalog update
- no claim that future Ingest memory retrieval is implemented
- no final Digest prompt design
