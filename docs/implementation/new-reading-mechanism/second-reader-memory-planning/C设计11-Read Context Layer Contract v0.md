# C设计11 - Read Context Layer Contract v0

## Purpose

This document records the evolving contract for how the `attentional_v2` Read node should receive structured context.

It starts from the current code fact that Read already receives structured data, but that the outer semantic layering is not yet clear enough. The current implementation sends a JSON-heavy prompt packet; this is structured for the program, but not yet ideal as a reader-facing context contract for the LLM.

This document is intentionally incremental. At this point it records the first accepted design decision: **use XML-style outer tags for high-level context layers, while keeping JSON for each layer's internal data payload when JSON is the natural machine-owned structure**.

## Status

- Status: `draft / design-in-progress`.
- Scope now: context-layer contract and prompt expression design.
- Not yet scope:
  - live Read prompt migration;
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
- **nestable**: memory can contain recent and durable sublayers without flattening their roles;
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
- the top-level XML blocks are `RoleAndInstruction`, `BookInfo`, `ReadingState`, `CurrentFocus`, and `OutputContract`;
- `RoleAndInstruction` and `OutputContract` are prompt structure, not reading input data;
- code should not be changed until the actual Read context layer taxonomy is accepted.

This document now settles the initial readable skeleton, but not the exact field-level projection policy or implementation details.

## Accepted Read Prompt Structure

The Read node prompt should be expressed as several semantically structured XML blocks:

```xml
<RoleAndInstruction>...</RoleAndInstruction>
<BookInfo>...</BookInfo>
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
   - Uses a static `PromptTemplateNode` tree, not ad-hoc string concatenation.
   - `element_name` is the XML element name that the model will eventually see.
   - `prompt_fragment_ref` points to a fixed prompt fragment in the prompt library.
   - `value_slot` points to dynamic per-call data supplied by the Read node.
   - `literal_value` is reserved for rare short fixed text.
   - `attributes` is reserved for rare lightweight XML attributes such as `Paragraph n="45"`.
   - `prompt_fragment_ref` / `value_slot` are assembly keys, not text for the model.
   - Program code resolves all refs and slots before the final prompt is sent.
   - A template may therefore look like:

```python
PromptTemplateNode(
    element_name="RoleAndInstruction",
    children=(
        PromptTemplateNode(
            element_name="Role",
            prompt_fragment_ref="attentional_v2.read.role.v30",
        ),
        PromptTemplateNode(
            element_name="ReadBehavior",
            prompt_fragment_ref="attentional_v2.read.behavior.v30",
        ),
    ),
)
```

2. **Final model-facing prompt layer**
   - Must not expose `prompt_fragment_ref`, `value_slot`, XML `ref` attributes, slot names, or fragment ids.
   - Contains the resolved prompt text inside the XML tags.
   - The final prompt sent to the model should therefore look like:

```xml
<RoleAndInstruction>
  <Role>
    You are a careful reader moving through this book.
  </Role>
  <ContextUseGuide>
    ...
  </ContextUseGuide>
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
    Append Recent Reading Memory only; durable consolidation is not a Read responsibility.
  </MemoryOperationInstruction>
  <SourceGroundingInstruction>
    ...
  </SourceGroundingInstruction>
  <DetourAndRoutingInstruction>
    ...
  </DetourAndRoutingInstruction>
