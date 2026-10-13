import csv

from mlca.config import ProviderConfig
from mlca.llm.catalog import parse, snapshot


def entry(identifier, prompt="0", outputs=("text",), tokenizer="GPT", coding=None):
    return {
        "id": identifier,
        "name": identifier,
        "pricing": {"prompt": prompt, "completion": prompt},
        "architecture": {"output_modalities": list(outputs), "tokenizer": tokenizer},
        "supported_parameters": ["response_format"],
        "benchmarks": {"artificial_analysis": {"coding_index": coding}},
    }


def test_snapshot_lists_free_models_and_shortlist_with_candidate_flags(tmp_path):
    models = parse(
        {
            "data": [
                entry("free/coder:free", coding=40.0),
                entry("openrouter/free", tokenizer="Router"),
                entry("free/music", outputs=("text", "audio")),
                entry("paid/model", prompt="0.000001"),
                entry("paid/other", prompt="0.000001"),
            ]
        }
    )
    path, missing = snapshot(
        ProviderConfig(kind="openrouter"), ["paid/model", "gone/model"], tmp_path, models
    )
    rows = {r["id"]: r for r in csv.DictReader(path.open())}
    assert path.name.startswith("openrouter_models_") and missing == ["gone/model"]
    assert set(rows) == {"free/coder:free", "openrouter/free", "free/music", "paid/model"}
    assert rows["paid/model"]["group"] == "selected" and rows["paid/model"]["usd_per_m_input"] == "1.0"
    assert (
        rows["free/coder:free"]["candidate"] == "True"
        and rows["free/coder:free"]["aa_coding_index"] == "40.0"
    )
    assert rows["openrouter/free"]["candidate"] == "False" and rows["free/music"]["candidate"] == "False"
