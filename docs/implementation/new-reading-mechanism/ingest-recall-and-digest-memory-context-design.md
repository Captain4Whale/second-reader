# Ingest Recall And Digest Memory Context Design

Purpose: define the implemented Unit Memory recall/context slice after the bottom hybrid retrieval framework: how Ingest expresses prior-reading recalls, how the Ingest LLM call invokes retrieval through tools, and how runtime-selected Unit Memory enters Digest context.
Use when: designing or implementing bounded multi-recall Ingest output, the `retrieve_unit_memory` tool loop, retrieval aggregation across recalls, runtime-owned memory selection, or Digest retrieved-memory XML context.
Not for: the already-landed Unit Memory ledger / FTS5 / sqlite-vec bottom framework, evaluation claims, or evidence-catalog updates.
Update when: Ingest recall wording, tool schema, recall output schema, retrieval aggregation, memory-selection ownership, retrieved-memory brief shape, or Digest context rules change.

## Status

- Date: `2026-06-02`
- Status: implemented in the current `attentional_v2` live path.
- Implemented live baseline:
  - `DEC-110` implemented the Unit Memory ledger, FTS5 text retrieval, optional sqlite-vec vector retrieval, retrieval mode config, and trace.
  - Ingest now emits bounded `memory_recalls[]` instead of model-facing `memory_query`.
  - The Ingest LLM call can invoke Unit Memory retrieval through an Anthropic-style `retrieve_unit_memory` tool loop.
  - Model-side recalls are contract-validated against the current source text before retrieval execution: recall text must use the current source text's primary language when that language is clear, and model-side `basis` must remain `selected_source_unit`.
  - `retrieve_unit_memory` action-tool preflight uses the same validator and returns `contract_violation` metadata when the action payload violates the recall contract, allowing the final-output repair path to correct the result without exposing retrieved memory back to Ingest.
  - Reading Runner/runtime keeps actual retrieval execution, score fusion, source-unit resolution, artifact writing, result selection, dedupe, budget trimming, and Digest `ReadingMemory` rendering.
  - Ingest does not see, choose, or return retrieved memory brief ids; Ingest only expresses recall intentions and receives compact status/count tool results.
  - Digest now receives one top-level `ReadingMemory` block assembled from hot current-chapter Understanding plus runtime-selected long-distance Unit Memory Understanding.
- Subject-continuity implementation:
  - Digest prompt `attentional_v2.digest.v9` carries subject continuity through prior Understanding in `ReadingMemory`, not by adding raw-source backfill or a new Ingest-side reference-resolution surface.
  - Digest uses current source text plus `ReadingMemory` to establish new subjects, continue known subjects, or explicitly preserve ambiguity inside `understanding`.
- Tool capability note:
  - On `2026-06-02`, a minimal live probe against the configured `MiniMax-M2.7` Anthropic-compatible endpoint succeeded with `tool_use -> tool_result -> final answer`.
  - The probe verifies basic provider support for Anthropic-style tools, not the Reading Companion retrieval tool implementation.
- Evaluation status: no eval run, no evidence-catalog update.

## Design Claim

Ingest should not be prompted as a query generator.

Ingest is the same Reader, at the moment just before careful reading. After choosing the next source unit, it should notice what the selected unit naturally asks the reader to remember from earlier reading.

Runtime can use those recalls as retrieval inputs, but the model-facing act should be reader-shaped:

- not "generate search queries"
- not "summarize prior context"
- but "what should I remember before I read this unit carefully?"

The tool call is an implementation channel, not the product-facing act. Ingest may call `retrieve_unit_memory`, but the prompt should still frame the activity as prior-reading recall in service of continuous reading, not as operating a search interface.

## Scope

This design covers:

- Ingest prompt wording for prior-reading recall
- the Ingest tool loop contract
- multi-recall output shape
- how recalls map to tool inputs and retrieval execution
- how multiple recall result lists should be merged
- how retrieved Unit Memory should be represented to Digest
- prompt/context guardrails for Digest once retrieved memory is injected

This design does not cover:

- changing the Unit Memory ledger entry shape
- changing the FTS5/sqlite-vec storage stack
- adding frontend controls
- running eval
- evidence catalog updates

## Subject Continuity Through Understanding

### Problem

The current source unit may contain pronouns, quoted speech, unclear speakers, or deliberately delayed identities. If Digest writes those references into `understanding` as bare local pronouns, the resulting memory becomes hard to reuse later inside `ReadingMemory` and Unit Memory retrieval.

The solution should not reintroduce raw-source backread through runtime context and should not turn Ingest into a reference-resolution node. Subject continuity should travel through the same channel as the rest of reading continuity: prior Understanding.

### Design Principle

Digest should use the current source unit plus existing `ReadingMemory` to continue, establish, or preserve uncertainty about subjects.

This keeps the mechanism simple and universal:

