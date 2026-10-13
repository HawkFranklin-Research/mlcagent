from typing import Any

from textual.widgets import Static


class StatusBar(Static):
    def render_state(self, status: Any) -> Any:
        usage = status["usage"]
        from rich.text import Text

        rendered = Text(
            f"{status['branch']} | {status['current_event']} | requests {usage['model_requests']} | known USD {usage['known_cost_usd']:.4f} | unknown costs {usage['unknown_cost_requests']}"
        )
        client = status.get("external_client")
        if client and client["mode"] == "brain":
            rendered.append(f"\n● Brain mode · driven by {client['actor']} · MLCA makes no model calls")
        active = status.get("active_step")
        if active and client:
            rendered.append(
                f"\n{client['actor']} is working on step {active['step_id']}: {active.get('phase', active['status'])}"
            )
        for role, info in (
            {} if client and client["mode"] == "brain" else status.get("model_status", {})
        ).items():
            rendered.append(
                "\n● ",
                style={"grey": "grey50", "green": "green", "yellow": "yellow", "red": "red"}[info["health"]],
            )
            label = (
                "not connected: press m"
                if not info["credential_available"]
                else "configured; connection not tested"
                if info["health"] == "grey"
                else info["health"]
            )
            reported = info.get("quota", {})
            quota = (
                f"{reported['used']}/{reported['limit']} today (last provider refresh)"
                if reported.get("used") is not None and reported.get("limit") is not None
                else f"{info['requests_today_in_project']} project requests today; account quota unknown"
            )
            rendered.append(
                f"{role}: {info['kind']} · {info['model']} → {info['model_reported'] or 'not answered yet'} · {label} · {quota}"
            )
        self.update(rendered)
