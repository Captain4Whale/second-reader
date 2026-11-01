是的，下一步应该进入**分步骤设计阶段**，不要再继续做大规模调研，也不要一次性让模型生成一个“完整总设计”。现在你已经有了两类很有价值的材料：

1. **External Evidence Pack**：外部已有工作的证据库、参考索引、引用来源。
2. **Project Assessment & Improvement Directions**：已经把外部证据和项目现状连接起来，形成了项目层面的判断、差距和调整方向。

接下来应该从“评估”切换到“设计”，核心任务变成：

> 基于评估结论，把 Memory 和 Planning 的关键机制逐块设计清楚，并形成可以沉淀到 RepoDocs / Notion、最终交给 Codex 实现的设计文档。

Memory 评估已经明确指出，当前机制的主要问题不是缺 vector DB、graph DB 或 manager agent，而是 memory contract 的语义稳定性不足，包括 store 身份、`memory_uptake_ops`、lifecycle、retrieval intent、evaluation / audit failure attribution 等。 Planning 评估也类似，它认为当前系统已经是一个不错的 source-grounded reading navigator skeleton，但 planning ontology、`Navigate.choose_next_unit` 职责、detour/look-back policy、visible route disclosure boundary、planning audit/evaluation 还需要正式设计。

## 前面调研结果还要不要作为输入？

要，但**角色要降级**。

设计阶段的输入优先级应该是：

```
第一优先级：当前 GitHub repo + 已接受的设计文档
第二优先级：Memory / Planning 评估报告
第三优先级：External Evidence Pack
第四优先级：综述、早期讨论、临时想法
```

也就是说，**评估报告是主输入**。因为它已经把外部研究、项目现状、差距、复杂度边界都整合过了。

但 **External Evidence Pack 仍然要带上或可访问**，原因是：设计文档里每个重要决策仍需要能说清“为什么这样做，参考了哪些外部工作”。评估报告会压缩证据，而 Evidence Pack 能帮助模型回到具体 paper / official docs，不至于把设计依据说空。Memory evidence pack 自己也明确说它只做外部证据包，不做项目内部设计，下一步才应该把证据映射到 Reading Companion 的 stores、settlement、SourceRef、JSON/JSONL 约束和评估体系上。 Planning evidence pack 也同样定位为外部证据包，而不是项目设计文档。

所以实际操作上，我建议每个设计会话都给它三类材料：

```
1. 当前 repo / GitHub
2. 对应的评估报告
3. 对应的 External Evidence Pack，作为证据索引
```

如果上下文太长，就不用整包塞进去，而是给它“相关章节 + Source Usage Appendix + 评估报告中对应模块”。但不要只给评估报告，否则后续设计文档里的外部依据可能会变弱。

## 是否应该分步骤设计？

应该，而且最好**一个设计块一个新会话**。

你这个判断是对的：每一部分都让一个新对话生成一篇完整文档，质量会比在一个长会话里连续写所有设计更稳。原因很简单：每个模块都有自己的 ontology、contract、边界和复杂度风险。如果放在一个会话里做，模型很容易越写越大，把 formation、management、retrieval、evaluation 混在一起。

但要注意一个关键点：

> 后面的设计必须把前面已经接受的设计文档作为输入。

否则每个新会话都会重新发明一遍术语，最后互相打架。

推荐流程是：

```
每个模块新开一个会话
  ↓
输入：当前 repo + 总评估报告 + 相关 evidence + 已完成的前置设计文档
  ↓
生成该模块设计文档
  ↓
你人工审查并标记 accepted / needs revision / rejected
  ↓
沉淀到 Notion 或 RepoDocs
  ↓
作为后续模块输入
```

## 我建议的设计分块与顺序

### Phase 0：Shared Design Charter

这是进入具体 Memory / Planning 之前的总边界页。

**文档名：**

```
Second Reader Agent Mechanism Design Charter v0
```

**它要解决：**

