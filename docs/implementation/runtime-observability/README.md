# Runtime Observability And Cost v1

Purpose: define the implemented product-runtime tracing, token usage, estimated usage value, efficiency reporting, and duplicate-worker fencing boundary.
Use when: changing runtime observation scopes, provider-usage normalization, pricing, reports, the local Phoenix sidecar, or worker lease behavior.
Not for: prompt or reading-mechanism design, public API semantics, evaluation runners/datasets/Judges, or provider invoice reconciliation.
Update when: an event or metric definition, provider mapping, price source, exporter, sidecar version, or lease rule changes.

## Outcome And Scope

Runtime observability v1 is implemented for ordinary product runs of `attentional_v2` and `iterator_v1`. A completed run can be reconstructed from a local append-only event ledger and answers:

- how many normalized source characters were accepted;
- elapsed, active, provider-call, unit, and logical-call time;
- how many logical calls and actual provider attempts occurred, including retries and failover;
- provider-reported input, output, total, cache-read, cache-write, and reasoning token facts when available;
- the known reference-rate usage value, its exact price snapshot, and how much remains unknown;
- where calls belong by run attempt, chapter, reading cycle, selected unit, stage, node, model, and target.

This lane is deliberately observation-only. It does not change prompts, selection, retrieval, memory, checkpoint data, settlement rules, output contracts, evaluation inputs, or evaluation metrics. It adds no public API or frontend cost display. Cost is a catalog-based estimate, not a provider invoice.

## Sources Of Truth

For product job `<job_id>` and book output `<output_dir>`:

```text
<output_dir>/_history/runs/<job_id>/observability/
├── events.jsonl       # append-only facts; canonical observation record
├── metrics.json       # deterministic machine-readable aggregate
├── report.md          # operator-readable book/chapter/unit breakdown
└── data_quality.json  # coverage and loss indicators
```

`events.jsonl` is authoritative for runtime observability. Reports are rebuildable. Phoenix is a derived local trace view. Job status remains authoritative in `reading-companion-backend/state/job_registry/`; checkpoints and reading state remain authoritative under book output; mechanism-private audits remain under `_mechanisms/<mechanism_key>/`.

Ledger writes use a process/thread lock, an OS file lock where available, one JSON object per append, and deterministic event IDs. Aggregation de-duplicates repeated IDs. A transient write failure is persisted as `ledger_write_failed` after the filesystem recovers. A total outage of the same filesystem cannot be represented durably there, so report generation also includes process-local failure diagnostics when still available.
If the ledger cannot be read, `report.md` stops at a prominent `Data unavailable` warning instead of rendering empty aggregates as observed zeros; `data_quality.json` records the read error type.

## Correlation Model

The immutable `ObservationContext` is propagated through `ContextVar` and contains:

- `job_id`, `job_kind`, `run_id`, `run_attempt_id`, and `lease_generation`;
- `book_id` and `mechanism_key`;
- `chapter_id` and `chapter_index`;
- `reading_cycle_id`;
- `unit_id`, `unit_index`, and normalized `source_char_count` after selection;
- `stage` and `node`;
- local OpenTelemetry trace/span identifiers when export is active.

The logical hierarchy is:

```text
job
└── run_attempt
    └── chapter
        ├── chapter-only parse/segmentation call
        └── reading_cycle
            ├── Ingest call before unit selection
            ├── unit_selected -> stable unit_id
            └── unit
                ├── Digest and other unit-scoped logical calls
                └── one or more provider attempts
```

Ingest must run before the reader knows the selected unit. The runtime therefore creates `reading_cycle_id` first, then emits `unit_selected`. Aggregation joins earlier Ingest facts to that unit by the stable `(job_id, run_attempt_id, chapter_id, reading_cycle_id)` key; it never infers ownership from timestamps. A failed pre-selection Ingest remains chapter/cycle-correlated without inventing a unit. Iterator semantic segmentation is intentionally chapter-scoped rather than unit-scoped, so data quality uses stage-appropriate correlation coverage and reports non-unit-eligible attempts separately.
On Iterator cancellation or foreground failure, the scheduler stops admitting new segmentation work and drains any provider calls that already started while the managed heartbeat remains active. The root scope therefore closes and writes final reports only after inherited background observation facts have settled.

The implemented event kinds are:

- `run_attempt_started`, `run_attempt_finished`;
- `chapter_started`, `chapter_finished`;
- `reading_cycle_started`, `unit_selected`, `unit_settled`;
- `llm_provider_attempt_started` immediately before each actual adapter request and `llm_provider_attempt_finished` when control returns;
- `llm_logical_call_finished` after retry/failover concludes;
- `ledger_write_failed` after a transient ledger error recovers;
- `observation_report_failed` when one or more derived artifacts cannot be written;
- `telemetry_export_failed` when optional export reports initialization or detected transport loss.

The start event is written immediately before `adapter.invoke`, so a process crash can leave explicit evidence of a possibly billable request whose finish/usage is unknown. A provider response is recorded before structured-output parsing. Consequently, a response that may be billable but later fails JSON/tool validation is not lost. Calls skipped before an adapter request, such as an exhausted local quota gate, are not counted as physical provider attempts.

## Token Usage Semantics

Usage is passively read from provider/LangChain response metadata; requests are unchanged. Each physical attempt stores a normalized usage object with:

- `input_tokens`, `output_tokens`, and `total_tokens`;
- `uncached_input_tokens`;
- `cache_read_input_tokens` and `cache_write_input_tokens`;
- `reasoning_tokens`;
- `billable_output_tokens`;
- `status=complete|partial|unavailable|invalid`;
- `source`, `provider_family`, and invalid-field names.

Normalization is provider-aware:

- OpenAI-compatible input commonly includes cached input, so uncached input is derived only when the cache categories needed for that subtraction are known.
- Raw Anthropic `input_tokens` represents uncached input; cache-read and cache-creation categories are added when deriving a total.
- Gemini candidate tokens exclude thoughts, so billable output is candidates plus reported thoughts; missing thought usage remains unknown.
- Generic LangChain metadata is not assigned provider-specific cache semantics unless the required categories are present.

Missing, malformed, or semantically incomplete usage is never converted to zero. Reasoning is retained as a subcategory and is not charged twice by default.
Internally contradictory metadata, such as cached input exceeding provider-defined total input, is marked `invalid` and is not priced.

## Pricing And Cost Semantics

Tracked price rules live in `reading-companion-backend/config/llm_pricing.json`. A complete ignored local replacement may be placed at `reading-companion-backend/config/llm_pricing.local.json`.

Matching priority is:

1. exact `target_id + model`;
2. fallback `provider contract + model` when a catalog rule explicitly uses it.

Each attempt freezes the matched rule into the ledger, including catalog version, entry ID, billing model, currency, effective interval, source URL/date, per-million rates, applicable usage categories, and a deterministic SHA-256 snapshot hash. Later catalog changes therefore do not rewrite historical estimates.

Values use Python `Decimal` and are serialized as decimal strings. Cost status remains non-complete when any priced category required by the rule is missing, when a used category has no known rate, or when no catalog rule matches. Reports expose the known sum and coverage; they do not label a partial sum as whole-book total.
Because the v1 estimate field is explicitly USD-denominated, the catalog rejects non-USD rules rather than silently placing another currency into `estimated_usage_value_usd`.

The tracked OpenCode Go rules are subscription based. They use the official published reference token rates to compute `estimated_usage_value_usd`, while preserving:

```text
billing_model = subscription
actual_billed_cost = null
```

This is a comparable usage value, not allocation of a monthly subscription and not actual cash spend.

## Implemented Metrics

Whole-run `metrics.json` includes:

- `accepted_source_chars`, de-duplicated from successfully settled units;
- `elapsed_seconds`, from earliest run start to latest run finish;
- `active_seconds`, the union of completed run-attempt intervals;
- `provider_seconds`, the sum of physical provider-attempt durations;
- characters per active minute and active minutes per 10,000 characters;
- input/output/total tokens and estimated usage value per 10,000 characters;
- logical calls, physical attempts, retries, retry amplification, and logical calls per accepted unit;
- expected, observed, matched, missing, and unexpected physical-attempt counts;
- provider-attempt start/finish coverage, including starts that have no durable finish row;
- p50/p95 logical-call and accepted-unit latency;
- quota/provider/profile gate waits and their combined share when recorded;
- retry-waste attempt usage/value;
- breakdowns by chapter, unit, stage, node, model, and target;
- the exact pricing snapshots present in the ledger.

`data_quality.json` includes:

- usage and pricing coverage;
- physical-attempt accounting coverage;
- chapter, selected-unit-scoped, and stage-appropriate correlation coverage;
- unknown usage and unknown estimated-value attempt counts;
- missing/unexpected physical attempts;
- malformed/duplicate ledger rows;
- ledger read/write and derived-report failures;
- detected Phoenix exporter failure batches and the number of spans in those failed exports.

