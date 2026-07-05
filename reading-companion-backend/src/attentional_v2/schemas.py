"""Phase 1 state schemas for the attentional_v2 reading mechanism."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, TypedDict

from src.reading_core.book_document import TextLocator, TextRole
from src.reading_core.normalized_outputs import ReactionType, SearchHit
from src.reading_core.runtime_contracts import ObservabilityMode, ResumeKind, RuntimeArtifactRefs, SharedRunCursor


StateOperationType = Literal[
    "append",
    "update",
    "close",
    "link",
    "create",
    "cool",
    "drop",
    "retain_anchor",
    "link_anchors",
    "promote",
    "supersede",
    "reactivate",
    "resolve",
]
BridgeResolutionDecision = Literal["bridge", "decline"]
ReflectivePromotionDecision = Literal["promote", "withhold"]
ReconsolidationDecision = Literal["reconsolidate", "keep_prior"]
KnowledgeUseMode = Literal["book_grounded_only", "book_grounded_plus_prior_knowledge"]
SearchPolicyMode = Literal["no_search", "defer_search", "search_now"]
SearchTrigger = Literal["none", "identity_critical_reference", "blocking_allusion", "genuine_curiosity", "ornamental_curiosity"]
ActivationStatus = Literal["weak", "plausible", "strong", "rejected", "dropped"]
AnchorRelationType = Literal["echo", "contrast", "cause", "support", "question_opened_by", "question_resolved_by", "callback"]
ATTENTIONAL_V2_SCHEMA_VERSION = 1
ATTENTIONAL_V2_MECHANISM_VERSION = "attentional_v2-phase9"
ATTENTIONAL_V2_POLICY_VERSION = "attentional_v2-policy-phase9"


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SourceRef(TypedDict, total=False):
    """Inline paragraph-offset source citation; not a registry entry."""

    source_span_id: str
    source_span: dict[str, object]
    quote: str
    role: str
    resolution: dict[str, object]


class ActiveAttentionItem(TypedDict, total=False):
    """One ActiveTension item carried in active attention."""

    item_id: str
    attention_tags: list[str]
    tension_from: str
    tension_focus: str
    working_interpretation: str
    answered_reason: str
    closed_reason: str
    source_refs: list[SourceRef]
    development_source_refs: list[SourceRef]
    opened_at_source_span_id: str
    opened_at_source_span: dict[str, object]
    opened_at_unit_span_id: str
    opened_at_unit_span: dict[str, object]
    answered_at_source_span_id: str
    answered_at_source_span: dict[str, object]
    answered_at_unit_span_id: str
    answered_at_unit_span: dict[str, object]
    closed_at_source_span_id: str
    closed_at_source_span: dict[str, object]
    closed_at_unit_span_id: str
    closed_at_unit_span: dict[str, object]
    status: str


class ActiveAttention(TypedDict, total=False):
    """Primary ActiveTension state for readerly charges still alive in attention."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    active_items: list[ActiveAttentionItem]


class RecentReadingMemoryEntry(TypedDict, total=False):
    """One append-only near-term memory entry created after reading a unit."""

    entry_id: str
    source_unit_span_id: str
    memory_text: str
    token_estimate: dict[str, object]
    status: str
    created_at_unit_index: int
    archived_by_consolidation_id: str | None


class RecentReadingMemoryState(TypedDict, total=False):
    """Near-term semantic memory of just-read units before consolidation."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    entries: list[RecentReadingMemoryEntry]


class LocalBufferSentence(TypedDict, total=False):
    """One recently seen sentence carried in the rolling local buffer."""

    sentence_id: str
    sentence_index: int
    paragraph_index: int
    text: str
    text_role: TextRole


class LocalBufferState(TypedDict, total=False):
    """Current rolling sentence buffer and open local meaning-unit span."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    current_sentence_id: str
    current_sentence_index: int
    recent_sentences: list[LocalBufferSentence]
    open_meaning_unit_sentence_ids: list[str]
    recent_meaning_units: list[list[str]]
    seen_sentence_ids: list[str]
    last_meaning_unit_closed_at_sentence_id: str
    is_reconstructed: bool
    reconstructed_from_checkpoint_id: str | None
    last_resume_kind: ResumeKind | None


