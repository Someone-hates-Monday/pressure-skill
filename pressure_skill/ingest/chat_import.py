"""Parse exported chat logs (file upload) — no cloud API."""

from __future__ import annotations

import json
import re
from typing import Any


def parse_chat_export(content: str, *, fmt: str = "auto") -> dict[str, Any]:
    """
    Returns {transcript, message_count, format_detected, warnings[]}.
    Supported: wechat_txt, feishu_json, generic_lines.
    """
    text = (content or "").strip()
    if not text:
        return {"transcript": "", "message_count": 0, "format_detected": "empty", "warnings": ["empty input"]}

    detected = fmt
    if fmt == "auto":
        detected = _detect_format(text)

    if detected == "feishu_json":
        return _parse_feishu_json(text)
    if detected == "wechat_txt":
        return _parse_wechat_txt(text)
    return _parse_generic_lines(text)


def _detect_format(text: str) -> str:
    t = text.lstrip()
    if t.startswith("{") or t.startswith("["):
        try:
            data = json.loads(text)
            if isinstance(data, dict) and ("messages" in data or "items" in data):
                return "feishu_json"
            if isinstance(data, list) and data and isinstance(data[0], dict):
                return "feishu_json"
        except json.JSONDecodeError:
            pass
    if re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}", text):
        return "wechat_txt"
    return "generic_lines"


def _parse_wechat_txt(text: str) -> dict[str, Any]:
    lines_out: list[str] = []
    warnings: list[str] = []
    current_speaker = ""
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf, current_speaker
        if current_speaker and buf:
            lines_out.append(f"{current_speaker}: {' '.join(buf)}")
        buf = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        m = re.match(
            r"^\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日\s]+\d{1,2}:\d{2}(?::\d{2})?\s+(.+)$",
            line,
        )
        if m:
            flush()
            current_speaker = m.group(1).strip()
            continue
        m2 = re.match(r"^(.{1,32}?)[：:]\s*(.+)$", line)
        if m2:
            flush()
            current_speaker = m2.group(1).strip()
            buf = [m2.group(2).strip()]
        else:
            buf.append(line)
    flush()

    if not lines_out:
        warnings.append("wechat_txt pattern not matched; fell back to generic")
        return _parse_generic_lines(text)
    transcript = "\n".join(lines_out)
    return {
        "transcript": transcript,
        "message_count": len(lines_out),
        "format_detected": "wechat_txt",
        "warnings": warnings,
    }


def _parse_feishu_json(text: str) -> dict[str, Any]:
    warnings: list[str] = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return {
            "transcript": "",
            "message_count": 0,
            "format_detected": "feishu_json",
            "warnings": [f"invalid json: {e}"],
        }
    rows: list[dict[str, Any]] = []
    if isinstance(data, dict):
        rows = list(data.get("messages") or data.get("items") or [])
    elif isinstance(data, list):
        rows = data
    lines_out: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        sender = (
            item.get("sender_name")
            or item.get("name")
            or item.get("from")
            or item.get("user")
            or "?"
        )
        body = item.get("text") or item.get("content") or item.get("body") or ""
        if isinstance(body, dict):
            body = body.get("text") or json.dumps(body, ensure_ascii=False)
        body = str(body).strip()
        if body:
            lines_out.append(f"{sender}: {body}")
    if not lines_out:
        warnings.append("no messages in feishu_json; try generic export")
        return _parse_generic_lines(text)
    return {
        "transcript": "\n".join(lines_out),
        "message_count": len(lines_out),
        "format_detected": "feishu_json",
        "warnings": warnings,
    }


def _parse_generic_lines(text: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return {
        "transcript": "\n".join(lines),
        "message_count": len(lines),
        "format_detected": "generic_lines",
        "warnings": [],
    }
