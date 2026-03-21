"""Tests for the backend reading-mechanism scaffold."""

from __future__ import annotations

import pytest

import main as main_module
from src.reading_runtime import available_mechanism_keys, default_mechanism_key, get_mechanism


def test_default_mechanism_registration_exposes_iterator_v1():
    """The scaffold should register the current iterator reader as the default."""

    assert "iterator_v1" in available_mechanism_keys()
    assert default_mechanism_key() == "iterator_v1"
    assert get_mechanism().key == "iterator_v1"
    assert get_mechanism("iterator_v1").label


def test_cli_mechanism_defaults_to_registered_default():
    """CLI parsing should expose the default mechanism without requiring a flag."""

    parser = main_module.build_parser()
    args = parser.parse_args(["read", "demo.epub"])

    assert args.mechanism == default_mechanism_key()


def test_cli_rejects_unknown_mechanism(capsys):
    """CLI parser should reject mechanisms that are not in the runtime registry."""

    parser = main_module.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["read", "demo.epub", "--mechanism", "unknown_v9"])

    captured = capsys.readouterr()
    assert "invalid choice" in captured.err
    assert "unknown_v9" in captured.err
