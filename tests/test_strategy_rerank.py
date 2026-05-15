from pressure_skill.advisor.strategy_rerank import rerank_reply_options
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def test_rerank_prefers_time_and_tradeoff_for_deflect():
    payload = {
        "reply_options": [
            "我会尽量处理。",
            "建议先交核心结论，周五给框架，下周一补齐细节。",
        ]
    }
    p = CommunicationProfile(
        relation=RelationRole.MANAGER,
        user_leverage_notes="本周还有高优先级任务",
        extra_context_notes="领导更在意可预期节奏",
    )
    out = rerank_reply_options(payload, profile=p, mode="deflect", scene_text="今天下班前交完整版")
    assert out["reply_options"][0].startswith("建议先交核心结论")
    assert "strategy_trace" in out
    assert out["strategy_trace"][0]["score"] >= out["strategy_trace"][-1]["score"]
