"""Orientation-only survey artifacts for attentional_v2."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

from src.reading_core import BookDocument, build_sentence_records
from src.iterator_reader.llm_utils import LLMTraceContext, current_llm_scope, invoke_json, llm_invocation_scope

from .schemas import ATTENTIONAL_V2_MECHANISM_VERSION, ATTENTIONAL_V2_SCHEMA_VERSION
from .storage import prompt_manifest_file, revisit_index_file, save_json, survey_map_file
from .prompts import ATTENTIONAL_V2_PROMPTS


SurveyRole = Literal["front_matter", "body", "back_matter"]
SurveyZone = Literal["main_body", "front_support", "back_support", "auxiliary"]

_FRONT_MATTER_MARKERS = ("contents", "table of contents", "overview", "road map", "roadmap", "preface", "prologue")
_BACK_MATTER_MARKERS = ("appendix", "epilogue", "afterword", "notes", "references", "bibliography", "index")
_FRONT_SUPPORT_MARKERS = ("preface", "foreword", "introduction", "prologue")
_BACK_SUPPORT_MARKERS = ("appendix", "epilogue", "afterword", "postscript")
_AUXILIARY_MARKERS = (
    "contents",
    "table of contents",
    "overview",
    "road map",
    "roadmap",
    "notes",
    "references",
    "bibliography",
    "index",
    "acknowledgments",
    "acknowledgements",
    "about the author",
    "credits",
)
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
    chapter_zone: SurveyZone
    zone_confidence: str
    zone_reason: str
    heading_text: str
    first_sentence_id: str
    last_sentence_id: str
    opening_sentences: list[SurveySentenceRef]
    closing_sentences: list[SurveySentenceRef]
    pivot_headings: list[str]


class SurveyReadingPlan(TypedDict, total=False):
    """One machine-readable chapter scheduling plan derived from the survey."""

    mode: str
    mainline_chapter_ids: list[int]
    deferred_chapter_ids: list[int]


class SurveyMap(TypedDict, total=False):
    """Persisted orientation-only survey artifact."""

    schema_version: int
    mechanism_version: str
    generated_at: str
    status: str
    book_frame: dict[str, object]
    chapter_map: list[SurveyChapterEntry]
    reading_plan: SurveyReadingPlan
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


def _zone_fallback(title: str, heading_text: str) -> tuple[SurveyZone, str, str]:
    """Return one deterministic chapter-zone fallback from lightweight structure cues."""

    lowered = " ".join(part for part in [title, heading_text] if part).strip().lower()
    if any(marker in lowered for marker in _AUXILIARY_MARKERS):
        return "auxiliary", "weak", "heuristic_auxiliary_marker"
    if any(marker in lowered for marker in _FRONT_SUPPORT_MARKERS):
        return "front_support", "weak", "heuristic_front_support_marker"
    if any(marker in lowered for marker in _BACK_SUPPORT_MARKERS):
        return "back_support", "weak", "heuristic_back_support_marker"
    return "main_body", "weak", "heuristic_default_main_body"


def _json_block(value: object) -> str:
    """Render one prompt context block as stable JSON."""

    return json.dumps(value, ensure_ascii=False, indent=2)


def _render_prompt(template: str, **replacements: str) -> str:
    """Render one prompt template without treating JSON braces as format fields."""

    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def _write_prompt_manifest(
    output_dir: Path | None,
    *,
    node_name: str,
    prompt_version: str,
    system_prompt: str,
    user_prompt: str,
    promptset_version: str,
) -> None:
    """Persist one survey prompt manifest when an output directory is available."""

    if output_dir is None:
        return
    save_json(
        prompt_manifest_file(output_dir, node_name),
        {
            "node_name": node_name,
            "prompt_version": prompt_version,
            "promptset_version": promptset_version,
            "generated_at": _timestamp(),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        },
    )


def _chapter_sample_payload(
    chapter_entry: SurveyChapterEntry,
    *,
    heuristic_zone: SurveyZone,
    heuristic_confidence: str,
    heuristic_reason: str,
) -> dict[str, object]:
    """Build the bounded chapter sample passed into the survey classifier."""

    return {
        "chapter_id": int(chapter_entry.get("chapter_id", 0) or 0),
        "title": str(chapter_entry.get("title", "") or ""),
        "chapter_number": chapter_entry.get("chapter_number"),
        "level": int(chapter_entry.get("level", 1) or 1),
        "heading_text": str(chapter_entry.get("heading_text", "") or ""),
        "opening_sentences": [
            dict(sentence)
            for sentence in chapter_entry.get("opening_sentences", [])
            if isinstance(sentence, dict)
        ],
        "closing_sentences": [
            dict(sentence)
            for sentence in chapter_entry.get("closing_sentences", [])
            if isinstance(sentence, dict)
        ],
        "pivot_headings": list(chapter_entry.get("pivot_headings", [])),
        "heuristic_zone": heuristic_zone,
        "heuristic_confidence": heuristic_confidence,
        "heuristic_reason": heuristic_reason,
    }


def _classify_chapter_zone(
    *,
    chapter_entry: SurveyChapterEntry,
    chapter_position: int,
    total_chapters: int,
    book_frame: dict[str, object],
    previous_title: str,
    next_title: str,
    output_dir: Path | None,
) -> tuple[SurveyZone, str, str]:
    """Classify one chapter's reading-order zone with LLM help plus deterministic fallback."""

    fallback_zone, fallback_confidence, fallback_reason = _zone_fallback(
        str(chapter_entry.get("title", "") or ""),
        str(chapter_entry.get("heading_text", "") or ""),
    )
    if current_llm_scope() is None:
        return fallback_zone, fallback_confidence, fallback_reason

    prompts = ATTENTIONAL_V2_PROMPTS
    chapter_sample = _chapter_sample_payload(
        chapter_entry,
        heuristic_zone=fallback_zone,
        heuristic_confidence=fallback_confidence,
        heuristic_reason=fallback_reason,
    )
    user_prompt = _render_prompt(
        prompts.survey_chapter_zone_prompt,
        book_frame=_json_block(
            {
                **book_frame,
                "chapter_position": chapter_position,
                "total_chapters": total_chapters,
            }
        ),
        chapter_sample=_json_block(chapter_sample),
        neighbor_titles=_json_block(
            {
                "previous_title": previous_title,
                "next_title": next_title,
            }
        ),
        heuristic_hint=_json_block(
            {
                "zone": fallback_zone,
                "confidence": fallback_confidence,
                "reason": fallback_reason,
            }
        ),
    )
    _write_prompt_manifest(
        output_dir,
        node_name="survey_chapter_zone_classifier",
        prompt_version=prompts.survey_chapter_zone_version,
        system_prompt=prompts.survey_chapter_zone_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
    )

    try:
        with llm_invocation_scope(trace_context=LLMTraceContext(stage="survey", node="chapter_zone_classifier")):
            payload = invoke_json(prompts.survey_chapter_zone_system, user_prompt, default={})
    except Exception:
        return fallback_zone, fallback_confidence, fallback_reason

    zone = str(payload.get("zone", "") or "").strip()
    if zone not in {"main_body", "front_support", "back_support", "auxiliary"}:
        zone = fallback_zone
    confidence = str(payload.get("confidence", "") or "").strip() or fallback_confidence
    reason = str(payload.get("reason", "") or "").strip() or fallback_reason
    return zone, confidence, reason


