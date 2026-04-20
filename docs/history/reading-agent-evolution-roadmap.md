# Reading Agent Evolution Roadmap

Purpose: summarize the major structural turns in the reading agent's mechanism and evaluation design so future contributors can understand why the project moved from `iterator_v1` to `attentional_v2`, and why the benchmark stack changed with it.
Use when: explaining the project's mechanism history, onboarding someone to the reader's evolution, or checking how mechanism redesign and benchmark redesign influenced each other.
Not for: source-of-truth current behavior, commit-by-commit change logs, or one-off run interpretation.
Update when: a later mechanism turn changes the overall historical picture enough that this roadmap would otherwise become misleading.

This document is historical synthesis, not current authority. Current behavior still belongs in the stable mechanism and evaluation docs.

## Through-Line

The reading agent did not evolve by chasing novelty. It evolved because the project kept running into the same deeper question:

- what is the real unit of reading?

`iterator_v1` answered that question with:

- parse the book first
- derive semantic `section`s before reading
- then read inside those pre-cut containers

That architecture was workable and often useful, but it gradually exposed a conceptual contradiction:

- the mechanism's most important semantic choice was being made before the reader had actually read

`attentional_v2` began as the attempt to remove that contradiction. Its direction was:

- keep sentence-order fidelity
- stop treating prebuilt `section`s as the natural cognitive unit
- let the reader discover what deserves focused reading while moving through the text

Later, the benchmark stack changed for the same reason. Early evaluation families were still too shaped by builder-defined excerpt chunks and bounded probe layouts. Over time, the project moved toward:

- user-aligned note cases for local selectivity
- target-centered threads for long-span accumulation

In other words, both the mechanism and the evaluation system moved in the same direction:

- away from predeclared containers
- toward text-grounded, runtime-discovered, product-relevant evidence

## 1. Section-First Baseline: `iterator_v1`

### What the mechanism shape was

`iterator_v1` is a section-first sequential reader.

Its outer traversal shape is:

- book
- chapter
- persisted semantic `section`

Inside each selected section, it may further split into runtime `subsegment`s and run a local loop such as:

- `read`
- `think`
- `express`
- optional `search`
- optional `fuse`
- `reflect`

The key fact is that the persisted semantic unit exists before deep reading begins.

### Why this shape made sense at the time

It solved several practical problems well:

- stable traversal units for checkpoints and resume
- a natural section-level compatibility surface for chapter views and marks
- bounded local context inside each section
- a clear way to merge multiple local reactions back into one section-level result

It was also the mechanism around which the first serious benchmark and frontend compatibility surfaces were built.

### The tension it introduced

The same shape also planted the seed of the later redesign.

The reader's most important semantic decision was effectively:

- where the text should be cut

But in `iterator_v1`, that cut was decided before the reading loop, during parse/derivation, not during reading itself.

That made the architecture increasingly hard to justify from a human-reading perspective. Even after later improvements, the mechanism still assumed:

- the book can be turned into the right semantic containers in advance
- runtime reading mainly happens inside those containers

That was the conceptual limit V2 was eventually created to break.

### Strengths worth preserving

Even after V2 became the main direction, `iterator_v1` preserved real strengths:

- stable structure
- understandable checkpoints
- relatively strong long-distance continuity
- a readable separation between local reaction work and slower chapter-level accumulation

Those strengths later became things V2 tried to selectively recover, not things to erase.

### Primary refs

- [iterator_v1.md](../backend-reading-mechanisms/iterator_v1.md)
- [decision-log.md](./decision-log.md)
  - `DEC-010`
  - `DEC-018`
  - `DEC-019`

## 2. Strengthening V1 Exposed the Deeper Problem

Before the project fully left the section-first world, it already started softening it from within.

One early inflection was:

- subsegment choice moved from heuristic-first slicing toward LLM-primary planning with deterministic validation and fallback

This was an important clue. It meant the project had already recognized that:

- the working unit is a semantic judgment, not just a length-control problem

