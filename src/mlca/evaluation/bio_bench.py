"""Ordered custom instructions are research artefacts, including unsuccessful requests."""

import json

from mlca.errors import MlcaUserError


def instructions(card):
    value = card.custom_instructions
    return (
        [{"event": event, "text": text} for event, text in value.items()]
        if isinstance(value, dict)
        else value
    )


def export_instructions(session):
    records = session.store.read()
    items = []
    for index, record in enumerate(records):
        if record.type.value != "CustomInstructionSubmitted":
            continue
        end = next(
            (
                j
                for j in range(index + 1, len(records))
                if records[j].type.value == "CustomInstructionSubmitted"
            ),
            len(records),
        )
        following = records[index + 1 : end]
        scope = [r.payload for r in following if r.type.value == "ScopeDecision"]
        step = next(
            (r for r in following if r.type.value == "StepStarted" and r.payload["action_id"] == "custom"),
            None,
        )
        result = next(
            (
                r
                for r in following
                if r.type.value in {"StepCompleted", "StepFailed"}
                and step
                and r.payload.get("step_id") == step.payload["step_id"]
            ),
            None,
        )
        not_achieved = next(
            (
                r.payload
                for r in following
                if r.type.value == "Note" and r.payload.get("text") == "Custom instruction not achieved"
            ),
            None,
        )
        request_ids = {
            r.payload.get("worker_request_id") for r in following if r.type.value == "ScriptWritten"
        }
        from mlca.llm.usage import read

        model_calls = [u for u in read(session.root) if u["request_id"] in request_ids]
        decision = scope[-1] if scope else {"decision": "not_checked", "reason": "No scope result recorded"}
        items.append(
            {
                "text": record.payload["text"],
                "event": record.event_id,
                "actor": record.actor,
                "step": step.payload["step_id"] if step else None,
                "scope": decision,
                "model": next((u.get("model_reported") or u.get("model") for u in model_calls), None)
                or session.config.roles.get("worker").model
                if session.config.roles.get("worker")
                else None,
                "outcome": result.type.value
                if result
                else "not achieved"
                if not_achieved
                else decision["decision"],
                "not_achieved_reason": not_achieved.get("reason") if not_achieved else None,
                "word_count": len(record.payload["text"].split()),
            }
        )
    path = session.root / "custom_instructions.md"
    lines = [
        "# Custom instructions",
        "",
        "Verbatim submitted instructions; failures and refusals are retained.",
        "",
    ]
    for i, item in enumerate(items, 1):
        lines += [
            f"## Instruction {i}",
            "",
            json.dumps({k: v for k, v in item.items() if k != "text"}, ensure_ascii=False),
            "",
            item["text"],
            "",
        ]
    path.write_text("\n".join(lines))
    return items


def drive(session, card, rng, seed):
    from mlca.engine import checks
    from mlca.evaluation.bench import drive_guided

    pending = list(instructions(card))
    known = set(session.workflow.events)
    if any(item["event"] not in known for item in pending):
        raise MlcaUserError("Custom instruction names an unknown event", category="invalid_request")
    with session.mutation():
        session.emit("ComparisonRequested", {})
        checks.run_all(session.state, session.workflow, session.root, session.emit)
    try:
        for _ in range(card.max_turns):
            event = session.state.current_event
            turn = session.turn()
            if turn.get("questions"):
                for question in session.questions():
                    session.answer_question(question["question_id"], question["recommended"])
                continue
            if (
                pending
                and pending[0]["event"] == event
                and (session.state.event_statuses.get(event) == "done" or pending[0].get("when") == "before")
            ):
                item = pending.pop(0)  # Never silently retry an instruction.
                try:
                    result = session.custom(item["text"])
                    if result.get("status") != "completed":
                        session.emit("Note", {"text": "Custom instruction not achieved", "result": result})
                except MlcaUserError as error:
                    session.emit(
                        "Note",
                        {
                            "text": "Custom instruction not achieved",
                            "reason": str(error),
                            "category": error.category,
                        },
                    )
                continue
            if session.state.event_statuses.get(event) == "done" and pending:
                ids = session.workflow.spec.events
                if ids.index(pending[0]["event"]) < ids.index(event):
                    raise MlcaUserError(
                        "Ordered custom instruction event was passed", category="invalid_request"
                    )
            # One turn at a time so instructions cannot be skipped by autopilot.
            sliced = card.model_copy(update={"max_turns": 1})
            try:
                drive_guided(session, sliced)
                if (
                    session.state.current_event == "report"
                    and session.state.event_statuses.get("report") == "done"
                ):
                    if pending:
                        raise MlcaUserError("Unissued custom instructions remain", category="gate_blocked")
                    return
            except MlcaUserError as error:
                if str(error) not in {
                    "Guided run stopped: step_limit",
                    "Guided task-card turn limit reached",
                }:
                    raise
        raise MlcaUserError("Bio-bench turn limit reached", category="budget_stop")
    finally:
        export_instructions(session)
