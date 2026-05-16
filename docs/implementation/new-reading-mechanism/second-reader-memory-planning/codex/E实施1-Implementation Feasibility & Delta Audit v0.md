# E实施1-Implementation Feasibility & Delta Audit v0

## 0. Executive Verdict

Verdict: ready for human review and acceptance before implementation.

The accepted Memory / Planning / Evaluation design chain is feasible as an optimization track for the existing `attentional_v2` mechanism. The current repo already has the main working skeleton: `Navigate.choose_next_unit`, `Read`, Reading Runner post-read settlement, inline `SourceRef`, mechanism-private runtime artifacts, bounded source skills, chapter-end slow-cycle behavior, and two active evaluation lanes.

The main delta is not a greenfield rebuild. It is contract and audit hardening:

- make `Read.memory_uptake_ops` admission explicit instead of implicit;
- align operation vocabulary across schema, node normalization, prompts, and settlement;
- record per-op validation, source binding, and settlement outcomes;
- separate candidate, settled, projected, and retrieved memory surfaces more visibly;
- add retrieval utilization and planning trace instrumentation before any broad AI evaluation;
- keep slow-cycle safety audit-first and avoid turning it into a planner or memory-manager agent.

No implementation code was modified in this audit. No tests, benchmark jobs, or full AI Evaluation were run.

Recommended next move after human acceptance: create a Pre-implementation Brief for Slice 1 / Contract and Audit Foundations. The PR order below is provisional and must not be treated as an accepted PR plan until this audit is reviewed.

Blocking issues: none for moving to human review.

Human confirmation needed:

- whether missing `target_store` should become an immediate validation error or a legacy-tolerant audit warning first;
- whether `resolve` should be admitted in the `nodes.py` operation allowlist to match `schemas.py`;
- final names for projection markers such as current-support vs lineage and visible-trace vs warrant;
- how much typed slow-cycle audit structure should land before the slow-cycle slice.

## 1. Scope / Inputs

### Governance inputs

