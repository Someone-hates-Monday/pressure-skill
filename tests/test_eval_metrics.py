"""Tests for eval_metrics scoring helpers."""
from pressure_skill.eval_metrics import (
    case_signal_lists,
    forbidden_hit,
    hit_ratio,
    option_weighted_score,
    score_output_for_case,
    topk_weighted_mean,
    train_objective_score,
)


def test_legacy_target_signals_maps_to_must_only():
    case = {"target_signals": ["a", "b"], "text": "x"}
    must, nice = case_signal_lists(case)
    assert must == ["a", "b"]
    assert nice == []


def test_split_must_nice():
    case = {
        "must_have_signals": ["必须"],
        "nice_to_have_signals": ["加分"],
        "text": "",
    }
    must, nice = case_signal_lists(case)
    assert must == ["必须"]
    assert nice == ["加分"]


def test_weighted_score_and_forbidden():
    case = {
        "must_have_signals": ["必须"],
        "nice_to_have_signals": ["加分"],
        "forbidden_substrings": ["脏话"],
    }
    s_ok = option_weighted_score("必须 加分", case, must_weight=0.7, nice_weight=0.3)
    assert s_ok > 0.9
    s_bad = option_weighted_score("必须 脏话", case, must_weight=0.7, nice_weight=0.3)
    assert s_bad == 0.0


def test_score_output_for_case_topk():
    out = {"reply_options": ["必须A 加分B", "只有必须A"]}
    case = {
        "must_have_signals": ["必须A"],
        "nice_to_have_signals": ["加分B"],
    }
    m = score_output_for_case(out, case, top_k=2, must_weight=0.5, nice_weight=0.5)
    assert m["top_weighted_score"] == 1.0
    assert m["topk_weighted_score"] < 1.0
    assert m["forbidden_hit_top"] is False


def test_train_objective_matches_topk_mean():
    out = {"reply_options": ["必须", "必须"]}
    case = {"must_have_signals": ["必须"]}
    assert train_objective_score(out, case, top_k=2, must_weight=0.7, nice_weight=0.3) == 1.0


def test_forbidden_hit_case_insensitive():
    assert forbidden_hit("有脏话", ["脏话"]) is True
    assert forbidden_hit("clean", ["脏话"]) is False


def test_hit_ratio_empty_targets():
    assert hit_ratio("abc", []) == 0.0
