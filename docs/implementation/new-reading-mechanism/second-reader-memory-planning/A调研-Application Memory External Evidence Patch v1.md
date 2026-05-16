# Application Memory External Evidence Patch v1

本补丁只补充**真实 Agent / assistant / coding agent / browser agent 产品的 memory 应用实现证据**，不进入 Second Reader 的正式项目设计、Candidate Decision Ledger、Memory Ontology 正文或 Codex 实施路线。为保证边界清晰，我本轮只读取了项目的 README、current-state 与上一轮外部证据包来做约束校准，没有读取 Second Reader GitHub 代码；当前项目仍以**source-grounded、可解释、可审计、文件优先**的 reading state 为约束。

**Usage Note for route disclosure.** Evidence about user-visible memory management or source disclosure may inform future route-disclosure UX, but it does not justify user route choice, route preference memory, or recommendation-driven navigation in Second Reader.

## 研究范围与来源质量

### Research Scope & Source Quality

本轮深读的高置信来源，主要来自官方 Help Center、官方开发者文档、官方产品/技术博客，以及少量官方开源文档站点。高置信覆盖已包括：ChatGPT / OpenAI、Claude / Anthropic、Claude Code、Gemini Apps、Gemini CLI、Microsoft 365 Copilot、Perplexity / Comet、Hermes Agent、Clawdbot / OpenClaw。整体上，最成熟的公开产品范式已经足够清晰：**saved memory、past chat reference、project/workspace memory、session summary、file memory、session archive search、temporary/incognito、admin controls** 已经形成稳定分层。

本轮没有读取 Second Reader GitHub 代码；只把仓库 README / current-state 和上一轮《Memory External Evidence Pack v1》当作**筛选约束**，原因是本轮目标是“外部应用实现证据补丁”，不是内部实现诊断。正式的 Evidence-to-Project Mapping 留到下一轮。

来源分层如下。

- 一手官方产品/开发者文档：OpenAI、Anthropic、Google、Microsoft、Perplexity、Comet、Claude Code、Gemini CLI、OpenClaw / Clawdbot、Hermes 官方页面。
- 开源/本地应用文档：Claude Code、Gemini CLI、OpenClaw / Clawd.bot、Hermes。
- 官方博客 / 技术说明：OpenAI memory blog、Hermes memory/skills/learning-loop 系列。
- 新闻/rollout confirmation：本轮只轻用，核心结论尽量不依赖新闻。
- 第三方 reverse-engineering / cautionary analysis：Manthan Gupta 系列被保留为**高价值线索、reverse-engineering、cautionary analysis**，不是官方事实；由于本轮在官方材料上已获得足够高置信骨架，而 token 预算又被系统强制截断，Manthan 五篇未能都做到逐篇深读，因此本报告里将它们明确标为 **secondary / not read, listed for future** 或 **secondary only**，并放入研究缺口。

### 实际深读 / 部分深读 / 未深读清单

| 类别 | 状态 | 覆盖内容 |
| --- | --- | --- |
| 官方产品文档 | deep-read | OpenAI memory help / FAQ / Temporary Chat / release notes；Claude chat search & memory / incognito / import-export / projects / RAG；Gemini saved info / past chats / temp chat / privacy；Copilot memory / personalization / history / admin control；Perplexity memory / enterprise memory / Comet memory；Claude Code memory；Gemini CLI memory；OpenClaw / Clawd.bot memory docs |
| 官方博客 / 技术页 | deep-read / partial-read | OpenAI memory product blog；Hermes memory / skills / learning-loop / persistent-memory 官方页 |
| 开源应用/agent docs | deep-read | Claude Code、Gemini CLI、OpenClaw / Clawd.bot |
| 第三方 reverse-engineering | not read, listed for future / secondary only | Manthan Gupta 五篇指定文章 |
| 新闻 / rollout | skimmed | 极少量，仅用于补充可用性语境；核心判断不依赖 |

### 置信等级总览

| 层级 | 置信等级 | 说明 |
| --- | --- | --- |
| 官方 help / docs / developer docs | High | 本轮主干证据 |
| 官方 blog / release notes | High-Medium | 对 rollout、定位、功能边界很重要；对底层 prompt assembly 仍不透明 |
| 官方开源 docs 站点 | Medium-High | 对 file-based memory、workspace memory、memory command、local state 很有价值 |
| 第三方 reverse-engineering | Medium-Low | 可提供机制线索，但不能当官方实现事实 |
| 新闻 / 社媒 / 论坛 | Low | 仅用作 rollout 或风险线索，不作为设计主依据 |

## 应用规范书目

### Application Canonical Bibliography

> 说明：Stable URL 一列使用稳定链接；Official / Secondary 明确标识是否为官方；“Read Status / Maturity / Evidence Type”按你要求保留英文受控值。
> 由于篇幅原因，表中 Why included 与 Relevance 采用短句；后文 Work Cards 与 Evidence Cards 再展开。

