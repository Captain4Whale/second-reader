"""Book-local source skills used by Navigate."""

from __future__ import annotations

import re

from src.reading_core import BookDocument
from src.reading_core.runtime_contracts import SharedRunCursor

from ..schemas import AnchorBankState


def _clean_text(value: object) -> str:
    """Normalize one free-text value."""

    return re.sub(r"\s+", " ", str(value or "")).strip()


def _sentence_id(sentence: dict[str, object]) -> str:
    """Return the sentence id from a sentence-like mapping."""

    return _clean_text(sentence.get("sentence_id") or sentence.get("id"))


def _chapter_ref(chapter: dict[str, object]) -> str:
    """Return the display reference for one chapter."""

    return _clean_text(chapter.get("reference") or chapter.get("title") or f"c{chapter.get('id', '')}")


def paragraph_index(sentence: dict[str, object]) -> int:
    """Return the best-effort paragraph index for one sentence."""

    locator = sentence.get("locator")
    raw_value: object
    if isinstance(locator, dict):
        raw_value = locator.get("paragraph_index", 0) or locator.get("paragraph_start", 0) or 0
    else:
        raw_value = sentence.get("paragraph_index", 0) or 0
    try:
        value = int(raw_value or 0)
    except (TypeError, ValueError):
        return 0
    return value if value > 0 else 0


def sentences_visible_to_mainline(
    chapter: dict[str, object],
    *,
    mainline_cursor: SharedRunCursor,
) -> list[dict[str, object]]:
    """Return the sentence slice visible before the mainline cursor."""

    chapter_id = int(chapter.get("id", 0) or 0)
    mainline_chapter_id = int(mainline_cursor.get("chapter_id", 0) or 0)
    sentences = [dict(sentence) for sentence in chapter.get("sentences", []) if isinstance(sentence, dict)]
    if chapter_id <= 0 or not sentences or mainline_chapter_id <= 0:
        return []
    if chapter_id < mainline_chapter_id:
        return sentences
    if chapter_id > mainline_chapter_id:
        return []
    mainline_sentence_id = _clean_text(mainline_cursor.get("sentence_id"))
    if not mainline_sentence_id:
        return []
    cutoff = next((index for index, sentence in enumerate(sentences) if _sentence_id(sentence) == mainline_sentence_id), -1)
    if cutoff < 0:
        return sentences
    return sentences[:cutoff]


def scope_card(
    *,
    card_id: str,
    label: str,
    summary: str,
    sentences: list[dict[str, object]],
) -> dict[str, object]:
    """Build one structured source-scope card from a bounded sentence slice."""

    return {
        "card_id": card_id,
        "label": label,
        "summary": summary,
        "start_sentence_id": _sentence_id(sentences[0]) if sentences else "",
        "end_sentence_id": _sentence_id(sentences[-1]) if sentences else "",
    }


def build_source_map_overview(
    *,
    document: BookDocument,
    survey_map: dict[str, object],
    mainline_cursor: SharedRunCursor,
) -> dict[str, object]:
    """Build chapter cards over the already-read book space."""

    chapter_summaries = {
        int(entry.get("chapter_id", 0) or 0): dict(entry)
        for entry in survey_map.get("chapter_map", [])
        if isinstance(entry, dict)
    } if isinstance(survey_map.get("chapter_map"), list) else {}
    cards: list[dict[str, object]] = []
    for raw_chapter in document.get("chapters", []):
        if not isinstance(raw_chapter, dict):
            continue
        chapter = dict(raw_chapter)
        chapter_id = int(chapter.get("id", 0) or 0)
        visible_sentences = sentences_visible_to_mainline(chapter, mainline_cursor=mainline_cursor)
        if chapter_id <= 0 or not visible_sentences:
            continue
        chapter_summary = chapter_summaries.get(chapter_id, {})
        opening_sentences = chapter_summary.get("opening_sentences", [])
        summary = ""
        if isinstance(opening_sentences, list) and opening_sentences:
            first_opening = opening_sentences[0]
            if isinstance(first_opening, dict):
                summary = _clean_text(first_opening.get("text"))
        if not summary:
            summary = _clean_text(visible_sentences[0].get("text"))[:180]
        cards.append(
            scope_card(
                card_id=f"chapter:{chapter_id}",
                label=_clean_text(chapter.get("title")) or _chapter_ref(chapter),
                summary=summary,
                sentences=visible_sentences,
            )
        )
    return {
        "scope_kind": "chapter_cards",
        "reason": "source_map_overview",
        "cards": cards,
    }


