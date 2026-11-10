# Reading Companion Workspace

Fixed-history Digest replay completed A1, A2 and B over the authorized 16 units.
A2/B ran at clean `ca4e28c`; A1/B are packaged for blind review with the frozen
16-unit `experiments/unit-sets/diag-001.json` subset.
See [status and evidence](docs/tasks/q1-digest-replay-2026-11-08.md).
From the backend, reconstruct without calling a model with
`.venv/bin/python scripts/rerun_fixed_history_digest.py --source-backend /absolute/original/backend --run-id RUN --unit-id UNIT --output state/experiments/NEW-DIR --prepare-only`.
The CLI also accepts `--model`, `--reasoning-effort` and `--prompt-version` for an
authorized live invocation. One pilot does not establish all-unit acceptance.

For the registered A1-only selection, run `scripts/run_fixed_history_a1.py` with
`--source-backend SOURCE --output-root state/experiments/q1_digest_fixed_history_20261108`
to freeze and verify inputs, then add `--execute` to consume that preflight. Existing
results are reused only after matching their model/config and full rendered input.
ID/order/body mismatches stop before the affected model call; reports stay under
the ignored `A1-full/` output directory. No A2/B generation is part of this command.
For offline importer export, use `scripts/export_fixed_history_digest.py --group-root GROUP_DIR --unit-set experiments/unit-sets/diag-001.json --source-backend SOURCE --experiment-id REGISTERED_ID --run-id REGISTERED_RUN --output state/experiments/NEW-DIR/group.json`. Then pass that same `--unit-set` and both group exports to `scripts/build_q1_comparison.py`; see the replay task record for the retained blind batch.

Purpose: provide setup, run, environment, local URL, and verification information for the workspace.
Use when: installing dependencies, starting local services, checking env vars, or running validation commands.
Not for: product flow decisions, public API contract details, runtime semantics, or temporary migration notes.
Update when: install/setup commands, startup commands, environment variables, default URLs, or validation commands change.

This directory is the unified working root for the Reading Companion project.

The project is maintained as one product with two sub-applications:
- `reading-companion-backend`: FastAPI API, upload/job orchestration, sequential deep-reading engine
- `reading-companion-frontend`: Vite/React web UI

## Step 0 清理后的运行边界

正常运行仅支持 `attentional_v2`。`iterator_v1` / `both` / `book_analysis` 选项显式报已退役；API enum 暂保留。只支持当前 chapter-planner schema 3 新建 run 的 resume，旧 checkpoint 错误提示 tag `pre-cleanup-2026-11`。旧书只读显示、启动 backfill、前端与 Annotation Pack 保留。验证和备份见 [执行记录](docs/tasks/lightweight-cleanup-step0-execution-2026-11-01.md)。

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
8. If you want the stack to survive a Codex or terminal restart, use the detached commands:
   - `make start-local-stack`
   - `make status-local-stack`
   - `make stop-local-stack`
9. Optional local runtime traces use a separately managed Phoenix sidecar:
   - `make setup-phoenix`
   - `make start-phoenix`
   - `make status-phoenix`
   - `make stop-phoenix`

## Default Local URLs
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/api/health`
- Optional Phoenix UI: `http://127.0.0.1:6006`
- Optional Phoenix OTLP/HTTP collector: `http://127.0.0.1:6006/v1/traces`

## Environment
Backend environment lives in `reading-companion-backend/.env`.

Important backend variables:
- `LLM_TARGETS_PATH`
- `LLM_PROFILE_BINDINGS_PATH`
- `CPA_PROXY_API_KEY`
- optional `LLM_TARGETS_JSON`
- optional `LLM_PROFILE_BINDINGS_JSON`
- optional operator overrides: `LLM_FORCE_TARGET_ID`, `LLM_FORCE_TIER_ID`
- optional product-path override: `BACKEND_READING_MECHANISM`
- compatibility: `LLM_REGISTRY_PATH`, `LLM_REGISTRY_JSON`
- `TAVILY_API_KEY`
- `UPLOAD_MAX_BYTES`
- `BACKEND_RUNTIME_ROOT`
- `BACKEND_CORS_ORIGINS`
- `BACKEND_HOST`
- `BACKEND_PORT`
- optional runtime telemetry switch: `READING_OBSERVABILITY_OTLP_ENABLED`
- optional OTLP/HTTP endpoint: `READING_OBSERVABILITY_OTLP_ENDPOINT`
- optional trace project: `READING_OBSERVABILITY_PROJECT`
- optional OpenTelemetry service identity: `OTEL_SERVICE_NAME`
- privacy controls: `OPENINFERENCE_HIDE_INPUTS`, `OPENINFERENCE_HIDE_OUTPUTS`, `OPENINFERENCE_HIDE_LLM_INVOCATION_PARAMETERS`, `OPENINFERENCE_HIDE_LLM_TOOLS`, `OPENINFERENCE_HIDE_EMBEDDING_VECTORS`

Relative backend config paths resolve from `reading-companion-backend/`, not from the shell cwd.
- this applies to `BACKEND_RUNTIME_ROOT`, `LLM_TARGETS_PATH`, `LLM_PROFILE_BINDINGS_PATH`, and `LLM_REGISTRY_PATH`
- keeping `BACKEND_RUNTIME_ROOT=.` in `reading-companion-backend/.env` is therefore safe when you launch backend scripts from the workspace root

Recommended local LLM setup:
- point the backend at two untracked local JSON files from `reading-companion-backend/.env`:
  - `LLM_TARGETS_PATH=config/llm_targets.local.json`
  - `LLM_PROFILE_BINDINGS_PATH=config/llm_profile_bindings.local.json`
