# Slice 6A: Slow-cycle Candidate and Settlement Audit Envelope Foundations — Post-implementation Report v0

## Summary

Slice 6A adds compact mechanism-private slow-cycle audit envelopes for existing Phase 6 chapter-end slow-cycle paths. The new audit stream distinguishes candidate evidence from settled durable outcomes without changing slow-cycle behavior.

New artifact:
- `_mechanisms/attentional_v2/runtime/slow_cycle_audit.jsonl`

This artifact is mechanism-private audit metadata. Candidate existence is not durable truth, promotion candidate existence is not promotion success, and audit envelope rows are not product-quality proof.

## Scope Implemented

Runtime/code changes:
- Added `SlowCycleAuditEnvelope` as an optional mechanism-private TypedDict.
- Added `slow_cycle_audit_file(output_dir)` and an artifact-map entry.
- Added compact slow-cycle audit envelope helpers in `slow_cycle.py`.
- Emitted one compact audit row per `run_phase6_chapter_cycle(...)` when `output_dir` is present and candidate/boundary evidence exists.

Audit decisions now visible:
- reflective promotion candidate `promoted` vs `withheld`
- cross-chapter active-attention item `carried` vs `not_carried`
- optional chapter reaction as `visible_trace_appended`
- knowledge activation operation as `warrant_context_update_observed`

Tests updated:
- `test_attentional_v2_slow_cycle.py`
- `test_attentional_v2_scaffold.py`

## Boundary Checks

Preserved boundaries:
- no slow-cycle behavior change
- no prompt text/version change
- no `runner.py` change
- no `read_context.py`, `state_projection.py`, or `skills/source_skills.py` change
- no public API, frontend, or eval runner change
- no full AI Evaluation
- no per-unit reflection, planner behavior, memory manager, retriever agent, vector DB, graph DB, or Memory OS

Audit safety:
- no full prompt packets copied
- no full chapter-consolidation payload copied
- no full durable stores copied
- no full source windows copied
- no audit dumps routed into prompts
- missing/ambiguous SourceRef evidence uses `missing_source_refs`, `not_assessed`, or compact omission-style metadata
- `withheld` and `not_carried` are valid auditable outcomes, not failures
- reaction records remain visible trace, not semantic memory
- knowledge activations remain warrant/context, not source truth

## Validation

Targeted tests run:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_slow_cycle.py tests/test_attentional_v2_scaffold.py -q
```

Result:
- `26 passed, 6 warnings`

Full AI Evaluation:
- not run by constraint

## Deviations From Accepted Brief

None.

`runner.py` was not changed because `slow_cycle.py` can emit audit evidence through the existing `output_dir`.

`continuation_capsule_delta` was omitted because Slice 6A can provide candidate/outcome envelopes without touching `state_projection.py` or copying larger continuation payloads.

## Next Gate

Human review of this Slice 6A Post-implementation Report.

Do not start the next implementation slice until this report is accepted or patched.
