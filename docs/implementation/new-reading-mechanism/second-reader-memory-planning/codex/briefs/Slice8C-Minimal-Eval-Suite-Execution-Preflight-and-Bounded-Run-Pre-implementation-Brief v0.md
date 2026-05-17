# Slice 8C: Minimal Eval Suite Execution Preflight and Bounded Run - Pre-implementation Brief v0

## PR Title

`Slice 8C: Minimal Eval Suite Execution Preflight and Bounded Run`

## Implementation Slice

Slice 8C is the execution-slice brief for a later bounded Minimal Eval Suite smoke run.

This landing is doc-only. It converts the accepted Slice 8B run brief into an exact future execution plan, including commands, run ids, background-job policy, expected outputs, acceptance checks, rollback rules, and cost posture.

Actual eval execution remains blocked until this Slice 8C brief is accepted. This brief landing does not run eval, launch benchmark jobs, call judges, start reading jobs, create eval run directories, modify runtime behavior, or modify eval runners.

## Design Sources

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
- `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- `reading-companion-backend/scripts/validate_minimal_eval_inventory_smoke.py`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.md`
- `reading-companion-backend/docs/evaluation/evidence_catalog.json`
- `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- `docs/tasks/registry.json`

## Current Code Facts

- Slice 8B Pre-implementation Brief is accepted by human reviewer instruction.
- Slice 7A inventory preserves exactly two active eval lanes:
  - Lane A: `lane_a_local_user_level_selective_legibility`
  - Lane B: `lane_b_long_span_mq_callback_fvi`
- Slice 7B smoke validator can validate manifest parseability, lane separation, required evidence surfaces, tracked/local-only paths, diagnostic additions, and interpretation guards without invoking eval runners.
- `run_user_level_selective_comparison.py` supports `--run-id`, `--manifest-path`, `--mechanism-filter`, `--judge-mode`, repeated `--segment-id`, repeated `--note-case-id`, and `--reuse-output-dir`.
- `run_long_span_vnext.py` supports `--run-id`, `--runs-root`, `--manifest-path`, `--memory-quality-probe-plan`, `--judge-mode`, repeated `--segment-id`, `--window-limit`, `--workers`, `--reaction-reuse-run-root`, `--memory-quality-source-run-root`, `--memory-quality-results-source-run-root`, `--rerun-reaction-audit`, and `--v2-only`.
- The future Lane B source run `attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504` exists locally and uses `probe_plan_id="memory_quality_semantic_probe_plan_20260504"` with `probe_selection_method="semantic_boundary_with_distance_reference"`.
- The future run directories are not present at brief-preparation time:
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`
- Existing eval runners can create run directories, launch reading jobs, and call judges, so Slice 8C brief landing must not invoke them.

## Files To Change For Brief Landing

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
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
- frontend
- public API
- durable mechanism state
- eval runners
- judge prompts
- evidence catalog
- stable evaluation docs

## Exact Execution Plan

The future bounded Minimal Eval Suite run includes both lanes, executed sequentially after this brief is accepted and a later execution request is made.

- Lane A runs first as a fresh `attentional_v2`-only Local / User-level Selective Legibility smoke on one segment and three note cases.
- Lane B runs second as an `attentional_v2`-only Long Span MQ / Callback / FVI smoke using existing semantic-probe source outputs, fresh Memory Quality rejudge, copied reaction audit, and no reading jobs.
- The two lanes remain separate run ids and separate registered background jobs.
- Cross-mechanism comparison is out of scope.
- Long Span vNext remains diagnostic phase 1 and is not promoted to formal benchmark authority.

## Preflight Commands For Later Execution

Run these before launching any future Slice 8C execution jobs:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517
test ! -e reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517
```

The forbidden runtime/frontend/eval-runner diff check must return empty output.

## Lane A Future Command

Underlying eval command:

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

Registered background-job launch shape for the later execution slice:

```bash
cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- \
  --root . \
  --job-id bgjob_minimal_eval_suite_lane_a_smoke_20260517 \
  --task-ref TASK-SECOND-READER-MEMORY-PLANNING-SLICE8C-EXECUTION \
  --lane mechanism_eval \
  --purpose "Slice 8C Lane A minimal eval smoke: V2-only user-level selective legibility" \
  --cwd . \
  --run-dir eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517 \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517/summary/aggregate.json \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517/summary/report.md \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517/summary/llm_usage.json \
  --shell-command ".venv/bin/python eval/attentional_v2/run_user_level_selective_comparison.py --run-id attentional_v2_minimal_eval_suite_lane_a_smoke_20260517 --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json --mechanism-filter attentional_v2 --judge-mode llm --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003 --note-case-id huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004"