def _build_section_or_window_scope(
    *,
    chapter: dict[str, object],
    selected_sentences: list[dict[str, object]],
) -> dict[str, object]:
    """Build a second-layer scope from one selected chapter region."""

    heading_indexes = [
        index
        for index, sentence in enumerate(selected_sentences)
        if _clean_text(sentence.get("text_role")) == "section_heading"
    ]
    if heading_indexes:
        cards: list[dict[str, object]] = []
        for offset, start_index in enumerate(heading_indexes):
            end_index = heading_indexes[offset + 1] - 1 if offset + 1 < len(heading_indexes) else len(selected_sentences) - 1
            scope_sentences = selected_sentences[start_index : end_index + 1]
            if not scope_sentences:
                continue
            cards.append(
                scope_card(
                    card_id=f"section:{_sentence_id(scope_sentences[0])}",
                    label=_clean_text(scope_sentences[0].get("text")) or f"Section {offset + 1}",
                    summary=_clean_text(scope_sentences[min(1, len(scope_sentences) - 1)].get("text"))[:180],
                    sentences=scope_sentences,
                )
            )
        if cards:
            return {
                "scope_kind": "section_cards",
                "reason": f"expand_{int(chapter.get('id', 0) or 0)}_sections",
                "cards": cards,
            }

    paragraphs: dict[int, list[dict[str, object]]] = {}
    for sentence in selected_sentences:
        paragraphs.setdefault(paragraph_index(sentence), []).append(sentence)
    ordered_paragraphs = [paragraphs[index] for index in sorted(paragraphs) if paragraphs[index]]
    window_size = 3
    cards = []
    for window_index in range(0, len(ordered_paragraphs), window_size):
        paragraph_window = ordered_paragraphs[window_index : window_index + window_size]
        scope_sentences = [sentence for paragraph in paragraph_window for sentence in paragraph]
        if not scope_sentences:
            continue
        first_paragraph = paragraph_index(scope_sentences[0])
        last_paragraph = paragraph_index(scope_sentences[-1])
        cards.append(
            scope_card(
                card_id=f"paragraph_window:{_sentence_id(scope_sentences[0])}",
                label=f"Paragraphs {first_paragraph}-{last_paragraph}",
                summary=_clean_text(scope_sentences[0].get("text"))[:180],
                sentences=scope_sentences,
            )
        )
    return {
        "scope_kind": "paragraph_window_cards",
        "reason": f"expand_{int(chapter.get('id', 0) or 0)}_paragraph_windows",
        "cards": cards,
    }


def _build_paragraph_preview_scope(*, selected_sentences: list[dict[str, object]]) -> dict[str, object]:
    """Build a final-layer scope as paragraph previews."""

    paragraphs: dict[int, list[dict[str, object]]] = {}
    for sentence in selected_sentences:
        paragraphs.setdefault(paragraph_index(sentence), []).append(sentence)
    cards: list[dict[str, object]] = []
    for index in sorted(paragraphs):
        paragraph_sentences = paragraphs[index]
        if not paragraph_sentences:
            continue
        preview = " ".join(_clean_text(sentence.get("text")) for sentence in paragraph_sentences[:2]).strip()
        cards.append(
            scope_card(
                card_id=f"paragraph:{_sentence_id(paragraph_sentences[0])}",
                label=f"Paragraph {index}",
                summary=preview[:220],
                sentences=paragraph_sentences,
            )
        )
    return {
        "scope_kind": "paragraph_preview_cards",
        "reason": "paragraph_preview_scope",
        "cards": cards,
    }


