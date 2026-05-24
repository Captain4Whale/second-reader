# C设计10 - Recent Reading Memory Design v0

## Status

Status: accepted for first-half implementation; Read-time formation is implemented. Consolidation remains deferred.

This document records the agreed first-half design for `recent_reading_memory`: definition, Read prompt formation, entry structure, status, and pre-consolidation management.

The first-half implementation now adds Read-time formation, append-only state application, runtime persistence, prompt projection, checkpoint / resume carriage, settlement audit visibility, and Memory Quality full-state snapshot inclusion. It does not run eval, update evidence catalog entries, remove `active_attention`, or implement the full long-term consolidation prompt. Consolidation into long-distance memory is intentionally deferred to a later design pass.

## Why This Exists

The project concluded that `active_attention` / ActiveTension should be deprecated and removed after a replacement lands. The missing layer is not another attention/tension tracker. The missing layer is a simple near-term semantic memory that prevents the reader from behaving as if it has forgotten the immediately preceding units.

The product goal is a real co-reader, not only a highlighter. Because the system reads a book unit by unit, each Read step must leave behind enough near-term understanding for future Read steps to continue coherently without rereading all previous source text.

## Core Definition

`Recent Reading Memory` is the reader's near-term semantic memory of just-read units.

It answers this question:

> If the next Read step cannot see the exact previous source text, what should it still carry so it does not read as if it has amnesia?

Recent Reading Memory records what the reader just understood and should keep available for coherent continued reading.

Each entry should be **context-resolvable, not standalone exhaustive**.

That means a future Read step should understand the entry from the memory packet even if it cannot see the exact source unit again. But the entry should not retell all background from scratch. If a person, concept, thread, or situation is already stable in prompt-visible `concept_registry` / `thread_trace` context, the Recent Memory can use that stable name and record only what changed or was newly learned. If something is newly introduced in the current unit, the entry should name or briefly describe it clearly enough for a later Read step to understand.

It is not:

- a copy of the source text;
- a visible reaction;
- Active Attention / ActiveTension;
- a concept or thread target prediction;
- a chapter summary;
- a formal long-term memory store;
- a prediction that something will matter later.

It is simply:

> I just read this unit; what did I understand, and what should I remember as I keep reading?

## Memory Hierarchy

The intended direction is:

```text
current source unit
  -> Read understands the unit
  -> recent_reading_memory records near-term semantic memory
  -> periodic consolidation
  -> concept_registry / thread_trace / reflective_frames
```

Responsibilities:

- `recent_reading_memory` owns near-term per-unit semantic memory.
- `concept_registry` owns stable reusable concepts, definitions, distinctions, and frameworks.
- `thread_trace` owns long-lived tensions, narrative / argumentative arcs, watchpoints, recurring patterns, and unresolved lines that persist beyond near-term continuity.
- `reflective_frames` / chapter summaries own broader chapter- or book-level understanding.
- `active_attention` / ActiveTension is deprecated and should not be expanded to fill this role.

## Formation Prompt

The Read prompt should frame Recent Reading Memory as a reader leaving memory for its future self, not as a mechanical memory-module action.

Agreed prompt wording:

```text
After reading this unit, write what your future reading self should remember from this unit unless the unit is empty or purely structural.

Recent Reading Memory is near-term memory for continuing this book.
Assume the exact source text of this unit may not be shown again in the next Read step.

Focus on the current unit's contribution: what it newly establishes, develops, clarifies, changes, contrasts, withholds, or explicitly frames.

Record source-established content before interpretation:
- what happened;
- who or what appeared;
- what the author claims or explains;
- what distinction, stage, example, condition, or consequence is introduced;
- what changes in a person, situation, argument, relationship, or emotional state;
- what author stance, evidence boundary, writing method, intended reader, or scope limit is declared.

Use the prompt-visible reading context as your carried memory.
Let that context help you understand the current unit as part of the unfolding book, but do not recap prior context for its own sake.
Mention prior context only when it makes the current unit's contribution understandable.

Write the memory so a future Read step can understand it from the memory packet.
If something is already stable in prompt-visible concept/thread context, use its stable name without retelling its whole history.
If something is newly introduced in this unit, name or briefly describe it clearly enough for later reading.

Compress source meaning into clear memory.
Do not copy the whole passage.
Do not write a visible reaction.
Do not predict whether something will matter later.
Do not import outside knowledge.

Do not turn the entry into an essay or theory about the passage.
Once the source-established content is clear, stop.
Do not add a closing label such as "this is a mechanism", "this reveals the essence", "this forms a tension", "this is a system", or "this proves..." unless the source itself explicitly names or frames it that way.

Avoid bare pronouns or vague references such as "he", "this", "that", or "the above situation" unless the referent is explicit in the same entry or stable in prompt-visible concept/thread context.
Keep the memory complete enough for future reading; do not make it artificially short.
```

