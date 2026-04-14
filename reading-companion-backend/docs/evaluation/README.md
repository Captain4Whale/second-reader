# Evaluation Report Index

This directory is the checked-in home for reviewed, human-readable evaluation reports.

## Layers

- Stable evaluation methodology lives in [docs/backend-reader-evaluation.md](../../../docs/backend-reader-evaluation.md).
- Machine-generated run artifacts live in `reading-companion-backend/eval/runs/`.
- Reviewed human interpretation reports live here under surface-specific subdirectories.

This split is intentional:

- `eval/runs/...` is the canonical raw run output.
- `docs/evaluation/...` is the human-facing interpretation/archive layer.

## Active Benchmark Pointers And Formal Evidence

| Surface | Run ID | Compared mechanisms | Status | One-line conclusion | Evidence |
| --- | --- | --- | --- | --- | --- |
| `user-level selective v1` | `attentional_v2_user_level_selective_v1_draft` | no formal judged run yet | `active benchmark definition` | The active local/user-level benchmark now uses one continuous reading segment per eligible note-linked book and scores `Selective Legibility` as note recall over aligned human notes. | [manifest](../../eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json) · [dataset](../../state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1/manifest.json) · [surface index](./user_level/README.md) |
| `bounded long-span accumulation comparison` | `attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407` | `attentional_v2` vs `iterator_v1` | `completed` | `iterator_v1` won the current durable long-span evidence lane on retrospective bridging and window-end closure; attentional_v2 still showed stronger main-thread fidelity on some single-chapter probes.` | [aggregate](../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/summary/aggregate.json) · [report](../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/summary/report.md) · [surface index](./long_span/README.md) · [interpretation](./long_span/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_interpretation.md) |

## Surface Directories

- [user_level/](./user_level/README.md)
  - active note-aligned user-level benchmark definition and future judged reports
- [excerpt/](./excerpt/README.md)
  - superseded excerpt-surface reports kept as historical evidence
- [long_span/](./long_span/README.md)
  - formal bounded long-span interpretation reports

## Historical / Legacy Checked-In Reports

These files remain useful historical reference, but they predate the current surface-index pattern and should not be mistaken for the current formal evidence entry points.

- `subsegment/`
  - older subsegment-era comparison reports
- `highlight_comparison_ch1.md`
- `highlight_comparison_ch2.md`
- `highlight_comparison_ch3.md`
- `highlight_comparison_ch3_before_prompt_tuning.md`

## Conventions

- One formal judged run should land one human interpretation report.
- Formal interpretation files follow `<run_id>_interpretation.md`.
- Each recurring formal surface should keep its own `README.md` index.
- This root `README.md` is the cross-surface discovery index, not the canonical machine output.