| Work ID | Tier | Product / System | Canonical Title | Authors / Organization | Year / First Posted / Last Updated | Source Type | Evidence Type | Stable URL | Official / Secondary | Read Status | Maturity | Confidence | Why included | Relevance to Reading Companion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| APP-WORK-001 | Tier 1 | ChatGPT / OpenAI | What is Memory? | OpenAI | 2025; updated 2026-04 | Help Center | Official stated behavior | <https://help.openai.com/en/articles/8983136-what-is-memory> | Official | deep-read | Official product docs | High | Saved memory vs chat history 总说明 | 账户级 memory 的主样本 |
| APP-WORK-002 | Tier 1 | ChatGPT / OpenAI | How does “Reference saved memories” work? | OpenAI | 2025; updated 2026-04 | Help Center | Official stated behavior | <https://help.openai.com/en/articles/11146739-how-does-reference-saved-memories-work> | Official | deep-read | Official product docs | High | Saved memories 细则 | durable memory 与删除边界 |
| APP-WORK-003 | Tier 1 | ChatGPT / OpenAI | Memory FAQ | OpenAI | 2025; updated 2025 | Help Center | Official stated behavior | <https://help.openai.com/en/articles/8590148-memory-faq> | Official | deep-read | Official product docs | High | chat history、storage、deletion | dynamic summary / recall 边界 |
| APP-WORK-004 | Tier 1 | ChatGPT / OpenAI | Temporary Chat FAQ | OpenAI | 2025; updated 2026-05 | Help Center | Official stated behavior | <https://help.openai.com/en/articles/8914046-temporary-chat-faq> | Official | deep-read | Official product docs | High | no-memory mode | reading session 隔离模式的重要先例 |
| APP-WORK-005 | Tier 1 | ChatGPT / OpenAI | Memory and new controls for ChatGPT | OpenAI | 2024; updated 2025 | Product blog | Official stated behavior | <https://openai.com/index/memory-and-new-controls-for-chatgpt> | Official | partial-read | Official blog / technical report | High | rollout + control narrative | 产品化 memory 的治理税 |
| APP-WORK-006 | Tier 1 | ChatGPT / OpenAI | ChatGPT — Release Notes | OpenAI | updated 2026-05 | Release notes | Official stated behavior | <https://help.openai.com/en/articles/6825453-chatgpt-release-notes> | Official | partial-read | Official product docs | High | 2026 Memory Sources UI | memory source disclosure 关键证据 |
| APP-WORK-007 | Tier 1 | Claude / Anthropic | Release Notes | Anthropic | updated 2026 | Help Center | News / rollout confirmation | <https://support.claude.com/en/articles/12138966-release-notes> | Official | partial-read | Official product docs | High | 记忆 rollout 时间线 | availability / rollout 语境 |
| APP-WORK-008 | Tier 1 | Claude / Anthropic | Use Claude’s chat search and memory to build on previous context | Anthropic | 2026-03-16 | Help Center | Official stated behavior | <https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context> | Official | deep-read | Official product docs | High | chat search + memory summary 主文档 | on-demand retrieval 与 summary 并存 |
| APP-WORK-009 | Tier 1 | Claude / Anthropic | Using incognito chats | Anthropic | 2026-04-09 | Help Center | Official stated behavior | <https://support.claude.com/en/articles/12260368-using-incognito-chats> | Official | deep-read | Official product docs | High | incognito 行为/保留/导出 | no-memory / retention 边界 |
| APP-WORK-010 | Tier 1 | Claude / Anthropic | Import and export your memory from Claude | Anthropic | 2026-03-16 | Help Center | Official stated behavior | <https://support.claude.com/en/articles/12123587-import-and-export-your-memory-from-claude> | Official | deep-read | Official product docs | High | import/export | memory portability / user control |
| APP-WORK-011 | Tier 1 | Claude / Anthropic | Understanding Claude’s personalization features | Anthropic | updated 2026 | Help Center | Official stated behavior | <https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features> | Official | deep-read | Official product docs | High | account-wide vs project instructions | instruction 与 memory 分层 |
| APP-WORK-012 | Tier 1 | Claude Projects | What are projects? | Anthropic | 2026-03-16 | Help Center | Official stated behavior | <https://support.claude.com/en/articles/9517075-what-are-projects> | Official | deep-read | Official product docs | High | project-scoped workspace | book/project scoped memory 类比 |
| APP-WORK-013 | Tier 1 | Claude Projects | Retrieval augmented generation for projects | Anthropic | 2026-03-16 | Help Center | Official stated behavior | <https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects> | Official | deep-read | Official product docs | High | project knowledge retrieval | project memory ≠ global user memory |
| APP-WORK-014 | Tier 1 | Claude Code | How Claude remembers your project | Anthropic | updated 2026 | Developer docs | Official developer-facing mechanism | <https://docs.anthropic.com/en/docs/claude-code/memory> | Official | deep-read | Official framework docs | High | CLAUDE.md、auto memory、/memory | file memory / auditable memory 样板 |
| APP-WORK-015 | Tier 1 | Gemini Apps | Save info and reference past chats in Gemini Apps | Google | updated 2026 | Help Center | Official stated behavior | <https://support.google.com/gemini/answer/15637730> | Official | deep-read | Official product docs | High | saved info 与 past chats | user-editable explicit state |
| APP-WORK-016 | Tier 1 | Gemini Apps | Find & manage your recent chats in Gemini Apps | Google | updated 2026 | Help Center | Official stated behavior | <https://support.google.com/gemini/answer/13666746> | Official | deep-read | Official product docs | High | previous chats label / delete | memory source disclosure |
| APP-WORK-017 | Tier 1 | Gemini Apps | Use Gemini Apps | Google | updated 2026 | Help Center | Official stated behavior | <https://support.google.com/gemini/answer/13275745> | Official | deep-read | Official product docs | High | temporary chat | no-memory reading mode 类比 |
| APP-WORK-018 | Tier 1 | Gemini Apps | Gemini Apps Privacy Hub | Google | updated 2025 | Help Center | Official stated behavior | <https://support.google.com/gemini/answer/13594961> | Official | partial-read | Official product docs | High | retention / Keep Activity | privacy / activity coupling |
| APP-WORK-019 | Tier 1 | Gemini CLI | Memory Tool (`save_memory`) | Google Gemini CLI | updated 2026 | Developer docs | Official developer-facing mechanism | <https://google-gemini.github.io/gemini-cli/docs/tools/memory.html> | Official | deep-read | Official framework docs | High | save_memory → GEMINI.md | lightweight file memory |
| APP-WORK-020 | Tier 1 | Gemini CLI | Provide Context with GEMINI.md Files | Google Gemini CLI | updated 2026 | Developer docs | Official developer-facing mechanism | <https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html> | Official | deep-read | Official framework docs | High | hierarchical context / /memory | file-based memory + inspectability |
| APP-WORK-021 | Tier 1 | Microsoft 365 Copilot | Manage Copilot Memory in Microsoft 365 Copilot | Microsoft | updated 2026-02 | Support | Official stated behavior | <https://support.microsoft.com/en-au/topic/manage-copilot-memory-in-microsoft-365-copilot-b3231eae-9e60-4b3c-ac58-81fddbe56279> | Official | deep-read | Official product docs | High | saved memories 管理 | manageability / deletion tax |
| APP-WORK-022 | Tier 1 | Microsoft 365 Copilot | Personalize what Microsoft 365 Copilot remembers | Microsoft | updated 2026-02 | Support | Official stated behavior | <https://support.microsoft.com/en-au/topic/personalize-what-microsoft-365-copilot-remembers-cba7b79a-c46f-4ca7-b46e-2fa22c563f90> | Official | deep-read | Official product docs | High | saved memory / chat history / temp chat | memory ontology 分层样板 |
| APP-WORK-023 | Tier 1 | Microsoft 365 Copilot | Revisit your Microsoft 365 Copilot Chat history | Microsoft | updated 2026-01 | Support | Official stated behavior | <https://support.microsoft.com/en-us/topic/revisit-your-microsoft-365-copilot-chat-history-6ea899e3-3bb1-450a-a2ae-220341ac193a> | Official | deep-read | Official product docs | High | chat history inference deletion | 30-day purge 重要边界 |
| APP-WORK-024 | Tier 1 | Microsoft 365 Copilot | Copilot personalization and memory | Microsoft | 2025-11 | Learn | Official stated behavior | <https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-personalization-memory> | Official | partial-read | Official product docs | Medium-High | storage / retention / enterprise | governance 与 compliance 边界 |
| APP-WORK-025 | Tier 1 | Microsoft 365 Copilot | Enhanced personalization control overview | Microsoft Graph / Learn | 2025-06 | Learn | Official developer-facing mechanism | <https://learn.microsoft.com/en-us/graph/control-enhanced-personalization-privacy> | Official | partial-read | Official framework docs | Medium-High | admin toggle / tenant control | enterprise boundary |
| APP-WORK-026 | Tier 1 | Perplexity | Memory | Perplexity | updated 2026 | Help Center | Official stated behavior | <https://www.perplexity.ai/help-center/en/articles/10968016-memory> | Official | deep-read | Official product docs | High | memories vs search history | search-oriented personalization 主样本 |
| APP-WORK-027 | Tier 1 | Perplexity Enterprise | Memory for Enterprise Organizations | Perplexity | updated 2026 | Help Center | Official stated behavior | <https://www.perplexity.ai/help-center/en/articles/13654357-memory-for-enterprise-organizations> | Official | deep-read | Official product docs | High | enterprise controls / data ownership | admin / ownership boundary |
| APP-WORK-028 | Tier 1 | Comet | Comet memory | Perplexity / Comet | 2026-03-04 | Help Center | Official stated behavior | <https://comet-help.perplexity.ai/en/articles/12658438-comet-memory> | Official | deep-read | Official product docs | High | browser memory 与 account memory | search history vs agent action boundary |
| APP-WORK-029 | Tier 2 | Comet | Getting Started with Comet | Perplexity | updated 2026 | Help Center | Official stated behavior | <https://www.perplexity.ai/help-center/en/articles/11172798-getting-started-with-comet> | Official | partial-read | Official product docs | Medium | Personal Search 定位 | browser memory 的边界样本 |
| APP-WORK-030 | Tier 2 | Perplexity | Incognito Mode Troubleshooting | Perplexity | updated 2026 | Help Center | Official stated behavior | <https://www.perplexity.ai/help-center/en/articles/12639758-incognito-mode-troubleshooting> | Official | partial-read | Official product docs | Medium | incognito thread 行为 | no-memory 模式参考 |
| APP-WORK-031 | Tier 1 | Hermes Agent | Persistent Memory — The Feature That Makes Hermes Different | Hermes Agent / Nous Research | updated 2026 | Product page | Official stated behavior | <https://hermes-agent.ai/features/persistent-memory> | Official | deep-read | Official blog / technical report | Medium-High | 3-layer memory 官方叙述 | hot/cold memory 分层 |
| APP-WORK-032 | Tier 1 | Hermes Agent | Inside Hermes’ Three-Layer Memory | Hermes Agent / Nous Research | 2026-04-04 | Technical blog | Official developer-facing mechanism | <https://hermes-agent.ai/blog/hermes-agent-memory-system> | Official | deep-read | Official blog / technical report | Medium-High | MEMORY.md / USER.md / skills / FTS5 | 最接近“应用实现剖面”的官方材料 |
| APP-WORK-033 | Tier 1 | Hermes Agent | Mastering Hermes Skills | Hermes Agent / Nous Research | 2026-04-04 | Technical blog | Official developer-facing mechanism | <https://hermes-agent.ai/blog/hermes-agent-skills-guide> | Official | deep-read | Official blog / technical report | Medium-High | skills as procedural memory | procedural memory 边界 |
| APP-WORK-034 | Tier 1 | Hermes Agent | Learning Loop — Self-Improving AI Skills | Hermes Agent / Nous Research | updated 2026 | Product page | Official stated behavior | <https://hermes-agent.ai/features/learning-loop> | Official | deep-read | Official blog / technical report | Medium | checkpoint → skill patch | settlement / post-run distillation 类比 |
| APP-WORK-035 | Tier 1 | Clawdbot | Memory | Clawdbot Docs | updated 2026 | Docs | Open-source docs | <https://docs.clawd.bot/concepts/memory> | Official-ish docs | deep-read | Official framework docs | Medium-High | daily log / MEMORY.md / pre-compaction | file-first / pre-compaction 样板 |
| APP-WORK-036 | Tier 1 | OpenClaw | Memory overview | OpenClaw Docs | updated 2026 | Docs | Open-source docs | <https://docs.openclaw.ai/concepts/memory> | Official-ish docs | deep-read | Official framework docs | Medium-High | DM-only MEMORY.md / daily notes | workspace memory / local ownership |
| APP-WORK-037 | Tier 2 | ChatGPT | How ChatGPT Memory Works | Manthan Gupta | 2025 | Blog post | Reverse-engineered / inferred | <https://manthanguptaa.in/posts/chatgpt_memory/> | Secondary | not read, listed for future | Secondary / background only | Low | reverse-engineering 线索 | 仅可作验证清单 |
| APP-WORK-038 | Tier 2 | Claude | Claude Memory | Manthan Gupta | 2025 | Blog post | Reverse-engineered / inferred | <https://manthanguptaa.in/posts/claude_memory/> | Secondary | not read, listed for future | Secondary / background only | Low | reverse-engineering 线索 | 仅可作验证清单 |
| APP-WORK-039 | Tier 2 | Hermes Agent | Hermes Memory | Manthan Gupta | 2025 | Blog post | Reverse-engineered / inferred | <https://manthanguptaa.in/posts/hermes_memory/> | Secondary | not read, listed for future | Secondary / background only | Low | 机制线索 | 需与官方页核验 |
| APP-WORK-040 | Tier 2 | Clawdbot / OpenClaw | Clawdbot Memory | Manthan Gupta | 2025 | Blog post | Reverse-engineered / inferred | <https://manthanguptaa.in/posts/clawdbot_memory/> | Secondary | not read, listed for future | Secondary / background only | Low | 命名与实现线索 | 需做命名消歧 |
| APP-WORK-041 | Tier 1 | Negative evidence | Memory Is Probably Hurting Your AI Product | Manthan Gupta | 2025 | Blog post | Opinion / cautionary analysis | <https://manthanguptaa.in/posts/memory_is_a_mistake/> | Secondary | not read, listed for future | Secondary / background only | Low | 反向边界论证 | product tax / anti-pattern 提醒 |

## 应用实现地图与综合结论

### Application Memory Field Map

| Area | Core question | Representative products / sources | Why it matters | Risk if copied blindly |
| --- | --- | --- | --- | --- |
| Saved Memory | 哪些信息被当作“长期应记住”？ | ChatGPT、Gemini Saved Info、Copilot saved memories、Perplexity Memories | durable explicit state 的主形态 | 容易滑向用户画像，而不是任务记忆 |
| Chat History / Past Chat Reference | 不进入 saved memory 的历史如何复用？ | ChatGPT chat history、Claude chat search、Gemini previous chats、Copilot chat history | 区分 always-on durable state 与动态历史回溯 | 把历史摘要错当“事实源” |
| Project / Workspace Memory | memory 是否按项目/工作区隔离？ | Claude Projects、Claude Code、OpenClaw、Clawdbot、Gemini CLI | 对 RC 更像“book / reading-run scoped state” | 如果做成全账号人格化，污染来源边界 |
| Session Summary / Recent Conversation Summary | 会话结束后是否压缩出 summary？ | Claude memory summary、Copilot inferred details、Hermes compression / skill distillation | 解释“压缩后仍可跨会话续接” | 摘要可能丢失 source-grounding |
| Always-injected Prompt Memory | memory 是否总进 prompt？ | ChatGPT saved memories、Claude memory summary、Hermes MEMORY.md/USER.md、Claude Code CLAUDE.md/GEMINI.md | hot memory 的典型做法 | prompt 膨胀、污染当前阅读判断 |
| On-demand Retrieval / Chat Search | 何时只在需要时检索？ | Claude chat search tool calls、Perplexity memory+history、Hermes FTS5、OpenClaw hybrid search docs text | cold archive 更适合可审计回调 | 如果强行 always inject，会带来 FVI 风险 |
| File-based Memory | memory 是否就是文件？ | Claude Code CLAUDE.md、Gemini CLI GEMINI.md、Hermes MEMORY.md / USER.md、OpenClaw MEMORY.md | 最贴近 RC 的 JSON / JSONL / Markdown 审计需求 | 文件碎片化、规则冲突、载入顺序复杂化 |
| Daily Logs / Handoff Memory | 是否区分 append-only 日志与整理记忆？ | OpenClaw / Clawdbot daily log + MEMORY.md、Hermes session DB + file memory | 很像 reading-run trace vs curated state | 如果不分层，日志会淹没 durable state |
| SQLite / Session Archive / FTS Recall | 完整历史如何留冷存档？ | Hermes state.db + FTS5、Claude search past chats、Perplexity search history | “热状态小，冷历史大” 的应用证据 | 会诱导过早引入复杂数据库 |
| Pre-compaction Memory Flush | compaction 前是否提醒写入 durable memory？ | Clawdbot/OpenClaw pre-compaction ping；Hermes self-eval checkpoint 属类比证据 | 对 reading-run settlement 很有类比价值 | 如果 flush 无 source audit，会写入噪声 |
| Explicit Remember / Forget Commands | 用户能否显式写入/删除？ | ChatGPT、Gemini、Claude Code /memory、OpenClaw “remember this” | 人机共管 memory 的最低可用面 | 让“remember” 变成任意 persistent side effect |
| Automatic Inference / Summary Generation | 系统会不会自己推断？ | ChatGPT automatic save、Claude 24h synthesis、Copilot inferred chat history、Perplexity generated memories | 解释为什么 mature product 都有 inferred layer | 推断层最容易制造不可解释误记 |
| User-visible Memory Management | 用户能否看/改/删？ | ChatGPT Manage Memories、Claude View and edit memory、Gemini Saved info、Copilot manage memory、Perplexity Manage Memories | 可解释性与 debug 基线 | 没有 UI/CLI 管理就会造成 system tax 暗债 |
| Temporary / Incognito / No-memory Mode | 是否有私密/临时模式？ | ChatGPT Temporary Chat、Claude incognito、Gemini temporary chat、Perplexity incognito、Copilot temporary chat | 对“本次阅读不要记住”非常关键 | 没有隔离，就会污染长期 reading state |
| Memory Source Disclosure | 回答是否标注用了哪些 memory？ | ChatGPT Memory Sources、Gemini “Previous chats”/“Your saved info”、Perplexity cited memories、Claude past chat citations | RC 最需要的是“这条状态从哪来” | 若只显示“用了 memory”而不显示来源，仍不够 |
| Admin / Enterprise Controls | 管理员能否关、能否继承策略？ | Copilot enhanced personalization、Perplexity Enterprise、Claude Enterprise owner controls、Claude Code managed policy | 展示 memory 的治理成本 | RC 现阶段不应过早引入 tenant-grade 重治理 |
| Privacy / Retention / Deletion | 删除后多久真正失效？ | ChatGPT 30 天、Claude 24h update / export、Copilot 30 天、Perplexity 30 天 deletion log、Gemini 72h temporary retention | 说明 memory 不是“写个 JSON”这么简单 | retention 语义若不清楚，会伤审计可信度 |
| Sensitive Memory Filtering | 是否主动避免敏感信息？ | OpenAI、Perplexity、Copilot docs、Hermes memory scan | 对 source-grounded 项目同样 relevant | 误以为“全记住”更先进会踩隐私雷 |
| Skills / Procedural Memory | “怎么做” 是否与 “记了什么” 分开？ | Hermes Skills、Claude Code rules/skills distinction、Gemini CLI project context | 非常适合 RC 中把 procedure 与 reading state 分层 | 如果混写，procedure 会污染 semantic state |
| Search History / Personal Search | 搜索历史是不是 memory？ | Perplexity、Comet、Gemini previous chats | 对 RC 是边界证据：history ≠ reading memory | 容易把 retrieval history 冒充理解状态 |
| Product Tax / Memory Anti-patterns | 记忆有没有系统税？ | 所有成熟产品都带 pause/delete/incognito/admin/export/retention 机制 | 反证“memory 不是免费功能” | 过早上 memory 会拉高维护税 |
| Application Fit vs RC Fit | 哪些机制直接 relevant？ | project/workspace/file memory / disclosure / temp mode / handoff memory | 帮下一轮 mapping | 防止把通用个性化误套到阅读任务 |

