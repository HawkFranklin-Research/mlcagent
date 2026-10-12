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
        if state.event_statuses.get(event.id) == "done" and action.role != "supporting":
            raise MlcaUserError(
                "Completed events accept supporting actions only; branch before a primary step"
            )
        if action.role == "supporting" and already_run(action.id, state):
            raise MlcaUserError("Supporting action already completed in this event generation")
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


def already_run(identifier, state):
    return any(
        step["status"] == "completed"
        and step["action_id"] == identifier
        and step["event_id"] == state.current_event
        and step.get("generation", 0) == state.generations.get(state.current_event, 0)
        for step in state.steps
    )


def fallback(state: Any, workflow: Any) -> Any:
    event = workflow.events[state.current_event]
    done = state.event_statuses.get(event.id) == "done"
    identifiers = list(
        dict.fromkeys(
            [
                *(
                    name
                    for name in event.default_options
                    if workflow.actions[name].role == "primary" and not done
                ),
                *(name for name in event.actions if workflow.actions[name].role == "primary" and not done),
                *(name for name in event.actions if workflow.actions[name].role == "supporting"),
            ]
        )
    )
    options, exhausted = [], []
    for identifier in identifiers:
        action = workflow.actions[identifier]
        if action.role == "supporting" and already_run(identifier, state):
            continue
        values = {
            name: (state.primary_data or next(iter(state.data)))
            if spec.type == "data_ref" and spec.default is None
            else spec.default
            for name, spec in action.params.items()
        }
        try:
            params = parameters(action, values, state)
        except MlcaUserError:
            # A required parameter without a default needs a custom instruction.
            continue
        duplicate = any(
            step["status"] == "completed"
            and step["action_id"] == identifier
            and step["params"] == params
            and step.get("generation", 0) == state.generations.get(step["event_id"], 0)
            for step in state.steps
        )
        option = {
            "id": "",
            "action_id": identifier,
            "params": params,
            "title": action.title,
            "why_now": "Template default action"
            if identifier in event.default_options
            else "Supporting inspection action"
            if action.role == "supporting"
            else "Alternative primary action",
            "advances": [],
            "expected_outputs": [output.name for output in action.outputs],
            "est_cost_usd": None,
        }
        if not duplicate:
            options.append(option)
        elif action.role == "primary" and action.params:
            exhausted.append({**option, "why_now": "Repeat with different parameters"})
    options = (options or exhausted)[: event.max_options]
    return [{**option, "id": str(index)} for index, option in enumerate(options, 1)]