</RoleAndInstruction>
```

Rules:

- `prompt_fragment_ref` and `value_slot` are program-side template mechanisms only.
- The model-facing prompt must not include fragment ids, slot names, file paths, Python variable names, or prompt registry handles.
- Fragment ids should be stable enough for tests, audits, and prompt manifests.
- Fragment ids should not encode filesystem paths. The registry can map ids to code, files, or generated prompt fragments internally.
- Current implementation now stores attentional_v2 prompts as per-node `PromptDefinition` objects in `src/attentional_v2/prompts/`, with `ATTENTIONAL_V2_PROMPT_REGISTRY` as the management entrypoint.
- `ATTENTIONAL_V2_PROMPTS` remains as a legacy projection over that registry for existing runtime call sites; new prompt-management work should prefer prompt definitions / registry.
- Current implementation also has a reusable prompt assembly infrastructure: `PromptFragment`, `PromptFragmentRegistry`, `PromptTemplateNode`, and `render_prompt_template_xml(...)`.
- That infrastructure can resolve fixed fragments, inject dynamic value slots, and render sibling / nested XML blocks without leaking template ids into model-facing text.
- It is not yet connected to the live XML Read prompt. `READ_UNIT_PROMPT_VERSION` is unchanged.
- Current implementation has split `read_unit_system` into lossless physical `PromptFragment` sections under `READ_UNIT_ROLE_AND_INSTRUCTION_FRAGMENTS`; the legacy projection still reconstructs the exact same `ATTENTIONAL_V2_PROMPTS.read_unit_system` string for live runtime calls.
- Current implementation now also exposes `READ_ROLE_AND_INSTRUCTION_TEMPLATE`, `READ_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY`, and `render_read_role_and_instruction_xml()` for the accepted target `RoleAndInstruction` XML assembly.
- This target renderer excludes `DurableMemory` and `ActiveTension`, keeps `SourceGrounding` directly under `RoleAndInstruction`, uses target-specific MemoryBoundary text that does not mention concept/thread durable writes, and remains disconnected from live Read prompt assembly.
- The target renderer also includes a short `ContextUseGuide` immediately after `ReaderRole`, so the model knows how to use `BookInfo`, `ReadingState`, `CurrentFocus`, and `OutputContract` without turning every data tag into a separate explanation block.
- Current implementation exposes `READ_BOOK_INFO_TEMPLATE` and `render_read_book_info_xml(...)` for the accepted target `BookInfo` XML assembly. It is dynamic slot injection only and remains disconnected from live Read prompt assembly.
- Current implementation exposes `READ_CURRENT_FOCUS_TEMPLATE` and `render_read_current_focus_xml(...)` for the accepted target `CurrentFocus` XML assembly. It renders `ReadingPath`, `ReadingPosition`, paragraph-shaped `ReadingObject`, and `ReadingIntent`, and remains disconnected from live Read prompt assembly.
- Current implementation exposes `READ_OUTPUT_CONTRACT_TEMPLATE`, `READ_OUTPUT_CONTRACT_FRAGMENT_REGISTRY`, and `render_read_output_contract_xml(...)` for the accepted target `OutputContract` XML assembly. It renders `OutputUseGuide`, dynamic `LanguageContract`, `ReturnFormat`, and `FieldContracts`, and remains disconnected from live Read prompt assembly.

### 1. `RoleAndInstruction`

`RoleAndInstruction` defines what Read is and how it should read. It is fixed prompt instruction, not reading input data.

Current source:

- prompt definition: `ATTENTIONAL_V2_PROMPT_REGISTRY.get("attentional_v2.read_unit")`
- legacy projection: `ATTENTIONAL_V2_PROMPTS.read_unit_system`
- prompt version field: `READ_UNIT_PROMPT_VERSION`
- current value at this design point: `attentional_v2.read.v30`
- promptset field: `ATTENTIONAL_V2_PROMPTSET_VERSION`

Current implementation note: prompts are now managed as per-node definitions, and the live `read_unit.system_prompt` is reconstructed from fixed role / instruction fragments without changing model-facing text.

Current code-side fixed fragment inventory:

1. `read.role_and_stance`
2. `read.reading_impression_policy`
3. `read.surfaced_reaction_policy`
4. `read.reaction_anchor_and_callback_policy`
5. `read.memory_general_policy`
6. `read.recent_reading_memory_policy`
7. `read.durable_memory_policy`
8. `read.active_tension_policy`
9. `read.source_grounding_policy`
10. `read.detour_and_routing_boundary`
11. `read.output_behavior_policy`

This inventory records current code facts. The target XML structure below is the model-facing semantic organization and does **not** need to preserve every current fragment as a future Read responsibility.

Target design decision for this pass:

- `Read` should not be instructed to consolidate or generate durable memory from Recent Reading Memory.
- `recent_reading_memory -> concept_registry / thread_trace / reflective_frames` consolidation should be handled by a later dedicated consolidation node / slow-cycle pass, not by the Read node.
- `active_attention` / ActiveTension is deprecated and should not be included in the new Read `RoleAndInstruction` structure.
- Current fragments `read.durable_memory_policy` and `read.active_tension_policy` are therefore treated as legacy / transitional prompt inventory, not target XML mapping entries.

Future XML assembly should reference only the accepted target fragments under `RoleAndInstruction` rather than copying their text into the XML template. The flat fragment list is the code-side prompt library order; the XML structure below is the model-facing semantic organization.

#### 1.1 `RoleAndInstruction` fragment mapping

| XML template path | `prompt_fragment_ref` | Purpose |
| --- | --- | --- |
| `RoleAndInstruction/ReaderRole` | `read.role_and_stance` | Reader identity, current-unit reading stance, and "not a field-filling task" boundary. |
| `RoleAndInstruction/ContextUseGuide` | `read.context_use_guide` | Lightweight guide for how to treat `BookInfo`, `ReadingState`, `CurrentFocus`, `ReadingObject`, and `OutputContract`. |
| `RoleAndInstruction/ReadingBehavior/ReadingImpression` | `read.reading_impression_policy` | `reading_impression` as natural post-reading impression, not summary or evaluator voice. |
| `RoleAndInstruction/ReadingBehavior/SurfacedReaction/ReactionSelection` | `read.surfaced_reaction_policy` | When to surface a reaction, density, anchor sizing, and swallowed-line / premise-plus-sharpening checks. |
| `RoleAndInstruction/ReadingBehavior/SurfacedReaction/ReactionGroundingAndCallback` | `read.reaction_anchor_and_callback_policy` | Prior callback visible-text boundary, internal-id suppression, and positive / negative examples. |
| `RoleAndInstruction/MemoryInstruction/MemoryBoundary` | `read.memory_general_policy` | General boundary for `memory_uptake_ops`: keep only what should remain available, and do not duplicate surfaced reactions into memory. |
| `RoleAndInstruction/MemoryInstruction/RecentReadingMemory` | `read.recent_reading_memory_policy` | Recent Reading Memory formation, continuity, source-established writing, natural sentences, and no operation-level reason. |
| `RoleAndInstruction/SourceGrounding` | `read.source_grounding_policy` | Exact quote responsibility for LLM output and program-owned SourceRef resolution. |
| `RoleAndInstruction/RouteBoundary` | `read.detour_and_routing_boundary` | Detour emission boundary: Read may emit a need but must not route secretly or name the next route. |
| `RoleAndInstruction/ResponseDiscipline` | `read.output_behavior_policy` | Output discipline such as no broad chapter summary, no prior-material explanation, and JSON-only behavior. |

Current placement note: `SourceGrounding` sits directly under `RoleAndInstruction`, not under `MemoryInstruction`, because exact quote discipline and program-owned SourceRef resolution apply to both visible reaction evidence and memory operation evidence. Before live migration, this fragment should be reviewed so it does not reintroduce deprecated ActiveTension-only wording.

Explicit target exclusions:

- `RoleAndInstruction/MemoryInstruction/DurableMemory` is not part of the target Read XML structure. Durable memory consolidation belongs to a future consolidation node / slow-cycle pass.
- `RoleAndInstruction/MemoryInstruction/ActiveTension` is not part of the target Read XML structure. ActiveTension is deprecated and should not be strengthened by the context redesign.

#### 1.2 Static template expression

`RoleAndInstruction` should be expressed as a static `PromptTemplateNode` tree. The template contains `prompt_fragment_ref` keys, but the model-facing prompt receives only XML elements and resolved text.

```python
READ_ROLE_AND_INSTRUCTION_TEMPLATE = (
    PromptTemplateNode(
        element_name="RoleAndInstruction",
        children=(
            PromptTemplateNode(
                element_name="ReaderRole",
                prompt_fragment_ref="read.role_and_stance",
            ),
            PromptTemplateNode(
                element_name="ContextUseGuide",
                prompt_fragment_ref="read.context_use_guide",
            ),
            PromptTemplateNode(
                element_name="ReadingBehavior",
                children=(
                    PromptTemplateNode(
                        element_name="ReadingImpression",
                        prompt_fragment_ref="read.reading_impression_policy",
                    ),
                    PromptTemplateNode(
                        element_name="SurfacedReaction",
                        children=(
                            PromptTemplateNode(
                                element_name="ReactionSelection",
                                prompt_fragment_ref="read.surfaced_reaction_policy",
                            ),
                            PromptTemplateNode(
                                element_name="ReactionGroundingAndCallback",
                                prompt_fragment_ref="read.reaction_anchor_and_callback_policy",
                            ),
                        ),
                    ),
                ),
            ),
            PromptTemplateNode(
                element_name="MemoryInstruction",
                children=(
                    PromptTemplateNode(
                        element_name="MemoryBoundary",
                        prompt_fragment_ref="read.memory_general_policy",
                    ),
                    PromptTemplateNode(
                        element_name="RecentReadingMemory",
                        prompt_fragment_ref="read.recent_reading_memory_policy",
                    ),
                ),
            ),
            PromptTemplateNode(
                element_name="SourceGrounding",
                prompt_fragment_ref="read.source_grounding_policy",
            ),
            PromptTemplateNode(
                element_name="RouteBoundary",
                prompt_fragment_ref="read.detour_and_routing_boundary",
            ),
            PromptTemplateNode(
                element_name="ResponseDiscipline",
                prompt_fragment_ref="read.output_behavior_policy",
            ),
        ),
    ),
)
```

Rendered model-facing XML must not expose `prompt_fragment_ref`, fragment ids, slot names, or Python variable names. The renderer resolves each fragment into the element body before sending the prompt to the model.

### 2. `BookInfo`

`BookInfo` orients Read inside the stable book identity. It should stay light and should not become a coordinate dump, table-of-contents dump, chapter-position packet, or runtime-state packet.

Current source:

- current old prompt input: `nodes._structural_frame(...)`
- current old fields: `book_title`, `author`, `chapter_title`, `output_language`
- target value source:
  - `book_title` and `author` come from book-level parsed / provisioned metadata (`ProvisionedBook` / canonical `book_document.metadata`).

Design decision: current chapter identity is not stable book metadata. It changes with the current reading call, so it belongs in `CurrentFocus/ReadingPosition`, not in `BookInfo`.

Target structure:

```xml
<BookInfo>
  <BookIdentity>{...}</BookIdentity>
