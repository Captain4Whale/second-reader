import json
import sqlite3

from src.attentional_v2.storage import (
    memory_retrieval_config_file,
    unit_memory_retrieval_trace_file,
    unit_memory_sqlite_file,
)
from src.attentional_v2.unit_memory import (
    UnitMemoryIndex,
    build_fts5_match_query,
    build_unit_memory_entry,
    effective_query_for_accepted_unit,
    resolve_memory_retrieval_config,
    retrieval_docs_from_entry,
)


def _source_unit(unit_id: str, sequence_index: int, text: str) -> dict[str, object]:
    return {
        "unit_id": unit_id,
        "sequence_index": sequence_index,
        "source_span_id": f"src:c1:p{sequence_index}@0-p{sequence_index}@{len(text)}",
        "source_span": {
            "start_cursor": {"chapter_id": 1, "paragraph_index": sequence_index, "char_offset": 0},
            "end_cursor": {"chapter_id": 1, "paragraph_index": sequence_index, "char_offset": len(text)},
        },
        "source_text": text,
        "paragraph_slices": [
            {
                "paragraph_index": sequence_index,
                "text_role": "body",
                "start_char": 0,
                "end_char": len(text),
                "text": text,
            }
        ],
    }


def _digest_result(understanding: str, response: str = "", annotation: str = "") -> dict[str, object]:
    annotations = (
        [
            {
                "source_quote": annotation,
                "content": f"mark {annotation}",
                "prior_link": None,
                "outside_link": None,
                "search_intent": None,
            }
        ]
        if annotation
        else []
    )
    return {
        "reading_impression": response,
        "surfaced_reactions": annotations,
        "memory_uptake_ops": [
            {
                "op": "append",
                "target_store": "recent_reading_memory",
                "payload": {"kind": "fact", "memory_text": understanding},
            }
        ],
    }


def _entry(unit_id: str, sequence_index: int, text: str, understanding: str) -> dict[str, object]:
    return build_unit_memory_entry(
        book_id="book-demo",
        chapter_id=1,
        chapter_ref="Chapter 1",
        source_unit=_source_unit(unit_id, sequence_index, text),
        digest_result=_digest_result(understanding, response="quiet pressure", annotation=text[:6]),
        memory_retrieval_mode="text_only",
    )


def test_unit_memory_entry_derives_weighted_surface_docs():
    entry = _entry("u000001", 1, "火车站台上的告别", "站台告别建立了旅程的起点。")

    docs = retrieval_docs_from_entry(entry)

    assert {doc["surface"] for doc in docs} == {
        "unit_source",
        "unit_understanding",
        "unit_response",
        "unit_annotation",
    }
    assert [doc for doc in docs if doc["surface"] == "unit_understanding"][0]["text"] == "站台告别建立了旅程的起点。"
    assert "\n" in [doc for doc in docs if doc["surface"] == "unit_annotation"][0]["text"]


def test_fts_query_builder_quotes_phrases_and_skips_short_queries():
    query, reason = build_fts5_match_query("火车站台。旅程开始；人物离开")

    assert reason == ""
    assert '"火车站台"' in query
    assert " OR " in query
    assert build_fts5_match_query("火")[1] == "empty_or_too_short_query"


def test_text_only_unit_memory_index_writes_and_retrieves_prior_units(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
        "max_units_to_digest_context": 3,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(_entry("u000001", 1, "火车站台上的告别", "站台告别建立了旅程的起点。"), index_vectors=False)
    index.write_entry(_entry("u000002", 2, "海边的静默", "海边静默改变了人物之间的距离。"), index_vectors=False)

    result = index.retrieve(
        book_id="book-demo",
        query={"query_version": "unit_memory_query.v1", "query_text": "火车站台 告别", "basis": "selected_source_unit"},
        query_source="ingest_output",
        current_unit_index=3,
    )

    assert unit_memory_sqlite_file(tmp_path).exists()
    assert result["effective_mode"] == "text_only"
    assert result["selected_units"][0]["unit_id"] == "u000001"
    trace_lines = unit_memory_retrieval_trace_file(tmp_path).read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(trace_lines[-1])["candidate_counts"]["lexical_docs"] >= 1

    with sqlite3.connect(unit_memory_sqlite_file(tmp_path)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM unit_memory_entries").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM retrieval_docs").fetchone()[0] >= 4


def test_hybrid_mode_degrades_when_vector_adapter_is_unavailable(tmp_path):
    config = {
        "mode": "hybrid",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(_entry("u000001", 1, "火车站台上的告别", "站台告别建立了旅程的起点。"), index_vectors=False)

    result = index.retrieve(
        book_id="book-demo",
        query={"query_version": "unit_memory_query.v1", "query_text": "火车站台 告别", "basis": "selected_source_unit"},
        query_source="ingest_output",
        current_unit_index=2,
    )

    assert result["mode"] == "hybrid"
    assert result["effective_mode"] in {"hybrid", "text_only"}
    if result["effective_mode"] == "text_only":
        assert "unavailable" in str(result["degradation_reason"]) or "embedding" in str(result["degradation_reason"])


def test_effective_query_falls_back_when_boundary_was_retried():
    source_unit = _source_unit("u000003", 3, "新的段落提出了一个关于记忆的问题。")

    query, source = effective_query_for_accepted_unit(
        ingest_query={"query_version": "unit_memory_query.v1", "query_text": "旧边界查询", "basis": "selected_source_unit"},
        source_unit=source_unit,
        boundary_was_retried=True,
        boundary_resolution_status="matched",
    )

    assert source == "runtime_source_text_fallback"
    assert query["query_text"].startswith("新的段落")


def test_resolve_memory_retrieval_config_persists_and_restores_mode(tmp_path):
    first = resolve_memory_retrieval_config(tmp_path, {"memory_retrieval_mode": "text_only"})
    resumed = resolve_memory_retrieval_config(tmp_path, {}, continue_mode=True)

    assert first["mode"] == "text_only"
    assert resumed["mode"] == "text_only"
    assert memory_retrieval_config_file(tmp_path).exists()
