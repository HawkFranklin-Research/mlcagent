from concurrent.futures import Future
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from textual import work
from textual.app import App
from textual.screen import ModalScreen

from mlca.api import Session
from mlca.config import Config, ProviderConfig, RoleConfig, load, save
from mlca.ui_text import text

from .screens.brief import FormScreen
from .screens.main import MainScreen
from .screens.onboarding import OnboardingScreen
from .screens.project import ProjectScreen
from .screens.report import ReportScreen
from .screens.welcome import WelcomeScreen
from .widgets.event_graph import EventGraph
from .widgets.facts import Facts
from .widgets.log_stream import LogStream
from .widgets.options import Options
from .widgets.status_bar import StatusBar
from .widgets.subgoals import Subgoals


class MlcaApp(App):
    TITLE = text("title")
    CSS = """#panels { height: 2fr; } #event-graph { width: 22%; padding: 1; border: solid $primary; } #center { width: 50%; } #subgoals { height: 1fr; padding: 1; overflow-y: auto; } #options { height: 1fr; padding: 1; overflow-y: auto; } #facts { width: 28%; padding: 1; overflow-y: auto; } #log-stream { height: 1fr; border: solid $accent; } #status-bar { height: 2; }"""
    BINDINGS = [
        ("1", "choose_1", text("choose")),
        ("2", "choose_2", text("choose")),
        ("3", "choose_3", text("choose")),
        ("4", "choose_4", text("choose")),
        ("n", "next", text("next")),
        ("l", "loop", text("loop")),
        ("c", "custom", text("custom")),
        ("f", "confirm", text("confirm")),
        ("b", "branches", text("branches")),
        ("r", "report", text("report")),
        ("u", "usage", text("usage")),
        ("v", "view_figure", text("view_figure")),
        ("t", "unlock", text("unlock")),
        ("ctrl+o", "open", text("open")),
        ("ctrl+i", "init", text("init")),
        ("ctrl+s", "configure", text("configure")),
        ("q", "quit", text("quit")),
    ]

    def __init__(self, project: Path, configure: Any = False) -> None:
        super().__init__()
        self.project = project
        self.configure_first = configure
        self.session = None
        self.busy = False

    def on_mount(self) -> Any:
        self.push_screen(WelcomeScreen())
        if self.configure_first:
            self.action_configure()
        elif (self.project / ".mlca/project.yaml").exists():
            self.open_project(self.project)

    def open_project(self, path: Any) -> Any:
        try:
            if self.session:
                self.session.close()
            self.project = Path(path).expanduser().resolve()
            self.session = Session.open(self.project, client="tui")
            self.session.output_callback = lambda channel, chunk: self.call_from_thread(
                self.write_log, channel + ": " + chunk[-2000:]
            )
            self.session.subscribe(
                lambda record: self.call_from_thread(self.write_log, record.type.value) if self.busy else None
            )
            self.switch_screen(MainScreen())
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def refresh_project(self, options: Any = None) -> Any:
        if not self.session or not isinstance(self.screen, MainScreen):
            return
        status = self.session.status()
        self.screen.query_one(EventGraph).render_state(status)
        self.screen.query_one(Subgoals).render_state(status)
        self.screen.query_one(Facts).render_state(status)
        self.screen.query_one(StatusBar).render_state(status)
        if options is not None:
            self.screen.query_one(Options).render_options(options)
        else:
            self.run_session_action("options", refresh_only=True)

    def write_log(self, value: Any) -> Any:
        if isinstance(self.screen, MainScreen):
            self.screen.query_one(LogStream).write(value)

    @work(thread=True, exclusive=True, group="session")
    def run_session_action(self, method: Any, *args: Any, refresh_only: Any = False) -> Any:
        if self.busy:
            return
        self.busy = True
        try:
            result = getattr(self.session, method)(*args)
            self.call_from_thread(self.write_log, json.dumps(result, default=str, ensure_ascii=False))
            options = result if method == "options" else self.session.options()
            self.call_from_thread(self.refresh_project, options)
            if method == "report":
                self.call_from_thread(self.show_reports, result)
        except Exception as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")
        finally:
            self.busy = False

    def _can_act(self) -> bool:
        if not self.session or isinstance(self.screen, ModalScreen) or self.busy:
            return False
        return True

    def action_open(self) -> Any:
        if self.busy:
            return
        self.push_screen(
            ProjectScreen(self.project), lambda result: self.open_project(result["path"]) if result else None
        )

    def action_init(self) -> Any:
        if self.busy:
            return

        def selected(result: Any) -> Any:
            if result:
                self.initialise_project(result)

        self.push_screen(ProjectScreen(self.project, initialise=True), selected)

    @work(thread=True, exclusive=True, group="init")
    def initialise_project(self, result: Any) -> Any:
        from mlca.project.init import initialise

        try:
            path = initialise(
                Path(result["path"]).expanduser(),
                [Path(result["data"]).expanduser()],
                result["template"],
                {k: result[k] for k in ["aim", "target", "unit", "event_column"]},
                column_picker=self.pick_column,
            )
            self.call_from_thread(self.open_project, path)
        except Exception as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")

    def pick_column(self, field: str, available: list[str]) -> str:
        answer = Future()

        def selected(result):
            answer.set_result(result["column"] if result else "")

        self.call_from_thread(
            self.push_screen,
            FormScreen(f"Choose {field}. Available columns: {', '.join(available)}", [("column", field, "")]),
            selected,
        )
        return answer.result()

    def action_configure(self) -> Any:
        if self.busy:
            return

        def selected(result: Any) -> Any:
            if not result:
                return
            try:
                config = load()
                kind = result["kind"]
                provider = ProviderConfig(
                    kind=kind,
                    api_key_env=result["api_env"] or None,
                    base_url=result["base_url"] or None,
                    request_cost_bound_usd=float(result["request_bound"])
                    if result["request_bound"]
                    else None,
                )
                providers = {**config.providers, "configured": provider}
                roles = {**config.roles}
                for role in ["navigator", "worker"]:
                    if result[role + "_model"]:
                        roles[role] = RoleConfig(provider="configured", model=result[role + "_model"])
                updated = config.model_copy(update={"providers": providers, "roles": roles})
                updated.sandbox.allow_level_b = result["allow_b"].lower() == "yes"
                save(Config.model_validate(updated.model_dump()))
                self.notify(text("saved"))
                if self.session:
                    self.session.close()
                    self.open_project(self.project)
            except Exception as exc:
                self.notify(str(exc), severity="error")

        self.push_screen(OnboardingScreen(load()), selected)

    def action_choose_1(self) -> Any:
        if self._can_act():
            self.run_session_action("choose", "1")

    def action_choose_2(self) -> Any:
        if self._can_act():
            self.run_session_action("choose", "2")

    def action_choose_3(self) -> Any:
        if self._can_act():
            self.run_session_action("choose", "3")

    def action_choose_4(self) -> Any:
        if self._can_act():
            self.run_session_action("choose", "4")

    def action_next(self) -> Any:
        if self._can_act():
            self.run_session_action("next")

    def action_custom(self) -> Any:
        if self._can_act():
            self.push_screen(
                FormScreen(text("custom"), [("instruction", text("custom"), "")]),
                lambda result: self.run_session_action("custom", result["instruction"]) if result else None,
            )

    def action_confirm(self) -> Any:
        if self._can_act():
            self.push_screen(
                FormScreen(text("confirm"), [("goal", text("subgoal"), ""), ("note", text("note"), "")]),
                lambda result: (
                    self.run_session_action("confirm", result["goal"], result["note"]) if result else None
                ),
            )

    def action_unlock(self) -> Any:
        if self._can_act():
            self.push_screen(
                FormScreen(
                    text("unlock"),
                    [("phrase", text("unlock_phrase"), ""), ("reason", text("unlock_reason"), "")],
                ),
                lambda result: (
                    self.run_session_action("unlock_test", result["phrase"], result["reason"])
                    if result
                    else None
                ),
            )

    def action_loop(self) -> Any:
        if self._can_act():
            self.push_screen(
                FormScreen(text("loop"), [("event", text("events"), "model")]),
                lambda result: self.run_session_action("loop", result["event"]) if result else None,
            )

    def action_branches(self) -> Any:
        if self._can_act():
            available = self.session.branches.list()
            self.push_screen(
                FormScreen(
                    text("branches") + "\n" + json.dumps(available),
                    [("name", text("branch_name"), ""), ("from_id", text("from_id"), "")],
                ),
                lambda result: (
                    self.run_session_action("branch", result["name"], result["from_id"])
                    if result and result["from_id"]
                    else self.run_session_action("checkout", result["name"])
                    if result
                    else None
                ),
            )

    def action_report(self) -> Any:
        if self._can_act():
            self.run_session_action("report", "all")

    def action_usage(self) -> Any:
        if self._can_act():
            self.push_screen(
                ReportScreen("```json\n" + json.dumps(self.session.status()["usage"], indent=2) + "\n```")
            )

    def action_quit(self) -> Any:
        if self.busy:
            return
        if self.session:
            self.session.close()
        self.exit()

    def show_reports(self, paths: dict) -> None:
        sections = []
        for name, relative in paths.items():
            path = self.project / relative
            sections.append("## " + name + "\n" + str(path) + "\n")
            if path.suffix == ".md":
                sections.append(path.read_text())
            else:
                sections.append("```json\n" + path.read_text()[:20000] + "\n```")
        self.push_screen(ReportScreen("\n".join(sections)))

    def action_view_figure(self) -> None:
        if not self._can_act():
            return
        figures = {
            f["path"]: f
            for step in self.session.state.steps
            if step["status"] == "completed"
            for f in step.get("figures", [])
        }

        def selected(result: dict | None) -> None:
            if not result:
                return
            relative = result["figure"]
            from mlca.paths import contained, sha256

            path = self.project / relative
            if (
                relative not in figures
                or not contained(path, self.project / ".mlca/steps")
                or sha256(path) != figures[relative]["sha256"]
            ):
                self.notify(text("failed"), severity="error")
                return
            viewer = shutil.which("open" if sys.platform == "darwin" else "xdg-open")
            if viewer:
                subprocess.Popen([viewer, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.notify(str(path))

        self.push_screen(
            FormScreen(text("view_figure"), [("figure", text("figure_path"), next(iter(figures), ""))]),
            selected,
        )
