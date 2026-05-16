# E实施0-Implementation Roadmap & Handoff v0

## 0. Executive Decision

设计阶段到这里应视为**基本完成**。C设计0–9 已经足够进入 implementation roadmap / handoff，不继续扩写 C设计10 / C设计11，不继续发散新 Memory、Planning 或 Evaluation 设计。

下一步不是直接让 Codex 改代码，而是让 Codex 先做 **Code-grounded Feasibility & Delta Audit**：把 C设计0–9 的契约逐项对照真实 repo 文件、字段、测试与风险，输出 delta matrix 和 PR 顺序。之后再进入小 PR、分阶段、可回滚实现。

实施策略为：

- 先补 contract / audit foundations；
- 再收紧 read-path memory formation；
- 再做 lifecycle / projection / retrieval / planning trace / slow-cycle safety；
- 早期只跑 engineering tests 和 contract smoke；
- full AI Evaluation 在核心机制落地并有足够 instrumentation 后集中跑一次；
- formal / larger eval 等稳定后再决定。

本 handoff 的目标是让项目从“继续设计”切换到“分阶段、可审计、可回滚实施”。

------

## 1. Scope and Non-goals

本文档是：

- implementation roadmap；
- C设计0–9 的实施压缩 handoff；
- implementation sequencing；
- slice dependency plan；
- contract / audit / smoke gate definition；
- Codex feasibility audit briefing。

本文档不是：

- 新设计文档；
- C设计10 / C设计11；
- Codex task list；
- 直接代码实现；
- PR diff；
- full evaluation framework；
- UI / route disclosure UX design；
- benchmark redesign；
- Memory OS / Planning OS 设计；
- 工程测试详细计划。

本文档的读者是：准备做 code-grounded audit、拆 PR、补测试、做 reviewer gate 的实现团队。

------

## 2. Accepted Design Source Map

权威顺序固定为：

1. 当前 GitHub repo：判断当前实现事实；
2. C设计0 Shared Charter：最高机制边界；
3. C设计1–9 accepted design chain：实施来源；
4. B分析 Memory / Planning：问题背景与复杂度边界；
5. A调研 external evidence packs：背景，不进入 roadmap 主体；
6. D审核文档：historical review，不作为权威输入。

| Design doc                                | Implementation role            | Key contracts to preserve                                    | Direct implementation relevance                             |
| ----------------------------------------- | ------------------------------ | ------------------------------------------------------------ | ----------------------------------------------------------- |
| C设计0 Shared Charter                     | 最高边界                       | `LLM proposes; deterministic runner settles`; source corpus / memory / planning state / audit / visible reaction / eval evidence 分层；no vector DB / graph DB / big planner by default | 所有 slice 的边界检查；尤其防止 Codex 过度实现              |
| C设计1 Memory Ontology                    | store 身份边界                 | `active_attention` hot state；`concept_registry` concept/object/definition；`thread_trace` development line；`reflective_frames` slow-cycle promoted；`reaction_records` visible trace；`knowledge_activations` warrant ledger | Slice 2–4 的 admission、projection、warning markers         |
| C设计2 Planning Ontology                  | planning 语义边界              | Planning = source-grounded reading path planning / attention scheduling；不是 AutoGPT task planning；`local_continuity` 是 v0 planning carrier | Slice 5 的 trace hardening；防止新增 general planner        |
| C设计3 Memory Formation & Settlement      | read-path write contract       | `memory_uptake_ops` 是 bounded write intent；Read 只 propose；Runner / settlement 才 settle；SourceRef binding 是核心 | Slice 1–2 的主要实现来源                                    |
| C设计4 Navigation Policy                  | Navigate 决策纪律              | mainline continuity default；detour bounded exception；source skill 是 evidence layer；no future text；no route disclosure owner | Slice 5 的 navigation trace / detour gate                   |
| C设计5 Memory Management & Evolution      | lifecycle 语义                 | visibility lifecycle ≠ semantic validity；cooling ≠ invalidation；supersede ≠ overwrite；reaction / knowledge 不得 semanticize | Slice 3 的 lifecycle / projection hardening                 |
| C设计6 Detour / Look-back / Active Recall | 三机制分工                     | active_recall = memory recovery；look_back = source calibration；detour = path deviation；failed look-back 不得由 memory confidence 静默替代 | Slice 4–5 的 retrieval/use trace 与 detour restore gate     |
| C设计7 Memory Retrieval & Utilization     | retrieval/utilization contract | retrieval intent-aware；retrieval hit ≠ utilization success；current support vs lineage；items_returned / items_used / no_use_reason | Slice 4 的最小 instrumentation                              |
| C设计8 Slow-cycle / Macro-planning        | slow-cycle safety 来源         | **未找到 standalone C设计8 文件**；本 handoff 只使用 C设计路线、C设计9 和用户给定 slice 范围中的 C8 intent：candidate vs settled、promotion evidence、carry-forward safety | Slice 6；Codex audit 必须继续查 repo / docs 目录是否存在 C8 |
| C设计9 Evaluation Calibration             | eval strategy                  | 保留 user-level selective 与 Long Span MQ / Callback / FVI 两条 lane；Planning / Slow-cycle 只轻量补 trace-quality / safety；engineering tests 与 AI Eval 分离 | Slice 7–8；决定何时跑 smoke / full eval                     |

