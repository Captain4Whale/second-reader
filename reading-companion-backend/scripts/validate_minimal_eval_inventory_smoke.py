#!/usr/bin/env python3
"""Validate the attentional_v2 minimal eval inventory without running eval."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_MANIFEST = {
    "manifest_id": "attentional_v2_minimal_eval_inventory_v1",
    "schema_version": 1,
    "status": "active_inventory",
    "purpose": "minimal_eval_asset_inventory_and_evidence_wiring",
}
REQUIRED_LANES = {
    "lane_a_local_user_level_selective_legibility",
    "lane_b_long_span_mq_callback_fvi",
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
REQUIRED_DIAGNOSTICS = {
    "planning_trace_quality",
    "slow_cycle_safety",
}
REQUIRED_GUARDS = {
    "retrieval_availability_is_not_utilization_success",
    "visible_reaction_presence_is_not_callback_correctness",
    "source_ref_count_is_not_fidelity_score",
    "trace_existence_is_not_planning_quality",
    "slow_cycle_audit_existence_is_not_slow_cycle_quality",
    "contract_audit_checks_are_not_product_quality_scores",
}
EXPECTED_ARTIFACT_TOKENS = {
    "read_audit": ("read_audit.jsonl",),
    "settlement_audit": ("settlement_audit.jsonl",),
    "ingest_trace": ("read_audit.ingest_trace",),
    "slow_cycle_audit": ("slow_cycle_audit.jsonl",),
    "source_ref_binding_resolution_markers": ("source_refs", "SourceRef"),
    "projection_markers": ("projection_role", "support_status", "lineage_only", "current_support", "visible_trace_support"),
    "memory_uptake_admission_outcome_fields": ("memory_uptake_admission_events", "memory_uptake_op_outcomes"),
}


def _load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("manifest root must be a JSON object")
    return payload


def _walk_mappings(value: Any) -> Iterator[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_mappings(item)


def _path_refs(manifest: Mapping[str, Any]) -> Iterator[Mapping[str, Any]]:
    for mapping in _walk_mappings(manifest):
        if "workspace_path" in mapping:
            yield mapping


def _ids(items: Any, *, field_name: str, errors: list[str]) -> set[str]:
    if not isinstance(items, list):
        errors.append(f"{field_name} must be a list")
        return set()
    ids: set[str] = set()
    for item in items:
        if not isinstance(item, Mapping):
            errors.append(f"{field_name} entries must be objects")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{field_name} entries must include non-empty string id")
            continue
        ids.add(item_id)
    return ids


def validate_manifest(manifest: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []

    for key, expected in EXPECTED_MANIFEST.items():
        if manifest.get(key) != expected:
            errors.append(f"{key} must be {expected!r}")

    lane_ids = _ids(manifest.get("active_lanes"), field_name="active_lanes", errors=errors)
    if lane_ids != REQUIRED_LANES:
        errors.append(f"active_lanes must be exactly {sorted(REQUIRED_LANES)}")

    historical_ids = _ids(manifest.get("historical_assets"), field_name="historical_assets", errors=errors)
    if lane_ids & historical_ids:
        errors.append("historical_assets must not be promoted into active_lanes")
    for item in manifest.get("historical_assets", []):
        if isinstance(item, Mapping) and item.get("not_active_lane") is not True:
            errors.append(f"historical asset {item.get('id')!r} must set not_active_lane=true")

    diagnostics = manifest.get("diagnostic_additions")
    diagnostic_ids = _ids(diagnostics, field_name="diagnostic_additions", errors=errors)
    if diagnostic_ids != REQUIRED_DIAGNOSTICS:
        errors.append(f"diagnostic_additions must be exactly {sorted(REQUIRED_DIAGNOSTICS)}")
    if isinstance(diagnostics, list):
        for item in diagnostics:
            if not isinstance(item, Mapping):
                continue
            diagnostic_id = item.get("id")
            if item.get("diagnostic_only") is not True:
                errors.append(f"diagnostic {diagnostic_id!r} must set diagnostic_only=true")
            if item.get("quality_score") is not False:
                errors.append(f"diagnostic {diagnostic_id!r} must set quality_score=false")
            if item.get("evidence_availability_only") is not True:
                errors.append(f"diagnostic {diagnostic_id!r} must set evidence_availability_only=true")

    surfaces = manifest.get("evidence_surfaces")
    evidence_surface_ids = _ids(surfaces, field_name="evidence_surfaces", errors=errors)
    if evidence_surface_ids != REQUIRED_EVIDENCE_SURFACES:
        errors.append(f"evidence_surfaces must be exactly {sorted(REQUIRED_EVIDENCE_SURFACES)}")
    valid_targets = REQUIRED_LANES | REQUIRED_DIAGNOSTICS
    if isinstance(surfaces, list):
        for item in surfaces:
            if not isinstance(item, Mapping):
                continue
            surface_id = item.get("id")
            artifact_or_field = item.get("artifact_or_field")
            if isinstance(surface_id, str):
                expected_tokens = EXPECTED_ARTIFACT_TOKENS.get(surface_id, ())
                if not isinstance(artifact_or_field, str):
                    errors.append(f"surface {surface_id!r} must include artifact_or_field")
                else:
                    missing_tokens = [token for token in expected_tokens if token not in artifact_or_field]
                    if missing_tokens:
                        errors.append(f"surface {surface_id!r} artifact_or_field missing tokens: {missing_tokens}")
            maps_to = item.get("maps_to")
            if not isinstance(maps_to, list) or not maps_to:
                errors.append(f"surface {surface_id!r} must map to at least one lane or diagnostic")
            elif not set(maps_to).issubset(valid_targets):
                errors.append(f"surface {surface_id!r} maps_to contains unsupported target")

    guards = manifest.get("interpretation_guards")
    if not isinstance(guards, Mapping):
        errors.append("interpretation_guards must be an object")
    else:
        for guard_id in sorted(REQUIRED_GUARDS):
            if guards.get(guard_id) is not True:
                errors.append(f"interpretation guard {guard_id!r} must be present and true")

    tracked_path_count = 0
    local_only_present_count = 0
    local_only_missing_count = 0
    for ref in _path_refs(manifest):
        workspace_path = ref.get("workspace_path")
        path_status = ref.get("path_status")
        if not isinstance(workspace_path, str) or not workspace_path:
            errors.append("workspace_path entries must be non-empty strings")
            continue
        if workspace_path.startswith("/"):
            errors.append(f"workspace_path must be repo-relative: {workspace_path}")
            continue
        if path_status not in {"tracked", "local_only"}:
            errors.append(f"workspace_path {workspace_path!r} must set path_status tracked or local_only")
            continue
        path = REPO_ROOT / workspace_path
        if path_status == "tracked":
            tracked_path_count += 1
            if not path.exists():
                errors.append(f"tracked workspace_path does not exist: {workspace_path}")
        else:
            if path.exists():
                local_only_present_count += 1
            else:
                local_only_missing_count += 1

    summary = {
        "status": "ok" if not errors else "failed",
        "manifest_id": manifest.get("manifest_id"),
        "lane_ids": sorted(lane_ids),
        "evidence_surface_ids": sorted(evidence_surface_ids),
        "tracked_path_count": tracked_path_count,
        "local_only_present_count": local_only_present_count,
        "local_only_missing_count": local_only_missing_count,
        "diagnostic_ids": sorted(diagnostic_ids),
    }
    return summary, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Path to the minimal eval inventory manifest.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    try:
        manifest = _load_manifest(manifest_path)
        summary, errors = validate_manifest(manifest)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        payload = {"status": "failed", "errors": [str(exc)]}
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1

    if errors:
        summary["errors"] = errors
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
