"""Unit Memory ledger and retrieval index for attentional_v2."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import re
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schemas import (
    ATTENTIONAL_V2_MECHANISM_VERSION,
    MemoryRetrievalMode,
    UnitMemoryEntry,
    UnitMemoryQuery,
    UnitMemoryRecall,
)
from .memory_tokens import token_estimate_payload
from .storage import (
    append_jsonl,
    load_json,
    memory_retrieval_config_file,
    save_json,
    unit_memory_retrieval_trace_file,
    unit_memory_sqlite_file,
)


UNIT_MEMORY_ENTRY_SCHEMA_VERSION = "unit_memory_entry.v2"
UNIT_MEMORY_QUERY_VERSION = "unit_memory_query.v1"
UNIT_MEMORY_RECALL_QUERY_VERSION = "unit_memory_recall_query.v1"
UNIT_MEMORY_RETRIEVAL_CONFIG_SCHEMA_VERSION = "unit_memory_retrieval_config.v1"
UNIT_MEMORY_QUERY_INSTRUCTION_VERSION = "unit_memory_query_instruction.v1"
DEFAULT_MEMORY_RETRIEVAL_MODE: MemoryRetrievalMode = "hybrid"
VALID_MEMORY_RETRIEVAL_MODES: set[str] = {"text_only", "hybrid"}

DEFAULT_RETRIEVAL_CONFIG: dict[str, object] = {
    "schema_version": UNIT_MEMORY_RETRIEVAL_CONFIG_SCHEMA_VERSION,
    "mode": DEFAULT_MEMORY_RETRIEVAL_MODE,
    "default_mode": DEFAULT_MEMORY_RETRIEVAL_MODE,
    "embedding_provider": "ollama",
    "embedding_model": "Qwen3-Embedding-0.6B",
    "ollama_model_id": "qwen3-embedding:0.6b",
    "embedding_dimension": 1024,
    "vector_metric": "cosine",
    "query_instruction_version": UNIT_MEMORY_QUERY_INSTRUCTION_VERSION,
    "lexical_top_k": 40,
    "dense_top_k": 40,
    "dense_max_distance": 0.80,
    "rrf_k": 60,
    "max_units_after_aggregation": 20,
    "max_units_to_digest_context": 40,
    "max_units_per_recall_to_digest_context": 6,
    "max_docs_per_unit_for_scoring": 5,
    "recent_neighbor_exclusion_unit_count": 20,
    "min_retrievable_prior_units": 20,
    "retrieval_total_timeout_ms": 800,
    "query_embedding_timeout_ms": 500,
    "fts_timeout_ms": 100,
    "vector_timeout_ms": 250,
    "aggregation_timeout_ms": 50,
    "vector_index_write_budget_ms": 1000,
}

SURFACE_CHANNEL_WEIGHTS: dict[str, dict[str, float]] = {
    "unit_understanding": {"lexical": 1.35, "dense": 1.35},
    "unit_source": {"lexical": 0.80},
    "unit_annotation": {"lexical": 0.65},
    "unit_response": {"lexical": 0.35},
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalized_query_text(value: object) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def normalize_memory_retrieval_mode(value: object) -> tuple[MemoryRetrievalMode, list[str]]:
    """Normalize one read-time memory retrieval mode."""

    normalized = str(value or "").strip().lower().replace("-", "_")
    if normalized in VALID_MEMORY_RETRIEVAL_MODES:
        return normalized, []  # type: ignore[return-value]
    if normalized:
        return DEFAULT_MEMORY_RETRIEVAL_MODE, [f"invalid_memory_retrieval_mode:{normalized}"]
    return DEFAULT_MEMORY_RETRIEVAL_MODE, []


def _coerce_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: object, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _config_with_mode(
    *,
    mode: MemoryRetrievalMode,
    selected_by: str,
    warnings: list[str] | None = None,
    base: Mapping[str, object] | None = None,
) -> dict[str, object]:
    config = {**DEFAULT_RETRIEVAL_CONFIG, **dict(base or {})}
    config["schema_version"] = UNIT_MEMORY_RETRIEVAL_CONFIG_SCHEMA_VERSION
    config["mode"] = mode
    config["default_mode"] = DEFAULT_MEMORY_RETRIEVAL_MODE
    config["selected_by"] = selected_by
    config["config_warnings"] = list(warnings or [])
    config["updated_at"] = _timestamp()
    return config


def resolve_memory_retrieval_config(
    output_dir: Path,
    mechanism_config: Mapping[str, object] | None,
    *,
    continue_mode: bool = False,
) -> dict[str, object]:
    """Resolve and persist the read-time Unit Memory retrieval config."""

    path = memory_retrieval_config_file(output_dir)
    existing = load_json(path) if path.exists() else {}
    raw_mode = dict(mechanism_config or {}).get("memory_retrieval_mode")
    selected_by = "mechanism_config" if raw_mode is not None else "default"
    if continue_mode and raw_mode is None and existing:
        mode, warnings = normalize_memory_retrieval_mode(existing.get("mode"))
        config = _config_with_mode(mode=mode, selected_by="resume_config", warnings=warnings, base=existing)
        save_json(path, config)
        return config

    if raw_mode is None and existing:
        mode, warnings = normalize_memory_retrieval_mode(existing.get("mode"))
        selected_by = str(existing.get("selected_by", "") or "persisted_config")
    else:
        mode, warnings = normalize_memory_retrieval_mode(raw_mode)
    config = _config_with_mode(mode=mode, selected_by=selected_by, warnings=warnings, base=existing)
    save_json(path, config)
    if continue_mode and raw_mode is not None and existing and str(existing.get("mode")) != mode:
        record_unit_memory_retrieval_trace(
            output_dir,
            {
                "event_type": "memory_retrieval_mode_changed_on_resume",
                "previous_mode": str(existing.get("mode", "") or ""),
                "mode": mode,
                "selected_by": selected_by,
                "recorded_at": _timestamp(),
            },
        )
    return config


def record_unit_memory_retrieval_trace(output_dir: Path | None, payload: Mapping[str, object]) -> None:
    """Append one Unit Memory retrieval trace row."""

    if output_dir is None:
        return
    append_jsonl(unit_memory_retrieval_trace_file(output_dir), dict(payload))


def _memory_query_from_value(value: object) -> UnitMemoryQuery:
    if not isinstance(value, Mapping):
        return {}
    query_text = _normalized_query_text(value.get("query_text"))
    if not query_text:
        return {}
    return {
        "query_version": _clean_text(value.get("query_version")) or UNIT_MEMORY_QUERY_VERSION,
        "query_text": query_text,
        "basis": _clean_text(value.get("basis")) or "selected_source_unit",
    }


def normalize_unit_memory_query(value: object) -> UnitMemoryQuery:
    """Normalize one internal Unit Memory retrieval query."""

    return _memory_query_from_value(value)


def normalize_unit_memory_recalls(value: object, *, limit: int = 3) -> list[UnitMemoryRecall]:
    """Normalize bounded Ingest prior-reading recalls."""

    if not isinstance(value, list):
        return []
    recalls: list[UnitMemoryRecall] = []
    seen_texts: set[str] = set()
    for item in value:
        if len(recalls) >= max(0, int(limit)):
            break
        if not isinstance(item, Mapping):
            continue
        recall_text = _normalized_query_text(item.get("recall_text"))
        if not recall_text:
            continue
        dedupe_key = recall_text.lower()
        if dedupe_key in seen_texts:
            continue
        seen_texts.add(dedupe_key)
        recall_id = _clean_text(item.get("recall_id")) or f"r{len(recalls) + 1}"
        basis = _clean_text(item.get("basis"))
        if basis != "runtime_source_text_fallback":
            basis = "selected_source_unit"
        recalls.append(
            {
                "recall_id": recall_id[:24],
                "recall_text": recall_text[:800],
                "basis": basis,
            }
        )
    return recalls


def query_from_recall(recall: Mapping[str, object]) -> UnitMemoryQuery:
    """Convert one reader-facing recall into a runtime retrieval query."""

    recall_text = _normalized_query_text(recall.get("recall_text"))
    if not recall_text:
        return {}
    return {
        "query_version": UNIT_MEMORY_RECALL_QUERY_VERSION,
        "query_text": recall_text,
        "basis": _clean_text(recall.get("basis")) or "selected_source_unit",
        "recall_id": _clean_text(recall.get("recall_id")),
    }


def fallback_query_from_source_unit(source_unit: Mapping[str, object] | None, *, limit: int = 1200) -> UnitMemoryQuery:
    """Build a runtime fallback retrieval query from accepted source text."""

    if not isinstance(source_unit, Mapping):
        return {}
    source_text = _normalized_query_text(source_unit.get("source_text"))
    if not source_text:
        pieces = [
            _normalized_query_text(item.get("text"))
            for item in source_unit.get("paragraph_slices", [])
            if isinstance(item, Mapping)
        ]
        source_text = _normalized_query_text(" ".join(piece for piece in pieces if piece))
    if not source_text:
        return {}
    return {
        "query_version": UNIT_MEMORY_QUERY_VERSION,
        "query_text": source_text[:limit],
        "basis": "runtime_source_text_fallback",
    }


def effective_query_for_accepted_unit(
    *,
    ingest_query: Mapping[str, object] | None,
    source_unit: Mapping[str, object] | None,
    boundary_was_retried: bool = False,
    boundary_resolution_status: str = "",
) -> tuple[UnitMemoryQuery, str]:
    """Return the query that should drive retrieval for the accepted source unit."""

    normalized = normalize_unit_memory_query(ingest_query)
    if (
        normalized
        and not boundary_was_retried
        and str(boundary_resolution_status or "").strip().lower() not in {"fallback", "unresolved_anchor"}
    ):
        return normalized, "ingest_output"
    fallback = fallback_query_from_source_unit(source_unit)
    return fallback, "runtime_source_text_fallback" if fallback else "empty"


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _json_dumps(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _json_loads(value: object, default: object) -> object:
    if not isinstance(value, str) or not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _entry_understanding_content(entry: object) -> str:
    if not isinstance(entry, Mapping):
        return ""
    digest = entry.get("digest")
    if not isinstance(digest, Mapping):
        return ""
    understanding = digest.get("understanding")
    if isinstance(understanding, Mapping):
        return _clean_text(understanding.get("content"))
    if isinstance(understanding, str):
        return _clean_text(understanding)
    return ""


def _compact_retrieval_unit(item: Mapping[str, object]) -> dict[str, object]:
    return {
        "unit_id": item.get("unit_id"),
        "unit_index": item.get("unit_index"),
        "score": item.get("score"),
        "matched_recalls": item.get("matched_recalls"),
        "surfaces": item.get("surfaces"),
        "channels": item.get("channels"),
        "best_docs": item.get("best_docs"),
    }


def _understanding_from_digest_result(digest_result: Mapping[str, object]) -> dict[str, object]:
    for operation in digest_result.get("memory_uptake_ops", []):
        if not isinstance(operation, Mapping):
            continue
        if str(operation.get("target_store", "") or "") != "recent_reading_memory":
            continue
        payload = operation.get("payload")
        if not isinstance(payload, Mapping):
            continue
        content = _clean_text(payload.get("memory_text"))
        if not content:
            continue
        return {
            "content": content,
            "token_estimate": token_estimate_payload(content),
        }
    return {"content": "", "token_estimate": token_estimate_payload("")}


def build_unit_memory_entry(
    *,
    book_id: str,
    chapter_id: int,
    chapter_ref: str,
    source_unit: Mapping[str, object],
    digest_result: Mapping[str, object],
    memory_retrieval_mode: MemoryRetrievalMode,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> UnitMemoryEntry:
    """Build one append-only Unit Memory entry from a completed read unit."""

    unit_id = _clean_text(source_unit.get("unit_id"))
    unit_index = _coerce_int(source_unit.get("sequence_index"), 0)
    source_span_id = _clean_text(source_unit.get("source_span_id"))
    annotations = [
        dict(item)
        for item in digest_result.get("surfaced_reactions", [])
        if isinstance(item, Mapping)
    ] if isinstance(digest_result.get("surfaced_reactions"), list) else []
    return {
        "unit_id": unit_id,
        "book_id": _clean_text(book_id),
        "schema_version": UNIT_MEMORY_ENTRY_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "created_at": _timestamp(),
        "chapter_id": int(chapter_id),
        "chapter_ref": _clean_text(chapter_ref),
        "unit_index": unit_index,
        "source_span_id": source_span_id,
        "accepted_source_unit": dict(source_unit),
        "digest": {
            "understanding": _understanding_from_digest_result(digest_result),
            "response": _clean_text(digest_result.get("reading_impression")),
            "annotations": annotations,
        },
        "index_status": {
            "fts": "pending",
            "vector": "pending" if memory_retrieval_mode == "hybrid" else "not_requested",
            "last_error": None,
        },
        "memory_retrieval_mode": memory_retrieval_mode,
    }


def _doc_text(value: object) -> str:
    return _normalized_query_text(value)


def retrieval_docs_from_entry(entry: Mapping[str, object]) -> list[dict[str, object]]:
    """Derive field-specific retrieval documents from one Unit Memory entry."""

    unit_id = _clean_text(entry.get("unit_id"))
    book_id = _clean_text(entry.get("book_id"))
    source_span_id = _clean_text(entry.get("source_span_id"))
    source_unit = entry.get("accepted_source_unit")
    source_unit = dict(source_unit) if isinstance(source_unit, Mapping) else {}
    digest = entry.get("digest")
    digest = dict(digest) if isinstance(digest, Mapping) else {}
    docs: list[dict[str, object]] = []

    for index, item in enumerate(source_unit.get("paragraph_slices", []), start=1):
        if not isinstance(item, Mapping):
            continue
        text = _doc_text(item.get("text"))
        if not text:
            continue
        docs.append(
            {
                "retrieval_doc_id": f"{unit_id}#source:{index}",
                "unit_id": unit_id,
                "book_id": book_id,
                "surface": "unit_source",
                "weight_profile": "source_default",
                "text": text,
                "source_span_id": source_span_id,
            }
        )

    understanding = digest.get("understanding")
    if isinstance(understanding, Mapping):
        text = _doc_text(understanding.get("content"))
        if text:
            docs.append(
                {
                    "retrieval_doc_id": f"{unit_id}#understanding",
                    "unit_id": unit_id,
                    "book_id": book_id,
                    "surface": "unit_understanding",
                    "weight_profile": "understanding_default",
                    "text": text,
                    "source_span_id": source_span_id,
                }
            )

    response = _doc_text(digest.get("response"))
    if response:
        docs.append(
            {
                "retrieval_doc_id": f"{unit_id}#response",
                "unit_id": unit_id,
                "book_id": book_id,
                "surface": "unit_response",
                "weight_profile": "response_default",
                "text": response,
                "source_span_id": source_span_id,
            }
        )

    annotations = digest.get("annotations", [])
    if isinstance(annotations, list):
        for index, annotation in enumerate(annotations, start=1):
            if not isinstance(annotation, Mapping):
                continue
            quote = _doc_text(annotation.get("source_quote"))
            content = _doc_text(annotation.get("content"))
            text = "\n".join(item for item in (quote, content) if item)
            if not text:
                continue
            docs.append(
                {
                    "retrieval_doc_id": f"{unit_id}#annotation:{index}",
                    "unit_id": unit_id,
                    "book_id": book_id,
                    "surface": "unit_annotation",
                    "weight_profile": "annotation_default",
                    "text": text,
                    "source_span_id": source_span_id,
                }
            )
    return docs


def build_fts5_match_query(query_text: object) -> tuple[str, str]:
    """Build a safe FTS5 phrase query for the trigram lexical index."""

    normalized = _normalized_query_text(query_text)
    if len(normalized) < 3:
        return "", "empty_or_too_short_query"
    stop_words = {
        "about",
        "again",
        "earlier",
        "from",
        "into",
        "paragraph",
        "prior",
        "reading",
        "recall",
        "the",
        "this",
        "unit",
    }
    lexical_text = normalized
    for pattern in (
        r"先前阅读中",
        r"此前阅读中",
        r"早前阅读中",
        r"前文中",
        r"本段",
        r"本单元",
        r"这一段",
        r"这一单元",
        r"第\d+段",
        r"paragraph\s*\d+",
        r"earlier reading",
        r"prior reading",
        r"recall",
    ):
        lexical_text = re.sub(pattern, " ", lexical_text, flags=re.IGNORECASE)
    lexical_text = _normalized_query_text(lexical_text)
    phrases: list[str] = []

    def add_phrase(value: str, *, max_len: int = 80) -> None:
        value = _normalized_query_text(value)
        if len(value) < 3:
            return
        escaped = value[:max_len].replace('"', '""')
        phrase = f'"{escaped}"'
        if phrase not in phrases:
            phrases.append(phrase)

    parts = re.split(r"[。！？!?；;\n\r]+", lexical_text)
    for part in parts:
        candidate = _normalized_query_text(part)
        candidate_values = [candidate]
        if re.search(r"\s", candidate):
            compact_candidate = _normalized_query_text(re.sub(r"\s+", "", candidate))
            if compact_candidate:
                candidate_values.append(compact_candidate)
            candidate_values.extend(_normalized_query_text(item) for item in re.split(r"\s+", candidate))
        for candidate_value in candidate_values:
            add_phrase(candidate_value)
            if len(phrases) >= 12:
                break
        if len(phrases) >= 12:
            break

    for token in re.findall(r"[A-Za-z][A-Za-z0-9_'-]{2,}", lexical_text):
        cleaned = token.strip("'\"")
        if cleaned.lower() in stop_words:
            continue
        add_phrase(cleaned, max_len=40)
        if len(phrases) >= 20:
            break

    cjk_text = re.sub(r"[^\u4e00-\u9fff]+", "", lexical_text)
    for length in (3, 4):
        for index in range(0, max(0, len(cjk_text) - length + 1)):
            chunk = cjk_text[index : index + length]
            if chunk in {"先前", "此前", "早前", "阅读中"}:
                continue
            add_phrase(chunk, max_len=8)
            if len(phrases) >= 28:
                break
        if len(phrases) >= 28:
            break
    if not phrases:
        return "", "empty_or_too_short_query"
    return " OR ".join(phrases), ""


class OllamaEmbedder:
    """Tiny local Ollama embedding client."""

    def __init__(
        self,
        *,
        model_id: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_ms: int = 500,
    ) -> None:
        self.model_id = model_id
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = max(0.05, timeout_ms / 1000)

    def embed(self, text: str) -> list[float] | None:
        payload = json.dumps({"model": self.model_id, "input": text}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/embed",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return None
        embeddings = data.get("embeddings")
        if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
            return [float(item) for item in embeddings[0]]
        embedding = data.get("embedding")
        if isinstance(embedding, list):
            return [float(item) for item in embedding]
        return None


class UnitMemoryIndex:
    """SQLite-backed Unit Memory ledger and retrieval adapter."""

    def __init__(self, output_dir: Path, *, config: Mapping[str, object] | None = None) -> None:
        self.output_dir = output_dir
        self.db_path = unit_memory_sqlite_file(output_dir)
        self.config = {**DEFAULT_RETRIEVAL_CONFIG, **dict(config or {})}
        self._sqlite_vec: Any | None = None
        self._vector_available: bool | None = None
        self._vector_unavailable_reason = ""

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _load_sqlite_vec(self, connection: sqlite3.Connection) -> bool:
        if self._vector_available is not None:
            if self._vector_available and self._sqlite_vec is not None:
                try:
                    if hasattr(connection, "enable_load_extension"):
                        connection.enable_load_extension(True)
                    self._sqlite_vec.load(connection)
                    if hasattr(connection, "enable_load_extension"):
                        connection.enable_load_extension(False)
                except Exception:
                    try:
                        if hasattr(connection, "enable_load_extension"):
                            connection.enable_load_extension(False)
                    except Exception:
                        pass
                    return False
            return bool(self._vector_available)
        try:
            import sqlite_vec  # type: ignore[import-not-found]

            if hasattr(connection, "enable_load_extension"):
                connection.enable_load_extension(True)
            sqlite_vec.load(connection)
            if hasattr(connection, "enable_load_extension"):
                connection.enable_load_extension(False)
        except Exception as exc:
            try:
                if hasattr(connection, "enable_load_extension"):
                    connection.enable_load_extension(False)
            except Exception:
                pass
            self._vector_available = False
            self._vector_unavailable_reason = f"sqlite_vec_unavailable:{type(exc).__name__}"
            return False
        self._sqlite_vec = sqlite_vec
        self._vector_available = True
        self._vector_unavailable_reason = ""
        return True

    def ensure_schema(self) -> None:
        """Create Unit Memory tables and rebuildable indexes when missing."""

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS unit_memory_entries (
                  unit_id TEXT PRIMARY KEY,
                  book_id TEXT NOT NULL,
                  schema_version TEXT NOT NULL,
                  mechanism_version TEXT NOT NULL,
                  chapter_id INTEGER,
                  chapter_ref TEXT,
                  unit_index INTEGER NOT NULL,
                  source_span_id TEXT NOT NULL,
                  source_text TEXT NOT NULL,
                  entry_json TEXT NOT NULL,
                  index_status_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS retrieval_docs (
                  retrieval_doc_pk INTEGER PRIMARY KEY,
                  retrieval_doc_id TEXT NOT NULL UNIQUE,
                  unit_id TEXT NOT NULL,
                  book_id TEXT NOT NULL,
                  surface TEXT NOT NULL,
                  weight_profile TEXT NOT NULL,
                  text TEXT NOT NULL,
                  source_span_id TEXT,
                  text_hash TEXT NOT NULL,
                  embedding_model TEXT,
                  embedding_provider TEXT,
                  embedding_dimension INTEGER,
                  doc_instruction_version TEXT,
                  vector_index_status TEXT NOT NULL DEFAULT 'pending',
                  created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS retrieval_docs_fts USING fts5(
                  text,
                  content='retrieval_docs',
                  content_rowid='retrieval_doc_pk',
                  tokenize='trigram',
                  detail=full,
                  columnsize=1
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS query_embedding_cache (
                  query_hash TEXT NOT NULL,
                  embedding_model TEXT NOT NULL,
                  embedding_dimension INTEGER NOT NULL,
                  query_instruction_version TEXT NOT NULL,
                  embedding_json TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  PRIMARY KEY (
                    query_hash,
                    embedding_model,
                    embedding_dimension,
                    query_instruction_version
                  )
                )
                """
            )
            if self._load_sqlite_vec(connection):
                dimension = _coerce_int(self.config.get("embedding_dimension"), 1024)
                try:
                    connection.execute(
                        f"""
                        CREATE VIRTUAL TABLE IF NOT EXISTS retrieval_doc_vectors USING vec0(
                          embedding float[{dimension}] distance_metric=cosine
                        )
                        """
                    )
                except sqlite3.Error:
                    connection.execute(
                        f"""
                        CREATE VIRTUAL TABLE IF NOT EXISTS retrieval_doc_vectors USING vec0(
                          embedding float[{dimension}]
                        )
                        """
                    )
                    self.config["vector_metric"] = "l2_on_normalized_vectors"
            connection.commit()

    def _delete_docs_for_unit(self, connection: sqlite3.Connection, unit_id: str) -> None:
        rows = connection.execute(
            "SELECT retrieval_doc_pk, text FROM retrieval_docs WHERE unit_id = ?",
            (unit_id,),
        ).fetchall()
        for row in rows:
            try:
                connection.execute(
                    "INSERT INTO retrieval_docs_fts(retrieval_docs_fts, rowid, text) VALUES('delete', ?, ?)",
                    (int(row["retrieval_doc_pk"]), str(row["text"])),
                )
            except sqlite3.Error:
                pass
            try:
                connection.execute("DELETE FROM retrieval_doc_vectors WHERE rowid = ?", (int(row["retrieval_doc_pk"]),))
            except sqlite3.Error:
                pass
        connection.execute("DELETE FROM retrieval_docs WHERE unit_id = ?", (unit_id,))

    def write_entry(self, entry: Mapping[str, object], *, index_vectors: bool = True) -> dict[str, object]:
        """Persist one Unit Memory entry and update rebuildable retrieval docs."""

        self.ensure_schema()
        unit_id = _clean_text(entry.get("unit_id"))
        if not unit_id:
            return {"status": "skipped", "reason": "missing_unit_id"}
        docs = retrieval_docs_from_entry(entry)
        source_unit = entry.get("accepted_source_unit")
        source_text = ""
        if isinstance(source_unit, Mapping):
            source_text = str(source_unit.get("source_text", "") or "")
        index_status = {"fts": "indexed", "vector": "not_requested", "last_error": None}
        with self._connect() as connection:
            self._load_sqlite_vec(connection)
            self._delete_docs_for_unit(connection, unit_id)
            connection.execute(
                """
                INSERT OR REPLACE INTO unit_memory_entries (
                  unit_id, book_id, schema_version, mechanism_version, chapter_id,
                  chapter_ref, unit_index, source_span_id, source_text, entry_json,
                  index_status_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    unit_id,
                    _clean_text(entry.get("book_id")),
                    _clean_text(entry.get("schema_version")) or UNIT_MEMORY_ENTRY_SCHEMA_VERSION,
                    _clean_text(entry.get("mechanism_version")) or ATTENTIONAL_V2_MECHANISM_VERSION,
                    _coerce_int(entry.get("chapter_id"), 0),
                    _clean_text(entry.get("chapter_ref")),
                    _coerce_int(entry.get("unit_index"), 0),
                    _clean_text(entry.get("source_span_id")),
                    source_text,
                    _json_dumps(entry),
                    _json_dumps(index_status),
                    _clean_text(entry.get("created_at")) or _timestamp(),
                ),
            )
            for doc in docs:
                surface = _clean_text(doc.get("surface"))
                cursor = connection.execute(
                    """
                    INSERT INTO retrieval_docs (
                      retrieval_doc_id, unit_id, book_id, surface, weight_profile,
                      text, source_span_id, text_hash, embedding_model,
                      embedding_provider, embedding_dimension, doc_instruction_version,
                      vector_index_status, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        _clean_text(doc.get("retrieval_doc_id")),
                        unit_id,
                        _clean_text(doc.get("book_id")),
                        surface,
                        _clean_text(doc.get("weight_profile")),
                        str(doc.get("text", "") or ""),
                        _clean_text(doc.get("source_span_id")),
                        _stable_hash(str(doc.get("text", "") or "")),
                        str(self.config.get("ollama_model_id", "") or ""),
                        str(self.config.get("embedding_provider", "ollama") or "ollama"),
                        _coerce_int(self.config.get("embedding_dimension"), 1024),
                        "",
                        "pending" if str(self.config.get("mode")) == "hybrid" and surface == "unit_understanding" else "not_requested",
                        _timestamp(),
                    ),
                )
                doc_pk = int(cursor.lastrowid)
                connection.execute(
                    "INSERT INTO retrieval_docs_fts(rowid, text) VALUES (?, ?)",
                    (doc_pk, str(doc.get("text", "") or "")),
                )
            connection.commit()

        if index_vectors and str(self.config.get("mode")) == "hybrid":
            vector_status = self._index_pending_vectors()
            index_status["vector"] = str(vector_status.get("status", "pending"))
            index_status["last_error"] = vector_status.get("last_error")  # type: ignore[assignment]
        else:
            index_status["vector"] = "not_requested"
        with self._connect() as connection:
            connection.execute(
                "UPDATE unit_memory_entries SET index_status_json = ? WHERE unit_id = ?",
                (_json_dumps(index_status), unit_id),
            )
            connection.commit()
        return {"status": "written", "unit_id": unit_id, "retrieval_doc_count": len(docs), "index_status": index_status}

    def _embedding_cache_key(self, text: str) -> tuple[str, str, int, str]:
        return (
            _stable_hash(_normalized_query_text(text)),
            str(self.config.get("ollama_model_id", "qwen3-embedding:0.6b") or "qwen3-embedding:0.6b"),
            _coerce_int(self.config.get("embedding_dimension"), 1024),
            UNIT_MEMORY_QUERY_INSTRUCTION_VERSION,
        )

    def _query_embedding_text(self, query_text: str) -> str:
        return (
            "Instruct: Given the next source unit in an ongoing deep reading of a book, "
            "retrieve prior read units that help understand this unit continuously without summarizing the whole book.\n"
            f"Query: {query_text}"
        )

    def _cached_query_embedding(self, connection: sqlite3.Connection, query_text: str) -> list[float] | None:
        query_hash, model, dimension, instruction_version = self._embedding_cache_key(query_text)
        row = connection.execute(
            """
            SELECT embedding_json FROM query_embedding_cache
            WHERE query_hash = ?
              AND embedding_model = ?
              AND embedding_dimension = ?
              AND query_instruction_version = ?
            """,
            (query_hash, model, dimension, instruction_version),
        ).fetchone()
        if row is None:
            return None
        value = _json_loads(row["embedding_json"], [])
        if isinstance(value, list):
            return [float(item) for item in value]
        return None

    def _save_query_embedding(self, connection: sqlite3.Connection, query_text: str, embedding: list[float]) -> None:
        query_hash, model, dimension, instruction_version = self._embedding_cache_key(query_text)
        connection.execute(
            """
            INSERT OR REPLACE INTO query_embedding_cache (
              query_hash, embedding_model, embedding_dimension,
              query_instruction_version, embedding_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (query_hash, model, dimension, instruction_version, _json_dumps(embedding), _timestamp()),
        )

    def _embed_query(self, connection: sqlite3.Connection, query_text: str) -> list[float] | None:
        cached = self._cached_query_embedding(connection, query_text)
        if cached is not None:
            return cached
        embedder = OllamaEmbedder(
            model_id=str(self.config.get("ollama_model_id", "qwen3-embedding:0.6b") or "qwen3-embedding:0.6b"),
            timeout_ms=_coerce_int(self.config.get("query_embedding_timeout_ms"), 500),
        )
        embedding = embedder.embed(self._query_embedding_text(query_text))
        if embedding is None:
            return None
        self._save_query_embedding(connection, query_text, embedding)
        connection.commit()
        return embedding

    def _serialize_vector(self, vector: list[float]) -> object:
        if self._sqlite_vec is not None and hasattr(self._sqlite_vec, "serialize_float32"):
            return self._sqlite_vec.serialize_float32(vector)
        return json.dumps(vector)

    def _index_pending_vectors(self) -> dict[str, object]:
        with self._connect() as connection:
            if not self._load_sqlite_vec(connection):
                return {"status": "pending", "last_error": self._vector_unavailable_reason or "sqlite_vec_unavailable"}
            rows = connection.execute(
                """
                SELECT retrieval_doc_pk, text FROM retrieval_docs
                WHERE vector_index_status = 'pending'
                  AND surface = 'unit_understanding'
                ORDER BY retrieval_doc_pk
                """
            ).fetchall()
            if not rows:
                return {"status": "indexed", "last_error": None}
            budget_ms = _coerce_int(self.config.get("vector_index_write_budget_ms"), 1000)
            deadline = time.monotonic() + max(0.05, budget_ms / 1000)
            embedder = OllamaEmbedder(
                model_id=str(self.config.get("ollama_model_id", "qwen3-embedding:0.6b") or "qwen3-embedding:0.6b"),
                timeout_ms=min(500, max(50, budget_ms)),
            )
            indexed = 0
            last_error = None
            for row in rows:
                if time.monotonic() > deadline:
                    last_error = "vector_index_write_budget_exceeded"
                    break
                embedding = embedder.embed(str(row["text"]))
                if embedding is None:
                    last_error = "embedding_unavailable"
                    break
                try:
                    connection.execute(
                        "INSERT OR REPLACE INTO retrieval_doc_vectors(rowid, embedding) VALUES (?, ?)",
                        (int(row["retrieval_doc_pk"]), self._serialize_vector(embedding)),
                    )
                    connection.execute(
                        "UPDATE retrieval_docs SET vector_index_status = 'indexed' WHERE retrieval_doc_pk = ?",
                        (int(row["retrieval_doc_pk"]),),
                    )
                    indexed += 1
                except sqlite3.Error as exc:
                    last_error = f"vector_insert_failed:{type(exc).__name__}"
                    break
            connection.commit()
            pending = connection.execute(
                "SELECT COUNT(*) AS count FROM retrieval_docs WHERE vector_index_status = 'pending' AND surface = 'unit_understanding'"
            ).fetchone()["count"]
        return {
            "status": "indexed" if int(pending) == 0 else "pending",
            "indexed_count": indexed,
            "last_error": last_error,
        }

    def _candidate_row(self, row: sqlite3.Row, *, channel: str, rank: int, raw_score: float) -> dict[str, object]:
        surface = str(row["surface"])
        rrf_k = max(1, _coerce_int(self.config.get("rrf_k"), 60))
        channel_weight = SURFACE_CHANNEL_WEIGHTS.get(surface, {}).get(channel, 1.0)
        score = channel_weight / (rrf_k + rank)
        return {
            "retrieval_doc_pk": int(row["retrieval_doc_pk"]),
            "retrieval_doc_id": str(row["retrieval_doc_id"]),
            "unit_id": str(row["unit_id"]),
            "book_id": str(row["book_id"]),
            "surface": surface,
            "text": str(row["text"]),
            "source_span_id": str(row["source_span_id"] or ""),
            "unit_index": int(row["unit_index"]),
            "entry_json": str(row["entry_json"]),
            "channel": channel,
            "rank": rank,
            "raw_score": raw_score,
            "score": score,
        }

    def _lexical_candidates(
        self,
        connection: sqlite3.Connection,
        *,
        book_id: str,
        fts_query: str,
        max_unit_index: int,
        excluded_source_unit_span_ids: set[str],
    ) -> list[dict[str, object]]:
        rows = connection.execute(
            """
            SELECT d.retrieval_doc_pk, d.retrieval_doc_id, d.unit_id, d.book_id,
                   d.surface, d.text, d.source_span_id, e.unit_index, e.entry_json,
                   bm25(retrieval_docs_fts) AS bm25_score
            FROM retrieval_docs_fts
            JOIN retrieval_docs d ON d.retrieval_doc_pk = retrieval_docs_fts.rowid
            JOIN unit_memory_entries e ON e.unit_id = d.unit_id
            WHERE retrieval_docs_fts MATCH ?
              AND d.book_id = ?
              AND e.unit_index <= ?
            ORDER BY bm25_score ASC
            LIMIT ?
            """,
            (
                fts_query,
                book_id,
                max_unit_index,
                max(1, _coerce_int(self.config.get("lexical_top_k"), 80)),
            ),
        ).fetchall()
        candidates = []
        for rank, row in enumerate(rows, start=1):
            if str(row["source_span_id"] or "") in excluded_source_unit_span_ids:
                continue
            candidates.append(self._candidate_row(row, channel="lexical", rank=rank, raw_score=float(row["bm25_score"])))
        return candidates

    def _dense_candidates(
        self,
        connection: sqlite3.Connection,
        *,
        book_id: str,
        query_text: str,
        max_unit_index: int,
        excluded_source_unit_span_ids: set[str],
    ) -> tuple[list[dict[str, object]], str, int]:
        if not self._load_sqlite_vec(connection):
            return [], self._vector_unavailable_reason or "sqlite_vec_unavailable", 0
        embedding = self._embed_query(connection, query_text)
        if embedding is None:
            return [], "query_embedding_unavailable", 0
        dense_top_k = max(1, _coerce_int(self.config.get("dense_top_k"), 80))
        max_distance = _coerce_float(self.config.get("dense_max_distance"), 0.80)
        try:
            rows = connection.execute(
                """
                SELECT d.retrieval_doc_pk, d.retrieval_doc_id, d.unit_id, d.book_id,
                       d.surface, d.text, d.source_span_id, e.unit_index, e.entry_json,
                       v.distance AS distance
                FROM retrieval_doc_vectors v
                JOIN retrieval_docs d ON d.retrieval_doc_pk = v.rowid
                JOIN unit_memory_entries e ON e.unit_id = d.unit_id
                WHERE v.embedding MATCH ?
                  AND k = ?
                  AND d.book_id = ?
                  AND e.unit_index <= ?
                  AND d.surface = 'unit_understanding'
                ORDER BY distance ASC
                """,
                (self._serialize_vector(embedding), dense_top_k, book_id, max_unit_index),
            ).fetchall()
        except sqlite3.Error as exc:
            return [], f"vector_query_failed:{type(exc).__name__}", 0
        candidates = []
        filtered_by_distance = 0
        for rank, row in enumerate(rows, start=1):
            distance = float(row["distance"])
            if distance > max_distance:
                filtered_by_distance += 1
                continue
            if str(row["source_span_id"] or "") in excluded_source_unit_span_ids:
                continue
            candidates.append(self._candidate_row(row, channel="dense", rank=rank, raw_score=distance))
        return candidates, "", filtered_by_distance

    def _aggregate_units(self, candidates: list[dict[str, object]]) -> list[dict[str, object]]:
        grouped: dict[str, list[dict[str, object]]] = {}
        for candidate in candidates:
            grouped.setdefault(str(candidate.get("unit_id")), []).append(candidate)
        units: list[dict[str, object]] = []
        for unit_id, docs in grouped.items():
            docs = sorted(docs, key=lambda item: float(item.get("score", 0.0)), reverse=True)
            scores = [float(item.get("score", 0.0)) for item in docs[: max(1, _coerce_int(self.config.get("max_docs_per_unit_for_scoring"), 5))]]
            score = scores[0] if scores else 0.0
            if len(scores) > 1:
                score += 0.35 * scores[1]
            if len(scores) > 2:
                score += 0.15 * sum(scores[2:5])
            surfaces = {str(item.get("surface", "")) for item in docs if item.get("surface")}
            channels = {str(item.get("channel", "")) for item in docs if item.get("channel")}
            recall_ids = {str(item.get("recall_id", "")) for item in docs if item.get("recall_id")}
            score += 0.03 * min(max(0, len(surfaces) - 1), 3)
            if {"lexical", "dense"} <= channels:
                score += 0.03
            entry_json = _json_loads(docs[0].get("entry_json"), {}) if docs else {}
            units.append(
                {
                    "unit_id": unit_id,
                    "unit_index": int(docs[0].get("unit_index", 0) or 0) if docs else 0,
                    "score": score,
                    "surfaces": sorted(surfaces),
                    "channels": sorted(channels),
                    "matched_recalls": sorted(recall_ids),
                    "best_docs": [
                        {
                            "retrieval_doc_id": item.get("retrieval_doc_id"),
                            "surface": item.get("surface"),
                            "channel": item.get("channel"),
                            "recall_id": item.get("recall_id"),
                            "rank": item.get("rank"),
                            "score": item.get("score"),
                        }
                        for item in docs[:3]
                    ],
                    "entry": entry_json,
                }
            )
        units.sort(key=lambda item: (-float(item.get("score", 0.0)), int(item.get("unit_index", 0) or 0)))
        return units[: max(1, _coerce_int(self.config.get("max_units_after_aggregation"), 20))]

    def _select_renderable_units(
        self,
        units: list[dict[str, object]],
        *,
        limit: int,
        per_recall_limit: int = 0,
    ) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
        selected: list[dict[str, object]] = []
        suppressed: list[dict[str, object]] = []
        selected_by_recall: dict[str, int] = {}
        for item in units:
            compact = _compact_retrieval_unit(item)
            entry = item.get("entry")
            if not isinstance(entry, Mapping):
                suppressed.append({**compact, "reason": "candidate_missing_entry"})
                continue
            if not isinstance(entry.get("digest"), Mapping):
                suppressed.append({**compact, "reason": "candidate_missing_understanding"})
                continue
            if not _entry_understanding_content(entry):
                suppressed.append({**compact, "reason": "candidate_not_renderable_empty_understanding"})
                continue
            matched_recalls = [
                _clean_text(recall_id)
                for recall_id in (item.get("matched_recalls") if isinstance(item.get("matched_recalls"), list) else [])
                if _clean_text(recall_id)
            ]
            if per_recall_limit > 0 and matched_recalls and all(
                selected_by_recall.get(recall_id, 0) >= per_recall_limit for recall_id in matched_recalls
            ):
                suppressed.append({**compact, "reason": "per_recall_selection_limit_exceeded"})
                continue
            if len(selected) < max(1, limit):
                selected.append(item)
                for recall_id in matched_recalls:
                    selected_by_recall[recall_id] = selected_by_recall.get(recall_id, 0) + 1
            else:
                suppressed.append({**compact, "reason": "selection_limit_exceeded"})
        return selected, suppressed

    def retrieve_for_recalls(
        self,
        *,
        book_id: str,
        recalls: list[Mapping[str, object]],
        query_source: str,
        current_unit_index: int,
        excluded_source_unit_span_ids: set[str] | None = None,
        tool_call_id: str = "",
        accepted_source_span_id: str = "",
        accepted_unit_id: str = "",
    ) -> dict[str, object]:
        """Retrieve prior Unit Memory candidates for multiple Ingest recalls."""

        started_at = time.monotonic()
        self.ensure_schema()
        mode, mode_warnings = normalize_memory_retrieval_mode(self.config.get("mode"))
        excluded_source_unit_span_ids = set(excluded_source_unit_span_ids or set())
        normalized_recalls = normalize_unit_memory_recalls(list(recalls))
        trace: dict[str, object] = {
            "recorded_at": _timestamp(),
            "event_type": "unit_memory_retrieval",
            "book_id": _clean_text(book_id),
            "recalls": [dict(item) for item in normalized_recalls],
            "query_source": query_source,
            "tool_call_id": _clean_text(tool_call_id),
            "accepted_source_span_id": _clean_text(accepted_source_span_id),
            "accepted_unit_id": _clean_text(accepted_unit_id),
            "mode": mode,
            "effective_mode": mode,
            "config_warnings": mode_warnings,
            "latency_ms": 0,
            "candidate_counts": {},
            "per_recall": [],
            "degradation_reason": "",
            "excluded_source_unit_span_count": len(excluded_source_unit_span_ids),
            "selected_units": [],
            "suppressed_units": [],
        }
        if not normalized_recalls:
            trace["degradation_reason"] = "no_recall"
            trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
            record_unit_memory_retrieval_trace(self.output_dir, trace)
            return {
                "recalls": [],
                "query_source": query_source,
                "mode": mode,
                "effective_mode": mode,
                "selected_units": [],
                "trace": trace,
            }

        recent_window = max(0, _coerce_int(self.config.get("recent_neighbor_exclusion_unit_count"), 20))
        max_unit_index = int(current_unit_index) - recent_window
        trace["horizon"] = {
            "current_unit_index": int(current_unit_index),
            "recent_neighbor_exclusion_unit_count": recent_window,
            "max_retrievable_unit_index": max_unit_index,
        }
        if max_unit_index < 1:
            trace["degradation_reason"] = "not_enough_prior_units_after_recent_exclusion"
            trace["candidate_counts"] = {
                "current_unit_index": int(current_unit_index),
                "excluded_recent_neighbor_units": recent_window,
                "remaining_retrievable_units": 0,
            }
            trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
            record_unit_memory_retrieval_trace(self.output_dir, trace)
            return {
                "recalls": [dict(item) for item in normalized_recalls],
                "query_source": query_source,
                "mode": mode,
                "effective_mode": mode,
                "selected_units": [],
                "trace": trace,
            }

        all_candidates: list[dict[str, object]] = []
        total_lexical = 0
        total_dense = 0
        total_dense_filtered = 0
        degradation_reasons: list[str] = []
        effective_mode = mode
        with self._connect() as connection:
            prior_count = int(
                connection.execute(
                    "SELECT COUNT(*) AS count FROM unit_memory_entries WHERE book_id = ? AND unit_index <= ?",
                    (book_id, max_unit_index),
                ).fetchone()["count"]
            )
            min_prior = max(0, _coerce_int(self.config.get("min_retrievable_prior_units"), 20))
            existing_horizon = trace.get("horizon")
            trace["horizon"] = {
                **(dict(existing_horizon) if isinstance(existing_horizon, dict) else {}),
                "prior_units_after_recent_exclusion": prior_count,
                "min_retrievable_prior_units": min_prior,
            }
            if prior_count < min_prior:
                trace["degradation_reason"] = "below_min_retrievable_prior_units"
                trace["candidate_counts"] = {
                    "prior_units": prior_count,
                    "min_retrievable_prior_units": min_prior,
                    "remaining_retrievable_units": prior_count,
                }
                trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
                record_unit_memory_retrieval_trace(self.output_dir, trace)
                return {
                    "recalls": [dict(item) for item in normalized_recalls],
                    "query_source": query_source,
                    "mode": mode,
                    "effective_mode": mode,
                    "selected_units": [],
                    "trace": trace,
                }

            for recall in normalized_recalls:
                query = query_from_recall(recall)
                query_text = _normalized_query_text(query.get("query_text"))
                recall_id = _clean_text(recall.get("recall_id"))
                per_recall: dict[str, object] = {
                    "recall_id": recall_id,
                    "recall_text": _clean_text(recall.get("recall_text")),
                    "query": dict(query),
                    "lexical_docs": 0,
                    "dense_docs": 0,
                    "degradation_reason": "",
                }
                if not query_text:
                    per_recall["degradation_reason"] = "empty_query"
                    trace.setdefault("per_recall", []).append(per_recall)  # type: ignore[union-attr]
                    continue
                fts_query, fts_skip = build_fts5_match_query(query_text)
                lexical_candidates: list[dict[str, object]] = []
                if fts_query:
                    try:
                        lexical_candidates = self._lexical_candidates(
                            connection,
                            book_id=book_id,
                            fts_query=fts_query,
                            max_unit_index=max_unit_index,
                            excluded_source_unit_span_ids=excluded_source_unit_span_ids,
                        )
                    except sqlite3.Error as exc:
                        per_recall["fts_error"] = f"fts_query_failed:{type(exc).__name__}"
                else:
                    per_recall["fts_skipped_reason"] = fts_skip
                for candidate in lexical_candidates:
                    candidate["recall_id"] = recall_id

                dense_candidates: list[dict[str, object]] = []
                dense_degradation = ""
                dense_filtered_by_distance = 0
                if mode == "hybrid":
                    dense_candidates, dense_degradation, dense_filtered_by_distance = self._dense_candidates(
                        connection,
                        book_id=book_id,
                        query_text=query_text,
                        max_unit_index=max_unit_index,
                        excluded_source_unit_span_ids=excluded_source_unit_span_ids,
                    )
                    for candidate in dense_candidates:
                        candidate["recall_id"] = recall_id
                    if dense_degradation:
                        effective_mode = "text_only"
                        degradation_reasons.append(f"{recall_id}:{dense_degradation}")
                        per_recall["degradation_reason"] = dense_degradation

                per_recall["lexical_docs"] = len(lexical_candidates)
                per_recall["dense_docs"] = len(dense_candidates)
                per_recall["dense_docs_filtered_by_distance"] = dense_filtered_by_distance
                total_lexical += len(lexical_candidates)
                total_dense += len(dense_candidates)
                total_dense_filtered += dense_filtered_by_distance
                all_candidates.extend([*lexical_candidates, *dense_candidates])
                trace.setdefault("per_recall", []).append(per_recall)  # type: ignore[union-attr]

        aggregated_units = self._aggregate_units(all_candidates)
        max_units_to_digest_context = max(1, _coerce_int(self.config.get("max_units_to_digest_context"), 40))
        max_units_per_recall = max(0, _coerce_int(self.config.get("max_units_per_recall_to_digest_context"), 6))
        selected_units, suppressed_units = self._select_renderable_units(
            aggregated_units,
            limit=max_units_to_digest_context,
            per_recall_limit=max_units_per_recall,
        )
        compact_selected = [_compact_retrieval_unit(item) for item in selected_units]
        trace["effective_mode"] = effective_mode
        trace["degradation_reason"] = ";".join(degradation_reasons)
        trace["candidate_counts"] = {
            "recall_count": len(normalized_recalls),
            "lexical_docs": total_lexical,
            "dense_docs": total_dense,
            "dense_docs_filtered_by_distance": total_dense_filtered,
            "candidate_units": len({str(item.get("unit_id")) for item in all_candidates if item.get("unit_id")}),
        }
        trace["selection_config"] = {
            "max_units_to_digest_context": max_units_to_digest_context,
            "max_units_per_recall_to_digest_context": max_units_per_recall,
        }
        trace["selected_units"] = compact_selected
        trace["suppressed_units"] = suppressed_units
        trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
        record_unit_memory_retrieval_trace(self.output_dir, trace)
        return {
            "recalls": [dict(item) for item in normalized_recalls],
            "query_source": query_source,
            "mode": mode,
            "effective_mode": effective_mode,
            "degradation_reason": trace["degradation_reason"],
            "selected_units": selected_units,
            "trace": trace,
        }

    def retrieve(
        self,
        *,
        book_id: str,
        query: Mapping[str, object],
        query_source: str,
        current_unit_index: int,
        excluded_source_unit_span_ids: set[str] | None = None,
    ) -> dict[str, object]:
        """Retrieve prior Unit Memory candidates for one accepted source unit."""

        started_at = time.monotonic()
        self.ensure_schema()
        mode, mode_warnings = normalize_memory_retrieval_mode(self.config.get("mode"))
        excluded_source_unit_span_ids = set(excluded_source_unit_span_ids or set())
        query_text = _normalized_query_text(query.get("query_text") if isinstance(query, Mapping) else "")
        trace: dict[str, object] = {
            "recorded_at": _timestamp(),
            "event_type": "unit_memory_retrieval",
            "book_id": _clean_text(book_id),
            "query": dict(query),
            "query_source": query_source,
            "mode": mode,
            "effective_mode": mode,
            "config_warnings": mode_warnings,
            "latency_ms": 0,
            "candidate_counts": {},
            "degradation_reason": "",
            "excluded_source_unit_span_count": len(excluded_source_unit_span_ids),
            "selected_units": [],
        }
        if not query_text:
            trace["degradation_reason"] = "empty_query"
            trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
            record_unit_memory_retrieval_trace(self.output_dir, trace)
            return {"query": dict(query), "query_source": query_source, "mode": mode, "effective_mode": mode, "selected_units": [], "trace": trace}

        recent_window = max(0, _coerce_int(self.config.get("recent_neighbor_exclusion_unit_count"), 20))
        max_unit_index = int(current_unit_index) - recent_window
        trace["horizon"] = {
            "current_unit_index": int(current_unit_index),
            "recent_neighbor_exclusion_unit_count": recent_window,
            "max_retrievable_unit_index": max_unit_index,
        }
        if max_unit_index < 1:
            trace["degradation_reason"] = "not_enough_prior_units_after_recent_exclusion"
            trace["candidate_counts"] = {
                "current_unit_index": int(current_unit_index),
                "excluded_recent_neighbor_units": recent_window,
                "remaining_retrievable_units": 0,
            }
            trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
            record_unit_memory_retrieval_trace(self.output_dir, trace)
            return {"query": dict(query), "query_source": query_source, "mode": mode, "effective_mode": mode, "selected_units": [], "trace": trace}

        with self._connect() as connection:
            prior_count = int(
                connection.execute(
                    "SELECT COUNT(*) AS count FROM unit_memory_entries WHERE book_id = ? AND unit_index <= ?",
                    (book_id, max_unit_index),
                ).fetchone()["count"]
            )
            min_prior = max(0, _coerce_int(self.config.get("min_retrievable_prior_units"), 20))
            existing_horizon = trace.get("horizon")
            trace["horizon"] = {
                **(dict(existing_horizon) if isinstance(existing_horizon, dict) else {}),
                "prior_units_after_recent_exclusion": prior_count,
                "min_retrievable_prior_units": min_prior,
            }
            if prior_count < min_prior:
                trace["degradation_reason"] = "below_min_retrievable_prior_units"
                trace["candidate_counts"] = {
                    "prior_units": prior_count,
                    "min_retrievable_prior_units": min_prior,
                    "remaining_retrievable_units": prior_count,
                }
                trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
                record_unit_memory_retrieval_trace(self.output_dir, trace)
                return {"query": dict(query), "query_source": query_source, "mode": mode, "effective_mode": mode, "selected_units": [], "trace": trace}

            fts_query, fts_skip = build_fts5_match_query(query_text)
            lexical_candidates: list[dict[str, object]] = []
            if fts_query:
                try:
                    lexical_candidates = self._lexical_candidates(
                        connection,
                        book_id=book_id,
                        fts_query=fts_query,
                        max_unit_index=max_unit_index,
                        excluded_source_unit_span_ids=excluded_source_unit_span_ids,
                    )
                except sqlite3.Error as exc:
                    trace["fts_error"] = f"fts_query_failed:{type(exc).__name__}"
            else:
                trace["fts_skipped_reason"] = fts_skip

            dense_candidates: list[dict[str, object]] = []
            dense_degradation = ""
            dense_filtered_by_distance = 0
            effective_mode = mode
            if mode == "hybrid":
                dense_candidates, dense_degradation, dense_filtered_by_distance = self._dense_candidates(
                    connection,
                    book_id=book_id,
                    query_text=query_text,
                    max_unit_index=max_unit_index,
                    excluded_source_unit_span_ids=excluded_source_unit_span_ids,
                )
                if dense_degradation:
                    effective_mode = "text_only"
            trace["effective_mode"] = effective_mode
            if dense_degradation:
                trace["degradation_reason"] = dense_degradation
            trace["candidate_counts"] = {
                "prior_units": prior_count,
                "lexical_docs": len(lexical_candidates),
                "dense_docs": len(dense_candidates),
                "dense_docs_filtered_by_distance": dense_filtered_by_distance,
            }
            aggregated_units = self._aggregate_units([*lexical_candidates, *dense_candidates])
            selected_units, suppressed_units = self._select_renderable_units(
                aggregated_units,
                limit=max(1, _coerce_int(self.config.get("max_units_to_digest_context"), 6)),
            )
            compact_selected = [_compact_retrieval_unit(item) for item in selected_units]
            trace["selected_units"] = compact_selected
            trace["suppressed_units"] = suppressed_units
            trace["latency_ms"] = int((time.monotonic() - started_at) * 1000)
            record_unit_memory_retrieval_trace(self.output_dir, trace)
            return {
                "query": dict(query),
                "query_source": query_source,
                "mode": mode,
                "effective_mode": effective_mode,
                "degradation_reason": dense_degradation,
                "selected_units": selected_units,
                "trace": trace,
            }
