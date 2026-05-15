# 支持数据来源（有出处才入库）

本仓库 **不收录无出处的编造 case**。评测/训练用 jsonl 分两类：

| 文件 | 含义 |
|------|------|
| `eval/cases.jsonl` | 仓库种子集（项目内标注） |
| `eval/cases_sourced.jsonl` | **CaSiNo 拉取草稿**（`needs_review`；与 `cases_casino_labeled.jsonl` 合并后才参与训练） |
| `eval/cases_casino_labeled.jsonl` | **标注**：手写覆盖 `id`，或运行 `scripts/build_casino_labels_from_annotations.py` 从 parquet 的 `annotations` 生成（见 [CASINO_LABEL.md](CASINO_LABEL.md)） |
| `eval/raw/casino/casino.json` | CaSiNo 原始 JSON（[GitHub](https://github.com/kushalchawla/CaSiNo/blob/main/data/casino.json)） |

## CaSiNo（当前默认拉取源）

- **数据集**：[kchawla123/casino](https://huggingface.co/datasets/kchawla123/casino)（HuggingFace）
- **论文**：Chawla et al., *CaSiNo: A Corpus of Campsite Negotiation Dialogues*, NAACL 2021
- **内容**：英文露营地资源谈判对话（约 1k 对话），与职场不完全同分布，但可作为 **谈判/让步句式** 的真实语料来源
- **拉取**：

```bash
py -3 -m pip install datasets pyarrow
py -3 scripts/fetch_sourced_cases.py --backend github --dialogue-limit 80
# 若已手动下载 HF 的 parquet（如 data/train-00000-of-00001.parquet）：
py -3 scripts/fetch_sourced_cases.py --parquet data/train-00000-of-00001.parquet --dialogue-limit 0
```

生成：

- `eval/cases_sourced.jsonl` — 每条含 `annotation_meta.source=casino_naacl2021`、`needs_review=true`
- `eval/raw/casino/manifest.json` — 拉取记录

**注意**：`cases_sourced.jsonl` 单行默认 `target_signals` 为空。在 `cases_casino_labeled.jsonl` 中标注后，`train_rerank.py` 默认会把合并结果并入训练集（见 [CASINO_LABEL.md](CASINO_LABEL.md)）；可用 `--no-casino-labeled` 关闭。

## 其他可尝试来源（需自行下载 + `convert_dialogue_seed.py`）

| 来源 | 链接 | 许可 |
|------|------|------|
| Persuasion For Good | [ConvoKit](https://convokit.cornell.edu/datasets.html) | 研究用 |
| DailyDialog | [官网](http://yanran.li/dailydialog) | 研究用 |

## 网络

若 `huggingface.co` 超时，可设镜像后重试：

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
py -3 scripts/fetch_sourced_cases.py
```

## 导入 SQLite

审阅后的 jsonl：

```bash
py -3 scripts/import_external_cases.py --input eval/cases_sourced.jsonl --db eval/eval_runs.db --source casino_naacl2021
```
