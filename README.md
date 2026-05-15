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

结构上借鉴 [titanwings/colleague-skill](https://github.com/titanwings/colleague-skill) 的「材料进 → 结构化画像 → 下游能力」：同事类 skill 蒸馏**那个人**，**我们蒸馏「怎么把天聊下去还不背锅」**。独立 **FastAPI** 服务 + **Cursor** 技能 **pressure-skill**（见 `.cursor/skills/pressure-skill/SKILL.md` 或 `.agents/skills/pressure-skill/SKILL.md`）。

**阶段**：**Phase 1 / MVP**（路线图见文末）。Push / PR 到 `main` 或 `master` 时，GitHub Actions 跑 **`pytest`**（[.github/workflows/ci.yml](.github/workflows/ci.yml)）。

[在 Cursor 里试](#在-cursor-里第一次实验) · [起服务](#快速开始) · [评测与训练](#本地评测避免只靠感觉) · [贡献](CONTRIBUTING.md)

<!--
GitHub 仓库 About「Description」可粘贴（任选其一，注意约 350 字符上限）：

中文：冰冷压力 → 温暖回复；立体攻防式沟通 + 你的超级嘴替。中英草稿 + Cursor Skill / FastAPI；无 Key 先跑模板。
English: Cold pressure → warm, sendable replies. Layered comms playbook + your super mouthpiece. ZH/EN + Cursor skill + FastAPI; offline templates.

中英拼一句：
Turn icy deadlines into warm replies—layered workplace comms + your articulate stand-in. Cursor skill + FastAPI; templates first.
-->

## 在 Cursor 里第一次实验

- **仅本仓库**：已含项目技能 `.cursor/skills/pressure-skill/`。  
- **所有项目都要用**：在仓库根运行 `.\scripts\install_cursor_personal_skill.ps1`（仅 Cursor + `.agents`），或 `.\scripts\install_pressure_skill.ps1` 一次装到 **Cursor / `.agents` / Claude Code / OpenClaw**；详见 [docs/skill-adapters.md](docs/skill-adapters.md)。

1. 在 Agent 中启用 **`/pressure-skill`**。Agent 会先读取 **`.cursor/skills/pressure-skill/references/wizard-full-flow.md`**，再按该文件**分步提问**（可跳过非必填项），最后给出结构化建议；可选运行 `bundle_local.py` 生成带 `readiness` 的 JSON。
2. 若只需快速试脚本（无需向导），在终端执行（无需 API Key，模板回退）。若输出乱码，可先 `chcp 65001` 或设置 `PYTHONIOENCODING=utf-8`。

```bash
py -3 scripts/bundle_local.py --relation manager --use-llm false --locale auto --situation "今天下班前必须交完整版" --vague "详细点，别流水账" --user-purpose "争取缓冲" --user-leverage "并行项目占用主要精力"
```

- `--locale`：`auto`（按文本推断中/英）、`zh`、`en`。响应里 `readiness.locale` 与模板/LLM 语言一致。
- 科研/「写明白」类模糊需求可补充：`--discipline-subfield`、`--artefact-preferences`、`--counterparty-seniority`（写入 `CommunicationProfile`，供 `readiness` 与 clarify 模板使用）。

3. 可选：将聊天记录保存为 UTF-8 文本，加上 `--transcript-file path/to/snippet.txt` 以更新启发式画像。

## 多平台 Skill（Cursor / Claude Code / OpenClaw）

- **完整说明**：[docs/skill-adapters.md](docs/skill-adapters.md)（路径约定、frontmatter 差异、排障）；**脚本索引**：[integrations/README.md](integrations/README.md)。
- **一键安装（PowerShell，仓库根）**  
  - 仅 Cursor + 用户 `.agents`：`.\scripts\install_cursor_personal_skill.ps1`  
  - **全部目标**：`.\scripts\install_pressure_skill.ps1`（写入 `%USERPROFILE%\.cursor\skills`、`\.agents\skills`、**`\.claude\skills`**、**`\.openclaw\workspace\skills`** 下的 `pressure-skill/`）  
  - 单独：`.\scripts\install_claude_code_skill.ps1` / `.\scripts\install_openclaw_skill.ps1`
- **macOS / Linux**：`bash scripts/install_pressure_skill.sh`（可选参数 `cursor` `agents` `claude` `openclaw` 或 `all`）。
- **说明**：各 Agent 里对话用的模型由**该产品**决定（例如 Cursor 里选中的模型）；本仓库 Python / `bundle_local.py` / `uvicorn` 仍在 **克隆下来的仓库根**执行（技能目录里只有 Markdown 向导，不含 `scripts/`）。仅当希望 **`bundle_local.py` 在本机调 API** 时，才需要配置 `.env` 与 `litellm`。

## 隐私
- 默认不持久化原始对话；API 仅处理请求体中的文本。
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
2. **Phase 2**：Streamlit 界面、聊天记录解析器（微信/企微/邮件片段）、SQLite 仅存摘要特征。
3. **Phase 3**：场景标签（行业/文化）、社区策略库、编辑器插件。

## License

MIT
