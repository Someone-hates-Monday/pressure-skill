# 示例（脱敏）

本目录用于**说服与演示**：对比裸问、展示结构化输出、拍视频。完整说明见 **[docs/demo-and-trust.md](../docs/demo-and-trust.md)**。

## 固定演示案例（推荐引用）

| 文件 | 用途 |
|------|------|
| [demo-scenario-manager-deadline.md](demo-scenario-manager-deadline.md) | 上级催交付：口播稿 + 屏幕上该亮哪些字段 |
| [video-shot-list.md](video-shot-list.md) | 5～6 分钟分镜表 |
| [raw-agent-baseline-prompt.md](raw-agent-baseline-prompt.md) | 裸问 Agent 对比用提示词 |

## JSON 样例（含 `reaction_hints`）

| 文件 | 说明 |
|------|------|
| [sample-bundle-with-leverage.json](sample-bundle-with-leverage.json) | 含侧写、筹码、场外；`readiness` + `deflect` + **reaction_hints** |
| [sample-bundle-thin-profile.json](sample-bundle-thin-profile.json) | 仅情境+目的；`missing_fields` 更多，对比「信息不足」 |

刷新（仓库根）：`py -3 scripts/refresh_demo_samples.py`

## 对比：有筹码/场外 vs 仅情境

**较完整画像：**

```bash
py -3 scripts/bundle_local.py --relation manager --use-llm false --locale auto ^
  --user-purpose "争取延期" ^
  --user-leverage "手头另有更高优先级项目已排满本周" ^
  --extra-context "领导更在意可预期的交付节奏而非单次通宵" ^
  --counterparty-notes "节奏快、讨厌模糊承诺" ^
  --situation "今天下班前必须交完整版" ^
  --write-advice-snapshot tmp/advice_snapshot.json
```

**极简：**

```bash
py -3 scripts/bundle_local.py --relation manager --use-llm false --locale auto ^
  --user-purpose "争取延期" ^
  --situation "今天下班前必须交完整版"
```

（Linux / macOS 将行尾 `^` 改为 `\`。）

会诊结束后可将 `tmp/advice_snapshot.json` 与 [feedback-outcome-template.json](feedback-outcome-template.json) 合并，用于 **feedback 校准**。

## 科研「写明白」模糊对齐（可选）

```bash
py -3 scripts/bundle_local.py --relation elder --use-llm false --locale zh ^
  --user-purpose "对齐导师交付标准" ^
  --vague "PPT 写明白再讨论" ^
  --user-leverage "组会 ddl 在周五" ^
  --discipline-subfield "cs_theory" ^
  --artefact-preferences "定理、假设、指标推导为主"
```

可与向导 `domain-artefact-cheatsheet.md` 对照。
