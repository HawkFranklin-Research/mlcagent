from mlca.tui.screens.custom import intent
from mlca.ui_text import record_message


def rec(kind, payload):
    from types import SimpleNamespace as NS

    return NS(type=NS(value=kind), payload=payload)


def test_do_it_for_me_requests_run_the_next_card():
    for text in [
        "Just do what you can complete the setup",
        "complete the setup",
        "continue",
        "Proceed please",
    ]:
        assert intent(text) == "proceed", text
    assert intent("Explain what this step needs from me") == "explain"
    assert intent("complete the missing-value analysis for age") is None
    assert intent("plot the class balance") is None


def test_refusals_show_the_reason_not_the_exception_type():
    refused = rec(
        "Refusal", {"category": "runtime_error", "operation": "session", "reason": "Pick a column first"}
    )
    assert record_message(refused) == "⚠ Not done: Pick a column first"
    ai = rec("Refusal", {"category": "invalid_options", "operation": "navigator_options"})
    assert record_message(ai) == "⚠ The AI's suggestions were unusable; showing built-in cards"
    assert record_message(rec("UserConfirmed", {"subgoal_id": "onboard.brief_confirmed"})) == (
        "✓ You approved the study brief"
    )
