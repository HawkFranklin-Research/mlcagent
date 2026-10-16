"""Autonomy/rails measurements, derived only from recorded evidence."""

from collections import Counter


def build(records, requests):
    from mlca.evaluation.metrics import measured

    configured = any(r.type.value == "AutonomyConfigured" for r in records)

    def count(kind):
        return measured(sum(r.type.value == kind for r in records) if configured else None, "exact")

    def by_event(kind):
        return (
            {
                str(k): measured(v, "exact")
                for k, v in Counter(r.event_id for r in records if r.type.value == kind).items()
            }
            if configured
            else None
        )

    proposals = [r.payload for r in records if r.type.value == "InferenceRecorded"]
    created = next((r for r in records if r.type.value == "ProjectCreated"), None)
    rail_details = created.payload.get("rails") if created else None
    requests = [r for r in requests if r.get("role") != "mcp"]
    models = Counter(r["model_reported"] for r in requests if r.get("model_reported"))
    return {
        "halt_window_s": next(
            (r.payload["halt_window_s"] for r in reversed(records) if r.type.value == "AutonomyConfigured"),
            None,
        ),
        "halts": count("DecisionWindowHalted"),
        "overrides": count("DecisionOverridden"),
        "halts_by_event": by_event("DecisionWindowHalted"),
        "overrides_by_event": by_event("DecisionOverridden"),
        "auto_resolved_questions": count("QuestionAutoResolved"),
        "questions_asked": measured(
            sum(r.type.value == "QuestionAsked" for r in records) if configured else None, "exact"
        ),
        "inference": {"choices": proposals, "correctness": measured(None)},
        "rails": rail_details or {"version": "rails-0.0", "sha256": None},
        "rails_fired": {
            key: measured(value, "exact")
            for key, value in Counter(
                r.payload["rail_id"] for r in records if r.type.value == "RailFired"
            ).items()
        },
        "model_reported_distribution": {
            key: measured(value, "exact") for key, value in sorted(models.items())
        },
        "model_reported_unavailable": measured(sum(not r.get("model_reported") for r in requests), "exact"),
        "window_wait_s": measured(
            sum(
                r.payload["wait_s"]
                for r in records
                if r.type.value in {"DecisionWindowHalted", "DecisionWindowExpired"}
            )
            if configured
            else None,
            "derived",
        ),
    }
