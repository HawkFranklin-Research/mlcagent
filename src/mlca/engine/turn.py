from typing import Any

from ulid import ULID

from mlca.engine import checks, facts
from mlca.errors import MlcaUserError
from mlca.project.files import materialise
from mlca.roles.navigator import Navigator
from mlca.runner.run_step import run_step


def execute(session: Any, action: Any, params: Any) -> Any:
    if action.event in {"split", "preprocess", "features", "model"} and session._ever_unlocked():
        raise MlcaUserError("Fitting and split changes are closed after project-wide test exposure")
    session.turn_id = str(ULID())
    session.emit("TurnStarted", {"turn_id": session.turn_id})
    try:
        observation = run_step(session, action, params)
        if observation.get("status") == "awaiting_script":
            return observation
        return finish(session, action, observation)
    finally:
        session.emit("TurnEnded", {"turn_id": session.turn_id})
        session.turn_id = None


def finish(session, action, observation):
    candidates = []
    if session.mode != "brain" and "navigator" in session.config.roles:
        try:
            candidates = Navigator(session).extract_facts(observation, action, observation["step_id"])
        except MlcaUserError as exc:
            session.emit("Note", {"text": "Fact extraction unavailable: " + str(exc)})
    # Runtime candidates retain exact source linkage; still subject to evidence validation.
    for candidate in observation.get("facts", []):
        output = next((o for o in observation["outputs"] if o["name"] == candidate.get("source")), None)
        if output:
            candidates.append(
                {
                    **candidate,
                    "source": output["path"],
                    "sha256": output["sha256"],
                    "step_id": observation["step_id"],
                }
            )
        else:
            candidates.append({**candidate, "step_id": observation["step_id"]})
    for candidate in candidates:
        valid, reason = facts.validate(candidate, session.root, session.state)
        if candidate.get("key") not in action.fact_candidates:
            valid, reason = False, "Fact key not declared by action"
        session.emit(
            "FactRecorded" if valid else "FactRejected",
            candidate if valid else {"candidate": candidate, "reason": reason},
            step_id=observation["step_id"],
            actor="engine" if session.mode == "brain" else "navigator",
        )
    if session.mode != "brain" and "inspector" in session.config.roles:
        from mlca.roles.inspector import Inspector

        for figure in observation["figures"]:
            if figure["name"].endswith(".png"):
                try:
                    note = Inspector(session).describe_figure(
                        session.root / figure["path"], figure.get("caption", ""), observation["step_id"]
                    )
                    session.emit(
                        "ObservationRecorded",
                        {"step_id": observation["step_id"], "note": note},
                        actor="inspector",
                    )
                except MlcaUserError as exc:
                    session.emit("Note", {"text": "Figure inspection unavailable: " + str(exc)})
    checks.run_all(session.state, session.workflow, session.root, session.emit)
    edits = materialise(session.root, session.state, session.emit)
    return {
        "step_id": observation["step_id"],
        "status": "completed",
        "observation": observation,
        "view_edits": edits,
    }
