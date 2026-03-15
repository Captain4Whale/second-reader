# Reading Companion Workspace Guide

## Scope
- This parent directory is the shared workspace root for the Reading Companion project.
- Treat the codebase as one product with two sub-applications:
  - `reading-companion-backend`: FastAPI API, sequential deep-reading engine, runtime artifacts
  - `reading-companion-frontend`: Vite/React web client

## Precedence
- Root `AGENTS.md` defines cross-project rules.
- Child `AGENTS.md` files define local rules for that subproject.
- If rules conflict:
  1. obey this root file for workspace-level behavior
  2. obey the child file for subproject-local behavior

## Working Rules
- Start from the parent directory unless a task is explicitly isolated to one subproject.
- Check `README.md` and `docs/` before making structural changes.
- Preserve the two existing subdirectories and their boundaries. Do not collapse them into a new monorepo layout unless explicitly requested.
- Keep API changes synchronized across both sides:
  - backend contract changes require frontend route/client review
  - frontend integration changes require backend contract verification
- Prefer codifying workflows in root scripts and docs instead of leaving process knowledge only in chat.
- Keep runtime artifacts in `reading-companion-backend/` unless a task explicitly migrates them.
- Do not remove the frontend repo’s Figma Make history or generated structure unless the change has a clear maintenance benefit.

## Documentation Maintenance
- Update required docs in the same task when a change alters product behavior, runtime behavior, integration behavior, or maintenance expectations.
- Trigger conditions are additive. One change may require updates in more than one document.
- Keep `AGENTS.md` files rule-oriented and concise. Move detailed reference material into `docs/`.
- Avoid duplicating detailed guidance across files. Keep one primary source of truth and add short pointers elsewhere when needed.
- If you intentionally leave docs unchanged, you should have a concrete reason, not just “code is self-explanatory.”

### Trigger Matrix
- `README.md`
  - install/setup commands
  - startup commands
  - environment variables
  - default local URLs
  - quick-start or operator-facing run behavior
- `docs/workspace-overview.md`
  - workspace structure
  - backend/frontend ownership boundaries
  - shared entrypoints
  - cross-project collaboration model
- `docs/product-interaction-model.md`
  - product interaction model
  - primary user journey or page responsibilities
  - canonical product flow such as landing -> upload -> analysis -> book -> chapter -> marks
  - core UX conventions
  - when a temporary or compatibility flow becomes the primary product path, or the reverse
- `docs/api-contract.md`
  - public API fields
  - public enums
  - canonical routes
  - identifier conventions
  - stable response/request schemas
- `docs/api-integration.md`
  - active frontend-used endpoint surface
  - polling or WebSocket coordination
  - runtime data flow between frontend and backend
  - long-task integration assumptions
- `docs/runtime-modes.md`
  - launcher behavior
  - reload/supervision behavior
  - healthcheck behavior
  - deployment entrypoints
  - recovery or resume runtime rules
- `docs/language-governance.md`
  - visible-text governance
  - terminology ownership
  - locale rules
  - controlled copy sourcing
- `docs/agent-handoff.md`
  - current focus
  - migration status
  - temporary warnings
  - active risks
  - project context that is useful now but not yet a stable rule
- root `AGENTS.md`
  - document map
  - this trigger matrix
  - cross-project collaboration rules
  - reading order for new agent tasks
- child `AGENTS.md`
  - subproject-local and long-lived engineering constraints
  - implementation boundaries
  - recurring pitfalls that should become stable rules

### Cross-Doc Rules
- If the product interaction flow changes and that also changes routes or public payloads, update `docs/product-interaction-model.md`, `docs/api-contract.md`, and `docs/api-integration.md` in the same task.
- If the same change also shifts workspace ownership boundaries or the recommended reading order for agents, update `docs/workspace-overview.md` and root `AGENTS.md`.
- If a temporary handoff note repeats across tasks, promote it into the relevant `AGENTS.md` as a stable rule.
- If a new key document becomes part of the standard reading path, add it to `README.md` and the "First Files To Read" section here.

## First Files To Read
- Root:
  - `README.md`
  - `docs/workspace-overview.md`
  - `docs/product-interaction-model.md`
  - `docs/api-contract.md`
  - `docs/api-integration.md`
  - `docs/agent-handoff.md`
  - `docs/runtime-modes.md`
- Backend:
  - `reading-companion-backend/AGENTS.md`
  - `reading-companion-backend/src/api/app.py`
  - `reading-companion-backend/src/library/catalog.py`
- Frontend:
  - `reading-companion-frontend/AGENTS.md`
  - `reading-companion-frontend/src/app/lib/api.ts`
  - `reading-companion-frontend/src/app/routes.tsx`

## Default Local Commands
- `make doctor`
- `make setup`
- `make dev-backend`
- `make dev-frontend`
- `make dev`
- `make test`
- `make build`

## Language Governance
- Follow `docs/language-governance.md` before adding or changing visible text.
- Classify user-visible text first:
  - content text
  - interface/control text
  - system/program-state text
  - fixed brand/governed terminology
- Do not handwrite key terminology or key product copy directly in UI components.
- Brand name `书虫` stays fixed; app interface copy follows the frontend locale layer.