- edit `reading-companion-backend/config/llm_targets.local.json` to define named runtime targets
  - current local operation uses CPA Manager Plus on `http://127.0.0.1:8317/v1` with `CPA_PROXY_API_KEY`
  - the default target is `cpa_codex_local` / `gpt-5.6-luna`, with explicit `reasoning_effort: medium`
  - write the provider `contract`, `base_url`, `model`, and credential env-var reference there
  - keep the real API key in `reading-companion-backend/.env`, not in tracked JSON
  - supported provider contracts include `anthropic`, `google_genai`, and `openai_compatible`
  - `openai_compatible` targets require the backend dependencies `langchain-openai`, `openai`, and `instructor`; Instructor is used only as an optional structure/validation aid and does not replace project validators
  - `provider_options` may be set on a target for provider-specific request options such as `response_format`, `thinking`, or `reasoning_effort`
  - `concurrency_strategy` may be set on a target:
    - omit it, or set `adaptive`, for conservative targets that should back off after provider pressure
    - set `fixed` only for trusted high-throughput targets whose key can sustain the declared `probe_max_concurrency`; quota cooldown and retry handling still apply
- edit `reading-companion-backend/config/llm_profile_bindings.local.json` to bind stable project profile ids to those named targets
  - current stable profile ids are:
    - `runtime_reader_default`
    - `dataset_review_high_trust`
    - `eval_judge_high_trust`
  - the recommended universal pattern is ordered `target_tiers`
    - put the preferred high-throughput target in the `primary` tier
    - put backup targets in later tiers
    - each scope chooses one concrete target up front and stays pinned to it for the full runtime, dataset-review, or evaluation scope
    - when one tier lists multiple `target_ids`, that tier acts as a same-priority dispatch pool rather than a strict first-success fallback chain
    - within one pooled tier, new sibling scopes may fan out across different targets, but each scope still pins one concrete target for its full lifetime
    - sibling Python processes now share a pooled-tier dispatch cursor under `BACKEND_RUNTIME_ROOT/state/llm_gateway/tier_dispatch/`, so future launches do not all restart from the first target in the tier
    - already-running scopes are not rebalanced mid-flight; if you want a live job to pick up new pooled-routing behavior, relaunch that job
  - this is the file where you choose which target tier policy each profile uses and any profile-level overrides such as `temperature`, `max_output_tokens`, `retry_attempts`, `max_concurrency`, `quota_retry_attempts`, and `quota_wait_budget_seconds`
  - `retry_attempts` means total provider-call attempts, including the first call; for example, `retry_attempts: 3` means one initial try plus up to two call-level retries before a higher runner layer decides whether to recover, partialize, or fail
  - `provider_options` may also be set per profile; profile options override target options at invocation time

Recommended tiered binding shape:
```json
{
  "profiles": [
    {
      "profile_id": "runtime_reader_default",
      "target_tiers": [
        {
          "tier_id": "primary",
          "target_ids": ["cpa_codex_local"],
          "min_required_stable_concurrency": 1
        }
      ],
      "temperature": 0.2,
      "max_output_tokens": 4096,
      "timeout_seconds": 120,
      "retry_attempts": 3,
      "max_concurrency": 1,
      "default_burst_concurrency": 1,
      "quota_retry_attempts": 2,
      "quota_wait_budget_seconds": 25
    }
  ]
}
```

Tracked templates for the new local setup:
- `reading-companion-backend/config/llm_targets.local.example.json`
- `reading-companion-backend/config/llm_profile_bindings.local.example.json`

CPA Luna OpenAI-compatible target:
```json
{
  "target_id": "cpa_codex_local",
  "contract": "openai_compatible",
  "base_url": "http://127.0.0.1:8317/v1",
  "model": "gpt-5.6-luna",
  "credentials": [
    {
      "credential_id": "local_proxy",
      "api_key_env": "CPA_PROXY_API_KEY"
    }
  ],
  "provider_options": {
    "reasoning_effort": "medium"
  },
  "timeout_seconds": 180,
  "retry_attempts": 2,
  "max_concurrency": 1,
  "initial_max_concurrency": 1,
  "probe_max_concurrency": 1,
  "min_stable_concurrency": 1,
  "concurrency_strategy": "adaptive"
}
```
- project tools stay in the internal canonical shape `name`, `description`, `input_schema`
- the Anthropic adapter emits Anthropic-style tool definitions; the OpenAI-compatible adapter emits OpenAI function tools and maps forced tool choice at the adapter boundary
- current CPA Luna Ingest/Digest calls use OpenAI-compatible function tools for final structured output plus the existing local validator/repair boundary
- `reasoning_effort: medium` is declared at target level, so runtime, dataset review, and eval judge inherit the same reasoning setting
- `retrieve_unit_memory` remains a normal `tool_choice="auto"` action tool; it is not forced merely to carry final structured output
- standard runtime artifacts and traces should not store raw reasoning/thinking content; keep only normal content, usage, and metadata unless a debug trace explicitly opts in
- the current CPA / Luna policy and historical OpenCode / MiniMax transport notes live in `docs/implementation/new-reading-mechanism/llm-structured-output-protocol-note.md`

Compatibility and fallback modes:
- `BACKEND_READING_MECHANISM`
  - unset or `attentional_v2`: use the normal default deep-reading path
  - `iterator_v1`: force the legacy-compatible fallback reader for new launches
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
  - optional `LLM_REASONING_EFFORT` (defaults to `medium` for the OpenAI-compatible legacy fallback)
  - optional `LLM_DATASET_REVIEW_MODEL`
  - optional `LLM_EVAL_JUDGE_MODEL`
  - optional `LLM_RUNTIME_MAX_OUTPUT_TOKENS`
  - optional `LLM_DATASET_REVIEW_MAX_OUTPUT_TOKENS`
  - optional `LLM_EVAL_JUDGE_MAX_OUTPUT_TOKENS`

Reference and compatibility files:
- shared provider/profile registry example:
  - `reading-companion-backend/config/llm_registry.example.json`
- tracked examples and current local profiles use CPA Luna. OpenCode Go, DeepSeek, and MiniMax references are historical only and require an explicit reintroduction plus a fresh health check before use.

