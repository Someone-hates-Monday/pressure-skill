# 演示案例：上级催「今天下班前交完整版」（脱敏）

用于视频口播、README 截图、线下分享。**请勿使用真实姓名与公司。**

## 情境卡片（给观众看 3 秒）

| 字段 | 示例值 |
|------|--------|
| 对方 | 张经理（上级） |
| 原话 | 「今天下班前把完整版发我，别再拖了。」 |
| 你的目的 | 争取延期到周五，不撕破脸 |
| 你的筹码 | 本周已排满更高优项目；可先交核心结论 |
| 场外 | 他更在意可预期节奏，单次通宵反而惹麻烦 |

## 向导里要说清的顺序（口播可照念）

1. 关系：上级  
2. 侧写：节奏快、讨厌模糊承诺  
3. 筹码 / 场外：（上表）  
4. **画像小结** → 请观众点头「没有」  
5. **目的**：争取延期（单独一问，必做）  
6. 场景：**A** 推脱 / 减量 / 延期  
7. 正文：粘贴原话 + 截止背景  

## 屏幕上建议高亮的一屏输出

从 [sample-bundle-with-leverage.json](sample-bundle-with-leverage.json) 取：

**推荐稿（示例第一条）**：

> 收到。为确保质量，我想和您对齐一下优先级：我手头还有 A、B 两项在本周截止。这份材料您更希望我先保证哪部分的深度？其余部分我可以在周五前给出框架，下周一补齐细节，您看是否可行？

**reaction_hints（示例）** — 展示 `one_line` 即可：

> 较可能：口头答应但留余地 / 拖延；较低可能：直接翻脸。

**可选第二屏** — `readiness.missing_fields`（说明「还会追问缺口」）：

- 聊天记录片段…（若你只给了情境也会提示补材料）

## 第二幕（可选，15 秒）：发出去之后

口播：「我发了第一条。他回：『周五中午前先看核心部分。』」

→ 填入 [feedback-outcome-template.json](feedback-outcome-template.json)  
→ `py -3 scripts/counterparty_cli.py feedback --slug zhang-mgr --feedback-file tmp/feedback.json`

口播：「下次还说张经理，Skill 会读 `[实测校准]`，预测更贴。」

## 结尾 CTA

- Star：https://github.com/Someone-hates-Monday/pressure-skill  
- 30 秒试：README [Quickstart](../README.md#quickstart)  
- 对比裸问：[raw-agent-baseline-prompt.md](raw-agent-baseline-prompt.md)
