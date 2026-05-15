from __future__ import annotations

import re
from statistics import mean
from typing import Any

_TS_LINE = re.compile(
    r"^\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2}[ T]\d{1,2}:\d{2}(?::\d{2})?)|(\d{1,2}:\d{2}(?::\d{2})?)\s*[-—]\s*"
)


def _split_messages(transcript: str) -> list[str]:
    lines = [ln.strip() for ln in transcript.splitlines() if ln.strip()]
    if not lines:
        return []
    # If very few lines, treat whole block as one message
    if len(lines) <= 2:
        return ["\n".join(lines)]
    return lines


def _imperative_score(text: str) -> float:
    hits = 0
    for w in (
        "必须",
        "尽快",
        "马上",
        "今天内",
        "立刻",
        "务必",
        "不要拖",
        "抓紧",
        "赶紧",
    ):
        hits += text.count(w)
    return min(1.0, hits / 3.0)


def _politeness_score(text: str) -> float:
    soft = sum(text.count(w) for w in ("麻烦", "请", "辛苦", "感谢", "谢谢", "方便"))
    return min(1.0, soft / 4.0)


def _avg_len(messages: list[str]) -> float:
    lens = [len(m) for m in messages]
    return float(mean(lens)) if lens else 0.0


def _parse_gaps_minutes(messages: list[str]) -> list[float]:
    """Best-effort gaps when lines start with a time token."""
    times: list[tuple[int, int]] = []
    for m in messages:
        m2 = m.strip()
        mo = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?", m2)
        if not mo:
            continue
        h, mi = int(mo.group(1)), int(mo.group(2))
        times.append((h, mi))
    gaps: list[float] = []
    for i in range(1, len(times)):
        a, b = times[i - 1], times[i]
        delta = (b[0] * 60 + b[1]) - (a[0] * 60 + a[1])
        if delta < 0:
            delta += 24 * 60
        gaps.append(float(delta))
    return gaps


def extract_features_from_transcript(transcript: str) -> dict[str, Any]:
    """
    Heuristic features from a small pasted fragment.
    Not a substitute for manual labels in early MVP.
    """
    messages = _split_messages(transcript)
    feats: dict[str, Any] = {
        "message_count": len(messages),
        "avg_message_len": round(_avg_len(messages), 2),
        "imperative_intensity": round(
            mean([_imperative_score(m) for m in messages]) if messages else 0.0,
            3,
        ),
        "soft_phrasing": round(
            mean([_politeness_score(m) for m in messages]) if messages else 0.0,
            3,
        ),
        "question_ratio": 0.0,
    }
    q = sum(1 for m in messages if "?" in m or "？" in m)
    feats["question_ratio"] = round(q / max(len(messages), 1), 3)

    gaps = _parse_gaps_minutes(messages)
    if gaps:
        feats["reply_gap_median_min"] = float(sorted(gaps)[len(gaps) // 2])
    return feats
