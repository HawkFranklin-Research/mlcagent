"""Fresh autonomous projects; no researcher manifest is read by this module."""

import hashlib
import json
import shutil
import time
from pathlib import Path

from mlca.api import Session
from mlca.config import Config, load, merge
from mlca.errors import MlcaUserError
from mlca.evaluation.bench import summarize
from mlca.evaluation.metrics import generate
from mlca.paths import atomic_json, canonical
from mlca.project.init import initialise

from .inference import Inference, infer
from .windows import DecisionWindow, principal

METRICS = {
    "binary": "roc_auc",
    "multiclass": "roc_auc_ovr",
    "regression": "rmse",
    "multioutput_regression": "rmse",
    "multilabel": "macro_f1",
    "clustering": "silhouette",
    "representation": "reconstruction_error",
    "survival": "c_index",
}


def drive(session, max_turns=100, *, cooldown_s=600, max_cooldowns=3, sleep=time.sleep):
    window = session.decision_window
    cooldowns = 0
    for _ in range(max_turns):
        result = session.autopilot(max_turns)
        if result["reason"] == "completed":
            return
        if result["reason"] == "failure":
            from mlca.evaluation.bench import provider_stopped

            if provider_stopped(session) and cooldowns < max_cooldowns:
                cooldowns += 1
                session.emit(
                    "Note",
                    {
                        "text": "Provider unavailable; waiting before retrying the step",
                        "cooldown_s": cooldown_s,
                    },
                    actor="user",
                )
                sleep(cooldown_s)
                for question in session.questions():
                    retry = next(
                        (
                            i
                            for i, o in enumerate(question["options"])
                            if o.get("effect", {}).get("kind") == "retry"
                        ),
                        None,
                    )
                    if retry is not None:
                        chosen, human = window.decide(session, "question", retry, question["options"])
                        if not human:
                            session.emit(
                                "QuestionAutoResolved",
                                {
                                    "question_id": question["question_id"],
                                    "answer": chosen,
                                    "reason": "Provider cooldown retry",
                                },
                            )
                        with principal(session, human):
                            session.answer_question(question["question_id"], chosen)
                continue
        if result["reason"] == "question":
            for question in session.questions():
                chosen, human = window.decide(
                    session, "question", question["recommended"], question["options"]
                )
                if not human:
                    session.emit(
                        "QuestionAutoResolved",
                        {
                            "question_id": question["question_id"],
                            "answer": chosen,
                            "reason": "Autonomous policy selected the recorded recommendation",
                        },
                    )
                with principal(session, human):
                    session.answer_question(question["question_id"], chosen)
        elif result["reason"] == "approval":
            for choice in result["turn"]:
                if not choice["id"].startswith("human:"):
                    continue
                allowed = choice["id"].startswith("human:confirm:") or choice["id"] == "human:unlock"
                if not allowed:
                    raise MlcaUserError(
                        "Autonomous policy cannot resolve this human card", category="human_decision"
                    )
                _, human = window.decide(session, "approval", 0, [choice])
                with principal(session, human):
                    if choice["id"] == "human:unlock":
                        session.unlock_test(
                            "UNLOCK TEST", "Preauthorized autonomous policy; validation is frozen"
                        )
                    else:
                        session.confirm(choice["id"].split(":", 2)[2], "Preauthorized autonomous policy")
        else:
            failure = next(
                (r.payload["category"] for r in reversed(session.store.read()) if r.payload.get("category")),
                "agent_failure",
            )
            raise MlcaUserError(
                "Autonomous run stopped: " + result["reason"],
                category="human_halt" if result["reason"] == "paused" else failure,
            )
    raise MlcaUserError("Autonomous turn limit reached", category="budget_stop")


def _input_hashes(files):
    from mlca.paths import sha256
    from mlca.project.discovery import registrations

    return {name: sha256(file) for name, file in registrations(files)}