- no raw prior-source context is injected by runtime
- no new Ingest-side reference-resolution output is added
- no separate entity/coreference schema is introduced
- `ReadingMemory` remains the prompt-facing carrier of prior Understanding
- `understanding` becomes the place where subject continuity, new subject establishment, and unresolved ambiguity are recorded

### Digest Subject-Continuity Rule

When a subject, narrator, speaker, actor, concept, relationship, or point of view is newly established in the current unit, Digest should write that establishment into Understanding.

If current source text uses first-person or second-person language, Digest should use `ReadingMemory` and the current unit to decide whether the subject is already known:

- if the subject is known, write the explicit subject in Understanding
- if the current unit introduces a new subject, establish the subject with a name, role, speaker, group, concept, or relationship description
- if the referent remains genuinely unclear, preserve that ambiguity explicitly instead of guessing

This is not a no-pronoun rule. Pronouns are acceptable when their referent is explicit inside the same Understanding and cannot be misunderstood. The rule is against floating pronouns whose referent would disappear after the Understanding is stored as memory.

Target prompt direction:

```text
# Subject continuity
Use ReadingMemory to understand whether the current source text continues an already established narrator, speaker, actor, concept, relationship, or point of view.

When the current unit establishes a new subject, write that subject explicitly in Understanding. If the identity is not yet fully known, use the clearest source-supported description, such as the first-person narrator, a quoted speaker, a prisoner, Siddhartha's son, a company, a claim, or a relationship.

When a pronoun or demonstrative clearly refers to a known subject from ReadingMemory or from the current unit, write the referent explicitly at its first important mention.

When the referent is genuinely ambiguous, do not guess. Record the ambiguity as part of the Understanding when it matters for continued reading.

Pronouns are acceptable after the referent is clear inside the same Understanding. Avoid floating pronouns that cannot be understood after this Understanding is stored as memory.
```

### Examples

Known subject continued:

```text
ReadingMemory:
P12 U4: The first-person narrator Frankl has arrived at the concentration camp and is describing the first night from his own experience.

Current source:
I did not want to say more about it.

Understanding:
Frankl avoids dwelling on the friend's death and turns toward the psychological experience of arriving at the camp.
```

New subject established:

```text
Current source:
I had never seen the city before.

Understanding:
A first-person narrator begins from an unfamiliar arrival in the city; the narrator's exact identity is not yet established.
```

Ambiguity preserved:

```text
Current source:
He returned before anyone could explain why.

Understanding:
A male figure returns before the cause of his earlier absence is explained; the current memory does not yet make clear which person "he" refers to.
```

Clear local pronoun allowed:

```text
Understanding:
Siddhartha recognizes that father-son suffering is recurring in his own life. This recognition gives Siddhartha hope and makes him want to speak with Vasudeva.
```

Here `This recognition` is acceptable because the referent is explicit in the preceding sentence.

Bad stored Understanding:

```text
He realizes that this is happening again and wants to tell him about it.
```

This is not acceptable because `he`, `this`, `him`, and `it` cannot be recovered once the Understanding is later rendered as memory.

### Ingest Boundary

Ingest should not be given a new raw-source continuity block for reference resolution in this design.

Ingest remains responsible for:

- choosing the next forward source unit
- expressing zero to three prior-reading recalls when the selected unit naturally asks for earlier memory
- invoking `retrieve_unit_memory` when recalls exist

`memory_recalls[]` should still be as standalone as the selected unit allows, but Ingest does not need to solve every pronoun in the source. Retrieval can often operate on concrete names, concepts, events, or pressure words in the selected unit. The final self-contained subject handling belongs to Digest Understanding.

### Runtime Boundary

Runtime should not inject raw preceding source text into Digest as a workaround for pronoun resolution.

Runtime remains responsible for:

- Unit Memory retrieval and selection
- `ReadingMemory` rendering
- post-Digest settlement
- trace / audit persistence

Runtime may later support an audit-only checker for unresolved or floating pronouns in `understanding`, but the first design response should be prompt and example work in Digest rather than a new runtime memory schema.

### Implementation Boundary

Implemented first prompt slice:

1. Digest `Understanding` instruction includes the subject-continuity rule.
2. `OutputContract / UnderstandingField` says `understanding` is stored as ReadingMemory / Unit Memory and must be self-contained enough for later reading.
3. Digest prompt examples include known subject continuation, new subject establishment, and ambiguity preservation.
4. Tests cover:
   - known first-person narrator continued through `ReadingMemory`
   - new first-person narrator established without a known identity
   - ambiguous pronoun preserved rather than guessed
   - clear pronoun inside the same Understanding allowed

This slice does not add raw-source backfill, Ingest reference-resolution fields, or a durable referent store.

## Ingest Prompt Design

### Current Problem

The current live prompt says Ingest should write one memory retrieval query.

That is operationally clear, but it creates two problems:

- It frames Ingest as a retrieval/query generator rather than as the Reader preparing to continue reading.
- One query can collapse multiple distinct recall needs into a single muddy text string.

