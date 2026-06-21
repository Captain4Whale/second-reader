# Decision Log

Purpose: preserve design evolution, key decisions, and rejected alternatives that would be difficult to reconstruct later from current-state docs alone.
Use when: tracing why the project converged on its current shape or recording a major change in direction.
Not for: routine change logs, source-of-truth engineering definitions, or interview-ready wording.
Update when: a major product or engineering decision is made, reversed, or becomes historically important to future contributors.

## Entry 1
**ID**: DEC-001
**Status**: superseded by `DEC-039`

**Decision / Inflection**: Converge on `sequential` as the primary product and engineering path.

**Period**: Early workspace baseline through the March 2026 cleanup period.

**Problem**: The repository still contained broader, more experimental reading paths, but the product needed one dependable loop that could be run, recovered, validated, and explained without splitting attention across competing architectures.

**Alternatives considered**: Keep a more generalized graph-first direction as the main path, or let `book_analysis`-style capabilities define the default product story.

**Why this path won**: A single sequential path created a cleaner basis for runtime recovery, frontend integration, and later documentation. It also made the product easier to demo as a coherent reading experience instead of a bundle of agent experiments.

**What changed in the system**: Product and backend rules now explicitly treat `sequential` as primary, while `book_analysis` remains secondary and non-authoritative for default decisions.

**Why it matters later**: This is the clearest example of the project choosing focus over maximal flexibility. Without recording it, later readers would see the remaining experimental traces but miss why the main path narrowed.

**Primary evidence**:
- `5d5c7b2` `Remove high-signal logic`
- `reading-companion-backend/AGENTS.md`
- `docs/product-interaction-model.md`

## Entry 2
**ID**: DEC-002
**Status**: active

**Decision / Inflection**: Shape the current long-task model around upload, deferred parse, and explicit `analysis/start` / `analysis/resume`.

**Period**: March 2026, especially the book-overview consolidation work.

**Problem**: The system needed a user-facing flow that could handle both "start immediately" and "prepare structure first" without splitting the product into separate tools or one-off routes.

**Alternatives considered**: Make upload always start full analysis immediately, keep parsing and deep reading as more disconnected workflows, or hide continuation behind internal-only recovery behavior.

**Why this path won**: The upload -> deferred parse -> explicit start/resume model made the book overview a real control surface. It gave the product a stable way to present structure readiness, continue actions, and long-running progress in one place.

**What changed in the system**: Upload provisioning, book overview state, and long-task orchestration converged on the current `POST /api/uploads/epub`, `analysis/start`, and `analysis/resume` model, with a clearer `ready` state between parse and deep reading.

**Why it matters later**: This is one of the core product-shaping decisions. It explains why the overview page is not just a result screen, but the operational center for a book.

**Primary evidence**:
- `3657e9e` `统一 Book overview 单页布局`
- `docs/product-interaction-model.md`
- `docs/backend-sequential-lifecycle.md`

## Entry 3
**ID**: DEC-003
**Status**: active

**Decision / Inflection**: Treat runtime recovery, checkpointing, and resume as product behavior rather than hidden operations.

**Period**: March 2026, first with stable runtime work and then with minimal resume recovery.

**Problem**: Book-length reading jobs can stall, restart, or cross process boundaries. A "just rerun it" model would have made the experience fragile and hard to trust.

**Alternatives considered**: Accept frequent reruns, keep recovery mostly invisible to the product layer, or handle failures manually as operator-only concerns.

**Why this path won**: For long-running reading, trust depends on visible continuity. Recovery had to show up in public state, user-facing controls, and documented runtime semantics.

**What changed in the system**: The backend gained explicit checkpoint-aware resume behavior, demo/prod runtime guardrails, paused states, recovery events, and surfaced fields like `resume_available` and `last_checkpoint_at`.

**Why it matters later**: This inflection marks the moment the project stopped behaving like a fragile background script and started behaving like a recoverable product system.

**Primary evidence**:
- `554fe5a` `Implement Railway health and demo`
- `d2650be` `Implement minimal resume recovery`
- `docs/runtime-modes.md`
- `docs/backend-sequential-lifecycle.md`

## Entry 4
**ID**: DEC-004
**Status**: active

**Decision / Inflection**: Make the API layer the normalization boundary for public routes, IDs, and taxonomy.

**Period**: Early March 2026 contract hardening.

**Problem**: Internal runtime artifacts, compatibility routes, and legacy taxonomy values did not line up cleanly with the frontend-facing contract.

**Alternatives considered**: Push normalization into the frontend, or require internal artifacts to match the public contract exactly before any response could be emitted.

**Why this path won**: The API layer was the narrowest place to preserve a stable external contract while allowing runtime artifacts and migration steps to evolve more gradually.

**What changed in the system**: OpenAPI snapshots, contract tests, generated frontend types, and API mapping logic were tightened so the public contract became explicit and checkable instead of implicit.

**Why it matters later**: This explains why current handlers and helpers still translate internal ids, routes, and taxonomy values instead of assuming the runtime storage format is already public-ready.

**Primary evidence**:
- `8ff9b14` `Align API contract documentation`
- `c3f39c6` `加强 API 合约校验步骤化执行方案`
- `docs/api-contract.md`
- `reading-companion-backend/src/api/contract.py`

## Entry 5
**ID**: DEC-005
**Status**: active

**Decision / Inflection**: Productize Reading Mindstream so "the reader is thinking now" becomes part of the main experience.

**Period**: March 2026.

**Problem**: The project needed to preserve the feeling of an active co-reader instead of flattening the experience into static results and generic summaries.

**Alternatives considered**: Keep progress updates mostly mechanical, leave the live reading trace in low-visibility backend artifacts, or center the UX on finished outputs only.

**Why this path won**: Surfacing the live reading trace made the system feel like an ongoing reading process rather than a delayed report generator. It also reinforced the product promise that the AI is reading with the user, not only after the fact.

**What changed in the system**: Realtime payloads, overview rendering, and runtime language were reshaped around live activity, pulse messages, and the current-reading snapshot.

**Why it matters later**: This is one of the clearest product differentiators. It records why the app now has a visible "mindstream" instead of a purely task-centric progress widget.

**Primary evidence**:
- `fa5157e` `Implement Reading Mindstream plan`
- `docs/product-interaction-model.md`
- `docs/api-integration.md`
- `reading-companion-backend/src/api/realtime.py`

## Entry 6
**ID**: DEC-006
**Status**: active

**Decision / Inflection**: Converge frontend routes and the book overview into the canonical control surface.

**Period**: March 2026, especially around the overview unification and chapter drawer work.

**Problem**: The product needed a more coherent route story and fewer split entrypoints between upload, analysis, overview, and chapter consumption.

**Alternatives considered**: Keep multiple parallel overview-like pages, continue relying on compatibility routes, or let upload and analysis live as more isolated screens.

**Why this path won**: Pulling state, controls, and chapter navigation into the book overview made the frontend easier to understand and better aligned with the long-task model.

**What changed in the system**: Canonical routes and overview responsibilities tightened around `/books`, `/books/:id`, and `/books/:id/chapters/:chapterId`, while compatibility routes became secondary.

**Why it matters later**: This explains why the current route model looks intentional rather than accidental, and why the overview page carries so much operational responsibility.

**Primary evidence**:
- `3657e9e` `统一 Book overview 单页布局`
- `63ccadf` `Add chapter drawer navigation`
- `docs/product-interaction-model.md`
- `reading-companion-frontend/src/app/routes.tsx`

## Entry 7
**ID**: DEC-007
**Status**: active

**Decision / Inflection**: Stabilize local demo and deployment runtime instead of treating development mode as the only supported way to run.

**Period**: March 2026.

**Problem**: Hot-reload development mode was not a good fit for demos or deployment-like reliability, and the project needed an operator story beyond "run the dev server and hope it stays up."

**Alternatives considered**: Continue using dev mode everywhere, rely on ad hoc manual restarts, or leave deployment/runtime expectations implicit in scripts.

**Why this path won**: Introducing explicit demo/stable runtime modes created a cleaner separation between coding ergonomics and presentation or deployment reliability.

**What changed in the system**: Healthcheck behavior, Railway entrypoints, stable backend launchers, and demo supervision became documented and script-backed parts of the workspace.

**Why it matters later**: This records the point where the project started behaving like a presentable, operable app rather than a dev-only sandbox.

**Primary evidence**:
- `554fe5a` `Implement Railway health and demo`
- `docs/runtime-modes.md`
- `railway.json`
- `scripts/run-backend-stable.sh`

## Entry 8
**ID**: DEC-008
**Status**: active

**Decision / Inflection**: Split documentation into stable facts, temporary handoff, archive material, and history instead of keeping mixed-purpose notes.

**Period**: Mid-March 2026.

**Problem**: Rules, current state, research notes, and archival material had started to bleed into one another, which made both agent context and human reading noisier.

**Alternatives considered**: Keep a flatter docs layout, continue using one-off handoff notes as semi-authoritative references, or leave research/evaluation materials mixed into regular reading paths.

**Why this path won**: A layered docs system reduced context pollution and made it clearer which documents define current behavior versus which ones preserve historical or reference-only material.

**What changed in the system**: Workspace docs were reorganized into control, stable facts, temporary working notes, archive/reference material, and now explicit engineering history.

**Why it matters later**: This entry explains why the repo now has separate stable docs and history docs, and why some old notes were intentionally demoted rather than deleted.

**Primary evidence**:
- `b7adf3d` `Redesign AGENTS documentation plan`
- `0b01400` `Reorganize docs hierarchy`
- `231c396` `Remove case study docs`
- `AGENTS.md`

## Entry 9
**ID**: DEC-009
**Status**: active

**Decision / Inflection**: Introduce a frontend visual-system document and separate core UI typography from reader-content scaling.

**Period**: Mid-March 2026.

**Problem**: The frontend already had a recognizable visual language, but typography rules were still scattered across page-local inline styles. At the same time, the chapter reading workspace needed a clear answer to which text should respect user-controlled reading scale and which text should remain fixed application chrome.

**Alternatives considered**: Keep page-local typography decisions implicit, force every page including landing into one typography system immediately, or let reader scale continue affecting both content and chrome without a documented boundary.

**Why this path won**: A documented visual system created a stable way to align the core application without erasing intentional special cases like the landing page. Separating UI typography from reader-content typography also preserved adjustable reading comfort without turning navigation and controls into moving targets.

**What changed in the system**: The workspace gained a stable frontend visual-system document, new theme tokens for core typography roles, and explicit reader-scale boundaries that distinguish scalable reading content from fixed application chrome.

**Why it matters later**: This is the point where typography stopped being a page-by-page implementation detail and became an explicit frontend system. Future contributors will need this context to understand why landing remains a controlled exception and why reader-scale logic is intentionally narrower than "all text in the chapter page."

**Primary evidence**:
- `docs/frontend-visual-system.md`
- `AGENTS.md`
- `reading-companion-frontend/AGENTS.md`
- `reading-companion-frontend/src/styles/theme.css`

## Entry 10
**ID**: DEC-010
**Status**: active

**Decision / Inflection**: Move runtime subsegment selection from heuristic-first slicing to LLM-primary planning with deterministic validation and heuristic fallback.

**Period**: Mid-March 2026.

**Problem**: The reader's smallest runtime work unit directly shapes what the model can notice, question, and say. The earlier slicing path was useful as an engineering guardrail, but it still optimized mainly for length and density control instead of for the smallest self-contained local reading move.

**Alternatives considered**: Keep the previous length/density-driven heuristic as the main selector, hard-code a richer rule engine for discourse boundaries, or add a more elaborate multi-model arbitration layer for only a few difficult sections.

**Why this path won**: An LLM-primary planner better matches the product goal of a thoughtful co-reader because subsegment choice is fundamentally a semantic judgment, not only a sizing problem. Keeping deterministic validation plus the existing sentence-boundary heuristic as fallback preserved runtime safety without letting safety logic define the semantic target.

**What changed in the system**: Multi-sentence sections now go through a planner prompt that proposes the fewest self-contained runtime units needed for one local nonfiction reading move at a time. The runtime validates full sentence coverage, ordering, reading-move labels, per-unit hard token caps, and the safety cap before materializing the plan. If any of those checks fail, the reader falls back to the older heuristic slicer. The default `slice_max_subsegments` cap was also widened and reframed as a safety guard rather than a semantic objective.

**Why it matters later**: This is a reader-core design shift, not a routine tuning pass. Future contributors will otherwise see both the planner and the fallback code paths but miss why the project stopped treating heuristic chunking as the primary definition of the attention unit.

**Primary evidence**:
- `docs/backend-reading-mechanism.md`
- `reading-companion-backend/src/iterator_reader/reader.py`
- `reading-companion-backend/src/iterator_reader/prompts.py`
- `reading-companion-backend/src/iterator_reader/policy.py`

## Entry 11
**ID**: DEC-011
**Status**: active

**Decision / Inflection**: Freeze the evaluation frame as product-first and mechanism-agnostic.

**Period**: March 2026, after the first stable subsegment benchmark baselines and benchmark taxonomy cleanup.

**Problem**: The project needed a durable way to judge reader quality without assuming that the current `section` / `subsegment` pipeline was the final architecture. Without that frame, later mechanism changes could be debated as implementation preference instead of product evidence.

**Alternatives considered**: Keep evaluation centered on the existing slicing pipeline, treat benchmark reports as the only meaningful authority, or delay a stable methodology until a future architecture change forced one.

**Why this path won**: A product-first evaluation constitution makes the reader architecture comparable across implementations. It preserves the existing `target` / `scope` / `method` taxonomy while letting future mechanisms compete on the same north-star criteria instead of on internal shape.

**What changed in the system**: The stable evaluation doc now explicitly treats `section`, `subsegment`, memory packing, search, and future reader designs as evaluable mechanisms rather than protected truths. It also separates stable methodology from evolving benchmark composition and per-run evidence.

**Why it matters later**: This is the point where evaluation becomes the project-level constitution for reader work. Future contributors should be able to ask whether a different mechanism is better without first accepting the current pipeline as canonical.

**Primary evidence**:
- `2187335` `Record runtime-first subsegment benchmark outputs`
- `6738155` `Refine subsegment eval taxonomy and direct-quality benchmark`
- `b18043c` `Add reader evaluation methodology documentation`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/eval/subsegment/run_benchmark.py`

## Entry 12
**ID**: DEC-012
**Status**: active

**Decision / Inflection**: Reframe the product purpose around a living co-reader mind rather than a narrower outcome-led promise.

**Period**: March 2026, after the evaluation constitution was stabilized.

**Problem**: The product promise was still dominated by outcome language such as helping readers notice blind spots or unknown unknowns. That language captured part of the value, but it was narrower than the actual product surfaces, which already emphasized live thought, resonance, saved marks, and the feeling of reading alongside an active mind.

**Alternatives considered**: Keep the old purpose centered mainly on user blind-spot discovery, define the product through a fixed closed list of downstream benefits, or broaden the purpose immediately into explicit user-agent dialogue and steering.

**Why this path won**: Centering the product on a genuinely curious co-reading mind preserves what feels special about the experience without locking the product to one narrow benefit channel. It also gives later evaluation and mechanism choices a deeper standard than "did it produce more surprises?" while avoiding premature commitment to a dialogue-first product.

**What changed in the system**: The stable product-purpose language now lives explicitly in `docs/product-interaction-model.md` and defines the product through essence, lived reading experience, and illustrative value channels. The evaluation methodology doc now aligns to that framing instead of competing with it, and explicit user-agent steering remains marked as emerging rather than canonical.

**Why it matters later**: This is the framing shift that lets future reader work optimize for a living reading intelligence rather than for a single visible outcome such as blind-spot discovery. It also explains why resonance, delight, recall, and companionship should be understood as important expressions of the product rather than as competing product identities.

**Primary evidence**:
- `docs/product-interaction-model.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-frontend/src/app/content/landing-content.ts`
- `reading-companion-frontend/src/app/config/product-lexicon.ts`

## Entry 13
**ID**: DEC-013
**Status**: active

**Decision / Inflection**: Promote product purpose into its own stable authority document and separate it from interaction-flow authority.

**Period**: March 2026, immediately after the living co-reader reframing.

**Problem**: `docs/product-interaction-model.md` had started carrying both the deeper product-purpose framing and the route/page interaction model. That made one document do two jobs at once and blurred the difference between "what this product fundamentally is" and "how the current product is organized on screen."

**Alternatives considered**: Keep product-purpose authority inside the interaction-model doc, duplicate the same product-purpose language across multiple stable docs, or create an overview doc but leave it outside the standard reading path.

**Why this path won**: A dedicated product-overview doc creates a clearer authority chain. It gives the product essence, value channels, and canonical-vs-emerging boundaries one stable home, while letting the interaction-model and evaluation docs align to that purpose without competing with it.

**What changed in the system**: `docs/product-overview.md` now owns product essence and value framing. `docs/product-interaction-model.md` now focuses on journey, routes, page responsibilities, and interaction rules. `docs/backend-reader-evaluation.md` now points to the overview doc as product-purpose authority. Root and child `AGENTS.md` files were updated so the new overview doc is part of the standard reading path.

**Why it matters later**: This split makes future product, design, and evaluation work easier to reason about. Contributors can refine purpose without accidentally rewriting flow rules, and they can refine flow without accidentally redefining the product's core identity.

**Primary evidence**:
- `docs/product-overview.md`
- `docs/product-interaction-model.md`
- `docs/backend-reader-evaluation.md`
- `AGENTS.md`

## Entry 14
**ID**: DEC-014
**Status**: active

**Decision / Inflection**: Make the reader evaluation constitution decision-complete around reader character, reader value, and runtime viability.

**Period**: Late March 2026, after product-purpose authority moved into `docs/product-overview.md`.

**Problem**: The evaluation frame was already product-first and mechanism-agnostic, but it still left important ambiguity about what the north star actually contained, how strong anti-goals should be, and which questions belonged in stable methodology versus in benchmark reports. Without that clarification, future contributors could still overfit evaluation to a flat blended checklist, over-police surprise or resonance, or quietly move benchmark policy into the constitution.

**Alternatives considered**: Keep the earlier north star as a looser blended list, make stronger anti-goals that discouraged surprise or resonance as such, elevate recall and re-entry to first-class north-star territory, or let benchmark reports continue filling in the missing methodology by convention.

**Why this path won**: Splitting the north star into `reader_character` and `reader_value`, with `runtime_viability` as a standing gate, makes the evaluation system clearer without hard-freezing current mechanisms. Narrowing anti-goals to anti-reduction rules preserves room for text-earned surprise, resonance, and delight while still protecting the product from collapsing into proxy optimization. Keeping recall and re-entry as secondary durable-trace audits also keeps the framework aligned with the actual product surfaces instead of forcing extra recap structure into the reader.

**What changed in the system**: `docs/backend-reader-evaluation.md` now defines the stable evaluation constitution around two north-star families plus one runtime gate, reframes evaluation layers as mechanism-agnostic product lenses, makes `pairwise_judge` and `rubric_judge` the default semantic tools, keeps human review optional calibration, and sharpens the boundary between stable methodology and evolving benchmark/report policy.

**Why it matters later**: This is the clarification that makes the evaluation constitution more usable as a day-to-day decision tool instead of only a high-level principle. Future contributors should be able to compare a subsegment-based reader, a non-slicing reader, or a search-heavy reader with the same framework without accidentally turning benchmark details, surprise effects, or recap-oriented audits into the product definition.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/product-overview.md`
- `reading-companion-backend/docs/evaluation/subsegment/subsegment_benchmark_v1_baseline.md`

## Entry 15
**ID**: DEC-015
**Status**: superseded by `DEC-055`

**Decision / Inflection**: Introduce a shared backend runtime shell for multiple reader mechanisms while freezing `iterator_reader` as the current default implementation.

**Period**: Late March 2026.

**Problem**: The project now has at least two materially different reader directions in view: the existing `section` / `subsegment` pipeline and newer designs built around different attention and progression logic. Evolving all of that inside `iterator_reader` would either force incompatible mechanisms into one internal ontology or split the backend into ad hoc parallel stacks with duplicated runtime and integration code.

**Alternatives considered**: Keep extending `iterator_reader` as the only backend architecture, build a "universal" internal reader model that every mechanism must conform to, or fork separate end-to-end backends per mechanism.

**Why this path won**: A narrow shared runtime shell preserves one place for jobs, checkpoints, public-state projection, and evaluation wiring, while allowing each reader mechanism to keep its own internal ontology. That keeps future mechanisms comparable without pretending they share the same attention unit, memory shape, or movement logic.

**What changed in the system**: Workspace and backend docs now distinguish backend-wide runtime/mechanism boundaries from the current default `iterator_reader` implementation. The backend direction is now "shared shell plus mechanism-specific readers," with `iterator_reader` retained as the only default/live mechanism during the first scaffold step.

**Why it matters later**: This is the decision that prevents future reader work from becoming either a maze of duplicated orchestration code or a fake abstraction layer that weakens every mechanism. Later contributors need to know that compatibility is expected at the runtime/evaluation boundary, not by forcing identical internal structures.

**Primary evidence**:
- `docs/workspace-overview.md`
- `reading-companion-backend/AGENTS.md`
- `reading-companion-backend/main.py`
- `reading-companion-backend/src/iterator_reader/`

## Entry 16
**ID**: DEC-016
**Status**: active

**Decision / Inflection**: Make `book_document.json` the canonical parsed-book substrate and treat `structure.json` as a current-mechanism derived artifact.

**Period**: Late March 2026, immediately after the first shared runtime/mechanism scaffold landed.

**Problem**: The first runtime scaffold still depended on `iterator_reader.models`, which meant the backend's supposed shared layer was still inheriting the current mechanism's ontology. That would have made future mechanisms compare against `section` / `subsegment` assumptions even when their real reading logic wanted different internal units.

**Alternatives considered**: Keep `BookStructure` as the de facto shared parsed-book model, move every future mechanism onto the same `structure.json` assumptions, or delay the shared substrate split until a second mechanism was already live.

**Why this path won**: Separating the canonical book substrate from current-mechanism traversal state creates a real narrow waist. The backend can now share chapter/paragraph/locator truth, mechanism-neutral runtime contracts, and normalized comparison outputs without pretending that all reader mechanisms share one internal planning shape.

**What changed in the system**: The backend now has `src/reading_core/` for canonical book substrate, runtime contracts, and normalized cross-mechanism output types. Parse flow writes `public/book_document.json` first, then `iterator_v1` derives its own structure artifact from that substrate. Shared runtime, library, and search modules now import neutral types from `reading_core` instead of from `iterator_reader.models`.

**Why it matters later**: This is the design boundary that should let future readers differ radically in internal ontology while still sharing the same runtime shell and evaluation seam. Later contributors need to know that `structure.json` is not the universal parsed-book truth anymore, even if the current public surfaces still consult it for iterator-shaped section views.

**Primary evidence**:
- `reading-companion-backend/src/reading_core/`
- `reading-companion-backend/src/reading_runtime/`
- `reading-companion-backend/src/iterator_reader/parse.py`
- `docs/backend-state-aggregation.md`

## Entry 17
**ID**: DEC-017
**Status**: active

**Decision / Inflection**: Separate transient uploads, durable source-library books, runtime book copies, and evaluation packages into distinct source-asset territories.

**Period**: March 2026, during the first serious `attentional_v2` evaluation-corpus planning pass.

**Problem**: The backend already had user uploads, runtime book copies, local data files, fixtures, and benchmark assets, but they were too easy to blur together conceptually. Without an explicit territory model, future contributors could quietly treat `state/uploads/` as a de facto library, build evaluation corpora from ad hoc runtime files, or lose the difference between one analyzed `book_id` and a durable source-book identity.

**Alternatives considered**: Keep all source books informally under one "backend data" idea, treat runtime book copies as the natural evaluation corpus, or let uploads flow into evaluation use without an explicit promotion boundary.

**Why this path won**: A territory model makes upstream and downstream responsibilities clearer. It preserves the product/runtime upload flow while also giving evaluation work a cleaner, more reproducible path. It also keeps manually curated backend books distinct from transient user uploads without forcing every durable source into the repo.

**What changed in the system**: Stable docs now distinguish:
- `state/uploads/` as transient intake
- per-book runtime copies under `output/<book_id>/...` as one analyzed book's reproducible source territory
- `state/library_sources/` as the durable local source-library territory for manually curated books
- `eval/datasets/` and `eval/manifests/` as evaluation-package territory

**Why it matters later**: This is the storage rule that should stop future evaluation work from becoming "whatever books happened to be uploaded recently." It also explains why user uploads are not automatically part of the durable library or benchmark corpus, and why promotion into those roles should remain explicit.

**Primary evidence**:
- `docs/workspace-overview.md`
- `docs/backend-sequential-lifecycle.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/AGENTS.md`

## Entry 18
**ID**: DEC-018
**Status**: active

**Decision / Inflection**: Organize benchmark inputs by evidence family and language track instead of by one active mechanism's folder tree.

**Period**: March 2026, during the first bilingual `attentional_v2` benchmark preparation pass.

**Problem**: The project now needs multiple kinds of benchmark inputs at once: excerpt cases, chapter corpora, runtime fixtures, and compatibility fixtures. Without a durable dataset layout, those assets would drift into ad hoc folders, silently mix tracked inputs with generated outputs, and make it harder to reuse the same structure for later mechanisms.

**Alternatives considered**: Keep adding one-off benchmark folders per mechanism, store all benchmark inputs in one flat dataset directory, or let manifests and tracked datasets live together without a stronger boundary.

**Why this path won**: A family-first layout matches the evaluation-question structure more closely than a mechanism-first pile. It also makes bilingual handling clearer by separating `en`, `zh`, and `shared` tracks at the package level, while keeping source-book inventories and corpus-selection manifests in their own manifest territory.

**What changed in the system**: The stable evaluation doc now defines dataset-organization rules for `excerpt_cases`, `chapter_corpora`, `runtime_fixtures`, and `compatibility_fixtures` under `reading-companion-backend/eval/datasets/`. The repo now also has tracked family roots and manifest roots under `reading-companion-backend/eval/manifests/` for source-book inventories, corpus manifests, split manifests, and local-path references.

**Why it matters later**: This is the storage rule that should keep future benchmark work reproducible and comparable across mechanisms. It also prevents the first `attentional_v2` benchmark package shape from becoming an accidental one-off that later mechanisms have to work around.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/eval/datasets/README.md`
- `reading-companion-backend/eval/manifests/README.md`
- `docs/implementation/new-reading-mechanism/evaluation-dataset-layout.md`

## Entry 19
**ID**: DEC-019
**Status**: active

**Decision / Inflection**: Mirror the family-first evaluation dataset layout under a local-only package territory for private books instead of forcing copyrighted inputs into tracked benchmark packages.

**Period**: Late March 2026, when the first serious private-book supplement from the user's local Downloads corpus entered `attentional_v2` evaluation planning.

**Problem**: The project already had a stable tracked dataset layout under `eval/datasets/`, but that layout alone was not enough once private contemporary books became part of the evaluation plan. We needed a way to use those books for excerpt, chapter, and runtime packages without quietly checking copyrighted source text into the repo or losing the same family-first structure that later evaluation code should rely on.

**Alternatives considered**: Keep all benchmark packages tracked and hope contributors avoid private books, store private excerpt/chapter packages in ad hoc local folders without a stable rule, or avoid using valuable local books entirely and limit the benchmark corpus to public-domain sources.

**Why this path won**: A local-only mirror keeps the legal and storage boundary honest while preserving the same package contract across tracked and private benchmark inputs. That lets the project benefit from richer modern books without making future evaluation code depend on a second informal layout.

**What changed in the system**: Stable docs now reserve `reading-companion-backend/state/eval_local_datasets/` as the local-only mirror for excerpt, chapter, runtime, and compatibility packages derived from private books. Tracked manifests under `reading-companion-backend/eval/manifests/` now explicitly cover both local source-book references and local dataset-package references, while tracked `eval/datasets/` remains the home for repo-safe benchmark packages.

**Why it matters later**: This is the rule that lets the benchmark corpus grow beyond public-domain books without making the repo itself a dumping ground for copyrighted text. Later contributors need to know that "private local package" is a first-class evaluation territory, not an ad hoc exception.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/workspace-overview.md`
- `docs/backend-sequential-lifecycle.md`
- `reading-companion-backend/AGENTS.md`
- `docs/implementation/new-reading-mechanism/evaluation-corpus-requirements.md`

## Entry 17
**ID**: DEC-020
**Status**: active

**Decision / Inflection**: Move mechanism-private reading artifacts under `_mechanisms/<mechanism_key>/` and reserve top-level `public/` plus `_runtime/` for shared cross-mechanism state.

**Period**: Late March 2026, immediately after the shared substrate extraction.

**Problem**: Even after `book_document.json` became the canonical parsed-book substrate, iterator-specific artifacts such as `structure.json`, `reader_memory.json`, checkpoints, and `book_analysis` outputs still lived in shared-looking top-level directories. That kept the output tree visually and semantically blurred, making it too easy for future contributors to mistake mechanism-private artifacts for universal runtime truth.

**Alternatives considered**: Keep the mixed top-level layout and rely on naming discipline alone, duplicate artifacts into both shared and mechanism-specific paths, or postpone output-layout cleanup until a second reader mechanism was already live.

**Why this path won**: Namespacing mechanism-private artifacts under `_mechanisms/<mechanism_key>/` finishes the same boundary that `reading_core` and `reading_runtime` were designed to create. It keeps shared product/runtime surfaces obvious, gives each mechanism room for its own derived structures and runtime state, and preserves backward compatibility through helper-based fallback instead of messy duplicate writes.

**What changed in the system**: `iterator_v1` now writes derived section structure to `_mechanisms/iterator_v1/derived/structure.json`, private runtime memory/checkpoints/plan state to `_mechanisms/iterator_v1/runtime/`, and secondary analysis artifacts to `_mechanisms/iterator_v1/internal/`. Shared helpers still resolve older shared-path and flat legacy artifacts on read, but new writes use the namespaced canonical layout. Normal runs no longer persist normalized eval bundles; explicit eval runs may write `_mechanisms/iterator_v1/exports/normalized_eval_bundle.json`.

**Why it matters later**: This is the artifact-layout decision that keeps future multi-mechanism work from collapsing back into top-level iterator assumptions. Later contributors need to know that top-level `public/` and `_runtime/` are shared shell territory, while `_mechanisms/` is where mechanism ontology, checkpoints, diagnostics, and optional eval exports belong.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/artifacts.py`
- `reading-companion-backend/src/iterator_reader/storage.py`
- `reading-companion-backend/src/iterator_reader/iterator.py`
- `reading-companion-backend/src/reading_mechanisms/iterator_v1.py`
- `docs/backend-sequential-lifecycle.md`
- `docs/backend-state-aggregation.md`

## Entry 18
**ID**: DEC-021
**Status**: active

**Decision / Inflection**: Split backend reading documentation into a shared mechanism-platform doc plus per-mechanism docs.

**Period**: Late March 2026, after the shared runtime, substrate, and artifact boundaries were already established.

**Problem**: The repo already needed to support multiple reader mechanisms, but the documentation still treated `docs/backend-reading-mechanism.md` as if one file could be both the shared platform authority and the full internal authority for the current default mechanism. That shape would have made future mechanism docs either second-class notes or would have silently universalized `iterator_v1` concepts such as `section` and `subsegment`.

**Alternatives considered**: Keep one shared mechanism doc and let it grow appendices for every mechanism, hard-rename the existing doc into `iterator_v1` immediately and replace it everywhere, or keep future mechanism designs only in research notes until implementation.

**Why this path won**: Keeping `docs/backend-reading-mechanism.md` as the shared platform/router doc preserves one stable shared entrypoint, while a dedicated `docs/backend-reading-mechanisms/` folder gives each mechanism equal documentary standing. That makes design-only mechanisms visible early, keeps shared boundaries clean, and prevents one mechanism's ontology from becoming implicit backend law.

**What changed in the system**: `docs/backend-reading-mechanism.md` now owns only shared mechanism-platform rules, status model, and doc routing. `docs/backend-reading-mechanisms/README.md` now owns the mechanism catalog and authoring rules. `docs/backend-reading-mechanisms/iterator_v1.md` now owns the live mechanism internals that previously lived in the shared doc, and `docs/backend-reading-mechanisms/attentional_v2.md` records the future design as a stable `design-only` mechanism doc.

**Why it matters later**: This is the documentation boundary that should keep future multi-mechanism work legible. Later contributors need to know which facts are shared platform rules, which facts belong to one mechanism, and how to add a new mechanism doc without re-centering the whole repo on the current default reader.

**Primary evidence**:
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/README.md`
- `docs/backend-reading-mechanisms/iterator_v1.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `AGENTS.md`
- `reading-companion-backend/AGENTS.md`

## Entry 19
**ID**: DEC-022
**Status**: active

**Decision / Inflection**: Split prompt ownership by boundary instead of keeping one global live prompt bank.

**Period**: Late March 2026, after the shared mechanism/runtime boundaries and the multi-mechanism doc split were already in place.

**Problem**: The repo still kept live parse, reader, book-analysis, shared fragment, and legacy prompt text together in one global `src/prompts/templates.py` module. That was workable while there was effectively one active reader, but it blurred which prompts belonged to a mechanism, which belonged to a reusable capability, and which fragments were truly shared infrastructure.

**Alternatives considered**: Keep the global prompt bank and rely on naming discipline, build a global cross-mechanism prompt registry, or postpone prompt ownership cleanup until a second live mechanism was already implemented.

**Why this path won**: Prompt ownership now matches the backend architecture. Shared fragments stay in `src/prompts/`, capability prompts such as `book_analysis` stay in capability-scoped modules, and mechanism-private prompts live with the mechanism implementation that owns them. That keeps future prompt work local to the reader or capability it actually changes, while the old `templates.py` can survive temporarily as a compatibility shim instead of remaining the canonical source of truth.

**What changed in the system**: Shared language/query fragments moved into `src/prompts/shared.py`. `iterator_v1` parse and reader prompts moved into `src/iterator_reader/prompts.py` with a typed `IteratorV1PromptSet`. `book_analysis` prompts moved into `src/prompts/capabilities/book_analysis.py` with a typed `BookAnalysisPromptSet`. Legacy unused prompt families moved into `src/prompts/legacy.py`. The current mechanism adapter now selects prompt bundles explicitly, and the old `src/prompts/templates.py` only re-exports from the new modules for migration compatibility.

**Why it matters later**: This is the prompt-boundary decision that keeps multi-mechanism work from collapsing back into one giant global template file. Later contributors need to know that prompt dispatch happens by mechanism or capability ownership, not by editing a universal prompt bank every time a reader changes.

**Primary evidence**:
- `reading-companion-backend/src/prompts/shared.py`
- `reading-companion-backend/src/prompts/capabilities/book_analysis.py`
- `reading-companion-backend/src/prompts/legacy.py`
- `reading-companion-backend/src/iterator_reader/prompts.py`
- `reading-companion-backend/src/reading_mechanisms/iterator_v1.py`
- `reading-companion-backend/src/prompts/templates.py`

## Entry 20
**ID**: DEC-023
**Status**: active

**Decision / Inflection**: Expand `book_document.json` from paragraph-only shared truth into a paragraph-plus-sentence canonical substrate.

**Period**: March 2026, during the first `attentional_v2` implementation phases.

**Problem**: The backend had already separated `book_document.json` from `iterator_v1`'s derived `structure.json`, but the shared substrate still stopped at paragraph records. That was enough for section-first readers, but not for a sentence-order mechanism that needs stable sentence ids, precise anchors, bounded look-back, and honest resume/reconstitution inputs without borrowing another mechanism's private splitter.

**Alternatives considered**: Keep sentence splitting entirely mechanism-private, create a second shared sentence artifact parallel to `book_document.json`, or force future mechanisms to derive their own sentence cursors from paragraph-only substrate at runtime.

**Why this path won**: Sentence order is substrate, not `attentional_v2`-only ontology. Extending `book_document.json` preserves one shared parsed-book truth while giving future mechanisms a stable chapter-local sentence inventory with grounded locators. Keeping the sentence layer parse-time and mechanism-neutral also avoids making `iterator_v1`'s `section` or `subsegment` logic the accidental universal authority for sentence-level reading.

**What changed in the system**: `src/reading_core/book_document.py` now models sentence records and locator character offsets. Parse flow now writes sentence inventories into each chapter of `public/book_document.json`, and load/build helpers backfill missing sentence layers into older paragraph-only documents when they are reloaded. `attentional_v2`'s Phase 1 scaffold also now rests on a real shared sentence substrate instead of on a planned placeholder.

**Why it matters later**: This is the substrate change that makes sentence-order mechanisms possible without introducing a second shared text authority. Future contributors will need to know that sentence ids and sentence-span locators belong to the canonical book document, even though current public surfaces may still remain section-shaped for compatibility.

**Primary evidence**:
- `reading-companion-backend/src/reading_core/book_document.py`
- `reading-companion-backend/src/reading_core/sentences.py`
- `reading-companion-backend/src/iterator_reader/parse.py`
- `docs/backend-reading-mechanism.md`
- `docs/backend-state-aggregation.md`

## Entry 21
**ID**: DEC-024
**Status**: active

**Decision / Inflection**: Keep `attentional_v2`'s v1 search design fully represented, but make search a rare escape hatch instead of a normal reading behavior.

**Period**: March 2026, during Phase 5 of the first `attentional_v2` implementation push.

**Problem**: The mechanism design explicitly included separate knowledge-use and search-policy state, but the implementation still had to choose whether version one would become search-heavy, silently defer real search to a later redesign, or preserve the full design while keeping the reading mind text-grounded.

**Alternatives considered**: Remove real search from v1 entirely and treat it as future-only, make search a common loop action whenever curiosity appeared, or collapse search decisions into the broader prior-knowledge mode instead of giving them their own state machine.

**Why this path won**: The project's core value is the visible reading mind, not a research reflex. Preserving `no_search`, `defer_search`, and `search_now` as real states keeps the design intact, but making `no_search` the normal posture protects the text-grounded reading direction. `defer_search` captures genuine curiosity without interrupting the read, while `search_now` survives only as a narrow escape hatch for identity-critical references or obscure allusions that would make continued reading less honest.

**What changed in the system**: `attentional_v2` now has a real knowledge-activation lifecycle, a conservative search-policy helper, and a Phase 5 `bridge_resolution` layer that judges earlier source anchors over a deterministic candidate set. The mechanism also now writes durable anchor-memory updates, typed anchor relations, motif and unresolved-reference indexes, trace links, and bridge move history instead of leaving those behaviors as prompt-only intentions.

**Why it matters later**: This is the decision that should stop future contributors from accidentally turning `attentional_v2` into a search-first reader while still preserving the original design's full control surface. It also marks the point where Phase 5 stopped being a design promise and became real durable state behavior in code.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/knowledge.py`
- `reading-companion-backend/src/attentional_v2/bridge.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/open-questions.md`

