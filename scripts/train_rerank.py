#!/usr/bin/env python3
"""Heuristic search over rerank_weights to maximize eval hit ratio (template path)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pressure_skill.eval_training import load_jsonl_cases, train_random_search
from pressure_skill.eval_casino_merge import merge_casino_labeled


def _default_case_paths() -> list[Path]:
    return [p for p in [ROOT / "eval" / "cases.jsonl"] if p.exists()]


def _casino_labeled_train_rows() -> list[dict[str, Any]]:
    labeled = ROOT / "eval" / "cases_casino_labeled.jsonl"
    sourced = ROOT / "eval" / "cases_sourced.jsonl"
    if not labeled.is_file() or not sourced.is_file():
        return []
    return merge_casino_labeled(sourced, labeled)


def _load_case_sets(paths: list[str], *, include_casino_labeled: bool) -> list[dict[str, Any]]:
    selected = [Path(p) for p in paths] if paths else _default_case_paths()
    if not selected:
        raise SystemExit("No case file found. Provide --cases at least once.")
    merged: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for p in selected:
        full = p if p.is_absolute() else (ROOT / p)
        rows = load_jsonl_cases(full)
        for row in rows:
            rid = str(row.get("id") or "")
            if rid and rid in seen_ids:
                continue
            if rid:
                seen_ids.add(rid)
            merged.append(row)
    if include_casino_labeled or not paths:
        for row in _casino_labeled_train_rows():
            rid = str(row.get("id") or "")
            if rid and rid in seen_ids:
                continue
            if rid:
                seen_ids.add(rid)
            merged.append(row)
    return merged


def main() -> None:
    ap = argparse.ArgumentParser(description="Train rerank weights via random search on eval cases")
    ap.add_argument(
        "--cases",
        action="append",
        default=[],
        help="Repeatable case file path (.jsonl). If omitted, loads eval/cases.jsonl plus optional CaSiNo labeled merge.",
    )
    ap.add_argument(
        "--no-casino-labeled",
        action="store_true",
        help="Do not append CaSiNo rows from cases_casino_labeled.jsonl + cases_sourced.jsonl (default: append when files exist).",
    )
    ap.add_argument(
        "--include-casino-labeled",
        action="store_true",
        help="When using explicit --cases, also append CaSiNo labeled merge (same as default append).",
    )
    ap.add_argument("--out", default="eval/rerank_weights.json")
    ap.add_argument("--iterations", type=int, default=400)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--eval-top-k",
        type=int,
        default=1,
        help="Training objective: mean weighted score over top K options (default 1).",
    )
    ap.add_argument("--must-weight", type=float, default=0.7)
    ap.add_argument("--nice-weight", type=float, default=0.3)
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="Do not print progress lines to stderr during search.",
    )
    args = ap.parse_args()

    include_casino = (not args.no_casino_labeled) and (bool(args.include_casino_labeled) or not args.cases)
    cases = _load_case_sets(args.cases, include_casino_labeled=include_casino)
    if not cases:
        raise SystemExit("No cases loaded")

    best_w, best_score = train_random_search(
        cases,
        iterations=args.iterations,
        seed=args.seed,
        eval_top_k=args.eval_top_k,
        must_weight=args.must_weight,
        nice_weight=args.nice_weight,
        log_progress=not args.quiet,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(best_w, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "best_score": best_score,
                "case_count": len(cases),
                "iterations": args.iterations,
                "eval_top_k": args.eval_top_k,
                "must_weight": args.must_weight,
                "nice_weight": args.nice_weight,
                "casino_train_rows": sum(
                    1 for c in cases if str(c.get("id", "")).startswith("casino_")
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
