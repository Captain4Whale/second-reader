"""Public runtime entrypoints for pluggable backend reading mechanisms."""

from __future__ import annotations

from src.reading_core.runtime_contracts import ParseRequest, ParseResult, ReadRequest, ReadResult

from .mechanisms import (
    ReadingMechanism,
    available_mechanism_keys as _available_mechanism_keys,
    default_mechanism_key as _default_mechanism_key,
    get_mechanism as _get_mechanism,
    register_mechanism,
)

_BUILTINS_REGISTERED = False


def _ensure_builtin_mechanisms() -> None:
    """Register built-in mechanisms on first runtime use."""

    global _BUILTINS_REGISTERED
    if _BUILTINS_REGISTERED:
        return
    from src.reading_mechanisms import register_builtin_mechanisms

    register_builtin_mechanisms()
    _BUILTINS_REGISTERED = True


def available_mechanism_keys() -> tuple[str, ...]:
    """Return the stable set of registered mechanism keys."""

    _ensure_builtin_mechanisms()
    return _available_mechanism_keys()


def default_mechanism_key() -> str:
    """Return the current default mechanism key."""

    _ensure_builtin_mechanisms()
    return _default_mechanism_key()


def get_mechanism(key: str | None = None) -> ReadingMechanism:
    """Resolve one registered mechanism, falling back to the default."""

    _ensure_builtin_mechanisms()
    return _get_mechanism(key)


def parse_book(request: ParseRequest) -> ParseResult:
    """Parse one book through the selected backend reading mechanism."""

    return get_mechanism(request.mechanism_key).parse_book(request)


def read_book(request: ReadRequest) -> ReadResult:
    """Read one book through the selected backend reading mechanism."""

    return get_mechanism(request.mechanism_key).read_book(request)


__all__ = [
    "ReadingMechanism",
    "ParseRequest",
    "ParseResult",
    "ReadRequest",
    "ReadResult",
    "available_mechanism_keys",
    "default_mechanism_key",
    "get_mechanism",
    "parse_book",
    "read_book",
    "register_mechanism",
]