### Cross-product Synthesis

**主流产品范式**已经很清楚了：

- 第一类是 **account-wide personalization**，代表是 ChatGPT saved memories、Gemini Saved info、Copilot saved memories、Perplexity memories。
- 第二类是 **past chats / history reference**，代表是 ChatGPT chat history、Claude chat search、Gemini previous chats、Copilot chat history、Perplexity search history。
- 第三类是 **project/workspace memory**，代表是 Claude Projects、Claude Code、Gemini CLI、OpenClaw / Clawdbot、Hermes。
- 第四类是 **procedural memory / skills**，代表是 Hermes Skills、Claude Code path-scoped rules、Gemini CLI hierarchical GEMINI.md。
- 第五类是 **temporary / incognito / no-memory mode**，全部成熟产品都在补。

**saved memories、chat history、project memory、workspace memory、session summaries、episodic search** 各自解决的问题并不相同。saved memory 解决“以后总要带着的偏好/事实”；chat history 解决“以前聊过但未必值得永久保存”；project/workspace memory 解决“这个项目成立域内的持续上下文”；session summary 解决“长对话压缩后的跨会话续接”；episodic search 解决“需要时从完整历史里回找证据”。把这些层混成一个“memory”概念，是很多产品误解的起点。

**always-injected memory** 主要出现在 ChatGPT saved memory、Claude memory summary、Hermes MEMORY.md/USER.md、Claude Code CLAUDE.md、Gemini CLI GEMINI.md 这类“冷启动就要带入的设置/长期事实”。**on-demand retrieval** 则清楚出现在 Claude chat search、Perplexity memory + search history、Hermes SQLite FTS5、Claude Projects RAG。**periodic summary** 的标志性样本是 Claude 的 memory summary，每 24 小时更新一次；Copilot 则更强调 inferred details from chat history；Hermes 更像自评 checkpoint + procedural distillation，而不是单一 summary。

对 Reading Companion 来看，**project/workspace-scoped memory 普遍比 account-wide personalization 更贴近问题结构**。Claude Projects、Claude Code、Gemini CLI、OpenClaw / Clawdbot、Hermes 都说明：如果任务是围绕某个工程、仓库、workspace、agent workspace 展开，那么 memory 的最自然边界不是“这个用户是谁”，而是“这个工作对象是什么”。这与“book / reading-run / accepted source units / source-grounded state”的结构更接近。相反，ChatGPT / Gemini / Perplexity 这类跨会话个性化，虽然产品上有用，但很容易把阅读状态滑成用户画像。

**file-based memory / Markdown memory / GEMINI.md / CLAUDE.md / MEMORY.md / daily logs** 给出的最强信号，不是“Markdown 比数据库更先进”，而是：**应用层可审计 state 可以先做成简单、可见、用户可编辑、可导出的磁盘事实源**。Claude Code、Gemini CLI、OpenClaw / Clawdbot、Hermes 都明确展示了这一点；而且它们同时展示出另一个现实：文件 memory 仍然需要层级规则、加载顺序、体积控制、冲突处理和显式管理命令，所以“文件化”只是降低基础设施复杂度，不是消灭复杂度。

**pre-compaction memory flush / handoff memory** 的应用证据里，最直接的是 Clawdbot / OpenClaw：在自动 compaction 前会触发 silent, agentic turn，提醒模型把 durable memory 写到磁盘。Hermes 虽然没有相同措辞，但其“every 15 tool calls 自评 checkpoint → 决定是否写 memory / create or patch skill”的机制，提供了同类生命周期钩子。这对 Reading Companion 的类比价值不在于“也要 compaction”，而在于：**长会话在被压缩、切段、settle 之前，应该有明确的状态沉淀关口。**

**用户可见的 memory management、Temporary Chat、Incognito、delete / pause / export** 已经形成成熟产品共识。ChatGPT 有 Manage Memories 与 Temporary Chat；Claude 有 View and edit memory、pause / reset、incognito、import/export；Gemini 有 Saved info 与 temporary chat；Copilot 有 memory 管理、chat history toggle、temporary chat；Perplexity / Comet 有 memory/search-history 分开开关与 incognito。成熟产品几乎没有一个敢把 memory 做成不可见、不可删、不可停。这个事实本身就是“memory 是产品与系统税”的外部证据。

**memory source disclosure** 仍是非常值得借鉴的少数成熟做法。ChatGPT 2026-05 的 release notes 说开始推出 Memory Sources，能看到 saved memories、past chats、custom instructions，部分计划还会显示 files 与 connected Gmail。Gemini 当 past chats 或 saved info 被引用时，会在 Sources and related content 下显示 “Previous chats” 或 “Your saved info”。Claude 在引用 previous conversations 时会给 past chat citations。Perplexity 也明确说，使用 memory 或 history 时会在答案里引用相关来源。对 Reading Companion 来说，这类 disclosure 价值明显高于“系统自己偷偷个性化”。

**企业产品的 admin / retention / compliance controls** 给出的更像边界启发，而不是直接方案。Copilot 的 Exchange hidden folder、tenant enhanced personalization、Purview / Graph 控制；Claude Enterprise 的 owner controls、retention/export；Perplexity Enterprise 的 org-owned memory、admin permissions，都说明一旦 memory 进入组织边界，问题立刻从“记不记”上升为“谁拥有、谁能关、删了多久生效、是否可导出、是否纳入审计”。这些启发对 RC 的价值主要是：**别太早上企业级治理结构；先把 source refs 与 state audit 做实。**

## Tier 1 Work Cards

### Work Card: ChatGPT / OpenAI

- Work ID: APP-WORK-001–006
- Source links: 见 APP-WORK-001–006
- Authors / Organization: OpenAI
- Year / First Posted / Last Updated: 2024–2026
- Source Type: Help Center + Product blog + Release notes
- Evidence Type: Official stated behavior
- Read status: deep-read / partial-read
- Maturity: Official product docs / Official blog / technical report
- Confidence: High
- Original product problem: 跨会话个性化，让通用助手减少重复提问。
- Target user / system setting: consumer / prosumer 通用助手。
- Memory ontology: saved memories、chat history、custom instructions、temporary chat。
- Memory representation: saved memory 类 notepad；chat-history-derived dynamic details；memory sources UI。
- Memory formation: explicit “remember”；也会 automatic save。
- Memory management / lifecycle: Manage Memories；可 delete specific / clear all；saved memory 与 originating chat 必须双删才算彻底去除；chat-history-derived details 关闭后 30 天删除。
- Memory retrieval / injection: saved memories 为 always considered；chat history 为 dynamic reference；2026 起开始显示 sources。
- Context engineering: broad personalization，且会在搜索查询中使用 memory。
- User controls: ask what it remembers、delete、turn off、Temporary Chat。
- Privacy / retention / deletion: Temporary Chat 不创建或使用 memories；saved memory 与 chat history 分开保留；删 chat 不等于删 saved memory。
- Audit / observability: 2026-05 的 Memory Sources 是最重要进展，但官方仍未公开 prompt layering 细节。
- Evaluation evidence, if any: 无公开 benchmark；主要是产品行为说明。
- Key mechanisms: saved durable memory vs dynamic history；temporary mode；source disclosure。
- What it directly supports: durable state 与 dynamic history 必须分层；用户必须能管理。
- What it only analogically supports: broad personalization。
- What it argues against: 把 user profile memory 误当 reading memory。
- Fit to Reading Companion: **中等偏低直连，高边界价值**。最有价值的是“durable vs dynamic”分层、delete/temporary/source disclosure，不是其用户个性化本身。
- Misfit / limitation: 其主目标是 personalization，不是 source-grounded reading state。
- Complexity implication: 一旦做 account-wide memory，必须补齐 delete / reset / temporary / disclosure / retention。
- Candidate project-relevant implications: durable memory 与 session/history summary 应明确分开；no-memory reading run 是合理需求。
- Evidence strength: 强。

### Work Card: Claude / Anthropic