- Second Reader 到底是什么，不是什么；
- source corpus / reading memory / planning state / audit trace / user-facing output 的边界；
- `attentional_v2` 当前的核心机制骨架；
- Simplicity and Universality 如何约束后续设计；
- 当前明确拒绝什么：memory OS、graph-first、vector-first、大 planner、多 agent、full graph workflow、RL memory editing 等。

这个文档不需要很长，但它很重要。它相当于后面所有设计页的“宪法”。没有它，Memory 和 Planning 设计会各自定义边界，容易分裂。

------

### Phase 1：Ontology 层

Ontology 应该先做，因为后面的 formation、management、retrieval、planning policy 都依赖“对象是什么”。

### 1. Memory Ontology Design

**文档名：**

```
Memory Ontology Design v0
```

**核心问题：**

- 什么是 source corpus？
- 什么是 reading memory？
- 什么是 audit？
- 什么是 visible trace？
- 什么是 prior / external knowledge warrant？
- `active_attention`、`concept_registry`、`thread_trace`、`reflective_frames`、`reaction_records`、`knowledge_activations` 各自是什么？
- 哪些 store 保留，哪些不新增？
- durable memory 必须满足什么 source-grounding 条件？

这是 Memory 里最应该先做的页面。评估报告已经说得很清楚：当前最大缺口之一就是 store ontology 的边界还不够锋利。

### 2. Planning Ontology Design

**文档名：**

```
Planning Ontology Design v0
```

**核心问题：**

- Planning 在 Reading Companion 里到底是什么？
- 它为什么不是 AutoGPT 式 task planning？
- reading path planning、attention scheduling、source-grounded navigation 之间是什么关系？
- source text、reading locus、memory state、planning state、audit trace、visible route disclosure 如何区分？
- micro / meso / macro planning 是否成立？
- internal navigation 与 visible route disclosure 是否分层？

这个页面可以在 Memory Ontology 之后做，也可以并行做。但我更建议**Memory Ontology 先半步**，因为 Planning 会引用 memory state、active attention、thread trace、reflective frame 等概念。

------

### Phase 2：核心运行契约层

这一层定义最核心的节点和操作契约。

### 3. Memory Formation & Settlement Design

**文档名：**

```
Memory Formation & Settlement Design v0
```

**核心问题：**

- `Read.memory_uptake_ops` 是什么？
- 它是 bounded memory intent，还是 final persisted object？
- `Read` 能提议什么，不能提议什么？
- settlement 拥有什么权限？
- SourceRef 如何绑定？
- formation 是否拆成 extraction / evidence binding / relation or conflict handling / settlement？
- 哪些写入属于 read-path，哪些必须留到 slow-cycle？

这个页面应该在 Memory Ontology 之后做。没有 store ontology，就无法定义 `memory_uptake_ops` 应该写向哪里。

### 4. Navigation Policy Design

**文档名：**

```
Navigation Policy Design v0
```

**核心问题：**

- `Navigate.choose_next_unit` 到底是什么？
- 它是 next-unit selector、micro-planner、source-grounded navigator，还是 router？
- 默认 source-order continuity 如何表达？
- continue mainline、look-back、detour、defer、deep-dive 如何取舍？
- 是否需要 value / cost / information scent 这类判断语言？
- 当前是否需要独立 planner node？

这个页面应该在 Planning Ontology 之后做。它是 Planning 机制的核心契约页。

------

### Phase 3：演化、回看与检索层

这一层开始处理“状态如何变化”和“什么时候取回什么”。

### 5. Memory Management & Evolution Design

**文档名：**

```
Memory Management & Evolution Design v0
```

**核心问题：**

- 最小 lifecycle 是什么？
- create / update / refresh / resolve / cool / drop / supersede 分别是什么意思？
- 不同 store 的 legal operation matrix 是什么？
- 后文修正前文时如何表达？
- destructive overwrite、soft invalidate、supersede、cooling 如何区分？
- slow-cycle 拥有什么 promotion / consolidation 权限？

这个页面依赖 Memory Formation，因为你要先知道 memory 是怎么进来的，才能设计它怎么演化。

### 6. Detour / Look-back / Active Recall Policy Design

**文档名：**

```
Detour Look-back Active Recall Policy Design v0
```

**核心问题：**

