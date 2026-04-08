#!/usr/bin/env python3
"""Wait for Lane A to finish, then run private-library round-3 ready cleanup."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.reading_runtime.background_job_registry import (  # noqa: E402
    archive_background_job,
    get_active_job,
    inspect_background_job,
    upsert_background_job,
)


LANE_A_JOB_ID = "bgjob_en_chapter_core_rerun_retry2_20260328"
LANE_A_RUN_ID = "attentional_v2_vs_iterator_v1_chapter_core_en_round2_microselectivity_retry2_20260328"
LANE_A_RUN_DIR = BACKEND_ROOT / "eval" / "runs" / "attentional_v2" / LANE_A_RUN_ID
LANE_A_EXPECTED_OUTPUTS = (
    LANE_A_RUN_DIR / "summary" / "report.md",
    LANE_A_RUN_DIR / "summary" / "aggregate.json",
)
LANE_A_PROGRESS_GLOBS = (
    "cases/*.json",
    "bundles/**/*.json",
)
LANE_A_PROGRESS_FILES = (
    "launcher.log",
    "llm_traces/standard.jsonl",
)

TASK_REF = "execution-tracker#private-library-cleanup-round3"
PENDING_PACKET_ROOT = BACKEND_ROOT / "eval" / "review_packets" / "pending"
ARCHIVE_PACKET_ROOT = BACKEND_ROOT / "eval" / "review_packets" / "archive"
QUEUE_SUMMARY_MD = BACKEND_ROOT / "eval" / "review_packets" / "review_queue_summary.md"
QUEUE_SUMMARY_JSON = BACKEND_ROOT / "eval" / "review_packets" / "review_queue_summary.json"

EN_DATASET = "attentional_v2_private_library_excerpt_en_v2"
ZH_DATASET = "attentional_v2_private_library_excerpt_zh_v2"

SELECTION_JSON = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round1-selection.json"
CHAPTER_SANITY_JSON = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round1-chapter-sanity-results.json"
EXECUTION_TRACKER_MD = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "new-reading-mechanism-execution-tracker.md"
AGENT_HANDOFF_MD = WORKSPACE_ROOT / "docs" / "agent-handoff.md"
ROUND1_EXECUTION_MD = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round1-execution.md"
ROUND2_PROMOTION_MD = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round2.md"
ROUND2_PROMOTION_JSON = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round2.json"

EN_READY_CASE_IDS = (
    "evicted_private_en__17__seed_2",
    "steve_jobs_private_en__17__seed_1",
    "steve_jobs_private_en__17__seed_2",
    "steve_jobs_private_en__24__seed_1",
    "steve_jobs_private_en__24__seed_2",
    "supremacy_private_en__13__seed_1",
)
ZH_READY_CASE_IDS = (
    "biji_de_fangfa_private_zh__13__seed_1",
    "kangxi_hongpiao_private_zh__12__seed_1",
    "zhangzhongmou_zizhuan_private_zh__4__seed_2",
    "zhangzhongmou_zizhuan_private_zh__10__seed_1",
)
PARKED_CASE_IDS = {
    "en": (
        "fooled_by_randomness_private_en__14__seed_2",
        "poor_charlies_almanack_private_en__10__seed_1",
        "evicted_private_en__10__seed_1",
        "poor_charlies_almanack_private_en__10__seed_2",
    ),
    "zh": (
        "fooled_by_randomness_private_zh__19__seed_2",
        "kangxi_hongpiao_private_zh__12__seed_2",
        "zouchu_weiyi_zhenliguan_private_zh__8__seed_1",
        "kangxi_hongpiao_private_zh__27__seed_1",
    ),
}

SECTION_TRACKER = "## 2026-03-28 Private-Library Round-3 Ready Cleanup"
SECTION_HANDOFF = "## 2026-03-28 Private-Library Cleanup Round-3 Closeout"
SECTION_EXECUTION = "## Round-3 Ready-Subset Cleanup And Promotion Draft"


@dataclass(frozen=True)
class PipelineConfig:
    language: str
    dataset_id: str
    packet_id: str
    job_id: str
    case_ids: tuple[str, ...]

    @property
    def packet_dir(self) -> Path:
        return PENDING_PACKET_ROOT / self.packet_id

    @property
    def archive_dir(self) -> Path:
        return ARCHIVE_PACKET_ROOT / self.packet_id


PIPELINES = (
    PipelineConfig(
        language="en",
        dataset_id=EN_DATASET,
        packet_id="attentional_v2_private_library_cleanup_round3_en_ready",
        job_id="bgjob_private_library_cleanup_round3_en_ready",
        case_ids=EN_READY_CASE_IDS,
    ),
    PipelineConfig(
        language="zh",
        dataset_id=ZH_DATASET,
        packet_id="attentional_v2_private_library_cleanup_round3_zh_ready",
        job_id="bgjob_private_library_cleanup_round3_zh_ready",
        case_ids=ZH_READY_CASE_IDS,
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def log(message: str) -> None:
    print(f"[{utc_now()}] {message}", flush=True)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON at {path}")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object row in {path}")
        rows.append(payload)
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_command(args: list[str], *, label: str) -> None:
    log(f"{label}: {' '.join(shlex.quote(part) for part in args)}")
    subprocess.run(args, cwd=BACKEND_ROOT, check=True)


def run_registry_check(job_id: str) -> dict[str, Any]:
    args = [
        str(BACKEND_ROOT / ".venv" / "bin" / "python"),
        "scripts/check_background_jobs.py",
        "--job-id",
        job_id,
        "--run-check-commands",
    ]
    completed = subprocess.run(
        args,
        cwd=BACKEND_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if not isinstance(payload, dict):
        raise ValueError("Unexpected registry-check payload")
    return payload


def append_unique_section(path: Path, header: str, body: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if header in existing:
        return
    suffix = "" if existing.endswith("\n") else "\n"
    block = f"{suffix}\n{header}\n{body.rstrip()}\n"
    path.write_text(existing + block, encoding="utf-8")


def lane_a_outputs_exist() -> bool:
    return all(path.exists() for path in LANE_A_EXPECTED_OUTPUTS)


def lane_a_progress_snapshot() -> dict[str, int]:
    snapshot: dict[str, int] = {}
    for pattern in LANE_A_PROGRESS_GLOBS:
        for path in sorted(LANE_A_RUN_DIR.glob(pattern)):
            if path.is_file():
                snapshot[str(path.relative_to(LANE_A_RUN_DIR))] = path.stat().st_mtime_ns
    for relative in LANE_A_PROGRESS_FILES:
        path = LANE_A_RUN_DIR / relative
        if path.exists():
            snapshot[str(path.relative_to(LANE_A_RUN_DIR))] = path.stat().st_mtime_ns
    return snapshot


def has_forward_progress(previous: dict[str, int], current: dict[str, int]) -> bool:
    for path, mtime in current.items():
        if previous.get(path, -1) < mtime:
            return True
    return False


def collect_run_state_errors() -> list[tuple[str, Any]]:
    errors: list[tuple[str, Any]] = []
    for path in sorted(LANE_A_RUN_DIR.glob("outputs/**/_runtime/run_state.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        error = payload.get("error")
        if error:
            errors.append((str(path.relative_to(LANE_A_RUN_DIR)), error))
    return errors


def wait_for_lane_a_completion(
    *,
    poll_seconds: int,
    registry_check_seconds: int,
    stall_seconds: int,
) -> None:
    if lane_a_outputs_exist():
        log("Lane A already has both final summary outputs; skipping wait.")
        return

    initial_job = get_active_job(LANE_A_JOB_ID, root=BACKEND_ROOT)
    if initial_job is None:
        raise RuntimeError(f"Lane A job is missing from the active registry: {LANE_A_JOB_ID}")

    observation = inspect_background_job(initial_job, run_check_command=False)
    if not observation.get("pid_alive"):
        raise RuntimeError("Lane A PID is not alive and final outputs are still missing.")
    errors = collect_run_state_errors()
    if errors:
        raise RuntimeError(f"Lane A has mechanism-local run_state errors: {errors}")

    last_snapshot = lane_a_progress_snapshot()
    last_progress_at = time.time()
    last_registry_check = 0.0
    stall_logged = False
    log(
        "Lane A wait loop started with "
        f"{len(last_snapshot)} progress artifacts and pid={initial_job.get('pid')!r}."
    )

    while True:
        if lane_a_outputs_exist():
            log("Lane A final summary outputs detected.")
            return

        now = time.time()
        if now - last_registry_check >= registry_check_seconds:
            payload = run_registry_check(LANE_A_JOB_ID)
            jobs = payload.get("jobs", [])
            log(
                "Lane A registry check refreshed: "
                f"jobs={len(jobs)} expected_outputs="
                f"{sum(1 for item in (jobs[0].get('latest_observation', {}).get('expected_outputs', []) if jobs else []) if item.get('exists'))}/2."
            )
            last_registry_check = now

        time.sleep(poll_seconds)
        current_snapshot = lane_a_progress_snapshot()
        if has_forward_progress(last_snapshot, current_snapshot):
            last_progress_at = time.time()
            stall_logged = False
            log(
                "Lane A artifacts advanced; "
                f"tracked_files={len(current_snapshot)} newest={max(current_snapshot.values(), default=0)}."
            )
        elif time.time() - last_progress_at >= stall_seconds and not stall_logged:
            log("Lane A appears stalled for >= 20 minutes; inspecting only, no restart.")
            job = get_active_job(LANE_A_JOB_ID, root=BACKEND_ROOT)
            if job is not None:
                observation = inspect_background_job(job, run_check_command=False)
                log(
                    "Lane A stall inspection: "
                    f"status={observation.get('status')} pid_alive={observation.get('pid_alive')}."
                )
            errors = collect_run_state_errors()
            if errors:
                raise RuntimeError(f"Lane A stall inspection found run_state errors: {errors}")
            stall_logged = True

        last_snapshot = current_snapshot
        if lane_a_outputs_exist():
            log("Lane A final summary outputs detected after artifact check.")
            return

        job = get_active_job(LANE_A_JOB_ID, root=BACKEND_ROOT)
        if job is None:
            raise RuntimeError("Lane A dropped out of the active registry before producing final outputs.")
        observation = inspect_background_job(job, run_check_command=False)
        if not observation.get("pid_alive"):
            raise RuntimeError("Lane A PID died before producing final outputs.")


def packet_manifest_case_ids(packet_dir: Path) -> list[str]:
    rows = load_jsonl(packet_dir / "cases.source.jsonl")
    return [str(row.get("case_id", "")).strip() for row in rows]


def validate_packet_contents(config: PipelineConfig) -> None:
    if not config.packet_dir.exists():
        raise FileNotFoundError(f"Pending packet missing: {config.packet_dir}")
    case_ids = packet_manifest_case_ids(config.packet_dir)
    expected = list(config.case_ids)
    if case_ids != expected:
        raise ValueError(
            f"Packet {config.packet_id} case ids mismatch. Expected {expected}, found {case_ids}"
        )
    parked = set(PARKED_CASE_IDS[config.language])
    if parked.intersection(case_ids):
        raise ValueError(f"Packet {config.packet_id} unexpectedly contains parked cases.")


def ensure_packet_materialized(config: PipelineConfig) -> None:
    if config.archive_dir.exists():
        raise FileExistsError(f"Archive packet already exists; refusing to rerun {config.packet_id}")
    if config.packet_dir.exists():
        log(f"Packet already materialized: {config.packet_dir}")
        validate_packet_contents(config)
        return

    args = [
        str(BACKEND_ROOT / ".venv" / "bin" / "python"),
        "-m",
        "eval.attentional_v2.generate_revision_replacement_packet",
        "--dataset-id",
        config.dataset_id,
        "--family",
        "excerpt_cases",
        "--storage-mode",
        "local-only",
        "--packet-id",
        config.packet_id,
    ]
    for case_id in config.case_ids:
        args.extend(["--case-id", case_id])
    run_command(args, label=f"materialize {config.packet_id}")
    validate_packet_contents(config)


def register_or_update_job(
    *,
    job_id: str,
    purpose: str,
    command: str,
    run_dir: Path | None,
    expected_outputs: list[Path],
    log_file: str,
    status: str,
    notes: str,
) -> None:
    check_command = f'test -f "{expected_outputs[0]}" && echo completed || tail -n 80 "{log_file}"'
    upsert_background_job(
        job_id=job_id,
        root=BACKEND_ROOT,
        task_ref=TASK_REF,
        lane="dataset_growth",
        purpose=purpose,
        command=command,
        cwd=str(BACKEND_ROOT),
        pid=os.getpid(),
        run_dir=str(run_dir) if run_dir else "",
        log_file=log_file,
        expected_outputs=[str(path) for path in expected_outputs],
        check_command=check_command,
        next_check_hint="Wait for the packet import summary to land, then archive the job.",
        decision_if_success="Use the refreshed local-only excerpt statuses to draft the next promotion shortlist.",
        decision_if_failure="Inspect the packet log and the packet/audit artifacts before retrying.",
        status=status,
        notes=notes,
    )


def archive_job_if_present(job_id: str, reason: str) -> None:
    if get_active_job(job_id, root=BACKEND_ROOT) is not None:
        archive_background_job(job_id, root=BACKEND_ROOT, archive_reason=reason)


def pipeline_command_summary(config: PipelineConfig) -> str:
    return " && ".join(
        [
            f".venv/bin/python -m eval.attentional_v2.run_case_design_audit --packet-id {config.packet_id} --max-workers 1",
            f".venv/bin/python -m eval.attentional_v2.auto_review_packet --packet-id {config.packet_id}",
            f".venv/bin/python -m eval.attentional_v2.import_dataset_review_packet --packet-id {config.packet_id} --review-origin llm --archive",
            ".venv/bin/python -m eval.attentional_v2.build_review_queue_summary",
        ]
    )


def run_cleanup_pipeline(config: PipelineConfig, *, orchestrator_log_file: str) -> None:
    ensure_packet_materialized(config)
    register_or_update_job(
        job_id=config.job_id,
        purpose=f"Private-library ready-subset cleanup pipeline ({config.language})",
        command=pipeline_command_summary(config),
        run_dir=config.packet_dir,
        expected_outputs=[config.archive_dir / "import_summary.json"],
        log_file=orchestrator_log_file,
        status="running",
        notes="Serial cleanup step launched by the Lane-A-safe orchestrator.",
    )
    try:
        run_command(
            [
                str(BACKEND_ROOT / ".venv" / "bin" / "python"),
                "-m",
                "eval.attentional_v2.run_case_design_audit",
                "--packet-id",
                config.packet_id,
                "--max-workers",
                "1",
            ],
            label=f"audit {config.packet_id}",
        )
        run_command(
            [
                str(BACKEND_ROOT / ".venv" / "bin" / "python"),
                "-m",
                "eval.attentional_v2.auto_review_packet",
                "--packet-id",
                config.packet_id,
            ],
            label=f"review {config.packet_id}",
        )
        run_command(
            [
                str(BACKEND_ROOT / ".venv" / "bin" / "python"),
                "-m",
                "eval.attentional_v2.import_dataset_review_packet",
                "--packet-id",
                config.packet_id,
                "--review-origin",
                "llm",
                "--archive",
            ],
            label=f"import {config.packet_id}",
        )
        run_command(
            [
                str(BACKEND_ROOT / ".venv" / "bin" / "python"),
                "-m",
                "eval.attentional_v2.build_review_queue_summary",
            ],
            label="refresh review queue",
        )
        register_or_update_job(
            job_id=config.job_id,
            purpose=f"Private-library ready-subset cleanup pipeline ({config.language})",
            command=pipeline_command_summary(config),
            run_dir=config.archive_dir,
            expected_outputs=[config.archive_dir / "import_summary.json"],
            log_file=orchestrator_log_file,
            status="completed",
            notes="Cleanup pipeline finished successfully and the packet was archived.",
        )
        archive_job_if_present(config.job_id, "completed_by_private_library_cleanup_round3_orchestrator")
    except Exception:
        register_or_update_job(
            job_id=config.job_id,
            purpose=f"Private-library ready-subset cleanup pipeline ({config.language})",
            command=pipeline_command_summary(config),
            run_dir=config.packet_dir,
            expected_outputs=[config.archive_dir / "import_summary.json"],
            log_file=orchestrator_log_file,
            status="failed",
            notes="Cleanup pipeline failed; inspect the orchestrator log and packet artifacts.",
        )
        raise


def dataset_primary_file_path(dataset_id: str) -> Path:
    dataset_dir = BACKEND_ROOT / "state" / "eval_local_datasets" / "excerpt_cases" / dataset_id
    manifest = load_json(dataset_dir / "manifest.json")
    return dataset_dir / str(manifest["primary_file"])


def role_for_row(row: dict[str, Any]) -> str:
    role = str(row.get("selection_role", "")).strip()
    if role:
        return role
    role_tags = row.get("role_tags", [])
    if isinstance(role_tags, list):
        for tag in role_tags:
            text = str(tag).strip()
            if text:
                return text
    return "unknown"


def classify_problem_family(row: dict[str, Any]) -> str:
    latest = row.get("review_latest") if isinstance(row.get("review_latest"), dict) else {}
    problem_types = {str(item).strip() for item in latest.get("problem_types", []) if str(item).strip()}
    benchmark_status = str(row.get("benchmark_status", "")).strip()
    if benchmark_status == "needs_replacement":
        return "replacement"
    if {"text_noise", "source_parse_problem"} & problem_types:
        return "parse_noise_boundary"
    if any(item in problem_types for item in {"ambiguous_focus", "too_easy", "weak_excerpt"}):
        return "focus_bucket"
    return "metadata_or_revision"


def summarize_survivors(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, dict[str, Any]] = {}
    role_counts: Counter[str] = Counter()
    for row in sorted(rows, key=lambda item: str(item.get("case_id", ""))):
        source_id = str(row.get("source_id", "")).strip() or str(row.get("case_id", "")).split("__seed_")[0]
        source_entry = by_source.setdefault(
            source_id,
            {
                "source_id": source_id,
                "book_title": str(row.get("book_title", "")).strip(),
                "author": str(row.get("author", "")).strip(),
                "case_count": 0,
                "role_counts": Counter(),
                "case_ids": [],
            },
        )
        role = role_for_row(row)
        role_counts[role] += 1
        source_entry["role_counts"][role] += 1
        source_entry["case_count"] += 1
        source_entry["case_ids"].append(str(row.get("case_id", "")).strip())

    sources = []
    for source_id in sorted(by_source):
        entry = by_source[source_id]
        entry["role_counts"] = dict(sorted(entry["role_counts"].items()))
        sources.append(entry)
    return {
        "reviewed_active_count": len(rows),
        "role_counts": dict(sorted(role_counts.items())),
        "sources": sources,
    }


def build_parked_backlog(rows_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for language, case_ids in PARKED_CASE_IDS.items():
        sources: dict[str, dict[str, Any]] = {}
        for case_id in case_ids:
            row = rows_by_id[case_id]
            source_id = str(row.get("source_id", "")).strip()
            source_entry = sources.setdefault(
                source_id,
                {
                    "source_id": source_id,
                    "book_title": str(row.get("book_title", "")).strip(),
                    "author": str(row.get("author", "")).strip(),
                    "cases": [],
                },
            )
            latest = row.get("review_latest") if isinstance(row.get("review_latest"), dict) else {}
            source_entry["cases"].append(
                {
                    "case_id": case_id,
                    "benchmark_status": str(row.get("benchmark_status", "")).strip(),
                    "selection_role": role_for_row(row),
                    "problem_family": classify_problem_family(row),
                    "problem_types": list(latest.get("problem_types", [])),
                    "notes": str(latest.get("notes", "")).strip(),
                }
            )
        payload[language] = {"source_count": len(sources), "sources": list(sources.values())}
    return payload


def build_round2_payload() -> dict[str, Any]:
    en_rows = load_jsonl(dataset_primary_file_path(EN_DATASET))
    zh_rows = load_jsonl(dataset_primary_file_path(ZH_DATASET))
    rows_by_id = {str(row.get("case_id", "")): row for row in [*en_rows, *zh_rows]}
    selection = load_json(SELECTION_JSON)
    chapter_sanity = load_json(CHAPTER_SANITY_JSON)

    en_survivors = [row for row in en_rows if str(row.get("benchmark_status", "")).strip() == "reviewed_active"]
    zh_survivors = [row for row in zh_rows if str(row.get("benchmark_status", "")).strip() == "reviewed_active"]

    def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
        return dict(sorted(Counter(str(row.get("benchmark_status", "")).strip() for row in rows).items()))

    return {
        "round_id": "private_library_promotion_round2",
        "generated_at": today_str(),
        "lane_a_run_id": LANE_A_RUN_ID,
        "cleanup_packets": [
            {
                "language": config.language,
                "packet_id": config.packet_id,
                "archive_dir": str(config.archive_dir),
                "import_summary": str(config.archive_dir / "import_summary.json"),
            }
            for config in PIPELINES
        ],
        "excerpt_survivors": {
            "en": summarize_survivors(en_survivors),
            "zh": summarize_survivors(zh_survivors),
        },
        "dataset_status_counts": {
            "en": status_counts(en_rows),
            "zh": status_counts(zh_rows),
        },
        "chapter_constraints": {
            "en": {
                "selected_ids": list(selection["chapter_lift"]["en"]["selected_ids"]),
                "eligible_count": len(selection["chapter_lift"]["en"]["selected_ids"]),
                "status": "keep_current_8",
            },
            "zh": {
                "selected_ids": list(chapter_sanity["languages"]["zh"]["promote_next"]),
                "eligible_count": len(chapter_sanity["languages"]["zh"]["promote_next"]),
                "status": "limit_to_current_2",
            },
        },
        "parked_backlog": build_parked_backlog(rows_by_id),
        "notes": [
            "Uses only post-cleanup reviewed_active rows for the excerpt shortlist.",
            "Does not materialize or import a new curated promotion packet in this slice.",
            "Keeps English chapter promotion at the current 8 and Chinese chapter promotion limited to the currently cleared 2.",
        ],
    }


def render_round2_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Private-Library Promotion Round 2 Draft",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- lane_a_run_id: `{payload['lane_a_run_id']}`",
        "- scope: post-cleanup survivor-based promotion planning only",
        "- rule: do not materialize or import a new curated promotion packet in this slice",
        "",
        "## Cleanup Packets",
    ]
    for packet in payload["cleanup_packets"]:
        lines.extend(
            [
                f"- `{packet['language']}`",
                f"  - packet_id: `{packet['packet_id']}`",
                f"  - archive_dir: `{packet['archive_dir']}`",
                f"  - import_summary: `{packet['import_summary']}`",
            ]
        )

    lines.extend(
        [
            "",
            "## Chapter Carry-Forward",
            "- English:",
            f"  - keep current `8`: `{', '.join(payload['chapter_constraints']['en']['selected_ids'])}`",
            "- Chinese:",
            f"  - limit to current `2`: `{', '.join(payload['chapter_constraints']['zh']['selected_ids'])}`",
        ]
    )

    for language in ("en", "zh"):
        summary = payload["excerpt_survivors"][language]
        lines.extend(
            [
                "",
                f"## Excerpt Survivors `{language}`",
                f"- reviewed_active: `{summary['reviewed_active_count']}`",
                f"- role_counts: `{json.dumps(summary['role_counts'], ensure_ascii=False)}`",
                f"- status_counts: `{json.dumps(payload['dataset_status_counts'][language], ensure_ascii=False)}`",
            ]
        )
        for source in summary["sources"]:
            lines.extend(
                [
                    f"- `{source['book_title']}` (`{source['source_id']}`) by `{source['author']}`",
                    f"  - case_count: `{source['case_count']}`",
                    f"  - role_counts: `{json.dumps(source['role_counts'], ensure_ascii=False)}`",
                    f"  - case_ids: `{', '.join(source['case_ids'])}`",
                ]
            )

    lines.extend(["", "## Parked Backlog"])
    for language in ("en", "zh"):
        parked = payload["parked_backlog"][language]
        lines.append(f"- `{language}` sources: `{parked['source_count']}`")
        for source in parked["sources"]:
            lines.append(f"  - `{source['book_title']}` (`{source['source_id']}`)")
            for case in source["cases"]:
                lines.extend(
                    [
                        f"    - `{case['case_id']}`",
                        f"      - benchmark_status: `{case['benchmark_status']}`",
                        f"      - selection_role: `{case['selection_role']}`",
                        f"      - problem_family: `{case['problem_family']}`",
                        f"      - problem_types: `{ '|'.join(case['problem_types']) }`",
                        f"      - notes: {case['notes']}",
                    ]
                )

    lines.extend(["", "## Notes"])
    for note in payload["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines).rstrip() + "\n"


def refresh_closeout_docs(payload: dict[str, Any]) -> None:
    en_counts = payload["dataset_status_counts"]["en"]
    zh_counts = payload["dataset_status_counts"]["zh"]
    tracker_body = f"""- Completed the private-library round-3 ready cleanup after Lane A finished.
