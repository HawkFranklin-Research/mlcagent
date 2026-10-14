import inspect

import mlca_runtime
from mlca.roles.base import prompt
from mlca.roles.worker import RUNTIME_HELPERS, runtime_api


def test_runtime_api_matches_runtime_signatures():
    api = runtime_api()
    for name in RUNTIME_HELPERS:
        assert f"mlca_runtime.{name}(" in api
    assert "set_seed(seed: int)" in api
    assert "save_json(value: object, name: str" in api
    assert "pathlib" not in api
    assert str(inspect.signature(mlca_runtime.save_table)).startswith("(df")


def test_write_and_repair_prompts_carry_the_signatures():
    api = runtime_api()
    write = prompt("worker_write.md", api=api)
    repair = prompt("worker_repair.md", api=api)
    for text in (write, repair):
        assert "{api}" not in text
        assert "mlca_runtime.save_json(value: object, name: str" in text


def test_repairs_keep_original_input_and_study_contract(monkeypatch):
    from types import SimpleNamespace as NS

    from mlca.roles.worker import Worker

    original = "train: train.parquet; duration: followup; event: observed; _protocol is JSON"
    monkeypatch.setattr("mlca.roles.worker.render_order", lambda *args: {"worker_prompt": original})
    calls = []

    def complete(role, messages, **kwargs):
        calls.append(messages[0]["content"])
        return NS(text="```python\npass\n```", request_id="test")

    worker = Worker(NS(client=NS(complete=complete)))
    monkeypatch.setattr(worker, "context", lambda *args: None)
    action = NS(id="select", prompt="Select covariates", outputs=[])
    worker.write_script(action, {}, {}, NS(), "s")
    worker.repair_script(action, "pass", "UnicodeDecodeError", "s")
    assert original in calls[-1]
    assert "{original_order}" not in calls[-1]


def test_work_order_explains_formats_and_pipeline_prediction():
    write = prompt("worker_write.md", api=runtime_api())
    assert "pandas.read_parquet" in write
    assert "actual outcome columns" in write
    assert "a second time" in write


def test_runtime_contract_keeps_path_values_and_estimator_conventions_explicit():
    api = runtime_api()
    assert "Path objects, not metadata dicts" in api
    assert "For lifelines CoxPHFitter" in api
    assert "duration_col=" in api and "event_col=" in api
    assert "For sklearn estimators" in api


def test_worker_accepts_fenced_and_plain_python_with_same_boundaries():
    from types import SimpleNamespace as NS

    from mlca.roles.worker import Worker
    from mlca.runner.static_checks import check

    worker = Worker(NS())
    source = "import mlca_runtime\nmlca_runtime.set_seed(42)"
    assert worker._script(NS(text=source, request_id="plain")) == (source + "\n", "plain")
    assert worker._script(NS(text="```python\n" + source + "\n```", request_id="fenced")) == (
        source + "\n",
        "fenced",
    )
    quoted = "import mlca_runtime\ntext = '```'"
    assert worker._script(NS(text="```python\n" + quoted + "\n```", request_id="quoted"))[0] == quoted + "\n"
    unsafe, _ = worker._script(NS(text="import os\nos.system('echo unsafe')", request_id="bad"))
    assert any("forbidden call system" in item for item in check(unsafe))


def test_worker_still_refuses_prose_json_and_multiple_code_blocks():
    from types import SimpleNamespace as NS

    import pytest

    from mlca.errors import MlcaUserError
    from mlca.roles.worker import Worker

    worker = Worker(NS())
    for text in [
        "Here is the script: import mlca_runtime",
        '{"name":"tool"}',
        "```python\nimport os\n```\n```python\nimport sys\n```",
    ]:
        with pytest.raises(MlcaUserError):
            worker._script(NS(text=text, request_id="bad"))


def test_fit_refusal_explains_temporary_models_without_relaxing_guard():
    from mlca.runner.static_checks import check

    for method in ("fit", "fit_transform", "partial_fit"):
        violations = check(f"temporary_model.{method}(training_frame)", require_fit=True)
        assert any("fit must use mlca_runtime.fit_record" in item for item in violations)
        assert any("temporary/univariable" in item for item in violations)
    assert check("fit_record(model, training_frame, 'train')", require_fit=True) == []