class LocalContinuityState(TypedDict, total=False):
    """Compact continuity envelope persisted separately from the heavier local buffer."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    chapter_id: int | None
    chapter_ref: str
    current_sentence_id: str
    current_sentence_index: int
    recent_sentence_ids: list[str]
    open_meaning_unit_sentence_ids: list[str]
    recent_meaning_units: list[list[str]]
    last_meaning_unit_closed_at_sentence_id: str
    mainline_cursor: SharedRunCursor
    current_source_span: dict[str, object]
    current_source_span_id: str
    reading_queue_stage: str
    is_reconstructed: bool
    reconstructed_from_checkpoint_id: str | None
    last_resume_kind: ResumeKind | None


class PreviewRange(TypedDict, total=False):
    """One bounded preview range exposed to the unitization node."""

    start_sentence_id: str
    end_sentence_id: str
    start_cursor: dict[str, object]
    end_cursor: dict[str, object]
    preview_end_reason: str
    estimated_token_count: int
    preview_token_estimator: str


class UnitizeDecision(TypedDict, total=False):
    """One prompt-led coverage-unit selection for the next formal read."""

    start_sentence_id: str
    end_sentence_id: str
    unit: dict[str, object]
    preview_partition: list[dict[str, object]]
    preview_partition_audit: list[dict[str, object]]
    preview_partition_audit_status: str
    unit_partition_range: dict[str, int]
    unit_partition_titles: list[str]
    unit_estimated_token_count: int
    unit_size_policy: dict[str, int]
    unit_size_status: str
    end_anchor_text: str
    source_span: dict[str, object]
    source_span_id: str
    resolution: dict[str, object]
    preview_range: PreviewRange
    evidence_sentence_ids: list[str]
    reason: str


class CarryForwardRef(TypedDict, total=False):
    """One bounded carry-forward reference exposed to the Digest node."""

    ref_id: str
    kind: str
    item_id: str
    summary: str
    source_span_id: str
    source_ref: SourceRef
    reaction_id: str
    route_id: str


class SessionContinuityCapsule(TypedDict, total=False):
    """Small session-continuity capsule that should stay cheap to reload every unit."""

    recent_sentence_ids: list[str]
    recent_meaning_units: list[list[str]]
    recent_reactions: list[dict[str, object]]


class ContinuationCapsule(TypedDict, total=False):
    """Persisted continuity seed used to restart carried context after pauses or resume."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    chapter_ref: str
    current_sentence_id: str
    session_continuity_capsule: SessionContinuityCapsule
    active_attention_digest: "ActiveAttentionDigest"
    recent_reading_memory: "RecentReadingMemoryDigest"
    chapter_reflective_frame: "ReflectiveFrameDigest"
    active_focus_digest: "ActiveFocusDigest"
    refs: list["CarryForwardRef"]


class ActiveAttentionDigest(TypedDict, total=False):
    """Prompt-facing digest of the current hot active-attention state."""

    active_items: list[dict[str, object]]
    hot_items: list[dict[str, object]]


class RecentReadingMemoryDigest(TypedDict, total=False):
    """Prompt-facing digest of active recent reading memory entries."""

    active_entries: list[dict[str, object]]
    active_entry_count: int


class ReflectiveFrameDigest(TypedDict, total=False):
    """Bounded reflective frame packet for the current chapter/book."""

    chapter_frames: list[dict[str, object]]
    book_frames: list[dict[str, object]]
    durable_definitions: list[dict[str, object]]


class ActiveFocusDigest(TypedDict, total=False):
    """Small digest of currently active attention plus recent moves and reactions."""

    active_items: list[dict[str, object]]
    recent_reactions: list[dict[str, object]]


