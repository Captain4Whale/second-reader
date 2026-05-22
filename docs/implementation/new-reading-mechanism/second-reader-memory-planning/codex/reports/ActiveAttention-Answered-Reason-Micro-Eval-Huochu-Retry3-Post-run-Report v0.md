# Active Attention Answered-Reason Micro Eval — Huochu Retry3 Post-run Report v0

Date: 2026-05-21

Run id: `attentional_v2_active_attention_live_question_micro_huochu_20260521_retry3`

Job id: `bgjob_active_attention_live_question_micro_huochu_20260521_retry3`

## Executive Summary

Retry3 completed successfully and is a partial-positive diagnostic pass for the answered-reason Active Attention lifecycle repair.

It shows that `attentional_v2` can now create live-inquiry Active Attention items, keep partial progress open, and resolve an item with `answered_reason` plus answer source evidence. It does not fully validate `close` behavior or downstream concept/thread lineage. The run remains diagnostic only: no evidence catalog update, no full eval, no Long Span formal-authority promotion, and no product-quality claim.

## What Ran

- Scope: one diagnostic micro window from `huochu` paragraphs `p45-p61`.
- Runner: `eval/attentional_v2/run_long_span_vnext.py`
- Mechanism: `attentional_v2` only.
- Judge mode: `llm`.
- Run directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry3`
- Run-local audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry3/analysis/active_attention_lifecycle_audit/README.md`

## LLM Health And Usage

- Health checker: `ok`
- Requests: `28`
- Successes: `28`
- Errors: `0`
- Retries: `2`
- Fallback-backed evidence: `0`
- Targets used: both configured MiniMax targets were used.

The retry count was provider-level retry/failover inside successful calls, not fallback-backed evidence.

## Aggregate Output

- Memory Quality probes: `5`
- Memory Quality windows: `1`
- Memory snapshot basis: `full_probe_time_memory_state` for all 5 probes
- Average Memory Quality: `3.55`
- Visible reactions: `17`
- Callback attempts: `5`
- Grounded callbacks: `3`
- Weak callbacks: `2`
- False Visible Integration: `0`
- Memory Quality source: `fresh_judge`
- Reaction audit source: `fresh_judge`

These aggregate scores are secondary in this micro eval. The primary diagnostic question was Active Attention creation and lifecycle behavior.

## Active Attention Findings

### Positive Findings

- `adaptation-paradox-survival` was created as a live inquiry and later resolved with `answered_reason`.
- The resolved item had opened source coordinates and answered source coordinates.
- The answer source quote matched exactly at `src:c1:p2@117-p2@138`.
- `moslem-survival-logic` remained `open` after partial progress rather than being forced into terminal state.
- `normal-reaction-suppression-mechanism` was created and then repeatedly updated, remaining `open` as the text kept developing the emotional-numbness / protective-shell line.
- No new statement-only Active Attention item was needed.

### Remaining Limitations

- `close` was not exercised. This source window did not produce a clear `closed_reason` case, so close behavior remains a future observation point.
- No `derived_from_active_attention_ids` appeared in `concept_registry` or `thread_trace`; downstream lineage was not covered by this micro window.
- Several source refs and answer source refs fell back to `fallback_unit_span`, usually because the model emitted a quote that was stitched, paraphrased, or slightly non-exact. These fallback refs are useful diagnostics, not precise source evidence.
- Some active items still trend broad, especially where one reading tension has several closely related sides. This should be managed by prompt semantics, not by adding another field.

## Interpretation

The answered-reason lifecycle is directionally right. It is simpler than the previous `answer_boundary` design because the model does not need to predict in advance what would count as enough answer. Instead, when it terminates an item, it must explain why with `answered_reason` or `closed_reason` and cite answer evidence.

The next adjustment should be small:

- improve deterministic source quote matching in the runtime;
- frame Active Attention as one coherent reading forward-pull, not a formal Q&A item;
- record downstream concept/thread lineage as a later longer-window/full-eval coverage gap rather than forcing it in this micro window.

## Guardrails

- No evidence catalog update was made.
- No full eval was run.
- No Long Span formal authority promotion is implied.
- No product-quality claim is made.
- The run remains diagnostic evidence for mechanism repair only.

## Recommended Next Step

Apply the source-grounding and forward-pull semantics adjustment, then run a fresh retry4 micro eval with a new run id. Retry3 should remain preserved as diagnostic evidence and marked `review_pending` in the run ledger.
