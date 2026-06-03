from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "reading-companion-backend/eval/manifests/attentional_v2_minimal_eval_inventory_v1.json"
SMOKE_SCRIPT_PATH = REPO_ROOT / "reading-companion-backend/scripts/validate_minimal_eval_inventory_smoke.py"

REQUIRED_LANES = {
    "lane_a_local_user_level_selective_legibility",
    "lane_b_long_span_unit_memory_safety",
}
REQUIRED_EVIDENCE_SURFACES = {
    "read_audit",
    "settlement_audit",
    "ingest_trace",
    "slow_cycle_audit",
    "source_ref_binding_resolution_markers",
    "projection_markers",
    "memory_uptake_admission_outcome_fields",
}
REQUIRED_GUARDS = {
    "retrieval_availability_is_not_utilization_success",
    "visible_reaction_presence_is_not_prior_memory_grounding",
    "source_ref_count_is_not_fidelity_score",
    "trace_existence_is_not_planning_quality",
    "slow_cycle_audit_existence_is_not_slow_cycle_quality",
}


def _load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _walk_mappings(value: object) -> Iterator[Mapping[str, object]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_mappings(item)


def _path_refs(manifest: Mapping[str, object]) -> Iterator[Mapping[str, object]]:
    for mapping in _walk_mappings(manifest):
        if "workspace_path" in mapping:
            yield mapping


def _run_smoke(manifest_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SMOKE_SCRIPT_PATH),
            "--manifest",
            str(manifest_path),
        ],
        cwd=REPO_ROOT / "reading-companion-backend",
        check=False,
        text=True,
        capture_output=True,
    )


def test_minimal_eval_inventory_preserves_two_active_lanes() -> None:
    manifest = _load_manifest()

    assert manifest["manifest_id"] == "attentional_v2_minimal_eval_inventory_v1"
    assert manifest["schema_version"] == 1
    assert manifest["status"] == "active_inventory"
    assert manifest["purpose"] == "minimal_eval_asset_inventory_and_evidence_wiring"

    lanes = manifest["active_lanes"]
    assert isinstance(lanes, list)
    lane_ids = {lane["id"] for lane in lanes}
    assert lane_ids == REQUIRED_LANES

    historical_ids = {item["id"] for item in manifest["historical_assets"]}
    assert historical_ids.isdisjoint(lane_ids)
    assert all(item["not_active_lane"] is True for item in manifest["historical_assets"])


def test_lane_a_distinguishes_active_dataset_from_formal_evidence_dataset() -> None:
    manifest = _load_manifest()
    lane_a = next(lane for lane in manifest["active_lanes"] if lane["id"] == "lane_a_local_user_level_selective_legibility")

    assert lane_a["status"] == "active_benchmark_lane"
    assert lane_a["formal_authority"] is True
    assert lane_a["active_dataset_pointer"]["dataset_id"] == "attentional_v2_user_level_selective_v1_repaired_20260422"
    assert "20260422" in lane_a["active_dataset_pointer"]["workspace_path"]

    formal_evidence = lane_a["current_formal_evidence"]
    assert formal_evidence["run_id"] == "attentional_v2_user_level_selective_v1_active_rerun_20260419"
    assert formal_evidence["formal_evidence_dataset_id"] == "attentional_v2_user_level_selective_v1_repaired_20260416"
    assert "20260416" in formal_evidence["formal_evidence_dataset_boundary"]["workspace_path"]
    assert formal_evidence["formal_evidence_dataset_boundary"]["workspace_path"] != lane_a["active_dataset_pointer"]["workspace_path"]


def test_lane_b_remains_diagnostic_not_formal_authority() -> None:
    manifest = _load_manifest()
    lane_b = next(lane for lane in manifest["active_lanes"] if lane["id"] == "lane_b_long_span_unit_memory_safety")

    assert lane_b["status"] == "diagnostic_phase_1"
    assert lane_b["formal_authority"] is False
    assert set(lane_b["dimensions"]) == {
        "memory_quality",
        "prior_memory_continuity_safety",
        "prior_memory_overclaim_guardrail",
    }
    assert lane_b["current_diagnostic_evidence"]["run_id"] == (
        "attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425"
    )


def test_required_evidence_surfaces_are_mapped() -> None:
    manifest = _load_manifest()

    evidence_surfaces = {item["id"]: item for item in manifest["evidence_surfaces"]}
    assert set(evidence_surfaces) == REQUIRED_EVIDENCE_SURFACES

    valid_targets = REQUIRED_LANES | {item["id"] for item in manifest["diagnostic_additions"]}
    for surface in evidence_surfaces.values():
        assert surface["maps_to"]
        assert set(surface["maps_to"]).issubset(valid_targets)

    lane_surface_ids = {
        surface_id
        for lane in manifest["active_lanes"]
        for surface_id in lane["evidence_surface_ids"]
    }
    assert REQUIRED_EVIDENCE_SURFACES.issuperset(lane_surface_ids)


def test_path_references_are_explicitly_tracked_or_local_only() -> None:
    manifest = _load_manifest()

    for ref in _path_refs(manifest):
        workspace_path = ref["workspace_path"]
        path_status = ref["path_status"]
        assert isinstance(workspace_path, str)
        assert not workspace_path.startswith("/")
        assert path_status in {"tracked", "local_only"}

        path = REPO_ROOT / workspace_path
        if path_status == "tracked":
            assert path.exists(), workspace_path
        elif path.exists() and path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))


def test_interpretation_guards_and_diagnostics_are_non_scoring() -> None:
    manifest = _load_manifest()

    guards = manifest["interpretation_guards"]
    assert REQUIRED_GUARDS.issubset(guards)
    assert all(guards[key] is True for key in REQUIRED_GUARDS)

    diagnostics = {item["id"]: item for item in manifest["diagnostic_additions"]}
    assert set(diagnostics) == {"planning_trace_quality", "slow_cycle_safety"}
    for diagnostic in diagnostics.values():
        assert diagnostic["diagnostic_only"] is True
        assert diagnostic["quality_score"] is False
        assert diagnostic["evidence_availability_only"] is True

    assert manifest["future_smoke_proposal"]["execute_in_slice_7a"] is False


def test_minimal_eval_inventory_smoke_validator_accepts_committed_manifest() -> None:
    result = _run_smoke(MANIFEST_PATH)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""

    summary = json.loads(result.stdout)
    assert summary["status"] == "ok"
    assert set(summary["lane_ids"]) == REQUIRED_LANES
    assert set(summary["evidence_surface_ids"]) == REQUIRED_EVIDENCE_SURFACES
    assert set(summary["diagnostic_ids"]) == {"planning_trace_quality", "slow_cycle_safety"}
    assert summary["tracked_path_count"] > 0
    assert summary["local_only_missing_count"] >= 0
    assert summary["local_only_present_count"] >= 0


def test_minimal_eval_inventory_smoke_validator_rejects_false_guard(tmp_path: Path) -> None:
    manifest = _load_manifest()
    manifest["interpretation_guards"]["source_ref_count_is_not_fidelity_score"] = False
    manifest_path = tmp_path / "manifest_with_false_guard.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = _run_smoke(manifest_path)

    assert result.returncode != 0
    assert result.stdout == ""

    failure = json.loads(result.stderr)
    assert failure["status"] == "failed"
    assert any("source_ref_count_is_not_fidelity_score" in error for error in failure["errors"])
