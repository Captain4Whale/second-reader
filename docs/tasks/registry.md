# Task Registry

Purpose: provide the canonical workspace task index for agent switching, routing, and traceability.
Use when: choosing what to work on next, recovering a task without chat history, or checking blockers, evidence, and linked truth docs.
Not for: full tracker detail, long-form design rationale, or mutable runtime job state.
Update when: task status, priority, blockers, decision refs, job refs, evidence refs, or next actions change.

This document is the human-readable companion to `docs/tasks/registry.json`.

Last updated: `2026-07-04T19:43:48+08:00`

## Status Values
- `active`
- `blocked`
- `queued`
- `waiting`
- `parked`
- `done`
- `cancelled`

## Active

### `TASK-SECOND-READER-INGEST-DIGEST-REFRAME-AUDIT-20260530` — Maintain the implemented Ingest/Digest and Unit Memory mechanism track
- Status: `active`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/current-state.md`
- Next: Digest is live as `attentional_v2.digest.v24` / promptset `attentional_v2-phase6-v84` / output contract `digest_understanding_response_marginalia_json_v8`: canonical visible-note output remains `marginalia[]` with explicit `kind: "highlight" | "note"`, and Notes remain an independent pass with non-empty visible `content`. The active diagnostic run `bgjob_digest_marginalia_v24_5book_parallel_fullwindow_20260704` is running over all five active unique-note dataset windows with `segment_workers=5`, high cap `units-per-segment=9999`, and `DEC-150` long partial-mode recovery (`6` extra same-cursor unit retries, delay schedule `0,120,300,600,900,1200`, `3600s` per-unit budget). After completion, inspect Ingest-selected units, Understanding, Response / `reading_impression`, Marginalia, and Unit Memory retrieval traces; if any segment ends `partial`, continue from the analysis root with a `..._continue1` run and preserve sibling-segment evidence.
- Jobs:
  - `bgjob_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5`
  - `bgjob_unit_memory_text_only_smoke_value_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_r9_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_r11_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_hot_exclusion_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_r13_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_r14_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_r15_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_r16_aux_backing_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_r15_mature_20260606`
  - `bgjob_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_20260606`
  - `bgjob_ingest_live_v16_token_preview_larger_to_old_unit13_20260613`
  - `bgjob_source_normalization_v1_1_multibook_validation_20260613`
  - `bgjob_ingest_live_v17_source_norm_token_preview_to_chapter1_20260614`
  - `bgjob_ingest_live_v17_source_norm_token_preview_to_chapter1_retry1_20260614`
  - `bgjob_digest_marginalia_v16_5book_parallel_20units_20260621`
  - `bgjob_digest_marginalia_v19_5book_parallel_20units_20260621`
  - `bgjob_digest_marginalia_v20_5book_parallel_20units_20260629`
  - `bgjob_digest_marginalia_v21_5book_parallel_20units_scheduler_fixed_retry1_20260630`
  - `bgjob_digest_marginalia_v22_5book_parallel_20units_20260701`
  - `bgjob_digest_marginalia_v23_5book_parallel_20units_20260701`
  - `bgjob_digest_marginalia_v23_5book_parallel_20units_recovery_retry1_20260702`
  - `bgjob_digest_marginalia_v24_5book_parallel_20units_20260703`
  - `bgjob_digest_marginalia_v24_5book_parallel_20units_continue1_20260704`
  - `bgjob_digest_marginalia_v24_5book_parallel_fullwindow_20260704`
- Evidence:
  - `DEC-103`
  - `DEC-104`
  - `DEC-105`
  - `DEC-106`
  - `DEC-107`
  - `DEC-108`
  - `DEC-109`
  - `DEC-110`
  - `DEC-112`
  - `DEC-113`
  - `DEC-114`
  - `DEC-115`
  - `DEC-116`
  - `DEC-117`
  - `DEC-118`
  - `DEC-120`
  - `DEC-121`
  - `DEC-122`
  - `DEC-123`
  - `DEC-124`
  - `DEC-125`
  - `DEC-126`
  - `DEC-127`
  - `DEC-128`
  - `DEC-129`
  - `DEC-130`
  - `DEC-131`
  - `DEC-132`
  - `DEC-133`
  - `DEC-134`
  - `DEC-135`
  - `DEC-136`
  - `DEC-137`
  - `DEC-138`
  - `DEC-139`
  - `DEC-140`
  - `DEC-141`
  - `DEC-142`
  - `DEC-143`
  - `DEC-144`
  - `DEC-145`
  - `DEC-146`
  - `DEC-147`
  - `DEC-148`
  - `DEC-149`
  - `DEC-150`
  - `docs/current-state.md`
  - `docs/backend-reader-evaluation.md`
  - `docs/implementation/new-reading-mechanism/ingest-context-and-navigate-mapping.md`
  - `docs/implementation/new-reading-mechanism/digest-understanding-response-marginalia-design.md`
  - `docs/implementation/new-reading-mechanism/digest-marginalia-quality-sourcebook.md`
  - `docs/implementation/new-reading-mechanism/digest-marginalia-prompt-revision-design.md`
  - `docs/implementation/new-reading-mechanism/unit-memory-hybrid-retrieval-design.md`
  - `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`
  - `docs/implementation/new-reading-mechanism/ingest-digest-unit-memory-conformance-goal.md`
  - `docs/implementation/new-reading-mechanism/ingest-select-next-unit-window-partition-draft-prompt.md`
  - `docs/implementation/new-reading-mechanism/ingest-next-unit-optimization-design.md`
  - `docs/implementation/new-reading-mechanism/source-normalization-design.md`
  - `reading-companion-backend/src/reading_runtime/source_normalization.py`
  - `reading-companion-backend/src/reading_core/book_document.py`
  - `reading-companion-backend/src/iterator_reader/parse.py`
  - `reading-companion-backend/scripts/run_source_normalization_v1_1_multibook_validation.py`
  - `reading-companion-backend/tests/test_iterator_parse.py`
  - `reading-companion-backend/tests/test_attentional_v2_source_spans.py`
  - `docs/implementation/new-reading-mechanism/mechanism-pattern-ledger.md`
  - `docs/implementation/new-reading-mechanism/unit-memory-retrieval-repair-validation-plan.md`
  - `docs/implementation/new-reading-mechanism/llm-structured-output-protocol-note.md`
  - `docs/implementation/new-reading-mechanism/codex/reports/Ingest-Digest-UnitMemory-Conformance-Smoke-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_value_20260606/analysis/unit_memory_retrieval_health/summary.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_value_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606/analysis/unit_memory_retrieval_health/summary.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r9_20260606/analysis/unit_memory_retrieval_review/README.md`
  - `docs/implementation/new-reading-mechanism/codex/reports/UnitMemory-Retrieval-TextOnly-PostR9-Relevance-Review v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606/analysis/unit_memory_retrieval_health/summary.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r11_20260606/analysis/unit_memory_retrieval_review/README.md`
  - `docs/implementation/new-reading-mechanism/codex/reports/UnitMemory-Retrieval-TextOnly-PostR11-Smoke-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v5_20260606/analysis/unit_memory_retrieval_review/README.md`
  - `docs/implementation/new-reading-mechanism/codex/reports/UnitMemory-Retrieval-TextOnly-PostIngestV5-Smoke-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_selection_cap_20260606/analysis/unit_memory_retrieval_review/README.md`
  - `docs/implementation/new-reading-mechanism/codex/reports/UnitMemory-Retrieval-TextOnly-PostSelectionCap-Smoke-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606/analysis/unit_memory_recall_language_review/summary.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606/analysis/unit_memory_recall_language_review/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606/analysis/unit_memory_retrieval_health/summary.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_20260606/analysis/unit_memory_recall_language_review/summary.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_20260606/analysis/unit_memory_recall_language_review/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r15_mature_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r15_mature_20260606/analysis/unit_memory_post_r15_mature_review/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r16_aux_backing_20260606/analysis/unit_memory_retrieval_health/README.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_r16_aux_backing_20260606/analysis/unit_memory_post_r16_aux_backing_review/README.md`
  - `reading-companion-backend/tests/test_unit_memory_hybrid_readiness_script.py`
  - `reading-companion-backend/scripts/check_unit_memory_hybrid_readiness.py`

### `TASK-ATTENTIONAL-V2-STRUCTURAL-REWORK` — Execute the post-Phase-9 structural rework of `attentional_v2`
- Status: `active`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/attentional_v2_structural_rework_plan.md` (historical slice ledger after `DEC-108`)
- Next: continue implementation from the current `Ingest -> Digest -> Reading Runner settlement` baseline:
  - keep the work under the existing `attentional_v2` mechanism key rather than minting `attentional_v3`
  - treat the structural rework plan as backend-only historical context; current mechanism authority lives in `docs/backend-reading-mechanisms/attentional_v2.md`
  - keep the existing frontend lane active in parallel under `TASK-V2-NATIVE-READING-PRESENTATION`
  - `Phase A` is now landed:
    - heuristic trigger output no longer suppresses formal正文 reading
    - this phase introduced the historical `Navigate.unitize + read + Reading Runner post-read settlement` skeleton that is now absorbed into `Ingest + Digest + Reading Runner post-Digest settlement`
    - span authority now matches the exact chosen unit
  - `Phase B` is now landed:
    - the concrete current-unit packet is now owned by `Digest`
    - the live runner now builds bounded carry-forward context from current state projections
    - mechanism-private `read_audit` records now capture carried refs and current `ingest_trace` shape; the temporary `raw_reaction` shell from that slice was later retired by `Phase F3`
  - `Phase C.1` is now landed:
    - live prompt inputs now flow through a bounded internal `state_packet.v1` layer
    - historical `Navigate.unitize` received a small `navigation_context`; current `Ingest` no longer receives that packet
    - the then-current concrete reading node received a packetized context that explicitly separated continuity capsule, active-attention digest, reflective frame, active focus, and source-ref digest
    - persisted runtime files and public/frontend compatibility surfaces remain unchanged
  - `Phase C.2` and `Phase C.3` are now historical state-territory experiments:
    - they introduced content-typed long-memory digests and stores during the post-eval structural rework
    - `DEC-109` supersedes that direction; current live code no longer exposes the retired concept/thread structured stores in schema, prompt packets, runtime artifacts, checkpoints, settlement, audit, or tests
    - current long-memory direction is a content-neutral Unit Memory baseline; `DEC-110` now implements the ledger/index/retrieval trace bottom framework, and its follow-through slice implements bounded Ingest recalls, the `retrieve_unit_memory` tool loop, runtime-owned retrieval selection, and Digest `ReadingMemory` packaging
    - old V2 state stores were demoted to cutover-only legacy territory during the cutover
    - old supplemental retrieval helpers from that branch were removed from the current code surface by `DEC-105`; current `Ingest` retrieval uses a separate Unit Memory recall/tool path rather than those retired helpers
    - checkpoint/resume temporarily accepted both old and new state territory during the cutover, while newly written checkpoints already used only the new primary keys
  - `Phase C.4` is now landed:
    - sentence-intake / slow-cycle now consume and write the new primary state layers directly; the old Anchor Bank relation-writing Bridge path is paused
    - the live runner no longer projects new state back into old V2 helper stores to execute helpers
    - live runtime loading and resume now reject pre-`Phase C.3` runtime directories and checkpoints
    - public/frontend compatibility surfaces remain unchanged
  - legacy gate/pressure sidecar cleanup is now landed:
    - current hot state is `active_attention.active_items[]`
    - active items now carry lightweight `attention_tags[]`; old `working_state` naming and fixed lists are historical
    - residual `local_hypothesis` / `live_hypotheses` vocabulary has been retired from current provenance; future hypothesis-like material should use content-neutral unit memory rather than the retired typed stores
    - old `gate_state`, `pressure_snapshot`, and working-pressure runtime artifacts are no longer current schema, prompt, runtime, checkpoint, or Memory Quality evidence fields
    - old `pressure_signals` were removed with the forward-settlement cutover; current `Digest` emits model-facing `understanding`, `response`, and `annotations`
  - `Phase D` is now landed:
    - that branch once explored a budget-bounded multi-step supplemental context loop around the old concrete reading node
    - runtime state and full checkpoints now persist a lightweight `continuation capsule` with rehydration entrypoints
    - warm resume now restores the latest usable continuation capsule together with new-format runtime/checkpoint state
    - the old supplemental source-span helper is no longer a current code, prompt, audit, or test interface after `DEC-105`
  - `Phase E1` through `Phase E3` are now preserved as a landed intermediate branch:
    - that branch retained the temporary old concrete reading-node -> Express split
    - persisted `reaction_records` now keep surfaced fields first
    - slow-cycle compatibility projection and normalized eval export now derive old family labels through one compat helper instead of treating legacy `type` as the internal truth
    - this branch remains valuable evidence, but it is no longer the approved end-state target
  - `Phase F1` is now landed:
    - the live per-unit loop was historically cut back to `Navigate.unitize -> read -> Reading Runner post-read settlement`; current code now calls it through `Ingest -> Digest -> Reading Runner post-Digest settlement`
    - `Digest` now owns model-facing `understanding`, `response`, and `annotations`
    - the dedicated live `Express` node is no longer on the runner path
    - `Digest` prompt packaging now follows XML context blocks with compact carried state
  - Digest naturalization is now landed on top of the F-line:
    - the prompt now frames `Digest` as a reader moving through the book rather than a field-filling node
    - current LLM-facing output fields are `understanding`, `response`, and `annotations`; `unit_delta`, `implicit_uptake_ops`, model-emitted `memory_uptake_ops`, and the prior model-facing `recent_reading_memory` contract are historical field names
    - explicit source structures that matter later, such as stage models or classifications, can settle into memory even without a visible reaction
  - `Phase F2` is now historical after `DEC-104`:
    - the old live Detour / source-backread path has been retired from the current runtime
    - `DEC-105` hard-purges the retired compatibility interfaces from current code, prompts, schemas, audits, and tests
    - `Ingest` now chooses only the next forward source unit
    - current `Digest` has no path-redirection output contract
    - current `local_continuity`, prompt manifests, and read audits do not emit retired Detour-era fields for new runs
  - Paragraph-offset mainline cursor and SourceRef cutover are now landed:
    - `SourceCursor` uses `chapter_id`, `chapter_ref`, `paragraph_index`, and `char_offset`
    - `Ingest` receives an adaptive paragraph-offset preview and returns `unit.end_paragraph_n` plus `unit.end_at`
    - `Reading Runner` resolves that boundary into an end-exclusive `SourceSpan`, advances to `end_cursor`, and records accepted units in `_mechanisms/attentional_v2/runtime/unit_span_ledger.jsonl`
    - sentence ids remain available for eval and reviewer orientation, but no longer define the `attentional_v2` mainline cursor
    - memory/reaction/probe-facing source evidence now uses inline `SourceRef` values (`source_span_id`, `source_span`, `quote`, `role`)
    - `anchor_bank.json` is no longer a canonical runtime artifact or checkpoint key for new runs; old anchor-bank runtimes must be rerun
    - chapter-end `active_attention` carry-forward now preserves inline `source_refs[]` by deterministic `item_id` merge after cooling; `chapter_consolidation` still decides what carries forward, but omission of `source_refs` no longer erases existing evidence coordinates
    - historical verification job `bgjob_attentional_v2_source_ref_nawaer_active_attention_fix_20260506` completed as a no-judge `nawaer` smoke; its old automatic check still expected now-retired structured stores such as `thread_trace`, so it is not a current blocker or next-step driver after `DEC-109` / `DEC-110`
  - `Phase F3` is now landed:
    - persisted visible reactions now enter the system only through `Digest.surfaced_reactions[]`
    - current forward reading uses one surfaced-native reaction-record builder; old non-mainline read artifacts are historical only
    - chapter-result compatibility projection and normalized eval export now read surfaced-native persisted records and derive old family labels only through the compat helper
    - dead live ownership paths for the old `Express` persistence flow and `raw_reaction` fallback are now removed
  - `Phase F4A` is now landed as the first focused quality-audit pack:
    - temporary one-off launcher / harness:
      - `reading-companion-backend/scripts/temporary/attentional_v2_f4a_oneoff_quality_audit.py`
    - completed job:
      - `bgjob_attentional_v2_f4a_quality_audit_20260419`
    - run id:
      - `attentional_v2_f4a_quality_audit_20260419`
    - outcome:
      - visible reaction density recovered across all six short-window cases
      - sampled wording is mostly back in reading-time territory
      - chapter-result compatibility projection and normalized eval export both survived
      - non-mainline path behavior from the historical F2 branch was not treated as validated product evidence
        - every shard stayed on the forward reading path
        - `backward_pull = 0` in every shard
      - surfaced optional semantics were also absent:
        - `prior_link_count = 0`
        - `outside_link_count = 0`
        - `search_intent_count = 0`
    - audit note:
      - `reading-companion-backend/docs/research/attentional_v2_f4a_focused_quality_audit_20260419.md`
    - run summary:
      - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_f4a_quality_audit_20260419/summary/report.md`
    - follow-up visibility fix already landed:
      - future `read_audit.jsonl` rows now persist full `surfaced_reactions`
      - the F4A summary/report harness now records explicit compat / normalized artifact availability
  - trigger/watch cleanup now also landed on top of the F4A baseline:
    - sentence intake is now pure `local_buffer` ingest
    - live runtime / checkpoint / resume no longer carry `trigger_state`
    - historical `Navigate.unitize` stopped receiving heuristic `watch_state`
    - the dead `trigger -> zoom_read -> meaning_unit_closure -> controller_decision -> reaction_emission` path has been removed from live code
    - `text_role` is now explicitly documented as an inherited block-level weak cue
  - the first special-content handling slice is now also landed on that cleaned baseline:
    - historical `Navigate.unitize` began treating heading roles as weak cues rather than automatic standalone units
    - meaningful headings may still stand alone, but label-like headings now prefer merging with the immediately following body paragraph when the preview allows
    - deterministic fallback now widens `heading + first body paragraph` instead of returning a bare heading when that body paragraph is already visible
    - `Digest` now explicitly stays proportionate around thin heading-like units and may remain silent there
  - `Phase F4B` is now landed as the survey-led `body-first` scheduling slice:
    - `survey` now runs one narrow LLM-backed `chapter_zone` classifier over lightweight structural samples
    - `survey_map.json` now persists both chapter-level zones and one machine-readable `reading_plan`
    - `runner` now consumes that plan in full-book mode:
      - `main_body` chapters first
      - deferred `front_support` / `back_support` chapters after the mainline queue drains
    - explicit chapter-targeted reads and benchmark windows are not forcibly reordered
    - runtime continuity and resume shell now carry `reading_queue_stage` for `mainline` vs `deferred_support`
  - the unit-internal anchor-selection repair is now landed on top of the cleaned F4A baseline:
    - `Digest` now prefers the smallest complete contiguous surfaced anchor inside a unit
    - multiple independently complete anchors inside one unit are now explicitly allowed
    - the repair is aimed at preventing a sharper later line from swallowing an earlier independently complete framing / hinge line
  - focused repair-level validation is now completed:
    - before:
      - `attentional_v2_f4a_quality_audit_20260419`
    - after:
      - `attentional_v2_window_ab_after_20260421`
    - comparison note:
      - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_window_ab_after_20260421/analysis/focused_window_ab_compare_20260421/README.md`
    - observed window-level lift:
      - `value_of_others_private_en__8_10`: visible reactions `6 -> 8`, with the selected setup hinge now surfaced
      - `huochu_shengming_de_yiyi_private_zh__segment_1`: visible reactions `8 -> 11`, with `silent_unit_count 3 -> 2`
    - evidence-boundary note:
      - this is valid window-level density/style evidence, but not the same thing as a direct proof about the narrower `People want things from other people.` regression sentence
  - next validation line:
    - let the V2-only full-window overnight spot check finish on the same two titles before deciding whether this repair is broad enough for wider reruns
    - then decide whether the new `body-first` scheduling slice needs its own focused full-book validation on support-heavy books such as `nawaer_baodian_private_zh`
    - active job:
      - `bgjob_attentional_v2_full_window_spotcheck_20260421`
    - run id:
      - `attentional_v2_full_window_spotcheck_20260421`
    - dedicated watchdog:
      - `bgjob_job_registry_auto_recovery_watchdog_full_window_spotcheck_20260421`
