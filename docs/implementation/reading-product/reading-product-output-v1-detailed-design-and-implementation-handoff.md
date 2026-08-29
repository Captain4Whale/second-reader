# Reading Product Output v1 — Detailed Design, Implementation Handoff, and Definition of Done

Status: active implementation authority for `TASK-READING-PRODUCT-OUTPUT-V1` under `DEC-158`.

## 1. Outcome

Create one mechanism-neutral product fact layer between private reading internals and downstream products:

```text
private reading mechanism
  -> accepted Unit product transaction
  -> partial Reading Product projection
  -> whole-book finalizer
  -> immutable complete Reading Product
  -> Annotation Pack and existing chapter/API compatibility projection
```

The canonical wire and coordinate rules live in [`contract/reading-product/v1/README.md`](../../../contract/reading-product/v1/README.md) and its JSON Schema. This document owns sequencing, recovery behavior, acceptance evidence, and the completion boundary. It must not restate or fork the field authority.

## 2. Fixed decisions

- Product facts are the accepted Unit's source range, `understanding`, `response`, and exact-source Marginalia.
- Unit-selection reasons, Marginalia `selection_reason`, prompts, traces, memory, retries, provider facts, jobs, and provenance are audit/runtime data.
- Model output may remain mechanism-private. Settlement performs the explicit conversion.
- Product Store is the accepted-Unit commit truth. Other mechanism ledgers and compatibility views are derived.
- A bad or ambiguous Marginalia item is skipped with a private finding; it does not discard valid U/R or sibling marks.
- Fresh reading creates UUIDv4 `reading_id`; resume retains it. V1 has no replacement/supersession field.
- Per-Unit settlement happens during reading. A deterministic finalizer seals the already committed book-level snapshot after the approved plan completes.
- `complete` requires all scheduled `mainline + deferred` chapters; `auxiliary` is excluded.
- Annotation Pack and existing chapter projections migrate to Reading Product, but the public HTTP/frontend shape remains compatible in this initiative.
- No live-model call is authorized in the current implementation round. The expired OpenCode Go key must not be read, tested, restored, or referenced by a command.

## 3. Storage and transaction model

For a reading revision:

```text
_runtime/reading-products/<reading_uuid>/
├── ledger.sqlite3
└── reading-product.partial.json

public/reading-products/
├── current.json
└── revisions/<product_sha256>/
    ├── reading-product.json
    └── validation-report.json
```

SQLite owns Unit commit rows, source identity, reading identity, timestamps, and canonical unit bytes. One transaction enforces contiguous sequence, ID/index coherence, source consistency, ordered non-overlap, and byte-identical replay. The partial JSON is atomically rebuilt from SQLite and is not a second truth source.

The finalizer checks the runtime reading plan and committed ledger, constructs canonical complete bytes once, validates them against the exact EPUB/BookDocument snapshot, writes an immutable revision, fsyncs files/directories, and atomically switches `current.json`. A selected revision never changes. A failed validation never advances current.

## 4. Settlement and recovery ordering

Required order for one Unit:

1. Prepare/select one candidate source Unit without advancing the accepted cursor.
2. Run Digest and require non-empty U/R for content-bearing source.
3. Resolve Marginalia to exact canonical ranges; audit and omit only invalid items.
4. Build and atomically commit the Product Unit.
5. Rebuild private Unit Memory, reaction records, compatibility projections, and audit from the committed product plus private settlement context.
6. Persist checkpoint/cursor carrying `reading_id`, last Unit ID, and sequence.

Crash recovery treats the Product Store as authoritative. If product is ahead of the private checkpoint, resume replays committed Units and rebuilds derived state without calling the model. If private transient state is ahead of product, it rolls back to the last product commit. Audit is never promoted into missing product meaning.

## 5. Implementation slices

### Slice 1 — Authority, contract, and shared foundations

- Add canonical README, strict schema, examples, auxiliary schemas, offline check, and allowlisted Pages projection.
- Register `DEC-158`, the active implementation task, and the deferred live-acceptance task.
- Move canonical JSON, source-range validation, and `sr-book-document-substrate-v1` projection/digest into `reading_core`; Annotation Pack keeps compatibility re-exports and identical results.
- Add a mechanism-neutral `reading_product` domain with strict runtime schema copy.
- Update source-of-truth, product/current/task facts, routing docs, and operator commands.

Acceptance: contract/examples/negative cases and Pages projection pass offline; shared helper regression proves Annotation Pack bytes/digests unchanged; no provider access occurs.

### Slice 2 — Per-Unit product settlement

- Create/reuse the reading revision store and partial projection.
- Insert the Product transaction into normal `attentional_v2` settlement before cursor advance.
- Require non-empty U/R, validate exact ranges, skip bad Marginalia into private findings, and enforce replay/conflict rules.
- Make Unit Memory/reaction/audit/compat outputs downstream of product commit.

Acceptance: focused tests cover empty U/R, body rules, containment, quote mismatch, ambiguity skip, empty Marginalia, duplicate/conflicting replay, sequence gaps, and crash boundaries without provider calls.

