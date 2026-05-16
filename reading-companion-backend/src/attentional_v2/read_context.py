"""Deterministic carry-forward and supplemental-context helpers."""

from __future__ import annotations

from collections.abc import Mapping

from src.reading_core import BookDocument

from .schemas import (
    CarryForwardContext,
    CarryForwardRef,
    ConceptRegistryState,
    ContextRequest,
    ReactionRecordsState,
    ReaderPolicy,
    ReflectiveFramesState,
    SourceRef,
    ThreadTraceState,
)
from .source_spans import dedupe_source_refs, source_unit_from_span
from .state_projection import build_carry_forward_context, clean_text, matching_chapter_items  # noqa: F401

_LOOK_BACK_RETRIEVAL_INTENT = "source_calibration"
_ACTIVE_RECALL_RETRIEVAL_INTENT = "memory_recovery"
_LOOK_BACK_RESULT_BOUNDARY = "source_refs_and_excerpts"
_ACTIVE_RECALL_RESULT_BOUNDARY = "settled_memory_refs_and_visible_trace_refs"
_VISIBLE_TRACE_RESULT_ROLE = "visible_trace"


def _dedupe_ref_items(items: list[dict[str, object]], *, id_key: str) -> list[dict[str, object]]:
    """Return one order-preserving deduplicated list of dict items."""

    seen: set[str] = set()
    deduped: list[dict[str, object]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = clean_text(item.get(id_key))
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        deduped.append(dict(item))
    return deduped


def _retrieval_event(
    *,
    kind: str,
    retrieval_intent: str,
    result_boundary: str,
    result_groups: list[str],
) -> dict[str, object]:
    """Return one compact supplemental-retrieval contract event."""

    return {
        "kind": kind,
        "retrieval_intent": retrieval_intent,
        "result_boundary": result_boundary,
        "result_groups": list(result_groups),
    }


def _actual_result_groups(*items_by_group: tuple[str, object]) -> list[str]:
    """Return result groups that are actually present in this retrieval result."""

    groups: list[str] = []
    for group, items in items_by_group:
        if isinstance(items, list) and items:
            groups.append(group)
    return groups


def _retrieval_events_from_context(context: dict[str, object]) -> list[dict[str, object]]:
    """Extract compact retrieval events from one supplemental context."""

    raw_events = context.get("retrieval_events")
    events: list[dict[str, object]] = []
    if isinstance(raw_events, list):
        events = [
            dict(item)
            for item in raw_events
            if isinstance(item, dict)
        ]
    if events:
        return events
    retrieval_intent = clean_text(context.get("retrieval_intent"))
    result_boundary = clean_text(context.get("result_boundary"))
    kind = clean_text(context.get("kind"))
    raw_result_groups = context.get("result_groups")
    result_groups: list[str] = []
    if isinstance(raw_result_groups, list):
        result_groups = [
            clean_text(item)
            for item in raw_result_groups
            if clean_text(item)
        ]
    if not retrieval_intent and not result_boundary and not result_groups:
        return []
    return [
        _retrieval_event(
            kind=kind,
            retrieval_intent=retrieval_intent,
            result_boundary=result_boundary,
            result_groups=result_groups,
        )
    ]


def _union_result_groups(events: list[dict[str, object]]) -> list[str]:
    """Return an order-preserving union of result groups from retrieval events."""

    groups: list[str] = []
    seen: set[str] = set()
    for event in events:
        raw_groups = event.get("result_groups")
        if not isinstance(raw_groups, list):
            continue
        for raw_group in raw_groups:
            group = clean_text(raw_group)
            if not group or group in seen:
                continue
            seen.add(group)
            groups.append(group)
    return groups


def merge_supplemental_contexts(
    existing: dict[str, object] | None,
    addition: dict[str, object] | None,
) -> dict[str, object] | None:
    """Merge one newly resolved supplemental context into the accumulated bundle."""

    if not isinstance(existing, dict) or not existing:
        return dict(addition or {}) if isinstance(addition, dict) else None
    if not isinstance(addition, dict) or not addition:
        return dict(existing)

    retrieval_events = _retrieval_events_from_context(existing) + _retrieval_events_from_context(addition)
    retrieval_kinds = {
        clean_text(event.get("kind"))
        for event in retrieval_events
        if clean_text(event.get("kind"))
    }
    merged: dict[str, object] = {
        "kind": "supplemental_bundle",
        "reason": " | ".join(
            reason
            for reason in (clean_text(existing.get("reason")), clean_text(addition.get("reason")))
            if reason
        ),
        "refs": _dedupe_ref_items(
            [dict(item) for item in existing.get("refs", []) if isinstance(item, dict)]
            + [dict(item) for item in addition.get("refs", []) if isinstance(item, dict)],
            id_key="ref_id",
        ),
    }
    if retrieval_events:
        merged["retrieval_events"] = retrieval_events
        merged["result_groups"] = _union_result_groups(retrieval_events)
        if len(retrieval_kinds) > 1:
            merged["retrieval_intent"] = "mixed"
            merged["result_boundary"] = "supplemental_bundle"
        else:
            first_event = retrieval_events[0]
            merged["retrieval_intent"] = clean_text(first_event.get("retrieval_intent"))
            merged["result_boundary"] = clean_text(first_event.get("result_boundary"))
    for key, id_key in (
        ("source_refs", "source_span_id"),
        ("concepts", "concept_key"),
        ("threads", "thread_key"),
        ("reactions", "reaction_id"),
        ("reflective_items", "item_id"),
        ("excerpts", "ref_id"),
    ):
        merged_items = _dedupe_ref_items(
            [dict(item) for item in existing.get(key, []) if isinstance(item, dict)]
            + [dict(item) for item in addition.get(key, []) if isinstance(item, dict)],
            id_key=id_key,
        )
        if merged_items:
            merged[key] = merged_items
    return merged


def _linked_keys_from_digest(
    carry_forward_context: CarryForwardContext,
    *,
    digest_key: str,
    id_key: str,
) -> set[str]:
    """Return ids already present in the carried-forward digest."""

    return {
        clean_text(item.get(id_key))
        for item in carry_forward_context.get(digest_key, [])
        if isinstance(item, dict) and clean_text(item.get(id_key))
    }


def _source_refs(value: object) -> list[SourceRef]:
    return dedupe_source_refs(value)


def _chapter_for_source_span(book_document: BookDocument, source_span: Mapping[str, object]) -> dict[str, object] | None:
    start = source_span.get("start_cursor")
    if not isinstance(start, Mapping):
        return None
    chapter_id = int(start.get("chapter_id", 0) or 0)
    chapter_ref = clean_text(start.get("chapter_ref"))
    for chapter in book_document.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        if chapter_id and int(chapter.get("id", 0) or 0) == chapter_id:
            return chapter
        if chapter_ref and clean_text(chapter.get("reference") or chapter.get("title")) == chapter_ref:
            return chapter
    return None


def _excerpt_for_source_ref(book_document: BookDocument, source_ref: Mapping[str, object]) -> dict[str, object] | None:
    source_span = source_ref.get("source_span")
    if not isinstance(source_span, Mapping):
        return None
    chapter = _chapter_for_source_span(book_document, source_span)
    if chapter is None:
        return None
    source_unit = source_unit_from_span(chapter=chapter, source_span=source_span)
    if not clean_text(source_unit.get("source_text")):
        return None
    source_span_id = clean_text(source_ref.get("source_span_id") or source_unit.get("source_span_id"))
    return {
        "ref_id": f"source:{source_span_id}",
        "source_span_id": source_span_id,
        "source_span": dict(source_unit.get("source_span", {})),
        "quote": clean_text(source_ref.get("quote")) or clean_text(source_unit.get("source_text")),
        "text": clean_text(source_unit.get("source_text")),
        "chapter_ref": clean_text(chapter.get("reference") or chapter.get("title")),
    }


def _requested_source_refs(context_request: ContextRequest, carry_forward_context: CarryForwardContext) -> list[SourceRef]:
    requested_ids = {
        clean_text(item)
        for item in context_request.get("source_ref_ids", [])
        if clean_text(item)
    }
    refs: list[dict[str, object]] = []
    for ref in carry_forward_context.get("refs", []):
        if not isinstance(ref, dict) or not isinstance(ref.get("source_ref"), dict):
            continue
        source_ref = dict(ref["source_ref"])
        source_span_id = clean_text(source_ref.get("source_span_id"))
        if not requested_ids or source_span_id in requested_ids or clean_text(ref.get("ref_id")) in requested_ids:
            refs.append(source_ref)
    for span in context_request.get("source_spans", []):
        if isinstance(span, dict):
            refs.append({"source_span": dict(span), "source_span_id": clean_text(span.get("source_span_id")), "quote": "", "role": "look_back"})
    return dedupe_source_refs(refs)[:4]


def resolve_context_request(
    *,
    context_request: ContextRequest,
    carry_forward_context: CarryForwardContext,
    book_document: BookDocument,
    chapter_ref: str,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    reaction_records: ReactionRecordsState,
    reader_policy: ReaderPolicy | None = None,
    current_unit_sentence_ids: list[str] | None = None,
) -> dict[str, object] | None:
    """Resolve one bounded supplemental-context request against persisted state."""

    _ = (reader_policy, current_unit_sentence_ids, reflective_frames, chapter_ref)
    kind = clean_text(context_request.get("kind"))
    reason = clean_text(context_request.get("reason"))

    if kind == "look_back":
        source_refs = _requested_source_refs(context_request, carry_forward_context)
        excerpts = [
            excerpt
            for excerpt in (_excerpt_for_source_ref(book_document, source_ref) for source_ref in source_refs)
            if excerpt is not None
        ]
        if not excerpts:
            return None
        source_refs_payload = [dict(ref) for ref in source_refs]
        refs = [
            {
                "ref_id": excerpt["ref_id"],
                "kind": "source",
                "source_span_id": excerpt["source_span_id"],
                "summary": clean_text(excerpt.get("quote")),
            }
            for excerpt in excerpts
        ]
        result_groups = _actual_result_groups(
            ("source_refs", source_refs_payload),
            ("excerpts", excerpts),
            ("refs", refs),
        )
        retrieval_event = _retrieval_event(
            kind="look_back",
            retrieval_intent=_LOOK_BACK_RETRIEVAL_INTENT,
            result_boundary=_LOOK_BACK_RESULT_BOUNDARY,
            result_groups=result_groups,
        )
        return {
            "kind": "look_back",
            "reason": reason,
            "retrieval_intent": _LOOK_BACK_RETRIEVAL_INTENT,
            "result_boundary": _LOOK_BACK_RESULT_BOUNDARY,
            "result_groups": result_groups,
            "retrieval_events": [retrieval_event],
            "source_refs": source_refs_payload,
            "excerpts": excerpts,
            "refs": refs,
        }

    if kind != "active_recall":
        return None

    carry_concept_keys = _linked_keys_from_digest(carry_forward_context, digest_key="concept_digest", id_key="concept_key")
    carry_thread_keys = _linked_keys_from_digest(carry_forward_context, digest_key="thread_digest", id_key="thread_key")
    concepts = [
        {
            "ref_id": f"concept:{clean_text(entry.get('concept_key'))}",
            "concept_key": clean_text(entry.get("concept_key")),
            "concept_type": clean_text(entry.get("concept_type")),
            "status": clean_text(entry.get("status")),
            "summary": clean_text(entry.get("summary")),
            "source_refs": _source_refs(entry.get("source_refs"))[:4],
            "linked_thread_ids": [
                clean_text(thread_id)
                for thread_id in entry.get("linked_thread_ids", [])
                if clean_text(thread_id)
            ][:4],
        }
        for entry in concept_registry.get("entries", [])
        if isinstance(entry, dict)
        and clean_text(entry.get("concept_key"))
        and clean_text(entry.get("concept_key")) not in carry_concept_keys
    ][:4]
    threads = [
        {
            "ref_id": f"thread:{clean_text(entry.get('thread_key'))}",
            "thread_key": clean_text(entry.get("thread_key")),
            "thread_type": clean_text(entry.get("thread_type")),
            "status": clean_text(entry.get("status")),
            "summary": clean_text(entry.get("summary")),
            "source_refs": _source_refs(entry.get("source_refs"))[:4],
            "linked_concept_keys": [
                clean_text(concept_key)
                for concept_key in entry.get("linked_concept_keys", [])
                if clean_text(concept_key)
            ][:4],
        }
        for entry in thread_trace.get("entries", [])
        if isinstance(entry, dict)
        and clean_text(entry.get("thread_key"))
        and clean_text(entry.get("thread_key")) not in carry_thread_keys
    ][:4]
    reactions = [
        {
            "ref_id": f"reaction:{clean_text(record.get('reaction_id'))}",
            "reaction_id": clean_text(record.get("reaction_id")),
            "type": clean_text(record.get("type")),
            "thought": clean_text(record.get("thought")),
            "primary_source_ref": dict(record.get("primary_source_ref", {}))
            if isinstance(record.get("primary_source_ref"), dict)
            else {},
            "source_quote": clean_text(record.get("source_quote")),
            "result_role": _VISIBLE_TRACE_RESULT_ROLE,
            "semantic_memory": False,
        }
        for record in reaction_records.get("records", [])[-4:]
        if isinstance(record, dict) and clean_text(record.get("reaction_id"))
    ]
    if not any((concepts, threads, reactions)):
        return None
    refs: list[CarryForwardRef] = []
    refs.extend(
        {
            "ref_id": clean_text(item.get("ref_id")),
            "kind": "concept",
            "item_id": clean_text(item.get("concept_key")),
            "summary": clean_text(item.get("summary")),
            "source_ref": (_source_refs(item.get("source_refs")) or [{}])[0],
            "source_span_id": clean_text((_source_refs(item.get("source_refs")) or [{}])[0].get("source_span_id")),
        }
        for item in concepts
    )
    refs.extend(
        {
            "ref_id": clean_text(item.get("ref_id")),
            "kind": "thread",
            "item_id": clean_text(item.get("thread_key")),
            "summary": clean_text(item.get("summary")),
            "source_ref": (_source_refs(item.get("source_refs")) or [{}])[0],
            "source_span_id": clean_text((_source_refs(item.get("source_refs")) or [{}])[0].get("source_span_id")),
        }
        for item in threads
    )
    refs.extend(
        {
            "ref_id": clean_text(item.get("ref_id")),
            "kind": "reaction",
            "item_id": clean_text(item.get("reaction_id")),
            "summary": clean_text(item.get("thought")),
            "source_ref": dict(item.get("primary_source_ref", {})) if isinstance(item.get("primary_source_ref"), dict) else {},
            "source_span_id": clean_text((item.get("primary_source_ref") or {}).get("source_span_id"))
            if isinstance(item.get("primary_source_ref"), dict)
            else "",
            "result_role": _VISIBLE_TRACE_RESULT_ROLE,
            "semantic_memory": False,
        }
        for item in reactions
    )
    refs_payload = [dict(ref) for ref in refs if isinstance(ref, dict)]
    result_groups = _actual_result_groups(
        ("concepts", concepts),
        ("threads", threads),
        ("reactions", reactions),
        ("refs", refs_payload),
    )
    retrieval_event = _retrieval_event(
        kind="active_recall",
        retrieval_intent=_ACTIVE_RECALL_RETRIEVAL_INTENT,
        result_boundary=_ACTIVE_RECALL_RESULT_BOUNDARY,
        result_groups=result_groups,
    )
    return {
        "kind": "active_recall",
        "reason": reason,
        "retrieval_intent": _ACTIVE_RECALL_RETRIEVAL_INTENT,
        "result_boundary": _ACTIVE_RECALL_RESULT_BOUNDARY,
        "result_groups": result_groups,
        "retrieval_events": [retrieval_event],
        "concepts": concepts,
        "threads": threads,
        "reactions": reactions,
        "refs": refs_payload,
    }