```

## Lane B Future Command

Underlying eval command:

```bash
cd reading-companion-backend && .venv/bin/python eval/attentional_v2/run_long_span_vnext.py \
  --run-id attentional_v2_minimal_eval_suite_lane_b_smoke_20260517 \
  --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json \
  --memory-quality-probe-plan eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json \
  --memory-quality-source-run-root eval/runs/attentional_v2/attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504 \
  --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 \
  --window-limit 1 \
  --v2-only \
  --workers 1 \
  --judge-mode llm
```

Registered background-job launch shape for the later execution slice:

```bash
cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- \
  --root . \
  --job-id bgjob_minimal_eval_suite_lane_b_smoke_20260517 \
  --task-ref TASK-SECOND-READER-MEMORY-PLANNING-SLICE8C-EXECUTION \
  --lane mechanism_eval \
  --purpose "Slice 8C Lane B minimal eval smoke: V2-only long-span MQ Callback FVI" \
  --cwd . \
  --run-dir eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517 \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/aggregate.json \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/report.md \
  --expected-output eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/llm_usage.json \
  --shell-command ".venv/bin/python eval/attentional_v2/run_long_span_vnext.py --run-id attentional_v2_minimal_eval_suite_lane_b_smoke_20260517 --manifest-path eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json --memory-quality-probe-plan eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json --memory-quality-source-run-root eval/runs/attentional_v2/attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504 --segment-id huochu_shengming_de_yiyi_private_zh__segment_1 --window-limit 1 --v2-only --workers 1 --judge-mode llm"
```

## Lane B Source Policy

- Use `--memory-quality-source-run-root` to reuse completed semantic-probe outputs and probe snapshots from `attentional_v2_long_span_vnext_semantic_probe_v2_only_20260504`.
- Do not use `--memory-quality-results-source-run-root`, because copying existing Memory Quality results would not exercise a fresh smoke rejudge.
- Omit `--rerun-reaction-audit`, so reaction audit is copied from the semantic source run rather than freshly judged.
- Expected reading jobs: zero for Lane B, assuming the source outputs and probe snapshots remain present.

## Foreground / Background Policy

- Use background registered jobs for both future lane commands.
- Run Lane A first.
- Launch Lane B only after Lane A reaches a terminal registry status.
- Record job state under `reading-companion-backend/state/job_registry/`.
- Expected job ids:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517`
  - `bgjob_minimal_eval_suite_lane_b_smoke_20260517`
- Expected logs:
  - `reading-companion-backend/state/job_registry/logs/bgjob_minimal_eval_suite_lane_a_smoke_20260517.log`
  - `reading-companion-backend/state/job_registry/logs/bgjob_minimal_eval_suite_lane_b_smoke_20260517.log`
- Interruption policy: preserve partial run directories and registry logs for debugging; do not overwrite run ids.
- Resume policy: no automatic same-run-id retry. Any retry requires human approval and a new `_retry1` run id.

## LLM Cost / Judge-call Posture

- Lane A expected cost posture:
  - one fresh `attentional_v2` read for one segment
  - three note-case judge calls
- Lane B expected cost posture:
  - five Memory Quality judge calls from one selected semantic-probe window
  - zero reading jobs
  - zero fresh reaction-audit judge calls
- If LLM quota or configuration is unavailable, the future run should fail visibly.
- Do not silently switch to `--judge-mode none`.

## Expected Output Paths / Run IDs

### Lane A

Run id:

- `attentional_v2_minimal_eval_suite_lane_a_smoke_20260517`

Run directory:

- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517`

Required outputs:

- `meta/selection.json`
- `segments/huochu_shengming_de_yiyi_private_zh__segment_1.json`
- `note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002.json`
- `note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003.json`
- `note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004.json`
- `summary/aggregate.json`
- `summary/report.md`
- `summary/llm_usage.json`
- V2 runtime audit artifacts under the selected output directory

Aggregate checks:

- `run_id == "attentional_v2_minimal_eval_suite_lane_a_smoke_20260517"`
- `segment_count == 1`
- `note_case_count == 3`
- mechanisms contain only `attentional_v2`

### Lane B

Run id:

- `attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`

Run directory:

- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517`

Required outputs:

