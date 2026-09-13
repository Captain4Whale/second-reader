"""Offline causal controls and fail-stop tests for the three-request diagnostic."""

import copy
import json

import pytest

from eval.attentional_v2 import context_scope_review as packet
from eval.attentional_v2 import run_context_scope_digest as experiment
from eval.attentional_v2 import run_whole_book_digest as single


def sources():
    paragraphs = []
    offset = 0
    for i, (chapter, text) in enumerate(
        [
            (7, "前文背景。"),
            (8, "目标章节。"),
            (8, "此处值得思考。"),
            (9, "后文背景。"),
        ],
        1,
    ):
        paragraphs.append(
            {
                "global_paragraph_index": i,
                "chapter_id": chapter,
                "chapter_title": str(chapter),
                "paragraph_index": i,
                "text": text,
                "start": offset,
                "end": offset + len(text),
            }
        )
        offset += len(text) + 2
    full = {
        "source_text": "\n\n".join(p["text"] for p in paragraphs),
        "paragraphs": paragraphs,
        "paragraph_slices": [
            {"paragraph_index": p["global_paragraph_index"], "text": p["text"]}
            for p in paragraphs
        ],
    }
    assembly = single.render_digest_prompt_xml(
        book_title="测试书",
        author="测试作者",
        chapter_title="全书",
        output_language_name="Chinese",
        reading_memory_lines=[],
        current_unit_source=full,
    )
    original = {
        "system_prompt": single.DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
        "user_prompt": assembly.rendered_text,
        "output_tool": single.DIGEST_RESULT_TOOL,
    }
    return original, full, experiment.chapter_source(full)


def test_pair_keeps_target_task_identical_and_full_source_once_in_order():
    original, full, target = sources()
    frozen = copy.deepcopy((original, full, target))
    b = experiment.build_chapter_packet(original, full, target, True)
    c = experiment.build_chapter_packet(original, full, target, False)
    experiment.verify_pair(b, c, full, target)
    assert (original, full, target) == frozen
    br, cr = map(single.xml_root, (b["user_prompt"], c["user_prompt"]))
    assert len(br.findall(".//Paragraph")) == 4
    assert len(cr.findall(".//Paragraph")) == 2
    for tag in experiment.FIXED_TAGS:
        import xml.etree.ElementTree as ET

        assert ET.tostring(br.find(tag)) == ET.tostring(
            single.xml_root(original["user_prompt"]).find(tag)
        )
    assert br.findtext("./CurrentFocus/ReadingIntent") == cr.findtext(
        "./CurrentFocus/ReadingIntent"
    )
    assert br.findtext("ReadingMemory").strip() == ""


def test_pair_rejects_extra_target_or_instruction_drift():
    original, full, target = sources()
    b = experiment.build_chapter_packet(original, full, target, True)
    c = experiment.build_chapter_packet(original, full, target, False)
    altered = {**b, "user_prompt": b["user_prompt"].replace("前文背景。", "目标章节。")}
    with pytest.raises(ValueError, match="truncated, duplicated, or reordered"):
        experiment.verify_pair(altered, c, full, target)
    altered = {
        **c,
        "user_prompt": c["user_prompt"].replace(
            experiment.SCOPE_INSTRUCTION, "different task"
        ),
    }
    with pytest.raises(ValueError, match="outside the extra source"):
        experiment.verify_pair(b, altered, full, target)


def test_quote_found_in_full_book_is_not_valid_target_quote():
    _, full, target = sources()
    payload = {
        "understanding": "理解",
        "response": "回应",
        "marginalia": [
            {"kind": "note", "source_quote": quote, "content": "批注"}
            for quote in ("目标章节。", "前文背景。", "不存在的引文")
        ],
    }
    before = copy.deepcopy(payload)
    review = experiment.chapter_review(payload, full, target)
    assert payload == before
    assert [item["target_scope"] for item in review["items"]] == [
        "inside",
        "outside",
        "unlocated",
    ]
    assert review["counts"]["total"] == 3
    assert review["counts"]["valid"] == 1
    assert review["counts"]["outside_target"] == 1
    assert review["items"][1]["full_book_candidates"]


