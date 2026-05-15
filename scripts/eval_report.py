#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.advisor.clap_back import suggest_clap_back
from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.push import suggest_push
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.eval_metrics import score_output_for_case


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _advise(c: dict, *, top_k: int, must_weight: float, nice_weight: float) -> dict:
    p = CommunicationProfile.model_validate(c.get("profile") or {})
    t = c["text"]
    m = c["mode"]
    if m == "deflect":
        out = suggest_deflect(t, p, use_llm=False)
    elif m == "push":
        out = suggest_push(t, p, use_llm=False)
    elif m == "clap_back":
        out = suggest_clap_back(t, p, use_llm=False)
    else:
        raise ValueError(m)
    metrics = score_output_for_case(out, c, top_k=top_k, must_weight=must_weight, nice_weight=nice_weight)
    opts = out.get("reply_options") or []
    top = opts[0] if opts else ""
    return {
        "id": c["id"],
        "mode": m,
        "top_hit_ratio": metrics["top_hit_ratio"],
        "top_weighted_score": metrics["top_weighted_score"],
        "topk_weighted_score": metrics["topk_weighted_score"],
        "forbidden_hit_top": metrics["forbidden_hit_top"],
        "top": top[:160],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="List low-scoring eval cases")
    ap.add_argument("--cases", default="eval/cases.jsonl")
    ap.add_argument("--threshold", type=float, default=0.35)
    ap.add_argument(
        "--metric",
        choices=("legacy", "weighted", "topk"),
        default="weighted",
        help="Which score to compare against --threshold (default weighted top-1).",
    )
    ap.add_argument("--top-k", type=int, default=2, dest="top_k")
    ap.add_argument("--must-weight", type=float, default=0.7, dest="must_weight")
    ap.add_argument("--nice-weight", type=float, default=0.3, dest="nice_weight")
    args = ap.parse_args()
    cases = _load_jsonl(Path(args.cases))
    rows = [
        _advise(
            c,
            top_k=args.top_k,
            must_weight=args.must_weight,
            nice_weight=args.nice_weight,
        )
        for c in cases
    ]
    key = {"legacy": "top_hit_ratio", "weighted": "top_weighted_score", "topk": "topk_weighted_score"}[
        args.metric
    ]
    bad = [r for r in rows if r[key] < args.threshold]
    print(
        json.dumps(
            {
                "threshold": args.threshold,
                "metric": args.metric,
                "score_field": key,
                "failures": bad,
                "failure_count": len(bad),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