------

## 3. Current Implementation Snapshot

### 3.1 Repo-level 当前事实

当前 repo 是 Reading Companion workspace，产品定位是一个 text-grounded、legible、self-propelled 的共读心智，而不是摘要器或服务型助手。机制层当前默认是 `attentional_v2`，`iterator_v1` 是 fallback / legacy-compatible path。共享 source truth 是 `public/book_document.json`，当前 `attentional_v2` 使用 paragraph + char-offset cursor 和 inline paragraph-offset `SourceRef`，没有 shared Anchor Bank / SourceRef registry。

当前 live loop 已经是：

```text
survey / reading_plan orientation
→ Navigate.choose_next_unit
→ Read
→ Reading Runner post-read settlement
→ cursor advance / unit span ledger / audit
→ chapter/session slow-cycle
```

`attentional_v2` 文档和 runner 代码都支持这个判断：Runner owns Navigate、Read、settlement、cursor advancement、detour state handoff 和 mechanism-private runtime persistence。

### 3.2 已实现

- **Source cursor / SourceSpan / SourceRef**：`source_spans.py` 已有 paragraph-offset `SourceCursor`、end-exclusive `SourceSpan`、exact quote → `SourceRef` binding、quote fallback marker、end-anchor resolution、accepted unit construction。
- **Navigate / Read / Runner skeleton**：`Navigate.choose_next_unit` 支持 mainline 和 detour mode；mainline 使用 exact `end_anchor_text`；detour mode 可 request bounded source skills / choose source-grounded unit / defer。
- **Read output contract**：`ReadUnitResult` 包含 `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`。
- **Memory stores**：`active_attention / concept_registry / thread_trace / reflective_frames / knowledge_activations / reaction_records / reconsolidation_records` schema 与 runtime artifacts 已存在。
- **state_ops apply layer**：active attention、concept、thread、reaction、reconsolidation、reflective supersede 都有 deterministic apply helper；source refs 会 merge / dedupe；reflective supersede 不 destructive overwrite statement。
- **state_projection**：已有 bounded `state_packet.v1`，包括 active_attention digest、concept digest、thread digest、reflective digest、recent reactions、source_ref digest、continuation capsule。
- **read_context active_recall / look_back**：`look_back` 可根据 SourceRef / SourceSpan 返回 earlier source excerpt；`active_recall` 可从 concept/thread/reaction records 返回未 carry 的 state。
- **detour / local_continuity**：`local_continuity` 已有 `mainline_cursor / reading_queue_stage / active_detour_id / active_detour_need / detour_trace`；runner 可 open / resolved / abandoned detour。
- **source skills**：用户要求的 `reading-companion-backend/src/attentional_v2/source_skills.py` 不存在；实际当前路径是 `reading-companion-backend/src/attentional_v2/skills/source_skills.py`。该实现只允许 already-read / visible-to-mainline source scope，future range 会被拒绝。
- **storage / audit**：file-based JSON / JSONL artifacts 已存在，包括 runtime state、unit ledger、read audit、settlement audit、probe export。
- **evaluation assets**：repo 已有 active user-level selective lane、active Long Span direction、Phase-1 long-span runner、probe export、semantic probe manifest、reaction audit、evidence catalog。

### 3.3 部分实现 / 需要 hardening

