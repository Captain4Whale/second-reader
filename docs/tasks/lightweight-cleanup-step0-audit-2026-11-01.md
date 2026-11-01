# Second Reader 第 0 步轻量清理：代码排查与执行提案

审查日期：2026-11-01（Asia/Shanghai）。状态：**待用户审阅；未执行清理**。

审查基线：`main`，`cdd987edadd10cac3b1d199c8c094fe6d22f6430`。开始排查时工作区干净。本轮只新增本文，没有修改既有文件、启动评测、调用模型、迁移数据、打 tag、提交或推送。

路径约定：下文 `B/` 指仓库内 `reading-companion-backend/`；代码行号均以此基线为准。检查采用源码阅读、tracked Python 的 AST import 反向引用扫描、全文符号/脚本入口搜索、已有运行 JSON/JSONL 统计和远端分支只读查询。没有以一次搜索无命中替代动态行为验证；外部消费者和运行中的进程环境无法由仓库静态扫描完全排除。

## 1. 审阅摘要

1. **实际默认机制是 attentional_v2。** 但 `iterator_reader` 目录包含它仍在使用的解析、语言、LLM gateway 包装、文件定位和 Library/API 工具。可以退役旧 reader，不能直接删除整个目录。
2. **slow cycle 不进入当前 Ingest / Digest prompt，但并非没有消费者。** 每个读完的章节仍调用 consolidation，候选 promotion 逐个调用模型；结果进入持久化、checkpoint、下一章 slow cycle、旧评测 bundle。它还会追加非 Product 的章末 reaction。`reconsolidation()` 则只找到定义、导出和测试，没有生产调用。
3. **用户的严格删除规则与 slow-cycle 降本目标存在范围交叉。** consolidation、promotion、active_attention 当前确实执行，按“不在实际运行路径上”不能直接判为确定删除。建议批准一个明确例外：关闭这条没有进入核心阅读 prompt / Product 的支路，再清理它的状态与专属评测。不得把这个例外假写成“死代码”。
4. **真人批注评测是删除旧机制前的首要保护对象。** `analyze_marginalia_note_precision_recall.py` 顶层导入 `run_user_level_selective_comparison.py`；后者及 `completed_output_reuse.py` 顶层导入 iterator adapter。先解开这些依赖，再删旧 reader，保留匹配、judge、数据集构建与人工审阅能力。
5. **当前 Product / Pack 不依赖旧 reader 语义，但当前 UI 投影依赖 slow_cycle.py 内的确定性函数。** 不能按模块名称整删 `slow_cycle.py`，也不能按“compatibility”关键词批删。
6. **已有整书实测可省量有界。** 《悉达多》已有账本的 325 次逻辑调用中，consolidation 为 15 次、77,614 tokens、累计调用耗时 344.128 秒。停用该支路对应约 4.6% 调用、3.5% 已知 tokens；不是消掉大部分成本。另发现 survey 重复执行，可作为独立可选小修。
7. **历史保全尚未过关。** `main`、Annotation Pack 分支与远端匹配；另一个 worktree 的 `codex/annotation-hub-v0` 有 28 个提交未被当前 origin 分支覆盖，远端无该分支。真人批注和大部分运行产物被 gitignore，必须先做仓库外备份。

## 2. 当前实际运行路径

### 2.1 入口、解析和阅读

```text
API upload/start/resume -> library/jobs.py -> main.py parse/read
CLI main.py -> reading_runtime.parse_book/read_book
  -> reading_mechanisms 注册表（默认 attentional_v2）
  -> AttentionalV2Mechanism
     parse_attentional_v2 / run_reading_runner
       -> ensure_canonical_parse
          -> parsers.parse_ebook + metadata/language/source asset
          -> iterator_reader.parse._load_or_build_book_document
             -> reading_core EPUB/BookDocument builder
             -> 新建时 deterministic source_normalization v1.2
             -> public/book_document.json
       -> initialize_artifact_tree + survey（逐章 LLM zone classifier）
       -> 恢复 checkpoint，打开/恢复 ReadingProductStore
       -> 从 Product commit truth 重建 private progress / Unit Memory
       -> 按 survey reading_plan 排章
          -> source_spans 构造段落+字符偏移 preview
          -> Ingest（边界；可调用一次 retrieve_unit_memory 工具）
          -> runtime 接受边界、检索/筛选 Unit Memory
          -> hot Understanding + retrieved Understanding -> ReadingMemory
          -> Digest -> Understanding / Response / Marginalia
          -> 校验坐标、提交 Product Unit
          -> 派生 recent memory / Unit Memory / reaction / audit / span ledger
          -> 前移 accepted cursor、写状态/checkpoint
          -> 章末 consolidation + 可选 promotion
          -> Product -> 当前 chapter/UI compatibility projection
       -> whole-book completion 校验 -> Product finalize -> current.json
独立、显式 export_annotation_pack -> complete Reading Product -> Pack
```

关键证据：

