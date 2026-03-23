"""Deterministic intake and trigger scaffolding for attentional_v2."""

from __future__ import annotations

import re

from .schemas import (
    AnchorMemoryState,
    GateState,
    LocalBufferSentence,
    LocalBufferState,
    TriggerSignal,
    TriggerState,
    WorkingPressureState,
)
from .state_ops import push_local_buffer_sentence, set_trigger_result


_TURN_MARKERS = (
    "however",
    "but",
    "yet",
    "instead",
    "meanwhile",
    "on the other hand",
    "in contrast",
)
_DEFINITION_MARKERS = ("defined as", "means", "refers to", "consists of", "in other words")
_CLAIM_MARKERS = ("must", "should", "cannot", "never", "always", "therefore", "thus")


def _token_set(text: str) -> set[str]:
    """Return a coarse lexical set for local cohesion and callback checks."""

    return {
        token
        for token in re.findall(r"[a-z][a-z'-]{2,}|[\u4e00-\u9fff]{2,}", (text or "").lower())
        if token not in {"the", "and", "for", "with", "this", "that", "from", "into"}
    }


def _signal(
    *,
    sentence_id: str,
    signal_kind: str,
    family: str,
    evidence: str,
    strength: str,
) -> TriggerSignal:
    """Build one trigger signal payload."""

    return {
        "signal_id": f"{sentence_id}:{signal_kind}",
        "signal_kind": signal_kind,  # type: ignore[typeddict-item]
        "family": family,  # type: ignore[typeddict-item]
        "sentence_id": sentence_id,
        "evidence": evidence,
        "strength": strength,
    }


def detect_trigger_signals(
    sentence: LocalBufferSentence | dict[str, object],
    *,
    local_buffer: LocalBufferState,
    working_pressure: WorkingPressureState,
    anchor_memory: AnchorMemoryState,
    cadence_limit: int = 4,
) -> tuple[list[TriggerSignal], list[str]]:
    """Emit cheap candidate-boundary and trigger signals for one ingested sentence."""

    sentence_id = str(sentence.get("sentence_id", "") or "")
    text = str(sentence.get("text", "") or "")
    text_role = str(sentence.get("text_role", "") or "")
    lowered = text.lower()
    signals: list[TriggerSignal] = []
    callback_anchor_ids: list[str] = []

    previous = local_buffer.get("recent_sentences", [])[-1] if local_buffer.get("recent_sentences") else None
    previous_text = str(previous.get("text", "") or "") if isinstance(previous, dict) else ""
    previous_role = str(previous.get("text_role", "") or "") if isinstance(previous, dict) else ""

    if any(lowered.startswith(marker) for marker in _TURN_MARKERS):
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="discourse_turn",
                family="integrity",
                evidence="sentence opens with a contrastive turn marker",
                strength="strong",
            )
        )
    if any(marker in lowered for marker in _DEFINITION_MARKERS) or ":" in text:
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="definition_or_distinction",
                family="integrity",
                evidence="sentence contains definition/distinction language",
                strength="strong",
            )
        )
    if any(marker in lowered for marker in _CLAIM_MARKERS):
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="claim_pressure",
                family="salience",
                evidence="sentence contains assertive claim language",
                strength="medium",
            )
        )
    if previous_role and text_role and previous_role != text_role:
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="sentence_role_shift",
                family="integrity",
                evidence=f"sentence role shifted from {previous_role} to {text_role}",
                strength="medium",
            )
        )

    current_tokens = _token_set(text)
    previous_tokens = _token_set(previous_text)
    if current_tokens and previous_tokens and not (current_tokens & previous_tokens):
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="local_cohesion_drop",
                family="integrity",
                evidence="lexical overlap with the immediately previous sentence dropped sharply",
                strength="medium",
            )
        )

    motif_keys = {
        key.lower()
        for key in anchor_memory.get("motif_index", {}).keys()
        if str(key or "").strip()
    }
    unresolved_keys = {
        key.lower()
        for key in anchor_memory.get("unresolved_reference_index", {}).keys()
        if str(key or "").strip()
    }
    callback_keys = [key for key in motif_keys | unresolved_keys if key and key in lowered]
    if callback_keys:
        callback_anchor_ids = sorted(
            {
                anchor_id
                for key in callback_keys
                for anchor_id in anchor_memory.get("motif_index", {}).get(key, []) + anchor_memory.get("unresolved_reference_index", {}).get(key, [])
            }
        )
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="callback_activation",
                family="salience",
                evidence="sentence overlaps an existing motif or unresolved reference key",
                strength="strong",
            )
        )

    if "?" in text or "？" in text or lowered.startswith("why ") or lowered.startswith("how "):
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="pressure_update_proxy",
                family="knowledge_risk",
                evidence="sentence introduces an explicit question or uncertainty marker",
                strength="medium",
            )
        )

    open_span_size = len(local_buffer.get("open_meaning_unit_sentence_ids", []))
    if open_span_size >= max(2, int(cadence_limit)):
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="cadence_guardrail",
                family="integrity",
                evidence="open meaning-unit span reached the cadence guardrail",
                strength="medium",
            )
        )

    if working_pressure.get("gate_state") in {"hot", "must_evaluate"} and current_tokens:
        signals.append(
            _signal(
                sentence_id=sentence_id,
                signal_kind="pressure_update_proxy",
                family="integrity",
                evidence="current working pressure is already escalated",
                strength="medium",
            )
        )

    return signals, callback_anchor_ids


