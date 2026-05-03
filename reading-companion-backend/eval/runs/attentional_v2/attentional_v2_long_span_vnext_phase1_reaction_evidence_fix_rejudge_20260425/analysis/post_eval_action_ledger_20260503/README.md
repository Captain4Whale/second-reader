# Long Span vNext Phase 1 Post-Eval Action Ledger

This ledger records implementation actions derived from the Long Span vNext Phase 1 diagnostic evaluation, not a new score or benchmark result.

- Source evaluation run: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Source reading run: `attentional_v2_long_span_vnext_phase1_20260423`
- Current purpose: keep a run-local, appendable trail from evaluation findings to follow-up implementation work.
- Scope boundary: this ledger does not change scores, judge payloads, reading outputs, or benchmark status.

## How To Use This Ledger

Each action is recorded only after the underlying finding has been discussed and a concrete disposition exists. Do not use this file as a speculative backlog for ideas that have not been shaped yet.

Each action should answer:

- `action_id`
- `status`: `planned`, `in_progress`, `landed`, `deferred`, or `superseded`
- `source finding`: what the evaluation or human review exposed
- `decision`: what we decided to do
- `implemented changes`: what actually changed
- `validation`: how the change was checked
- `evidence links`: where to inspect the supporting code, docs, reports, or tests
- `follow-up`: whether the action is complete or still needs a later pass

## Actions

### A1 — Legacy gate/pressure cleanup

- `action_id`: `A1_legacy_gate_pressure_cleanup`
- `status`: `landed`
- `source finding`:
  - While reviewing the Memory Quality probe audit, the working-state overview still displayed `gate_state`, `pressure_snapshot`, and related `working_pressure` fields.
  - These fields came from the older `trigger/watch/zoom` control-door design and could mislead a reviewer into treating them as current memory-quality evidence.
- `decision`:
  - At the time of A1, keep `working_state.active_items` as the current hot-state mechanism while removing the older gate/pressure sidecar.
  - Remove `gate_state / pressure_snapshot / working_pressure` as active current entities in code, prompt-facing packets, runtime artifacts, resume, and evaluation evidence surfaces.
  - Preserve old run artifacts and historical documents as evidence, but make stable current docs clear that those fields are historical.
- `implemented changes`:
  - Current `WorkingState` is narrowed to the active-item model and no longer inherits the legacy working-pressure sidecar.
  - Prompt/context projection no longer carries `working_pressure_digest`, `gate_state`, or `pressure_snapshot`.
  - New runs no longer create or resume from `working_pressure.json` or `trigger_state.json`.
  - Slow-cycle and state-operation paths were updated to write the then-current active-item hot state directly instead of writing legacy control fields.
  - Current stable mechanism/evaluation/state docs mark the old control fields as deprecated historical design, not current runtime truth.
- `validation`:
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2*.py -q`
  - Result recorded at implementation time: `66 passed, 6 warnings`.
  - `git diff --check` passed at implementation time.
  - `docs/tasks/registry.json` parsed successfully as JSON at implementation time.
- `evidence links`:
  - Current mechanism contract: `../../../../../../../docs/backend-reading-mechanisms/attentional_v2.md`
  - State aggregation boundary: `../../../../../../../docs/backend-state-aggregation.md`
  - Evaluation method notes: `../../../../../../../docs/backend-reader-evaluation.md`
  - Current-state/task routing: `../../../../../../../docs/current-state.md`, `../../../../../../../docs/tasks/registry.md`
  - Decision history: `../../../../../../../docs/history/decision-log.md`
  - Original Memory Quality evidence audit that exposed the confusion: `../memory_quality_probe_audit_20260502/README.md`
- `follow-up`:
  - Complete for the gate/pressure cleanup itself.
  - The hot-state naming and fixed bucket vocabulary were later tightened by `A2_active_attention_cutover`.
  - If Memory Quality evidence docs are regenerated after this cleanup, the new generated snapshots should no longer present `gate_state / pressure_snapshot` as current state layers.
  - Existing pre-cleanup audit files remain historical evidence for the April 25 run and should not be silently rewritten as if they were produced after the cleanup.

### A2 — Active attention contract cutover

- `action_id`: `A2_active_attention_cutover`
- `status`: `landed`
- `source finding`:
  - While reviewing the Memory Quality evidence after A1, the remaining `Working State` name still sounded too broad: it could be mistaken for the whole agent state rather than the hot near-term attention layer.
  - The old `kind / bucket` vocabulary and derived lists such as `open_questions`, `live_tensions`, `live_hypotheses`, and `live_motifs` made the layer look like a fixed ontology. In particular, `live_hypotheses` could encourage over-reading plain source statements as extra interpretation.
- `decision`:
  - Rename the current native hot-state layer to `active_attention`.
  - Make `active_attention.active_items[]` the only current hot-state truth.
  - Replace fixed item categories with lightweight `attention_tags[]`.
  - Do not dual-write or dual-read `working_state` for new runs; old artifacts remain historical evidence only.
- `implemented changes`:
  - Current schemas, runtime shell, checkpoints, resume, artifact map, state operations, prompt packets, and Memory Quality probe export now use `active_attention`.
  - Runtime artifacts now write `active_attention.json`; new-format state operations target `active_attention`.
  - Active attention items carry `attention_tags[]`; current digests no longer emit `open_questions / live_tensions / live_hypotheses / live_motifs` as first-class lists.
  - `Read` prompt guidance now says ordinary local understanding belongs in `unit_delta`, while only material that will continue to shape reading should be written to `active_attention`.
  - Stable mechanism, state aggregation, evaluation, current-state, task registry, and decision-log docs now name `Active Attention` as the current hot-state contract.
- `validation`:
  - `python3 -m compileall -q reading-companion-backend/src/attentional_v2`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_attentional_v2*.py -q`
  - `cd reading-companion-backend && .venv/bin/python -m pytest tests/test_long_span_vnext.py -q`
  - `python3 -m json.tool docs/tasks/registry.json >/dev/null`
  - `git diff --check`
