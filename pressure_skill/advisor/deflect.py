from __future__ import annotations

import os
import re

from pressure_skill.advisor.evidence_tone import evidence_instruction_block
from pressure_skill.advisor.strategy_rerank import rerank_reply_options
from pressure_skill.i18n import effective_locale
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.llm_client import complete_json_or_text


SYSTEM = """You are a workplace communication coach (Chinese + English).
Rules: match the user's language in JSON string values—if the situation text is primarily English, write reply_options/rationale/risk_notes in English; otherwise use Chinese.
Help defer pressure, negotiate scope/timeline without burning bridges. Tone: more results-oriented upward, collaborative peer-to-peer, professional with clients.
Use negotiation structure (interests vs positions, scope/time trades, phased delivery) instead of generic reassurance. Each reply_option must contain at least one concrete lever, constraint, or date drawn from the Profile JSON or the situation text—never empty pep talk."""


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lower = (text or "").lower()
    return any(n.lower() in lower for n in needles)


def _first_match(pattern: str, text: str) -> str:
    m = re.search(pattern, text, flags=re.IGNORECASE)
    return m.group(1) if m else ""


# Slot extraction scans user-provided strings; cap length so regex stays cheap
# even if a case/profile field is accidentally huge (e.g. pasted transcripts).
_SLOT_SCAN_CAP = 1200


def _clip_slot_text(s: str) -> str:
    if not s:
        return ""
    return s if len(s) <= _SLOT_SCAN_CAP else s[:_SLOT_SCAN_CAP]


_ZH_CONSTRAINT_KEYS = ("合规", "脱敏", "排期", "评审", "优先", "回款", "依赖", "风险", "测试", "上线")

_EN_CONSTRAINT_KEYS = ("compliance", "dependency", "stability", "priority", "billing", "review", "test", "risk")


def _constraint_snippet_zh(notes: str) -> str:
    """Linear-time window around first negotiation keyword (avoids regex backtracking)."""
    t = _clip_slot_text(notes)
    if not t:
        return ""
    best_i = 10**9
    best_k = ""
    for k in _ZH_CONSTRAINT_KEYS:
        i = t.find(k)
        if i != -1 and i < best_i:
            best_i, best_k = i, k
    if not best_k:
        return ""
    lo = max(0, best_i - 36)
    hi = min(len(t), best_i + len(best_k) + 36)
    return t[lo:hi].strip()


def _constraint_snippet_en(notes: str) -> str:
    t = _clip_slot_text(notes)
    if not t:
        return ""
    low = t.lower()
    best_i = 10**9
    best_k = ""
    for k in _EN_CONSTRAINT_KEYS:
        i = low.find(k)
        if i != -1 and i < best_i:
            best_i, best_k = i, k
    if not best_k:
        return ""
    lo = max(0, best_i - 40)
    hi = min(len(t), best_i + len(best_k) + 40)
    return t[lo:hi].strip()


def _deadline_phrase_zh(deadline: str) -> str:
    if not deadline:
        return "本周"
    if deadline.endswith("前"):
        return deadline
    return f"{deadline}前"


def _scene_slots_zh(situation: str, profile: CommunicationProfile) -> dict[str, str]:
    scene = _clip_slot_text(situation or "")
    deadline = _first_match(
        r"(今天下班前|今天|今晚|明天|周末|下周[一二三四五六日天]?|周[一二三四五六日天]|本周)",
        scene,
    ) or "本周"
    deliverable = _first_match(
        r"(完整版|附录|原始数据|数据|文档|接口|周报|材料|会议|功能|需求|上线)",
        scene,
    ) or "核心交付"
    notes = _clip_slot_text(
        "；".join(
            x
            for x in [
                profile.user_leverage_notes or "",
                profile.extra_context_notes or "",
                profile.counterparty_notes or "",
            ]
            if x
        )
    )
    constraint = _constraint_snippet_zh(notes)
    if not constraint:
        constraint = "质量与稳定性要求"
    return {"deadline": deadline, "deliverable": deliverable, "constraint": constraint}


