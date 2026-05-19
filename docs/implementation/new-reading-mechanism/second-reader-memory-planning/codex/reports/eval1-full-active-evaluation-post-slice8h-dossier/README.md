# Eval-1 Full Active Evaluation Post-Slice8H: Reviewer Audit Dossier

This dossier is the deep-review companion for the Eval-1 Retry1 interpretation report. It replaces the earlier shallow window summary with a reviewer-auditable structure modeled on the 20260425 / 20260503 Memory Quality source-map reports, adapted for the current two-lane Eval-1 run.

It is not an eval run, not an evidence-catalog update, not a Long Span formal-authority promotion, and not a product-quality claim.

## How To Read

1. Start with the main interpretation report for the executive answer and aggregate interpretation.
2. Use the window pages below for reviewer-grade evidence: Lane A case audit, Lane B probe audit, Callback/FVI audit, and raw artifact paths.
3. For Memory Quality, treat probe-time snapshots as scoring evidence. Final runtime files are diagnostic support only.
4. For Local/User-level recall, treat strict `segment_source_v1` source-span admission as the boundary. Unlocatable reactions and broad semantic similarity are not matches.

## Window Index

| Window | Segment | Notes | Recall | Exact | Focused | Incidental | Miss | MQ avg | Grounded | Weak | FVI | Audit page |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 活出生命的意义 | `huochu_shengming_de_yiyi_private_zh__segment_1` | 40 | 0.3750 | 7 | 8 | 2 | 23 | 3.70 | 19 | 9 | 0 | [open](windows/huochu.md) |
| 芒格之道 | `mangge_zhi_dao_private_zh__segment_1` | 25 | 0.3600 | 2 | 7 | 0 | 16 | 3.10 | 43 | 13 | 0 | [open](windows/mangge.md) |
| 纳瓦尔宝典 | `nawaer_baodian_private_zh__segment_1` | 23 | 0.4348 | 8 | 2 | 2 | 11 | 3.65 | 6 | 4 | 1 | [open](windows/nawaer.md) |
| The Value of Others | `value_of_others_private_en__segment_1` | 94 | 0.2979 | 10 | 18 | 4 | 62 | 3.65 | 11 | 9 | 1 | [open](windows/value_of_others.md) |
| 悉达多 | `xidaduo_private_zh__segment_1` | 20 | 0.4000 | 1 | 7 | 0 | 12 | 3.00 | 47 | 25 | 0 | [open](windows/xidaduo.md) |

## Relationship To Other Artifacts

- Main interpretation report: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Interpretation-Report v0.md`
- Post-run execution report: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md`
- Reporting standard: `reading-companion-backend/docs/evaluation/reporting_standard.md`
- Raw Lane A artifacts: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_<slug>`
- Raw Lane B artifacts: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_<slug>`

## What Changed From The Shallow Draft

- The previous window pages were mostly tables and representative snippets. This rewrite makes each window a reviewer audit document.
- Each Lane B probe now has its own section with position, source orientation, snapshot evidence, retained/missing interpretation, score rationale, and manual-check path.
- Lane A now explains representative exact/focused/incidental/miss cases and miss modes rather than only listing labels.
- Callback/FVI examples now explain prior-link quality and why weak/FVI labels matter.

## Guardrails

- `attentional_v2` only; no `iterator_v1` comparison.
- No historical or discontinued benchmark surfaces are interpreted here.
- No Reader Reaction Value / Insight and Clarification addendum is included.
- No evidence catalog entry is created by this dossier.
- Long Span vNext remains diagnostic pending a separate formal-authority brief.
- Selective note recall, Memory Quality, callback audit, and FVI audit remain separate evidence channels.