- `evidence links`:
  - Current mechanism contract: `../../../../../../../docs/backend-reading-mechanisms/attentional_v2.md`
  - State aggregation boundary: `../../../../../../../docs/backend-state-aggregation.md`
  - Evaluation method notes: `../../../../../../../docs/backend-reader-evaluation.md`
  - Current-state/task routing: `../../../../../../../docs/current-state.md`, `../../../../../../../docs/tasks/registry.md`
  - Decision history: `../../../../../../../docs/history/decision-log.md`
  - Code contract: `../../../../../../../reading-companion-backend/src/attentional_v2/schemas.py`, `../../../../../../../reading-companion-backend/src/attentional_v2/state_ops.py`, `../../../../../../../reading-companion-backend/src/attentional_v2/state_projection.py`
- `follow-up`:
  - Complete for current runtime and docs.
  - Later prompt polish can tune tag quality, but future work should treat `attention_tags[]` as lightweight labels, not as a mandatory taxonomy or routing contract.

### A3 — Read naturalization cutover

- `action_id`: `A3_read_naturalization_cutover`
- `status`: `landed`
- `source finding`:
  - While reviewing the `活出生命的意义` Memory Quality probe evidence, an important source-given framework appeared in local read interpretation but did not settle into durable memory: the author's three stages of prisoners' mental reaction to camp life.
  - This exposed a deeper prompt-shape problem: `Read` was still behaving too much like a field-filling node that separately fills local interpretation, visible reaction, and state operations.
- `decision`:
  - Keep the live loop `navigate.unitize -> read -> navigate.route`.
  - Naturalize the single `Read` call so it behaves like a reader: read the unit, form a natural impression, surface any underline / margin-note style reactions, then let material that should remain available settle into memory.
  - Rename the current contract fields from `unit_delta` to `reading_impression`, and from `implicit_uptake_ops` to `memory_uptake_ops`.
  - Do not dual-write or dual-read the historical field names in new runs.
- `implemented changes`:
  - `ReadUnitResult` now exposes `reading_impression`, `surfaced_reactions[]`, `memory_uptake_ops[]`, `pressure_signals`, and optional `detour_need`.
  - The `read_unit` prompt now addresses the model as a careful reader moving through the book, not as an authoritative field-filling node.
  - The prompt now treats `memory_uptake_ops` as natural memory settlement and explicitly allows source-given structures such as stage models, classifications, definitions, named distinctions, and chapter roadmaps to enter memory even without a visible reaction.
  - Runtime application, read audit, route reason, anchor creation, prompt manifests, tests, and stable docs now use the new field names.
  - Historical run artifacts and reports still retain old field names as historical evidence.
- `validation`:
  - Added prompt-contract coverage for `reading_impression` / `memory_uptake_ops`.
  - Added a focused contract regression for the `活出生命的意义` three-stage framework: the test asserts that a source-given stage model can produce a `thread_trace` memory operation without requiring a surfaced reaction.
  - Full validation commands are recorded in the task closeout for the implementation change.
