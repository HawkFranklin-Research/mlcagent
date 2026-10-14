import inspect
import re
from typing import Any

import mlca_runtime
from mlca.errors import MlcaUserError

from .base import Role, prompt


class Worker(Role):
    name = "worker"

    def _script(self, result: Any) -> Any:
        match = re.fullmatch(r"\s*```(?:python)?\s*\n(.*?)\n```\s*", result.text, flags=re.S)
        if not match:
            raise MlcaUserError("Worker must return exactly one fenced Python script")
        return match.group(1) + "\n", result.request_id

    def write_script(self, action: Any, params: Any, inputs: Any, state: Any, step_id: Any) -> Any:
        order = render_order(self.session, action, params, inputs, state)
        result = self.session.client.complete(
            self.name,
            [{"role": "user", "content": order["worker_prompt"]}],
            context=self.context("write", action.id, step_id),
            categories=["template_spec", "inventory_summary", "user_text"],
        )
        return self._script(result)

    def repair_script(self, action: Any, source: Any, error: Any, step_id: Any) -> Any:
        result = self.session.client.complete(
            self.name,
            [
                {
                    "role": "user",
                    "content": prompt(
                        "worker_repair.md",
                        api=runtime_api(),
                        script=source,
                        error=error[:4000],
                        scope=action.prompt,
                        outputs=[o.model_dump() for o in action.outputs],
                    ),
                }
            ],
            context=self.context("repair", action.id, step_id),
            categories=["script", "traceback", "template_spec"],
        )
        return self._script(result)


RUNTIME_HELPERS = (
    "inputs", "output_dir", "set_seed", "fit_record", "save_table", "save_json",
    "save_figure", "save_model", "record_metric", "record_fact_candidate",
)


def runtime_api():
    """Exact helper signatures, read from mlca_runtime so the prompt cannot drift from the code."""
    lines = [f"mlca_runtime.{name}{inspect.signature(getattr(mlca_runtime, name))}" for name in RUNTIME_HELPERS]
    return re.sub(r"pathlib\.(_local\.)?", "", "\n".join(lines))


def render_order(session, action, params, inputs, state):
    rendered = action.prompt
    for key, value in params.items():
        rendered = rendered.replace("{" + key + "}", str(value))
    if state.guided_enabled:
        rendered += "\nRead the declared _protocol JSON: use its task, primary_metric, outcome columns and exclusions. Binary threshold selection is validation-only; multiclass uses macro one-vs-rest ROC AUC without a binary threshold. Never fit after test exposure."
    names = {k: {"name": v.name, "format": v.suffix} for k, v in inputs.items()}
    if action.reads_test:
        names["test"] = {"name": "test.parquet", "format": ".parquet"}
    if (
        state.external
        and action.event in {"test", "interpret"}
        and (action.reads_test or any(i["ref"] == "external" for i in action.inputs))
    ):
        names["external"] = {"name": "external.parquet", "format": ".parquet"}
        rendered += "\nExternal cohort is available only for this one frozen-variant exposure. Score it without fitting; record metrics with split external."
    outputs = [o.model_dump() for o in action.outputs]
    brief = {
        "answers": state.brief,
        "columns": state.columns,
        "primary_data": state.primary_data,
        "task": state.task,
        "excluded_columns": state.excluded_columns,
    }
    return {
        "event": action.event,
        "action": action.id,
        "instructions": rendered,
        "inputs": names,
        "required_outputs": outputs,
        "allowed_fact_keys": action.fact_candidates,
        "params": params,
        "packages": session.packages(),
        "brief": brief,
        "runtime_api": runtime_api(),
        "rules": [
            "Use mlca_runtime.inputs()/output_dir()",
            "Fit only via fit_record on frozen train index",
            "No network or subprocess; no undeclared paths",
            "Only required outputs plus at most one figure; summary tables <=50 rows x12 columns; <=5 printed lines; record metrics and cite facts",
        ],
        "worker_prompt": prompt(
            "worker_write.md",
            api=runtime_api(),
            action=rendered,
            inputs=names,
            brief=brief,
            params=params,
            packages=session.packages(),
            outputs=outputs,
            facts=action.fact_candidates,
            event=action.event,
        ),
    }