| 环节 | 代码证据 | 清理时必须守住的边界 |
| --- | --- | --- |
| 注册/默认 | `B/src/reading_mechanisms/__init__.py:16`；`B/src/reading_runtime/__init__.py:55` | 默认 v2，iterator 仍被 eager import/注册；删除需同步注册和包导出 |
| 产品 worker | `B/src/library/jobs.py:650`、`:1022`；`B/main.py:111`、`:133` | shell-first resume 与机制身份；不能把旧 run 静默按 v2 继续 |
| 公共 parse | `B/src/reading_runtime/provisioning.py:10`、`:109`；`B/src/iterator_reader/parse.py:240` | 保留确切 EPUB、共享 BookDocument、坐标和 source digest |
| Source Normalization | `B/src/reading_runtime/source_normalization.py:104` | 默认无 classifier，只有显式传入 classifier 才走 audit 分支；普通 parse 不是 LLM source cleaning |
| Survey | `B/src/attentional_v2/survey.py:230`、`:630`；`runner.py:3181`、`:3261` | parse 和每次 read/resume 都重建；影响 mainline/deferred/auxiliary 和完整性判定 |
| Ingest | `B/src/attentional_v2/runner.py:2105`；`llm_calls.py:911` | prompt 是当前窗口/位置/书籍信息；不携带 active_attention/reflective_frames |
| 检索和上下文 | `runner.py:1586`、`:1707`、`:1784`；`unit_memory.py:408`、`:633` | hot 约 5k、retrieved 约 10k token 预算；不是全历史上下文；embedding 是额外模型调用面 |
| Digest | `llm_calls.py:1090`；`prompts/digest.py:882` | 实际 XML 只使用 SourceUnit、ReadingMemory 等当前块；packet 中的 attention/reflective 字段未传入 renderer |
| 提交顺序 | `runner.py:2945`、`:2994`；`product_output.py`；`reading_product/store.py` | Product 先提交，private settlement/cursor 后推进；Unit Memory 是程序派生，没有单独 LLM 摘要调用 |
| 恢复 | `runner.py:914`、`:1035`、`:3299`；`resume.py:811` | reading_id 不变、不得重读已提交 Unit；保留当前 Product/Unit Memory 恢复 |
| 章末/封版 | `runner.py:3559`、`:3601`、`:3704` | 删 slow cycle 后仍必须完成 chapter status/checkpoint/投影；只有整书达成才能 finalize |
| UI / Pack | `product_compatibility.py:17`；`annotation_pack/exporter.py:446`、`:605` | UI 投影调用 slow_cycle 内确定性 helper；默认 Pack 只吃 complete Product，phase9 legacy 显式选择、没有 fallback |

### 2.2 实际 LLM 调用清单

| 调用 | 频率/触发 | 是否保留 |
| --- | --- | --- |
| `chapter_zone_classifier` | 每次 survey 每章一次基础调用；失败可退回启发式 | 保留语义；重复运行去重见 D4 |
| `ingest` | 每个 Unit 至少一次基础模型响应；工具执行后的模型续答、边界重试、结构修复另计 | 保留，后续规则切分消融的实验对象 |
| `digest` | 每个新 Unit 一次基础调用；结构修复/失败恢复可能增加 | 保留 |
| `chapter_consolidation` | 每次完成一个被调度章节一次；在完成状态/checkpoint 前执行 | 建议经 D1 批准后停用 |
| `reflective_promotion` | 每个 consolidation 的 `promotion_candidates` 一次 | 建议同 D1 停用；无固定每书次数 |
| `reconsolidation` / `bridge_resolution` | 有实现和 prompt，无当前 runner 调用点 | 可删除相应专属代码；当前每书节省 0 |
| LLM source normalization | 仅显式 audit classifier 注入；普通路径 0 | 可去掉历史 LLM probe，保留 deterministic normalization |
| Unit Memory embedding | hybrid 索引/查询可能请求本地 Ollama；有缓存/降级 | 保留并单独观测；不混入上述 generation 调用数量 |

逻辑 LLM ledger 行、物理 provider attempt、一个 Ingest 操作、一个已提交 Unit 不是同一个计数。今后成本报告需要同时列这几项，不能用 `2 × Unit 数` 当整书总调用数。

### 2.3 文档与代码/数据漂移

- 根 `AGENTS.md` 的 First Files To Read 仍称 `iterator_v1.md` 为 current live/default；注册代码、后端 AGENTS、机制目录表和 current-state 均指向 v2。执行时改阅读指引，保留 iterator 文档归档。
- `attentional_v2.md:123` 的 “Sentence-intake … execute directly” 已不符合 runner：`process_sentence_intake` 只作为旧测试 monkeypatch seam 导入（`runner.py:46`），主循环使用 source preview。
- `attentional_v2.md:188`、`:603`、`:743` 将 reconsolidation 列入章末能力；当前 `run_phase6_chapter_cycle` 不调用它。应区分有函数与当前执行。
- `survey.py:636` 称 survey 为 orientation-only，但其 reading_plan 实际决定章队列和 finalizer completion scope，不能据此删除。
- `docs/backend-reader-evaluation.md:384`、`:398` 仍指 June 14 的 202-case 数据集；`user_level_selective_v1.py:30`、split manifest 第 17/29 行和磁盘实际指向 June 29 unique-notes 包：**5 segments、158 note cases**。清理应保留新旧数据，不拿旧文档覆盖当前 manifest。
- 文档声称 source normalization deterministic-only 与当前代码一致；旧 LLM classifier 残留不代表每本书仍付这部分模型成本。

## 3. 清理清单

“确定删除”表示经本方案整体批准、完成所列依赖拆除后执行；不是本轮授权。对仍在运行路径或未来实验可能使用的项，明确放在“保留/待决策”，不伪装为确定死代码。

### 3.1 确定删除：旧执行能力和专属代码

