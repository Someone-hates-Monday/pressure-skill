# 参与贡献

感谢你愿意改进 **pressure.skill**。本仓库定位为 **MVP / 实验阶段**，小步 PR 比大包大揽更容易合并。

## 环境

- Python **3.10+**（与 `pyproject.toml` 中 `requires-python` 一致）。
- 克隆后建议在仓库根执行：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

无需配置 API Key 即可跑通测试（advisor 默认走模板回退）。

## 评测与训练迭代

- `py -3 scripts/eval_local.py`：基线跑分。
- `py -3 scripts/train_rerank.py`：在 `eval/cases.jsonl` 上随机搜索 `rerank` 权重（启发式，不是神经网络训练）。
- 训练产物 `eval/rerank_weights.json` 默认 **gitignore**；仓库内保留 `eval/rerank_weights.defaults.json` 作为基线参考。

## PR 约定

- **一个 PR 一件事**：修 bug、加测试、改文档或加小功能分开提，便于 review。
- **先绿再推**：本地 `pytest` 通过；CI 会在 push / PR 到 `main` 或 `master` 时跑多版本 Python。
- **技能与向导同步**：若改 `pressure_skill/` 行为或 `readiness` 字段，请同步 **`.cursor/skills/pressure-skill/`** 与 **`.agents/skills/pressure-skill/`** 下的 `SKILL.md`、`references/*.md`（含 **`platform-wizard-notes.md`**）；两处应内容一致（或改主技能后运行 `scripts/install_cursor_personal_skill.ps1` / `install_pressure_skill.ps1` 从主技能覆盖副本）。
- **跨 Agent 安装**：Claude Code / OpenClaw 使用 `scripts/install_pressure_skill.ps1`（或 `.sh`）；说明见 [docs/skill-adapters.md](docs/skill-adapters.md) §5。
- **脱敏**：Issue / PR 描述、示例里不要贴真实姓名、工号、未公开项目细节。

## 代码风格

- 与现有文件一致：类型注解、`from __future__ import annotations`、无无关大重构。
- 新增逻辑尽量带 **测试**（`tests/` 下 pytest）。

## 好上手任务（可自行开 Issue）

- 为 `readiness` / `portrait_depth` 边界情况补测试用例。
- 扩充 `examples/` 中脱敏样例或英文场景。
- 文档：安装故障、Windows 编码说明、与 Cursor 版本差异。

如有破坏性 API 变更，请在 PR 正文写清迁移说明。

## 首次推送到 GitHub

1. 确认已 `git init` 且 `.gitignore` 符合预期（勿提交 `.env`、`.venv`、`eval/rerank_weights.json`、大体量再生数据等）。  
2. 本地 `pytest` 通过后：`git add -A`、`git status`、`git commit`，再 `git remote add` / `git push`。  
3. 仓库 **About**：Description 可选用 `README.md` 顶部 HTML 注释中的草稿；**Topics** 建议见 [docs/skill-adapters.md](docs/skill-adapters.md) §6。

### 未配置 `user.name` / `user.email` 时如何提交（不写全局 git config）

本仓库贡献约定：**不要**在自动化脚本里执行 `git config --global ...`。你可在本仓库**一次性**用 `-c` 只作用于当前命令，例如：

```bash
git -c user.name="Your Name" -c user.email="you@users.noreply.github.com" commit -m "Initial commit: pressure.skill MVP"
```

然后再执行 `git branch -M main`（先有提交，`main` 才存在）、`git push -u origin main`。远程 URL 请换成真实仓库地址，勿保留占位符 `https://github.com/<你>/<仓库>.git`。

若曾添加过占位 remote，先删掉再指向真实仓库：

```bash
git remote remove origin
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
```

用 `git remote -v` 确认 fetch/push 地址正确后再 `git push`。

若误将大文件加入暂存区（例如 `data/*.parquet`），先从索引移除并补进 `.gitignore`：

```bash
git rm --cached data/train-00000-of-00001.parquet
git add .gitignore
git commit -m "Stop tracking large parquet; ignore eval scratch JSON"
```
