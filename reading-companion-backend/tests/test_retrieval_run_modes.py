"""Requested/actual retrieval conditions remain visible and enforceable offline."""

import json
import socket

import pytest

from src.attentional_v2 import unit_memory as memory
from src.attentional_v2.storage import memory_retrieval_config_file, unit_memory_retrieval_trace_file
from tests.test_attentional_v2_unit_memory import _entry


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("READING_MEMORY_RETRIEVAL_MODE", raising=False)
    def forbidden(*args, **kwargs):
        raise AssertionError("offline retrieval test forbids networking")
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def query(index):
    return index.retrieve(book_id="book-demo", query={"query_text": "火车站台 告别", "basis": "selected_source_unit"}, query_source="fixture", current_unit_index=2)


def test_eval_requires_a_declared_condition_and_rejects_invalid_mode(tmp_path):
    with pytest.raises(ValueError, match="explicit"):
        memory.resolve_memory_retrieval_config(tmp_path, {"evaluation_run": True})
    with pytest.raises(ValueError, match="Invalid"):
        memory.resolve_memory_retrieval_config(tmp_path, {"memory_retrieval_mode": "typo"})


@pytest.mark.parametrize("mode", ["off", "text-only"])
def test_off_and_text_only_do_not_use_embeddings(tmp_path, monkeypatch, mode):
    def forbidden(*args, **kwargs):
        pytest.fail("off/text-only reached embeddings")
    monkeypatch.setattr(memory.OllamaEmbedder, "embed", forbidden)
    config = memory.resolve_memory_retrieval_config(tmp_path, {"evaluation_run": True, "memory_retrieval_mode": mode})
    index = memory.UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(_entry("u1", 1, "火车站台上的告别", "站台告别建立了旅程的起点。"))
    if mode == "off":
        monkeypatch.setattr(index, "_lexical_candidates", forbidden)
    result = query(index)
    assert result["effective_mode"] == mode.replace("-", "_")
    assert bool(result["selected_units"]) == (mode == "text-only")
    persisted = json.loads(memory_retrieval_config_file(tmp_path).read_text())
    assert persisted["query_degradation_count"] == 0


def test_hybrid_eval_fails_readiness_when_ollama_is_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(memory.UnitMemoryIndex, "_load_sqlite_vec", lambda *_: True)
    monkeypatch.setattr(memory.OllamaEmbedder, "embed", lambda *_: None)
    with pytest.raises(memory.MemoryRetrievalUnavailable, match="embedding_unavailable"):
        memory.resolve_memory_retrieval_config(tmp_path, {"evaluation_run": True, "memory_retrieval_mode": "hybrid"})
    persisted = json.loads(memory_retrieval_config_file(tmp_path).read_text())
    assert persisted["readiness"]["status"] == "failed"
    assert persisted["query_degradation_count"] == 0  # preflight is not a query


@pytest.mark.parametrize("evaluation", [False, True])
def test_query_failure_after_readiness_is_counted_and_eval_cannot_fall_back(tmp_path, monkeypatch, evaluation):
    with monkeypatch.context() as preflight:
        preflight.setattr(memory.UnitMemoryIndex, "_load_sqlite_vec", lambda *_: True)
        preflight.setattr(memory.OllamaEmbedder, "embed", lambda *_: [0.0] * 1024)
        config = memory.resolve_memory_retrieval_config(tmp_path, {"evaluation_run": evaluation, "memory_retrieval_mode": "hybrid"})
    # Only replace the failing dense query. Real SQLite FTS and result selection run.
    config["strict_retrieval"] = evaluation
    index = memory.UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(_entry("u1", 1, "火车站台上的告别", "站台告别建立了旅程的起点。"), index_vectors=False)
    monkeypatch.setattr(index, "_dense_candidates", lambda *args, **kwargs: ([], "query_embedding_unavailable", 0))
    if evaluation:
        with pytest.raises(memory.MemoryRetrievalUnavailable, match="degraded"):
            query(index)
    else:
        result = query(index)
        assert result["effective_mode"] == "text_only"
        assert result["selected_units"]
    persisted = json.loads(memory_retrieval_config_file(tmp_path).read_text())
    assert persisted["actual_modes"] == ["text_only"]
    assert persisted["query_count"] == persisted["query_degradation_count"] == 1
    assert "RETRIEVAL DEGRADED" in persisted["degradation_warning"]
    assert persisted["ollama_model_id"] == "qwen3-embedding:0.6b"
    row = json.loads(unit_memory_retrieval_trace_file(tmp_path).read_text().splitlines()[-1])
    assert row["query_degradation_count"] == 1
    assert row["embedding_model"] == "qwen3-embedding:0.6b"


def test_empty_recall_is_not_a_degraded_query(tmp_path):
    config = memory.resolve_memory_retrieval_config(tmp_path, {"memory_retrieval_mode": "hybrid"})
    memory.UnitMemoryIndex(tmp_path, config=config).retrieve_for_recalls(book_id="book-demo", recalls=[], query_source="fixture", current_unit_index=1)
    persisted = json.loads(memory_retrieval_config_file(tmp_path).read_text())
    assert persisted["query_count"] == persisted["query_degradation_count"] == 0
    assert persisted["effective_mode"] == "not_requested"