class CarryForwardContext(TypedDict, total=False):
    """Small stable continuity packet passed into every formal read."""

    packet_version: str
    continuation_capsule: ContinuationCapsule
    session_continuity_capsule: SessionContinuityCapsule
    active_attention_digest: ActiveAttentionDigest
    recent_reading_memory: RecentReadingMemoryDigest
    chapter_reflective_frame: ReflectiveFrameDigest
    active_focus_digest: ActiveFocusDigest
    reflective_digest: list[dict[str, object]]
    source_ref_digest: list[dict[str, object]]
    continuity_digest: dict[str, object]
    refs: list[CarryForwardRef]


class PriorMaterialUse(TypedDict, total=False):
    """Observation of whether prior material materially informed the current read."""

    materially_used: bool
    explanation: str
    supporting_ref_ids: list[str]


class ReadAnchorEvidence(TypedDict, total=False):
    """One exact unit-local anchor cited by the read step."""

    source_span_id: str
    source_ref: SourceRef
    quote: str
    why_it_matters: str


class DigestResult(TypedDict, total=False):
    """Structured record of one reader-like pass over a chosen coverage unit."""

    understanding: str
    reading_impression: str
    marginalia: list["MarginaliaItem"]
    surfaced_reactions: list["SurfacedReaction"]
    memory_uptake_ops: list["StateOperation"]
    memory_uptake_admission_events: list["MemoryUptakeAdmissionEvent"]


MemoryUptakeAdmissionStatus = Literal[
    "accepted",
    "dropped_unknown_operation",
    "dropped_malformed_operation",
    "dropped_unsupported_target_store",
    "dropped_unsupported_operation_for_target_store",
]
MemoryUptakeOperationStorePolicy = Literal["supported", "unsupported_target_store", "unsupported_operation_for_target_store"]


class MemoryUptakeAdmissionEvent(TypedDict, total=False):
    """Audit-only admission metadata captured before memory operations are normalized."""

    operation_index: int
    admission_status: MemoryUptakeAdmissionStatus
    operation_type_emitted: str
    operation_type_normalized: str
    target_store_emitted: str
    effective_target_store: str
    target_key: str
    item_id: str
    compatibility_warnings: list[str]
    drop_reason: str
    target_store_supported: bool
    operation_store_policy: MemoryUptakeOperationStorePolicy
    policy_warnings: list[str]


class StateOperation(TypedDict, total=False):
    """One explicit state mutation proposed by a Phase 4 node."""

    op: StateOperationType
    operation_type: StateOperationType
    target_store: str
    target_store_emitted: str
    effective_target_store: str
    target_key: str
    item_id: str
    reason: str
    compatibility_warnings: list[str]
    payload: dict[str, object]


class MarginaliaItem(TypedDict, total=False):
    """One visible page-margin reader note surfaced directly by Digest."""

    kind: str
    source_quote: str
    content: str
    selection_reason: str
    prior_link: "PriorLink" | None
    outside_link: "OutsideLink" | None
    search_intent: "SearchIntent" | None


class MarginaliaAuditItem(TypedDict, total=False):
    """Legacy mechanism-private selection audit for pre-v15 highlight Marginalia."""

    source_quote: str
    selection_reason: str


SurfacedReaction = MarginaliaItem


class IngestBoundaryResult(TypedDict, total=False):
    """One bounded Ingest LLM boundary result."""

    reason: str
    unit: dict[str, object]
    preview_partition: list[dict[str, object]]
    preview_partition_audit: list[dict[str, object]]
    preview_partition_audit_status: str
    unit_partition_range: dict[str, int]
    unit_partition_titles: list[str]
    unit_estimated_token_count: int
    unit_size_policy: dict[str, int]
    unit_size_status: str
    end_anchor_text: str
    memory_recalls: list["UnitMemoryRecall"]
    memory_recalls_status: str
    tool_loop_status: str
    tool_result_summary: dict[str, object]


