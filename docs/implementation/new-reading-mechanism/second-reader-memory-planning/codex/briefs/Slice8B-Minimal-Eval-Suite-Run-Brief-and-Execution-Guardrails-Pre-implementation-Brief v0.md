# Slice 8B: Minimal Eval Suite Run Brief and Execution Guardrails - Pre-implementation Brief v0

## PR Title

`Slice 8B: Minimal Eval Suite Run Brief and Execution Guardrails`

## Implementation Slice

Slice 8B is a doc-only run brief in Slice 8 / Post-implementation Review & Eval Readiness.

It builds on the accepted Slice 8A readiness gate and defines the guardrails for a later bounded Minimal Eval Suite execution. Slice 8B does not execute eval, run benchmark jobs, call judges, launch reading jobs, create eval run directories, modify runtime behavior, or change eval runners.

Actual Minimal Eval Suite execution remains blocked until a later separately accepted execution slice.

## Design Sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- Slice 7A minimal eval inventory manifest:
  - `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- Slice 7B smoke validator and tests:
  - `reading-companion-backend/scripts/validate_minimal_eval_inventory_smoke.py`
  - `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- Slice 8A readiness brief and post-implementation report
- Slice 1 through Slice 7B briefs, reports, and patch reports
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Current Code Facts

- Slice 8A Post-implementation Report is accepted by the latest reviewer instruction, and no prerequisite runtime patch or eval-runner patch is currently indicated before a later Minimal Eval Suite run brief.
- Slice 7A added the static minimal eval inventory manifest with exactly two active lanes:
  - Lane A: `lane_a_local_user_level_selective_legibility`
  - Lane B: `lane_b_long_span_mq_callback_fvi`
- Slice 7B added a stdlib-only manifest smoke validator that validates manifest shape, lane separation, tracked/local-only path handling, evidence surfaces, diagnostic additions, and interpretation guards.
- Lane A remains the active Local / User-level Selective Legibility benchmark lane. The active dataset pointer is `attentional_v2_user_level_selective_v1_repaired_20260422`, while the current formal evidence bundle boundary remains `attentional_v2_user_level_selective_v1_repaired_20260416`.
- Lane B remains Long Span MQ / Callback / FVI diagnostic phase 1 with `formal_authority=false`; it must not be promoted to formal benchmark authority by a smoke run.
- `run_user_level_selective_comparison.py` supports `--run-id`, `--manifest-path`, `--mechanism-filter`, `--judge-mode`, repeated `--segment-id`, repeated `--note-case-id`, and `--reuse-output-dir`.
- `run_long_span_vnext.py` supports `--run-id`, `--runs-root`, `--manifest-path`, `--memory-quality-probe-plan`, `--judge-mode`, repeated `--segment-id`, `--window-limit`, `--workers`, `--reaction-reuse-run-root`, `--memory-quality-source-run-root`, `--memory-quality-results-source-run-root`, `--rerun-reaction-audit`, and `--v2-only`.
- Existing eval runners can launch reading jobs and judge calls. Slice 8B must not invoke them.

## Files To Change

Slice 8B brief landing should change only process/status documentation:

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Files Explicitly Not Changing

- Runtime mechanism code under `reading-companion-backend/src/attentional_v2/`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_ops.py`
- `reading-companion-backend/src/attentional_v2/slow_cycle.py`
- `reading-companion-backend/src/attentional_v2/read_context.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- source skills
- eval runners, including:
  - `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
  - `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- judge prompts
- durable mechanism state
- public API
- frontend
- stable evaluation docs and evidence catalog, unless a later accepted execution/report explicitly scopes that update

## Planned Deltas

- Mark the Slice 8A Post-implementation Report as accepted.
- Add this Slice 8B Pre-implementation Brief as pending human review.
- Define a future bounded run profile and execution guardrails.
- Keep actual eval execution blocked until a later separately accepted execution slice.
- Do not add scoring, metric taxonomy, runtime behavior, prompt text/version changes, eval-runner changes, public API changes, frontend changes, or durable-state changes.

## Future Minimal Run Profile

The commands below are candidate future commands for a later accepted execution slice. They must not be run as part of Slice 8B brief landing.

### Preflight Static Checks

Any later execution slice should run these checks first:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

The forbidden runtime/frontend/eval-runner diff check must return empty output.

### Lane A: Local / User-level Selective Legibility

Future execution should use `run_user_level_selective_comparison.py` against the active `20260422` dataset pointer, but only on a tiny reviewed subset rather than the full lane.

Candidate future command:

