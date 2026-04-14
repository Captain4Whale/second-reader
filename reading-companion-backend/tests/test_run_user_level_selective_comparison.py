"""Tests for user-level selective note-recall matching."""

from __future__ import annotations

from pathlib import Path

from eval.attentional_v2 import run_user_level_selective_comparison as module


def _note_case(*, source_span_text: str, note_text: str = "note") -> module.NoteCase:
    return module.NoteCase(
        note_case_id="source_a__note_1",
        segment_id="source_a__segment_1",
        source_id="source_a",
        book_title="Book",
        author="Author",
        language_track="en",
        note_id="note_1",
        note_text=note_text,
        note_comment="",
        source_span_text=source_span_text,
        source_sentence_ids=["c1-s1"],
        chapter_id=1,
        chapter_title="Chapter 1",
        section_label="Section 1",
        raw_locator="1",
        provenance={},
    )


def _mechanism_payload(anchor_quote: str, *, content: str = "reaction") -> dict[str, object]:
    return {
        "status": "completed",
        "normalized_eval_bundle": {
            "reactions": [
                {
                    "reaction_id": "r1",
                    "type": "discern",
                    "section_ref": "1.1",
                    "anchor_quote": anchor_quote,
                    "content": content,
                }
            ]
        },
    }


def test_exact_match_counts_for_recall(tmp_path: Path) -> None:
    note_case = _note_case(source_span_text="Alpha hinge line.")
    result = module.evaluate_note_case_for_mechanism(
        note_case=note_case,
        mechanism_payload=_mechanism_payload("Alpha hinge line."),
        mechanism_key="attentional_v2",
        run_root=tmp_path,
        judge_mode="none",
    )

    assert result["label"] == "exact_match"
    assert result["counts_for_recall"] is True
    assert result["judgment"]["confidence"] == "high"


def test_non_exact_cover_does_not_auto_count_for_recall(tmp_path: Path) -> None:
    note_case = _note_case(source_span_text="Alpha hinge line.")
    result = module.evaluate_note_case_for_mechanism(
        note_case=note_case,
        mechanism_payload=_mechanism_payload("Alpha hinge line. Beta elaboration."),
        mechanism_key="attentional_v2",
        run_root=tmp_path,
        judge_mode="none",
    )

    assert result["label"] == "miss"
    assert result["counts_for_recall"] is False
    assert result["judgment"]["reason"] == "judge_disabled"


def test_focused_hit_counts_for_recall_when_judge_says_yes(tmp_path: Path, monkeypatch) -> None:
    note_case = _note_case(source_span_text="Alpha hinge line.")
    monkeypatch.setattr(
        module,
        "_judge_candidate_reaction",
        lambda **_kwargs: {
            "label": "focused_hit",
            "confidence": "high",
            "reason": "The reaction is clearly centered on the highlighted note.",
        },
    )

    result = module.evaluate_note_case_for_mechanism(
        note_case=note_case,
        mechanism_payload=_mechanism_payload("Alpha hinge line. Beta elaboration."),
        mechanism_key="attentional_v2",
        run_root=tmp_path,
        judge_mode="llm",
    )

    assert result["label"] == "focused_hit"
    assert result["counts_for_recall"] is True
    assert result["best_reaction"]["reaction_id"] == "r1"


def test_aggregate_results_counts_exact_and_focused_hits() -> None:
    aggregate = module._aggregate_results(
        note_case_payloads=[
            {
                "source_id": "source_a",
                "language_track": "en",
                "mechanism_results": {
                    "attentional_v2": {"label": "exact_match"},
                    "iterator_v1": {"label": "miss"},
                },
            },
            {
                "source_id": "source_a",
                "language_track": "en",
                "mechanism_results": {
                    "attentional_v2": {"label": "focused_hit"},
                    "iterator_v1": {"label": "incidental_cover"},
                },
            },
        ],
        mechanism_keys=("attentional_v2", "iterator_v1"),
    )

    assert aggregate["mechanisms"]["attentional_v2"]["note_recall"] == 1.0
    assert aggregate["mechanisms"]["attentional_v2"]["exact_match_count"] == 1
    assert aggregate["mechanisms"]["attentional_v2"]["focused_hit_count"] == 1
    assert aggregate["mechanisms"]["iterator_v1"]["note_recall"] == 0.0
    assert aggregate["mechanisms"]["iterator_v1"]["incidental_cover_count"] == 1
    assert aggregate["pairwise_delta"]["note_recall_delta"] == 1.0
