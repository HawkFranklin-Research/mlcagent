import pytest

from mlca.engine.checks import evaluate
from mlca.log.schema import ProjectState
from mlca.paths import sha256


@pytest.mark.parametrize("any_of", [True, False])
def test_output_exists_any_of(tmp_path, any_of):
    output = tmp_path / ".mlca/steps/s/outputs/split.json"
    output.parent.mkdir(parents=True)
    output.write_text("{}")
    state = ProjectState(
        generations={"split": 1},
        steps=[
            {
                "status": "completed",
                "action_id": "freeze_group",
                "event_id": "split",
                "generation": 1,
                "outputs": [
                    {
                        "name": "split.json",
                        "path": str(output.relative_to(tmp_path)),
                        "sha256": sha256(output),
                    }
                ],
            }
        ],
    )
    spec = {"type": "output_exists", "action": "freeze_group", "output": "split.json"}
    if any_of:
        spec = {
            "type": "output_exists",
            "any_of": [
                {"action": "freeze_stratified", "output": "split.json"},
                {"action": "freeze_group", "output": "split.json"},
            ],
        }
    assert evaluate(spec, state, tmp_path, event_id="split")[0]
    state.generations["split"] = 2
    assert not evaluate(spec, state, tmp_path, event_id="split")[0]
    state.generations["split"] = 1
    output.write_text("changed")
    assert not evaluate(spec, state, tmp_path, event_id="split")[0]
    state.steps[0]["status"] = "failed"
    assert not evaluate(spec, state, tmp_path, event_id="split")[0]
