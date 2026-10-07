import json
from datetime import timedelta

import pytest

from mlca.api import Session
from mlca.evaluation.import_usage import extract, import_usage
from mlca.evaluation.metrics import generate
from mlca.llm.usage import read


def test_client_usage_window_and_idempotence(project_factory, tmp_path):
    with Session.open(project_factory(), mode="brain") as s:
        s.options()
        start = s.store.read()[-1].ts
        s.emit("Note", {"text": "finished"})
        rows = [
            {
                "type": "assistant",
                "timestamp": start.isoformat(),
                "sessionId": "fixture",
                "message": {
                    "id": "a",
                    "model": "client-model",
                    "content": "PRIVATE_TEXT_CANARY",
                    "usage": {"input_tokens": 10, "output_tokens": 4, "cache_read_input_tokens": 2},
                },
            },
            {
                "type": "assistant",
                "timestamp": (start - timedelta(days=2)).isoformat(),
                "sessionId": "fixture",
                "message": {
                    "id": "outside",
                    "model": "client-model",
                    "content": "PRIVATE_TEXT_CANARY",
                    "usage": {"input_tokens": 99, "output_tokens": 99},
                },
            },
        ]
        path = tmp_path / "claude.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        assert import_usage(s, "claude", str(path))["records_processed"] == 1
        import_usage(s, "claude", str(path))
        assert len(read(s.root)) == 1
        assert "PRIVATE_TEXT_CANARY" not in (s.root / ".mlca/usage.jsonl").read_text()
        assert "PRIVATE_TEXT_CANARY" not in (s.root / ".mlca/egress.jsonl").read_text()
        model = generate(s)["models"]["external_agent"]
        assert model["input_tokens"] == {"value": 10, "source": "client-reported"}
        assert model["cost_usd"]["value"] is None


def test_codex_cumulative_duplicates_and_deltas(tmp_path):
    def row(total, last=None):
        return {
            "type": "event_msg",
            "timestamp": "2026-10-07T10:00:00Z",
            "payload": {
                "type": "token_count",
                "info": {"total_token_usage": total, "last_token_usage": last},
            },
        }

    rows = [
        {"type": "session_meta", "payload": {"id": "fixture"}},
        {"type": "turn_context", "payload": {"model": "codex-model", "messages": "PRIVATE_TEXT_CANARY"}},
        row(
            {"input_tokens": 10, "output_tokens": 2, "cached_input_tokens": 3},
            {"input_tokens": 10, "output_tokens": 2, "cached_input_tokens": 3},
        ),
        row({"input_tokens": 10, "output_tokens": 2, "cached_input_tokens": 3}),
        row({"input_tokens": 25, "output_tokens": 7, "cached_input_tokens": 8}),
    ]
    path = tmp_path / "codex.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows))
    results = list(extract(path, "codex"))
    assert len(results) == 2
    assert sum(r["input_tokens"] for r in results) == 25
    assert results[1]["output_tokens"] == 5
    assert all(r["model"] == "codex-model" for r in results)
    assert "PRIVATE_TEXT_CANARY" not in json.dumps(results)


def test_invalid_client_json_does_not_echo_content(tmp_path):
    path = tmp_path / "session.jsonl"
    path.write_text("PRIVATE_TEXT_CANARY")
    with pytest.raises(Exception, match="line 1") as error:
        list(extract(path, "claude"))
    assert "PRIVATE_TEXT_CANARY" not in str(error.value)