</BookInfo>
```

Current implementation now has a non-live renderer for this target structure:

- template: `READ_BOOK_INFO_TEMPLATE`
- renderer: `render_read_book_info_xml(book_title=..., author=...)`
- live status: not connected to `ATTENTIONAL_V2_PROMPTS.read_unit_prompt`
- prompt version impact: none; `READ_UNIT_PROMPT_VERSION` remains `attentional_v2.read.v30`

The renderer uses `value_slot` injection in the template layer and emits only model-facing XML plus resolved JSON text. It must not expose slot names, Python variable names, prompt refs, file paths, or runtime object names to the model.

#### 2.1 `BookIdentity`

Purpose: identify the book-level frame.

Current value source: `book_title` and `author` ultimately come from parse / provisioning metadata. The current runtime already carries them as `ProvisionedBook.title` and `ProvisionedBook.author` and passes them into `read_unit(...)`.

Target payload:

```json
{
  "book_title": "...",
  "author": "..."
}
```

#### 2.2 Explicit exclusions

- `output_language` currently lives in the old structural frame, but semantically belongs under `OutputContract`.
- `book_language` / source language is parsed book metadata, but it is not needed in this light orientation block for now.
- `chapter_title` belongs under `CurrentFocus/ReadingPosition`, not here.
- `chapter_ref` is a user-facing chapter reference available in current code, but it is not needed unless later review shows `chapter_title` / human-readable position is insufficient.
- `chapter_path`, table-of-contents data, neighboring chapters, and full chapter lists are not included in this first target shape.
- Exact `source_span`, sentence ids, source span ids, and other machine coordinates should not be foregrounded here.

### 3. `ReadingState`

`ReadingState` contains what the reader already carries from prior reading.

Target structure:

```xml
<ReadingState>
  <ReadingMemory>
    <RecentMemory>...</RecentMemory>
    <DurableMemory>
      <ConceptMemory>...</ConceptMemory>
      <ThreadMemory>...</ThreadMemory>
      <StructuralMemory>...</StructuralMemory>
    </DurableMemory>
  </ReadingMemory>
