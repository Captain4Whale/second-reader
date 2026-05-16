我的判断是：

```text
Status: Accepted draft with minor patch
Design quality: 8.8 / 10
As upstream input: 可用
As direct Codex implementation input: 不可直接使用，需要先压缩成 implementation handoff
Rerun needed: No
```

这篇不用重跑。它已经完成了设计6该完成的核心任务：把 **active recall / look-back / detour** 从“已有机制雏形”提升成了可继承、可审计的 policy contract。

## 总体评价

这篇设计的方向是对的。它开头明确继承 P0、Planning Ontology、Navigation Policy、Memory Ontology、Formation 和 Management，并且把自己的范围限定在：

```text
什么时候 active recall；
什么时候 look-back；
什么时候 open / continue / defer / abandon / resolve detour；
如何预算；
如何退出；
如何恢复主线；
如何审计。
```

它也明确不做完整 Retrieval、Recommendation、Evaluation、Codex roadmap，不新增 planner node 或 memory manager agent。这个边界非常重要，也说明它吸取了前面几轮“不要把一个页面写成所有页面”的教训。

这篇最核心的三分法也很稳：

```text
active_recall = memory recovery
look_back = source calibration
detour = planning path deviation
```

这个三分法正好继承了 P0 和 Planning Ontology：P0 已经把 active recall、look-back、detour 分别定义为 memory recovery、source calibration、planning path deviation，并规定 detour 必须有 origin、target hint、reason、budget、status 和 restore-mainline reason。 Planning Ontology 也已经把 `active_recall`、`look_back`、`detour` 写成三种不同对象，强调 active recall 不替代 source verification，look-back 不等于 memory recall，detour 不是 hidden supplemental fetch。

所以这篇设计6在整体架构上是合格的。

## 做得好的地方

### 1. Scope 没有跑偏

它没有重开 Planning Ontology，也没有重写 Navigation Policy。它明确说自己只是补 Navigation Policy 故意延后的 policy 问题：三种机制什么时候触发、什么时候停止、如何预算、如何审计。

这点很好。设计6本来就不该继续讨论 “Planning 是什么” 或 “Navigate 是什么”，而应该进入 policy 层。

### 2. 对当前实现理解扎实

它准确抓住了当前实现里的关键对象：

```text
Read.detour_need
DetourNeed schema: reason / target_hint / status
LocalContinuityState
active_detour_id / active_detour_need / detour_trace
NavigateActResult: choose_unit / request_skill / defer_detour
read_context.py: active_recall / look_back
source_skills.py: source_map_overview / source_scope_drilldown / source_window_fetch
state_projection.py: bounded navigation context
observability: read_audit / settlement_audit
```

这说明文档不是抽象写 policy，而是真的围绕 `attentional_v2` 的现有 surfaces 来收紧机制。

### 3. 它继承了 Navigation Policy 的关键 patch

这是我最关心的一点。设计6没有重新扩展 `NavigateActResult`，而是继续保持：

```text
choose_unit
request_skill
defer_detour
```

并且它明确说 `restore_mainline` 是 Runner / local_continuity settlement effect，不是 Navigate output；`active_recall_needed / look_back_needed` 是 support / audit 信号，不是 operational trigger。这和 Navigation Policy 的 patch 是一致的。

如果这里写错，后续实现会很危险，因为 Codex 可能会扩展 Navigate act space。现在这版没有犯这个错。

### 4. active recall 写得比较稳

Active recall 部分清楚区分了 trigger / non-trigger / allowed sources / output / exit / audit。尤其几个约束很好：

```text
active recall 不替代 source verification；
reaction_records 只能作为 visible trace / callback context；
knowledge_activations 只能作为 warrant-bearing projection；
superseded / invalidated / rejected memory 只能在 explicit lineage intent 下使用；
audit 要记录 trigger_reason、memory_refs_returned、status_markers、used_for、warning_markers。
```

这很好地继承了 Memory Ontology 和 Management 的边界。Memory Management 已经定义 current_truth_projection 与 lineage_projection，并规定 superseded / invalidated / rejected items 不应作为 current truth 普通返回。

### 5. look-back 终于被固定为 source calibration

Look-back 部分写得很清楚：它只回到 earlier source excerpt，用来校准 source evidence；它不写 memory、不改变 path、不自动成为 detour。这个判断正好解决 Planning Assessment 里指出的风险：look-back 不能因为“有点相关”就默认触发，它应该服务 comprehension calibration 和 FVI 防护。

