"""Build a combined private-library local supplement from all user-provided books.

This script combines:
- the earlier private Downloads batch
- the newer /Users/baiweijiang/Documents/BOOK batch

It then:
- promotes every reachable book into the durable local source library
- screens every book through the canonical parse pipeline
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

from corpus_builder import (
    ROOT,
    MANIFEST_ROOT,
    STATE_LOCAL_DATASET_ROOT,
    CandidateSpec,
    chapter_row_from_candidate,
    dataset_manifest,
    load_book_document,
    make_compatibility_fixtures,
    make_runtime_fixtures,
    promote_candidate,
    screen_source_book,
    write_json,
    write_jsonl,
)


DOWNLOAD_ROOT = Path.home() / "Downloads"
BOOK_ROOT = Path("/Users/baiweijiang/Documents/BOOK")

SOURCE_MANIFEST_ID = "attentional_v2_private_library_screen_v2"
LOCAL_REFS_MANIFEST_ID = "attentional_v2_private_library_v2_local_refs"
CORPUS_MANIFEST_ID = "attentional_v2_private_library_bilingual_v2"
SPLITS_MANIFEST_ID = "attentional_v2_private_library_bilingual_v2_splits"

PRIMARY_ROLE_ORDER = ("expository", "argumentative", "narrative_reflective", "reference_heavy")
EXCERPT_FRACTIONS = (0.24, 0.72)
MAX_CHAPTERS_PER_SOURCE = 4
MIN_RUNTIME_SENTENCE_COUNT = 18


def _spec(
    *,
    source_id: str,
    title: str,
    author: str,
    language: str,
    source_path: Path,
    promoted_local_path: str,
    origin: str,
    acquisition_batch_id: str,
    type_tags: list[str],
    role_tags: list[str],
    selection_priority: int,
    notes: list[str],
) -> dict[str, Any]:
    return {
        "spec": CandidateSpec(
            source_id=source_id,
            title=title,
            author=author,
            language=language,
            origin=origin,
            storage_mode="local-only",
            promoted_local_path=promoted_local_path,
            acquisition={"kind": "manual_local_file"},
            type_tags=type_tags,
            role_tags=role_tags,
            selection_priority=selection_priority,
            notes=notes,
        ),
        "source_path": source_path,
        "acquisition_batch_id": acquisition_batch_id,
        "origin_filename": source_path.name,
    }


def _private_specs() -> list[dict[str, Any]]:
    return [
        _spec(
            source_id="antifragile_private_en",
            title="Antifragile",
            author="Nassim Nicholas Taleb",
            language="en",
            source_path=DOWNLOAD_ROOT / "Antifragile (Nassim Nicholas Taleb) (Z-Library).epub",
            promoted_local_path="en/private/antifragile.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "psychology_decision", "modern_nonfiction"],
            role_tags=["argumentative", "reference_heavy"],
            selection_priority=20,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for distinction, fragility, and anti-intuitive argumentative pressure.",
            ],
        ),
        _spec(
            source_id="fooled_by_randomness_private_en",
            title="Fooled by Randomness",
            author="Nassim Nicholas Taleb",
            language="en",
            source_path=DOWNLOAD_ROOT / "Fooled by Randomness The Hidden Role of Chance in Life and in the Markets (Nassim Nicholas Taleb) (Z-Library).epub",
            promoted_local_path="en/private/fooled_by_randomness.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["psychology_decision", "management_economics", "modern_nonfiction"],
            role_tags=["argumentative", "reference_heavy"],
            selection_priority=6,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for luck-versus-skill, risk, and conceptual-boundary evaluation.",
            ],
        ),
        _spec(
            source_id="skin_in_the_game_private_en",
            title="Skin in the Game",
            author="Nassim Nicholas Taleb",
            language="en",
            source_path=DOWNLOAD_ROOT / "Skin In The Game Hidden Asymmetries In Daily Life (Nassim Nicholas Taleb) (Z-Library).epub",
            promoted_local_path="en/private/skin_in_the_game.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "business", "modern_nonfiction"],
            role_tags=["argumentative", "reference_heavy"],
            selection_priority=21,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for asymmetry, accountability, and ethical-pressure argument turns.",
            ],
        ),
        _spec(
            source_id="black_swan_private_en",
            title="The Black Swan",
            author="Nassim Nicholas Taleb",
            language="en",
            source_path=DOWNLOAD_ROOT / "The Black Swan Second Edition The Impact of the Highly Improbable With a New Section On Robustness and Fragility (Nassim Nicholas Taleb) (Z-Library).epub",
            promoted_local_path="en/private/the_black_swan.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["psychology_decision", "management_economics", "modern_nonfiction"],
            role_tags=["argumentative", "reference_heavy"],
            selection_priority=22,
            notes=[
                "Previously screened but not promoted; now included so the combined supplement covers the full reachable private library.",
                "Useful for high-variance causality, anti-explanation pressure, and long-range argument structure.",
            ],
        ),
        _spec(
            source_id="value_of_others_private_en",
            title="The Value of Others",
            author="Orion Taraban",
            language="en",
            source_path=DOWNLOAD_ROOT / "_OceanofPDF.com_The_Value_of_Others_-_Orion_Taraban.epub",
            promoted_local_path="en/private/the_value_of_others.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["psychology_decision", "social_thought", "modern_nonfiction"],
            role_tags=["argumentative", "expository"],
            selection_priority=24,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for modern philosophical prose with compressed distinctions and reaction-worthy lines.",
            ],
        ),
        _spec(
            source_id="making_of_a_manager_private_en",
            title="The Making of a Manager",
            author="Julie Zhuo",
            language="en",
            source_path=DOWNLOAD_ROOT / "The Making of a Manager What to Do When Everyone Looks to You (Julie Zhuo) (Z-Library).epub",
            promoted_local_path="en/private/the_making_of_a_manager.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "business", "modern_nonfiction"],
            role_tags=["narrative_reflective", "expository"],
            selection_priority=11,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for reflective management prose and contemporary workplace examples.",
            ],
        ),
        _spec(
            source_id="inspired_private_en",
            title="INSPIRED",
            author="Marty Cagan",
            language="en",
            source_path=DOWNLOAD_ROOT / "INSPIRED How to Create Tech Products Customers Love (Marty Cagan, Christian Idiodi, Lea Hickman etc.) (Z-Library).epub",
            promoted_local_path="en/private/inspired.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "business", "science_technology", "modern_nonfiction"],
            role_tags=["expository", "reference_heavy"],
            selection_priority=18,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for product-thinking distinctions and practical framework-heavy prose.",
            ],
        ),
        _spec(
            source_id="chance_private_en",
            title="Chance",
            author="Joseph Conrad",
            language="en",
            source_path=DOWNLOAD_ROOT / "joseph-conrad_chance.epub",
            promoted_local_path="en/private/chance.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["literature", "novel"],
            role_tags=["narrative_reflective"],
            selection_priority=29,
            notes=[
                "Legacy literary control title retained so the combined private library does not become pure nonfiction.",
            ],
        ),
        _spec(
            source_id="biji_de_fangfa_private_zh",
            title="笔记的方法",
            author="刘少楠, 刘白光",
            language="zh",
            source_path=DOWNLOAD_ROOT / "笔记的方法 (刘少楠, 刘白光) (Z-Library).epub",
            promoted_local_path="zh/private/bijidefangfa.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "method", "modern_nonfiction"],
            role_tags=["expository"],
            selection_priority=15,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for modern Chinese expository prose and method-oriented distinctions.",
            ],
        ),
        _spec(
            source_id="fooled_by_randomness_private_zh",
            title="随机漫步的傻瓜",
            author="纳西姆·尼古拉斯·塔勒布",
            language="zh",
            source_path=DOWNLOAD_ROOT / "随机漫步的傻瓜：发现市场和人生中的隐藏机遇 = Fooled by Randomness The Hidden Role of Chance in Life and in the Markets ( etc.) (Z-Library).epub",
            promoted_local_path="zh/private/suijimanbudesagua.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["psychology_decision", "management_economics", "modern_nonfiction"],
            role_tags=["argumentative", "reference_heavy"],
            selection_priority=5,
            notes=[
                "Legacy private source retained in the combined private-library supplement.",
                "Useful for Chinese argumentative prose on luck, uncertainty, and mistaken causality.",
            ],
        ),
        _spec(
            source_id="cracking_pm_career_private_en",
            title="Cracking the PM Career",
            author="Jackie Bavaro, Gayle McDowell",
            language="en",
            source_path=DOWNLOAD_ROOT / "Cracking the PM Career The Skills, Frameworks, and Practices To Become a Great Product Manager (Cracking the Interview … (Jackie Bavaro, Gayle McDowell) (Z-Library).epub",
            promoted_local_path="en/private/cracking_pm_career.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "business", "modern_nonfiction"],
            role_tags=["expository", "reference_heavy"],
            selection_priority=25,
            notes=[
                "Previously reserved; now included so all reachable private books are part of the combined supplement.",
                "Useful for framework-heavy management/career prose.",
            ],
        ),
        _spec(
            source_id="cracking_pm_interview_private_en",
            title="Cracking the PM Interview",
            author="Gayle Laakmann McDowell",
            language="en",
            source_path=DOWNLOAD_ROOT / "Cracking the PM Interview - How to Land a Product Manager Job in Technology (Gayle Laakmann McDowell) (Z-Library).epub",
            promoted_local_path="en/private/cracking_pm_interview.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "business", "modern_nonfiction"],
            role_tags=["expository", "reference_heavy"],
            selection_priority=27,
            notes=[
                "Previously rejected for the first tiny seed slice; now retained in the combined supplement inventory.",
                "Useful mainly as framework-heavy local supplement material rather than top-tier benchmark promotion material.",
            ],
        ),
        _spec(
            source_id="decode_and_conquer_private_en",
            title="Decode and Conquer",
            author="Lewis C. Lin",
            language="en",
            source_path=DOWNLOAD_ROOT / "Decode and Conquer Answers to Product Management Interviews (Lewis C. Lin) (Z-Library).epub",
            promoted_local_path="en/private/decode_and_conquer.epub",
            origin="manual-local-download",
            acquisition_batch_id="legacy_private_downloads_v1",
            type_tags=["management_economics", "business", "modern_nonfiction"],
            role_tags=["expository", "reference_heavy"],
            selection_priority=28,
            notes=[
                "Previously reserved; now included so all reachable private books are part of the combined supplement.",
                "Useful for structured answer frameworks and distinction-heavy expository prose.",
            ],
        ),
        _spec(
            source_id="elon_musk_private_en",
            title="Elon Musk",
            author="Walter Isaacson",
            language="en",
            source_path=BOOK_ROOT / "Elon Musk (Walter Isaacson) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/elon_musk.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["biography", "business", "science_technology", "modern_nonfiction"],
            role_tags=["narrative_reflective", "reference_heavy"],
            selection_priority=2,
            notes=[
                "New /BOOK batch title with strong multi-project biography pressure and institution-level causality.",
            ],
        ),
        _spec(
            source_id="evicted_private_en",
            title="Evicted",
            author="Matthew Desmond",
            language="en",
            source_path=BOOK_ROOT / "Evicted (Matthew Desmond) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/evicted.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["social_reportage", "history", "modern_nonfiction"],
            role_tags=["narrative_reflective", "expository"],
            selection_priority=13,
            notes=[
                "New /BOOK batch title covering fact-rich social reportage and institution-individual causality.",
            ],
        ),
        _spec(
            source_id="good_strategy_bad_strategy_private_en",
            title="Good Strategy/Bad Strategy",
            author="Richard Rumelt",
            language="en",
            source_path=BOOK_ROOT / "Good StrategyBad Strategy (Rumelt, Richard) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/good_strategy_bad_strategy.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["management_economics", "business", "modern_nonfiction"],
            role_tags=["argumentative", "expository"],
            selection_priority=3,
            notes=[
                "New /BOOK batch title covering diagnosis, guiding policy, and action coherence.",
            ],
        ),
        _spec(
            source_id="poor_charlies_almanack_private_en",
            title="Poor Charlie's Almanack",
            author="Charles T. Munger",
            language="en",
            source_path=BOOK_ROOT / "Poor Charlie’s Almanack The Wit and Wisdom of Charles T. Munger (Charles T. Munger) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/poor_charlies_almanack.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["business", "management_economics", "modern_nonfiction"],
            role_tags=["reference_heavy", "argumentative"],
            selection_priority=1,
            notes=[
                "New /BOOK batch title with strong principle extraction and example-to-principle mapping pressure.",
            ],
        ),
        _spec(
            source_id="principles_private_en",
            title="Principles",
            author="Ray Dalio",
            language="en",
            source_path=BOOK_ROOT / "Principles (Ray Dalio) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/principles.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["management_economics", "business", "modern_nonfiction"],
            role_tags=["expository", "reference_heavy"],
            selection_priority=7,
            notes=[
                "New /BOOK batch title with explicit rule systems, abstraction ladders, and principle/exception handling pressure.",
            ],
        ),
        _spec(
            source_id="shoe_dog_private_en",
            title="Shoe Dog",
            author="Phil Knight",
            language="en",
            source_path=BOOK_ROOT / "Shoe Dog (Phil Knight) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/shoe_dog.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["business", "biography", "modern_nonfiction"],
            role_tags=["narrative_reflective"],
            selection_priority=10,
            notes=[
                "New /BOOK batch title with entrepreneurial narrative nonfiction and long-horizon decision pressure.",
            ],
        ),
        _spec(
            source_id="snowball_private_en",
            title="Snowball",
            author="Gregory Bastianelli",
            language="en",
            source_path=BOOK_ROOT / "Snowball (Gregory Bastianelli) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/snowball.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["business", "biography", "modern_nonfiction"],
            role_tags=["narrative_reflective", "reference_heavy"],
            selection_priority=12,
            notes=[
                "New /BOOK batch title included as-supplied; category tags treat it as business/biographical nonfiction pending later finer review.",
            ],
        ),
        _spec(
            source_id="steve_jobs_private_en",
            title="Steve Jobs",
            author="Walter Isaacson",
            language="en",
            source_path=BOOK_ROOT / "Steve Jobs (Walter Isaacson) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/steve_jobs.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["biography", "business", "science_technology", "modern_nonfiction"],
            role_tags=["narrative_reflective", "reference_heavy"],
            selection_priority=4,
            notes=[
                "New /BOOK batch title with long-range character pattern and product/company causality.",
            ],
        ),
        _spec(
            source_id="supremacy_private_en",
            title="Supremacy",
            author="Parmy Olson",
            language="en",
            source_path=BOOK_ROOT / "Supremacy AI, ChatGPT, and the Race That Will Change the World (Parmy Olson) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/supremacy.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["business", "science_technology", "modern_nonfiction"],
            role_tags=["argumentative", "reference_heavy"],
            selection_priority=8,
            notes=[
                "New /BOOK batch title with modern AI-company rivalry, institutional incentives, and technology/business overlap.",
            ],
        ),
        _spec(
            source_id="naval_almanack_private_en",
            title="The Almanack of Naval Ravikant",
            author="Eric Jorgenson",
            language="en",
            source_path=BOOK_ROOT / "The Almanack of Naval Ravikant A Guide to Wealth and Happiness (Eric Jorgenson) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/the_almanack_of_naval_ravikant.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["business", "management_economics", "modern_nonfiction"],
            role_tags=["expository", "argumentative"],
            selection_priority=9,
            notes=[
                "New /BOOK batch title with aphoristic nonfiction and selective-anchor pressure.",
            ],
        ),
        _spec(
            source_id="book_of_elon_private_en",
            title="The Book of Elon",
            author="Eric Jorgenson",
            language="en",
            source_path=BOOK_ROOT / "The Book of Elon (Eric Jorgenson) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="en/private/the_book_of_elon.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["biography", "business", "modern_nonfiction"],
            role_tags=["expository", "narrative_reflective"],
            selection_priority=17,
            notes=[
                "New /BOOK batch title with entrepreneurial/personality framing that complements the larger Isaacson biography.",
            ],
        ),
        _spec(
            source_id="kangxi_hongpiao_private_zh",
            title="康熙的红票：全球化中的清朝",
            author="孙立天",
            language="zh",
            source_path=BOOK_ROOT / "康熙的红票：全球化中的清朝 (孙立天) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="zh/private/kangxidehongpiao.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["history", "modern_nonfiction"],
            role_tags=["argumentative", "reference_heavy"],
            selection_priority=14,
            notes=[
                "New /BOOK batch title with Chinese historical/institutional causality and diplomacy pressure.",
            ],
        ),
        _spec(
            source_id="zhangzhongmou_zizhuan_private_zh",
            title="张忠谋自传(1931-1964)",
            author="张忠谋",
            language="zh",
            source_path=BOOK_ROOT / "张忠谋自传 (1931-1964) = Autobiography of Morris C. M. Chang (张忠谋) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="zh/private/zhangzhongmou_zizhuan_1931_1964.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["biography", "business", "modern_nonfiction"],
            role_tags=["narrative_reflective"],
            selection_priority=16,
            notes=[
                "New /BOOK batch title with long-range career formation and business/technology biography pressure.",
            ],
        ),
        _spec(
            source_id="canglang_zhishui_private_zh",
            title="沧浪之水",
            author="阎真",
            language="zh",
            source_path=BOOK_ROOT / "沧浪之水 (阎真) (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="zh/private/canglangzhishui.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["literature", "novel"],
            role_tags=["narrative_reflective"],
            selection_priority=23,
            notes=[
                "New /BOOK batch literary control title for contemporary Chinese narrative pressure.",
            ],
        ),
        _spec(
            source_id="meiguoren_de_xingge_private_zh",
            title="美国人的性格",
            author="费孝通",
            language="zh",
            source_path=BOOK_ROOT / "美国人的性格【（费孝通先生经典作品） 中国社会学、人类学奠基人之一费孝通学术经典赢得《纽约时报》《时代周刊》赞誉探索美国人的性格特征... (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="zh/private/meiguorendexingge.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["social_reportage", "history", "modern_nonfiction"],
            role_tags=["argumentative", "expository"],
            selection_priority=19,
            notes=[
                "New /BOOK batch title with sociology/cultural interpretation pressure and cross-society comparison.",
            ],
        ),
        _spec(
            source_id="zouchu_weiyi_zhenliguan_private_zh",
            title="走出唯一真理观",
            author="陈嘉映",
            language="zh",
            source_path=BOOK_ROOT / "走出唯一真理观【豆瓣评分9.0！“中国最接近哲学家称呼的人”、《十三邀》嘉宾陈嘉映继《何为良好生活》后重磅新作！我们之所求，首先不是让... (z-library.sk, 1lib.sk, z-lib.sk).epub",
            promoted_local_path="zh/private/zouchu_weiyi_zhenliguan.epub",
            origin="user-book-directory",
            acquisition_batch_id="book_directory_20260326",
            type_tags=["psychology_decision", "philosophical", "modern_nonfiction"],
            role_tags=["argumentative", "expository"],
            selection_priority=26,
            notes=[
                "New /BOOK batch title with philosophical distinction pressure and modern Chinese argumentative prose.",
            ],
        ),
    ]


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
    items = _private_specs()

    source_records: list[dict[str, Any]] = []
    source_refs: list[dict[str, Any]] = []
    chapter_rows_by_language: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for item in items:
        spec: CandidateSpec = item["spec"]
        source_path = Path(item["source_path"])
        if not source_path.exists():
            raise FileNotFoundError(source_path)

        promoted_path = promote_candidate(source_path, spec.promoted_local_path)
        relative_local_path = str(promoted_path.relative_to(ROOT))
        record = screen_source_book(
            spec=spec,
            local_path=promoted_path,
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
            "description": "Tracked screening inventory for the combined private-library supplement built from the user's /BOOK directory plus earlier private Downloads books.",
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
            "description": "Local source-file and local-package references for the combined private-library attentional_v2 supplement.",
            "source_refs": source_refs,
            "local_dataset_packages": local_package_refs,
        },
    )

    write_json(
        corpora_manifest_path,
        {
            "manifest_id": CORPUS_MANIFEST_ID,
            "description": "Combined bilingual private-library source corpus for attentional_v2 evaluation supplementation.",
            "language_tracks": {
                "en": [record["source_id"] for record in source_records if record["language"] == "en"],
                "zh": [record["source_id"] for record in source_records if record["language"] == "zh"],
            },
        },
    )

    splits = {
        "all_private_library_sources": {
            "en": [record["source_id"] for record in source_records if record["language"] == "en"],
            "zh": [record["source_id"] for record in source_records if record["language"] == "zh"],
        },
        "legacy_private_downloads_v1": {
            "en": [record["source_id"] for record in source_records if record["acquisition_batch_id"] == "legacy_private_downloads_v1" and record["language"] == "en"],
            "zh": [record["source_id"] for record in source_records if record["acquisition_batch_id"] == "legacy_private_downloads_v1" and record["language"] == "zh"],
        },
        "book_directory_20260326": {
            "en": [record["source_id"] for record in source_records if record["acquisition_batch_id"] == "book_directory_20260326" and record["language"] == "en"],
            "zh": [record["source_id"] for record in source_records if record["acquisition_batch_id"] == "book_directory_20260326" and record["language"] == "zh"],
        },
        "chapter_corpus_eligible": {
            "en": [record["source_id"] for record in source_records if record["language"] == "en" and record["corpus_lane"] == "chapter_corpus_eligible"],
            "zh": [record["source_id"] for record in source_records if record["language"] == "zh" and record["corpus_lane"] == "chapter_corpus_eligible"],
        },
        "excerpt_only": {
            "en": [record["source_id"] for record in source_records if record["language"] == "en" and record["corpus_lane"] == "excerpt_only"],
            "zh": [record["source_id"] for record in source_records if record["language"] == "zh" and record["corpus_lane"] == "excerpt_only"],
        },
        "reject_this_pass": {
            "en": [record["source_id"] for record in source_records if record["language"] == "en" and record["corpus_lane"] == "reject"],
            "zh": [record["source_id"] for record in source_records if record["language"] == "zh" and record["corpus_lane"] == "reject"],
        },
    }
    write_json(
        splits_manifest_path,
        {
            "manifest_id": SPLITS_MANIFEST_ID,
            "description": "Split definitions for the combined private-library attentional_v2 supplement.",
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
