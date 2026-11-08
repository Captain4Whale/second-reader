import hashlib
import json
import subprocess
from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from src.reading_runtime.run_provenance import capture_workspace, provenance_scope, record_request


def test_actual_tool_history_and_contract_change_request_hash(tmp_path):
    trace = SimpleNamespace(node="ingest", extra={"prompt_version": "test.v1"})
    def record(messages, tools=None):
        return record_request(call_id="c", messages=messages, tools=tools, tool_choice=None,
                              expect_json=False, trace_context=trace)
    original = [SystemMessage(content="system"), HumanMessage(content="invented source")]
    with provenance_scope(tmp_path, stage="read") as receipt:
        a = record(original)
        b = record(original + [AIMessage(content="", tool_calls=[{"id":"t","name":"recall","args":{"query":"x"}}]), ToolMessage(content="result", tool_call_id="t")])
        c = record(original, [{"name":"submit","parameters":{"type":"object"}}])
        assert len({a["request_sha256"], b["request_sha256"], c["request_sha256"]}) == 3
        assert len(receipt["samples"]) == 1
        sample = json.loads(__import__("pathlib").Path(receipt["samples"]["ingest"]["path"]).read_text())
        assert sample["messages"][1]["content"] == "invented source"
    with provenance_scope(tmp_path, stage="read") as second:
        record(original)
        assert receipt["invocation_id"] != second["invocation_id"]
    assert len(list((tmp_path / "_runtime/provenance").glob("*/invocation.json"))) == 2


def test_dirty_patch_covers_staged_unstaged_and_inventory(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout
    git("init"); git("config", "user.name", "test"); git("config", "user.email", "test@example.invalid")
    for name in ("staged", "unstaged"):
        (repo / name).write_text("before\n")
    git("add", "."); git("commit", "-m", "initial")
    clean = capture_workspace(tmp_path / "clean", repo=repo)
    assert clean["code_dirty"] is False and clean["patch"] is None
    (repo / "staged").write_text("staged after\n");git("add", "staged")
    (repo / "unstaged").write_text("unstaged after\n")
    (repo / "untracked").write_text("untracked body\n")
    receipt = capture_workspace(tmp_path / "receipt", repo=repo)
    patch = __import__("pathlib").Path(receipt["patch"]["path"]).read_bytes()
    assert b"staged after" in patch and b"unstaged after" in patch
    assert b"untracked body" not in patch
    assert receipt["patch"]["sha256"] == hashlib.sha256(patch).hexdigest()
    assert receipt["untracked_files"][0]["path"] == "untracked"
    assert receipt["reproduction_complete"] is False
