"""Tests for the current attentional_v2 LLM-call set."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.attentional_v2 import llm_calls as llm_calls_module
from src.attentional_v2 import runner as runner_module
from src.attentional_v2.llm_calls import (
    build_unitize_preview,
    ingest,
    digest,
)
from src.attentional_v2.llm_output_tools import validate_ingest_result, validate_ingest_unit_memory_tool_args
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


def _unit(end_paragraph_n: object = 1, end_at: str = "paragraph_end") -> dict[str, object]:
    return {"end_paragraph_n": end_paragraph_n, "end_at": end_at}


def _partition(
    title: str = "First local move",
    end_paragraph_n: object = 1,
    end_at: str = "paragraph_end",
    status: str = "complete",
) -> dict[str, object]:
    return {
        "title": title,
        "end_paragraph_n": end_paragraph_n,
        "end_at": end_at,
        "status": status,
    }


def test_ingest_boundary_contract_has_only_boundary_fields() -> None:
    """Ingest should expose only current model fields plus internal recall status."""

    payload = llm_calls_module._normalize_ingest_boundary_result(  # noqa: SLF001
        {
            "unit": _unit(2, "paragraph_end"),
            "preview_partition": [_partition("First move", 2, "paragraph_end")],
            "end_anchor_text": "Beta.",
            "boundary_type": "paragraph_end",
            "reason": "Done.",
            "continuation" + "_pressure": True,
            "extra": "ignored",
        }
    )
    assert "decision" not in payload
    assert "selection" + "_mode" not in payload
    assert "boundary_type" not in payload
    assert "continuation" + "_pressure" not in payload
    assert "end_anchor_text" not in payload
    assert payload["unit"] == {"end_paragraph_n": "2", "end_at": "paragraph_end"}
    assert payload["preview_partition"] == [
        {
            "title": "First move",
            "end_paragraph_n": "2",
            "end_at": "paragraph_end",
            "status": "complete",
        }
    ]
    assert payload["memory_recalls"] == []
    assert payload["memory_recalls_status"] == "not_requested"


def test_ingest_normalizer_rejects_empty_unit_boundary() -> None:
    """Normalizer hardening prevents malformed payloads from becoming fallback units."""

    with pytest.raises(llm_calls_module.ReaderLLMError) as exc_info:
        llm_calls_module._normalize_ingest_boundary_result(  # noqa: SLF001
            {
                "unit": {"end_paragraph_n": "", "end_at": ""},
                "preview_partition": [_partition()],
                "reason": "missing anchor",
                "memory_recalls": [],
            }
        )

    assert exc_info.value.problem_code == "llm_contract"


def test_ingest_normalizer_ignores_legacy_final_memory_recalls() -> None:
    provided_empty = llm_calls_module._normalize_ingest_boundary_result(  # noqa: SLF001
        {
            "unit": _unit(),
            "preview_partition": [_partition()],
            "reason": "Done.",
            "memory_recalls": [],
        }
    )
    malformed = llm_calls_module._normalize_ingest_boundary_result(  # noqa: SLF001
        {
            "unit": _unit(),
            "preview_partition": [_partition()],
            "reason": "Done.",
            "memory_recalls": {"recall_text": "not a list"},
        }
    )

    assert provided_empty["memory_recalls"] == []
    assert provided_empty["memory_recalls_status"] == "not_requested"
    assert malformed["memory_recalls"] == []
    assert malformed["memory_recalls_status"] == "not_requested"


def test_ingest_tool_arg_validator_requires_selected_source_unit_basis() -> None:
    errors = validate_ingest_unit_memory_tool_args(
        {
            "unit": _unit(),
            "memory_recalls": [
                {
                    "recall_id": "r1",
                    "recall_text": "earlier setup",
                    "basis": "selected_unit_paragraphs_1_2",
                }
            ],
        },
    )

    assert "memory_recalls[0].basis must be selected_source_unit" in errors


def test_ingest_tool_arg_validator_requires_recall_language_to_match_source() -> None:
    errors = validate_ingest_unit_memory_tool_args(
        {
            "unit": _unit(1, "他继续向前走。"),
            "memory_recalls": [
                {
                    "recall_id": "r1",
                    "recall_text": "Earlier reading about Siddhartha leaving the Brahmin household with Govinda.",
                    "basis": "selected_source_unit",
                }
            ],
        },
        current_source_texts=[
            "悉达多继续向前走，乔文达仍然跟随他。两个人离开婆罗门的家，走向沙门的修行生活。"
        ],
    )

    assert "memory_recalls[0].recall_text must use the current source text's primary language" in errors

    valid_errors = validate_ingest_unit_memory_tool_args(
        {
            "unit": _unit(1, "他继续向前走。"),
            "memory_recalls": [
                {
                    "recall_id": "r1",
                    "recall_text": "悉达多离开婆罗门家庭并带着乔文达走向沙门修行。",
                    "basis": "selected_source_unit",
                }
            ],
        },
        current_source_texts=[
            "悉达多继续向前走，乔文达仍然跟随他。两个人离开婆罗门的家，走向沙门的修行生活。"
        ],
    )

    assert valid_errors == []


def test_ingest_result_validator_rejects_contract_violating_tool_result() -> None:
    errors = validate_ingest_result(
        {
            "unit": _unit(1, "他继续向前走。"),
            "preview_partition": [_partition("继续前行", 1, "他继续向前走。")],
        },
        tool_results=[{"result": {"status": "contract_violation", "degradation_reason": "bad recall language"}}],
        current_source_texts=[
            "悉达多继续向前走，乔文达仍然跟随他。两个人离开婆罗门的家，走向沙门的修行生活。"
        ],
    )

    assert "bad recall language" in errors


def test_ingest_result_validator_ignores_legacy_final_recalls_after_tool_call() -> None:
    errors = validate_ingest_result(
        {
            "unit": _unit(1, "他继续向前走。"),
            "preview_partition": [_partition("继续前行", 1, "他继续向前走。")],
            "memory_recalls": [
                {
                    "recall_id": "legacy",
                    "recall_text": "Bad legacy final recall echo.",
                    "basis": "wrong",
                }
            ],
        },
        tool_results=[
            {
                "name": "retrieve_unit_memory",
                "args": {
                    "memory_recalls": [
                        {
                            "recall_id": "r1",
                            "recall_text": "悉达多此前与求道有关的理解。",
                            "basis": "selected_source_unit",
                        }
                    ]
                },
                "result": {"status": "ok"},
            }
        ],
        current_source_texts=["悉达多继续向前走。"],
    )

    assert errors == []


def test_ingest_result_validator_rejects_invisible_paragraph_boundary() -> None:
    errors = validate_ingest_result(
        {
            "unit": _unit(99, "paragraph_end"),
            "preview_partition": [_partition("Invisible", 99, "paragraph_end")],
        },
        tool_results=[],
        current_visible_paragraph_ns=["1", "2"],
    )

    assert "unit.end_paragraph_n must match a visible Paragraph n" in errors


def test_ingest_result_validator_requires_preview_partition() -> None:
    errors = validate_ingest_result(
        {
            "unit": _unit(),
        },
        tool_results=[],
    )

    assert "preview_partition must be a non-empty array" in errors

    empty_errors = validate_ingest_result(
        {
            "unit": _unit(),
            "preview_partition": [],
        },
        tool_results=[],
    )

    assert "preview_partition must be a non-empty array" in empty_errors


def test_ingest_result_validator_rejects_invalid_preview_partition_fields() -> None:
    errors = validate_ingest_result(
        {
            "unit": _unit(1, "paragraph_end"),
            "preview_partition": [
                _partition("", 1, "paragraph_end"),
                _partition("Second move", 2, "paragraph_end", "open_tail"),
                _partition("Third move", 3, "", "bogus"),
            ],
        },
        tool_results=[],
        current_visible_paragraph_ns=["1", "2"],
    )

    assert "preview_partition[0].title must be non-empty" in errors
    assert "preview_partition open_tail is allowed only on the final partition" in errors
    assert "preview_partition[2].end_at must be non-empty" in errors
    assert "preview_partition[2].end_paragraph_n must match a visible Paragraph n" in errors
    assert "preview_partition[2].status must be complete or open_tail" in errors


def test_ingest_result_validator_requires_first_partition_to_match_unit() -> None:
    errors = validate_ingest_result(
        {
            "unit": _unit(2, "paragraph_end"),
            "preview_partition": [_partition("First move", 1, "paragraph_end")],
        },
        tool_results=[],
    )

    assert "preview_partition[0] must match unit" in errors


def test_ingest_result_validator_allows_tool_preflight_without_preview_partition() -> None:
    errors = validate_ingest_unit_memory_tool_args(
        {
            "unit": _unit(1, "paragraph_end"),
            "memory_recalls": [
                {
                    "recall_id": "r1",
                    "recall_text": "earlier setup",
                    "basis": "selected_source_unit",
                }
            ],
        },
    )

    assert errors == []


def test_ingest_tool_arg_validator_rejects_missing_and_empty_recalls() -> None:
    missing_errors = validate_ingest_unit_memory_tool_args({"unit": _unit(1, "paragraph_end")})
    empty_errors = validate_ingest_unit_memory_tool_args(
        {"unit": _unit(1, "paragraph_end"), "memory_recalls": []}
    )

    assert "memory_recalls must be a non-empty array for retrieve_unit_memory" in missing_errors
    assert "memory_recalls must be a non-empty array for retrieve_unit_memory" in empty_errors


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


def test_ingest_writes_manifest_and_uses_xml_unit_boundary_contract(tmp_path: Path, monkeypatch):
    """Ingest should write a prompt manifest and use the current unit-boundary contract."""

    captured: dict[str, str] = {}

    def fake_structured_output(system_prompt: str, prompt: str, *, output_tool, validator) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        payload = {
            "unit": _unit(1, "Beta."),
            "preview_partition": [_partition("Alpha and beta move", 1, "Beta.")],
            "reason": "The line clearly keeps running.",
            "continuation" + "_pressure": True,
        }
        assert output_tool["name"] == "submit_ingest_result"
        assert validator(payload) == []
        return SimpleNamespace(payload=payload, status="final_output_tool_called", tool_results=[])

    monkeypatch.setattr(llm_calls_module, "invoke_structured_output", fake_structured_output)

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
    assert "end_anchor_text" not in decision
    assert decision["unit"] == {"end_paragraph_n": "1", "end_at": "Beta."}
    assert decision["preview_partition"][0] == {
        "title": "Alpha and beta move",
        "end_paragraph_n": "1",
        "end_at": "Beta.",
        "status": "complete",
    }
    assert decision["memory_recalls"] == []
    assert decision["memory_recalls_status"] == "not_requested"
    assert captured["system_prompt"] == "Follow the structured Ingest prompt in the user message. Use the required submit_ingest_result tool as the final output channel."
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
    assert "boundary_type" not in captured["prompt"]
    assert "You are in the Ingest step of a sequential deep-reading loop." in captured["prompt"]
    assert "form a provisional map of its consecutive semantic units" in captured["prompt"]
    assert "Partition the forward window into coherent reading units, give each provisional unit a compact title" in captured["prompt"]
    assert "What a semantic unit is" in captured["prompt"]
    assert "Conceptually divide the window into consecutive reading units" in captured["prompt"]
    assert "compact local-function title" in captured["prompt"]
    assert "Only the committed first unit gets a boundary rationale" in captured["prompt"]
    assert "Do not write reasons, explanations, summaries, or interpretive comments for later provisional units" in captured["prompt"]
    assert '"preview_partition"' in captured["prompt"]
    assert "preview_partition[0]" in captured["prompt"]
    assert '"open_tail"' in captured["prompt"]
    assert "A boundary may fall inside a paragraph" in captured["prompt"]
    assert "The window is assembled from paragraph slices" in captured["prompt"]
    assert "Lexical cohesion / topic continuity" in captured["prompt"]
    assert "end_paragraph_n" in captured["prompt"]
    assert "paragraph_end" in captured["prompt"]
    assert "A recall is a retrieval target for prior reading memory" in captured["prompt"]
    assert "using the selected unit as the cue" in captured["prompt"]
    assert "book's ongoing movement" in captured["prompt"]
    assert "look backward beyond the selected unit" in captured["prompt"]
    assert "inside the selected unit itself" in captured["prompt"]
    assert "# Source scope" in captured["prompt"]
    assert "not treat any text in `CurrentView / Content` as already-read memory evidence" in captured["prompt"]
    assert "remaining preview text is future source text" in captured["prompt"]
    assert "describe a broader prior-memory target" in captured["prompt"]
    assert "# Retrieval-friendly content" in captured["prompt"]
    assert "does not need to assert that the prior memory already exists" in captured["prompt"]
    assert "这位青年人或陌生沙门" in captured["prompt"]
    assert "Do not mention paragraph numbers" in captured["prompt"]
    assert "Paragraph 109" in captured["prompt"]
    assert "Prefer one strong focused recall over several weak recalls" in captured["prompt"]
    assert "instead of inventing a name" in captured["prompt"]
    assert '"memory_recalls"' not in captured["prompt"]
    assert "The Unit Memory retrieval tool call is the only place to submit recall targets" in captured["prompt"]
    assert "Do not include `memory_recalls` in this final result" in captured["prompt"]
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
    assert "Ignore pure ornament / divider / separator lines" in captured["prompt"]
    assert "Boundary closure check" not in captured["prompt"]
    assert "end_anchor_text" not in captured["prompt"]
    assert "boundary rationale" in captured["prompt"]
    assert "boundary rationale for the first unit only" in captured["prompt"]
    assert "Do not include rationale, summary, commentary, explanation, or extra fields inside any `preview_partition` item" in captured["prompt"]
    assert "not a second source span" in captured["prompt"]
    assert "same primary language as the current source text" in captured["prompt"]
    assert "Set each recall `basis` exactly to `selected_source_unit`" in captured["prompt"]
    assert "Mainline preview" not in captured["prompt"]
    assert manifest["node_name"] == "ingest"
    assert manifest["prompt_version"] == "attentional_v2.ingest.v17"
    assert manifest["prompt_assembly"]["output_contract"] == "ingest_unit_boundary_preview_partition_json_v3"
    assert manifest["prompt_assembly"]["owner_node"] == "ingest"


def test_ingest_tool_loop_returns_recalls_and_runtime_status(tmp_path: Path, monkeypatch):
    captured: dict[str, object] = {}

    def fake_tool_loop(system_prompt, prompt, *, action_tools, output_tool, tool_handler, validator, max_tool_calls):
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        captured["tools"] = action_tools
        captured["output_tool"] = output_tool
        tool_args = {
            "unit": _unit(1, "Beta."),
            "memory_recalls": [
                {"recall_id": "r1", "recall_text": "the earlier beta setup", "basis": "selected_source_unit"}
            ],
        }
        tool_result = tool_handler(
            "retrieve_unit_memory",
            tool_args,
            "tool-1",
        )
        captured["tool_result"] = tool_result
        payload = {
            "unit": _unit(1, "Beta."),
            "preview_partition": [_partition("Beta closes", 1, "Beta.")],
            "reason": "Beta closes the local move.",
        }
        assert validator(payload, [{"name": "retrieve_unit_memory", "args": tool_args, "result": tool_result}]) == []
        return SimpleNamespace(
            payload=payload,
            status="action_tool_called",
            tool_results=[{"name": "retrieve_unit_memory", "args": tool_args, "result": tool_result}],
        )

    monkeypatch.setattr(llm_calls_module, "invoke_tool_loop_with_structured_output", fake_tool_loop)

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
    assert result["memory_recalls_status"] == "action_tool_args"
    assert result["tool_loop_status"] == "tool_called"
    assert result["tool_result_summary"]["status"] == "ok"
    assert result["tool_result_summary"]["tool_call_id_seen"] == "tool-1"
    assert captured["tools"][0]["name"] == "retrieve_unit_memory"
    recall_basis_schema = captured["tools"][0]["input_schema"]["properties"]["memory_recalls"]["items"]["properties"]["basis"]
    assert recall_basis_schema["enum"] == ["selected_source_unit"]
    assert "unit" in captured["tools"][0]["input_schema"]["properties"]
    assert "preview_partition" not in captured["tools"][0]["input_schema"]["properties"]
    assert "boundary_type" not in captured["tools"][0]["input_schema"]["properties"]
    assert captured["output_tool"]["name"] == "submit_ingest_result"
    assert "unit" in captured["output_tool"]["input_schema"]["properties"]
    assert "preview_partition" in captured["output_tool"]["input_schema"]["properties"]
    assert "preview_partition" in captured["output_tool"]["input_schema"]["required"]
    assert "memory_recalls" not in captured["output_tool"]["input_schema"]["properties"]
    assert "memory_recalls" not in captured["output_tool"]["input_schema"]["required"]
    assert "boundary_type" not in captured["output_tool"]["input_schema"]["properties"]
    assert "memory_query" not in json.dumps(captured["tools"], ensure_ascii=False)


def test_ingest_empty_recall_tool_call_is_runtime_noop(tmp_path: Path, monkeypatch):
    captured: dict[str, object] = {"retrieval_handler_called": False}

    def fake_tool_loop(system_prompt, prompt, *, action_tools, output_tool, tool_handler, validator, max_tool_calls):
        tool_args = {"unit": _unit(1, "Beta."), "memory_recalls": []}
        tool_result = tool_handler(
            "retrieve_unit_memory",
            tool_args,
            "tool-empty",
        )
        captured["tool_result"] = tool_result
        payload = {
            "unit": _unit(1, "Beta."),
            "preview_partition": [_partition("Beta closes", 1, "Beta.")],
            "reason": "Beta closes the local move.",
        }
        assert validator(payload, [{"name": "retrieve_unit_memory", "args": tool_args, "result": tool_result}]) == []
        return SimpleNamespace(
            payload=payload,
            status="action_tool_called",
            tool_results=[{"name": "retrieve_unit_memory", "args": tool_args, "result": tool_result}],
        )

    def unexpected_retrieval_handler(_args):
        captured["retrieval_handler_called"] = True
        return {"status": "contract_violation", "degradation_reason": "should_not_run"}

    monkeypatch.setattr(llm_calls_module, "invoke_tool_loop_with_structured_output", fake_tool_loop)

    result = ingest(
        current_view_position={"current_chapter_id": 1, "current_cursor": {"paragraph_index": 1, "char_offset": 0}},
        current_view_content={"paragraph_slices": [{"paragraph_index": 1, "text": "Beta."}]},
        output_dir=tmp_path,
        unit_memory_tool_handler=unexpected_retrieval_handler,
    )

    assert captured["retrieval_handler_called"] is False
    assert captured["tool_result"]["status"] == "empty_tool_noop"
    assert result["memory_recalls"] == []
    assert result["memory_recalls_status"] == "empty_tool_noop"
    assert result["tool_loop_status"] == "tool_called"
    assert result["tool_result_summary"]["degradation_reason"] == "empty_memory_recalls_noop"


def test_ingest_derives_recalls_from_tool_args_and_ignores_bad_final_echo(tmp_path: Path, monkeypatch):
    captured: dict[str, object] = {}

    def fake_tool_loop(system_prompt, prompt, *, action_tools, output_tool, tool_handler, validator, max_tool_calls):
        tool_result = {
            "status": "ok",
            "effective_mode": "text_only",
            "retrieval_summary": {"recall_count": 1, "candidate_unit_count": 0, "selected_unit_count": 0},
        }
        tool_args = {
            "unit": _unit(1, "乔文达仍然跟随他。"),
            "memory_recalls": [
                {
                    "recall_id": "r1",
                    "recall_text": "悉达多离开婆罗门家庭并带着乔文达走向沙门修行。",
                    "basis": "selected_source_unit",
                }
            ],
        }
        legacy_bad_payload = {
            "unit": _unit(1, "乔文达仍然跟随他。"),
            "preview_partition": [_partition("乔文达继续跟随", 1, "乔文达仍然跟随他。")],
            "reason": "The unit closes here.",
            "memory_recalls": [
                {
                    "recall_id": "legacy",
                    "recall_text": "Earlier reading about Siddhartha leaving home with Govinda.",
                    "basis": "wrong",
                }
            ],
        }
        captured["legacy_bad_errors"] = validator(
            legacy_bad_payload,
            [{"name": "retrieve_unit_memory", "args": tool_args, "result": tool_result}],
        )
        return SimpleNamespace(
            payload=legacy_bad_payload,
            status="action_tool_called",
            tool_results=[{"name": "retrieve_unit_memory", "args": tool_args, "result": tool_result}],
        )

    monkeypatch.setattr(llm_calls_module, "invoke_tool_loop_with_structured_output", fake_tool_loop)

    result = ingest(
        current_view_position={"current_chapter_id": 1, "current_cursor": {"paragraph_index": 1, "char_offset": 0}},
        current_view_content={
            "paragraph_slices": [
                {
                    "paragraph_index": 1,
                    "text": "悉达多继续向前走，乔文达仍然跟随他。两个人离开婆罗门的家，走向沙门的修行生活。",
                }
            ]
        },
        output_dir=tmp_path,
        unit_memory_tool_handler=lambda _args: {"status": "ok"},
    )

    assert captured["legacy_bad_errors"] == []
    assert result["memory_recalls"][0]["recall_text"].startswith("悉达多")


def test_ingest_contract_failure_propagates_llm_contract(tmp_path: Path, monkeypatch):
    """Structured-output contract failures must not become empty fallback boundaries."""

    def fake_tool_loop(*_args, **_kwargs):
        raise llm_calls_module.ReaderLLMError(
            "structured output contract failed",
            problem_code="llm_contract",
        )

    monkeypatch.setattr(llm_calls_module, "invoke_tool_loop_with_structured_output", fake_tool_loop)

    with pytest.raises(llm_calls_module.ReaderLLMError) as exc_info:
        ingest(
            current_view_position={"current_chapter_id": 1, "current_cursor": {"paragraph_index": 1, "char_offset": 0}},
            current_view_content={"paragraph_slices": [{"paragraph_index": 1, "text": "Beta."}]},
            output_dir=tmp_path,
            unit_memory_tool_handler=lambda _args: {"status": "ok"},
        )

    assert exc_info.value.problem_code == "llm_contract"


def test_ingest_can_trim_leading_boundary_residue(tmp_path: Path, monkeypatch):
    """Ingest preserves the selected end anchor for a short structural unit."""

    def fake_structured_output(_system_prompt: str, _prompt: str, **_kwargs) -> object:
        return SimpleNamespace(payload={
            "unit": _unit(2, "运用专长，发挥杠杆效应，最终你会得到自己应得的。"),
            "preview_partition": [
                _partition(
                    "杠杆效应的原则落点",
                    2,
                    "运用专长，发挥杠杆效应，最终你会得到自己应得的。",
                )
            ],
            "reason": "The divider is a structural cue, not content.",
        })

    monkeypatch.setattr(llm_calls_module, "invoke_structured_output", fake_structured_output)

    preview_sentences = [
        _sentence("c1-s1", "∨", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "运用专长，发挥杠杆效应，最终你会得到自己应得的。", sentence_index=2, paragraph_index=2),
    ]

    decision = _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert "decision" not in decision
    assert "selection" + "_mode" not in decision
    assert decision["unit"] == {
        "end_paragraph_n": "2",
        "end_at": "运用专长，发挥杠杆效应，最终你会得到自己应得的。",
    }


def test_ingest_refuses_to_trim_leading_lexical_content(tmp_path: Path, monkeypatch):
    """Ingest no longer exposes a separate mutable start boundary."""

    def fake_structured_output(_system_prompt: str, _prompt: str, **_kwargs) -> object:
        return SimpleNamespace(payload={
            "unit": _unit(1, "Other people are typically a problem until they prove otherwise."),
            "preview_partition": [
                _partition(
                    "People as a problem frame",
                    1,
                    "Other people are typically a problem until they prove otherwise.",
                )
            ],
            "reason": "The visible sentence completes the local move.",
        })

    monkeypatch.setattr(llm_calls_module, "invoke_structured_output", fake_structured_output)

    preview_sentences = [
        _sentence("c1-s1", "People want things from other people.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Other people are typically a problem until they prove otherwise.", sentence_index=2, paragraph_index=1),
    ]

    decision = _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert decision["unit"] == {
        "end_paragraph_n": "1",
        "end_at": "Other people are typically a problem until they prove otherwise.",
    }
    assert "start_sentence_id" not in decision


def test_ingest_llm_failure_does_not_return_empty_boundary_for_heading_preview(tmp_path: Path, monkeypatch):
    """LLM failure should stop Ingest instead of returning an empty boundary."""

    monkeypatch.setattr(
        llm_calls_module,
        "invoke_structured_output",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            llm_calls_module.ReaderLLMError("temporary ingest failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "认识财富创造的原理", sentence_index=1, paragraph_index=1, text_role="section_heading"),
        _sentence("c1-s2", "能学会。", sentence_index=2, paragraph_index=2),
        _sentence("c1-s3", "而且值得学。", sentence_index=3, paragraph_index=2),
    ]

    with pytest.raises(llm_calls_module.ReaderLLMError) as exc_info:
        _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert exc_info.value.problem_code == "network_blocked"


def test_ingest_llm_failure_does_not_return_empty_boundary_for_body_preview(tmp_path: Path, monkeypatch):
    """Ordinary body previews must not be settled from an empty LLM boundary."""

    monkeypatch.setattr(
        llm_calls_module,
        "invoke_structured_output",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            llm_calls_module.ReaderLLMError("temporary ingest failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "Alpha.", sentence_index=1, paragraph_index=1),
        _sentence("c1-s2", "Beta.", sentence_index=2, paragraph_index=1),
        _sentence("c1-s3", "Gamma.", sentence_index=3, paragraph_index=2),
    ]

    with pytest.raises(llm_calls_module.ReaderLLMError) as exc_info:
        _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert exc_info.value.problem_code == "network_blocked"


def test_ingest_llm_failure_does_not_return_empty_boundary_for_heading_only(tmp_path: Path, monkeypatch):
    """Heading-only previews still require a valid Ingest boundary."""

    monkeypatch.setattr(
        llm_calls_module,
        "invoke_structured_output",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            llm_calls_module.ReaderLLMError("temporary ingest failure", problem_code="network_blocked")
        ),
    )

    preview_sentences = [
        _sentence("c1-s1", "Chapter 2", sentence_index=1, paragraph_index=1, text_role="chapter_heading"),
    ]

    with pytest.raises(llm_calls_module.ReaderLLMError) as exc_info:
        _ingest_boundary_call(tmp_path=tmp_path, preview_sentences=preview_sentences)

    assert exc_info.value.problem_code == "network_blocked"


def test_digest_uses_live_xml_prompt_and_filters_surface_reactions(tmp_path: Path, monkeypatch):
    """Digest uses XML prompt assembly and keeps only source-anchored reader-facing reactions."""

    captured: dict[str, str] = {}

    def fake_structured_output(system_prompt: str, prompt: str, *, output_tool, validator) -> object:
        captured["system_prompt"] = system_prompt
        captured["prompt"] = prompt
        payload = {
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
            "understanding": "The current unit flips the frame around Alpha hinge.",
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
        assert output_tool["name"] == "submit_digest_result"
        assert validator(payload) == []
        return SimpleNamespace(payload=payload, status="final_output_tool_called")

    monkeypatch.setattr(llm_calls_module, "invoke_structured_output", fake_structured_output)

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

    assert captured["system_prompt"] == "Follow the structured Digest prompt in the user message. Use the required submit_digest_result tool as the final output channel."
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
    assert "# Read" in captured["prompt"]
    assert "Read the current source text and state what you understand from it." in captured["prompt"]
    assert "# Keep key information" in captured["prompt"]
    assert "Keep the minimum content needed to understand what this source text has added." in captured["prompt"]
    assert "For narrative or scene text" in captured["prompt"]
    assert "For claim, concept, or argument text" in captured["prompt"]
    assert "For list, taxonomy, or step text" in captured["prompt"]
    assert "# Writing stance" in captured["prompt"]
    assert "rather than the source container itself" in captured["prompt"]
    assert "# Examples" in captured["prompt"]
    assert "## Example 4 - Understanding" in captured["prompt"]
    assert "People have developed several ways to deal with dependence on others." in captured["prompt"]
    assert "# Empty-content exception" in captured["prompt"]
    assert "what this unit gives to the ongoing reading" not in captured["prompt"]
    assert "Write one holistic Understanding for this unit." not in captured["prompt"]
    assert "Do not split Understanding by sentence, paragraph, theme, future use, or separate memory point." not in captured["prompt"]
    assert "Split into multiple entries" not in captured["prompt"]
    assert "<Response>" in captured["prompt"]
    assert "<Annotation>" in captured["prompt"]
    assert '"understanding": "..."' in captured["prompt"]
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
        "memory_text": "The current unit flips the frame around Alpha hinge.",
    }
    assert op["target_key"] != "legacy-ignored"
    assert manifest["node_name"] == "digest"
    assert manifest["prompt_version"] == "attentional_v2.digest.v9"
    assert manifest["prompt_assembly"]["spec_id"] == "attentional_v2.digest.xml.v9"
    assert manifest["prompt_assembly"]["output_contract"] == "digest_understanding_response_annotation_json_v3"
    assert "mode" not in manifest["prompt_assembly"]
    assert manifest["prompt_assembly"]["rendered_blocks"] == [
        "ReaderRole",
        "Instruction",
        "BookInfo",
        "ReadingMemory",
        "CurrentFocus",
        "OutputContract",
    ]


def test_digest_rejects_legacy_understanding_list_payload(tmp_path: Path, monkeypatch):
    """Digest should not silently accept a legacy Understanding list payload."""

    def fake_structured_output(system_prompt: str, prompt: str, *, output_tool, validator) -> object:
        payload: dict[str, object] = {
            "response": "A compact response remains valid.",
            "annotations": [],
        }
        payload["understanding"] = [
            {
                "content": "Legacy list item should not become current memory.",
            }
        ]
        errors = validator(payload)
        assert "understanding must be a string" in errors
        raise llm_calls_module.ReaderLLMError(
            "structured output contract failed",
            problem_code="llm_contract",
        )

    monkeypatch.setattr(llm_calls_module, "invoke_structured_output", fake_structured_output)

    with pytest.raises(llm_calls_module.ReaderLLMError) as exc_info:
        digest(
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

    assert exc_info.value.problem_code == "llm_contract"


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
