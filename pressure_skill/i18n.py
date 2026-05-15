"""Lightweight locale hints (no heavy NLP)."""
from __future__ import annotations

import re
from typing import Any, Literal

Locale = Literal["zh", "en"]


def infer_locale(text: str) -> Locale:
    """
    If the sample is mostly Latin letters, treat as English; else Chinese default.
    """
    t = (text or "").strip()
    if not t:
        return "zh"
    letters = re.findall(r"[A-Za-z]", t)
    han = re.findall(r"[\u4e00-\u9fff]", t)
    if len(letters) >= 12 and len(letters) >= len(han) * 1.2:
        return "en"
    return "zh"


def merge_locale(*parts: str) -> Locale:
    return infer_locale("\n".join(p for p in parts if p))


def effective_locale(profile: Any, *text_samples: str) -> Locale:
    """Pick zh/en from profile.locale or infer from profile fields + extra text."""
    loc = getattr(profile, "locale", None)
    if loc in ("zh", "en"):
        return loc  # type: ignore[return-value]
    return merge_locale(
        getattr(profile, "user_purpose", None) or "",
        getattr(profile, "counterparty_notes", None) or "",
        getattr(profile, "user_leverage_notes", None) or "",
        getattr(profile, "extra_context_notes", None) or "",
        *text_samples,
    )
