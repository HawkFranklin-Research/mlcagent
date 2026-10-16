import json

import pandas as pd
import pytest

from mlca.autonomous.inference import Inference, inventory, validate
from mlca.errors import MlcaUserError
from mlca.log.store import Store
from mlca.project.init import initialise
from mlca.project.labels import apply_label_map


def example(**changes):
    return Inference(
        primary_data="sheet",
        problem_type="binary",
        targets=["label"],
        unit="One observation",
        repeated_subjects="No",
        reason="Predict an outcome",
        **changes,
    )


def test_approved_values_numeric_summary_and_hidden_exclusion(tmp_path):
    data = tmp_path / "sheet.csv"
    pd.DataFrame(
        {"label": ["yes", "yes."] * 15, "number": range(30), "hidden": ["NEVER_TRANSMIT"] * 30}
    ).to_csv(data, index=False)
    schemas, _ = inventory([data], ["hidden"])
    assert "NEVER_TRANSMIT" not in json.dumps(schemas)
    cols = {c["name"]: c for c in schemas[0]["columns"]}
    assert cols["label"]["value_counts"] == [{"value": "yes", "count": 15}, {"value": "yes.", "count": 15}]
    assert cols["number"]["numeric_summary"]["quantiles"]["0.5"] == 14.5


def test_spelling_map_before_cardinality_and_no_source_mutation(tmp_path, monkeypatch):
    frame = pd.DataFrame({"label": ["yes", "yes.", "no", "no."], "feature": [1, 2, 3, 4]})
    data = tmp_path / "sheet.csv"
    frame.to_csv(data, index=False)
    original = data.read_bytes()
    mapping = {"label": {"yes.": "yes", "no.": "no"}}
    proposal = example(label_map=mapping, label_map_reason="Trailing punctuation denotes the same labels")
    assert validate(proposal, {"sheet": frame}).problem_type == "binary"
    assert frame.label.nunique() == 4

    def environment(root, packages):
        (root / ".mlca/requirements.lock").write_text("")
        from mlca.paths import sha256

        return {
            "packages": [],
            "lock_sha256": sha256(root / ".mlca/requirements.lock"),
            "runtime_sha256": "unused",
        }

    monkeypatch.setattr("mlca.project.init.create", environment)
    root = initialise(
        tmp_path / "project",
        [data],
        "tabular_classification",
        {"target": "label", "unit": "One row"},
        primary_data="sheet",
        label_map=mapping,
        label_map_reason=proposal.label_map_reason,
    )
    records = Store(root).read()
    record = next(r for r in records if r.type.value == "DataRegistered")
    assert record.payload["label_map"] == mapping
    registered = pd.read_parquet(record.payload["original_path"])
    assert registered.label.nunique() == 2
    assert data.read_bytes() == original


@pytest.mark.parametrize(
    "mapping,reason",
    [
        ({"label": {"yes": "no"}}, "Combine distinct outcomes"),
        ({"label": {"unknown": "yes"}}, "Unknown key"),
        ({"label": {"yes.": "YES"}}, "Destination not observed"),
        ({"feature": {"yes.": "yes"}}, "Non target"),
        ({"label": {"yes.": "yes"}}, ""),
    ],
)
def test_invalid_label_maps_refused(mapping, reason):
    frame = pd.DataFrame({"label": ["yes", "yes.", "no", "no."], "feature": [1, 2, 3, 4]})
    with pytest.raises(MlcaUserError):
        apply_label_map(frame, mapping, ["label"], reason)
