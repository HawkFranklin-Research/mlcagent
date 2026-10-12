"""Persist only validated model/provider settings, never credentials."""

from mlca.config import Config


def changes(old, new):
    result = []
    for role in sorted(set(old.roles) | set(new.roles)):
        before, after = old.roles.get(role), new.roles.get(role)
        provider_before = old.providers.get(before.provider) if before else None
        provider_after = new.providers.get(after.provider) if after else None
        if before != after or provider_before != provider_after:
            result.append(
                {
                    "role": role,
                    "from": before.model_dump() if before else {},
                    "to": after.model_dump() if after else {},
                    "provider": after.provider if after else None,
                    "provider_config": provider_after.model_dump() if provider_after else None,
                }
            )
    return result


def replay_configuration(config, records):
    data = config.model_dump()
    for record in records:
        if record.type.value != "ModelChanged":
            continue
        p = record.payload
        if p["to"]:
            data["roles"][p["role"]] = p["to"]
            data["providers"][p["provider"]] = p["provider_config"]
        else:
            data["roles"].pop(p["role"], None)
    return Config.model_validate(data)
