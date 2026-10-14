import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from mlca.errors import MlcaUserError
from mlca.evaluation.bench import ApprovalPolicy, TaskCard, run
from mlca.evaluation.brain import capture_usage, client_plan, parse_output, policy_once, prompt_text
from mlca.llm.usage import read
from mlca.mcp.install import install


def test_opencode_preview_does_not_write(tmp_path):
    text = install("opencode", "project", project=tmp_path)
    assert '"type": "local"' in text and '"mcp"' in text
    assert not (tmp_path / "opencode.json").exists()


@pytest.mark.parametrize("client", ["claude", "codex", "opencode"])
def test_isolated_config_and_prompt(tmp_path, client):
    plan = client_plan(client, "provider/model", tmp_path / "project", tmp_path / client)
    text = Path(plan["config"]).read_text()
    assert "mlca" in text
    if client == "claude":
        assert "--strict-mcp-config" in plan["command"] and "--tools" in plan["command"]
        assert set(json.loads(text)["mcpServers"]) == {"mlca"}
    elif client == "codex":
        assert "shell_tool = false" in text and "read-only" in text
    else:
        assert json.loads(text)["permissions"][0]["effect"] == "deny"
        assert plan["env"]["OPENCODE_CONFIG_PROJECT_DISABLE"] == "1"
    card = TaskCard(
        data=["fixture"],
        brief={"aim": "Test"},
        custom_instructions=[{"event": "data", "text": "Verbatim instruction"}],
    )
    assert "Verbatim instruction" in prompt_text(card, tmp_path)


@pytest.mark.parametrize(
    "client,row",
    [
        (
            "claude",
            {
                "type": "result",
                "usage": {"input_tokens": 10, "output_tokens": 4, "cache_read_input_tokens": 3},
            },
        ),
        (
            "codex",
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 10, "output_tokens": 4, "cached_input_tokens": 3},
            },
        ),
        (
            "opencode",
            {
                "type": "step_finish",
                "part": {"id": "part-1", "tokens": {"input": 10, "output": 4, "cache": {"read": 3}}},
            },
        ),
    ],
)
def test_client_output_usage_counts_only(client, row, opened_project, tmp_path):
    row["secret_message"] = "Do not copy transcript text into usage"
    path = tmp_path / "client.jsonl"
    path.write_text(json.dumps(row) + "\n")
    result = list(parse_output(path.read_text(), client))[0]
    assert result["input_tokens"] == 10 and result["cached_tokens"] == 3
    assert result["cost_usd"] is None and result.get("reasoning_tokens") is None
    assert capture_usage(opened_project, path, client, "model") == 1
    records = read(opened_project.root)
    assert records[-1]["role"] == "external_agent" and records[-1]["cost_source"] == "client"
    assert "secret_message" not in json.dumps(records)


def test_policy_only_declared_approvals():
    resolved = []
    requests = [
        {"request_id": str(i), "kind": kind, "target": target}
        for i, (kind, target) in enumerate(
            [
                ("confirm", "brief"),
                ("unlock_test", "test"),
                ("package", "numpy"),
                ("package", "other"),
                ("study_fields", "study"),
            ]
        )
    ]
    s = SimpleNamespace(
        approvals=lambda: requests,
        questions=lambda: [],
        resolve_approval=lambda *a, **k: resolved.append(a[0]),
    )
    assert policy_once(s, ApprovalPolicy(confirm_subgoals=True, packages=["numpy"])) == ["0", "2"]
    assert resolved == ["0", "2"]


def test_brain_bench_agent_cannot_approve_and_no_models(project_factory, tmp_path, monkeypatch):
    from mlca.api import Session

    root = project_factory()
    config = yaml.safe_load((root / ".mlca/project.yaml").read_text())["config"]
    card = tmp_path / "card.yaml"
    card.write_text(
        yaml.safe_dump(
            {
                "mode": "brain",
                "client": "claude",
                "model": "fixture-model",
                "data": [str(root.parent / "synthetic.csv")],
                "brief": {"target": "y", "unit": "One sample"},
                "config": config,
            }
        )
    )

    def fake(session, card, client, model, timeout):
        assert session.client.disabled
        with Session(session.root, mode="brain", principal="agent:fixture/1") as agent:
            with pytest.raises(MlcaUserError):
                agent.confirm("brief_confirmed", "self approval")
        return {"command": ["fixture"], "client": client}

    monkeypatch.setattr("mlca.evaluation.brain.run", fake)
    result = run(card, 1, tmp_path / "bench")
    assert result["mode"] == "brain"
    assert read(tmp_path / "bench/run-001") == []


def test_mixed_arm_summary_marks_brain_unavailable(tmp_path):
    from mlca.evaluation.cross_arms import summarize

    for mode in ["brain", "driver"]:
        directory = tmp_path / mode
        directory.mkdir()
        (directory / "bench_summary.json").write_text(
            json.dumps(
                {
                    "mode": mode,
                    "client": "claude" if mode == "brain" else None,
                    "model": "model",
                    "task": "task",
                    "measurement_arm": "worker",
                    "run_count": {"value": 1},
                    "completed": {"value": 0},
                    "navigator_fallbacks": {"value": 0},
                }
            )
        )
    rows = summarize(tmp_path)["groups"]
    assert next(r for r in rows if r["mode"] == "brain")["navigator_fallbacks"] is None
    assert "n/a" in (tmp_path / "cross_arm_summary.csv").read_text()


def test_real_runner_retains_failed_client_and_usage(opened_project, tmp_path, monkeypatch):
    from mlca.evaluation import brain

    class Process:
        returncode = 0

        def communicate(self, *a, **k):
            return json.dumps(
                {"type": "turn.completed", "usage": {"input_tokens": 12, "output_tokens": 3}}
            ), ""

    monkeypatch.setattr(brain.shutil, "which", lambda c: "/fixture/" + c)
    monkeypatch.setattr(
        brain.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(stdout="--json --skip-git-repo-check --sandbox --model"),
    )
    monkeypatch.setattr(brain.subprocess, "Popen", lambda *a, **k: Process())
    card = TaskCard(data=["fixture.csv"], brief={}, approval_policy=ApprovalPolicy())
    with pytest.raises(MlcaUserError, match="did not complete"):
        brain.run(opened_project, card, "codex", "fixture-model")
    assert (opened_project.root / "brain_output.jsonl").exists()
    assert read(opened_project.root)[-1]["input_tokens"] == 12


def test_brain_missing_usage_is_not_zero():
    from mlca.evaluation.bench import _model_total

    assert _model_total({"models": {"external_agent": {"value": None}}}, "input_tokens", "brain") is None
