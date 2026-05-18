"""Apply real-world outcome feedback to counterparty portraits (prediction calibration)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.counterparty_store import (
    _corrections_path,
    _meta_path,
    _utc_now,
    append_correction,
    append_episode,
    counterparty_dir,
    merge_persisted_profiles,
    save_counterparty,
)

_OUTCOMES_FILE = "outcomes.jsonl"


def _outcomes_path(root: Path) -> Path:
    return root / _OUTCOMES_FILE


def _prediction_match_rank(match: str | None) -> int:
    m = (match or "").strip().lower()
    if m in ("right", "correct", "对", "准确"):
        return 3
    if m in ("partial", "部分", "partly"):
        return 2
    if m in ("wrong", "incorrect", "错", "偏差大"):
        return 1
    return 0


def format_calibration_block(feedback: dict[str, Any]) -> str:
    """Human-readable block merged into counterparty_notes for Agent context."""
    snap = feedback.get("advice_snapshot") or {}
    field = feedback.get("field_report") or {}
    dev = (feedback.get("deviation_summary") or "").strip()
    learned = feedback.get("learned_rules") or []
    lines = [
        f"[实测校准 {_utc_now()[:10]}]",
        f"目的: {(snap.get('user_purpose') or field.get('user_purpose') or '—')}",
    ]
    pred = snap.get("predicted_reactions")
    if pred:
        lines.append(f"曾预测反应: {pred if isinstance(pred, str) else ' / '.join(map(str, pred))}")
    actual = field.get("actual_reaction_tags") or field.get("actual_reaction")
    if actual:
        lines.append(f"实际反应: {actual if isinstance(actual, str) else ' / '.join(map(str, actual))}")
    match = field.get("prediction_match")
    if match:
        lines.append(f"预测吻合度: {match}")
    if field.get("sent_message"):
        lines.append(f"已发送: {str(field['sent_message'])[:200]}")
    if field.get("counterparty_reply"):
        lines.append(f"对方回复: {str(field['counterparty_reply'])[:300]}")
    if field.get("vague_probe") and field.get("vague_probe_reply"):
        lines.append(f"澄清问: {str(field['vague_probe'])[:120]}")
        lines.append(f"澄清答: {str(field['vague_probe_reply'])[:300]}")
    if dev:
        lines.append(f"偏差: {dev}")
    for rule in learned[:6]:
        if isinstance(rule, str) and rule.strip():
            lines.append(f"· {rule.strip()}")
    return "\n".join(lines)


def build_profile_patch_from_feedback(feedback: dict[str, Any]) -> dict[str, Any]:
    """Merge explicit profile_updates with auto-generated calibration notes."""
    patch: dict[str, Any] = dict(feedback.get("profile_updates") or {})
    block = format_calibration_block(feedback)
    if block:
        existing = (patch.get("counterparty_notes") or "").strip()
        patch["counterparty_notes"] = f"{existing}\n\n{block}".strip() if existing else block

    tags_add = feedback.get("pattern_tags_add") or []
    if tags_add:
        patch["pattern_tags"] = [t for t in tags_add if isinstance(t, str) and t.strip()]

    field = feedback.get("field_report") or {}
    vague_reply = (field.get("vague_probe_reply") or "").strip()
    if vague_reply:
        patch["praise_vs_critique_notes"] = _merge_vague_calibration(
            patch.get("praise_vs_critique_notes"),
            field.get("vague_probe"),
            vague_reply,
        )

    return patch


def _merge_vague_calibration(
    existing: str | None,
    probe: str | None,
    reply: str | None,
) -> str:
    chunk = f"[模糊话实测] 问:{(probe or '—')[:80]} → 答:{(reply or '—')[:200]}"
    if existing and chunk in existing:
        return existing
    return f"{existing}\n\n{chunk}".strip() if existing else chunk


def record_outcome_feedback(
    base_dir: str | Path,
    slug: str,
    feedback: dict[str, Any],
    *,
    apply_profile: bool = True,
) -> dict[str, Any]:
    """
    Persist field outcome, append episode, optional corrections, merge profile patch.

    Expected feedback keys (all optional except field_report with some content):
      advice_snapshot, field_report, deviation_summary, learned_rules,
      profile_updates, pattern_tags_add, corrections[]
    """
    root = counterparty_dir(base_dir, slug)
    if not root.is_dir():
        raise FileNotFoundError(f"counterparty not found: {slug}")

    field = feedback.get("field_report") or {}
    if not any(
        field.get(k)
        for k in (
            "sent_message",
            "counterparty_reply",
            "follow_up_thread",
            "vague_probe_reply",
            "actual_reaction_tags",
            "actual_reaction",
        )
    ):
        raise ValueError("field_report must include at least one of sent_message, counterparty_reply, vague_probe_reply, actual_reaction")

    record = dict(feedback)
    record["kind"] = "outcome_feedback"
    record["at"] = record.get("at") or _utc_now()

    with _outcomes_path(root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    episode_row = {
        "kind": "outcome_feedback",
        "user_purpose": (feedback.get("advice_snapshot") or {}).get("user_purpose")
        or field.get("user_purpose"),
        "situation_summary": (field.get("situation_summary") or "")[:500],
        "outcome": field.get("prediction_match") or field.get("actual_reaction"),
        "note": (feedback.get("deviation_summary") or "")[:800],
        "prediction_match": field.get("prediction_match"),
        "actual_reaction_tags": field.get("actual_reaction_tags"),
    }
    append_episode(base_dir, slug, episode_row)

    corrections = feedback.get("corrections") or []
    for c in corrections:
        if isinstance(c, str):
            append_correction(base_dir, slug, c, category="pattern")
        elif isinstance(c, dict) and c.get("text"):
            append_correction(
                base_dir,
                slug,
                str(c["text"]),
                category=str(c.get("category") or "pattern"),
            )

    match = field.get("prediction_match")
    if _prediction_match_rank(match) <= 1:
        dev = (feedback.get("deviation_summary") or "").strip()
        if dev:
            append_correction(
                base_dir,
                slug,
                f"预测偏差: {dev[:400]}",
                category="pattern",
            )

    profile_result = None
    if apply_profile:
        patch = build_profile_patch_from_feedback(feedback)
        if patch:
            profile_result = save_counterparty(
                base_dir,
                slug,
                CommunicationProfile.model_validate(
                    merge_persisted_profiles({}, patch),
                ),
                merge=True,
            )

    meta = json.loads(_meta_path(root).read_text(encoding="utf-8"))
    meta["feedback_count"] = int(meta.get("feedback_count") or 0) + 1
    meta["last_feedback_at"] = record["at"]
    meta["updated_at"] = _utc_now()
    _meta_path(root).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "slug": slug,
        "feedback_at": record["at"],
        "profile_merged": profile_result is not None,
        "calibration_preview": format_calibration_block(feedback)[:500],
    }


def load_recent_outcomes(
    base_dir: str | Path,
    slug: str,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    root = counterparty_dir(base_dir, slug)
    path = _outcomes_path(root)
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows[-limit:]
