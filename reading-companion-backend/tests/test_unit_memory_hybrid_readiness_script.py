import importlib.util
from pathlib import Path
import urllib.error


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_unit_memory_hybrid_readiness.py"
SPEC = importlib.util.spec_from_file_location("check_unit_memory_hybrid_readiness", SCRIPT_PATH)
hybrid_readiness = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(hybrid_readiness)


def test_hybrid_readiness_reports_ollama_unreachable(monkeypatch):
    monkeypatch.setattr(
        hybrid_readiness,
        "_load_sqlite_vec",
        lambda: {"import_ok": True, "load_ok": True, "vec0_table_ok": True, "version": "test", "error": ""},
    )

    def fake_fetch_json(*_args, **_kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(hybrid_readiness, "_fetch_json", fake_fetch_json)

    summary = hybrid_readiness.probe_hybrid_readiness(
        base_url="http://127.0.0.1:11434",
        model_id="qwen3-embedding:0.6b",
        expected_dimension=1024,
        timeout_ms=100,
    )

    assert summary["status"] == "blocked"
    assert summary["blocking_reasons"] == ["ollama_unreachable"]
    assert summary["ollama"]["reachable"] is False


def test_hybrid_readiness_reports_missing_model(monkeypatch):
    monkeypatch.setattr(
        hybrid_readiness,
        "_load_sqlite_vec",
        lambda: {"import_ok": True, "load_ok": True, "vec0_table_ok": True, "version": "test", "error": ""},
    )
    monkeypatch.setattr(
        hybrid_readiness,
        "_fetch_json",
        lambda *_args, **_kwargs: {"models": [{"name": "other-model:latest"}]},
    )

    summary = hybrid_readiness.probe_hybrid_readiness(
        base_url="http://127.0.0.1:11434",
        model_id="qwen3-embedding:0.6b",
        expected_dimension=1024,
        timeout_ms=100,
    )

    assert summary["status"] == "blocked"
    assert summary["blocking_reasons"] == ["ollama_model_missing"]
    assert summary["ollama"]["reachable"] is True
    assert summary["ollama"]["model_available"] is False


def test_hybrid_readiness_accepts_model_and_embedding_dimension(monkeypatch):
    monkeypatch.setattr(
        hybrid_readiness,
        "_load_sqlite_vec",
        lambda: {"import_ok": True, "load_ok": True, "vec0_table_ok": True, "version": "test", "error": ""},
    )

    def fake_fetch_json(url, **_kwargs):
        if url.endswith("/api/tags"):
            return {"models": [{"name": "qwen3-embedding:0.6b"}]}
        if url.endswith("/api/embed"):
            return {"embeddings": [[0.1, 0.2, 0.3]]}
        raise AssertionError(url)

    monkeypatch.setattr(hybrid_readiness, "_fetch_json", fake_fetch_json)

    summary = hybrid_readiness.probe_hybrid_readiness(
        base_url="http://127.0.0.1:11434",
        model_id="qwen3-embedding:0.6b",
        expected_dimension=3,
        timeout_ms=100,
    )

    assert summary["status"] == "ok"
    assert summary["blocking_reasons"] == []
    assert summary["embedding"]["ok"] is True
    assert summary["embedding"]["dimension"] == 3