The shared LLM layer still supports:
- provider contracts such as `anthropic`, `google_genai`, and `openai_compatible`
- multiple credentials inside one named target for same-model failover
- ordered target tiers for profile routing
  - primary and backup routing is no longer hardcoded to one provider family
  - one tier may represent a same-priority target pool or a single preferred target
  - when a tier lists multiple targets, new scopes fan out across targets that still have available stable capacity, then stay pinned to the selected target for the whole scope
  - when you want true fallback semantics, put the backup target in a later tier instead of appending it to the same tier
- adaptive same-key concurrency policy:
  - `initial_max_concurrency`
  - `probe_max_concurrency`
  - `min_stable_concurrency`
  - `concurrency_strategy`
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

Temporary operator overrides:
- `LLM_FORCE_TARGET_ID`
  - force new scopes onto one named target for debugging or recovery
- `LLM_FORCE_TIER_ID`
  - force new scopes onto one named tier such as `primary` or `backup`
- these overrides apply only when a new scope starts and should not be the normal policy surface

Current CPA backend defaults are conservative for new Python processes:
- runtime, dataset review, and eval judge all route to `cpa_codex_local`
- provider and profile concurrency are capped at `1` while the subscription proxy is characterized
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
- `make start-backend-detached`: start the stable backend in the background with logs and pid tracking under `reading-companion-backend/state/local_stack/`
- `make start-frontend-detached`: start the frontend dev server in the background with logs and pid tracking under `reading-companion-backend/state/local_stack/`
- `make start-local-stack`: start both detached services so they survive Codex or terminal restarts
- `make status-local-stack`: show detached backend/frontend status
- `make stop-local-stack`: stop the detached backend/frontend services
- `make setup-phoenix`: create the isolated repo-local Phoenix virtualenv and install pinned server `20.2.1`
- `make start-phoenix`: explicitly start the loopback-only Phoenix collector/UI; never called by normal app launchers
- `make status-phoenix`: show installation, PID, UI readiness, endpoints, and state path without starting Phoenix
- `make stop-phoenix`: stop only the PID verified as the repo-local Phoenix sidecar and preserve its data
- `make test`: run backend tests, frontend typecheck/build, and contract drift checks
- `make reading-product-contract-check`: verify the mechanism-neutral Reading Product Output v1 schemas, examples, semantic invariants, runtime copy, and unified strict GitHub Pages projection without network or model access
- `make annotation-pack-contract-check`: verify the minimal Annotation Pack v0 W3C/DC schema, examples, generated bindings/runtime copies, tracked Tiny Reader JSON/package golden, and strict GitHub Pages projection without network access
- `make contract-check`: verify docs appendix, backend OpenAPI snapshot, and frontend contract guards
- `make e2e`: run the fixture-backed upload -> analysis -> book -> chapter -> marks Playwright flow
- `make build`: build the frontend bundle
- `make agent-context`: print the canonical agent-switching brief from current state, tasks, jobs, and git status
- `make agent-check`: run contract/doc checks plus switching-memory traceability warnings
- `make backfill-covers`: scan existing backend outputs, extract missing EPUB covers, and refresh manifests
- `make dataset-review-pipeline DATASET_REVIEW_PIPELINE_ARGS="..."`: run the reusable mechanical dataset-review packet pipeline from the workspace root
- `make library-source-intake LIBRARY_SOURCE_INTAKE_ARGS="..."`: ingest books from the managed library inbox into canonical local source storage and the source catalog
- `make closed-loop-benchmark-curation CLOSED_LOOP_BENCHMARK_CURATION_ARGS="..."`: run the first scratch-safe closed-loop benchmark-curation pass for the managed local supplement
- `cd reading-companion-frontend && npm run generate-api-types`: refresh generated frontend API types after the backend OpenAPI snapshot changes

## Annotation Pack v0 Explicit Export

Annotation Pack export is an opt-in operator action. It is not called by normal reading completion and does not change the Agent, Digest, Memory, reading loop, Library, Reader, or public HTTP API. The default deliverable is the formal detached `.annotations` package together with its canonical development JSON.

Minimal v0 emits a strict W3C Web Annotation/Dublin Core `AnnotationSet`: one exact EPUB is identified by `dc:identifier = ["nih:sha-256;<exact EPUB SHA-256>"]`, and each Highlight or Note targets a relative EPUB XHTML href with an exact `TextQuoteSelector` followed by a Unicode-code-point `TextPositionSelector`. The public Pack has no `sr:*`, custom context/namespace, Work/Edition/File hierarchy, Track, chapter fingerprint, provenance, or public digest. The local validation report and `current.json` pointer remain internal publication companions; neither is part of `annotations.json` or the detached package.

From the backend directory, attempt an explicit export for one existing output that has an exact source EPUB, a coherent parser-built `BookDocument`, and a supported current phase9 settled producer ledger:

```bash
cd reading-companion-backend
BOOK_ID="replace-with-existing-book-id"
.venv/bin/python scripts/export_annotation_pack.py \
  --book-id "$BOOK_ID" \
  --track-key second-reader-agent \
  --track-name "Second Reader" \
  --creator-type Software \
  --creator-id urn:uuid:c8d82077-7433-5fe9-9075-01f3e3100656 \
  --creator-name "Second Reader"
```

The track/creator arguments select and validate the local publication lane; minimal v0 does not copy them into the public Pack. Historical phase8 or otherwise unsupported producer records fail closed rather than being upgraded. The current `attentional_v2-phase9` requirement belongs only to `SecondReaderProducerAdapter`: future mechanisms may use different private formats, but must map `kind`, exact shared-source range/quote, conditional Note text, and settlement time into the producer-neutral handoff defined by the canonical contract README. This command is an operator entrypoint, not evidence that every existing full-book output is currently exportable.

`--book-output-dir` is the mutually exclusive operator/testing alternative to `--book-id`; it must still resolve inside the configured `<BACKEND_RUNTIME_ROOT>/output` tree. A successful detached export writes one complete immutable revision under:

```text
<BACKEND_RUNTIME_ROOT>/output/<book_id>/public/annotation-packs/<track_slug>/
├── current.json
└── revisions/<revision_id>/
    ├── annotations.json
    ├── <track_slug>.annotations
    └── validation-report.json
```

The exporter writes and freezes the full revision before atomically selecting it through `current.json`. The internal pointer binds the relative paths and SHA-256 digests of JSON, package, and report; the internal validation report carries sanitized producer/adapter metadata and findings. The command summary contains safe ids, digests, counts, and finding codes; it intentionally omits local paths and annotation text.

Validate and inspect either artifact independently, without the source EPUB, BookDocument, or producer ledger:

```bash
cd reading-companion-backend
ANNOTATIONS_JSON="/absolute/path/to/public/annotation-packs/track/revisions/revision/annotations.json"
ANNOTATIONS_PACKAGE="/absolute/path/to/public/annotation-packs/track/revisions/revision/track.annotations"
.venv/bin/python scripts/validate_annotation_pack.py "$ANNOTATIONS_JSON"
.venv/bin/python scripts/validate_annotation_pack.py "$ANNOTATIONS_PACKAGE"
.venv/bin/python scripts/inspect_annotation_pack.py "$ANNOTATIONS_PACKAGE"
```

The detached artifact has media type `application/zip;profile="https://www.w3.org/TR/epub-anno-10/"` and exactly one root entry, `annotations.json`. It never contains the EPUB, validation report, XHTML, cover, source assets, or private runtime state. Validation performs bounded classic-ZIP envelope/DEFLATE/CRC checks and full canonical Pack validation without extracting to disk. `--schema-only` never bypasses package security or canonical-byte checks. An intentionally empty export must be revalidated with explicit `--allow-empty`; that policy flag is semantic-only and cannot be combined with `--schema-only`.

Use `--deliverables json` only when a development JSON-only revision is intentionally required. `json` is a minimum requirement: once a track has a detached current revision, later JSON requests do not retract the package. A non-forced JSON-only-to-detached upgrade packages the exact already-published `annotations.json` bytes in a new complete revision, revalidates the package and report, and leaves the old JSON-only revision unchanged. Repeating the same request verifies the selected revision and returns `unchanged` instead of rewriting it.

Standalone contract `Annotation` examples are schema fragments rather than full semantic Packs, so validate them only with the explicit schema-only mode:

```bash
cd reading-companion-backend
.venv/bin/python scripts/validate_annotation_pack.py \
  --schema-only ../contract/annotation-pack/v0/examples/*.json
```

The policy flags are independent:

- `--allow-partial` permits a stable settled snapshot from a paused/error run; it does not permit invalid-row skips.
- `--allow-skips` permits annotation-level invalid rows to be skipped when a valid item remains; it does not permit partial or empty exports.
- `--allow-empty` permits an explicitly empty Pack for the selected internal publication lane where the run-state policy allows it; it is not a quality claim.
- `--force-regenerate` requests a fresh publication pass rather than the ordinary verified no-op path; it does not retract an already-published detached deliverable.

Package generation fixes the root name, timestamp, Unix regular-file mode, DEFLATE level, entry order, and comments/extra fields. Byte reproducibility is a Second Reader project rule within the supported toolchain, not a W3C requirement or a promise that different zlib versions emit the same DEFLATE bitstream. Independent validation checks the observable safe envelope and uncompressed canonical JSON rather than requiring local recompression byte equality. Minimal v0 has no project JSON-LD namespace or custom context. The GitHub Pages-shaped schema IRI remains a reserved future location, but public hosting is explicitly deferred under `DEC-159`; the current workflow validates projection bytes only and does not upload or deploy a site.

The tracked public-safe end-to-end proof lives at `reading-companion-backend/tests/annotation_pack/fixtures/tiny-reader/`. Its deterministic builder creates a small real two-resource EPUB 3 publication, parses it through the production neutral `BookDocument` path, writes one current phase9-native Highlight and one Note, and runs the real exporter. The current golden proves the minimal W3C/DC shape, exact EPUB NIH identity, exact href/quote/prefix/suffix, resource-wide Unicode-code-point TextPosition round trips, single-root package, and internal report/pointer binding. It is bounded fixture evidence, not a claim that a prior real full-book Agent artifact has been converted or that an external Reader/public service is interoperating with it. Rebuild or byte-check it offline from the backend directory:

```bash
.venv/bin/python tests/annotation_pack/fixtures/tiny-reader/build_fixture.py --write
.venv/bin/python tests/annotation_pack/fixtures/tiny-reader/build_fixture.py --check
```

The EPUB bytes are ZIP_STORED and reproducible across the supported Python ZIP implementation. Exact detached-package bytes are golden evidence for the supported compressor toolchain recorded by the fixture; validators remain interoperable across zlib versions because they verify the safe envelope and decompressed canonical JSON instead of re-compressing it.

All three tools reserve exit code `0` for a successful operation (`published`, `degraded`, or verified `unchanged` for export; valid for validate/inspect), `1` for an operational or validation failure, and `2` for a fixed-shape CLI usage error. Each invocation emits machine-readable JSON only: one line per validated source, and exactly one line for export or inspect.

## Detached Local Stack
Use this when you want the project to keep running after you close the current shell or restart Codex.

Commands:
- `make start-local-stack`
- `make status-local-stack`
- `make stop-local-stack`

Behavior:
- backend runs in stable mode, not hot-reload mode
- frontend runs as the Vite dev server
- both services write logs and pid files under `reading-companion-backend/state/local_stack/`
- this mode is detached from the current shell, but it is not a full supervisor
- if one service crashes, it stays down until you restart it

## Optional Local Runtime Observability

Phoenix is an optional local sidecar for inspecting OpenTelemetry/OpenInference-compatible runtime traces. It is deliberately separate from the backend/frontend stack.

Install and operate it explicitly:

```bash
make setup-phoenix
make start-phoenix
make status-phoenix
make stop-phoenix
```

Behavior and boundaries:

