# Active Attention Live-Question Micro Eval Huochu Post-run Report v0

Date: 2026-05-21

Status: **completed as a diagnostic eval job; failed the Active Attention lifecycle behavior check**

This report records a small, fresh diagnostic run designed to test whether the new `Active Attention = live question set` repair changes runtime behavior on a natural open-question arc from *Man's Search for Meaning* / 《活出生命的意义》. It is not evidence-catalog material yet, not formal benchmark authority, and not a product-quality claim.

## Executive Summary

The micro eval ran successfully as infrastructure:

- job status: `completed`
- run id: `attentional_v2_active_attention_live_question_micro_huochu_20260521`
- job id: `bgjob_active_attention_live_question_micro_huochu_20260521`
- mechanism: `attentional_v2` only
- source excerpt: original `huochu` active-window paragraphs `p45-p61`
- LLM health: `ok`, `34 / 34` successful calls, `0` errors, `0` fallback traces
- Memory Quality source: fresh judge
- reaction audit source: fresh judge

But the behavior under test did **not** pass:

- all 5 probe-time `scoring_memory_state.active_attention.active_items` arrays were empty
- unit-level `settlement_audit.jsonl` showed no `active_attention` create/update/resolve/close/drop deltas during reading
- final `runtime/active_attention.json` contained 2 legacy `statement`-only open items with no `question_from`, no `driving_question`, no `working_answer`, no `answer_source_refs`, and empty `source_refs`

Diagnostic verdict: **failed for Active Attention live-question lifecycle behavior**.

## Commands Run

Preflight and setup:

```bash
git status --short
test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
cd reading-companion-backend && .venv/bin/python scripts/check_llm_targets_live.py
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_state_ops.py tests/test_attentional_v2_nodes.py tests/test_attentional_v2_state_projection.py tests/test_long_span_vnext.py -q
cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_run_ledger.py upsert ...
cd reading-companion-backend && .venv/bin/python scripts/update_evaluation_run_ledger.py --check
```

Micro dataset generation:

```bash
reading-companion-backend/.venv/bin/python /tmp/create_active_attention_micro_dataset.py
```

Launch:

```bash
cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- \
  --root . \
  --job-id bgjob_active_attention_live_question_micro_huochu_20260521 \
  --task-ref TASK-SECOND-READER-ACTIVE-ATTENTION-MICRO-EVAL-20260521 \
  --lane mechanism_eval \
  --purpose "Active Attention live-question micro eval: huochu p45-p61" \
  --cwd . \
  --run-dir eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521 \
  --expected-output eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/aggregate.json \
  --expected-output eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/report.md \
  --expected-output eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/llm_usage.json \
  --shell-command ".venv/bin/python eval/attentional_v2/run_long_span_vnext.py --run-id attentional_v2_active_attention_live_question_micro_huochu_20260521 --manifest-path state/eval_local_datasets/diagnostic_micro/active_attention_live_question_huochu_20260521/split_manifest.json --memory-quality-probe-plan state/eval_local_datasets/diagnostic_micro/active_attention_live_question_huochu_20260521/probe_plan.json --segment-id active_attention_live_question_huochu_p45_p61__segment_1 --v2-only --workers 1 --judge-mode llm --output-attempts 1 --output-retry-sleep-seconds 0 --reaction-reuse-run-root \"\""
```

Polling and validation:

```bash
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py --job-id bgjob_active_attention_live_question_micro_huochu_20260521
cd reading-companion-backend && .venv/bin/python scripts/check_eval_llm_health.py eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521
```

## Run Artifacts

