# Benchmark datasets

**Dataset work order 03, 15 October 2026:** these public tables form the development set for building MLCA's rails; the four held-out tables remain untouched until the agent freeze. See the [organized study design](../mlcagent-experiments/README.md) in the separate experiments repository and [`manifest.yaml`](manifest.yaml) for complete provenance, citations, licences, routes, counts, sizes and hashes. This directory documents data preparation only; it does not authorize benchmark runs.

All twelve new tables were downloaded from official UCI archive endpoints and converted with [`pull_benchmarks.py`](pull_benchmarks.py). The script needs pandas and openpyxl; use an isolated environment and keep its download cache outside the repository. It writes UTF-8, comma-separated CSVs with LF line endings and no index. It changes only the documented headers, joined official archive parts, Excel conversion, and delimiters. Reruns should reproduce byte-identical files.

## Development set

| Dataset | File | Problem type | Level | Rows × columns | Targets | Licence | Source |
|---|---|---|---|---:|---|---|---|
| Breast Cancer Wisconsin (Diagnostic) | `datasets/breast_cancer_diagnostic_uci.csv` | Binary classification | Simple | 569 × 31 | `Diagnosis` | CC BY 4.0 | [UCI 17](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) |
| Heart Disease (Cleveland) | `datasets/heart_disease_cleveland_uci.csv` | Binary classification | Simple | 303 × 15 | `heart_disease_binary` | CC BY 4.0 | [UCI 45](https://archive.ics.uci.edu/dataset/45/heart+disease) |
| Adult | `datasets/adult_census_uci.csv` | Binary classification | Complex | 48,842 × 15 | `income` | CC BY 4.0 | [UCI 2](https://archive.ics.uci.edu/dataset/2/adult) |
| Dry Bean | `datasets/dry_bean_uci.csv` | Multiclass classification | Medium | 13,611 × 17 | `Class` | CC BY 4.0 | [UCI 602](https://archive.ics.uci.edu/dataset/602/dry+bean+dataset) |
| Covertype | `datasets/covertype_uci.csv` | Multiclass classification | Complex | 581,012 × 55 | `Cover_Type` | CC BY 4.0 | [UCI 31](https://archive.ics.uci.edu/dataset/31/covertype) |
| Anuran Calls (MFCCs) | `datasets/anuran_calls_uci.csv` | Multi-label classification | Complex | 7,195 × 26 | `Family`, `Genus`, `Species`; group `RecordID` | CC BY 4.0 | [UCI 406](https://archive.ics.uci.edu/dataset/406/anuran+calls+mfccs) |
| Abalone | `datasets/abalone_uci.csv` | Regression | Simple | 4,177 × 9 | `Rings` | CC BY 4.0 | [UCI 1](https://archive.ics.uci.edu/dataset/1/abalone) |
| Bike Sharing (hourly) | `datasets/bike_sharing_hourly_uci.csv` | Regression | Complex | 17,379 × 17 | `cnt` | CC BY 4.0 | [UCI 275](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) |
| Energy Efficiency | `datasets/energy_efficiency_uci.csv` | Multi-output regression | Simple | 768 × 10 | `Y1`, `Y2` | CC BY 4.0 | [UCI 242](https://archive.ics.uci.edu/dataset/242/energy+efficiency) |
| Seeds | `datasets/seeds_uci.csv` | Clustering | Simple | 210 × 8 | `variety` evaluation only | CC BY 4.0 | [UCI 236](https://archive.ics.uci.edu/dataset/236/seeds) |
| Online Retail | `datasets/online_retail_uci.csv` | Clustering | Complex | 541,909 × 8 | None; transaction table | CC BY 4.0 | [UCI 352](https://archive.ics.uci.edu/dataset/352/online+retail) |
| Optical Recognition of Handwritten Digits | `datasets/optical_digits_uci.csv` | Representation learning | Medium | 5,620 × 65 | `digit` evaluation only | CC BY 4.0 | [UCI 80](https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits) |

The six original files remain unchanged. For heart disease, `num` is the source of the existing binary target `heart_disease_binary`. The legacy lung table has an all-zero `event` column; use `status`. The two survival tables remain outside the rails and are excluded from the development set.

## Held-out set

The four tables under [`heldout/`](heldout/README.md) are reserved until freeze. Before then, do not run, profile, preview, summarize or inspect them. At retrieval, only their row/column counts and hashes were recorded. Indicator validation for steel plates was skipped as required by the retrieval limit.

## Checksums and report

- [`datasets/SHA256SUMS.txt`](datasets/SHA256SUMS.txt) keeps the original six checksum lines and appends the eight development CSVs and the pull script.
- [`heldout/SHA256SUMS.txt`](heldout/SHA256SUMS.txt) covers the four reserved CSVs.
- [`DOWNLOAD_REPORT.md`](DOWNLOAD_REPORT.md) records all 18 tables, licences, routes, bytes, hashes, deviations and the held-out inspection boundary.

The four pre-existing UCI development tables are CC BY 4.0. The legacy survival tables remain unchanged; their license metadata were not present in the original dataset card and are marked as unrecorded in the manifest.
