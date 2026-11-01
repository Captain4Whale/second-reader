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

## 后续批次

尚未执行。
