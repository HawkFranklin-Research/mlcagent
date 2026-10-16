from types import SimpleNamespace as NS

import pytest

from mlca.autonomous.runner import drive, resume, run
from mlca.autonomous.windows import DecisionWindow
from mlca.errors import MlcaUserError


def test_questions_and_approvals_use_windows_and_policy():
    records, answers, confirmations = [], [], []
    turns = iter(
        [
            {"reason": "question"},
            {"reason": "approval", "turn": [{"id": "human:confirm:brief"}]},
            {"reason": "completed"},
        ]
    )
    s = NS(
        decision_window=DecisionWindow(0),
        principal="user:policy/0123456789ab",
        is_policy=True,
        progress_callback=None,
        autopilot=lambda *_: next(turns),
        questions=lambda: [{"question_id": "q1", "recommended": 1, "options": [{}, {}]}],
        emit=lambda kind, payload, **kw: records.append((kind, payload)),
        answer_question=lambda *args: answers.append(args),
        confirm=lambda *args: confirmations.append(args),
    )
    drive(s)
    assert answers == [("q1", 1)]
    assert confirmations[0][0] == "brief"
    assert [p["kind"] for k, p in records if k == "DecisionWindowOpened"] == ["question", "approval"]
    assert any(k == "QuestionAutoResolved" for k, p in records)


def test_provider_cooldown_is_bounded_and_not_a_rail():
    records, answers, sleeps = [], [], []
    turns = iter([{"reason": "failure"}, {"reason": "completed"}])
    store = NS(read=lambda: [NS(payload={"category": "provider_error"})])
    s = NS(
        decision_window=DecisionWindow(0),
        principal="user:policy/0123456789ab",
        is_policy=True,
        progress_callback=None,
        store=store,
        autopilot=lambda *_: next(turns),
        emit=lambda kind, payload, **kw: records.append((kind, payload)),
        questions=lambda: [
            {
                "question_id": "retry",
                "recommended": 0,
                "options": [{"effect": {"kind": "pause"}}, {"effect": {"kind": "retry"}}],
            }
        ],
        answer_question=lambda *args: answers.append(args),
    )
    drive(s, cooldown_s=10, sleep=sleeps.append)
    assert sleeps == [10]
    assert answers == [("retry", 1)]
    assert not any(k == "RailFired" for k, _ in records)


def test_terminal_failure_keeps_category():
    s = NS(
        decision_window=DecisionWindow(0),
        autopilot=lambda *_: {"reason": "failure"},
        store=NS(read=lambda: [NS(payload={"category": "fit_rule"})]),
    )
    with pytest.raises(MlcaUserError) as exc:
        drive(s, max_cooldowns=0)
    assert exc.value.category == "fit_rule"


def test_fresh_repeated_setup_failures_retained(tmp_path, monkeypatch):
    import pandas as pd

    import mlca.autonomous.runner as runner

    data = tmp_path / "table.csv"
    pd.DataFrame({"x": [1, 2, 3], "y": [0, 1, 0]}).to_csv(data, index=False)
    calls = []

    def fail(*args, **kwargs):
        calls.append(args[3])
        args[3].mkdir()
        raise MlcaUserError("bad proposal", category="invalid_inference")

    monkeypatch.setattr(runner, "infer", fail)
    result = run(data, tmp_path / "out", runs=2)
    assert [r["project"] for r in result["runs"]] == ["run-001", "run-002"]
    assert all(r["category"] == "invalid_inference" for r in result["runs"])
    assert len(set(calls)) == 2
    with pytest.raises(MlcaUserError, match="fresh"):
        run(data, tmp_path / "out")


def test_agent_cannot_start_human_policy():
    s = NS(principal="agent:test/1", mode="driver", measurement_arm="worker")
    with pytest.raises(MlcaUserError) as exc:
        resume(s)
    assert exc.value.category == "human_decision"


def test_tui_resume_restores_principal_after_halt(monkeypatch):
    import mlca.autonomous.runner as runner
    from mlca.autonomous.windows import Halted

    records = []
    s = NS(
        principal="user",
        mode="driver",
        measurement_arm="worker",
        client=NS(principal="user"),
        root="synthetic",
        emit=lambda kind, payload: records.append(kind),
    )

    def halt(session):
        assert session.is_policy and session.client.principal.startswith("user:policy/")
        raise Halted("paused")

    monkeypatch.setattr(runner, "drive", halt)
    s.is_policy = False
    assert resume(s)["reason"] == "paused"
    assert s.principal == s.client.principal == "user"
    assert not s.is_policy
    assert s.decision_window is None


def test_folder_discovery_is_frozen_before_outputs(tmp_path, monkeypatch):
    import pandas as pd

    import mlca.autonomous.runner as runner

    data = tmp_path / "input"
    data.mkdir()
    pd.DataFrame({"x": [1, 2, 3]}).to_csv(data / "source.csv", index=False)
    seen = []

    def fail(paths, brief, config, evidence, excluded, **kwargs):
        seen.append(list(paths))
        evidence.mkdir()
        pd.DataFrame({"output": [1]}).to_csv(evidence / "generated.csv", index=False)
        raise MlcaUserError("bad proposal", category="invalid_inference")

    monkeypatch.setattr(runner, "infer", fail)
    run(data, data / "outputs", runs=2)
    assert seen == [[data / "source.csv"], [data / "source.csv"]]


def test_setup_halt_is_retained_before_project_exists(tmp_path, monkeypatch):
    import json

    import pandas as pd

    import mlca.autonomous.runner as runner
    from mlca.autonomous.inference import Inference
    from mlca.autonomous.windows import Halted

    data = tmp_path / "source.csv"
    pd.DataFrame({"feature": [1, 2, 3]}).to_csv(data, index=False)

    def infer(paths, brief, conf, evidence, excluded, **kwargs):
        evidence.mkdir()
        proposal = Inference(
            primary_data="source",
            problem_type="clustering",
            unit="One row",
            repeated_subjects="No",
            reason="Explore groups",
        )
        return proposal, "request", "digest", "session"

    def stop(*args):
        raise Halted("Stop before registration")

    monkeypatch.setattr(runner, "infer", infer)
    window = DecisionWindow(60, poll=lambda _: True, override=stop)
    out = tmp_path / "out"
    result = run(data, out, halt_window=60, window=window)
    assert result["runs"][0]["category"] == "human_halt"
    assert not (out / "run-001").exists()
    decisions = json.loads((out / "setup-001/decision-windows.json").read_text())
    assert decisions[-1]["type"] == "DecisionWindowHalted"
    assert decisions[-1]["actor"] == "user"
    summary = json.loads((out / "bench_summary.json").read_text())
    assert summary["autonomy"]["halts"]["mean"]["value"] == 1
    assert summary["autonomy"]["runs_with_setup_only_autonomy"]["value"] == 1