### Slice 3 — Resume and complete finalization

- Extend checkpoint/recovery with reading revision identity and last product sequence.
- Rebuild private projections when product leads; roll back transient private state when product lags.
- Verify plan completeness and atomically publish immutable product/report/pointer files.
- Mark run completed only after finalization succeeds.

Acceptance: deterministic crash injection covers Digest success before product, product commit before derived files, pointer switch interruption, repeated finalization, concurrent finalization, source mutation, chapter-only/audit-cap/partial rejection, and plan-completeness rules.

### Slice 4 — Direct consumers

- Make complete Reading Product the default Annotation Pack producer input.
- Keep phase9 only as an explicitly selected legacy adapter; phase8 remains rejected.
- Derive existing chapter/API compatibility marks from committed product while keeping public response shapes stable.
- Prove Pack and chapter projections work after private reaction/audit/memory artifacts are removed.

Acceptance: Tiny Reader complete product generates the same minimal W3C/DC Pack semantics and an independently valid detached package; API/frontend contract snapshots remain unchanged.

### Slice 5 — Offline whole-book lifecycle and close-out

- Use the real Tiny Reader EPUB and normal parse/Runner/settlement/finalizer/Pack path.
- Inject deterministic Ingest/Digest test doubles only at the model boundary; do not bypass settlement, coordinates, storage, resume, finalizer, or export.
- Update final evidence, baseline separation, task status, and completion claims.

Acceptance: the offline full-book lifecycle covers Highlight, Note, empty Marginalia, invalid-item skip, crash/resume, repeated execution, and source mutation; all required offline checks pass.

## 6. Execution baseline

Pre-implementation baseline supplied and retained for comparison:

- `make annotation-pack-contract-check`: `55 passed`; Pages projection valid.
- affected regression set: `135 passed, 2 failed`; both failures are existing `slow_cycle.invoke_structured_output_tool` monkeypatch/interface drift.
- serial `make contract-check`: exit `0`.
- one concurrent `make agent-check` `npx` failure is classified as a concurrency transient; final acceptance must rerun the command serially before making a claim.

New failures outside these exact baseline cases are in-scope until explained or fixed. A passing aggregate must not erase a known baseline failure, and a baseline failure must not be presented as a Reading Product regression.

## 7. Offline test matrix

- Schema: required fields, strict whitelists, UUID/timestamp/hash shapes, partial/complete conditional, Highlight/Note body rules.
- Identity: one EPUB-byte or substrate-field change invalidates binding.
- Coordinates: Unicode code points, start-inclusive/end-exclusive, bounds/order, same chapter, Unit containment, single-resource Marginalia, exact cross-paragraph `\n\n` quote reconstruction.
- Isolation: reject prompt, memory, trace, provider, selection reason, job/private IDs, mechanism version, compatibility taxonomy, provenance, and supersession fields.
- Transaction: atomic commit, identical replay unchanged, conflicting replay rejected, no sequence gaps, non-overlapping Units, crash recovery, concurrency.
- Finalization: complete plan only, immutable bytes/revision, atomic pointer, failed validation isolation, repeated unchanged result.
- Consumers: Pack and chapter compatibility projection need only complete Reading Product plus verified source substrate.
- Commands: `make reading-product-contract-check`, `make annotation-pack-contract-check`, focused Reading Product/Agent/API suites, `make contract-check`, `make agent-check`, and the complete backend suite.

## 8. Definition of Done

Repo-local implementation is complete only when:

- [ ] canonical contract, examples, companion schemas, runtime copy, Pages projection, and offline checks agree;
- [ ] default reading settlement commits one strict Product Unit before cursor advance;
- [ ] resume/recovery honors Product Store commit truth without repeated model work;
- [ ] whole-book finalizer publishes only complete immutable revisions and switches current atomically;
- [ ] Annotation Pack and current chapter/API compatibility views consume Reading Product by default;
- [ ] deterministic real-EPUB offline whole-book lifecycle passes through normal runtime seams;
- [ ] privacy and private-artifact-deletion isolation tests pass;
- [ ] required checks are run serially at close-out and unrelated baseline problems are listed separately;
- [ ] each accepted Slice is committed and pushed on `codex/annotation-pack-v0` without force-push;
- [ ] current-state/task/docs and remote HEAD evidence are accurate.

The allowed completion statement is:

> The current default reading mechanism is wired to Reading Product Output v1; with a real EPUB and deterministic model substitutes, it can commit accepted Units, seal a whole-book product, build compatibility projections, and generate and independently validate Annotation Pack v0.

This round must not claim a live LLM whole-book read, validity of the expired OpenCode Go key, conversion of historical full-book outputs, public Pages availability, or native frontend display of Unit U/R.

## 9. Deferred live acceptance

`TASK-READING-PRODUCT-OUTPUT-V1-LIVE-ACCEPTANCE` is blocked solely on the owner supplying a usable model API credential in a future task. No implementation Slice may test the expired key. When unblocked, run one short real EPUB from the normal product entrypoint and verify `complete Reading Product -> Annotation Pack`; do not redesign or rebuild the offline implementation first.
