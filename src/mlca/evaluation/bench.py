"""Independent headless driver runs under an explicit, attributable task-card policy."""

import hashlib
import json
import random
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from mlca.api import Session
from mlca.config import Config
from mlca.errors import BudgetError, MlcaUserError
from mlca.evaluation.metrics import actor_kind, generate, measured
from mlca.llm.usage import read
from mlca.paths import atomic_json, canonical
from mlca.project.init import initialise


class ApprovalPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirm_subgoals: bool = False
    unlock_test: bool = False
    note: str = "Task-card policy approved before the run"
    packages: list[str] = Field(default_factory=list)


class TaskCard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: str = "driver"
    client: str | None = None
    model: str | None = None
    client_timeout_s: int = Field(default=1800, gt=0)
    measurement_arm: str = "worker"
    guided: bool = False
    data: list[str]
    data_roles: dict[str, str] = Field(default_factory=dict)
    primary_data: str | None = None
    brief: dict[str, str]
    template: str = "tabular_classification"
    option_policy: str = "default_first"
    custom_instructions: dict[str, str] | list[dict[str, str]] = Field(default_factory=dict)
    approval_policy: ApprovalPolicy = Field(default_factory=ApprovalPolicy)
    per_run_budget_usd: float = Field(default=10, gt=0)
    total_budget_usd: float = Field(default=30, gt=0)
    max_turns: int = Field(default=100, gt=0)
    # When the provider keeps refusing (rate limits, outage): wait, then retry the step.
    cooldown_s: int = Field(default=600, ge=0)
    max_cooldowns: int = Field(default=3, ge=0)
    config: dict = Field(default_factory=dict)


def drive(session, card, rng, seed):
    if card.guided:
        return drive_guided(session, card)
    customs = set()
    installed = set()
    for _ in range(card.max_turns):
        state = session.state
        event = session.workflow.events[state.current_event]
        if state.current_event == "report" and state.event_statuses.get("report") == "done":
            return
        for package in card.approval_policy.packages:
            if package not in installed:
                if any(c in package for c in (" ", "\n")):
                    raise MlcaUserError("Task-card package specs cannot contain whitespace")
                session.package(package, True, card.approval_policy.note)
                installed.add(package)
        ordinary = [g for g in event.subgoals if g.check.type != "user_confirm"]
        if all(state.subgoals.get(event.id + "." + g.id, {}).get("passed") for g in ordinary):
            for goal in event.subgoals:
                if goal.check.type == "user_confirm" and not state.subgoals.get(
                    event.id + "." + goal.id, {}
                ).get("passed"):
                    if not card.approval_policy.confirm_subgoals:
                        raise MlcaUserError(
                            "Task card does not authorize this confirmation", category="gate_blocked"
                        )
                    session.confirm(goal.id, card.approval_policy.note)
        if session.state.event_statuses.get(event.id) == "done":
            session.next()
            continue
        if event.id == "test" and not session.state.test_unlocked:
            if not card.approval_policy.unlock_test:
                raise MlcaUserError("Task card does not authorize test unlock", category="test_lock")
            session.unlock_test("UNLOCK TEST", card.approval_policy.note)
        if event.id in card.custom_instructions and event.id not in customs:
            customs.add(event.id)
            result = session.custom(card.custom_instructions[event.id])
            if result.get("decision") == "reject":
                raise MlcaUserError("Task-card custom instruction was refused", category="scope_layer1")
        else:
            options = session.options()
            actions = [
                o
                for o in options
                if "action_id" in o and session.workflow.actions[o["action_id"]].role == "primary"
            ]
            if not actions:
                raise MlcaUserError(
                    "No primary action satisfies the remaining checks", category="gate_blocked"
                )
            if card.option_policy == "seeded_random":
                choice = rng.choice(actions)
            elif card.option_policy == "navigator_first":
                choice = actions[0]
            else:
                default = event.default_options[0]
                choice = next((o for o in actions if o["action_id"] == default), actions[0])
            if "seed" in choice.get("params", {}):
                choice = {**choice, "params": {**choice["params"], "seed": seed}}
                session.emit("OptionsProposed", {"options": [choice], "source": "task_card"}, actor="user")
            result = session.choose(choice["id"])
        if result.get("status") not in {"completed"}:
            raise MlcaUserError(
                "Headless driver step did not complete", category="runtime_error:IncompleteStep"
            )
    raise MlcaUserError("Task-card turn limit reached", category="budget_stop")


