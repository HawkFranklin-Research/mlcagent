from typing import Any

from ulid import ULID

from mlca.engine import checks, facts
from mlca.errors import MlcaUserError
from mlca.project.files import materialise
from mlca.roles.navigator import Navigator
from mlca.runner.run_step import run_step


def execute(session: Any, action: Any, params: Any) -> Any:
    session._questions_clear()
    if action.event in {"split", "preprocess", "features", "model"} and session._ever_unlocked():
        raise MlcaUserError(
            "Fitting and split changes are closed after project-wide test exposure", category="test_lock"
        )
    session.rails.run(session, "before_step")
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
    row_guard = session.row_guard if not session.config.privacy.allow_sample_rows else None
    safe_facts = []
    for candidate in observation.get("facts", []):
        if row_guard and row_guard.contains_full_row(candidate.get("value")):
            session.emit(
                "FactRejected",
                {
                    "candidate": {k: candidate.get(k) for k in ("key", "source")},
                    "reason": "Fact value contains a registered data row",
                    "category": "privacy_refusal",
                },
                step_id=observation["step_id"],
            )
        else:
            safe_facts.append(candidate)
    observation = {**observation, "facts": safe_facts}
    candidates = []
    if not session.state.guided_enabled and session.mode != "brain" and "navigator" in session.config.roles:
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
        valid, reason = facts.validate(
            candidate, session.root, session.state, row_guard, session.config.privacy.allow_sample_rows
        )
        if candidate.get("key") not in action.fact_candidates:
            valid, reason = False, "Fact key not declared by action"
        session.emit(
            "FactRecorded" if valid else "FactRejected",
            candidate
            if valid
            else {
                "candidate": candidate,
                "reason": reason,
                "category": "privacy_refusal"
                if "registered data row" in reason
                else "runtime_error:FactValidationError",
            },
            step_id=observation["step_id"],
            actor="engine" if session.mode == "brain" else "navigator",
        )
    if not session.client.disabled and session.mode != "brain" and "inspector" in session.config.roles:
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
    if action.prepares_data:
        from mlca.paths import sha256
        from mlca.project.inventory import read_table

        output = next(o for o in observation["outputs"] if o["name"] == action.prepares_data)
        frame = read_table(session.root / output["path"])
        if frame.empty or not frame.index.is_unique:
            raise MlcaUserError("Prepared analysis table needs nonempty rows and unique row identifiers")
        session.emit(
            "DataPrepared",
            {
                "path": output["path"],
                "sha256": output["sha256"],
                "source_sha256": session.state.data[session.state.primary_data]["sha256"],
                "decision_sha256": sha256(session.root / output["path"]),
            },
        )
    session.rails.run(session, "after_step")
    session.progress("Checking sub-goals")
    checks.run_all(session.state, session.workflow, session.root, session.emit)
    edits = materialise(session.root, session.state, session.emit)
    session.progress("completed")
    result = {
        "step_id": observation["step_id"],
        "status": "completed",
        "observation": observation,
        "view_edits": edits,
    }

    if session.state.guided_enabled:
        from mlca.engine.guided import narrate

        result["summary"] = narrate(session, result)
    return result
