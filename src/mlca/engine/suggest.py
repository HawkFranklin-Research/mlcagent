"""Rule-based study-field suggestions. Local only: no model call, nothing leaves the machine.

Suggestions pre-fill the study details form; the human still saves them.
"""

import re

OUTCOME = {"target", "label", "class", "outcome", "diagnosis", "result", "response", "y", "disease"}
DURATION = {"time", "duration", "days", "months", "years", "survival", "os", "pfs", "followup", "follow"}
EVENT = {"event", "status", "death", "dead", "died", "cens", "censor", "censored", "observed", "relapse"}


def _tokens(name):
    return set(re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", str(name)).lower()))


def profile(frame):
    """Per-column facts the rules need (counts only)."""
    rows = len(frame)
    result = {}
    for position, column in enumerate(frame.columns):
        series = frame[column]
        unique = int(series.nunique(dropna=True))
        result[column] = {
            "unique": unique,
            "numeric": series.dtype.kind in "iuf",
            "float": series.dtype.kind == "f",
            "binary": unique == 2,
            "missing_share": float(series.isna().mean()) if rows else 0.0,
            "id_like": rows > 20 and unique >= 0.95 * rows and series.dtype.kind != "f",
            "last": position == len(frame.columns) - 1,
        }
    return result


def rank(frame, field="target"):
    """Columns ranked for a study field, best first: [(column, score, reasons)]."""
    words = {"target": OUTCOME, "duration": DURATION, "event_column": EVENT}[field]
    ranked = []
    for column, facts in profile(frame).items():
        score, reasons = 0.0, []
        tokens = _tokens(column)
        if tokens & words or str(column).lower() in words:
            score += 3
            reasons.append("named like an outcome" if field == "target" else "name fits")
        if facts["id_like"] or "id" in tokens:
            score -= 5
            reasons.append("looks like an identifier")
        if field == "target":
            if 2 <= facts["unique"] <= 20:
                score += 2
                reasons.append(f"{facts['unique']} categories")
            elif facts["float"] and facts["unique"] > 50:
                score -= 2
            if facts["last"]:
                score += 1
                reasons.append("last column")
        elif field == "event_column":
            if facts["binary"]:
                score += 3
                reasons.append("two values")
            else:
                score -= 2
        elif field == "duration":
            if facts["numeric"] and facts["unique"] > 10:
                score += 2
                reasons.append("numeric with many values")
            else:
                score -= 2
        if facts["missing_share"] > 0.2:
            score -= 1
            reasons.append(f"{facts['missing_share']:.0%} missing")
        ranked.append((column, score, reasons))
    return sorted(ranked, key=lambda item: -item[1])


def recommendations(frame, template_id):
    fields = ["duration", "event_column"] if template_id == "survival" else ["target"]
    result = {}
    for field in fields:
        ranked = [item for item in rank(frame, field) if item[1] > 0]
        if ranked:
            result[field] = ranked
    return result
