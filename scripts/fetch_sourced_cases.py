#!/usr/bin/env python3
"""Build eval/cases_sourced.jsonl from CaSiNo (GitHub or HuggingFace)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE_ID = "casino_naacl2021"
SOURCE_URL = "https://github.com/kushalchawla/CaSiNo"
SOURCE_JSON = "https://raw.githubusercontent.com/kushalchawla/CaSiNo/main/data/casino.json"
SOURCE_HF = "https://huggingface.co/datasets/kchawla123/casino"
SOURCE_PAPER = "Chawla et al., CaSiNo, NAACL 2021"


def _to_case(text: str, *, dialogue_id: str, turn_idx: int, speaker_id: str | None) -> dict[str, Any]:
    return {
        "id": f"casino_{dialogue_id}_{turn_idx:03d}",
        "mode": "deflect",
        "text": text[:500],
        "profile": {
            "relation": "peer",
            "extra_context_notes": "CaSiNo campsite negotiation (English); annotate before training use",
        },
        "target_signals": [],
        "annotation_meta": {
            "source": SOURCE_ID,
            "source_url": SOURCE_URL,
            "source_json": SOURCE_JSON,
            "source_hf_dataset": SOURCE_HF,
            "source_paper": SOURCE_PAPER,
            "dialogue_id": dialogue_id,
            "turn_index": turn_idx,
            "speaker_id": speaker_id,
            "tier": "sourced_raw",
            "needs_review": True,
            "language": "en",
        },
    }


def _cases_from_casino_json(data: list[dict[str, Any]], *, dialogue_limit: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    lim = len(data) if dialogue_limit <= 0 else min(dialogue_limit, len(data))
    for row in data[:lim]:
        did = str(row.get("dialogue_id", ""))
        for j, turn in enumerate(row.get("chat_logs") or []):
            if not isinstance(turn, dict):
                continue
            text = (turn.get("text") or "").strip()
            if len(text) < 12:
                continue
            cases.append(
                _to_case(
                    text,
                    dialogue_id=did,
                    turn_idx=j,
                    speaker_id=turn.get("id"),
                )
            )
    return cases


def _cases_from_parquet(path: Path, *, dialogue_limit: int) -> list[dict[str, Any]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise SystemExit("Install: py -3 -m pip install pyarrow") from e

    table = pq.read_table(path)
    n = table.num_rows
    lim = n if dialogue_limit <= 0 else min(dialogue_limit, n)
    cases: list[dict[str, Any]] = []
    for i in range(lim):
        row = table.slice(i, 1).to_pydict()
        chat_logs = (row.get("chat_logs") or [[]])[0]
        did = str(i)
        for j, turn in enumerate(chat_logs):
            if not isinstance(turn, dict):
                continue
            text = (turn.get("text") or "").strip()
            if len(text) < 12:
                continue
            cases.append(_to_case(text, dialogue_id=did, turn_idx=j, speaker_id=turn.get("id")))
    return cases


def _download_casino_json(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                "curl",
                "-L",
                "--connect-timeout",
                "30",
                "--max-time",
                "300",
                "-o",
                str(dest),
                SOURCE_JSON,
            ],
            check=True,
            capture_output=True,
        )
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    with urllib.request.urlopen(SOURCE_JSON, timeout=120) as resp:
        dest.write_bytes(resp.read())


def _load_from_github(path: Path, dialogue_limit: int) -> list[dict[str, Any]]:
    if not path.is_file():
        print(f"Downloading CaSiNo JSON to {path} ...", file=sys.stderr)
        _download_casino_json(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Expected casino.json to be a list of dialogues")
    return _cases_from_casino_json(data, dialogue_limit=dialogue_limit)


def _load_from_huggingface(split: str, dialogue_limit: int) -> list[dict[str, Any]]:
    from datasets import load_dataset

    ds = load_dataset("kchawla123/casino", split=split)
    if dialogue_limit > 0:
        ds = ds.select(range(min(dialogue_limit, len(ds))))
    # dialogue_limit <= 0: use full split
    cases: list[dict[str, Any]] = []
    for i, row in enumerate(ds):
        did = str(row.get("dialogue_id") or i)
        chat = row.get("chat_logs") or []
        if isinstance(chat, str):
            chat = json.loads(chat)
        for j, turn in enumerate(chat):
            if isinstance(turn, dict):
                text = (turn.get("text") or "").strip()
                sid = turn.get("id")
            else:
                text = str(turn).strip()
                sid = None
            if len(text) < 12:
                continue
            cases.append(_to_case(text, dialogue_id=did, turn_idx=j, speaker_id=sid))
    return cases


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch CaSiNo sourced cases (GitHub default)")
    ap.add_argument("--parquet", default="", help="Local HF parquet path (e.g. data/train-00000-of-00001.parquet)")
    ap.add_argument("--backend", choices=("github", "huggingface"), default="github")
    ap.add_argument("--split", default="train", help="HF split only")
    ap.add_argument(
        "--dialogue-limit",
        type=int,
        default=80,
        help="Max dialogues (rows). 0 = all rows in JSON/parquet.",
    )
    ap.add_argument("--raw-json", default="eval/raw/casino/casino.json")
    ap.add_argument("--out", default="eval/cases_sourced.jsonl")
    args = ap.parse_args()

    if args.parquet:
        pq_path = Path(args.parquet)
        if not pq_path.is_absolute():
            pq_path = ROOT / pq_path
        cases = _cases_from_parquet(pq_path, dialogue_limit=args.dialogue_limit)
        raw_note = str(Path(args.parquet).as_posix())
    elif args.backend == "huggingface":
        cases = _load_from_huggingface(args.split, args.dialogue_limit)
        raw_note = f"huggingface:kchawla123/casino split={args.split}"
    else:
        cases = _load_from_github(ROOT / args.raw_json, args.dialogue_limit)
        raw_note = str(Path(args.raw_json).as_posix())

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + ("\n" if cases else ""),
        encoding="utf-8",
    )

    manifest = {
        "source": SOURCE_ID,
        "source_url": SOURCE_URL,
        "source_hf_dataset": SOURCE_HF,
        "source_paper": SOURCE_PAPER,
        "backend": "parquet" if args.parquet else args.backend,
        "raw": raw_note,
        "dialogue_limit": args.dialogue_limit,
        "utterance_cases": len(cases),
        "out": str(out_path.relative_to(ROOT)).replace("\\", "/"),
        "needs_review": True,
        "train_note": "Not merged into train_rerank until target_signals annotated",
    }
    manifest_path = ROOT / "eval/raw/casino/manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
