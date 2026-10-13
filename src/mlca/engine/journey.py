"""A bounded, model-free projection of the current branch for all clients."""

from mlca.ui_text import record_message


def project(state, workflow, records):
    events = [
        {
            "id": event,
            "state": "current"
            if event == state.current_event
            else "done"
            if state.event_statuses.get(event) == "done"
            else "locked"
            if (event == "test" and not state.test_unlocked) or state.event_statuses.get(event) == "locked"
            else "ahead",
        }
        for event in workflow.spec.events
    ]
    items, steps = [], {}
    principals = {r.session_id: r.actor for r in records if r.type.value == "SessionStarted"}
    for record in records:
        kind, p = record.type.value, record.payload
        if kind == "StepStarted":
            action = workflow.actions.get(p["action_id"])
            item = {
                "step_id": p["step_id"],
                "title": action.title if action else "Custom instruction",
                "state": "running",
                "actor": principals.get(record.session_id, record.actor),
            }
            steps[p["step_id"]] = item
            items.append(item)
        elif kind in {"StepCompleted", "StepFailed"} and p["step_id"] in steps:
            steps[p["step_id"]]["state"] = "done" if kind == "StepCompleted" else "failed"
        elif kind in {"StudyFieldsResolved", "UserConfirmed", "TestUnlocked", "ApprovalResolved"}:
            items.append({"title": record_message(record), "state": "done", "actor": record.actor})
        elif kind == "ScriptRequested" and record.step_id in steps:
            steps[record.step_id]["state"] = "awaiting_script"
    messages = [line for r in records for line in (record_message(r) or "").splitlines()]
    return {"journey": {"events": events, "actions": items[-12:]}, "messages_data": messages[-10:]}
