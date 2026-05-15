from __future__ import annotations

import os

from pressure_skill.advisor.evidence_tone import evidence_instruction_block
from pressure_skill.advisor.strategy_rerank import rerank_reply_options
from pressure_skill.i18n import effective_locale
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.llm_client import complete_json_or_text


SYSTEM = """You are a workplace communication coach (Chinese + English). Match the user's language.
The user wants pushback / venting when the other side is low threat. Be sharp but: no slurs, no discrimination, no defamation, no illegal incitement.
Softer 'boundary' tone for manager/client/elder; more direct for peers when appropriate. Return JSON reply_options/rationale/risk_notes.
Each reply_option must restate a boundary plus a work-grounding next step (criteria, channel, time)—no pure vent with no constructive hook."""


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lower = (text or "").lower()
    return any(n.lower() in lower for n in needles)


def _clap_pool_formal_zh(provocation: str, profile: CommunicationProfile) -> list[str]:
    scene = provocation or ""
    opts = [
        "我理解你很急，但这种说法我不太能接受。我们把事拉回具体需求：你要的结果是什么、验收标准是什么，我可以按标准推进。",
        "收到。请把您对结果的要求、验收标准和时间节点说明白，我按标准推进，避免口头误会。",
        "我理解您的压力，但这种质疑我不太能接受。请把验收标准说清楚，我按标准推进交付。",
        "这类表述我不太能接受。请先对齐验收标准与推进节点，我们按标准把事推进下去。",
        "现在这样沟通效率很低。请你用可执行的要求说明白：时间、范围、优先级；否则我没法保证交付质量。",
    ]
    if _contains_any(scene, ("行不行", "耽误", "太慢", "能力")):
        opts.append(
            "我理解您着急，但用能力问题代替具体需求，我不太能接受。请把验收标准和时间节点说清楚，我按标准推进。"
        )
    if _contains_any(scene, ("差", "借口", "服务", "投诉", "专业")):
        opts.append(
            "我理解您的关切，但这种说法我不太能接受。请把验收标准和我们应对齐的推进节点说明白，我们按标准推进。"
        )
    if _contains_any(scene, ("锅", "甩锅", " blame")):
        opts.append(
            "这类甩锅式沟通我不太能接受。请对事说清楚：问题点、验收标准、推进节点，我们按标准协作推进。"
        )
    return opts


def _clap_pool_formal_en(provocation: str, profile: CommunicationProfile) -> list[str]:
    scene = provocation or ""
    opts = [
        "I get the urgency, but I can't accept that tone. Let's ground this: what outcome and acceptance criteria do you need? I'll align execution to that.",
        "Please restate as actionable asks—time, scope, acceptance criteria—and I'll push delivery against that standard.",
        "I can't accept that framing. Let's align on acceptance criteria and the next push milestone before we continue.",
        "This style isn't productive. Please restate as actionable asks—time, scope, priority—or I can't guarantee quality.",
    ]
    if _contains_any(scene, ("incompetent", "too slow", "delay", "excuse", "terrible")):
        opts.append(
            "I hear the concern, but I can't accept that tone. Please specify acceptance criteria and the push timeline so we can align and move forward."
        )
    return opts


def _clap_pool_peer_zh(provocation: str, profile: CommunicationProfile) -> list[str]:
    scene = provocation or ""
    opts = [
        "你这节奏我有点接不住。要不你先想清楚到底要什么，再一次性说清楚？我现在没法跟空气对齐。",
        "可以，但别用这种口气催。大家是协作，不是谁欠谁；你改个说法我更好配合。",
        "行，我知道了。后面这类事请提前一点说，别总踩点甩锅式沟通。",
        "请一次性把需求、时间和验收标准说清楚，我们好协作推进；这样来回催效率很低。",
        "咱们对事不对人：你把要的结果和截止点讲明白，我按标准配合。",
    ]
    if _contains_any(scene, ("催", "慢", "锅")):
        opts.append(
            "可以配合，但请别用这种口气。你把要的结果一次性说清楚，我们按协作方式推进。"
        )
    return opts