## Entry 22
**ID**: DEC-025
**Status**: active

**Decision / Inflection**: Make mechanism-authored anchored reactions the durable Phase 6 source of truth, and treat current chapter/API shapes as compatibility projections.

**Period**: March 2026, during Phase 6 of the first `attentional_v2` implementation push.

**Problem**: The new mechanism design says the durable visible object is an anchored reaction, but the existing app still depends on section-shaped chapter results, current reaction cards, integer reaction ids, and mark lookup through persisted chapter payloads. The implementation needed a way to preserve the original thought object without breaking future compatibility work.

**Alternatives considered**: Store only current chapter-result reaction cards and treat them as truth, re-key marks on anchors instead of reactions, or postpone durable reaction truth until after all top-layer/API redesign work.

**Why this path won**: A dual-layer model preserves the product's real value. The mechanism now owns the original anchored reaction record, while the current chapter-result-style envelope becomes a compatibility projection derived from that truth. That keeps history append-only, lets reconsolidation create later linked thoughts instead of mutating earlier ones, and avoids letting current section-shaped transport fields silently redefine the mechanism's ontology.

**What changed in the system**: `attentional_v2` now writes a `reaction_records.json` runtime ledger, has Phase 6 node contracts for `reflective_promotion`, `reconsolidation`, and `chapter_consolidation`, and can project mechanism-authored reactions into a mechanism-private current-contract chapter-result compatibility payload. Reconsolidation now produces append-and-link records, and chapter-end slow-cycle helpers can cool pressure, carry forward live questions, promote reflective summaries, and optionally emit a chapter-level anchored reaction.

**Why it matters later**: This is the historical-integrity boundary for the new mechanism. Future contributors need to know that `section_ref` and similar fields are compatibility sidecars, not the source of truth, and that earlier persisted reactions must remain immutable even when later reading materially changes their meaning.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/open-questions.md`

## Entry 23
**ID**: DEC-026
**Status**: active

**Decision / Inflection**: Make `attentional_v2` resume bounded, chapter-local, and explicitly reconstructive instead of silently restoring large hidden hot-state windows.

**Period**: March 2026, during Phase 7 of the first `attentional_v2` implementation push.

**Problem**: The mechanism design required warm, cold, and reconstitution resume, but the implementation still had to choose how much source text each mode should reread, where continuity should be persisted, and how to preserve the identity of the same reading mind without pretending a reconstructed state was the same thing as a truly warm in-memory continuation.

**Alternatives considered**: Restore all hot state as if it were still warm, reread large unbounded source tails to fake continuity, or leave resume semantics implicit until a later live runner existed.

**Why this path won**: A bounded chapter-local resume policy preserves honesty. `warm_resume` keeps reread at zero, `cold_resume` rebuilds near-term continuity from a small source window, and `reconstitution_resume` uses a larger but still capped current-chapter window tied to recent meaning units instead of hidden cross-chapter rereads. Persisting compact local continuity plus resume metadata also makes it explicit when hot state was reconstructed rather than warmed.

**What changed in the system**: `attentional_v2` now persists `local_continuity.json` and `resume_metadata.json`, writes full mechanism checkpoints alongside shared thin checkpoint summaries, and exposes helper functions for warm, cold, and reconstitution resume. The default reader policy now encodes the concrete reread window contract, and non-warm resume marks reconstructed hot state explicitly instead of silently treating it as warm continuity.

**Why it matters later**: This is the resume-honesty boundary for the new mechanism. Future contributors need to know that persisted slow-cycle state, not hidden large rereads, is the primary source of continuity, and that any non-warm rebuild must remain visible as a reconstruction rather than a perfect continuation.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/open-questions.md`

## Entry 24
**ID**: DEC-027
**Status**: active

**Decision / Inflection**: Treat section-era public fields as temporary compatibility sidecars and begin the public migration toward locus- and anchor-native `attentional_v2` surfaces.

**Period**: March 2026, during the first Phase 8 shared-surface integration pass.

**Problem**: The product had already decided that future frontend/API surfaces should not keep chapter `section` as the long-term primary container, because not every reading mechanism has that ontology. At the same time, the current routed frontend, chapter views, and marks pages still depended heavily on `section_ref` / `segment_ref`.

**Alternatives considered**: Keep the public model section-first indefinitely, break the current frontend immediately in favor of a new non-section contract, or hide `attentional_v2`'s richer locus/anchor truth until a later all-at-once rewrite.

**Why this path won**: An additive migration preserves product honesty without forcing a destabilizing rewrite. The backend can now expose the mechanism's real reading locus and anchored thought structure directly enough for future product work, while still serving the current section-era frontend through compatibility sidecars. This keeps the top layer closer to mechanism-authored truth without pretending the full frontend migration is already done.

**What changed in the system**: Public schemas and payload shaping now additively expose `reading_locus`, `primary_anchor`, `related_anchors`, `supersedes_reaction_id`, `move_type`, and runtime-shell-backed active reaction references on analysis-state, activity, chapter, and mark payloads. `section_ref` / `segment_ref` remain in place for compatibility, but the stable docs now describe them as migration-era sidecars rather than the future public ontology.

**Why it matters later**: This entry records the moment the project explicitly chose a de-sectionized long-term direction for new mechanisms without forcing an immediate frontend break. Future contributors will need this context to understand why both section-era fields and richer anchor/locus fields coexist for a while, and why later work still needs to redesign chapter/detail and marks around chapter text plus anchored reactions.

**Primary evidence**:
- `reading-companion-backend/src/api/schemas.py`
- `reading-companion-backend/src/library/catalog.py`
- `reading-companion-backend/src/library/user_marks.py`
- `docs/api-contract.md`
- `docs/backend-state-aggregation.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`

## Entry 25
**ID**: DEC-028
**Status**: active

**Decision / Inflection**: Split `attentional_v2` observability into thin standard runtime history and optional debug-only diagnostics.

**Period**: March 2026, during the later Phase 8 observability pass.

**Problem**: The mechanism now had enough runtime state, resume behavior, and shared-surface projection that observability could no longer stay implicit. The project needed enough default traceability for trustworthy resume, public/runtime history, and evaluation, but persisting all controller/candidate/prompt internals on every run would have inflated storage and blurred the product-facing trace.

**Alternatives considered**: Keep all observability thin and shared even if evaluation and diagnosis became weak, persist all controller forensics by default in the shared runtime path, or postpone the split until a live end-to-end runner existed.

**Why this path won**: A two-tier observability model preserves both runtime honesty and implementation discipline. Shared `_runtime/` artifacts and public-facing activity now remain thin enough to represent real product/runtime history, while mechanism-private full checkpoints keep resume-correctness state, and deeper controller forensics stay in optional debug-only diagnostics. This matches the broader `mechanism-authored core, shell-authored envelope` direction instead of letting debug needs redefine the runtime shell.

**What changed in the system**: `reader_policy.logging` now explicitly records `observability_mode` plus standard/debug logging toggles. Shared `runtime_shell.json` and checkpoint summaries now carry `observability_mode`. Checkpoint writes and resume restores now emit standard shared activity events, while debug-mode diagnostics continue under `_mechanisms/attentional_v2/internal/diagnostics/events.jsonl`. Stable docs now also distinguish standard evaluation evidence from optional debug forensics.

**Why it matters later**: This is the project’s first explicit observability boundary for a future non-default mechanism. Future contributors will need this context to understand why standard traces should be sufficient for baseline evaluation and trustworthy resume, why full checkpoints remain standard-private instead of public, and why deep controller forensics should remain optional rather than silently becoming the default runtime posture.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/reading_runtime/shell_state.py`
- `docs/backend-state-aggregation.md`
- `docs/backend-reader-evaluation.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`

## Entry 26
**ID**: DEC-029
**Status**: active

**Decision / Inflection**: Promote `attentional_v2` from a design-only scaffold to an experimental end-to-end mechanism behind the shared runtime shell.

**Period**: March 2026, during the Phase 8.5 live-runner integration pass.

**Problem**: The project had already landed sentence substrate, node contracts, slow-cycle state, resume helpers, observability, and eval exports, but `attentional_v2` still was not honestly live. Parse and read entrypoints still needed to run through shared provisioning, CLI `--mechanism`, async job launch/resume/recovery, and non-iterator compatibility aggregation without pretending `iterator_v1`'s `structure.json` was universal.

**Alternatives considered**: Keep `attentional_v2` marked design-only until the later evaluation corpus existed, fork more of `iterator_v1`'s job/runtime wiring into a second silo, or universalize the old mechanism's reader mind instead of extracting only the neutral lifecycle and provisioning helpers.

**Why this path won**: The backend direction is one shared runtime shell with multiple mechanism-specific reading minds. The right move was to extract mechanism-neutral provisioning and job plumbing into shared runtime helpers, keep mechanism ontology private, and then let `attentional_v2` run end to end as an experimental non-default mechanism. That preserves `iterator_v1` as default, keeps the public HTTP contract stable, and records that unsupported legacy `book_analysis` behavior should fail explicitly rather than by accident.

**What changed in the system**: Shared canonical provisioning now routes through `src/reading_runtime/`. Internal job launchers, resume, auto-resume, and incompatible fresh rerun now preserve `mechanism_key` with runtime-shell precedence. `AttentionalV2Mechanism()` is registered as a built-in experimental mechanism, `parse_book` and `read_book` are real entrypoints, CLI `--mechanism attentional_v2` is functional, and the backend can build manifests, analysis-state, chapter results, and marks-compatible payloads for non-iterator runs without requiring `iterator_v1` structure.

**Why it matters later**: This is the inflection point where `attentional_v2` stopped being a design promise and became a real backend runtime path. Future contributors need to know that experimental does not mean design-only anymore, that mechanism selection continuity across recovery now matters, and that the remaining work shifted from “make it runnable” to “evaluate it honestly and migrate the product surfaces intentionally.”

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/provisioning.py`
- `reading-companion-backend/src/library/jobs.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/reading_mechanisms/attentional_v2.py`
- `docs/backend-sequential-lifecycle.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/README.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`

## Entry 27
**ID**: DEC-030
**Status**: active

**Decision / Inflection**: Treat benchmark quality as a first-class evaluation concern and require dual diagnosis plus packet-based human review for high-impact case hardening.

**Period**: March 2026, immediately after the first corrected `attentional_v2` `mechanism_integrity` run on the tracked curated `v2` excerpt family.

**Problem**: The first serious local benchmark pass proved that the new bilingual excerpt benchmark family was viable, but it also showed that some weak results could plausibly come from benchmark-case design or harness behavior rather than the mechanism alone. Without an explicit rule, future work could overfit to mislabeled or under-reviewed cases and mistake benchmark weakness for mechanism weakness.

**Alternatives considered**: Treat the versioned curated dataset as de facto ground truth after the first full run, rely on ad hoc chat-based human feedback when a case looked suspicious, or keep all hardening inside LLM-only case-audit prompts without a durable human-review loop.

**Why this path won**: Evaluation needs stronger discipline than "run benchmark, trust score." The project now distinguishes factual dataset truth from reviewable benchmark judgment targets, requires dual diagnosis of mechanism versus dataset/harness problems, and adds a lightweight packet-based human review loop that works on the shared local machine without a frontend website. This keeps the benchmark executable and fast while making it much harder for weak cases to quietly steer the mechanism in the wrong direction.

**What changed in the system**: Stable evaluation docs now include a dataset trust model and the dual-diagnosis rule, the backend agent guide reminds coding agents not to blame mechanism or benchmark by default, and the backend now ships export/import tooling for packet-based benchmark review under `eval/review_packets/`. The temp implementation docs now record the full dataset-hardening method and the specific packet workflow for excerpt-case review and reimport.

**Why it matters later**: This is the point where dataset quality stopped being implicit benchmark hygiene and became an explicit project rule. Future contributors need this context to understand why some evaluation work now pauses for case hardening, why builder-curated cases are not automatically treated as final ground truth, and why packet-based human review exists even though there is no frontend review tool.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/AGENTS.md`
- `docs/implementation/new-reading-mechanism/dataset-quality-hardening.md`
- `reading-companion-backend/eval/attentional_v2/export_dataset_review_packet.py`
- `reading-companion-backend/eval/attentional_v2/import_dataset_review_packet.py`
- `reading-companion-backend/eval/review_packets/README.md`

## Entry 28
**ID**: DEC-031
**Status**: active

**Decision / Inflection**: Replace manual packet review with multi-prompt LLM adjudication as the operational default for current benchmark hardening.

**Period**: March 2026, during the first dataset-hardening loop after the initial weak-case packets were created.

**Problem**: The benchmark hardening workflow had become executable, but in practice it still depended on scarce human review time. That made the review loop the new bottleneck and risked leaving the benchmark in a half-hardened state where the project knew weak cases existed but could not clear them quickly enough to keep evaluation moving.

**Alternatives considered**: Keep manual review as the default blocker, let the dataset builder make ad hoc untracked judgments in chat, or rely only on the earlier primary/adversarial case-audit prompts without a distinct final adjudication step.

**Why this path won**: The project needed an operational reviewer that was independent enough from the builder logic to reduce self-confirming drift, but still executable without manual review bandwidth. The chosen answer was a multi-prompt LLM review stack: primary case audit, adversarial disagreement audit, and a separate final adjudication pass that writes packet decisions back into the dataset under `llm_reviewed`. Manual human review remains possible later for higher-trust promotion work, but it is no longer the default blocker for current packet hardening.

**What changed in the system**: Stable evaluation docs and the backend agent guide now say that multi-prompt LLM adjudication is the default packet reviewer until explicitly reversed. Packet imports now preserve `review_origin` and `review_policy`, datasets now distinguish `llm_reviewed` from `human_reviewed`, and the first round of weak-case packets was imported under the new rule. The hardening loop now freezes reviewed slices based on `reviewed_active` cases rather than waiting on manual packet completion.

**Why it matters later**: Future contributors need to know that the project deliberately traded human-review dependence for an explicit multi-prompt LLM review policy, not because human review became worthless, but because current benchmark hardening needed to remain executable. Without this context, later readers could misinterpret `llm_reviewed` slices as accidental stopgaps rather than the official operational review state for this period.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/AGENTS.md`
- `docs/implementation/new-reading-mechanism/dataset-quality-hardening.md`
- `reading-companion-backend/eval/attentional_v2/import_dataset_review_packet.py`
- `reading-companion-backend/eval/attentional_v2/auto_review_packet.py`
- `reading-companion-backend/eval/review_packets/README.md`

## Entry 29
**ID**: DEC-032
**Status**: active

**Decision / Inflection**: Promote project-owned LLM invocation, provider/profile policy, and trace emission into one shared backend layer.

**Period**: March 2026, during the benchmark-hardening side branch for universal LLM invocation and traceability.

**Problem**: The backend had accumulated multiple prompt-to-provider paths: iterator-specific helpers, eval scripts with direct provider clients, and a newer packet-audit tracing path that only covered one review workflow. That made failover policy, model-profile policy, and LLM traceability inconsistent across runtime and evaluation work. It also made the new packet-audit observability improvements look like a local tool instead of a backend capability.

**Alternatives considered**: Keep provider logic inside `src/iterator_reader/llm_utils.py` and patch more call sites around it, let each eval script keep its own provider client as long as it used the same API key, or support broad silent cross-model fallback for resilience.

**Why this path won**: The project needed one explicit invocation boundary that could separate operational concerns from semantic ones. A shared backend layer made it possible to keep same-model key failover as an operational fallback while forbidding silent cross-model switching inside one runtime or evaluation run. It also made task-level model policy concrete: cheaper/stabler runtime profiles, stronger pinned judge profiles, and explicit optional cross-model disagreement only when deliberately invoked. Centralizing trace emission also made runtime and eval observability comparable without requiring every mechanism or script to reinvent it.

**What changed in the system**: `src/reading_runtime/` now owns a structured provider/profile registry, contract adapters for `anthropic`, `google_genai`, and `openai_compatible`, one shared invocation gateway, and standard/debug trace helpers. The legacy iterator helper path is now a compatibility wrapper over that gateway. Runtime/eval call sites for packet audits, packet adjudication, integrity judging, `attentional_v2`, `iterator_v1`, and one-off comparison helpers now run through the shared layer. Backend setup now includes a registry example file plus env guidance for provider-specific secrets and task-level profiles.

**Why it matters later**: Future contributors need to know that failover policy, model choice, and traceability are now platform concerns, not mechanism-local conveniences. Without this entry, later readers could mistake the profile split between runtime and judge paths for ad hoc tuning, or reintroduce direct provider clients that silently bypass the shared trace contract.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/llm_registry.py`
- `reading-companion-backend/src/reading_runtime/llm_gateway.py`
- `reading-companion-backend/src/iterator_reader/llm_utils.py`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reader-evaluation.md`
- `README.md`

## Entry 30
**ID**: DEC-033
**Status**: active

**Decision / Inflection**: Treat reviewed-slice hardening plus mechanism repair as the gate for broader semantic comparison, then explicitly unblock chapter-scale comparison once the repaired reviewed slice generalized.

**Period**: Late March 2026, after the bilingual hardening and reviewed-slice expansion rounds, through repair pass 2.

**Problem**: The project had reached the point where `attentional_v2` was runnable and benchmarkable, but the first serious local excerpt results still mixed benchmark weakness with mechanism weakness. Moving straight into chapter-scale cross-mechanism comparison too early would have risked comparing architectures on a half-hardened benchmark and then overreacting to whatever the first broad results happened to say.

**Alternatives considered**: Start broader comparison as soon as the first reviewed slice existed, keep delaying broader comparison until every weak local case was repaired, or tune the mechanism directly against the still-small early reviewed slice without first proving that repairs generalized.

**Why this path won**: The project needed one explicit gate between local benchmark trust-building and broader comparison. The chosen rule was: harden the excerpt benchmark until the reviewed slice is meaningful, run narrowly targeted repair passes against the clearly weak local behaviors, then rerun the full reviewed slice. Only once that rerun showed strong generalization would broader chapter-scale comparison be unblocked. This protected the project from both premature broad claims and endless local overfitting.

**What changed in the system**: The tracker and handoff now record benchmark hardening as an explicit gating lane rather than a side chore. The project ran bilingual `4+4` hardening, bilingual `6+6` reviewed-slice expansion, a first reviewed-slice floor check, two mechanism-repair passes, and then a repaired full reviewed-slice rerun before allowing broader chapter comparison to proceed. The resulting first chapter-core comparison then produced split evidence instead of a flat win/loss story: `iterator_v1` remained stronger on English chapter-local reading, while `attentional_v2` was stronger on span trajectory overall and especially in Chinese.

**Why it matters later**: This is the historical hinge between “make the new mechanism evaluable” and “compare it honestly at chapter scale.” Later contributors need to know that broader semantic comparison was not simply delayed or rushed by instinct; it was explicitly gated by benchmark hardening and repaired-slice generalization, and the first broad comparison produced mixed evidence rather than a simplistic promotion signal.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/dataset-quality-hardening.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- `docs/agent-handoff.md`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_integrity_reviewed_slice_round3_repair_pass2_20260326/summary/report.md`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_en_round1_20260326/summary/report.md`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_vs_iterator_v1_chapter_core_zh_round1_20260326/summary/report.md`

## Entry 31
**ID**: DEC-034
**Status**: active

**Decision / Inflection**: Turn the modern private-library supplement into the formal benchmark-diversification and growth lane, instead of leaving copyright-restricted nonfiction as an ad hoc local side pool.

**Period**: Late March 2026, after the `/Users/baiweijiang/Documents/BOOK` batch was merged with the earlier private local books.

**Problem**: The tracked public/open benchmark family had become strong enough for first serious evaluation, but it was still skewed toward older public-domain material and literary/nonfiction mixes that did not reflect the user's actual reading priorities. The project needed a way to widen genre coverage toward modern business, management, biography, history, science, and other nonfiction without pretending that copyrighted books could live in the tracked repo dataset.

**Alternatives considered**: Keep relying on the public/open corpus as the main long-term benchmark source, add modern private books only opportunistically when a specific gap appeared, or treat the private books as useful local reading material but not as a formal benchmark-growth lane.

**Why this path won**: The project needed both breadth and honesty. A local-only supplement preserves copyright boundaries while still letting the benchmark grow in the directions that matter for real reading quality. Formalizing the supplement as its own manifest-backed source pool also keeps the process reproducible: ingest, fingerprint, parse, screen, package, then promote into the formal benchmark through balanced curation instead of ad hoc cherry-picking.

**What changed in the system**: The repo now treats the combined private library as a first-class local-only source family with source manifests, local refs, corpus manifests, split manifests, and generated local-only dataset packages. The current combined pool contains the newly supplied `/Users/baiweijiang/Documents/BOOK` titles plus the earlier private books, and the execution plan now includes a frozen round-1 promotion-preparation pass to lift balanced English/Chinese chapter and excerpt candidates from that supplement into the next formal curation/review cycle. The category strategy also shifted explicitly toward a more diversified benchmark mix, with special weight on business, management, and biography.

**Why it matters later**: This is the moment where benchmark growth stopped meaning “find more public-domain books” and started meaning “grow a diversified bilingual benchmark family across tracked public sources and local-only modern sources.” Later contributors need this context to understand why local-only manifests and package families exist, why modern nonfiction expansion is now part of the main evaluation roadmap, and why benchmark size and genre coverage are expected to grow together.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/modern-nonfiction-expansion-booklist.md`
- `docs/implementation/new-reading-mechanism/private-library-promotion-round1.md`
- `docs/implementation/new-reading-mechanism/private-library-promotion-round1-execution.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- `reading-companion-backend/eval/manifests/source_books/attentional_v2_private_library_screen_v2.json`
- `reading-companion-backend/eval/manifests/local_refs/attentional_v2_private_library_v2.json`

## Entry 32
**ID**: DEC-035
**Status**: active

**Decision / Inflection**: Make evaluation preserve portable strengths and repeatable failures, not only winner/loser conclusions.

**Period**: Late March 2026, after the first broader chapter-core comparison made the split result concrete.

**Problem**: The evaluation process had become strong enough to identify mixed results across mechanisms, but a plain winner/loser summary was not enough to support later mechanism synthesis. If the project only remembered which mechanism won each scope, it would lose the more valuable design memory: which local reading habits were genuinely strong, which chapter-scale accumulation behaviors were worth carrying forward, and which failures should not be repeated.

**Alternatives considered**: Keep comparison results mostly as run artifacts plus prose interpretation, store only high-level winner summaries in the tracker, or leave strength/failure extraction to later ad hoc chat reconstruction when synthesis work starts.

**Why this path won**: The project is not trying to preserve two permanently separate reader tribes. It is trying to build a better reader over time. That means evaluation must preserve both adoption candidates and anti-pattern memory. Turning this into an explicit rule keeps strong observed behaviors portable across mechanisms and keeps repeated mistakes visible before they re-enter future prompt, retrieval, memory, or controller work.

**What changed in the system**: Stable evaluation docs now require meaningful comparison and repair passes to preserve both positive adoption candidates and negative anti-patterns. The backend agent guide now reminds coding agents not to stop at winner/loser language when a run exposes transferable strengths or repeatable mistakes. The implementation workspace now also has a dedicated mechanism-pattern ledger that records concrete strengths, adoption candidates, failure modes, evidence links, and adoption status.

**Why it matters later**: This is the policy that makes later synthesis work possible without relying on fragile memory. Future contributors should be able to look back and answer not only "who won this run?" but also "what should survive into the next mechanism?" and "what must not be repeated?"

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/AGENTS.md`
- `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- `docs/agent-handoff.md`

## Entry 33
**ID**: DEC-036
**Status**: active

**Decision / Inflection**: Require each meaningful evaluation round to close the loop from result -> causal interpretation -> selective implementation or explicit deferment, instead of treating the ledger as a passive archive.

**Period**: Late March 2026, after the first broader comparison had already produced usable causal findings and the project recognized the risk of letting them pile up faster than they were absorbed.

**Problem**: The project had already created a stronger evaluation memory system by preserving strengths, anti-patterns, and causal findings. But that improvement carried a new risk: the ledger could become a large graveyard of good ideas and warnings that never shaped the active mechanism soon enough to matter. That would weaken context, delay learning, and make later synthesis feel like a one-time salvage exercise instead of a live engineering loop.

**Alternatives considered**: Keep the ledger as a long-term reference only, rely on future ad hoc synthesis passes to decide what to implement, or immediately copy every attractive behavior from the winning mechanism into the approved one.

**Why this path won**: The project needed a middle path between passive note-taking and mechanical feature-merging. The chosen rule is: every meaningful evaluation round should identify likely contributing causes, choose a small number of high-value actions that fit the currently approved mechanism, and either implement them promptly or record a concrete defer reason. This preserves context while avoiding two opposite mistakes: waiting too long to absorb real lessons, and copying behaviors without respecting the approved mechanism's framework.

**What changed in the system**: Stable evaluation docs now define an evaluation-to-implementation rule plus a selective synthesis rule. Root and backend agent guides now require agents to go beyond storing findings in docs: they must investigate what contributed to the result, convert high-confidence findings into selective implementation actions or explicit defer reasons, and preserve the approved mechanism's framework when carrying strengths forward. The mechanism-pattern ledger now carries dispositions and next actions rather than only descriptive findings.

**Why it matters later**: Future contributors need to know that evaluation memory is now operational, not archival. A later reader should be able to reconstruct not just what the project learned, but how those lessons were filtered, when they were acted on, and why some attractive ideas were deferred or rejected as misaligned.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/AGENTS.md`
- `AGENTS.md`
- `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md`

## Entry 34
**ID**: DEC-037
**Status**: active

**Decision / Inflection**: Add a durable registry for long-running eval and dataset background jobs so agent handoffs no longer depend on chat memory.

**Period**: Late March 2026, after repeated multi-minute and multi-hour evaluation runs made agent changes and overlapping reruns harder to manage safely.

**Problem**: The project increasingly relied on long-running offline work such as chapter comparison reruns, packet audits, packet adjudication, and dataset-construction passes. Those runs often lasted far longer than one chat turn or one active agent session. Without a durable job registry, later agents had to infer what was still running from scattered chat history, half-written handoff notes, or raw process output. That made it too easy to duplicate work, lose check commands, or forget what decision a still-running job was supposed to inform.

**Alternatives considered**: Keep relying on `docs/agent-handoff.md` plus informal chat summaries, reuse the product-runtime `state/jobs/` records even though they describe user-upload analysis jobs rather than offline eval work, or leave long-running eval jobs untracked except for their run directories.

**Why this path won**: The project needed a lightweight but durable workflow boundary for agent-owned offline work. A separate background-job registry keeps product runtime jobs and offline evaluation jobs distinct while still giving future agents one source of truth for what is running, what should be checked next, and what decision the job belongs to. Pairing the machine-readable registry with a generated human summary preserves handoff readability without forcing agents to hand-edit dynamic state into docs.

**What changed in the system**: Backend infrastructure now includes a shared background-job registry helper plus two scripts: one to create/update/archive job records and one to refresh and inspect them. The registry lives under `reading-companion-backend/state/job_registry/`. This entry's original `active_jobs.json` authority model was later superseded by `DEC-056`, which made per-job records under `jobs/<job_id>.json` canonical and left `active_jobs.json` / `active_jobs.md` as derived active-only mirrors. Workspace and backend agent rules now require jobs expected to run longer than roughly `10-15` minutes to be registered, and require later agents to refresh the registry before starting overlapping long-running work.

**Why it matters later**: Future contributors will otherwise see the registry files and helper scripts without understanding why the project chose a separate eval/agent job ledger instead of overloading product runtime jobs. This entry records that the registry exists to preserve task linkage, check commands, and decision context across agent changes, not simply to list processes.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/background_job_registry.py`
- `reading-companion-backend/scripts/register_background_job.py`
- `reading-companion-backend/scripts/check_background_jobs.py`
- `docs/backend-reader-evaluation.md`
- `docs/agent-handoff.md`
- `AGENTS.md`
- `reading-companion-backend/AGENTS.md`

## Entry 35
**ID**: DEC-038
**Status**: active

## Entry 36
**ID**: DEC-056
**Status**: active

**Decision / Inflection**: Realign Phase 9 evaluation into separate local excerpt and bounded long-span surfaces instead of forcing one benchmark family to answer every remaining reader-quality question.

**Period**: Early April 2026, after the clustered benchmark v1 freeze and the completed human-notes-guided excerpt reviewed freeze made the mismatch between local and accumulation surfaces explicit.

**Problem**: The project had already built two strong but differently shaped dataset lines. The clustered benchmark v1 was good for fast iteration and preserved a frozen `chapter_core`, but its chapter surface was still too coupled to the same texts as the excerpt surface and too pressure-imbalanced to remain the sole design center for `coherent_accumulation`. Meanwhile the human-notes-guided line had become highly efficient and credible for local excerpt evaluation, but its chapter-facing structures were cluster-shaped rather than a ready-made decisive chapter benchmark. Treating all three kept north-star dimensions as if they required one shared text surface was starting to blur the real evaluation questions.

**Alternatives considered**: Keep the clustered benchmark as the one active surface for chapter and excerpt work, promote the notes-guided line wholesale into the active benchmark pointer, or postpone local judged evaluation until a new universal benchmark family could be built.

**Why this path won**: The project needed to separate “what kind of reading span is being tested?” from “what kind of output value is being judged?”. `selective_legibility` fits a local excerpt surface where many cases can be reused per read. `coherent_accumulation` fits a bounded long-span window surface where continuity, carryover, and callback pressure are actually visible. `insight_and_clarification` is not a third span family; it is an orthogonal output-value axis that can score both local and long-span cases. This split lets the project start judged local eval immediately while building a better-fitting long-span benchmark in parallel.

**What changed in the system**: Stable evaluation docs now state that excerpt/local and long-span/window are separate evaluation surfaces. `coherent_accumulation` is now interpreted operationally as bounded long-span continuity and carryover rather than generic whole-book memory. The completed human-notes-guided excerpt reviewed freeze is now treated as a real runnable local eval surface. A new bounded long-span namespace, `attentional_v2_accumulation_benchmark_v1`, becomes the next dataset-construction lane, with `window_cases` and `accumulation_probes` rather than plain chapter rows. Clustered benchmark v1 remains preserved and readable, but it is no longer the sole design center for the next accumulation dataset.

**Why it matters later**: Future contributors should not assume that “one benchmark” always means “one text surface for every reader-quality question.” This decision records that the project deliberately chose better-fit surfaces over forced uniformity, while still keeping the resulting evaluation strategy bounded and interview-legible.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

**Decision / Inflection**: Make new runtime and evaluation processes concurrency-adaptive by default instead of relying on fixed worker counts inside individual scripts.

**Period**: Late March 2026, after the project had already introduced a structured LLM registry and identified case-level serial execution as a major source of wasted eval time.

**Problem**: Independent cases, packet reviews, and benchmark comparisons were still leaving throughput on the table because worker widths were hardcoded per runner, while the shared LLM layer already had enough structure to manage concurrency centrally. This made speed tuning inconsistent and encouraged local flags instead of one coherent default policy.

**Alternatives considered**: Keep adding runner-local `--max-workers` overrides while leaving defaults conservative, require multiple API keys before allowing real parallelism, or continue treating each script's fixed worker count as the main safety mechanism.

**Why this path won**: The project needed one place to own same-key parallelism, adaptive backoff, and default worker sizing. A shared adaptive budget makes new jobs faster by default while still preserving one explicit safety boundary for rate limits, timeouts, and malformed responses.

**What changed in the system**: Structured registry entries now carry explicit concurrency-policy fields, the shared gateway adapts provider-wide same-key concurrency for new processes, and major eval/review runners derive their default case fanout from a shared job-concurrency helper instead of fixed `1` or `2` worker defaults. `iterator_v1` background segmentation defaults are also now derived from the runtime budget unless explicit env overrides are present.

**Why it matters later**: Future contributors will otherwise see higher default parallelism and multiple thread pools across the codebase without understanding that this was an intentional system-wide redesign, not a set of unrelated speed tweaks.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/llm_gateway.py`
- `reading-companion-backend/src/reading_runtime/llm_registry.py`
- `reading-companion-backend/src/reading_runtime/job_concurrency.py`
- `docs/backend-reader-evaluation.md`
- `docs/runtime-modes.md`

## Entry 36
**ID**: DEC-039
**Status**: active

**Decision / Inflection**: Unify product and offline long-running jobs under one canonical registry while keeping public product job/status behavior stable.

**Period**: Late March 2026, after a completed English chapter-core eval run was misclassified as `abandoned` because the registry relied too heavily on optional status files.

**Problem**: The project had two separate job systems: product reading jobs under `state/jobs/` and offline eval/dataset jobs under `state/job_registry/active_jobs.json`. That split made storage authority ambiguous, forced some jobs to “serve the registry” by writing explicit completion markers, and let successful offline runs fall through to `abandoned` when they exited cleanly without a status file.

**Alternatives considered**: Keep the split system and only tighten the `abandoned` heuristic, push all lifecycle responsibility into individual job scripts, or expose a brand-new public API job model in the same pass.

**Why this path won**: The project needed one canonical job ledger that could observe both product and offline work, infer terminal state from objective evidence, and still leave public product routes untouched. A unified per-job registry under `state/job_registry/jobs/` keeps one source of truth for pid, exit code, runtime state, logs, and success evidence, while compatibility shadows and API mapping avoid a disruptive frontend change.

**What changed in the system**: Canonical job records now live under `reading-companion-backend/state/job_registry/jobs/<job_id>.json` for both product reading jobs and offline eval/dataset jobs. `active_jobs.json` and `active_jobs.md` became derived operator-facing mirrors rather than the primary store. Product `state/jobs/<job_id>.json` remains a compatibility shadow during the migration window. The registry now infers `completed` from successful outputs/checks even without a status file, narrows `abandoned` to genuinely orphaned cases, and adds a wrapper-first launcher for generic offline jobs.

