# API Integration

Purpose: describe the active routed-frontend endpoint surface and runtime coordination behavior.
Use when: changing endpoint usage, polling, WebSocket refresh behavior, or frontend/runtime data flow.
Not for: canonical field definitions, route authority, or product-level page responsibilities.
Update when: the connected endpoint surface, runtime coordination model, or frontend/backend data flow changes.

This file is the operational companion to `docs/api-contract.md`.
It intentionally tracks the current routed frontend surfaces and the hooks/components they reach, rather than every dormant API surface that still exists in the repo.

## Local Base URLs
- API base: `http://localhost:8000`
- WS base: `ws://localhost:8000`

Frontend defaults can be overridden with:
- `VITE_API_BASE_URL`
- `VITE_WS_BASE_URL`

## Active Routed Frontend Endpoints
- `POST /api/uploads/epub`
- `POST /api/books/{book_id}/analysis/start`
- `POST /api/books/{book_id}/analysis/resume`
- `GET /api/jobs/{job_id}`
- `GET /api/books`
- `GET /api/books/{book_id}`
- `GET /api/books/{book_id}/analysis-state`
- `GET /api/books/{book_id}/activity`
- `GET /api/books/{book_id}/marks`
- `GET /api/books/{book_id}/chapters/{chapter_id}`
- `GET /api/books/{book_id}/chapters/{chapter_id}/outline`
- `GET /api/books/{book_id}/cover`
- `GET /api/books/{book_id}/source`
- `GET /api/marks`
- `PUT /api/marks/{reaction_id}`
- `DELETE /api/marks/{reaction_id}`
- `WS /api/ws/books/{book_id}/analysis`

## Integration Notes
- In this document, public `analysis/*` routes and `analysis-state` refer to the current sequential deep-reading workflow. They do not refer to the older `book_analysis` capability.
- Backend images and source assets are returned as relative API paths and must be prefixed with the configured API base in the frontend.
- Backend `target_url`, `result_url`, and `open_target` values are frontend routes, not backend URLs.
- Backend analysis state and the mindstream view of the activity feed are used by the adaptive `/books/:id` overview when a book is in progress; WebSocket messages trigger refreshes, while polling remains the fallback.
- The top live line in `Reading mindstream` is driven by `analysis-state.current_reading_activity`, which is a realtime snapshot of the active reading phase rather than a persisted history item.
- The historical mindstream list still comes from `GET /api/books/{book_id}/activity` with `stream=mindstream` and remains separate from the live activity snapshot.
- Runtime guard events such as stalled heartbeats, timeout detection, unsupported runtime launches, and forced pauses are still written into the same activity feed with `stream=system`, but they are now reserved for internal diagnostics rather than the main user-facing overview.
- Additional system-side recovery events now include `resume_incompatible`, `fresh_rerun_started`, and `dev_run_abandoned`.
- `GET /api/books/{book_id}/analysis-log` remains available as an internal diagnostic endpoint, but it is no longer part of the routed frontend integration surface.
- Deferred upload stops after the chapter-level structure parse; `analysis/start` and `analysis/resume` then perform semantic segmentation as the preparation phase before deep reading continues on the same long-task surface.
- Public `book_id`, `reaction_id`, and `mark_id` values are integer IDs even when backend runtime artifacts still use internal string identifiers.
- `analysis-state.last_checkpoint_at` reflects deep-reading segment checkpoints as well as parse checkpoints, so the overview and runtime guards can point to the latest resumable point with one field.
- `WS /api/ws/jobs/{job_id}` still exists in the backend API and older upload/status surfaces, but it is not part of the current routed frontend integration.

## Machine-Readable Appendix
The JSON block below is the machine-readable appendix used by the integration drift checks.

```json
{
  "active_frontend_endpoints": [
    "POST /api/uploads/epub",
    "POST /api/books/{book_id}/analysis/start",
    "POST /api/books/{book_id}/analysis/resume",
    "GET /api/jobs/{job_id}",
    "GET /api/books",
    "GET /api/books/{book_id}",
    "GET /api/books/{book_id}/analysis-state",
    "GET /api/books/{book_id}/activity",
    "GET /api/books/{book_id}/marks",
    "GET /api/books/{book_id}/chapters/{chapter_id}",
    "GET /api/books/{book_id}/chapters/{chapter_id}/outline",
    "GET /api/books/{book_id}/cover",
    "GET /api/books/{book_id}/source",
    "GET /api/marks",
    "PUT /api/marks/{reaction_id}",
    "DELETE /api/marks/{reaction_id}",
    "WS /api/ws/books/{book_id}/analysis"
  ]
}
```
