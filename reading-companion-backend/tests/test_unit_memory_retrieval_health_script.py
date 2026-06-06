import importlib.util
import json
from pathlib import Path

from src.attentional_v2.storage import unit_memory_retrieval_trace_file
from src.attentional_v2.unit_memory import UnitMemoryIndex, build_unit_memory_entry, resolve_memory_retrieval_config


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "diagnose_unit_memory_retrieval_health.py"
SPEC = importlib.util.spec_from_file_location("diagnose_unit_memory_retrieval_health", SCRIPT_PATH)
health_script = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(health_script)


def _source_unit(unit_id: str, sequence_index: int, text: str) -> dict[str, object]:
    return {
        "unit_id": unit_id,
        "sequence_index": sequence_index,
        "source_span_id": f"src:c1:p{sequence_index}@0-p{sequence_index}@{len(text)}",
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


def _digest_result(understanding: str) -> dict[str, object]:
    ops = []
    if understanding:
        ops.append(
            {
                "op": "append",
                "target_store": "recent_reading_memory",
                "payload": {"memory_text": understanding},
            }
        )
    return {
        "reading_impression": "quiet response",
        "surfaced_reactions": [],
        "memory_uptake_ops": ops,
    }


def _write_entry(output_dir: Path, unit_id: str, sequence_index: int, text: str, understanding: str) -> None:
    entry = build_unit_memory_entry(
        book_id="book-demo",
        chapter_id=1,
        chapter_ref="Chapter 1",
        source_unit=_source_unit(unit_id, sequence_index, text),
        digest_result=_digest_result(understanding),
        memory_retrieval_mode="text_only",
    )
    UnitMemoryIndex(
        output_dir,
        config={
            "mode": "text_only",
            "recent_neighbor_exclusion_unit_count": 0,
            "min_retrievable_prior_units": 0,
        },
    ).write_entry(entry, index_vectors=False)


def test_health_script_reports_non_renderable_retrieval_candidate(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs" / "demo_segment" / "attentional_v2"
    config = resolve_memory_retrieval_config(output_dir, {"memory_retrieval_mode": "text_only"})
    _write_entry(output_dir, "u000001", 1, "火车站台上的告别", "")

    retrieval = UnitMemoryIndex(output_dir, config={**config, "min_retrievable_prior_units": 0, "recent_neighbor_exclusion_unit_count": 0}).retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "火车站台 告别", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=2,
    )
    assert not retrieval["selected_units"]
    assert retrieval["trace"]["suppressed_units"][0]["reason"] == "candidate_not_renderable_empty_understanding"
    unit_memory_retrieval_trace_file(output_dir).write_text(
        unit_memory_retrieval_trace_file(output_dir).read_text(encoding="utf-8")
        + json.dumps(
            {
                "event_type": "unit_memory_reading_memory_selection",
                "line_count": 0,
                "hot_line_count": 0,
                "retrieved_line_count": 0,
                "suppressed": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    summary = health_script.summarize_paths([tmp_path])

    assert summary["status"] == "needs_repair"
    assert summary["total"]["selected_unit_count"] == 0
    assert summary["total"]["renderable_selected_unit_count"] == 0
    assert summary["total"]["non_renderable_selected_unit_count"] == 0
    assert summary["total"]["retrieval_suppressed_unit_count"] == 1
    assert summary["total"]["retrieved_line_total"] == 0
    output = summary["outputs"][0]
    assert output["trace"]["retrieval_suppressed_reasons"] == {"candidate_not_renderable_empty_understanding": 1}


def test_health_script_reports_rendered_retrieved_unit_ids(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs" / "demo_segment" / "attentional_v2"
    config = resolve_memory_retrieval_config(output_dir, {"memory_retrieval_mode": "text_only"})
    _write_entry(output_dir, "u000001", 1, "火车站台上的告别", "站台告别建立了旅程起点。")
    UnitMemoryIndex(output_dir, config=config).retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "火车站台 告别", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=2,
        excluded_source_unit_span_ids={"src:c1:p99@0-p99@8"},
    )
    unit_memory_retrieval_trace_file(output_dir).write_text(
        unit_memory_retrieval_trace_file(output_dir).read_text(encoding="utf-8")
        + json.dumps(
            {
                "event_type": "unit_memory_reading_memory_selection",
                "line_count": 1,
                "hot_line_count": 0,
                "retrieved_line_count": 1,
                "rendered_retrieved_units": [
                    {
                        "unit_id": "u000001",
                        "source_span_id": "src:c1:p1@0-p1@8",
                        "unit_index": 1,
                        "matched_recalls": ["r1"],
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    summary = health_script.summarize_paths([tmp_path])

    assert summary["total"]["rendered_retrieved_unique_unit_count"] == 1
    assert summary["total"]["excluded_source_unit_span_total"] == 1
    assert summary["total"]["retrieval_rows_with_excluded_source_unit_spans"] == 1
    assert summary["total"]["max_excluded_source_unit_span_count"] == 1
    output = summary["outputs"][0]
    assert output["trace"]["excluded_source_unit_span_total"] == 1
    assert output["reading_memory"]["rendered_retrieved_unit_ids"] == ["u000001"]


def test_health_script_discovers_output_dir_from_nested_runtime_path(tmp_path: Path) -> None:
    output_dir = tmp_path / "custom_root" / "demo_segment" / "attentional_v2"
    config = resolve_memory_retrieval_config(output_dir, {"memory_retrieval_mode": "text_only"})
    _write_entry(output_dir, "u000001", 1, "火车站台上的告别", "站台告别建立了旅程起点。")
    UnitMemoryIndex(output_dir, config=config).retrieve_for_recalls(
        book_id="book-demo",
        recalls=[{"recall_id": "r1", "recall_text": "火车站台 告别", "basis": "selected_source_unit"}],
        query_source="tool_retrieve_unit_memory",
        current_unit_index=2,
    )

    discovered = health_script._discover_output_dirs(tmp_path / "custom_root")

    assert discovered == [output_dir]
