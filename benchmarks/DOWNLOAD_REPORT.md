# Benchmark download report

Retrieved 2026-10-15 from official UCI archive endpoints. The 12 new CSVs were regenerated twice; all 12 SHA-256 values were byte-identical across runs. Counts below count data rows excluding the header and include every CSV column, including targets and evaluation-only columns. The four held-out files were only downloaded, converted, counted, sized, and hashed. No held-out values were profiled or previewed.

| File | Rows × columns | Bytes | SHA-256 | Licence | Route |
|---|---:|---:|---|---|---|
| `datasets/breast_cancer_diagnostic_uci.csv` | 569 × 31 | 121,248 | `5c2238c5d8c38eefbbe1238b1c88f25cdee5299ad5010eb2103dd4b1e6a1c715` | CC BY 4.0 | existing bundled CSV; unchanged; none |
| `datasets/heart_disease_cleveland_uci.csv` | 303 × 15 | 13,099 | `d60c1050744de47db797974b237c3eca6cccb58742b2ccd7c619bb99b581873e` | CC BY 4.0 | existing bundled CSV; unchanged; none |
| `datasets/adult_census_uci.csv` | 48,842 × 15 | 5,291,600 | `82682cd3606b1c0592975abff21db758baed235950a2a9c02931c56f1b8157ee` | CC BY 4.0 | existing bundled CSV; unchanged; none |
| `datasets/dry_bean_uci.csv` | 13,611 × 17 | 2,471,169 | `1330e4ccc5c54a925e43daf60d1409ac62dad2a21de9a25213765bee4b655787` | CC BY 4.0 | existing bundled CSV; unchanged; none |
| `datasets/covertype_uci.csv` | 581,012 × 55 | 75,170,064 | `ea35ca6820fcbe0bdc6707e9ed31e11a9de84f07d88da73b511c737383c271a6` | CC BY 4.0 | official archive covtype.data.gz; gzip decompressed; header from UCI variable table |
| `datasets/anuran_calls_uci.csv` | 7,195 × 26 | 3,181,655 | `8b161e8d8535b871043cce7ecb7a3496e4b8baef377f1fe9bd4bc91b6effca38` | CC BY 4.0 | official archive Frogs_MFCCs.csv; CSV reserialized with UTF-8 and LF line endings |
| `datasets/abalone_uci.csv` | 4,177 × 9 | 191,962 | `add76d88a9dd9c7a9f147dd005725ce19dbfdf352877df9d28703486742d35a2` | CC BY 4.0 | official archive abalone.data; header from UCI variable table |
| `datasets/bike_sharing_hourly_uci.csv` | 17,379 × 17 | 1,139,356 | `b03a2d02e8c10f435c43c7f0b358b7e34a003afea53dbc37f0183f2763295133` | CC BY 4.0 | official archive hour.csv; CSV reserialized with UTF-8 and LF line endings |
| `datasets/energy_efficiency_uci.csv` | 768 × 10 | 33,489 | `88fb36f0eb6f0afdab8602f84e67d0d631790a604d7fe9beeb531be97f4ef553` | CC BY 4.0 | official archive ENB2012_data.xlsx; first worksheet exported to CSV; original X1–X8/Y1–Y2 headings retained |
| `datasets/seeds_uci.csv` | 210 × 8 | 9,386 | `e175383dd58fb4d3f8f31a03e992c477c871fdeb4754d7a504f448cdcba2c0a3` | CC BY 4.0 | official archive seeds_dataset.txt; whitespace parsing; fixed header added from work order |
| `datasets/online_retail_uci.csv` | 541,909 × 8 | 47,226,068 | `4d857902cbcaec35ab41d0d9ea60061c9324d0f04f27c91ffb89467e391f0508` | CC BY 4.0 | official archive Online Retail.xlsx; first worksheet exported; identifier fields read as text; InvoiceDate ISO 8601 |
| `datasets/optical_digits_uci.csv` | 5,620 × 65 | 828,924 | `930be32b2f41719c00cd6b9f9fa9e5769adb81ac136fe43a0bbbe784425d61a8` | CC BY 4.0 | official archive optdigits.tra followed by optdigits.tes; 64 pixel headers and digit header added; original split column omitted |
| `heldout/bank_marketing_uci.csv` | 45,211 × 17 | 3,706,094 | `b44507c26634736d4a0619ec2d7c4b6ff56a2c63cbeb5176d3134e7b25e416f0` | CC BY 4.0 | official archive bank.zip, nested bank-full.csv; semicolon-delimited source reserialized as comma-delimited UTF-8 CSV; unknown retained as text |
| `heldout/steel_plates_faults_uci.csv` | 1,941 × 34 | 298,004 | `315b45ecd2b7ab441335dc83efa0daed49eb97e6eee59f9612b4b7a1048aeb03` | CC BY 4.0 | official archive Faults.NNA plus Faults27x7_var; whitespace matrix reserialized as CSV; variable names added from official file |
| `heldout/wine_quality_uci.csv` | 6,497 × 13 | 384,221 | `c0fca2ca864220c74a5ce85e63f8ba3cf11c401aa3dedfc4c3cca5f7a29d99cd` | CC BY 4.0 | official archive winequality-red.csv followed by winequality-white.csv; semicolon to comma; color inserted before quality |
| `heldout/wholesale_customers_uci.csv` | 440 × 8 | 14,580 | `d0213b7d856bc7f98f2f52a86bedb5cb57d5b8e19959605e75bd4532d4ee0896` | CC BY 4.0 | official archive Wholesale customers data.csv; CSV reserialized with UTF-8 and LF line endings |
| `datasets/lung_cancer_survival.csv` | 228 × 11 | 9,503 | `81ea4657fd9d95cff85c8924792ea0442fd1106f0e318378caddc4fee0982395` | Not recorded in legacy dataset card | existing bundled CSV; unchanged; none |
| `datasets/gbsg2_breast_cancer_survival.csv` | 686 × 10 | 21,819 | `695954dbed9eaa619f9854f6c945bdccf5b21b12ea3fb46bd28797b9e8284d49` | Not recorded in legacy dataset card | existing bundled CSV; unchanged; none |

