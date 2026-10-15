"""Versioned project-local rails; existing safeguards remain authoritative."""

import hashlib
import re
import shutil
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field

from mlca.errors import IntegrityError, MlcaUserError
from mlca.log.schema import StrictModel
from mlca.paths import resource

PROBLEMS = {
    "all",
    "binary",
    "multiclass",
    "multilabel",
    "regression",
    "multioutput_regression",
    "clustering",
    "representation",
    "survival",
}
EVENTS = {
    "all",
    "onboard",
    "data",
    "eda",
    "split",
    "preprocess",
    "features",
    "model",
    "validate",
    "test",
    "interpret",
    "report",
}


class Rail(StrictModel):
    id: str = Field(pattern=r"^RL-[0-9]{4}$")
    kind: Literal["instruction", "check", "default"]
    roles: list[Literal["navigator", "worker", "engine"]]
    events: list[str]
    problem_types: list[str]
    text: str = ""
    check: str | None = None
    point: Literal["before_step", "after_step"] = "before_step"
    reason: str
    ledger: str = Field(pattern=r"^L-[0-9]{4}$")
    added_in: str = Field(pattern=r"^rails-0\.[0-9]+$")


class Rails:
    def __init__(self, version, items=(), digest=None):
        self.version, self.items, self.sha256 = version, tuple(items), digest

    def matching(self, role, event, problem):
        return [
            r
            for r in self.items
            if role in r.roles
            and ("all" in r.events or event in r.events)
            and ("all" in r.problem_types or problem in r.problem_types)
        ]

    def instructions(self, role, event, problem):
        rows = [f"[{r.id}] {r.text}" for r in self.matching(role, event, problem) if r.kind == "instruction"]
        return "\n\nFixed workflow rails:\n" + "\n".join(rows) if rows else ""

    def run(self, session, point):
        from .checks import FUNCTIONS

        for rail in self.matching("engine", session.state.current_event, problem_type(session.state)):
            if rail.kind == "instruction" or rail.point != point:
                continue
            fired, detail = FUNCTIONS[rail.check](session)
            if fired:
                session.emit(
                    "RailFired", {"rail_id": rail.id, "kind": rail.kind, "point": point, "detail": detail}
                )


def problem_type(state):
    return (
        state.task.get("type")
        or state.task.get("kind")
        or {
            "tabular_classification": "binary",
            "multilabel_classification": "multilabel",
        }.get(state.template_id, state.template_id)
    )


def load(path: Path) -> Rails:
    from .checks import FUNCTIONS

    path = Path(path)
    digest = hashlib.sha256()
    items = []
    try:
        version = (path / "VERSION").read_text().strip()
        if not re.fullmatch(r"rails-0\.[0-9]+", version):
            raise ValueError("Invalid rails version")
        digest.update(b"VERSION\0" + version.encode())
        for file in sorted(path.glob("*.yaml")):
            if file.is_symlink():
                raise ValueError("Rail symlinks are forbidden")
            body = file.read_bytes()
            rail = Rail.model_validate(yaml.safe_load(body))
            if rail.id != file.stem or rail.id in {r.id for r in items}:
                raise ValueError("Mismatched or duplicate rail id")
            if (
                not rail.roles
                or not rail.events
                or not rail.problem_types
                or not set(rail.events) <= EVENTS
                or not set(rail.problem_types) <= PROBLEMS
            ):
                raise ValueError("Invalid rail scope")
            if rail.kind == "instruction" and (not rail.text.strip() or rail.check):
                raise ValueError("Instruction needs text and no code reference")
            if rail.kind != "instruction" and (rail.check not in FUNCTIONS or rail.roles != ["engine"]):
                raise ValueError("Engine rail needs a registered trusted function and engine role")
            items.append(rail)
            digest.update(file.name.encode() + b"\0" + body)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise MlcaUserError(f"Invalid rails set: {exc}") from exc
    return Rails(version, items, digest.hexdigest())


def snapshot(destination):
    source = resource("rails")
    baseline = load(source)
    destination.mkdir(parents=True)
    shutil.copy2(source / "VERSION", destination / "VERSION")
    for file in source.glob("*.yaml"):
        shutil.copy2(file, destination / file.name)
    return {"version": baseline.version, "sha256": baseline.sha256}


def open_snapshot(root, created):
    expected = created.payload.get("rails")
    if expected is None:
        return Rails("rails-0.0")  # Historical projects predate explicit rails.
    try:
        actual = load(root / ".mlca/rails")
    except MlcaUserError as exc:
        raise IntegrityError("Project rails snapshot is missing or invalid") from exc
    if actual.version != expected["version"] or actual.sha256 != expected["sha256"]:
        raise IntegrityError("Project rails snapshot changed; start a new study")
    return actual


def instructions(session, role):
    rails = getattr(session, "rails", None)
    return rails.instructions(role, session.state.current_event, problem_type(session.state)) if rails else ""
