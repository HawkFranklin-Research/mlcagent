from typing import Any

from pydantic import Field

from mlca.errors import MlcaUserError
from mlca.log.schema import StrictModel


class Option(StrictModel):
    id: str
    action_id: str
    params: dict
    title: str = Field(max_length=80)
    why_now: str = Field(max_length=200)
    advances: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    est_cost_usd: float | None = None


class OptionsResponse(StrictModel):
    options: list[Option]


def parameters(action: Any, values: Any, state: Any) -> Any:
    if set(values) - set(action.params):
        raise MlcaUserError("Unknown action parameter")
    result = {}
    for name, spec in action.params.items():
        value = values.get(name, spec.default)
        if value is None:
            if spec.required:
                raise MlcaUserError(f"Required parameter: {name}")
            continue
        valid = True
        if spec.type in {"string", "data_ref", "enum"}:
            valid = isinstance(value, str)
        elif spec.type == "integer":
            valid = isinstance(value, int) and not isinstance(value, bool)
        elif spec.type == "number":
            valid = isinstance(value, (int, float)) and not isinstance(value, bool)
        elif spec.type == "boolean":
            valid = isinstance(value, bool)
        if not valid or (spec.enum and value not in spec.enum):
            raise MlcaUserError(f"Invalid parameter {name}")
        if spec.type == "data_ref" and value not in state.data:
            raise MlcaUserError("Unknown registered data reference")
        if (
            spec.minimum is not None
            and value < spec.minimum
            or spec.maximum is not None
            and value > spec.maximum
        ):
            raise MlcaUserError(f"Parameter out of range: {name}")
        result[name] = value
    return result


def validate(options: Any, state: Any, workflow: Any) -> Any:
    event = workflow.events[state.current_event]
    if not 1 <= len(options) <= event.max_options:
        raise MlcaUserError("Navigator must return a bounded nonempty list of options")
    result = []
    for n, option in enumerate(options, 1):
        if option.action_id not in event.actions:
            raise MlcaUserError("Action outside current event catalog")
        action = workflow.actions[option.action_id]
        params = parameters(action, option.params, state)
        for goal in option.advances:
            if goal not in {s.id for s in event.subgoals} or state.subgoals.get(f"{event.id}.{goal}", {}).get(
                "passed"
            ):
                raise MlcaUserError("Option advances an unknown or completed sub-goal")
        if not set(option.expected_outputs) <= {o.name for o in action.outputs}:
            raise MlcaUserError("Unknown expected output")
        if any(
            s["status"] == "completed"
            and s["action_id"] == action.id
            and s["params"] == params
            and s.get("generation", 0) == state.generations.get(s["event_id"], 0)
            for s in state.steps
        ):
            raise MlcaUserError("Duplicate completed action and parameters")
        if any(o["action_id"] == action.id and o["params"] == params for o in result):
            raise MlcaUserError("Duplicate option")
        result.append({**option.model_dump(), "id": str(n), "params": params, "est_cost_usd": None})
    return result


def fallback(state: Any, workflow: Any) -> Any:
    event = workflow.events[state.current_event]
    options = []
    for identifier in event.default_options:
        action = workflow.actions[identifier]
        values = {
            name: (
                next(iter(state.data)) if spec.type == "data_ref" and spec.default is None else spec.default
            )
            for name, spec in action.params.items()
        }
        params = parameters(action, values, state)
        if any(
            s["status"] == "completed"
            and s["action_id"] == identifier
            and s["params"] == params
            and s.get("generation", 0) == state.generations.get(s["event_id"], 0)
            for s in state.steps
        ):
            continue
        options.append(
            {
                "id": str(len(options) + 1),
                "action_id": identifier,
                "params": params,
                "title": action.title,
                "why_now": "Template default action",
                "advances": [],
                "expected_outputs": [o.name for o in action.outputs],
                "est_cost_usd": None,
            }
        )
    return options[: event.max_options]