def catalog_record(card_config, out):
    """Keep the model list each run was chosen from (OpenRouter only): file name and SHA-256."""
    from mlca.config import load, merge
    from mlca.llm.catalog import snapshot

    try:
        config = Config.model_validate(merge(load().model_dump(mode="json"), card_config))
        provider = next((p for p in config.providers.values() if p.kind == "openrouter"), None)
        if provider is None:
            return None
        path, missing = snapshot(provider, config.catalog.selected, out)
        return {
            "file": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "missing": missing,
        }
    except Exception as error:
        return {"error": type(error).__name__}


def structured_record(card_config):
    """Per role: whether requests use JSON-schema output, and why (after the catalogue refresh above)."""
    from mlca.config import load, merge
    from mlca.llm.client import structured_setting

    try:
        config = Config.model_validate(merge(load().model_dump(mode="json"), card_config))
    except Exception as error:
        return {"error": type(error).__name__}
    result = {}
    for role, selected in config.roles.items():
        enabled, source = structured_setting(config.providers[selected.provider], selected.model)
        result[role] = {"model": selected.model, "enabled": enabled, "source": source}
    return result


def charged(root):
    return sum(
        max(r.get("cost_usd") or 0, r.get("reserved_cost_usd") or 0)
        for r in read(root)
        if r["role"] not in {"mcp", "external_agent"}
    )


