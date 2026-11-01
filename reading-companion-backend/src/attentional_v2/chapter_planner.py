"""开读前给每章分类（正文/辅助等），生成阅读计划，并据此判定整书是否读完。"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

from src.reading_core import BookDocument, build_sentence_records
from src.iterator_reader.llm_utils import LLMTraceContext, current_llm_scope, invoke_structured_output, llm_invocation_scope
from src.reading_runtime.observation_context import chapter_observation_scope

from .llm_output_tools import CHAPTER_ZONE_RESULT_TOOL, require_mapping_fields
from .schemas import ATTENTIONAL_V2_MECHANISM_VERSION, ATTENTIONAL_V2_SCHEMA_VERSION
from .storage import append_jsonl, event_stream_file, load_json, prompt_manifest_file, save_json, chapter_plan_file
from .prompts import ATTENTIONAL_V2_PROMPTS


ChapterZone = Literal["main_body", "front_support", "back_support", "auxiliary"]

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
class ChapterSampleSentence(TypedDict, total=False):
    """One sentence reference retained for chapter scheduling."""

    sentence_id: str
    text: str


class ChapterPlanEntry(TypedDict, total=False):
    """One chapter scheduling chapter map entry."""

    chapter_id: int
    title: str
    chapter_number: int | None
    level: int
    chapter_zone: ChapterZone
    heading_text: str
    opening_sentences: list[ChapterSampleSentence]
    closing_sentences: list[ChapterSampleSentence]
    pivot_headings: list[str]


class ReadingPlan(TypedDict, total=False):
    """One machine-readable chapter scheduling plan derived from the chapter_planner."""

    mode: str
    mainline_chapter_ids: list[int]
    deferred_chapter_ids: list[int]


class ChapterPlan(TypedDict, total=False):
    """Persisted chapter scheduling chapter_planner artifact."""

    schema_version: int
    mechanism_version: str
    generated_at: str
    status: str
    book_frame: dict[str, object]
    chapter_map: list[ChapterPlanEntry]
    reading_plan: ReadingPlan
    policy_snapshot: dict[str, object]
    input_identity: dict[str, object]
    fingerprint: str
    generation: dict[str, object]


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _zone_fallback(title: str, heading_text: str) -> tuple[ChapterZone, str, str]:
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
    """Persist one chapter_planner prompt manifest when an output directory is available."""

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
    chapter_entry: ChapterPlanEntry,
    *,
    heuristic_zone: ChapterZone,
    heuristic_confidence: str,
    heuristic_reason: str,
) -> dict[str, object]:
    """Build the bounded chapter sample passed into the chapter_planner classifier."""

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


def classify_chapter_zones(
    *,
    chapter_entry: ChapterPlanEntry,
    chapter_position: int,
    total_chapters: int,
    book_frame: dict[str, object],
    previous_title: str,
    next_title: str,
    output_dir: Path | None,
) -> tuple[ChapterZone, str, str]:
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
        prompts.chapter_zone_prompt,
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
        node_name="chapter_zone_classifier",
        prompt_version=prompts.chapter_zone_version,
        system_prompt=prompts.chapter_zone_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
    )

    try:
        with (
            chapter_observation_scope(
                str(int(chapter_entry.get("chapter_id", 0) or 0)),
                chapter_index=max(0, int(chapter_position) - 1),
                stage="chapter_planner",
                node="chapter_zone_classifier",
            ),
            llm_invocation_scope(
                trace_context=LLMTraceContext(
                    stage="chapter_planner",
                    node="chapter_zone_classifier",
                )
            ),
        ):
            payload = invoke_structured_output(
                prompts.chapter_zone_system,
                user_prompt,
                output_tool=CHAPTER_ZONE_RESULT_TOOL,
                validator=require_mapping_fields("zone", "confidence", "reason"),
            ).payload
    except Exception:
        return fallback_zone, fallback_confidence, fallback_reason

    zone = str(payload.get("zone", "") or "").strip()
    if zone not in {"main_body", "front_support", "back_support", "auxiliary"}:
        zone = fallback_zone
    confidence = str(payload.get("confidence", "") or "").strip() or fallback_confidence
    reason = str(payload.get("reason", "") or "").strip() or fallback_reason
    return zone, confidence, reason


def _build_reading_plan(chapter_map: list[ChapterPlanEntry]) -> ReadingPlan:
    """Derive one body-first chapter queue from classified chapter_planner zones."""

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


def _sentence_refs(sentences: list[dict[str, object]], *, limit: int) -> list[ChapterSampleSentence]:
    """Keep only a small number of sentence refs for orientation."""

    refs: list[ChapterSampleSentence] = []
    for sentence in sentences[:limit]:
        refs.append(
            {
                "sentence_id": str(sentence.get("sentence_id", "") or ""),
                "text": str(sentence.get("text", "") or ""),
            }
        )
    return refs


def build_chapter_plan(
    document: BookDocument,
    *,
    output_dir: Path | None = None,
    policy_snapshot: dict[str, object] | None = None,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ChapterPlan:
    """Build an chapter scheduling chapter_planner artifact from the shared book document."""

    chapter_map: list[ChapterPlanEntry] = []
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
        pivot_headings = [
            str(sentence.get("text", "") or "")
            for sentence in sentence_records
            if isinstance(sentence, dict) and str(sentence.get("text_role", "") or "") == "section_heading"
        ][:3]

        chapter_entry: ChapterPlanEntry = {
            "chapter_id": chapter_id,
            "title": str(raw_chapter.get("title", "") or ""),
            "chapter_number": raw_chapter.get("chapter_number"),
            "level": int(raw_chapter.get("level", 1) or 1),
            "heading_text": heading_text,
            "opening_sentences": _sentence_refs(opening, limit=2),
            "closing_sentences": _sentence_refs(closing, limit=2),
            "pivot_headings": pivot_headings,
        }
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
        zone, _confidence, _reason = classify_chapter_zones(
            chapter_entry=chapter_entry,
            chapter_position=index + 1,
            total_chapters=len(chapter_map),
            book_frame=book_frame,
            previous_title=previous_title,
            next_title=next_title,
            output_dir=output_dir,
        )
        chapter_entry["chapter_zone"] = zone

    reading_plan = _build_reading_plan(chapter_map)
    chapter_planner: ChapterPlan = {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "generated_at": _timestamp(),
        "status": "ready",
        "book_frame": book_frame,
        "chapter_map": chapter_map,
        "reading_plan": reading_plan,
        "policy_snapshot": dict(policy_snapshot or {}),
    }
    return chapter_planner


def write_chapter_plan_artifacts(
    output_dir,
    document: BookDocument,
    *,
    policy_snapshot: dict[str, object] | None = None,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
    source_path: Path | None = None,
    continue_mode: bool = False,
) -> dict[str, object]:
    """Reuse a verified plan; resume may validate but must never regenerate it."""

    def digest(value: object) -> str:
        return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    policy = {key: value for key, value in (policy_snapshot or {}).items() if key != "updated_at"}
    identity = {
        "source_digest": hashlib.sha256(source_path.read_bytes()).hexdigest() if source_path else digest(document),
        "classification_prompt_version": ATTENTIONAL_V2_PROMPTS.chapter_zone_version,
        "policy_version": policy.get("policy_version", "unspecified"),
        "policy_digest": digest(policy),
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
    }
    path = chapter_plan_file(output_dir)
    try:
        existing = load_json(path) if path.exists() else {}
    except (OSError, ValueError):
        existing = {}
    previous_identity = existing.get("input_identity", {})
    if not isinstance(previous_identity, dict):
        previous_identity = {}
    reasons = [key + "_changed" for key, value in identity.items() if previous_identity.get(key) != value]
    if not existing.get("fingerprint"):
        reasons = ["missing_verified_plan"]
    elif existing["fingerprint"] != chapter_plan_fingerprint(existing):
        reasons.append("plan_content_changed")
    event = {
        "event_type": "chapter_plan",
        "recorded_at": _timestamp(),
        "action": "resume_rejected" if continue_mode and reasons else "generated" if reasons else "reused",
        "reasons": reasons,
        "previous_fingerprint": existing.get("fingerprint"),
    }
    if continue_mode and reasons:
        append_jsonl(event_stream_file(output_dir), event)
        raise RuntimeError("Resume chapter plan mismatch: " + ", ".join(reasons) + "; resume never regenerates the reading plan.")
    if not reasons:
        append_jsonl(event_stream_file(output_dir), {**event, "fingerprint": existing["fingerprint"]})
        return {"chapter_plan": existing}

    chapter_planner = build_chapter_plan(
        document,
        output_dir=output_dir,
        policy_snapshot=policy_snapshot,
        mechanism_version=mechanism_version,
    )
    chapter_planner["input_identity"] = identity
    chapter_planner["fingerprint"] = chapter_plan_fingerprint(chapter_planner)
    chapter_planner["generation"] = event
    save_json(chapter_plan_file(output_dir), chapter_planner)
    append_jsonl(event_stream_file(output_dir), {**event, "fingerprint": chapter_planner["fingerprint"]})
    return {
        "chapter_plan": chapter_planner,
    }


def chapter_plan_fingerprint(plan: dict[str, object]) -> str:
    """Bind the validated input identity to the exact persisted planning output."""
    payload = {key: value for key, value in plan.items() if key not in {"generated_at", "fingerprint", "generation"}}
    # Policy timestamps describe a write, not a planning input.
    payload["policy_snapshot"] = {key: value for key, value in dict(payload.get("policy_snapshot", {})).items() if key != "updated_at"}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
