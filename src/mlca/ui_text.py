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
    "events": "Workflow events",
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
    messages = {
        "BriefRecorded": lambda: "✓ Brief recorded",
        "StudyFieldsResolved": lambda: "✓ Study details chosen by you",
        "UserConfirmed": lambda: "✓ Your confirmation recorded: " + p["subgoal_id"],
        "EventEntered": lambda: "→ Continue to " + p["event_id"],
        "StepCompleted": lambda: "✓ Step completed; outputs recorded",
        "StepFailed": lambda: "⚠ Step failed: " + p["last_error"][:180],
        "StaticCheckFailed": lambda: "⚠ Script checks refused this attempt",
        "GateBlocked": lambda: "⚠ Complete the current requirements before moving on",
        "TestUnlocked": lambda: "✓ Planned test evaluation approved by you",
        "ApprovalRequested": lambda: "⚠ Your approval is required: " + p["kind"],
        "ApprovalResolved": lambda: "✓ Approval " + p["decision"],
        "ModelChanged": lambda: "✓ " + p["role"] + " model changed to " + p["to"]["model"],
        "ProviderFailed": lambda: "⚠ Model request failed; see Models for connection details",
        "BudgetStopped": lambda: "⚠ Budget reached; review Models before continuing",
        "Refusal": lambda: "⚠ Action refused: " + p.get("reason", p["category"]).replace("_", " "),
    }
    return messages[kind]() if kind in messages else None