| ID | 候选 | 为什么/证据 | 删除影响面与前置条件 |
| --- | --- | --- | --- |
| A1 | `B/src/reading_mechanisms/iterator_v1.py`；`iterator_reader/{iterator,reader,book_analysis,policy,markdown,mechanism_spec}.py` | 默认 v2 的实际阅读不调用旧 reader；后续基线不需要旧机制。adapter 的 parse/read 明确委托旧实现（`:55`、`:72`） | 注册/`__init__` eager imports、CLI choices、配置 override、job legacy resume、双机制 eval 都要一起解开。不得删共享 parse/language/storage；不得仅留下一个报 ImportError 的旧选项 |
| A2 | `attentional_v2/bridge.py`、`prompts/bridge_resolution.py` | AST 生产反向调用仅模块内部；外部调用来自 `test_attentional_v2_bridge.py`。runner 没有 phase5 bridge；当前 Digest 不发 bridge 意图 | 同步 prompt registry/types/包导出、工具 schema、专用测试和 bridge-only helper。保留 Marginalia 源定位能力 |
| A3 | `attentional_v2/retrieval.py`、`intake.py` | 旧 AnchorBank/逐句 candidate retrieval 与 sentence intake；前者仅桥接/测试消费者，后者 runner 是明确 `noqa: F401` 的 monkeypatch seam | 不是 `unit_memory.py`。删 seam，拆 `test_attentional_v2_intake_and_retrieval.py`；保留当前 source-span/preview/Unit Memory 测试 |
| A4 | `slow_cycle.py` 的 `reconsolidation()`、`apply_reconsolidation()` 及专属 normalizer/ID helper；`prompts/reconsolidation.py` | 无生产调用；主要函数在 `:1117`、`:1240`；旧 append/supersede 框架不属于本次实验基线 | 同步 export、prompt bundle、tool schema、专属测试；ledger/checkpoint 字段仍有运行消费者，字段移除随 D1/D2，而非直接破坏旧状态读取 |
| A5 | `B/scripts/temporary/` 下本次核对的 6 个 `.py`，具体见附录 | 各文件头声明 one-off；绑定 April/May 特定 run、旧对比/anchor repair，不是当前通用评测入口 | F4A 脚本被 `tests/test_f4a_quality_audit.py` 动态加载，连同专属测试删除；报告/原始结果只归档/备份。保留通用 memory-quality probe 模块 |
| A6 | `scripts/await_lane_a_then_run_private_library_cleanup_round3.py`、`private_library_cleanup_round3.py` | 绑定 March 28 lane/job IDs 与旧 private-library round3；不是后续数据集持续构建框架 | 先确认没有该历史 job 仍运行；不删 `run_dataset_review_pipeline` / library notes / corpus builder。保存其已生成报告与 coordination 数据 |
| A7 | `scripts/run_source_normalization_v1_1_multibook_validation.py` 和 `source_normalization.py` 中只供它使用的旧 LLM prompt/invoker | 验证旧 v1.1 source-flow 分类；当前 v1.2 默认 deterministic，且 Ingest 语义切分实验不是 parse source-flow 分类实验 | 只删孤立的 LLM probe 分支；共享 normalization 的保守规则、source metadata、句层重建、回归测试保留；注入 classifier 测试拆开处理 |
| A8 | `src/prompts/legacy.py`、`templates.py`、`capabilities/book_analysis.py` | quote expansion 等旧 prompt 仅通过 shim/旧能力导入；消费者是旧 iterator 与 prompt architecture 测试 | 更新 `test_prompt_architecture.py` 的旧断言，保留当前 prompt governance；`src/prompts/shared.py` 被 Digest/registry 使用，明确保留 |
| A9 | `src/tools/search.py` 的旧搜索能力，及其专属配置/依赖 | `search_web` 当前调用方只有旧 `iterator_reader/reader.py`、`book_analysis.py`；普通 v2 Digest 没有联网搜索 | 随 A1 移除 `get_tavily_api_key` 和不再使用的 `tavily-python` 依赖/锁文件条目；不改用户 `.env` 或凭据，不删除通用 provider/tool transport |
| A10 | 只验证上述旧能力的测试 | 不是未来基线；具体已计数的 10 个整文件见附录 | shared parse、API、Product、resume、LLM gateway 测试不可按 `iterator` 文件名前缀删除；旧专用断言删除后必须有保留能力的独立覆盖 |

### 3.2 移入归档：保留内容与可追踪性

建议建立 `docs/archive/pre-cleanup-2026-11/` 和 `B/docs/archive/pre-cleanup-2026-11/`，不把旧可执行代码搬进去继续保留在主干。执行时用移动映射和原路径索引维护证据链接。

| 内容 | 归档方案 | 影响面 |
| --- | --- | --- |
| `docs/backend-reading-mechanisms/iterator_v1.md` | 整篇移入根归档；机制 catalog 改为 retired、链接归档 | README、AGENTS、workspace/lifecycle/mechanism 路由同步；不保留误称 supported fallback 的正文 |
| 只服务旧机制的设计/阶段实施材料、paused Memory/Planning 轨道 | 保留完整内容，按主题移入归档；当前 approved design/运行说明不挪 | 先按 current-state、registry、decision-log、stable docs 引用找入链；不是整目录通配移动 |
| `B/docs/evaluation/excerpt/`、`long_span/` 等旧结果解读及对应 research 解读 | 旧 interpretation / appendix 移入后端归档；保留 run id、日期、原文件名和证据路径 | run ledger/evidence catalog 的报告路径、Markdown 链接需同步；历史数值不重算、不换口径 |
| `B/docs/evaluation/user_level/` 中旧评测报告 | 报告可以归档；**数据集、note matching、precision/recall 代码不随报告退役** | 活跃评测指南与可重现来源必须仍可找到 |
| 已 tracked 的 review packet archives | 当前已处 archive，共 479 个 tracked 文件；原地保留即可 | `.gitignore` 不等于未跟踪。不要 `git rm` 清掉其 evidence；新的原始产物仍不进 git |
| decision-log / run ledger / evidence catalog | **原位置完整保留**；仅未来执行时追加决策或更新移动后的定位链接 | 不删旧条目，不把历史指令当当前执行授权；不重写历史质量结论 |

归档只改变组织方式，不计入代码删除收益；ignored 的原始运行数据应做独立备份，不能以“文档已归档”代替。

### 3.3 保留：当前依赖、实验资产及待决策项