- English cleanup packet: `attentional_v2_private_library_cleanup_round3_en_ready`
- Chinese cleanup packet: `attentional_v2_private_library_cleanup_round3_zh_ready`
- Post-cleanup local-only excerpt status counts:
  - English: `{json.dumps(en_counts, ensure_ascii=False)}`
  - Chinese: `{json.dumps(zh_counts, ensure_ascii=False)}`
- Wrote the survivor-based promotion draft:
  - `{ROUND2_PROMOTION_MD}`
  - `{ROUND2_PROMOTION_JSON}`
- Kept chapter carry-forward constraints unchanged:
  - English: current `8`
  - Chinese: current `2`
"""
    append_unique_section(EXECUTION_TRACKER_MD, SECTION_TRACKER, tracker_body)

    handoff_body = f"""- Lane A completed at `{LANE_A_RUN_DIR}` and the ready-subset cleanup pipeline has landed.
- Cleanup packet archives:
  - `{PIPELINES[0].archive_dir}`
  - `{PIPELINES[1].archive_dir}`
- Promotion draft artifacts:
  - `{ROUND2_PROMOTION_MD}`
  - `{ROUND2_PROMOTION_JSON}`
- Next decision point:
  - decide which post-cleanup excerpt survivors enter the next curated benchmark pass
  - decide whether the Chinese chapter lane stays at `2` for now or waits for further recuts
