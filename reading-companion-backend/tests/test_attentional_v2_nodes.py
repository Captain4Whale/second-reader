"""Tests for the current attentional_v2 live node set."""

from __future__ import annotations

import json
from pathlib import Path

from src.attentional_v2 import nodes as nodes_module
from src.attentional_v2 import runner as runner_module
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


def test_navigate_act_space_remains_bounded() -> None:
    """Navigate should keep the accepted bounded act space."""

    assert nodes_module._NAVIGATE_ACT_DECISIONS == {"choose_unit", "request_skill", "defer_detour"}  # noqa: SLF001


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
    assert "After the impression and any surfaced reactions, maintain memory deliberately." in captured["system_prompt"]
    assert "First maintain Recent Reading Memory" in captured["system_prompt"]
    assert "source-grounded understanding, not essay-like analysis" in captured["system_prompt"]
    assert "Record what the source establishes, shows, says, names, contrasts, or changes" in captured[
        "system_prompt"
    ]
    assert "Compress meaning, not wording" in captured["system_prompt"]
    assert "do not make it artificially short" in captured["system_prompt"]
    assert "orient yourself with the prompt-visible reading context" in captured["system_prompt"]
    assert "Treat the provided context as what you already carry from the reading so far." in captured["system_prompt"]
    assert "current unit as part of the unfolding book" in captured["system_prompt"]
    assert "write the memory for the current unit itself" in captured["system_prompt"]
    assert "Do not turn the entry into a recap of the context." in captured["system_prompt"]
    assert "Do not force every entry to mention prior memory or framing." in captured["system_prompt"]
    assert "What should my future self remember from this unit" in captured["system_prompt"]
    assert "What can I say again about the prior context" in captured["system_prompt"]
    assert "Do not over-explain the hidden mechanism behind the passage." in captured["system_prompt"]
    assert "Avoid unsupported analytic upgrades" in captured["system_prompt"]
    assert "Be context-resolvable, not standalone exhaustive" in captured["system_prompt"]
    assert "Avoid bare pronouns or vague references" in (captured["system_prompt"] + captured["prompt"])
    assert "Recent Reading Memory append operations do not need an operation-level `reason`." in captured[
        "system_prompt"
    ]
    assert "\"target_store\": \"recent_reading_memory\"" in captured["prompt"]
    recent_memory_example = captured["prompt"].split('"target_store": "recent_reading_memory"', 1)[1].split(
        '"target_store": "active_attention"',
        1,
    )[0]
    assert '"reason"' not in recent_memory_example
    assert "stores ActiveTension" in captured["system_prompt"]
    assert "pause as a reader" in captured["system_prompt"]
    assert "Notice what still holds your attention after the unit is over." in captured["system_prompt"]
    assert "Do not require yourself to know whether it will matter later." in captured["system_prompt"]
    assert "current source unit, book or chapter framing shown in this prompt" in captured["system_prompt"]
    assert "existing memory state shown in the read context packet" in captured["system_prompt"]
    assert "Do not import outside knowledge about the book, author, or later chapters" in captured["system_prompt"]
    assert "readerly charge" in captured["system_prompt"]
    assert "tension_from" in captured["system_prompt"]
    assert "tension_focus" in captured["system_prompt"]
    assert "answer_boundary" not in captured["system_prompt"]
    assert "question_from" not in captured["system_prompt"]
    assert "working_interpretation" in captured["system_prompt"]
    assert "does not have to be phrased as a question" in captured["system_prompt"]
    assert "does not require you to predict whether it will shape later reading" in captured["system_prompt"]
    assert "answered_reason" in captured["system_prompt"]
    assert "closed_reason" in captured["system_prompt"]
    assert "short exact contiguous span copied from the current unit" in captured["system_prompt"]
    assert "If the basis is title/framing/prior memory" in captured["system_prompt"]
    assert "never invent source coordinates yourself" in captured["system_prompt"]
    assert "precondition, setup, clue, partial explanation, or reframing" in captured["system_prompt"]
    assert "a bomb is placed on the table" in captured["system_prompt"]
    assert "the author poses a problem or claim" in captured["system_prompt"]
    assert "a landscape or image is unusually vivid" in captured["system_prompt"]
    assert "a person or event feels distinctive" in captured["system_prompt"]
    assert "keep the basis honest in `tension_from`" in captured["system_prompt"]
    assert "Importance alone belongs" in captured["system_prompt"]
    assert "Do not create an ActiveTension when the current unit raises and fully digests it locally." in captured[
        "system_prompt"
    ]
    assert "\"op\": \"resolve\"" in captured["prompt"]
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
    assert "\"target_store\": \"concept_registry\"" in captured["prompt"]
    assert "\"target_store\": \"thread_trace\"" in captured["prompt"]
    assert "Do not target `concept_digest`, `thread_digest`, `active_focus_digest`" in captured["system_prompt"]
    assert manifest["prompt_version"] == "attentional_v2.read.v27"


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
                        "summary": "囚徒对集中营生活的精神反应被作者划分为收容、适应、释放与解放三个阶段。",
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
    assert "三个阶段" in result["memory_uptake_ops"][0]["payload"]["summary"]


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


