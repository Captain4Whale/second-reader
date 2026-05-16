是的，我审完这篇 **`C设计7-Memory Retrieval & Utilization Design v0`** 之后，判断是：

```text
Status: Accepted draft with minor patch
Design quality: 8.9 / 10
As upstream input: 可用
As direct Codex implementation input: 不可直接使用，需要先压缩成 implementation handoff packet
Rerun needed: No
```

这篇不用重跑。它已经完成了设计7该完成的核心任务：把 Memory Retrieval 从“固定 state packet + supplemental context”提升成了一个 **intent-aware、status-aware、SourceRef-first、bounded、可审计的 retrieval / utilization contract**。它也没有滑向 vector DB、graph DB、RAG pipeline、retriever agent 或 recommendation policy，这一点非常重要。

## 总体评价

这篇设计7的方向非常对。它接住了 P0 里 “retrieval must be intent-aware and bounded” 的原则，也继承了 Memory Ontology 对 store identity 的定义、Formation 对 settled state 的限制、Management 对 current truth / lineage 的分层、设计6 对 active recall / look-back / detour 的三分法。P0 已经明确要求 retrieval 先按 continuity carry、active recall、look-back、detour localization、slow-cycle consolidation、probe retrieval 等意图区分，而不是默认全局 semantic search。

这篇最核心的贡献是把下面这句话讲清楚了：

```text
retrieval hit ≠ successful utilization
```

这正是之前 Memory Assessment 里指出的核心短板之一：当前 retrieval 已经有 fixed packet、active_recall、look_back 雏形，但还没有稳定的 retrieval intent taxonomy，也没有回答“取回了什么、用了什么、用于什么、为什么没用、是否造成 FVI 风险”。

所以我的结论是：**这篇可以作为设计7 accepted draft，但需要一个小的 acceptance patch，主要是为了防止后续实现时字段膨胀、runtime/diagnostic intent 混淆，以及 utilization trace 被误解成模型内心真实使用记录。**

## 做得好的地方

### 1. Scope 很稳，没有写成 RAG 基建设计

它明确说本页不是：

```text
vector DB / graph DB / Memory OS 设计
new retriever agent
broad RAG pipeline
Recommendation object / UX
full Evaluation rubric
Codex implementation roadmap
```

这很重要。设计7真正该做的是把现有 `state_projection / read_context / source_ref / audit` 链路收紧，而不是上一个更强 RAG 系统。文档也明确把目标定义为 **file-based、SourceRef-first、status-aware、intent-aware、bounded、可审计** 的 retrieval contract。

这符合我们一路坚持的 Simplicity and Universality：先把现有机制的语义稳定下来，而不是引入新基础设施。

### 2. 对当前实现理解扎实

它准确抓住了当前实现里的 retrieval 相关 surfaces：

```text
state_projection.py:
  state_packet.v1
  active_attention_digest
  concept_digest
  thread_digest
  reflective_digest
  recent_reactions
  source_ref_digest
  continuation_capsule

read_context.py:
  active_recall
  look_back

source_spans.py:
  SourceRef / SourceSpan
  quote resolution
  fallback markers

observability.py:
  read_audit
  supplemental_ref_ids
  supplemental_steps
  stop_reason
  budget_exhausted
```

它也注意到了当前 gap：projection 已经 bounded，但还没有正式 intent label；active_recall 还主要是“未 carry + store scan”；reaction / knowledge projection 的 warning marker 需要收紧；read_audit 记录了 supplemental refs / steps / stop reason，但还没有统一 utilization trace。

这说明它不是抽象写“检索理论”，而是真的围绕 `attentional_v2` 的现有代码表面做机制收紧。

### 3. Retrieval intent taxonomy 很有价值

它定义的 MVP intents 是这篇最核心的产物：

```text
continuity_carry
active_recall
look_back_support
detour_support
source_ref_recalibration
lineage_recall
slow_cycle_consolidation
evaluation_probe
```

并把 `recommendation_support` 和 `manual_repair_support` 放到 extended subset。这基本符合设计目标。尤其 `continuity_carry` 这个命名很好，它把当前 fixed packet 重新解释为默认 carry-forward baseline，而不是唯一 retrieval policy。

