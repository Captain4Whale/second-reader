"""Focused tests for process-level product worker leases."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.reading_runtime import job_lease as job_lease_module
from src.reading_runtime.job_lease import (
    DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
    DEFAULT_LEASE_TTL_SECONDS,
    ENV_BOOK_ID,
    ENV_JOB_ID,
    ENV_JOB_KIND,
    ENV_LEASE_GENERATION,
    ENV_LEASE_TOKEN,
    ENV_MECHANISM_KEY,
    ENV_RUN_ATTEMPT_ID,
    ENV_RUNTIME_ROOT,
    JobLeaseConflict,
    JobLeaseLost,
    JobLeaseReadError,
    MAX_JOB_LEASE_BYTES,
    acquire_job_lease,
    assert_current_lease,
    current_lease,
    fence_job_lease,
    guard_book_writer_exclusion,
    grant_from_environment,
    heartbeat_job_lease,
    job_lease_file,
    job_lease_is_valid,
    lease_context,
    lease_context_from_environment,
    lease_environment,
    load_job_lease,
    process_birth_identity,
    sanitized_lease_metadata,
    validate_lease_timing,
)


def test_lease_defaults_and_timing_guard() -> None:
    assert DEFAULT_LEASE_TTL_SECONDS == 45.0
    assert DEFAULT_HEARTBEAT_INTERVAL_SECONDS == 10.0
    validate_lease_timing(ttl_seconds=30, heartbeat_interval_seconds=10)
    with pytest.raises(ValueError, match="at least three times"):
        validate_lease_timing(ttl_seconds=29.9, heartbeat_interval_seconds=10)


def test_current_process_has_a_stable_birth_identity() -> None:
    first = process_birth_identity()
    second = process_birth_identity()

    assert first
    assert first == second


@pytest.mark.skipif(sys.platform != "darwin", reason="Darwin libproc contract")
def test_darwin_birth_identity_distinguishes_processes_started_in_same_second() -> None:
    first = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(1)"])
    second = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(1)"])
    try:
        first_identity = process_birth_identity(first.pid)
        second_identity = process_birth_identity(second.pid)
    finally:
        first.terminate()
        second.terminate()
        first.wait(timeout=2)
        second.wait(timeout=2)

    assert first_identity and first_identity.startswith("darwin-proc-start:")
    assert second_identity and second_identity.startswith("darwin-proc-start:")
    assert first_identity != second_identity


def test_lease_generation_fences_old_attempt_and_never_exposes_token(tmp_path) -> None:
    now = datetime.now(timezone.utc)
    first = acquire_job_lease(
        "job-lease",
        root=tmp_path,
        book_id="book-1",
        job_kind="read",
        mechanism_key="attentional_v2",
        now=now,
    )

    raw_first = load_job_lease("job-lease", root=tmp_path)
    assert job_lease_module.job_lease_file("job-lease", tmp_path).stat().st_mode & 0o777 == 0o600
    metadata = sanitized_lease_metadata(raw_first, now=now)
    assert raw_first["token"] == first.token
    assert "token" not in metadata
    assert metadata["generation"] == 1
    assert metadata["valid"] is True
    with pytest.raises(JobLeaseConflict):
        acquire_job_lease("job-lease", root=tmp_path, now=now + timedelta(seconds=1))

    renewed = heartbeat_job_lease(first, owner_pid=1234, now=now + timedelta(seconds=5))
    assert renewed["owner_pid"] == 1234
    assert job_lease_is_valid(renewed, now=now + timedelta(seconds=6))
    fence_job_lease(
        "job-lease",
        root=tmp_path,
        expected_run_attempt_id=first.run_attempt_id,
        expected_generation=first.generation,
        now=now + timedelta(seconds=7),
    )
    second = acquire_job_lease("job-lease", root=tmp_path, now=now + timedelta(seconds=8))

    assert second.generation == 2
    assert second.run_attempt_id != first.run_attempt_id
    with pytest.raises(JobLeaseLost):
        heartbeat_job_lease(first, owner_pid=1234, now=now + timedelta(seconds=9))


def test_concurrent_acquire_allows_exactly_one_replacement_attempt(tmp_path) -> None:
    initial = acquire_job_lease("job-race", root=tmp_path)
    fence_job_lease(
        "job-race",
        root=tmp_path,
        expected_run_attempt_id=initial.run_attempt_id,
        expected_generation=initial.generation,
    )
    barrier = threading.Barrier(2)

    def _acquire() -> str:
        barrier.wait(timeout=1)
        try:
            return acquire_job_lease("job-race", root=tmp_path).run_attempt_id
        except JobLeaseConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [future.result() for future in [executor.submit(_acquire), executor.submit(_acquire)]]

    assert results.count("conflict") == 1
    assert len([result for result in results if result != "conflict"]) == 1
    assert load_job_lease("job-race", root=tmp_path)["generation"] == 2


def test_corrupt_existing_lease_fails_closed_but_missing_lease_is_distinct(tmp_path) -> None:
    assert load_job_lease("job-missing", root=tmp_path) == {}

    corrupt_path = tmp_path / "state" / "job_registry" / "leases" / "job-corrupt.json"
    corrupt_path.parent.mkdir(parents=True, exist_ok=True)
    corrupt_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(JobLeaseReadError, match="corrupt"):
        load_job_lease("job-corrupt", root=tmp_path)
    with pytest.raises(JobLeaseReadError, match="corrupt"):
        acquire_job_lease("job-corrupt", root=tmp_path)
    assert corrupt_path.read_text(encoding="utf-8") == "{not-json"


def test_job_ids_cannot_escape_the_lease_directory(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    absolute_target = tmp_path / "outside-job"
    invalid_ids: tuple[object, ...] = (
        str(absolute_target),
        "../outside-job",
        "nested/outside-job",
        "nested\\outside-job",
        ".",
        "..",
        " leading-space",
        "control\x00id",
        "control\u0085id",
        True,
    )

    for invalid_job_id in invalid_ids:
        with pytest.raises((TypeError, ValueError)):
            acquire_job_lease(invalid_job_id, root=runtime_root)  # type: ignore[arg-type]

    assert not absolute_target.with_suffix(".lock").exists()
    assert not absolute_target.with_suffix(".json").exists()
    assert not (runtime_root / "state").exists()


def test_transient_lease_read_error_is_not_treated_as_missing(tmp_path, monkeypatch) -> None:
    target = tmp_path / "state" / "job_registry" / "leases" / "job-unreadable.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}", encoding="utf-8")
    original_open = os.open

    def _open(path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if os.fspath(path) in {os.fspath(target), target.name}:
            raise PermissionError("temporary filesystem failure")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", _open)

    with pytest.raises(JobLeaseReadError, match="could not be read safely"):
        load_job_lease("job-unreadable", root=tmp_path)


def test_book_scoped_launch_guard_fails_closed_on_unreadable_sidecar(tmp_path) -> None:
    corrupt_path = tmp_path / "state" / "job_registry" / "leases" / "unknown-job.json"
    corrupt_path.parent.mkdir(parents=True, exist_ok=True)
    corrupt_path.write_text("{}", encoding="utf-8")

    with pytest.raises(JobLeaseReadError, match="missing required fencing fields"):
        acquire_job_lease(
            "job-new",
            root=tmp_path,
            book_id="book-new",
            enforce_book_exclusivity=True,
        )


def test_book_scoped_launch_guard_serializes_different_job_ids(tmp_path) -> None:
    barrier = threading.Barrier(2)

    def _acquire(job_id: str) -> str:
        barrier.wait(timeout=1)
        try:
            return acquire_job_lease(
                job_id,
                root=tmp_path,
                book_id="book-shared",
                enforce_book_exclusivity=True,
            ).job_id
        except JobLeaseConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [
            future.result()
            for future in [
                executor.submit(_acquire, "job-book-a"),
                executor.submit(_acquire, "job-book-b"),
            ]
        ]

    assert results.count("conflict") == 1
    assert len([result for result in results if result != "conflict"]) == 1


def test_book_scoped_launch_guard_blocks_expired_but_live_owner(tmp_path) -> None:
    now = datetime.now(timezone.utc)
    grant = acquire_job_lease(
        "job-live-owner",
        root=tmp_path,
        book_id="book-live-owner",
        ttl_seconds=3,
        heartbeat_interval_seconds=1,
        enforce_book_exclusivity=True,
        now=now,
    )
    heartbeat_job_lease(grant, owner_pid=os.getpid(), ttl_seconds=3, now=now)

    with pytest.raises(JobLeaseConflict, match="not been confirmed stopped"):
        acquire_job_lease(
            "job-replacement",
            root=tmp_path,
            book_id="book-live-owner",
            ttl_seconds=3,
            heartbeat_interval_seconds=1,
            enforce_book_exclusivity=True,
            now=now + timedelta(seconds=4),
        )


def test_book_writer_exclusion_guard_accepts_a_valid_unowned_book(tmp_path) -> None:
    entered = False

    with guard_book_writer_exclusion("book-export", root=tmp_path):
        entered = True

    assert entered is True


@pytest.mark.parametrize("book_id", ["", "   "])
def test_book_writer_exclusion_guard_rejects_empty_book_ids(tmp_path, book_id) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        with guard_book_writer_exclusion(book_id, root=tmp_path):
            pytest.fail("invalid book id entered the writer guard")


@pytest.mark.parametrize("book_id", [None, 1, True, ["book"]])
def test_book_writer_exclusion_guard_rejects_non_string_book_ids(
    tmp_path,
    book_id,
) -> None:
    with pytest.raises(TypeError, match="exact string"):
        with guard_book_writer_exclusion(book_id, root=tmp_path):
            pytest.fail("invalid book id entered the writer guard")


def test_book_writer_exclusion_guard_rejects_string_subclasses(tmp_path) -> None:
    class BookId(str):
        pass

    with pytest.raises(TypeError, match="exact string"):
        with guard_book_writer_exclusion(BookId("book-export"), root=tmp_path):
            pytest.fail("string subclass entered the writer guard")


def test_book_writer_exclusion_guard_conflicts_with_active_valid_lease(tmp_path) -> None:
    acquire_job_lease(
        "job-active-export",
        root=tmp_path,
        book_id="book-export",
        enforce_book_exclusivity=True,
    )

    with pytest.raises(
        JobLeaseConflict,
        match="Book writer exclusion could not be acquired safely",
    ):
        with guard_book_writer_exclusion("book-export", root=tmp_path):
            pytest.fail("active worker lease did not block the writer guard")


def test_book_conflict_scan_serializes_with_sidecar_writer_lock(tmp_path) -> None:
    grant = acquire_job_lease(
        "job-active-export",
        root=tmp_path,
        book_id="book-export",
    )
    writer_entered = threading.Event()
    release_writer = threading.Event()

    def _hold_sidecar_writer_lock() -> None:
        with job_lease_module._locked_job_lease(grant.job_id, tmp_path):
            writer_entered.set()
            assert release_writer.wait(timeout=1)

    def _guard_result() -> str:
        try:
            with guard_book_writer_exclusion("book-export", root=tmp_path):
                return "entered"
        except JobLeaseConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as executor:
        writer = executor.submit(_hold_sidecar_writer_lock)
        assert writer_entered.wait(timeout=1)
        guard = executor.submit(_guard_result)
        with pytest.raises(FutureTimeoutError):
            guard.result(timeout=0.05)
        release_writer.set()
        writer.result(timeout=1)
        assert guard.result(timeout=1) == "conflict"


@pytest.mark.parametrize("sidecar_contents", ["{not-json", "{}"])
def test_book_writer_exclusion_guard_fails_closed_on_malformed_sidecar(
    tmp_path,
    sidecar_contents,
) -> None:
    sidecar = tmp_path / "state" / "job_registry" / "leases" / "unknown.json"
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(sidecar_contents, encoding="utf-8")

    with pytest.raises(
        JobLeaseConflict,
        match="Book writer exclusion could not be acquired safely",
    ):
        with guard_book_writer_exclusion("book-export", root=tmp_path):
            pytest.fail("malformed sidecar did not fail closed")


def test_book_writer_exclusion_guard_rejects_duplicate_lease_keys(tmp_path) -> None:
    grant = acquire_job_lease(
        "job-duplicate-key",
        root=tmp_path,
        book_id="book-export",
    )
    sidecar = job_lease_file(grant.job_id, tmp_path)
    original = sidecar.read_text(encoding="utf-8")
    tampered = original.replace(
        '"book_id": "book-export"',
        '"book_id": "book-export",\n  "book_id": "other"',
        1,
    )
    assert tampered != original
    sidecar.write_text(tampered, encoding="utf-8")

    with pytest.raises(
        JobLeaseConflict,
        match="Book writer exclusion could not be acquired safely",
    ):
        with guard_book_writer_exclusion("book-export", root=tmp_path):
            pytest.fail("duplicate lease keys bypassed the writer guard")


def test_book_writer_exclusion_guard_fails_closed_on_unreadable_sidecar(
    tmp_path,
    monkeypatch,
) -> None:
    sidecar = tmp_path / "state" / "job_registry" / "leases" / "unknown.json"
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text("{}", encoding="utf-8")
    original_open = os.open

    def _open(path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if os.fspath(path) in {os.fspath(sidecar), sidecar.name}:
            raise PermissionError(f"private filesystem detail at {sidecar}")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", _open)

    with pytest.raises(
        JobLeaseConflict,
        match="Book writer exclusion could not be acquired safely",
    ) as error:
        with guard_book_writer_exclusion("book-export", root=tmp_path):
            pytest.fail("unreadable sidecar did not fail closed")
    rendered_traceback = "".join(
        traceback.format_exception(error.type, error.value, error.tb)
    )
    assert error.value.__cause__ is None
    assert "private filesystem detail" not in rendered_traceback
    assert str(sidecar) not in rendered_traceback


@pytest.mark.parametrize("sidecar_kind", ["fifo", "symlink", "oversized"])
def test_book_writer_exclusion_guard_rejects_unsafe_sidecars_without_blocking(
    tmp_path,
    sidecar_kind,
) -> None:
    leases = tmp_path / "state" / "job_registry" / "leases"
    leases.mkdir(parents=True, exist_ok=True)
    sidecar = leases / "unsafe.json"
    if sidecar_kind == "fifo":
        os.mkfifo(sidecar)
    elif sidecar_kind == "symlink":
        target = tmp_path / "private-lease.json"
        target.write_text("{}", encoding="utf-8")
        sidecar.symlink_to(target)
    else:
        sidecar.write_bytes(b" " * (MAX_JOB_LEASE_BYTES + 1))

    script = """
