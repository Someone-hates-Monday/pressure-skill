#!/usr/bin/env python3
"""One-command training loop: search weights -> write eval/rerank_weights.json -> print eval summary."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _child_env() -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _decode_pipe(data: bytes | None) -> str:
    if not data:
        return ""
    for enc in ("utf-8-sig", "utf-8", "gbk", "cp936"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run rerank weight search then eval_local")
    ap.add_argument("--iterations", type=int, default=500)
    ap.add_argument(
        "--cases",
        action="append",
        default=[],
        help="Repeatable case file path. If omitted, train_rerank auto-loads bundled case files.",
    )
    ap.add_argument("--out", default="eval/rerank_weights.json")
    ap.add_argument(
        "--train-eval-top-k",
        type=int,
        default=1,
        help="Passed to train_rerank: objective mean over top K options.",
    )
    ap.add_argument(
        "--report-top-k",
        type=int,
        default=2,
        help="Passed to eval_local: top-k weighted summary (default 2).",
    )
    ap.add_argument("--must-weight", type=float, default=0.7)
    ap.add_argument("--nice-weight", type=float, default=0.3)
    ap.add_argument(
        "--no-casino-labeled",
        action="store_true",
        help="Pass to train_rerank: skip CaSiNo labeled merge.",
    )
    ap.add_argument(
        "--include-casino-labeled",
        action="store_true",
        help="Pass to train_rerank: append CaSiNo merge when using explicit --cases.",
    )
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="Pass to train_rerank: suppress stderr progress during weight search.",
    )
    args = ap.parse_args()

    train_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "train_rerank.py"),
        "--out",
        str(ROOT / args.out),
        "--iterations",
        str(args.iterations),
        "--eval-top-k",
        str(args.train_eval_top_k),
        "--must-weight",
        str(args.must_weight),
        "--nice-weight",
        str(args.nice_weight),
    ]
    if args.no_casino_labeled:
        train_cmd.append("--no-casino-labeled")
    if args.include_casino_labeled:
        train_cmd.append("--include-casino-labeled")
    if args.quiet:
        train_cmd.append("--quiet")
    for case_path in args.cases:
        full = Path(case_path)
        if not full.is_absolute():
            full = ROOT / full
        train_cmd.extend(["--cases", str(full)])

    train = subprocess.run(train_cmd, cwd=str(ROOT), env=_child_env(), check=False)
    if train.returncode != 0:
        raise SystemExit(train.returncode)

    ev = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "eval_local.py"),
            "--top-k",
            str(args.report_top_k),
            "--must-weight",
            str(args.must_weight),
            "--nice-weight",
            str(args.nice_weight),
        ],
        cwd=str(ROOT),
        env=_child_env(),
        capture_output=True,
        check=False,
    )
    print(_decode_pipe(ev.stdout))
    if ev.returncode != 0:
        err = _decode_pipe(ev.stderr)
        if err.strip():
            print(err, file=sys.stderr)
        raise SystemExit(ev.returncode)


if __name__ == "__main__":
    main()
