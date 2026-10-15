# Benchmarks: datasets for `mlca bench`

> **15 October 2026 (organized plan, `../plan.md`):** these tables start the **development set** on which the agent's rails are built: about 10 tables, simple and complex, covering binary, multiclass and multi-label classification, regression, clustering and representation learning, plus 2–3 **held-out** tables kept apart and run only after the freeze. The four classification tables below join the development set; the two survival tables leave it, because survival is evaluated outside the rails. The final list (and possibly a new folder name) is still to be decided.

Six small public tables (7.7 MB) on which `mlca bench` measures MLCA as an agent with built-in templates and choices. They are copied unchanged (SHA-256 in `datasets/SHA256SUMS.txt`) from the former `mlca-paper-codebases/benchmark_datasets/`, now archived. `datasets/pull_datasets.py` regenerates them.

| File | Template | Rows × columns | Outcome |
|---|---|---|---|
| `breast_cancer_diagnostic_uci.csv` | `tabular_classification` | 569 × 31 | `Diagnosis` (M/B) |
| `heart_disease_cleveland_uci.csv` | `tabular_classification` | 303 × 15 | `heart_disease_binary`; `num` is its source (leakage if kept) |
| `adult_census_uci.csv` | `tabular_classification` | 48,842 × 15 | `income` (4 spellings of 2 classes) |
| `dry_bean_uci.csv` | `tabular_classification` (multiclass) | 13,611 × 17 | `Class` (7) |
| `lung_cancer_survival.csv` | `survival` | 228 × 11 | duration `time`, event **`status`**. The `event` column is all zeros, a known defect of `pull_datasets.py` l. 108; do not use it |
| `gbsg2_breast_cancer_survival.csv` | `survival` | 686 × 10 | duration `time`, event `cens` |

**Sources:** UCI Machine Learning Repository (IDs 17, 45, 2, 602); NCCTG lung and GBSG2 via lifelines / R survival data.

**Licence:** the UCI datasets are distributed under CC BY 4.0 (attribution required). The licences of the two survival tables must be checked before any public release. These files are not included in the PyPI wheel.

Task cards, model runs and results are **not** kept here. They live in the experiments repository (`../../mlcagent-experiments/bench/`; future `HawkFranklin-Research/mlcagent-experiments`).
