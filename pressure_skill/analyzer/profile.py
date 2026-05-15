from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RelationRole(str, Enum):
    """Who the counterparty is, relative to the user."""

    UNKNOWN = "unknown"
    MANAGER = "manager"
    PEER = "peer"
    REPORT = "report"
    CLIENT = "client"
    ELDER = "elder"


class CommunicationProfile(BaseModel):
    """Structured portrait used by the advisor."""

    relation: RelationRole = RelationRole.UNKNOWN
    scene_tags: list[str] = Field(
        default_factory=list,
        description="e.g. internet_cn, academia, state_owned",
    )
    reply_speed_hint: str | None = Field(
        default=None,
        description="User observation: fast / slow / irregular",
    )
    prefers: dict[str, float] = Field(
        default_factory=dict,
        description="Soft weights, e.g. speed vs detail, 0-1",
    )
    pain_points: list[str] = Field(default_factory=list)
    praise_vs_critique_notes: str | None = Field(
        default=None,
        description="Short contrast notes for implicit standards",
    )
    pattern_tags: list[str] = Field(default_factory=list)
    features: dict[str, Any] = Field(
        default_factory=dict,
        description="Quantitative/heuristic features from transcript",
    )
    counterparty_notes: str | None = Field(
        default=None,
        description="Free-text portrait of the other person (style, habits, ego, past interactions)",
    )
    user_leverage_notes: str | None = Field(
        default=None,
        description="User-side leverage: deadlines, unique info, alternatives, compliance, reputation",
    )
    extra_context_notes: str | None = Field(
        default=None,
        description="Broader context: org politics, power balance, skills, stakes for both sides",
    )
    user_purpose: str | None = Field(
        default=None,
        description="What the user wants to achieve in this session (declared after portrait)",
    )
    locale: str | None = Field(
        default=None,
        description="Response language hint: 'zh' | 'en'; when null, infer from text",
    )
    discipline_subfield: str | None = Field(
        default=None,
        description="e.g. cs_theory, cs_systems, cs_ml, cs_security, math, ee; disambiguates 'write clearly'",
    )
    artefact_preferences_notes: str | None = Field(
        default=None,
        description="What the counterparty rewards: formulas, code, diagrams, tables, prose, slides-only",
    )
    counterparty_seniority: str | None = Field(
        default=None,
        description="e.g. junior_faculty, mid_faculty, senior_faculty; optional, affects tone expectations",
    )

    def merge_manual(self, other: dict[str, Any]) -> "CommunicationProfile":
        """Overlay non-empty manual fields from a dict (API convenience)."""
        data = self.model_dump()
        for k, v in other.items():
            if v is None:
                continue
            if k == "relation" and isinstance(v, str):
                data["relation"] = v
            elif k in data and isinstance(data[k], dict) and isinstance(v, dict):
                data[k] = {**data[k], **v}
            elif k in data:
                data[k] = v
        return CommunicationProfile.model_validate(data)