class IngestTraceEntry(TypedDict, total=False):
    """One compact Ingest boundary trace entry."""

    reason: str
    unit: dict[str, object]
    preview_partition: list[dict[str, object]]
    preview_partition_audit: list[dict[str, object]]
    preview_partition_audit_status: str
    unit_partition_range: dict[str, int]
    unit_partition_titles: list[str]
    unit_estimated_token_count: int
    unit_size_policy: dict[str, int]
    unit_size_status: str
    end_anchor_text: str
    memory_recalls: list["UnitMemoryRecall"]
    memory_recalls_status: str
    tool_loop_status: str
    tool_result_summary: dict[str, object]
    source_span_id: str
    resolution: dict[str, object]
    error: str


MemoryRetrievalMode = Literal["text_only", "hybrid"]


class UnitMemoryQuery(TypedDict, total=False):
    """One internal runtime retrieval query derived from recalls or fallback source text."""

    query_version: str
    query_text: str
    basis: str
    recall_id: str


class UnitMemoryRecall(TypedDict, total=False):
    """One Ingest-authored prior-reading recall intention."""

    recall_id: str
    recall_text: str
    basis: str


class UnitMemoryRetrievalConfig(TypedDict, total=False):
    """Mechanism-private read-time Unit Memory retrieval configuration."""

    schema_version: str
    mode: MemoryRetrievalMode
    default_mode: MemoryRetrievalMode
    selected_by: str
    config_warnings: list[str]
    updated_at: str


class UnitMemoryRetrievalResult(TypedDict, total=False):
    """Trace-oriented result from one Unit Memory retrieval attempt."""

    query: UnitMemoryQuery
    recalls: list[UnitMemoryRecall]
    query_source: str
    mode: MemoryRetrievalMode
    effective_mode: MemoryRetrievalMode
    degradation_reason: str
    selected_units: list[dict[str, object]]
    reading_memory_lines: list[dict[str, object]]
    trace: dict[str, object]


class PreparedSourceUnit(TypedDict, total=False):
    """One runtime-prepared source unit that should be read next."""

    chapter_id: int
    chapter_ref: str
    selected_unit_sentences: list[dict[str, object]]
    selected_source_unit: dict[str, object]
    preview: dict[str, object]
    unitize_decision: UnitizeDecision
    ingest_trace: list[IngestTraceEntry]
    memory_recalls: list[UnitMemoryRecall]
    memory_recalls_status: str
    unit_memory_retrieval: UnitMemoryRetrievalResult


class UnitMemoryIndexStatus(TypedDict, total=False):
    """Index status stored with one Unit Memory entry."""

    fts: str
    vector: str
    last_error: str | None


class UnitMemoryEntry(TypedDict, total=False):
    """One content-neutral completed-unit memory entry."""

    unit_id: str
    book_id: str
    schema_version: str
    mechanism_version: str
    created_at: str
    chapter_id: int
    chapter_ref: str
    unit_index: int
    source_span_id: str
    accepted_source_unit: dict[str, object]
    digest: dict[str, object]
    index_status: UnitMemoryIndexStatus
    memory_retrieval_mode: MemoryRetrievalMode


class BridgeCandidate(TypedDict, total=False):
    """One bridge candidate record passed to later bridge judgment."""

    candidate_kind: str
    target_anchor_id: str
    target_sentence_id: str
    retrieval_channel: str
    relation_type: AnchorRelationType | str
    score: float
    why_now: str
    quote: str
    locator: TextLocator


class ReactionCandidate(TypedDict, total=False):
    """One candidate anchored reaction proposed before emission gating."""

    type: ReactionType
    source_quote: str
    content: str
    related_source_quotes: list[str]
    search_query: str
    search_results: list[SearchHit]


class PriorLink(TypedDict, total=False):
    """One explicit surfaced link back to earlier source-grounded material."""

    ref_ids: list[str]
    relation: str
    note: str


