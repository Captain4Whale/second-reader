# Ingest Context And Navigate Mapping

Purpose: capture the first design mapping from the current forward-only `Navigate` prompt to the proposed `Ingest` LLM call before implementation.
Use when: designing the `Ingest -> Digest` prompt/context split, migrating the current Navigate boundary-selection prompt into XML assembly, or checking what existing boundary-selection behavior should be reused.
Not for: stable mechanism authority, final prompt text, runtime implementation status, or evidence-catalog claims.
Update when: the Ingest role, XML context shape, retrieval-request contract, or mapping from old Navigate fields changes before implementation.

## Status

- Date: `2026-05-31`
- Status: working design note.
- Code status: not implemented.
- Evaluation status: no eval run, no evidence-catalog update.
- Current basis:
  - `DEC-103` pauses the old Second Reader Memory / Planning implementation track as the default direction.
  - `DEC-104` retires live Detour / source-backread.
  - `DEC-105` hard-purges retired Detour / backread / source-skill interfaces.
  - `DEC-106` separates the LLM call from runtime preparation / boundary governance.
  - Current code keeps the mature forward boundary-selection logic in `llm_calls.navigate(...)`.

## Design Claim

The current `Navigate` prompt already performs the useful first half of `Ingest`: selecting the next forward semantic reading unit from the current source frontier. That boundary-selection policy should be reused rather than redesigned.

The main change is not the boundary-selection content. The change is the node identity and context structure:

- old name: `Navigate`
- new name: `Ingest`
- old role: choose the next readable unit
- new role: choose the next readable unit and request prior-reading memory support for that unit
- old structure: flat prompt sections with JSON blocks
- new structure: XML prompt assembly aligned with the newer Read prompt framework
- old context block: `navigation_context`
- new split:
  - `ReadingState` for carried reading continuity used while choosing the unit
  - `RetrievalSurface` for memory indexes / retrieval policy used to request support for Digest

## Target Ingest Definition

`Ingest` is the reading-before-reading LLM call.

It receives the current reading frontier, a bounded forward source preview, compact prior-reading state, and a retrieval surface. It returns the next source-unit boundary plus a small set of memory retrieval requests that would help `Digest` read that unit continuously.

`Ingest` does not:

- interpret the selected unit for the reader
- produce reader-facing notes, highlights, or surfaced reactions
- update memory
- choose a backward path or source detour
- run external web search
- own runtime anchor resolution, retry, fallback, retrieval execution, settlement, or cursor advancement

## Target XML Context Shape

The target Ingest prompt should follow the XML assembly discipline used by the newer Read prompt, but its top-level blocks should be semantically direct. `ReaderRole` and `Instruction` are both top-level prompt blocks; do not wrap them in a `RoleAndInstruction` container.

Top-level rule:

- `ReaderRole` owns the stable reader identity.
- `Instruction` owns all fixed non-role directions for this LLM call.
- Runtime context/data blocks stay outside `Instruction`: `BookInfo`, `ReadingState`, `CurrentFocus`, `RetrievalSurface`, and `OutputContract`.

```xml
<ReaderRole>...</ReaderRole>

<Instruction>
  <CurrentStep>...</CurrentStep>
  <ContextUseGuide>...</ContextUseGuide>
  <SelectNextUnit>...</SelectNextUnit>
  <RequestMemorySupport>...</RequestMemorySupport>
  <ExecutionLimits>...</ExecutionLimits>
</Instruction>

<BookInfo>
  <BookIdentity>{...}</BookIdentity>
</BookInfo>

<ReadingState>
  <ContinuityState>{...}</ContinuityState>
  <PriorReadingState>{...}</PriorReadingState>
</ReadingState>

<CurrentFocus>
  <ReadingPath>{...}</ReadingPath>
  <ReadingPosition>{...}</ReadingPosition>
  <SourcePreview>
    <Paragraph n="..." role="..." start_char="..." end_char="...">...</Paragraph>
  </SourcePreview>
  <IngestIntent>{...}</IngestIntent>
</CurrentFocus>

<RetrievalSurface>
  <AvailableMemoryStores>{...}</AvailableMemoryStores>
  <MemoryIndex>{...}</MemoryIndex>
  <RetrievalPolicy>{...}</RetrievalPolicy>
</RetrievalSurface>

<OutputContract>
  <LanguageContract>...</LanguageContract>
  <ReturnFormat>...</ReturnFormat>
  <FieldContracts>...</FieldContracts>
</OutputContract>
```

