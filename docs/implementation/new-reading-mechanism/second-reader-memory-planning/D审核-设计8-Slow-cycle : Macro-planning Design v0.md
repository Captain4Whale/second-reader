我审完了。结论是：

```text
C设计8-Slow-cycle / Macro-planning Design v0
Status: Accepted draft with minor patch
Design quality: 8.8 / 10
As upstream input: 可用
As direct Codex input: 不可直接使用，需要压成 handoff packet
Rerun needed: No
```

这篇不用重跑。它已经完成了设计8该完成的核心任务：把 `slow_cycle.py` 相关的 **memory consolidation** 和 **macro carry-forward** 正式分开，并且没有滑向大 planner、memory manager agent、route surface UX 或 implementation roadmap。设计开头继承了 P0 的边界：`LLM proposes; deterministic runner settles`，并明确 slow-cycle 只能读 settled memory 与授权 retrieval packet，不能把 raw `memory_uptake_ops`、failed/skipped ops、deferred candidates、prompt projection、audit dump 或 evaluation report 当作 authoritative memory。

## 总体评价

这篇设计是合格的，而且质量比较高。它最重要的贡献是把 slow-cycle 从一个“代码里已经做了很多事的慢周期过程”，提升成了一个正式的机制契约：

```text
slow-cycle = boundary-time memory consolidation + macro carry-forward
```

它没有把 slow-cycle 写成：

```text
per-unit reflection
general planner
memory manager agent
prompt self-refiner
full book route optimizer
visible route surface UX
```

这点非常关键。P0 本来就规定 slow-cycle 同时涉及 memory consolidation 与 macro carry-forward，但不得成为大 planner、memory manager agent 或 self-modifying policy agent。 Planning Ontology 也已经把 slow-cycle 的输出分成 memory consolidation 和 macro-planning / carry-forward 两类。 设计8基本准确接住了这个上游定义。

## 做得好的地方

### 1. 当前实现理解扎实

它没有抽象地谈“慢周期反思”，而是具体读了当前实现表面：

```text
slow_cycle.py
chapter_consolidation
reflective promotion
reconsolidation
active_attention cooling / carry-forward
knowledge activation updates
continuation_capsule
state_ops
observability
```

它也识别出当前 gap：memory consolidation 和 macro carry-forward 边界还不显式，candidate / settled state 边界还不够硬，slow-cycle audit 不够阶段化，session boundary / re-entry 还没有正式 contract。

这一点很好，因为设计8必须服务真实 `attentional_v2`，不是生成一个新架构。

### 2. Trigger 设计整体合理

它把 slow-cycle trigger 分成：

```text
normal scheduled slow-cycle
event-triggered slow-cycle
diagnostic-only slow-cycle
manual/admin repair review
```

并且明确排除了：

```text
every unit
every surfaced reaction
every active recall
every look-back
every detour signal
ordinary curiosity
theme-only association
audit failure alone
```

这个边界非常重要。否则 slow-cycle 很容易退化成“每读一点就反思一次”的高噪声机制。设计8在这里是克制的。

### 3. Input contract 很好

它明确 slow-cycle 可以读取 settled stores、current chapter/session source refs、unit span ledger、local continuity / detour trace summary、slow_cycle_consolidation retrieval results、continuation capsule 等；但不能把 raw `Read.memory_uptake_ops`、failed/skipped ops、deferred candidates、full audit dump、evaluation reports、hidden reasoning、future text 当作 authoritative memory。

这和 Formation / Settlement 的边界一致：`memory_uptake_ops` 只是 bounded write intent，不是 final persisted object；settlement 才是 authoritative boundary。

### 4. Output contract 分层清楚

它把输出分成三层：

```text
Memory consolidation outputs
Macro carry-forward outputs
Audit-only outputs
```

其中 memory consolidation 包括 cooling、promotion candidate、reflective frame、reconsolidation、knowledge activation update、source-ref-preserving support update；macro carry-forward 包括 next chapter/session focus、active_attention to carry、unresolved obligations、resolved obligations、detour cleanup、mainline restoration rationale、continuation capsule update、route trace summary。

这正是设计8最该完成的事情：让 slow-cycle 既能处理 memory，也能处理下一阶段阅读焦点，但不变成 next-unit selector。

### 5. Active attention 部分很稳

`active_attention` 被明确为 near-term hot reading state，不承载 stable semantic truth。设计区分了：

```text
carry_forward
cooling / cooled
resolved
dormant / reactivated
not_carried
```

并强调 `not_carried` 不等于 drop、不等于 semantic invalidation、不等于 lineage 删除。这很好。尤其它指出当前实现替换 active_items 前应形成 not_carried audit，避免 silent disappearance。

这个点非常重要，因为 active_attention 是最容易“被慢周期清理掉但没有记录为什么”的 store。

### 6. Reflective promotion 的 guardrail 很强

它要求 reflective promotion 至少带：

```text
supporting_source_refs
promoted_from
chapter_ref / scope
frame type / target_bucket
confidence/status
rationale
projection impact estimate
```