class OutsideLink(TypedDict, total=False):
    """One explicit surfaced book-external reference carried by a visible reaction."""

    kind: str
    label: str
    note: str


class SearchIntent(TypedDict, total=False):
    """One explicit surfaced search follow-up request."""

    query: str
    rationale: str


class BridgeAttribution(TypedDict, total=False):
    """Explicit source-grounded explanation for one accepted bridge."""

    target_quote: str
    current_quote: str
    relation_explanation: str


class ReactionAnchor(TypedDict, total=False):
    """One persisted source anchor embedded directly into a durable visible reaction."""

    anchor_id: str
    sentence_start_id: str
    sentence_end_id: str
    quote: str
    locator: TextLocator


class AnchoredReactionRecord(TypedDict, total=False):
    """Mechanism-authored durable visible thought with source-preserving anchors."""

    reaction_id: str
    chapter_id: int
    chapter_ref: str
    emitted_at_source_span_id: str
    record_source: str
    type: ReactionType
    compat_family: ReactionType
    marginalia_kind: str
    thought: str
    source_quote: str
    primary_source_ref: SourceRef
    related_source_refs: list[SourceRef]
    reconsolidation_record_id: str
    supersedes_reaction_id: str
    compatibility_section_ref: str
    prior_link: PriorLink | None
    outside_link: OutsideLink | None
    search_intent: SearchIntent | None
    search_query: str
    search_results: list[SearchHit]
    created_at: str


class BridgeResolutionResult(TypedDict, total=False):
    """Structured bridge-judgment result over deterministic candidate retrieval."""

    decision: BridgeResolutionDecision
    reason: str
    primary_bridge: BridgeCandidate | None
    primary_attribution: BridgeAttribution | None
    supporting_bridges: list[BridgeCandidate]
    activation_updates: list[StateOperation]
    state_operations: list[StateOperation]
    knowledge_use_mode: KnowledgeUseMode
    search_policy_mode: SearchPolicyMode
    search_trigger: SearchTrigger
    search_query: str


class AnchorRecord(TypedDict, total=False):
    """One source-grounded anchor retained for later bridge or recall use."""

    anchor_id: str
    sentence_start_id: str
    sentence_end_id: str
    quote: str
    locator: TextLocator
    anchor_kind: str
    why_it_mattered: str
    status: str
    linked_reaction_ids: list[str]
    linked_activation_ids: list[str]


class AnchorRelation(TypedDict, total=False):
    """One typed relation between retained anchors."""

    relation_id: str
    relation_type: AnchorRelationType
    source_anchor_id: str
    target_anchor_id: str
    rationale: str


class AnchorBankState(TypedDict, total=False):
    """Primary source-grounded evidence store after the Phase C.3 migration."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    anchor_records: list[AnchorRecord]
    anchor_relations: list[AnchorRelation]


class AnchorMemoryState(TypedDict, total=False):
    """Retrieval-facing earlier state for bridge and callback behavior."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    anchor_records: list[AnchorRecord]
    anchor_relations: list[AnchorRelation]
    motif_index: dict[str, list[str]]
    unresolved_reference_index: dict[str, list[str]]
    trace_links: dict[str, list[str]]


class ReflectiveItem(TypedDict, total=False):
    """One promoted reflective understanding retained across local hot state."""

    item_id: str
    statement: str
    source_refs: list[SourceRef]
    confidence_band: str
    promoted_from: str
    status: str
    superseded_by_item_id: str
    chapter_ref: str


class ReflectivePromotionCandidate(TypedDict, total=False):
    """One candidate statement that may earn promotion into reflective summaries."""

    candidate_id: str
    statement: str
    source_refs: list[SourceRef]
    promoted_from: str
    target_bucket: str
    rationale: str


class ReflectivePromotionResult(TypedDict, total=False):
    """Structured result from the reflective-promotion node."""

    decision: ReflectivePromotionDecision
    reason: str
    target_bucket: str
    reflective_item: ReflectiveItem | None
    supersede_bucket: str
    supersede_item_id: str
    state_operations: list[StateOperation]


