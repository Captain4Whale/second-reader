# Eval-1 Full Active Evaluation Post-Slice8H: Playback Dossier

This dossier replays Eval-1 as a reading trace rather than as a score table. It is designed for human review of the product-facing reading experience: source window -> visible reactions -> note coverage -> callback/FVI audit -> probe-time scoring evidence -> scoring interpretation.

It is not a new eval run, not an evidence-catalog update, not product-quality proof, and not Long Span formal benchmark authority.

## How To Read

1. Open the dataset source window first for the book/window context.
2. Read the matching playback window page in order; every visible reaction from the Eval-1 run is listed.
3. Use the conditional Selective Legibility and Callback/FVI blocks only where they appear; local-only / non-target reactions stay compact.
4. At each Memory Quality probe, inspect the recorded probe-time digest fields before reading the score rationale; empty arrays, empty objects, and `null` values are shown as recorded rather than hidden behind a synthetic wrapper.
5. Use the final scoring interpretation to connect the trace back to the four metrics.

## Memory State Evidence Boundary

- `memory_quality_probe_snapshots.json` is the probe-time scoring evidence used by Memory Quality judging in this Eval-1 run. It contains digest fields such as `active_attention_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, and `source_ref_digest`.
- The `runtime/*.json` links in each window page are final full runtime state references. They are useful for diagnosis, but they are not the exact complete state at each probe point.
- `runtime/checkpoints/chapter-001.json` is the window boundary checkpoint. It should not be read as five separate probe-time full-store checkpoints.
- Current Eval-1 artifacts do not include per-probe full memory-store dumps. If future reviews need complete probe-time stores, the eval exporter should add explicit `exports/probe_state_snapshots/probe_###/...` artifacts rather than inferring from final runtime state.

## Window Index

| Window | Segment | Reactions | Notes | Recall | MQ avg | Grounded | Weak | FVI | Source window | Playback |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 活出生命的意义 | `huochu_shengming_de_yiyi_private_zh__segment_1` | 150 | 40 | 0.3750 | 3.70 | 19 | 9 | 0 | `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md` | [open](windows/huochu.md) |
| 芒格之道 | `mangge_zhi_dao_private_zh__segment_1` | 270 | 25 | 0.3600 | 3.10 | 43 | 13 | 0 | `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md` | [open](windows/mangge.md) |
| 纳瓦尔宝典 | `nawaer_baodian_private_zh__segment_1` | 40 | 23 | 0.4348 | 3.65 | 6 | 4 | 1 | `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/nawaer_baodian_private_zh__segment_1.md` | [open](windows/nawaer.md) |
| The Value of Others | `value_of_others_private_en__segment_1` | 58 | 94 | 0.2979 | 3.65 | 11 | 9 | 1 | `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/value_of_others_private_en__segment_1.md` | [open](windows/value_of_others.md) |
| 悉达多 | `xidaduo_private_zh__segment_1` | 211 | 20 | 0.4000 | 3.00 | 47 | 25 | 0 | `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/xidaduo_private_zh__segment_1.md` | [open](windows/xidaduo.md) |

## Coverage Checks

- Playback windows: `5`.
- Visible reactions listed: `729`.
- Lane A note cases represented: `202`.
- Memory Quality probes represented: `25`.
- Aggregation is report-level across shard outputs; there is no runner-emitted merged root summary for this high-parallel retry.

## Relationship To Other Reports

- Main interpretation report: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Interpretation-Report v0.md`
- Post-run execution report: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md`
- Metric/case/probe reviewer audit dossier: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/eval1-full-active-evaluation-post-slice8h-dossier/README.md`
- Reporting standard: `reading-companion-backend/docs/evaluation/reporting_standard.md`

## Guardrails

- `attentional_v2` only; no `iterator_v1` comparison.
- No historical/discontinued benchmark surfaces are interpreted here.
- No Reader Reaction Value / Insight and Clarification addendum is introduced.
- No evidence catalog entry is created by this dossier.
- Long Span vNext remains diagnostic pending a separate formal-authority brief.
- Selective note recall, Memory Quality, callback audit, and FVI audit remain separate evidence channels.
