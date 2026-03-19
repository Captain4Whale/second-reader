# Backend Reader Evaluation

Purpose: define how the backend reader's quality should be evaluated across mechanism, output, and runtime layers.
Use when: defining reader quality goals, planning evals for reader changes, choosing between deterministic metrics and LLM-as-judge, or deciding whether a change needs local A/B evaluation or broader regression evaluation.
Not for: public API contract authority, runtime lifecycle semantics, or one-off benchmark results.
Update when: reader quality dimensions, evaluation workflow, or evaluation artifact routing materially change.

Use `docs/backend-reading-mechanism.md` for how the reader works. Use this file for how we decide whether the reader is getting better or worse.

## Why Reader Evaluation Exists
- Reader evaluation exists to guide optimization first and preserve evidence second.
- The first job of eval is to make mechanism work legible:
  - what changed
  - what "better" means for that change
  - whether the change improved the intended reader behavior
- Records still matter because they:
  - preserve baselines
  - prevent "it feels better" drift
  - make it easier to understand why later mechanism choices were made
- A good evaluation practice should therefore support both:
  - local mechanism decisions
  - longer-term reader quality memory

## What Good Means
- Reader quality is layered, not a single score.
- Product-good and mechanism-good are related but not identical:
  - product-good asks whether the system feels like a thoughtful co-reader
  - mechanism-good asks whether one internal mechanism improved the reader's behavior in the intended way
- Good evaluation should therefore avoid collapsing everything into one vague judgment such as "smarter" or "more human."
- Reader quality should also avoid bad proxies:
  - more reactions is not automatically better
  - more human-like is not automatically better
  - longer notes are not automatically better
  - tighter lexical overlap with human highlights is not automatically better
- The working standard is:
  - the reader should select and process text in ways that support focused, source-grounded, selective, and coherent co-reading reactions under realistic runtime constraints

## Evaluation Taxonomy
- Reader eval naming should separate:
  - `target`
    - what mechanism or object is under evaluation
  - `scope`
    - how far the evaluation follows the effect of that target
  - `method`
    - how the judgment is produced

### Target
- `target` names the evaluated mechanism or object, not the layer or scoring method.
- Targets should use stable snake_case slugs.
- Current examples:
  - `subsegment_segmentation`
  - `reaction_generation`
  - `memory_carryover`
  - `section_merge`
  - `reader_end_to_end`

### Scope
- `direct_quality`
  - evaluate the target's own direct output
- `local_impact`
  - evaluate the target's effect on the next meaningful output layer
- `system_regression`
  - evaluate the broader reader after multiple interacting changes

### Method
- `deterministic_metrics`
- `pairwise_judge`
- `rubric_judge`
- `human_spot_check`

- Reports and run artifacts should record:
  - `target`
  - `scope`
  - `method`
  - dataset version
  - comparison target

## Evaluation Layers
### Subsegment
- Evaluate whether the runtime reading unit itself is well chosen.
- Core dimensions:
  - `self-containedness`
    - can the unit stand on its own as a local reading object?
  - `minimal sufficiency`
    - is it the smallest unit that still supports one complete local reading move?
  - `one primary reading move`
    - does the unit mostly support one main reading move instead of mixing several unrelated ones?

### Reaction
- Evaluate whether the reader's local response is good once the unit is chosen.
- Core dimensions:
  - `focus`
    - is each reaction centered on a clear point?
  - `source anchoring`
    - does the reaction stay grounded in the text and use a readable anchor quote?
  - `selectivity`
    - did the reader choose worthwhile things to say rather than reacting mechanically to everything?
  - `meaningful curiosity`
    - when curiosity appears, is it the kind that deepens reading rather than creating generic side-questions?

### Section
- Evaluate the merged section-level result after the reader finishes its local work.
- Core dimensions:
  - `coverage of meaningful points`
    - are important turns, definitions, causal links, or callbacks captured?
  - `coherence after merge`
    - do the section reactions still feel like one coherent reading trail after multiple runtime units are merged?
  - `low redundancy`
    - are repeated or near-duplicate reactions avoided?

### Chapter / Book Trajectory
- Evaluate whether the reader's understanding carries over across larger spans.
- Core dimensions:
  - `memory carry-over`
    - do earlier findings and open threads help later reading?
  - `thread continuity`
    - do callbacks, retrospects, and chapter synthesis feel earned?
  - `chapter-level arc quality`
    - does a chapter read like a developing line of thought rather than a pile of local notes?