def _scene_slots_en(situation: str, profile: CommunicationProfile) -> dict[str, str]:
    scene = _clip_slot_text(situation or "")
    deadline = _first_match(
        r"(today(?:\s+EOD)?|tonight|tomorrow|this weekend|weekend|next week|this week)",
        scene,
    ) or "this week"
    deliverable = _first_match(
        r"(full version|appendix|raw data|data|documentation|report|milestone|api|feature|release)",
        scene,
    ) or "core deliverable"
    notes = _clip_slot_text(
        " ; ".join(
            x
            for x in [
                profile.user_leverage_notes or "",
                profile.extra_context_notes or "",
                profile.counterparty_notes or "",
            ]
            if x
        )
    )
    constraint = _constraint_snippet_en(notes)
    if not constraint:
        constraint = "quality and stability constraints"
    return {"deadline": deadline, "deliverable": deliverable, "constraint": constraint}


def _deflect_pool_zh(situation: str, profile: CommunicationProfile) -> list[str]:
    rel = profile.relation.value
    scene = situation or ""
    slots = _scene_slots_zh(situation, profile)
    opts = [
        "收到。为确保质量，我想和您对齐一下优先级：我手头还有 A、B 两项在本周截止。这份材料您更希望我先保证哪部分的深度？其余部分我可以在周五前给出框架，下周一补齐细节，您看是否可行？",
        "明白您的节点。按上次类似交付的经验，完整版大约需要 X 天。如果本周五前必须给到一版，我建议先交付核心数据与结论，附录与排版我放到下周二，这样风险更可控。",
        "我建议先把验收范围定清楚：本轮先完成主流程与关键指标，次要项放到下一迭代。这样今天可以给您可验收版本，后续再按优先级补齐。",
        "可以推进，但我需要一个可执行顺序：先确定必交付清单，再排可延后项。若今晚前要结果，我先给核心页和决策结论，明天补完整附件。",
        "我理解您着急，我这边也在并行处理高优任务。为了不返工，建议先确认验收标准与截止点：先交可上线版本，余下优化在下个时间窗完成。",
        f"我理解您希望在{_deadline_phrase_zh(slots['deadline'])}完成 {slots['deliverable']}。为了稳住结果，我建议先交可验收主干，剩余细节分到下一时段；当前约束是 {slots['constraint']}，不建议硬压到一次性交付。",
        f"这项我会推进。建议按“两步交付”：在{_deadline_phrase_zh(slots['deadline'])}先给 {slots['deliverable']} 的核心结果与结论，随后补齐附件和扩展项，这样能在满足时点的同时控制 {slots['constraint']} 带来的返工风险。",
    ]
    if rel in ("manager", "client", "elder"):
        opts.append(
            "收到。为了保证您要的结果可落地，我建议先对齐范围和优先级：今天先交决策所需核心内容，周一补全细节与附件，并附上风险说明，您看这样是否更稳妥？"
        )
    else:
        opts.append(
            "我可以配合，但想先把边界说清：先把最影响进度的部分做完，剩余项按优先级排到明天。这样你今天有可用结果，我这边也能保证质量。"
        )

    if _contains_any(scene, ("周末", "加班", "今晚", "夜里")):
        opts.append(
            "这项我可以继续推进，但周末/今晚我建议改成“值守 + 关键事项优先”：先处理必须上线部分，其余排到明天白天集中完成，质量和节奏都更可控。"
        )
    if _contains_any(scene, ("会议室", "开会", "马上来", "对齐", "同步")):
        opts.insert(
            0,
            "我现在在处理线上优先事项。建议先通过邮件异步对齐：您发我时间、范围与验收三点；如果仍有分歧，我们再约 15 分钟会议集中拍板。",
        )
    if _contains_any(scene, ("数据", "脱敏", "合规", "原始")):
        opts.append(
            "原始数据这块涉及脱敏与合规流程，我建议先给可用汇总与结论，明天补齐合规版明细。这样既满足您当前决策，也不触发合规风险。"
        )
    return opts


