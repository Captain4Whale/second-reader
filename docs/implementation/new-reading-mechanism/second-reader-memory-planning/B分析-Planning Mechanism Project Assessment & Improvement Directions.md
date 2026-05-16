# Planning Mechanism Project Assessment & Improvement Directions

## 证据边界说明

本报告使用 `Planning External Evidence Pack v1` 作为外部工作索引，但不把它作为外部依据引用。正文中提到的外部依据均回到具体论文、官方文档或官方项目页面层面表述，并在文末 Source Usage Appendix 列出稳定来源。

本轮能读取 GitHub repo 文档与核心代码，并读取了当前项目文档中记录的运行诊断摘要；但没有逐条打开真实运行目录中的 `read_audit.jsonl / settlement_audit.jsonl / unit_span_ledger.jsonl / active_attention.json / concept_registry.json / thread_trace.json` 做逐行 runtime artifact 审计。因此，下面对 runtime quality 的判断主要是 **architecture-level 与 contract-level 评价**，辅以 repo 文档记录的诊断结果；不是充分的运行质量验证。

------

# 1. Executive Assessment

Reading Companion 当前 `attentional_v2` 的 Planning / Navigation / Recommendation 机制，整体处在 **“阅读过程专用 planning 的合理中期架构”**。它已经明显超过“LLM 随机继续读下一段”的早期形态：当前机制有 `Navigate.choose_next_unit -> Read -> Reading Runner post-read settlement` 的稳定主循环，有 paragraph-offset `SourceCursor / SourceSpan`，有 `Unit Span Ledger` 记录 accepted unit，有 `active_attention / concept_registry / thread_trace / reflective_frames` 作为持续状态层，有 bounded `active_recall / look_back`，也有 `detour_need -> Navigate-owned detour` 的机制雏形。机制文档明确指出当前循环由 `Navigate.choose_next_unit` 选择下一阅读单元，`Read` 产生 `reading_impression / surfaced_reactions / memory_uptake_ops / detour_need`，随后由 Reading Runner 确定性 settlement、写 audit、推进 cursor。

## Erratum / Interpretation Patch

本文早先使用的 “Recommendation Policy” gap 现在应解释为 **Visible Reading Route Surface Boundary** gap，而不是要求设计一个 recommender system。Second Reader remains an independent reader：users do not choose its route. Future user-visible surfaces may disclose, summarize, or annotate the reader's route, but must not create route steering, accept/reject navigation states, or learning-path controls.

它相对主流 Agent Planning 工作做对的最大一点，是没有把阅读误建模成 AutoGPT-style task execution。项目产品定位也支持这一点：Reading Companion 的核心不是摘要器，也不是服务式助手，而是一个 text-grounded、legible、self-propelled 的共同阅读心智。 这意味着 planning 的对象不是“完成一个外部任务”，而是 **source-grounded reading path planning / attention scheduling / navigation support**。从这个角度看，当前采用 deterministic runner + bounded LLM nodes，而不是大型 planner agent、多 agent workflow 或 MCTS 主循环，是正确克制。

当前最大的短板不是缺少“更强 planner”，而是 **planning ontology 与 navigation / visible route disclosure boundary 尚未正式命名和收紧**。`Navigate.choose_next_unit` 实际上同时承担 next-unit selector、source-grounded navigator、micro-planner、detour localizer 的职责；但这些职责还没有形成清晰 policy。Internal navigation 与 visible route disclosure 也还没有正式分层：系统现在有 visible reactions、`prior_link / outside_link / search_intent` 等面向用户的阅读痕迹，但还没有清楚定义哪些 route trace 可以未来展示、哪些永远只是 internal audit。

当前最不应该复杂化的方向是：新增大型 planner node、multi-agent reading team、graph workflow rewrite、把 Tree of Thoughts / LATS / MCTS 作为每个 next-unit decision 的默认主循环、让 recommendation 取代 source-order reading、把 planning reasoning 全部展示给用户、或把 planning state 与 memory state 合并成一个大 store。这些方向都很诱人，但对当前项目的阻塞问题帮助不大，反而会破坏 Simplicity and Universality。

必须分层看成熟度：

- **Architecture-level maturity：中高。** 主循环、source locus、state packet、detour skeleton、slow-cycle、audit 文件体系都已经存在。共享机制边界也明确规定 `public/book_document.json` 是 shared parsed-book truth，`attentional_v2` 使用 paragraph + char-offset cursor，当前 source citations 使用 inline paragraph-offset `SourceRef`，而不是共享 Anchor Bank。
- **Contract-level maturity：中等。** `ReadResult` 与 `NavigateNextUnitResult` 已有类型结构，schemas 中也定义了 `SourceRef`、`StateOperationType`、`DetourNeed`、`NavigateActResult`、`ConceptRegistryEntry`、`ThreadTraceEntry` 等关键对象。 但 planning option、navigation reason、detour exit、rejected alternatives、recommendation rationale、uncertainty、budget reason 等契约仍不足。
- **Runtime-quality maturity：低到中。** 当前 state 文档记录过一次 no-judge settlement-audit diagnostic：`59` 条 read-audit、`59` 条 settlement-audit，`29 / 59` 个 read units 产生 `31` 个 memory ops，且诊断发现并修复了 durable-store field-shape alignment 与 SourceRef carry-forward 问题。 但本报告没有逐行审计 runtime artifacts，因此不能断言真实运行质量已经充分稳定。

各模块成熟度判断如下：

- **Planning：中等。** 已有 micro / meso / macro 雏形，但 ontology 未正式化。
- **Navigation：中高。** `Navigate.choose_next_unit` 已经是合理的 source-grounded navigator，但 policy language 不够清晰。
- **Detour / Look-back / Active Recall：中等偏低。** 机制存在，但触发条件、退出条件、恢复主线规则、收益判断仍需 policy 化。
- **Visible Route Disclosure Boundary：低且 deferred。** 当前更像 visible reading trace 与 surfaced links，还不是成熟 route disclosure surface；这不意味着当前需要 recommender system。
- **Planning Audit / Evaluation：中等。** audit 与长跨度 evaluation 方向正确，但缺 planning-specific trace fields 与 planning metrics。

后续设计应围绕八个页面展开：Planning Ontology、Navigation Policy、Detour / Look-back / Active Recall Policy、Visible Reading Route Surface Boundary、Slow-cycle / Macro-planning、Planning Audit / Observability、Planning Evaluation、Orchestration / Infrastructure。

------

# 2. Current Project Level Assessment

## 2.1 What is already strong

当前最强的地方，是项目已经有一个清晰的阅读主循环，而不是把所有判断塞进一个大 prompt。`attentional_v2` 当前运行解释为：Reading Runner 维护 paragraph-offset `SourceCursor`，`Navigate.choose_next_unit` 接收 adaptive source preview 并返回 `end_anchor_text`，runner 将其解析为 accepted `SourceSpan`，`Read` 读取这个 unit，随后 runner 应用 memory uptake、持久化 surfaced reactions、写 audit、记录 accepted unit span、推进 cursor。 这与 ReAct 的 “reasoning + acting + observation correction” 有局部相似性：系统不是一次性想完全局计划，而是在 source observation 之后更新下一步。但 Reading Companion 的差异在于，observation 首先来自 source text，而不是工具环境；因此 ReAct 只能作为局部 detour / correction loop 的参照，不能作为全局阅读架构。

第二个强项是 source-grounded reading locus 已经很扎实。项目从 sentence-id traversal 转向 paragraph-offset cursor，`SourceSpan` 是 end-exclusive `[start_cursor, end_cursor)`，`unit_span_ledger.jsonl` 是 accepted unit fact。SourceRef cutover 也已经落地，新 runtime/checkpoint truth 不再依赖 Anchor Bank，而是 memory / reaction / probe-facing source evidence 使用 inline paragraph-offset `source_refs[]`。 这与 Information Foraging 的信息空间导航非常接近：下一步不是抽象任务动作，而是从当前 source locus 判断是否继续当前 patch、切换 patch、回看或 detour。相似点是都依赖局部线索和 value / cost；差异是 Reading Companion 必须维护 source-order continuity，而不是自由搜索。

第三个强项是 deterministic runner 已经承担了轻量 orchestration。Reading Runner 确定性负责 post-read settlement、cursor advancement、runtime persistence，而 LLM 节点只在 bounded slots 中做语义判断。 这与 HTN / Options / MAXQ 的分层思想相近：高层选择 temporally extended option，低层执行器完成受控步骤。Reading Companion 本地化得更轻：不是引入 formal planner 或 RL decomposition，而是让 runner 作为 deterministic executor，让 `Navigate` 做 local selection，让 slow-cycle 处理 chapter-level carry-forward。

