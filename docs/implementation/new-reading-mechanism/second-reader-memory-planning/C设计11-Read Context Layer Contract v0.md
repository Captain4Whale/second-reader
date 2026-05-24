# C设计11 - Read Context Layer Contract v0

## Purpose

This document records the evolving contract for how the `attentional_v2` Read node should receive structured context.

It starts from the current code fact that Read already receives structured data, but that the outer semantic layering is not yet clear enough. The current implementation sends a JSON-heavy prompt packet; this is structured for the program, but not yet ideal as a reader-facing context contract for the LLM.

This document is intentionally incremental. At this point it records the first accepted design decision: **use XML-style outer tags for high-level context layers, while keeping JSON for each layer's internal data payload when JSON is the natural machine-owned structure**.

## Status

- Status: `draft / design-in-progress`.
- Scope now: context-layer contract and prompt expression design.
- Not yet scope:
  - code implementation;
  - prompt version bump;
  - eval run;
  - Recent Memory consolidation;
  - Active Attention cleanup;
  - evidence catalog update;
  - product-quality claim.

## Current Problem Statement

The current Read prompt is not unstructured, but its structure is mostly an engineering packet. Different context roles can appear side by side, including book metadata, current source unit, carried memory, local orientation, optional source evidence, runtime policy, and output schema.

This can be valid JSON, but the LLM may not clearly understand the role boundary of each section unless the outer prompt explains those boundaries. In particular, the model needs to know which material is:

- stable role / behavior instruction;
- book or source metadata;
- reading state already carried from prior reading;
- current reading object and path;
- optional retrieved / detour / look-back evidence;
- runtime policy;
- output schema.

## Decision 1: XML Outer Layers, JSON Inner Payloads

Accepted direction:

> Use XML-style outer tags to mark high-level context layers. Inside each layer, keep JSON payloads when the data is program-owned, structured, and already naturally represented as JSON.

The key point is not XML as decoration. The key point is role isolation: the model should not have to infer from field names alone what role each block plays.

## Why XML Outside

XML-style tags are useful here because they are:

- **self-describing**: the tag name says what role the block plays;
- **visibly bounded**: the LLM can see where one context role ends and another begins;
- **nestable**: memory can contain near-term and long-distance sublayers without flattening their roles;
- **compatible with JSON payloads**: the program can still emit strict JSON inside a tagged block;
- **less ambiguous than a single large JSON packet** for mixed instruction / task / memory / evidence / output-contract material.

## Why Keep JSON Inside

JSON remains appropriate inside a layer when the payload is:

- produced by code;
- tested by schema or snapshot tests;
- naturally list / object shaped;
- consumed again by program logic;
- easier to diff and validate as structured data.

Therefore this design does **not** propose converting all context data to prose or all inner payloads to XML.

The recommended rule is:

> XML owns the outer semantic layer. JSON owns the inner machine-shaped value.

## Current Accepted Boundary

The following Read prompt structure decisions are accepted here:

- outer structure should use XML-style tags;
- no single outer root tag is required;
- inner machine values may remain JSON;
- Read context should be organized by product-semantic role rather than by incidental implementation packet names or provider API message split;
- the top-level XML blocks are `RoleAndInstruction`, `BookAndChapterInfo`, `ReadingState`, `CurrentFocus`, and `OutputContract`;
- `RoleAndInstruction` and `OutputContract` are prompt structure, not reading input data;
- code should not be changed until the actual Read context layer taxonomy is accepted.

This document now settles the initial readable skeleton, but not the exact field-level projection policy or implementation details.

## Accepted Read Prompt Structure

The Read node prompt should be expressed as several semantically structured XML blocks:

```xml
<RoleAndInstruction>...</RoleAndInstruction>
<BookAndChapterInfo>...</BookAndChapterInfo>
<ReadingState>...</ReadingState>
<CurrentFocus>...</CurrentFocus>
<OutputContract>...</OutputContract>
```

This structure is product-semantic. It is not a statement about whether the underlying provider call uses `system`, `user`, or any other message role.