- **settlement audit**：当前 `record_settlement()` 有 compact transaction summary 和 state ID delta，但还没有 per-op outcome、source-binding result、failure / defer reason。
- **operation normalization**：`schemas.py` 的 `StateOperationType` 包含 `resolve`，但 `nodes.py` 的 `_STATE_OPERATION_TYPES` 当前没有列出 `resolve`；此外，缺失 `target_store` 时 normalization 会默认到 `active_attention`。这是 design intent 与 current implementation fact 的明确冲突。
- **retrieval utilization trace**：`read_context.py` 已有 active_recall / look_back，但还没有 intent label、status-aware filtering、items_returned vs items_used、no_use_reason、utilization trace。
- **projection status semantics**：projection 有 digest 和 SourceRef，但还没有显式 current_support_projection vs lineage_projection、stale/superseded/rejected warning marker。
- **detour trace**：detour trace 有 open/resolved/abandoned，但 source_scent、detour_value、continuity_cost、restore-mainline reason、defer reason、budget stop reason 仍不足。
- **slow-cycle safety**：slow-cycle 已有 reaction persistence、reflective promotion、reconsolidation、chapter consolidation 等，但 C8 所要求的 candidate vs settled、promotion evidence、withhold reason、carry-forward delta 等需要 Codex code audit 后确认具体 delta。
- **evaluation**：Long Span vNext runner 与 tests 已存在；但 Planning Trace Quality、Slow-cycle Safety、instrumentation coverage audit 还未形成最小 eval slice。

### 3.4 缺失 / 不清楚

- **C设计8 standalone 文件未找到**：GitHub search 没找到 `C设计8 Slow-cycle / Macro-planning Design v0` 或 `Slow-cycle Macro-planning`，当前上传文件中也没有 standalone C8。本文对 C8 的实现角色只基于 C设计路线、C设计9 与用户给定 implementation slice，不假设 C8 正文细节。
- **runtime artifact audit 未做**：本文没有逐行读取真实运行目录中的 `read_audit.jsonl / settlement_audit.jsonl / unit_span_ledger.jsonl / active_attention.json / concept_registry.json / thread_trace.json / reaction_records.json`。因此本文只做 architecture / contract / repo-file-level snapshot，不声称 runtime-quality 已经验证。
- **`run_excerpt_comparison.py` 仍存在**：但 repo evaluation docs 已把 excerpt surface 标为 historical / superseded；它不应重新成为 active lane。
- **task registry 当前已有结构性 rework 线**：repo 任务登记显示 `TASK-ATTENTIONAL-V2-STRUCTURAL-REWORK` 仍是 active，并记录了 paragraph-offset SourceRef cutover、F4A audit、F4B scheduling、detour 未充分验证等事实。

### 3.5 设计意图 vs 当前实现冲突表

| Design intent                                                | Current implementation fact                                  | Implementation risk                      | Recommended handling                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------------- | ------------------------------------------------------------ |
| Read-path missing / illegal `target_store` 应 reject 或 tolerant marker | `_normalize_state_operations` 缺失 `target_store` 时默认 `active_attention` | illegal write silent remap               | Slice 1/2 增加 validation result 与 legacy tolerant parse marker |
| `resolve` 是合法 operation vocabulary                        | schemas 有 `resolve`，nodes allowlist 缺 `resolve`           | prompt/schema/state_ops 不一致           | Codex audit 后小 PR 对齐 allowlist 或收窄 schema             |
| 每个 memory op 应有 outcome                                  | settlement audit 只有 op count、target-store distribution、ID delta | failed/skipped/deferred silent disappear | Slice 1 增加 per-op outcome                                  |
| SourceRef binding 是 formation contract                      | runner 绑定 source_quote 到 SourceRef，但 fallback 可能进入 payload | fallback overtrusted                     | 记录 binding status；semantic writes 对 fallback 做 gate     |
| retrieval hit ≠ utilization success                          | active_recall / look_back 返回 context，但没有 utilization trace | eval 无法定位 retrieval/use failure      | Slice 4 加 retrieval event/use event audit                   |
| reaction_records 不是 semantic memory                        | recent reactions 进入 digest                                 | reaction semanticization                 | projection 加 visible_trace marker / warning                 |
| knowledge activations 不是 source truth                      | knowledge mode 可在 warrant 下变成 plus prior knowledge      | prior knowledge 被误作书中事实           | projection / retrieval 加 warrant marker                     |
| slow-cycle candidate ≠ settled truth                         | slow-cycle 已有 promotion / reconsolidation，但安全 envelope 不清楚 | source-free reflection / silent mutation | Slice 6 先做 candidate/outcome audit，不扩 slow-cycle behavior |

------

## 4. Implementation Principles

1. **Preserve current working skeleton.** 保留 `Navigate.choose_next_unit → Read → Runner settlement`。
2. **Implement contract and audit foundations before behavior expansion.**
3. **Prefer schema / audit / prompt deltas over new infrastructure.**
4. **File-based JSON / JSONL first.**
5. **SourceRef-first.**
6. **Status-aware and intent-aware, but bounded.**
7. **No vector DB / graph DB / Memory OS by default.**
8. **No new planner agent / memory manager agent / retriever agent.**
9. **No full eval during early implementation.**
10. **Engineering tests are Codex responsibility; AI Evaluation is separate.**
11. **Every slice must have rollback / compatibility notes.**
12. **Small PRs over big bang rewrite.**
13. **Audit rows do not enter runtime prompt.**
14. **Visible route disclosure remains explicitly out of scope.**
15. **Do not let C8 absence become design invention.** Codex must verify C8 file existence before implementing C8-specific names.

