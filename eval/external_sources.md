# 可接入外部语料方向（落地清单）

本项目已支持将外部语料先转为 `jsonl/csv`，再导入 SQLite：

```bash
py -3 scripts/import_external_cases.py --input <your_file.jsonl> --db eval/eval_runs.db --source <source_name>
```

## 推荐方向

1. **ConvoKit 语料生态（Cornell）**
   - 优点：对话结构化程度高，便于抽取角色与回合。
   - 用法：先在本地脚本中抽取你关心的场景为 `mode/text/profile/target_signals`。

2. **公开谈判/说服类语料**
   - 目标：补齐 “让步、条件交换、边界设定、催办” 话术模板。
   - 导入时建议：在 `profile_json` 中写入关系和场外约束（如 `relation`, `extra_context_notes`）。

3. **团队自建脱敏语料（优先级最高）**
   - 真实业务适配度最高。
   - 每条保留：
     - `mode`（deflect/push/clap_back）
     - `text`（原场景句）
     - `profile_json`（关系/筹码/场外）
     - `target_signals_csv`（你认定的有效信号词）

## 最小可用流程

1. 导入外部数据到 `eval/eval_runs.db`
2. 跑评测并保存 run：`scripts/eval_local.py --use-db-cases --save-run`
3. 用 `scripts/add_feedback.py` 记录人工反馈
4. 观察 `summary` 里的 **`avg_top_hit_ratio`（legacy）**、**`avg_top_weighted_score` / `avg_topk_weighted_score`（must/nice + 禁词）** 与人工反馈，再迭代模板与 `strategy_rerank.py`。`jsonl` 可写 `must_have_signals` / `nice_to_have_signals` / `forbidden_substrings`。

## 训练迭代（权重搜索）

在扩充的 `eval/cases.jsonl` 上运行：

```bash
py -3 scripts/train_rerank.py --iterations 600
py -3 scripts/eval_report.py --threshold 0.35
```

详见仓库根 `README.md`。
