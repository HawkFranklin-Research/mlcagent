"""Generic pre-split data review. Findings are heuristics, never proof of leakage."""

import hashlib
import re
from pathlib import Path

import pandas as pd

from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import atomic_json, canonical, sha256
from mlca.project.init import primary_for
from mlca.project.inventory import read_table
from mlca.task_metrics import default_metric

RULE_VERSION = "1"


def normalized(value):
    return re.sub(r"[\s.,;:!?]+$", "", str(value).strip()).casefold()


def source_frame(state):
    entry = state.data[primary_for(state)]
    path = Path(entry["original_path"])
    if sha256(path) != entry["sha256"]:
        raise IntegrityError("Registered input changed")
    return read_table(path).reset_index(drop=True)


def context_key(state):
    return hashlib.sha256(
        canonical(
            {
                "source": state.data[primary_for(state)]["sha256"],
                "columns": state.columns,
                "repeated": state.brief.get("repeated_subjects"),
                "rules": RULE_VERSION,
            }
        ).encode()
    ).hexdigest()


def findings(frame, columns, template, repeated="", outcome_reviewed=False, excluded=(), phase="all"):
    target = (
        (columns.get("duration") or columns.get("target"))
        if template == "survival"
        else columns.get("target")
    )
    if template in {"regression", "multilabel_classification", "clustering", "representation"}:
        targets = [c for c in columns.values() if c is not None]
        if phase == "train":
            return []
        result = []
        if targets and frame[targets].isna().any().any():
            result.append(
                {
                    "key": "missing_outcomes",
                    "header": "Missing outcomes",
                    "question": "Exclude rows with missing outcomes before the frozen split?",
                    "recommended": 0,
                    "explicit": True,
                    "human_only": True,
                    "options": [
                        {
                            "label": "Exclude missing outcomes",
                            "description": "Keep complete targets",
                            "effect": {"kind": "drop_missing", "columns": targets},
                        },
                        {
                            "label": "Keep unchanged",
                            "description": "Retain missing targets",
                            "effect": {"kind": "keep"},
                        },
                    ],
                }
            )
        return result
    if target not in frame:
        raise MlcaUserError("Choose the outcome column before reviewing the table", category="gate_blocked")
    if template == "survival" and columns.get("event_column") not in frame:
        raise MlcaUserError("Choose the survival event column", category="gate_blocked")
    result = []

    def add(rule, header, question, effect, alternatives=(), sensitive=False):
        labels_by_effect = {
            "merge_labels": "Merge labels",
            "exclude_column": "Exclude column",
            "set_outcome": "Use this outcome",
            "drop_duplicates": "Remove duplicate rows",
            "drop_missing": "Exclude missing outcomes",
            "set_task": "Predict all groups",
            "set_group": "Keep subjects together",
            "positive_times": "Exclude invalid times",
            "encode_event": "Use this coding",
        }
        options = [
            {
                "label": labels_by_effect.get(effect["kind"], "Use recommendation"),
                "description": question,
                "effect": effect,
            }
        ]
        options.extend(alternatives)
        result.append(
            {
                "key": rule,
                "header": header,
                "question": question,
                "options": options,
                "recommended": 0,
                "multiple": False,
                "explicit": sensitive,
                "human_only": sensitive,
                "why": "Generic table-property check; author review is required.",
            }
        )

    keep = {
        "label": "Keep unchanged",
        "description": "Retain the original values or feature.",
        "effect": {"kind": "keep"},
    }
    labels = frame[target].dropna().unique().tolist()
    if template != "survival":
        candidates = [target] + [
            c
            for c in frame
            if c != target
            and c not in excluded
            and re.search(
                r"(^|[ _.-])(target|label|class|outcome|diagnosis|result|status|response)([ _.-]|$)", c, re.I
            )
        ]
        if len(candidates) > 1 and not outcome_reviewed:
            add(
                "outcome_choice",
                "Outcome choice",
                "Several columns look like outcomes. Confirm which to predict; the others will be excluded.",
                {"kind": "set_outcome", "column": target, "exclude": candidates[1:]},
                [
                    {
                        "label": f"Outcome {i + 2}",
                        "description": c[:400],
                        "effect": {
                            "kind": "set_outcome",
                            "column": c,
                            "exclude": [v for v in candidates if v != c],
                        },
                    }
                    for i, c in enumerate(candidates[1:4])
                ],
                True,
            )
        groups = {}
        for value in labels:
            groups.setdefault(normalized(value), []).append(str(value))
        if any(len(values) > 1 for values in groups.values()):
            mapping = {str(value): normalized(value) for value in labels}
            add(
                "outcome_labels",
                "Outcome labels",
                "Some outcome labels differ only in spacing, case or punctuation. Merge them?",
                {"kind": "merge_labels", "column": target, "mapping": mapping},
                [keep],
                True,
            )
        if len({normalized(v) for v in labels}) > 2:
            add(
                "multiclass",
                "Prediction groups",
                "Predict all outcome groups, or one group against the rest?",
                {"kind": "set_task", "mode": "multiclass"},
                [
                    {
                        "label": "One against rest",
                        "description": "Choose a positive group explicitly.",
                        "effect": {"kind": "choose_positive"},
                    }
                ],
            )
        counts = frame[target].value_counts()
        rare = counts[(counts < 10) | (counts / len(frame) < 0.01)]
        if not rare.empty:
            values = [str(v) for v in rare.index]
            add(
                "rare_classes",
                "Rare groups",
                "Some outcome groups have fewer than 10 rows or under 1% of rows. Keep them?",
                {"kind": "keep"},
                [
                    {
                        "label": "Merge rare groups",
                        "description": "Combine rare groups as other; review explicitly.",
                        "effect": {"kind": "merge_rare", "column": target, "values": values},
                    },
                    {
                        "label": "Drop rare groups",
                        "description": "Exclude these groups before freezing partitions.",
                        "effect": {"kind": "drop_classes", "column": target, "values": values},
                    },
                ],
                True,
            )
    if frame[target].isna().any():
        add(
            "missing_outcome",
            "Missing outcomes",
            "Some outcomes are missing. Exclude those rows before splitting?",
            {"kind": "drop_missing", "columns": [target]},
            [keep],
            True,
        )
    if template == "survival":
        event = columns.get("event_column")
        if frame[event].dropna().eq(0).all():
            candidates = [c for c in frame if c not in {target, event} and frame[c].dropna().nunique() == 2]
            candidates.sort(key=lambda c: not bool(re.search(r"event|status|cens|observed|death", c, re.I)))
            if candidates:
                add(
                    "event_choice",
                    "Event status",
                    "The selected event indicator contains no observed events. Which column records the event? Confirm its meaning.",
                    {"kind": "set_event_column", "column": candidates[0]},
                    [
                        {
                            "label": f"Column {i + 2}",
                            "description": c,
                            "effect": {"kind": "set_event_column", "column": c},
                        }
                        for i, c in enumerate(candidates[1:4])
                    ],
                    True,
                )
                result[-1]["options"][0]["label"] = "Use " + candidates[0].split()[0][:40]
                result[-1]["options"][0]["description"] = candidates[0]
    protected = {target, columns.get("duration"), columns.get("event_column")}
    for column in frame:
        if column in protected or column in excluded:
            continue
        values = frame[column]
        distinct = values.nunique(dropna=True)
        identifier = distinct == len(frame) and (
            not pd.api.types.is_float_dtype(values)
            or re.search(r"(^|[ _.-])(id|identifier)([ _.-]|$)", column, re.I)
        )
        if identifier:
            add(
                "identifier:" + column,
                "Identifier feature",
                f"{column} looks like a row identifier. Exclude it from prediction?",
                {"kind": "exclude_column", "column": column},
                [keep],
            )
        probable = False
        categorical_mapping = False
        for outcome in protected - {None} if phase != "pre" else []:
            complete = frame[[column, outcome]].dropna().copy()
            if template != "survival":
                complete[outcome] = complete[outcome].map(normalized)
            if (
                len(complete)
                and complete[outcome].nunique() > 1
                and 1 < distinct <= min(50, max(2, len(frame) // 5))
            ):
                mapping = complete.groupby(column, observed=True)[outcome].nunique().max() == 1
                probable |= mapping
                categorical_mapping |= (
                    mapping and complete.groupby(outcome, observed=True)[column].nunique().max() == 1
                )
            if template != "survival" and len(labels) == 2 and pd.api.types.is_numeric_dtype(values):
                intervals = complete.groupby(outcome, observed=True)[column].agg(["min", "max"])
                if len(intervals) == 2:
                    probable |= (
                        intervals.iloc[0]["max"] < intervals.iloc[1]["min"]
                        or intervals.iloc[1]["max"] < intervals.iloc[0]["min"]
                    )
        named = any(str(outcome).casefold() in str(column).casefold() for outcome in protected - {None})
        if probable or (named and phase != "train"):
            add(
                "leakage:" + column,
                "Possible outcome source",
                f"{column} may encode or determine the outcome. Exclude it? This check cannot prove leakage.",
                {"kind": "exclude_column", "column": column},
                [keep],
                True,
            )
            if probable and not named and not categorical_mapping and pd.api.types.is_numeric_dtype(values):
                result[-1]["options"].reverse()
                result[-1]["options"][0]["label"] = "Keep and flag"
                result[-1]["options"][0]["description"] = (
                    "Keep this potentially strong predictor and flag the training-only finding in the report."
                )
        if values.isna().mean() > 0.5:
            add(
                "missing:" + column,
                "Mostly missing feature",
                f"More than half of {column} is missing. Exclude it?",
                {"kind": "exclude_column", "column": column},
                [keep],
            )
        if (
            str(repeated).casefold() != "no"
            and values.duplicated().any()
            and distinct >= 3
            and re.search(r"(^|[ _.-])(patient|subject|participant|group|id)([ _.-]|$)", column, re.I)
        ):
            add(
                "group:" + column,
                "Repeated units",
                f"Do rows sharing {column} belong to the same unit?",
                {"kind": "set_group", "column": column},
                [keep],
                True,
            )
    if frame.duplicated().any():
        add(
            "duplicates",
            "Duplicate rows",
            "Some rows are exact copies. Remove duplicates before splitting?",
            {"kind": "drop_duplicates"},
            [keep],
        )
    if template == "survival":
        event = columns.get("event_column")
        times = pd.to_numeric(frame[target], errors="coerce")
        if (times.isna() | (times <= 0)).any():
            add(
                "invalid_times",
                "Invalid follow-up",
                "Some times are missing or non-positive. Exclude those rows?",
                {"kind": "positive_times", "column": target},
                [keep],
                True,
            )
        if event not in frame:
            raise MlcaUserError("Choose the survival event column", category="gate_blocked")
        event_values = frame[event].dropna().unique().tolist()
        if not set(event_values) <= {0, 1}:
            if len(event_values) != 2:
                raise MlcaUserError(
                    "Review the nonbinary survival event definition before proceeding",
                    category="gate_blocked",
                )
            codes = sorted(event_values, key=str)
            add(
                "event_codes",
                "Event coding",
                "Which code means that the event happened? Confirm the coding explicitly.",
                {"kind": "encode_event", "column": event, "mapping": {str(codes[0]): 0, str(codes[1]): 1}},
                [
                    {
                        "label": "Reverse coding",
                        "description": "Use the first code as event and the second as censored.",
                        "effect": {
                            "kind": "encode_event",
                            "column": event,
                            "mapping": {str(codes[0]): 1, str(codes[1]): 0},
                        },
                    }
                ],
                True,
            )
        if frame[event].isna().any():
            add(
                "missing_events",
                "Missing event status",
                "Some event indicators are missing. Exclude those rows?",
                {"kind": "drop_missing", "columns": [event]},
                [keep],
                True,
            )
    return [q for q in result if phase != "train" or q["key"].startswith("leakage:")]


def apply(frame, decisions, preserve_index=False):
    frame = frame.copy()
    excluded, group, mode = [], None, None
    for decision in decisions:
        effect = decision["effect"]
        kind = effect["kind"]
        column = effect.get("column")
        if kind == "set_outcome":
            excluded.extend(effect["exclude"])
        elif kind in {"merge_labels", "encode_event"}:
            frame[column] = frame[column].map(
                lambda v: effect["mapping"].get(str(v), v) if pd.notna(v) else v
            )
        elif kind == "merge_rare":
            frame[column] = frame[column].astype(object)
            frame.loc[frame[column].astype(str).isin(effect["values"]), column] = "other"
        elif kind == "drop_classes":
            frame = frame.loc[~frame[column].astype(str).isin(effect["values"])]
        elif kind == "exclude_column":
            excluded.append(column)
        elif kind == "drop_missing":
            frame = frame.dropna(subset=effect["columns"])
        elif kind == "drop_duplicates":
            frame = frame.drop_duplicates()
        elif kind == "positive_times":
            frame = frame.loc[pd.to_numeric(frame[column], errors="coerce") > 0]
        elif kind == "set_group":
            group = column
            excluded.append(column)
        elif kind == "set_task":
            mode = effect["mode"]
        elif kind == "positive_class":
            frame[column] = (frame[column].astype(str) == effect["value"]).astype(int)
            mode = "binary"
    # Keep grouping columns in the partitions, but exclude them from prediction through the protocol.
    return (frame if preserve_index else frame.reset_index(drop=True)), sorted(set(excluded)), group, mode


def task_for(frame, state, mode=None):
    if state.template_id in {"regression", "multilabel_classification", "clustering", "representation"}:
        task = dict(state.task)
        targets = [c for c in state.columns.values() if c is not None]
        kind = (
            "multioutput_regression"
            if state.template_id == "regression" and len(targets) > 1
            else {"multilabel_classification": "multilabel"}.get(state.template_id, state.template_id)
        )
        return {
            **task,
            "type": kind,
            "targets": targets,
            "primary_metric": task.get("primary_metric", default_metric(kind)),
        }
    target = state.columns["target"]
    n = int(frame[target].nunique())
    if state.template_id == "survival":
        event = state.columns["event_column"]
        codes = set(frame[event].dropna().unique())
        if not codes <= {0, 1} or not frame[event].eq(1).any():
            raise MlcaUserError(
                "Survival requires an explicitly coded event indicator with observed events",
                category="gate_blocked",
            )
        return {"type": "survival", "n_classes": None, "primary_metric": default_metric("survival")}
    if n < 2:
        raise MlcaUserError("At least two outcome classes are required", category="gate_blocked")
    return {
        "type": "binary" if n == 2 else "multiclass",
        "n_classes": n,
        "primary_metric": default_metric("binary" if n == 2 else "multiclass"),
    }


def prepared(session):
    state = session.state
    if not state.data_review_context:
        return None
    if any(qid not in state.answers for qid in state.questions):
        raise MlcaUserError("Answer the data-review questions first", category="gate_blocked")
    raw = source_frame(state)
    frame, excluded, group, mode = apply(
        raw, state.data_decisions, preserve_index=bool(state.task.get("autonomous"))
    )
    group = group or state.group_column
    excluded = sorted(
        set(
            excluded
            + state.outcome_exclusions
            + (state.excluded_columns if state.task.get("autonomous") else [])
        )
    )
    if state.template_id == "survival":
        # Outcome fields are needed for scoring and training-only review; they
        # are separately excluded from predictors by the runtime contract.
        outcomes = {state.columns.get(k) for k in ("target", "duration", "event_column")}
        excluded = [c for c in excluded if c not in outcomes]
    task = {**state.task, **task_for(frame, state, mode)}
    frame = frame.drop(columns=[c for c in excluded if c != group], errors="ignore")
    digest = hashlib.sha256(
        canonical({"source": context_key(state), "decisions": state.data_decisions}).encode()
    ).hexdigest()
    suffix = (
        ".parquet"
        if state.task.get("autonomous")
        else Path(state.data[primary_for(state)]["original_path"]).suffix.lower()
    )
    path = session.root / ".mlca/data/prepared" / (digest + suffix)
    if state.prepared_data:
        path = session.root / state.prepared_data["path"]
        if sha256(path) != state.prepared_data["sha256"]:
            raise IntegrityError("Prepared input changed")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    if suffix == ".parquet":
        frame.to_parquet(path, index=bool(state.task.get("autonomous")))
    else:
        frame.to_csv(path, index=False, sep="\t" if suffix == ".tsv" else ",")
    session.emit("TaskConfigured", {"task": task, "excluded_columns": excluded, "group_column": group})
    session.emit(
        "DataPrepared",
        {
            "path": str(path.relative_to(session.root)),
            "sha256": sha256(path),
            "source_sha256": state.data[primary_for(state)]["sha256"],
            "decision_sha256": digest,
        },
    )
    return path


def protocol_input(session):
    state = session.state
    task = dict(state.task)
    task.setdefault(
        "type",
        {"tabular_classification": "binary", "multilabel_classification": "multilabel"}.get(
            state.template_id, state.template_id
        ),
    )
    if not task.get("primary_metric"):
        task["primary_metric"] = default_metric(task["type"])
    data = {
        "primary_data": state.primary_data,
        "columns": state.columns,
        "task": task,
        "excluded_columns": state.excluded_columns,
        "group_column": state.group_column,
        "targets": [c for c in state.columns.values() if c is not None],
        "seed": 42,
        "bootstrap_resamples": 1000,
    }
    digest = hashlib.sha256(canonical(data).encode()).hexdigest()
    path = session.root / ".mlca/data/protocol" / (digest + ".json")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(path, data)
    elif sha256(path) != hashlib.sha256((canonical(data) + "\n").encode()).hexdigest():
        # atomic_json is indented JSON; compare parsed contents rather than formatting.
        import json

        if json.loads(path.read_text()) != data:
            raise IntegrityError("Protocol snapshot changed")
    return path


def split_parameters(frame, params, target):
    """Keep stratification only when each class can enter all three partitions."""
    if params["method"] != "stratified":
        return params
    counts = frame[target].value_counts(dropna=False)
    train = (counts * params["train_fraction"]).astype(int)
    val = (counts * params["val_fraction"]).astype(int)
    if ((train < 1) | (val < 1) | ((counts - train - val) < 1)).any():
        return {**params, "method": "random"}
    return params
