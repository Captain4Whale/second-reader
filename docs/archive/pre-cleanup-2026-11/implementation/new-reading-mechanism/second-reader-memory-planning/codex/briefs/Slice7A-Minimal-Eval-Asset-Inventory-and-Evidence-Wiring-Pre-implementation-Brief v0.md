# Slice 7A: Minimal Eval Asset Inventory and Evidence Wiring - Pre-implementation Brief v0

## PR Title

`Slice 7A: Minimal Eval Asset Inventory and Evidence Wiring`

## Implementation Slice

Slice 7A is the first small sub-slice of Slice 7 / Minimal Eval Implementation.

This slice focuses on inventorying existing evaluation assets and mapping the minimum evidence wiring needed to connect Slice 1-6 instrumentation to the existing eval lanes. It is not an evaluation redesign, not a new benchmark platform, and not an eval execution slice.

## Design Sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- Slice 1 through Slice 6 pre-implementation briefs, post-implementation reports, and patch reports
- `codex/E实施-progress-ledger.md` reviewer constraints

## Current Eval Asset Inventory

### Lane A: Local / User-level Selective Legibility

- Active evaluation docs:
  - `reading-companion-backend/docs/evaluation/user_level/README.md`
- Active split manifest:
  - `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- Active dataset package:
  - `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/`
- Active runner:
  - `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- Active renderer:
  - `reading-companion-backend/eval/attentional_v2/render_user_level_selective_audit.py`
- Helper module:
  - `reading-companion-backend/eval/attentional_v2/user_level_selective_v1.py`

Lane A remains the active local/user-level benchmark lane. Its current metric is note recall over aligned human notes with strict source-span overlap. Slice 7A must not replace it with excerpt surface, accumulation, or a new benchmark family.

### Lane B: Long Span MQ / Callback / FVI

- Active evaluation docs:
  - `reading-companion-backend/docs/evaluation/long_span/README.md`
- Active long-span runner:
  - `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- Probe exporter:
  - `reading-companion-backend/src/attentional_v2/benchmark_probes.py`
- Probe manifest:
  - `reading-companion-backend/eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json`
- Existing diagnostic evidence:
  - the current long-span vNext Phase-1 diagnostic run family, including the April 25 reaction-evidence rejudge artifacts referenced from the long-span evaluation docs.

Lane B remains diagnostic Phase-1 territory, not formal benchmark authority. It must preserve the Memory Quality, Spontaneous Callback, and False Visible Integration lanes rather than collapsing them into one broad score.

### Historical / Reference Assets

- `excerpt surface v1.1` remains historical / superseded for the local-user benchmark role.
- `accumulation benchmark v1` remains older bounded long-span evidence.
- `accumulation benchmark v2` remains discontinued / invalidated target-centered diagnostic evidence.
- Subsegment and earlier excerpt / chapter comparison assets remain reference unless a later accepted eval slice explicitly reactivates them.

## Current Code Facts

- Runtime artifact maps now expose `read_audit.jsonl`, `settlement_audit.jsonl`, and `slow_cycle_audit.jsonl`.
- `read_audit.jsonl` includes Slice 1-5 evidence such as memory uptake ops, admission events, operation contracts, supplemental retrieval metadata, navigation trace, and detour trace evidence.
- `settlement_audit.jsonl` includes compact state deltas and memory uptake operation outcomes.
- `slow_cycle_audit.jsonl` includes compact chapter-end candidate-vs-settled envelopes for slow-cycle promotion, carry-forward, knowledge activation, and visible-trace chapter reaction boundaries.
- Existing targeted tests cover read-audit retrieval evidence, navigation/detour evidence, projection markers, state-op lifecycle boundaries, and slow-cycle audit envelopes.
- Long-span vNext remains diagnostic Phase-1 and has not been promoted to formal benchmark authority.
- User-level selective remains the active local/user-level benchmark lane.
- Current runtime mechanism behavior should not change for Slice 7A.

## Evidence Surfaces Available After Slice 1-6

- `read_audit`:
  - `memory_uptake_ops`
  - `memory_uptake_op_count`
  - `memory_uptake_ops_by_target_store`
  - `memory_uptake_op_contracts`
  - `memory_uptake_admission_events`
  - `supplemental_retrieval`
  - `navigation_trace`
  - `detour_trace_evidence`
- `settlement_audit`:
  - compact state deltas
  - `memory_uptake_op_outcomes`
  - target-store settlement evidence
- `slow_cycle_audit`:
  - candidate-vs-settled envelopes
  - promotion / withhold boundaries
  - carried / not-carried boundaries
  - knowledge activation warrant/context boundary
  - visible-trace chapter reaction boundary
- Runtime projection / state evidence:
  - inline SourceRefs
  - SourceRef binding and resolution markers where present
  - projection markers such as `projection_role`, `support_status`, `lineage_only`, `current_support`, and `visible_trace_support`
  - target-store admission metadata
  - operation-store policy metadata
  - visible-trace boundaries for reaction records

These surfaces are evidence substrate only. They are not product-quality scores by themselves.

## Files To Change In Future PR

- A compact machine-readable inventory / evidence-wiring manifest, recommended under:
  - `reading-companion-backend/eval/manifests/`
- A focused static validation test, recommended as:
  - `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- Optional evaluation docs pointer update only if needed, preferably:
  - `reading-companion-backend/docs/evaluation/README.md`