</ReadingState>
```

#### 3.1 `ReadingMemory`

Purpose: group prior-reading memory under one semantic layer.

Value rule: recent and durable memory are both memory; they should not become separate top-level prompt layers.

##### 3.1.1 `RecentMemory`

Purpose: provide active Recent Reading Memory from just-read units.

Naming rule: use `RecentMemory` instead of `NearTermMemory`. The layer carries recently read past units, not a future-near planning horizon, and it should line up with the existing `recent_reading_memory` store name.

Current source:

- `state_projection.build_read_prompt_packet(...).recent_reading_memory`
- derived from `recent_reading_memory.entries[]`
- only entries with `status == "active"` are projected

Target payload:

```json
[
  "..."
]
```

Value rules:

- Read receives only the `memory_text` strings from active Recent Reading Memory entries.
- Runtime / audit / consolidation storage may keep `entry_id`, `kind`, `source_unit_span_id`, `created_at_unit_index`, `status`, and archive fields, but these are not useful for the Read node and should not be rendered into `RecentMemory`.
- `kind` is useful in storage and review, but it is not needed in the Read context because the memory text itself is the semantic content.
- `entry_id`, source span handles, status, and unit indexes are provenance / consolidation / audit fields, not reading context.
- archived / consolidated entries should not be carried here.

##### 3.1.2 `DurableMemory`

Purpose: provide durable memory formed from prior reading.

Value rule: this layer contains concept, thread, and structural memory.

Naming rule: use `DurableMemory` instead of `LongDistanceMemory`. The distinguishing property is that the memory has been consolidated into a stable, reusable layer, not that it is far away in source distance. This also avoids confusion with Long Span / long-distance callback evaluation terminology.

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
- Thread memory is the durable place for recurring tensions, arcs, watchpoints, and unresolved lines after ActiveTension deprecation.
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

`CurrentFocus` describes the immediate reading scene for this Read call: which reading path is active, where the reader is now, what source text should be read, and why this unit is being read.

It is runtime-provided and call-specific. It is not stable book metadata, not carried memory, and not an output contract.

Target structure:

```xml
<CurrentFocus>
  <ReadingPath>...</ReadingPath>
  <ReadingPosition>...</ReadingPosition>
  <ReadingObject>...</ReadingObject>
  <ReadingIntent>...</ReadingIntent>