- Work ID: APP-WORK-007–013
- Source links: 见 APP-WORK-007–013
- Authors / Organization: Anthropic
- Year / First Posted / Last Updated: 2025–2026
- Source Type: Help Center + Release notes
- Evidence Type: Official stated behavior
- Read status: deep-read
- Maturity: Official product docs
- Confidence: High
- Original product problem: 让 Claude 成为“knowledgeable collaborator”，既能搜旧聊天，也能生成 memory summary，并按 project 隔离。
- Target user / system setting: personal + team + enterprise。
- Memory ontology: chat search、memory summary、project memory、project summary、project instructions、incognito。
- Memory representation: generated synthesis + project-specific memory space。
- Memory formation: search on demand；memory synthesis 每 24 小时更新；聊天中也能直接要求 Claude update memory summary。
- Memory management / lifecycle: pause memory、reset memory、delete chats affects synthesis、memory exports。
- Memory retrieval / injection: chat search 是 tool-call RAG；memory summary 为每个 standalone conversation 提供上下文；project chats 的 search confined to project。
- Context engineering: 明确把 on-demand past-chat retrieval 与 always-available memory summary 区分开。
- User controls: view/edit memory、toggle search and memory、incognito、import/export。
- Privacy / retention / deletion: deleted conversations are removed from synthesis；memory data in exports；Enterprise retention policies apply。
- Audit / observability: 官方明确说 past-chat reference 会带 citations。
- Evaluation evidence, if any: 无公开 benchmark。
- Key mechanisms: project-scoped memory；on-demand chat search；editable memory summary；incognito；memory portability。
- What it directly supports: project/book scoped state；retrieval vs summary 分层；可见可改 memory summary。
- What it only analogically supports: 其“knowledgeable collaborator”更偏工作协作 than reading state。
- What it argues against: account-wide undifferentiated memory。
- Fit to Reading Companion: **高**。特别是 project/book scope、citation-backed previous-chat reference、pause/reset/incognito。
- Misfit / limitation: Claude 的 memory summary 仍不是 source-grounded citation object；更像协作语境抽象层。
- Complexity implication: 一旦做 summary，就要有 delete propagation、update cadence、project boundary、visible edits。
- Candidate project-relevant implications: reading-run / book memory 比 account-wide memory 更自然；cold recall 可优先于 always-injected summary。
- Evidence strength: 强。

### Work Card: Gemini Apps / Google

- Work ID: APP-WORK-015–018
- Source links: 见 APP-WORK-015–018
- Authors / Organization: Google
- Year / First Posted / Last Updated: 2025–2026
- Source Type: Help Center
- Evidence Type: Official stated behavior
- Read status: deep-read / partial-read
- Maturity: Official product docs
- Confidence: High
- Original product problem: 把显式 saved info 与对 past chats 的引用分开，让个性化有来源标签。
- Target user / system setting: consumer assistant tied to Google account/activity。
- Memory ontology: Saved info、past chats、Gemini Apps Activity / Keep Activity、temporary chat。
- Memory representation: explicit user-editable saved facts；activity-backed old chats。
- Memory formation: saved info 可在设置中添加，也可对话中要求记住；past chats 依赖 activity；临时 chat 不进 recent chats / activity。
- Memory management / lifecycle: edit/delete saved info；turn on/off；delete chats from recent chats/activity。
- Memory retrieval / injection: 如果用了 saved info 会标注 “Your saved info”；如果用了 past chats 会标注 “Previous chats”。
- Context engineering: past-chat reference 与 saved-info reference 是两类 source label。
- User controls: saved info UI、temporary chat、activity controls。
- Privacy / retention / deletion: temporary chats 和 activity-off chats 有 72 小时 retention；Keep Activity 绑定可用性。
- Audit / observability: 是当前少数把 memory 来源标签做得非常显式的 consumer assistant。
- Evaluation evidence, if any: 无公开 benchmark。
- Key mechanisms: explicit state、visible labels、activity gating、temporary mode。
- What it directly supports: source-label disclosure；explicit user state 与 history source 分开。
- What it only analogically supports: account-level personalization。
- What it argues against: 把活动历史默认等同于 durable knowledge。
- Fit to Reading Companion: **中高**。最有借鉴意义的是 source labels 与 explicit saved state，不是生活偏好本身。
- Misfit / limitation: 受 Google account activity 机制强耦合；不是面向 source-grounded reading。
- Complexity implication: 如果要引用 past sessions，就需要区分 activity/history 与 explicit memory 的权限和标签。
- Candidate project-relevant implications: 被引用的 memory 类型应在回答层明确可见。
- Evidence strength: 强。

### Work Card: Microsoft 365 Copilot Memory

- Work ID: APP-WORK-021–025
- Source links: 见 APP-WORK-021–025
- Authors / Organization: Microsoft
- Year / First Posted / Last Updated: 2025–2026
- Source Type: Support + Learn + Microsoft Graph docs
- Evidence Type: Official stated behavior / Official developer-facing mechanism
- Read status: deep-read / partial-read
- Maturity: Official product docs / Official framework docs
- Confidence: High
- Original product problem: 在企业办公套件里做 personalization，同时兼顾 admin / compliance / retention。
- Target user / system setting: enterprise productivity assistant。
- Memory ontology: saved memories、inferred details from chat history、custom instructions、temporary chat、enhanced personalization control。
- Memory representation: mailbox-backed hidden store + user-facing settings。
- Memory formation: automatic save；history inference；custom instructions。
- Memory management / lifecycle: settings-based toggles；delete saved memories；turn off chat-history personalization deletes inferred details after 30 days；admin can disable enhanced personalization。
- Memory retrieval / injection: saved memories + inferred history + custom instructions 都可能进入 context。
- Context engineering: 更像 governed personalization rather than source recall。
- User controls: memory tile、chat history toggle、temporary chat。
- Privacy / retention / deletion: docs 明确 memory 存于 Exchange mailbox hidden folder；retention policies for memory differ from ordinary chat retention；admin deletion / DSR 更复杂。
- Audit / observability: governance 清楚，但“这次回答具体用了哪个 memory”不如 Gemini / ChatGPT 新 UI 透明。
- Evaluation evidence, if any: 无公开 benchmark。
- Key mechanisms: enterprise admin control；storage / retention caveats；temporary chat；separation of saved vs inferred vs instructions。
- What it directly supports: memory taxonomy 必须拆分；admin/user control 是独立层。
- What it only analogically supports: mailbox hidden-folder storage。
- What it argues against: 在 RC 早期把 compliance-heavy stack 一起引入。
- Fit to Reading Companion: **边界价值高，直接可搬价值中低**。
- Misfit / limitation: 企业治理复杂度远超当前 RC 所需。
- Complexity implication: 一旦走“组织化 memory”，就要承受 retention、ownership、admin APIs、hidden stores 的系统税。
- Candidate project-relevant implications: 先做 source audit，再做 memory admin。
- Evidence strength: 强。

### Work Card: Perplexity / Comet

- Work ID: APP-WORK-026–030
- Source links: 见 APP-WORK-026–030
- Authors / Organization: Perplexity / Comet
- Year / First Posted / Last Updated: 2026
- Source Type: Help Center
- Evidence Type: Official stated behavior
- Read status: deep-read / partial-read
- Maturity: Official product docs
- Confidence: High
- Original product problem: 搜索助手 / AI 浏览器 个性化。
- Target user / system setting: search-centric assistant + browser agent。
- Memory ontology: Memories、Search history / search library、incognito、Enterprise memory。
- Memory representation: saved memories + previous searches；Comet 复用 Perplexity account memory。
- Memory formation: 通过问答与偏好积累；Perplexity 自动决定何时使用 memory/history。
- Memory management / lifecycle: Personalize settings；Manage Memories；delete specific / all；organization-level disable deletes org memories。
- Memory retrieval / injection: memory 或 previous searches 只在“有助于更好回答时”使用，且会在 answer 中引用相关来源。
- Context engineering: search-oriented personalization，比 broad assistant 更偏检索行为。
- User controls: separate toggles for memory and history；incognito always off；Comet memory settings routed to Perplexity account。
- Privacy / retention / deletion: delete logs may be kept up to 30 days；Enterprise memory belongs to org；agent actions not stored in Comet memory。
- Audit / observability: 是少数明确说会 cite memory/history references 的产品。
- Key mechanisms: memory + history 分离；incognito；account-shared browser memory；agent actions not stored。
- What it directly supports: search history 不应与 durable memory 混同；引用时应显式显示来源。
- What it only analogically supports: personal search over browsing history。
- What it argues against: 把 personal search / browsing history 包装成 reading memory。
- Fit to Reading Companion: **中等**。有价值的是 history vs memory separation 与 cited references；浏览器个性化本身不适配。
- Misfit / limitation: 以搜索与 web personalization 为主，不以 source-grounded reading state 为主。
- Complexity implication: 一旦引入 history layer，就要区分 query history、memory、agent actions 三者。
- Evidence strength: 强。

### Work Card: Hermes Agent

- Work ID: APP-WORK-031–034
- Source links: 见 APP-WORK-031–034
- Authors / Organization: Hermes Agent / Nous Research
- Year / First Posted / Last Updated: 2026
- Source Type: Official feature pages + technical blog
- Evidence Type: Official stated behavior / Official developer-facing mechanism
- Read status: deep-read
- Maturity: Official blog / technical report
- Confidence: Medium-High
- Original product problem: 构造一个会随着用户和环境长期成长的本地/自托管 Agent。
- Target user / system setting: local or self-hosted autonomous agent。
- Memory ontology: MEMORY.md、USER.md、skills、SQLite session search、optional Honcho。
- Memory representation: bounded hot memory files + on-demand skills + full session archive。
- Memory formation: agent-curated memory；self-evaluation checkpoint；complex tasks 转 skill。
- Memory management / lifecycle: char limits、automatic consolidation、plain-text editability。
- Memory retrieval / injection: MEMORY.md / USER.md frozen snapshot；skills progressive disclosure；session DB FTS5 summarized on demand。
- Context engineering: 强调 prefix-cache stability，避免 mid-session rewrites destabilize context。
- User controls: files 可手工编辑/导出；本地 ownership 强。
- Privacy / retention / deletion: local-first。
- Audit / observability: files / db / skills 都比较可见；但官方公开材料仍偏 marketing-technical hybrid。
- Evaluation evidence, if any: 无系统 benchmark；多为机制说明。
- Key mechanisms: tiny hot memory + cold archive；procedural memory as skills；checkpoint distillation。
- What it directly supports: small authoritative prompt memory、cold episodic recall、procedural memory 分层。
- What it only analogically supports: richer user model / Honcho。
- What it argues against: “所有 memory 都应该进 prompt”。
- Fit to Reading Companion: **高**。尤其是 bounded hot memory + searchable cold archive + procedural memory boundary。
- Misfit / limitation: 其目标是 general autonomous agent；部分机制比 RC 当前需要更重。
- Complexity implication: 即便 local-first，也会带来 limits、consolidation、skill catalog、session DB、search summarization 等复杂度。
- Candidate project-relevant implications: 先做小热区 + 冷存档，不要默认全库提取；procedure 与 reading state 分档。
- Evidence strength: 中强。

### Work Card: Clawdbot / OpenClaw

- Work ID: APP-WORK-035–036
- Source links: 见 APP-WORK-035–036
- Authors / Organization: Clawd.bot / OpenClaw docs surfaces
- Year / First Posted / Last Updated: 2026
- Source Type: Docs
- Evidence Type: Open-source docs
- Read status: deep-read
- Maturity: Official framework docs
- Confidence: Medium-High
- Original product problem: local-first assistant/workspace agent 的持久化记忆与工作区真相源。
- Target user / system setting: local assistant / workspace agent。
- Memory ontology: MEMORY.md、memory/YYYY-MM-DD.md、一些文档中还出现 DREAMS.md。
- Memory representation: plain Markdown；workspace 是 source of truth。
- Memory formation: “remember this” 就写盘；决策/偏好进 MEMORY.md；日常运行上下文进 daily log。
- Memory management / lifecycle: read today + yesterday at session start；pre-compaction ping；only load MEMORY.md in main private session。
- Memory retrieval / injection: daily logs 自动读；curated MEMORY.md 私聊主会话加载；文档还指向 memory plugin / hybrid search。
- Context engineering: 强调 disk truth over hidden RAM state。
- User controls: 文件直读直改；可本地拥有。
- Privacy / retention / deletion: local workspace ownership；group context 不载入 private MEMORY.md。
- Audit / observability: 极强，因为 memory 就是文件。
- Key mechanisms: daily log vs durable memory；pre-compaction flush；private-session-only curated memory。
- What it directly supports: append-only trace 与 curated long-term state 分层；disk source-of-truth。
- What it only analogically supports: group-context safety rules。
- What it argues against: 把 runtime RAM state 当 authoritative memory。
- Fit to Reading Companion: **很高**。这是最接近“文件优先、可审计、source of truth on disk”的应用实践。
- Misfit / limitation: docs 中 memory search / plugin 仍在演进；命名关系（Clawd.bot vs OpenClaw）需继续消歧。
- Complexity implication: 文件简单，但仍要处理 read order、private/public boundary、pre-compaction lifecycle。
- Candidate project-relevant implications: daily log / settlement log / curated state 可以显式分层。
- Evidence strength: 中强。

