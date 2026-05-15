#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.eval_db import add_feedback


def main() -> None:
    ap = argparse.ArgumentParser(description="Add user feedback to eval SQLite")
    ap.add_argument("--db", default="eval/eval_runs.db")
    ap.add_argument("--accepted", required=True, choices=["yes", "no"])
    ap.add_argument("--case-id", default="")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--usefulness", type=int, default=None, help="1-5")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    if args.usefulness is not None and not (1 <= args.usefulness <= 5):
        raise SystemExit("--usefulness must be 1..5")

    add_feedback(
        args.db,
        case_id=args.case_id or None,
        run_id=args.run_id or None,
        accepted=args.accepted == "yes",
        usefulness=args.usefulness,
        note=args.note or None,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "db": args.db,
                "accepted": args.accepted,
                "case_id": args.case_id or None,
                "run_id": args.run_id or None,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