第四个强项是 Read 与 Navigate 已经不是完全混在一起。`Navigate.choose_next_unit` 是 current selector，`Read` 是 current unit reader；`Read` 不再是 checklist-filling state updater，而是先产生 reader-like impression，再 surfaced reactions，再 bounded memory uptake，再可选 detour_need。 这与 Plan-and-Solve 的 “先计划、再执行” 有 analogical support，但 Reading Companion 不应把每个 unit 都变成完整 planner-executor。更准确地说，`Navigate` 是 micro navigation decision，`Read` 是 grounded interpretation，runner 是 settlement executor。

第五个强项是 detour 已经被放进同一个阅读 loop，而不是作为隐式 side channel。机制文档明确说 detour 是 normal reading redirection；一旦 detour region 被选择，它通过同样的 `Navigate.choose_next_unit -> read -> settlement` 路径读取，而不是第二套读取机制。 这非常重要。ReWOO 可以启发局部 detour bundle 的成本控制，但 Reading Companion 现在更正确的选择是：先保持 detour 与 mainline 同 loop，避免出现一个不可审计的隐藏搜索器。

第六个强项是 bounded carry-forward packet 已经存在。`state_projection.py` 会构造 `state_packet.v1`，其中 active attention 最多取 6 条、concept digest 3 条、thread digest 3 条、source_ref_digest 8 条，并将 reaction、concept、thread、reflective items 投影为 prompt-facing refs。 这与 LangGraph / Letta / MemGPT 一类框架的 state projection / core-vs-archival 思想相近：不是把所有 state 塞进 prompt，而是形成 bounded prompt-facing projection。差异是 Reading Companion 的 projection 以 source-grounded reading state 为中心，不是用户画像或 persona memory。

第七个强项是 audit 与 evaluation 已经开始对准真正问题。`observability.py` 记录 read-audit：unitize decision、source span、carry_forward_ref_ids、context_request、supplemental steps、stop_reason、budget_exhausted、reading_impression、surfaced reactions、memory uptake ops、detour_need；settlement-audit 记录 memory op counts、target-store distribution、active_attention / concept_registry / thread_trace / reaction_records 的 id deltas。 长跨度 evaluation 也已经从旧的 target-centered accumulation 转向 `Memory Quality / Spontaneous Callback / False Visible Integration`，并明确 Memory Quality 不要求 gold sentences，而是整体判断当前 state 是否保留重要、主线、组织清晰、faithful 的内容。 这与 OpenAI trace grading、WebArena、τ-bench、ResQue、McNee 等工作共同提醒的方向一致：不能只看最终结果，必须看 trace、usefulness、reliability、failure localization。

第八个强项是当前没有过早引入大型 planner / graph workflow / multi-agent runtime。这一点在工程上可能显得“不够炫”，但对项目是强项。Tree of Thoughts、Graph of Thoughts、LATS 都说明 search-based deliberation 对 hard reasoning 有价值，但也带来显著成本、评估难度和 value function 问题。Reading Companion 当前主任务是持续阅读，不是每一步都需要 search tree。

## 2.2 What is weak, underspecified, or risky

最核心的弱点是 Planning Ontology 没有正式命名。当前项目事实已经说明：`Navigate.choose_next_unit` 选择 next coverage unit，`Read` 读 accepted source unit，settlement 确定性推进，slow-cycle 做 consolidation。 但“Planning”在这里到底指什么，还未形成正式定义。它不是 AutoGPT-style task planning，也不是 classical planner；更像 source-grounded navigation、attention scheduling、reading path control。HTN、Options、MAXQ 提醒我们，层级分工很重要；Information Foraging 提醒我们，下一步读哪里更像 value / cost / scent 判断；ReAct 提醒我们，局部 observation correction 有价值。但这些外部工作都不能直接替 Reading Companion 定义 planning。这里需要 project-specific ontology。

第二个风险是 `Navigate.choose_next_unit` 的职责边界不够清楚。它现在是唯一 current selector，主线 unitization 与 detour localization 都是这个 entrypoint 内的模式。 这在架构上很好，但 policy 上容易过宽：它到底是 next-unit selector、micro-planner、source-grounded navigator、router，还是 detour controller？如果职责不清，后续很容易把 recommendation、detour、look-back、deep-dive、mainline continuity 全部塞给 Navigate，导致 prompt 变成万能 planner。

第三个缺口是 internal navigation 与 visible route disclosure 尚未区分。当前 `Read.surfaced_reactions` 能包含 `prior_link / outside_link / search_intent`，reaction audit 也把这些作为 support evidence。 但这还不是 route disclosure boundary。Adaptive Hypermedia 和 Adaptive Navigation Support 告诉我们，navigation support 可以是 direct guidance、annotation、sorting、hiding、meta-adaptation；Learner Agency 和 Open Learner Model 只作为 display-boundary 参考。Reading Companion 当前缺的是：哪些是系统内部下一步读哪里，哪些只是未来可展示的 route trace，哪些只是 visible thought。

第四个风险是 detour / look-back / active recall 有机制，但 policy 不够清楚。`read_context.py` 中 `look_back` 会基于 source refs 返回 bounded earlier source excerpts，`active_recall` 会从 concept/thread/reaction records 中补充尚未 carry 的内容。 这是强雏形。但什么时候应该 look-back？什么时候应该 active recall？什么时候应该 detour？detour 的退出条件是什么？如何恢复主线？这些还未被正式 policy 化。Information Foraging 的 value / cost / scent 与 rereading / metacomprehension literature 都提醒：回看与 detour 不能只靠“感觉可能有用”；它们必须服务 comprehension calibration 或 source-grounded value，而不是 novelty chasing。

第五个缺口是 mainline continuity 的硬约束还没有作为 policy language 明确表达。当前 cursor 和 runner 能保证 coverage，但 policy 上还需要定义：默认继续主线，detour 必须有足够 value / source scent / unresolved need，look-back 必须有 calibration 或 evidence value，deep-dive 必须有明确收益与退出条件。否则机制虽然 source-grounded，仍可能因过多 detour 或 active recall 失焦。Information Foraging 支持 value-cost tradeoff，但 Reading Companion 需要把 value 函数本地化为 “理解收益 + 主线连续性 + source-grounding + 用户可读性”。

第六个风险是 slow-cycle 是否是 macro-planning 尚未正式定义。代码中 slow-cycle 包含 reflective promotion、reconsolidation、chapter consolidation、reaction compatibility projection 等。 这很像 macro-level carry-forward planning，但它也可能与 memory consolidation 混淆。Reflexion 支持 episode-between reflection / strategy memory，但 Reading Companion 不应把 slow-cycle 变成会自我学习策略的 planner manager。它应先被定义为 chapter boundary / session boundary 的 consolidation 与 carry-forward selection，不是“全书 planner agent”。

第七个风险是 planning audit 缺少最小 decision fields。当前 read/settlement audit 已经很好，但 Navigation audit 仍应补 candidate options、selected option、rejected alternatives、source evidence、memory used、uncertainty、budget reason、restore-mainline reason。OpenAI trace grading、WebArena、τ-bench 的启发是：要分清 planner 错、executor 错、retrieval 错、memory 错，不能只看最终 outcome。Reading Companion 不需要 dump full hidden reasoning，但需要 structured decision summary。

第八个缺口是 planning evaluation 还没有独立成体系。当前 active long-span direction 很接近 memory / visible callback / FVI，但对 planning 本身还缺 Reading Path Quality、Navigation Groundedness、Mainline Continuity、Detour Precision、Recovery Quality、Visible Route Disclosure Readiness、Overplanning / Thrashing Rate、Planning-Memory Alignment 等指标。McNee “Being Accurate Is Not Enough” 和 ResQue 都提醒，recommendation 不能只看准确率；WebArena / τ-bench 提醒，长链路 agent 要看 reliability 与 repeated-run consistency。Reading Companion 需要借鉴这些评估思想，而不是照搬 benchmark。

## 2.3 What is currently over-risky or not worth doing

