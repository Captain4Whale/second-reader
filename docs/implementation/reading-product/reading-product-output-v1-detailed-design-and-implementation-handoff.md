# Reading Product Output v1 — Detailed Design, Implementation Handoff, and Definition of Done

Status: repo-local offline implementation complete for `TASK-READING-PRODUCT-OUTPUT-V1` under `DEC-158`; the bounded CPA Luna live-model acceptance is complete under `TASK-READING-PRODUCT-OUTPUT-V1-LIVE-ACCEPTANCE`.

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
- The completed offline implementation round did not authorize or perform a live-model call. Its evidence boundary remains offline even though the current local provider is now CPA Luna Medium.

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

Delivery: accepted and pushed as `d83707a` (`feat(reading-product): establish v1 contract`).

### Slice 2 — Per-Unit product settlement

- Create/reuse the reading revision store and partial projection.
- Insert the Product transaction into normal `attentional_v2` settlement before cursor advance.
- Require non-empty U/R, validate exact ranges, skip bad Marginalia into private findings, and enforce replay/conflict rules.
- Make Unit Memory/reaction/audit/compat outputs downstream of product commit.

Acceptance: focused tests cover empty U/R, body rules, containment, quote mismatch, ambiguity skip, empty Marginalia, duplicate/conflicting replay, sequence gaps, and crash boundaries without provider calls.

Delivery: accepted and pushed as `7dcd160` (`feat(reading-product): make unit settlement authoritative`).

### Slice 3 — Resume and complete finalization

- Extend checkpoint/recovery with reading revision identity and last product sequence.
- Rebuild private projections when product leads; roll back transient private state when product lags.
- Verify plan completeness and atomically publish immutable product/report/pointer files.
- Mark run completed only after finalization succeeds.

Acceptance: deterministic crash injection covers Digest success before product, product commit before derived files, pointer switch interruption, repeated finalization, concurrent finalization, source mutation, chapter-only/audit-cap/partial rejection, and plan-completeness rules.

Delivery: accepted and pushed as `e7adccc` (`test(reading-product): verify recovery and finalization`).

### Slice 4 — Direct consumers

- Make complete Reading Product the default Annotation Pack producer input.
- Keep phase9 only as an explicitly selected legacy adapter; phase8 remains rejected.
- Derive existing chapter/API compatibility marks from committed product while keeping public response shapes stable.
- Prove Pack and chapter projections work after private reaction/audit/memory artifacts are removed.

Acceptance: Tiny Reader complete product generates the same minimal W3C/DC Pack semantics and an independently valid detached package; API/frontend contract snapshots remain unchanged.

Delivery: accepted and pushed as `6239147` (`feat(annotation-pack): consume complete reading products`).

### Slice 5 — Offline whole-book lifecycle and close-out

- Use the real Tiny Reader EPUB and normal parse/Runner/settlement/finalizer/Pack path.
- Inject deterministic Ingest/Digest test doubles only at the model boundary; do not bypass settlement, coordinates, storage, resume, finalizer, or export.
- Update final evidence, baseline separation, task status, and completion claims.

Acceptance: the offline full-book lifecycle covers Highlight, Note, empty Marginalia, invalid-item skip, crash/resume, repeated execution, and source mutation; all required offline checks pass.

Delivery: accepted and pushed as `a81a935` (`test(reading-product): accept offline whole-book lifecycle`). Immediately after push, local and `origin/codex/annotation-pack-v0` both resolved to `a81a9356988f7c711de5cac37eb7ae248e929134`.

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

- [x] canonical contract, examples, companion schemas, runtime copy, Pages projection, and offline checks agree;
- [x] default reading settlement commits one strict Product Unit before cursor advance;
- [x] resume/recovery honors Product Store commit truth without repeated model work;
- [x] whole-book finalizer publishes only complete immutable revisions and switches current atomically;
- [x] Annotation Pack and current chapter/API compatibility views consume Reading Product by default;
- [x] deterministic real-EPUB offline whole-book lifecycle passes through normal runtime seams;
- [x] privacy and private-artifact-deletion isolation tests pass;
- [x] unrelated pre-implementation baseline problems are listed separately rather than represented as Reading Product regressions;
- [x] Slices 1–4 were independently committed and pushed on `codex/annotation-pack-v0` without force-push;
- [x] Slice 5 was committed and pushed as `a81a935`; the post-push local/remote comparison matched at `a81a9356988f7c711de5cac37eb7ae248e929134`.

The allowed repo-local completion statement is:

> 当前默认阅读机制已经在代码层接入 Reading Product Output v1；使用真实 EPUB 和确定性模型替身，可以完成逐 Unit 提交、整书封版、兼容投影以及 Annotation Pack 的生成与独立验证。

This round must not claim a live LLM whole-book read, conversion of historical full-book outputs, public Pages availability, or native frontend display of Unit U/R. The later CPA configuration does not retroactively convert offline evidence into live evidence.

### 8.1 Offline acceptance evidence