def _clap_pool_peer_en(provocation: str, profile: CommunicationProfile) -> list[str]:
    opts = [
        "This pace is hard to work with. Figure out what you actually need and say it once—I can't align to vibes.",
        "Fine—but not with that tone. We're collaborating, not hazing; rephrase and I'll help.",
        "Noted. Next time flag earlier; last-minute blame-y pings aren't workable.",
        "Please state the ask, deadline, and acceptance criteria in one message so we can collaborate productively.",
    ]
    return opts


def _fallback_clap_back(provocation: str, profile: CommunicationProfile, loc: str) -> dict:
    rel = profile.relation
    if rel in (RelationRole.MANAGER, RelationRole.CLIENT, RelationRole.ELDER):
        if loc == "en":
            return {
                "reply_options": _clap_pool_formal_en(provocation, profile),
                "rationale": "Upward/client/elder: boundary + facts instead of insults—signal limits with lower retaliation risk.",
                "risk_notes": [
                    "Pure insults create receipts; keep it about work.",
                    "If reviews/contracts are involved, avoid emotional wording in writing.",
                ],
            }
        return {
            "reply_options": _clap_pool_formal_zh(provocation, profile),
            "rationale": "对上级/客户/长辈：用「边界 + 拉回事实」替代辱骂，既表态又降低报复风险。",
            "risk_notes": [
                "纯辱骂或阴阳怪气容易留下把柄；优先对事不对人。",
                "若涉及绩效考核/合同，避免情绪化措辞留书面证据对自己不利。",
            ],
        }
    if loc == "en":
        return {
            "reply_options": _clap_pool_peer_en(provocation, profile),
            "rationale": "Peer/low threat: short boundary + mild pushback without escalating to personal attacks.",
            "risk_notes": [
                "If they screenshot habitually, keep sarcasm low.",
                "If they can impact your performance, downgrade to softer boundary tone.",
            ],
        }
    return {
        "reply_options": _clap_pool_peer_zh(provocation, profile),
        "rationale": "平级/低威胁场景：短句立边界 + 轻微反击，避免升级成人身冲突。",
        "risk_notes": [
            "若对方录音/截图习惯阴阳你，控制讽刺浓度。",
            "若其实对方能影响你绩效，把语气降到「软钉子」档。",
        ],
    }


def suggest_clap_back(
    provocation: str,
    profile: CommunicationProfile,
    *,
    use_llm: bool | None = None,
    rerank_weights: dict[str, float] | None = None,
) -> dict:
    loc = effective_locale(profile, provocation)
    if use_llm is False or (
        use_llm is None and not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY")
    ):
        return rerank_reply_options(
            _fallback_clap_back(provocation, profile, loc),
            profile=profile,
            mode="clap_back",
            scene_text=provocation,
            weights=rerank_weights,
        )

    lang = "English" if loc == "en" else "中文"
    user = f"""Profile JSON:\n{profile.model_dump_json(ensure_ascii=False)}\n\nAnnoying provocation:\n{provocation}\n\n{evidence_instruction_block(profile, scene_text=provocation)}\n\nReturn JSON:
{{
  "reply_options": ["..."],
  "rationale": "...",
  "risk_notes": ["..."]
}}
Write in {lang}. 2-3 options; be more restrained for manager/client."""
    raw = complete_json_or_text(SYSTEM, user, temperature=0.45)
    if isinstance(raw, dict) and "reply_options" in raw:
        return rerank_reply_options(
            raw,
            profile=profile,
            mode="clap_back",
            scene_text=provocation,
            weights=rerank_weights,
        )
    return rerank_reply_options(
        _fallback_clap_back(provocation, profile, loc),
        profile=profile,
        mode="clap_back",
        scene_text=provocation,
        weights=rerank_weights,
    )
