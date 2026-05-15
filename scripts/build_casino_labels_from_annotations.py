#!/usr/bin/env python3
"""Write eval/cases_casino_labeled.jsonl from CaSiNo parquet (official dialog-act tags)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.eval_casino_label_map import labels_from_casino_parquet


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate cases_casino_labeled.jsonl from CaSiNo parquet")
    ap.add_argument(
        "--parquet",
        type=Path,
        default=ROOT / "data" / "train-00000-of-00001.parquet",
        help="HF CaSiNo train shard",
    )
    ap.add_argument("--out", type=Path, default=ROOT / "eval" / "cases_casino_labeled.jsonl")
    args = ap.parse_args()
    pq_path = args.parquet if args.parquet.is_absolute() else ROOT / args.parquet
    if not pq_path.is_file():
        raise SystemExit(f"Missing parquet: {pq_path}")
    labels = labels_from_casino_parquet(pq_path)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in labels) + ("\n" if labels else ""),
        encoding="utf-8",
    )
    print(json.dumps({"out": str(args.out), "lines": len(labels)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
