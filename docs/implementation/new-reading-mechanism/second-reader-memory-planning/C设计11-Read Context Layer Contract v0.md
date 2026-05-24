# C设计11 - Read Context Layer Contract v0

## Purpose

This document records the evolving contract for how the `attentional_v2` Read node should receive structured context.

It starts from the current code fact that Read already receives structured data, but that the outer semantic layering is not yet clear enough. The current implementation sends a JSON-heavy `Read context packet`; this is structured for the program, but not yet ideal as a reader-facing context contract for the LLM.

This document is intentionally incremental. It now records the first implemented Read-side direction: **use XML-style outer tags for high-level context layers, while keeping JSON for each layer's internal data payload when JSON is the natural machine-owned structure**.

## Status

- Status: `draft / first Read prompt packaging pass implemented`.
- Scope now: Read context-layer contract and prompt expression design.
- Not yet scope:
  - Navigate context redesign;
  - eval run;
  - Recent Memory consolidation;
  - Active Attention cleanup;
  - evidence catalog update;
  - product-quality claim.

## Starting Problem Statement

Before the first `read.v31` packaging pass, the Read prompt was not unstructured, but its structure was mostly an engineering packet:

- `Structural frame`
- `Current unit`
- `Read context packet`
- `Selective carry`
- `Policy snapshot`

Inside `Read context packet`, multiple conceptually different things are placed side by side:

- local continuity glue;
- deprecated `active_attention`;
- near-term `recent_reading_memory`;
- long-distance `concept_digest`;
- long-distance `thread_digest`;
- reflective frames;
- optional selective carry / detour material.

That was valid JSON, but the LLM could not clearly see the role boundary of each section unless the outer prompt explained those boundaries. In particular, the model needed to know which material is:

- the current reading task;
- near-term memory from just-read units;
- stable long-distance memory;
- local orientation glue;
- optional retrieved evidence;
- runtime policy;
- output schema.

## Decision 1: XML Outer Layers, JSON Inner Payloads

Accepted direction:

> Use XML-style outer tags to mark high-level context layers. Inside each layer, keep JSON payloads when the data is program-owned, structured, and already naturally represented as JSON.

The implemented Read-side pattern is:

```xml
<read_context>
  <role_instruction>
    Stable role, reader stance, memory-formation rules, source-grounding rules, and response schema live in the system prompt.
  </role_instruction>

  <book_context>
    {book title / author / chapter / output language JSON}
  </book_context>

  <reading_state>
    {
      "reading_memory": {
        "near_term_memory": {recent_reading_memory JSON},
        "long_distance_memory": {
          "concept_memory": {concept digest JSON},
          "thread_memory": {thread digest JSON},
          "structural_memory": {reflective / chapter-frame digest JSON}
        }
      }
    }
  </reading_state>

  <current_focus>
    {
      "reading_path": {mainline / detour state},
      "reading_position": {human-readable position plus machine audit handles},
      "reading_object": {current source unit},
      "reading_intent": {ordinary mainline intent or optional book-local evidence}
    }
  </current_focus>

  <runtime_policy>
    {reader policy JSON}
  </runtime_policy>
</read_context>

<output_contract>
  {required JSON output schema / instructions}
</output_contract>
```

This is not yet the final prompt. It is the accepted expression principle for the outer layer.

## Why XML Outside

XML-style tags are useful here because they are:

- **self-describing**: the tag name says what role the block plays;
- **visibly bounded**: the LLM can see where one context role ends and another begins;
- **nestable**: memory can contain near-term and long-distance sublayers without flattening their roles;
- **compatible with JSON payloads**: the program can still emit strict JSON inside a tagged block;
- **less ambiguous than a single large JSON packet** for mixed instruction / task / memory / evidence / output-contract material.

The key point is not XML as decoration. The key point is role isolation: the model should not have to infer from field names alone that `recent_reading_memory` is near-term continuity, `concept_digest` is long-distance structure, `local_continuity` is orientation glue, and `selective_carry` is optional retrieved evidence.

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

## Implemented Read Layer Taxonomy

The current Read prompt packaging uses these layers:

