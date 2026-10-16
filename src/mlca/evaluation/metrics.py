"""Project metrics from verified records and request envelopes; never invokes models."""

import hashlib
from collections import Counter, defaultdict
from datetime import datetime

from mlca.llm.usage import TOKEN_FIELDS, measured_total, read, summary
from mlca.log.replay import replay
from mlca.paths import atomic_json, canonical, sha256


def measured(value, source="derived", **metadata):
    return {"value": value, "source": source if value is not None else "unavailable", **metadata}


def sum_known(values, source="derived"):
    values = list(values)
    return measured(sum(values) if all(v is not None for v in values) else None, source)


def actor_kind(actor):
    return (
        "human"
        if actor == "user"
        else "policy"
        if actor.startswith("user:policy/")
        else "agent"
        if actor.startswith("agent:")
        else "engine"
    )


def navigator_use(records):
    """How often the Navigator's own choices were used, versus built-in cards after a failure.

    A run that completes on built-in cards measures the engine, not the model; report both."""
    proposals = sum(
        r.type.value == "OptionsProposed" and r.payload.get("source") == "navigator" for r in records
    )
    failures = [
        r for r in records if r.type.value == "Refusal" and r.payload.get("operation") == "navigator_options"
    ]
    budget = sum(r.payload.get("category") == "budget_stop" for r in failures)
    fallbacks = len(failures) - budget
    asked = proposals + fallbacks
    return {
        "proposals_used": measured(proposals),
        "fallbacks": measured(fallbacks),
        "budget_stops": measured(budget),
        "fallback_rate": measured(fallbacks / asked if asked else None),
    }


