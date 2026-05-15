from __future__ import annotations

from pressure_skill.i18n import effective_locale
from pressure_skill.analyzer.portrait_depth import infer_portrait_depth
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def _pick(loc: str, zh: str, en: str) -> str:
    return en if loc == "en" else zh


def _portrait_depth_hint(loc: str, depth: str) -> str:
    if depth == "minimal":
        return _pick(
            loc,
            "画像证据偏少（minimal）：意图只做试探性假设并写可推翻条件；话术禁止编造细节，只嵌入用户已提供事实。",
            "Portrait evidence is minimal: keep intent hypotheses tentative with disconfirmers; do not invent specifics—anchor only to stated facts.",
        )
    if depth == "deep":
        return _pick(
            loc,
            "画像证据充足（deep）：可做机制级推断，但必须能指回侧写/对话/场外的具体依据；话术须显式使用筹码、模式或约束。",
            "Portrait evidence is deep: mechanism-level intent OK only when traceable to notes/chat/context; tie replies to named patterns, incentives, or leverage.",
        )
    return _pick(
        loc,
        "画像证据中等（standard）：推断须标置信度；每条话术至少落一笔画像或场景中的具体锚点。",
        "Portrait evidence is standard: label confidence on guesses; anchor each reply line to at least one concrete profile or scene fact.",
    )