------

## 5. Implementation Slices Overview

| Slice | Name                                                   | Purpose                                              | Depends on               | Primary files                                                | Output                                      | Gate                                     |
| ----- | ------------------------------------------------------ | ---------------------------------------------------- | ------------------------ | ------------------------------------------------------------ | ------------------------------------------- | ---------------------------------------- |
| 0     | Codex Feasibility & Delta Audit                        | 对照真实代码与设计 contract                          | none                     | all relevant repo files                                      | delta matrix / risk / PR order              | human accepts audit                      |
| 1     | Contract / Audit Foundations                           | 先补可观测性和 per-op contract evidence              | 0                        | `schemas.py`, `runner.py`, `state_ops.py`, `observability.py`, `storage.py`, `source_spans.py` | audit fields / outcome markers              | no silent failed ops                     |
| 2     | Memory Formation & Settlement Hardening                | 收紧 read-path write intent                          | 1                        | `prompts.py`, `nodes.py`, `runner.py`, `state_ops.py`, `source_spans.py` | allowed-store / source-binding / validation | Read only propose; Runner settles        |
| 3     | Memory Lifecycle / Projection Hardening                | lifecycle + status-aware projection                  | 1–2                      | `schemas.py`, `state_ops.py`, `state_projection.py`, `knowledge.py`, `storage.py` | current support vs lineage markers          | stale rejected cannot be current support |
| 4     | Retrieval / Utilization Instrumentation                | intent-aware retrieval trace                         | 1–3                      | `read_context.py`, `state_projection.py`, `runner.py`, `observability.py` | retrieval/use audit                         | hit ≠ use                                |
| 5     | Planning Trace / Detour / Recall / Look-back Hardening | path control audit hardening                         | 1–4                      | `runner.py`, `nodes.py`, `prompts.py`, `skills/source_skills.py`, `read_context.py` | detour/restore/budget trace                 | bounded detour, auditable restore        |
| 6     | Slow-cycle Safety                                      | candidate vs settled; promotion/carry-forward safety | 1–5                      | `slow_cycle.py`, `state_ops.py`, `state_projection.py`, `knowledge.py`, `observability.py` | promotion/withhold/carry audit              | candidate not durable truth              |
| 7     | Minimal Eval Implementation Slice                      | 保留并轻调现有 eval assets                           | 1–6 core instrumentation | eval docs/runners/judge prompts/catalog                      | smoke + minimal suite readiness             | lanes preserved                          |
| 8     | Post-implementation Review & Eval Readiness            | 判断是否跑 Minimal Eval Suite                        | 1–7                      | docs/eval/runtime outputs                                    | readiness checklist                         | full eval only after core                |

------

## 6. Slice 0 — Codex Feasibility & Delta Audit

这是 Codex 的下一步，**不写代码**。

Codex 应验证：

- proposed changes 对应哪些真实文件；
- 哪些字段已存在；
- 哪些字段缺失；
- 哪些改动最小；
- 哪些改动风险最大；
- 哪些测试可复用；
- 哪些设计假设不符合代码现实；
- C设计8 standalone 是否存在；
- 推荐 PR 顺序。

Codex 输出：

```text
affected files matrix
current vs target delta
fields already present
missing fields
implementation risk notes
test availability
proposed PR slices
open questions
assumptions needing human confirmation
```

Gate：human reviewer 接受 feasibility audit 后，才进入代码实现。

------

## 7. Slice 1 — Contract / Audit Foundations

目标：先补可观测性和 contract evidence，避免后续行为变化不可诊断。

范围：

- SourceRef binding result markers；
- per-op settlement outcome；
- `target_store / operation` validation result；
- `source_refs_used / memory_refs_used`；
- warning markers；
- `failure_reason / defer_reason`；
- compact audit deltas；
- audit 不进入 runtime prompt。

可能影响文件：

```text
schemas.py
source_spans.py
runner.py
state_ops.py
observability.py
storage.py
prompts.py only if needed
```

Non-goals：

- 不改变大行为；
- 不新增完整 evaluation；
- 不做 retrieval ranking；
- 不做 lifecycle overhaul。

Engineering tests by Codex：

```text
malformed op
missing target_store
illegal target store
missing source quote
quote fallback
audit row shape
backward compatibility
```

Contract gate：

