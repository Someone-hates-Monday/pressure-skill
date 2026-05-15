"""Shared LLM instructions keyed by heuristic portrait evidence depth."""

from __future__ import annotations

from pressure_skill.analyzer.portrait_depth import infer_portrait_depth
from pressure_skill.analyzer.profile import CommunicationProfile


def evidence_instruction_block(
    profile: CommunicationProfile,
    *,
    transcript_raw: str = "",
    scene_text: str = "",
) -> str:
    depth, score = infer_portrait_depth(
        profile,
        transcript_raw=transcript_raw,
        extra_scene_text=scene_text,
    )
    rules = {
        "minimal": (
            "Portrait evidence: MINIMAL (score {score}/100). "
            "Intent: only low-commitment hypotheses; each must include what would falsify it. "
            "Replies: anchor ONLY to facts already in Profile JSON or the user's scene text—no invented deadlines, motives, or names. "
            "Avoid generic pep talk; if a fact is missing, say what you need to ask next."
        ),
        "standard": (
            "Portrait evidence: STANDARD (score {score}/100). "
            "Intent: label confidence (high/med/low) per bullet. "
            "Replies: each option must cite at least one concrete lever from profile (leverage, context, portrait, or praise_vs_critique pattern)."
        ),
        "deep": (
            "Portrait evidence: DEEP (score {score}/100). "
            "Intent: you may infer mechanisms (incentives, risk aversion, escalation habits, face needs) ONLY when tied to transcript/portrait/context fields—quote the cue. "
            "Replies: weave specific stakes, recurring patterns, or trade-offs from the profile; prefer BATNA / phased trade / written-vs-oral channel tactics over generic scripts. "
            "Still avoid mind-reading beyond evidence."
        ),
    }
    return rules[depth].format(score=score)
