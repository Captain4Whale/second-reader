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