| Layer | Purpose | Likely source |
| --- | --- | --- |
| `role_instruction` | Stable Read role pointer and boundary reminder. | Read system prompt, not duplicated in full. |
| `book_context` | Low-change book / chapter metadata. | Structural frame. |
| `reading_state` | What the reader already carries into this unit. | Memory projection packet. |
| `reading_state.reading_memory.near_term_memory` | Recent semantic memory from just-read units. | `recent_reading_memory.active_entries`. |
| `reading_state.reading_memory.long_distance_memory` | More durable memory and macro structure. | `concept_digest`, `thread_digest`, `reflective_digest`. |
| `current_focus` | The changing object of this Read call. | current path, position, current unit, optional intent/evidence. |
| `runtime_policy` | Runtime bounds and policy knobs. | `reader_policy`. |
| `output_contract` | Required response format and memory operation schema. | JSON output contract instructions. |

The important separation is by responsibility and change frequency:

- stable role / behavior remains in the system prompt and is only pointed to by `role_instruction`;
- low-change book metadata lives in `book_context`;
- carried understanding lives in `reading_state`;
- the high-churn source object, path, position, and optional reading intent live in `current_focus`;
- output schema lives in `output_contract`.

This avoids putting the stable Read role beside the most frequently changing current unit, and it groups near-term and long-distance memory under one common memory parent instead of treating them as unrelated root layers.

The first implemented pass intentionally does **not** carry deprecated `active_attention` state or `local_continuity` into the Read user prompt. If the content matters for future reading, it should be represented through Recent Reading Memory, concept memory, thread memory, structural memory, or explicit current-focus evidence rather than as a separate compatibility/context-glue block.

## Coordinate Display Policy

Read receives exact machine coordinates only as audit / source-anchoring handles. The LLM should read the supplied source text and memory text; it should not treat paragraph-char spans, sentence ids, or ref ids as semantic content.

Current policy:

- show human-readable book / chapter / paragraph position when useful;
- keep machine span ids under `reading_position.machine_source_span` or legacy orientation fields;
- use machine coordinates for source grounding and audit, not as a substitute for the source text;
- do not foreground sentence ids as the canonical coordinate.

## Optional Evidence Boundary

Look-back, detour, active-recall, and sparse source-ref evidence are part of `current_focus.reading_intent`, not a separate memory root. They describe why the current Read call may include optional book-local evidence, and how that evidence should be used for this unit.

They are not durable memory by themselves. If their content should persist, `Read` must write it into Recent Reading Memory, concept memory, or thread memory through normal memory operations.

## Current Read Prompt Content Structure

The Read node prompt now has two levels: stable instructions in the system prompt, and per-call context in the XML-wrapped user prompt.

### System Prompt: Stable Read Contract

The system prompt remains the home for fixed product / mechanism behavior. This pass intentionally does not rewrite those tuned instructions.

It currently contains:

| Content area | Purpose |
| --- | --- |
| Read role and stance | Defines Read as a careful reader moving through the book, not a field-filling extractor. |
| Reading impression rule | Keeps `reading_impression` as a brief natural impression while it remains in the contract. |
| Surfaced reaction rules | Controls visible in-the-moment reactions and source-quote anchoring. |
| Recent Reading Memory formation | Defines near-term memory as source-established, context-resolvable memory for the future reader. |
| Recent Memory style rules | Requires natural memory sentences / short paragraphs, not default small-title-colon entries or forced abstract labels. |
| Memory operation boundaries | Explains writable stores and prevents writing to projection-only digests. |
| Existing ActiveTension text | Still exists in the current prompt contract while `active_attention` cleanup remains a separate future task; this pass does not add deprecated active state to the prompt context. |
| Concept / Thread write examples | Gives canonical `summary`-based payloads for long-distance memory updates. |
| Source grounding rules | Requires exact source quotes and forbids model-invented source coordinates. |
| Detour request rules | Allows `detour_need` when current understanding genuinely needs bounded earlier material. |
| Output-only rule | Requires JSON-only output in the expected schema. |

### User Prompt: Per-call Read Context

