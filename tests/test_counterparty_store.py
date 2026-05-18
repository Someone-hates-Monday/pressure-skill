from __future__ import annotations

import json
from pathlib import Path

import pytest

from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.counterparty_store import (
    append_correction,
    append_episode,
    list_counterparties,
    load_counterparty,
    merge_persisted_profiles,
    save_counterparty,
    slugify,
)


def test_slugify() -> None:
    assert slugify("张老板") == "张老板"
    assert "boss" in slugify("Boss Zhang")


def test_save_load_merge(tmp_path: Path) -> None:
    base = tmp_path / "counterparties"
    p1 = CommunicationProfile(
        relation=RelationRole.MANAGER,
        counterparty_notes="急躁",
    )
    save_counterparty(base, "boss", p1, display_name="张老板", merge=False)
    p2 = CommunicationProfile(
        relation=RelationRole.MANAGER,
        counterparty_notes="好面子",
        user_leverage_notes="排期已满",
    )
    save_counterparty(base, "boss", p2, merge=True)
    data = load_counterparty(base, "boss")
    notes = data["profile"].counterparty_notes or ""
    assert "急躁" in notes
    assert "好面子" in notes
    assert "排期已满" in (data["profile"].user_leverage_notes or "")


def test_episode_and_correction(tmp_path: Path) -> None:
    base = tmp_path / "counterparties"
    save_counterparty(
        base,
        "peer-a",
        CommunicationProfile(relation=RelationRole.PEER),
        merge=False,
    )
    append_episode(
        base,
        "peer-a",
        {"user_purpose": "延期", "situation_summary": "催进度"},
    )
    append_correction(base, "peer-a", "不会在群里点名", category="portrait")
    data = load_counterparty(base, "peer-a")
    assert len(data["episodes"]) == 1
    assert data["episodes"][0]["user_purpose"] == "延期"
    assert "不会在群里点名" in data["corrections"]
    items = list_counterparties(base)
    assert len(items) == 1
    assert items[0]["session_count"] == 1


def test_merge_persisted_profiles_text_dedup() -> None:
    merged = merge_persisted_profiles(
        {"counterparty_notes": "急躁"},
        {"counterparty_notes": "急躁"},
    )
    assert merged["counterparty_notes"] == "急躁"