For example, one selected unit may contain:

- a returning person
- a renewed relationship pressure
- a repeated image
- a concept or claim that earlier units established

Packing all of those into one query weakens both lexical and dense retrieval. It can also cause the model to enumerate nouns instead of expressing actual recall needs.

It also keeps retrieval outside the Ingest LLM call. That was useful for the bottom-framework slice, but the next slice should let Ingest trigger retrieval through a tool while keeping retrieved-memory selection in runtime.

### Target Instruction Block

Replace the previous `RequestMemorySupport` instruction with a reader-facing recall block.

Recommended XML child under `Instruction`:

```xml
<RecallPriorReading>
...
</RecallPriorReading>
```

Target text:

```text
# Purpose

After choosing the next source unit, bring forward prior reading that would help Digest read this unit as part of the book's ongoing movement.

A recall is a focused memory intention: it names the earlier understanding that would make the selected unit more continuous, situated, or meaningful when read now.

The recall should look backward beyond the selected unit. Do not use recall to summarize, rephrase, or search for another sentence inside the selected unit itself.

# When to recall

Write a recall when the selected unit returns to, develops, contrasts with, or depends on something already read: a person, relationship, concept, question, object, image, scene, argument, choice, conflict, method, term, or unresolved pressure.

If the selected unit is purely structural, too thin to benefit from prior memory, or only invites generic background, return an empty list.

# Retrieval-friendly content

Write each `recall_text` as the prior understanding runtime should try to find.

A strong `recall_text` names the relevant subject and the earlier meaning, relation, claim, action, or tension to retrieve.

Use content-grounded wording:
- "悉达多此前对婆罗门教诲、沙门苦行和法义传授产生怀疑，认为教义和修习不能替代亲身探索、求道与觉悟。"
- "乔文达此前一直追随悉达多，把他视为精神上的榜样和同行者。"

# Focus

Let the selected unit decide the recall focus. The recall should support what Digest will need to understand in this unit: its claim, action, conflict, image, relationship, method, term, contrast, or development.

For doctrinal, argumentative, conceptual, or methodological units, recall prior claims, definitions, examples, contrasts, or teaching content.

For person or relationship units, recall earlier choices, conflicts, attachments, obligations, or unresolved tensions that matter to the present unit.

# Writing constraints

Write each `recall_text` in the same primary language as the current source text.

Preserve important names, titles, and technical terms in the form used by the source text when available.

Do not mention paragraph numbers, line numbers, XML ids, CurrentView labels, or phrases like "Paragraph 109" / "段落11".

Do not use outside knowledge about the book, author, later plot, or general literary context. Use only the selected source unit and the already-read continuity implied by the reading so far.

When naming people or speakers, use names that are explicit in the selected unit or unambiguous from already-read continuity. If the subject is unclear, keep the wording neutral instead of inventing a name.

Set each recall `basis` exactly to `selected_source_unit`.

# Number of recalls

Return zero to three recalls.

Prefer one strong focused recall over several weak recalls.

Create separate recalls only when the selected unit contains distinct continuity needs. Do not list every name or noun, and do not split mechanically by entity.

# Tool use

If you write one or more recalls, call the Unit Memory retrieval tool with those recalls so runtime can retrieve, select, and prepare the prior understanding that may support Digest.
```

### Current Step Adjustment

The `CurrentStep` wording should also avoid "query" language.

Target direction:

```text
Your work in this call is to select the next forward source unit that you should read carefully in the Digest step.

After selecting it, briefly name any earlier reading that this unit makes you want to remember before Digest reads it closely.

When those recalls exist, use the available Unit Memory retrieval tool so runtime can prepare prior-reading support before you return the final Ingest JSON.
```

### Context Use Guide Adjustment

The `RetrievalSurface` remains empty in the initial Ingest XML. Retrieved Unit Memory does not enter the model context in V1; the tool result only reports retrieval status, while runtime keeps and renders selected memory later.

Target direction:

```text
- the visible source preview is primary
- book identity is orientation, not source text
- `RetrievalSurface` is intentionally empty here
- prior-reading recall here means describing what should be remembered; runtime performs retrieval only through the provided tool
```

## Ingest Tool Loop

### Principle

The retrieval layer should be exposed to Ingest as a typed tool, not as prompt text and not as direct store access.

The LLM decides whether the selected unit calls for prior-reading recall. Runtime remains responsible for:

- resolving the selected source boundary against the visible preview
- executing FTS5 / sqlite-vec retrieval
- applying retrieval mode fallback and degradation handling
- fusing and aggregating results
- selecting retrieved units after rank aggregation, dedupe, and budget trimming
- writing retrieval traces
- rendering canonical prior Understanding lines into Digest `ReadingMemory`