@pytest.mark.parametrize(
    "failure, expected",
    [(None, ["A", "B", "C"]), ("A", ["A"]), ("B", ["A", "B"]), ("C", ["A", "B", "C"])],
)
def test_batch_stops_at_first_failure_and_cannot_be_reentered(
    tmp_path, monkeypatch, failure, expected
):
    calls = []
    monkeypatch.setattr(experiment, "verify_batch", lambda path: {})
    monkeypatch.setattr(experiment, "update_ledger", lambda *args: None)
    monkeypatch.setattr(packet, "render_packet", lambda path: None)
    for condition in experiment.CONDITIONS:
        (tmp_path / condition).mkdir()

    def fake_run(path, **kwargs):
        calls.append(path.name)
        single.reserve_request(path)
        single.write_json(path / "request.json", {"application_request_number": 1})
        return {
            "status": "failed" if path.name == failure else "review_pending",
            "application_request_count": 1,
        }

    monkeypatch.setattr(single, "run", fake_run)
    result = experiment.execute_batch(tmp_path)
    assert calls == expected
    assert result["application_request_count"] == len(expected)
    assert result["status"] == ("failed" if failure else "review_pending")
    assert result["unattempted_conditions"] == [
        c for c in experiment.CONDITIONS if c not in expected
    ]
    with pytest.raises(FileExistsError):
        experiment.execute_batch(tmp_path)
    assert calls == expected


def test_condition_hash_drift_stops_before_generation(tmp_path):
    single.write_json(tmp_path / "source.json", {"source_text": "frozen"})
    single.write_json(
        tmp_path / "manifest.json",
        {
            "condition": "C",
            "source_sha256": experiment.CHAPTER_HASH,
            "application_request_limit": 1,
            "artifact_hashes": {
                "source.json": single.digest_bytes(
                    (tmp_path / "source.json").read_bytes()
                )
            },
        },
    )
    experiment.verify_condition(tmp_path)
    (tmp_path / "source.json").write_text("changed")
    with pytest.raises(ValueError, match="Frozen condition"):
        experiment.verify_condition(tmp_path)
    assert not (tmp_path / "request.started.json").exists()


def test_blind_review_mapping_survives_rerender_and_omits_private_reason(
    tmp_path, monkeypatch
):
    _, full, target = sources()
    raw = {
        "kind": "highlight",
        "source_quote": "目标章节。",
        "selection_reason": "private-only-reason",
        "content": "",
    }
    item = experiment.chapter_review(
        {"understanding": "理解", "response": "回应", "marginalia": [raw]}, full, target
    )["items"][0]
    items = [{**item, "origin": "B", "identity": "B:1"}]
    monkeypatch.setattr(packet, "gather_items", lambda path: items)
    single.write_json(
        tmp_path / "summary.json", {"status": "review_pending", "conditions": {}}
    )
    packet.render_packet(tmp_path)
    key = (tmp_path / "review-key.json").read_bytes()
    review = (tmp_path / "review.md").read_bytes()
    packet.render_packet(tmp_path)
    assert (tmp_path / "review-key.json").read_bytes() == key
    assert (tmp_path / "review.md").read_bytes() == review
    assert b"private-only-reason" not in review
    assert b"B:1" not in review
    assert b"R001" in review


def test_failed_condition_review_keeps_unknown_output_and_http_status(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(packet, "gather_items", lambda path: [])
    (tmp_path / "C").mkdir()
    single.write_json(
        tmp_path / "summary.json",
        {
            "status": "failed",
            "conditions": {
                "C": {
                    "status": "failed",
                    "elapsed_seconds": 902.396,
                    "error": {"type": "ReaderLLMError", "problem_code": "llm_timeout"},
                }
            },
        },
    )
    # Real ledger rows are one-line JSON.
    (tmp_path / "C/llm-standard.jsonl").write_text(
        json.dumps({"error_message": "Error code: 408 - private-provider-message"})
        + "\n"
    )
    packet.render_packet(tmp_path)
    failure = (tmp_path / "C/review.md").read_text()
    assert "HTTP 408" in failure
    assert "不能记为零" in failure
    assert "private-provider-message" not in failure
    assert "未完成条件" in (tmp_path / "review.md").read_text()
    assert "[C 失败记录]" in (tmp_path / "execution-summary.md").read_text()