That change improved V1, but it also made the remaining contradiction clearer:

- even if subsegments are chosen semantically, they are still chosen inside a pre-cut section ontology

So the project was already leaning toward a more runtime-semantic reader before V2 formally arrived.

### Primary refs

- [decision-log.md](./decision-log.md)
  - `DEC-010`
- [iterator_v1.md](../backend-reading-mechanisms/iterator_v1.md)

## 3. Shared Runtime and Sentence Substrate: The Precondition for V2

V2 could not exist cleanly while the shared backend still treated `iterator_v1`'s private structure as universal truth.

So before the mechanism redesign could really land, the project made a set of platform decisions:

- separate shared runtime shell from mechanism internals
- separate canonical `book_document.json` from `iterator_v1`'s derived `structure.json`
- promote sentence order into the shared substrate
- keep mechanism comparability at the runtime/evaluation seam instead of forcing one internal ontology

This was the point where the repo stopped assuming that `section` and `subsegment` were universal backend truths.

That platform split mattered because V2 needed:

- sentence-order fidelity
- precise anchors and locators
- a non-section-first progression model

Without the shared sentence substrate and mechanism-neutral runtime shell, V2 would have been either:

- a fake abstraction on top of V1's ontology
- or a second backend stack with duplicated orchestration

### Primary refs

- [backend-reading-mechanism.md](../backend-reading-mechanism.md)
- [decision-log.md](./decision-log.md)
  - `DEC-011`
  - `DEC-017`
  - `DEC-018`
  - `DEC-019`

## 4. First-Principles Redesign: Why `attentional_v2` Was Created

### The core dissatisfaction

The decisive motivation behind V2 was not just that V1 underperformed on some benchmark. It was more basic:

- pre-cut semantic `section`s did not feel like an honest model of how reading should work

The project needed a mechanism whose reading logic would be driven by:

- every sentence being seen in order
- dynamic local accumulation
- meaning units discovered at runtime
- unresolved interpretive pressure, not fixed section traversal

### The first V2 ontology

The original V2 design introduced a different mental model:

- `sentence`
- `local buffer`
- `meaning unit`
- `trigger`
- `working pressure`
- `anchor memory`
- `reflective summaries`
- `knowledge activation`
- `move = advance | dwell | bridge | reframe`

It also fixed a new durable visible object:

- an anchored reaction, not a section-centered wrapper

This was a philosophical shift as much as a technical one. The mechanism was no longer saying:

- "first decide the section, then read inside it"

It was saying:

- "keep moving through the text, and let meaningful local reading events emerge from reading itself"

### What V2 was trying to preserve

The redesign was not anti-structure. It still wanted:

- text accountability
- bounded local reading
- durable state
- source-grounded memory
- visible anchored reactions

But it wanted those things without making prebuilt `section`s the cognitive center of the system.

### Primary refs

- [design-capture.md](../implementation/new-reading-mechanism/design-capture.md)
- [attentional_v2.md](../backend-reading-mechanisms/attentional_v2.md)

## 5. The First Implemented V2: Richer, More Dynamic, But Too Fragmented

The first implemented `attentional_v2` did not immediately land in its current shape. Its first real implementation followed a much more elaborate local-cycle architecture.

At a high level, it looked like:

- sentence intake
- cheap trigger detection
- optional escalation into a local-cycle path
- `zoom_read`
- `meaning_unit_closure`
- `controller_decision`
- `reaction_emission`
- optional bridge/search/slow-cycle work

This implementation added a lot of real machinery:

- sentence substrate
- survey artifacts
- typed state
- knowledge/search policy
- bridge resolution over source anchors
- reaction records
- chapter-end slow-cycle logic
- checkpointing and bounded resume
- normalized eval export
- real parse/read entrypoints under the shared runtime

### What this phase got right

This first implemented V2 established several lasting strengths:

- sentence-order fidelity became real substrate, not aspiration
- local reading became more text-sensitive than the section-first baseline
- anchored reaction truth became mechanism-native
- bridge/search behavior became explicit and controlled
- resume and state were treated as core mechanism behavior

### What this phase got wrong

It also accumulated too many semi-overlapping control surfaces.

The main problems later exposed were:

- heuristic trigger rules still acted like permission gates over what got a "real" read
- visibility and authority of spans drifted apart
- reading understanding, control, and visible reaction were split across too many nodes
- output truth could thin out after the mechanism had already formed local understanding

So the first implemented V2 was an important success, but not yet a coherent end-state.

### Primary refs

- [attentional_v2.md](../backend-reading-mechanisms/attentional_v2.md)
- [decision-log.md](./decision-log.md)
  - `DEC-020`
  - `DEC-021`
  - `DEC-022`
- [runtime-artifact-map.md](../implementation/new-reading-mechanism/runtime-artifact-map.md)

## 6. Formal Evaluation Changed the Question From “Tune It” to “Restructure It”

The next major turn did not come from theory alone. It came from formal evaluation, especially long-span review.

The key discovery was not simply:

- V2 lost some cases

It was:

- important text could fail to become a true reading event at all

The long-span follow-up work made several mechanism failures explicit:

- semantic permission gating was too dependent on fixed trigger heuristics
- a smaller visible analysis window could end up controlling a larger logical open span
- output ownership was too fragmented
- long-distance continuity remained weaker than V1 in important ways

This was the moment the project stopped treating V2 as something to polish incrementally and started treating it as something that needed structural rework.

The crucial decision here was:

- keep `attentional_v2` as the mechanism family
- but rework it in place rather than minting `attentional_v3`

That decision says a lot about the project's judgment:

- the direction was still right
- the current control shape was not

### Primary refs

- [attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_followup_reflection_and_decisions.md](../../reading-companion-backend/docs/evaluation/long_span/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_followup_reflection_and_decisions.md)
- [attentional_v2_structural_rework_plan.md](../implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md)

## 7. Post-Eval Structural Rework: From Complex Local Cycle to Simpler Reading Loop

The post-eval rework is the main line that produced the current V2 shape.

### Phase A-B: replace permission gating with a new control skeleton

The first big cut was:

- `navigate.unitize -> read -> navigate.route`

This changed the mechanism's center of gravity. Instead of letting trigger output decide whether正文 deserved real reading, the system moved to:

- mandatory formal reading of chosen coverage units
- semantic unitization up front
- route decisions after actual reading

This was the first major simplification.

### Phase C-D: make context and state actually usable

The next wave did not change the loop headline as dramatically, but it changed what the loop could carry:

- `state_packet.v1`
- packetized navigation/read context
- bounded `concept_digest` and `thread_digest`
- new primary state layers:
  - `working_state`
  - `concept_registry`
  - `thread_trace`
  - `reflective_frames`
  - `anchor_bank`
- continuation capsule and bounded supplemental recall / look-back

This phase matters because V2's problem was never only local reading. It was also:

- how to carry forward the right things without regressing to section-era structure or giant hidden state blobs

### Phase E: the temporary `Read -> Express` branch

For a while, the project tried an intermediate split:

- `read -> express(if needed) -> route`

This branch was useful because it isolated visible wording and forced surfaced semantics to become more explicit:

- `prior_link`
- `outside_link`
- `search_intent`

But it was deliberately not the final answer. The project later judged that the mechanism's visible reaction should stay closer to the same call that formed the reading understanding.

### Phase F: collapse back to a cleaner live shape

This is the major convergence phase.

The system moved to:

- `navigate.unitize -> read -> navigate.route`

with `Read` directly owning:

- surfaced reactions
- implicit uptake ops
- pressure signals
- optional detour need

Then it continued cleaning:

- `Navigate` took over detour search and dispatch
- persisted reactions became read-native truth
- old `Express` ownership and `raw_reaction` fallback were removed
- trigger/watch path was removed from the live runtime
- sentence intake became pure local-buffer ingest
- heading/special-content handling was softened so headings became weak cues rather than automatic standalone units