**Why it matters later**: Future contributors will otherwise see both `state/jobs/` and `state/job_registry/` and assume the split is still intentional. This entry records that the system has one canonical job store now, that `abandoned` is intentionally rare, and that wrapper-based observation should be the default for generic long-running jobs.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/background_job_registry.py`
- `reading-companion-backend/src/library/jobs.py`
- `reading-companion-backend/scripts/run_registered_job.py`
- `docs/runtime-modes.md`
- `docs/backend-sequential-lifecycle.md`
- `docs/backend-reader-evaluation.md`

## Entry 37
**ID**: DEC-040
**Status**: active

**Decision / Inflection**: Establish a repo-first agent-switching memory system with canonical current-state and task-router docs.

**Period**: Late March 2026, after the workspace had already accumulated strong stable docs, a detailed initiative tracker, and a durable job registry but still lacked one canonical repo-local switching surface.

**Problem**: The project was already fairly handoff-friendly, but live status still had to be reconstructed from several places: stable docs for rules, `docs/agent-handoff.md` for temporary summaries, initiative trackers for detailed progress, and the job registry for mutable runtime truth. That made agent switching possible, but slower and more drift-prone than it needed to be.

**Alternatives considered**: Keep relying on the existing handoff note plus initiative trackers, move current state authority into an external tool such as Notion, or let each coding agent invent its own working-memory convention.

**Why this path won**: A repo-first switching system keeps the workflow tool-agnostic and Git-traceable. Markdown remains the human-facing layer, JSON remains the machine-facing layer, and shell commands remain the common interface across Codex, Claude Code, Gemini CLI, and other agents. Adding canonical current-state and task-router docs closes the gap between stable truths and live work without replacing the detailed tracker or job-registry infrastructure that already holds the evidence.

**What changed in the system**: The workspace now has a source-of-truth map, a canonical `docs/current-state.md` with a machine-readable appendix, a workspace task registry in Markdown plus JSON, and two new commands: `make agent-context` and `make agent-check`. Root onboarding docs now route active work through the current-state/task layer, and `docs/agent-handoff.md` is reduced to session-only scratch space. Decision-log entries now also carry stable IDs plus lifecycle status so live task records can point to historical decisions directly.

**Why it matters later**: Future contributors and agents should now be able to switch in without chat history, recover the current objective quickly, trace any task to its detailed tracker and evidence, and trust that mutable job status still lives only in the job registry. This is the point where agent switching becomes an explicitly designed repo capability rather than a side effect of good documentation habits.

**Primary evidence**:
- `docs/source-of-truth-map.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `scripts/print-agent-context.py`
- `scripts/check-agent-traceability.py`
- `AGENTS.md`

## Entry 38
**ID**: DEC-041
**Status**: active

**Decision / Inflection**: Shift local LLM operator setup from provider-first registry editing to named model targets plus profile bindings.

**Period**: Late March 2026, after the shared LLM layer had already centralized invocation, retry, cooldown, tracing, and adaptive concurrency but the editing surface still made multi-provider local setup awkward.

**Problem**: The shared LLM platform had become strong enough to support multiple providers, URLs, models, and pooled credentials, but the main local editing surface still exposed that power as one provider-first registry. In practice this made a simple operator question harder than it should have been: “where do I write the URL, model name, and key for this concrete target, and where do I decide which project profile uses it?” The older shape was workable for one provider or one compatibility file, but it became harder to edit safely once runtime, packet review, and evaluation judging could point at different endpoints or key pools.

**Alternatives considered**: Keep recommending the single provider/profile registry as the main editing path, fall back to env-only configuration for local secrets and target swapping, or redesign the gateway and call sites around a brand-new runtime abstraction instead of compiling a clearer operator surface into the existing registry.

**Why this path won**: The project needed a better operator experience without destabilizing the shared runtime policy layer. Splitting local setup into named targets plus profile bindings makes editing clearer: one file owns endpoint identity and credentials, the other owns project-role assignment and profile-level invocation settings. Compiling those files back into the existing provider/profile registry keeps the shared gateway, retry, cooldown, tracing, and concurrency logic intact while making multi-provider local configuration easier to reason about and safer to edit.

**What changed in the system**: The backend now supports `LLM_TARGETS_PATH` / `LLM_PROFILE_BINDINGS_PATH` plus inline JSON variants as the preferred structured local setup. Operators can define named targets in `reading-companion-backend/config/llm_targets.local.json`, bind stable project profile ids in `reading-companion-backend/config/llm_profile_bindings.local.json`, and keep those real local files untracked under `config/*.local.json`. The registry layer now compiles the new target/binding format into the existing internal provider/profile model, supports direct raw keys or env-backed credentials inside one neutral key-slot pool, and preserves the older `LLM_REGISTRY_PATH` / `LLM_REGISTRY_JSON` and legacy single-provider env fallback as compatibility modes.

**Why it matters later**: Future contributors will otherwise see both the target/binding files and the older registry files and assume the duplication is accidental. This entry records that the shared LLM platform itself still centers on one compiled registry and one gateway, while the local operator-facing surface intentionally changed to make endpoint/model/key editing and profile assignment clearer in multi-provider setups.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/llm_registry.py`
- `reading-companion-backend/src/config.py`
- `reading-companion-backend/config/llm_targets.local.example.json`
- `reading-companion-backend/config/llm_profile_bindings.local.example.json`
- `reading-companion-backend/config/llm_registry.minimax_legacy_compatible.json`
- `README.md`
- `docs/backend-reader-evaluation.md`

## Entry 39
**ID**: DEC-042
**Status**: active

**Decision / Inflection**: Make profile routing tier-based and scope-pinned so target selection stays universal while each run keeps one consistent model/provider.

**Period**: Late March 2026, after the project had already moved local setup to named targets plus profile bindings and needed a cleaner answer to “primary now, backup only when headroom is not enough.”

**Problem**: The target-first editing model solved where operators write URLs, model names, and keys, but profile routing still leaned too much on one selected target plus fallback semantics that looked provider-specific and could still be interpreted as call-by-call failover. That was not a good fit for evaluation and dataset-review quality, where one scope should keep one model identity, and it was not a good long-term fit for future non-MiniMax primary/backup combinations.

**Alternatives considered**: Keep one hardcoded primary target plus provider-style fallback fields, move target switching into each individual call, or redesign the gateway around a brand-new planner layer instead of refining the existing profile-binding model.

**Why this path won**: Ordered target tiers keep the operator surface simple and universal. One profile can now express “prefer this pool, then that pool” without baking MiniMax-specific rules into the shared platform. Scope-start target selection preserves semantic consistency because runtime, packet review, and evaluation scopes now choose one concrete target up front and stay pinned to it, while same-target key-slot failover remains available inside that chosen target.

**What changed in the system**: `llm_profile_bindings.local.json` now supports ordered `target_tiers`, legacy `target_id` / `fallback_target_ids` compile into tiers for compatibility, and the shared gateway resolves one concrete target when an invocation scope starts. The gateway records the selected target/tier plus override reason in traces, supports temporary operator pins with `LLM_FORCE_TARGET_ID` and `LLM_FORCE_TIER_ID`, and only considers backup tiers when a new scope begins or when manual overrides request them. The current three shared profiles now all follow the same two-tier policy: prefer `MiniMax-M2.7-highspeed`, then fall back to `MiniMax-M2.7` when the primary tier cannot carry the required stable concurrency or is under quota pressure.

**Why it matters later**: Future contributors will otherwise see tier metadata, pinned-target trace fields, and override env vars without understanding why the project did not keep simpler per-call fallback. This entry records that the platform intentionally separates two concerns: within-target key failover can happen during a run, but cross-target model/provider choice is a scope-start decision so review and evaluation semantics stay stable.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/llm_registry.py`
- `reading-companion-backend/src/reading_runtime/llm_gateway.py`
- `reading-companion-backend/tests/test_llm_gateway.py`
- `reading-companion-backend/config/llm_profile_bindings.local.example.json`
- `README.md`
- `docs/backend-reader-evaluation.md`

## Entry 40
**ID**: DEC-043
**Status**: active

**Decision / Inflection**: Introduce a managed library-inbox plus source-catalog layer as the default operator path for future dataset-source additions.

**Period**: Late March 2026, after the dataset platform was re-scoped from one-pass corpus building toward a full closed build-review-refine loop.

**Problem**: The project already had a durable source library under `state/library_sources/` and strong parse/package/review machinery, but future private-library growth still depended too much on hard-coded external roots such as `/Users/.../BOOK` and `~/Downloads`. That made book addition workable for one-off rescue passes, but too brittle for the closed-loop automation target where future case mining, review, and regeneration should all consume one project-owned source of truth.

**Alternatives considered**: Keep relying on the existing hard-coded external roots, store future books only in chat or ad hoc local paths until the smart builder was ready, or jump directly to a full dataset orchestrator before defining a stable source-intake surface.

**Why this path won**: The shortest safe path was to land the source-governance foundation first. A managed inbox plus source catalog gives operators one simple workflow for future book additions while preserving the existing durable source-library convention. It also keeps provenance lightweight: filename, hash, batch, canonical path, and status are enough for repeatable automation without turning dataset work into paperwork.

**What changed in the system**: The backend now recognizes `state/library_inbox/` as the operator drop-zone for future books, `state/library_sources/` remains the canonical managed copy territory, and `state/dataset_build/` now stores the durable source catalog and intake-run summaries. The operator contract was later simplified further to one inbox folder instead of separate language/visibility folders: language is auto-resolved, `visibility` is optional sidecar metadata, and new sources default to private/local-only storage unless explicitly marked public. The CLI at `reading-companion-backend/eval/attentional_v2/ingest_library_sources.py` plus the root `make library-source-intake` command copies inbox books into canonical paths, reads optional sidecar metadata, writes `source_catalog.json` / `source_catalog.md`, and records per-run summaries. The current private-library supplement builder was then rewired to consume that managed source catalog and canonical `state/library_sources/` copies instead of reaching back to `/Users/.../BOOK` or `~/Downloads`. This is still Phase 1 only: it does not replace screening, smart case mining, or packet review, but it gives those later phases a stable source-input layer that current supplement refreshes already use.

**Why it matters later**: Future contributors will otherwise see `state/library_inbox/`, `state/dataset_build/`, and the new intake CLI as incidental clutter. This entry records that they are part of the deliberate dataset-platform direction: the project now expects future source additions to enter through a managed intake layer before parse/screen/build/review automation takes over.

**Primary evidence**:
- `reading-companion-backend/eval/attentional_v2/ingest_library_sources.py`
- `reading-companion-backend/tests/test_source_intake.py`
- `scripts/library-source-intake.sh`
- `README.md`
- `reading-companion-backend/AGENTS.md`
- `docs/workspace-overview.md`
- `docs/source-of-truth-map.md`
- `docs/implementation/new-reading-mechanism/dataset-platform-closed-loop.md`

## Entry 41
**ID**: DEC-044
**Status**: active

**Decision / Inflection**: Make Phase 2 of the dataset platform explicitly question-aligned case construction, and postpone the full unattended controller until those construction artifacts stabilize.

**Period**: Late March 2026, after managed source intake and catalog wiring had already landed and the next dataset-platform question became how to build stronger evaluation cases instead of merely automating the old heuristic builder.

**Problem**: The project already had strong source intake, parsing, screening, packaging, and packet-review machinery, but its weakest layer was still semantic case construction. The current excerpt path in `corpus_builder.py` was still heavily shaped by fixed windows, role tags, and chapter-position heuristics. At the same time, the phrase "smart builder" was too vague to guide implementation well. If the project jumped directly into an unattended loop, it would risk automating today's weaker heuristics instead of automating a genuinely stronger benchmark-construction method.

**Alternatives considered**: Keep the vague "smart builder" label and continue iterating heuristics informally, jump directly to the full unattended dataset loop before the new construction artifacts existed, or replace the current builder with a single monolithic LLM pass that handled source mining and dataset packaging together.

**Why this path won**: The project needed a clearer Phase 2 contract before more automation. `Question-Aligned Case Construction` names the real job: build cases because they answer explicit evaluation questions under judgeable conditions. It preserves the current deterministic strengths, introduces semantic intermediate artifacts such as target profiles and opportunity cards, and gives the future unattended loop a stable contract to orchestrate. Designing the loop boundary now is enough to avoid rework; fully designing the controller later avoids hardening the wrong semantics too early.

**What changed in the system**: The implementation workspace now treats Phase 2 as `Question-Aligned Case Construction` instead of `smart target-case mining`. The new design doc defines target profiles, opportunity cards, case assembly, adequacy reporting, and the deterministic-vs-LLM ownership split. The active dataset-platform task was renamed to match that design direction. The unattended loop remains a Phase 3 concern, but its artifact boundary is now explicitly defined: Phase 2 must emit stable target-profile, opportunity-card, reserve/replacement, and adequacy-report artifacts before the full unattended controller is finalized.

**Why it matters later**: Future contributors will otherwise see the automation goal and assume the next step was simply "make the builder autonomous." This entry records that the intended sequence is more deliberate: first build a stronger question-aligned semantic construction layer, then automate that stronger layer. It also records that Phase 3 should orchestrate stable construction artifacts instead of implicitly defining them.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/question-aligned-case-construction.md`
- `docs/implementation/new-reading-mechanism/dataset-platform-closed-loop.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Entry 42
**ID**: DEC-045
**Status**: active

**Decision / Inflection**: Stop treating public/private as a primary dataset-platform organizing rule; keep it only as compatibility metadata while the project optimizes for product quality, automation, and speed.

**Period**: Late March 2026, after the managed inbox, source catalog, and first question-aligned supplement landing had already clarified that the main product bottlenecks were case quality and automation rather than source-distribution handling.

**Problem**: The dataset platform had already simplified operator intake to one inbox folder, but `visibility` still leaked into canonical source paths, generated source ids, and parts of the dataset-platform narrative as if public/private distribution were a first-class product concern. That added friction and made future automation look more complicated than the actual product goal required. The project's immediate goal is stronger reader evaluation data and faster closed-loop improvement, not distribution packaging.

**Alternatives considered**: Keep the current visibility split everywhere because old manifests used it, remove all visibility metadata immediately and migrate every historical manifest/path, or build a heavier dual-track public/private architecture before the unattended loop landed.

**Why this path won**: The best tradeoff was to simplify the live platform without forcing a risky migration. New managed copies now use one language-rooted source tree, default generated source ids no longer bake visibility into the identifier, and the current managed supplement loader no longer treats visibility as its primary admission gate. Historical dataset ids, manifests, and older `/private/` paths still work, but they are explicitly compatibility baggage rather than the design center.

**What changed in the system**: `reading-companion-backend/eval/attentional_v2/ingest_library_sources.py` now treats `visibility` as optional compatibility metadata, writes new canonical copies under `state/library_sources/<language>/`, and generates default source ids as `<canonical_stem>_<language>`. `reading-companion-backend/eval/attentional_v2/build_private_library_supplement.py` now loads managed source records without filtering them by visibility. Stable docs and current-state/task routing now say explicitly that future dataset-platform work should optimize around managed-source quality and automation rather than around public/private branching. Historical `private_library` naming remains in some dataset ids and manifests for continuity with existing evidence.

**Why it matters later**: Future contributors would otherwise keep reintroducing public/private branching into primary jobs just because those words still existed in older ids and manifests. This entry records the intended rule clearly: unless a task is explicitly about distribution, export policy, or legacy recovery, public/private should stay in the background and must not slow the main product-quality and automation lanes.

**Primary evidence**:
- `reading-companion-backend/eval/attentional_v2/ingest_library_sources.py`
- `reading-companion-backend/eval/attentional_v2/build_private_library_supplement.py`
- `reading-companion-backend/tests/test_source_intake.py`
- `reading-companion-backend/tests/test_private_library_supplement.py`
- `README.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/implementation/new-reading-mechanism/dataset-platform-closed-loop.md`
- `docs/implementation/new-reading-mechanism/question-aligned-case-construction.md`

## Entry 43
**ID**: DEC-046
**Status**: active

**Decision / Inflection**: Land the dataset-platform controller as a scratch-safe bounded closed loop first, and keep the full unattended multi-iteration scheduler deferred until real scratch runs validate the new construction artifacts.

**Period**: Late March 2026, after question-aligned case construction had landed in code and the next practical problem became how to automate build-review-import work without touching live benchmark truth prematurely.

**Problem**: The project wanted to move quickly toward full dataset automation, but the new question-aligned builder was still fresh and the live `v2` review-truth datasets remained valuable feedback truth. A direct jump to a fully unattended multi-iteration scheduler would have mixed two risks together at once: weak semantic construction and unbounded control-loop behavior. The system needed a way to validate end-to-end build-review-import automation safely, without overwriting live manifests or live dataset ids.

**Alternatives considered**: Keep automation at the design-doc level only until every later scheduler detail was specified, let the new builder write directly into the live dataset ids and tracked manifests during validation, or build an entirely separate parallel builder instead of refactoring the current managed supplement path.

**Why this path won**: The safest fast path was a bounded scratch-safe controller. The existing managed supplement builder now resolves a run-scoped namespace when asked, so scratch validation runs can write manifests and build artifacts under `state/dataset_build/build_runs/<run_id>/` while still using normal local dataset package conventions through unique scratch dataset ids. The new `run_closed_loop_benchmark_curation.py` controller then reuses the proven packet-review machinery instead of replacing it: initial candidate review is exported with `--only-unreviewed`, bounded repair reuses `run_dataset_review_pipeline.py`, and the run stops with a final summary instead of silently crossing into promotion or cutover decisions.

**What changed in the system**: `reading-companion-backend/eval/attentional_v2/build_private_library_supplement.py` now has a reusable scratch-safe mode with run-scoped ids, manifests, and build summaries. `reading-companion-backend/eval/attentional_v2/run_closed_loop_benchmark_curation.py` plus the root `make closed-loop-benchmark-curation` surface now orchestrate the first bounded closed loop: construct scratch datasets, export initial review packets, audit, adjudicate, import, optionally run one repair wave, refresh the queue summary, and emit a final stop-and-summarize report. The task registry and current-state docs now treat this as an active dataset-platform lane rather than a purely queued future idea.

**Why it matters later**: Future contributors might otherwise assume the only meaningful automation step was a final always-on unattended scheduler. This entry records the intended staging clearly: first prove the question-aligned builder and bounded controller on isolated scratch runs, then widen the scheduler only after real evidence shows the new artifacts are trustworthy enough to automate aggressively.

**Primary evidence**:
- `reading-companion-backend/eval/attentional_v2/build_private_library_supplement.py`
- `reading-companion-backend/eval/attentional_v2/run_closed_loop_benchmark_curation.py`
- `reading-companion-backend/tests/test_private_library_supplement.py`
- `reading-companion-backend/tests/test_closed_loop_benchmark_curation.py`
- `README.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/question-aligned-case-construction.md`
- `docs/implementation/new-reading-mechanism/dataset-platform-closed-loop.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

## Entry 44
**ID**: DEC-047
**Status**: active

**Decision / Inflection**: Treat the dataset builder as a bounded enabling system, and make frozen-slice comparison cadence the rule that pulls the project back to the main evaluation goal.

**Period**: Late March 2026, after the question-aligned builder and bounded closed-loop controller had both landed and the main project risk shifted from missing infrastructure to infrastructure drift.

**Problem**: The repo now had real dataset-platform capabilities: managed source intake, question-aligned case construction, packetized review, and a scratch-safe controller. But those wins created a new risk. Without an explicit strategy rule, the project could keep refining the builder, packet audits, and automation breadth indefinitely, while decisive mechanism-eval lanes such as durable-trace / re-entry and runtime viability stayed queued. The original goal is still cross-mechanism judgment and a stronger reading mechanism, not a perpetually improving builder.

**Alternatives considered**: Keep treating builder progress as the implicit main mission until the dataset felt "good enough," force an immediate stop to dataset-platform work regardless of unresolved benchmark blockers, or leave the balance as an informal chat-only norm instead of writing it into the docs.

**Why this path won**: The best tradeoff was to keep dataset-platform work but bound it tightly. Builder and packet-hardening work remain necessary whenever they remove a specific evaluation blocker or shorten time-to-next-comparison, but they are no longer allowed to expand by default. Once a benchmark slice is good enough for diagnosis, the next move is frozen-slice comparison cadence rather than another open-ended builder wave. This also preserves the distinction between "good enough for diagnosis" and "good enough for final cutover confidence."

**What changed in the system**: The stable evaluation methodology now says explicitly that dataset building, dataset hardening, and automation are enabling lanes rather than independent success targets. The dataset-platform implementation docs now describe the current work as bounded hardening focused only on callback-bridge excerpt shaping and same-input audit/adjudication reproducibility. Current-state and task-routing docs now say the next default move after one bounded repair wave is to freeze a slice and hand comparison cadence back to the mechanism-eval lane, while durable-trace / re-entry and runtime-viability work remain visible as decisive pending evaluation lanes.

**Why it matters later**: Future contributors might otherwise see the large amount of dataset-platform infrastructure and assume the project was still primarily trying to perfect the builder before resuming evaluation. This entry records the intended discipline clearly: infrastructure exists to serve mechanism comparison, and frozen-slice comparison cadence is the rule that prevents infrastructure drift.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/dataset-platform-closed-loop.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

## Entry 45
**ID**: DEC-048
**Status**: active

**Decision / Inflection**: Replace the older broad `40 / 40` formal benchmark as the active Phase 9 benchmark pointer with a four-chapter clustered benchmark v1, and treat the older broad freeze as historical evidence only.

**Period**: Early April 2026, after the eval scope had already been reduced to three north-star dimensions and the project had enough builder/review infrastructure to stop widening blindly.

**Problem**: The project still needed serious mechanism evidence, but the broad formal benchmark shape was too slow for fast iteration. Too many excerpt judgments were effectively paying for whole-chapter reads one at a time across a wide book spread. That made the path back to the next mechanism decision too slow, while also encouraging continued dataset growth as a substitute for evaluation. The project needed a benchmark shape that stayed honest and reviewable but got much more value out of each chapter read.

**Alternatives considered**: Keep the broad formal freeze as the active benchmark and simply rerun it more patiently, keep expanding the broad benchmark until it felt unquestionably large enough, or hand-design a brand-new review stack just for clustered evaluation instead of reusing the existing builder and packet-review machinery.

**Why this path won**: The clustered shape makes one chapter read support many excerpt judgments, which is exactly the right tradeoff under the current time and cost posture. Four carefully chosen chapters preserve language balance and meaningful pressure variety while making the benchmark far more iteration-friendly and easier to explain in an interview. Reusing the existing question-aligned builder, audit, adjudication, and import pipeline also keeps the system legible: the change is in benchmark shape and clustered duplicate control, not in inventing a second review universe.

**What changed in the system**: The active benchmark pointer now lives in `attentional_v2_clustered_benchmark_v1_draft.json` plus `clustered-benchmark-v1-draft.md`. The builder gained clustered mode with explicit chapter whitelisting, multiple same-profile cases per chapter, stronger same-chapter dedup rules, and ranked same-profile ids such as `__seed_1` and `__reserve_1`. The excerpt comparison runner now defaults to the clustered manifest. The earlier broad formal freeze remains preserved in the repo, but the later formal decisive chapter/excerpt jobs were abandoned once the active pointer changed. A real smoke build over the four chosen chapters produced `24 + 24` primary candidates and `8 + 8` reserves, and the first bilingual review wave was launched directly from that clustered scratch output.

**Why it matters later**: Future contributors will otherwise see both the broad formal freeze and the clustered benchmark and wonder whether the latter was just an experiment. This entry records that the swap was deliberate. The active benchmark is now optimized for fast iteration and interview-legible mechanism evidence, while the broader formal freeze remains as recoverable historical evidence rather than as the live decision surface.

**Primary evidence**:
- `reading-companion-backend/eval/manifests/splits/attentional_v2_clustered_benchmark_v1_draft.json`
- `docs/implementation/new-reading-mechanism/clustered-benchmark-v1-draft.md`
- `reading-companion-backend/eval/attentional_v2/question_aligned_case_construction.py`
- `reading-companion-backend/eval/attentional_v2/build_private_library_supplement.py`
- `reading-companion-backend/eval/attentional_v2/run_excerpt_comparison.py`
- `reading-companion-backend/state/dataset_build/build_runs/clustered_benchmark_v1_smoke2_20260403/build_summary.json`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Entry 46
**ID**: DEC-049
**Status**: active

**Decision / Inflection**: Rejudge long-span source fit before freezing accumulation v1, and prefer genuinely continuous books plus compact note-backed windows over topical collections or weakly connected essay/talk surfaces.

**Period**: April 4, 2026, after the first accumulation review packet returned `0 keep / 10 revise / 8 drop`.

**Problem**: The first bounded long-span draft had enough harness support to run, but it still mixed good and bad source/window choices. The review packet showed a pattern that was too strong to ignore: many failures were not “the mechanism cannot accumulate,” but “this window does not actually carry forward one live thread.” `纳瓦尔宝典` windows fragmented into topical advice blocks, and the current `走出唯一真理观` window kept topic-shifting inside one chapter. If the project had simply repaired judge wording on top of that old window set, it would have locked a weak accumulation surface into Phase 9.

**Alternatives considered**: Keep the old six-window draft and only tweak probe wording, widen immediately to a fresh English long-span builder wave around new books such as `Shoe Dog`, or pause long-span work until a perfect broad benchmark existed.

**Why this path won**: The project needed a bounded but honest middle path. It now keeps only window/source pairs that are already materializable from current reviewed excerpt support and aligned human notes, while demoting the clearly weak source-fit windows. That preserves momentum and runtime efficiency without pretending the old draft was sound. The first reserve for later widening is now `shoe_dog_private_en`, but it stays a reserve because adding it cleanly would require new excerpt/window support construction rather than a small repair.

**What changed in the system**: `attentional_v2_accumulation_benchmark_v1` now rebuilds around six rejudged windows:
- `supremacy_private_en__13`
- `steve_jobs_private_en__17`
- `value_of_others_private_en__8_10`
- `xidaduo_private_zh__13_15`
- `huochu_shengming_de_yiyi_private_zh__8`
- `huochu_shengming_de_yiyi_private_zh__13_16`

The old active windows `nawaer_baodian_private_zh__wealth`, `nawaer_baodian_private_zh__judgment`, and `zouchu_weiyi_zhenliguan_private_zh__14` are demoted from long-span v1. The accumulation builder also now emits cleaner single-vs-cross-chapter judge focus and non-duplicative prior-context payloads before the rebuilt first-review lane runs again.

**Why it matters later**: Future contributors could easily look at the old packet and conclude only that “accumulation is hard.” This entry preserves the more useful lesson: long-span evaluation depends heavily on source/window fit, and a good accumulation surface often comes from compact multi-chapter continuity or one genuinely long chapter, not from whatever text happened to already be in a benchmark.

**Primary evidence**:
- `reading-companion-backend/eval/review_packets/archive/accumulation_benchmark_v1_probe_first_review_20260404/dataset_review_pipeline_summary.json`
- `reading-companion-backend/eval/review_packets/archive/accumulation_benchmark_v1_probe_first_review_20260404/llm_review_report.md`
- `reading-companion-backend/eval/attentional_v2/accumulation_benchmark_v1.py`
- `reading-companion-backend/eval/manifests/splits/attentional_v2_accumulation_benchmark_v1_draft.json`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

## Entry 47
**ID**: DEC-050
**Status**: active

**Decision / Inflection**: Separate global local-ceiling configuration from per-process launch budgets, and make comparison work artifact-staged (`bundle -> judge -> merge`) so eval restarts become an explicit ETA-gated choice instead of a blunt kill-and-rerun habit.

**Period**: April 5, 2026, after the first personal-key judged excerpt rerun was already in flight and the project needed higher utilization without losing control of one-key contention.

**Problem**: The software still had two different bottlenecks mixed together. One was artificial: local target/profile ceilings were still low enough that the runtime could self-throttle far below the practical key budget. The other was structural: excerpt and accumulation comparison work still behaved like one monolithic batch, so partial progress was hard to reuse and “should we restart?” had to be argued from intuition instead of from reusable artifacts plus measured throughput.

**Alternatives considered**: Keep the low local ceilings and only tune runner-local worker flags, add a hard in-gateway RPM limiter plus a cross-process coordinator immediately, or restart the in-flight judged rerun blindly as soon as the staged runner landed.

**Why this path won**: The project needed a bounded but real lift. Raising the global ceiling removes the purely local software bottleneck. Per-process caps preserve deliberate budgeting without inventing a heavier coordinator too early. The staged runner shape then makes restart decisions concrete: bundle work, case judgments, and merge outputs can be measured and resumed independently. That lets the project use a recorded ETA gate instead of killing expensive in-flight work on hope alone.

**What changed in the system**: Local target/profile ceilings were raised substantially, while new per-process env caps now clamp `runtime_reader_default`, `dataset_review_high_trust`, and `eval_judge_high_trust` budgets per launched Python process. `run_excerpt_comparison.py` and `run_accumulation_comparison.py` now both support staged/sharded execution with explicit shard ownership, `--skip-existing`, and merge-only summary emission. Lightweight `llm_usage.json` summaries are now written for shard/run observability. A short `run_llm_capacity_probe.py` path now validates software-side concurrency without involving reader-quality judgment. The first dual-heavy excerpt smoke then established a concrete gate outcome: the new runner architecture is valid, but the in-flight old judged rerun should continue because the observed throughput gain was not large enough to overcome already-sunk work plus the recorded `90` minute restart rule.

**Why it matters later**: Future contributors will otherwise see very high local ceilings, per-process cap envs, staged comparison CLIs, and a deliberately preserved old-format run all at once and assume the posture is inconsistent. This entry records the intended rule: keep the software ceiling high, budget each launched process explicitly, make comparison work resumable by artifact, and restart only when measured ETA evidence actually justifies it.

**Primary evidence**:
- `reading-companion-backend/config/llm_targets.local.json`
- `reading-companion-backend/config/llm_profile_bindings.local.json`
- `reading-companion-backend/src/reading_runtime/llm_registry.py`
- `reading-companion-backend/src/reading_runtime/llm_gateway.py`
- `reading-companion-backend/eval/attentional_v2/run_excerpt_comparison.py`
- `reading-companion-backend/eval/attentional_v2/run_accumulation_comparison.py`
- `reading-companion-backend/eval/attentional_v2/llm_usage_summary.py`
- `reading-companion-backend/eval/attentional_v2/run_llm_capacity_probe.py`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_excerpt_parallel_smoke_20260405/shards/smoke_dual_heavy/summary/llm_usage.json`
- `reading-companion-backend/eval/runs/attentional_v2/llm_capacity_probe_personal_20260405/summary/llm_usage.json`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

## Entry 48
**ID**: DEC-051
**Status**: active

**Decision / Inflection**: Supersede the in-flight monolithic personal-key local excerpt rerun and restart the decisive local lane under the staged/sharded runner, using one shared run root with disjoint shard ownership.

**Period**: April 5, 2026, immediately after the first restart gate had temporarily favored preserving the old rerun, but before that rerun had produced reusable judged evidence.

**Problem**: The initial ETA-gate call assumed the old personal-key rerun had already banked enough progress that restarting would waste too much time. Later inspection showed that assumption was wrong. The old run had only started `attentional_v2`, had touched only `2` units, and had not yet produced reusable staged bundles, case payloads, or summary outputs. At the same time, the staged smoke plus raw traces had already shown that the remaining bottleneck was heavy mechanism workload rather than provider/profile/quota waits. Keeping the old run would therefore preserve the slowest possible execution shape while protecting very little sunk value.

**Alternatives considered**: Continue letting the monolithic rerun crawl forward, buy a faster key before changing the launch posture, or restart under the new runner but still keep work inside one large shard.

**Why this path won**: The project's real objective was time-first decisive evidence, not loyalty to sunk progress. Once the old run was shown to have almost no reusable outputs, the earlier gate no longer reflected reality. The staged runner already had explicit shard ownership, resumable shard-local outputs, process-level budget caps, and healthy no-wait gateway evidence. Restarting into two disjoint shards therefore created meaningful unit-level and mechanism-level parallelism immediately without needing a new provider posture first.

**What changed in the system**: The old job `bgjob_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405` was deliberately abandoned. The decisive local excerpt lane now runs as two active shard jobs on the same personal key under shared run id `attentional_v2_human_notes_guided_excerpt_eval_v1_judged_parallel_retry1_20260405`. Each shard owns a disjoint `--unit-key` slice, runs `stage=all`, uses `mechanism_execution_mode=parallel`, and clamps per-process budgets with `LLM_PROCESS_RUNTIME_PROFILE_MAX_CONCURRENCY=8` plus `LLM_PROCESS_EVAL_JUDGE_PROFILE_MAX_CONCURRENCY=4`. The first shard-launch attempt failed immediately because the wrong `--unit-key` separator form was used; retry1 corrected that launch-only mistake and became the real active lane.

**Why it matters later**: Future contributors could otherwise see the earlier ETA-gate note, the abandoned monolithic rerun, and the active shard jobs and conclude the project changed direction impulsively. This entry records the actual rule: preserve in-flight work only when it has already materialized meaningful reusable evidence. If inspection shows the old run is still pre-bundle, pre-case, and effectively single-mechanism, restart under the sharded architecture instead of protecting sunk cost.

**Primary evidence**:
- `reading-companion-backend/state/job_registry/logs/bgjob_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405.log`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_excerpt_parallel_smoke_20260405/shards/smoke_dual_heavy/summary/llm_usage.json`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_excerpt_parallel_smoke_20260405/shards/smoke_dual_heavy/summary/llm_usage_recomputed.json`
- `reading-companion-backend/eval/runs/attentional_v2/llm_capacity_probe_personal_20260405/summary/llm_usage.json`
- `reading-companion-backend/state/job_registry/jobs/bgjob_human_notes_excerpt_parallel_judged_shard_a_retry1_20260405.json`
- `reading-companion-backend/state/job_registry/jobs/bgjob_human_notes_excerpt_parallel_judged_shard_b_retry1_20260405.json`
- `reading-companion-backend/state/job_registry/logs/bgjob_human_notes_excerpt_parallel_judged_shard_a_retry1_20260405.log`
- `reading-companion-backend/state/job_registry/logs/bgjob_human_notes_excerpt_parallel_judged_shard_b_retry1_20260405.log`
- `reading-companion-backend/eval/attentional_v2/run_excerpt_comparison.py`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

## Entry 49
**ID**: DEC-052
**Status**: active

**Decision / Inflection**: Treat excerpt-lane throughput as a first-class Phase 9 gate, and stop defaulting to broad excerpt-surface judged reruns before `attentional_v2` has both a bounded throughput repair and one ROI-first micro-slice harness.

**Period**: April 5, 2026, after the completed dual-pool retry3 judged excerpt lane finally produced reusable operational evidence but still failed to produce broad two-mechanism overlap.

**Problem**: The project now has a staged/sharded runner, pooled targets, and explicit usage summaries, so "the harness is monolithic" is no longer the main explanation for slow excerpt evaluation. The completed retry3 lane showed a different bottleneck clearly: `attentional_v2` can require several times more reader calls than `iterator_v1` on the same chapter, which then interacts with real quota cooldown and causes most of the surface to degrade into `iterator-only` or `mechanism_unavailable` outcomes. At the same time, the full notes-guided surface still includes low-ROI heavy chapters that can occupy early worker slots for hours before later evidence-rich units even begin. If the project kept rerunning full surfaces under that posture, it would keep paying for throughput diagnosis without actually accelerating iteration.

**Alternatives considered**: Keep rerunning the full notes-guided or `excerpt surface v1.1` judged lanes more patiently, focus only on throughput repair without changing excerpt iteration posture, or postpone mechanism repair and only redesign the dataset.

**Why this path won**: A smaller judged micro-slice and a bounded throughput repair solve different parts of the same problem. The micro-slice gives the project a fast, repeatable attribution harness; the throughput repair makes that harness meaningfully runnable for `attentional_v2`. Doing only one side would leave the project either optimizing blindly on a slow surface or measuring a better surface with a still-too-expensive mechanism. The right immediate posture is therefore combined but ordered: define the ROI-first slice, use it as the default judged harness, and repair throughput before spending on another broad excerpt rerun.

**What changed in the system**: Stable evaluation guidance now records throughput diagnosis and ROI-first excerpt iteration as explicit rules. The working ledger now treats `attentional_v2` local-cycle call amplification as a high-priority failure mode and full-surface low-ROI launch order as an evaluation anti-pattern. Living state now records the retry3 completion split (`7` both-complete, `34` iterator-only, `14` both-failed), the measured call-count asymmetry, and the new recommendation not to launch another broad excerpt judged rerun first. `TASK-PHASE9-DECISIVE-EVAL` now points to one ROI-first judged excerpt micro-slice plus bounded `attentional_v2` throughput repair as the next move.

**Why it matters later**: Future contributors will otherwise see the dual-pool retry3 lane as "another quota failure" and miss the more important lesson: by this point the project had enough runner and gateway machinery to expose a real mechanism-throughput bottleneck. This is the moment where throughput stopped being an operator complaint and became part of mechanism fitness and benchmark-launch design.

