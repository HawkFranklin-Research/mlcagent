from types import SimpleNamespace as NS

import pytest

from mlca.autonomous.windows import DecisionWindow, Halted, principal


class Clock:
    value = 0.0

    def now(self):
        return self.value

    def sleep(self, seconds):
        self.value += seconds


def session():
    events = []
    return NS(
        principal="user:policy/0123456789ab",
        is_policy=True,
        progress_callback=None,
        emit=lambda kind, payload, **kw: events.append((kind, payload, kw)),
        events=events,
    )


def test_window_expiry_and_autonomous_zero():
    clock = Clock()
    s = session()
    result = DecisionWindow(1, clock=clock.now, sleep=clock.sleep).decide(s, "choice", 0, [{"title": "Go"}])
    assert result == (0, False)
    assert s.events[-1][0] == "DecisionWindowExpired"
    assert s.events[-1][1]["wait_s"] == pytest.approx(1)
    before = clock.value
    DecisionWindow(0, clock=clock.now, sleep=clock.sleep).decide(s, "choice", 0, [{}])
    assert clock.value == before


def test_halt_and_override_keep_actor():
    clock = Clock()
    s = session()
    w = DecisionWindow(60, clock=clock.now, sleep=clock.sleep, poll=lambda _: True, override=lambda *args: 1)
    assert w.decide(s, "choice", 0, [{}, {}]) == (1, True)
    assert [e[0] for e in s.events] == ["DecisionWindowOpened", "DecisionWindowHalted", "DecisionOverridden"]
    with principal(s, True):
        assert s.principal == "user" and not s.is_policy
    assert s.is_policy and s.principal.startswith("user:policy/")


def test_tui_halt_pauses_without_changing_choice():
    s = session()
    s._autopilot_pause = True
    with pytest.raises(Halted) as error:
        DecisionWindow(60).decide(s, "choice", 0, [{}])
    assert error.value.category == "human_halt"


@pytest.mark.parametrize("seconds", [-1, float("nan"), float("inf")])
def test_bad_window_refused(seconds):
    from mlca.errors import MlcaUserError

    with pytest.raises(MlcaUserError):
        DecisionWindow(seconds)


def test_custom_override_and_client_attribution():
    s = session()
    s.client = NS(principal=s.principal)
    w = DecisionWindow(60, poll=lambda _: True, override=lambda *args: {"custom": "Inspect missingness"})
    assert w.decide(s, "choice", 0, [{}]) == ({"custom": "Inspect missingness"}, True)
    with principal(s, True):
        assert s.client.principal == "user"
    assert s.client.principal == s.principal


def test_cli_noninteractive_requires_autonomous(monkeypatch):
    import sys

    from mlca.autonomous.windows import cli_window
    from mlca.errors import MlcaUserError

    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    with pytest.raises(MlcaUserError, match="--autonomous"):
        cli_window(60)
    assert cli_window(0).seconds == 0


def test_countdown_names_the_decision():
    clock = Clock()
    s = session()
    ticks = []
    s.progress_callback = ticks.append
    DecisionWindow(0.2, clock=clock.now, sleep=clock.sleep).decide(
        s, "choice", 0, [{"title": "Fit baseline"}]
    )
    assert ticks and ticks[0]["remaining_s"] > 0
    assert "Fit baseline" in ticks[0]["phase"]