This is the point where V2 finally began to look like the mechanism it had been trying to become from the beginning:

- sentence-order
- runtime-discovered units
- read-native visible reactions
- navigation-owned movement
- less hidden gating
- simpler and more universal control logic

### Primary refs

- [attentional_v2.md](../backend-reading-mechanisms/attentional_v2.md)
- [attentional_v2_structural_rework_plan.md](../implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md)
- [current-state.md](../current-state.md)
- [registry.md](../tasks/registry.md)

## 8. Evaluation Also Had to Evolve With the Mechanism

The benchmark stack changed for the same reason the mechanism changed:

- older evaluation surfaces carried too much of the old ontology

## 8.1 First stable move: evaluation became mechanism-agnostic

One early major inflection was constitutional rather than dataset-specific:

- evaluation stopped treating the current `section` / `subsegment` architecture as protected truth

This mattered because it allowed the project to ask:

- is a different mechanism better for the product?

without first assuming the existing pipeline was correct.

### Primary refs

- [backend-reader-evaluation.md](../backend-reader-evaluation.md)
- [decision-log.md](./decision-log.md)
  - `DEC-011`
  - `DEC-014`
  - `DEC-015`

## 8.2 Early benchmark families: useful, but still too builder-shaped

The first serious benchmark families were still closer to the old mechanism world:

- excerpt micro-slice
- excerpt surface v1.1
- bounded long-span accumulation v1

These were useful for early diagnosis, but they had clear limits:

- excerpt targets were still too builder-curated
- long-span probes often over-relied on bounded `EARLY / MID / LATE` layouts
- some cases rewarded surface overlap more than truly user-relevant selective reading
- some long-span probes shared theme without proving real carry-forward

So these families were important stepping stones, but not the final benchmark philosophy.

### Primary refs

- [excerpt-micro-slice-v1-draft.md](../implementation/new-reading-mechanism/excerpt-micro-slice-v1-draft.md)
- [excerpt-surface-v1-1-draft.md](../implementation/new-reading-mechanism/excerpt-surface-v1-1-draft.md)
- [target_centered_accumulation_v2_design.md](../../reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md)
- [decision-log.md](./decision-log.md)
  - `DEC-024`
  - `DEC-025`

## 8.3 Transitional dataset work: question-aligned and human-notes-guided

Before the current active benchmarks, the project went through an intermediate phase of benchmark redesign:

- question-aligned case construction
- human-notes-guided dataset work
- private/local dataset territory and review pipeline hardening

This phase moved the benchmark platform forward in several ways:

- benchmark cases became more explicitly tied to evaluation questions
- private books became first-class local benchmark inputs
- benchmark review and adjudication became more rigorous

But it still had transitional baggage:

- cluster-mined synthetic cases
- more builder-authored benchmark semantics than the team ultimately wanted

This phase was necessary because it built the dataset platform and review discipline that the later active benchmarks rely on.

### Primary refs

- [question-aligned-case-construction.md](../implementation/new-reading-mechanism/question-aligned-case-construction.md)
- [evaluation-dataset-layout.md](../implementation/new-reading-mechanism/evaluation-dataset-layout.md)
- [decision-log.md](./decision-log.md)
  - `DEC-023`
  - `DEC-024`
  - `DEC-025`

## 8.4 Active excerpt benchmark: `user-level selective v1`

The biggest local-surface change was the move to the active note-aligned benchmark.

Its core design is:

- one continuous `reading_segment` per eligible book
- one `note_case` per aligned human note inside that segment
- score note recall against user-visible reactions

This changed the excerpt question from something like:

- did the mechanism hit builder-curated excerpt cases?

to something much closer to the product question:

- after reading this actual window, did the model visibly land on the places a human reader had really highlighted?

The matching contract also hardened:

- source-span overlap, not string or semantic similarity, is the gate
- `exact_match` is narrow and automatic
- non-exact overlaps go to judge
- only `focused_hit` counts alongside exact match