from pathlib import Path
import sys
from src.reading_runtime.job_lease import JobLeaseConflict, guard_book_writer_exclusion
try:
    with guard_book_writer_exclusion("book-export", root=Path(sys.argv[1])):
        pass
except JobLeaseConflict:
    raise SystemExit(0)
raise SystemExit(1)
"""
    completed = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )
    assert completed.returncode == 0
    assert str(sidecar) not in completed.stdout
    assert str(sidecar) not in completed.stderr


def test_book_writer_exclusion_guard_rejects_symlinked_lease_directory(
    tmp_path,
) -> None:
    registry = tmp_path / "state" / "job_registry"
    registry.mkdir(parents=True)
    outside = tmp_path / "outside-leases"
    outside.mkdir()
    (registry / "leases").symlink_to(outside, target_is_directory=True)

    with pytest.raises(JobLeaseReadError, match="opened safely"):
        with guard_book_writer_exclusion("book-export", root=tmp_path):
            pytest.fail("a symlinked lease registry acquired the writer guard")
    assert list(outside.iterdir()) == []


def test_book_writer_exclusion_guard_blocks_book_exclusive_acquisition_until_release(
    tmp_path,
) -> None:
    acquisition_started = threading.Event()

    def _acquire() -> str:
        acquisition_started.set()
        return acquire_job_lease(
            "job-after-export",
            root=tmp_path,
            book_id="book-export",
            enforce_book_exclusivity=True,
        ).job_id

    with ThreadPoolExecutor(max_workers=1) as executor:
        with guard_book_writer_exclusion("book-export", root=tmp_path):
            future = executor.submit(_acquire)
            assert acquisition_started.wait(timeout=1)
            with pytest.raises(FutureTimeoutError):
                future.result(timeout=0.05)
        assert future.result(timeout=1) == "job-after-export"


def test_book_writer_guard_survives_leases_directory_swap_across_processes(
    tmp_path,
) -> None:
    leases = tmp_path / "state" / "job_registry" / "leases"
    leases.mkdir(parents=True)
    parked = leases.with_name("leases-parked")
    replacement = leases.with_name("leases-replacement")
    script = """
