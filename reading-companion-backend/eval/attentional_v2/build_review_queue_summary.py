"""Build a machine-readable summary of active dataset-review packets."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .case_audit_runs import latest_case_audit_run, load_json

ROOT = Path(__file__).resolve().parents[2]
PENDING_ROOT = ROOT / "eval" / "review_packets" / "pending"
RUNS_ROOT = ROOT / "eval" / "runs" / "attentional_v2" / "case_audits"
OUTPUT_JSON = ROOT / "eval" / "review_packets" / "review_queue_summary.json"
OUTPUT_MD = ROOT / "eval" / "review_packets" / "review_queue_summary.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_summary() -> dict[str, Any]:
    packets: list[dict[str, Any]] = []
    for packet_dir in sorted(PENDING_ROOT.iterdir()):
        if not packet_dir.is_dir():
            continue
        manifest_path = packet_dir / "packet_manifest.json"
        if not manifest_path.exists():
            continue
        manifest = load_json(manifest_path)
        packet_id = str(manifest.get("packet_id", packet_dir.name))
        packets.append(
            {
                "packet_id": packet_id,
                "packet_dir": str(packet_dir),
                "created_at": str(manifest.get("created_at", "")),
                "dataset_id": str(manifest.get("dataset_id", "")),
                "family": str(manifest.get("family", "")),
                "storage_mode": str(manifest.get("storage_mode", "")),
                "case_count": int(manifest.get("case_count", 0) or 0),
                "selection_filters": dict(manifest.get("selection_filters", {})),
                "latest_case_audit": latest_case_audit_run(packet_id, RUNS_ROOT, require_completed=False),
                "latest_completed_case_audit": latest_case_audit_run(packet_id, RUNS_ROOT, require_completed=True),
            }
        )
    return {
        "generated_at": utc_now(),
        "active_packet_count": len(packets),
        "packets": packets,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Review Queue Summary",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        f"Active packets: `{summary['active_packet_count']}`",
        "",
    ]
    for packet in summary["packets"]:
        lines.extend(
            [
                f"## {packet['packet_id']}",
                "",
                f"- dataset: `{packet['dataset_id']}`",
                f"- storage_mode: `{packet['storage_mode']}`",
                f"- case_count: `{packet['case_count']}`",
                f"- created_at: `{packet['created_at']}`",
            ]
        )
        audit = packet.get("latest_case_audit")
        if isinstance(audit, dict) and audit:
            progress = audit.get("progress", {})
            lines.extend(
                [
                    f"- latest_case_audit: `{audit.get('run_id', '')}`",
                    f"- audit_status: `{audit.get('status', '')}`",
                    f"- audit_progress: `{json.dumps(progress, ensure_ascii=False, sort_keys=True)}`",
                ]
            )
            aggregate = audit.get("aggregate", {})
            if aggregate:
                lines.extend(
                    [
                        f"- audit_primary_decisions: `{json.dumps(aggregate.get('primary_decisions', {}), ensure_ascii=False, sort_keys=True)}`",
                        f"- audit_risk_counts: `{json.dumps(aggregate.get('adversarial_risk_counts', {}), ensure_ascii=False, sort_keys=True)}`",
                        f"- audit_excerpt_strength: `{aggregate.get('average_excerpt_strength', '')}`",
                    ]
                )
        completed_audit = packet.get("latest_completed_case_audit")
        if isinstance(completed_audit, dict) and completed_audit and completed_audit.get("run_id") != (audit or {}).get("run_id"):
            aggregate = completed_audit.get("aggregate", {})
            lines.extend(
                [
                    f"- latest_completed_case_audit: `{completed_audit.get('run_id', '')}`",
                    f"- completed_audit_primary_decisions: `{json.dumps(aggregate.get('primary_decisions', {}), ensure_ascii=False, sort_keys=True)}`",
                    f"- completed_audit_risk_counts: `{json.dumps(aggregate.get('adversarial_risk_counts', {}), ensure_ascii=False, sort_keys=True)}`",
                    f"- completed_audit_excerpt_strength: `{aggregate.get('average_excerpt_strength', '')}`",
                ]
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    summary = build_summary()
    OUTPUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(summary) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "active_packet_count": summary["active_packet_count"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