- `meta/selected_windows.json`
- `meta/output_sourcing.json`
- `summary/memory_quality_results.jsonl`
- `summary/reaction_audit_results.jsonl`
- `summary/reaction_window_summaries.jsonl`
- `summary/aggregate.json`
- `summary/report.md`
- `summary/llm_usage.json`

Aggregate checks:

- `mechanism_keys == ["attentional_v2"]`
- `probe_plan_id == "memory_quality_semantic_probe_plan_20260504"`
- `probe_selection_method == "semantic_boundary_with_distance_reference"`
- `memory_quality.window_count == 1`
- `memory_quality.probe_count == 5`
- `memory_quality_source == "fresh_judge"`
- `reaction_audit_source == "copied_from_memory_quality_source_run"`

## Evidence Catalog Policy

- Do not update `reading-companion-backend/docs/evaluation/evidence_catalog.md` during Slice 8C execution.
- Do not update `reading-companion-backend/docs/evaluation/evidence_catalog.json` during Slice 8C execution.
- The future post-run report may recommend a later diagnostic-only catalog entry.
- Any evidence-catalog update requires separate human review and explicit scope.

## Acceptance Criteria

- Static preflight checks pass before job launch.
- Lane A registered job completes successfully.
- Lane B registered job completes successfully after Lane A reaches terminal status.
- Expected output files exist for both lanes.
- Lane A aggregate checks pass.
- Lane B aggregate checks pass.
- `summary/llm_usage.json` exists for both lanes.
- No runtime mechanism, frontend, public API, eval-runner, or judge-prompt diff is introduced.
- Evidence catalog is not updated.
- Long Span vNext is not promoted to formal benchmark authority.
- The post-run report does not claim product quality from smoke results.

## Interpretation Guards

- Audit existence is not product quality.
- Retrieval availability is not utilization success.
- Visible reaction presence is not callback correctness.
- SourceRef count is not fidelity score.
- Trace existence is not planning quality.
- `slow_cycle_audit` existence is not slow-cycle quality.
- A bounded smoke run is evidence-readiness feedback, not formal product-quality proof.

## Non-goals

- No eval execution during this brief landing.
- No full AI Evaluation.
- No broad benchmark invocation.
- No cross-mechanism comparison.
- No eval-runner modification.
- No judge-prompt modification.
- No runtime behavior change.
- No prompt text/version change.
- No public API or frontend change.
- No durable mechanism state change.
- No scoring beyond existing lane metrics.
- No new metric taxonomy.
- No Long Span formal-authority promotion.
- No evidence catalog update in the execution slice unless separately scoped.

## Risks

- The future smoke can be overread as product-quality proof. Mitigation: preserve interpretation guards and report as bounded smoke evidence only.
- LLM quota or configuration can fail during Lane A or Lane B. Mitigation: fail visibly and do not silently switch to `--judge-mode none`.
- Source-run reuse assumptions for Lane B can drift if local run artifacts are missing or altered. Mitigation: preflight source-run existence and selected aggregate fields before launch.
- Partial run directories can be created by interrupted jobs. Mitigation: preserve them for debugging and require a new retry run id.
- Lane A may take longer than expected because it includes one fresh V2 read. Mitigation: use registered background jobs, logs, and status files.

## Rollback / Cleanup Plan

- Never overwrite an existing run id.
- Preserve failed or partial run directories for debugging.
- Mark failed registry jobs as failed or abandoned through the registry tooling.
- Do not catalog failed outputs.
- Do not manually splice partial outputs into evidence summaries.
- Any retry must use a new `_retry1` run id after human approval.
- Reverting this brief landing is a docs-only revert with no runtime cleanup.

## Open Questions

None blocking.

Default decisions:

- Include both Lane A and Lane B because Slice 8B framed the Minimal Eval Suite around both active lanes.
- Keep Lane A V2-only and one segment / three note cases.
- Keep Lane B V2-only and one window / five semantic probes.
- Use fresh Memory Quality rejudge for Lane B and copied reaction audit.
- Avoid reading jobs for Lane B by reusing semantic source outputs.
- Keep evidence catalog unchanged until a later human-reviewed report scopes any catalog entry.

## Go / No-go Recommendation

Go for human review of this Slice 8C Pre-implementation Brief.

No-go for actual eval execution, benchmark jobs, judge calls, reading jobs, eval run directories, runner changes, evidence-catalog changes, or formal-authority promotion until this brief is accepted and execution is explicitly requested.

## Brief Landing Validation

Run only static/doc checks for this Slice 8C brief landing:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

The forbidden runtime/frontend/eval-runner diff check must return empty output.
