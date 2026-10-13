from .schema import ProjectState, Record


def replay(records: list[Record]) -> ProjectState:
    state = ProjectState()
    for record in records:
        p, kind = record.payload, record.type.value
        state.head = record.id
        state.counts[kind] = state.counts.get(kind, 0) + 1
        if kind == "GuidedFlowEnabled":
            state.guided_enabled = True
        elif kind == "ComparisonRequested":
            state.compare_models = True
        elif kind == "TurnPresented":
            state.presented_turn = p
        elif kind == "DataReviewStarted":
            state.guided_enabled = True
            state.data_review_context = p["context_sha256"]
            state.questions, state.answers, state.data_decisions = {}, {}, []
            state.prepared_data = None
        elif kind == "QuestionAsked":
            state.questions[p["question_id"]] = {**p, "event_id": record.event_id}
        elif kind == "QuestionAnswered":
            state.answers[p["question_id"]] = p
            state.pending_options = None
            state.presented_turn = None
        elif kind == "OutcomeSelected":
            state.columns["target"] = p["column"]
            state.brief["target"] = p["column"]
            state.outcome_reviewed = True
            state.outcome_exclusions = p["excluded_columns"]
        elif kind == "DataDecision":
            if p["effect"]["kind"] == "set_outcome":
                state.outcome_reviewed = True
            state.data_decisions.append({**p, "actor": record.actor})
            state.prepared_data = None
        elif kind == "TaskConfigured":
            state.task = p["task"]
            state.excluded_columns = p.get("excluded_columns", [])
            state.group_column = p.get("group_column")
        elif kind == "DataPrepared":
            state.prepared_data = p
        elif kind == "ProjectCreated":
            state.project_id = p["project_id"]
            state.template_id, state.template_version = p["template_id"], p["template_version"]
        elif kind == "DataRegistered":
            state.data[p["name"]] = p
        elif kind == "InventoryRecorded":
            state.inventory = p["files"]
        elif kind in {"BriefRecorded", "StudyFieldsResolved"}:
            if kind == "BriefRecorded":
                state.original_brief = p["answers"]
            state.brief = p["answers"]
            state.columns = p.get("columns", {})
            state.primary_data = p.get("primary_data")
        elif kind == "EventEntered":
            state.presented_turn = None
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
        elif kind == "ModelChanged":
            state.presented_turn = None
            state.pending_options = None
        elif kind == "OptionsProposed":
            state.pending_options = p["options"]
        elif kind in (
            "OptionChosen",
            "CustomInstructionSubmitted",
            "TurnEnded",
            "BranchCreated",
            "BranchCheckedOut",
        ):
            state.pending_options = None
            state.presented_turn = None
        elif kind == "StepStarted":
            state.steps.append(
                {**p, "event_id": record.event_id, "status": "running", "runs": [], "scripts": []}
            )
        elif kind in ("ScriptRequested", "ScriptWritten", "RunFinished", "StepCompleted", "StepFailed"):
            step = next((s for s in state.steps if s["step_id"] == record.step_id), None)
            if step is not None:
                if kind == "ScriptRequested":
                    step.update(status="awaiting_script", work_order=p["work_order"], attempt=p["attempt"])
                elif kind == "ScriptWritten":
                    step["status"] = "running"
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
            state.presented_turn = None
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
