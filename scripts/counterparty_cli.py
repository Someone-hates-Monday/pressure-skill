#!/usr/bin/env python3
"""CLI for long-term counterparty portraits (local counterparties/ directory)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.counterparty_store import (
    append_correction,
    append_episode,
    list_counterparties,
    load_counterparty,
    save_counterparty,
    slugify,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Manage long-term counterparty profiles")
    ap.add_argument("--base-dir", default="counterparties", help="Root dir (default: ./counterparties)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List saved counterparties")

    p_show = sub.add_parser("show", help="Load one counterparty as JSON")
    p_show.add_argument("--slug", required=True)

    p_save = sub.add_parser("save", help="Create or merge profile.json")
    p_save.add_argument("--slug", default="", help="Directory name; derived from --name if empty")
    p_save.add_argument("--name", default="", help="Display name / alias for slugify")
    p_save.add_argument("--profile-file", required=True, help="JSON file: CommunicationProfile fields")
    p_save.add_argument("--no-merge", action="store_true", help="Replace profile instead of merging")

    p_ep = sub.add_parser("episode", help="Append a session episode")
    p_ep.add_argument("--slug", required=True)
    p_ep.add_argument("--purpose", default="")
    p_ep.add_argument("--scenes", default="", help="Comma-separated: deflect,push,clarify,clap")
    p_ep.add_argument("--summary", default="", help="Short situation summary")
    p_ep.add_argument("--outcome", default="", help="e.g. sent, deferred, escalated")
    p_ep.add_argument("--usefulness", type=int, default=None, help="1-5")
    p_ep.add_argument("--note", default="")

    p_corr = sub.add_parser("correction", help="Append a correction line")
    p_corr.add_argument("--slug", required=True)
    p_corr.add_argument("--text", required=True)
    p_corr.add_argument(
        "--category",
        default="portrait",
        choices=["portrait", "leverage", "context", "pattern", "other"],
    )

    args = ap.parse_args()

    if args.cmd == "list":
        items = list_counterparties(args.base_dir)
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return

    if args.cmd == "show":
        data = load_counterparty(args.base_dir, args.slug)
        out = {
            "slug": data["slug"],
            "meta": data["meta"],
            "profile": data["profile_dict"],
            "episodes": data["episodes"][-10:],
            "corrections_preview": (data["corrections"] or "")[:2000],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    if args.cmd == "save":
        slug = args.slug or slugify(args.name)
        if not slug:
            raise SystemExit("need --slug or --name")
        raw = json.loads(Path(args.profile_file).read_text(encoding="utf-8"))
        profile = CommunicationProfile.model_validate(raw)
        display = args.name or args.slug or slug
        result = save_counterparty(
            args.base_dir,
            slug,
            profile,
            display_name=display,
            merge=not args.no_merge,
        )
        print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
        return

    if args.cmd == "episode":
        ep: dict = {}
        if args.purpose:
            ep["user_purpose"] = args.purpose
        if args.scenes:
            ep["scene_modes"] = [s.strip() for s in args.scenes.split(",") if s.strip()]
        if args.summary:
            ep["situation_summary"] = args.summary
        if args.outcome:
            ep["outcome"] = args.outcome
        if args.usefulness is not None:
            ep["usefulness"] = args.usefulness
        if args.note:
            ep["note"] = args.note
        append_episode(args.base_dir, args.slug, ep)
        print(json.dumps({"ok": True, "slug": args.slug, "episode": ep}, ensure_ascii=False))
        return

    if args.cmd == "correction":
        append_correction(args.base_dir, args.slug, args.text, category=args.category)
        print(json.dumps({"ok": True, "slug": args.slug}, ensure_ascii=False))
        return


if __name__ == "__main__":
    main()
