from pressure_skill.advisor.clap_back import suggest_clap_back
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def test_fallback_clap_formal_has_diverse_pool():
    profile = CommunicationProfile(
        relation=RelationRole.MANAGER,
        counterparty_notes="压力下口不择言",
    )
    out = suggest_clap_back("你到底行不行？别耽误我", profile, use_llm=False)
    options = out.get("reply_options") or []
    assert len(options) >= 5
    top = options[0]
    assert "不能接受" in top or "验收" in top
    assert "推进" in top or "标准" in top


def test_fallback_clap_client_service_complaint():
    profile = CommunicationProfile(
        relation=RelationRole.CLIENT,
        counterparty_notes="情绪化投诉",
    )
    out = suggest_clap_back("你们服务太差了，别找借口", profile, use_llm=False)
    top = (out.get("reply_options") or [""])[0]
    assert "不能接受" in top or "请" in top
    assert "标准" in top or "对齐" in top or "推进" in top


def test_fallback_clap_peer_pool():
    profile = CommunicationProfile(relation=RelationRole.PEER)
    out = suggest_clap_back("你又不是老板，别在群里催命", profile, use_llm=False)
    options = out.get("reply_options") or []
    assert len(options) >= 4
    assert any("协作" in x or "说清楚" in x for x in options)
