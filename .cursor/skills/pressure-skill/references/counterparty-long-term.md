# 长期对象：对方画像的积累与复诊（Agent 执行手册）

本文件与 `wizard-full-flow.md` **配套**。当用户要**长期跟踪同一位沟通对象**、**复诊**、**追加材料/纠正画像**时，在读完主向导后 **必须 Read 本文件** 并按下列规则执行。

---

## 1. 产品定位（与单次向导的关系）

| 层次 | 内容 |
|------|------|
| **长期对象** | 一位对方（老板/客户/导师…）的 **CommunicationProfile** + 历史回合 + 用户纠正 |
| **单次会话** | 用户**此刻目的** + **新场景** A/B/C/D + 话术/意图推测（§5～§10） |
| **进化** | 新聊天记录、场外信息、反馈 → **合并进画像**，下次复诊更快、推断更稳 |

**禁止**把 `user_purpose` 写入长期 `profile.json`（目的每轮不同）；目的写入 **episode** 或仅留在当轮对话。

---

## 2. 本地存储（opt-in）

- 默认目录：**仓库根** `counterparties/{slug}/`（已在 `.gitignore`，**勿提交**真实人名与聊天）。  
- 用户拒绝落盘 → 仅当轮会话，不落库。  
- **Agent 不得**在未征得用户同意时写入 `counterparties/`。

| 文件 | 含义 |
|------|------|
| `meta.json` | 显示名、slug、创建/更新时间、会话次数 |
| `profile.json` | 可合并的画像字段（关系、侧写、筹码、场外、pattern 等） |
| `episodes.jsonl` | 每行一次「会诊」或 `kind=outcome_feedback` |
| `outcomes.jsonl` | **实地反馈**：已发送话术、对方真实回复、预测偏差、learned_rules |
| `corrections.md` | 用户纠正（「他不会这样」「其实更吃软」） |

---

## 3. 触发与首步

用户说例如：**继续上次 / 还是张老板 / 复诊 / 更新画像 / 追加聊天记录** → 进入 **复诊模式**。

1. 若工作区为 **pressure.skill 仓库根** 且可跑 Bash：  
   `py -3 scripts/counterparty_cli.py list`  
   展示已有 slug（显示名、session_count）；请用户选 **slug** 或 **新建**。
2. 加载：  
   `py -3 scripts/counterparty_cli.py show --slug <slug>`  
   将 `profile` 注入内部状态；**Read** `corrections.md` 全文（若 show 输出里 corrections_preview 不全，用 Read 读 `counterparties/<slug>/corrections.md`）。
3. 用 **3～5 句**复述已存画像 + 最近 1～2 条 episode 摘要，问用户要改什么或直接进入 **本轮新情况**。

**复诊时 §3 画像采集**：已有 `profile.json` 且用户未否定 → **压缩 §3**：只问「自上次以来有无新变化」或缺失项（≤2 问点），然后 **§4 小结确认**（必做）。**不可**跳过 §5 目的与 §6～7 新场景。

---

## 4. 单次会诊结束：沉淀

在 §10 产出且用户满意后，问一句（工作语言）：

> 要不要把本轮信息记进「{显示名}」的长期档案？（本地 `counterparties/`，默认不进 Git）

若同意：

1. 将当轮确认的画像字段写入临时 JSON（**不含** `user_purpose`），例如 `tmp/counterparty_profile_save.json`。  
2. 合并保存：  
   `py -3 scripts/counterparty_cli.py save --slug <slug> --name "<显示名>" --profile-file tmp/counterparty_profile_save.json`  
3. 追加 episode：  
   `py -3 scripts/counterparty_cli.py episode --slug <slug> --purpose "<本轮目的>" --scenes "deflect,clarify" --summary "<一句场景>" --outcome "<可选>" --usefulness <1-5> --note "<可选>"`  
4. 对用户只说：「已更新本地档案，下次提到 TA 可继续复诊。」

---

## 5. 进化模式

### 5A. 追加原材料

用户粘贴**新聊天记录**或补充侧写/筹码/场外 → 合并进 `profile.json`（`save` 默认 **merge**），并在对话中说明「已并入长期画像」。

### 5B. 对话纠正

用户说 **不对 / 他不会这样 / 其实是** →  

1. `py -3 scripts/counterparty_cli.py correction --slug <slug> --category portrait --text "<用户原话摘要>"`  
2. 把纠正**改写进** `counterparty_notes` 或对应字段，再 `save` 合并。  
3. **category** 可选：`portrait` | `leverage` | `context` | `pattern` | `other`。

### 5C. 反馈话术效果（简单）

用户仅口头说 **发了、对方怎样** 且不愿结构化 → 可只写 **episode** 的 `outcome` / `note` + **correction**。

### 5D. 实地反馈闭环（推荐：发出去之后）

用户带回**真实对话 + 对方反应 + 澄清模糊话后的含义** → **必须 Read** `references/counterparty-feedback-loop.md`，按其中步骤：

1. 对照上轮 **预测反应** vs **实际**；写 `deviation_summary` 与 `learned_rules`。  
2. 填 `tmp/feedback_outcome.json`（模板见 `examples/feedback-outcome-template.json`）。  
3. 运行 `counterparty_cli.py feedback --slug …` **合并进 profile**（生成 `[实测校准]` 块）。  
4. 下次复诊 **优先引用** `outcomes` 与校准块。

---

## 6. 复诊时的分析要求（对齐你的目标）

有长期画像时，§10.1 的 **对方意图推测** 必须：

- **优先引用** `profile.json`、`corrections.md`、**最近 `outcomes`（实地反馈）**、最近 episode 中的**具体事实**；  
- 对**模糊话**给出 **2～4 条互斥解读** + 相对可能性（与主向导 §10.1 一致）；  
- 对**各条回复建议**，简要标注 **对方可能反应**（接受 / 拖延 / 升级 / 甩锅）— 各 1 句即可，不必写剧本；  
- 若长期档案与本轮新事实冲突，**以本轮为准**并建议更新档案。

---

## 7. 新建对象

用户首次描述对方且无 slug：

1. 问 **花名/代号**（脱敏）→ `slug =` 脚本 `slugify` 或用户指定英文 slug。  
2. 走主向导 §3～§4 建画像；首次 **save** 用 `--no-merge` 或首次 save 即创建目录。  
3. 告知 slug，方便下次说「继续 {名字}」。

---

## 8. 命令速查（cwd = 仓库根）

```text
py -3 scripts/counterparty_cli.py list
py -3 scripts/counterparty_cli.py show --slug <slug>
py -3 scripts/counterparty_cli.py save --slug <slug> --name "<显示名>" --profile-file <path>
py -3 scripts/counterparty_cli.py episode --slug <slug> --purpose "..." --scenes "deflect" --summary "..."
py -3 scripts/counterparty_cli.py correction --slug <slug> --text "..." --category portrait
py -3 scripts/counterparty_cli.py feedback --slug <slug> --feedback-file tmp/feedback_outcome.json
```
