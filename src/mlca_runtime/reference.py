"""Frozen generic no-AI comparison routines; all fitting uses the supplied fit recorder."""

import json
import pickle

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import mlca_runtime as rt


def read(path):
    return (
        pd.read_parquet(path)
        if path.suffix == ".parquet"
        else pd.read_csv(path, sep="\t" if path.suffix == ".tsv" else ",")
    )


def load(paths, name):
    matches = [p for key, p in paths.items() if key.endswith("/" + name)]
    if not matches:
        raise ValueError("Missing declared artifact: " + name)
    with matches[-1].open("rb") as stream:
        return pickle.load(stream)


def protocol(paths):
    return json.loads(paths["_protocol"].read_text())


def predictors(frame, spec):
    excluded = set(spec["columns"].values()) | set(spec["excluded_columns"]) | {spec.get("group_column")}
    return frame.drop(columns=[c for c in excluded if c in frame])


def labels(frame, spec):
    y = frame[spec["columns"]["target"]]
    return y.astype(str)


def preprocessor(X, survival=False):
    numeric = list(X.select_dtypes(include="number").columns)
    categorical = [c for c in X if c not in numeric]
    transformers = []
    if numeric:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            )
        )
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
                        (
                            "encode",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                sparse_output=False,
                                drop="first" if survival else None,
                            ),
                        ),
                    ]
                ),
                categorical,
            )
        )
    if not transformers:
        raise ValueError("No prediction columns remain after the recorded exclusions")
    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=True)


class Retain(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        return X


class CoxSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y):
        from lifelines import CoxPHFitter

        scores = []
        for index in range(X.shape[1]):
            values = np.asarray(X)[:, index]
            if np.std(values) < 1e-10:
                continue
            data = pd.DataFrame(
                {"feature": values, "duration": y.iloc[:, 0].to_numpy(), "event": y.iloc[:, 1].to_numpy()}
            )
            try:
                fit = CoxPHFitter(penalizer=0.0).fit(data, "duration", "event")
                p = float(fit.summary.loc["feature", "p"])
                if p < 0.10:
                    scores.append((p, index))
            except (ValueError, ArithmeticError):
                continue
        if not scores:
            raise ValueError("No covariate passed the prespecified Cox filter")
        self.selected_ = [i for _, i in sorted(scores)[:20]]
        return self

    def transform(self, X):
        return np.asarray(X)[:, self.selected_]


class SurvivalModel:
    def __init__(self, preprocess, selector, penalizer=0.0):
        self.preprocess, self.selector, self.penalizer = preprocess, selector, penalizer

    def fit(self, X, y):
        from lifelines import CoxPHFitter

        values = np.asarray(self.selector.transform(self.preprocess.transform(X)))
        self.keep_ = np.std(values, axis=0) > 1e-10
        if not self.keep_.any():
            raise ValueError("No varying Cox covariates remain")
        transformed = pd.DataFrame(
            values[:, self.keep_], columns=[f"x{i}" for i in range(int(self.keep_.sum()))]
        )
        transformed["_duration"] = y.iloc[:, 0].to_numpy()
        transformed["_event"] = y.iloc[:, 1].to_numpy()
        self.cox_ = CoxPHFitter(penalizer=self.penalizer, l1_ratio=0.5 if self.penalizer else 0)
        self.cox_.fit(transformed, "_duration", "_event")
        return self

    def transformed(self, X):
        values = np.asarray(self.selector.transform(self.preprocess.transform(X)))[:, self.keep_]
        return pd.DataFrame(values, columns=[f"x{i}" for i in range(values.shape[1])])

    def predict(self, X):
        return self.cox_.predict_partial_hazard(self.transformed(X)).to_numpy().ravel()


def outcome_survival(frame, spec):
    return frame[[spec["columns"]["target"], spec["columns"]["event_column"]]]


def primary(y, score, spec):
    if spec["task"]["type"] == "survival":
        from lifelines.utils import concordance_index

        return float(concordance_index(y.iloc[:, 0], -score, y.iloc[:, 1]))
    if spec["task"]["type"] == "binary":
        return float(roc_auc_score(y, score[:, 1]))
    return float(roc_auc_score(y, score, multi_class="ovr", average="macro"))


def scores(model, X, spec):
    return model.predict(X) if spec["task"]["type"] == "survival" else model.predict_proba(X)


