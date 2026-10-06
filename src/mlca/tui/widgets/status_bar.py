from typing import Any

from textual.widgets import Static


class StatusBar(Static):
    def render_state(self, status: Any) -> Any:
        usage = status["usage"]
        self.update(
            f"{status['branch']} | {status['current_event']} | requests {usage['model_requests']} | "
            f"known USD {usage['known_cost_usd']:.4f} | unknown costs {usage['unknown_cost_requests']}"
        )