### 6. Detour Policy 是这篇最有价值的部分

Detour 的 open / continue / request skill / defer / abandon / resolve / restore mainline 写得比较完整。尤其这些边界是对的：

```text
target_hint 是 hint，不是 target；
source skills 是 evidence provider，不是 semantic relevance judge；
detour target 不能只由 memory projection 选中；
reaction digest / knowledge activation 不能作为 sole target basis；
defer_detour 不是 durable status；
restore_mainline 是 Runner effect；
detour unit 一旦被选中，必须走 Navigate → Read → settlement 同一 loop。
```

这正是前面 P0 和 Navigation Policy 反复强调的：detour 是 first-class path deviation，不是 hidden supplemental fetch。

### 7. Decision Table 很实用

第 9 节的 policy decision table 是一大亮点。它把很多真实场景落到了具体动作上，比如：

```text
当前 source 引用前文定义；
current source 与 memory summary 冲突；
reaction wants callback earlier moment；
prior knowledge activation triggered；
active recall returns superseded memory；
look-back source unavailable；
theme-only association appears interesting；
FVI risk detected；
current mainline can continue safely。
```

这张表会直接帮助后续 Implementation Handoff 和评估设计。它不是单纯填表，而是在帮助把 policy 用例化。

### 8. Implementation Readiness 很克制

它只把 logging / reason vocabulary / audit fields / warning markers / no-future-text guardrails 这类窄实现列为 ready，没有说现在可以实现 full retrieval、durable detour state machine、recommendation object、multi-detour queue 或 evaluation rubric。

这符合我们前面一直坚持的原则：设计页可以定义 policy，但不能直接变成 Codex roadmap。

## 主要需要小修的地方

整体不用重跑，但我建议做一个 **acceptance patch**。主要是为了防止后续实现误读。

### 1. active recall / look-back “reveals path need” 不应直接 open detour

现在第 7.1 写到：

```text
active recall / look-back reveals a source-grounded path need
```

可以打开 detour。这个方向可以接受，但要更硬地区分：

```text
active recall / look-back may produce a detour_candidate;
they do not directly open durable detour state.
```

否则后续实现可能让 read_context 直接改 `local_continuity`。

建议补一句：

```text
Active recall or look-back may surface a detour_candidate, but only Runner / policy-authorized settlement can open active_detour_need. read_context never mutates local_continuity.
```

这是第一优先级 patch。

### 2. `source_scent / detour_value / continuity_cost` 需要最小受控值

文档用这三个判断语言很好，但如果后续进入实现，完全 free-text 会不好审计。

建议加一个轻量 vocabulary，不需要数值模型：

```text
source_scent: none / weak / plausible / strong
detour_value: low / medium / high
continuity_cost: low / medium / high
```

并补一句：

```text
These are audit-facing qualitative markers, not numerical scores.
```

这样后续 Planning Audit / Evaluation 会更容易用。

### 3. Detour candidate 与 active detour state 需要更明确分层

现在文档定义了 detour need、detour localization、detour defer、resolve、abandon，但 **candidate** 这个中间状态还不够明显。

建议加一小节：

```text
Detour candidate:
  a source-grounded possibility that may justify path deviation;
  not yet active_detour_need;
  can be produced by active recall, look-back, source skill result, or Read;
  does not change cursor or local_continuity;
  must be admitted by policy before becoming active detour.
```

这样可以防止所有“可能值得绕一下”的信号都变成 active detour。

### 4. Active recall output 应按用途分 channel

现在 active recall 返回 `memory_refs / compact summaries / source_refs / status markers / used_for`，已经不错。但建议再明确它的输出通道：

```text
current_memory_support
lineage_support
visible_trace_support
warrant_support
not_used
```

原因是 active recall 可能取回 concept、thread、reaction、knowledge activation、superseded item。它们性质完全不同。设计5已经把 current_truth_projection 和 lineage_projection 分开了；设计6最好把 active recall result 也对应分层。

### 5. Look-back failure 后的行为可以再硬一点

现在 look-back failure 的 recovery 写了：

```text
continue mainline with uncertainty or defer
```

这个方向对，但建议加一句：

```text
A failed look-back must not be silently replaced by memory confidence.
```