- Run directory: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521`
- Job log: `reading-companion-backend/state/job_registry/logs/bgjob_active_attention_live_question_micro_huochu_20260521.log`
- Aggregate: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/aggregate.json`
- Report: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/report.md`
- LLM usage: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/llm_usage.json`
- Lifecycle audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/analysis/active_attention_lifecycle_audit/README.md`
- Local diagnostic dataset: `reading-companion-backend/state/eval_local_datasets/diagnostic_micro/active_attention_live_question_huochu_20260521`

The local diagnostic dataset and run artifacts are intentionally not force-added to git.

## Source Excerpt

The micro source was extracted from the active `20260422` user-level package's `huochu` source window.

- book: 《活出生命的意义》
- original source window paragraphs: `p45-p61`
- micro segment id: `active_attention_live_question_huochu_p45_p61__segment_1`
- micro sentence range: `c1-s1` through `c1-s79`
- paragraph count: `17`
- note cases: `0`

The excerpt was selected because it naturally contains a live-question arc:

- p45 asks how much suffering humans can endure and how adaptation works
- p46 frames the first-stage psychological response and the question of how people get used to anything
- p51 transitions into a second-stage emotional numbness
- p55 gives concrete numbness evidence
- p61 summarizes apathy as a protective shell

## Probe Targets

| Probe | Source-native target | Semantic boundary | Purpose |
| --- | --- | --- | --- |
| 1 | `src:c1:p2@0-p2@138` | live question opening | Should create or expose the live question about how prisoners adapt and at what cost. |
| 2 | `src:c1:p3@0-p3@276` | first-stage survival answer | Should update the working answer with first-stage death/fearlessness evidence. |
| 3 | `src:c1:p7@0-p7@260` | stage transition | Should update the working answer toward emotional numbness. |
| 4 | `src:c1:p11@0-p11@272` | numbness evidence | Should ground the answer in concrete suffering/numbness evidence. |
| 5 | `src:c1:p17@0-p17@87` | answer consolidation | Should close or stabilize the question around apathy as protective shell. |

## Aggregate Checks

From `summary/aggregate.json`:

- run id: `attentional_v2_active_attention_live_question_micro_huochu_20260521`
- target: `long_span_vnext_phase1`
- mechanism keys: `["attentional_v2"]`
- probe plan id: `active_attention_live_question_micro_huochu_20260521`
- probe selection method: `semantic_boundary_with_distance_reference`
- Memory Quality window count: `1`
- Memory Quality probe count: `5`
- Memory snapshot basis: `full_probe_time_memory_state` for all 5 probes
- average Memory Quality score: `2.05`
- visible reactions: `22`
- grounded callbacks: `1`
- weak callbacks: `0`
- false visible integrations: `0`
- local-only reactions: `21`

From `meta/output_sourcing.json`:

- fresh task count: `1`
- output mode: `fresh`
- `reaction_reuse_run_root`: empty
- `memory_quality_source_run_root`: empty
- LLM health for fresh output: `ok`

## Active Attention Lifecycle Findings

The core diagnostic result is negative.

| Check | Result |
| --- | --- |
| Probe-time active questions created? | No. All 5 probe snapshots had `active_items=[]`. |
| Unit-level active-attention state deltas? | No. All settlement rows had `active_attention` count `0 -> 0`. |
| `question_from` present? | No. |
| `driving_question` present? | No. |
| `working_answer` present or updated? | No. |
| `answer_source_refs` present? | No. |
| Questions resolved / answered / closed? | No lifecycle observed. |
| Final Active Attention state uses new shape? | No. Final state contains legacy `statement`-only items. |
| Final Active Attention source refs grounded? | No. Final items have `source_refs=[]`. |

The final `runtime/active_attention.json` contains:

- `ccf-001`: legacy `statement`-only open item about checking whether the two-stage model carries into a later meaning-seeking phase; no source refs
- `ccf-002`: legacy `statement`-only open item about the tension between external survival strategy and internal collapse; no source refs

These look like chapter-consolidation/carry-forward artifacts, not Read-time live-question maintenance. They also appear after the probe timeline, so they cannot explain or rescue the empty probe-time Active Attention evidence.

## Related Memory Findings

The run did populate some concept state:

- `psychological_reaction_stages`
- `death_normalization_sequence`
- `emotional_numbness_definition`

But the concept entries were thin:

- final concept summaries were empty
- source refs existed by the end, but early probe states were sparse
- `thread_trace.json` remained empty

This supports the MQ judge's low score: the mechanism retained fragments of the framework, but did not maintain the live question or organize the answer path as intended.

## Memory Quality And Reaction Audit

Memory Quality rows:

| Probe | Overall MQ | Judge signal |
| --- | ---: | --- |
| 1 | `1.25` | Memory state essentially empty; no live question stored. |
| 2 | `1.75` | Bare conceptual labels; no concrete details or active question. |
| 3 | `2.25` | Stage transition retained as an accurate quote; no active question/thread/reflection. |
| 4 | `2.25` | Thin framework; concrete numbness evidence missing from durable memory. |
| 5 | `2.75` | Protective-shell idea partially retained; organization remains weak. |

Reaction audit:

- total visible reactions: `22`
- callback attempts: `1`
- grounded callbacks: `1`
- weak callbacks: `0`
- false visible integrations: `0`
- local-only reactions: `21`

The single grounded callback was `rx:Full_Content:src:c1:p6@0-p6@27:retrospect:7`, which correctly linked the later smile reaction back to the earlier "human beings can get used to anything" logic. This is useful reaction-layer evidence, but it does not demonstrate Active Attention lifecycle success.

## LLM Usage

From `summary/llm_usage.json`:

- requests: `34`
- successes: `34`
- errors: `0`
- retries: `1`
- average rpm: `1.818`
- max inflight: `1`
- quota wait: `0 ms`
- provider gate wait: `0 ms`
- profile gate wait: `0 ms`
- runtime reader profile: `28` requests, `28` successes, `1` retry
- eval judge profile: `6` requests, `6` successes, `0` retries
- `MiniMax-M2.7-personal`: `4` requests
- `MiniMax-M2.7-personal-2`: `30` requests

Judge calls occurred: yes, Memory Quality and reaction audit judging both occurred.

Reading job occurred: yes, one fresh `attentional_v2` reading task was run.

## Interpretation

This micro eval did exactly what it was meant to do: it gave us a short, inspectable failure case for the Active Attention repair.

The current implementation can now:

- run with strict LLM health
- use full probe-time memory state for MQ judging
- produce source-native probe captures
- complete the Long Span diagnostic runner

But it still does not cause the reader to maintain Active Attention as an open live-question set. The prompt/schema repair is either not reaching the actual Read outputs, not strong enough to make the model use `active_attention`, or still being overridden by chapter consolidation / carry-forward logic that accepts legacy `statement` items.

## Recommendation

Do not rerun broader eval yet.

Recommended next implementation brief:

- inspect the actual `read_unit` and `chapter_consolidation` prompt manifests from this run
- remove or tighten remaining legacy `statement` active-attention paths from the prompt/consolidation contract
- add a targeted runtime/prompt test that expects an excerpt like this to produce at least one grounded item with `question_from`, `driving_question`, and `working_answer`
- ensure chapter consolidation cannot create ungrounded `statement`-only open Active Attention items as the final state

No evidence catalog update, Long Span formal-authority promotion, or product-quality claim is authorized from this diagnostic run.

## Guardrails

- No `iterator_v1` run.
- No cross-mechanism comparison.
- No full active evaluation run.
- No evidence catalog update.
- No product-quality claim.
- No Long Span vNext formal benchmark promotion.
- No frontend/public API/durable-state change.
- No runtime/eval-runner/judge-prompt change during this micro eval execution.

