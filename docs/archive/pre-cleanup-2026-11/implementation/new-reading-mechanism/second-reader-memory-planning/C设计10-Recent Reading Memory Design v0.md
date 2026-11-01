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
- `concept_registry` owns stable reusable dictionary-like concepts, definitions, terms, distinctions, models, objects, people, places, organizations, claims, and frameworks.
- `thread_trace` owns long-lived tensions, narrative / argumentative arcs, watchpoints, recurring patterns, and unresolved lines that persist beyond near-term continuity.
- `reflective_frames` / chapter summaries own broader chapter- or book-level understanding.
- `active_attention` / ActiveTension is deprecated and should not be expanded to fill this role.

## Formation Prompt

The Read prompt should frame Recent Reading Memory as a reader leaving memory for its future self, not as a mechanical memory-module action.

Agreed prompt wording:

```text
After reading this unit, write one Recent Reading Memory entry for your future self unless the unit is empty or purely structural.

Assume the exact source text of this unit may not be shown again in the next Read step.
Record what you now understand from this unit that should remain available for coherent continued reading.

Write Recent Reading Memory as source-established content first, not essay-like analysis.

First record what the source directly establishes for future reading:
- what happened;
- who or what appeared;
- what the author claims;
- what distinction, stage, example, condition, or consequence is introduced or stated;
- what writing position, evidence boundary, or reader-orientation is declared.

Add interpretation only when it is needed to preserve source-established meaning.
Do not start from your theory of the passage.
Record what the source establishes, shows, says, names, contrasts, changes, withholds, or explicitly frames.

Compress meaning, not wording.
Do not copy the whole passage.
Do not write a visible reaction.
Do not predict whether something will matter later.
Do not import outside knowledge.
Keep the memory complete enough for future reading; do not make it artificially short.

Before writing Recent Reading Memory, orient yourself with the prompt-visible reading context.
Treat the provided context as what you already carry from the reading so far.
Use that context to understand the current unit as part of the unfolding book.
But write the memory for the current unit itself: record what this unit newly establishes, develops, specifies, contrasts, changes, or makes memorable.
Do not turn the entry into a recap of the context.
Do not force every entry to mention prior memory or framing.
Only mention a connection to prior context when it helps make the current unit's meaning clear.
The entry should answer: "What should my future self remember from this unit, given the reading context I already carried into it?" not "What can I say again about the prior context?"

Write Recent Reading Memory so your future self can understand it from the memory packet, not from the vanished source unit.
Be context-resolvable, not standalone exhaustive.
Write Recent Reading Memory as natural memory sentences or a short paragraph, not as a heading followed by explanation.
Do not default to "<label>: <explanation>" or "<abstract name>: <explanation>" style.
Use a colon only when the source itself names a term, stage, framework, or quoted source term such as `Transfer` / `Selection`.

If a person, concept, thread, or situation is already stable in prompt-visible concept/thread context, use its stable name and only record what changed or was newly learned.
If something is newly introduced in this unit, name or describe it clearly enough for a later Read step to understand.

Capture new events, claims, explanations, facts, changes in a person/situation/argument/relationship/emotional state, definitions, distinctions, causal links, stages, examples, source-explicit tensions, images, source-explicit unresolved lines, author stance, evidence boundaries, reader-orientation notes, or updates to earlier context.

Do not over-explain the hidden mechanism behind the passage.
Do not turn a concrete scene into an abstract theory unless the source itself names or strongly frames it that way.
Prefer source-facing phrasing such as "the text says", "the text shows", "the text names", or "the text contrasts" when useful.
Avoid unsupported analytic upgrades such as "the essence is", "this proves", "this is an operation mechanism", or "the passage actively trains" unless the unit explicitly supports that wording.
Avoid abstract upgrades such as "psychological pressure weapon", "inner subject process", "systemic refusal", or "moral judgment is abandoned" unless the source itself directly establishes that abstraction. Prefer the concrete source memory first.

Author-facing or method-facing units still count as meaningful content. If the unit declares the author's witness position, evidence boundary, writing method, intended reader, or what the book will / will not explain, remember that as source-established content instead of treating it as empty structure.
If the unit mostly elaborates something already known, write the memory as the current best understanding rather than duplicating fragments.

Avoid bare pronouns or vague references such as "he", "this", "that", or "the above situation" unless the referent is explicit in the same entry or stable in prompt-visible concept/thread context.
```

Current prompt direction:

- `read.v29` tried a broader rewrite that told the model to stop after the current unit's contribution was clear, but the retry3 diagnostic made the entries feel too formulaic and did not improve overall quality enough.
- `read.v30` therefore returns to the `read.v28` shape above, with one small additional style constraint: do not default to small-title-colon entries unless the source itself names the term / stage / framework.
- The retry3 report is retained as historical diagnostic evidence, but it is superseded by the `read.v30` direction and should not be used as the next prompt style target.

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

