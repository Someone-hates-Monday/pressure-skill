import json
from pathlib import Path

from pressure_skill.advisor.rerank_weights import DEFAULT_WEIGHTS
from pressure_skill.eval_training import (
    clamp_weights,
    evaluate,
    load_jsonl_cases,
    train_random_search,
)


def test_evaluate_weights_runs(tmp_path: Path):
    cases_path = tmp_path / "c.jsonl"
    cases_path.write_text(
        json.dumps(
            {
                "id": "c1",
                "mode": "deflect",
                "text": "今天必须交",
                "profile": {"relation": "manager"},
                "target_signals": ["今天", "建议", "先"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    cases = load_jsonl_cases(cases_path)
    s = evaluate(dict(DEFAULT_WEIGHTS), cases)
    assert 0.0 <= s <= 1.0


def test_train_random_search_non_regressing(tmp_path: Path):
    cases_path = tmp_path / "c.jsonl"
    cases_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "c1",
                        "mode": "clap_back",
                        "text": "别催命",
                        "profile": {"relation": "peer"},
                        "target_signals": ["说清楚", "协作", "请"],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "id": "c2",
                        "mode": "deflect",
                        "text": "今天下班前交",
                        "profile": {"relation": "manager"},
                        "target_signals": ["建议", "先", "周"],
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    cases = load_jsonl_cases(cases_path)
    base = evaluate(dict(DEFAULT_WEIGHTS), cases)
    best_w, best_s = train_random_search(cases, iterations=120, seed=1, log_progress=False)
    assert best_s >= base - 1e-6
    assert best_w == clamp_weights(best_w)
