import asyncio

from mlca.api import Session
from mlca.evaluation.timing import Activity, lines_changed
from mlca.tui.app import MlcaApp


def test_decision_and_approval_timing(project_factory):
    with Session.open(project_factory(), mode="brain") as session:
        session.options()
        session.custom("Inspect the data schema")
        custom = next(r for r in session.store.read() if r.type.value == "CustomInstructionSubmitted")
        assert custom.payload["decision_wait_s"] >= 0
        assert custom.payload["chars"] == 23
        assert custom.payload["words"] == 4
        assert custom.payload["active_s"] is None
        request = session.request_approval("confirm", "brief_confirmed", "review")
        session.resolve_approval(request["request_id"], "declined")
        approval = session.store.read()[-1]
        assert approval.payload["wait_s"] >= 0


def test_tui_activity_excludes_idle_gaps(tmp_path):
    async def check():
        now = [0.0]
        app = MlcaApp(tmp_path)
        app.activity = Activity(clock=lambda: now[0])
        app.activity.begin("decision")
        async with app.run_test() as pilot:
            now[0] = 10
            await pilot.press("x")
            now[0] = 150
            await pilot.press("x")
            now[0] = 155
            await pilot.press("x")
            assert app.activity.value()["active_s"] == 15
            assert app.activity.cutoff == 120

    asyncio.run(check())


def test_changed_line_count():
    assert lines_changed("a\nb\n", "a\nx\nc\n") == 2