class ReflectiveSummariesState(TypedDict, total=False):
    """Slower durable understanding promoted from local reading state."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    chapter_understandings: list[ReflectiveItem]
    book_level_frames: list[ReflectiveItem]
    durable_definitions: list[ReflectiveItem]
    stabilized_motifs: list[ReflectiveItem]
    resolved_questions_of_record: list[ReflectiveItem]
    chapter_end_notes: list[ReflectiveItem]


class ReflectiveFramesState(ReflectiveSummariesState, total=False):
    """Primary slower reflective layer after the Phase C.3 migration."""


class KnowledgeActivation(TypedDict, total=False):
    """One activated piece of prior knowledge with separate warrant tracking."""

    activation_id: str
    trigger_source_ref: SourceRef
    activation_type: str
    source_candidate: str
    recognition_confidence: str
    reading_warrant: str
    role_assessment: str
    evidence_hints: list[str]
    evidence_rationale: str
    source_refs: list[SourceRef]
    conflict_source_refs: list[SourceRef]
    status: ActivationStatus


class KnowledgeActivationsState(TypedDict, total=False):
    """Knowledge-activation ledger plus current use-policy mode."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    knowledge_use_mode: KnowledgeUseMode
    search_policy_mode: SearchPolicyMode
    activations: list[KnowledgeActivation]


class ReactionRecordsState(TypedDict, total=False):
    """Append-only mechanism-owned durable reaction history."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    records: list[AnchoredReactionRecord]


class ReconsolidationRecord(TypedDict, total=False):
    """Append-only record of later reinterpretation linked to earlier thought."""

    record_id: str
    prior_reaction_id: str
    new_reaction_id: str
    change_kind: str
    what_changed: str
    rationale: str
    created_at: str


class ReconsolidationRecordsState(TypedDict, total=False):
    """Append-only ledger of reconsolidation events."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    records: list[ReconsolidationRecord]


class ReconsolidationResult(TypedDict, total=False):
    """Structured result from the reconsolidation node."""

    decision: ReconsolidationDecision
    reason: str
    reconsolidation_record: ReconsolidationRecord | None
    later_reaction: AnchoredReactionRecord | None
    state_updates: list[StateOperation]


class ChapterConsolidationResult(TypedDict, total=False):
    """Structured chapter-end sweep and carry-forward result."""

    chapter_ref: str
    backward_sweep: list[dict[str, object]]
    cooling_operations: list[StateOperation]
    promotion_candidates: list[ReflectivePromotionCandidate]
    knowledge_activation_updates: list[StateOperation]
    cross_chapter_carry_forward: list[ActiveAttentionItem]
    chapter_summary_note: str
    optional_chapter_reaction: ReactionCandidate | None


class SlowCycleAuditEnvelope(TypedDict, total=False):
    """Compact audit-only envelope for slow-cycle candidate and settlement evidence."""

    trigger_type: str
    chapter_ref: str
    candidate_type: str
    candidate_id: str
    source_ref_count: int
    source_ref_resolution_statuses: list[str]
    promotion_evidence_status: str
    settlement_decision: str
    settlement_reason: str
    withhold_promotion_reason: str
    not_carried_reason: str
    carry_forward_reason: str
    target_bucket: str
    settled_item_id: str
    supersede_bucket: str
    supersede_item_id: str


class LoggingPolicy(TypedDict, total=False):
    """Versioned observability policy for standard vs debug persistence."""

    observability_mode: ObservabilityMode
    event_stream: bool
    checkpoint_summaries: bool
    debug_event_stream: bool
    debug_checkpoint_diagnostics: bool


class ReaderPolicy(TypedDict, total=False):
    """Versioned mechanism policy kept separate from ontology-bearing state."""

    schema_version: int
    mechanism_version: str
    policy_version: str
    updated_at: str
    unitize: dict[str, object]
    read: dict[str, object]
    knowledge: dict[str, object]
    search: dict[str, object]
    bridge: dict[str, object]
    resume: dict[str, object]
    logging: LoggingPolicy


