from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_WEIGHTS: dict[str, float] = {
    "min_len": 0.4,
    "min_len_threshold": 24.0,
    "time_anchor": 1.1,
    "tradeoff": 1.0,
    "acceptance_scope": 0.9,
    "push_clear_ask": 1.0,
    "deflect_negotiation": 1.0,
    "clap_boundary": 0.8,
    "clap_boundary_extra": 1.2,
    "clarify_question": 0.9,
    "relation_formality": 0.9,
    "aggressive_penalty": -2.5,
    "urgency_match": 0.6,
    "note_hit_cap": 1.2,
    "note_hit_unit": 0.25,
    "directive_fit": 0.4,
    "fast_turnaround_fit": 0.4,
    "clap_formal_criteria": 0.7,
    "deflect_meeting_async": 1.0,
}


def _merge_weights(base: dict[str, float], override: dict[str, Any]) -> dict[str, float]:
    out = dict(base)
    for k, v in override.items():
        if k not in out:
            continue
        try:
            out[k] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def load_weights_from_file(path: Path) -> dict[str, float] | None:
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("\ufeff"):
        raw = raw.lstrip("\ufeff")
    data = json.loads(raw)
    if not isinstance(data, dict):
        return None
    return _merge_weights(DEFAULT_WEIGHTS, data)


def active_weights() -> dict[str, float]:
    env_json = os.getenv("PRESSURE_RERANK_WEIGHTS_JSON", "").strip()
    if env_json:
        try:
            data = json.loads(env_json)
            if isinstance(data, dict):
                return _merge_weights(DEFAULT_WEIGHTS, data)
        except json.JSONDecodeError:
            pass

    env_path = os.getenv("PRESSURE_RERANK_WEIGHTS_FILE", "").strip()
    candidates: list[Path] = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path("eval/rerank_weights.json"))

    for p in candidates:
        loaded = load_weights_from_file(p)
        if loaded is not None:
            return loaded
    return dict(DEFAULT_WEIGHTS)
