# New Reading Mechanism Requirement Ledger

Purpose: provide atomic traceability from the original design to implementation, deferral, rejection, validation, and stable-doc promotion.
Use when: checking whether a design point is tracked, deciding what work is still missing, or verifying that implementation has not outrun design coverage.
Not for: long-form rationale or stable mechanism authority.
Update when: a new requirement is captured, a disposition changes, or implementation/validation status changes.

## Ledger Policy
- Use one row per atomic requirement or tightly coupled invariant.
- If two design points could land separately, they should not share one row.
- Every row must have an explicit disposition.
- Phase 0 exception:
  - before full atomic expansion, we allow one seed row per confirmed source block or prompt contract block
  - those seed rows exist only to prevent silent omission
  - they must be expanded into atomic rows before implementation of that block begins

## Status Values
- `unmapped`
- `planned`
- `in_progress`
- `done`
- `deferred`
- `rejected`
- `promoted`

## Disposition Values
- `planned_for_implementation`
- `implemented`
- `explicitly_deferred`
- `explicitly_rejected`
- `promoted_to_stable_docs`

## Ledger
| Req ID | Source section | Atomic requirement | Disposition | Status | Phase | Validation | Stable-doc impact | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-BOOT-001 | Goal / First Principles | The new mechanism implementation must be driven by explicit design coverage, not by memory or implementation convenience. | `planned_for_implementation` | `planned` | Phase 0 | docs review | `none` | Bootstrap traceability rule |
| R-BOOT-002 | Coverage control | Every meaningful design point from the Notion page must map to implementation, explicit deferral, explicit rejection, or stable-doc promotion. | `planned_for_implementation` | `planned` | Phase 0 | docs review | `none` | Governs omission control for the whole project |

## Seed Coverage Rows
These rows are not the final atomic ledger. They are the minimum source-block inventory required to prevent silent loss before deeper decomposition.