新增大型 planner node 很诱人，因为它能把 “planning” 变成显式模块。但当前已有 `Navigate`、`Read`、runner、slow-cycle；问题不是缺一个 planner，而是职责边界、policy vocabulary、audit fields 尚不清楚。Plan-and-Solve 支持在复杂问题前先 plan，但它不支持每个阅读 unit 都引入 planner。对 Reading Companion，本地化应是边界式 plan sketch，而不是全局 planner node。

引入 multi-agent reading team 也不值得。AutoGen / CrewAI 等 multi-agent 体系适合多角色协作任务，但 Reading Companion 的产品不是多 agent debating room。它需要一个连贯的 co-reader mind。如果拆成 navigator agent、memory agent、critic agent、recommendation agent，很可能破坏产品体验与 source-grounded audit。

现在做 graph workflow rewrite 风险也大。LangGraph 的 durable execution、checkpoint、interrupt、trace 思想很有用，但当前 deterministic runner 已经是 orchestrator。Reading Companion 可以借 checkpoint / interrupt / trace / human-review gate 的思想，不必把整个 loop 重构成 graph runtime。基础设施迁移不能替代 reading judgment。

Tree of Thoughts / LATS / MCTS 作为默认 reading loop 应拒绝。ToT 和 LATS 对 deliberate reasoning、search、backtracking 有价值，但普通阅读主循环缺少明确 reward/value function，也对延迟极敏感。它们可作为 hard passage / deep-dive 的 later optional technique，而不是 next-unit 默认策略。

让 recommendation 取代 source-order reading 也应拒绝。Adaptive Navigation Support 支持提示与 annotation，但不是让系统接管用户路径。Course Sequencing 与 Learning Path Recommendation 说明 path recommendation 需要 goal、prior knowledge、prerequisite；Reading Companion 当前不是 learning path platform。Source-order discipline 仍应是默认。

把所有 planning reasoning 展示给用户不应做。Open Learner Model 与 controllability / explainability literature 支持可解释与可控，但不是暴露内部 chain-of-thought 或所有 rejected alternatives。用户需要的是 concise rationale、source grounding性，而不是内部 planner trace。

把 planning 和 memory 合并成同一 state store 不应做。Planning state 是下一步选择与 policy trace；memory state 是 source-grounded reading state；audit trace 是诊断记录；visible route disclosure 是交互建议。Zep、LangGraph、Letta 都提醒 state / memory / trace / context projection 应分层。

现在做复杂 learning path engine 或 full learner model 也不合适。Learner Agency、Open Learner Model、Course Sequencing 都有价值，但它们通常依赖明确学习目标、mastery model、prerequisite graph。Reading Companion 当前不是 tutoring system，也不应假装拥有完整 learner model。

------

# 3. Layered Improvement Analysis

## 3.1 Planning Ontology and Boundaries

### Current state and gap

当前项目的真实 planning 已经分散在多个层：survey 形成 body-first `reading_plan`，`Navigate.choose_next_unit` 做 next source unit selection，`Read` 产生 `detour_need` 和 `memory_uptake_ops`，runner 确定性推进 cursor，slow-cycle 做 chapter-end consolidation。机制文档还明确：survey 只做 orientation，不产生 visible reactions，也不写 durable reading memory；Navigate 不拥有 book-level chapter ordering，Reading Runner 消费 survey 的 reading_plan。

缺口是：这些 planning 行为没有被统一命名为一个本地 ontology。外部 Agent Planning 里的 “plan” 往往是 task decomposition；但 Reading Companion 的对象是 reading locus、attention、source-order continuity、detour / recall / recommendation，而不是完成外部任务。

### Improvement directions

**首先，应把 Planning 定义为 “source-grounded reading path planning / attention scheduling”，而不是 AutoGPT-style task planning。** HTN Planning 的层级任务分解、Options Framework 的 temporally extended action、MAXQ 的 controller-worker separation 都支持将长过程拆成层级，但 Reading Companion 的“任务”不是外部行动，而是阅读过程。可本地化为三层：micro planning 是 next unit / look-back / recall 的选择；meso planning 是 detour / deep-dive / chapter-local thread management；macro planning 是 chapter-end carry-forward、reflective frame、reading plan adjustment。这样既吸收层级思想，又不引入 formal planner。

**其次，source text、reading locus、memory state、planning state、audit trace、visible route disclosure 必须分开。** 项目已经把 `book_document.json` 作为 shared source truth，`_mechanisms/attentional_v2/` 作为机制私有 artifact territory，且当前 source citations 使用 inline SourceRef。 这应转化为 planning ontology：source text 是可被阅读和引用的 substrate；reading locus 是当前 cursor / accepted span；memory state 是已形成的 source-grounded reading state；planning state 是当前 pending decision / detour / mainline obligation；audit trace 是事后诊断；recommendation 是可展示给用户的 guidance。LangGraph / OpenAI Agents SDK 的 state / orchestration / trace 分层可以作为基础设施类比，但 Reading Companion 应使用自己的 reading ontology。

**第三，internal navigation 与 visible route disclosure 必须分层。** Adaptive Navigation Support 说明 navigation support 可以强弱不同：direct guidance、annotation、sorting、hiding、meta-adaptation。Learner Agency 研究则提醒，推荐应该支持用户目标与选择，而不是替用户决定。Reading Companion 本地化后，应让 internal navigation 决定系统下一步读哪里；visible route disclosure 只在必要时对用户提出“你可能要回看这里 / 这个 detour 值得看 / 当前最好继续主线”等支架。两者不能混用同一个 “recommendation” 词。

**第四，planning state 应与 memory state 分开，但暂不需要新增大型 planning store。** 当前 `local_continuity` 已经保存 `mainline_cursor / active_detour_id / active_detour_need / detour_trace`，这已经是轻量 planning state。 未来可以在现有 runtime artifacts 上补充 planning audit fields，而不是立即新增 planning_store。新增 store 的条件应是：existing local_continuity + audit 已无法表达 bounded planning obligations / compact rejected alternatives / restore-mainline obligations。

### Design implications

- Planning Ontology 页面应定义：micro / meso / macro planning。
- `source corpus != memory != plan != audit != recommendation` 必须成为硬边界。
- `local_continuity` 可作为轻量 planning state 起点，不急于新增 planning store。
- Internal navigation 与 visible route disclosure 分层命名。
- 避免 AutoGPT/task-planner language；优先使用 reading path、attention scheduling、source-grounded navigation。

------

## 3.2 Navigation Policy

### Current state and gap

`Navigate.choose_next_unit` 当前是唯一 current selector。它接收 adaptive paragraph-offset preview，返回 `end_anchor_text`，主线 unitization 与 detour localization 都是同一个 entrypoint 内的模式。它在 active detour 时可以请求 mechanism-private book-local skills：`source_map_overview / source_scope_drilldown / source_window_fetch`；这些 skills 不读未来文本、不做语义 relevance judgment、不访问外部网络，只提供 source evidence。

这是一种很好的 architecture，但 policy 上仍需要回答：Navigate 到底怎么判断 continue、look-back、detour、defer、deep-dive？source-order discipline 是硬约束、默认偏好，还是可被 detour 覆盖的规则？当前 `Navigate` 不应变成大型 planner，但也不能只是 anchor selector。

### Improvement directions

**第一，Navigation Policy 应把 source-order discipline 明确化为 default hard preference。** Reading Runner 的 cursor 和 unit span ledger 已经保障 coverage，但 policy 还应说清楚：没有明确 detour / look-back / active recall rationale 时，默认继续主线。Information Foraging 的 patch model 支持 stay / leave 的 value-cost判断；Reading Companion 应本地化为：mainline continuity 本身有价值，detour 必须证明边际收益高于 continuity cost。这个判断不是外部 work 的直接答案，而是 project-specific judgment，因为阅读书本与 web search 不同，source order 经常承载作者结构。

**第二，Navigate 应被定义为 source-grounded navigator / next-unit selector，而不是独立 planner node。** ReAct 支持局部 observation-grounded correction，但不要求全局 planner；Plan-and-Solve 支持复杂问题前 plan，但不是每步 plan；ReWOO 支持将 reasoning 与 observation 解耦以降成本，但更适合局部 multi-hop detour。对 Reading Companion，本地化是：Navigate 做局部下一单位选择，必要时请求 source-evidence skill；它不应生成整章完整计划，也不应重写 reading plan。

