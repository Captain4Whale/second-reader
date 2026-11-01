# 历史 note recall 来源只读核查

核查日期：2026-11-01。只读取 manifest、selection、aggregate 和 JSONL 行数；未重新跑 judge、未重算或回写历史结果。

| 数据集版本 | note cases / segments | 身份 |
| --- | --- | --- |
| `attentional_v2_user_level_selective_v1_repaired_20260416` | 203 / 5 | April 19 formal run 的实际输入 |
| `attentional_v2_user_level_selective_v1_repaired_20260614_source_norm_v1_2` | 202 / 5 | source-normalized 历史包 |
| `attentional_v2_user_level_selective_v1_repaired_20260629_source_norm_v1_2_unique_notes` | 158 / 5 | 当前 split manifest 选中的 unique-note 包 |

三版包都在 `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/`。June 14 本地 manifest 仍标 active；本次保留历史文件不回写，以 tracked split manifest 的 June 29 指针作为当前事实。June 29 有 210 条 raw covered rows，52 条作为 duplicate aliases，158 条唯一 case；不能把 202→158 当作同一评测样本的直接分数变化。

**0.35 / 0.12 属于 April 16 的 203-case 数据集，两者都不属于 June 版本。** run id 为 `attentional_v2_user_level_selective_v1_active_rerun_20260419`。十个 shard 的 `meta/selection.json` 都指向 April 16 包，各机制 case-id 并集各为 203。根 aggregate 原值：

- attentional_v2：32 exact_match + 39 focused_hit，203 cases，note_recall `0.3498`。
- iterator_v1：9 exact_match + 16 focused_hit，203 cases，note_recall `0.1232`。

证据（本地 ignored 原始数据已在仓库外备份）：

- [当前 split manifest](../../reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json)
- [历史 aggregate](../../reading-companion-backend/eval/runs/attentional_v2/attentional_v2_user_level_selective_v1_active_rerun_20260419/summary/aggregate.json)
- [历史 report](../../reading-companion-backend/eval/runs/attentional_v2/attentional_v2_user_level_selective_v1_active_rerun_20260419/summary/report.md)
- 同一 run 下 `shards/<source_id>__<mechanism>/meta/selection.json`（5 sources × 2 mechanisms）。

April 21 修复记录说明根汇总曾被单 shard recovery 覆盖，随后从十个完整 shard 恢复；本次读取的是现存完整根汇总。该结果仍使用当时的机制输出口径，不能作为清理后 Product-accepted Marginalia 的新基线。本次只同步 active pointer 文档和静态 inventory，不改变历史解读报告中的数字。
