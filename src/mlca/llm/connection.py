"""Explicit tiny preview requests: no study data, one attempt per role."""

from pathlib import Path

from mlca.llm.client import Client, RequestContext


def test_connection(config, root: Path, role):
    data = config.model_dump()
    data["roles"][role]["max_output_tokens"] = 64
    from mlca.config import Config

    preview = Config.model_validate(data)
    client = Client(root, preview)
    result = client.complete(
        role,
        [{"role": "user", "content": "Reply exactly OK."}],
        context=RequestContext(role=role, session_id="connection-preview", purpose="connection_test"),
        categories=["user_text"],
        max_attempts=1,
    )
    from .usage import read

    usage = next(r for r in reversed(read(root)) if r["request_id"] == result.request_id)
    return {
        "role": role,
        "latency_ms": result.latency_ms,
        "model_reported": usage.get("model_reported"),
        "request_id": result.request_id,
    }
