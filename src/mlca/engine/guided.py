"""Engine-owned guided turns; models can recommend only existing legal actions."""

import re

from pydantic import Field

from mlca.engine import checks, questions
from mlca.engine.options import Option, fallback, validate
from mlca.errors import IntegrityError, MlcaUserError
from mlca.llm.structured import decode
from mlca.log.schema import StrictModel
from mlca.roles.base import prompt
from mlca.roles.navigator import Navigator


class Choice(Option):
    what_happens: str = Field(max_length=200)
    recommended: bool = False


class Scene(StrictModel):
    situation: str = Field(min_length=1, max_length=240)
    choices: list[Choice] = Field(min_length=1, max_length=4)
    question: questions.Question | None = None


class Summary(StrictModel):
    text: str = Field(max_length=500)


def validate_effect(session, effect):
    kind = effect.get("kind")
    if kind == "answer_question" and set(effect) == {"kind", "question_id", "index"}:
        q = session.state.questions.get(effect["question_id"])
        if (
            q
            and effect["question_id"] not in session.state.answers
            and isinstance(effect["index"], int)
            and not isinstance(effect["index"], bool)
            and 0 <= effect["index"] < len(q["options"])
        ):
            return
    if kind == "set_brief" and set(effect) == {"kind", "field", "value"}:
        if (
            session.state.current_event == "onboard"
            and effect["field"] in {"aim", "unit", "repeated_subjects"}
            and isinstance(effect["value"], str)
            and 0 < len(effect["value"]) <= 600
        ):
            return
    if kind == "exclude_column" and set(effect) == {"kind", "column"}:
        if (
            session.state.current_event == "data"
            and not session.state.split
            and effect["column"] in session.state.inventory[0]["columns"]
            and effect["column"] not in set(session.state.columns.values())
        ):
            return
    if kind == "set_parameter" and set(effect) == {"kind", "action_id", "params"}:
        kind = "choose_action"
    if kind in {"pause", "retry"} and set(effect) == {"kind"}:
        return
    if kind == "choose_action" and set(effect) == {"kind", "action_id", "params"}:
        action = session.workflow.actions.get(effect["action_id"])
        if action and action.id in session.workflow.events[session.state.current_event].actions:
            validate(
                [
                    Option(
                        id="1",
                        action_id=action.id,
                        params=effect["params"],
                        title="Requested action",
                        why_now="Recorded answer",
                    )
                ],
                session.state,
                session.workflow,
            )
            return
    raise MlcaUserError("Question effect is not an allowed current action", category="invalid_request")


def apply_effect(session, effect):
    validate_effect(session, effect)
    if effect["kind"] == "set_brief":
        session._require_human()
        session.resolve_study({**session.state.brief, effect["field"]: effect["value"]})
    elif effect["kind"] == "answer_question":
        questions.answer(session, effect["question_id"], effect["index"])
    elif effect["kind"] == "pause":
        session.pause_autopilot()
    elif effect["kind"] == "retry":
        session._autopilot_pause = False
    else:
        session.emit(
            "OptionsProposed",
            {
                "source": "answer",
                "options": [
                    {
                        "id": "1",
                        "action_id": effect["action_id"],
                        "params": effect["params"],
                        "title": "Requested action",
                        "why_now": "Your recorded answer",
                        "advances": [],
                        "expected_outputs": [],
                        "est_cost_usd": None,
                    }
                ],
            },
        )


