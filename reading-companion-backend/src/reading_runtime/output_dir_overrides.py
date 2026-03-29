"""Thread-safe temporary output-dir overrides for eval and repair workflows."""

from __future__ import annotations

import contextvars
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


_CURRENT_OUTPUT_DIR_OVERRIDE: contextvars.ContextVar[Path | None] = contextvars.ContextVar(
    "reading_runtime_current_output_dir_override",
    default=None,
)


def get_output_dir_override() -> Path | None:
    """Return the active output-dir override for the current context, if any."""

    return _CURRENT_OUTPUT_DIR_OVERRIDE.get()


@contextmanager
def override_output_dir(path: Path) -> Iterator[Path]:
    """Temporarily force output-dir resolution for the current context only."""

    token = _CURRENT_OUTPUT_DIR_OVERRIDE.set(path)
    try:
        yield path
    finally:
        _CURRENT_OUTPUT_DIR_OVERRIDE.reset(token)
