# 阅读机制演进与第 0 步清理

`iterator_v1` 使用 section/subsegment 遍历和旧 reader memory。`attentional_v2` 后来通过共享 parse/runtime 边界接入，并成为默认机制；其当前循环为程序构建预览 → Ingest 选择下一 Unit 并提出 Unit Memory 检索 → 程序检索/选择 Understanding → Digest 产出 Understanding、Response、Marginalia → 确定性 Product 提交及派生状态持久化。Unit Memory 由已接纳 Unit 派生，近期窗口保留刚读过的 Understanding；它们承担当前跨 Unit / 跨章上下文接续。

2026-03-23 的 Phase 6 引入 slow cycle：chapter_consolidation、reflective_promotion 和 reconsolidation。其目标包括跨章连续性、理解的沉淀与修订，以及对既有反应的 append-and-link 历史记录。执行轨迹、当时的设计和 DEC-025 保留了这一阶段的定义。此后 prompt-facing 上下文转向 Unit Memory 检索 + 近期窗口；核心 Ingest / Digest prompt 不再读取 slow cycle 的状态产出。

slow cycle 的输出不再进入核心 Ingest / Digest prompt，只被 slow cycle 自身、checkpoint 和旧评测消费；本次删除该支路，保留 Product/UI 使用的确定性投影函数。

2026-09-03《悉达多》整书技术验收 run `cpa_luna_xidaduo_full_book_20260903` 的 ledger 有 325 次逻辑调用；其中 chapter_consolidation 为 15 次，共 77,614 token（约 7.8 万），reflective_promotion 无调用。该 run 的 reflective_frames 六个列表均为空。以上为此 run 的实测成本/状态事实，不外推到其他书；删除该支路后同等章节调度不再产生这 15 次章末调用。章末完成状态、checkpoint、Product finalizer 和 Pack 的确定性路径保留。

第 0 步删除 iterator 执行/双机制分支与旧 checkpoint resume，只支持清理后新 run 的恢复；旧书保持可显示，启动 backfill、前端及 Annotation Pack 不在本次改动范围。真人批注数据、note recall/precision 分析、当前记忆诊断和成本观测继续保留。新评测只消费 Product-accepted Marginalia，历史数字不回写。0.3498 / 0.1232 来自 April 19 run 的 April 16 203-case 包，见[只读核查](tasks/lightweight-cleanup-step0-historical-evidence-2026-11-01.md)。

历史证据：

- [decision-log](history/decision-log.md)：DEC-025、DEC-103、DEC-110、DEC-158 及本次 DEC-160；既有条目完整保留。
- [Phase 6 执行记录](archive/pre-cleanup-2026-11/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md)、[旧机制文档](archive/pre-cleanup-2026-11/backend-reading-mechanisms/iterator_v1.md)、[清理前 v2 文档](archive/pre-cleanup-2026-11/backend-reading-mechanisms/attentional_v2-pre-cleanup.md)。
- 本地《悉达多》证据：`reading-companion-backend/state/reading_product_live_acceptance/cpa_luna_xidaduo_full_book_20260903/book-output/_runtime/llm_standard.jsonl`，及同一输出目录 `_mechanisms/attentional_v2/runtime/reflective_frames.json`。
- 清理前代码：annotated tag `pre-cleanup-2026-11`（已推 origin）；全 refs bundle 和业务数据备份在 `~/Backups/second-reader-pre-cleanup-2026-11/`。归档映射见 [move-map](archive/pre-cleanup-2026-11/move-map.json)。

后续前置项（本次未实现）：**resume 时固定原 reading_plan，避免重新 survey 改变阅读范围**。