这比“所有东西都叫 retrieval”清晰很多。后续实现时，`read_context`、`state_projection`、`observability` 都可以围绕 intent label 收紧。

### 4. 它很好地继承了设计5的 lifecycle 约束

设计5已经明确区分 `current_truth_projection` 与 `lineage_projection`，并要求 superseded / invalidated / rejected items 不进入普通 current truth，cooled / dormant 只是低优先级而不是 false。

设计7把这些规则落到了 retrieval filtering：

```text
source_supported / refined → current truth priority
provisional → marker required
cooled / dormant → low priority, not false
superseded / invalidated / rejected → lineage_only
retired → historical recall only
fallback_source_ref / missing source_refs → downgraded
reaction_records → visible_trace marker
knowledge_activations → warrant marker
deferred candidates → excluded by default
```

这正是设计7应该做的事情：把 Management 的 lifecycle contract 转译成 retrieval filtering / context assembly 规则。

### 5. active_recall / look_back / detour_support 没有混淆

设计6已经把三者定义为：

```text
active_recall = memory recovery
look_back = source calibration
detour = planning path deviation
```

并要求 active recall 不写 memory、不改变 cursor、不打开 detour；look-back 返回 source excerpt，不自动写 memory或改变 path；detour unit 必须走同一个 Navigate → Read → settlement loop。

设计7继承得很好：

```text
active_recall:
  取回 memory state，不做 source verification。

look_back_support:
  返回 source excerpt，不是 semantic memory truth。

detour_support:
  可以提供 memory/source support，但 memory projection 不能单独选择 detour target。
```

这说明它没有把 Retrieval 页面写成 Detour Policy 的重写，也没有让 active_recall 替代 look-back。

### 6. Utilization Trace 是这篇的最大亮点

它明确提出最小字段：

```text
items_returned
source_refs_returned
items_used
source_refs_used
used_for
not_used_items
no_use_reason
status_markers
warning_markers
stop_reason
failure_reason
projection_impact
visible_output_impact
memory_write_impact
detour_impact
```

并定义了 `used_for`：

```text
read_continuity
definition_support
thread_continuity
visible_callback_support
source_calibration
detour_localization
slow_cycle_candidate
recommendation_support
evaluation_probe
manual_repair
not_used
```

这非常重要。它把 retrieval 质量从“有没有取回来”推进到“取回来有没有正确使用”。这会直接服务后续 Memory Audit / Evaluation 和 Planning Audit / Evaluation。

### 7. FVI guardrails 写得很到位

它专门列出了 FVI-sensitive retrieval 的风险：

```text
stale memory leakage
reaction semanticization
knowledge activation source-truth化
source excerpt becoming hidden reading unit
audit dump becoming prompt context
deferred candidate becoming memory item
theme-only thread association
over-retrieval causing prompt bloat
retrieval result over-integrated into visible reaction
```

并给出了一个很好的原则：

```text
Not-used is a valid success.
```

也就是说，在 FVI-sensitive contexts 里，正确地取回但不使用 stale / weak / warning-only material，是好结果，不是失败。这个判断很成熟。

### 8. Implementation readiness 比较克制

它没有说现在可以实现完整 retriever，而是把 ready for narrow implementation 限定在：

```text
retrieval_intent labels
status markers
current_truth vs lineage warning markers
items_returned / items_used / no_use_reason compact trace
source_refs_used / memory_refs_used
duplicate suppression logging
stale memory warning markers
visible_trace marker
warrant marker
budget / stop reason enrichment
fallback_source_ref warning
source_ref_ambiguous warning
```

这很安全。它把实现第一步限制在 labels / markers / compact trace / logging，而不是新增检索基础设施。

## 主要需要小修的地方

整体不用重跑，但建议加一个 **Acceptance Patch**。我认为需要补 8 个点。

### 1. 把 runtime retrieval intent 和 diagnostic / repair intent 再分层

现在 taxonomy 里把这些都放在一起：

```text
continuity_carry
active_recall
look_back_support
detour_support
source_ref_recalibration
lineage_recall
slow_cycle_consolidation
evaluation_probe
```

