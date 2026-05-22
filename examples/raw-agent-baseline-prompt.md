# 裸问 Agent 基线（用于对比演示）

录制「对比式」视频时，**不要挂 pressure-skill**，在同一模型里粘贴下面任一提示（脱敏后替换括号内容）。

## 中文版（通用）

```text
我是（你的角色），对方是我的（上级/同事/客户）。
对方刚发来这句话：
「（粘贴对方原话，例如：今天下班前把完整版发我，别再拖了）」

我此刻最想达成：（例如：争取延期到周五，但不撕破脸）

请直接给我可以复制进微信/邮件发送的回复，2～3 条即可。
```

## 中文版（极简，容易得到空话）

```text
老板催我今天下班前交完整版，我怎么回复？请给建议。
```

## 对比时镜头上要看出

| 裸问常见结果 | pressure.skill 目标结果 |
|--------------|-------------------------|
| 段落长、偏「沟通原则」 | 2～3 条短消息体 |
| 少具体时间节点/筹码 | 嵌入你已提供的筹码与排期 |
| 无「对方可能怎么回」 | `reaction_hints` 或向导 §10 多假设 |
| 不提示信息不足 | `readiness.missing_fields` 会追问 |

## 同一输入跑 Skill 侧

仓库根：

```bash
py -3 scripts/bundle_local.py --relation manager --use-llm false --locale zh ^
  --user-purpose "争取延期" ^
  --user-leverage "手头另有更高优先级项目已排满本周" ^
  --extra-context "领导更在意可预期的交付节奏" ^
  --counterparty-notes "节奏快、讨厌模糊承诺" ^
  --situation "今天下班前必须交完整版"
```

或 Cursor 中 **`/pressure-skill`** 走完整向导（见 [demo-scenario-manager-deadline.md](demo-scenario-manager-deadline.md)）。
