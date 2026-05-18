# Phase 2（本地可实现部分）

本仓库**不依赖**自建云服务或飞书/微信**在线 API**。下列能力均在本地完成。

## 已实现

| 能力 | 入口 |
|------|------|
| 长期画像 `counterparties/` | `scripts/counterparty_cli.py`、Agent `counterparty-long-term.md` |
| 实地反馈校准 | `counterparty_cli.py feedback`、`counterparty-feedback-loop.md` |
| **`reaction_hints` 结构化** | `bundle` / 各 advice API 响应中与 `reply_options` 对齐 |
| **聊天导出导入**（离线） | `scripts/import_chat_export.py`、`POST .../ingest-chat`、Streamlit「导入聊天」 |
| **API 本地持久化** | `PRESSURE_DATA_DIR`（默认 `./counterparties`），见 `pressure_skill/api_counterparty.py` |
| **Streamlit 管理界面** | `pip install -e ".[ui]"` → `streamlit run streamlit_app.py` |

### 聊天导入支持格式

- **微信**：PC 端导出 txt（时间行 + 昵称 + 内容，或 `昵称: 内容`）
- **飞书**：消息 JSON 导出（`messages` / `items` 数组，含 `sender_name` + `text`）
- **generic_lines**：每行一条，或任意纯文本

**不支持（需官方 API / 登录态，已跳过）**：飞书/钉钉全自动采集、企业微信实时拉取、加密云同步。

## 环境变量

- `PRESSURE_DATA_DIR`：画像根目录，默认 `counterparties`
- API Key 仍仅用于 **可选 LLM**；无 Key 时模板 + `reaction_hints` 启发式仍可用

## 启动 API（含持久化路由）

```bash
uvicorn app:app --reload --port 8765
# GET  /api/v1/counterparties
# GET  /api/v1/counterparties/{slug}
# PUT  /api/v1/counterparties/{slug}
# POST /api/v1/counterparties
# POST /api/v1/counterparties/{slug}/feedback
# POST /api/v1/counterparties/{slug}/ingest-chat
```

## 明确跳过（无云服务）

- 端到端加密云同步、多设备同步
- 飞书/钉钉 **live** collector（可参考 [colleague-skill](https://github.com/titanwings/colleague-skill) 自建，需自行配置 App 凭证）