Current code fact: `read_unit` still renders the old flat prompt from `ATTENTIONAL_V2_PROMPTS.read_unit_prompt` with `Structural frame`, `Current unit`, `Read context packet`, `Selective carry`, `Policy snapshot`, `Output language contract`, and `Return JSON`. The target structure preserves useful information from those sections, but not their incidental implementation-shaped names.

## Fixed Prompt Fragment Referencing

Some top-level XML blocks contain fixed instruction text rather than per-call reading data. `RoleAndInstruction` is the first example.

The design needs two distinct layers:

1. **Template assembly layer**
   - May use stable prompt fragment ids such as `attentional_v2.read.role.v30`.
   - The id is an assembly key, not text for the model.
   - Program code resolves each id through a prompt fragment registry / prompt bundle before the final prompt is sent.
   - A template may therefore look like:

```xml
<RoleAndInstruction>
  <Role ref="attentional_v2.read.role.v30" />
  <ReadBehavior ref="attentional_v2.read.behavior.v30" />
  <ReactionInstruction ref="attentional_v2.read.reaction.v30" />
  <RecentMemoryInstruction ref="attentional_v2.read.recent_memory.v30" />
  <MemoryOperationInstruction ref="attentional_v2.read.memory_ops.v30" />
  <DetourAndRoutingInstruction ref="attentional_v2.read.detour.v30" />
</RoleAndInstruction>
```

2. **Final model-facing prompt layer**
   - Must not expose `ref` attributes or fragment ids.
   - Contains the resolved prompt text inside the XML tags.
   - The final prompt sent to the model should therefore look like:

```xml
<RoleAndInstruction>
  <Role>
    You are a careful reader moving through this book.
  </Role>
  <ReadBehavior>
    ...
  </ReadBehavior>
  <ReactionInstruction>
    ...
  </ReactionInstruction>
  <RecentMemoryInstruction>
    ...
  </RecentMemoryInstruction>
  <MemoryOperationInstruction>
    ...
  </MemoryOperationInstruction>
  <DetourAndRoutingInstruction>
    ...
  </DetourAndRoutingInstruction>
</RoleAndInstruction>
```

Rules:

- `ref` is a program-side template mechanism only.
- The model-facing prompt must not include fragment ids, file paths, Python variable names, or prompt registry handles.
- Fragment ids should be stable enough for tests, audits, and prompt manifests.
- Fragment ids should not encode filesystem paths. The registry can map ids to code, files, or generated prompt fragments internally.
- Current implementation now has a reusable prompt assembly infrastructure: `PromptFragment`, `PromptFragmentRegistry`, `PromptXmlNode`, and `render_prompt_xml(...)`.
- That infrastructure can resolve fixed fragments and render sibling / nested XML blocks without leaking template ids into model-facing text.
- It is not yet connected to the live Read prompt. `read_unit_system` and `read_unit_prompt` still use the old flat live path, and `READ_UNIT_PROMPT_VERSION` is unchanged.
- Current implementation has not yet split `read_unit_system` into physical fragments. The fragment structure below remains the migration target that preserves the current prompt content while making its functional sections explicit.

### 1. `RoleAndInstruction`

`RoleAndInstruction` defines what Read is and how it should read. It is fixed prompt instruction, not reading input data.

Current source:

- prompt library object: `ATTENTIONAL_V2_PROMPTS.read_unit_system`
- prompt version field: `READ_UNIT_PROMPT_VERSION`
- current value at this design point: `attentional_v2.read.v30`
- promptset field: `ATTENTIONAL_V2_PROMPTSET_VERSION`

Current implementation note: the generic fragment resolver and XML renderer exist in code, but these functional sections are not yet physically separate prompt fragments. They are currently contiguous text inside `read_unit_system`; the section names below are the target migration structure for future prompt assembly.

Target structure:

```xml
<RoleAndInstruction>
  <Role>...</Role>
  <ReadBehavior>...</ReadBehavior>
  <ReactionInstruction>...</ReactionInstruction>
  <RecentMemoryInstruction>...</RecentMemoryInstruction>
  <MemoryOperationInstruction>...</MemoryOperationInstruction>
  <DetourAndRoutingInstruction>...</DetourAndRoutingInstruction>
</RoleAndInstruction>
```

