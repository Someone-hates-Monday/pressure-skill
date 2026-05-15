# integrations

本仓库以 **`.cursor/skills/pressure-skill/`** 为技能唯一维护源（`SKILL.md` + `references/`，含 **`wizard-full-flow.md`** 与多平台备忘 **`platform-wizard-notes.md`**）。

跨 Agent 安装不放在此目录，而由脚本将上述文件夹复制到各产品用户目录：

| 脚本 | 说明 |
|------|------|
| `scripts/install_cursor_personal_skill.ps1` | Cursor + `%USERPROFILE%\.agents\skills` |
| `scripts/install_pressure_skill.ps1` | 上列 + Claude Code（`.claude/skills`）+ OpenClaw（`.openclaw/workspace/skills`） |
| `scripts/install_claude_code_skill.ps1` | 仅 Claude Code |
| `scripts/install_openclaw_skill.ps1` | 仅 OpenClaw |
| `scripts/install_pressure_skill.sh` | macOS / Linux，同上逻辑 |

详见 [docs/skill-adapters.md](../docs/skill-adapters.md)。
