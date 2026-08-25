# Annotation Pack implementation baseline observations

Purpose: keep pre-existing, out-of-scope repository warnings separate from Annotation Pack Slice acceptance.

Observed on `2026-08-23` before and after Slice 1 with `make agent-check`:

- command exit status remains `0`; root contract, OpenAPI snapshot, frontend contract, and Annotation Pack checks pass
- the warning-only agent-switching audit still reports pre-existing traceability debt:
  - historical task records missing `acceptance_ref`
  - historical evidence paths pointing to retired `attentional_v2` files
  - `TASK-ACCUMULATION-BENCHMARK-V2` listed active in `docs/current-state.md` while its registry record is done
  - duplicate historical decision IDs `DEC-066` and `DEC-079`
- existing LangChain pending-deprecation warnings are emitted while importing unrelated runtime modules during three legacy contract checks

These observations are not Annotation Pack defects and were not repaired in this Epic. Slice acceptance must report them separately from focused failures and must not describe a warning-only `agent-check` as warning-free.

Observed while extracting the neutral no-write EPUB builder in Slice 2:

- the existing paragraph locator path maps `spine_index=0` through `int(value or -1)`, so the chapter retains spine index zero while its paragraph records carry `-1` and null CFI values; the extraction preserves and tests this behavior instead of silently repairing normal parsing
- the existing TOC parser may emit multiple canonical chapters when multiple fragment links address the same XHTML resource; Slice 2 normalizes fragments for identity/resource membership but does not change parser segmentation or reading behavior

Both parser behaviors predate Annotation Pack and remain explicit compatibility debt. They must not be presented as fixed by the neutral builder extraction; Slice 3 treats CFI as optional and continues to require quote/position validation from the exact verified resource.

Observed while running the broader Slice 2 affected-regression set on `2026-08-23`:

- `tests/test_attentional_v2_slow_cycle.py` has two pre-existing failures because the tests monkeypatch `slow_cycle.invoke_structured_output_tool`, while that module no longer exposes the attribute; the same test references and missing implementation symbol are present at the pre-Slice base commit `2d8aac2`
- the final combined affected set completed with `538 passed, 2 failed`; the Annotation Pack plus iterator parser acceptance set completed separately with `439 passed`

Slice 2 does not touch `attentional_v2/slow_cycle.py` or these tests. The two failures remain unrelated baseline test/interface drift and are not counted as Annotation Pack regressions.

Observed while running the broader Slice 3 affected-regression set on `2026-08-23`:

- the combined set completed with `612 passed, 2 failed`; both failures are the same two `tests/test_attentional_v2_slow_cycle.py` monkeypatch/interface-drift cases already reproduced at base `2d8aac2`
- the focused Annotation Pack + iterator parser + source-span set completed separately with `543 passed`
- Slice 3 does not modify `src/attentional_v2/slow_cycle.py`, the failing tests, Agent prompts, Digest, Memory, or the reading loop

The two failures remain unrelated baseline debt. They are not counted as Slice 3 regressions and were not repaired as part of the producer-neutral anchor/serialization work.

Observed while running the broader Slice 4 affected-regression set on `2026-08-23`:

- the combined set completed with `770 passed, 2 failed`; both failures are the same two `tests/test_attentional_v2_slow_cycle.py` monkeypatch/interface-drift cases already reproduced at base `2d8aac2`
- the full focused Annotation Pack suite completed separately with `636 passed`
- root `annotation-pack-contract-check`, `contract-check`, and `agent-check` exited `0`; the existing warning-only traceability and dependency deprecation output remains unchanged
- Slice 4 does not modify `src/attentional_v2/slow_cycle.py`, Agent prompts, Digest, Memory, the reading loop, frontend, or public HTTP APIs

The two failures remain unrelated baseline debt. They are not counted as Slice 4 regressions and were not repaired as part of the generic builder/validator work.

Observed while running the broader Slice 5 affected-regression set on `2026-08-23`:

- the combined set completed with `816 passed, 2 failed`; both failures are the same two `tests/test_attentional_v2_slow_cycle.py` monkeypatch/interface-drift cases already reproduced at base `2d8aac2`
- the full Annotation Pack suite completed separately with `682 passed`; the adapter-focused suite completed with `46 passed` and also passed independent adversarial replay under multiple hash seeds
- root `annotation-pack-contract-check`, `contract-check`, and `agent-check` exited `0`; the existing warning-only traceability and dependency deprecation output remains unchanged
- Slice 5 does not modify `src/attentional_v2/slow_cycle.py`, Agent prompts, Digest, Memory, the reading loop, frontend, public HTTP APIs, Readest, or Library

The two failures remain unrelated baseline debt. They are not counted as Slice 5 regressions and were not repaired as part of the strict current-native producer adapter.

Observed while running the broader Slice 6 affected-regression set on `2026-08-23`:

- the existing-mechanism regression command completed with `134 passed, 2 failed`; both failures are the same two `tests/test_attentional_v2_slow_cycle.py` monkeypatch/interface-drift cases already reproduced at base `2d8aac2`
- Slice 6 focused exporter/CLI/lease/artifact acceptance completed with `174 passed`, and the full Annotation Pack suite completed separately with `782 passed`
- root `annotation-pack-contract-check` completed with `42 passed` plus a valid Pages projection; `contract-check` and `agent-check` exited `0`
- the root checks still emit the already recorded dependency deprecations, history reminder, and warning-only agent-switching traceability debt; these warnings are not described as clean or fixed
- Slice 6 does not modify `src/attentional_v2/slow_cycle.py`, Agent prompts, Digest, Memory, the reading loop, frontend, public HTTP APIs, Readest, or Library discovery/completion behavior

