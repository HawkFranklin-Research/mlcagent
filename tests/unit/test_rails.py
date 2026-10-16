from types import SimpleNamespace as NS

import pytest
import yaml

from mlca.errors import IntegrityError, MlcaUserError
from mlca.rails import Rail, Rails, load, open_snapshot, snapshot


def spec(**changes):
    return {
        "id": "RL-0001",
        "kind": "instruction",
        "roles": ["worker"],
        "events": ["model"],
        "problem_types": ["regression"],
        "text": "Transform once.",
        "reason": "Avoid repeated transforms.",
        "ledger": "L-0001",
        "added_in": "rails-0.1",
        **changes,
    }


def write(path, data):
    path.mkdir(exist_ok=True)
    (path / "VERSION").write_text("rails-0.1\n")
    (path / "RL-0001.yaml").write_text(yaml.safe_dump(data))


def test_loader_and_scopes(tmp_path):
    write(tmp_path, spec())
    rails = load(tmp_path)
    assert "[RL-0001]" in rails.instructions("worker", "model", "regression")
    assert rails.instructions("navigator", "model", "regression") == ""
    assert rails.instructions("worker", "eda", "regression") == ""
    assert rails.instructions("worker", "model", "binary") == ""
    before = rails.sha256
    write(tmp_path, spec(text="Transform exactly once."))
    assert load(tmp_path).sha256 != before


@pytest.mark.parametrize(
    "changes",
    [
        {"extra": True},
        {"events": ["unknown"]},
        {"problem_types": ["unknown"]},
        {"check": "os.system"},
        {"id": "RL-0002"},
        {"roles": []},
    ],
)
def test_invalid_sets_refused(tmp_path, changes):
    write(tmp_path, spec(**changes))
    with pytest.raises((MlcaUserError, ValueError)):
        load(tmp_path)


def test_snapshot_anchored_and_legacy(tmp_path):
    root = tmp_path / "project"
    details = snapshot(root / ".mlca/rails")
    created = NS(payload={"rails": details})
    assert open_snapshot(root, created).sha256 == details["sha256"]
    (root / ".mlca/rails/VERSION").write_text("rails-0.99")
    with pytest.raises(IntegrityError):
        open_snapshot(root, created)
    assert open_snapshot(root, NS(payload={})).version == "rails-0.0"


def test_registered_check_firing(monkeypatch):
    from mlca.rails.checks import FUNCTIONS

    monkeypatch.setitem(FUNCTIONS, "mlca.rails.checks.synthetic", lambda _: (True, "Contract checked"))
    r = Rail.model_validate(
        spec(kind="check", roles=["engine"], text="", check="mlca.rails.checks.synthetic")
    )
    records = []
    session = NS(
        state=NS(task={"kind": "regression"}, current_event="model", template_id="regression"),
        emit=lambda kind, payload: records.append((kind, payload)),
    )
    Rails("rails-0.1", [r]).run(session, "after_step")
    assert not records
    Rails("rails-0.1", [r]).run(session, "before_step")
    assert records[0][0] == "RailFired" and records[0][1]["rail_id"] == r.id
