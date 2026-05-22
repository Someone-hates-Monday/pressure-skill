# 演示、传播与「如何让人信服」

pressure.skill **不适合**用「像不像某个人」或单一准确率来证明自己。对外请用下面四类**可展示、可复核**的标准。

## 我们承诺什么（不承诺什么）

| 承诺 | 不承诺 |
|------|--------|
| 给出**能复制发送**的短稿（2～3 条） | 保证对方一定满意、一定延期成功 |
| 信息不足时 **`readiness` 会提示缺口** | 读心、替你做 HR 决策 |
| 每条稿附带 **`reaction_hints`**（可能反应） | 替代律师/正式投诉文书 |
| 发出去后可 **feedback 校准** 同一对象 | 无需你提供任何上下文也能完美 |

## 四类「可信展示」（视频 / README / Issue 通用）

### 1. 对比式（最有效）

同一情境，并排：

- **裸问 Agent**：「老板催今天下班前交完整版，我怎么回？」→ 通常更长、偏建议、难直接发送  
- **pressure.skill**：`/pressure-skill` 或 `bundle_local.py` → 短稿 + `reaction_hints`

裸问基线提示词见 [examples/raw-agent-baseline-prompt.md](../examples/raw-agent-baseline-prompt.md)。

### 2. 结构化式

录屏时露出 JSON 或 UI 中的字段（不必全屏）：

- `readiness.missing_fields` / `evidence_score` — 「先告诉你缺什么」  
- `deflect.reply_options[]` — 可发送正文  
- `deflect.reaction_hints[]` — `likely` / `unlikely` / `one_line`

示例文件（脱敏、可引用）：  
[examples/sample-bundle-with-leverage.json](../examples/sample-bundle-with-leverage.json)  
[examples/sample-bundle-thin-profile.json](../examples/sample-bundle-thin-profile.json)

刷新示例：`py -3 scripts/refresh_demo_samples.py`

### 3. 行为式（长期口碑）

用户真实路径：

1. 用 Skill 出稿 → **复制发送**  
2. 带回对方原话 → `counterparty_cli.py feedback`  
3. 下次复诊 → 画像含 `[实测校准]`，预测更贴  

模板：[examples/feedback-outcome-template.json](../examples/feedback-outcome-template.json)

欢迎用 GitHub Issue：**「使用反馈」**（见 `.github/ISSUE_TEMPLATE/user-feedback.yml`）。

### 4. 边界式

对 **上级 + 回怼** 等场景，输出会带 **风险说明**；宁可少给激进稿，也不假装无后果。

## 视频节奏（5～6 分钟参考）

| 时间 | 内容 |
|------|------|
| 0:00–0:25 | 催办截图 + 「删了又改」共情 |
| 0:25–1:00 | 安装 Skill（加速） |
| 1:00–4:00 | `/pressure-skill`：画像 → 目的 → 场景 → **一条推荐稿 + reaction_hints** |
| 4:00–4:40 | 与裸问对比（可选） |
| 4:40–5:10 | 发出去后 feedback 一句（可选） |
| 5:10–5:30 | GitHub + Quickstart |

分镜细则：[examples/video-shot-list.md](../examples/video-shot-list.md)  
完整案例文案：[examples/demo-scenario-manager-deadline.md](../examples/demo-scenario-manager-deadline.md)

## 30 秒让观众「敢试」

```bash
git clone https://github.com/Someone-hates-Monday/pressure-skill.git
cd pressure-skill
py -3 scripts/bundle_local.py --relation manager --use-llm false --user-purpose "争取延期" --situation "今天下班前必须交完整版"
```

无需 API Key；有 Cursor 则 `install_pressure_skill.ps1` 后 `/pressure-skill`。

## 与 colleague-skill 的区分（口播一句）

- **colleague-skill**：把某人蒸馏成 Skill（像不像、话题性强）  
- **pressure.skill**：高压场景出稿 + 预测反应 + 实地校准（实用、可复诊）
