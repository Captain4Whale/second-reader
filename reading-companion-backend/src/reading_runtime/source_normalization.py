"""Import-time source-flow normalization for canonical book documents."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping

from src.reading_core.book_document import BookDocument
from src.reading_core.sentences import build_sentence_records
from src.reading_runtime.llm_gateway import LLMTraceContext, invoke_json, llm_invocation_scope, runtime_trace_context


SOURCE_NORMALIZATION_VERSION = "source_normalization.v1.2"
SOURCE_NORMALIZATION_METHOD = "deterministic_only"
SOURCE_NORMALIZATION_CHUNK_MAX_BLOCKS = 80
SOURCE_NORMALIZATION_CHUNK_MAX_CHARS = 12000
SOURCE_NORMALIZATION_MIN_EXCLUSION_CONFIDENCE = 0.80

SOURCE_NORMALIZATION_ROLES = {
    "mainline_body",
    "heading",
    "auxiliary_note",
    "reference_like",
    "front_back_matter",
    "layout_noise",
    "caption_or_table_support",
    "uncertain_keep_mainline",
}

SOURCE_NORMALIZATION_EXCLUSION_ROLES = {
    "auxiliary_note",
    "reference_like",
    "front_back_matter",
    "layout_noise",
    "caption_or_table_support",
}

SOURCE_NORMALIZATION_SYSTEM_PROMPT = """You are classifying original book blocks before reading begins.

Your task is source-flow classification, not importance judgment, summary, or rewriting.

Mainline text is what a reader should encounter in order while reading the book.
Auxiliary text explains, cites, indexes, attributes, repairs, or decorates the source, but is not itself the next narrative or argument unit.

Allowed normalized_role values:
- mainline_body
- heading
- auxiliary_note
- reference_like
- front_back_matter
- layout_noise
- caption_or_table_support
- uncertain_keep_mainline

Be conservative:
- If unsure, choose uncertain_keep_mainline.
- Do not mark unusual literary form as auxiliary merely because it is short, numbered, poetic, quoted, foreign-language, or formatted oddly.
- Do not mark letters, poems, dialogue, fictional documents, numbered main-body aphorisms, or author-intended note-like prose as auxiliary unless source-flow evidence clearly supports it.
- Treat source markup as evidence: blockquote/poem/verse containers usually protect mainline literary text, while footnote/endnote/reference containers may identify auxiliary source apparatus.
- Never mark blockquote, poem, verse, letter, dialogue, or fictional-document text as layout_noise merely because it is line-broken, repeated nearby, or stylistically unusual.
- Footnote, endnote, translator-note, reference, and note clusters may be auxiliary even if each note is meaningful.
- Layout artifacts, repeated running headers, duplicated titles, and isolated source-conversion symbols should not enter mainline reading.

Return pure JSON only."""

SOURCE_NORMALIZATION_USER_PROMPT_TEMPLATE = """Book:
{book_title}

Book language:
{book_language}

Output language:
{output_language}

Chunk {chunk_index} of {chunk_count}; classify these original numbered blocks.

Each block includes deterministic evidence. Use it to classify source-flow role. Do not rewrite text.

Input blocks:
{blocks_json}

