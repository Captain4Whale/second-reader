# Second Reader Memory / Planning Implementation Workspace

## Purpose

This directory contains the accepted Memory / Planning / Evaluation design chain and implementation handoff for optimizing the existing `attentional_v2` reading mechanism. It is not a greenfield redesign and does not replace the current mechanism. Its purpose is to provide a repo-local, implementation-facing source of truth for the next code-grounded feasibility audit and phased implementation.

This workspace is for tightening memory, planning, retrieval, slow-cycle, evaluation, and audit contracts in the current Second Reader / Reading Companion mechanism. It does not replace stable product docs, backend mechanism docs, or the evaluation constitution.

Use this directory to prepare the next Codex feasibility audit and later small, staged, auditable, reversible PRs. Do not use it to silently redefine stable behavior before implementation lands.

## Why This Exists

This design chain was triggered by a real implementation mismatch observed while implementing the current memory mechanism: `memory_uptake_ops` could be produced by `Read`, but downstream memory/state persistence and projection structures did not always align with that write intent. That failure mode raised the question of whether the project-owned memory and planning design had become too inward-looking.

The documents in this directory are the result of a follow-up loop: external evidence review, project-specific memory and planning assessment, accepted mechanism design, and implementation handoff. They should be read as a response to concrete `attentional_v2` implementation pressure, not as a detached new-mechanism proposal.

## Authority Order

1. Current repo implementation facts.
2. Stable project docs.
3. `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`.
4. `C设计1` through `C设计9` accepted design chain.
5. `E实施0-Implementation Roadmap & Handoff v0.md`.
6. `B分析` assessment reports.
7. `A调研` evidence packs, background only.
8. `D审核` review docs, historical only.

Evidence packs are external evidence indexes, not implementation sources. Review docs are historical review records and do not override the accepted design chain. `E实施0` is an implementation roadmap and handoff, not a final PR plan. `codex/E实施1-Implementation Feasibility & Delta Audit v0.md` is the accepted code-grounded feasibility and delta audit for the first implementation stage.

## Document Map