class ResumeMetadataState(TypedDict, total=False):
    """Mechanism-private metadata about checkpointing, reconstruction, and last resume behavior."""

    schema_version: int
    mechanism_version: str
    policy_version: str
    updated_at: str
    resume_available: bool
    default_resume_kind: ResumeKind
    last_checkpoint_id: str | None
    last_checkpoint_at: str | None
    last_resume_kind: ResumeKind | None
    last_resume_at: str | None
    last_resume_checkpoint_id: str | None
    last_resume_status: str
    last_resume_reason: str
    last_resume_window_sentence_ids: list[str]
    reconstructed_hot_state: bool


class FullCheckpointState(TypedDict, total=False):
    """Mechanism-owned full checkpoint used for warm, cold, and reconstitution resume."""

    schema_version: int
    mechanism_version: str
    policy_version: str
    checkpoint_id: str
    created_at: str
    checkpoint_reason: str
    resume_kind: ResumeKind
    cursor: SharedRunCursor
    active_artifact_refs: RuntimeArtifactRefs
    visible_reaction_ids: list[str]
    local_buffer: LocalBufferState
    local_continuity: LocalContinuityState
    continuation_capsule: ContinuationCapsule
    active_attention: ActiveAttention
    recent_reading_memory: RecentReadingMemoryState
    reflective_frames: ReflectiveFramesState
    reflective_summaries: ReflectiveSummariesState
    knowledge_activations: KnowledgeActivationsState
    reaction_records: ReactionRecordsState
    reconsolidation_records: ReconsolidationRecordsState
    reader_policy: ReaderPolicy
    memory_retrieval_config: UnitMemoryRetrievalConfig
    resume_metadata: ResumeMetadataState


def build_empty_active_attention(*, mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION) -> ActiveAttention:
    """Return the default primary hot attention state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "active_items": [],
    }


def build_empty_recent_reading_memory(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> RecentReadingMemoryState:
    """Return the default append-only recent reading memory state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "entries": [],
    }


def build_empty_local_buffer(*, mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION) -> LocalBufferState:
    """Return the default local buffer state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "current_sentence_id": "",
        "current_sentence_index": 0,
        "recent_sentences": [],
        "open_meaning_unit_sentence_ids": [],
        "recent_meaning_units": [],
        "seen_sentence_ids": [],
        "last_meaning_unit_closed_at_sentence_id": "",
        "is_reconstructed": False,
        "reconstructed_from_checkpoint_id": None,
        "last_resume_kind": None,
    }


def build_empty_local_continuity(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> LocalContinuityState:
    """Return the compact continuity envelope used by Phase 7 checkpointing and resume."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "chapter_id": None,
        "chapter_ref": "",
        "current_sentence_id": "",
        "current_sentence_index": 0,
        "recent_sentence_ids": [],
        "open_meaning_unit_sentence_ids": [],
        "recent_meaning_units": [],
        "last_meaning_unit_closed_at_sentence_id": "",
        "mainline_cursor": {
            "position_kind": "chapter",
            "chapter_id": None,
            "chapter_ref": "",
        },
        "reading_queue_stage": "",
        "is_reconstructed": False,
        "reconstructed_from_checkpoint_id": None,
        "last_resume_kind": None,
    }


def build_empty_continuation_capsule(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ContinuationCapsule:
    """Return the default persisted continuation capsule."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "chapter_ref": "",
        "current_sentence_id": "",
        "session_continuity_capsule": {
            "recent_sentence_ids": [],
            "recent_meaning_units": [],
            "recent_reactions": [],
        },
        "active_attention_digest": {
            "active_items": [],
            "hot_items": [],
        },
        "recent_reading_memory": {
            "active_entries": [],
            "active_entry_count": 0,
        },
        "chapter_reflective_frame": {
            "chapter_frames": [],
            "book_frames": [],
            "durable_definitions": [],
        },
        "active_focus_digest": {
            "active_items": [],
            "recent_reactions": [],
        },
        "refs": [],
    }


def build_empty_anchor_memory(*, mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION) -> AnchorMemoryState:
    """Return the default anchor-memory state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "anchor_records": [],
        "anchor_relations": [],
        "motif_index": {},
        "unresolved_reference_index": {},
        "trace_links": {},
    }


