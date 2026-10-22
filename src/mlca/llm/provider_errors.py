"""Extract only provider error type/message, never request objects or headers."""


def details(error):
    if not isinstance(getattr(error, "status_code", None), int):
        return {}
    body = getattr(error, "body", None)
    entry = body.get("error", body) if isinstance(body, dict) else None
    result = {}
    for field, attribute, key in (
        ("provider_error_type", "provider_error_type", "type"),
        ("provider_error_message", "provider_error_message", "message"),
    ):
        value = getattr(error, attribute, None)
        if value is None and isinstance(entry, dict):
            value = entry.get(key)
            if value is None and key == "type":
                value = entry.get("code")
        if isinstance(value, (str, int)):
            result[field] = str(value)
    return result
