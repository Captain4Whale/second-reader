"""Build a private-local bilingual seed corpus from the user's Downloads EPUB pool.

This script:
- screens candidate EPUBs from ~/Downloads against the current evaluation needs
- promotes a selected subset into state/library_sources/
- writes tracked source/corpus/split/local-ref manifests
- writes local-only dataset packages under state/eval_local_datasets/

The local-only packages intentionally carry excerpt text and other private-source
content outside the tracked repo dataset tree.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from src.reading_runtime.provisioning import ensure_canonical_parse


ROOT = Path(__file__).resolve().parents[2]
DOWNLOAD_ROOT = Path.home() / "Downloads"
STATE_LIBRARY_ROOT = ROOT / "state" / "library_sources"
STATE_LOCAL_DATASET_ROOT = ROOT / "state" / "eval_local_datasets"
MANIFEST_ROOT = ROOT / "eval" / "manifests"


CANDIDATE_BOOKS: list[dict[str, Any]] = [
    {
        "source_id": "antifragile_private_en",
        "title": "Antifragile",
        "author": "Nassim Nicholas Taleb",
        "language": "en",
        "download_filename": "Antifragile (Nassim Nicholas Taleb) (Z-Library).epub",
        "promoted_local_path": "en/private/antifragile.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["essayistic", "argumentative", "philosophical", "modern_nonfiction"],
        "suitability_notes": [
            "Good modern English conceptual-pressure book for local meaning-unit and bridge evaluation.",
            "Useful for distinction, reversal, and reconsolidation-worthy later reinterpretation.",
        ],
    },
    {
        "source_id": "fooled_by_randomness_private_en",
        "title": "Fooled by Randomness",
        "author": "Nassim Nicholas Taleb",
        "language": "en",
        "download_filename": "Fooled by Randomness The Hidden Role of Chance in Life and in the Markets (Nassim Nicholas Taleb) (Z-Library).epub",
        "promoted_local_path": "en/private/fooled_by_randomness.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["essayistic", "argumentative", "risk_thought", "modern_nonfiction"],
        "suitability_notes": [
            "Useful for uncertainty, luck, and interpretive-pressure passages.",
            "Complements the older public-domain pool with contemporary argumentative prose.",
        ],
    },
    {
        "source_id": "skin_in_the_game_private_en",
        "title": "Skin in the Game",
        "author": "Nassim Nicholas Taleb",
        "language": "en",
        "download_filename": "Skin In The Game Hidden Asymmetries In Daily Life (Nassim Nicholas Taleb) (Z-Library).epub",
        "promoted_local_path": "en/private/skin_in_the_game.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["essayistic", "argumentative", "ethical_pressure", "modern_nonfiction"],
        "suitability_notes": [
            "Good for asymmetry, accountability, and bridge-worthy argument turns.",
        ],
    },
    {
        "source_id": "black_swan_private_en",
        "title": "The Black Swan",
        "author": "Nassim Nicholas Taleb",
        "language": "en",
        "download_filename": "The Black Swan Second Edition The Impact of the Highly Improbable With a New Section On Robustness and Fragility (Nassim Nicholas Taleb) (Z-Library).epub",
        "promoted_local_path": None,
        "screening_status": "reserve_candidate",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["essayistic", "argumentative", "allusion_dense", "modern_nonfiction"],
        "suitability_notes": [
            "Strong modern source, but large and too Taleb-heavy for the first private supplement slice.",
        ],
    },
    {
        "source_id": "value_of_others_private_en",
        "title": "The Value of Others",
        "author": "Orion Taraban",
        "language": "en",
        "download_filename": "_OceanofPDF.com_The_Value_of_Others_-_Orion_Taraban.epub",
        "promoted_local_path": "en/private/the_value_of_others.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["philosophical", "relationship_thought", "modern_nonfiction"],
        "suitability_notes": [
            "Useful modern philosophical prose with strong reaction-worthy lines and local conceptual distinctions.",
        ],
    },
    {
        "source_id": "making_of_a_manager_private_en",
        "title": "The Making of a Manager",
        "author": "Julie Zhuo",
        "language": "en",
        "download_filename": "The Making of a Manager What to Do When Everyone Looks to You (Julie Zhuo) (Z-Library).epub",
        "promoted_local_path": "en/private/the_making_of_a_manager.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["narrative_reflective", "management", "modern_nonfiction"],
        "suitability_notes": [
            "Adds reflective managerial prose and contemporary narrative examples.",
        ],
    },
    {
        "source_id": "inspired_private_en",
        "title": "INSPIRED",
        "author": "Marty Cagan et al.",
        "language": "en",
        "download_filename": "INSPIRED How to Create Tech Products Customers Love (Marty Cagan, Christian Idiodi, Lea Hickman etc.) (Z-Library).epub",
        "promoted_local_path": "en/private/inspired.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["expository", "product_thought", "modern_nonfiction"],
        "suitability_notes": [
            "Useful modern expository/product book with many short chapter units and practical distinctions.",
        ],
    },
    {
        "source_id": "chance_private_en",
        "title": "Chance",
        "author": "Joseph Conrad",
        "language": "en",
        "download_filename": "joseph-conrad_chance.epub",
        "promoted_local_path": "en/private/chance.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["narrative_reflective", "novel", "social_detail"],
        "suitability_notes": [
            "Useful narrative supplement so the private seed does not become all modern nonfiction.",
        ],
    },
    {
        "source_id": "biji_de_fangfa_private_zh",
        "title": "笔记的方法",
        "author": "刘少楠, 刘白光",
        "language": "zh",
        "download_filename": "笔记的方法 (刘少楠, 刘白光) (Z-Library).epub",
        "promoted_local_path": "zh/private/bijidefangfa.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["expository", "modern_vernacular", "method"],
        "suitability_notes": [
            "Adds modern vernacular Chinese expository prose to complement the older seed pool.",
        ],
    },
    {
        "source_id": "fooled_by_randomness_private_zh",
        "title": "随机漫步的傻瓜",
        "author": "纳西姆·尼古拉斯·塔勒布",
        "language": "zh",
        "download_filename": "随机漫步的傻瓜：发现市场和人生中的隐藏机遇 = Fooled by Randomness The Hidden Role of Chance in Life and in the Markets ( etc.) (Z-Library).epub",
        "promoted_local_path": "zh/private/suijimanbudesagua.epub",
        "screening_status": "promote_seed",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["essayistic", "argumentative", "modern_vernacular", "risk_thought"],
        "suitability_notes": [
            "Adds contemporary Chinese-language argumentative prose with strong chapter lengths for resume and span tests.",
        ],
    },
    {
        "source_id": "cracking_pm_career_private_en",
        "title": "Cracking the PM Career",
        "author": "Jackie Bavaro, Gayle McDowell",
        "language": "en",
        "download_filename": "Cracking the PM Career The Skills, Frameworks, and Practices To Become a Great Product Manager (Cracking the Interview … (Jackie Bavaro, Gayle McDowell) (Z-Library).epub",
        "promoted_local_path": None,
        "screening_status": "reserve_candidate",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["career_guidance", "framework_heavy", "modern_nonfiction"],
        "suitability_notes": [
            "Parseable and potentially useful for later expository/runtime slices, but lower priority for the first reading-quality corpus.",
        ],
    },
    {
        "source_id": "cracking_pm_interview_private_en",
        "title": "Cracking the PM Interview",
        "author": "Gayle Laakmann McDowell",
        "language": "en",
        "download_filename": "Cracking the PM Interview - How to Land a Product Manager Job in Technology (Gayle Laakmann McDowell) (Z-Library).epub",
        "promoted_local_path": None,
        "screening_status": "reject_first_corpus",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["interview_prep", "qa_heavy", "modern_nonfiction"],
        "suitability_notes": [
            "Rejected for the first corpus because the EPUB collapses into one full-content chapter and overweights interview-prep style instead of stable chaptered prose.",
        ],
    },
    {
        "source_id": "decode_and_conquer_private_en",
        "title": "Decode and Conquer",
        "author": "Lewis C. Lin",
        "language": "en",
        "download_filename": "Decode and Conquer Answers to Product Management Interviews (Lewis C. Lin) (Z-Library).epub",
        "promoted_local_path": None,
        "screening_status": "reserve_candidate",
        "storage_policy": "private-local",
        "origin": "manual-local-download",
        "type_tags": ["interview_prep", "qa_heavy", "framework_heavy"],
        "suitability_notes": [
            "Usable for future structured-runtime experiments, but not a first-tier co-reading benchmark source.",
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


def select_chapters(chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not chapters:
        return []
    if len(chapters) <= 2:
        return chapters
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
        "selection_status": "private_seed_selected",
        "notes": "Auto-selected private local seed chapter unit from canonical parsed substrate.",
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
                    "fixture_status": "private_seed_generated",
                    "notes": "Auto-generated runtime/resume seed fixture from a private local chapter unit.",
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
    fractions = [0.2, 0.65] if source["language"] == "en" else [0.35, 0.7]
    chapter_number = int(chapter.get("chapter_number") or 0)
    chapter_title = chapter.get("title") or chapter.get("chapter_heading") or f"Chapter {chapter_number}"
    cases: list[dict[str, Any]] = []
    for index, fraction in enumerate(fractions, start=1):
        start, end = excerpt_window(sentences, fraction)
        window = sentences[start:end]
        cases.append(
            {
                "case_id": f"{source['source_id']}__ch{chapter_number}__private_seed_{index}",
                "split": "private_seed_auto",
                "source_id": source["source_id"],
                "book_title": source["title"],
                "author": source["author"],
                "output_language": source["language"],
                "chapter_title": chapter_title,
                "chapter_number": chapter_number,
                "start_sentence_id": window[0]["sentence_id"],
                "end_sentence_id": window[-1]["sentence_id"],
                "excerpt_text": "\n".join(sentence.get("text", "") for sentence in window).strip(),
                "tags": ["private_seed_auto_extracted", *source["type_tags"]],
                "notes": "Auto-extracted private local seed excerpt. Requires later manual curation before benchmark promotion.",
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
                "notes": "Spec-level compatibility audit fixture for a private local source. Requires live runtime outputs to materialize.",
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
        "storage_mode": "private-local",
    }


def promote_source(candidate: dict[str, Any]) -> Path | None:
    promoted_local_path = candidate.get("promoted_local_path")
    if not promoted_local_path:
        return None
    source_path = DOWNLOAD_ROOT / candidate["download_filename"]
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    dest = STATE_LIBRARY_ROOT / promoted_local_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or sha256_file(dest) != sha256_file(source_path):
        shutil.copy2(source_path, dest)
    return dest


def main() -> None:
    source_records: list[dict[str, Any]] = []
    selected_records: list[dict[str, Any]] = []
    chapter_rows_by_language: dict[str, list[dict[str, Any]]] = {"en": [], "zh": []}
    excerpt_rows_by_language: dict[str, list[dict[str, Any]]] = {"en": [], "zh": []}

    for candidate in CANDIDATE_BOOKS:
        source_path = DOWNLOAD_ROOT / candidate["download_filename"]
        if not source_path.exists():
            raise FileNotFoundError(source_path)

        promoted_path = promote_source(candidate) if candidate["screening_status"] == "promote_seed" else None
        parse_input = promoted_path or source_path
        provisioned = ensure_canonical_parse(parse_input)
        chapters = load_chapters(provisioned.output_dir)
        sentence_counts = [len(ch.get("sentences") or []) for ch in chapters]
        paragraph_counts = [len(ch.get("paragraphs") or []) for ch in chapters]
        selected = select_chapters(chapters) if candidate["screening_status"] == "promote_seed" else []

        record = {
            **candidate,
            "download_filename": source_path.name,
            "download_sha256": sha256_file(source_path),
            "download_file_size": source_path.stat().st_size,
            "relative_local_path": str(promoted_path.relative_to(ROOT)) if promoted_path else None,
            "local_sha256": sha256_file(promoted_path) if promoted_path else None,
            "local_file_size": promoted_path.stat().st_size if promoted_path else None,
            "output_dir": str(provisioned.output_dir),
            "detected_book_language": provisioned.book_language,
            "output_language": provisioned.output_language,
            "chapter_count": len(chapters),
            "sentence_count_total": sum(sentence_counts),
            "median_chapter_sentences": sorted(sentence_counts)[len(sentence_counts) // 2] if sentence_counts else 0,
            "median_chapter_paragraphs": sorted(paragraph_counts)[len(paragraph_counts) // 2] if paragraph_counts else 0,
            "screening_first_titles": [
                ch.get("title") or ch.get("chapter_heading") or ch.get("id") for ch in chapters[:5]
            ],
            "selected_seed_chapter_numbers": [int(ch.get("chapter_number") or 0) for ch in selected],
            "selected_seed_chapter_ids": [
                str(ch.get("id") or f"chapter-{int(ch.get('chapter_number') or 0)}") for ch in selected
            ],
        }
        source_records.append(record)

        if candidate["screening_status"] != "promote_seed":
            continue

        selected_records.append(record)
        for chapter in selected:
            row = chapter_record(candidate, chapter, provisioned.output_dir)
            chapter_rows_by_language[candidate["language"]].append(row)
            excerpt_rows_by_language[candidate["language"]].extend(make_excerpt_cases(candidate, chapter))

    source_manifest_path = MANIFEST_ROOT / "source_books" / "attentional_v2_private_downloads_screen_v1.json"
    local_refs_manifest_path = MANIFEST_ROOT / "local_refs" / "attentional_v2_private_downloads_seed_v1.json"
    corpora_manifest_path = MANIFEST_ROOT / "corpora" / "attentional_v2_private_downloads_bilingual_v1.json"
    splits_manifest_path = MANIFEST_ROOT / "splits" / "attentional_v2_private_downloads_bilingual_v1.json"

    write_json(
        source_manifest_path,
        {
            "manifest_id": "attentional_v2_private_downloads_screen_v1",
            "description": "Tracked screening inventory for private local EPUB candidates sourced from the user's Downloads folder.",
            "books": source_records,
        },
    )

    package_ids = {
        "chapter_corpora": {
            "en": "attentional_v2_private_chapters_en_v1",
            "zh": "attentional_v2_private_chapters_zh_v1",
        },
        "runtime_fixtures": {
            "en": "attentional_v2_private_runtime_en_v1",
            "zh": "attentional_v2_private_runtime_zh_v1",
        },
        "excerpt_cases": {
            "en": "attentional_v2_private_excerpt_en_v1",
            "zh": "attentional_v2_private_excerpt_zh_v1",
        },
        "compatibility_fixtures": {
            "shared": "attentional_v2_private_compat_shared_v1",
        },
    }

    local_package_refs = []
    for family, tracks in package_ids.items():
        for track, dataset_id in tracks.items():
            local_package_refs.append(
                {
                    "dataset_id": dataset_id,
                    "family": family,
                    "language_track": track,
                    "relative_local_path": str(
                        (STATE_LOCAL_DATASET_ROOT / family / dataset_id).relative_to(ROOT)
                    ),
                }
            )

    write_json(
        local_refs_manifest_path,
        {
            "manifest_id": "attentional_v2_private_downloads_seed_v1_local_refs",
            "description": "Local source-file and local-package references for the private Downloads-based attentional_v2 seed supplement.",
            "source_refs": [
                {
                    "source_id": record["source_id"],
                    "relative_local_path": record["relative_local_path"],
                    "sha256": record["local_sha256"],
                    "file_size": record["local_file_size"],
                }
                for record in selected_records
            ],
            "local_dataset_packages": local_package_refs,
        },
    )

    write_json(
        corpora_manifest_path,
        {
            "manifest_id": "attentional_v2_private_downloads_bilingual_v1",
            "description": "Private local bilingual source corpus selected from the user's Downloads pool for attentional_v2 evaluation supplementation.",
            "language_tracks": {
                "en": [record["source_id"] for record in selected_records if record["language"] == "en"],
                "zh": [record["source_id"] for record in selected_records if record["language"] == "zh"],
            },
        },
    )
    write_json(
        splits_manifest_path,
        {
            "manifest_id": "attentional_v2_private_downloads_bilingual_v1_splits",
            "description": "Split definitions for the private Downloads-based attentional_v2 seed supplement.",
            "splits": {
                "private_candidate_pool": {
                    "en": [record["source_id"] for record in source_records if record["language"] == "en"],
                    "zh": [record["source_id"] for record in source_records if record["language"] == "zh"],
                },
                "selected_private_seed": {
                    "en": [record["source_id"] for record in selected_records if record["language"] == "en"],
                    "zh": [record["source_id"] for record in selected_records if record["language"] == "zh"],
                },
            },
        },
    )

    source_manifest_refs = [
        str(source_manifest_path.relative_to(ROOT)),
        str(local_refs_manifest_path.relative_to(ROOT)),
        str(corpora_manifest_path.relative_to(ROOT)),
    ]
    split_refs = [str(splits_manifest_path.relative_to(ROOT))]

    runtime_en = make_runtime_fixtures(chapter_rows_by_language["en"])
    runtime_zh = make_runtime_fixtures(chapter_rows_by_language["zh"])
    compat_shared = make_compatibility_fixtures(
        chapter_rows_by_language["en"] + chapter_rows_by_language["zh"]
    )

    def package_root(family: str, dataset_id: str) -> Path:
        return STATE_LOCAL_DATASET_ROOT / family / dataset_id

    write_json(
        package_root("chapter_corpora", "attentional_v2_private_chapters_en_v1") / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_private_chapters_en_v1",
            family="chapter_corpora",
            language_track="en",
            description="English private-local chapter corpus derived from screened Downloads books for attentional_v2 evaluation supplementation.",
            primary_file="chapters.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        package_root("chapter_corpora", "attentional_v2_private_chapters_en_v1") / "chapters.jsonl",
        chapter_rows_by_language["en"],
    )
    write_json(
        package_root("chapter_corpora", "attentional_v2_private_chapters_zh_v1") / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_private_chapters_zh_v1",
            family="chapter_corpora",
            language_track="zh",
            description="Chinese private-local chapter corpus derived from screened Downloads books for attentional_v2 evaluation supplementation.",
            primary_file="chapters.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        package_root("chapter_corpora", "attentional_v2_private_chapters_zh_v1") / "chapters.jsonl",
        chapter_rows_by_language["zh"],
    )

    write_json(
        package_root("runtime_fixtures", "attentional_v2_private_runtime_en_v1") / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_private_runtime_en_v1",
            family="runtime_fixtures",
            language_track="en",
            description="English private-local runtime/resume fixtures derived from screened Downloads books.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        package_root("runtime_fixtures", "attentional_v2_private_runtime_en_v1") / "fixtures.jsonl",
        runtime_en,
    )
    write_json(
        package_root("runtime_fixtures", "attentional_v2_private_runtime_zh_v1") / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_private_runtime_zh_v1",
            family="runtime_fixtures",
            language_track="zh",
            description="Chinese private-local runtime/resume fixtures derived from screened Downloads books.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        package_root("runtime_fixtures", "attentional_v2_private_runtime_zh_v1") / "fixtures.jsonl",
        runtime_zh,
    )

    write_json(
        package_root("excerpt_cases", "attentional_v2_private_excerpt_en_v1") / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_private_excerpt_en_v1",
            family="excerpt_cases",
            language_track="en",
            description="English private-local excerpt seed cases auto-extracted from screened Downloads books.",
            primary_file="cases.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        package_root("excerpt_cases", "attentional_v2_private_excerpt_en_v1") / "cases.jsonl",
        excerpt_rows_by_language["en"],
    )
    write_json(
        package_root("excerpt_cases", "attentional_v2_private_excerpt_zh_v1") / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_private_excerpt_zh_v1",
            family="excerpt_cases",
            language_track="zh",
            description="Chinese private-local excerpt seed cases auto-extracted from screened Downloads books.",
            primary_file="cases.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        package_root("excerpt_cases", "attentional_v2_private_excerpt_zh_v1") / "cases.jsonl",
        excerpt_rows_by_language["zh"],
    )

    write_json(
        package_root("compatibility_fixtures", "attentional_v2_private_compat_shared_v1") / "manifest.json",
        dataset_manifest(
            dataset_id="attentional_v2_private_compat_shared_v1",
            family="compatibility_fixtures",
            language_track="shared",
            description="Shared private-local compatibility fixture specs derived from screened Downloads books.",
            primary_file="fixtures.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
        ),
    )
    write_jsonl(
        package_root("compatibility_fixtures", "attentional_v2_private_compat_shared_v1") / "fixtures.jsonl",
        compat_shared,
    )

    print("Private Downloads seed build complete.")
    print(f"Promoted source books: {len(selected_records)}")
    print(f"English chapter rows: {len(chapter_rows_by_language['en'])}")
    print(f"Chinese chapter rows: {len(chapter_rows_by_language['zh'])}")
    print(f"English runtime fixtures: {len(runtime_en)}")
    print(f"Chinese runtime fixtures: {len(runtime_zh)}")
    print(f"English excerpt cases: {len(excerpt_rows_by_language['en'])}")
    print(f"Chinese excerpt cases: {len(excerpt_rows_by_language['zh'])}")
    print(f"Compatibility specs: {len(compat_shared)}")


if __name__ == "__main__":
    main()
