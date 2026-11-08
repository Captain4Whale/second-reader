from copy import deepcopy
import json

import pytest

from eval.attentional_v2.fixed_history_digest import HistoricalRun, wire_span
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


def test_explicit_published_prompt_retains_full_default_text_and_rejects_unknown():
    inputs = dict(book_title="合成书", author="测试", chapter_title="章", output_language_name="Chinese",
                  reading_memory_lines=["P1 U1: 历史记忆"], current_unit_source={"source_text": "正文"})
    system, result = render_selected_digest_prompt("attentional_v2.digest.v24", **inputs)
    assert system == DIGEST_XML_TRANSPORT_SYSTEM_PROMPT
    assert result.rendered_text == render_digest_prompt_xml(**inputs).rendered_text
    with pytest.raises(ValueError, match="Unknown published"):
        render_selected_digest_prompt("attentional_v2.digest.v999", **inputs)
