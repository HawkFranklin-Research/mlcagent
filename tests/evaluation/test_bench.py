import json
from pathlib import Path

import pytest
import yaml

from mlca.evaluation.bench import run, summarize


def test_missing_run_metrics_are_not_consistent_decisions(tmp_path):
    (tmp_path / "bench.json").write_text(
        json.dumps(
            {"runs": [{"project": "run-001", "status": "failed"}, {"project": "run-002", "status": "failed"}]}
        )
    )
    summary = summarize(tmp_path)
    consistency = summary["decision_consistency"]
    assert consistency["exact_sequences"] == {"value": None, "source": "unavailable"}
    assert consistency["unavailable_sequences"]["value"] == 2
    assert consistency["pairwise"]["mean"]["value"] is None


@pytest.mark.parametrize("forced_failure", [False, True])
def test_three_independent_runs(project_factory, tmp_path, monkeypatch, forced_failure):
    import mlca.evaluation.bench as bench

    prototype = project_factory()
    settings = yaml.safe_load((prototype / ".mlca/project.yaml").read_text())
    card = {
        "data": [str(prototype.parent / "synthetic.csv")],
        "brief": yaml.safe_load((Path(__file__).parents[1] / "fixtures/synthetic_brief.yaml").read_text()),
        "config": settings["config"],
        "approval_policy": {"confirm_subgoals": True, "unlock_test": True},
    }
    path = tmp_path / "card.yaml"
    path.write_text(yaml.safe_dump(card))
    if forced_failure:
        original = bench.drive

        def drive(session, *args):
            if session.root.name == "run-002":
                raise bench.MlcaUserError("forced fixture failure", category="timeout")
            return original(session, *args)

        monkeypatch.setattr(bench, "drive", drive)
    out = tmp_path / "bench"
    manifest = run(path, 3, out)
    summary = summarize(out)
    assert len(manifest["runs"]) == 3
    assert summary["completion_rate"]["value"] == (2 / 3 if forced_failure else 1)
    assert (out / "run-002/.mlca/log/events.jsonl").exists()
    assert summary["interventions"]["human"]["mean"]["value"] == 0
    assert summary["interventions"]["policy"]["mean"]["value"] > 0
    for entry in manifest["runs"]:
        m = json.loads((out / entry["project"] / "reports/generated/metrics.json").read_text())
        assert m["run"]["task_card_sha256"] == manifest["task_card_sha256"]
        assert all(d["principal"].startswith("user:policy/") for d in m["decisions"])
    with pytest.raises(Exception, match="fresh empty"):
        run(path, 3, out)
