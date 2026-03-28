#!/usr/bin/env python3
"""Prepare and orchestrate the private-library round-3 cleanup after Lane A completes."""

from __future__ import annotations

import argparse
import csv
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


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
PYTHON = ROOT / ".venv" / "bin" / "python"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reading_runtime.background_job_registry import (  # noqa: E402
    get_active_job,
    process_is_alive,
    refresh_background_jobs,
    upsert_background_job,
)
from src.reading_runtime.llm_registry import (  # noqa: E402
    DEFAULT_DATASET_REVIEW_PROFILE_ID,
    DEFAULT_RUNTIME_PROFILE_ID,
    get_llm_registry,
)


LANE_A_JOB_ID = "bgjob_en_chapter_core_rerun_retry2_20260328"
ORCHESTRATOR_JOB_ID = "bgjob_private_library_cleanup_round3_orchestrator_20260328"
LANE_A_RUN_ID = "attentional_v2_vs_iterator_v1_chapter_core_en_round2_microselectivity_retry2_20260328"
LANE_A_RUN_DIR = ROOT / "eval" / "runs" / "attentional_v2" / LANE_A_RUN_ID
LANE_A_EXPECTED_OUTPUTS = (
    LANE_A_RUN_DIR / "summary" / "report.md",
    LANE_A_RUN_DIR / "summary" / "aggregate.json",
)
LANE_A_TRACK_PATTERNS = (
    "cases/*.json",
    "bundles/attentional_v2/*.json",
    "bundles/iterator_v1/*.json",
    "launcher.log",
    "llm_traces/standard.jsonl",
    "outputs/*/*/_runtime/run_state.json",
)

STATUS_DIR = ROOT / "state" / "job_registry" / "status"
LOG_DIR = ROOT / "state" / "job_registry" / "logs"
COORDINATION_DIR = ROOT / "state" / "coordination"

PRE_CLEANUP_DRAFT_JSON = COORDINATION_DIR / "private_library_promotion_round2_precleanup_draft.json"
PRE_CLEANUP_DRAFT_MD = COORDINATION_DIR / "private_library_promotion_round2_precleanup_draft.md"

ROUND2_DRAFT_MD = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round2.md"
ROUND2_DRAFT_JSON = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round2.json"
EXECUTION_TRACKER = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "execution-tracker.md"
AGENT_HANDOFF = WORKSPACE_ROOT / "docs" / "agent-handoff.md"
ROUND1_EXECUTION_DOC = WORKSPACE_ROOT / "docs" / "implementation" / "new-reading-mechanism" / "private-library-promotion-round1-execution.md"
CHAPTER_SANITY_RESULTS_JSON = (
    WORKSPACE_ROOT
    / "docs"
    / "implementation"
    / "new-reading-mechanism"
    / "private-library-promotion-round1-chapter-sanity-results.json"
)

REVIEW_PACKET_PENDING_ROOT = ROOT / "eval" / "review_packets" / "pending"
REVIEW_PACKET_ARCHIVE_ROOT = ROOT / "eval" / "review_packets" / "archive"

ORCHESTRATOR_STATUS_FILE = STATUS_DIR / f"{ORCHESTRATOR_JOB_ID}.json"
ORCHESTRATOR_LOG_FILE = LOG_DIR / f"{ORCHESTRATOR_JOB_ID}.log"

PREPARE_ONLY_NOTE = "prepare_only"
POLL_SECONDS = 300
CHECK_REFRESH_SECONDS = 900
STALL_SECONDS = 1200


@dataclass(frozen=True)
class PacketPlan:
    language: str
    dataset_id: str
    packet_id: str
    cleanup_job_id: str
    case_ids: tuple[str, ...]
    parked_case_ids: tuple[str, ...]


PACKET_PLANS = (
    PacketPlan(
        language="en",
        dataset_id="attentional_v2_private_library_excerpt_en_v2",
        packet_id="attentional_v2_private_library_cleanup_round3_en_ready",
        cleanup_job_id="bgjob_private_library_cleanup_round3_en_ready",
        case_ids=(
            "evicted_private_en__17__seed_2",
            "steve_jobs_private_en__17__seed_1",
            "steve_jobs_private_en__17__seed_2",
            "steve_jobs_private_en__24__seed_1",
            "steve_jobs_private_en__24__seed_2",
            "supremacy_private_en__13__seed_1",
        ),
        parked_case_ids=(
            "fooled_by_randomness_private_en__14__seed_2",
            "poor_charlies_almanack_private_en__10__seed_1",
            "evicted_private_en__10__seed_1",
            "poor_charlies_almanack_private_en__10__seed_2",
        ),
    ),
    PacketPlan(
        language="zh",
        dataset_id="attentional_v2_private_library_excerpt_zh_v2",
        packet_id="attentional_v2_private_library_cleanup_round3_zh_ready",
        cleanup_job_id="bgjob_private_library_cleanup_round3_zh_ready",
        case_ids=(
            "biji_de_fangfa_private_zh__13__seed_1",
            "kangxi_hongpiao_private_zh__12__seed_1",
            "zhangzhongmou_zizhuan_private_zh__4__seed_2",
            "zhangzhongmou_zizhuan_private_zh__10__seed_1",
        ),
        parked_case_ids=(
            "fooled_by_randomness_private_zh__19__seed_2",
            "kangxi_hongpiao_private_zh__12__seed_2",
            "zouchu_weiyi_zhenliguan_private_zh__8__seed_1",
            "kangxi_hongpiao_private_zh__27__seed_1",
        ),
    ),
)

