"""Skill request/result contracts for attentional_v2."""

from __future__ import annotations

from typing import Literal, TypedDict


SkillName = Literal[
    "source_map_overview",
    "source_scope_drilldown",
    "source_window_fetch",
    "anchor_resolve",
]
SkillStatus = Literal["ok", "error"]


class SkillRequest(TypedDict, total=False):
    """One bounded request for a mechanism-internal skill."""

    skill_name: SkillName | str
    reason: str
    arguments: dict[str, object]


class SkillResult(TypedDict, total=False):
    """One source-grounded skill execution result."""

    skill_name: SkillName | str
    status: SkillStatus
    result: dict[str, object]
    provenance: dict[str, object]
    error: str
