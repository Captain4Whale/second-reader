"""Phase 6 slow-cycle reasoning, durable reaction truth, and compatibility projection."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from src.reading_core.book_document import BookChapter, ParagraphRecord

from .llm_calls import (
    _clean_text,
)
from .schemas import (
    AnchorRecord,
    AnchoredReactionRecord,
    OutsideLink,
    PriorLink,
    ReactionAnchor,
    ReactionCandidate,
    ReactionRecordsState,
    SearchIntent,
    SurfacedReaction,
    SourceRef,
)
from .storage import chapter_result_compatibility_file, save_json
from .source_spans import source_ref_from_span


_FEATURED_PRIORITY = {
    "highlight": 0,
    "discern": 1,
    "association": 2,
    "retrospect": 3,
    "curious": 4,
}
_REFLECTIVE_BUCKETS = {
    "chapter_understandings",
    "book_level_frames",
    "durable_definitions",
    "stabilized_motifs",
    "resolved_questions_of_record",
    "chapter_end_notes",
}
_COMPAT_FAMILIES = {"highlight", "discern", "association", "retrospect", "curious", "silent"}
_SLOW_CYCLE_AUDIT_SCHEMA = "attentional_v2.slow_cycle_audit.v1"


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_reaction_anchor(anchor: AnchorRecord | dict[str, object]) -> ReactionAnchor:
    """Project one retained anchor into the embedded durable-reaction anchor shape."""

    locator = anchor.get("locator")
    return {
        "anchor_id": _clean_text(anchor.get("anchor_id")),
        "sentence_start_id": _clean_text(anchor.get("sentence_start_id")),
        "sentence_end_id": _clean_text(anchor.get("sentence_end_id") or anchor.get("sentence_start_id")),
        "quote": _clean_text(anchor.get("quote")),
        "locator": dict(locator) if isinstance(locator, dict) else {},
    }


def build_reaction_source_ref(value: SourceRef | dict[str, object]) -> SourceRef:
    """Project a source ref into the embedded durable-reaction source-ref shape."""

    if not isinstance(value, dict):
        return source_ref_from_span({}, quote="", role="reaction_anchor")
    source_span = value.get("source_span")
    return source_ref_from_span(
        source_span if isinstance(source_span, Mapping) else {},
        quote=_clean_text(value.get("quote")),
        role=_clean_text(value.get("role")) or "reaction_anchor",
        resolution=value.get("resolution") if isinstance(value.get("resolution"), Mapping) else None,
    )


def _source_ref_from_legacy_anchor(anchor: AnchorRecord | dict[str, object]) -> SourceRef:
    """Best-effort adapter for old tests and historical callers."""

    locator = anchor.get("locator")
    source_span = locator.get("source_span") if isinstance(locator, Mapping) else {}
    return source_ref_from_span(
        source_span if isinstance(source_span, Mapping) else {},
        quote=_clean_text(anchor.get("quote")),
        role="reaction_anchor",
        resolution={"status": "legacy_anchor_projection"},
    )


def _copy_prior_link(value: object) -> PriorLink | None:
    """Normalize one surfaced prior-link payload when present."""

    if not isinstance(value, Mapping):
        return None
    ref_ids = [_clean_text(item) for item in value.get("ref_ids", []) if _clean_text(item)]
    relation = _clean_text(value.get("relation"))
    note = _clean_text(value.get("note"))
    if not (ref_ids or relation or note):
        return None
    payload: PriorLink = {}
    if ref_ids:
        payload["ref_ids"] = ref_ids
    if relation:
        payload["relation"] = relation
    if note:
        payload["note"] = note
    return payload


def _copy_outside_link(value: object) -> OutsideLink | None:
    """Normalize one surfaced outside-link payload when present."""

    if not isinstance(value, Mapping):
        return None
    kind = _clean_text(value.get("kind"))
    label = _clean_text(value.get("label"))
    note = _clean_text(value.get("note"))
    if not (kind or label or note):
        return None
    payload: OutsideLink = {}
    if kind:
        payload["kind"] = kind
    if label:
        payload["label"] = label
    if note:
        payload["note"] = note
    return payload


def _copy_search_intent(value: object) -> SearchIntent | None:
    """Normalize one surfaced search-intent payload when present."""

    if not isinstance(value, Mapping):
        return None
    query = _clean_text(value.get("query"))
    rationale = _clean_text(value.get("rationale"))
    if not (query or rationale):
        return None
    payload: SearchIntent = {}
    if query:
        payload["query"] = query
    if rationale:
        payload["rationale"] = rationale
    return payload


def _surfaced_reaction_from_candidate(reaction: ReactionCandidate) -> SurfacedReaction | None:
    """Project one legacy reaction candidate into the surfaced-reaction truth shape."""

    content = _clean_text(reaction.get("content"))
    source_quote = _clean_text(reaction.get("source_quote") or reaction.get("anchor_quote"))
    if not (content and source_quote):
        return None
    return {
        "source_quote": source_quote,
        "content": content,
        "prior_link": None,
        "outside_link": None,
        "search_intent": _legacy_search_intent_from_candidate(reaction),
    }


def compat_reaction_family(payload: Mapping[str, object]) -> str:
    """Derive the legacy family label from one native persisted reaction shape."""

    if _copy_search_intent(payload.get("search_intent")) is not None:
        return "curious"
    if _copy_prior_link(payload.get("prior_link")) is not None:
        return "retrospect"
    if _copy_outside_link(payload.get("outside_link")) is not None:
        return "association"

    compat_family = _clean_text(payload.get("compat_family"))
    if compat_family == "silent":
        return "silent"
    if compat_family in _COMPAT_FAMILIES and compat_family != "silent":
        return compat_family

    explicit_type = _clean_text(payload.get("type"))
    if explicit_type == "silent":
        return "silent"
    if explicit_type in _COMPAT_FAMILIES and explicit_type != "silent":
        return explicit_type

    thought = _clean_text(payload.get("thought")) or _clean_text(payload.get("content"))
    source_quote = _clean_text(payload.get("source_quote") or payload.get("anchor_quote"))
    if thought and len(thought) <= max(120, len(source_quote) + 60):
        return "highlight"
    if thought:
        return "discern"
    return "highlight"


def compat_search_query(payload: Mapping[str, object]) -> str:
    """Project the legacy search-query sidecar from native surfaced fields."""

    search_intent = _copy_search_intent(payload.get("search_intent"))
    if search_intent is not None:
        return _clean_text(search_intent.get("query"))
    return _clean_text(payload.get("search_query"))


def _legacy_search_intent_from_candidate(reaction: ReactionCandidate) -> SearchIntent | None:
    """Project a legacy curious payload into the native surfaced search-intent shape."""

    query = _clean_text(reaction.get("search_query"))
    if not query:
        return None
    return {
        "query": query,
        "rationale": "",
    }


def derive_reaction_id(
    *,
    chapter_ref: str,
    emitted_at_source_span_id: str,
    reaction_type: str,
    ordinal: int | None = None,
) -> str:
    """Build a deterministic durable-reaction id from chapter, source span, and type."""

    parts = [
        "rx",
        _clean_text(chapter_ref).replace(" ", "_") or "chapter",
        _clean_text(emitted_at_source_span_id) or "source",
        _clean_text(reaction_type) or "reaction",
    ]
    if ordinal is not None and ordinal > 0:
        parts.append(str(int(ordinal)))
    return ":".join(parts)


def build_reaction_record(
    *,
    reaction: ReactionCandidate,
    primary_source_ref: SourceRef | dict[str, object] | None = None,
    related_source_refs: list[SourceRef | dict[str, object]] | None = None,
    primary_anchor: AnchorRecord | dict[str, object] | None = None,
    related_anchors: list[AnchorRecord | dict[str, object]] | None = None,
    chapter_id: int,
    chapter_ref: str,
    emitted_at_source_span_id: str = "",
    emitted_at_sentence_id: str = "",
    reaction_id: str | None = None,
    supersedes_reaction_id: str | None = None,
    compatibility_section_ref: str | None = None,
    created_at: str | None = None,
    ordinal: int | None = None,
    record_source: str = "legacy_builder",
) -> AnchoredReactionRecord:
    """Compatibility adapter from legacy candidates into the surfaced-native record builder."""

    surfaced_reaction = _surfaced_reaction_from_candidate(reaction)
    if surfaced_reaction is None:
        raise ValueError("legacy reaction candidate must contain anchor_quote and content")
    record = build_reaction_record_from_surfaced_reaction(
        reaction=surfaced_reaction,
        primary_source_ref=primary_source_ref,
        related_source_refs=related_source_refs,
        primary_anchor=primary_anchor,
        related_anchors=related_anchors,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        emitted_at_source_span_id=emitted_at_source_span_id or emitted_at_sentence_id,
        reaction_id=reaction_id,
        supersedes_reaction_id=supersedes_reaction_id,
        compatibility_section_ref=compatibility_section_ref,
        created_at=created_at,
        ordinal=ordinal,
        compat_family_override=_clean_text(reaction.get("type")),
    )
    if record is None:
        raise ValueError("legacy reaction candidate could not be converted into a surfaced reaction")
    record["record_source"] = _clean_text(record_source) or "legacy_candidate_adapter"
    record["search_results"] = [
        dict(item)
        for item in reaction.get("search_results", [])
        if isinstance(item, dict)
    ] if isinstance(reaction.get("search_results"), list) else []
    record["search_query"] = compat_search_query({"search_intent": record.get("search_intent"), "search_query": reaction.get("search_query")})
    return record


def build_reaction_record_from_surfaced_reaction(
    *,
    reaction: SurfacedReaction,
    primary_source_ref: SourceRef | dict[str, object] | None = None,
    related_source_refs: list[SourceRef | dict[str, object]] | None = None,
    primary_anchor: AnchorRecord | dict[str, object] | None = None,
    related_anchors: list[AnchorRecord | dict[str, object]] | None = None,
    chapter_id: int,
    chapter_ref: str,
    emitted_at_source_span_id: str = "",
    emitted_at_sentence_id: str = "",
    reaction_id: str | None = None,
    supersedes_reaction_id: str | None = None,
    compatibility_section_ref: str | None = None,
    created_at: str | None = None,
    ordinal: int | None = None,
    compat_family_override: str | None = None,
) -> AnchoredReactionRecord | None:
    """Build one native persisted reaction record directly from Digest-owned surfaced output."""

    normalized_primary_source_ref = (
        build_reaction_source_ref(primary_source_ref)
        if isinstance(primary_source_ref, dict)
        else _source_ref_from_legacy_anchor(primary_anchor or {})
    )
    thought = _clean_text(reaction.get("content"))
    source_quote = _clean_text(reaction.get("source_quote") or reaction.get("anchor_quote")) or _clean_text(
        normalized_primary_source_ref.get("quote")
    )
    if not (thought or source_quote):
        return None

    normalized_related = [
        build_reaction_source_ref(ref)
        for ref in (related_source_refs or [])
        if isinstance(ref, dict)
    ]
    if not normalized_related and related_anchors:
        normalized_related = [_source_ref_from_legacy_anchor(anchor) for anchor in related_anchors if isinstance(anchor, dict)]
    prior_link = _copy_prior_link(reaction.get("prior_link"))
    outside_link = _copy_outside_link(reaction.get("outside_link"))
    search_intent = _copy_search_intent(reaction.get("search_intent"))
    override_family = _clean_text(compat_family_override)
    if override_family not in _COMPAT_FAMILIES:
        override_family = ""
    compat_payload = {
        "content": thought,
        "source_quote": source_quote,
        "prior_link": prior_link,
        "outside_link": outside_link,
        "search_intent": search_intent,
    }
    digest_kind = _clean_text(reaction.get("kind")).lower()
    if override_family:
        compat_family = override_family
    elif prior_link is not None or outside_link is not None or search_intent is not None:
        compat_family = compat_reaction_family(compat_payload)
    elif digest_kind == "highlight":
        compat_family = "highlight"
    elif digest_kind == "note":
        compat_family = "association"
    else:
        compat_family = compat_reaction_family(compat_payload)

    return {
        "reaction_id": reaction_id
        or derive_reaction_id(
            chapter_ref=chapter_ref,
            emitted_at_source_span_id=emitted_at_source_span_id or emitted_at_sentence_id,
            reaction_type=compat_family,
            ordinal=ordinal,
        ),
        "chapter_id": int(chapter_id),
        "chapter_ref": _clean_text(chapter_ref),
        "emitted_at_source_span_id": _clean_text(emitted_at_source_span_id or emitted_at_sentence_id),
        "record_source": "read_surface",
        "type": compat_family,  # type: ignore[typeddict-item]
        "compat_family": compat_family,  # type: ignore[typeddict-item]
        "marginalia_kind": digest_kind if digest_kind in {"highlight", "note"} else "",
        "thought": thought,
        "source_quote": source_quote,
        "primary_source_ref": normalized_primary_source_ref,
        "related_source_refs": normalized_related,
        "supersedes_reaction_id": _clean_text(supersedes_reaction_id),
        "compatibility_section_ref": _clean_text(compatibility_section_ref),
        "prior_link": prior_link,
        "outside_link": outside_link,
        "search_intent": search_intent,
        "search_query": compat_search_query({"search_intent": search_intent}),
        "search_results": [],
        "created_at": created_at or _timestamp(),
    }


def reaction_records_for_chapter(
    state: ReactionRecordsState,
    *,
    chapter_ref: str,
) -> list[AnchoredReactionRecord]:
    """Return one chapter's durable visible reactions in persisted order."""

    return [
        dict(record)
        for record in state.get("records", [])
        if isinstance(record, dict) and _clean_text(record.get("chapter_ref")) == _clean_text(chapter_ref)
    ]


