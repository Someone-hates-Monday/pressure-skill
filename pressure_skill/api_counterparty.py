"""FastAPI routes for local counterparty persistence (PRESSURE_DATA_DIR)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from pressure_skill.analyzer.features import extract_features_from_transcript
from pressure_skill.analyzer.patterns import infer_pattern_tags
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.counterparty_feedback import record_outcome_feedback
from pressure_skill.counterparty_store import (
    load_counterparty,
    save_counterparty,
    slugify,
    list_counterparties,
)
from pressure_skill.ingest.chat_import import parse_chat_export
from pressure_skill.settings import counterparty_base_dir

router = APIRouter(prefix="/api/v1/counterparties", tags=["counterparties"])


class CounterpartySaveBody(BaseModel):
    profile: CommunicationProfile
    display_name: str | None = None
    merge: bool = True


class OutcomeFeedbackBody(BaseModel):
    feedback: dict[str, Any]


class ChatIngestBody(BaseModel):
    content: str = Field(..., min_length=1)
    format: str = Field(default="auto", description="auto | wechat_txt | feishu_json | generic_lines")
    merge_into_profile: bool = True


class CreateCounterpartyBody(BaseModel):
    display_name: str = Field(..., min_length=1)
    profile: CommunicationProfile | None = None


@router.get("")
def api_list_counterparties() -> dict[str, Any]:
    base = counterparty_base_dir()
    return {"base_dir": str(base), "items": list_counterparties(base)}


@router.get("/{slug}")
def api_get_counterparty(slug: str) -> dict[str, Any]:
    try:
        data = load_counterparty(counterparty_base_dir(), slug)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    return {
        "slug": data["slug"],
        "meta": data["meta"],
        "profile": data["profile_dict"],
        "episodes": data["episodes"][-20:],
        "outcomes": (data.get("outcomes") or [])[-10:],
        "corrections": data["corrections"],
    }


@router.put("/{slug}")
def api_put_counterparty(slug: str, body: CounterpartySaveBody) -> dict[str, Any]:
    result = save_counterparty(
        counterparty_base_dir(),
        slug,
        body.profile,
        display_name=body.display_name,
        merge=body.merge,
    )
    return {"ok": True, **result}


@router.post("/{slug}/feedback")
def api_post_feedback(slug: str, body: OutcomeFeedbackBody) -> dict[str, Any]:
    try:
        return record_outcome_feedback(
            counterparty_base_dir(),
            slug,
            body.feedback,
            apply_profile=True,
        )
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/{slug}/ingest-chat")
def api_ingest_chat(slug: str, body: ChatIngestBody) -> dict[str, Any]:
    try:
        data = load_counterparty(counterparty_base_dir(), slug)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e

    parsed = parse_chat_export(body.content, fmt=body.format)
    transcript = parsed.get("transcript") or ""
    if not transcript.strip():
        raise HTTPException(
            400,
            detail={"message": "no messages parsed", "warnings": parsed.get("warnings") or []},
        )

    profile = data["profile"]
    if body.merge_into_profile:
        feats = extract_features_from_transcript(transcript)
        tags = infer_pattern_tags(feats)
        merged_feats = {**(profile.features or {}), **feats}
        merged_tags = list({*(profile.pattern_tags or []), *tags})
        note_chunk = f"[导入聊天 {parsed.get('format_detected')}] {transcript[:400]}…" if len(transcript) > 400 else f"[导入聊天] {transcript}"
        cn = profile.counterparty_notes or ""
        if transcript[:80] not in cn:
            cn = f"{cn}\n\n{note_chunk}".strip() if cn else note_chunk
        profile = profile.model_copy(
            update={
                "features": merged_feats,
                "pattern_tags": merged_tags,
                "counterparty_notes": cn,
            }
        )
        save_counterparty(counterparty_base_dir(), slug, profile, merge=True)

    return {
        "ok": True,
        "slug": slug,
        "parsed": parsed,
        "profile_updated": body.merge_into_profile,
    }


@router.post("")
def api_create_counterparty(body: CreateCounterpartyBody) -> dict[str, Any]:
    slug = slugify(body.display_name)
    prof = body.profile or CommunicationProfile()
    result = save_counterparty(
        counterparty_base_dir(),
        slug,
        prof,
        display_name=body.display_name,
        merge=False,
    )
    return {"ok": True, "slug": slug, **result}
