# Slice 8D: Lane A Source-locator Compatibility Triage and Minimal Patch - Post-implementation Report v0

## PR Title / Branch

`Slice 8D: Lane A Source-locator Compatibility Triage and Minimal Patch`

Branch: `main`

## Slice

Slice 8D / Post-implementation Review & Eval Readiness

## Summary Of Actual Changes

Slice 8D implements a narrow Lane A eval-runner compatibility patch for the failed Slice 8C source-locator seam.

The user-level selective runner now derives one `segment_source_v1` slice from a structured same-paragraph `primary_source_ref.source_span` when `target_locator` is absent. Locator precedence remains strict: `target_locator.source_span_slices`, direct char locator, `primary_source_ref.source_span`, then the existing `primary_anchor.locator` fallback.

Truly unlocatable visible reactions are no longer hard-aborts. They are skipped from matching and recorded as compact diagnostics (`unlocatable_reaction_count`, first reaction ids) in note-case mechanism results and aggregate summaries. They do not become candidates or matches.

No Lane A retry was launched, Lane B remains blocked, and this report does not claim product quality or eval success.

## Failure And Artifact Facts

Slice 8C Lane A failed on:

```text
rx:Full_Content:src:c1:p1@0-p3@146:highlight:1
```

Read-only inspection of the preserved failed run showed:

- `normalized_eval_bundle.json` contained `153` reactions.
- `0` reactions had a valid `target_locator`.
- `152` reactions had valid same-paragraph `primary_source_ref.source_span` evidence.
- `1` final retrospect had a zero-length chapter-end SourceRef and remains unlocatable under this patch.
- The failed reaction had `target_locator=null`, but had `primary_source_ref.source_span` with paragraph `3`, chars `73-106`, and `resolution.status="matched"` in the normalized bundle; the same structured SourceRef was present in `reaction_records.json`.

## Files Changed

- `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
- `reading-companion-backend/tests/test_run_user_level_selective_comparison.py`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`
- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
- `docs/current-state.md`
- `docs/tasks/registry.md`
- `docs/tasks/registry.json`

## Design Contracts Addressed

- Structured SourceRef evidence is used before any reaction-id parsing.
- Valid source-span overlap matching remains unchanged.
- Unlocatable reactions are diagnostics only; they are not converted into matches.
- The normalized eval export and runtime mechanism output are unchanged.
- Evidence catalog files are unchanged.
- Lane A retry, Lane B launch, judge calls, reading jobs, and new eval run directories remain blocked.

## Deviations From Accepted Plan

None.

## Tests Added Or Updated

Updated `test_run_user_level_selective_comparison.py` to cover:

- `primary_source_ref.source_span` fallback when `target_locator` is missing.
- `target_locator.source_span_slices` priority over conflicting `primary_source_ref`.
- invalid or zero-length SourceRefs skipped as unlocatable diagnostics.
- missing-locator contract updated from hard abort to diagnostic skip.
- aggregate summary carries compact unlocatable diagnostics.

## Commands Run

Read-only artifact inspection:

```bash
find reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517 -name 'normalized_eval_bundle.json' -o -name 'reaction_records.json' | sort
node - <<'NODE'
...read preserved Lane A normalized_eval_bundle.json and reaction_records.json...
NODE
```

Targeted tests:

```bash
cd reading-companion-backend && .venv/bin/python -m pytest tests/test_run_user_level_selective_comparison.py -q
```

Required static checks:

```bash
node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"
git diff --check
git diff --name-only -- reading-companion-backend/src/attentional_v2 reading-companion-frontend reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py reading-companion-backend/docs/evaluation/evidence_catalog.md reading-companion-backend/docs/evaluation/evidence_catalog.json
```

## Test Results

- Targeted pytest: `14 passed, 6 warnings`.
- `docs/tasks/registry.json` parse: passed.
- `git diff --check`: passed.
- Forbidden runtime/frontend/Long Span/evidence-catalog diff check: empty output.

## Contract / Audit Evidence Produced

This patch adds mechanism-eval diagnostics only:

- `locator_diagnostics.unlocatable_reaction_count`
- `locator_diagnostics.unlocatable_reaction_ids`
- aggregate `unlocatable_reaction_count`
- aggregate `unlocatable_reaction_observation_count`
- aggregate `unlocatable_reaction_ids`

These diagnostics are compatibility evidence, not product scores.

## Backward Compatibility Notes

Existing valid locators keep priority. Existing source-span overlap matching semantics remain unchanged. The patch is additive for structured SourceRef fallback and diagnostic reporting.

Invalid, missing, multi-paragraph, or zero-length `primary_source_ref.source_span` evidence is skipped and reported as unlocatable instead of matched.

## Explicit Boundaries

- No eval retry was launched.
- Lane B was not launched.
- No judge calls were made.
- No reading jobs were launched.
- No new eval run directories were created.
- No evidence catalog update was made.
- No runtime mechanism code was changed.
- No prompt text or prompt version was changed.
- No judge prompt was changed.
- No frontend, public API, or durable mechanism state was changed.
- No Long Span runner change was made.
- No new metrics or scoring taxonomy were introduced.
- Long Span vNext was not promoted to formal benchmark authority.

## Risk / Rollback Notes

Risk: diagnostic skip behavior could hide locator regressions if the counts are ignored.

Mitigation: skipped reactions are explicitly surfaced in note-case mechanism results and aggregate summaries. They are not treated as matches or scoring evidence.

Rollback is a simple revert of the eval-runner/test/docs patch. No migration or artifact cleanup is required.

## Known Gaps

- The failed Slice 8C Lane A run remains failed evidence; no `_retry1` run has been attempted.
- Lane B remains unexecuted and blocked.
- Multi-paragraph SourceRefs are not converted in this patch; they remain unlocatable diagnostics unless a later brief explicitly scopes support.
- The zero-length final retrospect SourceRef remains unlocatable by design.

## Next Recommended Step

Human reviewer reviews this Slice 8D Post-implementation Report.

If accepted, the next action should be a separate accepted execution brief for a Lane A `_retry1` run, or another explicitly scoped decision. Do not retry Lane A, launch Lane B, update the evidence catalog, or start another eval slice until this report is accepted and the next execution action is explicitly approved.

## Required Checks

- Did this PR change behavior, schema, prompt, audit, evaluation, or tests?
  - It changed the Lane A eval runner compatibility behavior and targeted tests only.
- Did this PR introduce new infrastructure?
  - No.
- Did this PR preserve SourceRef-first behavior?
  - Yes; structured `primary_source_ref.source_span` is the new fallback.
- Did this PR avoid audit dump into runtime prompt?
  - Yes; no prompts changed.
- Did this PR avoid reaction_records as semantic memory?
  - Yes; no runtime memory behavior changed.
- Did this PR avoid knowledge_activations as source truth?
  - Yes; no knowledge activation behavior changed.
- Is this PR safe to review as a small slice?
  - Yes.
