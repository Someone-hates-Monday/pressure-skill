# 把 pressure-skill 装进 Cursor，以及跨 Agent 适配说明

## 1. Cursor 里「技能」放哪

| 类型 | 路径（Windows 示例） | 作用 |
|------|----------------------|------|
| **项目技能** | 仓库内 `.cursor/skills/pressure-skill/`（含 `SKILL.md` 与 `references/`） | 克隆本仓库的人自动带上，适合协作与版本管理。 |
| **个人技能** | `%USERPROFILE%\.cursor\skills\pressure-skill\`（整目录） | 所有项目都能用；向导正文在 `references/wizard-full-flow.md`。 |

**不要**往 `~/.cursor/skills-cursor/` 里放自定义内容，那是 Cursor 内置技能目录。

Cursor 要求的结构是：`技能名/` 目录下必须有 **`SKILL.md`**，且 frontmatter 里至少要有 **`name`** 与 **`description`**（见官方「Creating Skills」文档）。

## 2. 一键装到「个人 Cursor Skills」

在本仓库根目录执行（PowerShell）：

```powershell
.\scripts\install_cursor_personal_skill.ps1
# 或一次写入 Cursor + .agents + Claude Code + OpenClaw：
.\scripts\install_pressure_skill.ps1
```

会把你当前仓库里的 **整个** `.cursor/skills/pressure-skill/` 目录（含 `references/`）复制到：

- `%USERPROFILE%\.cursor\skills\pressure-skill\`
- `%USERPROFILE%\.agents\skills\pressure-skill\`

`install_pressure_skill.ps1` 还会额外复制到（若目录不存在会创建）：

- `%USERPROFILE%\.claude\skills\pressure-skill\`（**Claude Code** 常见用户技能路径，与 [colleague-skill](https://github.com/titanwings/colleague-skill) 安装方式一致）
- `%USERPROFILE%\.openclaw\workspace\skills\pressure-skill\`（**OpenClaw** 工作区技能路径，以当前社区约定为准；若你环境不同，可改脚本或手动复制到产品文档指定目录）

（`.cursor` / `.agents` 为 [Cursor 文档](https://cursor.com/docs/skills) 列出的用户级扫描目录。）

之后任意工作区都可以在 Agent 里试用 **`/pressure-skill`**（以各产品实际命令名为准）。

卸载：删除上述路径中名为 `pressure-skill` 的整段文件夹即可。

## 2.1 若 `/` 里搜不到、设置里显示 No Skills Yet

1. **先看筛选**：在 **Rules, Skills, Subagents** 页面顶部，把 **压力.skill** 切换为 **User** 或 **All**。仅看当前仓库时，**个人技能**（装在用户目录下的）有时不会出现在该列表里，但 `/pressure-skill` 仍可能可用。  
2. **完整命令名**：在 Agent 输入框输入 **`/pressure-skill`**（带连字符，与文件夹名一致）。  
3. **重载窗口**：`Ctrl+Shift+P` → **Developer: Reload Window**。  
4. **重新安装**：在仓库根目录执行 `.\scripts\install_cursor_personal_skill.ps1` 或 `.\scripts\install_pressure_skill.ps1`（同源复制，UTF-8 无 BOM）。  
5. **仍不行**：用 **New Skill** 走一遍向导（若版本支持从目录导入），或升级 Cursor 到文档要求的版本；社区有「全局技能不显示」类报告，可与官方论坛对照。

## 3. 加到「各种 AI Agent」要不要适配？

**Markdown 工作流本身可复用**（目标、步骤、隐私、示例话术），但 **元数据与运行环境几乎一定要按平台裁剪**，否则要么不加载，要么 Agent 乱用工具。

常见差异维度：

| 维度 | Cursor Agent Skill | Claude Code / OpenClaw 类「Skill」 | ChatGPT Custom GPT / 其它 |
|------|---------------------|-------------------------------------|----------------------------|
| 入口 | `.cursor/skills/<name>/SKILL.md` | 常为仓库内 `SKILL.md` + 安装路径约定 | 系统提示 + 上传知识，无统一 SKILL 目录 |
| Frontmatter | `name`、`description`，可选 `disable-model-invocation` | 常见 `argument-hint`、`allowed-tools`、`user-invocable` 等（与 Cursor 不完全相同） | 通常无 YAML，用配置页代替 |
| 工具名 | Cursor：`Read`、`Write`、`Bash`… | 另一套工具名或子 Agent 约束 | 插件/API，与本仓库脚本无直接对应 |
| 路径变量 | 工作区根目录 | 常有 `CLAUDE_SKILL_DIR` 等 | 无，需要写死「先 clone 再 cd」 |
| 触发方式 | 技能列表 / 描述匹配 | `/command`、规则文件、用户显式 @ | 用户选 GPT / @mention |

结论：**要适配运行环境与安装路径**；本仓库把 **Markdown 向导与协议** 做成一份主技能，用脚本复制到 Cursor / Claude Code / OpenClaw 等目录（见 **§2、§5**）。若某平台强制要求额外 frontmatter，再在该平台侧加薄封装，而不是复制整份 `references/`。

## 4. 其他开源 Skill 常见做法（可照抄的模式）

1. **仓库内一份「主 Skill」**（例如同事.skill 的 `SKILL.md`）：给 Claude Code 用，内含 `allowed-tools`、脚本路径。  
2. **另写短版或 wrapper**：给 Cursor 用，只保留 Cursor 支持的字段，并把「跑脚本」改成 `py -3 scripts/...` 或「用 Read 读某文件」。  
3. **不在多份正文里重复维护长文档**：长说明进 `docs/`，各平台 SKILL 只链接过去（渐进式披露，减少重复与漂移）。

本仓库采用 **「一份主技能 + 多路径安装」**：

- **主技能（唯一维护源）**：仓库内 `.cursor/skills/pressure-skill/`（含 `SKILL.md`、`references/*.md`）。  
- **PR 同步**：修改向导或协议时，请同步 `.agents/skills/pressure-skill/`（若仓库内也保留副本）或通过安装脚本从主技能再复制；避免两处手写漂移。

**Claude Code / OpenClaw**：不要求单独维护第二份 `SKILL.md`；将上述目录**原样复制**到各产品用户技能目录即可（见 §2）。各产品的 **frontmatter 扩展字段**（如 `allowed-tools`）若与 Cursor 冲突，以 Cursor 副本为准；需要平台专用字段时，再考虑拆 `integrations/...` 薄封装（当前未拆）。

## 5. Claude Code / OpenClaw 安装要点

1. **克隆本仓库**到任意路径（含 `scripts/`、`pressure_skill/`、`.cursor/skills/pressure-skill/`）。  
2. **安装技能目录**（PowerShell，仓库根）：
   - 仅 Claude Code：`.\scripts\install_claude_code_skill.ps1`
   - 仅 OpenClaw：`.\scripts\install_openclaw_skill.ps1`
   - 全部：`.\scripts\install_pressure_skill.ps1`
3. **macOS / Linux**：`bash scripts/install_pressure_skill.sh`（参数见 `scripts/install_pressure_skill.sh` 头部注释）。  
4. **运行 Python**：`bundle_local.py`、`eval_local.py`、`uvicorn` 等必须在 **pressure.skill 仓库根**执行；`~/.claude/skills/pressure-skill` 里**没有** `scripts/`，只有向导与协议。  
5. **触发方式**：以 Claude Code / OpenClaw 当前版本文档为准（常见为技能名或 `/` 命令列表）；若未发现技能，确认安装路径与产品「技能扫描目录」一致。

## 6. 首次推送到 GitHub（备忘）

1. 确认 `.gitignore` 已排除 `.venv/`、`eval/rerank_weights.json`、大体量本地数据（如 `eval/cases_sourced.jsonl`、`eval/cases_casino_labeled.jsonl` 等，按你仓库策略）。  
2. `git status` 检查无意提交的密钥（`.env` 应忽略）；**首次提交若未配置全局用户名/邮箱**，可用 `git -c user.name=... -c user.email=... commit ...`（不写 `git config`），见 [CONTRIBUTING.md](CONTRIBUTING.md) 文末「首次推送」小节。  
3. 本地 `pytest` 通过后再 `git push`；CI 见 `.github/workflows/ci.yml`。  
4. 仓库 **About** 可粘贴 `README.md` 顶部 HTML 注释中的 Description 草稿；**Topics** 建议：`cursor`、`agentskills`、`fastapi`、`communication`、`negotiation`、`coaching`、`python`。