def drilldown_source_scope(
    *,
    current_scope: dict[str, object],
    selected_sentences: list[dict[str, object]],
    chapter: dict[str, object],
) -> dict[str, object] | None:
    """Expand one source scope into its next finer-grained layer."""

    scope_kind = _clean_text(current_scope.get("scope_kind"))
    if scope_kind == "chapter_cards":
        return _build_section_or_window_scope(chapter=chapter, selected_sentences=selected_sentences)
    if scope_kind in {"section_cards", "paragraph_window_cards"}:
        return _build_paragraph_preview_scope(selected_sentences=selected_sentences)
    return None


def _sentence_range(
    chapter: dict[str, object],
    *,
    start_sentence_id: str,
    end_sentence_id: str,
    mainline_cursor: SharedRunCursor,
) -> tuple[list[dict[str, object]], str | None]:
    """Resolve a visible sentence range inside one chapter."""

    visible_sentences = sentences_visible_to_mainline(chapter, mainline_cursor=mainline_cursor)
    visible_ids = [_sentence_id(sentence) for sentence in visible_sentences]
    if start_sentence_id not in visible_ids or end_sentence_id not in visible_ids:
        return [], "range_outside_visible_scope"
    start_index = visible_ids.index(start_sentence_id)
    end_index = visible_ids.index(end_sentence_id)
    if end_index < start_index:
        return [], "range_order_invalid"
    return visible_sentences[start_index : end_index + 1], None


def resolve_visible_sentence_range(
    *,
    sentence_lookup: dict[str, dict[str, object]],
    chapter_lookup: dict[int, dict[str, object]],
    mainline_cursor: SharedRunCursor,
    start_sentence_id: str,
    end_sentence_id: str,
) -> tuple[dict[str, object] | None, list[dict[str, object]], str | None]:
    """Resolve one same-chapter visible sentence range."""

    start_entry = sentence_lookup.get(start_sentence_id, {})
    end_entry = sentence_lookup.get(end_sentence_id, {})
    start_chapter_id = int(start_entry.get("chapter_id", 0) or 0)
    end_chapter_id = int(end_entry.get("chapter_id", 0) or 0)
    if start_chapter_id <= 0 or start_chapter_id != end_chapter_id:
        return None, [], "range_not_same_chapter"
    chapter = chapter_lookup.get(start_chapter_id)
    if not isinstance(chapter, dict):
        return None, [], "chapter_not_found"
    sentences, error = _sentence_range(
        chapter,
        start_sentence_id=start_sentence_id,
        end_sentence_id=end_sentence_id,
        mainline_cursor=mainline_cursor,
    )
    if error:
        return chapter, [], error
    return chapter, sentences, None


def fetch_source_window(
    *,
    sentence_lookup: dict[str, dict[str, object]],
    chapter_lookup: dict[int, dict[str, object]],
    mainline_cursor: SharedRunCursor,
    start_sentence_id: str,
    end_sentence_id: str,
    context_before: int = 0,
    context_after: int = 0,
) -> tuple[dict[str, object], str | None]:
    """Fetch a visible source window with optional bounded context."""

    chapter, selected_sentences, error = resolve_visible_sentence_range(
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=mainline_cursor,
        start_sentence_id=start_sentence_id,
        end_sentence_id=end_sentence_id,
    )
    if error or chapter is None:
        return {}, error or "range_resolution_failed"

    visible_sentences = sentences_visible_to_mainline(chapter, mainline_cursor=mainline_cursor)
    visible_ids = [_sentence_id(sentence) for sentence in visible_sentences]
    start_index = visible_ids.index(start_sentence_id)
    end_index = visible_ids.index(end_sentence_id)
    window_start = max(0, start_index - max(0, int(context_before or 0)))
    window_end = min(len(visible_sentences) - 1, end_index + max(0, int(context_after or 0)))
    window_sentences = visible_sentences[window_start : window_end + 1]
    return {
        "chapter_id": int(chapter.get("id", 0) or 0),
        "chapter_ref": _chapter_ref(chapter),
        "start_sentence_id": _sentence_id(window_sentences[0]) if window_sentences else start_sentence_id,
        "end_sentence_id": _sentence_id(window_sentences[-1]) if window_sentences else end_sentence_id,
        "requested_range": {
            "start_sentence_id": start_sentence_id,
            "end_sentence_id": end_sentence_id,
        },
        "sentences": [
            {
                "sentence_id": _sentence_id(sentence),
                "text": _clean_text(sentence.get("text")),
                "paragraph_index": paragraph_index(sentence),
                "text_role": _clean_text(sentence.get("text_role")),
            }
            for sentence in window_sentences
        ],
    }, None


