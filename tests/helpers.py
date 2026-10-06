def choose_action(session, action_id, params=None):
    options = session.options()
    option = next((o for o in options if o.get("action_id") == action_id), None)
    assert option is not None, options
    if params:
        session.emit(
            "OptionsProposed",
            {"options": [{**option, "params": {**option["params"], **params}}], "source": "test"},
        )
    result = session.choose(option["id"])
    assert result["status"] == "completed"
    return result


def advance_to(session, target):
    while session.state.current_event != target:
        event = session.state.current_event
        choose_action(session, session.workflow.events[event].default_options[0])
        if event == "onboard":
            session.confirm("brief_confirmed", "Reviewed resolved columns and brief")
        if event == "validate":
            session.confirm("model_selected", "Selected before test exposure")
        if event == "test":
            raise AssertionError("Use explicit test unlock before advancing")
        assert session.state.event_statuses[event] == "done"
        session.next()
