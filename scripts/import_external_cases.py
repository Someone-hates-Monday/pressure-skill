#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.eval_db import upsert_cases


def _ensure_case_id(i: int, row: dict[str, Any], prefix: str) -> str:
    rid = (row.get("id") or "").strip()
    return rid or f"{prefix}_{i:04d}"


def _normalize_mode(raw: str) -> str:
    m = (raw or "").strip().lower()
    alias = {
        "defer": "deflect",
        "deflect": "deflect",
        "push": "push",
        "nudge": "push",
        "clap": "clap_back",
        "clap_back": "clap_back",
        "clap-back": "clap_back",
    }
    if m not in alias:
        raise ValueError(f"Unsupported mode: {raw}")
    return alias[m]


def _load_jsonl(path: Path, *, prefix: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        entry: dict[str, Any] = {
            "id": _ensure_case_id(i, row, prefix),
            "mode": _normalize_mode(row.get("mode", "")),
            "text": row.get("text", ""),
            "profile": row.get("profile") or {},
            "target_signals": row.get("target_signals") or [],
        }
        for k in ("must_have_signals", "nice_to_have_signals", "forbidden_substrings", "rubric_notes"):
            if k in row:
                entry[k] = row[k]
        out.append(entry)
    return out


def _load_csv(path: Path, *, prefix: str) -> list[dict[str, Any]]:
    """
    Expected columns:
    - id (optional)
    - mode (required): deflect/push/clap_back
    - text (required)
    - profile_json (optional): JSON object string
    - target_signals_csv (optional): comma-separated
    """
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            profile_json = row.get("profile_json") or "{}"
            signals_csv = row.get("target_signals_csv") or ""
            profile = json.loads(profile_json)
            signals = [x.strip() for x in signals_csv.split(",") if x.strip()]
            out.append(
                {
                    "id": _ensure_case_id(i, row, prefix),
                    "mode": _normalize_mode(row.get("mode", "")),
                    "text": (row.get("text") or "").strip(),
                    "profile": profile,
                    "target_signals": signals,
                }
            )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Import external eval cases into SQLite")
    ap.add_argument("--input", required=True, help="Path to external jsonl/csv")
    ap.add_argument("--db", default="eval/eval_runs.db", help="SQLite db path")
    ap.add_argument("--source", default="external", help="Source label, e.g. convokit")
    ap.add_argument("--id-prefix", default="ext", help="Auto case id prefix")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        raise SystemExit(f"Input not found: {path}")

    if path.suffix.lower() == ".jsonl":
        cases = _load_jsonl(path, prefix=args.id_prefix)
    elif path.suffix.lower() == ".csv":
        cases = _load_csv(path, prefix=args.id_prefix)
    else:
        raise SystemExit("Only .jsonl or .csv supported")

    n = upsert_cases(args.db, cases, source=args.source)
    print(json.dumps({"imported": n, "db": args.db, "source": args.source}, ensure_ascii=False))


if __name__ == "__main__":
    main()
