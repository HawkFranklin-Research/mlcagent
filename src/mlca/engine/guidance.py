"""Presentation guidance computed by the engine, never accepted from model output."""

from mlca.project.init import study_ready


def cards(session, options):
    state, workflow = session.state, session.workflow
    event = workflow.events[state.current_event]
    record = next(
        (r for r in reversed(session.branches.records()) if r.type.value == "OptionsProposed"), None
    )
    origin = "agent" if record and record.payload["source"] == "navigator" else "template"
    result = []
    for option in options:
        if option["id"] == "custom":
            continue
        action = workflow.actions.get(option.get("action_id"))
        item = dict(option)
        item["source"] = origin if action else "you decide"
        item["description"] = (
            action.prompt.splitlines()[0].removeprefix("Do: ").strip() if action else option["title"]
        )
        item["produces"] = (
            ", ".join(o.name for o in action.outputs) if action else "A recorded navigation decision"
        )
        item["why_now"] = event.goal if origin == "template" else item.get("why_now") or event.goal
        result.append(item)
    human = []
    if event.id == "onboard" and not study_ready(state)[0]:
        human.append(
            {
                "id": "human:study",
                "title": "Choose the target column"
                if not state.columns.get("target")
                else "Complete the study details",
                "description": "Select the outcome columns and describe what one row represents in Study details.",
                "produces": "Validated study fields",
                "why_now": "Required before confirming the brief",
            }
        )
    ordinary_done = all(
        state.subgoals.get(event.id + "." + g.id, {}).get("passed")
        for g in event.subgoals
        if g.check.type != "user_confirm"
    )
    if ordinary_done:
        for goal in event.subgoals:
            if goal.check.type == "user_confirm" and not state.subgoals.get(event.id + "." + goal.id, {}).get(
                "passed"
            ):
                human.append(
                    {
                        "id": "human:confirm:" + goal.id,
                        "title": "Confirm the study brief"
                        if event.id == "onboard"
                        else "Confirm " + goal.text,
                        "description": "Review this decision and add your note",
                        "produces": "Your recorded confirmation",
                        "why_now": goal.text,
                    }
                )
    if event.id == "test" and not state.test_unlocked:
        human.insert(
            0,
            {
                "id": "human:unlock",
                "title": "Approve the planned test evaluation",
                "description": "Review the test lock and type UNLOCK TEST",
                "produces": "Your test-use authorization",
                "why_now": "Held-out data require explicit human approval",
            },
        )
    for item in human:
        item["source"] = "you decide"
        result.append(item)
    custom = next(
        (dict(o) for o in options if o["id"] == "custom"), {"id": "custom", "title": "Custom instruction"}
    )
    custom.update(
        title="Custom instruction",
        source="you decide",
        description="Give an instruction within this event’s scope",
        produces="Outputs from an approved scoped step",
        why_now=event.custom_scope.description,
    )
    result.append(custom)
    return result


def mcp_card(option):
    """Attach the decision owner and the supported human-request route."""
    item = dict(option)
    identifier = item["id"]
    item["actor"] = (
        "human"
        if identifier.startswith("human:")
        else ("engine" if identifier == "next" or identifier.startswith("loop:") else "agent")
    )
    if item["actor"] == "human":
        how = {"tool": "mlca_request_approval"}
        if identifier == "human:study":
            how.update(kind="study_fields", target="onboard")
        elif identifier == "human:unlock":
            how.update(kind="unlock_test", target="test")
        else:
            how.update(kind="confirm", target=identifier.removeprefix("human:confirm:"))
        item["how"] = how
    return item