Return JSON:
{{
  "classifications": [
    {{
      "chapter_id": 1,
      "paragraph_index": 58,
      "normalized_role": "auxiliary_note",
      "text_role": "auxiliary",
      "kind": "translator_note",
      "confidence": 0.96,
      "reason_code": "numbered_endnote_cluster",
      "linked_markers": ["[1]"]
    }}
  ]
}}"""

SourceNormalizationClassifier = Callable[[list[dict[str, object]], Mapping[str, object]], object]


def normalize_book_document_source(
    document: BookDocument,
    *,
    output_dir: Path | None = None,
    diagnostics_path: Path | None = None,
    mechanism_key: str = "shared_parse",
    classifier: SourceNormalizationClassifier | None = None,
) -> tuple[BookDocument, dict[str, object]]:
    """Attach source-normalization metadata and rebuild sentences for a new book document."""

    blocks = _collect_source_blocks(document)
    diagnostics: dict[str, object] = {
        "version": SOURCE_NORMALIZATION_VERSION,
        "status": "completed",
        "method": SOURCE_NORMALIZATION_METHOD,
        "block_count": len(blocks),
        "chunk_count": 0,
        "classification_count": 0,
        "applied_exclusion_count": 0,
        "errors": [],
    }
    if not blocks:
        normalized = _merge_source_normalization(document, blocks, {}, diagnostics=diagnostics)
        _write_diagnostics(diagnostics_path, diagnostics)
        return normalized, diagnostics

    classification_rows: list[dict[str, object]] = []
    errors: list[str] = []
    fatal_error = False

    if classifier is not None:
        chunks = list(_chunk_blocks(blocks))
        diagnostics["chunk_count"] = len(chunks)
        diagnostics["classifier_mode"] = "explicit_audit"
        try:
            trace_context = (
                runtime_trace_context(
                    output_dir,
                    mechanism_key=mechanism_key,
                    stage="parse",
                    node="source_normalization",
                )
                if output_dir is not None
                else LLMTraceContext(stage="parse", node="source_normalization")
            )
            with llm_invocation_scope(trace_context=trace_context):
                for index, chunk in enumerate(chunks, start=1):
                    context = _classifier_context(document, chunk_index=index, chunk_count=len(chunks))
                    payload = classifier(chunk, context)
                    rows, row_errors = _classification_rows(payload)
                    classification_rows.extend(rows)
                    errors.extend(f"chunk {index}: {error}" for error in row_errors)
        except Exception as exc:  # pragma: no cover - exercised by tests through fake classifiers
            fatal_error = True
            errors.append(f"{type(exc).__name__}: {exc}")

    if fatal_error:
        classification_rows = []
        diagnostics["status"] = "degraded"
    elif errors:
        diagnostics["status"] = "completed_with_validation_warnings"

    classification_map = _classification_map(classification_rows)
    diagnostics["classification_count"] = len(classification_map)
    diagnostics["errors"] = errors

    normalized = _merge_source_normalization(
        document,
        blocks,
        classification_map,
        diagnostics=diagnostics,
    )
    _write_diagnostics(diagnostics_path, diagnostics)
    return normalized, diagnostics


def _invoke_source_normalization_classifier(
    blocks: list[dict[str, object]],
    context: Mapping[str, object],
) -> object:
    """Call the LLM classifier for one bounded source-normalization chunk."""

    return invoke_json(
        SOURCE_NORMALIZATION_SYSTEM_PROMPT,
        SOURCE_NORMALIZATION_USER_PROMPT_TEMPLATE.format(
            book_title=_clean(context.get("book_title")) or "(unknown)",
            book_language=_clean(context.get("book_language")) or "(unknown)",
            output_language=_clean(context.get("output_language")) or "(unknown)",
            chunk_index=int(context.get("chunk_index", 1) or 1),
            chunk_count=int(context.get("chunk_count", 1) or 1),
            blocks_json=json.dumps(blocks, ensure_ascii=False, indent=2),
        ),
        default={"classifications": []},
    )


def _collect_source_blocks(document: Mapping[str, object]) -> list[dict[str, object]]:
    """Collect prompt-facing block records plus deterministic evidence."""

    blocks: list[dict[str, object]] = []
    chapters = document.get("chapters", [])
    if not isinstance(chapters, list):
        return blocks

    for chapter_position, raw_chapter in enumerate(chapters, start=1):
        if not isinstance(raw_chapter, Mapping):
            continue
        chapter_id = _int(raw_chapter.get("id"), chapter_position)
        chapter_title = _clean(raw_chapter.get("title"))
        paragraphs = [
            item
            for item in raw_chapter.get("paragraphs", [])
            if isinstance(item, Mapping) and _clean(item.get("text"))
        ]
        if not paragraphs:
            continue

        linked_markers = _body_note_markers(paragraphs)
        cluster_ranges = _note_cluster_ranges(paragraphs)
        paragraph_count = len(paragraphs)
        for paragraph_position, paragraph in enumerate(paragraphs, start=1):
            paragraph_index = _int(paragraph.get("paragraph_index"), paragraph_position)
            evidence = _source_evidence(
                paragraph,
                chapter_title=chapter_title,
                paragraph_position=paragraph_position,
                paragraph_count=paragraph_count,
                linked_markers=linked_markers,
                cluster_ranges=cluster_ranges,
            )
            blocks.append(
                {
                    "chapter_id": chapter_id,
                    "chapter_title": chapter_title,
                    "paragraph_index": paragraph_index,
                    "paragraph_position": paragraph_position,
                    "paragraph_count": paragraph_count,
                    "text": _clean(paragraph.get("text")),
                    "current_text_role": _clean(paragraph.get("text_role")) or "body",
                    "baseline_normalized_role": _baseline_normalized_role(paragraph),
                    "block_tag": _clean(paragraph.get("block_tag")) or "p",
                    "heading_level": paragraph.get("heading_level"),
                    "html_id": _clean(paragraph.get("html_id")),
                    "html_class": _clean(paragraph.get("html_class")),
                    "epub_type": _clean(paragraph.get("epub_type")),
                    "role": _clean(paragraph.get("role")),
                    "ancestor_tags": _string_list(paragraph.get("ancestor_tags")),
                    "ancestor_html_ids": _string_list(paragraph.get("ancestor_html_ids")),
                    "ancestor_html_classes": _string_list(paragraph.get("ancestor_html_classes")),
                    "ancestor_epub_types": _string_list(paragraph.get("ancestor_epub_types")),
                    "ancestor_roles": _string_list(paragraph.get("ancestor_roles")),
                    "inline_anchor_ids": _string_list(paragraph.get("inline_anchor_ids")),
                    "inline_anchor_hrefs": _string_list(paragraph.get("inline_anchor_hrefs")),
                    "inline_anchor_texts": _string_list(paragraph.get("inline_anchor_texts")),
                    "href": _clean(paragraph.get("href")),
                    "evidence": evidence,
                }
            )
    return blocks


def _chunk_blocks(blocks: list[dict[str, object]]) -> list[list[dict[str, object]]]:
    """Chunk logical whole-book coverage only for prompt/output safety."""

    chunks: list[list[dict[str, object]]] = []
    current: list[dict[str, object]] = []
    current_chars = 0
    for block in blocks:
        block_chars = len(json.dumps(block, ensure_ascii=False))
        if (
            current
            and (
                len(current) >= SOURCE_NORMALIZATION_CHUNK_MAX_BLOCKS
                or current_chars + block_chars > SOURCE_NORMALIZATION_CHUNK_MAX_CHARS
            )
        ):
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(block)
        current_chars += block_chars
    if current:
        chunks.append(current)
    return chunks


def _classifier_context(
    document: Mapping[str, object],
    *,
    chunk_index: int,
    chunk_count: int,
) -> dict[str, object]:
    metadata = document.get("metadata", {})
    metadata = metadata if isinstance(metadata, Mapping) else {}
    return {
        "book_title": _clean(metadata.get("book")),
        "book_language": _clean(metadata.get("book_language")),
        "output_language": _clean(metadata.get("output_language")),
        "chunk_index": int(chunk_index),
        "chunk_count": int(chunk_count),
    }


def _classification_rows(payload: object) -> tuple[list[dict[str, object]], list[str]]:
    """Normalize classifier payload into rows plus validation warnings."""

    if not isinstance(payload, Mapping):
        return [], ["payload is not an object"]
    rows = payload.get("classifications")
    if not isinstance(rows, list):
        return [], ["classifications is not a list"]

    normalized: list[dict[str, object]] = []
    errors: list[str] = []
    for index, item in enumerate(rows, start=1):
        if not isinstance(item, Mapping):
            errors.append(f"classifications[{index}] is not an object")
            continue
        chapter_id = _int(item.get("chapter_id"))
        paragraph_index = _int(item.get("paragraph_index"))
        role = _normalize_role(item.get("normalized_role"))
        if chapter_id <= 0 or paragraph_index <= 0 or role not in SOURCE_NORMALIZATION_ROLES:
            errors.append(f"classifications[{index}] has invalid key or role")
            continue
        normalized.append(
            {
                "chapter_id": chapter_id,
                "paragraph_index": paragraph_index,
                "normalized_role": role,
                "text_role": _clean(item.get("text_role")),
                "kind": _clean(item.get("kind")),
                "confidence": _confidence(item.get("confidence")),
                "reason_code": _clean(item.get("reason_code")) or role,
                "linked_markers": _string_list(item.get("linked_markers")),
            }
        )
    return normalized, errors


def _classification_map(rows: list[dict[str, object]]) -> dict[tuple[int, int], dict[str, object]]:
    """Return the highest-confidence label per paragraph coordinate."""

    mapped: dict[tuple[int, int], dict[str, object]] = {}
    for row in rows:
        key = (_int(row.get("chapter_id")), _int(row.get("paragraph_index")))
        if key == (0, 0):
            continue
        current = mapped.get(key)
        if current is None or _confidence(row.get("confidence")) >= _confidence(current.get("confidence")):
            mapped[key] = row
    return mapped


def _merge_source_normalization(
    document: BookDocument | Mapping[str, object],
    blocks: list[dict[str, object]],
    classification_map: Mapping[tuple[int, int], Mapping[str, object]],
    *,
    diagnostics: dict[str, object],
) -> BookDocument:
    """Merge validated labels into paragraph records and rebuild sentence layers."""

    block_map = {
        (_int(block.get("chapter_id")), _int(block.get("paragraph_index"))): block
        for block in blocks
    }
    role_counter: Counter[str] = Counter()
    applied_exclusions = 0

    next_chapters: list[dict[str, object]] = []
    chapters = document.get("chapters", []) if isinstance(document, Mapping) else []
    for chapter_position, raw_chapter in enumerate(chapters, start=1):
        if not isinstance(raw_chapter, Mapping):
            continue
        chapter = dict(raw_chapter)
        chapter_id = _int(chapter.get("id"), chapter_position)
        next_paragraphs: list[dict[str, object]] = []
        for paragraph_position, raw_paragraph in enumerate(chapter.get("paragraphs", []), start=1):
            if not isinstance(raw_paragraph, Mapping):
                continue
            paragraph = dict(raw_paragraph)
            paragraph_index = _int(paragraph.get("paragraph_index"), paragraph_position)
            key = (chapter_id, paragraph_index)
            block = block_map.get(key, {})
            label = classification_map.get(key)
            source_normalization, next_text_role, applied = _normalized_paragraph_metadata(paragraph, block, label)
            paragraph["text_role"] = next_text_role
            paragraph["source_normalization"] = source_normalization
            role_counter[str(source_normalization.get("normalized_role", "uncertain_keep_mainline"))] += 1
            if applied:
                applied_exclusions += 1
            next_paragraphs.append(paragraph)

        chapter["paragraphs"] = next_paragraphs
        chapter["sentences"] = build_sentence_records(next_paragraphs, chapter_id=chapter_id)
        next_chapters.append(chapter)

    diagnostics["applied_exclusion_count"] = applied_exclusions
    diagnostics["normalized_role_counts"] = dict(sorted(role_counter.items()))
    return {
        "metadata": dict(document.get("metadata", {})) if isinstance(document, Mapping) else {},
        "chapters": next_chapters,  # type: ignore[typeddict-item]
    }


def _normalized_paragraph_metadata(
    paragraph: Mapping[str, object],
    block: Mapping[str, object],
    label: Mapping[str, object] | None,
) -> tuple[dict[str, object], str, bool]:
    """Return source_normalization metadata, text_role, and whether visibility changed."""

    baseline_text_role = _clean(paragraph.get("text_role")) or "body"
    baseline_role = _baseline_normalized_role(paragraph)
    evidence = dict(block.get("evidence")) if isinstance(block.get("evidence"), Mapping) else {}
    metadata: dict[str, object] = {
        "version": SOURCE_NORMALIZATION_VERSION,
        "normalized_role": baseline_role,
        "kind": _baseline_kind(baseline_role, evidence),
        "confidence": 0.60 if baseline_text_role != "auxiliary" else 0.82,
        "method": "deterministic_baseline",
        "reason_code": _baseline_reason_code(paragraph, evidence),
        "linked_markers": _string_list(evidence.get("linked_markers")),
        "evidence": evidence,
    }
    deterministic_exclusion = _deterministic_exclusion_metadata(paragraph, evidence, label)
    if deterministic_exclusion:
        deterministic_exclusion.pop("source", None)
        metadata.update(deterministic_exclusion)
        return metadata, "auxiliary", baseline_text_role != "auxiliary"

    if label is None:
        return metadata, baseline_text_role, False

    role = _normalize_role(label.get("normalized_role"))
    confidence = _confidence(label.get("confidence"))
    suggestion = {
        "normalized_role": role,
        "kind": _clean(label.get("kind")),
        "confidence": confidence,
        "reason_code": _clean(label.get("reason_code")),
        "linked_markers": _string_list(label.get("linked_markers")),
    }

    if role in {"mainline_body", "heading", "uncertain_keep_mainline"}:
        metadata.update(
            {
                "normalized_role": role,
                "kind": _clean(label.get("kind")) or _baseline_kind(role, evidence),
                "confidence": confidence,
                "method": "classifier_audit",
                "reason_code": _clean(label.get("reason_code")) or role,
                "linked_markers": _string_list(label.get("linked_markers")) or metadata["linked_markers"],
            }
        )
        return metadata, baseline_text_role, False

    if _should_apply_exclusion_label(paragraph, block, label):
        metadata.update(
            {
                "normalized_role": role,
                "kind": _clean(label.get("kind")) or _baseline_kind(role, evidence),
                "confidence": confidence,
                "method": "classifier_audit",
                "reason_code": _clean(label.get("reason_code")) or role,
                "linked_markers": _string_list(label.get("linked_markers")) or metadata["linked_markers"],
            }
        )
        return metadata, "auxiliary", baseline_text_role != "auxiliary"

    next_evidence = dict(evidence)
    next_evidence["rejected_classifier_suggestion"] = suggestion
    metadata["evidence"] = next_evidence
    metadata["method"] = "deterministic_baseline_classifier_rejected"
    return metadata, baseline_text_role, False


def _should_apply_exclusion_label(
    paragraph: Mapping[str, object],
    block: Mapping[str, object],
    label: Mapping[str, object],
) -> bool:
    """Conservatively decide whether one explicit audit label may hide a paragraph from mainline."""

    role = _normalize_role(label.get("normalized_role"))
    if role not in SOURCE_NORMALIZATION_EXCLUSION_ROLES:
        return False
    if _confidence(label.get("confidence")) < SOURCE_NORMALIZATION_MIN_EXCLUSION_CONFIDENCE:
        return False
    evidence = block.get("evidence")
    evidence = evidence if isinstance(evidence, Mapping) else {}
    if role == "layout_noise":
        return _has_structural_layout_noise_evidence(evidence)
    if _protected_mainline_candidate(paragraph, evidence):
        return False
    if _has_structural_exclusion_evidence(evidence):
        return True
    return _clean(paragraph.get("text_role")) == "auxiliary"


def _deterministic_exclusion_metadata(
    paragraph: Mapping[str, object],
    evidence: Mapping[str, object],
    label: Mapping[str, object] | None,
) -> dict[str, object] | None:
    """Return a high-confidence deterministic auxiliary label from source markup."""

    signals = set(_string_list(evidence.get("signals")))
    linked_markers = (
        _string_list(label.get("linked_markers")) if isinstance(label, Mapping) else []
    ) or _string_list(evidence.get("linked_markers"))
    if "html_auxiliary_marker" in signals:
        return {
            "normalized_role": "auxiliary_note",
            "kind": "translator_note",
            "confidence": max(0.94, _confidence(label.get("confidence")) if isinstance(label, Mapping) else 0.0),
            "method": "deterministic_markup",
            "reason_code": "html_auxiliary_marker",
            "linked_markers": linked_markers,
            "source": "explicit_markup",
        }
    if "reference_container" in signals:
        return {
            "normalized_role": "reference_like",
            "kind": "reference",
            "confidence": max(0.94, _confidence(label.get("confidence")) if isinstance(label, Mapping) else 0.0),
            "method": "deterministic_markup",
            "reason_code": "reference_container",
            "linked_markers": linked_markers,
            "source": "explicit_markup",
        }
    if "linked_note_definition" in signals:
        return {
            "normalized_role": "auxiliary_note",
            "kind": _clean(label.get("kind")) if isinstance(label, Mapping) else "note",
            "confidence": max(0.90, _confidence(label.get("confidence")) if isinstance(label, Mapping) else 0.0),
            "method": "deterministic_markup",
            "reason_code": "linked_note_definition",
            "linked_markers": linked_markers,
            "source": "explicit_markup",
        }
    return None


def _protected_mainline_candidate(paragraph: Mapping[str, object], evidence: Mapping[str, object]) -> bool:
    """Return whether a block looks like content that should remain mainline absent strong structure evidence."""

    if _has_structural_exclusion_evidence(evidence):
        return False
    signals = set(_string_list(evidence.get("signals")))
    if "literary_container" in signals:
        return True
    text = _clean(paragraph.get("text"))
    if not text:
        return False
    if re.match(r"^[\"'“‘《「『（(]", text):
        return True
    if re.match(r"^\d+[.)、]\s+\S+", text) and len(text) > 16:
        return True
    if re.search(r"[。！？.!?][\"'”’）)]?$", text) and len(text) >= 12:
        return True
    return False


def _has_structural_exclusion_evidence(evidence: Mapping[str, object]) -> bool:
    """Return whether deterministic evidence supports excluding a block."""

    signals = _string_list(evidence.get("signals"))
    strong = {
        "html_auxiliary_marker",
        "reference_container",
        "linked_note_definition",
    }
    return bool(strong.intersection(signals))


def _has_structural_layout_noise_evidence(evidence: Mapping[str, object]) -> bool:
    """Return whether deterministic evidence supports layout-noise exclusion."""

    signals = set(_string_list(evidence.get("signals")))
    return bool({"short_layout_noise_candidate", "duplicate_heading_candidate"}.intersection(signals))


def _source_evidence(
    paragraph: Mapping[str, object],
    *,
    chapter_title: str,
    paragraph_position: int,
    paragraph_count: int,
    linked_markers: set[str],
    cluster_ranges: Mapping[int, tuple[int, int]],
) -> dict[str, object]:
    """Build deterministic source-flow evidence for one paragraph."""

    text = _clean(paragraph.get("text"))
    own_attrs = [
        _clean(paragraph.get(key))
        for key in ("html_id", "html_class", "epub_type", "role", "href", "block_tag")
        if _clean(paragraph.get(key))
    ]
    ancestor_tags = _string_list(paragraph.get("ancestor_tags"))
    ancestor_classes = _string_list(paragraph.get("ancestor_html_classes"))
    ancestor_ids = _string_list(paragraph.get("ancestor_html_ids"))
    ancestor_epub_types = _string_list(paragraph.get("ancestor_epub_types"))
    ancestor_roles = _string_list(paragraph.get("ancestor_roles"))
    inline_anchor_ids = _string_list(paragraph.get("inline_anchor_ids"))
    inline_anchor_hrefs = _string_list(paragraph.get("inline_anchor_hrefs"))
    inline_anchor_texts = _string_list(paragraph.get("inline_anchor_texts"))
    structural_attrs = " ".join(
        [
            *own_attrs,
            *ancestor_tags,
            *ancestor_classes,
            *ancestor_ids,
            *ancestor_epub_types,
            *ancestor_roles,
        ]
    ).lower()
    signals: list[str] = []
    reason_fragments: list[str] = []
    markers = _leading_note_markers(text)
    inline_note_anchor = _inline_anchor_looks_like_note_definition(
        markers=markers,
        inline_anchor_ids=inline_anchor_ids,
        inline_anchor_hrefs=inline_anchor_hrefs,
        inline_anchor_texts=inline_anchor_texts,
    )
    inline_note_reference = _inline_anchor_looks_like_note_reference(
        inline_anchor_ids=inline_anchor_ids,
        inline_anchor_hrefs=inline_anchor_hrefs,
    )

    if markers and any(marker in linked_markers for marker in markers):
        signals.append("linked_note_marker")
    if paragraph_position in cluster_ranges:
        signals.append("numbered_note_cluster")
        start, end = cluster_ranges[paragraph_position]
        reason_fragments.append(f"note_cluster_p{start}_p{end}")
    if _structural_attrs_have_auxiliary_marker(structural_attrs):
        signals.append("html_auxiliary_marker")
    if _structural_attrs_have_reference_marker(structural_attrs):
        signals.append("reference_container")
    if inline_note_anchor:
        signals.append("inline_note_definition_anchor")
    if inline_note_reference:
        signals.append("inline_note_reference_anchor")
    if markers and inline_note_anchor:
        signals.append("linked_note_definition")
    elif markers and any(marker in linked_markers for marker in markers) and paragraph_position >= max(1, paragraph_count - 2):
        signals.append("orphan_note_like_candidate")
    if _literary_container(paragraph, ancestor_tags, ancestor_classes, ancestor_epub_types, ancestor_roles):
        signals.append("literary_container")
    if _orphan_note_like_candidate(text, paragraph_position=paragraph_position, paragraph_count=paragraph_count, linked_markers=linked_markers):
        signals.append("orphan_note_like_candidate")
    if re.search(r"figcaption|caption|table|figure", structural_attrs):
        signals.append("caption_or_table_marker")
    if re.search(r"https?://|www\.|[a-z0-9.-]+\.(com|org|net|edu|gov|pdf)\b", text.lower()):
        signals.append("reference_like")
    if paragraph_position <= 3 and re.search(r"copyright|contents|table of contents|目录|版权|出版", text.lower()):
        signals.append("front_back_matter_title")
    if len(text) <= 3 and not re.search(r"[\w\u4e00-\u9fff]{2,}", text):
        signals.append("short_layout_noise_candidate")
    if chapter_title and text.strip().lower() == chapter_title.strip().lower() and paragraph_position > 1:
        signals.append("duplicate_heading_candidate")

    return {
        "signals": sorted(set(signals)),
        "linked_markers": sorted(set(markers).intersection(linked_markers)),
        "leading_markers": markers,
        "ancestor_tags": ancestor_tags,
        "ancestor_html_classes": ancestor_classes,
        "ancestor_epub_types": ancestor_epub_types,
        "ancestor_roles": ancestor_roles,
        "inline_anchor_ids": inline_anchor_ids,
        "inline_anchor_hrefs": inline_anchor_hrefs,
        "inline_anchor_texts": inline_anchor_texts,
        "position": _position_hint(paragraph_position, paragraph_count),
        "reason_fragments": reason_fragments,
    }


def _inline_anchor_looks_like_note_definition(
    *,
    markers: list[str],
    inline_anchor_ids: list[str],
    inline_anchor_hrefs: list[str],
    inline_anchor_texts: list[str],
) -> bool:
    """Return whether inline anchors look like a footnote/endnote definition marker."""

    if not markers:
        return False
    marker_set = set(markers)
    normalized_anchor_texts = {
        _normalize_marker(text.strip("[]［］()（） "))
        for text in inline_anchor_texts
        if text
    }
    has_definition_id = bool(
        re.search(
            r"(?:^|[\s#/_-])(f|fn|footnote|endnote|note)[-_]?[0-9ivxlcdm０-９]+\b",
            " ".join(inline_anchor_ids).lower(),
            flags=re.IGNORECASE,
        )
    ) and not bool(re.search(r"(?:^|[\s#/_-])noteref[-_]?", " ".join(inline_anchor_ids).lower(), flags=re.IGNORECASE))
    has_reference_href = bool(
        re.search(r"#(?:s|src|source|ref|noteref)[-_]?[0-9ivxlcdm０-９]+\b", " ".join(inline_anchor_hrefs).lower(), flags=re.IGNORECASE)
    )
    return bool(marker_set.intersection(normalized_anchor_texts) and (has_definition_id or has_reference_href))


def _inline_anchor_looks_like_note_reference(
    *,
    inline_anchor_ids: list[str],
    inline_anchor_hrefs: list[str],
) -> bool:
    """Return whether inline anchors look like mainline note references."""

    ids = " ".join(inline_anchor_ids).lower()
    hrefs = " ".join(inline_anchor_hrefs).lower()
    has_reference_id = bool(
        re.search(
            r"(?:^|[\s#/_-])(?:s|src|source|noteref|note-ref)[-_]?[0-9ivxlcdm０-９]+\b",
            ids,
            flags=re.IGNORECASE,
        )
    )
    has_definition_href = bool(
        re.search(r"#(?:f|fn|footnote|endnote|note)[-_]?[0-9ivxlcdm０-９]+\b", hrefs, flags=re.IGNORECASE)
    )
    return has_reference_id or has_definition_href


def _structural_attrs_have_auxiliary_marker(attrs: str) -> bool:
    """Return whether structural attributes explicitly identify auxiliary apparatus."""

    if re.search(r"译注|注释|尾注", attrs):
        return True
    pattern = (
        r"(?:^|[\s#._:/-])"
        r"(?:footnote|footnotes|endnote|endnotes|fnote|fnotes|doc-footnote|doc-endnote|"
        r"translator-note|annotation|fn)"
        r"(?:$|[\s#._:/-])"
    )
    return bool(re.search(pattern, attrs, flags=re.IGNORECASE))


def _structural_attrs_have_reference_marker(attrs: str) -> bool:
    """Return whether structural attributes explicitly identify reference apparatus."""

    pattern = (
        r"(?:^|[\s#._:/-])"
        r"(?:references|bibliography|bibliographic|doc-bibliography|doc-biblioentry)"
        r"(?:$|[\s#._:/-])"
    )
    return bool(re.search(pattern, attrs, flags=re.IGNORECASE))


def _orphan_note_like_candidate(
    text: str,
    *,
    paragraph_position: int,
    paragraph_count: int,
    linked_markers: set[str],
) -> bool:
    """Return whether one unstructured block is suspicious note apparatus but not excluded."""

    if paragraph_position < max(1, paragraph_count - 3):
        return False
    match = re.match(r"^\s*([0-9０-９]{1,3})[《“\"A-Za-z\u4e00-\u9fff]", text)
    if not match:
        return False
    return _normalize_marker(match.group(1)) in linked_markers


def _literary_container(
    paragraph: Mapping[str, object],
    ancestor_tags: list[str],
    ancestor_classes: list[str],
    ancestor_epub_types: list[str],
    ancestor_roles: list[str],
) -> bool:
    """Return whether source markup identifies this block as literary body form."""

    block_tag = _clean(paragraph.get("block_tag")).lower()
    values = " ".join([block_tag, *ancestor_tags, *ancestor_classes, *ancestor_epub_types, *ancestor_roles]).lower()
    return bool(re.search(r"blockquote|poem|poetry|verse|stanza|letter", values))


def _body_note_markers(paragraphs: list[Mapping[str, object]]) -> set[str]:
    """Collect bracketed note markers from likely mainline body text."""

    markers: set[str] = set()
    for paragraph in paragraphs:
        text = _clean(paragraph.get("text"))
        if _leading_note_markers(text):
            continue
        markers.update(re.findall(r"[\[［]([0-9０-９]{1,3}|[ivxlcdm]{1,6})[\]］]", text, flags=re.IGNORECASE))
    return {_normalize_marker(marker) for marker in markers if marker}


def _note_cluster_ranges(paragraphs: list[Mapping[str, object]]) -> dict[int, tuple[int, int]]:
    """Return paragraph-position ranges for consecutive numbered note definitions."""

    ranges: dict[int, tuple[int, int]] = {}
    run: list[int] = []
    for position, paragraph in enumerate(paragraphs, start=1):
        if _leading_note_markers(_clean(paragraph.get("text"))):
            run.append(position)
            continue
        if len(run) >= 2:
            for item in run:
                ranges[item] = (run[0], run[-1])
        run = []
    if len(run) >= 2:
        for item in run:
            ranges[item] = (run[0], run[-1])
    return ranges


def _leading_note_markers(text: str) -> list[str]:
    """Return normalized leading footnote/endnote markers."""

    pattern = r"^\s*(?:[\[［]\s*([0-9０-９]{1,3}|[ivxlcdm]{1,6})\s*[\]］]|[（(]\s*([0-9０-９]{1,3})\s*[）)])"
    match = re.match(pattern, text, flags=re.IGNORECASE)
    if not match:
        return []
    return [_normalize_marker(group) for group in match.groups() if group]


def _normalize_marker(value: object) -> str:
    text = _clean(value)
    if not text:
        return ""
    return text.translate(str.maketrans("０１２３４５６７８９", "0123456789")).lower()


def _position_hint(paragraph_position: int, paragraph_count: int) -> str:
    if paragraph_position <= 3:
        return "chapter_start"
    if paragraph_position >= max(1, paragraph_count - 2):
        return "chapter_tail"
    return "chapter_middle"


def _baseline_normalized_role(paragraph: Mapping[str, object]) -> str:
    text_role = _clean(paragraph.get("text_role")) or "body"
    if text_role in {"chapter_heading", "section_heading"}:
        return "heading"
    if text_role == "auxiliary":
        return "auxiliary_note"
    return "mainline_body"


def _baseline_kind(role: str, evidence: Mapping[str, object]) -> str:
    if role == "heading":
        return "heading"
    if role == "auxiliary_note":
        signals = _string_list(evidence.get("signals"))
        if "reference_like" in signals:
            return "reference"
        return "auxiliary"
    if role == "layout_noise":
        return "layout"
    if role == "reference_like":
        return "reference"
    if role == "front_back_matter":
        return "front_back_matter"
    if role == "caption_or_table_support":
        return "caption_or_table"
    return "body"


def _baseline_reason_code(paragraph: Mapping[str, object], evidence: Mapping[str, object]) -> str:
    signals = _string_list(evidence.get("signals"))
    if signals:
        return signals[0]
    return f"baseline_{_clean(paragraph.get('text_role')) or 'body'}"


def _normalize_role(value: object) -> str:
    role = _clean(value).lower().replace("-", "_").replace(" ", "_")
    return role if role in SOURCE_NORMALIZATION_ROLES else ""


def _confidence(value: object) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    text = _clean(value).lower()
    if text in {"high", "confident"}:
        return 0.90
    if text in {"medium", "moderate"}:
        return 0.65
    if text in {"low", "uncertain"}:
        return 0.35
    try:
        return max(0.0, min(1.0, float(text)))
    except ValueError:
        return 0.0


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_clean(item) for item in value if _clean(item)]


def _clean(value: object) -> str:
    return str(value or "").strip()


def _int(value: object, default: int = 0) -> int:
    try:
        return int(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def _write_diagnostics(path: Path | None, diagnostics: Mapping[str, object]) -> None:
    if path is None:
        return
    payload: dict[str, object] = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                payload.update(existing)
        except json.JSONDecodeError:
            payload = {}
    payload["source_normalization"] = dict(diagnostics)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