### ReaderRole

`ReaderRole` should contain the fixed product-level reader identity, not runtime state.

Rules:

- must reference the same prompt fragment used by the current Read XML prompt: `reader.role`
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
- `RequestMemorySupport`
- `ExecutionLimits`

The child blocks should correspond to distinct model responsibilities, not to every policy paragraph. This keeps `Instruction` readable while avoiding duplicated task/policy pairs.

Merge rule:

- `CurrentStep` absorbs the old `StepPosition` and `TaskOverview`.
- `SelectNextUnit` absorbs the old `NextUnitSelection` and `BoundarySelection`.
- `RequestMemorySupport` absorbs the old `MemorySupportTask` and `MemoryRetrievalPlanning`.
- `ExecutionLimits` absorbs the old `ResponsibilityBoundary` and `ResponseDiscipline`.

Target assembly shape:

```xml
<ReaderRole prompt_fragment_ref="reader.role" />

<Instruction>
  <CurrentStep prompt_fragment_ref="ingest.current_step" />
  <ContextUseGuide prompt_fragment_ref="ingest.context_use_guide" />
  <SelectNextUnit prompt_fragment_ref="ingest.select_next_unit" />
  <RequestMemorySupport prompt_fragment_ref="ingest.request_memory_support" />
  <ExecutionLimits prompt_fragment_ref="ingest.execution_limits" />
</Instruction>
```

The `prompt_fragment_ref` attributes above are implementation-facing references in the assembly spec. The rendered model-facing XML should contain only resolved text, following the current Read XML assembly convention.

Recommended `Instruction` child meanings:

#### CurrentStep

`CurrentStep` says the model is in the `Ingest` step of a sequential deep-reading loop. This step happens before `Digest`: the model is previewing the next forward source area, not yet producing the final reading of that unit.

It defines two outputs for the call:

- selected next source unit boundary
- prior-reading memory retrieval requests for that selected unit

Proposed `ingest.current_step` fragment:

```text
You are in the Ingest step of a sequential deep-reading loop.

This step happens before Digest. You are not yet reading the selected unit for interpretation or reader-facing output. You are previewing the bounded forward source area from the current reading cursor in order to prepare Digest.

Your work in this call has two outputs:
- select the next forward source unit that you should read carefully in the Digest step;
- request prior-reading memory support that would help you read that selected unit continuously in the Digest step.
```

#### ContextUseGuide

`ContextUseGuide` tells the model how to use `BookInfo`, `ReadingState`, `CurrentFocus`, `RetrievalSurface`, and `OutputContract`.

It should emphasize:

- the visible source preview is primary
- prior state can support boundary/retrieval judgment
- prior state must not override the source text

#### SelectNextUnit

`SelectNextUnit` says Ingest must select one forward source unit from the current frontier. The unit starts at the current source cursor and ends at an exact visible anchor.

This is where the already-approved "determine next unit" task and prompt rules are placed together. It contains the mature next-unit boundary policy reused from current Navigate.

#### RequestMemorySupport

`RequestMemorySupport` says Ingest should ask what prior reading memory is needed in order to read the selected unit continuously in the Digest step.

It contains the detailed recall-query policy:

- Ingest emits retrieval queries / requests only
- actual retrieval is outside this LLM call
- favor dependency, premise, reference, contrast, unresolved attention, and continuity needs
- reject broad "recent because recent" retrieval

#### ExecutionLimits

`ExecutionLimits` says what Ingest must not do.

It should state:

- do not interpret the selected unit for the reader
- do not write notes, highlights, surfaced reactions, or memory updates
- do not execute retrieval, resolve anchors, retry/fallback, settle runtime state, or advance the cursor
- do not request external search
- return JSON only and follow `OutputContract`

### BookInfo

Maps from the old `structural_frame`.

#### BookIdentity

Target fields:

```json
{
  "book_title": "...",
  "author": "...",
  "chapter_title": "..."
}
```

`output_language` should move out of `BookInfo` and into `OutputContract / LanguageContract`, following the Read XML pattern.

### ReadingState

Maps from the old `navigation_context`, but only the continuity-bearing subset belongs here.

#### ContinuityState

`ContinuityState` carries compact local/session continuity and current forward cursor continuity if useful.

#### PriorReadingState

`PriorReadingState` carries compact prior-reading state useful for continuity and memory-support judgment.

Candidate contents:

