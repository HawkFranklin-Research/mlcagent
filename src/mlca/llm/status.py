from datetime import datetime, timezone

from .credentials import resolve


def roles(config, requests):
    result = {}
    today = datetime.now(timezone.utc).date().isoformat()
    for role, selected in config.roles.items():
        provider = config.providers[selected.provider]
        matching = [
            r
            for r in requests
            if r.get("role") == role
            and r.get("provider") == selected.provider
            and r.get("model") == selected.model
        ]
        last = matching[-1] if matching else None
        key_available = (
            provider.kind in {"fake", "openai_compatible"}
            and not provider.api_key_env
            or bool(resolve(provider.api_key_env))
        )
        health = "grey"
        if last:
            health = (
                "yellow"
                if last.get("status_code") == 429 or (last.get("latency_ms") or 0) > 30000
                else "green"
                if last["status"] == "ok"
                else "red"
            )
        if not key_available:
            health = "grey"
        result[role] = {
            "provider": selected.provider,
            "kind": provider.kind,
            "model": selected.model,
            "model_reported": last.get("model_reported") if last else None,
            "health": health,
            "credential_available": key_available,
            "requests_today_in_project": sum(r.get("ts", "").startswith(today) for r in matching),
            "quota_limit": None,
            "quota_source": "unavailable",
        }
    return result