- look-back 什么时候触发？
- active recall 和 look-back 有什么区别？
- detour 什么时候开启？
- detour 如何退出？
- 如何恢复主线？
- 如何避免 novelty chasing 和 over-search？
- memory retrieval 与 source look-back 如何配合？

这个页面横跨 Planning 和 Memory。它应该在 Navigation Policy 和 Memory Ontology 之后做，最好也等 Memory Formation 有初步结论后再做。

### 7. Memory Retrieval & Utilization Design

**文档名：**

```
Memory Retrieval & Utilization Design v0
```

**核心问题：**

- 当前 fixed packet 是否保留？
- retrieval intent taxonomy 是什么？
- continuity recall、definition recall、thread recall、look-back、detour support、slow-cycle retrieval、probe retrieval 如何区分？
- metadata / tags / source_refs / lightweight links 如何使用？
- memory 被取回后如何被真正利用，而不是只塞进 prompt？
- 当前是否仍坚持 file-based retrieval first？

这个页面应该在 Memory Ontology、Formation、Management 之后做，也要参考 Detour / Look-back Policy。否则 retrieval intent 会没有清晰来源。

------

### Phase 4：用户可见层与慢周期层

### 8. Slow-cycle / Macro-planning Design

**文档名：**

```
Slow-cycle Macro-planning Design v0
```

**核心问题：**

- slow-cycle 是 memory consolidation，还是 macro-planning，还是两者都有？
- chapter-end consolidation 与 carry-forward focus 如何定义？
- reflective_frames 与 macro-planning 的关系是什么？
- slow-cycle 可以 promote 什么？
- slow-cycle 不应该做什么？
- 是否记录策略失败或 navigation failure？

这个页面连接 Memory 和 Planning，可以保留 route trace summary for audit / future display readiness，但不得产生 user route controls、visible route surface object、accept/reject route state、learning path plan 或 route steering。它完成后，下一步进入 Evaluation Calibration，而不是直接拆 Memory / Planning 两套评测大文档。

### Future / Deferred：Visible Reading Route Surface Boundary Design

Status：Future / deferred / optional. Not part of the current implementation track. Current implementation should only preserve route trace and audit fields needed for reading progression and possible future disclosure; it should not implement user-facing route control, route-surface accept/reject, or route steering.

**文档名：**

```
Visible Reading Route Surface Boundary Design v0
```

**核心问题：**

- internal navigation 和 visible route disclosure 如何区分？
- 未来如果展示路线，展示的是哪些 `reading_route_trace` / visible reading note？
- next segment、look-back point、deep-dive、thematic path、carry-forward focus、no_user_surface_needed 如何分类？
- visible reading note rationale 应该暴露多少？
- 如何保持 source-grounded、不过度控制用户？
- 什么时候应该保持 `no_user_surface_needed`？

这个页面不要太早做。它依赖 Planning Ontology、Navigation Policy、Detour Policy。否则 route disclosure 很容易变成“系统想读哪里就让用户选择哪里”。

------

### Phase 5：Evaluation Calibration Layer

这层现在应先做校准，而不是直接拆成 Memory Audit & Evaluation 和 Planning Audit & Evaluation 两篇大系统设计。

Evaluation is not the same as engineering tests.

**Evaluation / AI Evals** 衡量 Second Reader 是否达到预期阅读行为和产品质量：faithful memory、useful continuity、natural callback、low FVI、grounded navigation、bounded detour、safe slow-cycle promotion。

**Contract / Audit Checks** 位于 Evaluation 与 Engineering Tests 之间。它们不是最终产品质量分数，而是 evaluation instrumentation / audit coverage / contract observability，用来保证 evaluation 有证据可查，例如 SourceRef binding result、per-op settlement outcome、retrieval utilization trace、detour restore reason、slow-cycle promotion evidence。

**Engineering Tests** 检查程序实现是否正确，例如 unit tests、integration tests、schema tests、file persistence tests、CI regression、migration tests。它们属于 Codex Implementation Handoff 和 implementation 阶段，不是 C设计9 的核心任务。

