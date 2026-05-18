---
name: pressure-skill
description: "Cold pressure → warm, sendable replies (ZH/EN). Layered workplace comms—deflect, nudge, pin vague specs—like a super mouthpiece that won't get you fired. Multi-platform Agent Skill (Cursor / Claude Code / OpenClaw) + FastAPI; offline templates. ZH: 拒绝被压力、拒绝职场PUA、反催办、不接锅、软拒绝、立边界。 EN: pushback, boundaries, anti-gaslighting, say-no."
disable-model-invocation: true
---

> **Language / 语言**  
> Supports **English and Chinese** (same pattern as many open skills): infer from the user’s **first substantive message** and stay in that language for questions and drafts unless they switch explicitly.  
> 支持**中文与英文**：根据用户**第一条实质性消息**判定语言，并**全程**使用同一语言；用户若明确切换语言则跟随。

# pressure.skill（多平台 Agent Skill）

> **轻松一句**：**冰冷压力 → 温暖回复**；像一套**立体攻防**替你守住边界，再当你的**超级嘴替**——把「再催我就鼠掉」翻译成**对方听得进、你发得出手**的版本。

## Agent 执行协议（最高优先级）

1. **定位技能根目录 `<skill-root>`**：即 **本 `SKILL.md` 所在目录**（无论装在仓库内 `.cursor/skills/pressure-skill/`、`.agents/skills/pressure-skill/`，还是用户目录下的 `~/.cursor/skills/pressure-skill`、`~/.claude/skills/pressure-skill`、`~/.openclaw/workspace/skills/pressure-skill` 等）。
2. **用户挂上本 Skill 后的第一条行动**：用**当前产品支持的读文件能力**读取  
   **`<skill-root>/references/wizard-full-flow.md`**  
   - **Cursor**：工具名一般为 **Read**。  
   - **Claude Code / OpenClaw**：使用文档中与 **Read** 等价的文件读取工具（名称以各版本为准）。  
   可选：先读 **`<skill-root>/references/platform-wizard-notes.md`**，了解多平台路径与 Python cwd 约定。
3. **若读取失败**（工作区未含该路径、或沙箱无法读盘）：请用户 **将 pressure.skill 仓库克隆根打开为工作区**、提供 `wizard-full-flow.md` 的磁盘路径，或 **将 `wizard-full-flow.md` 全文粘贴进对话**；在取得流程前 **不要编造**向导步骤。
4. **读完主向导后**：**严格按 `wizard-full-flow.md` 章节顺序**与用户多轮对话；除「快速通道」外，**禁止**在 **画像小结（§4）经用户确认前** 采集场景 A/B/C/D，**禁止**在 **用户声明目的（§5）前** 输出最终可发送话术定稿。  
5. **长期对象（复诊）**：用户要继续跟踪**同一位对方**、追加材料或反馈时，**再 Read** `<skill-root>/references/counterparty-long-term.md`；经用户同意后用仓库根 `scripts/counterparty_cli.py` 读写本地 `counterparties/`（默认不进 Git）。复诊时**仍须**每轮采集 **§5 目的** 与 **§6～7 新场景**。  
6. **收尾顺序**：遵循向导 **§10**——先问用户此刻最需要哪类产出并置顶作答，再写意图推测、**多假设意图**、**话术及对方可能反应**；科研/模糊对齐场景可按向导加载 `domain-artefact-cheatsheet.md`；**深证据**（`readiness.portrait_depth` = `deep`）时按向导加载 `evidence-based-reply-memo.md`。  
7. **语言**：遵循 `wizard-full-flow.md` 中的 **Language / 语言** 规则（中英一致）。

## 本文件其余内容（快速备忘）

- **隐私**：不默认写入仓库；提醒用户脱敏。  
- **双路径**：对话内可直接给建议（由**当前产品**绑定的模型执行）；**是否**在仓库根跑 `bundle_local.py` **由 Agent 按向导 §8 自行判断**（不向用户问工具名）；若跑，在用户话术里只用自然语言交代「做了信息结构化检查」。**若技能只装在用户目录**，向导仍在该 `<skill-root>/references/` 下；**Python 脚本**（`bundle_local.py`、`counterparty_cli.py` 等）必须在 **pressure.skill 仓库克隆根**（含 `scripts/`）执行。详见 **`platform-wizard-notes.md`** 与向导 **§8～§9**、长期档案 **`counterparty-long-term.md`**。  
- **readiness**：脚本/API 会输出信息是否够用；向导 **§10** 规定收尾顺序（先问产出优先级 → 再意图推测/话术/风险/追问）。  
- **工作目录**：运行脚本时 cwd 须为含 `scripts/` 的**仓库根**，不是 `<skill-root>`。  
- **多平台安装 / 排障**：见 [docs/skill-adapters.md](../../../docs/skill-adapters.md)。  
- **HTTP**：`uvicorn app:app`，接口见仓库 `README.md`。
