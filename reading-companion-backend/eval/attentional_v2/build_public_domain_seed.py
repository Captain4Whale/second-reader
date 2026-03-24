"""Build the first public-domain bilingual seed corpus for attentional_v2 evaluation.

This script:
- inspects downloaded source EPUBs under state/library_sources/
- ensures canonical parse artifacts exist
- writes tracked source/corpus/split manifests
- writes seed dataset packages for chapter, runtime, excerpt, and compatibility work

The seed packages are intentionally honest:
- chapter and runtime datasets are directly grounded in parsed substrate
- excerpt cases are auto-extracted seeds that still require later manual curation
- compatibility fixtures are spec-level audit targets until live runtime outputs are generated
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.reading_runtime.provisioning import ensure_canonical_parse


ROOT = Path(__file__).resolve().parents[2]
STATE_LIBRARY_ROOT = ROOT / "state" / "library_sources"
DATASET_ROOT = ROOT / "eval" / "datasets"
MANIFEST_ROOT = ROOT / "eval" / "manifests"


SOURCE_BOOKS: list[dict[str, Any]] = [
    {
        "source_id": "walden_205_en",
        "title": "Walden, and On The Duty Of Civil Disobedience",
        "author": "Henry David Thoreau",
        "language": "en",
        "local_path": "en/walden_205.epub",
        "source_url": "https://www.gutenberg.org/ebooks/205",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["expository", "philosophical", "essayistic"],
        "suitability_notes": [
            "Good for conceptual pressure and reflective prose.",
            "Useful for local closure and chapter-scale accumulation.",
        ],
    },
    {
        "source_id": "souls_of_black_folk_408_en",
        "title": "The Souls of Black Folk",
        "author": "W. E. B. Du Bois",
        "language": "en",
        "local_path": "en/souls_of_black_folk_408.epub",
        "source_url": "https://www.gutenberg.org/ebooks/408",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["essayistic", "argumentative", "social_thought"],
        "suitability_notes": [
            "Good for argumentative and reflective chapter passages.",
            "Likely useful for bridge-worthy concepts and durable trace.",
        ],
    },
    {
        "source_id": "pride_and_prejudice_1342_en",
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "language": "en",
        "local_path": "en/pride_and_prejudice_1342.epub",
        "source_url": "https://www.gutenberg.org/ebooks/1342",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["narrative_reflective", "novel", "social_detail"],
        "suitability_notes": [
            "Good for character judgment, revision, and later reinterpretation.",
        ],
    },
    {
        "source_id": "moby_dick_2701_en",
        "title": "Moby Dick; Or, The Whale",
        "author": "Herman Melville",
        "language": "en",
        "local_path": "en/moby_dick_2701.epub",
        "source_url": "https://www.gutenberg.org/ebooks/2701",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["narrative_reflective", "allusion_dense", "novel"],
        "suitability_notes": [
            "Good for motif, callback, and chapter-scale accumulation.",
        ],
    },
    {
        "source_id": "middlemarch_145_en",
        "title": "Middlemarch",
        "author": "George Eliot",
        "language": "en",
        "local_path": "en/middlemarch_145.epub",
        "source_url": "https://www.gutenberg.org/ebooks/145",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["narrative_reflective", "novel", "social_thought"],
        "suitability_notes": [
            "Good long-span reflective novel for chapter trajectory comparisons.",
        ],
    },
    {
        "source_id": "zhaohua_xishi_25271_zh",
        "title": "朝花夕拾",
        "author": "魯迅",
        "language": "zh",
        "local_path": "zh/zhaohua_xishi_25271.epub",
        "source_url": "https://www.gutenberg.org/ebooks/25271",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["essayistic", "narrative_reflective", "modern_vernacular"],
        "suitability_notes": [
            "Important modern vernacular Chinese track.",
            "Good for reflective prose and durable trace.",
        ],
    },
    {
        "source_id": "nahan_27166_zh",
        "title": "吶喊",
        "author": "魯迅",
        "language": "zh",
        "local_path": "zh/nahan_27166.epub",
        "source_url": "https://www.gutenberg.org/ebooks/27166",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["narrative_reflective", "short_story", "modern_vernacular"],
        "suitability_notes": [
            "Useful modern vernacular Chinese fiction track.",
            "Good for tension, turn, and anchored reactions.",
        ],
    },
    {
        "source_id": "rulin_waishi_24032_zh",
        "title": "儒林外史",
        "author": "吳敬梓",
        "language": "zh",
        "local_path": "zh/rulin_waishi_24032.epub",
        "source_url": "https://www.gutenberg.org/ebooks/24032",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["argumentative", "satirical", "vernacular_classic"],
        "suitability_notes": [
            "Good for social critique and satirical pressure.",
        ],
    },
    {
        "source_id": "laocan_youji_25124_zh",
        "title": "老殘遊記",
        "author": "劉鶚",
        "language": "zh",
        "local_path": "zh/laocan_youji_25124.epub",
        "source_url": "https://www.gutenberg.org/ebooks/25124",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["narrative_reflective", "social_critique", "vernacular_classic"],
        "suitability_notes": [
            "Good for social reflection and longer Chinese narrative spans.",
        ],
    },
    {
        "source_id": "jinghua_yuan_25377_zh",
        "title": "鏡花緣",
        "author": "李汝珍",
        "language": "zh",
        "local_path": "zh/jinghua_yuan_25377.epub",
        "source_url": "https://www.gutenberg.org/ebooks/25377",
        "storage_policy": "private-local",
        "origin": "public-domain-source",
        "type_tags": ["allusion_dense", "fantasy", "vernacular_classic"],
        "suitability_notes": [
            "Good for unusual transitions, motifs, and bridge opportunities.",
        ],
    },
]


QUESTION_IDS_BY_FAMILY = {
    "excerpt_cases": [
        "EQ-CM-002",
        "EQ-AV2-001",
        "EQ-AV2-002",
        "EQ-AV2-003",
        "EQ-AV2-004",
        "EQ-AV2-005",
        "EQ-AV2-006",
    ],
    "chapter_corpora": [
        "EQ-CM-001",
        "EQ-CM-003",
        "EQ-CM-004",
        "EQ-GATE-003",
    ],
    "runtime_fixtures": [
        "EQ-CM-005",
        "EQ-AV2-007",
        "EQ-GATE-001",
        "EQ-GATE-003",
    ],
    "compatibility_fixtures": [
        "EQ-AV2-008",
        "EQ-GATE-002",
    ],
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_chapters(output_dir: Path) -> list[dict[str, Any]]:
    book_document = json.loads((output_dir / "public" / "book_document.json").read_text(encoding="utf-8"))
    return book_document["chapters"]


def chapter_sentence_count(chapter: dict[str, Any]) -> int:
    return len(chapter.get("sentences") or [])


def select_chapters(chapters: list[dict[str, Any]], language: str) -> list[dict[str, Any]]:
    if not chapters:
        return []
    if len(chapters) <= 2:
        return chapters
    if language == "en":
        indices = sorted({0, len(chapters) // 2})
    else:
        indices = sorted({0, len(chapters) // 2})
    return [chapters[index] for index in indices]


def chapter_record(source: dict[str, Any], chapter: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    sentences = chapter.get("sentences") or []
    paragraphs = chapter.get("paragraphs") or []
    chapter_number = int(chapter.get("chapter_number") or 0)
    chapter_id = str(chapter.get("id") or f"chapter-{chapter_number}")
    title = chapter.get("title") or chapter.get("chapter_heading") or f"Chapter {chapter_number}"
    return {
        "chapter_case_id": f"{source['source_id']}__{chapter_id}",
        "source_id": source["source_id"],
        "book_title": source["title"],
        "author": source["author"],
        "language_track": source["language"],
        "type_tags": source["type_tags"],
        "output_dir": str(output_dir),
        "chapter_id": chapter_id,
        "chapter_number": chapter_number,
        "chapter_title": title,
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "href": chapter.get("href"),
        "spine_index": chapter.get("spine_index"),
        "selection_status": "seed_selected",
        "notes": "Auto-selected seed chapter unit from canonical parsed substrate.",
    }


def make_runtime_fixtures(chapter_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    for row in chapter_rows:
        sentence_count = int(row["sentence_count"])
        if sentence_count < 8:
            continue
        positions = [
            ("warm", max(1, int(sentence_count * 0.2))),
            ("cold", max(1, int(sentence_count * 0.5))),
            ("reconstitution", max(1, int(sentence_count * 0.8))),
        ]
        for resume_kind, sentence_index in positions:
            fixtures.append(
                {
                    "fixture_id": f"{row['chapter_case_id']}__{resume_kind}",
                    "source_id": row["source_id"],
                    "language_track": row["language_track"],
                    "chapter_case_id": row["chapter_case_id"],
                    "chapter_number": row["chapter_number"],
                    "chapter_title": row["chapter_title"],
                    "resume_kind": resume_kind,
                    "target_sentence_index": sentence_index,
                    "fixture_status": "seed_generated",
                    "notes": "Auto-generated runtime/resume seed fixture from chapter unit.",
                }
            )
    return fixtures


def excerpt_window(sentences: list[dict[str, Any]], center_fraction: float, radius: int = 3) -> tuple[int, int]:
    if not sentences:
        return (0, 0)
    center = max(0, min(len(sentences) - 1, int(len(sentences) * center_fraction)))
    start = max(0, center - radius)
    end = min(len(sentences), center + radius)
    if end <= start:
        end = min(len(sentences), start + 1)
    return start, end


def make_excerpt_cases(source: dict[str, Any], chapter: dict[str, Any]) -> list[dict[str, Any]]:
    sentences = chapter.get("sentences") or []
    if len(sentences) < 4:
        return []
    fractions = [0.2, 0.65] if source["language"] == "en" else [0.35]
    chapter_number = int(chapter.get("chapter_number") or 0)
    chapter_title = chapter.get("title") or chapter.get("chapter_heading") or f"Chapter {chapter_number}"
    cases: list[dict[str, Any]] = []
    for index, fraction in enumerate(fractions, start=1):
        start, end = excerpt_window(sentences, fraction)
        window = sentences[start:end]
        cases.append(
            {
                "case_id": f"{source['source_id']}__ch{chapter_number}__seed_{index}",
                "split": "seed_auto",
                "source_id": source["source_id"],
                "book_title": source["title"],
                "author": source["author"],
                "output_language": source["language"],
                "chapter_title": chapter_title,
                "chapter_number": chapter_number,
                "start_sentence_id": window[0]["sentence_id"],
                "end_sentence_id": window[-1]["sentence_id"],
                "excerpt_text": "\n".join(sentence.get("text", "") for sentence in window).strip(),
                "tags": ["seed_auto_extracted", *source["type_tags"]],
                "notes": "Auto-extracted seed excerpt. Requires later manual curation before benchmark promotion.",
            }
        )
    return cases


def make_compatibility_fixtures(chapter_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    for row in chapter_rows:
        fixtures.append(
            {
                "fixture_id": f"{row['chapter_case_id']}__compat",
                "source_id": row["source_id"],
                "language_track": row["language_track"],
                "chapter_case_id": row["chapter_case_id"],
                "target_surfaces": ["analysis_state", "activity", "chapter_detail", "marks"],
                "fixture_kind": "compat_projection_audit_spec",
                "fixture_status": "spec_only",
                "notes": "Spec-level compatibility audit fixture. Requires live attentional runtime outputs to materialize.",
            }
        )
    return fixtures


def dataset_manifest(
    *,
    dataset_id: str,
    family: str,
    language_track: str,
    description: str,
    primary_file: str,
    source_manifest_refs: list[str],
    split_refs: list[str],
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "family": family,
        "language_track": language_track,
        "version": "1",
        "description": description,
        "primary_file": primary_file,
        "question_ids": QUESTION_IDS_BY_FAMILY[family],
        "source_manifest_refs": source_manifest_refs,
        "split_refs": split_refs,
    }


def main() -> None:
    source_records: list[dict[str, Any]] = []
    chapter_rows_by_language: dict[str, list[dict[str, Any]]] = {"en": [], "zh": []}
    excerpt_rows_by_language: dict[str, list[dict[str, Any]]] = {"en": [], "zh": []}

    for source in SOURCE_BOOKS:
        local_file = STATE_LIBRARY_ROOT / source["local_path"]
        if not local_file.exists():
            raise FileNotFoundError(local_file)
        sha256 = sha256_file(local_file)
        provisioned = ensure_canonical_parse(local_file)
        chapters = load_chapters(provisioned.output_dir)
        selected = select_chapters(chapters, source["language"])
        source_records.append(
            {
                **source,
                "relative_local_path": str(local_file.relative_to(ROOT)),
                "sha256": sha256,
                "file_size": local_file.stat().st_size,
                "output_dir": str(provisioned.output_dir),
                "detected_book_language": provisioned.book_language,
                "output_language": provisioned.output_language,
                "chapter_count": len(chapters),
                "selected_seed_chapter_numbers": [int(ch.get("chapter_number") or 0) for ch in selected],
                "selected_seed_chapter_ids": [str(ch.get("id") or f"chapter-{int(ch.get('chapter_number') or 0)}") for ch in selected],
            }
        )
        for chapter in selected:
            row = chapter_record(source, chapter, provisioned.output_dir)
            chapter_rows_by_language[source["language"]].append(row)
            excerpt_rows_by_language[source["language"]].extend(make_excerpt_cases(source, chapter))

    # manifests
    write_json(
        MANIFEST_ROOT / "source_books" / "attentional_v2_public_domain_seed_v1.json",
        {
            "manifest_id": "attentional_v2_public_domain_seed_v1",
            "description": "Tracked source-book inventory for the first bilingual public-domain seed corpus used in attentional_v2 evaluation preparation.",
            "books": source_records,
        },
    )
    write_json(
        MANIFEST_ROOT / "local_refs" / "attentional_v2_public_domain_seed_v1.json",
        {
            "manifest_id": "attentional_v2_public_domain_seed_v1_local_refs",
            "description": "Local source-file references and checksums for the public-domain attentional_v2 seed corpus.",
            "refs": [
                {
                    "source_id": record["source_id"],
                    "relative_local_path": record["relative_local_path"],
                    "sha256": record["sha256"],
                    "file_size": record["file_size"],
                }
                for record in source_records
            ],
        },
    )
    write_json(
        MANIFEST_ROOT / "corpora" / "attentional_v2_public_domain_seed_bilingual_v1.json",
        {
            "manifest_id": "attentional_v2_public_domain_seed_bilingual_v1",
            "description": "Bilingual public-domain source corpus for the first attentional_v2 evaluation build.",
            "language_tracks": {
                "en": [record["source_id"] for record in source_records if record["language"] == "en"],
                "zh": [record["source_id"] for record in source_records if record["language"] == "zh"],
            },
        },
    )
    write_json(
        MANIFEST_ROOT / "splits" / "attentional_v2_public_domain_seed_bilingual_v1.json",
        {
            "manifest_id": "attentional_v2_public_domain_seed_bilingual_v1_splits",
            "description": "Initial bilingual split definitions for the attentional_v2 public-domain seed build.",
            "splits": {
                "seed_candidate_pool": {
                    "en": [record["source_id"] for record in source_records if record["language"] == "en"],
                    "zh": [record["source_id"] for record in source_records if record["language"] == "zh"],
                }
            },
        },
    )

    source_manifest_refs = [
        "eval/manifests/source_books/attentional_v2_public_domain_seed_v1.json",
        "eval/manifests/local_refs/attentional_v2_public_domain_seed_v1.json",
        "eval/manifests/corpora/attentional_v2_public_domain_seed_bilingual_v1.json",
    ]
    split_refs = [
        "eval/manifests/splits/attentional_v2_public_domain_seed_bilingual_v1.json",
    ]

    # chapter datasets
    write_json(
        DATASET_ROOT / "chapter_corpora" / "attentional_v2_chapters_en_v1" / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_chapters_en_v1",
            family="chapter_corpora",
            language_track="en",
            description="English seed chapter corpus grounded in the first public-domain attentional_v2 source pool.",
            primary_file="chapters.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        DATASET_ROOT / "chapter_corpora" / "attentional_v2_chapters_en_v1" / "chapters.jsonl",
        chapter_rows_by_language["en"],
    )
    write_json(
        DATASET_ROOT / "chapter_corpora" / "attentional_v2_chapters_zh_v1" / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_chapters_zh_v1",
            family="chapter_corpora",
            language_track="zh",
            description="Chinese seed chapter corpus grounded in the first public-domain attentional_v2 source pool.",
            primary_file="chapters.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        DATASET_ROOT / "chapter_corpora" / "attentional_v2_chapters_zh_v1" / "chapters.jsonl",
        chapter_rows_by_language["zh"],
    )

    # runtime fixtures
    runtime_en = make_runtime_fixtures(chapter_rows_by_language["en"])
    runtime_zh = make_runtime_fixtures(chapter_rows_by_language["zh"])
    write_json(
        DATASET_ROOT / "runtime_fixtures" / "attentional_v2_runtime_en_v1" / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_runtime_en_v1",
            family="runtime_fixtures",
            language_track="en",
            description="English runtime/resume seed fixtures derived from the attentional_v2 public-domain chapter corpus.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        DATASET_ROOT / "runtime_fixtures" / "attentional_v2_runtime_en_v1" / "fixtures.jsonl",
        runtime_en,
    )
    write_json(
        DATASET_ROOT / "runtime_fixtures" / "attentional_v2_runtime_zh_v1" / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_runtime_zh_v1",
            family="runtime_fixtures",
            language_track="zh",
            description="Chinese runtime/resume seed fixtures derived from the attentional_v2 public-domain chapter corpus.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        DATASET_ROOT / "runtime_fixtures" / "attentional_v2_runtime_zh_v1" / "fixtures.jsonl",
        runtime_zh,
    )

    # excerpt datasets
    write_json(
        DATASET_ROOT / "excerpt_cases" / "attentional_v2_excerpt_en_v1" / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_excerpt_en_v1",
            family="excerpt_cases",
            language_track="en",
            description="English auto-extracted seed excerpt cases from the public-domain attentional_v2 corpus. These require later manual curation before benchmark promotion.",
            primary_file="cases.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        DATASET_ROOT / "excerpt_cases" / "attentional_v2_excerpt_en_v1" / "cases.jsonl",
        excerpt_rows_by_language["en"],
    )
    write_json(
        DATASET_ROOT / "excerpt_cases" / "attentional_v2_excerpt_zh_v1" / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_excerpt_zh_v1",
            family="excerpt_cases",
            language_track="zh",
            description="Chinese auto-extracted seed excerpt cases from the public-domain attentional_v2 corpus. These require later manual curation before benchmark promotion.",
            primary_file="cases.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        DATASET_ROOT / "excerpt_cases" / "attentional_v2_excerpt_zh_v1" / "cases.jsonl",
        excerpt_rows_by_language["zh"],
    )

    # compatibility fixtures
    compat_rows = make_compatibility_fixtures(
        chapter_rows_by_language["en"] + chapter_rows_by_language["zh"]
    )
    write_json(
        DATASET_ROOT / "compatibility_fixtures" / "attentional_v2_compat_shared_v1" / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_compat_shared_v1",
            family="compatibility_fixtures",
            language_track="shared",
            description="Shared compatibility audit specs for attentional_v2 public-surface projection. These are spec-level fixtures until live runtime outputs are generated.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        DATASET_ROOT / "compatibility_fixtures" / "attentional_v2_compat_shared_v1" / "fixtures.jsonl",
        compat_rows,
    )

    print("Seed corpus build complete.")
    print(f"English chapter rows: {len(chapter_rows_by_language['en'])}")
    print(f"Chinese chapter rows: {len(chapter_rows_by_language['zh'])}")
    print(f"English runtime fixtures: {len(runtime_en)}")
    print(f"Chinese runtime fixtures: {len(runtime_zh)}")
    print(f"English excerpt cases: {len(excerpt_rows_by_language['en'])}")
    print(f"Chinese excerpt cases: {len(excerpt_rows_by_language['zh'])}")
    print(f"Compatibility specs: {len(compat_rows)}")


if __name__ == "__main__":
    main()