The model should see only a compact retrieval status/result summary. It must not receive raw retrieval internals, full retrieved memory candidates, selected memory ids, or mutable store handles. It does not choose which retrieved memory enters Digest. Runtime owns that selection because it can apply deterministic ranking, dedupe, current-neighbor suppression, token budgets, and traceable rendering.

### Call Sequence

Recommended first implementation:

```text
Initial Ingest XML prompt
  -> model selects a provisional forward boundary and writes 0-3 recalls
  -> if recalls are empty, model returns final JSON without tool use
  -> if recalls are non-empty, model calls retrieve_unit_memory
  -> runtime resolves the boundary, executes Unit Memory retrieval, selects candidate prior Understanding entries, and returns a compact status summary
  -> model returns final Ingest JSON with boundary fields and recalls only
  -> Reading Runner accepts/governs the boundary and assembles Digest ReadingMemory from runtime-selected prior Understanding entries
```

This keeps one Ingest LLM call conceptually, even if the transport contains multiple Anthropic Messages turns.

### Tool Name

Use a mechanism-private tool:

```text
retrieve_unit_memory
```

Tool description:

```text
Retrieve compact prior Unit Memory briefs that may help the Reader read the selected source unit continuously.
```

### Tool Input

The tool input should include the provisional boundary and the recalls. This lets runtime resolve the selected unit before retrieval, rather than trusting invented source text from the model.

```json
{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "...",
  "memory_recalls": [
    {
      "recall_id": "r1",
      "recall_text": "...",
      "basis": "selected_source_unit"
    }
  ]
}
```

The model should not pass selected source text, previous memory ids, SQL, scores, or store names.

Model-side recall `basis` is fixed to `selected_source_unit`. Runtime fallback recalls may use `runtime_source_text_fallback`, but that is not a model output value.

### Tool Result

The tool result should be compact, status-oriented, and traceable. It should not expose retrieved memory brief content or ids to Ingest, because Ingest no longer chooses memory support:

```json
{
  "status": "ok",
  "effective_mode": "hybrid",
  "boundary_resolution": {
    "status": "matched",
    "source_span_id": "..."
  },
  "retrieval_summary": {
    "recall_count": 1,
    "candidate_unit_count": 24,
    "selected_unit_count": 8,
    "estimated_reading_memory_tokens": 1370
  },
  "degradation_reason": ""
}
```

Allowed statuses:

- `ok`: retrieval ran and runtime selected one or more prior Understanding candidates
- `no_recall`: no recalls were supplied
- `no_match`: retrieval ran but no usable prior-unit candidate remained after filters
- `boundary_unresolved`: runtime could not resolve `end_anchor_text` against the current preview
- `degraded`: retrieval ran with fallback or partial capability, such as lexical-only under `hybrid`
- `error`: runtime tool execution failed in a recoverable way

The tool result should not expose raw scores, RRF internals, embedding distances, SQL, FTS snippets with markup, full previous unit text, prior responses, prior annotation text, prior Understanding text, selected unit ids, or brief ids. Those details stay in runtime trace / audit. The model only needs to know whether retrieval succeeded, degraded, found nothing, or failed.

### Tool Choice And Limits

First implementation defaults:

- allow at most one `retrieve_unit_memory` call per Ingest attempt
- do not allow arbitrary tool names
- if `memory_recalls` is empty, do not call the tool
- if `memory_recalls` is non-empty, force the `retrieve_unit_memory` tool path for that Ingest attempt
- if the model writes one or more recalls but finalizes without a tool call, treat it as a contract bug, not a normal degraded mode
- runtime should repair this by enforcing tool choice, retrying the Ingest/tool turn, or failing the attempt with a clear traceable error; it should not silently continue as if retrieval were optional
- if the tool returns `boundary_unresolved`, runtime should use the existing boundary retry path rather than letting the model perform unbounded repair inside the tool loop
- if the tool returns `degraded` or `error`, Ingest may still return a final boundary result; runtime records the degraded retrieval state in trace / audit rather than asking Ingest to report memory support

## Ingest Output Contract

### Final JSON Shape

Replace:

```json
{
  "memory_query": {
    "query_version": "unit_memory_query.v1",
    "query_text": "...",
    "basis": "selected_source_unit"
  }
}
```

With:

```json
{
  "memory_recalls": [
    {
      "recall_id": "r1",
      "recall_text": "...",
      "basis": "selected_source_unit"
    }
  ]
}
```

Full final output:

```json
{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "...",
  "memory_recalls": [
    {
      "recall_id": "r1",
      "recall_text": "...",
      "basis": "selected_source_unit"
    }
  ]
}
```

The final Ingest JSON should not copy retrieved brief content, selected memory ids, retrieval scores, or memory-support decisions. Runtime owns retrieved candidates, selected prior Understanding entries, and Digest context rendering after boundary governance.

### Empty Recall Output

When nothing in the selected unit calls for earlier reading:

```json
{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "...",
  "memory_recalls": []
}
```

### Field Semantics

