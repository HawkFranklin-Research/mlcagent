"""Failure taxonomy assigned at write time; historical uncategorized records stay unknown."""

import re

CATEGORIES = {
    "static_check",
    "sandbox_denied",
    "timeout",
    "missing_output",
    "fit_rule",
    "test_lock",
    "scope_layer1",
    "scope_layer2",
    "gate_blocked",
    "invalid_options",
    "invalid_request",
    "provider_error",
    "budget_stop",
    "privacy_refusal",
    "abandoned",
    "human_decision",
}


def valid(category):
    return category in CATEGORIES or bool(re.fullmatch(r"runtime_error:[A-Za-z_]\w*", category))


def execution_category(result):
    if result.get("timed_out"):
        return "timeout"
    stderr = result.get("stderr", "")
    # The child process reports its exception type; retain no exception message in the category.
    matches = re.findall(
        r"^(?:[A-Za-z_]\w*\.)*([A-Za-z_]\w*(?:Error|Exception))(?::|$)", stderr, re.MULTILINE
    )
    error = matches[-1] if matches else "ProcessError"
    if error == "PermissionError" or stderr.startswith("bwrap:"):
        return "sandbox_denied"
    if error == "FitRuleError":
        return "fit_rule"
    return "runtime_error:" + error


DEFAULTS = {
    "GateBlocked": "gate_blocked",
    "StaticCheckFailed": "static_check",
    "BudgetStopped": "budget_stop",
}


def enrich(kind, payload):
    payload = dict(payload)
    if kind in DEFAULTS:
        payload.setdefault("category", DEFAULTS[kind])
    if kind == "ScopeDecision" and payload.get("decision") == "reject":
        payload.setdefault("category", f"scope_layer{payload['layer']}")
    if kind == "RunFinished" and payload.get("exit_status") != 0:
        payload.setdefault("category", execution_category(payload))
    if "category" in payload and not valid(payload["category"]):
        raise ValueError("Unknown failure category")
    return payload
