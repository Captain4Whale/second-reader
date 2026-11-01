"""Tests for prompt ownership boundaries and compatibility shims."""

from __future__ import annotations

from pathlib import Path



def test_production_code_no_longer_imports_templates_shim():
    """Production iterator and mechanism code should not depend on the compatibility shim."""
    backend_root = Path(__file__).resolve().parents[1]
    source_roots = [
        backend_root / "src" / "iterator_reader",
        backend_root / "src" / "reading_mechanisms",
    ]
    forbidden = "src.prompts.templates"

    for root in source_roots:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert forbidden not in text, f"{path} still imports the deprecated prompt shim"
