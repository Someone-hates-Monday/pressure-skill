from __future__ import annotations

import os

from pressure_skill.advisor.evidence_tone import evidence_instruction_block
from pressure_skill.i18n import effective_locale
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.llm_client import complete_json_or_text


SYSTEM = """You are a workplace communication coach (Chinese + English).
Match the user's language. Turn vague asks into verifiable acceptance criteria (who signs off, dimensions, format, deadline), not pep talk.
If profile.discipline_subfield or profile.artefact_preferences_notes is set, map phrases like "write clearly" to concrete artefacts
(math derivations vs code vs diagrams vs tables vs long prose). If both are empty, still surface 2–3 mutually exclusive readings
in clarifying_questions (e.g. theory-style formalism vs systems vs experiments).
Each clarifying_question should be answerable in one reply; ban vague "just be clearer" echoes."""


def _fallback_clarify(vague_request: str, profile: CommunicationProfile, loc: str) -> dict:
    if loc == "en":
        return {
            "translations": [
                "Turn 'more detail' into: which data dimensions (time range, grain, comparison baseline), charts or not, how many conclusion paragraphs, appendix scope.",
                "Turn 'ASAP' into: a concrete time + an acceptable downgrade (e.g., numbers first, formatting later).",
                "Turn 'write it clearly' (slides/docs) into: primary artefact—theorem/lemma chain and metrics vs runnable code and configs vs architecture/storyline vs experiment tables.",
            ],
            "clarifying_questions": [
                "Who signs off—and what failure mode worries them most: data definition or narrative clarity?",
                "Can you share a redacted example of 'good enough' or the paragraph structure to mirror?",
                "If discipline is unclear: should 'clear' mean formal math (definitions, derivations, bounds), engineering proof (interfaces, repro), or empirical narrative (hypotheses, plots, ablations)?",
            ],
            "rationale": "Replace adjectives with checkable acceptance criteria to reduce churn.",
        }
    return {
        "translations": [
            "把“详细一点”具体化为：需要包含哪些数据维度（时间范围、粒度、对比口径）、是否需要可视化（表/图类型）、结论段落希望几段、附录材料范围。",
            "把“尽快”具体化为：期望时间点 + 可接受的降级版本（例如先给核心数，后补排版）。",
            "把“写明白 / PPT 写清楚”具体化为：以哪类材料为主——数学定义与推导链+指标、可复现代码与实验配置、系统框图与接口、还是假设—实验—结果的叙事与图表。",
        ],
        "clarifying_questions": [
            "这次交付的验收人是谁？最担心出现的错误类型是数据口径问题还是表达不清？",
            "能否给一个你认为“足够好”的参考样例（脱敏）或指出要对其齐的段落结构？",
            "对方口中的“写明白”更可能指：①公式与推导 ②代码与复现细节 ③图与流程 ④长文论证？若不确定，建议用邮件让对方三选一或勾选。",
        ],
        "rationale": "用可验证标准替代形容词，减少反复被追问的概率。",
    }


def suggest_clarify(
    vague_request: str,
    profile: CommunicationProfile,
    *,
    use_llm: bool | None = None,
) -> dict:
    loc = effective_locale(profile, vague_request)
    if use_llm is False or (
        use_llm is None and not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY")
    ):
        return _fallback_clarify(vague_request, profile, loc)

    lang = "English" if loc == "en" else "中文"
    user = f"""Profile JSON:\n{profile.model_dump_json(ensure_ascii=False)}\n\nVague request:\n{vague_request}\n\nUse praise_vs_critique_notes if present. Heavily use discipline_subfield and artefact_preferences_notes when set; if missing, ask questions that split math vs code vs figures vs prose.\n{evidence_instruction_block(profile, scene_text=vague_request)}\n\nReturn JSON:
{{
  "translations": ["..."],
  "clarifying_questions": ["..."],
  "rationale": "..."
}}
Write in {lang}."""
    raw = complete_json_or_text(SYSTEM, user, temperature=0.35)
    if isinstance(raw, dict) and "translations" in raw:
        return raw
    return _fallback_clarify(vague_request, profile, loc)
