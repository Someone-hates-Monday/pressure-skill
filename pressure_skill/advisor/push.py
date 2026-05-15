from __future__ import annotations

import os

from pressure_skill.advisor.evidence_tone import evidence_instruction_block
from pressure_skill.advisor.strategy_rerank import rerank_reply_options
from pressure_skill.i18n import effective_locale
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.llm_client import complete_json_or_text


SYSTEM = """You are a workplace communication coach (Chinese + English).
Match the user's language in JSON values. Help users push others gently: clear ask, reason, deadline, lower-cost options, no personal attacks.
Borrow from effective requests research: specific ask + reason it unblocks others + deadline + fallback that preserves their autonomy. Ban vague nudges with no anchor."""


def _fallback_push(goal: str, profile: CommunicationProfile, loc: str) -> dict:
    if loc == "en":
        return {
            "reply_options": [
                f"Could you prioritize {goal}? My downstream step is blocked without it. If you can share a first cut by 5pm today, we stay on track—otherwise core fields today and the rest tomorrow works too—what's easier for you?",
                f"On {goal}, what ETA should I plan around? I need to sync others. If you're blocked on dependencies (API/design), tell me and I'll chase them with you.",
            ],
            "rationale": "Shared goal + deadline + an easier fallback beats accusatory nudging.",
            "risk_notes": ["Avoid public call-outs; 1:1 is safer."],
        }
    return {
        "reply_options": [
            f"想麻烦你这边优先处理一下：{goal}。我这边后续环节卡在这一点上，如果今天下午 5 点前能给到初版，整体节奏会顺很多。若时间紧，也可以先给核心字段，其余明天补，你看哪种更顺手？",
            f"关于 {goal}，能否帮忙确认下预计完成时间？我这边需要同步给相关同学排期。如果有依赖项（比如接口/设计稿），你告诉我我来一起催。",
        ],
        "rationale": "用“共同目标 + 截止时间 + 减负选项”代替指责式催促。",
        "risk_notes": ["避免在公开场合点名施压；一对一沟通更安全。"],
    }


def suggest_push(
    goal: str,
    profile: CommunicationProfile,
    *,
    use_llm: bool | None = None,
    rerank_weights: dict[str, float] | None = None,
) -> dict:
    loc = effective_locale(profile, goal)
    if use_llm is False or (
        use_llm is None and not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY")
    ):
        return rerank_reply_options(
            _fallback_push(goal, profile, loc),
            profile=profile,
            mode="push",
            scene_text=goal,
            weights=rerank_weights,
        )

    lang = "English" if loc == "en" else "中文"
    user = f"""Profile JSON:\n{profile.model_dump_json(ensure_ascii=False)}\n\nGoal to push:\n{goal}\n\n{evidence_instruction_block(profile, scene_text=goal)}\n\nReturn JSON:
{{
  "reply_options": ["..."],
  "rationale": "...",
  "risk_notes": ["..."]
}}
Write in {lang}. 2-3 options; ~60-140 Chinese characters or similar density in English."""
    raw = complete_json_or_text(SYSTEM, user, temperature=0.35)
    if isinstance(raw, dict) and "reply_options" in raw:
        return rerank_reply_options(
            raw,
            profile=profile,
            mode="push",
            scene_text=goal,
            weights=rerank_weights,
        )
    return rerank_reply_options(
        _fallback_push(goal, profile, loc),
        profile=profile,
        mode="push",
        scene_text=goal,
        weights=rerank_weights,
    )
