# Active Attention Forward-pull Micro Eval — Huochu Retry4 Post-run Report v0

Date: 2026-05-22

Run id: `attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4`

Job id: `bgjob_active_attention_live_question_micro_huochu_20260521_retry4`

## Executive Summary

Retry4 completed successfully and is a mixed diagnostic result.

The source-grounding repair worked: Active Attention `answer_source_refs` are now exact matches, and the noisy update-time `fallback_unit_span` pattern from Retry3 is gone. The v21 prompt also kept a broad reading forward-pull open across the window.

The semantic result is not fully satisfactory. The run drifted toward a "meaning finding / third stage" forward-pull that is not directly established in this short excerpt, and then resolved a follow-up item using the protective-shell passage as a logical precondition rather than a direct answer. This is useful diagnostic evidence, but not a product-quality claim.

## What Changed Before This Run

- `source_ref_from_unit` now attempts raw exact match, normalized exact match, and ordered-fragment match before falling back to unit span.
- Read prompt was bumped to `attentional_v2.read.v21`.
- Active Attention wording was softened from formal Q&A/inquiry language toward one coherent reading forward-pull.
- `answered` / `closed` semantics remain soft terminal states.
- No new metric was added.
- No evidence catalog files were updated.

## Run Facts

- Scope: one diagnostic micro window from `huochu` paragraphs `p45-p61`.
- Mechanism: `attentional_v2` only.
- Judge mode: `llm`.
- Run directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4`
- Run-local audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4/analysis/active_attention_lifecycle_audit/README.md`

## LLM Health And Usage

- Health checker: `ok`
- Requests: `26`
- Successes: `26`
- Errors: `0`
- Retries: `0`
- Fallback-backed evidence: `0`
- Targets used: both configured MiniMax targets were used.

## Aggregate Output

- Memory Quality probes: `5`
- Memory Quality windows: `1`
- Memory snapshot basis: `full_probe_time_memory_state` for all 5 probes
- Average Memory Quality: `3.25`
- Visible reactions: `17`
- Callback attempts: `7`
- Grounded callbacks: `6`
- Weak callbacks: `1`
- False Visible Integration: `0`
- Memory Quality source: `fresh_judge`
- Reaction audit source: `fresh_judge`

These aggregate scores are not the main conclusion of this micro run.

## Source Grounding Result

Active Attention memory-op source resolution improved materially:

- `answer_source_refs`: `8` exact matches.
- `source_refs`: `1` exact match and `1` fallback.
- The remaining fallback was the opening cue `"关于痛苦承受力的惊奇发现"`, which is a paraphrase rather than a quote.

This validates the program-side source grounding repair direction. LLMs cite text snippets; runtime code resolves paragraph-char coordinates.

## Active Attention Result

### `q-adaptability-under-suffering`

This item stayed open across all probes. It tracks the relationship between body adaptation, first-stage psychological adaptation, second-stage emotional shutdown, and later meaning construction.

This is partly good: the item was not prematurely resolved when only partial evidence appeared.

It is also a caveat: by the final state, the item imports a "third stage / meaning finding" expectation that this micro excerpt does not directly open. That is a source-local restraint problem in prompt semantics.

### `q-meaning-under-emotional-death`

This item was created when the text showed the narrator continuing to drink soup after recognizing a recently living person as dead. It was then resolved when the text introduced the protective-shell function of coldness.

The grounding is exact, but the lifecycle judgment is debatable. The protective-shell passage explains survival under emotional numbness; it does not directly answer how meaning finding happens. This should be treated as a semantic caveat, not a source-coordinate failure.

## Remaining Gaps

- `close` behavior remains unexercised.
- Downstream `derived_from_active_attention_ids` remains unobserved in concept/thread stores.
- Active Attention can still over-import book-level themes if prompt language does not explicitly keep the forward-pull source-local.

## Interpretation

Retry4 confirms that the source-coordinate side is now cleaner and that the program/LLM division is healthier.

It also shows that the forward-pull concept needs one more semantic guardrail if we continue tuning: Active Attention may anticipate what the current source invites the reader to watch for, but it should not import later book-level themes unless the current source explicitly opens them.

No new field or metric is recommended from this run. The right next repair, if accepted, is prompt-level source-local restraint.

## Guardrails

- No evidence catalog update was made.
- No full eval was run.
- No Long Span formal authority promotion is implied.
- No product-quality claim is made.
- This remains diagnostic mechanism-repair evidence only.
