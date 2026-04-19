from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "temporary"
    / "attentional_v2_f4a_oneoff_quality_audit.py"
)
SPEC = importlib.util.spec_from_file_location("attentional_v2_f4a_quality_audit", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def test_case_target_assignments_stay_balanced() -> None:
    counts = {target_id: 0 for target_id in module.DEFAULT_TARGET_IDS}
    for case_id, target_id in module.CASE_TARGET_ASSIGNMENTS.items():
        assert case_id in module.ALL_CASE_IDS
        counts[target_id] += 1
    assert counts == {
        module.DEFAULT_TARGET_IDS[0]: 3,
        module.DEFAULT_TARGET_IDS[1]: 3,
    }


def test_render_window_text_from_book_document_preserves_selected_chapter_order() -> None:
    book_document = {
        "chapters": [
            {
                "id": 2,
                "title": "Chapter Two",
                "paragraphs": [{"text": "Second chapter first paragraph."}],
            },
            {
                "id": 4,
                "title": "Chapter Four",
                "paragraphs": [{"text": "Fourth chapter only paragraph."}],
            },
        ]
    }

    text = module.render_window_text_from_book_document(book_document, chapter_ids=[2, 4])

    assert "Chapter Two" in text
    assert "Second chapter first paragraph." in text
    assert "Chapter Four" in text
    assert "Fourth chapter only paragraph." in text
    assert text.index("Chapter Two") < text.index("Chapter Four")


def test_load_case_summary_reports_artifact_flags_and_surfaced_semantic_counts(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs" / "demo" / "attentional_v2"
    read_audit_path = module.read_audit_file(output_dir)
    reaction_records_path = module.reaction_records_file(output_dir)
    local_continuity_path = module.local_continuity_file(output_dir)
    normalized_path = module.normalized_eval_bundle_file(output_dir)
    chapter_result_path = module.chapter_result_compatibility_file(output_dir, 1)

    read_audit_path.parent.mkdir(parents=True, exist_ok=True)
    read_audit_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "surfaced_reaction_count": 0,
                        "pressure_signals": {"continuation_pressure": False, "backward_pull": True, "frame_shift_pressure": False},
                        "detour_need": {"status": "open"},
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "surfaced_reaction_count": 2,
                        "pressure_signals": {"continuation_pressure": True, "backward_pull": False, "frame_shift_pressure": True},
                        "detour_need": {"status": "resolved"},
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    reaction_records_path.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "reaction_id": "rx:1",
                        "compat_family": "highlight",
                        "primary_anchor": {"quote": "Alpha"},
                        "thought": "First thought",
                        "prior_link": {"kind": "explicit"},
                        "outside_link": {},
                        "search_intent": {},
                    },
                    {
                        "reaction_id": "rx:2",
                        "compat_family": "discern",
                        "primary_anchor": {"quote": "Beta"},
                        "thought": "Second thought",
                        "prior_link": {},
                        "outside_link": {"kind": "outside"},
                        "search_intent": {"query": "what next"},
                    },
                ]
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    local_continuity_path.write_text(json.dumps({"detour_trace": [{"detour_id": "d1"}]}, ensure_ascii=False) + "\n", encoding="utf-8")
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.write_text(
        json.dumps(
            {
                "reactions": [{"reaction_id": "rx:1"}, {"reaction_id": "rx:2"}],
                "chapters": [{"chapter_id": 1, "chapter_ref": "Chapter 1", "status": "completed", "visible_reaction_count": 2}],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    chapter_result_path.parent.mkdir(parents=True, exist_ok=True)
    chapter_result_path.write_text(json.dumps({"chapter_id": 1}, ensure_ascii=False) + "\n", encoding="utf-8")

    case = module.AuditCase(
        case_id="demo_case",
        source_id="demo_source",
        book_title="Demo Book",
        language_track="en",
        source_path=str(tmp_path / "demo.txt"),
        chapter_number=1,
        max_units=8,
        goal="Demo goal",
        target_id=module.DEFAULT_TARGET_IDS[0],
        source_kind="segment_source",
        source_details={},
    )

    summary = module._load_case_summary(case=case, output_dir=output_dir)

    assert summary["visible_reaction_count"] == 2
    assert summary["silent_unit_count"] == 1
    assert summary["pressure_signal_counts"] == {
        "continuation_pressure": 1,
        "backward_pull": 1,
        "frame_shift_pressure": 1,
    }
    assert summary["detour_status_counts"] == {"open": 1, "resolved": 1, "abandoned": 0}
    assert summary["prior_link_count"] == 1
    assert summary["outside_link_count"] == 1
    assert summary["search_intent_count"] == 1
    assert summary["compat_projection_available"] is True
    assert summary["normalized_eval_available"] is True
