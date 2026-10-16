from contextlib import closing

import pandas as pd
import pytest
from test_row_fingerprints import create_guard

import mlca_runtime
from mlca.autonomous.inference import Inference, StudyProposal
from mlca.privacy.rows import _CELL_MATCH_SQL
from mlca.runner.run_step import diagnostics


def proposal():
    return Inference(
        primary_data="sheet",
        problem_type="binary",
        targets=["label"],
        unit="Observation",
        repeated_subjects="No",
        reason="Predict an outcome",
    )


def test_explicit_wire_fields_and_historical_decode():
    schema = Inference.model_json_schema()
    assert set(schema["required"]) == set(schema["properties"])
    child = schema["$defs"]["StudyProposal"]
    assert set(child["required"]) == set(child["properties"])
    old = {
        "primary_data": "sheet",
        "problem_type": "binary",
        "targets": ["label"],
        "unit": "Observation",
        "repeated_subjects": "No",
        "reason": "Predict",
    }
    assert StudyProposal.model_validate(old).group_column is None
    with pytest.raises(ValueError, match="Explicit setup fields"):
        Inference.model_validate(old, context={"explicit_setup_fields": True})
    Inference.model_validate(proposal().model_dump(), context={"explicit_setup_fields": True})


def test_metric_refusals_are_value_free_and_explain_partitions():
    secret = "PRIVATE_COLUMN_VALUE"
    with pytest.raises(ValueError, match="MLCA: Metric partition") as error:
        mlca_runtime.record_metric("count", 3, secret)
    assert secret not in str(error.value)
    text = diagnostics({"stderr": "ValueError: " + str(error.value)}, False)
    assert "train, val, test or external" in text
    with pytest.raises(ValueError, match="MLCA: Metrics require a finite"):
        mlca_runtime.record_metric("score", float("nan"), "val")


@pytest.mark.parametrize(
    "error,hint",
    [
        (
            "ValueError: Unable to configure output for PRIVATE_VALUE() because set_output is not available",
            "custom transformer",
        ),
        (
            "AttributeError: Can't get attribute 'PRIVATE_VALUE' on <module '__main__'>",
            "local to an earlier script",
        ),
        (
            "ValueError: Some column names are not columns of the dataframe: {'PRIVATE_VALUE'}",
            "renamed or already-transformed",
        ),
    ],
)
def test_fixed_diagnostics_never_copy_source_values(error, hint):
    text = diagnostics({"stderr": error}, False)
    assert hint in text and "PRIVATE_VALUE" not in text


def legacy_verdict(guard, db, dataset, values, required):
    # Unit-test oracle for the unchanged bipartite matching semantics, not analysis code.
    candidates = {}
    for position, value in enumerate(values):
        for row, column in db.execute(
            _CELL_MATCH_SQL, (dataset, guard._digest(value, 6), dataset, guard._digest(value, 4))
        ):
            candidates.setdefault(row, {}).setdefault(position, set()).add(column)

    def enough(edges):
        owners = {}

        def assign(position, seen):
            for col in edges[position]:
                if col in seen:
                    continue
                seen.add(col)
                if col not in owners or assign(owners[col], seen):
                    owners[col] = position
                    return True
            return False

        return sum(assign(pos, set()) for pos in edges) >= required

    return any(enough(edges) for edges in candidates.values())


def test_streaming_verdict_matches_previous_distinct_cell_rule(tmp_path):
    import numpy as np

    rng = np.random.default_rng(42)
    frame = pd.DataFrame(rng.integers(0, 5, (25, 5)), columns=list("abcde"))
    frame["a"] = frame["a"] + 0.1234567
    guard, _ = create_guard(tmp_path / "study", frame)
    with closing(guard._connect()) as db:
        cases = [
            list(frame.iloc[0]),
            list(frame.iloc[0].round(4)),
            [0, 0, 0],
            [0, 8, 9],
            ["summary", "dtype", 0],
        ]
        cases += [list(rng.integers(0, 8, 5)) for _ in range(50)]
        for values in cases:
            assert guard._match_values(db, "registered:source", values, 3) == legacy_verdict(
                guard, db, "registered:source", values, 3
            )


def test_common_values_are_bounded_before_materialization(tmp_path):
    guard, _ = create_guard(tmp_path / "study", pd.DataFrame({f"x{i}": [0] * 1000 for i in range(6)}))
    with closing(guard._connect()) as db:

        class Traced:
            calls = []

            def execute(self, sql, parameters):
                self.calls.append(sql)
                return db.execute(sql, parameters)

        traced = Traced()
        assert not guard._match_values(traced, "registered:source", ["summary", "dtype", 0], 3)
        assert all("LIMIT 1" in sql for sql in traced.calls)
        assert guard._match_values(db, "registered:source", [0, 0, 0], 3)
        assert not guard._match_values(db, "registered:source", [0] * 7, 7)