| ID | 保留内容 | 依据/用途 | 允许的后续收窄 |
| --- | --- | --- | --- |
| K1 | `reading_core/`、parsers、provisioning、deterministic source normalization | 当前 source identity/坐标、Product、Pack 和真人批注对齐共用 | 仅剪 A7 旧 classifier 专属代码，不改 source 字节/段落/偏移 |
| K2 | `iterator_reader/language.py`、`llm_utils.py`、`storage.py` 及 parse/frontend_artifacts/models 中共享部分 | `provisioning.py:10`；`main.py:16`；`catalog.py:29`、`:39`；`jobs.py:69`、`:1062`；`user_marks.py:11` | 本步可保留旧目录名，直接删旧执行分支；不为清空目录另起重构。LLM wrapper 可作等价 import 改接，但无每书省调用收益 |
| K3 | `product_output.py`、`product_compatibility.py`、`reading_product/`；slow_cycle 内 reaction/compatibility 纯函数 | Product -> 旧 UI 仍调用 `build_reaction_record_from_surfaced_reaction` / `project_chapter_result_compatibility` | D1 只剪 LLM 支路，不能整删 slow_cycle.py。旧前端保持可用 |
| K4 | `annotation_pack/`、contracts、CLI、fixtures/golden、phase9 显式 legacy adapter | 用户明确暂不处理 Pack；默认 Product adapter 无旧 reader 语义依赖，但 exporter 顶层仍导入 legacy adapter | legacy adapter 此轮保留；它依赖 reaction_records 路径、SourceRef/schema，不能顺手删这些符号 |
| K5 | `unit_memory.py`、recent memory、source spans、span ledger、当前 resume/checkpoint、Product reconciliation | 检索 vs 全量 Understanding vs 近期窗口及规则切分实验需要；Product 恢复不能靠重新跑模型补齐 | 模式变化留到消融阶段；保留 off/text-only/hybrid、embedding cache、降级和配置冻结语义 |
| K6 | `library_notes.py`、register/refresh notes、`human_notes_guided_dataset.py`、cluster planning、`user_level_selective_v1.py`、corpus/source intake、相关 manifests/data | 当前 June 29 包 158 note cases/5 segments；notes catalog 5 assets/1,325 entries；源目录和对齐结果是核心资产 | 不把 raw notes、标注归一化、source spans、split 修复工具当旧 eval 垃圾 |
| K7 | `analyze_marginalia_note_precision_recall.py`、`run_user_level_selective_comparison.py` 的 matching/judge/current runner、`render_user_level_selective_audit.py`、user-level orchestrator；`completed_output_reuse.py` 的当前分支 | precision/recall 模块在 `:14` 直接导入 comparison；comparison `:15–28`、reuse `:10` 连接旧机制 | 删除 iterator imports/branch/CLI `both`，保留当前评分能力与历史结果的只读分析；不能整文件删除 |
| K8 | `eval/compare_highlights.py` | 虽支持旧 Markdown/structure，仍有真人 highlights 导入解析（`:350`）和 judge/matching 资产 | 暂保留，D5 确认是否仍有用户输入；必要时只剪旧产物 adapter，不能因“legacy”直接删 |
| K9 | LLM gateway/registry/usage/pricing/telemetry、observation_*、job lease/registry/concurrency、当前 observability/audit/report | 后续模型、缓存、成本/耗时实验直接复用；当前系统已提供本地 ledger，Phoenix 可选 | 清掉旧节点/旧 store 的专属字段，不删成本事实、失败/usage unknown、物理 attempt、run identity |
| K10 | `benchmark_probes.py`、`run_long_span_vnext.py` 中当前记忆诊断、`run_runtime_viability.py`、`run_integrity.py`、live smoke、Ingest probe、capacity/health、whole-book/context-scope 试验及审阅工具 | 后续记忆和上下文实验可用；`benchmark_probes` 已由 observability 调用，不是因为旧命名就失效 | 剪旧 iterator 和 active_attention 评分面；context-scope retry 的单次执行逻辑待当前人工审阅闭环后再评估 |
| K11 | `eval/subsegment` 的数据与可复用 boundary rubric | runner 绑定 iterator（`run_benchmark.py:27–28`），但切分质量题目与未来 Ingest-vs-rule 有交集 | 见 D5：建议删旧执行器，保留 dataset/judge 资产；不保留旧 reader 作比较基线 |
| K12 | `run_excerpt_comparison.py`、`run_chapter_comparison.py`、`run_accumulation_comparison.py`、`run_durable_trace_reentry.py` 暂作为待裁剪文件 | 旧双机制入口可删；但含 dataset loader、judge、失败处理/re-entry 等可复用部分；accumulation 还直接 import excerpt；编排脚本有调用 | D5 决定完整退役还是仅留当前诊断；不以“未来新旧对比”保留 iterator |
| K13 | `backfill_legacy_outputs.py`、artifact fallback、旧目录只读适配 | dev/stable/setup 实际启动调用 backfill；catalog/user_marks/job registry 使用 existing_* 定位器 | 见 D3；若停止启动回填，先删除三个 launcher 调用、明确旧书库可读/可恢复边界，再删脚本，不是 one-off 通删 |
| K14 | `active_attention` / reflective_frames / knowledge_activations / reconsolidation_records 的当前状态接线 | runner load/save、state projection、resume、checkpoint、integrity/normalized eval 仍消费 | 见 D1/D2。目标是删冗余支路，不是重新设计 memory；未批准前保留 |
| K15 | 源码中的 provider 协议、旧 registry/env 配置入口 | 模型选型可能需要；兼容配置与旧阅读机制不是同一件事 | 保留 Anthropic/OpenAI/Google transport、结构修复、路由与重试；本轮不因“legacy env”删除 |

## 4. slow cycle 与 active_attention 的依赖闭包

### 4.1 核心阅读 prompt：没有输入，但存在旁路处理

`runner._run_digest_for_source_unit()` 仍把 active_attention / reflective_frames 传给 `build_carry_forward_context`。`state_projection.build_digest_prompt_packet()` 也构造 attention / reflective 字段；然而 `llm_calls.digest():1116–1126` 仅取 recent memory，并把显式 `reading_memory_lines` 交给 XML renderer。因此“参数存在”不等于“送给模型”。

不能进一步推成“所有字段无影响”：carry-forward refs 还参与 Marginalia `allowed_ref_ids` 归一化；continuation capsule、checkpoint 和 audit 仍携带这些状态。删除时要以实际 prompt bytes、规范化 U/R/M、Product 投影和恢复行为分别验证，而不是只 grep prompt。

### 4.2 已证实的下游