def resume(session, *, seconds=60):
    """Human-started TUI automation, using a distinct policy identity."""
    if session.principal != "user" or session.mode != "driver" or session.measurement_arm != "worker":
        raise MlcaUserError("Only a human can start driver automation", category="human_decision")
    old, policy, client_actor = session.principal, session.is_policy, session.client.principal
    session.principal = (
        "user:policy/"
        + hashlib.sha256(canonical({"project": str(session.root), "window": seconds}).encode()).hexdigest()[
            :12
        ]
    )
    session.is_policy = True
    session.client.principal = session.principal
    session._autopilot_pause = False
    session.decision_window = DecisionWindow(seconds)
    session.halt_window_s = seconds
    session.emit("AutonomyConfigured", {"halt_window_s": seconds, "principal": session.principal})
    try:
        drive(session)
        return {"reason": "completed"}
    except MlcaUserError as exc:
        if exc.category == "human_halt":
            return {"reason": "paused"}
        raise
    finally:
        session.principal, session.is_policy, session.client.principal = old, policy, client_actor
        session.decision_window = None


def run(path, out, *, brief="", runs=1, config=None, exclude_columns=(), halt_window=0, window=None):
    if isinstance(runs, bool) or runs < 1:
        raise MlcaUserError("Run count must be positive", category="invalid_request")
    DecisionWindow(halt_window)  # Validate before any provider request.
    out = Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise MlcaUserError("Choose a fresh empty run output directory", category="invalid_request")
    from mlca.project.discovery import discover

    input_files = discover([Path(path)])
    input_hashes = _input_hashes(input_files)
    out.mkdir(parents=True, exist_ok=True)
    conf = Config.model_validate(merge(load().model_dump(mode="json"), config or {})).model_dump(mode="json")
    if conf["measurement_arm"] != "worker":
        raise MlcaUserError(
            "Autonomous runs require freshly generated Worker code", category="invalid_request"
        )
    # No provider/model defaults: role identifiers come only from user configuration.
    identifier = hashlib.sha256(
        canonical(
            {
                "brief": brief,
                "config": conf,
                "window_s": halt_window,
                "exclude_columns": list(exclude_columns),
                "runs": runs,
                "input_sha256": input_hashes,
            }
        ).encode()
    ).hexdigest()
    policy = "user:policy/" + identifier[:12]
    manifest = {
        "schema_version": "1",
        "kind": "independent_agent_runs",
        "measurement_arm": "worker",
        "mode": "driver",
        "task": Path(path).stem,
        "task_card_sha256": identifier,
        "runs": [],
        "models_locked": False,
        "policy_principal": policy,
        "autonomous_inference": True,
    }
    atomic_json(out / "bench.json", manifest)
    for index in range(1, runs + 1):
        project = out / f"run-{index:03d}"
        setup = out / f"setup-{index:03d}"
        entry = {"run": index, "project": project.name, "status": "failed"}
        manifest["runs"].append(entry)
        session = None
        setup_windows = []
        try:
            if _input_hashes(input_files) != input_hashes:
                raise MlcaUserError("Input changed between independent runs", category="invalid_request")
            proposal, request_id, digest, setup_session_id = infer(
                input_files, brief, conf, setup, exclude_columns, principal=policy
            )
            from types import SimpleNamespace

            controller = window or DecisionWindow(halt_window)
            setup_session = SimpleNamespace(
                principal=policy,
                is_policy=True,
                progress_callback=None,
                emit=lambda kind, payload, **kw: setup_windows.append((kind, payload, kw)),
            )
            options = [proposal, *[Inference.model_validate(p) for p in proposal.alternatives]]
            selected, inference_human = controller.decide(
                setup_session,
                "inference",
                0,
                [{"title": p.problem_type, "reason": p.reason} for p in options],
            )
            proposal = options[selected]
            digest = hashlib.sha256(canonical(proposal.model_dump()).encode()).hexdigest()
            answers = {
                "aim": brief or proposal.reason,
                "target": proposal.targets[0] if proposal.targets else "",
                "targets": json.dumps(proposal.targets),
                "unit": proposal.unit,
                "repeated_subjects": proposal.repeated_subjects,
                "duration": proposal.duration or "",
                "event_column": proposal.event_column or "",
            }
            initialise(
                project,
                input_files,
                proposal.template,
                answers,
                conf,
                principal=policy,
                primary_data=proposal.primary_data,
                exclude_columns=exclude_columns,
            )
            # Inference requests are retained with their original identity and egress evidence.
            for name in ("usage.jsonl", "egress.jsonl"):
                file = setup / ".mlca" / name
                if file.exists():
                    shutil.copy2(file, project / ".mlca" / name)
            if (setup / ".mlca/requests").exists():
                shutil.copytree(setup / ".mlca/requests", project / ".mlca/requests", dirs_exist_ok=True)
            if (setup / ".mlca/llm").exists():
                shutil.copytree(setup / ".mlca/llm", project / ".mlca/llm", dirs_exist_ok=True)
            session = Session.open(project, principal=policy, policy=True)
            session.halt_window_s = halt_window
            session.decision_window = controller
            session.emit(
                "AutonomyConfigured",
                {
                    "halt_window_s": halt_window,
                    "principal": policy,
                    "starting_brief": brief,
                    "starting_brief_word_count": len(brief.split()),
                },
            )
            for kind, payload, kw in setup_windows:
                with principal(session, kw.get("actor") == "user"):
                    session.emit(kind, payload, **kw)
            session.emit(
                "InferenceRecorded",
                {
                    "proposal": proposal.model_dump(),
                    "reason": proposal.reason,
                    "request_id": request_id,
                    "sha256": digest,
                    "setup_session_id": setup_session_id,
                    "selected_by": "user" if inference_human else policy,
                },
                actor="navigator",
            )
            if proposal.uncertain:
                session.emit(
                    "QuestionAutoResolved",
                    {
                        "question_id": "inference",
                        "answer": 0,
                        "reason": proposal.question or "Inferred study recommendation used",
                    },
                )
            session.emit(
                "TaskConfigured",
                {
                    "task": {
                        "type": proposal.problem_type,
                        "primary_metric": proposal.primary_metric or METRICS[proposal.problem_type],
                        "metric_reason": proposal.metric_reason,
                        "targets": proposal.targets,
                        "time_columns": proposal.time_columns,
                        "autonomous": True,
                    },
                    "excluded_columns": sorted(
                        set(proposal.identifier_suspects + proposal.leakage_suspects) - set(proposal.targets)
                    ),
                    "group_column": proposal.group_column,
                },
            )
            drive(session)
            entry["status"] = "completed"
        except Exception as exc:
            entry.update(
                error_type=type(exc).__name__,
                category=(getattr(exc, "category", None) or "runtime_error:" + type(exc).__name__),
                message=session.redact(str(exc)) if session else "Setup failed: " + type(exc).__name__,
            )
            if session:
                session.emit("Refusal", {"category": entry["category"], "operation": "autonomous_run"})
        finally:
            from mlca.llm.usage import read, summary

            entry["setup_usage"] = summary(read(setup)) if setup.exists() else None
            if setup.exists():
                atomic_json(
                    setup / "decision-windows.json",
                    [
                        {"type": kind, "payload": payload, "actor": kw.get("actor", policy)}
                        for kind, payload, kw in setup_windows
                    ],
                )
                if setup_windows and session is None:
                    from types import SimpleNamespace

                    from mlca.evaluation.autonomy import build as autonomy

                    rows = [
                        SimpleNamespace(
                            type=SimpleNamespace(value="AutonomyConfigured"),
                            payload={"halt_window_s": halt_window},
                            event_id="onboard",
                        )
                    ]
                    rows += [
                        SimpleNamespace(type=SimpleNamespace(value=kind), payload=payload, event_id="onboard")
                        for kind, payload, _ in setup_windows
                    ]
                    entry["setup_autonomy"] = autonomy(rows, read(setup))
                    entry["setup_autonomy"]["rails"] = {"version": None, "sha256": None}
            if session:
                try:
                    session.close()
                    generate(session)
                except Exception as exc:
                    entry.update(
                        status="failed",
                        error_type=type(exc).__name__,
                        category="runtime_error:" + type(exc).__name__,
                        message="Metrics finalization failed; project evidence retained",
                    )
            atomic_json(out / "bench.json", manifest)
    summarize(out)
    return manifest