def test_read_unit_resolves_active_tension_development_source_refs(tmp_path: Path, monkeypatch):
    """Read-output source normalization should keep opening and development evidence separate."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "The passage starts answering the open question.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "resolve",
                    "target_store": "active_attention",
                    "target_key": "bomb-question",
                    "reason": "The current unit gives enough answer to stop carrying the question.",
                    "payload": {
                        "working_interpretation": "Someone has noticed the bomb but has not disarmed it.",
                        "answered_reason": "The current unit explicitly answers who noticed the bomb.",
                        "development_source_quote": "Someone noticed the bomb.",
                    },
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "Someone noticed the bomb.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    normalized_ops = runner_module._normalize_memory_uptake_ops_source_refs(
        result["memory_uptake_ops"],
        source_unit={
            "source_text": "Someone noticed the bomb.",
            "source_span": {
                "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
                "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 24},
            },
            "paragraph_offsets": [{"paragraph_index": 1, "start": 0, "end": 24}],
        },
    )

    payload = normalized_ops[0]["payload"]
    assert payload["development_source_refs"][0]["quote"] == "Someone noticed the bomb."
    assert payload["development_source_refs"][0]["role"] == "development_support"
    assert payload["answered_reason"] == "The current unit explicitly answers who noticed the bomb."
    assert payload["answered_at_source_span_id"].startswith("src:c1:p1@")
    assert payload["answered_at_source_span"]["start_cursor"]["paragraph_index"] == 1
    assert payload["answered_at_unit_span_id"].startswith("src:c1:p1@")


def test_memory_uptake_source_ref_normalization_repairs_malformed_ref_lists():
    """Model-emitted SourceRef lists should not override source_quote resolution."""

    normalized_ops = runner_module._normalize_memory_uptake_ops_source_refs(
        [
            {
                "op": "update",
                "target_store": "concept_registry",
                "target_key": "concept-1",
                "payload": {
                    "summary": "The premise is now grounded.",
                    "source_quote": "The premise appears here.",
                    "source_refs": [
                        {
                            "source_span_id": "src:c99:p99@0-p99@9",
                            "source_span": {
                                "start_cursor": {
                                    "chapter_id": 99,
                                    "chapter_ref": "Wrong",
                                    "paragraph_index": 99,
                                    "char_offset": 0,
                                },
                                "end_cursor": {
                                    "chapter_id": 99,
                                    "chapter_ref": "Wrong",
                                    "paragraph_index": 99,
                                    "char_offset": 9,
                                },
                            },
                        }
                    ],
                    "development_source_quote": "The answer appears here.",
                    "development_source_refs": [
                        {
                            "source_span_id": "src:c99:p99@9-p99@18",
                            "source_span": {
                                "start_cursor": {
                                    "chapter_id": 99,
                                    "chapter_ref": "Wrong",
                                    "paragraph_index": 99,
                                    "char_offset": 9,
                                },
                                "end_cursor": {
                                    "chapter_id": 99,
                                    "chapter_ref": "Wrong",
                                    "paragraph_index": 99,
                                    "char_offset": 18,
                                },
                            },
                        }
                    ],
                },
            }
        ],
        source_unit={
            "source_text": "The premise appears here. The answer appears here.",
            "source_span": {
                "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
                "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 49},
            },
            "paragraph_offsets": [{"paragraph_index": 1, "start": 0, "end": 49}],
        },
    )

    payload = normalized_ops[0]["payload"]
    assert payload["source_refs"][0]["quote"] == "The premise appears here."
    assert payload["source_refs"][0]["source_span_id"].startswith("src:c1:p1@")
    assert payload["development_source_refs"][0]["quote"] == "The answer appears here."
    assert payload["development_source_refs"][0]["source_span_id"].startswith("src:c1:p1@")


def test_recent_reading_memory_normalization_uses_unit_level_provenance_only():
    """Recent Reading Memory should not carry model-emitted fine-grained source refs."""

    normalized_ops = runner_module._normalize_memory_uptake_ops_source_refs(
        [
            {
                "op": "append",
                "target_store": "recent_reading_memory",
                "target_key": "model-ignored",
                "payload": {
                    "kind": "event_or_situation",
                    "memory_text": "The current unit establishes the prisoners' initial adaptation pressure.",
                    "source_quote": "The current unit",
                    "source_refs": [{"source_span_id": "model:wrong"}],
                    "development_source_quote": "adaptation pressure",
                    "development_source_refs": [{"source_span_id": "model:wrong-development"}],
                },
            }
        ],
        source_unit={
            "source_text": "The current unit establishes the prisoners' initial adaptation pressure.",
            "source_span": {
                "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 45, "char_offset": 0},
                "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 45, "char_offset": 71},
            },
            "paragraph_offsets": [{"paragraph_index": 45, "start": 0, "end": 71}],
        },
    )

    payload = normalized_ops[0]["payload"]
    assert payload == {
        "kind": "event_or_situation",
        "memory_text": "The current unit establishes the prisoners' initial adaptation pressure.",
    }


def test_recent_reading_memory_operation_normalization_drops_op_reason():
    """Recent Reading Memory content should live in memory_text, not a generated op reason."""

    normalized_ops, admission_events = nodes_module._normalize_state_operations_with_admission(  # noqa: SLF001
        [
            {
                "op": "append",
                "target_store": "recent_reading_memory",
                "reason": "The model should not be asked to justify creating this memory.",
                "payload": {
                    "kind": "event_or_situation",
                    "memory_text": "The current unit establishes the prisoners' initial adaptation pressure.",
                },
            }
        ],
        enforce_read_store_policy=True,
    )

    assert len(normalized_ops) == 1
    assert normalized_ops[0]["target_store"] == "recent_reading_memory"
    assert "reason" not in normalized_ops[0]
    assert normalized_ops[0]["payload"] == {
        "kind": "event_or_situation",
        "memory_text": "The current unit establishes the prisoners' initial adaptation pressure.",
    }
    assert admission_events[0]["admission_status"] == "accepted"


def test_active_attention_create_without_quote_keeps_unit_coordinates_without_fake_source_refs():
    """Prompt-context-grounded active items may omit source_quote without inventing precise source refs."""

    normalized_ops = runner_module._normalize_memory_uptake_ops_source_refs(
        [
            {
                "op": "create",
                "target_store": "active_attention",
                "target_key": "framing-question",
                "payload": {
                    "tension_from": "The visible title and current unit together raise this charge.",
                    "tension_focus": "How the framing connects to this local adaptation.",
                    "working_interpretation": "",
                    "source_refs": [
                        {
                            "source_span_id": "src:c99:p99@0-p99@9",
                            "source_span": {
                                "start_cursor": {
                                    "chapter_id": 99,
                                    "chapter_ref": "Wrong",
                                    "paragraph_index": 99,
                                    "char_offset": 0,
                                },
                                "end_cursor": {
                                    "chapter_id": 99,
                                    "chapter_ref": "Wrong",
                                    "paragraph_index": 99,
                                    "char_offset": 9,
                                },
                            },
                        }
                    ],
                },
            }
        ],
        source_unit={
            "source_text": "The premise appears here. The answer appears here.",
            "source_span": {
                "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
                "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 49},
            },
            "paragraph_offsets": [{"paragraph_index": 1, "start": 0, "end": 49}],
        },
    )

    payload = normalized_ops[0]["payload"]
    assert "source_refs" not in payload
    assert payload["opened_at_source_span_id"].startswith("src:c1:p1@")
    assert payload["opened_at_unit_span_id"].startswith("src:c1:p1@")


def test_active_attention_lifecycle_coordinates_are_added_from_current_unit():
    """Active-attention create and close ops should carry source-native lifecycle coordinates."""

    normalized_ops = runner_module._normalize_memory_uptake_ops_source_refs(
        [
            {
                "op": "create",
                "target_store": "active_attention",
                "target_key": "live-question",
                "payload": {
                    "tension_from": "The premise appears here.",
                    "tension_focus": "How this premise develops.",
                    "working_interpretation": "",
                    "source_quote": "The premise appears here.",
                },
            },
            {
                "op": "close",
                "target_store": "active_attention",
                "target_key": "old-question",
                "reason": "The old question no longer shapes the next read.",
                "payload": {},
            },
        ],
        source_unit={
            "source_text": "The premise appears here. The answer appears here.",
            "source_span": {
                "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
                "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 49},
            },
            "paragraph_offsets": [{"paragraph_index": 1, "start": 0, "end": 49}],
        },
    )

    create_payload = normalized_ops[0]["payload"]
    close_payload = normalized_ops[1]["payload"]
    assert create_payload["opened_at_source_span_id"].startswith("src:c1:p1@")
    assert create_payload["opened_at_unit_span_id"].startswith("src:c1:p1@")
    assert create_payload["source_refs"][0]["quote"] == "The premise appears here."
    assert close_payload["closed_reason"] == "The old question no longer shapes the next read."
    assert close_payload["closed_at_source_span_id"].startswith("src:c1:p1@")
    assert close_payload["closed_at_unit_span_id"].startswith("src:c1:p1@")


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


def test_read_unit_drops_unsupported_target_store_with_admission_diagnostic(tmp_path: Path, monkeypatch):
    """Unsupported stores should not masquerade as accepted memory updates."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        return {
            "reading_impression": "A digest projection is mentioned but not a read-path target.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_store": "concept_digest",
                    "target_key": "digest-1",
                    "payload": {"summary": "This should not become a raw audit dump."},
                }
            ],
        }

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    result = read_unit(
        current_unit_sentences=[
            _sentence("c1-s1", "The passage tempts a digest write.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=tmp_path,
    )

    assert result["memory_uptake_ops"] == []

    admission_event = result["memory_uptake_admission_events"][0]
    assert admission_event["admission_status"] == "dropped_unsupported_target_store"
    assert admission_event["target_store_supported"] is False
    assert admission_event["operation_store_policy"] == "unsupported_target_store"
    assert admission_event["policy_warnings"] == ["unsupported_target_store"]
    assert admission_event["compatibility_warnings"] == ["unsupported_target_store"]
    assert admission_event["drop_reason"] == "unsupported_target_store"
    assert "payload" not in admission_event


def test_read_unit_drops_unsupported_operation_store_pair_with_admission_diagnostic(tmp_path: Path, monkeypatch):
    """Unsupported operation-store pairings should not reach state apply."""

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

    assert result["memory_uptake_ops"] == []

    admission_event = result["memory_uptake_admission_events"][0]
    assert admission_event["admission_status"] == "dropped_unsupported_operation_for_target_store"
    assert admission_event["target_store_supported"] is True
    assert admission_event["operation_store_policy"] == "unsupported_operation_for_target_store"
    assert admission_event["policy_warnings"] == ["unsupported_operation_for_target_store"]
    assert admission_event["compatibility_warnings"] == ["unsupported_operation_for_target_store"]
    assert admission_event["drop_reason"] == "unsupported_operation_for_target_store"


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