- Post-Phase-D evaluation posture:
  - the April 12 post-Phase-D smoke is finished and the April 13 targeted judged validation is also finished
  - completed judged runs:
    - `attentional_v2_post_phase_d_longspan_judged_20260413`
    - `attentional_v2_post_phase_d_excerpt_regression_20260413`
  - parent job id:
    - `bgjob_post_phase_d_parallel_judged_eval_retry2_20260413`
  - top-line comparative outcome:
    - `excerpt`:
      - prior formal `attentional_v2_excerpt_surface_v1_1_judged_20260406`
      - current `attentional_v2_post_phase_d_excerpt_regression_20260413`
      - `selective_legibility` changed from `27 / 21 / 11` to `24 / 24 / 11`
      - `insight_and_clarification` changed from `19 / 16 / 8` to `15 / 21 / 7`
    - `long-span`:
      - prior formal `attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407`
      - current `attentional_v2_post_phase_d_longspan_judged_20260413`
      - `coherent_accumulation` changed from `2 / 5` to `3 / 4` (`attentional_v2 / iterator_v1`)
      - `insight_and_clarification` changed from `2 / 4 / 1` to `1 / 5 / 1` (`attentional_v2 / iterator_v1 / tie`)
  - current audit direction:
    - treat the next durable output as the cross-run comparative audit set rather than another rerun
    - use these new evidence docs as the audit entrypoint:
      - `reading-companion-backend/docs/research/attentional_v2_post_phase_d_eval_comparative_audit_20260414.md`
      - `reading-companion-backend/docs/research/attentional_v2_post_phase_d_eval_comparative_audit_20260414_longspan_appendix.md`
      - `reading-companion-backend/docs/research/attentional_v2_post_phase_d_eval_comparative_audit_20260414_excerpt_appendix.md`
  - current interpretation constraint:
    - the key hard signal is not only winner movement but `attentional_v2` evidence-density collapse
    - excerpt average matched reactions dropped from `7.0` to `1.0`
    - long-span average matched reactions dropped from `19.71` to `2.29`
  - no active background eval jobs remain in the registry
- Archived diagnostic attempts:
  - `bgjob_value_of_others_ch8_debug_trace_20260413` (`failed`, archived after fixing registry-isolation bug in the launcher)
  - `bgjob_value_of_others_ch8_debug_trace_retry1_20260413` (`failed`, archived after verifying isolated registry load but hitting separate-key `MiniMax-M2.7` plan rejection)
