"""Map CaSiNo dialog-act annotation tags to English substring signals for rerank training.

Peer + English situation uses _deflect_pool_en; signals are chosen to hit that pool
case-insensitively (eval_metrics.hit_ratio).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# (must_have, nice_to_have)
TAG_SIGNALS: dict[str, tuple[list[str], list[str]]] = {
    "elicit-pref": (["Which", "first", "part"], ["priority", "align"]),
    "promote-coordination": (["align", "sequence", "suggest"], ["Friday", "Monday"]),
    "other-need": (["understand", "need"], ["deadline", "deliver"]),
    "self-need": (["I suggest", "I can"], ["priority", "core"]),
    "non-strategic": (["scope", "risk"], ["acceptance", "defer"]),
    "small-talk": (["Got it", "Understood"], ["quality", "week"]),
    "vouch-fair": (["quality", "reviewable"], ["risk", "today"]),
    "showing-empathy": (["Understood", "understand"], ["need", "Friday"]),
    "no-need": (["lower-priority", "defer"], ["next iteration", "move"]),
    "uv-part": (["suggest", "risk"], ["core", "align"]),
}

DEFAULT_MUST = ["suggest", "risk", "align"]
DEFAULT_NICE = ["priority", "quality"]


def merge_signal_caps(must: list[str], nice: list[str], *, max_each: int = 4) -> tuple[list[str], list[str]]:
    return must[:max_each], nice[:max_each]


def signals_for_tag_csv(tag_csv: str | None) -> tuple[list[str], list[str]]:
    if not tag_csv or not str(tag_csv).strip():
        return merge_signal_caps(list(DEFAULT_MUST), list(DEFAULT_NICE))
    must: list[str] = []
    nice: list[str] = []
    for raw in str(tag_csv).split(","):
        tag = raw.strip()
        if not tag or tag not in TAG_SIGNALS:
            continue
        m, n = TAG_SIGNALS[tag]
        for x in m:
            if x not in must:
                must.append(x)
        for x in n:
            if x not in nice:
                nice.append(x)
    if not must and not nice:
        return merge_signal_caps(list(DEFAULT_MUST), list(DEFAULT_NICE))
    return merge_signal_caps(must, nice)


def _annotation_map(annotations: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    if not isinstance(annotations, list):
        return out
    for pair in annotations:
        if isinstance(pair, (list, tuple)) and len(pair) >= 2:
            utt, tags = pair[0], pair[1]
            if isinstance(utt, str) and isinstance(tags, str):
                out[utt] = tags
    return out


def labels_from_casino_parquet(parquet_path: Path) -> list[dict[str, Any]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise ImportError("Install pyarrow to read CaSiNo parquet") from e

    table = pq.read_table(parquet_path)
    n = table.num_rows
    rows_out: list[dict[str, Any]] = []
    for i in range(n):
        slice_ = table.slice(i, 1).to_pydict()
        chat_logs = (slice_.get("chat_logs") or [[]])[0]
        annotations = (slice_.get("annotations") or [[]])[0]
        amap = _annotation_map(annotations)
        for j, turn in enumerate(chat_logs):
            if not isinstance(turn, dict):
                continue
            text = (turn.get("text") or "").strip()
            if len(text) < 12:
                continue
            cid = f"casino_{i}_{j:03d}"
            tag_csv = amap.get(text)
            must, nice = signals_for_tag_csv(tag_csv)
            rows_out.append(
                {
                    "id": cid,
                    "must_have_signals": must,
                    "nice_to_have_signals": nice,
                    "annotation_meta": {
                        "casino_dialog_acts": tag_csv or "",
                        "label_tier": "auto_from_casino_annotations",
                    },
                }
            )
    return rows_out


__all__ = [
    "TAG_SIGNALS",
    "DEFAULT_MUST",
    "DEFAULT_NICE",
    "merge_signal_caps",
    "signals_for_tag_csv",
    "labels_from_casino_parquet",
]
