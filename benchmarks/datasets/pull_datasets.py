"""
Pull canonical benchmark datasets from the UCI Machine Learning Repository and clinical survival sources.
Saves unified, ML-ready CSVs with clear feature and target definitions.
"""
import os
import pandas as pd
from ucimlrepo import fetch_ucirepo
import lifelines.datasets

OUT_DIR = "/home/prime/Documents/github/mlca-paper-codebases/benchmark_datasets"
os.makedirs(OUT_DIR, exist_ok=True)

manifest = []

# 1. Breast Cancer Wisconsin (Diagnostic) - UCI ID 17
print("--> Fetching Breast Cancer Wisconsin (Diagnostic)...")
try:
    bc = fetch_ucirepo(id=17)
    df_bc = pd.concat([bc.data.features, bc.data.targets], axis=1)
    # Target column is 'Diagnosis' (M = malignant, B = benign)
    target_col = bc.data.targets.columns[0]
    df_bc.to_csv(os.path.join(OUT_DIR, "breast_cancer_diagnostic_uci.csv"), index=False)
    manifest.append({
        "dataset": "Breast Cancer Wisconsin (Diagnostic)",
        "source": "UCI ML Repository (ID 17)",
        "file": "breast_cancer_diagnostic_uci.csv",
        "task": "Tabular Binary Classification",
        "rows": len(df_bc),
        "columns": len(df_bc.columns),
        "target": target_col,
        "description": "Biomedical diagnostic classification (Malignant vs Benign) based on 30 nuclear features."
    })
    print("    Saved:", len(df_bc), "rows,", len(df_bc.columns), "columns.")
except Exception as e:
    print("    Failed Breast Cancer:", e)

# 2. Heart Disease - UCI ID 45 (Cleveland clinical)
print("--> Fetching Heart Disease (Cleveland)...")
try:
    hd = fetch_ucirepo(id=45)
    df_hd = pd.concat([hd.data.features, hd.data.targets], axis=1)
    # Target is 'num' (0 = absence, 1-4 = presence). Create a binary diagnosis column as well
    target_col = hd.data.targets.columns[0]
    df_hd["heart_disease_binary"] = (df_hd[target_col] > 0).astype(int)
    df_hd.to_csv(os.path.join(OUT_DIR, "heart_disease_cleveland_uci.csv"), index=False)
    manifest.append({
        "dataset": "Heart Disease (Cleveland)",
        "source": "UCI ML Repository (ID 45)",
        "file": "heart_disease_cleveland_uci.csv",
        "task": "Tabular Binary/Multiclass Classification",
        "rows": len(df_hd),
        "columns": len(df_hd.columns),
        "target": "heart_disease_binary (or num)",
        "description": "Clinical diagnosis of coronary heart disease based on 13 physiological parameters (age, resting bp, cholesterol, ECG, etc.)."
    })
    print("    Saved:", len(df_hd), "rows,", len(df_hd.columns), "columns.")
except Exception as e:
    print("    Failed Heart Disease:", e)

# 3. Adult Census Income - UCI ID 2
print("--> Fetching Adult (Census Income)...")
try:
    adult = fetch_ucirepo(id=2)
    df_adult = pd.concat([adult.data.features, adult.data.targets], axis=1)
    target_col = adult.data.targets.columns[0]
    df_adult.to_csv(os.path.join(OUT_DIR, "adult_census_uci.csv"), index=False)
    manifest.append({
        "dataset": "Adult (Census Income)",
        "source": "UCI ML Repository (ID 2)",
        "file": "adult_census_uci.csv",
        "task": "Tabular Binary Classification (Mixed Continuous & Categorical)",
        "rows": len(df_adult),
        "columns": len(df_adult.columns),
        "target": target_col,
        "description": "Predict whether income exceeds $50K/yr based on census data (age, workclass, education, marital-status, occupation, etc.)."
    })
    print("    Saved:", len(df_adult), "rows,", len(df_adult.columns), "columns.")
except Exception as e:
    print("    Failed Adult:", e)