| File | Type | Role | Authority |
| --- | --- | --- | --- |
| `C设计-设计路线.md` | roadmap | design route and sequence overview | orientation |
| `E实施0-Implementation Roadmap & Handoff v0.md` | implementation handoff | implementation roadmap and handoff for the next audit | roadmap, not PR plan |
| `E实施0-Roadmap Review & Readiness Check v0.md` | review | roadmap readiness check | review, not accepted design authority |
| `codex/E实施-progress-ledger.md` | implementation ledger | implementation-stage progress, gates, reports, and reviewer decisions | progress record, not stable behavior authority |
| `codex/E实施1-Implementation Feasibility & Delta Audit v0.md` | implementation audit | code-grounded feasibility and delta audit for the accepted design chain | accepted code-grounded audit with reviewer constraints |
| `codex/briefs/README.md` | template | Pre-implementation Brief template | process template |
| `codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 1 contract and audit foundations brief | accepted pre-implementation brief |
| `codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 2A operation vocabulary and admission visibility hardening brief | accepted pre-implementation brief |
| `codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 2B store-specific admission and target-store policy hardening brief | accepted pre-implementation brief |
| `codex/briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 3A status-aware projection and boundary marker hardening brief | accepted pre-implementation brief |
| `codex/briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 3B lifecycle semantics and state-op boundary hardening brief | accepted pre-implementation brief |
| `codex/briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 4A supplemental retrieval intent and context assembly contract brief | accepted pre-implementation brief |
| `codex/briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 4B retrieval utilization trace and read-audit evidence brief | accepted pre-implementation brief |
| `codex/briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 5A detour lifecycle and navigation trace audit hardening brief | accepted pre-implementation brief |
| `codex/briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 5B planning support signals and detour value-cost audit markers brief | accepted pre-implementation brief |
| `codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 6A slow-cycle candidate and settlement audit envelope foundations brief | accepted pre-implementation brief |
| `codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 6B no-code closure checkpoint for slow-cycle re-entry, reconsolidation, and eval-readiness smoke | accepted no-code closure brief |
| `codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 7A minimal eval asset inventory and evidence wiring brief | accepted pre-implementation brief |
| `codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 7B minimal eval smoke harness and evidence availability validation brief | accepted pre-implementation brief |
| `codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 8A post-implementation review and minimal eval readiness gate brief | accepted pre-implementation brief |
| `codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 8B minimal eval suite run brief and execution guardrails | accepted pre-implementation brief |
| `codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 8C minimal eval suite execution preflight and bounded run brief | accepted pre-implementation brief |
| `codex/briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md` | pre-implementation brief | Slice 8H diagnostic evidence catalog entry brief for Minimal Eval Suite smoke | accepted pre-implementation brief |
| `codex/reports/README.md` | template | Post-implementation Report template | process template |
| `codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md` | post-implementation report | Slice 1 implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md` | post-implementation report | Slice 2A implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md` | post-implementation report | Slice 2B implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md` | post-implementation report | Slice 3A implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md` | post-implementation report | Slice 3B implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md` | post-implementation report | Slice 4A implementation evidence and review gate | reviewed; implementation direction accepted with patch request; not stable behavior authority |
| `codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md` | patch report | Slice 4A result-group precision patch evidence and review gate | accepted patch report; not stable behavior authority |
| `codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md` | post-implementation report | Slice 4B read-audit retrieval evidence implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md` | post-implementation report | Slice 5A detour lifecycle and navigation trace audit evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md` | post-implementation report | Slice 5B planning support marker implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md` | post-implementation report | Slice 6A slow-cycle candidate and settlement audit envelope evidence and review gate | reviewed; implementation direction accepted with patch request; not stable behavior authority |
| `codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md` | patch report | Slice 6A carried SourceRef audit evidence precision patch | accepted patch report; not stable behavior authority |
| `codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md` | post-implementation report | Slice 7A minimal eval asset inventory and evidence wiring implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md` | post-implementation report | Slice 7B minimal eval smoke harness and evidence availability validation implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md` | post-implementation report | Slice 8A readiness-gate evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md` | post-implementation report | Slice 8C bounded minimal eval execution attempt and failure evidence | accepted as failed execution evidence; not stable behavior authority |
| `codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md` | post-implementation report | Slice 8D Lane A source-locator compatibility patch evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md` | post-run report | Slice 8E Lane A `_retry1` bounded execution evidence and review gate | accepted post-run report; not stable behavior authority |
| `codex/reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md` | post-run report | Slice 8F Lane B bounded diagnostic smoke evidence and review gate | accepted post-run report; not stable behavior authority |
| `codex/reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md` | closure report | Slice 8G Minimal Eval Suite smoke closure and evidence interpretation report | accepted closure report; not stable behavior authority |
| `codex/reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md` | post-implementation report | Slice 8H diagnostic smoke evidence catalog entry report | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Aborted-Run-Report v0.md` | aborted-run report | Post-Slice8H Eval-1 full active evaluation attempt stop record and LLM-health finding | aborted operational evidence; not evaluation result authority |
| `codex/reports/Eval1-LLM-Health-and-Eval-Strictness-Repair-Post-implementation-Report v0.md` | post-implementation report | Eval-1 LLM health, eval strictness, same-tier failover, and operator preflight repair | accepted operational repair report; not evaluation result authority |
| `codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md` | post-run report | Eval-1 Retry1 high-parallel full active evaluation output for `attentional_v2` | pending human review; no catalog update or product-quality claim |
| `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md` | design | accepted mechanism boundary and charter | accepted design |
| `C设计1-Memory Ontology Design v0.md` | design | accepted memory ontology | accepted design |
| `C设计2-Planning Ontology Design v0.md` | design | accepted planning ontology | accepted design |
| `C设计3-Memory Formation & Settlement Design v0.md` | design | accepted memory formation and settlement design | accepted design |
| `C设计4-Navigation Policy Design v0.md` | design | accepted navigation policy design | accepted design |
| `C设计5-Memory Management & Evolution Design v0(patched).md` | design | accepted memory management and evolution design | accepted design |
| `C设计6-Detour : Look-back : Active Recall Policy Design v0.md` | design | accepted detour, look-back, and active recall policy | accepted design |
| `C设计7-Memory Retrieval & Utilization Design v0.md` | design | accepted memory retrieval and utilization design | accepted design |
| `C设计8-Slow-cycle : Macro-planning Design v0.md` | design | accepted slow-cycle and macro-planning design | accepted design |
| `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md` | design | accepted evaluation calibration and minimal eval implementation guidance | accepted design, evaluation implementation guidance |
| `B分析-Memory Mechanism Project Assessment & Improvement Directions.md` | assessment | memory mechanism assessment background | background |
| `B分析-Planning Mechanism Project Assessment & Improvement Directions.md` | assessment | planning mechanism assessment background | background |
| `A调研-Memory External Evidence Pack v1.md` | evidence | external memory evidence index | background only |
| `A调研-Planning External Evidence Pack v1.md` | evidence | external planning evidence index | background only |
| `A调研-Application Memory External Evidence Patch v1.md` | evidence | external application-memory evidence patch | background only |
| `D审核-设计5-Memory Management & Evolution Design v0.md` | review | historical review for design 5 | historical only |
| `D审核-设计6-Detour : Look-back : Active Recall Policy Design v0.md` | review | historical review for design 6 | historical only |
| `D审核-设计7-Memory Retrieval & Utilization Design v0.md` | review | historical review for design 7 | historical only |
| `D审核-设计8-Slow-cycle : Macro-planning Design v0.md` | review | historical review for design 8 | historical only |

## Current Next Step

Current next step:
Memory / Planning / Minimal Eval implementation track is closed after Slice 8H. The current follow-up is human review of the post-Slice8H Eval-1 Retry1 report; it is outside the closed implementation track and does not authorize catalog update, formal promotion, broader eval, or product-quality claims by itself.

Post-Slice8H Eval-1 full active evaluation was attempted later and stopped before completion. The conservative Lane A / Lane B jobs and the optimized Long Span producer job are all recorded as `abandoned`; the optimized producer generated only partial local artifacts and no `summary/aggregate.json`, `summary/report.md`, or `summary/llm_usage.json`. Its partial outputs must not be treated as valid full-evaluation evidence or reused as Lane A source outputs.

The LLM-health / eval-strictness repair is accepted. It adds strict eval output health gates, same-tier gateway failover for non-manual `network_blocked` / `llm_timeout` failures, live target preflight, and output health inspection tooling.

Eval-1 Retry1 high-parallel full active evaluation completed after the repair with fresh `20260519` run ids. It ran five Long Span producer windows in parallel, validated each producer with strict LLM health checks, and then ran five Lane A reuse shards from matching producer outputs. The post-run report is pending human review. No evidence catalog update, Long Span formal-authority promotion, or product-quality claim is authorized before that review.

Slice 4A implementation direction and precision patch are accepted. Slice 4B Pre-implementation Brief is accepted, Slice 4B implementation has landed, and the Slice 4B Post-implementation Report is accepted. Slice 5A Pre-implementation Brief is accepted, Slice 5A implementation has landed, and the Slice 5A Post-implementation Report is accepted. Slice 5B Pre-implementation Brief is accepted, Slice 5B implementation has landed, and the Slice 5B Post-implementation Report is accepted. Slice 6A Pre-implementation Brief is accepted, Slice 6A implementation has landed, the Slice 6A Post-implementation Report implementation direction is accepted with a requested carried SourceRef audit precision patch, and the Slice 6A patch report is accepted. Slice 6B no-code closure brief is accepted; Slice 6 is closed with no additional runtime implementation. Slice 7A minimal eval asset inventory and evidence wiring brief is accepted, Slice 7A implementation has landed, and the Slice 7A Post-implementation Report is accepted. Slice 7B minimal eval smoke harness and evidence availability validation brief is accepted, Slice 7B implementation has landed, and the Slice 7B Post-implementation Report is accepted. Slice 8A post-implementation review and minimal eval readiness gate brief is accepted, Slice 8A doc-only readiness gate has landed, and the Slice 8A Post-implementation Report is accepted. Slice 8B minimal eval suite run brief and execution guardrails is accepted. Slice 8C minimal eval suite execution preflight and bounded run brief is accepted, the bounded Lane A execution was attempted, Lane A failed after the fresh `attentional_v2` read completed because a visible reaction lacked a usable source-span locator for user-level selective matching, Lane B was not launched, and the Slice 8C Post-implementation Report is accepted as failed execution evidence. Slice 8D Lane A source-locator compatibility patch is implemented, and the Slice 8D Post-implementation Report is accepted. Slice 8E Lane A `_retry1` bounded execution completed successfully, and the Slice 8E Post-run Report is accepted. Slice 8F Lane B bounded diagnostic smoke completed successfully, and the Slice 8F Post-run Report is accepted. Slice 8G Minimal Eval Suite smoke closure and evidence interpretation report is accepted. Slice 8H diagnostic evidence catalog entry brief is accepted, the catalog entry has landed, and the Slice 8H Post-implementation Report is accepted. The Memory / Planning / Minimal Eval implementation track is closed after Slice 8H.

The completed Slice 8C through Slice 8G Minimal Eval Suite smoke is cataloged as `diagnostic_smoke` only. Further broader eval, formal authority promotion, runtime patches, additional catalog entries, or product-quality claims require a separate future brief.

## Non-goals

- No direct code implementation from this README.
- No new Memory design.
- No new Planning design.
- No `C设计10` / `C设计11` full pages unless later needed.
- No vector DB / graph DB / Memory OS.
- No manager agent / planner agent / retriever agent.
- No route steering UI.
- No user route choice.
- No full eval run before core instrumentation.
- No benchmark redesign.
- No evidence-pack-driven implementation.

## Implementation Posture

- Use small PRs.
- Build contract / audit foundations first.
- Harden formation / settlement.
- Harden lifecycle / projection.
- Add retrieval / utilization instrumentation.
- Harden planning trace.
- Add slow-cycle safety.
- Implement minimal eval after instrumentation.
- Run full AI evaluation only after core implementation is stable.

## Implementation Progress Tracking

Implementation-stage progress must be recorded in `codex/E实施-progress-ledger.md`.

Each implementation PR in this track requires an accepted Pre-implementation Brief before code changes and a Post-implementation Report after the PR. Use `codex/briefs/README.md` and `codex/reports/README.md` for the required templates.

The progress ledger and templates are process records. They do not replace stable product docs, stable mechanism docs, or `E实施1-Implementation Feasibility & Delta Audit`.

The current E实施1 audit is recorded at `codex/E实施1-Implementation Feasibility & Delta Audit v0.md` and has been accepted with reviewer constraints. Slice 1 implementation is recorded at `codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md` and is accepted. Slice 2A implementation is recorded at `codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md` and is accepted. Slice 2B implementation is recorded at `codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md` and is accepted. Slice 3A implementation is recorded at `codex/reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md` and is accepted. Slice 3B implementation is recorded at `codex/reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md` and is accepted. Slice 4A implementation is recorded at `codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`; its direction is accepted with a requested precision patch. The patch is recorded at `codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md` and is accepted. Slice 4B implementation is recorded at `codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md` and is accepted. Slice 5A Pre-implementation Brief is recorded at `codex/briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md` and is accepted. Slice 5A implementation is recorded at `codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md` and is accepted. Slice 5B Pre-implementation Brief is recorded at `codex/briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md` and is accepted. Slice 5B implementation is recorded at `codex/reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md` and is accepted. Slice 6A Pre-implementation Brief is recorded at `codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md` and is accepted. Slice 6A implementation is recorded at `codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`; its direction is accepted with a requested carried SourceRef audit precision patch. The patch is recorded at `codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md` and is accepted. Slice 6B no-code closure brief is recorded at `codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md` and is accepted; Slice 6 is closed. Slice 7A Pre-implementation Brief is recorded at `codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md` and is accepted. Slice 7A implementation is recorded at `codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md` and is accepted. Slice 7B Pre-implementation Brief is recorded at `codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md` and is accepted. Slice 7B implementation is recorded at `codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md` and is accepted. Slice 8A Pre-implementation Brief is recorded at `codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md` and is accepted. Slice 8A doc-only readiness gate is recorded at `codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md` and is accepted. Slice 8B Pre-implementation Brief is recorded at `codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md` and is accepted. Slice 8C Pre-implementation Brief is recorded at `codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md` and is accepted. Slice 8C bounded execution attempt is recorded at `codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md` and is accepted as failed execution evidence. Slice 8D Lane A source-locator compatibility patch is recorded at `codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md` and is accepted. Slice 8E Lane A `_retry1` bounded execution is recorded at `codex/reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md` and is accepted. Slice 8F Lane B bounded diagnostic smoke is recorded at `codex/reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md` and is accepted. Slice 8G Minimal Eval Suite smoke closure and evidence interpretation is recorded at `codex/reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md` and is accepted. Slice 8H diagnostic evidence catalog entry brief is recorded at `codex/briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md` and is accepted. Slice 8H implementation is recorded at `codex/reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md` and is accepted. The Memory / Planning / Minimal Eval implementation track is closed after Slice 8H.

Post-Slice8H Eval-1 full active evaluation was attempted and stopped before completion. The abort evidence is recorded at `codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Aborted-Run-Report v0.md`; it is operational evidence only, not an evaluation result or product-quality proof. The LLM-health / eval-strictness repair is recorded at `codex/reports/Eval1-LLM-Health-and-Eval-Strictness-Repair-Post-implementation-Report v0.md` and is accepted. The high-parallel Retry1 run is recorded at `codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md` and is pending human review before any catalog update, formal-authority promotion, broader eval, or product-quality claim.

## How To Use This Directory

1. Start with `README.md`.
2. Understand the causal chain: implementation mismatch -> external evidence review -> project assessment -> accepted design -> implementation handoff.
3. Read `E实施0-Implementation Roadmap & Handoff v0.md`.
4. Read `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`.
5. Read the relevant `C设计` docs for the implementation slice.
6. Use `B分析` assessments only as background.
7. Use `A调研` evidence only when design rationale needs source context, not as implementation instructions.
8. Do not treat `D审核` reviews as authority.
9. Read `codex/E实施1-Implementation Feasibility & Delta Audit v0.md`.
10. Read the current Pre-implementation Brief for the target slice.
11. Read the current Post-implementation Report if the target slice has already landed.
12. Do not advance to the next slice before the current Post-implementation Report is accepted.