| Req ID | Source section | Atomic requirement | Disposition | Status | Phase | Validation | Stable-doc impact | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-SRC-001 | Goal | Expand and track the full `Goal` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 0 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-002 | First Principles | Expand and track the full `First Principles` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 0 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-003 | Core Principle | Expand and track the full `Core Principle` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 0 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-004 | What Broad Prior Knowledge Is For | Expand and track the full `What Broad Prior Knowledge Is For` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 5 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-005 | Core Runtime Objects | Expand and track the full `Core Runtime Objects` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 1 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-006 | Tiered Reading State | Expand and track the full `Tiered Reading State` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 1 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-007 | Working Pressure | Expand and track the full `Working Pressure` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 1 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-008 | Anchor Memory | Expand and track the full `Anchor Memory` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 1 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-009 | Reflective Summaries | Expand and track the full `Reflective Summaries` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 1 / 6 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-010 | State Operations | Expand and track the full `State Operations` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 1 / 6 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-011 | Knowledge Activation Objects | Expand and track the full `Knowledge Activation Objects` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 5 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-012 | Knowledge-Use Policy | Expand and track the full `Knowledge-Use Policy` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 5 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-013 | Search Policy | Expand and track the full `Search Policy` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 5 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-014 | Bridge Retrieval | Expand and track the full `Bridge Retrieval` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 5 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-015 | Book Survey First | Expand and track the full `Book Survey First` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 2 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-016 | Qualitative Escalation Gates | Expand and track the full `Qualitative Escalation Gates` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 3 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-017 | Main Reading Loop | Expand and track the full `Main Reading Loop` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 3 / 4 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-018 | Controller | Expand and track the full `Controller` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 4 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-019 | Version-One Candidate-Boundary Signals | Expand and track the full `Version-One Candidate-Boundary Signals` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 3 | docs review | `none` | Seed row |
| R-SRC-020 | How Focus Is Selected | Expand and track the full `How Focus Is Selected` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 3 / 4 | docs review | `none` | Seed row |
| R-SRC-021 | Version-One Trigger Ensemble | Expand and track the full `Version-One Trigger Ensemble` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 3 | docs review | `none` | Seed row |
| R-SRC-022 | Trigger Ensemble Output Schema | Expand and track the full `Trigger Ensemble Output Schema` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 3 | docs review | `none` | Seed row |
| R-SRC-023 | When To Zoom To Sentence Level | Expand and track the full `When To Zoom To Sentence Level` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 3 / 4 | docs review | `none` | Seed row |
| R-SRC-024 | LLM Call Policy | Expand and track the full `LLM Call Policy` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 4 | docs review | `none` | Seed row |
| R-SRC-025 | Zoom Read Call | Expand and track the full `Zoom Read Call` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 4 | docs review | `none` | Seed row |
| R-SRC-026 | What Each Interpretive Call Should Return | Expand and track the full `What Each Interpretive Call Should Return` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 4 / 6 | docs review | `none` | Seed row |
| R-SRC-027 | Prompt Packet | Expand and track the full `Prompt Packet` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 4 | docs review | `none` | Seed row |
| R-SRC-028 | Non-Cheating Constraint | Expand and track the full `Non-Cheating Constraint` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 2 / 4 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-029 | User-Visible Output | Expand and track the full `User-Visible Output` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 4 / 6 / 8 | docs review | `docs/backend-state-aggregation.md`, `docs/api-contract.md` | Seed row |
| R-SRC-030 | Reconsolidation | Expand and track the full `Reconsolidation` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 6 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-031 | Anti-Miss Safeguards | Expand and track the full `Anti-Miss Safeguards` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 6 / 8 | docs review | `none` | Seed row |
| R-SRC-032 | Persistence and Resume | Expand and track the full `Persistence and Resume` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 7 | docs review | `docs/backend-sequential-lifecycle.md`, `docs/runtime-modes.md` | Seed row |
| R-SRC-033 | Relationship To The Existing Mechanism | Expand and track the full `Relationship To The Existing Mechanism` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 0 / 9 | docs review | `docs/backend-reading-mechanism.md` | Seed row |
| R-SRC-034 | Success Standard | Expand and track the full `Success Standard` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 8 / 9 | docs review | `docs/backend-reader-evaluation.md`, `docs/backend-reading-mechanisms/<mechanism>.md` | Seed row |
| R-SRC-035 | Decisions Made So Far | Expand and track the full `Decisions Made So Far` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 0 | docs review | `decision-log.md` | Seed row |
| R-SRC-036 | Calibration and Configuration Layer | Expand and track the full `Calibration and Configuration Layer` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 1 / 8 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md`, `docs/backend-reader-evaluation.md` | Seed row |
| R-SRC-037 | Failure Modes And Degradation Patterns | Expand and track the full `Failure Modes And Degradation Patterns` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 8 | docs review | `docs/backend-reader-evaluation.md` | Seed row |
| R-SRC-038 | Instrumentation and Observability Contract | Expand and track the full `Instrumentation and Observability Contract` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 8 | docs review | `docs/backend-reader-evaluation.md` | Seed row |
| R-SRC-039 | Evaluation Mapping And Acceptance Criteria | Expand and track the full `Evaluation Mapping And Acceptance Criteria` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 8 / 9 | docs review | `docs/backend-reader-evaluation.md` | Seed row |
| R-SRC-040 | Open Design Questions | Expand and track the full `Open Design Questions` block before work that depends on it proceeds. | `planned_for_implementation` | `planned` | Phase 0 onward | docs review | `open-questions.md` | Seed row |
| R-CTR-001 | `zoom_read` Contract v0 | Atomically expand and track the `zoom_read` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 4 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-002 | `meaning_unit_closure` Contract v0 | Atomically expand and track the `meaning_unit_closure` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 4 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-003 | `controller_decision` Contract v0 | Atomically expand and track the `controller_decision` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 4 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-004 | `bridge_resolution` Contract v0 | Atomically expand and track the `bridge_resolution` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 5 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-005 | `candidate_generation` Contract v0 | Atomically expand and track the `candidate_generation` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 3 / 5 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-006 | `reaction_emission` Contract v0 | Atomically expand and track the `reaction_emission` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 4 / 6 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md`, `docs/backend-state-aggregation.md` | Contract seed row |
| R-CTR-007 | `reflective_promotion` Contract v0 | Atomically expand and track the `reflective_promotion` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 6 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-008 | `reconsolidation` Contract v0 | Atomically expand and track the `reconsolidation` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 6 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-009 | `book_survey` Contract v0 | Atomically expand and track the `book_survey` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 2 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |
| R-CTR-010 | `chapter_consolidation` Contract v0 | Atomically expand and track the `chapter_consolidation` contract before node implementation begins. | `planned_for_implementation` | `planned` | Phase 6 | docs review | `docs/backend-reading-mechanisms/<mechanism>.md` | Contract seed row |

## Completion Rule
- We should not claim the design is fully covered until:
  - the source mirror is complete enough to review against the Notion page
  - every major source block has ledger rows
  - every ledger row has a non-`unmapped` disposition
  - every deferred or rejected item is explicit and justified