- 每个 memory op 有可追踪 outcome；
- failed / skipped / deferred 不 silent disappear；
- audit row compact；
- audit 不进入 runtime prompt；
- existing run artifacts 读写不被破坏。

Rollback / compatibility：

- 新 audit fields additive；
- old audit readers tolerant；
- no prompt behavior change unless required.

------

## 8. Slice 2 — Memory Formation & Settlement Hardening

目标：落实 C设计3 的 read-path write intent contract。

范围：

- `memory_uptake_ops` 明确作为 bounded write intent；
- explicit allowed target stores；
- operation validation；
- `source_quote → SourceRef` binding；
- payload normalization before `state_ops`；
- legacy tolerant parse marker；
- unknown target / op rejection；
- read-path cannot write reflective / reaction / audit / evaluation / planning stores；
- `resolve` schema / nodes allowlist 对齐。

可能影响文件：

```text
prompts.py
nodes.py
schemas.py
runner.py
state_ops.py
source_spans.py
observability.py
```

Gate：

- Read 只 propose；
- Runner / settlement settles；
- accepted writes are SourceRef-aware where needed；
- rejected writes are auditable；
- missing `target_store` 不再 silent default 成普通 accepted op。

Rollback / compatibility：

- 先允许 legacy tolerant parse；
- marker 进入 audit；
- 逐步 tighten，不直接破坏历史 outputs。

------

## 9. Slice 3 — Memory Lifecycle / Projection Hardening

目标：落实 C设计5 的 lifecycle semantics 与 C设计7 的 status-aware projection。

范围：

- visibility vs semantic validity markers；
- cooling ≠ invalidation；
- resolve ≠ permanent completion；
- supersede ≠ destructive overwrite；
- retire / invalidated / rejected / lineage-only markers；
- `current_support_projection` vs `lineage_projection`，或等价命名；
- reaction_records `visible_trace` marker；
- knowledge_activations `warrant` marker；
- stale / superseded / rejected warning markers；
- projection filtering rules。

可能影响文件：

```text
schemas.py
state_ops.py
state_projection.py
storage.py
observability.py
knowledge.py
prompts.py if projection labels need prompt support
```

Gate：

- stale / superseded / rejected memory cannot be used as current support without marker；
- reaction records are not semantic memory；
- knowledge activations are not source truth；
- no destructive overwrite；
- source refs preserved across update / carry-forward.

Rollback / compatibility：

- marker additive；
- old statuses tolerated；
- projection defaults conservative.

------

## 10. Slice 4 — Retrieval / Utilization Instrumentation

目标：落实 intent-aware retrieval 和 utilization trace 的最小版本。

范围：

- retrieval_intent labels；
- `continuity_carry`；
- `active_recall`；
- `look_back_support`；
- `detour_support`；
- `slow_cycle_consolidation`, if needed；
- `items_returned`；
- `items_claimed_used`；
- `items_evidenced_used`, if feasible；
- `source_refs_returned / source_refs_used`；
- `memory_refs_returned / memory_refs_used`；
- `no_use_reason`；
- status / warning markers；
- budget / stop reason。

可能影响文件：

```text
read_context.py
state_projection.py
runner.py
observability.py
schemas.py
prompts.py
source_spans.py
```

Non-goals：

- no vector DB；
- no graph DB；
- no ranking model；
- no retriever agent；
- no broad RAG pipeline。

Gate：

- retrieval hit is not treated as successful utilization；
- failed look_back is not replaced by memory confidence；
- audit can explain what was retrieved and whether it was used；
- lineage / reaction / knowledge items carry warning markers.

Rollback / compatibility：

- existing active_recall / look_back outputs preserved；
- add trace sidecar first；
- no broad retrieval behavior change in this slice.

------

## 11. Slice 5 — Planning Trace / Detour / Recall / Look-back Hardening

目标：让 planning path control 更可审计，不增强成大 planner。

范围：

- detour open / defer / abandon / resolve reason；
- restore-mainline reason；
- source_scent / detour_value / continuity_cost markers；
- active_recall_needed / look_back_needed as support/audit flags；
- request_skill reason；
- skill result provenance；
- budget / stop reason；
- no future text guardrails；
- route trace fields。

可能影响文件：

```text
schemas.py
runner.py
nodes.py
prompts.py
skills/source_skills.py
skills/runtime.py
source_spans.py
read_context.py
observability.py
storage.py
```

Non-goals：

- no new planner；
- no user route choice；
- no route disclosure UI；
- no multi-detour queue unless already supported safely；
- no full navigation rewrite；
- no expansion beyond current accepted Navigate act space unless Codex audit proves necessity。