并且规定普通情况下应有多条 source-backed lower-level signals；单条 source 只有在作者明确给出 stage model、core definition、chapter conclusion、named distinction、resolved question of record 时才可支持 promotion。它还列了 withhold 条件，比如 source_refs missing、candidate overbroad、chapter summary dump、reaction-only、knowledge-only、overrides current source evidence。

这很好，直接防止 slow-cycle 变成“章末大总结生成器”。

### 7. Reaction / reconsolidation 边界保住了

它明确：

```text
reaction_records = append-only visible trace
strong reaction 不自动进入 concept/thread/reflective
reconsolidation_records = reinterpretation ledger
reconsolidation 不等于 reflective frame
semantic memory change 需要 separate supersede operation
```

这和 Memory Ontology、Memory Management 的边界一致。 

### 8. Detour continuity 部分有用

它没有重写 Detour Policy，而是只定义 slow-cycle 如何在 boundary 处理 open / resolved / abandoned / deferred detour、restore-mainline reason、repeated defer risk、macro carry-forward focus。它明确 slow-cycle 不选择 next unit、不重排全书、不覆盖 Navigation Policy。

这和设计6是一致的：detour 是 planning path deviation，final state effect 由 Runner / local_continuity settle。

## 需要小修的地方

整体不用重跑，但我建议做一个 **acceptance patch**。这些问题不是方向错误，而是为了防止后续实现误读。

### 1. Trigger 需要分成 MVP 与 extended

现在 trigger 很完整，但如果直接交给 Codex，会有点宽。尤其这些：

```text
high-density active_attention overflow
reflective promotion threshold
reconsolidation opportunity
knowledge activation status review
```

都可能被实现成频繁触发的 mini-manager。

建议补一段：

```text
MVP slow-cycle triggers:
- chapter boundary
- lightweight session boundary / resume capsule refresh
- long detour completion, audit-only or bounded cleanup
- support/deferred chapter transition

Extended / later triggers:
- high-density active_attention overflow
- reflective promotion threshold
- reconsolidation opportunity
- knowledge activation status review

Extended triggers must not run full chapter-like consolidation unless explicitly authorized.
```

这样能避免 slow-cycle 过度频繁。

### 2. Session boundary 要再收紧

文档已经说 session boundary 不应强行做 chapter-level reflective promotion，只做 lightweight session consolidation。这个方向对，但建议再硬一点：

```text
Session boundary v0 should not promote reflective frames,
supersede concepts/threads, or run broad consolidation by default.

It may only:
- refresh continuation capsule;
- snapshot open obligations;
- mark stale focus;
- preserve detour continuity summary;
- add warning markers;
- write session-boundary audit.
```

否则“用户/系统暂停一下”就触发一轮大整理，会很重。

### 3. Candidate / settled state 还可以更字段化

文档反复强调 candidate 不是 settled memory，方向很好。但建议增加两个 envelope 名称，方便后续 handoff：

```text
SlowCycleCandidateSet:
  LLM / deterministic prefilter proposed candidates.
  No durable state mutation.

SlowCycleSettlementEvent:
  deterministic application result.
  Contains accepted / rejected / withheld / failed / no_change outcomes.
```

这能让 Codex 后面更容易把候选和落库结果分开。

### 4. `chapter_end_notes` 需要重新解释

Reflective frame bucket 里列了：

```text
chapter_end_notes
```

但后面又说：

```text
chapter_summary_note = audit/support note, not source truth
```

这里略有张力。`chapter_end_notes` 如果放进 `reflective_frames`，容易变成“章末摘要 dump”。

建议 patch：

```text
chapter_end_notes should be treated as audit/support note or continuation-capsule note,
not as reflective truth by default.

If stored in reflective_frames for compatibility, it must carry:
- note_only marker;
- supporting_source_refs;
- not_current_truth marker unless promoted by separate reflective promotion rule.
```

或者更简单：从 reflective frame type 中移除 `chapter_end_notes`，留给 audit / continuation capsule。

### 5. `not_carried` 的持久位置要先定成 v0 策略

文档把 `not_carried` 放在 Open Questions 里：是 active_attention store 状态，还是只在 slow-cycle audit 中？这个问题确实需要后续 Implementation Handoff，但作为设计8可以先给一个 v0 默认：

```text
In v0, not_carried is audit / continuation-capsule marker, not a durable active_attention status,
unless Implementation Handoff explicitly introduces it as a store marker.
```

理由是：如果现在把 `not_carried` 放进 store status，可能会让 active_attention schema 复杂化；但如果完全不记录，又会 silent loss。先做 audit marker 最稳。

### 6. Slow-cycle audit 字段需要 MVP subset

当前 audit fields 很完整，但略多。建议加一个 MVP：

```text
MVP SlowCycleAudit:
- slow_cycle_event_id
- trigger_type
- chapter_ref / session_id
- input_packet_summary
- candidate_counts
- items_selected
- items_rejected
- active_attention_changes
- reflective_promotions
- withheld_promotions
- reconsolidation_events
- knowledge_activation_changes
- detour_continuity_changes
- not_carried_items
- source_refs_used
- memory_refs_used
- outcomes
- failure_reasons
- projection_impact
- continuation_capsule_delta
```