def run(
    task_path,
    runs,
    out,
    mode="driver",
    budget_usd=None,
    seed=42,
    lock_models=False,
    bio=False,
    client=None,
    model=None,
):
    if mode not in {"driver", "brain"} or runs < 1:
        raise MlcaUserError("Bench requires driver/brain mode and a positive run count")
    path = Path(task_path).resolve()
    raw = path.read_bytes()
    try:
        card = TaskCard.model_validate(yaml.safe_load(raw))
    except ValueError as error:
        raise MlcaUserError("Invalid task-card fields: " + str(error), category="invalid_request") from error
    mode = card.mode if mode == "driver" and card.mode == "brain" else mode
    client, model = client or card.client, model or card.model
    if mode == "brain" and (
        client not in {"opencode", "claude", "codex"} or not model or card.measurement_arm != "worker"
    ):
        raise MlcaUserError(
            "Brain runs require a supported client, explicit model and worker arm", category="invalid_request"
        )
    if card.option_policy not in {"navigator_first", "default_first", "seeded_random"}:
        raise MlcaUserError("Unknown task-card option policy")
    if budget_usd is not None and budget_usd <= 0:
        raise MlcaUserError("Per-run budget must be positive")
    out = Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise MlcaUserError("Choose a fresh empty benchmark output directory")
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(raw).hexdigest()
    if card.measurement_arm not in {"worker", "reference"}:
        raise MlcaUserError("Unknown measurement arm")
    config = {**card.config, "measurement_arm": card.measurement_arm}
    for provider in config.get("providers", {}).values():
        if provider.get("script"):
            provider["script"] = str((path.parent / provider["script"]).resolve())
    try:
        Config.model_validate(config)
    except ValueError as error:
        raise MlcaUserError("Invalid task-card config: " + str(error), category="invalid_request") from error
    data = [(path.parent / p).resolve() for p in card.data]
    manifest = {
        "schema_version": "1",
        "mode": mode,
        "client": client if mode == "brain" else None,
        "model": model or config.get("roles", {}).get("worker", {}).get("model"),
        "task": Path(card.data[0]).stem,
        "kind": "independent_agent_runs" if card.measurement_arm == "worker" else "no_ai_reference_runs",
        "measurement_arm": card.measurement_arm,
        "task_card_sha256": digest,
        "models_locked": lock_models,
        "policy_principal": "user:policy/" + digest[:12],
        "runs": [],
    }
    manifest["model_catalog"] = (
        catalog_record(config, out) if card.measurement_arm == "worker" and mode == "driver" else None
    )
    manifest["structured_outputs"] = (
        structured_record(config) if card.measurement_arm == "worker" and mode == "driver" else {}
    )
    atomic_json(out / "bench.json", manifest)
    total = 0.0
    for index in range(runs):
        project = out / f"run-{index + 1:03d}"
        entry = {"run": index + 1, "project": project.name, "status": "failed"}
        manifest["runs"].append(entry)
        atomic_json(out / "bench.json", manifest)
        session = None
        try:
            initialise(
                project,
                data,
                card.template,
                card.brief,
                config,
                principal=manifest["policy_principal"],
                primary_data=card.primary_data,
                data_roles=card.data_roles,
            )
            session = Session.open(
                project, client="bench", principal=manifest["policy_principal"], policy=True, mode=mode
            )
            if lock_models:
                session.lock_models()
            session.task_card_sha256 = digest
            remaining = card.total_budget_usd - total
            session.config.budgets.session_max_usd = min(
                budget_usd or card.per_run_budget_usd,
                session.config.budgets.session_max_usd,
                max(remaining, 1e-12),
            )
            session.emit(
                "Note",
                {
                    "text": "Independent task-card run",
                    "task_card_sha256": digest,
                    "policy_seed": seed + index,
                    "split_seed": seed,
                    "measurement_kind": "agent_run"
                    if card.measurement_arm == "worker"
                    else "no_ai_reference",
                },
                actor="user",
            )
            if remaining <= 0:
                session.emit("BudgetStopped", {"reason": "Total benchmark budget exhausted"})
                raise BudgetError("Total benchmark budget exhausted")
            if mode == "brain":
                from mlca.evaluation.brain import run as brain_run

                entry["brain_client"] = brain_run(session, card, client, model, card.client_timeout_s)
                if bio:
                    from mlca.evaluation.bio_bench import export_instructions

                    export_instructions(session)
            elif bio:
                from mlca.evaluation.bio_bench import drive as bio_drive

                bio_drive(session, card, random.Random(seed + index), seed)
            else:
                drive(session, card, random.Random(seed + index), seed)
            entry["status"] = "completed"
        except Exception as error:
            entry["error_type"] = type(error).__name__
            entry["message"] = session.redact(str(error)) if session else str(error)
            entry["category"] = getattr(error, "category", "runtime_error:" + type(error).__name__)
            if session:
                session.emit("Refusal", {"category": entry["category"], "operation": "bench"}, actor="user")
        finally:
            if session:
                if bio:
                    from mlca.evaluation.bio_bench import export_instructions

                    export_instructions(session)
                session.close()
                generate(session)
                total += charged(project)
            entry["reserved_or_actual_charge_usd"] = measured(charged(project) if session else None)
            atomic_json(out / "bench.json", manifest)
    summarize(out)
    return manifest


def distribution(values):
    values = list(values)
    known = [v for v in values if v is not None]
    return {
        "n": measured(len(known)),
        "unavailable": measured(len(values) - len(known)),
        "mean": measured(statistics.mean(known) if known else None),
        "sd": measured(statistics.stdev(known) if len(known) > 1 else None),
        "min": measured(min(known) if known else None),
        "max": measured(max(known) if known else None),
    }


def _model_total(metrics, key, mode):
    if not metrics:
        return None
    entries = [
        r
        for role, r in metrics["models"].items()
        if (role == "external_agent") == (mode == "brain") and "calls" in r
    ]
    if mode == "brain" and not entries:
        return None
    values = [r.get(key, {"value": None}) for r in entries]
    if any(v["value"] is None or v.get("partial") for v in values):
        return None
    return sum(v["value"] for v in values)