- `memory_recalls`
  - zero to three recall descriptions
  - empty list means Ingest intentionally found no prior-reading recall need
- `recall_id`
  - stable local id within this Ingest result
  - recommended values: `r1`, `r2`, `r3`
- `recall_text`
  - reader-facing recall description that runtime can use as retrieval text
  - should combine concrete selected-unit cues with the kind of earlier reading needed
  - should not be a question for Digest to answer
  - should use the same primary language as the current source text
  - should preserve important names, titles, and technical terms in the form used by the source text when available
- `basis`
  - model-side value is exactly `selected_source_unit`

Retrieval status, selected unit ids, selected brief ids, suppression reasons, and budget decisions are runtime trace / audit fields, not Ingest model-output fields.

The same-language and basis rules are enforced as a structured-output contract, not only as prompt advice. If the source is clearly Chinese and the model emits an English recall, or if the model-side basis drifts from `selected_source_unit`, validation treats that as a contract failure and gives the model one repair attempt through the forced final-output tool path. Runtime fallback recalls may still use `runtime_source_text_fallback`, but that value is not a model-side basis.

### Good Recall Examples

```text
the earlier relationship between A and B before this renewed confrontation
```

```text
the previous seaside silence scene that gives this quiet exchange emotional continuity
```

```text
the earlier definition of value judgment that this paragraph now applies to a concrete case
```

### Poor Recall Examples

Too broad:

```text
everything about loneliness and growth in this chapter
```

Too entity-list-like:

```text
A B sea station mother promise
```

Too tool-shaped:

```text
search memory for all references to A
```

Too Digest-shaped:

```text
explain what this paragraph means
```

## Runtime Interaction

### Recalls As Tool Retrieval Inputs

The model-facing shape is `memory_recalls[]`.

For Ingest, each item is a prior-reading recall intention: what the selected unit makes the Reader want to remember before Digest reads carefully.

For runtime, each item becomes a retrieval query. Runtime should use `recall_text` directly as the query text after normal cleaning / clipping.

Do not add a separate `source_cues[]` field in V1. `recall_text` should already combine the selected-unit footing with the kind of earlier reading needed. Splitting out `source_cues[]` would duplicate `recall_text` and push Ingest back toward field-filling search behavior.

During `retrieve_unit_memory` execution, runtime maps each recall to an internal retrieval query:

```json
{
  "query_version": "unit_memory_recall_query.v1",
  "query_text": "<recall_text>",
  "basis": "selected_source_unit",
  "recall_id": "r1"
}
```

The term `query` remains runtime/internal. Prompt wording stays with "recall".

### Empty Recall Semantics

An empty `memory_recalls` list is meaningful.

If Ingest returns `memory_recalls: []`, it should not call `retrieve_unit_memory`. Runtime should skip long-distance Unit Memory retrieval for that cycle rather than manufacturing a fallback query.

If Ingest returns one or more valid recalls, retrieval is mandatory for that attempt. The intended contract is simple: recall need means retrieve; no recall need means do not retrieve.

Fallback should be used only when:

- the recall field is missing or malformed
- a boundary retry/fallback changes the accepted source unit enough that the original recalls/tool result no longer apply
- runtime needs diagnostic continuity for a degraded Ingest response

When fallback is used, it should be recorded as runtime fallback, not as model-authored recall.

### Boundary Retry / Fallback With Tool Loop

The tool input includes `end_anchor_text`, so runtime can resolve the provisional boundary before retrieval.

If the tool receives an unresolvable boundary:

- do not execute memory retrieval for that tool call
- return `boundary_unresolved` with compact resolution evidence
- let Reading Runner use the existing retry path rather than letting the model perform an unbounded repair loop inside tools

If the boundary returned by the final Ingest result cannot be resolved and runtime retries Ingest, use recalls and runtime retrieval results from the accepted retry result only.

If runtime deterministic fallback changes the accepted source unit after Ingest, discard model recalls and either:

- skip retrieved Unit Memory for that cycle, or
- derive one runtime-only fallback retrieval query from the accepted source unit excerpt for diagnostics
- skip retrieval if the fallback source unit is too short or structurally uninformative

Runtime-only fallback retrieval should be recorded as runtime-selected memory support only when it survives the same ranking, dedupe, and budget process as model-authored recalls.

Trace should distinguish:

- `ingest_recall`
- `retry_ingest_recall`
- `tool_retrieve_unit_memory`
- `tool_boundary_unresolved`
- `tool_call_contract_violation`
- `runtime_source_text_fallback`
- `skip_empty_recalls`
- `skip_unusable_fallback`

## Multi-Recall Retrieval Architecture

### Retrieval Execution

Retrieval execution happens inside the `retrieve_unit_memory` tool handler.

For each recall supplied to the tool:

1. Build one internal retrieval query from `recall_text`.
2. Run FTS5 lexical retrieval.
3. If mode is `hybrid`, run query embedding + sqlite-vec KNN when available.
4. Keep per-recall candidate lists.
5. Fuse and aggregate across recall ids.