**第三，Navigation decision language 应引入 value / cost / scent，但保持轻量。** Information Foraging 的 information scent、rate-of-gain、patch switching 很适合“下一步读哪里”。Reading Companion 可以用几个本地字段：`mainline_value`、`continuity_cost`、`detour_scent`、`lookback_value`、`uncertainty`、`source_evidence`。不需要数值模型；可以作为 structured reason categories。这样比“LLM reason free text”更可审计，也能帮助 evaluation 判断是否 novelty chasing。

**第四，continuation、look-back、detour、defer、deep-dive 应作为 policy options，而不是分散动作。** 当前 schemas 中 `NavigateActDecision` 有 `choose_unit / request_skill / defer_detour`，selection mode 有 `mainline / detour / deferred`。 这还不够表达 look-back 或 active recall，因为它们目前在 `Read` supplemental context 层。设计上应明确：Navigation Policy 决定下一 source unit；Read-context policy 决定是否补 active recall / look-back；Detour Policy 决定是否打开/关闭 active detour。三者互通，但不应互相吞掉职责。

### Design implications

- Navigation Policy 页面应正式定义 Navigate 是 source-grounded next-unit selector。
- Source-order continuity 是默认偏好；detour 是例外，需要 value / evidence。
- Navigation reason 应使用 value / cost / scent / continuity / uncertainty 语言。
- 不新增 independent planner node。
- Navigate 的 book-local skills 是 source evidence layer，不是 tool-use agent loop。
- Mainline、detour、defer、look-back、active recall 应有清晰归属。

------

## 3.3 Detour / Look-back / Active Recall Policy

### Current state and gap

当前项目已经有三个相关机制：`detour_need`、`look_back`、`active_recall`。`Read` 可以输出 bounded `detour_need`，runner 写入 `local_continuity`，下一个 Navigate 在 active-detour mode 下定位；`look_back` 会根据 source refs / spans 返回 earlier source excerpt；`active_recall` 会从 concept registry、thread trace、reaction records 中拿出尚未 carry 的内容。

差距是 policy。机制存在不等于知道何时用。当前需要避免三个风险：novelty chasing、over-search、为了回看而回看。还需要定义 detour exit 与 mainline recovery。

### Improvement directions

**第一，look-back 应被定义为 calibration move，不是默认 reread。** Rereading effect 和 metacomprehension research 支持一个关键点：回看有价值，常常因为它改善理解校准，而不是因为重复阅读本身总有益。Reading Companion 本地化后，look-back 触发条件应包括：当前 unit 依赖 earlier definition / distinction；memory 与当前 source 出现冲突；用户-facing callback 需要验证；当前理解不稳定且 earlier source_ref 可定位。它不应因为“有点相关”就回看。`look_back` 已经返回 bounded earlier source span，这是好边界；需要补的是 trigger reason 与 post-lookback use。

**第二，active recall 应区别于 look-back。** Active recall 从 memory state 取回概念、线程、反应；look-back 回到 source text。两者的功能不同：active recall 用于恢复已形成的 reading state，look-back 用于重新检查 source evidence。ReAct 的 observation correction 支持 source evidence 能纠正 reasoning；LongMemEval 的 retrieval vs reading distinction提醒我们，retrieved memory 不等于 source verification。Reading Companion 应要求：当问题是“我之前怎么理解这条 thread？”用 active recall；当问题是“原文到底怎么说？”用 look-back。

**第三，detour 应有明确开场、预算、退出与恢复主线。** 当前 detour trace 中记录 `detour_id / origin_cursor / origin_target_hint / status`，active detour 可以 choose unit、request skill、defer。 但 policy 应补：detour 开启必须有 source-grounded target_hint；detour 只能读 already-read source region 或当前允许范围内 source，不读未来；detour 成功条件是 resolve / clarify / reject / defer；detour 结束后必须记录 restore-mainline reason，并回到 `mainline_cursor`。Options Framework 的 termination condition 很适合这里：detour 是 temporally extended option，必须有终止条件。

**第四，detour 价值应按 information scent + reading value 判断。** Information Foraging 支持 value-cost-scent；Exploratory Search 支持开放理解过程，但也提醒会失焦。Reading Companion 的 detour value 不应只是新奇，而应是：是否修复当前理解缺口、是否解释当前 source 中 unresolved reference、是否支撑 mainline thread、是否帮助 later callback、是否会破坏主线节奏。若只是 thematic association，应倾向 defer 或 visible search_intent，而不是立即 detour。

**第五，active recall / detour 的评估应看 precision 与 recovery。** 如果 detour 很多但没改变后续 reading_impression 或 memory_uptake，就可能是 over-search。若 detour 后没有清楚恢复主线，就可能破坏阅读节奏。WebArena / τ-bench 的 recovery / reliability 思路可以类比支持：长链路系统要看是否能从偏离中恢复，而不只是看是否做了很多动作。

### Design implications

- Look-back 是 source calibration；active recall 是 memory recovery；detour 是 source-grounded path deviation。
- Detour 必须有 target_hint、origin_cursor、budget、exit status、restore-mainline reason。
- Detour 价值用 value / cost / scent 判断，避免 novelty chasing。
- Active recall 不应替代 source verification。
- Evaluation 应定义 Detour Precision、Recovery Quality、Over-search Rate。

------

## 3.4 Visible Reading Route Surface Boundary and User-facing Guidance

### Current state and gap

当前项目没有成熟的 visible route disclosure policy。它有 surfaced reactions、`prior_link / outside_link / search_intent`、visible mindstream，以及 future可能的 reading suggestion surface；但 internal navigation 与 visible route disclosure 尚未正式分层。产品文档也明确 explicit user-agent dialogue or steering 仍是 emerging territory，不是当前 canonical product identity。

这意味着 visible route disclosure 当前成熟度低，但不一定是坏事。Reading Companion 首先是 co-reader，不是 recommender system。当前需要保留的是 internal route trace 和 audit，不是让用户选择路线。

### Improvement directions

**第一，必须区分 internal navigation 与 visible route disclosure。** Internal navigation 是系统自己决定下一步读哪里；visible route disclosure 是未来可能展示“它刚才为什么这样读”的可见说明。Adaptive Hypermedia / Adaptive Navigation Support 只能作为边界参考：展示可以有强弱，但当前不设计 route control。Reading Companion 本地化后，应把 visible route disclosure 限制为 route trace / visible reading note / no_user_surface_needed。

**第二，visible reading note rationale 应可解释但不暴露全部内部 reasoning。** Learner Agency、Open Learner Model、Tsai & Brusilovsky 的 controllability / explainability work 只作为 display-boundary 参考。Reading Companion 不应展示所有 planner trace、candidate options、chain-of-thought。用户需要的是低打扰、source-grounded 的路线说明；内部 rejected alternatives 留在 audit。

**第三，visible route disclosure 必须保持 source-grounded、不过度控制用户。** Deschênes 的 learner agency review 支持系统不应替代学习者目标。Reading Companion 的本地化更强：用户不是 learner in a course sequence，而是读者；系统不是 tutor，而是第二读者。因此 route disclosure 只说明 Second Reader 做了什么，不设计接受 / 跳过 / 稍后 导致 route change。

**第四，当前不适合做完整 learning path recommendation 或 thematic path engine。** Course Sequencing 说明路径推荐需要 goal、prior knowledge、prerequisite；Learning Path Recommendation 不是 unordered related items top-N。Reading Companion 当前没有完整 learner model、课程目标或 prerequisite graph。因此 thematic path recommendation 应延后。可以先做 local “carry-forward focus” 或 “look-back point”，不要现在做全书 thematic itinerary。

**第五，推荐评价不能只看 accuracy 或 click-through。** McNee “Being Accurate Is Not Enough” 和 ResQue 支持 beyond-accuracy、user-centric usefulness、trust、satisfaction、interaction quality。Reading Companion 的 Visible Route Disclosure Readiness 应看：是否帮助理解、是否减少 thrashing、是否保留 agency、是否 source-grounded、是否用户是否不过度打断主线。

### Design implications

- Visible Reading Route Surface Boundary 页面应先定义 route trace / visible reading note / `no_user_surface_needed` 的展示边界。
- Internal navigation 与 visible route disclosure 分开。
- Rationale 面向用户，不暴露 full planning trace。
- Route disclosure 是 optional product surface，不是替用户读书，也不是让用户选路。
- 当前不做 full learner model、complex learning path engine、user-facing thematic path engine。
- Future display evaluation 应采用 legibility / grounding / low interruption，而非 accuracy-only 或 click-through。

------

## 3.5 Slow-cycle / Macro-planning

### Current state and gap

