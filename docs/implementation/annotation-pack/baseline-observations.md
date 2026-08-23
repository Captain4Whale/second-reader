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
