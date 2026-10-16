from types import SimpleNamespace as NS

import pandas as pd
import pytest

from mlca.engine.split import freeze, partitions
from mlca.errors import MlcaUserError
from mlca.paths import sha256


def params():
    return dict(
        method="group_time",
        group_column="unit",
        time_columns=["time"],
        train_fraction=0.6,
        val_fraction=0.2,
        seed=42,
    )


def assert_constraints(frame, labels):
    assert set(labels) == {"train", "val", "test"}
    assert labels.groupby(frame.unit).nunique().max() == 1
    blocks = [frame.loc[labels.eq(x), "time"] for x in ["train", "val", "test"]]
    assert blocks[0].max() < blocks[1].min() and blocks[1].max() < blocks[2].min()
    assert labels.index.equals(frame.index)


def test_joint_constraints_and_seed_independence():
    frame = pd.DataFrame({"unit": [i // 3 for i in range(30)], "time": range(30)})
    frame = frame.sample(frac=1, random_state=3)
    labels = partitions(frame, params(), "")
    assert_constraints(frame, labels)
    pd.testing.assert_series_equal(labels, partitions(frame, {**params(), "seed": 9}, ""))


def test_overlapping_intervals_and_equal_timestamps_stay_together():
    frame = pd.DataFrame({"unit": ["a", "a", "b", "b", "c", "d", "e"], "time": [0, 3, 2, 4, 10, 10, 20]})
    labels = partitions(frame, params(), "")
    assert_constraints(frame, labels)
    assert labels[0] == labels[2] and labels[4] == labels[5]


def test_impossible_joint_constraints_refuse_without_random_fallback():
    frame = pd.DataFrame({"unit": ["a", "b", "c"] * 2, "time": [0, 1, 2, 10, 11, 12]})
    with pytest.raises(MlcaUserError, match="cannot form three"):
        partitions(frame, params(), "")
    with pytest.raises(MlcaUserError, match="complete declared"):
        partitions(frame.drop(columns="time"), params(), "")


def test_freeze_enforces_both_declared_constraints(tmp_path):
    frame = pd.DataFrame(
        {"unit": [i // 3 for i in range(30)], "time": range(30), "feature": [i % 2 for i in range(30)]}
    )
    source = tmp_path / "synthetic.csv"
    frame.to_csv(source, index=False)
    state = NS(
        split=None,
        primary_data="source",
        data={"source": {"name": "source", "original_path": str(source), "sha256": sha256(source)}},
        prepared_data=None,
        task={"autonomous": True, "time_columns": ["time"]},
        group_column="unit",
        template_id="clustering",
        project_id="synthetic-joint-test",
    )
    result = freeze(
        tmp_path,
        state,
        dict(method="group", seed=42, train_fraction=0.6, val_fraction=0.2),
        "split",
        lambda *_: None,
    )
    assert result["parameters"]["method"] == "group_time"
    manifest = pd.read_csv(tmp_path / result["manifest"]["path"]).set_index("row_id")
    assert_constraints(frame, manifest.partition)


def test_unused_categorical_groups_do_not_create_empty_intervals():
    frame = pd.DataFrame(
        {"unit": pd.Categorical([i // 3 for i in range(30)], categories=range(15)), "time": range(30)}
    )
    assert_constraints(frame, partitions(frame, params(), ""))