def _target_locator_from_source_ref(source_ref: SourceRef | dict[str, object]) -> dict[str, object] | None:
    """Project one source ref into the current target-locator shape when EPUB CFI is available."""

    locator = source_ref.get("locator")
    if not isinstance(locator, dict):
        return None
    href = _clean_text(locator.get("href"))
    match_text = _clean_text(source_ref.get("quote"))
    if not href or not match_text:
        return None
    return {
        "href": href,
        "start_cfi": locator.get("start_cfi"),
        "end_cfi": locator.get("end_cfi"),
        "match_text": match_text,
        "match_mode": "exact",
    }


def _compatibility_section_ref(
    record: AnchoredReactionRecord | dict[str, object],
    *,
    chapter_id: int,
) -> str:
    """Resolve the current temporary section-ref compatibility sidecar."""

    explicit = _clean_text(record.get("compatibility_section_ref"))
    if explicit:
        return explicit
    primary_source_ref = record.get("primary_source_ref")
    if isinstance(primary_source_ref, dict):
        source_span = primary_source_ref.get("source_span")
        if isinstance(source_span, dict):
            start = source_span.get("start_cursor")
            if isinstance(start, dict):
                paragraph_index = int(start.get("paragraph_index", 0) or 0)
                if paragraph_index > 0:
                    return f"{int(chapter_id)}.{paragraph_index}"
    return f"{int(chapter_id)}.1"


