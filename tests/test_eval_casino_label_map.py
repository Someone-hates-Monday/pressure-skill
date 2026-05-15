"""Tests for CaSiNo annotation → rerank substring mapping."""
from pressure_skill.eval_casino_label_map import signals_for_tag_csv


def test_elicit_pref_includes_which_and_priority_nice():
    must, nice = signals_for_tag_csv("elicit-pref")
    assert "Which" in must
    assert "priority" in nice


def test_combined_tags_merge_unique():
    must, nice = signals_for_tag_csv("promote-coordination,elicit-pref")
    assert "align" in must
    assert "Which" in must
    assert len(must) <= 4


def test_empty_tags_use_defaults():
    must, nice = signals_for_tag_csv(None)
    assert must == ["suggest", "risk", "align"]
    assert nice == ["priority", "quality"]
