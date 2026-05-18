from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from pressure_skill.analyzer.features import extract_features_from_transcript
from pressure_skill.analyzer.patterns import infer_pattern_tags
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.analyzer.readiness import assess_readiness
from pressure_skill.advisor.clap_back import suggest_clap_back
from pressure_skill.advisor.clarify import suggest_clarify
from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.push import suggest_push
from pressure_skill.api_counterparty import router as counterparty_router

load_dotenv()

app = FastAPI(title="pressure.skill", version="0.1.0")
app.include_router(counterparty_router)


class ManualProfilePatch(BaseModel):
    relation: RelationRole | None = None
    scene_tags: list[str] | None = None
    reply_speed_hint: str | None = None
    prefers: dict[str, float] | None = None
    pain_points: list[str] | None = None
    praise_vs_critique_notes: str | None = None
    counterparty_notes: str | None = None
    user_leverage_notes: str | None = None
    extra_context_notes: str | None = None
    user_purpose: str | None = None
    locale: str | None = None
    discipline_subfield: str | None = None
    artefact_preferences_notes: str | None = None
    counterparty_seniority: str | None = None


class ProfileFromTextRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    manual: ManualProfilePatch | None = None


class AdviceRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Situation, goal, or vague request")
    profile: CommunicationProfile
    use_llm: bool | None = Field(
        default=None,
        description="True forces LLM; False forces template; null = auto from env",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/profile/from-text")
def profile_from_text(body: ProfileFromTextRequest) -> CommunicationProfile:
    feats = extract_features_from_transcript(body.transcript)
    tags = infer_pattern_tags(feats)
    base = CommunicationProfile(features=feats, pattern_tags=tags)
    if body.manual:
        return base.merge_manual(body.manual.model_dump(exclude_none=True))
    return base


@app.post("/api/v1/advice/deflect")
def api_deflect(body: AdviceRequest) -> dict[str, Any]:
    return suggest_deflect(body.text, body.profile, use_llm=body.use_llm)


@app.post("/api/v1/advice/push")
def api_push(body: AdviceRequest) -> dict[str, Any]:
    return suggest_push(body.text, body.profile, use_llm=body.use_llm)


@app.post("/api/v1/advice/clarify")
def api_clarify(body: AdviceRequest) -> dict[str, Any]:
    return suggest_clarify(body.text, body.profile, use_llm=body.use_llm)


class BundleRequest(BaseModel):
    situation_pressure_on_you: str | None = None
    your_goal_to_push_others: str | None = None
    vague_request_from_other: str | None = None
    clap_back_provocation: str | None = Field(
        default=None,
        description="When user wants sharp pushback / vent, low-threat counterparty",
    )
    profile: CommunicationProfile
    use_llm: bool | None = None
    transcript_snippet: str | None = Field(
        default=None,
        description="Optional raw chat for readiness heuristics only",
    )


@app.post("/api/v1/advice/clap-back")
def api_clap_back(body: AdviceRequest) -> dict[str, Any]:
    return suggest_clap_back(body.text, body.profile, use_llm=body.use_llm)


@app.post("/api/v1/advice/bundle")
def api_bundle(body: BundleRequest) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if body.situation_pressure_on_you:
        out["deflect"] = suggest_deflect(
            body.situation_pressure_on_you,
            body.profile,
            use_llm=body.use_llm,
        )
    if body.your_goal_to_push_others:
        out["push"] = suggest_push(
            body.your_goal_to_push_others,
            body.profile,
            use_llm=body.use_llm,
        )
    if body.vague_request_from_other:
        out["clarify"] = suggest_clarify(
            body.vague_request_from_other,
            body.profile,
            use_llm=body.use_llm,
        )
    if body.clap_back_provocation:
        out["clap_back"] = suggest_clap_back(
            body.clap_back_provocation,
            body.profile,
            use_llm=body.use_llm,
        )
    raw = body.transcript_snippet or ""
    scene_blob = " ".join(
        p.strip()
        for p in (
            body.situation_pressure_on_you,
            body.your_goal_to_push_others,
            body.vague_request_from_other,
            body.clap_back_provocation,
        )
        if p and p.strip()
    )
    out["readiness"] = assess_readiness(
        body.profile,
        transcript_raw=raw,
        scene_text_blob=scene_blob,
        has_situation=bool(body.situation_pressure_on_you),
        has_goal=bool(body.your_goal_to_push_others),
        has_vague=bool(body.vague_request_from_other),
        has_clap_back=bool(body.clap_back_provocation),
        user_purpose=body.profile.user_purpose,
    )
    return out
