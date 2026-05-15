from pathlib import Path

from pressure_skill.eval_db import add_feedback, load_cases, save_run, upsert_cases


def test_eval_db_roundtrip(tmp_path: Path):
    db = tmp_path / "eval.db"
    cases = [
        {
            "id": "case_1",
            "mode": "deflect",
            "text": "今天下班前交",
            "profile": {"relation": "manager"},
            "target_signals": ["今天", "先", "后"],
        }
    ]
    n = upsert_cases(str(db), cases, source="unit")
    assert n == 1

    loaded = load_cases(str(db))
    assert len(loaded) == 1
    assert loaded[0]["id"] == "case_1"

    run_id = save_run(
        str(db),
        {
            "cases": [{"id": "case_1", "top_hit_ratio": 0.5}],
            "summary": {"case_count": 1, "avg_top_hit_ratio": 0.5},
        },
    )
    assert run_id.startswith("run_")

    add_feedback(
        str(db),
        case_id="case_1",
        run_id=run_id,
        accepted=True,
        usefulness=4,
        note="usable",
    )


def test_eval_db_extended_signals_roundtrip(tmp_path: Path):
    db = tmp_path / "eval_ext.db"
    cases = [
        {
            "id": "ext_1",
            "mode": "deflect",
            "text": "今晚必须上线",
            "profile": {"relation": "manager"},
            "target_signals": ["今天"],
            "must_have_signals": ["今晚"],
            "nice_to_have_signals": ["风险"],
            "forbidden_substrings": ["滚"],
            "rubric_notes": "demo",
        }
    ]
    upsert_cases(str(db), cases, source="unit")
    loaded = load_cases(str(db))
    assert loaded[0]["must_have_signals"] == ["今晚"]
    assert loaded[0]["nice_to_have_signals"] == ["风险"]
    assert loaded[0]["forbidden_substrings"] == ["滚"]
    assert loaded[0]["rubric_notes"] == "demo"
