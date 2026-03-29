"""Build a combined private-library local supplement from managed source-catalog inputs.

This script now:
- reads private managed-source records from `state/dataset_build/source_catalog.json`
- reuses canonical copied books under `state/library_sources/`
- screens every reachable book through the canonical parse pipeline
- writes tracked source/corpus/split/local-ref manifests for the combined local pool
- writes larger local-only supplement datasets under state/eval_local_datasets/

The tracked manifests keep the benchmark family unified across storage modes, while
the text-bearing derived datasets remain local-only because they come from private
or copyrighted source text.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .corpus_builder import (
        ROOT,
        MANIFEST_ROOT,
        STATE_LOCAL_DATASET_ROOT,
        CandidateSpec,
        chapter_row_from_candidate,
        dataset_manifest,
        load_json,
        load_book_document,
        make_compatibility_fixtures,
        make_runtime_fixtures,
        screen_source_book,
        write_json,
        write_jsonl,
    )
except ImportError:  # pragma: no cover - script execution path
    from corpus_builder import (
        ROOT,
        MANIFEST_ROOT,
        STATE_LOCAL_DATASET_ROOT,
        CandidateSpec,
        chapter_row_from_candidate,
        dataset_manifest,
        load_json,
        load_book_document,
        make_compatibility_fixtures,
        make_runtime_fixtures,
        screen_source_book,
        write_json,
        write_jsonl,
    )

SOURCE_MANIFEST_ID = "attentional_v2_private_library_screen_v2"
LOCAL_REFS_MANIFEST_ID = "attentional_v2_private_library_v2_local_refs"
CORPUS_MANIFEST_ID = "attentional_v2_private_library_bilingual_v2"
SPLITS_MANIFEST_ID = "attentional_v2_private_library_bilingual_v2_splits"
SOURCE_CATALOG_PATH = ROOT / "state" / "dataset_build" / "source_catalog.json"
TRACKED_SOURCE_MANIFEST_PATH = MANIFEST_ROOT / "source_books" / f"{SOURCE_MANIFEST_ID}.json"

PRIMARY_ROLE_ORDER = ("expository", "argumentative", "narrative_reflective", "reference_heavy")
EXCERPT_FRACTIONS = (0.24, 0.72)
MAX_CHAPTERS_PER_SOURCE = 4
MIN_RUNTIME_SENTENCE_COUNT = 18


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_list(value: Any) -> list[str]:
    items = value if isinstance(value, list) else []
    return [str(item).strip() for item in items if str(item).strip()]


def _selection_priority(value: Any, *, fallback: int = 9999) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed > 0 else fallback


def _language_group(source_records: list[dict[str, Any]], *, language: str) -> list[str]:
    return sorted(str(record["source_id"]) for record in source_records if record["language"] == language)


def _tracked_private_library_overrides(path: Path = TRACKED_SOURCE_MANIFEST_PATH) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = load_json(path)
    books = payload.get("books", [])
    if not isinstance(books, list):
        return {}
    overrides: dict[str, dict[str, Any]] = {}
    for record in books:
        if not isinstance(record, dict):
            continue
        source_id = _clean_text(record.get("source_id"))
        if not source_id:
            continue
        overrides[source_id] = dict(record)
    return overrides


def _catalog_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing managed source catalog at {path}. Run make library-source-intake first."
        )
    payload = load_json(path)
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise ValueError(f"Expected 'records' list in managed source catalog at {path}")
    return [dict(record) for record in records if isinstance(record, dict)]


def _resolve_batch_id(record: dict[str, Any], override: dict[str, Any]) -> str:
    override_batch = _clean_text(override.get("acquisition_batch_id"))
    if override_batch:
        return override_batch
    ingest_batches = record.get("ingest_batch_ids")
    if isinstance(ingest_batches, list):
        for value in reversed(ingest_batches):
            cleaned = _clean_text(value)
            if cleaned:
                return cleaned
    acquisition = record.get("acquisition")
    if isinstance(acquisition, dict):
        return _clean_text(acquisition.get("ingest_batch_id"))
    return ""


def load_private_library_source_items(
    *,
    root: Path = ROOT,
    catalog_path: Path = SOURCE_CATALOG_PATH,
    tracked_manifest_path: Path = TRACKED_SOURCE_MANIFEST_PATH,
) -> list[dict[str, Any]]:
    overrides = _tracked_private_library_overrides(tracked_manifest_path)
    items: list[dict[str, Any]] = []
    for record in _catalog_records(catalog_path):
        if _clean_text(record.get("visibility")) != "private":
            continue
        language = _clean_text(record.get("language"))
        if language not in {"en", "zh"}:
            continue
        source_id = _clean_text(record.get("source_id"))
        relative_local_path = _clean_text(record.get("relative_local_path"))
        if not source_id or not relative_local_path:
            continue
        if not relative_local_path.startswith("state/library_sources/"):
            continue

        source_path = root / relative_local_path
        if not source_path.exists():
            raise FileNotFoundError(source_path)

        override = overrides.get(source_id, {})
        selection_priority = _selection_priority(record.get("selection_priority"))
        if selection_priority == 9999:
            selection_priority = _selection_priority(override.get("selection_priority"))

        type_tags = _normalize_list(record.get("type_tags")) or _normalize_list(override.get("type_tags"))
        role_tags = _normalize_list(record.get("role_tags")) or _normalize_list(override.get("role_tags"))
        notes = _normalize_list(record.get("notes")) or _normalize_list(override.get("notes"))
        title = _clean_text(record.get("title")) or _clean_text(override.get("title")) or source_path.stem
        author = _clean_text(record.get("author")) or _clean_text(override.get("author"))
        origin = _clean_text(record.get("origin")) or _clean_text(override.get("origin")) or "managed-library-source"
        acquisition_batch_id = _resolve_batch_id(record, override)
        acquisition = record.get("acquisition") if isinstance(record.get("acquisition"), dict) else {}
        promoted_local_path = relative_local_path.replace("state/library_sources/", "", 1)

        items.append(
            {
                "spec": CandidateSpec(
                    source_id=source_id,
                    title=title,
                    author=author,
                    language=language,
                    origin=origin,
                    storage_mode="local-only",
                    promoted_local_path=promoted_local_path,
                    acquisition={"kind": "managed_source_catalog", **acquisition},
                    type_tags=type_tags,
                    role_tags=role_tags,
                    selection_priority=selection_priority,
                    notes=notes,
                ),
                "source_path": source_path,
                "acquisition_batch_id": acquisition_batch_id,
                "origin_filename": _clean_text(record.get("original_filename")) or source_path.name,
                "relative_local_path": relative_local_path,
            }
        )
    items.sort(
        key=lambda item: (
            int(item["spec"].selection_priority),
            str(item["spec"].language),
            str(item["spec"].source_id),
        )
    )
    return items


def build_private_library_splits(source_records: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    splits: dict[str, dict[str, list[str]]] = {
        "all_private_library_sources": {
            "en": _language_group(source_records, language="en"),
            "zh": _language_group(source_records, language="zh"),
        },
        "chapter_corpus_eligible": {
            "en": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "en" and record["corpus_lane"] == "chapter_corpus_eligible"
            ),
            "zh": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "zh" and record["corpus_lane"] == "chapter_corpus_eligible"
            ),
        },
        "excerpt_only": {
            "en": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "en" and record["corpus_lane"] == "excerpt_only"
            ),
            "zh": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "zh" and record["corpus_lane"] == "excerpt_only"
            ),
        },
        "reject_this_pass": {
            "en": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "en" and record["corpus_lane"] == "reject"
            ),
            "zh": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "zh" and record["corpus_lane"] == "reject"
            ),
        },
    }
    batch_ids = sorted({_clean_text(record.get("acquisition_batch_id")) for record in source_records if _clean_text(record.get("acquisition_batch_id"))})
    for batch_id in batch_ids:
        splits[batch_id] = {
            "en": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "en" and _clean_text(record.get("acquisition_batch_id")) == batch_id
            ),
            "zh": sorted(
                str(record["source_id"])
                for record in source_records
                if record["language"] == "zh" and _clean_text(record.get("acquisition_batch_id")) == batch_id
            ),
        }
    return splits


def _primary_selection_role(role_tags: list[str]) -> str:
    for role in PRIMARY_ROLE_ORDER:
        if role in role_tags:
            return role
    return "reserve"


def _choose_runtime_seed_rows(chapter_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    seen_sources: set[str] = set()
    sorted_rows = sorted(
        chapter_rows,
        key=lambda row: (
            -float(row.get("candidate_score", 0.0)),
            int(row.get("selection_priority", 9999)),
            int(row.get("chapter_number", 0)),
        ),
    )
    for row in sorted_rows:
        source_id = str(row["source_id"])
        if source_id in seen_sources:
            continue
        if int(row.get("sentence_count", 0)) < MIN_RUNTIME_SENTENCE_COUNT:
            continue
        chosen.append(dict(row))
        seen_sources.add(source_id)
    return chosen


def _excerpt_window(sentences: list[dict[str, Any]], center_fraction: float, *, radius: int) -> tuple[int, int]:
    if not sentences:
        return (0, 0)
    center = max(0, min(len(sentences) - 1, int(len(sentences) * center_fraction)))
    start = max(0, center - radius)
    end = min(len(sentences), center + radius + 1)
    if end <= start:
        end = min(len(sentences), start + 1)
    return start, end


def _excerpt_seed_cases(chapter_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for row in chapter_rows:
        document = load_book_document(ROOT / str(row["output_dir"]))
        chapter = next(
            (candidate for candidate in document.get("chapters", []) if str(candidate.get("id")) == str(row["chapter_id"])),
            None,
        )
        if not chapter:
            continue
        sentences = list(chapter.get("sentences") or [])
        if len(sentences) < 6:
            continue
        radius = 3 if row["language_track"] == "en" else 2
        for index, fraction in enumerate(EXCERPT_FRACTIONS, start=1):
            start, end = _excerpt_window(sentences, fraction, radius=radius)
            window = sentences[start:end]
            excerpt_text = "\n".join(str(sentence.get("text") or "") for sentence in window).strip()
            if len(excerpt_text) < 80:
                continue
            cases.append(
                {
                    "case_id": f"{row['chapter_case_id']}__seed_{index}",
                    "split": "private_library_seed_v2",
                    "source_id": row["source_id"],
                    "book_title": row["book_title"],
                    "author": row["author"],
                    "output_language": row["language_track"],
                    "chapter_id": str(row["chapter_id"]),
                    "chapter_number": int(row["chapter_number"]),
                    "chapter_title": row["chapter_title"],
                    "start_sentence_id": window[0]["sentence_id"],
                    "end_sentence_id": window[-1]["sentence_id"],
                    "excerpt_text": excerpt_text,
                    "selection_role": row["selection_role"],
                    "type_tags": list(row.get("type_tags") or []),
                    "role_tags": list(row.get("role_tags") or []),
                    "candidate_position_bucket": row.get("candidate_position_bucket"),
                    "excerpt_seed_status": "private_library_seed_v2",
                    "notes": "Auto-extracted seed excerpt from the combined local private-library supplement. Requires later curation before benchmark promotion.",
                }
            )
    return cases


def _summary_counts(source_records: list[dict[str, Any]]) -> dict[str, Any]:
    language_counts = Counter(str(record["language"]) for record in source_records)
    lane_counts = Counter(str(record["corpus_lane"]) for record in source_records)
    batch_counts = Counter(str(record["acquisition_batch_id"]) for record in source_records)
    category_counts: Counter[str] = Counter()
    for record in source_records:
        for tag in list(record.get("type_tags") or []):
            category_counts[str(tag)] += 1
    return {
        "book_count_total": len(source_records),
        "language_counts": dict(sorted(language_counts.items())),
        "corpus_lane_counts": dict(sorted(lane_counts.items())),
        "acquisition_batch_counts": dict(sorted(batch_counts.items())),
        "type_tag_counts": dict(sorted(category_counts.items())),
    }


def main() -> None:
    items = load_private_library_source_items()
    if not items:
        raise ValueError(
            "No private managed-library sources are available in the source catalog. "
            "Run make library-source-intake first, then retry the private-library supplement build."
        )

    source_records: list[dict[str, Any]] = []
    source_refs: list[dict[str, Any]] = []
    chapter_rows_by_language: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for item in items:
        spec: CandidateSpec = item["spec"]
        source_path = Path(item["source_path"])
        if not source_path.exists():
            raise FileNotFoundError(source_path)

        relative_local_path = str(item["relative_local_path"])
        record = screen_source_book(
            spec=spec,
            local_path=source_path,
            relative_local_path=relative_local_path,
            acquisition_metadata={
                "download_url": None,
                "input_filename": item["origin_filename"],
                "acquisition_batch_id": item["acquisition_batch_id"],
            },
            selection_priority=spec.selection_priority,
        )
        record["storage_policy"] = "private-local"
        record["screening_status"] = "screened_private_library_v2"
        record["acquisition_batch_id"] = item["acquisition_batch_id"]
        record["origin_filename"] = item["origin_filename"]
        source_records.append(record)
        source_refs.append(
            {
                "source_id": record["source_id"],
                "relative_local_path": record["relative_local_path"],
                "sha256": record["sha256"],
                "file_size": record["file_size"],
                "acquisition_batch_id": item["acquisition_batch_id"],
            }
        )

        candidate_rows = list(record.get("candidate_chapters") or [])[:MAX_CHAPTERS_PER_SOURCE]
        primary_role = _primary_selection_role(list(record.get("role_tags") or []))
        for candidate in candidate_rows:
            row = chapter_row_from_candidate(record, candidate)
            row["selection_status"] = "private_library_candidate_v2"
            row["selection_role"] = primary_role
            row["corpus_lane"] = str(record["corpus_lane"])
            row["acquisition_batch_id"] = item["acquisition_batch_id"]
            chapter_rows_by_language[str(record["language"])].append(row)

    runtime_rows_by_language = {
        language: _choose_runtime_seed_rows(rows) for language, rows in chapter_rows_by_language.items()
    }
    excerpt_rows_by_language = {
        language: _excerpt_seed_cases(rows) for language, rows in chapter_rows_by_language.items()
    }
    compat_rows = make_compatibility_fixtures(runtime_rows_by_language.get("en", []) + runtime_rows_by_language.get("zh", []))

    source_manifest_path = MANIFEST_ROOT / "source_books" / f"{SOURCE_MANIFEST_ID}.json"
    local_refs_manifest_path = MANIFEST_ROOT / "local_refs" / "attentional_v2_private_library_v2.json"
    corpora_manifest_path = MANIFEST_ROOT / "corpora" / f"{CORPUS_MANIFEST_ID}.json"
    splits_manifest_path = MANIFEST_ROOT / "splits" / f"{CORPUS_MANIFEST_ID}.json"

    package_ids = {
        "chapter_corpora": {
            "en": "attentional_v2_private_library_chapters_en_v2",
            "zh": "attentional_v2_private_library_chapters_zh_v2",
        },
        "runtime_fixtures": {
            "en": "attentional_v2_private_library_runtime_en_v2",
            "zh": "attentional_v2_private_library_runtime_zh_v2",
        },
        "excerpt_cases": {
            "en": "attentional_v2_private_library_excerpt_en_v2",
            "zh": "attentional_v2_private_library_excerpt_zh_v2",
        },
        "compatibility_fixtures": {
            "shared": "attentional_v2_private_library_compat_shared_v2",
        },
    }

    write_json(
        source_manifest_path,
        {
            "manifest_id": SOURCE_MANIFEST_ID,
            "description": "Tracked screening inventory for the combined private-library supplement built from the managed source catalog and canonical local source library.",
            "summary": _summary_counts(source_records),
            "books": source_records,
        },
    )

    local_package_refs: list[dict[str, Any]] = []
    for family, tracks in package_ids.items():
        for track, dataset_id in tracks.items():
            local_package_refs.append(
                {
                    "dataset_id": dataset_id,
                    "family": family,
                    "language_track": track,
                    "relative_local_path": str((STATE_LOCAL_DATASET_ROOT / family / dataset_id).relative_to(ROOT)),
                }
            )

    write_json(
        local_refs_manifest_path,
        {
            "manifest_id": LOCAL_REFS_MANIFEST_ID,
            "description": "Local source-file and local-package references for the combined private-library attentional_v2 supplement built from managed source-catalog inputs.",
            "source_refs": source_refs,
            "local_dataset_packages": local_package_refs,
        },
    )

    write_json(
        corpora_manifest_path,
        {
            "manifest_id": CORPUS_MANIFEST_ID,
            "description": "Combined bilingual private-library source corpus for attentional_v2 evaluation supplementation, sourced from the managed local source catalog.",
            "language_tracks": {
                "en": [record["source_id"] for record in source_records if record["language"] == "en"],
                "zh": [record["source_id"] for record in source_records if record["language"] == "zh"],
            },
        },
    )
    splits = build_private_library_splits(source_records)
    write_json(
        splits_manifest_path,
        {
            "manifest_id": SPLITS_MANIFEST_ID,
            "description": "Split definitions for the combined private-library attentional_v2 supplement built from managed source-catalog inputs.",
            "splits": splits,
        },
    )

    source_manifest_refs = [
        str(source_manifest_path.relative_to(ROOT)),
        str(local_refs_manifest_path.relative_to(ROOT)),
        str(corpora_manifest_path.relative_to(ROOT)),
    ]
    split_refs = [str(splits_manifest_path.relative_to(ROOT))]

    def package_root(family: str, dataset_id: str) -> Path:
        return STATE_LOCAL_DATASET_ROOT / family / dataset_id

    en_chapter_dataset_id = package_ids["chapter_corpora"]["en"]
    zh_chapter_dataset_id = package_ids["chapter_corpora"]["zh"]
    en_runtime_dataset_id = package_ids["runtime_fixtures"]["en"]
    zh_runtime_dataset_id = package_ids["runtime_fixtures"]["zh"]
    en_excerpt_dataset_id = package_ids["excerpt_cases"]["en"]
    zh_excerpt_dataset_id = package_ids["excerpt_cases"]["zh"]
    compat_dataset_id = package_ids["compatibility_fixtures"]["shared"]

    write_json(
        package_root("chapter_corpora", en_chapter_dataset_id) / "manifest.json",
        dataset_manifest(
            dataset_id=en_chapter_dataset_id,
            family="chapter_corpora",
            language_track="en",
            description="English private-library chapter candidates derived from the combined user-supplied private book pool.",
            primary_file="chapters.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
    )
    write_jsonl(
        package_root("chapter_corpora", en_chapter_dataset_id) / "chapters.jsonl",
        chapter_rows_by_language.get("en", []),
    )
    write_json(
        package_root("chapter_corpora", zh_chapter_dataset_id) / "manifest.json",
        dataset_manifest(
            dataset_id=zh_chapter_dataset_id,
            family="chapter_corpora",
            language_track="zh",
            description="Chinese private-library chapter candidates derived from the combined user-supplied private book pool.",
            primary_file="chapters.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
    )
    write_jsonl(
        package_root("chapter_corpora", zh_chapter_dataset_id) / "chapters.jsonl",
        chapter_rows_by_language.get("zh", []),
    )

    write_json(
        package_root("runtime_fixtures", en_runtime_dataset_id) / "manifest.json",
        dataset_manifest(
            dataset_id=en_runtime_dataset_id,
            family="runtime_fixtures",
            language_track="en",
            description="English runtime/resume fixtures derived from the combined private-library supplement.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
    )
    write_jsonl(
        package_root("runtime_fixtures", en_runtime_dataset_id) / "fixtures.jsonl",
        make_runtime_fixtures(runtime_rows_by_language.get("en", [])),
    )
    write_json(
        package_root("runtime_fixtures", zh_runtime_dataset_id) / "manifest.json",
        dataset_manifest(
            dataset_id=zh_runtime_dataset_id,
            family="runtime_fixtures",
            language_track="zh",
            description="Chinese runtime/resume fixtures derived from the combined private-library supplement.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
    )
    write_jsonl(
        package_root("runtime_fixtures", zh_runtime_dataset_id) / "fixtures.jsonl",
        make_runtime_fixtures(runtime_rows_by_language.get("zh", [])),
    )

    write_json(
        package_root("excerpt_cases", en_excerpt_dataset_id) / "manifest.json",
        dataset_manifest(
            dataset_id=en_excerpt_dataset_id,
            family="excerpt_cases",
            language_track="en",
            description="English excerpt seed candidates derived from the combined private-library supplement.",
            primary_file="cases.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
    )
    write_jsonl(
        package_root("excerpt_cases", en_excerpt_dataset_id) / "cases.jsonl",
        excerpt_rows_by_language.get("en", []),
    )
    write_json(
        package_root("excerpt_cases", zh_excerpt_dataset_id) / "manifest.json",
        dataset_manifest(
            dataset_id=zh_excerpt_dataset_id,
            family="excerpt_cases",
            language_track="zh",
            description="Chinese excerpt seed candidates derived from the combined private-library supplement.",
            primary_file="cases.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
    )
    write_jsonl(
        package_root("excerpt_cases", zh_excerpt_dataset_id) / "cases.jsonl",
        excerpt_rows_by_language.get("zh", []),
    )

    write_json(
        package_root("compatibility_fixtures", compat_dataset_id) / "manifest.json",
        dataset_manifest(
            dataset_id=compat_dataset_id,
            family="compatibility_fixtures",
            language_track="shared",
            description="Shared compatibility fixture specs derived from the combined private-library supplement.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
    )
    write_jsonl(
        package_root("compatibility_fixtures", compat_dataset_id) / "fixtures.jsonl",
        compat_rows,
    )

    summary = {
        "books_total": len(source_records),
        "books_en": sum(1 for record in source_records if record["language"] == "en"),
        "books_zh": sum(1 for record in source_records if record["language"] == "zh"),
        "chapter_candidates_en": len(chapter_rows_by_language.get("en", [])),
        "chapter_candidates_zh": len(chapter_rows_by_language.get("zh", [])),
        "excerpt_seeds_en": len(excerpt_rows_by_language.get("en", [])),
        "excerpt_seeds_zh": len(excerpt_rows_by_language.get("zh", [])),
        "runtime_fixtures_en": len(make_runtime_fixtures(runtime_rows_by_language.get("en", []))),
        "runtime_fixtures_zh": len(make_runtime_fixtures(runtime_rows_by_language.get("zh", []))),
        "compatibility_fixtures_shared": len(compat_rows),
    }

    print("Combined private-library supplement build complete.")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