**Primary evidence**:
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_human_notes_guided_excerpt_eval_v1_judged_parallel_retry1_20260405/summary/llm_usage.json`
- `reading-companion-backend/state/job_registry/logs/bgjob_human_notes_excerpt_parallel_judged_shard_a_dualpool_recovery_retry3_20260405.log`
- `reading-companion-backend/state/job_registry/logs/bgjob_human_notes_excerpt_parallel_judged_shard_b_dualpool_recovery_retry3_20260405.log`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_human_notes_guided_excerpt_eval_v1_judged_parallel_retry1_20260405/shards/shard_a/units/nawaer_baodian_private_zh__chapter_22.json`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_human_notes_guided_excerpt_eval_v1_judged_parallel_retry1_20260405/shards/shard_a/units/value_of_others_private_en__chapter_8.json`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_human_notes_guided_excerpt_eval_v1_judged_parallel_retry1_20260405/shards/shard_b/units/huochu_shengming_de_yiyi_private_zh__chapter_8.json`
- `docs/backend-reader-evaluation.md`
- `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

## Entry 50
**ID**: DEC-053
**Status**: active

**Decision / Inflection**: On `excerpt surface v1.1`, stop treating full-surface smoke completion as the gate before any judged work can start; instead promote judged shards by chapter-unit readiness while keeping smoke merge and judged final merge as their own later synchronization points.

**Period**: April 6, 2026, after the ROI-first micro-slice throughput repair had already cleared its bounded gate and the project returned to the broader excerpt surface, but the remaining heavy smoke tail (`value_of_others`) was still delaying time-to-first-judged-result unnecessarily.

**Problem**: The staged/sharded runner could already reuse successful bundles across shard boundaries, but the excerpt orchestrator still behaved as if smoke were one whole-surface lock. That meant one heavy tail chapter in `smoke shard B` could delay every judged shard, even when several other chapter units already had reusable two-mechanism bundles on disk. This created avoidable latency without adding any real evaluation safety, because the safe ownership unit was already the chapter, not the whole surface.

**Alternatives considered**: Keep waiting for all smoke shards before any judged launch, split judged ownership down to case level for even earlier start, or kill the heavy smoke shard and restart it under a different order.

**Why this path won**: Chapter-unit readiness preserves the existing safe ownership boundary and reuses the staged runner as designed. It gives earlier judged evidence without introducing case-level write collisions or reopening dataset content decisions. Keeping smoke merge and judged merge as later explicit barriers preserves report integrity while allowing the judged lane to start paying off sooner. The later hardening to wait briefly for detached judged job records was a bounded operational fix that supported the same design rather than changing it.

**What changed in the system**: `run_excerpt_comparison.py` now exposes a reusable internal readiness helper that treats a chapter unit as judged-ready only when every requested mechanism already has a reusable successful bundle, including recovery/materialization from existing unit payloads or normalized exports when possible. `scripts/orchestrate_excerpt_surface_v1_1_eval.py` now polls smoke-job status and chapter readiness separately, launches only the judged shards whose owned chapter units are ready, keeps `value_of_others` isolated as its own heavy-tail shard, delays smoke merge until both smoke jobs succeed, and delays judged final merge until all judged shards succeed. The first live unit-ready orchestrator attempt successfully launched judged `shard_b` and `shard_c` while `smoke shard B` was still running, then exposed a detached-job registry-materialization race; the active retry now waits briefly for newly launched judged job records before refreshing judged status.

**Why it matters later**: Future contributors could otherwise see judged `shard_b` and `shard_c` running before smoke finished, plus a failed first unit-ready orchestrator attempt, and misread the situation as ad hoc operator improvisation. This entry preserves the intended rule: chapter-unit readiness is now the stable excerpt promotion boundary, whole-surface smoke is not, and launch-race hardening is an implementation detail in service of that rule.

**Primary evidence**:
- `reading-companion-backend/eval/attentional_v2/run_excerpt_comparison.py`
- `reading-companion-backend/scripts/orchestrate_excerpt_surface_v1_1_eval.py`
- `reading-companion-backend/tests/test_run_excerpt_comparison.py`
- `reading-companion-backend/tests/test_excerpt_surface_v1_1_orchestrator.py`
- `reading-companion-backend/state/job_registry/logs/bgjob_excerpt_surface_v1_1_eval_orchestrator_unitready_20260406.log`
- `reading-companion-backend/state/job_registry/logs/bgjob_excerpt_surface_v1_1_eval_orchestrator_unitready_retry1_20260406.log`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`

## Entry 51
**ID**: DEC-054
**Status**: active

**Decision / Inflection**: Reclassify `book_analysis` from a merely "secondary" capability to a retired legacy capability, while keeping current `/analysis/*` routes as compatibility names for the live deep-reading workflow.

**Period**: April 7, 2026, after the product direction had already converged on sequential deep reading and the remaining ambiguity was now mostly naming debt in docs and backend helpers.

**Problem**: The repo had already stopped treating `book_analysis` as an active product lane in practice, but several stable docs and backend function names still described it as a secondary capability. That wording made the live product boundary fuzzy and created a more concrete bug risk: the current deep-reading start path still ran through helpers named `book_analysis`, which made the active sequential flow look semantically tied to a capability the product no longer intends to pursue.

**Alternatives considered**: Keep calling `book_analysis` a secondary capability, delete the legacy code immediately, or fully rename the public `/analysis/*` HTTP surface in one risky compatibility-breaking pass.

**Why this path won**: The project needed a clearer truth without forcing unnecessary breakage. Marking `book_analysis` as retired legacy compatibility debt makes the product boundary explicit, while keeping `/analysis/*` as the public route prefix avoids churn in the active frontend/API contract. Internally, the active deep-reading launcher can be renamed and documented clearly without deleting the old legacy implementation before the team is ready.

**What changed in the system**: Stable docs now describe `book_analysis` as a retired legacy capability preserved only for compatibility/debugging. Backend job/API wiring now uses a canonical existing-book deep-reading launcher for the live sequential flow, while `launch_book_analysis_job` remains only as a deprecated compatibility alias. API handler names and OpenAPI operation ids now describe deep reading instead of `book_analysis`, and the retained legacy code paths are marked as retired rather than silently current.

**Why it matters later**: Future contributors could otherwise see `/analysis/*` routes, `book_analysis` helper names, and the preserved legacy implementation and mistakenly conclude that the product still supports two active reading modes. This entry records the intended boundary: one active deep-reading product lane, plus one retired legacy capability kept temporarily for compatibility debt management.

**Primary evidence**:
- `docs/product-interaction-model.md`
- `docs/backend-sequential-lifecycle.md`
- `docs/api-contract.md`
- `docs/api-integration.md`
- `docs/backend-state-aggregation.md`
- `docs/runtime-modes.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/AGENTS.md`
- `reading-companion-backend/src/library/jobs.py`
- `reading-companion-backend/src/api/app.py`

## Entry 52
**ID**: DEC-055
**Status**: active

**Decision / Inflection**: Complete the compatibility-first default cutover and make `attentional_v2` the normal product deep-reading mechanism, while preserving `iterator_v1` as an explicit fallback and legacy-resume path.

**Period**: April 8, 2026, after the completed `excerpt surface v1.1` formal judged result had already provided the main local-reading evidence bundle and the remaining long-span work had narrowed to one targeted recovery job.

**Problem**: The repo had already proved that `attentional_v2` was runnable end to end and had enough excerpt-level evidence to justify product use, but the actual default launch path, stable docs, and operator semantics still behaved as if `iterator_v1` were the normal reader. That mismatch made the product posture harder to explain, risked future agents re-centering work on the wrong mechanism, and left old iterator-era resume behavior vulnerable once the built-in default flipped.

**Alternatives considered**: Keep `iterator_v1` as default until every long-span lane was perfectly clean, flip the default without explicit fallback/legacy-resume protection, or jump straight into a V2-native frontend rewrite before landing the compatibility cutover.

**Why this path won**: The project needed a clean, truthful default first. Switching the product path to `attentional_v2` through the current compatibility surfaces lets the app use the new mechanism now, preserves a working frontend, and keeps `iterator_v1` callable where it is still useful. Adding legacy iterator resume inference at the same time avoids breaking older in-progress books just because the built-in default changed.

**What changed in the system**: Built-in mechanism registration now makes `attentional_v2` the default and leaves `iterator_v1` non-default. `BACKEND_READING_MECHANISM` now acts as an explicit fallback override rather than as the normal path selector: unset means the default `attentional_v2` path, while `iterator_v1` forces the fallback. Job refresh/resume now preserves old iterator runs even when shell/job metadata is missing by inferring `iterator_v1` from legacy structure artifacts before falling back to the new default. Stable docs, current-state routing, and Phase 9 task tracking now all say explicitly that compatibility cutover is complete, `attentional_v2` is the default deep-reading mechanism, and V2-native frontend work is the next separate lane.

**Why it matters later**: Future contributors will otherwise see a mixed repo shape: a default `attentional_v2` runtime in code, old section-first frontend surfaces, and lots of iterator-era artifacts on disk. This entry records the intended interpretation of that mixed state: the product has already cut over to `attentional_v2`, the current frontend is still a compatibility shell over that default, and `iterator_v1` survives as a supported fallback rather than as the center of the system.

**Primary evidence**:
- `reading-companion-backend/src/reading_mechanisms/__init__.py`
- `reading-companion-backend/src/config.py`
- `reading-companion-backend/src/library/jobs.py`
- `reading-companion-backend/tests/test_reading_runtime.py`
- `reading-companion-backend/tests/test_library_api.py`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/README.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reading-mechanisms/iterator_v1.md`
- `docs/backend-sequential-lifecycle.md`
- `docs/backend-state-aggregation.md`
- `docs/api-integration.md`
- `docs/product-interaction-model.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Entry 53
**ID**: DEC-066
**Status**: active

**Decision / Inflection**: Stop treating the old `iterator_v1` / section-first frontend presentation as a co-equal product UI direction, and make V2-native reading presentation the next active product-facing lane.

**Period**: April 9, 2026, immediately after the compatibility-first cutover had already landed and a live UX audit showed that the main remaining gap was presentation truth rather than mechanism availability.

**Problem**: After the default cutover, the product sat in an in-between state: `attentional_v2` was already the real reading mechanism, but the routed frontend still presented books mainly through a section-first compatibility shell. That created a new strategic ambiguity. The team could either keep investing in the old V1-shaped presentation as if it might remain a permanent product model, or accept that the compatibility shell had served its purpose and move the UI itself toward V2-native truth. Without an explicit decision, future work could easily drift into low-value cleanup, preserve the wrong mental model, or keep the product story blurry.

**Alternatives considered**: Keep the V1-shaped presentation as a parallel candidate product model, run a standalone cleanup-only pass to de-emphasize V1 concepts before any V2 redesign, or delay frontend migration until every long-span evidence lane was fully clean.

**Why this path won**: The project already has enough evidence to trust `attentional_v2` as the main reading path. The remaining weakness is not "can V2 read?" but "can the product show V2 honestly and vividly?" That makes a V2-native presentation pass more valuable than another round of preserving or polishing the older section-first model. At the same time, keeping the old presentation only as a compatibility shell preserves stability while the new UI lands, without forcing a risky all-at-once removal.

**What changed in the system**: Stable current-state and task-routing docs now treat `V2-native reading presentation` as the next active migration lane rather than as a distant queued idea. `iterator_v1` presentation concepts are now explicitly compatibility-only for product UI planning, not a co-equal design target. The next frontend sequence is fixed as: first repair truth/visibility bugs on the current routed surfaces, then promote V2 live-reading state on `/books/:id`, then redesign chapter and marks surfaces around anchors, loci, and thought lineage. `Section-first retirement` remains a later cleanup lane rather than the first move.

**Why it matters later**: Future contributors will otherwise see a mixed product and infer that the old section-first UI was still an endorsed product option. This entry records the intended interpretation instead: the compatibility shell remains only to avoid breaking the current app while the product-facing reading experience catches up to the already-landed V2 mechanism.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/phase9-compat-cutover-roadmap.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- `docs/api-integration.md`
- `docs/backend-state-aggregation.md`

## Entry 54
**ID**: DEC-057
**Status**: active

**Decision / Inflection**: Keep the existing `attentional_v2` mechanism key and evolve it in place through a structural Phase A rework, instead of branching into a separate `v3` mechanism.

**Period**: April 12, 2026, after the first full long-span judged rerun and the follow-up mechanism review had already isolated V2's current failures to trigger authority, span-authority mismatch, and weak long-distance reuse rather than to its core reading philosophy.

**Problem**: Formal evaluation showed a split result. `attentional_v2` had real excerpt-level strengths, especially around local pressure tracking and text-grounded reading discipline, but it also missed important long-span evidence because heuristic trigger outputs still controlled whether正文 entered formal reading and because smaller late-local analysis spans could effectively determine closure over larger hidden spans. The project needed a repair path that fixed those structural failures without discarding the sentence-fidelity, pressure-driven, typed-state advantages already proven valuable.

**Alternatives considered**: Launch a separate `v3` mechanism with a fresh key and parallel artifact tree, continue making only small local patches inside the old trigger-gated control shape, or fall back toward `iterator_v1`-style section-first reading because it still outperformed V2 on some long-span probes.

**Why this path won**: The evidence did not show that V2's underlying reading philosophy was wrong. It showed that specific control-surface decisions were wrong: trigger gating had too much authority, exact unit visibility and closure authority had drifted apart, and formal reading was not guaranteed for all正文. Keeping the same mechanism key preserves the product default, existing compatibility projections, and resume semantics, while letting the team selectively replace the failing control skeleton and carry V2's existing local-reading strengths forward.

**What changed in the system**: The live V2 runner now routes every forward正文 step through `navigate.unitize -> read -> navigate.route` without changing the public mechanism key. Sentence-level trigger detection remains as watch metadata and observability support, but it no longer decides whether正文 receives formal LLM reading. A new prompt-led `navigate_unitize` node now chooses the exact coverage unit inside a bounded preview window, a mechanism-private unitization audit stream records each chosen unit, and the formal read path now operates on the exact chosen unit rather than on a reconstructed narrow tail that could silently inherit authority over a larger span. The existing local-cycle internals remain in place for now, but only after the coverage unit has already been fixed.

**Why it matters later**: Future contributors will otherwise see a mix of old terminology (`phase4`, `trigger_state`, `zoom_now`) and new control behavior and may assume the code is half-migrated or that a `v3` branch was intended but never finished. This entry records the intended interpretation: Phase A is not an abandoned fork idea. It is the first landed slice of an in-place `attentional_v2` redesign that preserves V2's strengths while replacing the specific control skeleton that long-span evaluation proved unreliable.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `reading-companion-backend/docs/evaluation/long_span/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_followup_reflection_and_decisions.md`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`

## Entry 55
**ID**: DEC-058
**Status**: active

**Decision / Inflection**: Make `read` the canonical owner of formal unit reading, carried-forward-context use, `implicit_uptake`, and optional raw reaction in live `attentional_v2`, instead of keeping the old zoom/closure/controller/reaction-emission chain on the live path.

**Period**: April 12, 2026, immediately after Phase A had already fixed coverage admission and span-authority alignment, and the next mechanism question was how prior context and raw reaction truth should actually be integrated into one live read.

**Problem**: Phase A ensured that every chosen unit now gets formal reading, but the live semantics were still fragmented in the older local-cycle shape. That older chain made it too hard to explain what the mechanism had really read, where prior material entered, and which component truly owned the raw reaction. It also encouraged a misleading implementation direction where “reuse” might become a separate mechanism action instead of a natural consequence of reading with carried continuity.

**Alternatives considered**: Keep the old `zoom_read -> meaning_unit_closure -> controller_decision -> reaction_emission` chain on the live path, add a standalone `reuse` node/action, or let routing/reaction remain semi-LLM-owned after a thin local read step.

**Why this path won**: The project’s first-principles goal is a reading agent, not a pipeline that performs reading-adjacent bookkeeping through extra synthetic actions. A single authoritative `read` step matches that goal better: it reads the chosen unit, receives a small carried-forward continuity packet by default, asks for more context only when needed, and surfaces any raw reaction directly. That keeps the model’s semantic freedom where it belongs while leaving deterministic code to handle bounded recall/look-back, audit trails, and state application.

**What changed in the system**: The live runner now builds a bounded `carry-forward context` from persisted state before each formal unit read. `read` returns the authoritative `ReadUnitResult`, including `local_understanding`, `move_hint`, `continuation_pressure`, `implicit_uptake`, `anchor_evidence`, `prior_material_use`, optional `raw_reaction`, and optional `context_request`. If `read` explicitly asks for more context, the runner may perform at most one bounded supplemental step through deterministic `active_recall` or exact `look_back`, then rerun `read` once. `navigate.route` is now a deterministic consumer of the final read packet, raw reaction persistence comes directly from `read`, and private `read_audit` records now capture carry-forward refs plus supplemental-context satisfaction.

**Why it matters later**: Future contributors will otherwise see `read`, old phase-era helper names, and several state artifacts side by side and may assume the mechanism still has multiple competing owners for local understanding and reaction truth. This entry records the intended ownership boundary after Phase B: live `attentional_v2` reads through one authoritative `read` packet, while older helper nodes remain historical/compatibility territory rather than the live control spine.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`

## Entry 56
**ID**: DEC-059
**Status**: active

**Decision / Inflection**: Make `working_state / concept_registry / thread_trace / reflective_frames / anchor_bank` the canonical runtime and checkpoint state of live `attentional_v2`, and demote the old V2 state stores to legacy load/projection territory.

**Period**: April 12, 2026, after Phase C.1 and Phase C.2 had already proven the packetization seam and the bounded concept/thread digests, and before the remaining helper territories were retired in the next cleanup slice.

**Problem**: The mechanism had already gained a better live control skeleton and packetized continuity path, but runtime truth still sat ambiguously across the older V2 stores. That left two overlapping state stories in the system: the new packet layer was already talking in terms of `working_state`, concept/thread digests, and an `anchor_bank`-style evidence model, while the persisted runtime/checkpoint territory still treated `working_pressure / anchor_memory / reflective_summaries` as canonical. Without a direct cutover, continuity work, active recall, and later slow-cycle cleanup would keep inheriting fuzzy ownership.

**Alternatives considered**: Keep the old state stores canonical and let the new semantic layers remain packet-only projections, rewrite every remaining helper in one large simultaneous migration before changing runtime truth, or split into a fresh parallel `v3` state bundle.

**Why this path won**: A direct main-state cutover creates one honest ownership map without forcing an all-at-once subsystem rewrite. The new state layers already match the mechanism's intended semantics better: `working_state` for hot reading pressure, `concept_registry` for durable object memory, `thread_trace` for argument/plot/relationship lines, `reflective_frames` for slow chapter/book understanding, and `anchor_bank` for source-grounded evidence. By combining that cutover with deterministic legacy migration and legacy projection adapters, the system can move to one real semantic truth now while still preserving resume compatibility and helper continuity during the next cleanup phase.

**What changed in the system**: New runs now initialize and persist `working_state.json`, `concept_registry.json`, `thread_trace.json`, `reflective_frames.json`, and `anchor_bank.json` as the primary mechanism-private runtime artifacts. Newly written checkpoints now store those keys rather than the old V2 state keys. Load/resume accepts both old and new runtime/checkpoint shapes, migrating legacy `working_pressure / anchor_memory / reflective_summaries` forward in memory when needed. Live packet building and `active_recall` now pull first-class `concepts` and `threads` from the new state layers. Remaining sentence-intake, bridge, and chapter slow-cycle helpers may still receive legacy-shaped projections, but those projections are now adapters from the new canonical state rather than the other way around.

**Why it matters later**: Future contributors will otherwise see both old and new state names in code, tests, and runtime trees and may assume the project never actually chose which layer owns semantic truth. This entry records the intended interpretation: Phase C.3 is the point where live `attentional_v2` stopped treating the older V2 stores as canonical memory and committed to the new layered state model, with helper projections retained only as a bounded migration bridge.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/state_migration.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`
- `reading-companion-backend/tests/test_attentional_v2_state_migration.py`

## Entry 57
**ID**: DEC-060
**Status**: active

**Decision / Inflection**: Finish the live `attentional_v2` state migration by cutting sentence-intake, bridge, and chapter slow-cycle over to the new primary state layers directly, and stop accepting pre-`Phase C.3` runtime/checkpoint shapes on the live path.

**Period**: April 12, 2026, immediately after `Phase C.3` had already made the new layered state model canonical but while live helper execution still relied on legacy projections to finish its work.

**Problem**: After `Phase C.3`, the mechanism had one honest primary state model on paper, but the live implementation still had a split personality. Core helper territories such as sentence-intake, bridge execution, and chapter slow-cycle were still being fed by `project_legacy_*` adapters or migrate-back round trips, and resume/runtime loading still tolerated old-format state. That kept the code harder to explain, preserved unnecessary translation seams on the live path, and left the system one refactor away from reintroducing ambiguity about which state layer really owned behavior.

**Alternatives considered**: Keep the legacy projections in place as a long-term compatibility cushion, rewrite helper behavior and state ownership in one larger semantic redesign pass, or continue accepting old runtime/checkpoint shapes indefinitely while the new state model gradually spread.

**Why this path won**: The project had already decided on the new primary state model. At that point, the highest-value move was not another theoretical redesign, but an ownership cleanup: make helpers execute directly on the chosen state layers, retire the old projection round trips from the live runner, and make runtime/resume honesty match the implementation reality. Doing that now improves code consistency and debugging clarity without forcing another change to public compatibility outputs or to the top-level mechanism loop.

**What changed in the system**: `process_sentence_intake` now consumes `working_state / concept_registry / thread_trace / anchor_bank` directly. Bridge candidate generation and the live Phase 5 bridge cycle now use `anchor_bank` as the evidence source plus new-layer semantic support, and they write `working_state / concept_registry / thread_trace / anchor_bank` directly instead of round-tripping through legacy `anchor_memory` territory. The chapter slow cycle now consumes and updates `working_state / concept_registry / thread_trace / reflective_frames / anchor_bank` directly. The live runner no longer calls `project_legacy_*` or migrates helper outputs back from old shapes, and live runtime loading / resume now fail fast on pre-`Phase C.3` runtime directories and checkpoints instead of silently migrating them.

**Why it matters later**: Future contributors will otherwise see old state names preserved in historical code/tests and assume the live mechanism still depends on them. This entry records the sharper post-`Phase C.4` interpretation: the old V2 stores may remain visible in older artifacts and historical helpers, but they are no longer part of the supported live execution contract of `attentional_v2`.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `reading-companion-backend/src/attentional_v2/intake.py`
- `reading-companion-backend/src/attentional_v2/retrieval.py`
- `reading-companion-backend/src/attentional_v2/bridge.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/tests/test_attentional_v2_intake_and_retrieval.py`
- `reading-companion-backend/tests/test_attentional_v2_bridge.py`
- `reading-companion-backend/tests/test_attentional_v2_slow_cycle.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`

## Entry 58
**ID**: DEC-061
**Status**: partially superseded by `DEC-103` / `DEC-104`

**Decision / Inflection**: Polish live `attentional_v2` continuity around a lightweight persisted `continuation capsule` plus a budget-bounded multi-step supplemental recall loop, instead of keeping the old “one extra pass only” posture or introducing a heavy central compactor first.

**Period**: April 12, 2026, immediately after `Phase C.4` had already finished the new-state/helper cutover and the next mechanism problem became how live reading should carry continuity, request more prior material, and resume honestly under the new state model.

**Problem**: After `Phase C.4`, the live mechanism finally had one clean control skeleton and one clean primary state model, but the continuity path was still thinner than intended. `read` could only ask for one extra supplemental step, runtime/checkpoint continuity still relied mostly on raw persisted state rather than on an explicit lightweight continuity seed, and warm resume had no dedicated bounded artifact that said “this is what should be easy to rehydrate first.” That left long-distance reuse, recall traceability, and resume clarity better than before but still less explicit than the new design direction required.

**Alternatives considered**: Keep the single supplemental pass as the permanent live rule, jump straight to a heavier compaction/rehydration subsystem that tries to compress broad state into one replacement summary, or let warm resume continue reconstructing continuity only from full runtime/checkpoint state without a dedicated continuity artifact.

**Why this path won**: The project’s first-principles goal is still a reader that naturally carries continuity forward, not a system that hides continuity behind an oversized compactor. A lightweight persisted `continuation capsule` gives the runner and resume path one bounded continuity seed without flattening the primary state layers into a fake replacement memory. At the same time, a budget-bounded multi-step supplemental loop lets `read` ask for more context one step at a time when the current unit truly needs it, while still keeping runtime cost and runaway risk under deterministic control.

**What changed in the system**: The live runner then let `read` request supplemental context through a budget-bounded multi-step loop rather than stopping after one extra pass. Supplemental context could accumulate across multiple `active_recall` / exact `look_back` steps, `look_back` resolved one bounded earlier span per request, and private `read_audit` records captured each supplemental step, stop reason, and budget exhaustion. Runtime state and full checkpoints persisted `continuation_capsule.json` / checkpoint-embedded continuation capsules carrying bounded continuity digests plus explicit `rehydration entrypoints`. Warm resume remained `new-format only`, but restored the latest usable continuation capsule together with new-format runtime/checkpoint state instead of depending only on raw state files. After `DEC-103` / `DEC-104`, the supplemental `active_recall` / `look_back` helper loop is deprecated compatibility/reference surface and should not be treated as the future Ingest retrieval design.

**Why it matters later**: Future contributors will otherwise see the new state layers and helper contracts, but miss the next crucial continuity decision: the project explicitly chose a light persisted continuity seed plus bounded iterative recall over either a one-shot recall limit or an early heavy compaction subsystem. This entry records that `Phase D` was not “small cleanup.” It was the point where continuity, recall, and warm resume were made to match the new post-`Phase C` mechanism shape.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`

## Entry 59
**ID**: DEC-062
**Status**: active

**Decision / Inflection**: Replace the old profile-driven `excerpt surface v1.1` active local benchmark with a note-aligned `user-level selective v1` benchmark built directly from aligned human notes and continuous reading segments.

**Period**: April 14, 2026, after the post-Phase-D audit exposed the provenance ambiguity of the older excerpt-surface line and after direct review of the note-linked books showed that “human-notes-guided” chapter selection was still allowing machine-expanded same-chapter synthetic cases to masquerade as user-meaningful local targets.

**Problem**: The older active local benchmark no longer matched the product question closely enough. It had become useful evidence about one chapter-scoped local-reading surface, but it was still built through profile-driven chapter mining after note-guided chapter selection. That meant many active excerpt cases were not the user's real highlights, even when the surface name and provenance fields made them look like they were. Once the project's local/user-level question was restated clearly as “did the reader visibly notice the things the real user highlighted?”, keeping a mined excerpt surface as the active pointer would have kept the benchmark semantically misaligned.

**Alternatives considered**: Keep using `excerpt surface v1.1` as the active local benchmark and only fix its case provenance labels, continue the older notes-guided builder but forbid the most obvious same-chapter expansions, or postpone any local benchmark replacement until a later full benchmark-family redesign.

**Why this path won**: The project needed to stop confusing “chapter-local interesting text” with “the user's real note targets.” A note-aligned benchmark restores the right object of evaluation directly: the mechanism reads one continuous segment that starts at book body start, and the benchmark then checks whether user-visible reactions cover the aligned human notes inside that segment. This keeps the reading setup honest, restores provenance clarity, removes synthetic same-chapter expansion from the active path, and makes `Selective Legibility` legible again as note recall rather than as success on builder-generated excerpt cases.

**What changed in the system**: The active local/user-level split manifest is now `attentional_v2_user_level_selective_v1_draft.json`. The active package now lives under `state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1/` with one `reading_segment` per eligible note-linked book and one `note_case` per aligned note span. Segment construction now starts at body start and ends only after the segment covers at least the target note count at an honest structural boundary. The active runner is now `run_user_level_selective_comparison.py`, which evaluates `reader_character.selective_legibility` through note recall: `exact_match` auto-counts, non-exact cases go to judge, and only `focused_hit` also counts while `incidental_cover` stays supporting-only. The older `excerpt surface v1.1` split, dataset manifests, interpretation report, and related comparative audit remain preserved, but they are now labeled historical / superseded rather than active.

**Why it matters later**: Future contributors will otherwise see both the older excerpt-surface reports and the new note-aligned package in the repo and may assume they are co-equal active local benchmarks. This entry records the intended interpretation: the old excerpt surface is still useful historical evidence, but the active local/user-level benchmark has been redefined around aligned human notes and continuous reading segments. The temporary April 14 implementation constraint noted at decision time has since been cleared: after repairing the library-notes alignment fallback and re-registering the managed notes asset, `nawaer_baodian_private_zh` is now back inside the active package, so the local benchmark is once again `5 / 5` on registered note-linked books.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/eval/attentional_v2/user_level_selective_v1.py`
- `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1/manifest.json`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/excerpt/README.md`
- `reading-companion-backend/docs/research/attentional_v2_post_phase_d_eval_comparative_audit_20260414.md`

## Entry 60
**ID**: DEC-063
**Status**: active

**Decision / Inflection**: Add registry-level long-horizon auto-recovery for offline background jobs instead of relying only on per-call retries or one-off orchestrator-local retry loops.

**Period**: April 15, 2026, after the first judged `user-level selective v1` run showed that short-horizon retry inside individual scripts was not enough when provider instability lasted longer than one local retry budget.

**Problem**: The project already had transient LLM retry inside the gateway and some local retry inside specific orchestrators, but it still lacked a durable “wait and try again later” layer. When provider-side timeout, quota cooldown, `520`, or `529` instability outlasted those short retry windows, the parent background job still landed in a terminal state and then disappeared from active follow-up posture unless a human explicitly re-launched it. That was exactly the gap between “brief retry” and “long-horizon recovery.”

**Alternatives considered**: Keep all retry behavior inside individual eval/orchestrator scripts, require humans to re-launch failed jobs manually after checking the registry, or build a separate new queueing system outside the existing background-job registry.

**Why this path won**: The project already had one canonical ledger for long-running offline work. Extending that ledger with recovery policy was lighter and more legible than inventing another queue. A registry-level watchdog can keep using the same job record, command, log, check command, and decision context while adding the one missing behavior: if a recoverable failure persists longer than local retry budgets, wait a longer interval and relaunch from the registered command.

**What changed in the system**: Background job records now carry explicit long-horizon auto-recovery fields such as `auto_recovery_mode`, `auto_recovery_interval_seconds`, and relaunch counters. `check_background_jobs.py` now supports watchdog mode through `--watch --auto-recover`, so one long-running checker can periodically refresh the registry and relaunch eligible terminal jobs after the configured interval. Terminal jobs that are still pending auto-recovery remain visible in the derived active views instead of disappearing immediately. `run_registered_job.py` now also supports relaunch-safe `--shell-command` handling so the original registered command text can be preserved across repeated delayed relaunches.

**Why it matters later**: Future contributors will otherwise see both orchestrator-local retry logic and the new watchdog flags and assume they solve the same problem. This entry records the boundary clearly: gateway/orchestrator retries cover short transient failure inside one active run; registry-level auto-recovery covers longer provider outages by re-checking and relaunching the whole registered job after a longer wait.

**Primary evidence**:
- `reading-companion-backend/src/reading_runtime/background_job_registry.py`
- `reading-companion-backend/scripts/check_background_jobs.py`
- `reading-companion-backend/scripts/run_registered_job.py`
- `reading-companion-backend/scripts/register_background_job.py`
- `reading-companion-backend/tests/test_background_job_watchdog.py`
- `docs/source-of-truth-map.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/docs/evaluation/user_level/README.md`

## Entry 61
**ID**: DEC-064
**Status**: active

**Decision / Inflection**: Make `user-level selective v1` candidate retrieval strictly source-span grounded and invalidate the April 15 retry2 run that admitted candidates by string similarity.

**Period**: April 15, 2026, during inspection of the first judged `user-level selective v1` execution after several shards showed extreme note-case judge expansion.

**Problem**: The active user-level runner was supposed to test whether the reader visibly noticed the user's aligned note spans. Instead, its candidate retrieval admitted reactions when their quote/content text was merely similar to the note span. That made unrelated same-theme reactions enter LLM judging, caused huge candidate explosions, and, more importantly, changed the benchmark question from “did the reader quote the source location?” into “did the reader say something textually similar?” This was a benchmark-contract bug, not a mechanism result.

**Alternatives considered**: Keep broad text-similarity retrieval and batch judge candidates more efficiently, add a higher string-similarity threshold, or move the eligibility gate to exact source-position overlap before any LLM judge call.

**Why this path won**: `Selective Legibility` is a source-location question. LLM-as-judge is useful only after a real location overlap exists, to decide whether the overlap is focused or merely incidental. It must not be used to recover candidates that have no source-position overlap. The active benchmark therefore needs strict source-span eligibility, fail-fast locator requirements, and duplicate-span diagnostics rather than repeated judging of same-span reactions.

**What changed in the system**: The active note-case package now carries `segment_source_v1` char-span slices for every note case. Both mechanism-normalized reaction exports expose source locators for visible reactions. `run_user_level_selective_comparison.py` now deduplicates by canonical span and admits only candidates whose source spans intersect the note case span. Exact same-span matches auto-count; non-exact overlap candidates go to the existing `focused_hit / incidental_cover / miss` judge; visible reactions without usable locators fail the benchmark run instead of falling back to string matching. For reusable `iterator_v1` outputs, normalized export now reconstructs exact or normalized source char spans from public result locators when possible, and marks enclosing semantic-segment fallback spans explicitly so they can be judged but never auto-counted as exact hits. The runner also gained a rejudge-only path that rebuilds normalized bundles from completed reading outputs without calling `read_book`; incomplete reading shards still have to be re-read. The invalid `bgjob_user_level_selective_v1_failed_shards_retry2_20260415` run was stopped and retained only as bug-diagnostic evidence.

**Why it matters later**: Without this entry, future contributors could mistake the retry2 slowdown and partial results for evidence about `attentional_v2` or `iterator_v1`. This records that those results are invalid because the harness tested the wrong eligibility condition. It also preserves the stable rule that user-level note recall is grounded in source-position overlap, not semantic or textual resemblance.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/eval/attentional_v2/user_level_selective_v1.py`
- `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- `reading-companion-backend/src/reading_mechanisms/iterator_v1.py`
- `reading-companion-backend/src/attentional_v2/evaluation.py`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1/note_cases.jsonl`

## Entry 62
**ID**: DEC-065
**Status**: active

**Decision / Inflection**: Converge chapter identity semantics globally around three distinct concepts: stable `chapter_id`, optional visible `chapter_number`, and human-facing `chapter_ref`, while renaming dataset/eval parse-coordinate fields to `source_chapter_id` / `source_chapter_ids`.

**Period**: April 16, 2026, after the new user-level audit export made it obvious that a visible first body unit such as `第一部分` in *活出生命的意义* could still carry an internal parse coordinate like `8`, which was technically correct but humanly misleading when surfaced without semantic separation.

**Problem**: The codebase had already partially distinguished chapter key vs visible numbering since the V1 era, but that distinction was not globally explicit. Public API consumers could easily read `chapter_id` as if it were the book's visible chapter number, while dataset/audit artifacts were also reusing bare `chapter_id` for internal parse coordinates. That made front matter offsets, prefatory units, and non-numeric headings look like bugs when they were really a naming/semantics mismatch.

**Alternatives considered**: Break the public contract and rename `chapter_id` to a new key name everywhere, keep the old mixed semantics and only patch the audit export text, or formalize the existing separation without breaking routes and cache keys.

**Why this path won**: The system already depends on a stable integer chapter key for routes, caches, and compatibility payloads. Breaking that key would create wide churn for little product value. The better path is additive clarification: keep `chapter_id` as the stable parsed-book key, expose `chapter_number` additively when the source heading yields a reliable visible numeric ordinal, make `chapter_ref` the default human-facing label, and stop reusing bare `chapter_id` inside benchmark provenance where the meaning is really “source parse coordinate.”

**What changed in the system**: Stable docs now define `chapter_id` as the canonical parsed-book chapter key rather than as visible chapter numbering. Public backend payloads additively expose `chapter_number` on chapter-shaped responses, current-state payloads, activity/realtime chapter events, and marks metadata whenever the manifest/runtime truth can support it. Human-facing displays are expected to prefer `chapter_ref` and then `title`, not `chapter_id`. The active user-level benchmark package and its audit renderer now use `source_chapter_id` / `source_chapter_ids` for parse-coordinate provenance, and the audit export labels those values explicitly as internal/source ids instead of “chapter numbers.”

**Why it matters later**: Future contributors will otherwise rediscover the same confusion whenever a book begins with front matter, uses non-numeric units such as `Preface` or `第一部分`, or when an eval package needs to show parse provenance. This entry records the project-wide rule: stable key, optional visible number, human-facing reference, and separate source-coordinate naming in dataset/eval territory.

