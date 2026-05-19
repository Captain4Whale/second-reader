#!/usr/bin/env python3
"""Maintain the evaluation run ledger.

The run ledger is an operational index: it answers when an eval was run, what
status it reached, and where its artifacts/reports live. It is intentionally
broader than the evidence catalog, which only indexes reviewed evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = BACKEND_ROOT.parent
DEFAULT_LEDGER_JSON = BACKEND_ROOT / "docs" / "evaluation" / "run_ledger.json"
DEFAULT_LEDGER_MD = BACKEND_ROOT / "docs" / "evaluation" / "run_ledger.md"
DEFAULT_CATALOG_JSON = BACKEND_ROOT / "docs" / "evaluation" / "evidence_catalog.json"
RUNS_ROOT = BACKEND_ROOT / "eval" / "runs" / "attentional_v2"
SCHEMA_VERSION = 1

ALLOWED_STATUSES = {
    "planned",
    "running",
    "completed",
    "review_pending",
    "cataloged",
    "failed",
    "abandoned",
    "invalidated",
    "superseded",
    "historical",
    "uncataloged_local_artifact",
}

NON_CATALOG_STATUSES = {"", "not_cataloged", "review_pending", "none", "n/a"}

REQUIRED_FIELDS = {
    "run_id",
    "date",
    "surface",
    "lane",
    "status",
    "mechanisms",
    "dataset_or_manifest",
    "run_dir",
    "summary_paths",
    "job_ids",
    "report_paths",
    "catalog_status",
    "notes",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "updated_at": utc_now(), "entries": []}
    payload = _json_load(path)
    if not isinstance(payload, dict):
        raise ValueError(f"ledger must be a JSON object: {path}")
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("updated_at", utc_now())
    payload.setdefault("entries", [])
    if not isinstance(payload["entries"], list):
        raise ValueError(f"ledger entries must be a list: {path}")
    return payload


def _resolve_path(path: str | Path | None) -> Path:
    raw = str(path or "").strip()
    if not raw:
        return Path("")
    value = Path(raw).expanduser()
    if value.is_absolute():
        return value
    if raw == BACKEND_ROOT.name or raw.startswith(f"{BACKEND_ROOT.name}/"):
        return (WORKSPACE_ROOT / value).resolve()
    if raw == "docs" or raw.startswith("docs/"):
        return (WORKSPACE_ROOT / value).resolve()
    return (BACKEND_ROOT / value).resolve()


def _path_exists(path: str | Path | None) -> bool:
    raw = str(path or "").strip()
    return bool(raw) and _resolve_path(raw).exists()


def _rel_workspace_path(path: str | Path | None) -> str:
    raw = str(path or "").strip()
    if not raw:
        return ""
    value = _resolve_path(raw)
    try:
        return str(value.relative_to(WORKSPACE_ROOT)).replace(os.sep, "/")
    except ValueError:
        return str(value).replace(os.sep, "/")


def _rel_backend_path(path: str | Path | None) -> str:
    raw = str(path or "").strip()
    if not raw:
        return ""
    value = _resolve_path(raw)
    try:
        return str(value.relative_to(BACKEND_ROOT)).replace(os.sep, "/")
    except ValueError:
        return _rel_workspace_path(value)


def _infer_date_from_run_id(run_id: str) -> str:
    match = re.search(r"(20\d{6})", run_id)
    if not match:
        return ""
    value = match.group(1)
    return f"{value[:4]}-{value[4:6]}-{value[6:8]}"


def _maybe_load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = _json_load(path)
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _infer_mechanisms(aggregate: dict[str, Any]) -> list[str]:
    mechanisms = aggregate.get("mechanisms")
    if isinstance(mechanisms, dict):
        return sorted(str(key) for key in mechanisms.keys())
    mechanism_keys = aggregate.get("mechanism_keys")
    if isinstance(mechanism_keys, list):
        return sorted(str(item) for item in mechanism_keys)
    if "excerpt" in aggregate and "accumulation" in aggregate:
        return ["attentional_v2", "iterator_v1"]
    return []


def _summary_paths_from_run_dir(run_dir: str | Path | None) -> dict[str, str]:
    raw = str(run_dir or "").strip()
    if not raw:
        return {}
    resolved = _resolve_path(raw)
    summary = resolved / "summary"
    paths: dict[str, str] = {}
    for key, filename in (
        ("aggregate", "aggregate.json"),
        ("report", "report.md"),
        ("llm_usage", "llm_usage.json"),
        ("case_results", "case_results.jsonl"),
        ("memory_quality_results", "memory_quality_results.jsonl"),
        ("reaction_audit_results", "reaction_audit_results.jsonl"),
        ("reaction_window_summaries", "reaction_window_summaries.jsonl"),
    ):
        path = summary / filename
        if path.exists():
            paths[key] = _rel_workspace_path(path)
    return paths


def _parse_key_value(values: list[str] | None) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in values or []:
        if "=" not in item:
            raise ValueError(f"expected KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"empty key in {item!r}")
        try:
            parsed[key] = json.loads(value)
        except json.JSONDecodeError:
            parsed[key] = value
    return parsed


def _as_sorted_unique(values: list[str] | None) -> list[str]:
    return sorted(dict.fromkeys(str(item).strip() for item in values or [] if str(item).strip()))


def build_entry(
    *,
    run_id: str,
    date: str | None = None,
    surface: str,
    lane: str,
    status: str,
    mechanisms: list[str] | None = None,
    dataset_or_manifest: list[str] | None = None,
    run_dir: str | Path | None = None,
    summary_paths: dict[str, str] | None = None,
    job_ids: list[str] | None = None,
    report_paths: list[str] | None = None,
    catalog_status: str = "not_cataloged",
    notes: str = "",
    parent_run_id: str = "",
    child_run_ids: list[str] | None = None,
    synthetic: bool = False,
    local_missing_allowed: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"unsupported ledger status: {status}")
    inferred_summary_paths = _summary_paths_from_run_dir(run_dir)
    inferred_summary_paths.update(summary_paths or {})
    aggregate_path = inferred_summary_paths.get("aggregate")
    aggregate = _maybe_load_json(_resolve_path(aggregate_path)) if aggregate_path else {}
    inferred_mechanisms = mechanisms or _infer_mechanisms(aggregate)
    entry = {
        "run_id": run_id,
        "date": date or _infer_date_from_run_id(run_id),
        "surface": surface,
        "lane": lane,
        "status": status,
        "mechanisms": _as_sorted_unique(inferred_mechanisms),
        "dataset_or_manifest": _as_sorted_unique(dataset_or_manifest),
        "run_dir": _rel_workspace_path(run_dir),
        "summary_paths": {str(key): _rel_workspace_path(value) for key, value in sorted(inferred_summary_paths.items())},
        "job_ids": _as_sorted_unique(job_ids),
        "report_paths": [_rel_workspace_path(path) for path in report_paths or [] if str(path).strip()],
        "catalog_status": catalog_status,
        "notes": notes,
        "parent_run_id": parent_run_id,
        "child_run_ids": _as_sorted_unique(child_run_ids),
        "synthetic": bool(synthetic),
        "local_missing_allowed": [_rel_workspace_path(path) for path in local_missing_allowed or []],
        "metadata": metadata or {},
        "updated_at": utc_now(),
    }
    return entry


def upsert_ledger_entry(
    entry: dict[str, Any],
    *,
    ledger_json_path: Path = DEFAULT_LEDGER_JSON,
) -> dict[str, Any]:
    ledger = _read_ledger(ledger_json_path)
    entries = [existing for existing in ledger["entries"] if existing.get("run_id") != entry.get("run_id")]
    entries.append(entry)
    entries.sort(key=lambda item: (str(item.get("date", "")), str(item.get("run_id", ""))))
    ledger["entries"] = entries
    ledger["updated_at"] = utc_now()
    _json_dump(ledger_json_path, ledger)
    return ledger


def _catalog_run_ids(catalog_json_path: Path = DEFAULT_CATALOG_JSON) -> set[str]:
    if not catalog_json_path.exists():
        return set()
    payload = _json_load(catalog_json_path)
    entries = payload.get("entries") if isinstance(payload, dict) else []
    return {str(entry.get("run_id")) for entry in entries if isinstance(entry, dict) and entry.get("run_id")}


def _iter_paths(entry: dict[str, Any]) -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    if entry.get("run_dir"):
        paths.append(("run_dir", str(entry["run_dir"])))
    summary_paths = entry.get("summary_paths")
    if isinstance(summary_paths, dict):
        for key, value in summary_paths.items():
            if value:
                paths.append((f"summary_paths.{key}", str(value)))
    report_paths = entry.get("report_paths")
    if isinstance(report_paths, list):
        for index, value in enumerate(report_paths, 1):
            if value:
                paths.append((f"report_paths.{index}", str(value)))
    dataset_or_manifest = entry.get("dataset_or_manifest")
    if isinstance(dataset_or_manifest, list):
        for index, value in enumerate(dataset_or_manifest, 1):
            if value:
                paths.append((f"dataset_or_manifest.{index}", str(value)))
    return paths


def validate_ledger(
    *,
    ledger_json_path: Path = DEFAULT_LEDGER_JSON,
    catalog_json_path: Path = DEFAULT_CATALOG_JSON,
) -> list[str]:
    ledger = _read_ledger(ledger_json_path)
    errors: list[str] = []
    seen: set[str] = set()
    run_ids = {str(entry.get("run_id")) for entry in ledger.get("entries") or [] if isinstance(entry, dict)}
    catalog_run_ids = _catalog_run_ids(catalog_json_path)
    for index, entry in enumerate(ledger.get("entries") or [], 1):
        if not isinstance(entry, dict):
            errors.append(f"entry {index}: must be an object")
            continue
        missing_fields = sorted(REQUIRED_FIELDS - set(entry))
        if missing_fields:
            errors.append(f"entry {index}: missing required fields {', '.join(missing_fields)}")
        run_id = str(entry.get("run_id") or "")
        if not run_id:
            errors.append(f"entry {index}: missing run_id")
        if run_id in seen:
            errors.append(f"entry {index}: duplicate run_id {run_id}")
        seen.add(run_id)
        if str(entry.get("status") or "") not in ALLOWED_STATUSES:
            errors.append(f"entry {index}: invalid status {entry.get('status')!r}")
        for list_field in ("mechanisms", "dataset_or_manifest", "job_ids", "report_paths", "child_run_ids", "local_missing_allowed"):
            if list_field in entry and not isinstance(entry.get(list_field), list):
                errors.append(f"entry {index}: {list_field} must be a list")
        if "summary_paths" in entry and not isinstance(entry.get("summary_paths"), dict):
            errors.append(f"entry {index}: summary_paths must be an object")
        parent_run_id = str(entry.get("parent_run_id") or "")
        if parent_run_id and parent_run_id not in run_ids:
            errors.append(f"entry {index}: parent_run_id {parent_run_id} not found")
        for child_run_id in entry.get("child_run_ids") or []:
            if child_run_id not in run_ids:
                errors.append(f"entry {index}: child_run_id {child_run_id} not found")
        allowed_missing = set(str(path) for path in entry.get("local_missing_allowed") or [])
        synthetic = bool(entry.get("synthetic"))
        for path_key, path_value in _iter_paths(entry):
            if not path_value:
                continue
            if path_value in allowed_missing:
                continue
            if not _path_exists(path_value):
                errors.append(f"entry {index}: missing {path_key} path {path_value}")
        if not synthetic and not entry.get("run_dir") and entry.get("status") not in {"planned", "running"}:
            errors.append(f"entry {index}: non-synthetic completed entry requires run_dir")
        catalog_status = str(entry.get("catalog_status") or "")
        if catalog_status not in NON_CATALOG_STATUSES and run_id not in catalog_run_ids and not synthetic:
            errors.append(f"entry {index}: catalog_status={catalog_status!r} but run_id not found in evidence catalog")
    return errors


def _md_link(ledger_md_path: Path, value: str, label: str) -> str:
    if not value:
        return ""
    target = _resolve_path(value)
    try:
        href = os.path.relpath(target.resolve(), start=ledger_md_path.parent.resolve())
    except (OSError, ValueError):
        href = str(target)
    return f"[{label}]({href.replace(os.sep, '/')})"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        safe = [str(cell).replace("\n", "<br>").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(safe) + " |")
    return "\n".join(lines)


def write_markdown_ledger(
    ledger: dict[str, Any],
    *,
    ledger_md_path: Path = DEFAULT_LEDGER_MD,
) -> str:
    entries = list(ledger.get("entries") or [])
    lines = [
        "# Evaluation Run Ledger",
        "",
        "This ledger indexes important evaluation runs and points to their machine artifacts, job ids, reports, and catalog status. It is an operational run index, not evidence approval.",
        "",
        f"- Schema version: `{ledger.get('schema_version', SCHEMA_VERSION)}`",
        f"- Last updated: `{ledger.get('updated_at', '')}`",
        "",
        "## Layer Boundaries",
        "",
        "- `eval/runs/...`: raw machine artifacts and local run outputs.",
        "- `run_ledger.*`: operational run index answering when a run happened and where artifacts/reports live.",
        "- `evidence_catalog.*`: reviewed evidence index; only selected runs are cataloged as formal evidence, quality audits, diagnostics, or historical evidence.",
        "- `docs/implementation/.../codex/reports/...`: execution, repair, and interpretation reports that may or may not become cataloged evidence.",
        "",
        "## Runs",
        "",
    ]
    rows: list[list[str]] = []
    for entry in sorted(entries, key=lambda item: (str(item.get("date", "")), str(item.get("run_id", "")))):
        summary_paths = entry.get("summary_paths") if isinstance(entry.get("summary_paths"), dict) else {}
        summary_links = []
        for key in ("aggregate", "report", "llm_usage"):
            if summary_paths.get(key):
                summary_links.append(_md_link(ledger_md_path, str(summary_paths[key]), key))
        report_links = [
            _md_link(ledger_md_path, str(path), f"report {idx}")
            for idx, path in enumerate(entry.get("report_paths") or [], 1)
        ]
        run_link = _md_link(ledger_md_path, str(entry.get("run_dir") or ""), "run dir")
        if not run_link and entry.get("synthetic"):
            run_link = "_synthetic / multi-run_"
        rows.append(
            [
                str(entry.get("date", "")),
                f"`{entry.get('run_id')}`",
                str(entry.get("surface", "")),
                str(entry.get("lane", "")),
                str(entry.get("status", "")),
                ", ".join(f"`{item}`" for item in entry.get("mechanisms") or []),
                str(entry.get("catalog_status", "")),
                " · ".join(item for item in [run_link, *summary_links, *report_links] if item),
                ", ".join(f"`{item}`" for item in entry.get("job_ids") or []),
                str(entry.get("notes", "")),
            ]
        )
    if rows:
        lines.append(
            _table(
                [
                    "date",
                    "run id",
                    "surface",
                    "lane",
                    "status",
                    "mechanisms",
                    "catalog",
                    "artifacts / reports",
                    "job ids",
                    "notes",
                ],
                rows,
            )
        )
    else:
        lines.append("_No entries._")
    text = "\n".join(lines).rstrip() + "\n"
    ledger_md_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_md_path.write_text(text, encoding="utf-8")
    return text


def _scan_entry_from_run_dir(run_dir: Path) -> dict[str, Any]:
    run_id = run_dir.name
    aggregate = _maybe_load_json(run_dir / "summary" / "aggregate.json")
    mechanisms = _infer_mechanisms(aggregate)
    surface = "unknown"
    lane = "unknown"
    if "user_level_selective" in run_id or "user_level" in run_id:
        surface = "user_level_selective_v1"
        lane = "local_user_level_selective"
    elif "long_span" in run_id or "accumulation" in run_id:
        surface = "long_span"
        lane = "long_span"
    elif "excerpt" in run_id:
        surface = "excerpt"
        lane = "excerpt"
    return build_entry(
        run_id=run_id,
        surface=surface,
        lane=lane,
        status="uncataloged_local_artifact",
        mechanisms=mechanisms,
        dataset_or_manifest=[],
        run_dir=run_dir,
        catalog_status="not_cataloged",
        notes="Discovered by scan; not manually classified.",
    )


def scan_runs(*, runs_root: Path = RUNS_ROOT) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not runs_root.exists():
        return entries
    for run_dir in sorted(item for item in runs_root.iterdir() if item.is_dir()):
        if (run_dir / "summary" / "aggregate.json").exists() or (run_dir / "summary" / "report.md").exists():
            entries.append(_scan_entry_from_run_dir(run_dir))
    return entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger-json", type=Path, default=DEFAULT_LEDGER_JSON)
    parser.add_argument("--ledger-md", type=Path, default=DEFAULT_LEDGER_MD)
    parser.add_argument("--catalog-json", type=Path, default=DEFAULT_CATALOG_JSON)
    parser.add_argument("--check", action="store_true", help="Validate ledger JSON and verify markdown is up to date.")
    subparsers = parser.add_subparsers(dest="command")

    upsert = subparsers.add_parser("upsert", help="Create or update one ledger entry.")
    upsert.add_argument("--run-id", required=True)
    upsert.add_argument("--date", default=None)
    upsert.add_argument("--surface", required=True)
    upsert.add_argument("--lane", required=True)
    upsert.add_argument("--status", choices=sorted(ALLOWED_STATUSES), required=True)
    upsert.add_argument("--mechanism", dest="mechanisms", action="append", default=[])
    upsert.add_argument("--dataset-or-manifest", action="append", default=[])
    upsert.add_argument("--run-dir", default="")
    upsert.add_argument("--summary-path", dest="summary_paths", action="append", default=[])
    upsert.add_argument("--job-id", dest="job_ids", action="append", default=[])
    upsert.add_argument("--report-path", dest="report_paths", action="append", default=[])
    upsert.add_argument("--catalog-status", default="not_cataloged")
    upsert.add_argument("--notes", default="")
    upsert.add_argument("--parent-run-id", default="")
    upsert.add_argument("--child-run-id", dest="child_run_ids", action="append", default=[])
    upsert.add_argument("--synthetic", action="store_true")
    upsert.add_argument("--local-missing-allowed", action="append", default=[])
    upsert.add_argument("--metadata", action="append", default=[])

    subparsers.add_parser("render", help="Render markdown from ledger JSON.")
    scan = subparsers.add_parser("scan", help="Scan eval/runs for candidate entries.")
    scan.add_argument("--write", action="store_true", help="Upsert scanned entries into the ledger.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ledger_json_path = Path(args.ledger_json).resolve()
    ledger_md_path = Path(args.ledger_md).resolve()
    catalog_json_path = Path(args.catalog_json).resolve()
    if args.check:
        errors = validate_ledger(ledger_json_path=ledger_json_path, catalog_json_path=catalog_json_path)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        ledger = _read_ledger(ledger_json_path)
        rendered = write_markdown_ledger(ledger, ledger_md_path=ledger_md_path)
        current = ledger_md_path.read_text(encoding="utf-8") if ledger_md_path.exists() else ""
        if current != rendered:
            print(f"ledger markdown not up to date: {ledger_md_path}", file=sys.stderr)
            return 1
        print(f"ledger ok: {ledger_json_path}")
        return 0
    if args.command == "upsert":
        entry = build_entry(
            run_id=str(args.run_id),
            date=args.date,
            surface=str(args.surface),
            lane=str(args.lane),
            status=str(args.status),
            mechanisms=[str(item) for item in args.mechanisms],
            dataset_or_manifest=[str(item) for item in args.dataset_or_manifest],
            run_dir=args.run_dir,
            summary_paths={str(key): str(value) for key, value in _parse_key_value(args.summary_paths).items()},
            job_ids=[str(item) for item in args.job_ids],
            report_paths=[str(item) for item in args.report_paths],
            catalog_status=str(args.catalog_status),
            notes=str(args.notes),
            parent_run_id=str(args.parent_run_id),
            child_run_ids=[str(item) for item in args.child_run_ids],
            synthetic=bool(args.synthetic),
            local_missing_allowed=[str(item) for item in args.local_missing_allowed],
            metadata=_parse_key_value(args.metadata),
        )
        ledger = upsert_ledger_entry(entry, ledger_json_path=ledger_json_path)
        write_markdown_ledger(ledger, ledger_md_path=ledger_md_path)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return 0
    if args.command == "render":
        ledger = _read_ledger(ledger_json_path)
        write_markdown_ledger(ledger, ledger_md_path=ledger_md_path)
        print(f"rendered: {ledger_md_path}")
        return 0
    if args.command == "scan":
        entries = scan_runs()
        if args.write:
            ledger = _read_ledger(ledger_json_path)
            existing = {str(entry.get("run_id")) for entry in ledger.get("entries") or []}
            for entry in entries:
                if entry["run_id"] not in existing:
                    ledger = upsert_ledger_entry(entry, ledger_json_path=ledger_json_path)
            write_markdown_ledger(ledger, ledger_md_path=ledger_md_path)
        else:
            print(json.dumps(entries, ensure_ascii=False, indent=2))
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