- Evidence addendum:
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_post_phase_d_longspan_smoke_20260412/diagnostics/value_of_others_abnormal_call_snapshot_20260413.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_post_phase_d_longspan_smoke_20260412/diagnostics/value_of_others_progress_and_latency_check_20260413.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_value_of_others_ch8_debug_legacykey_20260413/analysis/registry_snapshot.json`

### `TASK-V2-NATIVE-READING-PRESENTATION` — Redesign the routed reading surfaces around chapter text and source-referenced reactions
- Status: `active`
- Lane: `migration`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/phase9-compat-cutover-roadmap.md`
- Next: keep `iterator_v1` section-first presentation in compatibility-only posture and continue the V2-native frontend lane from the new truth baseline. The first bounded truth/visibility slice is now landed and browser-validated:
  - overview fixes completed:
    - contradictory live status labels on `/books/:id`
    - false-empty recent trail when `recent_reactions` exists but mindstream history is sparse
    - live V2 overview chips for:
      - `reading_locus`
      - `active_reaction_id`
  - source-reader fixes completed:
    - honest slow-loading message
    - explicit missing-source state
    - explicit timeout/failure state instead of indefinite `Loading source EPUB...`
  - lifecycle/status-truth fixes completed:
    - stale orphan runtime snapshots now project to `paused` instead of fake live `analyzing`
    - routed bookshelf and overview now consume additive `status_reason`
    - paused stale/interrupted books now render last-known reading position honestly
    - resume CTA now stays hidden when `resume_available = false`
  - next redesign the chapter and marks surfaces around anchors and live thought lineage, with these page roles fixed:
    - `/books/:id/chapters/:chapterId` is the main chapter reading scene and default return-to-context page
    - `/marks` is the saved-reaction list plus jump-back surface, not the main reading scene
  - do not open a separate cleanup-only wave for V1 display concepts before this lane
- Jobs:
  - `bgjob_attentional_v2_f4a_quality_audit_20260419` (`completed`)
  - `bgjob_attentional_v2_full_window_spotcheck_20260421` (`running`)
  - `bgjob_job_registry_auto_recovery_watchdog_full_window_spotcheck_20260421` (`running`)

### `TASK-ACCUMULATION-BENCHMARK-V2` — Land the target-centered long-span accumulation v2 framework
- Status: `done`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/backend-reader-evaluation.md`
- Next: keep bounded long-span v1 as historical mechanism evidence, and keep `target-centered accumulation v2` as a discontinued / invalidated long-span route whose final April 22 rejudge remains readable only as diagnostic evidence.
  - landed design doc:
    - `reading-companion-backend/docs/evaluation/long_span/target_centered_accumulation_v2_design.md`
  - landed builder / schema:
    - `reading-companion-backend/eval/attentional_v2/accumulation_benchmark_v2.py`
  - landed runner:
    - `reading-companion-backend/eval/attentional_v2/run_accumulation_evaluation_v2.py`
  - archived route contract:
    - one `target_span / target_zone`
    - `2+` upstream nodes plus one explicit `expected_integration`
    - absolute per-mechanism `quality_score` as the main output
    - `callback_score` as a secondary bonus score
    - score only target-visible mechanism behavior:
      - target-local reactions
      - target-proximal callback actions
      - short-horizon followups
    - do not credit `target_span`, `upstream_refs`, or `expected_integration` as mechanism output evidence
    - no direct judging of raw mechanism-specific memory/state structures
    - no pairwise LLM judge prompt
  - archived substrate:
    - reused the repaired active `user-level selective v1` reading windows
  - archived frozen reviewed seed set:
    - unified review / freeze record:
      - `reading-companion-backend/docs/evaluation/long_span/target_centered_candidate_review.md`
    - frozen dataset:
      - `reading-companion-backend/state/eval_local_datasets/accumulation_target_cases/attentional_v2_accumulation_benchmark_v2_cases_frozen`
    - frozen split manifest:
      - `reading-companion-backend/eval/manifests/splits/attentional_v2_accumulation_benchmark_v2_frozen.json`
    - current frozen-set truth:
      - `12` frozen cases
      - `悉达多`: `6`
      - `活出生命的意义`: `4`
      - `芒格之道`: `2`
  - last corrected diagnostic evidence:
    - run id:
      - `attentional_v2_accumulation_benchmark_v2_frozen_rejudge_contract_fix_20260422`
    - summary:
      - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v2_frozen_rejudge_contract_fix_20260422/summary/report.md`
    - audit:
      - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v2_frozen_rejudge_contract_fix_20260422/analysis/longspan_rejudge_audit_20260422/README.md`
    - completed scope:
      - `12` target cases across `3` shared reading windows and `2` mechanisms
    - result under the discontinued route:
      - `attentional_v2 average_quality_score = 2.333`
      - `iterator_v1 average_quality_score = 1.0`
    - reuse posture:
      - completed April 19 normalized reading outputs were reused; no V1/V2 reading was rerun
  - invalidated diagnostic evidence:
    - run id:
      - `attentional_v2_accumulation_benchmark_v2_frozen_active_rerun_20260419`
    - old result:
      - `attentional_v2 average_quality_score = 2.583`
      - `iterator_v1 average_quality_score = 3.083`
    - invalidation reason:
      - the old judge contract could credit target source text itself or pre-target callbacks as if they were target-visible mechanism evidence
  - route-change outcome:
    - this task is now complete as historical implementation work
    - the project no longer treats this route as the active Long Span methodology
    - current active Long Span design authority has moved to:
      - `Memory Quality`
      - `Mechanism Conformance`
      - `Prior Memory Continuity / Safety`
- Jobs:
  - `bgjob_accumulation_benchmark_v2_active_formal_20260419` (`completed`)
  - `bgjob_accumulation_v2_rejudge_contract_fix_20260422` (`completed`)
  - `bgjob_job_registry_auto_recovery_watchdog_longspan_rejudge_20260422` (`completed / stopped`)

### `TASK-LONG-SPAN-MEMORY-DIRECTION-V1` — Design the new Long Span benchmark around memory quality and prior-memory safety
- Status: `active`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/backend-reader-evaluation.md`
- Next: review the completed scale-fixed Phase-1 diagnostic report, then decide whether phase 2 is needed before formal benchmark promotion.
  - landed Phase-1 runner:
    - `reading-companion-backend/eval/attentional_v2/run_long_span_vnext.py`
  - landed `Memory Quality` implementation:
    - benchmark-only V2 probe snapshots during continuous reading
    - probe snapshot capture now hangs off the `attentional_v2` runtime observability layer rather than a direct Reading Runner benchmark call
    - product runs without explicit `memory_quality_probe_export.enabled` plus semantic `probe_targets` do not build probe snapshots
    - standard runtime audit now includes `settlement_audit.jsonl`, a compact deterministic before/after transaction summary for Digest -> Reading Runner settlement
    - current probe placement is semantic-manifest-driven, not hard-ratio-driven
    - settlement-audit diagnostic run `attentional_v2_settlement_audit_nawaer_diagnostic_20260505` completed for `nawaer_baodian_private_zh__segment_1` with `judge-mode none`
    - diagnostic finding: the old concrete reading node did emit memory ops and Runner settlement materialized them, but durable-store field-shape alignment needed repair; the active path now normalizes unit-local source quotes into inline `source_refs[]` before settlement
    - follow-up SourceRef smoke `attentional_v2_source_ref_nawaer_smoke_20260506` exposed a narrower chapter-end issue: `active_attention` source refs could be lost when `chapter_consolidation` returned carry-forward items without refs
    - historical verification job `bgjob_attentional_v2_source_ref_nawaer_active_attention_fix_20260506` completed; because its check contract referenced now-retired structured stores, treat it as historical SourceRef diagnostic context rather than an active current job
  - current probe plan:
    - `reading-companion-backend/eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json`
    - selection method: `semantic_boundary_with_distance_reference`
    - no gold-sentence requirement
    - no hard dependency on human notes
  - landed prior-memory safety audit implementation:
    - grounded prior-memory use
    - weak prior-memory reference
    - prior-memory overclaim guardrail
    - complete-window visible reaction audit over reused normalized outputs; this is not a reward for prior-reference frequency
  - phase-1 scope:
    - `Memory Quality`: `attentional_v2` only
    - reaction audit: `attentional_v2` vs `iterator_v1`
  - current state:
    - phase 1 implementation landed
    - first real Phase-1 run completed, then Memory Quality was rejudged with the corrected `1 low / 5 high` scale:
      - source run id:
        - `attentional_v2_long_span_vnext_phase1_20260423`
      - corrected Memory Quality run id:
        - `attentional_v2_long_span_vnext_phase1_memory_quality_scale_fix_rejudge_20260425`
      - current reaction-evidence rejudge run id:
        - `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
      - post-eval action ledger:
        - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/analysis/post_eval_action_ledger_20260503/README.md`
        - recorded actions now include `A1_legacy_gate_pressure_cleanup`, `A2_active_attention_cutover`, `A3_read_naturalization_cutover`, `A4_memory_quality_structural_signal_supplement`, `A5_local_hypothesis_provenance_cleanup`, `A6_memory_quality_report_contract`, `A7_route_action_contract_cutover`, `A8_forward_settlement_cutover`, `A9_navigate_choose_next_unit_cutover`, `A10_reading_runner_naming_boundary`, `A11_navigate_book_local_skill_runtime`, `A12_navigate_unified_agent_loop_cutover`, and `A13_memory_quality_semantic_probe_plan`
      - Memory Quality evidence report contract:
        - `reading-companion-backend/docs/evaluation/long_span/memory_quality_report_contract.md`
        - future reports should use one full source document per window with probe markers, and label recent route explanations as `route reason` rather than generic `statement`
      - historical Navigator source-skill posture:
        - superseded by `DEC-104` and hard-purged by `DEC-105`
        - `Ingest` is forward-only and does not call source skills
        - the old mechanism-private Skill Runtime is not a current code, prompt, audit, or test interface
      - result:
        - `Memory Quality` average overall score: `3.48`
        - probe count: `25`
        - the April 25 Memory Quality result belongs to the historical hard-ratio probe era; future runs use the semantic probe manifest
        - next Memory Quality judgments will use `scale_v3_structural_signal_aware`, adding structural-signal-aware scoring for salient source-given stage models, classifications, definitions, roadmaps, and named distinctions
        - historical April 25 prior-label results: `attentional_v2` had `152` grounded callbacks and `84` weak callbacks over `1282` visible reactions; `iterator_v1` had `51` grounded callbacks and `13` weak callbacks over `375` visible reactions
        - historical April 25 overclaim/FVI results: `attentional_v2` had `2`; `iterator_v1` had `0`
        - judge unavailable count: `0` for both mechanisms
	    - evidence status:
	      - `quality_audit`
	    - rejudge posture:
	      - no books were reread
	      - Memory Quality judgments were copied from the scale-fixed April 25 run
	      - reaction audit was freshly judged from April 23 completed reading outputs with native V2 surfaced fields visible
	    - no active Long Span vNext background job remains for this run
	    - post-`DEC-110` evaluation boundary:
	      - before any new formal long-span rerun is promoted, verify that Memory Quality rows use Unit Memory and Digest `ReadingMemory` evidence, or explicitly mark incomplete probe evidence
	    - next likely phase-2 line:
	      - `iterator_v1` normalized probe export for cross-mechanism `Memory Quality`
	      - broader formal benchmark promotion
- Jobs:
  - no active Long Span vNext jobs remain for the completed Phase-1 diagnostic run

