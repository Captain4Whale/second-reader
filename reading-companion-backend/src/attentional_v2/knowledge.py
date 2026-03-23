"""Knowledge-activation lifecycle and conservative search-policy helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from .schemas import (
    KnowledgeActivation,
    KnowledgeActivationsState,
    KnowledgeUseMode,
    ReaderPolicy,
    SearchPolicyMode,
    SearchTrigger,
    StateOperation,
)
from .state_ops import upsert_knowledge_activation


_KNOWLEDGE_USE_MODES: set[KnowledgeUseMode] = {
    "book_grounded_only",
    "book_grounded_plus_prior_knowledge",
}
_SEARCH_POLICY_MODES: set[SearchPolicyMode] = {"no_search", "defer_search", "search_now"}
_SEARCH_TRIGGERS: set[SearchTrigger] = {
    "none",
    "identity_critical_reference",
    "blocking_allusion",
    "genuine_curiosity",
    "ornamental_curiosity",
}
_LIVE_ACTIVATION_STATUSES = {"weak", "plausible", "strong"}


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _touch_state(state: KnowledgeActivationsState) -> KnowledgeActivationsState:
    """Return a shallow-copied knowledge state with a fresh timestamp."""

    next_state = dict(state)
    next_state["updated_at"] = _timestamp()
    return next_state  # type: ignore[return-value]


def _default_knowledge_mode(reader_policy: ReaderPolicy | None) -> KnowledgeUseMode:
    """Read the configured default knowledge-use mode."""

    mode = str((reader_policy or {}).get("knowledge", {}).get("default_mode", "book_grounded_only") or "")
    if mode in _KNOWLEDGE_USE_MODES:
        return mode  # type: ignore[return-value]
    return "book_grounded_only"


def _default_search_mode(reader_policy: ReaderPolicy | None) -> SearchPolicyMode:
    """Read the configured default search-policy mode."""

    mode = str((reader_policy or {}).get("search", {}).get("default_mode", "no_search") or "")
    if mode in _SEARCH_POLICY_MODES:
        return mode  # type: ignore[return-value]
    return "no_search"


def set_knowledge_use_mode(
    state: KnowledgeActivationsState,
    mode: KnowledgeUseMode,
) -> KnowledgeActivationsState:
    """Replace the current knowledge-use mode."""

    next_state = _touch_state(state)
    next_state["knowledge_use_mode"] = mode
    return next_state


def set_search_policy_mode(
    state: KnowledgeActivationsState,
    mode: SearchPolicyMode,
) -> KnowledgeActivationsState:
    """Replace the current search-policy mode."""

    next_state = _touch_state(state)
    next_state["search_policy_mode"] = mode
    return next_state


def live_activations(state: KnowledgeActivationsState) -> list[KnowledgeActivation]:
    """Return currently live activations only."""

    return [
        activation
        for activation in state.get("activations", [])
        if isinstance(activation, dict) and str(activation.get("status", "") or "") in _LIVE_ACTIVATION_STATUSES
    ]


def refresh_knowledge_modes(
    state: KnowledgeActivationsState,
    *,
    reader_policy: ReaderPolicy | None = None,
) -> KnowledgeActivationsState:
    """Recompute the current knowledge-use mode while preserving explicit search state."""

    next_state = dict(state)
    active_with_warrant = [
        activation
        for activation in live_activations(state)
        if str(activation.get("reading_warrant", "") or "").strip()
        and str(activation.get("status", "") or "") in {"plausible", "strong"}
    ]
    next_state["knowledge_use_mode"] = (
        "book_grounded_plus_prior_knowledge"
        if active_with_warrant
        else _default_knowledge_mode(reader_policy)
    )
    current_search_mode = str(state.get("search_policy_mode", "") or "")
    next_state["search_policy_mode"] = (
        current_search_mode
        if current_search_mode in _SEARCH_POLICY_MODES
        else _default_search_mode(reader_policy)
    )
    next_state["updated_at"] = _timestamp()
    return next_state  # type: ignore[return-value]


def resolve_search_policy_mode(
    requested_mode: SearchPolicyMode | str | None,
    *,
    search_trigger: SearchTrigger | str = "none",
    reading_can_continue: bool = True,
    reader_policy: ReaderPolicy | None = None,
) -> SearchPolicyMode:
    """Apply the Phase 5 rare-search posture to one requested search action."""

    default_mode = _default_search_mode(reader_policy)
    requested = str(requested_mode or default_mode)
    trigger = str(search_trigger or "none")
    if requested not in _SEARCH_POLICY_MODES:
        requested = default_mode
    if trigger not in _SEARCH_TRIGGERS:
        trigger = "none"

    if requested == "no_search":
        return "no_search"

    if requested == "defer_search":
        return "no_search" if trigger == "ornamental_curiosity" else "defer_search"

    allow_search_now = bool((reader_policy or {}).get("search", {}).get("allow_search_now", True))
    if not allow_search_now:
        return default_mode
    if trigger in {"identity_critical_reference", "blocking_allusion"} and not reading_can_continue:
        return "search_now"
    if trigger == "genuine_curiosity":
        return "defer_search"
    return default_mode


def apply_activation_operations(
    state: KnowledgeActivationsState,
    operations: list[StateOperation],
    *,
    current_sentence_id: str,
    reader_policy: ReaderPolicy | None = None,
) -> KnowledgeActivationsState:
    """Apply explicit knowledge-activation operations and refresh policy modes."""

    next_state = state
    activation_index = {
        str(activation.get("activation_id", "") or ""): dict(activation)
        for activation in state.get("activations", [])
        if isinstance(activation, dict) and str(activation.get("activation_id", "") or "")
    }
    activation_counter = len(activation_index)

    for operation in operations:
        target_store = str(operation.get("target_store", "") or "")
        if target_store not in {"knowledge_activations", "knowledge_activation"}:
            continue
        payload = operation.get("payload")
        if not isinstance(payload, dict):
            continue

        activation_id = str(operation.get("item_id", "") or payload.get("activation_id", "") or "")
        if not activation_id:
            activation_counter += 1
            activation_id = f"ka:{current_sentence_id}:{activation_counter}"
        existing = activation_index.get(activation_id, {})
        operation_type = str(operation.get("operation_type", "") or "")

        if operation_type in {"create", "update", "reactivate"}:
            activation: KnowledgeActivation = {
                **existing,
                **{
                    key: value
                    for key, value in payload.items()
                    if key
                    in {
                        "trigger_anchor_id",
                        "activation_type",
                        "source_candidate",
                        "recognition_confidence",
                        "reading_warrant",
                        "role_assessment",
                        "evidence_hints",
                        "evidence_rationale",
                        "support_anchor_ids",
                        "conflict_anchor_ids",
                        "introduced_at_sentence_id",
                        "last_touched_sentence_id",
                        "status",
                    }
                },
                "activation_id": activation_id,
            }
            if not activation.get("introduced_at_sentence_id"):
                activation["introduced_at_sentence_id"] = str(existing.get("introduced_at_sentence_id", "") or current_sentence_id)
            activation["last_touched_sentence_id"] = str(
                activation.get("last_touched_sentence_id", "") or current_sentence_id
            )
            if operation_type == "reactivate" and str(activation.get("status", "") or "") in {"rejected", "dropped", ""}:
                activation["status"] = "plausible"
            elif not activation.get("status"):
                activation["status"] = "weak"

            next_state = upsert_knowledge_activation(next_state, activation)
            activation_index[activation_id] = dict(activation)
            continue

        if operation_type not in {"cool", "drop", "supersede"} or not existing:
            continue

        status = {
            "cool": "weak",
            "drop": "dropped",
            "supersede": "rejected",
        }[operation_type]
        cooled: KnowledgeActivation = {
            **existing,
            "activation_id": activation_id,
            "last_touched_sentence_id": current_sentence_id,
            "status": status,
        }
        next_state = upsert_knowledge_activation(next_state, cooled)
        activation_index[activation_id] = dict(cooled)

    return refresh_knowledge_modes(next_state, reader_policy=reader_policy)
