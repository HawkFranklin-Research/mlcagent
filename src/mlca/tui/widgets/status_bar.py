from typing import Any

from textual.widgets import Static


class StatusBar(Static):
    def render_state(self, status: Any) -> Any:
        usage = status["usage"]
        from rich.text import Text

        rendered = Text(
            f"{status['branch']} | {status['current_event']} | requests {usage['model_requests']} | known USD {usage['known_cost_usd']:.4f} | unknown costs {usage['unknown_cost_requests']}"
        )
        for role, info in status.get("model_status", {}).items():
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
            quota = f"{info['requests_today_in_project']} project requests today; account quota unknown"
            rendered.append(
                f"{role}: {info['kind']} · {info['model']} → {info['model_reported'] or 'not answered yet'} · {label} · {quota}"
            )
        self.update(rendered)
