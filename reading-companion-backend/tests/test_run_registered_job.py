"""Tests for the generic registry wrapper launcher."""

from __future__ import annotations

import json
import signal
import subprocess
import sys
import time
from pathlib import Path

from src.reading_runtime.background_job_registry import load_job_record


def test_run_registered_job_marks_successful_command_completed(tmp_path: Path) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    wrapper = backend_root / "scripts" / "run_registered_job.py"
    expected_output = tmp_path / "done.txt"

    command = [
        sys.executable,
        str(wrapper),
        "--root",
        str(tmp_path),
        "--job-id",
        "bgjob_wrapper_success",
        "--task-ref",
        "execution-tracker#wrapper-smoke",
        "--lane",
        "mechanism_eval",
        "--purpose",
        "Wrapper smoke test",
        "--cwd",
        str(tmp_path),
        "--expected-output",
        str(expected_output),
        "--",
        sys.executable,
        "-c",
        (
            "from pathlib import Path; "
            f"Path({str(expected_output)!r}).write_text('ok', encoding='utf-8'); "
            "print('done')"
        ),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["job_id"] == "bgjob_wrapper_success"
    record = load_job_record("bgjob_wrapper_success", root=tmp_path)
    assert record["status"] == "completed"
    assert expected_output.exists()


def test_run_registered_job_marks_signal_termination_abandoned(tmp_path: Path) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    wrapper = backend_root / "scripts" / "run_registered_job.py"

    command = [
        sys.executable,
        str(wrapper),
        "--root",
        str(tmp_path),
        "--job-id",
        "bgjob_wrapper_sigterm",
        "--task-ref",
        "execution-tracker#wrapper-sigterm",
        "--lane",
        "mechanism_eval",
        "--purpose",
        "Wrapper signal test",
        "--cwd",
        str(tmp_path),
        "--",
        sys.executable,
        "-c",
        "import time; time.sleep(30)",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1.0)
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=10)

    record = load_job_record("bgjob_wrapper_sigterm", root=tmp_path)
    assert record["status"] == "abandoned"
    assert record["error"] == "Registry wrapper received signal 15."
    assert record["exit_code"] is not None


def test_launch_registered_job_detached_completes_quick_command(tmp_path: Path) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    launcher = backend_root / "scripts" / "launch_registered_job_detached.py"
    expected_output = tmp_path / "done.txt"

    command = [
        sys.executable,
        str(launcher),
        "--",
        "--root",
        str(tmp_path),
        "--job-id",
        "bgjob_detached_success",
        "--task-ref",
        "execution-tracker#detached-wrapper-smoke",
        "--lane",
        "mechanism_eval",
        "--purpose",
        "Detached wrapper smoke test",
        "--cwd",
        str(tmp_path),
        "--expected-output",
        str(expected_output),
        "--",
        sys.executable,
        "-c",
        (
            "from pathlib import Path; "
            f"Path({str(expected_output)!r}).write_text('ok', encoding='utf-8'); "
            "print('done')"
        ),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["job_id"] == "bgjob_detached_success"

    deadline = time.time() + 10.0
    record = None
    while time.time() < deadline:
        try:
            record = load_job_record("bgjob_detached_success", root=tmp_path)
        except FileNotFoundError:
            time.sleep(0.2)
            continue
        if record["status"] == "completed":
            break
        time.sleep(0.2)
    assert record is not None
    assert record["status"] == "completed"
    assert expected_output.exists()
