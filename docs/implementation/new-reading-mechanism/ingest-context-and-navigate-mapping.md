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

The target Ingest prompt should follow the same top-level block discipline as the newer Read XML prompt:

```xml
<RoleAndInstruction>
  <IngestRole>...</IngestRole>
  <ContextUseGuide>...</ContextUseGuide>
  <BoundarySelection>...</BoundarySelection>
  <MemoryRetrievalPlanning>...</MemoryRetrievalPlanning>
  <ResponseDiscipline>...</ResponseDiscipline>
</RoleAndInstruction>

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

### RoleAndInstruction

`RoleAndInstruction` should contain fixed prompt fragments, not runtime state.

Recommended sub-blocks:

- `IngestRole`
  - says that Ingest prepares the next reading object for Digest
  - says that Ingest selects a forward source unit and requests memory support
- `ContextUseGuide`
  - tells the model how to use `BookInfo`, `ReadingState`, `CurrentFocus`, `RetrievalSurface`, and `OutputContract`
  - emphasizes that the visible source preview is primary
  - says prior state can support boundary/retrieval judgment but must not override the source text
- `BoundarySelection`
  - reuses the current Navigate boundary-selection rules
- `MemoryRetrievalPlanning`
  - new rules for proposing memory retrieval requests
  - tells the model to retrieve only for the selected unit
  - favors dependency, premise, reference, contrast, unresolved attention, and continuity needs
  - rejects broad "recent because recent" retrieval
- `ResponseDiscipline`
  - JSON only
  - no external search
  - no interpretation, note writing, or memory mutation

### BookInfo

Maps from the old `structural_frame`.

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

Target sub-blocks:

- `ContinuityState`
  - compact local/session continuity
  - current forward cursor continuity if useful
- `PriorReadingState`
  - compact `recent_reading_memory` digest or active entries
  - thin `active_attention` digest while that store remains active
  - compact `concept_digest`
  - compact `thread_digest`
  - compact reflective/chapter frame when useful

This block supports unit-boundary judgment and helps Ingest decide what memory support might matter. It should not contain large source excerpts, audit ledgers, reaction history, or historical route/move data.

### CurrentFocus

Maps from the old `reading_position`, `mainline_preview`, and `mainline_cursor`.

Target sub-blocks:

- `ReadingPath`
  - current path mode, currently forward/mainline only
  - no detour, route, source-backread, or selection-mode surface
- `ReadingPosition`
  - current chapter reference
  - current source cursor
  - retry evidence when the runtime is asking for a second anchor attempt
- `SourcePreview`
  - paragraph-offset preview rendered as XML paragraphs where practical
  - paragraph indexes and text roles may be attributes
  - the source text itself remains visible and primary
- `IngestIntent`
  - `select_next_unit_and_request_memory_support`

### RetrievalSurface

This is the new block with no direct old Navigate equivalent.

It should contain just enough discoverability for Ingest to ask for relevant memory support without injecting all memory bodies into the prompt.

Target sub-blocks:

- `AvailableMemoryStores`
  - the memory stores or indexes Ingest is allowed to request from
  - examples: `recent_reading_memory`, later durable memory index, selected concept/thread indexes if re-adopted
- `MemoryIndex`
  - lightweight memory cards / index entries
  - content-bearing labels, not vague taxonomy names
  - should be enough for the model to decide what to request
- `RetrievalPolicy`
  - request budget
  - allowed retrieval purposes
  - max results per request
  - source-grounding preference
  - no broad retrieval rule

This block should not contain full memory detail by default. The retrieval-first rule is: expose a discoverability layer first, then let runtime fetch deeper detail when Ingest requests it.

### OutputContract

Maps from the old return JSON and language contract, with one new retrieval-request field.

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

`selected_unit` preserves the current Navigate output semantics. `memory_retrieval_requests` is new and should be interpreted by runtime/tooling after the boundary-selection call.

## Old-To-New Mapping

| Current Navigate prompt surface | Target Ingest XML surface | Notes |
| --- | --- | --- |
| `You are Navigate...` | `RoleAndInstruction / IngestRole` | Rename role from path navigation to reading-object ingestion. |
| Boundary-selection rules | `RoleAndInstruction / BoundarySelection` | Reuse almost directly. |
| `Structural frame` | `BookInfo / BookIdentity` | Move output-language concerns to `OutputContract`. |
| `Reading position` | `CurrentFocus / ReadingPosition` | Keep current cursor and retry feedback here. |
| `Mainline preview` | `CurrentFocus / SourcePreview` | Prefer paragraph XML nodes over one JSON blob. |
| `Mainline cursor` | `CurrentFocus / ReadingPath` and `ReadingPosition` | Keep forward-only cursor facts; do not revive mode/decision fields. |
| `Navigation context` | `ReadingState` plus `RetrievalSurface` | Split continuity state from retrieval discoverability. |
| `Policy snapshot` | `BoundarySelection` policy plus `RetrievalPolicy` | Separate boundary budget from retrieval budget. |
| `Output language contract` | `OutputContract / LanguageContract` | Follow Read XML structure. |
| `end_anchor_text` | `selected_unit.end_anchor_text` | Same semantics: exact quote from preview tail. |
| `boundary_type` | `selected_unit.boundary_type` | Same boundary vocabulary unless later simplified. |
| `reason` | `selected_unit.reason` | Keep short explanation; useful for trace/audit. |
| `continuation_pressure` | `selected_unit.continuation_pressure` | Same meaning: chosen boundary may still carry forward pressure. |
| no old equivalent | `memory_retrieval_requests[]` | New Ingest responsibility. |

## Boundary-Selection Content To Reuse

The current Navigate policy should carry forward into `BoundarySelection`:

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

The instruction `Do not request tools or external web search` should not be copied unchanged. It should become:

```text
Do not request external web search. Request only prior-reading memory support through memory_retrieval_requests.
```

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
