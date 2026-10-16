"""One task-metric registry, shared by inference, execution and checks."""

DEFAULT_METRICS = {
    "binary": "roc_auc",
    "multiclass": "roc_auc_ovr",
    "regression": "rmse",
    "multioutput_regression": "rmse",
    "multilabel": "macro_f1",
    "clustering": "silhouette",
    "representation": "reconstruction_error",
    "survival": "c_index",
}
TEMPLATE_TASKS = {"tabular_classification": "binary", "multilabel_classification": "multilabel"}


def default_metric(task):
    return DEFAULT_METRICS.get(TEMPLATE_TASKS.get(task, task), "")


def normalize_metric(value):
    if not isinstance(value, str):
        return value
    value = value.strip().lower()
    return {"auc": "roc_auc", "f1_macro": "macro_f1"}.get(value, value)
