from .schema import ProjectState, Record


def replay(records: list[Record]) -> ProjectState:
    state = ProjectState()
    for record in records:
        p, kind = record.payload, record.type.value
        state.head = record.id
        state.counts[kind] = state.counts.get(kind, 0) + 1
        if kind == "ProjectCreated":
            state.project_id = p["project_id"]
            state.template_id, state.template_version = p["template_id"], p["template_version"]
        elif kind == "DataRegistered":
            state.data[p["name"]] = p
        elif kind == "InventoryRecorded":
            state.inventory = p["files"]
        elif kind == "BriefRecorded":
            state.brief = p["answers"]
        elif kind == "EventEntered":
            state.current_event = p["event_id"]
            for event in p.get("invalidate_events", []):
                state.event_statuses[event] = "locked"
                state.subgoals = {k: v for k, v in state.subgoals.items() if not k.startswith(event + ".")}
            for event in set(p.get("invalidate_events", []) + [p["event_id"]]):
                state.generations[event] = state.generations.get(event, 0) + 1
                state.confirmations = {
                    k: v for k, v in state.confirmations.items() if not k.startswith(event + ".")
                }
            state.event_statuses[p["event_id"]] = "open"
            state.pending_options = None
        elif kind == "OptionsProposed":
            state.pending_options = p["options"]
        elif kind in ("OptionChosen", "CustomInstructionSubmitted", "TurnEnded"):
            state.pending_options = None
        elif kind == "StepStarted":
            state.steps.append(
                {**p, "event_id": record.event_id, "status": "running", "runs": [], "scripts": []}
            )
        elif kind in ("ScriptWritten", "RunFinished", "StepCompleted", "StepFailed"):
            step = next((s for s in state.steps if s["step_id"] == record.step_id), None)
            if step is not None:
                if kind == "ScriptWritten":
                    step["scripts"].append(p)
                elif kind == "RunFinished":
                    step["runs"].append(p)
                else:
                    step.update(p)
                    step["status"] = "completed" if kind == "StepCompleted" else "failed"
                    for output in p.get("outputs", []):
                        state.artefacts[output["path"]] = {**output, "step_id": record.step_id}
        elif kind == "FactRecorded":
            state.facts[p["key"]] = p
        elif kind == "UserConfirmed":
            state.confirmations[p["subgoal_id"]] = p
        elif kind == "SubgoalChecked":
            state.subgoals[f"{record.event_id}.{p['subgoal_id']}"] = p
            if "event_done" in p:
                state.event_statuses[record.event_id] = "done" if p["event_done"] else "open"
        elif kind == "SplitFrozen":
            state.split = p
            state.test_unlocked = False
        elif kind == "TestUnlocked":
            state.test_unlocked = bool(state.split and p["split_sha256"] == state.split["sha256"])
        elif kind == "EnvironmentRecorded":
            state.lock_sha256 = p["lock_sha256"]
            state.environment_packages = p["packages"]
            state.runtime_sha256 = p.get("runtime_sha256")
    return state
