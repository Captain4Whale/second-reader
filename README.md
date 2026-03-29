# Reading Companion Workspace

Purpose: provide setup, run, environment, local URL, and verification information for the workspace.
Use when: installing dependencies, starting local services, checking env vars, or running validation commands.
Not for: product flow decisions, public API contract details, runtime semantics, or temporary migration notes.
Update when: install/setup commands, startup commands, environment variables, default URLs, or validation commands change.

This directory is the unified working root for the Reading Companion project.

The project is maintained as one product with two sub-applications:
- `reading-companion-backend`: FastAPI API, upload/job orchestration, sequential deep-reading engine
- `reading-companion-frontend`: Vite/React web UI

## Structure
- `reading-companion-backend/`: backend code, runtime artifacts, tests, `.env`
- `reading-companion-frontend/`: frontend code, Vite app, `.env.example`
- `docs/`: workspace-level stable docs and temporary handoff notes
- `docs/tasks/`: workspace task index for agent switching
- `scripts/`: root task wrappers used by the `Makefile`

## Quick Start
1. Run `make doctor`
2. Install Python 3.11 or newer if the doctor script reports it missing
3. Run `make setup`
4. Start the backend with `make dev-backend`
5. Start the frontend with `make dev-frontend`
6. Or run both together with `make dev`
7. For a more stable local demo loop, use `make run-demo`

