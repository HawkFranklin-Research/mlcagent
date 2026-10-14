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
