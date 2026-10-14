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
            "choices": [
                {
                    "message": {"content": "```python\nx = (", "refusal": refusal},
                    "finish_reason": finish_reason,
                }
            ],
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


def test_fit_record_rejects_arrays_with_a_repairable_message(monkeypatch):
    import numpy as np

    import mlca_runtime

    with pytest.raises(
        mlca_runtime.FitRuleError, match="MLCA: fit_record needs the training pandas DataFrame"
    ):
        mlca_runtime.fit_record(object(), np.zeros((3, 2)), "train")


def test_repair_diagnostics_quote_only_mlca_messages():
    from mlca.runner.run_step import diagnostics

    stderr = (
        'Traceback (most recent call last):\n  File "/x/script.py", line 12, in <module>\n'
        '  File "/x/runtime/mlca_runtime/__init__.py", line 140, in fit_record\n'
        "mlca_runtime.FitRuleError: MLCA: fit_record needs the training pandas DataFrame\n"
    )
    text = diagnostics({"stderr": stderr}, allow_samples=False)
    assert "script line 12" in text and "inside mlca_runtime.fit_record" in text
    assert "MLCA: fit_record needs the training pandas DataFrame" in text
    leaky = "File \"/x/script.py\", line 3\nKeyError: 'patient 0042 value 13.1'\n"
    assert "0042" not in diagnostics({"stderr": leaky}, allow_samples=False)


def test_brain_prompt_forbids_text_tool_calls():
    from mlca.evaluation.brain import prompt_text

    card = NS(template="tabular_classification", brief={}, custom_instructions=[])
    assert "Never write a tool call as text" in prompt_text(card, "/p")


def test_static_check_allows_slash_separator_but_not_paths():
    from mlca.runner.static_checks import check

    # Line 60 of the heart-nemotron-4 step 9 script, rejected twice before this fix.
    assert check('k = "a/b"\nname = k.split("/")[0] if "/" in k else k\n') == []
    for literal in ("/etc/passwd", "~/data.csv", "../secret.csv"):
        assert any("path literal" in v for v in check(f"open({literal!r})\n"))


@pytest.mark.parametrize(
    "stderr, hint",
    [
        ("ValueError: columns are missing: {'PATIENT_SECRET'}", "original raw feature columns"),
        (
            "ValueError: Specifying the columns using strings is only supported for dataframes. PATIENT_SECRET",
            "original pandas feature DataFrame",
        ),
        ("TypeError: '_Inputs' object is not callable. PATIENT_SECRET", "dictionary of Paths"),
    ],
)
def test_safe_library_hints_do_not_return_values(stderr, hint):
    from mlca.runner.run_step import diagnostics

    message = diagnostics({"stderr": stderr}, False)
    assert hint in message
    assert "PATIENT_SECRET" not in message
