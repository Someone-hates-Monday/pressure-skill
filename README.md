# pressure.skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/tests-pytest-green.svg)](CONTRIBUTING.md)

> 老板的「今天必须交」和你的生物钟，今天只能活一个？  
> 群里 @ 全体催命，你既不想撕破脸，又不想加班到假发起飞？  
> 客户只会说「尽快」「详细点」，验收标准比薛定谔的猫还量子？  
>
> **把冷冰冰的压力，变成能发出去的温暖回复。**  
> 一套长在沟通里的**立体攻防**：守（不接锅）— 转（换时间/范围）— 攻（把需求钉死）——再配一个靠谱的**超级嘴替**，替你开口、还不替你背锅。  
>
> **pressure.skill：我们不煲鸡汤，我们产「能直接发出去」的草稿。**

**[→ Quickstart：下载、安装与第一次使用](#quickstart)**

## 项目说明

**pressure.skill** 是一套面向职场高压沟通的 **Agent Skill + 本地工具**：先和你对齐**对方画像**与**本轮目的**，再按场景（推脱施压、柔和催办、对齐模糊需求、必要时立边界）给出**中英可发送草稿**，并附带**对方可能反应**的结构化提示（`reaction_hints`）。支持 **Cursor / Claude Code / OpenClaw** 同一套对话向导；可选 **FastAPI**、命令行 `bundle_local.py`、本地长期档案 `counterparties/`（复诊与实地反馈校准）。**无 API Key 可走模板**；配置 Key 后可接 LLM。设计参考 [colleague-skill](https://github.com/titanwings/colleague-skill) 的「材料结构化 + Skill」思路，**场景与实现独立**。

**阶段**：MVP（CI 见 [.github/workflows/ci.yml](.github/workflows/ci.yml)）。Phase 2 本地能力见 [docs/phase2-local.md](docs/phase2-local.md)。

**检索**：`pressure-skill` · Cursor `agent-skills` · `claude-code` · `openclaw` · 职场沟通 · **拒绝被压力** · **拒绝职场 PUA** · **反催办** · **软拒绝** · **立边界** · 催办回复 · 模糊需求对齐 · `fastapi` · 中英回复草稿

[如何验证效果](#如何验证效果) · [Nexent / 训练营提交](#nexent--训练营智能体形态) · [多平台 Skill](#多平台-skillcursor--claude-code--openclaw) · [隐私与长期画像](#隐私与长期画像) · [示例与演示](#示例与脱敏输出) · [API 与 CLI](#api-与-cli可选) · [评测与训练](#本地评测避免只靠感觉) · [贡献](CONTRIBUTING.md) · [路线图](#路线图与仓库实现同步迭代)

## Quickstart

### 1. 获取代码

```bash
git clone https://github.com/Someone-hates-Monday/pressure-skill.git
cd pressure-skill
```

也可在 GitHub 页面 **Code → Download ZIP**，解压后进入目录。

### 2. Python 环境（跑脚本 / API 时需要）

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
# 可选：LLM 路由
pip install "pressure-skill[llm]"
# 可选：Streamlit 档案界面
pip install "pressure-skill[ui]"
```

仅使用 **Cursor 等 Agent 里的 Skill 向导**、不在本机跑 Python 时，可跳过本节；但 **`bundle_local.py`、API、长期档案 CLI** 仍需在**已克隆的仓库根**执行。

### 3. 安装 Agent Skill（多平台）

在**仓库根目录**执行（会把 `.cursor/skills/pressure-skill/` 复制到用户目录）：

| 目标 | PowerShell（Windows） | macOS / Linux |
|------|------------------------|---------------|
| **Cursor + `.agents`** | `.\scripts\install_cursor_personal_skill.ps1` | `bash scripts/install_pressure_skill.sh cursor agents` |
| **全部**（含 Claude Code、OpenClaw） | `.\scripts\install_pressure_skill.ps1` | `bash scripts/install_pressure_skill.sh all` |
| 仅 Claude Code | `.\scripts\install_claude_code_skill.ps1` | `bash scripts/install_pressure_skill.sh claude` |
| 仅 OpenClaw | `.\scripts\install_openclaw_skill.ps1` | `bash scripts/install_pressure_skill.sh openclaw` |

安装后技能位于例如：`~/.cursor/skills/pressure-skill/`、`~/.claude/skills/pressure-skill/` 等。路径与排障见 **[docs/skill-adapters.md](docs/skill-adapters.md)**。

### 4. 第一次使用

1. 用 **Cursor**（或已安装技能的 Agent）**打开本仓库文件夹**作为工作区（推荐），或在任意项目里使用已安装的用户级 Skill。  
2. 在 Agent 对话中启用 **`/pressure-skill`**（名称以产品为准）。  
3. 按向导收集画像与场景，获得可发送草稿；需要结构化检查时，Agent 可能在仓库根运行 `bundle_local.py`（见 [examples/README.md](examples/README.md)）。

**只想快速试 CLI、不走向导**：

```bash
py -3 scripts/bundle_local.py --relation manager --user-purpose "争取延期" --situation "老板催今天下班前交"
```

### 5. 后续可选能力

| 能力 | 入口 |
|------|------|
| 本地 HTTP API | `uvicorn app:app --reload --port 8765` → 见下方 [API 与 CLI](#api-与-cli可选) |
| 长期对方档案 / 复诊 | `py -3 scripts/counterparty_cli.py list` · 协议见技能内 `references/counterparty-long-term.md` |
| 发出去后的真实反馈校准 | `counterparty_cli.py feedback` · [examples/feedback-outcome-template.json](examples/feedback-outcome-template.json) |
| 导入微信/飞书**导出文件** | `py -3 scripts/import_chat_export.py --file 导出.txt --slug <slug>` |
| Streamlit 管理界面 | `streamlit run streamlit_app.py` |

---

## 如何验证效果

本项目**不**用「像不像某个人」或单一准确率来证明自己，而用你可核对的结果：

| 你怎么看 | 在哪里体现 |
|----------|------------|
| **能直接发送** | `reply_options` 是消息体，不是长篇建议 |
| **信息不够会先说不瞎编** | `readiness.missing_fields`、`evidence_score` |
| **对方可能怎么回** | `reaction_hints`（`likely` / `one_line`） |
| **发完后能越用越准** | `counterparty_cli.py feedback` + 本地档案 |

**拍视频 / 写推文**：固定案例 [examples/demo-scenario-manager-deadline.md](examples/demo-scenario-manager-deadline.md)、裸问对比 [examples/raw-agent-baseline-prompt.md](examples/raw-agent-baseline-prompt.md)、分镜 [examples/video-shot-list.md](examples/video-shot-list.md)。  
**完整说明**：[docs/demo-and-trust.md](docs/demo-and-trust.md)。欢迎 [使用反馈 Issue](https://github.com/Someone-hates-Monday/pressure-skill/issues/new?template=user-feedback.yml)（脱敏）。

---

## Nexent / 训练营智能体形态

参加 [ModelEngine Nexent](https://github.com/ModelEngine-Group/nexent/discussions)（**重庆大学 AI 训练营** 等共用该讨论区）时，**提交用智能体**与 **Cursor Skill** 分开维护：

| 形态 | 目录 |
|------|------|
| Nexent 零代码智能体 + 发帖模板 | **[nexent-camp/](nexent-camp/README.md)** |
| 符合度自检（对照同学作品） | [nexent-camp/COMPLIANCE.md](nexent-camp/COMPLIANCE.md) |
| Discussions 正文模板 | [nexent-camp/SUBMISSION-DISCUSSION.md](nexent-camp/SUBMISSION-DISCUSSION.md) |

平台文档：[Nexent 概览](https://modelengine-group.github.io/nexent/zh/getting-started/overview.html)。可选生态：[ModelScope MCP](https://modelscope.cn/mcp)、[Exa](https://exa.ai/)、Datamate（见 `nexent-camp/agent/tools-setup.md`）。

---

## 多平台 Skill（Cursor / Claude Code / OpenClaw）

**向导**：全平台共用 `references/wizard-full-flow.md`（画像 → 目的 → 场景 → 话术 / 意图 / `reaction_hints`）；**长期复诊**见 `counterparty-long-term.md`；平台差异见 `platform-wizard-notes.md`。

- **Cursor**：仓库内 `.cursor/skills/pressure-skill/`，常用 **`/pressure-skill`**。  
- **Claude Code / OpenClaw**：安装脚本写入用户技能目录后，启用 **pressure-skill**，流程与 Cursor 一致。  
- **说明**：对话模型由**各 Agent 产品**决定；Python 脚本仅在**克隆下来的仓库根**运行。

完整说明：[docs/skill-adapters.md](docs/skill-adapters.md) · 脚本索引：[integrations/README.md](integrations/README.md)

---

## 隐私与长期画像

- **API / 单次对话**：默认不持久化原始对话；请求体仅在当次处理。  
- **长期对象（可选）**：经你同意后，脱敏画像写入本地 **`counterparties/{slug}/`**（已在 `.gitignore`，勿提交真实人名与聊天）。复诊、追加聊天、纠正与实地反馈见 `counterparty_cli.py` 与 `counterparty-feedback-loop.md`。  
- **无 API Key** 时走模板回退；接入云端 LLM 时请自行告知用户数据策略。

---

## API 与 CLI（可选）

```bash
uvicorn app:app --reload --port 8765
```

- `POST /api/v1/profile/from-text` — 从聊天记录启发式画像  
- `POST /api/v1/advice/bundle` — 组合场景；含 `readiness`、`reaction_hints`  
- **本地画像**：`GET/POST/PUT /api/v1/counterparties`、`POST .../feedback`、`POST .../ingest-chat`（`PRESSURE_DATA_DIR`，默认 `counterparties/`）

详见 [docs/phase2-local.md](docs/phase2-local.md)。

---

## 示例与脱敏输出

见 **[examples/README.md](examples/README.md)**（对比演示、含 `reaction_hints` 的 JSON、`refresh_demo_samples.py`）。

---

## 参与贡献

见 **[CONTRIBUTING.md](CONTRIBUTING.md)**。

---

## 本地评测（避免只靠感觉）

```bash
py -3 scripts/eval_local.py
```

- 基线：`eval/cases.jsonl`；加权命中、`must_have` / `forbidden_substrings` 等见脚本 `--help`。  
- 训练重排：`scripts/train_rerank.py`、`scripts/train_iter.py`  
- SQLite 闭环：`scripts/import_external_cases.py`、`scripts/add_feedback.py`  
- 语料与格式：[eval/DATA_SOURCES.md](eval/DATA_SOURCES.md)、[eval/external_sources.md](eval/external_sources.md)

---

## 研究与相关方向（技术路线参考）

- 谈判与多智能体协商评测（如 *NegotiationArena*、*LLM-Deliberation*）可作为「策略库 + 约束生成」旁证。  
- 协助式谈判 / 改写类工作与 advisor 模块一致，可用反馈迭代 prompt。

---

## 开发

```bash
pip install -e ".[dev]"
pytest
```

---

## 路线图（与仓库实现同步迭代）

1. **Phase 1**：半自动画像、多场景 API、无 Key 模板。  
2. **Phase 2（本地）**：Streamlit、`reaction_hints`、离线聊天导入、API 本地持久化 — [docs/phase2-local.md](docs/phase2-local.md)。**未做**：飞书/微信 live API、加密云同步。  
3. **Phase 3**：行业/文化场景标签、社区策略库、编辑器插件。

---

## License

MIT
