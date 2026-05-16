# Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0

## PR title

Slice 4A: Supplemental Retrieval Intent and Context Assembly Contract

## Implementation slice

Slice 4A is the first small sub-slice of Slice 4 / Retrieval & Utilization Instrumentation.

This brief scopes the future implementation PR to supplemental retrieval intent and result-boundary metadata in `read_context.py`, plus prompt-facing context assembly contract visibility in `state_projection.py`. It is not a new retriever, not a broad RAG pipeline, and not a full utilization trace implementation.

## Design sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计6-Detour : Look-back : Active Recall Policy Design v0.md`
- `C设计7-Memory Retrieval & Utilization Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
- `Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
- `Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`
- `Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
- `E实施-progress-ledger.md` reviewer constraints

## Current code facts

- `read_context.py` owns `resolve_context_request(...)` and `merge_supplemental_contexts(...)`.
- `look_back` currently resolves explicit source references into source excerpts, source refs, and flattened refs.
- `active_recall` currently resolves settled memory state and visible trace into concepts, threads, recent reactions, and flattened refs.
- `merge_supplemental_contexts(...)` preserves `refs`, `source_refs`, `concepts`, `threads`, `reactions`, `reflective_items`, and `excerpts`.
- `state_projection.build_read_prompt_packet(...)` currently projects supplemental `excerpts`, `source_refs`, and `refs` into `selective_carry`.
- Active-recall `concepts`, `threads`, and `reactions` therefore reach the Read prompt mainly through flattened `supporting_refs`, not as full supplemental objects.
- `observability.py` records supplemental ref ids, satisfaction, and supplemental steps, but it does not record explicit retrieval-intent or retrieval-result-boundary metadata.
- `reaction_records` in active recall are visible trace, not semantic memory.
- A read-only check found `tests/test_attentional_v2_phase_b.py` is currently stale around legacy `anchor_bank` expectations, so Slice 4A implementation should prefer new focused tests or scoped updates instead of relying on that file as-is.

## Files to change

Future implementation PR may change:

- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/tests/test_attentional_v2_read_context.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`

## Files explicitly not changing

Future implementation PR must not change:

- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- durable memory state
- navigation / detour policy
- public API
- frontend
- eval runners
- vector DB / graph DB / Memory OS
- retriever agent
- broad RAG pipeline

## Planned deltas

- Add compact supplemental retrieval metadata such as:
  - `retrieval_intent`
  - `result_boundary`
  - `result_groups`
  - `retrieval_events`
- Use `retrieval_intent="source_calibration"` for `look_back`.
- Use `retrieval_intent="memory_recovery"` for `active_recall`.
- Keep `look_back` bounded to source excerpts, source refs, and flattened refs.
- Keep `active_recall` bounded to settled memory refs and visible trace refs.
- Preserve existing `excerpts`, `source_refs`, and `refs` projection into `selective_carry`.
- Add prompt-packet metadata that explicitly states which supplemental result groups exist and whether full active-recall objects are forwarded.
- Do not project full active-recall `concepts`, `threads`, or `reactions` into the Read prompt packet in Slice 4A.
- Preserve or mirror Slice 3A boundary semantics where relevant:
  - lineage/source-ref-warning status remains metadata, not invalidation;
  - reaction-derived supplemental material remains visible trace, not semantic memory;
  - `knowledge_activations` remain out of Slice 4A projection and are not source truth.
- Do not implement full utilization trace in Slice 4A.

## Boundary policy

- `look_back` remains source calibration over source excerpts and source refs.
- `active_recall` remains memory recovery over settled memory state and visible trace refs.
- `reaction_records` remain visible trace, not semantic memory.
- `lineage_only` means not current support, not deletion, invalidation, or uselessness.
- `source_ref_missing` remains a projection warning, not invalidation.
- Retrieval-intent metadata is contract visibility, not proof that retrieval quality is sufficient.

## Engineering tests

Future implementation PR should add or update focused tests for:

- `look_back` returning `retrieval_intent="source_calibration"` and source-boundary metadata;
- `active_recall` returning `retrieval_intent="memory_recovery"` and memory / visible-trace boundary metadata;
- active-recall reactions carrying visible-trace boundary metadata and not being treated as semantic memory;
- `merge_supplemental_contexts(...)` preserving compact retrieval events and result-boundary metadata;
- `build_read_prompt_packet(...)` preserving existing `selective_carry` fields while adding compact retrieval-context contract metadata;
- prompt-packet metadata making explicit that full active-recall concepts / threads / reactions are not forwarded in Slice 4A;
- `knowledge_activations` not being projected by Slice 4A;
- stale Phase B tests not being used as the critical Slice 4A contract unless they are first scoped and updated.

Future PR test command:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_read_context.py tests/test_attentional_v2_state_projection.py -q
```

## Contract / audit checks

- Preserve SourceRef-first behavior.
- Do not treat `reaction_records` as semantic memory.
- Do not treat `knowledge_activations` as source truth.
- Do not route audit dumps into prompts.
- Do not change durable memory state.
- Do not change navigation or detour policy.
- Keep all additions compact and mechanism-private.
- Do not run full AI Evaluation.

## Non-goals

- No new retriever.
- No broad RAG pipeline.
- No full utilization trace.
- No prompt text change.
- No runner change.
- No `state_ops.py` change.
- No durable memory-state change.
- No navigation / detour policy change.
- No slow-cycle work.
- No public API change.
- No frontend change.
- No eval runner change.
- No vector DB / graph DB / Memory OS / retriever agent.
- No full AI Evaluation.

## Risks

- Retrieval-intent metadata could be mistaken for retrieval-quality proof.
- Keeping full active-recall objects out of the prompt packet preserves the current boundedness but may leave some product value unrealized until a later slice.
- Forwarding too much memory context later could add prompt noise or blur source calibration vs memory recovery.
- Stale Phase B tests could obscure the current Slice 4A contract if used without scoped repair.
- Duplicating Slice 3A marker logic in the retrieval path could drift; Slice 4A should use compact mirrored semantics only where needed.

## Rollback plan

Revert the future Slice 4A PR. Additive retrieval metadata in supplemental context and prompt-facing packets requires no migration and should return behavior to the Slice 3B state.

## Open questions

None blocking.

Slice 4A explicitly chooses no prompt change, no runner change, no full active-recall object projection, and no full utilization trace.

## Go / no-go recommendation

Go for human review of this brief.

No-go for implementation until the Slice 4A brief is accepted.