- The tracked Tiny Reader EPUB passes through ordinary canonical parse, the default `attentional_v2` Reading Runner, real source-unit selection/coordinate resolution, Product Store settlement, crash recovery, finalization, compatibility projection, and the default Reading Product Annotation Pack adapter. Only model invocation boundaries use deterministic test doubles; no provider preflight or real LLM request runs. The final isolated rerun explicitly set `PYTHON_DOTENV_DISABLED=1` and `READING_OBSERVABILITY_OTLP_ENABLED=0`, so that acceptance process neither loaded the backend `.env` nor attempted OTLP export.
- `tests/reading_product/test_offline_whole_book_lifecycle.py` proves empty Marginalia, native Highlight, native Note, item-local bad-anchor rejection, product-commit-ahead recovery without a repeated Digest, source-mutation failure, immutable complete publication, repeated runner execution, and byte-stable `unchanged` Pack export.
- With the same dotenv/OTLP isolation, the dedicated lifecycle test completed with `1 passed`, and the combined focused close-out command over `tests/reading_product`, `tests/test_attentional_v2_reading_product.py`, and `tests/annotation_pack/test_tiny_reader_golden.py` completed with `39 passed`.
- Slice-specific evidence also completed with Reading Product core `22 passed`, attentional runtime `101 passed`, the Annotation Pack/consumer set `803 passed`, Tiny Reader deterministic rebuild of `10` files, and `make annotation-pack-contract-check` at `55 passed`.
- Final serial governance completed with `make reading-product-contract-check`, `make annotation-pack-contract-check`, `make contract-check`, and `make agent-check` all exiting `0` under dotenv/provider isolation. `agent-check` still reports only the separately cataloged historical traceability warnings.
- The complete backend suite completed with `1834 passed, 9 failed`. None of the nine failures is in Reading Product or Annotation Pack: seven unchanged legacy tests monkeypatch removed `invoke_structured_output_tool` attributes, one minimal-eval inventory assertion expects an older active dataset pointer, and one F4A target-balancing assertion expects two configured targets while the isolated offline registry exposes one. The pre-implementation `135 passed, 2 failed` affected regression baseline, these full-suite baseline categories, and the earlier concurrent `agent-check` transient remain separately recorded in `docs/implementation/annotation-pack/baseline-observations.md`; no all-green claim is inferred.
- Commit evidence is `d83707a`, `7dcd160`, `e7adccc`, `6239147`, and `a81a935`; all five Slice commits were pushed without force-push, and Slice 5's immediate post-push local/remote comparison matched.

## 9. Live acceptance

`TASK-READING-PRODUCT-OUTPUT-V1-LIVE-ACCEPTANCE` is complete for the bounded tracked Tiny Reader EPUB. The real run used `cpa_codex_local` / `gpt-5.6-luna` with `reasoning_effort=medium`, ordinary `parse_book` / `read_book`, the default `attentional_v2` mechanism, real Product settlement/finalization, and no model-boundary replacement.

- The local canonical LLM ledger contains `10` successful calls: `4` survey, `4` phase4/Ingest, and `2` phase6/Digest records. The real reading runtime reached `completed` in `188.17` seconds.
- The immutable complete Reading Product revision is `bb5e72ff170e3b551a203a45679630ff2cba755df98ac58d51e5e4ecaac6655b`, with `2` Product Units, non-empty Understanding/Response in both Units, and `6` Marginalia (`4` Highlights and `2` Notes).
- Both chapter compatibility projections were generated from Product Units. The default Reading Product adapter published detached Pack revision `2c57131dd1f36439f2226cd2ad6422d400427c9415cdc3b816e74e88e74cba1f`; standalone validation and inspection report `6` exported, zero skipped/warnings/errors, both TextQuote/TextPosition capabilities, and the same `4`/`2` kind split.
- The initial registered wrapper is terminal `failed` because its first post-read compatibility helper invocation was malformed, but its real model/runtime phase had already completed and published the Product. Four follow-up runs made no model calls and corrected acceptance-harness-only mistakes (helper arguments, SourceRange field access, generated timestamp precision, and `ValidationResult.publishable`); `validation_retry4` completed the terminal downstream verification. The failed wrapper is therefore retained as evidence rather than rewritten as a passing job.
- The run ledger authority is `reading-companion-backend/docs/evaluation/run_ledger.json`; ignored runtime evidence is rooted at `reading-companion-backend/state/reading_product_live_acceptance/cpa_luna_tiny_reader_20260830/`.
- Close-out verification passed: standalone Pack validate/inspect; the `31`-test Reading Product plus `attentional_v2` Product integration set; `make reading-product-contract-check`; `make annotation-pack-contract-check` (`55 passed`); root `make contract-check`; and root `make agent-check`. The first sandboxed root-check attempts were interrupted only because `tsx` could not create its local IPC pipe; both passed when rerun outside that sandbox. `agent-check` continues to print the pre-existing warning-only traceability and duplicate-decision inventory while exiting `0`.

This permits only the following added claim: **在 tracked Tiny Reader 短小真实 EPUB 上，当前默认机制已通过 CPA Luna 的真实 LLM 调用完成普通入口整书阅读，并生成 complete Reading Product、章节兼容投影和独立验证通过的 Annotation Pack。** It does not prove conversion of historical《悉达多》《纳瓦尔宝典》outputs, production-scale book quality/performance, public Pages availability, a native Unit API, frontend Understanding/Response, or Library/API/Reader integration.