当前 slow-cycle 已经存在：reflective promotion、reconsolidation、chapter consolidation、carry-forward、compatibility projection 等都在 slow-cycle 代码和机制文档中出现。 这显然不只是 memory cleanup；它已经在决定哪些理解跨 chapter carry forward，哪些 active items 冷却，哪些 high-level frames 被 promoted。

缺口是它还没有被正式定位为 macro-planning / carry-forward planning，也没有清楚说明与 memory consolidation 的边界。

### Improvement directions

**第一，slow-cycle 应被定义为 macro-level carry-forward planning，而不是万能 planner。** Reflexion 的 verbal reinforcement learning 支持 episode-between reflection：失败经验与高层策略应在 episode 之间影响下一次尝试，而不是每步干预。Plan-and-Solve 支持在复杂边界处先规划；HTN / Options 支持不同时间尺度的 decision layer。Reading Companion 本地化后，slow-cycle 应处理 chapter boundary：哪些 active_attention 冷却 / carry forward，哪些 concept/thread 升级，哪些 reflective frame 形成，哪些 detour need 在 chapter-tail drain，哪些 unresolved concern 应保留到下一章。

**第二，slow-cycle 与 memory consolidation 要分工。** Memory consolidation 是“哪些 state 被稳定保存”；macro-planning 是“下一阶段阅读应该带着哪些 focus / obligations / unresolved questions”。二者重叠，但不等同。Reading Companion 当前可把 slow-cycle 输出拆成：state consolidation、carry-forward focus、open obligations、macro risks、optional next-focus suggestion。无需现在做复杂 plan tree。

**第三，slow-cycle 不应学习策略或自改 policy。** LangGraph / LangMem 的 prompt refinement as procedural memory 有启发，但当前项目不应让 slow-cycle 自行改 prompt。Reflexion 也提醒 reflection memory 若混入 content memory 会污染理解层。Reading Companion 当前应让 slow-cycle 产生 source-grounded reflective frames 和 carry-forward obligations，而不是 procedural strategy memory。

**第四，slow-cycle 应避免承担所有 macro-planning。** Survey 已经负责 book-level body-first scheduling；Navigate 负责 next-unit；Read 负责 detour_need；slow-cycle 负责 chapter/session carry-forward。不要让 slow-cycle 改 book queue、重排用户阅读路线、生成 thematic path、或替用户建立学习路径，除非后续设计明确新增权限。

### Design implications

- Slow-cycle 页面应定义为 chapter/session boundary 的 macro carry-forward planner。
- 输出应区分 consolidation、carry-forward focus、open obligation、resolved / superseded frame。
- 不做 self-learning strategy layer。
- 不让 slow-cycle 接管所有 macro-planning 或 recommendation。
- 它应服务 mainline continuity，而不是制造新路线。

------

## 3.6 Planning Audit and Observability

### Current state and gap

当前 `read_audit` 与 `settlement_audit` 已经能支撑一定诊断。它们记录 carried refs、supplemental context、stop reason、budget exhaustion、memory uptake ops、detour need，以及 settlement 后 state delta。 这对于 memory 与 read loop 非常有用。

但 planning audit 仍缺最小决策结构：Navigate 的候选、selected option、rejected alternatives、source evidence、memory used、uncertainty、budget reason、detour restore-mainline reason。当前 `NavigateActTraceEntry` 已有 decision、selection_mode、reason、skill request/result、budget state 等字段。 这说明 schema 起点存在，但还没有形成 planning audit policy。

### Improvement directions

**第一，planning audit 应记录 structured decision summary，而不是 full reasoning trace。** OpenAI trace grading 和 LangGraph tracing / interrupts 的启发是：生产 agent 需要 trace-level diagnosis，但不需要把全部内部推理暴露给用户。Reading Companion 应记录：decision type、candidate options summary、selected option、one-line reason、source evidence ids、memory ref ids、rejected alternatives count/reason class、uncertainty、budget state。不要记录 chain-of-thought。

**第二，audit 应区分 planner / navigator / retrieval / memory / executor 错。** WebArena 与 τ-bench 都说明 long-horizon failure 需要定位。Reading Companion 本地化后：如果 selected span 不合适，是 Navigate policy 错；如果 selected span 对但 source_ref resolution 失败，是 resolver / executor 错；如果 memory ref 不该出现，是 retrieval / memory projection 错；如果 detour 未恢复主线，是 detour policy / runner state 错；如果 recommendation 误导用户，是 user-facing guidance 错。

**第三，planning audit 应补 `candidate_options` 与 `rejected_alternatives` 的低成本版本。** 不需要列出所有 thought paths；只需记录当前主要可选项：continue_mainline、look_back、active_recall、open_detour、defer_detour、deep_dive、no_user_surface_needed。每项可以有 availability / reason_class / source_evidence。这样能支持 evaluation 判断 overplanning / thrashing。

**第四，audit 应记录 budget reason 与 restoration reason。** 当前 record_read 已经有 `stop_reason` 和 `budget_exhausted`，这很好。 Detour / active recall / skill loop 也应记录为什么停：resolved、low value、budget cap、weak scent、source unavailable、restore mainline。没有这些字段，detour quality 很难评估。

### Design implications

- Planning Audit 页面应定义最小 structured decision fields。
- 不暴露 full hidden reasoning。
- 必须能区分 navigator 错、retrieval 错、memory 错、executor 错、recommendation 错。
- Candidate/rejected alternatives 只需低成本 summary。
- Detour audit 需要 exit reason 与 restore-mainline reason。

------

## 3.7 Planning Evaluation

### Current state and gap

当前 evaluation 已经有 strong foundation：product-first、mechanism-agnostic，且 long-span active direction 明确为 Memory Quality、Spontaneous Callback、False Visible Integration。 但 planning-specific metrics 仍未成体系。现在能评估 memory state 与 visible callback，却还不能系统评估“路径选得好不好”。

### Improvement directions

**第一，定义 Reading Path Quality。** 它不等于读得快，也不等于 callback 多。应看：source-order continuity 是否保持；unit boundary 是否自然；是否在关键结构处停留；是否没有过早 detour；是否在难点处有合理 look-back / active recall；是否避免 thrashing。Information Foraging 的 value-cost 与 Exploratory Search 的 open-ended understanding 支持这种路径质量，但指标要本地化。

**第二，定义 Navigation Groundedness。** 每个 `Navigate.choose_next_unit` 决定应能回到 source preview、active detour need、memory refs 或 policy reason。若选择没有 source evidence，只是 thematic jump，应低分。WebArena 的 functional correctness / environment grounding 可类比支持，但 Reading Companion 的 environment 是 source text。

**第三，定义 Mainline Continuity。** 这是项目特有关键指标。Source-order discipline 不是外部论文直接给出的答案，而是 book reading 的 project-specific judgment。指标可以看 detour frequency、detour length、mainline restoration success、continuity capsule stability、unit_span_ledger 是否出现异常跳跃。

**第四，定义 Detour Precision 与 Recovery Quality。** Detour Precision 看 detour 是否解决了打开时的 target_hint；Recovery Quality 看 detour 后是否回到 mainline、是否记录 restore reason、是否避免重复 detour。Options Framework 的 termination condition、ReAct 的 observation-grounded correction、τ-bench 的 repeated reliability 都支持这些维度。

**第五，定义 Visible Route Disclosure Readiness。** McNee 与 ResQue 直接支持 recommendation 不能只看 accuracy。Reading Companion 的 usefulness 应包括：理解帮助、agency、trust、source-grounding、低打扰、是否减少 over-search。

**第六，定义 Overplanning / Thrashing Rate。** 过多 look-back、detour、active recall、skill request、recommendation 都可能是 planning 失败。ToT / LATS 的复杂度 boundary 支持只在 hard cases 使用 heavy deliberation，而不是主循环默认。

**第七，定义 Planning-Memory Alignment。** 如果 navigation decision 引用 memory，但 memory 没有 source_ref 或已 superseded，就是 alignment 失败。如果 memory state 中有重要 active concern，但 Navigate 从不使用，也可能是 retrieval / planning alignment 问题。LongMemEval 的 stage decomposition、HaluMem 的 operation-level failure localization 支持这个方向。

### Design implications