def _model_scene(session, legal):
    nav = Navigator(session)
    messages = [
        {
            "role": "user",
            "content": prompt(
                "navigator_turn.md",
                state={
                    "event": session.state.current_event,
                    "subgoals": session.state.subgoals,
                    "facts": session.state.facts,
                    "task": session.state.task,
                    "brief": session.state.brief,
                    "columns": session.state.columns,
                },
                catalog=legal,
                schema=Scene.model_json_schema(),
            ),
        }
    ]
    for attempt in range(2):
        response = session.client.complete(
            "navigator",
            messages,
            schema=Scene,
            context=nav.context("options"),
            categories=["template_spec", "facts"],
        )
        try:
            scene = Scene.model_validate(decode(response.text))
            if sum(c.recommended for c in scene.choices) != 1:
                raise MlcaUserError("Exactly one recommendation is required")
            allowed = {o["action_id"] for o in legal}
            if any(
                c.action_id not in allowed or len(c.title.split()) > 8 or len(c.what_happens.split()) > 20
                for c in scene.choices
            ):
                raise MlcaUserError("Choices must be short and from the legal catalogue")
            parsed = validate(
                [
                    Option.model_validate(
                        {k: v for k, v in c.model_dump().items() if k not in {"recommended", "what_happens"}}
                    )
                    for c in scene.choices
                ],
                session.state,
                session.workflow,
            )
            if scene.question:
                for option in scene.question.options:
                    validate_effect(session, option.effect)
                if any(o.effect["kind"] in {"exclude_column", "set_brief"} for o in scene.question.options):
                    scene.question.explicit = True
                    scene.question.human_only = True
            return scene, parsed, response.request_id
        except (ValueError, TypeError, MlcaUserError) as exc:
            if attempt:
                raise
            messages.extend(
                [
                    {"role": "assistant", "content": response.text},
                    {"role": "user", "content": "Repair this bounded JSON: " + str(exc)[:600]},
                ]
            )


def present(session):
    state = session.state
    if not state.guided_enabled:
        session.emit("GuidedFlowEnabled", {})
        state = session.state
    if state.current_event == "data" and not state.split:
        questions.review(session)
        state = session.state
    if questions.pending(session):
        return {
            "situation": "Your answer is needed before the next step.",
            "choices": [],
            "questions": questions.pending(session),
        }
    if state.presented_turn and state.pending_options is not None:
        return {**state.presented_turn, "questions": []}
    legal = (
        list(state.pending_options)
        if state.pending_options is not None
        else fallback(state, session.workflow)
    )
    if state.current_event == "onboard":
        from mlca.project.init import study_ready

        if not study_ready(state)[0]:
            legal = []
    if state.current_event == "features" and state.split and state.inventory:
        main = next((i for i in state.inventory if i["name"] == state.primary_data), state.inventory[0])
        if len(main["columns"]) > state.split["counts"]["train"]:
            legal.sort(key=lambda o: o.get("action_id") != "select_features")
    scene, source, request_id = None, "fallback", None
    # Human decisions and navigation are computed by the engine, never invented by a model.
    if (
        legal
        and state.event_statuses.get(state.current_event) != "done"
        and (
            session.mode != "brain"
            and "navigator" in session.config.roles
            and not getattr(session.client, "disabled", False)
        )
    ):
        try:
            scene, legal, request_id = _model_scene(session, legal)
            source = "navigator"
            if scene.question:
                questions.ask(session, scene.question.model_dump(), asker="navigator", key="turn")
                return {"situation": scene.situation, "choices": [], "questions": questions.pending(session)}
        except IntegrityError:
            raise
        except Exception as exc:
            session.emit(
                "Refusal",
                {
                    "category": getattr(exc, "category", "invalid_options"),
                    "operation": "navigator_options",
                    "reason": "Showing built-in choices after AI failure",
                    "error_type": type(exc).__name__,
                },
            )
    session.emit("OptionsProposed", {"options": legal, "source": source, "navigator_request_id": request_id})
    # Read-only menu adds next and engine-owned human cards.
    choices = session.guided_view()
    recommended = None
    if scene:
        recommended = next(c.action_id for c in scene.choices if c.recommended)
    for choice in choices:
        choice["recommended"] = choice.get("action_id") == recommended if recommended else False
        if scene and choice.get("action_id"):
            selected = next((c for c in scene.choices if c.action_id == choice["action_id"]), None)
            if selected:
                choice["description"] = selected.what_happens
    if not any(c.get("recommended") for c in choices):
        ready = next((c for c in choices if not c.get("disabled") and c["id"] != "custom"), None)
        if ready:
            ready["recommended"] = True
    choices.sort(key=lambda c: not c.get("recommended", False))
    situation = scene.situation if scene else session.workflow.events[state.current_event].goal
    session.emit("TurnPresented", {"situation": situation, "choices": choices})
    return {"situation": situation, "choices": choices, "questions": []}


