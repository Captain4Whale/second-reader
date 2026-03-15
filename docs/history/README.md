# Engineering History

Purpose: define where the project keeps non-authoritative history about design evolution, key decisions, and rejected alternatives.
Use when: you need to understand why the system evolved this way, which alternatives were rejected, or which context would be hard to reconstruct later from code alone.
Not for: source-of-truth product behavior, public API authority, runtime semantics, or interview-ready summaries.
Update when: the history doc set changes, its retention rules change, or a major decision or evolution step would otherwise be lost.

This directory is for historical context, not current authority. Facts about the current system still belong in the stable docs under `docs/`.

## What Belongs Here
- `decision-log.md`: durable decision history, including rejected alternatives, inflection points, and why the chosen path won

## What Does Not Belong Here
- restatements of current behavior that are already captured in stable docs
- implementation details that can be recovered directly from code
- interview scripts, one-page summaries, or recruiting-oriented packaging
- raw evaluation reports and experiment outputs that already live in archive/reference directories

## Writing Rules
- Record evolution and rationale, not just the final state.
- Prefer entries that answer "why did we end up here?" over entries that merely describe what exists now.
- If a point can be reconstructed later from stable docs and code with low effort, do not store it here.
- Link back to stable docs, code, or archived reports when they are the factual basis for the history entry.

## Maintenance Defaults
- Default engineering tasks do not need to load this directory.
- Update it only when a major decision, reversal, or design inflection point would otherwise be forgotten.
- Routine bugfixes, refactors, and contract-only updates do not belong here unless they mark a real change in direction.
