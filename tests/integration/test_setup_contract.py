import json

import pandas as pd
import pytest
import yaml

from mlca.autonomous.inference import Inference, StudyProposal, infer
from mlca.autonomous.runner import run
from mlca.errors import MlcaUserError
from mlca.llm.usage import read


def response(**changes):
    return {
        "primary_data": "sheet",
        "problem_type": "binary",
        "targets": ["label"],
        "unit": "One observation",
        "repeated_subjects": "No",
        "reason": "Predict an outcome",
        "alternatives": [],
        **changes,
    }


def configuration(tmp_path, replies):
    path = tmp_path / "responses.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "responses": [
                    {
                        "match": {"role": "navigator", "purpose": "inference"},
                        "response": reply,
                        "input_tokens": 123,
                        "output_tokens": 12,
                    }
                    for reply in replies
                ]
            }
        )
    )
    return {
        "providers": {"fake": {"kind": "fake", "script": str(path)}},
        "roles": {r: {"provider": "fake", "model": "scripted"} for r in ["navigator", "worker"]},
    }


@pytest.mark.parametrize(
    "bad",
    [
        response(primary_metric="accuracy"),
        response(
            alternatives=[{"problem_type": "regression", "targets": ["measure"], "aim": "Another study"}]
        ),
        response(targets=["not_a_column"]),
        response(problem_type="multiclass", primary_metric="roc_auc_ovr"),
    ],
)
def test_invalid_contract_is_repaired_locally_without_sending_rows(tmp_path, bad):
    data = tmp_path / "sheet.csv"
    pd.DataFrame({"measure": ["RAW_SENTINEL_ONE", "RAW_SENTINEL_TWO"] * 2, "label": [0, 1, 0, 1]}).to_csv(
        data, index=False
    )
    alternative = StudyProposal(
        primary_data="sheet",
        problem_type="clustering",
        unit="One observation",
        repeated_subjects="No",
        reason="Explore groups",
    )
    good = response(alternatives=[alternative.model_dump()])
    evidence = tmp_path / "setup"
    result, _, _, _ = infer([data], "", configuration(tmp_path, [bad, good]), evidence)
    assert result.targets == ["label"]
    assert isinstance(result.alternatives[0], StudyProposal)
    assert len(read(evidence)) == 2
    requests = [json.loads(f.read_text())["request"] for f in (evidence / ".mlca/llm").glob("*.json")]
    assert all("RAW_SENTINEL" not in json.dumps(r) for r in requests)
    assert all("validation_context" not in r for r in requests)


def test_failed_setup_has_known_usage_in_aggregates(tmp_path):
    data = tmp_path / "sheet.csv"
    pd.DataFrame({"measure": [1, 2, 3, 4], "label": [0, 1, 0, 1]}).to_csv(data, index=False)
    bad = response(alternatives=[{"problem_type": "clustering"}])
    out = tmp_path / "out"
    result = run(data, out, config=configuration(tmp_path, [bad, bad]))
    assert result["runs"][0]["category"] == "invalid_inference"
    assert result["runs"][0]["setup_usage"]["model_requests"] == 2
    summary = json.loads((out / "bench_summary.json").read_text())
    assert summary["tokens"]["input_tokens"]["mean"]["value"] == 246
    assert summary["tokens"]["output_tokens"]["mean"]["value"] == 24
    assert summary["tokens"]["cost_usd"]["mean"]["value"] == 0
    assert summary["autonomy"]["model_reported_distribution"]["scripted"]["value"] == 2
    assert summary["time"]["llm_s"]["mean"]["value"] is not None
    assert summary["time"]["compute_s"]["mean"]["value"] is None


def test_alternative_schema_is_complete_and_nonrecursive():
    schema = Inference.model_json_schema()
    alternative = schema["$defs"]["StudyProposal"]
    assert {"primary_data", "unit", "repeated_subjects", "reason"} <= set(alternative["required"])
    assert "alternatives" not in alternative["properties"]
    with pytest.raises(MlcaUserError):
        from mlca.autonomous.inference import validate

        validate(
            Inference.model_validate(response(problem_type="multiclass")),
            {"sheet": pd.DataFrame({"label": [0, 1]})},
        )