- `slow_cycle.py:1477` 的章末循环：cooling/carry-forward 改 active_attention、更新 knowledge_activations、promotion 改 reflective_frames；下一章 consolidation 又读这些状态。
- `slow_cycle.py` 章末 optional reaction 会追加到 reaction_records；这是独立于 Unit Product 的旧副作用。
- `evaluation.py:252` 把全部 reaction records 归一化；`:332` 读取 reflective_frames（还 fallback reflective_summaries）；`:483` 开始的 integrity 检查 reconsolidation 链。
- `runner.py:3559–3634` 把更新后的 bundle 写盘并进入 full checkpoint；`resume.py:943` 等读取这些键。
- Product/UI 消费器直接调用 slow_cycle 内的确定性 projection helper，而不是消费其 LLM consolidation 返回值。默认 Pack 从 complete Product 取数据。

已有《悉达多》产物进一步证明旁路：reaction_records 有 **210** 条，其中 `reaction_anchor=207`、`chapter_end=3`；Product/Pack 是 **207** 条。reflective_frames 六个列表和 active_items 均为空，但 consolidation 仍发生 15 次。这个样本支持“停用有直接降本价值”，不支持“所有书都没有 promotion”或“旧评测数值一定完全不变”。

**建议处置：** D1 批准后移除 consolidation/promotion 调用及其纯专属状态写入；保留 Product 生成和 compatibility helper。新实验评分输入对齐 Product-accepted Marginalia，历史 normalized 结果保留原样并标清旧口径，禁止悄悄回写历史分数。

## 5. 需要用户决策

| 编号 | 问题与选项 | 建议 |
| --- | --- | --- |
| D1 | 是否将仍执行但不进入核心 prompt/Product 的 slow cycle 纳入删除？A：按严格双条件只删死代码；B：批准关闭 consolidation/promotion 及章末 optional reaction，再删专属 stores/评测字段 | **B**。这是运行行为变化，不宣称无消费者；直接省模型调用。同步将新评测输入限定为 Product-accepted Marginalia，旧结果不重算 |
| D2 | 清理前 v2 checkpoint 的支持范围？A：仅新 run + 清理后 resume，旧 run 显式拒绝并用 tag 恢复；B：保留最小的一次性 v2 checkpoint 读取，忽略已退役 store，仍以 Product commit 重建；C：广泛兼容所有旧 runtime | **B，仅 Product-backed v2**。既验证过的整书中断恢复资产不应轻易丢失；没有 Product commit 的历史输出只读归档，不从 reaction 推断新 Product。若维护成本超出轻量范围，改 A，不能默认 C |
| D3 | 旧书库/API 与 legacy backfill 的边界？A：保留旧书库只读显示/用户 marks，去掉自动回填与旧 reader resume；B：旧目录完全退出当前 Library，仅在 tag checkout 查看 | **A**，符合前端暂不处理。停止自动 backfill 本身在启动路径上，作为单独批准项；若仍依赖它补封面或定位，保留相关只读工具，避免删坏现存书 |
| D4 | 是否本步顺带复用 survey？A：本步不动；B：同 source digest + prompt/policy version 的同一 reading 复用 survey，并固定 resume reading_plan；C：直接换规则 survey | **B，但独立小提交**；不做通用缓存系统。校验失配才重算，不能只看文件存在。C 会改变阅读范围，留到另一个设计/实验任务 |
| D5 | 旧 eval 中与未来实验重叠的资产？A：文件名旧就整删；B：删旧执行/双机制分支，保留切分样本/rubric、human-note 导入、当前 memory/re-entry 诊断；C：等待新评测环路建成再动所有旧 harness | **B**。`eval/subsegment` 的旧 iterator runner 不保留，boundary 样本/rubric 可保留；四个旧 comparison 文件按函数用途裁剪。请确认是否仍使用 `eval/compare_highlights.py` 的 Markdown/Google Books 批注输入 |
| D6 | 对外兼容选项如何退役？A：`iterator_v1`、`both`、旧 book_analysis 执行选项明确报“已退役”；B：自动改为 v2；C：保留旧机制 | **A**。不要 silently reroute。CLI help/env 文档/test 与 job 恢复错误消息同步；暂保留旧 API enum/历史记录解析，避免改前端契约 |
| D7 | 备份和未推送分支怎么保全？A：获授权后将 Annotation Hub 本地分支推 origin，并做仓库外备份；B：先 Git bundle 保全，暂不推，但不进入正式清理 | **A 才满足用户本次“全部已推送”前置要求**。需要指定/确认私有备份目标；tag 建在执行前最终 HEAD，不能只标本文审查基线。不要因另一个 worktree 分支未推而合并它 |

上述决策不会要求重新选择当前机制；iterator 的退役方向已经由本次任务给出。待回答的是依赖处理、已有数据可用性与轻量清理边界。

## 6. 预估效果与计数口径

### 6.1 文件/代码规模

统计仅计基线 tracked Python 文本行（含注释/空行），不计 Markdown、JSON、EPUB、运行数据、磁盘缓存；不是 SLOC，也不是已生成删除 diff。

| 组 | 整文件数 | 当前文本行 | 含义 |
| --- | ---: | ---: | --- |
| A1：iterator 专属执行文件 + adapter | 7 | 7,172 | 先解 eager import/eval/resume 依赖 |
| A2/A3/A4：dead v2 模块及两个 prompt | 5 | 1,088 | 不含 slow_cycle 混合文件中的函数级删除 |
| A5/A6/A7：6 个 temporary + 3 个历史脚本 | 9 | 6,040 | 不包含数据或报告 |
| A8/A9：旧 prompt/shim/search | 4 | 494 | shared.py 保留 |
| 上述代码小计 | **25** | **14,794** | 可审阅整文件候选清单 |
| 已识别的 10 个专属测试 | 10 | 3,206 | 删除旧能力的测试，不删共享契约测试 |
| 合计 | **35** | **18,000** | 审批和依赖裁剪后有望整体删除；不是整仓删完的保证 |

此外，四个旧 comparison 文件合计 6,608 行；`eval/subsegment` 5 个文件共 1,133 行。这两组**未计入确定删除量**，因 D5 需要保留可用资产。`slow_cycle.py`、`knowledge.py`、consolidation/promotion 两个 prompt 合计 2,020 行，也是混合/在用范围，不能全部计成收益。另有 schemas/resume/storage/CLI 的函数级剪裁与少量替代接线。

