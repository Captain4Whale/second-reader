# Slice 6B: Slow-cycle Re-entry, Reconsolidation, and Eval-readiness Smoke — Pre-implementation Brief v0

## PR Title

`Slice 6B: Slow-cycle Re-entry, Reconsolidation, and Eval-readiness Smoke`

## Implementation Slice

Slice 6B is a small closure checkpoint for Slice 6 / Slow-cycle Safety. It inspects whether any minimal follow-up is needed after Slice 6A and the carried SourceRef audit precision patch before moving to Slice 7 / Minimal Eval Implementation.

This brief recommends no runtime implementation PR for Slice 6B. If accepted, Slice 6 should close and the next gate should be Slice 7 / Minimal Eval Implementation.

## Design Sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计1-Memory Ontology Design v0.md`
- `C设计3-Memory Formation & Settlement Design v0.md`
- `C设计5-Memory Management & Evolution Design v0(patched).md`
- `C设计8-Slow-cycle : Macro-planning Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
- `codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
- `codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
- `codex/E实施-progress-ledger.md` reviewer constraints

## Current Code Facts

- `slow_cycle_audit.jsonl` records compact chapter-end envelopes for reflective promotion, cross-chapter carry-forward, knowledge activation updates, and optional chapter reactions.
- Carried `cross_chapter_carry_forward` audit evidence uses existing post-cooling active item SourceRefs plus carry-forward candidate SourceRefs, deduped with `dedupe_source_refs(...)`.
- Reflective promotion separates candidate/result from durable write: `apply_reflective_promotion(...)` only writes when the normalized result has `decision="promote"` and a valid reflective item.
- Reconsolidation separates candidate/result from durable writes: `reconsolidation(...)` returns a result, and `apply_reconsolidation(...)` appends a later reaction and reconsolidation record only when `decision="reconsolidate"`.
- Existing reconsolidation tests cover append-only behavior and verify the earlier reaction is not mutated.
- `reconsolidation_records.json`, `continuation_capsule.json`, `local_continuity.detour_trace`, `read_audit.navigation_trace`, and `read_audit.detour_trace_evidence` already provide adjacent evidence surfaces.
- Detour lifecycle and navigation trace ownership was handled in Slice 5A / Slice 5B and should remain there.
- Slice 7 / Minimal Eval Implementation is the accepted roadmap point for evaluating these instrumentation surfaces rather than adding more pre-emptive Slice 6 runtime instrumentation.

## Files To Change In Future PR

None. This brief recommends no code implementation for Slice 6B.

## Files Explicitly Not Changing

- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/skills/source_skills.py`
- durable memory stores
- public API
- frontend
- eval runners

## Planned Deltas

No code change.

The only planned landing work is this doc-only pre-implementation brief and status updates that:

- mark the Slice 6A carried SourceRef audit precision patch report as accepted;
- set Slice 6B brief review as the next human gate;
- state that Slice 6 can close if this no-code closure brief is accepted;
- defer any runtime quality claims to Slice 7 / Minimal Eval Implementation.

## Engineering Tests

No engineering tests are required for Slice 6B because no runtime implementation is recommended.

Brief landing validation should run only:

```bash
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only
```

Do not run backend tests, benchmark jobs, stale broad suites, or full AI Evaluation during the brief landing.

## Contract / Audit Checks

- Candidate existence remains separate from durable truth.
- Promotion candidate existence remains separate from promotion success.
- Withhold and not-carried remain valid auditable outcomes, not failures.
- Reconsolidation remains append-only visible trace / reconsolidation evidence, not destructive rewrite.
- Slow-cycle audit is sufficient for minimal eval-readiness on promotion, withhold, carried, not-carried, warrant/context, and visible-trace boundaries.
- Detour continuity remains owned by Slice 5 navigation/detour trace rather than slow-cycle audit.
- Continuation/re-entry should be evaluated in Slice 7 from existing artifacts rather than adding pre-emptive Slice 6 runtime instrumentation.
- Audit artifacts must not be routed into prompts.
- Slow-cycle instrumentation is eval substrate, not proof of slow-cycle quality.

## Non-goals

- No slow-cycle behavior change.
- No prompt text or prompt version change.
- No `runner.py` change.
- No reconsolidation audit stream expansion.
- No continuation-capsule delta implementation.
- No per-unit reflection.
- No general planner behavior.
- No source-skill behavior change.
- No retrieval loop.
- No public API or frontend change.
- No eval runner change.
- No vector DB, graph DB, Memory OS, memory manager agent, planner agent, or retriever agent.
- No full AI Evaluation.

## Risks

- Slice 7 may reveal that reconsolidation would benefit from a dedicated audit envelope, but existing append-only records and tests are enough for minimal smoke readiness.
- `continuation_capsule_delta` remains not explicitly traced; treat this as a Slice 7 observation target, not a Slice 6 blocker.
- Closing Slice 6 without code could be misread as proving slow-cycle quality. The actual claim is narrower: instrumentation is sufficient to start minimal eval smoke.

## Rollback Plan

No runtime rollback is needed because this brief recommends no code change.

If human review disagrees, create a new narrow Slice 6B implementation brief for one specific evidence gap rather than broadening this closure slice.

## Open Questions

None blocking.

Default decisions:

- No code implementation for Slice 6B.
- No prompt change.
- No `runner.py` change.
- No reconsolidation audit expansion before Slice 7.
- No continuation delta instrumentation before Slice 7.
- No full AI Evaluation.

## Go / No-go Recommendation

Go for human review of this no-code closure brief.

No-go for additional Slice 6 implementation. If accepted, close Slice 6 and proceed to Slice 7 / Minimal Eval Implementation.