方向可以接受，但实现时容易混淆。尤其 `evaluation_probe` 和 `manual_repair_support` 不是 runtime prompt retrieval；`source_ref_recalibration` 更像 validation subroutine；`slow_cycle_consolidation` 是 boundary process retrieval，不是 ordinary Read retrieval。

建议 patch 加一段：

```text
Retrieval intents are divided into three bands:

A. Runtime prompt-facing intents:
- continuity_carry
- active_recall
- look_back_support
- detour_support

B. Boundary / background intents:
- source_ref_recalibration
- lineage_recall
- slow_cycle_consolidation
- recommendation_support

C. Diagnostic / repair intents:
- evaluation_probe
- manual_repair_support

Only Band A may normally enter Read / Navigate prompt.
Band B requires explicit policy or boundary trigger.
Band C never enters runtime prompt.
```

这样可以防止 Codex 或后续模型把 `evaluation_probe` 当成 runtime retrieval 来实现。

### 2. `source_ref_recalibration` 应明确是 subroutine，不是普通 retrieval mode

这篇已经说 source_ref_recalibration 不自动更新 memory，也不把 fallback 升格成 exact evidence。但它放进 MVP intent 后，可能让实现以为要新增一个独立 retriever。

建议补：

```text
source_ref_recalibration is a validation / warning subroutine.
It may be invoked inside active_recall, look_back_support, lineage_recall, slow_cycle_consolidation, or manual_repair_support.
It should not become a general prompt-facing retrieval mode.
```

这能保持它的工具性，不让它膨胀成 repair workflow。

### 3. Utilization trace 字段要压成 MVP subset

现在 utilization trace 很完整，但字段较多。文档自己也在 Simplicity check 里承认 `utilization_trace` 字段可能膨胀。

建议加一个 MVP：

```text
MVP RetrievalUtilizationTrace:

retrieval_event_id
timestamp
requester
retrieval_intent
query_basis
store_scopes
filters_applied
budget_state
items_returned
source_refs_returned
items_used
source_refs_used
used_for
not_used_items
no_use_reason
status_markers
warning_markers
stop_reason
failure_reason
projection_impact
```

暂缓：

```text
candidates_considered_count
visible_output_impact
memory_write_impact
detour_impact
```

不是说这些没用，而是第一轮实现可能不稳定。它们可以作为 v0.2 或 evaluation-enriched trace。

### 4. `items_used` 需要区分“声明使用”和“可验证使用”

这是最重要的 patch。

Retrieval utilization 的难点是：模型可能说“我用了某个 memory”，但真正的 visible output、memory_uptake_ops、detour decision 未必能证明它用了。相反，有时模型隐式使用了某个 context，但没有明确引用。

所以建议把 `items_used` 拆成：

```text
items_claimed_used:
  LLM / node reports that it used these items.

items_evidenced_used:
  observable evidence shows use, such as:
  - source_refs cited in surfaced reaction;
  - memory_refs referenced in reason summary;
  - source_refs used in memory_uptake_ops;
  - detour target selected from source evidence;
  - visible output callback explicitly grounded in retrieved item.
```

然后补一句：

```text
Utilization trace records observable / declared use, not hidden mental use.
```

这会让后续 Audit / Evaluation 更诚实。否则 `items_used` 很容易变成一个伪精确字段。

### 5. `current_truth` 这个词可能略强，建议加本地解释

`current_truth_projection` 是从设计5继承来的，我理解它的意思是“当前可作为 source-so-far 下普通支持的 memory”。但 “truth” 容易让实现者或后续读者误解成 absolute truth。

建议加一句：

```text
In this design, current_truth means “currently usable as source-so-far reading support,” not absolute truth.
If this wording causes implementation confusion, Implementation Handoff may rename it to current_support_projection while preserving the same semantics.
```

这不是必须改名，但需要解释。尤其你的项目强调 source-grounded reading，不是事实数据库。

### 6. `slow_cycle_consolidation` 的输入要再防 prompt bloat

现在它允许 slow-cycle 读取 broader but bounded settled memory、reaction records、knowledge activations、deferred candidates as candidate evidence、selected audit summaries。方向对，但容易膨胀。

建议补：