def _next_gate_state(current_gate: GateState, signals: list[TriggerSignal]) -> GateState:
    """Convert cheap trigger evidence into a qualitative gate update."""

    if any(signal.get("family") == "knowledge_risk" for signal in signals):
        return "must_evaluate"
    if any(signal.get("strength") == "strong" and signal.get("family") == "integrity" for signal in signals):
        return "hot"
    if signals:
        if current_gate == "must_evaluate":
            return current_gate
        if current_gate == "hot":
            return current_gate
        return "watch"
    return "quiet"


def _trigger_output(gate_state: GateState, signals: list[TriggerSignal]) -> str:
    """Choose the trigger output class from the current cheap evidence."""

    if gate_state == "must_evaluate":
        return "zoom_now"
    if gate_state == "hot" and any(signal.get("strength") == "strong" for signal in signals):
        return "zoom_now"
    if signals or gate_state == "watch":
        return "monitor"
    return "no_zoom"


def process_sentence_intake(
    sentence: LocalBufferSentence | dict[str, object],
    *,
    local_buffer: LocalBufferState,
    working_pressure: WorkingPressureState,
    anchor_memory: AnchorMemoryState,
    window_size: int = 6,
    cadence_limit: int = 4,
) -> tuple[LocalBufferState, TriggerState]:
    """Ingest one sentence, update the local buffer, and emit trigger state."""

    next_buffer = push_local_buffer_sentence(
        local_buffer,
        sentence,  # type: ignore[arg-type]
        window_size=window_size,
    )
    signals, callback_anchor_ids = detect_trigger_signals(
        sentence,
        local_buffer=local_buffer,
        working_pressure=working_pressure,
        anchor_memory=anchor_memory,
        cadence_limit=cadence_limit,
    )
    gate_state = _next_gate_state(
        working_pressure.get("gate_state", "quiet"),  # type: ignore[arg-type]
        signals,
    )
    trigger_state = set_trigger_result(
        {
            "schema_version": int(local_buffer.get("schema_version", 1) or 1),
            "mechanism_version": str(local_buffer.get("mechanism_version", "") or ""),
            "current_sentence_id": "",
            "output": "no_zoom",
            "gate_state": "quiet",
            "signals": [],
            "cadence_counter": 0,
            "callback_anchor_ids": [],
        },
        sentence_id=str(sentence.get("sentence_id", "") or ""),
        output=_trigger_output(gate_state, signals),  # type: ignore[arg-type]
        gate_state=gate_state,
        signals=signals,
        cadence_counter=len(next_buffer.get("open_meaning_unit_sentence_ids", [])),
        callback_anchor_ids=callback_anchor_ids,
    )
    return next_buffer, trigger_state
