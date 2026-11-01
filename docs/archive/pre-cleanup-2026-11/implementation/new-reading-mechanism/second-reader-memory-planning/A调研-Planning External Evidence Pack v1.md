# Planning External Evidence Pack v1

## Research Scope & Source Quality

本轮研究只做**外部证据包**，不做项目内部设计，不写 Planning Ontology，不写 Candidate Decision Ledger，也不把外部机制直接映射成 `Navigate` 改造方案。研究起点先做了对 `Captain4Whale/second-reader` 仓库的**浅层文档确认**，用于核对项目确实是 Reading Companion / `attentional_v2` 语境；随后把主要精力放在一手论文、出版社页面、ACL Anthology、arXiv、以及官方框架文档上。本轮**没有深入 GitHub 项目代码**，因为这轮目标是沉淀长期可复用的外部证据，而不是做 repo 内部诊断。

**Usage Note for Second Reader route disclosure.** Adaptive Navigation / Learner Agency / Recommendation literature should be used only as boundary evidence for future user-visible route disclosure. It does not imply Second Reader should ask users to choose its route, and it does not authorize a recommender system, learner model, or learning-path engine.

本轮我实际完成的阅读强度分为四档。**deep-read**：Plan-and-Solve、Reflexion、Tree of Thoughts、Language Agent Tree Search、Graph of Thoughts、LangGraph 官方文档、OpenAI Agents SDK / trace grading 官方文档。**partial-read**：ReAct、ReWOO、RAP、HTN/Options/MAXQ、Information Foraging、Adaptive Hypermedia、Adaptive Navigation Support、Course Sequencing、The rereading effect、Metacomprehension、Open Learner Model、Learner Agency systematic review、Explainability/Controllability in recommenders、ResQue、accuracy-not-enough、AgentBench、WebArena、τ-bench。**skimmed**：Manouselis 等关于 TEL recommender 的综述、White & Roth 的 Exploratory Search book、Balog 等关于 scrutable user models。**secondary only**：上传的知乎 PDF 仅作为背景存在，本轮没有把它作为高置信主证据。

### Source confidence summary

| Source cluster | What I actually used | Confidence | Notes |
| --- | --- | --- | --- |
| 一手论文全文或长摘要页面 | ReAct / PS / Reflexion / ToT / LATS / GoT / RAP / HTN / Options / MAXQ | 高 | 大多来自 arXiv、ACL Anthology、DOI 页面；少数仅拿到摘要与元数据 |
| 官方框架 / 官方平台文档 | LangGraph、OpenAI Agents SDK | 高 | 对 orchestration、checkpoint、interrupt、trace grading 特别有用 |
| HCI / 教育 / 阅读研究论文与综述 | Information Foraging、Adaptive Hypermedia、Metacomprehension、Rereading、Learner Agency、OLM、Recommender UX | 中高 | 多数为出版社摘要页或正规收录页，足够支撑机制级推断 |
| agent benchmark 论文 / 官方 benchmark 站点 | AgentBench、WebArena、τ-bench | 中高 | 用于评价维度与失败模式，不直接迁移为阅读主循环 |
| 二手综述 | LLM agent survey、上传的知乎 PDF | 中低 | 仅做定位或补充背景，不作为核心设计证据 |

### Canonical Bibliography

