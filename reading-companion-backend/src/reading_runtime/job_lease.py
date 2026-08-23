"""Process-level leases for product reading workers.

The lease is intentionally independent from mechanism runtime state.  It fences
duplicate subprocesses without making either reading mechanism responsible for
worker ownership or heartbeat persistence.
"""

from __future__ import annotations

import json
import hashlib
import os
import secrets
import signal
import stat
import subprocess
import sys
import threading
import time
import unicodedata
import uuid
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterator, Mapping

try:  # pragma: no cover - exercised on supported Unix runtimes
    import fcntl
except ImportError:  # pragma: no cover - Windows compatibility fallback
    fcntl = None


ENV_JOB_ID = "READING_COMPANION_JOB_ID"
ENV_RUN_ATTEMPT_ID = "READING_COMPANION_RUN_ATTEMPT_ID"
ENV_LEASE_GENERATION = "READING_COMPANION_LEASE_GENERATION"
ENV_LEASE_TOKEN = "READING_COMPANION_LEASE_TOKEN"
ENV_RUNTIME_ROOT = "READING_COMPANION_RUNTIME_ROOT"
ENV_BOOK_ID = "READING_COMPANION_BOOK_ID"
ENV_JOB_KIND = "READING_COMPANION_JOB_KIND"
ENV_MECHANISM_KEY = "READING_COMPANION_MECHANISM_KEY"

DEFAULT_LEASE_TTL_SECONDS = 45.0
DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 10.0
MAX_JOB_LEASE_BYTES = 256 * 1024
_JOB_LEASE_READ_CHUNK_BYTES = 64 * 1024
ACTIVE_LEASE_STATES = {"starting", "active"}
_MAX_JOB_ID_UTF8_BYTES = 200


class JobLeaseConflict(RuntimeError):
    """Raised when another attempt still owns or may own a worker lease."""


class JobLeaseLost(RuntimeError):
    """Raised when a worker no longer owns the lease generation it received."""


class JobLeaseReadError(RuntimeError):
    """Raised when an existing lease sidecar cannot be read or validated."""


@dataclass(frozen=True)
class JobLeaseGrant:
    """Private launch-time capability used to start one managed worker."""

    job_id: str
    run_attempt_id: str
    generation: int
    token: str = field(repr=False)
    root: Path
    book_id: str = ""
    job_kind: str = ""
    mechanism_key: str = ""


@dataclass(frozen=True)
class CurrentLease:
    """Token-free lease identity available to neutral process consumers."""

    job_id: str
    run_attempt_id: str
    book_id: str
    job_kind: str
    mechanism_key: str
    generation: int
    acquired_at: str
    valid: bool


@dataclass(frozen=True)
class BookWriterExclusion:
    """Live proof that the guarded sidecar namespace is still the pinned one."""

    leases_path: Path = field(repr=False)
    leases_descriptor: int = field(repr=False)

    def assert_current(self) -> None:
        if not _directory_path_matches_descriptor(
            self.leases_path,
            self.leases_descriptor,
        ):
            raise JobLeaseReadError("Lease sidecar namespace changed unexpectedly.")


@dataclass
class _WorkerLeaseState:
    grant: JobLeaseGrant
    acquired_at: str = ""
    owner_birth_identity: str = ""
    invalidated: threading.Event = field(default_factory=threading.Event)
    last_verified_monotonic: float = field(default_factory=time.monotonic)
    verification_ttl_seconds: float = DEFAULT_LEASE_TTL_SECONDS
    verification_guard: threading.Lock = field(default_factory=threading.Lock)


_CURRENT_LEASE: ContextVar[_WorkerLeaseState | None] = ContextVar("reading_companion_current_lease", default=None)
_PROCESS_LEASE_GUARD = threading.Lock()
_PROCESS_LEASE_STATE: _WorkerLeaseState | None = None
_LOCAL_LOCKS_GUARD = threading.Lock()
_LOCAL_LOCKS: dict[str, threading.Lock] = {}


def _timestamp(now: datetime | None = None) -> str:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def job_leases_dir(root: Path | None = None) -> Path:
    """Return the local-only directory containing product worker leases."""

    return (root or Path.cwd()) / "state" / "job_registry" / "leases"


def _validated_job_id(job_id: object) -> str:
    if type(job_id) is not str:
        raise TypeError("Job id must be an exact string.")
    if (
        not job_id
        or job_id != job_id.strip()
        or job_id in {".", ".."}
        or "/" in job_id
        or "\\" in job_id
        or any(unicodedata.category(character) == "Cc" for character in job_id)
    ):
        raise ValueError("Job id is not a safe path leaf.")
    try:
        encoded = job_id.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        raise ValueError("Job id is not valid UTF-8 text.") from None
    if len(encoded) > _MAX_JOB_ID_UTF8_BYTES:
        raise ValueError("Job id is too long.")
    return job_id


def job_lease_file(job_id: str, root: Path | None = None) -> Path:
    """Return the durable lease sidecar for one product job."""

    safe_job_id = _validated_job_id(job_id)
    return job_leases_dir(root) / f"{safe_job_id}.json"


