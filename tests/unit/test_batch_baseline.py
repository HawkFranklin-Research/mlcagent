import os
import sys
import time

import pytest

from mlca.autonomous.inference import StudyProposal
from mlca.errors import MlcaUserError
from mlca.llm.deadline import exchange
from mlca.task_metrics import DEFAULT_METRICS, default_metric
from mlca.templates.registry import get


@pytest.mark.parametrize("given,expected", [("RMSE", "rmse"), (" auc ", "roc_auc"), ("f1_macro", "macro_f1")])
def test_equivalent_metric_aliases(given, expected):
    p = StudyProposal(
        primary_data="sheet",
        problem_type="regression",
        targets=["outcome"],
        primary_metric=given,
        unit="One observation",
        repeated_subjects="No",
        reason="Study",
    )
    assert p.primary_metric == expected


def test_registry_and_unknown_metric():
    for task, metric in DEFAULT_METRICS.items():
        assert default_metric(task) == metric
    assert default_metric("tabular_classification") == "roc_auc"
    with pytest.raises(ValueError):
        StudyProposal(
            primary_data="sheet",
            problem_type="binary",
            targets=["outcome"],
            primary_metric="accuracy",
            unit="One observation",
            repeated_subjects="No",
            reason="Study",
        )


def test_deadline_kills_transport(tmp_path):
    pid = tmp_path / "pid"
    code = f'import os,time;open({str(pid)!r},"w").write(str(os.getpid()));time.sleep(10)'
    start = time.monotonic()
    with pytest.raises(MlcaUserError) as error:
        exchange([sys.executable, "-c", code], {"key": "FAKE_CANARY"}, 0.2)
    assert error.value.category == "provider_error"
    assert time.monotonic() - start < 2
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid.read_text()), 0)


def test_transport_keeps_secrets_off_command_and_scrubs_other_keys(monkeypatch):
    monkeypatch.setenv("UNRELATED_API_KEY", "do-not-inherit")
    code = 'import os,sys,json;v=json.load(sys.stdin);print(json.dumps({"received":v["key"],"unrelated":os.environ.get("UNRELATED_API_KEY")}))'
    assert exchange([sys.executable, "-c", code], {"key": "FAKE_CANARY"}, 2) == {
        "received": "FAKE_CANARY",
        "unrelated": None,
    }


@pytest.mark.parametrize("template", ["clustering", "representation"])
def test_unsupervised_wording_and_action_methods(template):
    workflow = get(template)
    assert "target" not in [q["id"] for q in workflow.spec.brief_questions]
    assert workflow.actions["count_target"].title == "Count observations and feature types"
    assert "Stratified" not in workflow.actions["freeze_stratified"].title
    methods = [a.methods_text for a in workflow.actions.values()]
    assert len(methods) == len(set(methods))
    assert all("Follow the recorded task and saved model contract" not in text for text in methods)
