import json
import sqlite3

import pytest

import src.attentional_v2.unit_memory as unit_memory_module
from src.attentional_v2.storage import (
    memory_retrieval_config_file,
    unit_memory_retrieval_trace_file,
    unit_memory_sqlite_file,
)
from src.attentional_v2.unit_memory import (
    SURFACE_CHANNEL_WEIGHTS,
    UnitMemoryIndex,
    build_fts5_match_query,
    build_unit_memory_entry,
    effective_query_for_accepted_unit,
    normalize_unit_memory_recalls,
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
                "payload": {"memory_text": understanding},
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


def test_fts_query_builder_extracts_recall_terms_from_meta_wording():
    query, reason = build_fts5_match_query(
        "先前阅读中悉达多对佛陀法义的态度和评价，以及乔文达对佛陀法义宗旨的了解程度"
    )

    assert reason == ""
    assert '"悉达多"' in query
    assert '"乔文达"' in query
    assert '"先前阅读中"' not in query

    english_query, _reason = build_fts5_match_query(
        "Earlier reading on present value versus future value and how perceived attractiveness changes valuation"
    )
    assert '"present"' in english_query
    assert '"value"' in english_query
    assert '"Earlier"' not in english_query


def test_unit_memory_recalls_force_selected_source_unit_basis():
    recalls = normalize_unit_memory_recalls(
        [
            {
                "recall_id": "r1",
                "recall_text": "悉达多和乔文达此前共同求道。",
                "basis": "selected_unit_paragraphs_128_130",
            }
        ]
    )

    assert recalls == [
        {
            "recall_id": "r1",
            "recall_text": "悉达多和乔文达此前共同求道。",
            "basis": "selected_source_unit",
        }
    ]

    fallback_recalls = normalize_unit_memory_recalls(
        [
            {
                "recall_id": "runtime_fallback",
                "recall_text": "当前 source unit 文本。",
                "basis": "runtime_source_text_fallback",
            }
        ]
    )
    assert fallback_recalls[0]["basis"] == "runtime_source_text_fallback"


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


def test_text_only_retrieval_handles_meta_recall_wording(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
        "max_units_to_digest_context": 3,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(
        _entry(
            "u000001",
            1,
            "悉达多认真聆听佛陀说法。",
            "悉达多对佛陀法义保持敬意，但认为法义不能替代个人亲身求道。",
        ),
        index_vectors=False,
    )
    index.write_entry(_entry("u000002", 2, "乔文达继续追随朋友。", "乔文达仍把追随悉达多视为自己的道路。"), index_vectors=False)

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[
            {
                "recall_id": "r1",
                "recall_text": "先前阅读中悉达多对佛陀法义的态度和评价",
                "basis": "selected_source_unit",
            }
        ],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=3,
    )

    assert result["selected_units"][0]["unit_id"] == "u000001"
    trace_lines = unit_memory_retrieval_trace_file(tmp_path).read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(trace_lines[-1])["candidate_counts"]["lexical_docs"] >= 1


def test_text_only_retrieval_suppresses_empty_understanding_and_selects_renderable_unit(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
        "max_units_to_digest_context": 3,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(_entry("u000001", 1, "火车站台告别", ""), index_vectors=False)
    index.write_entry(
        _entry("u000002", 2, "火车站台上的旅程重新开始", "站台告别建立了旅程的起点。"),
        index_vectors=False,
    )

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "火车站台 告别 旅程", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=3,
    )

    assert [item["unit_id"] for item in result["selected_units"]] == ["u000002"]
    trace = json.loads(unit_memory_retrieval_trace_file(tmp_path).read_text(encoding="utf-8").strip().splitlines()[-1])
    assert trace["selected_units"][0]["unit_id"] == "u000002"
    assert trace["suppressed_units"][0]["unit_id"] == "u000001"
    assert trace["suppressed_units"][0]["reason"] == "candidate_not_renderable_empty_understanding"


def test_text_only_retrieval_handles_english_concept_recall(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
        "max_units_to_digest_context": 3,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(
        _entry(
            "u000001",
            1,
            "People assign value based on how others perceive desirability.",
            "Perceived attractiveness changes valuation because people often want what others seem to want.",
        ),
        index_vectors=False,
    )
    index.write_entry(_entry("u000002", 2, "A separate example discusses social distance.", "Social distance shapes cooperation."), index_vectors=False)

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[
            {
                "recall_id": "r1",
                "recall_text": "Earlier reading about perceived attractiveness and valuation",
                "basis": "selected_source_unit",
            }
        ],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=3,
    )

    assert result["selected_units"][0]["unit_id"] == "u000001"
    trace = json.loads(unit_memory_retrieval_trace_file(tmp_path).read_text(encoding="utf-8").strip().splitlines()[-1])
    assert trace["candidate_counts"]["lexical_docs"] >= 1


def test_retrieval_trace_records_horizon_gate_counts(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 2,
        "recent_neighbor_exclusion_unit_count": 1,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(_entry("u000001", 1, "火车站台上的告别", "站台告别建立了旅程的起点。"), index_vectors=False)

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "火车站台 告别", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=3,
    )

    assert result["selected_units"] == []
    trace = json.loads(unit_memory_retrieval_trace_file(tmp_path).read_text(encoding="utf-8").strip().splitlines()[-1])
    assert trace["degradation_reason"] == "below_min_retrievable_prior_units"
    assert trace["horizon"] == {
        "current_unit_index": 3,
        "recent_neighbor_exclusion_unit_count": 1,
        "max_retrievable_unit_index": 2,
        "prior_units_after_recent_exclusion": 1,
        "min_retrievable_prior_units": 2,
    }
    assert trace["candidate_counts"]["remaining_retrievable_units"] == 1


def test_multi_recall_retrieval_aggregates_by_unit_and_records_matches(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
        "max_units_to_digest_context": 4,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(_entry("u000001", 1, "火车站台上的告别", "站台告别建立了旅程的起点。"), index_vectors=False)
    index.write_entry(_entry("u000002", 2, "海边的静默", "海边静默改变了人物之间的距离。"), index_vectors=False)

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[
            {"recall_id": "r1", "recall_text": "火车站台 告别", "basis": "selected_source_unit"},
            {"recall_id": "r2", "recall_text": "海边 静默", "basis": "selected_source_unit"},
        ],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=3,
        tool_call_id="tool-1",
        accepted_source_span_id="src:c1:p3@0-p3@20",
    )

    selected_ids = {item["unit_id"] for item in result["selected_units"]}
    assert {"u000001", "u000002"} <= selected_ids
    assert any("r1" in item.get("matched_recalls", []) for item in result["selected_units"])
    trace_lines = unit_memory_retrieval_trace_file(tmp_path).read_text(encoding="utf-8").strip().splitlines()
    trace = json.loads(trace_lines[-1])
    assert trace["tool_call_id"] == "tool-1"
    assert trace["accepted_source_span_id"] == "src:c1:p3@0-p3@20"
    assert trace["candidate_counts"]["recall_count"] == 2
    assert len(trace["per_recall"]) == 2
    assert trace["selected_units"][0]["matched_recalls"]


def test_retrieval_selection_enforces_per_recall_digest_context_limit(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
        "max_units_after_aggregation": 10,
        "max_units_to_digest_context": 10,
        "max_units_per_recall_to_digest_context": 2,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    for sequence_index in range(1, 6):
        index.write_entry(
            _entry(
                f"u{sequence_index:06d}",
                sequence_index,
                f"共同主题在第 {sequence_index} 个场景里出现。",
                f"共同主题推动第 {sequence_index} 个单元的理解。",
            ),
            index_vectors=False,
        )

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "共同主题", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=6,
    )

    assert len(result["selected_units"]) == 2
    trace = json.loads(unit_memory_retrieval_trace_file(tmp_path).read_text(encoding="utf-8").strip().splitlines()[-1])
    assert trace["selection_config"]["max_units_per_recall_to_digest_context"] == 2
    suppressed_reasons = {item["reason"] for item in trace["suppressed_units"]}
    assert "per_recall_selection_limit_exceeded" in suppressed_reasons


def test_hybrid_vector_status_only_marks_understanding_docs_pending(tmp_path):
    index = UnitMemoryIndex(
        tmp_path,
        config={
            "mode": "hybrid",
            "min_retrievable_prior_units": 0,
            "recent_neighbor_exclusion_unit_count": 0,
        },
    )

    index.write_entry(_entry("u000001", 1, "火车站台上的告别", "站台告别建立了旅程的起点。"), index_vectors=False)

    with sqlite3.connect(unit_memory_sqlite_file(tmp_path)) as connection:
        rows = connection.execute(
            "SELECT surface, vector_index_status FROM retrieval_docs ORDER BY surface"
        ).fetchall()

    statuses = {surface: status for surface, status in rows}
    assert statuses["unit_understanding"] == "pending"
    assert statuses["unit_source"] == "not_requested"
    assert statuses["unit_response"] == "not_requested"
    assert statuses["unit_annotation"] == "not_requested"


def test_dense_channel_weight_exists_only_for_understanding_surface():
    dense_surfaces = {
        surface
        for surface, weights in SURFACE_CHANNEL_WEIGHTS.items()
        if "dense" in weights
    }

    assert dense_surfaces == {"unit_understanding"}


def test_hybrid_dense_retrieval_uses_understanding_vectors_and_filters_distance(tmp_path, monkeypatch):
    pytest.importorskip("sqlite_vec")

    class FakeEmbedder:
        def __init__(self, **kwargs):
            pass

        def embed(self, text):
            lowered = text.lower()
            if "river" in lowered or "ferryman" in lowered or "water" in lowered:
                return [1.0, 0.0, 0.0]
            if "merchant" in lowered or "profit" in lowered:
                return [0.0, 1.0, 0.0]
            return [0.0, 0.0, 1.0]

    monkeypatch.setattr(unit_memory_module, "OllamaEmbedder", FakeEmbedder)
    index = UnitMemoryIndex(
        tmp_path,
        config={
            "mode": "hybrid",
            "embedding_dimension": 3,
            "min_retrievable_prior_units": 0,
            "recent_neighbor_exclusion_unit_count": 0,
            "dense_top_k": 5,
            "lexical_top_k": 5,
            "dense_max_distance": 0.25,
        },
    )
    index.write_entry(
        _entry(
            "u000001",
            1,
            "The old ferryman waits.",
            "The ferryman listens beside flowing water.",
        ),
        index_vectors=True,
    )
    index.write_entry(
        _entry(
            "u000002",
            2,
            "A merchant counts coins.",
            "The merchant measures profit.",
        ),
        index_vectors=True,
    )

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "river crossing", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=3,
    )

    assert result["effective_mode"] == "hybrid"
    assert result["degradation_reason"] == ""
    assert [item["unit_id"] for item in result["selected_units"]] == ["u000001"]
    assert result["selected_units"][0]["best_docs"][0]["channel"] == "dense"
    trace = result["trace"]
    assert trace["candidate_counts"]["dense_docs"] == 1
    assert trace["candidate_counts"]["dense_docs_filtered_by_distance"] >= 1
    assert trace["per_recall"][0]["dense_docs_filtered_by_distance"] >= 1

    with index._connect() as connection:
        assert index._load_sqlite_vec(connection)
        vector_rows = connection.execute("SELECT COUNT(*) FROM retrieval_doc_vectors").fetchone()[0]
        query_cache_rows = connection.execute("SELECT COUNT(*) FROM query_embedding_cache").fetchone()[0]
    assert vector_rows == 2
    assert query_cache_rows == 1