#### 1.1 `Role`

Purpose: tell the model what kind of actor Read is.

Current value source: the opening role and job lines in `ATTENTIONAL_V2_PROMPTS.read_unit_system`.

Value rule: Read is a careful continuous reader moving through a book, not a generic summarizer, highlighter, evaluator, or field-filling worker.

#### 1.2 `ReadBehavior`

Purpose: describe how Read should approach the current source unit.

Current value source: the early reading behavior rules in `read_unit_system`.

Value rules:

- read the current unit as the present reading object;
- use prompt-visible reading state naturally when it helps;
- do not collapse the unit into chapter summary or evaluator voice;
- stay proportionate around thin headings / labels / structural cues.

#### 1.3 `ReactionInstruction`

Purpose: describe `reading_impression` and `surfaced_reactions`.

Current value source: the reaction and source-quote rules in `read_unit_system`.

Value rules:

- `reading_impression` is the brief natural impression after reading;
- surfaced reactions are optional, bounded, and anchored to the current unit;
- each reaction's `source_quote` must be exact text from the current unit;
- visible reaction text must not contain raw internal ids or source-coordinate handles;
- reaction examples and negative examples should stay with this section rather than being split into an abstract negative-rules bucket.

#### 1.4 `RecentMemoryInstruction`

Purpose: describe what Recent Reading Memory Read should form after this unit.

Current value source: the Recent Reading Memory section in `read_unit_system`, currently at `read.v30`.

Value rules:

- write Recent Reading Memory when the unit establishes content worth carrying;
- write natural memory sentences / short paragraphs, not default `<label>: <explanation>` entries;
- record source-established content first;
- add interpretation only when needed to preserve source-established meaning;
- keep entries context-resolvable for future Read calls.

#### 1.5 `MemoryOperationInstruction`

Purpose: describe memory operation output beyond the Recent Memory writing style.

Current value source: the `memory_uptake_ops` rules and examples in `read_unit_system` and `read_unit_prompt`.

Value rules:

- allowed durable target stores currently include `recent_reading_memory`, `concept_registry`, and `thread_trace`;
- `active_attention` still exists in current code but is deprecated as a primary memory layer and should not be strengthened by this context redesign;
- digests such as `concept_digest`, `thread_digest`, and `active_focus_digest` are projections, not writable stores;
- when an operation needs current-source evidence, the LLM should provide an exact quote and the program should resolve the quote into source refs;
- the LLM should not invent source coordinates.

#### 1.6 `DetourAndRoutingInstruction`

Purpose: describe optional detour output and the boundary between Read and route control.

Current value source: the `detour_need` and route-control rules near the end of `read_unit_system`.

Value rules:

- Read may emit `detour_need` when current understanding genuinely needs earlier material;
- Read does not secretly route, resolve, or name the next route by itself;
- after Read returns, the runner settles the unit and advances normally unless a detour need is present;
- final return-format details belong in `OutputContract`, not here.

### 2. `BookAndChapterInfo`

`BookAndChapterInfo` orients Read inside the book and chapter. It should not become a coordinate dump.

Current source:

- `nodes._structural_frame(...)`
- current fields: `book_title`, `author`, `chapter_title`, `output_language`

Target structure:

```xml
<BookAndChapterInfo>
  <BookIdentity>{...}</BookIdentity>
  <ChapterFrame>{...}</ChapterFrame>
  <SourceLanguage>...</SourceLanguage>
</BookAndChapterInfo>
```

#### 2.1 `BookIdentity`

Purpose: identify the book-level frame.

Current value source: `book_title` and `author` from the `read_unit(...)` call arguments through `_structural_frame(...)`.

Target payload:

```json
{
  "book_title": "...",
  "author": "..."
}
```

#### 2.2 `ChapterFrame`

Purpose: identify the current chapter / section frame in human-readable terms.

Current value source: `chapter_title` from `read_unit(...)` through `_structural_frame(...)`; `chapter_path` is optional if runtime later exposes it.

Target payload:

```json
{
  "chapter_title": "...",
  "chapter_path": "..."
}
```

#### 2.3 `SourceLanguage`

Purpose: record source-language orientation when known.