- `AGENTS.md`
- `reading-companion-backend/AGENTS.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Roadmap Review & Readiness Check v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### Accepted design inputs

- `C设计0-Second Reader Shared Memory–Planning Mechanism Charter v0.md`
- `C设计1-Memory Ontology Design v0.md`
- `C设计2-Planning Ontology Design v0.md`
- `C设计3-Memory Formation & Settlement Design v0.md`
- `C设计4-Navigation Policy Design v0.md`
- `C设计5-Memory Management & Evolution Design v0(patched).md`
- `C设计6-Detour : Look-back : Active Recall Policy Design v0.md`
- `C设计7-Memory Retrieval & Utilization Design v0.md`
- `C设计8-Slow-cycle : Macro-planning Design v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`

### Code and evaluation files inspected

| Area | Files |
| --- | --- |
| Runtime schema | `reading-companion-backend/src/attentional_v2/schemas.py` |
| Node normalization and prompts | `reading-companion-backend/src/attentional_v2/nodes.py`, `reading-companion-backend/src/attentional_v2/prompts.py` |
| Reading runner and settlement | `reading-companion-backend/src/attentional_v2/runner.py`, `reading-companion-backend/src/attentional_v2/state_ops.py` |
| Projection and context | `reading-companion-backend/src/attentional_v2/state_projection.py`, `reading-companion-backend/src/attentional_v2/read_context.py` |
| Source grounding and skills | `reading-companion-backend/src/attentional_v2/source_spans.py`, `reading-companion-backend/src/attentional_v2/skills/source_skills.py`, `reading-companion-backend/src/attentional_v2/skills/runtime.py` |
| Slow-cycle and durable stores | `reading-companion-backend/src/attentional_v2/slow_cycle.py`, `reading-companion-backend/src/attentional_v2/knowledge.py`, `reading-companion-backend/src/attentional_v2/storage.py` |
| Audit and observability | `reading-companion-backend/src/attentional_v2/observability.py` |
| Evaluation docs/tests | `reading-companion-backend/docs/evaluation/user_level/README.md`, `reading-companion-backend/docs/evaluation/long_span/README.md`, `reading-companion-backend/tests/test_long_span_vnext.py`, `reading-companion-backend/tests/test_attentional_v2_knowledge.py` |

### Non-goals for this audit

- No backend, frontend, prompt, schema, runner, or evaluation implementation changes.
- No PR implementation plan approval.
- No full AI Evaluation.
- No test execution.
- No rewrite of `C设计0` through `C设计9`, `E实施0`, or roadmap review docs.
- No stable behavior doc rewrite.

## 2. Design-to-file Delta Matrix

| Design contract | Current code fact | Delta / gap | Risk | Recommended handling |
| --- | --- | --- | --- | --- |
| Optimize existing `attentional_v2`; preserve working skeleton | The runner already coordinates `Navigate.choose_next_unit`, `Read`, post-read settlement, detour drain, and chapter cycle. | No structural replacement needed. | Low if PRs stay slice-scoped; high if implementation tries to redesign the loop. | Preserve current loop and add contracts around it. |
| SourceRef-first memory formation | `SourceRef` is inline in `schemas.py`; `runner.py` resolves `source_quote` into `source_refs`; `source_spans.py` has matched, ambiguous, and fallback resolution states. | Source-binding outcome is not surfaced as a first-class per-op audit result. Fallback source refs are not semantically gated per target store. | High because source-free or weakly grounded memory can look settled. | Add additive binding status fields and warnings before changing behavior. |
| Read write intent must be bounded and explicit | `ReadUnitResult` has `memory_uptake_ops`; prompt limits target stores to `active_attention`, `concept_registry`, and `thread_trace`. | Operation admission is still mostly implicit; malformed ops can be skipped or defaulted without a durable outcome. | High because the original mismatch came from write intent versus downstream store shape. | Add validation/admission audit first, then harden settlement. |
| Operation vocabulary must align across prompt, schema, normalization, and settlement | `schemas.py` includes `StateOperationType` with `resolve`; `state_ops.py` treats close/resolve; `nodes.py` allowlist omits `resolve`. | `resolve` is accepted by schema but can be dropped during node normalization. | High, especially for detour closure and memory lifecycle semantics. | Align allowlists after human confirms tolerant parse strategy. |
| Missing or invalid `target_store` should not silently redefine intent | `nodes.py` defaults missing `target_store` to `active_attention`; store apply functions then filter by target store. | A missing target can become active-attention intent without explicit evidence. | High because it hides schema drift and prompt mistakes. | First add warning/audit marker; later decide whether to reject. |
| Settlement must be auditable per op | `observability.record_settlement` records compact before/after deltas and target-store distribution. | No per-op outcome, failure reason, validation result, source binding result, or deferred reason. | High because implementation cannot prove which op settled, skipped, transformed, or failed. | Slice 1 should add additive per-op outcome contract and tests. |
| Memory lifecycle must distinguish active support, lineage, visible reaction, and warrant | `state_projection.py` builds `attentional_v2.state_packet.v1`; it includes active attention, concepts, threads, reflective frames, recent reactions, and knowledge activations. | Projection does not clearly mark current-support vs lineage, reaction visible trace, or knowledge activation warrant status. | Medium-high because runtime prompt context can blur source truth and derived memory. | Harden projection markers after settlement audit foundation. |
| `reaction_records` are visible traces, not semantic memory | Prompt tells `Read` not to write `reaction_records`; runner persists surfaced reactions separately; projection includes recent reactions. | Projection/retrieval markers can be stronger so downstream prompts do not treat reactions as durable semantic memory. | Medium. | Add explicit marker/contract in projection and audit docs when implementation lands. |
| `knowledge_activations` are warrant/activation state, not source truth | Knowledge activation state exists and has tests. | Projection/retrieval needs clearer warrant markers and guardrails. | Medium. | Add additive fields/labels; preserve existing knowledge tests. |
| Retrieval should record returned vs used memory | `read_context.py` supports `look_back` and `active_recall`; it returns source refs, excerpts, concepts, threads, and reactions. | No first-class retrieval utilization trace: no explicit intent, returned items, used items, ignored items, or no-use reason. | Medium-high because memory quality cannot be debugged from output alone. | Add retrieval utilization instrumentation before eval expansion. |
| Detour, look-back, and active recall should restore mainline safely | Runner tracks detour need, skill requests/results, budget state, defer reason, and navigation trace entries. | Trace lacks consistent source scent, detour value, continuity cost, and restore-mainline reason fields. | Medium. | Harden planning trace as a slice after retrieval instrumentation. |
| C设计8 slow-cycle should be audit-first, not a new planner | `slow_cycle.py` has chapter consolidation, carry-forward, promotion candidates, promote/withhold, reconsolidation, and optional reactions. | No unified candidate set / settlement event envelope; withhold/not-carried/capsule deltas are not first-class audit rows. | High if implemented as broad planner; medium if audit-only first. | Keep Slice 6 audit-first; do not add planner/manager agents. |
| Source skills path and boundary must be explicit | Actual path is `reading-companion-backend/src/attentional_v2/skills/source_skills.py`; runtime supports `source_map_overview`, `source_scope_drilldown`, and `source_window_fetch`, bounded by mainline cursor. | E实施1 confirms the actual path and boundary. | Low. | Use this path in later briefs; do not invent `source_skills.py` at package root. |
| Evaluation must remain two-lane and instrumentation-first | User-level selective v1 and Long Span MQ / Callback / FVI docs and runners exist. | Planning/slow-cycle eval should not be expanded before audit data exists. | Medium if eval is run before instrumentation. | Defer full AI Evaluation; implement minimal eval after core instrumentation. |

## 3. Fields Already Present

The repo already contains enough structure to support phased hardening:

- `StateOperationType`, including `resolve`, in `schemas.py`.
- Inline `SourceRef` with source span, quote, role, and resolution metadata.
- `ReadUnitResult` fields: `reading_impression`, `surfaced_reactions`, `memory_uptake_ops`, and `detour_need`.
- `StateOperation` fields: `op`, `operation_type`, `target_store`, `target_key`, `item_id`, `reason`, and `payload`.
- `NavigateActTraceEntry` with decision, selection, reason, end anchor, source span, skill request/result/error, and budget state.
- `KnowledgeActivation` and `KnowledgeActivationsState`.
- Prompt-level constraints for bounded memory ops, `source_quote`, no direct writes to `reaction_records`, and no secret detour routing.
- Runner-level `source_quote` to `source_refs` normalization for memory uptake ops.
- Runner-level settlement into `active_attention`, `concept_registry`, and `thread_trace`.
- `source_ref_from_unit` resolution states such as `matched`, `ambiguous_first_match`, and `fallback_unit_span`.
- `read_audit.jsonl`, `settlement_audit.jsonl`, `unit_span_ledger.jsonl`, and mechanism-private JSON stores.
- `active_recall` and `look_back` context resolution.
- Mechanism-private source skills under `skills/source_skills.py` and `skills/runtime.py`.
- Chapter-end slow-cycle candidate, carry-forward, promotion, withhold, and reaction compatibility paths.
- Active evaluation lanes for user-level selective legibility and Long Span Memory Quality / Spontaneous Callback / False Visible Integration.

## 4. Missing Fields / Contract Gaps

These are the implementation-relevant gaps that should drive later briefs:

| Gap | Current behavior | Why it matters | Likely slice |
| --- | --- | --- | --- |
| Per-op settlement outcome | Settlement audit records aggregate deltas, not one outcome per op. | Cannot tell accepted, transformed, skipped, failed, or deferred ops apart. | Slice 1 |
| Source-binding outcome per op | SourceRef resolution exists, but the result is not tied to each memory op outcome. | Weak/fallback evidence can become indistinguishable from exact grounding. | Slice 1 |
| Operation admission result | Unknown operations can be skipped during normalization; missing target store defaults to `active_attention`. | Hides schema drift and prompt-output mistakes. | Slice 1 / Slice 2 |
| `resolve` allowlist mismatch | Schema and settlement know `resolve`; node normalization allowlist omits it. | Accepted schema intent can disappear before settlement. | Slice 2 |
| Missing `target_store` default policy | Missing target store becomes `active_attention` in `nodes.py`. | Can silently rewrite write intent. | Slice 1 / Slice 2 |
| Legacy-tolerant parse marker | No first-class marker says an op was tolerated for compatibility. | Additive migration needs visibility before strict rejection. | Slice 1 |
| Current-support vs lineage projection | Projection compacts state but does not make this distinction first-class. | Prompts can overuse stale lineage as live support. | Slice 3 |
| Visible-trace marker for reactions | Recent reactions are projected but not strongly marked as visible traces only. | Prevents treating reactions as semantic memory. | Slice 3 |
| Warrant marker for knowledge activations | Knowledge activations exist but projection could label warrant/source-truth boundaries better. | Prevents knowledge activation from becoming source truth. | Slice 3 |
| Retrieval utilization trace | `look_back` / `active_recall` return context, but returned vs used items are not tracked. | Memory retrieval quality cannot be debugged from final prose. | Slice 4 |
| Planning trace hardening | Navigation trace exists but lacks stable fields for source scent, value/cost, and restore-mainline reason. | Detours and callbacks need auditable why/why-not traces. | Slice 5 |
| Slow-cycle candidate vs settled envelope | Slow-cycle has candidates and decisions, but not a dedicated audit envelope. | Prevents safe C设计8 implementation without overbuilding a planner. | Slice 6 |
| Minimal planning/slow-cycle eval fixtures | Evaluation lanes exist; planning/slow-cycle minimal suite is not implemented as a first-class fixture set. | Should wait until instrumentation has stable fields. | Slice 7 |

## 5. Test Availability

Existing useful test/eval assets:

- `reading-companion-backend/tests/test_long_span_vnext.py` covers Long Span vNext report and reuse contracts.
- `reading-companion-backend/tests/test_attentional_v2_knowledge.py` covers current knowledge activation behavior.
- User-level selective v1 docs and runner define the current local/user-level benchmark lane.
- Long Span docs and runner define current Memory Quality / Spontaneous Callback / False Visible Integration diagnostics.

Tests likely needed during later implementation PRs:

- node normalization tests for `resolve`, unknown ops, malformed ops, and missing `target_store`;
- source binding tests for exact, ambiguous, missing quote, and quote-not-found outcomes;
- settlement audit shape tests for per-op accepted/skipped/failed/deferred outcomes;
- state operation tests for target-store-specific admission and legacy compatibility;
- projection tests for current-support, lineage, visible-trace, and warrant markers;
- retrieval trace tests for intent, returned items, used items, ignored items, and no-use reasons;
- planning trace tests for detour value/cost, source scent, defer reason, and restore-mainline reason;
- slow-cycle audit tests for candidate set, settlement event, withhold, not-carried, and carry-forward deltas;
- minimal evaluation smoke tests after core instrumentation is stable.

No tests were run for this audit because no implementation code changed and this task explicitly excludes test/eval execution.

## 6. Risk Ranking

| Rank | Risk | Why | Mitigation |
| --- | --- | --- | --- |
| High | Tightening validation changes runtime behavior too early. | Existing artifacts and LLM outputs may rely on tolerant parsing. | Add audit markers first; only reject after human-approved brief. |
| High | Missing `target_store` default hides write-intent bugs. | It can convert ambiguous ops into active-attention state. | Record compatibility default outcome before changing rejection policy. |
| High | `resolve` mismatch causes accepted operation intent to vanish. | Schema says valid; normalizer can drop it. | Align schema/node allowlist in a small, tested slice. |
| High | Slow-cycle becomes a general planner or memory manager. | C设计8 is broad and tempting to over-implement. | Keep Slice 6 audit-first; no manager/planner agent. |
| Medium | Projection labels become too large and prompt-heavy. | More context metadata can crowd actual reading context. | Prefer compact markers and bounded packets. |
| Medium | Retrieval trace changes evaluation assumptions. | New audit artifacts may affect downstream report readers. | Keep additive fields and tolerant readers. |
| Medium | Evaluation expands before instrumentation stabilizes. | Scores would diagnose missing audit surfaces rather than mechanism quality. | Keep full AI Evaluation deferred. |
| Low | README/ledger references drift. | Process docs are easy to patch. | Update ledger and task registry with each phase transition. |

## 7. Provisional PR Order

This is a provisional order for human review. It is not an accepted PR plan.

1. Slice 1 / Contract and Audit Foundations
   - Add additive per-op validation, source-binding, and settlement outcome audit fields.
   - Add tolerant readers and tests for audit row shape.
   - Preserve current runtime behavior unless explicitly accepted otherwise.

2. Slice 2 / Memory Formation and Settlement Hardening
   - Align `resolve` vocabulary across schema, node normalization, prompt contract, and settlement.
   - Add missing `target_store` compatibility marker or rejection behavior according to human decision.
   - Harden store-specific admission for `active_attention`, `concept_registry`, and `thread_trace`.

3. Slice 3 / Memory Lifecycle and Projection Hardening
   - Add compact markers for current support, lineage, visible reaction trace, and knowledge activation warrant.
   - Keep `reaction_records` out of semantic memory.
   - Keep `knowledge_activations` out of source truth.

4. Slice 4 / Retrieval and Utilization Instrumentation
   - Add trace fields for retrieval intent, returned items, used items, ignored items, and no-use reasons.
   - Keep retrieval instrumentation separate from broad RAG redesign.

5. Slice 5 / Planning Trace, Detour, Recall, and Look-back Hardening
   - Harden trace fields for source scent, detour value/cost, defer reason, restore-mainline reason, and continuity budget.
   - Preserve existing source-skill boundary and no-future-text rule.

6. Slice 6 / Slow-cycle Safety
   - Add audit-first candidate and settlement envelopes for chapter-end slow-cycle behavior.
   - Track promote, withhold, not-carried, carry-forward, and capsule deltas.
   - Do not add a planner agent, memory-manager agent, or prompt self-refiner.

7. Slice 7 / Minimal Eval Implementation Slice
   - Add minimal contract/eval smoke only after core instrumentation is stable.
   - Keep Local/User-level Selective Legibility and Long Span MQ / Callback / FVI as the two evaluation lanes.

8. Slice 8 / Post-implementation Review and Eval Readiness
   - Review implementation evidence.
   - Decide whether full AI Evaluation is justified.
   - Promote stable behavior changes to stable docs only after implementation lands.

## 8. Open Questions

```text
Question:
Should missing target_store be rejected immediately or tolerated with an audit marker first?

