import asyncio

import pytest
from textual.widgets import Button

from mlca.errors import MlcaUserError
from mlca.project.restart import reserve_fresh_study
from mlca.tui.app import MlcaApp
from mlca.tui.screens.existing_project import ExistingProjectScreen


def test_fresh_study_preserves_previous_attempt(tmp_path):
    state = tmp_path / ".mlca"
    state.mkdir()
    evidence = state / "failed.log"
    evidence.write_bytes(b"original failed attempt")
    occupied = tmp_path / "study-001"
    occupied.mkdir()
    (occupied / "keep.txt").write_text("keep")
    fresh = reserve_fresh_study(tmp_path)
    assert fresh == tmp_path / "study-002"
    assert fresh.is_dir()
    assert evidence.read_bytes() == b"original failed attempt"
    assert (occupied / "keep.txt").read_text() == "keep"
    assert reserve_fresh_study(tmp_path).name == "study-003"


def test_missing_parent_refused(tmp_path):
    with pytest.raises(MlcaUserError):
        reserve_fresh_study(tmp_path / "missing")


@pytest.mark.parametrize("choice", ["fresh", "open", "cancel"])
def test_existing_project_choices_preserve_form(tmp_path, monkeypatch, choice):
    private = tmp_path / ".mlca"
    private.mkdir()
    (private / "project.yaml").write_text("old project")
    results, opened = [], []
    form = {"path": str(tmp_path), "aim": "new aim", "data": ["original.csv"]}

    async def check():
        app = MlcaApp(tmp_path / "other")
        monkeypatch.setattr(app, "initialise_project", results.append)
        monkeypatch.setattr(app, "open_project", opened.append)
        async with app.run_test(size=(80, 30)) as pilot:
            app.prepare_initialisation(form)
            await pilot.pause()
            assert isinstance(app.screen, ExistingProjectScreen)
            await pilot.click("#existing-" + choice)
            await pilot.pause()

    asyncio.run(check())
    if choice == "fresh":
        assert results == [{**form, "fresh_parent": str(tmp_path)}]
        assert not opened
    elif choice == "open":
        assert opened == [tmp_path]
        assert not results
    else:
        assert not results and not opened
    assert (private / "project.yaml").read_text() == "old project"
    assert not (tmp_path / "study-001").exists()


def test_partial_initialisation_still_offers_fresh_study(tmp_path):
    (tmp_path / ".mlca").mkdir()

    async def check():
        app = MlcaApp(tmp_path / "other")
        async with app.run_test(size=(80, 30)) as pilot:
            app.push_screen(ExistingProjectScreen(tmp_path))
            await pilot.pause()
            assert app.screen.query_one("#existing-open", Button).disabled
            assert not app.screen.query_one("#existing-fresh", Button).disabled

    asyncio.run(check())


def test_backend_refuses_overwriting_even_partial_attempt(tmp_path):
    from mlca.project.init import initialise

    private = tmp_path / ".mlca"
    private.mkdir()
    evidence = private / "failed.log"
    evidence.write_text("failed attempt")
    with pytest.raises(MlcaUserError, match="Open it to continue"):
        initialise(tmp_path, [], "tabular_classification", {})
    assert evidence.read_text() == "failed attempt"