- compact `recent_reading_memory` digest or active entries
- thin `active_attention` digest while that store remains active
- compact `concept_digest`
- compact `thread_digest`
- compact reflective/chapter frame when useful

This block supports unit-boundary judgment and helps Ingest decide what memory support might matter. It should not contain large source excerpts, audit ledgers, reaction history, or historical route/move data.

### CurrentFocus

Maps from the old `reading_position`, `mainline_preview`, and `mainline_cursor`.

#### ReadingPath

`ReadingPath` contains the current path mode, currently forward/mainline only.

It must not expose detour, route, source-backread, or selection-mode surfaces.

#### ReadingPosition

`ReadingPosition` contains the current chapter reference, current source cursor, and retry evidence when the runtime is asking for a second anchor attempt.

#### SourcePreview

`SourcePreview` contains the paragraph-offset preview rendered as XML paragraphs where practical.

Paragraph indexes and text roles may be attributes. The source text itself remains visible and primary.

#### IngestIntent

`IngestIntent` is `select_next_unit_and_request_memory_support`.

### RetrievalSurface

This is the new block with no direct old Navigate equivalent.

It should contain just enough discoverability for Ingest to ask for relevant memory support without injecting all memory bodies into the prompt.

#### AvailableMemoryStores

`AvailableMemoryStores` lists the memory stores or indexes Ingest is allowed to request from.

Examples: `recent_reading_memory`, later durable memory index, selected concept/thread indexes if re-adopted.

#### MemoryIndex

`MemoryIndex` contains lightweight memory cards / index entries.

Entries should use content-bearing labels, not vague taxonomy names. They should be enough for the model to decide what to request.

#### RetrievalPolicy

`RetrievalPolicy` contains request budget, allowed retrieval purposes, max results per request, source-grounding preference, and the no-broad-retrieval rule.

This block should not contain full memory detail by default. The retrieval-first rule is: expose a discoverability layer first, then let runtime fetch deeper detail when Ingest requests it.

### OutputContract

Maps from the old return JSON and language contract, with one new retrieval-request field.

#### LanguageContract

`LanguageContract` follows the Read XML structure. Explanatory fields should use the configured output language; source quotes remain in the source language.

#### ReturnFormat

`ReturnFormat` requires JSON only.

#### FieldContracts

Target top-level fields:

```json
{
  "selected_unit": {
    "end_anchor_text": "...",
    "boundary_type": "paragraph_end",
    "reason": "...",
    "continuation_pressure": false
  },
  "memory_retrieval_requests": [
    {
      "query": "...",
      "purpose": "dependency|premise|reference|contrast|unresolved_attention|continuity",
      "memory_kinds": ["recent_reading_memory"],
      "why_needed_for_selected_unit": "...",
      "expected_use_for_digest": "..."
    }
  ]
}
```

#### SelectedUnit

`selected_unit` preserves the current Navigate output semantics.

`selected_unit` contains:

- `end_anchor_text`
- `boundary_type`
- `reason`
- `continuation_pressure`

#### MemoryRetrievalRequests

`memory_retrieval_requests` is new and should be interpreted by runtime/tooling after the boundary-selection call.

Each request contains:

- `query`
- `purpose`
- `memory_kinds`
- `why_needed_for_selected_unit`
- `expected_use_for_digest`

## Old-To-New Mapping