PARKED_BACKLOG = {
    "en": [
        {
            "case_id": "fooled_by_randomness_private_en__14__seed_2",
            "source_id": "fooled_by_randomness_private_en",
            "book_title": "Fooled by Randomness",
            "problem_family": "parse_noise_boundary",
            "benchmark_status": "needs_revision",
        },
        {
            "case_id": "poor_charlies_almanack_private_en__10__seed_1",
            "source_id": "poor_charlies_almanack_private_en",
            "book_title": "Poor Charlie's Almanack",
            "problem_family": "parse_noise_boundary",
            "benchmark_status": "needs_revision",
        },
        {
            "case_id": "evicted_private_en__10__seed_1",
            "source_id": "evicted_private_en",
            "book_title": "Evicted",
            "problem_family": "replacement",
            "benchmark_status": "needs_replacement",
        },
        {
            "case_id": "poor_charlies_almanack_private_en__10__seed_2",
            "source_id": "poor_charlies_almanack_private_en",
            "book_title": "Poor Charlie's Almanack",
            "problem_family": "replacement",
            "benchmark_status": "needs_replacement",
        },
    ],
    "zh": [
        {
            "case_id": "fooled_by_randomness_private_zh__19__seed_2",
            "source_id": "fooled_by_randomness_private_zh",
            "book_title": "随机漫步的傻瓜",
            "problem_family": "parse_noise_boundary",
            "benchmark_status": "needs_revision",
        },
        {
            "case_id": "kangxi_hongpiao_private_zh__12__seed_2",
            "source_id": "kangxi_hongpiao_private_zh",
            "book_title": "康熙的红票：全球化中的清朝",
            "problem_family": "parse_noise_boundary",
            "benchmark_status": "needs_revision",
        },
        {
            "case_id": "zouchu_weiyi_zhenliguan_private_zh__8__seed_1",
            "source_id": "zouchu_weiyi_zhenliguan_private_zh",
            "book_title": "走出唯一真理观",
            "problem_family": "parse_noise_boundary",
            "benchmark_status": "needs_revision",
        },
        {
            "case_id": "kangxi_hongpiao_private_zh__27__seed_1",
            "source_id": "kangxi_hongpiao_private_zh",
            "book_title": "康熙的红票：全球化中的清朝",
            "problem_family": "replacement",
            "benchmark_status": "needs_replacement",
        },
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def append_log(path: Path, message: str) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{utc_now()}] {message}\n")


def write_status(path: Path, status: str, **extra: Any) -> None:
    payload = {"status": status, "updated_at": utc_now(), **extra}
    write_json(path, payload)


def run_logged(command: list[str], *, log_path: Path, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    append_log(log_path, f"$ {' '.join(shlex.quote(part) for part in command)}")
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    stdout = completed.stdout.rstrip()
    stderr = completed.stderr.rstrip()
    if stdout:
        append_log(log_path, stdout)
    if stderr:
        append_log(log_path, stderr)
    append_log(log_path, f"exit_code={completed.returncode}")
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed


def load_dataset_rows(dataset_id: str) -> list[dict[str, Any]]:
    path = ROOT / "state" / "eval_local_datasets" / "excerpt_cases" / dataset_id / "cases.jsonl"
    return read_jsonl(path)


def packet_dir(packet_id: str) -> Path:
    return REVIEW_PACKET_PENDING_ROOT / packet_id


def archived_packet_dir(packet_id: str) -> Path:
    return REVIEW_PACKET_ARCHIVE_ROOT / packet_id


def packet_status_file(job_id: str) -> Path:
    return STATUS_DIR / f"{job_id}.json"


def packet_log_file(job_id: str) -> Path:
    return LOG_DIR / f"{job_id}.log"


def packet_case_ids_from_csv(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [row["case_id"] for row in csv.DictReader(handle)]


def render_cleanup_command(plan: PacketPlan) -> str:
    case_flags = " ".join(f"--case-id {case_id}" for case_id in plan.case_ids)
    return (
        f"{PYTHON} -m eval.attentional_v2.generate_revision_replacement_packet "
        f"--dataset-id {plan.dataset_id} --family excerpt_cases --storage-mode local-only "
        f"--packet-id {plan.packet_id} {case_flags} "
        f"&& {PYTHON} -m eval.attentional_v2.run_case_design_audit --packet-id {plan.packet_id} --max-workers 1 "
        f"&& {PYTHON} -m eval.attentional_v2.auto_review_packet --packet-id {plan.packet_id} "
        f"&& {PYTHON} -m eval.attentional_v2.import_dataset_review_packet --packet-id {plan.packet_id} --review-origin llm --archive "
        f"&& {PYTHON} -m eval.attentional_v2.build_review_queue_summary"
    )


def current_llm_profile_summary() -> dict[str, Any]:
    registry = get_llm_registry()
    runtime = registry.get_profile(DEFAULT_RUNTIME_PROFILE_ID)
    dataset = registry.get_profile(DEFAULT_DATASET_REVIEW_PROFILE_ID)
    return {
        "source": registry.source,
        "runtime_provider": runtime.provider_id,
        "runtime_model": runtime.model,
        "dataset_provider": dataset.provider_id,
        "dataset_model": dataset.model,
        "same_provider": runtime.provider_id == dataset.provider_id and runtime.model == dataset.model,
        "runtime_concurrency": runtime.max_concurrency,
        "dataset_concurrency": dataset.max_concurrency,
    }


def materialize_or_validate_packet(plan: PacketPlan, *, log_path: Path) -> dict[str, Any]:
    pending_dir = packet_dir(plan.packet_id)
    if pending_dir.exists():
        append_log(log_path, f"Packet already exists, validating: {pending_dir}")
    else:
        command = [
            str(PYTHON),
            "-m",
            "eval.attentional_v2.generate_revision_replacement_packet",
            "--dataset-id",
            plan.dataset_id,
            "--family",
            "excerpt_cases",
            "--storage-mode",
            "local-only",
            "--packet-id",
            plan.packet_id,
        ]
        for case_id in plan.case_ids:
            command.extend(["--case-id", case_id])
        run_logged(command, log_path=log_path)

    manifest = read_json(pending_dir / "packet_manifest.json")
    manifest_case_ids = set(manifest.get("selection_filters", {}).get("case_ids", []))
    csv_case_ids = packet_case_ids_from_csv(pending_dir / "cases.review.csv")
    expected_case_ids = set(plan.case_ids)
    if manifest_case_ids != expected_case_ids:
        raise RuntimeError(f"{plan.packet_id}: manifest case ids do not match expected ids")
    if set(csv_case_ids) != expected_case_ids or len(csv_case_ids) != len(plan.case_ids):
        raise RuntimeError(f"{plan.packet_id}: review CSV case ids do not match expected ids")
    if set(csv_case_ids) & set(plan.parked_case_ids):
        raise RuntimeError(f"{plan.packet_id}: parked cases leaked into the ready packet")

    return {
        "packet_id": plan.packet_id,
        "packet_dir": str(pending_dir),
        "case_ids": csv_case_ids,
        "case_count": len(csv_case_ids),
    }


def lane_a_complete() -> bool:
    return all(path.exists() for path in LANE_A_EXPECTED_OUTPUTS)


def lane_a_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    for pattern in LANE_A_TRACK_PATTERNS:
        matches = sorted(LANE_A_RUN_DIR.glob(pattern))
        latest_mtime = max((path.stat().st_mtime for path in matches), default=0.0)
        latest_path = ""
        if matches:
            latest_path = str(max(matches, key=lambda item: item.stat().st_mtime))
        snapshot[pattern] = {
            "count": len(matches),
            "latest_mtime": latest_mtime,
            "latest_path": latest_path,
        }
    return snapshot


def snapshot_changed(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    for key, current_value in current.items():
        previous_value = previous.get(key, {})
        if previous_value.get("count") != current_value.get("count"):
            return True
        if previous_value.get("latest_mtime") != current_value.get("latest_mtime"):
            return True
    return False


def lane_a_pid_alive() -> bool:
    record = get_active_job(LANE_A_JOB_ID, root=ROOT)
    pid = record.get("pid") if isinstance(record, dict) else None
    return process_is_alive(pid if isinstance(pid, int) else None)


def refresh_lane_a_observation(log_path: Path) -> dict[str, Any]:
    command = [str(PYTHON), "scripts/check_background_jobs.py", "--job-id", LANE_A_JOB_ID, "--run-check-commands"]
    completed = run_logged(command, log_path=log_path)
    payload = json.loads(completed.stdout)
    jobs = payload.get("jobs", [])
    return jobs[0] if jobs else {}


def build_survivor_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed_rows = [row for row in rows if str(row.get("benchmark_status", "")).strip() == "reviewed_active"]
    by_role = Counter(str(row.get("selection_role", "unknown")) for row in reviewed_rows)
    by_source: dict[str, dict[str, Any]] = {}
    for row in reviewed_rows:
        source_id = str(row.get("source_id", ""))
        source_entry = by_source.setdefault(
            source_id,
            {
                "source_id": source_id,
                "book_title": str(row.get("book_title", "")),
                "case_ids": [],
                "roles": Counter(),
            },
        )
        source_entry["case_ids"].append(str(row.get("case_id", "")))
        source_entry["roles"][str(row.get("selection_role", "unknown"))] += 1

    ordered_sources = []
    for source_id in sorted(by_source):
        entry = by_source[source_id]
        ordered_sources.append(
            {
                "source_id": source_id,
                "book_title": entry["book_title"],
                "case_ids": sorted(entry["case_ids"]),
                "roles": dict(sorted(entry["roles"].items())),
            }
        )

    reviewed_rows_sorted = sorted(reviewed_rows, key=lambda row: str(row.get("case_id", "")))
    return {
        "count": len(reviewed_rows_sorted),
        "by_role": dict(sorted(by_role.items())),
        "by_source": ordered_sources,
        "cases": [
            {
                "case_id": str(row.get("case_id", "")),
                "source_id": str(row.get("source_id", "")),
                "book_title": str(row.get("book_title", "")),
                "selection_role": str(row.get("selection_role", "")),
                "benchmark_status": str(row.get("benchmark_status", "")),
            }
            for row in reviewed_rows_sorted
        ],
    }


def build_precleanup_scratch(*, log_path: Path) -> dict[str, Any]:
    chapter_sanity = read_json(CHAPTER_SANITY_RESULTS_JSON)
    language_payload: dict[str, Any] = {}
    for language, dataset_id in (
        ("en", "attentional_v2_private_library_excerpt_en_v2"),
        ("zh", "attentional_v2_private_library_excerpt_zh_v2"),
    ):
        language_payload[language] = build_survivor_summary(load_dataset_rows(dataset_id))

    payload = {
        "generated_at": utc_now(),
        "round_id": "private_library_promotion_round2_precleanup_draft",
        "lane_a_gate": {
            "job_id": LANE_A_JOB_ID,
            "run_dir": str(LANE_A_RUN_DIR),
            "expected_outputs": [str(path) for path in LANE_A_EXPECTED_OUTPUTS],
        },
        "llm_profiles": current_llm_profile_summary(),
        "survivors": language_payload,
        "chapter_constraints": {
            "en": {
                "eligible_count": len(chapter_sanity["languages"]["en"]["promote_next"]),
                "eligible_ids": list(chapter_sanity["languages"]["en"]["promote_next"]),
            },
            "zh": {
                "eligible_count": len(chapter_sanity["languages"]["zh"]["promote_next"]),
                "eligible_ids": list(chapter_sanity["languages"]["zh"]["promote_next"]),
            },
        },
        "ready_cleanup_packets": {
            plan.language: {
                "packet_id": plan.packet_id,
                "case_ids": list(plan.case_ids),
            }
            for plan in PACKET_PLANS
        },
        "parked_backlog": PARKED_BACKLOG,
    }

    lines = [
        "# Private-Library Promotion Round2 Pre-Cleanup Draft",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- lane_a_job_id: `{LANE_A_JOB_ID}`",
        f"- llm_profile_source: `{payload['llm_profiles']['source']}`",
        f"- shared_provider_model: `{payload['llm_profiles']['dataset_provider']}` / `{payload['llm_profiles']['dataset_model']}`",
        "",
        "## Live Survivors",
    ]
    for language in ("en", "zh"):
        summary = payload["survivors"][language]
        lines.extend(
            [
                f"### {language.upper()}",
                f"- reviewed_active: `{summary['count']}`",
                f"- by_role: `{json.dumps(summary['by_role'], ensure_ascii=False, sort_keys=True)}`",
                "",
            ]
        )
        for source in summary["by_source"]:
            lines.append(
                f"- `{source['source_id']}` | `{source['book_title']}` | roles `{json.dumps(source['roles'], ensure_ascii=False, sort_keys=True)}` | case_ids `{', '.join(source['case_ids'])}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Chapter Constraints",
            f"- English eligible chapters: `{len(payload['chapter_constraints']['en']['eligible_ids'])}`",
            f"- Chinese eligible chapters: `{len(payload['chapter_constraints']['zh']['eligible_ids'])}`",
            "",
            "## Ready Cleanup Packets",
        ]
    )
    for plan in PACKET_PLANS:
        lines.append(f"- `{plan.packet_id}`: `{', '.join(plan.case_ids)}`")
    lines.extend(["", "## Parked Backlog"])
    for language in ("en", "zh"):
        lines.append(f"### {language.upper()}")
        for entry in PARKED_BACKLOG[language]:
            lines.append(
                f"- `{entry['case_id']}` | `{entry['source_id']}` | family `{entry['problem_family']}` | status `{entry['benchmark_status']}`"
            )
        lines.append("")

    write_json(PRE_CLEANUP_DRAFT_JSON, payload)
    write_text(PRE_CLEANUP_DRAFT_MD, "\n".join(lines))
    append_log(log_path, f"Wrote pre-cleanup draft scratch: {PRE_CLEANUP_DRAFT_JSON}")
    return payload


def prepare_ready_subset_packets(*, log_path: Path) -> dict[str, Any]:
    scratch = build_precleanup_scratch(log_path=log_path)
    packets = {}
    for plan in PACKET_PLANS:
        packets[plan.language] = materialize_or_validate_packet(plan, log_path=log_path)
    run_logged([str(PYTHON), "-m", "eval.attentional_v2.build_review_queue_summary"], log_path=log_path)
    return {"scratch": scratch, "packets": packets}


def register_cleanup_job(plan: PacketPlan) -> tuple[Path, Path]:
    status_file = packet_status_file(plan.cleanup_job_id)
    log_file = packet_log_file(plan.cleanup_job_id)
    archived_import_summary = archived_packet_dir(plan.packet_id) / "import_summary.json"
    write_status(
        status_file,
        "registered",
        packet_id=plan.packet_id,
        language=plan.language,
        phase="queued",
        case_ids=list(plan.case_ids),
    )
    upsert_background_job(
        job_id=plan.cleanup_job_id,
        root=ROOT,
        task_ref="execution-tracker#private-library-round3-cleanup",
        lane="dataset_growth",
        purpose=f"Round-3 ready-subset cleanup pipeline ({plan.language.upper()})",
        command=render_cleanup_command(plan),
        cwd=str(ROOT),
        pid=os.getpid(),
        run_dir=str(packet_dir(plan.packet_id)),
        status_file=str(status_file),
        log_file=str(log_file),
        expected_outputs=[str(archived_import_summary)],
        check_command=f'test -f "{archived_import_summary}" && echo completed || tail -n 40 "{log_file}"',
        next_check_hint="Wait for import_summary.json under archive/ then archive the job.",
        decision_if_success="Refresh post-cleanup reviewed_active survivors and the promotion round-2 draft.",
        decision_if_failure="Inspect the packet log and the packet-specific audit/adjudication artifacts before retrying.",
        status="registered",
        notes="Managed by private_library_cleanup_round3.py after the Lane A gate run completes.",
    )
    return status_file, log_file


def archive_registered_job(job_id: str) -> None:
    refresh_background_jobs(root=ROOT, job_ids=[job_id], archive_terminal=True)


def run_cleanup_pipeline(plan: PacketPlan, *, orchestrator_log: Path) -> None:
    status_file, log_file = register_cleanup_job(plan)
    pending_dir = packet_dir(plan.packet_id)
    write_status(
        status_file,
        "running",
        packet_id=plan.packet_id,
        language=plan.language,
        phase="validating_packet",
        case_ids=list(plan.case_ids),
    )
    try:
        materialize_or_validate_packet(plan, log_path=orchestrator_log)
        pending_dir = packet_dir(plan.packet_id)
        upsert_background_job(job_id=plan.cleanup_job_id, root=ROOT, run_dir=str(pending_dir), status="running", pid=os.getpid())

        steps = [
            (
                "audit",
                [str(PYTHON), "-m", "eval.attentional_v2.run_case_design_audit", "--packet-id", plan.packet_id, "--max-workers", "1"],
            ),
            (
                "adjudication",
                [str(PYTHON), "-m", "eval.attentional_v2.auto_review_packet", "--packet-id", plan.packet_id],
            ),
            (
                "import",
                [
                    str(PYTHON),
                    "-m",
                    "eval.attentional_v2.import_dataset_review_packet",
                    "--packet-id",
                    plan.packet_id,
                    "--review-origin",
                    "llm",
                    "--archive",
                ],
            ),
            ("queue_summary", [str(PYTHON), "-m", "eval.attentional_v2.build_review_queue_summary"]),
        ]
        for phase, command in steps:
            write_status(
                status_file,
                "running",
                packet_id=plan.packet_id,
                language=plan.language,
                phase=phase,
                case_ids=list(plan.case_ids),
            )
            run_logged(command, log_path=log_file)

        import_summary = archived_packet_dir(plan.packet_id) / "import_summary.json"
        write_status(
            status_file,
            "completed",
            packet_id=plan.packet_id,
            language=plan.language,
            phase="completed",
            import_summary_path=str(import_summary),
        )
        upsert_background_job(job_id=plan.cleanup_job_id, root=ROOT, status="completed", run_dir=str(archived_packet_dir(plan.packet_id)))
        archive_registered_job(plan.cleanup_job_id)
        append_log(orchestrator_log, f"Completed cleanup pipeline: {plan.packet_id}")
    except Exception as exc:
        write_status(
            status_file,
            "failed",
            packet_id=plan.packet_id,
            language=plan.language,
            phase="failed",
            error=str(exc),
        )
        upsert_background_job(job_id=plan.cleanup_job_id, root=ROOT, status="failed")
        archive_registered_job(plan.cleanup_job_id)
        append_log(orchestrator_log, f"Cleanup pipeline failed for {plan.packet_id}: {exc}")
        raise


def replace_or_append_block(path: Path, *, start_marker: str, end_marker: str, body: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"{start_marker}\n{body.rstrip()}\n{end_marker}\n"
    if start_marker in existing and end_marker in existing:
        prefix, remainder = existing.split(start_marker, 1)
        _, suffix = remainder.split(end_marker, 1)
        new_text = f"{prefix}{block}{suffix.lstrip()}"
    else:
        separator = "\n" if existing.endswith("\n") else "\n\n"
        new_text = f"{existing.rstrip()}{separator}{block}"
    write_text(path, new_text)


def current_reviewed_active_summary() -> dict[str, Any]:
    chapter_sanity = read_json(CHAPTER_SANITY_RESULTS_JSON)
    payload = {
        "generated_at": utc_now(),
        "round_id": "private_library_promotion_round2",
        "source_of_truth": {
            "en": str(ROOT / "state" / "eval_local_datasets" / "excerpt_cases" / "attentional_v2_private_library_excerpt_en_v2" / "cases.jsonl"),
            "zh": str(ROOT / "state" / "eval_local_datasets" / "excerpt_cases" / "attentional_v2_private_library_excerpt_zh_v2" / "cases.jsonl"),
        },
        "cleanup_packets": {},
        "excerpt_survivors": {
            "en": build_survivor_summary(load_dataset_rows("attentional_v2_private_library_excerpt_en_v2")),
            "zh": build_survivor_summary(load_dataset_rows("attentional_v2_private_library_excerpt_zh_v2")),
        },
        "chapter_constraints": {
            "en": {
                "eligible_count": len(chapter_sanity["languages"]["en"]["promote_next"]),
                "eligible_ids": list(chapter_sanity["languages"]["en"]["promote_next"]),
                "basis": str(CHAPTER_SANITY_RESULTS_JSON),
            },
            "zh": {
                "eligible_count": len(chapter_sanity["languages"]["zh"]["promote_next"]),
                "eligible_ids": list(chapter_sanity["languages"]["zh"]["promote_next"]),
                "basis": str(CHAPTER_SANITY_RESULTS_JSON),
            },
        },
        "parked_fix_backlog": PARKED_BACKLOG,
    }

    for plan in PACKET_PLANS:
        archive_dir = archived_packet_dir(plan.packet_id)
        packet_entry: dict[str, Any] = {
            "packet_id": plan.packet_id,
            "archive_dir": str(archive_dir),
        }
        import_summary = archive_dir / "import_summary.json"
        if import_summary.exists():
            packet_entry["import_summary"] = read_json(import_summary)
        payload["cleanup_packets"][plan.language] = packet_entry

    return payload


def write_round2_promotion_draft(payload: dict[str, Any]) -> None:
    lines = [
        "# Private-Library Promotion Round2",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        "- source_of_truth:",
        f"  - EN: `{payload['source_of_truth']['en']}`",
        f"  - ZH: `{payload['source_of_truth']['zh']}`",
        "",
        "## Cleanup Packet Outcomes",
    ]
    for language in ("en", "zh"):
        entry = payload["cleanup_packets"].get(language, {})
        import_summary = entry.get("import_summary", {})
        if import_summary:
            lines.extend(
                [
                    f"### {language.upper()}",
                    f"- packet_id: `{entry['packet_id']}`",
                    f"- archive_dir: `{entry['archive_dir']}`",
                    f"- keep: `{import_summary.get('action_counts', {}).get('keep', 0)}`",
                    f"- revise: `{import_summary.get('action_counts', {}).get('revise', 0)}`",
                    f"- drop: `{import_summary.get('action_counts', {}).get('drop', 0)}`",
                    "",
                ]
            )
        else:
            lines.extend([f"### {language.upper()}", "- cleanup packet not archived yet", ""])

    lines.append("## Excerpt Survivors")
    for language in ("en", "zh"):
        summary = payload["excerpt_survivors"][language]
        lines.extend(
            [
                f"### {language.upper()}",
                f"- reviewed_active: `{summary['count']}`",
                f"- by_role: `{json.dumps(summary['by_role'], ensure_ascii=False, sort_keys=True)}`",
                "",
            ]
        )
        for source in summary["by_source"]:
            lines.append(
                f"- `{source['source_id']}` | `{source['book_title']}` | roles `{json.dumps(source['roles'], ensure_ascii=False, sort_keys=True)}` | case_ids `{', '.join(source['case_ids'])}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Chapter Constraints",
            f"- English chapter lane: keep the current `{payload['chapter_constraints']['en']['eligible_count']}` eligible chapters",
            f"- Chinese chapter lane: keep the current `{payload['chapter_constraints']['zh']['eligible_count']}` eligible chapters",
            "",
            "### English Eligible Chapter IDs",
            *[f"- `{case_id}`" for case_id in payload["chapter_constraints"]["en"]["eligible_ids"]],
            "",
            "### Chinese Eligible Chapter IDs",
            *[f"- `{case_id}`" for case_id in payload["chapter_constraints"]["zh"]["eligible_ids"]],
            "",
            "## Parked Fix Backlog",
        ]
    )
    for language in ("en", "zh"):
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in payload["parked_fix_backlog"][language]:
            grouped[entry["source_id"]].append(entry)
        lines.append(f"### {language.upper()}")
        for source_id in sorted(grouped):
            source_entries = grouped[source_id]
            book_title = source_entries[0]["book_title"]
            families = ", ".join(sorted({entry["problem_family"] for entry in source_entries}))
            case_ids = ", ".join(entry["case_id"] for entry in source_entries)
            lines.append(f"- `{source_id}` | `{book_title}` | families `{families}` | case_ids `{case_ids}`")
        lines.append("")

    write_json(ROUND2_DRAFT_JSON, payload)
    write_text(ROUND2_DRAFT_MD, "\n".join(lines))


def update_tracking_docs(payload: dict[str, Any]) -> None:
    en_count = payload["excerpt_survivors"]["en"]["count"]
    zh_count = payload["excerpt_survivors"]["zh"]["count"]
    en_keep = payload["cleanup_packets"].get("en", {}).get("import_summary", {}).get("action_counts", {}).get("keep", 0)
    zh_keep = payload["cleanup_packets"].get("zh", {}).get("import_summary", {}).get("action_counts", {}).get("keep", 0)

    tracker_body = "\n".join(
        [
            "## `2026-03-28` Private-Library Cleanup Round3",
            f"- Waited for Lane A completion at `{LANE_A_RUN_DIR}` before starting any LLM-heavy dataset work.",
            "- Completed the ready-subset cleanup pipelines serially:",
            f"  - EN packet: `{PACKET_PLANS[0].packet_id}` (`keep {en_keep}`)",
            f"  - ZH packet: `{PACKET_PLANS[1].packet_id}` (`keep {zh_keep}`)",
            f"- Post-cleanup reviewed-active excerpt counts now stand at EN `{en_count}` and ZH `{zh_count}` in the live local-only datasets.",
            "- Wrote the draft promotion artifacts for the next decision point:",
            f"  - `{ROUND2_DRAFT_MD}`",
            f"  - `{ROUND2_DRAFT_JSON}`",
            f"- Chapter constraint remains EN `{payload['chapter_constraints']['en']['eligible_count']}` vs ZH `{payload['chapter_constraints']['zh']['eligible_count']}` eligible chapter candidates.",
        ]
    )
    replace_or_append_block(
        EXECUTION_TRACKER,
        start_marker="<!-- BEGIN private_library_cleanup_round3_20260328 -->",
        end_marker="<!-- END private_library_cleanup_round3_20260328 -->",
        body=tracker_body,
    )

    round1_body = "\n".join(
        [
            "## Round-3 Cleanup And Round-2 Draft",
            "- The ready-subset cleanup packets are now completed and archived:",
            f"  - EN: `{archived_packet_dir(PACKET_PLANS[0].packet_id)}`",
            f"  - ZH: `{archived_packet_dir(PACKET_PLANS[1].packet_id)}`",
            f"- Correction to the earlier round-1 interpretation: `zhangzhongmou_zizhuan_private_zh__4__seed_1` is now `reviewed_active` in the live local-only excerpt dataset, so the old round-1 drop note remains historical packet output only and is no longer the current survivor truth.",
            "- The next curated decision artifact is now the round-2 draft:",
            f"  - `{ROUND2_DRAFT_MD}`",
            f"  - `{ROUND2_DRAFT_JSON}`",
            "- Do not materialize a new curated promotion packet in this slice; use the round-2 draft plus the parked backlog list for the next decision point.",
        ]
    )
    replace_or_append_block(
        ROUND1_EXECUTION_DOC,
        start_marker="<!-- BEGIN private_library_cleanup_round3_20260328 -->",
        end_marker="<!-- END private_library_cleanup_round3_20260328 -->",
        body=round1_body,
    )

    handoff_body = "\n".join(
        [
            "## `2026-03-28` Private-Library Cleanup Round3 Update",
            f"- Lane A is no longer the blocker for private-library cleanup; the gated cleanup pass waited for `{LANE_A_RUN_ID}` to finish first.",
            "- The ready-subset bilingual cleanup packets are now fully processed and archived.",
            f"- Live local-only excerpt survivors now stand at EN `{en_count}` and ZH `{zh_count}`.",
            f"- The next benchmark-growth decision should start from `{ROUND2_DRAFT_MD}` rather than from the older round-1 execution note.",
            "- The parked backlog remains explicitly deferred for a later deterministic/manual fix pass.",
        ]
    )
    replace_or_append_block(
        AGENT_HANDOFF,
        start_marker="<!-- BEGIN private_library_cleanup_round3_20260328 -->",
        end_marker="<!-- END private_library_cleanup_round3_20260328 -->",
        body=handoff_body,
    )


def wait_for_lane_a(*, log_path: Path) -> None:
    if lane_a_complete():
        append_log(log_path, "Lane A already completed before wait loop.")
        return

    append_log(log_path, f"Waiting for Lane A completion: {LANE_A_RUN_DIR}")
    previous_snapshot = lane_a_snapshot()
    last_progress_at = time.time()
    next_check_at = 0.0
    stall_reported = False

    while True:
        if lane_a_complete():
            append_log(log_path, "Lane A outputs detected; leaving wait loop.")
            return

        now = time.time()
        if now >= next_check_at:
            observation = refresh_lane_a_observation(log_path)
            write_status(
                ORCHESTRATOR_STATUS_FILE,
                "running",
                phase="waiting_for_lane_a",
                lane_a_observation=observation,
                last_progress_at=last_progress_at,
            )
            next_check_at = now + CHECK_REFRESH_SECONDS

        current_snapshot = lane_a_snapshot()
        if snapshot_changed(previous_snapshot, current_snapshot):
            last_progress_at = now
            previous_snapshot = current_snapshot
            stall_reported = False
            write_status(
                ORCHESTRATOR_STATUS_FILE,
                "running",
                phase="waiting_for_lane_a",
                last_progress_at=last_progress_at,
                lane_a_snapshot=current_snapshot,
            )
        else:
            idle_seconds = now - last_progress_at
            if lane_a_pid_alive() and idle_seconds >= STALL_SECONDS and not stall_reported:
                stall_reported = True
                append_log(
                    log_path,
                    f"Lane A stall candidate: no tracked artifacts advanced for {int(idle_seconds)} seconds while pid remains alive.",
                )
                write_status(
                    ORCHESTRATOR_STATUS_FILE,
                    "running",
                    phase="waiting_for_lane_a",
                    lane_a_progress="stall_candidate",
                    idle_seconds=int(idle_seconds),
                    lane_a_snapshot=current_snapshot,
                )
        time.sleep(POLL_SECONDS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", help="Only materialize/validate packets and write pre-cleanup scratch notes.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_status(
        ORCHESTRATOR_STATUS_FILE,
        "running",
        phase=PREPARE_ONLY_NOTE if args.prepare_only else "preparing",
        pid=os.getpid(),
        llm_profiles=current_llm_profile_summary(),
    )
    append_log(ORCHESTRATOR_LOG_FILE, "Starting private-library cleanup round3 orchestration.")

    try:
        prepare_ready_subset_packets(log_path=ORCHESTRATOR_LOG_FILE)
        if args.prepare_only:
            write_status(ORCHESTRATOR_STATUS_FILE, "completed", phase=PREPARE_ONLY_NOTE, prepared_only=True)
            append_log(ORCHESTRATOR_LOG_FILE, "Prepare-only mode completed.")
            return 0

        wait_for_lane_a(log_path=ORCHESTRATOR_LOG_FILE)

        for plan in PACKET_PLANS:
            write_status(
                ORCHESTRATOR_STATUS_FILE,
                "running",
                phase=f"cleanup_{plan.language}",
                packet_id=plan.packet_id,
            )
            run_cleanup_pipeline(plan, orchestrator_log=ORCHESTRATOR_LOG_FILE)

        payload = current_reviewed_active_summary()
        write_round2_promotion_draft(payload)
        update_tracking_docs(payload)
        write_status(
            ORCHESTRATOR_STATUS_FILE,
            "completed",
            phase="completed",
            round2_draft_md=str(ROUND2_DRAFT_MD),
            round2_draft_json=str(ROUND2_DRAFT_JSON),
        )
        append_log(ORCHESTRATOR_LOG_FILE, "Round-3 cleanup orchestration completed successfully.")
        return 0
    except Exception as exc:
        write_status(ORCHESTRATOR_STATUS_FILE, "failed", phase="failed", error=str(exc))
        append_log(ORCHESTRATOR_LOG_FILE, f"Orchestration failed: {exc}")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