**Primary evidence**:
- `docs/api-contract.md`
- `docs/backend-state-aggregation.md`
- `docs/backend-reader-evaluation.md`
- `docs/history/decision-log.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/src/api/schemas.py`
- `reading-companion-backend/src/library/catalog.py`
- `reading-companion-backend/src/library/user_marks.py`
- `reading-companion-backend/src/api/realtime.py`
- `reading-companion-backend/eval/attentional_v2/user_level_selective_v1.py`
- `reading-companion-backend/eval/attentional_v2/render_user_level_selective_audit.py`

## Entry 63
**ID**: DEC-066
**Status**: active

**Decision / Inflection**: Replace the old bounded `EARLY / MID / LATE` long-span evaluation method as the active methodology with a target-centered long-span accumulation v2 framework.

**Period**: April 18, 2026, after the long-span probe-mining reflection made it clear that the project no longer wanted to score whether a mechanism separately reacted at three fixed anchors, but instead wanted to score whether the mechanism reconstructed a prepared long-range thread at one final target point.

**Problem**: The old long-span v1 method was useful for the first bounded judged comparisons, but it tied the active methodology to one particular authoring shape: three anchors, bounded probe text, and pairwise LLM comparison between mechanisms. That shape was making dataset curation and evaluation logic drift apart from the actual research question. The project wanted to prepare arbitrary long-range threads with variable numbers of upstream nodes and then ask a simpler target-point question: when the mechanism reaches the prepared late point, does it actually build the earlier thread there? The old method also over-exposed mechanism-specific bundle details and pairwise prompt framing instead of centering on absolute quality at the target point.

**Alternatives considered**: Keep bounded v1 as the active method and only retune the probe dataset, continue writing three-anchor probes but reinterpret them more loosely, or treat long-span case mining as a purely manual memo exercise without changing the runner or schema.

**Why this path won**: The project needed the schema, judge contract, and mining workflow to align around the same real question. A target-centered case keeps the late target point explicit, lets the long-range thread use `2+` upstream nodes, and separates the active scoring logic from the old probe-writing convention. It also supports a cleaner evidence contract: judge only target-local reactions, explicit callback actions, and short-horizon followups, rather than rewarding private internal memory structures that never affect observable reading behavior. Absolute per-mechanism scoring keeps the method closer to the product question, while report-layer comparison still preserves cross-mechanism usefulness.

**What changed in the system**: The stable evaluation methodology now treats bounded long-span v1 as historical evidence rather than active authority. The new v2 framework defines `TargetCase`, `UpstreamNode`, `TargetEvidenceBundle`, and `AbsoluteAccumulationJudgeResult` as the core internal types, with thread logic carried by `expected_integration` rather than a separate required-relations entity. V2 reuses the active `user-level selective v1` reading windows as its substrate, uses `segment_source_v1` spans for target and upstream node grounding, and first ships only `reader_character.coherent_accumulation`. The new builder and runner live at `accumulation_benchmark_v2.py` and `run_accumulation_evaluation_v2.py`. Draft cases remain review-gated, and the project now records a dedicated long-span v2 design doc plus an empty draft dataset scaffold instead of prematurely freezing candidate cases.

**Why it matters later**: Future contributors will otherwise see both v1 historical long-span judged reports and the newer mining memo and assume they are variations on the same active method. This entry records a real methodological change: v1 is preserved as historical mechanism evidence, while v2 is the active target-centered long-span design that future dataset curation and judged runs should follow.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md`
- `reading-companion-backend/eval/attentional_v2/accumulation_benchmark_v2.py`
- `reading-companion-backend/eval/attentional_v2/run_accumulation_evaluation_v2.py`
- `reading-companion-backend/eval/manifests/splits/attentional_v2_accumulation_benchmark_v2_draft.json`

## Entry 64
**ID**: DEC-067
**Status**: active

**Decision / Inflection**: Treat the landed `Read -> Express` split as an intermediate compatibility-first branch, not as the final `attentional_v2` target shape; re-center the next implementation line on `Navigate -> Read -> Route -> slow cycle`, with `Read` owning surfaced reactions and `Navigate` owning revisit dispatch.

**Period**: April 19, 2026, after the post-E3 quality review and mechanism-design consolidation pass.

**Problem**: The Phase E1-E3 branch successfully separated visible wording into a dedicated `Express` node and proved native surfaced-reaction persistence, but the design review exposed a deeper issue: the main prompt/context burden had shifted into an overpacked `Read`, while the extra `Express` call duplicated understanding work and risked moving visible reactions away from the original first-reading moment. At the same time, revisit/look-back behavior was still too tied to runner-private supplemental fetch logic instead of the node definitions the project actually wanted: `Navigate` chooses what to read, `Read` understands it, and chapter-level consolidation stays in `slow cycle`.

**Alternatives considered**: Keep `Read -> Express` as the final live shape and only tune prompt wording, preserve a dedicated `Express` node but expand it to multiple reactions per unit, or collapse surfaced reactions back into `Read` while keeping deterministic orchestration and compatibility projections outside the semantic core.

**Why this path won**: The core product behavior is “read and react while reading,” not “read once and then hand wording to another steady-state node.” Returning surfaced reactions to `Read` keeps visible output closer to the first-reading impulse, simplifies node ownership, and better matches the mechanism's intended control boundaries. The same review also clarified that revisit is fundamentally a navigation decision, so `Read` should surface a `revisit_need` and `Navigate` should decide whether the next step is a bounded `inline_look_back` or a true `revisit_hop`. `slow cycle` remains the chapter-end maintenance territory, and `Runner` remains deterministic orchestration only.

**What changed in the system**: The stable mechanism doc and the structural rework plan now freeze a new target contract: keep `Phase E1-E3` as landed intermediate evidence, but make the next implementation line simplify the per-unit loop back toward `navigate.unitize -> read -> navigate.route`; let `Read` own `surfaced_reactions[]`, `implicit_uptake_ops[]`, `pressure_signals`, and optional `revisit_need`; let `Navigate` own `local_continuity` and revisit dispatch; keep `reflective_frames` as chapter-end `slow cycle` territory; and standardize prompt projections around `always carry / selective carry / not carry` instead of dumping full persisted state into every node.

**Why it matters later**: Without recording this reversal, future contributors would see the landed `Express` persistence work and assume the project wanted to deepen that split. This entry preserves the actual design outcome: the `Express` branch was useful evidence and migration scaffolding, but the approved long-term mechanism shape is simpler and more aligned with the reading-node definitions the project now wants to preserve.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Entry 65
**ID**: DEC-068
**Status**: active

**Decision / Inflection**: Land `Phase F1` by removing the live `Express` step from `attentional_v2`, returning surfaced-reaction ownership to `Read`, and narrowing `Read` prompt packaging to compact carried digests plus selective supplements only.

**Period**: April 19, 2026, during the first implementation slice after the post-E3 contract freeze.

**Problem**: The contract freeze had already established that the `Read -> Express` split was not the approved end-state shape, but until F1 actually landed the live code still risked drifting around the wrong steady-state assumptions: duplicated wording work, overpacked read prompts, and a mismatch between the stable docs and the real runner path.

**Alternatives considered**: Keep `Express` alive on the live path for one more compatibility slice, partially move surfaced reactions back into `Read` while still letting `Express` wordsmith the final output, or defer the cutover until revisit routing was also ready.

**Why this path won**: The safest clean cut was to restore one authoritative per-unit reading node first. That keeps visible reactions closest to the first-reading moment, removes the need to maintain a new compatibility ownership layer for a just-added node, and creates a simpler base for the next revisit-routing slice. By also narrowing prompt packaging at the same time, F1 fixes not only ownership confusion but also the prompt-overload problem that had helped push the mechanism toward summary-like output.

**What changed in the system**: The live per-unit runner path is now `navigate.unitize -> read -> navigate.route`. `Read` now directly returns `unit_delta`, `surfaced_reactions[]`, `implicit_uptake_ops[]`, `pressure_signals`, and optional `revisit_need`. The dedicated live `Express` call is gone from the runner path. `Read` prompt packaging now carries compact `local_continuity`, `working_state`, `concept_digest`, `thread_digest`, and `reflective_digest` by default, with bounded selective carry only for explicit supplements. State mutation now flows through explicit `append / update / close / link` ops instead of whole-object rewrites.

**Why it matters later**: This is the point where the approved post-E3 target shape stopped being only a design statement and became live runtime behavior. Future work on `Navigate`-owned revisit dispatch, reaction persistence cleanup, and dead-path removal can now build on a simpler factual base instead of reasoning about an intermediate `Express` ownership model that is no longer live.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`

## Entry 66
**ID**: DEC-069
**Status**: superseded by `DEC-104`

**Decision / Inflection**: Replace the planned `revisit` model with a unified `detour` model, and make F2 a `Navigate`-owned bounded hierarchical semantic search rather than a program-led candidate-recall subsystem.

**Period**: April 19, 2026, during the F2 design freeze immediately after landing Phase F1.

**Problem**: The post-F1 discussion made two issues explicit. First, the word `revisit` was too narrow for the actual behavior the project wanted: the reader might jump backward, chain to another earlier location, or otherwise leave the mainline reading path for semantically motivated reasons that were broader than “look back once and return.” Second, a program-led candidate-recall design would have pushed too much semantic authority into deterministic retrieval logic even though detour localization is fundamentally a meaning-driven reading move. The project wanted something simpler and more universal: one normal reading system, with `Navigate` temporarily redirecting that system when the current read says another region now matters.

**Alternatives considered**: Keep `revisit` as the stable term and split it into `inline_look_back` plus `revisit_hop`; let programs pre-recall semantic candidates and ask `Navigate` only to rank them; or force `Read` to provide exact earlier coordinates before any non-mainline jump could occur.

**Why this path won**: `Detour` better names the real behavior: a temporary departure from the mainline reading path whose destination and return behavior are decided by navigation rather than by a private reader-side helper. It also preserves universality. The same mechanism can cover a quick backward jump, a chained multi-hop excursion, or a future non-mainline jump without inventing separate sub-modes. Treating detour localization as `Navigate`-owned hierarchical semantic search keeps semantic authority where it belongs: the LLM reasons over structure cards, long-distance-memory digests, and source-grounded anchor handles; the program only supplies the searchable space, bounded expansion, and state bookkeeping. This matches the design lesson from coding agents: prefer maps, handles, and stepwise narrowing over heavy precomputed semantic recall.

**What changed in the system**: The stable mechanism doc and the structural rework plan now freeze F2 around `detour` terminology and behavior. `Read` will still emit the live F1 transitional field `revisit_need` until F2 lands, but the approved target shape is `detour_need`. `Navigate` will own `mainline_cursor`, `active_detour_id`, and `detour_trace`, and it will use one bounded `detour-search` prompt family whose legal outcomes are `narrow_scope`, `land_region`, and `defer_detour`. Detour search is bounded to one call when memory makes the target obvious, two calls for ordinary ambiguity, and three calls as the hard upper bound before best-effort landing or defer-to-mainline behavior. Once a detour region is landed, it is read through the same ordinary `navigate.unitize -> read -> navigate.route` loop as any other region.

**Why it matters later**: This entry preserves why the project once chose detour over revisit. `DEC-104` supersedes that live direction: future contributors should not harden `inline_look_back`, `revisit_hop`, or live Detour as current path steering. Prior-context pressure should instead be handled by the forthcoming Ingest memory-retrieval design.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/docs/research/claude_code_context_management_research_20260412.md`

## Entry 67
**ID**: DEC-070
**Status**: superseded by `DEC-104`

**Decision / Inflection**: Land `Phase F2` by cutting the live mechanism from transitional `revisit_need` into `Navigate`-owned `detour`, with bounded hierarchical semantic search and normal-loop detour reading.

**Period**: April 19, 2026, during the implementation slice immediately after the F2 design freeze.

**Problem**: After F1 landed, the mechanism still had a mismatch between the approved design and the live runtime. The docs already said detour should belong to `Navigate`, but the live code still treated it as a transitional placeholder and had not yet made non-mainline reading a first-class navigation behavior. That left three quality risks: semantic jump-reading was not yet truly owned by `Navigate`, persistence/resume had no durable detour state, and a fresh detour raised on the last mainline unit of a chapter could still be lost before chapter slow-cycle close.

**Alternatives considered**: Keep the F1 transitional `revisit_need` name a little longer, continue relying on runner-private supplemental helpers, or postpone the cutover until later persistence cleanup work.

**Why this path won**: The cleanest next step was to finish the ownership cutover before taking on later compatibility cleanup. That keeps the reading loop simple: `Read` says another region now matters, `Navigate` searches for it in a bounded way, and once found the mechanism just keeps reading normally. By also persisting detour state in `local_continuity`, resume and chapter transitions stay honest without inventing a second reading system or a heavy retrieval subsystem.

**What changed in the system**: The live `Read` contract now emits `detour_need`. `LocalContinuityState` now persists `mainline_cursor`, `active_detour_id`, `active_detour_need`, and `detour_trace`. The runner now uses one bounded `detour-search` prompt family with `narrow_scope / land_region / defer_detour`, performs detour search before choosing the next reading region, and routes landed detour regions back through the ordinary `navigate.unitize -> read -> navigate.route` loop. Resume snapshots and read audits now preserve detour state, and chapter-tail detours are drained before chapter slow-cycle close so a final-unit detour request is not silently dropped.

**Why it matters later**: This entry marks the point where detour became live runtime behavior. `DEC-104` later retired that live behavior: future work should treat this entry as historical evidence and should not assume a current `Navigate`-owned detour mechanism.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`

## Entry 68
**ID**: DEC-071
**Status**: active

**Decision / Inflection**: Land `Phase F3` by making `Read.surfaced_reactions[]` the only internal persisted visible-reaction truth, collapsing all remaining live persistence onto one surfaced-native builder, and deleting confirmed-dead `Express` / `raw_reaction` ownership paths instead of carrying them forward as indefinite compatibility shells.

**Period**: April 19, 2026, immediately after the F2 detour cutover had already stabilized the live reading loop.

**Problem**: F2 had already restored a clean live reading loop, but the persistence and downstream-compatibility layer still had too much lingering ambiguity. Old family/type vocabulary still risked being mistaken for the internal truth, there were still dead ownership traces from the `Express` branch and the old `raw_reaction` era, and mainline versus detour persistence could drift if they continued to build reaction records through slightly different code paths. Leaving that state in place would make later cleanup harder and keep misleading future design work.

**Alternatives considered**: Keep the old persistence fallbacks “just in case”, postpone cleanup until F4 quality validation, or do a breaking public-surface redesign now instead of first cleaning the backend truth/adapter boundary.

**Why this path won**: The project already had enough information to tell which reaction paths were still real consumers and which were only dead migration scaffolding. Cleaning that boundary now keeps the system honest: surfaced reactions are the thing the reader actually produces, so they should be the only internal persisted truth. Family labels, chapter-result compatibility outputs, and normalized eval exports can remain as projections for current consumers, but they should not continue to own semantics. Deleting dead paths at the same time avoids exactly the long-tail “compat forever” drift the project is trying to avoid.

**What changed in the system**: Mainline and detour reading now share one surfaced-native reaction-record builder. Persisted reaction records are now authored directly from `Read.surfaced_reactions[]` and keep native surfaced fields such as `thought`, `primary_anchor`, `prior_link`, `outside_link`, and `search_intent` as the internal truth. Chapter-result compatibility projection and normalized eval export now derive legacy family/type/search-query fields only through the compat helper rather than by trusting old record shapes. The old dedicated `Express` persistence ownership, the live `raw_reaction` fallback path, and other confirmed-dead family-first ownership branches were deleted instead of being kept as open-ended scaffolding.

**Why it matters later**: This is the point where the project stopped merely saying “surfaced reactions are the truth” and made that statement mechanically true inside the backend. Future work on F4 quality validation, public-surface redesign, or later cleanup can now reason about one honest internal reaction model instead of a mixture of surfaced-native truth and lingering legacy ownership code.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/__init__.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/evaluation.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`
- `reading-companion-backend/tests/test_attentional_v2_bridge.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_slow_cycle.py`
- `reading-companion-backend/tests/test_attentional_v2_evaluation.py`

## Entry 69
**ID**: DEC-072
**Status**: active

**Decision / Inflection**: Remove `trigger/watch` from the live `attentional_v2` runtime entirely, shrink sentence intake back to pure local-buffer ingest, and delete the dead local-cycle ownership chain instead of preserving it as “legacy helper territory.”

**Period**: April 19, 2026, immediately after the first F4A quality audit had already validated the new `navigate.unitize -> read -> navigate.route` shape.

**Problem**: Even after F1 through F3 had landed, the repo still contained a misleading second story about how `attentional_v2` worked. The live runner no longer depended on heuristic trigger permission or the old `zoom_read -> meaning_unit_closure -> controller_decision -> reaction_emission` chain, but several internal types, exports, tests, and docs still acted as if that machinery remained a supported runtime entity. That created exactly the drift risk the project had been worried about: future contributors could mistake dead scaffolding for live design and continue optimizing or working around systems that no longer owned anything real.

**Alternatives considered**: Leave the old trigger/watch objects in place as dormant compatibility shells, keep the old local-cycle nodes as internal-only helper territory, or defer cleanup until after the next special-content or F4B quality slice.

**Why this path won**: The project already had enough evidence to know the old control path was dead. Keeping it around would not improve compatibility, because current runtime/checkpoint/resume behavior had already moved elsewhere; it would only preserve confusion. The clean move was to make the new ownership model mechanically true all the way down: sentence intake is just buffer maintenance, `Navigate.unitize` reasons from bounded state/context packets without heuristic watch packets, and the old local-cycle chain now belongs only to historical records and archived artifacts.

**What changed in the system**: `process_sentence_intake(...)` now updates only `local_buffer`. `TriggerState`, `watch_state`, `trigger_state.json`, and the related runtime/checkpoint/resume/artifact-map paths are gone from the live mechanism. The dead `trigger -> zoom_read -> meaning_unit_closure -> controller_decision -> reaction_emission` chain was removed from `attentional_v2` live code and replaced in tests with the actual live node set (`build_unitize_preview`, `navigate_unitize`, `navigate_detour_search`, `read_unit`, `navigate_route`). Prompt bundles and exports no longer carry old local-cycle prompt constants. The stable docs now also define `text_role` as an inherited block-level weak cue rather than a sentence-level truth packet.

**Why it matters later**: This is the cleanup that turns the current Runner/Navigate contract from a design preference into the only credible implementation story. Future work on special-content unitization, detour quality, and F4B validation can now build on a simpler baseline without accidentally reanimating trigger/watch semantics or the dead local-cycle chain.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reading-mechanism.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/implementation/new-reading-mechanism/runtime-artifact-map.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/intake.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/__init__.py`
- `reading-companion-backend/tests/test_attentional_v2_intake_and_retrieval.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 76
**ID**: DEC-079
**Status**: active, with Detour scheduling superseded by `DEC-104`

**Decision / Inflection**: Cut current `attentional_v2` routing vocabulary from the historical `advance / dwell / bridge / reframe` move model to the current `Navigate.route` action contract: `commit`, `continue`, `bridge_back`, and `reframe`.

**Period**: May 3, 2026, after the Runner/Navigate cleanup made clear that the old controller vocabulary was no longer the live scheduling model and was only surviving through compatibility projection.

**Problem**: The old move names came from an earlier controller design where the mechanism chose among `advance`, `dwell`, `bridge`, and `reframe`. The current mechanism no longer operates that way. It reads a semantic unit, receives one-step `pressure_signals`, and lets deterministic `Navigate.route` record the next route action. Keeping `MoveType`, `move_type`, `move_history`, and the `continue -> dwell` projection made current code, public payloads, frontend copy, and evaluation exports look as if the older controller still governed reading. It also made `continue` easy to misread as merely a renamed `dwell`, which is not the current meaning.

**Alternatives considered**: Keep `move_type` as a public compatibility field while adding `route_action`, keep double-written `move_history` and `route_history` for a transition period, or only update docs while leaving code adapters in place. These were rejected because this project phase is explicitly cleaning confirmed-dead compatibility tails rather than preserving them indefinitely.

**Why this path won**: The new contract names what the live runner actually does. `commit` accepts the current unit and advances; `continue` means the current semantic movement still has forward continuation pressure; `bridge_back` records a source-grounded callback route into the bridge-resolution helper; `reframe` records that the current unit changed the active reading frame. These are route actions, not legacy controller moves. Removing the old projection makes the route layer easier to reason about and prevents future prompt/eval/report work from reintroducing `dwell` or `bridge` as current scheduling entities.

**What changed in the system**: New runtime artifacts now write `route_history.json` containing `routes[]` with `route_action`. New runtime and checkpoint loading fail fast on pre-cutover `move_history`-only state. Public analysis-state and activity payloads now expose `route_action` instead of `move_type`; the frontend generated API type and live-chip copy now use the same field and the four current values. Normalized eval exports and current Memory Quality report-writing contracts use route evidence rather than move evidence. Historical run artifacts and archived reports are not migrated.

**Why it matters later**: Future navigation work should start from the actual loop, `Navigate.unitize -> read -> Navigate.route`, not from the abandoned move-controller vocabulary. If a later mechanism needs richer route semantics, it should extend `route_action` deliberately rather than reviving `MoveType` or treating old `advance/dwell/bridge/reframe` as still canonical.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/api-contract.md`
- `docs/api-integration.md`
- `docs/backend-state-aggregation.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/api/schemas.py`
- `reading-companion-backend/src/library/catalog.py`
- `reading-companion-frontend/src/app/components/book-overview-page.tsx`
- `reading-companion-frontend/src/app/config/controlled-copy.ts`

## Entry 76
**ID**: DEC-079
**Status**: active

**Decision / Inflection**: Naturalize the current `attentional_v2` `Read` contract from field-filling node language to reader-like reading experience. The current field names are now `reading_impression` and `memory_uptake_ops`; `unit_delta` and `implicit_uptake_ops` are historical names.

**Period**: May 3, 2026, after the Memory Quality probe review showed that important source-given structures could remain trapped in the local read audit while not settling into durable memory.

**Problem**: The previous `Read` prompt still sounded like an authoritative node filling several independent output fields. That wording made the call easier to audit structurally, but it encouraged the model to treat local understanding, visible reactions, and memory updates as parallel form fields rather than as natural consequences of one reading experience. In particular, explicit source structures such as the three-stage model in `活出生命的意义` could be described in the local read result without being carried forward into concept or thread memory, even though they are exactly the kind of framework a human reader would remember.

**Alternatives considered**: Keep the fields and only strengthen the memory-uptake checklist, add a separate post-read memory extractor node, or carry major reactions forward in prompt packaging immediately. These were rejected for this slice because they would either preserve the field-filling posture, add another node before the core prompt problem was fixed, or solve a related context-packaging problem before the `Read` call itself was made more natural.

**Why this path won**: The approved reading model is simpler: read the unit as a reader, form a natural impression, surface any underlines or margin-note style reactions that genuinely arise, then let material that should remain available settle into bounded memory operations. Visible reaction and memory uptake are both consequences of the same reading act, but they are not duplicates: a reaction is already persisted as a reaction record, while memory uptake should capture durable concepts, threads, anchors, or active attention only when they naturally need to shape later reading. Author-given frameworks, stage models, classifications, definitions, and chapter roadmaps may be remembered even when they do not call for visible commentary.

**What changed in the system**: The `ReadUnitResult` contract now exposes `reading_impression`, `surfaced_reactions[]`, `memory_uptake_ops[]`, `pressure_signals`, and optional `detour_need`. The `read_unit` prompt now addresses the model as a careful reader moving through the book, explicitly avoids a field-filling stance, and treats `memory_uptake_ops` as natural memory settlement rather than a checklist. Runtime application, read audit, route reasoning, anchor creation, prompt manifests, tests, and evaluation guidance now use the new field names. New runs do not dual-write or dual-read the old fields. Historical run artifacts and reports that contain `unit_delta` or `implicit_uptake_ops` remain readable as pre-cutover evidence.

**Why it matters later**: Future memory-quality work should diagnose whether important material naturally settles into `active_attention`, `concept_registry`, `thread_trace`, or `anchor_bank`, not whether an old local delta string happened to mention it. This entry also records why a strong visible reaction should not automatically be copied into memory: the reaction record already preserves the expressive event, while memory should preserve what must remain useful for future reading.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-state-aggregation.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 70
**ID**: DEC-073
**Status**: active

**Decision / Inflection**: Keep the note-aligned `user-level selective v1` package and the repaired strict rejudge in an explicit dual-pointer posture instead of silently promoting the repaired sibling into the active dataset pointer.

**Period**: April 19, 2026, after the repaired strict source-span rejudge had completed and the project needed a clean dataset/evidence index.

**Problem**: By this point the repo had two truths that were both real but easy to conflate. The active local/user-level package was the rebuilt `attentional_v2_user_level_selective_v1` benchmark with `5` segments and `202` note cases, while the latest completed formal judged evidence lived on the repaired sibling package with `5` segments and `203` note cases. Leaving that distinction implicit made it too easy for future contributors to mistake the repaired evidence bundle for a silent benchmark promotion, or to keep describing the completed rerun as if it were still active.

**Alternatives considered**: Quietly switch the active benchmark pointer to the repaired sibling package, keep talking about the repaired rerun as if it were still an in-flight recovery lane, or collapse both truths into one vague "current dataset" label and let readers infer the rest.

**Why this path won**: An explicit dual-pointer posture preserves honesty without forcing an unnecessary benchmark promotion decision. It lets the project keep the current active package stable for local/workbench use, while still treating the repaired strict rejudge as the current formal evidence bundle. That makes dataset identity, evidence identity, and future promotion decisions all visible instead of smuggling one into another.

**What changed in the system**: Entry docs now distinguish:
- active dataset pointer:
  - `attentional_v2_user_level_selective_v1`
  - `5` reading segments / `202` note cases
- current formal evidence bundle:
  - `attentional_v2_user_level_selective_v1_repaired_rejudge_20260416`
  - run executed on `attentional_v2_user_level_selective_v1_repaired_20260416`
  - `5` reading segments / `203` note cases

The completed repaired run now has a checked-in human interpretation report, task state is recorded as `waiting` rather than `active`, and the stopped watchdog / failed reuse lane remain preserved only as historical evidence.

**Why it matters later**: Without this entry, future agents would see the repaired package, the completed strict rejudge, and the still-active `202`-case package and have to guess which one "counts." This decision preserves the intended answer: both count, but they count in different roles until a later explicit promotion decision is made.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/user_level/attentional_v2_user_level_selective_v1_repaired_rejudge_20260416_interpretation.md`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1/manifest.json`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260416/manifest.json`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_user_level_selective_v1_repaired_rejudge_20260416/summary/aggregate.json`

## Entry 71
**ID**: DEC-074
**Status**: active

**Decision / Inflection**: Retire the temporary dual-pointer posture, promote the repaired `203`-case `user-level selective v1` package into the active benchmark pointer, and run the full active excerpt + long-span formal rerun through one durable parent orchestrator with 5-minute auto-recovery.

**Period**: April 20, 2026, once the user explicitly requested a new full V1/V2 comparison over both active benchmark levels.

**Problem**: The dual-pointer posture from Entry 70 had done its job as a repair bridge, but it was no longer the cleanest operating model once the project was ready to rerun the full active benchmark stack. Keeping the active pointer on the older `202`-case package would have forced long-span v2 to keep reusing the wrong substrate root, while also making the new formal rerun semantically ambiguous: some docs would describe the repaired package as "formal evidence only" even though the actual requested run needed that repaired package to be the real active truth. At the same time, the project needed a durable execution shape so a full rerun could survive provider failures and resume from completed shard outputs rather than restarting from scratch.

**Alternatives considered**: Keep the older `202`-case package as the active pointer and run against a hidden repaired sibling again, leave excerpt and long-span as two fully separate rerun lanes that reread overlapping windows, or keep long-running recovery behavior as an operator-only manual ritual instead of encoding it in the orchestration layer.

**Why this path won**: Once the user explicitly asked for the full active rerun, the "temporary dual truth" cost became higher than the "explicit promotion" cost. Promoting the repaired package makes the benchmark identity honest again: the active excerpt substrate is the repaired `203`-case package, and long-span v2 reuses that same repaired substrate. Encoding the rerun as one parent orchestration line plus recoverable child jobs also turns the previously manual restart playbook into a durable system behavior instead of relying on memory or chat history.

**What changed in the system**: The active excerpt split manifest now points at `attentional_v2_user_level_selective_v1_repaired_20260416`, while the older `attentional_v2_user_level_selective_v1` package is preserved on disk but marked `superseded`. `run_accumulation_evaluation_v2.py` now supports `--reuse-output-dir`, excerpt and long-span reuse both rely on one shared completed-output rebuild helper, and the user-level orchestrator now supports same-run completed-shard reuse in addition to seed-run reuse. Two new durable orchestrators now exist: `orchestrate_accumulation_v2_eval.py` and `orchestrate_active_benchmark_eval.py`. The current formal rerun is now owned by:
- parent:
  - `bgjob_active_benchmark_rerun_20260419`
  - `attentional_v2_active_benchmark_rerun_20260419`
- shared watchdog:
  - `bgjob_job_registry_auto_recovery_watchdog_active_benchmark_20260419`
- excerpt child:
  - `bgjob_user_level_selective_v1_active_formal_20260419`
  - `attentional_v2_user_level_selective_v1_active_rerun_20260419`

The accumulation child is queued behind the same parent and will reuse overlapping excerpt outputs for the three shared windows instead of rereading them.

**Why it matters later**: This is the point where the repaired package stops being "special repair evidence" and becomes the normal active truth. Future agents no longer need to infer which excerpt substrate long-span v2 should reuse, and the next full rerun can be resumed from the registry plus completed outputs instead of being reconstructed from chat.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `docs/history/decision-log.md`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md`
- `reading-companion-backend/eval/attentional_v2/completed_output_reuse.py`
- `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- `reading-companion-backend/eval/attentional_v2/run_accumulation_evaluation_v2.py`
- `reading-companion-backend/eval/attentional_v2/user_level_selective_v1.py`
- `reading-companion-backend/eval/attentional_v2/accumulation_benchmark_v2.py`
- `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- `reading-companion-backend/eval/manifests/splits/attentional_v2_accumulation_benchmark_v2_frozen.json`
- `reading-companion-backend/scripts/orchestrate_user_level_selective_eval.py`
- `reading-companion-backend/scripts/orchestrate_accumulation_v2_eval.py`
- `reading-companion-backend/scripts/orchestrate_active_benchmark_eval.py`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1/manifest.json`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260416/manifest.json`

## Entry 72
**ID**: DEC-075
**Status**: active

**Decision / Inflection**: Move support-material ordering out of `Navigate` and into a survey-led `body-first` chapter scheduling layer, where `survey` classifies chapter zones and `runner` executes the resulting reading plan without mutating parse-order source truth.

**Period**: April 22, 2026, after the trigger/watch cleanup, the first special-content unitization slice, and the follow-up discussion about how prefaces, introductions, appendices, and afterwords should enter the live reading flow.

**Problem**: The project had already cleaned up sentence-level special-content handling inside `navigate.unitize`, but book-level support material still sat on an awkward boundary. Treating `Preface`, `Introduction`, `Appendix`, or `Afterword` as unconditional mainline reading made some books feel unlike normal reading practice, while asking `Navigate` to improvise whole-book order at runtime would have turned a local unit-selection node back into a control center. At the same time, keeping chapter-role classification purely heuristic risked a high-leverage upstream mistake: a bad chapter-role guess would distort the whole run's reading order and be amplified by later reading.

**Alternatives considered**: Keep all non-auxiliary chapters in source order, let `Navigate` infer support-vs-mainline order ad hoc during reading, or mutate parse-time chapter order so the source substrate itself becomes "body first."

**Why this path won**: The winning split preserves simplicity and source truth at the same time. `parse` continues to expose the book as it really is. `survey` is the right layer to make one narrow structural judgment, because it already sits between raw substrate and live reading and can cheaply inspect bounded chapter samples. `runner` is the right place to execute the resulting queue, because it already owns whole-run progression. This keeps `Navigate` local: it still decides how to unitize and where to detour within the currently active chapter/zone, but not how to reorder the book.

**What changed in the system**: `survey` now runs one bounded LLM-backed `chapter_zone` classifier over lightweight structural samples and emits both chapter-level zones and a machine-readable `reading_plan`. The legal scheduling zones are now `main_body`, `front_support`, `back_support`, and `auxiliary`. `runner` consumes that plan in full-book mode and drains `main_body` chapters before deferred support chapters. Explicit chapter-targeted reads and benchmark-window reads still bypass that queue rather than being forcibly reordered. Runtime continuity and resume shell now also carry a lightweight `reading_queue_stage` so the live run can expose whether it is in the mainline or deferred-support queue. Parse-order chapter ids and sentence ids remain the only source-of-truth locators; no new chapter primary key was introduced.

**Why it matters later**: This is the decision that keeps future special-content work from collapsing back into prompt-only improvisation. It gives the mechanism a realistic "body first, support later" default without making survey into hidden reading or making navigate into a book-level planner. It also creates a clean place for later refinements, such as validating support-heavy books or improving chapter-zone classification, without reopening parse-order truth or unit-selection ownership.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-sequential-lifecycle.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/survey.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/tests/test_attentional_v2_survey.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 73
**ID**: DEC-076
**Status**: active

**Decision / Inflection**: Retire `target-centered accumulation v2` as the active Long Span methodology and replace it with a new three-metric direction centered on `Memory Quality`, `Spontaneous Callback`, and `False Visible Integration`.

**Period**: April 22, 2026, after the April 22 rejudge repaired the old target-visible evidence contract, but the project concluded that the underlying Long Span product question itself had shifted.

**Problem**: The April 22 rejudge fixed a real bug in the `target-centered accumulation v2` route: it stopped giving credit from the target passage itself or from pre-target callbacks that never became target-visible mechanism evidence. But once that contract was repaired, a more fundamental issue became hard to ignore: the route was still asking the wrong first-order question for the current stage of the project. It was still centered on whether the Reader visibly reconstructed one prepared thread at one target point. The project had by then clarified that its nearer-term goal was different: verify that the Reader is actually reading continuously, forming high-quality memory over time, naturally callbacking prior material when it makes sense, and not inventing false visible integrations. Continuing to treat target-point visible reconstruction as the active Long Span authority would have kept the benchmark focused on prompt-facing visibility rather than on the context-management and memory-quality behavior the product now wanted to validate.

**Alternatives considered**: Keep `target-centered accumulation v2` as the active Long Span route and merely soften the interpretation of its scores, continue to treat the April 22 rejudge as the current formal Long Span authority while adding a second memory-oriented benchmark beside it, or abandon Long Span work entirely until a later product phase clarified visible integration requirements.

**Why this path won**: The new direction better matches the product question the team actually wants answered now. `Memory Quality` directly tests whether continuous reading produces retained, organized, mainline-faithful memory rather than isolated local interpretations. `Spontaneous Callback` gives a lightweight observable check that the Reader is not reading each unit as a disconnected sample. `False Visible Integration` keeps that callback pressure honest by penalizing overclaim, hard-linking, and drift. Together they test the value of the new context-management system much more directly than a single prepared target-point reconstruction question. This route also avoids conflating prompt style with memory quality: a mechanism can remember without always visibly restating its memory at one curated target, so the old target-centered question was too easy to misread as a memory verdict.

**What changed in the system**: Stable evaluation authority now explicitly treats `target-centered accumulation v2` as a discontinued / invalidated historical route whose runs, manifests, case sets, and audit docs remain preserved but no longer define the active Long Span methodology. The active Long Span direction in stable docs is now:
- `Memory Quality`
- `Spontaneous Callback`
- `False Visible Integration`

This new direction is design frozen but not yet implemented as a formal benchmark run. The first intended substrate remains the active `user-level selective v1` reading windows, but the benchmark contract will shift from prepared target cases to probe-based memory snapshots plus complete-window reaction audits.

**Why it matters later**: Without this entry, future contributors would see the April 22 rejudge, note that it fixed the old contract, and reasonably infer that `target-centered accumulation v2` remained the active Long Span authority. That would reopen exactly the wrong optimization loop: improving target-point visible reconstruction when the current project need is to validate continuous-reading memory quality and grounded callback behavior. This entry records the deeper route change so later work can distinguish “a repaired old method” from “the current method direction.”

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.json`
- `reading-companion-backend/docs/evaluation/evidence_catalog.md`

## Entry 74
**ID**: DEC-077
**Status**: superseded / refined by `DEC-078`

**Decision / Inflection**: Remove the legacy `gate_state / pressure_snapshot / working_pressure` sidecar from current `attentional_v2` state, prompt packets, runtime artifacts, checkpoint/resume, and Memory Quality evidence. Keep `working_state.active_items` as the current hot-state contract, and keep `pressure_signals` only as one-step `Read -> Navigate.route` signals.

