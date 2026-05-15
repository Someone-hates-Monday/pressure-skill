from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def test_fallback_deflect_has_diverse_candidate_pool():
    profile = CommunicationProfile(
        relation=RelationRole.MANAGER,
        user_leverage_notes="测试时间不足",
        extra_context_notes="先给核心结论",
    )
    out = suggest_deflect("今天下班前必须交完整版", profile, use_llm=False)
    options = out.get("reply_options") or []
    assert len(options) >= 6
    assert any("验收" in x for x in options)
    assert any("建议" in x for x in options)


def test_fallback_deflect_adds_scene_specific_candidates():
    profile = CommunicationProfile(relation=RelationRole.CLIENT)
    out = suggest_deflect("今天把所有原始数据导给我", profile, use_llm=False)
    options = out.get("reply_options") or []
    assert any("合规" in x for x in options)
    assert any("风险" in x for x in options)


def test_fallback_deflect_injects_scene_slots():
    profile = CommunicationProfile(
        relation=RelationRole.MANAGER,
        user_leverage_notes="数据脱敏流程不能跳过",
    )
    out = suggest_deflect("今天下班前给我完整版数据", profile, use_llm=False)
    options = out.get("reply_options") or []
    assert any("今天下班前" in x for x in options)
    assert any("完整版" in x for x in options)
    assert any("脱敏" in x for x in options)