> Recent Reading Memory should remember what the source content establishes, not convert every unit into an explanatory mini-essay or an abstract title. It should start with the current unit's concrete contribution before interpretation: who / what appeared, what happened, what claim or distinction was made, what example or stage was introduced, what condition or consequence was stated, or what authorial evidence boundary / reader-orientation was declared. Write it as natural memory sentences or a short paragraph. Do not default to `<label>: <explanation>` or `<abstract name>: <explanation>`; use a colon only when the source itself names a term, stage, framework, or quoted source term.

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

## Concept Registry Consolidation Design

This section records the accepted first-pass design for the first durable-memory destination produced from Recent Memory: `concept_registry`.

It does **not** reassign Concept formation back to the per-unit Read node. The intended direction remains:

```text
Read unit
  -> recent_reading_memory append
  -> periodic Consolidate pass over active Recent Memory
  -> concept_registry / thread_trace / reflective_frames
  -> archived Recent Memory
```

### Definition

`concept_registry` is the book-local dictionary of stable, reusable concepts.

It answers:

> When a future Read step sees this term, person, object, model, distinction, claim, or recurring idea again, what does it mean in this book, and what has the source established about it so far?

A Concept is not a summary of a unit. It is a named or nameable durable understanding unit that later reading can reuse.

Concepts can include:

- book-specific terms;
- people;
- places;
- organizations;
- important objects;
- source-named models;
- distinctions;
- classifications;
- claims;
- recurring ideas;
- frameworks that the source establishes as reusable.

Concepts should not include:

- every important Recent Memory entry;
- a chapter summary;
- a visible reaction;
- a thread / arc / developing line;
- a one-off local observation;
- a clever abstract label invented only because a passage feels interesting;
- a model-generated theory that the source has not established.

The important design correction from earlier runs is:

> Concept must behave like a dictionary entry, not like a mini-summary or an abstract title.

Older runs showed two failure modes:

- some Read-generated concept payloads used legacy fields such as `statement`, so the stored `summary` became empty;
- later Read-generated concepts with non-empty summaries often became over-abstract labels, such as model-invented names for a local paragraph.

### Formation Owner

Concept creation belongs to the future Consolidate node, not to the per-unit Read node.

Reason:

- Read owns local understanding and Recent Memory formation;
- Consolidate sees a batch of Recent Memory entries and can decide what is stable enough to become durable memory;
- Concept needs deduplication, conservative naming, and cross-entry merging, which are poor fits for a single Read unit.

Therefore, Read should not predict concept or thread targets while forming Recent Memory. The Consolidate pass owns the transformation from Recent Memory to Concept / Thread / Reflective Frame.

### Minimal Maintainable Structure

The first Concept structure should be intentionally small:

```json
{
  "concept_key": "stable_slug",
  "canonical_name": "book-local concept name",
  "aliases": [],
  "concept_type": "term|person|place|organization|model|distinction|claim|object|idea|other",
  "definition": "what this concept means in this book",
  "known_so_far": "currently established information, maintained as one readable paragraph",
  "source_refs": [],
  "provenance": {
    "derived_from_recent_memory_entry_ids": [],
    "created_at_unit_span_id": "...",
    "updated_at_unit_span_id": "..."
  }
}
```

LLM-maintained fields:

- `concept_key`
- `canonical_name`
- `aliases`
- `concept_type`
- `definition`
- `known_so_far`

Program-maintained fields:

- `source_refs`
- `provenance.derived_from_recent_memory_entry_ids`
- `provenance.created_at_unit_span_id`
- `provenance.updated_at_unit_span_id`
- timestamps or consolidation ids, if the implementation adds them later

The LLM may provide source quotes or Recent Memory entry ids as evidence inputs, but the runner / consolidation settlement layer owns final `SourceRef` resolution and provenance wiring.

### Field Meanings

#### `concept_key`

Stable slug used as the storage id.

It should be stable enough for future updates. Prefer a conservative source-facing slug over a clever abstraction.

#### `canonical_name`

The name future readers should see.

Prefer the book's own wording. If the source names the concept, use that name. If the source does not name it, use a plain descriptive name that does not add interpretation.

#### `aliases`

Other names, spellings, original-language forms, translations, abbreviations, or variants for the same concept.

`aliases` is included in the first version because it has high retrieval value and relatively low maintenance cost.

Rules:

- only record aliases that appear in the source, prompt-visible context, or Recent Memory batch;
- do not fill aliases from encyclopedia knowledge;
- empty array is acceptable;
- updates should union and dedupe aliases rather than replace the whole list unless the implementation explicitly needs correction semantics.

#### `concept_type`

Small category label:

```text
term | person | place | organization | model | distinction | claim | object | idea | other
```

This is for routing and display. It should not become a second ontology project.

#### `definition`

What the concept means in this book.

It is not a general encyclopedia definition unless the book itself provides that definition. For people, places, organizations, and objects, `definition` should briefly identify what the entity is in the book's context.

#### `known_so_far`

The current durable dictionary entry body.

It should be one readable paragraph that records the source-established information currently worth carrying. It replaces a more complex `established_facts[]` list for the first version.

Reason:

- a list of facts has value, but it encourages unnecessary field management;
- `known_so_far` is easier to maintain with full update semantics;
- one paragraph is enough for future Read context and later human review.

