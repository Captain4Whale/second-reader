# Workspace Overview

## What This Root Is For
- one place to understand the full product
- one place to understand the primary product interaction model
- one place to run local setup and dev commands
- one place to document front/back integration rules

## Key Workspace Docs
- Product interaction model: `docs/product-interaction-model.md`
- Public web/API contract: `docs/api-contract.md`
- Runtime integration notes: `docs/api-integration.md`
- Runtime launcher and deploy behavior: `docs/runtime-modes.md`
- Current focus, migration notes, and active risks: `docs/agent-handoff.md`

## Subprojects

### `reading-companion-backend`
- Python project declared in `pyproject.toml`
- FastAPI app in `src/api/app.py`
- CLI entrypoint in `main.py`
- runtime artifacts stored in:
  - `output/`
  - `state/`
- local server entrypoint: `serve.py`

### `reading-companion-frontend`
- Vite + React application
- routes in `src/app/routes.tsx`
- API client layer in `src/app/lib/api.ts`
- canonical frontend routes align with backend-returned route targets

## Runtime Boundaries
- Backend owns:
  - upload processing
  - background jobs
  - book manifests
  - chapter results
  - marks persistence
  - OpenAPI contract
- Frontend owns:
  - route rendering
  - upload form UX
  - polling/WebSocket UI updates
  - result views and mark actions

## Local Workflow
- Use the parent directory for shared commands.
- Use child directories when a task is clearly isolated.
- Keep runtime data in `reading-companion-backend/`.
- Do not assume the parent directory is the Git root.
- Runtime launcher intent is documented in `docs/runtime-modes.md`; do not infer it only from shell script names.

## Primary Integration Files
- Product flow:
  - `docs/product-interaction-model.md`
- Contract:
  - `docs/api-contract.md`
- Backend:
  - `reading-companion-backend/src/api/app.py`
  - `reading-companion-backend/src/api/schemas.py`
  - `reading-companion-backend/src/library/catalog.py`
- Frontend:
  - `reading-companion-frontend/src/app/lib/api.ts`
  - `reading-companion-frontend/src/app/lib/reactions.ts`
  - `reading-companion-frontend/src/app/routes.tsx`
