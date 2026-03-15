# Decision Log

Purpose: preserve design evolution, key decisions, and rejected alternatives that would be difficult to reconstruct later from current-state docs alone.
Use when: tracing why the project converged on its current shape or recording a major change in direction.
Not for: routine change logs, source-of-truth engineering definitions, or interview-ready wording.
Update when: a major product or engineering decision is made, reversed, or becomes historically important to future contributors.

## Entry 1
**Decision**: Treat `sequential` deep reading as the primary product and engineering path.

**Context**: The repo contains broader and more prototype-like agent capabilities, but the project needed one dependable main loop that could be run, recovered, and explained end to end.

**Alternatives considered**: Keep a more generalized graph-first or `book_analysis`-led path as the default product direction.

**Why chosen**: A single main path made the system easier to validate, recover, and evolve without splitting effort across competing product stories.

**Trade-offs**: Experimental capabilities remained secondary, and some architectural flexibility was intentionally deprioritized in favor of a cleaner main path.

**Current-state references**: `docs/product-interaction-model.md`, `docs/runtime-modes.md`, `reading-companion-backend/AGENTS.md`

## Entry 2
**Decision**: Keep public naming, route, and ID normalization at the API layer.

**Context**: Internal runtime artifacts, legacy route shapes, and older taxonomy values do not line up perfectly with the current web contract.

**Alternatives considered**: Push normalization into the frontend, or force runtime artifacts to match the public contract exactly before returning anything.

**Why chosen**: The API layer was the narrowest place to preserve a stable external contract while allowing internal artifacts and migration paths to evolve more gradually.

**Trade-offs**: The backend now carries compatibility logic that would not exist in a greenfield system with no legacy artifacts.

**Current-state references**: `docs/api-contract.md`, `docs/api-integration.md`

## Entry 3
**Decision**: Treat resume and runtime recovery as part of the product, not just an operational concern.

**Context**: Long-running reading jobs can stall, restart, or span process boundaries, and a "just rerun it" posture would have made the core reading experience fragile.

**Alternatives considered**: Accept frequent reruns and keep recovery semantics largely invisible to the product layer.

**Why chosen**: For a book-length workflow, trust and continuity are part of the user-facing experience. Recovery had to be visible in system state, not hidden as an ops-only detail.

**Trade-offs**: Runtime semantics, checkpoint compatibility, and stalled-run handling became part of system complexity and documentation.

**Current-state references**: `docs/runtime-modes.md`, `docs/api-contract.md`, `docs/backend-sequential-lifecycle.md`
