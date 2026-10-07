import hashlib
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml
from filelock import FileLock, Timeout
from ulid import ULID

from mlca import __version__
from mlca.config import load as load_config
from mlca.config import redact, redact_value
from mlca.engine import checks, gates
from mlca.engine.options import fallback, parameters
from mlca.engine.scope_guard import layer_one
from mlca.engine.turn import execute
from mlca.errors import BudgetError, IntegrityError, MlcaUserError
from mlca.llm.client import Client
from mlca.llm.usage import read as read_usage
from mlca.llm.usage import summary
from mlca.log.branches import Branches
from mlca.log.replay import replay
from mlca.log.store import Store
from mlca.paths import canonical
from mlca.project.files import materialise
from mlca.runner.run_step import inputs_for
from mlca.templates.loader import load as load_template
from mlca.templates.model import ActionSpec


class Session:
    def __init__(
        self,
        path: Path,
        client: Any = "cli",
        principal: str = "user",
        mode: str = "driver",
        non_blocking: bool = False,
    ) -> None:
        if principal != "user" and not principal.startswith("agent:"):
            raise MlcaUserError("Invalid caller principal")
        if mode not in {"brain", "driver"}:
            raise MlcaUserError("Mode must be brain or driver")
        self.principal, self.mode, self.non_blocking = principal, mode, non_blocking
        self._jobs = {}
        self._action_lock = FileLock(str(path.resolve() / ".mlca/action.lock"), timeout=0)
        self.root = path.resolve()
        settings = self.root / ".mlca/project.yaml"
        if not settings.exists():
            raise MlcaUserError("No MLCA project here; initialize or open a project folder")
        self.settings = yaml.safe_load(settings.read_text(encoding="utf-8"))
        self.store = Store(self.root)
        self.store.verify()
        self.branches = Branches(self.store)
        self.branch_name = self.branches.current()
        self.workflow = load_template(self.root / ".mlca/template")
        if self.workflow.sha256 != self.settings["template_sha256"]:
            raise IntegrityError("Project workflow snapshot changed; start a new study for template changes")
        records = self.store.read()
        created = next((r for r in records if r.type.value == "ProjectCreated"), None)
        if not created or created.payload["template_sha256"] != self.workflow.sha256:
            raise IntegrityError("Project metadata disagrees with immutable log")
        self.config = load_config(self.root)
        self.session_id = str(ULID())
        self.turn_id = None
        self.output_callback = None
        self.timing_context = None
        self.client = Client(self.root, self.config, self.emit)
        self.client.disabled = mode == "brain"
        self.client.principal = principal
        self.client_name = client
        self.closed = False
        self.started = False
        self._state_key = None
        self._state_cache = None

    @classmethod
    def open(cls, path: Any, client: Any = "cli", **kwargs) -> Any:
        return cls(Path(path), client, **kwargs)

    @property
    def state(self) -> Any:
        head = self.store.heads.get(self.branch_name)
        key = (self.branch_name, head)
        if key != self._state_key:
            self._state_cache = replay(self.branches.records(self.branch_name))
            self._state_key = key
        return self._state_cache

    def redact(self, text: Any) -> Any:
        return redact(text, self.config)

    @property
    def row_guard(self):
        from mlca.privacy.rows import guard

        return guard(self.root, self.state)

    def emit(
        self, kind: Any, payload: Any, *, step_id: Any = None, actor: Any = "engine", event_id: Any = None
    ) -> Any:
        self._start_session()
        event_id = event_id if event_id is not None else self.state.current_event
        from mlca.evaluation.timing import enrich

        payload = enrich(
            kind,
            payload,
            self.branches.records(self.branch_name),
            event_id,
            self.timing_context if self.client_name == "tui" else None,
        )
        if kind in {"OptionChosen", "CustomInstructionSubmitted", "ApprovalResolved", "UserConfirmed"}:
            payload["principal"] = self.principal
        payload = redact_value(payload, self.config)
        record = self.store.append(
            kind,
            payload,
            branch=self.branch_name,
            session_id=self.session_id,
            actor=self.principal if actor == "user" else actor,
            event_id=event_id,
            step_id=step_id,
        )
        self._state_key = None
        return record

    def _start_session(self):
        if self.started:
            return
        self.store.append(
            "SessionStarted",
            {
                "client": self.client_name,
                "mlca_version": __version__,
                "config_hash": hashlib.sha256(
                    canonical(self.config.model_dump(mode="json")).encode()
                ).hexdigest(),
            },
            branch=self.branch_name,
            session_id=self.session_id,
            actor=self.principal,
        )
        self.started = True
        self._state_key = None
        from mlca.evaluation.snapshot import capture

        self.store.append(
            "RunSnapshot",
            redact_value(capture(self), self.config),
            branch=self.branch_name,
            session_id=self.session_id,
            actor=self.principal,
        )
        self._state_key = None

    @contextmanager
    def mutation(self) -> Any:
        try:
            with self._action_lock:
                self.branch_name = self.branches.current()
                yield
        except Timeout as exc:
            raise MlcaUserError("Project busy; another client is changing it") from exc

    def subscribe(self, callback: Any) -> Any:
        self.store.callbacks.append(callback)
        return lambda: self.store.callbacks.remove(callback)

    def packages(self) -> Any:
        file = self.root / ".mlca/requirements.lock"
        return file.read_text(encoding="utf-8").splitlines() if file.exists() else []

    def status(self, recheck: Any = False) -> Any:
        if recheck:
            with self.mutation():
                checks.run_all(self.state, self.workflow, self.root, self.emit)
        state = self.state
        return {
            **state.model_dump(mode="json"),
            "branch": self.branch_name,
            "mode": self.mode,
            "active_step": self.active_step(),
            "approvals": self.approvals(),
            "usage": summary(read_usage(self.root)),
            "workflow": self.workflow.spec.model_dump(),
            "event_spec": self.workflow.events[state.current_event].model_dump(),
        }

    def options(self) -> Any:
        with self.mutation():
            state = self.state
            if state.pending_options is None:
                source, request_id = "fallback", None
                if state.event_statuses.get(state.current_event) == "done":
                    options = fallback(state, self.workflow)
                elif self.mode != "brain" and "navigator" in self.config.roles:
                    from mlca.roles.navigator import Navigator

                    try:
                        options, request_id = Navigator(self).propose_options()
                        source = "navigator"
                    except BudgetError:
                        raise
                    except (MlcaUserError, ValueError, TypeError):
                        options = fallback(state, self.workflow)
                else:
                    options = fallback(state, self.workflow)
                self.emit(
                    "OptionsProposed",
                    {"options": options, "source": source, "navigator_request_id": request_id},
                )
            options = list(self.state.pending_options or [])
            state = self.state
            if state.event_statuses.get(state.current_event) == "done":
                # Older cached menus may predate completion or contain only an empty next menu.
                from mlca.engine.options import already_run

                remaining = fallback(state, self.workflow)
                if any(
                    self.workflow.actions[o["action_id"]].role != "supporting"
                    or already_run(o["action_id"], state)
                    for o in options
                ) or (not options and remaining):
                    options = remaining
                    self.emit(
                        "OptionsProposed",
                        {"options": options, "source": "fallback", "navigator_request_id": None},
                    )
            ids = self.workflow.spec.events
            index = ids.index(state.current_event)
            if state.event_statuses.get(state.current_event) == "done" and index + 1 < len(ids):
                target = ids[index + 1]
                if gates.check(target, state, self.workflow, self.root)[0]:
                    options.insert(0, {"id": "next", "title": f"Continue to {target}"})
            if state.current_event == "validate" and not self._ever_unlocked():
                for transition in self.workflow.spec.transitions.get("loops", []):
                    if transition["from"] == "validate":
                        for target in transition["to"]:
                            options.append({"id": "loop:" + target, "title": f"Return to {target}"})
            worker = self.config.roles.get("worker")
            if worker:
                from mlca.llm.pricing import estimate

                cfg = self.config.providers[worker.provider]
                for option in options:
                    action = self.workflow.actions.get(option.get("action_id"))
                    if action:
                        if action.builtin:
                            option["est_cost_usd"] = 0.0
                        elif cfg.request_cost_bound_usd is not None:
                            option["est_cost_usd"] = (
                                cfg.request_cost_bound_usd * self.config.budgets.worker_max_attempts
                            )
                        else:
                            option["est_cost_usd"] = estimate(
                                worker.provider,
                                worker.model,
                                len(action.prompt.encode()),
                                worker.max_output_tokens,
                            )
            custom = {"id": "custom", "title": "Custom instruction (current event scope)"}
            if not options and state.event_statuses.get(state.current_event) != "done":
                custom["note"] = (
                    "All available actions are exhausted; this event needs a custom instruction or a branch."
                )
            options.append(custom)
            return options

    def choose(self, n: Any) -> Any:
        if self.non_blocking:
            return self._launch(lambda: self._choose(n))
        return self._choose(n)

    def _choose(self, n):
        with self.mutation():
            self._ensure_idle()
            return self._choose_available(n)

    def _choose_available(self, n):
        options = self.options()
        choice = next((o for o in options if o["id"] == str(n)), None)
        if choice is None:
            raise MlcaUserError("Choose an available option")
        if choice["id"] == "next":
            return self.next()
        if choice["id"].startswith("loop:"):
            return self.loop(choice["id"].split(":", 1)[1])
        if choice["id"] == "custom":
            raise MlcaUserError("Use custom(text) to provide an instruction")
        with self.mutation():
            self._ensure_idle()
            state = self.state
            action = self.workflow.actions[choice["action_id"]]
            if action.id not in self.workflow.events[state.current_event].actions:
                raise MlcaUserError("Option is stale; request current options")
            values = parameters(action, choice["params"], state)
            self.emit("OptionChosen", {"option_id": choice["id"]}, actor="user")
            return execute(self, action, values)

    def custom(self, text: Any) -> Any:
        if self.non_blocking:
            return self._launch(lambda: self._custom(text))
        return self._custom(text)

    def _custom(self, text):
        with self.mutation():
            self._ensure_idle()
            state = self.state
            event = self.workflow.events[state.current_event]
            self.emit("CustomInstructionSubmitted", {"text": text}, actor="user")
            refs = event.custom_scope.readable_inputs
            if state.split:
                refs = [r for r in refs if r != "registered_data"]
            reads_test = "test" in refs and event.id == "test" and state.test_unlocked
            if not reads_test:
                refs = [r for r in refs if r != "test"]
            action = ActionSpec(
                id="custom",
                event=event.id,
                title="Custom instruction",
                prompt=event.custom_scope.description + "\n" + text,
                inputs=[{"ref": ref} for ref in refs],
                outputs=[],
                reads_test=reads_test,
            )
            allowed = inputs_for(action, state, self.root)
            reason = layer_one(text, event, state, list(allowed.values()))
            if reason:
                self.emit("ScopeDecision", {"layer": 1, "decision": "reject", "reason": reason})
                return {"decision": "reject", "reason": reason}
            self.emit(
                "ScopeDecision", {"layer": 1, "decision": "in_scope", "reason": "Deterministic checks passed"}
            )
            if self.mode == "brain":
                self.emit("ScopeDecision", {"layer": 2, "decision": "skipped", "reason": "brain mode"})
                return execute(self, action, {})
            from mlca.roles.navigator import Navigator

            self.turn_id = str(ULID())
            try:
                decision = Navigator(self).classify_scope(text)
                self.emit("ScopeDecision", {"layer": 2, **decision.model_dump()})
            finally:
                self.turn_id = None
            if decision.decision != "in_scope":
                result = decision.model_dump()
                if decision.target_event in self.workflow.events:
                    result["gate"] = gates.check(decision.target_event, state, self.workflow, self.root)
                return result
            return execute(self, action, {})

    def _ever_unlocked(self) -> Any:
        return any(r.type.value == "TestUnlocked" for r in self.store.read())

    def _enter(self, target: Any, via: Any) -> Any:
        state = self.state
        if target not in self.workflow.events:
            raise MlcaUserError("Unknown workflow event")
        if not gates.check(target, state, self.workflow, self.root, self.emit)[0]:
            return {"entered": False, "event": target}
        invalidate = []
        if via == "loop":
            if self._ever_unlocked():
                raise MlcaUserError(
                    "Validation iteration is closed after test exposure; start a separate protocol"
                )
            ids = self.workflow.spec.events
            invalidate = ids[ids.index(target) :]
        self.emit(
            "EventEntered", {"event_id": target, "via": via, "invalidate_events": invalidate}, event_id=target
        )
        return {"entered": True, "event": target}

    def next(self) -> Any:
        with self.mutation():
            self._ensure_idle()
            checks.run_all(self.state, self.workflow, self.root, self.emit)
            state = self.state
            ids = self.workflow.spec.events
            index = ids.index(state.current_event)
            if state.event_statuses.get(state.current_event) != "done":
                raise MlcaUserError("Current event still has incomplete sub-goals")
            if index + 1 == len(ids):
                return {"complete": True}
            return self._enter(ids[index + 1], "next")

    def loop(self, event: Any) -> Any:
        with self.mutation():
            self._ensure_idle()
            if not any(
                t["from"] == self.state.current_event and event in t["to"]
                for t in self.workflow.spec.transitions.get("loops", [])
            ):
                raise MlcaUserError("Loop is not declared by the workflow template")
            return self._enter(event, "loop")

    def goto(self, event: Any) -> Any:
        with self.mutation():
            self._ensure_idle()
            if not any(
                t["from"] == self.state.current_event and event in t["to"]
                for t in self.workflow.spec.transitions.get("goto", [])
            ):
                raise MlcaUserError("Transition is not declared by the workflow template")
            return self._enter(event, "goto")

    def confirm(self, subgoal: Any, note: Any) -> Any:
        self._require_human()
        with self.mutation():
            event = self.workflow.events[self.state.current_event]
            if (
                subgoal not in {s.id for s in event.subgoals if s.check.type == "user_confirm"}
                or not note.strip()
            ):
                raise MlcaUserError("Confirm a current user-confirmation sub-goal with a note")
            self.emit("UserConfirmed", {"subgoal_id": event.id + "." + subgoal, "note": note}, actor="user")
            checks.run_all(self.state, self.workflow, self.root, self.emit)
            return self.status()

    def unlock_test(self, phrase: Any, reason: Any = "First planned test evaluation") -> Any:
        self._require_human()
        with self.mutation():
            state = self.state
            if (
                state.current_event != "test"
                or not state.split
                or phrase != "UNLOCK TEST"
                or not reason.strip()
            ):
                raise MlcaUserError("In the test event, type UNLOCK TEST and provide the reason")
            self.emit(
                "TestUnlocked",
                {"confirmation": phrase, "split_sha256": state.split["sha256"], "reason": reason},
                actor="user",
            )
            return {
                "test_unlocked": True,
                "project_unlock_count": sum(r.type.value == "TestUnlocked" for r in self.store.read()),
            }

    def branch(self, name: Any, from_id: Any) -> Any:
        with self.mutation():
            self._ensure_idle()
            self._start_session()
            self.branches.create(name, from_id, self.session_id, self.principal)
            self.branch_name = name
            checks.run_all(self.state, self.workflow, self.root, self.emit)
            materialise(self.root, self.state, self.emit)
            return self.branches.list()

    def checkout(self, name: Any) -> Any:
        with self.mutation():
            self._ensure_idle()
            self._start_session()
            self.branches.checkout(name, self.session_id, self.principal)
            self.branch_name = name
            checks.run_all(self.state, self.workflow, self.root, self.emit)
            materialise(self.root, self.state, self.emit)
            return self.status()

    def report(self, kind: Any = "all") -> Any:
        from mlca.report import generate

        with self.mutation():
            return generate(
                self.root, self.state, self.workflow, self.branches.records(self.branch_name), kind
            )

    def package(self, spec: Any, approve: Any = False, reason: Any = "User package request") -> Any:
        if approve:
            self._require_human()
        with self.mutation():
            if approve:
                self._ensure_idle()
            self.emit("PackageRequested", {"package": spec, "reason": reason}, actor="user")
            if approve and self._ever_unlocked():
                raise MlcaUserError("Environment changes are closed after test exposure")
            self.emit("PackageApproved" if approve else "PackageDenied", {"package": spec}, actor="user")
            if approve:
                if self._ever_unlocked():
                    raise MlcaUserError("Environment changes are closed after test exposure")
                from mlca.project.env import install

                record = install(self.root, spec)
                self.emit("EnvironmentRecorded", record)
            return {"approved": approve, "package": spec}

    def _require_human(self):
        if self.principal != "user":
            self.emit(
                "Note",
                {"text": "Human-only decision refused", "principal": self.principal},
                actor=self.principal,
            )
            raise MlcaUserError(
                "This decision is reserved for the human author; request it with mlca_request_approval."
            )

    def active_step(self):
        return next(
            (s for s in reversed(self.state.steps) if s["status"] in {"running", "awaiting_script"}), None
        )

    def _ensure_idle(self):
        active = self.active_step()
        if active:
            raise MlcaUserError(
                f"Step {active['step_id']} is {active['status']}; complete or abandon it first"
            )

    def submit_options(self, options):
        from mlca.engine.options import Option, validate

        if self.mode != "brain":
            raise MlcaUserError("submit_options is available in brain mode only")
        with self.mutation():
            self._ensure_idle()
            result = validate([Option.model_validate(o) for o in options], self.state, self.workflow)
            self.emit("OptionsProposed", {"options": result, "source": self.principal}, actor=self.principal)
            return result

    def step_status(self, step_id):
        if step_id in self._jobs:
            job = self._jobs[step_id]
            if job.get("step_id"):
                return self.step_status(job["step_id"])
            return {k: v for k, v in job.items() if k != "thread"}
        step = next((s for s in self.state.steps if s["step_id"] == step_id), None)
        if step is None:
            raise MlcaUserError("Unknown step id on this branch")
        active_job = next(
            (j for j in self._jobs.values() if j.get("step_id") == step_id and j["thread"].is_alive()), None
        )
        return {**step, "status": "running" if active_job else step["status"], "poll_after_s": 2}

    def submit_script(self, step_id, code):
        if self.mode != "brain":
            raise MlcaUserError("submit_script is available in brain mode only")
        if not isinstance(code, str) or len(code.encode()) > 1024 * 1024:
            raise MlcaUserError("Submit Python source of at most 1 MiB")
        if self.non_blocking:
            return self._launch(lambda: self._submit_script(step_id, code), step_id)
        return self._submit_script(step_id, code)

    def _submit_script(self, step_id, code):
        from mlca.runner.run_step import submit

        with self.mutation():
            active = self.active_step()
            if not active or active["step_id"] != step_id or active["status"] != "awaiting_script":
                raise MlcaUserError("Step is not awaiting a script on this branch")
            try:
                return submit(self, step_id, code)
            except Exception as exc:
                self.emit(
                    "StepFailed",
                    {
                        "step_id": step_id,
                        "attempts": active.get("attempt", 0),
                        "last_error": self.redact(str(exc)),
                    },
                    step_id=step_id,
                )
                from mlca.runner.artefacts import freeze

                freeze(self.root / ".mlca/steps" / step_id)
                raise

    def abandon_step(self, step_id, reason):
        with self.mutation():
            active = self.active_step()
            if not active or active["step_id"] != step_id or not reason.strip():
                raise MlcaUserError("Abandon an active step with a reason")
            self.emit(
                "StepFailed",
                {
                    "step_id": step_id,
                    "attempts": active.get("attempt", 0),
                    "last_error": "abandoned",
                    "reason": reason,
                },
                step_id=step_id,
                actor=self.principal,
            )
            from mlca.runner.artefacts import freeze

            freeze(self.root / ".mlca/steps" / step_id)
            return self.step_status(step_id)

    def request_approval(self, kind, target, reason):
        with self.mutation():
            if kind not in {"confirm", "unlock_test", "package"} or not reason.strip():
                raise MlcaUserError("An approval needs a supported kind and reason")
            state = self.state
            event = self.workflow.events[state.current_event]
            if kind == "confirm" and target not in {
                s.id for s in event.subgoals if s.check.type == "user_confirm"
            }:
                raise MlcaUserError("Request a current user-confirmation sub-goal")
            if kind == "unlock_test" and (event.id != "test" or target != "test"):
                raise MlcaUserError("Request test unlock in the test event")
            record = self.emit(
                "ApprovalRequested",
                {
                    "kind": kind,
                    "target": target,
                    "reason": reason,
                    "requested_by": self.principal,
                    "event": event.id,
                    "generation": state.generations.get(event.id),
                    "split_sha256": state.split["sha256"] if state.split else None,
                },
                actor=self.principal,
            )
            return {
                "request_id": record.id,
                "command": f"mlca --project {__import__('shlex').quote(str(self.root))} approvals approve {record.id}",
            }

    def approvals(self):
        records = self.store.read()
        resolved = {r.payload["request_id"] for r in records if r.type.value == "ApprovalResolved"}
        return [
            {"request_id": r.id, "branch": r.branch, **r.payload}
            for r in records
            if r.type.value == "ApprovalRequested" and r.id not in resolved
        ]

    def resolve_approval(self, request_id, decision, note="", phrase=""):
        self._require_human()
        with self.mutation():
            request = next((r for r in self.approvals() if r["request_id"] == request_id), None)
            if not request or decision not in {"approved", "declined"}:
                raise MlcaUserError("Unknown open approval or decision")
            if decision == "approved":
                state = self.state
                if (
                    request["branch"] != self.branch_name
                    or request["event"] != state.current_event
                    or request["generation"] != state.generations.get(state.current_event)
                ):
                    raise MlcaUserError(
                        "Approval request is stale; request a new decision in the current event"
                    )
                self._ensure_idle()
                if request["kind"] == "confirm":
                    self.confirm(request["target"], note or request["reason"])
                elif request["kind"] == "unlock_test":
                    if request["split_sha256"] != (state.split or {}).get("sha256"):
                        raise MlcaUserError("Approval split changed")
                    self.unlock_test(phrase, note or request["reason"])
                else:
                    self.package(request["target"], True, note or request["reason"])
            self.emit(
                "ApprovalResolved",
                {"request_id": request_id, "decision": decision, "note": note},
                actor="user",
            )
            return {"request_id": request_id, "decision": decision}

    def _launch(self, function, step_id=None):
        if any(j["thread"].is_alive() for j in self._jobs.values()):
            raise MlcaUserError("Project busy; a step is running")
        ready = threading.Event()
        job_id = str(ULID())
        job = {"step_id": step_id, "status": "running" if step_id else "starting", "poll_after_s": 2}

        def changed(record):
            if record.type.value == "StepStarted" or (
                record.type.value == "ScriptWritten" and record.step_id == step_id
            ):
                job.update(step_id=record.step_id, status="running")
                ready.set()

        def run():
            self.store.callbacks.append(changed)
            try:
                with self.mutation():
                    result = function()
                    job.update(result=result, status=result.get("status", "completed"))
                    if result.get("step_id"):
                        job["step_id"] = result["step_id"]
            except Exception as exc:
                job.update(status="failed", error=self.redact(str(exc)))
            finally:
                self.store.callbacks.remove(changed)
                ready.set()

        thread = threading.Thread(target=run, name="mlca-step", daemon=False)
        job["thread"] = thread
        self._jobs[job_id] = job
        thread.start()
        ready.wait(1)
        if not thread.is_alive():
            if "error" in job:
                raise MlcaUserError(job["error"])
            return job["result"]
        return {"step_id": job.get("step_id") or job_id, "status": job["status"], "poll_after_s": 2}

    def verify_scripts(self) -> Any:
        from mlca.runner.verify import verify

        with self.mutation():
            return verify(self)

    def close(self) -> Any:
        for job in self._jobs.values():
            job["thread"].join()
        if not self.closed:
            if self.started:
                self.emit("SessionEnded", {"client": self.client_name})
            self.closed = True

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *args: Any) -> Any:
        self.close()
