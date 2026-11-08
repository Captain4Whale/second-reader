from copy import deepcopy
import json

import pytest

from eval.attentional_v2.fixed_history_digest import HistoricalRun, render_packet
from src.attentional_v2.prompts.selection import render_selected_digest_prompt
from src.attentional_v2.prompts.digest import render_digest_prompt_xml, DIGEST_XML_TRANSPORT_SYSTEM_PROMPT


@pytest.fixture
def history():
    h = HistoricalRun.__new__(HistoricalRun)
    h.run_id = "synthetic-history"
    span = {"start_cursor": {"chapter_id": 1, "paragraph_index": 1, "char_offset": 0},
            "end_cursor": {"chapter_id": 1, "paragraph_index": 1, "char_offset": 2}}
    source = {"source_span_id": "src:c1:p1@0-p1@2", "source_span": span, "source_text": "正文",
              "paragraph_slices": [{"paragraph_index": 1, "text": "正文"}]}
    h.document = {"chapters": [{"id": 1, "title": "章", "paragraphs": [{"paragraph_index": 1, "text": "正文"}]}]}
    h.identity = {"book_title": "合成书", "author": "测试"}
    h.spans = [{"unit_id": "u000002", "sequence_index": 2, "chapter_id": 1,
                "source_span_id": source["source_span_id"], **span, "created_at": "2026-11-08T00:00:05Z"}]
    h.units = {"u000002": {"accepted_source_unit": source}}
    h.by_span = {"src:c1:p0@0-p0@1": {"unit_id": "u000001", "unit_index": 1,
                  "digest": {"understanding": {"content": "历史记忆"}}}}
    h.audit = {"src:c1:p0@0-p0@1": {"understanding": "历史记忆"},
               source["source_span_id"]: {"digest_result": {}}}
    h.recent = {}
    call = {"node": "digest", "status": "ok", "correlation": {"unit_id": "u000002"},
            "call_id": "accepted", "started_at": "2026-11-08T00:00:03Z", "completed_at": "2026-11-08T00:00:04Z",
            "model": "synthetic", "sampling": {}, "prompt_version": "attentional_v2.digest.v24",
            "code_commit": "synthetic", "code_dirty": False}
    h.calls = [call, {**call, "call_id": "later-unaccepted", "started_at": "2026-11-08T00:00:10Z", "completed_at": "2026-11-08T00:00:11Z"}]
    selection = {"source_span_id": source["source_span_id"], "recorded_at": "2026-11-08T00:00:02Z",
                 "line_count": 1, "rendered_retrieved_units": [], "rendered_hot_units": [{
                     "origin": "hot", "unit_id": "old-recent-id", "unit_index": 1, "source_span_id": "src:c1:p0@0-p0@1"}]}
    h.selections = [selection, {**selection, "recorded_at": "2026-11-08T00:00:09Z", "line_count": 0, "rendered_hot_units": []}]
    return h


def test_accepted_attempt_and_pre_call_memory_not_latest_state(history):
    before = deepcopy(history.__dict__)
    packet = history.reconstruct("u000002")
    assert packet["accepted_call"]["call_id"] == "accepted"
    assert packet["reading_memory_lines"] == ["P0 U1: 历史记忆"]
    assert history.__dict__ == before


def test_reconstruction_stops_for_missing_or_future_or_conflicting_memory(history):
    history.by_span["src:c1:p0@0-p0@1"]["unit_index"] = 2
    with pytest.raises(ValueError, match="future"):
        history.reconstruct("u000002")
    history.by_span["src:c1:p0@0-p0@1"]["unit_index"] = 1
    history.audit["src:c1:p0@0-p0@1"]["understanding"] = "不同文本"
    with pytest.raises(ValueError, match="text mismatch"):
        history.reconstruct("u000002")
    with pytest.raises(ValueError, match="accepted unit"):
        history.reconstruct("u999999")


def test_rejects_source_drift(history):
    history.document["chapters"][0]["paragraphs"][0]["text"] = "改文"
    with pytest.raises(ValueError):
        history.reconstruct("u000002")


