"""Validated questions and engine-owned answer effects."""

from datetime import datetime, timezone

from pydantic import Field
from ulid import ULID

from mlca.errors import MlcaUserError
from mlca.log.schema import StrictModel

from . import data_review


class AnswerOption(StrictModel):
    label: str = Field(min_length=1, max_length=60)
    description: str = Field(max_length=400)
    effect: dict


class Question(StrictModel):
    header: str = Field(min_length=1, max_length=30)
    question: str = Field(min_length=1, max_length=600)
    options: list[AnswerOption] = Field(min_length=1, max_length=4)
    recommended: int = Field(default=0, ge=0)
    multiple: bool = False
    why: str = Field(default="", max_length=600)
    explicit: bool = False
    human_only: bool = False
    allowed_values: list[str] = Field(default_factory=list)


def ask(session, question, *, asker="engine", key="question"):
    parsed = Question.model_validate({k: v for k, v in question.items() if k != "key"})
    if parsed.recommended >= len(parsed.options):
        raise MlcaUserError("Question recommendation is out of range", category="invalid_request")
    if any(not 1 <= len(o.label.split()) <= 5 for o in parsed.options):
        raise MlcaUserError("Question labels must have one to five words", category="invalid_request")
    qid = str(ULID())
    payload = {**parsed.model_dump(), "question_id": qid, "asker": asker, "key": key}
    session.emit("QuestionAsked", payload, actor=asker)
    return qid


def pending(session):
    return [
        {**q, "how": {"question_id": key, "command": f"mlca questions answer {key} <index>"}}
        for key, q in session.state.questions.items()
        if key not in session.state.answers
    ]


def review(session):
    state = session.state
    if state.current_event != "data" or state.split or session._ever_unlocked():
        raise MlcaUserError(
            "Data review belongs before the frozen split",
            category="test_lock" if state.split else "gate_blocked",
        )
    digest = data_review.context_key(state)
    if state.data_review_context != digest:
        session.emit(
            "DataReviewStarted", {"context_sha256": digest, "rules_version": data_review.RULE_VERSION}
        )
        for finding in data_review.findings(
            data_review.source_frame(state),
            state.columns,
            state.template_id,
            state.brief.get("repeated_subjects", ""),
            state.outcome_reviewed,
            state.outcome_exclusions,
        ):
            ask(session, finding, key=finding["key"])
    if not pending(session):
        data_review.prepared(session)
    return pending(session)


def answer(session, qid, index=None, *, default=False, free_text=None):
    state = session.state
    q = state.questions.get(qid)
    if q is None or qid in state.answers or q["event_id"] != state.current_event:
        raise MlcaUserError("Question is no longer awaiting an answer", category="invalid_request")
    if q.get("human_only"):
        session._require_human()
    if default and q.get("explicit"):
        raise MlcaUserError("This decision requires an explicit answer", category="human_decision")
    if default:
        index = q["recommended"]
    effect = None
    if free_text:
        if q.get("key") == "positive_class" and free_text.strip() in q.get("allowed_values", []):
            effect = {"kind": "positive_class", "column": state.columns["target"], "value": free_text.strip()}
            index = -1
        else:
            matches = [
                i
                for i, option in enumerate(q["options"])
                if option["label"].casefold() == free_text.strip().casefold()
            ]
            if len(matches) != 1:
                raise MlcaUserError(
                    "Choose an option or use the guided free-text mapping", category="invalid_request"
                )
            index = matches[0]
    if effect is None:
        if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(q["options"]):
            raise MlcaUserError("Choose a listed answer", category="invalid_request")
        effect = q["options"][index]["effect"]
    data_kinds = {
        "keep",
        "set_outcome",
        "merge_labels",
        "encode_event",
        "merge_rare",
        "drop_classes",
        "exclude_column",
        "drop_missing",
        "drop_duplicates",
        "positive_times",
        "set_group",
        "set_task",
        "positive_class",
        "choose_positive",
    }
    if effect["kind"] in data_kinds:
        if state.split or session._ever_unlocked():
            raise MlcaUserError("Data decisions are closed after split freezing", category="test_lock")
        if effect["kind"] != "choose_positive":
            candidate, _, _, mode = data_review.apply(
                data_review.source_frame(state), state.data_decisions + [{"effect": effect}]
            )
            data_review.task_for(candidate, state, mode)
    requested = next(
        r for r in session.store.read() if r.type.value == "QuestionAsked" and r.payload["question_id"] == qid
    )
    wait = max(0, (datetime.now(timezone.utc) - requested.ts).total_seconds())
    session.emit(
        "QuestionAnswered",
        {
            "question_id": qid,
            "answer": index,
            "by": "default"
            if default
            else "policy"
            if session.is_policy
            else "user"
            if session.principal == "user"
            else "agent",
            "free_text": free_text,
            "decision_wait_s": wait,
        },
        actor="user",
    )
    if effect["kind"] == "set_outcome" and effect["column"] != state.columns["target"]:
        session.emit(
            "OutcomeSelected",
            {"column": effect["column"], "excluded_columns": effect["exclude"]},
            actor="user",
        )
        return review(session)
    if effect["kind"] == "choose_positive":
        target = state.columns["target"]
        reviewed, _, _, _ = data_review.apply(data_review.source_frame(state), state.data_decisions)
        values = reviewed[target].dropna().astype(str).unique().tolist()
        ask(
            session,
            {
                "header": "Positive group",
                "question": "Which group should be predicted against the rest? Type an exact label for groups beyond the first four.",
                "options": [
                    {
                        "label": f"Group {i + 1}",
                        "description": value[:400],
                        "effect": {"kind": "positive_class", "column": target, "value": value},
                    }
                    for i, value in enumerate(values[:4])
                ],
                "allowed_values": values,
                "explicit": True,
                "human_only": True,
            },
            key="positive_class",
        )
        return pending(session)
    allowed = {
        "keep",
        "set_outcome",
        "merge_labels",
        "encode_event",
        "merge_rare",
        "drop_classes",
        "exclude_column",
        "drop_missing",
        "drop_duplicates",
        "positive_times",
        "set_group",
        "set_task",
        "positive_class",
    }
    if effect["kind"] in allowed:
        if state.split or session._ever_unlocked():
            raise MlcaUserError("Data decisions are closed after split freezing", category="test_lock")
        session.emit(
            "DataDecision",
            {"question_id": qid, "effect": effect, "rule": q.get("key", "question")},
            actor="user",
        )
        if not pending(session):
            data_review.prepared(session)
    else:
        # Guided turn questions use validated, non-data effects implemented by the turn engine.
        from .guided import apply_effect

        apply_effect(session, effect)
    return pending(session)