当前项目已经有 MQ / Callback / FVI、现有 dataset / probe / audit、以及 C设计0-8 的机制 contract。下一步最重要的是 inventory existing evaluation work，判断现有评测资产能覆盖什么、哪些指标继续保留、哪些新增 contract 只需要 audit / contract evidence、哪些 coverage gap 必须补，而不是从头发明完整 evaluation framework。

### 9. Evaluation Calibration & Minimal Eval Suite

**文档名：**

```
C设计9-Evaluation Calibration & Minimal Eval Suite v0
```

**Purpose：**

基于现有 evaluation assets、已有 datasets、已有 MQ / Callback / FVI 目标、已有 audit/probe 工作，以及 C设计0-8 的机制 contract，设计一个最小、可执行、可诊断的 AI evaluation suite。

It should preserve and calibrate existing evaluation work rather than replacing it.

**核心问题：**

- 当前已有 evaluation docs / dataset / probe / snapshot / judge prompt / eval runner 是什么？
- 现有 Memory Quality / Spontaneous Callback / False Visible Integration 能覆盖哪些失败模式？
- MQ / Callback / FVI 是否保留，以及如何根据 C设计0-8 调整或拔高？
- Memory 和 Planning 哪些关键行为必须被 eval 覆盖？
- 哪些机制只需要 audit / contract evidence，不需要新增 LLM judge？
- 哪些 coverage gap 是 blocking，哪些可以暂缓？
- 哪些 evaluation 暂时不做？
- 如何保持指标数量少、可执行、可诊断？

**Existing evaluation work priority：**

```text
Memory Quality
Spontaneous Callback
False Visible Integration
memory quality probe snapshots
existing eval docs / datasets / judge prompts / eval runner, if present
read_audit / settlement_audit / retrieval utilization trace / slow-cycle audit as evidence
```

C设计9 应先 inventory existing evaluation assets，再决定是否补新数据或新 rubric。

**明确非目标：**

```text
no new giant benchmark
no broad metric taxonomy
no full evaluation platform
no full Memory Evaluation encyclopedia
no full Planning Evaluation encyclopedia
no unit-test / integration-test design
no Codex task list
```

最小评测方向应是：

```text
Main evaluation targets:
- Memory Quality
- Spontaneous Callback / Callback Quality
- False Visible Integration
- Planning Trace Quality, lightweight
- Slow-cycle Promotion Safety, lightweight

Diagnostic tags / failure attribution:
- formation_issue
- settlement_issue
- management_issue
- retrieval_issue
- utilization_issue
- stale_memory_issue
- source_grounding_issue
- reaction_semanticization_issue
- knowledge_activation_source_truth_issue
- detour_recovery_issue
- slow_cycle_promotion_issue
- audit_missing_issue
```

Diagnostic tags 不一定是独立指标，不应扩展成一堆复杂分数。

Planning 只补最小 trace checks：

```text
Navigation Groundedness
Mainline Continuity
Detour Precision / Recovery
Planning-Memory Alignment
```

Look-back / Active Recall Appropriateness 可以作为 Planning Trace Quality 的 diagnostic tag，除非 C设计9 证明它需要独立 judge rubric。

### Phase 6：Optional Detailed Evaluation Pages

### 10 / 11. Audit & Evaluation Design, optional / only if needed

Calibration 后再决定是否拆分：

```text
情况 A：已有评测基本够
  不拆大文档；C设计9 输出 eval coverage / audit coverage / handoff requirements，
  交给 Implementation Handoff 决定 judge prompt implementation、eval runner implementation 和 engineering tests。

情况 B：Memory 评测需要细化，Planning 只需要 tags
  只写 C设计10-Memory Audit & Evaluation Design v0。

情况 C：Planning 评测确实复杂
  再写 C设计11-Planning Audit & Evaluation Design v0。
```

如果拆分，这两篇应继承 calibration 的结论，保持短文档，不再扩张成评测百科。

**Memory Audit & Evaluation Design, optional / only if needed**

**文档名：**

```
C设计10-Memory Audit & Evaluation Design v0
```

**核心问题：**

