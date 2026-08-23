#!/usr/bin/env python3
"""Safely validate Annotation Pack v0 JSON without network access.

Normal mode performs the complete AnnotationSet semantic validation. The
contract's standalone Annotation examples intentionally require
``--schema-only`` because they do not contain enough context for Pack-level
identity and semantic checks.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, NoReturn
import warnings


MAX_ANNOTATION_PACK_JSON_BYTES = 16 * 1024 * 1024
MAX_ANNOTATION_PACK_JSON_DEPTH = 64
MAX_ANNOTATION_PACK_JSON_NODES = 100_000
MAX_ANNOTATION_PACK_SINGLE_STRING_CODE_POINTS = 1024 * 1024
MAX_ANNOTATION_PACK_TOTAL_STRING_CODE_POINTS = 16 * 1024 * 1024
MAX_SCHEMA_FINDINGS = 256
_READ_CHUNK_BYTES = 1024 * 1024
_CODE_RE = re.compile(r"[a-z][a-z0-9_]{0,127}\Z")
_DIGEST_RE = re.compile(r"[0-9a-f]{64}\Z")
_PACK_ID_RE = re.compile(
    r"urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z"
)
_SEVERITIES = frozenset({"fatal", "error", "warning", "skipped"})
_SEVERITY_RANK = {"fatal": 0, "error": 1, "skipped": 2, "warning": 3}


class _SafeInputError(ValueError):
    """A fixed-code rejection that never carries source-controlled text."""

    __slots__ = ("code",)

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class _DuplicateKeyError(ValueError):
    pass


class _NonFiniteNumberError(ValueError):
    pass


def _duplicate_safe_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError
        result[key] = value
    return result


def _reject_nonfinite_number(_value: str) -> NoReturn:
    raise _NonFiniteNumberError


def _open_all_components_nofollow(path: Path) -> int:
    """Open ``path`` while refusing symlinks in every pathname component."""

    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory_flag = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory_flag is None:
        raise _SafeInputError("source_unavailable")

    parts = path.parts
    if path.is_absolute():
        directory = os.open(
            os.path.sep,
            os.O_RDONLY | os.O_CLOEXEC | directory_flag | nofollow,
        )
        parts = parts[1:]
    else:
        directory = os.open(
            ".",
            os.O_RDONLY | os.O_CLOEXEC | directory_flag | nofollow,
        )
    if not parts:
        os.close(directory)
        raise _SafeInputError("source_not_regular")

    try:
        for component in parts[:-1]:
            if component in {"", "."}:
                continue
            next_directory = os.open(
                component,
                os.O_RDONLY | os.O_CLOEXEC | directory_flag | nofollow,
                dir_fd=directory,
            )
            os.close(directory)
            directory = next_directory
        return os.open(
            parts[-1],
            os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow,
            dir_fd=directory,
        )
    except OSError:
        raise _SafeInputError("source_unavailable") from None
    finally:
        os.close(directory)


def _strict_json_document(path: Path) -> tuple[Any, bytes]:
    """Read one bounded, regular, stable, UTF-8 JSON file without following links."""

    try:
        descriptor = _open_all_components_nofollow(path)
    except _SafeInputError:
        raise
    except OSError:
        raise _SafeInputError("source_unavailable") from None

    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise _SafeInputError("source_not_regular")
        if before.st_size > MAX_ANNOTATION_PACK_JSON_BYTES:
            raise _SafeInputError("source_too_large")

        chunks: list[bytes] = []
        byte_count = 0
        while True:
            chunk = os.read(descriptor, _READ_CHUNK_BYTES)
            if not chunk:
                break
            byte_count += len(chunk)
            if byte_count > MAX_ANNOTATION_PACK_JSON_BYTES:
                raise _SafeInputError("source_too_large")
            chunks.append(chunk)
        after = os.fstat(descriptor)
        reopened_descriptor = _open_all_components_nofollow(path)
        try:
            reopened = os.fstat(reopened_descriptor)
        finally:
            os.close(reopened_descriptor)
    except OSError:
        raise _SafeInputError("source_unavailable") from None
    finally:
        os.close(descriptor)

    snapshot = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    if snapshot != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    ) or snapshot != (
        reopened.st_dev,
        reopened.st_ino,
        reopened.st_size,
        reopened.st_mtime_ns,
        reopened.st_ctime_ns,
    ) or after.st_size != byte_count:
        raise _SafeInputError("source_changed_during_read")

    content = b"".join(chunks)
    if content.startswith(b"\xef\xbb\xbf"):
        raise _SafeInputError("utf8_bom_forbidden")
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise _SafeInputError("invalid_utf8") from None

    try:
        document = json.loads(
            text,
            object_pairs_hook=_duplicate_safe_object,
            parse_constant=_reject_nonfinite_number,
        )
    except _DuplicateKeyError:
        raise _SafeInputError("duplicate_json_key") from None
    except _NonFiniteNumberError:
        raise _SafeInputError("nonfinite_json_number") from None
    except (json.JSONDecodeError, RecursionError):
        raise _SafeInputError("invalid_json") from None
    _enforce_json_limits(document)
    return document, content


def _enforce_json_limits(document: object) -> None:
    nodes = 0
    string_code_points = 0
    stack: list[tuple[object, int]] = [(document, 1)]
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if (
            nodes > MAX_ANNOTATION_PACK_JSON_NODES
            or depth > MAX_ANNOTATION_PACK_JSON_DEPTH
        ):
            raise _SafeInputError("document_limit_exceeded")
        if type(value) is dict:
            for key, child in value.items():
                if len(key) > MAX_ANNOTATION_PACK_SINGLE_STRING_CODE_POINTS:
                    raise _SafeInputError("document_limit_exceeded")
                string_code_points += len(key)
                stack.append((child, depth + 1))
        elif type(value) is list:
            stack.extend((child, depth + 1) for child in value)
        elif type(value) is str:
            if len(value) > MAX_ANNOTATION_PACK_SINGLE_STRING_CODE_POINTS:
                raise _SafeInputError("document_limit_exceeded")
            string_code_points += len(value)
        if string_code_points > MAX_ANNOTATION_PACK_TOTAL_STRING_CODE_POINTS:
            raise _SafeInputError("document_limit_exceeded")


def _safe_digest(value: object) -> str | None:
    return value if type(value) is str and _DIGEST_RE.fullmatch(value) else None


def _safe_pack_id(value: object) -> str | None:
    return value if type(value) is str and _PACK_ID_RE.fullmatch(value) else None


def _safe_nonnegative_int(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def _safe_finding(finding: object) -> dict[str, object]:
    from src.annotation_pack.validation import ERROR_CATALOG

    if isinstance(finding, Mapping):
        code = finding.get("code")
        severity = finding.get("severity")
        source_record_index = finding.get("source_record_index")
        source_record_digest = finding.get("source_record_digest")
    else:
        code = getattr(finding, "code", None)
        severity = getattr(finding, "severity", None)
        source_record_index = getattr(finding, "source_record_index", None)
        source_record_digest = getattr(finding, "source_record_digest", None)
    if (
        type(code) is not str
        or _CODE_RE.fullmatch(code) is None
        or code not in ERROR_CATALOG
    ):
        code = "invalid_finding"
    if severity not in _SEVERITIES:
        severity = "fatal"
    return {
        "code": code,
        "severity": severity,
        "source_record_index": _safe_nonnegative_int(source_record_index),
        "source_record_digest": _safe_digest(source_record_digest),
    }


def _finding_sort_key(finding: Mapping[str, object]) -> tuple[int, str, int, str]:
    index = finding["source_record_index"]
    return (
        _SEVERITY_RANK[str(finding["severity"])],
        str(finding["code"]),
        index if type(index) is int else -1,
        str(finding["source_record_digest"] or ""),
    )


def _fixed_finding(code: str, severity: str = "fatal") -> dict[str, object]:
    return {
        "code": code,
        "severity": severity,
        "source_record_index": None,
        "source_record_digest": None,
    }


def _failed_summary(code: str, *, mode: str) -> dict[str, object]:
    return {
        "status": "failed",
        "mode": mode,
        "pack_id": None,
        "semantic_digest": None,
        "input_snapshot_digest": None,
        "counts": {
            "input": 0,
            "exported": 0,
            "skipped": 0,
            "warnings": 0,
            "errors": 1,
        },
        "findings": [_fixed_finding(code)],
    }


def _schema_summary(document: Mapping[str, object]) -> dict[str, object]:
    from src.annotation_pack.schema import annotation_validator, pack_validator

    document_type = document.get("type")
    if document_type == "AnnotationSet":
        validator = pack_validator()
    elif document_type == "Annotation":
        validator = annotation_validator()
    else:
        return _failed_summary("unsupported_root_type", mode="schema-only")
    try:
        error_count = 0
        for _error in validator.iter_errors(document):
            error_count += 1
            if error_count > MAX_SCHEMA_FINDINGS:
                return _failed_summary(
                    "document_limit_exceeded",
                    mode="schema-only",
                )
    except Exception:
        return _failed_summary("schema_validation_failed", mode="schema-only")
    if error_count:
        summary = _failed_summary("schema_validation_failed", mode="schema-only")
        summary["counts"] = {
            "input": 0,
            "exported": 0,
            "skipped": 0,
            "warnings": 0,
            "errors": error_count,
        }
        return summary
    return {
        "status": "valid",
        "mode": "schema-only",
        "pack_id": None,
        "semantic_digest": None,
        "input_snapshot_digest": None,
        "counts": {
            "input": 0,
            "exported": 0,
            "skipped": 0,
            "warnings": 0,
            "errors": 0,
        },
        "findings": [],
    }


def _semantic_summary(
    document: Mapping[str, object],
    *,
    source_bytes: bytes,
    allow_empty: bool,
) -> dict[str, object]:
    if document.get("type") != "AnnotationSet":
        return _failed_summary("schema_only_required", mode="semantic")

    from src.annotation_pack.serialization import CanonicalJsonError, canonical_json_bytes
    from src.annotation_pack.validation import ValidationContext, validate_pack

    try:
        if canonical_json_bytes(document) != source_bytes:
            return _failed_summary("noncanonical_json", mode="semantic")
    except (CanonicalJsonError, TypeError, UnicodeError, ValueError):
        return _failed_summary("noncanonical_json", mode="semantic")

    try:
        result = validate_pack(
            document,
            context=ValidationContext(allow_empty=allow_empty),
        )
        raw_findings = tuple(result.findings)
    except Exception:
        return _failed_summary("semantic_validation_failed", mode="semantic")

    findings = [_safe_finding(finding) for finding in raw_findings]
    findings.sort(key=_finding_sort_key)
    status = (
        result.status
        if result.status in {"valid", "degraded", "failed"}
        else "failed"
    )
    counts = {
        "input": _safe_nonnegative_int(result.input_count),
        "exported": _safe_nonnegative_int(result.exported_count),
        "skipped": _safe_nonnegative_int(result.skipped_count),
        "warnings": _safe_nonnegative_int(result.warning_count),
        "errors": _safe_nonnegative_int(result.error_count),
    }
    if any(value is None for value in counts.values()):
        return _failed_summary("semantic_validation_failed", mode="semantic")
    return {
        "status": status,
        "mode": "semantic",
        "pack_id": _safe_pack_id(result.pack_id),
        "semantic_digest": _safe_digest(result.semantic_digest),
        "input_snapshot_digest": _safe_digest(result.input_snapshot_digest),
        "counts": counts,
        "findings": findings,
    }


def validate_path(
    path: Path,
    *,
    schema_only: bool = False,
    allow_empty: bool = False,
) -> dict[str, object]:
    """Return one deterministic, content-safe summary for ``path``."""

    mode = "schema-only" if schema_only else "semantic"
    try:
        document, source_bytes = _strict_json_document(path)
    except _SafeInputError as exc:
        return _failed_summary(exc.code, mode=mode)
    except Exception:
        return _failed_summary("source_unavailable", mode=mode)
    if type(document) is not dict:
        return _failed_summary("root_not_object", mode=mode)
    if schema_only:
        return _schema_summary(document)
    return _semantic_summary(
        document,
        source_bytes=source_bytes,
        allow_empty=allow_empty,
    )


def _json_line(summary: Mapping[str, object]) -> str:
    return json.dumps(
        summary,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


class _SafeArgumentParser(argparse.ArgumentParser):
    """Emit a fixed JSON usage failure without reflecting untrusted argv."""

    def error(self, _message: str) -> None:
        print(
            _json_line(_failed_summary("cli_usage_error", mode="usage")),
            file=sys.stderr,
        )
        raise SystemExit(2)


def _parser() -> argparse.ArgumentParser:
    parser = _SafeArgumentParser(
        prog="validate_annotation_pack.py",
        description=__doc__,
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="run only the strict local schema check (required for Annotation examples)",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="permit an explicitly empty semantic AnnotationSet",
    )
    parser.add_argument("sources", nargs="+", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.schema_only and args.allow_empty:
        parser.error("--allow-empty cannot be combined with --schema-only")
    # Some dependencies install their own warning filters while importing.
    # Recording the warnings prevents both those messages and absolute module
    # paths from breaking the one-line machine-output contract.
    with warnings.catch_warnings(record=True):
        summaries = [
            validate_path(
                source,
                schema_only=args.schema_only,
                allow_empty=args.allow_empty,
            )
            for source in args.sources
        ]
    failed = any(summary["status"] == "failed" for summary in summaries)
    for summary in summaries:
        stream = sys.stderr if summary["status"] == "failed" else sys.stdout
        print(_json_line(summary), file=stream)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