Gate：

- detour remains bounded；
- mainline restoration is auditable；
- active recall / look-back are not confused；
- Navigate act space remains `choose_unit / request_skill / defer_detour` unless explicitly approved；
- source skills remain book-local and bounded by mainline cursor。

Rollback / compatibility：

- trace fields additive；
- detour behavior unchanged before audit validates fields；
- no new surface exposed to user.

------

## 12. Slice 6 — Slow-cycle Safety

目标：落实 C设计8-style 的 candidate vs settled、promotion safety、carry-forward safety。

注意：standalone C设计8 未找到。此 slice 只实现 C设计路线 / C设计9 / 用户 handoff 中明确要求的 minimal slow-cycle safety，不引入 C8 未确认术语。

范围：

- `SlowCycleCandidateSet` or equivalent candidate envelope；
- `SlowCycleSettlementEvent` or equivalent settlement envelope；
- `trigger_type` logging；
- session boundary lightweight behavior；
- reflective promotion evidence markers；
- `withhold_promotion` reason；
- `not_carried` reason；
- active_attention carry_forward / not_carried audit；
- reconsolidation reason；
- knowledge activation review markers；
- detour continuity summary；
- `continuation_capsule_delta`。

可能影响文件：

```text
slow_cycle.py
prompts.py
schemas.py
state_ops.py
state_projection.py
knowledge.py
observability.py
storage.py
runner.py
```

Non-goals：

- no per-unit reflection；
- no general planner；
- no memory manager agent；
- no source-free reflection；
- no chapter summary dump；
- no broad full-store prompt dump。

Gate：

- promotion has supporting SourceRefs；
- withhold is valid and auditable；
- candidate is not durable truth；
- slow-cycle does not silently mutate stores outside canonical application path where feasible；
- reaction / knowledge boundary remains intact.

Rollback / compatibility：

- first PR can be audit-only envelopes；
- no broad slow-cycle behavior expansion；
- promotion behavior tightened only after smoke.

------

## 13. Slice 7 — Minimal Eval Implementation Slice

目标：保留现有 eval 资产，只做最小必要调整。

必须保留两条 eval lane。

### Lane A：Local / User-level Selective Legibility

保留：

- high-value human-note-aligned source spans；
- visible reaction source locator；
- note recall；
- `focused_hit / incidental_cover / miss`；
- strict source-span overlap first；
- old excerpt surface is historical；
- active goal remains user-level selective v1。

repo 当前 user-level selective docs 明确：active metric 是 note recall over aligned human notes；candidate retrieval 必须 strict source-span overlap，text / semantic similarity 不 admit candidates；visible reactions without usable source locator fail the run。

### Lane B：Long Span MQ / Callback / FVI

保留：

- Memory Quality；
- Spontaneous Callback；
- False Visible Integration；
- semantic probe manifest；
- reaction audit；
- utilization trace alignment if available。

repo 当前 long-span docs 明确：active direction 是 Memory Quality / Spontaneous Callback / False Visible Integration，Phase-1 implementation 已 landed，但不是 formal benchmark authority。

轻量新增：

- Planning Trace Quality, audit-first；
- Slow-cycle Safety, small sampled cases；
- instrumentation coverage audit。

可能影响文件：

```text
evaluation docs
eval runners
judge prompts
evidence catalog
observability outputs
probe snapshot exporters
tests only as engineering validation
```

Non-goals：

- no new giant benchmark；
- no broad metric taxonomy；
- no full eval platform rewrite；
- no full eval before core implementation；
- no engineering test plan in this slice。

Gate：

- existing eval lanes preserved；
- MQ / Callback / FVI remain；
- user-level selective remains；
- diagnostic tags do not become many independent scores；
- evaluation remains separate from engineering tests；
- old excerpt runner remains historical unless explicitly used for compatibility/historical report.

------

## 14. Slice 8 — Post-implementation Review & Eval Readiness

目标：核心 slices 落地后，判断是否准备跑 Minimal Eval Suite。

必须检查：

- engineering tests pass；
- contract / audit rows exist；
- SourceRef evidence is preserved；
- utilization trace is sufficient；
- detour restore reasons exist；
- slow-cycle promotion / withhold evidence exists；
- eval runners can consume needed artifacts；
- evidence catalog update path still works。

节奏：

```text
early slices:
  engineering tests + contract smoke only

middle slices:
  small behavior smoke only

after core slices:
  Minimal Eval Suite

after stability:
  formal eval / larger benchmark, if needed
```

Full eval 不应在每个 slice 后跑。

------

## 15. Cross-slice Dependency Order

顺序不能乱，原因如下：

