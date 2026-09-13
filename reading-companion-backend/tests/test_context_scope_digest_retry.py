"""Offline bounds for explicitly authorized C-only retries."""

import pytest

from eval.attentional_v2 import retry_context_scope_digest as retry
from eval.attentional_v2 import run_whole_book_digest as single


@pytest.mark.parametrize(
    "outcomes, expected, selected",
    [
        (["ok"], 1, 1),
        (["llm_timeout", "ok"], 2, 2),
        (["network_blocked", "llm_timeout", "ok"], 3, 3),
        (["llm_timeout"] * 3, 3, None),
        (["invalid_structure", "ok"], 1, None),
    ],
)
def test_retry_bound_first_success_and_nontransport_stop(
    tmp_path, monkeypatch, outcomes, expected, selected
):
    monkeypatch.setattr(retry, "verify", lambda path: None)
    monkeypatch.setattr(retry, "update_ledger", lambda *args: None)
    monkeypatch.setattr(retry, "write_review", lambda *args: None)
    calls = []
    for n in range(1, 4):
        (tmp_path / f"attempt-{n}/C").mkdir(parents=True)

    def invoke(path, **kwargs):
        calls.append(path)
        single.reserve_request(path)
        single.write_json(path / "request.json", {"application_request_number": 1})
        outcome = outcomes[len(calls) - 1]
        return {
            "status": "review_pending" if outcome == "ok" else "failed",
            "application_request_count": 1,
            "error": {"problem_code": outcome},
        }

    monkeypatch.setattr(single, "run", invoke)
    result = retry.run(tmp_path)
    assert len(calls) == result["application_request_count"] == expected
    assert result["selected_attempt"] == selected
    assert all(p.name == "C" for p in calls)
    with pytest.raises(FileExistsError):
        retry.run(tmp_path)
    assert len(calls) == expected


def test_prepare_copies_exact_inputs_and_rejects_later_drift(tmp_path, monkeypatch):
    original = tmp_path / "original"
    (original / "C").mkdir(parents=True)
    (original / "C/prompt.json").write_text('{"frozen":"原始 C 提示词"}')
    for name in ("full-source.json", "target-source.json"):
        single.write_json(original / name, {})
    single.write_json(original / "C/summary.json", {"status": "failed"})
    manifest = {
        "run_id": "original_C",
        "artifact_hashes": {
            "prompt.json": single.digest_bytes(
                (original / "C/prompt.json").read_bytes()
            )
        },
    }
    monkeypatch.setattr(retry, "ORIGINAL", original)
    monkeypatch.setattr(retry.experiment, "verify_condition", lambda p: manifest)
    monkeypatch.setattr(retry, "update_ledger", lambda *args: None)
    root = tmp_path / "retries"
    retry.prepare(root)
    retry.verify(root)
    for n in range(1, 4):
        assert (root / f"attempt-{n}/C/prompt.json").read_bytes() == (
            original / "C/prompt.json"
        ).read_bytes()
    (root / "attempt-1/C/prompt.json").write_text("changed")
    with pytest.raises(ValueError, match="Frozen retry input changed"):
        retry.verify(root)
    assert not (root / "request.started.json").exists()
