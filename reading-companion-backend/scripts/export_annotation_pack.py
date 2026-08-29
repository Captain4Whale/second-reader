#!/usr/bin/env python3
"""Explicitly export one Second Reader Annotation Pack publication revision."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
import re
import sys
import warnings


_CODE_RE = re.compile(r"[a-z][a-z0-9_]{0,127}\Z")
_DIGEST_RE = re.compile(r"[0-9a-f]{64}\Z")
_PACK_ID_RE = re.compile(
    r"urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z"
)
_SEVERITIES = frozenset({"fatal", "error", "warning", "skipped"})
_SEVERITY_RANK = {"fatal": 0, "error": 1, "skipped": 2, "warning": 3}
_SUCCESS_STATUSES = frozenset({"published", "degraded", "unchanged"})
_ALL_STATUSES = _SUCCESS_STATUSES | {"failed"}


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


def _empty_counts(*, errors: int) -> dict[str, int]:
    return {
        "input": 0,
        "exported": 0,
        "skipped": 0,
        "warnings": 0,
        "errors": errors,
    }


def _fixed_failure(code: str) -> dict[str, object]:
    return {
        "status": "failed",
        "pack_id": None,
        "semantic_digest": None,
        "input_snapshot_digest": None,
        "revision_id": None,
        "counts": _empty_counts(errors=1),
        "findings": [
            {
                "code": code,
                "severity": "fatal",
                "source_record_index": None,
                "source_record_digest": None,
            }
        ],
    }


def _safe_pack_value(pack: object, *path: str) -> object:
    value = pack
    for part in path:
        if not isinstance(value, Mapping):
            return None
        value = value.get(part)
    return value


def _result_summary(result: object) -> dict[str, object]:
    status = getattr(result, "status", None)
    validation = getattr(result, "validation", None)
    if status not in _ALL_STATUSES or validation is None:
        return _fixed_failure("unexpected_internal_error")

    raw_findings = getattr(validation, "findings", None)
    if not isinstance(raw_findings, (tuple, list)):
        return _fixed_failure("unexpected_internal_error")
    findings = [_safe_finding(finding) for finding in raw_findings]
    findings.sort(key=_finding_sort_key)

    count_fields = (
        ("input", "input_count"),
        ("exported", "exported_count"),
        ("skipped", "skipped_count"),
        ("warnings", "warning_count"),
        ("errors", "error_count"),
    )
    counts = {
        public_name: _safe_nonnegative_int(getattr(validation, attribute, None))
        for public_name, attribute in count_fields
    }
    if any(value is None for value in counts.values()):
        return _fixed_failure("unexpected_internal_error")

    pack = getattr(result, "pack", None)
    pack_id = _safe_pack_id(getattr(validation, "pack_id", None))
    if pack_id is None:
        pack_id = _safe_pack_id(_safe_pack_value(pack, "id"))
    semantic_digest = _safe_digest(getattr(validation, "semantic_digest", None))
    input_snapshot_digest = _safe_digest(
        getattr(validation, "input_snapshot_digest", None)
    )

    return {
        "status": status,
        "pack_id": pack_id,
        "semantic_digest": semantic_digest,
        "input_snapshot_digest": input_snapshot_digest,
        "revision_id": _safe_digest(getattr(result, "revision_id", None)),
        "counts": counts,
        "findings": findings,
    }


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
        print(_json_line(_fixed_failure("cli_usage_error")), file=sys.stderr)
        raise SystemExit(2)


def _parser() -> argparse.ArgumentParser:
    parser = _SafeArgumentParser(
        prog="export_annotation_pack.py",
        description=__doc__,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--book-id")
    source.add_argument("--book-output-dir", type=Path)
    parser.add_argument("--track-key", required=True)
    parser.add_argument("--track-name")
    parser.add_argument(
        "--creator-type",
        required=True,
        choices=("Software", "Person", "Organization"),
    )
    parser.add_argument("--creator-id", required=True)
    parser.add_argument("--creator-name", required=True)
    parser.add_argument(
        "--deliverables",
        default="detached",
        choices=("json", "detached"),
        help="publish detached JSON+package by default; use json for development-only output",
    )
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--allow-skips", action="store_true")
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--force-regenerate", action="store_true")
    parser.add_argument(
        "--producer-format",
        default="reading-product-v1",
        choices=("reading-product-v1", "attentional-v2-phase9-legacy"),
        help="read a complete Reading Product by default; phase9 is explicit legacy input",
    )
    return parser


def _execute(args: argparse.Namespace) -> dict[str, object]:
    """Run the product operation and return one already-sanitized summary."""

    try:
        from src.annotation_pack.builder import CreatorInput
        from src.annotation_pack.exporter import (
            ExportPolicy,
            export_annotation_pack,
            resolve_book_output_dir,
        )
    except Exception:
        return _fixed_failure("unexpected_internal_error")

    try:
        output_dir = resolve_book_output_dir(
            book_id=args.book_id,
            book_output_dir=args.book_output_dir,
        )
    except (OSError, TypeError, ValueError):
        return _fixed_failure("output_path_invalid")
    except Exception:
        return _fixed_failure("unexpected_internal_error")

    try:
        creator = CreatorInput(
            id=args.creator_id,
            type=args.creator_type,
            name=args.creator_name,
        )
        policy = ExportPolicy(
            deliverables=args.deliverables,
            allow_partial=args.allow_partial,
            allow_skips=args.allow_skips,
            allow_empty=args.allow_empty,
            force_regenerate=args.force_regenerate,
        )
        result = export_annotation_pack(
            output_dir=output_dir,
            track_key=args.track_key,
            track_name=args.track_name,
            creator=creator,
            policy=policy,
            producer_format=args.producer_format,
        )
        summary = _result_summary(result)
    except Exception:
        summary = _fixed_failure("unexpected_internal_error")
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    # Some dependencies install their own warning filters while importing.
    # Recording the warnings prevents both those messages and absolute module
    # paths from breaking the one-line machine-output contract.
    with warnings.catch_warnings(record=True):
        summary = _execute(args)

    succeeded = summary["status"] in _SUCCESS_STATUSES
    print(_json_line(summary), file=sys.stdout if succeeded else sys.stderr)
    return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