#### `source_refs`

Program-resolved evidence pointing back to source spans.

The Concept should be source-grounded, but the LLM should not invent coordinates. The implementation should derive refs from Recent Memory provenance and exact source quotes when available.

#### `provenance`

Program-owned audit lineage.

The first version should preserve at least which Recent Memory entries contributed to the Concept and which unit span created or last updated it. This is not prompt-visible by default.

### Excluded First-version Fields

These fields are deliberately not part of the LLM-maintained first version:

- `established_facts[]`
- `boundaries[]`
- `linked_thread_ids`
- complex `status`
- concept-to-concept relationship graph

Rationale:

- `established_facts[]` overlaps with `known_so_far` and invites unnecessary list maintenance.
- `boundaries[]` can be valuable, but many concepts do not need it; forcing it causes filler.
- `linked_thread_ids` should usually be owned by Thread or by a later consolidation/linking pass, not by the Concept formation prompt.
- Complex statuses repeat the earlier over-designed memory-state problem.
- Graph links are useful only after the core dictionary entry is reliable.

### State and Operations

Concept should have a small lifecycle.

First-version state:

```text
active
```

Implementation may keep timestamps, provenance, and audit history, but the prompt-level Concept contract should not ask the LLM to manage rich statuses.

First-version LLM operation:

```text
upsert
```

Meaning:

- create the Concept if it does not exist;
- otherwise rewrite the current durable dictionary entry as the best current version.

`Concept` should use full update semantics, not append semantics.

Reason:

- a dictionary entry should remain immediately readable;
- a future Read step should not reconstruct meaning from a pile of deltas;
- historical deltas belong in audit / provenance, not in the prompt-facing Concept state.

Potential later operations:

- `merge`, if duplicate concepts become a recurring problem;
- program-side `archive`, if a concept is later proven invalid or obsolete.

Do not add these in the first version unless tests show they are needed.

### Consolidate Prompt Contract

The future Consolidate prompt should be simple and conservative.

Draft wording:

```text
You are consolidating recent reading memories into durable book memory.

Build or update the Concept Registry as a dictionary for this book.

A Concept is a stable, reusable named or nameable thing that future reading may refer to:
a term, person, place, organization, model, distinction, claim, object, framework, or recurring idea.

Do not turn every important memory into a concept.
Do not invent elevated abstract labels just because a passage is interesting.
Do not summarize the recent memories.
Only create or update a concept when the recent memories establish something that should be reusable as a dictionary-like entry.

Prefer the book's own name or wording.
If the source names the concept, use that name.
If the source does not name it, create a plain, conservative name that describes the thing without adding interpretation.

For each concept:
- define what it means in this book;
- maintain the current known_so_far as one readable paragraph;
- include aliases only when they appear in the source, prompt-visible context, or Recent Memory batch;
- cite the recent memory entries and source evidence that support it;
- merge with an existing concept when it is the same thing.
```

Output shape:

```json
{
  "concept_registry_ops": [
    {
      "op": "upsert",
      "concept_key": "stable_slug",
      "payload": {
        "canonical_name": "...",
        "aliases": [],
        "concept_type": "term|person|place|organization|model|distinction|claim|object|idea|other",
        "definition": "...",
        "known_so_far": "...",
        "source_quotes": [],
        "derived_from_recent_memory_entry_ids": []
      }
    }
  ]
}
```

The model-facing output does not include `source_refs` coordinates. The program resolves those after the LLM output.

### Examples

Bad Concept behavior:

```json
{
  "concept_key": "asset-behavioral-independence",
  "canonical_name": "资产独立性-盈利能力不依附于经营状态",
  "definition": "优质资产的盈利能力不受所有者主观状态影响。"
}
```

This may be insightful, but it is too much like an abstract title invented from a local paragraph.

Better Concept behavior:

```json
{
  "concept_key": "municipal_bond",
  "canonical_name": "市政债券",
  "aliases": ["municipal bond"],
  "concept_type": "term",
  "definition": "在这段书中，市政债券作为一种不受持有人个人状态影响、仍可按自身机制运转的资产例子出现。",
  "known_so_far": "芒格用“我喝酒，但我的市政债券不喝酒”说明资产本身与持有人行为可以分离；这个例子支持他对资产底层质量和持有人处境之间关系的区分。"
}
```

Another example:

```json
{
  "concept_key": "moslem",
  "canonical_name": "Moslem",
  "aliases": ["Muselmann"],
  "concept_type": "term",
  "definition": "在集中营筛选语境中，指被认为体弱、有病、不能劳动、因此会被优先淘汰的囚徒类别。",
  "known_so_far": "书中用这个词说明筛选逻辑如何把人的生存价值压缩为劳动力价值；它不是普通宗教词，而是集中营内部的死亡筛选标签。"
}
```

### Implementation Boundary

Do not implement Concept consolidation directly from the old Read-path `memory_uptake_ops` design.

Before implementation, update code contracts so new Read runs do not treat `concept_registry` as a normal Read-owned target store. The durable-memory writer should be a future Consolidate node or equivalent slow-cycle pass.

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