def _darwin_process_birth_identity(pid: int) -> str | None:
    """Read Darwin's microsecond-resolution process start time via libproc."""

    if sys.platform != "darwin":
        return None
    try:
        import ctypes

        class ProcBsdInfo(ctypes.Structure):
            _fields_ = [
                ("pbi_flags", ctypes.c_uint32),
                ("pbi_status", ctypes.c_uint32),
                ("pbi_xstatus", ctypes.c_uint32),
                ("pbi_pid", ctypes.c_uint32),
                ("pbi_ppid", ctypes.c_uint32),
                ("pbi_uid", ctypes.c_uint32),
                ("pbi_gid", ctypes.c_uint32),
                ("pbi_ruid", ctypes.c_uint32),
                ("pbi_rgid", ctypes.c_uint32),
                ("pbi_svuid", ctypes.c_uint32),
                ("pbi_svgid", ctypes.c_uint32),
                ("rfu_1", ctypes.c_uint32),
                ("pbi_comm", ctypes.c_char * 16),
                ("pbi_name", ctypes.c_char * 32),
                ("pbi_nfiles", ctypes.c_uint32),
                ("pbi_pgid", ctypes.c_uint32),
                ("pbi_pjobc", ctypes.c_uint32),
                ("e_tdev", ctypes.c_uint32),
                ("e_tpgid", ctypes.c_uint32),
                ("pbi_nice", ctypes.c_int32),
                ("pbi_start_tvsec", ctypes.c_uint64),
                ("pbi_start_tvusec", ctypes.c_uint64),
            ]

        library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        library.proc_pidinfo.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        library.proc_pidinfo.restype = ctypes.c_int
        info = ProcBsdInfo()
        proc_pid_tbsdinfo = 3
        result = library.proc_pidinfo(
            int(pid),
            proc_pid_tbsdinfo,
            0,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if result != ctypes.sizeof(info) or int(info.pbi_pid) != int(pid):
            return None
        return (
            "darwin-proc-start:"
            f"{int(info.pbi_start_tvsec)}:{int(info.pbi_start_tvusec)}"
        )
    except (AttributeError, ImportError, OSError, TypeError, ValueError):
        return None


def process_birth_identity(pid: int | None = None) -> str | None:
    """Return a stable, non-secret identity for one concrete PID incarnation."""

    resolved_pid = int(pid or os.getpid())
    if resolved_pid <= 0:
        return None
    proc_stat = Path(f"/proc/{resolved_pid}/stat")
    try:
        raw_stat = proc_stat.read_text(encoding="utf-8")
        after_command = raw_stat.rsplit(")", 1)[1].strip().split()
        # /proc stat field 22 is process start time; field 3 is index 0 here.
        if len(after_command) > 19:
            return f"linux-proc-start:{after_command[19]}"
    except (OSError, IndexError):
        pass
    if darwin_identity := _darwin_process_birth_identity(resolved_pid):
        return darwin_identity
    try:
        completed = subprocess.run(
            ["ps", "-p", str(resolved_pid), "-o", "lstart=", "-o", "command="],
            check=False,
            capture_output=True,
            text=True,
            timeout=1,
        )
    except (OSError, subprocess.SubprocessError, TypeError):
        return None
    identity_source = completed.stdout.strip()
    if completed.returncode != 0 or not identity_source:
        return None
    digest = hashlib.sha256(identity_source.encode("utf-8")).hexdigest()
    return f"ps-start-command-sha256:{digest}"


def _job_lease_lock_file(job_id: str, root: Path | None = None) -> Path:
    safe_job_id = _validated_job_id(job_id)
    return job_leases_dir(root) / f"{safe_job_id}.lock"


def _book_lease_lock_file(book_id: str, root: Path | None = None) -> Path:
    digest = hashlib.sha256(str(book_id or "").strip().encode("utf-8")).hexdigest()
    # Book exclusion must survive replacement of the sidecar directory.  The
    # job-registry directory is the trusted namespace anchor; individual job
    # locks and JSON sidecars remain below its replaceable ``leases`` child.
    return job_leases_dir(root).parent / f"book-{digest}.lock"


def _open_directory_chain_nofollow(path: Path, *, create: bool) -> int:
    """Open one absolute directory chain while refusing every symlink."""

    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None:
        raise JobLeaseReadError("Lease storage could not be opened safely.")
    try:
        absolute = os.path.abspath(os.fspath(path))
    except (OSError, TypeError, ValueError):
        raise JobLeaseReadError("Lease storage could not be opened safely.") from None
    components = tuple(component for component in absolute.split(os.sep) if component)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | nofollow | directory
    try:
        current = os.open(os.sep, flags)
    except OSError:
        raise JobLeaseReadError("Lease storage could not be opened safely.") from None
    try:
        for component in components:
            if create:
                try:
                    os.mkdir(component, 0o700, dir_fd=current)
                except FileExistsError:
                    pass
                except OSError:
                    raise JobLeaseReadError(
                        "Lease storage could not be opened safely."
                    ) from None
            try:
                child = os.open(component, flags, dir_fd=current)
            except OSError:
                raise JobLeaseReadError(
                    "Lease storage could not be opened safely."
                ) from None
            os.close(current)
            current = child
        return current
    except BaseException:
        try:
            os.close(current)
        except OSError:
            pass
        raise


def _directory_path_matches_descriptor(path: Path, descriptor: int) -> bool:
    try:
        expected = os.fstat(descriptor)
        reopened = _open_directory_chain_nofollow(path, create=False)
    except (JobLeaseReadError, OSError):
        return False
    try:
        actual = os.fstat(reopened)
        return (
            stat.S_ISDIR(expected.st_mode)
            and stat.S_ISDIR(actual.st_mode)
            and (expected.st_dev, expected.st_ino) == (actual.st_dev, actual.st_ino)
        )
    finally:
        os.close(reopened)


@contextmanager
def _pinned_job_leases_directory(
    root: Path,
    *,
    create: bool,
) -> Iterator[int]:
    """Pin the sidecar namespace and fail if its registry child is replaced."""

    path = job_leases_dir(root)
    descriptor = _open_directory_chain_nofollow(path, create=create)
    try:
        if not _directory_path_matches_descriptor(path, descriptor):
            raise JobLeaseReadError("Lease sidecar namespace changed unexpectedly.")
        yield descriptor
    finally:
        with suppress(OSError):
            os.close(descriptor)


@contextmanager
def _locked_lease_file(lock_path: Path) -> Iterator[None]:
    """Hold one regular no-follow lease lock under a pinned parent directory."""

    key = str(lock_path.absolute())
    with _LOCAL_LOCKS_GUARD:
        local_lock = _LOCAL_LOCKS.setdefault(key, threading.Lock())
    with local_lock:
        parent_descriptor = _open_directory_chain_nofollow(
            lock_path.parent,
            create=True,
        )
        try:
            flags = (
                os.O_RDWR
                | os.O_CREAT
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            )
            descriptor = os.open(
                lock_path.name,
                flags,
                0o600,
                dir_fd=parent_descriptor,
            )
        except OSError:
            os.close(parent_descriptor)
            raise JobLeaseReadError("Lease lock could not be opened safely.") from None
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise JobLeaseReadError("Lease lock could not be opened safely.")
            if fcntl is not None:
                fcntl.flock(descriptor, fcntl.LOCK_EX)
            try:
                yield
            finally:
                if fcntl is not None:
                    with suppress(OSError):
                        fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            with suppress(OSError):
                os.close(descriptor)
            with suppress(OSError):
                os.close(parent_descriptor)


@contextmanager
def _locked_job_lease(job_id: str, root: Path | None = None) -> Iterator[None]:
    lock_path = _job_lease_lock_file(job_id, root)
    with _locked_lease_file(lock_path):
        yield


@contextmanager
def _locked_book_lease(book_id: str, root: Path | None = None) -> Iterator[None]:
    """Serialize launches that would otherwise use different per-job lease files."""

    lock_path = _book_lease_lock_file(book_id, root)
    with _locked_lease_file(lock_path):
        yield


def _lease_file_snapshot(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _read_job_lease_bytes_at(
    parent_descriptor: int,
    name: str,
    *,
    job_id: str,
) -> bytes | None:
    """Read one bounded stable sidecar through an already pinned directory."""

    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise JobLeaseReadError(f"Job lease '{job_id}' could not be read safely.")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0)
        | nofollow
    )
    try:
        path_before = os.stat(
            name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return None
    except OSError:
        raise JobLeaseReadError(
            f"Job lease '{job_id}' could not be read safely."
        ) from None
    if (
        not stat.S_ISREG(path_before.st_mode)
        or path_before.st_size > MAX_JOB_LEASE_BYTES
    ):
        raise JobLeaseReadError(f"Job lease '{job_id}' could not be read safely.")
    try:
        descriptor = os.open(name, flags, dir_fd=parent_descriptor)
    except OSError:
        raise JobLeaseReadError(
            f"Job lease '{job_id}' could not be read safely."
        ) from None
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or _lease_file_snapshot(before) != _lease_file_snapshot(path_before)
            or before.st_size > MAX_JOB_LEASE_BYTES
        ):
            raise JobLeaseReadError(
                f"Job lease '{job_id}' could not be read safely."
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            try:
                chunk = os.read(descriptor, _JOB_LEASE_READ_CHUNK_BYTES)
            except InterruptedError:
                continue
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_JOB_LEASE_BYTES:
                raise JobLeaseReadError(
                    f"Job lease '{job_id}' could not be read safely."
                )
            chunks.append(chunk)
        after = os.fstat(descriptor)
        path_after = os.stat(
            name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        reopened = os.open(name, flags, dir_fd=parent_descriptor)
        try:
            reopened_snapshot = os.fstat(reopened)
        finally:
            os.close(reopened)
    except JobLeaseReadError:
        raise
    except OSError:
        raise JobLeaseReadError(
            f"Job lease '{job_id}' could not be read safely."
        ) from None
    finally:
        os.close(descriptor)

    expected = _lease_file_snapshot(before)
    if (
        expected != _lease_file_snapshot(after)
        or expected != _lease_file_snapshot(path_after)
        or expected != _lease_file_snapshot(reopened_snapshot)
        or total != after.st_size
    ):
        raise JobLeaseReadError(f"Job lease '{job_id}' could not be read safely.")
    return b"".join(chunks)


def _read_job_lease_bytes(path: Path, *, job_id: str) -> bytes | None:
    """Read one bounded stable sidecar below a pinned no-follow parent."""

    parent_descriptor = _open_directory_chain_nofollow(path.parent, create=False)
    try:
        return _read_job_lease_bytes_at(
            parent_descriptor,
            path.name,
            job_id=job_id,
        )
    finally:
        os.close(parent_descriptor)


def _parse_job_lease_bytes(
    job_id: str,
    raw_bytes: bytes | None,
) -> dict[str, object]:
    if raw_bytes is None:
        return {}

    def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON object key")
            result[key] = value
        return result

    def _reject_constant(_value: str) -> object:
        raise ValueError("non-finite JSON number")

    try:
        raw_payload = raw_bytes.decode("utf-8", errors="strict")
        payload = json.loads(
            raw_payload,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, ValueError):
        raise JobLeaseReadError(
            f"Job lease '{job_id}' is corrupt and cannot be trusted."
        ) from None
    if not isinstance(payload, dict):
        raise JobLeaseReadError(f"Job lease '{job_id}' has an invalid payload shape.")
    required_fields = {"job_id", "run_attempt_id", "generation", "token", "state"}
    if not required_fields.issubset(payload):
        raise JobLeaseReadError(f"Job lease '{job_id}' is missing required fencing fields.")
    generation_value = payload.get("generation")
    if type(generation_value) is not int:
        raise JobLeaseReadError(f"Job lease '{job_id}' has an invalid generation.")
    generation = generation_value
    valid_states = ACTIVE_LEASE_STATES | {"fenced", "released"}
    if (
        type(payload.get("job_id")) is not str
        or payload["job_id"] != job_id
        or type(payload.get("run_attempt_id")) is not str
        or not payload["run_attempt_id"].strip()
        or generation <= 0
        or type(payload.get("token")) is not str
        or not payload["token"]
        or type(payload.get("state")) is not str
        or payload["state"] not in valid_states
        or ("book_id" in payload and type(payload["book_id"]) is not str)
    ):
        raise JobLeaseReadError(f"Job lease '{job_id}' has invalid fencing metadata.")
    return payload


def _read_job_lease_at(
    job_id: str,
    leases_descriptor: int,
) -> dict[str, object]:
    safe_job_id = _validated_job_id(job_id)
    raw_bytes = _read_job_lease_bytes_at(
        leases_descriptor,
        f"{safe_job_id}.json",
        job_id=safe_job_id,
    )
    return _parse_job_lease_bytes(safe_job_id, raw_bytes)


def _read_job_lease_unlocked(job_id: str, root: Path | None = None) -> dict[str, object]:
    path = job_lease_file(job_id, root)
    raw_bytes = _read_job_lease_bytes(path, job_id=job_id)
    return _parse_job_lease_bytes(job_id, raw_bytes)


def _write_job_lease_unlocked(job_id: str, payload: Mapping[str, object], root: Path | None = None) -> None:
    path = job_lease_file(job_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    try:
        descriptor = os.open(
            temp_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(dict(payload), handle, ensure_ascii=False, indent=2)
        temp_path.replace(path)
        path.chmod(0o600)
    finally:
        temp_path.unlink(missing_ok=True)


def load_job_lease(job_id: str, *, root: Path | None = None) -> dict[str, object]:
    """Load one raw lease sidecar for internal fencing decisions."""

    with _locked_job_lease(job_id, root):
        return dict(_read_job_lease_unlocked(job_id, root))


@contextmanager
def guard_job_lease_snapshot(
    job_id: str,
    *,
    root: Path | None = None,
    expected_run_attempt_id: str | None = None,
    expected_generation: int | None = None,
) -> Iterator[bool]:
    """Hold the lease lock while a matching registry snapshot is persisted."""

    with _locked_job_lease(job_id, root):
        current = _read_job_lease_unlocked(job_id, root)
        expected_attempt = str(expected_run_attempt_id or "").strip()
        if expected_attempt and expected_generation is not None:
            matches = (
                str(current.get("run_attempt_id", "") or "") == expected_attempt
                and int(current.get("generation", 0) or 0) == int(expected_generation)
            )
        else:
            # Legacy records may be refreshed only while no managed attempt has
            # appeared.  Once a sidecar exists, it is the generation authority.
            matches = not current
        yield matches


def job_lease_is_valid(payload: Mapping[str, object], *, now: datetime | None = None) -> bool:
    """Return whether a lease payload still represents a live owner."""

    if str(payload.get("state", "") or "") not in ACTIVE_LEASE_STATES:
        return False
    expires_at = _parse_timestamp(payload.get("expires_at"))
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    return expires_at is not None and expires_at > reference.astimezone(timezone.utc)


def sanitized_lease_metadata(payload: Mapping[str, object], *, now: datetime | None = None) -> dict[str, object]:
    """Return persistable lease metadata without the fencing token."""

    if not payload:
        return {}
    return {
        "generation": max(0, int(payload.get("generation", 0) or 0)),
        "state": str(payload.get("state", "") or ""),
        "owner_pid": int(payload.get("owner_pid", 0) or 0) or None,
        "owner_birth_identity": str(payload.get("owner_birth_identity", "") or "") or None,
        "acquired_at": str(payload.get("acquired_at", "") or ""),
        "heartbeat_at": str(payload.get("heartbeat_at", "") or ""),
        "expires_at": str(payload.get("expires_at", "") or ""),
        "released_at": str(payload.get("released_at", "") or ""),
        "fenced_at": str(payload.get("fenced_at", "") or ""),
        "valid": job_lease_is_valid(payload, now=now),
    }


def validate_lease_timing(*, ttl_seconds: float, heartbeat_interval_seconds: float) -> None:
    """Require enough missed-heartbeat tolerance before a worker is fenced."""

    interval = float(heartbeat_interval_seconds)
    ttl = float(ttl_seconds)
    if interval <= 0:
        raise ValueError("Job lease heartbeat interval must be positive.")
    if ttl < interval * 3:
        raise ValueError("Job lease TTL must be at least three times the heartbeat interval.")


def _process_exists(pid: int | None) -> bool:
    if pid is None or int(pid) <= 0:
        return False
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _book_worker_conflict(
    book_id: str,
    *,
    root: Path,
    leases_descriptor: int,
    now: datetime,
    confirmed_stopped_attempt: tuple[str, str, int] | None = None,
) -> dict[str, object] | None:
    """Return an existing same-book worker that cannot safely be replaced."""

    normalized_book_id = str(book_id or "").strip()
    if not normalized_book_id:
        return None
    try:
        sidecar_names = sorted(
            name
            for name in os.listdir(leases_descriptor)
            if name.endswith(".json") and len(name) > len(".json")
        )
    except OSError:
        raise JobLeaseReadError("Lease sidecars could not be listed safely.") from None
    for name in sidecar_names:
        job_id = name[: -len(".json")]
        # Heartbeats and launch finalization replace a sidecar atomically while
        # holding its job lock.  Take the same lock before the strict stable
        # snapshot so a legitimate concurrent replacement is serialized rather
        # than misclassified as an unsafe pathname race.  The enclosing book
        # lock keeps the global lock order book -> job consistent with acquire.
        with _locked_job_lease(job_id, root):
            payload = _read_job_lease_at(job_id, leases_descriptor)
        if not isinstance(payload, dict) or str(payload.get("book_id", "") or "").strip() != normalized_book_id:
            continue
        if confirmed_stopped_attempt is not None:
            stopped_job_id, stopped_run_attempt_id, stopped_generation = confirmed_stopped_attempt
            if (
                str(payload.get("state", "") or "") == "fenced"
                and str(payload.get("job_id", "") or "") == stopped_job_id
                and str(payload.get("run_attempt_id", "") or "") == stopped_run_attempt_id
                and int(payload.get("generation", 0) or 0) == stopped_generation
            ):
                continue
        if job_lease_is_valid(payload, now=now):
            return payload
        state = str(payload.get("state", "") or "")
        if state not in ACTIVE_LEASE_STATES | {"fenced"}:
            continue
        owner_pid = int(payload.get("owner_pid", 0) or 0) or None
        if state in ACTIVE_LEASE_STATES and owner_pid is None:
            # A launch capability in starting/active state can still heartbeat
            # after its TTL.  Without a concrete dead owner, allowing a book
            # writer would let that grant revive inside the exclusion window.
            return payload
        if not _process_exists(owner_pid):
            continue
        expected_identity = str(payload.get("owner_birth_identity", "") or "").strip()
        actual_identity = process_birth_identity(owner_pid)
        if expected_identity and actual_identity and expected_identity != actual_identity:
            continue
        # If the PID still exists and its incarnation cannot be disproved, fail
        # closed.  A refresh/manual resume may fence and confirm exit first.
        return payload
    return None


@contextmanager
def guard_book_writer_exclusion(
    book_id: str,
    *,
    root: Path | None = None,
    now: datetime | None = None,
) -> Iterator[BookWriterExclusion]:
    """Hold a book-scoped writer lock while no worker can own the book."""

    if type(book_id) is not str:
        raise TypeError("Book id must be an exact string.")
    normalized_book_id = book_id.strip()
    if not normalized_book_id:
        raise ValueError("Book id must not be empty.")

    resolved_root = (root or Path.cwd()).resolve()
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    reference = reference.astimezone(timezone.utc)

    with _locked_book_lease(normalized_book_id, resolved_root):
        with _pinned_job_leases_directory(
            resolved_root,
            create=True,
        ) as leases_descriptor:
            exclusion = BookWriterExclusion(
                leases_path=job_leases_dir(resolved_root),
                leases_descriptor=leases_descriptor,
            )
            exclusion.assert_current()
            try:
                conflict = _book_worker_conflict(
                    normalized_book_id,
                    root=resolved_root,
                    leases_descriptor=leases_descriptor,
                    now=reference,
                )
            except Exception:
                raise JobLeaseConflict(
                    "Book writer exclusion could not be acquired safely."
                ) from None
            if conflict is not None:
                raise JobLeaseConflict(
                    "Book writer exclusion could not be acquired safely."
                )
            yield exclusion


def _acquire_job_lease_unchecked(
    job_id: str,
    *,
    root: Path,
    book_id: str | None,
    job_kind: str | None,
    mechanism_key: str | None,
    ttl_seconds: float,
    reference: datetime,
) -> JobLeaseGrant:
    with _locked_job_lease(job_id, root):
        current = _read_job_lease_unlocked(job_id, root)
        if job_lease_is_valid(current, now=reference):
            raise JobLeaseConflict(f"Job '{job_id}' already has an active worker lease.")
        generation = max(0, int(current.get("generation", 0) or 0)) + 1
        run_attempt_id = uuid.uuid4().hex
        token = secrets.token_urlsafe(32)
        acquired_at = _timestamp(reference)
        payload: dict[str, object] = {
            "job_id": job_id,
            "run_attempt_id": run_attempt_id,
            "generation": generation,
            "token": token,
            "state": "starting",
            "owner_pid": None,
            "owner_birth_identity": "",
            "book_id": str(book_id or ""),
            "job_kind": str(job_kind or ""),
            "mechanism_key": str(mechanism_key or ""),
            "acquired_at": acquired_at,
            "heartbeat_at": acquired_at,
            "expires_at": _timestamp(reference + timedelta(seconds=max(1.0, float(ttl_seconds)))),
            "released_at": "",
            "fenced_at": "",
        }
        _write_job_lease_unlocked(job_id, payload, root)
    return JobLeaseGrant(
        job_id=job_id,
        run_attempt_id=run_attempt_id,
        generation=generation,
        token=token,
        root=root,
        book_id=str(book_id or ""),
        job_kind=str(job_kind or ""),
        mechanism_key=str(mechanism_key or ""),
    )


def acquire_job_lease(
    job_id: str,
    *,
    root: Path | None = None,
    book_id: str | None = None,
    job_kind: str | None = None,
    mechanism_key: str | None = None,
    ttl_seconds: float = DEFAULT_LEASE_TTL_SECONDS,
    heartbeat_interval_seconds: float = DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
    enforce_book_exclusivity: bool = False,
    confirmed_stopped_attempt: tuple[str, str, int] | None = None,
    now: datetime | None = None,
) -> JobLeaseGrant:
    """Acquire the next lease generation unless another attempt remains live."""

    job_id = _validated_job_id(job_id)
    validate_lease_timing(ttl_seconds=ttl_seconds, heartbeat_interval_seconds=heartbeat_interval_seconds)
    resolved_root = (root or Path.cwd()).resolve()
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    reference = reference.astimezone(timezone.utc)
    normalized_book_id = str(book_id or "").strip()
    if enforce_book_exclusivity and normalized_book_id:
        with _locked_book_lease(normalized_book_id, resolved_root):
            with _pinned_job_leases_directory(
                resolved_root,
                create=True,
            ) as leases_descriptor:
                conflict = _book_worker_conflict(
                    normalized_book_id,
                    root=resolved_root,
                    leases_descriptor=leases_descriptor,
                    now=reference,
                    confirmed_stopped_attempt=confirmed_stopped_attempt,
                )
                if conflict is not None:
                    raise JobLeaseConflict(
                        f"Book '{normalized_book_id}' already has a worker that has not been confirmed stopped."
                    )
                return _acquire_job_lease_unchecked(
                    job_id,
                    root=resolved_root,
                    book_id=normalized_book_id,
                    job_kind=job_kind,
                    mechanism_key=mechanism_key,
                    ttl_seconds=ttl_seconds,
                    reference=reference,
                )
    return _acquire_job_lease_unchecked(
        job_id,
        root=resolved_root,
        book_id=book_id,
        job_kind=job_kind,
        mechanism_key=mechanism_key,
        ttl_seconds=ttl_seconds,
        reference=reference,
    )


def _matches_grant(payload: Mapping[str, object], grant: JobLeaseGrant) -> bool:
    return (
        str(payload.get("job_id", "") or "") == grant.job_id
        and str(payload.get("run_attempt_id", "") or "") == grant.run_attempt_id
        and int(payload.get("generation", 0) or 0) == grant.generation
        and secrets.compare_digest(str(payload.get("token", "") or ""), grant.token)
    )


def heartbeat_job_lease(
    grant: JobLeaseGrant,
    *,
    owner_pid: int | None = None,
    owner_birth_identity: str | None = None,
    ttl_seconds: float = DEFAULT_LEASE_TTL_SECONDS,
    now: datetime | None = None,
) -> dict[str, object]:
    """Renew one lease only when its complete fencing capability still matches."""

    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    reference = reference.astimezone(timezone.utc)
    with _locked_job_lease(grant.job_id, grant.root):
        current = _read_job_lease_unlocked(grant.job_id, grant.root)
        if not _matches_grant(current, grant) or str(current.get("state", "") or "") not in ACTIVE_LEASE_STATES:
            raise JobLeaseLost(f"Worker lease for job '{grant.job_id}' is no longer current.")
        recorded_owner = int(current.get("owner_pid", 0) or 0) or None
        if recorded_owner is not None and (owner_pid is None or recorded_owner != int(owner_pid)):
            raise JobLeaseLost(f"Worker lease for job '{grant.job_id}' belongs to another process.")
        recorded_birth_identity = str(current.get("owner_birth_identity", "") or "").strip()
        resolved_birth_identity = str(owner_birth_identity or "").strip()
        if owner_pid is not None and not resolved_birth_identity:
            resolved_birth_identity = process_birth_identity(owner_pid) or ""
        if not resolved_birth_identity and recorded_owner == owner_pid:
            # A transient inability to run the birth probe does not disprove a
            # previously recorded identity for the same PID and fencing token.
            resolved_birth_identity = recorded_birth_identity
        if (
            recorded_birth_identity
            and resolved_birth_identity
            and recorded_birth_identity != resolved_birth_identity
        ):
            raise JobLeaseLost(f"Worker lease for job '{grant.job_id}' belongs to another PID incarnation.")
        current["state"] = "active"
        if owner_pid is not None:
            current["owner_pid"] = int(owner_pid)
        if resolved_birth_identity:
            current["owner_birth_identity"] = resolved_birth_identity
        current["heartbeat_at"] = _timestamp(reference)
        current["expires_at"] = _timestamp(reference + timedelta(seconds=max(1.0, float(ttl_seconds))))
        _write_job_lease_unlocked(grant.job_id, current, grant.root)
        return dict(current)


def release_job_lease(grant: JobLeaseGrant, *, now: datetime | None = None) -> dict[str, object]:
    """Release a lease without disturbing a newer fenced generation."""

    with _locked_job_lease(grant.job_id, grant.root):
        current = _read_job_lease_unlocked(grant.job_id, grant.root)
        if not _matches_grant(current, grant):
            return dict(current)
        released_at = _timestamp(now)
        current.update({"state": "released", "released_at": released_at, "expires_at": released_at})
        _write_job_lease_unlocked(grant.job_id, current, grant.root)
        return dict(current)


def fence_job_lease(
    job_id: str,
    *,
    root: Path | None = None,
    expected_run_attempt_id: str | None = None,
    expected_generation: int | None = None,
    now: datetime | None = None,
) -> dict[str, object]:
    """Fence one known generation while refusing to revoke a newer attempt."""

    with _locked_job_lease(job_id, root):
        current = _read_job_lease_unlocked(job_id, root)
        if not current:
            return {}
        if expected_run_attempt_id and str(current.get("run_attempt_id", "") or "") != expected_run_attempt_id:
            return dict(current)
        if expected_generation is not None and int(current.get("generation", 0) or 0) != int(expected_generation):
            return dict(current)
        fenced_at = _timestamp(now)
        current.update({"state": "fenced", "fenced_at": fenced_at, "expires_at": fenced_at})
        _write_job_lease_unlocked(job_id, current, root)
        return dict(current)


def lease_environment(grant: JobLeaseGrant) -> dict[str, str]:
    """Build the approved worker environment without logging its token."""

    return {
        ENV_JOB_ID: grant.job_id,
        ENV_RUN_ATTEMPT_ID: grant.run_attempt_id,
        ENV_LEASE_GENERATION: str(grant.generation),
        ENV_LEASE_TOKEN: grant.token,
        ENV_RUNTIME_ROOT: str(grant.root),
        ENV_BOOK_ID: grant.book_id,
        ENV_JOB_KIND: grant.job_kind,
        ENV_MECHANISM_KEY: grant.mechanism_key,
    }


def grant_from_environment(environment: Mapping[str, str] | None = None) -> JobLeaseGrant | None:
    """Load a managed-worker grant, or return None for a legacy/direct CLI."""

    source = environment if environment is not None else os.environ
    raw_job_id = source.get(ENV_JOB_ID, "")
    if raw_job_id == "":
        return None
    try:
        job_id = _validated_job_id(raw_job_id)
    except (TypeError, ValueError):
        raise JobLeaseLost("Managed worker job id is invalid.") from None
    required = {
        ENV_RUN_ATTEMPT_ID: str(source.get(ENV_RUN_ATTEMPT_ID, "") or "").strip(),
        ENV_LEASE_GENERATION: str(source.get(ENV_LEASE_GENERATION, "") or "").strip(),
        ENV_LEASE_TOKEN: str(source.get(ENV_LEASE_TOKEN, "") or "").strip(),
        ENV_RUNTIME_ROOT: str(source.get(ENV_RUNTIME_ROOT, "") or "").strip(),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise JobLeaseLost(f"Managed worker lease context is incomplete for job '{job_id}'.")
    try:
        generation = int(required[ENV_LEASE_GENERATION])
    except ValueError as exc:
        raise JobLeaseLost(f"Managed worker lease generation is invalid for job '{job_id}'.") from exc
    return JobLeaseGrant(
        job_id=job_id,
        run_attempt_id=required[ENV_RUN_ATTEMPT_ID],
        generation=generation,
        token=required[ENV_LEASE_TOKEN],
        root=Path(required[ENV_RUNTIME_ROOT]).resolve(),
        book_id=str(source.get(ENV_BOOK_ID, "") or "").strip(),
        job_kind=str(source.get(ENV_JOB_KIND, "") or "").strip(),
        mechanism_key=str(source.get(ENV_MECHANISM_KEY, "") or "").strip(),
    )


def current_lease() -> CurrentLease | None:
    """Return token-free identity for the current managed worker context."""

    state = _CURRENT_LEASE.get()
    if state is None:
        with _PROCESS_LEASE_GUARD:
            state = _PROCESS_LEASE_STATE
    if state is None:
        return None
    grant = state.grant
    return CurrentLease(
        job_id=grant.job_id,
        run_attempt_id=grant.run_attempt_id,
        book_id=grant.book_id,
        job_kind=grant.job_kind,
        mechanism_key=grant.mechanism_key,
        generation=grant.generation,
        acquired_at=state.acquired_at,
        valid=not state.invalidated.is_set(),
    )


def _invalidate_worker_state(state: _WorkerLeaseState) -> None:
    """Serialize invalidation with grace-path verification decisions."""

    with state.verification_guard:
        state.invalidated.set()


def assert_current_lease() -> CurrentLease | None:
    """Fail closed when the current managed worker no longer owns its lease."""

    state = _CURRENT_LEASE.get()
    if state is None:
        with _PROCESS_LEASE_GUARD:
            state = _PROCESS_LEASE_STATE
    if state is None:
        return None
    if state.invalidated.is_set():
        raise JobLeaseLost(f"Worker lease for job '{state.grant.job_id}' is no longer current.")
    grant = state.grant
    try:
        with _locked_job_lease(grant.job_id, grant.root):
            payload = _read_job_lease_unlocked(grant.job_id, grant.root)
    except (JobLeaseReadError, OSError) as exc:
        cause = exc.__cause__ if isinstance(exc, JobLeaseReadError) else exc
        with state.verification_guard:
            within_ttl_grace = (
                isinstance(cause, OSError)
                and time.monotonic() - state.last_verified_monotonic
                < state.verification_ttl_seconds
            )
            if within_ttl_grace and not state.invalidated.is_set():
                # Launchers also fail closed while the sidecar is unreadable, so
                # a bounded grace period preserves the sole worker without
                # allowing a replacement generation to start.  Invalidation is
                # checked under the same guard immediately before returning.
                return CurrentLease(
                    job_id=grant.job_id,
                    run_attempt_id=grant.run_attempt_id,
                    book_id=grant.book_id,
                    job_kind=grant.job_kind,
                    mechanism_key=grant.mechanism_key,
                    generation=grant.generation,
                    acquired_at=state.acquired_at,
                    valid=True,
                )
        _invalidate_worker_state(state)
        raise JobLeaseLost(f"Worker lease for job '{grant.job_id}' cannot be verified safely.") from exc
    if not _matches_grant(payload, grant) or str(payload.get("state", "") or "") not in ACTIVE_LEASE_STATES:
        _invalidate_worker_state(state)
        raise JobLeaseLost(f"Worker lease for job '{grant.job_id}' is no longer current.")
    owner_pid = int(payload.get("owner_pid", 0) or 0) or None
    expected_birth_identity = str(payload.get("owner_birth_identity", "") or "").strip()
    actual_birth_identity = state.owner_birth_identity
    if not actual_birth_identity and expected_birth_identity:
        # The heartbeat may have obtained the first successful birth probe
        # after context entry. The matching token/generation and PID make that
        # one-way fill safe; a later non-empty mismatch still fences normally.
        with state.verification_guard:
            if not state.owner_birth_identity:
                state.owner_birth_identity = expected_birth_identity
            actual_birth_identity = state.owner_birth_identity
    if owner_pid not in {None, os.getpid()} or (
        expected_birth_identity
        and expected_birth_identity != (actual_birth_identity or "")
    ):
        _invalidate_worker_state(state)
        raise JobLeaseLost(f"Worker lease for job '{grant.job_id}' belongs to another PID incarnation.")
    with state.verification_guard:
        state.last_verified_monotonic = time.monotonic()
    return current_lease()


def _terminate_current_process() -> None:  # pragma: no cover - process behavior
    os.kill(os.getpid(), signal.SIGTERM)


@contextmanager
def lease_context(
    grant: JobLeaseGrant | None,
    *,
    heartbeat_interval_seconds: float = DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
    ttl_seconds: float = DEFAULT_LEASE_TTL_SECONDS,
    terminate_on_loss: Callable[[], None] = _terminate_current_process,
) -> Iterator[CurrentLease | None]:
    """Validate, expose, and renew the outer process lease for one CLI run."""

    if grant is None:
        yield None
        return

    validate_lease_timing(ttl_seconds=ttl_seconds, heartbeat_interval_seconds=heartbeat_interval_seconds)
    global _PROCESS_LEASE_STATE

    owner_birth_identity = process_birth_identity(os.getpid()) or ""
    initial_payload = heartbeat_job_lease(
        grant,
        owner_pid=os.getpid(),
        owner_birth_identity=owner_birth_identity,
        ttl_seconds=ttl_seconds,
    )
    state = _WorkerLeaseState(
        grant=grant,
        acquired_at=str(initial_payload.get("acquired_at", "") or ""),
        owner_birth_identity=str(
            initial_payload.get("owner_birth_identity", "") or owner_birth_identity
        ),
        verification_ttl_seconds=float(ttl_seconds),
    )
    with _PROCESS_LEASE_GUARD:
        if _PROCESS_LEASE_STATE is not None and _PROCESS_LEASE_STATE.grant != grant:
            raise JobLeaseConflict("This process already has a different active worker lease.")
        _PROCESS_LEASE_STATE = state
    context_token = _CURRENT_LEASE.set(state)
    stop = threading.Event()

    def _heartbeat_loop() -> None:
        while not stop.wait(max(0.01, float(heartbeat_interval_seconds))):
            try:
                heartbeat_payload = heartbeat_job_lease(
                    grant,
                    owner_pid=os.getpid(),
                    owner_birth_identity=state.owner_birth_identity,
                    ttl_seconds=ttl_seconds,
                )
            except (JobLeaseReadError, OSError) as exc:
                cause = exc.__cause__ if isinstance(exc, JobLeaseReadError) else exc
                with state.verification_guard:
                    if stop.is_set():
                        return
                    within_ttl_grace = (
                        isinstance(cause, OSError)
                        and time.monotonic() - state.last_verified_monotonic
                        < float(ttl_seconds)
                    )
                if within_ttl_grace:
                    continue
                _invalidate_worker_state(state)
                terminate_on_loss()
                return
            except Exception:
                # A fencing mismatch is authoritative and must stop this
                # generation immediately; only transient filesystem failures
                # receive the TTL grace above.
                with state.verification_guard:
                    if stop.is_set():
                        return
                    state.invalidated.set()
                terminate_on_loss()
                return
            else:
                with state.verification_guard:
                    observed_birth_identity = str(
                        heartbeat_payload.get("owner_birth_identity", "") or ""
                    ).strip()
                    if not state.owner_birth_identity and observed_birth_identity:
                        state.owner_birth_identity = observed_birth_identity
                    state.last_verified_monotonic = time.monotonic()

    heartbeat = threading.Thread(target=_heartbeat_loop, name="job-lease-heartbeat", daemon=True)
    heartbeat.start()
    try:
        yield current_lease()
    finally:
        with state.verification_guard:
            stop.set()
        heartbeat.join(timeout=max(0.1, min(1.0, float(heartbeat_interval_seconds))))
        try:
            release_job_lease(grant)
        finally:
            _CURRENT_LEASE.reset(context_token)
            with _PROCESS_LEASE_GUARD:
                if _PROCESS_LEASE_STATE is state:
                    _PROCESS_LEASE_STATE = None


@contextmanager
def lease_context_from_environment(
    environment: Mapping[str, str] | None = None,
    *,
    heartbeat_interval_seconds: float = DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
    ttl_seconds: float = DEFAULT_LEASE_TTL_SECONDS,
    terminate_on_loss: Callable[[], None] = _terminate_current_process,
) -> Iterator[CurrentLease | None]:
    """Enter a managed lease when env metadata exists; otherwise stay inert."""

    grant = grant_from_environment(environment)
    with lease_context(
        grant,
        heartbeat_interval_seconds=heartbeat_interval_seconds,
        ttl_seconds=ttl_seconds,
        terminate_on_loss=terminate_on_loss,
    ):
        yield current_lease()


__all__ = [
    "ACTIVE_LEASE_STATES",
    "BookWriterExclusion",
    "CurrentLease",
    "DEFAULT_HEARTBEAT_INTERVAL_SECONDS",
    "DEFAULT_LEASE_TTL_SECONDS",
    "ENV_BOOK_ID",
    "ENV_JOB_ID",
    "ENV_JOB_KIND",
    "ENV_LEASE_GENERATION",
    "ENV_LEASE_TOKEN",
    "ENV_MECHANISM_KEY",
    "ENV_RUN_ATTEMPT_ID",
    "ENV_RUNTIME_ROOT",
    "JobLeaseConflict",
    "JobLeaseGrant",
    "JobLeaseLost",
    "JobLeaseReadError",
    "acquire_job_lease",
    "assert_current_lease",
    "current_lease",
    "fence_job_lease",
    "guard_book_writer_exclusion",
    "guard_job_lease_snapshot",
    "grant_from_environment",
    "heartbeat_job_lease",
    "job_lease_file",
    "job_lease_is_valid",
    "lease_context",
    "lease_context_from_environment",
    "lease_environment",
    "load_job_lease",
    "process_birth_identity",
    "release_job_lease",
    "sanitized_lease_metadata",
    "validate_lease_timing",
]