def assess_readiness(
    profile: CommunicationProfile,
    *,
    transcript_raw: str,
    scene_text_blob: str = "",
    has_situation: bool,
    has_goal: bool,
    has_vague: bool,
    has_clap_back: bool = False,
    user_purpose: str | None = None,
) -> dict:
    """
    Heuristic: when the portrait is thin vs usable, and what to ask next.
    """
    loc = effective_locale(
        profile,
        transcript_raw,
        user_purpose or "",
    )

    t = (transcript_raw or "").strip()
    t_len = len(t)
    feats = profile.features or {}
    msg_n = int(feats.get("message_count") or 0)

    cn = (profile.counterparty_notes or "").strip()
    ul = (profile.user_leverage_notes or "").strip()
    ex = (profile.extra_context_notes or "").strip()
    purpose = (user_purpose or profile.user_purpose or "").strip()

    portrait_depth, evidence_score = infer_portrait_depth(
        profile,
        transcript_raw=t,
        extra_scene_text=scene_text_blob,
    )
    depth_hint = _portrait_depth_hint(loc, portrait_depth)

    missing: list[str] = []
    if profile.relation == RelationRole.UNKNOWN:
        missing.append(
            _pick(
                loc,
                "relation（对方相对你的身份：上级/平级/下属/客户/长辈）",
                "relation (their role vs you: manager / peer / report / client / elder)",
            )
        )
    if t_len < 40 and msg_n < 2 and len(cn) < 15:
        missing.append(
            _pick(
                loc,
                "聊天记录片段，或对方人物侧写（至少一项，脱敏）",
                "chat snippet OR a short portrait of the other person (at least one; redact secrets)",
            )
        )
    if not profile.reply_speed_hint and t_len < 40 and len(cn) < 15:
        missing.append(
            _pick(
                loc,
                "reply_speed_hint（对方回消息快慢的主观印象，可选但有助于画像）",
                "reply_speed_hint (how fast they usually reply: fast/slow/irregular)",
            )
        )
    if has_vague and not (profile.praise_vs_critique_notes or "").strip():
        missing.append(
            _pick(
                loc,
                "praise_vs_critique_notes（对方曾满意/不满意的交付对比，可显著提升「详细」类澄清质量）",
                "praise_vs_critique_notes (one 'good' vs 'bad' example improves clarifying vague asks)",
            )
        )
    if has_vague and not (profile.discipline_subfield or "").strip():
        missing.append(
            _pick(
                loc,
                "discipline_subfield（学科/子领域：否则「写明白」易误判为代码/流程图而非公式推导等）",
                "discipline_subfield (subfield; avoids misreading 'write clearly' as code vs math)",
            )
        )
    if has_vague and not (profile.artefact_preferences_notes or "").strip():
        missing.append(
            _pick(
                loc,
                "artefact_preferences_notes（对方偏公式/代码/图/表/书面哪类载体；强烈建议填写）",
                "artefact_preferences_notes (formulas vs code vs figs vs tables—strongly recommended)",
            )
        )
    if not purpose:
        missing.append(
            _pick(
                loc,
                "user_purpose（你此刻最想达成的目的：必须先由用户说清楚）",
                "user_purpose (what you want to achieve this round — must be stated explicitly)",
            )
        )
    if not ul and not ex:
        missing.append(
            _pick(
                loc,
                "user_leverage_notes 或 extra_context_notes（筹码/场外信息至少写一点，避免话术空泛；可简短）",
                "user_leverage_notes OR extra_context_notes (your leverage / context — at least one short note)",
            )
        )

    warnings: list[str] = []
    if has_clap_back and profile.relation == RelationRole.MANAGER:
        warnings.append(
            _pick(
                loc,
                "对上级「硬怼」风险高：默认话术偏软钉子；请确认对方确实威胁不大。",
                "Pushback to a manager is risky: templates skew 'soft boundary'; confirm their leverage is low.",
            )
        )

    critical = 0
    if profile.relation == RelationRole.UNKNOWN:
        critical += 1
    if t_len < 40 and msg_n < 2 and len(cn) < 15:
        critical += 1
    if not purpose:
        critical += 1

    if critical >= 2:
        level = "thin"
        summary = _pick(
            loc,
            "画像或目的依据偏少：建议补「关系 + 侧写/对话 + 你的目的」后再采信具体措辞。",
            "Thin evidence: add role + portrait/chat + your stated goal before trusting wording details.",
        )
    elif critical == 1 or len(missing) >= 2:
        level = "ok_with_gaps"
        summary = _pick(
            loc,
            "可用作草稿：建议结合筹码与场外信息二次润色；回怼选项务必核对权力关系风险。",
            "Draft quality: weave in leverage/context; if using pushback, double-check power dynamics.",
        )
    else:
        level = "ok"
        summary = _pick(
            loc,
            "信息基本够用：可生成具体话术；仍建议脱敏、核对语气，回怼控制分寸。",
            "Good enough to draft replies; still redact secrets and calibrate tone—especially for pushback.",
        )

    if portrait_depth == "deep" and level == "ok":
        summary = _pick(
            loc,
            summary + "（证据分层：deep——可做机制级推断，但仍须逐条对齐画像依据。）",
            summary + " (Evidence tier: deep—mechanism-level inferences allowed if tied to captured facts.)",
        )
    elif portrait_depth == "minimal":
        summary = _pick(
            loc,
            summary + "（证据分层：minimal——少读心、多澄清；话术避免想当然。）",
            summary + " (Evidence tier: minimal—avoid mind-reading; prefer clarifying questions.)",
        )

    agent_steps = (
        [
            "If level is thin: ask at most 2 follow-ups at a time.",
            "Explicitly use leverage + context notes—avoid generic platitudes.",
            "If user chose pushback (D): restate risks; default to softer boundary for managers.",
        ]
        if loc == "en"
        else [
            "若 level 为 thin：一次最多追问 2 个缺失项。",
            "输出须显式使用画像中的筹码与场外信息，避免套话。",
            "若用户选回怼（D）：复述风险 notes，对上级默认推荐软钉子版本。",
        ]
    )
    if portrait_depth == "minimal":
        agent_steps.append(
            _pick(
                loc,
                "证据分层 minimal：向导走短采集；意图与话术禁止过度读心。",
                "Evidence tier minimal: short intake path; no high-confidence mind-reading.",
            )
        )
    elif portrait_depth == "deep":
        agent_steps.append(
            _pick(
                loc,
                "证据分层 deep：可走深画像推断（须逐条引用依据）；话术用利益/约束/升级链等机制语言。",
                "Evidence tier deep: mechanism-level analysis OK if cited; prefer interests/BATNA/escalation patterns over generic scripts.",
            )
        )
    else:
        agent_steps.append(
            _pick(
                loc,
                "证据分层 standard：推断标置信度；话术至少锚定一处画像事实。",
                "Evidence tier standard: label confidence; anchor wording to profile facts.",
            )
        )

    script_note = _pick(
        loc,
        "bundle_local.py 产出结构化 JSON；意图推测与置信度由 Cursor Agent 结合 readiness 生成。",
        "bundle_local.py returns structured JSON; intent hypotheses come from the Cursor Agent using readiness.",
    )

    return {
        "locale": loc,
        "level": level,
        "summary": summary,
        "portrait_depth": portrait_depth,
        "evidence_score": evidence_score,
        "portrait_depth_hint": depth_hint,
        "missing_fields": missing,
        "warnings": warnings,
        "agent_next_steps": agent_steps,
        "script_note": script_note,
    }
