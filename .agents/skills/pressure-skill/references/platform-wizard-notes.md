# 多平台向导：同一份流程，不同「壳」

**pressure-skill** 的**业务向导**只有一份：`wizard-full-flow.md`（与本文件同目录）。无论你从 **Cursor、Claude Code、OpenClaw** 哪一侧挂上技能，Agent 都应先读完 `wizard-full-flow.md` 再按章节执行。

下列差异只影响「**怎么读到文件**」「**用户怎么触发**」「**Python 在哪跑**」，**不改变 §1～§11 的业务规则**。

---

## 1. 技能根目录（最重要）

记 **`SKILL.md` 所在目录** 为 **`<skill-root>`**（例如 `.../pressure-skill/`）。

- 向导正文路径永远是： **`<skill-root>/references/wizard-full-flow.md`**
- 本说明路径： **`<skill-root>/references/platform-wizard-notes.md`**

Agent 应用 **所在产品提供的「读文件」能力** 读取上述路径（见下表「读文件」列）。若无法解析绝对路径，可让用户在对话里粘贴 `wizard-full-flow.md` 全文（脱敏由用户负责）。

---

## 2. 各平台对照（安装后）

| 平台 | 常见 `<skill-root>`（用户级安装） | 用户如何挂上技能（以各产品 UI 为准） | 读文件（Agent） |
|------|-----------------------------------|----------------------------------------|-----------------|
| **Cursor** | `%USERPROFILE%\.cursor\skills\pressure-skill\` 或仓库内 `.cursor/skills/pressure-skill/` | Agent 里 **`/pressure-skill`** 或 Skills 列表选择 | 工具名常为 **Read**（与 Cursor 文档一致） |
| **Cursor `.agents`** | `%USERPROFILE%\.agents\skills\pressure-skill\` | 同上，以 Cursor 对 `.agents/skills` 的扫描为准 | 同上 |
| **Claude Code** | `%USERPROFILE%\.claude\skills\pressure-skill\`（macOS/Linux 为 `~/.claude/skills/pressure-skill`） | 技能名 / `/` 命令列表中的 **pressure-skill**（以 Anthropic 文档与版本为准） | 使用 Claude Code 文档中的 **Read** 或与 **Read** 等价的文件工具 |
| **OpenClaw** | `%USERPROFILE%\.openclaw\workspace\skills\pressure-skill\`（路径以你方产品文档为准） | 工作区内技能扫描 / 命令面板中的 **pressure-skill** | 使用该产品暴露的**读文件**工具（名称以文档为准） |

**仓库协作**：若工作区是 **pressure.skill 克隆根**，项目内副本一般为 `.cursor/skills/pressure-skill/`（或 `.agents/skills/pressure-skill/`，内容应与主技能同步）。

---

## 3. `bundle_local.py` / API（与向导分离）

- **向导 Markdown** 只存在于 `<skill-root>/references/`，**不含** `scripts/`。
- 运行 **`bundle_local.py`**、**`uvicorn`**、评测脚本时，**当前工作目录（cwd）** 须为 **pressure.skill 仓库根**（含 `scripts/`、`pressure_skill/` 的目录）。
- 若用户只在 IDE 里挂了用户目录技能、**未**打开仓库根：Agent 应提示用户 **另开终端 cd 到克隆根** 或 **把仓库作为工作区打开**，再执行脚本；不要假设 `<skill-root>` 下能 `python scripts/...`。

---

## 4. 给 Agent 的一句话备忘

1. 定位 **`<skill-root>`** = 当前加载的 `SKILL.md` 的父目录。  
2. **读取** `<skill-root>/references/wizard-full-flow.md`（及向导内要求的其它 `references/*.md`）。  
3. 需要跑 Python 时，cwd = **仓库克隆根**，不是 `<skill-root>`。
