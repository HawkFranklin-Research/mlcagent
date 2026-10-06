import sys

import pytest

from mlca.errors import MlcaUserError
from mlca.sandbox.audit_hook import SOURCE
from mlca.sandbox.level import detect, explanation


def test_native_platform_level_b_requires_opt_in(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    with pytest.raises(MlcaUserError):
        detect(False)
    assert detect(True) == "B"
    assert "WSL2" in explanation("win32")
    assert "sandbox.allow_level_b: true" in explanation("darwin")


def test_audit_path_comparison_is_case_normalized():
    assert "os.path.normcase" in SOURCE
    assert "os.path.commonpath" in SOURCE


def test_banner_resource_uses_utf8(monkeypatch):
    from pathlib import Path

    from mlca.tui.banner import logo_lines

    original = Path.read_text

    def read(path, *args, **kwargs):
        if path.name == "logo.txt":
            assert kwargs.get("encoding") == "utf-8"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    assert logo_lines()