- Planning Evaluation 页面应与 Memory Quality 区分，但可共享 audit artifacts。
- 指标包括 Reading Path Quality、Navigation Groundedness、Mainline Continuity、Detour Precision、Recovery Quality、Visible Route Disclosure Readiness、Overplanning / Thrashing Rate、Planning-Memory Alignment。
- 不照搬 WebArena / τ-bench；只借 trace-aware、long-horizon、reliability 思路。
- Recommendation evaluation 不用 accuracy-only。
- 需要小窗口 repeated-run 验证稳定性。

------

## 3.8 Orchestration and Infrastructure Restraint

### Current state and gap

当前 deterministic Reading Runner 已经是 orchestrator。它维护 cursor、调用 Navigate、解析 anchor、调用 Read、执行 settlement、写 runtime artifacts、checkpoint/resume、slow-cycle。 项目也已经 repo-first、机制私有 artifact-root，`_mechanisms/<mechanism_key>/` 是机制-owned territory。

缺口不是 orchestration substrate，而是 policy / audit / evaluation。引入 graph runtime 或 multi-agent 只会把未定义的 policy 包进更复杂基础设施。

### Improvement directions

**第一，不需要独立 planner node。** 当前 architecture 的优势是：Navigate 做 local selection，Read 做 grounded reading，runner 做 deterministic settlement，slow-cycle 做 boundary consolidation。HTN / Options / MAXQ 支持这种分层；Plan-and-Solve 支持 boundary planning；但没有一个外部工作要求把所有阅读过程交给一个 global planner agent。

**第二，不需要 graph workflow rewrite。** LangGraph 的 durable execution、checkpoint、interrupt、trace 是优秀 infrastructure pattern；Reading Companion 可借 checkpoint、pause/resume、review gate、trace schema 思想。但当前 runner 已经实现了关键 orchestration，且产品不是通用 graph workflow 平台。只要 current runner 能表达 state / audit / retry / resume，就不应为框架而框架化。

**第三，不需要 multi-agent reading team。** AutoGen / CrewAI 可作为 boundary reference：多 agent 对复杂协作任务有价值，但 Reading Companion 的体验是一个 living co-reader mind。多 agent 会降低 voice coherence，增加 audit 与 recommendation responsibility 分配难度。

**第四，search-based deliberation 只能作为 optional hard-passage mode。** ToT、GoT、LATS、RAP 都支持在 difficult reasoning / planning 场景中进行 branching / MCTS / graph thought / world-model planning。但 Reading Companion 普通 next-unit selection 不具备清晰 terminal reward，也不能承受每步高成本 search。它们最多用于 later optional deep-dive：例如难段多解释比较、争议概念解析、thematic path 比较。

**第五，坚持 Simplicity and Universality。** 这是 project-specific judgment，但有外部 boundary support：成熟 agent frameworks 的价值不是引入所有复杂能力，而是把 state、trace、handoff、guardrails 分层。Reading Companion 当前应把复杂度花在 reading policy 与 evaluation 上，而不是基础设施迁移上。

### Design implications

- Deterministic runner 继续作为 orchestrator。
- 不新增 global planner agent、planning manager agent、multi-agent team。
- 借 LangGraph / Agents SDK 的 checkpoint、interrupt、trace 思想，不迁移整套 runtime。
- Search-based planning 只作为 later optional hard-mode。
- Infrastructure 设计服务 policy 与 audit，不反过来主导设计。

------

# 4. Cross-Module Priority Summary

## Blocking priorities

**明确 Planning Ontology 与 state 边界。**
归属模块：Planning Ontology and Boundaries。优先原因：如果 source text、memory state、planning state、audit trace、recommendation 不分开，后续所有 policy 都会混。主要外部依据：HTN、Options、Information Foraging、LangGraph / Agents SDK state-trace separation。复杂度：Medium。需要小窗口验证：是，验证同一 run 中 Navigate、Read、settlement、slow-cycle 的责任是否可审计区分。

**把 Navigation Policy 正式定义为 source-order default + bounded exceptions。**
归属模块：Navigation Policy。优先原因：否则 detour、look-back、deep-dive 会慢慢侵蚀主线。主要外部依据：Information Foraging、Exploratory Search、Options。复杂度：Medium。需要小窗口验证：是，观察 detour / recall 触发频率与 mainline recovery。

**把 detour / look-back / active recall 的触发与退出条件 policy 化。**
归属模块：Detour / Look-back / Active Recall。优先原因：机制已经存在，但如果 policy 不清，会产生 novelty chasing 与 over-search。主要外部依据：ReAct、ReWOO、Information Foraging、rereading effect、metacomprehension。复杂度：Medium。需要小窗口验证：是，尤其要验证 detour 是否真的被触发、退出、恢复主线。

**补 planning audit 最小字段。**
归属模块：Planning Audit / Observability。优先原因：没有 candidate / selected / rejected / evidence / memory-used / uncertainty / budget reason，就无法评估 planning。主要外部依据：OpenAI trace grading、LangGraph tracing、WebArena、τ-bench。复杂度：Low-to-Medium。需要小窗口验证：是。

## High-value next priorities

**定义 internal navigation vs visible route disclosure。**
归属模块：Visible Reading Route Surface Boundary。优先原因：否则 recommendation 会在“系统下一步读哪里”和“用户看到什么建议”之间混用。主要外部依据：Adaptive Navigation Support、Learner Agency、Open Learner Model、controllability / explainability recommender work。复杂度：Medium。需要小窗口验证：是，先验证少量 look-back / no_user_surface_needed / carry-forward focus。

**把 slow-cycle 定义为 macro carry-forward planning，而不是 memory-only cleanup。**
归属模块：Slow-cycle / Macro-planning。优先原因：当前 slow-cycle 已经承担 chapter-level carry-forward，但没有正式边界。主要外部依据：Reflexion、HTN、Options、Plan-and-Solve。复杂度：Medium。需要小窗口验证：是，观察 chapter-end active_attention carry-forward 是否合理。

**建立 planning-specific evaluation metrics。**
归属模块：Planning Evaluation。优先原因：Memory Quality 与 reaction audit 不足以评估路径选择。主要外部依据：ResQue、McNee、WebArena、τ-bench、AgentBench。复杂度：Medium。需要小窗口验证：是，先用固定 source windows 做 qualitative + structured audit。

**使用 value / cost / scent 作为 navigation reason vocabulary。**
归属模块：Navigation Policy / Detour Policy。优先原因：它能低成本连接 mainline、detour、look-back、deep-dive。主要外部依据：Information Foraging。复杂度：Low。需要小窗口验证：是。

## Later / optional priorities

**Hard-passage deep-dive mode。**
归属模块：Navigation / Detour / Evaluation。价值：可在难段比较两三种解释路径。主要外部依据：Tree of Thoughts、Graph of Thoughts、LATS。复杂度：High。需要小窗口验证：是，且只在 hard cases。

**Lightweight route-disclosure display preferences。**
归属模块：Visible Reading Route Surface Boundary。价值：支持 agency 与 controllability。主要外部依据：Open Learner Model、Tsai & Brusilovsky、Learner Agency review。复杂度：Medium。需要小窗口验证：是。

**Thematic path / learning path recommendation。**
归属模块：Recommendation / Slow-cycle。价值：未来可能有专题重读路线。主要外部依据：Course Sequencing、Learning Path Recommendation。复杂度：High。需要小窗口验证：是，但应后置。

## Reject / defer priorities

**Large planner node、multi-agent team、graph workflow rewrite、default ToT/LATS/MCTS、full planner-executor architecture、recommendation replacing source-order reading、exposing all planning reasoning、planning-memory merged store、complex learning path engine、full learner model、planning manager agent。**
归属模块：Orchestration / Recommendation / Ontology。优先原因：它们会提高复杂度，但当前 blockers 是 ontology、policy、audit、evaluation。主要外部依据：ToT / LATS complexity boundary、LangGraph / Agents SDK as infrastructure not judgment、Learner Agency / Course Sequencing boundary。复杂度：High。需要小窗口验证：只有在低复杂度方案被证明不足后再考虑。

------

# 5. What to Reject or Defer Now

**Large planner node now。**
诱惑是把 planning 具象成一个“高级智能节点”。但当前系统已经有 `Navigate -> Read -> settlement -> slow-cycle` 的分层，问题是职责边界和 policy 不够清楚。Plan-and-Solve 支持复杂问题前的 explicit plan，不支持每个阅读步都由 global planner 接管。只有当 Navigate 无法在 bounded policy 下稳定选择 next unit，且 evaluation 显示问题来自缺少 boundary-level planning，才值得考虑轻量 planner sketch。