```bash
cd reading-companion-backend && .venv/bin/python eval/attentional_v2/run_user_level_selective_comparison.py \
  --run-id attentional_v2_minimal_eval_suite_lane_a_smoke_20260517 \
  --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json \
  --mechanism-filter attentional_v2 \
  --judge-mode llm \
  --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 \
  --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002 \
  --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003 \
  --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004
```

Guardrails:

- Use a deterministic run id.
- Use `--mechanism-filter attentional_v2` for the minimal smoke unless a later accepted brief explicitly requests cross-mechanism comparison.
- Use a tiny segment/note-case subset.
- Do not broaden to the full Lane A package without a separate acceptance step.
- Treat the result as smoke/evidence readiness, not final product quality proof.

### Lane B: Long Span MQ / Callback / FVI

Future execution should keep Long Span vNext diagnostic phase 1 and use `run_long_span_vnext.py` with the semantic probe manifest. It should reuse completed outputs where possible to avoid unnecessary reading jobs.

Candidate future command:

```bash
cd reading-companion-backend && .venv/bin/python eval/attentional_v2/run_long_span_vnext.py \
  --run-id attentional_v2_minimal_eval_suite_lane_b_smoke_20260517 \
  --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json \
  --memory-quality-probe-plan eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json \
  --memory-quality-source-run-root eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425 \
  --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 \
  --v2-only \
  --workers 1 \
  --judge-mode llm
```

Guardrails:

- Keep `--workers 1` unless a later accepted execution slice explicitly widens concurrency.
- Prefer source-run reuse flags when available to avoid unnecessary reading jobs.
- Use bounded segment/window selection; do not launch broad/all-window Long Span runs from Slice 8B.
- Keep Lane B diagnostic phase 1 and `formal_authority=false`.
- Do not promote Long Span vNext to formal benchmark authority from a smoke run.

## Future Execution Guardrails

- A later execution slice must explicitly approve any judge calls, reading jobs, run-directory creation, and expected LLM cost.
- Register a background job before launch if expected runtime may exceed roughly `10-15` minutes.
- Use deterministic run ids.
- Use single-worker defaults unless explicitly widened.
- Keep Lane A and Lane B separate.
- Keep Planning Trace Quality and Slow-cycle Safety as diagnostic evidence-availability checks only, not scores.
- Do not update the evidence catalog or stable evaluation docs unless the later accepted execution/report explicitly scopes that update.
- Do not treat a smoke run as product-quality proof.

## Interpretation Guards

- Audit existence is not product quality.
- Retrieval availability is not utilization success.
- Visible reaction presence is not callback correctness.
- SourceRef count is not fidelity score.
- Trace existence is not planning quality.
- `slow_cycle_audit` existence is not slow-cycle quality.
- Planning Trace Quality and Slow-cycle Safety are diagnostic evidence-availability additions only.

## Engineering Validation Commands For Brief Landing

Run only static/doc checks:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

Do not run eval, benchmark jobs, judge calls, reading jobs, or create eval run directories during Slice 8B brief landing.

## Non-goals

- No full AI Evaluation.
- No benchmark jobs.
- No judge calls.
- No reading jobs.
- No eval run directories.
- No eval-runner modification.
- No judge-prompt modification.
- No runtime mechanism behavior change.
- No prompt text/version change.
- No public API or frontend change.
- No durable mechanism state change.
- No new metric taxonomy.
- No scoring.
- No Long Span vNext formal-authority promotion.
- No actual Minimal Eval Suite run before a later accepted execution slice.

## Risks

- The run brief could be mistaken for eval execution. Mitigation: label all run commands as future-only and keep the current task doc-only.
- The future `--judge-mode llm` commands may incur LLM cost. Mitigation: require explicit later execution acceptance, deterministic scope, and cost posture before running.
- Local-only dataset/run roots may differ by clone. Mitigation: require static manifest smoke and local-only availability reporting before execution.
- Reuse assumptions for completed Long Span outputs may drift. Mitigation: verify source-run roots in the later execution slice before launching any job.
- A minimal smoke result could be overread as product-quality proof. Mitigation: keep all interpretation guards explicit.

## Rollback Plan

Revert the doc-only Slice 8B landing. No migration, runtime rollback, eval artifact cleanup, judge-output cleanup, or durable-state repair is required.

## Open Questions

None blocking.

The later execution slice should confirm exact run ids, judge mode, background-job registration, subset selection, and whether Lane B should copy or rejudge any existing diagnostic outputs before launching anything.

## Go / No-go Recommendation

Go for human review of this Slice 8B Pre-implementation Brief.

No-go for actual Minimal Eval Suite execution, benchmark jobs, judge calls, reading jobs, eval run directories, runtime behavior changes, eval-runner changes, scoring, or formal-authority promotion until a later execution slice is created and accepted.