## Files Explicitly Not Changing

- Runtime mechanism code under `reading-companion-backend/src/attentional_v2/`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- source skills
- existing eval runners
- durable mechanism state
- prompt text or prompt versions
- public API
- frontend

## Planned Deltas

Future Slice 7A implementation should be static inventory and wiring only:

- Add a compact manifest that maps Lane A and Lane B assets to the Slice 1-6 evidence surfaces each lane can consume.
- Preserve the two active eval lanes:
  - Lane A: Local / User-level Selective Legibility
  - Lane B: Long Span MQ / Callback / FVI
- Add lightweight diagnostic slots for Planning Trace Quality and Slow-cycle Safety only as evidence-availability diagnostics.
- Record that Planning Trace Quality must not be scored from trace existence alone.
- Record that Slow-cycle Safety must not be scored from audit existence alone.
- Record that retrieval availability is not utilization success.
- Record that visible reaction presence is not callback correctness.
- Record that SourceRef count is not a fidelity score.
- Do not add new metrics beyond the existing lane framing.
- Do not modify or run eval runners.

## Engineering Validation Commands

Future Slice 7A implementation should run only targeted static validation:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

Do not run full AI Evaluation, benchmark jobs, judge calls, reading jobs, broad stale suites, or long-running eval jobs in Slice 7A.

## Minimal Eval Smoke Proposal

Slice 7A should define, but not execute, a later minimal eval smoke.

The proposed later smoke should verify:

- Lane A and Lane B asset paths exist.
- The active manifests parse.
- The active dataset / probe assets are discoverable.
- The evidence-surface map names only existing artifact streams or documented runtime fields.
- Planning Trace Quality and Slow-cycle Safety remain diagnostic additions, not product-quality metrics.

No judge calls, reading jobs, full AI Evaluation, benchmark jobs, or product-quality scoring should happen in Slice 7A.

## Non-goals

- No evaluation system redesign.
- No new giant benchmark.
- No new eval platform.
- No broad new metric taxonomy.
- No runtime mechanism behavior change.
- No prompt text or prompt version change.
- No public API or frontend change.
- No mechanism state change.
- No eval runner change.
- No full AI Evaluation.
- No scoring planning quality from trace existence alone.
- No scoring slow-cycle quality from audit existence alone.
- No treating retrieval availability as utilization success.
- No treating visible reaction presence as callback correctness.
- No treating SourceRef count as fidelity score.

## Risks

- Inventory metadata could be mistaken for eval result evidence. The future Slice 7A PR must state that it is wiring readiness only.
- Historical eval assets could confuse the active lane boundary. The future PR must preserve Lane A and Lane B as the active tracks and leave historical assets clearly marked.
- Slice 7B may reveal runner-level gaps. Slice 7A should surface those as follow-up work rather than quietly changing runners.
- Static validation may feel too modest, but keeping this slice small prevents accidental benchmark redesign before the evidence map is accepted.

## Rollback Plan

Revert the future Slice 7A implementation PR.

Static manifest, docs pointer, and validation-test changes require no migration and do not affect runtime behavior or historical eval artifacts.

## Open Questions

None blocking.

Default decisions:

- Implement Slice 7A as static inventory / evidence wiring only.
- Preserve Lane A and Lane B.
- Defer actual eval smoke execution to a later accepted slice.
- Do not run full AI Evaluation.
- Do not change runtime behavior, prompts, public API, frontend, or eval runners.

## Go / No-go Recommendation

Go for human review of this Slice 7A brief.

No-go for eval implementation or eval execution until this brief is accepted.
