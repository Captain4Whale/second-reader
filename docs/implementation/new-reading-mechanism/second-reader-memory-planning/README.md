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
| `codex/reports/README.md` | template | Post-implementation Report template | process template |
| `codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md` | post-implementation report | Slice 1 implementation evidence and review gate | accepted post-implementation report; not stable behavior authority |
| `codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md` | post-implementation report | Slice 2A implementation evidence and review gate | pending human review; not stable behavior authority |
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
Human review of `codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`.

Slice 2A implementation is complete and remains pending human review through the Post-implementation Report.

Codex must not start the next implementation slice until the Slice 2A Post-implementation Report is accepted and the next Pre-implementation Brief is created and accepted.

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

The current E实施1 audit is recorded at `codex/E实施1-Implementation Feasibility & Delta Audit v0.md` and has been accepted with reviewer constraints. Slice 1 implementation is recorded at `codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md` and is accepted. Slice 2A implementation is recorded at `codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md` and is pending human review.

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
