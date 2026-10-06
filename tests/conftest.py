import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from mlca.api import Session
from mlca.project.init import initialise

FIXTURES = Path(__file__).parent / "fixtures"


def pytest_configure(config):
    # Keep real environments on the cache filesystem, outside the source tree; /tmp may have quotas.
    if config.option.basetemp is None:
        base = (
            Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "mlca-tests" / str(os.getpid())
        )
        base.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(base)


def remove_project(folder):
    if not folder.exists():
        return
    for directory in [folder, *(p for p in folder.rglob("*") if p.is_dir() and not p.is_symlink())]:
        directory.chmod(0o700)

    def retry(function, path, error):
        Path(path).chmod(0o700)
        function(path)

    shutil.rmtree(folder, onerror=retry)


@pytest.fixture(autouse=True)
def isolated_user(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "userdata"))
    monkeypatch.setenv("UV_OFFLINE", "1")
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch))
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))


@pytest.fixture(params=["A", "B"] if os.name == "posix" and os.sys.platform == "linux" else ["B"])
def sandbox_level(request, monkeypatch):
    import shutil

    if request.param == "A" and not shutil.which("bwrap"):
        pytest.skip("bubblewrap is not installed")
    monkeypatch.setattr("mlca.runner.run_step.detect", lambda *_: request.param)
    monkeypatch.setattr("mlca.runner.verify.detect", lambda *_: request.param)
    return request.param


@pytest.fixture
def project_factory(tmp_path):
    counter = 0

    def create(*, group=False, brief=None, template="tabular_classification", responses=None):
        nonlocal counter
        counter += 1
        folder = tmp_path / f"case-{counter}"
        folder.mkdir()
        rng = np.random.default_rng(0)
        values = rng.normal(size=(400, 4))
        frame = pd.DataFrame(values, columns=["x1", "x2", "x3", "x4"])
        frame["y"] = (values[:, 0] + 0.5 * values[:, 1] + rng.normal(size=400) > 0).astype(int)
        if group:
            frame["group"] = np.arange(400) // 4
        if template == "survival":
            frame["duration"] = rng.exponential(size=400) + 0.1
            frame["observed"] = rng.binomial(1, 0.8, size=400)
        data = folder / "synthetic.csv"
        frame.to_csv(data, index=False)
        script = folder / "fake.yaml"
        fixture = yaml.safe_load((FIXTURES / "synthetic_fake_llm.yaml").read_text())
        original = next(r for r in fixture["responses"] if r["match"].get("action_id") == "train_logistic")
        fixture["responses"].append(
            {
                "match": {"role": "worker", "action_id": "train_alternative"},
                "text": original["text"].replace("model.pkl", "alternative_model.pkl"),
            }
        )
        if responses:
            fixture["responses"] = responses + fixture["responses"]
        script.write_text(yaml.safe_dump(fixture))
        config = {
            "providers": {"offline": {"kind": "fake", "script": str(script), "request_cost_bound_usd": 0}},
            "roles": {"worker": {"provider": "offline", "model": "scripted"}},
            "sandbox": {"allow_level_b": True},
        }
        answers = brief or yaml.safe_load((FIXTURES / "synthetic_brief.yaml").read_text())
        if template == "survival" and brief is None:
            answers = {**answers, "target": "duration", "duration": "duration", "event_column": "observed"}
        return initialise(folder / "project", [data], template, answers, config)

    yield create
    for folder in tmp_path.glob("case-*"):
        remove_project(folder)


@pytest.fixture
def opened_project(project_factory):
    with Session.open(project_factory()) as session:
        yield session
