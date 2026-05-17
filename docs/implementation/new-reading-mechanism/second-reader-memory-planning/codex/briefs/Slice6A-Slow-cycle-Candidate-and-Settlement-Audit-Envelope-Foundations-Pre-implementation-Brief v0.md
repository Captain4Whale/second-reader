# Slice 6A: Slow-cycle Candidate and Settlement Audit Envelope Foundations — Pre-implementation Brief v0

## PR Title

`Slice 6A: Slow-cycle Candidate and Settlement Audit Envelope Foundations`

## Implementation Slice

Slice 6A is the first small reversible sub-slice of Slice 6 / Slow-cycle Safety. It focuses on audit clarity for existing slow-cycle candidate and settlement paths, not slow-cycle behavior expansion.

This brief is a gate document only. Slice 6A implementation must not start until this brief is accepted by the human reviewer.

## Design Sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计1-Memory Ontology Design v0.md`
- `C设计3-Memory Formation & Settlement Design v0.md`
- `C设计5-Memory Management & Evolution Design v0(patched).md`
- `C设计8-Slow-cycle : Macro-planning Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `codex/briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
- `codex/reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`
- `codex/E实施-progress-ledger.md` reviewer constraints

## Current Code Facts

- `reading-companion-backend/src/attentional_v2/slow_cycle.py` owns chapter consolidation, reflective promotion, cross-chapter carry-forward, reconsolidation, and `run_phase6_chapter_cycle(...)`.
- `chapter_consolidation(...)` returns a normalized `ChapterConsolidationResult`.
- `_normalize_chapter_consolidation_result(...)` normalizes `cooling_operations`, `promotion_candidates`, `knowledge_activation_updates`, and `cross_chapter_carry_forward`.
- `run_phase6_chapter_cycle(...)` applies cooling operations, cross-chapter carry-forward, knowledge activation updates, reflective promotion candidates, and optional chapter reactions.
- Reflective promotion already separates candidate/result from durable writes: `apply_reflective_promotion(...)` returns unchanged state unless the normalized result has `decision="promote"` and a valid `reflective_item`.
- Reconsolidation already separates result from durable writes: `apply_reconsolidation(...)` appends later reaction and reconsolidation records only for `decision="reconsolidate"` and does not mutate the earlier reaction.
- Cross-chapter carry-forward preserves and dedupes existing `SourceRef` evidence by `item_id`; new carry-forward items without refs remain unsupported rather than borrowing refs by text.
- Existing artifact map includes `unitization_audit.jsonl`, `read_audit.jsonl`, and `settlement_audit.jsonl`, but there is no dedicated slow-cycle candidate-vs-settled audit envelope.
- Existing tests cover carry-forward SourceRef preservation, carry-forward ref dedupe, reconsolidation append-only behavior, and the Phase 6 chapter cycle.

## Files To Change In Future PR

- `reading-companion-backend/src/attentional_v2/schemas.py`, for optional mechanism-private audit envelope TypedDicts only.
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`, for helper-level audit envelope construction and emission only.
- `reading-companion-backend/src/attentional_v2/storage.py`, only if a compact `slow_cycle_audit.jsonl` path helper is chosen.
- `reading-companion-backend/src/attentional_v2/observability.py`, only if a compact slow-cycle audit writer is chosen.
- `reading-companion-backend/tests/test_attentional_v2_slow_cycle.py`.
- `reading-companion-backend/tests/test_attentional_v2_scaffold.py`, only if runner/scaffold-level artifact initialization needs coverage.

## Files Explicitly Not Changing

- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/skills/source_skills.py`
- public API files
- frontend files
- eval runners

`runner.py` should remain unchanged unless implementation proves slow-cycle audit evidence cannot be emitted from the existing `output_dir` path. No prompt text or prompt version change is planned.

## Planned Deltas

- Add compact mechanism-private slow-cycle audit envelopes that distinguish slow-cycle candidates from settled durable truth.
- Candidate envelope fields may include `trigger_type`, `candidate_type`, `candidate_id`, `source_ref_count`, `source_ref_resolution_statuses`, and `promotion_evidence_status`.
- Settlement/outcome fields may include `settlement_decision`, `settlement_reason`, `withhold_promotion_reason`, `not_carried_reason`, `carry_forward_reason`, and compact `continuation_capsule_delta` only if safely observable without copying full payloads.
- Use conservative outcome language. Candidate existence is not durable truth, promotion success, model quality proof, or source truth.
- Treat `withhold` and `not_carried` as valid auditable outcomes, not failures.
- Treat promoted reflective frames as requiring supporting `SourceRef` evidence.
- Keep `reaction_records` as visible trace, not semantic memory.
- Keep `knowledge_activations` as warrant/context, not source truth.
- Prefer `not_assessed`, omission, or count-only metadata when evidence is unavailable.
- Do not infer slow-cycle quality, source truth, or model utilization from candidate existence.

## Engineering Tests

Future implementation should run only the targeted tests:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_slow_cycle.py tests/test_attentional_v2_scaffold.py -q
```

Required test coverage:

- Promotion candidate audit envelope remains separate from settled reflective frame writes.
- Withheld promotion is recorded as a valid auditable outcome.
- Carry-forward records carried/not-carried evidence without changing SourceRef merge behavior.
- Reconsolidation records candidate/result boundaries without rewriting prior reactions.
- Knowledge activation updates remain warrant/context, not source truth.
- Optional chapter reactions remain visible trace, not semantic memory.
- Existing Phase 6 behavior remains unchanged unless a later accepted implementation brief patch explicitly scopes a tiny helper-level change.

## Contract / Audit Checks

- Candidate is not durable truth.
- Promotion requires supporting `SourceRef` evidence.
- Withhold is valid and auditable.
- Not-carried is valid and auditable.
- Reaction records remain visible trace, not semantic memory.
- Knowledge activations remain warrant/context, not source truth.
- Audit envelopes are mechanism-private and must not be routed into prompts.
- Do not copy full prompt packets, raw candidate payload dumps, or full durable-store payloads into audit rows.
- Do not run full AI Evaluation.

## Non-goals

- No slow-cycle behavior expansion.
- No per-unit reflection.
- No general planner behavior.
- No prompt text/version change.
- No source-skill behavior change.
- No retrieval loop.
- No public API or frontend change.
- No eval runner change.
- No vector DB, graph DB, Memory OS, memory manager agent, planner agent, or retriever agent.
- No full AI Evaluation.

## Risks

- Audit envelopes could be mistaken for durable state or promotion authority; names and report wording must keep candidate and settled truth separate.
- Source-ref resolution status may be incomplete for some candidate shapes; prefer `not_assessed` or omission instead of pretending precision.
- A dedicated slow-cycle audit stream could add artifact surface area; keep it compact, mechanism-private, and documented as non-authoritative process evidence.
- If implementation touches `runner.py` only to pass audit evidence, it could widen the slice; default is to emit from `slow_cycle.py` via existing `output_dir`.

## Rollback Plan

Revert the future Slice 6A PR. Optional TypedDicts and mechanism-private audit rows require no migration, and existing slow-cycle behavior returns to the Slice 5B accepted state.

## Open Questions

None blocking.

Default decisions:

- No prompt change.
- No `runner.py` change unless implementation proves it is necessary.
- No behavior change.
- No dedicated stable behavior doc update during implementation unless the future PR changes stable behavior, which is not intended.
- Use `not_assessed`, omission, or count-only metadata when evidence cannot be derived safely.

## Go / No-go Recommendation

Go for human review of this brief.

No-go for implementation until the Slice 6A Pre-implementation Brief is accepted.
