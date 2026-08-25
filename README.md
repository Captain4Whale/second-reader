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
- `OPENCODE_GO_API_KEY`
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
  - current local operation uses OpenCode Go targets with `OPENCODE_GO_API_KEY`
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
          "target_ids": ["opencode_deepseek_v4_flash"],
          "min_required_stable_concurrency": 1
        }
      ],
      "temperature": 0.2,
      "max_output_tokens": 4096,
      "timeout_seconds": 120,
      "retry_attempts": 3,
      "max_concurrency": 24,
      "default_burst_concurrency": 24,
      "quota_retry_attempts": 2,
      "quota_wait_budget_seconds": 25
    }
  ]
}
```

Optional pooled primary-tier shape for explicit OpenCode model fanout:
```json
{
  "profiles": [
    {
      "profile_id": "runtime_reader_default",
      "target_tiers": [
        {
          "tier_id": "primary",
          "target_ids": ["opencode_deepseek_v4_flash", "opencode_mimo_v25"],
          "min_required_stable_concurrency": 1
        }
      ],
      "max_concurrency": 2,
      "default_burst_concurrency": 2
    }
  ]
}
```
- in this pooled shape, the tier dispatches across target ids for explicit experiments; it does not create extra provider quota when those targets share the same OpenCode key
- if you want a true backup target instead of same-priority fanout, keep it in a later tier such as `backup`

Tracked templates for the new local setup:
- `reading-companion-backend/config/llm_targets.local.example.json`
- `reading-companion-backend/config/llm_profile_bindings.local.example.json`

OpenAI-compatible JSON-object targets:
```json
{
  "target_id": "opencode_deepseek_v4_flash",
  "contract": "openai_compatible",
  "base_url": "https://opencode.ai/zen/go/v1",
  "model": "deepseek-v4-flash",
  "credentials": [
    {
      "credential_id": "primary_env",
      "api_key_env": "OPENCODE_GO_API_KEY"
    }
  ],
  "provider_options": {
    "response_format": {"type": "json_object"},
    "thinking": {"type": "enabled"}
  },
  "timeout_seconds": 120,
  "retry_attempts": 3,
  "max_concurrency": 24,
  "initial_max_concurrency": 24,
  "probe_max_concurrency": 24,
  "min_stable_concurrency": 24,
  "concurrency_strategy": "fixed"
}
```
- project tools stay in the internal canonical shape `name`, `description`, `input_schema`
- the Anthropic adapter emits Anthropic-style tool definitions; the OpenAI-compatible adapter emits OpenAI function tools and maps forced tool choice at the adapter boundary
- when the selected OpenAI-compatible profile enables `response_format: {"type": "json_object"}`, current `attentional_v2` Ingest/Digest final structured outputs use JSON object mode plus local validator/repair
- thinking-enabled target/profile options default to a larger `max_output_tokens` budget when the profile does not set one explicitly; use `8192` for Ingest probes that need visible reasoning plus final JSON
- `retrieve_unit_memory` remains a normal `tool_choice="auto"` action tool; it is not forced merely to carry final structured output
- standard runtime artifacts and traces should not store raw reasoning/thinking content; keep only normal content, usage, and metadata unless a debug trace explicitly opts in
- the current OpenCode / DeepSeek JSON-object policy and historical MiniMax transport notes live in `docs/implementation/new-reading-mechanism/llm-structured-output-protocol-note.md`

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
  - optional `LLM_DATASET_REVIEW_MODEL`
  - optional `LLM_EVAL_JUDGE_MODEL`
  - optional `LLM_RUNTIME_MAX_OUTPUT_TOKENS`
  - optional `LLM_DATASET_REVIEW_MAX_OUTPUT_TOKENS`
  - optional `LLM_EVAL_JUDGE_MAX_OUTPUT_TOKENS`

Reference and compatibility files:
- shared provider/profile registry example:
  - `reading-companion-backend/config/llm_registry.example.json`
- the older MiniMax official-key local registry has been retired from the current checkout; use OpenCode Go targets for active local work

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

Package generation fixes the root name, timestamp, Unix regular-file mode, DEFLATE level, entry order, and comments/extra fields. Byte reproducibility is a Second Reader project rule within the supported toolchain, not a W3C requirement or a promise that different zlib versions emit the same DEFLATE bitstream. Independent validation checks the observable safe envelope and uncompressed canonical JSON rather than requiring local recompression byte equality. Minimal v0 has no project JSON-LD namespace or custom context. Its approved schema IRI uses the GitHub Pages location, but that IRI is not live until the workflow reaches `main`, Pages is enabled, deployment succeeds, and the served bytes pass HTTP comparison against the canonical contract file.

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
