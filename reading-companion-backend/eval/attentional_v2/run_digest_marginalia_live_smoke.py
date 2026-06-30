#!/usr/bin/env python3
"""Run a small live smoke for live Digest Marginalia.

This is a local diagnostic helper. It verifies the live Digest prompt/transport
contract and a short Ingest -> Digest -> settlement chain over the active
source-normalized user-level dataset. It does not run a formal evaluation or
promote any evidence catalog entry.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import sqlite3
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

DEFAULT_RUN_ID = "digest_marginalia_v21_live_smoke_20260630"
DEFAULT_ANALYSIS_ID = "digest_marginalia_v21_live_smoke"
DEFAULT_JOB_ID = "bgjob_digest_marginalia_v21_live_smoke_20260630"
DEFAULT_PROFILE_ID = "dataset_review_high_trust"
DEFAULT_DATASET_ROOT = (
    BACKEND_ROOT
    / "state"
    / "eval_local_datasets"
    / "user_level_benchmarks"
    / "attentional_v2_user_level_selective_v1_repaired_20260629_source_norm_v1_2_unique_notes"
)
DEFAULT_FOCUSED_SEGMENTS = (
    "xidaduo_private_zh__segment_1",
    "huochu_shengming_de_yiyi_private_zh__segment_1",
)


def _load_backend_env() -> None:
    env_path = BACKEND_ROOT / ".env"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    os.environ.setdefault("LLM_TARGETS_PATH", "config/llm_targets.local.json")
    os.environ.setdefault("LLM_PROFILE_BINDINGS_PATH", "config/llm_profile_bindings.local.json")


_load_backend_env()

from src.attentional_v2.llm_calls import (  # noqa: E402
    _digest_marginalia_payload,
    _normalize_marginalia_items,
)
from src.attentional_v2.llm_output_tools import DIGEST_RESULT_TOOL, validate_digest_result  # noqa: E402
from src.attentional_v2.prompts import ATTENTIONAL_V2_PROMPTS  # noqa: E402
from src.attentional_v2.prompts.digest import (  # noqa: E402
    DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
    render_digest_prompt_xml,
)
from src.attentional_v2.runner import (  # noqa: E402
    _build_sentence_lookup,
    _chapter_ref,
    _load_runtime_bundle,
    _settle_next_unit,
    _write_manifest,
    prepare_next_source_unit_for_read,
)
from src.attentional_v2.source_spans import (  # noqa: E402
    cursor_at_or_after_chapter_end,
    cursor_less_than,
    first_cursor_for_chapter,
    normalize_cursor_for_chapter,
)
from src.attentional_v2.state_projection import build_carry_forward_context, build_digest_prompt_packet  # noqa: E402
from src.attentional_v2.storage import (  # noqa: E402
    initialize_artifact_tree,
    prompt_manifest_file,
    reaction_records_file,
    read_audit_file,
    unit_memory_sqlite_file,
    unit_span_ledger_file,
)
from src.attentional_v2.unit_memory import resolve_memory_retrieval_config  # noqa: E402
from src.iterator_reader.llm_utils import ReaderLLMError  # noqa: E402
from src.reading_core.book_document import BookDocument  # noqa: E402
from src.reading_core.sentences import build_sentence_records  # noqa: E402
from src.reading_core.storage import book_document_file, save_book_document  # noqa: E402
from src.reading_runtime.llm_gateway import (  # noqa: E402
    LLMInvocationOverrides,
    eval_trace_context,
    invoke_structured_output,
    llm_invocation_scope,
)
from src.reading_runtime.provisioning import ProvisionedBook  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _json_dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _analysis_root(run_id: str, analysis_id: str) -> Path:
    return BACKEND_ROOT / "eval" / "runs" / "attentional_v2" / run_id / "analysis" / analysis_id


def _resolve_backend_path(value: str | os.PathLike[str]) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BACKEND_ROOT / path


def _source_span_text(source_unit: Mapping[str, object]) -> str:
    return _clean_text(source_unit.get("source_text"))


def _cursor_str(cursor: Mapping[str, object] | None) -> str:
    if not isinstance(cursor, Mapping):
        return "-"
    return f"P{cursor.get('paragraph_index')}@{cursor.get('char_offset')}"


def _span_str(span: Mapping[str, object] | None) -> str:
    if not isinstance(span, Mapping):
        return "-"
    start = span.get("start_cursor") if isinstance(span.get("start_cursor"), Mapping) else {}
    end = span.get("end_cursor") if isinstance(span.get("end_cursor"), Mapping) else {}
    return f"{_cursor_str(start)} -> {_cursor_str(end)}"


def _contains_exact_quote(texts: list[str], quote: str) -> bool:
    needle = str(quote or "").strip()
    if not needle:
        return False
    return any(needle in str(text or "") for text in texts)


def _legacy_field_leaks(payload: object) -> list[str]:
    leaks: list[str] = []
    if not isinstance(payload, Mapping):
        return leaks
    if isinstance(payload.get("annotations"), list):
        leaks.append("annotations")
    if isinstance(payload.get("marginalia_audit"), list):
        leaks.append("marginalia_audit")
    marginalia = payload.get("marginalia")
    if isinstance(marginalia, list):
        for index, item in enumerate(marginalia):
            if not isinstance(item, Mapping):
                continue
            for field in ("prior_link", "outside_link", "search_intent"):
                if field in item:
                    leaks.append(f"marginalia[{index}].{field}")
    return leaks


def _marginalia_kind(item: Mapping[str, object]) -> str:
    return "highlight_only" if not _clean_text(item.get("content")) else "note_bearing"


def _normalize_marginalia_audit_for_review(
    value: object,
    *,
    marginalia: list[dict[str, object]],
) -> list[dict[str, str]]:
    highlight_quotes = {
        _clean_text(item.get("source_quote"))
        for item in marginalia
        if isinstance(item, Mapping)
        and _clean_text(item.get("source_quote"))
        and not _clean_text(item.get("content"))
    }
    if not isinstance(value, list):
        return []
    audit: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, Mapping):
            continue
        source_quote = _clean_text(item.get("source_quote"))
        selection_reason = _clean_text(item.get("selection_reason"))
        if not source_quote or not selection_reason:
            continue
        if source_quote not in highlight_quotes or source_quote in seen:
            continue
        audit.append({"source_quote": source_quote, "selection_reason": selection_reason})
        seen.add(source_quote)
    return audit


def _quality_flags(
    *,
    item: Mapping[str, object],
    source_text: str,
    understanding: str,
    response: str,
) -> list[str]:
    flags: list[str] = []
    quote = _clean_text(item.get("source_quote"))
    content = _clean_text(item.get("content"))
    if quote and (len(quote) > 180 or (source_text and len(quote) / max(len(source_text), 1) > 0.7)):
        flags.append("quote_too_broad")
    if content:
        generic_patterns = (
            "很重要",
            "非常重要",
            "很美",
            "生动",
            "深刻",
            "vividly",
            "important",
            "beautiful",
            "profound",
        )
        lowered = content.lower()
        if len(content) < 24 or any(pattern.lower() in lowered for pattern in generic_patterns):
            flags.append("possibly_generic")
        compact_content = re.sub(r"\s+", "", content)
        compact_understanding = re.sub(r"\s+", "", understanding)
        compact_response = re.sub(r"\s+", "", response)
        if compact_content and (
            compact_content in compact_understanding
            or compact_content in compact_response
            or compact_content == re.sub(r"\s+", "", quote)
        ):
            flags.append("possibly_duplicated")
    return flags


def _summarize_marginalia(
    marginalia: list[dict[str, object]],
    *,
    source_text: str,
    understanding: str = "",
    response: str = "",
    marginalia_audit: list[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    reason_by_quote = {
        _clean_text(item.get("source_quote")): _clean_text(item.get("selection_reason"))
        for item in (marginalia_audit or [])
        if isinstance(item, Mapping) and _clean_text(item.get("source_quote"))
    }
    items: list[dict[str, object]] = []
    for index, item in enumerate(marginalia, start=1):
        quote = _clean_text(item.get("source_quote"))
        content = _clean_text(item.get("content"))
        kind = _marginalia_kind(item)
        selection_reason = (
            _clean_text(item.get("selection_reason")) or reason_by_quote.get(quote, "")
            if kind == "highlight_only"
            else ""
        )
        quality_flags = _quality_flags(
            item=item,
            source_text=source_text,
            understanding=understanding,
            response=response,
        )
        if kind == "highlight_only" and not selection_reason:
            quality_flags.append("missing_selection_reason")
        items.append(
            {
                "index": index,
                "kind": kind,
                "source_quote": quote,
                "content": content,
                "selection_reason": selection_reason,
                "quote_found_in_unit": _contains_exact_quote([source_text], quote),
                "quality_flags": quality_flags,
            }
        )
    return items


def _empty_runtime_context(chapter_ref: str) -> dict[str, object]:
    from src.attentional_v2.schemas import (  # local import keeps script import surface compact for tests
        build_empty_active_attention,
        build_empty_local_buffer,
        build_empty_reaction_records,
        build_empty_recent_reading_memory,
        build_empty_reflective_frames,
    )

    return build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[],
        local_buffer=build_empty_local_buffer(),
        active_attention=build_empty_active_attention(),
        recent_reading_memory=build_empty_recent_reading_memory(),
        reflective_frames=build_empty_reflective_frames(),
        reaction_records=build_empty_reaction_records(),
        continuation_capsule=None,
    )


@dataclass(frozen=True)
class DirectDigestProbe:
    probe_id: str
    book_title: str
    author: str
    chapter_title: str
    output_language: str
    source_text: str


CALIBRATION_DIRECT_PROBES = (
    DirectDigestProbe(
        probe_id="highlight_candidate_moonlight",
        book_title="记承天寺夜游",
        author="苏轼",
        chapter_title="controlled highlight candidate",
        output_language="zh",
        source_text="庭下如积水空明，水中藻荇交横，盖竹柏影也。",
    ),
    DirectDigestProbe(
        probe_id="note_candidate_kong_yiji",
        book_title="孔乙己",
        author="鲁迅",
        chapter_title="controlled note candidate",
        output_language="zh",
        source_text="孔乙己是站着喝酒而穿长衫的唯一的人。",
    ),
)


CLASSIC_PUBLIC_DOMAIN_DIRECT_PROBES = (
    DirectDigestProbe(
        probe_id="classic_zh_su_shi_moonlight",
        book_title="记承天寺夜游",
        author="苏轼",
        chapter_title="public-domain classic passage",
        output_language="zh",
        source_text="庭下如积水空明，水中藻荇交横，盖竹柏影也。",
    ),
    DirectDigestProbe(
        probe_id="classic_zh_zhuangzi_xiaoyao",
        book_title="庄子",
        author="庄周",
        chapter_title="逍遥游",
        output_language="zh",
        source_text=(
            "北冥有鱼，其名为鲲。鲲之大，不知其几千里也；化而为鸟，其名为鹏。"
            "鹏之背，不知其几千里也；怒而飞，其翼若垂天之云。"
        ),
    ),
    DirectDigestProbe(
        probe_id="classic_zh_lantingji",
        book_title="兰亭集序",
        author="王羲之",
        chapter_title="public-domain classic passage",
        output_language="zh",
        source_text=(
            "夫人之相与，俯仰一世。或取诸怀抱，悟言一室之内；"
            "或因寄所托，放浪形骸之外。虽趣舍万殊，静躁不同，"
            "当其欣于所遇，暂得于己，快然自足，不知老之将至。"
        ),
    ),
    DirectDigestProbe(
        probe_id="classic_zh_mencius_well",
        book_title="孟子",
        author="孟子",
        chapter_title="公孙丑上",
        output_language="zh",
        source_text=(
            "今人乍见孺子将入于井，皆有怵惕恻隐之心；非所以内交于孺子之父母也，"
            "非所以要誉于乡党朋友也，非恶其声而然也。由是观之，无恻隐之心，非人也。"
        ),
    ),
    DirectDigestProbe(
        probe_id="classic_en_pride_prejudice_opening",
        book_title="Pride and Prejudice",
        author="Jane Austen",
        chapter_title="Chapter 1",
        output_language="en",
        source_text=(
            "It is a truth universally acknowledged, that a single man in possession of a good fortune, "
            "must be in want of a wife."
        ),
    ),
    DirectDigestProbe(
        probe_id="classic_en_moby_dick_opening",
        book_title="Moby-Dick; or, The Whale",
        author="Herman Melville",
        chapter_title="Loomings",
        output_language="en",
        source_text=(
            "Call me Ishmael. Some years ago--never mind how long precisely--having little or no money "
            "in my purse, and nothing particular to interest me on shore, I thought I would sail about "
            "a little and see the watery part of the world."
        ),
    ),
    DirectDigestProbe(
        probe_id="classic_en_hamlet_soliloquy",
        book_title="Hamlet",
        author="William Shakespeare",
        chapter_title="Act III, Scene I",
        output_language="en",
        source_text=(
            "To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer "
            "the slings and arrows of outrageous fortune, or to take arms against a sea of troubles "
            "and by opposing end them."
        ),
    ),
    DirectDigestProbe(
        probe_id="classic_en_walden_woods",
        book_title="Walden",
        author="Henry David Thoreau",
        chapter_title="Where I Lived, and What I Lived For",
        output_language="en",
        source_text=(
            "I went to the woods because I wished to live deliberately, to front only the essential "
            "facts of life, and see if I could not learn what it had to teach, and not, when I came "
            "to die, discover that I had not lived. I did not wish to live what was not life, living "
            "is so dear; nor did I wish to practise resignation, unless it was quite necessary."
        ),
    ),
)


DIRECT_PROBE_SETS: dict[str, tuple[DirectDigestProbe, ...]] = {
    "calibration": CALIBRATION_DIRECT_PROBES,
    "classic_public_domain": CLASSIC_PUBLIC_DOMAIN_DIRECT_PROBES,
    "all": CALIBRATION_DIRECT_PROBES + CLASSIC_PUBLIC_DOMAIN_DIRECT_PROBES,
}


def _direct_probes_for_set(probe_set: str) -> tuple[DirectDigestProbe, ...]:
    try:
        return DIRECT_PROBE_SETS[probe_set]
    except KeyError as exc:
        raise ValueError(f"Unknown direct probe set: {probe_set}") from exc


def _llm_call_overrides(
    *,
    max_output_tokens: int,
    timeout_seconds: int,
    retry_attempts: int,
) -> LLMInvocationOverrides:
    return LLMInvocationOverrides(
        max_output_tokens=max_output_tokens,
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
    )


def run_direct_digest_smoke(
    *,
    analysis_root: Path,
    direct_probe_set: str,
    profile_id: str,
    max_output_tokens: int,
    timeout_seconds: int,
    retry_attempts: int,
) -> list[dict[str, object]]:
    """Run controlled live Digest calls and return raw/normalized diagnostics."""

    results: list[dict[str, object]] = []
    direct_root = analysis_root / "direct_digest"
    direct_root.mkdir(parents=True, exist_ok=True)
    for probe in _direct_probes_for_set(direct_probe_set):
        output_dir = direct_root / probe.probe_id
        output_dir.mkdir(parents=True, exist_ok=True)
        current_unit_source = {
            "source_span_id": f"{probe.probe_id}:P1@0-P1@{len(probe.source_text)}",
            "source_span": {
                "start_cursor": {"chapter_id": 1, "chapter_ref": probe.chapter_title, "paragraph_index": 1, "char_offset": 0},
                "end_cursor": {"chapter_id": 1, "chapter_ref": probe.chapter_title, "paragraph_index": 1, "char_offset": len(probe.source_text)},
            },
            "source_text": probe.source_text,
            "paragraph_slices": [{"paragraph_index": 1, "text_role": "body", "text": probe.source_text}],
            "char_count": len(probe.source_text),
            "paragraph_count": 1,
        }
        carry_forward_context = _empty_runtime_context(probe.chapter_title)
        prompt_packet = build_digest_prompt_packet(carry_forward_context=carry_forward_context)
        assembly_result = render_digest_prompt_xml(
            book_title=probe.book_title,
            author=probe.author,
            chapter_title=probe.chapter_title,
            output_language_name="Chinese" if probe.output_language == "zh" else "English",
            recent_reading_memory=prompt_packet.get("recent_reading_memory")
            if isinstance(prompt_packet.get("recent_reading_memory"), dict)
            else None,
            reading_memory_lines=[],
            current_unit_source=current_unit_source,
            current_unit_sentences=[],
        )
        prompt_manifest = {
            "node": "digest",
            "prompt_version": ATTENTIONAL_V2_PROMPTS.digest_version,
            "promptset_version": ATTENTIONAL_V2_PROMPTS.promptset_version,
            "system_prompt": DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
            "prompt_assembly": {
                "spec_id": assembly_result.spec_id,
                "owner_node": assembly_result.owner_node,
                "output_contract": assembly_result.output_contract,
                "rendered_blocks": list(assembly_result.rendered_blocks),
                "used_fragment_ids": list(assembly_result.used_fragment_ids),
                "used_slot_names": list(assembly_result.used_slot_names),
            },
        }
        _json_dump(output_dir / "prompt_manifest.json", prompt_manifest)
        trace_context = eval_trace_context(
            analysis_root,
            eval_target="digest_marginalia_v21_live_smoke",
            stage="direct_digest",
            node=probe.probe_id,
            extra={"probe_id": probe.probe_id},
        )
        overrides = _llm_call_overrides(
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
        )
        started_at = _now()
        started = time.perf_counter()
        with llm_invocation_scope(
            profile_id=profile_id,
            trace_context=trace_context,
            overrides=overrides,
            required_stable_concurrency=1,
        ):
            structured_output = invoke_structured_output(
                DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
                assembly_result.rendered_text,
                output_tool=DIGEST_RESULT_TOOL,
                validator=lambda payload: validate_digest_result(payload, current_unit_texts=[probe.source_text]),
            )
        payload = structured_output.payload
        marginalia = _normalize_marginalia_items(
            _digest_marginalia_payload(payload),
            current_unit_texts=[probe.source_text],
            allowed_ref_ids=set(),
        )
        marginalia_audit = _normalize_marginalia_audit_for_review(
            payload.get("marginalia_audit") if isinstance(payload, Mapping) else None,
            marginalia=marginalia,
        )
        result = {
            "probe_id": probe.probe_id,
            "probe_set": direct_probe_set,
            "status": "ok",
            "started_at": started_at,
            "finished_at": _now(),
            "duration_seconds": round(time.perf_counter() - started, 3),
            "prompt_version": ATTENTIONAL_V2_PROMPTS.digest_version,
            "promptset_version": ATTENTIONAL_V2_PROMPTS.promptset_version,
            "output_contract": assembly_result.output_contract,
            "structured_status": structured_output.status,
            "repair_attempted": structured_output.repair_attempted,
            "validation_errors": list(structured_output.validation_errors),
            "raw_payload": payload,
            "legacy_field_leaks": _legacy_field_leaks(payload),
            "normalized_marginalia": marginalia,
            "marginalia_review": _summarize_marginalia(
                marginalia,
                source_text=probe.source_text,
                marginalia_audit=marginalia_audit,
            ),
            "source_text": probe.source_text,
        }
        results.append(result)
    return results


def _load_dataset_segment(dataset_root: Path, segment_id: str) -> dict[str, object]:
    segments_path = dataset_root / "segments.jsonl"
    segment_row: dict[str, object] | None = None
    for raw_line in segments_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        row = json.loads(raw_line)
        if isinstance(row, dict) and _clean_text(row.get("segment_id")) == segment_id:
            segment_row = row
            break
    if segment_row is None:
        raise RuntimeError(f"Dataset segment not found: {segment_id} in {segments_path}")
    source_rel = _clean_text(segment_row.get("segment_source_path"))
    if not source_rel:
        raise RuntimeError(f"Dataset segment has no segment_source_path: {segment_id}")
    source_path = dataset_root / source_rel
    raw_paragraphs = [item.strip() for item in re.split(r"\n\s*\n+", source_path.read_text(encoding="utf-8")) if item.strip()]
    if not raw_paragraphs:
        raise RuntimeError(f"Dataset segment has no readable paragraphs: {source_path}")
    title_set = {
        _clean_text(item)
        for item in segment_row.get("chapter_titles", [])
        if _clean_text(item)
    } if isinstance(segment_row.get("chapter_titles"), list) else set()
    paragraphs = []
    for index, text in enumerate(raw_paragraphs, start=1):
        role = "chapter_heading" if _clean_text(text) in title_set else "body"
        paragraphs.append(
            {
                "paragraph_index": index,
                "text": text,
                "text_role": role,
                "source_normalization": {
                    "version": "dataset_segment_source_norm_v1_2",
                    "method": "prebuilt_dataset_segment",
                },
            }
        )
    chapter_title = (
        " / ".join(str(item) for item in segment_row.get("chapter_titles", []) if str(item).strip())
        if isinstance(segment_row.get("chapter_titles"), list)
        else segment_id
    )
    language_track = _clean_text(segment_row.get("language_track")) or "zh"
    chapter = {
        "id": 1,
        "ref": f"dataset_segment:{segment_id}",
        "title": chapter_title or segment_id,
        "chapter_number": 1,
        "paragraphs": paragraphs,
        "sentences": build_sentence_records(paragraphs, chapter_id=1),
    }
    document: BookDocument = {
        "schema_version": "book_document_v1",
        "metadata": {
            "book": _clean_text(segment_row.get("book_title")) or segment_id,
            "author": _clean_text(segment_row.get("author")) or "Unknown",
            "book_language": "en" if language_track == "en" else "zh",
            "output_language": "en" if language_track == "en" else "zh",
            "source_file": str(source_path),
        },
        "chapters": [chapter],
    }
    return {
        "segment_id": segment_id,
        "source_id": _clean_text(segment_row.get("source_id")),
        "book_title": _clean_text(segment_row.get("book_title")) or segment_id,
        "author": _clean_text(segment_row.get("author")) or "Unknown",
        "output_language": "en" if language_track == "en" else "zh",
        "segment_source_path": str(source_path),
        "chapter": chapter,
        "document": document,
    }


def _unit_memory_entries(output_dir: Path) -> list[dict[str, object]]:
    db_path = unit_memory_sqlite_file(output_dir)
    if not db_path.exists():
        return []
    entries: list[dict[str, object]] = []
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        for row in connection.execute(
            "SELECT unit_id, unit_index, source_span_id, entry_json FROM unit_memory_entries ORDER BY unit_index"
        ):
            try:
                entry_json = json.loads(row["entry_json"])
            except json.JSONDecodeError:
                entry_json = {}
            entries.append(
                {
                    "unit_id": row["unit_id"],
                    "unit_index": row["unit_index"],
                    "source_span_id": row["source_span_id"],
                    "entry_json": entry_json,
                }
            )
    return entries


def _unit_memory_doc_counts(output_dir: Path) -> dict[str, int]:
    db_path = unit_memory_sqlite_file(output_dir)
    if not db_path.exists():
        return {}
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("SELECT surface, COUNT(*) FROM retrieval_docs GROUP BY surface").fetchall()
    return {str(surface): int(count) for surface, count in rows}


def _runtime_artifact_summary(output_dir: Path) -> dict[str, object]:
    reaction_payload = _json_load(reaction_records_file(output_dir)) if reaction_records_file(output_dir).exists() else {}
    reaction_records = reaction_payload.get("records") if isinstance(reaction_payload.get("records"), list) else []
    read_rows = _jsonl_rows(read_audit_file(output_dir))
    unit_rows = _jsonl_rows(unit_span_ledger_file(output_dir))
    entries = _unit_memory_entries(output_dir)
    return {
        "output_dir": str(output_dir.relative_to(BACKEND_ROOT)) if output_dir.is_relative_to(BACKEND_ROOT) else str(output_dir),
        "read_audit_count": len(read_rows),
        "reaction_record_count": len(reaction_records),
        "unit_span_count": len(unit_rows),
        "unit_memory_entry_count": len(entries),
        "unit_memory_doc_counts": _unit_memory_doc_counts(output_dir),
        "read_audit_latest": read_rows[-1] if read_rows else {},
        "reaction_records": reaction_records,
        "unit_memory_entries": entries,
        "digest_prompt_manifest": _json_load(prompt_manifest_file(output_dir, "digest"))
        if prompt_manifest_file(output_dir, "digest").exists()
        else {},
    }


def _prepare_output_dir(analysis_root: Path, segment_id: str) -> Path:
    output_dir = analysis_root / "runtime" / segment_id
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def run_segment_units(
    *,
    analysis_root: Path,
    dataset_root: Path,
    segment_id: str,
    unit_count: int,
    profile_id: str,
    max_output_tokens: int,
    timeout_seconds: int,
    retry_attempts: int,
) -> dict[str, object]:
    segment = _load_dataset_segment(dataset_root, segment_id)
    chapter = dict(segment["chapter"]) if isinstance(segment.get("chapter"), Mapping) else {}
    document = dict(segment["document"]) if isinstance(segment.get("document"), Mapping) else {}
    output_dir = _prepare_output_dir(analysis_root, segment_id)
    save_book_document(book_document_file(output_dir), document)  # type: ignore[arg-type]
    initialize_artifact_tree(output_dir)
    _write_manifest(output_dir, document)  # type: ignore[arg-type]
    bundle = _load_runtime_bundle(output_dir)
    reader_policy = bundle["reader_policy"]
    memory_retrieval_config = resolve_memory_retrieval_config(output_dir, {}, continue_mode=False)
    _, chapter_lookup = _build_sentence_lookup(document)  # type: ignore[arg-type]
    provisioned = ProvisionedBook(
        book_path=Path(str(segment.get("segment_source_path"))),
        title=_clean_text(segment.get("book_title")),
        author=_clean_text(segment.get("author")),
        book_language=_clean_text(segment.get("output_language")) or "zh",
        output_language=_clean_text(segment.get("output_language")) or "zh",
        output_dir=output_dir,
        raw_chapters=None,
        book_document=document,  # type: ignore[arg-type]
    )
    local_buffer = bundle["local_buffer"]
    local_continuity = bundle["local_continuity"]
    active_attention = bundle["active_attention"]
    recent_reading_memory = bundle["recent_reading_memory"]
    reflective_frames = bundle["reflective_frames"]
    knowledge_activations = bundle["knowledge_activations"]
    reaction_records = bundle["reaction_records"]
    reconsolidation_records = bundle["reconsolidation_records"]
    chapter_ref = _chapter_ref(chapter)
    cursor = first_cursor_for_chapter(chapter)
    units: list[dict[str, object]] = []
    status = "ok"
    stop_reason = "unit_limit"
    started_at = _now()
    for unit_index in range(1, max(1, unit_count) + 1):
        if cursor_at_or_after_chapter_end(chapter, cursor):
            stop_reason = "chapter_end"
            break
        trace_context = eval_trace_context(
            analysis_root,
            eval_target="digest_marginalia_v21_live_smoke",
            stage="focused_runner",
            node=f"{segment_id}_unit_{unit_index:03d}",
            extra={"segment_id": segment_id, "unit_index": unit_index},
        )
        overrides = _llm_call_overrides(
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
        )
        unit_started = time.perf_counter()
        try:
            with llm_invocation_scope(
                profile_id=profile_id,
                trace_context=trace_context,
                overrides=overrides,
                required_stable_concurrency=1,
            ):
                prepared_source_unit = prepare_next_source_unit_for_read(
                    current_chapter=chapter,
                    current_cursor=dict(cursor),
                    local_buffer=local_buffer,  # type: ignore[arg-type]
                    continuation_capsule=dict(bundle.get("continuation_capsule", {})),
                    active_attention=active_attention,  # type: ignore[arg-type]
                    recent_reading_memory=recent_reading_memory,  # type: ignore[arg-type]
                    reflective_frames=reflective_frames,  # type: ignore[arg-type]
                    reaction_records=reaction_records,  # type: ignore[arg-type]
                    local_continuity=local_continuity,  # type: ignore[arg-type]
                    reader_policy=reader_policy,  # type: ignore[arg-type]
                    output_language=_clean_text(segment.get("output_language")) or "zh",
                    output_dir=output_dir,
                    book_title=_clean_text(segment.get("book_title")),
                    author=_clean_text(segment.get("author")),
                    book_id=segment_id,
                    memory_retrieval_config=memory_retrieval_config,
                )
                settled_unit = _settle_next_unit(
                    prepared_source_unit=prepared_source_unit,
                    chapter_lookup=chapter_lookup,
                    local_buffer=local_buffer,  # type: ignore[arg-type]
                    local_continuity=local_continuity,  # type: ignore[arg-type]
                    continuation_capsule=dict(bundle.get("continuation_capsule", {})),
                    active_attention=active_attention,  # type: ignore[arg-type]
                    recent_reading_memory=recent_reading_memory,  # type: ignore[arg-type]
                    reflective_frames=reflective_frames,  # type: ignore[arg-type]
                    knowledge_activations=knowledge_activations,  # type: ignore[arg-type]
                    reaction_records=reaction_records,  # type: ignore[arg-type]
                    reconsolidation_records=reconsolidation_records,
                    reader_policy=reader_policy,  # type: ignore[arg-type]
                    output_language=_clean_text(segment.get("output_language")) or "zh",
                    output_dir=output_dir,
                    provisioned=provisioned,
                    bundle=bundle,  # type: ignore[arg-type]
                    memory_retrieval_config=memory_retrieval_config,
                    reading_queue_stage="marginalia_live_smoke",
                    total_chapters=1,
                    completed_chapters=0,
                    memory_quality_probe_config=None,
                    ordered_probe_sentence_ids=[],
                    meaning_units_in_chapter=[],
                    already_ingested_sentence_ids=set(),
                    capture_memory_probe=False,
                )
        except ReaderLLMError as exc:
            status = "failed"
            stop_reason = _clean_text(getattr(exc, "problem_code", "")) or "reader_llm_error"
            units.append(
                {
                    "unit_index": unit_index,
                    "status": "failed",
                    "problem_code": stop_reason,
                    "error": str(exc),
                    "start_cursor": dict(cursor),
                    "duration_seconds": round(time.perf_counter() - unit_started, 3),
                }
            )
            break
        except Exception as exc:  # noqa: BLE001 - smoke runner should record the failure class.
            status = "failed"
            stop_reason = f"exception:{type(exc).__name__}"
            units.append(
                {
                    "unit_index": unit_index,
                    "status": "failed",
                    "problem_code": stop_reason,
                    "error": str(exc),
                    "start_cursor": dict(cursor),
                    "duration_seconds": round(time.perf_counter() - unit_started, 3),
                }
            )
            break

        local_buffer = settled_unit["local_buffer"]  # type: ignore[assignment]
        local_continuity = settled_unit["local_continuity"]  # type: ignore[assignment]
        active_attention = settled_unit["active_attention"]  # type: ignore[assignment]
        recent_reading_memory = settled_unit["recent_reading_memory"]  # type: ignore[assignment]
        reflective_frames = settled_unit["reflective_frames"]  # type: ignore[assignment]
        knowledge_activations = settled_unit["knowledge_activations"]  # type: ignore[assignment]
        reaction_records = settled_unit["reaction_records"]  # type: ignore[assignment]
        reconsolidation_records = settled_unit["reconsolidation_records"]  # type: ignore[assignment]
        bundle = settled_unit["bundle"]  # type: ignore[assignment]

        selected_source_unit = (
            dict(settled_unit.get("selected_source_unit", {}))
            if isinstance(settled_unit.get("selected_source_unit"), Mapping)
            else {}
        )
        source_span = dict(settled_unit.get("source_span", {})) if isinstance(settled_unit.get("source_span"), Mapping) else {}
        read_rows = _jsonl_rows(read_audit_file(output_dir))
        latest_read = read_rows[-1] if read_rows else {}
        digest_result = latest_read.get("digest_result") if isinstance(latest_read.get("digest_result"), Mapping) else {}
        marginalia = [
            dict(item)
            for item in latest_read.get("marginalia", [])
            if isinstance(item, Mapping)
        ] if isinstance(latest_read.get("marginalia"), list) else []
        marginalia_audit = _normalize_marginalia_audit_for_review(
            latest_read.get("marginalia_audit"),
            marginalia=marginalia,
        )
        source_text = _source_span_text(selected_source_unit)
        units.append(
            {
                "unit_index": unit_index,
                "status": "ok",
                "duration_seconds": round(time.perf_counter() - unit_started, 3),
                "start_cursor": dict(cursor),
                "end_cursor": dict(settled_unit.get("source_cursor", {}))
                if isinstance(settled_unit.get("source_cursor"), Mapping)
                else {},
                "source_span_id": _clean_text(selected_source_unit.get("source_span_id")),
                "source_span": source_span,
                "span": _span_str(source_span),
                "source_text": source_text,
                "reading_impression": _clean_text(latest_read.get("reading_impression")),
                "understanding": _clean_text(
                    (digest_result.get("memory_uptake_ops", [{}])[0].get("payload", {}) or {}).get("memory_text")
                    if isinstance(digest_result.get("memory_uptake_ops"), list)
                    and digest_result.get("memory_uptake_ops")
                    and isinstance(digest_result.get("memory_uptake_ops", [{}])[0], Mapping)
                    and isinstance(digest_result.get("memory_uptake_ops", [{}])[0].get("payload"), Mapping)
                    else ""
                ),
                "marginalia": marginalia,
                "marginalia_review": _summarize_marginalia(
                    marginalia,
                    source_text=source_text,
                    understanding=_clean_text(latest_read.get("reading_impression")),
                    response=_clean_text(latest_read.get("reading_impression")),
                    marginalia_audit=marginalia_audit,
                ),
                "marginalia_count": len(marginalia),
                "emitted_reaction_count": len(settled_unit.get("emitted_reactions", []))
                if isinstance(settled_unit.get("emitted_reactions"), list)
                else 0,
            }
        )
        next_cursor = settled_unit.get("source_cursor")
        if isinstance(next_cursor, dict) and cursor_less_than(cursor, next_cursor):
            cursor = normalize_cursor_for_chapter(chapter, next_cursor)
        else:
            stop_reason = "non_advancing_cursor"
            break
    return {
        "segment_id": segment_id,
        "book_title": segment.get("book_title"),
        "author": segment.get("author"),
        "status": status,
        "stop_reason": stop_reason,
        "started_at": started_at,
        "finished_at": _now(),
        "unit_count": len([unit for unit in units if unit.get("status") == "ok"]),
        "units": units,
        "runtime_artifacts": _runtime_artifact_summary(output_dir),
    }


def run_focused_segments(
    *,
    analysis_root: Path,
    dataset_root: Path,
    segment_ids: list[str],
    unit_count: int,
    profile_id: str,
    max_output_tokens: int,
    timeout_seconds: int,
    retry_attempts: int,
    segment_workers: int,
) -> list[dict[str, object]]:
    ordered_segment_ids = list(segment_ids)
    if not ordered_segment_ids:
        return []

    def _run_one(segment_id: str) -> dict[str, object]:
        try:
            return run_segment_units(
                analysis_root=analysis_root,
                dataset_root=dataset_root,
                segment_id=segment_id,
                unit_count=unit_count,
                profile_id=profile_id,
                max_output_tokens=max_output_tokens,
                timeout_seconds=timeout_seconds,
                retry_attempts=retry_attempts,
            )
        except Exception as exc:  # noqa: BLE001 - preserve one segment failure without hiding sibling results.
            return {
                "segment_id": segment_id,
                "status": "failed",
                "stop_reason": f"exception:{type(exc).__name__}",
                "error": str(exc),
                "started_at": "",
                "finished_at": _now(),
                "unit_count": 0,
                "units": [],
                "runtime_artifacts": {},
            }

    max_workers = max(1, min(int(segment_workers or 1), len(ordered_segment_ids)))
    if max_workers == 1:
        return [_run_one(segment_id) for segment_id in ordered_segment_ids]

    results_by_segment: dict[str, dict[str, object]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_segment = {
            executor.submit(_run_one, segment_id): segment_id
            for segment_id in ordered_segment_ids
        }
        for future in concurrent.futures.as_completed(future_to_segment):
            segment_id = future_to_segment[future]
            results_by_segment[segment_id] = future.result()
    return [results_by_segment[segment_id] for segment_id in ordered_segment_ids]


def _all_marginalia_items(direct_results: list[dict[str, object]], runner_results: list[dict[str, object]]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for result in direct_results:
        for item in result.get("marginalia_review", []):
            if isinstance(item, Mapping):
                items.append(dict(item))
    for segment in runner_results:
        for unit in segment.get("units", []):
            if not isinstance(unit, Mapping):
                continue
            for item in unit.get("marginalia_review", []):
                if isinstance(item, Mapping):
                    items.append(dict(item))
    return items


def _hard_failures(direct_results: list[dict[str, object]], runner_results: list[dict[str, object]]) -> list[str]:
    failures: list[str] = []
    prompt = ATTENTIONAL_V2_PROMPTS
    if prompt.digest_version != "attentional_v2.digest.v21":
        failures.append(f"unexpected_digest_version:{prompt.digest_version}")
    if prompt.promptset_version != "attentional_v2-phase6-v81":
        failures.append(f"unexpected_promptset:{prompt.promptset_version}")
    for result in direct_results:
        if result.get("status") != "ok":
            failures.append(f"direct_failed:{result.get('probe_id')}")
        if result.get("output_contract") != "digest_understanding_response_marginalia_json_v7":
            failures.append(f"unexpected_output_contract:{result.get('probe_id')}:{result.get('output_contract')}")
        leaks = result.get("legacy_field_leaks")
        if isinstance(leaks, list) and leaks:
            failures.append(f"legacy_field_leak:{result.get('probe_id')}:{','.join(str(item) for item in leaks)}")
        for item in result.get("marginalia_review", []):
            if isinstance(item, Mapping) and not item.get("quote_found_in_unit"):
                failures.append(f"direct_unresolved_quote:{result.get('probe_id')}:{item.get('index')}")
            if isinstance(item, Mapping) and "missing_selection_reason" in item.get("quality_flags", []):
                failures.append(f"direct_missing_selection_reason:{result.get('probe_id')}:{item.get('index')}")
    for segment in runner_results:
        if segment.get("status") != "ok":
            failures.append(f"runner_failed:{segment.get('segment_id')}:{segment.get('stop_reason')}")
        artifact_summary = segment.get("runtime_artifacts")
        artifact_summary = dict(artifact_summary) if isinstance(artifact_summary, Mapping) else {}
        if int(artifact_summary.get("read_audit_count", 0) or 0) <= 0:
            failures.append(f"missing_read_audit:{segment.get('segment_id')}")
        if int(artifact_summary.get("unit_memory_entry_count", 0) or 0) < int(segment.get("unit_count", 0) or 0):
            failures.append(f"unit_memory_entry_missing:{segment.get('segment_id')}")
        for unit in segment.get("units", []):
            if not isinstance(unit, Mapping) or unit.get("status") != "ok":
                continue
            for item in unit.get("marginalia_review", []):
                if isinstance(item, Mapping) and not item.get("quote_found_in_unit"):
                    failures.append(f"runner_unresolved_quote:{segment.get('segment_id')}:unit{unit.get('unit_index')}:{item.get('index')}")
                if isinstance(item, Mapping) and "missing_selection_reason" in item.get("quality_flags", []):
                    failures.append(
                        f"runner_missing_selection_reason:{segment.get('segment_id')}:unit{unit.get('unit_index')}:{item.get('index')}"
                    )
    return failures


def build_summary(
    *,
    mode: str,
    direct_probe_set: str,
    direct_results: list[dict[str, object]],
    runner_results: list[dict[str, object]],
    run_id: str,
    analysis_id: str,
    job_id: str,
) -> dict[str, object]:
    all_items = _all_marginalia_items(direct_results, runner_results)
    kind_counts: dict[str, int] = {}
    flag_counts: dict[str, int] = {}
    for item in all_items:
        kind = _clean_text(item.get("kind")) or "unknown"
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        for flag in item.get("quality_flags", []):
            flag_text = _clean_text(flag)
            if flag_text:
                flag_counts[flag_text] = flag_counts.get(flag_text, 0) + 1
    failures = _hard_failures(direct_results, runner_results)
    status = "pass" if not failures else "fail"
    if status == "pass" and flag_counts:
        status = "pass_with_caveats"
    if status == "pass" and kind_counts.get("highlight_only", 0) == 0:
        status = "pass_with_caveats"
    return {
        "run_id": run_id,
        "analysis_id": analysis_id,
        "job_id": job_id,
        "mode": mode,
        "direct_probe_set": direct_probe_set,
        "status": status,
        "generated_at": _now(),
        "prompt_version": ATTENTIONAL_V2_PROMPTS.digest_version,
        "promptset_version": ATTENTIONAL_V2_PROMPTS.promptset_version,
        "output_contract": "digest_understanding_response_marginalia_json_v7",
        "direct_probe_count": len(direct_results),
        "runner_segment_count": len(runner_results),
        "runner_unit_count": sum(int(result.get("unit_count", 0) or 0) for result in runner_results),
        "marginalia_count": len(all_items),
        "marginalia_kind_counts": kind_counts,
        "quality_flag_counts": flag_counts,
        "hard_failures": failures,
        "highlight_only_observed": kind_counts.get("highlight_only", 0) > 0,
    }


def render_report(
    *,
    summary: Mapping[str, object],
    direct_results: list[dict[str, object]],
    runner_results: list[dict[str, object]],
) -> str:
    lines: list[str] = [
        "# Digest Marginalia v21 Live Smoke",
        "",
        "## Summary",
        f"- status: `{summary.get('status')}`",
        f"- run_id: `{summary.get('run_id')}`",
        f"- prompt: `{summary.get('prompt_version')}` / `{summary.get('promptset_version')}`",
        f"- output_contract: `{summary.get('output_contract')}`",
        f"- direct_probe_set: `{summary.get('direct_probe_set')}`",
        f"- direct probes: `{summary.get('direct_probe_count')}`",
        f"- runner segments: `{summary.get('runner_segment_count')}`",
        f"- runner units: `{summary.get('runner_unit_count')}`",
        f"- marginalia count: `{summary.get('marginalia_count')}`",
        f"- marginalia kinds: `{json.dumps(summary.get('marginalia_kind_counts', {}), ensure_ascii=False)}`",
        f"- quality flags: `{json.dumps(summary.get('quality_flag_counts', {}), ensure_ascii=False)}`",
        f"- highlight-only observed: `{summary.get('highlight_only_observed')}`",
        "",
    ]
    failures = summary.get("hard_failures")
    if isinstance(failures, list) and failures:
        lines.extend(["## Hard Failures", ""])
        lines.extend(f"- `{failure}`" for failure in failures)
        lines.append("")
    lines.extend(["## Direct Digest Contract Probes", ""])
    for result in direct_results:
        lines.extend(
            [
                f"### {result.get('probe_id')}",
                f"- status: `{result.get('status')}` / structured: `{result.get('structured_status')}`",
                f"- legacy_field_leaks: `{json.dumps(result.get('legacy_field_leaks', []), ensure_ascii=False)}`",
                "",
                "**Source**",
                "",
                "```text",
                str(result.get("source_text", "")),
                "```",
                "",
                "**Raw Payload**",
                "",
                "```json",
                json.dumps(result.get("raw_payload", {}), ensure_ascii=False, indent=2),
                "```",
                "",
                "**Marginalia Review**",
                "",
            ]
        )
        review = result.get("marginalia_review")
        if isinstance(review, list) and review:
            for item in review:
                if not isinstance(item, Mapping):
                    continue
                lines.append(
                    f"- `{item.get('kind')}` quote_found=`{item.get('quote_found_in_unit')}` "
                    f"flags=`{json.dumps(item.get('quality_flags', []), ensure_ascii=False)}` "
                    f"quote={json.dumps(item.get('source_quote'), ensure_ascii=False)} "
                    f"content={json.dumps(item.get('content'), ensure_ascii=False)} "
                    f"selection_reason={json.dumps(item.get('selection_reason', ''), ensure_ascii=False)}"
                )
        else:
            lines.append("- No Marginalia emitted.")
        lines.append("")
    lines.extend(["## Focused Runner Units", ""])
    for segment in runner_results:
        lines.extend(
            [
                f"### {segment.get('book_title')} (`{segment.get('segment_id')}`)",
                f"- status: `{segment.get('status')}`",
                f"- stop_reason: `{segment.get('stop_reason')}`",
                f"- unit_count: `{segment.get('unit_count')}`",
                "",
            ]
        )
        artifact_summary = segment.get("runtime_artifacts")
        if isinstance(artifact_summary, Mapping):
            lines.extend(
                [
                    "**Runtime Artifacts**",
                    "",
                    f"- output_dir: `{artifact_summary.get('output_dir')}`",
                    f"- read_audit_count: `{artifact_summary.get('read_audit_count')}`",
                    f"- reaction_record_count: `{artifact_summary.get('reaction_record_count')}`",
                    f"- unit_memory_entry_count: `{artifact_summary.get('unit_memory_entry_count')}`",
                    f"- unit_memory_doc_counts: `{json.dumps(artifact_summary.get('unit_memory_doc_counts', {}), ensure_ascii=False)}`",
                    "",
                ]
            )
        for unit in segment.get("units", []):
            if not isinstance(unit, Mapping):
                continue
            lines.extend(
                [
                    f"#### Unit {unit.get('unit_index')}",
                    f"- status: `{unit.get('status')}`",
                    f"- span: `{unit.get('span')}`",
                    f"- marginalia_count: `{unit.get('marginalia_count')}`",
                    "",
                    "```text",
                    str(unit.get("source_text", "")).strip(),
                    "```",
                    "",
                ]
            )
            review = unit.get("marginalia_review")
            if isinstance(review, list) and review:
                for item in review:
                    if not isinstance(item, Mapping):
                        continue
                    lines.append(
                        f"- `{item.get('kind')}` quote_found=`{item.get('quote_found_in_unit')}` "
                        f"flags=`{json.dumps(item.get('quality_flags', []), ensure_ascii=False)}` "
                        f"quote={json.dumps(item.get('source_quote'), ensure_ascii=False)} "
                        f"content={json.dumps(item.get('content'), ensure_ascii=False)} "
                        f"selection_reason={json.dumps(item.get('selection_reason', ''), ensure_ascii=False)}"
                    )
            else:
                lines.append("- No Marginalia emitted.")
            lines.append("")
    if summary.get("status") == "pass_with_caveats" and not summary.get("highlight_only_observed"):
        lines.extend(
            [
                "## Caveat",
                "",
                "No live highlight-only Marginalia was naturally emitted in this smoke. "
                "That is a quality observation rather than a contract failure; deterministic tests cover quote-only persistence.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _load_existing_json(path: Path, fallback: object) -> object:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def _write_outputs(
    *,
    analysis_root: Path,
    mode: str,
    direct_probe_set: str,
    run_id: str,
    analysis_id: str,
    job_id: str,
    direct_results: list[dict[str, object]],
    runner_results: list[dict[str, object]],
) -> dict[str, object]:
    raw_dir = analysis_root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    if direct_results:
        _json_dump(raw_dir / "direct_digest_results.json", direct_results)
    if mode == "foreground-gate":
        _json_dump(raw_dir / "gate_runner_units.json", runner_results)
        existing_focused = _load_existing_json(raw_dir / "runner_units.json", [])
        report_runner_results = [*runner_results, *(existing_focused if isinstance(existing_focused, list) else [])]
    else:
        _json_dump(raw_dir / "runner_units.json", runner_results)
        existing_gate = _load_existing_json(raw_dir / "gate_runner_units.json", [])
        report_runner_results = [*(existing_gate if isinstance(existing_gate, list) else []), *runner_results]
    existing_direct = _load_existing_json(raw_dir / "direct_digest_results.json", [])
    report_direct_results = direct_results or (existing_direct if isinstance(existing_direct, list) else [])
    summary = build_summary(
        mode=mode,
        direct_probe_set=direct_probe_set,
        direct_results=report_direct_results,
        runner_results=report_runner_results,
        run_id=run_id,
        analysis_id=analysis_id,
        job_id=job_id,
    )
    _json_dump(raw_dir / "summary.json", summary)
    report = render_report(
        summary=summary,
        direct_results=report_direct_results,
        runner_results=report_runner_results,
    )
    (analysis_root / "marginalia_smoke_report.md").write_text(report, encoding="utf-8")
    return summary


def _status_payload(
    *,
    args: argparse.Namespace,
    status: str,
    summary: Mapping[str, object] | None = None,
    error: str = "",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": status,
        "run_id": args.run_id,
        "analysis_id": args.analysis_id,
        "job_id": args.job_id,
        "mode": args.mode,
        "direct_probe_set": args.direct_probe_set,
        "segment_ids": list(args.segment_id or DEFAULT_FOCUSED_SEGMENTS),
        "segment_workers": args.segment_workers,
        "updated_at": _now(),
        "analysis_root": str(_analysis_root(args.run_id, args.analysis_id).relative_to(BACKEND_ROOT)),
        "report": str((_analysis_root(args.run_id, args.analysis_id) / "marginalia_smoke_report.md").relative_to(BACKEND_ROOT)),
    }
    if summary:
        payload["summary_status"] = summary.get("status")
        payload["summary"] = dict(summary)
    if error:
        payload["error"] = error
    return payload


def run(args: argparse.Namespace) -> int:
    analysis_root = _analysis_root(args.run_id, args.analysis_id)
    status_file = analysis_root / "status.json"
    analysis_root.mkdir(parents=True, exist_ok=True)
    _json_dump(status_file, _status_payload(args=args, status="running"))
    direct_results: list[dict[str, object]] = []
    runner_results: list[dict[str, object]] = []
    try:
        if args.mode in {"direct", "foreground-gate", "all"}:
            direct_results = run_direct_digest_smoke(
                analysis_root=analysis_root,
                direct_probe_set=args.direct_probe_set,
                profile_id=args.profile_id,
                max_output_tokens=args.max_output_tokens,
                timeout_seconds=args.timeout_seconds,
                retry_attempts=args.retry_attempts,
            )
        if args.mode == "foreground-gate":
            runner_results = [
                run_segment_units(
                    analysis_root=analysis_root,
                    dataset_root=_resolve_backend_path(args.dataset_root),
                    segment_id="xidaduo_private_zh__segment_1",
                    unit_count=args.foreground_units,
                    profile_id=args.profile_id,
                    max_output_tokens=args.max_output_tokens,
                    timeout_seconds=args.timeout_seconds,
                    retry_attempts=args.retry_attempts,
                )
            ]
        if args.mode in {"focused", "all"}:
            segment_ids = list(args.segment_id or DEFAULT_FOCUSED_SEGMENTS)
            runner_results = run_focused_segments(
                analysis_root=analysis_root,
                dataset_root=_resolve_backend_path(args.dataset_root),
                segment_ids=segment_ids,
                unit_count=args.units_per_segment,
                profile_id=args.profile_id,
                max_output_tokens=args.max_output_tokens,
                timeout_seconds=args.timeout_seconds,
                retry_attempts=args.retry_attempts,
                segment_workers=args.segment_workers,
            )
        summary = _write_outputs(
            analysis_root=analysis_root,
            mode=args.mode,
            direct_probe_set=args.direct_probe_set,
            run_id=args.run_id,
            analysis_id=args.analysis_id,
            job_id=args.job_id,
            direct_results=direct_results,
            runner_results=runner_results,
        )
        terminal_status = "completed" if summary.get("status") != "fail" else "failed"
        _json_dump(status_file, _status_payload(args=args, status=terminal_status, summary=summary))
        return 0 if terminal_status == "completed" else 2
    except Exception as exc:  # noqa: BLE001 - preserve failure in status for job registry.
        _json_dump(status_file, _status_payload(args=args, status="failed", error=f"{type(exc).__name__}: {exc}"))
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--analysis-id", default=DEFAULT_ANALYSIS_ID)
    parser.add_argument("--job-id", default=DEFAULT_JOB_ID)
    parser.add_argument("--mode", choices=["direct", "foreground-gate", "focused", "all"], default="foreground-gate")
    parser.add_argument("--direct-probe-set", choices=sorted(DIRECT_PROBE_SETS), default="calibration")
    parser.add_argument("--dataset-root", default=str(DEFAULT_DATASET_ROOT.relative_to(BACKEND_ROOT)))
    parser.add_argument("--segment-id", action="append", default=None)
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--foreground-units", type=int, default=1)
    parser.add_argument("--units-per-segment", type=int, default=4)
    parser.add_argument("--segment-workers", type=int, default=1)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--retry-attempts", type=int, default=3)
    return parser


def main() -> int:
    return run(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