def _cards_by_id(scope: dict[str, object]) -> dict[str, dict[str, object]]:
    """Return scope cards keyed by card id."""

    return {
        _clean_text(card.get("card_id")): dict(card)
        for card in scope.get("cards", [])
        if isinstance(card, dict) and _clean_text(card.get("card_id"))
    }


def range_from_skill_arguments(
    arguments: dict[str, object],
    *,
    current_scope: dict[str, object] | None = None,
) -> tuple[str, str]:
    """Resolve a sentence range from skill arguments and current scope cards."""

    card_id = _clean_text(arguments.get("card_id"))
    if card_id and isinstance(current_scope, dict):
        card = _cards_by_id(current_scope).get(card_id)
        if card:
            return _clean_text(card.get("start_sentence_id")), _clean_text(card.get("end_sentence_id"))
    return _clean_text(arguments.get("start_sentence_id")), _clean_text(arguments.get("end_sentence_id"))


def resolve_anchor(
    *,
    anchor_bank: AnchorBankState,
    sentence_lookup: dict[str, dict[str, object]],
    chapter_lookup: dict[int, dict[str, object]],
    mainline_cursor: SharedRunCursor,
    anchor_id: str = "",
    sentence_id: str = "",
    ref_id: str = "",
) -> tuple[dict[str, object], str | None]:
    """Resolve an anchor or sentence handle into source-grounded context."""

    handle = _clean_text(anchor_id or ref_id)
    if handle:
        for anchor in anchor_bank.get("anchor_records", []):
            if not isinstance(anchor, dict):
                continue
            if _clean_text(anchor.get("anchor_id")) != handle:
                continue
            start_sentence_id = _clean_text(anchor.get("sentence_start_id"))
            end_sentence_id = _clean_text(anchor.get("sentence_end_id")) or start_sentence_id
            source_window, error = fetch_source_window(
                sentence_lookup=sentence_lookup,
                chapter_lookup=chapter_lookup,
                mainline_cursor=mainline_cursor,
                start_sentence_id=start_sentence_id,
                end_sentence_id=end_sentence_id,
                context_before=1,
                context_after=1,
            )
            if error:
                return {}, error
            return {
                "anchor_id": handle,
                "quote": _clean_text(anchor.get("quote")),
                "why_it_mattered": _clean_text(anchor.get("why_it_mattered")),
                "source_window": source_window,
            }, None
    sentence_handle = _clean_text(sentence_id or ref_id)
    if sentence_handle:
        source_window, error = fetch_source_window(
            sentence_lookup=sentence_lookup,
            chapter_lookup=chapter_lookup,
            mainline_cursor=mainline_cursor,
            start_sentence_id=sentence_handle,
            end_sentence_id=sentence_handle,
            context_before=1,
            context_after=1,
        )
        if error:
            return {}, error
        return {"sentence_id": sentence_handle, "source_window": source_window}, None
    return {}, "anchor_or_sentence_handle_required"
