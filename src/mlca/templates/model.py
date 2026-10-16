from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Spec(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CheckSpec(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str


class Subgoal(Spec):
    id: str
    text: str
    check: CheckSpec


class Scope(Spec):
    description: str
    deny_patterns: list[str] = Field(default_factory=list)
    readable_inputs: list[str] = Field(default_factory=list)


class EventSpec(Spec):
    id: str
    title: str
    goal: str
    gate: list[dict] = Field(default_factory=list)
    subgoals: list[Subgoal]
    actions: list[str]
    default_options: list[str]
    done_when: str | list[str] = "all_subgoals"
    custom_scope: Scope
    max_options: int = Field(default=4, ge=1, le=4)


class ParamSpec(Spec):
    type: Literal["data_ref", "string", "integer", "number", "boolean", "enum"]
    default: object = None
    required: bool = True
    enum: list = Field(default_factory=list)
    minimum: float | None = None
    maximum: float | None = None


class OutputSpec(Spec):
    name: str
    kind: Literal["table", "figure", "model", "report", "data", "other"]
    required: bool = True
    row_partitions: list[Literal["train", "val", "test"]] | None = Field(default=None, min_length=1)


class ActionSpec(Spec):
    id: str
    event: str
    title: str
    role: Literal["primary", "supporting"] = "primary"
    params: dict[str, ParamSpec] = Field(default_factory=dict)
    prompt: str
    inputs: list[dict] = Field(default_factory=list)
    outputs: list[OutputSpec] = Field(default_factory=list)
    fact_candidates: list[str] = Field(default_factory=list)
    reads_test: bool = False
    allow_network: bool = False
    timeout_s: int = Field(default=300, ge=1, le=86400)
    methods_text: str = ""
    builtin: Literal["split", "report", "inventory"] | None = None
    prepares_data: str | None = None


class TemplateSpec(Spec):
    id: str
    version: str
    title: str
    description: str
    brief_questions: list[dict] = Field(default_factory=list)
    events: list[str]
    transitions: dict = Field(default_factory=dict)
    style: str = "default"
    default_runtime_packages: list[str] = Field(default_factory=list)


class Workflow(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    spec: TemplateSpec
    events: dict[str, EventSpec]
    actions: dict[str, ActionSpec]
    path: Path
    sha256: str