def build(session, branch=None):
    branch = branch or session.branch_name
    records = session.branches.records(branch)
    state = replay(records)
    sessions = {r.session_id for r in records}
    sessions.update(
        r.payload["setup_session_id"]
        for r in records
        if r.type.value == "InferenceRecorded" and r.payload.get("setup_session_id")
    )
    step_ids = {s["step_id"] for s in state.steps}
    requests = [
        r
        for r in read(session.root)
        if r.get("session_id") in sessions
        or r.get("step_id") in step_ids
        or r.get("role") == "external_agent"
        and r.get("import_branch") == branch
    ]
    snapshots = [r for r in records if r.type.value == "RunSnapshot"]
    end = max(
        [r.ts for r in records] + [datetime.fromisoformat(r["ts"].replace("Z", "+00:00")) for r in requests]
    )
    start = min([records[0].ts] + [datetime.fromisoformat(r["ts"].replace("Z", "+00:00")) for r in requests])
    wall = max(0.0, (end - start).total_seconds())
    steps = []
    recovery = Counter()
    for step in state.steps:
        trace = [r for r in records if r.step_id == step["step_id"]]
        attempts = {
            r.payload["attempt"]
            for r in trace
            if r.type.value in {"ScriptWritten", "RunFinished", "StaticCheckFailed", "AttemptFailed"}
            and "attempt" in r.payload
        }
        failed = [
            r
            for r in trace
            if r.type.value in {"StaticCheckFailed", "AttemptFailed", "ProviderFailed"}
            or r.type.value == "RunFinished"
            and r.payload["exit_status"] != 0
        ]
        completion = next((r for r in trace if r.type.value == "StepCompleted"), None)
        recovered = bool(failed and completion)
        human = bool(
            recovered
            and any(
                r.actor == "user" and failed[0].ts < r.ts < completion.ts
                for r in records
                if r.type.value
                in {
                    "OptionChosen",
                    "CustomInstructionSubmitted",
                    "UserConfirmed",
                    "ApprovalResolved",
                    "ScriptWritten",
                    "ScriptEditedByUser",
                    "TestUnlocked",
                    "PackageApproved",
                }
            )
        )
        if failed:
            recovery["with_failures"] += 1
            recovery["after_human" if human else "automatic" if recovered else "unrecovered"] += 1
        steps.append(
            {
                "step_id": step["step_id"],
                "event": step["event_id"],
                "action": step["action_id"],
                "attempts": measured(len(attempts)),
                "first_try_success": measured(bool(completion and len(attempts) == 1 and not failed)),
                "recovered": measured(recovered),
                "status": step["status"],
                "compute_s": sum_known(
                    r.payload.get("duration") for r in trace if r.type.value == "RunFinished"
                ),
            }
        )
    # Count root failures/refusals; terminal StepFailed and API wrappers are not additional attempts.
    primary = {
        "StaticCheckFailed",
        "AttemptFailed",
        "ProviderFailed",
        "GateBlocked",
        "ScopeDecision",
        "FactRejected",
    }
    failed_records = [
        r
        for r in records
        if r.payload.get("category")
        and (r.type.value in primary or r.type.value == "RunFinished" and r.payload["exit_status"] != 0)
    ]
    for r in records:
        if r.payload.get("category") and r.type.value in {"StepFailed", "Refusal", "Note"}:
            if not any(
                f.session_id == r.session_id
                and f.event_id == r.event_id
                and f.payload["category"] == r.payload["category"]
                and (f.step_id == r.step_id if r.step_id else True)
                for f in failed_records
            ):
                failed_records.append(r)
    failure_counts = Counter(r.payload["category"] for r in failed_records)
    interventions = defaultdict(Counter)
    decisions = []
    options = {}
    for r in records:
        kind, p = r.type.value, r.payload
        if kind == "OptionsProposed":
            options = {o["id"]: o for o in p["options"]}
        action = options.get(p.get("option_id"), {})
        counts = interventions[r.actor]
        mapping = {
            "OptionChosen": "option_choices",
            "QuestionAnswered": "question_answers",
            "DataDecision": "data_decisions",
            "CustomInstructionSubmitted": "custom_instructions",
            "UserConfirmed": "confirmations",
            "StudyFieldsResolved": "study_resolutions",
            "ApprovalRequested": "approvals_requested",
            "TestUnlocked": "test_unlocks",
            "PackageApproved": "package_approvals",
            "ScriptEditedByUser": "script_edits",
        }
        if kind in mapping:
            counts[mapping[kind]] += 1
        if kind == "ApprovalRequested" and p["kind"] == "study_fields":
            counts["study_fields_proposed"] += 1
        if kind == "Refusal" and p.get("category") == "human_decision":
            counts["human_decision_refusals"] += 1
        if kind == "StudyFieldsResolved" and (p.get("proposer") or "").startswith("agent:"):
            counts["agent_proposals_applied"] += 1
        if kind == "CustomInstructionSubmitted":
            counts["custom_words"] += p.get("words", len(p["text"].split()))
        if kind == "ApprovalResolved":
            counts["approvals_granted" if p["decision"] == "approved" else "approvals_declined"] += 1
        if kind in {"OptionChosen", "CustomInstructionSubmitted"}:
            decisions.append(
                {
                    "event": r.event_id,
                    "action_id": action.get("action_id", "custom"),
                    "params_hash": hashlib.sha256(
                        canonical(
                            action.get("params", {}) if kind == "OptionChosen" else {"instruction": p["text"]}
                        ).encode()
                    ).hexdigest(),
                    "principal": r.actor,
                }
            )
    interventions = {
        actor: {
            "kind": actor_kind(actor),
            **{k: measured(v) for k, v in counts.items()},
            "script_lines": sum_known(
                r.payload.get("lines_changed")
                for r in records
                if r.actor == actor and r.type.value == "ScriptEditedByUser"
            ),
        }
        for actor, counts in interventions.items()
        if counts
    }
    timing = [
        r
        for r in records
        if r.type.value
        in {
            "OptionChosen",
            "CustomInstructionSubmitted",
            "UserConfirmed",
            "ApprovalResolved",
            "QuestionAnswered",
        }
    ]
    # Requested confirmations already have ApprovalResolved timing; don't double-count their UserConfirmed.
    requested_goals = {
        r.payload.get("event", "") + "." + r.payload["target"]
        for r in records
        if r.type.value == "ApprovalRequested" and r.payload["kind"] == "confirm"
    }
    timing = [
        r
        for r in timing
        if not (r.type.value == "UserConfirmed" and r.payload["subgoal_id"] in requested_goals)
    ]
    human_timing = [r for r in timing if actor_kind(r.actor) == "human"]
    agent_timing = [r for r in timing if actor_kind(r.actor) == "agent"]
    usage_summary = summary(requests)
    models = {}
    for role in sorted({r["role"] for r in requests if r["role"] != "mcp"}):
        calls = [r for r in requests if r["role"] == role]
        models[role] = {
            "calls": measured(len(calls)),
            **{
                key: measured_total(
                    usage_summary["groups"]["role"][role],
                    key,
                    "client-reported"
                    if role == "external_agent"
                    else "derived"
                    if key == "cost_usd" and any(r.get("cost_source") == "pricing_table" for r in calls)
                    else "exact",
                )
                for key in (*TOKEN_FIELDS, "cost_usd")
            },
            "cost_sources": sorted({r["cost_source"] for r in calls}),
            "model_reported": sorted({r["model_reported"] for r in calls if r.get("model_reported")}),
            "configured_models": sorted({r["model"] for r in calls if r.get("model")}),
        }
    models.setdefault("external_agent", measured(None))
    llm = [r for r in requests if r["role"] not in {"mcp", "external_agent"}]
    compute = sum(s["compute_s"]["value"] or 0 for s in steps)
    llm_s = sum_known(r.get("latency_ms") / 1000 if r.get("latency_ms") is not None else None for r in llm)
    human_wait = sum_known(r.payload.get("decision_wait_s", r.payload.get("wait_s")) for r in human_timing)
    active = sum_known(r.payload.get("active_s") for r in human_timing) if human_timing else measured(None)
    agent_s = sum_known(r.payload.get("decision_wait_s", r.payload.get("wait_s")) for r in agent_timing)
    # Pacing, rate-limit waits and bench cooldowns: infrastructure time, not model or engine time.
    provider_wait = sum((r.get("pacing_wait_s") or 0) + (r.get("rate_limit_wait_s") or 0) for r in llm) + sum(
        r.payload.get("cooldown_s", 0) for r in records if r.type.value == "Note"
    )
    others = [llm_s["value"], compute, human_wait["value"], agent_s["value"], provider_wait]
    overhead = wall - sum(others) if all(v is not None for v in others) else None
    envelopes = []
    for r in requests:
        path = session.root / ".mlca/requests" / (r["request_id"] + ".json")
        import json

        if path.exists():
            entry = json.loads(path.read_text())["egress"]
            if not entry.get("imported"):
                envelopes.append(entry)
    cats = Counter(c for e in envelopes for c in e.get("categories", []))
    artefacts = [
        o
        for s in state.steps
        if s["status"] == "completed"
        for o in s.get("outputs", [])
        if o["kind"] in {"table", "figure"}
    ]
    metrics = [m for s in state.steps if s["status"] == "completed" for m in s.get("metrics", [])]
    covered = 0
    for s in state.steps:
        if s["status"] != "completed":
            continue
        script = session.root / ".mlca/steps" / s["step_id"] / "script.py"
        manifest = session.root / ".mlca/steps" / s["step_id"] / "manifest.json"
        chain = bool(
            s.get("scripts")
            and s.get("runs")
            and script.is_file()
            and sha256(script) == s["scripts"][-1]["sha256"]
        )
        covered += sum(
            chain and (session.root / o["path"]).is_file() and sha256(session.root / o["path"]) == o["sha256"]
            for o in s.get("outputs", [])
            if o["kind"] in {"table", "figure"}
        )
        covered += (
            len(s.get("metrics", []))
            if chain
            and manifest.is_file()
            and any(
                o["name"] == "manifest.json" and sha256(manifest) == o["sha256"] for o in s.get("outputs", [])
            )
            else 0
        )
    denominator = len(artefacts) + len(metrics)
    primary_metric = state.task.get(
        "primary_metric", "roc_auc" if state.template_id == "tabular_classification" else "c_index"
    )
    results = {}
    for split in ("val", "test"):
        selected = next(
            (m for m in reversed(metrics) if m["name"] == primary_metric and m["split"] == split), None
        )
        results[split] = {
            "name": primary_metric,
            "value": measured(selected["value"], "exact") if selected else measured(None),
            "ci": measured(selected.get("ci"), "exact") if selected else measured(None),
        }
    chosen_metric = state.facts.get(
        "best_val_roc_auc" if state.template_id == "tabular_classification" else "best_val_c_index", {}
    ).get("value")
    if chosen_metric is not None:
        results["val"]["value"] = measured(chosen_metric, "exact")
    results["selected_model"] = measured(state.facts.get("best_model", {}).get("value"), "exact")
    approval_requests = [
        r for r in records if r.type.value == "ApprovalRequested" and r.actor.startswith("agent:")
    ]
    request_ids = {r.id for r in approval_requests}
    approval_decisions = [
        r
        for r in records
        if r.type.value == "ApprovalResolved" and r.actor == "user" and r.payload["request_id"] in request_ids
    ]
    sourced_steps = [
        step
        for step in state.steps
        if any((script.get("source") or "").startswith("agent:") for script in step.get("scripts", []))
    ]
    unknown_sources = [
        step
        for step in state.steps
        if any(not script.get("source") and not script.get("builtin") for script in step.get("scripts", []))
    ]
    snapshot_modes = {r.session_id: r.payload["mode"] for r in snapshots}
    modes = {
        r.payload.get("mode", snapshot_modes.get(r.session_id))
        for r in records
        if r.type.value == "StepStarted"
    }
    modes.discard(None)
    run_mode = (
        next(iter(modes))
        if len(modes) == 1
        else "mixed"
        if modes
        else snapshots[-1].payload["mode"]
        if snapshots
        else "unavailable"
    )
    from mlca.evaluation.autonomy import build as autonomy

    proposal_decisions = {r.payload["request_id"]: r for r in records if r.type.value == "ApprovalResolved"}
    return {
        "measurement_arm": state.measurement_arm,
        "schema_version": "1",
        "measurement_kind": "agent_run",
        "autonomy": autonomy(records, requests),
        "run": {
            "snapshot_refs": [r.id for r in snapshots],
            "snapshots": [r.payload for r in snapshots],
            "mode": run_mode,
            "principals": sorted({r.actor for r in records}),
            "start": start.isoformat(),
            "end": end.isoformat(),
            "wall_s": measured(wall),
            "branch": branch,
            "events_reached": sorted(state.event_statuses),
            "completed": measured(
                state.current_event == "report" and all(v == "done" for v in state.event_statuses.values())
            ),
            "task_card_sha256": next(
                (r.payload.get("task_card_sha256") for r in snapshots if r.payload.get("task_card_sha256")),
                None,
            ),
        },
        "steps": {"count": measured(len(steps)), "items": steps},
        "recovery": {
            key: measured(recovery[key])
            for key in ("with_failures", "automatic", "after_human", "unrecovered")
        },
        "failures": {key: measured(value) for key, value in failure_counts.items()},
        "navigator": navigator_use(records),
        "interventions": interventions,
        "brain_mode": {
            "agent_requested_approvals": measured(len(approval_requests), "exact"),
            "human_approval_wait_s": sum_known(r.payload.get("wait_s") for r in approval_decisions),
            "approval_wait_scope": "resolved agent requests decided by user; pending waits excluded",
            "pending_agent_approvals": measured(
                len(
                    request_ids
                    - {r.payload["request_id"] for r in records if r.type.value == "ApprovalResolved"}
                ),
                "exact",
            ),
            "agent_script_steps": measured(len(sourced_steps), "exact"),
            "agent_script_step_share": measured(
                len(sourced_steps) / len(state.steps) if state.steps and not unknown_sources else None,
                "derived",
                denominator="all started steps including engine actions and failures",
            ),
            "unknown_script_source_steps": measured(len(unknown_sources), "exact"),
        },
        "study_proposals": [
            {
                "request_id": r.id,
                "proposer": r.actor,
                "decider": proposal_decisions[r.id].actor if r.id in proposal_decisions else None,
                "decision": proposal_decisions[r.id].payload["decision"]
                if r.id in proposal_decisions
                else "pending",
            }
            for r in approval_requests
            if r.payload["kind"] == "study_fields"
        ],
        "time": {
            "llm_s": llm_s,
            "compute_s": measured(compute),
            "human_wait_s": human_wait,
            "human_active_s": active,
            "agent_decision_s": agent_s,
            "provider_wait_s": measured(provider_wait),
            "engine_overhead_s": measured(
                overhead,
                approximate=True,
                reason="Waits may overlap LLM/compute and include time outside MLCA; negative residuals are retained",
            ),
        },
        "models": models,
        "model_changes": [
            {"record_id": r.id, "actor": r.actor, **r.payload}
            for r in records
            if r.type.value == "ModelChanged"
        ],
        "models_locked": measured(any(r.type.value == "ModelsLocked" for r in session.store.read()), "exact"),
        "egress": {
            "requests": measured(len(envelopes)),
            "bytes": sum_known(e.get("bytes", e.get("bytes_sent")) for e in envelopes),
            "categories": {k: measured(v) for k, v in cats.items()},
            "sample_rows_sent": measured(
                any("sample_rows" in e.get("categories", []) for e in envelopes),
                "exact",
                scope="declared content categories; arbitrary encoding unverified",
            )
            if envelopes and all("categories" in e for e in envelopes)
            else measured(None),
        },
        "provenance": {
            "items": measured(denominator),
            "covered": measured(covered),
            "coverage": measured(covered / denominator if denominator else None),
        },
        "results": results,
        "safeguards": [
            {"category": r.payload["category"], "record_id": r.id, "step_id": r.step_id}
            for r in failed_records
            if r.payload["category"]
            in {
                "scope_layer1",
                "scope_layer2",
                "static_check",
                "fit_rule",
                "test_lock",
                "gate_blocked",
                "privacy_refusal",
                "sandbox_denied",
                "human_decision",
            }
        ],
        "decisions": decisions,
    }


def generate(session, branch=None, out=None):
    result = build(session, branch)
    atomic_json(session.root / "reports/generated/metrics.json", result)
    if out is not None:
        atomic_json(out, result)
    return result
