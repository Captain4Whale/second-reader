# Slice 8A: Post-implementation Review and Minimal Eval Readiness Gate - Pre-implementation Brief v0

## PR Title

`Slice 8A: Post-implementation Review and Minimal Eval Readiness Gate`

## Implementation Slice

Slice 8A is the first small sub-slice of Slice 8 / Post-implementation Review & Eval Readiness.

This is a readiness-gate slice, not an eval execution slice. It reviews accepted Slice 1 through Slice 7B evidence, checks whether the instrumentation and eval-wiring surfaces are ready for a later Minimal Eval Suite run, and decides whether a prerequisite patch is needed before that later run is briefed.

Default recommendation: no runtime patch and no eval-runner patch are indicated. Land a doc-only readiness gate, keep eval execution blocked, and proceed later to a separately accepted Minimal Eval Suite run brief.

## Design Sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `docs/backend-reader-evaluation.md`
- Slice 1 through Slice 7B Pre-implementation Briefs
- Slice 1 through Slice 7B Post-implementation Reports
- Slice 4A precision patch report
- Slice 6A carried SourceRef audit precision patch report
- Slice 6B no-code closure brief
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`
- `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- `reading-companion-backend/scripts/validate_minimal_eval_inventory_smoke.py`
- `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`

## Accepted-slice Inventory

| Slice | Accepted evidence | Readiness relevance |
| --- | --- | --- |
| Slice 1 | Contract / audit foundations report accepted | Introduced `read_audit` and `settlement_audit` contract/outcome surfaces. |
| Slice 2A | Operation vocabulary and admission visibility report accepted | Hardened memory uptake admission visibility and operation vocabulary. |
| Slice 2B | Store-specific admission and target-store policy report accepted | Hardened target-store policy and admission/outcome boundaries. |
| Slice 3A | Status-aware projection and boundary marker report accepted | Added projection/status/boundary markers for prompt-facing and diagnostic review. |
| Slice 3B | Lifecycle semantics and state-op boundary report accepted | Hardened lifecycle/state-op boundary tests without changing runtime `state_ops.py` behavior. |
| Slice 4A | Supplemental retrieval intent/context assembly report accepted with precision patch accepted | Made retrieval intent, boundaries, result groups, and forwarding policy explicit without full active-recall object forwarding. |
| Slice 4B | Retrieval utilization trace and read-audit evidence report accepted | Added compact `read_audit.supplemental_retrieval` evidence without claiming model utilization. |
| Slice 5A | Detour lifecycle/navigation trace report accepted | Added compact navigation and detour lifecycle audit evidence. |
| Slice 5B | Planning support signal/value-cost marker report accepted | Added non-scoring planning support markers to existing navigation/detour evidence. |
| Slice 6A | Slow-cycle audit envelope report accepted with carried SourceRef precision patch accepted | Added `slow_cycle_audit.jsonl` candidate-vs-settled envelopes and tightened carried SourceRef audit evidence. |
| Slice 6B | No-code slow-cycle closure brief accepted | Closed Slice 6 without more runtime implementation. |
| Slice 7A | Minimal eval inventory/evidence wiring report accepted | Added static inventory manifest mapping eval lanes to Slice 1-6 evidence surfaces. |
| Slice 7B | Minimal eval smoke harness report accepted by latest reviewer message | Added stdlib-only smoke validator for manifest/evidence availability; no eval execution. |

## Evidence-surface Readiness Matrix

| Evidence surface | Implemented | Targeted engineering coverage | Slice 7A manifest reference | Slice 7B smoke validation | Readiness note |
| --- | --- | --- | --- | --- | --- |
| `read_audit` | yes | yes, via observability and mechanism audit tests across Slice 1, Slice 4B, Slice 5A, and Slice 5B | yes | yes, as required evidence surface and artifact token | Ready as an audit substrate, not product-quality proof. |
| `settlement_audit` | yes | yes, via settlement/outcome and state-op boundary coverage | yes | yes, as required evidence surface and artifact token | Ready for memory uptake outcome evidence, not durable truth by itself. |
| `supplemental_retrieval` | yes | yes, via Slice 4B observability/state-projection tests | yes | yes, as `read_audit.supplemental_retrieval` | Ready for availability/contract evidence, not utilization success. |
| `navigation_trace` | yes | yes, via Slice 5A/5B observability, scaffold, and Navigate act-space tests | yes | yes, as `read_audit.navigation_trace` | Ready for planning trace diagnostics, not planning quality scoring. |
| `detour_trace_evidence` | yes | yes, via Slice 5A/5B detour lifecycle and observability tests | yes | yes, as `read_audit.detour_trace_evidence` | Ready for detour lifecycle evidence, not route recommendation or route UX. |
| `slow_cycle_audit` | yes | yes, via Slice 6A slow-cycle/scaffold tests and carried SourceRef precision patch coverage | yes | yes, as runtime `slow_cycle_audit.jsonl` artifact token | Ready for candidate-vs-settled review, not slow-cycle quality scoring. |
| SourceRef binding / resolution markers | yes | yes, via SourceRef-first settlement/projection/slow-cycle tests | yes | yes, through `source_refs` / `SourceRef` token validation | Ready for source binding diagnostics; SourceRef count is not a fidelity score. |
| Projection markers | yes | yes, via Slice 3A state-projection tests | yes | yes, through required projection marker tokens | Ready for boundary/status diagnostics, not source truth by itself. |
| Memory uptake admission / outcome fields | yes | yes, via Slice 1, 2A, and 2B audit/operation tests | yes | yes, through admission/outcome field token validation | Ready for operation-contract review, not product-quality proof. |

