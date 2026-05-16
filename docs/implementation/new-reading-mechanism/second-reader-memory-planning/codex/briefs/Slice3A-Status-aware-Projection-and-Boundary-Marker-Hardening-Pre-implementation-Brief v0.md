# Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0

## PR title

Slice 3A: Status-aware Projection and Boundary Marker Hardening

## Implementation slice

Slice 3A is the first small sub-slice of Slice 3 / Memory Lifecycle and Projection Hardening.

This brief scopes the future implementation PR to prompt-facing projection markers in `state_projection.py`. It does not change durable lifecycle mutation, settlement behavior, or state persistence semantics.

## Design sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计1-Memory Ontology Design v0.md`
- `C设计5-Memory Management & Evolution Design v0(patched).md`
- `C设计6-Detour : Look-back : Active Recall Policy Design v0.md`
- `C设计7-Memory Retrieval & Utilization Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
- `Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
- `E实施-progress-ledger.md` reviewer constraints

## Current code facts

- `state_projection.py` builds `active_attention_digest`, `concept_digest`, `thread_digest`, recent reactions, `source_ref_digest`, carry-forward context, navigation context, and read prompt packets.
- Active attention projection already includes `status`.
- Concept sorting reads status, but the concept digest currently omits status.
- Concept and thread digests include source refs and sample quotes, but do not carry explicit projection-role markers.
- Recent reactions are projected as continuity context, but do not carry `visible_trace_support`.
- `read_context.py` only re-exports `build_carry_forward_context`, so it should not change in Slice 3A.

## Files to change

Future implementation PR may change:

- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`

## Files explicitly not changing

Future implementation PR must not change:

- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- projection persistence outside `state_projection.py`
- retrieval utilization
- planning trace
- slow-cycle
- public API
- frontend
- eval runners

## Planned deltas

- Add compact additive projection markers to prompt-facing digest entries:
  - `projection_role`
  - `support_status`
  - `current_support`
  - `lineage_only`
  - `projection_warning`
- Use `visible_trace_support` only for reaction-derived entries.
- Keep all markers mechanism-private and prompt-packet scoped.
- Preserve current runtime behavior: do not filter, reject, mutate, settle, or persist state differently.

## Marker policy

Current / source-backed memory projection:

- `projection_role`: `current_support`
- `support_status`: `source_backed`
- `current_support`: `true`
- `lineage_only`: `false`
- `projection_warning`: `""`

Missing source refs:

- `support_status`: `source_ref_missing`
- `projection_warning`: `source_ref_missing`

Explicit stale / closed statuses such as `closed`, `resolved`, `superseded`, `invalidated`, `rejected`, `dropped`, or `retired`:

- `projection_role`: `lineage_only`
- `current_support`: `false`
- `lineage_only`: `true`
- `projection_warning`: `lineage_only_not_current_support`

## Reaction boundary

Recent reaction projection should receive:

- `projection_role`: `visible_trace`
- `support_status`: `visible_trace`
- `visible_trace_support`: `true`
- `current_support`: `false`
- `projection_warning`: `visible_trace_not_semantic_memory`

Reaction records remain visible trace, not semantic memory.

## Knowledge boundary

Slice 3A must not project `knowledge_activations`.

Any future knowledge projection must use warrant / context markers and must not become source truth.

## Engineering tests

Future implementation PR should add or update `reading-companion-backend/tests/test_attentional_v2_state_projection.py` to verify:

- current-support markers for source-backed current projection entries;
- lineage-only markers for stale / closed statuses;
- `source_ref_missing` warnings where source refs are absent;
- reaction visible-trace markers;
- marker preservation through `build_read_prompt_packet`.

Future PR test command:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_state_projection.py -q
```

## Contract / audit checks

- Preserve SourceRef-first behavior.
- Keep all new fields additive and mechanism-private.
- Do not filter, reject, mutate, or settle state differently.
- Do not route audit dumps into prompts.
- Do not treat reaction records as semantic memory.
- Do not treat knowledge activations as source truth.
- Do not run full AI Evaluation.

## Non-goals

- No `state_ops.py` lifecycle change.
- No strict validation.
- No prompt change.
- No `read_context.py` change.
- No retrieval utilization work.
- No planning trace work.
- No slow-cycle work.
- No public API change.
- No frontend change.
- No eval runner change.
- No vector DB / graph DB / Memory OS / manager agent.

## Risks

- Additive markers could be mistaken for authoritative lifecycle mutation unless naming and report language stay explicit.
- Stale-status vocabulary may be incomplete and should remain conservative.
- Prompt packet growth could add noise if markers are too verbose.

## Rollback plan

Revert the future Slice 3A PR. Additive prompt-packet fields require no migration and do not alter durable state.

## Open questions

None blocking.

Slice 3A explicitly chooses no prompt change and no `read_context.py` change.

## Go / no-go recommendation

Go for human review of this brief.

No-go for implementation until the Slice 3A brief is accepted.