**Multi-agent reading team now。**
多 agent 可以带来角色分工，但 Reading Companion 的产品核心是一个连贯的 co-reading mind。多 agent 会制造 voice fragmentation、audit 分配困难、recommendation 责任不清。AutoGen / CrewAI 适合作为 boundary reference，不适合作为当前架构方向。只有当产品明确转向 debate / seminar / multi-perspective mode，才值得重新评估。

**Graph workflow rewrite now。**
LangGraph 的 durable execution、interrupt、trace 很值得借鉴，但 Reading Runner 已经是 deterministic orchestrator。当前缺口是 policy 与 audit，不是 graph substrate。只有当现有 runner 无法表达 resume、interrupt、review gate、trace replay，才考虑 runtime migration。

**Tree of Thoughts as default reading loop。**
ToT 的 branch-and-backtrack 对 deliberate problem solving 有价值，但普通阅读没有稳定 reward，也不能承受每步高成本。它适合作为 hard-passage optional mode，不适合作为默认 reading loop。

**LATS / MCTS for every next-unit decision。**
LATS 将 reasoning、acting、planning 统一到 MCTS-like search，对复杂 agent task 有启发。但 Reading Companion 的 next-unit decision 多数是 source-order continuation，不是可模拟 reward search。只有在难段多解释比较、局部 deep-dive 中才可能考虑。

**Full planner-executor architecture now。**
ReWOO 和 Plan-and-Solve 支持某些 planner-executor decomposition，但 Reading Companion 的主循环更适合 situated navigation。提前冻结全程计划会破坏 responsive reading。当前只需要 boundary-level planning sketch，不需要 full planner-executor。

**Recommendation replacing source-order reading。**
Adaptive Navigation Support 支持路径提示，不支持系统接管阅读顺序。Course Sequencing 依赖学习目标与 prerequisite graph，Reading Companion 当前不是 tutoring platform。推荐应是 scaffold，不是主循环替代品。

**Exposing all planning reasoning to users。**
可解释性与可控性重要，但不等于暴露全部内部 reasoning。用户需要 source-grounded concise rationale；audit 才需要 internal decision summary。Open Learner Model 和 controllability work 支持可见状态与用户控制，但不是 full trace dump。

**Merging planning and memory into one state store。**
Planning state 是 pending decision / detour / recommendation obligation；memory state 是 source-grounded retained understanding；audit trace 是 diagnostic record。合并会导致 state pollution 和 evaluation ambiguity。Zep、LangGraph、Letta 的分层思想都支持边界。

**Complex learning path engine now。**
Learning path recommendation 需要 goal、prior knowledge、dependency graph。当前项目没有完整 learner model，也不应把书本阅读强行课程化。只有当产品明确支持用户目标、主题路径、学习路线时再考虑。

**Full learner model now。**
Open Learner Model 有价值，但 Reading Companion 当前不是 mastery diagnosis system。可先做 minimal user controllability，而不是完整 learner state。

**User-facing thematic path recommendation now。**
Thematic path 很吸引人，但容易把 source-order reading 变成 AI 选路。当前更适合 local look-back / carry-forward focus / no_user_surface_needed。只有当 internal navigation 和 recommendation audit 稳定后，才考虑 theme path。

**Slow cycle responsible for all macro-planning now。**
Slow-cycle 应处理 carry-forward、promotion、consolidation，不应接管 book scheduling、用户学习路线、全局 recommendation。否则它会变成隐藏 planner manager。

**Complex planning manager agent now。**
当前 deterministic runner + bounded LLM nodes 是正确方向。Planning manager agent 会增加不可预测性，并使 audit 更难。只有当 policy contract 已成熟且明确需要自治管理时才考虑。

------

# 6. Design Takeaways for Future Work

## Planning Ontology

- 要解决 Planning 在 Reading Companion 中到底是什么：它应被定义为 source-grounded reading path planning / attention scheduling，而不是 AutoGPT-style task planning。主要参考 HTN、Options、Information Foraging；避免 task-execution planner 语言。
- 要分清 source text、reading locus、memory state、planning state、audit trace、visible route disclosure。主要参考 LangGraph / Agents SDK 的 state / trace / orchestration 分层；避免把它们塞进一个 planning store。
- 要定义 micro / meso / macro planning。Micro 是 next-unit / recall / look-back；meso 是 detour / deep-dive；macro 是 slow-cycle carry-forward。主要参考 HTN、Options、MAXQ；避免把层级分工实现成复杂 runtime。
- 要区分 internal navigation 与 visible route disclosure。主要参考 Adaptive Navigation Support 和 Learner Agency；避免 recommendation 接管 source-order reading。

## Navigation Policy

- 要解决 `Navigate.choose_next_unit` 的身份：它是 source-grounded navigator / next-unit selector，不是 global planner。主要参考 ReAct、Information Foraging、Plan-and-Solve；避免新增 planner node。
- 要显式化 source-order discipline：默认继续主线，detour / look-back 是有理由的例外。主要参考 Information Foraging；避免 novelty chasing。
- 要引入 value / cost / information scent 的轻量理由语言。主要参考 Pirolli & Card；避免构造复杂 value model。
- 要定义 continuation、defer、detour、deep-dive、look-back、active recall 的归属。避免让 Navigate 成为万能节点。

## Detour / Look-back / Active Recall Policy

- 要解决三者边界：look-back 是 source calibration，active recall 是 memory recovery，detour 是 path deviation。主要参考 ReAct、rereading effect、metacomprehension、Information Foraging。
- 要定义 detour 的 open / resolve / abandon / restore-mainline。主要参考 Options Framework 的 termination condition；避免无退出 detour。
- 要定义触发条件：source-grounded unresolved concern、definition dependency、memory conflict、high-value scent。避免 theme-only detour。
- 要评估 detour 是否有实际阅读价值。主要参考 WebArena / τ-bench 的 recovery 与 reliability 思路；避免只统计 detour count。

## Visible Reading Route Surface Boundary

- 要解决推荐给用户的到底是什么：next segment、look-back point、deep-dive、carry-forward focus、thematic path、no_user_surface_needed。主要参考 Adaptive Navigation Support。
- 要把 recommendation 设计成 optional route-disclosure surface。主要参考 Learner Agency、Open Learner Model、controllability / explainability recommender work；避免替用户读书。
- 要控制 rationale 暴露：给 source-grounded concise reason，不暴露 full planning trace。避免把 audit trace 展示给用户。
- 当前不做 full learner model、learning path engine、thematic path recommender。主要参考 Course Sequencing 作为 boundary。

## Slow-cycle / Macro-planning

- 要解决 slow-cycle 是否是 macro-planning：它应是 chapter/session-level carry-forward planning + consolidation。主要参考 Reflexion、HTN、Options。
- 要区分 memory consolidation 与 macro planning：前者保留状态，后者选择下一阶段带什么 focus。避免 slow-cycle 变成万能 planner。
- 要限制 slow-cycle 权限：不自改 prompt、不学习策略、不重排全书路线。主要参考 Reflexion 的反思边界；避免 procedural memory 过早进入。

## Planning Audit / Observability

- 要解决 planning trace 不可诊断问题：记录 candidate options、selected option、rejected reason class、source evidence、memory used、uncertainty、budget reason、restore-mainline reason。
- 主要参考 LangGraph tracing、OpenAI trace grading、WebArena、τ-bench。
- 要避免 full reasoning dump；只记录 structured decision summary。
- 要能区分 navigator 错、retrieval 错、memory 错、executor 错、recommendation 错。

## Planning Evaluation

- 要定义 Reading Path Quality、Navigation Groundedness、Mainline Continuity、Detour Precision、Recovery Quality、Visible Route Disclosure Readiness、Overplanning / Thrashing Rate、Planning-Memory Alignment。
- 主要参考 McNee、ResQue、WebArena、τ-bench、AgentBench、Adaptive Navigation evaluation。
- 要从 agent evaluation 与 recommender evaluation 借鉴 trace-aware、beyond-accuracy、reliability、usefulness，而不是照搬 web task benchmark。
- 避免只看 final answer、callback count 或 click-through。

## Orchestration / Infrastructure

- 要坚持 deterministic runner 作为 orchestrator。主要参考 HTN / Options / MAXQ 的分层思想，以及 LangGraph / Agents SDK 的基础设施分层。
- 要借 checkpoint、interrupt、trace、guardrail 思想，不做 graph workflow rewrite。
- 要拒绝 multi-agent reading team、large planner manager、default ToT / LATS / MCTS。
- 要把复杂度花在 policy、audit、evaluation 上，而不是基础设施重构上。

