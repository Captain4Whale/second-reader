"""Tests for the current attentional_v2 LLM-call set."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from src.attentional_v2 import llm_calls as llm_calls_module
from src.attentional_v2 import runner as runner_module
from src.attentional_v2.llm_calls import (
    build_unitize_preview,
    ingest,
    digest,
)
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


def test_ingest_boundary_contract_has_only_boundary_fields() -> None:
    """Ingest should expose only current model fields plus internal recall status."""

    payload = llm_calls_module._normalize_ingest_boundary_result(  # noqa: SLF001
        {
            "end_anchor_text": "Beta.",
            "boundary_type": "paragraph_end",
            "reason": "Done.",
            "continuation" + "_pressure": True,
            "extra": "ignored",
        }
    )
    assert "decision" not in payload
    assert "selection" + "_mode" not in payload
    assert "continuation" + "_pressure" not in payload
    assert payload["end_anchor_text"] == "Beta."
    assert payload["memory_recalls"] == []
    assert payload["memory_recalls_status"] == "missing"


def test_ingest_recall_status_distinguishes_empty_from_malformed() -> None:
    provided_empty = llm_calls_module._normalize_ingest_boundary_result(  # noqa: SLF001
        {
            "end_anchor_text": "Beta.",
            "boundary_type": "paragraph_end",
            "reason": "Done.",
            "memory_recalls": [],
        }
    )
    malformed = llm_calls_module._normalize_ingest_boundary_result(  # noqa: SLF001
        {
            "end_anchor_text": "Beta.",
            "boundary_type": "paragraph_end",
            "reason": "Done.",
            "memory_recalls": {"recall_text": "not a list"},
        }
    )

    assert provided_empty["memory_recalls"] == []
    assert provided_empty["memory_recalls_status"] == "provided"
    assert malformed["memory_recalls"] == []
    assert malformed["memory_recalls_status"] == "malformed"


def _ingest_boundary_call(
    *,
    tmp_path: Path,
    preview_sentences: list[dict[str, object]],
) -> dict[str, object]:
    return ingest(
        current_view_position={
            "current_chapter_id": 2,
            "current_chapter_ref": "Chapter 2",
            "chapter_title": "Chapter 2",
            "current_cursor": {"paragraph_index": 1, "char_offset": 0},
            "retry": False,
        },
        current_view_content={
            "paragraph_slices": [
                {
                    "paragraph_index": sentence.get("paragraph_index"),
                    "text_role": sentence.get("text_role"),
                    "start_char": 0,
                    "end_char": len(str(sentence.get("text", "") or "")),
                    "text": sentence.get("text"),
                }
                for sentence in preview_sentences
            ],
        },
        output_dir=tmp_path,
        book_title="Demo Book",
        author="Tester",
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


def test_ingest_writes_manifest_and_uses_xml_anchor_contract(tmp_path: Path, monkeypatch):
    """Ingest should write a prompt manifest and keep the current forward anchor contract."""

    captured: dict[str, str] = {}

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        return {
            "end_anchor_text": "Beta.",
            "boundary_type": "cross_paragraph_continuation",
            "reason": "The line clearly keeps running.",
            "memory_recalls": [
                {
                    "recall_id": "r1",
                    "recall_text": "Beta continuation",
                    "basis": "selected_source_unit",
                }
            ],
            "continuation" + "_pressure": True,
        }

    monkeypatch.setattr(llm_calls_module, "invoke_json", fake_invoke_json)

    preview_sentences = [
        _sentence("c1-s1", "Alpha.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Beta.", sentence_index=2, paragraph_index=1),
    ]

    decision = ingest(
        current_view_position={
            "current_chapter_id": 1,
            "current_chapter_ref": "Chapter 1",
            "chapter_title": "Chapter 1",
            "current_cursor": {"paragraph_index": 1, "char_offset": 0},
            "retry": False,
        },
        current_view_content={
            "paragraph_slices": [
                {
                    "paragraph_index": sentence.get("paragraph_index"),
                    "text_role": sentence.get("text_role"),
                    "start_char": 0,
                    "end_char": len(str(sentence.get("text", "") or "")),
                    "text": sentence.get("text"),
                }
                for sentence in preview_sentences
            ],
        },
        output_dir=tmp_path,
        book_title="Demo Book",
        author="Tester",
    )

    manifest = json.loads((tmp_path / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "ingest.json").read_text(encoding="utf-8"))

    assert "decision" not in decision
    assert "selection" + "_mode" not in decision
    assert "continuation" + "_pressure" not in decision
    assert decision["end_anchor_text"] == "Beta."
    assert decision["memory_recalls"][0]["recall_text"] == "Beta continuation"
    assert captured["system_prompt"] == "Follow the structured Ingest prompt in the user message. Return JSON only."
    assert "<ReaderRole>" in captured["prompt"]
    assert "<Instruction>" in captured["prompt"]
    assert "<CurrentStep>" in captured["prompt"]
    assert "<ContextUseGuide>" in captured["prompt"]
    assert "<SelectNextUnit>" in captured["prompt"]
    assert "<RecallPriorReading>" in captured["prompt"]
    assert "<ExecutionLimits>" in captured["prompt"]
    assert "<BookInfo>" in captured["prompt"]
    assert "<BookIdentity>" in captured["prompt"]
    assert "<CurrentView>" in captured["prompt"]
    assert "<Position>" in captured["prompt"]
    assert '<Paragraph n="1" role="body" start_char="0" end_char="6">' in captured["prompt"]
    assert "<RetrievalSurface />" in captured["prompt"]
    assert "<OutputContract>" in captured["prompt"]
    assert "<OutputFields>" in captured["prompt"]
    assert "<ReturnFormat>" in captured["prompt"]
    assert "You are in the Ingest step of a sequential deep-reading loop." in captured["prompt"]
    assert "Select one forward source unit from the current reading cursor." in captured["prompt"]
    assert "notice whether this unit naturally calls back" in captured["prompt"]
    assert '"memory_recalls"' in captured["prompt"]
    assert '"memory_query"' not in captured["prompt"]
    assert "Do not resolve anchors, retry or choose fallback boundaries" in captured["prompt"]
    assert "Navigation context" not in captured["prompt"]
    assert "ReadingState" not in captured["prompt"]
    assert "LanguageContract" not in captured["prompt"]
    assert "FieldContracts" not in captured["prompt"]
    assert "selected_unit" not in captured["prompt"]
    assert "continuation" + "_pressure" not in captured["prompt"]
    assert "You are " + "Navi" + "gate" not in captured["prompt"]
    assert "Budget " + "state" not in captured["prompt"]
    assert "choose" + "_unit" not in captured["prompt"]
    assert "selection" + "_mode" not in captured["prompt"]
    assert "Return exactly one act" not in captured["prompt"]
    assert "weak structure cues, not automatic standalone units" in captured["prompt"]
    assert "purely non-lexical residue" in captured["prompt"]
    assert "Mainline preview" not in captured["prompt"]
    assert manifest["node_name"] == "ingest"
    assert manifest["prompt_version"] == "attentional_v2.ingest.v3"
    assert manifest["prompt_assembly"]["output_contract"] == "ingest_boundary_memory_recalls_json_v1"
    assert manifest["prompt_assembly"]["owner_node"] == "ingest"


def test_ingest_tool_loop_returns_recalls_and_runtime_status(tmp_path: Path, monkeypatch):
    captured: dict[str, object] = {}

    def fake_tool_loop(system_prompt, prompt, default, *, tools, tool_handler, max_tool_calls):
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        captured["tools"] = tools
        tool_result = tool_handler(
            "retrieve_unit_memory",
            {
                "end_anchor_text": "Beta.",
                "boundary_type": "paragraph_end",
                "memory_recalls": [
                    {"recall_id": "r1", "recall_text": "the earlier beta setup", "basis": "selected_source_unit"}
                ],
            },
            "tool-1",
        )
        captured["tool_result"] = tool_result
        return SimpleNamespace(
            payload={
                "end_anchor_text": "Beta.",
                "boundary_type": "paragraph_end",
                "reason": "Beta closes the local move.",
                "memory_recalls": [
                    {"recall_id": "r1", "recall_text": "the earlier beta setup", "basis": "selected_source_unit"}
                ],
            },
            status="tool_called",
            tool_results=[{"result": tool_result}],
        )

    monkeypatch.setattr(llm_calls_module, "invoke_json_with_tool_loop", fake_tool_loop)

    result = ingest(
        current_view_position={"current_chapter_id": 1, "current_cursor": {"paragraph_index": 1, "char_offset": 0}},
        current_view_content={"paragraph_slices": [{"paragraph_index": 1, "text": "Beta."}]},
        output_dir=tmp_path,
        unit_memory_tool_handler=lambda _args: {
            "status": "ok",
            "effective_mode": "text_only",
            "retrieval_summary": {"recall_count": 1, "candidate_unit_count": 2, "selected_unit_count": 1},
            "degradation_reason": "",
            "tool_call_id_seen": _args.get("_tool_call_id"),
        },
    )

    assert result["memory_recalls"][0]["recall_text"] == "the earlier beta setup"
    assert result["tool_loop_status"] == "tool_called"
    assert result["tool_result_summary"]["status"] == "ok"
    assert result["tool_result_summary"]["tool_call_id_seen"] == "tool-1"
    assert captured["tools"][0]["name"] == "retrieve_unit_memory"
    assert "memory_query" not in json.dumps(captured["tools"], ensure_ascii=False)


def test_ingest_marks_recalls_without_tool_as_contract_violation(tmp_path: Path, monkeypatch):
    calls = {"count": 0}

    def fake_tool_loop(*_args, **_kwargs):
        calls["count"] += 1
        return SimpleNamespace(
            payload={
                "end_anchor_text": "Beta.",
                "boundary_type": "paragraph_end",
                "reason": "Beta closes the local move.",
                "memory_recalls": [
                    {"recall_id": "r1", "recall_text": "the earlier beta setup", "basis": "selected_source_unit"}
                ],
            },
            status="final_without_tool",
            tool_results=[],
        )

    monkeypatch.setattr(llm_calls_module, "invoke_json_with_tool_loop", fake_tool_loop)

    result = ingest(
        current_view_position={"current_chapter_id": 1, "current_cursor": {"paragraph_index": 1, "char_offset": 0}},
        current_view_content={"paragraph_slices": [{"paragraph_index": 1, "text": "Beta."}]},
        output_dir=tmp_path,
        unit_memory_tool_handler=lambda _args: {"status": "ok"},
    )

    assert calls["count"] == 2
    assert result["tool_loop_status"] == "tool_call_contract_violation"


def test_ingest_can_trim_leading_boundary_residue(tmp_path: Path, monkeypatch):
    """Ingest preserves the selected end anchor for a short structural unit."""

    def fake_invoke_json(_system_prompt: str, _prompt: str, default: object) -> object:
        return {
            "end_anchor_text": "运用专长，发挥杠杆效应，最终你会得到自己应得的。",
            "boundary_type": "paragraph_end",
            "reason": "The divider is a structural cue, not content.",
        }

    monkeypatch.setattr(llm_calls_module, "invoke_json", fake_invoke_json)

    preview_sentences = [
        _sentence("c1-s1", "∨", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "运用专长，发挥杠杆效应，最终你会得到自己应得的。", sentence_index=2, paragraph_index=2),
    ]

    decision = _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert "decision" not in decision
    assert "selection" + "_mode" not in decision
    assert decision["end_anchor_text"] == "运用专长，发挥杠杆效应，最终你会得到自己应得的。"


def test_ingest_refuses_to_trim_leading_lexical_content(tmp_path: Path, monkeypatch):
    """Ingest no longer exposes a separate mutable start boundary."""

    def fake_invoke_json(_system_prompt: str, _prompt: str, default: object) -> object:
        return {
            "end_anchor_text": "Other people are typically a problem until they prove otherwise.",
            "boundary_type": "paragraph_end",
            "reason": "The visible sentence completes the local move.",
        }

    monkeypatch.setattr(llm_calls_module, "invoke_json", fake_invoke_json)

    preview_sentences = [
        _sentence("c1-s1", "People want things from other people.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Other people are typically a problem until they prove otherwise.", sentence_index=2, paragraph_index=1),
    ]

    decision = _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert decision["end_anchor_text"] == "Other people are typically a problem until they prove otherwise."
    assert "start_sentence_id" not in decision


def test_ingest_fallback_merges_heading_with_following_body(tmp_path: Path, monkeypatch):
    """LLM failure should fall back to an empty anchor and safe forward act shape."""

    monkeypatch.setattr(
        llm_calls_module,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            llm_calls_module.ReaderLLMError("temporary ingest failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "认识财富创造的原理", sentence_index=1, paragraph_index=1, text_role="section_heading"),
        _sentence("c1-s2", "能学会。", sentence_index=2, paragraph_index=2),
        _sentence("c1-s3", "而且值得学。", sentence_index=3, paragraph_index=2),
    ]

    decision = _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert "decision" not in decision
    assert "selection" + "_mode" not in decision
    assert decision["end_anchor_text"] == ""
    assert decision["reason"] == "ingest_llm_error"


def test_ingest_fallback_keeps_body_paragraph_behavior(tmp_path: Path, monkeypatch):
    """Ordinary body fallback keeps the same safe forward act shape."""

    monkeypatch.setattr(
        llm_calls_module,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            llm_calls_module.ReaderLLMError("temporary ingest failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "Alpha.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Beta.", sentence_index=2, paragraph_index=1),
        _sentence("c1-s3", "Gamma.", sentence_index=3, paragraph_index=2),
    ]

    decision = _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert decision["end_anchor_text"] == ""
    assert decision["boundary_type"] == "paragraph_end"
    assert decision["reason"] == "ingest_llm_error"


def test_ingest_fallback_allows_heading_only_when_no_body_follows(tmp_path: Path, monkeypatch):
    """Heading-only fallback keeps the same safe forward act shape."""

    monkeypatch.setattr(
        llm_calls_module,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            llm_calls_module.ReaderLLMError("temporary ingest failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "Chapter 2", sentence_index=1, paragraph_index=1, text_role="chapter_heading"),
    ]

    decision = _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert decision["end_anchor_text"] == ""
    assert decision["reason"] == "ingest_llm_error"


def test_digest_uses_live_xml_prompt_and_filters_surface_reactions(tmp_path: Path, monkeypatch):
    """Digest uses XML prompt assembly and keeps only source-anchored reader-facing reactions."""

    captured: dict[str, str] = {}

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        return {
            "response": "The line flips the frame.",
            "annotations": [
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
                    "source_quote": "Quote outside unit",
                    "content": "This one should be dropped.",
                }
            ],
            "understanding": {
                "kind": "claim_or_argument",
                "content": "The current unit flips the frame around Alpha hinge.",
            },
            "reading_impression": "legacy ignored",
            "surfaced_reactions": [
                {
                    "source_quote": "Beta consequence.",
                    "content": "Legacy surfaced reaction should be ignored.",
                }
            ],
            "recent_reading_memory": [
                {
                    "kind": "other",
                    "memory_text": "Legacy recent memory should be ignored.",
                }
            ],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_store": "active_attention",
                    "target_key": "legacy-ignored",
                    "payload": {"statement": "This legacy field is ignored by Digest."},
                }
            ],
        }

    monkeypatch.setattr(llm_calls_module, "invoke_json", fake_invoke_json)

    result = digest(
        current_unit_sentences=[
            _sentence("c1-s1", "Alpha hinge.", sentence_index=1, paragraph_index=1),
            _sentence("c1-s2", "Beta consequence.", sentence_index=2, paragraph_index=1),
        ],
        carry_forward_context={
            "packet_version": STATE_PACKET_VERSION,
            "refs": [
                {"ref_id": "source:src:c1:p1@0-p1@12", "kind": "source"},
            ],
            "recent_reading_memory": {
                "active_entries": [
                    {
                        "memory_text": "The previous unit established the author's witness boundary.",
                    }
                ],
            },
        },
        output_language="en",
        output_dir=tmp_path,
        book_title="Demo Book",
        author="Tester",
        chapter_title="Chapter 1",
    )

    manifest = json.loads((tmp_path / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "digest.json").read_text(encoding="utf-8"))

    assert captured["system_prompt"] == "Follow the structured Digest prompt in the user message. Return JSON only."
    assert "<ReaderRole>" in captured["prompt"]
    assert "<Instruction>" in captured["prompt"]
    assert "<BookInfo>" in captured["prompt"]
    assert "<ReadingMemory>" in captured["prompt"]
    assert "<ReadingState>" not in captured["prompt"]
    assert "<CurrentFocus>" in captured["prompt"]
    assert "<OutputContract>" in captured["prompt"]
    assert "The previous unit established the author's witness boundary." in captured["prompt"]
    assert "Alpha hinge." in captured["prompt"]
    assert "Structural frame:" not in captured["prompt"]
    assert "<Understanding>" in captured["prompt"]
    assert "Write one holistic Understanding for this unit." in captured["prompt"]
    assert "Do not split Understanding by sentence, paragraph, theme, future use, or separate memory point." in captured["prompt"]
    assert "Split into multiple entries" not in captured["prompt"]
    assert "<Response>" in captured["prompt"]
    assert "<Annotation>" in captured["prompt"]
    assert '"understanding": {' in captured["prompt"]
    assert '"response": "..."' in captured["prompt"]
    assert '"annotations": [' in captured["prompt"]
    assert '"reading_impression": "..."' not in captured["prompt"]
    assert '"surfaced_reactions": []' not in captured["prompt"]
    assert '"recent_reading_memory": []' not in captured["prompt"]
    assert '"memory_uptake_ops"' not in captured["prompt"]
    assert "memory_uptake_ops" not in captured["prompt"]
    assert "active_attention" not in captured["prompt"]
    assert "prompt_fragment_ref" not in captured["prompt"]
    assert "value_slot" not in captured["prompt"]
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
    assert len(result["memory_uptake_ops"]) == 1
    op = result["memory_uptake_ops"][0]
    assert op["target_store"] == "recent_reading_memory"
    assert op["payload"] == {
        "kind": "claim_or_argument",
        "memory_text": "The current unit flips the frame around Alpha hinge.",
    }
    assert op["target_key"] != "legacy-ignored"
    assert manifest["node_name"] == "digest"
    assert manifest["prompt_version"] == "attentional_v2.digest.v3"
    assert manifest["prompt_assembly"]["spec_id"] == "attentional_v2.digest.xml.v3"
    assert manifest["prompt_assembly"]["output_contract"] == "digest_understanding_response_annotation_json_v2"
    assert "mode" not in manifest["prompt_assembly"]
    assert manifest["prompt_assembly"]["rendered_blocks"] == [
        "ReaderRole",
        "Instruction",
        "BookInfo",
        "ReadingMemory",
        "CurrentFocus",
        "OutputContract",
    ]


def test_digest_ignores_legacy_understanding_list_payload(tmp_path: Path, monkeypatch):
    """Digest should no longer treat a legacy Understanding list as memory ops."""

    def fake_invoke_json(system_prompt: str, prompt: str, default: object) -> object:
        payload: dict[str, object] = {
            "response": "A compact response remains valid.",
            "annotations": [],
        }
        payload["understanding"] = [
            {
                "kind": "claim_or_argument",
                "content": "Legacy list item should not become current memory.",
            }
        ]
        return payload

    monkeypatch.setattr(llm_calls_module, "invoke_json", fake_invoke_json)

    result = digest(
        current_unit_sentences=[
            _sentence("c1-s1", "Alpha hinge.", sentence_index=1, paragraph_index=1),
        ],
        carry_forward_context={"packet_version": STATE_PACKET_VERSION, "refs": []},
        output_language="en",
        output_dir=tmp_path,
        book_title="Demo Book",
        author="Tester",
        chapter_title="Chapter 1",
    )

    assert result["reading_impression"] == "A compact response remains valid."
    assert result["memory_uptake_ops"] == []


def test_memory_uptake_source_ref_normalization_keeps_development_evidence_separate():
    """Runtime source normalization should keep opening and development evidence separate."""

    normalized_ops = runner_module._normalize_memory_uptake_ops_source_refs(
        [
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
                "target_store": "active_attention",
                "target_key": "attention-1",
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

    normalized_ops, admission_events = llm_calls_module._normalize_state_operations_with_admission(  # noqa: SLF001
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
