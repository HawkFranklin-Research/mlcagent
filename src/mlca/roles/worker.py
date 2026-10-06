import re
from typing import Any

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
        rendered = action.prompt
        for key, value in params.items():
            rendered = rendered.replace("{" + key + "}", str(value))
        result = self.session.client.complete(
            self.name,
            [
                {
                    "role": "user",
                    "content": prompt(
                        "worker_write.md",
                        action=rendered,
                        inputs={k: {"name": v.name, "format": v.suffix} for k, v in inputs.items()},
                        brief=state.brief,
                        params=params,
                        packages=self.session.packages(),
                        outputs=[o.model_dump() for o in action.outputs],
                        event=action.event,
                    ),
                }
            ],
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
