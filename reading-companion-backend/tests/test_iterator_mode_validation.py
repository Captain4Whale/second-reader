"""Tests for read-mode validation after removing legacy plan mode."""

from __future__ import annotations

from pathlib import Path

import pytest

import main as main_module




def test_cli_mode_choices_no_longer_include_plan(capsys):
    """CLI parser should reject --mode plan as an invalid choice."""
    parser = main_module.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["read", "demo.epub", "--mode", "plan"])

    captured = capsys.readouterr()
    assert "invalid choice" in captured.err
    assert "plan" in captured.err