**Period**: May 3, 2026, after the Memory Quality probe-audit report made the old control-door fields visible again and the project decided they were now misleading rather than useful compatibility.

**Problem**: The old trigger/watch/zoom design had left behind several control-door surfaces: `gate_state`, `pressure_snapshot`, a separate working-pressure runtime artifact, and related policy/default shells. Earlier phases had already removed the live trigger/watch path, but these sidecars still appeared in state schemas, projection helpers, runtime maps, resume handling, and Memory Quality audit explanations. That made the current mechanism look more complicated and more controller-driven than it actually is, and it risked misleading both humans and future agents into treating historical control scaffolding as current reader memory.

**Alternatives considered**: Keep the fields as legacy compatibility sidecars and merely label them as historical in reports, continue migrating old working-pressure files into current working state on resume, or remove only the report display while leaving the runtime/schema surfaces intact.

**Why this path won**: The current mechanism no longer needs these entities. The live reader's hot state is `working_state.active_items`, while the current route handoff is handled by per-step `pressure_signals`. Keeping a second old pressure/gate object would add complexity without improving reading, evaluation, or product behavior. Failing fast on pre-cutover runtime directories is cleaner than pretending old sidecars can be safely migrated into the current contract, because old run artifacts remain available as historical evidence but should not be treated as resumable current truth.

**What changed in the system**: `WorkingState` no longer inherits or projects the old working-pressure structure. Current prompt packets and carry-forward context no longer contain `working_pressure_digest`, `gate_state`, or `pressure_snapshot`. New runtime shells and checkpoints no longer create or read a working-pressure file, and pre-cutover runtime directories that only contain legacy pressure/anchor/reflective sidecars now fail fast with a re-run requirement. Slow-cycle carry-forward now writes directly into `working_state.active_items`. Memory Quality evidence docs now describe probe snapshots in terms of current prompt-facing state rather than old control-door fields. Public API and frontend payloads did not change.

**Why it matters later**: This is the cleanup point where `attentional_v2` stops carrying a compatibility shadow from an abandoned trigger/watch/zoom route. Future context-memory work should build on `working_state.active_items`, `concept_registry`, `thread_trace`, `reflective_frames`, and `anchor_bank`, not resurrect `gate_state` or `working_pressure` as if they were still live state. If historical reports show those fields, they should be read as pre-cleanup artifacts, not current mechanism authority.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-state-aggregation.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Entry 75
**ID**: DEC-078
**Status**: active

**Decision / Inflection**: Rename the current `attentional_v2` hot-state contract from `Working State` to `Active Attention`. The current native runtime truth is now `active_attention.active_items[]`, and each item carries lightweight `attention_tags[]` rather than a fixed `kind / bucket` ontology or the old derived lists `open_questions / live_tensions / live_hypotheses / live_motifs`.

**Period**: May 3, 2026, after the Memory Quality report review exposed that the old `Working State` name and fixed sublists made the hot attention layer look broader, more categorical, and more ontological than the mechanism now intends.

**Problem**: After the legacy gate/pressure cleanup, the remaining hot-state layer still used a name that was too broad. `Working State` sounded like it might cover the whole live agent state, even though concept memory, thread memory, reflective frames, anchors, audit history, and active focus are separate layers. The fixed `kind / bucket` vocabulary also made `live_hypotheses` and related lists look like durable categories, which encouraged over-reading ordinary local uptake as formal interpretation or long-term memory.

**Alternatives considered**: Keep the current code and clarify only in generated reports, keep `working_state` as a compatibility alias while also writing `active_attention`, or preserve fixed buckets as first-class categories. These options were rejected because they would leave another compatibility tail in the current mechanism contract and keep inviting future agents to treat a convenience classification as the ontology of the reader.

**Why this path won**: `Active Attention` names the layer by its real role: a hot, near-term attention surface that keeps items likely to shape the next stretch of reading. Lightweight `attention_tags[]` preserve useful labels such as `question`, `tension`, `interpretation`, `motif`, and `focus` without turning them into routing contracts or exhaustive buckets. This keeps the state hierarchy simple: `active_attention` for hot attention, `concept_registry` and `thread_trace` for longer memory, `reflective_frames` for slow chapter/book understanding, and `anchor_bank` for source-grounded evidence.

**What changed in the system**: Current schemas, runtime artifacts, checkpoints, state operations, prompt packets, Memory Quality probe export, and documentation now use `active_attention`. New runs create `active_attention.json`, not `working_state.json`. `StateOperation.target_store` uses `active_attention`. Current prompt-facing digests expose compact `active_items[]` with `attention_tags[]` and no longer emit `open_questions / live_tensions / live_hypotheses / live_motifs` as current lists. Old run artifacts and reports keep their original field names as historical evidence, but old-only `working_state` runtime/checkpoint state is not a supported warm-resume target for the current contract.

**Why it matters later**: Future memory work should not add new fixed hot-state buckets by default. If a reading pattern needs to be remembered briefly, it should usually become an `active_attention.active_items[]` entry with tags. If it becomes durable, it should graduate into `concept_registry`, `thread_trace`, or `reflective_frames`. This prevents the hot layer from becoming a dumping ground and keeps the distinction between current attention and long-distance memory crisp.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-state-aggregation.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/tests/test_attentional_v2_state_ops.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`
- `reading-companion-backend/tests/test_attentional_v2_resume.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 76
**ID**: DEC-079
**Status**: active, with Detour scheduling superseded by `DEC-104`

**Decision / Inflection**: Retire `Navigate.route` and the `commit / continue / bridge_back / reframe` route-action taxonomy from current `attentional_v2`. Forward reading became settled by the Reading Runner after `Read`; at that time, `Detour` remained the only non-mainline scheduling mechanism.

**Period**: May 4, 2026, after the project re-examined whether the remaining route-action layer still had a first-principles role after Read naturalization, Active Attention cleanup, and Detour ownership had landed.

**Problem**: The route-action layer survived several earlier cleanups because it was once a useful bridge away from older `advance / dwell / bridge / reframe` controller vocabulary. But after the mechanism stabilized around `Navigate.unitize -> read -> Reading Runner settlement`, the four current route actions no longer owned distinct behavior. Ordinary forward progress was already cursor progression performed by the Reading Runner. `Read` already owned memory uptake, surfaced reactions, and detour need. At that time, `Detour` owned non-mainline scheduling; `DEC-104` later superseded that part. `bridge_back` and `reframe` had become historical controller echoes rather than meaningful current scheduling actions.

**Alternatives considered**: Keep `route_action` as a public/eval explanation chip, collapse the taxonomy into a single `forward` action, or migrate `bridge_back` / `reframe` effects into `Read`. These were rejected because they would preserve a taxonomy for something that is now ordinary control flow. A single `forward` action would still make default cursor advancement look like a semantic decision, and migrating bridge/reframe would risk reintroducing low-value derived state updates that the current memory model no longer needs.

**Why this path won**: The simplest true model is also the most universal: `Navigate` chooses the next unit, `Read` reads the chosen unit and emits memory/reaction outputs, and the Reading Runner deterministically settles that read and advances the cursor. At the time this decision landed, non-mainline movement was concentrated in the explicit Detour mechanism; `DEC-104` later superseded that Detour scheduling part and made the current live path forward-only.

**What changed in the system**: The Reading Runner no longer calls `navigate_route`. `ReadResult` no longer emits `pressure_signals`. New runtime state no longer creates `route_history.json`, and old `route_history` / `move_history` runtime state fails fast on warm resume rather than being migrated. Public schemas, OpenAPI-generated frontend types, overview live-chip copy, normalized eval export, and Memory Quality probe support no longer expose `route_action` as current evidence. Stable mechanism/API/evaluation/current-state docs now describe post-read settlement as Reading Runner-owned deterministic behavior.

**Why it matters later**: Future navigation work should not resurrect a generic route taxonomy unless it creates a real scheduling capability. After `DEC-104`, the current mechanism also should not revive Detour as the default way to leave the mainline. If it is simply done reading the chosen unit, the Reading Runner advances. If a reaction links backward, the surfaced reaction and source evidence should carry that linkage rather than a route action.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/api-contract.md`
- `docs/api-integration.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-state-aggregation.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/api/schemas.py`
- `reading-companion-frontend/src/app/components/book-overview-page.tsx`
- `reading-companion-frontend/src/app/lib/generated/api-schema.d.ts`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`

## Entry 77
**ID**: DEC-080
**Status**: partially superseded by `DEC-104`

**Decision / Inflection**: Make `Navigate.choose_next_unit` the current `attentional_v2` Navigator contract. Its mechanism-level meaning is **Choose Next Unit That Should Be Read**.

**Period**: May 4, 2026, after `Navigate.route` and route-action vocabulary had been removed, and after the project reviewed whether mainline unitization and detour search should remain exposed as parallel current Navigator surfaces.

**Problem**: Once route actions were gone, the Reading Runner still effectively had two selection shapes: ordinary mainline unitization and a separate detour episode branch that performed its own search, unitization, read, and settlement flow. That split made the current mechanism harder to reason about than its actual first-principles model: every turn needs one next unit to read, whether it comes from the mainline cursor or from an already-open detour need. Leaving `Navigate.unitize` and `Navigate.detour_search` as parallel architecture-level nodes also risked rebuilding another controller taxonomy after the route cleanup.

**Alternatives considered**: Keep `Navigate.unitize` and `Navigate.detour_search` as two public mechanism nodes, rename the entrypoint to `prepare_next_unit`, or immediately introduce a tool/skill loop for source search. These were rejected for this slice. Keeping two public nodes preserved unnecessary ontology. `prepare_next_unit` sounded more like prompt packaging than selection. Tool/skill design may be useful later, but it would expand the scope beyond the current contract cleanup.

**Why this path won**: `choose_next_unit` states the universal job directly: select the next readable unit that should be read now. Mainline forward reading and detour reading become two modes inside one selection contract, not two separate scheduling systems. The Reading Runner can then consume one `NavigateNextUnitResult` and send both mainline and landed-detour units through the same `Read -> Reading Runner settlement` path.

**What changed in the system**: The schema then added `NavigateNextUnitResult` with `selection_mode = mainline | detour | deferred`, selected unit sentences, unitization decision, optional detour trace, and optional defer reason. The Reading Runner began calling `navigate_choose_next_unit(...)` each loop. Without an active detour it reused the existing bounded preview and unitization helper; with an active detour it ran the existing bounded detour search, unitized the landed region, and returned a normal read unit. Mainline and detour reads shared one settlement helper. The previous `_run_detour_episode(...)` duplicate read/settlement branch was removed. `DEC-104` later retired the live detour/deferred modes; the surviving current point from this decision is the forward `Navigate` LLM-call boundary.

**Why it matters later**: Future navigation work should start from `Navigate.choose_next_unit`, not from reintroducing route actions. The historical detour/source-search part of this decision is superseded by `DEC-104`; future Ingest retrieval should be designed separately rather than reviving detour search as a side channel.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`

## Entry 78
**ID**: DEC-081
**Status**: active, with detour wording superseded by `DEC-104`

**Decision / Inflection**: Name the current `attentional_v2` mechanism-internal read-progress executor `Reading Runner`.

**Period**: May 4, 2026, after the project clarified that this naming work is scoped to the current mechanism internals rather than to the shared runtime shell or mechanism registry.

**Problem**: The word `runner` was doing too much work. The shared runtime shell, mechanism adapters, evaluation runners, and the current mechanism's live read loop all used runner-like language. That made it easy to mistake `reading-companion-backend/src/attentional_v2/runner.py` for the whole product runtime or to keep describing current behavior through rollout-era `V2` / phase labels instead of through stable reading roles.

**Alternatives considered**: Rename the shared runtime layer, rename the `attentional_v2` package/key, or split/rename the whole mechanism directory immediately. These were rejected because the current issue is narrower: the project only needs a clear name for the current mechanism's internal read-progress executor. Shared `reading_runtime`, mechanism registration, adapter keys, historical artifacts, and old reports should remain stable.

**Why this path won**: `Reading Runner` says what this layer actually does: it executes the live reading loop for the current mechanism by calling `Navigate.choose_next_unit`, invoking `Read`, settling memory/reactions/audit, and advancing the cursor. At the time of this decision it also handed off detour state; that part is historical after `DEC-104`. The name clarifies the mechanism without making `V2` a node name and without disturbing the shared multi-mechanism architecture.

**What changed in the system**: The mechanism adapter now calls `run_reading_runner(...)` for reads. The current mechanism label no longer says `Attentional V2 scaffold (Phase 1-8)`. Stable mechanism/current-state/task docs now define `Reading Runner` as an `attentional_v2`-internal role rather than the shared runtime shell.

**Why it matters later**: Future SQL/tool/skill-loop work should not start by overloading `runner` again. If it concerns the current mechanism's live read loop, it belongs to the Reading Runner boundary. If it concerns shared product job lifecycle, mechanism registration, or cross-mechanism routing, it belongs to `reading_runtime` or the adapter layer.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/reading_mechanisms/attentional_v2.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/evaluation.py`
- `reading-companion-backend/tests/test_long_span_vnext.py`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`

## Entry 79
**ID**: DEC-082
**Status**: superseded by `DEC-104`

**Decision / Inflection**: Add a mechanism-private book-local Skill Runtime for `Navigate.choose_next_unit`, first used only by detour search.

**Period**: May 4, 2026, after the current mechanism had been reduced to `Navigate.choose_next_unit -> Read -> Reading Runner settlement`, and after the project clarified that future source-search capability should support the Navigator without turning the Reading Runner into the semantic owner.

**Problem**: Detour search needs source-grounded evidence beyond the current coarse scope, but the project does not want to push semantic search ownership into the Reading Runner. The Reading Runner should keep executing the loop and maintaining cursor/runtime state. Navigate should decide where to read next. At the same time, asking Navigate to hallucinate locations from memory alone would make detour localization brittle, while adding a broad generic tool loop or WebSearch now would over-expand the mechanism.

**Alternatives considered**: Keep detour search limited to prebuilt scope cards, let the Reading Runner perform programmatic semantic retrieval, add a generic native tool loop for all LLM nodes immediately, or let `Read` call source/web skills in the same slice. These were rejected because they either underpower Navigate, give semantic choice to the wrong layer, or make the first skill slice too large. The project deliberately starts with book-local source evidence for Navigate detours only.

**Why this path won**: The Skill Runtime preserves the clean responsibilities from the recent loop cleanup. Navigate can request bounded evidence; the Reading Runner dispatches the request and feeds back the result; the Skill Runtime enforces known skill names, argument boundaries, source visibility, errors, and provenance. Skills never choose the answer, never read future text, and never call external services. That keeps `Navigate.choose_next_unit` universal while giving detour search a controlled way to inspect the already-read book.

**What changed in the system**: `attentional_v2/skills/` now defines `SkillRequest`, `SkillResult`, the skill dispatcher, and four first-phase book-local skills: `source_map_overview`, `source_scope_drilldown`, `source_window_fetch`, and `anchor_resolve`. `Navigate.detour_search` may now return `decision=request_skill` with one `skill_request`. The detour search loop executes at most one skill request per search attempt, passes the result back into the same prompt family, and still enforces the existing three-attempt cap. Final `land_region`, `narrow_scope`, or `defer_detour` decisions remain Navigate-owned. Mainline unitization and `Read` do not call skills in this slice.

**Why it matters later**: This entry is historical evidence for why the project briefly tried a book-local source-skill runtime. `DEC-104` supersedes it for the live path: the Skill Runtime is deprecated compatibility/reference surface, and future Ingest memory retrieval should not inherit this source-skill loop by default.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/skills/`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/tests/test_attentional_v2_skills.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`

## Entry 80
**ID**: DEC-083
**Status**: partially superseded by `DEC-104`

**Decision / Inflection**: Collapse current Navigate execution into one unified `Navigate.choose_next_unit` agent act loop.

**Period**: May 4, 2026, after the first book-local Skill Runtime slice and after the project reviewed whether the remaining Navigator implementation still carried a historical mainline-vs-detour split.

**Problem**: `Navigate.choose_next_unit` had become the conceptual Navigator contract, but its implementation still acted like a Python dispatcher between two live prompt families: a mainline unitization helper and a detour-search helper. That kept the older `navigate_unitize / navigate_detour_search` split alive as current mechanism shape, made Detour feel like a side-channel, and obscured the simpler first-principles model: Navigate should choose the next readable unit that should be read.

**Alternatives considered**: Keep the current dispatcher and treat the two helper prompts as implementation details, rename the entrypoint again, or introduce a full generic native tool loop immediately. These were rejected for this slice. The dispatcher preserved too much old ontology, another rename would not fix the execution model, and a generic tool loop would add scope before the current source-skill boundary has earned it.

**Why this path won**: One Navigate act loop matches the mechanism's natural division of labor: Navigate chooses the next readable unit, Skills provide bounded source evidence when requested, and the Reading Runner executes and settles the chosen unit. Mainline and detour reading become modes inside one selection act rather than two competing navigation systems.

**What changed in the system**: The live path no longer called separate `navigate_unitize(...)` or `navigate_detour_search(...)` nodes. `navigate_choose_next_unit_act(...)` became the current prompt/trace node and could return `choose_unit`, `request_skill`, or `defer_detour`. Mainline calls ran with `skills_allowed=false` and fell back safely if the model requested a skill or defer. Active-detour calls used the same act loop, could request bounded book-local source skills within budget, and then either choose a source-grounded unit or defer. `NavigateNextUnitResult` carried a compact `navigate_trace`, while the Reading Runner sent both mainline and detour units through the same `Read -> Reading Runner settlement` path. `DEC-104` later retired the live `request_skill` / `defer_detour` / detour behavior; current `navigate_choose_next_unit_act(...)` is forward-only and normalizes those deprecated shapes to safe mainline fallback.

**Why it matters later**: The surviving lesson is the single Navigate entrypoint, not the old source-skill loop. Future Ingest retrieval should be designed as a new retrieval context path for the selected forward unit rather than by extending deprecated active-detour skill behavior.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`

## Entry 81
**ID**: DEC-084
**Status**: active

**Decision / Inflection**: Make Long Span vNext `Memory Quality` probes semantic-manifest-driven instead of hard-ratio-driven.

**Period**: May 4, 2026, after reviewing the first Memory Quality report and noticing that the old probe map selected `20% / 40% / 60% / 80% / end` checkpoints mechanically.

**Problem**: Hard ratio checkpoints are easy to automate but not always fair to a reading-memory audit. A probe can land in the middle of a semantic movement, forcing the judge to inspect a snapshot at an awkward point. The project only has five active windows, so one-time semantic probe selection is cheap and produces a better durable evaluation contract.

**Alternatives considered**: Keep the fixed ratio schedule, keep ratio targets but round to the next paragraph boundary, or let the runtime pick probes dynamically during reading. These were rejected. Fixed ratios were the problem. Paragraph-only rounding still ignores semantic structure. Runtime-dynamic probe selection would mix reading behavior and evaluation design, making runs harder to compare.

**Why this path won**: A versioned semantic probe manifest gives stable, reviewable probe points while preserving the runtime rule that reading is not interrupted for probes. Distance remains a distribution reference, but the selected sentence must be a meaningful semantic boundary with a rationale and structural signals to check.

**What changed in the system**: `memory_quality_semantic_probe_plan_20260504.json` now records five semantic probe targets for each active window. `benchmark_probes.py` requires explicit `probe_targets` when Memory Quality probe export is enabled and fails fast if they are missing. `run_long_span_vnext.py` loads the semantic manifest, injects targets into V2 reading config, and records `probe_plan_id`, `probe_plan_path`, and `probe_selection_method` in run metadata and summary output. The Memory Quality report contract and Long Span evaluation docs now describe probe placement as semantic-manifest-driven.

**Why it matters later**: The next complete Memory Quality run must use this manifest. Old April hard-ratio probe reports remain historical evidence, but they should not be treated as the current probe-placement contract.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/docs/evaluation/long_span/memory_quality_report_contract.md`
- `reading-companion-backend/eval/manifests/probes/README.md`
- `reading-companion-backend/eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json`
- `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- `reading-companion-backend/src/attentional_v2/benchmark_probes.py`
- `reading-companion-backend/tests/test_long_span_vnext.py`

## Entry 82
**ID**: DEC-085
**Status**: active

**Decision / Inflection**: Route `attentional_v2` runtime audit and Memory Quality probe capture through one observability boundary.

**Period**: May 5, 2026, after the V2-only semantic-probe evaluation exposed a visibility gap between `Read` memory uptake and durable runtime state.

**Problem**: `read_audit.jsonl` already recorded the naturalized Read output, but it did not persist `memory_uptake_ops`, so the project could not tell from audit artifacts whether durable memory weakness came from Read output, operation normalization, settlement, or later persistence. At the same time, Reading Runner directly called the Memory Quality probe exporter, leaving an evaluation concern visibly wired into the main reading loop.

**Alternatives considered**: Keep the current local audit helpers and only add the missing field, move all probe code entirely into the eval runner, or introduce a heavy per-unit settlement snapshot immediately. These were rejected for this slice. A field-only patch would leave the boundary messy, eval-only capture would lose the precise post-settlement runtime moment, and full settlement snapshots would add storage and design scope before the first observability cleanup had landed.

**Why this path won**: Reading Runner is the right owner of lifecycle timing, but not of audit schema details or benchmark semantics. A runtime observability layer can receive lifecycle events, write canonical audit artifacts, and expose optional eval consumers while preserving the product path's low-overhead standard mode.

**What changed in the system**: `attentional_v2/observability.py` now owns the runtime audit writers for unitization/read audit and the optional Memory Quality probe capture hook. `read_audit.jsonl` remains the canonical read audit artifact and now records normalized `memory_uptake_ops`, their count, and counts by target store. `unitization_audit.jsonl` remains the canonical unitization audit artifact. Reading Runner now calls `record_unitization`, `record_read`, and `maybe_capture_memory_quality_probe` instead of directly calling scattered audit writers or the benchmark probe persistence function. `benchmark_probes.py` still implements the Memory Quality export, but it is now an observability consumer rather than a Runner-owned concern.

**Why it matters later**: Future settlement audit work should attach to this observability boundary as compact transaction evidence, not by mixing diagnostic fields into Read prompts, state operations, or judge code. Normal product runs should keep avoiding Memory Quality snapshot construction unless the probe export is explicitly enabled with semantic targets.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/benchmark_probes.py`
- `reading-companion-backend/tests/test_attentional_v2_phase_b.py`
- `reading-companion-backend/tests/test_long_span_vnext.py`

## Entry 83
**ID**: DEC-086
**Status**: active

**Decision / Inflection**: Add lightweight per-unit settlement audit for `attentional_v2`.

**Period**: May 5, 2026, immediately after the runtime observability boundary refactor.

**Problem**: `read_audit.jsonl` now exposes the `memory_uptake_ops` proposed by `Read`, but that still leaves a missing link between proposed memory updates and actual runtime state changes. Without a settlement transaction record, durable-memory debugging still has to infer whether a weak final `concept_registry`, `thread_trace`, or `anchor_bank` came from absent Read ops, state-op filtering, reaction persistence, or later bundle persistence.

**Alternatives considered**: Save full per-unit state snapshots, instrument `state_ops` to return per-op accepted/skipped/invalid classifications, or keep relying on sparse Memory Quality probe snapshots. These were rejected for this slice. Full snapshots would bloat standard runtime artifacts, per-op instrumentation would change the state-op interface before the first transaction audit is proven useful, and probe snapshots are evaluation samples rather than a per-unit runtime audit trail.

**Why this path won**: A compact deterministic before/after diff gives enough evidence to trace state movement without adding LLM interpretation, full-state storage, or new reader semantics. It fits the existing observability boundary: Reading Runner owns the exact settlement timing, while `observability.py` owns the audit schema and persistence.

**What changed in the system**: `_mechanisms/attentional_v2/runtime/settlement_audit.jsonl` is now a canonical runtime audit artifact. Each row records the unit location, memory-op count and target-store distribution, and compact before/after deltas for active attention items, concept entries, thread entries, anchor records/relations, and reaction records. The audit does not persist raw prompt/response payloads, full state snapshots, or per-op accepted/skipped judgments.

**Why it matters later**: Future durable-memory investigations can line up `read_audit.jsonl`, `settlement_audit.jsonl`, and Memory Quality probe snapshots to distinguish “Read did not propose memory,” “settlement did not materialize it,” and “prompt-facing sampled state lost or failed to expose it.” If exact per-op filtering becomes necessary, it should be a later state-op instrumentation pass rather than hidden inside the first transaction audit.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 84
**ID**: DEC-087
**Status**: active

**Decision / Inflection**: Move `attentional_v2` mainline progress from sentence-id traversal to paragraph-offset source spans.

**Period**: May 5, 2026, after the project clarified that the reading unit should be chosen during reading by `Navigate.choose_next_unit`, while paragraph text provides the stable source substrate and character offsets provide exact coordinates.

**Problem**: The earlier V2 implementation had escaped V1's section/subsection pre-cutting, but still kept sentence ids as the mainline cursor and preview lattice. That risked turning sentence splitting into a hidden pre-reading segmentation step and made boundary quality depend on a preprocessing decision that is not the essence of reading. The mechanism needed ordered coverage, exact resume, and source-reference coordinates without making sentences the unit of reading.

**Alternatives considered**: Keep sentence ids as the mainline cursor, introduce smaller micro-spans or boundary handles, or ask the LLM to return raw numeric offsets. These were rejected. Sentence ids preserved too much of the old pre-cut lattice. Micro-spans and boundary handles would add new substrate complexity. Raw LLM offsets would be brittle and would make cursor correctness depend on model arithmetic.

**Why this path won**: Paragraph + char offset is simple, universal, and source-native. The book is already made of ordered paragraphs and character positions. `Navigate` can choose a natural unit by quoting exact end-anchor text from a bounded preview, while the Reading Runner deterministically resolves that quote to an end cursor. This keeps the semantic boundary decision with `Navigate` and the coordinate correctness with program logic.

**What changed in the system**: `attentional_v2` now has `SourceCursor` / `SourceSpan` helpers and an adaptive paragraph-offset preview builder. Mainline `Navigate.choose_next_unit` receives source text and paragraph slices and returns `end_anchor_text`. The Reading Runner resolves that anchor, reads `current_unit_source`, advances the mainline cursor to `end_cursor`, and appends `_mechanisms/attentional_v2/runtime/unit_span_ledger.jsonl` for accepted mainline units. Shared cursor payloads now support `position_kind = "span"` with paragraph-offset cursor data. Sentence records remain available for legacy/eval/detour compatibility, but they no longer define the `attentional_v2` mainline reading lattice.

**Why it matters later**: Future memory, reaction, source-anchor, and probe locator work should move toward source-span coordinates instead of reinforcing sentence-shaped payloads. Old sentence-target manifests and public compatibility projections can stay isolated, but they should not steer new mechanism design. The Unit Span Ledger is the durable reading-history fact to use for resume validation, coverage checks, and later source-grounding migrations.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/unit_span_ledger.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/reading_core/runtime_contracts.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 85
**ID**: DEC-088
**Status**: active

**Decision / Inflection**: Retire `Anchor Bank` from new `attentional_v2` runtime truth and unify source citation around inline paragraph-offset `SourceRef`.

**Period**: May 6, 2026, immediately after the paragraph-offset cursor and Unit Span Ledger cutover.

**Problem**: Once the mechanism's source coordinate became paragraph + char offset, `anchor_bank` stopped being necessary as a separate evidence registry. The earlier anchor layer existed partly because sentence ids were too coarse for precise quotes and partly because bridge/relation experiments wanted an evidence store. Keeping a central Anchor Bank after SourceCursor/SourceSpan landed would add a second source-coordinate truth, reintroduce compatibility drag, and obscure which state object actually owns a memory or reaction's evidence.

**Alternatives considered**: Keep Anchor Bank as a narrow evidence registry, introduce a new `SourceRef Bank`, or migrate old runtime/report artifacts into the new shape. These were rejected. A retained bank would preserve the extra registry problem under a different rationale. A `SourceRef Bank` would repeat the same centralization under a new name. Migrating old artifacts would spend effort on historical outputs rather than simplifying the live mechanism.

**Why this path won**: Inline `SourceRef` keeps the coordinate model simple and universal. The cited state object carries its own source evidence as `source_refs[]`; `source_span_id` is derived deterministically from the paragraph-offset span rather than registered elsewhere. Reading Runner can resolve Read-provided exact quotes against the accepted unit source text, normalize them into SourceRefs, and persist those refs directly on active attention, concepts, threads, reflective frames, knowledge activations, and reaction records.

**What changed in the system**: New `attentional_v2` runtime/checkpoint truth no longer includes `anchor_bank.json` or checkpoint `anchor_bank`. Read memory ops may provide `source_quote` / `source_role`, which the Runner resolves into inline `source_refs[]` before settlement. Reaction records now persist `source_quote`, `primary_source_ref`, and `related_source_refs`. Carry-forward context, Memory Quality probe snapshots, read/settlement audit, normalized eval exports, marks, and public API schemas now use source-ref naming. The old Bridge path that wrote Anchor Bank relations is paused rather than migrated into a new relation graph. Old runtimes with anchor-bank truth are rejected and should be rerun.

**Why it matters later**: Future source-grounding work should not recreate a central source registry unless a real product need appears. If callbacks or bridge-like behavior return, they should be designed source-span-native and should use inline citations or a deliberately justified relation mechanism, not revive Anchor Bank by inertia.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `contract/openapi.public.snapshot.json`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/benchmark_probes.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/api/schemas.py`
- `reading-companion-backend/src/library/catalog.py`
- `reading-companion-backend/src/library/user_marks.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`
- `reading-companion-backend/tests/test_attentional_v2_state_ops.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `reading-companion-backend/tests/test_public_contract.py`
- `reading-companion-backend/tests/test_library_api.py`

## Entry 86
**ID**: DEC-089
**Status**: active

**Decision / Inflection**: Adopt repo-local Memory-Planning design chain and implementation handoff for `attentional_v2` optimization.

**Period**: May 16, 2026, after the Memory / Planning / Evaluation design chain converged and was added to the repo under `docs/implementation/new-reading-mechanism/second-reader-memory-planning/`.

**Decision**: The Memory / Planning / Evaluation design chain is accepted as implementation-facing guidance for optimizing the existing `attentional_v2` mechanism. The project will proceed through `E实施1-Implementation Feasibility & Delta Audit v0` before code implementation.

**Rationale**: The design phase has converged; continuing to write design pages would create diminishing returns. Implementation should start with a code-grounded delta audit and then proceed through phased small PRs.

**Non-goals**: No greenfield redesign, no replacement mechanism, no route steering UI, no user route choice, no direct PR plan, and no full eval before core instrumentation.

**What changed in the project record**: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md` now defines the directory purpose, authority order, document map, non-goals, implementation posture, and current next step. `docs/source-of-truth-map.md`, `docs/current-state.md`, and `docs/tasks/registry.*` now route future agents to the directory and to the queued feasibility-audit task.

**Why it matters later**: Future agents should treat the new directory as an initiative-local implementation workspace for optimizing current `attentional_v2`, not as stable mechanism authority. Stable behavior changes still need to land in code and be promoted to the relevant stable docs.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
- `docs/source-of-truth-map.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Entry 87
**ID**: DEC-090
**Status**: active

**Decision / Clarification**: Preserve DEC-087 as the live coordinate decision, and clarify the remaining sentence-id boundary.

**Period**: May 20, 2026, after the Eval-1 playback/reporting pass exposed `target_sentence_id` / `target sentence` handles prominently enough to risk confusion about whether the current reader had regressed to sentence-driven progress.

**Clarification**: DEC-087 remains correct. Current `attentional_v2` mainline reading progress is source-span-native: the Reading Runner advances through paragraph-offset `SourceCursor` / `SourceSpan`, and current source evidence is expressed through inline paragraph-offset `SourceRef`. Seeing `sentence_id`, `target_sentence_id`, or `cN-sM` in artifacts does not mean the mainline reader is sentence-driven.

**Boundary**: Sentence records still exist because the shared parsed book substrate produces them and several consumers still need stable orientation handles. They may appear in compatibility projections, local-buffer sentence fields, detour evidence, semantic-probe target locators, window reuse checks, and reviewer orientation text. Those sentence ids are compatibility / eval locator metadata, not the authoritative coordinate for new `attentional_v2` mainline design.

**Risk**: Long Span semantic probes and reviewer-facing playback reports can still over-present sentence ids unless they are paired with paragraph-char source coordinates. If a sentence splitter produces an awkward boundary, any downstream task that treats the sentence id as primary can inherit that error. This is especially important for Memory Quality probe placement/reporting and for human review documents that show `target sentence` labels.

**Rule going forward**: New mechanism work and reviewer-facing reports should treat paragraph-char / source-span coordinates as canonical. Sentence ids may remain as orientation or legacy/eval metadata, but reports should label them that way and show the available paragraph-char locator, source span, or `SourceRef` evidence beside them. A future implementation slice may migrate Long Span probe targets or local-buffer state further toward source-span-native coordinates, but that is separate from this fact-maintenance decision.

**Primary evidence**:
- `docs/history/decision-log.md` DEC-087
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/benchmark_probes.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`

## Entry 88
**ID**: DEC-091
**Status**: active

**Decision / Inflection**: Redefine `Active Attention` as the reader's live open-question set.

**Period**: May 21, 2026, after Eval-1 playback review showed that the previous "hot state / recent important points" framing was too broad to guide creation, lifecycle maintenance, prompt use, or human review.

**Decision**: Current `attentional_v2` Active Attention now means questions raised by already-read source that still drive the reader to keep looking for an answer. Current active items use `question_from`, `driving_question`, `working_answer`, `source_refs`, `answer_source_refs`, and `status`. `statement` remains a legacy compatibility field for old artifacts, but new Read outputs should not create statement-only active items.

**Lifecycle rule**: `Read` owns active-question lifecycle intent. `create` / `append` creates a new `open` question, `update` / `reactivate` advances its `working_answer`, `resolve` marks it `answered`, `close` marks it `closed`, and `drop` removes a mistaken or obsolete question. Durable answers should be written into `concept_registry` or `thread_trace` and then close the active question; active-attention `promote` is not the main path.

**Prompt boundary**: Read prompt projection carries all open active questions, not a top-N slice. Prompt-visible fields are only `item_id`, `question_from`, `driving_question`, and `working_answer`. Runtime fields such as source refs, linked keys, statuses, and projection markers remain in artifacts and reports rather than the Read prompt.

**Why this path won**: The live-question definition gives Active Attention a sharper product role: it is the set of unresolved things that make the reader continue reading. That is easier to create, update, answer, and close than a broad "important recent memory" bucket. It also keeps stable concepts in `concept_registry`, unfolding lines in `thread_trace`, visible output in `reaction_records`, and active questions in their own hot layer.

**Why it matters later**: Future prompt, report, and eval work should not describe Active Attention as a digest summary or a cache of recent reactions. If a future run shows static active questions across probes, the first diagnosis should be lifecycle/use failure, not a need for another metric. Historical reports with statement-shaped active items remain readable as legacy artifacts.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/runner.py`

## Entry 89
**ID**: DEC-092
**Status**: superseded by DEC-093

**Decision / Clarification**: Tighten Active Attention from broad live-question state to one carried inquiry with one answer boundary.

**Period**: May 21, 2026, after the first successful Active Attention micro eval showed live-question creation and lifecycle behavior, but also exposed over-broad active items whose partial answers could be resolved too early.

**Clarification**: Active Attention remains the reader's carry-forward question layer from DEC-091, but the unit of state is now stricter: one source-triggered inquiry plus one `answer_boundary`. The `driving_question` field remains for compatibility, but it means the reader's driving inquiry; it does not have to be a literal question-mark sentence. The required semantic contract is that the item states what the reader is trying to find out or watch resolve, and what kind of later source evidence would advance, answer, or close it.

**Lifecycle rule**: `Read` should split candidate active items that contain multiple independent answer boundaries. If a passage answers only part of a broad inquiry, the reader should update the item and keep it open, or resolve the answered item and create a narrower follow-up item. `resolve` means the current unit satisfied the item's answer boundary enough that the inquiry no longer needs to be carried as open; `close` means it no longer helps reading forward without claiming a full answer.

**Why this matters later**: This keeps Active Attention from drifting back into a summary bucket or an ever-growing theme container. It also makes prompt projection and reviewer reports more auditable: an active item can be inspected for its source trigger, live inquiry, answer boundary, current answer, and source evidence. Stable answers should settle into `concept_registry` or `thread_trace`, optionally linked from the active item during resolve/close.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`

## Entry 90
**ID**: DEC-093
**Status**: active

**Decision / Clarification**: Demote `answer_boundary` to compatibility metadata and use answered/closed reasons for Active Attention lifecycle.