- `make setup-phoenix` installs `arize-phoenix==20.2.1` into `reading-companion-backend/state/phoenix/venv/`; the sidecar uses Python `>=3.12,<3.15` (or `PHOENIX_SETUP_PYTHON`) and does not modify the backend runtime virtualenv
- Phoenix data, logs, and PID state stay under the ignored `reading-companion-backend/state/phoenix/` directory
- the launcher binds only to loopback, keeps SQLite data across stops, disables Phoenix product telemetry, external resources, MCP, agent-assistant web/bash, sandbox-provider, and provider-playground surfaces, and does not forward backend provider credentials
- `make dev`, `make run-demo`, and `make start-local-stack` neither install nor start Phoenix
- normal `make setup` does not install the backend observability clients; install them explicitly with `cd reading-companion-backend && .venv/bin/python -m pip install -e ".[observability]"`
- backend export remains off unless `READING_OBSERVABILITY_OTLP_ENABLED=1`; the sidecar may run while the application emits no traces
- the default exporter target is the full OTLP/HTTP endpoint `http://127.0.0.1:6006/v1/traces`
- the privacy-first exporter omits book/prompt/output content and embedding vectors while preserving allowlisted model identity, timing, usage, error type, and domain IDs
- the append-only local fact ledger and generated JSON/Markdown reports remain runtime-observability truth; Phoenix is a derived operator view, and collector failure must not change ledger/report writes, reading status, or resume behavior

Optional local port override:

```bash
PHOENIX_PORT=6007 PHOENIX_GRPC_PORT=4318 make start-phoenix
```

If the HTTP port changes, update `READING_OBSERVABILITY_OTLP_ENDPOINT` to the matching `/v1/traces` URL before starting a telemetry-enabled backend process. The full span hierarchy, aggregation, privacy, retry, and cost rules live in `docs/implementation/runtime-observability/README.md`.

## Dataset Source Intake
Use the managed library inbox for future private/public source additions.

`reading-companion-backend/state/` is repo-local mutable operational data. The inbox is meant to stay simple for operators; the system does the classification and canonical copying.

Drop books into:
- `reading-companion-backend/state/library_inbox/`

Nested batch directories are allowed under that root for your own organization.

Optional sidecar metadata:
- place `<book>.source.json` next to the source file
- useful fields:
  - `source_id`
  - `title`
  - `author`
  - `canonical_filename`
  - `language`
  - `visibility`
  - `type_tags`
  - `role_tags`
  - `selection_priority`
  - `notes`
- normal use does not require a sidecar
- `language` is optional and is auto-detected when omitted
- `visibility` is optional compatibility metadata only
- new canonical managed copies no longer route into separate public/private folders
- if you omit `source_id`, the default generated id now follows `<canonical_stem>_<language>`
- most normal product work should ignore `visibility` entirely

Run intake:
- dry-run:
  - `make library-source-intake LIBRARY_SOURCE_INTAKE_ARGS="--dry-run"`
- ingest everything currently in the inbox:
  - `make library-source-intake`
- recover a missing source catalog from existing managed library files when this checkout already has `state/library_sources/` but no catalog:
  - `make library-source-intake LIBRARY_SOURCE_INTAKE_ARGS="--bootstrap-library-sources --run-id bootstrap_existing_sources_20260330"`
- ingest only English sources after automatic language resolution:
  - `make library-source-intake LIBRARY_SOURCE_INTAKE_ARGS="--language en"`
- optional compatibility filter if you need to inspect only explicitly public or private records:
  - `make library-source-intake LIBRARY_SOURCE_INTAKE_ARGS="--visibility public"`

Intake outputs:
- canonical copied books under `reading-companion-backend/state/library_sources/`
- current managed copies are language-rooted, for example:
  - `reading-companion-backend/state/library_sources/en/walden.epub`
  - `reading-companion-backend/state/library_sources/zh/朝花夕拾.epub`
- source catalog:
  - `reading-companion-backend/state/dataset_build/source_catalog.json`
  - `reading-companion-backend/state/dataset_build/source_catalog.md`
- per-run summaries:
  - `reading-companion-backend/state/dataset_build/source_intake_runs/`
- compatibility recovery note:
  - bootstrap mode seeds `source_catalog.json` from existing `state/library_sources/` files plus tracked manifest metadata without copying files again
  - older compatibility paths such as `state/library_sources/en/private/...` can still be backfilled into the catalog even though new operator-driven intake should use the simpler one-inbox workflow

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

## Closed-Loop Benchmark Curation
Use the first closed-loop benchmark-curation runner when you want one scratch-safe build-review-import pass over the managed local supplement.

Current scope:
- construct the question-aligned scratch datasets from managed local sources
- export initial `--only-unreviewed` review packets
- run case-design audit
- run LLM adjudication
- import and archive the packets
- optionally run one bounded revision/replacement repair wave
- refresh the queue summary
- emit a final stop-and-summarize report

Current boundaries:
- default mode is scratch-safe and writes run-scoped manifests/artifacts under `reading-companion-backend/state/dataset_build/build_runs/<run_id>/`
- scratch datasets still live under `reading-companion-backend/state/eval_local_datasets/`, but they use unique run-scoped dataset ids
- if the managed source catalog is missing but `state/library_sources/` already exists, the builder path now recovers by bootstrapping the catalog once before continuing
- `--from-stage` / `--through-stage` now support bounded partial runs cleanly, so the controller can stop after construction or export for smoke/recovery work without forcing `final_summary`
- the runner stops after summarizing and does not reopen promotion, freeze reviewed slices, or launch runtime/deployment decisions automatically

Examples:
- dry-run one scratch pass:
  - `make closed-loop-benchmark-curation CLOSED_LOOP_BENCHMARK_CURATION_ARGS="--run-id demo_curate --dry-run"`
- run only the scratch dataset-construction stage through the controller:
  - `make closed-loop-benchmark-curation CLOSED_LOOP_BENCHMARK_CURATION_ARGS="--run-id demo_construct --language en --limit-sources 1 --through-stage construct_dataset"`