### Process / Runtime
- Evaluate whether the reader remains operationally healthy while pursuing quality.
- Core dimensions:
  - `fallback rate`
    - how often semantic mechanisms fail and revert to safety behavior
  - `timeout rate`
    - how often the reader runs out of time or work budget
  - `cost / latency`
    - whether gains remain acceptable for the intended usage
  - `planner failure modes`
    - whether malformed plans, invalid structure, or oversized units are under control

## Evaluation Methods
### Deterministic Metrics
- Use deterministic metrics for structure and process questions.
- Typical examples:
  - subsegment count
  - average unit size
  - fallback rate
  - timeout rate
  - per-section reaction count
  - repeated-reaction rate
- These metrics are useful for guardrails and trend lines, but they are not sufficient for semantic quality by themselves.

### LLM-As-Judge
- Use LLM-as-judge for semantic quality questions that deterministic metrics cannot answer well.
- Good uses include:
  - whether one output is more focused than another
  - whether a subsegment is self-contained
  - whether a section output missed a meaningful turn or definition
  - whether version A or B is the better co-reading result under a defined rubric
- In this project, LLM-as-judge should be treated as an offline evaluator, not as a runtime reader agent.
- The value of the judge comes from the rubric, not from the judge existing on its own.

### Human Spot-Checking
- Human review should audit the evaluation system, not replace it as the default scoring path.
- Human spot-checking is especially useful for:
  - validating whether the judge rubric is sensible
  - catching judge drift
  - distinguishing real regressions from reasonable reading-style differences

### Pairwise Preference vs Rubric Scoring
- Use pairwise A/B preference when the question is:
  - which version is better overall for this specific task?
- Use rubric scoring when the question is:
  - what exactly improved or regressed, and along which dimensions?
- In practice, the two methods often work best together:
  - pairwise for summary preference
  - rubric for diagnostic explanation

## When To Evaluate
- Run local mechanism evaluation after major reader-core changes.
- Use local evaluation when the goal is attribution:
  - did this change itself improve the intended behavior?
- Run broader regression evaluation after a cluster of changes to prompts, memory, search, reflection, or synthesis.
- Do not wait for every mechanism to change before first evaluation.
- If evaluation is deferred too long, improvement and regression become hard to attribute.

## Current Example: Subsegment Planning
- The current subsegment planner is the first concrete example for this evaluation framework.
- The benchmark for this change should compare `heuristic_only` and `llm_primary` on the same tracked cases, with search disabled and a dedicated eval-only runtime root so the signal stays focused on slicing quality.
- The dedicated runner lives under `reading-companion-backend/eval/subsegment/` and should be invokable as one offline command rather than through the normal runtime read flow.
- In taxonomy terms:
  - `target = subsegment_segmentation`
  - default `scope = direct_quality`
  - optional `scope = local_impact`
- The older "plan-level" language maps to `scope = direct_quality`.
- The older "downstream section-level" language maps to `scope = local_impact`.
- The current benchmark should default to `direct_quality`.
- `local_impact` should be opt-in and used when we specifically want evidence that better slicing carries through to better section-level reading output.
- For this change, the goal is not:
  - more human-like slicing
  - more units
  - more reactions
- For this change, the goal is:
  - the fewest self-contained local reading units that support one main nonfiction reading move at a time
- The most important success dimensions for this change are:
  - `self-containedness`
    - does each chosen unit stand as a readable local object?
  - `reaction focus`
    - are reactions less blurred across multiple ideas?
  - `source-anchor quality`
    - are anchor quotes more complete and readable?
  - `coverage of meaningful turns / definitions / callbacks`
    - are important local moves less likely to be missed?
  - `coherence after merge back to section level`
    - does the section output still feel like one reading trail?
  - `acceptable runtime guardrails`
    - are fallback, timeout, and cost still reasonable?

## Artifact Layout
- Stable methodology belongs in `docs/`.
- Concrete evaluation reports belong in `reading-companion-backend/docs/evaluation/`.
- Executable evaluation code belongs in `reading-companion-backend/eval/`.
- Tracked benchmark datasets belong in `reading-companion-backend/eval/datasets/`.
- Machine-generated benchmark runs belong in `reading-companion-backend/eval/runs/` and should stay out of normal runtime `state/` / `output/` paths.
- Temporary experiment logs belong in `reading-companion-backend/docs/research/` only when they are not yet stable reports.

### Expectations For Evaluation Reports
- Per-run or per-change reports should state:
  - target
  - scope
  - method
  - comparison target
  - sample set
  - dataset version
  - rubric used
  - summary conclusion
  - known caveats
- This stable methodology document should not be used as a running benchmark log.
