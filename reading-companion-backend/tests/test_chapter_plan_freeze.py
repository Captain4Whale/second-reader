"""Offline evidence for plan identity, invalidation and fail-closed resume."""

from dataclasses import replace
import json
import socket
from types import SimpleNamespace

import pytest

from src.attentional_v2 import chapter_planner as planner
from src.attentional_v2.schemas import build_default_reader_policy
from src.attentional_v2.storage import chapter_plan_file, event_stream_file
from tests.test_attentional_v2_chapter_planner import _sample_book_document


@pytest.fixture
def planning(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline planner test forbids networking")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    calls = []
    monkeypatch.setattr(planner, "current_llm_scope", lambda: object())

    def classify(_system, prompt, **kwargs):
        calls.append(prompt)
        return SimpleNamespace(payload={"zone": "main_body", "confidence": "high", "reason": "fixture"})

    monkeypatch.setattr(planner, "invoke_structured_output", classify)
    source = tmp_path / "source"
    source.write_bytes(b"fixed source")
    policy = build_default_reader_policy()

    def write(*, resume=False):
        return planner.write_chapter_plan_artifacts(tmp_path, _sample_book_document(),
            source_path=source, policy_snapshot=policy, continue_mode=resume)["chapter_plan"]

    return write, calls, source, policy


@pytest.mark.parametrize("changed", ["prompt", "policy", "source"])
def test_changed_identity_rejects_resume_but_explicit_fresh_generation_is_recorded(planning, tmp_path, monkeypatch, changed):
    write, calls, source, policy = planning
    first = write()
    original = chapter_plan_file(tmp_path).read_bytes()
    assert len(calls) == 2
    assert write() == first
    assert write(resume=True) == first
    assert len(calls) == 2
    if changed == "prompt":
        monkeypatch.setattr(planner, "ATTENTIONAL_V2_PROMPTS", replace(planner.ATTENTIONAL_V2_PROMPTS, chapter_zone_version="test-version-2"))
    elif changed == "policy":
        policy["policy_version"] = "test-policy-2"
    else:
        source.write_bytes(b"changed source")
    with pytest.raises(RuntimeError, match="Resume chapter plan mismatch"):
        write(resume=True)
    assert len(calls) == 2
    assert chapter_plan_file(tmp_path).read_bytes() == original
    second = write()
    assert len(calls) == 4
    assert second["fingerprint"] != first["fingerprint"]
    assert second["generation"]["reasons"]
    events = [json.loads(line) for line in event_stream_file(tmp_path).read_text().splitlines()]
    assert [event["action"] for event in events] == ["generated", "reused", "reused", "resume_rejected", "generated"]


def test_missing_or_tampered_plan_is_never_a_resume_cache_hit(planning, tmp_path):
    write, calls, _source, _policy = planning
    with pytest.raises(RuntimeError, match="missing_verified_plan"):
        write(resume=True)
    assert not calls
    write()
    path = chapter_plan_file(tmp_path)
    data = json.loads(path.read_text())
    data["reading_plan"]["mainline_chapter_ids"] = [999]
    path.write_text(json.dumps(data))
    with pytest.raises(RuntimeError, match="plan_content_changed"):
        write(resume=True)
    assert len(calls) == 2