</CurrentFocus>
```

Current implementation now has a non-live renderer for this target structure:

- template: `READ_CURRENT_FOCUS_TEMPLATE`
- renderer: `render_read_current_focus_xml(chapter_title=..., current_unit_source=..., current_unit_sentences=..., reading_path_mode=..., detour_context=...)`
- live status: not connected to `ATTENTIONAL_V2_PROMPTS.read_unit_prompt`
- prompt version impact: none; `READ_UNIT_PROMPT_VERSION` remains `attentional_v2.read.v30`

The renderer uses runtime-owned values and emits only model-facing XML plus resolved JSON / paragraph text. It must not expose slot names, Python variable names, source span ids, sentence ids, paragraph-char offsets, or implementation packet names to the model.

#### 4.1 `ReadingPath`

Purpose: identify the current reading path.

Current source:

- mainline/detour state from runner-local continuity and `detour_context`
- `state_projection.build_read_prompt_packet(...).selective_carry.active_detour_need` when present
- current renderer input: `reading_path_mode`, with detour fallback from `detour_context.active_detour_need`

Target payload:

```json
{
  "mode": "mainline|detour|look_back"
}
```

Value rules:

- default to `mainline` when no detour/look-back intent is active;
- include detour / look-back state only when this Read call is actually serving that path;
- do not include broad route history, navigation trace, or future route choice here.

#### 4.2 `ReadingPosition`

Purpose: orient the current unit in human-readable reading position.

Current source:

- `chapter_title` currently passed to `read_unit(...)`;
- `current_unit_source.source_span`
- `current_unit_source.source_span_id`
- source paragraph range from `current_unit_source.paragraph_slices[]` when available
- current renderer input: `chapter_title` and `current_unit_source`

Target payload:

```json
{
  "chapter_title": "...",
  "human_position": "..."
}
```

Value rules:

- `chapter_title` lives here, not in `BookInfo`, because it is part of the current reading location;
- prefer human-readable position such as chapter title and paragraph range;
- do not foreground precise paragraph-char spans, sentence ids, or source span ids in the model-facing prompt;
- keep precise spans and ids in runtime / audit artifacts for matching, resume, and review;
- do not ask Read to reason from coordinates when the task is to read the current source unit.

#### 4.3 `ReadingObject`

Purpose: provide the actual current source unit to read.

Current source:

- `current_unit_source.source_text`
- current implementation also passes `current_unit_source.paragraph_slices[]`
- legacy fallback: `current_unit_sentences[]` with `sentence_id`, `text`, and `text_role`
- current renderer input: `current_unit_source`, with `current_unit_sentences` as compatibility fallback

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
- If paragraph numbers are available, use them as light orientation labels; do not make them the semantic center.

Renderer rule:

- when reliable paragraph slices exist, render:

```xml
<ReadingObject>
  <SourceUnit>
    <Paragraph n="45">...</Paragraph>
    <Paragraph n="46">...</Paragraph>
  </SourceUnit>
</ReadingObject>
```

- when paragraph slices are unavailable but `source_text` exists, render that text directly inside `SourceUnit`;
- when only legacy sentence input exists, join sentence text as compatibility source text and do not expose `sentence_id`.

#### 4.4 `ReadingIntent`

Purpose: state why this unit is being read now when the reason is not simple mainline continuation.

Current source:

- default mainline read intent from runner path;
- detour/look-back intent from `detour_context.active_detour_need` or related selective carry.
- current renderer input: `reading_path_mode` and `detour_context.active_detour_need`

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
- if no special intent exists, do not inflate the block with empty policy prose.

#### 4.5 Optional source evidence placement

There is no top-level `OptionalSourceEvidence` child in the current target `CurrentFocus` structure.

Reason:

- for normal mainline reading, optional earlier evidence should usually be absent;
- for detour / look-back reading, earlier source evidence is part of that specific reading purpose, not a default focus layer;
- if needed later, bounded earlier source evidence should be placed under `ReadingIntent` or as a clearly named supplemental source block inside `ReadingObject`, rather than as an always-present empty top-level child.

Possible future shape:

```xml
<ReadingIntent>
  {"intent": "look_back_to_check_prior_evidence", "question_or_uncertainty": "..."}