### `TASK-USER-LEVEL-SELECTIVE-V1` — Replace the active local/user-level benchmark with the note-aligned selective package
- Status: `active`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/backend-reader-evaluation.md`
- Next: keep the active local/user-level pointer on `user-level selective v1` and treat the older `excerpt surface v1.1` line as historical / superseded evidence only.
  - landed builder:
    - `reading-companion-backend/eval/attentional_v2/user_level_selective_v1.py`
  - landed runner:
    - `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
  - active split manifest:
    - `reading-companion-backend/eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json`
  - active dataset package truth:
    - dataset root:
      - `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260629_source_norm_v1_2_unique_notes`
    - `5` reading segments
    - `158` unique note cases
    - `210` raw covered note rows before duplicate folding
    - `52` raw duplicate rows folded into `provenance.duplicate_note_aliases`
    - current active source substrate was rebuilt from fresh isolated parses with Source Normalization v1.2 deterministic-only metadata, then repaired on June 29 so note cases are unique by source span
    - `target_note_count=20` now means unique note cases, not raw exported note rows
    - no active `note_cases.jsonl` rows share the same `(segment_id, source_span_slices)` key
    - `xidaduo_private_zh__segment_1` no longer contains structural footnote definitions such as `Brahmanen`, `Magadha`, `[2]Vishnus`, and `[3]Lakschmi`, while body note references remain visible
    - conservative orphan residue `1《爱经》...` remains body-visible and tracked as follow-up residue rather than excluded without structural proof
    - reading segments start at the first real body unit rather than the absolute beginning of the source file
    - front matter such as disclaimers, recommendation / preface material, book-about-book notes, timeline pages, and part/chapter stubs is skipped before segment construction
    - `nawaer_baodian_private_zh` now uses a benchmark-local body-start override at `c13`, with the active window repaired to `c13-s1 -> c13-s168` and the old preface-side case `e0056` removed
    - every note case now has `segment_source_v1` char-span slices; this is the strict matching coordinate for `Selective Legibility`
  - superseded June 14 source-normalized package:
    - `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260614_source_norm_v1_2`
    - `5` reading segments
    - `202` raw note cases before unique-span dedupe
  - superseded previous active package:
    - `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422`
    - `5` reading segments
    - `202` note cases
  - superseded prior repaired package:
    - `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260416`
    - `5` reading segments
    - `203` note cases
  - superseded historical predecessor:
    - `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1`
    - `5` reading segments
    - `202` note cases
  - latest completed formal evidence bundle before the new rerun:
    - run id:
      - `attentional_v2_user_level_selective_v1_repaired_rejudge_20260416`
  - latest formal-rerun evidence:
    - job id:
      - `bgjob_user_level_selective_v1_active_formal_20260419`
    - run id:
      - `attentional_v2_user_level_selective_v1_active_rerun_20260419`
    - summary:
      - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_user_level_selective_v1_active_rerun_20260419/summary/report.md`
    - completed scope:
      - `5` segments × `2` mechanisms = `10` shard reads
      - `203` note cases
    - result:
      - `attentional_v2 note_recall = 0.3498`
      - `iterator_v1 note_recall = 0.1232`
    - evidence boundary:
      - this formal rerun still used the then-active prior repaired package `attentional_v2_user_level_selective_v1_repaired_20260416`
      - the current active pointer has since moved to `attentional_v2_user_level_selective_v1_repaired_20260629_source_norm_v1_2_unique_notes` with `158` unique note cases; it retains `210` raw covered note rows and folds `52` duplicate rows into provenance aliases
    - April 21 repair note:
      - a shard-filtered recovery command had overwritten the root summary with a partial one-shard aggregate
      - the root summary/report are now regenerated from all completed shards
      - shard-filtered recovery now skips root-level merge/report ownership
- Jobs:
  - `bgjob_user_level_selective_v1_active_formal_20260419` (`completed`)
  - `bgjob_user_level_selective_v1_active_formal_recovery_iter_20260420` (`failed / archived as superseded`)
  - `bgjob_user_level_selective_v1_active_formal_recovery_xidaduo_attn_20260420` (`failed / archived as superseded`)

## Parked

### `TASK-SECOND-READER-READ-PROMPT-XML-FULL-ACTIVE-DIAGNOSTIC-20260526` — Historical diagnostic for old concrete-node XML prompt assembly and Recent Reading Memory
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计11-Read Context Layer Contract v0.md`
- Next: diagnostic completed and remains available as historical evidence, but it is no longer the next implementation driver after `DEC-103`. Do not continue the old concrete-node XML prompt migration or Recent Memory consolidation from this task unless the new ingest/digest feasibility audit explicitly re-adopts a piece of it. Keep this diagnostic out of the evidence catalog until explicit review.
- Jobs:
  - `bgjob_read_prompt_xml_full_diagnostic_20260526_huochu`
  - `bgjob_read_prompt_xml_full_diagnostic_20260526_mangge`
  - `bgjob_read_prompt_xml_full_diagnostic_20260526_nawaer`
  - `bgjob_read_prompt_xml_full_diagnostic_20260526_value_of_others`
  - `bgjob_read_prompt_xml_full_diagnostic_20260526_xidaduo`
  - parent ledger run: `attentional_v2_read_prompt_xml_full_active_diagnostic_20260526`
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ReadPromptXML-Full-Active-Diagnostic-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ReadPromptXML-Full-Active-Diagnostic-Reactions-And-RecentMemory-Full-Review v0.md`
  - `reading-companion-backend/docs/evaluation/run_ledger.md`

### `TASK-SECOND-READER-RECENT-READING-MEMORY-CONSOLIDATION-DESIGN-20260523` — Design Recent Reading Memory consolidation into long-distance memory
- Status: `parked`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- Next: parked by `DEC-103`. Do not continue the Recent Memory -> long-distance-memory consolidation design as the next implementation path. Keep the prior docs as historical/reference material unless a new ingest/digest feasibility audit explicitly re-adopts a slice.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/backend-reading-mechanisms/attentional_v2.md`
  - `docs/backend-reader-evaluation.md`
  - `reading-companion-backend/docs/evaluation/reporting_standard.md`
  - `docs/history/decision-log.md`