## Eval-lane Readiness Matrix

| Lane | Status | Evidence wiring | Readiness assessment |
| --- | --- | --- | --- |
| Lane A: Local / User-level Selective Legibility | active benchmark lane | `read_audit`, `settlement_audit`, SourceRef binding/resolution markers, projection markers, memory uptake admission/outcome fields | Ready for a later scoped minimal eval run brief. The active dataset pointer remains distinct from the current formal evidence bundle boundary. No new run is started in Slice 8A. |
| Lane B: Long Span MQ / Callback / FVI | diagnostic phase 1, not formal authority | all required evidence surfaces, including supplemental retrieval, navigation/detour trace evidence, and slow-cycle audit | Ready for later diagnostic smoke/run planning. Slice 8A must not promote Long Span vNext to formal benchmark authority. |

## Known Gaps

- No full AI Evaluation has been run after Slice 1 through Slice 7B instrumentation.
- No benchmark jobs, judge calls, reading jobs, or eval run directories are created by Slice 8A.
- No product-quality result is claimed from instrumentation availability.
- Local-only dataset and run-artifact pointers may differ by clone; Slice 7B reports availability state rather than failing missing local-only paths.
- Existing eval runners are intentionally not rewired to consume the Slice 7A manifest.
- Planning Trace Quality and Slow-cycle Safety remain evidence-availability diagnostics only.
- A later Minimal Eval Suite run brief still needs to define exact lane subset, run mode, judge mode, cost posture, background-job handling, and acceptance criteria before any eval execution.

## Files To Change In Future Slice 8A Landing

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

If this brief is accepted, a later doc-only Slice 8A readiness report may be created under `codex/reports/` to record the final gate decision before a Minimal Eval Suite run brief.

## Files Explicitly Not Changing

- Runtime mechanism code under `reading-companion-backend/src/attentional_v2/`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- source skills
- eval runners
- judge prompts
- durable mechanism state
- public API
- frontend

## Planned Deltas

Slice 8A should land a doc-only readiness gate:

- Mark the Slice 7B Post-implementation Report as accepted.
- Add this Slice 8A Pre-implementation Brief as pending human review.
- Record that Slice 1 through Slice 7B instrumentation and static eval wiring are ready enough for a later Minimal Eval Suite run brief.
- Explicitly state that no prerequisite runtime patch is currently indicated.
- Keep actual eval execution blocked until a later run brief is accepted.

No code change, runtime change, eval-runner change, prompt change, public API change, frontend change, durable-state change, benchmark job, judge call, reading job, or eval run directory is part of Slice 8A.

## Validation Commands

Slice 8A brief landing should run only static/readiness checks:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

The forbidden-file diff check must return empty output.

## Contract / Interpretation Checks

- Audit existence is not product quality.
- Retrieval availability is not utilization success.
- Visible reaction presence is not callback correctness.
- SourceRef count is not fidelity score.
- Trace existence is not planning quality.
- `slow_cycle_audit` existence is not slow-cycle quality.
- Contract / audit checks are readiness evidence, not product-quality scores.

## Non-goals

- No full AI Evaluation.
- No benchmark jobs.
- No judge calls.
- No reading jobs.
- No eval run directories.
- No eval-runner modification.
- No runtime mechanism behavior change.
- No prompt text/version change.
- No public API or frontend change.
- No durable mechanism state change.
- No new metric taxonomy.
- No scoring.
- No Long Span vNext promotion to formal benchmark authority.
- No actual Minimal Eval Suite run before a later accepted run brief.

## Risks

- Readiness language could be mistaken for eval result evidence. Mitigation: call Slice 8A readiness-only and keep product-quality claims out of scope.
- Local-only assets could create portability confusion. Mitigation: preserve Slice 7B local-only reporting semantics and do not fail missing local-only paths.
- Slice 8B or a later run brief may still discover run-level gaps. Mitigation: record them as eval-run prerequisites rather than silently changing runners in Slice 8A.
- Evidence-surface availability could be overread as quality. Mitigation: repeat the interpretation guards in the brief and any later readiness report.

## Rollback Plan

Revert the doc-only Slice 8A landing. No migration, runtime rollback, eval artifact cleanup, or durable-state repair is required.

## Open Questions

None blocking.

Default decision: no prerequisite runtime or eval-runner patch is indicated before a later Minimal Eval Suite run brief.

## Go / No-go Recommendation

Go for human review of this Slice 8A Pre-implementation Brief.

No-go for actual eval execution, benchmark jobs, judge calls, reading jobs, eval run directories, runtime behavior changes, or eval-runner changes until Slice 8A is accepted and a later Minimal Eval Suite run brief is created and accepted.