def metrics(model, frame, spec, threshold=None):
    X = predictors(frame, spec)
    survival = spec["task"]["type"] == "survival"
    y = outcome_survival(frame, spec) if survival else labels(frame, spec)
    score = scores(model, X, spec)
    measured = {spec["task"]["primary_metric"]: primary(y, score, spec)}
    if survival:
        return measured, y, score, None
    if spec["task"]["type"] == "binary":
        positive = model.classes_[1]
        encoded = (y == positive).astype(int)
        if threshold is None:
            fpr, tpr, thresholds = roc_curve(encoded, score[:, 1])
            finite = np.isfinite(thresholds)
            threshold = float(thresholds[np.flatnonzero(finite)[np.argmax((tpr - fpr)[finite])]])
        predictions = (score[:, 1] >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(encoded, predictions, labels=[0, 1]).ravel()
        measured.update(
            pr_auc=float(average_precision_score(encoded, score[:, 1])),
            balanced_accuracy=float(balanced_accuracy_score(encoded, predictions)),
            brier=float(brier_score_loss(encoded, score[:, 1])),
            sensitivity=float(tp / (tp + fn)) if tp + fn else 0.0,
            specificity=float(tn / (tn + fp)) if tn + fp else 0.0,
        )
    else:
        measured["balanced_accuracy"] = float(
            balanced_accuracy_score(y, model.classes_[score.argmax(axis=1)])
        )
    return measured, y, score, threshold


def run(action, fit=None):
    paths = rt.inputs()
    spec = protocol(paths)
    seed = spec["seed"]
    rt.set_seed(seed)
    survival = spec.get("task", {}).get("type") == "survival"
    if action == "audit_schema":
        frame = read(paths[spec["primary_data"]])
        schema = {
            c: {
                "dtype": str(frame[c].dtype),
                "distinct": int(frame[c].nunique()),
                "missing": int(frame[c].isna().sum()),
                "constant": bool(frame[c].nunique() <= 1),
            }
            for c in frame
        }
        rt.save_table(
            pd.DataFrame([{"column": c, **values} for c, values in schema.items()]).head(50), "schema.json"
        )
        for key, value in [
            ("n_rows", len(frame)),
            ("n_columns", len(frame.columns)),
            ("missing.total", int(frame.isna().sum().sum())),
        ]:
            rt.record_fact_candidate(key, value, source="schema.json")
        return
    if action == "describe_distributions":
        frame = read(paths[spec["primary_data"]])
        rows = [
            {
                "column": c,
                "dtype": str(frame[c].dtype),
                "distinct": frame[c].nunique(),
                "missing": frame[c].isna().sum(),
                "mean": float(frame[c].mean()) if pd.api.types.is_numeric_dtype(frame[c]) else None,
                "std": float(frame[c].std()) if pd.api.types.is_numeric_dtype(frame[c]) else None,
            }
            for c in frame
        ]
        rt.save_table(pd.DataFrame(rows).head(50), "distributions.csv")
        rt.record_fact_candidate(
            "n_numeric", len(frame.select_dtypes(include="number").columns), source="distributions.csv"
        )
        rt.record_fact_candidate(
            "n_categorical",
            len(frame.columns) - len(frame.select_dtypes(include="number").columns),
            source="distributions.csv",
        )
        return
    train = read(paths["train"])
    X = predictors(train, spec)
    y = outcome_survival(train, spec) if survival else labels(train, spec)
    if action == "fit_preprocessing":
        fitted = fit(preprocessor(X, survival), X, "train")
        fitted.transform(predictors(read(paths["val"]), spec))
        rt.save_model(fitted, "preprocessor.pkl")
        return
    preprocess = load(paths, "preprocessor.pkl")
    if action in {"retain_features", "select_features"}:
        transformed = pd.DataFrame(preprocess.transform(X), index=X.index)
        selector = (
            Retain()
            if action == "retain_features"
            else CoxSelector()
            if survival
            else SelectKBest(f_classif, k=min(20, transformed.shape[1]))
        )
        fit(selector, transformed, "train", y)
        rt.save_model(selector, "selector_all.pkl" if action == "retain_features" else "selector.pkl")
        return
    try:
        selector = load(paths, "selector.pkl")
    except ValueError:
        selector = load(paths, "selector_all.pkl")
    if action in {"train_logistic", "train_cox", "train_alternative"}:
        alternative = action == "train_alternative"
        if survival:
            model = SurvivalModel(preprocess, selector, 0.1 if alternative else 0.0)
        else:
            classifier = (
                HistGradientBoostingClassifier(random_state=seed, class_weight="balanced")
                if alternative
                else LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed)
            )
            model = Pipeline([("preprocess", preprocess), ("selector", selector), ("model", classifier)])
        fit(model, X, "train", y)
        rt.save_model(model, "alternative_model.pkl" if alternative else "model.pkl")
        return
    if action == "score_validation":
        val = read(paths["val"])
        candidates = []
        for name in ["model.pkl", "alternative_model.pkl"]:
            try:
                model = load(paths, name)
            except ValueError:
                continue
            measured, _, _, threshold = metrics(model, val, spec)
            candidates.append((name, measured, threshold, model))
        if not candidates:
            raise ValueError("No fitted candidate model")
        chosen = max(candidates, key=lambda c: c[1][spec["task"]["primary_metric"]])
        rows = []
        for name, measured, threshold, _ in candidates:
            for metric, value in measured.items():
                rows.append({"model": name, "metric": metric, "value": value, "threshold": threshold})
                rt.record_metric(metric, value, "val")
        rt.save_table(pd.DataFrame(rows), "validation_metrics.csv")
        rt.save_json({"model": chosen[0], "threshold": chosen[2]}, "selection.json")
        rt.record_fact_candidate("best_model", chosen[0], source="validation_metrics.csv")
        rt.record_fact_candidate(
            "best_val_c_index" if survival else "best_val_roc_auc",
            chosen[1][spec["task"]["primary_metric"]],
            source="validation_metrics.csv",
        )
        if survival:
            from lifelines.statistics import proportional_hazard_test

            model = candidates[0][3]
            prepared = model.transformed(X)
            prepared["_duration"] = y.iloc[:, 0].to_numpy()
            prepared["_event"] = y.iloc[:, 1].to_numpy()
            ph = proportional_hazard_test(model.cox_, prepared, time_transform="rank").summary.reset_index()
            rt.save_table(ph.head(50), "proportional_hazards.csv")
        return
    selected = next(p for k, p in paths.items() if k.endswith("/selection.json"))
    choice = json.loads(selected.read_text())
    model = load(paths, choice["model"])
    if action == "score_test":
        test = read(paths["test"])
        measured, y, score, _ = metrics(model, test, spec, choice["threshold"])
        rng = np.random.default_rng(seed)
        bootstrap = []
        for _ in range(spec["bootstrap_resamples"]):
            index = rng.integers(0, len(test), len(test))
            try:
                bootstrap.append(primary(y.iloc[index], score[index], spec))
            except (ValueError, ZeroDivisionError):
                continue
        if len(bootstrap) < max(50, spec["bootstrap_resamples"] // 2):
            raise ValueError("Too few valid prespecified bootstrap resamples")
        low, high = np.percentile(bootstrap, [2.5, 97.5]).tolist()
        rows = []
        for metric, value in measured.items():
            ci = [low, high] if metric == spec["task"]["primary_metric"] else None
            rt.record_metric(metric, value, "test", ci)
            rows.append(
                {
                    "metric": metric,
                    "value": value,
                    "ci_low": ci[0] if ci else None,
                    "ci_high": ci[1] if ci else None,
                }
            )
        rt.save_table(pd.DataFrame(rows), "test_metrics.csv")
        if not survival:
            # Standard per-row test predictions (B-0037): no feature columns.
            predicted = pd.DataFrame(
                {
                    "row_id": test.index,
                    "partition": "test",
                    "y_true": y.to_numpy(),
                    "y_pred": model.predict(predictors(test, spec)),
                }
            )
            for k, label in enumerate(model.classes_):
                predicted[f"proba__{label}"] = score[:, k]
            rt.save_row_outputs(predicted, "test_predictions.parquet")
        rt.record_fact_candidate(
            "test_c_index" if survival else "test_roc_auc",
            measured[spec["task"]["primary_metric"]],
            source="test_metrics.csv",
        )
        return
    if action == "explain_model":
        val = read(paths["val"])
        X = predictors(val, spec)
        y = outcome_survival(val, spec) if survival else labels(val, spec)
        baseline = primary(y, scores(model, X, spec), spec)
        rng = np.random.default_rng(seed)
        rows = []
        for column in X:
            effects = []
            for _ in range(20):
                permuted = X.copy()
                permuted[column] = rng.permutation(permuted[column].to_numpy())
                effects.append(baseline - primary(y, scores(model, permuted, spec), spec))
            rows.append(
                {
                    "feature": column,
                    "importance_mean": float(np.mean(effects)),
                    "importance_sd": float(np.std(effects)),
                }
            )
        table = pd.DataFrame(rows).sort_values("importance_mean", ascending=False).head(15)
        rt.save_table(table, "interpretation.csv")
        rt.record_fact_candidate(
            "top_covariate" if survival else "top_feature",
            str(table.iloc[0]["feature"]),
            source="interpretation.csv",
        )
        return
    raise ValueError("Unsupported reference action: " + action)
