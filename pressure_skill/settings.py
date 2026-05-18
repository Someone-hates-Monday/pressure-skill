"""Runtime paths (local-only; no cloud)."""

from __future__ import annotations

import os
from pathlib import Path


def counterparty_base_dir() -> Path:
    raw = os.getenv("PRESSURE_DATA_DIR", "counterparties")
    return Path(raw)