| Work ID | Tier | Canonical Title | Authors / Organization | Year / First Posted | Venue / Source | Source Type | Stable URL | DOI / arXiv ID / Official Doc URL | Read Status | Maturity | Why included | Relevance to Reading Companion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-WORK-001 | Tier 1 | ReAct: Synergizing Reasoning and Acting in Language Models | Shunyu Yao et al. | 2022 | arXiv / ICLR 2023 | paper | <https://arxiv.org/abs/2210.03629> | arXiv:2210.03629 | partial-read | Established paper | reasoning+action 交错的代表作 | detour/tool/source loop 的核心参照 |
| P-WORK-002 | Tier 1 | Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models | Lei Wang et al. | 2023 | ACL 2023 | paper | <https://aclanthology.org/2023.acl-long.147/> | DOI: [10.18653/v1/2023.acl-long.147](https://doi.org/10.18653/v1/2023.acl-long.147) | deep-read | Established paper | explicit plan-before-execution | 章级或难段边界式 planning 参考 |
| P-WORK-003 | Tier 1 | ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models | Binfeng Xu et al. | 2023 | arXiv | paper | <https://arxiv.org/abs/2305.18323> | arXiv:2305.18323 | partial-read | Recent arXiv | 规划与观察解耦 | detour/lookup 子回路降成本参照 |
| P-WORK-004 | Tier 1 | Reflexion: Language Agents with Verbal Reinforcement Learning | Noah Shinn et al. | 2023 | arXiv | paper | <https://arxiv.org/abs/2303.11366> | arXiv:2303.11366 | deep-read | Recent arXiv | reflection memory 的代表作 | slow cycle / failed navigation learning |
| P-WORK-005 | Tier 1 | Tree of Thoughts: Deliberate Problem Solving with Large Language Models | Shunyu Yao et al. | 2023 | arXiv | paper | <https://arxiv.org/abs/2305.10601> | arXiv:2305.10601 | deep-read | Recent arXiv | search-based deliberation 代表作 | hard passage deep-dive 的边界参考 |
| P-WORK-006 | Tier 2 | Graph of Thoughts: Solving Elaborate Problems with Large Language Models | Maciej Besta et al. | 2023 | arXiv / AAAI 2024 | paper | <https://arxiv.org/abs/2308.09687> | arXiv:2308.09687 | deep-read | Recent arXiv | arbitrary graph reasoning | 多主题路径比较的类比证据 |
| P-WORK-007 | Tier 1 | Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models | Andy Zhou et al. | 2023 | arXiv | paper | <https://arxiv.org/abs/2310.04406> | arXiv:2310.04406 | deep-read | Recent arXiv | MCTS-like agent planning 代表作 | deep-dive 时的 optional search 参考 |
| P-WORK-008 | Tier 2 | Reasoning with Language Model is Planning with World Model | Shibo Hao et al. | 2023 | arXiv / EMNLP 2023 | paper | <https://arxiv.org/abs/2305.14992> | arXiv:2305.14992 | partial-read | Established paper | world-model + MCTS | 说明何时不该把阅读问题过度规划化 |
| P-WORK-009 | Tier 1 | Hierarchical Task Network Planning: Formalization, Analysis, and Implementation | Kutluhan Erol | 1996 | University of Maryland thesis | thesis | <http://hdl.handle.net/1903/5810> | Official handle URL | partial-read | Classic theory | 经典 hierarchical decomposition | micro / meso / macro 分层参照 |
| P-WORK-010 | Tier 1 | Between MDPs and semi-MDPs: A Framework for Temporal Abstraction in Reinforcement Learning | Richard S. Sutton, Doina Precup, Satinder Singh | 1999 | Artificial Intelligence | paper | <https://doi.org/10.1016/S0004-3702(99)00052-1> | DOI: [10.1016/S0004-3702(99)00052-1](https://doi.org/10.1016/S0004-3702(99)00052-1) | partial-read | Classic theory | options / temporal abstraction | detour / slow cycle / chapter loop 抽象单位参考 |
| P-WORK-011 | Tier 2 | Hierarchical Reinforcement Learning with the MAXQ Value Function Decomposition | Thomas G. Dietterich | 2000 | JAIR | paper | <https://doi.org/10.1613/jair.639> | DOI: [10.1613/jair.639](https://doi.org/10.1613/jair.639) | partial-read | Classic theory | controller-worker decomposition | LLM 与 deterministic runner 分工参照 |
| P-WORK-012 | Tier 1 | LangGraph overview / durable execution / interrupts | LangGraph docs team | 2024–2026 | official docs | official framework docs | <https://docs.langchain.com/oss/javascript/langgraph/overview> | Official docs URL | deep-read | Official framework docs | orchestration / persistence / review gates | audit trace / resumability / runner settlement |
| P-WORK-013 | Tier 1 | OpenAI Agents SDK / trace grading docs | [OpenAI](https://openai.com) platform docs | 2025–2026 | official docs | official framework docs | <https://developers.openai.com/api/docs/guides/agents> | Official docs URL | deep-read | Official framework docs | handoff / guardrail / trace grading | planning audit 与失败归因参照 |
| P-WORK-014 | Tier 1 | Information Foraging | Peter Pirolli, Stuart K. Card | 1999 | Psychological Review | paper | <https://doi.org/10.1037/0033-295X.106.4.643> | DOI: [10.1037/0033-295X.106.4.643](https://doi.org/10.1037/0033-295X.106.4.643) | partial-read | Classic theory | value/cost/scent 的经典来源 | “下一步读哪里”比 task plan 更像信息觅食 |
| P-WORK-015 | Tier 2 | Exploratory Search: From Finding to Understanding | Gary Marchionini | 2006 | Communications of the ACM | paper | <https://cacm.acm.org/research/exploratory-search/> | Official article URL | partial-read | Established paper | lookup vs exploratory search 区分 | Reading Companion 更接近探索式支持 |
| P-WORK-016 | Tier 2 | Exploratory Search: Beyond the Query-Response Paradigm | Ryen W. White, Resa A. Roth | 2009 | Synthesis Lectures | book | <https://doi.org/10.2200/S00174ED1V01Y200901ICR003> | DOI: [10.2200/S00174ED1V01Y200901ICR003](https://doi.org/10.2200/S00174ED1V01Y200901ICR003) | skimmed | Established paper | open-ended search 的系统化框架 | detour / thematic path 的上位背景 |
| P-WORK-017 | Tier 1 | Adaptive Hypermedia | Peter Brusilovsky | 2001 | User Modeling and User-Adapted Interaction | paper | <https://doi.org/10.1023/A:1011143116306> | DOI: [10.1023/A:1011143116306](https://doi.org/10.1023/A:1011143116306) | partial-read | Classic theory | user model based adaptation 经典综述 | recommendation 与 navigation 分层参照 |
| P-WORK-018 | Tier 1 | Adaptive Navigation Support in Educational Hypermedia | Peter Brusilovsky | 2003 | British Journal of Educational Technology | paper | <https://doi.org/10.1111/1467-8535.00345> | DOI: [10.1111/1467-8535.00345](https://doi.org/10.1111/1467-8535.00345) | partial-read | Established paper | direct guidance / annotation / meta-adaptation | 什么时候提示、提示多强 的核心证据 |
| P-WORK-019 | Tier 1 | Course Sequencing Techniques for Large-Scale Web-Based Education | Peter Brusilovsky, Julita Vassileva | 2003 | IJCEELL | paper | <https://doi.org/10.1504/IJCEELL.2003.002154> | DOI: [10.1504/IJCEELL.2003.002154](https://doi.org/10.1504/IJCEELL.2003.002154) | partial-read | Established paper | prerequisite / goal / prior knowledge sequencing | chapter carry-forward 与 thematic path 参考 |
| P-WORK-020 | Tier 1 | The rereading effect: Metacomprehension accuracy improves across reading trials | Katherine A. Rawson, John Dunlosky, Keith W. Thiede | 2000 | Memory & Cognition | paper | <https://doi.org/10.3758/BF03209348> | DOI: [10.3758/BF03209348](https://doi.org/10.3758/BF03209348) | partial-read | Established paper | rereading 是否有益的直接证据 | look-back policy 的关键来源 |
| P-WORK-021 | Tier 1 | Metacomprehension: A Brief History and How to Improve Its Accuracy | John Dunlosky, Amanda R. Lipko | 2007 | Current Directions in Psychological Science | paper | <https://doi.org/10.1111/j.1467-8721.2007.00509.x> | DOI: [10.1111/j.1467-8721.2007.00509.x](https://doi.org/10.1111/j.1467-8721.2007.00509.x) | partial-read | Established paper | 读者自我判断往往不准 | agent 不应盲信表层“我懂了” |
| P-WORK-022 | Tier 1 | Recommender systems to support learners’ Agency in a Learning Context: a systematic review | Michelle Deschênes | 2020 | International Journal of Educational Technology in Higher Education | review | <https://doi.org/10.1186/s41239-020-00219-w> | DOI: [10.1186/s41239-020-00219-w](https://doi.org/10.1186/s41239-020-00219-w) | partial-read | Established paper | learner agency 的系统性证据 | user-visible route disclosure 要低打扰且不劫持目标 |
| P-WORK-023 | Tier 1 | Enhancing learning outcomes through self-regulated learning support with an Open Learner Model | Yanjin Long, Vincent Aleven | 2017 | User Modeling and User-Adapted Interaction | paper | <https://doi.org/10.1007/s11257-016-9186-6> | DOI: [10.1007/s11257-016-9186-6](https://doi.org/10.1007/s11257-016-9186-6) | partial-read | Established paper | open learner model + self-regulated learning | recommendation rationale / user control 的实证支撑 |
| P-WORK-024 | Tier 1 | The effects of controllability and explainability in a social recommender system | Chun-Hua Tsai, Peter Brusilovsky | 2021 | User Modeling and User-Adapted Interaction | paper | <https://doi.org/10.1007/s11257-020-09281-5> | DOI: [10.1007/s11257-020-09281-5](https://doi.org/10.1007/s11257-020-09281-5) | partial-read | Established paper | controllability + explainability 交互 | recommendation UI 的强相关证据 |
| P-WORK-025 | Tier 1 | Being accurate is not enough: How accuracy metrics have hurt recommender systems | Sean M. McNee, John Riedl, Joseph A. Konstan | 2006 | CHI EA 2006 | paper | <https://doi.org/10.1145/1125451.1125659> | DOI: [10.1145/1125451.1125659](https://doi.org/10.1145/1125451.1125659) | partial-read | Established paper | accuracy-only evaluation 的批判 | recommendation usefulness > hit-rate |
| P-WORK-026 | Tier 1 | A user-centric evaluation framework for recommender systems | Pearl Pu, Li Chen | 2011 | RecSys 2011 | paper | <https://doi.org/10.1145/2043932.2043962> | DOI: [10.1145/2043932.2043962](https://doi.org/10.1145/2043932.2043962) | partial-read | Established paper | ResQue user-centric evaluation | recommendation usefulness / trust / return intent |
| P-WORK-027 | Tier 2 | AgentBench: Evaluating LLMs as Agents | Xiao Liu et al. | 2023 | arXiv | paper | <https://arxiv.org/abs/2308.03688> | arXiv:2308.03688 | partial-read | Recent arXiv | agent benchmark background | planner/evaluator 分离的重要性 |
| P-WORK-028 | Tier 2 | WebArena: A Realistic Web Environment for Building Autonomous Agents | Shuyan Zhou et al. | 2023 | arXiv / ICLR 2024 | paper | <https://arxiv.org/abs/2307.13854> | arXiv:2307.13854 | partial-read | Established paper | long-horizon agent evaluation | functional correctness / recovery / grounding 指标借鉴 |
| P-WORK-029 | Tier 2 | τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains | Shunyu Yao et al. | 2024 | arXiv / ICLR 2025 | paper | <https://arxiv.org/abs/2406.12045> | arXiv:2406.12045 | partial-read | Recent arXiv | reliability over multiple trials | recommendation consistency / over-guidance 评估参考 |
| P-WORK-030 | Tier 2 | Recommender Systems in Technology Enhanced Learning | Nikos Manouselis et al. | 2011 | Recommender Systems Handbook | chapter | <https://doi.org/10.1007/978-0-387-85820-3_12> | DOI: [10.1007/978-0-387-85820-3_12](https://doi.org/10.1007/978-0-387-85820-3_12) | skimmed | Secondary / background only | TEL recommender 背景综述 | 区分 learning path 与普通 top-N |
| P-WORK-031 | Tier 2 | Explaining the user experience of recommender systems | Bart P. Knijnenburg et al. | 2012 | User Modeling and User-Adapted Interaction | paper | <https://doi.org/10.1007/s11257-011-9118-4> | DOI: [10.1007/s11257-011-9118-4](https://doi.org/10.1007/s11257-011-9118-4) | skimmed | Established paper | UX layers for recommender eval | recommendation rationale 的用户感受维度 |
| P-WORK-032 | Tier 2 | Transparent, Scrutable and Explainable User Models for Personalized Recommendation | Krisztian Balog, Filip Radlinski, Shushan Arakelyan | 2019 | SIGIR 2019 | paper | <https://doi.org/10.1145/3331184.3331211> | DOI: [10.1145/3331184.3331211](https://doi.org/10.1145/3331184.3331211) | skimmed | Established paper | scrutable user model | recommendation 可解释且可修正的证据 |

## External Planning Field Map

| Area | Core question | Representative works | Why it matters | Risk if copied blindly |
| --- | --- | --- | --- | --- |
| Agent Planning | agent 是否应先想完整计划 | P-WORK-002, 007, 008 | 帮助区分先规划与边做边调 | 把阅读强行问题化、任务化 |
| Action Selection | 下一步动作如何选 | P-WORK-001, 003, 007 | 阅读里等价于下一步读哪段/看哪源 | 把“读哪里”误当“调用哪个工具” |
| Reasoning + Acting | reasoning 与 action 如何交错 | P-WORK-001 | detour / source lookup 的近邻机制 | 让每个阅读步都显式推理过重 |
| Planner-Executor | planner 与 executor 是否分离 | P-WORK-002, 003 | 说明边界式规划何时值得 | 引入独立 planner node 过重 |
| Workflow Orchestration | 状态、重试、恢复、审计如何做 | P-WORK-012, 013 | 对 runner settlement / audit trace 很关键 | 为工程框架而框架化 |
| Router / Meta-controller | 谁决定交给谁做 | P-WORK-011, 013 | 对 LLM vs deterministic runner 分工重要 | 容易滑向多 agent 复杂化 |
| Hierarchical Planning | 宏观/中观/微观如何分层 | P-WORK-009, 010, 011 | 最贴近 read unit / detour / chapter cycle 分层 | 误把抽象层级当 runtime 复杂架构 |
| Search-based Deliberation | 是否要多路径搜索/回溯 | P-WORK-005, 006, 007, 008 | 只在 hard passage / thematic comparison 时可能需要 | 默认主循环采用搜索会过慢、难解释 |
| Reflection-based Planning | 失败经验如何影响后续 | P-WORK-004 | 适合 slow cycle / 策略修正 | 反思污染内容理解与 memory state |
| Information Foraging | 下一处信息源值不值得去 | P-WORK-014, 015, 016 | 最贴近“下一步读哪里” | novelty chasing 破坏主线 |
| Exploratory Search | 开放式探索怎样被支持 | P-WORK-015, 016 | Reading Companion 更像探索支架而非任务执行器 | 过度搜索导致失焦 |
| Active Reading | 系统如何支架而非代读 | P-WORK-020, 021 | look-back / self-monitoring 的证据背景 | 把读者主动性让给 agent |
| Rereading / Metacomprehension | 何时回看有益 | P-WORK-020, 021 | 直接支撑 look-back 不应无脑触发 | “为了回看而回看” 造成成本浪费 |
| Adaptive Navigation | 系统如何提示路径 | P-WORK-017, 018 | 与 user-visible route disclosure 高相关 | 过强 guidance 削弱 agency |
| Learner Agency | 用户目标与控制权怎样保留 | P-WORK-022, 023, 024 | 避免替用户做决定 | recommendation 变成 soft coercion |
| Pedagogical Sequencing | 依赖、难度、目标如何排序 | P-WORK-019, 030 | 对 thematic path / carry-forward 有用 | Reading Companion 不是 tutor，不能直接照搬 mastery model |
| Learning Path Recommendation | 路径不是 item ranking 而是 sequence design | P-WORK-019, 022, 030 | 说明“阅读路径推荐”不同于 top-N | 把路径简化成相关段落列表 |
| Recommendation-as-Planning | 推荐本身是否是轻量 planning | P-WORK-024, 032 | 说明 internal plan 与 user-visible rationale 要分层 | 直接暴露内部 plan 会僵硬 |
| Planning Evaluation | planner 错还是 executor 错 | P-WORK-013, 027, 028, 029 | 对 planning-memory-audit alignment 很关键 | 只看 end-task success，分不清错因 |
| Recommendation Evaluation | usefulness / trust / agency 如何评估 | P-WORK-025, 026, 031 | 适合 Reading Path Quality 与 over-guidance 指标 | 只看 accuracy / click rate |

## Tier 1 Work Cards

### Work Card: ReAct

- Work ID: P-WORK-001
- Source link: <https://arxiv.org/abs/2210.03629>
- Authors / Organization: Shunyu Yao et al.
- Year / First Posted: 2022
- Venue / Source: arXiv / ICLR 2023
- Source Type: paper
- Read status: partial-read
- Maturity: Established paper
- Original problem: 在 reasoning 与 acting 被分开研究的背景下，把二者交错，形成可纠错的 agent loop。
- Target agent / system / user setting: QA、fact verification、interactive decision-making agent。
- Planning / navigation / recommendation ontology: `Thought -> Action -> Observation -> Thought`。
- Control loop: 交替式 reasoning/action loop。
- Action selection or recommendation mechanism: 当前 reasoning trace 决定下一 action；observation 再修正后续 reasoning。
- Planner-executor interface: 基本未显式分层；同一主体同时推理和行动。
- Memory / state interface: 短程上下文内轨迹。
- Tool / environment interface: Wikipedia API / ALFWorld / WebShop 等外部环境。
- Evaluation method: QA accuracy、interactive success rate、trajectory interpretability。
- Key mechanisms: interleaved reasoning-action；observation-grounded correction；trajectory interpretability。
- What it directly supports: detour / source-skill loop；source-grounded action trace。
- What it only analogically supports: 阅读导航中的局部回看与插曲式补证。
- What it argues against: 用纯内部思维替代与源文本交互。
- Fit to Reading Companion: 适合**局部 detour**，尤其是“读到难点 -> 去查一处外部证据 -> 回主线”。
- Misfit / limitation: 不适合作为全局阅读 planner；阅读主循环不是连续的 tool-use task。
- Complexity implication: 低到中；但若每步都显式 ReAct，会抬高延迟与 token 成本。
- Candidate project-relevant implications: 可以借鉴“bounded interaction loop”，但不应把整本书阅读改写成 action sandbox。
- Evidence strength: 高

### Work Card: Planner-Executor decomposition

- Work ID: P-WORK-002
- Source link: <https://aclanthology.org/2023.acl-long.147/>
- Authors / Organization: Lei Wang et al.
- Year / First Posted: 2023
- Venue / Source: ACL 2023
- Source Type: paper
- Read status: deep-read
- Maturity: Established paper
- Original problem: Zero-shot-CoT 常漏步骤、算错、误解语义。
- Target agent / system / user setting: 多步 reasoning task。
- Planning / navigation / recommendation ontology: `Plan first -> solve subtasks`。
- Control loop: 两阶段，先切分任务，再执行子步骤。
- Action selection or recommendation mechanism: 显式计划先于推理执行。
- Planner-executor interface: 计划输出子任务序列，执行阶段按序展开。
- Memory / state interface: 基于 prompt 内显式计划。
- Tool / environment interface: 原论文偏 reasoning，不强依赖外部工具。
- Evaluation method: 10 个数据集、三类 reasoning problem。
- Key mechanisms: 先计划、再执行；PS+ 强化步骤质量与计算正确性。
- What it directly supports: chapter-level / hard-passage boundary planning。
- What it only analogically supports: 阅读路径推荐的“先给高层选项，再展开”。
- What it argues against: 完全无计划地进入复杂难段。
- Fit to Reading Companion: 适合**边界处**生成轻量 plan sketch，而非每个 unit 都规划。
- Misfit / limitation: 阅读是 source-order process；提前展开过细计划会脆弱。
- Complexity implication: 中；独立 planner 节点若全程运行会过重。
- Candidate project-relevant implications: 适合“章节起点”和“卡住时”而非主循环。
- Evidence strength: 高

### Work Card: ReWOO

- Work ID: P-WORK-003
- Source link: <https://arxiv.org/abs/2305.18323>
- Authors / Organization: Binfeng Xu et al.
- Year / First Posted: 2023
- Venue / Source: arXiv
- Source Type: paper
- Read status: partial-read
- Maturity: Recent arXiv
- Original problem: interleaved observation 导致提示冗余与高成本。
- Target agent / system / user setting: augmented language models with external tools。
- Planning / navigation / recommendation ontology: `reason without observation -> execute -> fill observations`。
- Control loop: reason / plan 与 observation 获取解耦。
- Action selection or recommendation mechanism: 先产生结构化执行草图，再逐条执行。
- Planner-executor interface: 很强；planner 输出变量绑定式计划。
- Memory / state interface: 计划中显式存变量引用。
- Tool / environment interface: 外部检索 / 工具执行。
- Evaluation method: six public NLP benchmarks。
- Key mechanisms: decoupling；token efficiency；robustness under tool failure。
- What it directly supports: detour bundle / multi-hop evidence gathering 的离线草图。
- What it only analogically supports: 一次性准备多个回看点。
- What it argues against: 每取到一点观察就重跑大模型。
- Fit to Reading Companion: 适合**受限 detour 包**，例如一次规划 2–3 个待核查点。
- Misfit / limitation: 阅读中很多跳转要基于最新理解实时改写，不能完全提前冻结计划。
- Complexity implication: 中；要引入占位变量和执行阶段绑定。
- Candidate project-relevant implications: 可借鉴到“局部证据采样”而非全局阅读。
- Evidence strength: 中高

### Work Card: Reflexion

- Work ID: P-WORK-004
- Source link: <https://arxiv.org/abs/2303.11366>
- Authors / Organization: Noah Shinn et al.
- Year / First Posted: 2023
- Venue / Source: arXiv
- Source Type: paper
- Read status: deep-read
- Maturity: Recent arXiv
- Original problem: 语言 agent 难以从 trial-and-error 快速学习。
- Target agent / system / user setting: sequential decision-making、coding、reasoning agents。
- Planning / navigation / recommendation ontology: `feedback -> verbal reflection -> episodic memory -> next trial`。
- Control loop: 试错式多轮 episode。
- Action selection or recommendation mechanism: 反思文本改变下一轮策略。
- Planner-executor interface: 反思位于 episode 之间，不是每步都干预。
- Memory / state interface: episodic memory buffer 存 reflective text。
- Tool / environment interface: 环境反馈、heuristics、self-evaluation、unit tests。
- Evaluation method: AlfWorld / HotPotQA / HumanEval 等。
- Key mechanisms: verbal reinforcement；feedback amplification to natural language；reflection memory。
- What it directly supports: slow-cycle planning adjustment；failed navigation learning。
- What it only analogically supports: reading strategy memo。
- What it argues against: 只记录结果、不记录错因。
- Fit to Reading Companion: 很适合**章末或 session 末**做策略校正，而不是内容理解主循环内频繁插反思。
- Misfit / limitation: 若把 reflection 混入内容记忆，会污染书本理解层。
- Complexity implication: 中；需要独立 reflection memory 层。
- Candidate project-relevant implications: audit trace 与 strategy memory 应分离于 source memory。
- Evidence strength: 高

### Work Card: Search-based deliberation family

- Work ID: P-WORK-005
- Source link: <https://arxiv.org/abs/2305.10601>
- Authors / Organization: Shunyu Yao et al.; Andy Zhou et al.; Shibo Hao et al.; Maciej Besta et al.
- Year / First Posted: 2023
- Venue / Source: arXiv family
- Source Type: papers
- Read status: deep-read for ToT/LATS/GoT; partial-read for RAP
- Maturity: Recent arXiv
- Original problem: 单路径自回归推理对 lookahead、探索、回溯不足。
- Target agent / system / user setting: difficult reasoning and planning tasks。
- Planning / navigation / recommendation ontology: branch / score / backtrack / search。
- Control loop: DFS/BFS/MCTS/graph-expansion。
- Action selection or recommendation mechanism: value/self-eval/environment feedback 决定扩展路径。
- Planner-executor interface: 搜索器与 candidate trajectory evaluator 分离。
- Memory / state interface: tree/graph nodes + value estimates。
- Tool / environment interface: 可接环境反馈，也可纯内部 world-model。
- Evaluation method: Game of 24、WebShop、HumanEval 等。
- Key mechanisms: branching、backtracking、value-guided search、aggregation。
- What it directly supports: hard passage deep-dive；thematic path comparison。
- What it only analogically supports: 普通阅读推进。
- What it argues against: 默认主循环采用 search-based planning。ToT 自己也强调其适合 deliberate reasoning，且代价可达 CoT 的 5–100 倍。
- Fit to Reading Companion: 作为**可选深钻模式**合理，作为默认读书主路不合理。
- Misfit / limitation: 成本高、延迟高、解释门槛高；对 source-order continuity 破坏大。
- Complexity implication: 高。
- Candidate project-relevant implications: 只应在“难段/争议解释/多主题比较”时触发。
- Evidence strength: 高

### Work Card: Hierarchical Planning / Options / MAXQ family

- Work ID: P-WORK-010
- Source link: <https://doi.org/10.1016/S0004-3702(99)00052-1>
- Authors / Organization: Richard S. Sutton, Doina Precup, Satinder Singh; Kutluhan Erol; Thomas G. Dietterich
- Year / First Posted: 1996–2000
- Venue / Source: thesis / Artificial Intelligence / JAIR
- Source Type: classic theory papers
- Read status: partial-read
- Maturity: Classic theory
- Original problem: 长时程控制中，每一步都重规划会低效，动作需要 temporally extended abstraction。
- Target agent / system / user setting: classical planning / hierarchical RL。
- Planning / navigation / recommendation ontology: tasks, subtasks, options, macro-actions, subroutines。
- Control loop: 高层选 option，低层执行直到终止。
- Action selection or recommendation mechanism: temporal abstraction 减少决策频率。
- Planner-executor interface: meta-controller / worker；subtask decomposition。
- Memory / state interface: 高层状态与低层状态可分层。
- Tool / environment interface: 域动作与子程序。
- Evaluation method: formal properties / sample efficiency / decomposition quality。
- Key mechanisms: hierarchy；temporally extended action；controller-worker separation。
- What it directly supports: book/chapter/section/unit/detour/slow-cycle 分层理解。
- What it only analogically supports: 用户可见推荐 UI。
- What it argues against: 把所有控制都塞进同一层 LLM loop。
- Fit to Reading Companion: 很强；尤其帮助区分 micro navigation、meso detour、macro chapter consolidation。
- Misfit / limitation: 这些理论不是为 source-grounded reading recommendation 写的，需做语义改造。
- Complexity implication: 低到中；如果只借“层级分工”思想，成本可控。
- Candidate project-relevant implications: `Navigate` 更像 meta-controller；runner 更像 deterministic executor。
- Evidence strength: 中高

### Work Card: Agent Workflow Orchestration

- Work ID: P-WORK-012
- Source link: <https://docs.langchain.com/oss/javascript/langgraph/overview>
- Authors / Organization: LangGraph docs team; [OpenAI](https://openai.com) platform docs
- Year / First Posted: 2024–2026
- Venue / Source: official docs
- Source Type: official framework docs
- Read status: deep-read
- Maturity: Official framework docs
- Original problem: agent 需要长时程状态、恢复、人工中断、审计与 tracing。
- Target agent / system / user setting: production orchestration runtimes。
- Planning / navigation / recommendation ontology: graphs, checkpoints, interrupts, handoffs, traces。
- Control loop: node-based orchestration + resumable state。
- Action selection or recommendation mechanism: graph edges / handoffs / guardrails。
- Planner-executor interface: 可显式路由 specialist ownership。
- Memory / state interface: persistence, checkpoints, resumable threads。
- Tool / environment interface: tools, MCP, human review, tracing。
- Evaluation method: traces / trace grading / debug visibility。
- Key mechanisms: durable execution；interrupt gates；trace grading。
- What it directly supports: audit trace、runner settlement、pause/resume review gate。
- What it only analogically supports: graph workflow runtime migration。
- What it argues against: 因为“看起来先进”就把系统重构成多 agent graph。
- Fit to Reading Companion: 工程启发强；架构迁移必要性弱。
- Misfit / limitation: 这些框架解决的是 orchestration substrate，不自动解决 reading judgment。
- Complexity implication: 中到高，取决于是否全量迁移。
- Candidate project-relevant implications: 借 checkpoint / interrupt / trace，不必照搬 graph runtime。
- Evidence strength: 高

### Work Card: Information Foraging / Exploratory Search

- Work ID: P-WORK-014
- Source link: <https://doi.org/10.1037/0033-295X.106.4.643>
- Authors / Organization: Peter Pirolli, Stuart K. Card; Gary Marchionini; Ryen W. White, Resa A. Roth
- Year / First Posted: 1999–2009
- Venue / Source: Psychological Review / CACM / book
- Source Type: theory + HCI
- Read status: partial-read / skimmed
- Maturity: Classic theory / Established paper
- Original problem: 人如何在信息空间中平衡价值、线索、成本与跳转。
- Target agent / system / user setting: information seekers in open information environments。
- Planning / navigation / recommendation ontology: patch、scent、cost-benefit、open-ended exploration。
- Control loop: 评估当前 patch 的边际收益，再决定 stay / leave。
- Action selection or recommendation mechanism: 信息气味与价值率。
- Planner-executor interface: 不强调 planner，强调 situated navigation。
- Memory / state interface: 依赖当前目标、局部线索、先前探索。
- Tool / environment interface: 信息空间导航。
- Evaluation method: rate of gain / exploratory task support。
- Key mechanisms: scent；value-cost tradeoff；iterative opportunistic navigation。
- What it directly supports: “什么时候继续主线，什么时候 detour”。
- What it only analogically supports: 全局 chapter plan。
- What it argues against: 把阅读导航当成固定任务分解问题。
- Fit to Reading Companion: 极高；这是本轮最贴近“下一步读哪里”的外部领域。
- Misfit / limitation: 人类信息觅食研究通常不含 LLM memory / audit trace / explanation surface。
- Complexity implication: 低；可先用 heuristics，不必先上 planner。
- Candidate project-relevant implications: mainline continuity 与 detour value 应被并列考量。
- Evidence strength: 高

### Work Card: Active Reading / Rereading / Metacomprehension

- Work ID: P-WORK-020
- Source link: <https://doi.org/10.3758/BF03209348>
- Authors / Organization: Katherine A. Rawson et al.; John Dunlosky, Amanda R. Lipko
- Year / First Posted: 2000–2007
- Venue / Source: Memory & Cognition / Current Directions in Psychological Science
- Source Type: reading / cognition papers
- Read status: partial-read
- Maturity: Established paper
- Original problem: 读者何时真正理解、何时只是以为理解。
- Target agent / system / user setting: human readers / learning regulation。
- Planning / navigation / recommendation ontology: reading trial、monitoring accuracy、rereading、self-evaluation。
- Control loop: 读 -> 判断理解 -> 回看 / 不回看 -> 再判断。
- Action selection or recommendation mechanism: 监控准确性与 reread 收益。
- Planner-executor interface: 无传统 planner；更像 metacognitive regulation。
- Memory / state interface: comprehension judgment 与 test performance 的关系。
- Tool / environment interface: text materials。
- Evaluation method: metacomprehension accuracy、gamma correlation、learning outcomes。
- Key mechanisms: rereading can improve metacomprehension accuracy；people’s metacomprehension is often poor。
- What it directly supports: look-back policy 不能靠直觉，应有触发条件。
- What it only analogically supports: 章末 carry-forward。
- What it argues against: “感觉不稳就再读一次” 的无差别回看。
- Fit to Reading Companion: 很高；look-back policy 的最直接外部证据之一。
- Misfit / limitation: 这些研究是人类受试者，不直接告诉 agent 如何实现触发器。
- Complexity implication: 低；更偏 policy heuristic than architecture。
- Candidate project-relevant implications: 回看应被视为 calibration move，而不是默认 move。
- Evidence strength: 高

### Work Card: Adaptive Navigation Support

- Work ID: P-WORK-018
- Source link: <https://doi.org/10.1111/1467-8535.00345>
- Authors / Organization: Peter Brusilovsky
- Year / First Posted: 2003
- Venue / Source: British Journal of Educational Technology
- Source Type: paper
- Read status: partial-read
- Maturity: Established paper
- Original problem: 在教育超媒体中，如何按用户知识水平提供不同导航支持。
- Target agent / system / user setting: educational hypermedia learners。
- Planning / navigation / recommendation ontology: direct guidance、sorting、hiding、annotation、generation。
- Control loop: 依据 learner model 动态调整 link-level navigation support。
- Action selection or recommendation mechanism: 基于知识水平与上下文的适配。
- Planner-executor interface: 无重 planner；重点在适配表面。
- Memory / state interface: learner knowledge level / history。
- Tool / environment interface: hypermedia links。
- Evaluation method: empirical studies of techniques across contexts。
- Key mechanisms: direct guidance、adaptive annotation、meta-adaptation。
- What it directly supports: user-visible route disclosure policy；何时提示、提示强度如何。
- What it only analogically supports: internal navigation planning。
- What it argues against: 单一强提示策略适用于所有用户与所有时刻。
- Fit to Reading Companion: 极高；尤其适用于 recommendation 不是命令、而是支架。
- Misfit / limitation: 教育超媒体中的 link adaptation 不等于 source-span reading。
- Complexity implication: 低到中。
- Candidate project-relevant implications: recommendation 应可弱提示、低打扰、可解释。
- Evidence strength: 高

### Work Card: Learner Agency / Open Learner Model

- Work ID: P-WORK-023
- Source link: <https://doi.org/10.1007/s11257-016-9186-6>
- Authors / Organization: Yanjin Long, Vincent Aleven; Michelle Deschênes
- Year / First Posted: 2017–2020
- Venue / Source: UMUAI / systematic review
- Source Type: paper + review
- Read status: partial-read
- Maturity: Established paper
- Original problem: 推荐与 learner modeling 如何支持 self-regulated learning，而不替代 learner。
- Target agent / system / user setting: ITS / technology-enhanced learning。
- Planning / navigation / recommendation ontology: open learner model、problem-selection decisions、agency support。
- Control loop: 系统显式呈现 learner state，并支持 learner 自主调整选择。
- Action selection or recommendation mechanism: 建模 + 可见状态 + user control。
- Planner-executor interface: 系统建议、用户决定。
- Memory / state interface: learner model exposed or partly exposed.
- Tool / environment interface: tutoring / learning platform。
- Evaluation method: learning outcomes + SRL support + agency review findings。
- Key mechanisms: open model；self-regulated selection；agency-preserving recommendation。
- What it directly supports: recommendation rationale 的“可理解但不强制”。
- What it only analogically supports: internal memory state exposure。
- What it argues against: 黑箱推荐直接接管阅读路线。
- Fit to Reading Companion: 很高；尤其适合把 recommendation 设计成 optional scaffold。
- Misfit / limitation: OLM 通常有显式 mastery / learner model；Reading Companion 不能假装自己有完整 mastery map。
- Complexity implication: 中。
- Candidate project-relevant implications: 可见 rationale 不等于暴露内部所有 planner state。
- Evidence strength: 中高

### Work Card: Learning Path Recommendation / TEL Recommenders

- Work ID: P-WORK-019
- Source link: <https://doi.org/10.1504/IJCEELL.2003.002154>
- Authors / Organization: Peter Brusilovsky, Julita Vassileva; Nikos Manouselis et al.
- Year / First Posted: 2003–2011
- Venue / Source: IJCEELL / Recommender Systems Handbook
- Source Type: paper + handbook chapter
- Read status: partial-read / skimmed
- Maturity: Established paper
- Original problem: 如何根据 goal / prior knowledge / prerequisite 生成个性化学习序列。
- Target agent / system / user setting: web-based education / TEL。
- Planning / navigation / recommendation ontology: course sequencing、learning objects、prerequisite path。
- Control loop: 根据 learner state 动态生成或调整课程序列。
- Action selection or recommendation mechanism: goal + knowledge + dependency constraints。
- Planner-executor interface: sequencing engine -> presented path。
- Memory / state interface: prior knowledge / success in acquiring knowledge。
- Tool / environment interface: course materials / learning objects。
- Evaluation method: pedagogical feasibility and personalization。
- Key mechanisms: prerequisite-aware sequencing；goal-conditioned path generation。
- What it directly supports: thematic path / deep-dive path / carry-forward checklist。
- What it only analogically supports: reading of non-instructional texts。
- What it argues against: 把路径推荐降格成“相关推荐 top-N”。
- Fit to Reading Companion: 中高；在“路径”概念上有价值，在 tutor 假设上要克制。
- Misfit / limitation: Reading Companion 不是 mastery-learning 系统。
- Complexity implication: 中。
- Candidate project-relevant implications: 路径应体现 dependency 与 effort，不只是 relevance。
- Evidence strength: 中

### Work Card: Planning / Recommendation Evaluation

- Work ID: P-WORK-025
- Source link: <https://doi.org/10.1145/1125451.1125659>
- Authors / Organization: Sean M. McNee et al.; Pearl Pu, Li Chen; Xiao Liu et al.; Shuyan Zhou et al.; Shunyu Yao et al.
- Year / First Posted: 2006–2024
- Venue / Source: CHI EA / RecSys / agent benchmarks
- Source Type: papers
- Read status: partial-read
- Maturity: Established paper / Recent arXiv
- Original problem: 系统成功不能只看 accuracy 或一次性 task success。
- Target agent / system / user setting: recommender systems / LLM agents。
- Planning / navigation / recommendation ontology: usefulness、trust、behavioral intention、functional correctness、pass^k reliability。
- Control loop: evaluation loop over traces, runs, tasks, repeated trials。
- Action selection or recommendation mechanism: N/A，偏评价。
- Planner-executor interface: trace grading / task log / repeated trial reliability。
- Memory / state interface: 可用 traces 区分 planner、executor、retrieval、memory 错误。
- Tool / environment interface: benchmark environments, user-centric questionnaires。
- Evaluation method: usefulness over accuracy；ResQue；functional correctness；pass^k。
- Key mechanisms: beyond-accuracy metrics；trace-aware diagnostics；multi-trial consistency。
- What it directly supports: Reading Path Quality / Recommendation Usefulness / Overplanning / Thrashing Rate 等评价方向。
- What it only analogically supports: 现成 benchmark 直接套到阅读。
- What it argues against: 只看“最后答得对不对”。
- Fit to Reading Companion: 极高；尤其对 audit trace、over-guidance、recovery quality。
- Misfit / limitation: 没有现成 benchmark 直接覆盖 source-span reading navigation。
- Complexity implication: 中。
- Candidate project-relevant implications: 评价需分 planner 错、memory 错、retrieval 错、execution 错。
- Evidence strength: 高

## Mechanism Evidence Cards

### LLM Agent Planning / Orchestration

#### Evidence Card: P-EXT-001

- External work: ReAct
- Work ID: P-WORK-001
- Year: 2022
- Mechanism name: Interleaved reasoning-action loop
- Original context: agent 在 QA / web-like environments 中交错生成 thought 与 action。
- Mechanism summary: reasoning 不先写完再执行，而是被 observation 持续修正。
- Supports which possible design area: Navigation Policy; Detour Policy; Orchestration; Audit
- Support type: Direct
- Reasoning bridge: Reading Companion 的 detour 不是先把整条 detour 路径规划完，而是先做一个局部跳转，再让新 source observation 修正后续去向。相似点是都依赖外部 observation 改写后续轨迹；差异点是 RC 的 observation 首先来自 source text，不是环境成功/失败信号。
- Why not direct copy: 阅读主循环不像 WebShop 连续动作空间；不能把每段阅读都包装成 action。
- Complexity implication: 低到中
- What project evidence would still be needed: 当前 detour 是否已有 action-observation closure
- Confidence: 高
- Stable citation: <https://arxiv.org/abs/2210.03629>

#### Evidence Card: P-EXT-002

- External work: ReAct
- Work ID: P-WORK-001
- Year: 2022
- Mechanism name: Observation-grounded correction
- Original context: external observation 用于纠正 hallucinated reasoning。
- Mechanism summary: action 带来 observation，observation 反过来约束 reasoning。
- Supports which possible design area: Detour Policy; Look-back Policy; Audit
- Support type: Direct
- Reasoning bridge: RC 中“去查一下再回主线”只有在 observation 真能改变理解时才值得。与 ReAct 相同的是 correction 依赖外部证据；不同的是 RC 的 correction 更常是解释层对齐，而非动作成败。
- Why not direct copy: 书本阅读的 observation 密度更低、解释空间更大。
- Complexity implication: 低
- What project evidence would still be needed: detour 返回主线时是否能记录“外部证据改变了什么”
- Confidence: 高
- Stable citation: <https://arxiv.org/abs/2210.03629>

#### Evidence Card: P-EXT-003

- External work: ReAct
- Work ID: P-WORK-001
- Year: 2022
- Mechanism name: Local loop boundary
- Original context: ReAct 更强于局部交互回路，而非全局任务规划。
- Mechanism summary: 它擅长 stepwise adjustment，不擅长事先给出全局长期阅读路线。
- Supports which possible design area: Planning Ontology; Navigation Policy
- Support type: Boundary
- Reasoning bridge: 这说明 ReAct 风格最适合 RC 的局部 detour/source skill loop，而不适合主线全局 planner。相似点是局部不确定性；差异点是 RC 还需要维护 mainline continuity。
- Why not direct copy: 会诱导系统每步都过度“想-行动-想”。
- Complexity implication: 中
- What project evidence would still be needed: 主循环 latency / token budget
- Confidence: 中高
- Stable citation: <https://arxiv.org/abs/2210.03629>

#### Evidence Card: P-EXT-004

- External work: Plan-and-Solve Prompting
- Work ID: P-WORK-002
- Year: 2023
- Mechanism name: Explicit pre-plan
- Original context: 先把任务拆成子步骤，再按计划求解。
- Mechanism summary: 显式计划缓解 missing-step errors。
- Supports which possible design area: Planning Ontology; Deep-dive Policy; Orchestration
- Support type: Direct
- Reasoning bridge: RC 的难段、章初、章末，比逐句主循环更适合显式 plan sketch。相似点是复杂过程会漏步；差异点是 RC 里的“步”通常是 source unit / cue / question，不是算术子题。
- Why not direct copy: 如果对每个 unit 都先输出计划，会造成 overplanning。
- Complexity implication: 中
- What project evidence would still be needed: 章节边界是否已有自然 planning moment
- Confidence: 高
- Stable citation: <https://aclanthology.org/2023.acl-long.147/>

#### Evidence Card: P-EXT-005

- External work: Plan-and-Solve Prompting
- Work ID: P-WORK-002
- Year: 2023
- Mechanism name: Boundary-level planning only
- Original context: planning 主要用于 multi-step difficulty。
- Mechanism summary: 不是“凡事先规划”，而是对复杂问题提前切分。
- Supports which possible design area: Navigation Policy; Deep-dive Policy
- Support type: Boundary
- Reasoning bridge: RC 应把 explicit planning 视为 boundary operation，不是 default operation。相似点是复杂性触发 planning；差异点是阅读中的复杂性常来自概念密度/前后文依赖，而不是解题长度。
- Why not direct copy: 用户会感到系统不断“重写阅读计划”。
- Complexity implication: 低
- What project evidence would still be needed: hard passage 的识别条件
- Confidence: 高
- Stable citation: <https://aclanthology.org/2023.acl-long.147/>

#### Evidence Card: P-EXT-006

- External work: ReWOO
- Work ID: P-WORK-003
- Year: 2023
- Mechanism name: Decoupled reasoning and observation
- Original context: 把 reasoning 先展开成结构，再去批量执行工具。
- Mechanism summary: 减少 tool-observation 交替带来的 prompt 冗余。
- Supports which possible design area: Detour Policy; Orchestration; Memory Interface
- Support type: Analogical
- Reasoning bridge: RC 的某些 detour 可以先产出“待核查点清单”，再去命中 source / evidence，而不是每看见一条证据就重新规划。相似点是降低切换成本；差异点是阅读理解的中途新发现更常逼迫重写计划。
- Why not direct copy: 过度冻结 detour plan 会降低 responsive reading。
- Complexity implication: 中
- What project evidence would still be needed: detour 是否常出现一次查多点的场景
- Confidence: 中高
- Stable citation: <https://arxiv.org/abs/2305.18323>

#### Evidence Card: P-EXT-007

- External work: ReWOO
- Work ID: P-WORK-003
- Year: 2023
- Mechanism name: Placeholder / variable-bound execution
- Original context: plan 中保留变量占位，执行后再回填。
- Mechanism summary: 计划是结构化 skeleton，不必当场拿到所有 observation。
- Supports which possible design area: Orchestration; Audit; Memory Interface
- Support type: Analogical
- Reasoning bridge: RC 可把“稍后验证的阅读疑点”作为 pending slots，而非立即打断主线。相似点是先保留 slot；差异点是 RC 的 slot 可能是语义问题而非工具返回值。
- Why not direct copy: 需要明确 slot 的过期条件与回填机制。
- Complexity implication: 中
- What project evidence would still be needed: source cursor 与 pending concern 之间如何绑定
- Confidence: 中
- Stable citation: <https://arxiv.org/abs/2305.18323>

#### Evidence Card: P-EXT-008

- External work: Reflexion
- Work ID: P-WORK-004
- Year: 2023
- Mechanism name: Episodic reflection buffer
- Original context: agent 在 episode 间存 reflective text 以改进后续尝试。
- Mechanism summary: 把失败经验存成语言化、可复用的策略记忆。
- Supports which possible design area: Memory Interface; Audit; Planning Ontology
- Support type: Direct
- Reasoning bridge: RC 中“某类 detour 常无收益”“某类难段常需回看前定义”更像 strategy memory，而不是内容 memory。相似点是跨 episode 调参；差异点是 RC 不能让 reflection 覆盖 source-grounded content state。
- Why not direct copy: 反思写进正文理解会污染内容层。
- Complexity implication: 中
- What project evidence would still be needed: project-side memory layering 是否已有独立策略层
- Confidence: 高
- Stable citation: <https://arxiv.org/abs/2303.11366>

#### Evidence Card: P-EXT-009

- External work: Reflexion
- Work ID: P-WORK-004
- Year: 2023
- Mechanism name: Feedback-to-language amplification
- Original context: binary/scalar feedback 被转成自然语言经验摘要。
- Mechanism summary: 把稀疏反馈变成可行动指导。
- Supports which possible design area: Audit; Evaluation; Memory Interface
- Support type: Direct
- Reasoning bridge: RC 若只记录“detour 成功/失败”太粗；记录“失败因为偏离主线、收益不足、证据不改判断”更有用。相似点是从弱反馈提炼策略线索；差异点是 RC 的反馈往往来自体验和路径质量，而非环境 reward。
- Why not direct copy: 语言化总结可能引入 hindsight bias。
- Complexity implication: 低到中
- What project evidence would still be needed: navigation failure taxonomy
- Confidence: 高
- Stable citation: <https://arxiv.org/abs/2303.11366>

#### Evidence Card: P-EXT-010

- External work: Tree of Thoughts
- Work ID: P-WORK-005
- Year: 2023
- Mechanism name: Branch-and-backtrack deliberation
- Original context: 在需要探索和 lookahead 的任务上探索多条 thought paths。
- Mechanism summary: 允许分支、评估、回溯。
- Supports which possible design area: Deep-dive Policy; Recommendation Policy
- Support type: Analogical
- Reasoning bridge: RC 在硬段落上可能需要比较两三种解释路径或阅读顺序候选。相似点是都需要比较替代路径；差异点是 RC 通常只需小规模分支，而不是全局树搜索。
- Why not direct copy: exposition-heavy text 的路径分支难客观打分。
- Complexity implication: 高
- What project evidence would still be needed: 哪类 hard passage 真需要多路径比较
- Confidence: 高
- Stable citation: <https://arxiv.org/abs/2305.10601>

#### Evidence Card: P-EXT-011

- External work: Tree of Thoughts
- Work ID: P-WORK-005
- Year: 2023
- Mechanism name: Search cost warning
- Original context: deliberate search 带来显著 token 与金钱开销。
- Mechanism summary: 论文明确指出 ToT 更适用于 CoT 失效的 deliberate reasoning，且成本可能高得多。
- Supports which possible design area: Navigation Policy; Evaluation
- Support type: Negative
- Reasoning bridge: 这直接支持 RC 不应把 search-based planning 设为默认主循环。相似点是都受成本限制；差异点是阅读陪伴系统对交互节奏更敏感。
- Why not direct copy: 默认主循环会慢、贵、难用。
- Complexity implication: 高
- What project evidence would still be needed: acceptable latency budget
- Confidence: 高
- Stable citation: <https://arxiv.org/abs/2305.10601>

#### Evidence Card: P-EXT-012

- External work: LATS
- Work ID: P-WORK-007
- Year: 2023
- Mechanism name: MCTS + value + self-reflection + environment feedback
- Original context: general language agent planning via Monte Carlo Tree Search。
- Mechanism summary: 用 MCTS 构造 trajectory，并结合 LM-powered value functions 与 self-reflections。
- Supports which possible design area: Deep-dive Policy; Evaluation
- Support type: Analogical
- Reasoning bridge: RC 可借鉴的是“难问题时临时上更重 deliberation”，不是“任何阅读步都走 MCTS”。相似点是局部困难需要多路径评估；差异点是 RC 缺少像 WebShop 那样清晰的外部 reward。
- Why not direct copy: value function 和 terminal reward 在阅读理解里更难定义。
- Complexity implication: 很高
- What project evidence would still be needed: 阅读路径质量可否可操作化成局部 value
- Confidence: 高
- Stable citation: <https://arxiv.org/abs/2310.04406>

#### Evidence Card: P-EXT-013

- External work: Reasoning with Language Model is Planning with World Model
- Work ID: P-WORK-008
- Year: 2023
- Mechanism name: World-model planning
- Original context: 让 LLM 同时扮演 reasoning agent 与 world model，用 MCTS 搜 reasoning path。
- Mechanism summary: 通过预测状态与奖励来进行 deliberate planning。
- Supports which possible design area: Planning Ontology; Deep-dive Policy
- Support type: Boundary
- Reasoning bridge: 这项工作说明“当状态可模拟、奖励可估计”时，planning with world model 很强；但阅读往往没有稳定可验证的 simulated future state。相似点是都要权衡下一步；差异点是阅读中的语义世界模型远不如 Blocksworld 清晰。
- Why not direct copy: 阅读对象是开放语义文本，不是封闭状态空间。
- Complexity implication: 很高
- What project evidence would still be needed: 是否存在少数可 world-model 化的 micro tasks
- Confidence: 中高
- Stable citation: <https://arxiv.org/abs/2305.14992>

#### Evidence Card: P-EXT-014

- External work: HTN planning
- Work ID: P-WORK-009
- Year: 1996
- Mechanism name: Hierarchical task decomposition
- Original context: 把任务分解为子任务网络。
- Mechanism summary: 高层目标通过结构化分解落到执行层。
- Supports which possible design area: Planning Ontology; Orchestration
- Support type: Direct
- Reasoning bridge: RC 的层级天然存在：book -> chapter -> section -> source unit -> detour。相似点是都需跨时间尺度控制；差异点是 RC 的分解对象不是外部任务，而是阅读进程。
- Why not direct copy: HTN 通常假设任务网络更明确。
- Complexity implication: 低到中
- What project evidence would still be needed: 现有项目对象层级是否稳定
- Confidence: 中高
- Stable citation: <http://hdl.handle.net/1903/5810>

#### Evidence Card: P-EXT-015

- External work: Options framework
- Work ID: P-WORK-010
- Year: 1999
- Mechanism name: Temporal abstraction via options
- Original context: 用 temporally extended actions 降低逐步决策负担。
- Mechanism summary: option 是可持续一段时间的宏动作。
- Supports which possible design area: Planning Ontology; Navigation Policy; Detour Policy
- Support type: Direct
- Reasoning bridge: RC 可以把“继续主线一段”“执行一个 bounded detour”“章末 consolidation”视为 options。相似点是减少每步重算；差异点是 RC 的 option 终止条件更偏语义而非状态机。
- Why not direct copy: 终止条件难以形式化。
- Complexity implication: 低
- What project evidence would still be needed: detour / look-back 的自然终止信号
- Confidence: 中高
- Stable citation: <https://doi.org/10.1016/S0004-3702(99)00052-1>

#### Evidence Card: P-EXT-016

- External work: MAXQ
- Work ID: P-WORK-011
- Year: 2000
- Mechanism name: Controller-worker decomposition
- Original context: 分解 value function 与 subroutine hierarchy。
- Mechanism summary: 高层控制器不必处理所有低层细节。
- Supports which possible design area: Orchestration; Memory Interface
- Support type: Analogical
- Reasoning bridge: RC 中高层 `Navigate` 不应承担所有 execution 细节，runner 可以保持 deterministic。相似点是层间职责分离；差异点是 RC 不需要 RL value decomposition 本身。
- Why not direct copy: RL formalism 不是直接实现蓝图。
- Complexity implication: 低
- What project evidence would still be needed: runner 与 LLM 之间当前职责边界
- Confidence: 中
- Stable citation: <https://doi.org/10.1613/jair.639>

#### Evidence Card: P-EXT-017

- External work: LangGraph
- Work ID: P-WORK-012
- Year: 2024–2026
- Mechanism name: Durable execution / checkpoints
- Original context: stateful, long-running agents 的恢复与 persistence。
- Mechanism summary: 保存每个执行步骤状态，支持失败后恢复。
- Supports which possible design area: Orchestration; Audit; Memory Interface
- Support type: Direct
- Reasoning bridge: RC 的 chapter/session 级运行天然可能被打断，且读者会跨会话继续。相似点是都需要 persistent cursor；差异点是 RC 还要区分 source cursor、memory state、user-facing state。
- Why not direct copy: checkpoint substrate 不能替代 navigation judgment。
- Complexity implication: 中
- What project evidence would still be needed: 当前 runner settlement 是否需要可恢复 checkpoint
- Confidence: 高
- Stable citation: <https://docs.langchain.com/oss/javascript/langgraph/overview>

#### Evidence Card: P-EXT-018

- External work: LangGraph
- Work ID: P-WORK-012
- Year: 2024–2026
- Mechanism name: Interrupt / human review gate
- Original context: workflow 在关键点暂停，等待外部输入，再从 checkpoint 恢复。
- Mechanism summary: interrupt 触发后保存状态，恢复时整节点从头执行，因此前置 side effects 必须幂等。
- Supports which possible design area: Recommendation Policy; Audit; Orchestration
- Support type: Direct
- Reasoning bridge: RC 的“是否把推荐展示给用户”“是否允许用户改写路径”可建模为 review gate。相似点是都需要 pause/resume；差异点是 RC 的中断多半是 UX 道德边界，而非高风险工具调用。
- Why not direct copy: 节点重启语义会影响 side-effecting code。
- Complexity implication: 中
- What project evidence would still be needed: recommendation surface 是否需要可暂停审批
- Confidence: 高
- Stable citation: <https://docs.langchain.com/oss/python/langgraph/interrupts>

#### Evidence Card: P-EXT-019

- External work: OpenAI Agents SDK
- Work ID: P-WORK-013
- Year: 2025–2026
- Mechanism name: Handoffs + guardrails + results/state separation
- Original context: code-first agent apps 中的 orchestration 与 ownership control。
- Mechanism summary: 文档明确把 orchestration and handoffs、guardrails、results and state 分开说明。
- Supports which possible design area: Orchestration; Audit; Recommendation Policy
- Support type: Background
- Reasoning bridge: 这不是直接告诉 RC “该如何导航”，但它强化了一个工程分层原则：routing、approval、state/result 不应混写。相似点是都需分层；差异点是 RC 的核心判断仍在阅读语义，不在 SDK surface。
- Why not direct copy: 官方 SDK 是通用 orchestration substrate。
- Complexity implication: 中
- What project evidence would still be needed: 当前项目是否已经有清晰 state/result layering
- Confidence: 高
- Stable citation: <https://developers.openai.com/api/docs/guides/agents>

#### Evidence Card: P-EXT-020

- External work: Trace grading docs
- Work ID: P-WORK-013
- Year: 2025–2026
- Mechanism name: Trace-level grading
- Original context: 用结构化分数/标签评估 agent trace。
- Mechanism summary: 面向 decisions、tool calls、reasoning steps 的 end-to-end logs 做诊断和回归。
- Supports which possible design area: Audit; Evaluation
- Support type: Direct
- Reasoning bridge: RC 若想分清 planner 错、memory 错、retrieval 错、recommendation 错，需要 trace-level grading，而不是仅看最终摘要对不对。相似点是都需要可归因日志；差异点是 RC 的 trace 中 source cursor / span 更关键。
- Why not direct copy: grading rubric 需针对阅读路径质量重写。
- Complexity implication: 中
- What project evidence would still be needed: trace schema 是否足够表达导航判断
- Confidence: 高
- Stable citation: <https://developers.openai.com/api/docs/guides/trace-grading>

### HCI / Reading Navigation / Recommendation

#### Evidence Card: P-EXT-021

- External work: Information Foraging
- Work ID: P-WORK-014
- Year: 1999
- Mechanism name: Rate-of-gain tradeoff
- Original context: 信息寻求是价值获取率最大化问题。
- Mechanism summary: 用户在成本与信息价值之间做 patch switching。
- Supports which possible design area: Navigation Policy; Detour Policy; Recommendation Policy
- Support type: Direct
- Reasoning bridge: RC 的“下一步读哪里”与其说是任务 planning，不如说是比较当前主线、回看、detour 三者的边际价值。相似点是都关注 value/cost；差异点是 RC 的价值不只是找到信息，更是维护理解连续性。
- Why not direct copy: 价值函数需要包含 comprehension continuity。
- Complexity implication: 低
- What project evidence would still be needed: 主线连续性的可操作 proxy
- Confidence: 高
- Stable citation: <https://doi.org/10.1037/0033-295X.106.4.643>

#### Evidence Card: P-EXT-022

- External work: Information Foraging
- Work ID: P-WORK-014
- Year: 1999
- Mechanism name: Information scent
- Original context: 局部线索提示某信息源是否值得继续。
- Mechanism summary: “气味”帮助决定 follow / abandon 当前路径。
- Supports which possible design area: Navigation Policy; Recommendation Policy
- Support type: Direct
- Reasoning bridge: RC 可把 source span 提供的实体、定义缺口、未闭合问题视为 scent。相似点是都是局部 cue 引导跳转；差异点是 RC 的 scent 要强绑定 source-grounded unresolved concerns。
- Why not direct copy: novelty 也会产生强 scent，但未必有益。
- Complexity implication: 低
- What project evidence would still be needed: 哪类 unresolved concern 真具高阅读收益
- Confidence: 中高
- Stable citation: <https://doi.org/10.1037/0033-295X.106.4.643>

#### Evidence Card: P-EXT-023

- External work: Exploratory Search
- Work ID: P-WORK-015
- Year: 2006
- Mechanism name: From finding to understanding
- Original context: 搜索不只是找事实，而是形成理解。
- Mechanism summary: exploratory search 是 open-ended、iterative、多策略的。
- Supports which possible design area: Recommendation Policy; User-facing Rationale
- Support type: Analogical
- Reasoning bridge: RC 的推荐阅读更像 exploratory support，而不是 known-item retrieval。相似点是目标不完全预设；差异点是 RC 已有主 source，不是从空白信息空间出发。
- Why not direct copy: 书籍阅读并非典型搜索会话。
- Complexity implication: 低
- What project evidence would still be needed: 用户目标显式程度与 exploratory need 的关系
- Confidence: 中高
- Stable citation: <https://cacm.acm.org/research/exploratory-search/>

#### Evidence Card: P-EXT-024

- External work: Adaptive Hypermedia
- Work ID: P-WORK-017
- Year: 2001
- Mechanism name: User-model-based adaptation
- Original context: 基于 goals / preferences / knowledge 的界面与内容适配。
- Mechanism summary: adaptation 不只是排序，也包含导航与 presentation。
- Supports which possible design area: Recommendation Policy; Memory Interface
- Support type: Analogical
- Reasoning bridge: RC 需要把 internal navigation 与 user-visible recommendation 分层，而 adaptive hypermedia 正好强调“基于用户模型适配交互表面”。相似点是用户状态驱动；差异点是 RC 更强调 source-groundedness。
- Why not direct copy: RC 可能没有成熟 learner model。
- Complexity implication: 中
- What project evidence would still be needed: 用户画像粒度是否值得进入 recommendation logic
- Confidence: 中高
- Stable citation: <https://doi.org/10.1023/A:1011143116306>

#### Evidence Card: P-EXT-025

- External work: Adaptive Navigation Support in Educational Hypermedia
- Work ID: P-WORK-018
- Year: 2003
- Mechanism name: Direct guidance / adaptive annotation
- Original context: 超媒体链接层面的适配提示。
- Mechanism summary: 不同用户知识水平适合不同 ANS 技术。
- Supports which possible design area: Recommendation Policy; User-facing Rationale
- Support type: Direct
- Reasoning bridge: RC 的 recommendation 可以是短提示、排序、注记，而不必须是强命令。相似点是都在 path surface 上做支架；差异点是 RC 的单位是 source spans 与 detours，不是网页链接。
- Why not direct copy: 链接 UI 不是 source-span UI。
- Complexity implication: 低
- What project evidence would still be needed: 哪种 recommendation surface 最不侵入
- Confidence: 高
- Stable citation: <https://doi.org/10.1111/1467-8535.00345>

#### Evidence Card: P-EXT-026

- External work: Adaptive Navigation Support in Educational Hypermedia
- Work ID: P-WORK-018
- Year: 2003
- Mechanism name: Meta-adaptation
- Original context: 不同情境、不同知识水平需要不同导航支持。
- Mechanism summary: 单一适配技术并不总是最优。
- Supports which possible design area: Recommendation Policy
- Support type: Boundary
- Reasoning bridge: RC 不应设计成固定强度的推荐器。相似点是 guidance 强度要依用户与阶段变；差异点是 RC 还要考虑文本难度和主线完整性。
- Why not direct copy: 需要更轻量的适配维度。
- Complexity implication: 低
- What project evidence would still be needed: 何种用户阶段需要更主动 recommendation
- Confidence: 高
- Stable citation: <https://doi.org/10.1111/1467-8535.00345>

#### Evidence Card: P-EXT-027

- External work: Course Sequencing
- Work ID: P-WORK-019
- Year: 2003
- Mechanism name: Prerequisite-aware sequencing
- Original context: goal、prior knowledge、prerequisite 约束下自动生成个性化课程序列。
- Mechanism summary: path 是 sequence，不是 unordered list。
- Supports which possible design area: Recommendation Policy; Planning Ontology
- Support type: Analogical
- Reasoning bridge: RC 的 thematic path 或 deep-dive path 如果存在，就应有 dependency logic。相似点是 sequence design；差异点是 RC 不应假设 mastery diagnosis。
- Why not direct copy: pedagogical sequencing 常依赖显式课程图谱。
- Complexity implication: 中
- What project evidence would still be needed: source graph / concept dependency feasibility
- Confidence: 中高
- Stable citation: <https://doi.org/10.1504/IJCEELL.2003.002154>

#### Evidence Card: P-EXT-028

- External work: The rereading effect
- Work ID: P-WORK-020
- Year: 2000
- Mechanism name: Rereading improves metacomprehension accuracy
- Original context: 读两遍的参与者对自己理解水平的判断更准。
- Mechanism summary: rereading 的价值部分在于 calibration，而不只是重复暴露。
- Supports which possible design area: Look-back Policy; Evaluation
- Support type: Direct
- Reasoning bridge: RC 推荐回看时，理由不应只是“再看一遍也许更懂”，而应更像“这里需要重新校准理解”。相似点是都服务于 understanding monitoring；差异点是 agent 需要定义何时收益大于成本。
- Why not direct copy: 人类实验不等于任意文本都值得回看。
- Complexity implication: 低
- What project evidence would still be needed: look-back 触发后的收益衡量
- Confidence: 高
- Stable citation: <https://doi.org/10.3758/BF03209348>

#### Evidence Card: P-EXT-029

- External work: Metacomprehension
- Work ID: P-WORK-021
- Year: 2007
- Mechanism name: Metacomprehension is often poor
- Original context: 人们对自己是否学会文本材料的判断长期以来都不准。
- Mechanism summary: 自我监控精度本身就是问题。
- Supports which possible design area: Look-back Policy; Deep-dive Policy; User-facing Rationale
- Support type: Direct
- Reasoning bridge: RC 不能简单照用户即时感觉“我懂了/我没懂”行事，也不能照 agent 自己的流畅感行事。相似点是都需要 calibration；差异点是 RC 还要在用户自主性与系统警告之间平衡。
- Why not direct copy: 不能以心理学结论为由否定用户判断。
- Complexity implication: 低
- What project evidence would still be needed: 可操作的 uncertainty / instability signals
- Confidence: 高
- Stable citation: <https://doi.org/10.1111/j.1467-8721.2007.00509.x>

#### Evidence Card: P-EXT-030

- External work: Learner agency review
- Work ID: P-WORK-022
- Year: 2020
- Mechanism name: Agency-preserving recommendation
- Original context: technology-enhanced learning recommenders 与 learners’ agency 的系统综述。
- Mechanism summary: 推荐系统应支持而非替代学习者定义和追求目标。
- Supports which possible design area: Recommendation Policy; User-facing Rationale
- Support type: Direct
- Reasoning bridge: RC 的推荐如果替用户决定“你应该读这个而不是那个”，就违背第二读者定位。相似点是 recommendation 需要 support agency；差异点是 RC 的对象常是深阅读而非课程平台。
- Why not direct copy: learning context 的 agency 指标需翻译成阅读场景。
- Complexity implication: 低
- What project evidence would still be needed: UI 层是否支持拒绝/跳过/稍后再看
- Confidence: 高
- Stable citation: <https://doi.org/10.1186/s41239-020-00219-w>

#### Evidence Card: P-EXT-031

- External work: Open Learner Model
- Work ID: P-WORK-023
- Year: 2017
- Mechanism name: SRL support with visible learner model
- Original context: OLM 支架 self-regulated learning，并支持 problem selection decisions。
- Mechanism summary: 支持用户做选择，而不是系统全部替做。
- Supports which possible design area: Recommendation Policy; User-facing Rationale; Memory Interface
- Support type: Analogical
- Reasoning bridge: RC 可以只暴露足以帮助用户决策的局部 rationale，而不是暴露全部内部思维。相似点是都借“可见状态”提升自调节；差异点是 RC 的状态是阅读关注点，不是 mastery meter。
- Why not direct copy: 完整 OLM 需要稳定 learner modeling。
- Complexity implication: 中
- What project evidence would still be needed: 哪些 internal signals 值得对用户可见
- Confidence: 中高
- Stable citation: <https://doi.org/10.1007/s11257-016-9186-6>

#### Evidence Card: P-EXT-032

- External work: Tsai & Brusilovsky 2021
- Work ID: P-WORK-024
- Year: 2021
- Mechanism name: Controllability + explainability
- Original context: 混合社交推荐系统中同时提供控制和解释。
- Mechanism summary: end users 参与推荐过程，解释提高透明度，二者组合影响用户体验。
- Supports which possible design area: Recommendation Policy; User-facing Rationale; Evaluation
- Support type: Direct
- Reasoning bridge: RC 的 recommendation 最理想的形态不是纯黑箱，也不是纯命令，而是可轻调、低打扰、可理解。相似点是 recommendation needs both control and reason-giving；差异点是 RC 的“控制”可能只是接受/拒绝/稍后。
- Why not direct copy: 具体可调参数在阅读中未必合适。
- Complexity implication: 中
- What project evidence would still be needed: 最低可行 controllability surface
- Confidence: 高
- Stable citation: <https://doi.org/10.1007/s11257-020-09281-5>

### Evaluation

#### Evidence Card: P-EXT-033

- External work: McNee et al. 2006
- Work ID: P-WORK-025
- Year: 2006
- Mechanism name: Beyond-accuracy evaluation
- Original context: accuracy metrics 不能代表 recommender usefulness。
- Mechanism summary: 最准确的不一定最有用。
- Supports which possible design area: Evaluation; Recommendation Policy
- Support type: Direct
- Reasoning bridge: RC 的 recommendation 不能只按“命中用户后来读了什么”衡量，更要看它是否真正帮助理解、减少 thrashing、保留 agency。相似点是 usefulness 不等于 predictive accuracy；差异点是 RC 的目标是 reading support 不是消费转化。
- Why not direct copy: 需要重写 usefulness constructs。
- Complexity implication: 低
- What project evidence would still be needed: 阅读效用指标定义
- Confidence: 高
- Stable citation: <https://doi.org/10.1145/1125451.1125659>

#### Evidence Card: P-EXT-034

- External work: ResQue
- Work ID: P-WORK-026
- Year: 2011
- Mechanism name: User-centric evaluation constructs
- Original context: 从用户角度评估推荐质量、可用性、满意度与行为意向。
- Mechanism summary: usefulness、usability、interaction qualities、satisfaction、behavioral intention 可共同评估。
- Supports which possible design area: Evaluation; Recommendation Policy
- Support type: Direct
- Reasoning bridge: RC 的 user-visible route disclosure 也应被单独评估，而不是被整体阅读输出掩盖。相似点是都讲 user experience；差异点是 RC 的行为意向可能是继续主线、接受 detour、忽略推荐。
- Why not direct copy: ResQue 原量表需场景改写。
- Complexity implication: 低到中
- What project evidence would still be needed: RC-specific questionnaire items
- Confidence: 高
- Stable citation: <https://doi.org/10.1145/2043932.2043962>

#### Evidence Card: P-EXT-035

- External work: WebArena
- Work ID: P-WORK-028
- Year: 2023
- Mechanism name: Functional correctness in realistic long-horizon environments
- Original context: realistic web tasks 上的 end-to-end success benchmark。
- Mechanism summary: long-horizon、realistic、functional correctness，显示当前 agent 与人类差距很大。
- Supports which possible design area: Evaluation; Audit
- Support type: Background
- Reasoning bridge: 对 RC 的启发不是“去用 Web benchmark”，而是提醒必须把 long-horizon recovery 与 correctness分开测。相似点是长链路错误会累积；差异点是 RC 没有按钮点击但有 source navigation。
- Why not direct copy: 环境和动作空间差异过大。
- Complexity implication: 低
- What project evidence would still be needed: source-reading benchmark scaffold
- Confidence: 中高
- Stable citation: <https://arxiv.org/abs/2307.13854>

#### Evidence Card: P-EXT-036

- External work: τ-bench
- Work ID: P-WORK-029
- Year: 2024
- Mechanism name: pass^k reliability
- Original context: tool-agent-user interaction 中 repeated-trial consistency。
- Mechanism summary: 单次成功率不够，需要看多次重复下的稳定性。
- Supports which possible design area: Evaluation; Recommendation Policy
- Support type: Direct
- Reasoning bridge: RC 的 recommendation 也应看 consistency：同类 source state 下是否稳定、是否频繁摇摆。相似点是都关心 repeated-trial reliability；差异点是 RC 的 repeated-trial 单元可能是同一本书不同 run。
- Why not direct copy: pass^k 需要重定义为导航/推荐一致性。
- Complexity implication: 低
- What project evidence would still be needed: repeated-run harness on fixed source bundles
- Confidence: 中高
- Stable citation: <https://arxiv.org/abs/2406.12045>

## External Evidence Ledger

| Evidence ID | Work ID | Work | Year | Mechanism | Topic | Support Type | Reasoning Bridge Summary | Possible RC Design Area | Why Not Direct Copy | Complexity Cost | Confidence | Stable Citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-EXT-001 | 001 | ReAct | 2022 | reasoning-action interleave | agent loop | Direct | detour 像局部 source interaction loop | Detour Policy | 阅读不是连续工具任务 | 中 | 高 | arXiv 2210.03629 |
| P-EXT-002 | 001 | ReAct | 2022 | observation correction | grounding | Direct | 外部证据修正后续阅读决定 | Detour / Audit | 解释空间更开放 | 低 | 高 | arXiv 2210.03629 |
| P-EXT-003 | 001 | ReAct | 2022 | local-loop boundary | boundary | Boundary | 适合局部，不适合全局 planner | Planning Ontology | 会过度 stepwise | 中 | 中高 | arXiv 2210.03629 |
| P-EXT-004 | 002 | Plan-and-Solve | 2023 | explicit pre-plan | planning | Direct | 难段/章节边界先 sketch 再读 | Deep-dive / Orchestration | 每步先规划过重 | 中 | 高 | ACL 2023 |
| P-EXT-005 | 002 | Plan-and-Solve | 2023 | boundary planning | planning | Boundary | planning 应在复杂边界触发 | Navigation Policy | 不是主循环默认动作 | 低 | 高 | ACL 2023 |
| P-EXT-006 | 003 | ReWOO | 2023 | reasoning-observation decoupling | efficiency | Analogical | detour 可先列待核查点 | Detour / Memory | 阅读中途常需改计划 | 中 | 中高 | arXiv 2305.18323 |
| P-EXT-007 | 003 | ReWOO | 2023 | placeholder execution | orchestration | Analogical | pending concern 可先占位后回填 | Audit / Memory | slot 管理复杂 | 中 | 中 | arXiv 2305.18323 |
| P-EXT-008 | 004 | Reflexion | 2023 | episodic reflection buffer | reflection | Direct | 策略记忆应独立于内容记忆 | Memory Interface | 容易污染理解层 | 中 | 高 | arXiv 2303.11366 |
| P-EXT-009 | 004 | Reflexion | 2023 | feedback-to-language | reflection | Direct | navigation 失败原因要语言化 | Audit / Evaluation | hindsight bias | 中 | 高 | arXiv 2303.11366 |
| P-EXT-010 | 005 | ToT | 2023 | branch and backtrack | search | Analogical | hard passage 可比较少量路径 | Deep-dive Policy | 解释路径难打分 | 高 | 高 | arXiv 2305.10601 |
| P-EXT-011 | 005 | ToT | 2023 | cost warning | evaluation | Negative | 默认主循环不应重搜索 | Navigation Policy | 成本高延迟高 | 高 | 高 | arXiv 2305.10601 |
| P-EXT-012 | 007 | LATS | 2023 | MCTS + value + reflection | search | Analogical | 只应在极难场景触发 | Deep-dive Policy | 阅读缺稳定 reward | 很高 | 高 | arXiv 2310.04406 |
| P-EXT-013 | 008 | RAP | 2023 | world-model planning | search | Boundary | 说明何种任务才适合 world-model planning | Planning Ontology | 开放语义文本难形式化 | 很高 | 中高 | arXiv 2305.14992 |
| P-EXT-014 | 009 | HTN | 1996 | hierarchical decomposition | hierarchy | Direct | 阅读进程天然有层级结构 | Planning Ontology | 任务网络没那么显式 | 中 | 中高 | hdl.handle.net/1903/5810 |
| P-EXT-015 | 010 | Options | 1999 | temporal abstraction | hierarchy | Direct | 主线、detour、slow cycle 可视为 options | Navigation Policy | 终止条件难写 | 低 | 中高 | DOI 10.1016/S0004-3702(99)00052-1 |
| P-EXT-016 | 011 | MAXQ | 2000 | controller-worker separation | hierarchy | Analogical | Navigate 与 runner 可职责分离 | Orchestration | RL formalism 不可直搬 | 低 | 中 | DOI 10.1613/jair.639 |
| P-EXT-017 | 012 | LangGraph | 2024 | durable execution | orchestration | Direct | 长时程阅读会话需要可恢复 state | Orchestration / Audit | substrate != judgment | 中 | 高 | LangGraph docs |
| P-EXT-018 | 012 | LangGraph | 2024 | interrupts / review gates | orchestration | Direct | recommendation 展示可视为可中断 gate | Recommendation / Audit | 节点重启有语义要求 | 中 | 高 | LangGraph interrupts docs |
| P-EXT-019 | 013 | Agents SDK | 2025 | handoffs + guardrails | orchestration | Background | routing / approval / state 应分层 | Orchestration | 通用框架不能替设计 | 中 | 高 | OpenAI docs |
| P-EXT-020 | 013 | Trace grading | 2025 | trace-level grading | eval | Direct | 需要区分 planner/memory/retrieval 错因 | Audit / Evaluation | rubric 要重写 | 中 | 高 | OpenAI trace grading docs |
| P-EXT-021 | 014 | Information Foraging | 1999 | rate-of-gain | navigation | Direct | 下一步读哪里是 value/cost 问题 | Navigation Policy | 需加入主线连续性 | 低 | 高 | DOI 10.1037/0033-295X.106.4.643 |
| P-EXT-022 | 014 | Information Foraging | 1999 | information scent | navigation | Direct | unresolved concern 可形成跳转线索 | Recommendation Ranking | novelty 误导风险 | 低 | 中高 | DOI 10.1037/0033-295X.106.4.643 |
| P-EXT-023 | 015 | Exploratory Search | 2006 | finding to understanding | exploratory search | Analogical | 推荐阅读更像探索支架 | Recommendation Policy | 不是典型 search session | 低 | 中高 | CACM 2006 |
| P-EXT-024 | 017 | Adaptive Hypermedia | 2001 | user-model adaptation | adaptive nav | Analogical | internal nav 与 user-facing rec 应分层 | Recommendation Policy | 没有完整 learner model | 中 | 中高 | DOI 10.1023/A:1011143116306 |
| P-EXT-025 | 018 | ANS | 2003 | direct guidance / annotation | adaptive nav | Direct | recommendation 可弱提示而非命令 | User-facing Rationale | UI 单位不同 | 低 | 高 | DOI 10.1111/1467-8535.00345 |
| P-EXT-026 | 018 | ANS | 2003 | meta-adaptation | adaptive nav | Boundary | guidance 强度应因人因时而变 | Recommendation Policy | 适配面过多会复杂 | 低 | 高 | DOI 10.1111/1467-8535.00345 |
| P-EXT-027 | 019 | Course Sequencing | 2003 | prerequisite-aware sequence | path recommendation | Analogical | path 应体现依赖关系 | Recommendation Policy | RC 不是 mastery tutor | 中 | 中高 | DOI 10.1504/IJCEELL.2003.002154 |
| P-EXT-028 | 020 | Rereading effect | 2000 | rereading as calibration | reading | Direct | look-back 应服务校准 | Look-back Policy | 不是任何文本都该回看 | 低 | 高 | DOI 10.3758/BF03209348 |
| P-EXT-029 | 021 | Metacomprehension | 2007 | poor self-monitoring | reading | Direct | 不应盲信“我懂了”的即时感 | Look-back / Deep-dive | 不能以此否定用户 | 低 | 高 | DOI 10.1111/j.1467-8721.2007.00509.x |
| P-EXT-030 | 022 | Learner agency review | 2020 | agency-preserving rec | agency | Direct | 推荐应低打扰、可跳过 | Recommendation Policy | agency 量表需翻译 | 低 | 高 | DOI 10.1186/s41239-020-00219-w |
| P-EXT-031 | 023 | Open Learner Model | 2017 | visible state for SRL | agency | Analogical | 可见 rationale 帮助用户自调节 | User-facing Rationale | 需要稳定 model | 中 | 中高 | DOI 10.1007/s11257-016-9186-6 |
| P-EXT-032 | 024 | Tsai & Brusilovsky | 2021 | control + explanation | recommender UX | Direct | recommendation 既要可控又要可解释 | Recommendation / Evaluation | 控制项需简化 | 中 | 高 | DOI 10.1007/s11257-020-09281-5 |
| P-EXT-033 | 025 | McNee et al. | 2006 | beyond-accuracy | evaluation | Direct | usefulness > accuracy | Evaluation | 需重写指标 | 低 | 高 | DOI 10.1145/1125451.1125659 |
| P-EXT-034 | 026 | ResQue | 2011 | user-centric constructs | evaluation | Direct | 单独衡量 recommendation UX | Evaluation | 量表需本地化 | 低中 | 高 | DOI 10.1145/2043932.2043962 |
| P-EXT-035 | 028 | WebArena | 2023 | functional correctness | agent eval | Background | 强调长链路 recovery 与 grounding | Evaluation | 环境差异大 | 低 | 中高 | arXiv 2307.13854 |
| P-EXT-036 | 029 | τ-bench | 2024 | pass^k reliability | agent eval | Direct | recommendation 一致性需 repeated-run 指标 | Evaluation | pass^k需重定义 | 低 | 中高 | arXiv 2406.12045 |

## Synthesis and Relevance Preview

### Adopt / Adapt / Reject by Work

| Work ID | Work | Adopt | Adapt | Reject | Why |
| --- | --- | --- | --- | --- | --- |
| 001 | ReAct | 局部 action-observation grounding | detour loop | 全局阅读 planner | 强于局部纠偏，弱于长程阅读路线 |
| 002 | Plan-and-Solve | 边界式显式计划 | 章节/难段 plan sketch | 每步先规划 | 复杂处有益，默认处过重 |
| 003 | ReWOO | 计划与执行解耦思想 | pending concern / detour bundle | 冻结式全程计划 | 阅读中途常需改写 |
| 004 | Reflexion | strategy memory 分层 | slow-cycle reflection | 反思混入内容记忆 | 容易污染 source understanding |
| 005 | ToT | 小规模路径比较 | hard-passage deep-dive | 默认主循环搜索 | 成本与延迟过高 |
| 006 | GoT | thought aggregation 概念 | multi-path compare 仅限专题场景 | arbitrary graph runtime | 对主循环过度复杂化 |
| 007 | LATS | optional deliberate search | bounded expert mode | default MCTS loop | 缺稳定 reward/value |
| 008 | RAP | “何时适合 world model” 的边界感 | 少量可模拟 micro task | 语义阅读 world-model 主循环 | 开放文本太难形式化 |
| 009 | HTN | 层级分工原则 | 阅读层级语义化 | 直接任务网迁移 | 阅读不是标准 HTN domain |
| 010 | Options | temporal abstraction | mainline / detour / consolidation options | RL formalism 原样照搬 | 终止条件需改写 |
| 011 | MAXQ | controller-worker 分工 | Navigate vs runner | RL value decomposition | 工程借鉴即可 |
| 012 | LangGraph | checkpoint / interrupt / trace 思想 | 仅借 substrate 能力 | 为 graph 而 graph | runtime 不能替代判断 |
| 013 | Agents SDK / trace grading | handoff / guardrail / trace eval 分层 | 读写为 RC trace schema | 通用 SDK 当设计答案 | 只能给工程骨架 |
| 014 | Information Foraging | value/cost/scent heuristics | 加入 mainline continuity | 纯信息增益最大化 | 会鼓励 novelty chasing |
| 015 | Exploratory Search | “推荐阅读是理解支架” | 面向已有主 source 改造 | 当成通用搜索引擎 UX | 场景不同 |
| 016 | White & Roth | open-ended exploration framing | thematic path support | 完整 exploratory system | 过宽泛 |
| 017 | Adaptive Hypermedia | adaptation should be user-state-aware | RC-specific user state | 强 learner model 假设 | 证据不足 |
| 018 | ANS | 直接引导/注记/元适配 | recommendation surface | 强制导航 | agency 风险高 |
| 019 | Course Sequencing | prerequisite-aware path idea | thematic / deep-dive path | mastery curriculum | RC 不是 tutor |
| 020 | Rereading effect | 回看用于 calibration | 定义触发条件 | 默认重读 | 有成本 |
| 021 | Metacomprehension | 不盲信流畅感 | 校准触发器 | 否定用户判断 | 需要 agency 平衡 |
| 022 | Learner agency review | 低打扰、可跳过、目标保持 | recommendation UX | 强 paternalism | 与第二读者定位冲突 |
| 023 | Open Learner Model | 适度暴露 rationale | source-grounded partial visibility | 全量暴露内部规划 | 信息过载且不稳 |
| 024 | Tsai & Brusilovsky | controllability + explainability | 最小控制面 | 纯黑箱推荐 | 影响接受度 |
| 025 | McNee et al. | usefulness over accuracy | RC metrics set | accuracy-only eval | 指标失真 |
| 026 | ResQue | 用户中心评价构念 | RC-specific问卷与 rubric | 原量表直接照抄 | 语境不同 |
| 027 | AgentBench | 多维 benchmark 意识 | 失效归因拆分 | 直接作 RC benchmark | 动作空间不同 |
| 028 | WebArena | long-horizon correctness / recovery 意识 | 路径恢复评估 | 浏览器任务 benchmark 迁移 | 场景错位 |
| 029 | τ-bench | reliability / pass^k 意识 | repeated-run navigation consistency | 原指标直接套用 | 需重定义 |
| 030 | TEL recommenders | learning path ≠ top-N | RC path semantics | 直接采用教育平台模型 | 目标不同 |
| 031 | Knijnenburg UX | UX layers matter | RC recommendation experience eval | 只看后台指标 | 用户体验缺失 |
| 032 | Transparent/Scrutable user models | 可修正的 user-model 思路 | minimal scrutable rationale | 完整用户模型编辑器 | 过重 |

### Cross-work Synthesis

**Agent Planning 的主流范式**大致分为五类：交错式 reasoning+acting（ReAct）、显式 plan-then-execute（Plan-and-Solve / ReWOO）、reflection-based adaptation（Reflexion）、search-based deliberation（ToT / LATS / RAP / GoT）、以及 orchestration/runtime substrate（LangGraph / Agents SDK 等）。这些范式并不互斥，但它们解决的问题不同：有的解决局部 grounded action，有的解决长程搜索，有的解决恢复与审计，而不是同一个“planning 问题”。

**从 task planning 到 action selection / orchestration / reflection / search planning 的演进**，本质上是从“事先写一个计划”转向“在何处需要什么粒度的控制”。ReAct 强调在线纠偏，Plan-and-Solve 强调显式拆分，Reflexion 强调跨 episode 学习，ToT/LATS 强调在高难度局部进行探索，LangGraph/OpenAI 文档则强调状态保存、人工审批与 trace 归因。对 Reading Companion 而言，这意味着真正重要的不是“有没有 planner”，而是**哪些判断要在线、哪些要边界化、哪些要写入审计层**。

**哪些方法适合 long-horizon agent，哪些只适合局部 tool loop**：ReAct 与 ReWOO 更适合局部 source/tool detour；Plan-and-Solve 适合边界处的轻量预规划；Reflexion 适合跨轮策略修正；ToT / LATS / RAP 适合高难度、可承受高成本的可选 deep-dive；LangGraph/Agents SDK 适合工程上的长时程恢复、trace 与 review gates。把它们一股脑塞进默认阅读主循环，会把系统从“第二读者”推成“过度自治的 planner”。

**hierarchical planning 对 micro / meso / macro 控制最有解释力**。HTN、Options、MAXQ 共同指出：真正高效的长流程 agent，不是每步都重新搜索，而是把控制分成多时间尺度。借到 Reading Companion 里，最自然的不是 graph workflow 语言，而是把“下一 unit 怎么读”“何时 detour”“章末 consolidation”放在不同层，且不要求每层都由 LLM 控制。

**ReAct / planner-executor / ToT / LATS 的适用边界**很清楚：ReAct 适合 observation-rich local loop；planner-executor 适合复杂问题边界；ToT 适合 deliberate reasoning 且成本高；LATS 适合需要更强搜索与价值评估的任务，但前提是可操作的 value/reward 存在。对阅读主路来说，默认更像 information foraging；对难段解释或主题分歧，才可能升级为 search-based deep-dive。

**为什么 Information Foraging、主动阅读、adaptive navigation 比 AutoGPT-style planning 更贴近推荐阅读**：因为“下一步读哪里”首先是一个**价值—成本—线索—连续性**问题，而不是“完成任务”的动作组合问题。Information Foraging 讲的是跳不跳 patch，active reading / metacomprehension 讲的是何时回看与校准，adaptive navigation 讲的是如何给支架而不过度接管——这三类文献共同更贴近 Reading Companion 的本体。

**recommendation-as-planning 与普通 recommender system 的差别**在于：这里推荐的不是孤立 item，而是序列、依赖、时机、解释，以及“此刻不推荐”的克制。课程排序与 learning path 文献都说明，路径需要考虑 prerequisite、目标和先前状态；learner agency 与 controllability/explainability 文献则提醒，路径推荐不能变成替用户完成学习。

**planning / recommendation evaluation 的重心**正在从单一成功率或 accuracy，转向 usefulness、functional correctness、reliability、trace-based error attribution 与 user experience。McNee 等反对 accuracy-only；ResQue 与 recommender UX 文献扩展到 usefulness / satisfaction / behavioral intention；trace grading、WebArena、τ-bench 则把重复试验稳定性、轨迹错误归因与长链路恢复拉进评估核心。对 Reading Companion，这很接近未来的 `Navigation Groundedness`、`Mainline Continuity`、`Detour Precision`、`Recommendation Usefulness`、`Overplanning/Thrashing Rate`。

**对 Reading Companion 最相关的趋势**有三条。第一，控制分层而不是 agent 叠加：hierarchical control + bounded detours。第二，internal navigation 与 user-visible route disclosure 分层：agent 可内部判断，但对用户只给必要、低打扰、source-grounded 的建议。第三，trace-first evaluation：没有规划审计，就很难判断 planner、memory、retrieval 谁错。

**最容易诱导过度复杂化的趋势**也有三条。第一，把 search-based planning 误当默认先进方案。第二，把 graph workflow/multi-agent runtime 误当阅读判断本身。第三，把 learner modeling 做得过深，以至于 recommendation 变成 paternalistic tutor。就本轮证据看，这三条都更适合作为边界警告，而不是默认方向。

### Reading Companion Relevance Preview

| External pattern | Possible RC relevance | Needed project-side validation | Risk |
| --- | --- | --- | --- |
| ReAct | 支持 detour / source-skill loop | detour 是否已有 observation 回路 | 步步显式推理导致慢与吵 |
| Plan-and-Solve | 支持 chapter / hard-passage 边界规划 | 章节边界是否天然是 planning moment | overplanning |
| ReWOO | 支持 detour bundle / pending concern | 是否存在一次查多点需求 | 计划冻结过早 |
| Reflexion | 支持 slow-cycle strategy memory | 是否已有独立 strategy memory 层 | 反思污染文本理解 |
| ToT / LATS | 支持 optional deep-dive expert mode | hard passage 识别条件 | 成本和延迟失控 |
| HTN / Options | 支持 micro-meso-macro 分层 | 现有对象层级是否稳定 | 抽象太漂亮但落地过虚 |
| LangGraph / trace grading | 支持 audit / checkpoint / recovery | trace schema 是否足够细 | 为工程框架而框架化 |
| Information Foraging | 支持 reading value / cost / scent heuristic | 主线连续性 proxy 是否可定义 | novelty chasing |
| Active reading / metacomprehension | 支持 look-back / calibration policy | 何种不稳定信号值得回看 | 为回看而回看 |
| Adaptive navigation / agency | 支持 user-visible route disclosure surface | UI 是否支持拒绝/跳过/稍后 | 替用户读书 |
| Course sequencing / learning path | 支持 thematic path / carry-forward | source dependency graph 是否值得建 | tutor 化 |
| Beyond-accuracy evaluation | 支持 usefulness / agency / reliability 指标 | 是否能采集 repeated-run 与 UX 数据 | 只剩漂亮指标，不连项目现实 |

## Research Gaps & Citation Quality Audit

### Research Gaps

| Gap | Why it matters | Suggested next action |
| --- | --- | --- |
| ReAct / ReWOO / LATS 的全文尚未像 Plan-and-Solve 那样做逐节精读 | 关键失败模式与 ablation 还可再细化 | 下一轮只补读最相关章节：method、ablation、limitations |
| HCI 中 active reading 的系统支持文献还不够深 | 当前回看证据偏 metacomprehension / rereading，缺系统 interface 研究 | 深挖 annotation / reading support systems / shared reading support |
| Learning path recommendation 与非教学阅读的边界还需要更细证据 | 容易把 Reading Companion tutor 化 | 专门补一轮“非 mastery 型路径推荐”文献 |
| 现成 benchmark 没有直接覆盖 source-span reading navigation | 影响后续 Evaluation 设计 | 下一轮做 benchmark gap mapping，但仍不写项目决策 |
| Adaptive navigation 与 controllability 的 UI 具体形态证据不够 | 现在能说原则，不能说最优界面交互 | 补看 controllable recommender / scrutable model HCI 实验 |
| reflection memory 与 content memory 的分层虽然证据强，但落到 RC 是否匹配尚未知 | 直接影响慢周期与审计设计 | 下一轮 Evidence-to-Project Mapping 时对照 `memory state` 与 `audit trace` |
| orchestration substrate 是否需要迁移到 graph runtime 证据不足 | 防止为工程时髦而改造 | 下一轮只做“是否需要框架迁移”的轻诊断，不碰代码深改 |

### Citation Quality Audit

| Check | Result | Notes |
| --- | --- | --- |
| 是否没有输出 `turn...` 作为最终 citation？ | Partial | 正文未把 `turn...` 当稳定来源；但为了研究型回答的事实支撑，系统级网页引用仍以内嵌 citation 形式存在。所有 Work / Card 已同时给出稳定 URL |
| 是否为所有 Work Cards 添加年份？ | Pass |  |
| 是否为所有 Work Cards 添加 stable URL？ | Pass |  |
| Tier 1 工作是否至少覆盖 12 个？ | Pass | 实际给出 13 个 Tier 1 / direction cards |
| HCI / Reading / Recommendation / Learning Path 方向是否至少覆盖 8 个？ | Pass | Bibliography 中超过 12 个 |
| 每个 Work Card 是否有一手来源或明确标注二手？ | Pass |  |
| 每个 Evidence Card 是否有 reasoning bridge？ | Pass |  |
| 是否区分 Direct / Analogical / Negative / Boundary / Background support？ | Pass |  |
| 是否避免把项目内部假设写成外部事实？ | Pass | 仅做 relevance preview，不做 mapping |
| 是否过度依赖二手综述而非一手来源？ | Partial | 主体仍是一手论文/官方文档；少量 HCI 方向用了 review 或出版社摘要页 |
| 是否明确标注未深读来源？ | Pass |  |
| 是否没有输出项目设计决策 / Candidate Decision Ledger？ | Pass |  |
