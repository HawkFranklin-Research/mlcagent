import json
import os
import shutil
import sys
import traceback
from pathlib import Path
from typing import Any

import typer
import yaml
from rich import print as rich_print

from mlca import __version__
from mlca.api import Session
from mlca.config import load
from mlca.errors import MlcaUserError
from mlca.ui_text import text

app = typer.Typer(invoke_without_command=True, no_args_is_help=False)
mcp_app = typer.Typer(invoke_without_command=True)
app.add_typer(mcp_app, name="mcp")
templates_app = typer.Typer()
approvals_app = typer.Typer(invoke_without_command=True)
app.add_typer(approvals_app, name="approvals")
app.add_typer(templates_app, name="templates")


def output(value: Any, json_output: Any = False) -> Any:
    if json_output:
        print(json.dumps(value, default=str, ensure_ascii=False))
    else:
        rich_print(value)


def _path(ctx: Any) -> Any:
    return ctx.obj["project"]


@app.callback()
def root(
    ctx: typer.Context,
    project: Path = typer.Option(Path("."), "--project", "-p"),
    version: bool = typer.Option(False, "--version"),
) -> Any:
    ctx.obj = {"project": project.resolve()}
    if version:
        print(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        from mlca.tui.app import MlcaApp

        MlcaApp(project=project.resolve()).run()


@mcp_app.callback()
def mcp_command(
    ctx: typer.Context, project: Path | None = typer.Option(None), mode: str | None = typer.Option(None)
):
    if mode is not None and mode not in {"brain", "driver"}:
        raise MlcaUserError("Mode must be brain or driver")
    if ctx.invoked_subcommand is None:
        from mlca.mcp.server import serve

        serve(project or _path(ctx), mode)


@mcp_app.command("doctor")
def mcp_doctor():
    import asyncio

    from mlca.mcp.install import client_status
    from mlca.mcp.server import probe

    result = asyncio.run(probe())
    result["clients"] = client_status()
    output(result, True)


@mcp_app.command("install")
def mcp_install(
    ctx: typer.Context,
    client: str = typer.Option(...),
    scope: str = typer.Option("user"),
    mode: str = typer.Option("brain"),
    yes: bool = typer.Option(False, "--yes"),
    with_skill: bool = typer.Option(False, "--with-skill"),
):
    from mlca.mcp.install import install
    from mlca.mcp.permissions import guidance

    print(install(client, scope, mode, _path(ctx), yes, with_skill))
    if client != "claude":
        # Preserve valid generic JSON on stdout; setup advice is separate.
        typer.echo(guidance(client, _path(ctx)), err=True)


@app.command()
def web(ctx: typer.Context, port: int = typer.Option(8000, min=1, max=65535)) -> None:
    from mlca.web import serve

    serve(_path(ctx), port)


@app.command("init")
def init_project(
    path: Path = typer.Argument(Path(".")),
    data: list[Path] = typer.Option([], "--data"),
    template: str = typer.Option("tabular_classification", "--template"),
    brief_file: Path | None = typer.Option(None, "--brief-file"),
) -> Any:
    from mlca.project.init import initialise, resolve_column
    from mlca.templates.registry import get
    from mlca.tui.banner import print_banner

    if not (data and brief_file):
        print_banner()
    if not data:
        data = [Path(typer.prompt(text("data")))]
    workflow = get(template)
    brief = (
        yaml.safe_load(brief_file.read_text(encoding="utf-8"))
        if brief_file
        else {q["id"]: typer.prompt(q["text"]) for q in workflow.spec.brief_questions}
    )

    def pick_column(field, available):
        typer.echo(f"Available columns for {field}: {', '.join(available)}")
        return resolve_column(typer.prompt(f"Choose the {field} column"), available, field)

    output(
        {
            "project": str(
                initialise(
                    path, data, template, brief, column_picker=pick_column if brief_file is None else None
                )
            )
        }
    )


@app.command()
def status(
    ctx: typer.Context, recheck: bool = False, json_output: bool = typer.Option(False, "--json")
) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.status(recheck), json_output)


@app.command()
def options(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.options(), json_output)


@app.command()
def choose(ctx: typer.Context, n: str, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.choose(n), json_output)


@app.command()
def custom(ctx: typer.Context, instruction: str, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.custom(instruction), json_output)


@app.command("abandon-step")
def abandon_step(ctx: typer.Context, step_id: str, reason: str = typer.Option(...)):
    with Session.open(_path(ctx)) as session:
        output(session.abandon_step(step_id, reason))


@app.command("next")
def next_event(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.next(), json_output)


@app.command()
def loop(ctx: typer.Context, event: str, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.loop(event), json_output)


@app.command("goto")
def goto_event(ctx: typer.Context, event: str, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.goto(event), json_output)


@app.command()
def confirm(
    ctx: typer.Context, subgoal: str, note: str, json_output: bool = typer.Option(False, "--json")
) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.confirm(subgoal, note), json_output)


@app.command("unlock-test")
def unlock_test(
    ctx: typer.Context,
    phrase: str = typer.Option("", "--phrase"),
    reason: str = typer.Option("First planned test evaluation", "--reason"),
    json_output: bool = typer.Option(False, "--json"),
) -> Any:
    if not phrase:
        phrase = typer.prompt(text("unlock_phrase"))
    with Session.open(_path(ctx)) as session:
        output(session.unlock_test(phrase, reason), json_output)


