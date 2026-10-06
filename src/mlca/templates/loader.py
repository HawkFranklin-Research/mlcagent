import hashlib
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from mlca.errors import MlcaUserError

from .model import ActionSpec, EventSpec, TemplateSpec, Workflow

CHECK_TYPES = {
    "event_done",
    "fact_present",
    "output_exists",
    "artefact_hash_recorded",
    "metric_present",
    "figure_count",
    "split_frozen",
    "fit_on_train_only",
    "test_unlocked",
    "user_confirm",
    "template_check",
}


def parse(path: Path, model: Any) -> Any:
    try:
        return model.model_validate(yaml.safe_load(path.read_text()))
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise MlcaUserError(f"{path}: {exc}") from exc


def load(path: Path) -> Workflow:
    path = path.resolve()
    spec = parse(path / "template.yaml", TemplateSpec)
    if len(spec.events) != len(set(spec.events)) or not spec.events:
        raise MlcaUserError("template.yaml: events must be nonempty and unique")
    for name in [spec.id, *spec.events]:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise MlcaUserError(f"template.yaml: unsafe identifier {name}")
    events = {name: parse(path / "events" / f"{name}.yaml", EventSpec) for name in spec.events}
    actions = {}
    for file in sorted((path / "actions").glob("*.yaml")):
        action = parse(file, ActionSpec)
        if action.id in actions or file.stem != action.id:
            raise MlcaUserError(f"{file}: duplicate or mismatched action id")
        for output in action.outputs:
            if Path(output.name).is_absolute() or ".." in Path(output.name).parts:
                raise MlcaUserError(f"{file}: unsafe output.name")
        actions[action.id] = action
    for name, event in events.items():
        filename = path / "events" / f"{name}.yaml"
        if event.id != name or not event.default_options:
            raise MlcaUserError(f"{filename}: id/default_options invalid")
        if len(event.subgoals) != len({s.id for s in event.subgoals}):
            raise MlcaUserError(f"{filename}: duplicate subgoal id")
        if isinstance(event.done_when, list) and not set(event.done_when) <= {s.id for s in event.subgoals}:
            raise MlcaUserError(f"{filename}: unknown done_when subgoal")
        for action_id in event.actions + event.default_options:
            if action_id not in actions or actions[action_id].event != name:
                raise MlcaUserError(
                    f"{filename}: actions/default_options: wrong or unknown action {action_id}"
                )
        for subgoal in event.subgoals:
            if subgoal.check.type not in CHECK_TYPES:
                raise MlcaUserError(f"{filename}: unknown check type {subgoal.check.type}")
        for gate in event.gate:
            kind = gate.get("type", "event_done" if "event_done" in gate else "")
            if kind not in CHECK_TYPES:
                raise MlcaUserError(f"{filename}: unknown gate type {kind}")
            if "event_done" in gate and gate["event_done"] not in events:
                raise MlcaUserError(f"{filename}: unknown gate event")
        for pattern in event.custom_scope.deny_patterns:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise MlcaUserError(f"{filename}: custom_scope.deny_patterns: {exc}") from exc
    required_check_fields = {
        "fact_present": {"key"},
        "output_exists": {"action", "output"},
        "metric_present": {"name", "split"},
        "figure_count": {"min"},
        "template_check": {"function"},
    }
    for event in events.values():
        for subgoal in event.subgoals:
            data = subgoal.check.model_dump()
            missing = required_check_fields.get(subgoal.check.type, set()) - set(data)
            if missing:
                raise MlcaUserError(f"events/{event.id}.yaml: check fields missing: {sorted(missing)}")
            if subgoal.check.type == "output_exists":
                owner = actions.get(data["action"])
                if not owner or data["output"] not in {o.name for o in owner.outputs}:
                    raise MlcaUserError(f"events/{event.id}.yaml: check references unknown output")
            if subgoal.check.type == "template_check" and not (path / "checks.py").is_file():
                raise MlcaUserError(f"events/{event.id}.yaml: template_check requires trusted checks.py")
    for action in actions.values():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", action.id):
            raise MlcaUserError(f"actions/{action.id}.yaml: unsafe action identifier")
        for parameter in action.params.values():
            if parameter.type == "enum" and not parameter.enum:
                raise MlcaUserError(f"actions/{action.id}.yaml: enum values are required")
        if action.event not in events or action.id not in events[action.event].actions:
            raise MlcaUserError(f"actions/{action.id}.yaml: action not listed by its event")
        if action.reads_test and action.event not in {"test", "interpret", "report"}:
            raise MlcaUserError(f"actions/{action.id}.yaml: reads_test forbidden in {action.event}")
    for transitions in spec.transitions.values():
        for transition in transitions:
            targets = transition.get("to", [])
            if isinstance(targets, str):
                targets = [targets]
            if transition.get("from") not in events or not set(targets) <= set(events):
                raise MlcaUserError("template.yaml: transition refers to unknown event")
    digest = hashlib.sha256()
    for file in sorted(path.rglob("*")):
        if file.is_file() and file.suffix in {".yaml", ".py"}:
            digest.update(str(file.relative_to(path)).encode())
            digest.update(file.read_bytes())
    return Workflow(spec=spec, events=events, actions=actions, path=path, sha256=digest.hexdigest())
