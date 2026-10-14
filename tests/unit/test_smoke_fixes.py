from types import SimpleNamespace as NS

import pytest

from mlca.errors import MlcaUserError
from mlca.evaluation.brain import client_plan
from mlca.evaluation.failures import valid
from mlca.llm.client import model_output_category
from mlca.llm.providers.openai_compatible import CompatibleProvider
from mlca.roles.base import prompt


def provider_returning(finish_reason, refusal=None):
    provider = CompatibleProvider.__new__(CompatibleProvider)
    response = NS(
        model_dump=lambda: {
            "choices": [{"message": {"content": "```python\nx = (", "refusal": refusal}, "finish_reason": finish_reason}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4096},
        }
    )
    provider.client = NS(chat=NS(completions=NS(create=lambda **_: response)))
    return provider


def test_truncated_output_is_a_model_attempt_not_a_provider_outage():
    with pytest.raises(MlcaUserError) as caught:
        provider_returning("length").complete({})
    assert caught.value.category == "output_truncated"
    assert caught.value.accounting["output_tokens"] == 4096
    assert model_output_category(caught.value) == "output_truncated"
    with pytest.raises(MlcaUserError) as refused:
        provider_returning("stop", refusal="no").complete({})
    assert model_output_category(refused.value) == "provider_error"
    assert model_output_category(TimeoutError()) == "provider_error"


def test_new_failure_categories_are_valid():
    assert valid("client_failure")
    assert valid("output_truncated")


def test_worker_prompts_require_the_runtime_import():
    assert "import mlca_runtime" in prompt("worker_write.md")
    assert "import mlca_runtime" in prompt("worker_repair.md")


def test_opencode_run_prints_server_logs(tmp_path):
    plan = client_plan("opencode", "openrouter/x", tmp_path / "project", tmp_path / "client")
    assert "--print-logs" in plan["command"]