from pathlib import Path
import sys
from src.reading_runtime.job_lease import acquire_job_lease
grant = acquire_job_lease(
    "job-after-swap",
    root=Path(sys.argv[1]),
    book_id="book-export",
    enforce_book_exclusivity=True,
)
print(grant.generation)
"""
    process: subprocess.Popen[str] | None = None
    try:
        with guard_book_writer_exclusion("book-export", root=tmp_path):
            leases.rename(parked)
            leases.mkdir()
            process = subprocess.Popen(
                [sys.executable, "-c", script, str(tmp_path)],
                cwd=Path(__file__).resolve().parents[1],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            with pytest.raises(subprocess.TimeoutExpired):
                process.wait(timeout=0.2)
            assert not (leases / "job-after-swap.json").exists()

            leases.rename(replacement)
            parked.rename(leases)

        assert process is not None
        stdout, stderr = process.communicate(timeout=2)
        assert process.returncode == 0
        assert stdout.strip() == "1"
        assert stderr == ""
        assert (leases / "job-after-swap.json").is_file()
        assert list(replacement.iterdir()) == []
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=2)


def test_book_writer_guard_does_not_block_other_book_heartbeat(tmp_path) -> None:
    grant = acquire_job_lease(
        "job-other-book",
        root=tmp_path,
        book_id="book-other",
        enforce_book_exclusivity=True,
    )

    with guard_book_writer_exclusion("book-export", root=tmp_path):
        renewed = heartbeat_job_lease(
            grant,
            owner_pid=os.getpid(),
        )

    assert renewed["state"] == "active"
    assert renewed["owner_pid"] == os.getpid()


def test_book_writer_guard_exposes_explicit_namespace_revalidation(tmp_path) -> None:
    leases = tmp_path / "state" / "job_registry" / "leases"
    leases.mkdir(parents=True)

    with guard_book_writer_exclusion("book-export", root=tmp_path) as exclusion:
        leases.rename(leases.with_name("leases-parked"))
        leases.mkdir()
        with pytest.raises(JobLeaseReadError, match="namespace changed"):
            exclusion.assert_current()


@pytest.mark.parametrize("lease_state", ["active", "fenced"])
def test_book_writer_exclusion_guard_conflicts_when_live_owner_cannot_be_disproved(
    tmp_path,
    lease_state,
) -> None:
    now = datetime.now(timezone.utc)
    grant = acquire_job_lease(
        f"job-{lease_state}-owner",
        root=tmp_path,
        book_id="book-export",
        ttl_seconds=3,
        heartbeat_interval_seconds=1,
        enforce_book_exclusivity=True,
        now=now,
    )
    heartbeat_job_lease(
        grant,
        owner_pid=os.getpid(),
        ttl_seconds=3,
        now=now,
    )
    if lease_state == "fenced":
        fence_job_lease(
            grant.job_id,
            root=tmp_path,
            expected_run_attempt_id=grant.run_attempt_id,
            expected_generation=grant.generation,
            now=now,
        )

    with pytest.raises(
        JobLeaseConflict,
        match="Book writer exclusion could not be acquired safely",
    ):
        with guard_book_writer_exclusion(
            "book-export",
            root=tmp_path,
            now=now + timedelta(seconds=4),
        ):
            pytest.fail("possibly live PID incarnation did not block export")


def test_book_writer_exclusion_guard_blocks_expired_ownerless_starting_grant(
    tmp_path,
) -> None:
    now = datetime.now(timezone.utc)
    grant = acquire_job_lease(
        "job-ownerless-starting",
        root=tmp_path,
        book_id="book-export",
        ttl_seconds=3,
        heartbeat_interval_seconds=1,
        enforce_book_exclusivity=True,
        now=now,
    )

    with pytest.raises(
        JobLeaseConflict,
        match="Book writer exclusion could not be acquired safely",
    ):
        with guard_book_writer_exclusion(
            "book-export",
            root=tmp_path,
            now=now + timedelta(seconds=4),
        ):
            pytest.fail("an ownerless grant could revive inside the writer guard")

    fence_job_lease(
        grant.job_id,
        root=tmp_path,
        expected_run_attempt_id=grant.run_attempt_id,
        expected_generation=grant.generation,
        now=now + timedelta(seconds=4),
    )
    with guard_book_writer_exclusion(
        "book-export",
        root=tmp_path,
        now=now + timedelta(seconds=4),
    ):
        pass


def test_expired_current_grant_can_renew_but_stale_generation_cannot_revive(tmp_path) -> None:
    now = datetime.now(timezone.utc)
    grant = acquire_job_lease(
        "job-expired",
        root=tmp_path,
        ttl_seconds=3,
        heartbeat_interval_seconds=1,
        now=now,
    )
    heartbeat_job_lease(
        grant,
        owner_pid=1234,
        owner_birth_identity="birth-1234",
        ttl_seconds=3,
        now=now,
    )

    renewed = heartbeat_job_lease(
        grant,
        owner_pid=1234,
        owner_birth_identity="birth-1234",
        ttl_seconds=3,
        now=now + timedelta(seconds=4),
    )

    assert job_lease_is_valid(renewed, now=now + timedelta(seconds=5))
    fence_job_lease(
        "job-expired",
        root=tmp_path,
        expected_run_attempt_id=grant.run_attempt_id,
        expected_generation=grant.generation,
        now=now + timedelta(seconds=5),
    )
    replacement = acquire_job_lease(
        "job-expired",
        root=tmp_path,
        ttl_seconds=3,
        heartbeat_interval_seconds=1,
        now=now + timedelta(seconds=6),
    )
    assert replacement.generation == grant.generation + 1

    with pytest.raises(JobLeaseLost):
        heartbeat_job_lease(
            grant,
            owner_pid=1234,
            owner_birth_identity="birth-1234",
            ttl_seconds=3,
            now=now + timedelta(seconds=7),
        )


def test_expired_grant_cannot_renew_under_a_different_owner_identity(tmp_path) -> None:
    now = datetime.now(timezone.utc)
    grant = acquire_job_lease(
        "job-owner-changed",
        root=tmp_path,
        ttl_seconds=3,
        heartbeat_interval_seconds=1,
        now=now,
    )
    heartbeat_job_lease(
        grant,
        owner_pid=1234,
        owner_birth_identity="birth-1234",
        ttl_seconds=3,
        now=now,
    )

    with pytest.raises(JobLeaseLost, match="another PID incarnation"):
        heartbeat_job_lease(
            grant,
            owner_pid=1234,
            owner_birth_identity="birth-reused",
            ttl_seconds=3,
            now=now + timedelta(seconds=4),
        )


def test_matching_owner_reuses_recorded_birth_identity_when_probe_is_unavailable(
    tmp_path,
    monkeypatch,
) -> None:
    grant = acquire_job_lease("job-birth-probe-transient", root=tmp_path)
    heartbeat_job_lease(
        grant,
        owner_pid=os.getpid(),
        owner_birth_identity="known-birth",
    )
    monkeypatch.setattr(job_lease_module, "process_birth_identity", lambda _pid=None: None)

    renewed = heartbeat_job_lease(grant, owner_pid=os.getpid())

    assert renewed["owner_birth_identity"] == "known-birth"


def test_worker_environment_and_current_lease_are_token_free(tmp_path) -> None:
    grant = acquire_job_lease(
        "job-context",
        root=tmp_path,
        book_id="book-context",
        job_kind="parse",
        mechanism_key="iterator_v1",
    )
    environment = lease_environment(grant)

    assert environment == {
        ENV_JOB_ID: "job-context",
        ENV_RUN_ATTEMPT_ID: grant.run_attempt_id,
        ENV_LEASE_GENERATION: "1",
        ENV_LEASE_TOKEN: grant.token,
        ENV_RUNTIME_ROOT: str(tmp_path.resolve()),
        ENV_BOOK_ID: "book-context",
        ENV_JOB_KIND: "parse",
        ENV_MECHANISM_KEY: "iterator_v1",
    }
    reconstructed = grant_from_environment(environment)
    assert reconstructed == grant

    with lease_context(grant, heartbeat_interval_seconds=1, ttl_seconds=3, terminate_on_loss=lambda: None):
        identity = current_lease()
        assert identity is not None
        assert identity.job_id == "job-context"
        assert identity.run_attempt_id == grant.run_attempt_id
        assert identity.book_id == "book-context"
        assert identity.job_kind == "parse"
        assert identity.mechanism_key == "iterator_v1"
        assert identity.generation == 1
        assert identity.valid is True
        assert not hasattr(identity, "token")
        assert assert_current_lease() == identity
        thread_identity: list[object] = []
        thread = threading.Thread(target=lambda: thread_identity.append(assert_current_lease()))
        thread.start()
        thread.join()
        assert thread_identity == [identity]

    assert current_lease() is None
    assert load_job_lease("job-context", root=tmp_path)["state"] == "released"


def test_worker_caches_pid_birth_identity_across_asserts_and_heartbeats(
    tmp_path,
    monkeypatch,
) -> None:
    calls = 0

    def one_success_then_unavailable(pid=None):
        nonlocal calls
        del pid
        calls += 1
        return "stable-worker-birth" if calls == 1 else None

    monkeypatch.setattr(
        job_lease_module,
        "process_birth_identity",
        one_success_then_unavailable,
    )
    grant = acquire_job_lease("job-cached-birth", root=tmp_path)

    with lease_context(
        grant,
        heartbeat_interval_seconds=0.01,
        ttl_seconds=0.03,
        terminate_on_loss=lambda: None,
    ):
        threading.Event().wait(0.04)
        assert assert_current_lease() is not None

    assert calls == 1


def test_worker_adopts_first_late_birth_probe_without_fencing_itself(
    tmp_path,
    monkeypatch,
) -> None:
    calls = 0

    def unavailable_then_stable(_pid=None):
        nonlocal calls
        calls += 1
        return None if calls <= 2 else "late-stable-birth"

    monkeypatch.setattr(
        job_lease_module,
        "process_birth_identity",
        unavailable_then_stable,
    )
    grant = acquire_job_lease("job-late-birth", root=tmp_path)

    with lease_context(
        grant,
        heartbeat_interval_seconds=0.01,
        ttl_seconds=0.05,
        terminate_on_loss=lambda: None,
    ):
        threading.Event().wait(0.035)
        assert assert_current_lease() is not None
        assert load_job_lease("job-late-birth", root=tmp_path)[
            "owner_birth_identity"
        ] == "late-stable-birth"


def test_worker_heartbeat_marks_context_invalid_after_fencing(tmp_path) -> None:
    grant = acquire_job_lease("job-fenced", root=tmp_path)
    terminated = threading.Event()

    with lease_context(
        grant,
        heartbeat_interval_seconds=0.01,
        ttl_seconds=1,
        terminate_on_loss=terminated.set,
    ):
        fence_job_lease(
            "job-fenced",
            root=tmp_path,
            expected_run_attempt_id=grant.run_attempt_id,
            expected_generation=grant.generation,
        )
        assert terminated.wait(timeout=1)
        identity = current_lease()
        assert identity is not None
        assert identity.valid is False
        with pytest.raises(JobLeaseLost):
            assert_current_lease()


def test_worker_tolerates_one_transient_heartbeat_io_failure_within_ttl(
    tmp_path,
    monkeypatch,
) -> None:
    grant = acquire_job_lease("job-transient-heartbeat", root=tmp_path)
    terminated = threading.Event()
    real_heartbeat = job_lease_module.heartbeat_job_lease
    heartbeat_calls = 0

    def one_failure_then_success(*args, **kwargs):
        nonlocal heartbeat_calls
        heartbeat_calls += 1
        # lease_context performs one synchronous heartbeat before starting the
        # background loop. Fail only the first background renewal.
        if heartbeat_calls == 2:
            raise OSError("transient filesystem interruption")
        return real_heartbeat(*args, **kwargs)

    monkeypatch.setattr(job_lease_module, "heartbeat_job_lease", one_failure_then_success)

    with lease_context(
        grant,
        heartbeat_interval_seconds=0.01,
        ttl_seconds=0.05,
        terminate_on_loss=terminated.set,
    ):
        threading.Event().wait(0.035)
        assert heartbeat_calls >= 3
        assert terminated.is_set() is False
        assert assert_current_lease() is not None


def test_normal_exit_never_terminates_for_a_late_blocked_heartbeat(
    tmp_path,
    monkeypatch,
) -> None:
    grant = acquire_job_lease("job-late-heartbeat-exit", root=tmp_path)
    heartbeat_started = threading.Event()
    release_heartbeat = threading.Event()
    heartbeat_finished = threading.Event()
    terminated = threading.Event()
    real_heartbeat = job_lease_module.heartbeat_job_lease
    heartbeat_calls = 0

    def block_background_heartbeat(*args, **kwargs):
        nonlocal heartbeat_calls
        heartbeat_calls += 1
        if heartbeat_calls == 1:
            return real_heartbeat(*args, **kwargs)
        heartbeat_started.set()
        assert release_heartbeat.wait(timeout=3.0)
        try:
            return real_heartbeat(*args, **kwargs)
        finally:
            heartbeat_finished.set()

    monkeypatch.setattr(
        job_lease_module,
        "heartbeat_job_lease",
        block_background_heartbeat,
    )

    with lease_context(
        grant,
        heartbeat_interval_seconds=0.01,
        ttl_seconds=0.03,
        terminate_on_loss=terminated.set,
    ):
        assert heartbeat_started.wait(timeout=1.0)

    assert load_job_lease(grant.job_id, root=tmp_path)["state"] == "released"
    release_heartbeat.set()
    assert heartbeat_finished.wait(timeout=1.0)
    assert terminated.is_set() is False


def test_worker_assert_tolerates_transient_read_error_but_not_corrupt_sidecar(
    tmp_path,
    monkeypatch,
) -> None:
    grant = acquire_job_lease("job-transient-assert", root=tmp_path)
    target = job_lease_module.job_lease_file(grant.job_id, tmp_path)
    original_read_text = Path.read_text
    fail_reads = False

    def conditional_read(path: Path, *args, **kwargs):
        if fail_reads and path == target:
            raise PermissionError("temporary filesystem interruption")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", conditional_read)
    valid_payload = target.read_text(encoding="utf-8")
    with lease_context(
        grant,
        heartbeat_interval_seconds=0.02,
        ttl_seconds=0.06,
        terminate_on_loss=lambda: None,
    ):
        fail_reads = True
        assert assert_current_lease() is not None
        fail_reads = False
        target.write_text("{not-json", encoding="utf-8")
        with pytest.raises(JobLeaseLost, match="cannot be verified safely"):
            assert_current_lease()
        target.write_text(valid_payload, encoding="utf-8")


def test_worker_assert_does_not_grace_an_already_invalidated_context(
    tmp_path,
    monkeypatch,
) -> None:
    grant = acquire_job_lease("job-invalidated-during-read", root=tmp_path)

    with lease_context(
        grant,
        heartbeat_interval_seconds=1,
        ttl_seconds=3,
        terminate_on_loss=lambda: None,
    ):
        state = job_lease_module._PROCESS_LEASE_STATE
        assert state is not None

        def invalidate_then_fail(*_args, **_kwargs):
            state.invalidated.set()
            raise PermissionError("temporary filesystem interruption")

        with monkeypatch.context() as scoped:
            scoped.setattr(
                job_lease_module,
                "_read_job_lease_unlocked",
                invalidate_then_fail,
            )

            with pytest.raises(JobLeaseLost, match="cannot be verified safely"):
                assert_current_lease()


def test_direct_cli_environment_remains_unmanaged() -> None:
    with lease_context_from_environment({}) as identity:
        assert identity is None
        assert current_lease() is None
        assert assert_current_lease() is None

    with pytest.raises(JobLeaseLost, match="incomplete"):
        grant_from_environment({ENV_JOB_ID: "job-incomplete"})

    with pytest.raises(JobLeaseLost, match="job id is invalid"):
        grant_from_environment({ENV_JOB_ID: "../escaped-job"})