def test_display_labels_retained_but_never_enter_digest_prompt(history):
    before = history.reconstruct("u000002")
    # Unit Memory reconstructed at resume and original ledger use different labels.
    history.units["u000002"]["accepted_source_unit"]["source_span"] = deepcopy(
        history.units["u000002"]["accepted_source_unit"]["source_span"])
    for cursor in ("start_cursor", "end_cursor"):
        history.units["u000002"]["accepted_source_unit"]["source_span"][cursor]["chapter_ref"] = "Chapter 1"
        history.spans[0][cursor]["chapter_ref"] = "第1章"
    after = history.reconstruct("u000002")
    assert after["label_provenance"]["unit_memory_cursor_refs"]["start_cursor"] == "Chapter 1"
    assert after["label_provenance"]["ledger_cursor_refs"]["start_cursor"] == "第1章"
    assert render_packet(before, "attentional_v2.digest.v24") == render_packet(after, "attentional_v2.digest.v24")
    changed_title = {**after, "chapter_title": "另一标题"}
    assert render_packet(after, "attentional_v2.digest.v24")[1] != render_packet(changed_title, "attentional_v2.digest.v24")[1]


def test_same_label_cannot_hide_changed_canonical_range_or_span_id(history):
    history.units["u000002"]["accepted_source_unit"]["source_span"] = deepcopy(
        history.units["u000002"]["accepted_source_unit"]["source_span"])
    history.units["u000002"]["accepted_source_unit"]["source_span"]["end_cursor"]["char_offset"] = 1
    with pytest.raises(ValueError, match="Unit source mismatch"):
        history.reconstruct("u000002")


def test_explicit_published_prompt_retains_full_default_text_and_rejects_unknown():
    inputs = dict(book_title="合成书", author="测试", chapter_title="章", output_language_name="Chinese",
                  reading_memory_lines=["P1 U1: 历史记忆"], current_unit_source={"source_text": "正文"})
    system, result = render_selected_digest_prompt("attentional_v2.digest.v24", **inputs)
    assert system == DIGEST_XML_TRANSPORT_SYSTEM_PROMPT
    assert result.rendered_text == render_digest_prompt_xml(**inputs).rendered_text
    with pytest.raises(ValueError, match="Unknown published"):
        render_selected_digest_prompt("attentional_v2.digest.v999", **inputs)


def test_capture_saves_usage_and_messages_without_provider_credentials(tmp_path):
    from langchain_core.messages import AIMessage, HumanMessage
    from eval.attentional_v2.fixed_history_digest import CaptureAdapter

    class FakeAdapter:
        def invoke(self, messages, **kwargs):
            return AIMessage(content="", tool_calls=[{
                "name": "submit_digest_result", "args": {"marginalia": []}, "id": "synthetic-call"}],
                usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15})

    capture = CaptureAdapter(FakeAdapter(), tmp_path)
    capture.invoke([HumanMessage(content="synthetic input")],
                   tools=[{"name": "submit_digest_result"}], tool_choice="required",
                   api_key="synthetic-secret-must-not-be-recorded")
    assert capture.response_usages[0]["input_tokens"] == 12
    assert capture.response_usages[0]["output_tokens"] == 3
    assert all("synthetic-secret" not in p.read_text() for p in tmp_path.iterdir())


def test_memory_id_and_order_check_rejects_tampered_serialized_packet(history):
    packet = history.reconstruct("u000002")
    assert packet["memory_selection_check"]["id_and_order_equal"]
    packet["memory_evidence"][0]["unit_id"] = "different-id"
    with pytest.raises(ValueError, match="IDs/order mismatch"):
        history.verify_memory_selection(packet)


def test_memory_body_chapter_labels_preserved_verbatim(history):
    text = "Chapter 1 与第2章形成对照；本章的论点不同。"
    history.by_span["src:c1:p0@0-p0@1"]["digest"]["understanding"]["content"] = text
    history.audit["src:c1:p0@0-p0@1"]["understanding"] = text
    packet = history.reconstruct("u000002")
    assert packet["memory_selection_check"]["body_labels"][0]["labels"] == ["Chapter 1", "第2章"]
    packet["reading_memory_lines"][0] = packet["reading_memory_lines"][0].replace("Chapter 1", "第1章")
    with pytest.raises(ValueError, match="body/label text mismatch"):
        history.verify_memory_selection(packet)


def test_memory_order_check_rejects_reversed_input(history):
    packet = history.reconstruct("u000002")
    older = {**history.selections[0]["rendered_hot_units"][0], "unit_id": "older-id", "unit_index": 0}
    history.selections[0]["rendered_hot_units"].append(older)
    history.selections[0]["line_count"] = 2
    packet["memory_evidence"].append(older)
    packet["reading_memory_lines"].append("P0 U0: 历史记忆")
    assert history.verify_memory_selection(packet)["ordered_ids"] == ["old-recent-id", "older-id"]
    packet["memory_evidence"].reverse()
    packet["reading_memory_lines"].reverse()
    with pytest.raises(ValueError, match="IDs/order mismatch"):
        history.verify_memory_selection(packet)