"""
    append_unique_section(AGENT_HANDOFF_MD, SECTION_HANDOFF, handoff_body)

    execution_body = f"""The round-3 ready cleanup is now complete.

- English packet archive:
  - `{PIPELINES[0].archive_dir}`
- Chinese packet archive:
  - `{PIPELINES[1].archive_dir}`
- Queue state:
  - `{QUEUE_SUMMARY_MD}`
- Post-cleanup survivor planning now lives in:
  - `{ROUND2_PROMOTION_MD}`
  - `{ROUND2_PROMOTION_JSON}`
- This execution pass still stops before materializing or importing a new curated promotion packet.
"""
    append_unique_section(ROUND1_EXECUTION_MD, SECTION_EXECUTION, execution_body)


def write_round2_artifacts(payload: dict[str, Any]) -> None:
    write_json(ROUND2_PROMOTION_JSON, payload)
    ROUND2_PROMOTION_MD.write_text(render_round2_markdown(payload), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-id", default="", help="Optional background-job id for this orchestrator.")
    parser.add_argument("--log-file", default="", help="Log file path used by the background-job registry.")
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--registry-check-seconds", type=int, default=900)
    parser.add_argument("--stall-seconds", type=int, default=1200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    command = " ".join(shlex.quote(part) for part in [sys.executable, *sys.argv])
    if args.job_id:
        register_or_update_job(
            job_id=args.job_id,
            purpose="Lane-A-safe private-library cleanup round-3 orchestrator",
            command=command,
            run_dir=LANE_A_RUN_DIR,
            expected_outputs=[ROUND2_PROMOTION_JSON, ROUND2_PROMOTION_MD],
            log_file=args.log_file,
            status="running",
            notes="Waiting for Lane A to finish before running the serial cleanup pipeline.",
        )

    try:
        wait_for_lane_a_completion(
            poll_seconds=args.poll_seconds,
            registry_check_seconds=args.registry_check_seconds,
            stall_seconds=args.stall_seconds,
        )
        for config in PIPELINES:
            run_cleanup_pipeline(config, orchestrator_log_file=args.log_file)

        payload = build_round2_payload()
        write_round2_artifacts(payload)
        refresh_closeout_docs(payload)
        log("Private-library round-3 cleanup and promotion draft closeout completed.")
        if args.job_id:
            register_or_update_job(
                job_id=args.job_id,
                purpose="Lane-A-safe private-library cleanup round-3 orchestrator",
                command=command,
                run_dir=BACKEND_ROOT,
                expected_outputs=[ROUND2_PROMOTION_JSON, ROUND2_PROMOTION_MD],
                log_file=args.log_file,
                status="completed",
                notes="Orchestrator finished successfully and wrote the round-2 promotion draft.",
            )
            archive_job_if_present(args.job_id, "completed_by_private_library_cleanup_round3_orchestrator")
        return 0
    except Exception as exc:
        log(f"Orchestrator failed: {exc}")
        if args.job_id:
            register_or_update_job(
                job_id=args.job_id,
                purpose="Lane-A-safe private-library cleanup round-3 orchestrator",
                command=command,
                run_dir=BACKEND_ROOT,
                expected_outputs=[ROUND2_PROMOTION_JSON, ROUND2_PROMOTION_MD],
                log_file=args.log_file,
                status="failed",
                notes=f"Failure: {exc}",
            )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
