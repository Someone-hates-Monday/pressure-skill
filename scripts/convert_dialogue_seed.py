#!/usr/bin/env python3
"""Convert raw dialogue rows into pressure.skill eval case drafts (needs human review)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _guess_mode(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("不能接受", "别这样", "口气", "甩锅", "阴阳", "can't accept", "tone")):
        return "clap_back"
    if any(k in t for k in ("能否", "麻烦", "请", "催", "确认", "预计", "could you", "eta")):
        return "push"
    return "deflect"


def _heuristic_signals(text: str, mode: str) -> list[str]:
    pool = ["建议", "先", "后", "风险", "范围", "验收", "今天", "明天", "麻烦", "请", "推进", "对齐"]
    if mode == "clap_back":
        pool = ["请", "协作", "说清楚", "推进", "标准", "不能接受", "对齐", "一次性"]
    elif mode == "push":
        pool = ["今天", "明天", "麻烦", "预计", "如果", "先", "确认", "截止"]
    hits = [w for w in pool if w in text]
    return hits[:6] if hits else pool[:4]


def _normalize_row(row: dict[str, Any], i: int, source: str) -> dict[str, Any] | None:
    text = (
        row.get("text")
        or row.get("utterance")
        or row.get("content")
        or row.get("sentence")
        or ""
    ).strip()
    if not text or len(text) < 4:
        return None
    mode = row.get("mode") or _guess_mode(text)
    profile = row.get("profile") if isinstance(row.get("profile"), dict) else {}
    if not profile.get("relation"):
        profile["relation"] = "peer"
    rid = (row.get("id") or "").strip() or f"{source}_{i:05d}"
    rid = re.sub(r"[^\w\-]+", "_", rid)
    return {
        "id": rid,
        "mode": mode,
        "text": text[:500],
        "profile": profile,
        "target_signals": row.get("target_signals") or _heuristic_signals(text, mode),
        "annotation_meta": {
            "source": source,
            "tier": "draft_auto",
            "needs_review": True,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert external dialogue jsonl to eval case drafts")
    ap.add_argument("--input", required=True, help="Input jsonl with text/utterance field per line")
    ap.add_argument("--out", required=True, help="Output jsonl path")
    ap.add_argument("--source", default="external_dialogue", help="Source label in annotation_meta")
    ap.add_argument("--limit", type=int, default=0, help="Max rows (0 = all)")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Input not found: {inp}")

    out_rows: list[dict[str, Any]] = []
    for i, line in enumerate(inp.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        norm = _normalize_row(row, i, args.source)
        if norm:
            out_rows.append(norm)
        if args.limit and len(out_rows) >= args.limit:
            break

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in out_rows) + ("\n" if out_rows else ""),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "written": str(out_path),
                "count": len(out_rows),
                "note": "Draft cases need human review before training merge",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
