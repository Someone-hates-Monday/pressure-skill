"""
Local counterparty manager (no cloud). Run from repo root:

  pip install -e ".[ui]"
  streamlit run streamlit_app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from pressure_skill.counterparty_feedback import record_outcome_feedback
from pressure_skill.counterparty_store import list_counterparties, load_counterparty, save_counterparty, slugify
from pressure_skill.ingest.chat_import import parse_chat_export
from pressure_skill.analyzer.profile import CommunicationProfile
from pressure_skill.settings import counterparty_base_dir

st.set_page_config(page_title="pressure.skill 档案", layout="wide")
st.title("pressure.skill — 本地沟通对象档案")

base = counterparty_base_dir()
st.caption(f"数据目录：`{base.resolve()}`（环境变量 `PRESSURE_DATA_DIR` 可改）")

tab_list, tab_detail, tab_import, tab_feedback = st.tabs(["列表", "详情", "导入聊天", "实地反馈"])

with tab_list:
    items = list_counterparties(base)
    if not items:
        st.info("尚无档案。在「详情」新建，或先用 Agent 会诊后 `counterparty_cli.py save`。")
    else:
        st.dataframe(
            [
                {
                    "slug": m.get("slug"),
                    "name": m.get("display_name"),
                    "sessions": m.get("session_count", 0),
                    "feedback": m.get("feedback_count", 0),
                    "updated": m.get("updated_at"),
                }
                for m in items
            ],
            use_container_width=True,
        )
    with st.expander("新建档案"):
        name = st.text_input("显示名（脱敏）", key="new_name")
        if st.button("创建") and name.strip():
            slug = slugify(name)
            save_counterparty(base, slug, CommunicationProfile(), display_name=name.strip(), merge=False)
            st.success(f"已创建 `{slug}`")
            st.rerun()

with tab_detail:
    slug = st.text_input("slug", key="detail_slug")
    if slug and st.button("加载"):
        try:
            data = load_counterparty(base, slug)
            st.session_state["cp_data"] = data
        except FileNotFoundError:
            st.error("未找到该 slug")
    data = st.session_state.get("cp_data")
    if data:
        st.subheader(data["meta"].get("display_name", data["slug"]))
        st.json(data["profile_dict"])
        st.markdown("**最近 outcomes**")
        st.json((data.get("outcomes") or [])[-5:])
        st.markdown("**corrections**")
        st.text(data.get("corrections") or "")

with tab_import:
    st.markdown("上传**导出文件**（微信 txt、飞书 JSON 导出、纯文本），**无需**在线 API。")
    slug_i = st.text_input("合并到 slug", key="import_slug")
    fmt = st.selectbox("格式", ["auto", "wechat_txt", "feishu_json", "generic_lines"])
    up = st.file_uploader("聊天导出", type=["txt", "json", "md"])
    if up and slug_i and st.button("解析并合并"):
        raw = up.read().decode("utf-8", errors="replace")
        parsed = parse_chat_export(raw, fmt=fmt)
        transcript = parsed.get("transcript") or ""
        if not transcript:
            st.warning(parsed)
        else:
            from pressure_skill.analyzer.features import extract_features_from_transcript
            from pressure_skill.analyzer.patterns import infer_pattern_tags

            d = load_counterparty(base, slug_i)
            p = d["profile"]
            feats = extract_features_from_transcript(transcript)
            tags = infer_pattern_tags(feats)
            note = f"[streamlit import {parsed.get('format_detected')}] {transcript[:800]}"
            cn = p.counterparty_notes or ""
            if transcript[:80] not in cn:
                cn = f"{cn}\n\n{note}".strip() if cn else note
            p = p.model_copy(
                update={
                    "features": {**(p.features or {}), **feats},
                    "pattern_tags": list({*(p.pattern_tags or []), *tags}),
                    "counterparty_notes": cn,
                }
            )
            save_counterparty(base, slug_i, p, merge=True)
            st.success(f"已合并 {parsed.get('message_count')} 条消息")
            st.json(parsed)

with tab_feedback:
    st.markdown("粘贴 `examples/feedback-outcome-template.json` 填好的内容。")
    slug_f = st.text_input("slug", key="fb_slug")
    raw = st.text_area("feedback JSON", height=320)
    if st.button("提交反馈并校准画像") and slug_f and raw.strip():
        try:
            body = json.loads(raw)
            out = record_outcome_feedback(base, slug_f, body, apply_profile=True)
            st.success("已写入 outcomes 并合并 profile")
            st.json(out)
        except Exception as e:
            st.error(str(e))
