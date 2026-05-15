from pressure_skill.analyzer.features import extract_features_from_transcript
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.advisor.deflect import suggest_deflect


def test_features_basic():
    t = "必须今天完成\n麻烦尽快给我\n？"
    f = extract_features_from_transcript(t)
    assert f["message_count"] >= 1
    assert "imperative_intensity" in f


def test_deflect_fallback():
    p = CommunicationProfile(relation=RelationRole.MANAGER)
    r = suggest_deflect("老板催我今天交报告", p, use_llm=False)
    assert "reply_options" in r
    assert isinstance(r["reply_options"], list)