</ReadingIntent>
<ReadingObject>
  <SourceUnit>...</SourceUnit>
  <SupplementalSourceUnit purpose="look_back_evidence">...</SupplementalSourceUnit>
</ReadingObject>
```

Current non-goal:

- do not route recent reactions, audit dumps, broad source replay, or memory digests into `CurrentFocus` as "optional evidence."

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
  <OutputUseGuide>...</OutputUseGuide>
  <LanguageContract>...</LanguageContract>
  <ReturnFormat>...</ReturnFormat>
  <FieldContracts>
    <ReadingImpressionContract>...</ReadingImpressionContract>
    <SurfacedReactionContract>...</SurfacedReactionContract>
    <RecentReadingMemoryContract>...</RecentReadingMemoryContract>
    <DetourNeedContract>...</DetourNeedContract>
  </FieldContracts>
</OutputContract>
```

Design rule: `OutputContract` should define the machine-readable return shape and language discipline. It should not repeat long reading-role guidance, reaction-selection policy, source-grounding policy, or memory ontology design that already belongs under `RoleAndInstruction`.

Naming rule: when an instruction and an output field refer to the same capability, use the same stable concept name. For example, `RoleAndInstruction/MemoryInstruction/RecentReadingMemory` explains how to form Recent Reading Memory, while `OutputContract/FieldContracts/RecentReadingMemoryContract` defines the exact output field shape.

#### 5.1 `OutputUseGuide`

Purpose: lightly connect output shape to the instructions above without duplicating the instructions.

Target text:

```text
Follow the instructions above when deciding what to produce; use this section for the exact JSON field names and shapes.
```

#### 5.2 `LanguageContract`

Purpose: define output language.

Current source: shared `LANGUAGE_OUTPUT_CONTRACT` and the current `output_language` value.

Value rule: `output_language` belongs here, not in `BookInfo`.

#### 5.3 `ReturnFormat`

Purpose: define the machine-readable result envelope.

Current source: the `Return JSON` block in `ATTENTIONAL_V2_PROMPTS.read_unit_prompt`.

Target contract:

- return JSON only;
- top-level fields remain:

```json
{
  "reading_impression": "...",
  "surfaced_reactions": [],
  "recent_reading_memory": [],
  "detour_need": null
}
```

Value rule: `ReturnFormat` describes the envelope, not every nested field rule. Nested field rules belong under `FieldContracts`.

#### 5.4 `FieldContracts`

Purpose: group the field-level output contracts under one layer so `OutputContract` is not a flat list of unrelated rules.

Target structure:

```xml
<FieldContracts>
  <ReadingImpressionContract>...</ReadingImpressionContract>
  <SurfacedReactionContract>...</SurfacedReactionContract>
  <RecentReadingMemoryContract>...</RecentReadingMemoryContract>
  <DetourNeedContract>...</DetourNeedContract>
</FieldContracts>
```

##### 5.4.1 `ReadingImpressionContract`

Purpose: define the reader's immediate unit-level subjective expression after reading.

Value rules:

- `reading_impression` is the reader's immediate expression after finishing the current unit: tone, felt pressure, atmosphere, affect, or overall impression;
- it is not durable memory and is not Recent Reading Memory;
- it should not be carried into later Read context by default;
- it should not duplicate `surfaced_reactions`: if the expression is tied to a specific source span and worth showing as a visible margin-note-style output, use `surfaced_reactions`;
- it should not duplicate `recent_reading_memory`: if the content should be remembered for coherent continued reading, write it as Recent Reading Memory.

##### 5.4.2 `SurfacedReactionContract`

Purpose: define visible reaction output.

Current source: `surfaced_reactions` examples and source quote rules in `read_unit_system` / `read_unit_prompt`.

Target shape:

```json
{
  "source_quote": "...",
  "content": "...",
  "prior_link": null,
  "outside_link": null,
  "search_intent": null
}
```

Value rule: this block defines the field shape. Detailed reaction-selection and source-quote behavior live under `RoleAndInstruction`.

##### 5.4.3 `RecentReadingMemoryContract`

Purpose: define the direct Recent Reading Memory output produced by Read.

Current source: target design comes from the Recent Reading Memory design; current live runtime still uses `memory_uptake_ops` as a transitional operation-envelope shape.