The two failures remain unrelated baseline debt. They are not counted as Slice 6 regressions and were not repaired as part of explicit JSON Annotation Pack publication.

Observed while running the broader Slice 7 affected-regression set on `2026-08-23`:

- the existing-mechanism regression command completed with `134 passed, 2 failed`; both failures are the same two `tests/test_attentional_v2_slow_cycle.py` monkeypatch/interface-drift cases already reproduced at base `2d8aac2`
- Slice 7 focused package/exporter/CLI/artifact acceptance completed with `221 passed`, and the full Annotation Pack suite completed separately with `876 passed`
- compileall and selected Ruff checks passed; root contract/governance checks are recorded in the Slice 7 checkpoint separately from their warning-only dependency/history/traceability output
- Slice 7 does not modify `src/attentional_v2/slow_cycle.py`, Agent prompts, Digest, Memory, the reading loop, frontend, public HTTP APIs, Readest, or Library discovery/completion behavior

The two failures remain unrelated baseline debt. They are not counted as Slice 7 regressions and were not repaired as part of detached Annotation Pack packaging or publication.

Observed while closing Slice 8 on `2026-08-24`:

- the Tiny Reader golden plus job-lease/concurrent-resume focused set completed with `55 passed`; the full Annotation Pack suite completed with `882 passed`
- the required existing-mechanism/parser/lease regression set completed with `183 passed, 2 failed`; both failures are the same two `attentional_v2.slow_cycle` monkeypatch/interface-drift cases already reproduced at base `2d8aac2`
- the full backend suite completed with `1882 passed, 9 failed`; an exact replay at base `2d8aac2` reproduced all nine failures:
  - three `attentional_v2.bridge` tests, two `attentional_v2.survey` tests, and the two already recorded `attentional_v2.slow_cycle` tests still monkeypatch removed `invoke_structured_output_tool` module attributes
  - one minimal-eval inventory test expects an older active dataset pointer than the tracked manifest now declares
  - one F4A quality-audit test expects two default targets while the current environment/config exposes one
- the first pre-Slice-8 full-suite run also exposed one additional concurrent-resume failure in `test_library_api.py` that did **not** reproduce at base. Investigation traced it to the Slice 6 strict lease scan racing a legitimate heartbeat sidecar replacement. The final patch takes the existing per-job lock while reading each sidecar under the already-held book lock, preserving the established `book -> job` order and all no-follow/identity checks. Its focused suite passed `49` tests, twenty isolated repetitions passed, and the final full backend suite no longer contains that failure.
- `annotation-pack-contract-check`, `contract-check`, and `agent-check` all exited `0`; the golden rebuild verified nine generated files and the contract slice remained `42 passed`. Agent check still reports only the historical traceability issues cataloged at the top of this document, and dependency imports still emit the recorded deprecation warnings.

The nine remaining full-suite failures are separately evidenced historical baseline drift and are not described as passing. The concurrency failure was an Annotation Pack regression and was repaired before Slice 8 acceptance rather than being relabeled as baseline.

Observed while accepting the minimal-v0 atomic replacement in Slice 2 on `2026-08-25`:

- authority reset `012788d` and atomic wire cutover `b44ba7d` were committed separately and pushed to `origin/codex/annotation-pack-v0`
- `make annotation-pack-contract-check` completed with `55 passed`; the complete Annotation Pack suite completed with `794 passed`
- `b44ba7d` replaced the canonical wire, runtime copies, producer/export/package path and Tiny Reader goldens together; it removed the custom JSON-LD context publication surface and did not retain an old-wire or phase8 compatibility layer
- Slice 2 did not modify `src/attentional_v2/slow_cycle.py` or `tests/test_attentional_v2_slow_cycle.py`

Observed for the minimal-v0 Slice 3 final candidate on `2026-08-25`:

- the required related Agent/source regression set completed with `134 passed, 2 failed`
- both failures are the same pre-existing `tests/test_attentional_v2_slow_cycle.py` cases that monkeypatch the removed `slow_cycle.invoke_structured_output_tool` module attribute; this test/interface drift was already reproduced at pre-Annotation-Pack base `2d8aac2`
- the two failures remain unrelated baseline debt: they are not counted as Annotation Pack regressions, were not repaired in the minimal-wire replacement, and are not described as passing
- the complete backend suite completed with `1794 passed, 9 failed`; the nine failures match the existing baseline categories already cataloged in this document: three `attentional_v2.bridge`, two `attentional_v2.survey` and two `attentional_v2.slow_cycle` cases monkeypatch the removed `invoke_structured_output_tool` module attributes, one minimal-eval inventory case expects an older active pointer, and one F4A quality-audit case expects two default targets while the current environment/config exposes one
- the minimal replacement did not touch those mechanisms, evaluation inventory or F4A target configuration; the nine failures are recorded explicitly and the full backend result is not represented as green
- no real whole-book Agent run or conversion of the historical Siddhartha/Naval artifacts was performed; Pages was not deployed or served-byte verified; Library, HTTP API, frontend and Reader integration were not implemented or claimed

Final minimal-v0 governance on `2026-08-25` completed with both `make contract-check` and `make agent-check` exiting `0`. The commands still emitted the historical traceability and LangChain warnings cataloged above. The contract check also emitted its warning-only high-signal-document reminder because close-out synchronizes `AGENTS.md`, backend aggregation, and backend rules; no additional decision entry was added because `DEC-156` already records the minimal-v0 direction and this Slice introduces no new product or architecture decision.

This evidence supports only the repo-local Tiny Reader fixture claim. Slice 3 is closed by the commit containing this acceptance record, followed by a non-force push and local/remote HEAD comparison recorded in the final handoff.
