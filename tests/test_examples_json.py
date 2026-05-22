import json
from pathlib import Path


def test_examples_json_are_valid():
    root = Path(__file__).resolve().parent.parent / "examples"
    for name in ("sample-bundle-with-leverage.json", "sample-bundle-thin-profile.json"):
        raw = (root / name).read_text(encoding="utf-8")
        if raw.startswith("\ufeff"):
            raw = raw.lstrip("\ufeff")
        data = json.loads(raw)
        assert "profile" in data
        assert "readiness" in data
        assert "deflect" in data
        r = data["readiness"]
        assert r["portrait_depth"] in ("minimal", "standard", "deep")
        assert "evidence_score" in r
        assert "portrait_depth_hint" in r
        hints = data["deflect"].get("reaction_hints") or []
        opts = data["deflect"].get("reply_options") or []
        if hints:
            assert len(hints) == len(opts)
            assert "one_line" in hints[0]