**Period**: May 21, 2026, after reviewing the Retry2 micro-eval output and deciding that predeclaring an answer boundary added unnecessary design weight. The simpler product-aligned rule is that the reader carries open inquiries, then explains why an inquiry is answered or no longer useful when it terminates.

**Clarification**: Active Attention remains the reader's carry-forward open-inquiry layer. New prompts should not require `answer_boundary` as the core contract. `answer_boundary` may remain on old artifacts and compatibility paths, but the current lifecycle contract is:
- `create` opens one prompt-context-grounded inquiry with `question_from`, `driving_question`, `working_answer`, and available source / framing / memory evidence.
- `update` records partial progress in `working_answer` and answer source evidence while keeping the item open.
- `resolve` is a soft terminal state that requires `answered_reason`, answer source evidence, and answered source/unit coordinates.
- `close` is a soft terminal state that requires `closed_reason` and closed source/unit coordinates when the inquiry no longer drives reading but is not claimed as answered.
- `drop` is reserved for mistaken, invalid, or obsolete items that should be removed from current state.

**Lineage rule**: Downstream durable memory should own lineage to Active Attention. `concept_registry` and `thread_trace` may record `derived_from_active_attention_ids`; new prompts should not require Active Attention items to link backward to downstream concept/thread keys.

**Why this path won**: The user-facing ontology is simpler: Active Attention is what the reader is still carrying, not a precomputed answer-contract object. The semantic burden belongs at termination time, where `Read` must justify why the inquiry can stop being carried. This reduces overfitting to any single example while making premature resolution auditable.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`

## Entry 91
**ID**: DEC-094
**Status**: superseded by DEC-095

**Decision / Clarification**: Treat Active Attention as coherent reading forward-pull, not a formal Q&A tracker.

**Period**: May 21-22, 2026, after Retry3 showed that answered-reason lifecycle worked but also made the design risk visible: if every active item is treated as a narrowly answerable question, the mechanism can drift away from reader interest and toward maintenance-friendly exam items.

**Clarification**: Active Attention remains the reader's carry-forward open-inquiry layer, but the unit is a coherent source-triggered forward pull: a question, tension, suspense, or watchpoint that makes the reader keep reading. `driving_question` remains the field name for compatibility, but the value does not need to be a literal question. One item may carry closely related sides of the same pull; it should not bundle independent tensions that need different later evidence to satisfy.

**Grounding rule**: The LLM cites source text snippets through `source_quote` and `answer_source_quote`; the runtime resolves paragraph-char coordinates. The runtime may use raw exact match, normalized exact match, and ordered-fragment matching for stitched-but-source-real snippets. If resolution still fails, the artifact should expose `fallback_unit_span` as a grounding caveat, not as precise evidence.

**Why this path won**: This keeps Active Attention close to product intent: it is the living curiosity and attention that drives reading forward. Lifecycle operations remain auditable through `answered_reason` / `closed_reason`, but the ontology is not reduced to predeclared answer boundaries or formal Q&A.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`

## Entry 92
**ID**: DEC-095
**Status**: superseded by DEC-097

**Decision / Clarification**: Treat Active Attention as prompt-context-grounded forward-pull.

**Period**: May 22, 2026, after reviewing Retry4 and clarifying that Active Attention should not be limited to the current source unit alone. A reader may legitimately carry a forward-pull created by the current source together with visible title / chapter framing or prior memory, but should not import outside book knowledge that was not present in the prompt.

**Clarification**: Active Attention remains the reader's carry-forward open-inquiry layer, and it remains a coherent reading forward-pull rather than a formal Q&A tracker. The grounding boundary is now prompt-visible context: current source unit, prompt-visible book or chapter framing, and existing memory state shown in the read context packet. `question_from` should honestly name that basis. If the item is grounded in title/framing/prior memory rather than a current-source phrase, `Read` should omit `source_quote` instead of pretending there is a precise quote.

**Grounding rule**: The LLM provides exact contiguous `source_quote` / `answer_source_quote` snippets only when it is citing the current source unit. The runtime owns paragraph-char coordinate resolution and does not trust model-emitted source coordinates. Missing quotes keep unit lifecycle coordinates for audit but do not create fake precise `source_refs`.

**Lifecycle rule**: `resolve` requires a grounded `answered_reason` explaining why cited evidence directly satisfies the carried forward-pull. Evidence that is only a precondition, setup, clue, partial explanation, or reframing should update `working_answer` and keep the item open.

**Why this path won**: This is the simplest general rule that preserves reader-like behavior without overfitting to one book. It lets titles, framing, and prior memory matter when they are truly in context, while still preventing the model from smuggling in outside knowledge or closing an inquiry on merely preparatory evidence.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`

## Entry 93
**ID**: DEC-096
**Status**: superseded by DEC-097

**Decision / Clarification**: Rename the Active Attention contract to ActiveTension semantics while keeping the runtime store key `active_attention`.

**Period**: May 23, 2026, after reviewing the full-window Active Attention lifecycle diagnostic and concluding that the prior inquiry/question framing was still too narrow. The user clarified that a reader may carry not only answer-seeking questions, but also beauty, vivid images, unusual events, distinctive characters, emotional residue, or unsettled patterns.

**Clarification**: Current `active_attention` state should be interpreted as ActiveTension: points that still hang in the reader's attention after a unit. An ActiveTension does not need to be phrased as a question, does not need to wait for an answer, and does not require `Read` to predict whether it will matter later. The creation test is whether the prompt-visible source/framing/memory leaves readerly charge that has not been fully digested into an ordinary fact, stable concept, chapter summary, or visible reaction.

**Field rule**: New prompts, projections, persisted state, and reviewer-facing reports should use `tension_from`, `tension_focus`, `working_interpretation`, and `development_source_refs`. Old question-only fields (`question_from`, `driving_question`, `working_answer`, `answer_source_refs`) are migration inputs at load / normalization boundaries only and should not be written back as current state. `statement` and `answer_boundary` are old artifact inputs, not current ActiveTension structure.

**Why this path won**: This preserves the product goal of a thoughtful co-reader. It avoids overfitting the memory state into a formal Q&A tracker, while still giving the runtime and reports a concrete, auditable structure for what is lingering in attention.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_migration.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`

## Entry 94
**ID**: DEC-097
**Status**: active

**Decision / Clarification**: Deprecate Active Attention / ActiveTension as a primary memory layer.

**Period**: May 23, 2026, after discussing the larger near-term memory architecture and concluding that ActiveTension overlaps with two cleaner responsibilities: per-unit recent reading memory and durable thread memory.

**Decision**: `active_attention` remains in the runtime and artifacts for now, but it is deprecated as the target short-term memory design and is pending removal after its replacement lands. Do not keep expanding Active Attention / ActiveTension with new fields, metrics, or report contracts. First design and implement a `recent_reading_memory` layer that records the compact semantic memory of each read unit. Let `thread_trace` inherit long-lived tensions, narrative arcs, watchpoints, and unresolved pulls that need to persist beyond near-term continuity.

**Rationale**: The product goal is a reader that remembers what it has just read without rereading the whole book every turn. ActiveTension captured some lingering attention, but it does not cover ordinary key information from each unit and can over-direct attention if treated as the main short-term context. A simpler hierarchy is: recent reading memory for near-term continuity, concept / thread memory for structured long-distance understanding, and chapter / reflective summaries for macro structure.

**Removal boundary**: Do not delete `active_attention` in this docs-only clarification. Old artifacts and current code paths may still contain it until `recent_reading_memory` is designed, implemented, validated, and a removal patch is explicitly approved. New post-cleanup product runs should write the new state only; do not keep an old-state compatibility tail unless a future task explicitly approves old-run migration / resume support. Existing ActiveTension reports remain useful diagnostic evidence, but future design work should not treat them as the canonical memory target.

**Primary evidence**:
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 95
**ID**: DEC-098
**Status**: active

**Decision / Clarification**: Implement first-half Recent Reading Memory formation for `attentional_v2`.

**Period**: May 23, 2026, after accepting the Recent Reading Memory design as the replacement direction for near-term per-unit memory, while explicitly deferring consolidation into long-distance memory.

**Decision**: `recent_reading_memory` is now a first-class runtime store for near-term semantic memory of just-read units. `Read` may append one or a small number of entries per unit through `memory_uptake_ops[]` with `target_store="recent_reading_memory"` and `op="append"`. The LLM supplies only `kind` and `memory_text`; the runner fills `entry_id`, `source_unit_span_id`, `created_at_unit_index`, `status`, and `archived_by_consolidation_id`.

**Formation rule**: Recent Reading Memory should be compressed meaning, not copied wording. It must be context-resolvable for future Read steps, but not standalone exhaustive. It should name newly introduced people, situations, claims, events, or concepts clearly enough for a future reader to understand, while relying on prompt-visible concept/thread context when that context already makes a referent stable.

**State rule**: Before consolidation, Recent Reading Memory is append-only. Read does not update, merge, resolve, close, drop, or link existing recent entries, and it does not guess future concept/thread destinations. Only `status="active"` entries are projected into Read prompt context. Future consolidation may archive processed entries; that consolidation prompt and lineage policy remain a later design.

**Why this path won**: This gives the mechanism the missing near-term memory layer without expanding deprecated ActiveTension into a catch-all. It keeps the memory hierarchy simple: Recent Reading Memory for short-range continuity, `concept_registry` / `thread_trace` for structured long-distance memory, and reflective/chapter frames for macro understanding.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/runner.py`

## Entry 96
**ID**: DEC-099
**Status**: active

**Decision / Clarification**: Tighten Recent Reading Memory formation toward source-grounded understanding instead of essay-like analysis.

**Period**: May 24, 2026, after reviewing the first `huochu p45-p61` Recent Reading Memory micro diagnostic.

**Decision**: Keep the Recent Reading Memory state shape and append-only first-half behavior unchanged, but update the Read prompt to `attentional_v2.read.v25`. The prompt now states that Recent Reading Memory should record what the source establishes, shows, says, names, contrasts, or changes. It should remain complete enough for future reading. A later clarification in DEC-100 generalizes the continuity wording to the full prompt-visible reading context rather than a hard-coded store list.

**Boundary**: Recent Reading Memory is not a place for essay-like explanation, unsupported hidden-mechanism claims, or abstract theory upgrades. It may compress meaning, but it should not turn a concrete source scene into claims such as "the essence is", "this proves", "this is an operation mechanism", or "the passage actively trains" unless the source itself clearly supports that wording.

**Why this path won**: The micro diagnostic showed that formation and continuity worked, but some entries sounded too analytical for a near-term memory layer. The product need is simpler: remember what was just read in a form that later Read steps can understand, without rereading the source and without converting every unit into a mini-interpretive essay.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`

## Entry 98
**ID**: DEC-101
**Status**: superseded

**Decision / Clarification**: Keep Recent Reading Memory source-established and stop after the current unit's contribution is clear.

**Period**: May 24, 2026, after reviewing the `read.v28` beginning-of-book `huochu p1-p24` retry2 diagnostic.

**Decision**: Update the Read prompt to `attentional_v2.read.v29`. Recent Reading Memory should remain a compact near-term memory for continuing the book: it uses prompt-visible context as carried memory, but primarily records the current unit's contribution. It should compress source meaning into clear memory, not produce an essay or theory about the passage.

**Boundary**: Once source-established content is clear, stop. Do not add a closing label such as "this is a mechanism", "this reveals the essence", "this forms a tension", "this is a system", or "this proves..." unless the source itself explicitly names or frames that abstraction. This is not a move toward mechanical extraction: the memory can still be readable and interpretively coherent, but it should not force every unit into a named concept or abstract explanation.

**Why this path won**: Retry2 improved coverage and remembered the previously missed author-method / evidence-boundary material, but several entries still ended by naming or elevating the source content into an abstract label. The chosen repair follows simplicity and universality: remember what the current unit establishes for future reading, use context to understand it, and stop when the source-established contribution is clear.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`

## Entry 99
**ID**: DEC-102
**Status**: active

**Decision / Clarification**: Revert the Recent Reading Memory prompt direction to the `read.v28` shape, with a narrow no-default-heading-colon style constraint.

**Period**: May 24, 2026, after reviewing the `read.v29` beginning-of-book `huochu p1-p24` retry3 diagnostic and comparing it against the stronger `read.v28` retry2 behavior.

**Decision**: Update the Read prompt to `attentional_v2.read.v30`. The new prompt keeps the `read.v28` formation shape: Recent Reading Memory is source-established, context-resolvable, complete enough for future reading, and oriented through prompt-visible reading context while still recording the current unit itself. The rejected `read.v29` holistic rewrite is not the next prompt direction.

**Boundary**: The only new style constraint on top of `read.v28` is that Recent Memory should be written as natural memory sentences or a short paragraph, not as a default `<label>: <explanation>` or `<abstract name>: <explanation>` pattern. A colon is appropriate when the source itself names a term, stage, framework, or quoted source term; otherwise the model should not force a small title onto the memory. The retry3 report remains historical diagnostic evidence, but its prompt direction is superseded.

**Why this path won**: The retry3 run reduced some forced abstract endings, but the broader rewrite made entries feel more formulaic and did not improve overall quality. The simpler and more universal repair is to return to the more readable `read.v28` body and add only the specific anti-pattern rule that the reviewer identified.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/docs/evaluation/reporting_standard.md`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Beginning-Micro-Diagnostic-Huochu-Retry3-Post-run-Report v0.md`

## Entry 97
**ID**: DEC-100
**Status**: active

**Decision / Clarification**: Clarify Recent Reading Memory continuity as prompt-context orientation with current-unit primacy.

**Period**: May 24, 2026, after discussing whether Recent Reading Memory should read like isolated notes or like a continuous unfolding reading.

**Decision**: Update the Read prompt to `attentional_v2.read.v26`. Before writing Recent Reading Memory, `Read` should orient through the full prompt-visible reading context and treat that context as what the reader already carries from the reading so far. This is intentionally universal: the rule applies to whatever context the program assembled, not to a hard-coded list of stores such as Recent Memory, Concept, Thread, chapter map, or book framing.

**Boundary**: Continuity is an orientation layer, not the output target. The entry should still primarily record what the current unit newly establishes, develops, specifies, contrasts, changes, or makes memorable. It should not become a recap of prior context, and it should not force every entry to mention earlier memory or framing. A good entry answers: "What should my future self remember from this unit, given the reading context I already carried into it?" rather than "What can I say again about the prior context?"

**Why this path won**: This keeps Recent Reading Memory simple and universal. The program owns context assembly; the reader model should use whatever prompt-visible state it receives to understand the current unit as part of the book, without turning the memory layer into explicit recent-to-recent links, a relationship graph, or a per-entry context-expansion task.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`

## Entry 100
**ID**: DEC-103
**Status**: active

**Decision / Inflection**: Pause the Second Reader Memory / Planning implementation track and restart from a narrower product-goal frame.

**Period**: May 30, 2026, after the Recent Reading Memory / Concept / Thread design discussion exposed that the mechanism work was drifting into an internal memory-ontology project rather than staying anchored to the user-facing note/highlight product value.

**Decision**: Stop using the `second-reader-memory-planning` design chain as the primary source for the next implementation path. The next mechanism design should start from a narrowed product target: understand the currently read text and present valuable reader-facing notes / highlights. The next workflow exploration should use the `ingest -> digest` framing rather than continuing the old `navigate -> read` path-steering frame. Prior context should be retrieved as needed instead of driving the mechanism through live回读 path selection.

**Boundary**: This does not delete previous code or invalidate all prior work. Eval health gates, run ledger discipline, source-coordinate governance, artifact-grounded reporting, and prompt assembly primitives remain potentially reusable. However, the previous ActiveTension, Recent Memory consolidation, Thread / Progression / Development memory, and Read XML context migration directions are paused as implementation authority until a new feasibility / delta audit explicitly re-adopts them.

**Why this path won**: The product value is not that the agent owns a complete internal memory ontology. The value is that sequential reading can surface useful notes the user might not have thought of: viewpoint supplements, important-content catches, line-recall moments, argument-jump warnings, tone shifts, definitions, frameworks, and companionship. Continuing to refine internal durable-memory structures before re-grounding that product loop risks building a more elaborate mechanism than the narrowed product needs.

**Next-start rule**: The next coding session should begin with a read-only feasibility / delta audit for the new direction. It should not implement code, launch eval, update the evidence catalog, or claim product quality before establishing how `ingest`, `digest`, retrieval, tool-owned non-text actions, and note/highlight output categories map onto the current codebase.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计11-Read Context Layer Contract v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计12-Prompt Assembly Layer Design v0.md`

## Entry 101
**ID**: DEC-104
**Status**: active

**Decision / Inflection**: Retire live Detour / source-backread from `attentional_v2` and make `Navigate.choose_next_unit` forward-only.

**Period**: May 31, 2026, during the first implementation slice after the `ingest -> digest` reframe began.

**Decision**: Remove Detour, source-backread, chapter-tail detour drain, and Navigate source-skill behavior from the live runtime path. The current live loop is now forward-only: `Navigate.choose_next_unit -> Read -> Reading Runner settlement`. `Navigate.choose_next_unit` selects the next forward source unit and no longer supports live `request_skill`, `defer_detour`, `detour`, or `deferred` behavior. `Read` is no longer prompted to emit `detour_need`; if a stale model-shaped response includes it, the Runner ignores it and does not mutate `local_continuity`.

**Boundary**: Historical Detour helper code, literal values, and old artifact readers may remain only as explicitly deprecated compatibility/reference surfaces. New live runs must not create or advance `active_detour_id`, `active_detour_need`, or `detour_trace`, must not emit new `detour_trace_evidence`, and must not use old source-skill runtime as the default basis for future Ingest retrieval design.

**Why this path won**: The new product direction replaces live回读 path steering with retrieval-first prior-context support. Keeping Detour alive inside Navigate would preserve the old path-selection center of gravity and make the first `Ingest` slice inherit the wrong control shape. A forward-only baseline makes the next design question crisp: which memories should Ingest retrieve for the selected unit, and how should Digest turn that context into useful reader-facing notes / highlights?

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/prompts/navigate.py`
- `reading-companion-backend/src/attentional_v2/prompts/read_unit.py`

## Entry 102
**ID**: DEC-105
**Status**: active

**Decision / Inflection**: Hard-purge retired Detour / source-backread compatibility interfaces from current `attentional_v2`.

**Period**: May 31, 2026, immediately after the first DEC-104 cleanup revealed that deprecated compatibility literals, audit fields, tests, and helper modules still made the retired path visible as if it were a current interface.

**Decision**: Current `attentional_v2` no longer exposes Detour / source-backread / source-skill / `look_back` / `active_recall` interfaces in live code, prompts, schemas, audits, or tests. `Navigate.choose_next_unit` now exposes only the forward source-boundary fields needed to choose the next unit; the intermediate `NavigateActDecision = choose_unit` and `NavigateSelectionMode = mainline` shells were removed in the follow-through cleanup. `LocalContinuityState` no longer has Detour continuity fields; `ReadUnitResult` no longer has `detour_need`; `Read` prompt packets and manifests no longer include path-redirection contracts; and the source-skill runtime / read-context compatibility helpers are removed.

**Compatibility boundary**: Old Detour-era checkpoints and private runtime artifacts are not a current compatibility target. Historical docs, old reports, old run outputs, and previous decision entries may still mention the retired mechanism for traceability, but stable current docs should describe it only as removed from the live surface. Future `Ingest` memory retrieval must be designed as a new retrieval surface rather than inherited from the retired helper loop by default.

**Why this path won**: Keeping deprecated literals and ignored fields in the current interface preserved the old path-selection center of gravity and made the new `Ingest -> Digest` design easier to confuse with the retired backread path. A hard purge gives the next design slice a clean baseline: `Navigate.choose_next_unit -> Read -> Reading Runner settlement`, with prior context to be supplied later through an explicit retrieval design.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/prompts/navigate.py`
- `reading-companion-backend/src/attentional_v2/prompts/read_unit.py`
- `reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 103
**ID**: DEC-106
**Status**: active

**Decision / Clarification**: Treat `Navigate` as the LLM boundary call, not the full runtime next-unit preparation operation.

**Period**: May 31, 2026, while preparing the codebase for the next `Ingest -> Digest` mechanism design pass after the Detour hard purge.

**Decision**: In current `attentional_v2`, `Navigate` names the LLM call that receives prepared reading position, preview, cursor, and navigation context, then returns only boundary fields for the next forward unit. In code, that call lives at `llm_calls.navigate(...)`. Runtime work before and after that call belongs to Reading Runner: `prepare_next_source_unit_for_read` prepares the source/context packet, invokes Navigate, resolves or retries the returned anchor, applies deterministic fallback boundary governance when needed, and hands the accepted source unit to `Read`.

**Boundary**: This is a structure and naming cleanup, not a new retrieval mechanism. It does not implement Ingest memory retrieval, change the Read/Digest contract, run eval, or update evidence catalog authority. The same LLM-call/runtime separation should guide later `Ingest` and `Digest` naming: LLM-call names describe model calls; runtime orchestration, tool retrieval, settlement, and boundary governance stay outside those call names.

**Why this path won**: Keeping one `navigate_choose_next_unit` runtime wrapper around preparation, model invocation, retry, boundary resolution, fallback, source-unit assembly, and settlement handoff made it hard to tell which behavior belonged to the LLM call and which behavior belonged to deterministic runtime control. Splitting the boundary gives the next Ingest/Digest work a cleaner API surface and prevents the old path-selection framing from leaking back through function names.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 104
**ID**: DEC-107
**Status**: active

**Decision / Inflection**: Replace the current `Navigate` LLM identity with `Ingest`.

**Period**: May 31, 2026, after `DEC-106` separated the LLM-call boundary from Reading Runner preparation/governance and the next product direction settled on an `Ingest -> Digest` framing.

**Decision**: The current boundary-selection LLM call is now `Ingest`, implemented at `llm_calls.ingest(...)`. It uses an XML prompt assembled through the prompt assembly framework with top-level `ReaderRole`, `Instruction`, `BookInfo`, `CurrentView`, an empty self-closing `RetrievalSurface`, and `OutputContract`. The first implemented slice keeps only forward next-unit boundary selection and returns flat JSON with `end_anchor_text`, `boundary_type`, and `reason`.

**Boundary**: This does not implement memory retrieval yet. `RetrievalSurface` is intentionally empty until the new memory design defines available stores, indexes, request shape, budget, and runtime tool behavior. Reading Runner still owns prompt preparation, anchor resolution, retry/fallback, accepted source-unit assembly, cursor advancement, audit, and settlement.

**Why this path won**: The project is no longer designing a path-navigation agent. The useful surviving behavior is the ability to choose the next forward semantic source unit; the next product step is to support that future read with relevant memory. Naming the LLM call `Ingest` makes the next-node boundary explicit: it prepares the reading object and later memory support for `Digest`, while deterministic runtime work stays outside the LLM-node identity.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/ingest-context-and-navigate-mapping.md`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/prompts/ingest.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 105
**ID**: DEC-108
**Status**: active

**Decision / Inflection**: Rename the concrete per-unit interpretation LLM call from `Read` / `read_unit` to `Digest`, and make the XML Digest prompt the only live path.

**Period**: May 31, 2026, after `DEC-107` renamed the forward boundary-selection LLM call to `Ingest` and the mechanism vocabulary settled on `Ingest -> Digest -> Reading Runner settlement`.

**Decision**: In current `attentional_v2`, `Read` / `read` is reserved for the overall Agent Reader read action and read cycle. The concrete LLM call that carefully reads one accepted source unit is `Digest`, implemented at `llm_calls.digest(...)`. Its prompt manifest, trace node, prompt definition, prompt module, and result type use `digest` naming. Digest always uses the XML prompt assembly path with `ReaderRole`, `Instruction`, `BookInfo`, `ReadingState`, `CurrentFocus`, and `OutputContract`; the old legacy prompt assembly toggle and `read_unit` prompt manifest are no longer live interfaces.

**Boundary**: This does not implement the new Ingest memory retrieval loop and does not change public API/frontend semantics. The mechanism-private `read_audit.jsonl` artifact remains named as a read-cycle audit because it records the whole cycle: Ingest trace, Digest output, and settlement inputs. Digest's LLM-facing output contract is `reading_impression`, `surfaced_reactions`, and `recent_reading_memory`; runtime still converts Recent Reading Memory entries into internal `memory_uptake_ops[]` for deterministic settlement.

**Why this path won**: Keeping `Read` as both the whole Agent Reader action and the concrete LLM node made the implementation repeat the same boundary confusion that `DEC-106` fixed for Navigate. Naming the concrete node `Digest` clarifies the loop: Ingest selects and prepares the next reading object, Digest carefully reads that object, and Reading Runner settles state and cursor movement around the completed read cycle.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 106
**ID**: DEC-109
**Status**: active

**Decision / Inflection**: Hard-purge the content-typed structured long-memory stores from current `attentional_v2`, and shift the next memory direction toward content-neutral Unit Memory.

**Period**: June 1, 2026, after the Ingest/Digest rename clarified that the next memory surface should be selected around the accepted source unit rather than around a fixed taxonomy of memory categories.

**Decision**: Current `attentional_v2` no longer exposes `concept_registry` or `thread_trace` as live schema, runtime artifacts, checkpoint keys, prompt projections, settlement targets, audit deltas, probe snapshot fields, helper APIs, or tests. `ConceptRegistry*`, `ThreadTrace*`, `concept_digest`, `thread_digest`, the migration/helper paths that wrote those stores, and the bridge / slow-cycle relation-writing surfaces tied to them are removed from active code. `Digest` still emits `recent_reading_memory[]`, and runtime still converts those entries into append-only `target_store="recent_reading_memory"` operations. `active_attention` remains a separate deprecated store pending a later cleanup slice.

**Boundary**: This slice does not implement the new Unit Memory Ledger, retrieval indexes, Ingest memory retrieval request shape, or Digest retrieval context. It intentionally breaks recovery compatibility for old concept/thread-era private checkpoints and runtime artifacts. Historical reports, old run outputs, archived planning notes, and older decision entries may still mention the retired stores, but stable current docs should not treat them as live authority.

**Why this path won**: The fixed concept/thread taxonomy kept making the memory mechanism content-shaped rather than reading-shaped. The more universal baseline is unit-level memory: preserve what each accepted source unit made worth remembering, then let future Ingest retrieval find relevant prior units for the next accepted unit. That keeps the framework independent of content type while still supporting continuity, source grounding, and later long-distance recall.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/benchmark_probes.py`
- `reading-companion-backend/src/attentional_v2/state_migration.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 107
**ID**: DEC-110
**Status**: active

**Decision / Inflection**: Make Unit Memory ledger + hybrid retrieval the current long-distance memory substrate for `attentional_v2`.

**Period**: June 1, 2026, after `DEC-109` removed the content-typed concept/thread stores and the Unit Memory design settled on unit-centered storage plus field-specific retrieval documents.

**Decision**: Current `attentional_v2` now writes one mechanism-private Unit Memory Entry per accepted source unit after Digest settlement. Each entry preserves the accepted source unit plus Digest's `understanding`, `response`, and `annotations`, then derives retrieval documents from source, understanding, response, and annotation surfaces. The retrieval index lives in `_mechanisms/attentional_v2/runtime/unit_memory.sqlite`, uses SQLite FTS5 trigram/BM25 as the required lexical channel, optionally uses sqlite-vec plus local Ollama Qwen3 embedding in `hybrid` mode, and degrades cleanly to text-only retrieval when vector support is unavailable. `Ingest` may emit one `memory_query` in the same LLM call that chooses the next boundary; Reading Runner resolves the accepted unit, executes retrieval before Digest, and writes `_mechanisms/attentional_v2/runtime/unit_memory_retrieval_trace.jsonl`.

**Boundary**: This slice does not inject retrieved Unit Memory cards into Digest XML context and does not change frontend presentation. Digest still receives existing Recent Reading Memory only. `memory_retrieval_mode = hybrid | text_only` is backend entry configuration, defaults to `hybrid`, is persisted in `memory_retrieval_config.json`, and is restored on resume unless the operator explicitly overrides it. No AI evaluation, evidence-catalog update, or background job is part of this decision.

**Why this path won**: The project needs long-distance continuity without returning to Detour/backread path steering or content-typed memory taxonomies. A Unit Memory ledger keeps the durable fact source simple and content-neutral, while field-specific retrieval documents let source text, Understanding, Response, and Annotation each contribute to recall. FTS5-first retrieval keeps the system locally inspectable and usable on every development machine; the hybrid vector channel can improve semantic recall when sqlite-vec and Ollama are available without making them required for reading to continue.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
- `docs/api-contract.md`
- `docs/api-integration.md`
- `docs/backend-sequential-lifecycle.md`
- `reading-companion-backend/src/attentional_v2/unit_memory.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/prompts/ingest.py`
- `reading-companion-backend/src/attentional_v2/storage.py`
- `reading-companion-backend/src/attentional_v2/resume.py`
- `reading-companion-backend/src/library/jobs.py`
- `reading-companion-backend/src/api/app.py`
- `reading-companion-backend/tests/test_attentional_v2_unit_memory.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_library_api.py`

## Entry 108
**ID**: DEC-111
**Status**: active

**Decision / Inflection**: Reframe the current Long Span evaluation surface away from backread/callback success metrics and toward Unit Memory conformance plus prior-memory safety.

**Period**: June 3, 2026, after the `Ingest -> Unit Memory retrieval/selection -> Digest ReadingMemory -> settlement` mechanism was implemented and the first five-window judged diagnostic completed.

**Decision**: Current active Long Span evaluation no longer treats Detour, backread, source-backread, callback action count, or visible prior-reference frequency as success metrics. Memory Quality must be judged against current Unit Memory and Digest `ReadingMemory` evidence, not only older hot-state or digest-only snapshots. The former callback/FVI reaction audit remains only as a secondary safety audit under prior-memory continuity terminology: grounded prior-memory use, weak prior-memory reference, and prior-memory overclaim. Prior-memory overclaim remains an important guardrail, but the number of prior-memory references is not a product-quality score.

**Boundary**: This does not rewrite historical reports, historical benchmark manifests, or old callback-bridge case datasets. Old labels may remain in archived outputs and historical tasks when clearly marked as historical. Current stable docs, active Long Span runner output, and active eval inventory should use the post-`DEC-110` evaluation surface.

**Why this path won**: The current mechanism no longer performs live回看 or Detour path steering, so evaluating callback or backread behavior as a positive capability would reward an obsolete design. The live product question is now whether Ingest expresses useful recall intent, runtime retrieves and selects relevant Unit Memory, Digest receives concise ReadingMemory, and the final visible reading remains grounded rather than polluted by prior memory.

**Primary evidence**:
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- `reading-companion-backend/src/attentional_v2/benchmark_probes.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- `reading-companion-backend/tests/test_long_span_vnext.py`

## Entry 109
**ID**: DEC-112
**Status**: active

**Decision / Inflection**: Carry subject continuity through Digest Understanding and ReadingMemory, not through raw-source backfill or Ingest-side reference-resolution fields.

**Period**: June 6, 2026, after the first Digest Understanding review exposed floating-pronoun and subject-continuity risks in stored Understanding memory.

**Decision**: The next subject-continuity follow-up should strengthen Digest Understanding rather than adding a separate reference-resolution surface. Digest should use the current source unit plus prior Understanding rendered in `ReadingMemory` to establish new subjects, continue known narrators / speakers / actors / concepts / relationships, or explicitly preserve meaningful ambiguity when the referent remains unclear. Stored `understanding.content` should be self-contained and memory-readable: it may use pronouns when their referent is explicit inside the same Understanding, but it should not store floating pronouns that later Digest calls cannot interpret.

**Boundary**: This decision rejects the pending alternative of adding raw prior-source continuity context to Ingest or Digest, adding Ingest-side referent-hint fields, or creating a durable referent/coreference store for this slice. Ingest remains responsible for forward unit selection and bounded prior-reading recalls. Runtime remains responsible for Unit Memory retrieval, ReadingMemory rendering, settlement, and audit. A later audit-only checker for floating pronouns may be added if diagnostics show prompt/example work is insufficient, but it should not become a new memory schema by default.

**Why this path won**: Subject continuity is part of reading continuity, and the project already has a channel for reading continuity: Understanding stored into Recent Reading Memory / Unit Memory and rendered back as `ReadingMemory`. Adding raw-source backfill would reintroduce a form of hidden backread, while adding Ingest referent hints would pull Ingest toward interpretation rather than boundary / recall preparation. The simpler universal rule is to make each Understanding carry the subject information that future reading needs, including ambiguity when the text itself withholds identity.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
- `docs/implementation/new-reading-mechanism/digest-understanding-response-marginalia-design.md`

## Entry 110
**ID**: DEC-113
**Status**: active

**Decision / Inflection**: Use forced final-output tool calls for current `attentional_v2` structured LLM outputs.

**Period**: June 6, 2026, after Digest Understanding diagnostics showed that free-text JSON output could still silently violate required output contracts and produce empty or malformed fields.

**Decision**: Current `attentional_v2` structured LLM calls now submit their final result through mechanism-private final-output tools instead of relying on `Return JSON only` text parsing. Ingest uses `submit_ingest_result`; Digest uses `submit_digest_result`; bridge resolution, reflective promotion, reconsolidation, chapter consolidation, and survey chapter-zone classification use their own `submit_*_result` tools. These tools are output channels only. `retrieve_unit_memory` remains the only live action tool and is kept separate from final-output submit tools.

**Boundary**: This migration covers the current `attentional_v2` mechanism. Retired `book_analysis`, legacy `iterator_reader`, and other non-current fallback paths may continue using legacy JSON parsing unless a later task explicitly migrates them. Runtime validators remain mandatory because tool schemas enforce shape but not reading-specific business semantics. If a required submit tool is missing, has the wrong name, has non-object args, or fails the node validator, the gateway attempts one repair; persistent failure is surfaced as public problem code `llm_contract`.

**Why this path won**: Tool-use output submission makes the model's structured-output channel explicit and easier to validate with MiniMax's Anthropic-compatible tool-use path, while still preserving the runtime's responsibility for semantic validation, repair, fallback, traceability, and public problem reporting. It also keeps true action tools, such as Unit Memory retrieval, separate from result-submission tools so Ingest/Digest control flow remains inspectable.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/api-contract.md`
- `docs/api-integration.md`
- `reading-companion-backend/src/reading_runtime/llm_gateway.py`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/bridge.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/survey.py`
- `reading-companion-backend/tests/test_llm_gateway.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`

## Entry 111
**ID**: DEC-114
**Status**: active

**Decision / Inflection**: Remove `understanding.kind` from current Digest / Recent Reading Memory / Unit Memory live surfaces.

**Period**: June 6, 2026, after the Digest Understanding review identified the inherited `kind` classifier as a leftover from the paused structured-memory direction rather than a necessary part of content-neutral Unit Memory.

**Decision**: Current Digest now submits `understanding` as one string, not a `{kind, content}` object. Runtime converts that string into `recent_reading_memory` append operations that carry only `memory_text`. New Unit Memory entries store `digest.understanding.content` plus token estimate, without a content-type classifier. Retrieval continues to use Understanding text as the primary semantic surface; it does not use a fixed content taxonomy or `kind` facet.

**Boundary**: This is a hard live-interface cleanup. Old artifacts and checkpoints that already contain `kind` remain historical data and are not migrated, but current model output, prompts, tool schema, runtime stores, prompt projection, tests, and stable docs should not expose `understanding.kind` as a live contract. Public frontend/API behavior is not changed.

**Why this path won**: The current memory direction favors simplicity, universality, and content-neutral unit-level memory. A lightweight classifier still asks the model to label content types and can quietly reintroduce taxonomy maintenance without serving retrieval or Digest continuity. The useful memory object is the source-grounded Understanding text itself.

**Primary evidence**:
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/digest-understanding-response-marginalia-design.md`
- `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
- `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/unit_memory.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`

## Entry 112
**ID**: DEC-115
**Status**: active

**Decision / Inflection**: Keep LLM prompts/tools protocol-neutral while allowing profile-selected structured-output transports.

**Period**: June 8, 2026, after deciding to add OpenAI-compatible OpenCode/DeepSeek runtime support without duplicating mechanism prompts or redefining action tools.

**Decision**: Project-owned tools and final-output schemas stay in one canonical shape: `name`, `description`, and `input_schema`. The shared LLM gateway now translates that shape into Anthropic-style tools or OpenAI-compatible function tools at the adapter boundary. Target/profile `provider_options` carry provider-specific invocation features such as `response_format`, `thinking`, and `reasoning_effort`. Current `attentional_v2` Ingest and Digest final structured outputs use the selected profile transport: Anthropic-compatible profiles keep forced final-output tools, while OpenAI-compatible profiles configured with `response_format: {"type": "json_object"}` use JSON-object output plus local validation/repair.

**Boundary**: This does not turn final structured outputs into business action tools. `retrieve_unit_memory` remains the live action tool and stays `tool_choice="auto"` so the model may choose whether retrieval is needed. Runtime validators remain mandatory for reading-specific correctness regardless of transport. Raw provider reasoning/thinking content is not stored in standard runtime artifacts; only normal content, usage, and compact metadata belong in standard traces unless a future debug-only path explicitly opts in.

**Why this path won**: The project needs to switch between Anthropic-compatible MiniMax and OpenAI-compatible DeepSeek/OpenCode profiles without letting provider protocol details leak into mechanism design. Treating forced final-output tools and JSON-object mode as transport choices preserves the clearer separation introduced by `DEC-113` while using the more natural OpenAI-compatible structured-output path for models that support JSON object mode but not strict JSON schema.

**Primary evidence**:
- `README.md`
- `docs/current-state.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `reading-companion-backend/config/llm_targets.local.example.json`
- `reading-companion-backend/pyproject.toml`
- `reading-companion-backend/src/reading_runtime/llm_registry.py`
- `reading-companion-backend/src/reading_runtime/llm_gateway.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/tests/test_llm_gateway.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`

