import json
import shutil

import pytest

from mlca.api import Session
from mlca.paths import atomic_json, user_data_dir
from mlca.project.env import python
from mlca.runner.process import execute
from tests.helpers import advance_to, choose_action


@pytest.mark.slow
@pytest.mark.skipif(not shutil.which("bwrap"), reason="bubblewrap is not installed")
def test_sandbox_denies_private_paths_and_network(project_factory):
    with Session.open(project_factory()) as session:
        advance_to(session, "split")
        choose_action(session, "freeze_stratified")
        step = session.root / ".mlca/probe"
        (step / "outputs").mkdir(parents=True)
        (step / "scratch").mkdir()
        atomic_json(step / "inputs.json", {})
        paths = [
            next(iter(session.state.data.values()))["original_path"],
            str(session.root / session.state.split["vault"]["path"]),
            str(user_data_dir() / "keys"),
        ]
        source = f"""import json, socket
from pathlib import Path
result = {{}}
for value in {paths!r}:
    try:
        p = Path(value)
        list(p.iterdir()) if p.is_dir() else p.read_bytes()
        result[value] = False
    except (PermissionError, FileNotFoundError):
        result[value] = True
try:
    socket.create_connection(("127.0.0.1", 9), timeout=0.1)
    result["network"] = False
except PermissionError:
    result["network"] = True
Path("outputs/probe.json").write_text(json.dumps(result))
"""
        (step / "script.py").write_text(source)
        result = execute(
            python(session.root / ".mlca/env"),
            step,
            [],
            session.root / ".mlca/env",
            session.root / ".mlca/runtime",
            session.root / ".mlca/style.mplstyle",
            "A",
            30,
        )
        assert result["exit_status"] == 0, result["stderr"]
        assert all(json.loads((step / "outputs/probe.json").read_text()).values())
