# 实地反馈闭环：发出去之后用真实对话校准画像（Agent 执行手册）

用户**已把上轮建议发进真实生活**，并带回**对方原话、反应、澄清模糊话后的真义**时，Read 本文件（可与 `counterparty-long-term.md` 联用）。

---

## 1. 触发

用户说例如：**我发了 / 对方回了 / 这是真实对话 / 和预测不一样 / 澄清后原来是要…**

→ 进入 **反馈闭环模式**（优先针对已存在的 **slug**；若无则先建档案或仅当轮分析不落盘）。

---

## 2. Agent 必做（对话内，≤2 轮问清）

向用户收集（脱敏），缺什么问什么，不要一次问 10 条：

| 字段 | 说明 |
|------|------|
| **sent_message** | 实际发出去的话（可与建议稿不同） |
| **counterparty_reply** | 对方原话回复 |
| **follow_up_thread** | 可选，后续几轮 |
| **vague_probe** / **vague_probe_reply** | 若去问了模糊要求，问法 + 对方澄清 |
| **actual_reaction_tags** | 如：接受、拖延、升级、甩锅、冷处理、抄送老板 |
| **prediction_match** | `right` / `partial` / `wrong`（相对上轮 §10 写的「可能反应」） |

并从**当轮上下文**回填 **advice_snapshot**：

- `user_purpose`、`predicted_reactions`（你上轮写的预测，或 `bundle_local.py --write-advice-snapshot tmp/advice_snapshot.json` 里的 `reaction_hints`）、`suggested_reply_text`（用户 adopted 的版本）

---

## 3. 偏差分析（Agent 推理，写进 JSON）

1. **对照**：上轮每条「可能反应」vs `actual_reaction_tags` / 原话。  
2. **意图再校准**：对方模糊话在实测下更可能属于哪条假设；**否定**至少 1 条旧假设。  
3. **deviation_summary**：3～6 句，写清错在哪、对在哪。  
4. **learned_rules**：2～5 条**可执行**规则（下次推断必须引用），例如「被点名 deadline 时会 cc 上级」。  
5. **profile_updates** / **pattern_tags_add** / **corrections**：把规则落到字段（见 `examples/feedback-outcome-template.json`）。

**禁止**无依据改写画像；每条 learned_rule 须能指回 `counterparty_reply` 或 `vague_probe_reply` 中的词。

---

## 4. 落盘（用户同意后）

1. 将上一步结构写入 `tmp/feedback_outcome.json`（可复制 `examples/feedback-outcome-template.json` 再填）。  
2. 在仓库根执行：  
   `py -3 scripts/counterparty_cli.py feedback --slug <slug> --feedback-file tmp/feedback_outcome.json`  
3. 向用户展示 **calibration_preview**（脚本输出）+ 你总结的 **下次会怎么变**（1～3 句）。  
4. 问是否**立刻进入新一轮会诊**（新目的 + 新场景）；复诊时 **必须 Read** 更新后的 `show` 输出中的 `outcomes` 与 `profile`。

`--no-apply-profile` 仅记录不测合并画像（一般不用）。

---

## 5. 下次推测如何使用校准

- `counterparty_cli.py show` 的 **outcomes** 最近几条 + **profile** 里 `[实测校准 …]` 块 → §10.1 **优先引用**。  
- 与旧假设冲突时：**以 outcomes 为准**，并提示用户是否还有新事实。  
- 对 **模糊话**：若存在 `vague_probe_reply`，优先用实测含义，勿重复已否定的解读。

---

## 6. 命令

```text
py -3 scripts/counterparty_cli.py feedback --slug <slug> --feedback-file tmp/feedback_outcome.json
```

模板：`examples/feedback-outcome-template.json`。