- run a bounded English-only scratch pass over two managed sources:
  - `make closed-loop-benchmark-curation CLOSED_LOOP_BENCHMARK_CURATION_ARGS="--run-id demo_curate --language en --limit-sources 2"`
- run the same one-source English scratch smoke plus one repair wave that has already been validated on the recovered catalog:
  - `make closed-loop-benchmark-curation CLOSED_LOOP_BENCHMARK_CURATION_ARGS="--run-id demo_curate --language en --limit-sources 1 --repair-open-backlog"`
- include one bounded repair wave after the initial import:
  - `make closed-loop-benchmark-curation CLOSED_LOOP_BENCHMARK_CURATION_ARGS="--run-id demo_curate --repair-open-backlog"`

Long-running wrapper example:
- `cd reading-companion-backend && .venv/bin/python scripts/run_registered_job.py --task-ref "execution-tracker#dataset-platform" --lane dataset_platform --purpose "Closed-loop benchmark curation scratch pass" --cwd "$PWD" -- .venv/bin/python -m eval.attentional_v2.run_closed_loop_benchmark_curation --run-id demo_curate --repair-open-backlog`

## Whole-Book Single-Call Digest Experiment
The isolated《悉达多》experiment reuses the September 3 completed BookDocument/source scope and Digest v24. It does not parse EPUB again or invoke Ingest/retrieval. Run these commands from `reading-companion-backend/`:

- Prepare and verify the complete input without a model request: `.venv/bin/python -m eval.attentional_v2.run_whole_book_digest --prepare`
- Execute the explicitly authorized single request after registering the job as described below: `.venv/bin/python -m eval.attentional_v2.run_whole_book_digest --run`
- Rebuild manual-review Markdown from saved artifacts without a model request: `.venv/bin/python -m eval.attentional_v2.run_whole_book_digest --render`

The fixed run ID is `xidaduo_fullbook_single_digest_20260913`, job ID is `bgjob_xidaduo_fullbook_single_digest_20260913`, and local artifacts belong under `state/experiments/xidaduo_fullbook_single_digest_20260913/`. The run stops after one application-side request, including failure; it does not auto-repair, retry, continue, or change models. Do not relaunch the model call to regenerate review files. See `docs/backend-reader-evaluation.md#whole-book-single-call-diagnostic` for evidence limits, and check/update `reading-companion-backend/docs/evaluation/run_ledger.*` when the run changes state.

## Context and Task Scope Digest Experiment
The authorized follow-up `xidaduo_context_scope_digest_20260913` runs three independent requests serially: A repeats the frozen whole-book request, B reads only 迦摩罗 with the rest of the original book as background, and C reads the identical chapter with empty background. It stops the batch on any failed request. From `reading-companion-backend/`:

- Prepare once, without model calls: `.venv/bin/python -m eval.attentional_v2.run_context_scope_digest --prepare`
- After registering `bgjob_xidaduo_context_scope_digest_20260913`, execute once: `.venv/bin/python -m eval.attentional_v2.run_context_scope_digest --run`
- Rebuild the review packet without model calls: `.venv/bin/python -m eval.attentional_v2.run_context_scope_digest --render`

Artifacts stay in ignored `state/experiments/xidaduo_context_scope_digest_20260913/`. Begin manual review with `review.md`; `review-key.json` and `execution-summary.md` reveal conditions. Re-entry is refused even after failure; `--render` preserves anonymous identifiers. See `docs/backend-reader-evaluation.md#context-and-task-scope-diagnostic` for controls and evidence limits.

The subsequently authorized C-only recovery uses `.venv/bin/python -m eval.attentional_v2.retry_context_scope_digest --prepare`, then `--run` under registered job `bgjob_xidaduo_context_scope_c_retry_20260913`. It allows at most three additional identical C requests, stops at the first structurally complete response or a non-transport failure, and preserves the original run. Artifacts are in ignored `state/experiments/xidaduo_context_scope_c_retry_20260913/`; `retry-summary.md` records attempts and `comparison/review.md` contains a new anonymous packet if C succeeds. Do not relaunch the batch or select an output by annotation count.

## Q1 manual error analysis

Annotator 3.0 supports window-aligned mixed blind comparisons and stepwise rubric
rejudgment. For q1-v0, follow [the rejudgment protocol](reading-companion-backend/experiments/rubric-review.md):
open the prepared review folder using “打开批次文件夹”. Keep `q1-rubric-form.js` next to
the HTML. A second row of squares shows each criterion as unjudged / pass / fail;
only the selected criterion and its optional reason are shown. Every criterion must
be judged before confirming the case in “汇总”. Labels, star, uncovered, case remarks
and prior judgment live in that summary. This pass has no omission controls.

Outside text fields, **P/F** marks the current criterion pass/fail and stays;
**R** focuses its optional reason. **Enter** advances only after a judgment, then
confirms/stays in the summary. **Shift+Enter** in the summary confirms and moves to
the next case only after browser and file save receipts succeed; window-end stays.
**[ / ]** browses steps; **1–4** selects Note criteria (**1–3** for Highlights);
**Shift+number** toggles help. **V** applies only to the current criterion's verification
flag. In the summary, **5/6/7** toggles Note labels, **0** uncovered, **S** star and
**B** saved prior judgment. **M** opens summary remarks; **U**, arrows, **J/K**, **?**
and **Esc** keep their existing meanings. Text-field Enter inserts a newline; Esc
retains the draft. Native button/link/disclosure Enter and Tab/Space remain available.

New confirmations append `q1-mixed-judgment/3` with independent criterion reasons.
Old completed rows remain “旧版整条确认”; explicitly restart to make a new stepwise
assessment. Old drafts retain checked failures; unchecked criteria remain unjudged.
Historical overall reasons are retained separately. No journal or cache identity is
rewritten. Annotator 3.0 is now integrated into `main`: open
`reading-companion-backend/tools/q1-annotator.html` from the main workspace and refresh
any already-open page. Opening a batch folder does not update the HTML code. The original
2.6 compatibility edits are backed up in a local stash; compatible behavior and tests
are retained in 3.0.