- `evidence links`:
  - Current mechanism contract: `../../../../../../../docs/backend-reading-mechanisms/attentional_v2.md`
  - State aggregation boundary: `../../../../../../../docs/backend-state-aggregation.md`
  - Evaluation method notes: `../../../../../../../docs/backend-reader-evaluation.md`
  - Current-state/task routing: `../../../../../../../docs/current-state.md`, `../../../../../../../docs/tasks/registry.md`
  - Decision history: `../../../../../../../docs/history/decision-log.md`
  - Prompt/code contract: `../../../../../../../reading-companion-backend/src/attentional_v2/prompts.py`, `../../../../../../../reading-companion-backend/src/attentional_v2/nodes.py`, `../../../../../../../reading-companion-backend/src/attentional_v2/runner.py`, `../../../../../../../reading-companion-backend/src/attentional_v2/read_context.py`, `../../../../../../../reading-companion-backend/src/attentional_v2/schemas.py`
  - Focused test: `../../../../../../../reading-companion-backend/tests/test_attentional_v2_nodes.py`
- `follow-up`:
  - Complete for the read-contract naturalization itself.
  - A later slice may decide whether major persisted reactions should be selectively carried into future read context; that context-packaging choice was intentionally left out of A3.

### A4 — Memory Quality structural-signal supplement

- `action_id`: `A4_memory_quality_structural_signal_supplement`
- `status`: `landed`
- `source finding`:
  - During human review of the `活出生命的意义` Memory Quality report, Probe 1 exposed a concrete structural-memory concern: the source-so-far explicitly introduced the author's three-stage model of prisoners' mental reaction to camp life, but the then-current evaluation evidence did not make this a visible scoring focus.
  - This issue should not turn Memory Quality back into a hard case-hit KPI, but it should make the judge reliably notice whether salient author-given structures actually settle into memory.
- `decision`:
  - Keep Memory Quality as a holistic state-quality metric.
  - Add a structural-signal-aware supplement to the judge contract: stage models, classifications, core definitions, roadmaps, and named distinctions should be checked when they are salient in the source-so-far.
  - Add a lightweight `probe_review_focus` hook for known high-risk probes. The focus is a scoring aid, not an exact-match gold answer.
- `implemented changes`:
  - `run_long_span_vnext.py` now uses `memory_quality_judge_contract = scale_v3_structural_signal_aware`.
  - The Memory Quality judge prompt now explicitly says source text alone cannot earn credit, but salient source-given structures missing from the snapshot should affect the relevant dimension scores.
  - `huochu_shengming_de_yiyi_private_zh__segment_1` Probe 1 now carries a review focus for the three-stage prisoner-response framework.
  - Future reports and the source-map audit renderer surface `Structural Signals To Check` for probes with review focus.
  - Stable evaluation docs now describe this supplement as a structural-signal check rather than a hard gold-label task.
- `validation`:
  - Added prompt-contract coverage for the structural-signal-aware Memory Quality judge prompt.
  - Added test coverage that the `活出生命的意义` Probe 1 review focus is registered.
  - Added report-rendering coverage for showing structural-signal focus in Memory Quality reports.
