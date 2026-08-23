#!/usr/bin/env python3
"""Validate Annotation Pack v0 JSON examples against the canonical schema.

Slice 1 supports JSON Pack documents and contract Annotation item examples. The
CLI is extended with semantic and detached-package validation in later slices.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from src.annotation_pack.schema import annotation_validator, pack_validator


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains the same member name twice."""


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_object_without_duplicate_keys,
    )


def _error_path(error: Any) -> str:
    if not error.absolute_path:
        return ""
    escaped = (
        str(part).replace("~", "~0").replace("/", "~1") for part in error.absolute_path
    )
    return "/" + "/".join(escaped)


def validate_path(path: Path) -> list[str]:
    try:
        document = _load_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        return [f"{path}: invalid JSON: {exc}"]
    if not isinstance(document, dict):
        return [f"{path}: root must be an object"]

    document_type = document.get("type")
    if document_type == "AnnotationSet":
        validator = pack_validator()
    elif document_type == "Annotation":
        validator = annotation_validator()
    else:
        return [f"{path}: unsupported root type: {document_type!r}"]

    return [
        f"{path}{_error_path(error)}: {error.message}"
        for error in sorted(
            validator.iter_errors(document),
            key=lambda item: tuple(str(part) for part in item.path),
        )
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path)
    args = parser.parse_args()

    failures: list[str] = []
    for source in args.sources:
        failures.extend(validate_path(source))
        if not failures or not any(line.startswith(f"{source}") for line in failures):
            print(f"valid: {source}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
