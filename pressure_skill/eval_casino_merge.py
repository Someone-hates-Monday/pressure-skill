"""Merge CaSiNo sourced rows with lightweight labeled overlays for training."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("\ufeff"):
        raw = raw.lstrip("\ufeff")
    rows: list[dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _has_trainable_signals(row: dict[str, Any]) -> bool:
    if row.get("must_have_signals") or row.get("nice_to_have_signals"):
        return True
    ts = row.get("target_signals") or []
    return bool(ts)


def _is_full_case_row(row: dict[str, Any]) -> bool:
    text = (row.get("text") or "").strip()
    mode = (row.get("mode") or "").strip()
    return len(text) >= 4 and bool(mode) and _has_trainable_signals(row)


def merge_casino_labeled(
    sourced_path: Path,
    labeled_path: Path,
) -> list[dict[str, Any]]:
    """
    Each line in labeled is either:
    - Full case: has text + mode + at least one of target_signals / must / nice → used as-is.
    - Overlay: same id as sourced, patch fields (target_signals, must_have_signals, nice_to_have_signals,
      forbidden_substrings, mode, profile, text, rubric_notes, annotation_meta).
    Unknown overlay ids are skipped.
    """
    sourced_rows = load_jsonl(sourced_path)
    by_id = {str(r.get("id", "")): r for r in sourced_rows if r.get("id")}

    out: list[dict[str, Any]] = []
    for lab in load_jsonl(labeled_path):
        rid = str(lab.get("id") or "").strip()
        if not rid:
            continue
        if _is_full_case_row(lab):
            row = dict(lab)
            row.setdefault("annotation_meta", {})
            if isinstance(row["annotation_meta"], dict):
                row["annotation_meta"] = {
                    **row["annotation_meta"],
                    "merge": "casino_full_row",
                }
            out.append(row)
            continue

        base = by_id.get(rid)
        if base is None:
            continue
        merged: dict[str, Any] = dict(base)
        for k in (
            "target_signals",
            "must_have_signals",
            "nice_to_have_signals",
            "forbidden_substrings",
            "mode",
            "profile",
            "text",
            "rubric_notes",
        ):
            if k in lab and lab[k] is not None:
                merged[k] = lab[k]
        am = lab.get("annotation_meta")
        if isinstance(am, dict):
            base_am = merged.get("annotation_meta")
            if isinstance(base_am, dict):
                merged["annotation_meta"] = {**base_am, **am, "labeled_overlay": True}
            else:
                merged["annotation_meta"] = {**am, "labeled_overlay": True}
        elif "annotation_meta" in lab:
            merged["annotation_meta"] = {"labeled_overlay": True}

        if not _has_trainable_signals(merged):
            continue
        out.append(merged)
    return out


__all__ = ["load_jsonl", "merge_casino_labeled"]
