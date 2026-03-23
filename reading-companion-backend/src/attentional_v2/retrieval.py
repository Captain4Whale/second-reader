"""Deterministic candidate-generation helpers for attentional_v2."""

from __future__ import annotations

import re

from src.reading_core import BookDocument, SentenceRecord

from .schemas import AnchorMemoryState


def _token_set(text: str) -> set[str]:
    """Return a coarse lexical set for cheap overlap ranking."""

    return {
        token
        for token in re.findall(r"[a-z][a-z'-]{2,}|[\u4e00-\u9fff]{2,}", (text or "").lower())
        if token not in {"the", "and", "for", "with", "this", "that", "from", "into"}
    }


def flatten_sentence_inventory(document: BookDocument) -> list[dict[str, object]]:
    """Flatten the shared sentence inventory into source order."""

    flattened: list[dict[str, object]] = []
    for chapter in document.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        chapter_id = int(chapter.get("id", 0) or 0)
        chapter_title = str(chapter.get("title", "") or "")
        for sentence in chapter.get("sentences", []):
            if not isinstance(sentence, dict):
                continue
            flattened.append(
                {
                    **sentence,
                    "chapter_id": chapter_id,
                    "chapter_title": chapter_title,
                }
            )
    return flattened


def bounded_lookback_source_space(
    document: BookDocument,
    *,
    current_sentence_id: str,
    max_candidates: int = 12,
) -> list[dict[str, object]]:
    """Return a bounded source-space window ending immediately before the current sentence."""

    sentences = flatten_sentence_inventory(document)
    current_index = next(
        (index for index, sentence in enumerate(sentences) if str(sentence.get("sentence_id", "") or "") == current_sentence_id),
        None,
    )
    if current_index is None or current_index <= 0:
        return []
    lower_bound = max(0, current_index - max(1, int(max_candidates)))
    return sentences[lower_bound:current_index]


def generate_candidate_set(
    document: BookDocument,
    *,
    current_sentence_id: str,
    current_text: str,
    anchor_memory: AnchorMemoryState,
    max_memory_candidates: int = 3,
    max_lookback_candidates: int = 12,
) -> dict[str, object]:
    """Generate deterministic bridge candidates without performing bridge judgment."""

    current_tokens = _token_set(current_text)
    memory_candidates: list[dict[str, object]] = []
    for anchor in anchor_memory.get("anchor_records", []):
        if not isinstance(anchor, dict):
            continue
        overlap = len(current_tokens & _token_set(str(anchor.get("quote", "") or "")))
        if overlap <= 0:
            continue
        memory_candidates.append(
            {
                "candidate_kind": "anchor_memory",
                "anchor_id": str(anchor.get("anchor_id", "") or ""),
                "sentence_start_id": str(anchor.get("sentence_start_id", "") or ""),
                "sentence_end_id": str(anchor.get("sentence_end_id", "") or ""),
                "quote": str(anchor.get("quote", "") or ""),
                "overlap_score": overlap,
            }
        )
    memory_candidates.sort(key=lambda candidate: (-int(candidate.get("overlap_score", 0) or 0), str(candidate.get("anchor_id", "") or "")))
    memory_candidates = memory_candidates[: max(1, int(max_memory_candidates))]

    lookback_window = bounded_lookback_source_space(
        document,
        current_sentence_id=current_sentence_id,
        max_candidates=max_lookback_candidates,
    )
    lookback_candidates: list[dict[str, object]] = []
    for sentence in reversed(lookback_window):
        overlap = len(current_tokens & _token_set(str(sentence.get("text", "") or "")))
        lookback_candidates.append(
            {
                "candidate_kind": "source_lookback",
                "sentence_id": str(sentence.get("sentence_id", "") or ""),
                "chapter_id": int(sentence.get("chapter_id", 0) or 0),
                "chapter_title": str(sentence.get("chapter_title", "") or ""),
                "text": str(sentence.get("text", "") or ""),
                "text_role": str(sentence.get("text_role", "") or ""),
                "locator": dict(sentence.get("locator", {})) if isinstance(sentence.get("locator"), dict) else {},
                "overlap_score": overlap,
            }
        )

    lookback_candidates.sort(
        key=lambda candidate: (
            -int(candidate.get("overlap_score", 0) or 0),
            str(candidate.get("sentence_id", "") or ""),
        )
    )

    return {
        "current_sentence_id": current_sentence_id,
        "memory_candidates": memory_candidates,
        "lookback_candidates": lookback_candidates[: max(1, int(max_lookback_candidates))],
    }