def _paragraph_locator(paragraph: ParagraphRecord | dict[str, object]) -> dict[str, object] | None:
    """Project one canonical paragraph into the current section-locator shape."""

    href = _clean_text(paragraph.get("href"))
    paragraph_index = int(paragraph.get("paragraph_index", 0) or 0)
    if not href or paragraph_index <= 0:
        return None
    return {
        "href": href,
        "start_cfi": paragraph.get("start_cfi"),
        "end_cfi": paragraph.get("end_cfi"),
        "paragraph_start": paragraph_index,
        "paragraph_end": paragraph_index,
    }


def _section_summary(record: AnchoredReactionRecord | dict[str, object], paragraph_index: int | None = None) -> str:
    """Build one compact temporary section summary for compatibility payloads."""

    thought = _clean_text(record.get("thought"))
    if thought:
        return thought[:160]
    if paragraph_index and paragraph_index > 0:
        return f"Anchored reactions around paragraph {paragraph_index}."
    return "Anchored reactions."


def project_chapter_result_compatibility(
    *,
    book_id: str,
    chapter: BookChapter | dict[str, object],
    reaction_records: list[AnchoredReactionRecord] | ReactionRecordsState,
    output_language: str,
    output_dir: Path | None = None,
    persist: bool = False,
) -> dict[str, object]:
    """Project mechanism-authored reactions into the current chapter_result-compatible shape."""

    chapter_id = int(chapter.get("id", 0) or 0)
    chapter_ref = _clean_text(chapter.get("reference") or chapter.get("chapter_ref") or f"Chapter {chapter_id}")
    chapter_title = _clean_text(chapter.get("title"))
    chapter_heading = dict(chapter.get("chapter_heading", {})) if isinstance(chapter.get("chapter_heading"), dict) else None
    paragraphs = [
        dict(paragraph)
        for paragraph in chapter.get("paragraphs", [])
        if isinstance(paragraph, dict)
    ]
    paragraphs_by_index = {
        int(paragraph.get("paragraph_index", 0) or 0): paragraph
        for paragraph in paragraphs
        if int(paragraph.get("paragraph_index", 0) or 0) > 0
    }

    records = (
        [dict(item) for item in reaction_records.get("records", []) if isinstance(item, dict)]
        if isinstance(reaction_records, dict) and "records" in reaction_records
        else [dict(item) for item in reaction_records if isinstance(item, dict)]
    )
    records = [
        record
        for record in records
        if _clean_text(record.get("chapter_ref")) == chapter_ref and compat_reaction_family(record) != "silent"
    ]

    section_groups: dict[str, dict[str, object]] = {}
    reaction_counts: Counter[str] = Counter()
    featured_candidates: list[dict[str, object]] = []

    for record in records:
        primary_source_ref = record.get("primary_source_ref")
        if not isinstance(primary_source_ref, dict):
            continue
        section_ref = _compatibility_section_ref(record, chapter_id=chapter_id)
        paragraph_index = 0
        source_span = primary_source_ref.get("source_span")
        if isinstance(source_span, dict) and isinstance(source_span.get("start_cursor"), dict):
            paragraph_index = int(source_span["start_cursor"].get("paragraph_index", 0) or 0)
        paragraph = paragraphs_by_index.get(paragraph_index, {})
        section = section_groups.get(section_ref)
        if section is None:
            section = {
                "segment_id": f"compat:{section_ref}",
                "segment_ref": section_ref,
                "summary": _section_summary(record, paragraph_index=paragraph_index or None),
                "original_text": _clean_text(paragraph.get("text")),
                "verdict": "keep",
                "quality_status": "kept",
                "reflection_summary": "",
                "reflection_reason_codes": [],
                "marginalia": [],
                "reactions": [],
            }
            paragraph_locator = _paragraph_locator(paragraph)
            if paragraph_locator is not None:
                section["locator"] = paragraph_locator
            section_groups[section_ref] = section

        target_locator = _target_locator_from_source_ref(primary_source_ref)
        reaction_type = compat_reaction_family(record)
        reaction_card = {
            "reaction_id": _clean_text(record.get("reaction_id")),
            "type": reaction_type,
            "source_quote": _clean_text(record.get("source_quote") or primary_source_ref.get("quote")),
            "content": _clean_text(record.get("thought")),
            "search_query": compat_search_query(record),
            "search_results": [
                dict(item)
                for item in record.get("search_results", [])
                if isinstance(item, dict)
            ]
            if isinstance(record.get("search_results"), list)
            else [],
            "primary_source_ref": build_reaction_source_ref(primary_source_ref),
            "related_source_refs": [
                build_reaction_source_ref(source_ref)
                for source_ref in record.get("related_source_refs", [])
                if isinstance(source_ref, dict)
            ]
            if isinstance(record.get("related_source_refs"), list)
            else [],
            "supersedes_reaction_id": _clean_text(record.get("supersedes_reaction_id")) or None,
        }
        if target_locator is not None:
            reaction_card["target_locator"] = target_locator
        section["marginalia"].append(reaction_card)
        section["reactions"].append(reaction_card)
        reaction_counts[reaction_type] += 1
        featured_candidates.append(
            {
                "reaction_id": _clean_text(record.get("reaction_id")),
                "type": reaction_type,
                "segment_ref": section_ref,
                "source_quote": _clean_text(record.get("source_quote") or primary_source_ref.get("quote")),
                "content": _clean_text(record.get("thought")),
                "target_locator": target_locator or {},
                "primary_source_ref": build_reaction_source_ref(primary_source_ref),
                "related_source_refs": [
                    build_reaction_source_ref(source_ref)
                    for source_ref in record.get("related_source_refs", [])
                    if isinstance(source_ref, dict)
                ]
                if isinstance(record.get("related_source_refs"), list)
                else [],
                "supersedes_reaction_id": _clean_text(record.get("supersedes_reaction_id")) or None,
            }
        )

    sections = sorted(section_groups.values(), key=lambda item: str(item.get("segment_ref", "")))
    featured = sorted(
        featured_candidates,
        key=lambda item: (
            _FEATURED_PRIORITY.get(str(item.get("type", "")), 99),
            str(item.get("segment_ref", "")),
            str(item.get("reaction_id", "")),
        ),
    )[:3]
    payload = {
        "book_id": book_id,
        "chapter": {
            "id": chapter_id,
            "title": chapter_title,
            "reference": chapter_ref,
            "status": "completed",
        },
        "chapter_heading": chapter_heading,
        "output_language": output_language,
        "generated_at": _timestamp(),
        "sections": sections,
        "chapter_reflection": {},
        "featured_marginalia": featured,
        "featured_reactions": featured,
        "visible_marginalia_count": sum(len(section.get("marginalia", section.get("reactions", []))) for section in sections),
        "visible_reaction_count": sum(len(section.get("reactions", [])) for section in sections),
        "marginalia_type_diversity": len(reaction_counts),
        "reaction_type_diversity": len(reaction_counts),
        "ui_summary": {
            "kept_section_count": len(sections),
            "skipped_section_count": 0,
            "marginalia_counts": dict(sorted(reaction_counts.items())),
            "reaction_counts": dict(sorted(reaction_counts.items())),
        },
    }
    if persist and output_dir is not None:
        save_json(chapter_result_compatibility_file(output_dir, chapter_id), payload)
    return payload