The user prompt carries only the concrete context for this call:

| XML block | Content | Notes |
| --- | --- | --- |
| `read_context.role_instruction` | A short pointer back to the system prompt's stable role and output rules. | It does not duplicate the full role prompt. |
| `read_context.book_context` | Book title, author, chapter title, output language. | Low-change metadata. |
| `read_context.reading_state.reading_memory.near_term_memory` | Active `recent_reading_memory` entries. | Near-term memory from just-read units. |
| `read_context.reading_state.reading_memory.long_distance_memory.concept_memory` | Compact concept digest. | Long-distance structured memory. |
| `read_context.reading_state.reading_memory.long_distance_memory.thread_memory` | Compact thread digest. | Long-distance arcs / lines of development. |
| `read_context.reading_state.reading_memory.long_distance_memory.structural_memory` | Compact reflective / chapter-frame digest. | Macro / structural memory. |
| `read_context.current_focus.reading_path` | Mainline / detour mode and active detour need when present. | Current reading route. |
| `read_context.current_focus.reading_position` | Human-readable chapter / paragraph orientation plus machine audit handles. | Coordinates are not semantic content. |
| `read_context.current_focus.reading_object` | The current source unit text and paragraph slices. | The primary material to read now. |
| `read_context.current_focus.reading_intent` | Ordinary mainline intent, or optional book-local evidence when a detour/look-back path supplies it. | Optional evidence belongs to the current focus, not memory. |
| `read_context.runtime_policy` | Reader policy JSON. | Runtime bounds and knobs. |
| `output_contract` | Output language contract and required JSON schema. | Kept visible to preserve response shape. |

### Not Carried By Default

The current Read user prompt does not carry these as context layers:

- deprecated `active_attention` state;
- `local_continuity`;
- recent visible reactions as memory;
- full `reaction_records`;
- full `read_audit` / `settlement_audit`;
- full source-reference history;
- navigation traces or debug ledgers;
- prompt-internal machine ids except where they are needed as audit/source anchoring handles.

If one of these contains meaning that should affect future reading, the preferred path is to write that meaning into Recent Reading Memory, concept memory, thread memory, structural memory, or explicit current-focus evidence.

## Current Non-Decisions

The following are intentionally not decided yet:

- whether any narrow local-orientation signal is still needed after Recent Memory consolidation exists;
- how much `recent_reading_memory` to carry before consolidation;
- how to prioritize `recent_reading_memory` vs `concept_digest` / `thread_digest`;
- whether `reflective_digest` should be renamed in the prompt-facing layer;
- whether the output JSON schema should stay duplicated in the user prompt after the XML `output_contract` pass matures;
- whether Navigate should receive a similar outer XML layer contract.

## Design Guardrails

- Do not use XML to hide unclear memory semantics. First define the role of each layer.
- Do not turn the prompt into a decorative markup document; tags should map to real context roles.
- Do not duplicate the same content across layers unless the duplication has a specific role.
- Do not let deprecated `active_attention` become more permanent just because it receives a tag.
- Do not treat `local_continuity` or recent visible reactions as durable semantic memory.
- Keep inner payloads concise enough that the Read node still focuses on the current unit.
- Keep prompt changes testable through prompt snapshot / contract tests.

## Relationship To Existing Docs

- `C设计10-Recent Reading Memory Design v0.md` owns the definition, structure, and formation prompt for `recent_reading_memory`.
- This document owns the higher-level question of how Read context should be layered and expressed.
- `docs/backend-reading-mechanisms/attentional_v2.md` remains the stable mechanism doc and now records the first implemented Read packaging pass.
- `codex/reports/Read-Context-Assembly-Current-State-Audit v0.md` records the pre-change code fact before this contract's first implementation pass.

## Future Update Log

Add later accepted discussion decisions here, instead of scattering them across chat:

- pending: final layer names;
- accepted / implemented first pass: exact Read XML skeleton;
- pending: Recent Memory projection policy;
- pending: long-distance memory projection policy;
- pending: local continuity / visible trace boundary;
- pending: prompt migration plan and test plan.
