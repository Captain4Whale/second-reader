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
- the top-level XML blocks are `RoleDefinition`, `SourceContext`, `ReadingState`, `CurrentFocus`, and `OutputContract`;
- `RoleDefinition` and `OutputContract` are prompt structure, not reading input data;
- code should not be changed until the actual Read context layer taxonomy is accepted.

This document now settles the initial readable skeleton, but not the exact field-level projection policy or implementation details.

## Accepted Read Prompt Structure

The Read node prompt should be expressed as several semantically structured XML blocks:

```xml
<RoleDefinition>...</RoleDefinition>
<SourceContext>...</SourceContext>
<ReadingState>...</ReadingState>
<CurrentFocus>...</CurrentFocus>
<OutputContract>...</OutputContract>
```

This structure is product-semantic. It is not a statement about whether the underlying provider call uses `system`, `user`, or any other message role.

### 1. `RoleDefinition`

`RoleDefinition` explains what the Read node is and how it should behave as a reader.

It should include stable behavior such as:

- Read is a continuous reader moving through a book, not a generic summarizer, highlighter, or field-filling worker;
- Read should understand the current source unit in light of the prompt-visible reading state;
- Read should write Recent Reading Memory for the future reader when the unit contains source-established content worth carrying;
- Read should keep source grounding honest and avoid prompt-external book, author, or later-chapter knowledge;
- Read should not treat surfaced reactions, audit traces, or runtime ids as semantic memory;
- Read should focus on understanding the current unit, not on maintaining state for its own sake.

This layer is stable and low-churn. It should not contain the current source unit. It is part of the prompt contract, not part of the reading input data.

### 2. `SourceContext`

`SourceContext` describes the book/source frame for the current Read call.

It should include low-change metadata such as:

- book title;
- author;
- chapter title or chapter path;
- source language / output language when relevant;
- broad source position if it helps reader orientation.

It should not foreground dense machine coordinates. Exact paragraph-char spans, sentence ids, and ref ids are useful for program audit and source anchoring, but they are not semantic substitutes for the source text.

### 3. `ReadingState`

`ReadingState` contains what the reader already carries from prior reading.

It should center on `ReadingMemory`:

- `NearTermMemory`
  - active `recent_reading_memory` entries;
  - near-term semantic memory from just-read units;
  - intended to help the next Read call continue the book without rereading all prior source text.
- `LongDistanceMemory`
  - `ConceptMemory`: durable concepts, definitions, entities, models, or distinctions;
  - `ThreadMemory`: durable arcs, tensions, watchpoints, narrative/argument lines, or cross-passage developments;
  - `StructuralMemory`: chapter / macro / reflective understanding.

This layer should not default-carry:

- deprecated `active_attention`;
- `local_continuity`;
- recent visible reactions;
- audit/debug traces;
- full source-ref history;
- navigation trace data.

If any of those contain content that future Read calls should understand, that content should be represented through Recent Reading Memory, Concept Memory, Thread Memory, Structural Memory, or explicit current-focus evidence.

### 4. `CurrentFocus`

`CurrentFocus` describes what this Read call is currently reading and why.

It should include:

- `ReadingPath`
  - whether the reader is on the mainline path, a detour, a look-back, or another explicitly supported path;
  - any active path state needed to understand why this unit is being read.
- `ReadingPosition`
  - human-readable position such as chapter and paragraph/range orientation;
  - machine spans may appear as audit handles, but should not dominate the layer.
- `ReadingObject`
  - the current source unit text;
  - paragraph slices or source-native structure needed to read the unit.
- `ReadingIntent`
  - optional;
  - used when this read is not simply mainline continuation, for example when a detour or look-back is trying to answer a specific uncertainty.
- `OptionalSourceEvidence`
  - optional;
  - bounded earlier source excerpts, source-ref details, or book-local evidence needed for this current read;
  - belongs here because it serves this current reading path/intention, not because it is durable memory.

### 5. `OutputContract`

`OutputContract` describes what Read must return after reading.

It should include:

- output language contract;
- JSON-only requirement;
- `reading_impression` contract while that field remains in use;
- `surfaced_reactions` contract;
- `memory_uptake_ops` contract;
- Recent Reading Memory append format;
- concept / thread update formats;
- source quote rules;
- `detour_need` contract.

This layer is separate because it is not reading context or reading input data. It tells Read how to return the result after using the preceding context.

## XML Skeleton Example

The following is a readable target shape, not yet an implementation patch:

```xml
<RoleDefinition>
  Read as a continuous reader moving through this book.
  Use the prompt-visible reading state to understand the current source unit.
  Keep source grounding honest.
  Write useful Recent Reading Memory for your future reading self when the unit establishes something worth carrying.
</RoleDefinition>

<SourceContext>
  {
    "book_title": "...",
    "author": "...",
    "chapter_title": "...",
    "source_language": "...",
    "output_language": "..."
  }
</SourceContext>

<ReadingState>
  <ReadingMemory>
    <NearTermMemory>
      {
        "recent_reading_memory": {
          "active_entries": []
        }
      }
    </NearTermMemory>

    <LongDistanceMemory>
      <ConceptMemory>
        {
          "concept_digest": []
        }
      </ConceptMemory>

      <ThreadMemory>
        {
          "thread_digest": []
        }
      </ThreadMemory>

      <StructuralMemory>
        {
          "reflective_digest": {}
        }
      </StructuralMemory>
    </LongDistanceMemory>
  </ReadingMemory>
</ReadingState>

<CurrentFocus>
  <ReadingPath>
    {
      "mode": "mainline"
    }
  </ReadingPath>

  <ReadingPosition>
    {
      "chapter_title": "...",
      "paragraph_range": "...",
      "machine_source_span": {}
    }
  </ReadingPosition>

  <ReadingObject>
    {
      "source_text": "...",
      "paragraph_slices": []
    }
  </ReadingObject>

  <ReadingIntent>
    {
      "intent": "read_current_object_in_sequence"
    }
  </ReadingIntent>

  <OptionalSourceEvidence>
    {}
  </OptionalSourceEvidence>
</CurrentFocus>

<OutputContract>
  {
    "return": "JSON only",
    "fields": [
      "reading_impression",
      "surfaced_reactions",
      "memory_uptake_ops",
      "detour_need"
    ]
  }
</OutputContract>
```

The example keeps JSON inside layers where the values are program-owned. Final implementation may adjust exact field names, payload compaction, or omission rules after review.

## Current Non-Decisions

The following are intentionally not decided yet:

- how much `recent_reading_memory` to carry before consolidation;
- how to prioritize Recent Memory vs concept / thread / structural memory;
- whether any local orientation signal remains needed after Recent Memory consolidation;
- how optional source evidence should be expressed inside current focus;
- whether output JSON schema should stay in the prompt body or move into an explicit XML block;
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
- accepted: top-level sibling XML blocks `RoleDefinition`, `SourceContext`, `ReadingState`, `CurrentFocus`, and `OutputContract`;
- pending: Recent Memory projection policy;
- pending: long-distance memory projection policy;
- pending: local continuity / visible trace boundary;
- pending: prompt migration plan and test plan.