## Entry 113
**ID**: DEC-116
**Status**: active

**Decision / Inflection**: Treat Ingest next-unit selection as bounded-lookahead semantic planning, while keeping Digest as the focused interpreter of the accepted unit.

**Period**: June 13, 2026, after reviewing the rolling A/B report for the `window_partition_draft` Ingest selector and promoting that selector into the live prompt baseline.

**Decision**: The current `attentional_v2` Ingest design should be understood as a bounded-lookahead planner. It receives a forward preview window, conceptually partitions that window into consecutive coherent reading units, and commits only the first unit through `unit.end_paragraph_n` / `unit.end_at`. Later preview text may be used as boundary evidence because the first unit's end is often clarified by where the second unit begins, but later preview text is not treated as read or digested. Digest remains the focused reader/interpreter for the single accepted source span.

**Boundary**: This decision did not change the live prompt or runtime contract beyond the already-promoted `attentional_v2.ingest.v14` / `attentional_v2-phase6-v64` baseline at the time it was recorded. It did not rerun formal evaluation and did not update evidence-catalog authority. The `preview_partition[]` follow-up named here was later implemented as the live v15 mechanism-private audit contract in `DEC-117`; only the first committed unit remains authoritative runtime input for Digest.

**Why this path won**: The reviewed A/B examples showed the strongest quality lift when the selector avoided a first-plausible paragraph stop and instead used the rest of the preview to see whether following paragraphs still belonged to the same local move. In `xidaduo_private_zh__segment_1`, the draft kept Siddhartha's external portrait together through the natural `可是` turn; in other windows it similarly preserved claim/support/refinement or principle/action pairs that the older selector split. This is a reader-control decision, not just prompt wording: Ingest looks ahead to choose the next work unit, while Digest stays centered on the chosen unit so future source text is not consumed early.

**Primary evidence**:
- `7475d01` `feat: promote ingest window partition prompt`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/backend-reader-evaluation.md`
- `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md`
- `docs/implementation/new-reading-mechanism/ingest-select-next-unit-window-partition-draft-prompt.md`
- `reading-companion-backend/src/attentional_v2/prompts/ingest.py`
- `reading-companion-backend/eval/runs/attentional_v2/ingest_select_next_unit_rolling_ab_probe_20260610/analysis/rolling_select_next_unit_ab/README.md`
- `reading-companion-backend/eval/runs/attentional_v2/ingest_select_next_unit_rolling_ab_probe_20260610/analysis/rolling_select_next_unit_ab/segments/xidaduo_private_zh__segment_1/window_partition_draft_units.md`

## Entry 114
**ID**: DEC-117
**Status**: active

**Decision / Inflection**: Promote Ingest `preview_partition[]` from a follow-up candidate into the live v15 mechanism-private audit contract.

**Period**: June 13, 2026, after accepting the bounded-lookahead explanation in `DEC-116` and deciding to make Ingest's whole-preview map explicit for audit.

**Decision**: Live `attentional_v2` Ingest now requires a structured `preview_partition[]` alongside the authoritative `unit`. `preview_partition[0]` must match `unit.end_paragraph_n` / `unit.end_at`; later entries title provisional future units and expose the model's whole-window semantic map. Runtime still accepts only the first unit for Digest, resolves it to the authoritative `source_span` / `source_span_id`, and records later partition resolution only as audit metadata.

**Boundary**: This is a mechanism-private prompt/schema/runtime artifact change, not a frontend/public API change and not a Unit Memory retrieval change. `retrieve_unit_memory` action-tool inputs and recall matching semantics remain unchanged, and tool preflight does not require `preview_partition[]`. No formal A/B evaluation was rerun and historical June 2026 A/B report packages were not regenerated.

**Why this path won**: The prior review showed that seeing the whole preview helps choose the first semantic unit. Requiring `preview_partition[]` makes that planning frame explicit, improves auditability, and gives future reviewers a way to see whether Ingest over-split, over-merged, or understood the second unit boundary that justified the first boundary.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/ingest-next-unit-optimization-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/attentional_v2/prompts/ingest.py`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 115
**ID**: DEC-118
**Status**: active

**Decision / Inflection**: Make live Ingest preview construction character-bounded instead of paragraph-count bounded.

**Period**: June 13, 2026, after reviewing `window_partition_draft_preview_units.md` examples where dialogue-heavy short paragraphs caused the preview to stop before a complete scene arc was visible.

**Decision**: Live `attentional_v2` now builds the Ingest lookahead preview by adding paragraph-aligned slices until source tail, the source-character hard budget, or an emergency paragraph guard. `preview_hard_max_chars` remains `7000`, `emergency_max_preview_paragraphs` defaults to `200`, and old `max_lookahead_paragraphs` policy values are ignored as normal stopping rules. Preview metadata now records `preview_end_reason` so audits can distinguish source-tail, hard-budget, emergency-guard, and empty previews.

**Boundary**: This is a runtime preview-construction repair, not an Ingest prompt/schema change, not a Unit Memory retrieval change, and not a frontend/public API change. Historical A/B report packages were not regenerated, and no formal A/B rerun was launched in this slice.

**Why this path won**: The reviewed Siddhartha father-son dialogue showed that a low paragraph-count cap can make a dialogue preview look structurally full while still containing only a few hundred source characters and missing the decisive scene resolution. Since modern model context is not the limiting factor for this bounded lookahead, source-character budget is the better capacity rule; paragraphs remain the coordinate and assembly boundary.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/ingest-next-unit-optimization-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 116
**ID**: DEC-119
**Status**: active

**Decision / Inflection**: Retire MiniMax official-key targets from the current local LLM posture and use OpenCode Go as the active key path.

**Period**: June 13, 2026, after confirming the available MiniMax official keys were no longer usable and the current runnable provider path was OpenCode Go.

**Decision**: Active local profiles should route through `LLM_TARGETS_PATH` / `LLM_PROFILE_BINDINGS_PATH` to OpenCode Go targets using `OPENCODE_GO_API_KEY`, with `opencode_deepseek_v4_flash` as the primary local target. MiniMax official-key registry examples and script defaults are removed from the current path; historical MiniMax protocol behavior remains documented only as compatibility evidence.

**Boundary**: This is an operational LLM provider-posture cleanup, not an Ingest/Digest prompt/schema change, not a Unit Memory semantic change, and not a frontend/public API change. The shared gateway still supports multiple provider contracts and legacy env/registry surfaces when explicitly configured, but the current checkout no longer recommends or defaults to MiniMax official-key routing.

**Why this path won**: Keeping dead MiniMax targets in examples and default script arguments made later diagnostics ambiguous: failures could be caused by stale credentials instead of the actual Ingest prompt, preview sizing, or JSON-object tool-loop behavior under review. Moving active defaults to the only currently usable key path keeps future probes reproducible and makes remaining LLM-call issues easier to diagnose.

**Primary evidence**:
- `README.md`
- `docs/current-state.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/llm-structured-output-protocol-note.md`
- `reading-companion-backend/.env.example`
- `reading-companion-backend/config/llm_targets.local.example.json`
- `reading-companion-backend/config/llm_profile_bindings.local.example.json`
- `reading-companion-backend/config/llm_registry.example.json`
- `reading-companion-backend/src/config.py`

## Entry 117
**ID**: DEC-120
**Status**: active

**Decision / Inflection**: Make live Ingest preview capacity token-bounded and constrain non-first preview-partition output burden.

**Period**: June 13, 2026, after the character-bounded preview repair fixed the Siddhartha dialogue under-preview but made later previews too long and output-heavy.

**Decision**: Live `attentional_v2` now builds the Ingest lookahead preview with token-bounded, paragraph-aligned assembly. The default policy is `preview_soft_min_tokens=1000`, `preview_target_max_tokens=1800`, `preview_hard_max_tokens=2600`, and `emergency_max_preview_paragraphs=200`; old char-budget and paragraph-count policy snapshots no longer control normal preview stopping. Preview metadata records `estimated_token_count` and `preview_token_estimator`. Ingest prompt v16 / promptset v66 keeps the same output schema, but states that only the committed first unit gets the optional top-level boundary `reason`; later `preview_partition[]` entries stay compact audit records with title, boundary, and status.

**Boundary**: This is an Ingest runtime/prompt-discipline change, not a Digest behavior change, Unit Memory retrieval change, frontend/public API change, or historical A/B report regeneration. Paragraph-char `SourceSpan` / `source_span_id` remain the authoritative accepted-unit coordinates.

**Why this path won**: The interim 7000-character preview solved the short-dialogue under-preview defect but pushed Ingest into multi-page planning windows, especially for Chinese text with many short paragraphs. Token budget better tracks the model's real workload while keeping the lookahead large enough to see the first unit and the next-unit turn. Constraining later partitions keeps the audit map useful without letting non-authoritative future units consume output budget.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/ingest-next-unit-optimization-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/prompts/ingest.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/unit_span_ledger.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 118
**ID**: DEC-121
**Status**: active

**Decision / Inflection**: Calibrate live Ingest v16 preview capacity upward after the first token-bounded focused probe.

**Period**: June 13, 2026, after reviewing the live v16 Siddhartha focused report through old Unit 013.

**Decision**: Keep the token-bounded paragraph-aligned preview policy and Ingest v16 / promptset v66 contract, but raise the live default capacity from `preview_soft_min_tokens=1000`, `preview_target_max_tokens=1800`, `preview_hard_max_tokens=2600` to `preview_soft_min_tokens=1600`, `preview_target_max_tokens=3000`, `preview_hard_max_tokens=4200`; `emergency_max_preview_paragraphs` remains `200`. This is a capacity calibration only: `unit`, `preview_partition[]`, Unit Memory retrieval, Digest behavior, and frontend/public API contracts do not change.

**Boundary**: This is not a formal A/B rerun, not a prompt/schema version bump, and not a historical report-package regeneration. It updates live runtime defaults and the stable docs that name those defaults.

**Why this path won**: The initial v16 token-bounded preview solved the severe prompt/output burden of the interim 7000-character preview, but the focused Siddhartha report suggested the window had become slightly narrow for Ingest's planning role. Ingest benefits from enough visible future text to decide whether the current local move is a standalone unit or part of a larger scene. Expanding to roughly `1.6x-1.7x` the initial token window gives more peripheral context while staying materially lighter than the prior character-bounded windows.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/ingest-next-unit-optimization-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/attentional_v2/source_spans.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`

## Entry 119
**ID**: DEC-122
**Status**: active

**Decision / Inflection**: Define Source Normalization as the upstream solution for footnote/noise text entering Ingest.

**Period**: June 13, 2026, after reviewing Siddhartha report units where translator/endnote paragraphs were parsed as body text and Ingest correctly selected them as standalone units.

**Decision**: Treat source cleanup as an import-time Source Normalization layer over original paragraph/block records. The design classifies records into mainline, heading, auxiliary-note, reference-like, front/back-matter, layout-noise, caption/table-support, or uncertain-keep-mainline roles before Ingest/Digest run. Ingest must not emit arbitrary skip operations; it reads only the normalized mainline stream. Raw paragraph coordinates remain canonical, and v1 does not introduce persistent `reading_blocks[]`.

**Boundary**: This is a design direction and documentation update, not a live parser/runtime change, not an Ingest prompt/schema change, not a Digest behavior change, and not a frontend highlight-contract change. Current live behavior still filters only paragraphs already marked `text_role == "auxiliary"`.

**Why this path won**: The problematic Siddhartha units were not caused by bad next-unit reasoning; the source stream told Ingest that translator notes were body paragraphs. A separate source-normalization layer can use deterministic structure evidence plus conservative LLM classification to keep footnotes, note clusters, layout noise, and reference apparatus out of the mainline reader while preserving original coordinates for highlights and support-context retrieval.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/source-normalization-design.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/iterator_reader/parse.py`
- `reading-companion-backend/src/attentional_v2/source_spans.py`

## Entry 120
**ID**: DEC-123
**Status**: active

**Decision / Inflection**: Implement Source Normalization v1 for newly parsed books.

**Period**: June 13, 2026, immediately after `DEC-122` established Source Normalization as the upstream answer to footnote/noise paragraphs entering Ingest.

**Decision**: New parses now run import-time Source Normalization before `public/book_document.json` is persisted. The parser preserves paragraph coordinates and source text, extracts lightweight EPUB/HTML evidence, runs a whole-book LLM source-flow classifier in bounded chunks, validates conservatively, attaches `source_normalization` metadata to each paragraph, rebuilds the sentence layer, and lets existing downstream mechanisms continue to use the coarse `text_role == "auxiliary"` gate. Existing parsed artifacts are not automatically migrated or rewashed.

**Boundary**: This is a parser/source-substrate change only. It does not change Ingest/Digest prompts or schemas, Unit Memory retrieval, accepted `SourceSpan` coordinates, frontend/public API payloads, historical eval packages, or old parsed outputs. If the classifier fails, parse degrades to deterministic roles and records diagnostics instead of failing the book parse.

**Why this path won**: The product needs clean mainline reading input, but Ingest should not become a skip-span planner. Whole-book classification gives the model enough context to recognize source-flow apparatus, while conservative merge rules prevent the classifier from deleting unusual literary forms, numbered body aphorisms, dialogue, poems, or other author-intended text without structural evidence.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/source-normalization-design.md`
- `docs/backend-reading-mechanism.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/reading_runtime/source_normalization.py`
- `reading-companion-backend/src/iterator_reader/parse.py`
- `reading-companion-backend/src/reading_core/book_document.py`
- `reading-companion-backend/tests/test_iterator_parse.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`

## Entry 121
**ID**: DEC-124
**Status**: active

**Decision / Inflection**: Upgrade Source Normalization to markup-aware v1.1 guardrails for new parses.

**Period**: June 13, 2026, after a real Siddhartha Source Normalization probe showed that v1 solved clustered footnotes but still missed single footnotes without enough retained markup evidence, and could falsely exclude blockquote poem lines when the parser emitted both a parent aggregate and child paragraphs.

**Decision**: New parses now preserve source-structure metadata on paragraph records: ancestor tags/classes/ids/EPUB types/roles plus bounded inline anchor ids/hrefs/texts. The EPUB parser skips pure parent containers that only aggregate textual child blocks, so `blockquote > p` keeps the child paragraph records without emitting a duplicate parent paragraph. Source Normalization v1.1 uses explicit footnote/endnote/note-definition markup as deterministic exclusion evidence, keeps linked note/numbered-note cluster guardrails, tightens `layout_noise` so duplicate/repeated LLM reasons need deterministic layout-noise evidence, and protects blockquote/poem/verse/letter正文 from false auxiliary/noise exclusion unless explicit auxiliary/reference evidence is also present.

**Boundary**: This remains a parser/source-substrate change for newly created `book_document.json` files only. Existing parsed artifacts are not migrated or rewashed. It does not change Ingest/Digest prompts or schemas, Unit Memory retrieval, accepted `SourceSpan` coordinates, frontend/public API payloads, or historical eval/report packages.

**Why this path won**: The failures were source-substrate failures, not Ingest reasoning failures. The raw EPUB already had useful structure such as `div.fnote` and `blockquote > p`, but v1 did not carry enough of that structure into paragraph records and allowed the classifier to treat short literary lines as duplicate noise. Markup-aware deterministic evidence gives the normalizer a simple, auditable way to remove source apparatus while preserving unusual author-intended literary forms and original highlight coordinates.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/source-normalization-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/iterator_reader/parse.py`
- `reading-companion-backend/src/reading_core/book_document.py`
- `reading-companion-backend/src/reading_runtime/source_normalization.py`
- `reading-companion-backend/tests/test_iterator_parse.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`

## Entry 122
**ID**: DEC-125
**Status**: active

**Decision / Inflection**: Switch live Source Normalization to deterministic-only v1.2.

**Period**: June 14, 2026, after partial multi-book validation showed that broad LLM source-flow classification could falsely exclude real正文, especially when inline note references were confused with note definitions.

**Decision**: New parses still run Source Normalization before `public/book_document.json` is persisted, but the live default no longer calls a whole-book LLM classifier. Source Normalization v1.2 uses deterministic source-structure evidence only: explicit footnote/endnote/translator-note/reference containers and note-definition anchors can set `text_role="auxiliary"`, while inline body note references such as `s1 -> #f1` or `noteref-1 -> #note-1` remain mainline. Malformed orphan-note-like paragraphs without structural proof are recorded as audit candidates but stay `body`. Existing paragraph coordinates, source text, locators, and frontend highlight compatibility remain unchanged.

**Boundary**: This is a parser/source-substrate change for newly created parsed-book documents only. It does not change Ingest/Digest prompts or schemas, Unit Memory retrieval, accepted `SourceSpan` coordinates, frontend/public API payloads, historical eval/report packages, or existing parsed artifacts. Optional classifier hooks may remain for tests or offline audit, but they are not live visibility authority.

**Why this path won**: The original Siddhartha footnote failure can be solved by simple EPUB/HTML structure such as `div.fnote` and `f1 -> #s1` note-definition anchors. A broad LLM classifier added cost and false-positive risk that conflicts with the stronger product rule: never remove author-intended正文 unless the source itself provides strong apparatus evidence.

**Primary evidence**:
- `docs/implementation/new-reading-mechanism/source-normalization-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `reading-companion-backend/src/reading_runtime/source_normalization.py`
- `reading-companion-backend/tests/test_iterator_parse.py`
- `reading-companion-backend/tests/test_reading_core_sentences.py`
- `reading-companion-backend/tests/test_attentional_v2_source_spans.py`

## Entry 123
**ID**: DEC-126
**Status**: active

**Decision / Inflection**: Promote the source-normalized deterministic v1.2 user-level selective dataset package as the active local/user-level pointer.

**Period**: June 14, 2026, after the source-normalized candidate rebuild preserved all user-level note cases while removing structurally marked Siddhartha footnotes from the active source window.

**Decision**: The active `user-level selective v1` split manifest now points to `attentional_v2_user_level_selective_v1_repaired_20260614_source_norm_v1_2`. The package keeps `5` reading segments and `202` note cases, was rebuilt from fresh isolated Source Normalization v1.2 deterministic-only parses, and preserves non-empty `source_span_slices` for every note case. Relative to the previous active `20260422` package, `source_span_text` remains stable while paragraph indexes may move after auxiliary / duplicate source records are removed. In `xidaduo_private_zh__segment_1`, structural footnote definitions such as `Brahmanen`, `Magadha`, `[2]Vishnus`, and `[3]Lakschmi` are removed from the active source window; body note references remain visible. The malformed orphan residue `1《爱经》...` remains body-visible under the conservative deterministic policy.

**Boundary**: This promotes the local dataset pointer and default dataset builder target only. It does not mutate historical dataset packages, historical eval runs, the evidence catalog, or the April 19 formal rerun result, which still reflects `attentional_v2_user_level_selective_v1_repaired_20260416`. It does not change Ingest, Digest, Unit Memory, frontend/public APIs, or source-coordinate contracts.

**Why this path won**: The source-normalized candidate fixed the concrete Siddhartha footnote-window pollution that motivated the rebuild while keeping the benchmark's scoring surface stable: all note cases remain, source-span text remains unchanged, and the previous active package remains available as a comparison baseline. Promoting a new active pointer preserves historical evidence integrity better than rewriting the old package in place.

**Primary evidence**:
- `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- `reading-companion-backend/eval/attentional_v2/user_level_selective_v1.py`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260614_source_norm_v1_2/manifest.json`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260614_source_norm_v1_2/candidate_validation_report.md`
- `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260614_source_norm_v1_2/source_normalized_window_review_against_20260422.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `docs/backend-reader-evaluation.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 124
**ID**: DEC-127
**Status**: active

**Decision / Inflection**: Make `retrieve_unit_memory` action-tool args the only model-authored Ingest Unit Memory recall-intent surface.

**Period**: June 14, 2026, after the focused larger-preview Siddhartha v16 probe failed at unit 7 with an `llm_contract` caused by final `memory_recalls[]` language/tool-call mismatch even though provider calls returned `ok`.

**Decision**: Live Ingest is bumped to `attentional_v2.ingest.v17` / promptset `attentional_v2-phase6-v67`. The final Ingest result now carries only the accepted boundary contract and audit map: `unit.end_paragraph_n`, `unit.end_at`, `preview_partition[]`, and optional first-unit boundary `reason`. Prior-reading recall intent is submitted only through the `retrieve_unit_memory` action tool. Runtime derives private/audit `memory_recalls[]` from the action-tool args, and final-output validation ignores any legacy final `memory_recalls[]` echo rather than requiring it to match the tool call.

**Boundary**: This does not change Ingest into two business nodes, does not change Unit Memory retrieval semantics, retrieval indexes, Digest `ReadingMemory`, frontend/public APIs, source coordinates, or historical eval/report artifacts. The provider-level tool loop may still have an action-tool turn, final JSON turn, and repair turn; those remain one Ingest business call cycle.

**Why this path won**: The failure was not an OpenAI-compatible JSON-object / action-tool incompatibility. The real problem was duplicated authorship: the model had to express the same recall intent once as an action-tool call and again as final structured output. Keeping the action tool as the single recall-intent channel preserves strict preflight validation while removing a brittle final/tool signature match that could stop otherwise valid boundary selection.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/ingest.py`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/implementation/new-reading-mechanism/llm-structured-output-protocol-note.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 125
**ID**: DEC-128
**Status**: active

**Decision / Inflection**: Promote Marginalia as the canonical Digest visible-note concept.

**Period**: June 20, 2026, after reviewing the current Digest prompt and deciding that `Annotation` was too generic for the product-visible note surface.

**Decision**: Live Digest is bumped to `attentional_v2.digest.v10` / XML spec v10 / promptset `attentional_v2-phase6-v68`, with output contract `digest_understanding_response_marginalia_json_v4`. The canonical model-facing Digest outputs are now `understanding`, `response`, and `marginalia[]`. Prompt XML uses `<Marginalia>` / `<MarginaliaField>`, and the prompt frames Marginalia as page-margin reader notes anchored to exact source spans rather than generic explanatory annotations. Runtime stores canonical `DigestResult.marginalia`, Unit Memory writes `digest.marginalia`, retrieval derives `unit_marginalia`, and public/frontend surfaces expose canonical `marginalia_id`, `marginalia_type`, `visible_marginalia`, and `featured_marginalia`.

**Boundary**: This is a terminology and contract migration, not a Marginalia quality-policy change. Existing historical eval artifacts, old decision entries, `reaction_records.json` filenames, old `annotations[]` payloads, `surfaced_reactions`, public `reaction_*` fields, marks routes keyed by `{reaction_id}`, and third-party EPUB.js `rendition.annotations` remain compatibility or external-library vocabulary. New code/docs should prefer Marginalia names while compatibility adapters keep older artifacts and clients working.

**Why this path won**: `Marginalia` better names the product value: a reader-visible note in the margin, grounded in a source quote, carrying the companion's live reading attention. `Annotation` sounded like a generic labeling/explanation task, and `reaction` carried old mechanism-family baggage. The migration lets the main product surface use the right concept without breaking old data or old public fields in the same slice.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/unit_memory.py`
- `reading-companion-backend/src/api/schemas.py`
- `reading-companion-backend/src/api/app.py`
- `reading-companion-backend/src/library/catalog.py`
- `reading-companion-frontend/src/app/lib/api.ts`
- `reading-companion-frontend/src/app/lib/contract.ts`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/api-contract.md`
- `docs/api-integration.md`
- `docs/backend-state-aggregation.md`
- `docs/implementation/new-reading-mechanism/digest-understanding-response-marginalia-design.md`
- `docs/implementation/new-reading-mechanism/digest-marginalia-quality-sourcebook.md`

## Entry 126
**ID**: DEC-129
**Status**: active

**Decision / Inflection**: Simplify live Digest Marginalia output to exact quote plus optional note content.

**Period**: June 20, 2026, after drafting the Marginalia quality prompt and deciding that highlight-only marks must be first-class visible notes rather than forced notes with filler content.

**Decision**: Live Digest is bumped to `attentional_v2.digest.v11` / XML spec v11 / promptset `attentional_v2-phase6-v69`, with output contract `digest_understanding_response_marginalia_json_v5`. The normal model-facing Marginalia item now contains only `source_quote` and optional `content`: `source_quote` is required, empty/null/omitted `content` means highlight-only, and non-empty `content` means note-bearing Marginalia. The prompt now teaches the model to choose between no mark, highlight-only, and note-bearing Marginalia using source-grounded decision rules, minimal-intervention discipline, and evidence/honesty checks.

**Boundary**: This does not change Ingest, Unit Memory retrieval semantics, Digest `Understanding` / `Response` ownership, frontend routes, or historical artifacts. Legacy `annotations[]`, `surfaced_reactions`, `reaction_*` public fields, and inherited `prior_link` / `outside_link` / `search_intent` metadata remain compatibility-read or adapter fields where older artifacts and internal callers require them, but they are no longer part of the live Digest model-facing Marginalia item.

**Why this path won**: The product-visible reading surface needs both highlights and notes. Requiring `content` forced the model to manufacture marginal notes when the correct reader action was simply to preserve a strong quote. Keeping only `source_quote` plus optional `content` matches normal reading-app behavior, preserves source anchoring, reduces model output burden, and keeps future research / backlink behavior from hiding inside ordinary Marginalia metadata.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_unit_memory.py`
- `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 127
**ID**: DEC-130
**Status**: active

**Decision / Inflection**: Tighten highlight-only Marginalia to excerpt-worthy source quotes.

**Period**: June 21, 2026, after the first Digest Marginalia v11 smoke examples showed that the prompt could treat structurally ordinary or context-dependent sentences as quote-only highlights.

**Decision**: Live Digest is bumped to `attentional_v2.digest.v12` / XML spec v12 / promptset `attentional_v2-phase6-v70` while keeping output contract `digest_understanding_response_marginalia_json_v5`. The Marginalia schema remains `source_quote` plus optional `content`, but the prompt now teaches a stricter selection boundary: highlight-only Marginalia is for exact quotes that can stand alone as excerpt-worthy spans, where another reader can see the reason for preservation from the quoted words themselves. Spans whose value depends on structure, context, contrast, turn, or explanation should be skipped, represented in Understanding/Response, or emitted as note-bearing Marginalia with non-empty `content`.

**Boundary**: This is a quality-policy prompt change, not a public API or runtime schema change. It does not change Ingest, Unit Memory retrieval semantics, Digest `Understanding` / `Response` ownership, source-coordinate resolution, frontend routes, or compatibility handling for legacy `annotations[]`, `surfaced_reactions`, `reaction_*`, `prior_link`, `outside_link`, or `search_intent` fields.

**Why this path won**: Highlight-only marks should behave like real reader highlights: the excerpt itself carries enough meaning, force, image, distinction, or principle to be worth preserving without added commentary. Many topic sentences, roadmaps, recaps, and setup questions are important to comprehension but are not good quote-only highlights because their value disappears outside surrounding context. Separating excerpt-worthiness from structural importance should reduce bland highlights without forcing unnecessary notes.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/eval/attentional_v2/run_digest_marginalia_live_smoke.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 128
**ID**: DEC-131
**Status**: active

**Decision / Inflection**: Add intrinsic excerpt value as a required gate for highlight-only Marginalia.

**Period**: June 21, 2026, immediately after the v12 highlight-only boundary review clarified that "standing alone" is necessary but not enough: the quoted source text must itself have value as an excerpt.

**Decision**: Live Digest is bumped to `attentional_v2.digest.v13` / XML spec v13 / promptset `attentional_v2-phase6-v71` while keeping output contract `digest_understanding_response_marginalia_json_v5`. The prompt now states that highlight-only Marginalia has two gates: the quote must be self-contained enough to stand alone, and it must have intrinsic excerpt value. A merely complete, informative, or easy-to-locate sentence is not enough. Quote-only highlights should target source text whose original wording, image, insight, emotional force, conceptual compression, or compact principle carries value by itself.

**Boundary**: This is a prompt-selection discipline refinement only. It does not change the Marginalia item schema, Digest runtime normalization, source-quote resolution, public API, frontend routes, Unit Memory retrieval semantics, Ingest behavior, or compatibility handling for historical annotation/reaction artifacts.

**Why this path won**: The product should surface highlights that feel like real reader excerpts, not just locally useful markers. The added gate makes the basic "text itself has value" condition explicit, preserving the difference between a sentence that is important for comprehension and a sentence that is worth extracting because it has its own force.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 129
**ID**: DEC-132
**Status**: active

**Decision / Inflection**: Add private selection reasons for highlight-only Marginalia.

**Period**: June 21, 2026, after deciding that highlight-only marks should still leave an auditable reason for why the quote was selected, while note-bearing Marginalia already carries its reason in visible note content.

**Decision**: Live Digest is bumped to `attentional_v2.digest.v14` / XML spec v14 / promptset `attentional_v2-phase6-v72`, with output contract `digest_understanding_response_marginalia_json_v6`. The visible Marginalia item remains `source_quote` plus optional `content`: empty, null, or omitted `content` means highlight-only; non-empty `content` means note-bearing. A new private `marginalia_audit[]` field is required in final Digest output, and each highlight-only Marginalia item must have one matching audit item with the same exact `source_quote` and a short `selection_reason`.

**Boundary**: This does not expose selection reasons as product-visible Marginalia content, does not add a public/frontend field, and does not change Ingest, Unit Memory retrieval semantics, source-coordinate resolution, or legacy annotation/reaction compatibility. Note-bearing Marginalia should not receive private audit reasons because the visible `content` is already the reader-facing reason.

**Why this path won**: Highlight-only selection is deliberately stricter after DEC-130 and DEC-131, but an empty visible `content` field makes later audit harder: reviewers can see the quote, but not why the model believed it had standalone excerpt value. Adding a short private reason gives prompt pressure and reviewability without turning every highlight into a visible note or polluting Unit Memory retrieval text with internal justification.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/unit_memory.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_unit_memory.py`
- `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
- `docs/implementation/new-reading-mechanism/digest-understanding-response-marginalia-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 130
**ID**: DEC-133
**Status**: active

**Decision / Inflection**: Move private highlight-selection reasons inline on Marginalia items.

**Period**: June 21, 2026, after reviewing the v14 smoke report shape and deciding that a separate top-level `marginalia_audit[]` duplicated each highlight record too heavily.

**Decision**: Live Digest is bumped to `attentional_v2.digest.v15` / XML spec v15 / promptset `attentional_v2-phase6-v73`, with output contract `digest_understanding_response_marginalia_json_v7`. The live final output now requires only top-level `understanding`, `response`, and `marginalia[]`. Each Marginalia item still requires `source_quote`; `content` remains optional / nullable / empty for highlight-only marks. Highlight-only Marginalia must include a short private inline `selection_reason`; note-bearing Marginalia may omit it because visible `content` already carries the reason.

**Boundary**: `selection_reason` is mechanism-private audit metadata, not public/frontend Marginalia content. New live prompts, schemas, read audit, Unit Memory entries, and smoke reports do not emit a fresh top-level `marginalia_audit[]`; legacy v14 artifacts may still be read as compatibility input and merged by `source_quote` where needed. This does not change Ingest, Unit Memory retrieval semantics, source-coordinate resolution, public marks payloads, or legacy reaction aliases.

**Why this path won**: The separate audit array made reports noisier and created a second structure to keep synchronized with the visible Marginalia item. Inline private `selection_reason` keeps the reason adjacent to the selected quote, preserves the prompt pressure needed for highlight-only quality, and avoids duplicating the whole Marginalia list in runtime/debug artifacts.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/src/attentional_v2/llm_output_tools.py`
- `reading-companion-backend/src/attentional_v2/llm_calls.py`
- `reading-companion-backend/src/attentional_v2/unit_memory.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/eval/attentional_v2/run_digest_marginalia_live_smoke.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_attentional_v2_unit_memory.py`
- `reading-companion-backend/tests/test_digest_marginalia_live_smoke_runner.py`
- `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
- `docs/implementation/new-reading-mechanism/digest-understanding-response-marginalia-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 131
**ID**: DEC-134
**Status**: active

**Decision / Inflection**: Require Marginalia quotes to use the smallest complete local meaning span.

**Period**: June 21, 2026, after live classic-passage smoke review showed fragmentary `source_quote` choices such as isolated clauses or terms that were exact but not meaningful enough as reader-facing Marginalia anchors.

**Decision**: Live Digest is bumped to `attentional_v2.digest.v16` / XML spec v16 / promptset `attentional_v2-phase6-v74`, while keeping output contract `digest_understanding_response_marginalia_json_v7`. Marginalia `source_quote` selection now says to choose the smallest complete contiguous local meaning span, not the shortest exact phrase. Highlight-only Marginalia has three gates: complete local meaning, standalone readability, and intrinsic excerpt value. Famous tail clauses, clipped predicates, and adjacent sentences or clauses that jointly form one coherent image, thought, contrast, or emotional movement should be quoted together with the smallest needed surrounding span instead of split into fragments.

**Boundary**: This is a prompt-selection discipline refinement only. It does not change the Marginalia item schema, Digest runtime normalization, Unit Memory retrieval semantics, public API / frontend fields, Ingest behavior, or source-coordinate resolution. The final output remains `understanding`, `response`, and `marginalia[]`, with inline private `selection_reason` required only for highlight-only items.

**Why this path won**: Exact matching alone can push the model toward short anchors that satisfy validators but feel broken to readers. Reader-visible Marginalia should quote a complete thought, image, or local claim. The new rule keeps quotes tight without making them fragmentary, and it directly addresses highlight-only failures where the selected text was important only after surrounding context or explanation.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/digest.py`
- `reading-companion-backend/eval/attentional_v2/run_digest_marginalia_live_smoke.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `reading-companion-backend/tests/test_digest_marginalia_live_smoke_runner.py`
- `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
- `docs/implementation/new-reading-mechanism/digest-understanding-response-marginalia-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`

## Entry 132
**ID**: DEC-135
**Status**: active

**Decision / Inflection**: Add the same-local-function boundary rule to live Ingest unit selection.

**Period**: June 21, 2026, after the five-book Digest v16 diagnostic revealed that the current live Ingest selector could split the Siddhartha opening at `P3` even though earlier reviewed Ingest reports kept the opening character/social setup together through `P8` or `P9`.

**Decision**: Live Ingest is bumped to `attentional_v2.ingest.v18` / XML spec v18 / promptset `attentional_v2-phase6-v75`, while keeping output contract `ingest_unit_boundary_preview_partition_json_v3`. The prompt now states that adjacent paragraphs jointly performing the same setup, character construction, scene build, argument support, example chain, or emotional turn remain one unit even when smaller facets can be titled separately. It explicitly warns that `preview_partition[]` titles should not force an early split: before committing a boundary, the model should ask whether the next visible paragraphs start a genuinely new move or merely continue the same local function from another angle.

**Boundary**: This is a prompt-selection discipline refinement only. It does not change Ingest schema, `preview_partition[]` shape, boundary resolver behavior, Unit Memory retrieval semantics, Digest behavior, Source Normalization, public API, frontend contracts, or historical eval/report artifacts.

**Why this path won**: Whole-preview partitioning improved first-unit selection by making later context visible, but it also introduced a new failure mode: the model can over-trust its ability to title smaller sub-aspects and mistake those titles for true unit boundaries. The same-local-function rule preserves the global planning benefit while making it harder to split a single exposition, portrait, scene, or support chain just because it contains several namable facets.

**Primary evidence**:
- `reading-companion-backend/src/attentional_v2/prompts/ingest.py`
- `reading-companion-backend/tests/test_attentional_v2_llm_calls.py`
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`
- `docs/implementation/new-reading-mechanism/ingest-next-unit-optimization-design.md`
- `docs/backend-reading-mechanisms/attentional_v2.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
