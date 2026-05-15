from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def serialize_case_signals(c: dict[str, Any]) -> str:
    """Store legacy list or extended object in target_signals_json column."""
    legacy = c.get("target_signals") or []
    must = c.get("must_have_signals")
    nice = c.get("nice_to_have_signals")
    fb = c.get("forbidden_substrings")
    rub = c.get("rubric_notes")
    if must is None and nice is None and fb is None and rub is None:
        return json.dumps(legacy, ensure_ascii=False)
    obj: dict[str, Any] = {"target_signals": legacy}
    if must is not None:
        obj["must_have_signals"] = must
    if nice is not None:
        obj["nice_to_have_signals"] = nice
    if fb is not None:
        obj["forbidden_substrings"] = fb
    if rub is not None:
        obj["rubric_notes"] = rub
    return json.dumps(obj, ensure_ascii=False)


def parse_case_signals(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return {"target_signals": []}
    if isinstance(data, list):
        return {"target_signals": [x for x in data if isinstance(x, str)]}
    if isinstance(data, dict):
        out: dict[str, Any] = {
            "target_signals": [x for x in (data.get("target_signals") or []) if isinstance(x, str)],
        }
        for k in ("must_have_signals", "nice_to_have_signals", "forbidden_substrings", "rubric_notes"):
            if k in data:
                out[k] = data[k]
        return out
    return {"target_signals": []}


def ensure_schema(db_path: str) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS eval_cases (
                id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                text TEXT NOT NULL,
                profile_json TEXT NOT NULL,
                target_signals_json TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'local',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS eval_runs (
                run_id TEXT PRIMARY KEY,
                run_at TEXT NOT NULL,
                case_count INTEGER NOT NULL,
                avg_top_hit_ratio REAL NOT NULL,
                rows_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS eval_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                run_id TEXT,
                accepted INTEGER NOT NULL,
                usefulness INTEGER,
                note TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def upsert_cases(db_path: str, cases: list[dict[str, Any]], *, source: str) -> int:
    ensure_schema(db_path)
    conn = sqlite3.connect(db_path)
    now = _utc_now()
    n = 0
    try:
        for c in cases:
            conn.execute(
                """
                INSERT INTO eval_cases(id, mode, text, profile_json, target_signals_json, source, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    mode=excluded.mode,
                    text=excluded.text,
                    profile_json=excluded.profile_json,
                    target_signals_json=excluded.target_signals_json,
                    source=excluded.source
                """,
                (
                    c["id"],
                    c["mode"],
                    c["text"],
                    json.dumps(c.get("profile") or {}, ensure_ascii=False),
                    serialize_case_signals(c),
                    source,
                    now,
                ),
            )
            n += 1
        conn.commit()
        return n
    finally:
        conn.close()


def load_cases(db_path: str) -> list[dict[str, Any]]:
    ensure_schema(db_path)
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, mode, text, profile_json, target_signals_json
            FROM eval_cases
            ORDER BY id
            """
        ).fetchall()
    finally:
        conn.close()
    out: list[dict[str, Any]] = []
    for row in rows:
        sig = parse_case_signals(row[4])
        item: dict[str, Any] = {
            "id": row[0],
            "mode": row[1],
            "text": row[2],
            "profile": json.loads(row[3] or "{}"),
            "target_signals": sig.get("target_signals") or [],
        }
        for k in ("must_have_signals", "nice_to_have_signals", "forbidden_substrings", "rubric_notes"):
            if k in sig:
                item[k] = sig[k]
        out.append(item)
    return out


def save_run(db_path: str, result: dict[str, Any]) -> str:
    ensure_schema(db_path)
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO eval_runs(run_id, run_at, case_count, avg_top_hit_ratio, rows_json)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                run_id,
                _utc_now(),
                int(result.get("summary", {}).get("case_count") or 0),
                float(result.get("summary", {}).get("avg_top_hit_ratio") or 0.0),
                json.dumps(result.get("cases") or [], ensure_ascii=False),
            ),
        )
        conn.commit()
        return run_id
    finally:
        conn.close()


def add_feedback(
    db_path: str,
    *,
    case_id: str | None,
    run_id: str | None,
    accepted: bool,
    usefulness: int | None,
    note: str | None,
) -> None:
    ensure_schema(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO eval_feedback(case_id, run_id, accepted, usefulness, note, created_at)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                run_id,
                1 if accepted else 0,
                usefulness,
                note,
                _utc_now(),
            ),
        )
        conn.commit()
    finally:
        conn.close()