| Current Navigate prompt surface | Target Ingest XML surface | Notes |
| --- | --- | --- |
| `You are Navigate...` | `ReaderRole` plus `Instruction / CurrentStep` | Replace the old node-specific role with the reader role fragment `reader.role`; put the Ingest step position in `CurrentStep`. |
| `Your single job is to choose...` | `Instruction / CurrentStep` | Replace with the two-part Ingest task: select the next source unit and request memory support. |
| Next-unit task framing | `Instruction / SelectNextUnit` | Name the task and keep the detailed boundary policy together here. |
| Boundary-selection rules | `Instruction / SelectNextUnit` | Reuse almost directly. This is where the already-approved next-unit selection prompt content belongs. |
| no old equivalent | `Instruction / RequestMemorySupport` | Name the recall task and put the detailed retrieval-query policy together here. |
| `Structural frame` | `BookInfo / BookIdentity` | Move output-language concerns to `OutputContract`. |
| `Reading position` | `CurrentFocus / ReadingPosition` | Keep current cursor and retry feedback here. |
| `Mainline preview` | `CurrentFocus / SourcePreview` | Prefer paragraph XML nodes over one JSON blob. |
| `Mainline cursor` | `CurrentFocus / ReadingPath` and `ReadingPosition` | Keep forward-only cursor facts; do not revive mode/decision fields. |
| `Navigation context` | `ReadingState` plus `RetrievalSurface` | Split continuity state from retrieval discoverability. |
| `Policy snapshot` | `Instruction / SelectNextUnit` policy plus `RetrievalSurface / RetrievalPolicy` | Separate boundary policy from retrieval budget. |
| `Output language contract` | `OutputContract / LanguageContract` | Follow Read XML structure. |
| `end_anchor_text` | `selected_unit.end_anchor_text` | Same semantics: exact quote from preview tail. |
| `boundary_type` | `selected_unit.boundary_type` | Same boundary vocabulary unless later simplified. |
| `reason` | `selected_unit.reason` | Keep short explanation; useful for trace/audit. |
| `continuation_pressure` | `selected_unit.continuation_pressure` | Same meaning: chosen boundary may still carry forward pressure. |
| no old equivalent | `memory_retrieval_requests[]` | New Ingest responsibility. |

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
- use prior reading state only as secondary support
- judge from visible source text first
- never cross the provided preview boundary
- the unit always starts at the current source cursor
- return an exact `end_anchor_text` copied character-for-character from the preview
- preserve `continuation_pressure` when the move is still unfolding

The following current Navigate prompt material should move or be adjusted:

- `You are Navigate...` should not carry forward as text. The product-level identity comes from top-level `<ReaderRole>` / `reader.role`; the step framing comes from `Instruction / CurrentStep`.
- `Your single job is to choose...` should be replaced by the Ingest instruction charter, because Ingest now has two outputs: selected unit and memory retrieval requests.
- `Use navigation context only as secondary support...` should become `Use ReadingState only as secondary support...`; the rule still belongs in `Instruction / SelectNextUnit`.
- `Do not request tools or external web search` should not be copied unchanged. It should become:

```text
Do not request external web search. Request only prior-reading memory support through memory_retrieval_requests.
```

- `Return JSON only` belongs in `Instruction / ExecutionLimits` and the concrete `OutputContract`.
- The old flat return JSON example belongs in `OutputContract`, nested under `selected_unit` plus `memory_retrieval_requests`.

## Runtime Boundary

The LLM-call/runtime split from `DEC-106` should remain.

In the target shape:

1. Reading Runner builds the Ingest prompt packet.
2. Ingest LLM returns `selected_unit` and `memory_retrieval_requests`.
3. Reading Runner resolves `selected_unit.end_anchor_text`, retries/falls back if needed, and accepts the source unit.
4. Runtime/tooling executes memory retrieval requests against allowed memory stores.
5. Reading Runner assembles the Digest packet with:
   - accepted source unit
   - retrieved supporting memory
   - compact carried state still needed by Digest
6. Digest reads the unit and produces reader-facing/current-reading outputs.
7. Reading Runner settles output, memory updates, audit, unit ledger, and cursor advance.

This means the first Ingest LLM call should not directly contain retrieved memory bodies produced after its own selection, unless the implementation later adopts an explicit multi-step Ingest tool loop.

## Digest Packet Implication

The Ingest output is not the final Digest context. The Digest context should be assembled after runtime boundary acceptance and retrieval execution.

Digest should receive:

- the accepted source unit, not just the preview
- retrieved supporting memory selected because of the accepted unit
- compact local continuity that remains useful for reading
- output contract for reader-facing note/highlight/reaction work

Digest should not receive the entire Ingest preview, all candidate memory indexes, or runtime retry/audit machinery unless a later design gives a specific reason.

## Open Design Questions

- Should `memory_retrieval_requests` be emitted in the same first Ingest call, or should Ingest become an explicit tool loop after boundary acceptance?
- Should `selected_unit.reason` remain in the long-term contract, or become audit-only once confidence is high?
- Should `boundary_type` keep the current unitization vocabulary, or become a smaller Digest-facing boundary classification?
- Which memory indexes are allowed in the first implementation slice: only `recent_reading_memory`, or a new durable memory index as well?
- Should `RetrievalSurface / MemoryIndex` contain source-span handles, natural-language labels, or both?
- How much retrieved support should Digest receive before it starts overweighting prior memory against the current source unit?

## Non-Goals For The First Mapping

- no Detour / source-backread restoration
- no old source-skill loop restoration
- no ActiveRecall / look_back revival
- no eval run
- no evidence catalog update
- no claim that the new Ingest prompt is implemented
- no final Digest prompt design
