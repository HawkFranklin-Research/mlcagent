"""Explicit, reasoned spelling maps; never silently combine distinct outcomes."""

from mlca.errors import MlcaUserError


def spelling(value):
    return value.strip().casefold().rstrip(".").rstrip()


def apply_label_map(frame, mapping, targets, reason):
    if not mapping:
        return frame
    if not reason.strip() or not set(mapping) <= set(targets):
        raise MlcaUserError(
            "Label mapping requires target columns and a reason", category="invalid_inference"
        )
    result = frame.copy()
    for column, replacements in mapping.items():
        if column not in frame:
            raise MlcaUserError("Label mapping names an unknown column", category="invalid_inference")
        domain = set(frame[column].dropna().unique())
        if len(domain) > 20 or not all(isinstance(x, str) for x in domain):
            raise MlcaUserError(
                "Spelling maps require at most twenty string labels", category="invalid_inference"
            )
        for old, new in replacements.items():
            if old not in domain or new not in domain or spelling(old) != spelling(new):
                raise MlcaUserError(
                    "Label mapping may only merge observed spellings of the same label",
                    category="invalid_inference",
                )
        result[column] = result[column].replace(replacements)
    return result
