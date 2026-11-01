# 第 1 步前置任务执行记录

范围：chapter_planner 命名、阅读计划冻结、显式检索与运行配置证据。分支 `codex/step1-prereqs`，起点 `4bc7ee0`；不 push，不调用真实模型、不跑真书，不修改历史结果、评测指标、数据集或 judge。

## A. 改名前输出 / 消费者盘点

对 `src/`、当前 `eval/`、`scripts/`、测试和 API/前端引用进行静态检索，并沿 runner 调用核对。下列删除只针对新产物，不删除已有业务文件。

| 输出 | 当前消费者 | 处置 |
| --- | --- | --- |
| `chapter_map[].chapter_id / chapter_zone` | runner 的队列、章节状态、完成判定及 fallback 计划 | 保留 |
| `reading_plan.mode / mainline_chapter_ids / deferred_chapter_ids` | `_reading_plan_from_survey`、`_scheduled_chapter_ids`、`_apply_reading_plan_statuses`、`_reading_queue_stage_for_chapter`、最终完成判断 | 保留 |
| `title / chapter_number / level / heading_text / pivot_headings` | 分类器 sample、book_frame TOC、相邻标题 | 保留，chapter_map 同时用作分类 sample |
| `opening_sentences / closing_sentences`（含 `sentence_id / text`） | 分类器 sample（每端最多两句） | 保留输入，不能作为死输入删除 |
| `first_sentence_id / last_sentence_id` | 仅旧 revisit builder 与测试 | 删除新输出 |
| `structural_role_guess / role_confidence` | 无当前消费者（共享 parser 的同名 role_confidence 是另一字段） | 删除 |
| `zone_confidence / zone_reason` | 分类器返回值，落盘后无运行消费者 | 保留分类器协议，删除 chapter_map 冗余输出 |
| `initial_motif_seeds` | 仅 `_motif_seeds` → `build_revisit_index` 与测试 | 删除 |
| `revisit_index`、`chapter_boundaries`、`opening_sentence_ids / closing_sentence_ids`、`motif_seed_index` | 仅生成、artifact map、初始化和测试；没有当前读者 | 删除新输出及专属 helper |
| `book_frame` | 分类器 prompt，含书名/作者/语言/章节数/TOC | 保留分类输入 |
| `status` | runner `_artifact_summary` | 保留，改为计划就绪含义 |
| `survey_caveats` | 无运行消费者 | 删除 |
| `schema_version / mechanism_version / generated_at / policy_snapshot` | 产物身份与配置追溯；D 补全严格版本校验 | 保留 |
| `survey_mode: orientation_only` | 当前代码中只有测试传入，没有生产 policy 定义或分支读取 | 改为明确的 `chapter_planning_mode: body_first` |
| prompt manifest | 当前 prompt 审计/诊断 | 改名；成本 ledger node `chapter_zone_classifier` 保持 |

没有发现需要修改公开 API 或前端的 survey 字段；`mechanism_artifact` 是内部 ParseResult/ReadResult 数据。

## F. 改前配置证据盘点

- `_runtime/llm_standard.jsonl` 已逐调用记录 provider / contract / model、profile、node、目标选择、调用次数、耗时、usage/cost；采样参数尚不完整。
- 机制 `internal/prompt_manifests/` 已记录分类、Ingest、Digest 版本与 prompt；需在运行结果中提供统一版本索引。
- `runtime/memory_retrieval_config.json` 已记录 requested mode、embedding provider/model/dimension；逐查询 trace 已有 effective_mode 与 degradation_reason，但没有运行级实际模式及查询降级计数。
- reader_policy / runtime shell 已有 policy_version；缺少章节计划输入 fingerprint 与运行代码 commit。
- 后续只扩展这些已有记录及 normalized eval bundle，不引入通用缓存/配置框架。

## 验证与进度

A 已完成；B 改名及死输出清理已完成。改前封网全量测试 1747 passed / 2 failed（原有 monkeypatch）；改名前后固定 transport 的阅读计划、核心 prompt、Product U/R/M、Pack、固定 judge 匹配完全一致。离线基线位于 ignored `reading-companion-backend/state/step1_prereqs/`。模型 transport 使用固定替身，socket 连接被封锁。B–F 待实施。

B 命名：`survey.py` → `chapter_planner.py`；`build_book_survey` → `build_chapter_plan`；`_classify_chapter_zone` → `classify_chapter_zones`；writer → `write_chapter_plan_artifacts`；`SurveyMap` → `ChapterPlan`；`survey_map.json` / `survey_map` → `chapter_plan.json` / `chapter_plan`；`survey_status` → `chapter_planner_status`；prompt `survey_chapter_zone` → `chapter_zone`，submit tool 同步。成本 ledger 的 node 不变。

## C. 既有测试修复

两项失败均为测试 monkeypatch 入口过期：生产分类器已使用协议中立的 `invoke_structured_output`，测试仍替换不存在的 `invoke_structured_output_tool`，在模型调用前即报 AttributeError。只修测试；成功分类和错误时规则 fallback 的功能未改。

C 封网全量后端：1749 passed（改前 1747 passed / 2 failed），日志 `state/step1_prereqs/c-tests.log`。

## D. 计划冻结

`chapter_plan.json` 带源文件 SHA-256、分类 prompt 版本、policy 版本/内容摘要及整份计划 fingerprint。parse/read 在身份一致时复用；缺失/变化时仅非 resume 允许显式生成，原因写入计划 generation 与既有 diagnostics/events.jsonl。resume 校验失败即报错，不改写计划；checkpoint 绑定原计划 fingerprint。

离线 Tiny Reader（2 章）实际走 parse → read → Product 提交后故障 → resume：分类器总计 2 次，恢复前后计划文件逐字节相同。prompt / policy / source 逐项变更：resume 零新增调用且拒绝；非 resume 从 2 次增到 4 次并记录原因。缺失和内容篡改均拒绝恢复。专项 99 passed。

## E. 显式检索条件

内部配置 / CLI 支持 off、text-only（落盘规范名 text_only）、hybrid；HTTP enum 与前端保持原契约。评测必须在 mechanism_config 或 `READING_MEMORY_RETRIEVAL_MODE` 声明模式；复用 persist_normalized_eval_bundle 标记识别评测，并支持内部 evaluation_run 标记。hybrid 评测启动时校验 sqlite-vec、Ollama 模型及维度；查询或索引中途降级同样失败，不被产品的宽容异常处理吞掉。普通产品默认 hybrid，可降级；配置累计 actual_modes、query_count、query_degradation_count、index_degradation_count 和醒目 warning，逐查询 trace 保留 embedding model / 实际模式 / 降级次数。无 recall 或无 prior units 不算降级查询。resume 按 append-only trace 恢复计数。

专项 123 passed：包含 off/text-only 零 embedding、hybrid 缺模型失败、就绪后故障的产品降级/评测拒绝及精确计数。已有向量不可用测试改为明确模拟 unavailable，取消对本机 Ollama 状态的依赖。
