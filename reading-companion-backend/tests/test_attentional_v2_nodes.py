"""Tests for the current attentional_v2 live node set."""

from __future__ import annotations

import json
from pathlib import Path

from src.attentional_v2 import nodes as nodes_module
from src.attentional_v2.nodes import (
    build_unitize_preview,
    navigate_detour_search,
    navigate_route,
    navigate_unitize,
    read_unit,
)
from src.attentional_v2.schemas import build_default_reader_policy
from src.attentional_v2.state_projection import STATE_PACKET_VERSION


def _sentence(
    sentence_id: str,
    text: str,
    *,
    sentence_index: int,
    paragraph_index: int,
    text_role: str = "body",
) -> dict[str, object]:
    return {
        "sentence_id": sentence_id,
        "sentence_index": sentence_index,
        "paragraph_index": paragraph_index,
        "text": text,
        "text_role": text_role,
    }


def _navigation_context() -> dict[str, object]:
    return {
        "packet_version": STATE_PACKET_VERSION,
        "session_continuity_capsule": {"recent_sentence_ids": ["c0-s9"]},
        "active_attention_digest": {"active_items": []},
        "chapter_reflective_frame": {"chapter_frames": []},
        "active_focus_digest": {"recent_moves": []},
        "concept_digest": [],
        "thread_digest": [],
        "anchor_bank_digest": {"active_anchors": []},
        "refs": [],
    }


def test_build_unitize_preview_stays_within_current_and_next_non_heading_paragraph():
    """Preview should start at the current sentence, finish the paragraph, then include one following body paragraph."""

    chapter_sentences = [
        _sentence("c1-s1", "Heading.", sentence_index=1, paragraph_index=1, text_role="section_heading"),
        _sentence("c1-s2", "Alpha.", sentence_index=2, paragraph_index=2),
        _sentence("c1-s3", "Beta.", sentence_index=3, paragraph_index=2),
        _sentence("c1-s4", "Gamma.", sentence_index=4, paragraph_index=3),
        _sentence("c1-s5", "Delta.", sentence_index=5, paragraph_index=4, text_role="section_heading"),
        _sentence("c1-s6", "Epsilon.", sentence_index=6, paragraph_index=5),
    ]

    preview, preview_range = build_unitize_preview(
        chapter_sentences=chapter_sentences,
        current_sentence_id="c1-s3",
    )

    assert [sentence["sentence_id"] for sentence in preview] == ["c1-s3", "c1-s4"]
    assert preview_range == {
        "start_sentence_id": "c1-s3",
        "end_sentence_id": "c1-s4",
    }


