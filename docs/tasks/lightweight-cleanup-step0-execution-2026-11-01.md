# 第 0 步轻量清理执行记录（2026-11-01）

按审阅后的 D1–D7 执行 Batch 0 → 1 → 2 → 3 → 5，各批独立提交。审计报告见 [排查报告](lightweight-cleanup-step0-audit-2026-11-01.md)。用户批准的执行指令优先于报告建议。

## 边界与待办

- 删除 iterator 执行能力和 slow cycle 模型支路，保留共享解析、Product/UI 确定性投影、旧书只读、启动 backfill、Annotation Pack、旧前端、真人批注评测和成本观测。
- 仅支持清理后新 run 的 resume；旧 checkpoint 显式提示 `pre-cleanup-2026-11`，不迁移。
- 新评测只消费 Product-accepted Marginalia，历史结果不重算不回写。
- 不执行 Batch 4。第 1 步前置待办：**resume 时固定原 reading_plan，避免重新 survey 改变阅读范围**。
- 演进说明采用用户核准表述：“slow cycle 的输出不再进入核心 Ingest / Digest prompt，只被 slow cycle 自身、checkpoint 和旧评测消费；本次删除该支路，保留 Product/UI 使用的确定性投影函数。”
- 本轮不 push 分支；只推清理前 annotated tag。

## Batch 0：安全步骤及基线

- 起点 main HEAD：`cdd987edadd10cac3b1d199c8c094fe6d22f6430`。
- tag `pre-cleanup-2026-11` 已推 origin 并核对 peeled HEAD；tag object `39b9dcd42fa3029aacc55324d22fc0bec75f6ce8`。
- 工作分支：`codex/lightweight-cleanup-step0`。annotation-hub 分支未推送，worktree 未删除。
- 备份：`~/Backups/second-reader-pre-cleanup-2026-11/`；`all-local-refs.bundle` 包含全部 14 refs，verify 通过；`backend-business-data.tar` 包含完整 state、output、eval/runs、eval/review_packets、data（目录整体包含 SQLite/WAL/SHM）。
- 备份前检查进程、后台 job registry 和 lsof：无业务目录写入者；旧 watchdog running 记录对应 PID 已不存在。
- 归档抽查：活跃数据集 158 note cases / 5 segments 可读；10 个 library_notes 文件在；《悉达多》ledger 325 条在。
- 后端 `make test` 阶段：1885 passed / 9 failed（68.32 秒）；后续阶段因 pytest 失败未继续，已分别运行。
- 前端 typecheck/build：通过，原有 bundle size 提示。
- 独立 `make agent-check`：Product/Pack/schema/生成副本/契约测试通过；文档 traceability 检查有既有缺失 acceptance_ref、失效证据路径及重复 DEC-066、DEC-079。完整原始输出保留在下述基线路径，后续比较新增项。
- `tests/cleanup_probe.py` 在 transport 层替换模型、封锁 socket；真实 prompt/gateway/ledger/Product/finalizer/Pack 路径。固定 judge 匹配及核心 prompt/U/R/M/Pack 两次运行完全相同。
- 本地证据：`reading-companion-backend/state/cleanup_step0/batch0/`；副本置于上述外部备份目录的 `batch0-evidence/`。不提交私有数据或生成运行产物。

### 既有后端失败

```text
FAILED tests/test_attentional_v2_bridge.py::test_bridge_resolution_writes_manifest_and_keeps_search_rare
FAILED tests/test_attentional_v2_bridge.py::test_bridge_resolution_declines_generic_bridge_without_specific_attribution
FAILED tests/test_attentional_v2_bridge.py::test_run_phase5_bridge_cycle_materializes_anchor_state
FAILED tests/test_attentional_v2_minimal_eval_inventory.py::test_lane_a_distinguishes_active_dataset_from_formal_evidence_dataset
FAILED tests/test_attentional_v2_slow_cycle.py::test_reconsolidation_appends_later_reaction_without_mutating_earlier_one
FAILED tests/test_attentional_v2_slow_cycle.py::test_run_phase6_chapter_cycle_applies_cooling_promotion_and_optional_reaction
FAILED tests/test_attentional_v2_survey.py::test_build_book_survey_uses_llm_zone_classifier_when_available
FAILED tests/test_attentional_v2_survey.py::test_build_book_survey_falls_back_when_llm_classifier_errors
FAILED tests/test_f4a_quality_audit.py::test_case_target_assignments_stay_balanced
```

## Batch 1：真人批注评测入口

