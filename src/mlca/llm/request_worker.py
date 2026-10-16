"""Trusted SDK transport. Never persist or print its secret-bearing input."""

import json
import sys


def main():
    from openai import OpenAI

    request = json.load(sys.stdin)
    try:
        with OpenAI(
            api_key=request["key"], base_url=request["base_url"], timeout=request["timeout_s"], max_retries=0
        ) as client:
            response = client.chat.completions.create(**request["payload"])
            result = {"data": response.model_dump()}
    except Exception as exc:
        headers = getattr(getattr(exc, "response", None), "headers", {})
        result = {
            "error": str(exc).replace(request["key"], "[REDACTED]"),
            "status_code": getattr(exc, "status_code", None),
            "retry_after": headers.get("retry-after") if headers else None,
        }
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
