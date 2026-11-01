# C设计12 - Prompt Assembly Layer Design v0

## Purpose

This document defines the project-owned Prompt Assembly layer for `attentional_v2` and future nearby LLM nodes.

It answers a narrower question than `C设计11`: not whether the Read context should use XML-style outer structure, but **how the project should assemble model-facing prompts from fixed prompt fragments, runtime context projections, node-specific templates, output contracts, and provider transport adapters**.

The design target is simple but not shallow:

- one shared prompt assembly engine;
- separate node-specific assembly specs for Read, Navigate, and later Consolidate / slow-cycle nodes;
- no one-off string concatenation per node;
- no forced reuse of Read's exact context taxonomy by other nodes;
- deterministic, snapshot-testable, auditable output.

## Status

- Status: `draft / design accepted for discussion`.
- Scope now: Prompt Assembly architecture and implementation direction.
- Not yet scope:
  - live Read prompt migration;
  - live Navigate prompt migration;
  - prompt version bump;
  - LLM eval or product-quality claim;
  - external prompt-management service adoption;
  - provider-specific message optimization.

## Current Code Facts

The repo has already moved partway toward this architecture.

Current prompt asset management:

- `src/attentional_v2/prompts/types.py`
  - `PromptDefinition`
  - `PromptRegistry`
  - `AttentionalV2PromptSet` legacy projection
- `src/attentional_v2/prompts/registry.py`
  - `ATTENTIONAL_V2_PROMPT_REGISTRY`
  - `ATTENTIONAL_V2_PROMPTS`
- per-node prompt files:
  - `survey_chapter_zone.py`
  - `navigate_choose_next_unit.py`
  - `read_unit.py`
  - `bridge_resolution.py`
  - `reflective_promotion.py`
  - `reconsolidation.py`
  - `chapter_consolidation.py`

Current template rendering primitives:

- `src/attentional_v2/prompts/assembly.py`
  - `PromptFragment`
  - `PromptFragmentRegistry`
  - `PromptTemplateNode`
  - `render_prompt_template_xml(...)`

Current node-level assembly infrastructure:

- `src/attentional_v2/prompts/assembler.py`
  - `PromptAssemblySpec`
  - `PromptAssemblyResult`
  - `PromptAssembler`

Current Read XML target helpers:

- `render_read_role_and_instruction_xml(...)`
- `render_read_book_info_xml(...)`
- `render_read_current_focus_xml(...)`
- `render_read_reading_state_xml(...)`
- `render_read_output_contract_xml(...)`

Important current limitation:

> The generic Prompt Assembly infrastructure now exists, and Read now has an opt-in XML assembly path behind `READ_UNIT_PROMPT_ASSEMBLY_MODE` / `ATTENTIONAL_V2_READ_PROMPT_ASSEMBLY_MODE=xml`. Default product behavior remains the legacy prompt assembly path. Navigate has not yet been migrated.

## External Reference Pattern

External systems point to a useful separation of concerns:

- LangChain `ChatPromptTemplate` models prompt construction as message templates with variables. It is useful for provider message formatting, but it does not define this project's semantic context layers.
- LangSmith adds prompt versioning, environments, commit tags, access controls, and prompt hub workflows. It is useful later for prompt lifecycle management, not necessary for the local assembly core.
- LlamaIndex treats prompts as templates used at different pipeline operations and supports `RichPromptTemplate` for variable / logic-rich prompt formatting.
- Haystack `PromptBuilder` is a pipeline component placed before a generator; it renders a template with runtime variables and can fail on missing required variables.
- Semantic Kernel treats prompts as function-like assets with templates and input variables.
- PydanticAI distinguishes static instructions, dynamic instructions, and runtime instructions; this is especially relevant to our split between fixed prompt fragments and runtime reading context.

References:

