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

Only the expression method is accepted here:

- outer structure should use XML-style tags;
- inner machine values may remain JSON;
- Read context should be organized by semantic role rather than by incidental implementation packet names;
- code should not be changed until the actual Read context layer taxonomy is accepted.

This document does **not** yet settle the final top-level layer names or exact skeleton.

## Open Design Direction Under Discussion

The current working direction from discussion is that Read context should be organized around product-semantic roles, not around the underlying LLM API message split.

The candidate top-level semantic areas under discussion are:

- role / reader instruction;
- book or source metadata;
- reading state, including reading memory;
- current focus, including current path, reading position, reading object, and optional reading intent.

This is not yet an implementation contract. It should be refined before any prompt code changes.

## Current Non-Decisions

The following are intentionally not decided yet:

- exact top-level XML layer names;
- exact nested memory structure;
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
- pending: final layer names;
- pending: exact XML skeleton;
- pending: Recent Memory projection policy;
- pending: long-distance memory projection policy;
- pending: local continuity / visible trace boundary;
- pending: prompt migration plan and test plan.