### `TASK-SECOND-READER-RECENT-READING-MEMORY-MICRO-DIAGNOSTIC-REVIEW-20260523` — Review Recent Reading Memory micro diagnostics
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Micro-Diagnostic-Huochu-Post-run-Report v0.md`
- Next: parked by `DEC-103`. Keep the micro diagnostics as historical evidence about the paused Recent Reading Memory direction; do not use them as the next prompt/runtime implementation driver unless a new audit explicitly re-adopts the direction.
- Jobs:
  - `bgjob_recent_reading_memory_micro_huochu_20260523` (`completed`)
  - `bgjob_recent_reading_memory_beginning_huochu_20260524` (`completed`)
  - `bgjob_recent_reading_memory_beginning_huochu_20260524_retry1` (`completed`)
  - `bgjob_recent_reading_memory_beginning_huochu_20260524_retry2` (`completed`)
  - `bgjob_recent_reading_memory_beginning_huochu_20260524_retry3` (`completed / superseded prompt direction`)
  - `bgjob_recent_reading_memory_beginning_huochu_20260524_retry4` (`completed / review_pending`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Micro-Diagnostic-Huochu-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Beginning-Micro-Diagnostic-Huochu-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Beginning-Micro-Diagnostic-Huochu-Retry1-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Beginning-Micro-Diagnostic-Huochu-Retry2-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Beginning-Micro-Diagnostic-Huochu-Retry3-Post-run-Report v0.md`
  - `reading-companion-backend/docs/evaluation/run_ledger.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_micro_huochu_20260523/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_micro_huochu_20260523/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry1/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry1/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry2/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry2/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry3/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry3/summary/llm_usage.json`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/RecentReadingMemory-Beginning-Micro-Diagnostic-Huochu-Retry4-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry4/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_recent_reading_memory_beginning_huochu_20260524_retry4/summary/llm_usage.json`

### `TASK-SECOND-READER-READING-IMPRESSION-REACTION-CONTRACT-CLEANUP-20260524` — Revisit `reading_impression` during reaction/Digest-contract tuning
- Status: `parked`
- Lane: `mechanism_runtime`
- Priority: `medium`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- Next: parked by `DEC-103`. Revisit `reading_impression` only inside the new digest / reader-facing note contract design; do not clean it up as a continuation of the paused Recent Memory consolidation track.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
  - `docs/backend-reading-mechanisms/attentional_v2.md`
  - `docs/current-state.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-PROMPT-CONTEXT-DIAGNOSTIC-RETRY1-20260522` — Review ActiveTension lifecycle review for full-window diagnostic Retry1
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Prompt-Context-Grounded-Full-Window-Diagnostic-Retry1-ActiveTension-Lifecycle-Review v0.md`
- Next: parked by `DEC-103`. Keep the completed retry1 diagnostic and lifecycle review as historical diagnostic material only. Do not expand ActiveTension or use this lane as the next mechanism-design direction.
- Jobs:
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_retry1_huochu` (`completed`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_retry1_mangge` (`completed`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_retry1_nawaer` (`completed`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_retry1_value_of_others` (`completed`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_retry1_xidaduo` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Prompt-Context-Grounded-Full-Window-Diagnostic-Retry1-ActiveTension-Lifecycle-Review v0.md`
  - `reading-companion-backend/docs/evaluation/run_ledger.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-PROMPT-CONTEXT-DIAGNOSTIC-REPORT-REVIEW` — Review Active Attention prompt-context full-window diagnostic report
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Prompt-Context-Grounded-Full-Window-Diagnostic-Post-run-Report v0.md`
- Next: parked by `DEC-103`. Preserve the report as historical repair/diagnostic material only; do not continue Active Attention prompt-context work as the next implementation path.
- Jobs:
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_huochu` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_mangge` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_nawaer` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_value_of_others` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_xidaduo` (`failed`, exit `-15`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Prompt-Context-Grounded-Full-Window-Diagnostic-Post-run-Report v0.md`
  - `reading-companion-backend/docs/evaluation/run_ledger.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-FORWARD-PULL-RETRY4-REPORT-REVIEW` — Review Active Attention forward-pull Retry4 report
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Forward-Pull-Micro-Eval-Huochu-Retry4-Post-run-Report v0.md`
- Next: parked by `DEC-103`. Preserve Retry4 as historical evidence about the abandoned Active Attention direction; do not continue this repair lane without a new accepted plan.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521_retry4` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Forward-Pull-Micro-Eval-Huochu-Retry4-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Answered-Reason-Micro-Eval-Huochu-Retry3-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4/analysis/active_attention_lifecycle_audit/README.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-INQUIRY-BOUNDARY-REPAIR-RETRY2-REPORT-REVIEW` — Review Active Attention inquiry-boundary repair Retry2 report
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Inquiry-Boundary-Micro-Eval-Huochu-Retry2-Post-run-Report v0.md`
- Next: parked by `DEC-103`. Preserve Retry2 as historical evidence about the abandoned Active Attention direction; do not continue this repair lane without a new accepted plan.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521_retry2` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Inquiry-Boundary-Micro-Eval-Huochu-Retry2-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry2/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry2/analysis/active_attention_lifecycle_audit/README.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-MICRO-EVAL-RETRY1-REPORT-REVIEW` — Review Active Attention live-question micro eval Retry1 report
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Live-Question-Micro-Eval-Huochu-Retry1-Post-run-Report v0.md`
- Next: parked by `DEC-103`. Preserve Retry1 as historical evidence about the abandoned Active Attention direction; do not continue this repair lane without a new accepted plan.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521_retry1` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Live-Question-Micro-Eval-Huochu-Retry1-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/analysis/active_attention_lifecycle_audit/README.md`

### `TASK-ATTENTIONAL-V2-NARROW-REPAIR-V1` — Run the bounded local-anchor and callback-bridge repair loop on `attentional_v2`
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: the April 7 retry landed new `llm_calls.py` / `prompts.py` / `runner.py` behavior plus the long-span harness support in `run_accumulation_comparison.py`, and the targeted tests all passed. The repair gate run on `attentional_v2_excerpt_micro_slice_v1_smoke_excerpt_repair_laneA_retry1_20260407` finished cleanly, but its judged stage regressed against the April 5 micro-slice baseline. Keep the known misses explicit, but do not reopen this repair lane by default while the product/demo decision is using the completed excerpt formal run as good-enough evidence and long-span smoke is the active priority.
- Jobs: none

### `TASK-RUNTIME-VIABILITY-GATES` — Keep runtime viability and non-mainline comparison lanes paused under the reduced eval scope
- Status: `parked`
- Lane: `mechanism_eval`
- Priority: `medium`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: reuse the existing runtime-viability and durable-trace evidence; do not relaunch those lanes unless one of the three kept north-star dimensions later requires them or the cost posture changes explicitly
- Jobs:
  - `bgjob_durable_trace_reentry_gate_20260401` (`failed`)
  - `bgjob_durable_trace_reentry_gate_parallel3_20260401` (`completed`)
  - `bgjob_durable_trace_reentry_gate_personal_serial_20260401` (`abandoned`)
  - `bgjob_runtime_viability_gate_20260401` (`completed`)
  - `bgjob_runtime_viability_gate_serialfix_20260401` (`completed`)

## Cancelled

### `TASK-SECOND-READER-MEMORY-PLANNING-EVAL1-FULL-ACTIVE-EVALUATION` — Run post-Slice8H full active evaluation for `attentional_v2`
- Status: `cancelled`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Aborted-Run-Report v0.md`
- Next: Eval-1 was stopped before completion after LLM-health investigation showed that partial Long Span producer progress included runtime fallback during `network_blocked` / `llm_timeout` failures and no summary outputs were produced. Do not reuse partial outputs, launch Lane A reuse shards, update the evidence catalog, promote Long Span vNext, or claim product quality. Any retry requires a separate accepted brief or patch plan for LLM-health / fallback guardrails plus fresh run ids.
- Jobs:
  - `bgjob_full_user_level_selective_post_slice8h_20260518` (`abandoned`)
  - `bgjob_full_long_span_vnext_post_slice8h_20260518` (`abandoned`)
  - `bgjob_full_long_span_vnext_post_slice8h_20260518_parallel5` (`abandoned`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Aborted-Run-Report v0.md`
  - `reading-companion-backend/state/job_registry/jobs/bgjob_full_user_level_selective_post_slice8h_20260518.json`
  - `reading-companion-backend/state/job_registry/jobs/bgjob_full_long_span_vnext_post_slice8h_20260518.json`
  - `reading-companion-backend/state/job_registry/jobs/bgjob_full_long_span_vnext_post_slice8h_20260518_parallel5.json`
  - `reading-companion-backend/state/job_registry/logs/bgjob_full_long_span_vnext_post_slice8h_20260518_parallel5.log`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_full_long_span_vnext_post_slice8h_20260518_parallel5/meta/selected_windows.json`

## Waiting

### `TASK-SECOND-READER-MEMORY-PLANNING-EVAL1-RETRY1-HIGH-PARALLEL-REPORT-REVIEW` — Review Eval-1 Retry1 high-parallel full active evaluation report
- Status: `waiting`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md`
- Next: review the completed Eval-1 Retry1 high-parallel full active evaluation. Do not update the evidence catalog, promote Long Span vNext, launch broader eval, or claim product quality before human review.
- Jobs: none
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/aggregate.json`

## Done

### `TASK-SECOND-READER-RECENT-READING-MEMORY-DESIGN-20260523` — Design and implement first-half Recent Reading Memory formation
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
- Next: first-half formation is implemented and tested, but the follow-up consolidation task is now parked by `DEC-103`. Do not continue this as the next mechanism path unless the new ingest/digest feasibility audit explicitly re-adopts a slice.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/C设计10-Recent Reading Memory Design v0.md`
  - `docs/backend-reading-mechanisms/attentional_v2.md`
  - `docs/backend-reader-evaluation.md`
  - `reading-companion-backend/docs/evaluation/reporting_standard.md`
  - `docs/history/decision-log.md`
  - `reading-companion-backend/src/attentional_v2/schemas.py`
  - `reading-companion-backend/src/attentional_v2/prompts.py`
  - `reading-companion-backend/src/attentional_v2/state_ops.py`
  - `reading-companion-backend/src/attentional_v2/state_projection.py`
  - `reading-companion-backend/src/attentional_v2/runner.py`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-PROMPT-CONTEXT-DIAGNOSTIC-20260522` — Implement Active Attention prompt-context grounding repair and attempt five-window diagnostic
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Prompt-Context-Grounded-Full-Window-Diagnostic-Post-run-Report v0.md`
- Next: implementation and diagnostic attempt are recorded in `TASK-SECOND-READER-ACTIVE-ATTENTION-PROMPT-CONTEXT-DIAGNOSTIC-REPORT-REVIEW`. Treat the five-window diagnostic as invalidated because all shards were manually terminated before terminal summaries; do not treat partial traces as behavior evidence or catalog input.
- Jobs:
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_huochu` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_mangge` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_nawaer` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_value_of_others` (`failed`, exit `-15`)
  - `bgjob_active_attention_prompt_context_window_diagnostic_20260522_xidaduo` (`failed`, exit `-15`)
- Evidence:
  - `docs/backend-reading-mechanisms/attentional_v2.md`
  - `docs/backend-reader-evaluation.md`
  - `docs/history/decision-log.md`
  - `reading-companion-backend/docs/evaluation/reporting_standard.md`
  - `reading-companion-backend/docs/evaluation/run_ledger.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Prompt-Context-Grounded-Full-Window-Diagnostic-Post-run-Report v0.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-FORWARD-PULL-RETRY4-20260521` — Implement Active Attention source-grounding / forward-pull repair and run Retry4 micro eval on `huochu`
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Forward-Pull-Micro-Eval-Huochu-Retry4-Post-run-Report v0.md`
- Next: Retry4 diagnostic execution is complete and recorded in `TASK-SECOND-READER-ACTIVE-ATTENTION-FORWARD-PULL-RETRY4-REPORT-REVIEW`. Treat the result as mixed diagnostic evidence: source grounding improved, but Active Attention can still over-import book-level themes. Do not treat it as cataloged evidence, product-quality proof, or authorization for broader eval.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521_retry4` (`completed`)
- Evidence:
  - `reading-companion-backend/docs/evaluation/run_ledger.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Forward-Pull-Micro-Eval-Huochu-Retry4-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry4/analysis/active_attention_lifecycle_audit/README.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-ANSWERED-REASON-RETRY3-20260521` — Implement Active Attention answered-reason repair and run Retry3 micro eval on `huochu`
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Answered-Reason-Micro-Eval-Huochu-Retry3-Post-run-Report v0.md`
- Next: Retry3 diagnostic execution is complete and is now supporting evidence for Retry4 review. The result was partial-positive: live-inquiry creation/update/answered lifecycle worked, while source grounding still had fallback caveats and close/downstream lineage were not exercised.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521_retry3` (`completed`)
- Evidence:
  - `reading-companion-backend/docs/evaluation/run_ledger.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Answered-Reason-Micro-Eval-Huochu-Retry3-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry3/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry3/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry3/analysis/active_attention_lifecycle_audit/README.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-INQUIRY-BOUNDARY-REPAIR-RETRY2-20260521` — Implement Active Attention inquiry-boundary repair and run Retry2 micro eval on `huochu`
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Inquiry-Boundary-Micro-Eval-Huochu-Retry2-Post-run-Report v0.md`
- Next: Retry2 diagnostic execution is complete and recorded in `TASK-SECOND-READER-ACTIVE-ATTENTION-INQUIRY-BOUNDARY-REPAIR-RETRY2-REPORT-REVIEW`. The result is partial-positive diagnostic evidence: the `answer_boundary` contract is wired, but answer-boundary satisfaction still needs human review before any next repair. Do not treat it as cataloged evidence, product-quality proof, or authorization for broader eval.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521_retry2` (`completed`)
- Evidence:
  - `reading-companion-backend/docs/evaluation/run_ledger.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Inquiry-Boundary-Micro-Eval-Huochu-Retry2-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry2/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry2/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry2/analysis/active_attention_lifecycle_audit/README.md`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-MICRO-EVAL-20260521` — Run Active Attention live-question diagnostic micro eval on `huochu`
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Live-Question-Micro-Eval-Huochu-Post-run-Report v0.md`
- Next: diagnostic execution is complete and recorded in `TASK-SECOND-READER-ACTIVE-ATTENTION-MICRO-EVAL-REPORT-REVIEW`. The result is a useful failure case for Active Attention live-question behavior; do not treat it as cataloged evidence, product-quality proof, or authorization for broader eval.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521` (`completed`)
- Evidence:
  - `reading-companion-backend/docs/evaluation/run_ledger.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521/summary/llm_usage.json`

### `TASK-SECOND-READER-ACTIVE-ATTENTION-MICRO-EVAL-RETRY1-20260521` — Run Active Attention reader-native prompt repair Retry1 micro eval on `huochu`
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/ActiveAttention-Live-Question-Micro-Eval-Huochu-Retry1-Post-run-Report v0.md`
- Next: Retry1 diagnostic execution is complete and recorded in `TASK-SECOND-READER-ACTIVE-ATTENTION-MICRO-EVAL-RETRY1-REPORT-REVIEW`. The result is positive diagnostic evidence for the targeted Active Attention live-question behavior; do not treat it as cataloged evidence, product-quality proof, or authorization for broader eval.
- Jobs:
  - `bgjob_active_attention_live_question_micro_huochu_20260521_retry1` (`completed`)
- Evidence:
  - `reading-companion-backend/docs/evaluation/run_ledger.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_attention_live_question_micro_huochu_20260521_retry1/analysis/active_attention_lifecycle_audit/README.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-EVAL1-RETRY1-HIGH-PARALLEL` — Run Eval-1 Retry1 high-parallel full active evaluation for `attentional_v2`
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md`
- Next: Eval-1 Retry1 completed all 5 active Long Span semantic-probe windows and all 5 Lane A user-level reuse shards for `attentional_v2`. Results are pending human review; no evidence catalog update, Long Span formal-authority promotion, broader eval, or product-quality claim is authorized.
- Jobs:
  - `bgjob_eval1_long_span_post_slice8h_20260519_huochu` (`completed`)
  - `bgjob_eval1_long_span_post_slice8h_20260519_mangge` (`completed`)
  - `bgjob_eval1_long_span_post_slice8h_20260519_nawaer` (`completed`)
  - `bgjob_eval1_long_span_post_slice8h_20260519_value_of_others` (`completed`)
  - `bgjob_eval1_long_span_post_slice8h_20260519_xidaduo` (`completed`)
  - `bgjob_eval1_user_level_post_slice8h_20260519_reuse_huochu` (`completed`)
  - `bgjob_eval1_user_level_post_slice8h_20260519_reuse_mangge` (`completed`)
  - `bgjob_eval1_user_level_post_slice8h_20260519_reuse_nawaer` (`completed`)
  - `bgjob_eval1_user_level_post_slice8h_20260519_reuse_value_of_others` (`completed`)
  - `bgjob_eval1_user_level_post_slice8h_20260519_reuse_xidaduo` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-EVAL1-LLM-HEALTH-REPAIR-REPORT-REVIEW` — Review Eval-1 LLM health and eval strictness repair report
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-LLM-Health-and-Eval-Strictness-Repair-Post-implementation-Report v0.md`
- Next: repair accepted and used by Eval-1 Retry1. Keep strict eval health gates, live target preflight, and same-tier failover in force for future eval runs.
- Jobs: none
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-LLM-Health-and-Eval-Strictness-Repair-Post-implementation-Report v0.md`
  - `reading-companion-backend/eval/attentional_v2/llm_health.py`
  - `reading-companion-backend/scripts/check_llm_targets_live.py`
  - `reading-companion-backend/scripts/check_eval_llm_health.py`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8H-REPORT-REVIEW` — Review Slice 8H Diagnostic Evidence Catalog Entry Report
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`
- Next: Slice 8H Post-implementation Report is accepted. The Memory / Planning / Minimal Eval implementation track is closed after Slice 8H. The completed Slice 8C through Slice 8G Minimal Eval Suite smoke is cataloged as `diagnostic_smoke` only; any broader eval, formal-authority promotion, runtime patch, further catalog entry, or product-quality claim requires a separate future brief.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517` (`failed`)
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1` (`completed`)
  - `bgjob_minimal_eval_suite_lane_b_smoke_20260517` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`
  - `reading-companion-backend/docs/evaluation/evidence_catalog.md`
  - `reading-companion-backend/docs/evaluation/evidence_catalog.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/report.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/report.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/meta/output_sourcing.json`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-DATASET-QUESTION-ALIGNED-CASE-CONSTRUCTION` — Build question-aligned case construction for evaluation datasets
- Status: `waiting`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: keep the landed builder available as support infrastructure, but do not open a new general builder wave by default now that the current decisive eval lanes are resolved; broader construction should resume only if later regression work exposes a concrete blocker or if one explicitly scoped audit-stage-only reproducibility pass is requested
- Jobs:
  - `bgjob_closed_loop_en_broader_callbackpromptfix_20260331` (`completed`)
  - `bgjob_closed_loop_zh_callbacklookback_20260330` (`completed`)
  - `bgjob_closed_loop_zh_callbackpriorcontext_20260330` (`completed`)
  - `bgjob_closed_loop_zh_cueguard_20260330` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackbridgefix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackcontentfix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackinferencefix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackfocusfix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_tensionfocusfix_20260331` (`completed`)
  - `bgjob_callbackslice_auditv4_packet_20260331` (`failed`)
  - `bgjob_callbackslice_auditv4_packet_retry_quota_20260331` (`completed`)
  - `bgjob_callbackslice_probeonly_20260331` (`completed`)
  - `bgjob_callbackslice_auditrerun_20260331` (`completed`)

### `TASK-DATASET-FULL-AUTOMATION` — Make dataset building fully automated as one closed build-review-refine loop
- Status: `waiting`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: keep the bounded controller scratch-safe and reusable, but do not widen automation by default now that the current decisive mechanism-eval lane is closed; with current model cost pressure, do not spend on non-mainline comparison support loops unless later work needs one explicitly scoped audit-stage-only reproducibility pass or another concrete support-lane unblocker
- Jobs:
  - `bgjob_closed_loop_en_broader_callbackpromptfix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackpromptfix_20260331` (`failed`)
  - `bgjob_callbackslice_auditv4_packet_20260331` (`failed`)
  - `bgjob_callbackslice_auditv4_packet_retry_quota_20260331` (`completed`)
  - `bgjob_callbackslice_probeonly_20260331` (`completed`)
  - `bgjob_callbackslice_auditrerun_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackfocusfix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_tensionfocusfix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackinferencefix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackcontentfix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_callbackbridgefix_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_whitespacefix_20260331` (`completed`)
  - `bgjob_closed_loop_en_broader_whitespacefix_20260331` (`completed`)
  - `bgjob_closed_loop_en_henry_whitespacefix_20260331` (`completed`)
  - `bgjob_closed_loop_en_broader_auditconsensusv3_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_auditconsensusv3_20260331` (`completed`)
  - `bgjob_closed_loop_en_broader_auditcontractv3_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_auditcontractv3_20260331` (`completed`)
  - `bgjob_closed_loop_en_broader_auditcontractv2_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_auditcontractv2_20260331` (`completed`)
  - `bgjob_closed_loop_en_broader_auditpair_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_auditpair_20260331` (`completed`)
  - `bgjob_closed_loop_en_broader_adjudicationv4_20260331` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_adjudicationv4_20260331` (`completed`)
  - `bgjob_closed_loop_en_broader_compactadjudication_20260330` (`completed`)
  - `bgjob_closed_loop_en_broader_compactadjudication_repeat_20260330` (`failed`)
  - `bgjob_closed_loop_en_broader_compactadjudication_repeat_resume_20260330` (`completed`)
  - `bgjob_packet_adjudication_probe_en_compactrepeat_20260330` (`completed`)
  - `bgjob_packet_adjudication_probe_en_compactrepeat_compactauditv2_20260330` (`completed`)
  - `bgjob_closed_loop_en_broader_auditsemanticretry_20260330` (`completed`)
  - `bgjob_closed_loop_en_broader_auditcoherencefix_repeat_20260330` (`completed`)
  - `bgjob_closed_loop_bilingual_broader_auditcoherencefix_20260330` (`completed`)

## Queued

### `TASK-FE-SECTION-RETIREMENT` — Retire section-first chapter/detail and marks surfaces
- Status: `queued`
- Lane: `migration`
- Priority: `medium`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Blocked by: `TASK-V2-NATIVE-READING-PRESENTATION`
- Next: keep section-first compatibility fields and containers only as migration sidecars; start removal only after the V2-native overview, chapter, and marks surfaces are stable enough that the older presentation model is no longer needed for normal product use
### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8H-BRIEF-ACCEPTANCE` — Review Slice 8H Diagnostic Evidence Catalog Entry Brief
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`
- Next: Slice 8H Pre-implementation Brief is accepted. Slice 8H catalog entry implementation has landed and is recorded in `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8H-REPORT-REVIEW`; do not run eval, promote Long Span vNext, add further catalog entries, or claim product quality until the Slice 8H report is reviewed.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517` (`failed`)
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1` (`completed`)
  - `bgjob_minimal_eval_suite_lane_b_smoke_20260517` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`
  - `reading-companion-backend/docs/evaluation/evidence_catalog.md`
  - `reading-companion-backend/docs/evaluation/evidence_catalog.json`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8G-REPORT-REVIEW` — Review Slice 8G Minimal Eval Suite Smoke Closure Report
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`
- Next: Slice 8G Minimal Eval Suite smoke closure report is accepted. Slice 8H diagnostic evidence catalog entry brief is pending review; do not update the evidence catalog, promote Long Span vNext, run broader eval, or start another eval slice until the Slice 8H brief is reviewed.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517` (`failed`)
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1` (`completed`)
  - `bgjob_minimal_eval_suite_lane_b_smoke_20260517` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8G-Minimal-Eval-Suite-Smoke-Closure-and-Evidence-Interpretation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8H-Diagnostic-Evidence-Catalog-Entry-for-Minimal-Eval-Suite-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8F-REPORT-REVIEW` — Review Slice 8F Post-run Report for Lane B Bounded Diagnostic Smoke
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
- Next: Slice 8F Post-run Report is accepted. Minimal Eval Suite smoke closure and evidence interpretation has landed and is recorded in `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8G-REPORT-REVIEW`; do not update the evidence catalog, promote Long Span vNext, run broader eval, or start another eval slice until the Slice 8G report is reviewed.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_b_smoke_20260517` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8F-Lane-B-Bounded-Diagnostic-Smoke-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/report.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/summary/llm_usage.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_b_smoke_20260517/meta/output_sourcing.json`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8E-REPORT-REVIEW` — Review Slice 8E Post-run Report for Lane A `_retry1` Bounded Execution
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
- Next: Slice 8E Post-run Report is accepted. Lane B bounded diagnostic smoke is accepted, and the smoke closure report is recorded in `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8G-REPORT-REVIEW`; do not update the evidence catalog, promote Long Span vNext, or start another eval slice until the Slice 8G report is reviewed.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517_retry1` (`completed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8E-Lane-A-Retry1-Bounded-Execution-Post-run-Report v0.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/report.md`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_minimal_eval_suite_lane_a_smoke_20260517_retry1/summary/llm_usage.json`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8D-REPORT-REVIEW` — Review Slice 8D Post-implementation Report for Lane A Source-locator Compatibility Triage and Minimal Patch
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
- Next: Slice 8D Post-implementation Report is accepted. Lane A `_retry1` and Lane B bounded diagnostic smoke are accepted, and the smoke closure report is recorded in `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8G-REPORT-REVIEW`; do not update the evidence catalog or start another eval slice until the Slice 8G report is reviewed.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517` (`failed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8D-Lane-A-Source-locator-Compatibility-Triage-and-Minimal-Patch-Post-implementation-Report v0.md`
  - `reading-companion-backend/eval/attentional_v2/run_user_level_selective_comparison.py`
  - `reading-companion-backend/tests/test_run_user_level_selective_comparison.py`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8C-REPORT-REVIEW` — Review Slice 8C Post-implementation Report for Minimal Eval Suite Execution Preflight and Bounded Run
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
- Next: Slice 8C Post-implementation Report is accepted as failed execution evidence. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8D-REPORT-REVIEW`; do not retry Lane A, launch Lane B, update the evidence catalog, or start another eval slice until the Slice 8D patch report is reviewed.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517` (`failed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8C-BRIEF-ACCEPTANCE` — Review Slice 8C Pre-implementation Brief for Minimal Eval Suite Execution Preflight and Bounded Run
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
- Next: Slice 8C Pre-implementation Brief is accepted, bounded execution was attempted, Lane A failed before summary generation after the fresh V2 read completed, Lane B was not launched, and the Slice 8C report is accepted as failed execution evidence. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8D-REPORT-REVIEW`; do not retry Lane A, launch Lane B, update the evidence catalog, or start another eval slice until the Slice 8D report is reviewed.
- Jobs:
  - `bgjob_minimal_eval_suite_lane_a_smoke_20260517` (`failed`)
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8B-BRIEF-ACCEPTANCE` — Review Slice 8B Pre-implementation Brief for Minimal Eval Suite Run Brief and Execution Guardrails
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
- Next: Slice 8B Pre-implementation Brief is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8C-BRIEF-ACCEPTANCE`; do not run eval before the Slice 8C execution brief is accepted and execution is explicitly requested.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8C-Minimal-Eval-Suite-Execution-Preflight-and-Bounded-Run-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8A-REPORT-REVIEW` — Review Slice 8A Post-implementation Report for Post-implementation Review and Minimal Eval Readiness Gate
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
- Next: Slice 8A Post-implementation Report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8B-BRIEF-ACCEPTANCE`; do not run eval before the Slice 8B run brief and a later execution slice are accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8B-Minimal-Eval-Suite-Run-Brief-and-Execution-Guardrails-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8A-BRIEF-ACCEPTANCE` — Review Slice 8A Pre-implementation Brief for Post-implementation Review and Minimal Eval Readiness Gate
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
- Next: Slice 8A Pre-implementation Brief is accepted, the doc-only readiness gate has landed, and the Slice 8A report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8B-BRIEF-ACCEPTANCE`; do not run eval before the Slice 8B run brief and a later execution slice are accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7B-REPORT-REVIEW` — Review Slice 7B Post-implementation Report for Minimal Eval Smoke Harness and Evidence Availability Validation
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
- Next: Slice 7B Post-implementation Report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE8A-BRIEF-ACCEPTANCE`; do not run eval before the Slice 8A readiness gate and later eval-run brief are accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice8A-Post-implementation-Review-and-Minimal-Eval-Readiness-Gate-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7B-BRIEF-ACCEPTANCE` — Review Slice 7B Pre-implementation Brief for Minimal Eval Smoke Harness and Evidence Availability Validation
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
- Next: Slice 7B Pre-implementation Brief is accepted and implemented. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7B-REPORT-REVIEW`; do not start the next eval slice or run eval before the Slice 7B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7A-REPORT-REVIEW` — Review Slice 7A Post-implementation Report for Minimal Eval Asset Inventory and Evidence Wiring
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
- Next: Slice 7A Post-implementation Report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7B-BRIEF-ACCEPTANCE`; do not start Slice 7B implementation or run eval before the Slice 7B Pre-implementation Brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7B-Minimal-Eval-Smoke-Harness-and-Evidence-Availability-Validation-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7A-BRIEF-ACCEPTANCE` — Review Slice 7A Pre-implementation Brief for Minimal Eval Asset Inventory and Evidence Wiring
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
- Next: Slice 7A Pre-implementation Brief is accepted and implemented. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7A-REPORT-REVIEW`; do not start Slice 7B or run eval before the Slice 7A Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6B-BRIEF-ACCEPTANCE` — Review Slice 6B Pre-implementation Brief for Slow-cycle Re-entry, Reconsolidation, and Eval-readiness Smoke
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
- Next: Slice 6B no-code closure brief is accepted and Slice 6 is closed. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE7A-BRIEF-ACCEPTANCE`; do not start eval implementation or run evaluation before the Slice 7A brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice7A-Minimal-Eval-Asset-Inventory-and-Evidence-Wiring-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6A-PATCH-REPORT-REVIEW` — Review Slice 6A patch report for Carry-forward Settled SourceRef Evidence Precision
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
- Next: Slice 6A patch report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6B-BRIEF-ACCEPTANCE`; do not start Slice 7 / Minimal Eval Implementation before the Slice 6B closure brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6B-Slow-cycle-Re-entry-Reconsolidation-and-Eval-readiness-Smoke-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6A-REPORT-REVIEW` — Review Slice 6A Post-implementation Report for Slow-cycle Candidate and Settlement Audit Envelope Foundations
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
- Next: Slice 6A Post-implementation Report was reviewed; implementation direction accepted with a required carried SourceRef audit precision patch. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6A-PATCH-REPORT-REVIEW`; do not start the next implementation slice before the Slice 6A patch report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Patch-Carry-forward-Settled-SourceRef-Evidence-Precision-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6A-BRIEF-ACCEPTANCE` — Review Slice 6A Pre-implementation Brief for Slow-cycle Candidate and Settlement Audit Envelope Foundations
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
- Next: Slice 6A Pre-implementation Brief is accepted and implemented, and the Slice 6A Post-implementation Report has been reviewed with a required patch. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6A-PATCH-REPORT-REVIEW`; do not start the next implementation slice before the Slice 6A patch report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5B-REPORT-REVIEW` — Review Slice 5B Post-implementation Report for Planning Support Signals and Detour Value-Cost Audit Markers
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`
- Next: Slice 5B Post-implementation Report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE6A-BRIEF-ACCEPTANCE`; do not start Slice 6A implementation before the Slice 6A Pre-implementation Brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice6A-Slow-cycle-Candidate-and-Settlement-Audit-Envelope-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5B-BRIEF-ACCEPTANCE` — Review Slice 5B Pre-implementation Brief for Planning Support Signals and Detour Value-Cost Audit Markers
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
- Next: Slice 5B Pre-implementation Brief is accepted and implemented. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 5B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5A-REPORT-REVIEW` — Review Slice 5A Post-implementation Report for Detour Lifecycle and Navigation Trace Audit Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
- Next: Slice 5A Post-implementation Report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5B-BRIEF-ACCEPTANCE`; do not start Slice 5B implementation before the Slice 5B Pre-implementation Brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5B-Planning-Support-Signals-and-Detour-Value-Cost-Audit-Markers-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5A-BRIEF-ACCEPTANCE` — Review Slice 5A Pre-implementation Brief for Detour Lifecycle and Navigation Trace Audit Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
- Next: Slice 5A Pre-implementation Brief is accepted and implemented. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5A-REPORT-REVIEW`; do not start the next implementation slice before the Slice 5A Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4B-REPORT-REVIEW` — Review Slice 4B Post-implementation Report for Retrieval Utilization Trace and Read-audit Evidence
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
- Next: Slice 4B Post-implementation Report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE5A-BRIEF-ACCEPTANCE`; do not start Slice 5A implementation before the Slice 5A Pre-implementation Brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice5A-Detour-Lifecycle-and-Navigation-Trace-Audit-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4B-BRIEF-ACCEPTANCE` — Review Slice 4B Pre-implementation Brief for Retrieval Utilization Trace and Read-audit Evidence
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
- Next: Slice 4B Pre-implementation Brief is accepted and implemented. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 4B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4A-PATCH-REPORT-REVIEW` — Review Slice 4A precision patch report for result groups and forwarding metadata
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
- Next: Slice 4A precision patch report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4B-BRIEF-ACCEPTANCE`; do not start Slice 4B implementation before the Slice 4B Pre-implementation Brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice4B-Retrieval-Utilization-Trace-and-Read-audit-Evidence-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4A-REPORT-REVIEW` — Review Slice 4A Post-implementation Report for Supplemental Retrieval Intent and Context Assembly Contract
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
- Next: Slice 4A implementation direction is accepted with a required precision patch. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4A-PATCH-REPORT-REVIEW`; do not start Slice 4B before the Slice 4A patch report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Patch-Precise-Result-Groups-and-Forwarding-Metadata-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4A-BRIEF-ACCEPTANCE` — Review Slice 4A Pre-implementation Brief for Supplemental Retrieval Intent and Context Assembly Contract
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
- Next: Slice 4A Pre-implementation Brief is accepted and implemented. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4A-REPORT-REVIEW`; do not start the next implementation slice before the Slice 4A Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW` — Review Slice 3B Post-implementation Report for Lifecycle Semantics and State-op Boundary Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
- Next: Slice 3B Post-implementation Report is accepted. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE4A-BRIEF-ACCEPTANCE`; do not start Slice 4A implementation before the Slice 4A Pre-implementation Brief is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice4A-Supplemental-Retrieval-Intent-and-Context-Assembly-Contract-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-BRIEF-ACCEPTANCE` — Review Slice 3B Pre-implementation Brief for Lifecycle Semantics and State-op Boundary Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3A-REPORT-REVIEW` — Review Slice 3A Post-implementation Report for Status-aware Projection and Boundary Marker Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3B-Lifecycle-Semantics-and-State-op-Boundary-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3A-BRIEF-ACCEPTANCE` — Review Slice 3A Pre-implementation Brief for Status-aware Projection and Boundary Marker Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE2B-REPORT-REVIEW` — Review Slice 2B Post-implementation Report for Store-specific Admission and Target-store Policy Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice3A-Status-aware-Projection-and-Boundary-Marker-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE2B-BRIEF-ACCEPTANCE` — Review Slice 2B Pre-implementation Brief for Store-specific Admission and Target-store Policy Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE2A-REPORT-REVIEW` — Review Slice 2A Post-implementation Report for Operation Vocabulary and Admission Visibility Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2B-Store-specific-Admission-and-Target-store-Policy-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE2A-BRIEF-ACCEPTANCE` — Review Slice 2A Pre-implementation Brief for Operation Vocabulary and Admission Visibility Hardening
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE1-REPORT-REVIEW` — Review Slice 1 Post-implementation Report for Contract and Audit Foundations
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice2A-Operation-Vocabulary-and-Admission-Visibility-Hardening-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-SLICE1-BRIEF-ACCEPTANCE` — Review Slice 1 Pre-implementation Brief for Contract and Audit Foundations
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Slice1-Contract-Audit-Foundations-Post-implementation-Report v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-SECOND-READER-MEMORY-PLANNING-FEASIBILITY-AUDIT` — Run Implementation Feasibility & Delta Audit for Second Reader Memory-Planning optimization
- Status: `done`
- Lane: `mechanism_runtime`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
- Next: Slice 3B Pre-implementation Brief is accepted and implemented, and the Slice 3B Post-implementation Report is pending review. Continue with `TASK-SECOND-READER-MEMORY-PLANNING-SLICE3B-REPORT-REVIEW`; do not start the next implementation slice before the Slice 3B Post-implementation Report is accepted.
- Evidence:
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/README.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/E实施0-Implementation Roadmap & Handoff v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施1-Implementation Feasibility & Delta Audit v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/briefs/Slice1-Contract-Audit-Foundations-Pre-implementation-Brief v0.md`
  - `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/E实施-progress-ledger.md`

### `TASK-ACTIVE-BENCHMARK-FORMAL-RERUN` — Run the formal active V1/V2 benchmark rerun across excerpt and long-span surfaces
- Status: `done`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/backend-reader-evaluation.md`
- Next: keep the April 19 formal rerun as the current active benchmark evidence bundle for excerpt only; do not relaunch by default unless a new mechanism or dataset change requires fresh evidence.
  - parent run:
    - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_active_benchmark_rerun_20260419/summary/report.md`
  - excerpt child:
    - run id: `attentional_v2_user_level_selective_v1_active_rerun_20260419`
    - scope: `203` note cases across `5` reading windows and `2` mechanisms
    - result: `attentional_v2 note_recall = 0.3498`; `iterator_v1 note_recall = 0.1232`
  - long-span child:
    - run id: `attentional_v2_accumulation_benchmark_v2_frozen_active_rerun_20260419`
    - scope: `12` target cases across `3` windows and `2` mechanisms
    - result: `attentional_v2 average_quality_score = 2.583`; `iterator_v1 average_quality_score = 3.083`
    - status: discontinued / invalidated diagnostic evidence because the judge contract credited non-target-visible evidence
  - preserved long-span rejudge for the discontinued route:
    - run id: `attentional_v2_accumulation_benchmark_v2_frozen_rejudge_contract_fix_20260422`
    - scope: `12` target cases across `3` windows and `2` mechanisms
    - result: `attentional_v2 average_quality_score = 2.333`; `iterator_v1 average_quality_score = 1.0`
    - posture: rejudge-only; no reading rerun
    - status: discontinued / invalidated diagnostic evidence after the Long Span route change
  - April 21 repair note:
    - all shard outputs were complete, but a shard-filtered recovery invocation had overwritten the excerpt root summary with a partial one-shard aggregate
    - the root summary/report were regenerated from all completed shards
    - shard-filtered recovery now skips root-level merge/report so this partial-summary overwrite cannot recur
    - the parent orchestrator now validates complete child outputs before treating terminal child status as fatal
- Jobs:
  - `bgjob_active_benchmark_rerun_20260419` (`completed`)
  - `bgjob_user_level_selective_v1_active_formal_20260419` (`completed`)
  - `bgjob_accumulation_benchmark_v2_active_formal_20260419` (`completed`)
  - `bgjob_job_registry_auto_recovery_watchdog_active_benchmark_20260419` (`completed / stopped`)
  - `bgjob_user_level_selective_v1_active_formal_recovery_iter_20260420` (`failed / archived as superseded`)
  - `bgjob_user_level_selective_v1_active_formal_recovery_xidaduo_attn_20260420` (`failed / archived as superseded`)

### `TASK-ACCUMULATION-BENCHMARK-V1` — Build the bounded long-span window benchmark for `coherent_accumulation`
- Status: `done`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: keep `attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407` as the durable long-span evidence bundle, treat the April 6 lane as diagnosed invalid harness evidence rather than mechanism evidence, and reopen long-span repair only if a future rerun reproduces bundle/probe materialization failure or schema-invalid judge collapse.
- Jobs:
  - `bgjob_accumulation_benchmark_v1_first_review_20260404` (`completed`)
  - `bgjob_accumulation_benchmark_v1_rejudged_first_review_20260404` (`completed`)
  - `bgjob_accumulation_benchmark_v1_repair_first_review_20260405` (`completed`)
  - `bgjob_accumulation_benchmark_v1_judged_20260406` (`completed`)
  - `bgjob_accumulation_smoke_pair_recovery_20260407` (`completed`)
  - `bgjob_accumulation_benchmark_v1_judged_rerun_20260407` (`completed`)
  - `bgjob_accumulation_value_of_others_iterator_v1_bundle_20260408` (`completed`)
  - `bgjob_accumulation_benchmark_v1_value_of_others_iterator_v1_recovery_20260408` (`completed`)

### `TASK-PHASE9-DECISIVE-EVAL` — Run the split-surface Phase 9 evaluation lanes
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: keep `excerpt surface v1.1` as the current durable excerpt evidence bundle, keep the cleaned long-span rerun as the durable long-span evidence bundle, and do not reopen decisive eval reruns by default unless a later product question or regression reproduces a concrete blocker.
- Jobs:
  - `bgjob_human_notes_excerpt_smoke_light_20260404` (`completed`)
  - `bgjob_human_notes_guided_excerpt_eval_v1_judged_20260404` (`completed`)
  - `bgjob_human_notes_guided_excerpt_eval_v1_judged_personal_rerun_20260405` (`abandoned`)
  - `bgjob_human_notes_excerpt_parallel_smoke_20260405` (`abandoned`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_a_20260405` (`failed`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_b_20260405` (`failed`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_a_retry1_20260405` (`failed`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_b_retry1_20260405` (`failed`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_a_dualpool_recovery_20260405` (`failed`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_b_dualpool_recovery_20260405` (`failed`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_a_dualpool_recovery_retry2_20260405` (`abandoned`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_b_dualpool_recovery_retry2_20260405` (`abandoned`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_a_dualpool_recovery_retry3_20260405` (`completed`)
  - `bgjob_human_notes_excerpt_parallel_judged_shard_b_dualpool_recovery_retry3_20260405` (`completed`)
  - `bgjob_attentional_v2_excerpt_micro_slice_smoke_20260405` (`completed`)
  - `bgjob_attentional_v2_excerpt_micro_slice_judged_20260405` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_a_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_b_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_c_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_d_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_eval_orchestrator_unitready_retry1_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_smoke_supremacy_recovery_20260406` (`completed`)
  - `bgjob_accumulation_benchmark_v1_judged_20260406` (`completed`)

### `TASK-PHASE9-COMPAT-CUTOVER` — Finish Phase 9 through compatibility cutover and default-path readiness
- Status: `done`
- Lane: `migration`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/phase9-compat-cutover-roadmap.md`
- Next: keep `attentional_v2` as the default product deep-reading path, keep `iterator_v1` as the explicit fallback/legacy-resume path, and treat later V2-native frontend presentation plus section-first retirement as post-Phase-9 initiatives rather than as unfinished cutover scope.
- Jobs: none

### `TASK-RUNTIME-STALE-PAUSE-TRUTH` — Reconcile stale/interrupted reading truth across backend lifecycle state and routed frontend surfaces
- Status: `done`
- Lane: `migration`
- Priority: `high`
- Detail: `docs/backend-sequential-lifecycle.md`
- Next: keep `status_reason` as the additive explanation layer for paused/error-like runtime states, keep stale-orphan reconciliation in startup/runtime recovery instead of GET paths, and treat restart/rerun UX as a separate future task rather than as part of this truth fix.
- Jobs: none

### `TASK-DOC-Q10` — Decide when to promote `attentional_v2` working design into stable docs
- Status: `done`
- Lane: `documentation`
- Priority: `medium`
- Detail: `docs/implementation/new-reading-mechanism/open-questions.md`
- Next: keep `docs/backend-reading-mechanisms/attentional_v2.md` as the stable live-mechanism authority, and keep future unfinished migration/cutover work in the Phase 9 tracker instead of reopening this timing question.

### `TASK-BOOK-ANALYSIS-RETIREMENT-CLARITY` — Mark `book_analysis` as retired legacy capability and remove ambiguity from the live deep-reading path
- Status: `done`
- Lane: `documentation`
- Priority: `high`
- Detail: `docs/history/decision-log.md`
- Next: keep the public `/analysis/*` route prefix as compatibility naming for the live deep-reading workflow, keep the legacy `book_analysis` implementation only as marked compatibility debt, and avoid expanding it as if it were an active product lane again.
- Jobs: none

### `TASK-EXCERPT-SURFACE-V1.1` — Retune the next excerpt surface incrementally from the notes-guided freeze
- Status: `done`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/excerpt-surface-v1-1-draft.md`
- Next: keep `excerpt surface v1.1` frozen as historical / superseded evidence with its explicit `5`-case exception on `nawaer_baodian_private_zh__22`; do not use it as the active local/user-level benchmark pointer now that `user-level selective v1` has replaced that role.
- Jobs:
  - `bgjob_excerpt_surface_v1_1_smoke_shard_a_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_smoke_shard_b_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_eval_orchestrator_20260406` (`abandoned`)
  - `bgjob_excerpt_surface_v1_1_eval_orchestrator_reshard4_20260406` (`abandoned`)
  - `bgjob_excerpt_surface_v1_1_eval_orchestrator_unitready_20260406` (`failed`)
  - `bgjob_excerpt_surface_v1_1_eval_orchestrator_unitready_retry1_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_a_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_b_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_c_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_judged_shard_d_20260406` (`completed`)
  - `bgjob_excerpt_surface_v1_1_smoke_supremacy_recovery_20260406` (`completed`)

### `TASK-DATASET-HUMAN-NOTES-GUIDED-V1` — Land the isolated human-notes-guided dataset line from the 5 linked books
- Status: `done`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/human-notes-guided-dataset-v1-freeze-draft.md`
- Next: keep the completed reviewed freeze as historical source material that fed the later excerpt-surface and note-aligned user-level lines; do not treat this task's output as the active benchmark pointer by itself.
- Jobs:
  - `bgjob_human_notes_guided_dataset_v1_scratch_20260404` (`failed`)
  - `bgjob_human_notes_guided_dataset_v1_scratch_retry1_20260404` (`completed`)
  - `bgjob_human_notes_guided_dataset_v1_scratch_retry2_20260404` (`completed`)
  - `bgjob_human_notes_guided_dataset_v1_scratch_retry3_20260404` (`completed`)
  - `bgjob_human_notes_guided_dataset_v1_first_review_en_20260404` (`failed`)
  - `bgjob_human_notes_guided_dataset_v1_first_review_zh_20260404` (`failed`)
  - `bgjob_human_notes_guided_dataset_v1_first_review_en_retry1_20260404` (`failed`)
  - `bgjob_human_notes_guided_dataset_v1_first_review_en_retry2_20260404` (`completed`)
  - `bgjob_human_notes_guided_dataset_v1_first_review_zh_retry1_20260404` (`completed`)

### `TASK-PHASE9-CLUSTERED-BENCHMARK` — Freeze clustered benchmark v1 as the active Phase 9 evaluation surface
- Status: `done`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/clustered-benchmark-v1-draft.md`
- Next: keep the frozen clustered benchmark as the active Phase 9 evaluation surface, preserve the honest `reserve = 7 / 8` shortfall, and move back to decisive mechanism-eval rather than reopening builder widening by default
- Jobs:
  - `bgjob_clustered_benchmark_v1_first_review_en_20260403` (`completed`)
  - `bgjob_clustered_benchmark_v1_first_review_zh_20260403` (`completed`)
  - `bgjob_clustered_benchmark_v1_reserve_review_en_20260404` (`completed`)
  - `bgjob_clustered_benchmark_v1_reserve_review_zh_20260404` (`completed`)

### `TASK-BENCH-BACKLOG-RESCUE` — Apply the round-2 backlog-rescue decision from the modern supplement
- Status: `done`
- Lane: `dataset_growth`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/private-library-promotion-round2.md`
- Next: keep the recorded `hold_for_backlog_rescue` outcome in force, do not reopen promotion without genuinely new benchmark-strengthening evidence, and treat the completed gate review as the route-back-to-mainline checkpoint
- Jobs: none

### `TASK-BENCH-ROUND3-CLEANUP` — Finish private-library cleanup and write the round-2 promotion draft
- Status: `done`
- Lane: `dataset_growth`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: use the landed round-2 draft plus the March 29 recovery summaries as the source of truth for the next dataset-growth move
- Jobs: none

### `TASK-BENCH-PROMOTION-ROUND2` — Decide the next benchmark-promotion move from the modern supplement
- Status: `done`
- Lane: `dataset_growth`
- Priority: `medium`
- Detail: `docs/implementation/new-reading-mechanism/private-library-promotion-round2.md`
- Next: keep the recorded `hold_for_backlog_rescue` decision in force until a human explicitly reopens the post-recovery gate discussion
- Jobs: none

### `TASK-MECH-EN-RERUN` — Run the focused English round-3 narrative/reference rerun
- Status: `done`
- Lane: `mechanism_eval`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: treat the completed backup-tier substantive rerun as evidence only; preserve the `walden` strength, keep the `up_from_slavery` chapter-arc weakness explicit, and do not launch default-cutover or promotion work automatically
- Jobs:
  - `bgjob_en_chapter_core_rerun_round3_caseiso_judged_followup_20260330` (`completed`)
  - `bgjob_en_chapter_core_rerun_round3_caseiso_judged_substantive_backup_20260331` (`completed`)

### `TASK-AGENT-SWITCHING-SYSTEM` — Land the repo-first agent-switching memory system
- Status: `done`
- Lane: `docs_tooling`
- Priority: `high`
- Detail: `docs/source-of-truth-map.md`
- Next: keep `docs/current-state.md` and `docs/tasks/registry.*` updated whenever live work changes

### `TASK-DATASET-SOURCE-GOVERNANCE` — Make source-book intake and intermediate artifacts clear and durable
- Status: `done`
- Lane: `dataset_platform`
- Priority: `high`
- Detail: `docs/implementation/new-reading-mechanism/new-reading-mechanism-execution-tracker.md`
- Next: keep using the managed inbox plus source catalog as the source of truth for future book additions, and treat public/private only as compatibility metadata instead of a primary workflow branch
- Jobs: none