Coverage denominators use the greatest durable evidence implied by logical-call records, provider-attempt start rows, and finish rows. Thus, if a logical call says it made two provider attempts but only one finish row exists—or a start survives without a finish—usage/pricing coverage cannot falsely remain `1.0`.

No efficiency target is set in v1. The first real baseline is for validating calculability, provenance, and useful slicing; targets should be proposed only after representative runs exist.

## Duplicate-Worker Lease

Managed product jobs use a lease sidecar under:

```text
reading-companion-backend/state/job_registry/leases/
```

For every launch or resume, the launcher creates a new `run_attempt_id`, monotonically increasing generation, and opaque token, then passes them to the worker through internal environment variables. The worker renews its lease every 10 seconds; the expiry window is 45 seconds.

Safety rules:

- fresh leases and same-book workers whose exit cannot be proved block another launch;
- the product upload path fails closed before worker launch if provisioning cannot resolve a canonical book/output identity; internal pre-provision launch paths derive that identity by inspection and use a source digest only as a last-resort lock key;
- corrupt, invalid, or unreadable existing leases fail closed rather than appearing absent;
- a transient filesystem read/write interruption is tolerated only within the current grant's bounded TTL because launchers also fail closed during that window; corruption or fencing mismatch still fails immediately;
- a matching owner/token/generation may renew after a sleep or long pause even if the wall-clock TTL passed;
- fenced, released, old-generation, wrong-owner, and wrong-PID-incarnation grants cannot renew;
- manual resume fences the exact recorded attempt, validates PID birth identity (Linux `/proc` start tick or Darwin `libproc` microsecond start time), rechecks that identity immediately before signaling, terminates it, waits for exit, and only then rotates generation; an unavailable recheck fails closed;
- legacy records that contain only a bare PID cannot authorize an automatic signal; if that process still appears live, recovery pauses rather than risking termination of a reused unrelated PID;
- if child launch succeeds but heartbeat or registry persistence fails, the exact child is terminated and reaped before the lease is released;
- the gateway checks fencing immediately before an adapter request, and mechanisms check again before unit settlement;
- direct CLI reads generate isolated observation identities but do not create managed lease sidecars.

The lease changes only worker ownership. It does not change the order or result of a healthy single-worker reading run.

V1 does not claim a kernel-held process handle on every platform. Linux can eventually replace this final check/use boundary with `pidfd`; Darwin's POSIX signal call still accepts a PID after the immediate second identity probe, so a theoretical reuse window remains between that probe and the syscall. Legacy or unverifiable owners are never signaled automatically.

## Phoenix Local Observation View

Phoenix is optional, local-only, and disabled by default:

```dotenv
READING_OBSERVABILITY_OTLP_ENABLED=0
READING_OBSERVABILITY_OTLP_ENDPOINT=http://127.0.0.1:6006/v1/traces
READING_OBSERVABILITY_PROJECT=reading-companion-runtime
```

Pinned components:

| Surface | Package | Version |
| --- | --- | --- |
| Sidecar server | `arize-phoenix` | `20.2.1` |
| Backend helper | `arize-phoenix-otel` | `0.17.1` |
| OpenInference configuration | `openinference-instrumentation` | `0.1.57` |
| OTel API/SDK/OTLP HTTP | OpenTelemetry packages | `1.44.0` |

The backend client dependencies are optional under `.[observability]`. Phoenix runs in `reading-companion-backend/state/phoenix/venv` with Python `>=3.12,<3.15`; this leaves the backend's Python 3.11 environment unchanged. `make setup-phoenix` auto-detects Python 3.12 through 3.14 or accepts `PHOENIX_SETUP_PYTHON`.

Operator commands:

```bash
make setup-phoenix
make start-phoenix
make status-phoenix
make stop-phoenix
```

The unauthenticated UI and OTLP/HTTP collector bind only to loopback:

- UI: `http://127.0.0.1:6006`
- traces: `http://127.0.0.1:6006/v1/traces`

Unit-bearing work uses this manual span hierarchy:

```text
reading.run_attempt
└── reading.chapter
    └── reading.unit_attempt
        └── llm.call
            └── llm.attempt
```

Survey, parse/segmentation, and other chapter-only calls appear beneath `reading.chapter` without a fabricated unit span. No provider, LangChain, or FastAPI auto-instrumentation is enabled, so one adapter request has one project-owned cost-bearing `llm.attempt` span.

