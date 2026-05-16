"""Tests for the current attentional_v2 live node set."""

from __future__ import annotations

import json
from pathlib import Path

from src.attentional_v2 import nodes as nodes_module
from src.attentional_v2.nodes import (
    build_unitize_preview,
    navigate_choose_next_unit_act,
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
        "active_focus_digest": {"recent_reactions": []},
        "concept_digest": [],
        "thread_digest": [],
        "source_ref_digest": [],
        "refs": [],
    }


def _navigate_act(
    *,
    tmp_path: Path,
    preview_sentences: list[dict[str, object]],
    output_language: str = "en",
    active_detour_need: dict[str, object] | None = None,
    skills_allowed: bool = False,
    allowed_sentence_ids: set[str] | None = None,
) -> dict[str, object]:
    return navigate_choose_next_unit_act(
        reading_position={
            "mode": "detour" if active_detour_need else "mainline",
            "current_sentence_id": preview_sentences[0]["sentence_id"] if preview_sentences else "",
        },
        mainline_preview={
            "current_sentence": preview_sentences[0] if preview_sentences else {},
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"] if preview_sentences else "",
                "end_sentence_id": preview_sentences[-1]["sentence_id"] if preview_sentences else "",
            },
            "preview_sentences": preview_sentences,
        },
        active_detour_need=active_detour_need,
        mainline_cursor={"chapter_id": 2, "sentence_id": "c2-s1"},
        navigation_context=_navigation_context(),
        source_evidence={},
        skill_catalog=[{"skill_name": "source_window_fetch"}] if skills_allowed else [],
        skill_results_so_far=[],
        budget_state={"skills_allowed": skills_allowed},
        reader_policy=build_default_reader_policy(),
        output_language=output_language,
        output_dir=tmp_path,
        available_sentences=preview_sentences,
        allowed_sentence_ids=allowed_sentence_ids or {str(sentence["sentence_id"]) for sentence in preview_sentences},
        default_selection_mode="detour" if active_detour_need else "mainline",
        skills_allowed=skills_allowed,
    )


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


def test_navigate_choose_next_unit_writes_manifest_and_applies_sentence_cap(tmp_path: Path, monkeypatch):
    """Navigate should honor the prompt result, then clamp it to the emergency coverage ceiling."""

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

    decision = navigate_choose_next_unit_act(
        reading_position={"mode": "mainline", "current_sentence_id": "c1-s1"},
        mainline_preview={
            "current_sentence": preview_sentences[0],
            "preview_range": {"start_sentence_id": "c1-s1", "end_sentence_id": "c1-s2"},
            "preview_sentences": preview_sentences,
        },
        active_detour_need=None,
        mainline_cursor={},
        navigation_context=_navigation_context(),
        source_evidence={},
        skill_catalog=[],
        skill_results_so_far=[],
        budget_state={"skills_allowed": False},
        reader_policy=reader_policy,
        output_language="en",
        output_dir=tmp_path,
        available_sentences=preview_sentences,
        allowed_sentence_ids={"c1-s1", "c1-s2"},
        default_selection_mode="mainline",
        skills_allowed=False,
    )

    manifest = json.loads((tmp_path / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "navigate_choose_next_unit.json").read_text(encoding="utf-8"))

    assert decision["decision"] == "choose_unit"
    assert decision["start_sentence_id"] == "c1-s1"
    assert decision["end_sentence_id"] == "c1-s1"
    assert decision["preview_range"]["end_sentence_id"] == "c1-s2"
    assert decision["continuation_pressure"] is True
    assert "\"packet_version\": \"attentional_v2.state_packet.v1\"" in captured["prompt"]
    assert "weak structure cues, not automatic permission to cut a standalone unit" in captured["system_prompt"]
    assert "purely non-lexical residue" in captured["system_prompt"]
    assert "Use them as structural cues, not content" in captured["system_prompt"]
    assert "Never trim symbols or unusual characters that belong to a substantive sentence" in captured["system_prompt"]
    assert "Mainline preview" in captured["prompt"]
    assert manifest["prompt_version"] == "attentional_v2.navigate_choose_next_unit.v1"


def test_navigate_choose_next_unit_can_trim_leading_boundary_residue(tmp_path: Path, monkeypatch):
    """Navigate may start after a pure separator when the LLM treats it as boundary residue."""

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

    decision = _navigate_act(tmp_path=tmp_path, preview_sentences=preview_sentences, output_language="zh")

    assert decision["preview_range"]["start_sentence_id"] == "c1-s1"
    assert decision["start_sentence_id"] == "c1-s2"
    assert decision["end_sentence_id"] == "c1-s2"
    assert decision["evidence_sentence_ids"] == ["c1-s2"]