```text
Slow-cycle consolidation retrieval should use a two-stage packet:
1. candidate index packet:
   IDs, store, status, source_refs, short reason, warning markers.
2. expanded evidence packet:
   only for selected candidates that pass budget and source-ref gate.

Do not send full broad memory plus audit summaries in one prompt.
```

这可以避免 slow-cycle 变成“把一堆东西都塞进去让模型总结”。

### 7. `recommendation_support` 要再强调 evidence-only

这篇已经说不设计 recommendation object，但 `recommendation_support` 作为 extended intent 仍可能被误用成 recommendation policy。

建议补：

```text
recommendation_support returns evidence scaffolds only.
It must not produce:
- recommendation text;
- user-facing rationale;
- accept / skip state;
- reading path change;
- recommendation persistence.
```

这会防止设计9之前提前泄漏 recommendation 逻辑。

### 8. 需要一个 Pre-Handoff Gate

和前几篇一样，这篇不能直接交给 Codex。建议加一个小 gate：

```text
Before Codex implementation, convert this design into a Memory Retrieval & Utilization Handoff Packet containing:

1. MVP retrieval intent labels
2. marker vocabulary
3. current_support / lineage filtering rules
4. compact utilization trace fields
5. read_context changes
6. state_projection changes
7. observability changes
8. explicit non-goals
```

这样 Codex 不会拿 10 万字设计全文直接拆 task。

## 建议的 Acceptance Patch

可以不重写全文，只补一个 patch：

```text
Memory Retrieval & Utilization Design v0 — Acceptance Patch

1. Split retrieval intents into three bands:
   A. Runtime prompt-facing:
      continuity_carry, active_recall, look_back_support, detour_support
   B. Boundary / background:
      source_ref_recalibration, lineage_recall, slow_cycle_consolidation, recommendation_support
   C. Diagnostic / repair:
      evaluation_probe, manual_repair_support

2. Clarify source_ref_recalibration:
   It is a validation / warning subroutine, not a general prompt-facing retrieval mode.

3. Define MVP RetrievalUtilizationTrace:
   retrieval_event_id, timestamp, requester, retrieval_intent, query_basis,
   store_scopes, filters_applied, budget_state, items_returned,
   source_refs_returned, items_used, source_refs_used, used_for,
   not_used_items, no_use_reason, status_markers, warning_markers,
   stop_reason, failure_reason, projection_impact.

4. Split utilization into:
   items_claimed_used
   items_evidenced_used

   Utilization trace records observable / declared use, not hidden mental use.

5. Clarify current_truth:
   current_truth means currently usable as source-so-far reading support,
   not absolute truth. Implementation Handoff may rename it to current_support_projection.

6. Add slow-cycle retrieval packet discipline:
   first candidate index packet, then expanded evidence packet only for selected candidates.

7. Clarify recommendation_support:
   evidence scaffold only; no recommendation object, no user-facing rationale,
   no accept/skip state, no path change.

8. Add Pre-Handoff Gate:
   convert this design into a narrow handoff packet before Codex implementation.
```

## 是否可用于后续设计？

可以。它可以作为以下页面的上游输入：

```text
C设计8-Slow-cycle / Macro-planning Design v0
C设计9-Recommendation Policy Design v0
Memory Audit & Evaluation Design
Planning Audit & Evaluation Design
Integrated Mechanism Design
Implementation Handoff
```

尤其对后续 Audit / Evaluation 很关键，因为它给了一个非常清晰的失败分解：

```text
formation failure
settlement failure
retrieval failure
utilization failure
FVI pollution
```

这正好补上 Memory Assessment 里说的：不能只看最终 memory quality，需要 stage-aware diagnosis。

## 最终判定

我会把这篇标记为：

```text
C设计7-Memory Retrieval & Utilization Design v0
Status: Accepted draft with minor patch
Use as upstream input: Yes
Use as direct Codex input: No
Rerun needed: No
```

它最重要的贡献是把 retrieval 从“把一些上下文塞进 prompt”变成了：

```text
为什么取回；
从哪里取回；
按什么状态过滤；
以什么 channel 返回；
是否进入 prompt；
是否真的被使用；
没用为什么没用；
是否造成 FVI 风险。
```

这就是设计7应该完成的事情。小 patch 后，它可以正式进入 accepted draft。