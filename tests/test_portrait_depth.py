from pressure_skill.analyzer.portrait_depth import infer_portrait_depth
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def test_infer_portrait_depth_minimal():
    p = CommunicationProfile(relation=RelationRole.UNKNOWN)
    depth, score = infer_portrait_depth(p, transcript_raw="", extra_scene_text="")
    assert depth == "minimal"
    assert 0 <= score < 38


def test_infer_portrait_depth_deep_rich_material():
    p = CommunicationProfile(
        relation=RelationRole.MANAGER,
        counterparty_notes="x" * 120,
        user_leverage_notes="y" * 50,
        extra_context_notes="z" * 50,
        features={"message_count": 10},
    )
    transcript = "w\n" * 250
    scene = "situation " * 80
    depth, score = infer_portrait_depth(
        p,
        transcript_raw=transcript,
        extra_scene_text=scene,
    )
    assert depth == "deep"
    assert score >= 72
