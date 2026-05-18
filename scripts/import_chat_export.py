#!/usr/bin/env python3
"""Parse offline chat export and optionally merge into a counterparty profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.analyzer.features import extract_features_from_transcript
from pressure_skill.analyzer.patterns import infer_pattern_tags
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.counterparty_store import load_counterparty, save_counterparty
from pressure_skill.ingest.chat_import import parse_chat_export
from pressure_skill.settings import counterparty_base_dir


def main() -> None:
    ap = argparse.ArgumentParser(description="Import WeChat/Feishu/generic chat export (offline)")
    ap.add_argument("--file", required=True, help="UTF-8 export file")
    ap.add_argument("--format", default="auto", choices=["auto", "wechat_txt", "feishu_json", "generic_lines"])
    ap.add_argument("--slug", default="", help="Merge into existing counterparty")
    ap.add_argument("--base-dir", default="", help="Override PRESSURE_DATA_DIR")
    ap.add_argument("--stdout-only", action="store_true", help="Print transcript only, do not save")
    args = ap.parse_args()

    content = Path(args.file).read_text(encoding="utf-8")
    parsed = parse_chat_export(content, fmt=args.format)
    transcript = parsed.get("transcript") or ""

    if args.stdout_only or not args.slug:
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
        if not args.slug:
            print("\n# Tip: --slug <id> to merge into counterparties/", file=sys.stderr)
        return

    base = Path(args.base_dir) if args.base_dir else counterparty_base_dir()
    data = load_counterparty(base, args.slug)
    profile: CommunicationProfile = data["profile"]
    feats = extract_features_from_transcript(transcript)
    tags = infer_pattern_tags(feats)
    note = f"[import {parsed.get('format_detected')}] excerpt:\n{transcript[:1200]}"
    cn = profile.counterparty_notes or ""
    if transcript[:80] not in cn:
        cn = f"{cn}\n\n{note}".strip() if cn else note
    profile = profile.model_copy(
        update={
            "features": {**(profile.features or {}), **feats},
            "pattern_tags": list({*(profile.pattern_tags or []), *tags}),
            "counterparty_notes": cn,
        }
    )
    save_counterparty(base, args.slug, profile, merge=True)
    print(json.dumps({"ok": True, "slug": args.slug, "parsed": parsed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