Granularity wording:

```text
Usually write one Recent Reading Memory entry for this unit.
Split into multiple entries only when the unit contains distinct meanings that a future reader would naturally remember and use separately.
Do not split by sentence or paragraph.
Do not create many small note fragments.
```

Source-boundary wording:

```text
Each Recent Reading Memory entry is grounded in the current read unit as a whole.
You do not need to cite exact sentences.
Only include a short exact source quote if one specific phrase is essential to the memory.
```

The first implementation should not require exact source quotes for Recent Memory. The default provenance is the read unit span.

Operation-reason boundary:

```text
Recent Reading Memory append operations do not need an operation-level reason.
The memory_text is the content to keep; do not spend attention justifying why you wrote it.
```

This is intentional. Recent Reading Memory is the reader's near-term semantic record, not a decision log. The Read node should spend its attention on writing the memory entry itself. If a review report needs to judge whether an entry is good, it should compare `memory_text` against the source unit and surrounding context, not foreground a generated "why I wrote this memory" explanation.

## Deferred Boundary With `reading_impression`

`reading_impression` predates `recent_reading_memory`.

It was introduced by the earlier Read naturalization cutover as the temporary read-after impression for a unit: what the reader immediately understood, noticed, or felt before producing visible reactions and bounded memory ops.

Now that `recent_reading_memory` owns near-term per-unit semantic memory, the two fields partially overlap:

- both can describe what the reader understood from the current unit;
- `reading_impression` is not durable memory, but can read like a mini interpretation paragraph;
- if foregrounded in reports or prompts, it can make Recent Memory look more essay-like than intended.

Current design boundary:

- `recent_reading_memory` remains the durable near-term semantic memory layer.
- `reading_impression` should not be treated as Recent Memory evidence or displayed as a primary field in Recent Memory reviewer reports.
- Do not remove or redesign `reading_impression` inside the Recent Memory formation or consolidation slice.
- Revisit it with the future `surfaced_reactions` / reaction prompt tuning pass, because it sits between immediate reading impression, visible reaction selection, and memory formation.

Future decision:

> During reaction/read-contract tuning, decide whether `reading_impression` should be demoted to debug-only, made optional, or removed from the main Read contract now that `recent_reading_memory` carries the durable near-term understanding.

## Entry Granularity

Default rule:

> Each Read unit usually produces one Recent Memory entry.

Multiple entries are allowed, but should be conservative. Split only when the unit contains distinct meanings that a future reader would naturally remember and use separately.

One Recent Memory entry means:

> one independently carryable near-term semantic memory.

It usually satisfies:

- it can be explained in one or two readable sentences;
- it comes from a coherent semantic block in the current unit;
- it is not merely a sentence-level fragment;
- it can help future reading independently;
- it is not only a decorative subdivision of the same idea.

Split into multiple entries when the unit clearly contains separate memory objects, for example:

- two different people / objects are advanced independently;
- one part records an event while another records an independent argument claim;
- one part completes a local conclusion while another opens a new line;
- a stable concept definition appears alongside a separate narrative or emotional shift;
- the parts would later naturally consolidate into different long-term stores.

Do not split when:

- the unit only gives several details of one event;
- the unit only gives examples for one claim;
- the unit is one continuous emotional or scenic description;
- splitting would create thin note fragments;
- splitting is done only to look structured.

