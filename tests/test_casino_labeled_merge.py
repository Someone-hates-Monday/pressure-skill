"""Tests for CaSiNo sourced + labeled overlay merge."""
import json
from pathlib import Path

from pressure_skill.eval_casino_merge import merge_casino_labeled


def test_overlay_merges_signals_from_sourced(tmp_path: Path):
    sourced = tmp_path / "s.jsonl"
    sourced.write_text(
        json.dumps(
            {
                "id": "casino_0_001",
                "mode": "deflect",
                "text": "Hello negotiation line here long enough",
                "profile": {"relation": "peer"},
                "target_signals": [],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    labeled = tmp_path / "l.jsonl"
    labeled.write_text(
        json.dumps({"id": "casino_0_001", "target_signals": ["a", "b"]}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    out = merge_casino_labeled(sourced, labeled)
    assert len(out) == 1
    assert out[0]["text"].startswith("Hello")
    assert out[0]["target_signals"] == ["a", "b"]


def test_overlay_skips_unknown_id(tmp_path: Path):
    sourced = tmp_path / "s.jsonl"
    sourced.write_text(
        json.dumps(
            {"id": "casino_0_001", "mode": "deflect", "text": "x" * 20, "profile": {}, "target_signals": []},
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    labeled = tmp_path / "l.jsonl"
    labeled.write_text(
        json.dumps({"id": "casino_99_999", "target_signals": ["a"]}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    assert merge_casino_labeled(sourced, labeled) == []


def test_full_row_appended_without_sourced_id(tmp_path: Path):
    sourced = tmp_path / "s.jsonl"
    sourced.write_text(
        json.dumps(
            {"id": "casino_0_001", "mode": "deflect", "text": "y" * 20, "profile": {}, "target_signals": []},
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    labeled = tmp_path / "l.jsonl"
    labeled.write_text(
        json.dumps(
            {
                "id": "custom_1",
                "mode": "push",
                "text": "Please send the report today please",
                "profile": {"relation": "peer"},
                "target_signals": ["today", "please"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    out = merge_casino_labeled(sourced, labeled)
    assert len(out) == 1
    assert out[0]["id"] == "custom_1"
    assert out[0]["mode"] == "push"