也就是说，如果 source calibration 失败，系统不能说“那就相信 memory”。这对防 FVI 很重要。

### 6. `defer_detour` 的 reattempt guard 仍偏软

文档已经写：

```text
Prevent immediate reattempt only if implementation or later policy supports cooldown.
```

这是保守的。但为了防止 detour loop，建议在 policy 层加一个最低要求：

```text
Even if behavior-level cooldown is not implemented, audit must record same_detour_reattempt_risk when the same target_hint is deferred repeatedly.
```

这样即使不做状态机，也能诊断重复 defer。

### 7. Detour abandon 的权限需要再明确

现在 abandon 条件写得好，但谁能最终 abandon 还可以更清楚。

建议补：

```text
Read may propose resolved / abandoned status inside active detour;
Navigate may provide evidence for defer;
Runner / local_continuity settlement records final status transition.
```

也就是不要让 Navigate 直接 abandon；它可以 defer 或提供 reason，最终状态还是 Runner settle。

### 8. Implementation Readiness 要再压缩成 MVP subset

现在 ready for narrow implementation 仍然稍微多了一点。建议在 implementation handoff 前压成 MVP：

```text
MVP ready:
- reason logging for active_recall / look_back / detour
- source_evidence_used / memory_refs_used
- support flags as audit-only
- detour defer / resolve / abandon / restore reason logging
- budget_state / stop_reason
- stale memory warning marker
- no future text guardrail
```

暂缓：

```text
full active recall execution changes
full look-back execution changes
detour candidate admission engine
defer cooldown behavior
durable deferred status
multi-detour queue
```

这样 Codex 会更安全。

## 建议的 acceptance patch 清单

你可以让模型补一个短 patch，不必重写全文：

```text
Detour / Look-back / Active Recall Policy Design v0 — Acceptance Patch

1. Clarify that active recall / look-back may produce detour_candidate,
   but cannot directly open active_detour_need or mutate local_continuity.

2. Add qualitative audit markers:
   source_scent = none / weak / plausible / strong
   detour_value = low / medium / high
   continuity_cost = low / medium / high

3. Define detour_candidate as separate from active detour state.

4. Split active recall outputs into:
   current_memory_support
   lineage_support
   visible_trace_support
   warrant_support
   not_used

5. Clarify failed look-back:
   failed source calibration must not be replaced by memory confidence.

6. Add repeated defer diagnostic:
   same_detour_reattempt_risk should be logged if the same target_hint is repeatedly deferred.

7. Clarify abandon authority:
   Read may propose resolved / abandoned inside active detour;
   Runner / settlement records final detour status transition.

8. Split implementation readiness into MVP-ready vs later:
   logging and audit markers first;
   no full trigger engine / retrieval ranking / durable deferred status yet.
```

## 是否可用于后续设计？

可以。

我会把它标记为：

```text
C设计6-Detour / Look-back / Active Recall Policy Design v0
Status: Accepted draft with minor patch
Use as upstream input: Yes
Use as direct Codex input: No
Rerun needed: No
```

它已经可以作为后续这些页面的上游输入：

```text
C设计7-Memory Retrieval & Utilization Design v0
C设计8-Slow-cycle / Macro-planning Design v0
C设计9-Recommendation Policy Design v0
Planning Audit / Observability Design
Planning Evaluation Design
Memory Audit / Evaluation Design
Implementation Handoff
```

尤其对 **Memory Retrieval & Utilization** 很关键。设计6已经定义了三种 retrieval-facing intent：

```text
active recall: memory recovery
look-back: source calibration
detour support: source-grounded path need
```

后续设计7就可以接着回答：每种 intent 如何取回、如何过滤、如何组装、如何记录 utilization trace，而不是再争论三者是什么。

## 最终判断

这篇设计6成功完成了它该做的事：它把原来散落在 `Read.detour_need`、`Navigate` detour mode、`read_context.active_recall`、`read_context.look_back`、source skills 和 local_continuity 里的行为，整理成了一个清晰的 policy 层。

最重要的是，它没有追求更强 planner，而是把已有机制收紧：

```text
active recall 只恢复 memory；
look-back 只校准 source；
detour 只控制 path；
source skill 只提供 evidence；
Runner 才 settle state；
audit 记录 reason / evidence / budget / outcome；
mainline continuity 仍是默认。
```

这个方向非常稳。小 patch 后可以正式作为设计6 accepted draft。