- **audit foundations before behavior changes**：否则 failure 无法定位。
- **formation before lifecycle / retrieval**：否则取回和演化的对象不稳定。
- **lifecycle before status-aware retrieval**：否则 stale / superseded / rejected 无法过滤。
- **retrieval instrumentation before callback / FVI utilization eval**：否则只能看 visible output，不能判断 memory 是否真的被使用。
- **planning trace before planning eval**：否则 Navigation Groundedness / Detour Recovery 没有 evidence substrate。
- **slow-cycle safety before slow-cycle eval**：否则 promotion / withhold / not_carried 无法判断。
- **minimal eval after instrumentation exists**：否则 eval 只会暴露“缺证据”，不是机制质量。

------

## 16. Quality Gates

### Engineering Test Gate

由 Codex 负责：

```text
unit tests
schema tests
integration smoke
malformed input tests
backward compatibility tests
CI
runner/eval runner contract tests
storage JSON/JSONL shape tests
```

Engineering tests 证明代码按契约运行，不证明产品质量。

### Contract / Audit Gate

由 reviewer 重点看：

```text
SourceRef preserved
per-op outcome present
candidate vs settled separated
no audit dump into prompt
no reaction semanticization
no knowledge activation source-truth
no silent overwrite/drop
no unauthorized store write
failed/skipped/deferred auditable
fallback SourceRef marked
```

### Behavior Smoke Gate

只跑极少量样本：

```text
1–2 local/user-level selective cases
1–2 MQ / Callback / FVI cases
1 detour / restore-mainline case
1 slow-cycle promotion / withhold case
```

Smoke 只验证机制没明显破坏，不当作正式产品评价。

------

## 17. Evaluation Strategy During Implementation

明确策略：

- 不在每个 phase 后跑完整 eval；
- 不在核心机制落地前跑大 long-span；
- 不重建 benchmark；
- 不新增大量指标；
- 保留现有 user-level selective 和 long-span lanes；
- full Minimal Eval Suite 在核心 slices 后跑一次；
- formal eval / larger benchmark 等稳定后再决定；
- engineering tests 不等于 AI Evaluation；
- contract / audit checks 是 eval substrate，不是产品质量分数。

当前 repo 的 evaluation constitution 也明确：评估是 product-first、mechanism-agnostic，活跃 long-span direction 是 Memory Quality / Spontaneous Callback / False Visible Integration，且 active local benchmark 是 user-level selective。

------

## 18. Codex Handoff Instructions

Codex 下一步不是直接写代码，而是做：

```text
Code-grounded Feasibility & Delta Audit
```

Codex 应输出：

1. **design-to-file delta matrix**
   每条 C设计 contract 对应哪些真实文件、字段、函数、prompt、audit row。
2. **fields already present**
   例如 `SourceRef`、`StateOperationType`、`NavigateActTraceEntry`、`read_audit`、`settlement_audit`、`local_continuity` 已有哪些字段。
3. **missing fields**
   例如 per-op outcome、source binding outcome、utilization trace、restore-mainline reason、promotion withhold reason。
4. **minimal code changes**
   每个 slice 的最小 additive change。
5. **risk ranking**
   高风险：schema migration、prompt bloat、silent behavior change、eval runner breakage。
6. **tests available**
   复用哪些 existing tests；新增哪些 unit/schema/smoke tests。
7. **proposed PR order**
   保持小 PR，不一次性实现所有 slice。
8. **assumptions needing human confirmation**
   尤其 C设计8 是否存在、field naming 是否可定、legacy artifact compatibility 是否保留。

Feasibility audit 被 human reviewer 接受后，再进入第一轮实现 PR。

------

## 19. Deferred / Explicitly Not Now

| Item                                        | Why not now                                                  |
| ------------------------------------------- | ------------------------------------------------------------ |
| C设计10 / C设计11 full pages                | C设计9 已足够进入 implementation；继续写会延迟落地           |
| Visible Reading Route Surface UX            | 当前只保留 trace / audit；不做 user-facing route controls    |
| vector DB                                   | 当前瓶颈是 contract/audit/source-ref，不是 similarity infra  |
| graph DB                                    | 先用 JSON links / source_refs / supersede chain              |
| Memory OS                                   | 产品不是通用 memory runtime                                  |
| retriever agent                             | retrieval 应 intent-aware and bounded，不新增 agent          |
| memory manager agent                        | management 是 lifecycle contract，不是新 actor               |
| general planner                             | Planning 是 reading path control，不是 AutoGPT task planning |
| multi-agent reading team                    | 产品需要一个连贯 co-reader mind                              |
| full benchmark redesign                     | 现有两条 lane 保留，只补最小 diagnostic                      |
| full formal eval before core implementation | instrumentation 未落地前大 eval 只会制造噪声                 |
| user route choice                           | Second Reader is independent reader                          |
| route steering UI                           | 当前不做 visible route disclosure surface                    |
| broad RAG pipeline                          | source corpus / memory / look-back 已分层，不做泛化 RAG      |
| per-unit reflection                         | slow-cycle 才能做高层 consolidation                          |
| source-free reflective truth                | promotion 必须有 SourceRef / settled support                 |
| ToT / MCTS default loop                     | 普通阅读不需要高成本 search-based deliberation               |
| full snapshot per unit audit                | compact audit + per-op outcome 更合适                        |

