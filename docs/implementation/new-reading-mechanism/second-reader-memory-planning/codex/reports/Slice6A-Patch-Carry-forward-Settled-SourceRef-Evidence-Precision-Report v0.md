# Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0

## Patch title / branch

Slice 6A Patch: Carry-forward Settled SourceRef Evidence Precision

Branch: `main`

## Slice

Slice 6A patch / Slow-cycle Safety.

This patch refines the accepted Slice 6A audit envelope evidence precision. It does not start the next implementation slice.

## Summary of actual changes

- Tightened `cross_chapter_carry_forward` audit envelopes with `settlement_decision="carried"` so SourceRef evidence now reflects the settled carried item evidence shape.
- For carried items that reuse an existing post-cooling `active_attention.item_id`, audit evidence is derived from existing item SourceRefs plus carry-forward candidate SourceRefs.
- Reused the same `dedupe_source_refs(...)` semantics used by `apply_cross_chapter_carry_forward(...)`.
- Kept the change audit-only. The merged refs are not copied into audit rows and durable carry-forward behavior is unchanged.
- Preserved compact audit evidence fields:
  - `source_ref_count`
  - `source_ref_resolution_statuses`
  - `promotion_evidence_status`

## Files changed

- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/tests/test_attentional_v2_slow_cycle.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design contracts addressed

- Candidate existence is not durable truth.
- Carry-forward audit evidence reflects settled carried item support, not only the raw candidate payload.
- Existing active-attention SourceRefs remain preserved by durable carry-forward behavior.
- Ambiguous SourceRef resolution remains `not_assessed`; this patch improves evidence source selection, not evidence certainty.
- No full durable store payloads, source windows, prompt packets, or audit dumps are copied into audit rows.

## Deviations from accepted patch scope

None.

## Tests added or updated

- Updated `reading-companion-backend/tests/test_attentional_v2_slow_cycle.py` with a sparse carried-candidate case where the existing active item has SourceRefs and the carry-forward candidate omits them.

## Commands run

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_slow_cycle.py tests/test_attentional_v2_scaffold.py -q
```

## Test results

```text
26 passed, 6 warnings
```

Warnings were dependency deprecation warnings from import-time packages.

## Boundary checks

- Slow-cycle behavior did not change.
- Prompt text and prompt versions did not change.
- `runner.py` was not changed.
- `read_context.py`, `state_projection.py`, and `skills/source_skills.py` were not changed.
- Durable memory state, public API, frontend, and eval runners were not changed.
- Full AI Evaluation was not run.

## Known gaps

- This patch does not add continuation-capsule delta audit.
- This patch does not expand slow-cycle behavior or create a new slow-cycle settlement policy.
- The next slice has not started.

## Next recommended step

Human reviewer should review and accept this Slice 6A patch report before any next implementation slice begins.
