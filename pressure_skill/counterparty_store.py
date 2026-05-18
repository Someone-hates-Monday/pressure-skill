"""Local persistence for long-term counterparty portraits (opt-in, user workspace)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole

_PROFILE_PERSIST_KEYS = (
    "relation",
    "scene_tags",
    "reply_speed_hint",
    "prefers",
    "pain_points",
    "praise_vs_critique_notes",
    "pattern_tags",
    "features",
    "counterparty_notes",
    "user_leverage_notes",
    "extra_context_notes",
    "locale",
    "discipline_subfield",
    "artefact_preferences_notes",
    "counterparty_seniority",
)


def slugify(alias: str) -> str:
    s = alias.strip().lower()
    s = re.sub(r"[^\w\u4e00-\u9fff\-]+", "-", s, flags=re.UNICODE)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "counterparty"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def counterparty_dir(base_dir: str | Path, slug: str) -> Path:
    return Path(base_dir) / slug


def _meta_path(root: Path) -> Path:
    return root / "meta.json"


def _profile_path(root: Path) -> Path:
    return root / "profile.json"


def _episodes_path(root: Path) -> Path:
    return root / "episodes.jsonl"


def _corrections_path(root: Path) -> Path:
    return root / "corrections.md"


def _merge_text(old: str | None, new: str | None) -> str | None:
    o = (old or "").strip()
    n = (new or "").strip()
    if not n:
        return o or None
    if not o:
        return n
    if n in o:
        return o
    return f"{o}\n\n---\n\n{n}"


def _merge_lists(old: list[str], new: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in old + new:
        x = (x or "").strip()
        if not x or x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def profile_to_persist_dict(profile: CommunicationProfile | dict[str, Any]) -> dict[str, Any]:
    if isinstance(profile, CommunicationProfile):
        data = profile.model_dump(mode="json")
    else:
        data = dict(profile)
    out: dict[str, Any] = {}
    for k in _PROFILE_PERSIST_KEYS:
        if k in data and data[k] is not None:
            out[k] = data[k]
    rel = out.get("relation")
    if isinstance(rel, RelationRole):
        out["relation"] = rel.value
    return out


def merge_persisted_profiles(
    existing: dict[str, Any],
    incoming: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(existing)
    for k in _PROFILE_PERSIST_KEYS:
        if k not in incoming:
            continue
        v = incoming[k]
        if v is None:
            continue
        if k in ("counterparty_notes", "user_leverage_notes", "extra_context_notes", "praise_vs_critique_notes"):
            merged[k] = _merge_text(merged.get(k), v if isinstance(v, str) else str(v))
        elif k in ("scene_tags", "pain_points", "pattern_tags"):
            merged[k] = _merge_lists(list(merged.get(k) or []), list(v or []))
        elif k == "prefers":
            merged[k] = {**(merged.get("prefers") or {}), **(v or {})}
        elif k == "features":
            merged[k] = {**(merged.get("features") or {}), **(v or {})}
        else:
            merged[k] = v
    return merged


def list_counterparties(base_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(base_dir)
    if not root.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        mp = _meta_path(p)
        if not mp.is_file():
            continue
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        meta.setdefault("slug", p.name)
        out.append(meta)
    return out


def load_counterparty(
    base_dir: str | Path,
    slug: str,
) -> dict[str, Any]:
    root = counterparty_dir(base_dir, slug)
    if not root.is_dir():
        raise FileNotFoundError(f"counterparty not found: {slug}")
    meta = json.loads(_meta_path(root).read_text(encoding="utf-8"))
    profile_raw = json.loads(_profile_path(root).read_text(encoding="utf-8"))
    profile = CommunicationProfile.model_validate(profile_raw)
    episodes: list[dict[str, Any]] = []
    ep_path = _episodes_path(root)
    if ep_path.is_file():
        for line in ep_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                episodes.append(json.loads(line))
    corrections = ""
    cp = _corrections_path(root)
    if cp.is_file():
        corrections = cp.read_text(encoding="utf-8")
    outcomes: list[dict[str, Any]] = []
    op = root / "outcomes.jsonl"
    if op.is_file():
        for line in op.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                outcomes.append(json.loads(line))
    return {
        "slug": slug,
        "meta": meta,
        "profile": profile,
        "profile_dict": profile.model_dump(mode="json"),
        "episodes": episodes,
        "outcomes": outcomes,
        "corrections": corrections,
    }


def save_counterparty(
    base_dir: str | Path,
    slug: str,
    profile: CommunicationProfile | dict[str, Any],
    *,
    display_name: str | None = None,
    merge: bool = True,
) -> dict[str, Any]:
    root = counterparty_dir(base_dir, slug)
    root.mkdir(parents=True, exist_ok=True)
    incoming = profile_to_persist_dict(profile)

    meta: dict[str, Any]
    if _meta_path(root).is_file():
        meta = json.loads(_meta_path(root).read_text(encoding="utf-8"))
    else:
        meta = {
            "slug": slug,
            "display_name": display_name or slug,
            "created_at": _utc_now(),
            "session_count": 0,
        }
    if display_name:
        meta["display_name"] = display_name
    meta["updated_at"] = _utc_now()

    if merge and _profile_path(root).is_file():
        existing = json.loads(_profile_path(root).read_text(encoding="utf-8"))
        merged = merge_persisted_profiles(existing, incoming)
    else:
        merged = incoming

    _profile_path(root).write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _meta_path(root).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"slug": slug, "meta": meta, "profile": merged}


def append_episode(
    base_dir: str | Path,
    slug: str,
    episode: dict[str, Any],
) -> None:
    root = counterparty_dir(base_dir, slug)
    if not root.is_dir():
        raise FileNotFoundError(f"counterparty not found: {slug}")
    ep = dict(episode)
    ep.setdefault("at", _utc_now())
    with _episodes_path(root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(ep, ensure_ascii=False) + "\n")
    meta = json.loads(_meta_path(root).read_text(encoding="utf-8"))
    meta["session_count"] = int(meta.get("session_count") or 0) + 1
    meta["updated_at"] = _utc_now()
    meta["last_episode_at"] = ep["at"]
    _meta_path(root).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_correction(
    base_dir: str | Path,
    slug: str,
    text: str,
    *,
    category: str = "portrait",
) -> None:
    root = counterparty_dir(base_dir, slug)
    if not root.is_dir():
        raise FileNotFoundError(f"counterparty not found: {slug}")
    line = f"- [{category}] {text.strip()}\n"
    cp = _corrections_path(root)
    if cp.is_file():
        body = cp.read_text(encoding="utf-8")
        if not body.endswith("\n"):
            body += "\n"
        body += line
    else:
        body = f"# Corrections ({slug})\n\n## {_utc_now()[:10]}\n{line}"
    cp.write_text(body, encoding="utf-8")
    meta = json.loads(_meta_path(root).read_text(encoding="utf-8"))
    meta["corrections_count"] = int(meta.get("corrections_count") or 0) + 1
    meta["updated_at"] = _utc_now()
    _meta_path(root).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