------

## 20. Risks and Rollback Notes

| Risk                                           | Mitigation                                                   |
| ---------------------------------------------- | ------------------------------------------------------------ |
| audit field explosion                          | 只加 gate 必需字段；compact rows；debug-only detail 分层     |
| schema migration breaking old artifacts        | additive fields；tolerant readers；legacy marker；avoid deleting old keys early |
| prompt bloat                                   | 优先 audit/schema deltas；prompt only if behavior contract requires |
| eval over-expansion                            | 保留两条 lane；Planning/Slow-cycle 只 diagnostic tags        |
| slow-cycle overreach                           | candidate envelope first；no source-free promotion；withhold is valid |
| hidden behavior changes                        | 每个 PR 标注 behavior/non-behavior；contract smoke           |
| SourceRef fallback overtrusted                 | binding status/warning marker；semantic stores stricter than active_attention |
| reaction misuse                                | visible_trace marker；projection warning；no automatic semantic promotion |
| knowledge misuse                               | warrant marker；not source truth；requires source evidence for concept writes |
| Codex implementing too much at once            | enforce slice PR order；reviewer rejects big-bang PR         |
| C8 absence causing invention                   | Codex must locate C8 or mark absent; implement only confirmed minimal slow-cycle safety |
| engineering tests confused with AI Eval        | separate test gate vs behavior smoke vs eval suite           |
| current eval runners broken by instrumentation | eval runner smoke before full eval; keep artifacts backward compatible |

------

## 21. Output Format / Handoff Close

本文件的 implementation stance 是：

```text
Stop expanding design.
Do feasibility audit.
Implement contract gates first.
Move in small PRs.
Run engineering tests early.
Run AI Evaluation late.
```

### Recommended next action for Codex

Codex 先做 **Code-grounded Feasibility & Delta Audit**，覆盖：

```text
schemas.py
nodes.py
prompts.py
runner.py
state_ops.py
state_projection.py
read_context.py
source_spans.py
skills/source_skills.py
skills/runtime.py
slow_cycle.py
knowledge.py
observability.py
storage.py
evaluation docs/runners/tests
```

并明确报告：

- C设计8 是否存在；
- `source_skills.py` 路径差异；
- `resolve` schema / nodes allowlist delta；
- missing `target_store` default behavior；
- per-op settlement outcome gap；
- retrieval utilization trace gap；
- slow-cycle candidate vs settled gap。

### First three PR slices likely to implement

1. **PR 1：Contract / Audit Foundations**
   Additive audit shape、per-op outcome skeleton、binding/validation markers、backward-compatible readers。
2. **PR 2：Memory Formation & Settlement Hardening**
   Allowed target-store gate、operation validation、SourceRef binding outcome、legacy tolerant parse marker、unknown op/store rejection。
3. **PR 3：Lifecycle / Projection Hardening**
   current support vs lineage markers、reaction visible_trace marker、knowledge warrant marker、stale/superseded/rejected warning markers。

### What the human reviewer should inspect after Codex’s feasibility audit

Reviewer 应重点看：

- Codex 是否逐文件确认真实字段；
- 是否把设计 intent 与 current implementation fact 分开；
- 是否保持 `LLM proposes; deterministic runner settles`；
- 是否避免新增 planner / retriever / memory manager；
- 是否把 engineering tests 与 AI Eval 分开；
- 是否把 C8 absence 标清楚；
- 是否每个 slice 都可小 PR、可回滚；
- 是否先 contract / audit，后 behavior。

### What should not be implemented yet

现在不要实现：

```text
C设计10 / C设计11
visible route disclosure UX
user route choice
route steering UI
vector DB
graph DB
Memory OS
retriever agent
memory manager agent
general planner
multi-agent reading team
broad RAG pipeline
per-unit reflection
source-free reflective truth
full benchmark redesign
full formal eval before core implementation
```

这份 handoff 到此结束。下一步进入 Codex feasibility audit，而不是继续设计。