def _deflect_pool_en(situation: str, profile: CommunicationProfile) -> list[str]:
    rel = profile.relation.value
    scene = situation or ""
    slots = _scene_slots_en(situation, profile)
    opts = [
        "Got it. To protect quality, I need to align priorities: I also have A and B due this week. Which part of this deliverable do you want deepest first? I can share a solid outline by Friday and fill details by Monday—does that work?",
        "Understood on the deadline. Based on similar past work, a full version realistically needs X days. If you need something by Friday, I suggest we ship core findings + data first and move appendix/formatting to Tuesday to reduce risk.",
        "I suggest we lock acceptance scope first: this round delivers the core flow and key metrics, and lower-priority items move to the next iteration. That gives you something reviewable today without hiding risk.",
        "I can move this forward, but I need an executable sequence: first confirm must-have outcomes, then rank deferrable items. If tonight is fixed, I can deliver decision-critical pages now and complete attachments tomorrow.",
        f"I understand you need the {slots['deliverable']} by {slots['deadline']}. I suggest we deliver the decision-critical core first and stage the rest in the next slot; this keeps momentum while managing {slots['constraint']}.",
        f"I can commit to a two-step plan: by {slots['deadline']} I deliver the core {slots['deliverable']} with acceptance criteria, then complete appendices and polish next. That reduces rework pressure tied to {slots['constraint']}.",
    ]
    if rel in ("manager", "client", "elder"):
        opts.append(
            "Understood. To make this dependable, let's align scope and priority first: today I deliver decision-ready core content, and on Monday I complete the detailed appendix with risk notes."
        )
    else:
        opts.append(
            "I can support this, but let's keep boundaries clear: we finish the highest-impact part first, then schedule the rest for tomorrow. You still get usable output today and we avoid rushed rework."
        )
    if _contains_any(scene, ("weekend", "overtime", "tonight")):
        opts.append(
            "I can keep momentum, but for tonight/weekend I recommend duty mode plus prioritization: we ship must-have items first and schedule non-critical parts tomorrow in focused blocks."
        )
    if _contains_any(scene, ("meeting", "join now", "sync now", "war room")):
        opts.append(
            "I'm handling a priority issue right now. Let's align asynchronously first: send the top 3 constraints (deadline, scope, acceptance), and I'll return a concrete plan before we decide whether a 15-minute sync is still needed."
        )
    if _contains_any(scene, ("data", "compliance", "raw")):
        opts.append(
            "Raw data delivery touches compliance checks. I suggest we send decision-ready summaries first and provide the compliant detailed package tomorrow, so we keep speed without creating policy risk."
        )
    return opts


def _fallback_deflect(situation: str, profile: CommunicationProfile, loc: str) -> dict:
    rel = profile.relation.value
    if loc == "en":
        return {
            "reply_options": _deflect_pool_en(situation, profile),
            "rationale": f"relation={rel}: use priority trade-offs + phased delivery instead of a blunt 'no'.",
            "risk_notes": [
                "If they hate negotiation, shorten to one commitment + one concrete timestamp.",
            ],
        }
    return {
        "reply_options": _deflect_pool_zh(situation, profile),
        "rationale": f"关系={rel}：用“优先级对齐 + 分阶段交付”替代单纯拒绝，降低对抗感。",
        "risk_notes": ["若对方极度厌恶讨价还价，可缩短为单句承诺 + 一个具体时间点。"],
    }


def suggest_deflect(
    situation: str,
    profile: CommunicationProfile,
    *,
    use_llm: bool | None = None,
    rerank_weights: dict[str, float] | None = None,
) -> dict:
    loc = effective_locale(profile, situation)
    if use_llm is False or (
        use_llm is None and not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY")
    ):
        return rerank_reply_options(
            _fallback_deflect(situation, profile, loc),
            profile=profile,
            mode="deflect",
            scene_text=situation,
            weights=rerank_weights,
        )

    lang = "English" if loc == "en" else "中文"
    user = f"""Profile JSON:\n{profile.model_dump_json(ensure_ascii=False)}\n\nSituation:\n{situation}\n\n{evidence_instruction_block(profile, scene_text=situation)}\n\nReturn JSON:
{{
  "reply_options": ["..."],
  "reaction_hints": [{{"likely": ["partial_accept","delay"], "unlikely": ["escalate"], "confidence": "medium", "one_line": "..."}}],
  "rationale": "...",
  "risk_notes": ["..."]
}}
reaction_hints length must match reply_options. Tags: accept, partial_accept, delay, vague_promise, escalate, deflect_blame, cold_ignore, push_back, clarify_back.
Write reply_options/rationale/risk_notes in {lang}. 2-3 options, 80-160 words each if Chinese; similar density if English."""
    raw = complete_json_or_text(SYSTEM, user, temperature=0.4)
    if isinstance(raw, dict) and "reply_options" in raw:
        return rerank_reply_options(
            raw,
            profile=profile,
            mode="deflect",
            scene_text=situation,
            weights=rerank_weights,
        )
    return rerank_reply_options(
        _fallback_deflect(situation, profile, loc),
        profile=profile,
        mode="deflect",
        scene_text=situation,
        weights=rerank_weights,
    )