Current value source: not consistently present in the current Read structural frame.

Value rule: include only when known; do not infer it from output language.

#### 2.4 Explicit exclusions

- `output_language` currently lives in the old structural frame, but semantically belongs under `OutputContract`.
- Exact `source_span`, sentence ids, source span ids, and other machine coordinates should not be foregrounded here.

### 3. `ReadingState`

`ReadingState` contains what the reader already carries from prior reading.

Target structure:

```xml
<ReadingState>
  <ReadingMemory>
    <NearTermMemory>...</NearTermMemory>
    <LongDistanceMemory>
      <ConceptMemory>...</ConceptMemory>
      <ThreadMemory>...</ThreadMemory>
      <StructuralMemory>...</StructuralMemory>
    </LongDistanceMemory>
  </ReadingMemory>
</ReadingState>
```

#### 3.1 `ReadingMemory`

Purpose: group prior-reading memory under one semantic layer.

Value rule: near-term and long-distance memory are both memory; they should not become separate top-level prompt layers.

##### 3.1.1 `NearTermMemory`

Purpose: provide active Recent Reading Memory from just-read units.

Current source:

- `state_projection.build_read_prompt_packet(...).recent_reading_memory`
- derived from `recent_reading_memory.entries[]`
- only entries with `status == "active"` are projected

Target payload:

```json
{
  "active_entries": [
    {
      "entry_id": "...",
      "kind": "...",
      "memory_text": "...",
      "source_unit_span_id": "...",
      "created_at_unit_index": 0
    }
  ],
  "active_entry_count": 0
}
```

Value rules:

- `memory_text` is the semantic content Read should use.
- `kind` is a light category, not a replacement for `memory_text`.
- `source_unit_span_id` and `created_at_unit_index` are provenance handles; they may remain in JSON for auditability but should not dominate the prompt.
- archived / consolidated entries should not be carried here.

##### 3.1.2 `LongDistanceMemory`

Purpose: provide durable memory formed from prior reading.

Value rule: this layer contains concept, thread, and structural memory.

###### 3.1.2.1 `ConceptMemory`

Current source:

- `state_projection.build_read_prompt_packet(...).concept_digest`
- derived from `concept_registry.entries[]`

Target payload:

```json
[
  {
    "ref_id": "concept:...",
    "concept_key": "...",
    "concept_type": "...",
    "rationale": "...",
    "sample_quotes": [],
    "source_refs": []
  }
]
```

Value rules:

- `rationale` is the prompt-facing concept summary from the store's canonical `summary`.
- `sample_quotes` support orientation but are not the concept itself.
- `source_refs` are audit/source grounding handles and should not be the semantic center.

###### 3.1.2.2 `ThreadMemory`

Current source:

- `state_projection.build_read_prompt_packet(...).thread_digest`
- derived from `thread_trace.entries[]`

Target payload:

```json
[
  {
    "ref_id": "thread:...",
    "thread_key": "...",
    "thread_type": "...",
    "rationale": "...",
    "sample_quotes": [],
    "source_refs": []
  }
]
```

Value rules:

- `rationale` is the prompt-facing description of the continuing arc / line of development.
- Thread memory is the long-distance place for recurring tensions, arcs, watchpoints, and unresolved lines after ActiveTension deprecation.
- `source_refs` and `sample_quotes` provide grounding support but should not make the block look like a source-coordinate task.

###### 3.1.2.3 `StructuralMemory`

Current source:

- `state_projection.build_read_prompt_packet(...).reflective_digest`
- related current structured source: `chapter_reflective_frame`
- derived from `reflective_frames`

Target payload:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

Value rules:

- use this block for macro/chapter/book-level understanding that has already been formed;
- do not use it for raw chapter source, runtime audit, or per-unit recent memory.

#### 3.2 Explicit `ReadingState` exclusions

These current or legacy packet fields should not be default `ReadingState` content:

- `local_continuity`;
- recent visible reactions;
- deprecated `active_attention` / ActiveTension as a carried state layer;
- `active_focus_digest`;
- `source_ref_digest`;
- `continuation_capsule`;
- `refs`;
- read / settlement audit traces.

