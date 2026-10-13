import json
import shutil
import subprocess
import sys
from concurrent.futures import Future
from pathlib import Path
from typing import Any

from textual import work
from textual.app import App
from textual.screen import ModalScreen
from textual.widgets import Static

from mlca.api import Session
from mlca.config import Config, load, save
from mlca.evaluation.timing import Activity
from mlca.ui_text import text

from .screens.brief import FormScreen
from .screens.main import MainScreen
from .screens.onboarding import OnboardingScreen
from .screens.project import ProjectScreen
from .screens.report import ReportScreen
from .screens.welcome import WelcomeScreen
from .widgets.event_graph import EventGraph
from .widgets.facts import Facts
from .widgets.journey import Journey
from .widgets.log_stream import LogStream, result_summary
from .widgets.options import Options
from .widgets.progress import Progress
from .widgets.status_bar import StatusBar
from .widgets.subgoals import Subgoals


class MlcaApp(App):
    TITLE = text("title")
    CSS = """#panels { height: 1fr; } #event-graph { width: 22; padding: 1 1; border-right: tall $panel; } #center { width: 1fr; } #subgoals { height: auto; max-height: 9; padding: 1 2; overflow-y: auto; } #options { height: 1fr; min-height: 8; padding: 0 2; overflow-y: auto; } #facts { width: 30; padding: 1; overflow-y: auto; } #log-stream { height: 10; border: solid $accent; } #status-bar { height: auto; max-height: 4; }"""
    BINDINGS = []

    def __init__(self, project: Path, configure: Any = False) -> None:
        super().__init__()
        self.project = project
        self.configure_first = configure
        self.session = None
        self.busy = False
        self.pending_config = None
        self.external_client = None
        self._external_head = None
        self.activity = Activity()

    def on_mount(self) -> Any:
        self.set_interval(1, self.poll_external)
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
            self.session.timing_context = self.activity.value
            self.session.output_callback = lambda channel, chunk: self.call_from_thread(
                self.write_log, channel + ": " + chunk[-2000:]
            )
            self.session.progress_callback = lambda payload: self.call_from_thread(
                self.update_progress, payload
            )
            self.session.subscribe(
                lambda record: self.call_from_thread(self.record_arrived, record) if self.busy else None
            )
            self.sync_external_mode()
            self.switch_screen(MainScreen())
        except Exception as exc:
            self.notify(str(exc), severity="error")

    def sync_external_mode(self):
        from mlca.live import clients

        attached = clients(self.session)
        self.external_client = attached[-1] if attached else None
        self.session.mode = self.external_client["mode"] if self.external_client else "driver"
        self.session.client.disabled = self.session.mode == "brain"

    @work(thread=True, exclusive=True, group="external-poll")
    def poll_external(self):
        if not self.session or self.busy:
            return
        try:
            self.session.branch_name = self.session.branches.current()
            records = self.session.store.read()
            self.sync_external_mode()
            from mlca.live import project_busy

            locked = project_busy(self.session)
            key = (
                records[-1].id if records else None,
                self.session.branch_name,
                (self.external_client or {}).get("session_id"),
                locked,
            )
            if key != self._external_head:
                self._external_head = key
                options = self.session.guided_view()
                active = self.session.active_step()
                if active or locked:
                    options = [{**o, "disabled": not o["id"].startswith("human:")} for o in options]
                self.call_from_thread(self.refresh_project, options)
        except Exception as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")

    def decorated_status(self) -> dict:
        """Session status plus the presentation facts every panel needs."""
        status = self.session.status()
        status["external_client"] = self.external_client
        from mlca.llm.status import roles
        from mlca.llm.usage import read

        status["model_status"] = roles(self.session.config, read(self.session.root))
        from mlca.llm.quota import for_provider

        for info in status["model_status"].values():
            info["quota"] = for_provider(
                self.session.root, info["provider"], self.session.config.providers[info["provider"]]
            )
        from mlca.project.init import study_ready
        from mlca.ui_text import EVENT_TITLES

        state, workflow = self.session.state, self.session.workflow
        status["event_titles"] = {
            e: EVENT_TITLES.get(e, workflow.events[e].title) for e in workflow.spec.events
        }
        last = {}
        for step in state.steps:
            last[step["event_id"]] = step["status"]
        status["failed_events"] = {e for e, s in last.items() if s == "failed"}
        status["study_detail"] = study_ready(state)[1]
        return status

    def with_connect_card(self, options):
        """Driver mode without any model: offer connecting as the first card."""
        if self.external_client or self.session.config.roles or any(o["id"] == "ui:connect" for o in options):
            return options
        card = {
            "id": "ui:connect",
            "title": "Connect an AI model",
            "description": "Sign in free with OpenRouter, or use an OpenAI key or a local model.",
            "produces": "Navigator and Worker ready; AI-proposed cards and custom steps",
            "source": "template",
        }
        return [card, *options]

    def refresh_project(self, options: Any = None) -> Any:
        if not self.session or not isinstance(self.screen, MainScreen):
            return
        status = self.decorated_status()
        count = len(status["approvals"])
        self.screen.query_one("#approvals-banner", Static).update(
            f"{count} approval(s) waiting (a)" if count else ""
        )
        self.screen.query_one(Journey).render_state(
            status, self.session.branches.records(), self.session.workflow
        )
        self.screen.query_one(EventGraph).render_state(status)
        self.screen.query_one(Subgoals).render_state(status)
        self.screen.query_one(Facts).render_state(status)
        self.screen.query_one(StatusBar).render_state(status)
        if options is None and self.external_client:
            options = self.session.guided_view()
        if options is not None:
            options = self.with_connect_card(options)
            records = self.session.branches.records()
            anchor = next((r.id for r in reversed(records) if r.type.value == "OptionsProposed"), None)
            self.activity.begin(anchor)
            self.call_later(self.screen.query_one(Options).render_options, options)
        else:
            self.run_session_action("options", refresh_only=True)

    def on_key(self, event):
        if not self.busy:
            self.activity.touch()

    def on_mouse_move(self, event):
        if not self.busy:
            self.activity.touch()

    def on_mouse_down(self, event):
        if not self.busy:
            self.activity.touch()

    def write_log(self, value: Any) -> Any:
        if isinstance(self.screen, MainScreen):
            self.screen.query_one(LogStream).write(value)

    def record_arrived(self, record):
        if isinstance(self.screen, MainScreen):
            self.write_log(json.dumps(record.model_dump(mode="json"), ensure_ascii=False))
            self.screen.query_one(Journey).render_state(
                self.decorated_status(), self.session.branches.records(), self.session.workflow
            )

    def action_engine_log(self):
        if isinstance(self.screen, MainScreen):
            log = self.screen.query_one(LogStream)
            log.display = not log.display

    @work(thread=True, exclusive=True, group="session")
    def run_session_action(self, method: Any, *args: Any, refresh_only: Any = False) -> Any:
        if self.busy:
            return
        self.busy = True
        role = self.session.config.roles.get("navigator" if method == "options" else "worker")
        model = role.model if role else "engine / template"
        self.call_from_thread(self.start_progress, method, model)
        error = None
        note = None
        try:
            result = (
                getattr(self.session, method)(True)
                if method == "options"
                else getattr(self.session, method)(*args)
            )
            self.call_from_thread(self.write_log, result_summary(method, result))
            if (
                method == "custom"
                and isinstance(result, dict)
                and result.get("decision") in {"reject", "other_event"}
            ):
                from mlca.ui_text import scope_message

                note = scope_message(result)
                self.call_from_thread(self.notify, note, severity="warning", timeout=12)
            changed_models = False
            if self.pending_config and not self.session.active_step():
                updated = self.pending_config
                try:
                    self.session.change_models(updated)
                    save(updated)
                    changed_models = True
                except Exception as exc:
                    self.call_from_thread(
                        self.notify,
                        "Model switch was not applied: " + self.session.redact(str(exc)),
                        severity="error",
                    )
                self.pending_config = None
            options = result if method == "options" and not changed_models else self.session.options(True)
            self.call_from_thread(self.refresh_project, options)
            if method == "report":
                self.call_from_thread(self.show_reports, result)
        except Exception as exc:
            error = self.session.redact(str(exc))
            self.call_from_thread(self.notify, error, severity="error")
        finally:
            self.call_from_thread(self.finish_progress, error, note)
            self.busy = False

    def start_progress(self, operation, model):
        if isinstance(self.screen, MainScreen):
            self.screen.query_one(Progress).start(operation, model)

    def update_progress(self, payload):
        if isinstance(self.screen, MainScreen):
            self.screen.query_one(Progress).phase(payload)

    def finish_progress(self, error=None, note=None):
        if isinstance(self.screen, MainScreen):
            self.screen.query_one(Progress).finish(error, note)
            from mlca.llm.status import roles
            from mlca.llm.usage import read

            status = self.session.status()
            status["model_status"] = roles(self.session.config, read(self.session.root))
            from mlca.llm.quota import for_provider

            for info in status["model_status"].values():
                info["quota"] = for_provider(
                    self.session.root, info["provider"], self.session.config.providers[info["provider"]]
                )
            self.screen.query_one(StatusBar).render_state(status)

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
                self.prepare_initialisation(result)

        self.push_screen(ProjectScreen(self.project, initialise=True), selected)

    def prepare_initialisation(self, result):
        path = Path(result["path"]).expanduser().resolve()
        if not (path / ".mlca").exists():
            self.initialise_project(result)
            return
        from mlca.tui.screens.existing_project import ExistingProjectScreen

        def selected(choice):
            if choice == "open":
                self.open_project(path)
            elif choice == "fresh":
                self.initialise_project({**result, "fresh_parent": str(path)})
            elif choice == "archive":

                def confirmed(answer):
                    if not answer:
                        return
                    try:
                        from mlca.project.restart import archive_incomplete

                        archived = archive_incomplete(path, answer["phrase"])
                        self.notify("Earlier attempt archived at " + str(archived))
                        self.initialise_project(result)
                    except Exception as exc:
                        self.notify(str(exc), severity="error")

                self.push_screen(
                    FormScreen(
                        "Archive the incomplete setup, retaining its files. Then retry this new-study form.",
                        [("phrase", "Type ARCHIVE INCOMPLETE SETUP", "")],
                    ),
                    confirmed,
                )

        self.push_screen(ExistingProjectScreen(path), selected)

    @work(thread=True, exclusive=True, group="init")
    def initialise_project(self, result: Any) -> Any:
        from mlca.project.init import initialise

        try:
            destination = Path(result["path"]).expanduser()
            if result.get("fresh_parent"):
                from mlca.project.restart import reserve_fresh_study

                destination = reserve_fresh_study(Path(result["fresh_parent"]))
            path = initialise(
                destination,
                [Path(p).expanduser() for p in result["data"]],
                result["template"],
                {
                    k: result[k]
                    for k in ["aim", "target", "duration", "unit", "event_column", "repeated_subjects"]
                },
                primary_data=result["primary_data"],
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
        def selected(result: Any) -> Any:
            if not result:
                if self.session and not self.busy:
                    self.refresh_project()
                return
            try:
                updated = Config.model_validate(result["config"])
                if self.session and (self.busy or self.session.active_step()):
                    self.pending_config = updated
                    self.notify("Model change queued until the current step finishes")
                else:
                    if self.session:
                        self.session.change_models(updated)
                    save(updated)
                    self.notify("Models saved; changes apply to the next request")
                    if self.session:
                        self.refresh_project()
            except Exception as exc:
                self.notify(str(exc), severity="error")

        current = self.session.config if self.session else load()
        self.push_screen(OnboardingScreen(current, project=self.project), selected)

    def check_action(self, action, parameters):
        if action == "select_card":
            if not isinstance(self.screen, MainScreen):
                return None
            return True if parameters[0] <= len(self.screen.query_one(Options).items) else False
        return True

    def on_options_selected(self, event):
        self.select_option(event.option_id)

    def action_select_card(self, number):
        if self._can_act():
            options = self.screen.query_one(Options).items
            if 1 <= number <= len(options):
                self.select_option(options[number - 1]["id"])

    def select_option(self, identifier):
        if not self._can_act():
            return
        if identifier == "ui:connect":
            self.action_configure()
        elif identifier.startswith("locked:"):
            self.notify("Not yet: complete the study details first (card 1).", severity="warning")
        elif identifier == "human:study":
            self.action_study()
        elif identifier.startswith("human:confirm:"):
            self.action_confirm()
        elif identifier == "human:unlock":
            self.action_unlock()
        elif identifier == "custom":
            self.action_custom()
        else:
            self.run_session_action("choose", identifier)

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
            from mlca.tui.screens.custom import CustomScreen

            event = self.session.workflow.events[self.session.state.current_event]
            self.push_screen(
                CustomScreen(event.custom_scope.description, self.custom_suggestions(event)),
                lambda result: self.route_instruction(result["instruction"]) if result else None,
            )

    def runnable_cards(self):
        items = self.screen.query_one(Options).items if isinstance(self.screen, MainScreen) else []
        return [
            o
            for o in items
            if not o.get("disabled")
            and o["id"] not in {"custom", "ui:connect"}
            and not o["id"].startswith("locked:")
        ]

    def custom_suggestions(self, event):
        """Ready-made prompts: do the next step, the step's cards (AI-proposed when a model is connected), help."""
        items = ["Complete this step for me"]
        for card in self.runnable_cards():
            if card["id"].startswith("human:") or card["id"] == "next":
                continue
            items.append(card["title"])
        for action_id in event.actions:
            title = self.session.workflow.actions[action_id].title
            if title not in items:
                items.append(title)
        items.append("Explain what this step needs from me")
        return items[:6]

    def route_instruction(self, instruction):
        from mlca.tui.screens.custom import intent
        from mlca.ui_text import next_hint

        kind = intent(instruction)
        titles = {self.session.workflow.actions[a].title: a for a in self.session.workflow.actions}
        if kind == "proceed":
            cards = self.runnable_cards()
            if not cards:
                self.notify("Nothing can run yet. " + next_hint(self.decorated_status()), severity="warning")
                return
            self.notify("Doing the next step: " + cards[0]["title"])
            self.select_option(cards[0]["id"])
        elif kind == "explain":
            status = self.decorated_status()
            event = status.get("event_spec") or {}
            pending = [
                g["text"]
                for g in event.get("subgoals", [])
                if not status.get("subgoals", {}).get(event.get("id", "") + "." + g["id"], {}).get("passed")
            ]
            self.notify(
                "This step: "
                + str(event.get("goal", ""))
                + ("\nStill to do: " + "; ".join(pending) if pending else "")
                + "\nNext: "
                + next_hint(status),
                timeout=20,
            )
        elif instruction in titles:
            card = next((o for o in self.runnable_cards() if o["title"] == instruction), None)
            if card:
                self.select_option(card["id"])
            else:
                self.run_session_action("custom", instruction)
        else:
            self.run_session_action("custom", instruction)

    def action_approvals(self):
        if not self._can_act():
            return
        requests = self.session.approvals()
        if not requests:
            self.notify("No approvals waiting")
            return

        def selected(result):
            if result:
                decision = {"approve": "approved", "decline": "declined"}.get(
                    result["decision"], result["decision"]
                )
                request = next((r for r in requests if r["request_id"] == result["id"]), None)
                if request and request["kind"] == "study_fields" and decision == "approved":
                    from .screens.study import StudyScreen

                    self.push_screen(
                        StudyScreen(self.session.state, request.get("proposed", {})),
                        lambda fields: (
                            self.run_session_action(
                                "resolve_approval",
                                result["id"],
                                decision,
                                result["note"],
                                result["phrase"],
                                {**fields["answers"], "primary_data": fields["primary_data"]},
                            )
                            if fields
                            else None
                        ),
                    )
                else:
                    self.run_session_action(
                        "resolve_approval", result["id"], decision, result["note"], result["phrase"]
                    )

        self.push_screen(
            FormScreen(
                "Pending approvals (review each request before deciding)\n"
                + json.dumps(requests, ensure_ascii=False),
                [
                    ("id", "Request ID", requests[0]["request_id"]),
                    ("decision", "approve or decline", ""),
                    ("note", "Author note", ""),
                    ("phrase", "Type UNLOCK TEST for test unlock only", ""),
                ],
            ),
            selected,
        )

    def action_study(self):
        if self._can_act():
            from .screens.study import StudyScreen

            drafter = self.session.draft_brief if "navigator" in self.session.config.roles else None
            self.push_screen(
                StudyScreen(self.session.state, drafter=drafter),
                lambda result: (
                    self.run_session_action("resolve_study", result["answers"], result["primary_data"])
                    if result
                    else None
                ),
            )

    def action_confirm(self) -> Any:
        if self._can_act():
            from mlca.project.init import study_ready

            if self.session.state.current_event == "onboard" and not study_ready(self.session.state)[0]:
                self.notify("Resolve study details before confirming")
                self.action_study()
                return
            event = self.session.workflow.events[self.session.state.current_event]
            goal = next((g for g in event.subgoals if g.check.type == "user_confirm"), None)
            if goal is None:
                self.notify("Nothing to approve in this step")
                return
            self.push_screen(
                FormScreen(
                    self.approval_summary(event, goal),
                    [("note", "Note (optional)", "")],
                    submit="Approve",
                ),
                lambda result: (
                    self.run_session_action("confirm", goal.id, result["note"].strip() or "Approved as shown")
                    if result
                    else None
                ),
            )

    def approval_summary(self, event, goal):
        state = self.session.state
        if event.id != "onboard":
            return "[b]Approve[/b]\n" + goal.text
        brief = state.brief
        lines = ["[b]Approve the study brief[/b]", ""]
        lines.append("Aim: " + str(brief.get("aim") or "—"))
        lines.append("Main table: " + str(state.primary_data or "—"))
        for field, label in [
            ("target", "Predict"),
            ("duration", "Time column"),
            ("event_column", "Event column"),
        ]:
            if state.columns.get(field):
                lines.append(label + ": " + state.columns[field])
        lines.append("One row is: " + str(brief.get("unit") or "—"))
        repeated = {"yes": "yes", "no": "no"}.get(brief.get("repeated_subjects"), "not sure")
        lines.append("Same subject in several rows: " + repeated)
        lines += ["", "To change anything, cancel and open the study details card."]
        return "\n".join(lines)

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
        from mlca.llm.credentials import forget

        forget()
        self.exit()

    def show_reports(self, paths: dict) -> None:
        sections = []
        for name, relative in paths.items():
            path = self.project / relative
            sections.append("## " + name + "\n" + str(path) + "\n")
            if path.suffix == ".md":
                sections.append(path.read_text(encoding="utf-8"))
            else:
                sections.append("```json\n" + path.read_text(encoding="utf-8")[:20000] + "\n```")
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