This benchmark is a major philosophical shift. It replaces:

- builder-curated excerpt surfaces

with:

- human note + aligned source span + visible reaction

### Primary refs

- [backend-reader-evaluation.md](../backend-reader-evaluation.md)
- [user_level/README.md](../../reading-companion-backend/docs/evaluation/user_level/README.md)
- [current-state.md](../current-state.md)

## 8.5 Active long-span benchmark: `target-centered accumulation v2`

The long-span redesign is just as important.

The old bounded long-span question was too close to:

- did the mechanism react separately at early / middle / late points?

The active long-span question is now:

- when the reader reaches the prepared target point, does it actually reconstruct the earlier thread there?

So the active case shape became:

- one target span
- `2+` upstream nodes
- one expected integration statement
- callback-eligible spans and tempting false targets

And the judge now looks at:

- target-local reactions
- explicit callback actions
- short-horizon followups
- target and upstream refs

It does **not** directly score raw mechanism state.

This is another major philosophical shift:

- long-span quality is no longer framed as generic memory or themed recurrence
- it is framed as successful integration at the target point

That makes the benchmark much closer to what "coherent accumulation" actually means.

### Primary refs

- [backend-reader-evaluation.md](../backend-reader-evaluation.md)
- [target_centered_accumulation_v2_design.md](../../reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md)
- [current-state.md](../current-state.md)

## 9. The Larger Pattern

Across both mechanism and evaluation, the project has been moving through the same three directional changes.

### 9.1 From predeclared semantic containers to runtime-discovered reading units

Mechanism side:

- `section`-first outer traversal

became:

- sentence-order intake
- runtime unitization
- pressure-driven reading

Evaluation side:

- builder-curated excerpt/probe containers

became:

- user-aligned notes
- target-centered threads

### 9.2 From section-shaped wrappers to anchored reading truth

Mechanism side:

- the durable visible object moved toward anchored reactions, not section wrappers

Evaluation side:

- scoring moved toward source-grounded visible reactions and target-point integration, not generic mechanism-internal summaries

### 9.3 From mechanism-internal convenience to product-first judgment

Both the runtime and the benchmark stack became less willing to say:

- this is easy to build, so it must be the right unit

and more willing to say:

- does this preserve the feeling of a living, text-grounded co-reader?

That is the real through-line of the whole evolution.

## 10. Current Position

Today the project sits in a deliberately asymmetric posture:

- `iterator_v1` is still kept as a supported fallback and comparison baseline
- `attentional_v2` is the default and the active direction
- V2 is being evolved in place rather than replaced by `attentional_v3`
- the active excerpt benchmark is `user-level selective v1`
- the active long-span benchmark is `target-centered accumulation v2`

So the project is no longer asking:

- should we go back to section-first reading?

It is asking:

- how do we keep V2's runtime-discovered, sentence-faithful reading shape while regaining the strongest continuity and reliability traits that V1 exposed?

That is the current frontier.

## Source Map

- shared mechanism boundary:
  - [backend-reading-mechanism.md](../backend-reading-mechanism.md)
- current V1 authority:
  - [iterator_v1.md](../backend-reading-mechanisms/iterator_v1.md)
- current V2 authority:
  - [attentional_v2.md](../backend-reading-mechanisms/attentional_v2.md)
- post-eval V2 rework plan:
  - [attentional_v2_structural_rework_plan.md](../implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md)
- initial V2 design capture:
  - [design-capture.md](../implementation/new-reading-mechanism/design-capture.md)
- evaluation constitution:
  - [backend-reader-evaluation.md](../backend-reader-evaluation.md)
- active user-level benchmark:
  - [user_level/README.md](../../reading-companion-backend/docs/evaluation/user_level/README.md)
- active long-span benchmark:
  - [target_centered_accumulation_v2_design.md](../../reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md)
- historical inflection record:
  - [decision-log.md](./decision-log.md)
