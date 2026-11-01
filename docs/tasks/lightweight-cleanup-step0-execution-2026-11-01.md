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
