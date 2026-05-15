# 示例（脱敏）

本目录为 **示意结构**：真实输出请以本机运行 `scripts/bundle_local.py` 为准（`readiness.evidence_score` 会随 `--transcript-file`、侧写长度等变化）。

## 对比：有筹码/场外 vs 仅情境

| 文件 | 说明 |
|------|------|
| [sample-bundle-with-leverage.json](sample-bundle-with-leverage.json) | 含 `counterparty_notes`、`user_leverage_notes`、`extra_context_notes`；`readiness.missing_fields` 仍可能提示补聊天记录（模板演示）。 |
| [sample-bundle-thin-profile.json](sample-bundle-thin-profile.json) | 仅 `relation` + `user_purpose` + `situation`；`missing_fields` 会多出 **筹码/场外** 等缺口，便于对照「信息不足时系统会追问什么」。 |

## 复现命令（仓库根）

**较完整画像（与上表「有筹码」接近）：**

```bash
py -3 scripts/bundle_local.py --relation manager --use-llm false --locale auto ^
  --user-purpose "争取延期" ^
  --user-leverage "手头另有更高优先级项目已排满本周" ^
  --extra-context "领导更在意可预期的交付节奏而非单次通宵" ^
  --counterparty-notes "节奏快、讨厌模糊承诺" ^
  --situation "今天下班前必须交完整版"
```

**极简（与「thin」接近）：**

```bash
py -3 scripts/bundle_local.py --relation manager --use-llm false --locale auto ^
  --user-purpose "争取延期" ^
  --situation "今天下班前必须交完整版"
```

（Linux / macOS 将行尾 `^` 改为 `\`。）

## 科研「写明白」模糊对齐（可选参数）

```bash
py -3 scripts/bundle_local.py --relation elder --use-llm false --locale zh ^
  --user-purpose "对齐导师交付标准" ^
  --vague "PPT 写明白再讨论" ^
  --user-leverage "组会 ddl 在周五" ^
  --discipline-subfield "cs_theory" ^
  --artefact-preferences "定理、假设、指标推导为主"
```

输出中的 `clarify` 与 `readiness` 会随上述字段变化；可与向导里的 `domain-artefact-cheatsheet.md` 对照使用。