The legacy open_coding instructions below retain their original behavior.

For ordinary mixed batch preparation, use
`build_q1_comparison.py` and open its output folder; the annotator reads only `mixed.json`.
Data preparation, the fixed-history Digest output contract, synthetic acceptance and
statistics instructions are in [comparison workflow](reading-companion-backend/experiments/comparison.md).
Side-by-side and reveal are deferred. Original single-group batches/journals remain supported.

From `reading-companion-backend/`, sample **one finished book output** with its evaluation-ledger run ID:

```sh
.venv/bin/python scripts/sample_q1_annotations.py "$BOOK_OUTPUT" --run-id "$RUN_ID" --preset bovary --seed 20261103
```

Use `sapiens` for the one-batch preset. For an already finished single-chapter pilot, add `--pilot-product "$PARTIAL_JSON" --pilot-original "$ORIGINAL_BOOK_OUTPUT" --pilot-all`. Each immutable `batch.json` is printed with its counts and stored under ignored `state/q1_annotation/<batch-id>/`. A repeat with identical inputs reuses the same batch. Never point pilot options at a running job.

### 在本机标注

宽屏（≥1440px）使用左侧单元判断、中间原文、右侧批注判断三栏；960–1439px 使用两栏，更窄时上下排列。原文在可用窗口高度内独立滚动，顶部工具栏常驻；长侧栏由整页滚动承接，引文和文本框随内容展开。窄窗口使用整页滚动。


1. 用 Chrome / Edge 打开 [q1-annotator.html](reading-companion-backend/tools/q1-annotator.html)，点「打开批次文件夹」，选择含 `batch.json` 的目录并允许读写，即可读取批次并连接同目录的 `judgments.jsonl`；文件缺失时在批次校验通过后创建。取消、拒绝授权或校验失败时保留当前批次。兼容入口在「更多 → 单独打开 JSON」，此方式需另行连接结果文件；「另选结果文件」可手动选择已有 JSONL。
2. 按 **↑ / ↓** 切换批注，**← / →** 切换单元。**P** 判过并停留，**F** 判不过并进入理由框。**S / V** 切换星标／待核实，**1 / 2 / 3** 选择密度多／合适／少。首尾停留，批注导航不会跨单元。**J / K** 向下／向上滚动原文，**Shift+J / Shift+K** 滚动整页处理长侧栏，可长按；窄屏下均滚动整页。新批次显示书名、作者、章节及按原书可读字符计算的单元中点百分比；旧批次缺失的信息显示为未知。
3. 按 **R / M / U** 进入理由／条目备注／单元备注。输入后立即保存浏览器草稿，停笔 500 毫秒后将有效修改追加到文件；退出文本框或导航时立即处理待保存内容。字段旁的“草稿仅存浏览器／修改已存浏览器”表示浏览器保存；文件写入状态以顶部提示为准。文本框内 **Enter 换行**，**Esc 返回阅读**，方向键移动光标。空的不过理由和漏标理由显示“待补理由”，草稿会保留，原有确认记录也会保留。
4. 在本单元正文划选后，点击选区旁的「记为漏标 O」或按 **O** 建立漏标草稿并进入理由框；已有漏标草稿时 O 回到该框。最多两处，已有草稿或达到上限时在选区旁提示。漏标原文显示淡紫色高亮，待补理由用虚线下划线，有效理由用实线；与产物黄色高亮重叠时保留黄色并加紫色下划线。输入理由后自动保存，Esc 结束有效的漏标编辑；未补理由时仍保留草稿。已保存漏标可以编辑或撤回。
5. 按 **?** 或点提示按钮查看全部快捷键，Esc 关闭。中文输入法候选确认和 Cmd／Ctrl／Option 组合键保留正常行为；文本框内不触发单键导航或判断。
6. 在同一浏览器配置中重开同一 HTML，自动恢复上次批次、位置、草稿及按批次记住的目录／文件句柄；权限有效时自动核对并同步，需要授权时点「恢复文件连接」，无需重新选路径。文件与浏览器历史相同则继续，一方是另一方的完整历史前缀时恢复较新文件或补写浏览器记录；发生分叉、批次不匹配或 JSONL 损坏时停止同步并保留双方内容，先导出浏览器历史核对，不会覆盖文件。有效的待保存草稿会自动处理，空失败理由／空漏标理由仍只存浏览器，不生成草稿文件。

顶部“浏览器与文件均已保存”表示当前有效修订已收到两端保存回执；未完成草稿在字段旁显示“待补理由 · 草稿仅存浏览器”。写入期间显示“浏览器已保存 · 文件同步中”，授权失效或写入失败显示“浏览器已保存 · 文件待同步”并提供恢复／重试。浏览器保存失败单独提示并可重试，请保持页面打开直至恢复；导出只含有效修订，不能替代未完成草稿。写入串行执行并在取得写锁后复核文件；重复同步不追加重复修订。存储回归检查：`node --test reading-companion-backend/tools/q1-annotator-storage.test.cjs`。

顶部按“书籍与文件操作、导航与完成计数、全宽单元方格”紧凑排列；桌面书名过长时省略，悬停可查看全名，手机宽度完整换行。完整操作提示见「? 快捷键」。顶部完成图每格对应一个单元，按批次顺序排列；空心表示未开始、部分填充表示进行中、实心带勾表示已完成，描边表示当前单元。点击方格，或用 Tab 聚焦后按 Enter，可跳到该单元第一条批注；点击当前格保留当前位置。方格提示包含单元序号、条目完成数和未完成原因。顶部同时显示单元与条目完成计数，左右判断区分别显示当前单元状态和条目在本单元／批次内的序号。

