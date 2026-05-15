"""Heuristic portrait evidence tier: drives minimal vs deep intake and advisor tone."""

from __future__ import annotations

from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def infer_portrait_depth(
    profile: CommunicationProfile,
    *,
    transcript_raw: str = "",
    extra_scene_text: str = "",
) -> tuple[str, int]:
    """
    Returns (portrait_depth, evidence_score 0-100).

    - minimal: little chat + thin notes → short intake, tentative inference, no invented specifics.
    - standard: usable mix.
    - deep: enough material for mechanism-style hypotheses if anchored to profile/transcript.
    """
    t = (transcript_raw or "").strip()
    t_len = len(t)
    scene = (extra_scene_text or "").strip()
    scene_len = len(scene)
    feats = profile.features or {}
    msg_n = int(feats.get("message_count") or 0)
    cn = (profile.counterparty_notes or "").strip()
    ul = (profile.user_leverage_notes or "").strip()
    ex = (profile.extra_context_notes or "").strip()

    score = 0.0
    if profile.relation != RelationRole.UNKNOWN:
        score += 12.0
    score += min(t_len / 400.0, 1.0) * 28.0
    score += min(msg_n / 10.0, 1.0) * 22.0
    score += min(len(cn) / 120.0, 1.0) * 22.0
    score += min((len(ul) + len(ex)) / 100.0, 1.0) * 16.0
    score += min(scene_len / 220.0, 1.0) * 8.0

    evidence_score = int(round(min(score, 100.0)))
    if evidence_score < 38:
        return "minimal", evidence_score
    if evidence_score >= 72:
        return "deep", evidence_score
    return "standard", evidence_score