## Deviations and notes

- The UCI Covertype page reports 54 features; the packaged CSV has 55 columns because it includes the `Cover_Type` target.
- The study-design table describes features separately from labels. The manifest and README report total CSV columns, including targets/evaluation-only fields: Anuran 26, optical digits 65, steel 34, wine 13, and wholesale customers 8.
- UCI metadata lists Bike Sharing as 17,389 instances; the official `hour.csv` archive contains 17,379 data rows, retained as published.
- The Energy Efficiency workbook includes its column names in the first row; these names were retained as the CSV header, producing 768 data rows × 10 columns.
- The downloaded Covertype CSV is 75,170,064 bytes (>50 MB). Online Retail is 47,226,068 bytes (under 50 MB). Covertype is the only new CSV above the requested threshold; author decision on Git LFS, compression, or download-only storage is pending.
- **Heldout steel check deviation:** the work order requested checking whether each row has exactly one fault indicator set. Per the explicit retrieval limit, indicator values were not checked and the count of violating rows is not reported. The recorded 1,941 × 34 count and hash are the only steel-table content checks.
- The two pre-existing survival files have no recorded license/citation in their legacy dataset card; they were left unchanged and marked as unrecorded in the manifest. The four pre-existing UCI classification tables cite their official UCI pages.
- No other difference from the requested expected row/column sizes was found using counts only for held-out data.

## Verification

- Dataset hashes: both `sha256sum -c` checks passed.
- Pull determinism: identical hashes before and after the second full script run for all 12 new CSVs.
- Existing-file preservation: the six pre-existing CSVs and their original checksum lines remain unchanged.
- `.mlca/` scan under `benchmarks/`: no matches.
- No MLCA commands, task cards, model calls, dataset analysis, or experiments were run. No commit, push, upload, or publication occurred.

## Files changed or added

- Updated `benchmarks/README.md`.
- Added `benchmarks/manifest.yaml`, `benchmarks/pull_benchmarks.py`, and `benchmarks/DOWNLOAD_REPORT.md`.
- Added eight CSVs under `benchmarks/datasets/` and appended their checksum records plus the pull-script hash to `benchmarks/datasets/SHA256SUMS.txt`; the six pre-existing checksum lines are preserved.
- Added `benchmarks/heldout/README.md`, `benchmarks/heldout/SHA256SUMS.txt`, and four heldout CSVs.
