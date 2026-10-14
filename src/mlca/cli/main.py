import json
import os
import shutil
import sys
import traceback
from pathlib import Path
from typing import Any

import typer
import yaml
from click import edit as edit_text
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
usage_app = typer.Typer(invoke_without_command=True)
app.add_typer(usage_app, name="usage")
bench_app = typer.Typer()
app.add_typer(bench_app, name="bench")
bio_bench_app = typer.Typer()
app.add_typer(bio_bench_app, name="bio-bench")
auth_app = typer.Typer()
app.add_typer(auth_app, name="auth")


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


@auth_app.command("status")
def auth_status():
    from mlca.llm.credentials import resolve

    config = load()
    output(
        {
            name: {
                "kind": p.kind,
                "credential_available": bool(resolve(p.api_key_env)) if p.api_key_env else None,
                "storage": "OS keyring"
                if p.api_key_env and p.api_key_env.startswith("MLCA_KEYRING_")
                else "environment / session",
            }
            for name, p in config.providers.items()
        },
        True,
    )


@app.command("signin")
def signin(headless: bool = False, provider: str = "openrouter"):
    if provider == "openai":
        return openai_signin(headless)
    if provider != "openrouter":
        raise MlcaUserError("Sign-in provider must be openrouter or openai")
    """Connect a user-owned OpenRouter key and select the free router."""
    from mlca.config import save
    from mlca.llm.openrouter_auth import Flow, configure_free, secure_backend, store_key

    # Separate CLI commands require secure persistence; a process-only key would vanish.
    secure_backend()
    flow = Flow(headless=headless)
    try:
        typer.echo("Authorize OpenRouter at: " + flow.url)
        if headless:
            flow.accept(typer.prompt("Authorization code", hide_input=True))
        else:
            flow.open_browser()
            flow.wait()
        reference = store_key(flow.exchange())
        save(configure_free(load(), reference))
    finally:
        flow.close()
    typer.echo("OpenRouter connected. Navigator and Worker use openrouter/free. Free requests have quotas.")


def openai_signin(headless):
    from mlca.llm.openai_auth import OpenAIFlow, save_profile

    config = load()
    if not config.chatgpt_auth.client_id:
        raise MlcaUserError("ChatGPT sign-in is coming soon: register MLCA and set chatgpt_auth.client_id")
    if not typer.confirm("Allow MLCA to request your ChatGPT plan allowance and its caps?"):
        return
    flow = OpenAIFlow(config.chatgpt_auth.client_id)
    try:
        typer.echo(flow.url)
        if headless:
            flow.accept(typer.prompt("Complete redirected URL", hide_input=True))
        else:
            flow.open_browser()
            flow.wait()
        save_profile(flow.exchange())
    finally:
        flow.close()
    typer.echo(
        "ChatGPT authorized. Select ChatGPT plan and an account model in Models; no default model was selected."
    )


@app.command("signout")
def signout_command(provider: str = "openrouter"):
    if provider == "openai":
        from mlca.llm.openai_auth import signout as openai_signout

        client_id = load().chatgpt_auth.client_id
        if not client_id:
            raise MlcaUserError("No MLCA ChatGPT registration configured")
        revoked = openai_signout(client_id)
        typer.echo(
            "Local ChatGPT tokens removed. "
            + (
                "Remote renewable session revoked."
                if revoked
                else "Remote revocation not confirmed; disconnect MLCA in ChatGPT settings."
            )
        )
        return
    if provider != "openrouter":
        raise MlcaUserError("Sign-out provider must be openrouter or openai")
    from mlca.llm.openrouter_auth import signout

    signout()
    typer.echo(
        "Local OpenRouter credential removed. Revoke the remote key at https://openrouter.ai/settings/keys"
    )


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
    primary_data: str | None = typer.Option(None, "--primary-data"),
    measurement_arm: str = typer.Option("worker", "--measurement-arm"),
) -> Any:
    if measurement_arm not in {"worker", "reference"}:
        raise MlcaUserError("Measurement arm must be worker or reference")
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
        else {
            q["id"]: typer.prompt(q["text"], default="", show_default=False)
            for q in workflow.spec.brief_questions
        }
    )

    def pick_column(field, available):
        typer.echo(f"Available columns for {field}: {', '.join(available)}")
        return resolve_column(typer.prompt(f"Choose the {field} column"), available, field)

    output(
        {
            "project": str(
                initialise(
                    path,
                    data,
                    template,
                    brief,
                    config={"measurement_arm": measurement_arm},
                    column_picker=pick_column if brief_file is None else None,
                    primary_data=primary_data,
                )
            )
        }
    )


@app.command("study")
def study(
    ctx: typer.Context,
    target: str | None = None,
    duration: str | None = None,
    event_column: str | None = None,
    unit: str | None = None,
    aim: str | None = None,
    primary_data: str | None = None,
):
    """Resolve deferred study fields during Onboard; no model call."""
    answers = {
        k: v
        for k, v in {
            "target": target,
            "duration": duration,
            "event_column": event_column,
            "unit": unit,
            "aim": aim,
        }.items()
        if v is not None
    }
    if duration is not None:
        answers["target"] = duration
    with Session.open(_path(ctx)) as session:
        output(session.resolve_study(answers, primary_data))


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


