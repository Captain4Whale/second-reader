# Slice 7B: Minimal Eval Smoke Harness and Evidence Availability Validation - Pre-implementation Brief v0

## PR Title

`Slice 7B: Minimal Eval Smoke Harness and Evidence Availability Validation`

## Implementation Slice

Slice 7B is a small, reversible sub-slice of Slice 7 / Minimal Eval Implementation.

This slice builds on the accepted Slice 7A static inventory manifest and defines a minimal non-LLM smoke validator for eval asset availability and evidence-surface wiring. It is not an evaluation execution slice, not a benchmark redesign, and not a runtime mechanism change.

## Design Sources

- `E实施1-Implementation Feasibility & Delta Audit v0.md`
- `E实施0-Implementation Roadmap & Handoff v0.md`
- `C设计9-Evaluation Calibration & Minimal Eval Suite v0.md`
- `docs/backend-reader-evaluation.md`
- `reading-companion-backend/docs/evaluation/README.md`
- `reading-companion-backend/docs/evaluation/user_level/README.md`
- `reading-companion-backend/docs/evaluation/long_span/README.md`
- `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`
- `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- Slice 7A Pre-implementation Brief
- Slice 7A Post-implementation Report
- `codex/E实施-progress-ledger.md` reviewer constraints

## Current Code Facts

- Slice 7A added `reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json`.
- The manifest preserves exactly two active lanes:
  - Lane A: `lane_a_local_user_level_selective_legibility`
  - Lane B: `lane_b_long_span_mq_callback_fvi`
- Lane A remains the active local / user-level benchmark lane and distinguishes:
  - current active dataset pointer: `attentional_v2_user_level_selective_v1_repaired_20260422`
  - current formal evidence bundle dataset boundary: `attentional_v2_user_level_selective_v1_repaired_20260416`
- Lane B remains `diagnostic_phase_1` with `formal_authority=false`.
- Slice 7A's static validation test already checks manifest parseability, lane separation, tracked path existence, explicit `local_only` handling, required evidence surface IDs, interpretation guards, and non-scoring diagnostic additions.
- Existing eval runners can run reading jobs and judge calls, so Slice 7B must not import, invoke, or modify them.
- The smallest remaining gap is a reusable smoke command that validates the accepted manifest without relying on pytest as the only entrypoint.

## Files To Change In Future PR

- `reading-companion-backend/scripts/validate_minimal_eval_inventory_smoke.py`
- `reading-companion-backend/tests/test_attentional_v2_minimal_eval_inventory.py`
- Optionally `reading-companion-backend/docs/evaluation/README.md` for a short smoke-command pointer
- Slice 7B Post-implementation Report
- Initiative status docs:
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
- existing eval runners, including:
  - `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
  - `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
- judge prompts
- durable mechanism state
- public API
- frontend

## Planned Deltas

Future Slice 7B implementation should add a tiny stdlib-only smoke validator script that reads the Slice 7A manifest and exits nonzero on contract violations.

The validator should check:

- manifest ID, schema version, status, and purpose;
- exactly the two active lane IDs required by Slice 7A;
- tracked `workspace_path` existence;
- explicit `local_only` handling, with missing local-only paths reported but not failed;
- required evidence surface IDs;
- expected artifact / field-name wiring for key evidence surfaces;
- Planning Trace Quality and Slow-cycle Safety remain diagnostic-only and non-scoring;
- interpretation guards remain present and true.

The validator should emit a compact JSON summary to stdout with:

- `status`;
- `manifest_id`;
- `lane_ids`;
- `evidence_surface_ids`;
- `tracked_path_count`;
- `local_only_present_count`;
- `local_only_missing_count`;
- `diagnostic_ids`.

The validator must not:

- import eval runners;
- call LLMs or judges;
- create run directories;
- write smoke outputs by default;
- launch reading jobs;
- inspect runtime artifacts beyond path existence;
- change runtime mechanism behavior.

Tests should invoke the validator against the committed manifest and include at least one negative temp-manifest case for guard or evidence-surface validation.

## Engineering Validation Commands

Future implementation should run only:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2_minimal_eval_inventory.py -q
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py
```

## Smoke Validation Proposal

Use a small non-LLM script rather than a new benchmark, new platform, or eval-runner modification.

Recommended future command:

```bash
cd reading-companion-backend && .venv/bin/python scripts/validate_minimal_eval_inventory_smoke.py --manifest eval/manifests/attentional_v2_minimal_eval_inventory_v1.json
```

Expected behavior:

- Return exit code `0` for the accepted Slice 7A manifest.
- Print a compact JSON smoke summary.
- Treat missing `local_only` paths as allowed and reported.
- Fail if tracked assets are missing, lanes are changed, historical assets are promoted, diagnostic additions become scoring, or interpretation guards are removed / false.

## Non-goals

- No full AI Evaluation.
- No benchmark jobs.
- No judge calls.
- No reading jobs.
- No eval-runner modification.
- No runtime mechanism behavior change.
- No new metric taxonomy.
- No scoring.
- No new benchmark platform.
- No Long Span vNext formal-authority promotion.
- No inference that retrieval availability is utilization success.
- No inference that visible reaction presence is callback correctness.
- No inference that SourceRef count is fidelity score.
- No inference that trace existence is planning quality.
- No inference that `slow_cycle_audit` existence is slow-cycle quality.

## Risks

- A smoke validator could be mistaken for eval result evidence. Mitigation: name it and document it as evidence-availability validation only.
- Artifact / field-name validation could become too brittle. Mitigation: validate exact IDs and high-signal field tokens, not prose.
- A script under `scripts/` may be missed by eval users. Mitigation: add a small evaluation README pointer.
- Local-only paths may be absent in other clones. Mitigation: report absent local-only paths as availability state, not failure.

## Rollback Plan

Revert the future Slice 7B PR. The script, tests, report, and status-doc updates are static/read-only and require no migration.

## Open Questions

None blocking.

Default decision: implement a tiny non-LLM smoke validator script plus tests; do not modify eval runners.

## Go / No-go Recommendation

Go for human review of this Slice 7B Pre-implementation Brief.

No-go for implementation, eval execution, judge calls, reading jobs, or eval-runner changes until this brief is accepted.