Value rules:

- target Read contract should output Recent Reading Memory directly, not through a generic memory-operation bus;
- target shape:

```json
{
  "recent_reading_memory": [
    {
    "kind": "event_or_situation|claim_or_argument|definition_or_distinction|causal_or_structural_link|character_or_relationship|emotional_or_tonal_shift|image_or_scene|local_pattern_or_thread|fact|other",
    "memory_text": "..."
    }
  ]
}
```

- current live runtime still accepts `memory_uptake_ops`; when the XML Read prompt becomes live, normalizer / apply code should migrate to the cleaner `recent_reading_memory` output field;
- direct `concept_registry` / `thread_trace` writes are current-runtime transitional behavior, not the target Read context responsibility;
- durable consolidation from Recent Reading Memory into concept / thread / reflective memory belongs to a future dedicated consolidation node / slow-cycle pass;
- `active_attention` still exists in current code, but is deprecated as a primary memory layer and is excluded from the target Read context structure;
- digests such as `concept_digest` and `thread_digest` are prompt projections, not writable stores.

##### 5.4.4 `DetourNeedContract`

Purpose: define optional detour request output.

Current source: `detour_need` rules in `read_unit_system` and `Return JSON`.

Target shape:

```json
{
  "reason": "...",
  "target_hint": "...",
  "status": "open|resolved|abandoned"
}
```

Value rule: `detour_need` is output routing intent; it is not a memory store and not a self-routed action. Normal mainline output should use `null`.

### Pending placement: `Policy snapshot`

Current source: old `read_unit_prompt` receives `policy_snapshot={reader_policy}`.

Current design status:

- `Policy snapshot` is real current input, but it does not yet have an accepted top-level XML block.
- It should not be hidden inside `BookInfo` or `ReadingObject`.
- Candidate future placement:
  - a separate `ReadingPolicy` block; or
  - split stable policy into `RoleAndInstruction` and per-call response limits into `OutputContract`.

This document records the gap instead of silently dropping the field. A later design decision should settle the placement before implementation.

## XML Skeleton Example

The following is a readable target shape, not yet an implementation patch:

