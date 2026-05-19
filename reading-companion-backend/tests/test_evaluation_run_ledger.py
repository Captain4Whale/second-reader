import json
from pathlib import Path

from scripts.update_evaluation_run_ledger import (
    build_entry,
    scan_runs,
    upsert_ledger_entry,
    validate_ledger,
    write_markdown_ledger,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _make_run(tmp_path: Path, run_id: str = "attentional_v2_user_level_selective_v1_20260519") -> Path:
    run_dir = tmp_path / "runs" / run_id
    _write_json(
        run_dir / "summary" / "aggregate.json",
        {
            "run_id": run_id,
            "mechanisms": {"attentional_v2": {"note_recall": 0.5}},
            "note_case_count": 2,
        },
    )
    (run_dir / "summary" / "report.md").write_text("# report\n", encoding="utf-8")
    (run_dir / "summary" / "llm_usage.json").write_text("{}\n", encoding="utf-8")
    return run_dir


def test_upsert_and_render_run_ledger(tmp_path: Path) -> None:
    run_dir = _make_run(tmp_path)
    ledger_json = tmp_path / "run_ledger.json"
    ledger_md = tmp_path / "run_ledger.md"
    catalog_json = tmp_path / "evidence_catalog.json"
    _write_json(catalog_json, {"entries": []})

    entry = build_entry(
        run_id=run_dir.name,
        surface="user_level_selective_v1",
        lane="local_user_level_selective",
        status="review_pending",
        run_dir=run_dir,
        catalog_status="review_pending",
        notes="Pending human review.",
    )
    ledger = upsert_ledger_entry(entry, ledger_json_path=ledger_json)
    text = write_markdown_ledger(ledger, ledger_md_path=ledger_md)

    assert validate_ledger(ledger_json_path=ledger_json, catalog_json_path=catalog_json) == []
    assert run_dir.name in text
    assert "aggregate" in text
    assert "Pending human review." in text


def test_check_rejects_missing_artifact_unless_allowed(tmp_path: Path) -> None:
    ledger_json = tmp_path / "run_ledger.json"
    catalog_json = tmp_path / "evidence_catalog.json"
    _write_json(catalog_json, {"entries": []})

    missing_path = str(tmp_path / "missing" / "aggregate.json")
    entry = build_entry(
        run_id="missing_run_20260519",
        surface="user_level_selective_v1",
        lane="local_user_level_selective",
        status="failed",
        run_dir=tmp_path / "missing",
        summary_paths={"aggregate": missing_path},
        catalog_status="not_cataloged",
        notes="Failed before summary.",
        local_missing_allowed=[],
    )
    upsert_ledger_entry(entry, ledger_json_path=ledger_json)
    errors = validate_ledger(ledger_json_path=ledger_json, catalog_json_path=catalog_json)
    assert any("missing run_dir path" in item for item in errors)
    assert any("missing summary_paths.aggregate path" in item for item in errors)

    entry["local_missing_allowed"] = [entry["run_dir"], entry["summary_paths"]["aggregate"]]
    upsert_ledger_entry(entry, ledger_json_path=ledger_json)
    assert validate_ledger(ledger_json_path=ledger_json, catalog_json_path=catalog_json) == []


def test_cataloged_entry_must_exist_in_catalog_or_be_synthetic(tmp_path: Path) -> None:
    run_dir = _make_run(tmp_path, run_id="cataloged_run_20260519")
    ledger_json = tmp_path / "run_ledger.json"
    catalog_json = tmp_path / "evidence_catalog.json"
    _write_json(catalog_json, {"entries": []})

    entry = build_entry(
        run_id=run_dir.name,
        surface="user_level_selective_v1",
        lane="local_user_level_selective",
        status="cataloged",
        run_dir=run_dir,
        catalog_status="current_formal_evidence",
        notes="Cataloged evidence.",
    )
    upsert_ledger_entry(entry, ledger_json_path=ledger_json)
    errors = validate_ledger(ledger_json_path=ledger_json, catalog_json_path=catalog_json)
    assert any("run_id not found in evidence catalog" in item for item in errors)

    _write_json(catalog_json, {"entries": [{"run_id": run_dir.name}]})
    assert validate_ledger(ledger_json_path=ledger_json, catalog_json_path=catalog_json) == []


def test_scan_discovers_runs_without_writing(tmp_path: Path) -> None:
    run_dir = _make_run(tmp_path, run_id="attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_demo")

    entries = scan_runs(runs_root=run_dir.parent)

    assert [entry["run_id"] for entry in entries] == [run_dir.name]
    assert entries[0]["surface"] == "user_level_selective_v1"
    assert entries[0]["status"] == "uncataloged_local_artifact"