def build_empty_anchor_bank(*, mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION) -> AnchorBankState:
    """Return the default primary anchor-bank state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "anchor_records": [],
        "anchor_relations": [],
    }


def build_empty_reflective_summaries(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ReflectiveSummariesState:
    """Return the default reflective-summary state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "chapter_understandings": [],
        "book_level_frames": [],
        "durable_definitions": [],
        "stabilized_motifs": [],
        "resolved_questions_of_record": [],
        "chapter_end_notes": [],
    }


def build_empty_reflective_frames(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ReflectiveFramesState:
    """Return the default reflective-frames state."""

    return build_empty_reflective_summaries(mechanism_version=mechanism_version)


def build_empty_knowledge_activations(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> KnowledgeActivationsState:
    """Return the default knowledge-activation state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "knowledge_use_mode": "book_grounded_only",
        "search_policy_mode": "no_search",
        "activations": [],
    }


def build_empty_reaction_records(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ReactionRecordsState:
    """Return the default durable anchored-reaction state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "records": [],
    }


def build_empty_reconsolidation_records(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ReconsolidationRecordsState:
    """Return the default reconsolidation state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": _timestamp(),
        "records": [],
    }


def build_default_reader_policy(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
    policy_version: str = ATTENTIONAL_V2_POLICY_VERSION,
) -> ReaderPolicy:
    """Return the default versioned reader policy."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "policy_version": policy_version,
        "updated_at": _timestamp(),
        "unitize": {
            "max_coverage_unit_sentences": 12,
            "preview_soft_min_tokens": 1600,
            "preview_target_max_tokens": 3000,
            "preview_hard_max_tokens": 4200,
            "unit_soft_min_tokens": 300,
            "unit_target_max_tokens": 900,
            "unit_hard_max_tokens": 1600,
            "emergency_max_preview_paragraphs": 200,
        },
        "knowledge": {
            "default_mode": "book_grounded_only",
            "allow_prior_knowledge_when_warranted": True,
        },
        "search": {
            "default_mode": "no_search",
            "allow_search_now": True,
            "rare_search_posture": True,
            "defer_curiosity_by_default": True,
        },
        "bridge": {"enabled": False, "source_ref_required": True, "max_supporting_candidates": 2},
        "resume": {
            "default_mode": "warm_resume",
            "cold_resume_target_sentences": 8,
            "cold_resume_max_sentences": 12,
            "reconstitution_resume_target_sentences": 24,
            "reconstitution_resume_max_sentences": 30,
            "reconstitution_resume_target_meaning_units": 3,
            "chapter_local_only": True,
            "checkpoint_summary_required": True,
        },
        "logging": {
            "observability_mode": "standard",
            "event_stream": True,
            "checkpoint_summaries": True,
            "debug_event_stream": False,
            "debug_checkpoint_diagnostics": False,
        },
    }


def build_empty_resume_metadata(
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
    policy_version: str = ATTENTIONAL_V2_POLICY_VERSION,
) -> ResumeMetadataState:
    """Return the default resume metadata state."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "policy_version": policy_version,
        "updated_at": _timestamp(),
        "resume_available": False,
        "default_resume_kind": "warm_resume",
        "last_checkpoint_id": None,
        "last_checkpoint_at": None,
        "last_resume_kind": None,
        "last_resume_at": None,
        "last_resume_checkpoint_id": None,
        "last_resume_status": "not_started",
        "last_resume_reason": "",
        "last_resume_window_sentence_ids": [],
        "reconstructed_hot_state": False,
    }
