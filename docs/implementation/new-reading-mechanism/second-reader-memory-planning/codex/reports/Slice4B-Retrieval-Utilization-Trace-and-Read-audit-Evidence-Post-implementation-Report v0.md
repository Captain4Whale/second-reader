# Slice 4B: Retrieval Utilization Trace and Read-audit Evidence - Post-implementation Report v0

## PR Title / Branch

PR title / branch:
- `Slice 4B: Retrieval Utilization Trace and Read-audit Evidence`
- Branch: `main`

Slice:
- Slice 4B, a small Slice 4 / Retrieval & Utilization Instrumentation sub-slice.

## Summary of Actual Changes

Slice 4B adds compact, mechanism-private `read_audit.jsonl` retrieval evidence when `supplemental_context` already contains retrieval metadata. It does not change retrieval behavior, prompt text, runner flow, durable memory state, public API, frontend, eval runners, or full utilization tracing.

Runtime changes:
- Extracted `build_supplemental_selective_carry(...)` in `state_projection.py` so prompt packet assembly and read-audit evidence use the same forwarding logic.
- Added `supplemental_retrieval` in `observability.record_read(...)` only when the supplemental context produces retrieval metadata.
- Kept empty/non-retrieval supplemental contexts from writing an empty `supplemental_retrieval` block.
- Recorded compact returned/forwarded ref summaries and availability summaries as `{count, ref_ids}` objects.
- Kept `utilization_observed=false` and `utilization_basis="not_claimed_by_read_output"`.

Important boundary:
- Current runner main read path still passes `supplemental_context=None`.
- This PR does not create a supplemental retrieval loop.
- Retrieval availability is not claimed as actual model utilization.
- Full retrieval utilization trace remains deferred.

## Files Changed

Runtime:
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/observability.py`

Tests:
- `reading-companion-backend/tests/test_attentional_v2_observability.py`
- `reading-companion-backend/tests/test_attentional_v2_state_projection.py`

Docs / process:
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

Files intentionally not changed:
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- durable memory state
- navigation / detour policy
- public API
- frontend
- eval runners

## Design Contracts Addressed

- `read_audit.jsonl` gets retrieval evidence only when retrieval metadata exists.
- No empty `supplemental_retrieval` block is written for missing or non-retrieval supplemental context.
- `look_back` remains source calibration.
- `active_recall` remains memory recovery.
- Reaction refs remain visible trace, not semantic memory.
- `knowledge_activations` remain excluded and are not treated as source truth.
- Prompt-facing forwarding logic is shared through `build_supplemental_selective_carry(...)`.
- Full active-recall concepts, threads, and reactions are not forwarded into the Read prompt packet.
- Existing `read_audit` fields remain present:
  - `context_request`
  - `supplemental_ref_ids`
  - `supplemental_satisfied`
  - `supplemental_steps`
  - memory uptake fields from Slice 1 / 2A / 2B

## Deviations from Accepted Brief

None.

The implementation stayed within the accepted brief and reviewer constraints:
- no retrieval behavior change;
- no `runner.py` change;
- no prompt text/version change;
- no `state_ops.py` / `slow_cycle.py` change;
- no public API / frontend / eval runner change;
- no full utilization trace;
- no full AI Evaluation.

## Tests Added or Updated

Updated `test_attentional_v2_observability.py` to cover:
- no `supplemental_retrieval` block when no retrieval metadata exists;
- `look_back` source-calibration `supplemental_retrieval` evidence;
- sparse `active_recall` memory-recovery evidence with precise result groups;
- mixed supplemental bundle evidence with source, memory, and visible-trace refs;
- visible-trace reaction refs not counted as semantic memory;
- `utilization_observed=false` and `utilization_basis="not_claimed_by_read_output"`;
- old read-audit fields still present.

Updated `test_attentional_v2_state_projection.py` to cover:
- prompt-facing `retrieval_context` behavior remains unchanged after helper extraction;
- `build_read_prompt_packet(...)` and `build_supplemental_selective_carry(...)` share the same selective-carry output for retrieval contexts;
- full active-recall concepts, threads, reactions, and `knowledge_activations` are not forwarded.

## Commands Run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_observability.py tests/test_attentional_v2_state_projection.py -q
```

Result:
- `12 passed, 6 warnings`

Additional validation:

```bash
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2/runner.py reading-companion-backend/src/attentional_v2/prompts.py reading-companion-backend/src/attentional_v2/state_ops.py reading-companion-backend/src/attentional_v2/slow_cycle.py reading-companion-frontend reading-companion-backend/eval
```

Result:
- `registry-json-ok`
- `git diff --check` passed
- forbidden-file diff check returned no changed files

## Contract / Audit Evidence Produced

`read_audit.jsonl` can now include a compact `supplemental_retrieval` block with:
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

This is availability and forwarding evidence only. It is not actual model-utilization proof.

## Backward Compatibility Notes

- Additive mechanism-private audit field only.
- No public API migration required.
- No prompt text/version change.
- No runtime artifact schema version change.
- Existing read-audit fields are preserved.
- If no retrieval metadata exists, `supplemental_retrieval` is omitted.

## Risk / Rollback Notes

Rollback:
- Revert this PR. The additive audit field requires no migration.

Risks:
- `supplemental_retrieval` could be misread as retrieval quality or model utilization proof; the block explicitly records `utilization_observed=false`.
- The current main runner path still does not pass supplemental context, so the new block is available for supplemental flows/tests but is not yet produced by the main read loop.
- Full utilization trace and Callback / FVI evaluation substrate remain future work.

## Known Gaps

- Main read runner still passes `supplemental_context=None`.
- No supplemental retrieval loop is introduced.
- Actual model utilization is not observed or claimed.
- `read_audit` retrieval evidence is compact availability/forwarding evidence, not full utilization trace.
- Full AI Evaluation was not run.
- Stable mechanism docs were not updated because this is mechanism-private audit instrumentation pending report review.

## Next Recommended Step

Human review of this Slice 4B Post-implementation Report.

Do not start the next implementation slice until this report is accepted or patched.
