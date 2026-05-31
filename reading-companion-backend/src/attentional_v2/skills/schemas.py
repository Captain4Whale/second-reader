"""Deprecated after DEC-103/DEC-104: legacy skill request/result contracts for attentional_v2."""

from __future__ import annotations

from typing import Literal, TypedDict


SkillName = Literal[
    "source_map_overview",
    "source_scope_drilldown",
    "source_window_fetch",
]
SkillStatus = Literal["ok", "error"]


class SkillRequest(TypedDict, total=False):
    """Deprecated after DEC-103/DEC-104: one legacy mechanism-internal skill request."""

    skill_name: SkillName | str
    reason: str
    arguments: dict[str, object]


class SkillResult(TypedDict, total=False):
    """Deprecated after DEC-103/DEC-104: one legacy source-grounded skill execution result."""

    skill_name: SkillName | str
    status: SkillStatus
    result: dict[str, object]
    provenance: dict[str, object]
    error: str
