#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.advisor.clap_back import suggest_clap_back
from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.push import suggest_push
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.eval_db import load_cases as load_cases_from_db
from pressure_skill.eval_db import save_run as save_run_to_db
from pressure_skill.eval_metrics import score_output_for_case


def _load_cases(path: Path) -> list[dict]:
    rows: list[dict] = []
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("\ufeff"):
        raw = raw.lstrip("\ufeff")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _run_case(
    c: dict,
    *,
    top_k: int,
    must_weight: float,
    nice_weight: float,
) -> dict:
    mode = c["mode"]
    profile = CommunicationProfile.model_validate(c.get("profile") or {})
    text = c["text"]
    if mode == "deflect":
        out = suggest_deflect(text, profile, use_llm=False)
    elif mode == "push":
        out = suggest_push(text, profile, use_llm=False)
    elif mode == "clap_back":
        out = suggest_clap_back(text, profile, use_llm=False)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    options = out.get("reply_options") or []
    top = options[0] if options else ""
    metrics = score_output_for_case(
        out,
        c,
        top_k=top_k,
        must_weight=must_weight,
        nice_weight=nice_weight,
    )
    row: dict = {
        "id": c["id"],
        "mode": mode,
        "top_hit_ratio": metrics["top_hit_ratio"],
        "top_weighted_score": metrics["top_weighted_score"],
        "topk_weighted_score": metrics["topk_weighted_score"],
        "forbidden_hit_top": metrics["forbidden_hit_top"],
        "signal_breakdown": metrics["signal_breakdown"],
        "top_preview": top[:120],
        "strategy_trace": out.get("strategy_trace") or [],
    }
    if metrics.get("rubric_notes"):
        row["rubric_notes"] = metrics["rubric_notes"]
    return row


def main() -> None:
    ap = argparse.ArgumentParser(description="Local heuristic eval for pressure.skill")
    ap.add_argument(
        "--cases",
        default="eval/cases.jsonl",
        help="Path to jsonl eval cases",
    )
    ap.add_argument(
        "--db",
        default="",
        help="Optional SQLite path. If set with --use-db-cases, load cases from DB.",
    )
    ap.add_argument(
        "--use-db-cases",
        action="store_true",
        help="Load eval cases from SQLite db instead of --cases file.",
    )
    ap.add_argument(
        "--save-run",
        action="store_true",
        help="When --db is set, persist this eval run into eval_runs table.",
    )
    ap.add_argument(
        "--top-k",
        type=int,
        default=2,
        help="Average weighted score over first K reply options (default 2).",
    )
    ap.add_argument(
        "--must-weight",
        type=float,
        default=0.7,
        help="Weight for must_have_signals in weighted score (default 0.7).",
    )
    ap.add_argument(
        "--nice-weight",
        type=float,
        default=0.3,
        help="Weight for nice_to_have_signals in weighted score (default 0.3).",
    )
    args = ap.parse_args()

    if args.use_db_cases:
        if not args.db:
            raise SystemExit("--use-db-cases requires --db")
        cases = load_cases_from_db(args.db)
    else:
        cases = _load_cases(Path(args.cases))
    rows = [
        _run_case(
            c,
            top_k=args.top_k,
            must_weight=args.must_weight,
            nice_weight=args.nice_weight,
        )
        for c in cases
    ]
    overall_legacy = round(mean([r["top_hit_ratio"] for r in rows]), 3) if rows else 0.0
    overall_w1 = round(mean([r["top_weighted_score"] for r in rows]), 3) if rows else 0.0
    overall_wk = round(mean([r["topk_weighted_score"] for r in rows]), 3) if rows else 0.0
    forbidden_hits = sum(1 for r in rows if r.get("forbidden_hit_top"))
    result = {
        "cases": rows,
        "summary": {
            "case_count": len(rows),
            "avg_top_hit_ratio": overall_legacy,
            "avg_top_weighted_score": overall_w1,
            "avg_topk_weighted_score": overall_wk,
            "forbidden_hit_case_count": forbidden_hits,
            "eval_top_k": max(1, int(args.top_k)),
            "must_weight": args.must_weight,
            "nice_weight": args.nice_weight,
        },
    }
    if args.save_run:
        if not args.db:
            raise SystemExit("--save-run requires --db")
        run_id = save_run_to_db(args.db, result)
        result["summary"]["saved_run_id"] = run_id

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