------

# 7. Source Usage Appendix

| External source                                              | Authors / Organization                              | Year             | Stable URL                                                   | Used in sections                | Role                                    |
| ------------------------------------------------------------ | --------------------------------------------------- | ---------------- | ------------------------------------------------------------ | ------------------------------- | --------------------------------------- |
| ReAct: Synergizing Reasoning and Acting in Language Models   | Shunyu Yao et al.                                   | 2022 / ICLR 2023 | https://arxiv.org/abs/2210.03629                             | 2.1, 2.2, 3.2, 3.3, 5, 6        | Direct support / Boundary support       |
| Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models | Lei Wang et al.                                     | 2023             | https://aclanthology.org/2023.acl-long.147/                  | 2.1, 2.3, 3.1, 3.2, 3.5, 5      | Direct support / Boundary support       |
| ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models | Binfeng Xu et al.                                   | 2023             | https://arxiv.org/abs/2305.18323                             | 2.1, 3.3, 5                     | Analogical support                      |
| Reflexion: Language Agents with Verbal Reinforcement Learning | Noah Shinn et al.                                   | 2023             | https://arxiv.org/abs/2303.11366                             | 3.5, 5, 6                       | Direct support / Boundary support       |
| Tree of Thoughts: Deliberate Problem Solving with Large Language Models | Shunyu Yao et al.                                   | 2023             | https://arxiv.org/abs/2305.10601                             | 2.3, 3.7, 3.8, 5                | Boundary / negative support             |
| Graph of Thoughts: Solving Elaborate Problems with Large Language Models | Maciej Besta et al.                                 | 2023             | https://arxiv.org/abs/2308.09687                             | 3.8, 4, 5                       | Boundary / analogical support           |
| Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models | Andy Zhou et al.                                    | 2023             | https://arxiv.org/abs/2310.04406                             | 2.3, 3.7, 3.8, 5                | Boundary / negative support             |
| Reasoning with Language Model is Planning with World Model   | Shibo Hao et al.                                    | 2023             | https://arxiv.org/abs/2305.14992                             | 3.8, 5                          | Boundary / negative support             |
| Hierarchical Task Network Planning: Formalization, Analysis, and Implementation | Kutluhan Erol                                       | 1996             | http://hdl.handle.net/1903/5810                              | 3.1, 3.2, 3.5, 3.8, 6           | Direct support                          |
| Between MDPs and semi-MDPs: A Framework for Temporal Abstraction in Reinforcement Learning | Richard S. Sutton, Doina Precup, Satinder Singh     | 1999             | https://doi.org/10.1016/S0004-3702(99)00052-1                | 3.1, 3.2, 3.3, 3.5, 6           | Direct support                          |
| Hierarchical Reinforcement Learning with the MAXQ Value Function Decomposition | Thomas G. Dietterich                                | 2000             | https://doi.org/10.1613/jair.639                             | 2.1, 3.1, 3.8                   | Analogical support                      |
| LangGraph documentation: durable execution, interrupts, tracing / memory concepts | LangChain / LangGraph                               | 2024–2025        | https://docs.langchain.com/oss/python/langgraph/overview     | 2.3, 3.1, 3.6, 3.8, 6           | Direct support / Infrastructure support |
| OpenAI Agents SDK / tracing and trace grading documentation  | OpenAI                                              | 2025             | https://developers.openai.com/                               | 3.1, 3.6, 3.7, 6                | Background / infrastructure support     |
| Information Foraging                                         | Peter Pirolli, Stuart K. Card                       | 1999             | https://doi.org/10.1037/0033-295X.106.4.643                  | 2.1, 2.2, 3.1, 3.2, 3.3, 3.7, 6 | Direct support                          |
| Exploratory Search: From Finding to Understanding            | Gary Marchionini                                    | 2006             | https://cacm.acm.org/research/exploratory-search/            | 2.2, 3.3, 3.7                   | Analogical support                      |
| Exploratory Search: Beyond the Query-Response Paradigm       | Ryen W. White, Resa A. Roth                         | 2009             | https://doi.org/10.2200/S00174ED1V01Y200901ICR003            | 3.3, 3.7                        | Background / analogical support         |
| Adaptive Hypermedia                                          | Peter Brusilovsky                                   | 2001             | https://doi.org/10.1023/A:1011143116306                      | 3.4, 6                          | Direct support                          |
| Adaptive Navigation Support in Educational Hypermedia        | Peter Brusilovsky                                   | 2003             | https://doi.org/10.1111/1467-8535.00345                      | 2.2, 3.4, 6                     | Direct support                          |
| Course Sequencing Techniques for Large-Scale Web-Based Education | Peter Brusilovsky, Julita Vassileva                 | 2003             | https://doi.org/10.1504/IJCEELL.2003.002154                  | 3.4, 5, 6                       | Boundary / analogical support           |
| The rereading effect: Metacomprehension accuracy improves across reading trials | Katherine A. Rawson, John Dunlosky, Keith W. Thiede | 2000             | https://doi.org/10.3758/BF03209348                           | 3.3, 6                          | Direct support                          |
| Metacomprehension: A Brief History and How to Improve Its Accuracy | John Dunlosky, Amanda R. Lipko                      | 2007             | https://doi.org/10.1111/j.1467-8721.2007.00509.x             | 3.3, 6                          | Direct support                          |
| Recommender systems to support learners’ Agency in a Learning Context: a systematic review | Michelle Deschênes                                  | 2020             | https://doi.org/10.1186/s41239-020-00219-w                   | 3.4, 5, 6                       | Direct support                          |
| Enhancing learning outcomes through self-regulated learning support with an Open Learner Model | Yanjin Long, Vincent Aleven                         | 2017             | https://doi.org/10.1007/s11257-016-9186-6                    | 3.4, 5, 6                       | Analogical support                      |
| The effects of controllability and explainability in a social recommender system | Chun-Hua Tsai, Peter Brusilovsky                    | 2021             | https://doi.org/10.1007/s11257-020-09281-5                   | 3.4, 5, 6                       | Direct support                          |
| Being accurate is not enough: How accuracy metrics have hurt recommender systems | Sean M. McNee, John Riedl, Joseph A. Konstan        | 2006             | https://doi.org/10.1145/1125451.1125659                      | 3.4, 3.7, 6                     | Direct support                          |
| A user-centric evaluation framework for recommender systems / ResQue | Pearl Pu, Li Chen                                   | 2011             | https://doi.org/10.1145/2043932.2043962                      | 3.4, 3.7, 6                     | Direct support                          |
| AgentBench: Evaluating LLMs as Agents                        | Xiao Liu et al.                                     | 2023             | https://arxiv.org/abs/2308.03688                             | 3.7, 6                          | Background support                      |
| WebArena: A Realistic Web Environment for Building Autonomous Agents | Shuyan Zhou et al.                                  | 2023 / ICLR 2024 | https://arxiv.org/abs/2307.13854                             | 3.6, 3.7, 6                     | Analogical support                      |
| τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains | Shunyu Yao et al.                                   | 2024             | https://arxiv.org/abs/2406.12045                             | 3.6, 3.7, 6                     | Analogical support                      |
| Generative Agents: Interactive Simulacra of Human Behavior   | Joon Sung Park et al.                               | 2023             | https://research.google/pubs/generative-agents-interactive-simulacra-of-human-behavior/ | 3.5, 3.6                        | Analogical support                      |
| Mem0 memory operations documentation                         | Mem0                                                | 2025             | https://docs.mem0.ai/core-concepts/memory-operations/add     | 3.1, 3.6                        | Analogical support                      |
| Zep graph / facts / observations documentation               | Zep                                                 | 2025             | https://help.getzep.com/graph-overview                       | 3.1, 3.6                        | Analogical support                      |
| GraphRAG documentation and paper                             | Microsoft Research / Darren Edge et al.             | 2024             | https://microsoft.github.io/graphrag/                        | 3.7, 3.8                        | Boundary / analogical support           |

## Final Interpretation Note

Any remaining historical “recommendation” language in this assessment should be read as a visible route disclosure boundary concern, not as user route choice, recommender-system behavior, accept/reject route state, or route steering. The current authoritative framing is: Second Reader chooses its own route; future user-visible surfaces may disclose or explain `reading_route_trace`, but they must not control navigation.
