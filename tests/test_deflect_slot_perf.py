"""Guardrails: slot extraction must stay linear-time on long profile notes."""
import time

from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.rerank_weights import DEFAULT_WEIGHTS
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole


def test_deflect_en_completes_quickly_with_huge_profile_notes():
    filler = "a" * 80000
    profile = CommunicationProfile(
        relation=RelationRole.PEER,
        extra_context_notes=filler + " compliance review required before ship",
    )
    t0 = time.perf_counter()
    suggest_deflect("We should align on scope before Friday.", profile, use_llm=False, rerank_weights=dict(DEFAULT_WEIGHTS))
    assert time.perf_counter() - t0 < 2.0