def _build_reading_plan(chapter_map: list[SurveyChapterEntry]) -> SurveyReadingPlan:
    """Derive one body-first chapter queue from classified survey zones."""

    mainline_chapter_ids = [
        int(chapter.get("chapter_id", 0) or 0)
        for chapter in chapter_map
        if int(chapter.get("chapter_id", 0) or 0) > 0 and chapter.get("chapter_zone") == "main_body"
    ]
    deferred_chapter_ids = [
        int(chapter.get("chapter_id", 0) or 0)
        for chapter in chapter_map
        if int(chapter.get("chapter_id", 0) or 0) > 0 and chapter.get("chapter_zone") in {"front_support", "back_support"}
    ]

    if not mainline_chapter_ids:
        fallback_ids = [
            int(chapter.get("chapter_id", 0) or 0)
            for chapter in chapter_map
            if int(chapter.get("chapter_id", 0) or 0) > 0 and chapter.get("chapter_zone") != "auxiliary"
        ]
        if fallback_ids:
            mainline_chapter_ids = fallback_ids
            deferred_chapter_ids = []
        else:
            mainline_chapter_ids = [
                int(chapter.get("chapter_id", 0) or 0)
                for chapter in chapter_map
                if int(chapter.get("chapter_id", 0) or 0) > 0
            ]
            deferred_chapter_ids = []

    return {
        "mode": "body_first",
        "mainline_chapter_ids": mainline_chapter_ids,
        "deferred_chapter_ids": deferred_chapter_ids,
    }


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
    output_dir: Path | None = None,
    policy_snapshot: dict[str, object] | None = None,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> SurveyMap:
    """Build an orientation-only survey artifact from the shared book document."""

    chapter_map: list[SurveyChapterEntry] = []
    chapters = document.get("chapters", [])
    metadata = dict(document.get("metadata", {}))

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

    book_frame = {
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
    }

    for index, chapter_entry in enumerate(chapter_map):
        previous_title = str(chapter_map[index - 1].get("title", "") or "") if index > 0 else ""
        next_title = str(chapter_map[index + 1].get("title", "") or "") if index + 1 < len(chapter_map) else ""
        zone, zone_confidence, zone_reason = _classify_chapter_zone(
            chapter_entry=chapter_entry,
            chapter_position=index + 1,
            total_chapters=len(chapter_map),
            book_frame=book_frame,
            previous_title=previous_title,
            next_title=next_title,
            output_dir=output_dir,
        )
        chapter_entry["chapter_zone"] = zone
        chapter_entry["zone_confidence"] = zone_confidence
        chapter_entry["zone_reason"] = zone_reason

    reading_plan = _build_reading_plan(chapter_map)
    survey: SurveyMap = {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "generated_at": _timestamp(),
        "status": "orientation_only",
        "book_frame": book_frame,
        "chapter_map": chapter_map,
        "reading_plan": reading_plan,
        "initial_motif_seeds": _motif_seeds(document, chapter_map),
        "survey_caveats": [
            "Orientation only; not a substitute for sequential reading.",
            "Motif seeds are tentative and may be rejected during live reading.",
            "Survey inputs are limited to title, TOC, chapter boundaries, openings, closings, and structural pivots.",
            "Chapter-zone classification is limited to scheduling roles; it must not become hidden chapter summarization or durable understanding.",
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
        output_dir=output_dir,
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
