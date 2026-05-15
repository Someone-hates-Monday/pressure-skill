from __future__ import annotations

import copy
import json
import random
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any

from pressure_skill.advisor.clap_back import suggest_clap_back
from pressure_skill.advisor.deflect import suggest_deflect
from pressure_skill.advisor.push import suggest_push
from pressure_skill.advisor.rerank_weights import DEFAULT_WEIGHTS
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.eval_metrics import hit_ratio, train_objective_score


def load_jsonl_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("\ufeff"):
        raw = raw.lstrip("\ufeff")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def run_case(
    c: dict[str, Any],
    weights: dict[str, float],
    *,
    eval_top_k: int = 1,
    must_weight: float = 0.7,
    nice_weight: float = 0.3,
) -> float:
    profile = CommunicationProfile.model_validate(c.get("profile") or {})
    text = c["text"]
    mode = c["mode"]
    if mode == "deflect":
        out = suggest_deflect(text, profile, use_llm=False, rerank_weights=weights)
    elif mode == "push":
        out = suggest_push(text, profile, use_llm=False, rerank_weights=weights)
    elif mode == "clap_back":
        out = suggest_clap_back(text, profile, use_llm=False, rerank_weights=weights)
    else:
        raise ValueError(f"Unsupported mode: {mode}")
    return train_objective_score(
        out,
        c,
        top_k=eval_top_k,
        must_weight=must_weight,
        nice_weight=nice_weight,
    )


def evaluate(
    weights: dict[str, float],
    cases: list[dict[str, Any]],
    *,
    eval_top_k: int = 1,
    must_weight: float = 0.7,
    nice_weight: float = 0.3,
) -> float:
    scores = [
        run_case(
            c,
            weights,
            eval_top_k=eval_top_k,
            must_weight=must_weight,
            nice_weight=nice_weight,
        )
        for c in cases
    ]
    return round(mean(scores), 4) if scores else 0.0


def clamp_weights(w: dict[str, float]) -> dict[str, float]:
    bounds: dict[str, tuple[float, float]] = {
        "min_len": (0.0, 2.0),
        "min_len_threshold": (12.0, 200.0),
        "time_anchor": (0.0, 3.0),
        "tradeoff": (0.0, 3.0),
        "acceptance_scope": (0.0, 3.0),
        "push_clear_ask": (0.0, 3.0),
        "deflect_negotiation": (0.0, 3.0),
        "clap_boundary": (0.0, 3.0),
        "clap_boundary_extra": (0.0, 3.0),
        "clarify_question": (0.0, 3.0),
        "relation_formality": (0.0, 3.0),
        "aggressive_penalty": (-6.0, -0.1),
        "urgency_match": (0.0, 3.0),
        "note_hit_cap": (0.0, 3.0),
        "note_hit_unit": (0.0, 1.0),
        "directive_fit": (0.0, 2.0),
        "fast_turnaround_fit": (0.0, 2.0),
        "clap_formal_criteria": (0.0, 2.0),
        "deflect_meeting_async": (0.0, 3.0),
    }
    out = dict(w)
    for k, (lo, hi) in bounds.items():
        if k in out:
            out[k] = max(lo, min(hi, float(out[k])))
    return out


def train_random_search(
    cases: list[dict[str, Any]],
    *,
    iterations: int,
    seed: int,
    eval_top_k: int = 1,
    must_weight: float = 0.7,
    nice_weight: float = 0.3,
    log_progress: bool = True,
) -> tuple[dict[str, float], float]:
    random.seed(seed)
    keys = list(DEFAULT_WEIGHTS.keys())
    best_w = clamp_weights(dict(DEFAULT_WEIGHTS))
    t0 = time.perf_counter()
    best_score = evaluate(
        best_w,
        cases,
        eval_top_k=eval_top_k,
        must_weight=must_weight,
        nice_weight=nice_weight,
    )
    if log_progress:
        dt = time.perf_counter() - t0
        est = dt * (1 + max(0, iterations))
        print(
            f"[train_rerank] cases={len(cases)} baseline={best_score:.4f} "
            f"initial_eval={dt:.1f}s rough_total~{est:.0f}s for {iterations} iters",
            file=sys.stderr,
            flush=True,
        )

    progress_mod = 50 if iterations >= 100 else (10 if iterations >= 25 else 1)

    for it in range(1, iterations + 1):
        cand = copy.deepcopy(best_w)
        k = random.choice(keys)
        step = abs(best_w[k]) * 0.25 + 0.1
        cand[k] = best_w[k] + random.uniform(-step, step)
        cand = clamp_weights(cand)
        sc = evaluate(
            cand,
            cases,
            eval_top_k=eval_top_k,
            must_weight=must_weight,
            nice_weight=nice_weight,
        )
        if sc > best_score:
            best_w, best_score = cand, sc
        if log_progress and progress_mod > 0 and it % progress_mod == 0:
            elapsed = time.perf_counter() - t0
            print(
                f"[train_rerank] iter {it}/{iterations} best={best_score:.4f} elapsed={elapsed:.0f}s",
                file=sys.stderr,
                flush=True,
            )
    if log_progress and iterations:
        print(
            f"[train_rerank] done best={best_score:.4f} total={time.perf_counter() - t0:.0f}s",
            file=sys.stderr,
            flush=True,
        )
    return best_w, best_score