## No `memory_points`

The first version should not include nested `memory_points`.

Reason:

- `Recent Reading Memory` should remain a simple near-term semantic memory, not a mini ontology.
- Nested points would immediately raise extra design questions: point granularity, point linkage, point retrieval, point consolidation, and point scoring.
- If the unit contains multiple independent memories, create multiple entries instead of one entry with nested points.

Therefore:

> A Recent Memory entry is the smallest unit. It is not a point list.

## No Future-target Links At Creation Time

The first version should not include:

- `related_recent_entry_ids`
- `candidate_concept_keys`
- `candidate_thread_keys`

Rationale:

- Recent Memory entries are naturally ordered by reading sequence; explicit recent-to-recent links are not needed at this stage.
- Recent Memory is periodically consolidated after a fixed number of read units; that consolidation pass can naturally merge related entries.
- The direction of memory transformation is from recent memory to long-distance memory.
- That transformation is an active later action. Read should not guess concept/thread targets while forming Recent Memory.
- Concept/thread assignment belongs to the consolidation LLM call, not to the per-unit Read call.

Rule:

> `recent_reading_memory` does not carry links to future concept/thread targets. Consolidation owns that transformation.

## Source Evidence Boundary

The default source evidence for a Recent Memory entry is the read unit.

Required:

- `source_unit_span_id`

Not required by default:

- fine-grained `source_refs`
- exact sentence quotes
- paragraph-char quote matching

Reason:

- Recent Memory is a semantic compression of the current unit as a whole.
- Many entries represent whole-unit understanding rather than one exact sentence.
- Forcing exact quotes can make the model pick a local phrase that falsely appears to support a broader memory.
- The read unit span is enough to audit whether the memory has source support.

Future optional extension:

- A later implementation may add optional `supporting_source_quote` or `supporting_source_refs` only for cases where one specific phrase is essential.
- That should not be part of the first-version core contract.

## Entry Structure

Canonical entry:

```json
{
  "entry_id": "recent:c1:u0007:m1",
  "source_unit_span_id": "unit:c1:p45@0-p48@312",
  "kind": "event_or_situation",
  "memory_text": "本段说明囚徒刚进入集中营后的第一阶段反应：他们先被震惊和恐惧击中，但很快开始意识到人能忍受比想象中更多的痛苦。",
  "status": "active",
  "created_at_unit_index": 7,
  "archived_by_consolidation_id": null
}
```

Read should only need to provide:

```json
{
  "kind": "event_or_situation",
  "memory_text": "本段说明囚徒刚进入集中营后的第一阶段反应：他们先被震惊和恐惧击中，但很快开始意识到人能忍受比想象中更多的痛苦。"
}
```

Program-owned fields:

- `entry_id`
- `source_unit_span_id`
- `created_at_unit_index`
- `status`
- `archived_by_consolidation_id`

## Field Semantics

### `entry_id`

Stable id for one Recent Memory entry.

Suggested shape:

```text
recent:<chapter_id>:u<unit_index>:m<entry_index>
```

Example:

```text
recent:c1:u0007:m1
```

### `source_unit_span_id`

The read unit span that produced the entry.

This is the default provenance boundary. It is enough for first-version audit and review.

### `kind`

Lightweight label for reviewer readability and later consolidation hints.

This is not a complex ontology and should not drive routing.

Suggested first-version values:

- `fact`
- `event_or_situation`
- `claim_or_argument`
- `definition_or_distinction`
- `causal_or_structural_link`
- `character_or_relationship`
- `emotional_or_tonal_shift`
- `image_or_scene`
- `local_pattern_or_thread`
- `other`

### `memory_text`

The core memory.

Requirements:

- readable;
- compressed;
- source-established content first rather than essay-like analysis;
- semantically faithful;
- context-resolvable from the future Read memory packet;
- not standalone exhaustive;
- complete enough for future reading, not artificially shortened;
- clear about newly introduced people, objects, events, claims, and situations;
- allowed to use stable concept/thread names without restating their full history;
- avoids bare pronouns or vague local references unless the referent is explicit in the same entry or stable in prompt-visible concept/thread context;
- useful for continued reading;
- shorter than the source;
- not a visible reaction;
- not a prediction of importance.