因此合理预期是：先拿到约 **1.8 万行、35 个整文件**的可核查删除范围，再依据 D1/D5 增加若干函数/文件；净减量应在执行 diff 后重算。移到共享位置的代码不算删除，保留测试与修复接线会抵消部分净减量。删除旧 reader、bridge、脚本本身对正常 v2 每书 LLM 次数贡献为 **0**。

### 6.2 每本书 LLM 节省

设 `C` 为实际完成章末 cycle 的次数，`P` 为实际 promotion candidate 总数，`R` 为相关结构修复/重试增加的调用。关闭 slow cycle 节省基础调用 `C + P`；实际 ledger/物理 attempt 节省还受 `R` 影响。章节总数含 auxiliary，不能直接等同于 `C`；resume 在章末写 checkpoint 前失败可能重复 chapter cycle。

本地已有《悉达多》验收账本：

`B/state/reading_product_live_acceptance/cpa_luna_xidaduo_full_book_20260903/book-output/_runtime/llm_standard.jsonl`

| node | 逻辑调用 | 物理 attempts | 已知 tokens | 累计 duration_ms |
| --- | ---: | ---: | ---: | ---: |
| chapter_zone_classifier | 48 | 48 | 80,308 | 189,925 |
| ingest | 171 | 173 | 1,138,652 | 2,029,988 |
| digest | 91 | 98 | 897,757 | 2,287,837 |
| chapter_consolidation | 15 | 15 | 77,614 | 344,128 |
| 合计 | 325 | 334 | 2,194,331 | 4,851,878 |

- 89 个 Product Units；16 章 BookDocument，15 个读完的章末 cycle。一个 Ingest 失败 usage 未知；tokens 是已知总量。
- 关闭本样本 slow cycle：**15 次逻辑/物理调用、77,614 tokens、约 5.74 分钟累计调用耗时**，分别约占 4.62%、3.54%、7.09%。耗时是 ledger duration 累加，不能当真实 wall-clock 加速保证，更不能推出固定人民币节省。
- 该样本 promotion/reconsolidation 为 0；其他书的 promotion 数不能从本样本外推。
- 48 次 survey 对应 16 章在 parse/read/resume 三次入口执行。如果 D4 复用成功，同一输入从三轮变一轮，可再少 **32 次基础 survey 调用**；这是单独可选优化，不计入纯删除收益。不保证省掉不同 prompt/source/policy 下本应重算的 survey。
- 当前 Unit Memory 来自已生成 Understanding 等数据，删除某个“memory”名称不意味着省一个摘要模型调用。后续真正的大项仍是 Ingest/记忆上下文消融与模型/缓存实验；本步不提前改它们。

## 7. 执行前安全步骤

### 7.1 Git 与工作树

本轮 `git ls-remote --heads origin` 的实际结果只有：

| 分支 | 本地/远端状态 |
| --- | --- |
| main | 本地与 origin 均为 `cdd987e…` |
| codex/annotation-pack-v0 | 本地与 origin 均为 `02b7b72…` |
| codex/annotation-hub-v0 | 本地 `e323902…`，远端无对应 head；28 个提交不被当前远端 refs 覆盖 |

另一个 worktree 位于 `/Users/baiweijiang/.codex/worktrees/2096/reading-companion`。本轮未操作其文件、分支或工作进程。

正式删除前依次完成：

1. 列出每个 worktree 的 dirty/untracked、所有本地 heads、stash 和仅 reflog 可达的重要提交；本轮只核验了 heads/远端覆盖，不声称已证明所有历史本地提交都安全。
2. 经批准处理未推分支，逐一核对远端 OID/可达性；不要 `push --all` 把未知分支盲推。不要自动 merge/rebase Annotation Hub。
3. 同时保存仓库外 Git bundle（覆盖所有 refs；单独处理未提交工作、stash/重要 reflog 引用），验证 bundle 可读；它是额外保险，不替代“远端已推”的要求。
4. 在最终清理前 HEAD 创建 annotated tag，例如 `pre-cleanup-2026-11`，确认未重名；获授权后推 tag，并核对远端 peeled commit。
5. 从该点建立 `codex/lightweight-cleanup-step0`。不要把本轮方案写入误认作已经执行的清理记录。

### 7.2 仓库外数据备份清单

根 `.gitignore` 忽略整个 `B/state/`；后端 ignore 还忽略 output、eval/runs、packet archives 等。Git/tag 保存不了这些本地数据。

以下是本轮磁盘普通文件计数和逻辑字节大小（MiB；不是压缩后大小，执行前重扫）：

| 路径（B/ 下） | 文件数 | MiB | 原因 |
| --- | ---: | ---: | --- |
| state/library_notes | 10 | 2.94 | 原始真人批注与归一化记录，最高优先级 |
| state/dataset_build | 990 | 30.76 | notes/source catalogs、构建/对齐/provenance |
| state/eval_local_datasets | 1,044 | 113.98 | 活跃和历史私有数据集、note cases、source spans |
| state/library_sources | 65 | 148.62 | 稳定源 EPUB 与 source 身份 |
| state/library_inbox | 8 | 2.95 | 尚未规范导入的来源 |
| state/experiments | 209 | 14.30 | 全书/上下文 A/B/C 等生成与人工审阅证据 |
| state/reading_product_live_acceptance | 186 | 20.75 | Product/Pack/断点恢复实证和 cost ledger |
| state/job_registry | 820 | 21.40 | job 历史和恢复定位 |
| state/jobs | 42 | 0.87 | 产品 job 状态 |
| state/llm_cache_experiments | 6 | 0.03 | 后续缓存研究已有资产 |
| output | 852 | 1,415.85 | 书库源/产物、Product Store、checkpoint、用户 marks |
| eval/runs | 21,561 | 3,298.48 | 原始评测结果、调用日志、报告和 review packets |
| eval/review_packets/archive | 1,777 | 20.92 | 部分 tracked、部分 ignored；完整备份 |
| data | 39 | 4.52 | 本地输入和评测来源 |

