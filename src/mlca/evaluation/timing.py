"""Pending-decision timestamps and an explicit TUI activity estimator."""

import time
from datetime import datetime, timezone
from difflib import SequenceMatcher


class Activity:
    def __init__(self, clock=time.monotonic, cutoff=120):
        self.clock, self.cutoff = clock, cutoff
        self.key, self.last, self.total = None, None, 0.0

    def begin(self, key):
        if key != self.key:
            self.key, self.last, self.total = key, self.clock(), 0.0

    def touch(self):
        now = self.clock()
        if self.last is not None and 0 <= now - self.last <= self.cutoff:
            self.total += now - self.last
        self.last = now

    def value(self):
        self.touch()
        return {"active_s": self.total, "active_source": "derived", "idle_cutoff_s": self.cutoff}


def elapsed(ts, now=None):
    return max(0.0, ((now or datetime.now(timezone.utc)) - ts).total_seconds())


def enrich(kind, payload, records, event, activity=None):
    payload = dict(payload)
    if kind in {"OptionChosen", "CustomInstructionSubmitted"}:
        proposal = None
        for r in reversed(records):
            if r.event_id != event:
                continue
            if r.type.value in {"OptionChosen", "CustomInstructionSubmitted", "EventEntered"}:
                break
            if r.type.value == "OptionsProposed":
                proposal = r
                break
        payload["decision_wait_s"] = elapsed(proposal.ts) if proposal else None
        payload["timing_source"] = "derived" if proposal else "unavailable"
        payload["options_record_id"] = proposal.id if proposal else None
        if kind == "CustomInstructionSubmitted":
            payload.update(chars=len(payload["text"]), words=len(payload["text"].split()))
    elif kind == "ApprovalResolved":
        request = next((r for r in records if r.id == payload["request_id"]), None)
        payload["wait_s"] = elapsed(request.ts) if request else None
        payload["timing_source"] = "derived" if request else "unavailable"
    elif kind == "UserConfirmed":
        # Reconstruct the first instant this confirmation was the sole outstanding check.
        checks, since = {}, None
        for r in records:
            if r.event_id != event:
                continue
            if r.type.value == "EventEntered":
                checks, since = {}, None
            elif r.type.value == "SubgoalChecked":
                checks[r.payload["subgoal_id"]] = r.payload["passed"]
                missing = [k for k, passed in checks.items() if not passed]
                if missing == [payload["subgoal_id"]] and len(checks) > 1:
                    since = since or r.ts
                else:
                    since = None
        payload["wait_s"] = elapsed(since) if since else None
        payload["timing_source"] = "derived" if since else "unavailable"
    else:
        return payload
    payload["active_s"] = None
    payload["active_source"] = "unavailable"
    if activity is not None:
        payload.update(activity())
    return payload


def lines_changed(old, new):
    return sum(
        max(i2 - i1, j2 - j1)
        for tag, i1, i2, j1, j2 in SequenceMatcher(None, old.splitlines(), new.splitlines()).get_opcodes()
        if tag != "equal"
    )