# 4. Dry Bean - UCI ID 602
print("--> Fetching Dry Bean Dataset...")
try:
    bean = fetch_ucirepo(id=602)
    df_bean = pd.concat([bean.data.features, bean.data.targets], axis=1)
    target_col = bean.data.targets.columns[0]
    df_bean.to_csv(os.path.join(OUT_DIR, "dry_bean_uci.csv"), index=False)
    manifest.append({
        "dataset": "Dry Bean Dataset",
        "source": "UCI ML Repository (ID 602)",
        "file": "dry_bean_uci.csv",
        "task": "Tabular Multiclass Classification",
        "rows": len(df_bean),
        "columns": len(df_bean.columns),
        "target": target_col,
        "description": "16 morphological features extracted from 13,611 bean grains across 7 registered bean cultivars."
    })
    print("    Saved:", len(df_bean), "rows,", len(df_bean.columns), "columns.")
except Exception as e:
    print("    Failed Dry Bean:", e)

# 5. NCCTG Lung Cancer (Survival Analysis)
print("--> Fetching NCCTG Lung Cancer (Survival Analysis)...")
try:
    df_lung = lifelines.datasets.load_lung()
    # columns: inst, time, status, age, sex, ph.ecog, ph.karno, pat.karno, meal.cal, wt.loss
    # status: 1 = censored, 2 = dead (often mapped to 0 = censored, 1 = event)
    df_lung["event"] = (df_lung["status"] == 2).astype(int)
    df_lung.to_csv(os.path.join(OUT_DIR, "lung_cancer_survival.csv"), index=False)
    manifest.append({
        "dataset": "NCCTG Lung Cancer",
        "source": "North Central Cancer Treatment Group (Mayo Clinic / lifelines)",
        "file": "lung_cancer_survival.csv",
        "task": "Survival Analysis (Time-to-Event)",
        "rows": len(df_lung),
        "columns": len(df_lung.columns),
        "target": "time, event (status)",
        "description": "Survival of patients with advanced lung cancer; evaluation of performance scores (ECOG, Karnofsky), age, sex, and weight loss."
    })
    print("    Saved:", len(df_lung), "rows,", len(df_lung.columns), "columns.")
except Exception as e:
    print("    Failed Lung Cancer:", e)

# 6. GBSG2 German Breast Cancer (Survival Analysis)
print("--> Fetching GBSG2 German Breast Cancer (Survival Analysis)...")
try:
    df_gbsg = lifelines.datasets.load_gbsg2()
    df_gbsg.to_csv(os.path.join(OUT_DIR, "gbsg2_breast_cancer_survival.csv"), index=False)
    manifest.append({
        "dataset": "German Breast Cancer Study Group (GBSG2)",
        "source": "Comprehensive Cancer Centers / lifelines",
        "file": "gbsg2_breast_cancer_survival.csv",
        "task": "Survival Analysis (Time-to-Event)",
        "rows": len(df_gbsg),
        "columns": len(df_gbsg.columns),
        "target": "time, cens",
        "description": "Node-positive breast cancer trial (686 patients) studying hormonal therapy, tumor size, progesterone/estrogen receptors, and nodes."
    })
    print("    Saved:", len(df_gbsg), "rows,", len(df_gbsg.columns), "columns.")
except Exception as e:
    print("    Failed GBSG2:", e)

# Save README.md in the folder
manifest_df = pd.DataFrame(manifest)
readme_path = os.path.join(OUT_DIR, "README.md")
with open(readme_path, "w") as f:
    f.write("# Benchmark Machine Learning Datasets\n\n")
    f.write("Pulled from the **UCI Machine Learning Repository** (`archive.ics.uci.edu`) and clinical survival sources.\n")
    f.write("Formatted as ready-to-use CSVs for testing `mlca`, scikit-learn, XGBoost, and survival models.\n\n")
    f.write("| Dataset | File | Task | Rows | Features | Target Column |\n")
    f.write("|---|---|---|---|---|---|\n")
    for m in manifest:
        f.write(f"| {m['dataset']} | `{m['file']}` | {m['task']} | {m['rows']:,} | {m['columns']} | `{m['target']}` |\n")
    f.write("\n## Dataset Details\n\n")
    for m in manifest:
        f.write(f"### {m['dataset']}\n")
        f.write(f"- **File:** `{m['file']}`\n")
        f.write(f"- **Source:** {m['source']}\n")
        f.write(f"- **Task:** {m['task']}\n")
        f.write(f"- **Target:** `{m['target']}`\n")
        f.write(f"- **Summary:** {m['description']}\n\n")

print("\nManifest successfully written to:", readme_path)