- 移除 user-level runner / completed-output reuse 对 IteratorV1Mechanism 的导入和执行分支；默认仅 attentional_v2，iterator_v1 / both 在数据访问前明确报已退役。
- orchestrator 的完整机制集合改为当前机制，历史结果匹配和分析保持可读；未修改 compare_highlights.py。
- 验证：主要评测测试 45 passed；library notes / human-note manifest 11 passed；CLI help 通过；固定 judge 匹配结果和核心 prompt/Product/Pack 与 Batch 0 完全一致，socket 封锁，无外部请求。无新增失败。
- 本地证据：`reading-companion-backend/state/cleanup_step0/batch1/`。

## Batch 2 前暂停：报告漏列的依赖

依照用户停止条件第 4 条，暂停后续清理。尚未执行 Batch 2/3/5，尚未删除文件。

- `eval/attentional_v2/run_accumulation_evaluation_v2.py:34` 直接导入 IteratorV1Mechanism；`:268` 仍有旧执行器分支；`:1125` 和 CLI 默认 both。
- `scripts/orchestrate_accumulation_v2_eval.py:25` 导入上述 runner；`scripts/orchestrate_active_benchmark_eval.py:34` 调用其 orchestrator。
- 这条 target-centered accumulation v2 链不同于报告 K12 明列的 `run_accumulation_comparison.py`，报告未列出该依赖和对应编排/测试影响面。
- 待用户确认建议：纳入 Batch 2，保留当前 accumulation 数据/evidence/judge/运行能力，移除 iterator/双机制执行分支，补跑 `test_run_accumulation_evaluation_v2.py` 及对应 orchestrator 测试。未自行扩展实施。
- 历史 0.35/0.12 数据集/run id 核查与演进说明属于尚未执行的 Batch 5，暂无新结论。


## Batch 2：旧执行能力退役

用户已确认把漏列的 target-centered accumulation v2 / active benchmark 编排链纳入本批，保留当前评测与 judge，移除 iterator/双机制执行分支。

- 删除旧 reader/adapter、bridge/intake/retrieval、旧 prompt shim/book_analysis/search、已批准的一次性脚本及专属测试。保留 iterator 目录内共享 parse/storage/language/frontend projection。
- 旧 subsegment 和 excerpt/chapter/accumulation 双机制执行器退出；数据集、匹配、rubric 和历史结果分析仍在。当前 accumulation v2、memory/re-entry、runtime viability 只执行 attentional_v2。
- 旧机制、book_analysis 和旧 reader 专属 CLI 参数明确报“已退役”；API enum 不变。旧书仍可只读显示，旧 reader 不再自动/手动 resume；启动 backfill 未改。
- 全量后端：**1763 passed / 5 failed**，5 项均在 Batch 0 既有失败清单内；退役专属测试移除后原有 4 个失败随能力退出。
- 固定 judge / prompt / Product / Pack 对照通过；零外部请求。修改文件 F821 静态检查通过。日志位于 `state/cleanup_step0/batch2/accepted-tests.log`、`probe.json`。
- 本批没有实现 D4；接下来 Batch 3。

## Batch 3：退出 slow cycle，收窄当前状态

- 删除 chapter consolidation / reflective promotion / optional chapter-end reaction 模型支路及独占 prompt、state/store、checkpoint/eval 字段；slow_cycle.py 保留 Product/UI 确定性投影。当前 runner、观测和诊断不再 load/save active_attention / reflective_frames / knowledge_activations / reconsolidation_records。
- 当前 runtime schema / resume compatibility 升为 2，full checkpoint 带独立格式标识；旧 run/checkpoint 显式拒绝并提示历史 tag，不再自动清空/重跑。parse/read 的 continue 入口在 survey/运行状态初始化前拒绝旧 run。共享 canonical parse/provisioning 仍先解析输出位置。
- 新评测从 Reading Product 已接纳的 Unit/Marginalia 和源坐标构造输入，Understandings 用于 memory summary；私有 reaction ledger 追加的未接纳反应不会进入评测。历史结果及 Pack legacy adapter 保留，只读解释旧快照的 judge fixture 保留。
- 完整后端验证：**1744 passed / 3 failed**，仅剩 Batch 0 已有 inventory 漂移及两项 survey monkeypatch 失败。追加两个旧 run 入口保护测试后，resume 专项 **11 passed**。
- 相同模型 transport 替身下，固定 judge / 核心 Ingest、Digest prompt / Product U/R/M / Pack 与 Batch 0 完全相同；真实本地 ledger 不再出现 chapter_consolidation / reflective_promotion。socket 封锁，零外部模型请求。
- 章节完成、checkpoint warm/cold/reconstitution、Product commit 后故障恢复、finalizer 和 Pack 生命周期测试通过。没有执行 D4，也没有新增真实跑书。
- 证据：`state/cleanup_step0/batch3/accepted-tests.log`、`resume-tests.log`、`probe-final.json`、`probe-final.log`。静态 F821 检查通过。

