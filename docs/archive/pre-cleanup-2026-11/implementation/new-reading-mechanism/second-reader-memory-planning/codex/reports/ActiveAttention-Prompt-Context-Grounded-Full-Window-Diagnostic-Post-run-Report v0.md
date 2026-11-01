# Active Attention Prompt-Context Grounded Full-Window Diagnostic Post-run Report v0

Date: 2026-05-22

## Executive Summary

The Active Attention prompt-context grounding repair landed, but the planned 5-window diagnostic run did not complete. The five registered Long Span jobs were launched in parallel, produced only partial reading traces, and were deliberately terminated before summary generation after it became clear that the run would not produce clean terminal diagnostic artifacts in this attempt.

This report should be read as an implementation-and-operational-failure report, not as Active Attention lifecycle evidence. No evidence catalog update is authorized, no Long Span vNext formal authority is promoted, and no product-quality claim is made.

## What Changed Before Launch

- Read prompt version was bumped to `attentional_v2.read.v22`.
- Prompt semantics now define Active Attention as a prompt-context-grounded reading forward-pull.
- Active Attention may be grounded in the current source unit, prompt-visible book/chapter framing, or prompt-visible prior memory.
- The prompt explicitly forbids importing outside knowledge about the book, author, or later chapters unless that knowledge is present in the prompt context.
- `source_quote` and `answer_source_quote` are required to be exact contiguous current-unit text when present.
- Runtime normalization no longer trusts model-emitted `source_refs` / `answer_source_refs`; it recomputes precise refs from exact quotes and otherwise does not manufacture precise source refs.
- `resolve` was tightened: a partial clue, setup, precondition, or reframing should update the open item, not answer it.

## Validation Before Diagnostic Launch

- Targeted tests passed: `103 passed, 6 warnings`.
- Live LLM target preflight passed for the configured MiniMax targets.
- Run ledger accepted planned entries before launch.
- No evidence catalog file was changed.
- No frontend or public API change was made.

## Diagnostic Execution

The run used the current active Long Span manifest and the current semantic probe plan:

- split manifest: `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
- probe plan: `reading-companion-backend/eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json`
- mechanism: `attentional_v2` only
- concurrency: five registered jobs in parallel, one per active Long Span window
- runner: `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`

| Window | Run id | Job id | Terminal status | Summary output |
| --- | --- | --- | --- | --- |
| huochu | `attentional_v2_active_attention_prompt_context_window_diagnostic_20260522_huochu` | `bgjob_active_attention_prompt_context_window_diagnostic_20260522_huochu` | failed, exit `-15` after manual termination | missing |
| mangge | `attentional_v2_active_attention_prompt_context_window_diagnostic_20260522_mangge` | `bgjob_active_attention_prompt_context_window_diagnostic_20260522_mangge` | failed, exit `-15` after manual termination | missing |
| nawaer | `attentional_v2_active_attention_prompt_context_window_diagnostic_20260522_nawaer` | `bgjob_active_attention_prompt_context_window_diagnostic_20260522_nawaer` | failed, exit `-15` after manual termination | missing |
| value_of_others | `attentional_v2_active_attention_prompt_context_window_diagnostic_20260522_value_of_others` | `bgjob_active_attention_prompt_context_window_diagnostic_20260522_value_of_others` | failed, exit `-15` after manual termination | missing |
| xidaduo | `attentional_v2_active_attention_prompt_context_window_diagnostic_20260522_xidaduo` | `bgjob_active_attention_prompt_context_window_diagnostic_20260522_xidaduo` | failed, exit `-15` after manual termination | missing |

Each run directory is preserved under `reading-companion-backend/eval/runs/attentional_v2/`. These are local run artifacts and were not force-added.

## Partial Artifact Facts

All five jobs created `meta/selected_windows.json`. None produced `summary/aggregate.json`, `summary/report.md`, or `summary/llm_usage.json`.

Runtime traces were partial. They contain successful early LLM calls, but not terminal evidence:

| Window | LLM trace rows | Activity rows | Trace status summary |
| --- | ---: | ---: | --- |
| huochu | 44 | 37 | partial, all observed rows `ok`; one observed same-tier failover |
| mangge | 58 | 34 | partial, all observed rows `ok` |
| nawaer | 58 | 40 | partial, all observed rows `ok`; one observed same-tier failover |
| value_of_others | 49 | 30 | partial, all observed rows `ok` |
| xidaduo | 52 | 28 | partial, all observed rows `ok`; three observed same-tier failovers |

Because the jobs were terminated before summaries, Memory Quality results, reaction audit results, selected-window aggregates, and full lifecycle audits were not produced. The partial traces must not be interpreted as completed Active Attention evidence.

## Why This Attempt Is Invalidated

This attempt is invalidated for evaluation purposes because all five jobs ended with exit `-15` after manual termination and did not reach terminal runner output. A run without completed summaries cannot answer whether prompt-context-grounded Active Attention works across the five full windows.

The partial traces do show that provider calls eventually succeeded, but they do not provide a complete lifecycle sequence, Memory Quality output, reaction audit output, or post-run health verdict. Treating the partial outputs as evidence would create the exact kind of false confidence this eval process is designed to avoid.

## Guardrails

- No eval catalog update was made.
- No `iterator_v1` run was launched.
- No old historical benchmark surface was run.
- No Reader Reaction Value / Insight and Clarification metric was added.
- No frontend, public API, or evidence catalog file was changed.
- No product-quality claim is made.
- Long Span vNext remains non-formal diagnostic territory.

## Interpretation

The code-side repair is in place and covered by targeted tests. The full-window diagnostic did not complete, so it cannot confirm or reject the Active Attention lifecycle behavior under the new v22 prompt.

The operational lesson is narrower but important: a registered job being alive, or having partial `ok` traces, is not enough. For this diagnostic, the acceptance boundary remains terminal runner summaries plus run-local lifecycle audit, not partial trace presence.

## Recommended Next Step

Review this invalidated diagnostic attempt and the v22 implementation diff. If we retry, use fresh run ids and consider one of these safer launch shapes:

- run one full window first to terminal, then parallelize;
- keep five-window parallelism but add a stricter first-trace / first-summary watchdog;
- add a runner-level heartbeat that reports current unit index and last successful LLM completion so progress is not inferred from PID liveness.

Do not reuse these five run ids as evidence.
