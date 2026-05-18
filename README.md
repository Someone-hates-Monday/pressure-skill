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
> 给场景 + **沟通画像** → 更得体、可执行的**中英回复建议**（圆滑减量/延期、柔和推人、把模糊话落成可验收说法）。**没 API Key 也能先跑模板**，有 Key 再让 LLM 加码。

Skill 形态上曾受 [colleague-skill](https://github.com/titanwings/colleague-skill) 等开源 **Agent Skill** 实践的启发（材料结构化后再接能力），**场景与实现与本项目不同**。本仓库提供独立 **FastAPI** 与 **pressure-skill** 技能目录（`.cursor/skills/pressure-skill/`、`.agents/skills/pressure-skill/`）。

**阶段**：**Phase 1 / MVP**（路线图见文末）。Push / PR 到 `main` 或 `master` 时，GitHub Actions 跑 **`pytest`**（[.github/workflows/ci.yml](.github/workflows/ci.yml)）。

[示例与 bundle](#示例与脱敏输出) · [Skill / 多平台安装](#多平台-skillcursor--claude-code--openclaw) · [快速开始](#快速开始) · [评测与训练](#本地评测避免只靠感觉) · [贡献](CONTRIBUTING.md)

便于站内外检索（技术向）：`pressure-skill`、`cursor`、`agent-skills`、`claude-code`、`openclaw`、`fastapi`、`workplace-communication`、`negotiation`、`reply-drafts`、`zh-en`、`offline-templates`。  
便于中文检索（场景向）：**拒绝被压力**、**拒绝职场 PUA**、**反催办**、**不接锅**、**软拒绝**、**立边界**、**难沟通话术**、**催进度怎么回**、**需求太模糊**、**高情商回复草稿**。（**Git 本身没有「关键词」字段**；主要靠 GitHub **Topics / Description**、README、`pyproject.toml` 的 `keywords`、以及 Skill 的 `description`  frontmatter，详见 [GitHub 可发现性](#github-可发现性)。）

<!--
GitHub 仓库 About「Description」可粘贴（任选其一，注意约 350 字符上限）：

中文：冰冷压力 → 温暖回复；立体攻防式沟通 + 你的超级嘴替。中英草稿 + Cursor Skill / FastAPI；无 Key 先跑模板。
中文（含检索向，约 350 字内可截断）：拒绝被压力、拒绝职场 PUA；催办/模糊需求/不接锅 → 得体中英草稿。Cursor Agent Skill + FastAPI；无 Key 先跑模板。
English: Cold pressure → warm, sendable replies. Layered comms playbook + your super mouthpiece. ZH/EN + Cursor skill + FastAPI; offline templates.
English (searchy): Pushback, boundaries, anti-gaslighting vibes—turn vague pressure into sendable ZH/EN replies. Cursor skill + FastAPI; offline templates.

中英拼一句：
Turn icy deadlines into warm replies—layered workplace comms + your articulate stand-in. Cursor skill + FastAPI; templates first.
-->

## 多平台 Skill（Cursor / Claude Code / OpenClaw）

**向导**：全平台共用 **`references/wizard-full-flow.md`**（画像 → 目的 → 场景 → 话术/意图/对方可能反应）；**长期复诊**见 **`references/counterparty-long-term.md`**（本地 `counterparties/` 画像积累）。路径/触发差异见 **`references/platform-wizard-notes.md`**。

- **Cursor**：仓库内 **`.cursor/skills/pressure-skill/`**；Agent 中常用 **`/pressure-skill`**；协议见同目录 **`SKILL.md`**（先读 `wizard-full-flow.md`）。任意项目使用：在仓库根执行安装脚本（下条）或见 [docs/skill-adapters.md](docs/skill-adapters.md) **§0～§1**。  
- **Claude Code**：安装到 **`~/.claude/skills/pressure-skill/`**（脚本见下）；启用 **pressure-skill** 后 **同一套向导**（先读 `wizard-full-flow.md`）。详见 [docs/skill-adapters.md](docs/skill-adapters.md) **§5**。  
- **OpenClaw**：安装到 **`~/.openclaw/workspace/skills/pressure-skill/`**（以脚本与环境为准）；启用后 **同一套向导**。详见 **§5** 与 `platform-wizard-notes.md`。  
- **只想试 CLI、不要向导**：在仓库根运行 **`bundle_local.py`** 的示例命令与参数说明见 **[examples/README.md](examples/README.md)**；终端乱码可设 `PYTHONIOENCODING=utf-8` 或 `chcp 65001`（Windows）。向导内是否调用脚本由 Agent 按 `wizard-full-flow.md` **§8** 判断，不必在 README 重复。

- **完整说明**：[docs/skill-adapters.md](docs/skill-adapters.md)（多平台向导、路径约定、frontmatter 差异、排障）；**脚本索引**：[integrations/README.md](integrations/README.md)。
- **一键安装（PowerShell，仓库根）**  
  - 仅 Cursor + 用户 `.agents`：`.\scripts\install_cursor_personal_skill.ps1`  
  - **全部目标**：`.\scripts\install_pressure_skill.ps1`（写入 `%USERPROFILE%\.cursor\skills`、`\.agents\skills`、**`\.claude\skills`**、**`\.openclaw\workspace\skills`** 下的 `pressure-skill/`）  
  - 单独：`.\scripts\install_claude_code_skill.ps1` / `.\scripts\install_openclaw_skill.ps1`
- **macOS / Linux**：`bash scripts/install_pressure_skill.sh`（可选参数 `cursor` `agents` `claude` `openclaw` 或 `all`）。
- **说明**：各 Agent 里对话用的模型由**该产品**决定（例如 Cursor 里选中的模型）；本仓库 Python / `bundle_local.py` / `uvicorn` 仍在 **克隆下来的仓库根**执行（技能目录里只有 Markdown 向导，不含 `scripts/`）。仅当希望 **`bundle_local.py` 在本机调 API** 时，才需要配置 `.env` 与 `litellm`。

## 隐私与长期画像
- **API / 单次对话**：默认不持久化原始对话；请求体仅在当次处理。
- **长期对象（可选）**：经你同意后，Agent 可将脱敏后的**对方画像**合并保存到仓库根 **`counterparties/{slug}/`**（本地目录，已在 `.gitignore`，勿提交真实人名与聊天）。用于**复诊**：每次新情况仍走目的+场景分析，并可持续追加聊天记录、纠正与结果反馈。  
- **实地反馈闭环**：你把建议**真发出去**后，把对方回复、真实反应、以及「问清模糊话」后的含义带回；Agent 对照上轮预测写偏差，运行 `py -3 scripts/counterparty_cli.py feedback --slug … --feedback-file …` 写入 **`outcomes.jsonl`** 并合并进画像（`[实测校准]`）。模板：`examples/feedback-outcome-template.json`；协议：`references/counterparty-feedback-loop.md`。  
- CLI：`py -3 scripts/counterparty_cli.py list|show|save|episode|correction|feedback`。
- 未配置任何 API Key 时走**本地模板**回退，便于离线演示。
- 若自行接入云端 LLM，请在部署说明中告知用户数据出境与留存策略。

## 研究与相关方向（技术路线参考）

- 谈判与多智能体协商评测（LLM 策略、话术与结果）：如 *NegotiationArena*（ICML 2024）、*LLM-Deliberation* 等，可作为「策略库 + 约束生成」的理论旁证，而非直接复现游戏环境。
- 协助式谈判/改写类工作（将生硬表述改写成更易达成共识的说法）与「补救型 agent」思路，与本项目的 advisor 模块一致，可用 few-shot + 用户反馈（👍/👎）迭代 prompt。

## 快速开始

```bash
cd 压力.skill
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# 需要云端/本地多模型路由时再装：
pip install "pressure-skill[llm]"
# 可选：复制 .env.example 为 .env 并填写 OPENAI_API_KEY；本地模型可设 PRESSURE_MODEL=ollama/...
uvicorn app:app --reload --port 8765
```

- `POST /api/v1/profile/from-text`：粘贴少量聊天记录，返回启发式特征 + 可选人工补丁。
- `POST /api/v1/advice/clap-back`：回怼 / 立边界（低威胁场景，上级默认更克制）。  
- `POST /api/v1/advice/bundle`：组合场景；`profile` 可带 `counterparty_notes`、`user_leverage_notes`、`extra_context_notes`、`user_purpose`；可选 `clap_back_provocation`；响应含 `readiness`（`warnings`、`portrait_depth`、`evidence_score` 等）。

## 示例与脱敏输出

- 见 **[examples/README.md](examples/README.md)**：两条 `bundle_local.py` 对照命令 + 示意 JSON（`readiness.missing_fields` 等差异）。
- 将仓库推到 GitHub 后，可在 Actions 页查看 **CI** 是否通过。

## 参与贡献

见 **[CONTRIBUTING.md](CONTRIBUTING.md)**（环境、`pytest`、PR 粒度、与 Cursor Skill 同步约定）。

## 本地评测（避免只靠感觉）

```bash
py -3 scripts/eval_local.py
```

- 用 `eval/cases.jsonl` 跑模板路径基线；**summary 双轨**：`avg_top_hit_ratio`（仅对 `target_signals` 的 legacy 命中）+ `avg_top_weighted_score` / `avg_topk_weighted_score`（`must_have` / `nice_to_have` 加权，含 `forbidden_substrings` 硬门禁）。
- 每条 case 输出 `top_weighted_score`、`topk_weighted_score`、`forbidden_hit_top`、`signal_breakdown`；仍有 `strategy_trace`（重排原因标签）。
- **Case 扩展字段**（可选）：`must_have_signals`、`nice_to_have_signals`、`forbidden_substrings`、`rubric_notes`。未拆分时仍只用 `target_signals`。
- `eval_local.py` 支持 `--top-k`（默认 2）、`--must-weight` / `--nice-weight`（默认 0.7 / 0.3）。
- 当前脚本是 **heuristic baseline**，用于回归对比；更严的人工 rubric 可写在 `rubric_notes` 并配合离线表。

### 训练迭代（重排权重随机搜索）

```bash
# 1) 搜索重排权重（默认仅 eval/cases.jsonl）
py -3 scripts/train_rerank.py --iterations 600 --seed 7

# 从 CaSiNo 拉取真实语料（GitHub；见 eval/DATA_SOURCES.md）
py -3 scripts/fetch_sourced_cases.py --backend github --dialogue-limit 80
py -3 scripts/train_rerank.py --eval-top-k 2 --must-weight 0.7 --nice-weight 0.3

# 2) 一键：训练后立即跑 eval_local 看 summary
py -3 scripts/train_iter.py --iterations 600

# 3) 列出低分 case（默认按 weighted top-1；可用 --metric legacy|weighted|topk）
py -3 scripts/eval_report.py --threshold 0.35
```

- 默认权重见 `eval/rerank_weights.defaults.json`；训练产物 `eval/rerank_weights.json` 由 `.gitignore` 忽略，避免 PR 互相覆盖。
- `--cases` 支持重复传入（如 `--cases eval/cases.jsonl --cases your_cases.jsonl`），会按 case id 去重合并。
- **CaSiNo 已标注子集**：可用 `py -3 scripts/build_casino_labels_from_annotations.py` 从官方 `annotations` 生成 `eval/cases_casino_labeled.jsonl`（与 parquet 回合对齐）；或手写覆盖行（与 `eval/cases_sourced.jsonl` 对齐），默认训练会自动合并；格式见 [eval/CASINO_LABEL.md](eval/CASINO_LABEL.md)。显式 `--cases` 时需加 `--include-casino-labeled`；关闭合并用 `--no-casino-labeled`。
- 也可用环境变量覆盖：`PRESSURE_RERANK_WEIGHTS_FILE` 或 `PRESSURE_RERANK_WEIGHTS_JSON`（见 `pressure_skill/advisor/rerank_weights.py`）。
- Windows 控制台常为 GBK：`train_iter.py` 对子进程设置 `PYTHONIOENCODING=utf-8` 并对捕获输出尝试 UTF-8 / GBK 解码，避免 `UnicodeDecodeError`。
- **训练耗时**：`train_rerank.py` 每轮迭代会对当前加载的**全部** case 跑一次 `evaluate`；合并 CaSiNo 后可达上万条，总时间约为「单次 evaluate 耗时 × (iterations+1)」量级（本机约数秒/evaluate 时，600 轮约数十分钟）。进度与粗略总耗时估计会打印到 **stderr**；不需要时用 `train_rerank.py --quiet` 或 `train_iter.py --quiet` 关闭。
- `train_iter.py` 可将 `--train-eval-top-k` 传给 `train_rerank.py`，将 `--report-top-k` / `--must-weight` / `--nice-weight` 传给 `eval_local.py`（与 CLI 默认值一致）。

### SQLite 闭环（cases / runs / feedback）

```bash
# 1) 从本地 jsonl 导入/覆盖到 SQLite（也支持 csv）
py -3 scripts/import_external_cases.py --input eval/cases.jsonl --db eval/eval_runs.db --source local_seed

# 2) 用 DB 中 case 跑评测并保存 run
py -3 scripts/eval_local.py --db eval/eval_runs.db --use-db-cases --save-run

# 3) 记录人工反馈（是否采纳、主观有用度）
py -3 scripts/add_feedback.py --db eval/eval_runs.db --accepted yes --run-id <run_id> --usefulness 4 --note "对上级可用"
```

### 外部数据接入方向（可用）

- **ConvoKit / 公开谈判或沟通语料**：先转为 `jsonl` 或 `csv`，再走 `scripts/import_external_cases.py`。
- `jsonl` 单条格式示例：
  - `id`, `mode` (`deflect|push|clap_back`), `text`, `profile`(JSON), `target_signals`(array)
  - 可选：`must_have_signals`, `nice_to_have_signals`, `forbidden_substrings`, `rubric_notes`（扩展评测与 SQLite 序列化已支持）
- `csv` 列示例：
  - `id,mode,text,profile_json,target_signals_csv`

这套流程让“外部语料 → 本地评测库 → 跑分 → 人工反馈”打通，不再只靠主观感觉。
更具体来源与导入建议见 [eval/DATA_SOURCES.md](eval/DATA_SOURCES.md)、[eval/external_sources.md](eval/external_sources.md)。

## 开发

```bash
pip install -e ".[dev]"
pytest
```

## 路线图（与仓库实现同步迭代）

1. **Phase 1（当前）**：手动 + 半自动画像、三场景 API、无 Key 模板回退。
2. **Phase 2**：Streamlit 界面、聊天记录解析器（微信/企微/邮件片段）；长期画像已提供 **`counterparties/` + CLI**（MVP），后续可接加密或云端同步。
3. **Phase 3**：场景标签（行业/文化）、社区策略库、编辑器插件。

## GitHub 可发现性

GitHub **没有无限多个「关键词输入框」**，但你可以在多个**互不相干、都会被搜索/展示用到的字段**里重复、互补地放检索词（中文适合放 **Description / README**；**Topics** 以英文、连字符为主更稳）。

### 在网页上怎么设置（推荐顺序）

1. 打开仓库 → 右上角 **About** 旁的 **⚙️（Edit repository details）**。  
2. **Description**：粘贴 README 里 HTML 注释中的短简介（可优先用「含检索向」那条，注意约 **350 字符**上限）。  
3. **Website**：填文档站、在线 Demo、或 README 锚点链接（没有可留空）。  
4. **Topics**：在输入框里逐个输入标签后回车；可删除不合适的。  
5. 需要更全的元数据时：**Settings → General** 里同一套 **Description / Website / Topics** 也会同步思路（部分入口以 About 为准）。

### 还能填的「更多字段」（可选）

| 位置 | 作用 | 建议 |
|------|------|------|
| **Repository name** | URL 与品牌 | 已是 `pressure-skill` 类即可，少改 |
| **About → Description** | GitHub/Google 摘要 | 中英 + **拒绝被压力 / 拒绝 PUA / 边界** 等短语 |
| **About → Website** | 外链预览 | Demo、文档、或 Releases 页 |
| **Topics** | GitHub 主题聚合 | 见下方英文标签 + 少量你验证可用的中文（若输入框接受） |
| **README 标题与首段** | 站外 SEO、站内 code search | 已含中英文检索句 |
| **Releases 标题与说明** | 版本更新被搜到 | 每条 Release 正文里带 1～2 个核心场景词 |
| **Discussions（若开启）** | 社区长尾检索 | 置顶帖写清「适用场景」关键词 |
| **`pyproject.toml` → `[project.urls]`** | PyPI 项目页链接区 | `Homepage` / `Repository` / `Issues`（已指向本仓库） |
| **`.cursor/.../SKILL.md` 的 `description:`** | Cursor 里 `/` 搜技能 | 已加长，含中英触发词 |
| **Settings → General → Social preview** | 链接预览卡片图（可选） | 上传含项目名的截图，利于外部分享点击率 |

### Topics（GitHub 标签）建议复制

**英文（Topics 最常用）**：  
`cursor` `agent-skills` `cursor-agent` `claude-code` `openclaw` `fastapi` `pydantic` `python` `llm` `litellm` `workplace` `communication` `negotiation` `boundaries` `pushback` `say-no` `anti-gaslighting` `difficult-conversations` `soft-rejection` `reply-templates` `zh-cn` `english` `skill` `mvp` `api` `templates` `open-source` `workplace-wellbeing`

**说明**：GitHub Topics 对**非英文、空格、特殊符号**支持不稳定；**「拒绝被压力」「拒绝 PUA」**等请优先写在 **Description 与 README**（本文件已写）。若 Topics 输入框能接受简短中文，可额外加：`职场` `沟通`（以你实际能保存为准）。

### 用 GitHub CLI 批量加 Topics（可选）

在本机已登录 `gh` 时，可在仓库根执行（把 `OWNER/REPO` 换成你的，例如 `Someone-hates-Monday/pressure-skill`）：

```bash
gh repo edit OWNER/REPO --add-topic cursor --add-topic agent-skills --add-topic fastapi --add-topic workplace --add-topic communication --add-topic boundaries --add-topic pushback --add-topic anti-gaslighting --add-topic negotiation --add-topic llm --add-topic claude-code --add-topic openclaw
```

其余标签同理追加 `--add-topic <name>`；**Description** 可用：

```bash
gh repo edit OWNER/REPO --description "拒绝被压力、拒绝职场PUA；催办/模糊需求→得体中英草稿。Cursor Agent Skill + FastAPI；无Key模板。Cold pressure→warm replies."
```

（若提示超长，缩短到 350 字符内。）

## License

MIT