@app.command("models")
def models_command(
    select: list[str] = typer.Option([], "--select", help="Add a model ID to the saved shortlist"),
    unselect: list[str] = typer.Option([], "--unselect", help="Remove a model ID from the shortlist"),
    out: Path | None = typer.Option(None, help="Also write the snapshot CSV into this folder"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Pull the OpenRouter catalogue: free models plus your shortlist, saved as a dated CSV."""
    from mlca.config import ProviderConfig, save
    from mlca.llm.catalog import fetch, snapshot

    config = load()
    if select or unselect:
        chosen = [m for m in config.catalog.selected if m not in unselect]
        chosen += [m for m in select if m not in chosen]
        config.catalog.selected = chosen
        save(config)
    provider = next(
        (p for p in config.providers.values() if p.kind == "openrouter"), ProviderConfig(kind="openrouter")
    )
    models = fetch(provider)
    path, missing = snapshot(provider, config.catalog.selected, out, models)
    rows = [m for m in models if m.free or m.id in config.catalog.selected]
    if json_output:
        output({"snapshot": str(path), "missing": missing, "models": [m.id for m in rows]}, True)
        return
    for m in sorted(rows, key=lambda m: (m.id not in config.catalog.selected, -(m.coding_index or -1))):
        group = "selected" if m.id in config.catalog.selected else "free"
        note = " (router)" if m.router else "" if m.text_only else " (not text-only)"
        coding = f"{m.coding_index:.1f}" if m.coding_index is not None else "-"
        typer.echo(f"{group:<9} {m.id:<55} coding {coding:>5}  json {'yes' if m.json_output else 'no'}{note}")
    if missing:
        typer.echo("Not listed by OpenRouter: " + ", ".join(missing))
    typer.echo("Snapshot: " + str(path))


@bench_app.command("run")
def bench_run(
    task_card: Path,
    runs: int = typer.Option(1),
    out: Path = typer.Option(...),
    mode: str = typer.Option("driver"),
    budget_usd: float | None = typer.Option(None),
    seed: int = typer.Option(42),
    lock_models: bool = typer.Option(False, "--lock-models"),
):
    from mlca.evaluation.bench import run

    output(run(task_card, runs, out, mode, budget_usd, seed, lock_models), True)


@bio_bench_app.command("run")
def bio_bench_run(task_card: Path, runs: int = typer.Option(1), out: Path = typer.Option(...)):
    from mlca.evaluation.bench import run

    output(run(task_card, runs, out, bio=True), True)


@bench_app.command("summarize")
def bench_summarize(directory: Path):
    from mlca.evaluation.bench import summarize

    output(summarize(directory), True)


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


@usage_app.callback()
def usage(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json"),
    csv_file: Path | None = typer.Option(None, "--csv"),
) -> Any:
    if ctx.invoked_subcommand is not None:
        return
    with Session.open(_path(ctx)) as session:
        from mlca.llm.usage import export_csv

        data = session.status()["usage"]
        if csv_file:
            export_csv(session.root, csv_file)
        if json_output:
            output(data, True)
        else:
            output({"totals": data["totals"]})
            for model, group in data["groups"]["model_reported"].items():
                output({"model_reported": model, **group})


@usage_app.command("backfill")
def usage_backfill(ctx: typer.Context):
    from mlca.llm.backfill import backfill

    with Session.open(_path(ctx)) as session:
        with session.mutation():
            output(backfill(session), True)


@usage_app.command("import")
def usage_import(
    ctx: typer.Context,
    client: str = typer.Option(...),
    session_file: str = typer.Option(..., "--session"),
    since: str | None = typer.Option(None, "--from"),
    until: str | None = typer.Option(None, "--to"),
):
    from mlca.evaluation.import_usage import import_usage

    with Session.open(_path(ctx)) as session:
        with session.mutation():
            output(import_usage(session, client, session_file, since, until), True)


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
    ctx: typer.Context,
    request_id: str,
    note: str = typer.Option(""),
    phrase: str = typer.Option(""),
    edit: bool = typer.Option(False, "--edit"),
):
    with Session.open(_path(ctx)) as session:
        request = next((r for r in session.approvals() if r["request_id"] == request_id), None)
        if request and request["kind"] == "unlock_test" and not phrase:
            phrase = typer.prompt(text("unlock_phrase"))
        proposed = None
        if request and request["kind"] == "study_fields":
            output({"proposed_by": request["requested_by"], "proposed": request.get("proposed", {})})
            if edit:
                edited = edit_text(json.dumps(request.get("proposed", {}), indent=2))
                if edited is None:
                    raise MlcaUserError("Study-field approval cancelled")
                proposed = json.loads(edited)
        elif edit:
            raise MlcaUserError("--edit applies to study_fields approvals only")
        output(session.resolve_approval(request_id, "approved", note, phrase, proposed))


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
    from mlca.llm.credentials import resolve
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
                    "credential_available": bool(resolve(p.api_key_env)),
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


questions_app = typer.Typer(invoke_without_command=True)
app.add_typer(questions_app, name="questions")


@questions_app.callback()
def questions_list(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        with Session(_path(ctx)) as session:
            output(session.questions(), True)


@questions_app.command("answer")
def question_answer(
    ctx: typer.Context,
    question_id: str,
    index: int | None = None,
    default: bool = False,
    free_text: str | None = None,
):
    with Session(_path(ctx)) as session:
        output(session.answer_question(question_id, index, default, free_text), True)


@app.command("turn")
def guided_turn(ctx: typer.Context):
    with Session(_path(ctx)) as session:
        output(session.turn(), True)


@app.command("autopilot")
def autopilot(ctx: typer.Context, max_steps: int = 100):
    with Session(_path(ctx)) as session:
        output(session.autopilot(max_steps), True)


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
    except Exception as exc:
        # No traceback containing credentials is emitted to stdout; local tracebacks are scrubbed.
        from mlca.config import redact

        text_value = redact(traceback.format_exc(), load())
        directory = Path.cwd() / ".mlca/log"
        if directory.exists():
            with (directory / "errors.log").open("a", encoding="utf-8") as stream:
                stream.write(text_value)
        from rich.console import Console

        Console(stderr=True).print(redact(str(exc), load()) or text("failed"), markup=False)
        raise SystemExit(1) from None
