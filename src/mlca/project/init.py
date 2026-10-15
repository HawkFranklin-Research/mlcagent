import hashlib
import os
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

import yaml
from filelock import FileLock
from ulid import ULID

from mlca import __version__
from mlca.config import Config, redact_value
from mlca.errors import MlcaUserError
from mlca.log.store import Store
from mlca.paths import atomic_json, resource, sha256, user_data_dir
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
    if template_id in {"clustering", "representation"}:
        return {}
    fields = {"target": brief.get("target", "")}
    if template_id in {"regression", "multilabel_classification"}:
        import json

        targets = json.loads(brief.get("targets", "[]")) or [brief.get("target", "")]
        if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
            raise MlcaUserError("Targets must be a JSON list of column names")
        fields = {("target" if i == 0 else f"target_{i + 1}"): t for i, t in enumerate(targets)}
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
        if state.template_id not in {"clustering", "representation"}:
            column_for(state)
            for field in state.columns:
                column_for(state, field)
        else:
            primary_for(state)
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


def _build_initialisation(
    path: Path,
    data: list[Path],
    template_id: str,
    brief: dict,
    config: dict | None = None,
    column_picker: Callable | None = None,
    principal: str = "user",
    primary_data: str | None = None,
    data_roles: dict[str, str] | None = None,
    exclude_columns: tuple[str, ...] = (),
    final_root: Path | None = None,
) -> Path:
    root = path.resolve()
    validated_config = Config.model_validate(config or {})
    if (root / ".mlca").exists():
        raise MlcaUserError(
            "This folder already contains an MLCA study or an earlier initialization attempt. Open it to continue, or choose a new project folder. Existing files will not be overwritten."
        )
    workflow = get(template_id)
    registered = []
    local_paths = {}
    for name, file in registrations(discover(data)):
        if not file.is_file():
            raise MlcaUserError(f"Data file does not exist: {file}")
        if name in {item["name"] for item in registered}:
            raise MlcaUserError("Registered data names must be unique")
        source_digest = sha256(file)
        if exclude_columns:
            from .inventory import read_table

            frame = read_table(file)
            frame = frame.drop(columns=list(exclude_columns), errors="ignore")
            if frame.empty or not len(frame.columns):
                raise MlcaUserError("Exclusion leaves no usable data")
            file = root / ".mlca/data/registered" / (name + ".parquet")
            file.parent.mkdir(parents=True, exist_ok=True)
            frame.to_parquet(file, index=True)
        local_paths[name] = file
        destination = (final_root / file.relative_to(root)) if exclude_columns else file
        registered.append(
            {
                "name": name,
                "original_path": str(destination),
                "source_sha256": source_digest,
                "sha256": sha256(file),
                "size": file.stat().st_size,
                "read_only": True,
            }
        )
    if not registered:
        raise MlcaUserError("At least one data file is required")
    data_roles = data_roles or {}
    for item in registered:
        item["role"] = data_roles.get(item["name"], data_roles.get(item["original_path"], "discovery"))
        if item["role"] not in {"discovery", "external"}:
            raise MlcaUserError("Table role must be discovery or external")
    inventory = [scan(item["name"], local_paths[item["name"]]) for item in registered]
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
    if next(i for i in registered if i["name"] == primary_data)["role"] == "external":
        raise MlcaUserError("The main study table cannot be external")
    main_inventory = [item for item in inventory if item["name"] == primary_data]
    columns = resolve_columns(brief, main_inventory, template_id, column_picker)
    root.mkdir(parents=True, exist_ok=True)
    for folder in ["log", "steps", "data/splits", "vault", "llm", "runtime"]:
        (root / ".mlca" / folder).mkdir(parents=True, exist_ok=True)
    # Freeze workflow content inside each project; user template edits cannot mutate historical studies.
    shutil.copytree(workflow.path, root / ".mlca/template", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(resource("styles") / "default.mplstyle", root / ".mlca/style.mplstyle")
    from mlca.rails import snapshot

    rails = snapshot(root / ".mlca/rails")
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

    RowFingerprints(root).ensure([{**i, "original_path": str(local_paths[i["name"]])} for i in registered])
    store = Store(root)
    store.append(
        "ProjectCreated",
        {
            "project_id": project_id,
            "measurement_arm": validated_config.measurement_arm,
            "rails": rails,
            "mlca_version": __version__,
            "template_id": workflow.spec.id,
            "template_version": workflow.spec.version,
            "template_sha256": workflow.sha256,
        },
    )
    for item in registered:
        store.append("DataRegistered", item)
        if item["role"] == "external":
            import io

            from mlca.sandbox.vault import seal

            from .inventory import read_table

            buffer = io.BytesIO()
            read_table(Path(item["original_path"])).to_parquet(buffer, index=False)
            destination = root / ".mlca/vault" / ("external_" + item["name"] + ".enc")
            key_id = "external_" + item["name"]
            seal(project_id, key_id, buffer.getvalue(), destination)
            store.append(
                "ExternalSealed",
                {
                    "name": item["name"],
                    "key_id": key_id,
                    "path": str(destination.relative_to(root)),
                    "sha256": sha256(destination),
                    "plain_sha256": hashlib.sha256(buffer.getvalue()).hexdigest(),
                },
            )
    atomic_json(root / ".mlca/inventory.json", inventory)
    store.append("InventoryRecorded", {"files": inventory, "sha256": sha256(root / ".mlca/inventory.json")})
    store.append(
        "BriefRecorded",
        {"answers": redact_value(brief, validated_config), "columns": columns, "primary_data": primary_data},
        actor=principal,
    )
    lock_data = create(
        root,
        workflow.spec.default_runtime_packages,
        **({"measurement_arm": "reference"} if validated_config.measurement_arm == "reference" else {}),
    )
    store.append("EnvironmentRecorded", lock_data)
    store.append(
        "EventEntered",
        {"event_id": workflow.spec.events[0], "via": "start"},
        event_id=workflow.spec.events[0],
    )
    return root


def _rebase_environment(staged: Path, destination: Path):
    # Virtualenv entry-point shebangs, activators, cfg and local direct_url metadata contain
    # absolute paths. Installed wheels/runtime sources stay byte-identical.
    environment = staged / ".mlca/env"
    old = str(staged).encode()
    new = str(destination).encode()
    for file in environment.rglob("*"):
        if not file.is_file() or file.is_symlink():
            continue
        if file.parent.name not in {"bin", "Scripts"} and file.name not in {"pyvenv.cfg", "direct_url.json"}:
            continue
        body = file.read_bytes()
        if b"\0" in body or old not in body:
            continue
        try:
            body.decode("utf-8")
        except UnicodeDecodeError:
            continue
        mode = file.stat().st_mode
        # uv may hardlink dependency files to its shared cache. Replace, never edit in place.
        temporary = file.with_name(file.name + ".mlca-rebase")
        temporary.write_bytes(body.replace(old, new))
        temporary.chmod(mode)
        os.replace(temporary, file)


def initialise(
    path,
    data,
    template_id,
    brief,
    config=None,
    column_picker=None,
    principal="user",
    primary_data=None,
    data_roles=None,
    exclude_columns=(),
):
    root = Path(path).expanduser().resolve()
    locks = user_data_dir() / "init-locks"
    locks.mkdir(parents=True, exist_ok=True)
    with FileLock(str(locks / (hashlib.sha256(str(root).encode()).hexdigest() + ".lock"))):
        if (root / ".mlca").exists() or (root / ".mlca").is_symlink():
            raise MlcaUserError(
                "This folder already contains an MLCA study or an earlier initialization attempt. Open it to continue, or choose a new project folder. Existing files will not be overwritten."
            )
        created_root = False
        try:
            root.mkdir(parents=True, exist_ok=False)
            created_root = True
        except FileExistsError:
            pass
        try:
            with tempfile.TemporaryDirectory(prefix=".mlca-init-", dir=root) as directory:
                staged = Path(directory)
                _build_initialisation(
                    staged,
                    data,
                    template_id,
                    brief,
                    config,
                    column_picker,
                    principal,
                    primary_data,
                    data_roles,
                    **(
                        {"exclude_columns": tuple(exclude_columns), "final_root": root}
                        if exclude_columns
                        else {}
                    ),
                )
                _rebase_environment(staged, root)
                if (root / ".mlca").exists() or (root / ".mlca").is_symlink():
                    raise MlcaUserError(
                        "Another study appeared during initialization; no existing files were replaced"
                    )
                os.rename(staged / ".mlca", root / ".mlca")
        except BaseException:
            if created_root:
                try:
                    root.rmdir()  # Only remove our new folder if it is still empty.
                except OSError:
                    pass  # Preserve any files another process or the user added.
            raise
        return root