```xml
<RoleAndInstruction>
  <Role>Read as a continuous reader moving through this book.</Role>
  <ContextUseGuide>Treat BookInfo as stable book identity, ReadingState as carried understanding, CurrentFocus/ReadingObject as the current source text, and OutputContract as response requirements.</ContextUseGuide>
  <ReadBehavior>Use the prompt-visible reading state to understand the current source unit.</ReadBehavior>
  <ReactionInstruction>Surface only bounded current-unit reactions that naturally feel worth marking.</ReactionInstruction>
  <RecentMemoryInstruction>Write useful Recent Reading Memory for your future reading self when the unit establishes something worth carrying.</RecentMemoryInstruction>
  <MemoryOperationInstruction>Append Recent Reading Memory for the current unit. Do not consolidate durable memory here.</MemoryOperationInstruction>
  <SourceGroundingInstruction>Give exact current-source quotes when evidence is needed; program code resolves source coordinates.</SourceGroundingInstruction>
  <DetourAndRoutingInstruction>Emit detour_need only when needed; do not secretly route by yourself.</DetourAndRoutingInstruction>
</RoleAndInstruction>

<BookInfo>
  <BookIdentity>{"book_title": "...", "author": "..."}</BookIdentity>
</BookInfo>

<ReadingState>
  <ReadingMemory>
    <RecentMemory>
      [
        "..."
      ]
    </RecentMemory>

    <DurableMemory>
      <ConceptMemory>[]</ConceptMemory>
      <ThreadMemory>[]</ThreadMemory>
      <StructuralMemory>{"chapter_frames": [], "book_frames": [], "durable_definitions": []}</StructuralMemory>
    </DurableMemory>
  </ReadingMemory>
</ReadingState>

<CurrentFocus>
  <ReadingPath>{"mode": "mainline"}</ReadingPath>
  <ReadingPosition>{"chapter_title": "...", "human_position": "..."}</ReadingPosition>
  <ReadingObject>
    <SourceUnit>
      <Paragraph n="...">...</Paragraph>
    </SourceUnit>
  </ReadingObject>
  <ReadingIntent>{"intent": "read_current_source_unit_in_sequence"}</ReadingIntent>
</CurrentFocus>

<OutputContract>
  <OutputUseGuide>...</OutputUseGuide>
  <LanguageContract>...</LanguageContract>
  <ReturnFormat>{"fields": ["reading_impression", "surfaced_reactions", "recent_reading_memory", "detour_need"]}</ReturnFormat>
  <FieldContracts>
    <ReadingImpressionContract>...</ReadingImpressionContract>
    <SurfacedReactionContract>...</SurfacedReactionContract>
    <RecentReadingMemoryContract>...</RecentReadingMemoryContract>
    <DetourNeedContract>...</DetourNeedContract>
  </FieldContracts>
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
- accepted: top-level sibling XML blocks `RoleAndInstruction`, `BookInfo`, `ReadingState`, `CurrentFocus`, and `OutputContract`;
- accepted: Read-facing `ReadingObject` should expose the source unit as readable source text / paragraph blocks, not as implementation-shaped `paragraph_slices`;
- accepted: precise source coordinates are program/audit metadata and should not dominate the Read-facing prompt;
- accepted: `BookInfo` stays light: `BookIdentity` uses parsed / provisioned book metadata (`book_title`, `author`) only;
- accepted: current chapter information belongs in `CurrentFocus/ReadingPosition`, not in `BookInfo`;
- accepted: `CurrentFocus` has four target children for now: `ReadingPath`, `ReadingPosition`, `ReadingObject`, and `ReadingIntent`;
- accepted: no default `OptionalSourceEvidence` child under `CurrentFocus`; detour / look-back evidence should be modeled later as a specific reading intent and supplemental reading object if needed;
- accepted: `OutputContract` has three target layers: `LanguageContract`, `ReturnFormat`, and `FieldContracts`;
- accepted: `OutputContract` includes a short `OutputUseGuide` that connects field shapes to the instructions above without duplicating those instructions;
- accepted: `OutputContract/FieldContracts/RecentReadingMemoryContract` should describe target Read memory output as direct `recent_reading_memory` entries; active attention, `memory_uptake_ops`, and direct durable-memory write examples are excluded from the target contract;
- accepted: `RoleAndInstruction` should not include DurableMemory as a Read-owned responsibility; Recent Memory to durable memory consolidation belongs to a future dedicated consolidation node / slow-cycle pass;
- accepted: `RoleAndInstruction` should not include ActiveTension / `active_attention`; that store is deprecated and excluded from the target Read context structure;
- accepted: `SourceGrounding` sits directly under `RoleAndInstruction`, not under `MemoryInstruction`, because it governs both reaction evidence and memory-operation evidence;
- accepted: `RoleAndInstruction` includes a lightweight `ContextUseGuide` immediately after `ReaderRole` to explain how the top-level context blocks should be used;
- accepted: `ReadingState/ReadingMemory/RecentMemory` should render active Recent Reading Memory as a plain string array of `memory_text` values only; ids, kind, source span, unit index, status, and archive fields stay in runtime/audit/consolidation storage, not in Read context;
- pending: placement of current `policy_snapshot` in the target structure;
- pending: durable memory projection policy;
- pending: local continuity / visible trace boundary;
- implemented prompt management: attentional_v2 prompts moved from one large `prompts.py` bundle into per-node `PromptDefinition` files plus `ATTENTIONAL_V2_PROMPT_REGISTRY`; `ATTENTIONAL_V2_PROMPTS` remains a compatibility projection only;
- implemented prompt management: `read_unit.system_prompt` is now a lossless sequence of role / instruction `PromptFragment` sections for future standalone reference, while the live reconstructed prompt text remains unchanged;
- implemented infrastructure: fixed prompt fragment resolution and generic XML prompt assembly helper exist, with tests, but are not connected to the live Read prompt;
- implemented infrastructure: target `RoleAndInstruction` XML assembly exists for the accepted fragment mapping, excludes DurableMemory / ActiveTension, keeps MemoryBoundary Recent-Memory-only, and is not connected to the live Read prompt;
- implemented infrastructure: target `BookInfo` XML assembly exists for `BookIdentity` (`book_title`, `author`) and is not connected to the live Read prompt;
- implemented infrastructure: target `CurrentFocus` XML assembly exists for runtime-provided reading path, reading position, paragraph-shaped reading object, and reading intent, and is not connected to the live Read prompt;
- implemented infrastructure: target `OutputContract` XML assembly exists for `OutputUseGuide`, dynamic `LanguageContract`, target `ReturnFormat`, and field contracts for `reading_impression`, `surfaced_reactions`, `recent_reading_memory`, and `detour_need`; it is not connected to the live Read prompt;
- implemented infrastructure: target `ReadingState` XML assembly exists for the accepted `RecentMemory` subset and renders only active recent-memory text strings; `DurableMemory` assembly remains pending and is not connected to the live Read prompt;
- pending: prompt migration plan and test plan for connecting the live Read prompt to this assembly layer.
