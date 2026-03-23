"""Orientation-only survey artifacts for attentional_v2."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Literal, TypedDict

from src.reading_core import BookDocument, build_sentence_records

from .schemas import ATTENTIONAL_V2_MECHANISM_VERSION, ATTENTIONAL_V2_SCHEMA_VERSION
from .storage import revisit_index_file, save_json, survey_map_file


SurveyRole = Literal["front_matter", "body", "back_matter"]

_FRONT_MATTER_MARKERS = ("contents", "table of contents", "overview", "road map", "roadmap", "preface", "prologue")
_BACK_MATTER_MARKERS = ("appendix", "epilogue", "afterword", "notes", "references", "bibliography", "index")
_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "from",
    "this",
    "into",
    "your",
    "their",
    "about",
    "chapter",
    "part",
    "book",
    "intro",
    "introduction",
    "note",
    "notes",
}


class SurveySentenceRef(TypedDict, total=False):
    """One sentence reference retained for orientation only."""

    sentence_id: str
    text: str


class MotifSeed(TypedDict, total=False):
    """One tentative motif seed surfaced by the survey pass."""

    seed_id: str
    label: str
    normalized_key: str
    source_chapter_ids: list[int]
    source_kinds: list[str]
    confidence: str


class SurveyChapterEntry(TypedDict, total=False):
    """One orientation-only chapter map entry."""

    chapter_id: int
    title: str
    chapter_number: int | None
    level: int
    structural_role_guess: SurveyRole
    role_confidence: str
    heading_text: str
    first_sentence_id: str
    last_sentence_id: str
    opening_sentences: list[SurveySentenceRef]
    closing_sentences: list[SurveySentenceRef]
    pivot_headings: list[str]


class SurveyMap(TypedDict, total=False):
    """Persisted orientation-only survey artifact."""

    schema_version: int
    mechanism_version: str
    generated_at: str
    status: str
    book_frame: dict[str, object]
    chapter_map: list[SurveyChapterEntry]
    initial_motif_seeds: list[MotifSeed]
    survey_caveats: list[str]
    policy_snapshot: dict[str, object]


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _role_guess(title: str, heading_text: str) -> tuple[SurveyRole, str]:
    """Make a weak structural-role guess from headings only."""

    lowered = " ".join(part for part in [title, heading_text] if part).strip().lower()
    if any(marker in lowered for marker in _FRONT_MATTER_MARKERS):
        return "front_matter", "weak"
    if any(marker in lowered for marker in _BACK_MATTER_MARKERS):
        return "back_matter", "weak"
    return "body", "weak"


def _sentence_refs(sentences: list[dict[str, object]], *, limit: int) -> list[SurveySentenceRef]:
    """Keep only a small number of sentence refs for orientation."""

    refs: list[SurveySentenceRef] = []
    for sentence in sentences[:limit]:
        refs.append(
            {
                "sentence_id": str(sentence.get("sentence_id", "") or ""),
                "text": str(sentence.get("text", "") or ""),
            }
        )
    return refs


def _candidate_seed_tokens(text: str) -> list[str]:
    """Extract conservative candidate motif tokens from headings and openings."""

    lowered = (text or "").lower()
    tokens = re.findall(r"[a-z][a-z'-]{2,}|[\u4e00-\u9fff]{2,}", lowered)
    return [
        token
        for token in tokens
        if token not in _STOPWORDS
        and not token.isdigit()
    ]


def _motif_seeds(document: BookDocument, chapter_map: list[SurveyChapterEntry]) -> list[MotifSeed]:
    """Build tentative motif seeds from titles, headings, and opening sentences only."""

    mentions: dict[str, dict[str, object]] = {}
    chapter_sources = defaultdict(set)
    source_kinds = defaultdict(set)
    counts: Counter[str] = Counter()

    for chapter, chapter_entry in zip(document.get("chapters", []), chapter_map, strict=False):
        if not isinstance(chapter, dict):
            continue
        chapter_id = int(chapter_entry.get("chapter_id", 0) or 0)
        sources = [
            ("book_title", str(document.get("metadata", {}).get("book", "") or "")),
            ("chapter_title", str(chapter.get("title", "") or "")),
            ("heading", str(chapter.get("chapter_heading", {}).get("text", "")) if isinstance(chapter.get("chapter_heading"), dict) else ""),
        ]
        sources.extend(
            ("opening_sentence", str(sentence.get("text", "") or ""))
            for sentence in chapter_entry.get("opening_sentences", [])
            if isinstance(sentence, dict)
        )
        for source_kind, source_text in sources:
            for token in _candidate_seed_tokens(source_text):
                counts[token] += 1
                chapter_sources[token].add(chapter_id)
                source_kinds[token].add(source_kind)
                mentions.setdefault(token, {"label": token})

    ranked = sorted(
        counts,
        key=lambda token: (
            -len(chapter_sources[token]),
            -counts[token],
            token,
        ),
    )
    seeds: list[MotifSeed] = []
    for index, token in enumerate(ranked, start=1):
        if len(seeds) >= 8:
            break
        if len(chapter_sources[token]) < 2 and counts[token] < 2:
            continue
        seeds.append(
            {
                "seed_id": f"seed-{index}",
                "label": str(mentions[token]["label"]),
                "normalized_key": token,
                "source_chapter_ids": sorted(chapter_sources[token]),
                "source_kinds": sorted(source_kinds[token]),
                "confidence": "tentative",
            }
        )

    if seeds:
        return seeds

    fallback_titles = [
        str(chapter.get("title", "") or "")
        for chapter in document.get("chapters", [])
        if isinstance(chapter, dict) and str(chapter.get("title", "") or "").strip()
    ]
    fallback_tokens: list[str] = []
    for title in fallback_titles:
        fallback_tokens.extend(_candidate_seed_tokens(title))
    seen: set[str] = set()
    for index, token in enumerate(fallback_tokens, start=1):
        if token in seen:
            continue
        seen.add(token)
        seeds.append(
            {
                "seed_id": f"seed-{index}",
                "label": token,
                "normalized_key": token,
                "source_chapter_ids": [],
                "source_kinds": ["chapter_title"],
                "confidence": "tentative",
            }
        )
        if len(seeds) >= 5:
            break
    return seeds


def build_book_survey(
    document: BookDocument,
    *,
    policy_snapshot: dict[str, object] | None = None,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> SurveyMap:
    """Build an orientation-only survey artifact from the shared book document."""

    chapter_map: list[SurveyChapterEntry] = []
    chapters = document.get("chapters", [])

    for chapter_index, raw_chapter in enumerate(chapters, start=1):
        if not isinstance(raw_chapter, dict):
            continue
        chapter_id = int(raw_chapter.get("id", chapter_index) or chapter_index)
        sentence_records = raw_chapter.get("sentences")
        if not isinstance(sentence_records, list):
            sentence_records = build_sentence_records(
                raw_chapter.get("paragraphs", []),  # type: ignore[arg-type]
                chapter_id=chapter_id,
            )
        opening = [sentence for sentence in sentence_records[:2] if isinstance(sentence, dict)]
        closing = [sentence for sentence in sentence_records[-2:] if isinstance(sentence, dict)]
        heading_text = (
            str(raw_chapter.get("chapter_heading", {}).get("text", ""))
            if isinstance(raw_chapter.get("chapter_heading"), dict)
            else ""
        )
        role_guess, role_confidence = _role_guess(str(raw_chapter.get("title", "") or ""), heading_text)
        pivot_headings = [
            str(sentence.get("text", "") or "")
            for sentence in sentence_records
            if isinstance(sentence, dict) and str(sentence.get("text_role", "") or "") == "section_heading"
        ][:3]

        chapter_entry: SurveyChapterEntry = {
            "chapter_id": chapter_id,
            "title": str(raw_chapter.get("title", "") or ""),
            "chapter_number": raw_chapter.get("chapter_number"),
            "level": int(raw_chapter.get("level", 1) or 1),
            "structural_role_guess": role_guess,
            "role_confidence": role_confidence,
            "heading_text": heading_text,
            "opening_sentences": _sentence_refs(opening, limit=2),
            "closing_sentences": _sentence_refs(closing, limit=2),
            "pivot_headings": pivot_headings,
        }
        if opening:
            chapter_entry["first_sentence_id"] = str(opening[0].get("sentence_id", "") or "")
        if closing:
            chapter_entry["last_sentence_id"] = str(closing[-1].get("sentence_id", "") or "")
        chapter_map.append(chapter_entry)

    metadata = dict(document.get("metadata", {}))
    survey: SurveyMap = {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "generated_at": _timestamp(),
        "status": "orientation_only",
        "book_frame": {
            "book": metadata.get("book", ""),
            "author": metadata.get("author", ""),
            "book_language": metadata.get("book_language", ""),
            "output_language": metadata.get("output_language", ""),
            "total_chapters": len(chapter_map),
            "table_of_contents": [
                {
                    "chapter_id": entry["chapter_id"],
                    "title": entry["title"],
                    "chapter_number": entry.get("chapter_number"),
                    "level": entry["level"],
                }
                for entry in chapter_map
            ],
        },
        "chapter_map": chapter_map,
        "initial_motif_seeds": _motif_seeds(document, chapter_map),
        "survey_caveats": [
            "Orientation only; not a substitute for sequential reading.",
            "Motif seeds are tentative and may be rejected during live reading.",
            "Survey inputs are limited to title, TOC, chapter boundaries, openings, closings, and structural pivots.",
            "No anchors, knowledge activations, or user-visible reactions may be created from survey alone.",
        ],
        "policy_snapshot": dict(policy_snapshot or {}),
    }
    return survey


def build_revisit_index(survey: SurveyMap) -> dict[str, object]:
    """Build a minimal orientation-only revisit index from the survey artifact."""

    chapter_boundaries: dict[str, object] = {}
    opening_sentence_ids: list[str] = []
    closing_sentence_ids: list[str] = []
    for chapter in survey.get("chapter_map", []):
        if not isinstance(chapter, dict):
            continue
        chapter_id = str(chapter.get("chapter_id", "") or "")
        first_sentence_id = str(chapter.get("first_sentence_id", "") or "")
        last_sentence_id = str(chapter.get("last_sentence_id", "") or "")
        chapter_boundaries[chapter_id] = {
            "first_sentence_id": first_sentence_id,
            "last_sentence_id": last_sentence_id,
            "pivot_headings": list(chapter.get("pivot_headings", [])),
        }
        opening_sentence_ids.extend(
            str(sentence.get("sentence_id", "") or "")
            for sentence in chapter.get("opening_sentences", [])
            if isinstance(sentence, dict)
        )
        closing_sentence_ids.extend(
            str(sentence.get("sentence_id", "") or "")
            for sentence in chapter.get("closing_sentences", [])
            if isinstance(sentence, dict)
        )

    motif_seed_index = {
        str(seed.get("normalized_key", "") or ""): {
            "seed_id": str(seed.get("seed_id", "") or ""),
            "chapter_ids": list(seed.get("source_chapter_ids", [])),
            "confidence": str(seed.get("confidence", "tentative") or "tentative"),
        }
        for seed in survey.get("initial_motif_seeds", [])
        if isinstance(seed, dict)
    }

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": str(survey.get("mechanism_version", ATTENTIONAL_V2_MECHANISM_VERSION)),
        "status": "survey_seeded",
        "chapter_boundaries": chapter_boundaries,
        "opening_sentence_ids": [sentence_id for sentence_id in opening_sentence_ids if sentence_id],
        "closing_sentence_ids": [sentence_id for sentence_id in closing_sentence_ids if sentence_id],
        "motif_seed_index": motif_seed_index,
    }


def write_book_survey_artifacts(
    output_dir,
    document: BookDocument,
    *,
    policy_snapshot: dict[str, object] | None = None,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> dict[str, object]:
    """Persist the orientation-only survey artifacts for attentional_v2."""

    survey = build_book_survey(
        document,
        policy_snapshot=policy_snapshot,
        mechanism_version=mechanism_version,
    )
    revisit_index = build_revisit_index(survey)
    save_json(survey_map_file(output_dir), survey)
    save_json(revisit_index_file(output_dir), revisit_index)
    return {
        "survey_map": survey,
        "revisit_index": revisit_index,
    }
