"""Tests for the backend reading-mechanism scaffold."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

import main as main_module
from src import config as config_module
from src.iterator_reader.storage import activity_file, chapter_result_file, normalized_eval_bundle_file, reader_memory_file, run_state_file, save_json
from src.reading_core.runtime_contracts import ReadRequest
from src.reading_core.storage import save_book_document
from src.reading_runtime import available_mechanism_keys, default_mechanism_key, get_mechanism


def test_default_mechanism_registration_exposes_attentional_v2():
    """The scaffold should register attentional_v2 as the product default."""

    assert "attentional_v2" in available_mechanism_keys()
    assert "iterator_v1" not in available_mechanism_keys()
    assert default_mechanism_key() == "attentional_v2"
    assert get_mechanism().key == "attentional_v2"
    with pytest.raises(ValueError, match="已退役"):
        get_mechanism("iterator_v1")
    assert get_mechanism("attentional_v2").label


def test_cli_mechanism_defaults_to_registered_default():
    """CLI parsing should expose the default mechanism without requiring a flag."""

    parser = main_module.build_parser()
    args = parser.parse_args(["read", "demo.epub"])

    assert args.mechanism == default_mechanism_key()
    assert args.memory_retrieval_mode is None


def test_cli_memory_retrieval_mode_is_explicit_only():
    """Omitted mode lets resume restore persisted config; explicit mode still parses."""

    parser = main_module.build_parser()
    args = parser.parse_args(["read", "demo.epub", "--memory-retrieval-mode", "text_only"])

    assert args.memory_retrieval_mode == "text_only"


def test_cli_main_wraps_command_in_outer_worker_lease_context(monkeypatch):
    """The process lease should wrap mechanism dispatch without changing parser or command functions."""

    events: list[str] = []

    @contextmanager
    def _lease_context():
        events.append("lease-enter")
        try:
            yield None
        finally:
            events.append("lease-exit")

    class _Parser:
        @staticmethod
        def parse_args():
            return SimpleNamespace(func=lambda _args: events.append("command") or 0)

    monkeypatch.setattr(main_module, "build_parser", lambda: _Parser())
    monkeypatch.setattr(main_module, "lease_context_from_environment", _lease_context)

    assert main_module.main() == 0
    assert events == ["lease-enter", "command", "lease-exit"]


def test_backend_reading_mechanism_override_only_returns_explicit_fallback(monkeypatch):
    """The product-path override should stay quiet for the default and only return iterator_v1 fallback."""

    monkeypatch.delenv("BACKEND_READING_MECHANISM", raising=False)
    assert config_module.get_backend_reading_mechanism_key() is None

    monkeypatch.setenv("BACKEND_READING_MECHANISM", "attentional_v2")
    assert config_module.get_backend_reading_mechanism_key() is None

    monkeypatch.setenv("BACKEND_READING_MECHANISM", "iterator_v1")
    with pytest.raises(ValueError, match="已退役"):
        config_module.get_backend_reading_mechanism_key()

    monkeypatch.setenv("BACKEND_READING_MECHANISM", "unknown_v9")
    assert config_module.get_backend_reading_mechanism_key() is None


def test_cli_rejects_unknown_mechanism(capsys):
    """CLI parser should reject mechanisms that are not in the runtime registry."""

    parser = main_module.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["read", "demo.epub", "--mechanism", "unknown_v9"])

    captured = capsys.readouterr()
    assert "invalid choice" in captured.err
    assert "unknown_v9" in captured.err


def test_shared_modules_do_not_import_iterator_reader_models_directly():
    """Shared runtime/library/search modules should depend on reading_core, not iterator models."""

    backend_root = Path(main_module.__file__).resolve().parent
    candidate_files = [
        backend_root / "src" / "reading_runtime" / "__init__.py",
        backend_root / "src" / "reading_runtime" / "mechanisms.py",
        backend_root / "src" / "library" / "models.py",
        backend_root / "src" / "library" / "user_marks.py",
    ]

    for path in candidate_files:
        assert "src.iterator_reader.models" not in path.read_text(encoding="utf-8"), path


@pytest.mark.parametrize("arguments", [
    ["--mechanism", "iterator_v1"], ["--mechanism", "both"],
    ["--mode", "book_analysis"], ["--analysis-max-core-claims", "2"],
])
def test_cli_retired_options_report_retirement(arguments, capsys):
    with pytest.raises(SystemExit):
        main_module.build_parser().parse_args(["read", "missing.epub", *arguments])
    assert "已退役" in capsys.readouterr().err
