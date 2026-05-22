#!/usr/bin/env python3
"""Regenerate examples/sample-bundle-*.json (includes reaction_hints). Run from repo root."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.advisor.deflect import suggest_deflect


def _trim_deflect(payload: dict, *, max_options: int = 3) -> dict:
    """Keep demo JSON small: top-N replies + reaction_hints, drop strategy_trace."""
    out = dict(payload)
    opts = out.get("reply_options") or []
    if isinstance(opts, list):
        out["reply_options"] = [o for o in opts if isinstance(o, str)][:max_options]
    hints = out.get("reaction_hints") or []
    if isinstance(hints, list):
        out["reaction_hints"] = hints[: len(out["reply_options"])]
    out.pop("strategy_trace", None)
    return out

from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.analyzer.readiness import assess_readiness


def _bundle_like(
    *,
    relation: RelationRole,
    purpose: str,
    situation: str,
    counterparty_notes: str | None = None,
    user_leverage: str | None = None,
    extra_context: str | None = None,
) -> dict:
    profile = CommunicationProfile(
        relation=relation,
        counterparty_notes=counterparty_notes,
        user_leverage_notes=user_leverage,
        extra_context_notes=extra_context,
        user_purpose=purpose,
        locale="zh",
    )
    deflect = _trim_deflect(suggest_deflect(situation, profile, use_llm=False))
    readiness = assess_readiness(
        profile,
        transcript_raw="",
        scene_text_blob=situation,
        has_situation=True,
        has_goal=False,
        has_vague=False,
        user_purpose=purpose,
    )
    return {
        "profile": profile.model_dump(mode="json"),
        "readiness": readiness,
        "deflect": deflect,
    }


def main() -> None:
    out_dir = ROOT / "examples"
    full = _bundle_like(
        relation=RelationRole.MANAGER,
        purpose="争取延期",
        situation="今天下班前必须交完整版",
        counterparty_notes="节奏快、讨厌模糊承诺",
        user_leverage="手头另有更高优先级项目已排满本周",
        extra_context="领导更在意可预期的交付节奏而非单次通宵",
    )
    thin = _bundle_like(
        relation=RelationRole.MANAGER,
        purpose="争取延期",
        situation="今天下班前必须交完整版",
    )
    (out_dir / "sample-bundle-with-leverage.json").write_text(
        json.dumps(full, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "sample-bundle-thin-profile.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "written": [str(out_dir / n) for n in (
        "sample-bundle-with-leverage.json",
        "sample-bundle-thin-profile.json",
    )]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
