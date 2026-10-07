from pathlib import Path
from typing import Any

from mlca.errors import MlcaUserError
from mlca.llm.usage import read as read_usage
from mlca.paths import atomic_json

from . import figure_index, methods, provenance, usage_report


def generate(root: Path, state: Any, workflow: Any, records: Any, kind: Any = "all") -> Any:
    if kind not in {"all", "methods", "provenance", "figures", "usage"}:
        raise MlcaUserError("Unknown report type")
    steps = {s["step_id"] for s in state.steps}
    sessions = {r.session_id for r in records}
    requests = [
        r
        for r in read_usage(root)
        if r.get("step_id") in steps or (not r.get("step_id") and r.get("session_id") in sessions)
    ]
    outputs = {}
    directory = root / "reports/generated"
    directory.mkdir(parents=True, exist_ok=True)
    builders = {
        "methods": lambda: methods.build(state, workflow),
        "provenance": lambda: provenance.build(root, state, requests),
        "figures": lambda: figure_index.build(state),
        "usage": lambda: usage_report.build(state, requests, records),
    }
    for name in builders if kind == "all" else [kind]:
        value = builders[name]()
        file = directory / (name + ".md" if isinstance(value, str) else name + ".json")
        if isinstance(value, str):
            file.write_text(value, encoding="utf-8")
        else:
            atomic_json(file, value)
        outputs[name] = str(file.relative_to(root))
    # Always expose all unlocks, including other branches, so reports cannot hide test exposure.
    from mlca.log.store import Store

    all_records = Store(root).read()
    atomic_json(
        directory / "project_test_exposure.json",
        [r.model_dump(mode="json") for r in all_records if r.type.value == "TestUnlocked"],
    )
    outputs["project_test_exposure"] = "reports/generated/project_test_exposure.json"
    atomic_json(
        directory / "trust_boundary.json",
        {
            "agent_file_access": "unknown (outside MLCA)",
            "contains_data_rows": [
                output["path"] for output in state.artefacts.values() if output.get("contains_data_rows")
            ],
            "row_fingerprint_limit": "Verbatim matches only; derived summaries and figures can reveal data",
        },
    )
    outputs["trust_boundary"] = "reports/generated/trust_boundary.json"
    return outputs