def test_lexical_surface_weights_prioritize_understanding_over_auxiliary_surfaces():
    assert SURFACE_CHANNEL_WEIGHTS["unit_understanding"]["lexical"] > SURFACE_CHANNEL_WEIGHTS["unit_source"]["lexical"]
    assert SURFACE_CHANNEL_WEIGHTS["unit_understanding"]["lexical"] > SURFACE_CHANNEL_WEIGHTS["unit_annotation"]["lexical"]
    assert SURFACE_CHANNEL_WEIGHTS["unit_understanding"]["lexical"] > SURFACE_CHANNEL_WEIGHTS["unit_response"]["lexical"]


def test_text_only_retrieval_prefers_understanding_match_over_source_only_match(tmp_path):
    config = {
        "mode": "text_only",
        "min_retrievable_prior_units": 0,
        "recent_neighbor_exclusion_unit_count": 0,
        "max_units_to_digest_context": 2,
    }
    index = UnitMemoryIndex(tmp_path, config=config)
    index.write_entry(
        _entry("u000001", 1, "铺垫文字之后出现共同短语", "这个单元的理解与目标概念无关。"),
        index_vectors=False,
    )
    index.write_entry(
        _entry("u000002", 2, "另一个场景", "共同短语标记的理解内容应该优先成为长期记忆召回结果。"),
        index_vectors=False,
    )

    result = index.retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "共同短语", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=3,
    )

    assert result["selected_units"][0]["unit_id"] == "u000002"
    assert result["selected_units"][0]["best_docs"][0]["surface"] == "unit_understanding"


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