def test_navigate_choose_next_unit_refuses_to_trim_leading_lexical_content(tmp_path: Path, monkeypatch):
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

    decision = _navigate_act(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert decision["start_sentence_id"] == "c1-s1"
    assert decision["end_sentence_id"] == "c1-s2"
    assert decision["evidence_sentence_ids"] == ["c1-s1", "c1-s2"]


def test_navigate_choose_next_unit_fallback_merges_heading_with_following_body(tmp_path: Path, monkeypatch):
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

    decision = _navigate_act(tmp_path=tmp_path, preview_sentences=preview_sentences, output_language="zh")

    assert decision["start_sentence_id"] == "c1-s1"
    assert decision["end_sentence_id"] == "c1-s3"
    assert decision["evidence_sentence_ids"] == ["c1-s1", "c1-s2", "c1-s3"]
    assert decision["reason"] == "unitize_fallback_heading_with_body"


def test_navigate_choose_next_unit_fallback_keeps_body_paragraph_behavior(tmp_path: Path, monkeypatch):
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

    decision = _navigate_act(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert decision["end_sentence_id"] == "c1-s2"
    assert decision["evidence_sentence_ids"] == ["c1-s1", "c1-s2"]
    assert decision["reason"] == "unitize_fallback_current_paragraph"


def test_navigate_choose_next_unit_fallback_allows_heading_only_when_no_body_follows(tmp_path: Path, monkeypatch):
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

    decision = _navigate_act(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert decision["end_sentence_id"] == "c1-s1"
    assert decision["evidence_sentence_ids"] == ["c1-s1"]
    assert decision["reason"] == "unitize_fallback_current_paragraph"


def test_navigate_choose_next_unit_detour_refuses_out_of_scope_unit(tmp_path: Path, monkeypatch):
    """Detour Navigate should refuse to choose outside current source evidence."""

    monkeypatch.setattr(
        nodes_module,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "decision": "choose_unit",
            "selection_mode": "detour",
            "reason": "Try a sentence that was not offered.",
            "start_sentence_id": "missing-s1",
            "end_sentence_id": "missing-s2",
        },
    )

    result = _navigate_act(
        tmp_path=tmp_path,
        preview_sentences=[
            _sentence("c1-s1", "Opening setup.", sentence_index=1, paragraph_index=1),
            _sentence("c1-s2", "More setup.", sentence_index=2, paragraph_index=1),
        ],
        active_detour_need={"reason": "Need the setup again.", "target_hint": "opening setup", "status": "open"},
        allowed_sentence_ids={"c1-s1", "c1-s2"},
        skills_allowed=True,
    )

    assert result == {
        "decision": "defer_detour",
        "selection_mode": "detour",
        "reason": "chosen_unit_outside_allowed_source_evidence",
    }
    manifest = json.loads(
        (
            tmp_path
            / "_mechanisms"
            / "attentional_v2"
            / "internal"
            / "prompt_manifests"
            / "navigate_choose_next_unit.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["prompt_version"] == "attentional_v2.navigate_choose_next_unit.v1"
    assert "choose the next readable unit" in manifest["system_prompt"]
    assert "Available skills in detour mode only" in manifest["system_prompt"]
    assert "source_window_fetch" in manifest["system_prompt"]
    assert "Skill results so far" in manifest["user_prompt"]


def test_navigate_choose_next_unit_detour_can_request_one_skill(tmp_path: Path, monkeypatch):
    """Detour Navigate may request one bounded book-local source skill."""

    monkeypatch.setattr(
        nodes_module,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "decision": "request_skill",
            "reason": "Need exact source text before landing.",
            "skill_request": {
                "skill_name": "source_window_fetch",
                "reason": "Fetch the candidate range.",
                "arguments": {
                    "start_sentence_id": "c1-s1",
                    "end_sentence_id": "c1-s2",
                },
            },
        },
    )

    result = _navigate_act(
        tmp_path=tmp_path,
        preview_sentences=[
            _sentence("c1-s1", "Opening setup.", sentence_index=1, paragraph_index=1),
            _sentence("c1-s2", "More setup.", sentence_index=2, paragraph_index=1),
        ],
        active_detour_need={"reason": "Need the setup again.", "target_hint": "opening setup", "status": "open"},
        skills_allowed=True,
    )

    assert result["decision"] == "request_skill"
    assert result["skill_request"]["skill_name"] == "source_window_fetch"
    assert result["skill_request"]["arguments"] == {
        "start_sentence_id": "c1-s1",
        "end_sentence_id": "c1-s2",
    }


def test_read_unit_filters_unanchored_surface_and_uses_naturalized_contract(tmp_path: Path, monkeypatch):
    """Read should keep only reader-facing surfaced reactions and use the current naturalized contract."""

    captured: dict[str, str] = {}

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        return {
            "reading_impression": "The line flips the frame.",
            "surfaced_reactions": [
                {
                    "source_quote": "Alpha hinge.",
                    "content": "That phrase suddenly snaps the claim into place.",
                    "prior_link": {
                        "ref_ids": ["source:src:c1:p1@0-p1@12"],
                        "relation": "callback",
                        "note": "It answers the earlier thread.",
                    },
                },
                {
                        "source_quote": "Beta consequence.",
                    "content": "This pushes further than c1-s1135.",
                },
                {
                        "source_quote": "Beta consequence.",
                    "content": "This answers source:src:c1:p1@0-p1@12 directly.",
                },
                {
                        "source_quote": "Quote outside unit",
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
                {"ref_id": "source:src:c1:p1@0-p1@12", "kind": "source"},
            ],
        },
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    manifest = json.loads((tmp_path / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "read_unit.json").read_text(encoding="utf-8"))

    assert result["reading_impression"] == "The line flips the frame."
    assert result["surfaced_reactions"] == [
        {
                "source_quote": "Alpha hinge.",
            "content": "That phrase suddenly snaps the claim into place.",
            "prior_link": {
                    "ref_ids": ["source:src:c1:p1@0-p1@12"],
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
    assert "Choose each `source_quote` as the smallest self-sufficient span" in captured["system_prompt"]
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
    assert "Never copy any `ref_id`, sentence id, source span id" in captured["system_prompt"]
    assert "This pushes beyond the earlier 'irrecoverable' framing." in captured["system_prompt"]
    assert "This answers source:src:c1:p1@0-p1@12 directly." in captured["system_prompt"]
    assert "`unit_delta`" not in captured["system_prompt"]
    assert "`implicit_uptake_ops`" not in captured["system_prompt"]
    assert "Do not decide or name the next route." in captured["system_prompt"]
    assert "`pressure_signals`" not in captured["system_prompt"]
    assert manifest["prompt_version"] == "attentional_v2.read.v15"


def test_read_unit_contract_preserves_source_given_stage_model_as_memory_uptake(tmp_path: Path, monkeypatch):
    """Source-given structural frameworks should be allowed to settle into memory without requiring a reaction."""

    captured: dict[str, str] = {}

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        return {
            "reading_impression": "作者把集中营生活的精神反应先搭成三阶段框架，并开始进入第一阶段。",
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
                        "source_quote": "三个阶段：收容阶段、适应阶段、释放与解放阶段",
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


def test_read_unit_marks_missing_target_store_as_compatibility_default(tmp_path: Path, monkeypatch):
    """Missing target_store remains tolerated while becoming visible in audit metadata."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "The line opens a live question.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_key": "hot-missing-store",
                    "payload": {"statement": "A live question should remain in attention."},
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "A live question appears.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    op = result["memory_uptake_ops"][0]
    assert op["target_store"] == "active_attention"
    assert op["target_store_emitted"] == ""
    assert op["effective_target_store"] == "active_attention"
    assert op["compatibility_warnings"] == ["missing_target_store_defaulted"]

    admission_event = result["memory_uptake_admission_events"][0]
    assert admission_event["admission_status"] == "accepted"
    assert admission_event["target_store_emitted"] == ""
    assert admission_event["effective_target_store"] == "active_attention"
    assert admission_event["compatibility_warnings"] == ["missing_target_store_defaulted"]
    assert admission_event["target_store_supported"] is True
    assert admission_event["operation_store_policy"] == "supported"
    assert admission_event["policy_warnings"] == []


def test_read_unit_admits_resolve_memory_operation(tmp_path: Path, monkeypatch):
    """Schema-valid resolve ops should not disappear at node normalization."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "The earlier question has been answered.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "resolve",
                    "target_store": "active_attention",
                    "target_key": "hot-question",
                    "payload": {"status": "resolved"},
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "The answer closes the earlier question.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    assert len(result["memory_uptake_ops"]) == 1
    op = result["memory_uptake_ops"][0]
    assert op["op"] == "resolve"
    assert op["operation_type"] == "resolve"
    assert op["target_store"] == "active_attention"

    assert result["memory_uptake_admission_events"] == [
        {
            "operation_index": 0,
            "admission_status": "accepted",
            "operation_type_emitted": "resolve",
            "operation_type_normalized": "resolve",
            "target_store_emitted": "active_attention",
            "effective_target_store": "active_attention",
            "target_key": "hot-question",
            "item_id": "hot-question",
            "compatibility_warnings": [],
            "drop_reason": "",
            "target_store_supported": True,
            "operation_store_policy": "supported",
            "policy_warnings": [],
        }
    ]


def test_read_unit_records_dropped_memory_uptake_admission_events(tmp_path: Path, monkeypatch):
    """Unknown and malformed raw ops stay dropped but become visible in audit metadata."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "Only one operation is admissible.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                "not an operation",
                {
                    "op": "invent",
                    "target_store": "concept_registry",
                    "target_key": "concept-unknown",
                    "payload": {"summary": "This raw payload should not be copied into admission metadata."},
                },
                {
                    "target_store": "thread_trace",
                    "target_key": "thread-missing-op",
                    "payload": {"summary": "Missing operation type."},
                },
                {
                    "op": "append",
                    "target_key": "hot-accepted",
                    "payload": {"statement": "This remains admissible."},
                },
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "A mixed set of memory ops appears.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    assert [op["target_key"] for op in result["memory_uptake_ops"]] == ["hot-accepted"]

    admission_events = result["memory_uptake_admission_events"]
    assert [event["admission_status"] for event in admission_events] == [
        "dropped_malformed_operation",
        "dropped_unknown_operation",
        "dropped_malformed_operation",
        "accepted",
    ]
    assert admission_events[0]["drop_reason"] == "operation_not_object"
    assert admission_events[1]["operation_type_emitted"] == "invent"
    assert admission_events[1]["operation_type_normalized"] == "invent"
    assert admission_events[1]["drop_reason"] == "unknown_operation_type"
    assert admission_events[2]["drop_reason"] == "missing_operation_type"
    assert admission_events[3]["effective_target_store"] == "active_attention"
    assert admission_events[3]["compatibility_warnings"] == ["missing_target_store_defaulted"]
    assert admission_events[3]["target_store_supported"] is True
    assert admission_events[3]["operation_store_policy"] == "supported"
    assert admission_events[3]["policy_warnings"] == []
    assert all("payload" not in event for event in admission_events)


def test_read_unit_records_unsupported_target_store_policy_warning(tmp_path: Path, monkeypatch):
    """Unsupported stores remain normalized while admission audit shows policy risk."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "A reflective frame is mentioned but not a read-path target.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_store": "reflective_frames",
                    "target_key": "frame-1",
                    "payload": {"summary": "This should not become a raw audit dump."},
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "The passage tempts a reflective frame.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    op = result["memory_uptake_ops"][0]
    assert op["target_store"] == "reflective_frames"
    assert op["compatibility_warnings"] == ["unsupported_target_store"]

    admission_event = result["memory_uptake_admission_events"][0]
    assert admission_event["admission_status"] == "accepted"
    assert admission_event["target_store_supported"] is False
    assert admission_event["operation_store_policy"] == "unsupported_target_store"
    assert admission_event["policy_warnings"] == ["unsupported_target_store"]
    assert admission_event["compatibility_warnings"] == ["unsupported_target_store"]
    assert "payload" not in admission_event


def test_read_unit_records_unsupported_operation_store_policy_warning(tmp_path: Path, monkeypatch):
    """Unsupported operation-store pairings remain normalized but visible."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "A concept is cooling, but that pairing is only audit-visible here.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "cool",
                    "target_store": "concept_registry",
                    "target_key": "concept-1",
                    "payload": {"summary": "Cooling is not a concept-store admission policy op."},
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "The concept cools in importance.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    op = result["memory_uptake_ops"][0]
    assert op["target_store"] == "concept_registry"
    assert op["compatibility_warnings"] == ["unsupported_operation_for_target_store"]

    admission_event = result["memory_uptake_admission_events"][0]
    assert admission_event["admission_status"] == "accepted"
    assert admission_event["target_store_supported"] is True
    assert admission_event["operation_store_policy"] == "unsupported_operation_for_target_store"
    assert admission_event["policy_warnings"] == ["unsupported_operation_for_target_store"]
    assert admission_event["compatibility_warnings"] == ["unsupported_operation_for_target_store"]


def test_read_unit_records_supported_store_policy_without_warning(tmp_path: Path, monkeypatch):
    """Supported operation-store pairings include policy metadata without warnings."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "A concept is updated with stable admission policy.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "update",
                    "target_store": "concept_registry",
                    "target_key": "concept-1",
                    "payload": {"summary": "The concept stays aligned."},
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "The concept becomes clearer.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    op = result["memory_uptake_ops"][0]
    assert op["compatibility_warnings"] == []

    admission_event = result["memory_uptake_admission_events"][0]
    assert admission_event["target_store_supported"] is True
    assert admission_event["operation_store_policy"] == "supported"
    assert admission_event["policy_warnings"] == []
