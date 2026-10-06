import shutil
from collections.abc import Callable
from pathlib import Path

import yaml
from ulid import ULID

from mlca import __version__
from mlca.config import Config, redact_value
from mlca.errors import MlcaUserError
from mlca.log.store import Store
from mlca.paths import atomic_json, resource, sha256
from mlca.templates.registry import get

from .env import create
from .inventory import scan


def resolve_column(answer: str, available: list[str], field: str, picker: Callable | None = None) -> str:
    if answer in available:
        return answer
    matches = [column for column in available if column.casefold() == str(answer).casefold()]
    if len(matches) == 1:
        return matches[0]
    if picker is not None:
        selected = picker(field, available)
        if selected in available:
            return selected
    raise MlcaUserError(f"Unresolved {field} column {answer!r}. Available columns: {', '.join(available)}")


def resolve_columns(
    brief: dict, inventory: list[dict], template_id: str, picker: Callable | None = None
) -> dict:
    available = inventory[0]["columns"]
    fields = {"target": brief.get("target", "")}
    if template_id == "survival":
        fields["duration"] = brief.get("duration") or brief.get("target", "")
        fields["event_column"] = brief.get("event_column", "")
    return {field: resolve_column(answer, available, field, picker) for field, answer in fields.items()}


def column_for(state, field: str = "target") -> str:
    """Old projects accept only an exact inventory column; never guess from free text."""
    available = state.inventory[0]["columns"] if state.inventory else []
    value = state.columns.get(field)
    if value is None:
        value = state.brief.get(field, state.brief.get("target") if field == "duration" else None)
    if value not in available:
        raise MlcaUserError(
            f"Unresolved {field} column in project. Available columns: {', '.join(available)}. Initialize with a validated column name."
        )
    return value


def initialise(
    path: Path,
    data: list[Path],
    template_id: str,
    brief: dict,
    config: dict | None = None,
    column_picker: Callable | None = None,
    principal: str = "user",
) -> Path:
    root = path.resolve()
    validated_config = Config.model_validate(config or {})
    if (root / ".mlca").exists():
        raise MlcaUserError("Project already initialized; refusing to overwrite it")
    workflow = get(template_id)
    registered = []
    for file in data:
        file = file.resolve()
        if not file.is_file():
            raise MlcaUserError(f"Data file does not exist: {file}")
        name = file.stem
        if name in {item["name"] for item in registered}:
            raise MlcaUserError("Registered data names must be unique")
        registered.append(
            {
                "name": name,
                "original_path": str(file),
                "sha256": sha256(file),
                "size": file.stat().st_size,
                "read_only": True,
            }
        )
    if not registered:
        raise MlcaUserError("At least one data file is required")
    inventory = [scan(item["name"], Path(item["original_path"])) for item in registered]
    columns = resolve_columns(brief, inventory, template_id, column_picker)
    root.mkdir(parents=True, exist_ok=True)
    for folder in ["log", "steps", "data/splits", "vault", "llm", "runtime"]:
        (root / ".mlca" / folder).mkdir(parents=True, exist_ok=True)
    # Freeze workflow content inside each project; user template edits cannot mutate historical studies.
    shutil.copytree(workflow.path, root / ".mlca/template", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(resource("styles") / "default.mplstyle", root / ".mlca/style.mplstyle")
    project_id = str(ULID())
    settings = {
        "project_id": project_id,
        "template_id": workflow.spec.id,
        "template_version": workflow.spec.version,
        "template_sha256": workflow.sha256,
        "config": config or {},
    }
    (root / ".mlca/project.yaml").write_text(yaml.safe_dump(settings, sort_keys=False), encoding="utf-8")
    store = Store(root)
    store.append(
        "ProjectCreated",
        {
            "project_id": project_id,
            "mlca_version": __version__,
            "template_id": workflow.spec.id,
            "template_version": workflow.spec.version,
            "template_sha256": workflow.sha256,
        },
    )
    for item in registered:
        store.append("DataRegistered", item)
    atomic_json(root / ".mlca/inventory.json", inventory)
    store.append("InventoryRecorded", {"files": inventory, "sha256": sha256(root / ".mlca/inventory.json")})
    store.append(
        "BriefRecorded",
        {"answers": redact_value(brief, validated_config), "columns": columns},
        actor=principal,
    )
    lock_data = create(root, workflow.spec.default_runtime_packages)
    store.append("EnvironmentRecorded", lock_data)
    store.append(
        "EventEntered",
        {"event_id": workflow.spec.events[0], "via": "start"},
        event_id=workflow.spec.events[0],
    )
    return root