重点核对活跃包：`state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260629_source_norm_v1_2_unique_notes/`。必须包含 `manifest.json`、`segments.jsonl`、`note_cases.jsonl`、`segment_sources/`、`fresh_parse_outputs/`、人工可读审阅和 validation report，不能只备份两个 JSONL。

上述约 5.1 GiB 是已列目录，不是完整 state 上限。还应盘点 `state/coordination`、`source_normalization_probe`、其他 observability smoke/历史实验、`uploads` 中独有源文件、外部笔记路径。推荐对非缓存业务数据做完整私有快照，再单独列出可再生成缓存的排除项。不能按目录名含 `tmp` 就自动丢弃。

备份必须有相对路径、大小、SHA-256 清单；在独立临时目录完成恢复演练：158 note cases/5 segments、原始批注 catalog、源 EPUB digest、一个 Product publication、一个 checkpoint/SQLite Store 能被只读解析。SQLite 备份需在确认无写入后包含 WAL/SHM 或用一致性 backup，不能只复制主 `.sqlite` 文件。先确认活跃工作，不能擅自终止别的任务。

本轮看到 `active_jobs.json` 的 jobs 为空，但时间戳为 2026-09-13，**不足以证明现在没有运行任务**。执行前核对 job lease/进程与其他 worktree。秘密配置不写进备份清单内容、不进 git；若需要备份凭据，只走用户指定的受保护位置。

## 8. 建议执行顺序与独立提交

所有批次均在用户批准清单/D1–D7 后执行；每批只 stage 相关文件并独立 commit，不自动 push。下面是未来验证计划，**本轮没有运行这些会生成文件/可能写状态的测试或脚本**。

### Batch 0：恢复能力与基线证据

- 完成 tag、远端确认、私有数据备份/恢复演练。
- 固定当前 Product-backed v2 微型 EPUB 输入、模型替身输出、source digest、U/R/M、Product/Pack bytes 或去除 run identity 后的语义比较方式。
- 运行现有测试以分离预先存在的失败；记录 current/eval dataset 指针，不启动付费模型评测。

### Batch 1：先保护真人批注评测与共享导入

- 移除 user-level runner / completed-output reuse 中的 iterator dependency，保留当前匹配/judge/数据读取；需要复用的少量纯匹配 helper 可就地保留或小范围拆出，不创建新框架。
- 确认 import/CLI `--help` 不需要旧 reader；保留源解析、语言、gateway、API 共享代码。
- 验证：`tests/test_marginalia_note_precision_recall.py`、`test_run_user_level_selective_comparison.py`、`test_user_level_selective_v1_manifest.py`、`test_user_level_selective_orchestrator.py`、`test_human_notes_guided_dataset.py`、notes 相关测试；用固定可控 judge 替身验证同样输入得到相同匹配结果，零外部请求。

### Batch 2：退役 iterator 执行能力、孤立 bridge/旧 prompt/一次性脚本

- 按 A1–A10 剪旧 reader，改 registry、CLI/config 和 job 旧 resume 错误路径；保留当前文件契约/API enum。
- 旧 subsegment/comparison 执行器按 D5 结果处理；通用数据集/评分资产不删。同步 shell/docs 中旧入口引用。
- 删除旧测试中已经没有产品承诺的断言；保留混合文件的共享测试，不用删除测试掩盖 retained behavior 失败。
- 验证：backend pytest collection 全量、`test_reading_runtime.py`、`test_reading_runtime_artifacts.py`、`test_library_api.py`、`test_public_contract.py`、`test_llm_gateway.py`、`test_iterator_parse.py`/`test_iterator_frontend_artifacts.py` 中保留的共享用例、`tests/annotation_pack/test_epub_document.py`。CLI parse/read help 与 explicit retired key/error 断言。`test_iterator_selection.py` 和 `test_iterator_mode_validation.py` 是混合测试：保留 storage 命名与当前 CLI 拒绝 plan 的断言，仅剪 iterator 专属部分。

### Batch 3：经批准关闭 slow cycle、收窄当前 state

- 先移除 chapter-end 模型支路，保留章完成、checkpoint、compatibility projection 和 finalization；再剪 active_attention/reflective/knowledge/recon 专属 schema/store/admission/audit 字段。
- 按 D2 处理当前 checkpoint：Product commit 必须继续主导恢复；不能重建一条“迁移旧 reaction 为 Product”的路径。
- 更新 normalized eval 的新实验输入来源/口径，避免继续评分非 Product 的章末 reaction。历史 bundle 保留，版本/来源明确。
- 验证：`test_attentional_v2_reading_product.py`、`test_attentional_v2_resume.py`、`test_attentional_v2_llm_calls.py`、`test_attentional_v2_state_projection.py`、`test_attentional_v2_state_ops.py`、`test_attentional_v2_unit_memory.py`、`test_attentional_v2_evaluation.py`、`test_attentional_v2_observability.py`；mixed `test_attentional_v2_slow_cycle.py` 的纯投影测试必须留下。
- 增加有意义的隔离断言：相同模型替身输出下核心 prompt/U/R/M/Pack 相等；章末不再出现 slow-cycle LLM node；Product commit 后、private settlement 前崩溃可恢复且不重调已提交 Unit。

### Batch 4：可选 survey 去重和启动回填收尾

- D4 批准才复用 survey：source/prompt/policy fingerprint 命中复用，resume 固定原 plan；变更时明确失效。不要搭建通用缓存/改规则 survey。
- D3 批准才移除启动 backfill；显式验证旧书只读、用户 marks、封面/资源/章节页面仍正常。不要碰原始 output 数据。
- 验证：`test_attentional_v2_survey.py`、`test_reading_runtime.py`、`test_library_api.py`，parse→read→resume 的 classifier 次数和 plan 一致性；launcher `bash -n`。旧前端保留时用现有 e2e 验证一个现存书和一个新 Product 书。

### Batch 5：文档归档与全量验收

