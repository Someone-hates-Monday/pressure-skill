"""Structured likely counterparty reactions per reply option (template + LLM fill)."""

from __future__ import annotations

from typing import Any

from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.i18n import effective_locale

# Stable tags for feedback loop / UI
REACTION_TAGS = (
    "accept",
    "partial_accept",
    "delay",
    "vague_promise",
    "escalate",
    "deflect_blame",
    "cold_ignore",
    "push_back",
    "clarify_back",
)


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    t = (text or "").lower()
    return any(n.lower() in t for n in needles)


def infer_reaction_hint(
    reply_text: str,
    *,
    profile: CommunicationProfile,
    mode: str,
    scene_text: str = "",
) -> dict[str, Any]:
    loc = effective_locale(profile, scene_text, reply_text)
    rel = profile.relation
    text = reply_text or ""
    likely: list[str] = []
    unlikely: list[str] = []

    if mode == "deflect":
        if _contains_any(text, ("分阶段", "先给", "phased", "first cut", "core")):
            likely.extend(["partial_accept", "delay"])
        if _contains_any(text, ("对齐", "建议", "align", "suggest")):
            likely.append("clarify_back")
        if rel == RelationRole.MANAGER:
            likely.append("vague_promise")
            unlikely.append("cold_ignore")
            if _contains_any(text, ("合规", "风险", "compliance", "risk")):
                likely.append("accept")
        else:
            likely.append("partial_accept")
        if _contains_any(scene_text, ("今天", "今晚", "today", "tonight", "必须")):
            likely.append("escalate")
            unlikely.append("accept")

    elif mode == "push":
        likely.extend(["delay", "vague_promise", "partial_accept"])
        if _contains_any(text, ("依赖", "一起", "dependency", "together")):
            likely.append("clarify_back")
        if rel in (RelationRole.REPORT, RelationRole.PEER):
            likely.append("accept")
        unlikely.append("escalate")

    elif mode == "clap_back":
        if rel in (RelationRole.MANAGER, RelationRole.CLIENT, RelationRole.ELDER):
            likely.extend(["escalate", "cold_ignore", "deflect_blame"])
            unlikely.append("accept")
        else:
            likely.extend(["push_back", "partial_accept", "clarify_back"])
            unlikely.append("escalate")

    elif mode == "clarify":
        likely.extend(["clarify_back", "partial_accept", "delay"])
        unlikely.append("escalate")

    # De-dup preserve order
    def _uniq(xs: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in xs:
            if x not in seen and x in REACTION_TAGS:
                seen.add(x)
                out.append(x)
        return out[:4]

    likely_u = _uniq(likely) or ["partial_accept", "delay"]
    unlikely_u = _uniq(unlikely)

    one_line = _one_line(likely_u, unlikely_u, loc)
    return {
        "likely": likely_u,
        "unlikely": unlikely_u,
        "confidence": "medium",
        "one_line": one_line,
    }


def _one_line(likely: list[str], unlikely: list[str], loc: str) -> str:
    labels_zh = {
        "accept": "明确接受",
        "partial_accept": "口头答应但留余地",
        "delay": "拖延/改期",
        "vague_promise": "模糊答应",
        "escalate": "升级/抄送上级",
        "deflect_blame": "甩锅",
        "cold_ignore": "冷处理",
        "push_back": "顶回来",
        "clarify_back": "反问澄清",
    }
    labels_en = {
        "accept": "clear accept",
        "partial_accept": "soft yes with wiggle room",
        "delay": "stall/reschedule",
        "vague_promise": "vague promise",
        "escalate": "escalate/cc boss",
        "deflect_blame": "blame shift",
        "cold_ignore": "go silent",
        "push_back": "push back",
        "clarify_back": "ask clarifying questions",
    }
    lab = labels_en if loc == "en" else labels_zh
    top = " / ".join(lab.get(t, t) for t in likely[:2])
    if unlikely:
        low = lab.get(unlikely[0], unlikely[0])
        if loc == "en":
            return f"Likely: {top}; less likely: {low}."
        return f"较可能：{top}；较低可能：{low}。"
    if loc == "en":
        return f"Likely: {top}."
    return f"较可能：{top}。"


def attach_reaction_hints(
    payload: dict[str, Any],
    *,
    profile: CommunicationProfile,
    mode: str,
    scene_text: str = "",
) -> dict[str, Any]:
    options = payload.get("reply_options")
    if not isinstance(options, list) or not options:
        return payload
    hints_in = payload.get("reaction_hints")
    out_hints: list[dict[str, Any]] = []
    for i, opt in enumerate(options):
        if not isinstance(opt, str):
            continue
        if (
            isinstance(hints_in, list)
            and i < len(hints_in)
            and isinstance(hints_in[i], dict)
            and hints_in[i].get("likely")
        ):
            out_hints.append(hints_in[i])
        else:
            out_hints.append(
                infer_reaction_hint(opt, profile=profile, mode=mode, scene_text=scene_text)
            )
    payload["reaction_hints"] = out_hints
    return payload


def attach_clarify_intent_hypotheses(
    payload: dict[str, Any],
    *,
    profile: CommunicationProfile,
    scene_text: str,
) -> dict[str, Any]:
    """Map vague phrase readings to likely true intent + if user clarifies with Q."""
    loc = effective_locale(profile, scene_text)
    translations = payload.get("translations") or []
    hyps: list[dict[str, Any]] = []
    for i, tr in enumerate(translations[:4]):
        if not isinstance(tr, str):
            continue
        hyps.append(
            {
                "reading_index": i,
                "reading_summary": tr[:200],
                "likely_true_intent": [
                    "scope_expansion",
                    "quality_bar_raise",
                    "face_saving_delay",
                ][: 2 + (i % 2)],
                "if_you_ask_clarify": infer_reaction_hint(
                    tr,
                    profile=profile,
                    mode="clarify",
                    scene_text=scene_text,
                ),
            }
        )
    if hyps:
        payload["intent_hypotheses"] = hyps
    return payload
