"""Explicit no-AI baseline source. Never used as a Worker repair fallback."""

import json

from mlca.errors import MlcaUserError

PRIMARY = {
    "audit_schema",
    "describe_distributions",
    "fit_preprocessing",
    "retain_features",
    "select_features",
    "train_logistic",
    "train_cox",
    "train_alternative",
    "score_validation",
    "score_test",
    "explain_model",
}


class ReferenceSource:
    def script(self, action, params, inputs, state, step_id, previous, error):
        if error or action.id not in PRIMARY or "_protocol" not in inputs:
            raise MlcaUserError(
                "Reference arm supports guided primary actions only; never repairs Worker code"
            )
        source = "import mlca_runtime as rt\nfrom mlca_runtime.reference import run\n"
        if action.event in {"preprocess", "features", "model"}:
            source += "def fit_record(*args, **kwargs):\n    return rt.fit_record(*args, **kwargs)\n"
            source += "run(" + json.dumps(action.id) + ", fit_record)\n"
        else:
            source += "run(" + json.dumps(action.id) + ")\n"
        return source, None
