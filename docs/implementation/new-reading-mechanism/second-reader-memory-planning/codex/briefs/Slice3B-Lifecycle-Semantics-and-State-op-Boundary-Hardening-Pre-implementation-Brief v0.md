# Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0

## PR title

Slice 3B: Lifecycle Semantics and State-op Boundary Hardening

## Implementation slice

Slice 3B is a small sub-slice of Slice 3 / Memory Lifecycle and Projection Hardening.

This brief scopes the future implementation PR to existing lifecycle semantics in `state_ops.py` and targeted tests. It builds on Slice 3A projection markers, but it does not change durable lifecycle mutation unless a narrow helper-level clarification is proven necessary by tests.

## Design sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计1-Memory Ontology Design v0.md`
- `C设计3-Memory Formation & Settlement Design v0.md`
- `C设计5-Memory Management & Evolution Design v0(patched).md`
- `C设计7-Memory Retrieval & Utilization Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
- `Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
- `E实施-progress-ledger.md` reviewer constraints

## Current code facts

- `apply_active_attention_operations(...)` handles `cool` by marking an active item as `cooling` when the payload does not provide a status; it does not delete or invalidate the item.
- `apply_active_attention_operations(...)` handles `close` and `resolve` by marking existing or merged items as `closed` / `resolved` when the payload does not provide a status; it does not delete the item.
- `apply_active_attention_operations(...)` handles `drop` by removing the matching active item.
- `apply_concept_registry_operations(...)` and `apply_thread_trace_operations(...)` are store-specific and ignore operations whose `target_store` does not match their store.
- Concept and thread helpers normalize `close` to `resolve`.
- Concept and thread helpers handle `drop` by removing the matching store-specific entry.
- `append_reaction_record(...)` appends reaction records in occurrence order.
- `supersede_reflective_item(...)` marks one reflective item as `superseded` and records `superseded_by_item_id` without mutating the item's statement.
- Slice 3A added prompt-facing projection markers in `state_projection.py`; Slice 3B should preserve or test those markers, not alter their runtime meaning.

## Files to change

Future implementation PR may change:

- `reading-companion-backend/src/attentional_v2/state_ops.py`, only if tests reveal a narrow helper-level clarification is necessary
- `reading-companion-backend/tests/test_attentional_v2_state_ops.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`, only to preserve or test Slice 3A marker compatibility

## Files explicitly not changing

Future implementation PR must not change:

- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- retrieval utilization
- planning trace
- public API
- frontend
- eval runners
- schema version
- durable persistence format

## Planned deltas

- Prefer tests and contract clarification before behavior changes.
- Add or strengthen targeted tests that lock the existing lifecycle boundary:
  - cooling is not invalidation;
  - resolve is not deletion;
  - close / resolve retain items as lineage-capable state;
  - supersede is not destructive overwrite;
  - reaction records remain append-only visible trace;
  - concept and thread close / resolve / drop behavior remains deterministic and store-specific.
- Preserve Slice 3A projection markers and their meanings:
  - `lineage_only` means not current support, not deletion, invalidation, or uselessness;
  - `source_ref_missing` remains a projection warning, not invalidation.
- Make only minimal helper-level clarification in `state_ops.py` if current tests expose ambiguity that cannot be locked by tests alone.
- Do not introduce strict validation, schema migration, prompt changes, knowledge projection, or runtime behavior broadening.

## Engineering tests

Future implementation PR should add or update targeted tests for:

- active-attention `cool` preserving the item, source refs, and non-deletion semantics while setting or preserving the intended status;
- active-attention `resolve` / `close` preserving the item and source refs while marking lifecycle status;
- active-attention `drop` remaining the explicit deletion path;
- concept and thread `close` / `resolve` / `drop` behavior staying deterministic and store-specific;
- `append_reaction_record(...)` remaining append-only and visible-trace oriented;
- `supersede_reflective_item(...)` preserving the original statement while marking `superseded`;
- Slice 3A projection marker compatibility for closed / resolved / superseded state, if needed.

Future PR test command:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_state_ops.py tests/test_attentional_v2_state_projection.py -q
```

## Contract / audit checks

- Cooling is not invalidation.
- Resolve is not deletion.
- Supersede is not destructive overwrite.
- Reaction records remain append-only visible trace, not semantic memory.
- Closed / resolved / superseded entries remain available as lineage where projected, not treated as useless or erased.
- `source_ref_missing` remains a projection warning, not invalidation.
- `knowledge_activations` are not projected in Slice 3B.
- Preserve SourceRef-first behavior.
- Do not route audit dumps into prompts.
- Do not run full AI Evaluation.

## Non-goals

- No `state_ops.py` rewrite.
- No broad durable lifecycle behavior change.
- No schema migration.
- No prompt change.
- No strict validation.
- No retrieval utilization work.
- No planning trace work.
- No slow-cycle work.
- No public API change.
- No frontend change.
- No eval runner change.
- No vector DB / graph DB / Memory OS / manager agent.
- No full AI Evaluation.

## Risks

- Existing lifecycle semantics may be weaker than the desired contract; the future PR should report that fact rather than silently widening behavior.
- Over-hardening could accidentally redefine deletion, resolution, or lineage semantics.
- Projection-marker compatibility tests could tempt runtime projection edits; Slice 3B should avoid changing `state_projection.py` unless a narrow test-only preservation check is sufficient.
- Store-specific lifecycle tests could be misread as a full `state_ops.py` behavior redesign; this slice is intentionally small and reversible.

## Rollback plan

Revert the future Slice 3B PR. Test-only changes and narrow helper-level clarifications require no migration and should return behavior to the Slice 3A state.

## Open questions

None blocking.

Slice 3B explicitly chooses no prompt change, no schema migration, no knowledge projection, and no durable lifecycle semantic change unless narrowly proven necessary by tests.

## Go / no-go recommendation

Go for human review of this brief.

No-go for implementation until the Slice 3B brief is accepted.
