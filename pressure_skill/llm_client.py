from __future__ import annotations

import json
import os
import re
from typing import Any

def _model() -> str:
    return os.getenv("PRESSURE_MODEL", "gpt-4o-mini")


def complete_json_or_text(system: str, user: str, *, temperature: float = 0.3) -> dict[str, Any] | str:
    """
    Ask the model for JSON; fall back to parsing a JSON substring or raw text.
    """
    try:
        from litellm import completion
    except ImportError as e:
        raise RuntimeError(
            "LLM 路径需要安装 litellm：pip install litellm"
        ) from e

    resp = completion(
        model=_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    text = resp.choices[0].message.content or ""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}\s*$", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return text