### Aggregation

The current Unit Memory retriever already aggregates document candidates by unit. Multi-recall retrieval should extend that path.

Recommended flow:

```text
memory_recalls[]
  -> per recall lexical candidates
  -> per recall dense candidates
  -> per recall/channel ranked lists
  -> RRF over (recall_id, channel) lists
  -> unit-level aggregation
  -> recent-neighbor exclusion and dedupe
  -> runtime-selected prior Understanding entries
  -> compact retrieval-status summary for the tool result
  -> runtime-rendered Digest ReadingMemory text
```

### Why Multi-Recall Instead Of One Query

Multiple recalls are useful when the selected unit has distinct recall needs.

They are not useful when they merely enumerate entities. The model should not create one recall per noun, name, or object unless each one asks for a different kind of earlier reading.

### First Budgets

Initial recommendation:

- `max_recalls_per_ingest = 3`
- per recall lexical top-k: lower than current single-query top-k, for example `40`
- per recall dense top-k: lower than current single-query top-k, for example `40`
- aggregate final retrieved units: keep a bounded runtime selection cap, calibrated for broad Understanding coverage
- let runtime select fewer than the retrieval cap, including none, after relevance, dedupe, neighbor exclusion, and token-budget checks
- apply a content-neutral selection-quality gate before final Digest context rendering, so weak broad candidates do not fill long-distance slots merely because budget remains
- skip vector work entirely in `text_only` mode
- cache query embeddings per recall text

These numbers should be treated as calibration defaults, not product-quality claims.

### Trace Additions

`unit_memory_retrieval_trace.jsonl` should record:

- tool call id
- accepted source unit id / span id
- recall count
- per recall:
  - `recall_id`
  - `recall_text`
  - query source
  - lexical candidate count
  - dense candidate count
  - degradation reason
- aggregated selected units
- which recalls matched each selected unit
- runtime-selected unit ids and suppression reasons
- ReadingMemory line count and estimated token usage
- final retrieval mode / effective mode
- latency breakdown
- tool-loop status such as `ok`, `no_recall`, `no_match`, `boundary_unresolved`, `degraded`, `tool_call_contract_violation`, or `error`

## Digest ReadingMemory Context

### Placement

Retrieved Unit Memory should enter Digest as reading memory, not as instruction and not as a separate long-memory structure.

Recommended placement:

```xml
<ReadingMemory>
P42 U18: The earlier unit established ...
P41 U17: The preceding unit clarified ...
P12 U04: Much earlier, the book framed ...
</ReadingMemory>
```

Rationale:

- The prompt-facing substance of both direct recent memory and retrieved long-distance memory is the same: prior Understanding.
- A separate `ReadingState` wrapper is unnecessary while the only prompt-facing state is `ReadingMemory`.
- A separate `RecentMemory` / `RetrievedUnitMemory` split exposes retrieval machinery that Digest does not need.
- `ContextUseGuide` can explain `ReadingMemory` as prior understanding carried into the present read.
- Digest's task remains Understanding / Response / Annotation.
- Reading memory should help continuity without becoming the object of reading.
- Runtime assembles this context from direct recent memory plus runtime-selected long-distance Understanding entries, not from free-form text or selected ids in the final Ingest JSON.

### Prompt-Facing Memory Shape

Each prompt-facing memory item should become one compact text line inside `ReadingMemory`.

Do not wrap every memory item in its own XML tag. The extra tags cost tokens and make the model attend to bookkeeping rather than to the carried understanding.

Candidate text shape:

```text
P42 U18: ...
P41 U17: ...
P12 U04: ...
```

Field guidance:

- position prefix
  - use the shortest readable locator that lets the Reader sense reading order
  - V1 default: `P{paragraph_index} U{unit_index}` when paragraph position is available
  - include a compact chapter prefix only when needed for disambiguation, for example `C2 P42 U18`
  - never expose internal `source_span_id`, retrieval doc ids, SQL row ids, or embedding ids in prompt-facing memory
- memory text
  - use the canonical prior `understanding`
  - keep it as prose, not JSON
  - omit empty Understanding entries
- source / retrieval metadata
  - keep recent-vs-retrieved origin, matched recall ids, matched surfaces, scores, and suppression reasons in runtime trace / audit
  - do not expose them in `ReadingMemory` unless a later review proves the Reader needs a small visible locator

### Budget And Token Estimation

V1 `ReadingMemory` should use two internal budget pools before rendering one prompt-facing block:

- hot chapter memory: up to `5,000` estimated tokens
  - source: already-read Understanding entries from the current chapter
  - no retrieval needed
  - trim nearest-prior first when the current chapter exceeds budget
