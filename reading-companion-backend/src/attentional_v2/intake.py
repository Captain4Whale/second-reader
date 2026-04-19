"""Deterministic sentence-intake helpers for attentional_v2."""

from __future__ import annotations

from .schemas import LocalBufferSentence, LocalBufferState
from .state_ops import push_local_buffer_sentence


def process_sentence_intake(
    sentence: LocalBufferSentence | dict[str, object],
    *,
    local_buffer: LocalBufferState,
    window_size: int = 6,
) -> LocalBufferState:
    """Ingest one sentence into the rolling local buffer."""

    return push_local_buffer_sentence(
        local_buffer,
        sentence,  # type: ignore[arg-type]
        window_size=window_size,
    )
