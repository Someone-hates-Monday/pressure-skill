from __future__ import annotations

import re
from typing import Any

from pressure_skill.advisor.rerank_weights import active_weights
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole

_TIME_RE = re.compile(r"(\d{1,2}[:：]\d{2}|today|tomorrow|tonight|周[一二三四五六日天]|明天|今天|下周)")


def _tokenize_notes(text: str) -> list[str]:
    raw = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,}", text or "")
    stop = {
        "这个",
        "那个",
        "以及",
        "如果",
        "我们",
        "你们",
        "他们",
        "please",
        "would",
        "could",
        "with",
        "that",
        "this",
    }
    return [t.lower() for t in raw if t.lower() not in stop]


def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    t = text.lower()
    return any(w.lower() in t for w in words)


def score_reply_option(
    option: str,
    *,
    profile: CommunicationProfile,
    mode: str,
    scene_text: str,
    weights: dict[str, float] | None = None,
) -> tuple[float, list[str]]:
    w = weights if weights is not None else active_weights()
    score = 0.0
    reasons: list[str] = []
    text = option.strip()
    rel = profile.relation
    th = int(w.get("min_len_threshold", 24))
    if len(text) >= th:
        score += w.get("min_len", 0.4)
        reasons.append("min_len")
    if _TIME_RE.search(text):
        score += w.get("time_anchor", 1.1)
        reasons.append("has_time_anchor")
    if _contains_any(text, ("先", "后", "if", "otherwise", "优先", "分阶段", "core", "appendix")):
        score += w.get("tradeoff", 1.0)
        reasons.append("has_tradeoff")
    if _contains_any(text, ("验收", "标准", "criteria", "scope", "priority", "范围")):
        score += w.get("acceptance_scope", 0.9)
        reasons.append("has_acceptance_scope")

    if mode == "push" and _contains_any(text, ("能否", "could you", "eta", "预计", "麻烦")):
        score += w.get("push_clear_ask", 1.0)
        reasons.append("push_has_clear_ask")
    if mode == "deflect" and _contains_any(text, ("建议", "I suggest", "对齐", "align", "先给")):
        score += w.get("deflect_negotiation", 1.0)
        reasons.append("deflect_has_negotiation_move")
    if mode == "clap_back":
        if _contains_any(
            text,
            ("不能接受", "can't accept", "请你", "please restate", "推进", "对齐", "align"),
        ):
            score += w.get("clap_boundary", 0.8)
            reasons.append("clap_back_has_boundary")
        if _contains_any(
            text,
            ("说清楚", "一次性", "协作", "对事", "边界", "rephrase", "productive"),
        ):
            score += w.get("clap_boundary_extra", 1.2)
            reasons.append("clap_back_soft_boundary")
        if rel in (RelationRole.MANAGER, RelationRole.CLIENT, RelationRole.ELDER):
            if _contains_any(text, ("验收", "标准", "criteria")) and _contains_any(
                text, ("推进", "对齐", "push", "align")
            ):
                score += w.get("clap_formal_criteria", 0.7)
                reasons.append("clap_formal_criteria_push")
    if mode == "clarify" and ("?" in text or "？" in text):
        score += w.get("clarify_question", 0.9)
        reasons.append("clarify_is_question")

    if rel in (RelationRole.MANAGER, RelationRole.CLIENT, RelationRole.ELDER):
        if _contains_any(text, ("请", "您", "could", "please", "understood", "建议")):
            score += w.get("relation_formality", 0.9)
            reasons.append("relation_formality_fit")
        if _contains_any(text, ("闭嘴", "滚", "废话", "idiot")):
            score += w.get("aggressive_penalty", -2.5)
            reasons.append("relation_too_aggressive")

    scene = scene_text.lower()
    if "尽快" in scene or "asap" in scene or "今天" in scene:
        if _TIME_RE.search(text):
            score += w.get("urgency_match", 0.6)
            reasons.append("matches_urgency")

    notes_blob = " ".join(
        [
            profile.user_leverage_notes or "",
            profile.extra_context_notes or "",
            profile.counterparty_notes or "",
            profile.user_purpose or "",
        ]
    )
    note_tokens = _tokenize_notes(notes_blob)
    if note_tokens:
        hits = sum(1 for t in note_tokens if t in text.lower())
        if hits:
            cap = w.get("note_hit_cap", 1.2)
            unit = w.get("note_hit_unit", 0.25)
            score += min(cap, hits * unit)
            reasons.append("anchors_profile_notes")

    if "directive_tone" in (profile.pattern_tags or []):
        if _contains_any(text, ("范围", "priority", "scope", "分阶段", "先")):
            score += w.get("directive_fit", 0.4)
            reasons.append("fits_directive_countermove")
    if "fast_turnaround" in (profile.pattern_tags or []):
        if _TIME_RE.search(text):
            score += w.get("fast_turnaround_fit", 0.4)
            reasons.append("fits_fast_turnaround")

    if mode == "deflect" and _contains_any(scene, ("会议室", "开会", "马上来")):
        if _contains_any(text, ("异步", "邮件", "如果", "分钟")):
            score += w.get("deflect_meeting_async", 1.0)
            reasons.append("deflect_meeting_async_fit")

    return score, reasons


def rerank_reply_options(
    payload: dict[str, Any],
    *,
    profile: CommunicationProfile,
    mode: str,
    scene_text: str,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    options = payload.get("reply_options")
    if not isinstance(options, list) or not options:
        return payload

    w = weights if weights is not None else active_weights()
    ranked: list[tuple[float, str, list[str]]] = []
    for opt in options:
        if not isinstance(opt, str):
            continue
        sc, rs = score_reply_option(opt, profile=profile, mode=mode, scene_text=scene_text, weights=w)
        ranked.append((sc, opt, rs))
    if not ranked:
        return payload

    ranked.sort(key=lambda x: x[0], reverse=True)
    payload["reply_options"] = [x[1] for x in ranked]
    payload["strategy_trace"] = [
        {"score": round(x[0], 3), "reason_tags": x[2], "preview": x[1][:80]} for x in ranked
    ]
    return payload


__all__ = ["rerank_reply_options", "score_reply_option"]
