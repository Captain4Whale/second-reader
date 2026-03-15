# Product Interaction Model

## Purpose
- This document is the repo-local source of truth for the primary product journey, page responsibilities, and interaction model.
- Use `docs/api-contract.md` for stable routes, public fields, enums, and identifier rules.
- Use `docs/api-integration.md` for runtime wiring, endpoint usage, polling, and WebSocket coordination.

## Core Product Promise
- Help readers discover viewpoints, tensions, and blind spots they did not notice while reading nonfiction.
- Preserve the feeling of "AI thinking while reading" rather than collapsing into a generic summary experience.
- Optimize for a thoughtful co-reader experience, not a report generator.

## Primary Product Path
### 1. Landing
- Canonical route: `/`
- Role: introduce the product, frame the reading experience, and route users into the book workflow.
- Ownership: frontend-owned experience; it is not a backend compatibility surface.

### 2. Upload Entry
- Canonical entry point: `/books?upload=1`
- Role: let the user bring a book into the system and choose whether analysis starts immediately or after outline parsing.
- `/upload` remains a compatibility redirect, not the primary product path.

### 3. Analysis Start And Resume
- Upload may be immediate or deferred.
- Deferred upload stops after chapter-level structure parsing.
- `analysis/start` and `analysis/resume` perform semantic segmentation and continue the deep-reading workflow on the main long-task surface.

### 4. Book Overview
- Canonical route: `/books/:id`
- Role: main control center for an in-progress or completed book.
- Responsibilities:
  - show current analysis state
  - surface current reading activity and program log context
  - expose resume/continue actions
  - provide chapter access and book-scoped marks context

### 5. Chapter Deep Read
- Canonical route: `/books/:id/chapters/:chapterId`
- Role: present the chapter reading artifact and support mark actions on reactions.
- This is the main surface for consuming finished deep-reading output.

### 6. Global Marks
- Canonical route: `/marks`
- Role: provide a cross-book saved-mark view and re-entry path back into books and chapters.

## Page Responsibilities
- Landing:
  - frame the experience
  - preview the product
  - route users into books/upload
- Bookshelf and upload flow:
  - act as the operational entrypoint for library management and new uploads
  - expose upload-triggered analysis entry
- Book overview:
  - act as the adaptive home for progress, controls, state panels, and chapter navigation
- Chapter page:
  - act as the main reading artifact surface for a completed chapter
- Marks page:
  - act as the global recall surface for saved reactions

## Interaction Rules
- The canonical user journey is `landing -> upload -> analysis -> book overview -> chapter -> marks`, even though users may re-enter later at `/books`, `/books/:id`, or `/marks`.
- Backend `target_url`, `result_url`, and `open_target` values should send users into canonical frontend routes.
- Compatibility routes may remain as redirects, but they should not become the primary user path without updating this document and `docs/api-contract.md`.
- Live analysis behavior depends on both the live snapshot (`analysis-state.current_reading_activity`) and the historical activity/program-log stream.

## Product Defaults
- `sequential` deep reading is the primary product mode and default optimization target.
- `book_analysis` is a secondary capability and should not drive default product or architecture decisions.
- Do not reintroduce backend-owned landing or sample-browser flows unless that is an intentional product change.
- Do not broaden the default experience into a generic book-summary product without an explicit product decision.

## Documentation Rule
- If the primary product journey, page responsibilities, or interaction model changes, update this file in the same task.
- If the same change also affects public routes or payloads, update `docs/api-contract.md` and `docs/api-integration.md` in the same task.
