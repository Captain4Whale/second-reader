# Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0

## PR title

Slice 4B: Retrieval Utilization Trace and Read-audit Evidence

## Implementation slice

Slice 4B, a small reversible sub-slice of Slice 4 / Retrieval & Utilization Instrumentation.

The future PR focuses on compact `read_audit.jsonl` evidence for supplemental retrieval context. It is not a retrieval behavior change, not a new retriever, and not a full utilization trace.

## Design sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计6-Detour : Look-back : Active Recall Policy Design v0.md`
- `C设计7-Memory Retrieval & Utilization Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
- `Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
- `Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- `E实施-progress-ledger.md`

## Current code facts

- `observability.record_read(...)` already accepts `context_request`, `supplemental_context`, `supplemental_satisfied`, `supplemental_steps`, and `read_result`.
- `record_read(...)` currently writes `context_request`, `supplemental_ref_ids`, `supplemental_satisfied`, and `supplemental_steps`, but does not write explicit retrieval intent, boundary, result group, or forwarding metadata.
- `state_projection.build_read_prompt_packet(...)` already derives prompt-facing `selective_carry.retrieval_context` with:
  - `retrieval_intent`
  - `result_boundary`
  - `result_groups`
  - `retrieval_events`
  - `forwarded_result_groups`
  - `not_forwarded_result_groups`
  - `active_recall_full_objects_forwarded=false`
- Current `runner.py` call path passes `supplemental_context=None` to `read_unit(...)` and does not currently run a supplemental retrieval loop for the main read path.
- Adding a retrieval loop, changing runner behavior, or forwarding full active-recall objects is out of Slice 4B.

## Files to change

Future implementation PR may change:

- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`, only to extract or reuse existing supplemental selective-carry / retrieval-context logic without changing prompt packet behavior
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`, only to preserve helper and prompt-packet compatibility

## Files explicitly not changing

- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- durable memory state
- navigation / detour policy
- public API
- frontend
- eval runners

## Planned deltas

- Add compact `read_audit` retrieval evidence only when `supplemental_context` contains retrieval metadata.
- Reuse prompt-facing forwarding logic from `state_projection.py` instead of duplicating group-forwarding rules in `observability.py`.
- Add a mechanism-private `supplemental_retrieval` audit block with:
  - `retrieval_intent`
  - `result_boundary`
  - `result_groups`
  - `retrieval_events`
  - `forwarded_result_groups`
  - `not_forwarded_result_groups`
  - `supplemental_refs_returned`
  - `supplemental_refs_forwarded_to_prompt`
  - `source_refs_available`
  - `memory_refs_available`
  - `visible_trace_refs_available`
  - `utilization_observed=false`
  - `utilization_basis="not_claimed_by_read_output"`
- Preserve existing `read_audit` fields:
  - `context_request`
  - `supplemental_ref_ids`
  - `supplemental_satisfied`
  - `supplemental_steps`
- Do not claim actual model utilization from retrieval availability.
- Do not infer utilization from `reading_impression`, surfaced reactions, memory ops, or source-ref overlap.
- Preserve:
  - `look_back=source_calibration`
  - `active_recall=memory_recovery`
  - reaction refs as visible trace, not semantic memory
  - precise result groups from the Slice 4A patch

## Engineering tests

Future PR should run:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_state_projection.py -q
```

Future PR should add or update tests proving:

- `record_read(...)` writes compact retrieval audit metadata for `look_back`.
- `record_read(...)` writes compact retrieval audit metadata for sparse and mixed `active_recall`.
- visible-trace reaction refs remain visible trace and are not counted as semantic memory.
- `utilization_observed` is `false` and `utilization_basis` is `not_claimed_by_read_output`.
- old read-audit fields remain present.
- prompt-facing forwarding metadata remains unchanged by any helper extraction.

## Contract / audit checks

- SourceRef-first behavior remains preserved.
- `look_back` remains source calibration, not memory recovery.
- `active_recall` remains memory recovery, not source calibration.
- reaction refs remain visible trace, not semantic memory.
- `knowledge_activations` are not projected or treated as source truth.
- retrieval metadata is contract / audit visibility, not product quality proof.
- retrieval availability is not actual model utilization.
- audit dumps are not routed into prompts.
- full retrieval utilization trace remains deferred.
- full AI Evaluation is not run.

## Non-goals

- No retrieval behavior change.
- No prompt text change.
- No `runner.py` behavior change.
- No full utilization trace.
- No new retriever.
- No vector DB / graph DB / Memory OS / retriever agent.
- No full active-recall object forwarding.
- No durable memory state change.
- No navigation / detour policy change.
- No public API / frontend / eval runner change.
- No full AI Evaluation.

## Risks

- Audit metadata may be mistaken for proof that retrieved material influenced the model output.
- Reusing prompt-facing forwarding logic from `state_projection.py` must avoid changing prompt packet behavior.
- Current runner does not yet pass real supplemental context in the main read path, so this slice mostly creates audit substrate for future retrieval-bearing paths and tests.
- Too much audit detail could bloat `read_audit.jsonl`; the future PR should keep the block compact.

## Rollback plan

Revert the future Slice 4B PR. The planned changes are additive mechanism-private audit metadata and tests, with no migration requirement.

## Open questions

None blocking.

Default decisions for Slice 4B:

- No prompt change.
- No `runner.py` change.
- No retrieval behavior change.
- No actual utilization claim.
- No full utilization trace.

## Go / no-go recommendation

Go for human review of this brief.

No-go for implementation until the Slice 4B Pre-implementation Brief is accepted.