- long-distance retrieved memory: up to `10,000` estimated tokens
  - source: selected retrieved Understanding entries from prior non-neighbor units
  - selected by runtime after retrieval ranking, dedupe, neighbor exclusion, and budget checks
  - trim to maximize distinct relevant prior units rather than expanding a few entries
  - do not vary this budget by recall count, genre, or apparent question type in V1
- total prompt-facing `ReadingMemory`: up to `15,000` estimated tokens
  - Digest does not see the hot/retrieved distinction
  - runtime keeps the distinction for budget accounting, trace, and review

Use `tiktoken` as the first budget estimator instead of a character-count multiplier.

Recommended estimator:

- estimator id: `tiktoken_o200k_base_v1`
- encoding: `o200k_base`
- fallback encoding: `cl100k_base` only if the installed `tiktoken` package does not expose `o200k_base`
- safety multiplier: start with `1.10` because `tiktoken` is not the MiniMax tokenizer
- fallback when `tiktoken` is unavailable: use a conservative CJK / Latin heuristic only as a degraded runtime path, and record the degradation
- default retention assumption: keep `tiktoken_o200k_base_v1` as the long-running estimator unless implementation or provider-usage review shows a concrete mismatch
- if observed MiniMax input-token usage diverges materially from the estimate, report it as an implementation finding and adjust the multiplier or tokenizer strategy deliberately
- implementation note: `tiktoken` is now an explicit backend dependency for ReadingMemory budget control rather than an incidental environment package

When Digest produces an Understanding, runtime should estimate and store the token cost of the `understanding` text with the Unit Memory / recent-memory entry:

```json
{
  "understanding": {
    "content": "...",
    "token_estimate": {
      "estimator": "tiktoken_o200k_base_v1",
      "tokens": 86,
      "raw_tokens": 78,
      "safety_multiplier": 1.1
    }
  }
}
```

When rendering `ReadingMemory`, runtime should add the position-prefix cost for each line:

```text
line_estimated_tokens =
  stored_understanding_token_estimate
  + estimate_tokens("P42 U18: ")
```

If a stored entry lacks token metadata, estimate it lazily during rendering and record the estimator version in trace. Do not split one Understanding line mid-sentence to fit the budget; omit the whole line once adding it would exceed the relevant pool budget.

Provider usage should calibrate the estimator over time. After each Digest call, compare prompt-side estimates with provider-reported input token usage when available. If `tiktoken` consistently underestimates MiniMax input tokens, raise the safety multiplier before switching estimator strategy. MiniMax's official tokenizer can replace or calibrate `tiktoken` later, but V1 chooses `tiktoken` for speed and implementation simplicity.

### Document-To-ReadingMemory Policy

All retrieval documents may participate in recall, ranking, fusion, and Entry selection, but Digest `ReadingMemory` is Understanding-only.

- `unit_source`
  - participates in lexical / FTS retrieval
  - helps the system find relevant Entries
  - uses an auxiliary lexical weight lower than `unit_understanding`
  - does not enter `ReadingMemory` as prior source text
  - is not embedded for dense vector retrieval in V1
- `unit_understanding`
  - participates in lexical / FTS retrieval
  - is the primary lexical surface for Entry selection
  - is the only surface embedded for dense vector retrieval in V1
  - enters `ReadingMemory` by default for selected Entries when non-empty
  - provides the preferred quality signal for final selection
- `unit_response`
  - participates in lexical / FTS retrieval with lower weight
  - does not enter `ReadingMemory`
  - remains a useful retrieval auxiliary because it may contain questions, aftertaste, or pressure words that help find the right Entry
- `unit_annotation`
  - participates in lexical / FTS retrieval with lower or medium weight
  - does not enter `ReadingMemory`
  - remains a useful retrieval auxiliary because its quote and note can help recall a marked earlier Entry

Do not add a separate annotation-specific threshold. Annotation documents follow the same lexical retrieval / fusion / Entry-selection process as every other retrieval document; the special rule is now simpler: annotation content helps select an Entry, but it is not shown to Digest.

### What Not To Include

Do not expose raw retrieval scores, RRF internals, embedding distances, FTS snippets with markup, or full previous unit text by default.

Do not dump every matched document. Digest should receive compact prior-reading support, not a retrieval audit.

Do not include the raw source text of the previous Unit as a memory line. Source text is useful for finding memories, but Digest continuity should be carried by the remembered Understanding rather than by replaying old source units.

Do not include prior `Response` or prior `Annotation` text in `ReadingMemory`. They are reader-output traces and retrieval auxiliaries; they may be too subjective, may duplicate Understanding, and may bias later reading.

Do not let Ingest rewrite memory text, choose brief ids, or decide memory inclusion for Digest context. Runtime supplies the canonical Understanding text, selects which entries survive retrieval governance, and renders the final `ReadingMemory`.

### Digest Instruction Adjustment

Digest's `ContextUseGuide` should explain `ReadingMemory` softly but clearly:

```text
Let ReadingMemory hold prior understanding that the reading has already carried forward.

Use it for continuity, contrast, callback, and unresolved pressure when it genuinely clarifies the current source unit.

Do not treat ReadingMemory as current source text, prior reader response to imitate, or a reason to force a connection. The current unit remains primary.
```

### Relationship To Direct Recent Memory

Direct recent memory remains the near-neighbor continuity layer internally.

Retrieved Unit Memory is for farther or non-neighbor recall internally. Prompt-facing Digest should not see this source distinction. Runtime should merge both sources into one ordered `ReadingMemory` block and dedupe so Digest does not receive the same prior unit twice.

If runtime selects a retrieved unit and later suppresses it by dedupe, neighbor exclusion, or budget trimming, runtime should record the suppression in trace and omit that Understanding line from `ReadingMemory`.

Recommended ordering:

1. Merge direct recent Understanding entries and selected retrieved Understanding entries.
2. Dedupe by unit id / source span id before rendering.
3. Sort prompt-facing lines by reading position, nearest prior first.
4. Use retrieval score for selection, not for final prompt order.
5. Put `ReadingMemory` before `CurrentFocus` in the Digest prompt so the current unit still appears after the carried memory and remains the immediate object of reading.

The current unit remains the object of reading regardless of context ordering.

## Retrieval Result Packaging

### Unit-Level Runtime Briefs, Not Doc-Level Bundles

Runtime should aggregate retrieval results into unit-level memory briefs internally. Digest should receive the runtime-selected briefs rendered as simple `ReadingMemory` text lines. The Ingest tool result should report retrieval status and counts, not expose the briefs themselves.

Retrieval docs are internal matching surfaces. If source, understanding, response, and annotation documents from the same prior unit all match, runtime should aggregate them into one prior unit brief and Digest should see one `ReadingMemory` line containing that unit's Understanding, not four separate doc blocks and not a richer multi-field bundle.

The selection goal is to maximize useful continuity under a small context budget:

- cover as much relevant reading span as possible
- include more distinct Entries rather than enriching a few Entries
- avoid repeating the same remembered content across briefs
- prefer compact Understanding briefs over raw source text or subjective prior responses
- allow no long-distance retrieved line when the available candidates are too weak; not filling the budget is better than injecting broad continuity noise

### Selection Within A Unit

For each selected unit:

- include only its non-empty Understanding
- use response/source/annotation matches to help select the Entry, not to add more content to the `ReadingMemory` line
- do not include raw prior unit source text, even when `unit_source` helped retrieve the Entry
- do not include prior Response or Annotation text, even when those surfaces helped retrieve the Entry

### Dedupe And Suppression

Suppress:

- current unit
- recent-neighbor units already carried by direct recent memory
- duplicate units across recalls
- Entries with only weak response / annotation matches and no credible source or understanding support
- repeated brief content that says the same thing as another selected brief with weaker coverage value

## Resolved Implementation Decisions

- Tool use is conditional but deterministic: if there are valid recalls, retrieval is required; if there are no recalls, retrieval is skipped.
- A model response that includes recalls but does not call `retrieve_unit_memory` is a contract bug to fix through tool-choice enforcement, retry, or explicit failure, not a designed runtime mode.
- ReadingMemory budgets are fixed in V1: `5,000` estimated tokens for hot current-chapter memory, `10,000` for long-distance retrieved memory, and `15,000` total prompt-facing memory.
- `tiktoken_o200k_base_v1` remains the default estimator unless implementation evidence shows a real mismatch; such mismatch should be reported and handled deliberately.
- Retrieval-effectiveness review is part of the implementation slice. The implementer should design targeted tests / review cases that check recall quality, retrieval coverage, noise suppression, budget behavior, and downstream Digest usefulness.

## Implemented Recommendation

The implemented slice moves the live path from single model-facing `memory_query` to bounded model-facing `memory_recalls[]` plus a mechanism-private `retrieve_unit_memory` tool loop.

Prompt Ingest as a reader noticing what the selected unit asks it to remember, not as a query generator. Allow zero to three recalls. When recalls exist, Ingest calls `retrieve_unit_memory`; runtime resolves the selected boundary, maps each recall to internal retrieval queries, retrieves per recall, fuses across recall/channel lists, aggregates by Unit Memory Entry, dedupes against direct recent memory, selects the prior Understanding entries under budget, and returns only a compact retrieval-status summary to Ingest.

Ingest should not see compact Understanding briefs or return memory-selection fields. For Digest, introduce a top-level `ReadingMemory` block, not `ReadingState`, `RecentMemory`, or `RetrievedUnitMemory`. Runtime should merge direct recent Understanding and runtime-selected retrieved Understanding into simple position-sorted text lines. Raw prior Unit source text, Response, and Annotation remain retrieval surfaces / audit material and should not be replayed into Digest context.

The implementation should enforce the recall/tool boundary rather than treating it as a soft model preference: `memory_recalls[]` is the Reader's recall intention, and runtime retrieval is the required operational consequence of that intention.
