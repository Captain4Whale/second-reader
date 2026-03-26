"""Tests for attentional_v2 deterministic intake and candidate generation."""

from __future__ import annotations

from src.attentional_v2.intake import process_sentence_intake
from src.attentional_v2.retrieval import bounded_lookback_source_space, generate_candidate_set
from src.attentional_v2.schemas import build_empty_anchor_memory, build_empty_local_buffer, build_empty_working_pressure


def _sentence(sentence_id: str, index: int, text: str, *, text_role: str = "body", paragraph_index: int = 1) -> dict[str, object]:
    return {
        "sentence_id": sentence_id,
        "sentence_index": index,
        "paragraph_index": paragraph_index,
        "text": text,
        "text_role": text_role,
    }


def _book_document() -> dict[str, object]:
    return {
        "metadata": {
            "book": "Value in Motion",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": "demo.epub",
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "sentences": [
                    _sentence("c1-s1", 1, "People want things from other people."),
                    _sentence("c1-s2", 2, "Markets arise in relationships."),
                    _sentence("c1-s3", 3, "However, definitions matter when value shifts."),
                    _sentence("c1-s4", 4, "This creates friction."),
                ],
            }
        ],
    }


def test_process_sentence_intake_updates_local_buffer_and_emits_monitor_signal():
    """Cheap intake should update the rolling buffer and emit trigger output without an LLM step."""

    local_buffer = build_empty_local_buffer()
    working_pressure = build_empty_working_pressure()
    anchor_memory = build_empty_anchor_memory()

    next_buffer, trigger = process_sentence_intake(
        _sentence("c1-s3", 3, "Value should matter here."),
        local_buffer=local_buffer,
        working_pressure=working_pressure,
        anchor_memory=anchor_memory,
        cadence_limit=4,
    )

    assert next_buffer["current_sentence_id"] == "c1-s3"
    assert next_buffer["seen_sentence_ids"] == ["c1-s3"]
    assert next_buffer["open_meaning_unit_sentence_ids"] == ["c1-s3"]
    assert trigger["output"] == "monitor"
    assert {signal["signal_kind"] for signal in trigger["signals"]} == {"claim_pressure"}


def test_process_sentence_intake_raises_to_zoom_now_for_knowledge_risk_and_callbacks():
    """Explicit uncertainty plus anchor-memory callback pressure should escalate the trigger output."""

    local_buffer = build_empty_local_buffer()
    working_pressure = build_empty_working_pressure()
    anchor_memory = build_empty_anchor_memory()
    anchor_memory["motif_index"] = {"value": ["a-1"]}

    next_buffer, trigger = process_sentence_intake(
        _sentence("c1-s4", 4, "Why does value return here?", paragraph_index=2),
        local_buffer=local_buffer,
        working_pressure=working_pressure,
        anchor_memory=anchor_memory,
        cadence_limit=1,
    )

    assert next_buffer["current_sentence_id"] == "c1-s4"
    assert trigger["output"] == "zoom_now"
    assert trigger["gate_state"] == "must_evaluate"
    assert "a-1" in trigger["callback_anchor_ids"]
    assert {signal["signal_kind"] for signal in trigger["signals"]} >= {
        "callback_activation",
        "pressure_update_proxy",
    }


def test_generate_candidate_set_is_memory_first_then_bounded_lookback():
    """Candidate generation should separate anchor-memory candidates from source look-back candidates."""

    anchor_memory = build_empty_anchor_memory()
    anchor_memory["anchor_records"] = [
        {
            "anchor_id": "a-1",
            "sentence_start_id": "c1-s1",
            "sentence_end_id": "c1-s1",
            "quote": "People want things from other people.",
            "status": "active",
        },
        {
            "anchor_id": "a-2",
            "sentence_start_id": "c1-s2",
            "sentence_end_id": "c1-s2",
            "quote": "Markets arise in relationships.",
            "status": "active",
        },
    ]

    candidates = generate_candidate_set(
        _book_document(),  # type: ignore[arg-type]
        current_sentence_id="c1-s4",
        current_text="Value in relationships creates friction.",
        anchor_memory=anchor_memory,
        max_memory_candidates=2,
        max_lookback_candidates=2,
    )

    lookback = bounded_lookback_source_space(
        _book_document(),  # type: ignore[arg-type]
        current_sentence_id="c1-s4",
        max_candidates=2,
    )

    assert [candidate["anchor_id"] for candidate in candidates["memory_candidates"]] == ["a-2"]
    assert [candidate["sentence_id"] for candidate in candidates["lookback_candidates"]] == ["c1-s2", "c1-s3"]
    assert [sentence["sentence_id"] for sentence in lookback] == ["c1-s2", "c1-s3"]


def test_generate_candidate_set_can_surface_nonlocal_callback_candidates():
    """Explicit callback cues should allow deterministic retrieval beyond the bounded local window."""

    document = {
        "metadata": {
            "book": "Callback Demo",
            "author": "Tester",
            "book_language": "zh",
            "output_language": "zh",
            "source_file": "demo.epub",
        },
        "chapters": [
            {
                "id": 1,
                "title": "第一章",
                "sentences": [
                    _sentence("c1-s1", 1, "自從那日尋訪林之洋下落，始終沒有消息。"),
                    _sentence("c1-s2", 2, "宮門外忽然熱鬧起來。"),
                    _sentence("c1-s3", 3, "眾人都望著殿上。"),
                    _sentence("c1-s4", 4, "唐敖一時不語。"),
                    _sentence("c1-s5", 5, "國王正要進宮。"),
                    _sentence("c1-s6", 6, "唐敖自從那日同多九公尋訪林之洋下落，訪來訪去，絕無消息。"),
                ],
            }
        ],
    }

    candidates = generate_candidate_set(
        document,  # type: ignore[arg-type]
        current_sentence_id="c1-s6",
        current_text="唐敖自從那日同多九公尋訪林之洋下落，訪來訪去，絕無消息。",
        anchor_memory=build_empty_anchor_memory(),
        max_memory_candidates=0,
        max_lookback_candidates=2,
    )

    assert candidates["lookback_candidates"][0]["sentence_id"] == "c1-s1"
    assert candidates["lookback_candidates"][0]["candidate_kind"] == "source_callback"
