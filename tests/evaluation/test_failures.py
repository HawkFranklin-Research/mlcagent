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
