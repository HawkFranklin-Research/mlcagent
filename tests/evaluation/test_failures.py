import pytest

from mlca.api import Session
from mlca.errors import MlcaUserError
from mlca.evaluation.failures import CATEGORIES, enrich, execution_category


@pytest.mark.parametrize("category", sorted(CATEGORIES) + ["runtime_error:ValueError"])
def test_category_write_validation(project_factory, category):
    # No model call or step is needed to validate the persisted taxonomy.
    from mlca.log.schema import Record

    payload = enrich("Refusal", {"category": category, "operation": "test"})
    assert Record(type="Refusal", session_id="test", payload=payload).payload["category"] == category


def test_refusal_at_engine_and_execution_boundary(project_factory):
    with Session.open(project_factory(), mode="brain") as session:
        with pytest.raises(MlcaUserError):
            session.next()
        assert session.store.read()[-1].payload["category"] == "gate_blocked"
        session.custom("train a model")
        refusal = [
            r
            for r in session.store.read()
            if r.type.value == "ScopeDecision" and r.payload.get("decision") == "reject"
        ][-1]
        assert refusal.payload["category"] == "scope_layer1"
    for payload, expected in [
        ({"timed_out": True}, "timeout"),
        ({"stderr": "PermissionError: denied"}, "sandbox_denied"),
        ({"stderr": "ValueError: bad"}, "runtime_error:ValueError"),
    ]:
        assert execution_category(payload) == expected


def test_known_refusal_origins(tmp_path):
    from types import SimpleNamespace

    from mlca.errors import BudgetError
    from mlca.llm.egress import classify
    from mlca.runner.artefacts import collect
    from mlca_runtime import FitRuleError, fit_record

    with pytest.raises(MlcaUserError) as error:
        classify({}, ["sample_rows"], False)
    assert error.value.category == "privacy_refusal"
    assert BudgetError("budget").category == "budget_stop"
    with pytest.raises(FitRuleError):
        fit_record(None, None, "test")
    assert execution_category({"stderr": "mlca_runtime.FitRuleError: denied"}) == "fit_rule"
    step = tmp_path / "step"
    step.mkdir()
    (step / "outputs").mkdir()
    action = SimpleNamespace(outputs=[SimpleNamespace(name="missing.csv", required=True)], event="data")
    with pytest.raises(MlcaUserError) as error:
        collect(tmp_path, step, action, SimpleNamespace())
    assert error.value.category == "missing_output"
    action = SimpleNamespace(outputs=[], event="model")
    with pytest.raises(MlcaUserError) as error:
        collect(tmp_path, step, action, SimpleNamespace(split={"train_index_sha256": "test"}))
    assert error.value.category == "fit_rule"


def test_submitted_options_and_abandonment(project_factory):
    with Session.open(project_factory(), mode="brain") as session:
        with pytest.raises(MlcaUserError):
            session.submit_options([{"bad": "value"}])
        assert session.store.read()[-1].payload["category"] == "invalid_options"
        session.custom("Review the input data")
        session.abandon_step(session.active_step()["step_id"], "cannot proceed")
        assert session.store.read()[-1].payload["category"] == "abandoned"
    assert enrich("ScopeDecision", {"layer": 2, "decision": "reject"})["category"] == "scope_layer2"
