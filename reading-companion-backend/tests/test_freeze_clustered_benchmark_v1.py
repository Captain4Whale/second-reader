from __future__ import annotations

from eval.attentional_v2.freeze_clustered_benchmark_v1 import (
    ChapterFreezeResult,
    build_freeze_manifest_payload,
    freeze_one_chapter,
    is_freeze_eligible,
    update_active_manifest,
)


def make_row(
    case_id: str,
    *,
    source_id: str = "steve_jobs_private_en",
    chapter_id: str = "17",
    target_profile_id: str = "tension_reversal",
    action: str = "keep",
    problem_types: list[str] | None = None,
    notes: str = "",
    construction_priority: float = 5.0,
    judgeability_score: float = 5.0,
    reserve_rank: int | None = None,
    source_order: int = 0,
) -> dict:
    row = {
        "case_id": case_id,
        "source_id": source_id,
        "chapter_id": chapter_id,
        "target_profile_id": target_profile_id,
        "construction_priority": construction_priority,
        "judgeability_score": judgeability_score,
        "_source_order": source_order,
        "review_latest": {
            "action": action,
            "problem_types": list(problem_types or []),
            "notes": notes,
        },
    }
    if reserve_rank is not None:
        row["reserve_rank"] = reserve_rank
    return row


def test_is_freeze_eligible_blocks_problem_types_and_requires_negligible_text_noise() -> None:
    assert is_freeze_eligible(make_row("ok"))
    assert not is_freeze_eligible(make_row("wrong_bucket", problem_types=["wrong_bucket"]))
    assert not is_freeze_eligible(make_row("not_keep", action="revise"))
    assert not is_freeze_eligible(make_row("text_noise_bad", problem_types=["text_noise"], notes="contains visible corruption"))
    assert is_freeze_eligible(
        make_row(
            "text_noise_ok",
            problem_types=["text_noise"],
            notes="Minor text noise is negligible and does not affect judgment.",
        )
    )


def test_freeze_one_chapter_promotes_best_reserves_when_primary_short() -> None:
    primary_rows = [
        make_row("p1", construction_priority=9.0, source_order=0),
        make_row("p2", construction_priority=8.0, source_order=1),
        make_row("blocked", construction_priority=99.0, problem_types=["weak_excerpt"], source_order=2),
    ]
    reserve_rows = [
        make_row("r2", reserve_rank=2, source_order=0),
        make_row("r1", reserve_rank=1, source_order=1),
    ]

    result = freeze_one_chapter(
        chapter_case_id="steve_jobs_private_en__17",
        primary_rows=primary_rows,
        reserve_rows=reserve_rows,
        primary_target=3,
        reserve_target=2,
    )

    assert result.primary_case_ids == ["p1", "p2", "r1"]
    assert [row["case_id"] for row in result.promoted_reserve_rows] == ["r1"]
    assert result.reserve_case_ids == ["r2"]
    assert result.saturated_shortfall == 0


def test_freeze_one_chapter_prefers_overflow_primaries_for_reserve_slots() -> None:
    primary_rows = [
        make_row("p1", construction_priority=10.0, source_order=0),
        make_row("p2", construction_priority=9.0, source_order=1),
        make_row("p3", construction_priority=8.0, source_order=2),
        make_row("p4", construction_priority=7.0, source_order=3),
    ]
    reserve_rows = [make_row("r1", reserve_rank=1, source_order=0)]

    result = freeze_one_chapter(
        chapter_case_id="steve_jobs_private_en__17",
        primary_rows=primary_rows,
        reserve_rows=reserve_rows,
        primary_target=3,
        reserve_target=2,
    )

    assert result.primary_case_ids == ["p1", "p2", "p3"]
    assert result.reserve_case_ids == ["p4", "r1"]


def test_build_freeze_manifest_payload_derives_insight_subset_from_primary_profiles() -> None:
    chapter_results = {
        "demo_source_en__1": ChapterFreezeResult(
            chapter_case_id="demo_source_en__1",
            primary_rows=[
                make_row("dist1", target_profile_id="distinction_definition"),
                make_row("anchor1", target_profile_id="anchored_reaction_selectivity"),
            ],
            promoted_reserve_rows=[],
            reserve_rows=[make_row("reserve1", target_profile_id="callback_bridge")],
            overflow_primary_rows=[],
            eligible_primary_count=2,
            eligible_reserve_count=1,
            saturated_shortfall=0,
        ),
        "demo_source_zh__2": ChapterFreezeResult(
            chapter_case_id="demo_source_zh__2",
            primary_rows=[
                make_row(
                    "tension1",
                    source_id="meiguoren_de_xingge_private_zh",
                    chapter_id="19",
                    target_profile_id="tension_reversal",
                ),
                make_row(
                    "callback1",
                    source_id="meiguoren_de_xingge_private_zh",
                    chapter_id="19",
                    target_profile_id="callback_bridge",
                ),
            ],
            promoted_reserve_rows=[],
            reserve_rows=[],
            overflow_primary_rows=[],
            eligible_primary_count=2,
            eligible_reserve_count=0,
            saturated_shortfall=0,
        ),
    }

    payload = build_freeze_manifest_payload(
        selected_chapter_case_ids=["demo_source_en__1", "demo_source_zh__2"],
        chapter_results=chapter_results,
        excerpt_primary_target_total=20,
        reserve_target_total=4,
    )

    assert payload["splits"]["chapter_core_frozen_draft"] == {
        "by_language": {
            "en": ["demo_source_en__1"],
            "zh": ["demo_source_zh__2"],
        },
        "all": ["demo_source_en__1", "demo_source_zh__2"],
    }
    assert payload["splits"]["excerpt_core_primary_frozen_draft"]["all"] == [
        "dist1",
        "anchor1",
        "tension1",
        "callback1",
    ]
    assert payload["splits"]["insight_and_clarification_subset_frozen_draft"]["all"] == [
        "dist1",
        "tension1",
        "callback1",
    ]
    assert payload["splits"]["insight_and_clarification_subset_frozen_draft"]["by_pressure"] == {
        "distinction_definition": ["dist1"],
        "tension_reversal": ["tension1"],
        "callback_bridge": ["callback1"],
    }


def test_update_active_manifest_merges_freeze_splits_without_dropping_existing_keys(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        """
{
  "manifest_id": "demo",
  "quota_status": {
    "chapter_core": {"target_total": 4, "ready_now": 0, "gap": 4}
  },
  "splits": {
    "legacy_split": {"all": ["old_case"]}
  }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    update_active_manifest(
        manifest_path,
        manifest_payload={
            "quota_status": {
                "chapter_core": {"target_total": 4, "ready_now": 4, "gap": 0},
            },
            "splits": {
                "chapter_core_frozen_draft": {
                    "by_language": {"en": ["a"], "zh": ["b"]},
                    "all": ["a", "b"],
                },
            },
        },
        freeze_summary_ref="state/dataset_build/demo_summary.json",
    )

    payload = manifest_path.read_text(encoding="utf-8")
    assert '"ready_now": 4' in payload
    assert '"legacy_split"' in payload
    assert '"chapter_core_frozen_draft"' in payload
    assert '"freeze_summary_ref": "state/dataset_build/demo_summary.json"' in payload
