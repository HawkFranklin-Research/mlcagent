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

from .discovery import discover, registrations
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
        fields["target"] = brief.get("duration") or brief.get("target", "")
        fields["duration"] = brief.get("duration") or brief.get("target", "")
        fields["event_column"] = brief.get("event_column", "")
    return {
        field: resolve_column(answer, available, field, picker) if str(answer or "").strip() else None
        for field, answer in fields.items()
    }


def primary_for(state) -> str:
    name = state.primary_data
    if name is None and len(state.data) == 1:
        name = next(iter(state.data))
    if name not in state.data:
        raise MlcaUserError("Choose the main study table before continuing", category="gate_blocked")
    return name


def study_ready(state) -> tuple[bool, str]:
    try:
        column_for(state)
        if state.template_id == "survival":
            column_for(state, "duration")
            column_for(state, "event_column")
        if not str(state.brief.get("unit", "")).strip() or state.brief.get("unit") == "Not sure yet":
            return False, "Explain what one row represents before confirming the study"
        return True, "Main table, required columns and row meaning resolved"
    except MlcaUserError as exc:
        return False, str(exc)


def column_for(state, field: str = "target") -> str:
    """Old projects accept only an exact inventory column; never guess from free text."""
    if not state.data and len(state.inventory) == 1:
        available = state.inventory[0]["columns"]
    else:
        name = primary_for(state)
        available = next(item["columns"] for item in state.inventory if item["name"] == name)
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
    primary_data: str | None = None,
) -> Path:
    root = path.resolve()
    validated_config = Config.model_validate(config or {})
    if (root / ".mlca").exists():
        raise MlcaUserError(
            "This folder already contains an MLCA study or an earlier initialization attempt. Open it to continue, or choose a new project folder. Existing files will not be overwritten."
        )
    workflow = get(template_id)
    registered = []
    for name, file in registrations(discover(data)):
        if not file.is_file():
            raise MlcaUserError(f"Data file does not exist: {file}")
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
    if primary_data is not None:
        primary_data = next(
            (
                item["name"]
                for item in registered
                if item["original_path"] == str(Path(primary_data).expanduser().resolve())
            ),
            primary_data,
        )
    if primary_data is None and len(registered) == 1:
        primary_data = registered[0]["name"]
    if primary_data not in {item["name"] for item in registered}:
        raise MlcaUserError("Choose a main study table by its registered name before initialization")
    main_inventory = [item for item in inventory if item["name"] == primary_data]
    columns = resolve_columns(brief, main_inventory, template_id, column_picker)
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
    from mlca.privacy.rows import RowFingerprints

    RowFingerprints(root).ensure(registered)
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
        {"answers": redact_value(brief, validated_config), "columns": columns, "primary_data": primary_data},
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