### Work Card: Claude Code

- Work ID: APP-WORK-014
- Source links: 见 APP-WORK-014
- Authors / Organization: Anthropic
- Year / First Posted / Last Updated: 2026
- Source Type: Developer docs
- Evidence Type: Official developer-facing mechanism
- Read status: deep-read
- Maturity: Official framework docs
- Confidence: High
- Original product problem: 让 coding agent 在新 session 里复用项目规则、个人习惯与自动积累的 learnings。
- Target user / system setting: coding agent / terminal / IDE。
- Memory ontology: CLAUDE.md、CLAUDE.local.md、rules、auto memory、/memory。
- Memory representation: plain Markdown hierarchy + machine-local auto memory directory。
- Memory formation: 人工写 CLAUDE.md；Claude 根据 corrections 自动写 auto memory。
- Memory management / lifecycle: /memory 可浏览、开关 auto memory、打开文件；project/user/org/local 多层级。
- Memory retrieval / injection: CLAUDE.md 全量起始加载；subtree files on demand；MEMORY.md index only first 200 lines / 25KB start-load。
- Context engineering: 通过 hierarchy、rule scoping、on-demand topic files 来抑制 prompt 膨胀。
- User controls: files plain-text editable；/memory 可见。
- Privacy / retention / deletion: machine-local；not shared across machines unless sync。
- Audit / observability: 很强。
- Key mechanisms: hierarchy、path-scoped rules、small index + topic files on demand、/memory command。
- What it directly supports: file hierarchy + small hot index + cold topic files。
- What it only analogically supports: coding-rule memory。
- What it argues against: 把所有项目约束都放在一个巨大启动 prompt。
- Fit to Reading Companion: **高**。特别是小索引 + 主题文件 + 显式查看/编辑。
- Misfit / limitation: coding rules 与 reading state 不是同一类信息。
- Complexity implication: 层级与加载规则需要非常明确，不然冲突难 debug。
- Candidate project-relevant implications: project/book scoped file memory 值得优先考虑。
- Evidence strength: 强。

### Work Card: Gemini CLI

- Work ID: APP-WORK-019–020
- Source links: 见 APP-WORK-019–020
- Authors / Organization: Google Gemini CLI
- Year / First Posted / Last Updated: 2026
- Source Type: Developer docs
- Evidence Type: Official developer-facing mechanism
- Read status: deep-read
- Maturity: Official framework docs
- Confidence: High
- Original product problem: 让 terminal agent 用简单上下文文件和命令管理持续指令。
- Target user / system setting: coding / terminal agent。
- Memory ontology: GEMINI.md hierarchy、save_memory tool、/memory add/show/refresh。
- Memory representation: global GEMINI.md + project/ancestor/subdir context files。
- Memory formation: save_memory fact appends to global GEMINI.md；/memory add；手工维护 context files。
- Memory management / lifecycle: /memory show / refresh / add；可 imports。
- Memory retrieval / injection: hierarchical context files are concatenated and sent with every prompt；tool writes concise facts to home GEMINI.md。
- Context engineering: files > hidden DB；explicit hierarchy；inspectable full current memory。
- User controls: show / refresh / edit by hand。
- Privacy / retention / deletion: local files。
- Audit / observability: 很强。
- Key mechanisms: file hierarchy + memory command + explicit fact appends。
- What it directly supports: lightweight auditable file memory。
- What it only analogically supports: coding/project instructions。
- What it argues against: 过早引入 opaque service-side memory。
- Fit to Reading Companion: **高**。特别适合“先做 JSON/JSONL / file state，不急着上 DB”。
- Misfit / limitation: 它主要处理 instruction/context，不处理 source-grounded semantic trace。
- Complexity implication: hierarchy / imports / refresh semantics 仍需设计清楚。
- Candidate project-relevant implications: 先做显式文件 state + inspect command 是合理低风险路线。
- Evidence strength: 强。

### Work Card: Negative evidence / Memory-as-tax line

- Work ID: APP-WORK-001–030, 041
- Source links: 见 APP-WORK-001–030, APP-WORK-041
- Authors / Organization: 多方官方；Manthan Gupta 为 secondary cautionary reference
- Year / First Posted / Last Updated: 2024–2026
- Source Type: 综合
- Evidence Type: Boundary + Opinion / cautionary analysis
- Read status: mixed
- Maturity: mixed
- Confidence: Medium-High for boundary claim；Low for未深读 Manthan 具体论证
- Original product problem: 不是单一产品，而是从多个产品逆向看 memory 的产品税。
- Key mechanisms: delete propagation、temporary/incognito、admin controls、source disclosure、retention caveats、toggle granularity、prompt budget controls。
- What it directly supports: “memory 需要 inspect/edit/delete/pause/export/no-memory mode” 不是可选装饰，而是产品负债清单。
- What it only analogically supports: 直接反 memory 口号。
- What it argues against: 在 RC 还没把 source-grounded state、audit、SourceRef 做稳前，就上广义 personalization memory。
- Fit to Reading Companion: **极高的边界价值**。
- Misfit / limitation: negative evidence 只能限定边界，不能直接给正向方案。
- Complexity implication: memory 带来治理税、debug 税、prompt 税、privacy 税。
- Candidate project-relevant implications: “先做显式状态，再做隐式记忆” 应视为强边界。
- Evidence strength: 中强；但 APP-WORK-041 仍待补读。

## Mechanism Evidence Cards 与 Evidence Ledger

### Mechanism Evidence Cards

> 说明：以下采用**压缩卡片格式**；每张卡仍给出 external system、mechanism、support area、support type、reasoning bridge、why not direct copy、complexity、confidence、stable citation。
> 为控制长度，部分元字段合并到同一行。
> Support Type 严格使用 Direct / Analogical / Negative / Boundary / Background。

