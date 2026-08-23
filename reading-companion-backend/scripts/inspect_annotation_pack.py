#!/usr/bin/env python3
"""Inspect one Annotation Pack JSON file and emit only public-safe metadata."""

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
_UUID5_RE = re.compile(
    r"urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z"
)
_SEVERITIES = frozenset({"fatal", "error", "warning", "skipped"})
_SEVERITY_RANK = {"fatal": 0, "error": 1, "skipped": 2, "warning": 3}
_COUNT_KEYS = frozenset({"total", "highlight", "note"})
_ANCHOR_CAPABILITIES = frozenset(
    {
        "TextQuoteSelector",
        "sr:ParagraphCharSelector",
        "sr:EpubCfiSelector",
        "epubcfi",
    }
)
_ANCHOR_ORDER = {
    "TextQuoteSelector": 0,
    "sr:ParagraphCharSelector": 1,
    "sr:EpubCfiSelector": 2,
    "epubcfi": 3,
}


def _safe_digest(value: object) -> str | None:
    return value if type(value) is str and _DIGEST_RE.fullmatch(value) else None


def _safe_uuid5(value: object) -> str | None:
    return value if type(value) is str and _UUID5_RE.fullmatch(value) else None


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


def _fixed_failure(code: str = "unexpected_internal_error") -> dict[str, object]:
    return {
        "valid": False,
        "pack_id": None,
        "track_id": None,
        "semantic_digest": None,
        "item_counts": {"highlight": 0, "note": 0, "total": 0},
        "anchor_capabilities": [],
        "findings": [
            {
                "code": code,
                "severity": "fatal",
                "source_record_index": None,
                "source_record_digest": None,
            }
        ],
    }


def _inspection_summary(result: object) -> dict[str, object]:
    valid = getattr(result, "valid", None)
    raw_counts = getattr(result, "item_counts", None)
    raw_capabilities = getattr(result, "anchor_capabilities", None)
    raw_findings = getattr(result, "findings", None)
    if type(valid) is not bool or not isinstance(raw_counts, Mapping):
        raise ValueError("invalid inspection result")
    if type(raw_capabilities) is not tuple or type(raw_findings) is not tuple:
        raise ValueError("invalid inspection result")

    counts = dict(raw_counts)
    if set(counts) != _COUNT_KEYS:
        raise ValueError("invalid inspection result")
    sanitized_counts = {
        key: _safe_nonnegative_int(counts[key])
        for key in ("highlight", "note", "total")
    }
    if any(value is None for value in sanitized_counts.values()):
        raise ValueError("invalid inspection result")
    if valid and sanitized_counts["total"] != (
        sanitized_counts["highlight"] + sanitized_counts["note"]
    ):
        raise ValueError("invalid inspection result")

    if any(
        type(capability) is not str or capability not in _ANCHOR_CAPABILITIES
        for capability in raw_capabilities
    ):
        raise ValueError("invalid inspection result")
    capabilities = sorted(set(raw_capabilities), key=_ANCHOR_ORDER.__getitem__)
    findings = [_safe_finding(finding) for finding in raw_findings]
    findings.sort(key=_finding_sort_key)
    return {
        "valid": valid,
        "pack_id": _safe_uuid5(getattr(result, "pack_id", None)),
        "track_id": _safe_uuid5(getattr(result, "track_id", None)),
        "semantic_digest": _safe_digest(
            getattr(result, "semantic_digest", None)
        ),
        "item_counts": sanitized_counts,
        "anchor_capabilities": capabilities,
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
        prog="inspect_annotation_pack.py",
        description=__doc__,
    )
    parser.add_argument("source", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    # Some dependencies install their own warning filters while importing.
    # Recording the warnings prevents both those messages and absolute module
    # paths from breaking the one-line machine-output contract.
    with warnings.catch_warnings(record=True):
        try:
            from src.annotation_pack.exporter import inspect_annotation_pack

            summary = _inspection_summary(inspect_annotation_pack(args.source))
        except Exception:
            summary = _fixed_failure()
    print(_json_line(summary), file=sys.stdout if summary["valid"] else sys.stderr)
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