If any content from these fields is semantically needed by future Read calls, represent it through Recent Reading Memory, Concept Memory, Thread Memory, Structural Memory, or explicit `CurrentFocus` evidence.

### 4. `CurrentFocus`

`CurrentFocus` describes what this Read call is currently reading and why.

Target structure:

```xml
<CurrentFocus>
  <ReadingPath>...</ReadingPath>
  <ReadingPosition>...</ReadingPosition>
  <ReadingObject>...</ReadingObject>
  <ReadingIntent>...</ReadingIntent>
  <OptionalSourceEvidence>...</OptionalSourceEvidence>
</CurrentFocus>
```

#### 4.1 `ReadingPath`

Purpose: identify the current reading path.

Current source:

- mainline/detour state from runner-local continuity and `detour_context`
- `state_projection.build_read_prompt_packet(...).selective_carry.active_detour_need` when present

Target payload:

```json
{
  "mode": "mainline|detour|look_back",
  "active_detour_need": {}
}
```

Value rules:

- default to `mainline` when no detour/look-back intent is active;
- include detour state only when this Read call is actually serving that path.

#### 4.2 `ReadingPosition`

Purpose: orient the current unit in human-readable reading position.

Current source:

- `current_unit_source.source_span`
- `current_unit_source.source_span_id`
- chapter title / chapter path from source metadata when available

Target payload:

```json
{
  "chapter_title": "...",
  "human_position": "...",
  "source_unit_span_id": "..."
}
```

Value rules:

- prefer human-readable position such as chapter and paragraph range;
- keep precise paragraph-char spans as program/audit metadata;
- do not ask Read to reason from coordinates when the task is to read the current unit.

#### 4.3 `ReadingObject`

Purpose: provide the actual current source unit to read.

Current source:

- `current_unit_source.source_text`
- current implementation also passes `current_unit_source.paragraph_slices[]`
- legacy fallback: `current_unit_sentences[]` with `sentence_id`, `text`, and `text_role`

Target structure:

```xml
<ReadingObject>
  <SourceUnit>
    <Paragraph n="...">...</Paragraph>
    <Paragraph n="...">...</Paragraph>
  </SourceUnit>
</ReadingObject>
```

Value rules:

- Read should primarily see the current unit source text.
- Preserve paragraph boundaries when useful.
- Do not expose the implementation name `paragraph_slices` as the reader-facing contract.
- Do not foreground `start_char`, `end_char`, or full `source_span` inside the reading object.
- Program code can retain source spans and char offsets for matching, audit, and resume.
- Sentence-shaped fallback is compatibility only, not the target context contract.

#### 4.4 `ReadingIntent`

Purpose: state why this unit is being read now when the reason is not simple mainline continuation.

Current source:

- default mainline read intent from runner path;
- detour/look-back intent from `detour_context.active_detour_need` or related selective carry.

Target payload:

```json
{
  "intent": "read_current_source_unit_in_sequence",
  "question_or_uncertainty": "",
  "target_hint": ""
}
```

Value rules:

- for normal mainline reading, keep this minimal;
- for detour/look-back reading, include the specific uncertainty or target.

#### 4.5 `OptionalSourceEvidence`

Purpose: provide bounded earlier source evidence only when the current read path needs it.

Current source:

- `state_projection.build_supplemental_selective_carry(...)`
- possible fields: `earlier_excerpts`, `source_ref_details`, `supporting_refs`, `retrieval_context`
- `detour_context` may add `mainline_background` and `detour_trace_summary`

Target payload:

```json
{
  "earlier_excerpts": [],
  "source_ref_details": [],
  "supporting_refs": [],
  "retrieval_context": {},
  "mainline_background": {},
  "detour_trace_summary": []
}
```

Value rules:

- optional; omit when not needed;
- not durable memory;
- not a backdoor for recent reactions, audit dumps, or broad prior-source replay.

### 5. `OutputContract`

`OutputContract` tells Read how to return the result after using the context.

Current source:

- `ATTENTIONAL_V2_PROMPTS.read_unit_system`
- `ATTENTIONAL_V2_PROMPTS.read_unit_prompt` `Return JSON` block
- shared `LANGUAGE_OUTPUT_CONTRACT`
- current read version: `attentional_v2.read.v30`

