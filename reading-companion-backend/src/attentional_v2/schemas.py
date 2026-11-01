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
ReconsolidationDecision = Literal["reconsolidate", "keep_prior"]
SearchTrigger = Literal["none", "identity_critical_reference", "blocking_allusion", "genuine_curiosity", "ornamental_curiosity"]
ActivationStatus = Literal["weak", "plausible", "strong", "rejected", "dropped"]
ATTENTIONAL_V2_SCHEMA_VERSION = 3
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
    recent_reading_memory: "RecentReadingMemoryDigest"
    refs: list["CarryForwardRef"]


class RecentReadingMemoryDigest(TypedDict, total=False):
    """Prompt-facing digest of active recent reading memory entries."""

    active_entries: list[dict[str, object]]
    active_entry_count: int


class CarryForwardContext(TypedDict, total=False):
    """Small stable continuity packet passed into every formal read."""

    packet_version: str
    continuation_capsule: ContinuationCapsule
    session_continuity_capsule: SessionContinuityCapsule
    recent_reading_memory: RecentReadingMemoryDigest
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
    supersedes_reaction_id: str
    compatibility_section_ref: str
    prior_link: PriorLink | None
    outside_link: OutsideLink | None
    search_intent: SearchIntent | None
    search_query: str
    search_results: list[SearchHit]
    created_at: str


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




class ReactionRecordsState(TypedDict, total=False):
    """Append-only mechanism-owned durable reaction history."""

    schema_version: int
    mechanism_version: str
    updated_at: str
    records: list[AnchoredReactionRecord]


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
    chapter_planning_mode: str
    unitize: dict[str, object]
    read: dict[str, object]
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
    reading_id: str | None
    last_product_unit_id: str | None
    last_product_unit_sequence: int


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
    reading_id: str
    last_product_unit_id: str | None
    last_product_unit_sequence: int
    local_buffer: LocalBufferState
    local_continuity: LocalContinuityState
    continuation_capsule: ContinuationCapsule
    recent_reading_memory: RecentReadingMemoryState
    reaction_records: ReactionRecordsState
    reader_policy: ReaderPolicy
    memory_retrieval_config: UnitMemoryRetrievalConfig
    resume_metadata: ResumeMetadataState


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
        "recent_reading_memory": {
            "active_entries": [],
            "active_entry_count": 0,
        },
        "refs": [],
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
        "chapter_planning_mode": "body_first",
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
        "reading_id": None,
        "last_product_unit_id": None,
        "last_product_unit_sequence": 0,
    }