- [LangSmith prompt management](https://docs.langchain.com/langsmith/manage-prompts)
- [LlamaIndex prompts](https://developers.llamaindex.ai/python/framework/module_guides/models/prompts/)
- [Haystack PromptBuilder](https://docs.haystack.deepset.ai/docs/promptbuilder)
- [Semantic Kernel prompt template syntax](https://learn.microsoft.com/en-us/semantic-kernel/concepts/prompts/prompt-template-syntax)
- [PydanticAI agent prompts and instructions](https://pydantic.dev/docs/ai/core-concepts/agent/)

Design takeaway:

> Mature systems separate prompt assets, runtime variables, operation-specific templates, and model invocation. We should follow that separation without importing a large framework that would obscure our domain-specific context contract.

## Decision

Implement one shared Prompt Assembly layer with node-specific specs.

The shared layer owns:

- fixed prompt fragment resolution;
- dynamic value-slot injection;
- XML-safe rendering;
- required fragment / required slot validation;
- deterministic rendered output;
- assembly metadata for tests and audit;
- provider-agnostic model-input construction.

Each LLM node owns:

- its own semantic block taxonomy;
- its own required runtime inputs;
- its own output contract;
- its own dynamic projection policy;
- its own prompt versioning decision.

Therefore:

- Read should use a `ReadPromptAssemblySpec`.
- Navigate should later use a `NavigatePromptAssemblySpec`.
- Consolidate / slow-cycle should later use their own specs.
- These specs may share the same assembly engine but should not be forced into Read's exact XML skeleton.

## Non-decisions

This document does not decide:

- the final live Read XML prompt migration plan;
- the exact Navigate XML taxonomy;
- the Durable Memory projection details;
- whether prompt assets should later move to LangSmith or another remote manager;
- whether provider calls should use one message or multiple messages;
- prompt caching strategy.

## Core Concepts

### 1. Prompt Fragment

A `PromptFragment` is fixed prompt text addressed by a stable internal id.

It is useful for:

- role instructions;
- behavior policies;
- output field contracts;
- source-grounding rules;
- node-specific fixed guidance.

Rules:

- fragment ids are code / audit handles, not model-facing text;
- final prompts must not leak fragment ids or file paths;
- fragments should be small enough to review and reuse, but not split just for aesthetic neatness;
- fragments are not runtime context.

### 2. Prompt Template Node

A `PromptTemplateNode` is a static XML template element.

It can contain exactly one content source:

- `prompt_fragment_ref`;
- `value_slot`;
- `literal_value`;
- `children`.

Rules:

- `element_name` becomes the final XML tag name;
- `prompt_fragment_ref` and `value_slot` are template-layer mechanisms only;
- final model-facing XML contains only XML tags and resolved text;
- runtime values must be escaped so source text cannot break XML structure;
- a node with multiple content sources is invalid.

### 3. Prompt Assembly Spec

A `PromptAssemblySpec` is the missing cross-node object.

It should describe one node's full prompt assembly contract:

```python
PromptAssemblySpec(
    spec_id="attentional_v2.read_unit.xml.v1",
    owner_node="read_unit",
    prompt_version="attentional_v2.read.v30",
    promptset_version="attentional_v2-phase6-v38",
    template_nodes=(...),
    fragment_registry=...,
    required_slots=("book_identity", "recent_memory", "source_unit", ...),
    output_contract="read_unit_xml_json_v1",
)
```

The exact Python shape can be refined during implementation, but the semantic responsibility is stable:

> a spec says what this node's model-facing prompt is made of and which runtime values must be supplied.

### 4. Prompt Assembly Input

The assembler should not pull arbitrary runtime state itself.

Before assembly, node-specific projector code should turn runtime objects into a clean slot map:

```python
slot_values = {
    "book_identity": "{...json...}",
    "recent_memory": "[...json array of memory strings...]",
    "source_unit": "...",
    "reading_intent": "{...json...}",
}
```

This keeps business logic out of the generic assembler.

### 5. Prompt Assembly Result

The assembler should return more than a bare string.

Target shape:

```python
PromptAssemblyResult(
    rendered_text="...",
    spec_id="attentional_v2.read_unit.xml.v1",
    owner_node="read_unit",
    prompt_version="attentional_v2.read.v30",
    promptset_version="attentional_v2-phase6-v38",
    rendered_blocks=("RoleAndInstruction", "BookInfo", ...),
    used_fragment_ids=(...),
    used_slot_names=(...),
)
```

The model receives only `rendered_text` or provider messages. Audit / tests can inspect metadata.

### 6. Transport Adapter

Prompt Assembly should be provider-agnostic.

The semantic assembly result should later be adapted into whatever the gateway expects:

- current `system_prompt` + `user_prompt`;
- one combined text prompt;
- provider chat messages;
- provider-specific cache-friendly static / dynamic split.

Rules:

- provider message roles must not define our semantic prompt structure;
- semantic blocks such as `RoleAndInstruction`, `ReadingState`, and `CurrentFocus` belong to the assembly spec;
- provider role split belongs to the transport adapter.

## Layering

The target architecture has six layers:

1. **Prompt Asset Layer**
   - owns `PromptDefinition`, `PromptFragment`, prompt versions, and prompt registry.

2. **Runtime Projection Layer**
   - turns runtime state into clean slot values.
   - Examples:
     - active Recent Memory -> JSON string array of `memory_text`;
     - current source unit -> paragraph-shaped source text;
     - book metadata -> `{book_title, author}`;
     - detour context -> reading intent.

3. **Assembly Spec Layer**
   - owns node-level XML skeleton and required slots.
   - Read and Navigate use different specs.

4. **Generic Prompt Assembler**
   - validates required fragments and slots;
   - renders deterministic XML text;
   - returns `PromptAssemblyResult`;
   - does not call the LLM.

5. **Transport Adapter**
   - maps semantic rendered prompt into gateway/provider message shape.
   - Keeps provider details outside prompt semantics.

6. **LLM Invocation Gateway**
   - sends model input;
   - records LLM traces;
   - handles retries / failover / health.

## Why One Assembler But Multiple Specs

One assembler is right because:

- fixed-fragment resolution should behave identically everywhere;
- slot validation should behave identically everywhere;
- XML escaping should behave identically everywhere;
- audit metadata should have one shape;
- tests should not duplicate rendering logic per node.

Multiple specs are necessary because:

- Read's job is to read the current unit and produce reading output / recent memory;
- Navigate's job is to choose the next reading move;
- Consolidate's future job is to transform recent memory into durable memory;
- these nodes do not share the same task, current-focus structure, or output contract.

Therefore the target is:

```text
PromptAssembler
  + ReadPromptAssemblySpec
  + NavigatePromptAssemblySpec
  + ConsolidatePromptAssemblySpec
```

not:

```text
ReadPromptAssembler only
```

and not:

```text
one universal Read-shaped XML context for every node
```

## Package / Dependency Decision

Do not introduce a new prompt framework for the core assembly layer right now.

Reasons:

- The backend already depends on `langchain` / `langchain-core`, but LangChain prompt templates mainly solve message template formatting and variable substitution; they do not encode our domain-specific context contract.
- Haystack / Semantic Kernel / LlamaIndex provide useful patterns, but introducing them would add framework concepts around a small deterministic need we already mostly own.
- Our core requirement is stricter than generic templating: final prompt must not leak ref ids, slot names, file paths, model-invisible coordinates, or deprecated context fields.
- Our assembly output must be snapshot-testable against project-specific XML block contracts.

Acceptable future use:

- LangSmith may be useful later for prompt version / environment management.
- LangChain `ChatPromptTemplate` may be useful as a transport-level adapter if the gateway wants message-template objects.

Current default:

> Keep the core Prompt Assembly layer local, small, typed, deterministic, and project-owned.

## Proposed Code Organization

Near-term implementation should stay under `src/attentional_v2/prompts/` because the current work is mechanism-private.

Recommended shape:

```text
src/attentional_v2/prompts/
  types.py
  registry.py
  assembly.py
  assembler.py
  read_unit.py
  navigate_choose_next_unit.py
  ...
```

`assembly.py` should keep low-level primitives:

- `PromptFragment`
- `PromptFragmentRegistry`
- `PromptTemplateNode`
- `render_prompt_template_xml(...)`

`assembler.py` should add node-level assembly:

- `PromptAssemblySpec`
- `PromptAssemblyResult`
- `PromptAssembler`
- validation helpers

Node files should own their specs:

- `read_unit.py`
  - fixed fragments;
  - `READ_PROMPT_ASSEMBLY_SPEC`;
  - Read slot projection helpers, if they are still mechanism-local and simple.
- `navigate_choose_next_unit.py`
  - future Navigate fragments;
  - `NAVIGATE_PROMPT_ASSEMBLY_SPEC`.

If a later mechanism needs the same assembly engine, promote the generic portion to a shared backend prompt package. Do not prematurely move it before another mechanism actually uses it.

## Assembler Responsibilities

The generic assembler should:

- accept one `PromptAssemblySpec`;
- accept a mapping of runtime slot values;
- validate required slots;
- validate referenced fragments;
- render XML using existing `PromptTemplateNode` logic;
- return `PromptAssemblyResult`;
- expose used blocks, fragments, and slots for tests / audit;
- keep final model-facing text free of refs, slots, file paths, and Python names.

The generic assembler should not:

- call the LLM;
- load book/runtime state directly;
- decide what memory is relevant;
- perform retrieval;
- mutate runtime state;
- decide routing;
- know Read-specific or Navigate-specific semantics.

## Read Spec Direction

The Read spec should assemble the already accepted top-level blocks from `C设计11`:

```xml
<RoleAndInstruction>...</RoleAndInstruction>
<BookInfo>...</BookInfo>
<ReadingState>...</ReadingState>
<CurrentFocus>...</CurrentFocus>
<OutputContract>...</OutputContract>
```

The current individual render helpers can become either:

- sub-template helpers inside the Read spec; or
- backward-compatible test helpers that call the shared assembler with partial specs.

The Read assembly spec should not reintroduce:

- `active_attention` / ActiveTension as a target context layer;
- direct durable memory writes from Read;
- `recent reactions` / `local continuity` as default prompt context;
- sentence ids as canonical source coordinates.

## Navigate Spec Direction

Navigate should use the same assembler engine but a different spec.

Likely future top-level blocks:

```xml
<RoleAndInstruction>...</RoleAndInstruction>
<BookInfo>...</BookInfo>
<ReadingState>...</ReadingState>
<NavigationState>...</NavigationState>
<CandidateMoves>...</CandidateMoves>
<OutputContract>...</OutputContract>
```

This is only an orientation sketch. The exact Navigate structure should be designed separately.

Key point:

> Navigate may share `BookInfo` and parts of `ReadingState`, but it should not inherit Read's `CurrentFocus` / `ReadingObject` shape if its job is route choice rather than current-unit reading.

## Validation Requirements

When the shared assembler is implemented, tests should cover:

- missing required slot fails fast;
- missing fragment ref fails fast;
- duplicate spec id or fragment id fails fast;
- rendered prompt contains expected top-level blocks in order;
- rendered prompt does not leak:
  - `prompt_fragment_ref`;
  - `value_slot`;
  - fragment ids;
  - slot names;
  - file paths;
  - Python variable names;
  - `ref=`;
- XML escaping for dynamic source text;
- metadata records used fragments and slots;
- Read live prompt remains unchanged until a separate migration slice;
- Navigate can later define a spec without changing assembler internals.

## Migration Plan

### Step 1 - Design Record

This document.

### Step 2 - Generic Assembler Infrastructure

Add:

- `PromptAssemblySpec`
- `PromptAssemblyResult`
- `PromptAssembler`

Keep it disconnected from live Read / Navigate calls.

Implementation status: completed in `src/attentional_v2/prompts/assembler.py`. The generic assembler validates required slots, delegates XML rendering to the existing template renderer, returns rendered text with assembly metadata, and remains disconnected from live model calls.

### Step 3 - Read Assembly Spec

Fold current Read XML block renderers into one `READ_PROMPT_ASSEMBLY_SPEC` and one renderer:

```python
render_read_prompt_xml(...)
```

Still keep live Read prompt unchanged.

Implementation status: completed as an opt-in path. `render_read_prompt_xml(...)` assembles the accepted Read XML blocks through `PromptAssembler`, and `read_unit` can use it when explicitly switched to `xml`. The default remains `legacy`, so normal model input is unchanged until diagnostic review approves the switch.

### Step 4 - Diagnostic Read XML Path

Add an explicit diagnostic / opt-in path to render and inspect the full XML prompt.

Do not switch product runtime by default.

Implementation status: completed at code level. The switch is:

- module variable: `READ_UNIT_PROMPT_ASSEMBLY_MODE = "legacy" | "xml"`;
- environment override: `ATTENTIONAL_V2_READ_PROMPT_ASSEMBLY_MODE=xml`.

When XML mode is used, prompt manifests include `prompt_assembly` metadata with spec id, rendered blocks, used fragments, and used slots. Direct `recent_reading_memory` model output is converted internally into current runtime recent-memory append operations.

### Step 5 - Navigate Assembly Spec

Design and implement Navigate's spec using the same assembler.

### Step 6 - Live Migration Decision

Only after inspection and small diagnostic runs should the live Read / Navigate prompt paths migrate.

## Open Questions

1. Should the assembled prompt result be stored in `read_audit.jsonl` in full, or only fingerprint + block metadata?
2. Should provider transport split stable instructions and dynamic context for prompt caching?
3. Should `PromptAssemblySpec` live inside `attentional_v2` permanently, or move to shared backend infrastructure after Navigate / Consolidate adoption?
4. Should LangSmith be introduced later for prompt version governance, or is git + tests enough for current development?

These questions do not block the next infrastructure slice.

## Current Recommendation

Implement the next slice as:

> Add a generic prompt assembler under `src/attentional_v2/prompts/assembler.py`, backed by current `PromptTemplateNode` and fragment registry primitives. Keep it disconnected from live model calls. Then use it to define one full Read assembly spec and a later Navigate spec.

This is the smallest useful architecture that is still universal enough for multiple nodes.
