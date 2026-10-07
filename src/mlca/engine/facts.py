from typing import Any

from mlca.paths import contained, sha256


def validate(candidate: Any, root: Any, state: Any, row_guard=None, allow_sample_rows=False) -> Any:
    source = candidate.get("source", "")
    output = state.artefacts.get(source)
    if output is None:
        return False, "Fact source must be a completed, indexed artifact"
    path = root / source
    if (
        not contained(path, root / ".mlca/steps")
        or not path.is_file()
        or sha256(path) != candidate.get("sha256")
    ):
        return False, "Fact source hash does not match"
    if candidate.get("step_id") != output["step_id"]:
        return False, "Fact step does not own its artifact"
    if not candidate.get("key") or "value" not in candidate:
        return False, "Fact key/value missing"
    if not allow_sample_rows and row_guard and row_guard.contains_full_row(candidate["value"]):
        return False, "Fact value contains a registered data row"
    return True, "Citation validated; semantic correctness still requires inspection"