暂缓：

```text
full candidate counts by store
full items_considered list
full thread/concept changes if not yet stable
full state_ops_application_summary
```

不是说这些没用，而是实现第一步不宜太大。

### 7. Slow-cycle 与 state_ops 的 authority 再硬一点

文档已经说 deterministic runner / state_ops / settlement applies final state changes。很好。建议补：

```text
If current slow_cycle.py directly mutates any durable store,
that behavior should be treated as current implementation fact, not final design authority.
Implementation Handoff should route durable mutations through canonical state_ops / settlement-style wrappers where feasible.
```

这样可以防止“因为当前 slow_cycle.py 已经直接 apply，所以设计上也允许自由 apply”。

### 8. `route trace summary for audit/display-readiness` 当前没问题，但要保留 display-only 语义

这篇没有重新引入“用户选择路线”的问题，做得不错。它把 route trace summary 定义为 audit/display-readiness summary，并且说不是 Visible Route Surface UX，不创建 route controls。

这里只建议加一句：

```text
Route trace summary is produced for audit and future disclosure readiness only.
It is not product copy and not visible route surface text.
```

虽然正文里已经差不多有了，但这一句能防止后续产品化过早。

## 是否有过度清理或漏掉有价值信息？

没有明显过度清理。它保留了未来路线展示可能需要的内部数据：

```text
reading_route_trace summary
detour continuity summary
restore-mainline reason
open obligations
source_refs_used
memory_refs_used
continuation_capsule_delta
no_user_surface_needed / display-readiness boundary
```

同时没有把它产品化成 route surface UX。这是符合我们上一轮修正后的方向的。

它也没有误删 external rationale。附录仍然保留了 Generative Agents、Reflexion、LangGraph/LangMem、Mem0、Zep、MemoryBank、LongMemEval、HaluMem、HTN/Options/MAXQ、Information Foraging、ReAct/ReWOO 等外部依据，并且大多是作为 analogical / boundary / negative support 使用，不是硬搬。

## 是否可用于后续设计？

可以。

我会标记为：

```text
C设计8-Slow-cycle / Macro-planning Design v0
Status: Accepted draft with minor patch
Use as upstream input: Yes
Use as direct Codex input: No
Rerun needed: No
```

它可以作为以下后续页面的上游输入：

```text
Memory Audit / Evaluation Design
Planning Audit / Evaluation Design
Integrated Mechanism Design
Implementation Handoff
Future Visible Reading Route Surface Boundary
```

尤其对 Audit / Evaluation 很有帮助，因为它把 slow-cycle 的失败模式拆得很清楚：

```text
insufficient source evidence
overbroad promotion
source_refs missing
stale memory only
reaction-only evidence
knowledge-only evidence
deferred candidate only
conflicting concept/thread
too many active_attention items
slow-cycle output malformed
state_ops application failure
runtime artifact unavailable
```

这正是后续评估需要的 stage-aware diagnosis。Memory Assessment 也一直强调当前最该做的是收紧已有骨架，而不是引入复杂基础设施。

## 建议的 Acceptance Patch

可以让 Codex 只补一个短 patch，不需要重写全文：

```text
Slow-cycle / Macro-planning Design v0 — Acceptance Patch

1. Split triggers into MVP and extended:
   MVP:
   - chapter boundary
   - lightweight session boundary / resume capsule refresh
   - long detour completion
   - support/deferred chapter transition

   Extended:
   - active_attention overflow
   - reflective promotion threshold
   - reconsolidation opportunity
   - knowledge activation status review

2. Clarify session boundary v0:
   session boundary should only refresh continuation capsule,
   snapshot open obligations, mark stale focus, preserve detour summary,
   and write audit. No default reflective promotion.

3. Add two envelopes:
   - SlowCycleCandidateSet
   - SlowCycleSettlementEvent

4. Clarify chapter_end_notes:
   chapter_end_notes are audit/support/continuation notes,
   not reflective truth unless separately promoted under reflective promotion rules.

5. Define v0 not_carried:
   not_carried is audit / continuation-capsule marker by default,
   not durable active_attention status unless Implementation Handoff decides.

6. Add MVP SlowCycleAudit fields.

7. Strengthen authority:
   durable state mutation should go through canonical state_ops / settlement-style wrappers.

8. Clarify route trace summary:
   audit/display-readiness only; not product copy, not visible route surface text.
```

## 最终判断

这篇设计8是成功的。它把 slow-cycle 这个原本最容易变复杂的部分压在了合适的位置：

```text
边界时整理，而不是每步反思；
提出候选，而不是直接写真相；
整合 memory，而不是重写 memory；
carry forward focus，而不是规划全书；
记录 route trace，而不是做 UI；
写 audit，而不是写 evaluation score。
```

小 patch 后，它就可以作为 accepted draft，进入后续 **Audit / Evaluation** 或 **Integrated Mechanism Design**。