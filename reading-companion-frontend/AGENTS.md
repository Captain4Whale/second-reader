# Frontend Agent Guide

## Scope
- This directory contains the Reading Companion web client.
- Use `/Users/baiweijiang/Documents/Projects/reading-companion/docs/product-interaction-model.md` for product flow and `/Users/baiweijiang/Documents/Projects/reading-companion/docs/api-contract.md` for the public contract. This file is for frontend-local constraints.

## Local Rules
- Keep route definitions centralized in `src/app/routes.tsx`.
- Keep raw API requests inside `src/app/lib/api.ts`.
- Do not spread ad-hoc `fetch()` calls across page components.
- Preserve the useful Figma Make-generated structure unless a clear maintenance problem justifies cleanup.
- Prefer preserving the existing visual language unless a task explicitly asks for redesign.
- Keep compatibility routes if backend-returned paths or older links still rely on them.

## Integration Constraints
- Do not reintroduce mock data as the primary source of truth.
- Do not change backend contract names on the frontend side without checking the backend.
- Keep route normalization aligned with the canonical frontend routes returned by the backend.
- Avoid large component framework rewrites unless the task explicitly calls for one.

## Language Governance
- Follow `/Users/baiweijiang/Documents/Projects/reading-companion/docs/language-governance.md`.
- Core UI text must come from the locale layer, not ad-hoc string literals in components.
- Key terms must come from the product lexicon.
- Key sentence-level UI copy must come from the controlled copy catalog.
- Only content values may remain in the book/content language; control and status text must follow `appLocale`.
