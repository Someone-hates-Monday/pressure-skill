# CaSiNo 标注并入训练

## 文件

| 文件 | 作用 |
|------|------|
| `eval/cases_sourced.jsonl` | 由 `fetch_sourced_cases.py` 从 parquet / GitHub 生成，**未标注**行 `target_signals` 为空 |
| `eval/cases_casino_labeled.jsonl` | 已标注行（可只写 `id` + 信号）；可由脚本从官方 `annotations` 批量生成（见下） |

## 从 parquet 自动生成（推荐）

与 `fetch_sourced_cases.py --parquet` 使用**同一** `data/train-00000-of-00001.parquet` 时，按回合文本对齐 `annotations` 中的 dialog-act 标签，并映射为英文 **must/nice 子串**（与英文 deflect 模板 `_deflect_pool_en` 可匹配，供 rerank 训练打分）。

```bash
py -3 scripts/build_casino_labels_from_annotations.py
```

映射表见 `pressure_skill/eval_casino_label_map.py`。无标注对齐的短句（与 sourced 同规则 `len(text)<12` 已过滤）不会出现于 sourced；若某条 utterance 无 annotation 条目，则使用默认 `must/nice`。

## 两种行格式（手写覆盖）

### 1. 轻量覆盖（推荐）

`id` 必须与 `cases_sourced.jsonl` 中某条 **完全一致**（如 `casino_0_003`）。可覆盖：

`target_signals`、`must_have_signals`、`nice_to_have_signals`、`forbidden_substrings`、`mode`、`profile`、`text`、`rubric_notes`、`annotation_meta`

**至少**要有 `target_signals` 或 `must_have_signals` / `nice_to_have_signals` 之一非空，否则该行会被跳过。

示例（英文 CaSiNo 回合，信号自定）：

```json
{"id": "casino_0_003", "target_signals": ["firewood", "water", "deal"]}
```

```json
{"id": "casino_1_002", "must_have_signals": ["Food", "Water"], "nice_to_have_signals": ["Firewood"]}
```

### 2. 整行独立 case

含 `text`（≥4 字）、`mode`、且带有可训练信号时，**整行**直接加入训练集（不要求 id 存在于 sourced）。

## 训练

默认：`train_rerank.py` 在无 `--cases` 时加载 `eval/cases.jsonl`，并在 **`cases_casino_labeled.jsonl` 与 `cases_sourced.jsonl` 均存在** 时，把合并后的 CaSiNo 行追加到训练集。

```bash
py -3 scripts/train_rerank.py --iterations 600
```

显式传了 `--cases` 时，默认**不**再追加 CaSiNo；若要追加：

```bash
py -3 scripts/train_rerank.py --cases eval/cases.jsonl --include-casino-labeled
```

关闭 CaSiNo 合并：

```bash
py -3 scripts/train_rerank.py --no-casino-labeled
```

训练结束打印的 JSON 中含 `casino_train_rows`（以 `casino_` 开头的 id 条数）。