Target structure:

```xml
<OutputContract>
  <LanguageContract>...</LanguageContract>
  <ReturnFormat>...</ReturnFormat>
  <ReadingImpressionContract>...</ReadingImpressionContract>
  <SurfacedReactionContract>...</SurfacedReactionContract>
  <MemoryUptakeContract>...</MemoryUptakeContract>
  <DetourNeedContract>...</DetourNeedContract>
</OutputContract>
```

#### 5.1 `LanguageContract`

Purpose: define output language.

Current source: shared `LANGUAGE_OUTPUT_CONTRACT` and the current `output_language` value.

Value rule: `output_language` belongs here, not in `BookAndChapterInfo`.

#### 5.2 `ReturnFormat`

Purpose: define the machine-readable result envelope.

Current source: the `Return JSON` block in `ATTENTIONAL_V2_PROMPTS.read_unit_prompt`.

Target top-level fields:

```json
{
  "reading_impression": "...",
  "surfaced_reactions": [],
  "memory_uptake_ops": [],
  "detour_need": null
}
```

#### 5.3 `ReadingImpressionContract`

Purpose: preserve the current `reading_impression` field while it remains in the contract.

Value rule: `reading_impression` is a brief natural impression, not a memory store. It overlaps with Recent Reading Memory and is already marked for future reaction/read-contract cleanup.

#### 5.4 `SurfacedReactionContract`

Purpose: define visible reaction output.

Current source: `surfaced_reactions` examples and source quote rules in `read_unit_system` / `read_unit_prompt`.

Value rule: surfaced reactions must stay anchored to the current unit, and each `source_quote` must be exact text from the current unit.

#### 5.5 `MemoryUptakeContract`

Purpose: define allowed memory operation output.

Current source: `memory_uptake_ops` examples and admission policy.

Value rules:

- durable target stores include `recent_reading_memory`, `concept_registry`, and `thread_trace`;
- `active_attention` still exists in current code, but is deprecated as a primary memory layer and should not be strengthened by this context redesign;
- digests such as `concept_digest` and `thread_digest` are prompt projections, not writable stores.

#### 5.6 `DetourNeedContract`

Purpose: define optional detour request output.

Current source: `detour_need` rules in `read_unit_system` and `Return JSON`.

Value rule: `detour_need` is output routing intent; it is not a memory store and not a self-routed action.

### Pending placement: `Policy snapshot`

Current source: old `read_unit_prompt` receives `policy_snapshot={reader_policy}`.

Current design status:

- `Policy snapshot` is real current input, but it does not yet have an accepted top-level XML block.
- It should not be hidden inside `BookAndChapterInfo` or `ReadingObject`.
- Candidate future placement:
  - a separate `ReadingPolicy` block; or
  - split stable policy into `RoleAndInstruction` and per-call response limits into `OutputContract`.

This document records the gap instead of silently dropping the field. A later design decision should settle the placement before implementation.

## XML Skeleton Example

The following is a readable target shape, not yet an implementation patch:

```xml
<RoleAndInstruction>
  <Role>Read as a continuous reader moving through this book.</Role>
  <ReadBehavior>Use the prompt-visible reading state to understand the current source unit.</ReadBehavior>
  <ReactionInstruction>Surface only bounded current-unit reactions that naturally feel worth marking.</ReactionInstruction>
  <RecentMemoryInstruction>Write useful Recent Reading Memory for your future reading self when the unit establishes something worth carrying.</RecentMemoryInstruction>
  <MemoryOperationInstruction>Use explicit bounded memory operations; prompt digests are projections, not writable stores.</MemoryOperationInstruction>
  <DetourAndRoutingInstruction>Emit detour_need only when needed; do not secretly route by yourself.</DetourAndRoutingInstruction>
</RoleAndInstruction>

<BookAndChapterInfo>
  <BookIdentity>{"book_title": "...", "author": "..."}</BookIdentity>
  <ChapterFrame>{"chapter_title": "...", "chapter_path": "..."}</ChapterFrame>
  <SourceLanguage>...</SourceLanguage>
</BookAndChapterInfo>

<ReadingState>
  <ReadingMemory>
    <NearTermMemory>
      {
        "active_entries": [
          {
            "entry_id": "...",
            "kind": "...",
            "memory_text": "...",
            "source_unit_span_id": "...",
            "created_at_unit_index": 0
          }
        ],
        "active_entry_count": 1
      }
    </NearTermMemory>

    <LongDistanceMemory>
      <ConceptMemory>[]</ConceptMemory>
      <ThreadMemory>[]</ThreadMemory>
      <StructuralMemory>{"chapter_frames": [], "book_frames": [], "durable_definitions": []}</StructuralMemory>
    </LongDistanceMemory>
  </ReadingMemory>
</ReadingState>

<CurrentFocus>
  <ReadingPath>{"mode": "mainline"}</ReadingPath>
  <ReadingPosition>{"chapter_title": "...", "human_position": "...", "source_unit_span_id": "..."}</ReadingPosition>
  <ReadingObject>
    <SourceUnit>
      <Paragraph n="...">...</Paragraph>
    </SourceUnit>
  </ReadingObject>
  <ReadingIntent>{"intent": "read_current_source_unit_in_sequence"}</ReadingIntent>
  <OptionalSourceEvidence>{}</OptionalSourceEvidence>
</CurrentFocus>

<OutputContract>
  <LanguageContract>...</LanguageContract>
  <ReturnFormat>{"fields": ["reading_impression", "surfaced_reactions", "memory_uptake_ops", "detour_need"]}</ReturnFormat>
</OutputContract>
```

Final implementation may adjust exact field names, payload compaction, or omission rules after review.

## Current Non-Decisions

The following are intentionally not decided yet:

- how much `recent_reading_memory` to carry before consolidation;
- how to prioritize Recent Memory vs concept / thread / structural memory;
- whether any local orientation signal remains needed after Recent Memory consolidation;
- how optional source evidence should be expressed inside current focus;
- whether output JSON schema should stay in the prompt body or move into an explicit XML block;
- where `policy_snapshot` should live in the target XML structure;
- whether Navigate should receive a separate outer XML layer contract.

## Design Guardrails

- Do not use XML to hide unclear memory semantics. First define the role of each layer.
- Do not turn the prompt into decorative markup; tags should map to real context roles.
- Do not confuse product-semantic context layers with the provider API split between system and user messages.
- Do not duplicate the same content across layers unless the duplication has a specific role.
- Do not let deprecated `active_attention` become more permanent just because it receives a tag.
- Do not treat `local_continuity` or recent visible reactions as durable semantic memory.
- Keep inner payloads concise enough that the Read node still focuses on the current source unit.
- Keep prompt changes testable through prompt snapshot / contract tests.

## Relationship To Existing Docs

- `C设计10-Recent Reading Memory Design v0.md` owns the definition, structure, and formation prompt for `recent_reading_memory`.
- This document owns the higher-level question of how Read context should be layered and expressed.
- `docs/backend-reading-mechanisms/attentional_v2.md` remains the stable mechanism doc and should be updated only when the context-layer contract is implemented as stable behavior.

## Future Update Log

Add later accepted discussion decisions here, instead of scattering them across chat:

- accepted: XML-style outer tags and JSON inner payloads;
- accepted: no single `ReadInput` root tag;
- accepted: top-level sibling XML blocks `RoleAndInstruction`, `BookAndChapterInfo`, `ReadingState`, `CurrentFocus`, and `OutputContract`;
- accepted: Read-facing `ReadingObject` should expose the source unit as readable source text / paragraph blocks, not as implementation-shaped `paragraph_slices`;
- accepted: precise source coordinates are program/audit metadata and should not dominate the Read-facing prompt;
- pending: placement of current `policy_snapshot` in the target structure;
- pending: Recent Memory projection policy;
- pending: long-distance memory projection policy;
- pending: local continuity / visible trace boundary;
- implemented infrastructure: fixed prompt fragment resolution and generic XML prompt assembly helper exist, with tests, but are not connected to the live Read prompt;
- pending: prompt migration plan and test plan for connecting the live Read prompt to this assembly layer.