Style guardrail:

> Recent Reading Memory should remember what the source content establishes, not convert every unit into an explanatory mini-essay. It should start with the current unit's concrete contribution before interpretation: who / what appeared, what happened, what claim or distinction was made, what example or stage was introduced, what condition or consequence was stated, or what authorial evidence boundary / reader-orientation was declared. Once the source-established content is clear, stop. Do not add a closing label such as "this is a mechanism", "this reveals the essence", "this forms a tension", "this is a system", or "this proves..." unless the source itself explicitly names or frames it that way.

Continuity guardrail:

> Recent Reading Memory should be written by a reader who carries the full prompt-visible reading context, not by a reader seeing an isolated excerpt. However, continuity is an orientation layer, not the output target. The entry should still primarily record what the current unit contributes, and should mention prior context only when that connection clarifies the current unit's meaning.

### `status`

First-version statuses:

```text
active
archived
```

No `resolved`, `closed`, `dropped`, `cooling`, or `answered` statuses are needed for Recent Memory.

### `created_at_unit_index`

The Read unit index that created the entry.

### `archived_by_consolidation_id`

The consolidation pass that archived this entry.

Null while active.

Example after archival:

```json
{
  "entry_id": "recent:c1:u0007:m1",
  "source_unit_span_id": "unit:c1:p45@0-p48@312",
  "kind": "event_or_situation",
  "memory_text": "本段说明囚徒刚进入集中营后的第一阶段反应：他们先被震惊和恐惧击中，但很快开始意识到人能忍受比想象中更多的痛苦。",
  "status": "archived",
  "created_at_unit_index": 7,
  "archived_by_consolidation_id": "recent_consolidation:c1:k001"
}
```

## State Model

Recent Memory has a deliberately small lifecycle:

```text
append -> active -> archived
```

Meaning:

- `active`: still in the near-term window; eligible for Read prompt context.
- `archived`: already processed by a consolidation pass; retained for audit/replay, but not carried into Read prompt.

`archived` is the preferred name because:

- it does not imply the entry was wrong;
- it does not imply it was fully converted into long-term memory;
- it does not imply it should be deleted;
- it clearly means "no longer active prompt context."

## Operations

Before consolidation, Recent Memory should have only one operation:

```text
append
```

Read behavior:

- read current unit;
- produce one or a small number of Recent Memory entries;
- append them to the active Recent Memory list.

Read should not:

- update existing Recent Memory entries;
- merge old entries;
- resolve entries;
- close entries;
- decide concept/thread destinations;
- maintain relationships between recent entries.

After future consolidation:

```text
archive_recent_memory_batch
```

The system marks processed entries as `archived`.

The consolidation pass itself will later decide what content should become:

- `concept_registry`
- `thread_trace`
- `reflective_frames`
- chapter / book-level summaries
- no long-term memory at all

That consolidation design is not part of this document.

## Prompt Context Assembly

Read should carry:

```text
recent_reading_memory entries where status = active
```

Read should not carry:

```text
recent_reading_memory entries where status = archived
```

Because entries are archived after periodic consolidation, the active set should remain bounded.

The first design target is a fixed-count consolidation cadence, for example:

```text
after every 10 Read units, consolidate the active Recent Memory batch
```

The exact value can be configurable in implementation. The important design point is that Recent Memory does not grow indefinitely in prompt context.

## Disk / Artifact Policy

Recent Memory should be soft-archived rather than hard-deleted.

Reason:

- archived entries are useful for audit, replay, debugging, and evaluation;
- they can explain where later concept/thread memories came from;
- text size is expected to be small relative to raw source, eval artifacts, runtime traces, and LLM logs;
- prompt context stays small because only `active` entries are carried.

Soft archive does not mean old state compatibility. It means the local artifact keeps historical reading memory entries for review.

## Examples

### One-entry Unit

If a unit describes a single coherent transition:

```json
{
  "kind": "emotional_or_tonal_shift",
  "memory_text": "这一段把囚徒从初到集中营的震惊推进到情感麻木：痛苦和恐惧仍在，但心理反应开始转为保护性的迟钝。"
}
```

### Multi-entry Unit

If a unit contains two independent meanings:

```json
[
  {
    "kind": "event_or_situation",
    "memory_text": "囚徒在集中营中开始经历第二阶段的情感麻木，许多原本会激起强烈反应的事情逐渐变得迟钝。"
  },
  {
    "kind": "causal_or_structural_link",
    "memory_text": "这种麻木不是简单冷漠，而是一种心理自我保护：人在极端环境中通过降低感受强度来维持生存。"
  }
]
```

This split is acceptable because the first entry records the situation shift, while the second records an explanatory causal interpretation.

### Bad Fragmentation

Avoid:

```json
[
  {"kind": "fact", "memory_text": "囚徒害怕。"},
  {"kind": "fact", "memory_text": "囚徒震惊。"},
  {"kind": "fact", "memory_text": "囚徒麻木。"}
]
```

These are thin fragments of one memory and should be merged.

Better:

```json
{
  "kind": "emotional_or_tonal_shift",
  "memory_text": "囚徒的心理反应从初始恐惧和震惊逐步转向麻木，这种变化显示他们正在适应集中营的极端环境。"
}
```

### Context-resolvable, Not Exhaustive

If `thread_trace` already contains a stable thread such as "囚徒心理反应阶段", avoid retelling the whole prior sequence.

Too exhaustive:

```json
{
  "kind": "local_pattern_or_thread",
  "memory_text": "本书前面已经说明囚徒刚到集中营时先经历震惊，然后适应，接着逐渐情感麻木；这一段继续说明这个过程。"
}
```

Better:

```json
{
  "kind": "emotional_or_tonal_shift",
  "memory_text": "囚徒心理反应阶段线索在本段推进到“情感麻木”：这种麻木被解释为一种保护性迟钝，而不是单纯冷漠。"
}
```

If the referent is newly introduced, make it explicit instead of using a bare pronoun.

Too vague:

```json
{
  "kind": "event_or_situation",
  "memory_text": "他开始意识到这种情况比想象中更严重。"
}
```

Better:

```json
{
  "kind": "event_or_situation",
  "memory_text": "刚进入集中营的新囚徒开始意识到，集中营生活的痛苦和剥夺比他们原先想象得更极端。"
}
```

## Consolidation Boundary

This document only defines the front half:

- formation;
- structure;
- append-only management before consolidation;
- active / archived state.

The future consolidation design must answer:

- what exact prompt reads the active Recent Memory batch;
- how it decides concept vs thread vs reflective destinations;
- how it records lineage from archived Recent Memory to long-distance memory;
- whether it keeps a compact post-consolidation summary;
- how it reports dropped / locally transitional entries;
- how often consolidation runs in product mode vs eval mode.

Do not implement consolidation semantics from this document alone.

## Explicit Non-goals

- No ActiveTension redesign.
- No ActiveTension compatibility tail.
- No recent-to-recent relationship graph.
- No candidate concept/thread links at creation time.
- No nested `memory_points`.
- No default fine-grained `source_refs`.
- No retrieval algorithm.
- No long-term consolidation prompt.
- No eval run, new metric, judge redesign, or evidence catalog update.
- No evidence catalog update.
- No product-quality claim.

## Acceptance Checklist For Future Implementation

The first implementation now satisfies:

- Each Read unit can append one or a small number of Recent Memory entries.
- Read prompt uses the agreed "future self" formation wording.
- Read prompt requires memory text to be context-resolvable, not standalone exhaustive.
- Entry structure contains only the minimal fields listed above.
- Program fills ids, unit span, status, and unit index.
- Read does not update old Recent Memory entries.
- Read does not guess concept/thread targets.
- Only `active` entries are carried into Read prompt context.
- Consolidation can later archive the active batch.
- Archived entries remain available for audit but are not prompt-carried.
- `active_attention` is not expanded as part of this work.