def test_navigate_unitize_writes_manifest_and_applies_sentence_cap(tmp_path: Path, monkeypatch):
    """Unitize should honor the prompt result, then clamp it to the emergency coverage ceiling."""

    captured: dict[str, str] = {}

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        return {
            "start_sentence_id": "c1-s1",
            "end_sentence_id": "c1-s2",
            "boundary_type": "cross_paragraph_continuation",
            "evidence_sentence_ids": ["c1-s1", "c1-s2"],
            "reason": "The line clearly keeps running.",
            "continuation_pressure": True,
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    reader_policy = build_default_reader_policy()
    reader_policy["unitize"]["max_coverage_unit_sentences"] = 1
    preview_sentences = [
        _sentence("c1-s1", "Alpha.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Beta.", sentence_index=2, paragraph_index=1),
    ]

    decision = navigate_unitize(
        current_sentence=preview_sentences[0],
        preview_sentences=preview_sentences,
        navigation_context=_navigation_context(),
        reader_policy=reader_policy,
        output_language="en",
        output_dir=tmp_path,
    )

    manifest = json.loads((tmp_path / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "navigate_unitize.json").read_text(encoding="utf-8"))

    assert decision["start_sentence_id"] == "c1-s1"
    assert decision["end_sentence_id"] == "c1-s1"
    assert decision["preview_range"]["end_sentence_id"] == "c1-s2"
    assert decision["continuation_pressure"] is True
    assert "\"packet_version\": \"attentional_v2.state_packet.v1\"" in captured["prompt"]
    assert "weak structure cues, not automatic permission to cut a standalone unit" in captured["system_prompt"]
    assert "purely non-lexical residue" in captured["system_prompt"]
    assert "Use them as structural cues, not content" in captured["system_prompt"]
    assert "Never trim symbols or unusual characters that belong to a substantive sentence" in captured["system_prompt"]
    assert "may move forward only to trim leading purely non-lexical boundary residue" in captured["prompt"]
    assert manifest["prompt_version"] == "attentional_v2.navigate_unitize.v4"


def test_navigate_unitize_can_trim_leading_boundary_residue(tmp_path: Path, monkeypatch):
    """Unitize may start after a pure separator when the LLM treats it as boundary residue."""

    def fake_invoke_json(_system_prompt: str, _prompt: str, default: object) -> object:
        return {
            "start_sentence_id": "c1-s2",
            "end_sentence_id": "c1-s2",
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": ["c1-s2"],
            "reason": "The divider is a structural cue, not content.",
            "continuation_pressure": False,
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    preview_sentences = [
        _sentence("c1-s1", "∨", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "运用专长，发挥杠杆效应，最终你会得到自己应得的。", sentence_index=2, paragraph_index=2),
    ]

    decision = navigate_unitize(
        current_sentence=preview_sentences[0],
        preview_sentences=preview_sentences,
        navigation_context=_navigation_context(),
        reader_policy=build_default_reader_policy(),
        output_language="zh",
        output_dir=tmp_path,
    )

    assert decision["preview_range"]["start_sentence_id"] == "c1-s1"
    assert decision["start_sentence_id"] == "c1-s2"
    assert decision["end_sentence_id"] == "c1-s2"
    assert decision["evidence_sentence_ids"] == ["c1-s2"]


def test_navigate_unitize_refuses_to_trim_leading_lexical_content(tmp_path: Path, monkeypatch):
    """A shifted start is accepted only when skipped leading sentences are pure residue."""

    def fake_invoke_json(_system_prompt: str, _prompt: str, default: object) -> object:
        return {
            "start_sentence_id": "c1-s2",
            "end_sentence_id": "c1-s2",
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": ["c1-s2"],
            "reason": "Badly tries to skip normal content.",
            "continuation_pressure": False,
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    preview_sentences = [
        _sentence("c1-s1", "People want things from other people.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Other people are typically a problem until they prove otherwise.", sentence_index=2, paragraph_index=1),
    ]

    decision = navigate_unitize(
        current_sentence=preview_sentences[0],
        preview_sentences=preview_sentences,
        navigation_context=_navigation_context(),
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    assert decision["start_sentence_id"] == "c1-s1"
    assert decision["end_sentence_id"] == "c1-s2"
    assert decision["evidence_sentence_ids"] == ["c1-s1", "c1-s2"]


def test_navigate_unitize_fallback_merges_heading_with_following_body(tmp_path: Path, monkeypatch):
    """Heading-only fallback should widen to heading plus the next body paragraph when available."""

    monkeypatch.setattr(
        nodes_module,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            nodes_module.ReaderLLMError("temporary navigation failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "认识财富创造的原理", sentence_index=1, paragraph_index=1, text_role="section_heading"),
        _sentence("c1-s2", "能学会。", sentence_index=2, paragraph_index=2),
        _sentence("c1-s3", "而且值得学。", sentence_index=3, paragraph_index=2),
    ]

    decision = navigate_unitize(
        current_sentence=preview_sentences[0],
        preview_sentences=preview_sentences,
        navigation_context=_navigation_context(),
        reader_policy=build_default_reader_policy(),
        output_language="zh",
        output_dir=tmp_path,
    )

    assert decision["start_sentence_id"] == "c1-s1"
    assert decision["end_sentence_id"] == "c1-s3"
    assert decision["evidence_sentence_ids"] == ["c1-s1", "c1-s2", "c1-s3"]
    assert decision["reason"] == "unitize_fallback_heading_with_body"


def test_navigate_unitize_fallback_keeps_body_paragraph_behavior(tmp_path: Path, monkeypatch):
    """Ordinary body fallback should still stop at the current paragraph end."""

    monkeypatch.setattr(
        nodes_module,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            nodes_module.ReaderLLMError("temporary navigation failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "Alpha.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Beta.", sentence_index=2, paragraph_index=1),
        _sentence("c1-s3", "Gamma.", sentence_index=3, paragraph_index=2),
    ]

    decision = navigate_unitize(
        current_sentence=preview_sentences[0],
        preview_sentences=preview_sentences,
        navigation_context=_navigation_context(),
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    assert decision["end_sentence_id"] == "c1-s2"
    assert decision["evidence_sentence_ids"] == ["c1-s1", "c1-s2"]
    assert decision["reason"] == "unitize_fallback_current_paragraph"


def test_navigate_unitize_fallback_allows_heading_only_when_no_body_follows(tmp_path: Path, monkeypatch):
    """Heading fallback may remain isolated when the preview does not contain a following body paragraph."""

    monkeypatch.setattr(
        nodes_module,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            nodes_module.ReaderLLMError("temporary navigation failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "Chapter 2", sentence_index=1, paragraph_index=1, text_role="chapter_heading"),
    ]

    decision = navigate_unitize(
        current_sentence=preview_sentences[0],
        preview_sentences=preview_sentences,
        navigation_context=_navigation_context(),
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    assert decision["end_sentence_id"] == "c1-s1"
    assert decision["evidence_sentence_ids"] == ["c1-s1"]
    assert decision["reason"] == "unitize_fallback_current_paragraph"


def test_navigate_detour_search_normalizes_invalid_land_into_defer(tmp_path: Path, monkeypatch):
    """Detour search should refuse to land outside the visible search space."""

    monkeypatch.setattr(
        nodes_module,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "decision": "land_region",
            "reason": "Try a sentence that was not offered.",
            "start_sentence_id": "missing-s1",
            "end_sentence_id": "missing-s2",
        },
    )

    result = navigate_detour_search(
        search_scope={
            "scope_kind": "chapter_cards",
            "reason": "search earlier setup",
            "cards": [
                {
                    "start_sentence_id": "c1-s1",
                    "end_sentence_id": "c1-s2",
                    "card_summary": "Opening setup",
                }
            ],
        },
        detour_need={"reason": "Need the setup again.", "target_hint": "opening setup", "status": "open"},
        navigation_context={"packet_version": STATE_PACKET_VERSION},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    assert result == {
        "decision": "defer_detour",
        "reason": "Try a sentence that was not offered.",
        "start_sentence_id": "",
        "end_sentence_id": "",
    }


def test_read_unit_filters_unanchored_surface_and_derives_pressure_from_legacy_move_hint(tmp_path: Path, monkeypatch):
    """Read should keep only reader-facing surfaced reactions and use the current naturalized contract."""

    captured: dict[str, str] = {}

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        return {
            "reading_impression": "The line flips the frame.",
            "move_hint": "reframe",
            "surfaced_reactions": [
                {
                    "anchor_quote": "Alpha hinge.",
                    "content": "That phrase suddenly snaps the claim into place.",
                    "prior_link": {
                        "ref_ids": ["anchor:a-1"],
                        "relation": "callback",
                        "note": "It answers the earlier thread.",
                    },
                },
                {
                    "anchor_quote": "Beta consequence.",
                    "content": "This pushes further than c1-s1135.",
                },
                {
                    "anchor_quote": "Beta consequence.",
                    "content": "This answers anchor:a-1 directly.",
                },
                {
                    "anchor_quote": "Quote outside unit",
                    "content": "This one should be dropped.",
                },
            ],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_store": "active_attention",
                    "target_key": "q-1",
                    "payload": {"statement": "The frame just shifted."},
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "Alpha hinge.", sentence_index=1, paragraph_index=1),
            _sentence("c1-s2", "Beta consequence.", sentence_index=2, paragraph_index=1),
        ],
        carry_forward_context={
            "packet_version": STATE_PACKET_VERSION,
            "refs": [
                {"ref_id": "anchor:a-1", "kind": "anchor"},
            ],
        },
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    manifest = json.loads((tmp_path / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "read_unit.json").read_text(encoding="utf-8"))

    assert result["reading_impression"] == "The line flips the frame."
    assert result["pressure_signals"] == {
        "continuation_pressure": False,
        "backward_pull": False,
        "frame_shift_pressure": True,
    }
    assert result["surfaced_reactions"] == [
        {
            "anchor_quote": "Alpha hinge.",
            "content": "That phrase suddenly snaps the claim into place.",
            "prior_link": {
                "ref_ids": ["anchor:a-1"],
                "relation": "callback",
                "note": "It answers the earlier thread.",
            },
            "outside_link": None,
            "search_intent": None,
        }
    ]
    assert result["memory_uptake_ops"][0]["target_store"] == "active_attention"
    assert "You are a careful reader moving through this book." in captured["system_prompt"]
    assert "not as a field-filling task" in captured["system_prompt"]
    assert "Let `reading_impression` be the brief natural impression" in captured["system_prompt"]
    assert "After the impression and any surfaced reactions, let memory settle naturally." in captured["system_prompt"]
    assert "A surfaced reaction is already persisted as a reaction record." in captured["system_prompt"]
    assert "Explicit source structures can be worth remembering" in captured["system_prompt"]
    assert "Keep proportion around thin structural units." in captured["system_prompt"]
    assert "Do not inflate a bare heading or structural cue" in captured["system_prompt"]
    assert "Choose each `anchor_quote` as the smallest self-sufficient span" in captured["system_prompt"]
    assert "If a sentence would lose its meaning when isolated" in captured["system_prompt"]
    assert "Do not let one sharper later sentence erase an earlier framing line" in captured["system_prompt"]
    assert "If the unit contains multiple independently valuable local triggers" in captured["system_prompt"]
    assert "do one last swallowed-line check" in captured["system_prompt"]
    assert "it is often better to surface both" in captured["system_prompt"]
    assert "A common version of this pattern is premise plus sharpening" in captured["system_prompt"]
    assert "People want things from other people." in captured["system_prompt"]
    assert "other people are typically a problem until they prove otherwise" in captured["system_prompt"]
    assert "do not default to quoting only the sharper later line" in captured["system_prompt"]
    assert "If one line already stands by itself, a single-sentence anchor is fine: `能学会。`" in captured["system_prompt"]
    assert "Compressing a whole paragraph into one reaction" in captured["system_prompt"]
    assert "Quoting only the later sharper line" in captured["system_prompt"]
    assert "premise-plus-sharpening pair" in captured["system_prompt"]
    assert "`prior_link.ref_ids` are internal system handles" in captured["system_prompt"]
    assert "Never copy any `ref_id`, sentence id, anchor id" in captured["system_prompt"]
    assert "This pushes beyond the earlier 'irrecoverable' framing." in captured["system_prompt"]
    assert "This answers anchor:a-1 directly." in captured["system_prompt"]
    assert "`unit_delta`" not in captured["system_prompt"]
    assert "`implicit_uptake_ops`" not in captured["system_prompt"]
    assert manifest["prompt_version"] == "attentional_v2.read.v13"


def test_read_unit_contract_preserves_source_given_stage_model_as_memory_uptake(tmp_path: Path, monkeypatch):
    """Source-given structural frameworks should be allowed to settle into memory without requiring a reaction."""

    captured: dict[str, str] = {}

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        return {
            "reading_impression": "作者把集中营生活的精神反应先搭成三阶段框架，并开始进入第一阶段。",
            "pressure_signals": {
                "continuation_pressure": True,
                "backward_pull": False,
                "frame_shift_pressure": False,
            },
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_store": "thread_trace",
                    "target_key": "camp-reaction-stages",
                    "reason": "The three-stage structure will organize later reading.",
                    "payload": {
                        "thread_key": "camp_reaction_stages",
                        "statement": "囚徒对集中营生活的精神反应被作者划分为收容、适应、释放与解放三个阶段。",
                        "support_anchor_ids": [],
                    },
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence(
                "c1-s1",
                "囚徒对集中营生活的精神反应可以被划分为三个阶段：收容阶段、适应阶段、释放与解放阶段。",
                sentence_index=1,
                paragraph_index=1,
            ),
            _sentence(
                "c1-s2",
                "第一阶段显露的症状是惊恐。",
                sentence_index=2,
                paragraph_index=1,
            ),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="zh",
        output_dir=tmp_path,
        book_title="活出生命的意义",
    )

    assert "stage models" in captured["system_prompt"]
    assert "even when they do not call for a visible reaction" in captured["system_prompt"]
    assert result["surfaced_reactions"] == []
    assert result["memory_uptake_ops"][0]["target_store"] == "thread_trace"
    assert "三个阶段" in result["memory_uptake_ops"][0]["payload"]["statement"]


def test_navigate_route_uses_pressure_signals_only():
    """Route decisions should be deterministic projections of the normalized read packet."""

    decision = navigate_route(
        read_result={
            "reading_impression": "This section wants to keep unfolding.",
            "pressure_signals": {
                "continuation_pressure": True,
                "backward_pull": False,
                "frame_shift_pressure": False,
            },
        }
    )

    assert decision == {
        "action": "continue",
        "reason": "This section wants to keep unfolding.",
        "close_current_unit": True,
        "target_anchor_id": "",
        "target_sentence_id": "",
    }