- only if C设计9 proves it is needed；
- focus on MQ / Callback / FVI rubric and dataset alignment；
- 对 formation / settlement / management / retrieval / utilization / slow-cycle 做 stage-aware failure attribution；
- should not invent many metrics。

**Planning Audit & Evaluation Design, optional / only if needed**

**文档名：**

```
C设计11-Planning Audit & Evaluation Design v0
```

**核心问题：**

- only if C设计9 proves it is needed；
- 只在 Planning evaluation 不能用轻量 trace-quality tags 表达时单独写；
- 聚焦 Navigation Groundedness、Mainline Continuity、Detour Precision / Recovery、Planning-Memory Alignment；
- should remain trace-based and lightweight；
- 不把 visible route disclosure 做成 route steering 或 UI evaluation。

------

### Phase 7：Integration and Implementation Handoff

### 12. Integrated Agent Mechanism Design

**文档名：**

```
Integrated Attentional v2 Mechanism Design v0
```

**核心问题：**

- 如何整合 C设计0-9，以及 optional 10/11 if present？
- Memory 和 Planning 的接口是什么？
- Navigate、Read、Runner、Settlement、Slow-cycle、State Projection、Audit 的完整闭环是什么？
- 哪些设计已经 accepted？
- 哪些仍是 open question？
- 哪些不进入本轮实现？

### 13. Codex Implementation Handoff

**文档名：**

```
Codex Implementation Handoff v0
```

**核心问题：**

- 哪些改动先做？
- 哪些 schema delta？
- 哪些 prompt delta？
- 哪些 state_ops delta？
- 哪些 observability / audit fields 加？
- 哪些 eval runner / judge prompt implementation 加？
- 哪些 engineering tests / regression tests 加？
- 哪些必须保持 backward compatibility？
- 哪些暂不实现？

这个阶段才适合交给 Codex。前面设计阶段不要急着让 Codex 拆 task。

## 推荐顺序总表

| 顺序 | 设计文档                           | 为什么先做                                                   | 依赖                                  |
| ---- | ---------------------------------- | ------------------------------------------------------------ | ------------------------------------- |
| 0    | Shared Memory-Planning Mechanism Charter | 先统一边界，避免 Memory / Planning 各说各话                  | 两份评估报告                          |
| 1    | Memory Ontology                    | 后续 formation、management、retrieval 都依赖 store 身份      | Charter                               |
| 2    | Planning Ontology                  | 后续 navigation、route disclosure、audit 都依赖 planning 对象定义 | Charter + Memory Ontology 初稿        |
| 3    | Memory Formation & Settlement      | 解决 `Read.memory_uptake_ops` 和 settlement 权限             | Memory Ontology                       |
| 4    | Navigation Policy                  | 解决 `Navigate.choose_next_unit` 职责与主线纪律              | Planning Ontology                     |
| 5    | Memory Management & Evolution      | 解决 lifecycle、supersede、cool、resolve                     | Memory Formation                      |
| 6    | Detour / Look-back / Active Recall Policy | 横跨 planning 和 memory，定义回看、绕路、召回                | Navigation + Memory Ontology          |
| 7    | Memory Retrieval & Utilization     | 定义 retrieval intent 和 context assembly                    | Memory Ontology + Management + Detour |
| 8    | Slow-cycle / Macro-planning        | 定义 consolidation、carry-forward、macro planning            | Memory Management + Planning Ontology |
| 9    | Evaluation Calibration & Minimal Eval Suite | 复用现有 MQ / Callback / FVI 与 dataset/probe/audit，校准最小 eval suite | C设计0-8 + existing eval assets       |
| 10   | Memory Audit & Evaluation, optional / only if needed | 仅当 C设计9 证明 Memory 评测需独立展开时拆分                 | Evaluation Calibration + Memory pages |
| 11   | Planning Audit & Evaluation, optional / only if needed | 仅当 C设计9 证明 Planning trace checks 需要独立 judge rubric 时拆分 | Evaluation Calibration + Planning pages |
| 12   | Integrated Agent Mechanism Design  | 整合 C设计0-9，以及 optional 10/11 if present                 | Accepted design chain                 |
| 13   | Codex Implementation Handoff       | 交给 Codex 拆解实现，包括 engineering tests / regression tests | Integrated Design                     |