| Evidence ID | External product / system | Work ID | Year | Mechanism name | Supports which possible design area | Support Type | Mechanism summary | Reasoning bridge | Why not direct copy | Complexity implication | Confidence | Stable citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| APP-EXT-001 | ChatGPT | APP-WORK-001/002/003 | 2025–2026 | Saved durable memory vs dynamic chat history | Memory Ontology / Retrieval / User Control | Direct | 把 saved memories 与 chat history 明确分成两层。 | RC 也需要把“durable reading state”与“本轮会话历史/摘要”拆开；相似点是都存在跨会话续接，差异点是 RC 的 durable state 必须有 source grounding。 | ChatGPT 的 durable layer主要是 user preference，不是 source-grounded observation。 | 需要双存储语义与删除传播。 | High | [APP-WORK-001–003](https://help.openai.com/en/articles/8983136-what-is-memory) |
| APP-EXT-002 | ChatGPT | APP-WORK-004 | 2026 | Temporary Chat | User Control / Privacy / Governance / Planning / Session Interface | Direct | no-memory session，不访问也不更新 memory。 | RC 需要“本次阅读不要吸收到 future state”的开关；相似点是 session isolation，差异在于 RC 还要控制是否写入 reading observations。 | 不能只复制 UI，不定义 run-level write policy。 | 需要会话隔离与保留策略。 | High | [APP-WORK-004](https://help.openai.com/en/articles/8914046-temporary-chat-faq) |
| APP-EXT-003 | ChatGPT | APP-WORK-006 | 2026 | Memory Sources UI | Audit / User Control / Context Engineering | Direct | 回答后展示用了哪些 memories / past chats / instructions。 | RC 最需要的是“这条回答到底用了哪些 prior state/source”；相似点是 answer-time disclosure，差异点是 RC 还需要指向 SourceRef / run trace。 | 只显示“用了 memory”而不显示 source coords 不够。 | 需要回答层 provenance UI。 | High | [APP-WORK-006](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) |
| APP-EXT-004 | ChatGPT | APP-WORK-002/003 | 2025–2026 | Delete requires both memory deletion and source chat cleanup | Memory Management / Privacy / Governance | Boundary | 删除记忆与删除原聊天不是同一个动作。 | RC 若将状态从 accepted source units 抽取出来，也会面临“删状态”与“删原trace / provenance”的双层问题。 | RC 可以更简单，因为 source 是书和 accepted units，不是生活聊天。 | 需要删除传播模型。 | High | [APP-WORK-002–003](https://help.openai.com/en/articles/11146739-how-does-reference-saved-memories-work) |
| APP-EXT-005 | Claude | APP-WORK-008 | 2026 | On-demand chat search as tool call | Memory Retrieval / Context Engineering / Audit | Direct | past-chat retrieval 通过 tool-call RAG 显式发生。 | RC 中“回忆过去阅读”更像检索旧 run / trace，而不是 always inject；相似点是需要按需找旧上下文，差异点是 RC 应优先找 source-grounded units。 | 不应直接把过去聊天当作权威 source。 | 需要检索接口与引用链。 | High | [APP-WORK-008](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| APP-EXT-006 | Claude | APP-WORK-008 | 2026 | 24-hour memory synthesis | Memory Formation / Management / Retrieval | Analogical | Claude 将非 project chats 综合成 memory summary，每 24h 更新。 | 这支持“periodic consolidation / settlement summary”这一设计方向；相似点是都需要从长对话压缩，差异点是 RC 必须显式保留 source-groundedness。 | 不能把 summary 直接当事实源。 | 需要 cadence、overwrite policy、staleness policy。 | High | [APP-WORK-008](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| APP-EXT-007 | Claude | APP-WORK-008/012 | 2026 | Project memory and project summary | Memory Ontology / Storage / Planning / Session Interface | Direct | 每个 project 有独立 memory space 和 summary。 | 最贴近 RC 的不是账号级 persona，而是 book/project scoped state；相似点是对象边界清晰，差异点是 RC 的 project 是 book / run / accepted units。 | Claude project memory 仍偏协作，不是阅读证据层。 | 需要 workspace / book boundary 设计。 | High | [APP-WORK-008–012](https://support.claude.com/en/articles/9517075-what-are-projects) |
| APP-EXT-008 | Claude | APP-WORK-009 | 2026 | Incognito chats excluded from memory and history | User Control / Privacy / Governance | Direct | incognito 不进 history，不进 memory summary。 | RC 应支持 private/no-memory reading run；相似点是隔离敏感会话，差异是 RC 还可能保留本地审计而不转入 durable memory。 | Claude incognito 仍可访问 profile info。 | 需要 run privacy mode 语义。 | High | [APP-WORK-009](https://support.claude.com/en/articles/12260368-using-incognito-chats) |
| APP-EXT-009 | Claude | APP-WORK-010 | 2026 | Import / export memory | User Control / Governance | Boundary | memory 可迁移、可备份、可导出。 | 说明一旦 memory 成为用户资产，就会出现 portability 需求；RC 短期未必需要，但这是中长期产品税信号。 | RC 初期不宜先做跨产品迁移。 | 需要 schema stability 与 export contract。 | High | [APP-WORK-010](https://support.claude.com/en/articles/12123587-import-and-export-your-memory-from-claude) |
| APP-EXT-010 | Claude | APP-WORK-008 | 2026 | Past chat citations | Audit / Retrieval / User Control | Direct | Claude 引用旧聊天时给 citations。 | RC 的 reading memory 更应能指出“这条回忆来自哪条过去 observation / source unit”；相似点是 recall must be inspectable。 | 不能只引用旧摘要，要能落到原 source evidence。 | 需要 provenance pointer design。 | High | [APP-WORK-008](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| APP-EXT-011 | Gemini Apps | APP-WORK-015 | 2026 | Saved info as user-editable explicit state | Memory Representation / User Control | Direct | Saved info 是显式、可编辑的保存信息层。 | RC 可以从中借“explicit state beats hidden inference”原则；相似点是都需要人可见 state，差异点是 RC state 应围绕 source-grounded reading facts。 | 不能把生活偏好直接映射为阅读 memory。 | 需要显式 state surface。 | High | [APP-WORK-015](https://support.google.com/gemini/answer/15637730) |
| APP-EXT-012 | Gemini Apps | APP-WORK-016 | 2026 | Previous chats label | Audit / Memory Source Disclosure | Direct | 若引用过去聊天，会显示 “Previous chats”。 | 对 RC 来说，最需要的也是“这段回答引用了过去哪类状态”；相似点是 disclosure，差异点是 RC 应显示更细的 source class / refs。 | label 粒度仍偏粗。 | 需要 UI metamodel。 | High | [APP-WORK-016](https://support.google.com/gemini/answer/13666746) |
| APP-EXT-013 | Gemini Apps | APP-WORK-015 | 2026 | Your saved info label | Audit / User Control / Context Engineering | Direct | 若引用 saved info，会显示 “Your saved info”。 | 支持“按来源类型披露”的方向；RC 可分 accepted observation / session summary / durable memory。 | 不能只有标签没有 source text。 | 需要 source-type UI，且可 drill-down。 | High | [APP-WORK-015](https://support.google.com/gemini/answer/15637730) |
| APP-EXT-014 | Gemini Apps | APP-WORK-017/018 | 2025–2026 | Temporary chat + Keep Activity coupling | Privacy / Governance / Planning / Session Interface | Boundary | temporary chat 不入 recent chats/activity；activity controls 影响可用性。 | 提醒 RC：如果未来做 past-run lookup，必须明确 activity-like retention 开关；相似点是 retention gates behavior。 | RC 不应把 activity-style telemetry 作为前提。 | 需要 retention semantics。 | High | [APP-WORK-017–018](https://support.google.com/gemini/answer/13275745) |
| APP-EXT-015 | Microsoft 365 Copilot | APP-WORK-021/022/023 | 2025–2026 | Saved memories vs inferred chat-history details vs custom instructions | Memory Ontology | Direct | Copilot 把 personalization 拆成三层。 | RC 也应该显式区分 structural state、past-run inferences、execution instructions；相似点是 context sources heterogenous。 | 不能把所有层都叫 memory。 | 需要多层 ontology。 | High | [APP-WORK-021–023](https://support.microsoft.com/en-au/topic/personalize-what-microsoft-365-copilot-remembers-cba7b79a-c46f-4ca7-b46e-2fa22c563f90) |
| APP-EXT-016 | Microsoft 365 Copilot | APP-WORK-023 | 2026 | Turning off history deletes inferred details after 30 days | Memory Management / Privacy | Boundary | inferred history layer 可关闭并触发延迟删除。 | RC 如果将“自动推断摘要”与“显式 durable state”并存，也要定义关闭后的 purge 行为。 | 早期最好少做 inferred layer。 | 需要 purge clock / grace period。 | High | [APP-WORK-023](https://support.microsoft.com/en-us/topic/revisit-your-microsoft-365-copilot-chat-history-6ea899e3-3bb1-450a-a2ae-220341ac193a) |
| APP-EXT-017 | Microsoft 365 Copilot | APP-WORK-024/025 | 2025–2026 | Admin enhanced personalization control | Governance / Privacy / Storage | Boundary | tenant-level enhanced personalization 决定 memory 是否可用。 | 对 RC 是边界证据：一旦走组织级 memory，就不再只是产品小功能，而是治理系统。 | 当前 RC 不该过早引入 tenant-grade controls。 | 高治理复杂度。 | Medium-High | [APP-WORK-024–025](https://learn.microsoft.com/en-us/graph/control-enhanced-personalization-privacy) |
| APP-EXT-018 | Microsoft 365 Copilot | APP-WORK-024 | 2025 | Exchange hidden-folder storage | Storage / Governance | Boundary | memory 存在 user mailbox hidden folder。 | 说明企业 memory 往往依附既有企业数据平面。对 RC 是反向边界：当前不应模仿这种重存储耦合。 | 与 RC 的 simplicity principle 不匹配。 | 高。 | Medium-High | [APP-WORK-024](https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-personalization-memory) |
| APP-EXT-019 | Perplexity | APP-WORK-026 | 2026 | Memory vs search history separation | Memory Ontology / Retrieval | Direct | Perplexity分别处理 memories 与 search history。 | RC 中也应区分“durable reading state”与“旧查询/旧会话检索痕迹”；相似点是回答时可能用两类来源。 | 搜索历史不是理解状态。 | 需要 two-source policy。 | High | [APP-WORK-026](https://www.perplexity.ai/help-center/en/articles/10968016-memory) |
| APP-EXT-020 | Perplexity | APP-WORK-026 | 2026 | Always cite memory/history references in answer | Audit / Context Engineering | Direct | 官方明确说 memory/history references 会被 cited。 | 这是 RC 的强正向证据：memory 使用必须有用户可见 provenance。 | Perplexity 的 citation 仍偏 broad source label。 | 需要 answer-level provenance model。 | High | [APP-WORK-026](https://www.perplexity.ai/help-center/en/articles/10968016-memory) |
| APP-EXT-021 | Perplexity / Comet | APP-WORK-028/029/030 | 2026 | Incognito disables memory and history; agent actions not stored | Privacy / Governance / Boundary | Boundary | 搜索型产品把 incognito 与 agent action persistence 分开。 | 对 RC 的启发是：如果将来有 action layer 或 tool actions，不要默认它们进入 reading memory。 | 不能把 browser agent semantics 直接照搬。 | 需要 action-vs-memory boundary。 | High | [APP-WORK-028–030](https://comet-help.perplexity.ai/en/articles/12658438-comet-memory) |
| APP-EXT-022 | Perplexity Enterprise | APP-WORK-027 | 2026 | Org-owned memory + org-level disable deletes existing memories | Governance / User Control / Privacy | Boundary | 组织拥有 memory，管理员可全局删除。 | 对 RC 是强边界：若未来做团队版，ownership 与个人版会完全不同。 | 当前 RC 不应先为 team-memory 设计。 | 高治理复杂度。 | High | [APP-WORK-027](https://www.perplexity.ai/help-center/en/articles/13654357-memory-for-enterprise-organizations) |
| APP-EXT-023 | Hermes Agent | APP-WORK-031/032 | 2026 | Small hot memory + cold session archive | Storage / Retrieval / Context Engineering | Direct | MEMORY.md/USER.md 小而常驻；SQLite FTS5 无限冷存档，按需总结。 | 这几乎就是 RC 最值得借的结构：小热区保存最关键 reading state，大量旧 run 留冷存档；相似点是都需要 bounded prompt + deep recall。 | Hermes 的 general-agent memory 比 RC 更偏 broad workflow。 | 需要 hot/cold boundary、search summarization。 | Medium-High | [APP-WORK-031–032](https://hermes-agent.ai/blog/hermes-agent-memory-system) |
| APP-EXT-024 | Hermes Agent | APP-WORK-032 | 2026 | Frozen snapshot pattern | Context Engineering / Storage | Direct | session start 注入冻结 memory，不在中途重写。 | RC 可借此保护 prompt 稳定性，避免 mid-run state drift；相似点是长阅读过程中需要稳定判断底座。 | RC 仍需支持 source-linked live updates elsewhere。 | 需要 split between live state and startup snapshot。 | Medium-High | [APP-WORK-032](https://hermes-agent.ai/blog/hermes-agent-memory-system) |
| APP-EXT-025 | Hermes Agent | APP-WORK-032 | 2026 | Hard character limits + consolidation | Memory Management / Context Engineering | Direct | hot memory 受 2,200 / 1,375 字符限制，并自动压缩。 | RC 也应把热状态看成稀缺 prompt 预算，必须有 consolidation/selection。 | 不能把阅读关键结构压得过度抽象。 | 需要 memory budget 与 consolidation policy。 | Medium-High | [APP-WORK-032](https://hermes-agent.ai/blog/hermes-agent-memory-system) |
| APP-EXT-026 | Hermes Agent | APP-WORK-033/034 | 2026 | Skills as procedural memory | Memory Ontology / Planning / Session Interface | Direct | 把“怎么做”写成 SKILL.md，按需加载。 | RC 里 procedure memory 与 content memory 应分开；相似点是都需要重复流程规范，差异点是 reading content state 不能混进 procedure。 | 不能用 skills 代替 reading evidence。 | 需要 procedure/content separation。 | Medium-High | [APP-WORK-033–034](https://hermes-agent.ai/blog/hermes-agent-skills-guide) |
| APP-EXT-027 | Hermes Agent | APP-WORK-034 | 2026 | Self-evaluation checkpoint every 15 tool calls | Memory Formation / Management / Evaluation | Analogical | 周期性自评决定是否更新 memory / patch skill。 | 这支持“reading-run settlement 前应有显式状态沉淀钩子”；相似点是 bounded lifecycle checkpoint。 | RC 的 trigger 不应按 tool calls，而应按 read/settlement semantics。 | 需要 lifecycle hooks。 | Medium | [APP-WORK-034](https://hermes-agent.ai/features/learning-loop) |
| APP-EXT-028 | Clawdbot / OpenClaw | APP-WORK-035/036 | 2026 | Disk is source of truth | Storage / Audit | Direct | memory 只有写到 workspace 文件才算“记住”。 | 这是与 RC “可解释、可审计、source-grounded”最一致的应用证据；相似点是都强调 disk truth over hidden latent state。 | OpenClaw 的 workspace 仍是 general assistant，不是 reading graph。 | 需要 explicit disk schema。 | Medium-High | [APP-WORK-035–036](https://docs.openclaw.ai/concepts/memory) |
| APP-EXT-029 | Clawdbot / OpenClaw | APP-WORK-035/036 | 2026 | Daily log vs curated MEMORY.md | Memory Representation / Management / Audit | Direct | append-only daily log 与 curated durable memory 分层。 | RC 非常适合 adopted as principle：run trace / settlement audit / curated reading state 分立。 | daily log 不能等于 final state。 | 需要 log-to-state promotion rules。 | Medium-High | [APP-WORK-035–036](https://docs.clawd.bot/concepts/memory) |
| APP-EXT-030 | Clawdbot / OpenClaw | APP-WORK-035/036 | 2026 | Read today + yesterday at session start | Retrieval / Session Interface | Analogical | 启动时只读取最近日志，保持轻量 continuity。 | RC 可类比为“默认只加载最近 run context，老历史按需取”；相似点是 recency-biased continuity。 | 今天/昨天规则未必适合阅读对象边界。 | 需要 recency policy 更基于 book/run than date。 | Medium-High | [APP-WORK-035–036](https://docs.clawd.bot/concepts/memory) |
| APP-EXT-031 | Clawdbot / OpenClaw | APP-WORK-035 | 2026 | Pre-compaction ping | Memory Management / Lifecycle | Direct | compaction 前 silent turn 提醒写 durable memory。 | 对 RC 最有价值的 lifecycle 证据之一：在 context 被压缩或 run 结束前，做 memory flush / settlement。 | 必须配 source audit，否则 flush 只会把噪声持久化。 | 需要 pre-settlement trigger 与 write filters。 | Medium-High | [APP-WORK-035](https://docs.clawd.bot/concepts/memory) |
| APP-EXT-032 | OpenClaw | APP-WORK-036 | 2026 | Main private session only loads MEMORY.md | Privacy / Governance / Context Engineering | Boundary | curated long-term memory 只在主私有会话加载，不进 group contexts。 | 对 RC 的启发是 memory scope 依上下文类型而变化；相似点是并非所有 surfaces 都应带同一 memory。 | RC 当前未必有 group context，但将来 surface-aware loading 很关键。 | 需要 surface-scoped loading policy。 | Medium-High | [APP-WORK-036](https://docs.openclaw.ai/concepts/memory) |
| APP-EXT-033 | Claude Code | APP-WORK-014 | 2026 | Hierarchical file memory | Storage / Context Engineering | Direct | org / project / user / local 多层 CLAUDE.md；subtree on-demand。 | 对 RC 的启发是 book / workspace / user / local experiment 这些 scope 将来可分层；相似点是多层上下文。 | 早期不该做太多层级，容易过度工程。 | 需要 precedence rules。 | High | [APP-WORK-014](https://docs.anthropic.com/en/docs/claude-code/memory) |
| APP-EXT-034 | Claude Code | APP-WORK-014 | 2026 | Small startup index, topic files on demand | Context Engineering / Storage | Direct | MEMORY.md 只加载前 200 行/25KB，其余 topic files 按需读。 | RC 可借其“small hot index + cold topic files”思想；相似点是 prompt budget 固定而 archive 可大。 | reading memory 需要 source refs，比 coding notes 更严格。 | 需要 index/topic contract。 | High | [APP-WORK-014](https://docs.anthropic.com/en/docs/claude-code/memory) |
| APP-EXT-035 | Gemini CLI | APP-WORK-019/020 | 2026 | save_memory appends concise fact to GEMINI.md | Memory Formation / Storage / Audit | Direct | 用极轻量方式把 fact 写入全局文件，并可 /memory show。 | 这支持 RC 先从 file-based explicit updates 起步，而不是上 opaque auto-memory；相似点是用户/agent 都能 inspect memory text。 | 不能把任意 fact append 成无审计 reading state。 | 需要 write validation。 | High | [APP-WORK-019–020](https://google-gemini.github.io/gemini-cli/docs/tools/memory.html) |
| APP-EXT-036 | Cross-product boundary | APP-WORK-001–030 | 2024–2026 | Memory feature implies product tax | Governance / Evaluation / Planning | Negative | 几乎所有成熟产品都补了 toggles、delete、temp/incognito、retention、admin、disclosure。 | 这说明“memory 不是白送的产品功能”，而是一串治理义务；RC 的正确读法不是反 memory，而是 narrow, task-bound, auditable memory。 | 不能把“别人都有”当成“我们也要马上上”。 | 复杂度持续上升。 | High | [APP-WORK-001–030](https://help.openai.com/en/articles/8983136-what-is-memory) |

### Application Evidence Ledger

| Evidence ID | Work ID | Product / System | Year | Mechanism | Topic | Support Type | Reasoning Bridge Summary | Possible RC Design Area | Why Not Direct Copy | Complexity Cost | Confidence | Stable Citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| APP-EXT-001 | APP-WORK-001–003 | ChatGPT | 2025–2026 | saved vs history split | ontology | Direct | durable vs dynamic 必须拆开 | ontology / retrieval | user profile != reading state | Medium | High | 见 APP-WORK-001–003 |
| APP-EXT-002 | APP-WORK-004 | ChatGPT | 2026 | temporary chat | session control | Direct | no-memory reading run 需要明示 | user control | 只复制 UI 不够 | Medium | High | 见 APP-WORK-004 |
| APP-EXT-003 | APP-WORK-006 | ChatGPT | 2026 | memory sources UI | audit | Direct | 回答层 disclosure 很关键 | audit / UX | 仍需 SourceRef 粒度 | Medium | High | 见 APP-WORK-006 |
| APP-EXT-004 | APP-WORK-002–003 | ChatGPT | 2025–2026 | delete propagation | lifecycle | Boundary | 删 state 与删原trace不同 | management | RC 可更简单但仍要定义 | Medium | High | 见 APP-WORK-002–003 |
| APP-EXT-005 | APP-WORK-008 | Claude | 2026 | chat search tool call | retrieval | Direct | on-demand recall 更贴近 RC | retrieval | past-chat 不是 authority | Medium | High | 见 APP-WORK-008 |
| APP-EXT-006 | APP-WORK-008 | Claude | 2026 | 24h synthesis | formation | Analogical | settlement-like summary 可借 | management | summary 可能失 grounding | Medium | High | 见 APP-WORK-008 |
| APP-EXT-007 | APP-WORK-008/012 | Claude | 2026 | project memory | scoping | Direct | book/project scope 更自然 | storage / ontology | 协作语境不等同阅读 | Medium | High | 见 APP-WORK-008/012 |
| APP-EXT-008 | APP-WORK-009 | Claude | 2026 | incognito | privacy | Direct | private run 很必要 | governance | still has profile access | Medium | High | 见 APP-WORK-009 |
| APP-EXT-009 | APP-WORK-010 | Claude | 2026 | import/export | portability | Boundary | 持久资产终会要求导出 | user control | 早期不必先做 | High | High | 见 APP-WORK-010 |
| APP-EXT-010 | APP-WORK-008 | Claude | 2026 | past chat citations | audit | Direct | recall 必须可追溯 | audit | 需落到 source refs | Medium | High | 见 APP-WORK-008 |
| APP-EXT-011 | APP-WORK-015 | Gemini | 2026 | saved info | explicit state | Direct | explicit state 优于 hidden inference | representation | 生活偏好不是 reading memory | Low-Med | High | 见 APP-WORK-015 |
| APP-EXT-012 | APP-WORK-016 | Gemini | 2026 | previous chats label | disclosure | Direct | 被引用来源类型可见 | audit | 标签粒度偏粗 | Low-Med | High | 见 APP-WORK-016 |
| APP-EXT-013 | APP-WORK-015 | Gemini | 2026 | your saved info label | disclosure | Direct | saved info 与 history 应分标签 | UX | 仍需 source text | Low-Med | High | 见 APP-WORK-015 |
| APP-EXT-014 | APP-WORK-017/018 | Gemini | 2025–2026 | temp chat + activity | retention | Boundary | history feature 与 retention 耦合 | privacy | 不应用 activity 化 | Medium | High | 见 APP-WORK-017/018 |
| APP-EXT-015 | APP-WORK-021–023 | Copilot | 2025–2026 | saved vs inferred vs instructions | ontology | Direct | 多层 personalization 必须明分 | ontology | 不应一律叫 memory | Medium | High | 见 APP-WORK-021–023 |
| APP-EXT-016 | APP-WORK-023 | Copilot | 2026 | 30-day purge for inferred history | lifecycle | Boundary | inferred layers 要有 purge model | management | 最好少做 inferred early | Medium | High | 见 APP-WORK-023 |
| APP-EXT-017 | APP-WORK-024/025 | Copilot | 2025–2026 | admin control | governance | Boundary | 组织级 memory 是治理系统 | governance | RC 早期过重 | High | Med-High | 见 APP-WORK-024/025 |
| APP-EXT-018 | APP-WORK-024 | Copilot | 2025 | hidden-folder storage | storage | Boundary | 重企业耦合不适合 RC 当前 | storage | simplicity 不符 | High | Med-High | 见 APP-WORK-024 |
| APP-EXT-019 | APP-WORK-026 | Perplexity | 2026 | memory vs search history | ontology | Direct | query history 与 durable memory 区分 | retrieval | history 不等于 state | Medium | High | 见 APP-WORK-026 |
| APP-EXT-020 | APP-WORK-026 | Perplexity | 2026 | cite memory/history refs | disclosure | Direct | 回答里必须显示所用历史 | audit | 粒度仍可更细 | Low-Med | High | 见 APP-WORK-026 |
| APP-EXT-021 | APP-WORK-028–030 | Comet/Perplexity | 2026 | incognito + no agent-action memory | boundary | Boundary | agent actions 不应默认进 memory | governance | 浏览器语境不同 | Medium | High | 见 APP-WORK-028–030 |
| APP-EXT-022 | APP-WORK-027 | Perplexity Enterprise | 2026 | org-owned memory | governance | Boundary | team memory ownership 很复杂 | governance | 当前无需 | High | High | 见 APP-WORK-027 |
| APP-EXT-023 | APP-WORK-031/032 | Hermes | 2026 | hot memory + cold archive | storage | Direct | 小热区 + 大冷库 非常适合 RC | storage / retrieval | general-agent 语境更宽 | Medium | Med-High | 见 APP-WORK-031/032 |
| APP-EXT-024 | APP-WORK-032 | Hermes | 2026 | frozen snapshot | prompt stability | Direct | 启动快照保护推理稳定性 | context engineering | live update 另需通道 | Medium | Med-High | 见 APP-WORK-032 |
| APP-EXT-025 | APP-WORK-032 | Hermes | 2026 | hard limits | budget | Direct | 热状态应视为稀缺预算 | management | 过度压缩有风险 | Medium | Med-High | 见 APP-WORK-032 |
| APP-EXT-026 | APP-WORK-033/034 | Hermes | 2026 | skills as procedural memory | procedure boundary | Direct | procedure 与 content 分层 | ontology | 不能替代 content state | Medium | Med-High | 见 APP-WORK-033/034 |
| APP-EXT-027 | APP-WORK-034 | Hermes | 2026 | self-eval checkpoint | lifecycle | Analogical | settlement 前检查点有类比价值 | management | trigger 不应照搬 | Medium | Medium | 见 APP-WORK-034 |
| APP-EXT-028 | APP-WORK-035/036 | OpenClaw/Clawd.bot | 2026 | disk truth | file state | Direct | 明确磁盘为 authoritative state | storage / audit | 仍需 schema discipline | Low-Med | Med-High | 见 APP-WORK-035/036 |
| APP-EXT-029 | APP-WORK-035/036 | OpenClaw/Clawd.bot | 2026 | daily log vs MEMORY.md | layered state | Direct | trace 与 curated state 分层 | representation | 日志不能等于记忆 | Low-Med | Med-High | 见 APP-WORK-035/036 |
| APP-EXT-030 | APP-WORK-035/036 | OpenClaw/Clawd.bot | 2026 | read today+yesterday | recency recall | Analogical | 默认 recent continuity，老历史按需取 | retrieval | 日期规则未必适配书 | Low-Med | Med-High | 见 APP-WORK-035/036 |
| APP-EXT-031 | APP-WORK-035 | Clawdbot | 2026 | pre-compaction ping | flush lifecycle | Direct | run/compaction 前写 durable memory | lifecycle | 无 audit 会持久化噪声 | Medium | Med-High | 见 APP-WORK-035 |
| APP-EXT-032 | APP-WORK-036 | OpenClaw | 2026 | private-session-only MEMORY.md | surface scoping | Boundary | 不同 surface 装载不同 memory | governance | RC 当前 surface 少 | Medium | Med-High | 见 APP-WORK-036 |
| APP-EXT-033 | APP-WORK-014 | Claude Code | 2026 | hierarchical file memory | workspace memory | Direct | scope / precedence 设计启发强 | storage | 层级过多会过工 | Medium | High | 见 APP-WORK-014 |
| APP-EXT-034 | APP-WORK-014 | Claude Code | 2026 | small index + topic files | hot/cold file split | Direct | 小索引 + 主题文件按需加载 | retrieval / storage | reading refs 更严格 | Medium | High | 见 APP-WORK-014 |
| APP-EXT-035 | APP-WORK-019/020 | Gemini CLI | 2026 | save_memory to GEMINI.md | write path | Direct | 从显式 append 开始最稳妥 | formation / audit | 需写入验证 | Low-Med | High | 见 APP-WORK-019/020 |
| APP-EXT-036 | APP-WORK-001–030 | Cross-product | 2024–2026 | memory implies product tax | anti-pattern | Negative | 成熟产品都用 controls 证明系统税存在 | planning | 不能因为别人有就早上 | High | High | 综合见前述官方来源 |

## 产品取舍与 Reading Companion 相关性预览

### Adopt / Adapt / Reject by Product

| Work ID | Product / System | Adopt | Adapt | Reject | Why |
| --- | --- | --- | --- | --- | --- |
| APP-WORK-001–006 | ChatGPT / OpenAI | saved vs history 分层；temporary mode；source disclosure | 把 sources 细化到 SourceRef / run trace | 账号级 broad personalization | 直接可用的是分层与治理，不是 persona memory |
| APP-WORK-007–013 | Claude / Anthropic | project scope；chat search；past-chat citations；view/edit/pause/reset | memory summary 需要更强 source grounding | 把协作型 summary 当权威记忆 | Claude 最接近 RC 的 retrieval+project 范式 |
| APP-WORK-015–018 | Gemini Apps | saved info / previous chats 分标签；temporary chat | explicit saved state 改造成 reading-state UI | activity-driven personalization | 标签披露值得 adopt，activity coupling 不值得 |
| APP-WORK-021–025 | Microsoft 365 Copilot | ontology 拆分；admin tax awareness | 部分 user controls 可借鉴 | hidden-folder / enterprise compliance stack | 治理边界价值大，当前实现过重 |
| APP-WORK-026–030 | Perplexity / Comet | memory vs history 分离；citation-to-history；incognito | search-like recall 可适配成 old-run lookup | personal search / browser-history memory | search orientation 是边界证据，不是默认方案 |
| APP-WORK-031–034 | Hermes Agent | hot/cold split；frozen snapshot；skills boundary；checkpoint distillation | char limits / skill loop 需按 reading semantics 改 | optional richer user model / Honcho | Hermes 是最强应用层架构类比之一 |
| APP-WORK-035–036 | Clawdbot / OpenClaw | file-as-truth；daily log vs MEMORY.md；pre-compaction flush | 加上 SourceRef / settlement audit / JSONL | group-chat/agentic workspace 细节 | 与 RC “文件优先、可审计”原则贴合度最高 |
| APP-WORK-014 | Claude Code | hierarchical files；small startup index；/memory manageability | 把 CLAUDE.md 改造成 reading/book/run scopes | coding-rule surface 直接照搬 | 对 file memory 与 inspectability 很有价值 |
| APP-WORK-019–020 | Gemini CLI | GEMINI.md + save_memory + /memory | 变成 explicit RC state commands | coding/project context 直接等同阅读记忆 | 轻量起步路径清晰 |
| APP-WORK-041 | “Memory is a mistake” line | memory-as-tax 边界意识 | 作为 anti-overreach checklist | “因此完全不要 memory” 的简单化结论 | 应作为 boundary evidence，不是 dogma |

### Reading Companion Relevance Preview

| External application pattern | Possible RC relevance | Needed project-side validation | Risk |
| --- | --- | --- | --- |
| Saved memory vs chat history | 可帮助拆 durable reading state vs dynamic run history | 需要验证 RC 中哪些状态 truly durable | durables 被用户画像污染 |
| Project/book scoped memory | 很可能比 account-wide 更适合 | 需验证 book / segment / run scope 哪个最稳 | 作用域过多难 debug |
| Tiny prompt memory + cold archive | 很强相关 | 需验证 active_attention / concept_registry 是否适合进 hot zone | 过度压缩丢结构 |
| File-based memory | 很强相关 | 需验证 JSON/JSONL 与 Markdown 的分工 | 文件碎片和冲突增长 |
| Daily logs vs curated long-term memory | 很强相关 | 需验证 read audit / settlement audit 如何晋升为 curated state | 日志污染长期状态 |
| Pre-compaction flush | 很强相关 | 需验证 settlement 前有无安全 write hook | flush 噪声进入 durable memory |
| Explicit remember/delete commands | 中高相关 | 需验证谁能触发：用户、agent、reviewer？ | side effects 不可控 |
| User-visible manage memory | 高相关 | 需验证最小 UI/CLI 面板 | overload 用户 |
| Temporary / no-memory mode | 很高相关 | 需验证 run-level read/write suppression | 与审计需求冲突 |
| Memory source disclosure | 极高相关 | 需验证 SourceRef / run trace / memory type disclosure model | 只做标签不够细 |
| On-demand chat / run search | 高相关 | 需验证 old-run retrieval 是否显著优于 always inject | 检索伪相关导致 FVI |
| Periodic memory summary | 中相关 | 需验证 summary 是否会破坏 source grounding | 把摘要当事实 |
| Skills / procedural memory | 中高相关 | 需验证 reading procedure 与 content state 分层接口 | procedure 污染内容状态 |
| Enterprise compliance controls | 低直连，高边界价值 | 需验证是否真要多用户/组织部署 | 过重系统税 |
| Memory product tax | 极高相关 | 需验证删除、暂停、导出、审计最小集 | 低估维护成本 |
| Anti-overpersonalization / explicit state over implicit memory | 极高相关 | 需验证 explicit state 是否已足够覆盖主要需求 | 为“高级”而过度复杂化 |

## 研究缺口与引用质量审计

### Research Gaps

| Gap | Why it matters | Suggested next action |
| --- | --- | --- |
| Manthan 五篇未完成逐篇深读 | 用户明确要求优先读；它们是 reverse-engineering 与 cautionary bridge 的重要线索 | 下一轮先补读并逐条与官方 docs 核验 |
| Clawdbot / Clawd.bot / OpenClaw 命名与谱系仍需消歧 | 当前 docs surfaces 相似，但不能默认同一实现事实 | 下一轮单独做 naming / repo / docs lineage note |
| Hermes 若要进一步提升置信度，仍需补正式 docs / repo-level docs 对照 | 当前官方材料偏技术博客 / feature pages | 下一轮只做 very shallow docs-code path 核验 |
| Cursor / Windsurf / Replit Agent / Devin / Codex memory 官方覆盖不足 | coding-agent memory 生态还未补齐 | 单列为 Tier 2 扩展包，不在本补丁硬写 |
| Meta AI / Grok 官方 memory docs 未纳入 | 影响 consumer assistant 对比完整度 | 若下一轮仍要补全 consumer 对照，再独立检索 |
| 官方 docs 多描述用户行为与开关，不暴露真实 prompt assembly | 会限制对 memory 注入层的确定性判断 | 下一轮严格区分“official stated behavior”与“prompt-layer inference” |
| memory source disclosure 的细粒度含义各产品不统一 | “显示 previous chats” 不等于显示具体 source coordinates | 下一轮做 disclosure taxonomy |
| API memory tools 与 consumer assistant memory 不是一层 | 容易误把 dev-surface 设计套到消费产品，或反过来 | 下一轮正式 mapping 时分别进入不同证据桶 |
| 缺少真正“reading agent”产品级 memory 公案 | 当前多是通用助手、搜索助手、coding agent、browser agent | 下一轮把“类比强度”作为独立打分项 |
| 尚未把应用证据映射到 RC 的 JSON/JSONL、SourceRef、settlement audit | 这是本次刻意不做的部分 | 下一轮 Evidence-to-Project Mapping 专做这一层 |

### Citation Quality Audit

| Check | Result | Notes |
| --- | --- | --- |
| 是否没有输出 turn... 作为最终 citation？ | Pass | 全文已清理为稳定链接或移除不可追溯的内部引用标记 |
| 是否为所有 Work Cards 添加年份或 last updated？ | Pass | 均已给出 |
| 是否为所有 Work Cards 添加 stable URL？ | Pass | 通过 Bibliography 统一提供 |
| 官方产品/开发者文档是否至少 10 个？ | Pass | 实际远超 10 个 |
| 开源应用/agent memory docs 是否至少 4 个？ | Pass | Claude Code、Gemini CLI、Clawdbot、OpenClaw |
| 第三方 reverse-engineering / cautionary posts 是否明确标注 secondary？ | Pass | APP-WORK-037–041 全部明确标注 |
| 每个 Work Card 是否区分 official / inferred / reverse-engineered？ | Pass | 已区分 |
| 每个 Evidence Card 是否有 reasoning bridge？ | Pass | 均有压缩版 reasoning bridge |
| 是否区分 Direct / Analogical / Negative / Boundary / Background support？ | Pass | 已严格区分；本轮未额外使用 Background 卡 |
| 是否避免把应用实现假设写成外部事实？ | Pass | 未把 prompt assembly 反推当官方事实 |
| 是否避免把用户画像 memory 当成阅读 memory？ | Pass | 多处明确反对 |
| 是否明确标注未深读来源？ | Pass | Manthan 系列已诚实标注 |
| 是否没有输出项目设计决策 / Candidate Decision Ledger？ | Pass | 只有 relevance preview，没有设计决策 |
| 是否没有读取 Second Reader GitHub 代码？ | Pass | 只读取 README/current-state 与上一轮材料做约束校准 |

### 结论性综合

当前流行 Agent 应用的 memory 已经显示出一个很清楚的产品规律：**它不是一个东西，而是一组必须分层管理的东西。** 成熟产品不会只说“我们有 memory”；它们会区分 saved memory、history reference、project/workspace memory、summary、file context、skills、temporary mode、admin control、retention 和 disclosure。这个共识本身，就是对 Reading Companion 最重要的外部证据之一。

对 Reading Companion 最相关的，不是“通用助手记住了我喜欢什么餐厅”，而是以下几条应用层原则：

**按对象而不是按人格做作用域；把热状态做小，把冷历史做可检索；把日志、整理记忆、程序性技能分开；在回答层披露用了哪些已有状态；给用户与系统都留出 pause/delete/no-memory 通道；把 memory 当成产品税而不是免费魔法。** 这些原则在 Claude Projects / Claude Code / Gemini CLI / OpenClaw / Clawdbot / Hermes 的证据里最强，在 ChatGPT / Gemini / Copilot / Perplexity 的控制面与披露面里最成熟。

同样清楚的是，很多看起来“先进”的 memory 机制，对 Reading Companion 其实只是**边界证据**：账号级 user profiling、enterprise hidden stores、browser personal search、社交画像、跨应用 personalization，都说明 memory 很容易越界，不说明 RC 必须照搬。对于一个以 inside-trial reading observations、source-grounded reading state、file-based JSON / JSONL、inline SourceRef、read/settlement audit 为核心约束的系统，**先把显式状态做实，往往比先做隐式个性化更稳。**
