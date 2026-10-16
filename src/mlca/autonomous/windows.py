"""Decision windows shared by CLI and TUI; no permission is granted by a timeout."""

import math
import time
from contextlib import contextmanager

from mlca.errors import MlcaUserError


class Halted(MlcaUserError):
    def __init__(self, message):
        super().__init__(message, category="human_halt")


class DecisionWindow:
    def __init__(self, seconds=60, *, clock=time.monotonic, sleep=time.sleep, poll=None, override=None):
        if not math.isfinite(seconds) or seconds < 0:
            raise MlcaUserError("Halt window must be finite and nonnegative", category="invalid_request")
        self.seconds, self.clock, self.sleep = seconds, clock, sleep
        self.poll, self.override = poll, override

    def decide(self, session, kind, proposed, options):
        from ulid import ULID

        wid = str(ULID())
        start = self.clock()
        session.emit(
            "DecisionWindowOpened",
            {
                "window_id": wid,
                "kind": kind,
                "seconds": self.seconds,
                "proposed": proposed,
                "options": options,
                "principal": session.principal,
            },
        )
        while self.clock() - start < self.seconds:
            remaining = self.seconds - (self.clock() - start)
            callback = session.progress_callback or getattr(self, "display", None)
            if callback:
                callback(
                    {
                        "phase": f"{options[proposed].get('title') or options[proposed].get('label') or kind} · decision in {remaining:.0f}s · h: Halt",
                        "remaining_s": remaining,
                        "phase_code": "decision_window",
                    }
                )
            halted = getattr(session, "_autopilot_pause", False) or (
                self.poll and self.poll(min(0.1, remaining))
            )
            if halted:
                with principal(session, True):
                    session.emit(
                        "DecisionWindowHalted",
                        {"window_id": wid, "wait_s": self.clock() - start},
                        actor="user",
                    )
                session.halted_decision = {"window_id": wid, "started": self.clock()}
                if self.override is None:
                    raise Halted("Decision halted; choose a card or answer the question")
                choice = self.override(kind, proposed, options)
                custom = (
                    isinstance(choice, dict)
                    and kind == "choice"
                    and set(choice) == {"custom"}
                    and isinstance(choice["custom"], str)
                    and bool(choice["custom"].strip())
                )
                if not custom and (
                    isinstance(choice, bool) or not isinstance(choice, int) or not 0 <= choice < len(options)
                ):
                    raise MlcaUserError("Choose a listed decision", category="invalid_request")
                with principal(session, True):
                    session.emit(
                        "DecisionOverridden",
                        {"window_id": wid, "selection": choice, "wait_s": self.clock() - start},
                        actor="user",
                    )
                session.halted_decision = None
                return choice, True
            self.sleep(min(0.1, remaining))
        session.emit("DecisionWindowExpired", {"window_id": wid, "wait_s": self.clock() - start})
        return proposed, False


@contextmanager
def principal(session, human):
    old, policy = session.principal, session.is_policy
    client = getattr(session, "client", None)
    client_principal = getattr(client, "principal", old)
    if human:
        session.principal, session.is_policy = "user", False
        if client is not None:
            client.principal = "user"
    try:
        yield
    finally:
        session.principal, session.is_policy = old, policy
        if client is not None:
            client.principal = client_principal


def cli_window(seconds):
    import select
    import sys

    if seconds and not sys.stdin.isatty():
        raise MlcaUserError("Use --autonomous for a noninteractive terminal", category="invalid_request")

    def poll(timeout):
        import os

        if os.name == "nt":
            import msvcrt

            return msvcrt.kbhit() and msvcrt.getwch().lower() in {"h", " "}
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            if not select.select([sys.stdin], [], [], timeout)[0]:
                return False
            return sys.stdin.read(1).lower() in {"h", " "}
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def override(kind, proposed, options):
        print(f"Halted: {kind}")
        for i, item in enumerate(options, 1):
            print(f"{i}. {item.get('title') or item.get('label') or item.get('reason') or 'Use proposal'}")
        # A scoped instruction is still validated by Session.custom.
        while True:
            answer = input("Choose a number, c for custom instruction, or q to stop: ").strip()
            if answer.lower() == "q":
                raise Halted("Stopped by the human during a decision window")
            if answer.lower() == "c" and kind == "choice":
                return {"custom": input("Custom instruction: ")}
            if answer.isdigit() and 1 <= int(answer) <= len(options):
                return int(answer) - 1

    window = DecisionWindow(seconds, poll=poll, override=override)
    window.display = lambda payload: print(
        "\r" + payload["phase"] + "   ", end="", file=sys.stderr, flush=True
    )
    return window
