import shutil

import pytest
import yaml

from mlca.errors import MlcaUserError
from mlca.templates.loader import load
from mlca.templates.registry import get


@pytest.mark.parametrize("template", ["tabular_classification", "survival"])
def test_templates_cover_alternatives(template):
    workflow = get(template)
    for name in ("split", "features", "model"):
        check = workflow.events[name].subgoals[0].check.model_dump()
        assert len(check["any_of"]) == 2
    assert workflow.actions["count_target"].fact_candidates == []


@pytest.mark.parametrize("supporting", [False, True])
def test_primary_supporting_validation(tmp_path, supporting):
    folder = tmp_path / "template"
    shutil.copytree(get("tabular_classification").path, folder)
    file = folder / "actions/audit_schema.yaml" if supporting else folder / "actions/count_target.yaml"
    data = yaml.safe_load(file.read_text())
    data["role"] = "supporting" if supporting else "primary"
    file.write_text(yaml.safe_dump(data))
    with pytest.raises(MlcaUserError, match=f"events/data.yaml:.*{data['id']}"):
        load(folder)