条目判过，或判不过且理由非空，即计为完成；按当前草稿优先、最新确认记录其次计算。星标、待核实和选填备注不影响完成度。单元完成还需选择密度，且没有理由为空的漏标草稿；零批注单元同样需要选密度。仅浏览不计开始，已有判断、标记、非空备注或漏标操作则计为进行中。完成状态表示标注要求已满足，并不表示已经写入本地文件，落盘仍以顶部文件状态为准。完成图由已有记录及草稿推导，不增加 JSONL 字段或修订。

JSONL 每行是一条带时间的修订，`record_type` 区分 `marginalia`、`density`、`unit_note`、`omission`。按 `(batch_id, record_type, record_id)` 取最后一个 `revision` 可还原当前判断。单独切换标记可能产生 `judgment: null`；单元备注在 `unit_note` 的 `remarks` 中原样保存，清空后追加空字符串；漏标的 `action: remove` 表示撤回。导出包括历次确认的修订。试跑同时保存产品与原书坐标，均使用段内 Unicode 码点和左闭右开区间。

## Long-Running Eval Jobs
Use the backend background-job registry for evaluation, packet review, or dataset jobs that may run for `10-15` minutes or longer.

- Register or update one job:
  - `cd reading-companion-backend && .venv/bin/python scripts/register_background_job.py --task-ref "execution-tracker#example" --lane mechanism_eval --purpose "English chapter-core rerun" --command ".venv/bin/python eval/attentional_v2/run_chapter_comparison.py --help" --cwd "$PWD"`
- Launch one generic job through the registry wrapper:
  - `cd reading-companion-backend && .venv/bin/python scripts/run_registered_job.py --task-ref "execution-tracker#example" --lane mechanism_eval --purpose "English chapter-core rerun" --cwd "$PWD" -- .venv/bin/python eval/attentional_v2/run_chapter_comparison.py --help`
- Launch one generic job through the detached wrapper when the shell/session itself may go away:
  - `cd reading-companion-backend && .venv/bin/python scripts/launch_registered_job_detached.py -- --root "$PWD" --task-ref "execution-tracker#example" --lane mechanism_eval --purpose "English chapter-core rerun" --cwd "$PWD" -- .venv/bin/python eval/attentional_v2/run_chapter_comparison.py --help`
  - this starts `run_registered_job.py` in a new session so the registered job can survive non-interactive tooling shells more reliably
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
- `make annotation-pack-contract-check` is the focused, offline-after-install guard for the root Annotation Pack v0 contract and its derived Python/Pages artifacts.
- `make contract-check` is the first guard for public contract drift.
- `make agent-check` is the canonical switching-memory guard for current state, task routing, and handoff hygiene.
- `make e2e` is the canonical upload -> analysis -> book -> chapter -> marks regression.

## Next Docs
- Start with `AGENTS.md` for workspace rules and document routing.
- Read `docs/current-state.md` for canonical live project status.
- Read the relevant child `AGENTS.md` before making subproject-local changes.
- Read `docs/tasks/registry.md` for the active task router and evidence chain.
- Read `docs/source-of-truth-map.md` when deciding where durable information belongs.

章节调度由 `attentional_v2/chapter_planner.py` 的 `build_chapter_plan` 负责；新产物为 `derived/chapter_plan.json`，不再生成 revisit/motif 索引。当前 runtime schema 为 3；旧格式显式拒绝，禁止转换旧 checkpoint。

### Explicit retrieval conditions (Step 1 prerequisites)

Internal `mechanism_config.memory_retrieval_mode` and CLI `--memory-retrieval-mode` accept `off`, `text-only` (canonical `text_only`), and `hybrid`. Product default remains hybrid. Off disables retrieval, not the recent Understanding window. Evaluation must explicitly select a mode; existing runners without a mode flag use `READING_MEMORY_RETRIEVAL_MODE=text_only` (or off/hybrid). `persist_normalized_eval_bundle=True` automatically requires strict evaluation behavior; internal diagnostics may also set `evaluation_run=True`. Hybrid evaluations fail on readiness or mid-run degradation. Product degradation emits a warning.

`runtime/memory_retrieval_config.json` records requested mode, embedding model, actual modes, query count and query/index degradation counts. `unit_memory_retrieval_trace.jsonl` records per-query evidence. `not_requested` means no actual query has run; it is not proof of working hybrid retrieval. The public HTTP API keeps its existing hybrid/text_only contract; off is internal/CLI only in this task.

Run configuration lookup: `_mechanisms/attentional_v2/runtime/run_configuration.json` joins code commit/dirty state, per-node model/sampling/prompt receipts, plan fingerprint and retrieval actual-mode/degradation counters. Normalized evaluation outputs include the same `run_configuration` snapshot. Historical invocation receipts remain in the existing mechanism diagnostics event stream.

Q1 prompt releases load exact version files and require private few-shot assets before API startup or reader tests. Provisioning, offline recovery and immutable-version checks: [iteration provenance](reading-companion-backend/experiments/README.md).

Q1 iteration checks (offline): `cd reading-companion-backend && .venv/bin/python scripts/check_prompt_releases.py && .venv/bin/python scripts/check_iteration_provenance.py`. The historical experiment baseline remains in `experiments/log.jsonl`; computed results are append-only in `experiments/scorings.jsonl`. Do not manually fill or edit old log rows. Use this branch's annotator 3.0 for new `weijiang` / rubric-attributed append-only judgments. Existing first-batch journals remain in the Q1 annotation worktree and are bound by prefix hashes. Runtime standard traces now include complete logical request hashes; each invocation retains private samples and a base-commit-bound dirty patch under `_runtime/provenance/`.

Q1 评分总表：[experiments/INDEX.md](reading-companion-backend/experiments/INDEX.md)。
主表只列每次评分的最新快照；历史快照、模型/单元/尺子、标注哈希和可比性见折叠小节。
运行 `cd reading-companion-backend && .venv/bin/python scripts/q1_scoring.py --evidence`
可复算本机冻结证据；`scripts/q1_experiment_index.py --check` 验证总表。
本机备份与恢复命令见 [Q1 管理文档](reading-companion-backend/experiments/README.md#中文总表与本机备份)。
