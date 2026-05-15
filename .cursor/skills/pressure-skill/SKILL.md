---
name: pressure-skill
description: "Cold pressure → warm, sendable replies (ZH/EN). Layered workplace comms—deflect, nudge, pin vague specs—like a super mouthpiece that won't get you fired. Cursor skill + FastAPI; offline templates. Triggers: deadlines, pressure, vague asks, pressure.skill."
disable-model-invocation: true
---

> **Language / 语言**  
> Supports **English and Chinese** (same pattern as many open skills): infer from the user’s **first substantive message** and stay in that language for questions and drafts unless they switch explicitly.  
> 支持**中文与英文**：根据用户**第一条实质性消息**判定语言，并**全程**使用同一语言；用户若明确切换语言则跟随。

# pressure.skill（Cursor 实验版）

> **轻松一句**：**冰冷压力 → 温暖回复**；像一套**立体攻防**替你守住边界，再当你的**超级嘴替**——把「再催我就鼠掉」翻译成**对方听得进、你发得出手**的版本。

## Agent 执行协议（最高优先级）

1. **用户挂上本 Skill 后的第一条行动**：用 **Read** 读取与本文件同目录的  
   `references/wizard-full-flow.md`  
   若当前工作区是 **`压力.skill` 仓库根**，路径一般为：  
   `.cursor/skills/pressure-skill/references/wizard-full-flow.md`  
   （若 `.agents/skills/` 下也有同名技能，路径为 `.agents/skills/pressure-skill/references/wizard-full-flow.md`。）
2. **若 Read 失败**（例如未打开本仓库）：向用户说明——请 **打开 `压力.skill` 文件夹作为 Cursor 工作区**，或把 `wizard-full-flow.md` 全文粘贴进对话；在取得流程前 **不要编造**向导步骤。
3. **读完向导文件后**：**严格按其中章节顺序**与用户多轮对话；除「快速通道」外，**禁止**在 **画像小结（§4）经用户确认前** 采集场景 A/B/C/D，**禁止**在 **用户声明目的（§5）前** 输出最终可发送话术定稿。  
4. **收尾顺序**：遵循向导 **§10**——先问用户此刻最需要哪类产出并置顶作答，再写意图推测与追问；科研/模糊对齐场景可按向导加载 `domain-artefact-cheatsheet.md`；**深证据**（`readiness.portrait_depth` = `deep`）时按向导加载 `evidence-based-reply-memo.md`。  
5. **语言**：遵循 `wizard-full-flow.md` 中的 **Language / 语言** 规则（中英一致）。

## 本文件其余内容（快速备忘）

- **隐私**：不默认写入仓库；提醒用户脱敏。  
- **双路径**：对话内可直接给建议（Cursor 自带模型）；需要结构化 JSON 时在仓库根运行 `py -3 scripts/bundle_local.py ...`（详见向导 §6～§7）。**若技能只装在用户目录**（如 `~/.claude/skills/pressure-skill`），向导仍在该副本的 `references/` 下；**Python 脚本与 API** 必须在 **pressure.skill 仓库克隆根**（含 `scripts/`）执行。
- **readiness**：脚本/API 会输出信息是否够用；向导 **§10** 规定收尾顺序（先问产出优先级 → 再意图推测/话术/风险/追问）。  
- **工作目录**：运行脚本时 cwd 须为含 `scripts/` 的仓库根。  
- **多平台 / 安装 / 故障排查**：见 [docs/skill-adapters.md](../../../docs/skill-adapters.md)。  
- **HTTP**：`uvicorn app:app`，接口见仓库 `README.md`。