- 按第 3.2 节移动文档并修引用；decision-log 追加本次退役/状态边界决策，保留全部既有条目。
- 同步 root/backend AGENTS、README、current-state、registry.md/json、mechanism catalog/v2 文档、lifecycle/state-aggregation、reader-evaluation。仅确有 API 变化时更新 API contract/integration；默认本步不改 public wire。
- 不创建新的 tracked runtime 中间目录；若验证生成新路径，同批补 `.gitignore`。不 force-add 私有 note/source 数据。
- 依次运行以下验收，失败先归因，不以减少测试范围交付：

```bash
# 在仓库根运行；make test 包含后端 pytest、前端 typecheck/build、agent-check。
make test

# 如需分批单独验收 wire，可先分别运行；最终 make test 不必无理由重复。
make reading-product-contract-check
make annotation-pack-contract-check

# 后端目录：只检查已存在的 ledger/catalog，不重新评测。
cd reading-companion-backend
.venv/bin/python scripts/update_evaluation_run_ledger.py --check
.venv/bin/python scripts/update_evaluation_catalog.py --check
```

尤其保留并通过 `tests/reading_product/test_offline_whole_book_lifecycle.py`：真实 Tiny Reader EPUB + 确定性模型替身、提交后崩溃/恢复、complete publication、Pack 生成和独立校验。该现有测试是在同一测试进程中模拟故障与重新打开 Store；真正的跨进程重启验收仍需独立验证，不能把它当现成证据。真实 LLM 全书验收不属于本轮方案排查；执行阶段若要新增付费/耗时跑书，另定预算与证据目的。

## 9. 主要风险与验证

| 风险 | 具体失误 | 验证/防护 |
| --- | --- | --- |
| 混合目录误删 | iterator parse/storage/llm_utils 仍服务 v2，包 `__init__` 又有 eager imports | API/CLI/eval import smoke + shared parser/identity/gateway 测试；按符号/消费者剪，不按目录名 |
| 兼容投影误删 | slow_cycle 中 pure helper 被 Product/UI 使用 | 同一 Product 输入的章投影/marks/Pack 回归；JSON 字节或语义结果稳定 |
| 评测悄悄失效 | note precision/recall 顶层依赖旧 runner；删 iterator 后 import 就失败 | Batch 1 必须先独立通过；固定 note cases/匹配对/aggregate，使用 judge 替身 |
| 把旧评分当新基线 | normalized eval 210 reactions 对 Product 207 | 新实验显式 Product scope；历史报告只归档不回填；记录来源/version |
| checkpoint 不可用或重复计费 | 删除 store key 后旧 v2 恢复崩溃，或 cursor 提前 | Product commit 边界故障注入、same reading_id、无重复 Unit/LLM；拒绝不支持的历史 run |
| survey 改变阅读范围 | 去重只判断文件存在，或 resume 重新随机分章 | source/prompt/policy fingerprint、冻结 reading_plan、auxiliary/mainline/deferred/partial completion 测试 |
| 扩大成重构 | 为清空 iterator 目录搬整个 parser/模型/存储层 | 共享代码保留现位置；只做退役所需 import/分支修复，目录重排留给后续拆仓库 |
| 历史/私有数据丢失 | tag 无法保存 ignored 数据；SQLite 复制不一致 | SHA-256 清单、备份恢复演练、停写一致性、逐分支远端核验；清理源码不顺带删除 output/state |
| 日志“变少”却不可观测 | 删除整个 observability 或把 unknown usage 当零 | 保留 llm logical/physical calls、usage coverage、成本 unknown、retrieval degradation、checkpoint/run IDs；只去掉退役节点字段 |
| 不明外部使用方 | repo 内无引用不等于外部无人调用 CLI/env/legacy export | D3/D5/D6 明确兼容边界，显式 retirement 错误；Annotation Pack 本轮不退役 legacy adapter |

## 附录：整文件计数清单

以下路径相对 B；最终执行应将用户批准后的清单展开为精确删除 diff，不使用通配 `rm`。

### 25 个代码文件（14,794 行）

```text
src/reading_mechanisms/iterator_v1.py
src/iterator_reader/iterator.py
src/iterator_reader/reader.py
src/iterator_reader/book_analysis.py
src/iterator_reader/policy.py
src/iterator_reader/markdown.py
src/iterator_reader/mechanism_spec.py
src/attentional_v2/bridge.py
src/attentional_v2/retrieval.py
src/attentional_v2/intake.py
src/attentional_v2/prompts/bridge_resolution.py
src/attentional_v2/prompts/reconsolidation.py
scripts/temporary/active_benchmark_full_audit_20260421.py
scripts/temporary/attentional_v2_f4a_oneoff_quality_audit.py
scripts/temporary/attentional_v2_window_ab_compare_20260421.py
scripts/temporary/long_span_vnext_partial_memory_quality_judge_20260423.py
scripts/temporary/longspan_rejudge_audit_20260422.py
scripts/temporary/memory_quality_probe_audit_source_map_20260503.py
scripts/await_lane_a_then_run_private_library_cleanup_round3.py
scripts/private_library_cleanup_round3.py
scripts/run_source_normalization_v1_1_multibook_validation.py
src/prompts/legacy.py
src/prompts/templates.py
src/prompts/capabilities/book_analysis.py
src/tools/search.py
```

### 10 个专属测试文件（3,206 行）

```text
tests/test_iterator_checkpoint.py
tests/test_iterator_policy.py
tests/test_iterator_reader.py
tests/test_iterator_markdown.py
tests/test_iterator_v1_prompts.py
tests/test_iterator_v1_normalized_locator.py
tests/test_book_analysis_mode.py
tests/test_book_analysis_prompts.py
tests/test_attentional_v2_bridge.py
tests/test_f4a_quality_audit.py
```

本轮未改 current-state/registry/decision-log：本文是待审批排查交付物，没有改变已实施机制、任务执行状态或正式设计决策。上述持久状态和决策更新列在实际清理批次内，避免把尚未批准的提案登记为已经发生。
