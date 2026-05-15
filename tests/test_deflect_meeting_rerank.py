from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.rerank_weights import DEFAULT_WEIGHTS
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def test_deflect_meeting_prefers_async_template():
    profile = CommunicationProfile(
        relation=RelationRole.MANAGER,
        user_leverage_notes="手头线上故障在处理",
        extra_context_notes="会议可改异步",
    )
    out = suggest_deflect(
        "马上来会议室对齐",
        profile,
        use_llm=False,
        rerank_weights=dict(DEFAULT_WEIGHTS),
    )
    top = (out.get("reply_options") or [""])[0]
    opts = out.get("reply_options") or []
    assert any("邮件" in o or "异步" in o for o in opts)
    assert "建议" in top
    assert "如果" in top or "时间" in top
