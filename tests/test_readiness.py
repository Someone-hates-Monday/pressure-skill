from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.analyzer.readiness import assess_readiness


def test_readiness_thin():
    p = CommunicationProfile(relation=RelationRole.UNKNOWN)
    r = assess_readiness(
        p,
        transcript_raw="",
        has_situation=True,
        has_goal=False,
        has_vague=False,
        has_clap_back=False,
        user_purpose=None,
    )
    assert r["level"] == "thin"
    assert "warnings" in r
    assert r["portrait_depth"] == "minimal"
    assert "evidence_score" in r
    assert "portrait_depth_hint" in r
    joined = "".join(r["missing_fields"])
    assert "relation" in joined or "目的" in joined


def test_readiness_ok():
    p = CommunicationProfile(
        relation=RelationRole.MANAGER,
        reply_speed_hint="fast",
        features={"message_count": 5},
        user_leverage_notes="掌握关键数据口径",
        counterparty_notes="急躁、爱面子",
        extra_context_notes="季度汇报节点真实压力在中台不在你",
        user_purpose="对齐交付范围",
    )
    r = assess_readiness(
        p,
        transcript_raw="a\n" * 30,
        has_situation=True,
        has_goal=False,
        has_vague=False,
        has_clap_back=False,
        user_purpose="对齐交付范围",
    )
    assert r["level"] in ("ok", "ok_with_gaps")
    assert r["portrait_depth"] in ("minimal", "standard", "deep")
    assert "evidence_score" in r
    assert "portrait_depth_hint" in r


def test_clap_back_fallback():
    from pressure_skill.advisor.clap_back import suggest_clap_back

    p = CommunicationProfile(relation=RelationRole.PEER)
    out = suggest_clap_back("你又不是老板凶什么凶", p, use_llm=False)
    assert "reply_options" in out


def test_readiness_locale_en():
    p = CommunicationProfile(
        relation=RelationRole.UNKNOWN,
        locale="en",
        user_leverage_notes="I control the rollout calendar",
        extra_context_notes="VP cares about optics only",
        user_purpose="De-risk my week",
    )
    r = assess_readiness(
        p,
        transcript_raw="",
        has_situation=True,
        has_goal=False,
        has_vague=False,
        user_purpose="De-risk my week",
    )
    assert r["locale"] == "en"
    assert any("relation" in m.lower() for m in r["missing_fields"])
