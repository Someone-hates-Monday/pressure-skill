from __future__ import annotations

from pressure_skill.ingest.chat_import import parse_chat_export


def test_wechat_style():
    raw = """2024-01-02 14:30 张三
你好，今天能交吗
2024-01-02 14:31 我
还在整理数据"""
    r = parse_chat_export(raw, fmt="wechat_txt")
    assert r["message_count"] >= 2
    assert "张三" in r["transcript"]


def test_feishu_json():
    raw = """{"messages": [
      {"sender_name": "Li", "text": "ASAP please"},
      {"sender_name": "Me", "text": "Need scope first"}
    ]}"""
    r = parse_chat_export(raw, fmt="feishu_json")
    assert r["message_count"] == 2
    assert "ASAP" in r["transcript"]