Recommended default:
Tolerate initially with a compatibility/audit marker, then tighten after artifact compatibility is understood.

Human confirmation needed:
yes
```

```text
Question:
Should resolve be added to the nodes.py operation allowlist or removed from the schema?

Recommended default:
Add resolve to the nodes.py allowlist and test store-specific settlement behavior, because schema and state_ops already recognize resolve.

Human confirmation needed:
yes
```

```text
Question:
Should projection introduce formal fields named current_support_projection and lineage_projection, or start with lighter markers?

Recommended default:
Start with compact markers inside the existing packet shape unless the first implementation brief proves a stronger field boundary is needed.

Human confirmation needed:
yes
```

```text
Question:
Should slow-cycle typed envelopes be introduced in Slice 1 or wait until Slice 6?

Recommended default:
Wait until Slice 6. Slice 1 should only ensure the shared audit foundation can support later slow-cycle rows.

Human confirmation needed:
yes
```

```text
Question:
How much legacy artifact compatibility should be preserved?

Recommended default:
Use additive fields and tolerant readers in early PRs; avoid deleting or rewriting existing artifacts in the first pass.

Human confirmation needed:
yes
```

## 9. Human Review Gate

Current phase after this document: waiting for human review.

Reviewer options:

- Accept E实施1 and authorize a Pre-implementation Brief for Slice 1 / Contract and Audit Foundations.
- Accept with patch, specifying field names, validation posture, or PR-order adjustments.
- Block implementation if stable docs need an additional promotion pass before code work.

Codex must not start implementation, create an implementation PR, or run full AI Evaluation until this audit is accepted.
