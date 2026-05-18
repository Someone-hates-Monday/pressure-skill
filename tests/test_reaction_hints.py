from __future__ import annotations

from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.reaction_hints import attach_reaction_hints
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def test_deflect_includes_reaction_hints():
    p = CommunicationProfile(relation=RelationRole.MANAGER)
    r = suggest_deflect("老板催今天下班前交完整报告", p, use_llm=False)
    assert "reaction_hints" in r
    assert len(r["reaction_hints"]) == len(r["reply_options"])
    h0 = r["reaction_hints"][0]
    assert "likely" in h0 and "one_line" in h0


def test_attach_aligns_count():
    p = CommunicationProfile()
    payload = {"reply_options": ["选项甲", "选项乙"]}
    out = attach_reaction_hints(payload, profile=p, mode="deflect", scene_text="催交付")
    assert len(out["reaction_hints"]) == 2