def summarize(out):
    out = Path(out)
    if not (out / "bench.json").exists():
        from mlca.evaluation.cross_arms import summarize as summarize_arms

        return summarize_arms(out)
    manifest = json.loads((out / "bench.json").read_text())
    loaded = []
    for run in manifest["runs"]:
        file = out / run["project"] / "reports/generated/metrics.json"
        loaded.append(json.loads(file.read_text()) if file.exists() else None)
    count = len(loaded)
    completed = sum(bool(m and m["run"]["completed"]["value"]) for m in loaded)
    sequences = [
        [(d["event"], d["action_id"], d["params_hash"]) for d in m["decisions"]] if m else None
        for m in loaded
    ]
    pairs = []
    for i in range(count):
        for j in range(i + 1, count):
            a, b = sequences[i], sequences[j]
            if a is None or b is None:
                pairs.append(None)
            else:
                denominator = max(len(a), len(b))
                pairs.append(sum(x == y for x, y in zip(a, b)) / denominator if denominator else None)
    event_sequences = defaultdict(list)
    events = {d[0] for sequence in sequences if sequence for d in sequence}
    for event in sorted(events):
        for sequence in sequences:
            event_sequences[event].append(
                tuple(d[1] for d in sequence if d[0] == event) if sequence is not None else None
            )
    failures = Counter()
    for run, m in zip(manifest["runs"], loaded):
        if m:
            failures.update({key: val["value"] for key, val in m["failures"].items()})
        elif run.get("category"):
            failures[run["category"]] += 1

    def values(section, key):
        return [m[section][key]["value"] if m else None for m in loaded]

    metrics = {
        split: distribution(m["results"][split]["value"]["value"] if m else None for m in loaded)
        for split in ("val", "test")
    }
    summary = {
        "kind": manifest.get("kind", "independent_agent_runs"),
        "measurement_arm": manifest.get("measurement_arm", "worker"),
        "runs": manifest["runs"],
        "run_count": measured(count),
        "completed": measured(completed),
        "completion_rate": measured(completed / count if count else None),
        # Completions on built-in cards after Navigator failures measure the engine, not the model.
        "navigator_fallback_rate": distribution(
            m["navigator"]["fallback_rate"]["value"] if m and "navigator" in m else None for m in loaded
        ),
        "navigator_fallbacks": measured(
            sum(m["navigator"]["fallbacks"]["value"] for m in loaded if m and "navigator" in m)
        ),
        "navigator_budget_stops": measured(
            sum(m["navigator"]["budget_stops"]["value"] for m in loaded if m and "navigator" in m)
        ),
        "completed_without_navigator_fallback": measured(
            sum(
                bool(m["run"]["completed"]["value"])
                and "navigator" in m
                and m["navigator"]["fallbacks"]["value"] == 0
                for m in loaded
                if m
            )
        ),
        "failures": {k: measured(v) for k, v in failures.items()},
        "steps_per_run": distribution(values("steps", "count")),
        "first_try_success_rate": distribution(
            sum(s["first_try_success"]["value"] for s in m["steps"]["items"]) / len(m["steps"]["items"])
            if m and m["steps"]["items"]
            else None
            for m in loaded
        ),
        "automatic_recovery_rate": distribution(
            m["recovery"]["automatic"]["value"] / m["recovery"]["with_failures"]["value"]
            if m and m["recovery"]["with_failures"]["value"]
            else None
            for m in loaded
        ),
        "time": {
            key: distribution(values("time", key))
            for key in (
                "llm_s",
                "compute_s",
                "human_wait_s",
                "human_active_s",
                "agent_decision_s",
                "engine_overhead_s",
            )
        },
        "tokens": {
            key: distribution(_model_total(m, key, manifest.get("mode", "driver")) for m in loaded)
            for key in (
                "input_tokens",
                "output_tokens",
                "reasoning_tokens",
                "cached_tokens",
                "cache_write_tokens",
                "cost_usd",
            )
        },
        "cost_sources": sorted(
            {
                source
                for m in loaded
                if m
                for role, model in m["models"].items()
                if (role == "external_agent") == (manifest.get("mode") == "brain") and "calls" in model
                for source in model["cost_sources"]
            }
        ),
        "interventions": {
            kind: distribution(
                sum(
                    v["value"]
                    for actor, group in m["interventions"].items()
                    if actor_kind(actor) == kind
                    for key, v in group.items()
                    if key not in {"kind", "script_lines", "custom_words"}
                )
                if m
                else None
                for m in loaded
            )
            for kind in ("policy", "human", "agent")
        },
        "results": metrics,
        "decision_consistency": {
            "exact_sequences": measured(
                max(Counter(canonical(s) for s in sequences if s is not None).values())
                / sum(s is not None for s in sequences)
                if any(s is not None for s in sequences)
                else None
            ),
            "available_sequences": measured(sum(s is not None for s in sequences)),
            "unavailable_sequences": measured(sum(s is None for s in sequences)),
            "pairwise": distribution(pairs),
            "per_event": {
                event: measured(
                    max(Counter(s for s in seq if s is not None).values()) / sum(s is not None for s in seq)
                )
                for event, seq in event_sequences.items()
            },
        },
        "limits": "Sample SD needs at least two available values. Failures are retained; unavailable fields are excluded only from each numeric statistic and counted explicitly. Recovery rate is undefined without failures.",
    }
    summary.update({key: manifest.get(key) for key in ("mode", "client", "model", "task")})
    if manifest.get("mode") == "brain":
        summary["navigator_fallbacks"] = measured(None)
        summary["navigator_budget_stops"] = measured(None)
        summary["completed_without_navigator_fallback"] = measured(None)
        summary["navigator_fallback_rate"] = distribution([None] * count)
        if not any(m and "calls" in m["models"].get("external_agent", {}) for m in loaded):
            summary["tokens"] = {key: distribution([None] * count) for key in summary["tokens"]}
    atomic_json(out / "bench_summary.json", summary)
    lines = [
        "# Benchmark summary",
        "",
        f"Runs: {count}",
        f"Completed: {completed}",
        f"Completion rate: {summary['completion_rate']['value']}",
        "",
        "Independent agent runs, not frozen-code replay. Policy decisions are not human interventions.",
        "",
        "Detailed sourced statistics and unavailable counts: bench_summary.json",
        "",
        "| Run | Status |",
        "|---|---|",
    ]
    lines.extend(f"| {r['project']} | {r['status']} |" for r in manifest["runs"])
    (out / "bench_summary.md").write_text("\n".join(lines) + "\n")
    return summary


