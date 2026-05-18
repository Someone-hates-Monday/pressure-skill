#!/usr/bin/env python3
"""
Local one-shot: build profile from transcript + print bundle advice (no HTTP).
Run from repo root: py -3 scripts/bundle_local.py --help
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.advisor.clap_back import suggest_clap_back
from pressure_skill.advisor.clarify import suggest_clarify
from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.push import suggest_push
from pressure_skill.analyzer.features import extract_features_from_transcript
from pressure_skill.analyzer.patterns import infer_pattern_tags
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.analyzer.readiness import assess_readiness
from pressure_skill.i18n import merge_locale


def _read_text(path: str | None, inline: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return inline or ""


def _parse_use_llm(s: str) -> bool | None:
    if s == "auto":
        return None
    if s in ("1", "true", "yes"):
        return True
    if s in ("0", "false", "no"):
        return False
    raise SystemExit(f"Invalid --use-llm: {s}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="pressure.skill local bundle (Cursor-friendly)")
    ap.add_argument("--transcript", default="", help="Inline transcript snippet")
    ap.add_argument("--transcript-file", default="", help="UTF-8 file path for transcript")
    ap.add_argument(
        "--relation",
        default="unknown",
        choices=[e.value for e in RelationRole],
        help="Counterparty vs you",
    )
    ap.add_argument("--scene-tags", default="", help="Comma-separated tags, e.g. internet_cn,academia")
    ap.add_argument("--reply-speed-hint", default="", help="e.g. fast / slow / irregular")
    ap.add_argument("--praise-vs-critique-notes", default="", help="Contrast notes for implicit standards")
    ap.add_argument(
        "--discipline-subfield",
        default="",
        help="e.g. cs_theory, cs_ml, cs_systems — disambiguates 'write clearly'",
    )
    ap.add_argument(
        "--artefact-preferences",
        default="",
        help="What they reward: formulas, code, diagrams, tables, prose",
    )
    ap.add_argument(
        "--counterparty-seniority",
        default="",
        help="Optional: senior_faculty, junior_faculty, industry_mentor, …",
    )
    ap.add_argument("--counterparty-notes", default="", help="Portrait of the other person (free text)")
    ap.add_argument("--user-leverage", default="", help="Your chips / leverage (deadlines, options, etc.)")
    ap.add_argument("--extra-context", default="", help="Org power, abilities, stakes, off-channel facts")
    ap.add_argument("--user-purpose", default="", help="What you want this round (required by wizard)")
    ap.add_argument(
        "--situation",
        default="",
        help="对方施压情境（推脱/减量/延期）",
    )
    ap.add_argument("--goal", default="", help="You want to push someone to do something")
    ap.add_argument("--vague", default="", help="Their vague ask to translate/clarify")
    ap.add_argument(
        "--clap",
        default="",
        help="对方烦人/可回怼的低威胁表述（出口气/立边界）",
    )
    ap.add_argument(
        "--use-llm",
        default="auto",
        help="auto | true | false (false uses templates, no API key needed)",
    )
    ap.add_argument(
        "--locale",
        default="auto",
        choices=["auto", "zh", "en"],
        help="Output language: auto infers from text; zh/en forces",
    )
    ap.add_argument(
        "--write-advice-snapshot",
        default="",
        help="Write advice_snapshot JSON for later feedback loop (e.g. tmp/advice_snapshot.json)",
    )
    args = ap.parse_args()

    transcript = _read_text(args.transcript_file or None, args.transcript)
    scene_tags = [t.strip() for t in args.scene_tags.split(",") if t.strip()]
    use_llm = _parse_use_llm(args.use_llm)

    if transcript.strip():
        feats = extract_features_from_transcript(transcript)
        tags = infer_pattern_tags(feats)
        profile = CommunicationProfile(
            relation=RelationRole(args.relation),
            scene_tags=scene_tags or [],
            reply_speed_hint=args.reply_speed_hint or None,
            praise_vs_critique_notes=args.praise_vs_critique_notes or None,
            features=feats,
            pattern_tags=tags,
        )
    else:
        profile = CommunicationProfile(
            relation=RelationRole(args.relation),
            scene_tags=scene_tags or [],
            reply_speed_hint=args.reply_speed_hint or None,
            praise_vs_critique_notes=args.praise_vs_critique_notes or None,
        )

    extra: dict = {}
    if args.counterparty_notes.strip():
        extra["counterparty_notes"] = args.counterparty_notes.strip()
    if args.user_leverage.strip():
        extra["user_leverage_notes"] = args.user_leverage.strip()
    if args.extra_context.strip():
        extra["extra_context_notes"] = args.extra_context.strip()
    if args.user_purpose.strip():
        extra["user_purpose"] = args.user_purpose.strip()
    if args.discipline_subfield.strip():
        extra["discipline_subfield"] = args.discipline_subfield.strip()
    if args.artefact_preferences.strip():
        extra["artefact_preferences_notes"] = args.artefact_preferences.strip()
    if args.counterparty_seniority.strip():
        extra["counterparty_seniority"] = args.counterparty_seniority.strip()
    if args.locale == "auto":
        loc = merge_locale(
            transcript,
            args.user_purpose,
            args.situation,
            args.goal,
            args.vague,
            args.clap,
            args.counterparty_notes,
            args.user_leverage,
            args.extra_context,
            args.discipline_subfield,
            args.artefact_preferences,
            args.counterparty_seniority,
        )
    else:
        loc = args.locale
    extra["locale"] = loc
    profile = profile.model_copy(update=extra)

    if not (
        args.situation.strip()
        or args.goal.strip()
        or args.vague.strip()
        or args.clap.strip()
    ):
        ap.error("Provide at least one of --situation / --goal / --vague / --clap")

    scene_blob = " ".join(
        s.strip()
        for s in (args.situation, args.goal, args.vague, args.clap)
        if (s or "").strip()
    )
    out: dict = {
        "profile": profile.model_dump(mode="json"),
        "readiness": assess_readiness(
            profile,
            transcript_raw=transcript,
            scene_text_blob=scene_blob,
            has_situation=bool(args.situation.strip()),
            has_goal=bool(args.goal.strip()),
            has_vague=bool(args.vague.strip()),
            has_clap_back=bool(args.clap.strip()),
            user_purpose=args.user_purpose.strip() or None,
        ),
    }
    if args.situation.strip():
        out["deflect"] = suggest_deflect(args.situation.strip(), profile, use_llm=use_llm)
    if args.goal.strip():
        out["push"] = suggest_push(args.goal.strip(), profile, use_llm=use_llm)
    if args.vague.strip():
        out["clarify"] = suggest_clarify(args.vague.strip(), profile, use_llm=use_llm)
    if args.clap.strip():
        out["clap_back"] = suggest_clap_back(args.clap.strip(), profile, use_llm=use_llm)

    if args.write_advice_snapshot.strip():
        snap: dict = {"user_purpose": args.user_purpose.strip() or None, "predicted_reactions": []}
        opts: list[dict] = []
        for mode, key in (
            ("deflect", "deflect"),
            ("push", "push"),
            ("clarify", "clarify"),
            ("clap_back", "clap_back"),
        ):
            block = out.get(key)
            if not isinstance(block, dict):
                continue
            for i, text in enumerate(block.get("reply_options") or []):
                if not isinstance(text, str):
                    continue
                hints = block.get("reaction_hints") or []
                hint = hints[i] if i < len(hints) and isinstance(hints[i], dict) else {}
                likely = hint.get("likely") or []
                snap["predicted_reactions"].extend(
                    [f"{mode}:{t}" for t in likely if isinstance(t, str)]
                )
                opts.append(
                    {
                        "mode": mode,
                        "index": i,
                        "reply_text": text[:500],
                        "reaction_hint": hint,
                    }
                )
        snap["reply_options_catalog"] = opts
        Path(args.write_advice_snapshot.strip()).write_text(
            json.dumps(snap, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