## Batch 5：归档、版本核查与最终验收

- 118 个历史文档移入根/后端 `docs/archive/pre-cleanup-2026-11/`，逐项映射见根归档 `move-map.json`；另保留清理前 v2 文档完整快照。当前 approved Ingest/Digest/Unit Memory 设计、真人批注/切分资产、已有 review packet archives 留在原位。decision-log 原条目完整保留并追加 DEC-160；run ledger / evidence catalog 仅修移动后的定位引用。
- 同步 AGENTS、README、current-state、任务 registry、机制/生命周期/恢复/聚合/评测/API 文档；API enum 和前端契约不变。旧书显示和启动 backfill 不改。`eval/compare_highlights.py` 未改。
- [历史数字只读核查](lightweight-cleanup-step0-historical-evidence-2026-11-01.md)：`attentional_v2_user_level_selective_v1_active_rerun_20260419` 的 10 个 shard selection 均指向 April 16 的 203-case / 5-segment 包，aggregate 原值为 0.3498 / 0.1232。June 14 是 202 cases，June 29 当前指针是 158 unique cases。只修文档/静态 inventory 和相应漂移测试；未重算、回写原始数据集或历史 aggregate。
- 已写[中文演进说明](../reading-mechanism-evolution-step0.md)，采用用户核准的 slow-cycle 消费者表述，保留 Phase 6 日期、原意、当前上下文接续机制、15 次 / 77,614 token 实测及历史证据/tag。
- 遇到报告漏列的 `contract-check.sh → check-reading-mechanism-doc.py → iterator_reader/mechanism_spec.py` 依赖后，按停止条件暂停；用户确认纳入本批后，删除旧机制专属检查及调用项。其他契约检查保留。该脚本的“current default”标题原先实际指向 iterator 文档/常量。
- 最终 `make test` 后端：**1747 passed / 2 failed**（54.74 秒）；仅剩 Batch 0 两项已有 survey monkeypatch 失败。inventory 漂移在本批纠正；旧能力专属测试随能力移除。`make test` 遇 pytest 失败会短路，因此前端和 agent-check 分别补跑：前端 typecheck/build 通过（既有 chunk size 提示），Product/Pack/schema/生成副本/API/OpenAPI/前端静态契约检查通过。
- 文档 traceability 与 Batch 0 同为 **17 条既有告警**，无新增。清理删除的历史证据代码引用改为 `pre-cleanup-2026-11` tag 链接；归档 Markdown 相对链接检查无新增断链。ledger/catalog `--check` 通过。
- 最终证据目录：`reading-companion-backend/state/cleanup_step0/batch5/`。所有模型行为验证均使用固定替身；未启动付费评测或真实模型跑书。此批不因既有 survey 测试失败扩大到 survey 实现修复。

## 与原报告/执行指令的差异

- 按用户指令跳过 Batch 4，未实现 survey 去重、reading_plan 固定或启动 backfill 改动。
- 两处报告漏列依赖均先暂停并获得确认：Batch 2 的 accumulation v2 编排链；Batch 5 的旧机制文档检查链。除此之外没有自行扩大代码改动范围。
- 历史 recall 的核查结果是 April 16 的 203-case 包，而非问题中举例的两个 June 版本；据原始 selection/aggregate 修正文档，没有改历史结果。
- `make test` 未全绿：两项既有 survey 失败和 17 条既有 traceability 告警明确保留，不以跳过测试或降低检查标准消除。独立完成了被短路的后续检查。
- D4 待办：**resume 时固定原 reading_plan，避免重新 survey 改变阅读范围**，作为第 1 步重建评测前置项，已登记 `TASK-RESUME-READING-PLAN-FREEZE`。

## 最终规模与安全复核

- 相对 `pre-cleanup-2026-11`：实际删除 45 个文件，文档归档移动 118 个文件；无 Markdown 文档删除。代码/配置（`.py`、`.sh`、`.toml`、`.lock`）净减 **30,301 行**，不把归档移动计作删除收益。
- 最终再次确认远端 tag peeled HEAD 为 `cdd987edadd10cac3b1d199c8c094fe6d22f6430`；bundle verify 通过（备份时全部 14 refs）。annotation-hub worktree 仍在且未推送；本轮未推任何分支。
- Batch 0–3 commits：`d389338` / `021c65a` / `1b67553` / `cc253f8`；Batch 5 为本执行记录最后更新所在提交。最终 `agent-check-final.log` 与基线逐条对照，17 条既有追踪告警完全相同。
