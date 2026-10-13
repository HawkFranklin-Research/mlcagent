"""Shared labels for command-line and terminal clients."""

TEXT = {
    "study": "Study details",
    "approvals": "Approvals",
    "title": "MLCA — Guided machine learning workflows",
    "tagline": "Machine Learning Copilot Agent",
    "subtitle": "guided, event-based ML workflows",
    "project": "Project folder",
    "data": "Data file or folder",
    "template": "Workflow template",
    "brief": "Study aim",
    "target": "Target or duration column",
    "unit": "Unit of analysis",
    "event_column": "Survival event column",
    "init": "Initialize project",
    "open": "Open project",
    "configure": "Configure models",
    "navigator_model": "Navigator model",
    "worker_model": "Worker model",
    "provider": "Provider kind",
    "key_env": "API key environment variable name",
    "base_url": "Provider base URL (optional)",
    "save_config": "Save configuration",
    "first_run": "Choose a project or configure models to begin.",
    "confirm": "Confirm sub-goal",
    "custom": "Custom instruction",
    "next": "Next event",
    "loop": "Return to an earlier validation event",
    "branches": "Branches",
    "report": "Generate reports",
    "usage": "Usage",
    "quit": "Quit",
    "options": "Options",
    "refresh": "Refresh",
    "unlock": "Unlock test",
    "unlock_phrase": "Type UNLOCK TEST",
    "unlock_reason": "Reason for test use",
    "subgoal": "Sub-goal identifier",
    "note": "Author note",
    "branch_name": "Branch name",
    "from_id": "Starting record or completed step ID",
    "checkout": "Checkout branch",
    "create_branch": "Create branch",
    "submit": "Submit",
    "cancel": "Cancel",
    "reports": "Reports",
    "view_figure": "Open recorded figure",
    "figure_path": "Recorded figure path",
    "facts": "Recorded facts",
    "events": "Workflow",
    "log": "Execution log",
    "ready": "Ready",
    "working": "Working…",
    "saved": "Configuration saved",
    "opened": "Project opened",
    "created": "Project created",
    "choose": "Choose an option",
    "action": "Action",
    "failed": "Action failed",
    "no_project": "Open or initialize a project first.",
    "config_help": "Models are required only for Navigator/Worker calls; keys stay in environment variables.",
    "budget_bound": "Maximum USD per model request",
    "duration": "Duration",
    "reason": "Reason",
    "allow_b": "Allow weaker level B for trusted code only",
    "approved": "Approve package installation",
    "package": "Package specification",
    "usage_hint": "Unknown costs remain unknown. Request bounds enforce conservative budgets.",
}


def text(key: str) -> str:
    return TEXT[key]


def record_message(record):
    """One presentation map; raw protocol records remain separately accessible."""
    p, kind = record.payload, record.type.value
    if kind == "InventoryRecorded":
        return "\n".join(
            f"✓ Registered table {f['name']} ({f['rows']:,} rows, {len(f['columns'])} columns)"
            for f in p["files"]
        )
    if kind == "ScopeDecision":
        return scope_message(p)
    if kind == "Refusal" and p.get("category") == "gate_blocked":
        return "⚠ Can't continue yet: finish this step's requirements first"
    messages = {
        "BriefRecorded": lambda: "✓ Brief recorded",
        "StudyFieldsResolved": lambda: "✓ Study details chosen by you",
        "UserConfirmed": lambda: "✓ You confirmed: " + p["subgoal_id"].split(".")[-1].replace("_", " "),
        "EventEntered": lambda: (
            "↻ Setup re-checked after your study details"
            if p.get("via") == "study_fields_updated"
            else ("→ Started " if p.get("via") == "start" else "→ Moved to ")
            + EVENT_TITLES.get(p["event_id"], p["event_id"])
        ),
        "StepCompleted": lambda: "✓ Step completed; outputs recorded",
        "StepFailed": lambda: "⚠ Step failed: " + p.get("category", "runtime failure").replace("_", " "),
        "StaticCheckFailed": lambda: "⚠ Script checks refused this attempt",
        "GateBlocked": lambda: "⚠ Complete the current requirements before moving on",
        "TestUnlocked": lambda: "✓ Planned test evaluation approved by you",
        "ApprovalRequested": lambda: "⚠ Your approval is required: " + p["kind"],
        "ApprovalResolved": lambda: (
            ("✓ You approved: " if p["decision"] == "approved" else "✗ You declined: ")
            + str(p.get("kind", "request")).replace("_", " ")
        ),
        "ModelChanged": lambda: "✓ " + p["role"].capitalize() + " model set to " + p["to"]["model"],
        "ProviderFailed": lambda: "⚠ Model request failed; see Models for connection details",
        "BudgetStopped": lambda: "⚠ Budget reached; review Models before continuing",
        "Refusal": lambda: "⚠ Action refused: " + p.get("reason", p["category"]).replace("_", " "),
    }
    return messages[kind]() if kind in messages else None


EVENT_TITLES = {"onboard": "Project setup"}


def scope_message(p):
    """What happened to a custom instruction, in plain words."""
    decision, layer = p.get("decision"), p.get("layer")
    reason = " ".join(str(p.get("reason", "")).split())
    if len(reason) > 160:
        reason = reason[:157] + "…"
    if decision == "in_scope":
        return "✓ Your instruction fits this step; running it" if layer == 2 else None
    if decision == "other_event":
        target = p.get("target_event")
        where = EVENT_TITLES.get(target, target) if target else "a later step"
        return f"⚠ Your instruction belongs to {where}, not here: {reason}"
    if decision == "skipped":
        return None
    return "⚠ Instruction not run: " + (reason or "outside this step's scope")


def missing_study_fields(detail):
    """Turn a study-readiness message into the missing field names."""
    detail = detail or ""
    if "row represents" in detail:
        return "what one row represents"
    if "duration" in detail:
        return "the time-to-event column"
    if "event_column" in detail:
        return "the event column"
    if "target" in detail:
        return "the column to predict"
    return ""


def next_hint(status):
    """One sentence: the first thing the user should do now."""
    models = status.get("model_status")
    if models is not None and not models and not status.get("external_client"):
        return "connect an AI model (card 1, or press m). Until then only built-in steps can run."
    event = status["event_spec"]
    title = EVENT_TITLES.get(event["id"], event.get("title", event["id"]))
    for goal in event["subgoals"]:
        result = status["subgoals"].get(event["id"] + "." + goal["id"], {})
        if result.get("passed"):
            continue
        check = goal["check"]["type"]
        if check == "study_fields_resolved":
            missing = missing_study_fields(result.get("detail") or status.get("study_detail", ""))
            return "open Complete the study details and fill in " + (missing or "the missing fields") + "."
        if check == "user_confirm":
            return "review and confirm: " + goal["text"].lower() + "."
        if check == "test_unlocked":
            return "approve the planned test evaluation (type UNLOCK TEST)."
        return goal["text"][0].lower() + goal["text"][1:] + " (choose the matching card)."
    events = status["workflow"]["events"]
    index = events.index(event["id"])
    if index + 1 < len(events):
        return f"{title} is complete. Choose Continue to {events[index + 1]}."
    return "all steps are complete. Open Reports (r)."
