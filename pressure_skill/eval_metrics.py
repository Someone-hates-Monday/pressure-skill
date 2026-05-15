"""Shared eval scoring: legacy substring hits, weighted must/nice, optional forbidden gates, top-k average."""
from __future__ import annotations

from statistics import mean
from typing import Any


def hit_ratio(text: str, targets: list[str]) -> float:
    if not targets:
        return 0.0
    t = (text or "").lower()
    hits = sum(1 for s in targets if s and s.lower() in t)
    return hits / len(targets)


def case_signal_lists(case: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (must_have, nice_to_have). Legacy rows use target_signals as must-only."""
    must_raw = case.get("must_have_signals")
    nice_raw = case.get("nice_to_have_signals")
    if must_raw is not None or nice_raw is not None:
        must = [x for x in (must_raw or []) if isinstance(x, str) and x]
        nice = [x for x in (nice_raw or []) if isinstance(x, str) and x]
        return must, nice
    legacy = [x for x in (case.get("target_signals") or []) if isinstance(x, str) and x]
    return legacy, []


def effective_flat_targets(case: dict[str, Any]) -> list[str]:
    """Single list for legacy-style top_hit_ratio when target_signals is empty."""
    explicit = [x for x in (case.get("target_signals") or []) if isinstance(x, str) and x]
    if explicit:
        return explicit
    must, nice = case_signal_lists(case)
    return must + nice


def weighted_signal_score(
    text: str,
    must: list[str],
    nice: list[str],
    *,
    must_weight: float,
    nice_weight: float,
) -> float:
    if not must and not nice:
        return 1.0
    must_r = hit_ratio(text, must) if must else 1.0
    nice_r = hit_ratio(text, nice) if nice else 1.0
    if must and nice:
        wsum = must_weight + nice_weight
        if wsum <= 0:
            return 0.0
        return (must_weight * must_r + nice_weight * nice_r) / wsum
    if must:
        return must_r
    return nice_r


def forbidden_hit(text: str, forbidden: list[str]) -> bool:
    t = (text or "").lower()
    for f in forbidden:
        if isinstance(f, str) and f and f.lower() in t:
            return True
    return False


def option_weighted_score(
    text: str,
    case: dict[str, Any],
    *,
    must_weight: float,
    nice_weight: float,
) -> float:
    must, nice = case_signal_lists(case)
    fb = [x for x in (case.get("forbidden_substrings") or []) if isinstance(x, str) and x]
    if forbidden_hit(text, fb):
        return 0.0
    return weighted_signal_score(text, must, nice, must_weight=must_weight, nice_weight=nice_weight)


def top_weighted_score(
    reply_options: list[Any],
    case: dict[str, Any],
    *,
    must_weight: float,
    nice_weight: float,
) -> float:
    opts = [o for o in (reply_options or []) if isinstance(o, str)]
    if not opts:
        return 0.0
    return option_weighted_score(opts[0], case, must_weight=must_weight, nice_weight=nice_weight)


def topk_weighted_mean(
    reply_options: list[Any],
    case: dict[str, Any],
    *,
    top_k: int,
    must_weight: float,
    nice_weight: float,
) -> float:
    opts = [o for o in (reply_options or []) if isinstance(o, str)]
    if not opts:
        return 0.0
    k = max(1, int(top_k))
    chunk = opts[:k]
    return mean(
        option_weighted_score(o, case, must_weight=must_weight, nice_weight=nice_weight) for o in chunk
    )


def legacy_top_hit_ratio(top: str, case: dict[str, Any]) -> float:
    """Dashboard-compatible: substring hit rate vs target_signals, else flat must+nice."""
    explicit = [x for x in (case.get("target_signals") or []) if isinstance(x, str) and x]
    if explicit:
        return hit_ratio(top, explicit)
    return hit_ratio(top, effective_flat_targets(case))


def score_output_for_case(
    out: dict[str, Any],
    case: dict[str, Any],
    *,
    top_k: int,
    must_weight: float,
    nice_weight: float,
) -> dict[str, Any]:
    options = out.get("reply_options") or []
    top = options[0] if options else ""
    must, nice = case_signal_lists(case)
    fb = [x for x in (case.get("forbidden_substrings") or []) if isinstance(x, str) and x]
    rubric_notes = case.get("rubric_notes")
    rubric_notes_out = rubric_notes if isinstance(rubric_notes, str) else None

    return {
        "top_hit_ratio": round(legacy_top_hit_ratio(top, case), 3),
        "top_weighted_score": round(
            top_weighted_score(options, case, must_weight=must_weight, nice_weight=nice_weight),
            3,
        ),
        "topk_weighted_score": round(
            topk_weighted_mean(
                options,
                case,
                top_k=top_k,
                must_weight=must_weight,
                nice_weight=nice_weight,
            ),
            3,
        ),
        "forbidden_hit_top": forbidden_hit(top, fb),
        "signal_breakdown": {
            "must_count": len(must),
            "nice_count": len(nice),
            "forbidden_count": len(fb),
            "uses_split_signals": (case.get("must_have_signals") is not None)
            or (case.get("nice_to_have_signals") is not None),
        },
        "rubric_notes": rubric_notes_out,
    }


def train_objective_score(
    out: dict[str, Any],
    case: dict[str, Any],
    *,
    top_k: int,
    must_weight: float,
    nice_weight: float,
) -> float:
    """Scalar for weight search: mean top-k weighted (same as topk_weighted_mean)."""
    return topk_weighted_mean(
        out.get("reply_options") or [],
        case,
        top_k=top_k,
        must_weight=must_weight,
        nice_weight=nice_weight,
    )


__all__ = [
    "case_signal_lists",
    "effective_flat_targets",
    "forbidden_hit",
    "hit_ratio",
    "legacy_top_hit_ratio",
    "option_weighted_score",
    "score_output_for_case",
    "top_weighted_score",
    "topk_weighted_mean",
    "train_objective_score",
    "weighted_signal_score",
]