@app.command()
def branch(
    ctx: typer.Context,
    name: str,
    from_id: str = typer.Option(..., "--from"),
    json_output: bool = typer.Option(False, "--json"),
) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.branch(name, from_id), json_output)


@app.command()
def checkout(ctx: typer.Context, name: str, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.checkout(name), json_output)


@app.command()
def branches(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.branches.list(), json_output)


@app.command("log")
def log_records(
    ctx: typer.Context,
    verify: bool = typer.Option(False, "--verify"),
    branch_name: str | None = typer.Option(None, "--branch"),
    json_output: bool = typer.Option(False, "--json"),
) -> Any:
    with Session.open(_path(ctx)) as session:
        output(
            session.store.verify()
            if verify
            else [
                r.model_dump(mode="json")
                for r in session.branches.records(branch_name or session.branch_name)
            ],
            json_output,
        )


@app.command("replay")
def replay_project(
    ctx: typer.Context,
    verify: bool = typer.Option(False, "--verify"),
    json_output: bool = typer.Option(False, "--json"),
) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.verify_scripts() if verify else session.state.model_dump(mode="json"), json_output)


@app.command()
def report(
    ctx: typer.Context, kind: str = typer.Argument("all"), json_output: bool = typer.Option(False, "--json")
) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.report(kind), json_output)


@app.command()
def metrics(
    ctx: typer.Context,
    branch: str | None = typer.Option(None),
    json_output: bool = typer.Option(False, "--json"),
    out: Path | None = typer.Option(None),
):
    from mlca.evaluation.metrics import generate

    with Session.open(_path(ctx)) as session:
        with session.mutation():
            output(generate(session, branch, out), json_output)


@app.command()
def usage(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.status()["usage"], json_output)


@app.command()
def package(
    ctx: typer.Context,
    spec: str,
    approve: bool = typer.Option(False, "--approve"),
    json_output: bool = typer.Option(False, "--json"),
) -> Any:
    with Session.open(_path(ctx)) as session:
        output(session.package(spec, approve), json_output)


@approvals_app.callback()
def approval_list(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        with Session.open(_path(ctx)) as session:
            output(session.approvals())


@approvals_app.command("approve")
def approval_approve(
    ctx: typer.Context, request_id: str, note: str = typer.Option(""), phrase: str = typer.Option("")
):
    with Session.open(_path(ctx)) as session:
        request = next((r for r in session.approvals() if r["request_id"] == request_id), None)
        if request and request["kind"] == "unlock_test" and not phrase:
            phrase = typer.prompt(text("unlock_phrase"))
        output(session.resolve_approval(request_id, "approved", note, phrase))


@approvals_app.command("decline")
def approval_decline(ctx: typer.Context, request_id: str, note: str = typer.Option("")):
    with Session.open(_path(ctx)) as session:
        output(session.resolve_approval(request_id, "declined", note))


@app.command("config")
def configuration(ctx: typer.Context, operation: str = typer.Argument("show")) -> Any:
    if operation == "edit":
        from mlca.tui.app import MlcaApp

        MlcaApp(project=_path(ctx), configure=True).run()
    elif operation in {"show", "check"}:
        output(load(_path(ctx)).model_dump(mode="json"))
    else:
        raise MlcaUserError("Use config show, edit or check")


@app.command()
def doctor(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> Any:
    config = load(_path(ctx))
    from mlca.sandbox.level import explanation

    if not json_output:
        from mlca.tui.banner import print_banner

        print_banner()
    output(
        {
            "python": sys.version.split()[0],
            "uv": shutil.which("uv"),
            "bwrap": shutil.which("bwrap"),
            "sandbox_detected": "A (unverified until execution)"
            if shutil.which("bwrap") and sys.platform == "linux"
            else "B (opt-in required)",
            "sandbox_guidance": explanation(),
            "sandbox_allow_level_b": config.sandbox.allow_level_b,
            "providers": {
                name: {
                    "kind": p.kind,
                    "credential_env_present": bool(os.environ.get(p.api_key_env)) if p.api_key_env else None,
                }
                for name, p in config.providers.items()
            },
            "roles": list(config.roles),
        },
        json_output,
    )


@templates_app.command("list")
def list_templates(json_output: bool = typer.Option(False, "--json")) -> Any:
    from mlca.templates.registry import available

    output({k: str(v) for k, v in available().items()}, json_output)


@templates_app.command("validate")
def validate_template(path: Path, json_output: bool = typer.Option(False, "--json")) -> Any:
    from mlca.templates.loader import load as load_template

    workflow = load_template(path)
    output(
        {
            "valid": True,
            "template": workflow.spec.id,
            "events": len(workflow.events),
            "sha256": workflow.sha256,
        },
        json_output,
    )


def main() -> Any:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        app()
    except MlcaUserError as exc:
        from rich.console import Console

        Console(stderr=True).print(str(exc), markup=False)
        raise SystemExit(1) from exc
    except Exception:
        # No traceback containing credentials is emitted to stdout; local tracebacks are scrubbed.
        from mlca.config import redact

        text_value = redact(traceback.format_exc(), load())
        directory = Path.cwd() / ".mlca/log"
        if directory.exists():
            with (directory / "errors.log").open("a", encoding="utf-8") as stream:
                stream.write(text_value)
        from rich.console import Console

        Console(stderr=True).print(text("failed"), markup=False)
        raise SystemExit(1) from None