Exporter span and resource attributes use explicit scalar-key allowlists: stable service and domain IDs, stage/node/model/target, lengths, status, timing, token counts, and estimated value. Unknown attribute names are dropped, and generic `OTEL_RESOURCE_ATTRIBUTES` are not merged into the resource. Raw book text, prompts, completions, tool arguments, provider error bodies, API keys, authorization/cookies, and lease tokens are not emitted. The sidecar receives an allowlisted process environment rather than backend provider credentials; its agent assistant, web/bash agent access, sandbox providers, MCP server, external resources, and provider playground are disabled by the launcher.

The backend wraps the OTLP exporter and inspects each batch result, then ends the run span and flushes before taking a run-local counter delta. Each OTLP HTTP request has a five-second timeout; the pinned SDK's force-flush timeout is not treated as a stronger hard deadline. Initialization, span, flush, and detected HTTP export failures are isolated from provider retry/error classification and reading return values. Failed-export span counts do not claim exhaustive visibility into any loss internal to the OpenTelemetry batch queue. The ledger remains enabled when OTLP export is off or unavailable.

## Deferred Beyond v1

The current implementation intentionally does not claim:

- provider invoice ingestion or per-call allocation of subscription payments;
- streaming/TTFT measurement, p99 latency, tokens-per-second, sampling, or retention policy;
- HTTP-request-to-worker OpenTelemetry links or trace IDs written into job-registry records;
- response-model/finish-reason, source-text hash, prompt-template version, or checkpoint outcome attributes not already available at the shared hook;
- a custom dashboard, public observability API, or frontend cost UI;
- trace-to-evaluation-record correlation.

These require separate product or infrastructure decisions and must not be inferred from the v1 ledger.

## Verification Contract

Required automated checks cover:

- OpenAI-compatible, Anthropic, and Gemini complete/partial/missing/malformed usage;
- cache/reasoning semantics, subscription value, unknown price/category, effective dates, snapshots, and Decimal aggregation;
- one ledger row per real retry/failover attempt and billing capture before structured-output parsing;
- observation/Phoenix failure isolation;
- async/thread context propagation, Ingest-to-unit joining, and direct/evaluation scope separation;
- lease expiry, corrupt reads, concurrent refresh, dead/alive PID handling, PID reuse, stale-generation fencing, and post-launch cleanup;
- deterministic event de-duplication, physical-attempt reconciliation, data-quality coverage, and report rebuilding;
- a deterministic fake-adapter product read using `tests/fixtures/e2e_runtime/sample-upload.epub`;
- a loopback Phoenix smoke with the unit-scoped five-level hierarchy plus legitimate chapter-only calls, persistence across restart, privacy-field inspection, and collector-down behavior.

The deterministic product-path and loopback Phoenix proofs pass. The remaining live public-book acceptance against `state/library_sources/zh/beiying_public_v2.epub` is externally blocked: the configured DeepSeek target requires a regional workspace opt-in and the configured Mimo fallback reports insufficient credits. No region, billing, or account setting is changed automatically, and this blocker does not invalidate the deterministic runtime evidence.

Latest implementation validation on 2026-08-17: the observability/lease/gateway/mechanism/API/E2E focused suite passed `222` tests. The backend-wide suite completed `947` tests successfully and retained `9` unrelated repository-baseline failures: seven stale tests patch the removed `invoke_structured_output_tool` name, one evaluation-inventory assertion points at an older dataset, and one quality-audit assertion assumes two configured targets while the local configuration exposes one. This lane does not alter those mechanism/evaluation surfaces. `make agent-check` and `make contract-check` both exit successfully; `agent-check` continues to print the repository's pre-existing traceability warnings.

Run:

```bash
cd reading-companion-backend
.venv/bin/pytest -q
cd ..
make agent-check
make contract-check
```

Do not invoke an evaluation runner, Judge, dataset, or evaluation ledger while validating this infrastructure lane.

## References

- [OpenCode Go pricing](https://opencode.ai/docs/go/)
- [OpenAI usage fields](https://platform.openai.com/docs/api-reference/usage/audio_transcriptions_object)
- [Anthropic token and cache pricing semantics](https://docs.anthropic.com/en/docs/about-claude/pricing)
- [Gemini `usageMetadata`](https://ai.google.dev/api/generate-content)
- [Phoenix local deployment](https://arize.com/docs/phoenix/self-hosting/deployment-options)
- [Phoenix OpenTelemetry setup](https://www.arize.com/docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel)
- [OpenInference privacy configuration](https://arize-ai.github.io/openinference/spec/configuration.html)
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