- `evidence links`:
  - Runner / judge contract: `../../../../../../../reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
  - Source-map audit renderer: `../../../../../../../reading-companion-backend/scripts/temporary/memory_quality_probe_audit_source_map_20260503.py`
  - Long Span method docs: `../../../../../../../docs/backend-reader-evaluation.md`, `../../../../../../../reading-companion-backend/docs/evaluation/long_span/README.md`
  - Focused tests: `../../../../../../../reading-companion-backend/tests/test_long_span_vnext.py`
- `follow-up`:
  - Complete for the evaluation-contract supplement.
  - The fix will only be empirically validated after a fresh post-Read-naturalization Memory Quality run. The specific check is whether `活出生命的意义` Probe 1 snapshots retain the three-stage framework in active attention, concept, thread, anchor, or reflective memory layers.

### A5 — Local hypothesis provenance cleanup

- `action_id`: `A5_local_hypothesis_provenance_cleanup`
- `status`: `landed`
- `source finding`:
  - After the `A2_active_attention_cutover`, one residual slow-cycle provenance default still used the old term `local_hypothesis`.
  - That wording could make code or report reviewers think `local_hypotheses / live_hypotheses` still existed as current hot-state buckets, even though current runtime truth is `active_attention.active_items[]` plus lightweight `attention_tags[]`.
- `decision`:
  - Treat `local_hypothesis` and `live_hypotheses` as historical vocabulary only.
  - Use `active_attention_item` as the current default provenance when a reflective item is promoted from the hot attention layer.
  - Keep `attention_tags[]` as non-ontological labels; do not restore fixed question/tension/hypothesis/motif lists.
- `implemented changes`:
  - Slow-cycle reflective-item normalization now defaults `promoted_from` to `active_attention_item`.
  - Tests and current documentation now use the current provenance term.
  - Current state / task registry notes clarify that hypothesis-like material is either a tagged active-attention item or, if stable and reusable, concept/thread memory.
- `validation`:
  - Added a focused slow-cycle test for the default `promoted_from = active_attention_item`.
  - Static checks confirmed current `src/attentional_v2` code no longer contains `local_hypothesis / live_hypothesis / local_hypotheses / live_hypotheses`.
- `evidence links`:
  - Slow-cycle normalization: `../../../../../../../reading-companion-backend/src/attentional_v2/slow_cycle.py`
  - Slow-cycle tests: `../../../../../../../reading-companion-backend/tests/test_attentional_v2_slow_cycle.py`
  - Current mechanism contract: `../../../../../../../docs/backend-reading-mechanisms/attentional_v2.md`
  - State aggregation boundary: `../../../../../../../docs/backend-state-aggregation.md`
  - Evaluation method notes: `../../../../../../../docs/backend-reader-evaluation.md`
- `follow-up`:
  - Complete for terminology/provenance cleanup.
  - Future work can still tune `attention_tags[]` quality, but should not reintroduce fixed hot-state bucket lists.

### A6 — Memory Quality report contract

- `action_id`: `A6_memory_quality_report_contract`
- `status`: `landed`
- `source finding`:
  - While reviewing the Memory Quality source-map audit, the `Recent Moves` section labeled route explanations as `statement`, even though the data came from `move_history.moves[].reason`.
  - The report-writing shape had also been improved several times by hand, which created a risk that the next evaluation report would drift back into unreadable or inconsistent evidence layout.
- `decision`:
  - Treat Memory Quality report writing as part of the fixed Long Span vNext evidence contract.
  - Rename the report label for route explanations from `statement` to `move reason`.
  - Keep `Recent Moves` explicitly scoped as a compact projection from `move_history.moves[-3:]`, not as raw move history and not as long-term memory.
  - Persist the full evidence-report shape so future renderers reuse the same structure instead of reinventing it.
- `implemented changes`:
  - Added a stable Memory Quality evidence report contract under the Long Span evaluation docs.
  - Updated the source-map audit renderer so regenerated reports normalize `Recent Moves` sections to use `move reason` and explain their source.
  - Regenerated the current source-map audit docs so the visible report now uses the corrected label.
  - Linked the report contract from current Long Span evaluation docs, backend reader evaluation docs, current-state, and task registry.
- `validation`:
  - Regenerated `memory_quality_probe_audit_20260503_source_map` without changing scores, judgments, or reading outputs.
  - Checked that generated source-map reports contain 5 windows, 25 probes, 5 full source documents, and 25 raw snapshot links.
  - Checked that `Recent Moves` blocks no longer label route reasons as `statement`.
- `evidence links`:
  - Report contract: `../../../../../../../reading-companion-backend/docs/evaluation/long_span/memory_quality_report_contract.md`
  - Source-map renderer: `../../../../../../../reading-companion-backend/scripts/temporary/memory_quality_probe_audit_source_map_20260503.py`
  - Regenerated source-map audit: `../memory_quality_probe_audit_20260503_source_map/README.md`
  - Long Span evaluation docs: `../../../../../../../reading-companion-backend/docs/evaluation/long_span/README.md`
  - Stable evaluation method: `../../../../../../../docs/backend-reader-evaluation.md`
- `follow-up`:
  - Complete for the current report-writing contract.
  - Future Memory Quality report changes should update the contract first or in the same task as the renderer change.

## Next Actions Pending

The first six post-eval actions are recorded above. Later actions should be appended here only after their finding, decision, and implementation boundary have been agreed.

### Action Template

```text
### A<N> — <short action name>

- action_id:
- status:
- source finding:
- decision:
- implemented changes:
- validation:
- evidence links:
- follow-up:
```