def narrate(session, result):
    observation = result.get("observation", {})
    measured = observation.get("metrics", [])
    text = "The step completed and its outputs were checked. "
    text += (
        "; ".join(f"{m['name']} on {m['split']}: {m['value']:.4g}" for m in measured[:3]) + "."
        if measured
        else "The next study decision is ready."
    )
    if session.mode != "brain" and "navigator" in session.config.roles and not session.client.disabled:
        from mlca.llm.structured import complete

        try:
            response = complete(
                session.client,
                "navigator",
                [
                    {
                        "role": "user",
                        "content": prompt(
                            "navigator_summary.md",
                            result={
                                "metrics": measured,
                                "outputs": [o["name"] for o in observation.get("outputs", [])],
                            },
                            schema=Summary.model_json_schema(),
                        ),
                    }
                ],
                Summary,
                Navigator(session).context("summary"),
                ["facts"],
            )
            candidate = response.parsed.text
            numbers = re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", candidate)
            known = {str(m["value"]) for m in measured} | {f"{m['value']:.4g}" for m in measured}
            if len(re.findall(r"[.!?](?:\s|$)", candidate)) == 2 and all(n in known for n in numbers):
                text = candidate
        except IntegrityError:
            raise
        except Exception:
            pass
    session.emit("ResultSummary", {"text": text, "step_id": result.get("step_id")})
    return text


def drive(session, max_steps=100):
    if isinstance(max_steps, bool) or not 1 <= max_steps <= 1000:
        raise MlcaUserError("Autopilot step limit must be 1–1000", category="invalid_request")
    session._autopilot_pause = False
    with session.mutation():
        session._ensure_idle()
        if not session.state.compare_models and not session._ever_unlocked():
            ids = session.workflow.spec.events
            if ids.index(session.state.current_event) > ids.index("model"):
                raise MlcaUserError(
                    "Start autopilot before leaving Model to compare both candidates; branch before Model or continue this protocol in step mode",
                    category="gate_blocked",
                )
            session.emit("ComparisonRequested", {})
            checks.run_all(session.state, session.workflow, session.root, session.emit)
    reason, last = "step_limit", None
    for _ in range(max_steps):
        if session._autopilot_pause:
            reason = "paused"
            break
        turn = session.turn()
        if turn["questions"]:
            reason = "question"
            break
        human = next((c for c in turn["choices"] if c["id"].startswith("human:")), None)
        if human:
            reason = "approval"
            break
        if session.state.current_event == "report" and session.state.event_statuses.get("report") == "done":
            reason = "completed"
            break
        choice = next((c for c in turn["choices"] if c.get("recommended") and not c.get("disabled")), None)
        if not choice or choice["id"] == "custom":
            reason = "decision"
            break
        try:
            last = session.choose(choice["id"])
            if last.get("status") == "awaiting_script":
                reason = "awaiting_script"
                break
        except IntegrityError:
            raise
        except Exception as exc:
            reason = "budget" if getattr(exc, "category", "") == "budget_stop" else "failure"
            with session.mutation():
                if reason == "failure" and not session.questions():
                    questions.ask(
                        session,
                        {
                            "header": "Step stopped",
                            "question": "The step failed after its allowed repairs. Retry or pause?",
                            "why": session.redact(str(exc))[:600],
                            "explicit": True,
                            "options": [
                                {
                                    "label": "Pause",
                                    "description": "Keep the failure and review it",
                                    "effect": {"kind": "pause"},
                                },
                                {
                                    "label": "Retry",
                                    "description": "Start a new attempt; keep the failed step",
                                    "effect": {"kind": "retry"},
                                },
                            ],
                        },
                        key="recovery",
                    )
            break
    with session.mutation():
        session.emit("AutopilotStopped", {"reason": reason})
    return {"reason": reason, "last": last, "turn": session.guided_view(), "questions": session.questions()}
