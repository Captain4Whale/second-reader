"""User-authorized C-only recovery: at most three fresh attempts, first success wins."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import run_context_scope_digest as experiment
from . import run_whole_book_digest as single
from .context_scope_review import render_packet

ORIGINAL = experiment.DEFAULT_RUN_DIR
RUN_ID = "xidaduo_context_scope_c_retry_20260913"
JOB_ID = f"bgjob_{RUN_ID}"
ROOT = single.BACKEND_ROOT / "state/experiments" / RUN_ID
LIMIT = 3
RETRYABLE = {"llm_timeout", "network_blocked", "llm_quota"}


def update_ledger(root: Path, status: str, results: list[dict]) -> None:
    from scripts import update_evaluation_run_ledger as ledger

    def relative(path: Path) -> str:
        return str(path.relative_to(single.BACKEND_ROOT.parent))

    summary_paths = {"manifest": relative(root / "manifest.json")}
    reports = []
    for name in ("summary.json", "comparison/summary.json"):
        if (root / name).exists():
            summary_paths[name] = relative(root / name)
    for name in (
        "retry-summary.md",
        "comparison/review.md",
        "comparison/execution-summary.md",
    ):
        if (root / name).exists():
            reports.append(relative(root / name))
    entry = {
        "run_id": RUN_ID,
        "date": "2026-09-13",
        "surface": "context_scope_digest_retry",
        "lane": "mechanism_eval",
        "status": status,
        "mechanisms": ["attentional_v2"],
        "dataset_or_manifest": [relative(root / "manifest.json")],
        "run_dir": relative(root),
        "summary_paths": summary_paths,
        "job_ids": [JOB_ID],
        "report_paths": reports,
        "catalog_status": "not_cataloged",
        "notes": "User explicitly authorized retrying failed C. At most three additional C-only requests, serial, stop at the first structurally complete response; only transport/quota failures permit another attempt. Exact original C packet/settings, no repair or hidden gateway retries, no A/B rerun or judge. Original failure remains intact. This is operational recovery, not three quality samples or selection of the best output.",
        "metadata": {
            "original_run_id": experiment.RUN_ID,
            "attempt_limit": LIMIT,
            "attempts": results,
        },
    }
    ledger.write_markdown_ledger(ledger.upsert_ledger_entry(entry))
    subprocess.run(
        [sys.executable, str(Path(ledger.__file__)), "--check"],
        check=True,
        capture_output=True,
    )


def prepare(root: Path) -> dict:
    original = experiment.verify_condition(ORIGINAL / "C")
    if single.read_json(ORIGINAL / "C/summary.json")["status"] != "failed":
        raise ValueError("Only the failed original C is authorized for recovery")
    root.mkdir(parents=True, exist_ok=False)
    frozen = {}
    for number in range(1, LIMIT + 1):
        path = root / f"attempt-{number}" / "C"
        path.mkdir(parents=True)
        for name in ("full-source.json", "target-source.json"):
            shutil.copyfile(ORIGINAL / name, path.parent / name)
        for name in original["artifact_hashes"]:
            shutil.copyfile(ORIGINAL / "C" / name, path / name)
        manifest = {
            **original,
            "run_id": f"{RUN_ID}_{number}",
            "job_id": JOB_ID,
            "prepared_at": single.now(),
            "retry_of": original["run_id"],
            "attempt_number": number,
        }
        single.write_json(path / "manifest.json", manifest)
        experiment.verify_condition(path)
    for path in root.rglob("*"):
        if path.is_file():
            frozen[str(path.relative_to(root))] = single.digest_bytes(path.read_bytes())
    manifest = {
        "run_id": RUN_ID,
        "job_id": JOB_ID,
        "prepared_at": single.now(),
        "original_run": str(ORIGINAL),
        "additional_request_limit": LIMIT,
        "first_success_stops": True,
        "artifact_hashes": frozen,
        "code_hashes": {
            str(Path(m.__file__)): single.digest_bytes(Path(m.__file__).read_bytes())
            for m in (single, experiment)
        },
        "retry_runner_sha256": single.digest_bytes(Path(__file__).read_bytes()),
    }
    single.write_json(root / "manifest.json", manifest)
    single.write_json(root / "status.json", {"status": "prepared"})
    update_ledger(root, "planned", [])
    return manifest


def verify(root: Path) -> None:
    manifest = single.read_json(root / "manifest.json")
    if (
        manifest["additional_request_limit"] != LIMIT
        or not manifest["first_success_stops"]
    ):
        raise ValueError("Retry policy changed")
    for name, digest in manifest["artifact_hashes"].items():
        if single.digest_bytes((root / name).read_bytes()) != digest:
            raise ValueError("Frozen retry input changed")
    for name, digest in manifest["code_hashes"].items():
        if single.digest_bytes(Path(name).read_bytes()) != digest:
            raise ValueError("Frozen runner changed")
    if (
        single.digest_bytes(Path(__file__).read_bytes())
        != manifest["retry_runner_sha256"]
    ):
        raise ValueError("Retry runner changed")
    for number in range(1, LIMIT + 1):
        path = root / f"attempt-{number}" / "C"
        experiment.verify_condition(path)
        if (path / "request.started.json").exists():
            raise ValueError("Retry batch cannot be resumed or relaunched")
        for name in single.read_json(path / "manifest.json")["artifact_hashes"]:
            if (path / name).read_bytes() != (ORIGINAL / "C" / name).read_bytes():
                raise ValueError("Retry differs from the original C input")


def write_review(root: Path, summary: dict) -> None:
    lines = [
        "# C 授权重试记录",
        "",
        "最多追加三次，首次结构完整即停止；未按批注数量或质量挑选结果。",
        "",
        "| 尝试 | 状态 | 耗时（秒） | 错误 |",
        "|---|---|---:|---|",
    ]
    for result in summary["attempts"]:
        lines.append(
            f"| {result['attempt']} | {result['status']} | {result.get('elapsed_seconds', '—')} | {result.get('error', {}).get('problem_code', '—')} |"
        )
    lines.extend(
        [
            "",
            f"本次追加请求数：{summary['application_request_count']}。原 C 失败和 A/B 结果均保留。",
            "",
        ]
    )
    (root / "retry-summary.md").write_text("\n".join(lines))
    selected = summary.get("selected_attempt")
    if selected is None:
        return
    comparison = root / "comparison"
    comparison.mkdir()
    for name in (
        "full-source.json",
        "target-source.json",
        "target-source.md",
        "historical-chapter.json",
        "historical-reference.md",
    ):
        shutil.copyfile(ORIGINAL / name, comparison / name)
    for condition in "AB":
        shutil.copytree(ORIGINAL / condition, comparison / condition)
    shutil.copytree(root / f"attempt-{selected}/C", comparison / "C")
    conditions = {c: single.read_json(comparison / c / "summary.json") for c in "ABC"}
    single.write_json(
        comparison / "summary.json",
        {
            "run_id": RUN_ID,
            "status": "review_pending",
            "conditions": conditions,
            "C_retry_attempt": selected,
            "original_C_failure": str(ORIGINAL / "C/summary.json"),
        },
    )
    render_packet(comparison)
    note = "本页 C 来自用户授权后的首次成功重试；原始 C 调用失败仍保留。此次重新混排编号，旧审阅材料未修改。详见 ../retry-summary.md。\n\n"
    for name in ("review.md", "execution-summary.md"):
        path = comparison / name
        path.write_text(note + path.read_text())


def run(root: Path) -> dict:
    verify(root)
    single.reserve_request(root, RUN_ID)
    started = time.monotonic()
    results = []
    selected = None
    update_ledger(root, "running", results)
    try:
        for number in range(1, LIMIT + 1):
            single.write_json(
                root / "status.json",
                {"status": "running", "attempt": number, "updated_at": single.now()},
            )
            print(f"Starting authorized C retry {number}/{LIMIT}", flush=True)
            result = single.run(
                root / f"attempt-{number}/C",
                prepared_verifier=experiment.verify_condition,
                result_renderer=experiment.render_condition,
            )
            compact = {
                k: result[k]
                for k in (
                    "status",
                    "application_request_count",
                    "counts",
                    "target_counts",
                    "elapsed_seconds",
                    "usage",
                    "error",
                    "response_metadata",
                )
                if k in result
            }
            results.append({"attempt": number, **compact})
            single.write_json(
                root / "summary.json", {"status": "running", "attempts": results}
            )
            update_ledger(root, "running", results)
            print(json.dumps(results[-1], ensure_ascii=False), flush=True)
            if result["status"] == "review_pending":
                selected = number
                break
            if result.get("error", {}).get("problem_code") not in RETRYABLE:
                break
    except Exception as exc:
        results.append(
            {
                "attempt": len(results) + 1,
                "status": "failed",
                "error": {"type": type(exc).__name__},
            }
        )
    status = "review_pending" if selected else "failed"
    summary = {
        "run_id": RUN_ID,
        "status": status,
        "selected_attempt": selected,
        "attempts": results,
        "application_request_count": sum(
            single.read_json(p)["application_request_number"]
            for p in root.glob("attempt-*/C/request.json")
        ),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "completed_at": single.now(),
    }
    single.write_json(root / "summary.json", summary)
    write_review(root, summary)
    update_ledger(root, status, results)
    single.write_json(
        root / "status.json",
        {
            "status": "completed" if selected else "failed",
            "review_status": status,
            "updated_at": single.now(),
        },
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--run", action="store_true")
    args = parser.parse_args()
    result = prepare(ROOT) if args.prepare else run(ROOT)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result.get("status") == "failed")


if __name__ == "__main__":
    raise SystemExit(main())
