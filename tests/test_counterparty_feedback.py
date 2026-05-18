from __future__ import annotations

import json
from pathlib import Path

from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.counterparty_feedback import (
    format_calibration_block,
    record_outcome_feedback,
)
from pressure_skill.counterparty_store import load_counterparty, save_counterparty


def test_record_outcome_feedback_merges_profile(tmp_path: Path) -> None:
    base = tmp_path / "counterparties"
    save_counterparty(
        base,
        "boss",
        CommunicationProfile(relation=RelationRole.MANAGER, counterparty_notes="急躁"),
        merge=False,
    )
    feedback = {
        "advice_snapshot": {
            "user_purpose": "延期",
            "predicted_reactions": ["口头答应"],
        },
        "field_report": {
            "sent_message": "能否周五前",
            "counterparty_reply": "不行，今天下班前要，已抄送总监",
            "actual_reaction_tags": ["escalated"],
            "prediction_match": "wrong",
        },
        "deviation_summary": "预测拖延错了，实际升级",
        "learned_rules": ["点名 deadline 会抄送上级"],
        "pattern_tags_add": ["cc_on_deadline"],
    }
    result = record_outcome_feedback(base, "boss", feedback)
    assert result["ok"] is True
    data = load_counterparty(base, "boss")
    notes = data["profile"].counterparty_notes or ""
    assert "实测校准" in notes
    assert "抄送" in notes
    assert data["profile"].pattern_tags
    assert "cc_on_deadline" in data["profile"].pattern_tags
    assert len(data.get("outcomes") or []) == 1
    corr = data["corrections"]
    assert "预测偏差" in corr


def test_format_calibration_block() -> None:
    block = format_calibration_block(
        {
            "field_report": {"prediction_match": "partial", "counterparty_reply": "再说吧"},
            "learned_rules": ["喜欢模糊答应"],
        }
    )
    assert "partial" in block
    assert "模糊答应" in block
