"""Strict adapter for current native Second Reader reaction records.

This is the only Annotation Pack module allowed to know where the active
Second Reader mechanism stores its settled reaction ledger.  It deliberately
does not load compatibility chapter output, audits, prompts, memories, or
Digest results, and it never projects mechanism-private fields into drafts.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import NoReturn
import unicodedata

from src.annotation_pack.drafts import (
    AnnotationDraft,
    ProducerAdapterError,
    ProducerDraftResult,
    SourceCoordinate,
    SourceRange,
)
from src.annotation_pack.validation import make_validation_finding
from src.attentional_v2.storage import reaction_records_file


ADAPTER_VERSION = "0.1.0"
SUPPORTED_SCHEMA_VERSION = 1
SUPPORTED_MECHANISM_VERSION = "attentional_v2-phase9"

MAX_REACTION_LEDGER_BYTES = 16 * 1024 * 1024
MAX_REACTION_RECORDS = 2_000
MAX_REACTION_LEDGER_JSON_DEPTH = 64
MAX_REACTION_LEDGER_JSON_NODES = 100_000
MAX_REACTION_LEDGER_SINGLE_STRING_CODE_POINTS = 64 * 1024
MAX_REACTION_LEDGER_TOTAL_STRING_CODE_POINTS = 16 * 1024 * 1024
MAX_REACTION_RECORD_CANONICAL_BYTES = 128 * 1024
REACTION_LEDGER_HASH_CHUNK_BYTES = 1024 * 1024
MAX_NOTE_CODE_POINTS = 16_384
MAX_SOURCE_QUOTE_CODE_POINTS = 1_024

_ENVELOPE_KEYS = frozenset(
    {"schema_version", "mechanism_version", "updated_at", "records"}
)
_ROW_ALLOWED_KEYS = frozenset(
    {
        "reaction_id",
        "chapter_id",
        "chapter_ref",
        "emitted_at_source_span_id",
        "record_source",
        "type",
        "compat_family",
        "marginalia_kind",
        "thought",
        "source_quote",
        "primary_source_ref",
        "related_source_refs",
        "reconsolidation_record_id",
        "supersedes_reaction_id",
        "compatibility_section_ref",
        "prior_link",
        "outside_link",
        "search_intent",
        "search_query",
        "search_results",
        "created_at",
    }
)
_ROW_REQUIRED_KEYS = frozenset(
    {
        "record_source",
        "marginalia_kind",
        "source_quote",
        "primary_source_ref",
        "created_at",
    }
)
_PRIMARY_REF_ALLOWED_KEYS = frozenset(
    {"source_span_id", "source_span", "quote", "role", "resolution"}
)
_PRIMARY_REF_REQUIRED_KEYS = frozenset({"source_span", "quote", "resolution"})
_SOURCE_SPAN_KEYS = frozenset({"start_cursor", "end_cursor"})
_CURSOR_ALLOWED_KEYS = frozenset(
    {"chapter_id", "chapter_ref", "paragraph_index", "char_offset"}
)
_CURSOR_REQUIRED_KEYS = frozenset(
    {"chapter_id", "paragraph_index", "char_offset"}
)
_RESOLUTION_KEYS = frozenset({"status", "method", "match_count"})
_UTC_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?Z\Z"
)
_MISSING = object()


class _DuplicateJsonKey(ValueError):
    pass


class _RejectedRow(ValueError):
    __slots__ = ("code",)

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SecondReaderProducerAdapter:
    """Load one stable current-native reaction ledger into neutral drafts."""

    def load_drafts(self, *, output_dir: Path) -> ProducerDraftResult:
        """Return accepted drafts plus exact ledger and row provenance.

        Ledger-level failures raise :class:`ProducerAdapterError`; row-level
        failures are returned as catalog-owned findings so later export policy
        can choose strict failure or explicit skipping without heuristic repair.
        """

        try:
            ledger_path = reaction_records_file(output_dir)
        except Exception:
            _fail("reaction_ledger_unavailable")
        ledger_bytes, ledger_sha256 = _read_ledger_bytes(ledger_path)
        document = _parse_strict_json(ledger_bytes)
        _enforce_document_limits(document)
        records = _supported_records(document)

        drafts: list[AnnotationDraft] = []
        findings = []
        accepted_record_digests: list[str] = []
        for index, row in enumerate(records):
            row_bytes = _canonical_record_bytes(row)
            record_digest = hashlib.sha256(row_bytes).hexdigest()
            try:
                draft = _draft_from_row(
                    row,
                    index=index,
                    record_digest=record_digest,
                )
            except _RejectedRow as exc:
                findings.append(
                    make_validation_finding(
                        exc.code,
                        "error",
                        source_record_index=index,
                        json_pointer=f"/records/{index}",
                        source_record_digest=record_digest,
                    )
                )
                continue
            drafts.append(draft)
            accepted_record_digests.append(record_digest)

        return ProducerDraftResult(
            drafts=tuple(drafts),
            reaction_ledger_sha256=ledger_sha256,
            accepted_record_digests=tuple(accepted_record_digests),
            findings=tuple(findings),
            input_count=len(records),
        )


def _read_ledger_bytes(path: Path) -> tuple[bytes, str]:
    descriptor, parent_descriptor, leaf_name = _open_ledger_nofollow(
        path,
        failure_code="reaction_ledger_unavailable",
    )

    try:
        try:
            before = os.fstat(descriptor)
            before_path = os.stat(
                leaf_name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except (OSError, TypeError, ValueError):
            _fail("reaction_ledger_unavailable")
        if not stat.S_ISREG(before.st_mode):
            _fail("reaction_ledger_unavailable")
        if _stat_identity(before) != _stat_identity(before_path):
            _fail("input_changed_during_export")
        if before.st_size > MAX_REACTION_LEDGER_BYTES:
            _fail("reaction_ledger_limit_exceeded")

        chunks: list[bytes] = []
        digest = hashlib.sha256()
        total = 0
        while True:
            try:
                chunk = os.read(descriptor, REACTION_LEDGER_HASH_CHUNK_BYTES)
            except InterruptedError:
                continue
            except OSError:
                _fail("reaction_ledger_unavailable")
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_REACTION_LEDGER_BYTES:
                _fail("reaction_ledger_limit_exceeded")
            digest.update(chunk)
            chunks.append(chunk)

        try:
            after = os.fstat(descriptor)
            after_path = os.stat(
                leaf_name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except (OSError, TypeError, ValueError):
            _fail("input_changed_during_export")
        reopened, reopened_parent, _reopened_leaf = _open_ledger_nofollow(
            path,
            failure_code="input_changed_during_export",
        )
        try:
            try:
                reopened_stat = os.fstat(reopened)
            except OSError:
                _fail("input_changed_during_export")
        finally:
            _close_descriptor(reopened)
            _close_descriptor(reopened_parent)
        if (
            _stat_identity(before) != _stat_identity(after)
            or _stat_identity(after) != _stat_identity(after_path)
            or _stat_identity(after) != _stat_identity(reopened_stat)
            or total != before.st_size
            or total != after.st_size
        ):
            _fail("input_changed_during_export")
        return b"".join(chunks), digest.hexdigest()
    finally:
        _close_descriptor(descriptor)
        _close_descriptor(parent_descriptor)


def _open_ledger_nofollow(
    path: Path,
    *,
    failure_code: str,
) -> tuple[int, int, str]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None:
        _fail(failure_code)
    try:
        absolute = os.path.abspath(os.fspath(path))
    except (OSError, TypeError, ValueError):
        _fail(failure_code)
    components = tuple(component for component in absolute.split(os.sep) if component)
    if not components:
        _fail(failure_code)

    directory_flags = (
        os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow | directory
    )
    try:
        current = os.open(os.sep, directory_flags)
    except (OSError, TypeError, ValueError):
        _fail(failure_code)
    try:
        for component in components[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
            except (OSError, TypeError, ValueError):
                _fail(failure_code)
            _close_descriptor(current)
            current = child
        file_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow
        try:
            descriptor = os.open(components[-1], file_flags, dir_fd=current)
        except (OSError, TypeError, ValueError):
            _fail(failure_code)
        return descriptor, current, components[-1]
    except BaseException:
        _close_descriptor(current)
        raise


def _close_descriptor(descriptor: int) -> None:
    try:
        os.close(descriptor)
    except OSError:
        pass


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _parse_strict_json(payload: bytes) -> object:
    if payload.startswith(b"\xef\xbb\xbf"):
        _fail("reaction_ledger_invalid_json")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        _fail("reaction_ledger_invalid_json")
    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except RecursionError:
        _fail("reaction_ledger_limit_exceeded")
    except Exception:
        _fail("reaction_ledger_invalid_json")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey("duplicate JSON object key")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> NoReturn:
    raise ValueError("non-finite JSON number")


def _enforce_document_limits(document: object) -> None:
    nodes = 0
    string_code_points = 0
    stack: list[tuple[object, int]] = [(document, 1)]
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if (
            nodes > MAX_REACTION_LEDGER_JSON_NODES
            or depth > MAX_REACTION_LEDGER_JSON_DEPTH
        ):
            _fail("reaction_ledger_limit_exceeded")
        if isinstance(value, dict):
            for key, child in value.items():
                string_code_points += _checked_string_length(key)
                if (
                    string_code_points
                    > MAX_REACTION_LEDGER_TOTAL_STRING_CODE_POINTS
                ):
                    _fail("reaction_ledger_limit_exceeded")
                stack.append((child, depth + 1))
        elif isinstance(value, list):
            stack.extend((child, depth + 1) for child in value)
        elif isinstance(value, str):
            string_code_points += _checked_string_length(value)
            if (
                string_code_points
                > MAX_REACTION_LEDGER_TOTAL_STRING_CODE_POINTS
            ):
                _fail("reaction_ledger_limit_exceeded")
        elif value is None or isinstance(value, (bool, int, float)):
            continue
        else:  # pragma: no cover - json.loads produces only the cases above
            _fail("reaction_ledger_invalid_json")


def _checked_string_length(value: str) -> int:
    if len(value) > MAX_REACTION_LEDGER_SINGLE_STRING_CODE_POINTS:
        _fail("reaction_ledger_limit_exceeded")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        _fail("reaction_ledger_invalid_json")
    return len(value)


def _supported_records(document: object) -> list[object]:
    if not isinstance(document, dict) or frozenset(document) != _ENVELOPE_KEYS:
        _fail("reaction_ledger_schema_unsupported")
    if (
        type(document["schema_version"]) is not int
        or document["schema_version"] != SUPPORTED_SCHEMA_VERSION
        or type(document["mechanism_version"]) is not str
        or document["mechanism_version"] != SUPPORTED_MECHANISM_VERSION
        or _timestamp_or_none(document["updated_at"]) is None
        or type(document["records"]) is not list
    ):
        _fail("reaction_ledger_schema_unsupported")
    records = document["records"]
    if len(records) > MAX_REACTION_RECORDS:
        _fail("reaction_ledger_limit_exceeded")
    return records


def _canonical_record_bytes(row: object) -> bytes:
    try:
        encoded = json.dumps(
            row,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8") + b"\n"
    except Exception:
        _fail("reaction_ledger_invalid_json")
    if len(encoded) > MAX_REACTION_RECORD_CANONICAL_BYTES:
        _fail("reaction_ledger_limit_exceeded")
    return encoded


def _draft_from_row(
    row: object,
    *,
    index: int,
    record_digest: str,
) -> AnnotationDraft:
    if not isinstance(row, dict) or not _supported_key_subset(
        row,
        required=_ROW_REQUIRED_KEYS,
        allowed=_ROW_ALLOWED_KEYS,
    ):
        raise _RejectedRow("unsupported_legacy_record")
    if (
        type(row["record_source"]) is not str
        or row["record_source"] != "read_surface"
    ):
        raise _RejectedRow("unsupported_legacy_record")

    kind = row["marginalia_kind"]
    if type(kind) is not str or kind not in {"highlight", "note"}:
        if kind is None or kind == "":
            raise _RejectedRow("unsupported_legacy_record")
        raise _RejectedRow("unsupported_kind")
    thought = row.get("thought", _MISSING)
    if kind == "highlight":
        if thought is not _MISSING and (
            type(thought) is not str or thought != ""
        ):
            raise _RejectedRow("highlight_body_present")
    elif type(thought) is not str:
        raise _RejectedRow("note_body_missing")
    normalized_thought: str | None = None
    if kind == "note":
        try:
            normalized_thought = unicodedata.normalize("NFC", thought)
            normalized_thought.encode("utf-8")
        except (TypeError, UnicodeEncodeError, ValueError):
            raise _RejectedRow("note_body_missing") from None
        if (
            not normalized_thought.strip()
            or len(normalized_thought) > MAX_NOTE_CODE_POINTS
        ):
            raise _RejectedRow("note_body_missing")

    created_at = _timestamp_or_none(row["created_at"])
    if created_at is None:
        raise _RejectedRow("invalid_annotation_timestamp")

    source_quote = row["source_quote"]
    if type(source_quote) is not str or not source_quote:
        raise _RejectedRow("unresolved_source_quote")
    if len(source_quote) > MAX_SOURCE_QUOTE_CODE_POINTS:
        raise _RejectedRow("source_quote_too_long")

    primary_ref = row["primary_source_ref"]
    if not isinstance(primary_ref, dict) or not _supported_key_subset(
        primary_ref,
        required=_PRIMARY_REF_REQUIRED_KEYS,
        allowed=_PRIMARY_REF_ALLOWED_KEYS,
    ):
        raise _RejectedRow("unsupported_legacy_record")
    if type(primary_ref["quote"]) is not str or primary_ref["quote"] != source_quote:
        raise _RejectedRow("unresolved_source_quote")

    resolution = primary_ref["resolution"]
    if not isinstance(resolution, dict) or frozenset(resolution) != _RESOLUTION_KEYS:
        raise _RejectedRow("unresolved_source_quote")
    status = resolution["status"]
    method = resolution["method"]
    match_count = resolution["match_count"]
    if type(status) is not str or type(method) is not str:
        raise _RejectedRow("unresolved_source_quote")
    if (
        status == "ambiguous_first_match"
        or type(match_count) is not int
        or match_count != 1
    ):
        raise _RejectedRow("ambiguous_source_quote")
    if status != "matched" or method != "exact_text":
        raise _RejectedRow("unresolved_source_quote")

    source_range = _source_range(primary_ref["source_span"])
    return AnnotationDraft(
        kind=kind,
        source_range=source_range,
        source_quote=source_quote,
        body_text=normalized_thought,
        created_at=created_at,
        source_record_index=index,
        source_record_digest=record_digest,
    )


def _source_range(
    value: object,
) -> SourceRange:
    if not isinstance(value, dict) or frozenset(value) != _SOURCE_SPAN_KEYS:
        raise _RejectedRow("malformed_source_span")
    start_value = value["start_cursor"]
    end_value = value["end_cursor"]
    start = _coordinate(start_value)
    end = _coordinate(end_value)
    if start.chapter_id != end.chapter_id:
        raise _RejectedRow("malformed_source_span")
    if (start.paragraph_index, start.char_offset) >= (
        end.paragraph_index,
        end.char_offset,
    ):
        raise _RejectedRow("malformed_source_span")
    return SourceRange(start=start, end=end)


def _coordinate(value: object) -> SourceCoordinate:
    if not isinstance(value, dict) or not _supported_key_subset(
        value,
        required=_CURSOR_REQUIRED_KEYS,
        allowed=_CURSOR_ALLOWED_KEYS,
    ):
        raise _RejectedRow("malformed_source_span")
    chapter_id = value["chapter_id"]
    paragraph_index = value["paragraph_index"]
    char_offset = value["char_offset"]
    if (
        type(chapter_id) is not int
        or chapter_id < 1
        or type(paragraph_index) is not int
        or paragraph_index < 1
        or type(char_offset) is not int
        or char_offset < 0
    ):
        raise _RejectedRow("malformed_source_span")
    return SourceCoordinate(
        chapter_id=chapter_id,
        paragraph_index=paragraph_index,
        char_offset=char_offset,
    )


def _supported_key_subset(
    value: dict[object, object],
    *,
    required: frozenset[str],
    allowed: frozenset[str],
) -> bool:
    keys = frozenset(value)
    return required.issubset(keys) and keys.issubset(allowed)


def _timestamp_or_none(value: object) -> datetime | None:
    if type(value) is not str or _UTC_TIMESTAMP.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _fail(code: str) -> NoReturn:
    raise ProducerAdapterError(code) from None


__all__ = [
    "ADAPTER_VERSION",
    "MAX_REACTION_LEDGER_BYTES",
    "MAX_REACTION_LEDGER_JSON_DEPTH",
    "MAX_REACTION_LEDGER_JSON_NODES",
    "MAX_REACTION_LEDGER_SINGLE_STRING_CODE_POINTS",
    "MAX_REACTION_LEDGER_TOTAL_STRING_CODE_POINTS",
    "MAX_REACTION_RECORDS",
    "MAX_REACTION_RECORD_CANONICAL_BYTES",
    "REACTION_LEDGER_HASH_CHUNK_BYTES",
    "SUPPORTED_MECHANISM_VERSION",
    "SUPPORTED_SCHEMA_VERSION",
    "SecondReaderProducerAdapter",
]