def provider_stopped(session):
    """True when the last categorised record of the run is a provider failure."""
    categorised = [r for r in session.store.read() if r.payload.get("category")]
    return bool(categorised) and categorised[-1].payload["category"] == "provider_error"


def drive_guided(session, card, sleep=time.sleep):
    cooldowns = 0
    for _ in range(card.max_turns):
        result = session.autopilot(card.max_turns)
        if result["reason"] == "completed":
            return
        if result["reason"] == "failure" and provider_stopped(session) and cooldowns < card.max_cooldowns:
            cooldowns += 1
            with session.mutation():
                session.emit(
                    "Note",
                    {
                        "text": "Provider unavailable; waiting before retrying the step",
                        "cooldown_s": card.cooldown_s,
                    },
                    actor="user",
                )
            sleep(card.cooldown_s)
            for q in session.questions():
                retry = next(
                    (
                        i
                        for i, o in enumerate(q.get("options", []))
                        if o.get("effect", {}).get("kind") == "retry"
                    ),
                    None,
                )
                if retry is not None:
                    session.answer_question(q["question_id"], retry)
            continue
        if result["reason"] == "question":
            for q in session.questions():
                session.answer_question(q["question_id"], q["recommended"])
        elif result["reason"] == "approval":
            for choice in result["turn"]:
                if choice["id"].startswith("human:confirm:"):
                    if not card.approval_policy.confirm_subgoals:
                        raise MlcaUserError("Task card does not authorize confirmation")
                    session.confirm(choice["id"].split(":", 2)[2], card.approval_policy.note)
                elif choice["id"] == "human:unlock":
                    if not card.approval_policy.unlock_test:
                        raise MlcaUserError("Task card does not authorize test unlock")
                    session.unlock_test("UNLOCK TEST", card.approval_policy.note)
        else:
            raise MlcaUserError("Guided run stopped: " + result["reason"])
    raise MlcaUserError("Guided task-card turn limit reached")
