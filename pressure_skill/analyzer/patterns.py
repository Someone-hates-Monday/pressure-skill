from __future__ import annotations

from typing import Any


def infer_pattern_tags(features: dict[str, Any]) -> list[str]:
    """Map coarse features to human-readable pattern tags."""
    tags: list[str] = []
    imp = float(features.get("imperative_intensity") or 0)
    soft = float(features.get("soft_phrasing") or 0)
    gap = features.get("reply_gap_median_min")

    if imp >= 0.34:
        tags.append("directive_tone")
    if soft >= 0.25:
        tags.append("face_saving_language")
    if isinstance(gap, (int, float)) and gap <= 5:
        tags.append("fast_turnaround")
    if isinstance(gap, (int, float)) and gap >= 12 * 60:
        tags.append("slow_async_communication")

    if not tags:
        tags.append("neutral_tone")
    return tags