## Default Local URLs
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/api/health`

## Environment
Backend environment lives in `reading-companion-backend/.env`.

Important backend variables:
- `LLM_TARGETS_PATH`
- `LLM_PROFILE_BINDINGS_PATH`
- optional `LLM_TARGETS_JSON`
- optional `LLM_PROFILE_BINDINGS_JSON`
- compatibility: `LLM_REGISTRY_PATH`, `LLM_REGISTRY_JSON`
- `TAVILY_API_KEY`
- `UPLOAD_MAX_BYTES`
- `BACKEND_RUNTIME_ROOT`
- `BACKEND_CORS_ORIGINS`
- `BACKEND_HOST`
- `BACKEND_PORT`

Recommended local LLM setup:
- point the backend at two untracked local JSON files from `reading-companion-backend/.env`:
  - `LLM_TARGETS_PATH=config/llm_targets.local.json`
  - `LLM_PROFILE_BINDINGS_PATH=config/llm_profile_bindings.local.json`
- edit `reading-companion-backend/config/llm_targets.local.json` to define named runtime targets
  - write the provider `contract`, `base_url`, `model`, and one or more credentials there
  - this is the file where you put URL, model name, and API key information
- edit `reading-companion-backend/config/llm_profile_bindings.local.json` to bind stable project profile ids to those named targets
  - current stable profile ids are:
    - `runtime_reader_default`
    - `dataset_review_high_trust`
    - `eval_judge_high_trust`
  - this is the file where you choose which target each profile uses and any profile-level overrides such as `temperature`, `max_output_tokens`, `retry_attempts`, `max_concurrency`, `quota_retry_attempts`, and `quota_wait_budget_seconds`

Tracked templates for the new local setup:
- `reading-companion-backend/config/llm_targets.local.example.json`
- `reading-companion-backend/config/llm_profile_bindings.local.example.json`

Compatibility and fallback modes:
- inline equivalents also work:
  - `LLM_TARGETS_JSON`
  - `LLM_PROFILE_BINDINGS_JSON`
- the older single registry surface still works:
  - `LLM_REGISTRY_PATH`
  - `LLM_REGISTRY_JSON`
- legacy env-only fallback still works when no structured config is provided:
  - `LLM_PROVIDER_CONTRACT`
  - `LLM_BASE_URL`
  - `LLM_API_KEY`
  - `LLM_MODEL`
  - optional `LLM_DATASET_REVIEW_MODEL`
  - optional `LLM_EVAL_JUDGE_MODEL`
  - optional `LLM_RUNTIME_MAX_OUTPUT_TOKENS`
  - optional `LLM_DATASET_REVIEW_MAX_OUTPUT_TOKENS`
  - optional `LLM_EVAL_JUDGE_MAX_OUTPUT_TOKENS`

Reference and compatibility files:
- shared provider/profile registry example:
  - `reading-companion-backend/config/llm_registry.example.json`
- Minimax-focused compatibility-mode registry:
  - `reading-companion-backend/config/llm_registry.minimax_legacy_compatible.json`

The shared LLM layer still supports:
- provider contracts such as `anthropic`, `google_genai`, and `openai_compatible`
- multiple credentials inside one named target for same-model failover
- adaptive same-key concurrency policy:
  - `initial_max_concurrency`
  - `probe_max_concurrency`
  - `min_stable_concurrency`
  - `backoff_window_seconds`
  - `recover_window_seconds`
- quota-pressure coordination policy:
  - `quota_cooldown_base_seconds`
  - `quota_cooldown_max_seconds`
  - `quota_state_ttl_seconds`
- stable project profile ids with profile-level invocation settings:
  - `runtime_reader_default`
  - `dataset_review_high_trust`
  - `eval_judge_high_trust`

Current backend defaults are now throughput-oriented for new Python processes:
- same-key parallelism is enabled by default
- provider concurrency starts at `6`, can probe up to `12`, and backs off automatically on sustained timeout/rate-limit pressure
- provider quota cooldown state is shared under `BACKEND_RUNTIME_ROOT/state/llm_gateway/providers/` so sibling Python processes can honor the same bounded wait window
- runtime keeps a short bounded quota wait budget before surfacing `llm_quota`, while dataset review and eval judge profiles keep a longer bounded quota wait budget for offline work
- eval/review worker counts derive from the shared concurrency policy rather than fixed script-local defaults

Frontend environment is optional for local development and can be set via `reading-companion-frontend/.env.local`.

Important frontend variables:
- `VITE_API_BASE_URL`
- `VITE_WS_BASE_URL`

## Common Commands
- `make doctor`: validate prerequisites, ports, and env files
- `make setup`: install frontend deps and create/install backend virtualenv
- `make dev-backend`: run FastAPI from the workspace root safely
- `make dev-frontend`: run Vite with the shared API defaults
- `make dev`: run both apps together
- `make run-demo`: run frontend plus a supervised non-reload backend that auto-restarts if it exits
- `make test`: run backend tests, frontend typecheck/build, and contract drift checks
- `make contract-check`: verify docs appendix, backend OpenAPI snapshot, and frontend contract guards
- `make e2e`: run the fixture-backed upload -> analysis -> book -> chapter -> marks Playwright flow
- `make build`: build the frontend bundle
- `make agent-context`: print the canonical agent-switching brief from current state, tasks, jobs, and git status
- `make agent-check`: run contract/doc checks plus switching-memory traceability warnings
- `make backfill-covers`: scan existing backend outputs, extract missing EPUB covers, and refresh manifests
- `make dataset-review-pipeline DATASET_REVIEW_PIPELINE_ARGS="..."`: run the reusable mechanical dataset-review packet pipeline from the workspace root
- `cd reading-companion-frontend && npm run generate-api-types`: refresh generated frontend API types after the backend OpenAPI snapshot changes

## Dataset Review Pipeline
Use the reusable dataset-review pipeline when the work is limited to the mechanical packet lifecycle:
- generate a revision/replacement packet
- run packet case-design audit
- run LLM packet adjudication
- import and archive the packet
- refresh the review queue summary
- emit a final stop-and-summarize report

The pipeline intentionally stops there. It does not reopen benchmark promotion, freeze reviewed slices, or launch durable-trace, re-entry, or runtime-viability work automatically.

Current local-only English cleanup example:
- `make dataset-review-pipeline DATASET_REVIEW_PIPELINE_ARGS="--dataset-id attentional_v2_private_library_excerpt_en_v2 --family excerpt_cases --storage-mode local-only --packet-id attentional_v2_private_library_cleanup_en_example"`

Long-running wrapper example:
- `cd reading-companion-backend && .venv/bin/python scripts/run_registered_job.py --task-ref "execution-tracker#example" --lane dataset_growth --purpose "English dataset review pipeline" --cwd "$PWD" -- .venv/bin/python -m eval.attentional_v2.run_dataset_review_pipeline --dataset-id attentional_v2_private_library_excerpt_en_v2 --family excerpt_cases --storage-mode local-only --packet-id attentional_v2_private_library_cleanup_en_example`

## Long-Running Eval Jobs
Use the backend background-job registry for evaluation, packet review, or dataset jobs that may run for `10-15` minutes or longer.

- Register or update one job:
  - `cd reading-companion-backend && .venv/bin/python scripts/register_background_job.py --task-ref "execution-tracker#example" --lane mechanism_eval --purpose "English chapter-core rerun" --command ".venv/bin/python eval/attentional_v2/run_chapter_comparison.py --help" --cwd "$PWD"`
- Launch one generic job through the registry wrapper:
  - `cd reading-companion-backend && .venv/bin/python scripts/run_registered_job.py --task-ref "execution-tracker#example" --lane mechanism_eval --purpose "English chapter-core rerun" --cwd "$PWD" -- .venv/bin/python eval/attentional_v2/run_chapter_comparison.py --help`
- Refresh active jobs:
  - `cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py`
- Refresh and also execute stored `check_command` probes:
  - `cd reading-companion-backend && .venv/bin/python scripts/check_background_jobs.py --run-check-commands`

Registry files live under `reading-companion-backend/state/job_registry/`:
- `jobs/<job_id>.json`: canonical per-job source of truth for product and offline jobs
- `active_jobs.json`: derived active-job view for operator-facing long-running offline work
- `active_jobs.md`: human-readable mirror for handoff and agent recovery
- `history_jobs.jsonl`: archived terminal jobs

## Validation
- `make contract-check` is the first guard for public contract drift.
- `make agent-check` is the canonical switching-memory guard for current state, task routing, and handoff hygiene.
- `make e2e` is the canonical upload -> analysis -> book -> chapter -> marks regression.

## Next Docs
- Start with `AGENTS.md` for workspace rules and document routing.
- Read `docs/current-state.md` for canonical live project status.
- Read the relevant child `AGENTS.md` before making subproject-local changes.
- Read `docs/tasks/registry.md` for the active task router and evidence chain.
- Read `docs/source-of-truth-map.md` when deciding where durable information belongs.
