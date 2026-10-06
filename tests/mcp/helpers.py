import asyncio
import json
import time


def data(result):
    assert not result.is_error, result
    return json.loads(result.content[0].text)["data"]


async def poll(client, step_id):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        saved = data(await client.call_tool("mlca_step_status", {"step_id": step_id}))
        if saved["status"] in {"completed", "failed", "awaiting_script"}:
            return saved
        await asyncio.sleep(0.03)
    raise AssertionError("Step never finished")


async def choose(client, action):
    menu = data(await client.call_tool("mlca_options", {}))
    option = next(o for o in menu["options"] if o.get("action_id") == action)
    result = data(await client.call_tool("mlca_choose", {"option_id": option["id"]}))
    return (
        await poll(client, result["step_id"])
        if result["status"] not in {"completed", "awaiting_script"}
        else result
    )