Visible Reading Route Surface Boundary 仍保留为 Future / deferred / optional，不属于当前 implementation track 的主编号。当前实现轨道只保留 internal route trace / audit / policy data，不实现 user route choice、route-surface accept/reject 或 route steering。

## 每个新会话应该怎么输入

每次新开一个设计会话，建议输入包保持固定：

```
1. 设计目标：本次只写哪一页
2. 当前 GitHub repo
3. Memory / Planning 评估报告中对应章节
4. External Evidence Pack 中对应 work / source appendix
5. 已经 accepted 的前置设计页
6. 明确非目标：不写实现路线、不扩张到其他模块、不新增复杂基础设施
```

例如写 Memory Formation 时，输入：

```
- Shared Design Charter
- Memory Ontology Design v0
- Memory Assessment Report 中 Formation / Write Contract 相关部分
- Memory External Evidence Pack 中 Mem0、HaluMem、LangGraph、Generative Agents、Zep 相关 work cards
- GitHub repo 当前 schemas.py / state_ops.py / runner.py / prompts.py / observability.py
```

写 Navigation Policy 时，输入：

```
- Shared Design Charter
- Planning Ontology Design v0
- Planning Assessment Report 中 Navigation Policy 相关部分
- Planning External Evidence Pack 中 Information Foraging、ReAct、Plan-and-Solve、ReWOO、HTN/Options/MAXQ 相关部分
- GitHub repo 当前 nodes.py / runner.py / prompts.py / schemas.py / read_context.py
```

写 Evaluation Calibration 时，输入：

```
- C设计0-8 accepted contracts
- existing evaluation docs / datasets / probe snapshots / judge prompts / eval runner, if present
- Memory Quality 相关数据与 judge/rubric
- Spontaneous Callback / Callback Quality 相关数据与可见 callback 案例
- False Visible Integration 相关数据与 pollution / drift 案例
- read_audit / settlement_audit / retrieval utilization trace / slow-cycle audit as evidence
- Navigation / detour / look-back trace 样本
- Slow-cycle / continuation capsule / promotion safety 样本
- engineering tests 的现状只作为 handoff 参考，不作为 C设计9 核心任务
- 当前 repo 的 docs/current-state.md、docs/history/decision-log.md、docs/tasks/registry.md
```

## 最重要的流程原则

你现在最应该避免的是“一口气生成完整 Memory + Planning 总设计”。这会让模型重新变成泛泛而谈。

更好的节奏是：

```
先定边界
再定 ontology
再定核心节点 contract
再定 lifecycle / policy
再定 retrieval / slow-cycle
再做 evaluation calibration
最后按需定 audit / evaluation / integration / implementation
```

每一页完成后，你做一次人工判断：哪些接受，哪些删掉，哪些推迟。只有被接受的设计，才进入下一页输入。

进入评测层后，最重要的是避免“评测百科化”。评测设计应遵守：

```text
少量主指标 + 少量 diagnostic tags + audit-backed failure attribution；
保留 MQ / Callback / FVI；
Planning 只补最小 trace-quality eval；
Contract / Audit Checks 提供 evaluation evidence，不等于产品质量分数；
Engineering Tests 留给 Codex Implementation Handoff；
新增 contract 优先判断是否靠 audit coverage 即可检查；
不设计全新 benchmark、复杂指标库或 full automated evaluation platform。
```

当前下一步是 **C设计9-Evaluation Calibration & Minimal Eval Suite v0**。它应先校准现有评测资产与 C设计0-8 的 contract，确保 necessary evaluation coverage is not missing，再决定是否需要拆出 Memory Audit & Evaluation 或 Planning Audit & Evaluation。

------

英文表达可以这样说：

> “We should move from evidence-informed assessment to modular design, using the assessments as the primary design brief and the evidence packs as citation-backed reference material.”

有用表达：**primary design brief**，意思是“主要设计简报 / 主要设计输入”。
