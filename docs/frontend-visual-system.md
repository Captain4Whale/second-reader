# Frontend Visual System

Purpose: define the stable typography system, reader-scale boundaries, and minimal visual tokens for the frontend.
Use when: changing page typography, card and shell hierarchy, reader text scaling, or core frontend visual tokens.
Not for: product flow, API behavior, backend content generation, or temporary visual experiments.
Update when: typography roles, reader-scale behavior, token usage rules, or documented exceptions change.

## Design Principles
- Prefer a small, reusable typography ramp over page-specific font-size decisions.
- Keep hierarchy consistent across the core application surfaces even when page layouts differ.
- Preserve the product's reading-first feel by separating application chrome from reading content.
- Allow documented exceptions when a surface has a distinct product role, rather than forcing every page into one visual pattern.

## Coverage
- This document governs the core application surfaces:
  - `layout`
  - `bookshelf`
  - `book overview`
  - `chapter read`
  - `global marks`
  - upload surfaces
- The landing page marketing/promo area is a documented exception in v1:
  - it may keep its tuned promotional typography
  - it should not be used as the default source of truth for core application type choices

## Text Classes
### 1. Brand / Marketing
- Purpose: brand lockups, landing slogans, promotional framing.
- Default owner: landing and brand surfaces.
- Rule: may use a more expressive scale than the core application.

### 2. App Shell
- Purpose: top navigation, brand lockup inside the app shell, persistent chrome.
- Rule: should use stable shell-level typography, not page-local overrides.

### 3. Page Hero / Book Identity
- Purpose: page titles, book titles, chapter/workspace hero labels.
- Rule: should carry the main serif hierarchy for the page.

### 4. Section / Card Heading
- Purpose: card titles, section headings, modal titles, grouped content titles.
- Rule: use the shared heading ramp before inventing a custom title size.

### 5. Body / Supporting / Meta / Caption
- Purpose: descriptions, supporting text, metadata, secondary labels, compact summaries.
- Rule: default to shared body/meta/caption steps and only deviate when the exception is documented.

### 6. Controls / Forms / Tabs / Status / Chips
- Purpose: buttons, links that behave like controls, tabs, chips, status words, compact UI labels.
- Rule: these are UI chrome and must stay on fixed application typography.

### 7. Reader Content
- Purpose: reaction text, quotes, inline supporting reading text, source-book text.
- Rule: this is the only class that may follow the shared reader font-scale control.

## Typography Ramp
The theme token source of truth is `reading-companion-frontend/src/styles/theme.css`.

### UI Typography
- `--rc-type-shell-brand`: app-shell brand lockup
- `--rc-type-shell-tagline`: app-shell supporting tagline
- `--rc-type-page-title`: page-level title
- `--rc-type-card-title`: major card title
- `--rc-type-panel-title`: panel/modal/section title
- `--rc-type-body`: body/supporting copy
- `--rc-type-meta`: metadata and control-adjacent support text
- `--rc-type-caption`: caption-sized secondary text
- `--rc-type-chip`: chips, badges, compact labels
- `--rc-type-control`: standard button/link control text
- `--rc-type-control-compact`: compact shell controls
- `--rc-type-action-sm`: small inline actions
- `--rc-type-eyebrow`: section eyebrow labels

### Reader Typography
- `--rc-type-reader-body`: main reader/result prose
- `--rc-type-reader-quote`: reader quotes and anchored excerpts
- `--rc-type-reader-meta`: reader-adjacent supporting metadata
- `--rc-type-reader-label`: reader labels and section references
- `--rc-type-reader-chip`: compact reader chips/buttons
- `--rc-type-reader-caption`: dense reader captions and tiny provenance labels

## Reader Scale Policy
- The reader scale is shared across:
  - reaction body text
  - reaction quotes and anchored excerpts
  - source-book text in the EPUB reader
  - reading-adjacent supporting text that behaves like content, not controls
- The reader scale must not affect:
  - tabs
  - topbars
  - tool buttons
  - settings popovers
  - badges and chips that function as controls
  - page navigation
  - structural chrome such as chapter drawers and workspace framing labels
- Implementation rule:
  - use reader typography helpers only for `reader content`
  - use UI typography helpers for all `reader chrome`

## Minimal Visual Tokens
### Colors
- Use the `warm-*` and `amber-*` palette as the default application palette.
- Prefer semantic aliases like surface/background/border usage over page-specific hex values.

### Spacing
- Use a compact spacing ladder for core surfaces:
  - `--rc-space-1`
  - `--rc-space-2`
  - `--rc-space-3`
  - `--rc-space-4`
  - `--rc-space-5`
- Prefer repeated spacing tokens over one-off padding values for shared shells and cards.

### Radius
- `--rc-radius-card`: standard card radius
- `--rc-radius-panel`: larger panel/modal radius

### Border and Shadow
- `--rc-border-subtle` and `--rc-border-strong` are the default border strengths for surfaces.
- `--rc-shadow-surface` and `--rc-shadow-surface-strong` are the default core application surface shadows.

## Usage Rules
- Core application surfaces should prefer the shared helpers in `src/app/lib/visual-system.ts`.
- Do not introduce new naked inline `fontSize` values for a role that already has a visual-system token.
- If a component needs a new typography role, add it to the token layer and document it here before spreading the size through multiple pages.
- If a surface intentionally breaks the ramp, record it as a named exception instead of leaving it implicit.

## Current Exceptions
- Landing marketing typography is intentionally exempt from the core application ramp in v1.
- EPUB-rendered source text remains governed by reader-scale behavior and EPUB theme constraints rather than the core application serif/sans ramp.
